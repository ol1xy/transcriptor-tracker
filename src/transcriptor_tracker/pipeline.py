import json
import os
from typing import Dict, Any, List

from src.transcriptor_tracker.transcribe import BaseTranscriberAdapter
from src.transcriptor_tracker.summarize import BaseLLMAdapter
from src.transcriptor_tracker.publish import BaseTrackerAdapter
from src.transcriptor_tracker.events import EvidenceBuilder
from src.transcriptor_tracker.models import SummaryModel


class PipelineEngine:
    """
    Main control pipeline (Orchestrator).
    Links isolated adapters into a unified processing chain.
    """
    def __init__(
            self,
            transcriber: BaseTranscriberAdapter,
            summarizer: BaseLLMAdapter,
            tracker: BaseTrackerAdapter,
            evidence_builder: EvidenceBuilder
        ):
        
        self.transcriber = transcriber
        self.summarizer = summarizer
        self.tracker = tracker
        self.evidence_builder = evidence_builder

    def _format_to_markdown(self, summary: SummaryModel) -> str:
        """
        Internal helper.
        Converts the `SummaryModel` Pydantic model into a
        structured Markdown string for publication.
        """
        lines = [
            "# Конспект встречи\n",
            f"### Контекст\n{summary.context}\n"
        ]

        if summary.decisions:
            lines.append("### Принятые решения")
            for d in summary.decisions:
                lines.append(f"* {d}")
            lines.append("")

        if summary.open_questions:
            lines.append("### Открытые вопросы")
            for q in summary.open_questions:
                lines.append(f"* {q}")
            lines.append("")

        if summary.conflicts:
            lines.append("### Выявленные противоречия / конфликты")
            for c in summary.conflicts:
                lines.append(f"* {c}")
            lines.append("")

        if summary.next_actions:
            lines.append("### Следующие шаги (Задачи)")
            for item in summary.next_actions:
                assignee_str = f" @{item.assignee}" if item.assignee else ""
                smart_str = " [SMART]" if item.is_smart else ""
                lines.append(f"* {item.task}{assignee_str}{smart_str}")
            lines.append("")

        return "\n".join(lines)

    def _extract_skills(self, summary: SummaryModel) -> List[str]:
        """
        Internal helper. 
        Analyzes the summary and extracts a list of demonstrated skills
        (for inclusion in an xAPI event).
        """
        skills = []

        has_smart = any(item.is_smart for item in summary.next_actions)
        if has_smart:
            skills.append("smart-task-definition")

        if summary.conflicts:
            skills.append("conflict-resolution")

        return skills
    
