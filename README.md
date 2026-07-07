# Agents Workflow

个人 agents workflow 能力库，用来沉淀可复用的 `skills`、专用 `agents` 和可执行 `commands`。

## 目录

- `skills/`: 可复用技能。每个技能聚焦一种稳定能力或工作方法。
- `agents/`: 专用 agent 配置。每个 agent 定义角色、边界、输入输出和协作方式。
- `commands/`: 可直接触发的 workflow 命令。每个命令描述触发场景、步骤和验收方式。

## 约定

- 内容以 Markdown 为主，先保持轻量，不引入构建系统。
- 文件名使用小写短横线，例如 `code-review.md`。
- 新增能力时优先补齐使用场景、输入、输出、约束和验证方式。
- 临时文件放在仓库根目录 `temp/`，不要散落到能力目录中。

## 快速开始

1. 在 `skills/` 记录可复用能力。
2. 在 `agents/` 记录面向任务或角色的 agent。
3. 在 `commands/` 记录可执行工作流。
