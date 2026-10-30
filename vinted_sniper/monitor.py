from __future__ import annotations

import asyncio
import logging
import signal
from typing import Callable

from vinted_sniper.client import VintedClient
from vinted_sniper.config import AppConfig
from vinted_sniper.filters import SeenCache, filter_new_listings
from vinted_sniper.notifier import MultiNotifier

log = logging.getLogger(__name__)


class Monitor:
    """polls vinted catalog and dispatches alerts."""

    def __init__(
        self,
        config: AppConfig,
        client: VintedClient,
        notifier: MultiNotifier,
    ) -> None:
        self.config = config
        self.client = client
        self.notifier = notifier
        self.seen = SeenCache(max_size=config.monitor.max_seen_cache)
        self._running = False

    async def run_once(self) -> int:
        listings = await self.client.search(self.config.search)
        alerts = filter_new_listings(listings, self.seen, self.config.rules)
        for alert in alerts:
            await self.notifier.send(alert)
        log.info("polled %d listings, %d alerts", len(listings), len(alerts))
        return len(alerts)

    async def run(self, stop_event: asyncio.Event | None = None) -> None:
        self._running = True
        warmed = await self.client.warmup()
        if not warmed:
            log.warning("warmup failed — catalog calls may return empty results")

        # seed cache on first poll to avoid alerting on existing listings
        seed = await self.client.search(self.config.search)
        for item in seed:
            self.seen.add(item.id)
        log.info("seeded cache with %d listings", len(seed))

        stop = stop_event or asyncio.Event()
        while self._running and not stop.is_set():
            try:
                await self.run_once()
            except Exception as exc:  # noqa: BLE001 — keep loop alive
                log.exception("poll error: %s", exc)
            try:
                await asyncio.wait_for(
                    stop.wait(),
                    timeout=self.config.monitor.poll_interval,
                )
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        self._running = False


def install_signal_handlers(loop: asyncio.AbstractEventLoop, stop: asyncio.Event) -> None:
    def _handler(*_: object) -> None:
        log.info("shutdown requested")
        stop.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handler)
        except NotImplementedError:
            pass
