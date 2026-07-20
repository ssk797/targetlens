# TargetLens / 靶点梳理助手

面向药物研发场景的证据驱动型肿瘤靶点研读与立项辅助工作台。当前保留 Mock 优先演示路径，同时提供可选的 DeepSeek 问答和权威来源预览连接器；没有外部网络或 API Key 时仍可完整演示产品流程。

> 本仓库用于公开展示产品工程成果。仓库不包含真实 API 密钥、用户研究记录或内部知识图谱数据；私人研究内容只保存在部署后的受认证工作区中。

## 当前实现

- Next.js + TypeScript 前端工作台
- 无需登录的 `/public-library` 公开成果页，提供 ROR1、JAK2、KRAS、EGFR 的可追溯示范快照
- 数据库模式下基于账号隔离的研究会话、消息和证据接口
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

公开成果页：`http://localhost:3000/public-library`。未登录访问工作台时会跳转至登录页。

登录页：`http://localhost:3000/login`。点击“进入本地演示模式”会由后端签发本地演示会话；普通账户只能读取自己的研究记录以及明确标记的演示记录。

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
`alembic upgrade head`。Compose 的宿主机端口仅绑定到 `127.0.0.1`；示例口令只用于本机开发，部署时必须通过环境变量或托管平台的 Secret Store 替换。

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

公开成果库是教学与产品展示快照，不是实时研发结论。工作台会显式展示来源状态、数据截至时间和降级连接器；DeepSeek 调用使用本地或部署环境变量，密钥不会进入浏览器代码或 Git 仓库。正式生产环境仍应配置独立数据库凭据、HTTPS、限速、备份和企业身份体系。

## 公开范围与安全

- 公开：源代码、产品界面、四个策展式靶点示范快照及其原始来源链接。
- 私有：用户账号、问题、追问、研究会话、证据缓存、内部关系索引和第三方 API 密钥。
- 本地 `.env`、Word 文档和项目图片默认被排除或保持未跟踪；提交前请运行密钥扫描。
- 安全问题请参照 [SECURITY.md](SECURITY.md)，不要在公开 Issue 中粘贴密钥或私人研究数据。

## 使用与版权

本仓库为成果展示用途，未授予开源许可。除 GitHub 平台正常浏览和评审所必需的权利外，未经许可不得复制、分发或用于商业用途。
