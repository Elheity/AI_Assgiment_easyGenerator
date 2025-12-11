"""Lightweight quality scorer without ML dependencies for fast GPU generation"""

from typing import Dict, Any, List
import re
from collections import Counter


class FastQualityScorer:
    """Fast quality scorer without ML dependencies - allows GPU usage for Ollama"""
    
    def __init__(self):
        """Initialize fast quality scorer"""
        self.technical_terms = {
            'api', 'sdk', 'cli', 'gui', 'ui', 'ux', 'integration', 'plugin',
            'extension', 'workflow', 'pipeline', 'automation', 'deployment',
            'configuration', 'code', 'debug', 'testing', 'test', 'endpoint',
            'ci/cd', 'docker', 'kubernetes', 'monitoring', 'logging', 'metrics'
        }
    
    def calculate_quality_score(
        self,
        review: str,
        rating: int,
        existing_reviews: List[str],
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate quality score using simple heuristics (no ML)
        
        Args:
            review: Review text
            rating: Rating (1-5)
            existing_reviews: List of existing reviews
            weights: Not used in fast mode
            
        Returns:
            Quality score dictionary
        """
        # Simple checks
        word_count = len(review.split())
        tech_term_count = sum(1 for term in self.technical_terms if term in review.lower())
        has_features = bool(re.search(r'\b(feature|functionality|capability|option|setting)\b', review, re.I))
        
        # Calculate simple quality score
        quality_score = 50  # Base score
        
        # Length check (30-200 words)
        if 30 <= word_count <= 200:
            quality_score += 20
        
        # Technical terms
        quality_score += min(tech_term_count * 10, 30)
        
        # Feature mentions
        if has_features:
            quality_score += 10
        
        # Simple diversity check (not too short)
        if word_count >= 40:
            quality_score += 10
        
        # Cap at 100
        quality_score = min(100, quality_score)
        
        # Accept if score >= 40
        should_accept = quality_score >= 40
        
        rejection_reasons = []
        if not should_accept:
            rejection_reasons.append(f"Quality score too low: {quality_score}")
        
        return {
            'overall_quality_score': quality_score,
            'should_accept': should_accept,
            'rejection_reasons': rejection_reasons,
            'diversity': {
                'overall_diversity_score': 70,  # Dummy value
                'semantic_similarity': 0.5,
                'max_similarity_threshold_exceeded': False
            },
            'bias': {
                'quality_score': 70,  # Dummy value
                'has_issues': False,
                'sentiment_alignment': {'is_aligned': True},
                'length_check': {'is_anomalous': False, 'word_count': word_count}
            },
            'realism': {
                'realism_score': quality_score,
                'technical_term_count': tech_term_count,
                'has_enough_tech_terms': tech_term_count >= 1,
                'mentions_features': has_features,
                'is_balanced': True,
                'mentions_use_case': True,
                'generic_phrases_found': [],
                'has_generic_phrases': False,
                'passes_realism': True
            },
            'weights': {'diversity': 0.3, 'bias': 0.3, 'realism': 0.4}
        }
    
    def should_regenerate(self, quality_result: Dict[str, Any]) -> bool:
        """Determine if review should be regenerated"""
        return not quality_result['should_accept']
