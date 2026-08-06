from typing import Any

import httpx

DEFAULT_TIMEOUT = 30.0


class ZAPIService:
    def __init__(self):
        from src.api.config import settings

        self.instance_id = settings.ZAPI_INSTANCE_ID
        self.instance_token = settings.ZAPI_INSTANCE_TOKEN
        self.security_token = settings.ZAPI_SECURITY_TOKEN
        self.base_url = f"https://api.z-api.io/instances/{self.instance_id}/token/{self.instance_token}"

    def _request(self, method: str, url: str, **kwargs: Any) -> dict:
        timeout = kwargs.pop("timeout", DEFAULT_TIMEOUT)
        headers = kwargs.pop("headers", {})
        headers["Client-Token"] = self.security_token
        kwargs["headers"] = headers
        with httpx.Client(timeout=timeout) as client:
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

    def send_message(self, phone: str, message: str) -> dict:
        url = f"{self.base_url}/send-text"
        payload = {
            "phone": phone,
            "message": message,
        }
        return self._request("POST", url, json=payload)

    def send_buttons(self, phone: str, message: str, buttons: list[str]) -> dict:
        url = f"{self.base_url}/send-button-text"
        payload = {
            "phone": phone,
            "text": message,
            "buttons": buttons,
        }
        return self._request("POST", url, json=payload)

    def send_text_with_button(self, phone: str, text: str, button_text: str) -> dict:
        url = f"{self.base_url}/send-text"
        payload = {
            "phone": phone,
            "text": text,
            "title": button_text,
        }
        return self._request("POST", url, json=payload)


zapi_service = ZAPIService()
