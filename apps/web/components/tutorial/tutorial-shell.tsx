"use client";

import { ArrowLeft, ArrowRight, Award, BookOpen, Check, ChevronRight, CircleHelp, RotateCcw, Sparkles, Target, Trophy } from "lucide-react";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { mockTutorial } from "@/lib/mocks/data";

const identityChoices = [
  { id: "egfr-gene", label: "EGFR gene", kind: "基因", correct: true, note: "标准基因实体：EGFR / ERBB1。" },
  { id: "egfr-drug", label: "Osimertinib", kind: "药物", correct: false, note: "这是 EGFR 抑制剂，不是靶点本身。" },
  { id: "egfr-protein", label: "EGFR protein", kind: "蛋白", correct: false, note: "蛋白是基因表达出的实体；此题要求标准基因实体。" },
  { id: "egfr-alias", label: "HER1 / ERBB1", kind: "别名", correct: false, note: "这是常见别名，需要映射到 EGFR 标准实体。" },
];

const evidenceCards = [
  { id: "e1", text: "经重复验证的临床试验结果与公开终点", answer: "E1", hint: "临床确证层级最高。" },
  { id: "e2", text: "动物模型中的剂量反应与机制一致性", answer: "E2", hint: "体内证据仍需关注模型外推。" },
  { id: "e3", text: "细胞系中观察到靶点抑制后的表型变化", answer: "E3", hint: "体外功能证据支持方向，但不能当临床确证。" },
  { id: "e4", text: "专家综述提出的研究假设，未展示原始数据", answer: "E4", hint: "综述可以帮助定位，但需要回到原始证据。" },
  { id: "e5", text: "待验证的机制推断或来源不完整的线索", answer: "E5", hint: "应显式标记未知，不要包装成事实。" },
];

const kindLabel = (kind: string) => kind === "IDENTITY" ? "靶点身份" : kind === "EVIDENCE" ? "证据分级" : kind === "READING" ? "研究阅读" : "立项判断";

export function TutorialShell() {
  const router = useRouter();
  const [activeLesson, setActiveLesson] = useState("lesson-1");
  const [identityChoice, setIdentityChoice] = useState<string | null>(null);
  const [evidenceAnswers, setEvidenceAnswers] = useState<Record<string, string>>({});
  const [submittedIdentity, setSubmittedIdentity] = useState(false);
  const [submittedEvidence, setSubmittedEvidence] = useState(false);
  const [completedLessons, setCompletedLessons] = useState<string[]>([]);

  const totalLessons = mockTutorial.lessons.length;
  const completedCount = useMemo(() => completedLessons.length, [completedLessons]);
  const activeLessonData = mockTutorial.lessons.find((lesson) => lesson.id === activeLesson) ?? mockTutorial.lessons[0];
  const evidenceCorrect = evidenceCards.filter((card) => evidenceAnswers[card.id] === card.answer).length;
  const markCompleted = (lessonId: string) => setCompletedLessons((current) => current.includes(lessonId) ? current : [...current, lessonId]);
  const clearCompleted = (lessonId: string) => setCompletedLessons((current) => current.filter((id) => id !== lessonId));

  return (
    <div className="tutorial-shell">
      <aside className="tutorial-sidebar">
        <div className="tutorial-brand"><button className="icon-button" onClick={() => router.push("/workspace")} aria-label="返回工作台"><ArrowLeft size={17} /></button><div className="brand-lockup"><div className="brand-icon"><Sparkles size={17} /></div><span>教程练习</span></div></div>
        <div className="course-identity"><div className="course-target-mark">EGFR</div><div><p className="eyebrow">TargetLens course</p><h1>{mockTutorial.title}</h1><span>{totalLessons} 个关卡 · {completedCount} / {totalLessons} 已完成</span></div></div>
        <div className="lesson-progress"><span><i style={{ width: `${Math.max(completedCount ? (completedCount / totalLessons) * 100 : 4, 4)}%` }} /></span><strong>{completedCount} / {totalLessons}</strong></div>
        <nav className="lesson-list" aria-label="课程关卡">
          {mockTutorial.lessons.map((lesson) => {
            const completed = completedLessons.includes(lesson.id);
            return <button key={lesson.id} className={`lesson-item ${activeLesson === lesson.id ? "lesson-item-active" : ""} lesson-item-unlocked`} onClick={() => setActiveLesson(lesson.id)}><span className="lesson-number">{completed ? <Check size={14} /> : String(lesson.number).padStart(2, "0")}</span><span><strong>{lesson.title}</strong><small>{lesson.duration} · 已开放</small></span>{activeLesson === lesson.id ? <ChevronRight size={15} /> : null}</button>;
          })}
        </nav>
        <div className="tutorial-sidebar-footer"><div className="coach-mini"><CircleHelp size={15} /><span><strong>AI 教练在线</strong><small>随时解释你的判断</small></span></div><button className="return-workspace" onClick={() => router.push("/workspace")}><Target size={15} />进入真实靶点研读</button></div>
      </aside>
      <main className="lesson-workspace">
        <header className="lesson-topbar"><div><span className="breadcrumb-link" onClick={() => router.push("/workspace")}>靶点研读</span><ChevronRight size={14} /><strong>EGFR 课程</strong></div><div className="lesson-top-actions"><span className="mock-mode-label"><span className="live-dot" />离线练习模式</span><button className="icon-button" aria-label="课程选项"><CircleHelp size={17} /></button></div></header>
        <div className="lesson-canvas">
          <div className="lesson-meta"><span className="lesson-chip">关卡 {String(activeLessonData.number).padStart(2, "0")}</span><span>{kindLabel(activeLessonData.kind)}</span><span>预计 {activeLessonData.duration}</span><span className="lesson-open-label">全部关卡已开放</span></div>
          {activeLesson === "lesson-1" ? <IdentityLesson choice={identityChoice} submitted={submittedIdentity} onChoice={setIdentityChoice} onSubmit={() => { setSubmittedIdentity(true); markCompleted("lesson-1"); }} onReset={() => { setIdentityChoice(null); setSubmittedIdentity(false); clearCompleted("lesson-1"); }} /> : activeLesson === "lesson-4" ? <EvidenceLesson answers={evidenceAnswers} submitted={submittedEvidence} score={evidenceCorrect} onChoose={(id, level) => setEvidenceAnswers((current) => ({ ...current, [id]: level }))} onSubmit={() => { setSubmittedEvidence(true); markCompleted("lesson-4"); }} onReset={() => { setEvidenceAnswers({}); setSubmittedEvidence(false); clearCompleted("lesson-4"); }} /> : <GuidedLesson lesson={activeLessonData} completed={completedLessons.includes(activeLessonData.id)} onComplete={() => markCompleted(activeLessonData.id)} onReset={() => clearCompleted(activeLessonData.id)} />}
          <div className="coach-drawer"><div className="coach-avatar"><Sparkles size={17} /></div><div><span className="eyebrow">AI 教练提示</span><p>{activeLessonData.kind === "IDENTITY" ? "先问自己：题目要求的是哪一种实体？基因、蛋白和药物名称在研究流程中的职责不同。" : activeLessonData.kind === "EVIDENCE" ? "证据等级描述的是可以支持到什么程度，不是对研究价值的永久判决。" : "把这一关的判断写成可核验的小问题，再回到真实靶点卡中验证。"}</p></div><button className="text-button">展开解释 <ArrowRight size={14} /></button></div>
        </div>
      </main>
    </div>
  );
}

function IdentityLesson({ choice, submitted, onChoice, onSubmit, onReset }: { choice: string | null; submitted: boolean; onChoice: (id: string) => void; onSubmit: () => void; onReset: () => void }) {
  const selected = identityChoices.find((item) => item.id === choice);
  return <section className="lesson-card"><div className="lesson-card-head"><div className="lesson-icon lesson-icon-blue"><Target size={19} /></div><div><p className="eyebrow">Lesson 01 · Entity resolution</p><h1>先确认你研究的对象</h1><p>同一个靶点有基因、蛋白、别名和药物等不同表达。先完成实体确认，后面的证据才不会串错。</p></div></div><div className="task-prompt"><span>任务</span><strong>从候选名称中选择 EGFR 的标准基因实体。</strong></div><div className="choice-grid">{identityChoices.map((item) => <button className={`choice-card ${choice === item.id ? "choice-card-selected" : ""} ${submitted ? (item.correct ? "choice-card-correct" : choice === item.id ? "choice-card-wrong" : "") : ""}`} key={item.id} onClick={() => !submitted && onChoice(item.id)}><span className="choice-kind">{item.kind}</span><strong>{item.label}</strong><span className="choice-radio">{choice === item.id ? <Check size={14} /> : null}</span></button>)}</div>{submitted && selected ? <div className={`lesson-feedback ${selected.correct ? "feedback-success" : "feedback-warning"}`}><div>{selected.correct ? <Check size={18} /> : <CircleHelp size={18} />}</div><div><strong>{selected.correct ? "判断正确" : "再看一层"}</strong><p>{selected.note}</p></div></div> : null}<div className="lesson-actions"><span className="lesson-hint">{submitted ? "已记录本关判断，可重新尝试" : "选择一个答案后提交"}</span>{submitted ? <button className="secondary-button" onClick={onReset}><RotateCcw size={15} />重新作答</button> : <button className="primary-button" disabled={!choice} onClick={onSubmit}>提交判断 <ArrowRight size={15} /></button>}</div></section>;
}

function EvidenceLesson({ answers, submitted, score, onChoose, onSubmit, onReset }: { answers: Record<string, string>; submitted: boolean; score: number; onChoose: (id: string, level: string) => void; onSubmit: () => void; onReset: () => void }) {
  return <section className="lesson-card"><div className="lesson-card-head"><div className="lesson-icon lesson-icon-amber"><Award size={19} /></div><div><p className="eyebrow">Lesson 04 · Evidence grading</p><h1>把证据放到它能支持的位置</h1><p>证据分级不是给研究贴永久标签，而是约束结论的表达强度。把下面五条材料分别放入 E1–E5。</p></div></div><div className="evidence-task-grid"><div className="evidence-stack"><span className="mini-label">待分类材料</span>{evidenceCards.map((card) => <div className={`evidence-task-card ${submitted ? (answers[card.id] === card.answer ? "task-correct" : "task-wrong") : ""}`} key={card.id}><div className="task-card-index">{card.id.replace("e", "0")}</div><p>{card.text}</p><div className="task-card-select">{["E1", "E2", "E3", "E4", "E5"].map((level) => <button key={level} className={answers[card.id] === level ? "level-selected" : ""} onClick={() => !submitted && onChoose(card.id, level)}>{level}</button>)}</div>{submitted ? <small>{answers[card.id] === card.answer ? <><Check size={12} />正确 · {card.hint}</> : <><CircleHelp size={12} />应为 {card.answer} · {card.hint}</>}</small> : null}</div>)}</div><div className="grading-guide"><span className="mini-label">分级参考</span>{["E1 · 临床确证", "E2 · 体内验证", "E3 · 体外功能", "E4 · 间接 / 综述", "E5 · 待验证"].map((item, index) => <div key={item} className="grading-row"><span className={`evidence-badge evidence-e${index + 1}`}>E{index + 1}</span><strong>{item.split(" · ")[1]}</strong><small>{index === 2 ? "不能当作临床确证" : index === 4 ? "显式标记未知" : ""}</small></div>)}</div></div>{submitted ? <div className="lesson-feedback feedback-success"><div><Trophy size={18} /></div><div><strong>完成本关：{score} / 5</strong><p>体外证据可以支持研究假设，但不能被写成临床有效性结论。</p></div></div> : null}<div className="lesson-actions"><span className="lesson-hint">{submitted ? "可以重置后再次练习" : `${Object.keys(answers).length} / 5 条已分类`}</span>{submitted ? <button className="secondary-button" onClick={onReset}><RotateCcw size={15} />重新练习</button> : <button className="primary-button" disabled={Object.keys(answers).length !== 5} onClick={onSubmit}>提交分级 <ArrowRight size={15} /></button>}</div></section>;
}

function GuidedLesson({ lesson, completed, onComplete, onReset }: { lesson: { id: string; number: number; title: string; kind: string; duration: string }; completed: boolean; onComplete: () => void; onReset: () => void }) {
  const isDecision = lesson.kind === "DECISION";
  const icon = lesson.kind === "READING" ? <BookOpen size={19} /> : isDecision ? <Target size={19} /> : <Award size={19} />;
  const prompt = lesson.kind === "IDENTITY" ? "把一个名称拆成标准实体、别名、蛋白和药物四类，并写出需要核验的映射。" : lesson.kind === "READING" ? "从当前靶点卡中挑出一条功能或机制陈述，标记它需要的原始来源。" : isDecision ? "把证据、风险和未知项各写成一句话，形成可回溯的下一步判断。" : "找出一条证据并判断它能支持到哪一层。";
  return <section className="lesson-card"><div className="lesson-card-head"><div className="lesson-icon lesson-icon-blue">{icon}</div><div><p className="eyebrow">Lesson {String(lesson.number).padStart(2, "0")} · {kindLabel(lesson.kind)}</p><h1>{lesson.title}</h1><p>这一关已经开放。你可以先完成方法练习，再回到真实靶点卡核验来源；教程不会把未完成关卡锁住。</p></div></div><div className="task-prompt"><span>练习任务</span><strong>{prompt}</strong></div><div className="guided-checklist"><div><Check size={15} /><span>明确研究对象和范围</span></div><div><Check size={15} /><span>记录证据来源与不确定性</span></div><div><Check size={15} /><span>把结论写成可验证的下一步</span></div></div>{completed ? <div className="lesson-feedback feedback-success"><div><Check size={18} /></div><div><strong>本关已完成</strong><p>完成状态只记录练习进度，不会替代真实靶点检索。</p></div></div> : null}<div className="lesson-actions"><span className="lesson-hint">{completed ? "可以重置后再次练习" : "全部关卡已开放，完成后会记录进度"}</span>{completed ? <button className="secondary-button" onClick={onReset}><RotateCcw size={15} />重置本关</button> : <button className="primary-button" onClick={onComplete}>标记本关完成 <ArrowRight size={15} /></button>}</div></section>;
}
