from pathlib import Path
from tko.play.language_setter import LanguageSetter
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths
from tko.config.settings import Settings
from tko.repository.repository_config import RepositoryConfig
from tko.i18n import Msg
from tko.util.console import Console


_REPO_STARTER_LANGUAGE_SET = Msg(
    pt="A linguagem do repositório foi definida como [y]{language}[.].",
    en="Repository language set to [y]{language}[.].",
)
_REPO_STARTER_OPEN_HINT = Msg(
    pt="Voce pode acessar o repositório com o comando [g]tko open[]",
    en="You can access the repository with the command [g]tko open[]",
)
_REPO_STARTER_EXISTS = Msg(
    pt="Já existe um repositório TKO na pasta [g]{folder}[]",
    en="A TKO repository already exists in folder [g]{folder}[]",
)
_REPO_STARTER_RESET_PROMPT = Msg(
    pt="Deseja resetar o repositório? [[Y/N]]: ",
    en="Do you want to reset the repository? [[Y/N]]: ",
)
_REPO_STARTER_INSIDE_OTHER_REPO = Msg(
    pt="Você está tentando criar um repositório dentro de outro, pois já existe rep em [r]{parent}[]",
    en="You are trying to create a repository inside another one, because there is already a repo in [r]{parent}[]",
)
_REPO_STARTER_DEEP_REPO_WARN_2 = Msg(
    pt="Porém já existem repositórios TKO abaixo dessa pasta. Mova ou apague-os",
    en="But there are already TKO repositories below that folder. Move or delete them",
)
_REPO_STARTER_OVERWRITE_PROMPT = Msg(
    pt="Deseja sobrescrever as configurações do repositório em [y]{folder}[] ? [[Y/n]]: ",
    en="Do you want to overwrite the repository settings in [y]{folder}[] ? [[Y/n]]: ",
)
_REPO_STARTER_DEEP_REPO_WARN = Msg(
    pt="Você está tentando criar um repositório TKO na pasta [y]{folder}[]",
    en="You are trying to create a TKO repository in folder [y]{folder}[]",
)
_REPO_STARTER_EMPTY_REPO = Msg(
    pt="Criando repositório ...",
    en="Creating repository ...",
)

_REPO_ASK_DEFAULT_REMOTES = Msg(
    pt="Você [g]deseja adicionar[] algum dos [g]repositório[] padrão de atividades? [[Y/n]]: ",
    en="Do you [g]want to add[] any of the default activity [g]repositories[]? [[Y/n]]: ",
)
_REPO_ASK_DEFAULT_REMOTES_FUP = Msg(
    pt="[y]fup[] - Fundamentos de Programação",
    en="[y]fup[] - Programming Fundamentals",
)
_REPO_ASK_DEFAULT_REMOTES_POO = Msg(
    pt="[y]poo[] - Programação Orientada a Objetos",
    en="[y]poo[] - Object Oriented Programming",
)
_REPO_ASK_DEFAULT_REMOTES_ED = Msg(
    pt="[y]ed[] - Estruturas de Dados",
    en="[y]ed[] - Data Structures",
)

_REPO_NONE_ADDED = Msg(
    pt="Nenhum repositório adicionado. Você pode adicionar com o comando [y]{cmd}",
    en="No repository added. You can add with the command [y]{cmd}",
)

_REPO_INVALID_OPTION = Msg(
    pt="Opção inválida. Por favor, escolha uma opção válida.",
    en="Invalid option. Please, choose a valid option.",
)

_WITCH_REPO = Msg(
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
        repo = Repository(self.folder, self.settings.rs)        
        self.repo = repo
        self.create_empty_repo()
        self.language = LanguageSetter.check_prog_lang_in_text_mode(self.settings, self.repo, selected=self.language)
        Console.print(_REPO_STARTER_LANGUAGE_SET, language=self.language)
        
        if not self.skip:
            self.ask_about_default_remotes()

        RepositoryConfig(repo).save()
        Console.print(_REPO_STARTER_OPEN_HINT)
        return True

    def ask_about_default_remotes(self):
        Console.print(_REPO_ASK_DEFAULT_REMOTES, end="")
        answer = input().lower()
        if answer == "n":
            Console.print(_REPO_NONE_ADDED, cmd="[.y] tko remote add LABEL URL")
            return
        Console.print(_REPO_ASK_DEFAULT_REMOTES_FUP)
        Console.print(_REPO_ASK_DEFAULT_REMOTES_POO)
        Console.print(_REPO_ASK_DEFAULT_REMOTES_ED)

        options = ["fup", "poo", "ed", "none"]
        while True: 
            Console.print(_WITCH_REPO, options=", ".join(options), end="")
            op = input().lower()
            if op in options:
                if op != "none":
                    self.add_remote(op)
                return

    def add_remote(self, target: str):
        from tko.repository.remote_actions import RemoteActions
        rep_actions = RemoteActions(self.settings, self.repo)
        rep_actions.remote_add(
            name=target,
            remote_default=target, 
        )

    
    def validate_path(self) -> bool:
        path_parents = RepositoryPaths.rec_search_for_repo_parents(self.folder)

        if path_parents is not None and path_parents.resolve() == self.folder.resolve():
            Console.print(_REPO_STARTER_EXISTS, folder=self.folder.resolve())                
            Console.print(_REPO_STARTER_RESET_PROMPT, end="")
            op = input().lower()
            if op == "n":
                return False

        elif path_parents is not None:
            if self.folder != path_parents:
                Console.print(_REPO_STARTER_INSIDE_OTHER_REPO, parent=path_parents)
                Console.print(_REPO_STARTER_DEEP_REPO_WARN_2)
            self.folder = path_parents
            Console.print(_REPO_STARTER_OVERWRITE_PROMPT, folder=self.folder, end="")
            op = input().lower()
            if op == "n":
                return False
        else:
            path_subdir_list = RepositoryPaths.rec_search_for_repo_subdir(self.folder)
            if len(path_subdir_list) > 0:
                Console.print(_REPO_STARTER_DEEP_REPO_WARN, folder=self.folder.resolve())
                Console.print(_REPO_STARTER_DEEP_REPO_WARN_2)
                for path in path_subdir_list:
                    Console.print(f"- [r]{path}")
                return False

        return True
    
    def create_empty_repo(self):
        source = self.repo.create_default_sandbox_source()
        self.repo.data.set_remote(source)
        Console.print(_REPO_STARTER_EMPTY_REPO)
