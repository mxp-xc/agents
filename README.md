# Agents Workflow

个人 agents workflow 能力库，用来维护通用指令、可复用的 `skills`、专用 `agents` 和可执行 `commands`。

## 目录

- `instructions/`: 个人通用指令，通过软链接供各客户端作为全局指令读取。
- `skills/`: 可复用技能。每个技能聚焦一种稳定能力或工作方法。
- `agents/`: 专用 agent 配置。每个 agent 定义角色、边界、输入输出和协作方式。
- `commands/`: 可直接触发的 workflow 命令。每个命令描述触发场景、步骤和验收方式。
- `learning/`: 隔离的学习、调研和选型材料，不参与任何 skill、agent 或 command 的发现与执行；结论稳定后再提炼到能力目录。

## 约定

- 内容以 Markdown 为主，先保持轻量，不引入构建系统。
- 文件名使用小写短横线，例如 `code-review.md`。
- 新增能力时优先补齐使用场景、输入、输出、约束和验证方式。
- 临时文件放在仓库根目录 `temp/`，不要散落到能力目录中。

## 个人全局指令

统一修改 [instructions/personal-instructions.md](instructions/personal-instructions.md)。以下文件均软链接到该文件的绝对路径：

| 客户端 | 全局指令文件 |
| --- | --- |
| Codex | `~/.codex/AGENTS.md` |
| Claude Code | `~/.claude/CLAUDE.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` |

建立链接前备份已有文件；移动仓库后更新链接目标。修改后启动新会话以加载最新指令。
通用指令保留 `@/Users/maoxinchen/.codex/RTK.md` 引用，该文件独立维护并需保留在原路径。

## 快速开始

1. 在 `skills/` 记录可复用能力。
2. 在 `agents/` 记录面向任务或角色的 agent。
3. 在 `commands/` 记录可执行工作流。
4. 在 `learning/` 隔离尚未固化的研究结论。
