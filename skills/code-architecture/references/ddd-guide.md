# 务实 DDD 深度落地指南

当项目通过 [architecture-principles.md](architecture-principles.md) 选定 **L1 轻量务实 DDD** 或 **L2 严格整洁 DDD** 时，按本文划分界限上下文（`modules/*`）、组织模块内四层结构并处理跨模块协作。

## 一、界限上下文拆分（`modules/*` 怎么划）

系统包含 **2 个及以上**独立核心业务概念时，在 `modules/` 下按界限上下文垂直拆包。

### 1. 拆分决策流（4 条判据）

```text
评估两个业务概念 A 与 B（如 Account vs Order vs Inventory）：
  ├── 1. 生命周期独立？（独立创建、流转、归档）
  ├── 2. 核心主表独立？（一张主表只归属一个模块写改，不共享直接写表）
  ├── 3. 变更原因独立？（改 A 的业务规则时，无需同步修改 B 的领域模型）
  └── 4. 门面边界清晰？（能用 2~5 个 application 门面方法概括对外能力）
        │
        ├── 满足 ──▶ 拆分为独立模块 modules/<a>/ 与 modules/<b>/
        └── 不满足（如 Order 与 OrderItem、RuleGroup 与 RuleItem，子表依附主表生存）
              └── 留在同一模块、同一聚合根内部维护强一致不变量
```

### 2. 跨模块黑盒访问红线

```text
modules/orders/
  └── application/OrderApplicationService
        │
        ├── [允许] ──▶ modules/inventory/application/InventoryApplicationService (公开门面/只读视图)
        │
        ├── [禁止] ──✕─▶ modules/inventory/interfaces/*       (严禁调内部控制器)
        ├── [禁止] ──✕─▶ modules/inventory/domain/*           (严禁直接拿对方可变聚合根)
        └── [禁止] ──✕─▶ modules/inventory/infrastructure/*   (严禁跨模块直接查改对方 Mapper/表)
```

## 二、模块内四层结构与职责

### 1. 四层依赖与子包收敛规则

```text
┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────────┐
│  interfaces  │ ──▶ │  application  │ ──▶ │    domain    │ ◀── │  infrastructure  │
│  (协议适配)  │     │ (用例与事务)  │     │ (规则与模型) │     │ (持久化与外部IO) │
└──────────────┘     └───────────────┘     └──────────────┘     └──────────────────┘

子目录按需收敛规则 (L1 档位):
  if 某层内部总文件数 <= 3 (或某子目录只有 1 个文件):
    直接放平在该层根目录下（不建单文件子目录套娃）
  else if 同职责文件 >= 3:
    按下方标准子包分组归位（严禁跨层混放 DTO 与 Entity）
```

```text
modules/orders/
├── interfaces/                  # 薄协议适配层：零业务判断、零数据库事务
│   ├── rest/                    # Controller / Router（入参校验、调 application、返回 ApiResponse<T>）
│   └── dto/
│       ├── request/             # CreateOrderRequest（一类一文件，带校验注解与 toCommand()）
│       └── response/            # OrderResponse（带 from(View)，严禁直出数据库实体）
├── application/                 # 用例编排层：事务边界、跨模块门面调用、权限归属核验
│   ├── OrderApplicationService  # 写用例入口（@Transactional）与对外模块门面
│   ├── command/                 # 入参 > 3~4 个时封装不可变 Command（少参数直接传值对象/ID）
│   └── query/                   # OrderQueryService（只读列表/分页投影，不绕写侧聚合根）
├── domain/                      # 核心业务层：零 Web/ORM/框架横切依赖，可纯内存单测
│   ├── model/                   # 聚合根 Order、内部子实体 OrderItem
│   ├── vo/                      # 域内不可变值对象（跨模块共用的提入根包 types/vo/）
│   ├── enums/                   # 状态枚举 OrderStatus + 本特性错误码 OrderErrorCode
│   ├── repository/              # 仅面向聚合根定义 OrderRepository 接口
│   ├── service/                 # [按需] 跨多实体纯内存规则或 Policy（绝大多数模块不需要）
│   └── event/                   # [按需] 过去式不可变领域事件（如 OrderConfirmedEvent）
└── infrastructure/              # 技术实现层：仅向内依赖 domain 与 application，严禁引 interfaces
    ├── persistence/             # OrderRepositoryImpl、ORM Mapper/JPA、以及 L2/异构表下的 po/
    └── gateway/                 # [按需] 外部第三方 SDK 防腐层（翻译外部协议与异常）
```

### 2. `domain/` 建模代码形态对比

把状态机与不变量收拢进聚合根与强类型枚举，消灭贫血 setter 与散落的字符串判断：

```diff
 // 反例：贫血模型 + Service 散落字符串判断
-if (!"PENDING".equals(order.getStatus())) {
-    throw new OrderCancelException("已支付订单不可取消");
-}
-order.setStatus("CANCELLED");
-order.setCancelReason(reason);
-order.setUpdatedAt(Instant.now());

 // 正例：强类型状态枚举 + 聚合根业务动词方法 + 唯一默认 BusinessException
+public void cancel(String reason, Instant now) {
+    Objects.requireNonNull(reason, "cancel reason must not be null");
+    Objects.requireNonNull(now, "now must not be null");
+    if (!this.status.canTransitionTo(OrderStatus.CANCELLED)) {
+        throw new BusinessException(OrderErrorCode.ORDER_CANCEL_NOT_ALLOWED);
+    }
+    this.status = OrderStatus.CANCELLED;
+    this.cancelReason = reason;
+    this.updatedAt = now;
+}
```

`domain/` 各组件边界约束：

| 组件 | 核心规则 |
| --- | --- |
| **聚合根 (`model/`)** | 唯一外部修改入口；跨聚合只持有对方 ID（如 `customerId`），严禁直接嵌套其他聚合对象树做级联更新 |
| **值对象 (`vo/`)** | 无 ID、不可变、构造器自校验（合法即存在）；仅本模块用的放 `domain/vo/`，跨模块提至根包 `types/vo/` |
| **枚举与错误码 (`enums/`)** | 状态枚举封装 `canTransitionTo`；特性错误码枚举（如 `OrderErrorCode`）实现根包 `exceptions/ErrorCode`，维护两层或三层全大写点分层码（`ORDER.NOT_FOUND`、`ORDER.CANCEL.ALREADY_PAID`） |
| **仓储端口 (`repository/`)** | 只为聚合根建仓储（不为子实体单建）；出入参仅限领域对象、值对象或 ID，严禁出现 HTTP DTO 或 ORM 查询器 |

### 3. `application/` 用例编排标准调用树

写用例方法固定承担事务开启、时钟采样、资格/归属校验、领域调用与审计日志 5 件事：

```text
OrderApplicationService.cancelOrder(actor, orderId, reason)  [@Transactional]
  ├── 1. accountFacade.requireActiveAccount(actor.id())      # 跨模块调门面核验实时资格
  ├── 2. order = orderRepository.findById(orderId)           # 加载聚合根（不存在抛 ORDER.NOT_FOUND）
  ├── 3. order.assertOwnedBy(actor.id())                     # 校验资源归属（越权抛 AUTH.FORBIDDEN）
  ├── 4. order.cancel(reason, clock.instant())               # 注入统一 Clock，驱动领域状态流转
  ├── 5. orderRepository.save(order)                         # 持久化新状态
  └── 6. log.info("order_cancelled id={} by={}", ...)        # 结构化审计日志（MDC 自动带 trace_id）
```

列表筛选与分页查询直接走轻量读通道（CQRS 读写分离）：

```text
OrderController.listOrders(queryDto)
  └── OrderQueryService.pageOrders(pageQuery)                [@Transactional(readOnly = true)]
        └── OrderReadRepository / Mapper                     # 只读事务内直接查 total + items 视图投影
              └── 直接返回 PageResult<OrderSummaryView>      # 不加载写侧 Order 聚合根，避免 N+1
```

### 4. `infrastructure/` 持久模型（L1 vs L2 分界）

```text
if 档位 == L1 and 数据库表与领域实体 1:1 对齐 and 无重度框架注解污染:
  Mapper/DAO 读取轻量 Row 记录 -> 在 RepositoryImpl 内通过领域构造器重水化 (Rehydrate) 为领域实体
else (表结构拆分/合并、含大量软删/乐观锁技术列、或选定 L2 档位):
  在 infrastructure/persistence/po/ 独立定义 Persistence Object (PO)
  在 RepositoryImpl 显式转换 Domain Entity <-> PO，严禁 ORM 注解或数据库异常越出 infrastructure/
```

## 三、跨模块协作模式速查

| 协作场景 | 推荐机制 | 禁止做法 |
| --- | --- | --- |
| **同事务强一致写** | 上游 `application` 开启写事务（`REQUIRED`），调用下游 `application` 门面（同处一个事务）；全局写锁辅助放根包 `persistence/` | 把多张业务表揉回一个上帝 `Store`/`Mapper`，或跨模块直接改对方表 |
| **跨模块资格/存在性校验** | 下游 `application` 暴露 `requireActive` / `getSummaryView` 只读门面（只返不可变 View、布尔或 ID） | 下游把可变领域聚合根或 DAO 直接暴露给其他模块 |
| **跨模块组合分页查询** | 数据库受控只读 SQL 视图或专属读查询通道，在单只读事务内同时查总数与当前页 | 先查模块 A 分页，再在循环里调模块 B 接口做内存过滤（分页总数失真 + N+1） |
| **非强一致后置副作用** | 主事务提交后发布过去式领域事件或走 `mq/` 异步消费 | 把发邮件、算积分、统计报表同步塞进核心写事务 |

## 四、L1 与 L2 裁剪对照表

| 维度 | L1：轻量务实 DDD（默认） | L2：严格六边形 / 整洁 DDD |
| --- | --- | --- |
| **持久映射** | 表与模型一致时允许轻量 Row 重水化；出现拆表或框架污染时拆 `po/` | `domain` 零任何框架/ORM 注解；Entity 与 PO 100% 物理分离 |
| **端口抽象** | 仅对聚合根仓储、外部网关与只读查询建接口；用例服务直接写具体类 | 每个用例入出参均定义显式 `InputPort` / `OutputPort` 接口 |
| **读路径** | `application` 定义只读查询服务/端口，`infrastructure` 直接投影视图 | 独立 CQRS 读模型管道，与写侧存储模型完全解耦 |
| **测试组合** | 真实数据库/容器端到端集成测试 + 核心领域不变量单测 + 机械护栏 | 内存 Fake 仓储驱动的毫秒级领域/用例单测 + 适配器契约测试 + 机械护栏 |

## 五、常见“假 DDD”反模式排雷

| 反模式症状 | 根因 | 修复动作 |
| --- | --- | --- |
| **贫血实体 + 五层透传** | 实体全是 setter，外面套 `Controller -> Manager -> Service -> Handler` | 删掉纯透传中间层；状态流转与不变量收进实体、值对象与强类型枚举 |
| **单实现 `*ServiceImpl` 泛滥** | 每个应用服务和 Assembler 都硬拆接口 + `Impl`，跳代码多跳一层 | L1 下应用服务直接写具体类，只对仓储端口和外部网关保留接口 |
| **跨聚合嵌套对象树** | `Order` 直接持 `Customer` 与 `Product` 实体引用，一查拉起半张库 | 聚合间只存对方强类型 ID 或必要快照值，由 `application` 编排协作 |
| **借口同事务建上帝仓储** | 以“共用事务/写锁”为由把多模块 SQL 塞进一个文件 | 用声明式事务传播 + 根包 `persistence/` 公共事务包装，各模块只写自己的表 |
| **分页列表走写侧聚合根** | 先查 ID 列表再循环 `findById` 拼聚合根转 DTO | 列表筛选一律走只读查询投影直出 `View` |
