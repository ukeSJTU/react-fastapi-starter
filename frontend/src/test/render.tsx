import { QueryClient } from "@tanstack/react-query"
import {
  render as testingLibraryRender,
  type RenderOptions,
} from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import type { ReactElement } from "react"

import { AppProviders } from "@/app/providers"

type CustomRenderOptions = Omit<RenderOptions, "wrapper"> & {
  queryClient?: QueryClient
}

export function render(
  ui: ReactElement,
  {
    queryClient = createTestQueryClient(),
    ...options
  }: CustomRenderOptions = {}
) {
  const result = testingLibraryRender(
    <AppProviders queryClient={queryClient}>{ui}</AppProviders>,
    options
  )

  return {
    ...result,
    queryClient,
    user: userEvent.setup(),
  }
}

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  })
}
