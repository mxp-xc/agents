# Agent 使用规范

## 基本原则

- 对用户可见内容用中文；代码标识符、命令、技术名词保留原文。
- 技术表述准确客观；不夸大、不作未验证承诺。
- 执行复杂任务或多文件改动前，先简述分析思路、改动范围和关键步骤，确认符合意图后再修改。
- 优先选择对现有架构改动最小、阅读理解成本最低的方案，不单纯追求技术先进性。

## 交互准则

- **表达逻辑**：直接、自然。先给结论，再按需解释理由，避免铺垫。
- **降噪准则**：删除反驳、重复、客套和夸赞；结尾停在有用信息上，不进行自我评价。
- **沟通边界**：针对我实际表达的观点纠错，补充辅助我做决定的关键证据，对显而易见的事实不进行过度科普。
- **引用习惯**：解释复杂技术问题时，优先给出具体的代码示例或操作路径，再做理论说明。

## 工作区与版本控制

- 保护已有改动，不改无关文件。
- 如需随代码或配置变更同步修改现有数据，先征得用户同意。
- 仅 `git push` 须用户明确要求或批准；其他 Git 操作默认允许。
- 提交前检查 status/diff，只提交本次任务相关文件。
- 提交时在 Commit Message 体现改动意图（Why），重大业务逻辑变更须在代码块上方标注动机。

{{ github.tools }}

## 维护与组织

- 调整代码、文档或规则的位置与引用时，按使用范围和读者归属：共用规则集中维护，全局入口保留通用规则与必要导航，具体内容按需读取。抽离公共内容时，权衡维护成本与阅读跳转。
- 区分参考链接与执行期依赖；公共规则应能独立理解。独立交付时按交付环境检查资源与外部依赖是否可用；源码维护说明从维护入口查阅。
- 编写指令或派发任务时写明目标、边界和完成条件；已有规则优先引用接收方可读的文件，其余内容按任务补充。
- 收到纠正后，一并排查本次改动中同一原因导致的其他问题。

## 代码、测试与日志

- 少量代码不提前拆文件。只用一次且不提升可读性或可维护性的包装函数直接内联；保留便于调试的关键中间变量。
- 仅在业务、协议或用户明确要求时计算内容 hash、SHA 等摘要，不将其作为常规验证步骤。
- 测试覆盖业务行为、关键分支、边界、错误处理和对外契约；除产品契约、审计或排障需要外，不为凑覆盖率测试内部实现细节。
- 日志框架、配置、上下文注入、轮转和保留策略可单独测试；业务测试只验证业务结果、状态和异常契约，不断言 `logger.xxx` 调用、日志文案、级别或附带的异常信息。
- 异常捕获后若继续向上抛出，当前层保留有排障价值的业务上下文日志，不因外层会记日志而省略；错误对象和堆栈由最终消费异常的一层统一记录，当前层不重复记堆栈。
- 异常在当前层被消费（如降级、转为返回值或不再外抛）时，必须记录完整错误对象和堆栈（如 `logger.error({ err }, msg)`），不静默忽略、不只记 `err.message`，也不为拿堆栈而自抛自捕。
- 识别关键路径（核心决策、外部调用、数据写入、状态流转）并加运行时日志：同一请求用 `trace_id` 串联，记录输入、关键中间值和外部响应，使一次用户操作可复现。
- 敏感资源（资产、权限、配置、用户等）的增删改和授权等关键操作，写审计日志入库，记录操作人、时间、对象、变更前后值和结果；审计日志只读。

## 代码注释与 API 字段说明

- 新增源码文件在开头简述职责与使用约定；新增类、公共函数或方法在定义处用注释或 docstring 说明职责与调用约定；新增枚举成员在旁注明取值、业务含义及与其他成员的区别。
- 新增或修改 API 请求、响应字段的业务语义时，在定义处说明用途，并按需写明允许值、默认值、省略或传空时的行为及必填/生效条件。Pydantic schema 优先用 `Field(description=...)` 写入 OpenAPI。
- 提交前对照 diff，检查本次涉及的上述代码与接口元素是否已补齐说明。

## 文档与时间

- 项目文档记录当前的架构、约定、命令、入口、约束和已知陷阱；仅在产品契约、审计、排障或理解上下文确有需要时补充内部实现与历史沿革。
- 日期时间默认使用上海时区（`Asia/Shanghai`），格式为 `YYYY-MM-DD HH:MM:SS`，可按所需精度从开头截取，如 `YYYY-MM-DD`、`YYYY-MM`。外部 API 或协议有明确要求时，遵循接口约定。

## 工具与临时文件
{{ rtk.instructions }}
- `Glob`/`Grep` 禁止直接扫描 `/` 或 `~`。
- 开发 CLI 应用时，默认优先沿用项目现有技术栈；有 Python 依赖时，优先采用 Python + Typer。
- Python 用 `uv`：运行用 `uv run`，添加依赖用 `uv add`，一次性代码用 `uv run python -c "..."`，临时依赖用 `uv run --with <pkg> python -c "..."`。
- Python 项目 CLI 优先注册命令入口，日常命令使用 `uv run <命令>`。隔离分析、固定解释器或禁止同步等场景按需添加参数，并说明用途；日常入口不默认添加 `--no-sync`、`--no-project` 或 `--no-python-downloads`。
- JS/TS 用 `bun` 执行和管理依赖；业务代码保持 Node.js 兼容，使用 Node 包和 Vitest，除 bun 专属项目或启动入口外禁用 `bun:test`、`Bun.*`。
- 项目文档和交付文件按项目目录规范存放。临时产物除用户指定或工具强制位置外，按以下规则存放：
  - 需保留或向用户展示的材料（如一次性评估报告、临时交接文档）放项目根目录 `temp/`；其中的脚本按语言放 `temp/code/<language>/*.xx`。
  - 仅供 agent 当次查看、用后即弃的过程产物放系统临时目录。

## 搜索与浏览器

- 浏览器命令必须指定 session：`opencli browser <session>` 用位置参数，`playwright-cli open` 用 `-s`。默认命名为 `{task}-{uuid}`（`uuid` 由 `uv run python -c "import uuid; print(uuid.uuid4().hex[:8])"` 生成），同一任务复用；共享 session 用能说明用途的固定名称；用户指定名称时按用户要求。
- 不自行安装浏览器；不得通过 `npx playwright install`、`google`、`puppeteer` 绕过这一限制。

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->

@/Users/maoxinchen/.codex/RTK.md


{{ harness.instructions }}
