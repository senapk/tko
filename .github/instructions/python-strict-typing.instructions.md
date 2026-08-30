---
name: python-strict-typing
description: "Enforce Python Pylance strict type checking for all code in the TKO project. Use when: writing or reviewing Python code (*.py files); creating new classes, functions, methods, or fixtures; ensuring type safety and domain/interface separation; catching type errors early in development."
applyTo: "src/**/*.py,tests/**/*.py"
---

# Python Strict Type Checking (Pylance Mode)

All Python code in this project **must comply with Pylance strict type mode**. This ensures:
- Early type error detection
- Better domain/interface separation (pure domain logic has no I/O types)
- Improved testability through explicit interfaces
- Clear architectural boundaries between layers

## Mandatory Rules

### 1. **No String Type Annotations**
❌ **Wrong:**
```python
def get_report() -> "ExecutionReport":
    return ExecutionReport()

def handle_error(err: "RuntimeError | None") -> None:
    pass
```

✅ **Correct:**
```python
def get_report() -> ExecutionReport:
    return ExecutionReport()

def handle_error(err: RuntimeError | None) -> None:
    pass
```

**Why:** String annotations cause `unknown` type errors in strict mode. Always use direct imports.

### 2. **Explicit Return Types on ALL Methods/Functions**
❌ **Wrong:**
```python
def set_name(self, name: str):  # Missing return type
    self.name = name

def get_value(self):  # Missing return type
    return self.value
```

✅ **Correct:**
```python
def set_name(self, name: str) -> None:  # Explicit void return
    self.name = name

def get_value(self) -> int:  # Explicit return type
    return self.value

def set_config(self, config: RunConfig) -> RunContext:  # Fluent API pattern
    self.config = config
    return self
```

**Why:** Pylance strict mode requires explicit return types. This also clarifies fluent API patterns.

### 3. **Direct Imports, No TYPE_CHECKING Guards**
❌ **Wrong:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tko.run.solver_builder import SolverBuilder

# ...later in code...
solver: "SolverBuilder | None" = wdir.solver  # String quote + getattr
```

✅ **Correct:**
```python
from tko.run.solver_builder import SolverBuilder

# ...later in code...
solver: SolverBuilder | None = wdir.solver  # Direct import, direct access
```

**Why:** String annotations and deferred imports cause circular import detection issues. Direct imports resolve correctly.

### 4. **Use Union Operator `|` Instead of `Union[]`**
❌ **Wrong:**
```python
from typing import Union

def process(value: Union[int, str, None]) -> Union[bool, None]:
    pass
```

✅ **Correct:**
```python
def process(value: int | str | None) -> bool | None:
    pass
```

**Why:** Python 3.10+ supports the `|` operator, which is more readable and strict-mode compliant.

### 5. **No `Any` Type for Domain Objects**
❌ **Wrong:**
```python
solver: Any = getattr(wdir, "solver", None)
```

✅ **Correct:**
```python
solver: SolverBuilder | None = wdir.solver
```

**Why:** `Any` defeats type checking. Use the actual field type from the class definition.

### 6. **Dataclass Fields Must Have Type Annotations**
❌ **Wrong:**
```python
from dataclasses import dataclass

@dataclass
class RunConfig:
    no_run = False  # Missing type
    timeout = 30    # Missing type
```

✅ **Correct:**
```python
from dataclasses import dataclass

@dataclass
class RunConfig:
    no_run: bool = False
    timeout: int = 30
```

**Why:** Dataclass fields without type annotations are silently ignored by type checkers.

### 7. **Fixture Functions Must Return Explicit Types**
❌ **Wrong:**
```python
@pytest.fixture
def fman():  # Missing return type
    return _DummyFloatingManager()

def test_something(fman):  # Missing type annotation
    pass
```

✅ **Correct:**
```python
@pytest.fixture
def fman() -> _DummyFloatingManager:  # Explicit return type
    return _DummyFloatingManager()

def test_something(fman: _DummyFloatingManager) -> None:  # Explicit parameter type
    pass
```

**Why:** Pytest fixtures without type hints create `unknown` types in strict mode.

### 8. **No Lambdas With Unknown Parameter Types**
❌ **Wrong:**
```python
monkeypatch.setattr("builtins.input", lambda _prompt: "n")
resolver = SimpleNamespace(target_file=lambda _task: missing_readme)
```

✅ **Correct:**
```python
def decline_removal(_prompt: str = "") -> str:
    return "n"

def target_file(_task: Task) -> Path:
    return missing_readme

monkeypatch.setattr("builtins.input", decline_removal)
resolver = SimpleNamespace(target_file=target_file)
```

**Why:** A lambda parameter without a known contextual type produces `reportUnknownLambdaType`. Use a named local function with explicit parameter and return annotations. Lambdas are allowed only when every parameter type is inferred from a fully typed callable context.

### 9. **Mock/Cast Arguments Must Be Properly Typed**
❌ **Wrong:**
```python
from unittest.mock import MagicMock
from typing import Any, cast

repo = MagicMock()  # Creates untyped mock
resolver = cast(Any, resolver)  # Cast to Any defeats typing
```

✅ **Correct:**
```python
from types import SimpleNamespace
from typing import cast

repo = SimpleNamespace(remotes={"labs": remote})  # Properly structured namespace
resolver = cast(ResolverType, resolver)  # Cast to specific type
```

**Why:** Untyped mocks and `Any` casts cause type errors. Use `SimpleNamespace` with proper field structure.

### 9. **Immutable Data Objects Use Frozen Dataclasses**
❌ **Wrong:**
```python
class RunProgress:
    def __init__(self, percent: int):
        self.percent = percent  # Mutable, no validation
```

✅ **Correct:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RunProgress:
    percent: int

    @classmethod
    def from_units(cls, units: list[Unit], no_run: bool) -> RunProgress:
        count = sum(1 for u in units if u.result == ExecutionResult.SUCCESS)
        percent = (count * 100) // len(units) if units and not no_run else 0
        return cls(percent)
```

**Why:** Frozen dataclasses prevent accidental mutation and make type contracts explicit.

### 10. **Collection Type Hints Must Specify Element Types**
❌ **Wrong:**
```python
def get_units(self) -> list:  # Missing element type
    return self.units

def get_results(self) -> dict:  # Missing key/value types
    return self.results
```

✅ **Correct:**
```python
def get_units(self) -> list[Unit]:  # Explicit element type
    return self.units

def get_results(self) -> dict[str, ExecutionResult]:  # Explicit key/value types
    return self.results
```

**Why:** Untyped collections are treated as containing `Unknown` elements in strict mode.

## Architectural Pattern: Strict Type Boundaries

Use types to enforce layer boundaries:

### Domain Layer (Pure Logic)
```python
@dataclass(frozen=True)
class ExecutionReport:
    """Pure data object - no I/O, no side effects"""
    summary: RunExecutionSummary
    units: list[Unit]
    
    def get_failed_units(self) -> list[Unit]:
        return [u for u in self.units if u.result != ExecutionResult.SUCCESS]
```

### Application Layer (Orchestration)
```python
class RunExecutor:
    """Coordinates domain objects with infrastructure"""
    def __init__(self, ctx: RunContext) -> None:
        self.ctx = ctx
    
    def get_report(self) -> ExecutionReport:
        summary = RunExecutionSummary.from_wdir(self.ctx.wdir, self.ctx.no_run)
        return ExecutionReport.from_execution(summary, self.ctx.units, ...)
```

### Infrastructure Layer (I/O & External Systems)
```python
class RunTracker:
    """Handles persistence - receives typed data objects"""
    def persist(self, report: ExecutionReport) -> None:
        if ExecutionOrchestrator.should_persist_execution(report):
            self._write_to_file(report)
```

### Interface Layer (CLI/Console)
```python
class RunPresenter:
    """Displays data - receives typed presentation objects"""
    def show_results(self, report: ExecutionReport) -> None:
        for unit in report.get_failed_units():
            self.console.print(f"Failed: {unit.name}")
```

## Validation: Running Pylance Strict

In **VS Code**, add to `.vscode/settings.json`:
```json
{
  "python.linting.pylanceArgs": [
    "--pythonversion=3.14",
    "--typeCheckingMode=strict"
  ]
}
```

Or in **pyproject.toml** (Pylance reads this):
```toml
[tool.pylance]
pythonVersion = "3.14"
typeCheckingMode = "strict"
```

Run pytest with type checking:
```bash
. .venv/bin/activate
python -m pytest -q  # All tests must pass
```

## Checklist: Before Committing

- [ ] All functions/methods have explicit return types
- [ ] No string type annotations (`"ClassName"` → `ClassName`)
- [ ] No `Any` or `TYPE_CHECKING` imports for domain objects
- [ ] Collection types specify elements: `list[T]`, `dict[K, V]`
- [ ] Fixtures have return type annotations
- [ ] Mock objects use `SimpleNamespace` with proper structure, not `MagicMock` with `Any`
- [ ] Dataclass fields have type annotations
- [ ] Data objects use frozen dataclasses
- [ ] Tests pass: `pytest -q`

## Common Fixes

| Error | Fix |
|-------|-----|
| `Unknown` in function signature | Add explicit return type: `-> ReturnType` |
| String quotes on type | Remove quotes: `"ClassName"` → `ClassName` |
| `Any` on domain object | Use actual field type: `Any` → `SpecificType` |
| Missing element type on collection | Add type: `list` → `list[ElementType]` |
| Fixture not typed | Add return type to fixture: `-> FixtureType` |
| Mock creates `Any` | Use SimpleNamespace instead: `MagicMock()` → `SimpleNamespace(...)` |

---

## Resources

- [Pylance Documentation](https://microsoft.github.io/pylance/)
- [PEP 585: Type Hinting Generics](https://www.python.org/dev/peps/pep-0585/)
- [PEP 604: Union with `|` operator](https://www.python.org/dev/peps/pep-0604/)
- [TKO Architecture: Domain/Application/Infrastructure/Interface](../../../docs/ARCHITECTURE.md)
