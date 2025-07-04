# config.py

# ==== Allowed Medical and Training Keywords ====
ALLOWED_KEYWORDS = [
    "pain", "ache", "fever", "nausea", "vomit", "dizzy", "cold", "cough", "fatigue",
    "history", "health", "sick", "feeling", "stomach", "headache", "infection", "treatment","issue"
    "medicine", "doctor", "appointment", "surgery", "diagnosis", "pressure", "sleep", "diet","medical","health"
    "family", "medical", "symptom", "update", "checkup", "report", "name", "age", "how are you","tell me",
    # Greetings and polite phrases
    "hello", "hi", "hey", "good morning", "good evening", "how are you", "nice to meet you","yes", "no"

    # Medical education topics
    "case study", "clinical scenario", "osce", "mcq", "viva", "medical quiz",
    "differential diagnosis", "clinical reasoning", "explain", "define", "compare",
    "mnemonic", "signs and symptoms", "investigation", "management", "treatment plan",

    # Medical science topics
    "anatomy", "physiology", "biochemistry", "pharmacology", "pathology",
    "microbiology", "forensic medicine", "community medicine", "internal medicine",
    "surgery", "obstetrics", "gynecology", "pediatrics", "orthopedics", "radiology",
    "psychiatry", "dermatology", "ophthalmology", "ent",

    # Systems and specialties
    "cardiac", "respiratory", "gastrointestinal", "neurological", "endocrine",
    "musculoskeletal", "genitourinary", "hematologic", "immunologic",

    # Clinical skills
    "history taking", "examination", "inspection", "palpation", "percussion", "auscultation",
    "symptom", "sign", "finding", "presentation", "complaint", "progression", "duration",

    # Diagnostics
    "lab test", "x-ray", "mri", "ct scan", "ecg", "cbc", "thyroid", "liver function test",
    "urinalysis", "sputum", "biopsy", "ultrasound", "vital signs", "oxygen", "heart rate",
    "blood pressure", "temperature", "respiratory rate",

    # Treatment and procedures
    "treatment", "medication", "surgery", "dose", "route", "frequency", "care plan",
    "prescription", "follow-up", "referral", "therapy", "monitoring", "procedure", "complication",

    # Medical context and logic
    "how", "why", "what happens if", "is this correct", "rationale", "mechanism", "explanation",
    "clinical pearls", "key points", "exam question", "true or false", "clinical correlation"
]


# ==== Blocked/Banned Topics - Keywords ====
BANNED_TOPICS = [
    # Celebrities, entertainment, sports
    "virat kohli", "rohit sharma", "shahrukh khan", "salman khan", "modi", "biden", "trump",
    "putin", "rahul gandhi", "kejriwal", "cricket", "ipl", "football", "fifa", "match", "goal",
    "team", "score", "player", "movie", "film", "actor", "actress", "song", "music", "album",
    "singer", "youtube", "tiktok", "instagram", "facebook", "social media", "reels", "meme",

    # Romantic or personal
    r"\bwife\b", r"\bhusband\b", r"\bgirlfriend\b", r"\bboyfriend\b", r"\bcrush\b", r"\bflirt\b",
    r"\bdate\b", r"\bmarried\b", r"\bsingle\b", r"\blove\b", r"\bkiss\b", r"\bsexy\b", r"\bhot\b",
    r"\bcute\b", r"\bbeautiful\b", r"\bhandsome\b", r"\bpretty\b", r"\bare you single\b", r"\bdo you love me\b",

    # Religious or political
    "god", "allah", "jesus", "ram", "temple", "church", "mosque", "bible", "quran", "gita",
    "religion", "pray", "politics", "election", "vote", "party", "nato", "war", "israel",
    "gaza", "ukraine", "pakistan", "prime minister","Country","city","owner"

    # Irrelevant or distracting
    "joke", "tell me a joke", "funny", "magic", "superpower", "robot", "story", "riddle",
    "guess", "weather", "capital of", "country", "animal", "space", "moon", "sun", "zoo",
    "alien", "which country are you from", "what team do you support",

    "who is your favorite cricketer",
    "do you watch ipl",
    "do you like virat kohli",
    "what is your favorite movie",
    "tell me a joke",
    "do you love me",
    "are you single",
    "will you marry me",
    "you look beautiful",
    "how old are you",
    "what's your salary",
    "where do you live",
    "do you believe in god",
    "do you pray",
    "do you like music",
    "what's your favorite actor",
    "do you watch movies",
    "play a song",
    "tell me about modi",
    "what is the weather like",
    "are you a robot",
    "you are cute",
    "i love you",
    "will you be my girlfriend",
    "tell me a funny story",
    "do you use instagram",
    "show me memes",
    "do you play games",
    "what team do you support",
    "do you believe in aliens",
    "which country are you from",
    "can you dance",
    "will you go on a date with me",
    "can you be my friend",
    "you are hot",
    "you look sexy",
    "are you human",
    "what is your religion"
]


# ==== Blocked Phrases/Sentences ====
BANNED_SENTENCES = [
    "who is your favorite cricketer",
    "do you watch ipl",
    "do you like virat kohli",
    "what is your favorite movie",
    "tell me a joke",
    "do you love me",
    "are you single",
    "will you marry me",
    "you look beautiful",
    "how old are you",
    "what's your salary",
    "where do you live",
    "do you believe in god",
    "do you pray",
    "do you like music",
    "what's your favorite actor",
    "do you watch movies",
    "play a song",
    "tell me about modi",
    "what is the weather like",
    "are you a robot",
    "you are cute",
    "i love you",
    "will you be my girlfriend",
    "tell me a funny story",
    "do you use instagram",
    "show me memes",
    "do you play games",
    "what team do you support",
    "do you believe in aliens",
    "which country are you from",
    "can you dance",
    "will you go on a date with me",
    "can you be my friend",
    "you are hot",
    "you look sexy",
    "are you human",
    "what is your religion"
]
INTENTS = [
    "symptom_description",  # "I have a headache and fever"
    "diagnosis_request",    # "What could be causing this?"
    "treatment_advice",     # "What medication should I take?"
    "medical_history",      # "I have a family history of diabetes"
    "general_health",       # "How can I improve my sleep?"
    "irrelevant"           # Non-medical queries
]

# ==== Rejection Message ====
REJECTION_MESSAGE = (
    "⚠️ I'm here to assist with **medical education and training** only. "
    "Please focus on health-related discussions such as symptoms, diagnosis, clinical reasoning, or treatment planning."
)


