import os

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client


# Load variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


app = FastAPI(title="Task API - Assignment 4")


# -------------------------
# Request models
# -------------------------

class AuthRequest(BaseModel):
    email: str
    password: str


# -------------------------
# Basic routes
# -------------------------

@app.get("/")
def root():
    return {
        "message": "Task API with Supabase Auth"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# -------------------------
# Authentication routes
# -------------------------

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


# -------------------------
# Public route
# -------------------------

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


# -------------------------
# Protected route
# -------------------------

@app.get("/protected/profile")
def protected_profile(authorization: str | None = Header(default=None)):

    # Check whether the Authorization header exists
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    # Check that the header uses Bearer format
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    # Extract the token from "Bearer <token>"
    token = authorization.replace("Bearer ", "", 1).strip()

    # Make sure a token was actually provided
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    # Verify the access token with Supabase
    try:
        response = supabase.auth.get_user(token)

        if response.user is None:
            raise Exception("User not found")

        user = response.user

        # Return only safe user information
        return {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )