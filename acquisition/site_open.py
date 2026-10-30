"""Observe prices rendered by a public market page in Chromium.

This is an acquisition experiment, separate from the Decimal calculation
engines. It reads visible page state and the page's own WebSocket activity;
it does not log in, place orders, reload the page, or poll a site API.

Optional setup:
    pip install playwright
    playwright install chromium
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    from playwright.sync_api import sync_playwright
except ImportError:  # Keep the rest of the acquisition package importable.
    PlaywrightTimeout = TimeoutError  # type: ignore[assignment,misc]
    sync_playwright = None  # type: ignore[assignment]


PRICE_RE = re.compile(r"\b\d{1,3}(?:\.\d+)?\s*(?:¢|%)")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def price_lines(text: str) -> list[str]:
    """Return unique visible lines containing a percent or cent price."""

    seen: set[str] = set()
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())
        if line and PRICE_RE.search(line) and line not in seen:
            seen.add(line)
            lines.append(line)
    return lines


def _trim(payload: object, limit: int = 300) -> str:
    text = payload if isinstance(payload, str) else f"<{len(payload)} binary bytes>"
    return text[:limit]


def open_page(
    url: str,
    watch: int = 0,
    headed: bool = False,
    out_dir: str | Path | None = None,
    tick: float = 2.0,
    timeout_ms: int = 45_000,
) -> dict[str, object]:
    """Open a public page, capture its rendered state, and optionally watch it."""

    if sync_playwright is None:
        raise RuntimeError(
            "site_open requires Playwright. Install it with "
            "'pip install playwright' and 'playwright install chromium'."
        )

    host = urlparse(url).netloc.replace(":", "_") or "page"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = Path(out_dir or f"snapshots/{host}_{stamp}")
    output.mkdir(parents=True, exist_ok=True)
    sockets: dict[str, dict[str, object]] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not headed)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        def on_websocket(websocket: object) -> None:
            socket_url = websocket.url  # type: ignore[attr-defined]
            info = sockets.setdefault(
                socket_url, {"frames_in": 0, "frames_out": 0, "sample": []}
            )

            def received(payload: object) -> None:
                info["frames_in"] = int(info["frames_in"]) + 1
                sample = info["sample"]
                if isinstance(sample, list) and len(sample) < 3:
                    sample.append(_trim(payload))

            websocket.on("framereceived", received)  # type: ignore[attr-defined]
            websocket.on(  # type: ignore[attr-defined]
                "framesent",
                lambda _payload: info.__setitem__(
                    "frames_out", int(info["frames_out"]) + 1
                ),
            )

        page.on("websocket", on_websocket)
        print(f"[{_now()}] opening {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        try:
            page.wait_for_load_state("networkidle", timeout=15_000)
        except PlaywrightTimeout:
            print(f"[{_now()}] page did not become network-idle; continuing")
        page.wait_for_timeout(1_500)

        def state() -> dict[str, str]:
            return page.evaluate(
                "() => ({title: document.title, url: location.href, "
                "text: document.body ? document.body.innerText : ''})"
            )

        current = state()
        page.screenshot(path=str(output / "page.png"))
        prices = price_lines(current["text"])
        changes: list[dict[str, object]] = []
        if watch:
            last = set(prices)
            end = time.time() + watch
            while time.time() < end:
                page.wait_for_timeout(int(tick * 1000))
                current = state()
                now_prices = price_lines(current["text"])
                now_set = set(now_prices)
                added, removed = now_set - last, last - now_set
                if added or removed:
                    changes.append(
                        {
                            "t": _now(),
                            "added": sorted(added),
                            "removed": sorted(removed),
                        }
                    )
                    last = now_set
            prices = price_lines(current["text"])
            page.screenshot(path=str(output / "page.png"))
        browser.close()

    result: dict[str, object] = {
        "url": current["url"],
        "title": current["title"],
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "price_lines": prices,
        "text": current["text"],
        "websockets": sockets,
        "changes_while_watching": changes,
        "screenshot": str(output / "page.png"),
    }
    (output / "snapshot.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--watch", type=int, default=0)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    try:
        open_page(args.url, watch=args.watch, headed=args.headed, out_dir=args.out)
    except PlaywrightTimeout:
        sys.exit("Timed out loading the page. Check the URL and your connection.")
