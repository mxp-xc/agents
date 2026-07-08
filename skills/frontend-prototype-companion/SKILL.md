---
name: frontend-prototype-companion
description: Use when asked to create UI prototypes, mockups, visual comparisons, or variants for an existing frontend project, including requests like "画原型图", "mockup", or "visual companion". Build previewable prototypes from current repo components, styles, routes, fixtures, and dev tooling; keep prototype files isolated and ignored; record minimal touchpoints; promote and clean up after selection. Do not use for greenfield apps, text-only specs, or raster image generation.
---

# Frontend Prototype Companion

在已有前端项目里创建代码支撑的 UI 原型。原型要复用当前项目的组件、样式、数据形状和开发工具，避免画出无法落地的静态稿。

## Rules

- 先识别框架、package manager、入口、路由、组件目录、样式系统、mock/fixture 和预览方式。
- 原型文件默认放在 `temp/prototypes/<topic>/`，并确保 `.gitignore` 覆盖 `/temp/` 或 `/temp/prototypes/`。
- 默认让原型 import 项目代码，不让生产应用 import 原型；不要假设 `src/*` 或 workspace package 能直接引用 `temp/*`。
- 非原型目录只允许最小接入点、配置或 ignore 改动；所有这类改动都必须标记并写入 manifest 的 `Touchpoints`。
- 默认使用 fixture、mock handler 或只读测试数据；真实写操作、支付、邮件、删除、部署和生产变更不属于原型默认行为。
- 原型至少考虑正常、空状态、loading、错误、长文本和移动视口；范围很小时可按风险裁剪。

## Carrier Order

1. **Sidecar**：首选。在 `temp/prototypes/<topic>/` 创建 preview app、story、playground 或局部入口，由它 import `src/*` 或 `packages/<workspace>/*` 的现有代码。
2. **Marked adapter**：必须嵌进现有 dev server 时使用。只添加极薄 route/adapter/script，并用 `PROTOTYPE_ENTRY: temp/prototypes/<topic>` 标记。
3. **In-source fallback**：工具链禁止从 `temp` 运行或 import 时使用。目录为 `src/prototype-lab/<topic>/` 或 `packages/<workspace>/src/prototype-lab/<topic>/`，并确保对应 ignore 规则存在。

选载体前先判断 bundler/framework、`tsconfig include`、workspace boundary、dev server root 和 lint/import 规则；不确定时不要硬接入。

## Workflow

1. 检查项目结构和可复用资产，读现有组件 API 后再写原型。
2. 创建原型目录，确认 ignore 规则，并维护 `prototype-manifest.md`。
3. 用现有组件和 mock/fixture 组合原型；需要比较时用 tabs、segmented control 或并列视图呈现 2-3 个变体。
4. 启动预览并自动验证渲染，修复空白页、重叠、溢出、控制台错误和明显样式断裂。
5. 交付预览 URL、carrier、touchpoints、复用内容和验证结果。
6. 方向确定后，将可复用代码迁移到正式位置，替换 mock/fixture，并删除原型目录、adapter、fallback 和其他 prototype-only 改动。

## Manifest

`prototype-manifest.md` 保持短小，只记录原型定位和清理所需信息：

```text
Topic: <topic>
Prototype root: temp/prototypes/<topic>/
Preview: <command or url>
Carrier: sidecar | marked-adapter | in-source-fallback
Touchpoints:
- <non-prototype file>: <why it changed>
Verification:
- <command or viewport check>
Promotion target:
- <planned production location>
Cleanup:
- <items to remove after decision>
```

临时接入点示例：

```ts
// PROTOTYPE_ENTRY: temp/prototypes/<topic>
// Remove after prototype decision.
```

## Verification

- 能跑则运行相关 `lint`、`typecheck`、测试或构建；范围较小时选最小有效命令。
- 前端渲染必须自动验证；按项目约定优先 `playwright-cli`，不要把“打开浏览器看看”当作验收。
- 截图、trace、临时报告等验证产物放在 `temp/prototypes/<topic>/artifacts/`。
- 自动化受限时，说明阻塞，并静态复读改动文件和预览入口。

## Constraints

- 不为原型新增永久依赖，不重写设计系统，不把 prototype-only 代码混入生产路径。
- 原型文件默认不进入版本控制；需要保留的产物应先迁移到正式代码位置，再纳入版本控制。
- 不创建与项目风格脱节的独立静态页面；仅在现有项目无法承载原型时，才允许临时降级并说明原因。
- 不在应用可见界面写原型说明文案；必要的变体切换控件应像产品内工具一样克制。
