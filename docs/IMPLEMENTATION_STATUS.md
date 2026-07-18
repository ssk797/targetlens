# 实施状态

## 当前阶段

阶段 1、阶段 2 已完成；阶段 3 的 FastAPI Mock API 骨架已完成，准备进入真实数据与持久化阶段。

## 已完成

- Git 仓库与 GitHub 远程仓库初始化。
- Next.js 前端工程骨架与设计令牌。
- 靶点研读工作台、证据抽屉、连续追问、差异化建议、评分面板。
- EGFR 教程首页与两个可交互关卡。
- FastAPI Mock API 骨架。
- 1366×768 Playwright 浏览器烟雾验证与页面截图。

## 运行过的检查

- `pnpm lint`：通过。
- `pnpm typecheck`：通过。
- `pnpm test`：通过，2 个前端测试。
- `pnpm build`：通过，工作台和教程路由均静态构建。
- `python -m pytest apps/api/tests -q`：通过，4 个后端测试；有 1 条 Starlette/httpx 弃用提示。
- 前端 HTTP：`/workspace` 返回 200；后端 `/health` 返回 Mock 模式。
- SSE：研究任务返回 202，并包含进度和 `research.completed` 事件。
- Playwright：证据抽屉、连续追问、教程关卡 1、关卡 4 和 1366×768 截图通过。

## 未完成

- 真实数据库、外部连接器、DeepSeek Provider、正式评分规则和报告导出。
- Docker Compose、Alembic 迁移与完整 E2E 浏览器测试。

## 已知问题

- 本机暂未安装 `uv` 与 Docker CLI，因此尚未运行 `uv run` 和 Docker Compose 检查。
- 后端测试依赖当前环境的 Python 用户安装路径；团队环境应使用项目虚拟环境或 `uv`。
- 当前研究结论、项目名称和临床状态均是带 Mock 标记的演示数据。

## 下一步

- 安装并验证后端依赖。
- 加入 API 契约测试和 Playwright E2E。
- 逐步接入首批权威来源。
