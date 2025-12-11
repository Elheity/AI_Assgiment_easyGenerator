"""Quality scorer - aggregates all quality metrics"""

from typing import Dict, Any, List
from .diversity_metrics import DiversityMetrics
from .bias_detector import BiasDetector
from .realism_validator import RealismValidator


class QualityScorer:
    """Aggregate quality scorer for reviews"""
    
    def __init__(self):
        """Initialize quality scorer"""
        self.diversity_metrics = DiversityMetrics()
        self.bias_detector = BiasDetector()
        self.realism_validator = RealismValidator()
        
    def calculate_quality_score(
        self,
        review: str,
        rating: int,
        existing_reviews: List[str],
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall quality score for a review
        
        Args:
            review: Review text
            rating: Rating (1-5)
            existing_reviews: List of existing reviews (for diversity check)
            weights: Weights for different quality dimensions
            
        Returns:
            Dictionary with all quality metrics and overall score
        """
        if weights is None:
            weights = {
                'diversity': 0.30,
                'bias': 0.30,
                'realism': 0.40
            }
        
        # Calculate diversity score
        diversity_result = self.diversity_metrics.calculate_diversity_score(
            review, existing_reviews
        )
        
        # Calculate bias score
        bias_result = self.bias_detector.calculate_bias_score(review, rating)
        
        # Calculate realism score
        realism_result = self.realism_validator.calculate_realism_score(review, rating)
        
        # Calculate weighted overall score (0-100)
        overall_score = (
            diversity_result['overall_diversity_score'] * weights['diversity'] +
            bias_result['quality_score'] * weights['bias'] +
            realism_result['realism_score'] * weights['realism']
        )
        
        # Determine if review should be accepted
        should_accept = (
            overall_score >= 60 and  # Minimum overall score
            not diversity_result['max_similarity_threshold_exceeded'] and
            not bias_result['has_issues'] and
            realism_result['passes_realism']
        )
        
        # Collect rejection reasons
        rejection_reasons = []
        if overall_score < 60:
            rejection_reasons.append(f"Overall quality score too low: {overall_score:.1f}")
        if diversity_result['max_similarity_threshold_exceeded']:
            rejection_reasons.append(
                f"Too similar to existing review: {diversity_result['semantic_similarity']:.2f}"
            )
        if bias_result['has_issues']:
            if not bias_result['sentiment_alignment']['is_aligned']:
                rejection_reasons.append("Sentiment doesn't match rating")
            if bias_result['length_check']['is_anomalous']:
                rejection_reasons.append("Review length is anomalous")
        if not realism_result['passes_realism']:
            rejection_reasons.append(f"Realism score too low: {realism_result['realism_score']:.1f}")
        
        return {
            'overall_quality_score': overall_score,
            'should_accept': should_accept,
            'rejection_reasons': rejection_reasons,
            'diversity': diversity_result,
            'bias': bias_result,
            'realism': realism_result,
            'weights': weights
        }
    
    def should_regenerate(self, quality_result: Dict[str, Any]) -> bool:
        """
        Determine if review should be regenerated
        
        Args:
            quality_result: Result from calculate_quality_score
            
        Returns:
            True if review should be regenerated
        """
        return not quality_result['should_accept']
