"""OpenAI GPT-4 generator"""

import os
import time
from typing import Dict, Any
from openai import OpenAI
from .base_generator import BaseGenerator


class OpenAIGenerator(BaseGenerator):
    """Generator using OpenAI GPT-4"""
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize OpenAI generator
        
        Args:
            model_config: Model configuration
        """
        super().__init__(model_config)
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        
    def generate_review(
        self,
        persona: Dict[str, Any],
        tool_category: Dict[str, Any],
        rating: int,
        review_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate review using OpenAI GPT-4
        
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
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a developer writing an authentic, realistic review for a dev tool. Write naturally and honestly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            generation_time = time.time() - start_time
            
            # Extract review text
            review_text = response.choices[0].message.content.strip()
            
            # Build metadata
            metadata = {
                'model': self.model_name,
                'provider': self.provider,
                'generation_time': generation_time,
                'tokens_used': response.usage.total_tokens,
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'persona': persona['name'],
                'tool_category': tool_category['name'],
                'rating': rating
            }
            
            return {
                'review_text': review_text,
                'metadata': metadata
            }
            
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {str(e)}")
