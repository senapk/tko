from tko.play.frame import Frame
from tko.play.keys import GuiKeys
from tko.util.rtext import RText
from tko.util.symbols import Symbols


class GuiHelpPanel:

    def show(self, frame: Frame) -> None:
        frame.draw()
        dx = frame.get_dx() - 2
        help_lines: list[RText] = []
        help_lines.append(RText.format("{g}", " Configuração ").center(dx, RText("-")))
        help_lines.append(RText.format("   Bordas {r} Habilita {r}{R}{r}", "B", "", "bordas redondas", ""))
        help_lines.append(RText.format(" Calibrar {r} Para calibrar os direcionais do teclado", GuiKeys.calibrate))

        help_lines.append(RText(" Símbolos ", "g").center(dx, RText("-")))
        help_lines.append(RText.format(" {y} Tarefa sugeridas, {} Tarefa opcional", Symbols.star_filled, Symbols.star_void))
        help_lines.append(RText.format(" {g} Estudo/Consulta, {y} Escrever e refazer, {r} Fazer sem consulta", Symbols.loss_free, Symbols.loss_part, Symbols.loss_zero))
        help_lines.append(RText.format(" {g}{g}{g} Fez Autoavaliação       , {}{}{} Sem Autoavaliação",
                                       Symbols.diamond_filled, Symbols.circle_filled, Symbols.task_view,
                                       Symbols.diamond_void, Symbols.circle_void, Symbols.task_view))
        help_lines.append(RText.format("{g}", " Navegação ").center(dx, RText("-")))
        help_lines.append(RText.format("  setas {r} Para navegar entre os elementos", "↑↓→"))
        help_lines.append(RText.format("    Enter {r} Interage com o elemento de acordo com o contexto", "↲"))
        help_lines.append(RText(" Interface ", "g").center(dx, RText("-")))
        help_lines.append(RText.format("    Inbox {r} Mostra as tarefas sugeridas e iniciadas", GuiKeys.inbox))
        help_lines.append(RText.format("    Todas {r} Mostra as todas tarefas cadastradas", GuiKeys.all_tasks))
        help_lines.append(RText.format("   Paleta {r} Abre o menu de ações e configurações", GuiKeys.palette))
        help_lines.append(RText.format("    Tempo {r} Mostrar/Oculta o tempo gasto nas tarefas", GuiKeys.show_duration))
        help_lines.append(RText.format("    Busca {r} Abre a barra de pesquisa", GuiKeys.search))

        help_lines.append(RText(" Tarefas ", "g").center(dx, RText("-")))
        help_lines.append(RText.format(" Download {r} Baixa novamente a tarefa selecionada", GuiKeys.down_task))
        help_lines.append(RText.format("   Apagar {r} Apaga a pasta da tarefa selecionada", GuiKeys.delete_folder))
        help_lines.append(RText.format(" Rascunho {r} Cria um rascunho para escrever código ou anotações", GuiKeys.create_draft))
        help_lines.append(RText.format("Avaliação {r} Abre tela para auto avaliação", GuiKeys.self_evaluate))

        help_lines.append(RText.format("{g}", " Editor padrão ").center(dx, RText("-")))
        help_lines.append(RText(" Para mudar o editor padrão para abrir arquivos use o comando"))
        help_lines.append(RText("tko config set --editor <comando>", "y").center(dx))

        for i, line in enumerate(help_lines):
            frame.write(i, 0, line)
