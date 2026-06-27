import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.services.seeding_service import seed_database
from app.models import Base  # Load all models to register metadata

def main():
    print("Initializing database tables...")
    # This will create tables in our configured database (SQLite or PostgreSQL)
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully!")

    print("Seeding curriculum data...")
    db = SessionLocal()
    try:
        seed_database(db)
        print("Curriculum data seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    main()
