from pathlib import Path
from typing import Callable

from tko.game.game import Game
from tko.floating import Floating
from tko.floating.floating_manager import FloatingManager
from tko.floating.floating_input_text import FloatingInputText
from tko.play_tree.task_tree import TaskTree
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.i18n import Msg, t
from tko.util.rt import RT
from tko.config.sandbox_drafts import SandboxDrafts


class _DraftMsg:
    TITLE_PLACEHOLDER = Msg(pt="Digite o título da tarefa aqui", en="Type task title here")
    FOLDER_EXISTS = Msg(pt="A pasta {folder} já existe.", en="Folder {folder} already exists.")
    CREATED_AT = Msg(pt="Rascunho criado em {folder}", en="Draft created at {folder}")
    TITLE_PROMPT = Msg(
        pt="Digite o Título (use @label para definir a chave manualmente)",
        en="Type the Title (use @label to define the key manually)",
    )


class DraftCreator:

    def __init__(self, repo: Repository, settings: Settings, fman: FloatingManager, tree: TaskTree, game: Game, reload_fn: Callable[[], None]):
        self.repo = repo
        self.settings = settings
        self.fman = fman
        self.tree = tree
        self.game = game
        self.reload = reload_fn

    def create_draft(self):
        sandbox_source = self.game.get_sandbox_remote_throw()
        sandbox_folder: Path = sandbox_source.path.work_dir
        sandbox_folder.mkdir(parents=True, exist_ok=True)

        def find_numbered_draft_id(sandbox_folder: Path) -> int:
            task_keys_only: list[str] = []
            for quest in self.game.quests.values():
                for task in quest.get_tasks():
                    task_keys_only.append(task.basic.key)
            for element in sandbox_folder.iterdir():
                task_keys_only.append(element.name)
            draft_id = SandboxDrafts.find_max_numbered_key(task_keys_only=task_keys_only) + 1
            return draft_id

        def search_for_key(text: str) -> tuple[str, str]:
            key = ""
            title_words: list[str] = []
            words = text.split(" ")
            for word in words:
                if word.startswith("@"):
                    key = word[1:]
                else:
                    title_words.append(word)
            return key, " ".join(title_words)

        def __create(draft_title: str):
            key, title = search_for_key(draft_title)
            if key == "":
                key = SandboxDrafts.format_draft_key(find_numbered_draft_id(sandbox_folder))
            if title == "":
                title = t(_DraftMsg.TITLE_PLACEHOLDER)

            folder: Path = sandbox_folder / key
            if not folder.exists():
                folder.mkdir()
            else:
                self.fman.add_input(
                    Floating().bottom().right()
                    .put_text("\n" + t(_DraftMsg.FOLDER_EXISTS, folder=folder) + "\n")
                    .set_error()
                )
                return

            lang_drafts: dict[str, str] = self.settings.get_languages_settings().get_languages_with_drafts()
            draft = ""
            if self.repo.data.lang in lang_drafts:
                draft = lang_drafts[self.repo.data.lang]
            draft_path = folder / "src" / self.repo.data.lang / f"draft.{self.repo.data.lang}"
            draft_path.parent.mkdir(parents=True, exist_ok=True)
            with open(draft_path, "w", encoding="utf-8") as f:
                f.write(draft)

            SandboxDrafts.create_sandbox_draft(folder, title)
            self.tree.state.selected = f"{sandbox_source.data.name}@{key}"
            self.tree.state.expanded.add(f"{sandbox_source.data.name}@{sandbox_source.data.name}")
            self.repo.data.selected = self.tree.state.selected
            self.reload()
            self.fman.add_input(
                Floating().bottom().right()
                .put_text(t(_DraftMsg.CREATED_AT, folder=folder))
                .set_warning()
            )

        current_folders_on_rep: list[str] = [f"@{folder.name}" for folder in sandbox_folder.iterdir() if folder.is_dir()]
        obj = FloatingInputText(RT(t(_DraftMsg.TITLE_PROMPT)), __create, current_folders_on_rep)
        obj.id = "drafts"
        self.fman.add_input(obj)
