import { describe, expect, it } from "vitest"

import {
  getHealth,
  getGetHealthQueryKey,
  getGetHealthUrl,
} from "@/api/generated/endpoints/health/health"
import { getGetHealthMockHandler } from "@/api/generated/endpoints/health/health.msw"
import { server } from "@/test/server"

describe("generated API contract", () => {
  it("preserves origin-relative OpenAPI paths", () => {
    expect(getGetHealthUrl()).toBe("/health")
  })

  it("uses stable operation IDs for query keys", () => {
    expect(getGetHealthQueryKey()).toEqual(["getHealth"])
  })

  it("sends requests through an explicitly declared MSW handler", async () => {
    server.use(getGetHealthMockHandler({ status: "healthy" }))

    const response = await getHealth()

    expect(response.status).toBe(200)
    expect(response.data).toEqual({ status: "healthy" })
  })
})
