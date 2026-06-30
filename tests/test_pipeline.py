import os
from unittest.mock import MagicMock
from src.transcriptor_tracker.pipeline import PipelineEngine
from src.transcriptor_tracker.summarize import TemplateLLMAdapter
from src.transcriptor_tracker.publish import MockTrackerAdapter
from src.transcriptor_tracker.events import EvidenceBuilder


def test_pipeline_engine_full_run(tmp_path):
    mock_transcriber = MagicMock()
    mock_transcriber.transcribe.return_value = """
    Контекст: Обсуждение интеграции.
    Решение: Объединить модули через PipelineEngine.
    Задача: Написать автотесты @ol1xy [SMART]
    """

    summarizer = TemplateLLMAdapter()
    
    test_base_dir = str(tmp_path / "published")
    tracker = MockTrackerAdapter(base_dir=test_base_dir)
    
    evidence_builder = EvidenceBuilder()

    engine = PipelineEngine(
        transcriber=mock_transcriber,
        summarizer=summarizer,
        tracker=tracker,
        evidence_builder=evidence_builder
    )

    result = engine.run(
        audio_path="fake_audio.mp3",
        job_id="job_test_101",
        actor_name="Ivan Ivanov",
        actor_email="ivan@edu.ru"
    )

    assert os.path.exists(result["markdown_path"])
    assert os.path.exists(result["xapi_path"])

    event = result["xapi_event"]
    assert event["actor"]["name"] == "Ivan Ivanov"
    assert event["verb"]["display"]["ru-RU"] == "опубликовал"
    
    ext_key = "https://example.edu/xapi/extensions/detected-patterns"
    assert "smart-task-definition" in event["result"]["extensions"][ext_key]