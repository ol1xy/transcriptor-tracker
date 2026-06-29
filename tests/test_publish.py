import os
from src.transcriptor_tracker.publish import MockTrackerAdapter


def test_mock_tracker_adapter_publish(tmp_path):
    test_base_dir = str(tmp_path / "published")
    adapter = MockTrackerAdapter(base_dir=test_base_dir)
    job_id = "job_42"
    test_content = "# Итоги\nРабота продолжается. Много исправлять."

    result_path = adapter.publish(job_id, test_content)

    assert os.path.exists(result_path)
    assert job_id in result_path
    assert result_path.endswith("summary.md")

    with open(result_path, "r", encoding="utf-8") as f:
        saved_content = f.read()
    assert saved_content == test_content
