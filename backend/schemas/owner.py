from pydantic import BaseModel, EmailStr, Field

class OwnerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    restaurant_location: str