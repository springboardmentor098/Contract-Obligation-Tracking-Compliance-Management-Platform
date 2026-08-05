
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

#database engine is created using the create_engine function from SQLAlchemy. The DATABASE_URL environment variable is passed as an argument to this function, which specifies the database connection details such as the database type, username, password, host, port, and database name. The engine is responsible for managing the connection pool and executing SQL statements against the database.
engine = create_engine(
    settings.DATABASE_URL
)

#sessionmaker is a factory for creating new Session objects. It is used to manage database connections and transactions. The sessionmaker function takes several parameters, including autocommit, autoflush, and bind. In this case, we set autocommit and autoflush to False, which means that changes made to the database will not be automatically committed or flushed to the database until we explicitly call commit() or flush(). The bind parameter is set to the engine we created earlier, which allows the session to connect to the database specified in the DATABASE_URL environment variable.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
#To create the base class for our models, we use the declarative_base function from SQLAlchemy. This base class will be used to define our database models.
Base = declarative_base()

#dependency to get the database session
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