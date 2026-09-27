import os

from fastapi import FastAPI
from dotenv import load_dotenv
from supabase import create_client, Client

# Load variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Task API - Assignment 4")


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