from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="unsolved", nullable=False)  # unsolved, solved, revisit
    notes = Column(Text, nullable=True)
    attempts = Column(Integer, default=0, nullable=False)
    solve_time = Column(Integer, default=0, nullable=False)  # in seconds
    bookmark = Column(Boolean, default=False, nullable=False)
    accuracy = Column(Float, default=100.0, nullable=False)  # 0 to 100
    solved_at = Column(DateTime, nullable=True)

    # SuperMemo SM-2 Spaced Repetition parameters
    srs_interval = Column(Integer, default=0, nullable=False)  # in days
    srs_ease_factor = Column(Float, default=2.5, nullable=False)
    srs_repetitions = Column(Integer, default=0, nullable=False)
    next_revision_date = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="progress")
    question = relationship("Question", back_populates="user_progresses")

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uq_user_question"),
    )
