import type { AskInput, CreateSessionInput, ResearchInput, ResearchJob, ResearchSessionDetail, TargetLensClient } from "@/lib/api/client";
import type { DecisionMemo, GroundedAnswer, ResearchSession, TargetCard, TutorialCourse } from "@/lib/types/domain";

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

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
  ask: (sessionId: string, input: AskInput) => request<GroundedAnswer>(`/api/v1/sessions/${sessionId}/messages`, { method: "POST", body: JSON.stringify(input) }),
  generateDecisionMemo: (sessionId: string) => request<DecisionMemo>(`/api/v1/sessions/${sessionId}/decision-memos`, { method: "POST" }),
  getTutorials: () => request<TutorialCourse[]>("/api/v1/tutorials"),
};
