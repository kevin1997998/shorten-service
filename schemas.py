from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class URLBase(BaseModel):
    original_url: str


class URLInfo(BaseModel):
    short_url: str
    success: bool
    expiration_date: Optional[datetime]
    reason: Optional[str]