"""
Agentic AI package

Exposes main components for the Agentic AI layer:
- QueryAnalyzer: fetches context from vector DB and detects intent
- LLMEvaluator: communicates with AWS Bedrock (with mock fallback)
- RecommendationEngine: converts LLM output to actionable recommendations
- CacheManager: caches daily/precomputed results
"""

from .query_analysis import QueryAnalyzer
from .llm_engine import LLMEvaluator
from .recommendation import RecommendationEngine
from .cache_manager import CacheManager

__all__ = [
    "QueryAnalyzer",
    "LLMEvaluator",
    "RecommendationEngine",
    "CacheManager",
]
