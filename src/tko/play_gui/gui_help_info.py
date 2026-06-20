from tko.play.gui_keys import GuiKeys
from tko.i18n import Msg
from tko.util.rt import RT
from tko.util.symbols import Symbols


class _GuiHelpMsg:
    SECTION_CONFIG = Msg.parse(pt="[g] Configuração []", en="[g] Configuration [g]")

    CALIBRATE_LINE = Msg.parse(pt=" Calibrar [r]{}[] Para calibrar os direcionais do teclado", 
                         en=" Calibrate [r]{}[] To calibrate the keyboard arrow keys")

    SECTION_SYMBOLS = Msg.text(pt=" Símbolos ", en=" Symbols ")
    SYMBOL_STUDY_WRITE_NOHELP = Msg.parse(pt=" [g]{}[] Estudo/Consulta, [y]{}[] Escrever e refazer, [r]{}[] Fazer sem consulta", 
                                    en=" [g]{}[] Study/Consult, [y]{}[] Write and redo, [r]{}[] Do without help")
    SYMBOL_SELF_EVAL = Msg.parse(
        pt=" [g]{} {} {}[] Fez Autoavaliação       , [r]{} {} {}[] Sem Autoavaliação",
        en=" [g]{} {} {}[] Self evaluation done       , [r]{} {} {}[] No self evaluation",
    )

    SECTION_NAVIGATION = Msg.text(pt=" Navegação ", 
                             en=" Navigation ")
    NAV_ARROWS = Msg.parse(pt="  setas [r]{}[] Para navegar entre os elementos", 
                     en="  arrows [r]{}[] To navigate between elements")
    NAV_ENTER = Msg.parse(pt="    Enter [r]{}[] Interage com o elemento de acordo com o contexto", 
                    en="    Enter [r]{}[] Interacts with the element depending on context")

    SECTION_INTERFACE = Msg.text(pt=" Interface ", 
                            en=" Interface ")
    INTERFACE_INBOX = Msg.parse(pt="    Inbox [r]{}[] Mostra as tarefas sugeridas e iniciadas", 
                          en="    Inbox [r]{}[] Shows suggested and started tasks")
    INTERFACE_ALL = Msg.parse(pt="    Todas [r]{}[] Mostra as todas tarefas cadastradas", 
                        en="    All [r]{}[] Shows all registered tasks")
    INTERFACE_PALETTE = Msg.parse(pt="   Paleta [r]{}[] Abre o menu de ações e configurações", 
                            en="  Palette [r]{}[] Opens the actions and settings menu")
    INTERFACE_TIME = Msg.parse(pt="    Tempo [r]{}[] Mostrar/Oculta o tempo gasto nas tarefas", 
                         en="     Time [r]{}[] Shows/Hides the time spent on tasks")
    INTERFACE_SEARCH = Msg.parse(pt="    Busca [r]{}[] Abre a barra de pesquisa", 
                           en="   Search [r]{}[] Opens the search bar")

    SECTION_TASKS = Msg.text(pt=" Tarefas ", en=" Tasks ")
    TASK_DOWNLOAD = Msg.parse(pt=" Download [r]{}[] Baixa novamente a tarefa selecionada", 
                        en=" Download [r]{}[] Downloads the selected task again")
    TASK_DELETE = Msg.parse(pt="   Apagar [r]{}[] Apaga a pasta da tarefa selecionada", 
                      en="   Delete [r]{}[] Deletes the selected task folder")
    TASK_DRAFT = Msg.parse(pt=" Rascunho [r]{}[] Cria um rascunho para escrever código ou anotações", 
                     en="    Draft [r]{}[] Creates a draft for code or notes")
    TASK_EVALUATION = Msg.parse(pt="Avaliação [r]{}[] Abre tela para auto avaliação", 
                          en=" Evaluate [r]{}[] Opens self-evaluation screen")

    SECTION_DEFAULT_EDITOR = Msg.text(pt=" Editor padrão ", 
                                 en=" Default editor ")
    EDITOR_DESC = Msg.parse(pt=" Para mudar o editor padrão para abrir arquivos use o comando", 
                      en=" To change the default editor used to open files, run")
    EDITOR_COMMAND = Msg.parse(pt="tko config set --editor <comando>", 
                         en="tko config set --editor <command>")


class GuiHelpInfo:

    @staticmethod
    def show() -> list[RT]:
        help_lines: list[RT] = []
        dx = 65
        help_lines.append(_GuiHelpMsg.SECTION_CONFIG.t().center(dx, RT("-")))
        help_lines.append(_GuiHelpMsg.CALIBRATE_LINE.t().format(GuiKeys.calibrate))

        help_lines.append(_GuiHelpMsg.SECTION_SYMBOLS.t().set_style("g").center(dx, RT("-")))
        help_lines.append(_GuiHelpMsg.SYMBOL_STUDY_WRITE_NOHELP.t().format(Symbols.loss_free, Symbols.loss_part, Symbols.loss_zero))
        help_lines.append(_GuiHelpMsg.SYMBOL_SELF_EVAL.t().format(
            Symbols.diamond_filled, Symbols.circle_filled, Symbols.task_view,
            Symbols.diamond_void, Symbols.circle_void, Symbols.task_view))
        help_lines.append(_GuiHelpMsg.SECTION_NAVIGATION.t().set_style("g").center(dx, RT("-")))
        help_lines.append(_GuiHelpMsg.NAV_ARROWS.t().format("↑↓→"))
        help_lines.append(_GuiHelpMsg.NAV_ENTER.t().format("↲"))
        help_lines.append(_GuiHelpMsg.SECTION_INTERFACE.t().set_style("g").center(dx, RT("-")))
        help_lines.append(_GuiHelpMsg.INTERFACE_INBOX.t().format(GuiKeys.inbox))
        help_lines.append(_GuiHelpMsg.INTERFACE_ALL.t().format(GuiKeys.all_tasks))
        help_lines.append(_GuiHelpMsg.INTERFACE_PALETTE.t().format(GuiKeys.palette))
        help_lines.append(_GuiHelpMsg.INTERFACE_TIME.t().format(GuiKeys.show_duration))
        help_lines.append(_GuiHelpMsg.INTERFACE_SEARCH.t().format(GuiKeys.search))

        help_lines.append(_GuiHelpMsg.SECTION_TASKS.t().set_style("g").center(dx, RT("-")))
        help_lines.append(_GuiHelpMsg.TASK_DOWNLOAD.t().format(GuiKeys.down_task))
        help_lines.append(_GuiHelpMsg.TASK_DELETE.t().format(GuiKeys.delete_folder))
        help_lines.append(_GuiHelpMsg.TASK_DRAFT.t().format(GuiKeys.create_draft))
        help_lines.append(_GuiHelpMsg.TASK_EVALUATION.t().format(GuiKeys.self_evaluate))

        help_lines.append(_GuiHelpMsg.SECTION_DEFAULT_EDITOR.t().set_style("g").center(dx, RT("-")))
        help_lines.append(_GuiHelpMsg.EDITOR_DESC.t())
        help_lines.append(_GuiHelpMsg.EDITOR_COMMAND.t().set_style("y").center(dx))

        return help_lines
