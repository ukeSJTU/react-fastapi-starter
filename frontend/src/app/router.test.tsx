import { RouterProvider } from "@tanstack/react-router"
import { screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { router } from "@/app/router"
import { render } from "@/test/render"

describe("router", () => {
  it("renders the index file route", async () => {
    await router.load()

    render(<RouterProvider router={router} />)

    expect(
      await screen.findByRole("heading", { name: "Project ready." })
    ).toBeInTheDocument()
  })
})
