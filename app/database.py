from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import cx_Oracle
from fastapi import HTTPException
import logging
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Oracle connection settings from environment variables
    dsn = cx_Oracle.makedsn(
        settings.DB_HOST,
        settings.DB_PORT,
        service_name=settings.DB_SERVICE
    )
    DATABASE_URL = f"oracle+cx_oracle://{settings.DB_USER}:{settings.DB_PASSWORD}@{dsn}"

    # Create engine with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=True
    )

    # Test the connection
    try:
        with engine.connect() as connection:
            # Use text() to create a proper SQLAlchemy text object
            connection.execute(text("SELECT 1 FROM DUAL"))
            logger.info("Successfully connected to the database")
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Database connection failed. Please check if Oracle is running and the service name is correct."
        )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    def get_db():
        db = SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Database operation failed"
            )
        finally:
            db.close()

except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Failed to initialize database connection. Please check your Oracle installation and configuration."
    )
