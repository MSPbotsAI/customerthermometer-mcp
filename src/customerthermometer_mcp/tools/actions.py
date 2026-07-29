from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..api_client import CustomerThermometerClient, CustomerThermometerError
from ._common import NO_TOKEN


def register(mcp: FastMCP, client_factory: Callable[[], CustomerThermometerClient | None]) -> None:

    @mcp.tool()
    async def customerthermometer_send_email(
        thermometer_id: int,
        list_id: int,
        email_address: str,
        blast_id: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        company_name: str | None = None,
        custom1: str | None = None,
        custom2: str | None = None,
        custom3: str | None = None,
    ) -> str:
        """Send a single Email Thermometer survey to one recipient.

        API: GET api.php?getMethod=sendEmail

        Adds the recipient to the given list (creating it if needed), and
        sends the given prebuilt Thermometer. If blast_id is omitted, a new
        blast (of just this one person) is created and its ID returned.

        Args:
            thermometer_id: Required. ID of the prebuilt Thermometer to send.
            list_id: Required. Recipient List ID to add the email address to.
            email_address: Required. Recipient's email address.
            blast_id: Optional. Blast ID to log sends/responses against.
            first_name: Optional. Recipient's first name.
            last_name: Optional. Recipient's last name.
            company_name: Optional. Recipient's company name.
            custom1: Optional. Custom data field 1.
            custom2: Optional. Custom data field 2.
            custom3: Optional. Custom data field 3.

        Returns an integer: the Blast ID on success, or 0 if the account
        cannot send any more emails.
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
            return await client.get("sendEmail", params=params)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_log_response(
        recipient: str,
        temperature_id: int,
        thermometer_id: int,
        blast_id: int | None = None,
        nps_rating: int | None = None,
        iso_country: str | None = None,
        response_date: str | None = None,
        comment: str | None = None,
        user_agent: str | None = None,
        email_notification_flag: bool | None = None,
        webhook_notification_flag: bool | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        company_name: str | None = None,
    ) -> str:
        """Manually log a Thermometer response (immediately registers it in
        reporting and can trigger email/webhook notifications).

        API: POST api.php?getMethod=logResponse

        Args:
            recipient: Required. Recipient's email address.
            temperature_id: Required. Rating: 1, 2, 3, or 4.
            thermometer_id: Required. The Thermometer ID this response is for.
            blast_id: Optional. Blast ID to log this response against.
            nps_rating: Optional. NPS rating, 0-10.
            iso_country: Optional. Two-letter country code, e.g. "GB".
            response_date: Optional. "YYYY-MM-DD HH:MM:SS".
            comment: Optional. Free-text comment.
            user_agent: Optional. Recipient's browser user-agent string.
            email_notification_flag: Optional. Trigger email notifications.
            webhook_notification_flag: Optional. Trigger webhook notifications.
            first_name: Optional. Recipient's first name.
            last_name: Optional. Recipient's last name.
            company_name: Optional. Recipient's company name.
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
            return await client.post("logResponse", body=body)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_add_recipient_to_list(
        email_address: str,
        list_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        company_name: str | None = None,
    ) -> str:
        """Add a recipient to an existing recipient list.

        API: POST api.php?getMethod=addRecipientToList

        Args:
            email_address: Required. Recipient's email address.
            list_id: Required. The existing List ID to add the recipient to.
            first_name: Optional. Recipient's first name.
            last_name: Optional. Recipient's last name.
            company_name: Optional. Recipient's company name.

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
            return await client.post("addRecipientToList", body=body)
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_delete_response(response_id: int) -> str:
        """Delete a single response from reporting.

        API: GET api.php?getMethod=deleteResponse

        ⚠ The response moves to a bin and is permanently cleared after 30 days.

        Args:
            response_id: Required. ID of the response to delete.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        try:
            return await client.get("deleteResponse", params={"responseID": response_id})
        except CustomerThermometerError as e:
            return f"Error: {e}"

    @mcp.tool()
    async def customerthermometer_unsubscribe_recipient(
        email_address: str, notify: bool | None = None
    ) -> str:
        """Add an email address to the unsubscribe list (blocks future
        Email Thermometer blasts to this address).

        API: POST api.php?getMethod=unsubscribeRecipient

        Args:
            email_address: Required. Email address to unsubscribe.
            notify: Optional. Whether to send an unsubscribe notification.
        """
        client = client_factory()
        if client is None:
            return NO_TOKEN
        body = {"emailAddress": email_address, "notify": notify}
        try:
            return await client.post("unsubscribeRecipient", body=body)
        except CustomerThermometerError as e:
            return f"Error: {e}"
