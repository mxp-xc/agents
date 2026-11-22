# Python（FastAPI / 业务服务 / CLI）务实分层落地方案

参考 `fastapi-fullstack` 等现代 FastAPI 工程实践，Python 服务默认采用**轻量务实展平分层**（直接按职责横向分层，不做按域重型四层套娃），配套 `uv` + `pyproject.toml` + `app/`（库项目用 `src/<pkg>/`）。纯胶水脚本或单表极简工具直接降级最小结构；仅当超大型项目演进为多界限上下文且需要强物理隔离（L2）时，再拆分为按域独立包。

## 一、推荐目录骨架（轻量务实展平分层）

```text
project/
├── pyproject.toml               # 依赖、ruff 与 import-linter 契约配置
├── app/                         # 库项目用 src/<pkg>/，应用默认 app/
│   ├── main.py                  # 启动与集中装配：创建 FastAPI/CLI 实例、挂中间件、异常处理器与路由
│   ├── core/                    # 【应用核心配置与安全基建】
│   │   ├── config.py            # pydantic-settings 环境变量配置
│   │   ├── security.py          # 鉴权、Token/密码校验（按需）
│   │   └── middleware.py        # TraceId、请求日志、CORS 等中间件（按需）
│   ├── api/                     # 【接口接入层】HTTP 路由 / CLI 命令，只做输入解析、鉴权依赖、调 services
│   │   ├── router.py            # 聚合各业务子路由
│   │   ├── deps.py              # 集中鉴权、当前操作者、DB Session 等依赖注入
│   │   └── routes/              # 按业务资源拆路由文件（如 orders.py、inventory.py）
│   ├── services/                # 【业务逻辑与用例层】按业务资源拆文件（orders.py、inventory.py）
│   │                            # 负责事务边界、状态流转、业务校验与跨资源协调
│   ├── repositories/            # 【数据访问层】按业务资源拆文件，隔离 SQLAlchemy/SQLModel 查询细节
│   ├── schemas/                 # 【API 契约层】Pydantic v2 请求与响应 Schema（带 Field(description=...)）
│   ├── db/                      # 【数据库引擎与表模型】
│   │   ├── session.py           # Engine / Session / UnitOfWork
│   │   └── models/              # SQLAlchemy / SQLModel ORM 表模型（按业务资源拆文件）
│   ├── exceptions/              # 【异常体系】纯语义异常与协议处理器分离
│   │   ├── errors.py            # BusinessError 基类及语义子类（零框架依赖）
│   │   └── handlers.py          # FastAPI 全局异常处理器（映射 HTTP 状态码）
│   ├── types/                   # 【通用类型与传值】零框架依赖，按需创建，不用 common 泛化命名
│   │   ├── enums.py             # 公共 StrEnum 枚举（强类型状态与分类）
│   │   ├── vo.py                # 不可变值对象（如时间区间、金额 dataclass）
│   │   └── dto.py               # 通用分页查询/结果等跨处传值结构
│   └── utils/                   # 【纯通用工具】纯无状态工具函数（零框架、跨处复用才建）
└── tests/
    ├── architecture/            # 架构与导入方向检查入口（可选）
    ├── unit/                    # 内存 Fake / Mock 仓储测 services 核心业务规则
    └── integration/             # TestClient + 真实数据库测端到端行为
```

- **按需扩展技术目录**：若项目需要异步任务队列、CLI 管理命令或外部网关客户端，可直接在 `app/` 下同级增设 `worker/`、`commands/`、`clients/`；无实际需求时不预建空目录。

## 二、关键约束与正反模式

1. **单向依赖与 `services/` 洁净度**：严格保持 `api → services → repositories → db`。`services/` 与 `exceptions/errors.py`、`types/`、`utils/` 内**严禁导入 FastAPI 请求对象（`Request`、`Depends`、`HTTPException`）或 `app.api`**；`repositories/` 与 `db/` 严禁反向导入 `api/`、`services/` 或 `schemas/`；`types/`、`utils/`、`exceptions/errors.py` 严禁反向导入业务层或 `core/`、`exceptions/handlers.py`。
2. **契约（`schemas/`）与表模型（`db/models/`）分离**：`schemas/` 用 Pydantic v2 定义对外输入校验与输出投影；`db/models/` 仅表达数据库表结构与约束。禁止路由直接透传 ORM 表对象，也禁止把 Pydantic 请求模型直接贯穿进持久化查询拼装。
3. **事务与异常边界**：数据库 `Session` 或 `UnitOfWork` 在 `services/` 用例入口管理事务边界，不泄漏到路由手写零散提交；底层或业务异常在 `services/`、`repositories/` 统一以 `exceptions/errors.py` 语义化异常抛出，由 `exceptions/handlers.py` 唯一映射为 HTTP 状态码或 CLI 退出码，不散落 `HTTPException(status_code=...)`。
4. **强类型枚举与全局目录节制**：核心状态与分类使用 `StrEnum`，状态合法性判断收拢在对应 `services/` 或 `types/vo.py` / 领域值对象中；单业务资源私有的助手机制留在对应服务模块内，跨多处复用且零框架依赖的才放 `types/` 或 `utils/`，禁止堆出 `common/` 杂物桶。

## 三、机械护栏：import-linter + ruff

### 1. `import-linter` 分层契约（放入 `pyproject.toml`）

```toml
[tool.importlinter]
root_package = "app"

[[tool.importlinter.contracts]]
name = "Layered architecture dependency"
type = "layers"
layers = [
    "app.api",
    "app.services",
    "app.repositories",
    "app.db",
]
exhaustive = false

[[tool.importlinter.contracts]]
name = "Services must not depend on web framework or api"
type = "forbidden"
source_modules = ["app.services"]
forbidden_modules = [
    "app.api",
    "app.exceptions.handlers",
    "fastapi",
    "starlette",
]

[[tool.importlinter.contracts]]
name = "Repositories and db must not depend on api, services, or schemas"
type = "forbidden"
source_modules = ["app.repositories", "app.db"]
forbidden_modules = [
    "app.api",
    "app.services",
    "app.schemas",
]

[[tool.importlinter.contracts]]
name = "Pure types, utils, and base errors must stay independent"
type = "forbidden"
source_modules = [
    "app.types",
    "app.utils",
    "app.exceptions.errors",
]
forbidden_modules = [
    "app.api",
    "app.services",
    "app.repositories",
    "app.db",
    "app.core",
    "app.schemas",
    "app.exceptions.handlers",
    "fastapi",
    "sqlalchemy",
]
```

### 2. `ruff` 复杂度与参数检查（放入 `pyproject.toml`）

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "PLR0913", "C901"]

[tool.ruff.lint.pylint]
max-args = 5

[tool.ruff.lint.mccabe]
max-complexity = 12
```

## 四、验证方式

- 执行静态架构与质量检查：`uv run lint-imports && uv run ruff check .`
- 执行业务测试：`uv run pytest`
- 验证边界解耦：在 `tests/unit/` 中替换内存 Fake 仓储测试 `app.services`，确认不依赖 FastAPI 容器或真实数据库即可验证核心业务流转与异常语义。
