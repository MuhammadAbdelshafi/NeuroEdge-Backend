import re
import json
import logging

logger = logging.getLogger(__name__)

class SummaryParser:
    @staticmethod
    def parse(llm_output: str) -> dict:
        """
        Parses the structured output from Mistral.
        Expected format:
        Objective: ...
        Methods: ...
        Results: ...
        Conclusion: ...
        Clinical Relevance: ...
        Key Points: ...
        """
        parsed = {}
        
        # Define regex patterns for each section
        # We look for the section header and capture everything until the next section or end of string
        # Using DOTALL to capture newlines
        
        sections = [
            "Objective",
            "Methods",
            "Results",
            "Conclusion",
            "Clinical Relevance",
            "Key Points"
        ]
        
        # We can iterate and find indices
        lower_output = llm_output.lower()
        
        for i, section in enumerate(sections):
            start_idx = lower_output.find(section.lower() + ":")
            if start_idx == -1:
                logger.warning(f"Section '{section}' not found in LLM output.")
                parsed[section.lower().replace(" ", "_")] = None
                continue
            
            # Start after "Section:"
            content_start = start_idx + len(section) + 1
            
            # Find end index (start of next section)
            end_idx = len(llm_output)
            
            # Look for the earliest occurrence of any subsequent section
            for next_section in sections[i+1:]:
                next_in = lower_output.find(next_section.lower() + ":", content_start)
                if next_in != -1:
                    end_idx = min(end_idx, next_in)
            
            content = llm_output[content_start:end_idx].strip()
            # Clean up leading/trailing dashes or stars if model added bullets
            content = re.sub(r'^[\-\*]\s+', '', content)
            
            parsed_key = section.lower().replace(" ", "_")
            parsed[parsed_key] = content

        # Special handling for Key Points (should be JSON list)
        key_points_raw = parsed.get("key_points")
        if key_points_raw:
            # Remove Markdown code blocks if present
            key_points_raw = re.sub(r'```json\s*', '', key_points_raw)
            key_points_raw = re.sub(r'```\s*', '', key_points_raw)
            key_points_raw = key_points_raw.strip()

            try:
                # Try to parse strict JSON first if model outputted JSON
                if key_points_raw.startswith("[") and key_points_raw.endswith("]"):
                    loaded = json.loads(key_points_raw)
                    # If it's a list, check elements
                    if isinstance(loaded, list):
                        final_points = []
                        for item in loaded:
                            if isinstance(item, str):
                                final_points.append(item)
                            elif isinstance(item, dict):
                                # Extract values from dict
                                final_points.extend([str(v) for v in item.values()])
                            else:
                                final_points.append(str(item))
                        parsed["key_points"] = final_points
                    else:
                         parsed["key_points"] = list(loaded.values()) if isinstance(loaded, dict) else [str(loaded)]
                else:
                    raise ValueError("Not a JSON array")
            except Exception as e:
                logger.warning(f"Failed to parse key points JSON: {e}. Falling back to line splitting.")
                # Fallback: Split by newlines or bullets
                points = [
                    line.strip().lstrip("-*•").strip() 
                    for line in key_points_raw.split('\n') 
                    if line.strip().lstrip("-*•").strip()
                ]
                parsed["key_points"] = points
        else:
             parsed["key_points"] = []

        return parsed
