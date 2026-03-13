from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from supabase import create_client, Client
from datetime import date, datetime, timezone
from typing import Optional
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="President API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://zhangsgithub04.github.io"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("Missing SUPABASE_URL")

if not SUPABASE_KEY:
    raise RuntimeError("Missing SUPABASE_KEY")

if not SUPABASE_URL.startswith("https://") or "supabase.co" not in SUPABASE_URL:
    raise RuntimeError(f"Invalid SUPABASE_URL: {SUPABASE_URL}")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class PresidentCreate(BaseModel):
    firstname: str = Field(..., min_length=1, max_length=100)
    lastname: str = Field(..., min_length=1, max_length=100)
    birthdate: Optional[date] = None


class PresidentUpdate(BaseModel):
    firstname: Optional[str] = Field(None, min_length=1, max_length=100)
    lastname: Optional[str] = Field(None, min_length=1, max_length=100)
    birthdate: Optional[date] = None


@app.get("/")
async def root():
    response = supabase.table("president").select("*", count="exact").execute()
    return {
        "message": "President API is running",
        "president_count": response.count
    }


@app.get("/presidents")
async def list_presidents():
    response = (
        supabase
        .table("president")
        .select("*")
        .order("id")
        .execute()
    )
    return response.data


@app.get("/presidents/{president_id}")
async def get_president(president_id: int):
    response = (
        supabase
        .table("president")
        .select("*")
        .eq("id", president_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="President not found")

    return response.data[0]


@app.post("/presidents", status_code=201)
async def create_president(president: PresidentCreate):
    payload = {
        "firstname": president.firstname.strip(),
        "lastname": president.lastname.strip(),
        "birthdate": president.birthdate.isoformat() if president.birthdate else None,
        "updated_at": utc_now_iso()
    }

    response = supabase.table("president").insert(payload).execute()

    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create president")

    return response.data[0]


@app.patch("/presidents/{president_id}")
async def update_president(president_id: int, president: PresidentUpdate):
    update_data = president.model_dump(exclude_none=True)

    if "firstname" in update_data:
        update_data["firstname"] = update_data["firstname"].strip()

    if "lastname" in update_data:
        update_data["lastname"] = update_data["lastname"].strip()

    if "birthdate" in update_data and update_data["birthdate"] is not None:
        update_data["birthdate"] = update_data["birthdate"].isoformat()

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    update_data["updated_at"] = utc_now_iso()

    response = (
        supabase
        .table("president")
        .update(update_data)
        .eq("id", president_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="President not found")

    return response.data[0]


@app.put("/presidents/{president_id}")
async def replace_president(president_id: int, president: PresidentCreate):
    payload = {
        "firstname": president.firstname.strip(),
        "lastname": president.lastname.strip(),
        "birthdate": president.birthdate.isoformat() if president.birthdate else None,
        "updated_at": utc_now_iso()
    }

    response = (
        supabase
        .table("president")
        .update(payload)
        .eq("id", president_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="President not found")

    return response.data[0]


@app.delete("/presidents/{president_id}")
async def delete_president(president_id: int):
    response = (
        supabase
        .table("president")
        .delete()
        .eq("id", president_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="President not found")

    return {"message": "President deleted successfully"}
