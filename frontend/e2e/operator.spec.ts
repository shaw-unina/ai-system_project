import { expect, test } from "@playwright/test";

test("operator dashboard lists reports and live metrics tiles", async ({ page }) => {
  await page.goto("/operator");
  await expect(page.getByTestId("metrics-tiles")).toBeVisible();
  await expect(page.getByTestId("report-list")).toBeVisible();
  await expect(page.getByTestId("lowconf-empty").or(page.getByTestId("lowconf-table"))).toBeVisible();
});
