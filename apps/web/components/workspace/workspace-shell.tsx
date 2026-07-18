"use client";

import { ArrowLeft, ChevronDown, Download, Menu, Plus, Search, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { mockAnswers, mockDecisionMemo, mockEvidence, mockScore, mockSessions, mockTargetCard } from "@/lib/mocks/data";
import type { EvidenceItem, GroundedAnswer } from "@/lib/types/domain";
import { EvidenceDrawer } from "@/components/workspace/evidence-drawer";
import { buildMarkdownReport, downloadTextFile } from "@/lib/utils/report";
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
const defaultQuestion = "ROR1 在三阴性乳腺癌中是否适合开发 ADC？";

export function WorkspaceShell() {
  const router = useRouter();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeId, setActiveId] = useState<string | null>("session-ror1");
  const [hasResearch, setHasResearch] = useState(true);
  const [progressIndex, setProgressIndex] = useState(5);
  const [isResearching, setIsResearching] = useState(false);
  const [drawerEvidence, setDrawerEvidence] = useState<EvidenceItem | null>(null);
  const [memoVisible, setMemoVisible] = useState(true);
  const [conversation, setConversation] = useState<ConversationItem[]>([]);
  const [answerIndex, setAnswerIndex] = useState(0);
  const [isAsking, setIsAsking] = useState(false);
  const [composerSeed, setComposerSeed] = useState("");

  useEffect(() => {
    if (!isResearching) return;
    const timer = window.setInterval(() => {
      setProgressIndex((current) => {
        const next = Math.min(current + 1, progressSequence.length - 1);
        if (next === progressSequence.length - 1) {
          window.clearInterval(timer);
          window.setTimeout(() => setIsResearching(false), 650);
        }
        return next;
      });
    }, 560);
    return () => window.clearInterval(timer);
  }, [isResearching]);

  const currentSession = useMemo(() => mockSessions.find((session) => session.id === activeId), [activeId]);
  const stage = progressSequence[progressIndex];

  const startResearch = (question: string) => {
    setActiveId("session-ror1");
    setHasResearch(true);
    setComposerSeed("");
    setConversation([{ kind: "user", text: question }]);
    setMemoVisible(false);
    setProgressIndex(0);
    setIsResearching(true);
  };

  const handleAsk = async (question: string) => {
    setConversation((current) => [...current, { kind: "user", text: question }]);
    setIsAsking(true);
    try {
      const answer = await httpClient.ask(activeId ?? "session-ror1", { question });
      setConversation((current) => [...current, { kind: "answer", answer }]);
    } catch {
      const answer = mockAnswers[answerIndex % mockAnswers.length];
      setConversation((current) => [...current, { kind: "answer", answer }]);
      setAnswerIndex((current) => current + 1);
    } finally {
      setIsAsking(false);
    }
  };

  const handleNew = () => {
    setActiveId(null);
    setHasResearch(false);
    setConversation([]);
    setMemoVisible(false);
    setIsResearching(false);
    setIsAsking(false);
    setComposerSeed("");
    setProgressIndex(0);
    setDrawerEvidence(null);
  };

  const handleSelect = (id: string) => {
    setActiveId(id);
    setHasResearch(id === "session-ror1");
    setConversation(id === "session-ror1" ? [] : []);
    setMemoVisible(id === "session-ror1");
  };

  const openEvidence = (id: string) => {
    const evidence = mockEvidence.find((item) => item.id === id);
    if (evidence) setDrawerEvidence(evidence);
  };

  const exportReport = () => downloadTextFile("targetlens-ror1-research-report.md", buildMarkdownReport(mockTargetCard, mockDecisionMemo, mockScore));

  return (
    <div className="app-shell">
      <HistorySidebar sessions={mockSessions} activeId={activeId} collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed((value) => !value)} onSelect={handleSelect} onNew={handleNew} onTutorial={() => router.push("/tutorial")} />
      <main className="main-viewport">
        <header className="session-topbar">
          <div className="breadcrumb"><button className="mobile-menu icon-button" onClick={() => setSidebarCollapsed(false)} aria-label="打开导航"><Menu size={20} /></button><span>靶点研读</span><span className="breadcrumb-separator">/</span><strong>{currentSession?.title ?? "新建研读"}</strong></div>
          <div className="topbar-actions"><span className="mock-mode-label"><span className="live-dot" />Mock 模式</span><button className="topbar-button"><Search size={15} />搜索</button><button className="topbar-button"><Download size={15} />导出</button><button className="icon-button" aria-label="更多会话操作"><ChevronDown size={16} /></button></div>
        </header>

        <div className="conversation-viewport">
          {!hasResearch ? <EmptyWorkspace onPreset={setComposerSeed} onTutorial={() => router.push("/tutorial")} /> : <div className="conversation-column">
            <div className="conversation-intro"><span className="conversation-date">今天 · 14:32</span><span className="intro-rule" /><span className="conversation-cutoff">数据截至 {mockTargetCard.metadata.dataCutoff}</span></div>
            {conversation.length > 0 ? conversation.map((item, index) => item.kind === "user" ? <UserMessage key={`user-${index}`} text={item.text} /> : <GroundedAnswerCard key={item.answer.id} answer={item.answer} onEvidence={openEvidence} />) : <UserMessage text={defaultQuestion} />}
            {isResearching ? <ResearchProgress stage={stage} onRetry={() => setProgressIndex(Math.max(progressIndex - 1, 0))} /> : null}
            {!isResearching ? <TargetCard card={mockTargetCard} onEvidence={setDrawerEvidence} onExport={exportReport} /> : null}
            {!isResearching && memoVisible ? <DecisionMemo memo={mockDecisionMemo} /> : null}
            {!isResearching ? <ScorePanel score={mockScore} onEvidence={openEvidence} /> : null}
            {!isResearching && !memoVisible ? <button className="generate-memo-banner" onClick={() => setMemoVisible(true)}><span><Sparkles size={17} /><strong>生成差异化立项建议</strong><small>结合当前靶点卡、风险和竞争空间形成结构化 Decision Memo</small></span><ArrowLeft size={17} className="turn-right" /></button> : null}
          </div>}
        </div>
        <ResearchComposer initialValue={composerSeed} onSubmit={hasResearch ? handleAsk : startResearch} onDecision={() => setMemoVisible(true)} onExport={exportReport} disabled={isResearching || isAsking} />
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
  return <div className="empty-workspace"><div className="empty-kicker"><span className="kicker-line" />TargetLens / Research workspace<span className="kicker-line" /></div><div className="empty-hero-mark"><div className="hero-ring hero-ring-one" /><div className="hero-ring hero-ring-two" /><div className="hero-core"><Sparkles size={26} /></div></div><h1>快速读懂一个肿瘤靶点</h1><p className="empty-subtitle">整合权威数据库、论文、临床试验与指南，<br />生成可追溯靶点卡，并支持连续追问与立项分析。</p><div className="preset-heading"><span>从一个研究方向开始</span><small>选择后会带入下方输入框</small></div><div className="preset-grid" aria-label="研究方向快捷入口">{presets.map(([label, description]) => <button key={label} className="preset-card" onClick={() => onPreset(`${label}：${description}`)}><strong>{label}</strong><span>{description}</span></button>)}</div><div className="authority-row"><span>权威来源</span><strong>Open Targets</strong><i>·</i><strong>UniProt</strong><i>·</i><strong>PubMed</strong><i>·</i><strong>ClinicalTrials.gov</strong><i>·</i><strong>ChEMBL</strong></div><p className="empty-disclaimer">演示数据仅用于展示产品流程，不用于真实研发判断。<button onClick={onTutorial}>先去学习靶点研读方法 <ArrowLeft size={15} className="turn-right" /></button></p></div>;
}
