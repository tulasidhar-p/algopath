import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.models import Domain, Topic

@pytest.fixture(name="db_session")
def db_session_fixture():
    """Fixture that initializes an in-memory SQLite database, creates all schemas, and yields a session."""
    engine = create_engine(
        "sqlite:///:memory:", 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Ensure all tables are registered on metadata
    import app.models  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(name="seeded_topics")
def seeded_topics_fixture(db_session):
    """Fixture that seeds a mockup domain and topics for testing user progress initialization."""
    domain = Domain(
        name="Data Structures",
        slug="dsa",
        description="Data Structures & Algorithms",
        order_index=1
    )
    db_session.add(domain)
    db_session.commit()
    db_session.refresh(domain)
    
    topic1 = Topic(
        domain_id=domain.id,
        name="Arrays & Hashing",
        slug="arrays",
        description="Learn arrays and hashing",
        order_index=1,
        total_questions=5
    )
    topic2 = Topic(
        domain_id=domain.id,
        name="Two Pointers",
        slug="two-pointers",
        description="Learn two pointer techniques",
        order_index=2,
        total_questions=3
    )
    db_session.add_all([topic1, topic2])
    db_session.commit()
    db_session.refresh(topic1)
    db_session.refresh(topic2)
    return [topic1, topic2]
