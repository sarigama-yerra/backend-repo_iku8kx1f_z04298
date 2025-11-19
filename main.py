import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Destination, Itinerary, Subscriber, Message

app = FastAPI(title="Travel App API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Travel API running"}


# Health + DB test
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# ------------ Content Endpoints ------------
@app.get("/api/destinations", response_model=List[Destination])
def list_destinations(limit: int = 12):
    docs = get_documents("destination", {}, limit)
    # Ensure missing fields handled
    result: List[Destination] = []
    for d in docs:
        result.append(Destination(
            name=d.get("name", ""),
            country=d.get("country", ""),
            image=d.get("image"),
            tagline=d.get("tagline"),
        ))
    return result


@app.post("/api/subscribe")
def subscribe(sub: Subscriber):
    try:
        create_document("subscriber", sub)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/contact")
def contact(msg: Message):
    try:
        create_document("message", msg)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example Itinerary endpoints
class ItineraryCreate(BaseModel):
    name: str
    owner_email: str


@app.post("/api/itineraries")
def create_itinerary(payload: ItineraryCreate):
    try:
        itin = Itinerary(name=payload.name, owner_email=payload.owner_email, items=[])
        create_document("itinerary", itin)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/itineraries", response_model=List[Itinerary])
def list_itineraries(owner_email: Optional[str] = None, limit: int = 20):
    flt = {"owner_email": owner_email} if owner_email else {}
    docs = get_documents("itinerary", flt, limit)
    result: List[Itinerary] = []
    for d in docs:
        result.append(Itinerary(
            name=d.get("name", ""),
            owner_email=d.get("owner_email", ""),
            items=d.get("items", []),
        ))
    return result


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
