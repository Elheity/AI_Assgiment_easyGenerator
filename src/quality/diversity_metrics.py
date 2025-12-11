"""Diversity metrics for review quality assessment"""

import numpy as np
from typing import List, Dict, Any
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


class DiversityMetrics:
    """Calculate diversity metrics for generated reviews"""
    
    def __init__(self):
        """Initialize diversity metrics calculator"""
        # Load sentence transformer for semantic similarity (CPU to avoid CUDA 6.1 issues)
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        self.embeddings_cache = {}
        
    def calculate_vocabulary_overlap(self, reviews: List[str]) -> float:
        """
        Calculate vocabulary diversity (unique words ratio)
        
        Args:
            reviews: List of review texts
            
        Returns:
            Ratio of unique words to total words (0-1, higher is more diverse)
        """
        if not reviews:
            return 0.0
        
        all_words = []
        for review in reviews:
            words = review.lower().split()
            all_words.extend(words)
        
        if not all_words:
            return 0.0
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        
        return unique_words / total_words
    
    def calculate_semantic_similarity(self, review: str, existing_reviews: List[str]) -> float:
        """
        Calculate maximum semantic similarity between a review and existing reviews
        
        Args:
            review: New review text
            existing_reviews: List of existing review texts
            
        Returns:
            Maximum cosine similarity (0-1, lower is more diverse)
        """
        if not existing_reviews:
            return 0.0
        
        # Get embedding for new review
        review_embedding = self.model.encode([review])[0]
        
        # Get embeddings for existing reviews
        existing_embeddings = self.model.encode(existing_reviews)
        
        # Calculate cosine similarities
        similarities = cosine_similarity(
            [review_embedding],
            existing_embeddings
        )[0]
        
        # Return maximum similarity
        return float(np.max(similarities))
    
    def calculate_ngram_diversity(self, reviews: List[str], n: int = 3) -> float:
        """
        Calculate n-gram diversity (ratio of unique n-grams)
        
        Args:
            reviews: List of review texts
            n: N-gram size (default: 3 for trigrams)
            
        Returns:
            Ratio of unique n-grams to total n-grams (0-1, higher is more diverse)
        """
        if not reviews:
            return 0.0
        
        all_ngrams = []
        for review in reviews:
            words = review.lower().split()
            ngrams = [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]
            all_ngrams.extend(ngrams)
        
        if not all_ngrams:
            return 0.0
        
        unique_ngrams = len(set(all_ngrams))
        total_ngrams = len(all_ngrams)
        
        return unique_ngrams / total_ngrams
    
    def calculate_diversity_score(
        self,
        review: str,
        existing_reviews: List[str],
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate overall diversity score
        
        Args:
            review: New review text
            existing_reviews: List of existing reviews
            weights: Weights for different metrics (default: equal weights)
            
        Returns:
            Dictionary with individual metrics and overall score
        """
        if weights is None:
            weights = {
                'semantic_similarity': 0.6,  # Most important
                'vocabulary': 0.2,
                'ngram': 0.2
            }
        
        # Calculate semantic similarity (lower is better, so invert)
        semantic_sim = self.calculate_semantic_similarity(review, existing_reviews)
        semantic_diversity = 1.0 - semantic_sim
        
        # Calculate vocabulary diversity for all reviews including new one
        all_reviews = existing_reviews + [review]
        vocab_diversity = self.calculate_vocabulary_overlap(all_reviews)
        
        # Calculate n-gram diversity
        ngram_diversity = self.calculate_ngram_diversity(all_reviews)
        
        # Calculate weighted overall score (0-100)
        overall_score = (
            semantic_diversity * weights['semantic_similarity'] +
            vocab_diversity * weights['vocabulary'] +
            ngram_diversity * weights['ngram']
        ) * 100
        
        return {
            'semantic_similarity': semantic_sim,
            'semantic_diversity': semantic_diversity,
            'vocabulary_diversity': vocab_diversity,
            'ngram_diversity': ngram_diversity,
            'overall_diversity_score': overall_score,
            'max_similarity_threshold_exceeded': semantic_sim > 0.85
        }
