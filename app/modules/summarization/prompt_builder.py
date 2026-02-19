from app.db.models.paper import Paper

class PromptBuilder:
    @staticmethod
    def build_summary_prompt(paper: Paper) -> str:
        """
        Constructs a prompt for Mistral-7B-Instruct to summarize the paper.
        """
        # Clean abstract slightly if needed
        abstract = paper.abstract or "No abstract available."
        
        prompt = f"""[INST] You are a specialized Neurology Research Assistant. Your task is to summarize the following research paper abstract for a clinician.

Global Constraints:
1. Do NOT use markdown formatting (no bolding like **text**, no italics).
2. Do NOT use filler phrases like "Not explicitly detailed in the abstract", "Inferred from context", or "Key findings implied". 
3. If a section is missing from the abstract, write "Not available." or omit the section content.
4. Be concise and professional.

Please extract/generate the following sections:
- Objective: (What was the goal? Max 1 sentence)
- Methods: (How was it done? Study design, N=? Max 2 sentences)
- Results: (What were the key findings? P-values, Hazard Ratios if avail. Max 3 sentences)
- Conclusion: (What do these results mean? Max 1 sentence)
- Clinical Relevance: (Why does this matter for a neurologist? Max 1 sentence)
- Key Points: (Provide 3 concise bullet points as a JSON list)

Return the output in the following format:
Objective: ...
Methods: ...
Results: ...
Conclusion: ...
Clinical Relevance: ...
Key Points: ...

Abstract:
{abstract}
[/INST]"""
        return prompt
