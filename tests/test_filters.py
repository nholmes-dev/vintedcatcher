import pytest

from vinted_sniper.filters import SeenCache, evaluate_rules, matches_keywords
from vinted_sniper.models import Listing
from vinted_sniper.config import FlipRule


def test_seen_cache_deduplicates():
    cache = SeenCache(max_size=10)
    assert cache.add(1) is True
    assert cache.add(1) is False
    assert cache.add(2) is True


def test_flip_rule_matches():
    listing = Listing(
        id=1,
        title="nike tech fleece hoodie",
        brand="Nike",
        price=35.0,
        currency="EUR",
        url="https://example.com",
    )
    rule = FlipRule(name="test", max_buy_price=40, target_resell=70, keywords=["tech fleece"])
    alert = evaluate_rules(listing, [rule])
    assert alert is not None
    assert alert.profit_estimate == 35.0


def test_keywords_filter():
    listing = Listing(id=1, title="adidas jacket", brand="Adidas", price=10, currency="EUR", url="")
    assert matches_keywords(listing, ["nike"]) is False
    assert matches_keywords(listing, ["jacket"]) is True
