from datetime import datetime

from pydantic import BaseModel


class RecordModel(BaseModel):
    currency: str
    amount: float
    total_amount: float
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    is_vidano: bool = False
    vidano_time: str = None  # 2025 01 13 16:06:30

    is_visible: bool = True
    is_needed: bool = False
