import re
from pathlib import Path


class TemplateError(ValueError):
    pass


PLACEHOLDER = re.compile(r"\{\{(.*?)\}\}", re.DOTALL)


def flatten(data: dict, source: Path) -> dict[str, str]:
    result: dict[str, str] = {}

    def visit(node: dict, prefix: str = "") -> None:
        for key, value in node.items():
            name = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict) and set(value) == {"value"} and isinstance(value["value"], str):
                if name in result:
                    raise TemplateError(f"{source}: 配置 key 冲突: {name}")
                result[name] = value["value"]
            elif isinstance(value, dict) and value and "value" not in value:
                visit(value, name)
            else:
                raise TemplateError(f"{source}: {name} 应为含字符串 value 的表")

    visit(data)
    return result


def render(template: str, defaults: dict[str, str], overrides: dict[str, str]) -> str:
    matches = list(PLACEHOLDER.finditer(template))
    keys = set()
    for match in matches:
        key = match.group(1).strip()
        if not key:
            line = template.count("\n", 0, match.start()) + 1
            raise TemplateError(f"第 {line} 行存在空 key")
        keys.add(key)

    values = defaults | overrides
    missing = keys - values.keys()
    if missing:
        raise TemplateError(f"缺少配置 key: {', '.join(sorted(missing))}")
    unused = values.keys() - keys
    if unused:
        raise TemplateError(f"配置含未使用的 key: {', '.join(sorted(unused))}")
    return PLACEHOLDER.sub(lambda match: values[match.group(1).strip()], template)
