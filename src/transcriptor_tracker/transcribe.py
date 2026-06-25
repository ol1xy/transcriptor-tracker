from abc import ABC, abstractmethod
from faster_whisper import WhisperModel

class BasicTranscriberAdapter(ABC):
    """
    Abstract class (interface) for speech recognition systems.
    It defines a unified rule for all future transcribers.
    """
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass


class WhisperLocalAdapter(BasicTranscriberAdapter):
    """
    Local transcription adapter based on faster_whisper module.
    """
    def __init__(self, model_size: str = "tiny"):
        self.model_size = model_size

    def transcribe(self, audio_path: str) -> str:
        model = WhisperModel(self.model_size, device = "cpu",
                             compute_type = "int8")
        
        segments, info = model.transcribe(audio_path, beam_size=5)

        text_segments = []
        for segment in segments:
            text_segments.append(segment.text)

        full_text = "".join(text_segments)

        return full_text.strip()