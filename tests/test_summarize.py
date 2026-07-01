from src.transcriptor_tracker.summarize import (
    TemplateLLMAdapter, GeminiLLMAdapter
)
from src.transcriptor_tracker.models import SummaryModel
from unittest.mock import patch, MagicMock
import json
import os


def test_template_llm_adapter_parsing():

    mock_transcript = """
    Контекст: Обсуждение архитектуры MVP и интеграции xAPI.
    Решение: Использовать паттерн Адаптер для слабой связности.
    Решение: Вынести Pydantic-модели в отдельный файл.
    Вопрос: Какой LRS-сервер использовать для тестов?
    Конфликт: Разногласия по поводу структуры папки logs.
    Задача: Написать Makefile @ol1xy [SMART]
    Задача: Проверить Pull Request напарника @fedor
    Задача: Написать документацию проекта [SMART]
    """

    adapter = TemplateLLMAdapter()

    summary = adapter.summarize(mock_transcript)

    assert isinstance(summary, SummaryModel)
    assert summary.context == "Обсуждение архитектуры MVP и интеграции xAPI."

    assert len(summary.decisions) == 2
    assert "Использовать паттерн Адаптер" in summary.decisions[0]

    expected_question = "Какой LRS-сервер использовать для тестов?"
    assert summary.open_questions[0] == expected_question

    expected_conflict = "Разногласия по поводу структуры папки logs."
    assert summary.conflicts[0] == expected_conflict

    assert len(summary.next_actions) == 3

    task_1 = summary.next_actions[0]
    assert task_1.task == "Написать Makefile"
    assert task_1.assignee == "ol1xy"
    assert task_1.is_smart is True

    task_2 = summary.next_actions[1]
    assert task_2.task == "Проверить Pull Request напарника"
    assert task_2.assignee == "fedor"
    assert task_2.is_smart is False

    task_3 = summary.next_actions[2]
    assert task_3.task == "Написать документацию проекта"
    assert task_3.assignee is None
    assert task_3.is_smart is True


@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_test_key_123"})
@patch("src.transcriptor_tracker.summarize.genai.GenerativeModel")
@patch("src.transcriptor_tracker.summarize.genai.configure")
def test_gemini_llm_adapter_parsing(mock_configure, mock_generative_model):
    fake_json_response = {
        "context": "Консультация с куратором",
        "decisions": ["Утвердить план"],
        "open_questions": ["Как писать тесты?"],
        "conflicts": ["В ТЗ указана БД, а куратор сказал делать без БД"],
        "next_actions": [
            {
                "task": "Написать адаптер",
                "assignee": "Robert",
                "is_smart": True
            }
        ]
    }

    mock_model_instance = MagicMock()
    mock_generative_model.return_value = mock_model_instance

    mock_response = MagicMock()
    mock_response.text = json.dumps(fake_json_response)
    mock_model_instance.generate_content.return_value = mock_response

    adapter = GeminiLLMAdapter()
    summary = adapter.summarize(
        transcript="Привет, я куратор. Не используйте БД.",
        history="Проект требует интеграции БД SQLite."
    )

    assert isinstance(summary, SummaryModel)
    assert summary.context == "Консультация с куратором"
    assert "В ТЗ указана БД, "
    "а куратор сказал делать без БД" in summary.conflicts
    assert summary.next_actions[0].task == "Написать адаптер"

    mock_model_instance.generate_content.assert_called_once()
    call_kwargs = mock_model_instance.generate_content.call_args.kwargs
    assert call_kwargs["generation_config"]["response_mime_type"] == (
        "application/json"
    )
