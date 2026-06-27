from sqlalchemy.orm import Session
from app.models.user import User, UserTopicProgress
from app.models.topic import Topic

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, name: str, email: str, password_hash: str) -> User:
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        streak_count=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def initialize_user_topic_progress(db: Session, user_id: int):
    # Retrieve all seeded topics
    topics = db.query(Topic).order_by(Topic.order_index).all()
    
    for topic in topics:
        # Check if progress record already exists
        exists = db.query(UserTopicProgress).filter(
            UserTopicProgress.user_id == user_id,
            UserTopicProgress.topic_id == topic.id
        ).first()
        
        if not exists:
            # Unlock the first topic (order_index == 1) by default, lock subsequent topics
            is_unlocked = (topic.order_index == 1)
            
            progress = UserTopicProgress(
                user_id=user_id,
                topic_id=topic.id,
                solved_count=0,
                total_count=topic.total_questions,
                is_unlocked=is_unlocked
            )
            db.add(progress)
    
    db.commit()
