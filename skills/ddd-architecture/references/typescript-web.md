# TypeScript（前端 Web / Node 后端）务实 DDD 落地方案

区分 **前端 Web 应用（如 React）** 与 **Node/TS 后端服务** 两种形态，核心原则一致：**按业务域垂直划分模块、状态与传输边界明确、单文件与跨模块导入受静态工具约束**。

## 一、前端 Web 应用（React / Vite 等）

前端即使属于后台管理或联调工作台，只要包含登录态、异步状态、多业务视图或乐观/重试逻辑，就必须建立清晰边界，严禁把路由、请求、鉴权与所有表格堆进单一 `App.tsx`。

### 推荐目录骨架

```text
src/
├── app/                         # 应用壳、路由表、全局 Provider（只做装配，不放业务请求与状态机）
├── shared/
│   ├── api/                     # 统一 HTTP 客户端（拦截器、TraceId、错误解包、基础响应校验）
│   ├── ui/                      # 无业务语义的通用基础组件
│   └── lib/                     # 时间、格式化等纯工具函数
├── session/                     # 【横切认证与会话域】
│   ├── sessionStore.ts          # 当前身份、token 刷新、登出
│   └── requestGuard.ts          # 账号切换代际（epoch）/ AbortController 隔离，拦截旧账号迟到响应
├── features/                    # 【业务特征域】按领域垂直分包
│   └── orders/
│       ├── api.ts               # 该域后端契约调用与 Zod/结构校验（进页面前校验响应合法性）
│       ├── model.ts             # 前端领域类型、状态枚举、状态转换/派生计算（纯函数）
│       ├── hooks/               # useOrders.ts、useCreateOrder.ts（串联异步状态与 sessionGuard）
│       └── components/          # 仅负责渲染与用户交互，不直接调 fetch
└── main.tsx
```

### 前端核心约束

1. **会话与请求代际隔离集中化**：Token 自动刷新、登出清理、账号切换时丢弃在途旧请求的响应，全部由 `session/` 统一拦截或提供 `isCurrentSession(epoch)` 守卫，不得分散在各页面的 `useEffect` 里重复判断。
2. **页面零裸 `fetch`**：`features/*/components/` 只能调用同域 `hooks/` 或 `model.ts`；响应进入状态前在 `api.ts` 完成结构校验，防御畸形返回破坏页面渲染。
3. **跨 feature 隔离**：`features/a` 不得深层导入 `features/b/components/*` 内部实现，仅允许通过模块根出口或提升为 `shared/` 组件共享。

---

## 二、Node / TypeScript 后端服务（模块化单体默认）

先按界限上下文垂直分包，每个模块内部再分四层，并通过模块出口 `index.ts` 暴露协作能力：

```text
src/
├── bootstrap.ts                 # 集中装配：环境变量、DB/连接池、依赖注入、路由挂载
├── shared/
│   ├── errors.ts                # AppError 基类及语义子类（ValidationError/ConflictError/NotFoundError...）
│   └── types.ts                 # Branded ID、Result/分页基元等
├── infrastructure/
│   └── http/                    # 鉴权中间件、Trace 中间件、全局异常转 HTTP 状态码处理器
└── modules/
    ├── orders/                  # 【界限上下文 1】先业务，后分层
    │   ├── index.ts             # 仅导出对外门面（Application UseCase / 公开事件类型）
    │   ├── interfaces/          # HTTP 路由/Controller + Zod/Valibot Schema（输入输出契约）
    │   ├── application/         # UseCase 用例编排、事务边界、Command/Query 类型
    │   ├── domain/              # 领域实体/聚合、强类型联合状态、领域不变量、Repository 接口
    │   └── infrastructure/      # Drizzle/Prisma/SQL 仓储实现与映射
    └── inventory/               # 【界限上下文 2】同构四层，跨模块仅通过 index.ts 协作
        ├── index.ts
        ├── interfaces/
        ├── application/
        ├── domain/
        └── infrastructure/
```

- 后端关键规则：输入验证由 `interfaces` 层 Schema 库声明完成；`domain` 严禁引用 Express/Fastify/Hono 请求对象或 ORM Client；异常在 `domain`/`application` 以语义化 `Error` 子类抛出，在 `infrastructure/http/` 统一映射协议错误码。

---

## 三、机械护栏：ESLint 结构约束 + dependency-cruiser

### 1. ESLint 规则（防巨型上帝文件、超长参数与跨层越界导入）

在 `eslint.config.*` 中加入以下硬性约束（按项目目录调整路径匹配）：

```js
export default [
  {
    rules: {
      // 阻止单文件膨胀成上千行上帝组件（如巨型 App.tsx）
      "max-lines": ["error", { max: 350, skipBlankLines: true, skipComments: true }],
      // 超过 4 个参数强制收拢为具名参数对象或 Command/Query 类型
      "max-params": ["error", 4],
      // 禁止业务组件直接绕过 api 客户端使用裸 fetch，或跨 feature 深层导入
      "no-restricted-imports": ["error", {
        patterns: [
          {
            group: ["**/features/*/**", "!**/features/*/index"],
            message: "禁止跨业务模块深层导入内部实现，请通过模块入口或提升至 shared/。"
          }
        ]
      }],
    },
  },
];
```

### 2. dependency-cruiser 依赖方向检查（后端或复杂前端推荐）

在 `.dependency-cruiser.cjs` 中固化分层规则，接入 `package.json` 的 `lint:arch` 脚本：

```js
module.exports = {
  forbidden: [
    {
      name: "domain-must-not-depend-on-outer-layers",
      severity: "error",
      from: { path: "^src/.*/domain/" },
      to: { path: "^src/.*/(interfaces|application|infrastructure)/" },
    },
    {
      name: "infrastructure-must-not-depend-on-interfaces",
      severity: "error",
      from: { path: "^src/.*/infrastructure/" },
      to: { path: "^src/.*/interfaces/" },
    },
    {
      name: "interfaces-must-not-depend-on-infrastructure-persistence",
      severity: "error",
      from: { path: "^src/.*/interfaces/" },
      to: { path: "^src/.*/infrastructure/" },
    },
    {
      name: "no-cross-module-internals",
      severity: "error",
      from: { path: "^src/modules/([^/]+)/" },
      to: {
        path: "^src/modules/(?!\\1/)[^/]+/(interfaces|domain|infrastructure)/",
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

## 四、验证方式

- 运行类型检查、构建、规范检查与测试（按项目工具链使用 `bun` / `pnpm` / `npm`，如 `bun run lint && bun run build && bun run test`）。
- 若未引入 `dependency-cruiser`，确保 ESLint `no-restricted-imports` + `max-lines` 已对所有 `src/` 文件生效并返回非零退出码阻断违规。
