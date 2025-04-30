from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import enum

class LoanStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    RETURNED = "Returned"
    DENIED = "Denied"

# Loan schemas
class LoanBase(BaseModel):
    user_id: int
    book_id: int

class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: int
    loan_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus

    class Config:
        orm_mode = True
