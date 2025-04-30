from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy.exc import SQLAlchemyError
from utils import update_book_availability

# Create a loan
def create_loan(db: Session, loan: schemas.LoanCreate):
    db_loan = models.Loan(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

# Get all loans with pagination
def get_all_loans(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Loan).offset(skip).limit(limit).all()

# Get all loans by user_id
def get_loans_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Loan).filter(models.Loan.user_id == user_id).offset(skip).limit(limit).all()

# Get all loans for a book
def get_loans_by_book(db: Session, book_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Loan).filter(models.Loan.book_id == book_id).offset(skip).limit(limit).all()

# Get a specific loan
def get_loan_by_id(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

def update_loan_status(db: Session, loan_id: int, status: str, headers: dict):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not db_loan:
        return None
    previous_status = db_loan.status

    if previous_status != status:
        if status.upper() == "APPROVED":
            update_book_availability(db_loan.book_id, -1, headers)
        elif status.upper() == "RETURNED":
            update_book_availability(db_loan.book_id, 1, headers)

    db_loan.status = status
    db.commit()
    db.refresh(db_loan)


    return db_loan