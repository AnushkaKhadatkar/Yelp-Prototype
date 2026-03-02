from pydantic import BaseModel
from typing import Optional


class PreferenceResponse(BaseModel):
    cuisines: Optional[str] = None
    price_range: Optional[str] = None
    location: Optional[str] = None
    dietary_needs: Optional[str] = None
    ambiance: Optional[str] = None
    sort_preference: Optional[str] = None


class PreferenceUpdate(BaseModel):
    cuisines: Optional[str] = None
    price_range: Optional[str] = None
    location: Optional[str] = None
    dietary_needs: Optional[str] = None
    ambiance: Optional[str] = None
    sort_preference: Optional[str] = None