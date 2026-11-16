# Python + FastAPI

FastAPI 项目分层骨架。SQLAlchemy 与 Pydantic 规范见 [sqlalchemy.md](sqlalchemy.md)、[pydantic.md](pydantic.md)。

## 目录骨架

```
project/
├── pyproject.toml
├── alembic.ini
├── alembic/
│   └── versions/
├── app/
│   ├── main.py              # 创建 app、挂路由、启动事件
│   ├── core/config.py       # pydantic-settings 读环境变量
│   ├── db/
│   │   ├── base.py          # SQLAlchemy Base 与 metadata
│   │   └── session.py       # engine、session 工厂、get_db 依赖
│   ├── models/              # SQLAlchemy 模型，一表一文件
│   ├── schemas/             # Pydantic 请求与响应
│   ├── services/            # 业务逻辑，显式接收 session
│   └── api/
│       ├── deps.py          # 公共依赖
│       └── routers/orders.py
└── tests/
    └── test_orders.py
```

库用 src/ 布局；应用默认 app/ 平铺。多 API 版本并存时才加 api/v1/ 一层。

## 分层规则

- 路由只解析参数、调 service、组装响应；复用逻辑放 api/deps.py。
- service 持有事务边界，ORM 与 schema 转换在此完成。
- 数据库 URL 只出现在 db/session.py；密钥经 core/config.py 读环境变量。
- 领域变多时按领域划分子目录（routers/orders.py、services/orders/、models/orders.py）；共享和替换需求增多时按 [ddd.md](../ddd.md) 调整。

## 空项目搭建顺序

```bash
uv init
uv add fastapi uvicorn sqlalchemy pydantic-settings alembic
uv run alembic init alembic
uv run uvicorn app.main:app --reload
```

命令是 uv 示例，工具按项目现状选择。文件按依赖方向从里到外创建：

1. core/config.py、db/base.py、db/session.py。
2. 示例资源：models → schemas → services → router，main.py 挂载。
3. alembic 指向 app.db.base，生成迁移并 upgrade head。
4. tests/ 冒烟测试：TestClient 请求示例接口，断言状态码与响应字段。

## 已有项目常见调整

- 路由堆业务逻辑：抽到 services/，接口行为不变。
- schemas 与 models 混用：建 Out schema，替换直接返回 ORM 对象的位置。
- 连接和配置散落：收拢到 db/session.py 和 core/config.py。
- 多入口重复创建 app：抽 create_app 工厂，入口和测试共用。
- 单文件 app 变大：按 models、schemas、services、routers 依次拆，每步可运行。

## 验证

- uv run uvicorn app.main:app 可启动，/docs 能打开。
- 测试通过；示例资源走通请求、响应与持久化。
- alembic upgrade head 与 downgrade base 可执行。
- import 方向：models 不 import schemas、services；services 不 import api。
