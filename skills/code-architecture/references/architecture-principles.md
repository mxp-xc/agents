# 通用代码架构原则

在确定具体框架或是否启用 DDD 前，按本文确定初始化分支、演进阶段、架构档位、目录边界与统一响应/异常协议。

## 一、存量检查与运行阶段策略

### 1. 首次初始化 3 分支决策流

目标仓库的编码规范固定存放在 `docs/CODING_STANDARDS.md`（不放仓库根目录）。

```text
检查目标仓库
│
├─ [分支 A] 已存在 docs/CODING_STANDARDS.md（或明确项目架构规范）
│   ├─ 跳过全仓扫描与重建蓝图，直接以现有规范为准
│   └─ 若现有规范仅覆盖部分维度（如只有目录，缺异常/响应/护栏）
│       └─ 完整保留既有约定 + 仅将缺失章节按本文标准补齐进 docs/CODING_STANDARDS.md
│
├─ [分支 B] 无规范文档，但有存量业务代码
│   ├─ 扫描现有包结构、配置、响应/异常风格与既有约束
│   ├─ 以当前项目既有结构为蓝图（不推倒强套默认模板）
│   ├─ 仅对代码中未约束的空白项引入本文默认标准
│   └─ 输出蓝图与拟补齐项 ──▶ 向用户询问确认 ──▶ 落盘 docs/CODING_STANDARDS.md
│
└─ [分支 C] 无规范文档，且无存量代码的全新项目
    ├─ 按第二节选定架构档位，拟定 1 页默认架构蓝图
    └─ 输出 1 页默认蓝图 ──▶ 向用户询问确认 ──▶ 落盘 docs/CODING_STANDARDS.md
        (注：用户明确要求直接端到端落地或处于不可交互子任务委派时，直接按默认落盘并在汇报中明示)
```

### 2. 未上线整改 vs 已上线渐进演进

```text
if 系统尚未上线 or 处于早期开发阶段:
  发现业务与技术目录混排、层间反向依赖、魔法字符串或巨型文件
    -> 立即按蓝图结构性重整（不带歪骨架叠功能）
    -> 先重整耦合最重的 1 个核心模块作为标杆垂直切片
    -> 构建 + 测试 + 架构护栏全绿后，分批清理其余模块

else (系统已上线 or 存在外部稳定依赖):
  保持现有 HTTP/RPC/CLI 契约、状态码与数据库表结构语义兼容
  先接入机械架构护栏锁定现状（历史遗留模块在 docs/CODING_STANDARDS.md 登记豁免范围与清理条件）
  按绞杀者（Strangler）模式演进：每次只抽离 1 个聚合或 1 条写路径，回归全绿后再推进下一处
```

## 二、架构档位选型矩阵

先按业务复杂度与技术生态选定档位，写入 `docs/CODING_STANDARDS.md`：

```text
是否是纯脚本 / 单表无状态小工具？
 ├── 是 ──▶ 【极简平铺】（最小平铺文件，不建分层套娃）
 └── 否 ──▶ 是否是前端应用 / Python FastAPI / 规则直白的中小 CRUD 服务？
             ├── 是 ──▶ 【轻量务实分层】（按职责横向分层，不拆重型四层）
             └── 否 ──▶ 是否有多协议(HTTP+MQ+gRPC) / 多团队并行 / 强迫零框架纯净领域？
                         ├── 否 ──▶ 【L1：轻量务实 DDD】（复杂后端默认）
                         └── 是 ──▶ 【L2：严格六边形 / 整洁 DDD】
```

| 档位 | 适用场景 | 目录特征 | 需读 [ddd-guide.md](ddd-guide.md) |
| --- | --- | --- | --- |
| **极简平铺** | 一次性脚本、单表工具、无状态胶水程序 | 平铺入口 + 少量模块文件 | 否 |
| **轻量务实分层** | FastAPI 服务、前端 Web 应用、规则直白的 CRUD 服务 | 横向分层（`api → services → repositories → db` 或 `app / features / shared`） | 否 |
| **L1：轻量务实 DDD** | 含 ≥2 个核心业务主表、状态机、权限归属或并发约束的单体后端 | `modules/<业务域>/` 内分四层 + 根包展平横切；砍掉 1:1 无用透传接口 | **必读** |
| **L2：严格整洁 DDD** | 多接入协议、极复杂核心域、多团队协作长周期系统 | `domain` 零框架注解；Entity 与 PO 严格分离；显式 Port/Adapter 与 CQRS | **必读** |

## 三、通用目录二分法与依赖红线

### 1. 全局目录二分图（按“是否含框架/IO”切分）

根包严禁把业务模块与零散技术目录按字母序混排，也严禁在根包建与模块内重名的顶层 `infrastructure/`。全局目录按是否含框架/IO 依赖一分为二：

```text
目标仓库根包 (com.example.app / src / app)
│
├── 【1. 业务区】
│   └── modules/<context>/ (L1/L2 后端)  或  features/<domain>/ (前端)  或  api+services+repositories (轻量分层)
│
├── 【2. 带框架横切与装配区】（含 Web / ORM / MQ / 容器依赖，核心业务层严禁依赖）
│   ├── config/ (或 core/)            # 框架配置、OpenAPI、Clock、连接池
│   ├── filters/ (或 middlewares/)    # TraceFilter (X-Trace-Id)、AuthFilter (身份解析)
│   ├── aop/                          # 审计、幂等切面（按需）
│   ├── exceptions/handler/           # 全局异常拦截器 (@RestControllerAdvice / FastAPI handler)
│   └── persistence/ (或 db/)         # 持久基建、公共事务/写锁（mq/、scheduler/ 按需同级展开）
│
└── 【3. 无框架公共区】（零框架、零 Web/DB/IO 依赖，所有层可依赖，严禁反向依赖业务或横切区）
    ├── types/                        # 跨 ≥2 模块复用的纯类型（禁用 common/ 垃圾桶命名）
    │   ├── enums/                    # 跨模块通用枚举
    │   ├── vo/                       # 跨模块不可变值对象（如 Money、TimeWindow）
    │   └── dto/                      # ApiResponse<T>、PageQuery、PageResult
    ├── utils/                        # 纯无状态静态工具函数（统一复数 utils/）
    └── exceptions/ (根包纯语义层)     # ErrorCode 接口、BaseErrorCode、唯一默认 BusinessException
```

### 2. 四条空间依赖红线

```text
[合法]  interfaces ──▶ application ──▶ domain ◀── infrastructure
[合法]  api        ──▶ services    ──▶ repositories ──▶ db
[合法]  任意层     ──▶ 无框架公共区 (types / utils / exceptions 纯异常)

[禁止]  domain (或 services)    ──✕──▶ interfaces / api / 带框架横切区 / Web 或 SQL 框架包
[禁止]  infrastructure / db     ──✕──▶ interfaces / api / 控制器 DTO
[禁止]  interfaces / api        ──✕──▶ 绕过业务层直接调用写侧 persistence / db
[禁止]  无框架公共区             ──✕──▶ modules / features / 带框架横切区
```

单模块私有的枚举、错误码、DTO 与辅助函数必须留在各自业务模块内，跨 ≥2 个模块复用时才提入 `types/` 或 `utils/`。当前无需求的子目录不预建空目录。

## 四、统一响应、通用异常与分层错误码

### 1. 请求与异常运行时链路

**契约优先原则**：目标项目已有明确接口规格或外部协议时（如要求直返资源 JSON 或指定 4xx/5xx 状态码），严格遵循既有契约。无既定规范时，采用以下全量 HTTP 200 + `ApiResponse<T>` 默认链路：

```text
HTTP Request
  └── TraceFilter / Middleware
        ├── 生成 traceId -> 绑定日志 MDC (trace_id)
        ├── 写入响应头: X-Trace-Id: <traceId>   (严禁塞入 ApiResponse.data！)
        └── AuthFilter / Dependency
              ├── 解析身份头/Token -> 注入 ActorContext (失败抛 BusinessException(AUTH.UNAUTHENTICATED))
              └── Controller / Router (@Valid 声明式校验)
                    ├── [正常路径] 调用 Application / Service
                    │     └── 显式返回 HTTP 200 + ApiResponse.ok(data)
                    └── [异常路径] 抛出 BusinessException(XxxErrorCode) 或校验异常
                          └── GlobalExceptionHandler (exceptions/handler/)
                                └── 统一拦截并返回 HTTP 200 + ApiResponse.fail(code, message)
```

默认响应 JSON 结构（定义于 `types/dto/ApiResponse`）：

```json
// 成功响应 (HTTP 200, Header: X-Trace-Id: 9f8e7d6c...)
{
  "code": "SUCCESS",
  "message": "success",
  "data": { "id": 101, "status": "ACTIVE" }
}

// 失败响应 (HTTP 200, Header: X-Trace-Id: 9f8e7d6c...)
{
  "code": "RISK.CREATE.ERROR",
  "message": "风控规则创建失败",
  "data": null
}
```

### 2. 唯一默认 `BusinessException` + 分散全大写点分层 `ErrorCode`

全系统默认**只定义一个通用业务异常类** `BusinessException`（Java/Python 为 `BusinessException`，仅 TypeScript 使用 `BusinessError`），接收 `ErrorCode`。不按业务模块创建一堆空壳异常子类（仅当极少数场景必须在异常上携带额外结构化字段供专门 `catch` 时，才可选继承 `BusinessException`）。

错误码采用**全大写 + 点号 `.` 分层**（两层 `领域.错误` 或三层 `领域.动作.错误`），按归属分散维护：

```text
exceptions/ErrorCode (接口: code() + defaultMessage())
  ├── exceptions/BaseErrorCode              # 外层通用错误码（全局唯一）
  ├── modules/risk/domain/enums/RiskErrorCode     # 风控模块内部独立维护
  └── modules/orders/domain/enums/OrderErrorCode  # 订单模块内部独立维护
```

| 归属位置 | 层级 | 错误码 (`code`) | 默认文案 (`message`) | 触发场景 |
| --- | --- | --- | --- | --- |
| **外层通用**<br>`exceptions/BaseErrorCode` | 单层 | `SUCCESS` | `success` | 请求成功 |
| 同上 | 三层 | `COMMON.PARAM.INVALID` | `请求参数不合法` | 入参格式、非空或校验注解失败 |
| 同上 | 二层 | `AUTH.UNAUTHENTICATED` | `未登录或身份凭证无效` | 缺失身份头或 Token 失效 |
| 同上 | 二层 | `AUTH.FORBIDDEN` | `无权限执行该操作` | 角色不匹配或非资源归属人越权 |
| 同上 | 三层 | `COMMON.RESOURCE.NOT_FOUND` | `请求的资源不存在` | 通用路径或基础资源不存在 |
| 同上 | 三层 | `COMMON.SYSTEM.ERROR` | `系统繁忙，请稍后重试` | 未预期异常兜底（内部记 ERROR 日志） |
| **业务模块内**<br>`domain/enums/XxxErrorCode` | 二层 | `RISK.INVALID` | `风控配置参数无效` | `特性.错误性质` |
| 同上 | 二层 | `TASK.TIMEOUT` | `任务执行超时` | `特性.错误性质` |
| 同上 | 二层 | `ORDER.NOT_FOUND` | `订单不存在` | `特性.错误性质` |
| 同上 | 三层 | `RISK.CREATE.ERROR` | `风控规则创建失败` | `特性.动作.错误性质` |
| 同上 | 三层 | `RISK.UPDATE.ERROR` | `风控规则更新失败` | `特性.动作.错误性质` |
| 同上 | 三层 | `ORDER.CREATE.INSUFFICIENT_STOCK` | `库存不足，无法创建订单` | `特性.动作.具体原因` |
| 同上 | 三层 | `ORDER.CANCEL.ALREADY_PAID` | `已支付订单不支持直接取消` | `特性.动作.具体原因` |

## 五、业务规则归属速查表

| 业务规则或场景 | 正确归属位置 | 禁止做法 |
| --- | --- | --- |
| 字段格式、范围、非空、枚举值合法性 | 接入层声明式校验（`@Valid` / Pydantic / Zod）+ 值对象构造自校验 | 在 Service 或 Repository 堆砌手工 `if (x == null)` |
| 状态流转约束与跨操作不变量 | 强类型状态枚举方法或领域实体行为方法（违规则抛 `BusinessException`） | 在多个 Service 方法各写一套裸字符串状态判断 |
| 主子集合强一致不变量 | 聚合根封装内部集合与业务动词方法 | 暴露全字段 setter 由外部逐个字段拼装改写 |
| 单事务增删改与幂等落库 | `application` / `services` 用例事务入口 + 数据库唯一约束/条件更新 | 为无状态机逻辑的简单记录硬建重型聚合根 |
| 身份提取 vs 角色/归属防越权 | 身份头解析放集中 Filter/Middleware；角色与资源归属校验放用例事务内 | 在每个 Controller 签名重复解析 Header，或轻信请求体里的 `userId` |
| 参与者业务资格（如账号冻结/启用） | 账号模块 `application` 资格门面或 Policy 对象 | 硬编码在前端或通用路由网关过滤器 |
| 组合筛选、分页列表与统计工作台 | 只读事务内直接走 Read View / 只读查询投影（同快照查总数与当前页） | 加载整棵写侧聚合根对象树再在内存过滤分页 |

## 六、反过度设计 5 项检查

写代码前逐条核对，命中即删减：

```text
[1. 删除测试] 删掉某接口/包装类后，调用方复杂度未增加反而直接消失？ ──▶ 它是纯透传中间人，删！
[2. 单一实现] 某接口在可预见周期内只有唯一实现，且单测无需替换？     ──▶ L1/轻量分层下直接写具体类，不拆 Foo + FooImpl
[3. 贫血空转] 实体只有 getter/setter，外面却套了 5 层 Manager/Handler？ ──▶ 合并透传层，把状态判断收进实体或枚举
[4. 空壳目录] 某层或某子包当前只有 1~2 个文件？                       ──▶ 直接放平在该层根目录，满 3 个同职责文件再建子包
[5. 不可机检] 某条架构规则无法写成自动化 import 断言？                 ──▶ 说明边界定义含糊，先收口目录边界再写代码
```
