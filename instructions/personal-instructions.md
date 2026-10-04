# Agent 使用规范

## 基本原则

- 对用户可见内容用中文；代码标识符、命令、技术名词保留原文。
- 技术表述准确客观；不夸大、不承诺未验证结果。

## 工作区与版本控制

- 保护已有改动，不改无关文件。
- `git commit`、`git push`、`git reset --hard`、`git clean` 及分支/worktree 变更，须用户明确要求或批准。
- 提交前检查 status/diff，只提交本次任务相关文件。

## 代码、测试与日志

- 少量代码不提前拆文件；内联低价值单次包装，保留便于调试的关键中间变量。
- 测试覆盖业务行为、关键分支、边界、错误处理和对外契约；不为覆盖率测试低价值实现细节，除非涉及产品契约、审计或排障。
- 日志框架、日志配置、上下文注入、轮转和保留策略可以测试；业务测试只验证业务结果、状态和异常契约，不断言 `logger.xxx` 是否调用、日志文案、级别或异常附件。
- 按异常所有权记录日志：异常被捕获后若会继续传播或重新抛出，当前层保留有排障价值的业务上下文日志，但不要求重复记录错误对象与堆栈，由最终处理边界统一记录；不得仅因外层会记录异常而删除局部业务日志。若异常在当前层被吞掉、降级、转换为返回值或 terminal outcome、不再传播，则当前层必须记录完整错误对象与堆栈（如 `logger.error({ err }, msg)`）。不得静默吞错或只记录 `err.message`，也不得为了生成堆栈而自抛自捕异常。

## 文档与时间

- 项目文档只写当前的架构、约定、命令、入口、约束和已知陷阱；除产品契约、审计、排障或理解所必需外，不写内部实现和历史沿革。
- 所有日期时间强制使用中国时区（不标注），格式为 `YYYY-MM-DD HH:MM:SS` 及其连续前缀，不使用 ISO8601 等其他格式。

## 工具与临时文件

- RTK：优先使用对应的原生子命令；不确定命令或参数支持情况时，查询 `rtk --help` 或 `rtk <子命令> --help`。
- 仅当 RTK 不支持目标命令或参数，或当前任务确需未经筛选的完整输出时，使用 `rtk proxy <cmd>`。
- `Glob`/`Grep` 禁止直接扫描 `/` 或 `~`。
- Python 用 `uv`：运行 `uv run`，安装 `uv add`，一次性代码用 `uv run python -c "..."`，临时依赖用 `uv run --with <pkg> python -c "..."`。
- JS/TS 用 `bun` 执行和管理依赖；业务代码保持 Node.js 兼容，使用 Node 包和 Vitest，除 bun 专属项目或启动入口外禁用 `bun:test`、`Bun.*`。
- 反复调试的 Python 脚本放 `temp/code/*.py`，用 `uv run <file>` 执行；其他临时产物放项目根目录 `temp/`。用户指定或工具强制时除外。

## 搜索与浏览器

- 网络搜索优先 `zhipu__web-*`，回退 `WebSearch`；subagent 按需继承此要求。
- 浏览器命令必须指定 session：`opencli browser <session>` 使用位置参数，`playwright-cli open` 使用 `-s`。默认 session 为 `{task}-{uuid}`，其中 uuid 由 `uv run python -c "import uuid; print(uuid.uuid4().hex[:8])"` 生成并复用；共享时用固定语义名，用户指定时从其要求。
- 不自行安装浏览器；禁用 `npx playwright install`、`google`、`puppeteer` 绕过。

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->

@/Users/maoxinchen/.codex/RTK.md
