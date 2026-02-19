from app.db.session import engine
from app.db.base import Base
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_user_schema():
    logger.info("Updating user schema with preference columns...")
    with engine.connect() as conn:
        # Check if columns exist (simple check for sqlite/postgres agnostic)
        try:
            conn.execute(text("SELECT subspecialties FROM users LIMIT 1"))
            logger.info("Column 'subspecialties' already exists.")
        except Exception:
            logger.info("Adding 'subspecialties' column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN subspecialties JSON DEFAULT '[]'"))

        try:
            conn.execute(text("SELECT research_types FROM users LIMIT 1"))
            logger.info("Column 'research_types' already exists.")
        except Exception:
            logger.info("Adding 'research_types' column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN research_types JSON DEFAULT '[]'"))

        try:
            conn.execute(text("SELECT email_frequency FROM users LIMIT 1"))
            logger.info("Column 'email_frequency' already exists.")
        except Exception:
            logger.info("Adding 'email_frequency' column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN email_frequency VARCHAR DEFAULT 'weekly'"))

        try:
            conn.execute(text("SELECT last_notification_date FROM users LIMIT 1"))
            logger.info("Column 'last_notification_date' already exists.")
        except Exception:
            logger.info("Adding 'last_notification_date' column...")
            conn.execute(text("ALTER TABLE users ADD COLUMN last_notification_date TIMESTAMP"))
            
        conn.commit()
    logger.info("User schema updated successfully.")

if __name__ == "__main__":
    update_user_schema()
