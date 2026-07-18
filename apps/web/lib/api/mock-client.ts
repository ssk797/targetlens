import { mockAnswers, mockDecisionMemo, mockSessions, mockScore, mockTargetCard, mockTutorial } from "@/lib/mocks/data";
import type { TargetLensClient } from "@/lib/api/client";

export const mockClient: TargetLensClient = {
  async listSessions() { return mockSessions; },
  async getSession(id) { return { ...mockSessions.find((session) => session.id === id) ?? mockSessions[0], question: mockTargetCard.scope.question, targetCard: mockTargetCard, score: mockScore, decisionMemo: mockDecisionMemo }; },
  async createSession(input) { return { id: `session-${Date.now()}`, title: input.question.slice(0, 30), subtitle: "刚刚创建 · Mock", status: "DRAFT", updatedAt: "刚刚" }; },
  async startResearch(sessionId) { return { jobId: `job-${sessionId}`, status: "QUEUED", eventsUrl: `/api/v1/sessions/${sessionId}/events` }; },
  async getTargetCard() { return mockTargetCard; },
  async getScores() { return mockScore; },
  async getMessages(sessionId) { return [{ id: `message-${sessionId}`, sessionId, role: "user", content: mockTargetCard.scope.question, createdAt: new Date().toISOString(), isMock: true }]; },
  async ask(_sessionId, input) { return { ...mockAnswers[0], summary: `${mockAnswers[0].summary} 你的问题：${input.question}` }; },
  async patchSession(sessionId, input) { return { ...mockSessions.find((session) => session.id === sessionId) ?? mockSessions[0], ...(input.title ? { title: input.title } : {}), ...(input.pinned !== undefined ? { pinned: input.pinned } : {}) }; },
  async deleteSession() {},
  async generateDecisionMemo() { return mockDecisionMemo; },
  async getTutorials() { return [mockTutorial]; },
};
