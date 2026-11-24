# TypeScript（前端 Web / Node 后端）代码架构落地方案

按 **前端 Web 应用（React 等）** 与 **Node/TS 后端服务** 分别组织目录与护栏（通用原则见 [architecture-principles.md](../architecture-principles.md)，Node 后端四层细则见 [ddd-guide.md](../ddd-guide.md)）。

## 一、前端 Web 应用（`app / features / shared`）

包含登录态、多视图状态或异步请求的前端应用，按职责拆分为应用壳（`app/`）、业务特征域（`features/`）与无业务共享内核（`shared/`），禁止把路由、请求、鉴权与业务表格堆进单一 `App.tsx`。

### 1. 前端目录树与组件调用链

```text
src/
├── main.tsx
├── app/                         # 【应用壳与会话底座】路由表、全局 Provider、会话与请求代际守卫
│   └── session/
│       ├── sessionStore.ts      # 登录态、Token、登出清理
│       └── requestGuard.ts      # epoch / AbortController（账号切换时丢弃在途旧响应）
├── shared/                      # 【零业务耦合共享内核】严禁反向 import features/*
│   ├── api/client.ts            # 统一 HTTP 客户端（读 X-Trace-Id 响应头，解包 {code, message, data}）
│   ├── ui/                      # 通用基础 UI 组件
│   └── utils/                   # 纯无状态格式化/时间工具
└── features/                    # 【业务特征域】按业务垂直分包，跨 feature 严禁深层互引内部文件
    └── orders/
        ├── index.ts             # 对外唯一导出入口
        ├── api.ts               # 调用 shared/api/client + Zod 响应结构校验
        ├── model.ts             # 领域类型、状态枚举与纯派生计算函数
        ├── hooks/               # useOrders.ts（串联 api.ts、异步状态与 requestGuard）
        └── components/          # 纯渲染与交互组件（严禁直接调裸 fetch）
```

```text
前端数据流向：
  <OrderListPage> (features/orders/components/)
    └── useOrders() (features/orders/hooks/)
          ├── requestGuard.captureEpoch() (app/session/)
          └── fetchOrders() (features/orders/api.ts)
                ├── httpClient.get() (shared/api/client.ts)
                │     ├── 提取响应头 X-Trace-Id
                │     └── 校验 body.code === "SUCCESS"（失败转统一业务错误提示）
                └── OrderListSchema.parse(body.data)
```

### 2. 前端代码形态对比

```diff
 // features/orders/components/OrderList.tsx
 export function OrderList() {
-  // 反例：组件内直接裸调 fetch、手写 Token 头、无代际隔离与结构校验
-  useEffect(() => {
-    fetch("/api/orders", { headers: { Authorization: token } })
-      .then(r => r.json())
-      .then(res => setOrders(res.data));
-  }, []);

+  // 正例：组件只消费同域 hook 与纯模型函数
+  const { orders, isLoading, error, cancelOrder } = useOrders();
+  return <OrderTable items={orders} onCancel={cancelOrder} />;
 }
```

---

## 二、Node / TypeScript 后端服务（`modules/` + 展平横切）

业务域统一收拢在 `src/modules/` 下按界限上下文垂直分包（内部四层同构，由 `index.ts` 暴露对外门面）；非业务横切与无框架公共类型直接展平在 `src/` 根目录。

### 1. 后端目录树与依赖边界

```text
src/
├── bootstrap.ts                 # 集中装配：依赖注入、中间件、全局异常拦截器、路由挂载
│
├── modules/                     # 【1. 业务区】唯一业务入口，跨模块仅通过对方 index.ts (application 门面) 协作
│   ├── orders/
│   │   ├── index.ts             # 仅导出 application 门面与公开事件类型
│   │   ├── interfaces/          # HTTP 路由/Controller + Zod/Valibot 请求响应 Schema
│   │   ├── application/         # UseCase 用例编排、事务边界、Command/Query
│   │   ├── domain/              # 聚合根、值对象、状态枚举、OrderErrorCode、Repository 接口
│   │   └── infrastructure/      # Drizzle/Prisma/SQL 仓储实现与持久映射
│   └── inventory/
│       ├── index.ts
│       ├── interfaces/
│       ├── application/
│       ├── domain/
│       └── infrastructure/
│
├── config/                      # 【2. 带框架横切区】环境变量、OpenAPI、日志、DB 连接配置
├── middlewares/                 # traceMiddleware (写 X-Trace-Id 响应头)、authMiddleware
├── persistence/                 # 公共事务包装、数据库基建（cron/、mq/ 按需同级展开）
│
├── exceptions/                  # 【3. 异常体系（纯语义层与框架拦截器分离）】
│   ├── business-error.ts        # [无框架] ErrorCode 接口、BaseErrorCode、唯一默认 BusinessError
│   └── handler/                 # [带框架] 全局异常拦截中间件（默认返回 HTTP 200 + ApiResponse 失败体）
│
├── types/                       # 【4. 无框架公共类型】禁用 common 垃圾桶命名
│   ├── enums/                   # 跨模块公共枚举
│   ├── vo/                      # Branded ID、时间区间等不可变值对象
│   └── dto/                     # ApiResponse<T>({code, message, data})、PageQuery、PageResult
└── utils/                       # 【5. 无框架纯工具】纯无状态通用函数
```

### 2. 统一响应与唯一默认 `BusinessError` 代码模板

```ts
// 1. src/types/dto/api-response.ts（零框架依赖，traceId 走 X-Trace-Id 响应头，不进 data）
export interface ApiResponse<T> {
  readonly code: string;
  readonly message: string;
  readonly data: T | null;
}

export const ApiResponse = {
  ok<T>(data: T): ApiResponse<T> {
    return { code: "SUCCESS", message: "success", data };
  },
  fail(code: string, message: string): ApiResponse<null> {
    return { code, message, data: null };
  },
};

// 2. src/exceptions/business-error.ts（零框架依赖）
export interface ErrorCode {
  readonly code: string;
  readonly defaultMessage: string;
}

export const BaseErrorCode = {
  SUCCESS: { code: "SUCCESS", defaultMessage: "success" },
  COMMON_PARAM_INVALID: { code: "COMMON.PARAM.INVALID", defaultMessage: "请求参数不合法" },
  AUTH_UNAUTHENTICATED: { code: "AUTH.UNAUTHENTICATED", defaultMessage: "未登录或身份凭证无效" },
  AUTH_FORBIDDEN: { code: "AUTH.FORBIDDEN", defaultMessage: "无权限执行该操作" },
  COMMON_RESOURCE_NOT_FOUND: { code: "COMMON.RESOURCE.NOT_FOUND", defaultMessage: "请求的资源不存在" },
  COMMON_SYSTEM_ERROR: { code: "COMMON.SYSTEM.ERROR", defaultMessage: "系统繁忙，请稍后重试" },
} as const satisfies Record<string, ErrorCode>;

export class BusinessError extends Error {
  constructor(
    public readonly errorCode: ErrorCode,
    message = errorCode.defaultMessage,
  ) {
    super(message);
    this.name = "BusinessError";
  }
}

// 3. src/modules/risk/domain/enums/risk-error-code.ts（各业务模块独立维护两层或三层全大写点分层码）
export const RiskErrorCode = {
  RISK_INVALID: { code: "RISK.INVALID", defaultMessage: "风控配置参数无效" },
  RISK_CREATE_ERROR: { code: "RISK.CREATE.ERROR", defaultMessage: "风控规则创建失败" },
  RISK_UPDATE_ERROR: { code: "RISK.UPDATE.ERROR", defaultMessage: "风控规则更新失败" },
} as const satisfies Record<string, ErrorCode>;
```

---

## 三、机械护栏：ESLint + dependency-cruiser

### 1. ESLint 结构约束（`eslint.config.mjs`）

拦截巨型上帝文件与跨 feature 深层导入：

```js
export default [
  {
    rules: {
      "max-lines": ["error", { max: 350, skipBlankLines: true, skipComments: true }],
      "no-restricted-imports": ["error", {
        patterns: [
          {
            group: ["**/features/*/**", "!**/features/*/index"],
            message: "禁止跨 feature 深层导入内部实现，请经模块 index 出口或提升至 shared/。"
          }
        ]
      }],
    },
  },
];
```

### 2. dependency-cruiser 依赖红线（`.dependency-cruiser.cjs`）

```text
[规则 1] modules/*/domain/               ──✕──▶ interfaces / application / infrastructure / 带框架横切区
[规则 2] types / utils / business-error  ──✕──▶ modules / 带框架横切区
[规则 3] modules/*/infrastructure/       ──✕──▶ modules/*/interfaces/
[规则 4] modules/*/interfaces/           ──✕──▶ domain/repository / infrastructure / persistence
[规则 5] modules/<A>/                    ──✕──▶ modules/<B>/(interfaces|domain|infrastructure)/  且无循环依赖
```

```js
module.exports = {
  forbidden: [
    {
      name: "domain-must-not-depend-on-outer-layers-or-framework",
      severity: "error",
      from: { path: "^src/modules/[^/]+/domain/" },
      to: {
        path: "^src/(modules/[^/]+/(interfaces|application|infrastructure)|config|middlewares|persistence|exceptions/handler)/",
      },
    },
    {
      name: "pure-types-utils-exceptions-must-stay-independent",
      severity: "error",
      from: { path: "^src/(types/|utils/|exceptions/[^/]+\\.ts$)" },
      to: { path: "^src/(modules|config|middlewares|persistence|exceptions/handler)/" },
    },
    {
      name: "infrastructure-must-not-depend-on-interfaces",
      severity: "error",
      from: { path: "^src/modules/[^/]+/infrastructure/" },
      to: { path: "^src/modules/[^/]+/interfaces/" },
    },
    {
      name: "interfaces-must-not-depend-on-repositories-or-persistence",
      severity: "error",
      from: { path: "^src/modules/[^/]+/interfaces/" },
      to: { path: "^src/(modules/[^/]+/(domain/repository|infrastructure)|persistence)/" },
    },
    {
      name: "no-cross-module-internals",
      severity: "error",
      from: { path: "^src/modules/([^/]+)/" },
      to: {
        path: "^src/modules/[^/]+/",
        pathNot: ["^src/modules/$1/", "^src/modules/[^/]+/index\\.ts$"],
      },
    },
    {
      name: "no-module-cycles",
      severity: "error",
      from: { path: "^src/modules/" },
      to: { circular: true },
    },
  ],
};
```

## 四、验证命令

```bash
bun run lint && bun run build && bun run test
```
