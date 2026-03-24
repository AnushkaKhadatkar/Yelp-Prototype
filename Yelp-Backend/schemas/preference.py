from pydantic import BaseModel
from typing import Optional, List

class PreferenceResponse(BaseModel):
    cuisines: Optional[List[str]] = []
    price_range: Optional[str] = None
    location: Optional[str] = None
    dietary_needs: Optional[List[str]] = []
    ambiance: Optional[List[str]] = []
    sort_preference: Optional[str] = None

class PreferenceUpdate(BaseModel):
    cuisines: Optional[List[str]] = None
    price_range: Optional[str] = None
    location: Optional[str] = None
    dietary_needs: Optional[List[str]] = None
    ambiance: Optional[List[str]] = None
    sort_preference: Optional[str] = None