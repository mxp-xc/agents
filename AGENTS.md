# Agent 使用规范

本仓库用于维护个人 agents workflow 能力。

## 目录职责

- `instructions/`: 个人通用指令的唯一内容来源，通过软链接供各客户端作为全局指令读取。
- `skills/`: 可复用技能说明。
- `agents/`: 专用 agent 角色和协作协议。
- `commands/`: 可直接调用的 workflow 命令。
- `learning/`: 隔离的调研、选型和方法学习笔记，不参与能力发现与执行。

## 内容原则

- Skill 的 `SKILL.md` frontmatter 中 `description`，以及 `agents/openai.yaml` 的全部 UI 文案（包括 `display_name`、`short_description`、`default_prompt`）使用英文；正文使用中文。
- 文档只写当前事实，不写历史沿革。
- 保持轻量，先用 Markdown 记录核心约定，不提前引入复杂脚本或生成流程。
- 新增内容应包含适用场景、输入、输出、约束和验证方式。
- 错误处理、降级策略或风险点需要明确记录，不写无法验证的承诺。
