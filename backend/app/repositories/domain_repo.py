from sqlalchemy.orm import Session
from app.models import Domain, Topic, UserTopicProgress

def get_all_domains(db: Session):
    return db.query(Domain).order_by(Domain.order_index).all()

def get_domain_by_slug(db: Session, slug: str) -> Domain:
    return db.query(Domain).filter(Domain.slug == slug).first()

def get_topics_by_domain_id(db: Session, domain_id: int):
    return db.query(Topic).filter(Topic.domain_id == domain_id).order_by(Topic.order_index).all()

def get_user_topic_progress(db: Session, user_id: int, topic_id: int) -> UserTopicProgress:
    return db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == user_id,
        UserTopicProgress.topic_id == topic_id
    ).first()

def get_all_user_topic_progresses(db: Session, user_id: int):
    progresses = db.query(UserTopicProgress).filter(UserTopicProgress.user_id == user_id).all()
    return {p.topic_id: p for p in progresses}
