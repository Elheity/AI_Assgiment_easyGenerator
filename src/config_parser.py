"""Configuration parser for YAML/JSON config files"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
import random


class ConfigParser:
    """Parse and manage configuration for review generation"""
    
    def __init__(self, config_path: str):
        """
        Initialize config parser
        
        Args:
            config_path: Path to YAML or JSON config file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            if self.config_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif self.config_path.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {self.config_path.suffix}")
    
    def get_generation_settings(self) -> Dict[str, Any]:
        """Get generation settings"""
        return self.config.get('generation', {})
    
    def get_models(self) -> List[Dict[str, Any]]:
        """Get enabled model configurations"""
        models = self.config.get('models', [])
        return [m for m in models if m.get('enabled', True)]
    
    def get_personas(self) -> List[Dict[str, Any]]:
        """Get persona configurations"""
        return self.config.get('personas', [])
    
    def get_random_persona(self) -> Dict[str, Any]:
        """Get a random persona based on weights"""
        personas = self.get_personas()
        weights = [p.get('weight', 1.0) for p in personas]
        return random.choices(personas, weights=weights, k=1)[0]
    
    def get_rating_distribution(self) -> Dict[int, float]:
        """Get rating distribution"""
        dist = self.config.get('rating_distribution', {})
        # Convert string keys to integers
        return {int(k): v for k, v in dist.items()}
    
    def get_random_rating(self) -> int:
        """Get a random rating based on distribution"""
        dist = self.get_rating_distribution()
        ratings = list(dist.keys())
        weights = list(dist.values())
        return random.choices(ratings, weights=weights, k=1)[0]
    
    def get_tool_categories(self) -> List[Dict[str, Any]]:
        """Get dev tool categories"""
        return self.config.get('tool_categories', [])
    
    def get_random_tool_category(self) -> Dict[str, Any]:
        """Get a random tool category"""
        categories = self.get_tool_categories()
        return random.choice(categories)
    
    def get_review_characteristics(self) -> Dict[str, Any]:
        """Get review characteristics"""
        return self.config.get('review_characteristics', {})
    
    def get_quality_thresholds(self) -> Dict[str, Any]:
        """Get quality guardrail thresholds"""
        return self.config.get('quality_thresholds', {})
