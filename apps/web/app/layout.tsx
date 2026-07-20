import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "靶点梳理助手 · TargetLens",
  description: "面向药物研发的证据驱动型靶点研读工作台",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
