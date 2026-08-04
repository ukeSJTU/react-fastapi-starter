import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import type { ReactNode } from "react"

import { ThemeProvider } from "@/components/theme-provider"

type AppProvidersProps = {
  children: ReactNode
  queryClient?: QueryClient
}

const appQueryClient = new QueryClient()

export function AppProviders({
  children,
  queryClient = appQueryClient,
}: AppProvidersProps) {
  return (
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </ThemeProvider>
  )
}
