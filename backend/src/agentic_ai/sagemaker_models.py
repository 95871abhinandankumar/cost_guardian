"""SageMaker runtime wrapper for model inference."""

import json
import logging
import os
import time
from typing import Any, Dict, Optional, Union
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

SAGEMAKER_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
SAGEMAKER_ENDPOINT_ARN = os.getenv("SAGEMAKER_ENDPOINT_ARN", "")
MAX_RETRIES = int(os.getenv("SAGEMAKER_MAX_RETRIES", "3"))
BACKOFF_BASE = float(os.getenv("SAGEMAKER_BACKOFF_BASE", "2.0"))
TIMEOUT = int(os.getenv("SAGEMAKER_TIMEOUT_SECONDS", "30"))

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


class SageMakerClientWrapper:
    """Wrapper for SageMaker Runtime with retry and backoff logic."""

    def __init__(self, region: str = SAGEMAKER_REGION) -> None:
        try:
            self.client = boto3.client(
                "sagemaker-runtime",
                region_name=region,
                config=Config(read_timeout=TIMEOUT, retries={"max_attempts": MAX_RETRIES})
            )
            logger.info("✅ SageMaker Runtime client initialized (region=%s)", region)
        except Exception as e:
            logger.exception("❌ Failed to initialize SageMaker client: %s", e)
            self.client = None

    def invoke_endpoint(self, endpoint_name: str, payload: Dict[str, Any]) -> str:
        """
        Invoke a SageMaker endpoint with JSON payload and retry logic.

        Args:
            endpoint_name: SageMaker endpoint name (not ARN).
            payload: Input JSON payload.

        Returns:
            Raw string output from the model.
        """
        if not self.client:
            raise RuntimeError("SageMaker client not initialized")

        body = json.dumps(payload)
        last_error: Optional[Exception] = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.client.invoke_endpoint(
                    EndpointName=endpoint_name,
                    ContentType="application/json",
                    Body=body
                )
                result = response["Body"].read().decode("utf-8")
                logger.info("✅ SageMaker inference succeeded on attempt %d", attempt)
                return result
            except (BotoCoreError, ClientError) as e:
                last_error = e
                logger.warning("⚠️ Attempt %d failed invoking SageMaker endpoint: %s", attempt, e)
                if attempt < MAX_RETRIES:
                    time.sleep(BACKOFF_BASE ** attempt)

        raise RuntimeError(f"SageMaker invocation failed after {MAX_RETRIES} attempts") from last_error


# --------------------------------------------------------------------------
# High-Level Evaluator
# --------------------------------------------------------------------------
class SageMakerEvaluator:
    """
    High-level API for structured inference through SageMaker endpoints.

    Responsibilities:
    - Prepare and send requests
    - Parse structured (JSON/text) responses
    - Handle fallback logic if endpoint or client fails
    """

    def __init__(self, endpoint_arn: Optional[str] = None, region: str = SAGEMAKER_REGION):
        self.endpoint_arn = endpoint_arn or os.getenv("SAGEMAKER_ENDPOINT_ARN", "")
        self.endpoint_name = self._extract_endpoint_name(self.endpoint_arn)
        self.client = SageMakerClientWrapper(region=region) if self.endpoint_name else None

    def analyze(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls SageMaker endpoint with structured payload and returns parsed output.

        Args:
            input_data: Dict input for the model.

        Returns:
            Parsed structured JSON from the model (or fallback if unavailable).
        """
        logger.info("🚀 SageMakerEvaluator.analyze called with keys: %s", list(input_data.keys()))

        if not self.client or not self.endpoint_name:
            logger.warning("⚠️ No SageMaker endpoint configured, using fallback response.")
            return self._fallback_response(input_data)

        try:
            raw_output = self.client.invoke_endpoint(self.endpoint_name, input_data)
            return self._parse_output(raw_output)
        except Exception as e:
            logger.exception("❌ SageMaker analyze failed: %s — returning fallback", e)
            return self._fallback_response(input_data)

    def _parse_output(self, raw: Union[str, bytes]) -> Dict[str, Any]:
        """Parse the SageMaker response — JSON if possible, else text wrapped in a dict."""
        try:
            parsed = json.loads(raw)
            if not isinstance(parsed, dict):
                parsed = {"result": parsed}
            return parsed
        except json.JSONDecodeError:
            return {"result": raw.strip(), "raw_output": True}

    def _extract_endpoint_name(self, arn: str) -> str:
        """Extracts the endpoint name from ARN (safe for boto3 calls)."""
        if not arn:
            return ""
        return arn.split("/")[-1] if "/" in arn else arn

    def _fallback_response(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deterministic fallback response if endpoint is unavailable."""
        return {
            "intent": "insight",
            "anomalies": [],
            "forecast": {"predicted_costs": [], "horizon_days": 0},
            "recommendations": [],
            "message": "Fallback response — SageMaker endpoint not available",
            "input": input_data,
        }
