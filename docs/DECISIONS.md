# 工程决策记录

## ADR-001 使用 SSE 而非 WebSocket

原因：研究任务是服务端向前端推送阶段性进度，SSE 在浏览器端接入成本更低、便于断线重连，也更符合第一轮单向进度流的需求。

影响：前端使用事件流展示 `RESOLVING_ENTITY`、`FETCHING_STRUCTURED_DATA`、`GENERATING_CARD` 和 `READY` 等阶段；后续如加入双向协作，再评估 WebSocket。

日期：2026-07-18
