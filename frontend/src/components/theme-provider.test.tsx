import { screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { useTheme } from "@/components/theme-provider"
import { render } from "@/test/render"

function ThemeControl() {
  const { theme, setTheme } = useTheme()

  return (
    <button type="button" onClick={() => setTheme("dark")}>
      {`Theme: ${theme}`}
    </button>
  )
}

describe("ThemeProvider", () => {
  it("restores the selected theme when the application remounts", async () => {
    const firstRender = render(<ThemeControl />)

    await firstRender.user.click(
      screen.getByRole("button", { name: "Theme: system" })
    )
    firstRender.unmount()

    render(<ThemeControl />)

    expect(
      screen.getByRole("button", { name: "Theme: dark" })
    ).toBeInTheDocument()
  })
})
