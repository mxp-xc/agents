# 目标仓库 `docs/CODING_STANDARDS.md` 模板

在目标仓库创建或补齐 `docs/CODING_STANDARDS.md` 时使用以下模板。若目标仓库已有规范文档，保留其全部既有约定，仅补齐缺失章节。

---

````markdown
# CODING_STANDARDS

> 本仓库架构边界、编码规范与代码审查的唯一准绳（路径：`docs/CODING_STANDARDS.md`）。

## 1. 架构定位与模块分工

- **运行阶段**：`<未上线早期开发 | 已上线运行中>`
- **架构档位**：`<轻量务实分层 | L1 轻量务实 DDD | L2 严格整洁 DDD>`
- **核心技术栈**：`<语言 / Web 框架 / 持久层 / 校验库 / 前端框架>`

| 区域 | 目录路径 | 职责边界 |
| --- | --- | --- |
| **业务模块** | `<如 modules/orders 或 services/orders>` | `<一句话说明该域核心主表与业务职责>` |
| **业务模块** | `<如 modules/account 或 services/account>` | `<一句话说明该域核心主表与业务职责>` |
| **带框架横切区** | `<如 config, filters/middlewares, aop, exceptions/handler, persistence 或 core>` | 框架装配、鉴权/Trace 拦截、全局异常处理器、公共持久基建 |
| **无框架公共区** | `<如 types(enums/vo/dto), utils, exceptions 根包>` | 零框架共享枚举、值对象、`ApiResponse`、`BusinessException` 与 `ErrorCode`、纯工具 |

## 2. 目录结构与依赖红线

```text
<粘贴本仓库实际包/目录树，每个顶层目录附一句话职责>
```

```text
强制单向依赖：
  DDD 四层：   interfaces ──▶ application ──▶ domain ◀── infrastructure
  轻量分层：   api        ──▶ services    ──▶ repositories ──▶ db
```

- **`domain`（或核心业务层）零框架污染**：仅允许依赖标准库与无框架公共区（`types`、`utils`、`exceptions` 纯异常），严禁依赖 `interfaces`/`api`、`application`、`infrastructure`/`db` 或任何带框架横切目录。
- **无框架公共区零反向依赖**：`types`、`utils`、`exceptions` 根包严禁反向依赖业务模块或带框架横切目录。
- **持久层与接入层隔离**：`infrastructure`（或 `repositories`/`db`）严禁反向引用 `interfaces`/`api`（含控制器与请求/响应 DTO）；`interfaces`/`api` 严禁绕过应用层直接调用写侧持久化实现。
- **跨模块黑盒协作**：`modules/*` 之间仅通过对方 `application` 公开门面或领域事件协作，禁止直接查改其他模块的内部表、实体或仓储；单模块私有代码严禁放入全局 `types/` 或 `utils/`（禁用 `common/` 目录）。

## 3. 统一响应、通用异常与领域建模

```text
HTTP Request ──▶ Trace (写 X-Trace-Id 响应头 & MDC) ──▶ Auth (解析身份) ──▶ Controller (@Valid)
  ├── 正常 ──▶ HTTP 200 + ApiResponse.ok(data)         -> { "code": "SUCCESS", "message": "success", "data": ... }
  └── 异常 ──▶ BusinessException(ErrorCode) ──▶ Handler -> HTTP 200 + { "code": "XXX.YYY", "message": "...", "data": null }
```

- **统一响应契约（`ApiResponse<T>`）**：<默认统一返回 HTTP 200 与 `{ "code": "SUCCESS", "message": "success", "data": ... }`，失败时 `data` 为 `null` 并由 `code` 标识错误码；若受外部契约约束需直返资源或使用 4xx/5xx 状态码，在此写明契约规则>。
- **请求追踪（`X-Trace-Id`）**：统一通过响应头 `X-Trace-Id` 返回并绑定日志 MDC `trace_id`，严禁将 `traceId` 塞入 `ApiResponse.data`。
- **唯一默认 `BusinessException` + 分散点分层 `ErrorCode`**：全系统默认统一抛 `BusinessException(ErrorCode)`（仅 TypeScript 为 `BusinessError`，不按业务重复建异常子类）；错误码采用全大写点分层（两层如 `RISK.INVALID`，三层如 `RISK.CREATE.ERROR`），通用码放外层 `BaseErrorCode`（`COMMON.PARAM.INVALID`、`AUTH.UNAUTHENTICATED`、`AUTH.FORBIDDEN` 等），业务特性码在各业务模块内部（如 `domain/enums/XxxErrorCode` 或对应 `services/<domain>.py`）独立维护。
- **契约与表模型分离**：请求/响应 DTO 与数据库实体分离建模，入参在接入层声明式校验（`@Valid` / Pydantic / Zod）。
- **强类型状态与读写分离**：核心状态用强类型枚举或值对象封装合法流转判断，禁止裸字符串魔法值；写事务边界在 `application`（或 `services`）用例入口，分页列表走只读事务直接投影视图模型（不绕写侧聚合根）。
- **文件体积约束**：单文件建议不超过 `<350>` 行，超长时按职责拆分子模块或组件。

## 4. 横切基础设施入口

| 横切能力 | 集中入口位置 | 约定说明 |
| --- | --- | --- |
| **认证与身份上下文** | `<如 filters/AuthFilter 或 api/deps.py>` | `<说明如何解析身份并向应用层传递当前操作者>` |
| **请求追踪与日志** | `<如 filters/TraceFilter 或 core/middleware.py>` | `<说明 X-Trace-Id 响应头与日志 trace_id 绑定方式>` |
| **全局异常拦截** | `<如 exceptions/handler/GlobalExceptionHandler>` | `<说明 BusinessException 与校验异常如何转为统一响应>` |

## 5. 自动化架构护栏与验证命令

提交前执行以下检查并确保全绿：

```bash
# 1. 构建与类型检查
<mvn compile | bun run build | uv run pyrefly check>

# 2. 架构护栏、代码规范与业务测试
<mvn test (或启用 Checkstyle 时 mvn verify) | bun run lint && bun run test | uv run lint-imports && uv run ruff check . && uv run ruff format --check . && uv run pytest>
```

- **护栏定义位置**：`<如 src/test/.../ArchitectureRulesTest.java | .dependency-cruiser.cjs | pyproject.toml [tool.importlinter]>`

## 6. 显式豁免与 ADR 索引

- **当前豁免项**：`<无豁免 | 列明历史兼容或受限环境的豁免模块、原因与清理条件>`
- **决策与术语**：架构决策记录见 `docs/adr/`，领域术语见 `GLOSSARY.md`。
````
