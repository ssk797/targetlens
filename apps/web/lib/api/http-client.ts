import type { AskInput, CreateSessionInput, ResearchInput, ResearchJob, ResearchSessionDetail, TargetLensClient } from "@/lib/api/client";
import type { DecisionMemo, GroundedAnswer, ResearchSession, TargetCard, TutorialCourse } from "@/lib/types/domain";

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

interface BackendAnswer {
  id: string;
  status: string;
  summary: string;
  question: string;
  data_cutoff: string;
  is_mock: boolean;
  provider?: string;
  provider_status?: string;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  if (!response.ok) throw new Error(`TargetLens API ${response.status}`);
  return response.json() as Promise<T>;
}

export const httpClient: TargetLensClient = {
  listSessions: () => request<ResearchSession[]>("/api/v1/sessions"),
  getSession: (id) => request<ResearchSessionDetail>(`/api/v1/sessions/${id}`),
  createSession: (input: CreateSessionInput) => request<ResearchSession>("/api/v1/sessions", { method: "POST", body: JSON.stringify(input) }),
  startResearch: async (sessionId: string, input: ResearchInput) => request<ResearchJob>(`/api/v1/sessions/${sessionId}/research`, { method: "POST", body: JSON.stringify(input) }),
  getTargetCard: (sessionId: string) => request<TargetCard>(`/api/v1/sessions/${sessionId}/target-card`),
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
    };
  },
  generateDecisionMemo: (sessionId: string) => request<DecisionMemo>(`/api/v1/sessions/${sessionId}/decision-memos`, { method: "POST" }),
  getTutorials: () => request<TutorialCourse[]>("/api/v1/tutorials"),
};
