"""Select the best billed Gemini API model for a task."""

from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys
from dataclasses import dataclass


THIS_DIR = pathlib.Path(__file__).resolve().parent
SKILL_DIR = THIS_DIR.parent
DEFAULT_PRICING_FILE = SKILL_DIR / "pricing_catalog.json"
REFRESHER_PATH = THIS_DIR / "refresh_pricing.py"
REFRESHER_SPEC = importlib.util.spec_from_file_location("subagent_balancer_api_refresh", REFRESHER_PATH)
REFRESHER = importlib.util.module_from_spec(REFRESHER_SPEC)
assert REFRESHER_SPEC and REFRESHER_SPEC.loader
sys.modules[REFRESHER_SPEC.name] = REFRESHER
REFRESHER_SPEC.loader.exec_module(REFRESHER)


MODEL_PROFILES = {
    "gemini-2.5-flash-lite": {"tier": "lite", "preview": False, "quality": 40},
    "gemini-2.5-flash": {"tier": "flash", "preview": False, "quality": 74},
    "gemini-2.5-pro": {"tier": "pro", "preview": False, "quality": 92},
    "gemini-3-flash-preview": {"tier": "flash", "preview": True, "quality": 82},
    "gemini-3.1-flash-lite-preview": {"tier": "lite", "preview": True, "quality": 58},
    "gemini-3.1-pro-preview": {"tier": "pro", "preview": True, "quality": 98},
}

DEFAULT_PRICES = {
    "gemini-2.5-flash-lite": {
        "standard": {"input": 0.10, "output": 0.40},
        "batch": {"input": 0.05, "output": 0.20},
    },
    "gemini-2.5-flash": {
        "standard": {"input": 0.30, "output": 2.50},
        "batch": {"input": 0.15, "output": 1.25},
    },
    "gemini-2.5-pro": {
        "standard": {"input": 1.25, "output": 10.00},
        "batch": {"input": 0.625, "output": 5.00},
        "standard_long": {"input": 2.50, "output": 15.00},
        "batch_long": {"input": 1.25, "output": 7.50},
    },
    "gemini-3-flash-preview": {
        "standard": {"input": 0.50, "output": 3.00},
        "batch": {"input": 0.25, "output": 1.50},
    },
    "gemini-3.1-flash-lite-preview": {
        "standard": {"input": 0.25, "output": 1.50},
        "batch": {"input": 0.125, "output": 0.75},
    },
    "gemini-3.1-pro-preview": {
        "standard": {"input": 2.00, "output": 12.00},
        "batch": {"input": 1.00, "output": 6.00},
        "standard_long": {"input": 4.00, "output": 18.00},
        "batch_long": {"input": 2.00, "output": 9.00},
    },
}

QUALITY_FLOORS = {
    "review": {"trivial": 22, "normal": 34, "hard": 50, "ambiguous": 64},
    "search": {"trivial": 18, "normal": 28, "hard": 44, "ambiguous": 58},
    "verification": {"trivial": 28, "normal": 40, "hard": 56, "ambiguous": 68},
    "implementation": {"trivial": 42, "normal": 66, "hard": 84, "ambiguous": 94},
    "refactor": {"trivial": 48, "normal": 72, "hard": 88, "ambiguous": 96},
}

BUDGET_ADJUSTMENTS = {
    "min-cost": -8,
    "balanced": 0,
    "quality-first": 8,
}

DEFAULT_TOKEN_ESTIMATES = {
    "small": {"input": 0.03, "output": 0.01},
    "medium": {"input": 0.12, "output": 0.04},
    "large": {"input": 0.35, "output": 0.12},
}


@dataclass
class ApiModel:
    """Known model configuration for cost-aware API routing."""

    name: str
    tier: str
    preview: bool
    quality: int
    prices: dict[str, dict[str, float]]

    def estimate_cost(
        self,
        delivery_mode: str,
        estimated_input_mtokens: float,
        estimated_output_mtokens: float,
    ) -> float:
        """Estimate total token cost in USD for the given task size."""
        price_key = delivery_mode
        if estimated_input_mtokens > 0.2 and f"{delivery_mode}_long" in self.prices:
            price_key = f"{delivery_mode}_long"
        price = self.prices[price_key]
        return (
            estimated_input_mtokens * price["input"]
            + estimated_output_mtokens * price["output"]
        )


def load_catalog_data(pricing_file: pathlib.Path | None) -> dict[str, object]:
    """Load pricing data from disk with a baked-in fallback."""
    fallback = {
        "source_url": REFRESHER.DEFAULT_PRICING_URL,
        "page_last_updated": "2026-03-18 UTC",
        "models": DEFAULT_PRICES,
    }
    if not pricing_file or not pricing_file.exists():
        return fallback
    try:
        data = json.loads(pricing_file.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("models"), dict):
            return data
    except Exception:
        pass
    return fallback


def maybe_refresh_catalog(
    pricing_file: pathlib.Path,
    refresh_pricing: bool,
    pricing_url: str,
) -> dict[str, object]:
    """Refresh pricing data on demand, then load the catalog."""
    if refresh_pricing:
        REFRESHER.refresh_catalog_file(pricing_url=pricing_url, output_path=pricing_file)
    return load_catalog_data(pricing_file)


def load_models(pricing_file: pathlib.Path | None = None) -> list[ApiModel]:
    """Load the API model catalog from disk or the built-in fallback."""
    catalog = load_catalog_data(pricing_file)
    model_prices = catalog.get("models", {})
    models: list[ApiModel] = []
    for name, profile in MODEL_PROFILES.items():
        prices = model_prices.get(name) or DEFAULT_PRICES.get(name)
        if not prices:
            continue
        models.append(
            ApiModel(
                name=name,
                tier=profile["tier"],
                preview=bool(profile["preview"]),
                quality=int(profile["quality"]),
                prices=prices,
            )
        )
    return models


def estimate_tokens(
    scope: str,
    estimated_input_mtokens: float | None,
    estimated_output_mtokens: float | None,
) -> tuple[float, float]:
    """Resolve explicit or default token estimates."""
    defaults = DEFAULT_TOKEN_ESTIMATES[scope]
    return (
        estimated_input_mtokens if estimated_input_mtokens is not None else defaults["input"],
        estimated_output_mtokens if estimated_output_mtokens is not None else defaults["output"],
    )


def required_quality(task_type: str, complexity: str, budget_mode: str) -> int:
    """Return the minimum acceptable quality score for the task."""
    base = QUALITY_FLOORS[task_type][complexity]
    adjusted = base + BUDGET_ADJUSTMENTS[budget_mode]
    return max(0, min(100, adjusted))


def value_score(model: ApiModel, estimated_cost: float, target_quality: int, budget_mode: str) -> float:
    """Score a model when no candidate cleanly satisfies the quality floor."""
    budget_weight = {"min-cost": 18, "balanced": 12, "quality-first": 6}[budget_mode]
    quality_gap = max(0, target_quality - model.quality)
    preview_penalty = 10 if model.preview else 0
    return model.quality * 2.5 - estimated_cost * budget_weight - quality_gap * 3 - preview_penalty


def choose_model(
    task_type: str,
    scope: str,
    complexity: str,
    budget_mode: str,
    delivery_mode: str,
    preferred_model: str | None,
    avoid_models: set[str],
    allow_preview: bool,
    estimated_input_mtokens: float | None,
    estimated_output_mtokens: float | None,
    pricing_file: pathlib.Path | None = None,
) -> dict[str, object]:
    """Select the cheapest acceptable API model for the task."""
    models = load_models(pricing_file)
    by_name = {model.name: model for model in models}
    input_mtokens, output_mtokens = estimate_tokens(
        scope=scope,
        estimated_input_mtokens=estimated_input_mtokens,
        estimated_output_mtokens=estimated_output_mtokens,
    )
    target_quality = required_quality(task_type, complexity, budget_mode)

    if preferred_model:
        preferred = by_name.get(preferred_model)
        if preferred and preferred.name not in avoid_models and (allow_preview or not preferred.preview):
            estimated_cost = preferred.estimate_cost(delivery_mode, input_mtokens, output_mtokens)
            return {
                "route": "subagent",
                "selected_model": preferred.name,
                "estimated_cost_usd": round(estimated_cost, 6),
                "reason": (
                    f"Explicit preference for {preferred.name} is allowed; "
                    f"estimated cost ${estimated_cost:.4f}."
                ),
                "ranked_candidates": [preferred.name],
            }
        return {
            "route": "local",
            "selected_model": None,
            "estimated_cost_usd": None,
            "reason": f"Preferred model {preferred_model} is unavailable or blocked by the preview policy.",
            "ranked_candidates": [model.name for model in models],
        }

    candidates: list[tuple[float, int, str]] = []
    fallback: list[tuple[float, float, str]] = []
    for model in models:
        if model.name in avoid_models:
            continue
        if not allow_preview and model.preview:
            continue

        estimated_cost = model.estimate_cost(delivery_mode, input_mtokens, output_mtokens)
        if model.quality >= target_quality:
            candidates.append((estimated_cost, -model.quality, model.name))
        fallback.append((value_score(model, estimated_cost, target_quality, budget_mode), estimated_cost, model.name))

    if candidates:
        candidates.sort()
        selected_cost, _, selected_name = candidates[0]
        selected = by_name[selected_name]
        ranked_candidates = [name for _, _, name in candidates]
        return {
            "route": "subagent",
            "selected_model": selected.name,
            "estimated_cost_usd": round(selected_cost, 6),
            "reason": (
                f"{selected.name} clears the quality floor ({target_quality}) for "
                f"task={task_type}, scope={scope}, complexity={complexity} at estimated cost ${selected_cost:.4f}."
            ),
            "ranked_candidates": ranked_candidates,
            "quality_floor": target_quality,
        }

    if not fallback:
        return {
            "route": "local",
            "selected_model": None,
            "estimated_cost_usd": None,
            "reason": "No acceptable API model remained after applying limits and preferences.",
            "ranked_candidates": [],
        }

    fallback.sort(reverse=True)
    _, selected_cost, selected_name = fallback[0]
    selected = by_name[selected_name]
    return {
        "route": "subagent",
        "selected_model": selected.name,
        "estimated_cost_usd": round(selected_cost, 6),
        "reason": (
            f"No model cleared the quality floor ({target_quality}); {selected.name} had the best "
            f"quality-to-cost tradeoff for task={task_type}, scope={scope}, complexity={complexity}."
        ),
        "ranked_candidates": [name for _, _, name in fallback],
        "quality_floor": target_quality,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--task-type",
        choices=["review", "search", "implementation", "verification", "refactor"],
        default="review",
    )
    parser.add_argument("--scope", choices=["small", "medium", "large"], default="medium")
    parser.add_argument(
        "--complexity",
        choices=["trivial", "normal", "hard", "ambiguous"],
        default="normal",
    )
    parser.add_argument(
        "--budget-mode",
        choices=["min-cost", "balanced", "quality-first"],
        default="balanced",
    )
    parser.add_argument("--delivery-mode", choices=["standard", "batch"], default="standard")
    parser.add_argument("--estimated-input-mtokens", type=float)
    parser.add_argument("--estimated-output-mtokens", type=float)
    parser.add_argument("--preferred-model")
    parser.add_argument("--avoid-model", action="append", default=[])
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--pricing-file", default=str(DEFAULT_PRICING_FILE))
    parser.add_argument("--refresh-pricing", action="store_true")
    parser.add_argument("--pricing-url", default=REFRESHER.DEFAULT_PRICING_URL)
    return parser


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    pricing_file = pathlib.Path(args.pricing_file)
    maybe_refresh_catalog(
        pricing_file=pricing_file,
        refresh_pricing=args.refresh_pricing,
        pricing_url=args.pricing_url,
    )
    result = choose_model(
        task_type=args.task_type,
        scope=args.scope,
        complexity=args.complexity,
        budget_mode=args.budget_mode,
        delivery_mode=args.delivery_mode,
        preferred_model=args.preferred_model,
        avoid_models=set(args.avoid_model),
        allow_preview=not args.no_preview,
        estimated_input_mtokens=args.estimated_input_mtokens,
        estimated_output_mtokens=args.estimated_output_mtokens,
        pricing_file=pricing_file,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
