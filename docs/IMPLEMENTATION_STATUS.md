# 实施状态

## 当前阶段

阶段 1、阶段 2 已完成；阶段 3 已完成首批真实连接器、可选 LLM Provider、数据库在线校验和登录入口，当前进入证据快照落库与真实会话持久化阶段。

## 已完成

- Git 仓库与 GitHub 远程仓库初始化。
- Next.js 前端工程骨架与设计令牌。
- 靶点研读工作台、证据抽屉、连续追问、差异化建议、评分面板。
- EGFR 教程首页与两个可交互关卡。
- FastAPI API 骨架与 CORS/环境配置。
- `uv.lock` 依赖锁定、结构化日志、SQLAlchemy ORM 及 17 张核心表。
- Alembic `0001_initial_targetlens` 初始迁移。
- PostgreSQL / Redis / MinIO / API / Celery worker 的 Compose 编排。
- 服务端确定性评分引擎、红线推荐上限与评分接口。
- 1366×768 Playwright 浏览器烟雾验证与页面截图。
- 首页上方重复输入框移除，统一字号/图标放大，新增 8 个研究方向快捷入口。
- 侧栏收起后提供独立的“展开侧栏”浮动按钮，并覆盖移动端打开入口。
- 登录页、本地演示模式和工作台路由跳转。
- DeepSeek Provider、AI 状态接口、API Key 脱敏和不可用时的明确降级。
- PubMed（Europe PMC 备用）、ClinicalTrials.gov、UniProt、ChEMBL、Open Targets 连接器及统一研究预览接口。
- Compose 数据库健康检查为 `connected`，在线 Alembic 检查无待迁移操作。

## 运行过的检查

- `pnpm lint`：通过。
- `pnpm typecheck`：通过。
- `pnpm test`：通过，2 个前端测试。
- `pnpm build`：通过，工作台和教程路由均静态构建。
- `cd apps/api && uv run pytest -q`：通过，9 个后端测试；有 1 条 Starlette/httpx 弃用提示。
- `cd apps/api && uv run ruff check app tests`：通过。
- `cd apps/api && uv run mypy app --ignore-missing-imports`：通过。
- `cd apps/api && uv run alembic upgrade head --sql`：离线迁移 SQL 生成通过。
- `docker compose up --build -d`：通过，PostgreSQL / Redis / MinIO / API / worker 全部运行。
- `docker compose exec -T api uv run alembic check`：通过，在线数据库无待迁移操作。
- 前端 HTTP：`/workspace`、`/login` 返回 200；本地默认后端 `/health` 为 Mock 模式，Compose 后端 `/health` 为 database 模式且数据库为 `connected`。
- Compose 实测 `/api/v1/ai/status` 已识别 DeepSeek 配置；最小化问答请求返回 `provider=deepseek`、`is_mock=false`。
- Compose 实测 `/api/v1/research/preview` 返回 PubMed、UniProt、Open Targets 证据和知识关系；临床试验来源在当前网络环境返回 `DEGRADED`，不会伪造结果。
- SSE：研究任务返回 202，并包含进度和 `research.completed` 事件。
- Playwright：证据抽屉、连续追问、教程关卡 1、关卡 4 和 1366×768 截图通过。

## 未完成

- 证据快照、连接器响应和报告版本化落库。
- 正式身份认证、组织/项目权限和完整 E2E 浏览器测试矩阵。

## 已知问题

- `uv` 已安装并用于项目虚拟环境；Docker Desktop 4.82.0 已安装，Compose 使用 WSL 2 引擎运行。
- 工作台结构化卡、评分和项目状态仍是带 Mock 标记的演示数据；研究预览必须以连接器状态和原始来源为准。
- `apps/api/.env` 为本机忽略文件，不能提交；用户曾在聊天中粘贴密钥，正式使用前应在服务商控制台轮换。

## 下一步

- 为会话、证据、风险、教程和报告补齐 API 契约测试。
- 将研究预览结果转为来源快照、证据版本和审计事件并落库。
- 补齐 ClinicalTrials.gov 的网络重试/代理策略、限速和缓存，接入企业 SSO 后再打开生产身份流。
