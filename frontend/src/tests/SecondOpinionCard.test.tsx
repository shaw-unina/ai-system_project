import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import SecondOpinionCard from "@/components/SecondOpinionCard";
import type { SecondOpinionResponse } from "@/lib/types";

function withQuery(ui: React.ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{ui}</QueryClientProvider>;
}

function mockFetch(body: SecondOpinionResponse) {
  global.fetch = vi.fn(async () =>
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { "content-type": "application/json" },
    }),
  ) as unknown as typeof fetch;
}

describe("SecondOpinionCard", () => {
  it("renders disabled state when API key is unset", async () => {
    mockFetch({
      claim: "x",
      results: [],
      fetched_at: 0,
      source: "disabled",
    });
    render(withQuery(<SecondOpinionCard claim="x" />));
    await waitFor(() =>
      expect(screen.getByTestId("second-opinion-disabled")).toBeInTheDocument(),
    );
  });

  it("renders entries when results are returned", async () => {
    mockFetch({
      claim: "vaccines cause autism",
      results: [
        {
          publisher: "PolitiFact",
          rating: "False",
          review_url: "https://example.com",
          review_date: "2024-08-12",
          claim_text: "vaccines cause autism",
          language: "en",
        },
      ],
      fetched_at: 0,
      source: "google_fact_check_tools_v1alpha1",
    });
    render(withQuery(<SecondOpinionCard claim="vaccines cause autism" />));
    await waitFor(() =>
      expect(screen.getByTestId("second-opinion-list")).toBeInTheDocument(),
    );
    expect(screen.getByText("PolitiFact")).toBeInTheDocument();
    expect(screen.getByText("False")).toBeInTheDocument();
  });

  it("renders empty state when no results", async () => {
    mockFetch({
      claim: "x",
      results: [],
      fetched_at: 0,
      source: "google_fact_check_tools_v1alpha1",
    });
    render(withQuery(<SecondOpinionCard claim="x" />));
    await waitFor(() =>
      expect(screen.getByTestId("second-opinion-empty")).toBeInTheDocument(),
    );
  });
});
