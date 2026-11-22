# Python（FastAPI / 业务服务 / CLI）务实 DDD 落地方案

适用于存在核心业务规则、状态流转或多外部系统集成的 Python 项目（默认 `uv` + `pyproject.toml` + `src/` 或 `app/` 布局）。纯胶水脚本或单表简单 CRUD 按 `ddd-tactical-guide.md` 降级为常规三层，不强套 DDD。

## 一、推荐目录骨架（模块化单体默认）

单体项目默认先按界限上下文垂直分包，模块内再分四层（仅独立单域微服务才省去业务模块名这一层）：

```text
project/
├── pyproject.toml               # 依赖、ruff 与 import-linter 契约配置
├── app/                         # 库项目用 src/<pkg>/，应用默认 app/
│   ├── main.py                  # 集中装配：创建 FastAPI/CLI 实例、注入仓储与服务、挂路由与异常处理器
│   ├── config.py                # pydantic-settings 读环境变量
│   ├── shared/
│   │   ├── errors.py            # DomainError / ApplicationError 基类及语义子类
│   │   └── types.py             # 通用值对象、时间辅助
│   ├── orders/                  # 【界限上下文 1】先业务，后分层
│   │   ├── domain/
│   │   │   ├── models.py        # 领域实体、聚合根、值对象（仅用 dataclass / Enum）
│   │   │   ├── enums.py         # StrEnum 强类型状态与流转校验
│   │   │   ├── exceptions.py    # 继承 shared.errors.DomainError
│   │   │   └── repository.py    # Protocol 仓储端口定义
│   │   ├── application/
│   │   │   ├── commands.py      # 不可变 Command / Query dataclass（避免长参数）
│   │   │   ├── use_cases.py     # 用例编排、显式事务边界（session/uow 不外泄给 domain）
│   │   │   └── ports.py         # 外部网关 Protocol（支付、通知等）
│   │   ├── infrastructure/
│   │   │   ├── db/
│   │   │   │   ├── models.py    # SQLAlchemy ORM 表模型
│   │   │   │   └── repositories.py # 仓储实现，负责 ORM 模型 ↔ Domain 实体转换
│   │   │   └── gateways/        # 外部 HTTP/MQ 客户端适配器（httpx2 等）
│   │   └── interfaces/
│   │       ├── schemas.py       # Pydantic v2 请求与响应 Schema（带 Field(description=...)）
│   │       ├── routers.py       # FastAPI 路由 / Typer 命令，只做输入解析、调 UseCase、返回 Schema
│   │       └── deps.py          # 集中鉴权与当前操作者依赖注入
│   └── inventory/               # 【界限上下文 2】同构四层，跨模块仅通过 application 门面协作
│       ├── domain/
│       ├── application/
│       │   └── use_cases.py
│       ├── infrastructure/
│       └── interfaces/
└── tests/
    ├── architecture/            # 架构与导入方向检查入口
    ├── unit/                    # 内存 Fake 仓储测 domain 与 use_cases
    └── integration/             # TestClient + 真实数据库测端到端行为
```

## 二、关键约束与正反模式

1. **`domain` 纯净度**：`domain/` 内只允许导入 Python 标准库（`dataclasses`、`enum`、`typing.Protocol`、`datetime` 等）和 `shared/` 基础错误，**严禁导入 FastAPI、Pydantic、SQLAlchemy 或 httpx2**。
2. **契约与领域分离**：`interfaces/schemas.py` 用 Pydantic v2 定义对外 HTTP/CLI 契约与校验；`infrastructure/db/models.py` 定义 ORM 表映射；`domain/models.py` 承载业务不变量与状态方法。禁止路由直接返回 ORM 模型，也禁止把 Pydantic `BaseModel` 当作持久层表对象贯穿全层。
3. **事务与异常边界**：数据库 `Session` 或 `UnitOfWork` 在 `application` 用例层开启、提交、回滚，不传进 `domain`；底层 ORM/网络异常在 `infrastructure` 捕获并转为语义化异常或向上抛出，由 `interfaces` 全局异常处理器映射 HTTP 状态码或 CLI 退出码。
4. **集中装配**：依赖绑定（把 `SqlAlchemyOrderRepository` 注入 `OrderUseCases`）只发生在 `main.py` 或 `interfaces/deps.py`，不在领域层内部 `new` 基础设施实例。

## 三、机械护栏：import-linter + ruff

### 1. `import-linter` 分层契约（放入 `pyproject.toml`）

```toml
[tool.importlinter]
root_package = "app"

[[tool.importlinter.contracts]]
name = "Clean DDD layer dependency"
type = "layers"
layers = [
    "app.orders.interfaces",
    "app.orders.application",
    "app.orders.domain",
]
exhaustive = true

[[tool.importlinter.contracts]]
name = "Domain must not import infrastructure or frameworks"
type = "forbidden"
source_modules = ["app.orders.domain"]
forbidden_modules = [
    "app.orders.infrastructure",
    "app.orders.interfaces",
    "fastapi",
    "pydantic",
    "sqlalchemy",
]

[[tool.importlinter.contracts]]
name = "Infrastructure must not import interfaces"
type = "forbidden"
source_modules = ["app.orders.infrastructure"]
forbidden_modules = ["app.orders.interfaces"]

[[tool.importlinter.contracts]]
name = "Modules must not bypass target application facade"
type = "forbidden"
source_modules = ["app.orders"]
forbidden_modules = [
    "app.inventory.domain",
    "app.inventory.infrastructure",
    "app.inventory.interfaces",
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
- 验证依赖倒置：在 `tests/unit/` 使用内存 Fake 实现 `OrderRepository` Protocol，确认不启动数据库即可跑通核心 `use_cases` 测试。
