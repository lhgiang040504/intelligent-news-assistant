from pathlib import Path

from config.settings import Settings
from src.pipeline.pipeline import NewsPipeline


def main() -> None:
    settings = Settings.default()
    pipeline = NewsPipeline(settings=settings)
    report_markdown = pipeline.run()

    output_path = Path(settings.report_output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_markdown, encoding="utf-8")

    print(f"Weekly report generated: {output_path}")


if __name__ == "__main__":
    main()