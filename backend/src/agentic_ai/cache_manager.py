"""
Cache Manager for Agentic AI
----------------------------
Handles caching of model outputs (Bedrock / SageMaker) and other agent results.

Features:
- Uses `diskcache` for performance if available, else JSON fallback.
- Structured logging with timestamps.
- Smart get_or_infer wrapper to auto-cache model calls.
- Deterministic key generation for Bedrock & SageMaker inferences.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any, Callable, Optional

from .utils import iso_date

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

# Default cache directory
DEFAULT_CACHE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "cache")
)


class CacheManager:
    """Manages cache for model outputs and agent responses."""

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        try:
            import diskcache as dc  # type: ignore
            self._store = dc.Cache(self.cache_dir)
            self._use_diskcache = True
            logger.info("✅ CacheManager initialized with diskcache at %s", self.cache_dir)
        except Exception:
            self._store = None
            self._use_diskcache = False
            logger.warning("⚠️ Diskcache not available, using JSON file cache at %s", self.cache_dir)

    # ------------------------------- Basic Storage ------------------------------- #
    def _key_to_path(self, key: str) -> str:
        safe_key = key.replace(os.path.sep, "_")
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def set(self, key: str, value: Any, expire_seconds: int = 24 * 3600) -> None:
        """Store a value in cache."""
        try:
            if self._use_diskcache and self._store is not None:
                self._store.set(key, value, expire=expire_seconds)
            else:
                path = self._key_to_path(key)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(value, f, indent=2, default=str, ensure_ascii=False)
            logger.debug("🗂️ Cache set: %s", key)
        except Exception as e:
            logger.exception("❌ Failed to set cache for %s: %s", key, e)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache or None if not present/expired."""
        try:
            if self._use_diskcache and self._store is not None:
                return self._store.get(key)
            path = self._key_to_path(key)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.exception("❌ Failed to get cache for %s: %s", key, e)
            return None

    # ------------------------------- Key Utilities ------------------------------- #
    def make_key(self, tenant_id: str, query_id: str, date: Optional[str] = None) -> str:
        """Create deterministic cache key: tenant_date_queryid"""
        date = date or iso_date()
        return f"{tenant_id}__{date}__{query_id}"

    def make_bedrock_key(self, model_id: str, prompt: str) -> str:
        """Create a deterministic cache key for Bedrock LLM calls."""
        prompt_hash = hashlib.sha1(prompt.encode("utf-8")).hexdigest()[:10]
        return f"bedrock__{model_id}__{prompt_hash}"

    def make_sagemaker_key(self, model_name: str, input_payload: Any) -> str:
        """Create deterministic key for SageMaker model calls."""
        input_hash = hashlib.sha1(json.dumps(input_payload, sort_keys=True).encode()).hexdigest()[:10]
        return f"sagemaker__{model_name}__{input_hash}"

    # ---------------------------- Smart Get or Infer ----------------------------- #
    def get_or_infer(
        self,
        key: str,
        infer_func: Callable[[], Any],
        expire_seconds: int = 24 * 3600,
        force_refresh: bool = False,
    ) -> Any:
        """
        Return cached result if available; else compute, store, and return.
        """
        if not force_refresh:
            cached = self.get(key)
            if cached is not None:
                logger.info("💾 Cache hit for key: %s", key)
                return cached

        logger.info("⚙️ Cache miss — running inference for key: %s", key)
        result = infer_func()
        self.set(key, result, expire_seconds)
        return result
