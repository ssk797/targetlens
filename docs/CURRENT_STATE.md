# 当前仓库状态

## 已有技术栈

- Next.js 15 App Router、React 19、TypeScript、Lucide Icons、Vitest。
- FastAPI 0.139、Pydantic 2、Uvicorn；第一轮为内存 Mock API。
- 已初始化 Git，并创建 GitHub 私有仓库 `ssk797/targetlens`。
- Node.js 24、pnpm 11、Python 3.11 可用；当前环境未发现 `uv` 与 Docker CLI。

## 已有可复用模块

- 产品需求、视觉规范、Mock 数据约束、API 草案和验收清单均在执行指南中。
- `apps/web/lib/types/domain.ts`：证据、来源、风险、评分、教程领域类型。
- `apps/web/lib/mocks/data.ts`：ROR1 靶点卡、来源、回答、建议、评分和 EGFR 课程数据。
- `apps/api/app/main.py`：健康检查、会话、研究任务、SSE 和 Mock 问答接口。

## 需要保留的代码

- 保留执行指南原文，作为产品边界和交付验收依据。

## 需要新增的代码

- 后续接入真实数据源、数据库、连接器快照、LLM Provider 和正式评分引擎。
- 报告导出、Alembic 迁移、Docker Compose 与完整 E2E 测试矩阵。

## 发现的风险

- 第一轮需要在没有 `uv`、Docker 和真实数据连接器的本地环境下可演示。
- E1–E5、T0–T4 和 R1–R4 的正式判定规则仍需在后端阶段固化。
- 当前 Mock 数据只能用于展示结构，不得被误认为实时研发结论。

## 实施顺序

1. 已完成前端设计系统和工作台 Mock 演示。
2. 已完成教程中心两个互动关卡。
3. 已完成 FastAPI Mock API 与 SSE。
4. 下一阶段进入前后端契约、数据连接器、LLM Provider 和正式评分引擎。
