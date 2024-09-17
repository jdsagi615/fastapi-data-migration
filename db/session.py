from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///C:\\Users\\Juan David Salazar\\Desktop\\apichallenge\\globant.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) 