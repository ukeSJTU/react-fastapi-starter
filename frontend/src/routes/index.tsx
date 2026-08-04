import { createFileRoute } from "@tanstack/react-router"

import { useTheme } from "@/components/theme-provider"
import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/")({
  component: HomePage,
})

export function HomePage() {
  const { theme, setTheme } = useTheme()

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark")
  }

  return (
    <main className="flex min-h-svh items-center p-6">
      <div className="flex max-w-md min-w-0 flex-col gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-medium tracking-tight">Project ready.</h1>
          <p className="text-sm leading-relaxed text-muted-foreground">
            Start building from a clean, modern foundation.
          </p>
        </div>
        <Button className="self-start" variant="outline" onClick={toggleTheme}>
          Toggle theme
        </Button>
      </div>
    </main>
  )
}
