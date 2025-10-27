"""Recommendation engine: converts structured LLM output into dashboard-ready payloads."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


class RecommendationEngine:
    """
    Converts structured AI responses (from SageMaker or Bedrock models)
    into dashboard-compatible JSON structures.

    Responsibilities:
    - Map standardized LLM output fields (anomalies, forecast, recommendations)
      to dashboard payloads.
    - Handle dashboard-specific post-processing (finance, IT, MSP).
    - Provide fault-tolerant, structured outputs for front-end rendering.
    """

    def __init__(self) -> None:
        pass

    def to_dashboard_payload(
        self,
        llm_response: Dict[str, Any],
        dashboard_type: str = "finance"
    ) -> Dict[str, Any]:
        """
        Convert structured LLM output into a dashboard-ready JSON format.

        Args:
            llm_response: Parsed response from LLM (Bedrock or SageMaker).
            dashboard_type: One of {'finance', 'it', 'msp'} determining the view transformation.

        Returns:
            Dashboard-ready payload dictionary.
        """
        try:
            anomalies: List[Dict[str, Any]] = llm_response.get("anomalies", [])
            forecast: Dict[str, Any] = llm_response.get("forecast", {})
            recommendations: List[Dict[str, Any]] = llm_response.get("recommendations", [])

            # Generic base structure
            payload: Dict[str, Any] = {
                "summary": {
                    "intent": llm_response.get("intent", "insight"),
                    "anomaly_count": len(anomalies),
                    "forecast_horizon": forecast.get("horizon_days"),
                },
                "anomalies": anomalies,
                "forecast": forecast,
                "recommendations": recommendations,
            }

            # Dashboard-specific augmentation
            if dashboard_type == "finance":
                predicted = forecast.get("predicted_costs") or []
                payload["finance_view"] = {
                    "predicted_total": sum(predicted) if predicted else None,
                    "top_recommendations": recommendations[:3],
                }

            elif dashboard_type == "it":
                payload["it_view"] = {
                    "service_focused_recommendations": [
                        r for r in recommendations if any(svc in str(r) for svc in ("EC2", "S3", "Lambda"))
                    ][:5],
                    "ops_actions": [
                        "Investigate high CPU utilization",
                        "Review autoscaling policies",
                        "Audit unused resources"
                    ],
                }

            elif dashboard_type == "msp":
                payload["msp_view"] = {
                    "tenant_priorities": recommendations[:5],
                    "multi_tenant_summary": f"{len(anomalies)} anomalies detected across tenants",
                }

            else:
                logger.warning("Unknown dashboard type '%s'. Returning base payload.", dashboard_type)

            logger.info("Generated %s dashboard payload successfully.", dashboard_type)
            return payload

        except Exception as e:
            logger.exception("Failed to convert LLM response to dashboard payload: %s", e)
            return {
                "error": "payload_conversion_failed",
                "details": str(e),
                "raw_response": llm_response,
            }
