# Agent 使用规范

## 基本原则

- 对用户可见内容用中文；代码标识符、命令、技术名词保留原文。
- 目标明确、范围小的改动直接执行；多文件、架构性或影响面大的改动先简述分析思路、改动范围和关键步骤，确认后再修改。
- 收到纠正后，一并排查本次改动中同一原因导致的其他问题。
- **已上线或有外部稳定依赖的系统**：采用对现有架构改动最小、风险可控的渐进方案。
- **新建项目、新独立模块或未上线系统**：建立并维护清晰的分层与模块边界（MVP 缩减功能范围，不降级工程骨架），发现职责错位或结构腐化时主动提出整理；涉及确立目录骨架或架构整理时，先调用 `ddd-architecture` 技能确立架构蓝图、`CODING_STANDARDS.md` 与架构护栏再展开实现。

## 交互准则

- 回复先给结论，再按需解释理由；去掉客套、夸赞、铺垫和结尾自我评价。
- 针对我实际表达的观点纠错并补充关键证据；解释复杂技术问题时先给代码示例或操作路径。

## 界面设计

- 界面设计、改版和交互原型默认采用 `ui-designer`（角色名 `UI Designer`）角色规范；用户指定其他角色时按其要求执行。
- 若同时命中「T3 Code：任务委派」中的默认模型规则（如前端开发默认用 `deepseek-flash`），**模型优先**：通过跨模型委派执行并在提示中注入角色定义，不得为调用原生命名角色而回退到主模型。
- `$impeccable` 是可选的补充设计技能。

## 工程与代码规范

- 编写或修改业务代码、测试、错误处理、运行时或审计日志、API schema，或提交前检查注释与字段说明时，先读取 `{{ agentctl.config-dir }}/references/coding-standards.md`。

## 工作区与版本控制

- 提交前检查 status/diff，只改动并提交本次任务相关文件；如需随代码或配置变更同步修改现有数据，先征得用户同意。
- 仅 `git push` 须用户明确要求或批准；其他 Git 操作默认允许。
- Commit Message 体现改动意图（Why）；重大业务逻辑变更在代码块上方标注动机。{{ github.tools }}

## 文档与时间

- 项目文档记录当前的架构、约定、命令、入口、约束和已知陷阱；仅在产品契约、审计、排障或理解上下文确有需要时补充内部实现与历史沿革。
- 日期时间默认使用上海时区（`Asia/Shanghai`），格式 `YYYY-MM-DD HH:MM:SS`，可按精度从开头截取（如 `YYYY-MM-DD`、`YYYY-MM`）；外部 API 或协议另有要求时遵循接口约定。

## 工具与临时文件
{{ rtk.instructions }}
- `Glob`/`Grep` 禁止直接扫描 `/` 或 `~`。
- 开发 CLI 应用优先沿用项目现有技术栈；有 Python 依赖时优先采用 Python + Typer。
- Python 使用 `uv`（`uv run`、`uv add`、`uv run python -c`、`uv run --with <pkg> python -c`）；CLI 优先注册命令入口并用 `uv run <命令>`，日常入口不默认加 `--no-sync`、`--no-project` 或 `--no-python-downloads`（确需隔离或固定解释器时按需添加并说明）。
- JS/TS 用 `bun` 执行和管理依赖；业务代码保持 Node.js 兼容，使用 Node 包和 Vitest，除 bun 专属项目或启动入口外禁用 `bun:test`、`Bun.*`。
- 项目文档和交付文件按项目目录规范存放。临时产物除用户指定或工具强制位置外：
  - 需保留或向用户展示的材料（评估报告、临时交接文档）放项目根目录 `temp/`，脚本按语言放 `temp/code/<language>/*.xx`。
  - 仅供 agent 当次查看、用后即弃的过程产物放系统临时目录。

## 浏览器

- 浏览器命令必须指定 session：`opencli browser <session>` 用位置参数，`playwright-cli open` 用 `-s`。默认命名为 `{task}-{uuid}`（`uuid` 用 `uv run python -c "import uuid; print(uuid.uuid4().hex[:8])"` 生成），同一任务复用；共享 session 用能说明用途的固定名称；用户指定名称时按用户要求。
- 不自行安装浏览器，不得通过 `npx playwright install`、`puppeteer` 等工具绕过。

{{ t3.instructions }}

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
{{ harness.instructions }}