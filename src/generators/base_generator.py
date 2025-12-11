"""Base generator abstract class"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import random


class BaseGenerator(ABC):
    """Abstract base class for review generators"""
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize generator
        
        Args:
            model_config: Model configuration from config file
        """
        self.model_name = model_config.get('name')
        self.provider = model_config.get('provider')
        self.temperature = model_config.get('temperature', 0.8)
        self.max_tokens = model_config.get('max_tokens', 500)
        
    @abstractmethod
    def generate_review(
        self, 
        persona: Dict[str, Any],
        tool_category: Dict[str, Any],
        rating: int,
        review_characteristics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a review
        
        Args:
            persona: Persona configuration
            tool_category: Tool category configuration
            rating: Rating (1-5)
            review_characteristics: Review characteristics from config
            
        Returns:
            Dictionary with:
                - review_text: Generated review text
                - metadata: Generation metadata (model, tokens, time, etc.)
        """
        pass
    
    def _build_prompt(
        self,
        persona: Dict[str, Any],
        tool_category: Dict[str, Any],
        rating: int,
        review_characteristics: Dict[str, Any]
    ) -> str:
        """
        Build prompt for review generation
        
        Args:
            persona: Persona configuration
            tool_category: Tool category configuration
            rating: Rating (1-5)
            review_characteristics: Review characteristics
            
        Returns:
            Formatted prompt string
        """
        # Select random tool from category
        tool_name = random.choice(tool_category['examples'])
        
        # Select random features to mention
        features = tool_category.get('features', [])
        num_features = min(3, len(features))
        selected_features = random.sample(features, num_features)
        
        # Build tone instruction
        tones = review_characteristics.get('tone', ['professional'])
        tone = random.choice(tones)
        
        # Get length constraints
        length = review_characteristics.get('length', {})
        min_words = length.get('min_words', 30)
        max_words = length.get('max_words', 200)
        
        # Build the prompt
        prompt = f"""You are a {persona['name']} writing a review for a dev tool.

Tool: {tool_name}
Category: {tool_category['name']}
Your Rating: {rating}/5 stars

Persona Description: {persona['description']}
Your characteristics:
{chr(10).join(f"- {char}" for char in persona['characteristics'])}

Write a realistic, authentic review that:
1. Reflects your {rating}/5 star rating (be honest about pros and cons)
2. Mentions specific features like: {', '.join(selected_features)}
3. Uses a {tone} tone
4. Is between {min_words}-{max_words} words
5. Includes your specific use case or context
6. Sounds like a real developer wrote it (not overly formal or marketing-like)

Important: 
- If rating is 1-2: Focus on problems, bugs, missing features
- If rating is 3: Balanced - mention both good and bad aspects
- If rating is 4-5: Mostly positive but mention minor areas for improvement
- Use technical vocabulary appropriate for a {persona['name']}
- Be specific and concrete, avoid generic statements

Write ONLY the review text, no additional commentary:"""

        return prompt
    
    def _extract_rating_sentiment(self, rating: int) -> str:
        """Map rating to expected sentiment"""
        sentiment_map = {
            1: "very negative",
            2: "negative",
            3: "neutral/mixed",
            4: "positive",
            5: "very positive"
        }
        return sentiment_map.get(rating, "neutral")
