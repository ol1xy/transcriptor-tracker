import re
from abc import ABC, abstractmethod
from src.transcriptor_tracker.models import SummaryModel, ActionItem
import google.generativeai as genai
from src.transcriptor_tracker.prompts import CONTRADICTION_PROMPT_TEMPLATE
import os


class BaseLLMAdapter(ABC):
    """
    Interface for work with LLM.
    Defines a strict contract: transcript text as input,
    SummaryModel as output.
    """
    @abstractmethod
    def summarize(
        self, transcript: str, project_context: str = ""
    ) -> SummaryModel:
        pass


class TemplateLLMAdapter(BaseLLMAdapter):
    """
    Template-based parser adapter. Searhes the text for marker keywords and
    converts them into strictly validated Pydantic model.
    """
    def summarize(self, transcript: str, history: str = "") -> SummaryModel:

        context = "Контекст встречи не определен"
        decisions = []
        open_questions = []
        conflicts = []
        next_actions = []

        lines = transcript.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Контекст:"):
                context = line.replace("Контекст:", "").strip()

            elif line.startswith("Решение:"):
                decisions.append(line.replace("Решение:", "").strip())

            elif line.startswith("Вопрос:"):
                open_questions.append(line.replace("Вопрос:", "").strip())

            elif line.startswith("Конфликт:"):
                conflicts.append(line.replace("Конфликт:", "").strip())

            elif line.startswith("Задача:"):
                task_text = line.replace("Задача:", "").strip()
                assignee = None
                assignee_match = re.search(r"@(\S+)", task_text)

                if assignee_match:
                    assignee = assignee_match.group(1)
                    task_text = re.sub(r"@\S+", "", task_text).strip()

                is_smart = (
                    "[SMART]" in task_text or ("SMART") in task_text
                )

                task_text = task_text.replace("[SMART]", "")
                task_text = task_text.replace("(SMART)", "").strip()

                next_actions.append(ActionItem(
                    task=task_text,
                    assignee=assignee,
                    is_smart=is_smart
                ))

        return SummaryModel(
            context=context,
            decisions=decisions,
            open_questions=open_questions,
            conflicts=conflicts,
            next_actions=next_actions
        )


class GeminiLLMAdapter(BaseLLMAdapter):
    """
    Адаптер для работы с API Google Gemini.
    Гарантирует возврат валидного JSON под Pydantic-модель.
    """
    def __init__(self, model_name: str = "gemini-3.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("В переменных окружения не найден GEMINI_API_KEY")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def summarize(
            self, transcript: str, history: str = ""
    ) -> SummaryModel:
        prompt = CONTRADICTION_PROMPT_TEMPLATE.format(
            project_history=history,
            meeting_transcript=transcript
        )

        response = self.model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )

        try:
            return SummaryModel.model_validate_json(response.text)
        except Exception as e:
            raise RuntimeError(
                f"Ошибка парсинга ответа Gemini: {e}\nТекст: {response.text}"
            )
