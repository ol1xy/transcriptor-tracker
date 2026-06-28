import os
from abc import ABC, abstractmethod


class BaseTrackerAdapter(ABC):
    @abstractmethod
    def publish(self, job_id: str, content: str) -> str:
        pass


class MockTrackerAdapter(BaseTrackerAdapter):
    def __init__(self, base_dir: str = "data/published"):
        self.base_dir = base_dir

    def publish(self, job_id: str, content: str) -> str:
        job_dir = os.path.join(self.base_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)
        file_path = os.path.join(job_dir, "summary.md")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path
