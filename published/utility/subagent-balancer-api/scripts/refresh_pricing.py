"""Refresh the API pricing catalog from the official Gemini pricing page."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
import re
import urllib.request


DEFAULT_PRICING_URL = "https://ai.google.dev/gemini-api/docs/pricing"
THIS_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_OUTPUT_PATH = THIS_DIR.parent / "pricing_catalog.json"
TRACKED_MODELS = (
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.1-pro-preview",
)


def fetch_pricing_page(pricing_url: str = DEFAULT_PRICING_URL) -> str:
    """Download the official pricing page HTML."""
    request = urllib.request.Request(
        pricing_url,
        headers={"User-Agent": "gemini-skills-subagent-balancer-api/1.0"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="ignore")


def extract_page_last_updated(html_text: str) -> str | None:
    """Extract the official page last-updated marker."""
    match = re.search(r"Last updated ([0-9-]+ UTC)\.", html_text)
    return match.group(1) if match else None


def model_block(html_text: str, model_name: str) -> str:
    """Extract the HTML block for a single model section."""
    marker = f'id="{model_name}"'
    start = html_text.find(marker)
    if start == -1:
        raise ValueError(f"Could not find pricing section for {model_name}.")

    next_start = html_text.find('<div class="models-section">', start + len(marker))
    if next_start == -1:
        return html_text[start:]
    return html_text[start:next_start]


def strip_tags(raw_html: str) -> str:
    """Collapse HTML into readable text."""
    text = re.sub(r"<br\s*/?>", "\n", raw_html)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(" ".join(text.split()))


def extract_paid_cell(table_html: str, row_label: str) -> str:
    """Extract the paid-tier cell for a given pricing row label."""
    pattern = (
        r"<tr>\s*<td>"
        + re.escape(row_label)
        + r"</td>\s*<td>.*?</td>\s*<td>(.*?)</td>\s*</tr>"
    )
    match = re.search(pattern, table_html, flags=re.S)
    if not match:
        raise ValueError(f"Could not find paid-tier row '{row_label}'.")
    return strip_tags(match.group(1))


def extract_price_values(text: str) -> list[float]:
    """Extract numeric dollar values from pricing text."""
    return [float(value) for value in re.findall(r"\$([0-9]+(?:\.[0-9]+)?)", text)]


def parse_mode_table(model_html: str, mode_name: str) -> dict[str, dict[str, float]]:
    """Parse standard or batch pricing for a model block."""
    section_match = re.search(
        r"<section><h3[^>]*>"
        + re.escape(mode_name)
        + r"</h3><table class=\"pricing-table\">(.*?)</table></section>",
        model_html,
        flags=re.S,
    )
    if not section_match:
        raise ValueError(f"Could not find {mode_name} pricing table.")

    table_html = section_match.group(1)
    input_row = None
    for candidate in (
        "Input price",
        "Input price (text, image, video)",
    ):
        try:
            input_row = extract_paid_cell(table_html, candidate)
            break
        except ValueError:
            continue
    if input_row is None:
        raise ValueError(f"Could not find {mode_name} input pricing row.")

    output_row = extract_paid_cell(table_html, "Output price (including thinking tokens)")
    input_prices = extract_price_values(input_row)
    output_prices = extract_price_values(output_row)
    if not input_prices or not output_prices:
        raise ValueError(f"Could not parse {mode_name} price values.")

    parsed: dict[str, dict[str, float]] = {
        mode_name.lower(): {"input": input_prices[0], "output": output_prices[0]}
    }
    if len(input_prices) > 1 and len(output_prices) > 1:
        parsed[f"{mode_name.lower()}_long"] = {"input": input_prices[1], "output": output_prices[1]}
    return parsed


def parse_pricing_catalog(html_text: str) -> dict[str, object]:
    """Parse the pricing page into a tracked catalog structure."""
    models: dict[str, dict[str, dict[str, float]]] = {}
    for model_name in TRACKED_MODELS:
        block = model_block(html_text, model_name)
        model_prices: dict[str, dict[str, float]] = {}
        for mode_name in ("Standard", "Batch"):
            model_prices.update(parse_mode_table(block, mode_name))
        models[model_name] = model_prices

    return {
        "source_url": DEFAULT_PRICING_URL,
        "page_last_updated": extract_page_last_updated(html_text),
        "fetched_at_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "models": models,
    }


def refresh_catalog_file(
    pricing_url: str = DEFAULT_PRICING_URL,
    output_path: pathlib.Path = DEFAULT_OUTPUT_PATH,
) -> dict[str, object]:
    """Fetch, parse, and persist a fresh pricing catalog."""
    html_text = fetch_pricing_page(pricing_url)
    catalog = parse_pricing_catalog(html_text)
    catalog["source_url"] = pricing_url
    output_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    return catalog


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pricing-url", default=DEFAULT_PRICING_URL)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    catalog = refresh_catalog_file(
        pricing_url=args.pricing_url,
        output_path=pathlib.Path(args.output),
    )
    print(json.dumps(catalog, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
