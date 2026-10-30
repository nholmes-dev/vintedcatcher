from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from vinted_sniper.models import SearchQuery


@dataclass
class NotifierConfig:
    telegram_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook: str = ""
    console: bool = True


@dataclass
class MonitorConfig:
    poll_interval: float = 30.0
    max_seen_cache: int = 5000
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    session_file: str = "session.json"
    domain: str = "www.vinted.fr"


@dataclass
class FlipRule:
    """simple margin rule for auto-alerts."""

    name: str
    max_buy_price: float
    target_resell: float
    keywords: list[str] = field(default_factory=list)
    brands: list[str] = field(default_factory=list)


@dataclass
class AppConfig:
    search: SearchQuery = field(default_factory=SearchQuery)
    monitor: MonitorConfig = field(default_factory=MonitorConfig)
    notifier: NotifierConfig = field(default_factory=NotifierConfig)
    rules: list[FlipRule] = field(default_factory=list)


def load_config(path: str | Path) -> AppConfig:
    raw = yaml.safe_load(Path(path).read_text()) or {}
    search_raw = raw.get("search", {})
    monitor_raw = raw.get("monitor", {})
    notifier_raw = raw.get("notifier", {})

    search = SearchQuery(
        keywords=search_raw.get("keywords", ""),
        brand_ids=search_raw.get("brand_ids", []),
        catalog_ids=search_raw.get("catalog_ids", []),
        max_price=search_raw.get("max_price"),
        min_price=search_raw.get("min_price"),
        size_ids=search_raw.get("size_ids", []),
        order=search_raw.get("order", "newest_first"),
        country=search_raw.get("country", "fr"),
    )
    monitor = MonitorConfig(
        poll_interval=float(monitor_raw.get("poll_interval", 30)),
        max_seen_cache=int(monitor_raw.get("max_seen_cache", 5000)),
        user_agent=monitor_raw.get("user_agent", MonitorConfig.user_agent),
        session_file=monitor_raw.get("session_file", "session.json"),
        domain=monitor_raw.get("domain", "www.vinted.fr"),
    )
    notifier = NotifierConfig(
        telegram_token=notifier_raw.get("telegram_token", ""),
        telegram_chat_id=str(notifier_raw.get("telegram_chat_id", "")),
        discord_webhook=notifier_raw.get("discord_webhook", ""),
        console=bool(notifier_raw.get("console", True)),
    )
    rules = [
        FlipRule(
            name=r.get("name", "rule"),
            max_buy_price=float(r["max_buy_price"]),
            target_resell=float(r.get("target_resell", 0)),
            keywords=r.get("keywords", []),
            brands=r.get("brands", []),
        )
        for r in raw.get("rules", [])
    ]
    return AppConfig(search=search, monitor=monitor, notifier=notifier, rules=rules)


def example_config() -> dict[str, Any]:
    return {
        "search": {
            "keywords": "nike tech fleece",
            "max_price": 45,
            "order": "newest_first",
            "country": "fr",
        },
        "monitor": {
            "poll_interval": 25,
            "domain": "www.vinted.fr",
            "session_file": "session.json",
        },
        "notifier": {
            "console": True,
            "telegram_token": "",
            "telegram_chat_id": "",
            "discord_webhook": "",
        },
        "rules": [
            {
                "name": "tech fleece flip",
                "max_buy_price": 40,
                "target_resell": 75,
                "keywords": ["tech fleece"],
                "brands": ["nike"],
            }
        ],
    }
