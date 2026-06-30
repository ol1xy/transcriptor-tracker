from unittest.mock import patch
from typer.testing import CliRunner
from src.transcriptor_tracker.cli import app

runner = CliRunner()


@patch("src.transcriptor_tracker.transcribe.WhisperLocalAdapter.transcribe")
def test_cli_integration_abort_scenario(mock_transcribe, tmp_path):
    """
    Негативный сценарий: Пользователь отказывается от публикации (вводит N).
    """
    fake_audio = tmp_path / "fake_audio.mp3"
    fake_audio.write_text("fake")

    mock_transcribe.return_value = (
        "Контекст: Тест отмены.\nРешение: Ничего."
    )

    result = runner.invoke(app, [
        str(fake_audio),
        "--project-id", "proj-1",
        "--issue-id", "101"
    ], input="N\n")

    assert result.exit_code != 0
    assert "Операция прервана пользователем" in result.stdout


@patch("src.transcriptor_tracker.publish.MockTrackerAdapter.publish")
@patch("src.transcriptor_tracker.transcribe.WhisperLocalAdapter.transcribe")
def test_cli_integration_success_scenario(
    mock_transcribe, mock_publish, tmp_path
):
    """
    Позитивный сценарий: Пользователь соглашается на публикации (вводит Y).
    """
    fake_audio = tmp_path / "fake_audio.mp3"
    fake_audio.write_text("fake")

    mock_transcribe.return_value = (
        "Контекст: Тест успеха.\nРешение: Публикуем."
    )
    mock_publish.return_value = "data/published/test/summary.md"

    with patch("builtins.open"), patch("json.dump"):
        result = runner.invoke(app, [
            str(fake_audio),
            "--project-id", "proj-1",
            "--issue-id", "101"
        ], input="y\n")

    assert result.exit_code == 0
    assert "Успешно. Файл сохранен:" in result.stdout
    mock_publish.assert_called_once()


def test_cli_integration_file_not_found():
    """
    Проверка перехвата ошибки несуществующего файла в CLI.
    """
    result = runner.invoke(app, [
        "missing_file_123.mp3",
        "--project-id", "proj-1",
        "--issue-id", "101"
    ])

    assert result.exit_code != 0
    assert "Ошибка файла" in result.stdout
