# Python + SQLAlchemy

模型、会话与迁移规范。任何用 SQLAlchemy 的 Python 项目适用；Web 项目目录位置见 [fastapi.md](fastapi.md)。

## 模型

- 一表一文件，放 models/；DDD 项目放 infrastructure/db/models.py。
- 2.x 声明式风格：Base 继承 DeclarativeBase，列用 Mapped[type] 与 mapped_column，表名、约束、索引显式声明。
- 关系注明 cascade 和 lazy；循环里默认 lazy="select" 产生 N+1，用 selectinload、joinedload 显式加载。
- 模型只表达表结构；业务方法放 service，入参校验归 Pydantic（见 [pydantic.md](pydantic.md)）。

## 会话

- engine 在 db/ 模块集中创建，只建一次；连接串从环境变量读。
- session 显式传入或经依赖注入，不用全局单例。
- 事务边界在 service 层：一个业务动作一个事务。
- 脚本与 CLI：sessionmaker 配 contextmanager，一次任务一个 with session。

## 迁移

- Alembic 的 env.py 从 Base.metadata 取结构，不手写建表 SQL。
- 模型改动后 revision --autogenerate，人工核对 diff 再 upgrade head。
- 迁移文件进仓库；downgrade 可执行，改表类迁移补反向步骤。
