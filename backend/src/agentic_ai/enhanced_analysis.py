"""
enhanced_analysis.py

Enhanced analysis runner for Agentic AI:
- Uses local dataset (src/data/raw_data.json)
- Invokes LLMEngine (Bedrock preferred, SageMaker fallback)
- Ensures explicit anomaly flags are honored
- Calculates week-over-week cost trends
- Appends Bedrock-generated insights
- Writes structured JSON to src/agentic_ai/analysis_output.json
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

from dotenv import load_dotenv
from agentic_ai.llm_engine import LLMEvaluator  # alias for LLMEngine
from agentic_ai.insight_generator import InsightGenerator

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("enhanced_analysis")

# Paths
ROOT = Path.cwd()
DATA_PATH = ROOT / "src" / "data" / "raw_data.json"
OUTPUT_PATH = ROOT / "src" / "agentic_ai" / "analysis_output.json"

DEFAULT_QUERY = "Detect anomalies and forecast next month's cloud cost trends"
DEFAULT_HORIZON_DAYS = 30


# ----------------------------------------------------------------------
# Data Utilities
# ----------------------------------------------------------------------
def load_raw_data(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        logger.error("Raw data file not found at %s", path)
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            doc = json.load(f)
            if isinstance(doc, list):
                return doc
            if isinstance(doc, dict) and "records" in doc and isinstance(doc["records"], list):
                return doc["records"]
            return [doc]
    except Exception as e:
        logger.exception("Failed to load raw data: %s", e)
        return []


def extract_explicit_anomalies(dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in dataset:
        try:
            if r.get("anomaly_flag") is True:
                out.append(r)
            else:
                score = float(r.get("anomaly_score", 0) or 0)
                if score >= 0.8:
                    out.append(r)
        except Exception:
            continue
    return out


def merge_model_and_explicit_anomalies(model_result: Dict[str, Any], explicit_anoms: List[Dict[str, Any]]):
    model_anoms = model_result.get("anomalies") or []
    seen = set()
    merged = []

    def key_for(r: Dict[str, Any]) -> str:
        return f"{r.get('service_name') or r.get('service')}_{r.get('resource_id') or r.get('account_id')}_{r.get('usage_date') or r.get('date') or ''}"

    for r in model_anoms:
        k = key_for(r)
        seen.add(k)
        merged.append(r)

    for r in explicit_anoms:
        k = key_for(r)
        if k not in seen:
            cleaned = {
                "service_name": r.get("service_name") or r.get("service"),
                "resource_id": r.get("resource_id"),
                "account_id": r.get("account_id"),
                "usage_date": r.get("usage_date") or r.get("date"),
                "cost": r.get("cost"),
                "anomaly_score": r.get("anomaly_score", None),
                "anomaly_flag": True,
            }
            merged.append(cleaned)
            seen.add(k)

    model_result["anomalies"] = merged
    model_result["anomaly_summary"] = {"count": len(merged)}
    return model_result


# ----------------------------------------------------------------------
# Week-over-week cost change detection
# ----------------------------------------------------------------------
def compute_weekly_cost_change(dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute week-over-week cost change if usage_date/date is available."""
    try:
        # Parse and sort by date
        records = [
            (datetime.fromisoformat(r.get("usage_date") or r.get("date")), float(r.get("cost", 0) or 0))
            for r in dataset
            if r.get("usage_date") or r.get("date")
        ]
        records.sort(key=lambda x: x[0])
        if len(records) < 14:
            return {"week_over_week_change": None}

        last_7 = sum(v for (_, v) in records[-7:])
        prev_7 = sum(v for (_, v) in records[-14:-7])
        if prev_7 == 0:
            pct_change = 0
        else:
            pct_change = ((last_7 - prev_7) / prev_7) * 100

        direction = "increase" if pct_change > 5 else "decrease" if pct_change < -5 else "stable"
        return {
            "week_over_week_change": {
                "previous_week_cost": round(prev_7, 2),
                "current_week_cost": round(last_7, 2),
                "percent_change": round(pct_change, 2),
                "trend_direction": direction,
            }
        }
    except Exception as e:
        logger.warning(f"Failed WoW computation: {e}")
        return {"week_over_week_change": None}


# ----------------------------------------------------------------------
# Console summary
# ----------------------------------------------------------------------
def short_summary_and_save(result: Dict[str, Any], out_path: Path):
    dashboard = result.get("dashboard", "unknown").upper()
    summary = result.get("summary", {})
    anomalies = result.get("anomalies", [])
    recs = result.get("recommendations", [])

    print("\n" + "=" * 72)
    print("COST GUARDIAN — ENHANCED ANALYSIS RESULT")
    print("=" * 72)
    print(f"Dashboard       : {dashboard}")
    print(f"Records analyzed: {summary.get('records', 'N/A')}")
    print(f"Total cost (USD): {summary.get('total_cost_usd', 'N/A')}")
    print(f"Forecast method : {result.get('forecast_meta', {}).get('method', 'N/A')}")
    print(f"Anomalies found : {len(anomalies)}")

    if summary.get("week_over_week_change"):
        wow = summary["week_over_week_change"]
        print(f"\nWeek-over-week change: {wow['percent_change']}% ({wow['trend_direction']})")

    if anomalies:
        print("\nTop anomalies (up to 3):")
        for a in anomalies[:3]:
            print(f" - {a.get('service_name')} | {a.get('region','-')} | cost={a.get('cost')} | score={a.get('anomaly_score', 'N/A')}")

    if recs:
        print("\nTop recommendations (up to 5):")
        for r in recs[:5]:
            print(f" - {r}")
    print("=" * 72 + "\n")

    # Save JSON for dashboard
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    logger.info("Saved analysis output to %s", out_path)


# ----------------------------------------------------------------------
# Main pipeline
# ----------------------------------------------------------------------
def run_enhanced_analysis(query: str = DEFAULT_QUERY, horizon_days: int = DEFAULT_HORIZON_DAYS, force_refresh: bool = True):
    logger.info("Starting enhanced analysis. Loading raw data from %s", DATA_PATH)
    dataset = load_raw_data(DATA_PATH)

    explicit_anoms = extract_explicit_anomalies(dataset)
    logger.info("Explicit anomalies found: %d", len(explicit_anoms))

    engine = LLMEvaluator()
    try:
        model_result = engine.analyze(query, raw_data=dataset, context=None, horizon_days=horizon_days, force_refresh=force_refresh)
    except Exception as e:
        logger.exception("Engine analyze failed: %s", e)
        model_result = {
            "intent": "insight",
            "dashboard": "finance",
            "summary": {},
            "anomalies": explicit_anoms,
            "forecast": {},
            "recommendations": ["Local fallback analysis"],
            "engine_used": "error-fallback",
        }

    merged = merge_model_and_explicit_anomalies(model_result, explicit_anoms)

    # Base summary
    merged.setdefault("summary", {})
    merged["summary"].setdefault("records", len(dataset))
    merged["summary"].setdefault("total_cost_usd", round(sum(float(x.get("cost", 0) or 0) for x in dataset), 2))

    # Add week-over-week computation
    merged["summary"].update(compute_weekly_cost_change(dataset))

    # -------------------------------
    # 🔹 Bedrock-based Insight Layer
    # -------------------------------
    try:
        generator = InsightGenerator()
        ai_insight = generator.generate_insight(analysis_data=merged)
        merged["ai_insight"] = ai_insight
        logger.info("✅ AI Insight generated and appended.")
    except Exception as e:
        logger.warning(f"⚠️ Insight generation failed: {e}")
        merged["ai_insight"] = "Insight unavailable due to engine error."

    # Save & print
    short_summary_and_save(merged, OUTPUT_PATH)
    print("🧠 AI Insight:")
    print(merged.get("ai_insight", "No insight available."))
    print("=" * 72 + "\n")

    return merged


if __name__ == "__main__":
    run_enhanced_analysis(force_refresh=True)
