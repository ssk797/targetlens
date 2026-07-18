# TargetLens API

第一轮只提供 Mock API 和 SSE 研究进度，不依赖数据库、Redis 或外部模型。

```bash
python -m pip install -e .[dev]
python -m uvicorn app.main:app --reload
python -m pytest tests -q
```
