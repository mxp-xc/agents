# Python 选型推荐

技术栈未定时按本表给默认组合。每条一句话理由；版本以落地时 PyPI 稳定版为准。

## 后端

| 用途 | 推荐 | 理由 |
| --- | --- | --- |
| Web 框架 | FastAPI | 类型驱动，OpenAPI 自动生成，生态围绕 Pydantic |
| ORM | SQLAlchemy | 2.x 类型注解完善，与 Alembic 配套 |
| 数据校验 | Pydantic v2 | 当前稳定基线；v1 已停止维护 |
| HTTP 客户端 | httpx2 | httpx 的活跃维护分支（Pydantic 团队），同步异步同一套 API；原 httpx 停留在 0.28.1 |
| 迁移 | Alembic | SQLAlchemy 官方迁移工具 |
| 包管理 | uv | 安装快，锁文件稳定 |
| 测试 | pytest | 生态与插件最全 |

### httpx2 说明

- 包名与导入名都是 httpx2；与原 httpx 可共存，逐模块迁移（换成 `import httpx2`），依赖树里还在用 httpx 的库不受影响。
- HTTP/2 装 `httpx2[http2]`，命令行客户端在 `httpx2[cli]`。
- 新代码统一 httpx2；只有依赖库强制要求时保留 httpx。

### 组织方式

- Web 项目按 [fastapi.md](fastapi.md)，套用 [sqlalchemy.md](sqlalchemy.md) 与 [pydantic.md](pydantic.md)。
- 脚本/CLI 只用 ORM 按 [sqlalchemy.md](sqlalchemy.md)；以数据契约为核心按 [pydantic.md](pydantic.md)。
- 业务边界复杂时按 [ddd.md](../ddd.md)。

## 事实来源

- [httpx2 (PyPI)](https://pypi.org/project/httpx2/)
- [httpx 停更与 httpx2 分支背景](https://github.com/deepset-ai/haystack/issues/12593)
- [SQLAlchemy 发布记录](https://www.sqlalchemy.org/blog/)
- [Pydantic V3 计划](https://pydantic.dev/articles/pydantic-validation-next-steps)
