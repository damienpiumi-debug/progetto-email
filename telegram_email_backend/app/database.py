from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL


try:
    engine = create_engine(DATABASE_URL)
    print("database connected successfully")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

except Exception as e:
    print(f"error connecting to the database: {e}")
    
    # base per i modelli
Base = declarative_base()


