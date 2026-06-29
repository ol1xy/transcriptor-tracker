from src.transcriptor_tracker.summarize import TemplateLLMAdapter
from src.transcriptor_tracker.models import SummaryModel


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
