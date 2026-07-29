import httpx


class CustomerThermometerError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Customer Thermometer API error {status_code}: {message}")


class CustomerThermometerClient:
    """Async httpx client wrapping the Customer Thermometer REST API.

    A single endpoint (api.php) dispatches on the "getMethod" query
    parameter. Responses are XML, plain integers, or plain strings
    depending on the method — never JSON — so this client returns the raw
    response text rather than a parsed object.
    """

    def __init__(self, api_key: str, api_url: str):
        self._api_key = api_key
        url = api_url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        self._api_url = url

    def _clean_params(self, params: dict | None) -> dict:
        if not params:
            return {}
        return {k: v for k, v in params.items() if v is not None}

    async def get(self, get_method: str, params: dict | None = None) -> str:
        query = {"apiKey": self._api_key, "getMethod": get_method}
        query.update(self._clean_params(params))
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.get(self._api_url, params=query)
            except httpx.RequestError as e:
                raise CustomerThermometerError(
                    0, f"{e or type(e).__name__} (url={self._api_url})"
                ) from e
            self._raise_for_status(resp)
            return resp.text

    async def post(self, get_method: str, body: dict | None = None) -> str:
        query = {"apiKey": self._api_key, "getMethod": get_method}
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(
                    self._api_url, params=query, data=self._clean_params(body)
                )
            except httpx.RequestError as e:
                raise CustomerThermometerError(
                    0, f"{e or type(e).__name__} (url={self._api_url})"
                ) from e
            self._raise_for_status(resp)
            return resp.text

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code >= 400:
            raise CustomerThermometerError(resp.status_code, resp.text)
