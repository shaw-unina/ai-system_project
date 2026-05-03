import { fireEvent, render, screen } from "@testing-library/react";
import DisclosureBadge from "@/components/DisclosureBadge";

describe("DisclosureBadge", () => {
  it("renders the AI-generated pill closed by default", () => {
    render(<DisclosureBadge />);
    const trigger = screen.getByRole("button", { name: /ai-generated/i });
    expect(trigger).toBeInTheDocument();
    expect(trigger).toHaveAttribute("aria-expanded", "false");
  });

  it("opens a popover with the disclosure copy on click", () => {
    render(<DisclosureBadge />);
    fireEvent.click(screen.getByRole("button", { name: /ai-generated/i }));
    expect(screen.getByRole("dialog", { name: /ai disclosure/i })).toBeInTheDocument();
    expect(
      screen.getByText(/Verdicts, confidence scores, evidence/i),
    ).toBeInTheDocument();
  });
});
