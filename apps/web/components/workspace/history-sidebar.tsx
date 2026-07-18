"use client";

import { BookOpen, ChevronLeft, ChevronRight, Clock3, MoreHorizontal, Pin, Plus, Search, Settings2, Sparkles } from "lucide-react";
import type { ResearchSession } from "@/lib/types/domain";
import { StatusPill } from "@/components/ui/status-pill";

interface HistorySidebarProps {
  sessions: ResearchSession[];
  activeId: string | null;
  collapsed: boolean;
  onToggle: () => void;
  onSelect: (id: string) => void;
  onNew: () => void;
  onTutorial: () => void;
}

export function HistorySidebar({ sessions, activeId, collapsed, onToggle, onSelect, onNew, onTutorial }: HistorySidebarProps) {
  if (collapsed) {
    return (
      <aside className="sidebar sidebar-collapsed" aria-label="折叠导航栏">
        <div className="collapsed-mark"><Sparkles size={18} /></div>
        <button className="collapsed-button" onClick={onNew} aria-label="新建靶点研读"><Plus size={18} /></button>
        <button className="collapsed-button" onClick={onTutorial} aria-label="教程练习"><BookOpen size={18} /></button>
        <button className="collapsed-button sidebar-bottom" onClick={onToggle} aria-label="展开侧栏"><ChevronRight size={18} /></button>
      </aside>
    );
  }

  const pinned = sessions.filter((session) => session.pinned);
  const recent = sessions.filter((session) => !session.pinned);

  return (
    <aside className="sidebar" aria-label="会话历史">
      <div className="brand-row">
        <div className="brand-lockup"><div className="brand-icon"><Sparkles size={17} /></div><span>靶点梳理助手</span></div>
        <button className="icon-button sidebar-toggle" onClick={onToggle} aria-label="折叠侧栏"><ChevronLeft size={17} /></button>
      </div>

      <button className="new-research-button" onClick={onNew}><Plus size={17} /><span>新建靶点研读</span><kbd>⌘ K</kbd></button>

      <label className="sidebar-search">
        <Search size={16} aria-hidden="true" />
        <span className="sr-only">搜索会话</span>
        <input placeholder="搜索会话" aria-label="搜索会话" />
        <kbd>⌘ F</kbd>
      </label>

      <div className="sidebar-scroll">
        <SessionGroup label="固定" icon={<Pin size={13} />} sessions={pinned} activeId={activeId} onSelect={onSelect} />
        <SessionGroup label="最近 7 天" icon={<Clock3 size={13} />} sessions={recent} activeId={activeId} onSelect={onSelect} />
      </div>

      <div className="sidebar-footer">
        <button className="tutorial-entry" onClick={onTutorial}><span className="tutorial-entry-icon"><BookOpen size={15} /></span><span><strong>教程练习</strong><small>EGFR · 2 / 9 已解锁</small></span><ChevronRight size={15} /></button>
        <div className="user-row"><div className="avatar">S</div><span><strong>研究工作台</strong><small>Mock 演示模式</small></span><button className="icon-button" aria-label="打开设置"><Settings2 size={16} /></button></div>
      </div>
    </aside>
  );
}

function SessionGroup({ label, icon, sessions, activeId, onSelect }: { label: string; icon: React.ReactNode; sessions: ResearchSession[]; activeId: string | null; onSelect: (id: string) => void }) {
  return (
    <section className="session-group">
      <div className="session-group-label">{icon}<span>{label}</span></div>
      <div className="session-list">
        {sessions.map((session) => (
          <button key={session.id} className={`session-item ${activeId === session.id ? "session-item-active" : ""}`} onClick={() => onSelect(session.id)}>
            <span className="session-item-main"><span className={`session-status-dot session-status-${session.status.toLowerCase()}`} /><span className="session-title">{session.title}</span></span>
            <span className="session-item-meta"><span>{session.subtitle}</span><span>{session.updatedAt}</span></span>
            {session.status === "UPDATED" ? <StatusPill tone="amber" dot>需更新</StatusPill> : null}
            <MoreHorizontal className="session-more" size={16} aria-label={`${session.title} 更多操作`} />
          </button>
        ))}
      </div>
    </section>
  );
}
