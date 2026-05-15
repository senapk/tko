
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