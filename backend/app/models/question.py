from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for Question <-> Tag
question_tag_links = Table(
    "question_tag_links",
    Base.metadata,
    Column("question_id", Integer, ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for Question <-> Company
question_company_links = Table(
    "question_company_links",
    Base.metadata,
    Column("question_id", Integer, ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True),
    Column("company_id", Integer, ForeignKey("companies.id", ondelete="CASCADE"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relationships
    questions = relationship("Question", secondary=question_tag_links, back_populates="tags")


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)

    # Relationships
    questions = relationship("Question", secondary=question_company_links, back_populates="companies")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    concept_id = Column(Integer, ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    difficulty = Column(String(50), nullable=False)  # Easy, Medium, Hard
    source = Column(String(100), nullable=False)  # LeetCode, CodeForces, CodeChef, HackerRank, GeeksForGeeks
    url = Column(String(500), nullable=False)
    estimated_solve_time = Column(Integer, default=30, nullable=False)  # Minutes
    is_important = Column(Boolean, default=False, nullable=False)
    order_index = Column(Integer, nullable=False)

    # Relationships
    concept = relationship("Concept", back_populates="questions")
    tags = relationship("Tag", secondary=question_tag_links, back_populates="questions")
    companies = relationship("Company", secondary=question_company_links, back_populates="questions")
    user_progresses = relationship("UserProgress", back_populates="question", cascade="all, delete-orphan")
