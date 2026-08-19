from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import CustomerThermometerClient, CustomerThermometerError
from ._common import NO_TOKEN

# Customer Thermometer's own API does not document a hard maximum for
# "limit" — a support-doc example shows &limit=100000 being accepted — so
# there is no vendor-side ceiling stricter than the SOP's own fallback.
# We enforce the SOP ceiling ourselves to keep get_blast_results/get_comments
# (the two tools whose payload size actually scales with limit) bounded.
_MAX_LIMIT = 200


def _clamped(limit: int | None) -> int | None:
    return min(limit, _MAX_LIMIT) if limit is not None else None


def register(mcp: FastMCP, client_factory: Callable[[], CustomerThermometerClient | None]) -> None:

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_thermometers() -> str:
        """List all Thermometer survey templates (name + ID) in the account."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("getThermometers")
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_recipient_lists() -> str:
        """List all recipient list names and IDs in the account."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("getRecipientLists")
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_send_quota() -> str:
        """Get the number of Thermometer send credits remaining in the account."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("getSendQuota")
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_happiness_value(
        limit: Annotated[
            int | None,
            Field(description="Most-recent results to consider (vendor default 100, capped at 200)."),
        ] = None,
        blast_id: Annotated[int | None, Field(description="Limit results to this Blast ID.")] = None,
        from_date: Annotated[
            str | None, Field(description="Start of date range (YYYY-MM-DD).")
        ] = None,
        to_date: Annotated[str | None, Field(description="End of date range (YYYY-MM-DD).")] = None,
    ) -> str:
        """Get the Happiness Factor percentage for the account or one blast."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "limit": _clamped(limit),
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            result = await client.get("getHappinessValue", params=params)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_nps_value(
        limit: Annotated[
            int | None,
            Field(
                description=(
                    "Most-recent results to consider, capped at 200. Vendor docs say "
                    "this should be combined with blast_id or a date range."
                )
            ),
        ] = None,
        blast_id: Annotated[int | None, Field(description="Limit results to this Blast ID.")] = None,
        from_date: Annotated[
            str | None, Field(description="Start of date range (YYYY-MM-DD).")
        ] = None,
        to_date: Annotated[str | None, Field(description="End of date range (YYYY-MM-DD).")] = None,
    ) -> str:
        """Get the NPS score for the account, one blast, or a date range."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "limit": _clamped(limit),
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            result = await client.get("getNPSValue", params=params)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_temp_rating_value(
        limit: Annotated[
            int | None,
            Field(description="Most-recent results to consider (vendor default 100, capped at 200)."),
        ] = None,
        blast_id: Annotated[int | None, Field(description="Limit results to this Blast ID.")] = None,
        from_date: Annotated[
            str | None, Field(description="Start of date range (YYYY-MM-DD).")
        ] = None,
        to_date: Annotated[str | None, Field(description="End of date range (YYYY-MM-DD).")] = None,
    ) -> str:
        """Get the Temperature Rating percentage for the account or one blast."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "limit": _clamped(limit),
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            result = await client.get("getTempRatingValue", params=params)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_response_rate_value(
        limit: Annotated[
            int | None,
            Field(description="Most-recent results to consider (vendor default 100, capped at 200)."),
        ] = None,
        blast_id: Annotated[int | None, Field(description="Limit results to this Blast ID.")] = None,
        from_date: Annotated[
            str | None, Field(description="Start of date range (YYYY-MM-DD).")
        ] = None,
        to_date: Annotated[str | None, Field(description="End of date range (YYYY-MM-DD).")] = None,
    ) -> str:
        """Get the Email Thermometer response rate percentage for the account or one blast."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "limit": _clamped(limit),
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            result = await client.get("getResponseRateValue", params=params)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_num_responses_value(
        temperature_id: Annotated[
            int | None,
            Field(description="Filter by rating: 1 (gold), 2 (green), 3 (yellow), 4 (red)."),
        ] = None,
        limit: Annotated[
            int | None, Field(description="Most-recent results to consider, capped at 200.")
        ] = None,
        blast_id: Annotated[int | None, Field(description="Limit results to this Blast ID.")] = None,
        from_date: Annotated[
            str | None, Field(description="Start of date range (YYYY-MM-DD).")
        ] = None,
        to_date: Annotated[str | None, Field(description="End of date range (YYYY-MM-DD).")] = None,
    ) -> str:
        """Get the count of responses received for the account or one blast."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "temperatureID": temperature_id,
            "limit": _clamped(limit),
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            result = await client.get("getNumResponsesValue", params=params)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_blast_results(
        temperature_id: Annotated[
            int | None,
            Field(description="Filter by rating: 1 (gold), 2 (green), 3 (yellow), 4 (red)."),
        ] = None,
        limit: Annotated[
            int | None, Field(description="Most-recent results to return (vendor default 200, capped at 200).")
        ] = None,
        blast_id: Annotated[int | None, Field(description="Limit results to this Blast ID.")] = None,
        from_date: Annotated[
            str | None, Field(description="Start of date range (YYYY-MM-DD).")
        ] = None,
        to_date: Annotated[str | None, Field(description="End of date range (YYYY-MM-DD).")] = None,
    ) -> str:
        """Get detailed response records for the account or one blast."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "temperatureID": temperature_id,
            "limit": _clamped(limit),
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            result = await client.get("getBlastResults", params=params)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    async def customerthermometer_get_comments(
        temperature_id: Annotated[
            int | None,
            Field(description="Filter by rating: 1 (gold), 2 (green), 3 (yellow), 4 (red)."),
        ] = None,
        limit: Annotated[
            int | None, Field(description="Most-recent results to return (vendor default 200, capped at 200).")
        ] = None,
        blast_id: Annotated[int | None, Field(description="Limit results to this Blast ID.")] = None,
        from_date: Annotated[
            str | None, Field(description="Start of date range (YYYY-MM-DD).")
        ] = None,
        to_date: Annotated[str | None, Field(description="End of date range (YYYY-MM-DD).")] = None,
    ) -> str:
        """Get free-text comments left on responses for the account or one blast."""
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "temperatureID": temperature_id,
            "limit": _clamped(limit),
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            result = await client.get("getComments", params=params)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()
