from pydantic import BaseModel
from datetime import date
from uuid import UUID
from datetime import datetime

class CustomerCreate(BaseModel):
    name: str
    phone: str | None = None


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    phone: str | None
    created_at: datetime

    class Config:
        from_attributes = True #Important(Pydantic v2)


class CustomerLogin(BaseModel):
    mobile: str