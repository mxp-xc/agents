# agentctl 开发指南

`agentctl` 是本仓库的 Python CLI，集中提供维护 agents workflow 能力的命令。项目配置和命令入口在根目录 `pyproject.toml`，通过 `uv run agentctl` 运行；依赖通过 `uv add` 管理。

## 代码组织

- `cli.py` 创建根命令并注册子命令。
- `commands/` 按能力存放子命令；`instructions.py` 负责个人指令的生成和检查，`instruction_template.py` 集中处理模板变量及配置检查。
- 根目录 `tests/` 存放命令行为测试，使用临时目录隔离实际配置。

新增子命令时，在 `commands/` 实现并在 `cli.py` 注册；按需要添加测试，并在对应能力文档中说明使用方式和维护约定。避免把能力专属逻辑放进根命令。维护个人指令生成行为或配置时，先阅读[个人指令维护说明](../docs/instructions/README.md)。

## 验证

从仓库根目录运行：

```bash
uv run agentctl --help
uv run python -m unittest discover -s tests -v
uv build
```

涉及个人指令输出时，用 `uv run agentctl instructions check --test` 检查测试目标；首次运行前可用 `uv run agentctl instructions sync --test` 生成。正式全局指令的迁移和覆盖要求见个人指令维护说明。
