# 目标仓库 `CODING_STANDARDS.md` 模板

执行 `ddd-architecture` 时，将以下模板裁剪并具体化为目标仓库根目录的 `CODING_STANDARDS.md`。该文件同时服务于实现阶段的规范对齐与 `code-review` 的 Standards 审查。

---

```markdown
# CODING_STANDARDS

> 本文档由 `ddd-architecture` 确立，是本仓库架构边界、编码规范与代码审查的唯一准绳。

## 1. 架构定位与演进阶段

- **当前运行阶段**：`<未上线早期开发 | 已上线运行中>`
- **DDD 复杂度梯度**：`<L1 轻量务实 DDD | L2 严格六边形/整洁 DDD>`
- **核心技术栈**：`<语言 / Web 框架 / ORM 或持久层 / 校验库 / 前端框架>`
- **业务与全局分工**：
  - `<业务模块或服务域，如 modules/<context-a> 或 services/<domain-a>>`：<一句话职责边界>
  - `<业务模块或服务域，如 modules/<context-b> 或 services/<domain-b>>`：<一句话职责边界>
  - `<带框架横切目录，如 config / filters / aop / exceptions/handler / persistence 或 core>`：<框架装配、横切拦截、异常协议映射与公共 IO/持久基建职责>
  - `<无框架公共区，如 types（enums/vo/dto）、utils、纯语义异常>`：<零框架共享枚举、值对象、通用传值 DTO、语义异常基类与通用工具职责>

## 2. 目录结构与依赖红线

```text
<粘贴本仓库实际包/目录树及每层/每个顶层目录一句话职责>
```

**强制依赖方向**：`interfaces → application → domain ← infrastructure`（轻量分层架构为 `api → services → repositories → db`）

- **严禁**：`domain`（或核心业务层）依赖 `interfaces`/`api`、`application`、`infrastructure`/`db` 或任何带框架横切目录（仅允许依赖标准库与无框架公共区，<另标明 L1 下允许的轻量注解白名单或 L2 零框架要求>）。
- **严禁**：无框架公共区（`types`、`utils`、纯语义异常根包等）反向依赖业务模块或带框架横切目录。
- **严禁**：`infrastructure` 反向引用 `interfaces`（包括控制器、请求/响应 DTO 与分页包装）。
- **严禁**：`interfaces` 绕过 `application` 直接调用写路径持久化实现或操作数据库实体。
- **跨上下文协作**：`modules/*` 间仅通过各自 `application` 公开门面或领域事件协作，禁止直接查询或修改其他上下文的内部持久化表/实体，且禁止单模块私有辅助代码流入全局目录。

## 3. 契约、领域建模与异常规范

- **接口契约（DTO）**：请求与响应独立建模（按类/文件清晰分离），禁止复用数据库实体直接对外暴露；输入格式校验在 `interfaces` 层声明式完成（如 `@Valid` / Pydantic / Zod）。
- **强类型状态与值对象**：业务状态流转必须由强类型枚举或值对象表达（含合法状态迁移判断），禁止在业务与持久化判断中硬编码裸字符串魔法值。
- **语义化异常**：`domain` 与 `infrastructure` 仅抛出语义明确的业务/领域异常（不含 HTTP 状态码）；协议状态码映射统一集中在全局异常处理器完成。
- **事务与读写分离**：写事务边界归属 `application` 层单一用例入口；列表筛选、分页与统计优先走只读查询通道并直接投影视图模型。
- **单文件与参数约束**：单文件建议不超过 `<如 350>` 行，公共方法/函数参数超过 `<如 4-5>` 个时封装为明确的 Command / Query / Value Object。

## 4. 横切基础设施入口

- **认证与上下文**：<标明统一的认证 Filter / Middleware / Dependency 入口及如何向应用层传递已认证操作者>
- **请求追踪与日志**：<标明 trace_id 串联与关键路径日志约定>
- **审计与幂等**：<标明审计落库及关键写操作幂等处理入口>

## 5. 自动化架构护栏与验证命令

每次提交或完成任务前，必须执行以下检查并确保全绿：

- **构建与类型检查**：`<mvn compile | bun run build | uv run mypy ...>`
- **业务测试与架构护栏测试**：`<mvn test / verify | bun run lint && bun run test | uv run lint-imports && uv run pytest>`
- **护栏覆盖说明**：<列明当前已接入的 ArchUnit / ESLint / dependency-cruiser / import-linter / 自定义导入检查文件位置>

## 6. 显式特例与 ADR 索引

- <如因历史兼容或离线受限存在暂时豁免项，在此写明豁免范围、理由与清理条件；无豁免写“当前无豁免”。>
- 相关决策记录见 `docs/adr/`，领域术语以 `GLOSSARY.md` 为准。
```
