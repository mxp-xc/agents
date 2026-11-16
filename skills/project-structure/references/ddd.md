# DDD 分层

领域驱动设计的四层目录：领域、应用、基础设施、接口。用于业务规则复杂、需要替换基础设施或多团队协作的项目。

## 目录骨架

```
project/
├── domain/
│   └── orders/
│       ├── entities.py      # 实体与值对象
│       ├── repository.py    # 仓储接口（协议）
│       └── services.py      # 领域服务
├── application/
│   └── orders/
│       ├── use_cases.py     # 用例编排、DTO、事务边界
│       └── ports.py         # 外部系统端口：支付网关等
├── infrastructure/
│   ├── db/
│   │   ├── alembic/         # 迁移，env.py 指向本层 models.py
│   │   ├── models.py        # SQLAlchemy 模型
│   │   └── repositories.py  # 仓储实现
│   └── payments/
│       └── gateway.py       # 支付网关实现
├── interfaces/
│   ├── routers/
│   │   └── orders.py        # FastAPI 路由
│   └── schemas/
│       └── orders.py        # Pydantic 请求与响应
├── main.py                  # 装配：把实现绑定到接口
└── tests/
```

模块按聚合组织，聚合内再分文件；文件多到难找时再在聚合下加子目录，不提前建空目录。

聚合变多、团队按业务划分时，顶层可以按业务能力组织（screaming architecture）：orders/、payments/ 各自包含自己的四层。默认从四层顶层开始，规模到了再切换。

## 依赖方向

这四层就是端口与适配器：application 定义端口（ports），infrastructure 实现适配器（adapters）。

- domain 不 import 任何其他层；实体、值对象、仓储接口都在这一层。
- application 只依赖 domain；用例通过仓储接口读写，事务边界在用例函数内。
- infrastructure 实现 domain 的仓储接口和 application 的端口，依赖这两层，不依赖 interfaces。
- interfaces 是 Web 入口，调用 application 的用例，不直接碰 infrastructure 的实现。
- main.py 负责装配：把具体实现绑定到接口，其余各层不出现装配代码。

## 何时用

- 业务规则复杂且稳定，有明确领域语言：订单状态机、结算规则、库存预留。
- 需要替换基础设施：数据库、支付渠道、外部服务。接口把替换限制在 infrastructure 层。
- 多个团队在同一代码库协作，模块边界同时是工作边界。

CRUD 为主、规则在表单校验和数据库约束里的项目，四层结构是纯成本，用 FastAPI 分层就够；业务边界坐实后再迁移。

## 与 FastAPI 结合

骨架与各层职责见 [fastapi.md](python/fastapi.md)，这里是分层映射：

- interfaces/routers 放 FastAPI 路由，interfaces/schemas 放 Pydantic 模型。
- 用例的输入输出用 application 层的 DTO；路由把 schema 转成 DTO 再调用用例，domain 实体不出接口层。
- 仓储接口定义在 domain/orders/repository.py，实现在 infrastructure/db/repositories.py；用例只依赖接口。
- session 不出 application 层；事务在用例函数内开启、提交、回滚，domain 代码里不出现 session。

## 已有项目的改造顺序

- 先确认需要 DDD 再动手，从最容易隔离的一个聚合开始，一次迁移一个，不做全量重排。
- 第一步分开 Web 层与业务层（routers 与 services 的边界），第二步把 services 按聚合分组，第三步抽 domain 实体与仓储接口。
- 每步之后测试全绿再继续；可运行优先，过渡结构允许存在。

## 验证

- import 方向：domain 不 import 其他三层，infrastructure 不 import interfaces。
- 用内存版仓储替换数据库实现，跑同一批用例测试；用例不改动即通过，说明接口边界成立。
- TestClient 走通从路由到用例的完整请求路径。
