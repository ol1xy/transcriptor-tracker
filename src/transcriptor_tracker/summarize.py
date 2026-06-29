import re
from abc import ABC, abstractmethod
from src.transcriptor_tracker.models import SummaryModel, ActionItem


class BaseLLMAdapter(ABC):
    """
    Interface for work with LLM.
    Defines a strict contract: transcript text as input,
    SummaryModel as output.
    """
    @abstractmethod
    def summarize(self, transcript: str) -> SummaryModel:
        pass


class TemplateLLMAdapter(BaseLLMAdapter):
    """
    Template-based parser adapter. Searhes the text for marker keywords and
    converts them into strictly validated Pydantic model.
    """
    def summarize(self, transcript: str) -> SummaryModel:

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
