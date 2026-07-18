import type { DecisionMemo, GroundedAnswer, ResearchSession, ScoreSnapshot, TargetCard, TutorialCourse } from "@/lib/types/domain";

export interface CreateSessionInput { question: string }
export interface ResearchInput { question: string; officialOnly?: boolean }
export interface AskInput { question: string; officialOnly?: boolean; reasoning?: boolean }
export interface ResearchJob { jobId: string; status: "QUEUED" | "RUNNING" | "READY"; eventsUrl: string }
export interface ResearchSessionDetail extends ResearchSession { question: string; targetCard?: TargetCard; score?: ScoreSnapshot; decisionMemo?: DecisionMemo }

export interface TargetLensClient {
  listSessions(): Promise<ResearchSession[]>;
  getSession(id: string): Promise<ResearchSessionDetail>;
  createSession(input: CreateSessionInput): Promise<ResearchSession>;
  startResearch(sessionId: string, input: ResearchInput): Promise<ResearchJob>;
  getTargetCard(sessionId: string): Promise<TargetCard>;
  ask(sessionId: string, input: AskInput): Promise<GroundedAnswer>;
  generateDecisionMemo(sessionId: string): Promise<DecisionMemo>;
  getTutorials(): Promise<TutorialCourse[]>;
}
