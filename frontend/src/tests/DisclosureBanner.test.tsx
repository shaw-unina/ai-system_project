import { render, screen } from "@testing-library/react";
import DisclosureBanner from "@/components/DisclosureBanner";

describe("DisclosureBanner", () => {
  it("renders the AI-generated disclosure with role=alert", () => {
    render(<DisclosureBanner />);
    const el = screen.getByTestId("disclosure-banner");
    expect(el).toHaveAttribute("role", "alert");
    expect(el.textContent).toMatch(/AI-generated/i);
  });
});
