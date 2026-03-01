from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    cuisine = Column(String(100), nullable=False)

    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(10))
    zip_code = Column(String(20))

    description = Column(Text)
    contact_phone = Column(String(20))
    contact_email = Column(String(150))

    price_tier = Column(Enum("$", "$$", "$$$", "$$$$"))
    ambiance = Column(String(255))
    amenities = Column(String(255))
    hours = Column(Text)
    photos = Column(Text)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    avg_rating = Column(DECIMAL(2, 1), default=0.0)
    review_count = Column(Integer, default=0)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())