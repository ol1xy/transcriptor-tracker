import os
from unittest.mock import MagicMock
from src.transcriptor_tracker.pipeline import PipelineEngine
from src.transcriptor_tracker.summarize import TemplateLLMAdapter
from src.transcriptor_tracker.publish import MockTrackerAdapter
from src.transcriptor_tracker.events import EvidenceBuilder
from src.transcriptor_tracker.models import SummaryModel
from src.transcriptor_tracker.knowledge_base import LocalKnowledgeBase
import pytest


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

    mock_kb = MagicMock()
    mock_kb.load_history.return_value = "Базовая история проекта ТЗ"

    engine = PipelineEngine(
        transcriber=mock_transcriber,
        summarizer=summarizer,
        tracker=tracker,
        evidence_builder=evidence_builder,
        knowledge_base=mock_kb
    )

    result = engine.run(
        audio_path="data/examples/sample-meeting.mp3",
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


def test_pipeline_engine_step_by_step(tmp_path):

    mock_transcriber = MagicMock()
    mock_transcriber.transcribe.return_value = "Контекст: Интеграция."

    summarizer = TemplateLLMAdapter()

    test_base_dir = str(tmp_path / "published_steps")
    tracker = MockTrackerAdapter(base_dir=test_base_dir)

    evidence_builder = EvidenceBuilder()

    mock_kb = MagicMock()
    mock_kb.load_history.return_value = "Базовая история проекта ТЗ"

    engine = PipelineEngine(
        transcriber=mock_transcriber,
        summarizer=summarizer,
        tracker=tracker,
        evidence_builder=evidence_builder,
        knowledge_base=mock_kb
    )

    summary = engine.analyze_audio("data/examples/sample-meeting.mp3")

    assert isinstance(summary, SummaryModel)
    assert summary.context == "Интеграция."

    result = engine.publish_summary(
        summary_model=summary,
        job_id="job_test_102",
        actor_name="Ivan Ivanov",
        actor_email="ivan@edu.ru"
    )

    assert os.path.exists(result["markdown_path"])
    assert os.path.exists(result["xapi_path"])

    event = result["xapi_event"]
    assert event["actor"]["name"] == "Ivan Ivanov"
    assert event["verb"]["display"]["ru-RU"] == "опубликовал"


def test_pipeline_engine_file_not_found(tmp_path):

    mock_kb = MagicMock()
    mock_kb.load_history.return_value = "Базовая история проекта ТЗ"

    engine = PipelineEngine(
        transcriber=MagicMock(),
        summarizer=MagicMock(),
        tracker=MagicMock(),
        evidence_builder=MagicMock(),
        knowledge_base=mock_kb
    )

    with pytest.raises(FileNotFoundError) as exc_info:
        engine.analyze_audio("non_existent_file.mp3")

    assert "Аудиофайл не найден по указанному пути" in str(exc_info.value)
