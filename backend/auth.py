from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field, EmailStr, constr
from passlib.context import CryptContext
from pymongo import MongoClient, DESCENDING
from datetime import datetime, timedelta
from bson import ObjectId
import uuid
import config
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

client = MongoClient("mongodb://localhost:27017/")
db = client["meditrain"]
users_collection = db["users"]
chat_collection = db["chat_history"]
sessions_collection = db["chat_sessions"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    username: str
    email: str
    password: str

class LoginData(BaseModel):
    email: str
    password: str

class ChatMessage(BaseModel):
    email: str
    case_id: str
    session_id: str
    role: str  # "user" or "bot"
    message: str

class CreateSession(BaseModel):
    email: str
    case_id: str
    session_name: str

class UpdateSessionName(BaseModel):
    email: str
    session_id: str
    new_name: str

# === Pydantic Models ===
class ChatRequest(BaseModel):
    user_message: str
    case_id: str

class DiagnosisRequest(BaseModel):
    conversation: str
    diagnosis: str
    treatment: str
    case_id: str

class ExtractRequest(BaseModel):
    conversation: str
    case_id: str

class SymptomInput(BaseModel):
    text: str
    
# class EditMessage(BaseModel):
#     message_id: str
#     new_message: str

@router.post("/register")
def register(user: User):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        hashed_pwd = pwd_context.hash(user.password)
        users_collection.insert_one({
            "username": user.username,
            "email": user.email,
            "password": hashed_pwd
        })
    except Exception as e:
        logger.exception("Registration error")
        raise HTTPException(status_code=500, detail="Registration failed")
    return {"message": "User registered successfully"}

@router.post("/login")
def login(data: LoginData):
    user = users_collection.find_one({"email": data.email})
    if not user or not pwd_context.verify(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "username": user["username"]}

@router.post("/create_session")
def create_session(data: CreateSession):
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "email": data.email,
        "case_id": data.case_id,
        "session_name": data.session_name,
        "created_at": datetime.utcnow()
    }
    try:
        sessions_collection.insert_one(session_data)
    except Exception as e:
        logger.exception("Error creating session")
        raise HTTPException(status_code=500, detail="Session creation failed")
    return {"status": "success", "session_id": session_id}

@router.get("/sessions")
def get_sessions(email: str, case_id: str = None):
    query = {"email": email}
    if case_id:
        query["case_id"] = case_id
    try:
        sessions = list(sessions_collection.find(query).sort("created_at", DESCENDING))
    except Exception as e:
        logger.exception("Error fetching sessions")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")
    for s in sessions:
        s["_id"] = str(s["_id"])
        s["created_at"] = s["created_at"].isoformat()
    return {"sessions": sessions}

@router.post("/store_chat")
def store_chat(data: ChatMessage):
    chat_collection.insert_one({
        "user_email": data.email,
        "case_id": data.case_id,
        "session_id": data.session_id,
        "role": data.role,
        "message": data.message,
        "timestamp": datetime.utcnow()
    })
    return {"status": "success"}
 # Adjust this import based on your structure


@router.get("/chat_history")
async def get_chat_history(email: str, case_id: str):
    """
    Return all chat sessions and chats for a given user and case_id.
    """
    try:
        chat_documents = chat_collection.find({
            "user_email": email,
            "session_id": case_id
        })
        print(chat_documents)

        session_chat_map = []
        for doc in chat_documents:
            print(doc)
            session_id = doc["session_id"]
            # if session_id not in session_chat_map:
            #     session_chat_map[session_id] = []
            session_chat_map.append({
                "role": doc["role"],
                "message": doc["message"],
                "timestamp": doc.get("timestamp", "")
            })

        return {"status": "success", "chat_history": session_chat_map}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_session")
def delete_session(email: str = Query(...), session_id: str = Query(...)):
    session_result = sessions_collection.delete_one({"email": email, "session_id": session_id})
    chat_result = chat_collection.delete_many({"user_email": email, "session_id": session_id})

    if session_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {
        "status": "success",
        "message": "Session and related chats deleted.",
        "chats_deleted": chat_result.deleted_count
    }

@router.put("/update_session")
def update_session_name(data: UpdateSessionName):
    result = sessions_collection.update_one(
        {"email": data.email, "session_id": data.session_id},
        {"$set": {"session_name": data.new_name}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"status": "success", "message": "Session name updated."}