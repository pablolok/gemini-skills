"""Tests for the API pricing refresh parser."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest


MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "skills"
    / "subagent-balancer-api"
    / "scripts"
    / "refresh_pricing.py"
)

SPEC = importlib.util.spec_from_file_location("subagent_balancer_api_refresh", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


# Claude pricing has no long-context (200k) split and no audio tier, so each
# paid-tier cell carries a single flat price.
def _model_section(model_id: str, std_in: str, std_out: str, batch_in: str, batch_out: str) -> str:
    return f"""
    <div class="models-section">
      <div class="heading-group">
        <h2 id="{model_id}" data-text="{model_id}" tabindex="-1">{model_id}</h2>
      </div>
    </div>
    <div class="ds-selector-tabs" data-ds-scope="code-sample">
      <section><h3 id="standard_{model_id}" data-text="Standard" tabindex="-1">Standard</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>-</td><td>${std_in}</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>-</td><td>${std_out}</td></tr>
        </tbody>
      </table></section>
      <section><h3 id="batch_{model_id}" data-text="Batch" tabindex="-1">Batch</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>-</td><td>${batch_in}</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>-</td><td>${batch_out}</td></tr>
        </tbody>
      </table></section>
    </div>
"""


HTML_SNIPPET = (
    """
<html>
  <body>
    <p>Last updated 2026-06-24 UTC.</p>
"""
    + _model_section("claude-haiku-4-5", "1.00", "5.00", "0.50", "2.50")
    + _model_section("claude-sonnet-5", "3.00", "15.00", "1.50", "7.50")
    + _model_section("claude-opus-4-8", "5.00", "25.00", "2.50", "12.50")
    + _model_section("claude-fable-5", "5.00", "25.00", "2.50", "12.50")
    + """
  </body>
</html>
"""
)


class TestSubagentBalancerApiRefresh(unittest.TestCase):
    """Verify parsing of the official pricing page format."""

    def test_extract_page_last_updated(self) -> None:
        self.assertEqual(MODULE.extract_page_last_updated(HTML_SNIPPET), "2026-06-24 UTC")

    def test_parse_pricing_catalog(self) -> None:
        catalog = MODULE.parse_pricing_catalog(HTML_SNIPPET)
        self.assertEqual(catalog["page_last_updated"], "2026-06-24 UTC")
        self.assertEqual(catalog["models"]["claude-haiku-4-5"]["standard"]["input"], 1.0)
        self.assertEqual(catalog["models"]["claude-sonnet-5"]["standard"]["output"], 15.0)
        self.assertEqual(catalog["models"]["claude-opus-4-8"]["batch"]["output"], 12.5)
        # Claude has no long-context premium, so no *_long price keys are parsed.
        self.assertNotIn("standard_long", catalog["models"]["claude-opus-4-8"])


if __name__ == "__main__":
    unittest.main()
