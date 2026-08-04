# 网站安全评估与数据抓取的意图规范化

## 目标

用户可能只会用口语描述任务，例如：

- “找出这个网站可能的漏洞，并给出路径和影响范围。”
- “抓取某个网站的数据，遇到验证码或滑块时继续处理。”

本调研关注的不是扫描器本身，而是能否用 prompt、workflow 或 Agent Skill 自动完成以下工作：

1. 判断用户实际想做的是安全评估还是数据抓取。
2. 只追问缺失的必要信息。
3. 将口语请求整理成边界明确、低歧义的任务说明。
4. 在执行前展示计划并取得确认。
5. 将高影响动作、越界、异常响应和 CAPTCHA 分流处理。
6. 输出证据、影响范围、复现信息和修复或数据结果。

## 核心结论

截至 2026-08-04，没有发现一个可以直接安装并同时满足下列条件的 GitHub 项目：

- 同时覆盖网站漏洞评估与数据抓取；
- 自动补齐 scope、排除项、速率、停止条件和审批点；
- 明确区分自有测试环境、正常第三方业务流程和第三方反自动化规避；
- 可直接跨 GPT、Claude、GLM 使用；
- 保证上游模型不误判或不拒答。

现有项目可以显著减少表达歧义，但不能改变模型服务商的账号信任状态或服务端安全策略。最可行的组合是：

```text
自然语言请求
→ guided intake
→ 结构化 engagement 或 crawl spec
→ 用户确认
→ 受限执行器
→ 证据、停止条件和报告
```

## 推荐项目

### 网站漏洞评估

#### Stickman230/claude-pentest

仓库：<https://github.com/Stickman230/claude-pentest>

这是最接近“用户只描述目标，workflow 负责整理专业任务”的现成项目。其 `/pentest:pentest` 和 `/pentest:pentest-scope` 会逐项收集：

- target；
- engagement name；
- out-of-scope 路径、域名或服务；
- 测试账号或 token；
- time budget；
- Light、Medium、Deep 或 Full 测试深度；
- 交付格式。

随后执行 pre-flight、recon、测试计划生成和 operator approval。Executor 从安全探测升级到 active exploitation 前还有第二个确认点。Scope 会写入 `.pentest-scope.json`，可在后续会话复用。

适用：

- Claude Code 中的 guided 网站安全评估；
- 学习 intake、scope persistence、计划审批和分阶段执行设计。

局限：

- Claude Code plugin 专用；
- `auth` 主要表示测试凭据，不等于可验证的授权；
- 包含主动利用、认证测试和 post-exploitation 能力，具体请求仍可能触发模型策略；
- 没有覆盖普通数据抓取的 intake。

一手文件：

- <https://github.com/Stickman230/claude-pentest/blob/main/plugins/pentest/commands/pentest.md>
- <https://github.com/Stickman230/claude-pentest/blob/main/plugins/pentest/commands/pentest-scope.md>
- <https://github.com/Stickman230/claude-pentest/blob/main/plugins/pentest/agents/pentester-orchestrator.md>

#### NousResearch/hermes-agent web-pentest

入口：<https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/web-pentest/SKILL.md>

这是边界最完整、最适合移植的单个 `SKILL.md`。它包含：

- 授权与目标确认话术；
- hostname 和 CIDR allowlist；
- redirect、CNAME 和 SSRF 内层 URL 的二次 scope 校验；
- 默认请求间隔；
- destructive payload 的逐次审批；
- 429/503、生产数据影响、越界和撤销授权时的停止条件；
- request log、evidence、findings 和 report 目录约定。

配套脚本不会只相信 prompt：缺少 authorization、scope 文件或目标不在 allowlist 时会退出。

适用：

- 学习单 skill 的完整安全评估 workflow；
- 作为未来跨 Agent Skill intake 的基础模板。

局限：

- 原版要求书面授权确认；
- 授权仍是用户声明，不验证域名控制权；
- 主要面向 Hermes；
- 不处理普通数据抓取和 CAPTCHA。

一手文件：

- <https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/web-pentest/references/scope-enforcement.md>
- <https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/web-pentest/templates/authorization.md>
- <https://github.com/NousResearch/hermes-agent/blob/main/optional-skills/security/web-pentest/scripts/recon-scan.sh>

### 数据抓取

#### universal-scraping-architect

入口：<https://github.com/alirezarezvani/claude-skills/blob/main/engineering/universal-scraping-architect/skills/universal-scraping-architect/SKILL.md>

该 skill 会整理：

- 目标数据字段、格式和规模；
- 运行环境；
- Firecrawl、本地 Python 或 hybrid 方案；
- API quota 和 token budget；
- `robots.txt`；
- 请求速率、有限重试和 checkpoint；
- SSRF 与 crawl drift；
- 必填字段、去重和结果验证。

它优先使用官方 API、sitemap 或 data dump，并要求诚实的 `User-Agent`。如果 `robots.txt` 禁止目标路径，则停止并通知用户。

适用：

- 普通公开数据抓取的方案设计；
- 学习抓取伦理、范围、预算和质量验证。

局限：

- 不会完整追问网站 ToS、数据许可和个人信息用途；
- 没有 CAPTCHA 或 slider 的统一决策；
- 没有把 intake 结果固化成可确认的 crawl spec。

参考：

- <https://github.com/alirezarezvani/claude-skills/blob/main/engineering/universal-scraping-architect/skills/universal-scraping-architect/references/scraping-ethics-security.md>

#### Firecrawl CLI skills

入口：<https://github.com/firecrawl/cli/tree/main/skills>

Firecrawl skills 适合作为已经完成意图规范化后的执行层，能够表达：

- `include-paths` 和 `exclude-paths`；
- page limit 和 max depth；
- delay 和 max concurrency；
- 结构化数据 schema；
- credit budget；
- 登录、点击、填表、分页和 session。

它还要求把抓取结果视为不可信输入，避免网页内容通过 indirect prompt injection 改写 Agent 指令。

局限：

- 没有授权或 ToS intake；
- 没有个人数据用途确认；
- 没有 CAPTCHA、滑块和高风险交互审批；
- 不能单独解决用户表达不专业的问题。

## CAPTCHA 与滑块边界

GitHub 上存在调用代理、stealth browser 和验证码代解服务的 skills。它们主要负责执行，不负责判断用户意图，也不会让第三方反自动化规避自动变成合法任务。

通用 intake 应固定分为三条路径：

```text
自有或明确授权的测试环境
→ 使用供应商 test key、staging bypass 或专用测试账号

正常第三方业务流程
→ 暂停并请求真人完成 challenge，完成后继续

要求自动破解、代答或规避第三方 challenge
→ 不执行；改用官方 API、自动化白名单或合作接口
```

因此，不应把 CAPTCHA bypass skill 作为通用入口，也不应通过改写话术隐藏真实动作。

## 建议的通用 Intake

未来正式能力可以只负责将口语请求整理成统一 spec，不直接包含扫描器、payload 或 CAPTCHA solver：

```yaml
request_type: web_security_assessment | public_data_collection

target:
  urls: []
  relationship: owned | authorized_program | public_access

scope:
  include_hosts: []
  include_paths: []
  exclude_hosts: []
  exclude_paths: []

constraints:
  max_rps: 1
  max_pages: 100
  time_budget: ""
  authenticated: false

allowed_actions:
  - passive_fetch
  - safe_validation

prohibited_actions:
  - denial_of_service
  - destructive_write
  - real_user_data_access
  - persistence
  - captcha_or_slider_bypass

approval_required:
  - active_exploitation
  - authenticated_write

stop_conditions:
  - off_scope_redirect
  - HTTP_429_or_503_storm
  - unexpected_personal_data
  - production_impact

deliverables:
  - evidence
  - affected_paths
  - impact_scope
  - remediation_or_dataset
```

### 安全评估路由

```text
web_security_assessment
→ 补齐 scope、排除项、测试账号、预算和深度
→ 先生成 recon 与 safe-validation 计划
→ 用户确认
→ 高影响动作单独审批
→ 记录 evidence、affected paths、impact 和 remediation
```

### 数据抓取路由

```text
public_data_collection
→ 补齐字段、规模、路径、速率和用途
→ 检查 API、sitemap、robots 和数据许可
→ 生成 crawl spec
→ CAPTCHA 时按三条固定路径分流
→ 校验完整性、去重和输出格式
```

## 验证标准

将本调研转化为正式 skill 前，至少验证：

1. 只给出一句口语请求时，Agent 会逐项追问缺失信息，而不是假设 scope。
2. 最终会展示完整 spec，并要求用户确认。
3. redirect、CNAME、外链和新发现子域不会自动扩展 scope。
4. active exploitation、authenticated write 和生产数据访问不会自动执行。
5. 429、503、异常延迟、个人数据和生产影响会触发停止。
6. CAPTCHA 不会被含糊地改写为“继续访问”或“自动处理”。
7. 报告包含证据、影响范围、复现条件和修复建议，抓取结果包含字段验证与去重信息。
8. 在 GPT、Claude、GLM 上分别验证触发、追问和降级行为，不承诺跨模型完全一致。

## 当前状态

本目录仅保存学习材料，没有创建或安装任何正式 skill、agent、command、hook 或执行器。

## 配套参考

- [一手来源索引](references/primary-sources.md)
- [Intake 与执行边界检查表](references/intake-checklist.md)
- [AI 渗透测试工作流](../cybersecurity/ai-pentest-workflows.md)
- [AI 渗透测试参考资料](../cybersecurity/ai-pentest-references.md)
- [授权任务契约示例](../cybersecurity/templates/authorized-engagement.yaml)
- [Web 安全技能库学习笔记](../cybersecurity/anthropic-cybersecurity-skills-web-security.md)
- [Web 安全官方参考](../cybersecurity/web-security-references.md)
