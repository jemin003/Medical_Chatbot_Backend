# main.py
from fastapi import FastAPI, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.metrics import accuracy_score
from auth import *
# Local imports
from config import *
from utils import *
from auth import router as auth_router
from ml_model import predict_diagnosis
from utils import accuracy_score as similarity_score
import logging
# from fastapi import UploadFile, File
import speech_recognition as sr
from io import BytesIO
import wave
from fastapi.responses import JSONResponse
from report_generator import generate_medical_report

# === App Initialization ===
app = FastAPI()

# === CORS Configuration ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Routers ===
app.include_router(auth_router)

# === Startup Log ===
print("🚀 Starting FastAPI backend at http://127.0.0.1:8000")

# === General Knowledge Blocking Keywords ===
GENERAL_KNOWLEDGE_TOPICS = [
    "newton", "physics", "math", "formula", "president", "country",
    "earth", "space", "galaxy", "ai", "machine learning"
]

# === Message Filtering ===
def is_general_knowledge_question(text: str) -> bool:
    return any(topic in text.lower() for topic in GENERAL_KNOWLEDGE_TOPICS)

def is_irrelevant_message(message: str) -> bool:
    banned = ["hello", "hi", "how are you", "what is your name", "who are you"]
    return any(phrase in message.lower() for phrase in banned)

def is_medical_input(user_input: str) -> bool:
    input_lower = user_input.lower()
    return (
        not any(sentence in input_lower for sentence in BANNED_SENTENCES) and
        not any(word in input_lower for word in BANNED_TOPICS) and
        any(keyword in input_lower for keyword in ALLOWED_KEYWORDS)
    )

def calculate_accuracy(predicted: str, actual: str) -> float:
    similarity = similarity_score(predicted, actual)
    # return round(accuracy_score(predicted, actual), 2)


# === Routes ===

@app.get("/")
def root():
    return {"message": "MediTrain API is running. Use /chat, /diagnosis, /report, and /extract."}

@app.get("/status")
def deployment_status():
    return {"message": "Render Deployment Active"}

class SymptomInput(BaseModel):
    text: str

@app.post("/extract_symptoms")
def get_extracted_symptoms(symptom_input: SymptomInput):
    extracted = extract_symptoms_from_text(symptom_input.text)
    return {"symptoms": extracted}

class ChatRequest(BaseModel):
    case_id: str
    user_message: str

@app.post("/chat", tags=["LLM"])
async def chat_with_patient(data: ChatRequest):
    """
    Handles doctor-patient chat interaction using LLM.
    """
    case = load_case(data.case_id)
    if not case:
        return {"reply": "Case not found."}

    user_msg = data.user_message.strip()
    if user_msg in ["Could not understand audio", ""]:
        return {"reply": "Sorry, I couldn't hear you clearly. Could you please repeat that?"}
    
    if not user_msg:
        return {"reply": case.get("intro_message", "Hello doctor, I'm not feeling well.")}

    if is_general_knowledge_question(user_msg):
        return {"reply": "I'm not sure about that, Doctor. Can we talk about my health instead?"}

    prompt = generate_prompt(case, user_msg)
    try:
        reply = call_llm(prompt)
    except Exception as e:
        reply = "Sorry, I couldn't process that right now."
    return {"reply": reply}

class ChatInput(BaseModel):
    message: str
    age: int
    gender: str

@app.post("/chat_diagnose")
def chat_diagnose(input: ChatInput):
    symptoms = extract_symptoms_from_text(input.message)
    if not symptoms:
        return {"reply": "Sorry, I couldn't detect any medical symptoms. Can you describe your issues in more detail?"}

    diagnosis = predict_diagnosis(symptoms, input.age, input.gender)
    reply = (
        f"Based on your symptoms: {', '.join(symptoms)}, "
        f"you may be experiencing: **{diagnosis}**.\n\n"
        "This is a preliminary suggestion. Please consult a doctor for a professional diagnosis."
    )
    return {"reply": reply, "diagnosis": diagnosis, "symptoms": symptoms}

class DiagnosisRequest(BaseModel):
    case_id: str
    diagnosis: str
    treatment: str
    conversation: str

@app.post("/diagnosis", tags=["Evaluation"])
async def submit_diagnosis(data: DiagnosisRequest):
    case = load_case(data.case_id)
    if not case:
        return {"error": "Case not found."}

    report = generate_report(case, data.conversation, data.diagnosis, data.treatment)
    return report

class ReportInput(BaseModel):
    name: str
    age: int
    gender: str
    symptoms: list[str]
    diagnosis: str
    duration: str = "unknown"

@app.post("/generate_report")
def create_report(input: ReportInput):
    report = generate_diagnosis_report(
        input.name, input.age, input.gender,
        input.symptoms, input.diagnosis, input.duration
    )
    return {"report": report}

class ExtractRequest(BaseModel):
    conversation: str

@app.post("/extract")
def extract_diagnosis_treatment(data: ExtractRequest):
    prompt = (
        f"From the following conversation, extract diagnosis and treatment:\n"
        f"{data.conversation}\n\nFormat:\nDiagnosis: <...>\nTreatment: <...>"
    )
    llm_response = call_llm(prompt)
    diagnosis, treatment = extract_diagnosis_and_treatment(llm_response)
    return {"diagnosis": diagnosis, "treatment": treatment}

class DiagnosisInput(BaseModel):
    age: int
    gender: str
    symptoms: list[str]

@app.post("/predict_diagnosis", tags=["ML"])
def get_prediction(input: DiagnosisInput):
    diagnosis = predict_diagnosis(input.symptoms, input.age, input.gender)
    return {"diagnosis": diagnosis}

@app.get("/get_sessions", tags=["Chat History"])
def get_sessions(email: str = Query(...)):
    sessions = chat_collection.find({"email": email})
    return [
        {
            "session_id": str(session["_id"]),
            "case_id": session["case_id"],
            "timestamp": session["timestamp"],
            "preview": session["messages"][-1]["content"][:50] + "..."
        }
        for session in sessions
    ]

@app.get("/docs-redirect", include_in_schema=False)
def redirect_docs():
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/docs")



@app.post("/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...)):
    audio_data = await audio_file.read()
    print(audio_data[:50])  # Print first 100 bytes for debugging
    # logging.info(f"Received audio file: {audio_file.filename}, size: {len(audio_data)} bytes")
    recognizer = sr.Recognizer()
    print("Initializing speech recognition...")
    print(recognizer)
    try:
        print("Converting audio to text...")
        # Convert bytes to wav file in memory
        with BytesIO(audio_data) as wav_buffer:
            # with wave.open(wav_buffer, 'rb') as wav_file:
            with sr.AudioFile(wav_buffer) as source:
                audio = recognizer.record(source)
                print("Audio recorded successfully.", audio)
                text = recognizer.recognize_google(audio)
                print("Speech recognition completed.", text)
        return {"text": text}
    except sr.UnknownValueError:
        return {"text": "Could not understand audio"}
    except Exception as e:
        return {"text": f"Error: {e}"}


#

@app.get("/cases")
def get_cases():
    try:
        files = os.listdir("cases")  # path relative to main.py
        cases_list = []
        for f in files:
            if f.endswith(".json"):
                with open(os.path.join("cases", f), "r") as file:
                    case_data = json.load(file)
                    cases_list.append({
                        "id": f.replace(".json", ""),
                        "title": case_data.get("title", "Untitled Case")
                    })
        return JSONResponse(content=cases_list)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/generate_report")
def generate_report_endpoint(
    session_id: str = Form(...),
    patient_name: str = Form(...),
    symptoms: str = Form(...),  # comma-separated
    diagnosis: str = Form(...),
    treatment: str = Form(...),
    remarks: str = Form(...)
):
    file_path = generate_medical_report(
        session_id,
        patient_name,
        symptoms.split(","),
        diagnosis,
        treatment,
        remarks
    )
    return {"status": "success", "file_path": file_path}


@app.post("/doctor-chat")
async def doctor_chat(input: dict):
    user_msg = input.get("message", "")
    reply = call_llm(user_msg)  # Use Gemini/GPT/OpenAI/Gemini API
    return {"reply": reply}
