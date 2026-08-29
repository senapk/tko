from pathlib import Path
from tko.play.language_setter import LanguageSetter
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths
from tko.config.settings import Settings
from tko.repository.repository_config import RepositoryLoader
from tko.i18n import Msg
from tko.util.console import Console
from tko.util.rt import RT
from tko.repository.git_cache import GitCache
from tko.config.user_data import UserData

_REPO_STARTER_LANGUAGE_SET = Msg.parse(
    pt="A linguagem do repositório foi definida como [y]{language}[].",
    en="Repository language set to [y]{language}[].",
)
_REPO_STARTER_OPEN_HINT = Msg.parse(
    pt="Voce pode acessar o repositório com o comando [g]tko open[]",
    en="You can access the repository with the command [g]tko open[]",
)
_REPO_STARTER_EXISTS = Msg.parse(
    pt="Já existe um repositório TKO na pasta [g]{folder}[]",
    en="A TKO repository already exists in folder [g]{folder}[]",
)
_REPO_STARTER_RESET_PROMPT = Msg.parse(
    pt="Deseja resetar o repositório? [[Y/n]]: ",
    en="Do you want to reset the repository? [[Y/n]]: ",
)
_REPO_STARTER_INSIDE_OTHER_REPO = Msg.parse(
    pt="Você está tentando criar um repositório dentro de outro, pois já existe rep em [r]{parent}[]",
    en="You are trying to create a repository inside another one, because there is already a repo in [r]{parent}[]",
)
_REPO_STARTER_DEEP_REPO_WARN_2 = Msg.text(
    pt="Porém já existem repositórios TKO abaixo dessa pasta. Mova ou apague-os",
    en="But there are already TKO repositories below that folder. Move or delete them",
)
_REPO_STARTER_OVERWRITE_PROMPT = Msg.parse(
    pt="Deseja sobrescrever as configurações do repositório em [y]{folder}[] ? [[Y/n]]: ",
    en="Do you want to overwrite the repository settings in [y]{folder}[] ? [[Y/n]]: ",
)
_REPO_STARTER_DEEP_REPO_WARN = Msg.parse(
    pt="Você está tentando criar um repositório TKO na pasta [y]{folder}[]",
    en="You are trying to create a TKO repository in folder [y]{folder}[]",
)
_REPO_STARTER_EMPTY_REPO = Msg.text(
    pt="Criando repositório ...",
    en="Creating repository ...",
)

_REPO_ASK_DEFAULT_SOURCES = Msg.parse(
    pt="Você [g]deseja adicionar[] algum dos [g]repositório[] padrão de atividades? [[Y/n]]: ",
    en="Do you [g]want to add[] any of the default activity [g]repositories[]? [[Y/n]]: ",
)
_REPO_ASK_DEFAULT_SOURCES_FUP = Msg.parse(
    pt="[y]fup[] - Fundamentos de Programação",
    en="[y]fup[] - Programming Fundamentals",
)
_REPO_ASK_DEFAULT_SOURCES_POO = Msg.parse(
    pt="[y]poo[] - Programação Orientada a Objetos",
    en="[y]poo[] - Object Oriented Programming",
)
_REPO_ASK_DEFAULT_SOURCES_ED = Msg.parse(
    pt="[y]ed[] - Estruturas de Dados",
    en="[y]ed[] - Data Structures",
)

_REPO_NONE_ADDED = Msg.parse(
    pt="Nenhum repositório adicionado. Você pode adicionar com o comando [y]{cmd}",
    en="No repository added. You can add with the command [y]{cmd}",
)

_REPO_INVALID_OPTION = Msg.parse(
    pt="Opção inválida. Por favor, escolha uma opção válida.",
    en="Invalid option. Please, choose a valid option.",
)

_WITCH_REPO = Msg.parse(
    pt="Qual repositório você deseja adicionar [[[y]{options}[.]]]: ",
    en="Which repository do you want to add [[[y]{options}[.]]]: ",
)

class RepositoryStarter:
    def __init__(self, settings: Settings, language: str | None, skip_add_remote: bool, force_location: bool = False):
        self.settings = settings
        self.skip = skip_add_remote
        self.force_location = force_location
        self.folder: Path = settings.rs.changedir
        self.language = language

    def execute(self) -> bool:
        if not self.force_location:
            if not self.validate_path():
                return False
        git_cache = GitCache(cache_dir=UserData.global_cache_dir(), update_mode=self.settings.rs.update_mode)
        repo = Repository(self.folder, self.settings.rs, git_cache=git_cache)
        self.repo = repo
        self.language = LanguageSetter.check_prog_lang_in_text_mode(self.settings, self.repo, selected=self.language)
        Console.print(_REPO_STARTER_LANGUAGE_SET.t().format(language=self.language))

        if not self.skip:
            self.ask_about_default_sources()

        authoring = repo.data.get_authoring_remote() if hasattr(repo.data, "get_authoring_remote") else None
        if authoring is not None:
            index_file, _ = repo.remote_resolver.resolve_index_file(authoring, load_git=False)
            index_file.parent.mkdir(parents=True, exist_ok=True)
            if not index_file.exists():
                index_file.write_text(f"# {authoring.name}\n\n", encoding="utf-8")
            repo.remote_resolver.source_activity_dir(authoring).mkdir(parents=True, exist_ok=True)

        RepositoryLoader(repo).save()
        Console.print(_REPO_STARTER_OPEN_HINT.t())
        return True

    def ask_about_default_sources(self):
        Console.print(_REPO_ASK_DEFAULT_SOURCES, end="")
        answer = input().lower()
        if answer == "n":
            Console.print(_REPO_NONE_ADDED.t().format(cmd="tko source add LABEL URI"))
            return
        Console.print(_REPO_ASK_DEFAULT_SOURCES_FUP.t())
        Console.print(_REPO_ASK_DEFAULT_SOURCES_POO.t())
        Console.print(_REPO_ASK_DEFAULT_SOURCES_ED.t())

        options = ["fup", "poo", "ed", "none"]
        while True:
            Console.print(_WITCH_REPO.t().format(options=", ".join(options)), end="")
            op = input().lower()
            if op in options:
                if op != "none":
                    self.add_default_source(op)
                return

    def add_default_source(self, target: str):
        from tko.repository.source_actions import SourceActions
        source_actions = SourceActions(self.settings, self.repo)
        source_actions.add_default_source(label=target, default_alias=target)


    def validate_path(self) -> bool:
        path_parents = RepositoryPaths.rec_search_for_repo_parents(self.folder)

        if path_parents is not None and path_parents.resolve() == self.folder.resolve():
            Console.print(_REPO_STARTER_EXISTS.t().format(folder=self.folder.resolve()))
            Console.print(_REPO_STARTER_RESET_PROMPT.t(), end="")
            op = input().lower()
            if op == "n":
                return False

        elif path_parents is not None:
            if self.folder != path_parents:
                Console.print(_REPO_STARTER_INSIDE_OTHER_REPO.t().format(parent=path_parents))
                Console.print(_REPO_STARTER_DEEP_REPO_WARN_2.t())
            self.folder = path_parents
            Console.print(_REPO_STARTER_OVERWRITE_PROMPT.t().format(folder=self.folder), end="")
            op = input().lower()
            if op == "n":
                return False
        else:
            path_subdir_list = RepositoryPaths.rec_search_for_repo_subdir(self.folder)
            if len(path_subdir_list) > 0:
                Console.print(_REPO_STARTER_DEEP_REPO_WARN.t().format(folder=self.folder.resolve()))
                Console.print(_REPO_STARTER_DEEP_REPO_WARN_2.t())
                for path in path_subdir_list:
                    Console.print(RT.parse(f"- [r]{path}"))
                return False

        return True
