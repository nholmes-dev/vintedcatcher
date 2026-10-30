from __future__ import annotations

from collections import OrderedDict

from vinted_sniper.config import FlipRule
from vinted_sniper.models import Alert, Listing


class SeenCache:
    """bounded lru-style cache of listing ids."""

    def __init__(self, max_size: int = 5000) -> None:
        self.max_size = max_size
        self._ids: OrderedDict[int, None] = OrderedDict()

    def add(self, listing_id: int) -> bool:
        """returns true if this id is new."""
        if listing_id in self._ids:
            self._ids.move_to_end(listing_id)
            return False
        self._ids[listing_id] = None
        while len(self._ids) > self.max_size:
            self._ids.popitem(last=False)
        return True

    def __contains__(self, listing_id: int) -> bool:
        return listing_id in self._ids


def matches_keywords(listing: Listing, keywords: list[str]) -> bool:
    if not keywords:
        return True
    hay = f"{listing.title} {listing.brand}".lower()
    return any(k.lower() in hay for k in keywords)


def matches_brands(listing: Listing, brands: list[str]) -> bool:
    if not brands:
        return True
    lb = listing.brand.lower()
    return any(b.lower() in lb for b in brands)


def evaluate_rules(listing: Listing, rules: list[FlipRule]) -> Alert | None:
    for rule in rules:
        if listing.price > rule.max_buy_price:
            continue
        if not matches_keywords(listing, rule.keywords):
            continue
        if not matches_brands(listing, rule.brands):
            continue
        margin = rule.target_resell - listing.price if rule.target_resell else None
        return Alert(
            listing=listing,
            reason=f"matched flip rule: {rule.name}",
            profit_estimate=margin,
        )
    return None


def filter_new_listings(
    listings: list[Listing],
    seen: SeenCache,
    rules: list[FlipRule],
) -> list[Alert]:
    alerts: list[Alert] = []
    for listing in listings:
        if not seen.add(listing.id):
            continue
        alert = evaluate_rules(listing, rules)
        if alert:
            alerts.append(alert)
        elif not rules:
            alerts.append(Alert(listing=listing, reason="new listing"))
    return alerts
