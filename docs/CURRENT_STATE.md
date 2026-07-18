# 当前仓库状态

## 已有技术栈

- Next.js 15 App Router、React 19、TypeScript、Lucide Icons、Vitest。
- FastAPI 0.139、Pydantic 2、Uvicorn；支持 Mock 模式和数据库基础设施配置。
- SQLAlchemy 2、asyncpg、Alembic、Redis、Celery、structlog；`uv.lock` 已生成。
- 已初始化 Git，并创建 GitHub 私有仓库 `ssk797/targetlens`。
- Node.js 24、pnpm 11、Python 3.11、uv 0.11.29、Docker Desktop 4.82.0 / CLI 29.6.1 可用；Compose 已通过在线健康检查。

## 已有可复用模块

- 产品需求、视觉规范、Mock 数据约束、API 草案和验收清单均在执行指南中。
- `apps/web/lib/types/domain.ts`：证据、来源、风险、评分、教程领域类型。
- `apps/web/lib/mocks/data.ts`：ROR1 靶点卡、来源、回答、建议、评分和 EGFR 课程数据。
- `apps/api/app/main.py`：健康检查、会话、研究任务、SSE、Mock 问答和评分接口。
- `apps/api/app/db/models/core.py`：17 张核心表的 ORM 定义；`apps/api/alembic/versions/0001_initial_targetlens.py`：初始迁移。
- `apps/api/app/services/scoring/`：后端三轴评分、置信度因子、风险惩罚和红线推荐上限。

## 需要保留的代码

- 保留执行指南原文，作为产品边界和交付验收依据。

## 需要新增的代码

- 后续接入真实数据源、连接器快照、LLM Provider 和报告版本化落库。
- Compose 在线迁移验证与完整 E2E 测试矩阵。

## 发现的风险

- 第一轮仍需在没有真实数据连接器的环境下可演示；Compose 作为持久化开发路径。
- E1–E5、T0–T4 和 R1–R4 的正式判定规则还要结合首批权威来源校准。
- 当前 Mock 数据只能用于展示结构，不得被误认为实时研发结论。

## 实施顺序

1. 已完成前端设计系统和工作台 Mock 演示。
2. 已完成教程中心两个互动关卡。
3. 已完成 FastAPI Mock API 与 SSE。
4. 已完成后端工程化底座、Alembic 初始迁移、Compose 编排和正式评分规则第一版。
5. 下一阶段进入权威数据连接器、证据快照、API 契约扩展与真实会话持久化。
