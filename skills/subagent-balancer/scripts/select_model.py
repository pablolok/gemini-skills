"""Select a Gemini subagent model from a quota snapshot."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass


KNOWN_MODELS = {
    "gemini-1.5-flash-8b": {"tier": "lite", "preview": False},
    "gemini-1.5-flash": {"tier": "flash", "preview": False},
    "gemini-1.5-pro": {"tier": "pro", "preview": False},
    "gemini-2.0-flash": {"tier": "flash", "preview": False},
    "gemini-2.0-flash-lite-preview-02-05": {"tier": "lite", "preview": True},
    "gemini-2.0-pro-exp-02-05": {"tier": "pro", "preview": True},
}

TIER_WEIGHTS = {
    "review": {"lite": 10, "flash": 4, "pro": 2},
    "search": {"lite": 10, "flash": 4, "pro": 2},
    "verification": {"lite": 8, "flash": 4, "pro": 3},
    "implementation": {"lite": 1, "flash": 4, "pro": 8},
    "refactor": {"lite": 1, "flash": 4, "pro": 8},
}

SCOPE_BONUS = {
    "small": {"lite": 6, "flash": 1, "pro": 0},
    "medium": {"lite": 0, "flash": 3, "pro": 2},
    "large": {"lite": -6, "flash": 0, "pro": 6},
}

MODEL_RE = re.compile(r"(gemini-\S+)")
PERCENT_RE = re.compile(r"(\d+)%")


@dataclass
class ModelQuota:
    """Parsed quota information for a single model."""

    name: str
    limited: bool
    usage_percent: int | None
    reset_text: str

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


def parse_snapshot(text: str) -> list[ModelQuota]:
    """Parse a Gemini quota table into model quota entries."""
    models: list[ModelQuota] = []

    # Flatten and split by whitespace to handle dense tables
    tokens = text.replace(",", " ").replace(":", " ").replace(")", " ").split()
    
    current_model = None
    for i, token in enumerate(tokens):
        if token.startswith("gemini-"):
            # If we were tracking a model, save it
            if current_model:
                models.append(current_model)
            
            name = token
            # Look ahead for percentage
            usage_percent = None
            limited = False
            
            # Search next 5 tokens for status
            for j in range(1, 6):
                if i + j >= len(tokens):
                    break
                next_token = tokens[i+j]
                if next_token.startswith("gemini-"):
                    break
                if "limit" in next_token.lower():
                    limited = True
                percent_match = PERCENT_RE.search(next_token)
                if percent_match and usage_percent is None:
                    usage_percent = int(percent_match.group(1))

            current_model = ModelQuota(
                name=name,
                limited=limited,
                usage_percent=usage_percent,
                reset_text=" ".join(tokens[i+1:i+6]) # Heuristic reset text
            )

    if current_model:
        models.append(current_model)

    return models


def choose_model(
    models: list[ModelQuota],
    task_type: str,
    scope: str,
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
        usage_weight = 100 - (model.usage_percent or 0)
        preview_penalty = -20 if model.preview else 0
        score = task_weight * 30 + scope_weight * 15 + usage_weight + preview_penalty
        ranked.append((score, model.name, model.reset_text))

    ranked.sort(reverse=True)

    if not ranked:
        return {
            "route": "local",
            "selected_model": None,
            "reason": "No acceptable model remained after applying limits and preferences.",
            "ranked_candidates": [m.name for m in visible],
        }

    selected_score, selected_model, _ = ranked[0]
    selected_quota = by_name[selected_model]
    return {
        "route": "subagent",
        "selected_model": selected_model,
        "reason": (
            f"{selected_model} scored highest for task={task_type}, scope={scope}, "
            f"usage={selected_quota.usage_percent}%."
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
        preferred_model=args.preferred_model,
        avoid_models=set(args.avoid_model),
        allow_preview=not args.no_preview,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
