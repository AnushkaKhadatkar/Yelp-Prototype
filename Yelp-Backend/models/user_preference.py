from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from database import Base

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    cuisines = Column(String(255))
    price_range = Column(Enum("$", "$$", "$$$", "$$$$"))
    preferred_locations = Column(String(255))
    dietary_needs = Column(String(255))
    ambiance = Column(String(255))
    sort_preference = Column(String(50))