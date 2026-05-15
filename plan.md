## Mapa de Acoplamentos Críticos

### 🔴 P1 — Violação de camada (architecture smell)

#### 1. repository.py importa `play.flags`
```python
# src/tko/repository/repository.py
from tko.play.flags import Flags
```
`Repository` é entidade de domínio puro (persistência, git, game). Ela não deve conhecer nada de UI. `Flags` é estado de apresentação (painel, modo inbox, etc.).  
**Risco**: qualquer mudança em `play.flags` quebra o domínio.  
**Solução**: mover `Flags` para `tko.config.flags` ou `tko.game.view_state`, ou separar serialização de Flags do Repository.

---

### 🔴 P2 — God Class

#### 2. `play/play_actions.py` (382 linhas)
Mistura de 7+ responsabilidades distintas:

| Grupo | Métodos |
|---|---|
| Navegação/tarefa | `select_task`, `select_task_action`, `run_selected_task` |
| Download | `down_remote_task`, `__down_remote_task` |
| Criação | `create_draft` |
| Arquivo/editor | `open_code`, `open_link`, `open_versions` |
| Avaliação | `self_evaluate`, `self_evaluate_full` |
| UI/config | `resize_panels`, `reload`, `delete_folder_ask` |
| Log | `register_action` |

Recebe `Gui` inteiro para extrair 6 dependências (`app`, `settings`, `fman`, `repo`, `tree`, `game`).  
**Risco**: classe afetada por qualquer mudança em qualquer subsistema da UI.

---

### 🟡 P3 — Mutable Bag / Feature Envy

#### 3. `run/run_context.py`
Objeto com 12 flags booleanas/estado mutável espalhado por toda a pipeline `run`:
```
curses_mode, run_without_ask, show_track_info, show_self_info,
eval_mode, complex_percent, abord_on_exec_error, no_run,
timeout, repo, task, track_folder, opener
```
Mistura **config imutável** (timeout, eval_mode) com **estado descoberto** (repo, task, opener).  
**Risco**: qualquer serviço pode mutar ctx causando bugs difíceis de rastrear.

---

### 🟡 P4 — Mistura de presentation + business

#### 4. `run/run_executor.py`
`_run_all_tests_top_line()` mistura `print()` diretamente com iteração de testes e cálculo de taxa:
```python
print("[", end="")  # render
unit.result = UnitRunner.run_unit(...)  # business
print(ExecutionResult.get_symbol(...))  # render
```
`run_tests()` decide o modo de execução (curses × raw terminal) mas não separa as responsabilidades de cada modo.  
**Risco**: impossível testar lógica de execução sem capturar stdout.

---

### 🟡 P5 — Dispatch manual sem extensibilidade

#### 5. `run/solver_builder.py` (258 linhas)
`prepare_exec()` com `if/elif` por extensão de arquivo (`mk`, `yaml`, `ts`, extensão registrada, default):
```python
if first.suffix == ".mk": self.__prepare_make()
elif first.suffix == ".yaml": self.__prepare_yaml()
elif first.suffix == ".ts": self.__prepare_ts()
elif first.suffix[1:] in settings...: self.prepare_exec_with_lang()
else: ...
```
`__prepare_ts()` contém 50+ linhas de lógica TypeScript-específica incluindo **injeção de código TS inline** (o literal `input_cmd`).  
**Risco**: adicionar nova linguagem especial exige alterar solver_builder inteiro.

---

### 🟢 P6 — Acoplamento cruzado de domínio

#### 6. run_executor.py → `Tester` diretamente
```python
from tko.tester import Tester
...
cdiff = Tester(self.ctx.settings, self.ctx.repo, self.ctx.wdir, self.ctx.get_task())
```
`RunExecutor` (camada de execução de linha de comando) instancia `Tester` (UI TUI completo). Isso acopla o fluxo CLI com o TUI, dificultando testar ou substituir o modo curses.

---

## Plano Priorizado

### Wave 1 — Quebrar violação de camada (P1)
**Módulos**: repository.py, `play/flags.py`

1. Mover `Flags` para `tko.config.flags` (sem dependência de play)
2. Atualizar todos os imports
3. Validar com grep global + pytest

---

### Wave 2 — Decompor play_actions.py (P2)
**Módulos**: `play/play_actions.py` → 4 serviços

| Novo arquivo | Responsabilidade |
|---|---|
| `play/task_launcher.py` | `select_task`, `select_task_action`, `run_selected_task` |
| `play/task_download_service.py` | `down_remote_task`, `__down_remote_task` |
| `play/draft_creator.py` | `create_draft` |
| `play/task_editor_service.py` | `open_code`, `open_link`, `open_versions` |
| `play/play_actions.py` | reduz para fachada de wiring + `self_evaluate`, `reload`, `resize_panels`, `delete_folder_ask` |

---

### Wave 3 — Separar RunContext: config × estado (P3)
**Módulos**: `run/run_context.py` → 2 objetos

| Novo objeto | Conteúdo |
|---|---|
| `RunConfig` (imutável) | `curses_mode`, `eval_mode`, `timeout`, `abord_on_exec_error`, `no_run`, `show_track_info`, `show_self_info`, `complex_percent` |
| `RunContext` (estado) | `wdir`, `repo`, `task`, `opener`, `track_folder`, `lang`, `target_list` |

`RunContext` passa a receber `RunConfig` em vez de acumular flags.

---

### Wave 4 — Separar render de execução no RunExecutor (P4)
**Módulos**: `run/run_executor.py` → 2 serviços

| Novo arquivo | Responsabilidade |
|---|---|
| `run/test_loop_service.py` | iteração e coleta de resultados (sem print) |
| `run/run_presenter.py` (já existe, expandir) | formatação de output raw terminal |
| `run/run_executor.py` | orquestra os dois + decide modo curses × raw |

---

### Wave 5 — Strategy pattern em SolverBuilder (P5)
**Módulos**: `run/solver_builder.py` → estratégias por tipo

| Novo arquivo | Responsabilidade |
|---|---|
| `run/build/make_builder.py` | build de `.mk` |
| `run/build/yaml_builder.py` | build de `.yaml` |
| `run/build/ts_builder.py` | build de `.ts` (inclui injeção de input) |
| `run/build/lang_builder.py` | build de linguagem registrada |
| `run/solver_builder.py` | factory que delega ao strategy correto |

---

### Wave 6 — Desacoplar RunExecutor do Tester (P6)
**Módulo**: `run/run_executor.py`

Extrair `CursesModeRunner` ou usar uma interface `TesterRunner` que `RunExecutor` recebe por injeção — assim CLI não importa UI TUI diretamente.

---

## Sequência sugerida de execução

```
Wave 1  →  Wave 2  →  Wave 3  →  Wave 4  →  Wave 5  →  Wave 6
(~30min)   (~45min)   (~30min)   (~30min)   (~45min)   (~20min)
```

Posso implementar a **Wave 1** agora, já que é cirúrgica (mover `Flags` para fora de `play`) e resolve a violação de camada mais grave. Deseja começar por ela ou escolher outra wave?

Completed: *Extract frame loop from Tester* (5/5)