from collections.abc import Callable
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .._json import dump_json_capped
from ..api_client import CustomerThermometerClient, CustomerThermometerError
from ._common import NO_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], CustomerThermometerClient | None]) -> None:

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False)
    )
    async def customerthermometer_send_email(
        thermometer_id: Annotated[int, Field(description="ID of the prebuilt Thermometer to send.")],
        list_id: Annotated[
            int, Field(description="Recipient List ID to add the email address to.")
        ],
        email_address: Annotated[str, Field(description="Recipient's email address.")],
        blast_id: Annotated[
            int | None, Field(description="Blast ID to log this send/response against.")
        ] = None,
        first_name: Annotated[str | None, Field(description="Recipient's first name.")] = None,
        last_name: Annotated[str | None, Field(description="Recipient's last name.")] = None,
        company_name: Annotated[str | None, Field(description="Recipient's company name.")] = None,
        custom1: Annotated[str | None, Field(description="Custom data field 1.")] = None,
        custom2: Annotated[str | None, Field(description="Custom data field 2.")] = None,
        custom3: Annotated[str | None, Field(description="Custom data field 3.")] = None,
    ) -> str:
        """Send one Email Thermometer survey to a recipient, creating the list/blast if needed.

        Returns the Blast ID on success, or 0 if the account has no send credits left.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        params = {
            "thermometerID": thermometer_id,
            "listID": list_id,
            "emailAddress": email_address,
            "blastID": blast_id,
            "firstName": first_name,
            "lastName": last_name,
            "companyName": company_name,
            "custom1": custom1,
            "custom2": custom2,
            "custom3": custom3,
        }
        try:
            result = await client.get("sendEmail", params=params)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False)
    )
    async def customerthermometer_log_response(
        recipient: Annotated[str, Field(description="Recipient's email address.")],
        temperature_id: Annotated[int, Field(description="Rating: 1, 2, 3, or 4.")],
        thermometer_id: Annotated[int, Field(description="The Thermometer ID this response is for.")],
        blast_id: Annotated[
            int | None, Field(description="Blast ID to log this response against.")
        ] = None,
        nps_rating: Annotated[int | None, Field(description="NPS rating, 0-10.")] = None,
        iso_country: Annotated[
            str | None, Field(description='Two-letter country code, e.g. "GB".')
        ] = None,
        response_date: Annotated[
            str | None, Field(description='Response timestamp, "YYYY-MM-DD HH:MM:SS".')
        ] = None,
        comment: Annotated[str | None, Field(description="Free-text comment.")] = None,
        user_agent: Annotated[
            str | None, Field(description="Recipient's browser user-agent string.")
        ] = None,
        email_notification_flag: Annotated[
            bool | None, Field(description="Whether to trigger email notifications.")
        ] = None,
        webhook_notification_flag: Annotated[
            bool | None, Field(description="Whether to trigger webhook notifications.")
        ] = None,
        first_name: Annotated[str | None, Field(description="Recipient's first name.")] = None,
        last_name: Annotated[str | None, Field(description="Recipient's last name.")] = None,
        company_name: Annotated[str | None, Field(description="Recipient's company name.")] = None,
    ) -> str:
        """Manually record a Thermometer response.

        It appears immediately in reporting and can trigger email/webhook
        notifications, same as a real recipient response would.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        body = {
            "recipient": recipient,
            "temperatureId": temperature_id,
            "thermometerId": thermometer_id,
            "blastId": blast_id,
            "npsRating": nps_rating,
            "isoCountry": iso_country,
            "responseDate": response_date,
            "comment": comment,
            "userAgent": user_agent,
            "emailNotificationFlag": email_notification_flag,
            "webhookNotificationFlag": webhook_notification_flag,
            "firstName": first_name,
            "lastName": last_name,
            "companyName": company_name,
        }
        try:
            result = await client.post("logResponse", body=body)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False)
    )
    async def customerthermometer_add_recipient_to_list(
        email_address: Annotated[str, Field(description="Recipient's email address.")],
        list_id: Annotated[int, Field(description="The existing List ID to add the recipient to.")],
        first_name: Annotated[str | None, Field(description="Recipient's first name.")] = None,
        last_name: Annotated[str | None, Field(description="Recipient's last name.")] = None,
        company_name: Annotated[str | None, Field(description="Recipient's company name.")] = None,
    ) -> str:
        """Add a recipient to an existing recipient list.

        Returns the email address on success.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        body = {
            "emailAddress": email_address,
            "listId": list_id,
            "firstName": first_name,
            "lastName": last_name,
            "companyName": company_name,
        }
        try:
            result = await client.post("addRecipientToList", body=body)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True)
    )
    async def customerthermometer_delete_response(
        response_id: Annotated[int, Field(description="ID of the response to delete.")],
    ) -> str:
        """Delete one response from reporting.

        The response moves to a bin and is permanently cleared after 30 days.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            result = await client.get("deleteResponse", params={"responseID": response_id})
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()

    @mcp.tool(
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True)
    )
    async def customerthermometer_unsubscribe_recipient(
        email_address: Annotated[str, Field(description="Email address to unsubscribe.")],
        notify: Annotated[
            bool | None, Field(description="Whether to send an unsubscribe notification.")
        ] = None,
    ) -> str:
        """Add an email address to the account's unsubscribe list.

        Blocks future Email Thermometer sends to this address.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        body = {"emailAddress": email_address, "notify": notify}
        try:
            result = await client.post("unsubscribeRecipient", body=body)
            return dump_json_capped(result)
        except CustomerThermometerError as e:
            return e.to_envelope()
