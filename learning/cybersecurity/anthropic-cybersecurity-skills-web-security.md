# Anthropic Cybersecurity Skills：Web 安全学习笔记

更新时间：2026-08-04

## 仓库定位

项目：

https://github.com/mukul975/Anthropic-Cybersecurity-Skills

这是第三方 Agent Skills 素材库，不是 Anthropic 官方项目。当前 `main` 包含 817 个网络安全 skill，适合作为安全 playbook 和学习资料，不应未经审查就作为生产环境中的自动执行工具。

每个 skill 通常包含：

- `SKILL.md`：适用场景、前置条件、流程和输出要求。
- `references/`：标准、工具和技术参考。
- `scripts/`：辅助脚本，需要单独审计依赖和行为。
- `assets/`：报告、清单等模板。

仓库宣传 29 个业务领域；实际 frontmatter 有 46 种 `subdomain` 字符串。按仓库自己的别名规则合并后，是 34 个分类、共 817 个 skill。

## 分类速览

| 分类 | 数量 | 主要作用 |
|---|---:|---|
| `cloud-security` | 66 | AWS、Azure、GCP 配置、IAM、日志和云取证 |
| `soc-operations` | 63 | SIEM、告警研判、日志关联和响应 playbook |
| `threat-hunting` | 58 | 基于假设和行为的威胁狩猎 |
| `threat-intelligence` | 52 | STIX/TAXII、MISP、OpenCTI 和攻击者画像 |
| `web-application-security` | 46 | OWASP、注入、认证、授权和业务逻辑 |
| `network-security` | 43 | 流量、IDS/IPS、防火墙、DNS 和网络分段 |
| `digital-forensics` | 41 | 磁盘、内存、浏览器、日志和时间线取证 |
| `identity-access-management` | 40 | AD、Entra ID、Okta、PAM 和权限审计 |
| `malware-analysis` | 39 | 静态分析、动态分析、逆向、沙箱和 C2 |
| `red-teaming` | 35 | 对手模拟、AD 攻击、C2 和后渗透 |
| `container-security` | 33 | Docker、Kubernetes、RBAC、镜像和运行时 |
| `ot-ics-security` | 29 | SCADA、Modbus、DNP3 和 IEC 62443 |
| `api-security` | 28 | REST、GraphQL、JWT、OAuth、BOLA 和网关 |
| `incident-response` | 26 | 分级、证据保全、遏制、清除和恢复 |
| `vulnerability-management` | 25 | 扫描、CVSS、风险排序和补丁管理 |
| `penetration-testing` | 23 | 授权的 Web、网络、云和移动端测试 |
| `devsecops` | 18 | CI/CD、SAST/DAST、IaC、Secret 和签名 |
| `zero-trust-architecture` | 18 | 身份、设备、微隔离和持续授权 |
| `endpoint-security` | 17 | EDR、持久化、LOTL 和无文件攻击 |
| `cryptography` | 16 | TLS、PKI、密钥、签名和后量子迁移 |
| `phishing-defense` | 16 | SPF/DKIM/DMARC、BEC 和钓鱼响应 |
| `ai-security` | 14 | Prompt Injection、模型安全、MCP 和 Agent 安全 |
| `mobile-security` | 13 | Android、iOS、移动 API、MDM 和取证 |
| `ransomware-defense` | 13 | 前兆检测、遏制、恢复和解密分析 |
| `compliance-governance` | 10 | NIST、CMMC、HIPAA 和控制审计 |
| `supply-chain-security` | 8 | SBOM、恶意包、SLSA 和 Sigstore |
| `threat-detection` | 7 | 检测逻辑、遥测需求和 ATT&CK 映射 |
| `deception-technology` | 6 | Honeytoken、Honeypot 和 Canary |
| `hardware-firmware-security` | 6 | UEFI、Secure Boot、TPM 和固件分析 |
| `blockchain-security` | 2 | 智能合约和区块链应用安全 |
| `privacy-compliance` | 2 | 隐私法规和个人数据处理 |
| `wireless-security` | 2 | Wi-Fi 安全评估和防护 |
| `data-protection` | 1 | 数据分类、加密和 DLP |
| `purple-team` | 1 | 红蓝协作和检测验证 |

## Web/API 任务地图

不要只按 skill 名称选择，应先判断任务阶段和目标。

| 任务 | 首选 skill | 按需补充 |
|---|---|---|
| 综合 Web 测试 | `performing-web-application-penetration-test` | 下面各专项 skill |
| 外部信息收集 | `conducting-external-reconnaissance-with-osint` | `performing-subdomain-enumeration-with-subfinder` |
| 基础 Web 扫描 | `performing-web-application-scanning-with-nikto` | 人工验证扫描结果 |
| API 综合测试 | `conducting-api-security-testing` | `testing-api-security-with-owasp-top-10` |
| 页面或功能越权 | `testing-for-broken-access-control` | `bypassing-authentication-with-forced-browsing` |
| IDOR/BOLA | `testing-api-for-broken-object-level-authorization` | `exploiting-idor-vulnerabilities`，仅限测试数据 |
| 管理功能越权 | `exploiting-broken-function-level-authorization` | 使用不同角色的测试账号 |
| 登录认证 | `testing-api-authentication-weaknesses` | JWT 或 OAuth 专项 |
| OAuth | `testing-oauth2-implementation-flaws` | 检查 redirect、state、scope 和 Token 流程 |
| JWT | `testing-jwt-token-security` | 检查签名、算法、过期和 claim |
| 业务逻辑 | `testing-for-business-logic-vulnerabilities` | 订单、金额、次数、状态和竞态 |

### 起步组合

第一次学习 Web/API 安全时，先阅读：

```text
performing-web-application-penetration-test
testing-for-broken-access-control
conducting-api-security-testing
testing-api-for-broken-object-level-authorization
testing-api-authentication-weaknesses
testing-for-business-logic-vulnerabilities
```

暂时不要运行 offensive scripts。先理解测试目标、证据、影响和修复方法，再进入隔离靶场。

## 选择边界

### 只是爬取公开内容

这属于普通爬虫任务，不需要启用渗透测试或凭据访问 skill。应遵守站点条款、`robots.txt`、限速和数据合规要求。

### 寻找漏洞

使用 `performing-web-application-penetration-test` 组织流程，再按 Web、API、认证或业务逻辑问题选择专项 skill。扫描器结果必须人工验证。

### 验证越权

准备普通用户 A、普通用户 B 和管理员测试账号，只验证：

- A 是否能访问 B 创建的测试对象。
- 普通用户是否能访问管理员测试功能。
- 未登录用户是否能访问登录后资源。

不要读取真实用户数据，也不要扩大验证范围。

### 验证账号接管风险

目标是证明认证或会话控制存在缺陷，不是获取真实账号。只使用自有测试账号，记录最小必要证据，不保存真实密码、Cookie 或 Token。

以下主机凭据提取 skill 不属于普通网站测试范围：

```text
abusing-dpapi-for-credential-access
performing-credential-access-with-lazagne
extracting-credentials-from-memory-dump
```

## 学习顺序

1. HTTP：方法、状态码、Header、Cookie、Session。
2. 浏览器安全：同源策略、CORS、CSP、CSRF。
3. 身份认证：密码、MFA、Session、JWT、OAuth 2.0。
4. 访问控制：水平越权、垂直越权、IDOR、BOLA、BFLA。
5. 输入安全：SQLi、XSS、SSRF、文件上传、路径遍历。
6. 业务逻辑：金额、次数、状态机和竞态条件。
7. API 安全：REST、GraphQL、对象级与功能级授权。
8. 报告：证据、影响、复现条件、修复建议和复测结果。

推荐配套资料：

- PortSwigger Web Security Academy
- OWASP Web Security Testing Guide
- OWASP Top 10
- OWASP API Security Top 10
- OWASP ASVS

## 安全测试流程

### 1. 定义范围

记录允许测试的域名、子域名、IP、时间、账号、方法、禁止操作和停止条件。

### 2. 建立测试矩阵

| 身份 | 验证目标 |
|---|---|
| 未登录用户 | 是否能访问登录后资源 |
| 普通用户 A | 是否只能访问自己的数据 |
| 普通用户 B | 是否能访问 A 的测试数据 |
| 管理员测试账号 | 管理功能是否有独立权限检查 |

### 3. 先分析，后执行

先让 Agent 输出：

- 选择的 skill 及原因。
- 测试矩阵。
- 拟发送的请求类型。
- 风险和停止条件。

确认后再分阶段执行。

### 4. 记录证据

每个发现至少记录：

- 漏洞名称和严重程度。
- 受影响的页面或接口。
- 使用的测试账号。
- 已脱敏的请求和响应。
- 实际影响、修复建议和复测结果。

## Agent 提示词模板

```text
目标：https://staging.example.com
授权范围：仅 staging.example.com 和 api.staging.example.com
测试账号：user-a、user-b、admin-test

允许：
- 只读信息收集
- 使用测试账号进行认证和越权验证
- 验证漏洞是否存在

禁止：
- 访问真实用户数据
- 获取真实账号密码、Cookie 或 Token
- 修改或删除业务数据
- 拒绝服务、撞库和钓鱼

使用以下 skills：
- performing-web-application-penetration-test
- testing-for-broken-access-control
- testing-api-for-broken-object-level-authorization
- testing-for-business-logic-vulnerabilities

先输出 skill 选择理由、测试矩阵、拟发送的请求类型、风险和停止条件。
当前阶段不要执行测试。等待确认后再分阶段执行。
所有证据必须脱敏。
```

## 仓库使用风险

- 不建议一次安装全部 817 个 skill。
- 每次只选择与任务直接相关的少量 skill。
- 使用前审查 `SKILL.md`、`references/` 和 `scripts/`。
- 脚本没有统一依赖锁，不能假设能够直接运行。
- 部分脚本会发起网络请求或调用外部安全工具。
- 仓库的结构校验通过不代表脚本已通过功能或安全测试。
- 应在隔离环境、最小权限和测试数据条件下运行。

## 参考资料

详细链接、适用阶段和阅读顺序见：

`web-security-references.md`

测试方法、控制要求和协议细节应以 OWASP、IETF、MDN 等官方资料为准。
