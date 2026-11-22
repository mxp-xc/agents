# Java + Spring Boot 务实 DDD 落地方案

适用于 JDK 17/21 + Spring Boot 3/4 服务。默认采用**按界限上下文垂直分包（模块化单体）+ 内部四层**的 **L1 轻量务实 DDD**。

## 一、推荐包骨架（模块化单体默认）

只要业务规格包含 **2 个及以上核心实体/主表或独立生命周期模块**（例如账号、库存、订单），必须先按业务域拆为独立顶层包，每个业务模块内部保持同构的四层，**禁止合并成单一 Controller / Service / Mapper**。以 `account`（账号）、`inventory`（库存）与 `orders`（订单）并存为例：

```text
com.example.app/
├── Application.java                       # 启动入口
├── config/                                # 集中装配：OpenAPI、Clock、Web/Jackson、ORM 插件配置
├── shared/
│   ├── domain/                            # 跨上下文值对象基元、时间工具（非业务杂物间）
│   ├── exception/                         # BusinessException 根异常及语义子类（InvalidInput/NotFound/Conflict/Forbidden/Unauthorized）
│   └── persistence/                       # BaseEntity（审计字段/软删）、公共写锁/事务辅助（如 WriteTransaction）
├── infrastructure/                        # 跨上下文横向 Web/安全基建
│   └── web/                               # AuthFilter、ActorContext、TraceFilter、GlobalExceptionHandler
├── account/                               # 【界限上下文 1】账号与资格，向其他模块暴露 Application 门面
│   ├── interfaces/
│   ├── application/
│   │   └── AccountApplicationService.java
│   ├── domain/
│   └── infrastructure/
├── inventory/                             # 【界限上下文 2】与 orders 同构，对外只暴露 Application 门面
│   ├── interfaces/
│   ├── application/
│   │   └── InventoryApplicationService.java
│   ├── domain/
│   └── infrastructure/
└── orders/                                # 【界限上下文 3】先业务，后分层
    ├── interfaces/
    │   ├── rest/                          # OrderController（只做协议转换、参数绑定、调 Application）
    │   └── dto/
    │       ├── request/                   # CreateOrderRequest.java、CancelOrderRequest.java（一类一文件，带 @Valid）
    │       └── response/                  # OrderResponse.java、PageResponse.java（共享分页可放 shared）
    ├── application/
    │   ├── OrderApplicationService.java   # 用例编排、@Transactional 边界、角色/归属检查（跨模块仅调用对方 Application 门面）
    │   ├── command/                       # CreateOrderCommand.java（入参 >3 个时封装为不可变 Command/Query）
    │   └── query/                         # OrderQueryService.java（只读列表/分页投影）
    ├── domain/
    │   ├── model/                         # Order.java、OrderItem.java（封装状态流转与不变量）
    │   ├── enums/                         # OrderStatus.java（含 canTransitionTo 等规则）
    │   ├── exception/                     # OrderStateException.java（继承 shared.exception.BusinessException）
    │   └── repository/                    # OrderRepository.java（面向领域对象的仓储端口）
    └── infrastructure/
        └── persistence/
            ├── OrderRepositoryImpl.java   # 实现 domain.repository.OrderRepository，内部调用 Mapper/JPA
            ├── mapper/                    # MyBatis-Plus Mapper 或 Spring Data JPA Repository
            └── po/                        # L2 时独立 PO；L1 模型一致时可酌情复用并严格隔离注解泄漏
```

- **单域切换条件（极窄）**：仅当**用户明确要求**单聚合微型服务（全系统只有一个核心实体与主表）或采用 Maven 多模块物理分包时，才可省去顶层业务模块包。多业务域或默认单体项目一律保持上述“先业务、后分层”。
- **跨模块协作与共享事务**：在 Spring Boot 单体中，`OrderApplicationService`（标注 `@Transactional`）调用 `InventoryApplicationService` 或 `AccountApplicationService` 的门面方法时，会自动参与同一数据库事务（默认 `Propagation.REQUIRED`）；若需执行数据库全局写锁前置语句或统一事务包装，放在 `shared/persistence/` 中供各业务层复用，**严禁将多业务表揉进单一上帝 `Store`/`Mapper` 破坏模块边界**。

## 二、起手一次拍板的关键选型

写第一行业务代码前一次性确定以下 5 项，避免中途返工重写：

1. **持久层选型**：直接确定 **MyBatis-Plus**（偏 SQL 可控与复杂联表）或 **Spring Data JPA**（偏标准对象图持久化），禁止手写裸 JDBC 模板拼接增删改查。
2. **声明式参数校验**：引入 `spring-boot-starter-validation`，Controller 参数使用 `@Valid`，DTO 字段直接标注 `@NotBlank`、`@NotNull`、`@Size` 等约束，并配合 `@RestControllerAdvice` 统一返回结构化字段错误。
3. **集中鉴权占位**：哪怕首期只有简化登录或固定测试账号，也必须在 `infrastructure/web/`（或统一 `web/` 横切入口）建好 `AuthFilter`（或 `HandlerInterceptor`）与 `ActorContext`（可配合 `HandlerMethodArgumentResolver`）统一提取并解析身份头/Token，Controller 方法签名禁止重复使用 `@RequestHeader` 接收裸身份字符串再手工解析；需要校验实时账号状态/角色或纳入写事务时，由业务 `application` 层基于已解析的身份调用账号模块门面校验；OpenAPI 文档需展示鉴权请求头时，在 `config/` 中通过 `OpenAPI` SecurityScheme 或 `OperationCustomizer` 统一声明。
4. **语义化异常树**：`shared/exception/` 定义通用 `BusinessException` 基类及语义分类子类（`InvalidInputException`、`UnauthorizedException`、`ForbiddenException`、`NotFoundException`、`ConflictException`），各业务模块直接抛出对应语义异常并传入本模块稳定 `errorCode`（或定义本模块异常子类），**禁止把全系统所有模块的错误码集中硬编码在同一个枚举类里导致跨模块耦合**；**由 `GlobalExceptionHandler` 唯一负责把语义异常映射为 HTTP 400/401/403/404/409**。
5. **OpenAPI 文档**：引入 `springdoc-openapi-starter-webmvc-ui`，DTO 与 Controller 使用 `@Schema`、`@Operation` 描述契约，保持接口文档随代码自动同步。

## 三、关键正反模式

| 关注点 | 推荐做法（正例） | 禁止做法（反例） |
| --- | --- | --- |
| **DTO 组织** | `CreateOrderRequest.java`、`OrderResponse.java` 独立成类，字段带 `@NotNull`/`@Schema` | 把全模块十几个嵌套 `record` 塞进单一 `*Contract.java` 聚合文件 |
| **状态流转** | `OrderStatus` 枚举内定义 `canTransitionTo(target)` 或实体方法 `order.cancel(reason, now)` | 全项目散落 `"CONFIRMED".equals(row.status)` 与分散的状态判断 |
| **仓储边界** | `OrderRepository` 接收领域模型或 `OrderQuery`，返回领域对象或只读投影 | `Repository` 直接 `import` Controller DTO，并在持久层校验分页参数或拼接面向前端的报错文案 |
| **异常表达** | `throw new ConflictException("ORDER_ALREADY_PAID", ...)` | 在 `domain` 或 `infrastructure/persistence` 里写 `throw new ApiError(409, ...)` |
| **长参数方法** | 方法参数超过 4 个时引入不可变 `Command` / `Query` record | Controller 或 Service 签名连续传入 6~8 个零散字符串和基础类型 |
| **身份解析** | `AuthFilter` / `HandlerInterceptor` 统一解析身份头/Token 并写入 `ActorContext`（或经 `HandlerMethodArgumentResolver` 注入强类型身份），鉴权头文档在 `config/` 统一声明 | 在多个 Controller 方法签名重复使用 `@RequestHeader` 接收裸身份字符串并在方法体内逐一解析 |

## 四、机械护栏：ArchUnit（必选）+ Checkstyle（推荐）

### 1. ArchUnit 依赖方向与跨模块隔离护栏（随 `mvn test` 自动运行）

在 `pom.xml` 引入测试依赖 `com.tngtech.archunit:archunit-junit5`（以当前 Maven Central 稳定版为准），在 `src/test/java/<basePackage>/ArchitectureRulesTest.java` 中固化**三类必选规则**：（1）四层依赖方向；（2）各业务模块跨模块隔离（禁止绕过对方 `..application..` 门面访问对方 `..interfaces..`/`..domain..`/`..infrastructure..`）；（3）禁止业务模块间循环依赖。

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
    static final ArchRule domainMustNotDependOnOuterLayers =
        noClasses().that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage("..interfaces..", "..application..", "..infrastructure..");

    @ArchTest
    static final ArchRule domainMustNotDependOnWebOrSqlDrivers =
        noClasses().that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage("org.springframework.web..", "jakarta.servlet..", "java.sql..");

    @ArchTest
    static final ArchRule infrastructureMustNotDependOnInterfaces =
        noClasses().that().resideInAPackage("..infrastructure..")
            .should().dependOnClassesThat().resideInAPackage("..interfaces..");

    @ArchTest
    static final ArchRule interfacesMustNotBypassApplicationToPersistence =
        noClasses().that().resideInAPackage("..interfaces..")
            .should().dependOnClassesThat().resideInAPackage("..infrastructure.persistence..");

    @ArchTest
    static final ArchRule controllersMustResideInInterfacesRest =
        classes().that().areAnnotatedWith(RestController.class)
            .should().resideInAPackage("..interfaces.rest..");

    // 模块化单体跨模块隔离（按实际业务模块清单扩展，禁止绕过对方 Application 门面穿透内部实现）
    @ArchTest
    static final ArchRule ordersMustNotBypassInventoryApplicationFacade =
        noClasses().that().resideInAPackage("com.example.app.orders..")
            .should().dependOnClassesThat().resideInAnyPackage(
                "com.example.app.inventory.interfaces..",
                "com.example.app.inventory.domain..",
                "com.example.app.inventory.infrastructure..");

    // 禁止业务模块间循环依赖
    @ArchTest
    static final ArchRule businessModulesMustBeFreeOfCycles =
        SlicesRuleDefinition.slices()
            .matching("com.example.app.(*)..")
            .should().beFreeOfCycles();
}
```

### 2. 可选辅助检查（防大文件与超长参数列表）

- 在 `maven-checkstyle-plugin` 中配置 `ParameterNumber`（如 `max = 5`）和 `FileLength`（如 `max = 400`），绑定到 `verify` 或 `validate` 阶段，迫使超长参数和巨型类在编译构建阶段自动暴露并收拢为值对象/Command/模块拆分。

## 五、验证方式

- 执行 `mvn test`（或 `mvn verify`）：确认 `ArchitectureRulesTest` 与标杆垂直切片集成测试全部通过。
- 人为试错检验：若在 `infrastructure` 临时引入 `interfaces` DTO 或在 `domain` 引入 `org.springframework.web`，`ArchitectureRulesTest` 必须立即失败报错。
