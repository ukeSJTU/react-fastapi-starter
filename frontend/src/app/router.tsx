import { createRouter, type RouterHistory } from "@tanstack/react-router"

import { routeTree } from "@/routeTree.gen"

type AppRouterOptions = {
  history?: RouterHistory
}

export function createAppRouter({ history }: AppRouterOptions = {}) {
  return createRouter({
    routeTree,
    defaultPreload: "intent",
    scrollRestoration: true,
    ...(history ? { history } : {}),
  })
}

export const router = createAppRouter()

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}
