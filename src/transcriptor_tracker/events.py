from datetime import datetime, timezone
from typing import Dict, Any, Optional


class EvidenceBuilder:

    def __init__(self, platform_uri: str = "https://example.edu/xapi"):
        self.platform_uri = platform_uri

    def _get_actor(self, name: str, email: str) -> Dict[str, Any]:
        return {
            "name": name,
            "mbox": f"mailto:{email}"
        }

    def build_base_event(
        self, actor_name: str, actor_email: str,
        verb_id: str, verb_display: str,
        object_id: str, object_name: str, object_type: str,
        result: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        event = {
            "actor": self._get_actor(actor_name, actor_email),
            "verb": {
                "id": verb_id,
                "display": {"ru-RU": verb_display}
            },
            "object": {
                "id": object_id,
                "definition": {
                    "name": {"ru-RU": object_name},
                    "type": object_type
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if result:
            event["result"] = result

        if context:
            event["context"] = context

        return event

    def build_file_uploaded(
        self, file_path: str, actor_name: str, actor_email: str
    ) -> Dict[str, Any]:
        return self.build_base_event(
            actor_name=actor_name,
            actor_email=actor_email,
            verb_id=f"{self.platform_uri}/verbs/uploaded",
            verb_display="загрузил",
            object_id=f"{self.platform_uri}/files/{file_path}",
            object_name=f"Аудиофайл {file_path}",
            object_type=f"{self.platform_uri}/activity-types/file"
        )

    def build_transcribed(
        self, file_path: str, actor_name: str, actor_email: str
    ) -> Dict[str, Any]:
        return self.build_base_event(
            actor_name=actor_name,
            actor_email=actor_email,
            verb_id=f"{self.platform_uri}/verbs/transcribed",
            verb_display="транскрибировал",
            object_id=f"{self.platform_uri}/files/{file_path}",
            object_name=f"Транскрипт аудио {file_path}",
            object_type=f"{self.platform_uri}/activity-types/transcript"
        )

    def build_published(
        self, issue_url: str, actor_name: str, actor_email: str,
        skills: list[str] = None
    ) -> Dict[str, Any]:
        skills = skills or []
        ext_key = f"{self.platform_uri}/extensions/detected-patterns"
        result_block = {
            "success": True,
            "extensions": {ext_key: skills}
        }

        return self.build_base_event(
            actor_name=actor_name,
            actor_email=actor_email,
            verb_id="http://adlnet.gov/expapi/verbs/created",
            verb_display="опубликовал",
            object_id=issue_url,
            object_name="Проверенное резюме обсуждения",
            object_type=f"{self.platform_uri}/activity-types/artifact",
            result=result_block
        )
