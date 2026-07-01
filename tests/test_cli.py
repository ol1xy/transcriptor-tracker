from unittest.mock import patch
from typer.testing import CliRunner
from src.transcriptor_tracker.cli import app
from src.transcriptor_tracker.models import SummaryModel

runner = CliRunner()

# Создаем фейковую SummaryModel, которую якобы вернула Нейросеть
fake_summary_model = SummaryModel(
    context="Тестовый контекст.",
    decisions=[],
    open_questions=[],
    conflicts=["Тестовый конфликт"],
    next_actions=[]
)


@patch("src.transcriptor_tracker.pipeline.PipelineEngine.analyze_audio")
def test_cli_integration_abort_scenario(mock_analyze, tmp_path):
    """Негативный сценарий:
    Пользователь отказывается от публикации (вводит N)."""
    fake_audio = tmp_path / "fake_audio.mp3"
    fake_audio.write_text("fake")
    mock_analyze.return_value = fake_summary_model

    result = runner.invoke(app, [
        str(fake_audio),
        "--project-id", "proj-1",
        "--issue-id", "101"
    ], input="N\n")

    assert result.exit_code != 0
    assert "Операция прервана пользователем" in result.stdout


@patch("src.transcriptor_tracker.pipeline.PipelineEngine.publish_summary")
@patch(
    "src.transcriptor_tracker.pipeline.PipelineEngine.analyze_audio"
    )
def test_cli_integration_success_scenario(
    mock_analyze, mock_publish, tmp_path
):
    """Позитивный сценарий:
    Пользователь соглашается на публикации (вводит Y)."""
    fake_audio = tmp_path / "fake_audio.mp3"
    fake_audio.write_text("fake")

    mock_analyze.return_value = fake_summary_model
    mock_publish.return_value = {
        "markdown_path": "fake/path/summary.md",
        "xapi_path": "fake/path/event.json"
    }

    result = runner.invoke(app, [
        str(fake_audio),
        "--project-id", "proj-1",
        "--issue-id", "101"
    ], input="y\n")

    assert result.exit_code == 0
    assert "Успешно" in result.stdout
    mock_publish.assert_called_once()


@patch("src.transcriptor_tracker.pipeline.PipelineEngine.analyze_audio")
def test_cli_integration_file_not_found(mock_analyze):
    """Проверка перехвата ошибки несуществующего файла в CLI."""

    mock_analyze.side_effect = FileNotFoundError("Аудиофайл не найден")

    result = runner.invoke(app, [
        "missing_file_123.mp3",
        "--project-id", "proj-1",
        "--issue-id", "101"
    ])

    assert result.exit_code != 0
    assert "Ошибка файла" in result.stdout
