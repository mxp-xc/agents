# Web/API 安全参考资料

更新时间：2026-08-04

本文件只收录官方标准、官方项目和合法练习环境。链接内容可能更新，使用时以其当前版本为准。

## 建议阅读顺序

1. MDN：理解 HTTP、Cookie 和浏览器安全模型。
2. OWASP Top 10：建立漏洞分类概念。
3. PortSwigger Web Security Academy：在授权实验环境中完成专题练习。
4. OWASP WSTG：学习完整测试流程。
5. OWASP API Security Top 10：学习 API 风险。
6. OWASP ASVS：把漏洞检查转为可验收的安全控制。
7. IETF/OIDC 标准：深入认证、OAuth 和 JWT。
8. NIST、CVSS、CWE：完善测试计划、定级和报告。

## HTTP 与浏览器基础

### MDN HTTP

https://developer.mozilla.org/en-US/docs/Web/HTTP

用于学习 HTTP 方法、状态码、Header、缓存、认证和内容协商。

### Cookie

https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies

重点关注 `Secure`、`HttpOnly`、`SameSite`、Domain、Path 和生命周期。

### Same-origin policy

https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy

理解 Origin、浏览器跨域读取限制以及 CORS 的前置知识。

### CORS

https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

重点区分简单请求、预检请求、凭据请求，以及“请求能够发送”和“响应能够被浏览器读取”。

### Content Security Policy

https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP

学习 CSP 指令、Nonce、Hash 和严格 CSP。CSP 是缓解措施，不是输入处理的替代品。

## OWASP 核心资料

### OWASP Top 10

https://owasp.org/www-project-top-ten/

用于建立常见 Web 风险分类，适合初学和管理沟通，但不能替代完整测试清单。

对应 skill：

- `performing-web-application-penetration-test`
- `testing-for-broken-access-control`
- 各类 SQLi、XSS、SSRF 和配置测试 skill

### OWASP Web Security Testing Guide

项目主页：

https://owasp.org/www-project-web-security-testing-guide/

稳定版 v4.2：

https://owasp.org/www-project-web-security-testing-guide/v42/

用途：

- 覆盖信息收集、配置、认证、授权、Session 和业务逻辑。
- 可作为测试计划和报告目录。
- OWASP 正在开发 5.0，引用测试编号时应注明版本。

对应 skill：

- `performing-web-application-penetration-test`
- `testing-api-authentication-weaknesses`
- `testing-for-business-logic-vulnerabilities`

### OWASP Application Security Verification Standard

项目主页：

https://owasp.org/www-project-application-security-verification-standard/

官方仓库：

https://github.com/OWASP/ASVS

当前稳定版为 ASVS 5.0.0。它用于把“发现漏洞”转成可验证的安全控制要求，适合开发验收、安全评审和修复复测。

### OWASP API Security Top 10

项目主页：

https://owasp.org/API-Security/

2023 版目录：

https://owasp.org/API-Security/editions/2023/en/0x11-t10/

重点包括 BOLA、Broken Authentication、BOPLA、资源消耗、BFLA、SSRF、配置错误和 API Inventory。

对应 skill：

- `conducting-api-security-testing`
- `testing-api-security-with-owasp-top-10`
- `testing-api-for-broken-object-level-authorization`
- `exploiting-broken-function-level-authorization`

## OWASP Cheat Sheet

总目录：

https://cheatsheetseries.owasp.org/

重点专题：

- [Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

这些资料适合回答“应该如何修复”和“正确实现应该是什么样”，不要只从攻击角度学习。

## OAuth、OIDC 与 JWT

### OAuth 2.0 Security Best Current Practice

RFC 9700：

https://datatracker.ietf.org/doc/rfc9700/

用于学习 redirect URI、PKCE、Token 泄漏、刷新 Token 和不安全授权流程，对应 `testing-oauth2-implementation-flaws`。

### JWT Best Current Practices

RFC 8725：

https://datatracker.ietf.org/doc/html/rfc8725

用于学习算法、Issuer、Audience、Token 类型和密钥校验，对应 `testing-jwt-token-security`。

### OpenID Connect Core

https://openid.net/specs/openid-connect-core-1_0.html

用于区分 OAuth 授权和 OIDC 身份认证，并理解 ID Token、UserInfo、Nonce、Issuer 和 Audience。

## 合法练习环境

以下目标专门用于学习。不要把相同测试方法直接用于陌生互联网网站。

### PortSwigger Web Security Academy

https://portswigger.net/web-security

免费在线实验，覆盖 SQLi、XSS、CSRF、SSRF、认证、授权、OAuth、JWT、API 和业务逻辑。建议作为主线练习平台。

### OWASP Juice Shop

https://owasp.org/www-project-juice-shop/

故意包含漏洞的现代 Web 应用，适合本地部署和综合练习。

### OWASP WebGoat

https://owasp.org/www-project-webgoat/

以课程形式解释漏洞原理和防护方法，适合理解根因。

### OWASP crAPI

https://owasp.org/www-project-crapi/

故意存在漏洞的 API/microservice 应用，重点练习 BOLA、认证、资源消耗和 API 业务逻辑。

## 测试工具官方文档

### Burp Suite

https://portswigger.net/burp/documentation

优先学习 Proxy、HTTP history、Repeater、Scope、Session handling 和扫描结果人工验证。

### OWASP ZAP

https://www.zaproxy.org/docs/

用于被动扫描、代理分析和本地靶场自动化辅助测试。不要把主动扫描指向未授权目标。

## 爬虫与自动采集

普通内容采集与渗透测试是不同任务。爬虫应单独考虑站点条款、隐私、版权、负载和访问控制。

### Robots Exclusion Protocol

RFC 9309：

https://www.rfc-editor.org/rfc/rfc9309

`robots.txt` 是爬虫行为规范，不是访问授权机制。未禁止抓取也不代表可以绕过登录、付费墙或技术控制。

### Scrapy

https://docs.scrapy.org/en/latest/

重点学习请求调度、去重、限速、重试、并发控制、`robots.txt` 和数据字段校验。

## 测试计划与报告

### NIST SP 800-115

https://csrc.nist.gov/pubs/sp/800/115/final

用于规划安全测试、定义 Rules of Engagement、组织证据和报告。

### CVSS 4.0

https://www.first.org/cvss/v4.0/

用于描述漏洞技术严重程度。CVSS 不是业务风险的全部，还要记录数据、权限和业务影响。

### CWE

https://cwe.mitre.org/

用于以统一编号描述弱点根因。报告中可同时记录 CWE、OWASP 分类和受影响控制。

## 学习成果检查

完成一个主题后，应能回答：

1. 漏洞产生的根因是什么？
2. 哪些前置条件必须成立？
3. 如何在测试账号和测试数据内安全验证？
4. 哪些证据足以证明影响，而不需要扩大访问？
5. 应如何在服务端修复？
6. 如何编写回归测试防止复发？
7. 对应 OWASP、ASVS、CWE 或 RFC 的哪一项？
