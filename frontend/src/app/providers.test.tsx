import { useQueryClient } from "@tanstack/react-query"
import { screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"

import { useTheme } from "@/components/theme-provider"
import { render } from "@/test/render"

function ProviderProbe() {
  const queryClient = useQueryClient()
  const { theme } = useTheme()

  return (
    <output>{`theme:${theme};queries:${queryClient.getQueryCache().getAll().length}`}</output>
  )
}

describe("AppProviders", () => {
  it("provides query and theme contexts", () => {
    render(<ProviderProbe />)

    expect(screen.getByRole("status")).toHaveTextContent(
      "theme:system;queries:0"
    )
  })
})
