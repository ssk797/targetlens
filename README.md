# TargetLens / 靶点梳理助手

面向药物研发场景的证据驱动型肿瘤靶点研读与立项辅助工作台。第一轮交付采用 Mock 优先策略：即使没有外部网络或 API Key，也可以完整演示靶点确认、研究进度、结构化靶点卡、证据抽屉、连续追问、差异化建议、三轴评分和 EGFR 教程关卡。

## 当前实现

- Next.js + TypeScript 前端工作台
- ROR1 / 三阴性乳腺癌 / ADC 的完整 Mock 会话
- 证据等级 E1–E5、来源等级 T0–T4、风险等级 R1–R4
- 证据抽屉、知识关系图谱降级表格、风险红线和可追溯元数据
- 三轮 Mock 追问与结构化 Decision Memo
- EGFR 教程首页与“靶点身份”“证据分级”两个可交互关卡
- FastAPI API 骨架，支持健康检查、会话、靶点卡、SSE 研究进度和后端评分接口
- `uv` 管理的后端依赖、结构化日志、SQLAlchemy ORM 与 Alembic 初始迁移
- PostgreSQL、Redis、MinIO、API、Celery worker 的 `compose.yaml` 本地编排

## 启动前端

```bash
pnpm install
pnpm dev
```

浏览器打开 `http://localhost:3000`。

## 启动后端

使用 `uv` 安装并锁定后端依赖：

```bash
cd apps/api
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

健康检查：`http://localhost:8000/health`。

## 启动本地基础设施

Docker Desktop 启动后，在仓库根目录运行：

```bash
docker compose up --build
```

这会启动 PostgreSQL、Redis、MinIO、FastAPI 和 Celery worker，并由 API 容器执行
`alembic upgrade head`。Compose 中的账号和密码只用于本机开发，部署前必须通过环境变量替换。

后端评分接口：`GET /api/v1/sessions/{session_id}/scores`；评分规则在服务端计算，红线会单独限制建议等级并保留人工复核标记。

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

当前所有研究内容均是带 `isMock: true` 标记的演示数据，不用于真实研发判断。正式接入阶段需要实现来源快照、数据截至时间、证据校验、连接器降级、审计日志和后端评分规则。
