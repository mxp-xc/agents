---
name: using-reqable-capture
description: Use when a task mentions Reqable, HTTP capture, proxy traffic.
---

# Using Reqable Capture

## 概览

把 Reqable 当作实时 HTTP 抓包代理使用。按阶梯执行：界定目标、启动 capture、触发流量、缩小候选、检查记录，只在有复现价值时生成 cURL。

第一轮保持被动定位：先用已有 URL、host、method、status、headers、body 文本和时间信息。如果当前环境没有 Reqable MCP 工具，直接说明这条抓包路径不可用，不要编造记录。

## 抓包阶梯

1. 界定目标：记录触发动作、近似时间窗口，以及至少一个 selector，例如 URL/path、host、method、status、header、body 片段或 client application。

2. 启动 capture：调用 `capture_live_set_enabled({"enabled": true})`。不确定 Reqable 端口时，用 `lsof -nP -iTCP -sTCP:LISTEN | rg -i 'Reqable|9000|8888|8080'` 确认。

3. 接入代理：优先用启动环境或临时配置让服务走 Reqable，例如 `HTTP_PROXY=http://127.0.0.1:9000 HTTPS_PROXY=http://127.0.0.1:9000 NO_PROXY=`。最后才改代码强制某个请求走代理。

4. 触发一次目标动作：记录动作前后的时间点。第一次尝试保持被测系统不变。

5. 缩小候选：用最强 selector 调 `capture_live_filter`。可组合 keyword/body、host、URL、method、status code、application metadata。目标是得到一个高概率 record 或短候选列表。

6. 检查记录：对候选调 `capture_live_get_by_id`，用 URL、headers、body、status 和时间证据证明匹配；只看“最新记录”不是证据。

7. 按需 replay：需要复现、分享或变体测试时，再调 `capture_live_generate_curl` 把 record 生成 `curl`。定位请求本身不需要这一步。

## Selector 阶梯

| Selector | 例子 |
| --- | --- |
| Body text | 唯一 JSON key、prompt 片段、query 值、报错参数 |
| URL or host | 精确 URL、API path、上游 host |
| Method and status | `POST` + `400`，`GET` + `200` |
| Time window | 动作开始和结束之间的 records |
| Headers | content type、user agent、已有 request id |
| Shape | body size、JSON 结构、streaming/non-streaming |

被动 selector 噪声太大时，用天然唯一输入再触发一次。只有被动缩小仍不够、且任务允许时，才添加临时 marker、header 或 trace id。

## 工具速查

| 需求 | Tool |
| --- | --- |
| 启停抓包 | `capture_live_set_enabled` |
| 查候选 records | `capture_live_filter` |
| 读 request/response | `capture_live_get_by_id` |

定位链路按顺序推进：启动 capture -> 触发请求 -> filter -> get_by_id。需要复现时再生成 cURL。

## 代理注意事项

- 系统代理可能不是 Reqable；localhost 也常被 `NO_PROXY` 排除。先检查，再启动服务。
- 代理接入优先级：启动环境变量 -> 服务临时配置文件/启动参数 -> 代码里强制单个请求走代理。
- HTTPS 抓包可能要求信任 Reqable CA。调试时可按运行时放宽校验，例如 Python `verify=False`，Node/TS `NODE_TLS_REJECT_UNAUTHORIZED=0`。
- 上游 `503`、`400` 等失败不代表抓包失败；只要 record 里有目标 request，就能继续分析。

## 产物

默认直接使用 MCP 结果。只有用户要求文件、body 太大不适合回复，或调查需要跨轮保留证据时，才把 notes、JSON records 或 cURL 放到项目 `temp/` 目录。

初始抓包状态未知时，不要盲目恢复开关；报告本次调查期间是否启用了 capture。

## 常见错误

- 只按时间过滤，然后拿最新 record 当目标请求。
- keyword 命中很宽时，不检查 body 就认定它是目标。
- 还没尝试已有 body、URL、host、method、status selector，就先加 trace 代码。
