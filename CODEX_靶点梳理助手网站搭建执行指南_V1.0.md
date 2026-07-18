---
title: "靶点梳理助手网站：Codex 工程搭建执行指南"
version: "V1.0"
date: "2026-07-18"
project: "TargetLens / 靶点梳理助手"
usage: "将本文件放置于仓库根目录，命名为 CODEX_BUILD_GUIDE.md，并要求 Codex 严格按顺序执行"
---

# 0. 给 Codex 的总指令

你是本项目的首席全栈开发工程师、前端架构师和工程实施负责人。你的任务不是输出建议，而是直接在当前代码仓库中完成可运行的网站。

必须遵守以下工作方式：

1. 先检查现有仓库，禁止在不了解已有代码的情况下整体推翻重写。
2. 先建立实施计划，再按阶段修改代码；不得一次性创建大量未经验证的文件。
3. 每完成一个阶段，必须运行对应检查命令并修复失败项。
4. 所有核心功能必须提供可演示的 Mock 模式；没有 API Key 或外部网络时，网站仍能完整演示。
5. 产品只允许两个普通用户一级入口：
   - 靶点研读工作台；
   - 教程练习中心。
6. 搜索、靶点卡、追问、风险、差异化建议和评分必须处于同一个连续会话页面。
7. 禁止自行增加独立首页、风险雷达页、知识图谱页、数据大屏、新闻中心或复杂管理门户。
8. 禁止将网站做成大面积渐变、霓虹色、玻璃拟态或普通 AI 落地页。
9. 任何关键结论必须显示来源、证据等级和数据截至时间；Mock 数据也必须遵循相同结构。
10. 不得使用 AI 输出替代正式风险规则、评分规则和后端数据校验。
11. 不得把所有逻辑堆入一个 React 页面或一个 FastAPI 文件。
12. 不得在代码中硬编码 API Key、数据库密码、模型名称和外部地址。
13. 不得只生成静态 HTML 截图；必须交付可启动、可交互、可测试的工程。
14. 遇到非关键歧义时自行采用本指南默认值，不要暂停开发反复询问。
15. 遇到影响数据库、核心路由或产品范围的重大冲突时，在 `docs/OPEN_QUESTIONS.md` 中记录，并采用最保守、最小范围的实现继续推进。

# 1. 交付目标

完成一个适合比赛演示的 Web 系统，形成以下完整链路：

```text
输入靶点或研究问题
→ 靶点实体确认
→ 显示研究进度
→ 生成结构化靶点卡
→ 查看来源与知识关系
→ 连续追问
→ 生成差异化立项建议
→ 展示机会/风险/证据评分
→ 导出报告
```

同时完成教程链路：

```text
进入教程
→ 选择 EGFR 训练课程
→ 按关卡阅读证据并提交判断
→ 获取 AI 教练提示
→ 保存学习进度
→ 生成结业报告
→ 一键进入真实靶点研读
```

# 2. 最终验收结果

项目完成时必须满足：

- `pnpm dev` 可以启动前端；
- `uv run uvicorn app.main:app --reload` 可以启动后端；
- Docker Compose 可以启动 PostgreSQL、Redis 和 MinIO；
- 默认开启 Mock 模式，无需外部 API Key 即可演示；
- 左侧存在历史记录；
- 只有“靶点研读”和“教程练习”两个主入口；
- 主工作台可输入问题并形成完整会话；
- 可展示一份完整 ROR1 或 CCR8 Mock 靶点卡；
- 可进行至少三轮追问；
- 可生成结构化差异化建议；
- 可展示三轴评分和红线；
- 可进入 EGFR 教程并完成至少两个真实交互关卡；
- 可打开证据抽屉查看来源；
- 可导出 HTML 或 Markdown 报告；
- 支持 1366×768 和 1440×900；
- TypeScript、Lint、单元测试和 E2E 测试通过；
- README 包含启动、环境变量和演示步骤。

# 3. 开始工作前的仓库检查

第一步必须执行：

```bash
pwd
find . -maxdepth 3 -type f | sort | sed -n '1,240p'
git status --short
```

然后检查：

- 是否已有 Next.js；
- 是否已有 FastAPI；
- 是否已有 `package.json`、`pyproject.toml`；
- 是否已有数据库；
- 是否已有设计系统；
- 是否已有同名路由；
- 是否已有未提交修改。

将检查结果写入：

```text
docs/CURRENT_STATE.md
```

文件必须包含：

```markdown
# 当前仓库状态
## 已有技术栈
## 已有可复用模块
## 需要保留的代码
## 需要新增的代码
## 发现的风险
## 实施顺序
```

如果仓库为空，按本指南的标准 Monorepo 结构初始化。

# 4. 实施阶段

严格按照以下顺序执行。未经前一阶段验收，不进入下一阶段。

---

# 阶段 1：工程骨架和离线 Mock 演示

## 4.1 阶段目标

先完成纯前端可演示版本，确认产品结构和视觉，不等待真实数据库和 AI。

## 4.2 推荐工程结构

```text
targetlens/
├─ apps/
│  ├─ web/
│  │  ├─ app/
│  │  │  ├─ workspace/
│  │  │  │  ├─ new/page.tsx
│  │  │  │  └─ [sessionId]/page.tsx
│  │  │  ├─ tutorial/
│  │  │  │  ├─ page.tsx
│  │  │  │  └─ [courseId]/
│  │  │  │     ├─ page.tsx
│  │  │  │     └─ lesson/[lessonId]/page.tsx
│  │  │  ├─ layout.tsx
│  │  │  └─ globals.css
│  │  ├─ components/
│  │  │  ├─ layout/
│  │  │  ├─ workspace/
│  │  │  ├─ target-card/
│  │  │  ├─ evidence/
│  │  │  ├─ decision/
│  │  │  ├─ tutorial/
│  │  │  └─ ui/
│  │  ├─ features/
│  │  │  ├─ sessions/
│  │  │  ├─ research/
│  │  │  ├─ qa/
│  │  │  ├─ scoring/
│  │  │  └─ tutorials/
│  │  ├─ lib/
│  │  │  ├─ api/
│  │  │  ├─ mocks/
│  │  │  ├─ types/
│  │  │  ├─ utils/
│  │  │  └─ constants/
│  │  └─ tests/
│  └─ api/
├─ packages/
│  └─ shared-schemas/
├─ docs/
├─ infra/
└─ tests/
```

## 4.3 初始化命令

如果不存在前端工程：

```bash
corepack enable
pnpm create next-app apps/web \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir=false \
  --import-alias="@/*"

cd apps/web
pnpm add \
  @tanstack/react-query \
  zustand \
  zod \
  lucide-react \
  class-variance-authority \
  clsx \
  tailwind-merge \
  recharts \
  cytoscape \
  react-cytoscapejs \
  react-markdown \
  remark-gfm \
  date-fns

pnpm add -D \
  @playwright/test \
  vitest \
  @testing-library/react \
  @testing-library/jest-dom \
  prettier \
  prettier-plugin-tailwindcss
```

优先使用已有 shadcn/ui；不存在时再初始化：

```bash
pnpm dlx shadcn@latest init
```

只安装实际使用的组件：

```bash
pnpm dlx shadcn@latest add \
  button input textarea card badge tabs \
  dropdown-menu dialog sheet tooltip \
  accordion progress separator skeleton \
  table scroll-area alert checkbox select
```

## 4.4 环境模式

创建：

```text
apps/web/.env.example
```

内容：

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCKS=true
NEXT_PUBLIC_APP_NAME=靶点梳理助手
```

代码必须通过 `NEXT_PUBLIC_USE_MOCKS` 切换数据层，不允许把 Mock 判断散落在组件中。

创建统一数据客户端：

```text
apps/web/lib/api/client.ts
apps/web/lib/api/mock-client.ts
apps/web/lib/api/http-client.ts
```

导出同一接口：

```ts
export interface TargetLensClient {
  listSessions(): Promise<ResearchSession[]>;
  getSession(id: string): Promise<ResearchSessionDetail>;
  createSession(input: CreateSessionInput): Promise<ResearchSession>;
  startResearch(sessionId: string, input: ResearchInput): Promise<ResearchJob>;
  getTargetCard(sessionId: string): Promise<TargetCard>;
  ask(sessionId: string, input: AskInput): Promise<GroundedAnswer>;
  generateDecisionMemo(sessionId: string): Promise<DecisionMemo>;
  getTutorials(): Promise<TutorialCourse[]>;
}
```

## 4.5 阶段验收

必须实现：

- 左侧历史栏；
- 空白工作台；
- 一条完整 Mock 会话；
- 靶点卡九个区块；
- 证据抽屉；
- 三轮 Mock 追问；
- 差异化建议；
- 评分面板；
- 教程入口和课程页。

运行：

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm dev
```

---

# 阶段 2：主工作台视觉和交互

# 5. 全局视觉规范

## 5.1 视觉定位

目标风格：

- 专业药物研发工作台；
- 接近 ChatGPT 的会话布局；
- 接近 Open Targets 的数据严谨度；
- 接近 Linear/Notion 的克制界面；
- 不模仿任何品牌 Logo；
- 不做传统后台管理大屏。

## 5.2 设计基线

```text
桌面设计：1440 × 900
最低演示：1366 × 768
左侧历史栏：248 px
折叠左栏：72 px
顶部栏：56 px
主内容最大宽度：1120 px
会话正文宽度：960 px
证据抽屉：420 px
页面左右留白：32 px
卡片间距：20 px
区块间距：24 px
圆角：10 px
```

## 5.3 色彩令牌

在 `globals.css` 或 Tailwind Theme 中定义：

```css
:root {
  --page-bg: #f6f8fb;
  --surface: #ffffff;
  --surface-muted: #f1f4f8;
  --border: #d9e0ea;
  --text-primary: #172033;
  --text-secondary: #526075;
  --text-muted: #7b8798;

  --brand: #2457a6;
  --brand-hover: #1d488c;
  --brand-soft: #eaf2ff;

  --success: #2f8f5b;
  --success-soft: #eaf7f0;
  --warning: #d98a14;
  --warning-soft: #fff7e5;
  --danger: #c53d3d;
  --danger-soft: #fff0f0;
  --info: #2f6fdb;
  --info-soft: #edf4ff;
}
```

禁止：

- 大面积渐变；
- 发光效果；
- 霓虹蓝紫；
- 大块纯红风险背景；
- 超过 4 种主色；
- 每个卡片使用不同彩色背景。

## 5.4 字体

```css
font-family:
  Inter,
  "PingFang SC",
  "Microsoft YaHei",
  "Noto Sans CJK SC",
  system-ui,
  sans-serif;
```

```text
页面标题：28 px / 650
会话标题：22 px / 650
区块标题：18 px / 600
卡片标题：15–16 px / 600
正文：14 px / 400
表格：13–14 px
元数据：12 px
核心数值：28 px / 650
```

任何内容不得小于 12 px。

# 6. 全局 Shell

## 6.1 组件树

```text
AppShell
├─ HistorySidebar
│  ├─ ProductMark
│  ├─ NewResearchButton
│  ├─ SidebarSearch
│  ├─ PinnedSessions
│  ├─ RecentSessions
│  ├─ TutorialEntry
│  └─ UserMenu
├─ MainViewport
│  ├─ SessionTopBar
│  ├─ ConversationViewport
│  └─ ResearchComposer
└─ EvidenceDrawer
```

## 6.2 左侧栏要求

必须包含：

- 产品名“靶点梳理助手”；
- 新建靶点研读；
- 搜索会话；
- 固定；
- 今天；
- 最近 7 天；
- 更早；
- 教程练习；
- 折叠；
- 用户菜单。

会话行：

```text
靶点简称 + 任务摘要
癌种 · 最近更新时间
状态图标
```

状态：

- 普通；
- 已固定；
- 需更新；
- 正在处理；
- 已生成建议。

交互：

- hover 显示更多菜单；
- 菜单含重命名、固定、归档、删除；
- 删除必须弹窗确认；
- 当前会话高亮；
- 折叠后只显示图标和 Tooltip。

# 7. 工作台空状态设计

## 7.1 页面结构

```text
顶部轻量说明
中心标题
中心副标题
大型输入框
六个快捷任务
权威来源行
免责声明
```

推荐文案：

```text
标题：快速读懂一个肿瘤靶点
副标题：整合权威数据库、论文、临床试验、指南与监管信息，
生成可追溯靶点卡，并支持连续追问与差异化立项分析。
```

输入框：

```text
输入靶点，或描述你的研究问题
例如：ROR1 在三阴性乳腺癌中是否适合开发 ADC？
```

快捷任务使用轻量按钮，不使用大卡片：

```text
快速梳理靶点
分析特定癌种
判断药物形式
查看临床进展
检查失败风险
生成差异化建议
```

权威来源显示为文本徽标：

```text
Open Targets · UniProt · PubMed · ClinicalTrials.gov · ChEMBL · FDA/EMA/NMPA
```

# 8. 研究进度消息

研究开始后，在会话流中插入 `ResearchProgressCard`。

## 8.1 进度步骤

```ts
type ResearchStage =
  | "RESOLVING_ENTITY"
  | "FETCHING_STRUCTURED_DATA"
  | "RETRIEVING_LITERATURE"
  | "BUILDING_GRAPH"
  | "GENERATING_CARD"
  | "READY";
```

显示：

```text
已识别靶点
已匹配标准实体
已获取疾病与表达证据
正在整理代表药物和临床试验
正在核查失败与监管风险
正在生成靶点卡
```

要求：

- 完成项使用勾选；
- 当前项使用轻量动画；
- 待完成项使用空心圆；
- 不使用夸张 Loading 动画；
- 可展开查看数据源状态；
- `PARTIAL_READY` 时显示未完成来源；
- 支持“重试失败来源”。

# 9. 靶点卡设计

## 9.1 总体结构

`TargetCard` 是会话中的大型复合消息，不跳转独立页面。

```text
TargetCard
├─ TargetCardHeader
├─ TargetMetrics
├─ ExecutiveSummary
├─ BiologySection
├─ ExpressionSection
├─ ValidationSection
├─ DruggabilitySection
├─ DrugClinicalSection
├─ CompetitionSection
├─ RiskSection
├─ GraphSection
└─ UnknownsSection
```

所有区块默认可见标题和摘要，详细内容可折叠。

禁止：

- 九个同等大小的小卡片平铺；
- 每段内容都套多层边框；
- 固定高度导致文字溢出；
- 横向滚动整个页面。

## 9.2 靶点头部

显示：

```text
ROR1
Receptor tyrosine kinase-like orphan receptor 1
当前范围：三阴性乳腺癌 · ADC
数据截至：2026-07-18
卡片版本：V1
```

右侧操作：

- 刷新；
- 仅官方来源；
- 导出；
- 更多。

指标行：

- 证据成熟度；
- 最高临床阶段；
- 主要药物形式；
- 风险状态；
- 竞争拥挤度；
- 引用覆盖率。

指标不得渲染为夸张仪表盘；使用简洁数值和状态文本。

## 9.3 区块统一结构

每个区块使用：

```text
标题
一句话结论
关键数据/图表
支持证据
限制与反证
查看全部来源
```

统一组件：

```ts
interface EvidenceAwareSectionProps {
  title: string;
  summary: string;
  evidenceCount: number;
  evidenceLevel?: EvidenceLevel;
  freshness?: string;
  limitations?: string[];
  children: React.ReactNode;
}
```

## 9.4 生物学功能

建议布局：

- 左侧：机制链；
- 右侧：核心功能和争议；
- 底部：证据列表。

机制链：

```text
上游调控
→ 靶点激活/异常
→ 信号通路
→ 肿瘤表型
→ 潜在干预结果
```

每条边可以点击查看证据。

## 9.5 表达与人群

建议组件：

- 癌种表达横向条形图；
- 正常组织暴露表；
- 患者亚群标签；
- 依赖性摘要；
- 固定科学边界提示。

不要在 Mock 阶段伪造精确生物学数值。可以使用标注为“演示数据”的相对等级：

```text
高 / 中 / 低 / 证据不足
```

## 9.6 靶点验证

采用证据矩阵而非雷达图。

列：

```text
等级
结论
方向
研究类型
癌种/模型
来源
时间
状态
```

证据等级徽标：

- E1 深蓝；
- E2 蓝；
- E3 绿色；
- E4 灰蓝；
- E5 灰色。

冲突证据使用橙色边框并成对展示。

## 9.7 成药逻辑

使用药物形式比较表。

```text
形式 | 适配 | 支持证据 | 主要限制 | 必须验证
```

适配值：

```text
HIGH
MEDIUM
LOW
INSUFFICIENT
```

不要只使用颜色，必须有文字。

## 9.8 代表药物和临床

默认展示 5–8 个关键项目。

视图：

- 表格；
- 时间线切换。

筛选：

- 癌种；
- 企业；
- 药物形式；
- 阶段；
- 状态；
- 地区。

关键规则：

- 完成 ≠ 成功；
- 终止必须展示原因是否已知；
- 注册状态和企业披露分来源展示；
- 点击 NCT 号进入来源。

## 9.9 风险区块

风险卡：

```text
严重度
风险类型
事件标题
适应证/地区
事实摘要
对当前方向的影响
来源等级
发布时间
审核状态
```

视觉：

- 红色仅用于 R4 标签；
- 橙色用于 R3；
- 黄色用于 R2；
- 蓝色用于 R1；
- 来源可信度单独显示 T0–T4。

不得把新闻直接渲染为正式 R4。

## 9.10 图谱

默认高度 420 px。

节点颜色按实体类型，避免超过 8 种颜色。

要求：

- 默认 1–2 跳；
- 支持缩放；
- 支持按实体类型筛选；
- 点击节点打开证据抽屉；
- 点击边显示关系、来源和有效时间；
- 不支持用户在 MVP 中拖拽编辑关系；
- 图谱加载失败时显示关系表格降级。

# 10. 对话和追问

## 10.1 消息类型

```ts
type MessageKind =
  | "USER_QUERY"
  | "ENTITY_CONFIRMATION"
  | "RESEARCH_PROGRESS"
  | "TARGET_CARD"
  | "GROUNDED_ANSWER"
  | "RISK_ALERT"
  | "DECISION_MEMO"
  | "SCORE_PANEL"
  | "REPORT_RESULT"
  | "SYSTEM_NOTICE";
```

## 10.2 回答卡

`GroundedAnswer` 固定显示：

- 结论；
- 支持证据；
- 反对/限制；
- 适用范围；
- 不确定性；
- 下一步；
- 引用；
- 数据截至时间。

引用使用 `[1] [2]`，点击打开证据抽屉。

回答状态显示：

```text
证据充分
部分支持
证据不足
存在冲突
需要复核
```

## 10.3 输入框

输入框固定在底部，但不能遮挡正文。

包含：

- 多行文本；
- 发送；
- “仅官方来源”开关；
- 当前岗位视角；
- 引用当前区块；
- 生成建议；
- 导出。

快捷追问使用可横向滚动的 Chip。

# 11. 差异化建议界面

`DecisionMemo` 不得只显示长 Markdown。

结构：

```text
项目定义
为什么值得做
难在哪里
差异化选项
下一步验证
退出条件
结论边界
```

每个差异化选项显示：

```text
差异化类型
建议内容
支持证据
限制
优先级
验证成本等级
```

类型：

```text
PATIENT_SELECTION
INDICATION
MODALITY
EPITOPE_OR_BINDING_SITE
SELECTIVITY
BIOMARKER
COMBINATION
DELIVERY
CLINICAL_STRATEGY
```

# 12. 评分界面

## 12.1 显示方式

禁止只展示单一圆形总分。

并列展示：

```text
机会基础分
风险负担分
证据置信度
调整后方向指数
建议等级
```

下面展示可展开维度：

- 临床需求；
- 生物学验证；
- 患者分层；
- 成药性；
- 竞争空间；
- 临床可行性；
- 安全可控性。

## 12.2 红线

红线单独区域，优先于总分。

有红线时：

```text
当前建议等级受红线限制
```

显示：

- 红线事件；
- 来源；
- 影响范围；
- 是否可缓解；
- 需要人工复核。

# 13. 教程中心设计

## 13.1 教程首页

只展示：

- EGFR 主课程；
- 课程目标；
- 9 个关卡；
- 完成进度；
- 继续学习。

不要做课程商城。

## 13.2 课程页面组件树

```text
TutorialShell
├─ LessonSidebar
│  ├─ CourseHeader
│  ├─ LessonList
│  └─ ProgressSummary
├─ LessonWorkspace
│  ├─ LessonGoal
│  ├─ EvidenceMaterial
│  ├─ UserTask
│  ├─ AnswerEditor
│  └─ LessonActions
└─ AICoachDrawer
```

## 13.3 至少完成两个可交互关卡

### 关卡 1：靶点身份

用户任务：

- 从候选别名中选择标准实体；
- 判断基因、蛋白和药物名称；
- 查看错误解释。

### 关卡 4：证据分级

用户任务：

- 将 5 条证据拖入 E1–E5；
- 提交后显示正确分类；
- 解释为什么体外证据不能当作临床确证。

其他关卡可以先使用内容型原型，但必须有完整路由和进度结构。

# 14. Mock 数据规范

## 14.1 文件结构

```text
apps/web/lib/mocks/
├─ sessions.ts
├─ target-card-ror1.ts
├─ answers-ror1.ts
├─ decision-ror1.ts
├─ tutorial-egfr.ts
├─ graph-ror1.ts
└─ index.ts
```

## 14.2 Mock 数据必须标识

```ts
metadata: {
  isMock: true,
  generatedForDemo: true,
  dataCutoff: "2026-07-18",
  disclaimer: "演示数据，不用于真实研发判断"
}
```

## 14.3 不得伪造

Mock 中禁止使用看似精确但未经确认的：

- 患者人数；
- 响应率；
- 风险发生率；
- 企业项目状态；
- 监管结论；
- 具体试验结果。

可使用：

- 示例性结构；
- 公开且已核验的标识；
- “高/中/低”相对级别；
- 明确写为演示的抽象数据。

# 15. TypeScript 核心类型

创建：

```text
apps/web/lib/types/domain.ts
```

最少包括：

```ts
export type EvidenceLevel = "E1" | "E2" | "E3" | "E4" | "E5";
export type SourceTier = "T0" | "T1" | "T2" | "T3" | "T4";
export type RiskSeverity = "R1" | "R2" | "R3" | "R4";

export interface SourceRef {
  id: string;
  title: string;
  organization: string;
  url: string;
  tier: SourceTier;
  publishedAt?: string;
  retrievedAt: string;
  locator?: string;
}

export interface EvidenceItem {
  id: string;
  level: EvidenceLevel;
  polarity: "SUPPORTS" | "CONTRADICTS" | "NEUTRAL";
  statement: string;
  studyType: string;
  disease?: string;
  modelOrPopulation?: string;
  limitations: string[];
  source: SourceRef;
  reviewStatus: "AUTO_ACCEPTED" | "PENDING" | "REVIEWED";
}

export interface TargetCard {
  id: string;
  sessionId: string;
  version: number;
  target: TargetIdentity;
  scope: ResearchScope;
  metrics: TargetMetrics;
  executiveSummary: string;
  biology: BiologySectionData;
  expression: ExpressionSectionData;
  validation: EvidenceItem[];
  druggability: ModalityAssessment[];
  drugs: DrugProgram[];
  trials: ClinicalTrial[];
  competition: CompetitionSummary;
  risks: RiskEvent[];
  graph: KnowledgeGraphData;
  conclusions: TargetConclusion;
  metadata: CardMetadata;
}

export interface GroundedClaim {
  id: string;
  statement: string;
  evidenceIds: string[];
  certainty: "HIGH" | "MEDIUM" | "LOW";
  limitations: string[];
}

export interface GroundedAnswer {
  id: string;
  status:
    | "SUPPORTED"
    | "PARTIAL"
    | "INSUFFICIENT_EVIDENCE"
    | "CONFLICTING_EVIDENCE"
    | "REVIEW_REQUIRED";
  summary: string;
  claims: GroundedClaim[];
  conflicts: string[];
  nextActions: string[];
  dataCutoff: string;
}

export interface ScoreSnapshot {
  baseOpportunity: number;
  riskBurden: number;
  evidenceConfidence: number;
  adjustedDirectionIndex: number;
  recommendation:
    | "STRONG_GO"
    | "GO"
    | "CONDITIONAL_GO"
    | "WATCH"
    | "NO_GO";
  dimensions: ScoreDimension[];
  redFlags: RedFlag[];
  ruleVersion: string;
}
```

类型必须完整，禁止主要数据使用 `any`。

# 16. 后端阶段

---

# 阶段 3：FastAPI 和数据库骨架

## 16.1 初始化

如果后端不存在：

```bash
mkdir -p apps/api
cd apps/api
uv init
uv add \
  fastapi \
  "uvicorn[standard]" \
  pydantic \
  pydantic-settings \
  sqlalchemy \
  asyncpg \
  alembic \
  httpx \
  tenacity \
  redis \
  celery \
  structlog \
  python-multipart \
  orjson

uv add --dev \
  pytest \
  pytest-asyncio \
  pytest-cov \
  ruff \
  mypy
```

## 16.2 后端目录

```text
apps/api/app/
├─ api/
│  ├─ dependencies.py
│  └─ v1/
│     ├─ sessions.py
│     ├─ evidence.py
│     ├─ tutorials.py
│     └─ health.py
├─ core/
│  ├─ config.py
│  ├─ logging.py
│  ├─ security.py
│  └─ errors.py
├─ db/
│  ├─ base.py
│  ├─ session.py
│  └─ models/
├─ schemas/
├─ repositories/
├─ services/
│  ├─ sessions/
│  ├─ research/
│  ├─ evidence/
│  ├─ qa/
│  ├─ scoring/
│  ├─ tutorials/
│  └─ reports/
├─ workers/
├─ connectors/
└─ main.py
```

## 16.3 核心数据库表

优先完成：

```text
research_session
session_message
session_context
target_card_version
decision_memo_version
score_snapshot
source_registry
source_snapshot
evidence_item
claim
claim_evidence
relation_fact
risk_event
tutorial_course
tutorial_lesson
tutorial_attempt
audit_log
```

字段使用 UUID，时间使用 UTC `TIMESTAMPTZ`。

必须使用 Alembic，禁止应用启动时自动临时建表作为正式方案。

## 16.4 Docker Compose

创建：

```text
docker-compose.yml
```

服务：

- postgres；
- redis；
- minio；
- api；
- worker；
- web，可选。

提供：

- healthcheck；
- named volume；
- `.env`；
- 非默认生产密码说明；
- 本地开发端口。

# 阶段 4：API 契约

## 17.1 核心接口

```text
POST   /api/v1/sessions
GET    /api/v1/sessions
GET    /api/v1/sessions/{id}
PATCH  /api/v1/sessions/{id}
DELETE /api/v1/sessions/{id}

POST   /api/v1/sessions/{id}/research
GET    /api/v1/sessions/{id}/events
GET    /api/v1/sessions/{id}/target-card
POST   /api/v1/sessions/{id}/target-card/refresh

POST   /api/v1/sessions/{id}/messages
POST   /api/v1/sessions/{id}/decision-memos
GET    /api/v1/sessions/{id}/scores
POST   /api/v1/sessions/{id}/reports

GET    /api/v1/evidence/{id}
GET    /api/v1/sessions/{id}/evidence
GET    /api/v1/sessions/{id}/graph
GET    /api/v1/sessions/{id}/risks
GET    /api/v1/sessions/{id}/landscape

GET    /api/v1/tutorials
GET    /api/v1/tutorials/{id}
POST   /api/v1/tutorials/{id}/attempts
GET    /api/v1/attempts/{id}
POST   /api/v1/attempts/{id}/lessons/{lessonId}/submit
POST   /api/v1/attempts/{id}/coach
POST   /api/v1/attempts/{id}/complete
```

## 17.2 响应规范

统一错误：

```json
{
  "code": "ENTITY_AMBIGUOUS",
  "message": "输入可映射到多个标准靶点",
  "details": {},
  "request_id": "req_xxx"
}
```

长任务：

```http
HTTP/1.1 202 Accepted
```

```json
{
  "job_id": "job_xxx",
  "status": "QUEUED",
  "events_url": "/api/v1/sessions/xxx/events"
}
```

## 17.3 SSE 事件

```text
event: research.progress
data: {"stage":"FETCHING_STRUCTURED_DATA","progress":35}

event: research.section_ready
data: {"section":"biology"}

event: research.partial_failure
data: {"source":"clinicaltrials","retryable":true}

event: research.completed
data: {"target_card_version":1}
```

实现重连和 `Last-Event-ID` 基础支持。

# 阶段 5：连接器和真实数据

## 18.1 连接器统一接口

```py
class SourceConnector(Protocol):
    source_code: str

    async def healthcheck(self) -> ConnectorHealth: ...
    async def fetch(self, request: ConnectorRequest) -> RawSourceResult: ...
    def normalize(self, raw: RawSourceResult) -> list[NormalizedRecord]: ...
```

每个连接器必须具备：

- 超时；
- 重试；
- 限速；
- User-Agent；
- 原始响应保存；
- 内容哈希；
- 来源版本；
- 错误分类；
- Mock Fixture；
- 契约测试。

## 18.2 P0 连接器顺序

按以下顺序实施：

1. UniProt；
2. Open Targets；
3. PubMed；
4. ClinicalTrials.gov；
5. ChEMBL；
6. RCSB PDB；
7. HPA；
8. 监管页面人工/半自动录入。

先保证 4 个连接器稳定，不要同时开发十多个。

## 18.3 连接器降级

外部源失败时：

- 保留其他来源结果；
- 标记数据缺失；
- 提供重试；
- 不让整个靶点卡失败；
- 不允许 AI 补造缺失事实。

# 阶段 6：AI 和 DeepSeek

## 19.1 模型配置

环境变量：

```dotenv
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=
DEEPSEEK_MODEL_FAST=
DEEPSEEK_MODEL_REASONING=
AI_ENABLED=false
AI_TIMEOUT_SECONDS=60
```

模型名称必须由环境变量配置，不在业务代码写死。

`AI_ENABLED=false` 时使用确定性 Mock Provider。

## 19.2 Provider 接口

```py
class LLMProvider(Protocol):
    async def extract_evidence(...) -> EvidenceExtractionResult: ...
    async def answer_grounded(...) -> GroundedAnswer: ...
    async def analyze_conflicts(...) -> ConflictReport: ...
    async def generate_decision_memo(...) -> DecisionMemo: ...
```

实现：

```text
MockLLMProvider
DeepSeekLLMProvider
```

## 19.3 禁止自由直连

问答顺序必须是：

```text
意图解析
→ 会话上下文
→ 结构化查询
→ 文本检索
→ 证据桶
→ 模型 JSON 输出
→ Schema 校验
→ 声明—证据校验
→ 渲染
```

不得直接：

```text
用户问题 → DeepSeek → 展示答案
```

## 19.4 JSON Schema

使用 Pydantic 定义输出，模型结果必须校验。

校验失败：

- 修复提示重试一次；
- 再失败则返回证据不足；
- 记录原始输出，仅管理员可见；
- 不把非法 JSON 展示给用户。

# 阶段 7：评分引擎

## 20.1 评分必须由后端计算

模型只能提供解释草稿，不得直接写最终分数。

实现：

```text
apps/api/app/services/scoring/rules.py
apps/api/app/services/scoring/engine.py
apps/api/app/services/scoring/schemas.py
```

## 20.2 评分维度

机会基础分：

```text
unmet_need                  15
target_validation           20
patient_selection           15
modality_fit                15
differentiation_space       15
clinical_feasibility        10
safety_controllability      10
```

风险负担：

```text
normal_tissue_window        20
known_safety_class_risk     20
clinical_failure_risk       20
regulatory_risk             15
scientific_uncertainty      15
competitive_window          10
```

证据置信度：

```text
evidence_coverage           30
source_authority            25
cross_source_consistency    20
freshness                   15
scope_clarity               10
```

## 20.3 公式

```py
confidence_factor = 0.65 + 0.35 * evidence_confidence / 100
risk_penalty = max(0, risk_burden - 50) * 0.30
adjusted = base_opportunity * confidence_factor - risk_penalty
adjusted = min(100, max(0, adjusted))
```

## 20.4 红线

红线单独处理：

- 不修改原始分；
- 限制推荐等级；
- 记录触发规则；
- 绑定证据 ID；
- 显示是否可以缓解；
- 标记人工复核。

# 21. 报告导出

MVP 支持：

- Markdown；
- HTML；
- 浏览器打印为 PDF。

报告必须包含：

- 项目范围；
- 数据截至时间；
- 卡片版本；
- 结论；
- 证据；
- 风险；
- 差异化建议；
- 评分；
- 红线；
- 引用；
- 免责声明。

禁止生成与当前会话版本不一致的报告。

# 22. 测试要求

## 22.1 前端

使用 Vitest 和 Playwright。

至少测试：

- 左栏历史记录；
- 新建会话；
- 输入靶点；
- 进度状态；
- 靶点卡展开；
- 证据抽屉；
- 追问；
- 生成建议；
- 评分红线；
- 教程提交；
- 1366×768 截图。

## 22.2 后端

至少测试：

- 会话 CRUD；
- 实体歧义；
- 长任务 202；
- SSE；
- 评分公式；
- 红线限制；
- 证据 ID 校验；
- 连接器超时和降级；
- Mock Provider；
- 非法模型输出；
- 报告版本一致性。

## 22.3 测试命令

```bash
# Frontend
cd apps/web
pnpm lint
pnpm typecheck
pnpm test
pnpm playwright test

# Backend
cd apps/api
uv run ruff check .
uv run mypy app
uv run pytest -q --cov=app
```

# 23. 可访问性

必须满足：

- 所有按钮有可读标签；
- 图标按钮有 `aria-label`；
- 键盘可操作；
- Dialog/Sheet 有焦点管理；
- 颜色不是唯一状态标识；
- 图表提供文本摘要；
- 风险等级同时显示文字；
- 表格有标题和列头；
- 输入框错误与字段关联。

# 24. 安全要求

- API Key 仅服务端读取；
- 外部 URL 使用 allowlist；
- 防 SSRF；
- 禁止抓取用户任意 URL；
- Markdown 渲染禁止原始 HTML；
- 对 Prompt 注入文本进行来源隔离；
- 用户输入不直接拼接 SQL；
- 导出内容转义；
- 删除、导出和管理操作写审计日志；
- `.env` 不提交；
- 提供 `.env.example`；
- README 提示仅使用公开数据。

# 25. Codex 的提交和进度文件

每完成一个阶段，更新：

```text
docs/IMPLEMENTATION_STATUS.md
```

格式：

```markdown
# 实施状态

## 当前阶段
## 已完成
## 运行过的检查
## 未完成
## 已知问题
## 下一步
```

维护：

```text
docs/DECISIONS.md
```

记录：

```markdown
## ADR-001 使用 SSE 而非 WebSocket
原因：
影响：
日期：
```

不要声称测试通过，除非实际运行。

# 26. 开发顺序清单

按顺序执行：

```text
[ ] 检查仓库
[ ] 编写 CURRENT_STATE.md
[ ] 初始化前端
[ ] 建立主题和 AppShell
[ ] 建立 Mock Client
[ ] 完成工作台空状态
[ ] 完成历史栏
[ ] 完成研究进度
[ ] 完成靶点卡
[ ] 完成证据抽屉
[ ] 完成追问
[ ] 完成差异化建议
[ ] 完成评分
[ ] 完成教程两个交互关卡
[ ] 完成响应式和空/错/部分状态
[ ] 前端测试通过
[ ] 初始化 FastAPI
[ ] 数据库迁移
[ ] 会话 API
[ ] Mock API
[ ] SSE
[ ] 前后端联调
[ ] 实施首批连接器
[ ] 实施 LLM Provider
[ ] 实施证据校验
[ ] 实施报告
[ ] 后端测试通过
[ ] E2E 通过
[ ] README
[ ] 离线 Demo 快照
```

# 27. 第一轮只允许完成的范围

第一次交付只做：

- 双页面 UI；
- 完整 Mock 数据；
- 工作台连续流程；
- 证据抽屉；
- 三轴评分；
- EGFR 两个交互关卡；
- 基础 FastAPI Mock API；
- SSE 模拟；
- 测试；
- README。

第一次交付禁止做：

- Neo4j；
- OpenSearch；
- 登录系统；
- 飞书；
- 商业数据库；
- 真实患者数据；
- 自动爬取 NMPA 全站；
- 自动生成分子；
- 多智能体炫技；
- 移动端完整图谱；
- 复杂工作流审批。

# 28. 第一轮完成后向用户汇报的格式

Codex 完成后必须输出：

```markdown
## 已完成
- ...

## 主要页面
- ...

## 启动方式
```bash
...
```

## 测试结果
- lint:
- typecheck:
- unit:
- e2e:

## 演示路径
1. ...
2. ...

## 未完成与原因
- ...

## 下一阶段建议
- ...
```

# 29. 最终禁止事项

- 不得只给代码片段而不修改仓库；
- 不得只写产品文档；
- 不得将所有页面做成静态图；
- 不得自行增加 5 个以上一级导航；
- 不得用单一总分代表靶点价值；
- 不得隐藏风险红线；
- 不得把无来源文本显示为事实；
- 不得把 Mock 数据伪装成实时数据；
- 不得将行业新闻直接判定为监管结论；
- 不得将完整聊天记录直接作为可信上下文；
- 不得把 DeepSeek 当搜索引擎；
- 不得把模型输出直接写入正式证据表；
- 不得跳过测试；
- 不得声称已完成未实际实现的功能。

# 30. Codex 首次执行命令

收到本指南后立即执行：

```bash
pwd
git status --short
find . -maxdepth 3 -type f | sort | sed -n '1,240p'
```

然后：

1. 创建 `docs/CURRENT_STATE.md`；
2. 创建 `docs/IMPLEMENTATION_STATUS.md`；
3. 给出 8—12 项实施计划；
4. 直接开始阶段 1；
5. 不要等待用户确认普通工程细节；
6. 完成阶段 1 后运行测试并汇报真实结果。
