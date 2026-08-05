from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()



def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
def test_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        print("Database connection successful.")

    except Exception as error:
        print("Database connection failed.")
        print(error)