# Java + Spring Boot 务实 DDD 落地方案

适用于现代 JDK + Spring Boot 服务（默认选用最新 LTS / 稳定版）。默认采用**模块化单体（`modules/` 收拢业务域 + 根包展平横切）+ 模块内四层**的 **L1 轻量务实 DDD**（四层细则见 [ddd-guide.md](../ddd-guide.md)，通用底线见 [architecture-principles.md](../architecture-principles.md)）。

## 一、包骨架与依赖边界

包含 ≥2 个核心业务主表或独立生命周期概念（如 `account`、`inventory`、`orders`）时，全部收拢在 `modules/` 下拆为独立子包；非业务横切与无框架公共类型直接展平在根包，避免根包业务与技术目录混排或顶层 `infrastructure/` 重名。

### 1. 标准目录树

```text
com.example.app/
├── Application.java                          # 启动入口（留根包，自动扫描全包）
│
├── modules/                                  # 【1. 业务区】唯一业务入口，按界限上下文拆包
│   ├── account/                              # 账号域（对外仅暴露 application 门面）
│   │   ├── interfaces/
│   │   ├── application/AccountApplicationService.java
│   │   ├── domain/
│   │   └── infrastructure/
│   ├── inventory/                            # 库存域（对外仅暴露 application 门面）
│   │   ├── interfaces/
│   │   ├── application/InventoryApplicationService.java
│   │   ├── domain/
│   │   └── infrastructure/
│   └── orders/                               # 订单域（先业务，后四层）
│       ├── interfaces/
│       │   ├── rest/OrderController.java     # 协议适配、@Valid 校验、调 application、返回 ApiResponse<T>
│       │   └── dto/
│       │       ├── request/                  # CreateOrderRequest.java（一类一文件）
│       │       └── response/                 # OrderResponse.java（纯业务载荷）
│       ├── application/
│       │   ├── OrderApplicationService.java  # @Transactional 边界、跨模块门面编排、归属核验
│       │   ├── command/                      # 入参 >4 个时封装不可变 record Command
│       │   └── query/OrderQueryService.java  # 只读列表/分页投影 (@Transactional(readOnly = true))
│       ├── domain/
│       │   ├── model/Order.java              # 聚合根与子实体（封装状态流转与不变量）
│       │   ├── enums/
│       │   │   ├── OrderStatus.java          # 强类型状态枚举（含 canTransitionTo）
│       │   │   └── OrderErrorCode.java       # 本模块全大写点分层错误码（实现 ErrorCode）
│       │   └── repository/OrderRepository.java # 面向聚合根的仓储端口
│       └── infrastructure/
│           └── persistence/
│               ├── OrderRepositoryImpl.java  # 实现 OrderRepository，内部调 Mapper/JPA
│               ├── mapper/                   # MyBatis-Plus Mapper 或 Spring Data JPA Repository
│               └── po/                       # L2 或异构表时独立 PO；L1 表一致时可轻量重水化
│
├── config/                                   # 【2. 带框架横切区】OpenAPI、Clock、Web、ORM 配置
├── filters/                                  # TraceFilter (写 X-Trace-Id 与 MDC)、AuthInterceptor / 身份参数解析器
├── aop/                                      # 审计、幂等切面（按需创建）
├── persistence/                              # BaseEntity、公共写锁/事务包装（按需；mq/、scheduler/ 同理）
│
├── exceptions/                               # 【3. 异常体系（纯语义层与 Spring Web 拦截层分包）】
│   ├── ErrorCode.java                        # [无框架] 错误码接口 (code() + defaultMessage())
│   ├── BaseErrorCode.java                    # [无框架] 外层通用错误码 (SUCCESS / COMMON.* / AUTH.*)
│   ├── BusinessException.java                # [无框架] 全系统唯一默认业务异常
│   └── handler/
│       └── GlobalExceptionHandler.java       # [带框架] @RestControllerAdvice（domain 严禁依赖此子包）
│
├── types/                                    # 【4. 无框架公共类型】禁用 common 垃圾桶命名，按需建子包
│   ├── enums/                                # 跨 ≥2 模块共用的纯枚举
│   ├── vo/                                   # 跨 ≥2 模块共用的不可变值对象（Money, TimeWindow）
│   └── dto/                                  # ApiResponse.java, PageQuery.java, PageResult.java
└── utils/                                    # 【5. 无框架纯工具】跨 ≥2 模块复用的纯静态方法
```

> 单域简化条件：仅当用户明确要求单聚合微型服务（全库仅 1 张核心主表）或采用 Maven 多模块物理分包时，才可省去 `modules/<context>` 层级。

### 2. 请求、事务与异常运行时调用树

```text
HTTP Request
  └── filters.TraceFilter
        ├── 生成 traceId -> MDC.put("trace_id", traceId)
        ├── response.setHeader("X-Trace-Id", traceId)
        └── filters.AuthInterceptor / ActorArgumentResolver (或委托 HandlerExceptionResolver 的 Filter)
              ├── 提取并校验身份 Header/Token (失败抛 BusinessException(BaseErrorCode.AUTH_UNAUTHENTICATED))
              └── modules.orders.interfaces.rest.OrderController
                    ├── @Valid 触发入参校验 (失败由 GlobalExceptionHandler 转为 COMMON.PARAM.INVALID)
                    ├── 调用 OrderApplicationService.createOrder(actor, req.toCommand())  [@Transactional]
                    │     ├── accountService.requireActive(actor.id())    # 自动共享同一 Spring 事务 (REQUIRED)
                    │     ├── inventoryService.reserveStock(...)          # 跨模块仅调对方 application 门面
                    │     ├── order = Order.create(...)                   # 领域不变量校验 (失败抛 ORDER.*)
                    │     └── orderRepository.save(order)
                    └── 返回 ApiResponse.ok(OrderResponse.from(order))    # HTTP 200
```

## 二、起手一次拍板的 5 项选型

写第一行业务代码前一次性敲定并记入 `docs/CODING_STANDARDS.md`：

| 选型项 | 落地规范 |
| --- | --- |
| **1. 持久层框架** | 二选一：**MyBatis-Plus**（偏 SQL 可控与定制投影）或 **Spring Data JPA**（偏标准对象持久化），禁手写裸 JDBC 拼接 |
| **2. 声明式校验** | `spring-boot-starter-validation`，Controller 入参加 `@Valid`，Request DTO 字段标 `@NotBlank`/`@NotNull`/`@Size` |
| **3. 追踪与集中鉴权** | `TraceFilter` 统一写响应头 **`X-Trace-Id`** 与日志 MDC；`HandlerInterceptor`/参数解析器（或委托 `HandlerExceptionResolver` 的 Filter）统一提取操作者身份，使 `BusinessException` 能被 `@RestControllerAdvice` 统一捕获 |
| **4. 响应与异常体系** | 默认全量 HTTP 200 + `ApiResponse<T>`（既有契约另有规定的从契约）；全系统唯一 `BusinessException` + 分散全大写点分层 `ErrorCode` |
| **5. 契约文档** | `springdoc-openapi-starter-webmvc-ui`，DTO 与端点加 `@Schema`、`@Operation` |

### 统一响应与异常核心代码模板

```java
// 1. types/dto/ApiResponse.java（零框架依赖，traceId 走 X-Trace-Id 响应头，不进 data）
public record ApiResponse<T>(String code, String message, T data) {
    public static <T> ApiResponse<T> ok(T data) { return new ApiResponse<>("SUCCESS", "success", data); }
    public static ApiResponse<Void> ok() { return new ApiResponse<>("SUCCESS", "success", null); }
    public static ApiResponse<Void> fail(String code, String message) { return new ApiResponse<>(code, message, null); }
}

// 2. exceptions/ErrorCode.java & BaseErrorCode.java（零框架依赖）
public interface ErrorCode {
    String code();
    String defaultMessage();
}

public enum BaseErrorCode implements ErrorCode {
    SUCCESS("SUCCESS", "success"),
    COMMON_PARAM_INVALID("COMMON.PARAM.INVALID", "请求参数不合法"),
    AUTH_UNAUTHENTICATED("AUTH.UNAUTHENTICATED", "未登录或凭证无效"),
    AUTH_FORBIDDEN("AUTH.FORBIDDEN", "无权限执行该操作"),
    COMMON_RESOURCE_NOT_FOUND("COMMON.RESOURCE.NOT_FOUND", "目标资源不存在"),
    COMMON_SYSTEM_ERROR("COMMON.SYSTEM.ERROR", "服务内部异常");
    // 构造器与 code() / defaultMessage() 实现...
}

// 3. modules/orders/domain/enums/OrderErrorCode.java（各模块独立维护两层或三层全大写点分层码）
public enum OrderErrorCode implements ErrorCode {
    ORDER_INVALID("ORDER.INVALID", "订单参数或状态无效"),
    ORDER_NOT_FOUND("ORDER.NOT_FOUND", "订单不存在"),
    ORDER_CREATE_INSUFFICIENT_STOCK("ORDER.CREATE.INSUFFICIENT_STOCK", "库存不足，无法创建订单"),
    ORDER_CANCEL_ALREADY_PAID("ORDER.CANCEL.ALREADY_PAID", "已支付订单不可取消");
    // 构造器与 code() / defaultMessage() 实现...
}

// 4. exceptions/BusinessException.java（全系统默认只抛这一个业务异常类）
public class BusinessException extends RuntimeException {
    private final ErrorCode errorCode;
    public BusinessException(ErrorCode errorCode) { super(errorCode.defaultMessage()); this.errorCode = errorCode; }
    public BusinessException(ErrorCode errorCode, String message) { super(message); this.errorCode = errorCode; }
    public ErrorCode errorCode() { return errorCode; }
}
```

## 三、关键正反模式代码对比

### 1. 身份解析与响应包装

```diff
 @RestController
 @RequestMapping("/api/orders")
 public class OrderController {
-    // 反例：每个方法手工解析 Header、裸返 Map 或把 traceId 塞进 data
-    @PostMapping
-    public Map<String, Object> create(@RequestHeader("X-User-Id") String rawUserId,
-                                      @RequestBody CreateOrderRequest req) { ... }

+    // 正例：前置解析强类型 Actor、@Valid 声明校验、显式返回 ApiResponse<T>
+    @PostMapping
+    public ApiResponse<OrderResponse> create(@CurrentActor Actor actor,
+                                             @Valid @RequestBody CreateOrderRequest req) {
+        OrderView view = orderApplicationService.createOrder(actor, req.toCommand());
+        return ApiResponse.ok(OrderResponse.from(view));
+    }
 }
```

### 2. 正反模式速查表

| 关注点 | 推荐做法 | 禁止做法 |
| --- | --- | --- |
| **DTO 与响应** | `CreateOrderRequest`、`OrderResponse` 一类一文件；显式返回 `ApiResponse<OrderResponse>`；`traceId` 放 `X-Trace-Id` 响应头 | 把十几个嵌套 `record` 塞进单一 `*Contract.java`；或把 `traceId` 塞入 `data` |
| **异常与错误码** | 全系统抛 `new BusinessException(OrderErrorCode.XXX)`；各模块独立维护 `XxxErrorCode` | 每个模块建一堆空壳异常类；或把所有模块错误码塞进同一个全局大枚举 |
| **状态流转** | `OrderStatus.canTransitionTo(target)` + 实体方法 `order.cancel(reason, now)` | 散落 `"CONFIRMED".equals(row.getStatus())` 魔法字符串 |
| **仓储边界** | `OrderRepository` 出入参仅限领域实体、值对象与强类型 ID | `Repository` 直接 `import` Controller DTO 或处理 HTTP 分页参数 |
| **长参数收敛** | 参数 >4 个时封装不可变 `Command` / `Query` record | 方法签名连续传 6~8 个零散 `String` / 基础类型 |
| **公共包纪律** | 跨模块枚举/VO/DTO 放 `types/{enums,vo,dto}/`，纯工具放 `utils/` | 根包业务与技术目录混排、建顶层 `infrastructure/` 或 `common/` 垃圾桶 |

## 四、机械护栏：ArchUnit（必选）+ Checkstyle（推荐）

### 1. ArchUnit 护栏测试（`src/test/java/<basePackage>/ArchitectureRulesTest.java`）

在 `pom.xml` 引入 `com.tngtech.archunit:archunit-junit5`，随 `mvn test` 自动校验以下 4 条硬边界：

```text
[规则 1] ..domain..               ──✕──▶ ..interfaces.. / ..application.. / ..infrastructure.. / 带框架横切包 / Spring Web & SQL
[规则 2] types / utils / 纯异常    ──✕──▶ modules.. / 带框架横切包 / Spring & Servlet & SQL
[规则 3] ..infrastructure..       ──✕──▶ ..interfaces..  且  ..interfaces.. ──✕──▶ ..persistence..
[规则 4] modules.<A>..            ──✕──▶ modules.<B>.(interfaces|domain|infrastructure)..  且  modules.(*).. 无循环依赖
```

```java
package com.example.app;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.library.dependencies.SlicesRuleDefinition;
import org.springframework.web.bind.annotation.RestController;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

@AnalyzeClasses(packages = "com.example.app", importOptions = ImportOption.DoNotIncludeTests.class)
class ArchitectureRulesTest {

    @ArchTest
    static final ArchRule domainMustNotDependOnOuterLayersOrFrameworkPackages =
        noClasses().that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage(
                "..interfaces..", "..application..", "..infrastructure..",
                "com.example.app.config..", "com.example.app.filters..", "com.example.app.aop..",
                "com.example.app.persistence..", "com.example.app.mq..", "com.example.app.scheduler..",
                "com.example.app.exceptions.handler..");

    @ArchTest
    static final ArchRule domainMustNotDependOnWebOrSqlDrivers =
        noClasses().that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage(
                "org.springframework.web..", "jakarta.servlet..", "java.sql..");

    @ArchTest
    static final ArchRule pureCommonTypesAndUtilsMustStayIndependent =
        noClasses().that().resideInAnyPackage("com.example.app.types..", "com.example.app.utils..")
            .or().resideInAPackage("com.example.app.exceptions")
            .should().dependOnClassesThat().resideInAnyPackage(
                "com.example.app.modules..", "com.example.app.config..", "com.example.app.filters..",
                "com.example.app.aop..", "com.example.app.persistence..", "com.example.app.mq..",
                "com.example.app.scheduler..", "com.example.app.exceptions.handler..",
                "org.springframework..", "jakarta.servlet..", "java.sql..");

    @ArchTest
    static final ArchRule infrastructureMustNotDependOnInterfaces =
        noClasses().that().resideInAPackage("..infrastructure..")
            .should().dependOnClassesThat().resideInAPackage("..interfaces..");

    @ArchTest
    static final ArchRule interfacesMustNotBypassApplicationToPersistence =
        noClasses().that().resideInAPackage("..interfaces..")
            .should().dependOnClassesThat().resideInAnyPackage(
                "..domain.repository..", "..infrastructure.persistence..", "com.example.app.persistence..");

    @ArchTest
    static final ArchRule controllersMustResideInInterfaces =
        classes().that().areAnnotatedWith(RestController.class)
            .should().resideInAnyPackage("..interfaces..", "..interfaces.rest..");

    // 按实际业务模块清单扩展：禁止跨模块穿透 interfaces / domain / infrastructure
    @ArchTest
    static final ArchRule ordersMustNotBypassInventoryApplicationFacade =
        noClasses().that().resideInAPackage("com.example.app.modules.orders..")
            .should().dependOnClassesThat().resideInAnyPackage(
                "com.example.app.modules.inventory.interfaces..",
                "com.example.app.modules.inventory.domain..",
                "com.example.app.modules.inventory.infrastructure..");

    @ArchTest
    static final ArchRule businessModulesMustBeFreeOfCycles =
        SlicesRuleDefinition.slices()
            .matching("com.example.app.modules.(*)..")
            .should().beFreeOfCycles();
}
```

### 2. Checkstyle 体积与参数护栏（可选推荐）

在 `maven-checkstyle-plugin` 配置 `ParameterNumber (max = 5)` 与 `FileLength (max = 400)` 绑定至 `verify` 阶段，自动拦截超长参数方法与巨型类。

## 五、验证命令

```bash
mvn test   # 若已启用 Checkstyle 插件并绑定至 verify 阶段，执行 mvn verify
```

确认 `ArchitectureRulesTest` 与标杆垂直切片集成测试全部通过。
