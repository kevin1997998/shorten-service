from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class URLBase(BaseModel):
    original_url: str


class URLInfo(BaseModel):
    short_url: str
    success: bool
    expiration_date: Optional[datetime]
    reason: Optional[str]
