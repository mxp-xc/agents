# Python（FastAPI / 业务服务 / CLI）务实分层落地方案

参考 `fastapi-fullstack` 等现代 Python 工程惯例，Python 服务默认采用**轻量务实展平分层**（按职责水平分层，不做按域重型四层套娃），配套 `uv` + `pyproject.toml` + `app/`（库项目用 `src/<pkg>/`）。通用边界与响应/异常协议见 [architecture-principles.md](../architecture-principles.md)；仅超大型多上下文系统选定 L2 时才结合 [ddd-guide.md](../ddd-guide.md) 按域分包。

## 一、目录骨架与单向依赖

### 1. 标准目录树

```text
project/
├── pyproject.toml               # 依赖、ruff、pyrefly 与 import-linter 配置
├── app/                         # 库项目用 src/<pkg>/，应用服务默认 app/
│   ├── main.py                  # 启动装配：创建 FastAPI/CLI、挂载中间件、异常拦截器与路由
│   │
│   ├── api/                     # 【接入层】只做输入解析、鉴权依赖、调 services、显式返回 ApiResponse[T]
│   │   ├── router.py            # 聚合各业务子路由（由 main.py 注入 service 实例，api 零 db 导入）
│   │   ├── deps.py              # 集中鉴权、当前操作者依赖注入
│   │   └── routes/              # 按业务资源拆文件（orders.py, risk.py）
│   ├── schemas/                 # 【契约层】Pydantic 请求与响应业务数据 Schema（带 Field 描述）
│   ├── services/                # 【业务逻辑与用例层】按业务资源拆文件（orders.py, risk.py）
│   │                            # 负责事务边界、状态流转与业务校验（失败抛 BusinessException(XxxErrorCode)）
│   ├── repositories/            # 【数据访问层】按业务资源拆文件，封装 SQLAlchemy/SQLModel 查询
│   ├── db/                      # 【数据库引擎与表模型】
│   │   ├── session.py           # Engine / Session / UnitOfWork
│   │   └── models/              # ORM 表模型（按业务资源拆文件，严禁直接作为 API 响应返回）
│   │
│   ├── core/                    # 【带框架横切底座】
│   │   ├── config.py            # pydantic-settings 环境变量配置
│   │   ├── security.py          # 鉴权与凭证核验
│   │   └── middleware.py        # TraceId 中间件（写 X-Trace-Id 响应头与日志上下文）
│   ├── exceptions/              # 【异常体系（纯语义异常与 FastAPI 拦截器分离）】
│   │   ├── errors.py            # [无框架] ErrorCode、BaseErrorCode 与唯一默认 BusinessException
│   │   └── handlers.py          # [带框架] FastAPI 全局异常处理器（默认返回 HTTP 200 + ApiResponse 失败体，兜底异常同步回写 X-Trace-Id 响应头）
│   │
│   ├── types/                   # 【无框架公共类型】零 Web/DB/IO 依赖（允许纯数据模型 pydantic），禁用 common 命名
│   │   ├── enums.py             # 跨 ≥2 模块共用的公共 StrEnum（单业务私有错误码留在各自 services/<domain>.py）
│   │   ├── vo.py                # 不可变值对象（@dataclass(frozen=True)）
│   │   └── dto.py               # ApiResponse[T]({code, message, data})、PageQuery、PageResult
│   └── utils/                   # 【无框架纯工具】纯无状态辅助函数（跨处复用才建）
└── tests/
    ├── unit/                    # 内存 Fake 仓储测 services 核心业务规则（零 FastAPI/DB 容器依赖）
    └── integration/             # TestClient + 真实数据库测端到端切片
```

> 按需扩展：有异步队列、CLI 子命令或外部 HTTP 客户端时，在 `app/` 下同级增设 `worker/`、`commands/`、`clients/`；无需求时不预建空目录。

### 2. 层间依赖与运行时调用树

```text
依赖方向：
  app.api ──▶ app.services ──▶ app.repositories ──▶ app.db
                   │
                   └──▶ 无框架公共区 (app.types / app.utils / app.exceptions.errors)
                        (严禁反向 import api / services / repositories / db / core / fastapi / sqlalchemy)
```

```text
HTTP Request
  └── core.middleware.TraceMiddleware
        ├── 生成 trace_id -> 绑定 contextvars / logging
        ├── 写入响应头: X-Trace-Id: <trace_id>
        └── api.deps.get_current_actor
              ├── 校验 Token/Header (失败抛 BusinessException(BaseErrorCode.AUTH_UNAUTHENTICATED))
              └── api.routes.orders.create_order(payload: CreateOrderRequest)
                    ├── Pydantic 自动校验入参 (失败由 handlers.py 转为 COMMON.PARAM.INVALID)
                    ├── 调用 services.orders.create_order(session, actor, payload)
                    │     ├── 校验业务规则与状态流转 (失败抛 BusinessException(OrderErrorCode.XXX))
                    │     ├── repositories.orders.save(session, order_model)
                    │     └── session.commit()                 # 事务边界收口在 services
                    └── 返回 ApiResponse.ok(OrderResponse.model_validate(order))  # HTTP 200
```

## 二、统一响应与唯一默认 `BusinessException` 代码形态

无外部契约特殊规定时，默认全量返回 **HTTP 200** + `ApiResponse[T]`（既有契约另有规定的从契约）：

```python
# 1. app/types/dto.py（零框架依赖，traceId 走 X-Trace-Id 响应头，不进 data）
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应信封。"""

    code: str = "SUCCESS"
    message: str = "success"
    data: T | None = None

    @classmethod
    def ok(cls, data: T | None = None) -> "ApiResponse[T]":
        """构造成功响应。"""
        return cls(code="SUCCESS", message="success", data=data)

    @classmethod
    def fail(cls, code: str, message: str) -> "ApiResponse[None]":
        """构造失败响应。"""
        return cls(code=code, message=message, data=None)
```

```python
# 2. app/exceptions/errors.py（零框架依赖：ErrorCode + BaseErrorCode + 唯一 BusinessException）
from enum import Enum

class ErrorCode(Enum):
    """错误码枚举基类，直接通过 __init__ 绑定 code 与 default_message 字段。"""

    code: str
    default_message: str

    def __init__(self, code: str, default_message: str) -> None:
        self.code = code
        self.default_message = default_message

class BaseErrorCode(ErrorCode):
    """外层通用错误码（全大写点分层）。"""

    SUCCESS = ("SUCCESS", "success")
    COMMON_PARAM_INVALID = ("COMMON.PARAM.INVALID", "请求参数不合法")
    AUTH_UNAUTHENTICATED = ("AUTH.UNAUTHENTICATED", "未登录或身份凭证无效")
    AUTH_FORBIDDEN = ("AUTH.FORBIDDEN", "无权限执行该操作")
    COMMON_RESOURCE_NOT_FOUND = ("COMMON.RESOURCE.NOT_FOUND", "请求的资源不存在")
    COMMON_SYSTEM_ERROR = ("COMMON.SYSTEM.ERROR", "系统繁忙，请稍后重试")

class BusinessException(Exception):
    """全系统唯一默认业务异常，由全局异常处理器转换为统一响应。"""

    def __init__(self, error_code: ErrorCode, message: str | None = None) -> None:
        self.error_code = error_code
        self.message = message or error_code.default_message
        super().__init__(self.message)
```

```python
# 3. app/services/risk.py（各业务特性在自身模块内独立定义全大写点分层错误码）
from app.exceptions.errors import ErrorCode

class RiskErrorCode(ErrorCode):
    """风控特性错误码。"""

    RISK_INVALID = ("RISK.INVALID", "风控配置参数无效")
    RISK_CREATE_ERROR = ("RISK.CREATE.ERROR", "风控规则创建失败")
    RISK_UPDATE_ERROR = ("RISK.UPDATE.ERROR", "风控规则更新失败")
```

## 三、关键正反模式对比

| 关注点 | 推荐做法 | 禁止做法 |
| --- | --- | --- |
| **服务层洁净度** | `services/` 只接收 Python 原生类型、Schema 或领域对象，抛 `BusinessException(XxxErrorCode)` | 在 `services/` 内 `import fastapi`、接 `Request` 或直接抛 `HTTPException(status_code=...)` |
| **事务边界** | 在 `services/` 用例入口统一 `commit/rollback`（或通过 `UnitOfWork` 上下文管理器） | 在 `api/routes/` 或 `repositories/` 每个小查询里零散 `session.commit()` |
| **契约与表模型** | `schemas/`（Pydantic）与 `db/models/`（ORM）严格分文件；路由显式返回 `ApiResponse[OrderSchema]` | 路由直接裸返 ORM Model 实例，或把 `trace_id` 塞进 `ApiResponse.data` |
| **状态与公共目录** | 状态用 `StrEnum`；跨模块纯类型放 `types/`、工具放 `utils/` | 散落裸字符串状态比较；或建 `common/` 目录把单业务私有函数丢进全局 |

### 默认选型与框架细则

- **默认技术栈**：各依赖均采用最新稳定版。Web 用 `FastAPI`，校验用 `Pydantic`，ORM 用 `SQLAlchemy` + `Alembic`，HTTP 客户端优先 `httpx2`（替代停更的 `httpx`，与依赖树中的 `httpx` 可共存；需 HTTP/2 时装 `httpx2[http2]`），包管理用 `uv`，测试用 `pytest`。
- **Pydantic**：使用现代 API（`BaseModel`、`model_config = ConfigDict(from_attributes=True)`、`model_validator`、`Field(description=...)`），不引入过时写法（`orm_mode`、`@validator`）。
- **SQLAlchemy 与 Alembic**：基类继承 `DeclarativeBase`，列用 `Mapped[T]` 与 `mapped_column`；关系显式声明 `cascade`/`lazy`，防循环触发默认 `lazy="select"` N+1（用 `selectinload`/`joinedload`）；`Alembic` 基于 `Base.metadata` 执行 `revision --autogenerate`，人工核对 diff 并补齐 `downgrade` 后再 `upgrade head`。

## 四、机械护栏：import-linter + ruff + pyrefly

Python 项目不强制限制函数 `max-args`（FastAPI 依赖注入与关键字参数天然较多），默认使用 **`import-linter`**（分层依赖护栏）+ **`ruff`**（静态规范、格式与模块/类/函数 docstring 检查）+ **`pyrefly`**（类型检查）。通过 `uv add --group dev import-linter pre-commit pyrefly pytest ruff` 安装最新稳定版，并在 `pyproject.toml` 写入以下配置：

```toml
[tool.ruff.lint]
select = ["E4", "E7", "E9", "F"]
extend-select = ["D100", "D101", "D102", "D103", "D104"]

[tool.pyrefly]

[tool.importlinter]
root_package = "app"
include_external_packages = true

# 注：若项目尚未创建 app.utils / app.db 等可选子包，按实际存在的模块裁剪 layers / source_modules / forbidden_modules
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
name = "Api must not bypass services to repositories or db"
type = "forbidden"
source_modules = ["app.api"]
forbidden_modules = [
    "app.repositories",
    "app.db",
]
allow_indirect_imports = true
# 推荐在 main.py 集中装配并注入 service/事务工厂，实现零豁免；若使用 api/deps.py 直连 db.session，可加 ignore_imports = ["app.api.deps -> app.db.**"]

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

## 五、验证命令与常见提示

```bash
uv run lint-imports && uv run ruff check --force-exclude --output-format concise && uv run ruff format --check --force-exclude --output-format concise && uv run pyrefly check && uv run pytest
```

- **Pyrefly + FastAPI 异常处理器签名**：`app.add_exception_handler(BusinessException, handler)` 注册的处理函数签名应接收 `exc: Exception` 并在函数体内用 `isinstance(exc, BusinessException)` 收窄类型，避免 `pyrefly check` 报回调逆变类型错误。
