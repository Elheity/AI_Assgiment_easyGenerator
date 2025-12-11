"""Bias detection for review quality assessment"""

from typing import Dict, Any, List
from transformers import pipeline
import numpy as np


class BiasDetector:
    """Detect bias and unrealistic patterns in reviews"""
    
    def __init__(self):
        """Initialize bias detector"""
        # Load sentiment analysis model (CPU to avoid CUDA 6.1 issues)
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1  # CPU mode
        )
        
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of review text
        
        Args:
            text: Review text
            
        Returns:
            Dictionary with sentiment label and score
        """
        result = self.sentiment_analyzer(text[:512])[0]  # Truncate to model max length
        return {
            'label': result['label'],  # POSITIVE or NEGATIVE
            'score': result['score']   # Confidence score
        }
    
    def check_sentiment_rating_alignment(self, review: str, rating: int) -> Dict[str, Any]:
        """
        Check if sentiment matches the rating
        
        Args:
            review: Review text
            rating: Rating (1-5)
            
        Returns:
            Dictionary with alignment check results
        """
        sentiment = self.analyze_sentiment(review)
        
        # Map rating to expected sentiment
        # 1-2: Should be NEGATIVE
        # 3: Can be either (neutral)
        # 4-5: Should be POSITIVE
        
        expected_sentiment = None
        if rating <= 2:
            expected_sentiment = "NEGATIVE"
        elif rating >= 4:
            expected_sentiment = "POSITIVE"
        else:
            expected_sentiment = "NEUTRAL"  # 3-star can be mixed
        
        # Check alignment
        is_aligned = True
        if expected_sentiment != "NEUTRAL":
            is_aligned = sentiment['label'] == expected_sentiment
        
        # Calculate sentiment-rating mismatch score
        # Higher score = bigger mismatch
        mismatch_score = 0.0
        if rating <= 2 and sentiment['label'] == "POSITIVE":
            mismatch_score = sentiment['score']
        elif rating >= 4 and sentiment['label'] == "NEGATIVE":
            mismatch_score = sentiment['score']
        
        return {
            'sentiment': sentiment,
            'expected_sentiment': expected_sentiment,
            'is_aligned': is_aligned,
            'mismatch_score': mismatch_score
        }
    
    def detect_length_anomalies(self, review: str, rating: int) -> Dict[str, Any]:
        """
        Detect if review length is anomalous for the rating
        
        Args:
            review: Review text
            rating: Rating (1-5)
            
        Returns:
            Dictionary with anomaly detection results
        """
        word_count = len(review.split())
        
        # Expected length ranges by rating
        # Lower ratings tend to be shorter (just complaints)
        # Higher ratings tend to be longer (detailed praise)
        expected_ranges = {
            1: (20, 150),
            2: (30, 180),
            3: (40, 200),
            4: (40, 200),
            5: (30, 180)
        }
        
        min_words, max_words = expected_ranges.get(rating, (30, 200))
        
        is_too_short = word_count < min_words
        is_too_long = word_count > max_words
        is_anomalous = is_too_short or is_too_long
        
        return {
            'word_count': word_count,
            'expected_range': (min_words, max_words),
            'is_too_short': is_too_short,
            'is_too_long': is_too_long,
            'is_anomalous': is_anomalous
        }
    
    def detect_rating_distribution_bias(self, ratings: List[int]) -> Dict[str, Any]:
        """
        Detect if rating distribution is biased
        
        Args:
            ratings: List of all ratings
            
        Returns:
            Dictionary with bias detection results
        """
        if not ratings:
            return {'is_biased': False}
        
        # Calculate distribution
        rating_counts = {i: ratings.count(i) for i in range(1, 6)}
        total = len(ratings)
        distribution = {k: v/total for k, v in rating_counts.items()}
        
        # Check for extreme bias patterns
        is_biased = False
        bias_reasons = []
        
        # Check if >60% are 5-star (too positive)
        if distribution.get(5, 0) > 0.6:
            is_biased = True
            bias_reasons.append("Too many 5-star reviews (>60%)")
        
        # Check if >60% are 1-star (too negative)
        if distribution.get(1, 0) > 0.6:
            is_biased = True
            bias_reasons.append("Too many 1-star reviews (>60%)")
        
        # Check if no mid-range ratings (3-star)
        if total > 20 and distribution.get(3, 0) < 0.05:
            is_biased = True
            bias_reasons.append("Too few 3-star reviews (<5%)")
        
        return {
            'distribution': distribution,
            'is_biased': is_biased,
            'bias_reasons': bias_reasons
        }
    
    def calculate_bias_score(
        self,
        review: str,
        rating: int,
        all_ratings: List[int] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall bias score for a review
        
        Args:
            review: Review text
            rating: Rating (1-5)
            all_ratings: List of all ratings (optional, for distribution check)
            
        Returns:
            Dictionary with bias metrics and overall score
        """
        # Check sentiment-rating alignment
        sentiment_check = self.check_sentiment_rating_alignment(review, rating)
        
        # Check length anomalies
        length_check = self.detect_length_anomalies(review, rating)
        
        # Calculate bias score (0-100, lower is better)
        bias_score = 0.0
        
        # Penalize sentiment mismatch
        if not sentiment_check['is_aligned']:
            bias_score += sentiment_check['mismatch_score'] * 50
        
        # Penalize length anomalies
        if length_check['is_anomalous']:
            bias_score += 30
        
        # Invert to quality score (higher is better)
        quality_score = max(0, 100 - bias_score)
        
        return {
            'sentiment_alignment': sentiment_check,
            'length_check': length_check,
            'bias_score': bias_score,
            'quality_score': quality_score,
            'has_issues': not sentiment_check['is_aligned'] or length_check['is_anomalous']
        }
