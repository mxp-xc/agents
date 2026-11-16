# Python + Pydantic

schema 命名、边界与 v2 写法。任何用 Pydantic 定义数据形状的项目适用；Web 项目目录位置见 [fastapi.md](fastapi.md)。

## 边界

- schema 是数据契约（入参、出参、配置对象）；数据库结构归 SQLAlchemy 模型（见 [sqlalchemy.md](sqlalchemy.md)），转换在 service 层完成。
- 路由层进出都是 schema，ORM 对象不出接口层。

## 命名与形状

- OrdersCreate、OrdersUpdate、OrdersOut；入参与出参分开，共用字段放基类。
- 只用于响应的字段只在 Out 出现；要暴露的数据库字段随 Out 显式声明。
- 从 ORM 转出用 model_config = ConfigDict(from_attributes=True)。
- 字段语义写进 Field(description=...)，带进 OpenAPI；长度、范围等约束声明在 schema 上。

## v2 写法

- 统一 v2 风格：BaseModel、model_config、model_validator、Field；v1 已停止维护，不引入 v1 写法（orm_mode、@validator 旧签名）。
- 版本以落地时 PyPI 稳定版为准；v3 发布后按官方迁移说明评估。
