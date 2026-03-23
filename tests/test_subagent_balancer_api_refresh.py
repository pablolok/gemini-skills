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


HTML_SNIPPET = """
<html>
  <body>
    <p>Last updated 2026-03-18 UTC.</p>
    <div class="models-section">
      <div class="heading-group">
        <h2 id="gemini-2.5-flash" data-text="Gemini 2.5 Flash" tabindex="-1">Gemini 2.5 Flash</h2>
      </div>
    </div>
    <div class="ds-selector-tabs" data-ds-scope="code-sample">
      <section><h3 id="standard_a" data-text="Standard" tabindex="-1">Standard</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Free of charge</td><td>$0.30 (text / image / video)<br>$1.00 (audio)</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Free of charge</td><td>$2.50</td></tr>
        </tbody>
      </table></section>
      <section><h3 id="batch_a" data-text="Batch" tabindex="-1">Batch</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Not available</td><td>$0.15 (text / image / video)<br>$0.50 (audio)</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Not available</td><td>$1.25</td></tr>
        </tbody>
      </table></section>
    </div>
    <div class="models-section">
      <div class="heading-group">
        <h2 id="gemini-2.5-pro" data-text="Gemini 2.5 Pro" tabindex="-1">Gemini 2.5 Pro</h2>
      </div>
    </div>
    <div class="ds-selector-tabs" data-ds-scope="code-sample">
      <section><h3 id="standard_b" data-text="Standard" tabindex="-1">Standard</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Free of charge</td><td>$1.25, prompts &lt;= 200k tokens<br>$2.50, prompts &gt; 200k tokens</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Free of charge</td><td>$10.00, prompts &lt;= 200k tokens<br>$15.00, prompts &gt; 200k</td></tr>
        </tbody>
      </table></section>
      <section><h3 id="batch_b" data-text="Batch" tabindex="-1">Batch</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Not available</td><td>$0.625, prompts &lt;= 200k tokens<br>$1.25, prompts &gt; 200k tokens</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Not available</td><td>$5.00, prompts &lt;= 200k tokens<br>$7.50, prompts &gt; 200k</td></tr>
        </tbody>
      </table></section>
    </div>
    <div class="models-section">
      <div class="heading-group">
        <h2 id="gemini-2.5-flash-lite" data-text="Gemini 2.5 Flash-Lite" tabindex="-1">Gemini 2.5 Flash-Lite</h2>
      </div>
    </div>
    <div class="ds-selector-tabs" data-ds-scope="code-sample">
      <section><h3 id="standard_c" data-text="Standard" tabindex="-1">Standard</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price (text, image, video)</td><td>Free of charge</td><td>$0.10 (text / image / video)<br>$0.30 (audio)</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Free of charge</td><td>$0.40</td></tr>
        </tbody>
      </table></section>
      <section><h3 id="batch_c" data-text="Batch" tabindex="-1">Batch</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price (text, image, video)</td><td>Not available</td><td>$0.05 (text / image / video)<br>$0.15 (audio)</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Not available</td><td>$0.20</td></tr>
        </tbody>
      </table></section>
    </div>
    <div class="models-section">
      <div class="heading-group">
        <h2 id="gemini-3-flash-preview" data-text="Gemini 3 Flash Preview" tabindex="-1">Gemini 3 Flash Preview</h2>
      </div>
    </div>
    <div class="ds-selector-tabs" data-ds-scope="code-sample">
      <section><h3 id="standard_d" data-text="Standard" tabindex="-1">Standard</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Not available</td><td>$0.50 (text / image / video)<br>$1.00 (audio)</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Not available</td><td>$3.00</td></tr>
        </tbody>
      </table></section>
      <section><h3 id="batch_d" data-text="Batch" tabindex="-1">Batch</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Not available</td><td>$0.25 (text / image / video)<br>$0.50 (audio)</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Not available</td><td>$1.50</td></tr>
        </tbody>
      </table></section>
    </div>
    <div class="models-section">
      <div class="heading-group">
        <h2 id="gemini-3.1-flash-lite-preview" data-text="Gemini 3.1 Flash-Lite Preview" tabindex="-1">Gemini 3.1 Flash-Lite Preview</h2>
      </div>
    </div>
    <div class="ds-selector-tabs" data-ds-scope="code-sample">
      <section><h3 id="standard_e" data-text="Standard" tabindex="-1">Standard</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Free of charge</td><td>$0.25 (text / image / video)<br>$0.50 (audio)</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Free of charge</td><td>$1.50</td></tr>
        </tbody>
      </table></section>
      <section><h3 id="batch_e" data-text="Batch" tabindex="-1">Batch</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Not available</td><td>$0.125 (text / image / video)<br>$0.25 (audio)</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Not available</td><td>$0.75</td></tr>
        </tbody>
      </table></section>
    </div>
    <div class="models-section">
      <div class="heading-group">
        <h2 id="gemini-3.1-pro-preview" data-text="Gemini 3.1 Pro Preview" tabindex="-1">Gemini 3.1 Pro Preview</h2>
      </div>
    </div>
    <div class="ds-selector-tabs" data-ds-scope="code-sample">
      <section><h3 id="standard_f" data-text="Standard" tabindex="-1">Standard</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Not available</td><td>$2.00, prompts &lt;= 200k tokens<br>$4.00, prompts &gt; 200k tokens</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Not available</td><td>$12.00, prompts &lt;= 200k tokens<br>$18.00, prompts &gt; 200k</td></tr>
        </tbody>
      </table></section>
      <section><h3 id="batch_f" data-text="Batch" tabindex="-1">Batch</h3><table class="pricing-table">
        <tbody>
          <tr><td>Input price</td><td>Not available</td><td>$1.00, prompts &lt;= 200k tokens<br>$2.00, prompts &gt; 200k tokens</td></tr>
          <tr><td>Output price (including thinking tokens)</td><td>Not available</td><td>$6.00, prompts &lt;= 200k tokens<br>$9.00, prompts &gt; 200k</td></tr>
        </tbody>
      </table></section>
    </div>
  </body>
</html>
"""


class TestSubagentBalancerApiRefresh(unittest.TestCase):
    """Verify parsing of the official pricing page format."""

    def test_extract_page_last_updated(self) -> None:
        self.assertEqual(MODULE.extract_page_last_updated(HTML_SNIPPET), "2026-03-18 UTC")

    def test_parse_pricing_catalog(self) -> None:
        catalog = MODULE.parse_pricing_catalog(HTML_SNIPPET)
        self.assertEqual(catalog["page_last_updated"], "2026-03-18 UTC")
        self.assertEqual(catalog["models"]["gemini-2.5-flash"]["standard"]["input"], 0.3)
        self.assertEqual(catalog["models"]["gemini-2.5-pro"]["standard_long"]["output"], 15.0)
        self.assertEqual(catalog["models"]["gemini-3.1-pro-preview"]["batch_long"]["input"], 2.0)


if __name__ == "__main__":
    unittest.main()
