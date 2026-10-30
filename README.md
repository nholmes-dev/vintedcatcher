# vinted-sniper

Async monitor for [Vinted](https://www.vinted.fr) listings. Polls the catalog API, filters by your flip rules, and pushes alerts to the console, Telegram, or Discord.

Built for buy-and-resell workflows — spot underpriced items before they disappear.

## install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## quick start

```bash
vinted-sniper init
# edit config.yaml with your search and rules
vinted-sniper search -c config.yaml
vinted-sniper watch -c config.yaml
```

## config

Copy `config.example.yaml` or run `vinted-sniper init`. Key sections:

- **search** — keywords, max price, country, sort order
- **rules** — flip criteria (max buy price, target resell, keyword/brand filters)
- **notifier** — console, Telegram bot token, Discord webhook
- **monitor** — poll interval and session file path

## commands

| command | description |
|---------|-------------|
| `init` | generate example config |
| `search` | one-shot catalog lookup |
| `watch` | continuous polling with alerts |
| `watch --once` | single poll cycle |

## how it works

1. Warm up a session against the Vinted homepage (cookies saved to `session.json`)
2. Poll `/api/v2/catalog/items` with your search params
3. Deduplicate seen listing ids
4. Match flip rules and compute estimated margin
5. Push alerts to configured channels

## disclaimer

Vinted does not provide a public API. This tool reverse-engineers the same endpoints used by the website and **may stop working** when Vinted updates their frontend. Use at your own risk. Automated scraping may violate Vinted's Terms of Service — this project is for educational purposes. The author is not responsible for account restrictions or misuse.

## license

MIT
