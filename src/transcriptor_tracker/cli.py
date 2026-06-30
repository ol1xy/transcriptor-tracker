import typer
from src.transcriptor_tracker.transcribe import WhisperLocalAdapter
from src.transcriptor_tracker.summarize import TemplateLLMAdapter
from src.transcriptor_tracker.publish import MockTrackerAdapter
from src.transcriptor_tracker.events import EvidenceBuilder
from src.transcriptor_tracker.pipeline import PipelineEngine

app = typer.Typer(
    help="Инструмент для создания xAPI артефактов из аудиовстреч."
    )


@app.command()
def process(
    audio_path: str = typer.Argument(
        ..., help="Путь к аудиофайлу "
        "(например: data/examples/sample_meeting.mp3)"
    ),
    project_id: str = typer.Option(
        ..., "--project-id", help="Идентификатор проекта в трекере"
    ),
    issue_id: str = typer.Option(
        ..., "--issue-id", help="Идентификатор задачи в трекере"
    ),
    actor_name: str = typer.Option(
        "John Doe", "--actor-name", help="Имя пользователя для xAPI"
    ),
    actor_email: str = typer.Option(
        "john@example.com", "--actor-email", help="Почта пользователя для xAPI"
    )
):
    """
    Основная команда запуска пайплайна
    с остановкой на ревью (Human-in-the-loop).
    """
    typer.echo("Запуск Transcriptor-Tracker Pipeline...")

    # 1. Собираем двигатель из реальных адаптеров
    engine = PipelineEngine(
        transcriber=WhisperLocalAdapter(),
        summarizer=TemplateLLMAdapter(),
        tracker=MockTrackerAdapter(),
        evidence_builder=EvidenceBuilder()
    )

    typer.echo(f"Распознавание и анализ аудио: {audio_path}")

    try:
        summary_model = engine.analyze_audio(audio_path)

        markdown_text = engine._format_to_markdown(summary_model)
        typer.echo("\n" + markdown_text)

        confirm = typer.confirm(
            "Опубликовать данное резюме в трекер и создать xAPI событие?"
            )

        if not confirm:
            typer.secho(
                "Операция прервана пользователем. Публикация отменена.",
                fg=typer.colors.RED)
            raise typer.Abort()

        job_full_id = f"{project_id}_{issue_id}"
        pub_result = engine.publish_summary(
            summary_model=summary_model,
            job_id=job_full_id,
            actor_name=actor_name,
            actor_email=actor_email
        )

        typer.secho(f"Успешно. Файл сохранен: {pub_result['markdown_path']}",
                    fg=typer.colors.GREEN)
        typer.secho(f"xAPI событие сгенерировано: {pub_result['xapi_path']}",
                    fg=typer.colors.GREEN)

    except FileNotFoundError as e:
        typer.secho(f"\nОшибка файла: {str(e)}", fg=typer.colors.RED)
        raise typer.Abort()
    except Exception as e:
        typer.secho(f"\nСистемная ошибка: {str(e)}", fg=typer.colors.RED)
        raise typer.Abort()


if __name__ == "__main__":
    app()
