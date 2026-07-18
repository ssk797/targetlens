# TargetLens / 靶点梳理助手

面向药物研发场景的证据驱动型肿瘤靶点研读与立项辅助工作台。当前保留 Mock 优先演示路径，同时提供可选的 DeepSeek 问答和权威来源预览连接器；没有外部网络或 API Key 时仍可完整演示产品流程。

## 当前实现

- Next.js + TypeScript 前端工作台
- ROR1 / 三阴性乳腺癌 / ADC 的完整 Mock 会话
- 证据等级 E1–E5、来源等级 T0–T4、风险等级 R1–R4
- 证据抽屉、知识关系图谱降级表格、风险红线和可追溯元数据
- 三轮 Mock 追问与结构化 Decision Memo
- EGFR 教程首页与“靶点身份”“证据分级”两个可交互关卡
- FastAPI API 骨架，支持健康检查、会话、靶点卡、SSE 研究进度和后端评分接口
- 登录页与本地演示模式入口（正式部署可替换为企业 SSO）
- DeepSeek Provider（OpenAI-compatible Chat Completions）、AI 状态检查与安全降级
- PubMed / Europe PMC 备用文献入口、ClinicalTrials.gov、UniProt、ChEMBL、Open Targets 连接器
- `/api/v1/research/preview` 统一证据和知识关系预览，连接器逐个返回 READY / EMPTY / DEGRADED 状态
- `uv` 管理的后端依赖、结构化日志、SQLAlchemy ORM 与 Alembic 初始迁移
- PostgreSQL、Redis、MinIO、API、Celery worker 的 `compose.yaml` 本地编排

## 启动前端

```bash
pnpm install
pnpm dev
```

浏览器打开 `http://localhost:3000`。

登录页：`http://localhost:3000/login`。点击“进入本地演示模式”即可进入工作台；演示身份只保存在当前浏览器。

## 启动后端

使用 `uv` 安装并锁定后端依赖：

```bash
cd apps/api
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

健康检查：`http://localhost:8000/health`。

若要启用 DeepSeek，请复制 `apps/api/.env.example` 为 `apps/api/.env`，只在本机填写密钥：

```dotenv
AI_ENABLED=true
DEEPSEEK_API_KEY=你的本地密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL_FAST=deepseek-v4-flash
DEEPSEEK_MODEL_REASONING=deepseek-v4-pro
```

容器启动时会自动检查数据库连接；没有本地 `.env` 也可以启动 Compose（此时 AI 默认为关闭）。不要把真实密钥提交到 Git。

## 启动本地基础设施

Docker Desktop 启动后，在仓库根目录运行：

```bash
docker compose up --build
```

这会启动 PostgreSQL、Redis、MinIO、FastAPI 和 Celery worker，并由 API 容器执行
`alembic upgrade head`。Compose 中的账号和密码只用于本机开发，部署前必须通过环境变量替换。

后端评分接口：`GET /api/v1/sessions/{session_id}/scores`；评分规则在服务端计算，红线会单独限制建议等级并保留人工复核标记。

研究来源预览：`POST /api/v1/research/preview`，请求体示例：`{"target":"ROR1","disease":"triple-negative breast cancer","modality":"ADC"}`。响应会包含来源证据、截至时间和一跳知识关系；单个外部来源失败不会阻断其他来源。

## 检查命令

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
cd apps/api && uv run pytest -q
cd apps/api && uv run ruff check app tests
cd apps/api && uv run mypy app --ignore-missing-imports
```

## 演示路径

1. 在工作台点击“新建靶点研读”，输入 `ROR1 在三阴性乳腺癌中是否适合开发 ADC？`。
2. 展开靶点卡中的证据矩阵、风险和图谱区块，点击任意来源打开证据抽屉。
3. 使用快捷追问完成三轮问答，再点击“生成差异化建议”。
4. 从左侧进入“教程练习”，打开 EGFR 课程，完成关卡 1 和关卡 4。

## 数据说明

工作台中的 ROR1 结构化卡和评分仍带 Mock 标记，不能视为实时研发结论；连接器预览和 DeepSeek 问答会显式返回来源/Provider 状态。正式部署前仍需补齐来源快照落库、权限、审计日志、限速和企业 SSO。DeepSeek 的调用方式采用官方 OpenAI-compatible Chat Completions 接口，具体地址和模型以环境变量为准。
