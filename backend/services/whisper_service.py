import whisper

_model = None

def get_model():
    global _model
    if _model is None:
        print("[Whisper] Loading model... (first use only)")
        _model = whisper.load_model("base")
        print("[Whisper] Model loaded.")
    return _model

def transcribe_audio(file_path: str) -> str:
    model = get_model()
    result = model.transcribe(file_path)
    return result["text"]