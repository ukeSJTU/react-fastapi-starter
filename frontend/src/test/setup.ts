import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterAll, afterEach, beforeAll } from "vitest"

import { server } from "@/test/server"

const storageValues = new Map<string, string>()
const localStorage = {
  get length() {
    return storageValues.size
  },
  clear() {
    storageValues.clear()
  },
  getItem(key: string) {
    return storageValues.get(key) ?? null
  },
  key(index: number) {
    return Array.from(storageValues.keys())[index] ?? null
  },
  removeItem(key: string) {
    storageValues.delete(key)
  },
  setItem(key: string, value: string) {
    storageValues.set(key, value)
  },
} satisfies Storage

Object.defineProperty(window, "localStorage", {
  configurable: true,
  value: localStorage,
})

Object.defineProperty(window, "matchMedia", {
  configurable: true,
  value: (query: string): MediaQueryList => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  }),
})

Object.defineProperty(window, "scrollTo", {
  configurable: true,
  value: () => undefined,
})

beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" })
})

afterEach(() => {
  cleanup()
  server.resetHandlers()
  window.localStorage.clear()
  document.documentElement.className = ""
})

afterAll(() => {
  server.close()
})
