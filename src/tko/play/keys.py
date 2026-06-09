from tko.i18n import Msg


class GuiActions:
    create_draft = Msg(pt="Criar Rascunho", en="Create Draft")
    tab = Msg(pt="↔TAB", en="↔TAB")
    leave = Msg(pt="Sair [esc]", en="Quit [esc]")
    edit = Msg(pt="Ver tarefa", en="View task")
    show_time = Msg(pt="Tempo", en="Time")
    filter = Msg(pt="Filtrar", en="Filter")
    principal = Msg(pt="Principal", en="Main")
    github = Msg(pt="Web", en="Web")
    help = Msg(pt="Ajuda", en="Help")
    download = Msg(pt="Baixar", en="Download")
    activate = Msg(pt="Ativar", en="Activate")
    navigate = Msg(pt="←↓→", en="←↓→")
    uncheck = Msg(pt="Desmarcar", en="Uncheck")
    search = Msg(pt="Busca", en="Search")
    goback = Msg(pt="Tela Anterior[Esc]", en="Previous Screen[Esc]")
    pallete = Msg(pt="Paleta", en="Palette")
    grade = Msg(pt="Auto Avaliação", en="Self Evaluation")
    time_limit = Msg(pt="Limite de tempo", en="Time limit")
    evaluate_tester = Msg(pt="Testar", en="Test")
    execute_tester = Msg(pt="Executar", en="Run")
    calibrate = Msg(pt="Calibrar teclas", en="Calibrate keys")
    draft = Msg(pt="Rascunho", en="Draft")
    all = Msg(pt="Todos", en="All")

class GuiKeys:
    calibrate = "c"

    inbox = "1"
    all_tasks = "2"
    
    panel_graph = "3"
    panel_logs = "4"
    panel_skills = "5"
    panel_help = "6"
    panel_toggle = " "

    show_duration = "T"

    panel_resize_inc = ">"
    panel_resize_dec = "<"
    palette = "p"
    images = "I"
    down_task = "b"
    activate = "\n"
    reload_game = "R"
    
    expand_all = ']'
    collapse_all = "["
    create_draft = "r"
    set_lang_drafts = "L"
    toggle_ui_language = "P"
    open_url = "u"
    key_quit = "q"
    edit= "v"
    colors = "C"
    search = "/"
    self_evaluate = "a"
    self_evaluate_full = "A"
    delete_folder = "D"
    diff = "d"
    unfold_patch = "V"
    execute = "e"
    evaluate = "t"
    toggle_main = "\t"
    lock = "u"
    limite  = "l"
