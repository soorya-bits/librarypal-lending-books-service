from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# Enum for Loan Status
class LoanStatus(enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    RETURNED = "Returned"
    DENIED = "Denied"

class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Assuming user_id comes from external user service
    book_id = Column(Integer, nullable=False)  # Assuming book_id comes from external book service
    loan_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)

    # We do not need relationships here since these are external services
