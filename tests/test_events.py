import pytest
from src.transcriptor_tracker.events import EvidenceBuilder


@pytest.fixture
def builder():
    return EvidenceBuilder()


def test_build_file_uploaded(builder):
    event = builder.build_file_uploaded(
        "audio.mp3",
        "John Doe",
        "test_mail@gmail.com"
    )

    assert "actor" in event
    assert event["actor"]["name"] == "John Doe"
    assert event["verb"]["display"]["ru-RU"] == "загрузил"
    assert "audio.mp3" in event["object"]["id"]
    assert "timestamp" in event
    assert isinstance(event["timestamp"], str)


def test_build_transcribed(builder):
    event = builder.build_transcribed(
        "audio.mp3",
        "John Doe",
        "test_mail@gmail.com"
    )

    assert event["verb"]["display"]["ru-RU"] == "транскрибировал"
    assert "activity-types/transcript" in event["object"]["definition"]["type"]

    assert "timestamp" in event
    assert isinstance(event["timestamp"], str)


def test_build_published(builder):
    event = builder.build_published(
        issue_url="https://tracker/issues/1",
        actor_name="John Doe",
        actor_email="test_mail@gmail.com",
        skills=["smart-tasks"]
    )

    assert event["verb"]["display"]["ru-RU"] == "опубликовал"
    assert event["result"]["success"] is True

    ext_url = "https://example.edu/xapi/extensions/detected-patterns"
    assert "smart-tasks" in event["result"]["extensions"][ext_url]

    assert "timestamp" in event
    assert isinstance(event["timestamp"], str)


def test_build_base_event_with_context(builder):
    event = builder.build_base_event(
        actor_name="John", actor_email="j@d.com",
        verb_id="http://test/verb", verb_display="test",
        object_id="http://test/obj", object_name="obj", object_type="type",
        context={"registration": "12345"}
    )
    assert event["context"]["registration"] == "12345"
    assert "timestamp" in event
    assert isinstance(event["timestamp"], str)
