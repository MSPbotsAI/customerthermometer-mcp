from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import CustomerThermometerClient, CustomerThermometerError
from ._common import NO_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], CustomerThermometerClient | None]) -> None:

    @mcp.tool()
    async def customerthermometer_get_thermometers() -> str:
        """List all Thermometer names and IDs in the account.

        API: GET api.php?getMethod=getThermometers

        Returns an XML document.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            return await client.get("getThermometers")
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_recipient_lists() -> str:
        """List all recipient List names and IDs in the account.

        API: GET api.php?getMethod=getRecipientLists

        Returns an XML document.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            return await client.get("getRecipientLists")
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_send_quota() -> str:
        """Get the number of Thermometer credits remaining in the account.

        API: GET api.php?getMethod=getSendQuota

        Returns an integer.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            return await client.get("getSendQuota")
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_happiness_value(
        limit: int | None = None,
        blast_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> str:
        """Get the Happiness Factor (%) for the account or a specific blast.

        API: GET api.php?getMethod=getHappinessValue

        No required parameters (defaults to account-wide, last 100 results).

        Args:
            limit: Optional. Number of most-recent results to consider (default 100).
            blast_id: Optional. Limit results to this Blast ID.
            from_date: Optional. Start of date range (YYYY-MM-DD).
            to_date: Optional. End of date range (YYYY-MM-DD).
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {"limit": limit, "blastID": blast_id, "fromDate": from_date, "toDate": to_date}
        try:
            return await client.get("getHappinessValue", params=params)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_nps_value(
        limit: int | None = None,
        blast_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> str:
        """Get the NPS score for the account or a specific blast/date range.

        API: GET api.php?getMethod=getNPSValue

        No required parameters (defaults to account-wide, all results).

        Args:
            limit: Optional. Number of most-recent results to consider. Must
                be combined with blast_id or a date range per the vendor docs.
            blast_id: Optional. Limit results to this Blast ID.
            from_date: Optional. Start of date range (YYYY-MM-DD).
            to_date: Optional. End of date range (YYYY-MM-DD).
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {"limit": limit, "blastID": blast_id, "fromDate": from_date, "toDate": to_date}
        try:
            return await client.get("getNPSValue", params=params)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_temp_rating_value(
        limit: int | None = None,
        blast_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> str:
        """Get the Temperature Rating (%) for a specific blast or the account.

        API: GET api.php?getMethod=getTempRatingValue

        No required parameters (defaults to account-wide, last 100 results).

        Args:
            limit: Optional. Number of most-recent results to consider (default 100).
            blast_id: Optional. Limit results to this Blast ID.
            from_date: Optional. Start of date range (YYYY-MM-DD).
            to_date: Optional. End of date range (YYYY-MM-DD).
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {"limit": limit, "blastID": blast_id, "fromDate": from_date, "toDate": to_date}
        try:
            return await client.get("getTempRatingValue", params=params)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_response_rate_value(
        limit: int | None = None,
        blast_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> str:
        """Get the Response Rate (%) for the account or a specific blast.

        API: GET api.php?getMethod=getResponseRateValue

        No required parameters (defaults to account-wide, last 100 results,
        Email Thermometer blasts only).

        Args:
            limit: Optional. Number of most-recent results to consider (default 100).
            blast_id: Optional. Limit results to this Blast ID.
            from_date: Optional. Start of date range (YYYY-MM-DD).
            to_date: Optional. End of date range (YYYY-MM-DD).
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {"limit": limit, "blastID": blast_id, "fromDate": from_date, "toDate": to_date}
        try:
            return await client.get("getResponseRateValue", params=params)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_num_responses_value(
        temperature_id: int | None = None,
        limit: int | None = None,
        blast_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> str:
        """Get the number of responses received for the account or a specific blast.

        API: GET api.php?getMethod=getNumResponsesValue

        No required parameters (defaults to account-wide, no limit).

        Args:
            temperature_id: Optional. Filter by rating: 1 (gold), 2 (green),
                3 (yellow), 4 (red).
            limit: Optional. Number of most-recent results to consider.
            blast_id: Optional. Limit results to this Blast ID.
            from_date: Optional. Start of date range (YYYY-MM-DD).
            to_date: Optional. End of date range (YYYY-MM-DD).
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "temperatureID": temperature_id,
            "limit": limit,
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            return await client.get("getNumResponsesValue", params=params)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_blast_results(
        temperature_id: int | None = None,
        limit: int | None = None,
        blast_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> str:
        """Get response details for the account or a specific blast.

        API: GET api.php?getMethod=getBlastResults

        No required parameters (defaults to the last 200 results account-wide).

        Args:
            temperature_id: Optional. Filter by rating: 1 (gold), 2 (green),
                3 (yellow), 4 (red).
            limit: Optional. Number of most-recent results to consider (default 200).
            blast_id: Optional. Limit results to this Blast ID.
            from_date: Optional. Start of date range (YYYY-MM-DD).
            to_date: Optional. End of date range (YYYY-MM-DD).

        Returns an XML document.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "temperatureID": temperature_id,
            "limit": limit,
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            return await client.get("getBlastResults", params=params)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_get_comments(
        temperature_id: int | None = None,
        limit: int | None = None,
        blast_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> str:
        """Get comments left on responses for the account or a specific blast.

        API: GET api.php?getMethod=getComments

        No required parameters (defaults to the last 200 results account-wide).

        Args:
            temperature_id: Optional. Filter by rating: 1 (gold), 2 (green),
                3 (yellow), 4 (red).
            limit: Optional. Number of most-recent results to consider (default 200).
            blast_id: Optional. Limit results to this Blast ID.
            from_date: Optional. Start of date range (YYYY-MM-DD).
            to_date: Optional. End of date range (YYYY-MM-DD).

        Returns an XML document.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "temperatureID": temperature_id,
            "limit": limit,
            "blastID": blast_id,
            "fromDate": from_date,
            "toDate": to_date,
        }
        try:
            return await client.get("getComments", params=params)
        except CustomerThermometerError as e:
            return f"Error: {e}"
