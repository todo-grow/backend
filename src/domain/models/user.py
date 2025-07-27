from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    id: Optional[int] = None
    kakao_id: Optional[str] = None
    email: Optional[str] = None
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None