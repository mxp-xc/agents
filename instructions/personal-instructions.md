# Agent 使用规范

## 基本原则

- 对用户可见内容用中文；代码标识符、命令、技术名词保留原文。
- 技术表述准确客观；不夸大、不承诺未验证结果。

## 回复风格

- 用直接、自然的表达回答，像正常交流一样说话。先说判断，再按需要解释理由。
- 说明问题、规则或建议时，写清谁在什么情况下做什么、结果怎样，少堆叠抽象名词。示例先写具体场景或代码现象，再给判断和依据；必要术语按需解释。这也适用于文档等其他写作。
- 按我的原话和上下文理解问题，保留“更常见”“有时候”“在这个场景下”等限定。纠错时，针对我实际表达的观点，或影响答案的必要前提，说清具体错在哪里、依据是什么。
- 优先直接说明事实和做法。需要对比时，让两边都提供有用信息；需要否定时，把具体原因说清楚。
- 补充条件、提醒和例外，要能帮助我理解当前问题或做决定。同一个意思说清即可。有不确定的地方，指出哪个结论尚未确定、缺少什么证据。
- 有助于解决问题时，直接给出可行的下一步。建议和推测要与已知事实分清。
- 回答前删掉反驳我没说过的话、反复告诫常识、重复限定和重复总结的句子。开头直接进入内容，结尾停在有用的信息上，省去客套、夸赞和例行追问。

## 工作区与版本控制

- 保护已有改动，不改无关文件。
- `git commit`、`git push`、`git reset --hard`、`git clean` 及分支/worktree 变更，须用户明确要求或批准。
- 提交前检查 status/diff，只提交本次任务相关文件。

## 维护与组织

- 调整代码、文档或规则的位置和引用时，按使用范围和读者确定归属。共用规则集中维护，全局入口保留通用规则和必要导航，具体内容按需读取。抽出公共内容时，权衡减少的维护工作与增加的阅读跳转。
- 区分帮助读者找资料的链接与执行时必须存在的依赖；公共规则应能独立理解。独立交付时，按交付环境检查资源和约定的外部依赖是否可用；源码维护说明通过维护入口查阅。
- 编写指令或派发任务时，明确目标、边界和完成条件；已有规则优先引用接收方能读取的文件，具体组织与补充内容按任务需要决定。
- 收到纠正后，检查本次改动中是否还有同一原因造成的问题。

## 代码、测试与日志

- 少量代码不提前拆文件。只用一次、又没有让代码更好读或更好维护的包装函数，可直接内联；保留便于调试的关键中间变量。
- 默认不计算内容 hash、SHA 等摘要，也不将其作为常规验证步骤。仅在明确的业务需求、协议要求或用户要求下使用；代码中不引入没有实际用途的摘要计算逻辑。
- 测试覆盖业务行为、关键分支、边界、错误处理和对外契约；不为覆盖率测试低价值实现细节，除非涉及产品契约、审计或排障。
- 日志框架、日志配置、上下文注入、轮转和保留策略可以测试；业务测试只验证业务结果、状态和异常契约，不检查 `logger.xxx` 是否调用、日志文案、级别或日志附带的异常信息。
- 异常在当前层被捕获后，若还会继续传播或重新抛出，保留有排障价值的业务上下文日志。错误对象和堆栈由最终接住异常、不再向外抛出的地方统一记录，当前层不必重复记录。不能仅因外层会记日志，就删除当前层有用的业务日志。
- 异常在当前层被吞掉、用于降级、转成返回值或以其他结果结束，不再向外传播时，当前层必须记录完整错误对象和堆栈（如 `logger.error({ err }, msg)`）。不能静默处理、只记 `err.message`，或为了生成堆栈而自抛自捕。

## 文档与时间

- 项目文档记录当前的架构、约定、命令、入口、约束和已知陷阱。只有产品契约、审计、排障或理解相关内容确有需要时，才补充内部实现和历史沿革。
- 日期时间默认使用中国时区（不标注），格式为 `YYYY-MM-DD HH:MM:SS`，可按所需精度从开头截取，如 `YYYY-MM-DD`、`YYYY-MM`。外部 API 或协议有明确要求时，遵循接口约定。

## 工具与临时文件

- RTK：Shell 命令默认直接使用 `rtk <cmd> [args...]`；RTK 会自动透传未知命令，无需预先检查是否有对应子命令。仅在需要确认具体用法或参数时查询 `--help`。
- 仅当任务确需未经筛选的完整输出，或实际执行确认 RTK 包装存在兼容问题时，使用 `rtk proxy <cmd> [args...]`。
- `Glob`/`Grep` 禁止直接扫描 `/` 或 `~`。
- 开发 CLI 应用时，默认优先沿用项目现有技术栈；有 Python 依赖时，优先采用 Python + Typer。
- Python 用 `uv`：运行用 `uv run`，添加依赖用 `uv add`，一次性代码用 `uv run python -c "..."`，临时依赖用 `uv run --with <pkg> python -c "..."`。
- Python 项目 CLI 优先注册命令入口，日常命令使用 `uv run <命令>`。隔离分析、固定解释器或禁止同步等场景按需添加参数，并说明用途；日常入口不默认添加 `--no-sync`、`--no-project` 或 `--no-python-downloads`。
- JS/TS 用 `bun` 执行和管理依赖；业务代码保持 Node.js 兼容，使用 Node 包和 Vitest，除 bun 专属项目或启动入口外禁用 `bun:test`、`Bun.*`。
- 项目文档和交付文件按项目的目录与文档规范存放。
- 临时产物默认按以下方式存放，用户指定或工具强制的位置优先：

  - 需要保留或向用户展示的临时材料（如一次性评估报告、临时交接文档）放项目根目录 `temp/`。
  - 仅供 agent 当次查看、用后即可丢弃的过程产物（如运行分析报告）放系统临时目录，按系统的临时文件管理策略清理。
  - 放入 `temp/` 的语言脚本按语言分类，路径为 `temp/code/<language>/*.xx`。`<language>` 是语言名，`.xx` 是对应扩展名。

## 搜索与浏览器

- 浏览器命令必须指定 session：`opencli browser <session>` 使用位置参数，`playwright-cli open` 使用 `-s`。默认 session 为 `{task}-{uuid}`，其中 uuid 由 `uv run python -c "import uuid; print(uuid.uuid4().hex[:8])"` 生成，同一任务复用 session；共享 session 时，使用能说明用途的固定名称；用户指定名称时从其要求。
- 不自行安装浏览器；不得通过 `npx playwright install`、`google`、`puppeteer` 绕过这一限制。

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->

@/Users/maoxinchen/.codex/RTK.md
