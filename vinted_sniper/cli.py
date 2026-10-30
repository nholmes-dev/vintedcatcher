from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import yaml

from vinted_sniper.client import VintedClient
from vinted_sniper.config import example_config, load_config
from vinted_sniper.monitor import Monitor, install_signal_handlers
from vinted_sniper.notifier import build_notifier


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_init(args: argparse.Namespace) -> int:
    path = Path(args.output)
    if path.exists() and not args.force:
        print(f"config already exists: {path}", file=sys.stderr)
        return 1
    path.write_text(yaml.dump(example_config(), sort_keys=False, allow_unicode=True))
    print(f"wrote {path}")
    return 0


async def cmd_watch(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    domain = cfg.monitor.domain
    if cfg.search.country and "vinted" not in domain:
        domain = f"www.vinted.{cfg.search.country}"

    client = VintedClient(
        domain=domain,
        user_agent=cfg.monitor.user_agent,
        session_file=cfg.monitor.session_file,
    )
    notifier = build_notifier(cfg.notifier)
    monitor = Monitor(cfg, client, notifier)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    install_signal_handlers(loop, stop)

    try:
        if args.once:
            await monitor.run_once()
        else:
            await monitor.run(stop)
    finally:
        await client.close()
    return 0


async def cmd_search(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    client = VintedClient(domain=cfg.monitor.domain, session_file=cfg.monitor.session_file)
    await client.warmup()
    listings = await client.search(cfg.search, per_page=args.limit)
    for item in listings:
        print(f"{item.price_label:>12}  {item.brand:15}  {item.title[:50]}")
        print(f"             {item.url}")
    await client.close()
    print(f"\n{len(listings)} results")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vinted-sniper",
        description="monitor vinted listings for buy-and-flip opportunities",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init", help="write example config.yaml")
    init_p.add_argument("-o", "--output", default="config.yaml")
    init_p.add_argument("-f", "--force", action="store_true")

    watch_p = sub.add_parser("watch", help="poll catalog and send alerts")
    watch_p.add_argument("-c", "--config", default="config.yaml")
    watch_p.add_argument("--once", action="store_true", help="single poll then exit")

    search_p = sub.add_parser("search", help="one-shot catalog search")
    search_p.add_argument("-c", "--config", default="config.yaml")
    search_p.add_argument("-n", "--limit", type=int, default=20)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(args.verbose)

    if args.command == "init":
        raise SystemExit(cmd_init(args))
    if args.command == "watch":
        raise SystemExit(asyncio.run(cmd_watch(args)))
    if args.command == "search":
        raise SystemExit(asyncio.run(cmd_search(args)))
    parser.print_help()
    raise SystemExit(1)


if __name__ == "__main__":
    main()
