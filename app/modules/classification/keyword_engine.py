import yaml
import re
from pathlib import Path
from typing import Dict, List, Any

# Get current directory
CURRENT_DIR = Path(__file__).parent
CONFIG_DIR = CURRENT_DIR / "config"

class KeywordLoader:
    @staticmethod
    def _load_yaml(filename: str) -> Dict[str, List[str]]:
        file_path = CONFIG_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
                return data or {}
            except yaml.YAMLError as e:
                print(f"Error parse YAML file {filename}: {e}")
                return {}

    @classmethod
    def load_subspecialties(cls) -> Dict[str, List[str]]:
        return cls._load_yaml("subspecialty_keywords.yaml")

    @classmethod
    def load_research_types(cls) -> Dict[str, List[str]]:
        return cls._load_yaml("research_type_keywords.yaml")


class KeywordScorer:
    @staticmethod
    def score(text: str, keywords: List[str]) -> int:
        """
        Count occurrences of keywords in text using regex word boundaries.
        Returns the total count of matches.
        """
        score = 0
        if not text or not keywords:
            return 0
            
        for kw in keywords:
            # Escape regex special characters in keyword
            escaped_kw = re.escape(kw)
            # Use word boundaries with case insensitive flag (though text is already lowercased)
            # \b matches word boundary
            pattern = rf"\b{escaped_kw}\b"
            
            # Find all non-overlapping matches
            matches = re.findall(pattern, text)
            score += len(matches)
            
        return score
