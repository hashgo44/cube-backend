from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None


class ArticleResponse(ArticleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

