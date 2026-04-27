import soundfile as sf
from chord_extractor.extractors import Chordino


def extract_chords(audio_path: str) -> dict:
    chordino = Chordino(roll_on=1)
    raw = chordino.extract(audio_path)

    duration = float(sf.info(audio_path).duration)

    return {
        "duration": duration,
        "chords": [
            {"chord": c.chord, "timestamp": float(c.timestamp)}
            for c in raw
        ],
    }
