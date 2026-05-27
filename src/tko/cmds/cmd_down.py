from typing import Callable
import os
import shutil

from tko.cmds.drafts_finder_cached import DraftsFinderCached
from tko.repository.repository import Repository
from tko.config.settings import Settings
from tko.game.game import Game
from tko.util.decoder import Decoder
from tko.feno.link_rebase import LinkRebase
from tko.game.task import Task
from tko.game.task_enums import TaskEval
from tko.feno.filter import CodeFilter
from pathlib import Path
from tko.loader.toml_parser import TomlParser
from tko.i18n import Msg, t


_DOWN_INVALID_REPO_ARG = Msg(
    pt="O parâmetro para o comando tko down deve a pasta onde você iniciou o repositório.",
    en="The argument for tko down must be the folder where you initialized the repository.",
)
_DOWN_INVALID_REPO_ARG_ACTION = Msg(
    pt="Navegue ou passe o caminho até a pasta do repositório e tente novamente.",
    en="Navigate to that folder or pass its path and try again.",
)
_CMD_DOWN_ACTIVITY_LINK_NOT_DOWNLOADABLE = Msg(
    pt="Atividade {task_key} é do tipo link, ela não é para download",
    en="Activity {task_key} is a link type and is not downloadable",
)
_CMD_DOWN_ACTIVITY_NO_ORIGIN_FOLDER = Msg(
    pt="Atividade {task_key} não possui pasta de origem para download",
    en="Activity {task_key} has no source folder for download",
)
_CMD_DOWN_ACTIVITY_NO_DESTINY_FOLDER = Msg(
    pt="Atividade {task_key} não possui pasta de destino para download",
    en="Activity {task_key} has no destination folder for download",
)
_DOWN_ACTIVITY_ALREADY_PRESENT = Msg(
    pt="Atividade já está no repositório, precisa baixar nenhum arquivo",
    en="Activity is already in the repository; no files need to be downloaded",
)
_DOWN_LINK_HAS_NO_DOWNLOAD = Msg(
    pt="falha: link para atividade não possui link para download",
    en="fail: activity link does not provide a download link",
)
_DOWN_CREATING_NEW_DRAFT_FOLDER = Msg(
    pt="Criando nova pasta de rascunhos: {folder}",
    en="Creating new drafts folder: {folder}",
)
_DOWN_COPY_NEW_DRAFTS_MANUALLY = Msg(
    pt="Se quiser utilizar os novos rascunhos, copie manualmente",
    en="If you want to use the new drafts, copy them manually",
)
_DOWN_COPY_NEW_DRAFTS_TO_LANG = Msg(
    pt="os novos rascunhos para a pasta {lang}",
    en="the new drafts to folder {lang}",
)
_DOWN_LATEST_DRAFT = Msg(
    pt="Último rascunho em {name}",
    en="Latest draft in {name}",
)
_DOWN_ACTIVITY_DOWNLOADED_SUCCESS = Msg(
    pt="Atividade baixada com sucesso",
    en="Activity downloaded successfully",
)
_DOWN_CHOOSE_DRAFT_EXTENSION = Msg(
    pt="Escolha uma extensão para os rascunhos: [{options}]: ",
    en="Choose a draft extension: [{options}]: ",
)
_DOWN_FILE_NEW = Msg(
    pt="{path} (Novo)",
    en="{path} (New)",
)
_DOWN_FILE_UPDATED = Msg(
    pt="{path} (Atualizado)",
    en="{path} (Updated)",
)
_DOWN_FILE_UNCHANGED = Msg(
    pt="{path} (Inalterado)",
    en="{path} (Unchanged)",
)
_DOWN_FILE_EMPTY = Msg(
    pt="{path} (Vazio)",
    en="{path} (Empty)",
)
_DOWN_FILE_NOT_OVERWRITTEN = Msg(
    pt="{path} (Não sobrescrito)",
    en="{path} (Not overwritten)",
)

class CmdLineDown:
    def __init__(self, settings: Settings, rep: Repository, task_key: str, game: Game | None = None):
        self.settings = settings
        self.rep = rep
        self.task_key = task_key
        if game is None:
            from tko.repository.repository_config import RepositoryConfig
            from tko.repository.game_coordinator import GameCoordinator
            RepositoryConfig(self.rep).load()
            GameCoordinator(self.rep).load_game(verbose=True)
            self.game = self.rep.game
        else:
            self.game = game
        
    def execute(self):
        if not self.rep.paths.config_file.exists():
            print(t(_DOWN_INVALID_REPO_ARG))
            print(t(_DOWN_INVALID_REPO_ARG_ACTION))
            return False
    
        CmdDown(self.rep, self.task_key, self.settings).execute()
        return True


class CmdDown:
    def __init__(self, repo: Repository, task_key: str, settings: Settings):
        self.repo = repo
        self.task_key = task_key
        self.settings = settings
        self.task: Task = self.repo.game.get_task(self.task_key)
        self.resolver = self.task.path
        if self.task.resource.is_read:
            raise ValueError(t(_CMD_DOWN_ACTIVITY_LINK_NOT_DOWNLOADABLE, task_key=self.task_key))
        
        origin_target = self.resolver.origin_target
        destiny_folder = self.resolver.work_dir
        if origin_target is None:
            raise ValueError(t(_CMD_DOWN_ACTIVITY_NO_ORIGIN_FOLDER, task_key=self.task_key))
        if destiny_folder is None:
            raise ValueError(t(_CMD_DOWN_ACTIVITY_NO_DESTINY_FOLDER, task_key=self.task_key))

        self.origin_folder: Path = origin_target.parent        
        self.destiny_folder: Path = destiny_folder
       
        self.language: str = ""
        self.check_and_get_language()
        self.actions = DownActions(self.settings)
        
    def execute(self) -> bool:
        if self.task.resource.is_import_type:
            return self.download_from_external_remote()
        if self.task.resource.is_static_type:
            if not self.copy_drafts():
                self.actions.send_to_print(t(_DOWN_ACTIVITY_ALREADY_PRESENT))
            return False
        self.actions.send_to_print(t(_DOWN_LINK_HAS_NO_DOWNLOAD))
        return False

    def set_fnprint(self, fnprint: Callable[[str], None]):
        self.actions.fnprint = fnprint
        return self

    def remove_empty_destiny_folder(self):
        if os.path.exists(self.destiny_folder):
            if len(os.listdir(self.destiny_folder)) == 0:
                os.rmdir(self.destiny_folder)

    def find_and_create_folder_for_drafts(self, force: bool = False) -> Path:
        lang = self.language
        finder = DraftsFinderCached(self.destiny_folder, lang)
        drafts_folder = finder.find_dir_for_drafts()
        if not drafts_folder.exists():
            drafts_folder.mkdir(parents=True, exist_ok=True)
            return drafts_folder
        elif force:
            shutil.rmtree(drafts_folder)
            drafts_folder.mkdir(parents=True, exist_ok=True)
            return drafts_folder
        
        drafts_folder = finder.find_dir_for_drafts_secondary()
        self.actions.send_to_print("")
        self.actions.send_to_print(t(_DOWN_CREATING_NEW_DRAFT_FOLDER, folder=drafts_folder.name))
        self.actions.send_to_print("")
        self.actions.send_to_print(t(_DOWN_COPY_NEW_DRAFTS_MANUALLY))
        self.actions.send_to_print(t(_DOWN_COPY_NEW_DRAFTS_TO_LANG, lang=lang))
        return Path(drafts_folder)

    def download_from_external_remote(self) -> bool:
        self.destiny_folder.mkdir(exist_ok=True, parents=True)
        self.copy_readme()
        self.copy_tests()
        return self.copy_drafts()

    def copy_drafts(self):
        self.actions.cached = True
        finder = DraftsFinderCached(self.destiny_folder, self.language)
        if not self.task.resource.is_import_type:
            destiny_drafts_folder: Path = finder.find_dir_for_drafts()
            destiny_drafts_folder.mkdir(exist_ok=True, parents=True)
            self.actions.create_default_draft(destiny_drafts_folder, self.language)
            return True

        destiny_drafts_folder: Path = self.find_and_create_folder_for_drafts()
        origin_drafts_source: Path = CodeFilter.get_source_drafts_dir(self.origin_folder, self.language)
        if not self.copy_drafts_from(origin_drafts_source, destiny_drafts_folder):
            self.actions.create_default_draft(destiny_drafts_folder, self.language)
        if self.task.config.test == TaskEval.SELF:
            self.actions.create_default_draft(destiny_drafts_folder, "md")
        removed, last_path = finder.remove_secondary_dir_if_duplicated()
        self.actions.cached = False
        if not removed:
            for msg in self.actions.cache_msgs:
                self.actions.send_to_print(msg)
            self.actions.cache_msgs.clear()
        else:
            self.actions.send_to_print(t(_DOWN_LATEST_DRAFT, name=os.path.basename(last_path)))
        self.actions.send_to_print("")
        self.actions.send_to_print(t(_DOWN_ACTIVITY_DOWNLOADED_SUCCESS))
        return True
    
    def copy_readme(self):
        origin_readme  = self.origin_folder /"README.md"
        destiny_readme = self.destiny_folder/ "README.md"

        source_folder_rel = self.origin_folder.resolve().relative_to(self.destiny_folder.resolve(), walk_up=True)
        content = Decoder.load(origin_readme)
        content = LinkRebase.change_to_relative_folder(content, source_folder_rel)
        self.actions.compare_and_save_to(content, destiny_readme)
    
    def copy_drafts_from(self, origin_drafts_folder: Path, destiny_draft_folder: Path) -> bool:
        if not os.path.exists(origin_drafts_folder):
            return False
        destiny_draft_folder.mkdir(exist_ok=True)
        if self.copy_drafts_from_cache(origin_drafts_folder, destiny_draft_folder):
            return True
        return False
        

    def copy_drafts_from_cache(self, cache_draft_folder: Path, destiny_draft_folder: Path) -> bool:
        found: bool = False
        for file in cache_draft_folder.iterdir():
            destiny_path = destiny_draft_folder / file.name
            self.actions.compare_and_save_to(Decoder.load(file), destiny_path)
            found = True
        return found
        

    def copy_tests(self):
        source_folder = self.origin_folder
        destiny_folder = self.destiny_folder
        # copy any file with extension .toml or .tio from source_folder to destiny_folder, if they are different
        for file in source_folder.iterdir():
            if file.suffix == ".tio": 
                destiny_path = destiny_folder / file.name
                self.actions.compare_and_save_to(Decoder.load(file), destiny_path)
            if file.suffix == ".toml":
                destiny_path = destiny_folder / file.name
                content = TomlParser.load_and_expand_from_path(file)
                self.actions.compare_and_save_to(content, destiny_path)


    def check_and_get_language(self) -> None:
        language_def = self.repo.data.lang

        if self.language == "":
            if language_def != "":
                self.language = language_def
            else:
                langs = self.settings.get_languages_settings().get_languages_with_drafts()
                print(t(_DOWN_CHOOSE_DRAFT_EXTENSION, options=", ".join(langs.keys())), end="")
                self.language = input()

class DownActions:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.fnprint: Callable[[str], None] = print
        self.cache_msgs: list[str] = []
        self.cached: bool = False

    def send_to_print(self, text: str):
        if self.cached:
            self.cache_msgs.append(text)
        else:
            self.fnprint(text)

    @staticmethod
    def folder_and_file(path: Path, parts: int = 3) -> str:
        """ Return the folder and file name of the path """
        return path.relative_to(Path.cwd(), walk_up=True).as_posix()
        # pieces = path.resolve().parts
        # pieces = pieces[-parts:]  # Get the last 'parts' elements
        # return os.path.join(*pieces)

    def compare_and_save_to(self, content: str, path: Path):
        if not os.path.exists(path):
            Decoder.save(path, content)
            self.send_to_print(t(_DOWN_FILE_NEW, path=self.folder_and_file(path)))
        else:
            path_content = Decoder.load(path)
            if path_content != content:
                self.send_to_print(t(_DOWN_FILE_UPDATED, path=self.folder_and_file(path)))
                Decoder.save(path, content)
            else:
                self.send_to_print(t(_DOWN_FILE_UNCHANGED, path=self.folder_and_file(path)))

    def create_default_draft(self, destiny: Path, language: str):
        filename = "draft."
        draft_path = destiny / (filename + language)
        os.makedirs(os.path.dirname(draft_path), exist_ok=True)
        lang_drafts: dict[str, str] = self.settings.get_languages_settings().get_languages_with_drafts()
        if not os.path.exists(draft_path):
            with open(draft_path, "w", encoding="utf-8") as f:
                if language in lang_drafts.keys():
                    f.write(lang_drafts[language])
                else:
                    f.write("")
            self.send_to_print(t(_DOWN_FILE_EMPTY, path=self.folder_and_file(draft_path, 3)))
        else:
            self.send_to_print(t(_DOWN_FILE_NOT_OVERWRITTEN, path=self.folder_and_file(draft_path, 3)))
        return draft_path
