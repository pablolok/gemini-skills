"""Select a Gemini subagent model from a quota snapshot."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass


KNOWN_MODELS = {
    "gemini-1.5-flash-8b": {"tier": "lite", "preview": False, "scarcity": 14},
    "gemini-1.5-flash": {"tier": "flash", "preview": False, "scarcity": 8},
    "gemini-1.5-pro": {"tier": "pro", "preview": False, "scarcity": -6},
    "gemini-2.0-flash": {"tier": "flash", "preview": False, "scarcity": 6},
    "gemini-2.0-flash-lite-preview-02-05": {"tier": "lite", "preview": True, "scarcity": 6},
    "gemini-2.0-pro-exp-02-05": {"tier": "pro", "preview": True, "scarcity": -12},
    "gemini-2.5-flash-lite": {"tier": "lite", "preview": False, "scarcity": 20},
    "gemini-2.5-flash": {"tier": "flash", "preview": False, "scarcity": 12},
    "gemini-2.5-pro": {"tier": "pro", "preview": False, "scarcity": -10},
    "gemini-3-flash-preview": {"tier": "flash", "preview": True, "scarcity": 2},
    "gemini-3.1-pro-preview": {"tier": "pro", "preview": True, "scarcity": -18},
}

TIER_WEIGHTS = {
    "review": {"lite": 12, "flash": 5, "pro": 1},
    "search": {"lite": 12, "flash": 5, "pro": 1},
    "verification": {"lite": 10, "flash": 6, "pro": 2},
    "implementation": {"lite": 1, "flash": 11, "pro": 4},
    "refactor": {"lite": 0, "flash": 9, "pro": 6},
}

SCOPE_BONUS = {
    "small": {"lite": 6, "flash": 2, "pro": -4},
    "medium": {"lite": 0, "flash": 3, "pro": 0},
    "large": {"lite": -6, "flash": 3, "pro": 2},
}

MODEL_RE = re.compile(r"(gemini-\S+)")
PERCENT_RE = re.compile(r"(\d+)%")
RESET_WINDOW_RE = re.compile(r"\((?:(?P<days>\d+)d)?\s*(?:(?P<hours>\d+)h)?\s*(?:(?P<minutes>\d+)m)?\)")

TIER_ECONOMY_BONUS = {
    "lite": 15,
    "flash": 8,
    "pro": -12,
}

COMPLEXITY_ESCALATION = {
    ("implementation", "large"): {"pro": 10},
    ("refactor", "large"): {"pro": 18},
}

COMPLEXITY_WEIGHTS = {
    "trivial": {"lite": 8, "flash": 3, "pro": -10},
    "normal": {"lite": 1, "flash": 5, "pro": 0},
    "hard": {"lite": -10, "flash": 2, "pro": 14},
    "ambiguous": {"lite": -14, "flash": 0, "pro": 18},
}

COMPLEXITY_ESCALATION_BY_LEVEL = {
    "hard": {"pro": 42},
    "ambiguous": {"pro": 56},
}


@dataclass
class ModelQuota:
    """Parsed quota information for a single model."""

    name: str
    limited: bool
    usage_percent: int | None
    reset_text: str
    reset_window_minutes: int | None

    @property
    def tier(self) -> str:
        """Return the tier of the model."""
        if self.name in KNOWN_MODELS:
            return KNOWN_MODELS[self.name]["tier"]
        lower = self.name.lower()
        if "pro" in lower:
            return "pro"
        if "lite" in lower or "8b" in lower:
            return "lite"
        if "flash" in lower:
            return "flash"
        return "unknown"

    @property
    def preview(self) -> bool:
        """Return whether the model is a preview model."""
        if self.name in KNOWN_MODELS:
            return bool(KNOWN_MODELS[self.name]["preview"])
        lower = self.name.lower()
        return "preview" in lower or "exp" in lower

    @property
    def scarcity_bonus(self) -> int:
        """Return a model-specific scarcity bonus."""
        if self.name in KNOWN_MODELS:
            return int(KNOWN_MODELS[self.name].get("scarcity", 0))
        if self.preview:
            return -8 if self.tier == "flash" else -14
        if self.tier == "lite":
            return 12
        if self.tier == "flash":
            return 6
        if self.tier == "pro":
            return -8
        return 0


def parse_snapshot(text: str) -> list[ModelQuota]:
    """Parse a Gemini quota table into model quota entries."""
    models: list[ModelQuota] = []

    for raw_line in text.splitlines():
        line = " ".join(raw_line.strip().split())
        if "gemini-" not in line:
            continue

        model_match = MODEL_RE.search(line)
        if not model_match:
            continue

        name = model_match.group(1).rstrip(",:)")
        limited = " limit " in f" {line.lower()} "
        percent_match = PERCENT_RE.search(line)
        usage_percent = None if limited or not percent_match else int(percent_match.group(1))
        reset_text = line.split(name, 1)[1].strip()
        reset_window_minutes = parse_reset_window_minutes(reset_text)

        models.append(
            ModelQuota(
                name=name,
                limited=limited,
                usage_percent=usage_percent,
                reset_text=reset_text,
                reset_window_minutes=reset_window_minutes,
            )
        )

    return models


def parse_reset_window_minutes(reset_text: str) -> int | None:
    """Extract a relative reset window from free-form text."""
    match = RESET_WINDOW_RE.search(reset_text)
    if not match:
        return None

    days = int(match.group("days") or 0)
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    total_minutes = days * 24 * 60 + hours * 60 + minutes
    return total_minutes if total_minutes > 0 else None


def build_reason(
    selected_quota: ModelQuota,
    task_type: str,
    scope: str,
    complexity: str,
    allow_preview: bool,
) -> str:
    """Build a concise explanation for the winning model."""
    usage = (
        f"{selected_quota.usage_percent}% used"
        if selected_quota.usage_percent is not None
        else "usage unavailable"
    )
    reset = selected_quota.reset_text or "reset unknown"
    preview_policy = "preview allowed" if allow_preview else "preview blocked"
    return (
        f"{selected_quota.name} best fits task={task_type}, scope={scope}, complexity={complexity}; "
        f"{usage}, {reset}, {preview_policy}."
    )


def compute_reset_bonus(model: ModelQuota) -> int:
    """Score reset timing proportionally with stronger penalties for constrained models."""
    if model.reset_window_minutes is None:
        return 0

    usage_percent = model.usage_percent or 0
    hours_until_reset = max(model.reset_window_minutes / 60, 1)
    if usage_percent >= 85:
        return max(-22, 16 - int(hours_until_reset))
    if usage_percent >= 70:
        return max(-14, 12 - int(hours_until_reset / 1.5))
    if usage_percent >= 40:
        return max(-6, 8 - int(hours_until_reset / 3))
    return max(-2, 6 - int(hours_until_reset / 6))


def compute_usage_penalty(model: ModelQuota) -> int:
    """Penalize heavily-used models so scarce tiers are preserved longer."""
    usage_percent = model.usage_percent or 0
    if usage_percent >= 90:
        return -30
    if usage_percent >= 80:
        return -20
    if usage_percent >= 70:
        return -10
    return 0


def choose_model(
    models: list[ModelQuota],
    task_type: str,
    scope: str,
    complexity: str,
    preferred_model: str | None,
    avoid_models: set[str],
    allow_preview: bool,
) -> dict[str, object]:
    """Choose the best model or return a local fallback."""
    valid_candidates = [m for m in models if m.tier != "unknown"]
    if not valid_candidates:
        return {
            "route": "local",
            "selected_model": None,
            "reason": "No valid Gemini models were parsed from the quota snapshot.",
            "ranked_candidates": [],
        }

    by_name = {model.name: model for model in valid_candidates}
    if preferred_model:
        preferred = by_name.get(preferred_model)
        if preferred and not preferred.limited and (allow_preview or not preferred.preview):
            return {
                "route": "subagent",
                "selected_model": preferred.name,
                "reason": f"Explicit preference for {preferred.name} is available and allowed.",
                "ranked_candidates": [preferred.name],
            }

        return {
            "route": "local",
            "selected_model": None,
            "reason": f"Preferred model {preferred_model} is unavailable or blocked by the preview policy.",
            "ranked_candidates": [m.name for m in valid_candidates],
        }

    ranked: list[tuple[int, str, str]] = []
    for model in valid_candidates:
        if model.name in avoid_models:
            continue
        if model.limited:
            continue
        if not allow_preview and model.preview:
            continue

        task_weight = TIER_WEIGHTS.get(task_type, TIER_WEIGHTS["review"]).get(model.tier, 0)
        scope_weight = SCOPE_BONUS.get(scope, SCOPE_BONUS["medium"]).get(model.tier, 0)
        complexity_weight = COMPLEXITY_WEIGHTS.get(complexity, COMPLEXITY_WEIGHTS["normal"]).get(model.tier, 0)
        economy_bonus = TIER_ECONOMY_BONUS.get(model.tier, 0)
        scarcity_bonus = model.scarcity_bonus
        escalation_bonus = COMPLEXITY_ESCALATION.get((task_type, scope), {}).get(model.tier, 0)
        complexity_escalation = COMPLEXITY_ESCALATION_BY_LEVEL.get(complexity, {}).get(model.tier, 0)
        usage_weight = 100 - (model.usage_percent or 0)
        usage_penalty = compute_usage_penalty(model)
        reset_bonus = compute_reset_bonus(model)
        preview_penalty = -20 if model.preview else 0
        score = (
            task_weight * 25
            + scope_weight * 12
            + complexity_weight * 18
            + economy_bonus
            + scarcity_bonus
            + escalation_bonus
            + complexity_escalation
            + usage_weight
            + usage_penalty
            + reset_bonus
            + preview_penalty
        )
        ranked.append((score, model.name, model.reset_text))

    ranked.sort(reverse=True)

    if not ranked:
        return {
            "route": "local",
            "selected_model": None,
            "reason": "No acceptable model remained after applying limits and preferences.",
            "ranked_candidates": [m.name for m in valid_candidates],
        }

    selected_score, selected_model, _ = ranked[0]
    selected_quota = by_name[selected_model]
    return {
        "route": "subagent",
        "selected_model": selected_model,
        "reason": build_reason(
            selected_quota=selected_quota,
            task_type=task_type,
            scope=scope,
            complexity=complexity,
            allow_preview=allow_preview,
        ),
        "ranked_candidates": [name for _, name, _ in ranked],
        "score": selected_score,
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot-file", help="Path to a text file containing the quota snapshot.")
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
    parser.add_argument("--preferred-model")
    parser.add_argument("--avoid-model", action="append", default=[])
    parser.add_argument("--no-preview", action="store_true")
    return parser


def load_snapshot_text(snapshot_file: str | None) -> str:
    """Load snapshot text from a file or stdin."""
    if snapshot_file:
        with open(snapshot_file, "r", encoding="utf-8") as handle:
            return handle.read()
    return sys.stdin.read()


def main() -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    snapshot_text = load_snapshot_text(args.snapshot_file)
    models = parse_snapshot(snapshot_text)
    result = choose_model(
        models=models,
        task_type=args.task_type,
        scope=args.scope,
        complexity=args.complexity,
        preferred_model=args.preferred_model,
        avoid_models=set(args.avoid_model),
        allow_preview=not args.no_preview,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
