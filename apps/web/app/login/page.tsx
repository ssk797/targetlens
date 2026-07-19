"use client";

import { ArrowRight, DatabaseZap, Eye, EyeOff, LockKeyhole, ShieldCheck, Sparkles } from "lucide-react";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { httpClient } from "@/lib/api/http-client";

type LoginMode = "login" | "register";

function apiError(error: unknown, fallback: string) {
  const message = error instanceof Error ? error.message : "";
  if (message.includes("409")) return "这个邮箱已经注册，请直接登录。";
  if (message.includes("401")) return "邮箱或密码不正确，请重试。";
  if (message.includes("422")) return "请检查邮箱格式和密码长度（至少 8 位）。";
  return fallback;
}

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<LoginMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [remember, setRemember] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const goNext = () => {
    const next = typeof window !== "undefined" ? new URLSearchParams(window.location.search).get("next") : null;
    router.replace(next?.startsWith("/") ? next : "/workspace");
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    if (mode === "register" && password.length < 8) {
      setError("密码至少需要 8 位。");
      return;
    }
    setBusy(true);
    try {
      const user = mode === "register"
        ? await httpClient.register({ email: email.trim(), password, displayName: displayName.trim() || "研究员" })
        : await httpClient.login({ email: email.trim(), password, remember });
      window.localStorage.setItem("targetlens-session", JSON.stringify({ email: user.email, displayName: user.displayName, signedInAt: new Date().toISOString() }));
      goNext();
    } catch (requestError) {
      setError(apiError(requestError, mode === "register" ? "注册没有完成，请稍后重试。" : "登录没有完成，请检查 API 服务。"));
    } finally {
      setBusy(false);
    }
  };

  const enterDemo = async () => {
    setError("");
    setBusy(true);
    try {
      const user = await httpClient.demoLogin();
      window.localStorage.setItem("targetlens-session", JSON.stringify({ email: user.email, displayName: user.displayName, demo: true, signedInAt: new Date().toISOString() }));
      goNext();
    } catch (requestError) {
      setError(apiError(requestError, "演示登录没有完成，请确认 API 和数据库已启动。"));
    } finally {
      setBusy(false);
    }
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
          <div><LockKeyhole size={20} /><span><strong>研究空间隔离</strong><small>会话由后端账户和会话 Cookie 保护</small></span></div>
        </div>
      </section>

      <section className="login-card" aria-label="登录 TargetLens">
        <div className="login-card-head"><span className="eyebrow">RESEARCH WORKSPACE</span><h2>{mode === "login" ? "登录工作台" : "创建研究账户"}</h2><p>{mode === "login" ? "进入你的靶点研读、证据抽屉和立项判断空间。" : "创建一个本地研究账户，保存你的研读记录和追问。"}</p></div>
        <div className="login-mode-switch" role="tablist" aria-label="账户操作"><button type="button" className={mode === "login" ? "login-mode-active" : ""} onClick={() => { setMode("login"); setError(""); }} role="tab" aria-selected={mode === "login"}>登录</button><button type="button" className={mode === "register" ? "login-mode-active" : ""} onClick={() => { setMode("register"); setError(""); }} role="tab" aria-selected={mode === "register"}>注册</button></div>
        <form onSubmit={handleSubmit} className="login-form">
          {mode === "register" ? <><label htmlFor="login-name">显示名称</label><input id="login-name" type="text" value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="例如：张研究员" autoComplete="name" /></> : null}
          <label htmlFor="login-email">工作邮箱</label>
          <input id="login-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="name@company.com" autoComplete="email" required />
          <label htmlFor="login-password">密码</label>
          <div className="password-field"><input id="login-password" type={showPassword ? "text" : "password"} value={password} onChange={(event) => setPassword(event.target.value)} placeholder={mode === "register" ? "至少 8 位" : "输入密码"} autoComplete={mode === "register" ? "new-password" : "current-password"} required /><button type="button" className="password-toggle" onClick={() => setShowPassword((value) => !value)} aria-label={showPassword ? "隐藏密码" : "显示密码"}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>
          {mode === "login" ? <label className="remember-row"><input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />保持登录 7 天</label> : null}
          {error ? <p className="login-error" role="alert">{error}</p> : null}
          <button className="login-submit" type="submit" disabled={busy}>{busy ? "处理中…" : mode === "login" ? "登录并进入工作台" : "创建账户并进入"} {!busy ? <ArrowRight size={18} /> : null}</button>
        </form>
        <div className="login-divider"><span>或</span></div>
        <button className="login-demo" type="button" onClick={() => void enterDemo()} disabled={busy}>进入本地演示模式</button>
        <p className="login-note">演示模式会使用后端创建的本地演示账户；正式环境可在此基础上接入企业 SSO。</p>
      </section>
    </main>
  );
}
