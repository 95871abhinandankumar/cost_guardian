"""Unified interface for Google Gemini API with cost analysis."""

import json
import logging
import os
import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from dotenv import load_dotenv
from .cache_manager import CacheManager
from .utils import sha_hash, iso_date
from .gemini_provider import GeminiProvider

# AWS imports commented out - using Gemini instead
# import boto3
# from botocore.exceptions import BotoCoreError, ClientError

load_dotenv()

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except Exception:
    try:
        from fbprophet import Prophet
        PROPHET_AVAILABLE = True
    except Exception:
        PROPHET_AVAILABLE = False

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

# Gemini configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# AWS configuration (commented out - kept for reference)
# BEDROCK_REGION = os.getenv("BEDROCK_REGION")
# BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
# SAGEMAKER_ENDPOINT_ARN = os.getenv("SAGEMAKER_ENDPOINT_ARN")
# SAGEMAKER_REGION = os.getenv("SAGEMAKER_REGION", "us-east-1")

DEFAULT_DATA_PATH = os.path.join(os.getcwd(), "src", "data", "raw_data.json")

Record = Dict[str, Any]


class LLMEngine:
    def __init__(self, tenant_id: str = "default") -> None:
        self.tenant_id = tenant_id
        self.cache = CacheManager()
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize LLM provider clients."""
        # Initialize Gemini provider (primary)
        try:
            self.gemini = GeminiProvider(api_key=GEMINI_API_KEY, model_name=GEMINI_MODEL)
            if self.gemini.is_available():
                logger.info("Gemini provider initialized successfully")
            else:
                logger.warning("Gemini provider not available - check GEMINI_API_KEY")
                self.gemini = None
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {e}")
            self.gemini = None

        # AWS Bedrock client (commented out - using Gemini instead)
        # try:
        #     self.bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
        #     logger.info("Bedrock client initialized")
        # except Exception as e:
        #     self.bedrock = None
        #     logger.warning("Bedrock client unavailable: %s", e)
        self.bedrock = None  # Disabled

        # AWS SageMaker client (commented out - using Gemini instead)
        # try:
        #     self.sagemaker = boto3.client("sagemaker-runtime", region_name=SAGEMAKER_REGION)
        #     logger.info("SageMaker client initialized")
        # except Exception as e:
        #     self.sagemaker = None
        #     logger.warning("SageMaker client unavailable: %s", e)
        self.sagemaker = None  # Disabled

        # AWS S3 client (commented out - S3 loading still works if needed)
        # try:
        #     self.s3 = boto3.client("s3")
        # except Exception:
        #     self.s3 = None
        self.s3 = None  # Disabled

    def analyze(
        self,
        query: str,
        raw_data: Optional[Union[str, List[Record], Dict[str, Any]]] = None,
        context: Optional[List[str]] = None,
        horizon_days: int = 30,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """Main entrypoint for cost analysis and recommendations."""
        dataset = self._load_dataset(raw_data)
        dataset_hash = sha_hash(json.dumps(dataset, sort_keys=True)) if dataset else "empty"
        cache_key = self.cache.make_key(self.tenant_id, sha_hash(f"{query}:{dataset_hash}"), iso_date())

        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("Cache hit - returning cached analysis.")
                return cached

        # Local analysis
        anomalies, anomaly_summary = self._detect_anomalies(dataset)
        summary = self._dataset_summary(dataset)
        dashboard = self._route_dashboard(query, dataset, anomalies)
        forecast, forecast_meta = self._forecast_costs(dataset, horizon_days=horizon_days)

        # Build LLM prompt
        llm_prompt = self._build_prompt(query, dashboard, summary, anomalies, forecast, context, horizon_days)

        # Try Gemini (primary), then fallback to local reasoning
        llm_response = None
        used_engine = "none"

        try:
            # Use Gemini provider (primary)
            if self.gemini and self.gemini.is_available():
                llm_response = self.gemini.invoke(llm_prompt)
                used_engine = "gemini" if llm_response else used_engine
                logger.info(f"Gemini invocation {'succeeded' if llm_response else 'failed'}")

            # AWS Bedrock fallback (commented out - using Gemini instead)
            # if not llm_response and self.bedrock and BEDROCK_MODEL_ID:
            #     llm_response = self._invoke_bedrock_prompt(llm_prompt)
            #     used_engine = "bedrock" if llm_response else used_engine

            # AWS SageMaker fallback (commented out - using Gemini instead)
            # if not llm_response and self.sagemaker and SAGEMAKER_ENDPOINT_ARN:
            #     llm_response = self._invoke_sagemaker_prompt(llm_prompt)
            #     used_engine = "sagemaker" if llm_response else used_engine

        except Exception as e:
            logger.exception("Cloud model invocation error: %s", e)

        # Fallback to local mock reasoning if all providers fail
        if not llm_response:
            llm_response = self._local_reasoning(summary, anomalies, forecast, dashboard)
            used_engine = "mock"
            logger.info("Using local mock reasoning as fallback")

        recommendations = self._tune_recommendations(
            llm_response.get("recommendations", []), dashboard, anomalies, summary
        )

        result = {
            "intent": llm_response.get("intent", summary.get("dominant_intent", "insight")),
            "dashboard": dashboard,
            "summary": summary,
            "anomalies": anomalies,
            "anomaly_summary": anomaly_summary,
            "forecast": forecast,
            "forecast_meta": forecast_meta,
            "recommendations": recommendations,
            "engine_used": used_engine,
            "raw_llm": llm_response.get("raw", None),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        self.cache.set(cache_key, result)
        return result

    def _load_dataset(self, raw_data) -> List[Record]:
        if isinstance(raw_data, list):
            return raw_data
        if isinstance(raw_data, dict):
            if "records" in raw_data:
                return raw_data["records"]
            return [raw_data]
        if isinstance(raw_data, str) and raw_data.strip():
            if raw_data.startswith("s3://"):
                return self._load_from_s3(raw_data)
            if os.path.exists(raw_data):
                with open(raw_data, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else [data]

        if os.path.exists(DEFAULT_DATA_PATH):
            with open(DEFAULT_DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        return []

    def _load_from_s3(self, s3_path: str) -> List[Record]:
        if not self.s3:
            return []
        _, _, rest = s3_path.partition("s3://")
        bucket, _, key = rest.partition("/")
        try:
            obj = self.s3.get_object(Bucket=bucket, Key=key)
            body = obj["Body"].read().decode("utf-8")
            data = json.loads(body)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.warning("S3 load failed: %s", e)
            return []

    def _dataset_summary(self, dataset: List[Record]) -> Dict[str, Any]:
        total_cost = round(sum(float(r.get("cost", 0.0) or 0.0) for r in dataset), 2)
        by_service, by_region = {}, {}
        for r in dataset:
            svc = r.get("service_name") or r.get("service") or "unknown"
            reg = r.get("region") or "unknown"
            by_service[svc] = by_service.get(svc, 0.0) + float(r.get("cost", 0.0) or 0.0)
            by_region[reg] = by_region.get(reg, 0.0) + float(r.get("cost", 0.0) or 0.0)

        return {
            "total_cost_usd": total_cost,
            "records": len(dataset),
            "service_breakdown": by_service,
            "region_breakdown": by_region,
            "top_services": sorted(by_service.items(), key=lambda x: x[1], reverse=True)[:5],
            "dominant_intent": "anomaly"
            if any(r.get("anomaly_flag") for r in dataset)
            else "insight",
        }

    def _detect_anomalies(self, dataset: List[Record]) -> Tuple[List[Record], Dict[str, Any]]:
        anomalies = [r for r in dataset if r.get("anomaly_flag") or r.get("anomaly_score", 0) > 0.8]
        by_service = {}
        for r in dataset:
            svc = r.get("service_name") or "unknown"
            by_service[svc] = by_service.get(svc, 0.0) + float(r.get("cost", 0.0) or 0.0)

        if by_service:
            mean_ = statistics.mean(by_service.values())
            std_ = statistics.pstdev(by_service.values()) if len(by_service) > 1 else 0
            threshold = mean_ + 3 * std_ if std_ else mean_ * 2
            for svc, tot in by_service.items():
                if tot > threshold:
                    anomalies.append({"service_name": svc, "cost": tot, "reason": "service_total_exceeds_threshold"})
        return anomalies, {"count": len(anomalies)}

    def _forecast_costs(self, dataset: List[Record], horizon_days: int = 30):
        by_date = {}
        for r in dataset:
            d = r.get("usage_date") or r.get("date")
            if not d:
                continue
            by_date[d] = by_date.get(d, 0) + float(r.get("cost", 0.0) or 0.0)
        if not by_date:
            return {"predicted_costs": []}, {"method": "none"}

        dates = sorted(by_date.items())
        meta = {"method": "prophet" if PROPHET_AVAILABLE else "moving_average"}

        if PROPHET_AVAILABLE and len(dates) >= 3:
            try:
                import pandas as pd
                df = pd.DataFrame(dates, columns=["ds", "y"])
                df["ds"] = pd.to_datetime(df["ds"])
                model = Prophet()
                model.fit(df)
                future = model.make_future_dataframe(periods=horizon_days)
                forecast = model.predict(future)
                preds = forecast.tail(horizon_days)["yhat"].tolist()
                return {"predicted_costs": [round(x, 2) for x in preds]}, meta
            except Exception as e:
                logger.warning("Prophet failed: %s", e)

        avg = sum(v for _, v in dates[-min(7, len(dates)):]) / min(7, len(dates))
        preds = [round(avg * (1 + 0.005 * i), 2) for i in range(horizon_days)]
        return {"predicted_costs": preds}, meta

    # ---------------------------------------------------------------------
    # Prompt building & invocations
    # ---------------------------------------------------------------------
    def _build_prompt(self, query, dashboard, summary, anomalies, forecast, context, horizon_days):
        top_services = ", ".join([f"{s} (${c})" for s, c in summary.get("top_services", [])])
        context_block = "\n".join(context or [])[:2000]
        return (
            f"You are a cost analysis assistant.\n"
            f"DASHBOARD: {dashboard}\nQUERY: {query}\n"
            f"TOP_SERVICES: {top_services}\nANOMALIES: {json.dumps(anomalies[:3])}\n"
            f"FORECAST_NEXT_{horizon_days}_DAYS: {forecast}\nCONTEXT: {context_block}\n"
            "Return JSON with keys: intent, summary, anomalies, recommendations."
        )

    # AWS Bedrock invocation (commented out - using Gemini instead)
    # def _invoke_bedrock_prompt(self, prompt: str):
    #     if not (self.bedrock and BEDROCK_MODEL_ID):
    #         return None
    #     try:
    #         body = {"input": prompt}
    #         resp = self.bedrock.invoke_model(
    #             modelId=BEDROCK_MODEL_ID,
    #             body=json.dumps(body),
    #             accept="application/json",
    #             contentType="application/json",
    #         )
    #         raw = resp["body"].read().decode("utf-8")
    #         parsed = json.loads(raw)
    #         return parsed
    #     except Exception as e:
    #         logger.warning("Bedrock invoke failed: %s", e)
    #         return None

    # AWS SageMaker invocation (commented out - using Gemini instead)
    # def _invoke_sagemaker_prompt(self, prompt: str):
    #     if not (self.sagemaker and SAGEMAKER_ENDPOINT_ARN):
    #         return None
    #     try:
    #         endpoint = SAGEMAKER_ENDPOINT_ARN.split("/")[-1]
    #         payload = {"prompt": prompt}
    #         resp = self.sagemaker.invoke_endpoint(
    #             EndpointName=endpoint,
    #             Body=json.dumps(payload),
    #             ContentType="application/json",
    #         )
    #         raw = resp["Body"].read().decode("utf-8")
    #         return json.loads(raw)
    #     except Exception as e:
    #         logger.warning("SageMaker invoke failed: %s", e)
    #         return None

    def _local_reasoning(self, summary, anomalies, forecast, dashboard):
        recs = []
        if anomalies:
            recs.append(f"Detected {len(anomalies)} anomalies — investigate flagged resources first.")
        if summary.get("top_services"):
            recs.append(f"Review top service: {summary['top_services'][0][0]}")
        recs.append("Enable S3 lifecycle rules and set budget alerts.")
        return {"intent": "anomaly" if anomalies else "insight", "recommendations": recs, "raw": {"summary": summary}}

    def _tune_recommendations(self, base_recs, dashboard, anomalies, summary):
        recs = list(base_recs)
        
        # Convert dict recommendations to strings for deduplication
        processed_recs = []
        seen = set()
        for rec in recs:
            if isinstance(rec, dict):
                # Extract text from dict if available
                rec_text = rec.get('recommendation') or rec.get('action') or rec.get('text') or str(rec)
            else:
                rec_text = str(rec)
            
            # Deduplicate by text content
            rec_lower = rec_text.lower().strip()
            if rec_lower not in seen:
                seen.add(rec_lower)
                processed_recs.append(rec_text)
        
        # Add dashboard-specific recommendations
        if dashboard == "finance":
            processed_recs.append("Set AWS Budget alerts at 80% and 100%.")
        if dashboard == "it":
            processed_recs.append("Review high CPU EC2 instances.")
        if dashboard == "msp":
            processed_recs.append("Prioritize anomalies by tenant SLA.")
        
        return processed_recs

    def _route_dashboard(self, query, dataset, anomalies):
        q = query.lower()
        if any(k in q for k in ["cost", "budget", "finance"]):
            return "finance"
        if any(k in q for k in ["anomaly", "usage", "cpu"]):
            return "it"
        if any(k in q for k in ["tenant", "client", "msp"]):
            return "msp"
        return "finance"

    def invoke_model(self, prompt: str, deterministic: bool = True):
        """Invoke the Gemini model or fallback to mock reasoning."""
        try:
            return self.analyze(prompt, force_refresh=True)
        except Exception as e:
            logger.warning(f"invoke_model fallback: {e}")
            return {"text": "Local fallback: Costs stable, monitor anomalies & adjust budgets."}


LLMEvaluator = LLMEngine

if __name__ == "__main__":
    engine = LLMEngine("demo")
    out = engine.analyze("Detect anomalies and forecast next month")
    print(json.dumps(out, indent=2))
