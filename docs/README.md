# 项目文档

存放本仓库能力的介绍、维护约定和限制。维护某项能力前，先读取对应说明；执行时使用的规则仍放在该能力目录中。

## 组织约定

- 按所说明的仓库目录和主题归组，例如 `docs/skills/<skill>.md`、`docs/agents/<agent>.md`；内容形成独立主题后再拆分目录。
- 说明适用场景、相关入口、目录职责、修改限制和验证方式，链接到已有规则，避免复制整份执行流程。
- 只记录当前约定和已知陷阱。尚未固化的调研放 `learning/`，一次性交付和过程产物按个人通用指令存放。
- 新增说明时在下方登记；修改能力的目录、引用方式或维护约定时，同步核对对应文档与读取入口。

## 维护说明

- [Skill 通用维护约定](skills/README.md)：所有 skill 的独立分发与资源引用边界。
- [refactor-advisor](skills/refactor-advisor.md)：领域与公共资源的划分、引用方向、扩展边界和验证要求。
- [orchestrate-development](skills/orchestrate-development.md)：开发协调流程、正式版本与草案的维护边界、实现入口和验证要求。
