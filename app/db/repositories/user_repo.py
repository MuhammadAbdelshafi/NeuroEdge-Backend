from sqlalchemy.orm import Session
from app.db.models.user import User
from app.core.auth.password_hasher import PasswordHasher
import uuid

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: uuid.UUID) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, password: str, phone: str = None, full_name: str = None, 
               age: int = None, nationality: str = "Egypt", place_of_work: str = None, 
               years_of_experience: int = 0, degree: str = None, linkedin_profile: str = None) -> User:
        hashed_password = PasswordHasher.get_password_hash(password)
        db_user = User(
            email=email,
            password_hash=hashed_password,
            phone_number=phone,
            full_name=full_name,
            age=age,
            nationality=nationality,
            place_of_work=place_of_work,
            years_of_experience=years_of_experience,
            degree=degree,
            linkedin_profile=linkedin_profile
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update(self, user_id: uuid.UUID, to_update: dict) -> User:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
            
        for key, value in to_update.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def change_password(self, user_id: uuid.UUID, new_password: str) -> User:
        hashed_password = PasswordHasher.get_password_hash(new_password)
        return self.update(user_id, {"password_hash": hashed_password})
