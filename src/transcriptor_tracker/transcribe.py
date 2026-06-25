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

