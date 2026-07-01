import os


class LocalKnowledgeBase:
    """
    Class for uploading knowledge base
    from local disk.
    """
    def __init__(self,
                 history_path: str =
                 "data/knowledge_base/project_history.md"):
        self.history_path = history_path

    def load_history(self) -> str:
        """
        Reads the project history file.
        Throws an error if the file is missing.
        """
        if not os.path.exists(self.base_dir if hasattr(self, 'base_dir')
                              else self.history_path):
            raise FileNotFoundError(
                f"История проекта не найдена по пути: {self.history_path}"
            )
        
        with open(self.history_path, "r", encoding="utf-8") as f:
            return f.read().strip()