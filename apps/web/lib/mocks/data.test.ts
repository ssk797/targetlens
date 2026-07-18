import { describe, expect, it } from "vitest";
import { mockDecisionMemo, mockScore, mockTargetCard } from "@/lib/mocks/data";
import { buildMarkdownReport } from "@/lib/utils/report";

describe("TargetLens demo fixtures", () => {
  it("keeps the target card evidence-aware", () => {
    expect(mockTargetCard.metadata.isMock).toBe(true);
    expect(mockTargetCard.validation.length).toBeGreaterThanOrEqual(5);
    expect(mockTargetCard.validation.every((item) => item.source.retrievedAt)).toBe(true);
  });

  it("keeps the red line separate from the recommendation score", () => {
    expect(mockScore.redFlags.length).toBeGreaterThan(0);
    expect(mockScore.recommendation).toBe("CONDITIONAL_GO");
    expect(mockScore.adjustedDirectionIndex).toBeLessThan(mockScore.baseOpportunity);
  });

  it("exports the current card version with its evidence boundary", () => {
    const report = buildMarkdownReport(mockTargetCard, mockDecisionMemo, mockScore);
    expect(report).toContain("ROR1 靶点研读报告");
    expect(report).toContain("2026-07-18");
    expect(report).toContain("正常组织窗口尚未锁定");
  });
});
