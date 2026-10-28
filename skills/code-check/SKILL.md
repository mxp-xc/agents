---
name: code-check
description: 当需要检查指定代码中的正确性、安全性、性能、并发、资源管理、错误处理、日志、依赖、测试、代码结构或可维护性问题时使用。
disable-model-invocation: true
---

# 代码检查

检查用户指定的代码，验证疑似问题并报告可操作的 findings。默认只读：仅检查并报告；仅当用户明确要求修复时才修改代码。

## 检查范围

- 检查目标由用户指定：任意文件、目录、模块、功能或仓库，无需 Git diff、commit、branch 或 pull request。
- 检查领域由 `references/` 下的文件定义：一个文件一个大类，文件内容就是该类检查的完整 prompt（组织与维护方式见文末两节）。

## 工作流

1. 确定检查目标，读取目标项目适用的规范（CLAUDE.md、AGENTS.md、lint 配置等），提炼要点。
2. 枚举 `references/` 下全部文件，无条件为每个文件并行 spawn 一个 reviewer subagent，
   prompt 按 reviewer prompt template（见下）填充生成：检查目标、项目规范要点、该 reference 的文件路径。
   完成标准：每个 reference 文件都派出了 reviewer 且已收到返回。
3. 合并全部候选 findings，根因重叠的合并为一条。
   完成标准：候选列表中任意两条的根因互不重叠。
4. spawn 一个 verifier subagent：对每条候选，读相关代码并主动尝试反驳，分类为
   `CONFIRMED`、`PLAUSIBLE` 或 `REFUTED`。
   完成标准：每条候选都有分类。
5. 报告：排除 `REFUTED`，保留 `CONFIRMED` 与 `PLAUSIBLE`，并写明 `PLAUSIBLE` 中尚未消除的不确定性。
6. 仅当用户明确要求修复时修改代码，并在修改后验证行为。

## Reviewer prompt template

spawn reviewer 时按此模板填充生成，三段外部材料用 `<<>>` 标出：

```markdown
你是只读 reviewer：只检查、只返回候选 findings，不修改任何文件。

## 输入

- 检查目标：`<<检查目标>>`
- 项目规范：`<<项目规范要点，无则写"无">>`

## 检查要求

- 读取检查 prompt 文件，按其中的标准逐条核对。
- 每条判断都要阅读足够的关联代码与契约，在实际上下文中做出，以可观察证据为依据。
- 项目规范与检查 prompt 冲突时以项目规范为准，该条单独归类为「观察」。

## 输出

- 每条候选 finding 包含：具体位置、可观察证据、触发条件、实际影响。
- 你的输出是待验证假设，不是结论。

## 检查 prompt

- 文件：`<<reference 文件路径>>`，读取该文件，以文件内容为检查 prompt。
```

## references 约定

`references/` 是用户的个人检查规则库，一个文件 = 一个大类 = 一段给 reviewer 的检查 prompt。

- 文件名：kebab-case 英文（如 `architecture.md`），名称体现大类。
- 文件内容：一段自包含的检查 prompt，写清查什么、怎么判断、什么算问题。
- 通用部分（输出格式、只读约束、项目规范优先）由上面的模板提供，reference 只写该大类特有的判断标准。
- 内容只有检查指令本身：无 rationale、无背景、无日期、无编号。

## 新增或修改 reference

当任务是扩展规则（用户口述检查想法）而非执行检查时，按本节操作：

1. 判断归属：想法属于已有大类，编辑对应文件；是新大类，新建 kebab-case 文件。
2. 把用户想法改写成一段自包含的检查 prompt 写入文件，遵循上一节约定。
3. 保存即生效：工作流会自动发现并枚举全部文件。仅当通用模板或工作流本身需要变化时才修改本文件。
