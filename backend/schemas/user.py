from pydantic import BaseModel, EmailStr, Field

# ---------- Signup ----------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


# ---------- Login ----------

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------- Token Response ----------

class TokenResponse(BaseModel):
    token: str
    user_id: int
    role: str