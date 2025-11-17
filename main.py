import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Contactmessage

app = FastAPI(title="Portfolio Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Portfolio API running"}

# Contact endpoint - stores messages in MongoDB
class ContactIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    subject: str = Field(..., min_length=3, max_length=120)
    message: str = Field(..., min_length=10, max_length=2000)

@app.post("/api/contact")
def submit_contact(payload: ContactIn):
    try:
        inserted_id = create_document("contactmessage", payload)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects")
def list_projects() -> List[dict]:
    """
    Simple static list of projects for now. You can later move this to DB if needed.
    """
    projects = [
        {
            "id": "p1",
            "title": "Smart Attendance System",
            "tech": ["Python", "OpenCV", "FastAPI"],
            "description": "Face-recognition based attendance for classrooms.",
            "link": "#"
        },
        {
            "id": "p2",
            "title": "Campus Navigator App",
            "tech": ["React Native", "Maps API"],
            "description": "Turn-by-turn navigation across campus buildings.",
            "link": "#"
        },
        {
            "id": "p3",
            "title": "Placement Tracker",
            "tech": ["MongoDB", "React", "Express"],
            "description": "Track job applications, interviews and offers.",
            "link": "#"
        }
    ]
    return projects

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
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
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
