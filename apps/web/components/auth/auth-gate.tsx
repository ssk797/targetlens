"use client";

import { LoaderCircle } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { httpClient } from "@/lib/api/http-client";

/** Keep workspace routes private while preserving the intended destination. */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void httpClient.getCurrentUser()
      .then(() => { if (!cancelled) setReady(true); })
      .catch(() => {
        if (!cancelled) router.replace(`/login?next=${encodeURIComponent(pathname || "/workspace")}`);
      });
    return () => { cancelled = true; };
  }, [pathname, router]);

  if (!ready) {
    return <main className="auth-loading" aria-live="polite"><LoaderCircle className="spin" size={22} /><span>正在验证工作台会话…</span></main>;
  }
  return <>{children}</>;
}
