import type { DecisionMemo, GroundedAnswer, ResearchSession, ScoreSnapshot, TargetCard, TutorialCourse } from "@/lib/types/domain";

export interface CreateSessionInput { question: string }
export interface ResearchInput { question: string; officialOnly?: boolean; forceRefresh?: boolean }
export interface AskInput { question: string; officialOnly?: boolean; reasoning?: boolean }
export interface ResearchJob { jobId: string; status: "QUEUED" | "RUNNING" | "READY"; eventsUrl: string }
export interface ResearchSessionDetail extends ResearchSession { question: string; targetCard?: TargetCard; score?: ScoreSnapshot; decisionMemo?: DecisionMemo }
export interface SessionMessageRecord { id: string; sessionId: string; role: "user" | "assistant"; content: string; createdAt: string; provider?: string; isMock?: boolean }
export interface SessionPatchInput { title?: string; pinned?: boolean }

export interface TargetLensClient {
  listSessions(): Promise<ResearchSession[]>;
  getSession(id: string): Promise<ResearchSessionDetail>;
  createSession(input: CreateSessionInput): Promise<ResearchSession>;
  startResearch(sessionId: string, input: ResearchInput): Promise<ResearchJob>;
  getTargetCard(sessionId: string): Promise<TargetCard>;
  getScores(sessionId: string): Promise<ScoreSnapshot>;
  getMessages(sessionId: string): Promise<SessionMessageRecord[]>;
  ask(sessionId: string, input: AskInput): Promise<GroundedAnswer>;
  patchSession(sessionId: string, input: SessionPatchInput): Promise<ResearchSession>;
  deleteSession(sessionId: string): Promise<void>;
  generateDecisionMemo(sessionId: string, question?: string): Promise<DecisionMemo>;
  getDecisionMemo(sessionId: string): Promise<DecisionMemo | null>;
  getTutorials(): Promise<TutorialCourse[]>;
}
