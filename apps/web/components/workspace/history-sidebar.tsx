"use client";

import { BookOpen, ChevronLeft, ChevronRight, Clock3, Download, MoreHorizontal, Pencil, Pin, Plus, Search, Settings2, Sparkles, Trash2 } from "lucide-react";
import { useState } from "react";
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
  onRename: (id: string, title: string) => void;
  onTogglePin: (id: string) => void;
  onDelete: (id: string) => void;
  onExport: () => void;
  searchInputRef?: React.RefObject<HTMLInputElement | null>;
  settingsOpen?: boolean;
  officialOnly?: boolean;
  onSettings: () => void;
  onToggleOfficial?: () => void;
}

export function HistorySidebar({ sessions, activeId, collapsed, onToggle, onSelect, onNew, onTutorial, onRename, onTogglePin, onDelete, onExport, searchInputRef, settingsOpen = false, officialOnly = false, onSettings, onToggleOfficial }: HistorySidebarProps) {
  const [query, setQuery] = useState("");

  if (collapsed) {
    return <><aside className="sidebar sidebar-collapsed" aria-label="折叠导航栏"><div className="collapsed-mark"><Sparkles size={22} /></div><button className="collapsed-button" onClick={onNew} aria-label="新建靶点研读"><Plus size={20} /></button><button className="collapsed-button" onClick={onTutorial} aria-label="教程练习"><BookOpen size={20} /></button><button className="collapsed-button sidebar-bottom" onClick={onToggle} aria-label="展开侧栏"><ChevronRight size={20} /></button></aside><button className="sidebar-reopen" onClick={onToggle} aria-label="展开侧栏"><ChevronRight size={20} /></button></>;
  }

  const normalizedQuery = query.trim().toLocaleLowerCase();
  const filteredSessions = normalizedQuery
    ? sessions.filter((session) => `${session.title} ${session.subtitle}`.toLocaleLowerCase().includes(normalizedQuery))
    : sessions;
  const pinned = filteredSessions.filter((session) => session.pinned);
  const recent = filteredSessions.filter((session) => !session.pinned);

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
        <input ref={searchInputRef} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索会话" aria-label="搜索会话" />
        <kbd>Ctrl F</kbd>
      </label>

      <div className="sidebar-scroll">
        <SessionGroup label="固定" icon={<Pin size={13} />} sessions={pinned} activeId={activeId} onSelect={onSelect} onRename={onRename} onTogglePin={onTogglePin} onDelete={onDelete} onExport={onExport} />
        <SessionGroup label="最近 7 天" icon={<Clock3 size={13} />} sessions={recent} activeId={activeId} onSelect={onSelect} onRename={onRename} onTogglePin={onTogglePin} onDelete={onDelete} onExport={onExport} />
        {normalizedQuery && filteredSessions.length === 0 ? <div className="session-empty"><span>没有匹配的研读记录</span><button onClick={() => setQuery("")}>清除搜索</button></div> : null}
      </div>

      <div className="sidebar-footer">
        <button className="tutorial-entry" onClick={onTutorial}><span className="tutorial-entry-icon"><BookOpen size={15} /></span><span><strong>教程练习</strong><small>EGFR · 9 / 9 已开放</small></span><ChevronRight size={15} /></button>
        {settingsOpen ? <div className="sidebar-settings" role="dialog" aria-label="工作台设置"><div className="sidebar-settings-head"><strong>工作台设置</strong><button className="icon-button" onClick={onSettings} aria-label="关闭设置">×</button></div><p>控制当前会话的检索偏好，不会改变已保存的证据。</p><button className={`sidebar-setting-toggle ${officialOnly ? "sidebar-setting-toggle-active" : ""}`} onClick={onToggleOfficial} aria-pressed={officialOnly}><span><strong>仅使用官方来源</strong><small>UniProt · Open Targets · ChEMBL · ClinicalTrials.gov · 企业公告</small></span><span className="toggle-indicator">{officialOnly ? "开" : "关"}</span></button><div className="sidebar-shortcut"><kbd>Ctrl F</kbd><span>快速聚焦会话搜索</span></div></div> : null}
        <div className="user-row"><div className="avatar">S</div><span><strong>研究工作台</strong><small>实时来源已连接</small></span><button className="icon-button" onClick={onSettings} aria-label={settingsOpen ? "关闭设置" : "打开设置"} aria-expanded={settingsOpen}><Settings2 size={16} /></button></div>
      </div>
    </aside>
  );
}

function SessionGroup({ label, icon, sessions, activeId, onSelect, onRename, onTogglePin, onDelete, onExport }: { label: string; icon: React.ReactNode; sessions: ResearchSession[]; activeId: string | null; onSelect: (id: string) => void; onRename: (id: string, title: string) => void; onTogglePin: (id: string) => void; onDelete: (id: string) => void; onExport: () => void }) {
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  return (
    <section className="session-group">
      <div className="session-group-label">{icon}<span>{label}</span></div>
      <div className="session-list">
        {sessions.map((session) => (
          <div key={session.id} className={`session-item ${activeId === session.id ? "session-item-active" : ""}`}>
            <button className="session-select" onClick={() => { setOpenMenuId(null); onSelect(session.id); }}>
              <span className="session-item-main"><span className={`session-status-dot session-status-${session.status.toLowerCase()}`} /><span className="session-title">{session.title}</span></span>
              <span className="session-item-meta"><span>{session.subtitle}</span><span>{session.updatedAt}</span></span>
              {session.status === "UPDATED" ? <StatusPill tone="amber" dot>需更新</StatusPill> : null}
            </button>
            <button className="session-more-button" onClick={(event) => { event.stopPropagation(); setOpenMenuId((current) => current === session.id ? null : session.id); }} aria-label={`${session.title} 更多操作`} aria-expanded={openMenuId === session.id}><MoreHorizontal size={16} /></button>
            {openMenuId === session.id ? <div className="session-menu" role="menu" aria-label={`${session.title} 操作`}>
              <button role="menuitem" onClick={() => { setOpenMenuId(null); onRename(session.id, session.title); }}><Pencil size={14} />重命名</button>
              <button role="menuitem" onClick={() => { setOpenMenuId(null); onTogglePin(session.id); }}><Pin size={14} />{session.pinned ? "取消固定" : "固定记录"}</button>
              <button role="menuitem" onClick={() => { setOpenMenuId(null); onExport(); }}><Download size={14} />导出记录</button>
              <button role="menuitem" className="session-menu-danger" onClick={() => { setOpenMenuId(null); onDelete(session.id); }}><Trash2 size={14} />删除记录</button>
            </div> : null}
          </div>
        ))}
      </div>
    </section>
  );
}
