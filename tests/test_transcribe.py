from unittest.mock import MagicMock, patch
import pytest
from src.transcriptor_tracker.transcribe import WhisperLocalAdapter


@patch("src.transcriptor_tracker.transcribe.WhisperModel")
def test_whisper_local_adapter_success(mock_whisper_model):

    mock_model_instance = MagicMock()
    mock_whisper_model.return_value = mock_model_instance

    mock_segment = MagicMock()
    mock_segment.text = "Привет, это тестовый транскрипт"

    mock_model_instance.transcribe.return_value = ([mock_segment], None)

    adapter = WhisperLocalAdapter(model_size="tiny")
    result = adapter.transcribe("data/examples/sample_meeting.mp3")

    assert result == "Привет, это тестовый транскрипт"

    mock_whisper_model.assert_called_once_with("tiny", device = "cpu",
                                               compute_type = "int8")
    
    mock_model_instance.transcribe.assert_called_once_with("data/examples/sample_meeting.mp3",
                                                           beam_size = 5)