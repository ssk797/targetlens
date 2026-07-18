"use client";

import { ArrowRight, DatabaseZap, LockKeyhole, ShieldCheck, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const enterWorkspace = (event?: FormEvent<HTMLFormElement>) => {
    event?.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError("请输入邮箱和密码，或直接使用演示账号进入。");
      return;
    }
    window.localStorage.setItem("targetlens-session", JSON.stringify({ email: email.trim(), signedInAt: new Date().toISOString() }));
    router.push("/workspace");
  };

  const enterDemo = () => {
    setEmail("researcher@targetlens.local");
    setPassword("demo");
    window.localStorage.setItem("targetlens-session", JSON.stringify({ email: "researcher@targetlens.local", demo: true, signedInAt: new Date().toISOString() }));
    router.push("/workspace");
  };

  return (
    <main className="login-shell">
      <section className="login-brief" aria-label="TargetLens 产品介绍">
        <div className="login-brand"><div className="brand-icon"><Sparkles size={22} /></div><span>TargetLens</span></div>
        <div className="login-brief-copy">
          <span className="eyebrow">EVIDENCE-LED TARGET RESEARCH</span>
          <h1>把一个模糊的靶点问题，变成一条可复核的证据链。</h1>
          <p>连接结构化数据库、文献、临床试验与知识关系，帮助团队在进入实验和立项之前先看清边界。</p>
        </div>
        <div className="login-signal-list">
          <div><DatabaseZap size={20} /><span><strong>来源可追溯</strong><small>每个结论都能回到证据快照</small></span></div>
          <div><ShieldCheck size={20} /><span><strong>风险单独审查</strong><small>红线不会被总分掩盖</small></span></div>
          <div><LockKeyhole size={20} /><span><strong>研究空间隔离</strong><small>会话和连接器按项目管理</small></span></div>
        </div>
      </section>

      <section className="login-card" aria-label="登录 TargetLens">
        <div className="login-card-head"><span className="eyebrow">RESEARCH WORKSPACE</span><h2>登录工作台</h2><p>进入你的靶点研读、证据抽屉和立项判断空间。</p></div>
        <form onSubmit={enterWorkspace} className="login-form">
          <label htmlFor="login-email">工作邮箱</label>
          <input id="login-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@company.com" autoComplete="email" />
          <label htmlFor="login-password">密码</label>
          <input id="login-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="输入密码" autoComplete="current-password" />
          {error ? <p className="login-error" role="alert">{error}</p> : null}
          <button className="login-submit" type="submit">登录并进入工作台 <ArrowRight size={18} /></button>
        </form>
        <div className="login-divider"><span>或</span></div>
        <button className="login-demo" type="button" onClick={enterDemo}>进入本地演示模式</button>
        <p className="login-note">演示账号只保存在当前浏览器；正式部署时接入企业 SSO 或统一身份服务。</p>
      </section>
    </main>
  );
}
