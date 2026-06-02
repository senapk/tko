from pathlib import Path
from tko.play.language_setter import LanguageSetter
from tko.util.rt import RT
from tko.repository.repository import Repository
from tko.repository.repository_paths import RepositoryPaths
import shutil
from tko.config.settings import Settings
from tko.repository.repository_config import RepositoryConfig
from tko.i18n import Msg, t


_REPO_STARTER_LANGUAGE_SET = Msg(
    pt="A linguagem do repositório foi definida como <{language}:y>.",
    en="Repository language set to <{language}:y>.",
)
_REPO_STARTER_OPEN_HINT = Msg(
    pt="Voce pode acessar o repositório com o comando <tko open:g>",
    en="You can access the repository with the command <tko open:g>",
)
_REPO_STARTER_EXISTS = Msg(
    pt="Já existe um repositório TKO na pasta <{folder}:y>",
    en="A TKO repository already exists in folder <{folder}:y>",
)
_REPO_STARTER_RESET_PROMPT = Msg(
    pt="Deseja resetar o repositório? (<s:g>/<n:r>): ",
    en="Do you want to reset the repository? (<y:g>/<n:r>): ",
)
_REPO_STARTER_INSIDE_OTHER_REPO = Msg(
    pt="Você está tentando criar um repositório dentro de outro, pois já existe rep em <{parent}:r>",
    en="You are trying to create a repository inside another one, because there is already a repo in <{parent}:r>",
)
_REPO_STARTER_DEEP_REPO_WARN_2 = Msg(
    pt="Porém já existem repositórios TKO abaixo dessa pasta. Mova ou apague-os",
    en="But there are already TKO repositories below that folder. Move or delete them",
)
_REPO_STARTER_OVERWRITE_PROMPT = Msg(
    pt="Deseja sobrescrever as configurações do repositório em <{folder}:y> ? (<s:g>/<n:r>): ",
    en="Do you want to overwrite the repository settings in <{folder}:y> ? (<y:g>/<n:r>): ",
)
_REPO_STARTER_DEEP_REPO_WARN = Msg(
    pt="Você está tentando criar um repositório TKO na pasta <{folder}:y>",
    en="You are trying to create a TKO repository in folder <{folder}:y>",
)
_REPO_STARTER_EMPTY_REPO = Msg(
    pt="Criando repositório vazio, como pasta para atividades locais",
    en="Creating empty repository, as a folder for local activities",
)

_REPO_ASK_DEFAULT_REMOTES = Msg(
    pt="Você deseja adicionar algum dos repositório padrão de atividades?",
    en="Do you want to add any of the default activity repositories?",
)
_REPO_ASK_DEFAULT_REMOTES_OP1 = Msg(
    pt="Sim, <FUP:g>  - Fundamentos de Programação",
    en="Yes, <FUP:g>  - Programming Fundamentals",
)
_REPO_ASK_DEFAULT_REMOTES_OP2 = Msg(
    pt="Sim, <POO:g>  - Programação Orientada a Objetos",
    en="Yes, <POO:g>  - Object Oriented Programming",
)
_REPO_ASK_DEFAULT_REMOTES_OP3 = Msg(
    pt="Sim, <ED :g>  - Estruturas de Dados",
    en="Yes, <ED :g>  - Data Structures",
)
_REPO_ASK_DEFAULT_REMOTES_OP4 = Msg(
    pt="<Não:g> desejo adicionar nenhum repositório agora, vou adicionar manualmente depois",
    en="<No:g> I don't want to add any repository now, I'll add manually later",
)
_REPO_NONE_ADDED = Msg(
    pt="Nenhum repositório adicionado. Você pode adicionar repositórios depois com o comando ",
    en="No repository added.",
)

_REPO_INVALID_OPTION = Msg(
    pt="Opção inválida. Por favor, escolha uma opção válida.",
    en="Invalid option. Please, choose a valid option.",
)

class RepositoryStarter:
    def __init__(self, settings: Settings, folder: Path | None, language: str | None, skip: bool):
        self.settings = settings
        self.skip = skip
        # if folder is set, use folder, else use local folder.
        self.folder: Path = Path.cwd()
        if folder is not None:
            self.folder = folder
        self.language = language

    def execute(self) -> bool:
        repo = self.create_repository()
        if repo is None:
            return False
        
        self.repo = repo
        self.create_empty_repo()
        # erase cache folder to avoid conflicts
        cache_folder = repo.paths.cache_folder
        if cache_folder.exists():
            shutil.rmtree(cache_folder)
        cache_folder.mkdir(parents=True, exist_ok=True)
        self.language = LanguageSetter.check_lang_in_text_mode(self.settings, self.repo, selected=self.language)
        print(RT.parse(t(_REPO_STARTER_LANGUAGE_SET, language=self.language)))
        
        if not self.skip:
            self.ask_about_default_remotes()

        RepositoryConfig(repo).save()
        self.print_end_msg()
        return True

    def ask_about_default_remotes(self):
        print("\n" + t(_REPO_ASK_DEFAULT_REMOTES))
        print(RT.parse("<1, y>."), RT.parse(t(_REPO_ASK_DEFAULT_REMOTES_OP1)))
        print(RT.parse("<2, y>."), RT.parse(t(_REPO_ASK_DEFAULT_REMOTES_OP2)))
        print(RT.parse("<3, y>."), RT.parse(t(_REPO_ASK_DEFAULT_REMOTES_OP3)))
        print(RT.parse("<4, y>."), RT.parse(t(_REPO_ASK_DEFAULT_REMOTES_OP4)))
        while True: 
            op = input("Escolha uma opção: ")
            if op == "1":
                self.add_remote("fup")
                return
            elif op == "2":
                self.add_remote("poo")
                return
            elif op == "3":
                self.add_remote("ed")
                return
            elif op == "4":
                print(RT.parse(t(_REPO_NONE_ADDED)) + RT.parse(" <$:y>", "tko remote add <label> <url>"))
                return
            else:
                print(RT.parse(t(_REPO_INVALID_OPTION)))

    def add_remote(self, target: str):
        from tko.repository.remote_actions import RemoteActions
        rep_actions = RemoteActions(self.settings, self.repo)
        rep_actions.remote_add(
            name=target,
            remote_default=target, 
        )
        rep_actions.print_end_msg()

    def print_end_msg(self):
        print(RT.parse(t(_REPO_STARTER_OPEN_HINT)))
    
    def create_repository(self) -> Repository | None:
        path_parents = RepositoryPaths.rec_search_for_repo_parents(self.folder)

        if path_parents is not None and path_parents.resolve() == self.folder.resolve():
            print(RT.parse(t(_REPO_STARTER_EXISTS, folder=self.folder.resolve())))
            print(RT.parse(t(_REPO_STARTER_RESET_PROMPT)), end="")
            op = input()
            if op == "n":
                return None

        elif path_parents is not None:
            if self.folder != path_parents:
                print(RT.parse(t(_REPO_STARTER_INSIDE_OTHER_REPO, parent=path_parents)))
                print(RT.parse(t(_REPO_STARTER_DEEP_REPO_WARN_2)))
            self.folder = path_parents
            print(RT.parse(t(_REPO_STARTER_OVERWRITE_PROMPT, folder=self.folder)), end="")
            op = input()
            if op == "n":
                return None
        else:
            path_subdir_list = RepositoryPaths.rec_search_for_repo_subdir(self.folder)
            if len(path_subdir_list) > 0:
                print(RT.parse(t(_REPO_STARTER_DEEP_REPO_WARN, folder=self.folder.resolve())))
                print(RT.parse(t(_REPO_STARTER_DEEP_REPO_WARN_2)))
                for path in path_subdir_list:
                    print(RT.parse("- <$:r>", path))
                return None

        return Repository(self.folder)
    
    def create_empty_repo(self):
        source = self.repo.create_default_sandbox_source()
        self.repo.data.set_remote(source)
        print(RT.parse(t(_REPO_STARTER_EMPTY_REPO)))
