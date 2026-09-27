import os

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client


# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Bearer authentication for Swagger
security = HTTPBearer()

# Create FastAPI application
app = FastAPI(title="Task API - Assignment 4")


# Request model for authentication
class AuthRequest(BaseModel):
    email: str
    password: str


# Reusable authentication dependency
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Reusable authentication dependency.

    It:
    1. Gets the Bearer token from the Authorization header.
    2. Extracts the access token.
    3. Verifies the token with Supabase.
    4. Returns the authenticated user.
    """

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)

        if response.user is None:
            raise Exception("User not found")

        return response.user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# Root endpoint
@app.get("/")
def root():
    return {"message": "Task API with Supabase Auth"}


# Health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}


# Signup endpoint
@app.post("/auth/signup", status_code=201)
def signup(request: AuthRequest):

    if not request.email.strip() or not request.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })

        if response.user is None:
            raise HTTPException(
                status_code=400,
                detail="Signup failed"
            )

        return {
            "id": response.user.id,
            "email": response.user.email
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# Login endpoint
@app.post("/auth/login")
def login(request: AuthRequest):

    if not request.email.strip() or not request.password.strip():
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )


# Logout endpoint
@app.post("/auth/logout", status_code=204)
def logout(user=Depends(get_current_user)):

    try:
        supabase.auth.sign_out()

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Logout failed"
        )

    return None


# Public endpoint
@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


# Protected profile endpoint
@app.get("/protected/profile")
def protected_profile(user=Depends(get_current_user)):

    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }


# Second protected endpoint
@app.get("/protected/dashboard")
def protected_dashboard(user=Depends(get_current_user)):

    return {
        "message": "Welcome to your protected dashboard!",
        "user_id": user.id
    }