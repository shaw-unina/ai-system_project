import { render, screen, fireEvent } from "@testing-library/react";
import LowConfidenceTable from "@/components/LowConfidenceTable";
import { recordIfLowConf, clearLowConf } from "@/lib/lowconf";
import { mkVerify } from "./_fixtures";

describe("LowConfidenceTable", () => {
  beforeEach(() => {
    window.localStorage.removeItem("misinfo:lowconf");
  });

  it("renders empty state when nothing is recorded", () => {
    render(<LowConfidenceTable />);
    expect(screen.getByTestId("lowconf-empty")).toBeInTheDocument();
  });

  it("only records rows when low_confidence is true", () => {
    recordIfLowConf("safe claim", mkVerify({ low_confidence: false }));
    recordIfLowConf("risky claim", mkVerify({ low_confidence: true, confidence: 0.2 }));
    render(<LowConfidenceTable />);
    expect(screen.queryByTestId("lowconf-empty")).toBeNull();
    expect(screen.getByTestId("lowconf-table").textContent).toMatch(/risky claim/);
    expect(screen.getByTestId("lowconf-table").textContent).not.toMatch(/safe claim/);
  });

  it("clear button wipes the session list", () => {
    recordIfLowConf("a claim", mkVerify({ low_confidence: true, confidence: 0.1 }));
    render(<LowConfidenceTable />);
    fireEvent.click(screen.getByTestId("lowconf-clear"));
    expect(screen.getByTestId("lowconf-empty")).toBeInTheDocument();
  });

  it("clearLowConf alone removes the storage key", () => {
    recordIfLowConf("a", mkVerify({ low_confidence: true }));
    clearLowConf();
    expect(window.localStorage.getItem("misinfo:lowconf")).toBeNull();
  });
});
