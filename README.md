# customerthermometer-mcp

MCP server for **Customer Thermometer** — an email-based CSAT/NPS survey
platform. Exposes its full public REST API (survey reporting + sending) as
MCP tools.

## Overview

- Stateless HTTP service. No credentials are ever persisted — each request
  supplies its own credentials via headers, used only for the lifetime of
  that single request.
- Supports concurrent requests; per-request credential isolation is done via
  Python `contextvars`, not a global/shared client instance.
- Entry points: `POST /mcp` (MCP protocol) and `GET /health` (health check).
- Default port: `8080` (configurable via `MCP_HTTP_PORT`).

## Scope

**15 tools** — the vendor's entire public API (single `api.php` endpoint,
dispatched via a `getMethod` query parameter): 10 read methods
(`get_thermometers`, `get_recipient_lists`, `get_send_quota`,
`get_happiness_value`, `get_nps_value`, `get_temp_rating_value`,
`get_response_rate_value`, `get_num_responses_value`, `get_blast_results`,
`get_comments`) and 5 write methods (`send_email`, `log_response`,
`add_recipient_to_list`, `delete_response`, `unsubscribe_recipient`).
MSPbots itself only calls 5 of the 10 read methods (BlastResults, Comments,
ResponseRateValue, NumResponsesValue, NPSValue) — this MCP covers the full
API since the vendor's entire public surface is small enough to implement
completely.

## Authentication

Customer Thermometer authenticates with a static **API key**, sent as the
`apiKey` query-string parameter on every call (the vendor's "super API key"
style — no `Authorization: Bearer` header, which the vendor docs reserve for
scoped "sub-API keys"). MSPbots' own integration also stores the API host
(`api_url`) as a per-tenant field, so this server treats it as per-request
too rather than a fixed default.

### HEADER 授权参数说明

| Header | 类型 | 是否必填 | 默认值 | 枚举值 | 字段描述 | Example |
|---|---|---|---|---|---|---|
| `X-CustomerThermometer-Api-Key` | string | 是 | 无 | 无 | Customer Thermometer API Key，转发为上游 `apiKey` 查询参数 | `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6` |
| `X-CustomerThermometer-Api-Url` | string | 是 | 无 | 无 | API 主机地址（不带协议前缀也可，自动补 `https://`） | `app.customerthermometer.com/api.php` |

Missing either header returns `401`:
```json
{
  "error": "Missing credentials",
  "message": "This server requires the X-CustomerThermometer-Api-Key and X-CustomerThermometer-Api-Url headers",
  "required_headers": ["X-CustomerThermometer-Api-Key", "X-CustomerThermometer-Api-Url"],
  "optional_headers": []
}
```

## Environment Variables

| Variable | 类型 | 是否必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `MCP_HTTP_PORT` | int | 否 | `8080` | HTTP 监听端口 |
| `MCP_HTTP_HOST` | string | 否 | `0.0.0.0` | HTTP 监听地址 |

(No `*_BASE_URL` env var — the API host is per-tenant and always supplied
via the `X-CustomerThermometer-Api-Url` header, never a fixed default.)

## MCP Endpoint

- `POST /mcp` — MCP protocol (streamable HTTP transport)
- `GET /health` — health check, returns `{"status": "ok", "service": "customerthermometer-mcp", "transport": "http"}`

## Tool List

Responses are **not JSON** — the vendor returns XML documents (list/report
methods) or plain integers/strings, so tools return the raw response text
as-is rather than a parsed/re-serialized object.

| Tool | 功能 | 参数 | 返回格式 |
|---|---|---|---|
| `customerthermometer_get_thermometers` | 列出所有 Thermometer 名称和 ID | 无 | XML |
| `customerthermometer_get_recipient_lists` | 列出所有收件人 List 名称和 ID | 无 | XML |
| `customerthermometer_get_send_quota` | 获取剩余可发送额度 | 无 | Integer |
| `customerthermometer_get_happiness_value` | 获取 Happiness Factor（%） | `limit`, `blast_id`, `from_date`, `to_date`（均可选） | Integer |
| `customerthermometer_get_nps_value` | 获取 NPS 分数 | `limit`, `blast_id`, `from_date`, `to_date`（均可选） | Integer |
| `customerthermometer_get_temp_rating_value` | 获取 Temperature Rating（%） | `limit`, `blast_id`, `from_date`, `to_date`（均可选） | Integer |
| `customerthermometer_get_response_rate_value` | 获取回复率（%） | `limit`, `blast_id`, `from_date`, `to_date`（均可选） | Integer |
| `customerthermometer_get_num_responses_value` | 获取回复数量 | `temperature_id`, `limit`, `blast_id`, `from_date`, `to_date`（均可选） | Integer |
| `customerthermometer_get_blast_results` | 获取详细回复结果 | `temperature_id`, `limit`, `blast_id`, `from_date`, `to_date`（均可选） | XML |
| `customerthermometer_get_comments` | 获取回复评论 | `temperature_id`, `limit`, `blast_id`, `from_date`, `to_date`（均可选） | XML |
| `customerthermometer_send_email` | 发送单封 Email Thermometer 调查 | `thermometer_id`(必填), `list_id`(必填), `email_address`(必填), `blast_id`/`first_name`/`last_name`/`company_name`/`custom1-3`（可选） | Integer |
| `customerthermometer_log_response` | 手动登记一条回复 | `recipient`/`temperature_id`/`thermometer_id`(必填), 其余均可选 | — |
| `customerthermometer_add_recipient_to_list` | 添加收件人到 List | `email_address`/`list_id`(必填), `first_name`/`last_name`/`company_name`（可选） | String |
| `customerthermometer_delete_response` | ⚠ 删除一条回复（30 天后彻底清除） | `response_id`(必填) | Integer |
| `customerthermometer_unsubscribe_recipient` | 将邮箱加入退订名单 | `email_address`(必填), `notify`（可选） | String |

## 测试示例

```bash
# Health check
curl -s http://localhost:8080/health

# Call a tool via the MCP protocol (streamable HTTP) — requires an
# initialize handshake first per the MCP spec; abbreviated example below
# shows the tool-call request body only:
curl -s -X POST http://localhost:8080/mcp \
  -H "X-CustomerThermometer-Api-Key: <your-api-key>" \
  -H "X-CustomerThermometer-Api-Url: app.customerthermometer.com/api.php" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: <session-id-from-initialize>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "customerthermometer_get_send_quota",
      "arguments": {}
    }
  }'
```

**Live-verified** (2026-07-29): `customerthermometer_get_send_quota` and
`customerthermometer_get_nps_value` were both called end-to-end through
this running server with a real API key and returned real account data
(a credit count and an NPS score respectively).

## API Reference

- Full public documentation: https://www.customerthermometer.com/integration/api-documentation/

## Known Gaps

- **`getResponseRateValue`/`getNumResponsesValue` method-name ambiguity in
  the vendor's own docs**: each method's parameter table names the
  `getMethod` value without the `Value` suffix (`getResponseRate`,
  `getNumResponses`), but every worked example on the same page uses the
  `...Value` suffixed name — and MSPbots' own configured endpoint names
  ("ResponseRateValue", "NumResponsesValue") match the suffixed form. This
  server uses the suffixed names (`getResponseRateValue`,
  `getNumResponsesValue`), consistent with the examples and MSPbots' usage.
- **POST body encoding is not specified in the vendor docs** for
  `logResponse`, `addRecipientToList`, and `unsubscribeRecipient` — they
  only list field names/types, not a content-type. This server sends them
  as `application/x-www-form-urlencoded` (the traditional convention for a
  PHP-based endpoint like this); if the vendor actually expects JSON, these
  three tools would need `client.post` to switch from `data=` to `json=`.
- Only the 5 tools matching MSPbots' own usage plus `get_send_quota` were
  live-verified with real data; the remaining tools are structurally
  correct (schema validated, MCP-protocol `tools/list` confirmed) but not
  individually smoke-tested — several (`send_email`, `log_response`, etc.)
  are write operations that would create/modify real survey data, so they
  weren't exercised against the live test account.
