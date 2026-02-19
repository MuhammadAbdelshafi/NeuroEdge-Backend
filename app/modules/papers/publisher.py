import logging

logger = logging.getLogger(__name__)

class PaperPublisher:
    """
    Handles publishing events when a new paper is ingested.
    For MVP, this will just log the event.
    Refactor via RabbitMQ/SQS later.
    """
    def __init__(self):
        pass

    def push_new_paper(self, paper_id: str, title: str):
        """Publish NEW_PAPER_INGESTED event"""
        event_payload = {
            "event": "NEW_PAPER_INGESTED",
            "paper_id": paper_id,
            "title": title
        }
        # TODO: Replace with actual Queue publish
        logger.info(f" [EVENT PUBLISHED] New Paper Ingested: {title} (ID: {paper_id})")
