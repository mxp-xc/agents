# ddd-architecture 维护说明

修改工作流、梯度判定标准、参考文件索引或展示文案前，先读本文，再定位对应文件。运行时规则以 [SKILL.md](../../skills/ddd-architecture/SKILL.md) 为准；本文说明维护边界。

通用要求见 [Skill 通用维护约定](README.md)。

## 能力定位

- **自主触发（model-invoked）**：面向新建项目、新增独立业务模块或**尚未上线/早期开发阶段**需要结构整改的场景；不设置 `disable-model-invocation: true`，由全局指令指针或模型自主判断触发。
- **与 `project-structure` 的边界**：`project-structure` 聚焦纯目录骨架与文件摆放（用户手动触发）；`ddd-architecture` 负责务实 DDD 分层边界、技术栈关键选型拍板、落盘 `CODING_STANDARDS.md`、接入机械架构护栏（ArchUnit / ESLint + dependency-cruiser / import-linter）并交付标杆垂直切片。
- **维护保留原则**：保留按“运行阶段（未上线 vs 已上线）”判定演进自由度的步骤、L1（默认）/ L2 两档梯度区分、4 步落盘闭环与受限环境降级策略。

## 目录职责

| 位置 | 维护内容 |
| --- | --- |
| [SKILL.md](../../skills/ddd-architecture/SKILL.md) | 触发语义、5 步工作流及完成标准、通用架构红线、约束与降级策略 |
| [references/index.md](../../skills/ddd-architecture/references/index.md) | 参考文件导航、必读与按栈读取顺序、扩展约定 |
| [references/ddd-tactical-guide.md](../../skills/ddd-architecture/references/ddd-tactical-guide.md) | 语言无关四层职责、分包策略、L1/L2 梯度、规则机制选型表、未上线整改 vs 已上线演进、反过度设计清单 |
| [references/coding-standards-template.md](../../skills/ddd-architecture/references/coding-standards-template.md) | 落盘至目标仓库根目录的 `CODING_STANDARDS.md` 模板 |
| [references/*.md](../../skills/ddd-architecture/references/) | 各语言/框架特化落地方案与机械护栏模板（当前含 `java-spring.md`、`typescript-web.md`、`python.md`） |
| [agents/openai.yaml](../../skills/ddd-architecture/agents/openai.yaml) | 展示名称、简述、默认提示词与 `allow_implicit_invocation: true` 策略 |

正文与展示文案的语言规则见仓库 [AGENTS.md](../../AGENTS.md)（`description` 与 `openai.yaml` 文案用英文，正文用中文）。

## 规则归属与引用

- 所有语言通用的 DDD 原则、梯度表与防过度设计检查留在 `references/ddd-tactical-guide.md`，通用流程与红线留在 `SKILL.md`。
- 仅属于单一语言或生态的目录树、框架选型与静态护栏代码放到 `references/<lang-framework>.md`，不回写进 `SKILL.md` 或全局指令。
- 新增技术栈支持时，在 `references/` 新增 `<lang-framework>.md` 并在 `references/index.md` 登记，只有读取机制变化时才修改 `SKILL.md`。
- 本技能目录内保持独立分发：所有引用落在 `skills/ddd-architecture/` 内部，不回链 `docs/`、`AGENTS.md` 或 `instructions/`，也不绑定任何特定业务项目名称。

## 修改与验证

1. 核对 `SKILL.md` frontmatter 未启用 `disable-model-invocation: true`，且 `agents/openai.yaml` 中 `allow_implicit_invocation` 为 `true`。
2. 检查 `skills/ddd-architecture/` 内全部相对链接目标均存在，且无越出目录的引用。
3. 核对三类场景在文档中有明确落点：未上线新项目从 0 到 1 建骨架与护栏、未上线早期代码职责错位整改、已上线系统保护契约渐进接入护栏。
