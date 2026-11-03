# 个人指令维护

`target`、指令模板和默认配置的含义见[个人指令术语](../../GLOSSARY.md)。

`agentctl instructions` 从 Markdown 模板和 TOML 配置生成普通 Markdown，不启动 harness，不执行或上传源文件中的内容。默认目标是各 harness 的全局指令路径；开发测试时通过 `--test` 显式切换到仓库内的 `generated/`，该目录是被 Git 忽略的可重建产物。

## 当前维护入口

四个 harness 的全局指令均读取生成的普通文件。公共规则维护在 `instructions/template.md`，专属规则维护在对应的 target TOML；“回复风格”和“GitHub 工具”由 Codex 配置提供，其他 target 默认不生成。修改源文件后先预览，再运行 `uv run agentctl instructions sync --all` 并检查结果。

模板本身决定组合顺序；当前先放公共规则，末尾 `{{ harness.instructions }}` 放专属规则。生成文件直接包含替换后的 Markdown。成对的 `{{ ... }}` 中，去除两端空白后的完整文本是 key；其他内容原样保留，TOML 值也不会递归解析。未配对的 `{{`、单独的 `}}` 及 `{% ... %}` 视为普通文本；空 key 报错。配置值应写成可独立插入当前位置的完整 Markdown，避免破坏标题和列表结构。公共规则保持通用，专属规则只补充适用范围或明确说明差异；若存在冲突，文件中出现的先后顺序不保证改变各 harness 的指令优先级。

## 配置与扩展

- `instructions/template.md`：公共 Markdown 模板，使用 `{{ group.key }}` 形式的占位符；不支持 Jinja 表达式或控制语句。
- `instructions/agents/default.toml`：占位符的默认值；当前 `harness.instructions` 为空字符串，表示没有专属补充。
- `instructions/agents/<target>.toml`：target 文件名即 CLI 中的名称；`[target].output` 是正式目标路径，`test_output` 是测试路径，其他表提供占位符的值。

例如，在模板放入 `{{ github.tools }}`，在默认配置中提供可选的公共默认值，并在目标配置中覆盖：

```toml
[target]
output = "~/.codex/AGENTS.md"
test_output = "generated/codex/AGENTS.md"

[github.tools]
value = """
- 根据该 harness 支持的能力选择 GitHub 工具。
"""
```

渲染时每个 key 优先采用 target 的值，再回退到 default；模板引用的 key 在两处都不存在时报错。空字符串是明确配置的值，不触发回退。default 文件可以不存在，但这时所有 key 都必须由 target 提供。模板未引用的配置 key 会报错。TOML 嵌套表路径以点连接成 key，路径不同但结果相同时报冲突；特殊字符使用 TOML 带引号的表名，例如 `{{ github[field] }}` 对应 `["github[field]"]`。新增占位符时，为所有目标提供相应值或配置默认值，再运行全量检查。新增 harness 时添加一个 TOML 文件并配置不同目标路径，CLI 会自动发现；无需修改生成逻辑。配置项必须是 TOML 字符串，配置文件和模板使用 UTF-8。

相对输出路径相对于项目根目录，支持 `~` 和环境变量展开；使用所在系统的路径语义。正式目标的父目录必须预先存在；测试目标的父目录在写入时自动创建，dry-run 和 check 不创建目录。指定 `--test` 时，所有选中 target 都必须配置 `test_output`，缺少时立即报错，避免意外回退到正式路径。新增 target 时应一并配置测试路径。

## 日常操作

从仓库根目录运行：

```bash
uv run agentctl instructions sync --all --test --dry-run
uv run agentctl instructions sync codex --test
uv run agentctl instructions sync --all --test
uv run agentctl instructions check --test
uv run python -m unittest discover -s tests -v
```

省略 target 等同全部；也可以指定多个 target。子命令的 `--root` 可指定项目根目录，省略 `--test` 则操作各 target 配置中的正式路径。先用 `sync --dry-run` 查看目标和差异，确认后执行 `sync`。源文件或配置变更后重新生成，再运行全量 `check`；输出缺失、不一致时退出码为 1，配置和读写错误为 2，成功为 0。`check` 只校验所选目标：默认检查全部；生成文件未经写入时检查会报告不一致。

生成器在目标旁的隐藏文件 `.<文件名>.agentctl-state` 保存上次生成内容，用于识别生成文件和检测人工修改；记录也包含指令内容，应与目标文件一样保护。记录缺失或内容不一致时，默认拒绝覆盖与本次生成结果不同的文件；软链接也默认拒绝覆盖。要预览或执行此类覆盖必须显式加 `--force`。强制覆盖会丢失原文件内容；目标是软链接时替换链接本身，不沿链接写入其目标。先备份再操作。`--dry-run` 不写入文件，带 `--force` 才能预览被保护目标的替换内容。

写入前先检查全部选中目标，内容不变时不重写；写入使用目标目录中的临时文件和原子替换。每个目标使用独占锁，防止本工具的并发写入；进程异常终止可能遗留 `.<文件名>.agentctl.lock`，确认没有相关运行进程后再人工删除。写入前还会检查目标是否在预检后变化。跨多个目标不提供整体原子性：运行中失败时会列出已经更新的目标并停止后续写入。

## 迁移真实全局指令

将其他已有指令文件迁移到生成方式前：

1. 确认各 harness 的读取路径和当前文件类型，检查模板、目标专属规则及生成内容。
2. 用户确认迁移方案后，备份现有链接和文件；确认各 target 中的正式路径，使用带 `--force` 的 dry-run 预览目标和内容，再明确执行。
3. 检查生成文件及 harness 的实际加载行为，必要时从备份恢复。

本工具不会自动接入启动流程；如有需要，可由用户在确认启动方式和失败处理后自行选择性调用。当前三个已核查的 Codex、Claude Code 和 OpenCode 全局指令路径不由 chezmoi 管理，chezmoi 另管理 OpenCode 配置。若将来选择由 chezmoi 管理生成结果，应先审查 source 和 apply 的覆盖行为并单独确定迁移方案；本工具不会修改 chezmoi。

模板保留的 `@/Users/maoxinchen/.codex/RTK.md` 是原指令中的外部引用，工具不会展开它；迁移到其他机器或 harness 前需确认目标环境及 harness 对该引用的支持。
