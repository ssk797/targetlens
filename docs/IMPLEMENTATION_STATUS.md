# 实施状态

## 当前阶段

阶段 1、阶段 2 已完成；阶段 3 的后端工程化底座已完成，正在进入真实数据连接器阶段。

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

## 运行过的检查

- `pnpm lint`：通过。
- `pnpm typecheck`：通过。
- `pnpm test`：通过，2 个前端测试。
- `pnpm build`：通过，工作台和教程路由均静态构建。
- `cd apps/api && uv run pytest -q`：通过，7 个后端测试；有 1 条 Starlette/httpx 弃用提示。
- `cd apps/api && uv run ruff check app tests`：通过。
- `cd apps/api && uv run mypy app --ignore-missing-imports`：通过。
- `cd apps/api && uv run alembic upgrade head --sql`：离线迁移 SQL 生成通过。
- `docker compose up --build -d`：通过，PostgreSQL / Redis / MinIO / API / worker 全部运行。
- `docker compose exec -T api uv run alembic check`：通过，在线数据库无待迁移操作。
- 前端 HTTP：`/workspace` 返回 200；本地默认后端 `/health` 为 Mock 模式，Compose 后端 `/health` 为 database 模式。
- SSE：研究任务返回 202，并包含进度和 `research.completed` 事件。
- Playwright：证据抽屉、连续追问、教程关卡 1、关卡 4 和 1366×768 截图通过。

## 未完成

- 外部连接器、DeepSeek Provider 和报告版本化落库。
- 完整 E2E 浏览器测试矩阵。

## 已知问题

- `uv` 已安装并用于项目虚拟环境；Docker Desktop 4.82.0 已安装，Compose 使用 WSL 2 引擎运行。
- 当前研究结论、项目名称和临床状态均是带 Mock 标记的演示数据。

## 下一步

- 为会话、证据、风险、教程和报告补齐 API 契约测试。
- 接入首批权威来源连接器，保留来源快照、截至时间和降级状态。
