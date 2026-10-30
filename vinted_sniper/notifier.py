from __future__ import annotations

import asyncio
import json
import logging
from typing import Protocol

import httpx

from vinted_sniper.config import NotifierConfig
from vinted_sniper.models import Alert

log = logging.getLogger(__name__)


class Notifier(Protocol):
    async def send(self, alert: Alert) -> None: ...


def format_alert(alert: Alert) -> str:
    item = alert.listing
    lines = [
        f"[vinted] {alert.reason}",
        f"{item.title}",
        f"brand: {item.brand or 'n/a'} | size: {item.size or 'n/a'}",
        f"price: {item.price_label}",
        f"url: {item.url}",
    ]
    if alert.profit_estimate is not None:
        lines.append(f"est. margin: {alert.profit_estimate:.2f} {item.currency}")
    return "\n".join(lines)


class ConsoleNotifier:
    async def send(self, alert: Alert) -> None:
        print(format_alert(alert))
        print("-" * 40)


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self.chat_id = chat_id
        self._url = f"https://api.telegram.org/bot{token}/sendMessage"

    async def send(self, alert: Alert) -> None:
        if not self.token or not self.chat_id:
            return
        payload = {"chat_id": self.chat_id, "text": format_alert(alert), "disable_web_page_preview": False}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(self._url, json=payload)
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            log.error("telegram notify failed: %s", exc)


class DiscordNotifier:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def send(self, alert: Alert) -> None:
        if not self.webhook_url:
            return
        embed = {
            "title": alert.listing.title,
            "url": alert.listing.url,
            "description": alert.reason,
            "fields": [
                {"name": "price", "value": alert.listing.price_label, "inline": True},
                {"name": "brand", "value": alert.listing.brand or "n/a", "inline": True},
            ],
            "color": 5763719,
        }
        if alert.profit_estimate is not None:
            embed["fields"].append(
                {"name": "est. margin", "value": f"{alert.profit_estimate:.2f}", "inline": True}
            )
        payload = {"embeds": [embed]}
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            log.error("discord notify failed: %s", exc)


class MultiNotifier:
    def __init__(self, notifiers: list[Notifier]) -> None:
        self.notifiers = notifiers

    async def send(self, alert: Alert) -> None:
        await asyncio.gather(*(n.send(alert) for n in self.notifiers))


def build_notifier(cfg: NotifierConfig) -> MultiNotifier:
    notifiers: list[Notifier] = []
    if cfg.console:
        notifiers.append(ConsoleNotifier())
    if cfg.telegram_token and cfg.telegram_chat_id:
        notifiers.append(TelegramNotifier(cfg.telegram_token, cfg.telegram_chat_id))
    if cfg.discord_webhook:
        notifiers.append(DiscordNotifier(cfg.discord_webhook))
    return MultiNotifier(notifiers)
