import type { ScoreSnapshot, TargetCard, DecisionMemo } from "@/lib/types/domain";

export function buildMarkdownReport(card: TargetCard, memo: DecisionMemo, score: ScoreSnapshot): string {
  return `# ${card.target.symbol} 靶点研读报告\n\n> ${card.metadata.disclaimer}\n\n- 研究范围：${card.scope.disease} · ${card.scope.modality}\n- 数据截至：${card.metadata.dataCutoff}\n- 卡片版本：V${card.version}\n- 推荐等级：${score.recommendation}\n\n## 结论\n\n${card.conclusions.verdict}\n\n## 证据摘要\n\n${card.validation.map((item) => `- [${item.level}] ${item.statement}（${item.source.organization}，${item.source.tier}）`).join("\\n")}\n\n## 风险与红线\n\n${card.risks.map((risk) => `- ${risk.severity} · ${risk.title}：${risk.impact}`).join("\\n")}\n\n## 差异化建议\n\n${memo.options.map((option) => `- ${option.priority} ${option.title}：${option.content}`).join("\\n")}\n\n## 评分\n\n- 机会基础分：${score.baseOpportunity}\n- 风险负担：${score.riskBurden}\n- 证据置信度：${score.evidenceConfidence}\n- 调整后方向指数：${score.adjustedDirectionIndex}\n\n## 免责声明\n\n${card.metadata.disclaimer}；本报告不替代药理、毒理、临床或监管判断。\n`;
}

export function downloadTextFile(filename: string, content: string): void {
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
