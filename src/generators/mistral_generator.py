"""Mistral API generator"""

import os
import time
import requests
from typing import Dict, Any
from .base_generator import BaseGenerator


class MistralGenerator(BaseGenerator):
    """Generator using Mistral API"""
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize Mistral generator
        
        Args:
            model_config: Model configuration
        """
        super().__init__(model_config)
        
        # Initialize Mistral API
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        
    def generate_review(
        self,
        persona: Dict[str, Any],
        tool_category: Dict[str, Any],
        rating: int,
        review_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate review using Mistral API
        
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
        
        # Track generation time
        start_time = time.time()
        
        try:
            # Call Mistral API
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a developer writing an authentic, realistic review for a dev tool. Write naturally and honestly."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                timeout=30
            )
            
            response.raise_for_status()
            generation_time = time.time() - start_time
            
            # Parse response
            result = response.json()
            review_text = result['choices'][0]['message']['content'].strip()
            
            # Build metadata
            metadata = {
                'model': self.model_name,
                'provider': self.provider,
                'generation_time': generation_time,
                'tokens_used': result['usage']['total_tokens'],
                'prompt_tokens': result['usage']['prompt_tokens'],
                'completion_tokens': result['usage']['completion_tokens'],
                'persona': persona['name'],
                'tool_category': tool_category['name'],
                'rating': rating
            }
            
            return {
                'review_text': review_text,
                'metadata': metadata
            }
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Mistral API generation failed: {str(e)}")
