# TargetLens API

默认仍可运行 Mock API 和 SSE 研究进度；配置 `AI_ENABLED=true` 后可启用 DeepSeek 问答，数据库模式下 `/health` 会检查 PostgreSQL，研究预览接口会并行访问公开来源连接器。

```bash
python -m pip install -e .[dev]
python -m uvicorn app.main:app --reload
python -m pytest tests -q
```

主要接口：

- `GET /health`：API、模式和数据库状态。
- `GET /api/v1/ai/status`：Provider 配置状态（不返回密钥）。
- `POST /api/v1/research/preview`：归一化文献、结构化数据库和知识关系预览。
- `POST /api/v1/sessions/{session_id}/messages`：DeepSeek 或 Mock 降级问答。
