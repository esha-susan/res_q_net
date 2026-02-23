from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace 'your_password' with your local MySQL password
# Ensure you have created the database 'resqnet_db' in MySQL first
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:taesha123@localhost/resqnet_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()