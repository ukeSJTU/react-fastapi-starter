import { screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { HomePage } from "@/routes/index"
import { render } from "@/test/render"

describe("HomePage", () => {
  it("renders a business-neutral starting point", () => {
    render(<HomePage />)

    expect(
      screen.getByRole("heading", { name: "Project ready." })
    ).toBeInTheDocument()
    expect(
      screen.getByText("Start building from a clean, modern foundation.")
    ).toBeInTheDocument()
  })

  it("keeps the theme control available", async () => {
    const { user } = render(<HomePage />)

    await user.click(screen.getByRole("button", { name: "Toggle theme" }))

    expect(document.documentElement).toHaveClass("dark")
  })
})
