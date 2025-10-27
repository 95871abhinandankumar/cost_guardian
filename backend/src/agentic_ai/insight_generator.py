"""
insight_generator.py

Insight Generator - Natural language Bedrock reasoning layer.

Purpose:
- Read enhanced analysis results
- Summarize trends, anomalies, and forecasts
- Generate human-readable insights using Bedrock or fallback logic
- Append insights back into analysis_output.json for dashboard use

Example output:
"Your EC2 spend in us-east-1 increased 12% week-over-week, likely due to Dev workload spikes.
Storage usage remained stable. Consider reviewing EC2 instance rightsizing and budget alerts."
"""

from __future__ import annotations
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict
from agentic_ai.llm_engine import LLMEvaluator

# Setup logging
logger = logging.getLogger("InsightGenerator")
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

# File paths
ROOT = Path.cwd()
ANALYSIS_PATH = ROOT / "src" / "agentic_ai" / "analysis_output.json"


class InsightGenerator:
    """Generate cost insights using Bedrock-based reasoning (fallback to deterministic logic)."""

    def __init__(self):
        self.engine = LLMEvaluator()

    # ----------------------------------------------------------------------
    # Public interface
    # ----------------------------------------------------------------------
    def generate_insight(
        self,
        analysis_output_path: str | Path = ANALYSIS_PATH,
        analysis_data: Dict[str, Any] | None = None,
        append_to_file: bool = True,
    ) -> str:
        """
        Generate and optionally append natural-language insight to analysis_output.json.

        Args:
            analysis_output_path: Path to analysis_output.json
            analysis_data: Already loaded dict (optional)
            append_to_file: Whether to update file with generated insight

        Returns:
            str: Generated insight paragraph
        """
        if not analysis_data and analysis_output_path:
            try:
                with open(analysis_output_path, "r", encoding="utf-8") as f:
                    analysis_data = json.load(f)
            except FileNotFoundError:
                logger.error("❌ analysis_output.json not found. Run enhanced_analysis.py first.")
                return ""
            except Exception as e:
                logger.exception("Failed to read analysis file: %s", e)
                return ""

        # Summarize relevant data for prompt
        summary = {
            "dashboard": analysis_data.get("dashboard"),
            "summary": analysis_data.get("summary", {}),
            "anomalies": analysis_data.get("anomalies", [])[:5],
            "forecast": analysis_data.get("forecast", {}),
            "recommendations": analysis_data.get("recommendations", [])[:3],
        }

        # Build LLM reasoning prompt
        prompt = f"""
You are a FinOps cloud cost analyst.
Your job is to summarize this data for an executive dashboard in 3 concise sentences:
1. Highlight major trends or shifts in cost.
2. Mention anomalies, spikes, or regional/service drivers.
3. End with a proactive recommendation.

Return only a human-readable paragraph (no JSON, no markdown).

Context:
{json.dumps(summary, indent=2)}
"""

        try:
            logger.info("🧠 Invoking Bedrock for reasoning-based insight generation...")
            response = self.engine.invoke_model(prompt, deterministic=False)
            if isinstance(response, dict):
                insight_text = response.get("text") or json.dumps(response)
            else:
                insight_text = str(response)
            logger.info("✅ Insight generated successfully via Bedrock.")
        except Exception as e:
            logger.warning("⚠️ Bedrock failed (%s). Using local fallback...", e)
            insight_text = self._local_fallback(summary)

        # Optionally append to file for dashboard use
        if append_to_file:
            try:
                analysis_data["insight_summary"] = {
                    "text": insight_text,
                    "engine_used": "bedrock" if "Fallback" not in insight_text else "mock",
                }
                with open(analysis_output_path, "w", encoding="utf-8") as f:
                    json.dump(analysis_data, f, indent=2, ensure_ascii=False)
                logger.info("📝 Insight appended to analysis_output.json")
            except Exception as e:
                logger.exception("Failed to append insight to file: %s", e)

        return insight_text

    # ----------------------------------------------------------------------
    # Local deterministic fallback
    # ----------------------------------------------------------------------
    def _local_fallback(self, summary: Dict[str, Any]) -> str:
        """Generate a basic fallback insight when Bedrock is offline."""
        anomalies = summary.get("anomalies", [])
        forecast = summary.get("forecast", {})
        total_cost = summary.get("summary", {}).get("total_cost_usd", "N/A")
        dashboard = summary.get("dashboard", "General")

        if anomalies:
            top = anomalies[0]
            service = top.get("service_name") or top.get("service") or "unknown service"
            region = top.get("region", "global")
            return (
                f"{dashboard} costs show {len(anomalies)} anomalies, primarily in {service} ({region}). "
                f"Total spend is around ${total_cost}. Forecast suggests a slight upward trend. "
                "Recommend reviewing top spenders and optimizing EC2 instances or S3 tiers."
            )
        else:
            return (
                f"{dashboard} costs appear stable with no significant anomalies. "
                f"Total spend is approximately ${total_cost}. "
                "Expect consistent spend next cycle; maintain current optimization policies."
            )


# ----------------------------------------------------------------------
# Standalone execution
# ----------------------------------------------------------------------
if __name__ == "__main__":
    generator = InsightGenerator()
    if ANALYSIS_PATH.exists():
        insight = generator.generate_insight(ANALYSIS_PATH)
        print("\n🧠 Bedrock Insight Summary:\n")
        print("=" * 70)
        print(insight)
        print("=" * 70)
    else:
        print("❌ No analysis_output.json found. Run enhanced_analysis.py first.")
