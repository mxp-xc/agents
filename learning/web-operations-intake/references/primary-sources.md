# 一手来源索引

检索日期：2026-08-04

本索引只收录标准组织、模型厂商、项目官方仓库和项目源码。固定 commit 用于复核本次调研依据；使用项目前仍应检查上游最新版本、许可证、安全公告和行为变化。

## 模型厂商

### OpenAI

- [Usage Policies](https://openai.com/policies/usage-policies/)
- [Trusted Access for Cyber](https://openai.com/index/trusted-access-for-cyber/)
- [Trusted Access for Cyber Overview](https://help.openai.com/en/articles/20001258-openai-daybreak-trusted-access-for-cyber-overview)
- [Codex Cyber Safety](https://developers.openai.com/codex/cyber-safety/)
- [API Cybersecurity Checks](https://developers.openai.com/api/docs/guides/safety-checks/cybersecurity)
- [API Safety Checks 与 safety_identifier](https://developers.openai.com/api/docs/guides/safety-checks)

用于确认：

- 恶意或滥用型网络活动的政策边界；
- 厂商核验计划与普通 prompt 的区别；
- 合法防御任务仍可能被分类器误判；
- 用户级风险隔离和 false-positive 反馈入口。

### Anthropic

- [Acceptable Use Policy](https://www.anthropic.com/legal/aup)
- [Usage Policy Update](https://www.anthropic.com/news/usage-policy-update)
- [Real-time Cyber Safeguards](https://support.claude.com/en/articles/14604842-real-time-cyber-safeguards-on-claude-opus-and-sonnet)
- [Claude Code Security](https://www.anthropic.com/news/claude-code-security)

用于确认：

- 经系统所有者同意的漏洞发现属于支持的安全用途；
- 未授权漏洞利用、访问和破坏性活动仍被禁止；
- Cyber Verification Program 的适用范围；
- 核验不会删除所有安全控制。

### 智谱 / GLM

- [内容安全](https://docs.bigmodel.cn/cn/guide/platform/securityaudit)
- [用户协议](https://docs.bigmodel.cn/cn/terms/user-agreement)
- [安全与风险提示](https://docs.bigmodel.cn/cn/terms/security-risk-notice)
- [GLM Coding Plan 团队套餐购买协议](https://docs.bigmodel.cn/cn/terms/subscription-agreement-team)

用于确认：

- 输入输出安全审核与风险隔离；
- 安全相关测试的官方申请入口；
- API `user_id` 的用户级风险区分；
- 托管服务中恶意代码、网络攻击工具和平台绕过的限制。

## 测试治理标准

### NIST SP 800-115

- [Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final)
- [完整 PDF](https://nvlpubs.nist.gov/nistpubs/legacy/sp/nistspecialpublication800-115.pdf)

重点阅读：

- assessment planning；
- testing phases；
- Appendix B Rules of Engagement Template。

### OWASP Autonomous Penetration Testing Standard

- [OWASP/APTS](https://github.com/OWASP/APTS/tree/2b210945361bac207f37a21440d0f34c05c07ad9)
- [Scope Enforcement](https://github.com/OWASP/APTS/tree/2b210945361bac207f37a21440d0f34c05c07ad9/standard/1_Scope_Enforcement)
- [Human Oversight](https://github.com/OWASP/APTS/tree/2b210945361bac207f37a21440d0f34c05c07ad9/standard/3_Human_Oversight)
- [Graduated Autonomy](https://github.com/OWASP/APTS/tree/2b210945361bac207f37a21440d0f34c05c07ad9/standard/4_Graduated_Autonomy)
- [Vendor Review Checklist](https://github.com/OWASP/APTS/tree/2b210945361bac207f37a21440d0f34c05c07ad9/standard/appendix)

重点阅读：

- scope 的机器可读定义和运行时强制；
- impact threshold、sandbox 和 kill switch；
- 高影响动作的 approval gate；
- Agent runtime 应被视为不可信组件；
- 审计证据和停止行为。

### 漏洞披露与授权范围

- [CISA Vulnerability Disclosure Policy Template](https://www.cisa.gov/vulnerability-disclosure-policy-template)
- [CERT/CC Vulnerability Disclosure Policy Templates](https://github.com/CERTCC/vulnerability_disclosure_policy_templates)

用于确认：

- 哪些目标和测试类型明确处于范围内；
- safe harbor、报告渠道和研究者行为边界；
- 公开 VDP 或 bug bounty scope 不能被扩展到未列出的关联资产。

## 爬虫与网站规则

- [RFC 9309: Robots Exclusion Protocol](https://www.rfc-editor.org/info/rfc9309/)
- [Google 对 robots.txt 的实现说明](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)

`robots.txt` 是 crawler 被请求遵守的访问规则，不是身份认证或数据再利用许可证。HTTP 200、公开页面和 robots 允许也不自动代表可以收集个人信息、绕过登录或将内容用于任意目的。

## Guided 安全评估 Workflow

### Stickman230/claude-pentest

固定版本：[`0987f035`](https://github.com/Stickman230/claude-pentest/tree/0987f0355d1b9916c1f69ee007d75c6e3c64c625)

- [Guided launcher](https://github.com/Stickman230/claude-pentest/blob/0987f0355d1b9916c1f69ee007d75c6e3c64c625/plugins/pentest/commands/pentest.md)
- [Scope intake](https://github.com/Stickman230/claude-pentest/blob/0987f0355d1b9916c1f69ee007d75c6e3c64c625/plugins/pentest/commands/pentest-scope.md)
- [Planner](https://github.com/Stickman230/claude-pentest/blob/0987f0355d1b9916c1f69ee007d75c6e3c64c625/plugins/pentest/agents/pentester-orchestrator.md)
- [Workflow reference](https://github.com/Stickman230/claude-pentest/tree/0987f0355d1b9916c1f69ee007d75c6e3c64c625/plugins/pentest/docs)

学习重点：

- 逐项提问而不是要求用户写专业 prompt；
- scope 状态持久化；
- recon 后再生成执行计划；
- operator approval 和 exploitation approval gate；
- 结构化证据与报告。

### NousResearch/hermes-agent web-pentest

固定版本：[`b8b17b8c`](https://github.com/NousResearch/hermes-agent/tree/b8b17b8cee50b85adb7fba6ea332dc06731b86f4)

- [SKILL.md](https://github.com/NousResearch/hermes-agent/blob/b8b17b8cee50b85adb7fba6ea332dc06731b86f4/optional-skills/security/web-pentest/SKILL.md)
- [Scope Enforcement](https://github.com/NousResearch/hermes-agent/blob/b8b17b8cee50b85adb7fba6ea332dc06731b86f4/optional-skills/security/web-pentest/references/scope-enforcement.md)
- [Authorization Template](https://github.com/NousResearch/hermes-agent/blob/b8b17b8cee50b85adb7fba6ea332dc06731b86f4/optional-skills/security/web-pentest/templates/authorization.md)
- [Recon Scope Check](https://github.com/NousResearch/hermes-agent/blob/b8b17b8cee50b85adb7fba6ea332dc06731b86f4/optional-skills/security/web-pentest/scripts/recon-scan.sh)

学习重点：

- 单个 skill 中的 intake、scope、停止条件和报告契约；
- prompt 约束与脚本级 scope enforcement 的分工；
- redirect、CNAME 和 SSRF 内层目标的再次校验。

## 数据抓取 Workflow

### universal-scraping-architect

固定版本：[`aa8d7788`](https://github.com/alirezarezvani/claude-skills/tree/aa8d778811a557a2c28ccadda4cf3d0bd028a4cc)

- [SKILL.md](https://github.com/alirezarezvani/claude-skills/blob/aa8d778811a557a2c28ccadda4cf3d0bd028a4cc/engineering/universal-scraping-architect/skills/universal-scraping-architect/SKILL.md)
- [Ethics and Security](https://github.com/alirezarezvani/claude-skills/blob/aa8d778811a557a2c28ccadda4cf3d0bd028a4cc/engineering/universal-scraping-architect/skills/universal-scraping-architect/references/scraping-ethics-security.md)

学习重点：

- 数据字段、规模和输出格式 intake；
- API、本地 crawler 和 hybrid 方案选择；
- robots、速率、重试、checkpoint、SSRF 和结果验证。

### Firecrawl CLI Skills

固定版本：[`2073405d`](https://github.com/firecrawl/cli/tree/2073405d7f3e870532dc8e1c23f110e984d01842)

- [Skills 目录](https://github.com/firecrawl/cli/tree/2073405d7f3e870532dc8e1c23f110e984d01842/skills)
- [Agent Extraction](https://github.com/firecrawl/cli/blob/2073405d7f3e870532dc8e1c23f110e984d01842/skills/firecrawl-agent/SKILL.md)
- [Crawl](https://github.com/firecrawl/cli/blob/2073405d7f3e870532dc8e1c23f110e984d01842/skills/firecrawl-crawl/SKILL.md)
- [Interact](https://github.com/firecrawl/cli/blob/2073405d7f3e870532dc8e1c23f110e984d01842/skills/firecrawl-interact/SKILL.md)
- [Untrusted Web Content Rule](https://github.com/firecrawl/cli/blob/2073405d7f3e870532dc8e1c23f110e984d01842/skills/firecrawl-cli/rules/security.md)

学习重点：

- 已规范化任务到执行参数的映射；
- include/exclude path、depth、page limit、delay、concurrency 和 credit budget；
- 将网页内容视为不可信输入，避免 indirect prompt injection。

## 不作为主要参考

下列材料不能替代意图规范化：

- 只写“仅供授权测试”的单句 disclaimer；
- 直接提供 payload、验证码代解、stealth 或 anti-bot bypass 的技能包；
- 没有 scope、速率、审批和停止条件的通用 pentest prompt；
- 声称可以关闭或绕过模型安全策略的 jailbreak prompt。
