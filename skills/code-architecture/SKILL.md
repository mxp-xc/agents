---
name: code-architecture
description: Pragmatic code architecture and Domain-Driven Design (DDD) bootstrap, boundary reorganization, and automated guardrail setup. Trigger autonomously when starting a new project or bounded module, establishing layered directory skeletons, reorganizing pre-launch or early-stage code with blurred boundaries, or generating docs/CODING_STANDARDS.md and mechanical architecture checks (ArchUnit, dependency-cruiser, import-linter).
---

# 代码架构与务实 DDD

为新建项目、独立业务模块或未上线早期代码建立分层边界、编码规范（`docs/CODING_STANDARDS.md`）、统一响应与异常体系、自动化架构护栏及标杆垂直切片（Walking Skeleton）。

```text
[1. 存量优先分流] ──▶ [2. 选档位出 1 页蓝图] ──▶ [3. 落盘规范与机械护栏] ──▶ [4. 交付标杆垂直切片] ──▶ [5. 验证与交接]
```

## 适用场景与输入输出

| 维度 | 内容 |
| --- | --- |
| **触发场景** | ① 新项目或新业务模块写代码前立骨架<br>② 未上线代码职责错位、反向依赖或单文件膨胀需结构整理<br>③ 既有系统补齐 `docs/CODING_STANDARDS.md` 与自动化架构护栏 |
| **输入** | 目标仓库现有规范文档、存量代码、`GLOSSARY.md`、`docs/adr/`、业务需求规格、目标技术栈与运行阶段 |
| **输出** | 1 页架构蓝图、`docs/CODING_STANDARDS.md`、自动化架构护栏测试、1 个贯穿全层的标杆垂直切片及验证结果 |

## 按需加载指针

不要一次性读取全部参考文件。按当前步骤与目标技术栈按需加载（完整索引见 [references/index.md](references/index.md)）：

```text
读 references/architecture-principles.md    # 必读：3 分支初始化、档位选型、目录二分边界、统一响应与异常
├── 选定 L1 / L2 务实 DDD？
│   └── 读 references/ddd-guide.md          # 界限上下文拆分、四层内部职责、跨模块事务与查询协作
├── 挑选目标技术栈参考（可多选，位于 references/stacks/）：
│   ├── Java / Spring Boot ──▶ 读 references/stacks/java.md
│   ├── Python / FastAPI   ──▶ 读 references/stacks/python.md
│   └── TypeScript 前后端  ──▶ 读 references/stacks/typescript-web.md
└── 准备落盘规范文档时
    └── 读 references/coding-standards-template.md
```

## 执行步骤

按顺序执行以下 5 步，每步满足完成标准后进入下一步。

### 1. 存量检查与初始化分流

先检查目标仓库是否存在 `docs/CODING_STANDARDS.md`（或其他明确架构规范）及存量业务代码，按以下逻辑分流：

```text
if 存在 docs/CODING_STANDARDS.md 或明确项目规范:          # 分支 A：已有规范
  跳过全仓架构扫描，直接以现有规范为准
  记录缺失维度（如缺异常/响应/护栏），留待第 3 步按默认标准补齐合并

else if 存在存量业务代码:                                 # 分支 B：有代码无规范
  读取现有代码结构、响应/异常风格与既有约束
  以当前项目既有结构作为第 2 步蓝图基准，仅对未约束空白项引入默认标准

else:                                                     # 分支 C：全新空项目
  读 architecture-principles.md 选定架构档位（极简平铺 / 轻量务实分层 / L1 / L2）
```

完成标准：已按 A/B/C 分支确定运行阶段（未上线 vs 已上线）、架构档位及规范基准来源。

### 2. 输出 1 页架构蓝图

按上方指针读取对应技术栈参考（选定 L1/L2 时一并读 [ddd-guide.md](references/ddd-guide.md)），输出包含以下 5 项的 1 页蓝图（分支 A 已有完整规范时直接沿用并仅列缺失增量；分支 B/C 在此步将蓝图交用户确认，仅当用户明确要求直接端到端落地或处于不可交互子任务委派时才按默认推进并明示）：

1. **目录骨架**：业务区（如 `modules/`、`features/` 或水平分层 `api/services/repositories/db`）、无框架公共区（`types/`、`utils/`、`exceptions/` 纯异常）、带框架横切区（`config/`、`filters/`、`middlewares/`、`aop/`、`exceptions/handler/`、`persistence/`）。
2. **层间与模块依赖图**：标明单向依赖方向与跨模块访问门面。
3. **响应与异常协议**：统一响应体 `ApiResponse<T>`（默认 HTTP 200 + `{code, message, data}`，契约另有规定的从契约）、`X-Trace-Id` 响应头、唯一默认 `BusinessException` + 全大写点分层 `ErrorCode`。
4. **横切与持久选型**：ORM/持久方案、声明式入参校验、集中鉴权与身份注入入口。
5. **状态建模**：核心业务状态枚举与合法流转收拢位置。

完成标准：1 页蓝图已包含目录树、依赖方向红线与上述 5 项选型，无悬而未决的边界冲突。

### 3. 落盘 `docs/CODING_STANDARDS.md` 与机械护栏

读取 [coding-standards-template.md](references/coding-standards-template.md)，在目标仓库创建或更新 `docs/CODING_STANDARDS.md`。

按技术栈参考接入自动化架构护栏，并挂入默认测试或 lint 命令：

| 技术栈 | 护栏工具 | 必检的 4 条边界规则 |
| --- | --- | --- |
| **Java / Spring** | ArchUnit (+ Checkstyle) | ① 层间单向依赖（接入层不跳层写库，持久层不引接入层）<br>② 核心业务/领域层不依赖 Web 框架与带框架横切目录<br>③ 无框架公共区（`types`/`utils`/纯异常）不反向依赖业务或框架目录<br>④ 多业务模块仅经 `application` 门面协作，无循环依赖 |
| **TypeScript** | ESLint + dependency-cruiser | 同上（前端附加 `features/*` 隔离与组件禁裸 `fetch`） |
| **Python** | import-linter + ruff + pyrefly | 同上（`api -> services -> repositories -> db` 单向依赖 + 类型与文档规范检查） |

完成标准：`docs/CODING_STANDARDS.md` 已落盘，护栏命令实测可运行并能阻断越界 import。

### 4. 交付 1 个标杆垂直切片（Walking Skeleton）

选取 1 个核心业务用例，按蓝图实现从接入层、应用/服务层、领域/核心层到持久化的完整纵向切片，配套真实集成与单元测试（若任务仅为已上线系统补齐规范与架构护栏，直接以既有核心用例作为验证切片，不重写正常运行的业务代码）。

未上线早期代码整改按以下顺序推进：

```text
挑耦合最重的核心模块重整为标杆切片
  └── 跑通构建 + 业务测试 + 架构护栏
        └── 按模块分批迁移其余代码（每批保持测试全绿）
```

完成标准：标杆切片贯穿全部层级与横切入口，业务测试与架构护栏测试全部通过。

### 5. 验证与交接

在目标仓库执行完整构建、业务测试与架构护栏命令，对照 `docs/CODING_STANDARDS.md` 核对文件归属、依赖方向、统一响应/异常与状态枚举。向用户汇报落盘文件清单、架构档位、护栏命令与实测结果。

完成标准：构建、测试与架构护栏命令全部零报错通过。

## 核心架构底线

```text
                  ┌──────────────────────────────────────────┐
                  │         带框架横切与装配区               │
                  │ config / filters / middlewares / aop     │
                  │ exceptions/handler / persistence         │
                  └────────────────────┬─────────────────────┘
                                       │ 装配与拦截（核心层严禁反向依赖）
                                       ▼
┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────────┐
│  interfaces  │ ──▶ │  application  │ ──▶ │    domain    │ ◀── │  infrastructure  │
│   (或 api)   │     │ (或 services) │     │ (核心业务层) │     │(或 repositories) │
└──────────────┘     └───────────────┘     └──────┬───────┘     └──────────────────┘
                                                  │ 允许依赖（零框架/零 IO）
                                                  ▼
                  ┌──────────────────────────────────────────┐
                  │             无框架公共区                 │
                  │ types(enums/vo/dto) / utils              │
                  │ exceptions(ErrorCode, BusinessException) │
                  └──────────────────────────────────────────┘
```

所有非脚本项目必须守住以下 4 条底线（细则见 [architecture-principles.md](references/architecture-principles.md)）：

1. **强类型状态流转**：用强类型枚举或值对象封装业务状态与合法转移判断，禁止在业务流程中用裸字符串魔法值驱动状态流转。
2. **统一响应与唯一默认业务异常**：无外部契约冲突时统一返回 HTTP 200 与 `ApiResponse<T>({code, message, data})`，`traceId` 走响应头 `X-Trace-Id`（严禁塞入 `data`）；全系统默认只抛 `BusinessException(ErrorCode)`，各模块独立维护全大写点分层错误码（如 `RISK.INVALID`、`RISK.CREATE.ERROR`）。
3. **横切能力集中前置**：鉴权解析、请求追踪、入参格式校验与全局异常拦截在集中入口一次就位，不在控制器或业务方法内重复手工处理。
4. **契约与存储分离**：请求/响应 DTO、领域模型与数据库实体分包分文件独立组织，禁用 `common/` 泛化垃圾桶命名。

## 约束与降级策略

- **反过度设计**：简单 CRUD 不建 1:1 空壳透传接口；列表与分页查询直接走只读投影，不绕经写侧聚合根。
- **已上线契约保护**：已上线系统或存在外部稳定依赖时，保持现有接口契约、HTTP 状态码与表结构兼容；未经用户明确同意，不得破坏既有契约或改写存量数据。
- **受限环境降级**：离线环境无法安装第三方护栏库时，在测试套件中编写静态 AST/正则 import 检查测试替代，并在 `docs/CODING_STANDARDS.md` 记录限制与替换条件。
- **独立分发**：所有参考文件路径均在本技能目录内解析。
