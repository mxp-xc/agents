# Agent 使用规范

本仓库用于维护个人 agents workflow 能力。

## 目录职责

- `instructions/`: 个人指令及生成配置；各客户端的读取方式见个人指令维护说明。
- `src/`: 仓库级 CLI 的实现，维护说明见 [CLI 开发指南](src/README.md)。
- `skills/`: 可复用技能说明。
- `agents/`: 专用 agent 角色和协作协议。
- `commands/`: 可直接调用的 workflow 命令。
- `docs/`: 按仓库目录和主题组织的能力介绍、维护约定和限制，入口见[文档索引](docs/README.md)。
- `learning/`: 隔离的调研、选型和方法学习笔记，不参与能力发现与执行。

## 维护入口

维护能力前，通过文档索引查阅对应说明；修改个人指令或生成配置时读取[个人指令维护说明](docs/instructions/README.md)，修改 `skills/` 时读取 [Skill 通用维护约定](docs/skills/README.md)。

## 内容原则

- Skill 的 `SKILL.md` frontmatter 中 `description`，以及 `agents/openai.yaml` 的全部 UI 文案（包括 `display_name`、`short_description`、`default_prompt`）使用英文；正文使用中文。
- 文档只写当前事实，不写历史沿革。
- 保持轻量，先用 Markdown 记录核心约定，不提前引入复杂脚本或生成流程。
- 新增内容应包含适用场景、输入、输出、约束和验证方式。
- 错误处理、降级策略或风险点需要明确记录，不写无法验证的承诺。
