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
