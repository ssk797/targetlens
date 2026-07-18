# TargetLens / 靶点梳理助手

面向药物研发场景的证据驱动型肿瘤靶点研读与立项辅助工作台。第一轮交付采用 Mock 优先策略：即使没有外部网络或 API Key，也可以完整演示靶点确认、研究进度、结构化靶点卡、证据抽屉、连续追问、差异化建议、三轴评分和 EGFR 教程关卡。

## 当前实现

- Next.js + TypeScript 前端工作台
- ROR1 / 三阴性乳腺癌 / ADC 的完整 Mock 会话
- 证据等级 E1–E5、来源等级 T0–T4、风险等级 R1–R4
- 证据抽屉、知识关系图谱降级表格、风险红线和可追溯元数据
- 三轮 Mock 追问与结构化 Decision Memo
- EGFR 教程首页与“靶点身份”“证据分级”两个可交互关卡
- FastAPI Mock API 骨架，支持健康检查、会话、靶点卡和 SSE 研究进度

## 启动前端

```bash
pnpm install
pnpm dev
```

浏览器打开 `http://localhost:3000`。

## 启动后端

需要 Python 环境安装 `apps/api/pyproject.toml` 中的依赖：

```bash
python -m pip install -e apps/api
python -m uvicorn app.main:app --app-dir apps/api --reload
```

健康检查：`http://localhost:8000/health`。

## 检查命令

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## 演示路径

1. 在工作台点击“新建靶点研读”，输入 `ROR1 在三阴性乳腺癌中是否适合开发 ADC？`。
2. 展开靶点卡中的证据矩阵、风险和图谱区块，点击任意来源打开证据抽屉。
3. 使用快捷追问完成三轮问答，再点击“生成差异化建议”。
4. 从左侧进入“教程练习”，打开 EGFR 课程，完成关卡 1 和关卡 4。

## 数据说明

当前所有研究内容均是带 `isMock: true` 标记的演示数据，不用于真实研发判断。正式接入阶段需要实现来源快照、数据截至时间、证据校验、连接器降级、审计日志和后端评分规则。
