from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import os
import uuid
import tempfile

from services.nlp_service import extract_features_from_text
from services.decision_engine import generate_decision
from services.whisper_service import transcribe_audio

app = FastAPI(title="Field Sales AI MVP", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

def load_model_safe(path):
    if not os.path.exists(path):
        raise RuntimeError(
            f"Model file not found: {path}\n"
            f"Please run ml_training/train_closure.py and ml_training/train_strategy.py first."
        )
    return joblib.load(path)

try:
    closure_model = load_model_safe(os.path.join(MODEL_DIR, "closure_model.pkl"))
    closure_scaler = load_model_safe(os.path.join(MODEL_DIR, "closure_scaler.pkl"))
    strategy_model = load_model_safe(os.path.join(MODEL_DIR, "strategy_model.pkl"))
    strategy_scaler = load_model_safe(os.path.join(MODEL_DIR, "strategy_scaler.pkl"))
    print("[Startup] ✅ All models loaded successfully.")
except RuntimeError as e:
    print(f"[Startup] ❌ {e}")
    closure_model = closure_scaler = strategy_model = strategy_scaler = None

FEATURE_ORDER = [
    "sentiment_score",
    "objection_price",
    "objection_competitor",
    "objection_no_need",
    "discount_requested_percent",
    "trial_requested_units",
    "engagement_level",
    "doctor_experience_years",
    "hospital_type",
    "previous_orders",
    "meeting_duration_minutes",
    "followup_delay_days"
]

def run_pipeline(features_dict: dict) -> dict:
    if closure_model is None:
        raise HTTPException(
            status_code=503,
            detail="ML models not loaded. Run training scripts first."
        )

    feature_vector = np.array([[features_dict[col] for col in FEATURE_ORDER]])

    closure_scaled = closure_scaler.transform(feature_vector)
    closure_prob = float(closure_model.predict_proba(closure_scaled)[0][1])
    closure_prediction = int(closure_prob > 0.5)

    strategy_scaled = strategy_scaler.transform(feature_vector)
    strategy_prediction = int(strategy_model.predict(strategy_scaled)[0])

    decision_output = generate_decision(features_dict, closure_prob, strategy_prediction)

    return {
        "extracted_features": features_dict,
        "closure_probability": round(closure_prob, 3),
        "predicted_closure": closure_prediction,
        "recommended_strategy": decision_output["recommended_strategy_text"],
        "decision_summary": decision_output["decision_summary"],
        "risk_level": decision_output["risk_level"]
    }

@app.get("/")
def root():
    models_ready = closure_model is not None
    return {
        "message": "Field Sales AI Backend Running",
        "status": "ready" if models_ready else "models_not_loaded",
        "endpoints": ["/analyze-meeting", "/analyze-voice", "/health"]
    }

@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": closure_model is not None}

class MeetingInput(BaseModel):
    text: str

@app.post("/analyze-meeting")
def analyze_meeting(data: MeetingInput):
    if not data.text or not data.text.strip():
        raise HTTPException(status_code=400, detail="Meeting text cannot be empty.")

    features_dict = extract_features_from_text(data.text)
    result = run_pipeline(features_dict)
    result["transcript"] = data.text
    return result

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}

@app.post("/analyze-voice")
async def analyze_voice(file: UploadFile = File(...)):

    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )

    temp_file_path = os.path.join(
        tempfile.gettempdir(),
        f"sales_audio_{uuid.uuid4().hex}{ext}"
    )

    try:
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        transcript = transcribe_audio(temp_file_path)

        if not transcript or not transcript.strip():
            raise HTTPException(status_code=422, detail="Could not transcribe audio. Please check the recording.")

        features_dict = extract_features_from_text(transcript)

        result = run_pipeline(features_dict)
        result["transcript"] = transcript
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)