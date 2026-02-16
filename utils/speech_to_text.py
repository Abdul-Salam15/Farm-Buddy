import tempfile
import numpy as np
import soundfile as sf
import whisper

# Load once
model = whisper.load_model("base")

def transcribe_audio(audio: np.ndarray, sample_rate: int = 48000) -> str:
    """
    audio: 1D numpy float array
    """
    if audio is None or audio.size == 0:
        return ""

    # Whisper expects float32
    audio = audio.astype("float32")

    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        sf.write(f.name, audio, sample_rate)
        result = model.transcribe(f.name)

    return result.get("text", "").strip()
