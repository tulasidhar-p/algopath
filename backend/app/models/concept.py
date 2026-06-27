from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for self-referential concept prerequisites
concept_prerequisite_association = Table(
    "concept_prerequisites",
    Base.metadata,
    Column("concept_id", Integer, ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True),
    Column("prerequisite_id", Integer, ForeignKey("concepts.id", ondelete="CASCADE"), primary_key=True),
)

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_id = Column(Integer, ForeignKey("patterns.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    theory_markdown = Column(Text, nullable=True) # Full Markdown theory explanations
    learning_objectives = Column(Text, nullable=True) # Stored as JSON string
    order_index = Column(Integer, nullable=False)

    # Relationships
    pattern = relationship("Pattern", back_populates="concepts")
    questions = relationship("Question", back_populates="concept", cascade="all, delete-orphan")
    
    prerequisites = relationship(
        "Concept",
        secondary=concept_prerequisite_association,
        primaryjoin="Concept.id==concept_prerequisites.c.concept_id",
        secondaryjoin="Concept.id==concept_prerequisites.c.prerequisite_id",
        backref="required_by"
    )
