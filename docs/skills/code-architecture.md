# code-architecture 维护说明

修改工作流、档位判定标准、参考文件索引或展示文案前先读本文，再定位对应文件。运行时规则以 [SKILL.md](../../skills/code-architecture/SKILL.md) 为准。

通用要求见 [Skill 通用维护约定](README.md)。

## 能力定位

- **自主触发（model-invoked）**：面向新建项目、新增独立业务模块、未上线早期代码结构整理，以及既有系统补齐规范与架构护栏的场景；不设置 `disable-model-invocation: true`。
- **与 `project-structure` 的边界**：`project-structure` 聚焦目录骨架与文件摆放（用户手动触发）；`code-architecture` 负责分层边界、技术栈关键选型拍板、落盘 `docs/CODING_STANDARDS.md`、接入自动化架构护栏（ArchUnit / ESLint + dependency-cruiser / import-linter）并交付标杆垂直切片。

## 目录职责与单一事实源

| 位置 | 维护内容（单一事实源） |
| --- | --- |
| [SKILL.md](../../skills/code-architecture/SKILL.md) | 触发指针、按需加载路由图、5 步执行流（含完成标准）、顶层依赖图与 4 条架构底线 |
| [references/index.md](../../skills/code-architecture/references/index.md) | 参考文件读取路由图、职责速查表与扩展约定 |
| [references/architecture-principles.md](../../skills/code-architecture/references/architecture-principles.md) | 3 分支初始化决策流、未上线 vs 已上线策略、4 档架构选型矩阵、全局目录二分图、统一响应 `ApiResponse` + `X-Trace-Id` + 唯一默认 `BusinessException` + 分散全大写点分层 `ErrorCode`、规则归属表、反过度设计 5 检 |
| [references/ddd-guide.md](../../skills/code-architecture/references/ddd-guide.md) | `modules/*` 拆分 4 判据、四层内部结构与代码形态对比、跨模块事务与查询协作、L1 vs L2 裁剪矩阵、假 DDD 反模式排雷 |
| [references/coding-standards-template.md](../../skills/code-architecture/references/coding-standards-template.md) | 落盘至目标仓库 `docs/CODING_STANDARDS.md` 的规范模板 |
| [references/stacks/java.md](../../skills/code-architecture/references/stacks/java.md) | Java/Spring Boot 目录树、运行时调用树、5 项起手选型、正反模式 diff、ArchUnit 护栏测试 |
| [references/stacks/python.md](../../skills/code-architecture/references/stacks/python.md) | Python/FastAPI 轻量展平目录树、依赖与调用树、统一响应与 `BusinessException` 模板、`import-linter` + `ruff` + `pyrefly` 配置 |
| [references/stacks/typescript-web.md](../../skills/code-architecture/references/stacks/typescript-web.md) | 前端 `app/features/shared` 组件调用链、Node 后端 `modules/` + 展平横切树、ESLint + `dependency-cruiser` 护栏 |
| [agents/openai.yaml](../../skills/code-architecture/agents/openai.yaml) | 展示名称、简述、默认提示词与 `allow_implicit_invocation: true` 策略 |

## 写作与维护原则

- **渐进式披露与消除重复**：`SKILL.md` 只保留工作流步骤、完成标准、读取路由指针与核心底线图，不在 `SKILL.md` 重复展开 `architecture-principles.md` 和 `ddd-guide.md` 的详细规则表。
- **视觉优先（参考 `show-me`）**：优先用伪代码分支（`if/else`）、调用树、ASCII 依赖图、浅层文件树和 `diff` 正反例替代大段文字叙述。
- **独立分发**：所有引用落在 `skills/code-architecture/` 内部，不回链仓库外层 `docs/`、`AGENTS.md` 或 `instructions/`，不出现特定业务项目私有词。

## 修改与验证

1. 核对 `SKILL.md` frontmatter 未启用 `disable-model-invocation: true`，且 `agents/openai.yaml` 中 `allow_implicit_invocation` 为 `true`。
2. 检查 `skills/code-architecture/` 内全部相对链接目标均存在，且无越出目录的引用。
3. 运行仓库测试 `uv run python -m unittest discover -s tests`，确保全绿。
