from pathlib import Path

from tko.config.settings import Settings


class DefaultDraftCreator:
    """Creates a language-specific draft without replacing existing work."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def create(self, folder: Path, language: str) -> Path | None:
        draft_path = folder / f"draft.{language}"
        if draft_path.exists():
            return None

        drafts = self.settings.get_languages_settings().get_languages_with_drafts()
        folder.mkdir(exist_ok=True, parents=True)
        draft_path.write_text(drafts.get(language, ""), encoding="utf-8")
        return draft_path
