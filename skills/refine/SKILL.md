---
name: refine
description: Iteratively refine a target (spec/plan/doc/design/code) over N rounds of multi-angle review → verify → sweep → in-place modify until convergence.
disable-model-invocation: true
argument-hint: "[target] [times] [effort] [--for <desc>]"
---

# Refine（迭代精炼）

迭代精炼 spec/plan/doc/design/代码等目标物至收敛。代码也支持（`code-review` 含 `--fix` 更专精）。

**目录**：接口 · 目标物类型判定 · description 方向聚焦 · effort · 核心循环 · 迭代记忆 · critic · verify · sweep · modify · 收敛与停止 · 报告 · 走查示例

## Quick start

```
/refine spec.md 2 high                      # 默认全面挑刺
/refine spec.md 2 high --for 检查有没有 bug  # 聚焦查 bug
/refine spec.md --for 优化话术              # 默认 2 轮 medium，优化话术
/refine --for 检查写得好不好                 # 最近产物，检查质量
```

## 接口

`/refine [target] [times] [effort] [--for <desc>]`：

- **target**：路径/文件名/片段→文件；自然语言指代（"spec""上面的方案"）→会话产物；省略→最近 AI 产物。模糊或读不到→问用户或中止。
- **times**：纯数字，默认 `2`，上限 `5`（超出截断并提示）。
- **effort**：`low`/`medium`/`high`/`xhigh`/`max`，默认 `medium`。
- **--for <desc>**：迭代方向，放最后跟自然语言。未提供则全面挑刺。

## 目标物类型判定

按文件名/内容判定，未知/模糊→通用兜底。

**角度库**：spec=完整性/可行性/一致性/可验证性/遗漏/风险；plan=步骤合理性/依赖与顺序/风险与回退/可验证性/资源估计；代码=正确性/性能/安全/可维护性/契约一致性；文档=准确性/完整性/清晰度/一致性；设计=可行性/一致性/边界情况/可维护性/风险；通用兜底=完整性/一致性/可行性/风险。

**verify 补充**：代码按需跑测试复现（见 verify 节）；非代码与上下文/源材料交叉验证。

## description 方向聚焦（--for）

若提供 `--for <desc>`：

- **角度聚焦**：从目标物类型角度库按 desc 相关性选最相关角度（数量由 effort 决定），desc 注入各 review subagent prompt。
- **全流程约束**：sweep/critic 也聚焦 desc，与 desc 无关的 gap 不产出或降权；critic 在 --for 下对 desc 相关角度子集做覆盖度。
- **verify 相关性**：与 desc 无关的 finding 降权或驳回，不进 confirmed。

## effort

| effort | review | verify（谁 · 策略） | sweep | critic | 报告 |
|---|---|---|---|---|---|
| low | 主 agent 1-2 角度 | 主 agent · refute-by-default | — | — | 简短过程 |
| medium | 2-3 角度精选 | 主 agent · refute-by-default | — | — | 简短过程 |
| high | 4-6 角度 | 1 verifier/finding · recall | 条件触发+收尾 | — | 结构化混合 |
| xhigh | 6-8 角度 | 1 verifier/finding · recall | 每轮+收尾 | ✓ | 结构化混合 |
| max | 8+ 角度 | 2-3 投票/finding · recall | 每轮+收尾 | ✓ | 结构化混合 |

## 核心循环

最多 `times` 轮，每轮：

1. **Review** — 按 effort 派 N 个不同角度 subagent 挑刺，产出 findings（带角度标签）。有 `--for` 则角度按 desc 聚焦。
2. **[critic]** — 仅 xhigh/max，review 后。找漏掉的角度/场景，产出进 verify 池。
3. **Verify** — 逐条 3 态判定 review+critic findings，`CONFIRMED`/`PLAUSIBLE`/`REFUTED`，**只判定不产新 finding**。
4. **[Sweep → Verify-sweep]** — 仅 high+（high：review 0 新 confirmed 时触发收敛门；xhigh/max：每轮）。产出过 verify 后入 confirmed。
5. **Modify** — 主 agent 按 confirmed 清单原地改。
6. **轮间补充点** — 声明本轮已改，用户可补上下文/约束，不补则继续。

## 迭代记忆

注入 review/verify/sweep/critic subagent：

```
【迭代记忆 - 第 N 轮】
迭代目的：<desc，若提供>
已解决（上轮已改，确认仍已修；若回归了当新 finding 报）：
- <finding 摘要>
已驳回（误报或有意设计；若驳回理由不再成立可重新提）：
- <finding 摘要> | 理由：<用户约束或验证理由>
用户补充约束：
- <用户在轮间补充点提供的上下文>
```

**轮间补充点**：每轮 modify 后声明"本轮已改 X，如需补充上下文/约束请提出，否则继续"。用户补充约束入记忆；与已改内容/已驳回理由/desc 冲突 → 暂停问用户。

## critic（仅 xhigh/max）

覆盖度审查，对齐目标物类型完整角度库，找漏掉的**角度/场景**（top-down）；sweep 找漏点（见 sweep 节）。

- 时机：review 后、verify 前。review 产出须带角度标签；critic 产出前主 agent 过滤与 review 已扫角度重叠者。
- 产出 finding 过 verify（同 review policy）。
- --for 下：对 desc 相关角度子集做覆盖度。
- 注入迭代记忆。

## verify

逐条判定，返回 `CONFIRMED`/`PLAUSIBLE`/`REFUTED` + 理由：

- **CONFIRMED**：确为真缺陷。
- **PLAUSIBLE**：机制真但触发不确定。
- **REFUTED**：事实上错或他处已防护。

要求：

- **只判定不产新 finding**。verify subagent 不提改法。
- 给 verifier diff+相关文件+finding，要求尝试反驳。
- **policy**：≤medium refute-by-default（只留 CONFIRMED）；≥high recall（留 CONFIRMED+PLAUSIBLE）。
- **subagent**：low/medium 主 agent；high/xhigh 每条 1 verifier；max 每条 2-3 不同视角投票，多数非 REFUTED 即 confirm，否则归 PLAUSIBLE。
- 若有 desc：先按相关性筛，与 desc 无关的 finding 降权或驳回。
- 代码类 verify：finding 涉及具体输入/状态且可构造最小复现用例时跑测试；纯设计层面不跑。

## sweep

仅 high+。finder（不是 verify），带已验证清单，对齐目标物文本，找 review 漏掉的具体缺陷。

- **触发**：
  - **收敛门**：某轮 review 0 新 confirmed 时（轮内）。产出过 verify（同 review policy）→ confirmed → 可 modify（计为本轮 modify）。
  - **收尾**：times 用尽后一次。主 agent 按 3 态判定——CONFIRMED/PLAUSIBLE → `sweep 未及`；REFUTED → 丢弃。不再 modify、不再 verify。
  - xhigh/max：每轮 sweep（替代收敛门，candidate 上限 4）+ 收尾。
- 空产出（0 candidate）→ 0 verify；无新 gap 返回空，不凑数。
- 上限 8 条 candidate（xhigh/max 每轮 4）。
- 注入迭代记忆。

## modify

主 agent 按 confirmed 清单原地改（subagent 不提改法），处理 findings 间交互。

- **重大不确定决策**暂停问用户——判据：同一 finding 的 ≥2 种改法导致目标物对外行为/契约不同（仅措辞/实现路径不同不算）；或涉及用户在轮间补充点声明的约束。
- **代码类 modify 后**跑测试/lint/typecheck；无测试/lint 可跑则跳过、主 agent 静态重读改动段落兜底并记日志"无自动回归"；有测试则失败重试一次，仍失败回退该改动 + 进 residual(`确认但超范围`) + 可停下问用户。
- **非代码 modify 后**重读改动段+直接引用段，查新矛盾/已解决回归。
- **PLAUSIBLE（recall 档）**：非代码→modify；代码→residual(`PLAUSIBLE-code`)。

## 收敛与停止

- **真收敛**：某轮 0 新 confirmed 且该轮 sweep 0 gap（high+；low/medium 无 sweep，0 新即真收敛）→ 停。
- **状态机（high+）**：review 0 新 confirmed → 触发收敛门 sweep（轮内）→ sweep 0 gap → 真收敛停；sweep 有 gap → verify+modify → 下一轮（times 未满）或进 residual（times 满）。
- **"0 新 confirmed"** = 不在 已解决/已驳回 记忆里的 confirmed finding。
- **首轮 0 新 confirmed**（含全 REFUTED）：仍走收敛门 sweep（high+）；sweep 亦空 → 单轮收敛。
- **times=1 末轮**：review 0 新 → 收敛门 sweep 产出过 verify 后 modify → 再跑收尾 sweep 进 residual。
- **times 用尽**：跑满 times 轮后停；收尾 sweep 产出进 residual，不再 modify。
- sweep 每轮都找新 gap → 跑满 times 停。

## 报告

### 每轮日志

```
第 N 轮（effort=high）
- review：6 角度，findings 12 条
- verify：confirmed 7，驳回 5（误报 3 / 有意设计 2）
- sweep：收敛门，新增 gap 2 → verify → confirmed 1 / 驳回 1
- modify：改 8 处
- 记忆新增：已解决 8 / 已驳回 6
```

### 最终报告

- **low/medium**：简短过程总结（confirmed 清单 + 本轮改动摘要）。
- **high+ 结构化混合**：
  - **已修**：CONFIRMED（非代码含 PLAUSIBLE）且改掉的，带摘要 + 改了什么。
  - **残留**：`PLAUSIBLE-code` / `确认但超范围` / `sweep 未及`。
  - **驳回**：`误报(REFUTED)` / `用户约束` / `有意设计`，带理由。
  - **收敛状态**：轮数 + 停因（真收敛 / 跑满 times / 单轮收敛）。
  - **改动摘要**：累计改动总览。

## 走查示例

### 示例 1：`/refine spec.md 2 high`（spec，非代码路径）

**第 1 轮**：Review 6 角度产出 N 条 finding → verify 留 5 confirmed → modify。用户轮间补充「留存 90 天合规」→ 入记忆。

**第 2 轮（末轮，times=2）**：Review 注入记忆，0 新 confirmed → **触发收敛门 sweep**（关键转折）→ sweep 找出 review 漏的 2 条 gap：F7(CONFIRMED)、F8(PLAUSIBLE) → verify-sweep 确认 → modify（spec 非代码，PLAUSIBLE 也改）。times 用尽 → 收尾 sweep 0 gap → 无残留。

最终报告：已修 F1-F5+F7+F8（含 sweep 发现 2 条，F8 为 PLAUSIBLE）；驳回 F6（误报）；用户约束遵守。

> `--for` 时角度按 desc 聚焦、无关 finding 驳回，见 description 方向聚焦节。

### 示例 2：`/refine service.py 2 high`（代码路径）

- verify：F1(CONFIRMED) + F2(PLAUSIBLE，疑似竞态)。
- modify：F1 改；F2 代码 → 进 residual(`PLAUSIBLE-code`)，不硬改。
- modify 后：跑测试/lint；F1 改动若测试失败 → 重试一次，仍失败回退 + 进 residual(`确认但超范围`)。
- 报告残留：`PLAUSIBLE-code: F2`（及可能的 `确认但超范围: F1`）。
