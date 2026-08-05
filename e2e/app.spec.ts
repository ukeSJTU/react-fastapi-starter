import { expect, test } from "@playwright/test"

test("serves and hydrates the application", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" })
  await page.goto("/")

  await expect(
    page.getByRole("heading", { name: "Project ready." })
  ).toBeVisible()

  const root = page.locator("html")
  await expect(root).toHaveClass(/light/)
  await page.getByRole("button", { name: "Toggle theme" }).click()
  await expect(root).toHaveClass(/dark/)
})

test("serves the production backend through the public origin", async ({
  request,
}) => {
  const healthResponse = await request.get("/health")

  expect(healthResponse.ok()).toBe(true)
  await expect(healthResponse.json()).resolves.toEqual({ status: "healthy" })

  const openApiResponse = await request.get("/openapi.json")

  expect(openApiResponse.status()).toBe(404)
})
