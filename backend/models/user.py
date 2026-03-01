from sqlalchemy import Column, Integer, String, Text, Enum, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    phone = Column(String(20))
    about = Column(Text)
    city = Column(String(100))
    state = Column(String(10))
    country = Column(String(100))
    languages = Column(String(255))
    gender = Column(String(20))
    profile_pic = Column(String(255))
    restaurant_location = Column(String(255), nullable=True)
    role = Column(Enum("user", "owner"), default="user")

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )