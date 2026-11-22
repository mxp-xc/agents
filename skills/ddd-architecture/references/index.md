# 参考索引

本目录包含语言无关的务实 DDD 设计指南、规范模板与各技术栈特化落地参考。

## 读取顺序

1. **通用必读（所有任务均须读取）**：
   - [ddd-tactical-guide.md](ddd-tactical-guide.md)：四层职责与依赖红线、L1/L2 梯度选型、规则机制选型表、未上线整改与已上线演进策略、反过度设计清单。
   - [coding-standards-template.md](coding-standards-template.md)：落盘到目标仓库根目录的 `CODING_STANDARDS.md` 模板。
2. **技术栈特化（按目标项目语言与框架读取）**：
   - [java-spring.md](java-spring.md)：Java 17/21 + Spring Boot 分包骨架、选型拍板、正反模式与 ArchUnit / Checkstyle 机械护栏。
   - [typescript-web.md](typescript-web.md)：TypeScript 前端 Web 应用（React 等）与 Node/TS 后端分层结构、会话/状态隔离、ESLint 与 dependency-cruiser 护栏。
   - [python.md](python.md)：Python（FastAPI / 业务服务 / CLI）分层骨架、Pydantic/领域边界、import-linter 与 ruff 护栏。

## 扩展约定

- 新增技术栈或框架支持时，在本目录新增 `<lang-framework>.md` 文件（包含目录骨架、关键选型、正反模式及可运行的机械护栏与验证命令），并在上方列表登记适用场景。
