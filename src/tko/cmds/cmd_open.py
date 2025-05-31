from tko.settings.settings import Settings
from tko.settings.repository import Repository
from tko.play.play import Play
from tko.settings.logger import Logger
from tko.util.text import Text, aprint

class CmdOpen:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.need_update = False
        self.rep: Repository | None = None
        self.folder = ""

    def set_need_update(self):
        self.need_update = True

    def load_folder(self, folder: str):
        self.folder = folder
        self.rep = Repository(folder)
        if not self.rep.has_local_config_file():
            aprint(Text.format("{r}: O parâmetro para o comando {g} {y} deve a pasta onde você iniciou o repositório.", "Erro", "tko open", "<pasta>"))
            aprint(Text.format("{g}: Navegue ou passe o caminho até a pasta do repositório e tente novamente.", "Ação"))
            aprint(Text.format("{g}: Ou use {y} para criar um novo repositório.", "Ação","tko init --remote [fup|poo|ed]"))
            raise Warning(Text.format("{r}: {y} {}", "Erro:", folder, "não contém um repositório do tko"))
        self.rep.load_config().load_game()
        return self


    def execute(self):
        if self.rep is None:
            raise Warning("Repositório não encontrado")
        Logger.instance = Logger(self.rep)
        logger: Logger = Logger.get_instance()
        logger.set_log_files(self.rep.get_history_file(), self.rep.get_track_folder())
        logger.record_open()
        play = Play(self.settings, self.rep)
        if self.need_update:
            play.set_need_update()
        play.play()
        logger.record_quit()
