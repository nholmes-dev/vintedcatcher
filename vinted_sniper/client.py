from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from vinted_sniper.models import Listing, SearchQuery

log = logging.getLogger(__name__)


class VintedClient:
    """async http client for vinted catalog endpoints.

    note: vinted does not publish a stable public api. this client targets
    the same catalog routes used by the web app and may break when vinted
    changes their frontend. use responsibly and respect platform tos.
    """

    def __init__(
        self,
        domain: str = "www.vinted.fr",
        user_agent: str | None = None,
        session_file: str = "session.json",
        timeout: float = 20.0,
    ) -> None:
        self.domain = domain
        self.base_url = f"https://{domain}"
        self.api_url = f"{self.base_url}/api/v2"
        self.session_file = Path(session_file)
        self._client = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "User-Agent": user_agent
                or (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
            },
            follow_redirects=True,
        )
        self._load_session()

    def _load_session(self) -> None:
        if not self.session_file.exists():
            return
        try:
            data = json.loads(self.session_file.read_text())
            cookies = data.get("cookies", {})
            for name, value in cookies.items():
                self._client.cookies.set(name, value, domain=self.domain)
            log.debug("loaded session from %s", self.session_file)
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("failed to load session: %s", exc)

    def save_session(self) -> None:
        cookies = {c.name: c.value for c in self._client.cookies.jar}
        payload = {"cookies": cookies, "domain": self.domain}
        self.session_file.write_text(json.dumps(payload, indent=2))

    async def close(self) -> None:
        await self._client.aclose()

    async def search(self, query: SearchQuery, page: int = 1, per_page: int = 24) -> list[Listing]:
        params = query.to_params()
        params.update({"page": page, "per_page": per_page})
        url = f"{self.api_url}/catalog/items"
        log.debug("fetching %s params=%s", url, params)
        try:
            resp = await self._client.get(url, params=params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            log.error("catalog request failed: %s", exc)
            return []
        except httpx.HTTPError as exc:
            log.error("network error: %s", exc)
            return []
        return self._parse_items(resp.json())

    def _parse_items(self, payload: dict[str, Any]) -> list[Listing]:
        items = payload.get("items") or payload.get("catalog_items") or []
        out: list[Listing] = []
        for raw in items:
            listing = self._parse_item(raw)
            if listing:
                out.append(listing)
        return out

    def _parse_item(self, raw: dict[str, Any]) -> Listing | None:
        item_id = raw.get("id")
        if item_id is None:
            return None
        price_block = raw.get("price") or raw.get("total_item_price") or {}
        if isinstance(price_block, (int, float)):
            amount = float(price_block)
            currency = raw.get("currency", "EUR")
        else:
            amount = float(price_block.get("amount") or price_block.get("numeric") or 0)
            currency = price_block.get("currency_code") or price_block.get("currency") or "EUR"
        brand = ""
        if isinstance(raw.get("brand_title"), str):
            brand = raw["brand_title"]
        elif isinstance(raw.get("brand"), dict):
            brand = raw["brand"].get("title", "")
        photo = ""
        photos = raw.get("photos") or raw.get("photo") or []
        if photos and isinstance(photos[0], dict):
            photo = photos[0].get("url", "") or photos[0].get("full_size_url", "")
        created = None
        ts = raw.get("created_at_ts") or raw.get("created_at")
        if isinstance(ts, (int, float)):
            created = datetime.fromtimestamp(ts, tz=timezone.utc)
        path = raw.get("path") or raw.get("url") or f"/items/{item_id}"
        if path.startswith("/"):
            url = f"{self.base_url}{path}"
        else:
            url = path
        return Listing(
            id=int(item_id),
            title=str(raw.get("title") or ""),
            brand=str(brand),
            price=amount,
            currency=str(currency),
            url=url,
            size=str(raw.get("size_title") or raw.get("size") or ""),
            condition=str(raw.get("status") or raw.get("condition") or ""),
            photo_url=photo,
            created_at=created,
            raw=raw,
        )

    async def warmup(self) -> bool:
        """fetch homepage to obtain cookies before catalog calls."""
        try:
            resp = await self._client.get(self.base_url)
            resp.raise_for_status()
            self.save_session()
            return True
        except httpx.HTTPError as exc:
            log.error("warmup failed: %s", exc)
            return False
