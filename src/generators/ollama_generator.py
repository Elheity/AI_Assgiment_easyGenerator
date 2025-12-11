"""Ollama local model generator"""

import os
import time
import requests
from typing import Dict, Any
from .base_generator import BaseGenerator


class OllamaGenerator(BaseGenerator):
    """Generator using Ollama local models"""
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize Ollama generator
        
        Args:
            model_config: Model configuration
        """
        super().__init__(model_config)
        
        # Get Ollama base URL from environment or use default
        self.base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.api_url = f"{self.base_url}/api/generate"
        
        # Test connection
        self._test_connection()
        
    def _test_connection(self):
        """Test connection to Ollama server"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Cannot connect to Ollama server at {self.base_url}. "
                f"Make sure Ollama is running. Error: {str(e)}"
            )
    
    def generate_review(
        self,
        persona: Dict[str, Any],
        tool_category: Dict[str, Any],
        rating: int,
        review_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate review using Ollama
        
        Args:
            persona: Persona configuration
            tool_category: Tool category configuration
            rating: Rating (1-5)
            review_characteristics: Review characteristics
            
        Returns:
            Dictionary with review_text and metadata
        """
        # Build prompt
        prompt = self._build_prompt(persona, tool_category, rating, review_characteristics)
        
        # Add system context to prompt for Ollama
        full_prompt = f"""You are a developer writing an authentic, realistic review for a dev tool. Write naturally and honestly.

{prompt}"""
        
        # Track generation time
        start_time = time.time()
        
        try:
            # Call Ollama API
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                },
                timeout=120  # Longer timeout for local models
            )
            
            response.raise_for_status()
            generation_time = time.time() - start_time
            
            # Parse response
            result = response.json()
            review_text = result.get('response', '').strip()
            
            # Build metadata
            metadata = {
                'model': self.model_name,
                'provider': self.provider,
                'generation_time': generation_time,
                'tokens_used': result.get('eval_count', 0) + result.get('prompt_eval_count', 0),
                'prompt_tokens': result.get('prompt_eval_count', 0),
                'completion_tokens': result.get('eval_count', 0),
                'persona': persona['name'],
                'tool_category': tool_category['name'],
                'rating': rating
            }
            
            return {
                'review_text': review_text,
                'metadata': metadata
            }
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama generation failed: {str(e)}")
