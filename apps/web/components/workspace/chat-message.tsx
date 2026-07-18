import { CheckCheck, CircleAlert, MessageSquareQuote } from "lucide-react";
import type { GroundedAnswer } from "@/lib/types/domain";
import { EvidenceBadge } from "@/components/ui/evidence-badge";

export function UserMessage({ text }: { text: string }) {
  return <div className="message-row message-row-user"><div className="user-message"><span>{text}</span><small>刚刚</small></div><div className="message-avatar">S</div></div>;
}

export function GroundedAnswerCard({ answer, onEvidence }: { answer: GroundedAnswer; onEvidence: (id: string) => void }) {
  const statusLabels = { SUPPORTED: "证据充分", PARTIAL: "部分支持", INSUFFICIENT_EVIDENCE: "证据不足", CONFLICTING_EVIDENCE: "存在冲突", REVIEW_REQUIRED: "需要复核" };
  const providerLabel = answer.provider === "deepseek" && answer.status === "SUPPORTED" ? "DeepSeek · grounded route" : "Mock grounded answer";
  return <div className="message-row message-row-assistant"><div className="assistant-mark"><MessageSquareQuote size={16} /></div><div className="answer-card"><div className="answer-card-head"><span className={`answer-status answer-${answer.status.toLowerCase()}`}>{answer.status === "SUPPORTED" ? <CheckCheck size={14} /> : <CircleAlert size={14} />}{statusLabels[answer.status]}</span><span className="answer-cutoff">数据截至 {answer.dataCutoff}</span></div><p className="answer-summary">{answer.summary}</p><div className="claim-list">{answer.claims.map((claim) => <div className="claim-row" key={claim.id}><span className="claim-mark">—</span><div><p>{claim.statement}</p><div className="claim-meta">{claim.evidenceIds.map((evidenceId) => <button key={evidenceId} onClick={() => onEvidence(evidenceId)}><EvidenceBadge level={evidenceId.includes("window") ? "E5" : evidenceId.includes("clinical") ? "E4" : "E3"} /> {evidenceId.replace("ev-", "")}</button>)}<span>置信度 {claim.certainty}</span></div></div></div>)}</div>{answer.conflicts.length > 0 ? <div className="conflict-note"><CircleAlert size={14} /><span>{answer.conflicts.join("；")}</span></div> : null}<div className="answer-footer"><div><span className="mini-label">下一步</span><span>{answer.nextActions.join(" · ")}</span></div><span className="generated-label">{providerLabel}</span></div></div></div>;
}
