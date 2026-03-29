from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. For Docker Compose use host `mysql` (see docker-compose.yml). "
        "For local dev set it in backend/.env."
    )

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def init_db() -> None:
    """Create tables if they do not exist. Import all model modules so metadata is complete."""
    import models.user  # noqa: F401
    import models.restaurant  # noqa: F401
    import models.review  # noqa: F401
    import models.favourite  # noqa: F401
    import models.user_preference  # noqa: F401
    try:
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        orig = getattr(e, "orig", None)
        code = getattr(orig, "args", [None])[0] if orig is not None else None
        if code == 1050:
            return
        raise


# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()