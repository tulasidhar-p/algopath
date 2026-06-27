from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for self-referential topic prerequisites
topic_prerequisite_association = Table(
    "topic_prerequisites",
    Base.metadata,
    Column("topic_id", Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True),
    Column("prerequisite_id", Integer, ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True),
)

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    icon = Column(String(50), nullable=True)
    unlock_percentage = Column(Float, default=0.3, nullable=False) # Configurable threshold (e.g. 0.3 = 30%)
    learning_objectives = Column(Text, nullable=True) # Stored as JSON string listing learning targets
    total_questions = Column(Integer, default=0, nullable=False)

    # Relationships
    domain = relationship("Domain", back_populates="topics")
    patterns = relationship("Pattern", back_populates="topic", cascade="all, delete-orphan")
    user_topic_progresses = relationship("UserTopicProgress", back_populates="topic", cascade="all, delete-orphan")
    
    prerequisites = relationship(
        "Topic",
        secondary=topic_prerequisite_association,
        primaryjoin="Topic.id==topic_prerequisites.c.topic_id",
        secondaryjoin="Topic.id==topic_prerequisites.c.prerequisite_id",
        backref="required_by"
    )
