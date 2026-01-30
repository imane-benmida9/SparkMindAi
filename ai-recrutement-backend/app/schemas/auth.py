from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["candidat", "recruteur"]
    nom: str | None = None  # Nom du candidat ou entreprise du recruteur


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


class MeResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    is_active: bool
