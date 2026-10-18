"""Small local web bridge for the Jim Rockies analytical tools.

Run with ``python3 tools_server.py`` and open http://127.0.0.1:8000/tools.html.
The server deliberately delegates calculations to the existing Python modules;
it only translates JSON input and Decimal-based results for the browser.
"""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import arb_math
import arb_reach
import arb_wave
import event_arb
import hedge_range


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8000


def decimal(value: Any, label: str) -> Decimal:
    try:
        return value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{label} must be numeric.") from error


def json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if hasattr(value, "__dict__"):
        return json_value(vars(value))
    return value


def parse_odds(value: Any, mode: str) -> arb_math.Odds:
    if mode == "american":
        return arb_math.Odds.from_american(decimal(value, "American odds"))
    if mode == "probability":
        return arb_math.Odds.from_probability(decimal(value, "Probability"))
    return arb_math.Odds.from_decimal(decimal(value, "Decimal odds"))


def calculate_arb_math(payload: dict[str, Any]) -> dict[str, Any]:
    odds_a = parse_odds(payload.get("odds_a"), payload.get("mode", "decimal"))
    odds_b = parse_odds(payload.get("odds_b"), payload.get("mode", "decimal"))
    stake_a = payload.get("stake_a")
    stake_b = payload.get("stake_b")
    if (stake_a is None) != (stake_b is None):
        raise ValueError("Enter both stakes or leave both stakes blank.")

    entry = arb_math.Concretes(
        odds_a,
        odds_b,
        stake_a=decimal(stake_a, "Stake A") if stake_a is not None else None,
        stake_b=decimal(stake_b, "Stake B") if stake_b is not None else None,
    )
    return {
        "decimal_a": entry.decimal_a,
        "decimal_b": entry.decimal_b,
        "probability_a": entry.prob_a,
        "probability_b": entry.prob_b,
        "arb_index": entry.arb_index,
        "theoretical_arb": entry.is_theoretical_arb,
        "market_vig": entry.market_vig,
        "guaranteed_margin": entry.guaranteed_margin,
        "total_stake": entry.total_stake,
        "payout_a": entry.payout_a,
        "payout_b": entry.payout_b,
        "profit_a": entry.profit_a,
        "profit_b": entry.profit_b,
        "realized_arb": entry.is_realized_arb,
    }


def calculate_arb_reach(payload: dict[str, Any]) -> dict[str, Any]:
    mode = payload.get("mode", "decimal")
    anchor = parse_odds(payload.get("anchor"), mode)
    board = parse_odds(payload.get("board"), mode)
    reference = arb_reach.ReachReference()
    reference_mode = payload.get("reference", "assumed")
    if reference_mode == "neutral":
        reference.reset_neutral()
    elif reference_mode == "observed":
        reference.use_observed_vig(anchor.probability, board.probability)
    else:
        reference.use_assumed_vig(decimal(payload.get("vig", "5"), "Assumed vig"))

    reach = arb_reach.Reach(
        anchor,
        reference=reference,
        target_margin=decimal(payload.get("margin", "0"), "Target margin"),
    )
    spectrum = [
        {"probability": probability, "decimal_odds": odds.decimal}
        for probability, odds in reach.spectrum(5)
    ]
    return {
        "mode": reference.mode,
        "active_reference": reference.active_reference,
        "anchor_probability": reach.anchor_probability,
        "acceptable_probability": reach.acceptable_probability,
        "acceptable_decimal_odds": reach.acceptable_odds.decimal,
        "ideal_probability": reach.ideal_probability,
        "ideal_decimal_odds": reach.ideal_odds.decimal,
        "spectrum": spectrum,
    }


def calculate_hedge_range(payload: dict[str, Any]) -> dict[str, Any]:
    total_stake = decimal(payload.get("total_stake"), "Total stake")
    if total_stake <= 0:
        raise ValueError("Total stake must be greater than zero.")
    index, status, scale = hedge_range.analyze_range(
        payload.get("odds_a"),
        payload.get("odds_b"),
        total_stake,
        mode=payload.get("mode", "multiplier"),
        fee_a=decimal(payload.get("fee_a", "0"), "Fee A"),
        fee_b=decimal(payload.get("fee_b", "0"), "Fee B"),
    )
    high_ev_side = payload.get("high_ev_side", "A")
    best_arb = hedge_range.find_best_arb(scale)
    best_high_ev = hedge_range.find_best_high_ev(scale, high_ev_side)
    max_profit = hedge_range.find_max_profit(scale)
    center = best_arb or best_high_ev or max_profit
    center_index = int(center["stake_a"]) if center else 0
    sample = scale[max(0, center_index - 5): center_index + 6]
    return {
        "arb_index": index,
        "status": status,
        "evaluated_splits": len(scale),
        "best_arb": best_arb,
        "best_high_ev": best_high_ev,
        "max_profit": max_profit,
        "sample": sample,
    }


def calculate_event_arb(_: dict[str, Any]) -> dict[str, Any]:
    return event_arb.main()


def calculate_arb_wave(payload: dict[str, Any]) -> dict[str, Any]:
    start_probability = decimal(payload.get("start_percent", "1"), "Start percentage") / 100
    end_probability = decimal(payload.get("end_percent", "99"), "End percentage") / 100
    increment = decimal(payload.get("increment_percent", "1"), "Increment percentage") / 100
    mode = payload.get("mode", "target_profit")
    if mode == "fixed_stake":
        rows = arb_wave.generate_stake_wave(
            stake=payload.get("stake", "100"),
            start_probability=start_probability,
            end_probability=end_probability,
            increment=increment,
        )
    elif mode == "target_profit":
        rows = arb_wave.generate_wave(
            target_profit=payload.get("target_profit", "100"),
            start_probability=start_probability,
            end_probability=end_probability,
            increment=increment,
        )
    else:
        raise ValueError("Wave mode must be 'target_profit' or 'fixed_stake'.")
    return {"mode": mode, "rows": rows}


CALCULATORS = {
    "/api/arb-math": calculate_arb_math,
    "/api/arb-reach": calculate_arb_reach,
    "/api/arb-wave": calculate_arb_wave,
    "/api/hedge-range": calculate_hedge_range,
    "/api/event-arb": calculate_event_arb,
}


class ToolsHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(json_value(data)).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        calculator = CALCULATORS.get(route)
        if calculator is None:
            self.send_json({"error": "Unknown tool endpoint."}, status=404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            self.send_json({"ok": True, "result": calculator(payload)})
        except (ValueError, KeyError, InvalidOperation, json.JSONDecodeError) as error:
            self.send_json({"ok": False, "error": str(error)}, status=400)
        except Exception as error:  # Keep the browser response readable for module errors.
            self.send_json({"ok": False, "error": str(error)}, status=500)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ToolsHandler)
    print(f"Jim Rockies tools available at http://{HOST}:{PORT}/tools.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Jim Rockies tools server.")
        server.server_close()
