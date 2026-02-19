from sqlalchemy.orm import Session
import json

from app.modules.classification.preprocessing import TextCleaner
from app.modules.classification.classifiers import SubspecialtyClassifier, ResearchTypeClassifier, ConfidenceCalculator
from app.db.models.paper import Paper
# We will need a way to update the paper. 
# Assuming we have repository access or direct DB session.

class PaperClassificationService:
    def __init__(self, db: Session):
        self.db = db
        self.cleaner = TextCleaner()
        self.sub_classifier = SubspecialtyClassifier()
        self.rt_classifier = ResearchTypeClassifier()
        self.confidence_calc = ConfidenceCalculator()
        
    def classify_paper(self, paper: Paper) -> Paper:
        """
        Run classification pipeline on a single paper and update it in the DB.
        """
        # 1. Prepare Text
        # Combine title and abstract. inner join with space.
        raw_text = f"{paper.title} {paper.abstract or ''}"
        clean_text = self.cleaner.clean(raw_text)
        
        # 2. Run Classifiers
        subspecialties = self.sub_classifier.classify(clean_text)
        research_type = self.rt_classifier.classify(clean_text)
        
        # 3. Compute Confidence
        confidence = self.confidence_calc.compute(clean_text, subspecialties, research_type)
        
        # 4. Update Paper
        # Ensure we store list as JSON string if DB doesn't support JSON type natively in a way SQLAlchemy handles automatically without TypeDecorator
        # But commonly SQLAlchemy with SQLite types.JSON works if handled correctly. 
        # For safety/simplicity in MVP with SQLite, we might serialize here if model expects Text.
        # Let's assume the Model will handle it or we update the model to use JSON type.
        
        paper.subspecialties = subspecialties # SQLAlchemy JSON type should handle list
        paper.research_type = research_type
        paper.classification_confidence = confidence
        paper.classification_status = "completed"
        
        self.db.add(paper)
        self.db.commit()
        self.db.refresh(paper)
        
        return paper

    def classify_all_pending(self, batch_size: int = 100):
        """
        Fetch pending papers and classify them.
        """
        # Query papers where classification_status is pending or null
        papers = self.db.query(Paper).filter(
            (Paper.classification_status == None) | (Paper.classification_status == 'pending')
        ).limit(batch_size).all()
        
        print(f"Found {len(papers)} pending papers for classification.")
        
        for p in papers:
            try:
                self.classify_paper(p)
            except Exception as e:
                print(f"Failed to classify paper {p.id}: {e}")
                # Optionally mark as failed
                p.classification_status = "failed"
                self.db.add(p)
                self.db.commit()
