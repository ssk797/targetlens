"use client";

import { ArrowLeft, ChevronDown, Download, Menu, RefreshCw, Search, Sparkles } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { mockSessions, mockTargetCard } from "@/lib/mocks/data";
import type { DecisionMemo as DecisionMemoData, EvidenceItem, GroundedAnswer, ResearchSession, ScoreSnapshot, TargetCard as TargetCardData } from "@/lib/types/domain";
import { EvidenceDrawer } from "@/components/workspace/evidence-drawer";
import { downloadTextFile } from "@/lib/utils/report";
import { HistorySidebar } from "@/components/workspace/history-sidebar";
import { UserMessage, GroundedAnswerCard } from "@/components/workspace/chat-message";
import { ResearchComposer } from "@/components/workspace/research-composer";
import { ResearchProgress } from "@/components/workspace/research-progress";
import { TargetCard } from "@/components/workspace/target-card";
import { DecisionMemo } from "@/components/workspace/decision-memo";
import { ScorePanel } from "@/components/workspace/score-panel";
import { httpClient } from "@/lib/api/http-client";

export type ResearchStage = "RESOLVING_ENTITY" | "FETCHING_STRUCTURED_DATA" | "RETRIEVING_LITERATURE" | "BUILDING_GRAPH" | "GENERATING_CARD" | "READY";

type ConversationItem = { kind: "user"; text: string } | { kind: "answer"; answer: GroundedAnswer };
const progressSequence: ResearchStage[] = ["RESOLVING_ENTITY", "FETCHING_STRUCTURED_DATA", "RETRIEVING_LITERATURE", "BUILDING_GRAPH", "GENERATING_CARD", "READY"];
const differentiationRequestPattern = /(?:生成|输出|给我|制定|做)?差异化(?:立项)?建议/;

function isDifferentiationRequest(question: string) {
  return differentiationRequestPattern.test(question.replace(/\s+/g, ""));
}

function answerFromHistory(message: { id: string; content: string; provider?: string; isMock?: boolean; createdAt: string }): GroundedAnswer {
  const isLive = message.provider === "deepseek" && !message.isMock;
  return {
    id: message.id,
    status: isLive ? "SUPPORTED" : "PARTIAL",
    summary: message.content,
    claims: [],
    conflicts: isLive ? [] : ["这条回答没有附带新的逐条引文，请打开当前靶点卡来源复核。"],
    nextActions: ["回到当前靶点卡核验来源", "补充适应证和药物形式后继续追问"],
    dataCutoff: message.createdAt.slice(0, 10),
    provider: message.provider ?? (message.isMock ? "mock" : "unknown"),
  };
}

export function WorkspaceShell() {
  const router = useRouter();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [sessions, setSessions] = useState<ResearchSession[]>(mockSessions);
  const [activeId, setActiveId] = useState<string | null>("session-ror1");
  const [hasResearch, setHasResearch] = useState(true);
  const [progressIndex, setProgressIndex] = useState(5);
  const [isResearching, setIsResearching] = useState(false);
  const [loadingSession, setLoadingSession] = useState(false);
  const [drawerEvidence, setDrawerEvidence] = useState<EvidenceItem | null>(null);
  const [memoVisible, setMemoVisible] = useState(false);
  const [currentCard, setCurrentCard] = useState<TargetCardData | null>(null);
  const [currentMemo, setCurrentMemo] = useState<DecisionMemoData | null>(null);
  const [currentScore, setCurrentScore] = useState<ScoreSnapshot | null>(null);
  const [conversation, setConversation] = useState<ConversationItem[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [composerSeed, setComposerSeed] = useState("");
  const [sourceMode, setSourceMode] = useState("实时来源");
  const [officialOnly, setOfficialOnly] = useState(false);
  const [topbarMenuOpen, setTopbarMenuOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement | null>(null);

  const focusSessionSearch = useCallback(() => {
    setSidebarCollapsed(false);
    window.setTimeout(() => searchInputRef.current?.focus(), 0);
  }, []);

  const currentSession = useMemo(() => sessions.find((session) => session.id === activeId), [activeId, sessions]);
  const stage = progressSequence[progressIndex];
  const firstFollowUpIndex = conversation.findIndex((item, index) => index > 0 && item.kind === "user");
  const conversationBeforeCard = firstFollowUpIndex === -1 ? conversation : conversation.slice(0, firstFollowUpIndex);
  const conversationAfterCard = firstFollowUpIndex === -1 ? [] : conversation.slice(firstFollowUpIndex);

  useEffect(() => {
    if (!isResearching) return;
    const timer = window.setInterval(() => setProgressIndex((current) => Math.min(current + 1, progressSequence.length - 1)), 700);
    return () => window.clearInterval(timer);
  }, [isResearching]);

  useEffect(() => {
    const handleShortcut = (event: KeyboardEvent) => {
      if (!(event.ctrlKey || event.metaKey) || event.key.toLowerCase() !== "f") return;
      const target = event.target as HTMLElement | null;
      if (target?.tagName === "INPUT" || target?.tagName === "TEXTAREA") return;
      event.preventDefault();
      focusSessionSearch();
    };
    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, [focusSessionSearch]);

  const loadSession = useCallback(async (id: string) => {
    setActiveId(id);
    window.sessionStorage.setItem("targetlens.activeSession", id);
    setLoadingSession(true);
    setDrawerEvidence(null);
    try {
      const [detail, card, messages, score] = await Promise.all([httpClient.getSession(id), httpClient.getTargetCard(id), httpClient.getMessages(id), httpClient.getScores(id)]);
      const displayDetail = detail.title.startsWith("未解析靶点") && card.target.symbol !== "未解析靶点" ? { ...detail, title: `${card.target.symbol} · ${card.scope.disease || "新建研读"}` } : detail;
      setSessions((existing) => existing.some((session) => session.id === displayDetail.id) ? existing.map((session) => session.id === displayDetail.id ? { ...session, ...displayDetail } : session) : [...existing, displayDetail]);
      setCurrentCard(card);
      setSourceMode(card.metadata.isMock ? "离线缓存" : "实时来源");
      setOfficialOnly(false);
      setHasResearch(true);
      setConversation(messages.map((message) => message.role === "user" ? { kind: "user", text: message.content } : { kind: "answer", answer: answerFromHistory(message) }));
      setCurrentMemo(null);
      setMemoVisible(false);
      setCurrentScore(score);
    } catch {
      // Keep the workspace usable when the API is temporarily unavailable, but
      // label the fallback explicitly instead of presenting it as live data.
      if (id === "session-ror1") {
        setCurrentCard(mockTargetCard);
        setSourceMode("离线缓存");
        setConversation([]);
        setCurrentScore(null);
        setHasResearch(true);
      } else {
        setHasResearch(false);
        setCurrentCard(null);
        setCurrentScore(null);
      }
    } finally {
      setLoadingSession(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    const initializeWorkspace = async () => {
      try {
        const remoteSessions = await httpClient.listSessions();
        if (cancelled) return;
        if (remoteSessions.length > 0) setSessions(remoteSessions);
        const storedId = window.sessionStorage.getItem("targetlens.activeSession");
        const initialId = storedId && remoteSessions.some((session) => session.id === storedId) ? storedId : remoteSessions[0]?.id ?? "session-ror1";
        await loadSession(initialId);
      } catch {
        if (!cancelled) await loadSession("session-ror1");
      }
    };
    void initializeWorkspace();
    return () => { cancelled = true; };
  }, [loadSession]);

  const startResearch = async (question: string) => {
    setIsResearching(true);
    setProgressIndex(0);
    setComposerSeed("");
    setConversation([{ kind: "user", text: question }]);
    setCurrentCard(null);
    setCurrentMemo(null);
    setMemoVisible(false);
    setCurrentScore(null);
    try {
      const session = await httpClient.createSession({ question });
      setSessions((existing) => [session, ...existing.filter((item) => item.id !== session.id)]);
      setActiveId(session.id);
      window.sessionStorage.setItem("targetlens.activeSession", session.id);
      setHasResearch(true);
      await httpClient.startResearch(session.id, { question, officialOnly });
      const [card, score] = await Promise.all([httpClient.getTargetCard(session.id), httpClient.getScores(session.id)]);
      setCurrentCard(card);
      setCurrentScore(score);
      setSourceMode(card.metadata.isMock ? "离线模式" : "实时来源");
      setSessions((existing) => existing.map((item) => item.id === session.id ? { ...item, status: "READY", subtitle: `${card.target.symbol} · ${card.scope.disease} · 实时更新` } : item));
      setProgressIndex(progressSequence.length - 1);
    } catch {
      setConversation((existing) => [...existing, { kind: "answer", answer: { id: `error-${Date.now()}`, status: "REVIEW_REQUIRED", summary: "本次检索没有完成。请检查 API、网络连接器状态后重试；不会用 ROR1 演示卡替代你的问题。", claims: [], conflicts: ["检索任务失败或来源暂时不可用。"], nextActions: ["点击重试", "检查来源状态"], dataCutoff: new Date().toISOString().slice(0, 10), provider: "system" } }]);
    } finally {
      setIsResearching(false);
    }
  };

  const handleAsk = async (question: string) => {
    if (!activeId) return startResearch(question);
    if (currentCard && isDifferentiationRequest(question)) {
      await generateMemo(question);
      return;
    }
    setConversation((current) => [...current, { kind: "user", text: question }]);
    setIsAsking(true);
    try {
      const answer = await httpClient.ask(activeId, { question, officialOnly });
      setConversation((current) => [...current, { kind: "answer", answer }]);
    } catch {
      setConversation((current) => [...current, { kind: "answer", answer: { id: `error-${Date.now()}`, status: "REVIEW_REQUIRED", summary: `当前问题仍属于“${currentCard?.scope.question ?? currentSession?.title ?? "本会话"}”的连续追问，但回答服务暂时不可用。`, claims: [], conflicts: ["没有丢弃已有会话上下文，请稍后重试。"], nextActions: ["重试本轮问题", "打开当前靶点卡来源"], dataCutoff: currentCard?.metadata.dataCutoff ?? new Date().toISOString().slice(0, 10), provider: "system" } }]);
    } finally {
      setIsAsking(false);
    }
  };

  const refreshResearch = async () => {
    if (!activeId || !currentCard || isResearching) return;
    setIsResearching(true);
    setProgressIndex(0);
    try {
      await httpClient.startResearch(activeId, { question: currentCard.scope.question, officialOnly, forceRefresh: true });
      const [card, score] = await Promise.all([httpClient.getTargetCard(activeId), httpClient.getScores(activeId)]);
      setCurrentCard(card);
      setCurrentScore(score);
      setSourceMode(card.metadata.isMock ? "离线模式" : "实时来源");
    } catch {
      setConversation((existing) => [...existing, { kind: "answer", answer: { id: `refresh-${Date.now()}`, status: "REVIEW_REQUIRED", summary: "刷新没有完成，保留当前靶点卡和会话上下文。", claims: [], conflicts: ["至少一个来源暂时不可用。"], nextActions: ["稍后重试刷新", "查看当前来源状态"], dataCutoff: currentCard.metadata.dataCutoff, provider: "system" } }]);
    } finally {
      setIsResearching(false);
      setProgressIndex(progressSequence.length - 1);
    }
  };

  const handleNew = () => {
    setActiveId(null);
    window.sessionStorage.removeItem("targetlens.activeSession");
    setHasResearch(false);
    setConversation([]);
    setCurrentCard(null);
    setCurrentMemo(null);
    setMemoVisible(false);
    setIsResearching(false);
    setIsAsking(false);
    setComposerSeed("");
    setProgressIndex(0);
    setDrawerEvidence(null);
    setSourceMode("实时来源");
    setOfficialOnly(false);
  };

  const handleRename = async (id: string, title: string) => {
    const nextTitle = window.prompt("给这条研读记录命名", title);
    if (!nextTitle?.trim()) return;
    try {
      const updated = await httpClient.patchSession(id, { title: nextTitle.trim() });
      setSessions((existing) => existing.map((session) => session.id === id ? { ...session, ...updated } : session));
    } catch {
      setSessions((existing) => existing.map((session) => session.id === id ? { ...session, title: nextTitle.trim() } : session));
    }
  };

  const handleTogglePin = async (id: string) => {
    const session = sessions.find((item) => item.id === id);
    if (!session) return;
    const pinned = !session.pinned;
    setSessions((existing) => existing.map((item) => item.id === id ? { ...item, pinned } : item));
    try { await httpClient.patchSession(id, { pinned }); } catch { /* local state remains useful offline */ }
  };

  const handleDelete = async (id: string) => {
    setSessions((existing) => existing.filter((session) => session.id !== id));
    try { await httpClient.deleteSession(id); } catch { /* API may already have removed it */ }
    if (activeId === id) handleNew();
  };

  const exportReport = () => {
    if (!currentCard) return;
    const evidence = currentCard.validation.map((item) => `- [${item.level}] ${item.statement}（${item.source.organization}，${item.source.tier}）`).join("\n");
    const content = `# ${currentCard.target.symbol} 靶点研读报告\n\n> ${currentCard.metadata.disclaimer}\n\n- 研究范围：${currentCard.scope.disease} · ${currentCard.scope.modality}\n- 数据截至：${currentCard.metadata.dataCutoff}\n- 卡片版本：V${currentCard.version}\n\n## 结论\n\n${currentCard.conclusions.verdict}\n\n## 证据摘要\n\n${evidence || "暂无可用证据"}\n\n## 风险\n\n${currentCard.risks.map((risk) => `- ${risk.severity} · ${risk.title}：${risk.impact}`).join("\n")}\n`;
    downloadTextFile(`targetlens-${currentCard.target.symbol.toLowerCase()}-research-report.md`, content);
  };

  const generateMemo = async (triggerQuestion?: string) => {
    if (!activeId || !currentCard) return;
    if (triggerQuestion) setConversation((current) => [...current, { kind: "user", text: triggerQuestion }]);
    setIsAsking(true);
    try {
      const memo = await httpClient.generateDecisionMemo(activeId);
      setCurrentMemo(memo);
      setMemoVisible(true);
    } catch {
      setConversation((existing) => [...existing, { kind: "answer", answer: { id: `memo-error-${Date.now()}`, status: "REVIEW_REQUIRED", summary: "当前立项建议生成失败，已保留靶点卡和会话上下文；请稍后重试。", claims: [], conflicts: ["Decision Memo 服务暂时不可用。"], nextActions: ["稍后重试生成建议", "先从证据抽屉核验来源"], dataCutoff: currentCard.metadata.dataCutoff, provider: "system" } }]);
    } finally {
      setIsAsking(false);
    }
  };

  const openEvidence = (id: string) => {
    const evidence = currentCard?.validation.find((item) => item.id === id);
    if (evidence) setDrawerEvidence(evidence);
  };

  const referenceCurrentCard = () => {
    if (!currentCard) return;
    setComposerSeed(`请基于当前 ${currentCard.target.symbol} 靶点卡，引用相关证据并说明当前最关键的限制。`);
  };

  return (
    <div className="app-shell">
      <HistorySidebar sessions={sessions} activeId={activeId} collapsed={sidebarCollapsed} searchInputRef={searchInputRef} settingsOpen={settingsOpen} officialOnly={officialOnly} onSettings={() => setSettingsOpen((value) => !value)} onToggleOfficial={() => setOfficialOnly((value) => !value)} onToggle={() => setSidebarCollapsed((value) => !value)} onSelect={(id) => void loadSession(id)} onNew={handleNew} onTutorial={() => router.push("/tutorial")} onRename={handleRename} onTogglePin={handleTogglePin} onDelete={handleDelete} onExport={exportReport} />
      <main className="main-viewport">
        <header className="session-topbar">
          <div className="breadcrumb"><button className="mobile-menu icon-button" onClick={() => setSidebarCollapsed(false)} aria-label="打开导航"><Menu size={20} /></button><span>靶点研读</span><span className="breadcrumb-separator">/</span><strong>{currentSession?.title ?? "新建研读"}</strong></div>
          <div className="topbar-actions"><span className="mock-mode-label"><span className="live-dot" />{sourceMode}</span><button className="topbar-button" onClick={focusSessionSearch}><Search size={15} />搜索</button><button className="topbar-button" onClick={exportReport} disabled={!currentCard}><Download size={15} />导出</button><div className="topbar-menu-wrap"><button className="icon-button" aria-label="更多会话操作" aria-expanded={topbarMenuOpen} onClick={() => setTopbarMenuOpen((value) => !value)}><ChevronDown size={16} /></button>{topbarMenuOpen ? <div className="topbar-menu" role="menu" aria-label="会话操作"><button role="menuitem" onClick={() => { setTopbarMenuOpen(false); void refreshResearch(); }} disabled={!currentCard || isResearching}><RefreshCw size={14} />刷新当前来源</button><button role="menuitem" onClick={() => { setTopbarMenuOpen(false); handleNew(); }}><Sparkles size={14} />新建靶点研读</button><button role="menuitem" onClick={() => { setTopbarMenuOpen(false); setOfficialOnly((value) => !value); }}><span className="menu-check">{officialOnly ? "✓" : "○"}</span>仅使用官方来源</button></div> : null}</div></div>
        </header>

        <div className="conversation-viewport">
          {!hasResearch ? <EmptyWorkspace onPreset={setComposerSeed} onTutorial={() => router.push("/tutorial")} /> : <div className="conversation-column">
            <div className="conversation-intro"><span className="conversation-date">当前会话</span><span className="intro-rule" /><span className="conversation-cutoff">数据截至 {currentCard?.metadata.dataCutoff ?? "检索完成后"}</span></div>
            {conversationBeforeCard.map((item, index) => item.kind === "user" ? <UserMessage key={`user-${index}`} text={item.text} /> : <GroundedAnswerCard key={item.answer.id} answer={item.answer} onEvidence={openEvidence} />)}
            {(isResearching || (loadingSession && !currentCard)) ? <ResearchProgress stage={stage} onRetry={() => setProgressIndex(Math.max(progressIndex - 1, 0))} /> : null}
            {!isResearching && currentCard ? <TargetCard card={currentCard} onEvidence={setDrawerEvidence} onExport={exportReport} onRefresh={() => void refreshResearch()} officialOnly={officialOnly} onToggleOfficial={() => setOfficialOnly((value) => !value)} /> : null}
            {!isResearching && currentScore ? <ScorePanel score={currentScore} onEvidence={openEvidence} /> : null}
            {conversationAfterCard.map((item, index) => item.kind === "user" ? <UserMessage key={`follow-up-user-${index}`} text={item.text} /> : <GroundedAnswerCard key={item.answer.id} answer={item.answer} onEvidence={openEvidence} />)}
            {!isResearching && currentCard && memoVisible && currentMemo ? <DecisionMemo memo={currentMemo} sourceMode={sourceMode === "实时来源" ? "实时规则" : sourceMode} /> : null}
          </div>}
        </div>
        <ResearchComposer initialValue={composerSeed} onSubmit={hasResearch ? handleAsk : startResearch} onDecision={() => void generateMemo()} onReference={currentCard ? referenceCurrentCard : undefined} onExport={exportReport} disabled={isResearching || isAsking} sourceMode={sourceMode} officialOnly={officialOnly} onToggleOfficial={() => setOfficialOnly((value) => !value)} placeholder={hasResearch ? "继续追问当前靶点，或补充适应证、药物形式…" : "输入靶点或研究问题，例如：JAK2 在 MPN 中是否适合开发小分子？"} />
      </main>
      <EvidenceDrawer evidence={drawerEvidence} onClose={() => setDrawerEvidence(null)} />
    </div>
  );
}

function EmptyWorkspace({ onPreset, onTutorial }: { onPreset: (question: string) => void; onTutorial: () => void }) {
  const presets = [
    ["靶点身份", "确认标准实体、别名和蛋白关系"],
    ["患者分层", "寻找可检测的人群和标志物"],
    ["药物形式", "比较 ADC、双抗和小分子逻辑"],
    ["临床进展", "查看试验阶段与项目状态"],
    ["安全窗口", "检查正常组织表达与红线"],
    ["竞争格局", "梳理同靶点项目和差异化"],
    ["文献综述", "汇总最新论文与证据强度"],
    ["立项建议", "生成可验证、可退出的下一步"],
  ] as const;
  return <div className="empty-workspace"><div className="empty-kicker"><span className="kicker-line" />TargetLens · 真实研究工作台<span className="kicker-line" /></div><div className="empty-hero-mark"><div className="hero-ring hero-ring-one" /><div className="hero-ring hero-ring-two" /><div className="hero-core"><Sparkles size={26} /></div></div><h1>从一个靶点问题开始</h1><p className="empty-subtitle">输入基因、蛋白或研究问题，系统会按步骤检索权威来源，<br />整理为可追溯的小卡片，再支持连续追问。</p><div className="preset-heading"><span>你可以先看这几类问题</span><small>点击后仍需提交才会开始检索</small></div><div className="preset-grid" aria-label="研究方向快捷入口">{presets.map(([label, description]) => <button key={label} className="preset-card" onClick={() => onPreset(`${label}：${description}`)}><strong>{label}</strong><span>{description}</span></button>)}</div><div className="authority-row"><span>检索来源</span><strong>Open Targets</strong><i>·</i><strong>UniProt</strong><i>·</i><strong>PubMed</strong><i>·</i><strong>ClinicalTrials.gov</strong><i>·</i><strong>ChEMBL</strong></div><p className="empty-disclaimer">每次提交都会按当前靶点重新检索，不会复用其他会话的靶点卡。<button onClick={onTutorial}>了解研读步骤 <ArrowLeft size={15} className="turn-right" /></button></p></div>;
}
