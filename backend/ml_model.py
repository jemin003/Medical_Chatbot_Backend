
import os
import json
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Define base directory and file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CASE_FOLDER = os.path.join(BASE_DIR, "cases")
MODEL_PATH = os.path.join(BASE_DIR, "diagnosis_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "symptom_encoder.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "model_metrics.json")

# Load all cases from the folder
def load_case_data():
    data = []
    for file in os.listdir(CASE_FOLDER):
        if file.endswith(".json"):
            with open(os.path.join(CASE_FOLDER, file), "r") as f:
                case = json.load(f)

                patient = case.get("patient_profile", {})
                age = patient.get("age")
                gender = patient.get("gender")
                symptoms = case.get("symptoms", [])
                diagnosis = case.get("correct_diagnosis")

                if age is not None and gender is not None and diagnosis is not None:
                    data.append({
                        "age": age,
                        "gender": gender,
                        "symptoms": symptoms,
                        "diagnosis": diagnosis
                    })
    return pd.DataFrame(data)

# Preprocess the data for ML model
def preprocess_data(df):
    df["gender"] = df["gender"].map({"male": 0, "female": 1})
    df = df.dropna(subset=["gender"])

    mlb = MultiLabelBinarizer()
    symptoms_encoded = mlb.fit_transform(df["symptoms"])
    symptoms_df = pd.DataFrame(symptoms_encoded, columns=mlb.classes_)

    X = pd.concat([df[["age", "gender"]].reset_index(drop=True), symptoms_df], axis=1)
    y = df["diagnosis"]

    return X, y, mlb

# Train and save the model and encoder
def train_model():
    df = load_case_data()
    if df.empty:
        print("❌ No valid case data found.")
        return

    X, y, mlb = preprocess_data(df)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    with open(METRICS_PATH, "w") as f:
        json.dump(report, f, indent=2)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(mlb, ENCODER_PATH)
    print("✅ Model trained and saved successfully. Metrics saved to model_metrics.json.")

# Predict diagnosis from new input
def predict_diagnosis(symptoms, age, gender):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError("Model or encoder file not found. Train the model first.")

    model = joblib.load(MODEL_PATH)
    mlb = joblib.load(ENCODER_PATH)

    if gender.lower() not in ["male", "female"]:
        raise ValueError("Gender must be 'male' or 'female'")

    gender_val = 0 if gender.lower() == "male" else 1

    known_symptoms = set(mlb.classes_)
    filtered_symptoms = [s for s in symptoms if s in known_symptoms]
    if not filtered_symptoms:
        raise ValueError("❌ None of the symptoms are recognized from the training data.")

    symptoms_vector = mlb.transform([filtered_symptoms])

    input_df = pd.DataFrame(
        [[age, gender_val] + list(symptoms_vector[0])],
        columns=["age", "gender"] + list(mlb.classes_)
    )

    return model.predict(input_df)[0]
