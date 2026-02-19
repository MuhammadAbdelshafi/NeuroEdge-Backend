from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.db.models.paper import Paper
from app.db.models.summary import PaperSummary
from app.modules.summarization.llm_client import LLMClient
from app.modules.summarization.prompt_builder import PromptBuilder
from app.modules.summarization.parser import SummaryParser
from app.modules.summarization.config import summarization_settings

logger = logging.getLogger(__name__)

class SummarizationService:
    def __init__(self, db: Session):
        self.db = db
        self.client = LLMClient()
        self.parser = SummaryParser()

    def summarize_paper(self, paper: Paper) -> PaperSummary:
        """
        Full pipeline: Build Prompt -> Call LLM -> Parse -> Save
        """
        logger.info(f"Summarizing paper {paper.id}: {paper.title}")
        
        # Update status to processing
        paper.summarization_status = "processing"
        self.db.commit()
        
        try:
            # 1. Build Prompt
            prompt = PromptBuilder.build_summary_prompt(paper)
            
            # 2. Call LLM
            llm_output = self.client.generate(prompt)
            
            # 3. Parse Output
            structured_data = self.parser.parse(llm_output)
            
            # 4. Save Summary
            summary = PaperSummary(
                paper_id=paper.id,
                objective=structured_data.get("objective"),
                methods=structured_data.get("methods"),
                results=structured_data.get("results"),
                conclusion=structured_data.get("conclusion"),
                clinical_relevance=structured_data.get("clinical_relevance"),
                key_points=structured_data.get("key_points"),
                model_used=summarization_settings.SUMMARIZATION_MODEL
            )
            
            self.db.add(summary)
            
            # Update Paper Status
            paper.summarization_status = "completed"
            
            self.db.commit()
            self.db.refresh(summary)
            logger.info(f"Successfully summarized paper {paper.id}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize paper {paper.id}: {e}")
            self.db.rollback()
            paper.summarization_status = "failed"
            self.db.commit()
            raise e

    def summarize_next_batch(self, batch_size: int = 5):
        """
        Fetch classified papers pending summarization.
        Only process X at a time to respect rate limits.
        """
        # Fetch pending summaries where fetch is classified (meaning abstract is ready) or just exists.
        # Ideally we summarize classified papers.
        papers = self.db.query(Paper).filter(
            (Paper.summarization_status == "pending") | (Paper.summarization_status == None),
            Paper.abstract.isnot(None),
            Paper.abstract != ""
        ).limit(batch_size).all()
        
        logger.info(f"Found {len(papers)} papers pending summarization.")
        
        for paper in papers:
            try:
                self.summarize_paper(paper)
            except Exception:
                continue # Logged inside summarize_paper
