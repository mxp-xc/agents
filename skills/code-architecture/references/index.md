# 参考文件导航

按当前任务的架构档位与目标技术栈按需加载，不一次读完整个目录。

## 读取路由图

```text
开始任务
 │
 ├── 1. 必读基础
 │    └── architecture-principles.md        # 3 分支初始化、4 档架构选型、目录二分法、统一响应与异常、规则归属
 │
 ├── 2. 架构档位分支
 │    ├── 选定 L1 / L2 务实 DDD ─────────▶ ddd-guide.md (模块划分 4 判据、四层职责、跨模块协作、L1/L2 裁剪)
 │    └── 选定 极简平铺 / 轻量务实分层 ──▶ 跳过 ddd-guide.md
 │
 ├── 3. 技术栈特化（位于 stacks/ 子目录，按仓库实际语言加载）
 │    ├── Java 17/21 + Spring Boot ──────▶ stacks/java.md
 │    ├── Python / FastAPI / CLI ────────▶ stacks/python.md
 │    └── TypeScript (React / Node) ─────▶ stacks/typescript-web.md
 │
 └── 4. 落盘目标仓库规范
      └── coding-standards-template.md      # 生成或补齐目标仓库 docs/CODING_STANDARDS.md
```

## 文件职责速查

| 文件 | 何时读取 | 核心内容 |
| --- | --- | --- |
| [architecture-principles.md](architecture-principles.md) | 所有任务第一步必读 | 3 分支初始化决策树、未上线 vs 已上线策略、4 档架构选型矩阵、目录二分图、`ApiResponse` + `X-Trace-Id` + `BusinessException` + 点分层 `ErrorCode`、规则归属表、反过度设计 5 检 |
| [ddd-guide.md](ddd-guide.md) | 选定 L1 或 L2 务实 DDD 时 | `modules/*` 拆分 4 判据、四层内部结构与代码示例、跨模块事务/只读查询协作图、L1 vs L2 裁剪矩阵、假 DDD 反模式对比 |
| [coding-standards-template.md](coding-standards-template.md) | 准备生成或更新 `docs/CODING_STANDARDS.md` 时 | 目标仓库 `docs/CODING_STANDARDS.md` 标准章节与占位模板 |
| [stacks/java.md](stacks/java.md) | 目标项目含 Java / Spring Boot | `modules/` + 根包展平目录树、5 项起手选型、请求与异常调用树、正反模式对比、ArchUnit 护栏测试代码 |
| [stacks/python.md](stacks/python.md) | 目标项目含 Python / FastAPI / CLI | `app/` 轻量展平分层目录树、单向依赖图、`BusinessException` 拦截链路、`import-linter` + `ruff` + `pyrefly` 配置 |
| [stacks/typescript-web.md](stacks/typescript-web.md) | 目标项目含前端 Web 或 Node/TS 后端 | 前端 `app / features / shared` 组件与调用树、Node 后端 `modules/` + 展平横切树、ESLint 与 `dependency-cruiser` 规则 |

## 扩展约定

新增技术栈支持时，在 `stacks/` 子目录添加 `<stack>.md`（包含目录树、依赖图、统一响应/异常接入、可运行机械护栏配置及验证命令），并在上方路由图与表格中登记。
