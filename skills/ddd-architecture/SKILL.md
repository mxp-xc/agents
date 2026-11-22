---
name: ddd-architecture
description: Pragmatic Domain-Driven Design (DDD) architecture bootstrap, boundary reorganization, and automated guardrail setup. Trigger autonomously when starting a new project or bounded module, establishing layered directory skeletons, reorganizing pre-launch or early-stage code with blurred boundaries, or generating a repository CODING_STANDARDS.md and mechanical architecture checks (ArchUnit, dependency-cruiser, import-linter).
---

# 务实 DDD 架构

为新建项目、独立业务模块或尚未上线的早期系统建立清晰的务实 DDD 分层边界、项目编码规范（`CODING_STANDARDS.md`）、自动化架构护栏与标杆垂直切片（Walking Skeleton），防止业务扩张后结构退化或边界失控。

## 适用场景与输入输出

- **适用场景**：
  - 新建项目或新增独立业务模块，需要在写第一行业务代码前确立工程骨架与技术选型。
  - 尚未上线或处于早期开发阶段的代码，出现职责错位、层间反向依赖或单一文件膨胀，需要主动作结构整理。
  - 已有系统需要补齐分层边界规范、`CODING_STANDARDS.md` 与自动化架构检查。
- **输入**：业务目标或需求规格（若目标仓库存在 `GLOSSARY.md`、`docs/adr/` 或现有代码，应先读取）、目标技术栈、系统运行阶段（未上线/早期开发 vs 已上线稳定运行）。
- **输出**：1 页架构蓝图、目标仓库根目录 `CODING_STANDARDS.md`、接入默认检查链路的自动化架构护栏测试、1 个贯穿全层的标杆垂直切片（Walking Skeleton）及验证结果。

## 工作流

按以下 5 步顺序执行，每步必须满足其完成标准后才进入下一步：

1. **判定运行阶段与复杂度梯度**
   - 核对目标仓库现有代码、术语表（`GLOSSARY.md`）和架构决策记录（`docs/adr/`），确认系统处于**未上线/早期开发阶段**（允许一次理顺分层、命名、异常与横切入口）还是**已上线运行中系统**（保护对外契约与存量数据，按模块渐进演进）。
   - 读取 [ddd-tactical-guide.md](references/ddd-tactical-guide.md)，结合业务复杂度选定 **L1（轻量务实 DDD，默认）** 或 **L2（严格六边形/整洁 DDD）**；纯一次性脚本或极简工具直接降级为最小平铺结构并说明理由。
   - **完成标准**：运行阶段、DDD 梯度（或降级结论）及已参考的领域术语/ADR 均已明确。

2. **加载技术栈参考并输出 1 页架构蓝图**
   - 读取 [index.md](references/index.md)，按项目使用的语言与框架加载对应 `references/<stack>.md`（前后端或多端仓库分别读取）；尚未覆盖的技术栈按通用四层规则与该生态主流工程惯用法推导，并在蓝图中写明依据。
   - 单体项目默认**先按业务模块垂直分包、模块内再分四层**；凡存在 **2 个及以上**独立生命周期的核心业务概念或主表，均须拆分为同构业务模块，禁止合并为单一上帝 Controller / Service / Repository；跨模块协作统一经对方 `application` 门面并依托声明式事务传播。
   - 在 1 页架构蓝图中一次性拍板关键选型：持久层方案、声明式输入校验、集中鉴权与请求上下文入口、统一异常体系、强类型状态枚举策略、界限上下文分包与目录树、层间与模块间依赖红线。
   - 若技术栈未定或存在破坏性改动、重大架构取舍，先向用户简述蓝图并确认后再写代码；需求明确且已获授权的全新开发可直接落地蓝图并推进。
   - **完成标准**：蓝图包含目标目录树、依赖方向红线与关键技术选型，无悬而未决的架构冲突。

3. **落盘规范与机械护栏**
   - 读取 [coding-standards-template.md](references/coding-standards-template.md)，结合本次蓝图在目标仓库根目录创建或更新 `CODING_STANDARDS.md`，使后续实现与代码审查有唯一可核对的架构准绳。
   - 按对应技术栈参考接入自动化架构护栏（如 Java 的 ArchUnit / Checkstyle、TypeScript 的 ESLint 规则与 dependency-cruiser、Python 的 import-linter / ruff），护栏必须同时覆盖**四层依赖方向 + 跨模块隔离 + 无循环依赖**，并挂入项目默认测试或静态检查流程。
   - **完成标准**：`CODING_STANDARDS.md` 已落盘，架构护栏命令可执行且能拦截跨层、跨模块或反向依赖违规。

4. **交付 1 个标杆垂直切片（Walking Skeleton）**
   - 选取 1 个有代表性的核心业务用例，严格按照蓝图实现从接入入口到持久化落库的完整纵向切片并附带真实集成/单元测试，作为后续全仓扩展与委派子任务模仿的标杆样本。
   - 若属于未上线系统整改，先将耦合最严重的核心模块重整为标杆，再按界限上下文或模块分批迁移，每批迁移后保持构建与测试全绿。
   - **完成标准**：标杆切片完整贯穿四层与横切入口，业务测试与架构护栏测试全部通过。

5. **验证与交接**
   - 在目标仓库运行完整构建、业务测试与架构护栏检查，对照 `CODING_STANDARDS.md` 核对包归属、依赖方向、契约校验、异常与状态建模。
   - 汇报已落盘的文件清单、选定的 DDD 梯度与技术选型、护栏命令及实测结果，并明确后续新增功能沿标杆切片扩展的约定。
   - **完成标准**：全部构建、测试与架构护栏命令实测通过，无未闭环的跨层违规。

## 通用架构红线

- **依赖单向向内**：默认四层为 `interfaces → application → domain ← infrastructure`。`domain` 不得依赖外层协议、Web 框架或路由契约；`infrastructure` 不得反向依赖 `interfaces`；`interfaces` 不得绕过 `application` 直接调用写路径持久化实现。
- **模块化单体跨模块边界**：多业务模块共存时，先按业务分包、模块内再分四层；模块间仅允许经对方 `application` 门面或领域事件协作，禁止绕过门面穿透对方 `domain`、`infrastructure` 或 `interfaces`，且禁止模块间循环依赖。
- **四条底线（L1 与 L2 均须遵守）**：
  1. **强类型状态与领域概念**：业务状态与核心识别码使用强类型枚举或值对象，禁止在核心流程中用裸字符串魔法值驱动状态流转。
  2. **语义化异常与协议解耦**：领域层与持久化层只抛出表达业务含义的语义化异常，不出现 HTTP 状态码或协议响应细节；协议映射集中在入口异常处理器完成。
  3. **横切能力集中前置**：鉴权与身份解析、请求追踪、输入格式校验、全局异常映射从首版就在集中入口（Filter/Middleware/Interceptor 等）就位，不散落在业务方法内重复判断。
  4. **契约与分层独立组织**：对外请求/响应契约、领域模型与各层职责按约定分包分文件组织，不因初期代码量少而把多类公开契约或跨层逻辑混写进单一文件。

## 约束与降级策略

- **反过度设计**：不为简单 CRUD 强行引入 1:1 透传接口或空壳抽象；查询展示优先走轻量只读路径，不强行绕经写侧聚合根。
- **已上线系统保护**：存在外部稳定依赖或生产数据时，禁止未经用户明确同意破坏已有对外契约、修改表结构语义或变更存量数据。
- **受限环境降级**：若目标环境离线或受策略限制无法引入第三方架构检测依赖（如 ArchUnit、dependency-cruiser、import-linter），应在测试套件或构建脚本中编写轻量静态导入断言作为替代护栏，并在目标仓库 `CODING_STANDARDS.md` 中写明当前限制与后续补齐条件。
- **自包含分发**：本技能所有规范与参考文件均在当前技能目录内解析，不引用外部文档或特定项目私有规则。
