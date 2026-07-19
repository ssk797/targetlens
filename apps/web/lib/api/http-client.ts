import type { AskInput, CreateSessionInput, ResearchInput, ResearchJob, ResearchSessionDetail, SessionMessageRecord, SessionPatchInput, TargetLensClient } from "@/lib/api/client";
import type { DecisionMemo, GroundedAnswer, ResearchSession, ScoreSnapshot, TargetCard, TutorialCourse } from "@/lib/types/domain";

// The desktop browser may isolate `localhost` from the local API port while
// still allowing the explicit loopback address. Normalize the development
// default so the UI cannot silently fall back to the demo client.
const baseUrl = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000").replace("://localhost", "://127.0.0.1");

interface BackendAnswer {
  id: string;
  status: string;
  summary: string;
  question: string;
  data_cutoff: string;
  is_mock: boolean;
  provider?: string;
  provider_status?: string;
  reply_to?: string | null;
}

interface BackendSession {
  id: string;
  title: string;
  question: string;
  status: ResearchSession["status"];
  created_at: string;
  updated_at?: string | null;
  data_cutoff: string;
  subtitle?: string;
  pinned?: boolean;
  is_mock?: boolean;
}

interface BackendScore {
  base_opportunity: number;
  risk_burden: number;
  evidence_confidence: number;
  adjusted_score: number;
  recommendation: "GO" | "PILOT" | "HOLD" | "STOP";
  redlines: Array<{ id: string; name: string; rationale: string; evidence_ids: string[]; mitigable: boolean }>;
}

function normalizeScore(score: BackendScore): ScoreSnapshot {
  const recommendation = { GO: "GO", PILOT: "CONDITIONAL_GO", HOLD: "WATCH", STOP: "NO_GO" }[score.recommendation] as ScoreSnapshot["recommendation"];
  return {
    baseOpportunity: score.base_opportunity,
    riskBurden: score.risk_burden,
    evidenceConfidence: score.evidence_confidence,
    adjustedDirectionIndex: score.adjusted_score,
    recommendation,
    dimensions: [
      { label: "机会基础分", value: score.base_opportunity, note: "服务端规则引擎" },
      { label: "风险负担", value: score.risk_burden, note: "数值越高代表风险越重" },
      { label: "证据置信度", value: score.evidence_confidence, note: "来源覆盖、权威性与一致性" },
    ],
    redFlags: score.redlines.map((redline) => ({
      id: redline.id,
      title: redline.name,
      severity: "R3" as const,
      sourceId: redline.evidence_ids[0] ?? "",
      impact: redline.rationale,
      mitigable: redline.mitigable,
    })),
    ruleVersion: "targetlens-rules-v1",
  };
}

function normalizeSession(session: BackendSession): ResearchSession & { question: string } {
  return {
    id: session.id,
    title: session.title,
    subtitle: session.subtitle || "实时研究 · 待查看",
    status: session.status,
    updatedAt: session.updated_at ? new Date(session.updated_at).toLocaleString("zh-CN", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "刚刚",
    pinned: session.pinned ?? false,
    question: session.question,
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  if (!response.ok) throw new Error(`TargetLens API ${response.status}`);
  return response.json() as Promise<T>;
}

export const httpClient: TargetLensClient = {
  listSessions: async () => (await request<BackendSession[]>("/api/v1/sessions")).map(normalizeSession),
  getSession: async (id) => normalizeSession(await request<BackendSession>(`/api/v1/sessions/${id}`)) as ResearchSessionDetail,
  createSession: async (input: CreateSessionInput) => normalizeSession(await request<BackendSession>("/api/v1/sessions", { method: "POST", body: JSON.stringify(input) })),
  startResearch: async (sessionId: string, input: ResearchInput) => {
    const job = await request<{ job_id: string; status: ResearchJob["status"]; events_url: string }>(`/api/v1/sessions/${sessionId}/research`, { method: "POST", body: JSON.stringify({ question: input.question, official_only: input.officialOnly ?? false, force_refresh: input.forceRefresh ?? false }) });
    return { jobId: job.job_id, status: job.status, eventsUrl: job.events_url };
  },
  getTargetCard: (sessionId: string) => request<TargetCard>(`/api/v1/sessions/${sessionId}/target-card`),
  getScores: async (sessionId: string) => normalizeScore(await request<BackendScore>(`/api/v1/sessions/${sessionId}/scores`)),
  getMessages: async (sessionId: string): Promise<SessionMessageRecord[]> => {
    const messages = await request<Array<{ id: string; session_id: string; role: "user" | "assistant"; content: string; created_at: string; provider?: string; is_mock?: boolean; reply_to?: string | null }>>(`/api/v1/sessions/${sessionId}/messages`);
    return messages.map((message) => ({ id: message.id, sessionId: message.session_id, role: message.role, content: message.content, createdAt: message.created_at, provider: message.provider, isMock: message.is_mock, replyTo: message.reply_to }));
  },
  ask: async (sessionId: string, input: AskInput): Promise<GroundedAnswer> => {
    const answer = await request<BackendAnswer>(`/api/v1/sessions/${sessionId}/messages`, { method: "POST", body: JSON.stringify({ question: input.question, official_only: input.officialOnly ?? false, reasoning: input.reasoning ?? false }) });
    return {
      id: answer.id,
      status: answer.is_mock ? "PARTIAL" : "SUPPORTED",
      summary: answer.summary,
      claims: [],
      conflicts: answer.provider_status === "DEGRADED" ? ["DeepSeek 暂时不可用，当前回答未经过实时模型生成。"] : [],
      nextActions: ["回到证据抽屉核验来源", "补充适应证和药物形式后继续追问"],
      dataCutoff: answer.data_cutoff,
      provider: answer.provider ?? (answer.is_mock ? "mock" : "unknown"),
      replyTo: answer.reply_to,
    };
  },
  patchSession: async (sessionId: string, input: SessionPatchInput) => normalizeSession(await request<BackendSession>(`/api/v1/sessions/${sessionId}`, { method: "PATCH", body: JSON.stringify(input) })),
  deleteSession: async (sessionId: string) => { await request<unknown>(`/api/v1/sessions/${sessionId}`, { method: "DELETE" }); },
  generateDecisionMemo: (sessionId: string, question?: string) => request<DecisionMemo>(`/api/v1/sessions/${sessionId}/decision-memos`, { method: "POST", body: JSON.stringify(question ? { question } : {}) }),
  getDecisionMemo: (sessionId: string) => request<DecisionMemo | null>(`/api/v1/sessions/${sessionId}/decision-memos`),
  getTutorials: () => request<TutorialCourse[]>("/api/v1/tutorials"),
};
