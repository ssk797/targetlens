# TargetLens API

FastAPI 服务负责本地身份会话、研究任务、公开来源连接、证据整合、靶点卡、连续问答和差异化建议。默认配置使用 Mock 模式；外部来源或 AI 不可用时会返回明确状态，不伪造来源记录。

## 本地启动

```powershell
Copy-Item .env.example .env
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

健康检查：`GET http://localhost:8000/health`。

## 主要接口

- `POST /api/v1/auth/register`、`POST /api/v1/auth/login`：本地 V1 身份入口。
- `GET /api/v1/ai/status`：Provider 状态，不返回 API Key。
- `POST /api/v1/research/preview`：多来源研究预览和连接器状态。
- `POST /api/v1/sessions/{session_id}/research`：启动会话内研究任务。
- `GET /api/v1/sessions/{session_id}/events`：SSE 研究进度。
- `GET /api/v1/sessions/{session_id}/target-card`：当前结构化靶点卡。
- `POST /api/v1/sessions/{session_id}/messages`：带会话上下文的问答。
- `POST /api/v1/sessions/{session_id}/decision-memos`：按需生成差异化建议。

## 验证

```powershell
uv run pytest -q
uv run ruff check app tests
uv run mypy app --ignore-missing-imports
uv run alembic upgrade head --sql
```

真实密钥只允许写入本地 `.env` 或部署平台的 Secret Store。
