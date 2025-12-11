"""Domain realism validator for dev tool reviews"""

import re
from typing import Dict, Any, List, Set


class RealismValidator:
    """Validate domain realism of dev tool reviews"""
    
    def __init__(self):
        """Initialize realism validator"""
        # Technical vocabulary for dev tools
        self.technical_terms = {
            # General dev terms
            'api', 'sdk', 'cli', 'gui', 'ui', 'ux', 'integration', 'plugin',
            'extension', 'workflow', 'pipeline', 'automation', 'deployment',
            'configuration', 'setup', 'installation', 'documentation', 'docs',
            
            # Programming concepts
            'code', 'debug', 'debugging', 'testing', 'test', 'unit test',
            'integration test', 'endpoint', 'request', 'response', 'json',
            'xml', 'yaml', 'rest', 'graphql', 'webhook', 'authentication',
            'authorization', 'oauth', 'token', 'jwt',
            
            # DevOps terms
            'ci/cd', 'continuous integration', 'continuous deployment',
            'container', 'docker', 'kubernetes', 'k8s', 'microservices',
            'monitoring', 'logging', 'metrics', 'observability', 'tracing',
            'alert', 'dashboard', 'visualization',
            
            # Performance terms
            'performance', 'latency', 'throughput', 'scalability', 'optimization',
            'caching', 'load time', 'response time', 'bottleneck',
            
            # Quality terms
            'bug', 'issue', 'error', 'exception', 'crash', 'stability',
            'reliability', 'uptime', 'downtime', 'maintenance',
            
            # Development workflow
            'git', 'github', 'gitlab', 'version control', 'commit', 'branch',
            'merge', 'pull request', 'pr', 'code review', 'refactor',
            'repository', 'repo'
        }
        
        # Generic/marketing phrases that reduce realism
        self.generic_phrases = [
            'game changer', 'revolutionary', 'best ever', 'perfect solution',
            'absolutely amazing', 'mind blowing', 'life changing', 'incredible tool',
            'flawless', 'without any issues', 'zero problems', 'perfect in every way'
        ]
    
    def count_technical_terms(self, review: str) -> int:
        """
        Count technical terms in review
        
        Args:
            review: Review text
            
        Returns:
            Number of technical terms found
        """
        review_lower = review.lower()
        count = 0
        
        for term in self.technical_terms:
            if term in review_lower:
                count += 1
        
        return count
    
    def check_specific_features(self, review: str) -> bool:
        """
        Check if review mentions specific features (not just generic praise)
        
        Args:
            review: Review text
            
        Returns:
            True if specific features are mentioned
        """
        # Look for patterns that indicate specific features
        patterns = [
            r'\b(feature|functionality|capability|option|setting)\b',
            r'\b(allows|enables|supports|provides|includes)\b',
            r'\b(integration with|works with|compatible with)\b',
            r'\b(can|could|able to)\b.*\b(do|use|configure|customize)\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, review, re.IGNORECASE):
                return True
        
        return False
    
    def check_balanced_critique(self, review: str, rating: int) -> bool:
        """
        Check if review has balanced critique (pros and cons for mid-range ratings)
        
        Args:
            review: Review text
            rating: Rating (1-5)
            
        Returns:
            True if appropriately balanced
        """
        # For 3-star reviews, expect both positive and negative aspects
        if rating == 3:
            has_positive = any(word in review.lower() for word in [
                'good', 'great', 'nice', 'helpful', 'useful', 'works', 'like', 'love'
            ])
            has_negative = any(word in review.lower() for word in [
                'but', 'however', 'unfortunately', 'issue', 'problem', 'bug',
                'missing', 'lack', 'could', 'should', 'wish', 'hope'
            ])
            return has_positive and has_negative
        
        # For 4-5 star, should have mostly positive with minor critiques
        elif rating >= 4:
            has_positive = any(word in review.lower() for word in [
                'good', 'great', 'excellent', 'helpful', 'useful', 'love', 'recommend'
            ])
            return has_positive
        
        # For 1-2 star, should have mostly negative
        else:
            has_negative = any(word in review.lower() for word in [
                'bad', 'poor', 'terrible', 'awful', 'issue', 'problem', 'bug',
                'disappointing', 'frustrated', 'waste'
            ])
            return has_negative
    
    def detect_generic_phrases(self, review: str) -> List[str]:
        """
        Detect generic marketing phrases
        
        Args:
            review: Review text
            
        Returns:
            List of generic phrases found
        """
        found_phrases = []
        review_lower = review.lower()
        
        for phrase in self.generic_phrases:
            if phrase in review_lower:
                found_phrases.append(phrase)
        
        return found_phrases
    
    def check_use_case_mention(self, review: str) -> bool:
        """
        Check if review mentions a specific use case or context
        
        Args:
            review: Review text
            
        Returns:
            True if use case is mentioned
        """
        # Look for patterns indicating use case
        patterns = [
            r'\b(use|using|used)\b.*\b(for|to|in|with)\b',
            r'\b(project|team|company|work|development)\b',
            r'\b(need|needed|require|required)\b',
            r'\b(my|our|we|i)\b.*\b(project|workflow|pipeline|setup)\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, review, re.IGNORECASE):
                return True
        
        return False
    
    def calculate_realism_score(self, review: str, rating: int) -> Dict[str, Any]:
        """
        Calculate overall realism score
        
        Args:
            review: Review text
            rating: Rating (1-5)
            
        Returns:
            Dictionary with realism metrics and overall score
        """
        # Count technical terms
        tech_term_count = self.count_technical_terms(review)
        has_enough_tech_terms = tech_term_count >= 2
        
        # Check specific features
        mentions_features = self.check_specific_features(review)
        
        # Check balanced critique
        is_balanced = self.check_balanced_critique(review, rating)
        
        # Detect generic phrases
        generic_phrases = self.detect_generic_phrases(review)
        has_generic_phrases = len(generic_phrases) > 0
        
        # Check use case
        mentions_use_case = self.check_use_case_mention(review)
        
        # Calculate realism score (0-100)
        score = 0.0
        
        # Technical terms (30 points)
        if has_enough_tech_terms:
            score += 30
        else:
            score += tech_term_count * 10  # Partial credit
        
        # Specific features (25 points)
        if mentions_features:
            score += 25
        
        # Balanced critique (20 points)
        if is_balanced:
            score += 20
        
        # Use case mention (15 points)
        if mentions_use_case:
            score += 15
        
        # No generic phrases (10 points)
        if not has_generic_phrases:
            score += 10
        
        return {
            'technical_term_count': tech_term_count,
            'has_enough_tech_terms': has_enough_tech_terms,
            'mentions_features': mentions_features,
            'is_balanced': is_balanced,
            'mentions_use_case': mentions_use_case,
            'generic_phrases_found': generic_phrases,
            'has_generic_phrases': has_generic_phrases,
            'realism_score': min(100, score),
            'passes_realism': score >= 60
        }
