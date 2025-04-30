import os
import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

security = HTTPBearer()

# Get the Auth service URL from environment variable
USER_AUTH_SERVICE_URL = os.getenv("USER_AUTH_SERVICE_URL", "http://localhost:8000")
BOOK_SERVICE_URL = os.getenv("BOOK_SERVICE_URL", "http://localhost:8001")

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = httpx.get(f"{USER_AUTH_SERVICE_URL}/verify-token", headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Invalid or expired token")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Auth service unavailable")

def validate_book(book_id: int):
    try:
        response = httpx.get(f"{BOOK_SERVICE_URL}/books/{book_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book = response.json()
        if int(book.get("avail_status", 0)) == 0:
            raise HTTPException(status_code=400, detail="Book is not available for lending")
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Error contacting Book Service: {e}")
    except (KeyError, ValueError):
        raise HTTPException(status_code=500, detail="Invalid book data received from Book Service")

def update_book_availability(book_id: int, delta: int, headers: dict):
    try:
        response = httpx.get(f"{BOOK_SERVICE_URL}/books/{book_id}", headers=headers)
        response.raise_for_status()
        book = response.json()

        current_status = int(book.get("avail_status", 0))
        new_status = current_status + delta

        updated_book = {
            "title": book["title"],
            "author": book["author"],
            "genre": book["genre"],
            "desc": book["desc"],
            "url": book["url"],
            "avail_status": str(new_status)
        }
        put_response = httpx.put(
            f"{BOOK_SERVICE_URL}/books/{book_id}",
            json=updated_book,
            headers=headers,
            timeout=5.0
        )
        put_response.raise_for_status()

    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Book Service unavailable: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to update book availability")
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Invalid book data format: {e}")
