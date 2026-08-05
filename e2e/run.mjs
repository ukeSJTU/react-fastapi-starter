import { spawn } from "node:child_process"
import { randomBytes } from "node:crypto"
import { mkdir, writeFile } from "node:fs/promises"
import { fileURLToPath } from "node:url"

const repositoryRoot = fileURLToPath(new URL("..", import.meta.url))
const projectName = `react-fastapi-starter-e2e-${process.pid}-${randomBytes(4).toString("hex")}`
const composeFiles = ["compose.yaml", "compose.production.yaml"]
const composePrefix = [
  "compose",
  "--project-name",
  projectName,
  ...composeFiles.flatMap((file) => ["--file", file]),
]
const composeEnvironment = {
  ...process.env,
  APP_PORT: "0",
  POSTGRES_PASSWORD: randomBytes(24).toString("hex"),
}

let activeChild
let receivedSignal

class CommandError extends Error {
  constructor(command, args, result) {
    const outcome = result.signal
      ? `received ${result.signal}`
      : `exited with code ${result.code}`
    super(`${command} ${args.join(" ")} ${outcome}`)
    this.name = "CommandError"
  }
}

function handleSignal(signal) {
  if (receivedSignal) {
    process.removeAllListeners(signal)
    process.kill(process.pid, signal)
    return
  }

  receivedSignal = signal
  activeChild?.kill(signal)
}

process.on("SIGINT", () => handleSignal("SIGINT"))
process.on("SIGTERM", () => handleSignal("SIGTERM"))

function runCommand(
  command,
  args,
  {
    capture = false,
    allowFailure = false,
    allowAfterSignal = false,
    env = process.env,
  } = {}
) {
  if (receivedSignal && !allowAfterSignal) {
    throw new Error(`Interrupted by ${receivedSignal}`)
  }

  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: repositoryRoot,
      env,
      stdio: capture ? ["ignore", "pipe", "pipe"] : "inherit",
    })
    activeChild = child

    let stdout = ""
    let stderr = ""

    if (capture) {
      child.stdout.setEncoding("utf8")
      child.stderr.setEncoding("utf8")
      child.stdout.on("data", (chunk) => {
        stdout += chunk
      })
      child.stderr.on("data", (chunk) => {
        stderr += chunk
      })
    }

    child.once("error", (error) => {
      activeChild = undefined
      reject(error)
    })
    child.once("close", (code, signal) => {
      activeChild = undefined
      const result = { code, signal, stdout, stderr }

      if (code === 0 || allowFailure) {
        resolve(result)
        return
      }

      reject(new CommandError(command, args, result))
    })
  })
}

function runCompose(args, options = {}) {
  return runCommand("docker", [...composePrefix, ...args], {
    env: composeEnvironment,
    ...options,
  })
}

async function writeDiagnostics() {
  const services = await runCompose(["ps", "--all"], {
    capture: true,
    allowFailure: true,
    allowAfterSignal: true,
  })
  const logs = await runCompose(["logs", "--no-color"], {
    capture: true,
    allowFailure: true,
    allowAfterSignal: true,
  })
  const diagnosticsDirectory = fileURLToPath(
    new URL("../test-results/", import.meta.url)
  )
  const diagnostics = [
    "docker compose ps --all\n",
    services.stdout,
    services.stderr,
    "\ndocker compose logs --no-color\n",
    logs.stdout,
    logs.stderr,
  ].join("")

  await mkdir(diagnosticsDirectory, { recursive: true })
  await writeFile(`${diagnosticsDirectory}compose.log`, diagnostics)

  process.stderr.write(diagnostics)
}

function findPublishedPort(output) {
  for (const endpoint of output.trim().split(/\s+/)) {
    const match = endpoint.match(/:(\d+)$/)
    if (match?.[1]) {
      return match[1]
    }
  }

  throw new Error(
    `Could not determine the published application port: ${output}`
  )
}

async function main() {
  let failure

  try {
    process.stdout.write(`[e2e] Building isolated stack ${projectName}\n`)
    await runCompose(["--profile", "tools", "--parallel", "2", "build"])

    process.stdout.write("[e2e] Applying database migrations\n")
    await runCompose(["run", "--rm", "migrate"])

    process.stdout.write("[e2e] Starting production stack\n")
    await runCompose(["up", "--detach", "--wait", "--no-build"])

    const portResult = await runCompose(["port", "frontend", "8080"], {
      capture: true,
    })
    const publishedPort = findPublishedPort(portResult.stdout)
    const baseURL = `http://127.0.0.1:${publishedPort}`

    process.stdout.write(`[e2e] Running Chromium smoke tests at ${baseURL}\n`)
    const pnpmCommand = process.platform === "win32" ? "pnpm.cmd" : "pnpm"
    await runCommand(
      pnpmCommand,
      ["exec", "playwright", "test", ...process.argv.slice(2)],
      {
        env: { ...process.env, PLAYWRIGHT_BASE_URL: baseURL },
      }
    )
  } catch (error) {
    failure = error
    process.exitCode = 1
    process.stderr.write(
      `[e2e] ${error instanceof Error ? error.message : String(error)}\n`
    )

    try {
      await writeDiagnostics()
    } catch (diagnosticsError) {
      process.stderr.write(
        `[e2e] Could not write diagnostics: ${diagnosticsError instanceof Error ? diagnosticsError.message : String(diagnosticsError)}\n`
      )
    }
  } finally {
    process.stdout.write(`[e2e] Removing isolated stack ${projectName}\n`)

    try {
      await runCompose(
        ["down", "--volumes", "--remove-orphans", "--rmi", "local"],
        { allowAfterSignal: true }
      )
    } catch (cleanupError) {
      process.exitCode = 1
      process.stderr.write(
        `[e2e] Cleanup failed: ${cleanupError instanceof Error ? cleanupError.message : String(cleanupError)}\n`
      )
    }
  }

  if (receivedSignal) {
    process.exitCode = receivedSignal === "SIGINT" ? 130 : 143
  } else if (failure) {
    process.exitCode = 1
  }
}

await main()
