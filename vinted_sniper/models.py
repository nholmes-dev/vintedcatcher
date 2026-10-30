from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Listing:
    """normalized vinted item from catalog search."""

    id: int
    title: str
    brand: str
    price: float
    currency: str
    url: str
    size: str = ""
    condition: str = ""
    photo_url: str = ""
    created_at: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def price_label(self) -> str:
        return f"{self.price:.2f} {self.currency}"


@dataclass
class SearchQuery:
    """user search parameters."""

    keywords: str = ""
    brand_ids: list[int] = field(default_factory=list)
    catalog_ids: list[int] = field(default_factory=list)
    max_price: float | None = None
    min_price: float | None = None
    size_ids: list[int] = field(default_factory=list)
    order: str = "newest_first"
    country: str = "fr"

    def to_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {"order": self.order}
        if self.keywords:
            params["search_text"] = self.keywords
        if self.max_price is not None:
            params["price_to"] = self.max_price
        if self.min_price is not None:
            params["price_from"] = self.min_price
        for i, bid in enumerate(self.brand_ids):
            params[f"brand_ids[{i}]"] = bid
        for i, cid in enumerate(self.catalog_ids):
            params[f"catalog_ids[{i}]"] = cid
        for i, sid in enumerate(self.size_ids):
            params[f"size_ids[{i}]"] = sid
        return params


@dataclass
class Alert:
    """notification payload for a matching listing."""

    listing: Listing
    reason: str
    profit_estimate: float | None = None
