"use client";

import { ArrowRight, BookOpen, CheckCircle2, ChevronRight, ExternalLink, LockKeyhole, RefreshCw, ShieldCheck, Sparkles } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { getPublicLibraryEntry, listPublicLibrary, type PublicLibraryEntry, type PublicLibrarySummary } from "@/lib/api/public-library";

const sectionIcons = ["01", "02", "03", "04", "05", "06"];

export default function PublicLibraryPage() {
  const [entries, setEntries] = useState<PublicLibrarySummary[]>([]);
  const [selectedSlug, setSelectedSlug] = useState("");
  const [selectedEntry, setSelectedEntry] = useState<PublicLibraryEntry | null>(null);
  const [listLoading, setListLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");

  const loadEntries = () => {
    setListLoading(true);
    setError("");
    void listPublicLibrary()
      .then((nextEntries) => {
        setEntries(nextEntries);
        setSelectedSlug((current) => current || nextEntries[0]?.slug || "");
      })
      .catch(() => setError("公开证据库暂时无法连接，请稍后重试。"))
      .finally(() => setListLoading(false));
  };

  useEffect(() => {
    loadEntries();
  }, []);

  useEffect(() => {
    if (!selectedSlug) {
      setSelectedEntry(null);
      return;
    }
    let active = true;
    setDetailLoading(true);
    getPublicLibraryEntry(selectedSlug)
      .then((entry) => {
        if (active) setSelectedEntry(entry);
      })
      .catch(() => {
        if (active) setError("该公开快照暂时无法读取，请重试。" );
      })
      .finally(() => {
        if (active) setDetailLoading(false);
      });
    return () => {
      active = false;
    };
  }, [selectedSlug]);

  return (
    <main className="public-library-shell">
      <header className="public-library-header">
        <Link href="/public-library" className="public-library-brand" aria-label="TargetLens 公开证据库首页">
          <span className="public-library-brand-icon"><Sparkles size={20} /></span>
          <span><strong>TargetLens</strong><small>靶点研究助手</small></span>
        </Link>
        <div className="public-library-header-actions">
          <span className="public-access-pill"><span className="live-dot" />公开只读</span>
          <Link href="/login?next=%2Fworkspace" className="public-login-link">进入研究工作台 <ArrowRight size={16} /></Link>
        </div>
      </header>

      <section className="public-library-intro" aria-labelledby="public-library-title">
        <div className="public-library-eyebrow"><BookOpen size={15} /> PUBLIC EVIDENCE LIBRARY</div>
        <div className="public-library-intro-grid">
          <div>
            <h1 id="public-library-title">先看公开证据，再开始私有研究</h1>
            <p>这里展示经过来源标注的靶点教学快照。它们只读、无账号数据，不会显示任何人的提问、会话或内部知识图谱。</p>
          </div>
          <div className="public-boundary-note">
            <ShieldCheck size={18} />
            <div><strong>访问边界清晰</strong><span>未登录只能读取本页公开内容；登录后工作台按账号隔离。</span></div>
          </div>
        </div>
      </section>

      {listLoading ? (
        <div className="public-library-state" aria-busy="true"><RefreshCw size={18} className="public-spin" />正在读取公开快照…</div>
      ) : error && entries.length === 0 ? (
        <div className="public-library-state public-library-state-error" role="alert"><p>{error}</p><button type="button" className="public-retry-button" onClick={loadEntries}><RefreshCw size={15} />重新连接</button></div>
      ) : (
        <section className="public-library-content" aria-label="公开靶点快照">
          <aside className="public-library-target-list" aria-label="选择靶点">
            <div className="public-library-list-heading"><span>公开靶点</span><small>{entries.length} 个快照</small></div>
            {entries.map((entry) => (
              <button
                type="button"
                key={entry.slug}
                className={`public-target-option ${selectedSlug === entry.slug ? "public-target-option-active" : ""}`}
                onClick={() => setSelectedSlug(entry.slug)}
                aria-pressed={selectedSlug === entry.slug}
              >
                <span className="public-target-symbol">{entry.target.symbol.slice(0, 2)}</span>
                <span className="public-target-option-copy"><strong>{entry.target.symbol}</strong><small>{entry.headline}</small></span>
                <ChevronRight size={16} />
              </button>
            ))}
            {!entries.length ? <p className="public-empty-copy">暂时没有已发布的公开快照。</p> : null}
          </aside>

          <div className="public-library-detail" aria-live="polite">
            {detailLoading ? <div className="public-library-state public-detail-state" aria-busy="true"><RefreshCw size={18} className="public-spin" />正在读取靶点快照…</div> : null}
            {!detailLoading && selectedEntry ? (
              <article className="public-entry-card">
                <div className="public-entry-head">
                  <div className="public-entry-symbol">{selectedEntry.target.symbol.slice(0, 2)}</div>
                  <div className="public-entry-title"><div className="public-entry-kicker"><span className="public-access-pill"><span className="live-dot" />PUBLIC</span><span>公开快照 · {selectedEntry.updated_at}</span></div><h2>{selectedEntry.target.symbol}</h2><p>{selectedEntry.target.name}</p><div className="public-aliases">{selectedEntry.target.aliases.map((alias) => <span key={alias}>{alias}</span>)}</div></div>
                </div>
                <div className="public-entry-summary"><Sparkles size={18} /><div><strong>{selectedEntry.headline}</strong><p>{selectedEntry.summary}</p></div></div>
                <div className="public-section-grid">
                  {selectedEntry.sections.map((section, index) => (
                    <section className="public-evidence-section" key={section.key} aria-labelledby={`public-section-${section.key}`}>
                      <div className="public-section-heading"><span>{sectionIcons[index] ?? String(index + 1).padStart(2, "0")}</span><div><h3 id={`public-section-${section.key}`}>{section.title}</h3><p>{section.summary}</p></div></div>
                      <ul>{section.points.map((point) => <li key={point}><CheckCircle2 size={15} />{point}</li>)}</ul>
                    </section>
                  ))}
                </div>
                <div className="public-sources-panel">
                  <div className="public-sources-heading"><div><span className="eyebrow">SOURCE ATTRIBUTION</span><h3>支持来源</h3></div><span>{selectedEntry.sources.length} 个公开链接</span></div>
                  <div className="public-source-list">{selectedEntry.sources.map((source) => <a key={source.id} href={source.url} target="_blank" rel="noreferrer" className="public-source-link"><span><strong>{source.title}</strong><small>{source.organization} · {source.license}</small></span><ExternalLink size={15} /></a>)}</div>
                  <p className="public-disclaimer"><LockKeyhole size={14} />{selectedEntry.disclaimer}</p>
                </div>
              </article>
            ) : null}
          </div>
        </section>
      )}

      <footer className="public-library-footer"><span>公开内容与私有工作区分离</span><Link href="/login?next=%2Fworkspace">登录后创建自己的研究会话 <ArrowRight size={14} /></Link></footer>
    </main>
  );
}
