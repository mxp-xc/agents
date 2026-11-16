# project-structure 维护说明

修改入口流程、通用原则、参考文件组织方式或展示文案前，先读本文，再定位对应文件。运行时规则以 [SKILL.md](../../skills/project-structure/SKILL.md) 为准；本文说明维护边界。

通用要求见 [Skill 通用维护约定](README.md)。

## 能力定位

指导新项目的目录骨架和已有项目的结构调整，只处理结构、职责与模块边界。维护时保留：空项目与已有项目两条路径、执行时 ls references/ 按文件名读取参考文件、用户确认后才改文件、技术栈由用户决定（本 skill 只推荐）。

## 目录职责

| 位置 | 维护内容 |
| --- | --- |
| [SKILL.md](../../skills/project-structure/SKILL.md) | 工作流、通用原则、references 的读取方式 |
| [references/](../../skills/project-structure/references/) | 按语言子目录组织的框架规范（一个文件一个框架）；[index.md](../../skills/project-structure/references/index.md) 说明结构与使用顺序，各语言子目录的 picks.md 放该语言选型推荐，语言无关的规范（ddd.md）放根目录 |
| [agents/openai.yaml](../../skills/project-structure/agents/openai.yaml) | 展示名称、简述和默认提示词，与手动调用策略一致 |

正文与展示文案的语言规则见仓库 [AGENTS.md](../../AGENTS.md)，以其为准。保留现有调用策略，除非用户明确要求调整。

## 规则归属与引用

- 所有分支共用的规则留在 SKILL.md 通用原则；只与一种框架相关的规则放对应 references/ 文件，不重复写回 SKILL.md。
- 文件名是索引：SKILL.md 与本文不逐个登记参考文件。新增框架参考时，放一个 `<框架>.md` 到 references/ 对应语言子目录（语言无关的规范放 references/ 根目录）即可；只有读取方式本身变化时才改 SKILL.md 工作流。
- 参考文件之间可以链接（组合型文件指向组件文件）。
- 各语言 picks.md 里的版本事实会过期：写当前稳定版本并附来源链接，维护时对照复核，不在 SKILL.md 重复版本信息。

## 修改与验证

1. 改通用原则前，确认它适用于所有框架；只适用于一种框架的规则放到对应 references/。
2. 新增框架参考：`<框架>.md` 放 references/ 对应语言子目录，语言无关的放根目录；新增语言时建子目录并放 picks.md。文件名即索引，无需登记。
3. 引用只落在 skill 目录内，SKILL.md 不引用 docs/ 或仓库外层资源。
4. 用两个场景推演：空项目走通骨架与验证，已有项目走通诊断、迁移与验证。检查两个场景下 agent 都能按语言子目录与文件名在 references/ 定位所需规则，目录树与约束不互相矛盾。
