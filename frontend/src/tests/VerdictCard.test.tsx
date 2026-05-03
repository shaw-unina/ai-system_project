import { render, screen } from "@testing-library/react";
import VerdictCard from "@/components/VerdictCard";
import { mkVerify } from "./_fixtures";

describe("VerdictCard", () => {
  it("renders the verdict chip and confidence dial", () => {
    render(<VerdictCard response={mkVerify({ verdict: "Supported", confidence: 0.9 })} />);
    expect(screen.getByText(/Supported/i)).toBeInTheDocument();
    expect(screen.getByRole("meter")).toHaveAttribute("aria-valuenow", "0.9");
  });

  it("shows the low-confidence flag when set", () => {
    render(<VerdictCard response={mkVerify({ low_confidence: true, confidence: 0.3 })} />);
    expect(screen.getByTestId("low-conf-flag")).toBeInTheDocument();
  });

  it("renders AbstainCallout when verdict is Abstain", () => {
    render(
      <VerdictCard
        response={mkVerify({
          verdict: "Abstain",
          rationale: "Abstained: confidence below threshold; retrieval coverage low.",
          low_confidence: true,
        })}
      />,
    );
    const callout = screen.getByTestId("abstain-callout");
    expect(callout).toBeInTheDocument();
    expect(callout.textContent).toMatch(/confidence below threshold/);
    expect(callout.textContent).toMatch(/retrieval coverage low/);
  });
});
