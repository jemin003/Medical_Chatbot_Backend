# utils.py

# Standard libraries
import os
import re
import json
import string
import unicodedata
from difflib import SequenceMatcher
from typing import Optional, Dict, Tuple

import spacy
# Third-party
import google.generativeai as genai
from dotenv import load_dotenv
# from langdetect import detect, DetectorFactory  # Optional if multilingual

# Local imports
from config import ALLOWED_KEYWORDS, BANNED_TOPICS
import logging

logging.basicConfig(level=logging.INFO)

# Normalize text
def normalize_text(text: str) -> str:
    """
    Normalize text by:
    - Lowercasing
    - Removing punctuation
    - Removing extra whitespace
    - Removing diacritics (accents)
    """
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Optional: Language detection setup
# DetectorFactory.seed = 0
# def detect_language(text: str) -> str:
#     try:
#         return detect(text)
#     except:
#         return "unknown"

# Load environment and configure Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# Load case from file
def load_case(case_id: str) -> Optional[Dict]:
    path = f"cases/{case_id}.json"
    if not os.path.exists(path):
        logging.warning(f"[CASE NOT FOUND] {path}")
        return None
    with open(path, "r") as f:
        return json.load(f)

# Prompt generator for virtual patient
def generate_prompt(case, user_input: str) -> str:
    p = case["patient_profile"]
    symptoms = ', '.join(case['symptoms'])
    med_hist = ', '.join(case['additional_info']['medical_history'])
    fam_hist = ', '.join(case['additional_info']['family_history'])

    template = f"""
You are a virtual patient named {p['name']}, age {p['age']}, gender {p['gender']}.
You are speaking to a doctor during a consultation. Your main complaint is: {p['chief_complaint']}.
Your symptoms include: {symptoms}.
Medical History: {med_hist}
Family History: {fam_hist}

INSTRUCTIONS:
- Always respond **as the patient**, not as an AI or assistant.
- Only answer **medical or personal health-related** questions, including:
  - Your pain, symptoms, medical/family history, or recent changes.
  - Basic identity and emotional state (name, tell me, how you’re feeling, etc.).
- **Do NOT** answer questions about science, math, geography, or anything unrelated to your condition.
  - For those, politely deflect and redirect the conversation to your health.
- Doctor may use multiple languages for input. You must understand and respond accordingly as a **virtual patient**.
- Maintain a natural, emotional, and human tone.

Doctor: {user_input}
""".strip()
    return template

# Filter out invalid or irrelevant user messages
def is_allowed_message(message: str) -> bool:
    normalized = normalize_text(message)
    for banned in BANNED_TOPICS:
        if re.search(rf'\b{re.escape(banned)}\b', normalized):
            return False
    for keyword in ALLOWED_KEYWORDS:
        if re.search(rf'\b{re.escape(keyword)}\b', normalized):
            return True
    return False

# Call the Gemini model with generated prompt
def call_llm(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.warning(f"[LLM ERROR] {e}")
        return "⚠️ Sorry, something went wrong while generating the response."

# Accuracy calculation for diagnosis/treatment match
def accuracy_score(user_text: str, correct_text: str) -> float:
    user_text = normalize_text(user_text)
    correct_text = normalize_text(correct_text)
    return SequenceMatcher(None, user_text, correct_text).ratio() * 100

# Report generation
def generate_report(case: dict, conversation: list, diagnosis: str, treatment: str) -> dict:
    correct_diagnosis = case['correct_diagnosis'].lower()
    correct_treatment = case['recommended_treatment'].lower()
    diag_accuracy = accuracy_score(diagnosis.lower(), correct_diagnosis)
    treat_accuracy = accuracy_score(treatment.lower(), correct_treatment)

    return {
        "report": f'''
🧾 Report:
Patient described {case["patient_profile"]["chief_complaint"]}.
Diagnosis: {diagnosis}
Treatment: {treatment}

✅ Diagnosis Accuracy: {diag_accuracy:.2f}%
💊 Treatment Accuracy: {treat_accuracy:.2f}%
'''.strip(),
        "accuracy": {
            "diagnosis": diag_accuracy,
            "treatment": treat_accuracy
        }
    }

# Extract diagnosis and treatment lines from raw text
def extract_diagnosis_and_treatment(text: str) -> Tuple[str, str]:
    diagnosis_match = re.search(r'diagnosis[:\-]\s*(.+)', text, re.IGNORECASE)
    treatment_match = re.search(r'treatment[:\-]\s*(.+)', text, re.IGNORECASE)

    diagnosis = diagnosis_match.group(1).strip() if diagnosis_match else ""
    treatment = treatment_match.group(1).strip() if treatment_match else ""

    return diagnosis, treatment


# llm_utils.py

def generate_diagnosis_report(name, age, gender, symptoms, diagnosis, duration="unknown"):
    prompt = f"""
    Patient Name: {name}
    Age: {age}
    Gender: {gender}
    Symptom Duration: {duration}
    Symptoms: {', '.join(symptoms)}
    Predicted Diagnosis: {diagnosis}

    Based on the above information, write a detailed, medically accurate diagnosis report including:
    - Summary of the patient's condition
    - Explanation of the likely diagnosis
    - General treatment suggestions
    - A professional tone
    """

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Error generating report: {str(e)}"

# nlp_utils.py

# Attempt to load SpaCy model with fallback installer
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Clinical symptom keywords (canonical names)
SYMPTOM_KEYWORDS = [
    "fever", "cough", "headache", "fatigue", "nausea",
    "vomiting", "diarrhea", "pain", "sore throat",
    "chills", "shortness of breath", "dizziness",
    "rash", "itching", "abdominal pain", "blurred vision"
]

# Synonyms or common variations mapped to canonical symptom keywords
SYMPTOM_SYNONYMS = {
    "tired": "fatigue",
    "exhausted": "fatigue",
    "sick": "nausea",
    "queasy": "nausea",
    "throwing up": "vomiting",
    "upset stomach": "abdominal pain",
    "belly pain": "abdominal pain",
    "breathless": "shortness of breath",
    "dizzy": "dizziness",
    "lightheaded": "dizziness",
    "blurred sight": "blurred vision",
    "itchy": "itching",
    "sore throat": "sore throat"
}

def extract_symptoms_from_text(user_input):
    raw_text = user_input.lower()
    doc = nlp(raw_text)
    lemmatized_text = " ".join([token.lemma_ for token in doc])
    symptoms_found = set()

    # Check canonical symptom keywords in lemmatized and raw text
    for symptom in SYMPTOM_KEYWORDS:
        if symptom in lemmatized_text or symptom in raw_text:
            symptoms_found.add(symptom)

    # Check for synonyms in both raw and lemmatized forms
    for synonym, mapped_symptom in SYMPTOM_SYNONYMS.items():
        if (synonym in raw_text or synonym in lemmatized_text) and mapped_symptom in SYMPTOM_KEYWORDS:
            symptoms_found.add(mapped_symptom)

    return list(symptoms_found)

print("✅ NLP utils loaded")


