import logging

import httpx2

# URL Bot API memuat token bot. Logger HTTP mencetak URL di level INFO, jadi dibungkam di sini.
for _name in ("httpx", "httpx2", "httpcore", "httpcore2"):
    logging.getLogger(_name).setLevel(logging.WARNING)

_CODE_BY_STATUS = {400: "bad_request", 403: "forbidden", 429: "rate_limited"}
ALLOWED_UPDATES = ["message", "callback_query"]
COMMANDS = [
    {"command": "selesai", "description": "Tutup booking yang sedang berjalan"},
    {"command": "oke", "description": "Konfirmasi booking dari grup"},
]


class TelegramError(Exception):
    """`code` singkat (SA 2.8); `detail` hanya dari `description` Telegram, tanpa URL dan token."""

    def __init__(self, code, detail=None):
        super().__init__(code)
        self.code = code
        self.detail = detail


class TelegramClient:
    def __init__(self, token, api_base="https://api.telegram.org", transport=None, timeout=10.0):
        self._token = token
        self._http = httpx2.Client(base_url=f"{api_base}/bot{token}/", timeout=timeout, transport=transport)

    def close(self):
        self._http.close()

    def _scrub(self, text):
        return text.replace(self._token, "***")[:300]

    def call(self, method, **params):
        try:
            resp = self._http.post(method, json=params)
        except httpx2.HTTPError as exc:
            raise TelegramError("network", type(exc).__name__) from None
        try:
            body = resp.json()
        except ValueError:
            body = {}
        if resp.status_code == 200 and body.get("ok"):
            return body.get("result")
        description = body.get("description") if isinstance(body, dict) else None
        detail = self._scrub(description) if isinstance(description, str) else None
        if resp.status_code >= 500:
            raise TelegramError("server_error", detail)
        raise TelegramError(_CODE_BY_STATUS.get(resp.status_code, "bad_request"), detail)

    def send_message(self, chat_id, text, reply_markup=None):
        params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "link_preview_options": {"is_disabled": True}}
        if reply_markup:
            params["reply_markup"] = reply_markup
        return self.call("sendMessage", **params)["message_id"]

    def answer_callback(self, callback_query_id):
        self.call("answerCallbackQuery", callback_query_id=callback_query_id)

    def set_webhook(self, url, secret):
        self.call("setWebhook", url=url, secret_token=secret, allowed_updates=ALLOWED_UPDATES)

    def set_commands(self):
        self.call("setMyCommands", commands=COMMANDS)
