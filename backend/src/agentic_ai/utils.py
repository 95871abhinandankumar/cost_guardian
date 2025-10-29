"""Utility functions for agentic AI."""

import json
import logging
import os
import hashlib
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


def sha_hash(text: str) -> str:
    """Return a short, consistent SHA256 hash string for caching and keys."""
    if not isinstance(text, str):
        text = str(text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def safe_json_dumps(obj: Any, indent: int = 2) -> str:
    """Safely serialize object to JSON with graceful fallback."""
    try:
        return json.dumps(obj, indent=indent, default=str, ensure_ascii=False)
    except Exception as e:
        logger.warning("safe_json_dumps failed for object: %s — %s", type(obj), e)
        try:
            return json.dumps(str(obj), indent=indent, ensure_ascii=False)
        except Exception:
            return "{}"  # final fallback


def iso_date(dt: Optional[datetime] = None) -> str:
    """Return ISO date string (YYYY-MM-DD)."""
    dt = dt or datetime.utcnow()
    return dt.date().isoformat()


def normalize_text(s: str) -> str:
    """Lightweight normalization for queries or prompt text."""
    return " ".join(s.strip().split())


def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Safe environment variable fetch with optional default and validation.
    Example:
        model_id = get_env_var("BEDROCK_MODEL_ID", required=True)
    """
    val = os.getenv(key, default)
    if required and not val:
        logger.warning("Missing required environment variable: %s", key)
    return val


def log_section(title: str) -> None:
    """Pretty-print a visual separator in logs for clarity."""
    logger.info("\n" + "=" * 80)
    logger.info(f"{title.center(80)}")
    logger.info("=" * 80 + "\n")
