import { describe, expect, it } from "vitest"

import {
  getHealth,
  getGetHealthQueryKey,
  getGetHealthUrl,
} from "@/api/generated/endpoints/health/health"

describe("generated API contract", () => {
  it("preserves origin-relative OpenAPI paths", () => {
    expect(getGetHealthUrl()).toBe("/health")
  })

  it("uses stable operation IDs for query keys", () => {
    expect(getGetHealthQueryKey()).toEqual(["getHealth"])
  })

  it("uses generated MSW handlers for API requests", async () => {
    const response = await getHealth()

    expect(response.status).toBe(200)
    expect(response.data.status).toMatch(/^(healthy|unavailable)$/)
  })
})
