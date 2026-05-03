import { render, screen } from "@testing-library/react";
import ConfidenceDial from "@/components/ConfidenceDial";

describe("ConfidenceDial", () => {
  it("exposes confidence as an aria meter with the right value", () => {
    render(<ConfidenceDial value={0.83} />);
    const m = screen.getByRole("meter");
    expect(m).toHaveAttribute("aria-valuenow", "0.83");
    expect(m).toHaveAttribute("aria-valuemax", "1");
  });

  it("clamps out-of-range values", () => {
    render(<ConfidenceDial value={1.5} />);
    expect(screen.getByRole("meter")).toHaveAttribute("aria-valuenow", "1");
  });

  it("indicates below-threshold values in the aria label", () => {
    render(<ConfidenceDial value={0.2} />);
    expect(screen.getByRole("meter")).toHaveAccessibleName(
      /confidence 0\.20.*below threshold/i,
    );
  });
});
