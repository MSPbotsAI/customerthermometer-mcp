"""tools/list snapshot + error-envelope mapping tests.

No network calls: tool enumeration goes through FastMCP's in-process
list_tools(), and the error-code mapping is tested directly against
CustomerThermometerError, independent of any real HTTP request.
"""

import pytest

from customerthermometer_mcp.api_client import CustomerThermometerError
from customerthermometer_mcp.config import Settings
from customerthermometer_mcp.server import create_mcp_server

# name -> (required params, readOnlyHint, destructiveHint, idempotentHint)
EXPECTED_TOOLS = {
    "customerthermometer_get_thermometers": (set(), True, None, None),
    "customerthermometer_get_recipient_lists": (set(), True, None, None),
    "customerthermometer_get_send_quota": (set(), True, None, None),
    "customerthermometer_get_happiness_value": (set(), True, None, None),
    "customerthermometer_get_nps_value": (set(), True, None, None),
    "customerthermometer_get_temp_rating_value": (set(), True, None, None),
    "customerthermometer_get_response_rate_value": (set(), True, None, None),
    "customerthermometer_get_num_responses_value": (set(), True, None, None),
    "customerthermometer_get_blast_results": (set(), True, None, None),
    "customerthermometer_get_comments": (set(), True, None, None),
    "customerthermometer_send_email": (
        {"thermometer_id", "list_id", "email_address"},
        False,
        False,
        False,
    ),
    "customerthermometer_log_response": (
        {"recipient", "temperature_id", "thermometer_id"},
        False,
        False,
        False,
    ),
    "customerthermometer_add_recipient_to_list": (
        {"email_address", "list_id"},
        False,
        False,
        False,
    ),
    "customerthermometer_delete_response": ({"response_id"}, False, True, True),
    "customerthermometer_unsubscribe_recipient": ({"email_address"}, False, False, True),
}


@pytest.mark.asyncio
async def test_tools_list_snapshot():
    mcp = create_mcp_server(Settings())
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    assert names == set(EXPECTED_TOOLS), f"unexpected tool set: {names}"

    by_name = {t.name: t for t in tools}
    for name, (expected_required, read_only, destructive, idempotent) in EXPECTED_TOOLS.items():
        tool = by_name[name]
        required = set(tool.inputSchema.get("required", []))
        assert required == expected_required, f"{name}: required={required}"

        assert tool.annotations is not None, f"{name}: missing annotations"
        assert tool.annotations.readOnlyHint is read_only, f"{name}: readOnlyHint"
        if destructive is not None:
            assert tool.annotations.destructiveHint is destructive, f"{name}: destructiveHint"
        if idempotent is not None:
            assert tool.annotations.idempotentHint is idempotent, f"{name}: idempotentHint"

        description = tool.description or ""
        assert len(description) <= 500, f"{name}: description too long ({len(description)} chars)"
        first_line = description.strip().splitlines()[0]
        assert len(first_line) <= 100, f"{name}: first line too long: {first_line!r}"
        assert "API:" not in description, f"{name}: description leaks implementation detail"


@pytest.mark.asyncio
async def test_service_instructions_present_and_bounded():
    mcp = create_mcp_server(Settings())
    assert mcp.instructions
    assert len(mcp.instructions) <= 1500


@pytest.mark.parametrize(
    "status_code,expected_code,expected_retryable",
    [
        (0, "upstream_error", True),
        (400, "invalid_argument", False),
        (401, "unauthorized", False),
        (403, "unauthorized", False),
        (404, "not_found", False),
        (422, "invalid_argument", False),
        (429, "rate_limited", True),
        (500, "upstream_error", True),
        (503, "upstream_error", True),
    ],
)
def test_error_envelope_mapping(status_code, expected_code, expected_retryable):
    import json

    err = CustomerThermometerError(status_code, "boom")
    envelope = json.loads(err.to_envelope())
    assert envelope["error"]["code"] == expected_code
    assert envelope["error"]["retryable"] is expected_retryable
    assert envelope["error"]["message"] == "boom"
