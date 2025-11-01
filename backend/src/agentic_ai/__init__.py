"""
Agentic AI package

Exposes main components for the Agentic AI layer:
- QueryAnalyzer: fetches context from vector DB and detects intent
- LLMEvaluator: communicates with Google Gemini API (with mock fallback)
- RecommendationEngine: converts LLM output to actionable recommendations
- CacheManager: caches daily/precomputed results
- GeminiProvider: Google Gemini API provider for LLM inference
"""

from .query_analysis import QueryAnalyzer
from .llm_engine import LLMEvaluator
from .recommendation import RecommendationEngine
from .cache_manager import CacheManager
from .gemini_provider import GeminiProvider

__all__ = [
    "QueryAnalyzer",
    "LLMEvaluator",
    "RecommendationEngine",
    "CacheManager",
    "GeminiProvider",
]
