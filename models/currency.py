from pydantic import BaseModel


class CurrencyModel(BaseModel):
    currency: str
    price: float
