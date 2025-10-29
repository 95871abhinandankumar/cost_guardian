"""Google Gemini API provider for LLM inference."""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")

# Try to import Google Generative AI SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI SDK not installed. Install with: pip install google-generativeai")


class GeminiProvider:
    """Provider for Google Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini provider.

        Args:
            api_key: Gemini API key. If not provided, reads from GEMINI_API_KEY env var.
            model_name: Model to use (default: gemini-2.5-flash for fast responses).
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = None
        self.model = None

        if not GEMINI_AVAILABLE:
            logger.error("Google Generative AI SDK not available")
            return

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.client = True  # Client initialized
            logger.info(f"Gemini provider initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {e}")
            self.client = None
            self.model = None

    def is_available(self) -> bool:
        """Check if Gemini provider is available."""
        return self.client is not None and self.model is not None

    def invoke(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Invoke Gemini model with a prompt.

        Args:
            prompt: The prompt to send to the model.
            **kwargs: Additional parameters (temperature, max_tokens, etc.).

        Returns:
            Parsed response dict or None if invocation fails.
        """
        if not self.is_available():
            logger.warning("Gemini provider not available")
            return None

        try:
            # Generate content
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 8192),
            }

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Extract text from response
            response_text = response.text if hasattr(response, 'text') else str(response)

            # Try to parse as JSON first (since our prompts ask for JSON)
            try:
                parsed = json.loads(response_text)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    # If parsed but not a dict, wrap it
                    return {"result": parsed, "raw_text": response_text}
            except json.JSONDecodeError:
                # If not JSON, try to extract JSON from the text
                # Look for JSON-like structures in the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                        return parsed if isinstance(parsed, dict) else {"result": parsed, "raw_text": response_text}
                    except json.JSONDecodeError:
                        pass

                # If no JSON found, structure the text response as a dict
                logger.info("Gemini response was not JSON, structuring as text response")
                return {
                    "intent": "insight",
                    "summary": response_text[:500],  # Truncate for summary
                    "recommendations": self._extract_recommendations_from_text(response_text),
                    "raw": response_text,
                    "raw_text": response_text
                }

        except Exception as e:
            logger.error(f"Gemini invocation failed: {e}", exc_info=True)
            return None

    def _extract_recommendations_from_text(self, text: str) -> List[str]:
        """
        Extract recommendation-like items from free-form text.

        Args:
            text: The response text.

        Returns:
            List of recommendation strings.
        """
        recommendations = []
        # Match lines starting with numbers, bullets, or dashes
        patterns = [
            r'^\d+[\.\)]\s*(.+)$',  # Numbered: "1. recommendation"
            r'^[-•*]\s*(.+)$',      # Bullets: "- recommendation"
            r'^Recommendation.*?:\s*(.+)$',  # "Recommendation: ..."
        ]

        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    rec = match.group(1).strip()
                    if len(rec) > 10:  # Filter out very short matches
                        recommendations.append(rec)

        # If no structured recommendations found, split by sentences and take first few
        if not recommendations:
            sentences = re.split(r'[.!?]+', text)
            recommendations = [s.strip() for s in sentences if len(s.strip()) > 20][:5]

        return recommendations[:10]  # Limit to 10 recommendations

