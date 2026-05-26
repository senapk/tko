from tko.widget.frame import Frame
from tko.play.keys import GuiKeys
from tko.i18n import Msg, t
from tko.util.rt import RT
from tko.util.symbols import Symbols


class _GuiHelpMsg:
    SECTION_CONFIG = Msg(pt=" Configuração ", en=" Configuration ")

    CALIBRATE_LINE = Msg(pt=" Calibrar <$:r> Para calibrar os direcionais do teclado", en=" Calibrate <$:r> To calibrate the keyboard arrow keys")

    SECTION_SYMBOLS = Msg(pt=" Símbolos ", en=" Symbols ")
    SYMBOL_STUDY_WRITE_NOHELP = Msg(pt=" <$:g> Estudo/Consulta, <$:y> Escrever e refazer, <$:r> Fazer sem consulta", en=" <$:g> Study/Consult, <$:y> Write and redo, <$:r> Do without help")
    SYMBOL_SELF_EVAL = Msg(
        pt=" <$:g> <$:g> <$:g> Fez Autoavaliação       , <$> <$> <$> Sem Autoavaliação",
        en=" <$:g> <$:g> <$:g> Self evaluation done       , <$> <$> <$> No self evaluation",
    )

    SECTION_NAVIGATION = Msg(pt=" Navegação ", en=" Navigation ")
    NAV_ARROWS = Msg(pt="  setas <$:r> Para navegar entre os elementos", en="  arrows <$:r> To navigate between elements")
    NAV_ENTER = Msg(pt="    Enter <$:r> Interage com o elemento de acordo com o contexto", en="    Enter <$:r> Interacts with the element depending on context")

    SECTION_INTERFACE = Msg(pt=" Interface ", en=" Interface ")
    INTERFACE_INBOX = Msg(pt="    Inbox <$:r> Mostra as tarefas sugeridas e iniciadas", en="    Inbox <$:r> Shows suggested and started tasks")
    INTERFACE_ALL = Msg(pt="    Todas <$:r> Mostra as todas tarefas cadastradas", en="      All <$:r> Shows all registered tasks")
    INTERFACE_PALETTE = Msg(pt="   Paleta <$:r> Abre o menu de ações e configurações", en="  Palette <$:r> Opens the actions and settings menu")
    INTERFACE_TIME = Msg(pt="    Tempo <$:r> Mostrar/Oculta o tempo gasto nas tarefas", en="     Time <$:r> Shows/Hides the time spent on tasks")
    INTERFACE_SEARCH = Msg(pt="    Busca <$:r> Abre a barra de pesquisa", en="   Search <$:r> Opens the search bar")

    SECTION_TASKS = Msg(pt=" Tarefas ", en=" Tasks ")
    TASK_DOWNLOAD = Msg(pt=" Download <$:r> Baixa novamente a tarefa selecionada", en=" Download <$:r> Downloads the selected task again")
    TASK_DELETE = Msg(pt="   Apagar <$:r> Apaga a pasta da tarefa selecionada", en="   Delete <$:r> Deletes the selected task folder")
    TASK_DRAFT = Msg(pt=" Rascunho <$:r> Cria um rascunho para escrever código ou anotações", en="    Draft <$:r> Creates a draft for code or notes")
    TASK_EVALUATION = Msg(pt="Avaliação <$:r> Abre tela para auto avaliação", en=" Evaluate <$:r> Opens self-evaluation screen")

    SECTION_DEFAULT_EDITOR = Msg(pt=" Editor padrão ", en=" Default editor ")
    EDITOR_DESC = Msg(pt=" Para mudar o editor padrão para abrir arquivos use o comando", en=" To change the default editor used to open files, run")
    EDITOR_COMMAND = Msg(pt="tko config set --editor <comando>", en="tko config set --editor <command>")


class GuiHelpPanel:

    def show(self, frame: Frame) -> None:
        frame.draw()
        dx = frame.get_dx() - 2
        help_lines: list[RT] = []
        help_lines.append(RT(t(_GuiHelpMsg.SECTION_CONFIG), "g").center(dx, RT("-")))
        help_lines.append(RT.parse(t(_GuiHelpMsg.CALIBRATE_LINE), GuiKeys.calibrate))

        help_lines.append(RT(t(_GuiHelpMsg.SECTION_SYMBOLS), "g").center(dx, RT("-")))
        help_lines.append(RT.parse(t(_GuiHelpMsg.SYMBOL_STUDY_WRITE_NOHELP), Symbols.loss_free, Symbols.loss_part, Symbols.loss_zero))
        help_lines.append(RT.parse(t(_GuiHelpMsg.SYMBOL_SELF_EVAL),
                                       Symbols.diamond_filled, Symbols.circle_filled, Symbols.task_view,
                                       Symbols.diamond_void, Symbols.circle_void, Symbols.task_view))
        help_lines.append(RT(t(_GuiHelpMsg.SECTION_NAVIGATION), "g").center(dx, RT("-")))
        help_lines.append(RT.parse(t(_GuiHelpMsg.NAV_ARROWS), "↑↓→"))
        help_lines.append(RT.parse(t(_GuiHelpMsg.NAV_ENTER), "↲"))
        help_lines.append(RT(t(_GuiHelpMsg.SECTION_INTERFACE), "g").center(dx, RT("-")))
        help_lines.append(RT.parse(t(_GuiHelpMsg.INTERFACE_INBOX), GuiKeys.inbox))
        help_lines.append(RT.parse(t(_GuiHelpMsg.INTERFACE_ALL), GuiKeys.all_tasks))
        help_lines.append(RT.parse(t(_GuiHelpMsg.INTERFACE_PALETTE), GuiKeys.palette))
        help_lines.append(RT.parse(t(_GuiHelpMsg.INTERFACE_TIME), GuiKeys.show_duration))
        help_lines.append(RT.parse(t(_GuiHelpMsg.INTERFACE_SEARCH), GuiKeys.search))

        help_lines.append(RT(t(_GuiHelpMsg.SECTION_TASKS), "g").center(dx, RT("-")))
        help_lines.append(RT.parse(t(_GuiHelpMsg.TASK_DOWNLOAD), GuiKeys.down_task))
        help_lines.append(RT.parse(t(_GuiHelpMsg.TASK_DELETE), GuiKeys.delete_folder))
        help_lines.append(RT.parse(t(_GuiHelpMsg.TASK_DRAFT), GuiKeys.create_draft))
        help_lines.append(RT.parse(t(_GuiHelpMsg.TASK_EVALUATION), GuiKeys.self_evaluate))

        help_lines.append(RT(t(_GuiHelpMsg.SECTION_DEFAULT_EDITOR), "g").center(dx, RT("-")))
        help_lines.append(RT(t(_GuiHelpMsg.EDITOR_DESC)))
        help_lines.append(RT(t(_GuiHelpMsg.EDITOR_COMMAND), "y").center(dx))

        for i, line in enumerate(help_lines):
            frame.write(i, 0, line)
