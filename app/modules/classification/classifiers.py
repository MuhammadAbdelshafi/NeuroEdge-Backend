from typing import List, Dict, Any
from app.modules.classification.keyword_engine import KeywordLoader, KeywordScorer

class SubspecialtyClassifier:
    def __init__(self):
        self.taxonomy = KeywordLoader.load_subspecialties()
        self.scorer = KeywordScorer()
        
    def classify(self, text: str) -> List[str]:
        """
        Classify text into multiple subspecialties based on keyword hits.
        Returns a list of matching subspecialties.
        Default: ["General Neurology"]
        """
        scores = {}
        for label, keywords in self.taxonomy.items():
            scores[label] = self.scorer.score(text, keywords)
            
        # Select labels with at least one match
        labels = [label for label, score in scores.items() if score > 0]
        
        # Sort by score descending (optional, but nice to have primary first)
        labels.sort(key=lambda l: scores[l], reverse=True)
        
        if not labels:
            return ["General Neurology"]
            
        return labels

class ResearchTypeClassifier:
    def __init__(self):
        self.taxonomy = KeywordLoader.load_research_types()
        self.scorer = KeywordScorer()
        
    def classify(self, text: str) -> str:
        """
        Classify text into a single research type based on highest keyword hits.
        Returns the best matching research type.
        Default: "Other"
        """
        scores = {}
        for label, keywords in self.taxonomy.items():
            scores[label] = self.scorer.score(text, keywords)
            
        if not scores:
            return "Other"
            
        # Find the label with the maximum score
        best_label = max(scores, key=scores.get)
        
        # If max score is 0, return Other
        if scores[best_label] == 0:
            return "Other"
            
        return best_label

class ConfidenceCalculator:
    @staticmethod
    def compute(text: str, subspecialties: List[str], research_type: str) -> float:
        """
        Compute a confidence score (0.0 - 1.0) based on total keyword hits.
        Simple heuristic: more hits = higher confidence.
        Target 5 hits = 1.0 confidence.
        """
        # We could re-score or pass scores down, but for MVP let's re-calculate total hits roughly
        # Or better yet, we can't easily access the scores here without refactoring.
        # Let's simple count hits again using the assigned labels' keywords
        
        total_hits = 0
        scorer = KeywordScorer()
        
        # Add hits from subspecialties
        sub_taxonomy = KeywordLoader.load_subspecialties()
        for sub in subspecialties:
             if sub in sub_taxonomy:
                 total_hits += scorer.score(text, sub_taxonomy[sub])
                 
        # Add hits from research type
        rt_taxonomy = KeywordLoader.load_research_types()
        if research_type in rt_taxonomy:
            total_hits += scorer.score(text, rt_taxonomy[research_type])
            
        # Formula: min(1.0, hits / 5)
        return min(1.0, total_hits / 5.0)
