from fastapi import FastAPI, Depends, HTTPException, Path, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine, get_db
from models import Base
from utils import verify_jwt_token, validate_book, security
from starlette.middleware.cors import CORSMiddleware

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LibraryPal Lending Book Service",
    description="API for managing books in the LibraryPal application.",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healthcheck (no auth needed)
@app.get("/health", tags=["Health"])
def healthcheck():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except SQLAlchemyError as e:
        return {"status": "error", "db": "unreachable", "detail": str(e)}
    finally:
        db.close()

# Get all loans
@app.get("/loans", response_model=list[schemas.Loan], tags=["Loans"])
def get_all_loans(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    verify_jwt_token(credentials)
    loans = crud.get_all_loans(db=db, skip=skip, limit=limit)
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found.")
    return loans

# Get a specific loan by ID
@app.get("/loans/{loan_id}", response_model=schemas.Loan, tags=["Loans"])
def get_loan_by_id(
    loan_id: int = Path(..., title="The ID of the loan to retrieve"),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    verify_jwt_token(credentials)
    loan = crud.get_loan_by_id(db=db, loan_id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found.")
    return loan

# Create a new loan
@app.post("/loans/", response_model=schemas.Loan, tags=["Loans"])
def create_loan(
    loan: schemas.LoanCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    verify_jwt_token(credentials)
    validate_book(loan.book_id)
    return crud.create_loan(db=db, loan=loan)

# Get loans by user
@app.get("/loans/user/{user_id}", response_model=list[schemas.Loan], tags=["Loans"])
def get_loans_by_user(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    verify_jwt_token(credentials)
    loans = crud.get_loans_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found for this user.")
    return loans

# Get loans by book
@app.get("/loans/book/{book_id}", response_model=list[schemas.Loan], tags=["Loans"])
def get_loans_by_book(
    book_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    verify_jwt_token(credentials)
    validate_book(book_id)
    loans = crud.get_loans_by_book(db=db, book_id=book_id, skip=skip, limit=limit)
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found for this book.")
    return loans

# Update loan status
@app.put("/loans/{loan_id}/status/{status}", response_model=schemas.Loan, tags=["Loans"])
def update_loan_status(
    loan_id: int,
    status: schemas.LoanStatus,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    verify_jwt_token(credentials)
    headers = {
        "Authorization": f"{credentials.scheme} {credentials.credentials}"
    }
    loan = crud.update_loan_status(db=db, loan_id=loan_id, status=status, headers=headers)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found.")
    return loan
