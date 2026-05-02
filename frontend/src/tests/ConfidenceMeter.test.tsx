import { render, screen } from "@testing-library/react";
import ConfidenceMeter from "@/components/ConfidenceMeter";

describe("ConfidenceMeter", () => {
  it("sets aria-valuenow proportional to value", () => {
    render(<ConfidenceMeter value={0.42} />);
    const bar = screen.getByRole("progressbar");
    expect(bar).toHaveAttribute("aria-valuenow", "42");
  });

  it("clamps value into [0, 1]", () => {
    render(<ConfidenceMeter value={1.7} />);
    expect(screen.getByRole("progressbar")).toHaveAttribute("aria-valuenow", "100");
  });
});
