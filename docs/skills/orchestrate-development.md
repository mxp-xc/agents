# orchestrate-development 维护说明

用于将开发任务中的实现、测试、审查或研究等目标交给自主负责人，由协调者跟踪进展、处理依赖和阻塞、组织整合与验收。输入可以是目标与任务说明、spec、tickets 或进行中项目；输出按任务包括实现、测试结果、审查发现或研究结论及其证据，以及未解决的问题。

运行时规则以 [SKILL.md](../../skills/orchestrate-development/SKILL.md) 为准，通用维护要求见 [Skill 通用维护约定](README.md)。

## 文件归属

| 位置 | 用途 |
| --- | --- |
| [skills/orchestrate-development/](../../skills/orchestrate-development/) | 正式执行与分发版本 |
| [temp/orchestrate-development/](../../temp/orchestrate-development/) | 保留的工作草案，供后续试改与审阅 |
| [references/workspaces.md](../../skills/orchestrate-development/references/workspaces.md) | 工作区、整合和清理的补充约定 |
| [references/examples.md](../../skills/orchestrate-development/references/examples.md) | 按需读取的情境示例 |
| [agents/openai.yaml](../../skills/orchestrate-development/agents/openai.yaml) | 英文展示文案及显式调用策略 |

草案更新经检查后，再同步到正式目录。正式版本不依赖 `temp/`，也不回链维护文档。当前客户端已有的目录链接可发现正式版本，不从 `temp/` 加载执行规则。

## 维护边界

- 保留协调者与各类负责人的分工，以及负责人在任务范围内选择方法、执行和继续委派的能力。阻塞先交由上级处理，只有上级无法决定或需要用户信息、选择、授权时才询问用户。
- 实现入口使用 `SKILL.md` 中约定的外部 `implement` 技能。分发或更换环境时核对该入口及其必要依赖是否可读取；更新入口时同步检查派工说明。
- 本 Skill 仅供用户显式调用，保留 `disable-model-invocation: true` 和 `policy.allow_implicit_invocation: false`。派工传递具体目标、流程及约束，不要求下级加载本协调 Skill。
- 调度过程由本 Skill 自身维护。借鉴其他工作流时，核对其输入、后续依赖和额外执行成本；情境建议留在示例中，不据此增加统一门槛。

## 修改与验证

核对草案与正式版本的预期差异，修改归属明确后再同步。涉及工作区选择、引用条件或资源移动时，同步检查对应参考文件与读取入口。

检查 frontmatter、展示文案和调用策略；核对内部引用在独立分发目录中可解析，以及约定的外部实现入口可用。用相关场景检查规划、派工、进度纠偏、逐级处理阻塞和交付条件是否一致。静态检查与文档审阅不能替代实际调度验证。
