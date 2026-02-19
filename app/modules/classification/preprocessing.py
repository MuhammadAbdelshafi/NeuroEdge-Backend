import re
import string

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        """
        Normalize text for keyword matching:
        - Lowercase
        - Remove punctuation
        - Normalize whitespace
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove punctuation (replace with space to avoid merging words like "bi-lateral" -> "bilateral")
        # However, for some medical terms, we might want to keep hyphens, but generally removing them is safer for broad matching
        # or replacing them with spaces.
        # Let's replace punctuation with space, then normalize whitespace
        translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        text = text.translate(translator)
        
        # Remove extra whitespace (newlines, tabs, double spaces)
        text = " ".join(text.split())
        
        return text
