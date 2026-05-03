import { expect, test } from "@playwright/test";

test("verify page submits a claim and renders a verdict", async ({ page }) => {
  await page.goto("/verify");
  await expect(page.getByRole("heading", { name: /verify/i })).toBeVisible();

  await page.getByRole("textbox").fill("The Eiffel Tower is in Paris.");
  await page.getByRole("button", { name: /submit/i }).click();

  await expect(page.getByTestId("verdict-card")).toBeVisible({ timeout: 60_000 });
});

test("AI disclosure banner is always present", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("disclosure-banner")).toBeVisible();
});
