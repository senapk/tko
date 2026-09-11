from __future__ import annotations

import ast
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


class XpExpressionError(ValueError):
    """A source XP formula or its values cannot be evaluated safely."""


@dataclass(frozen=True, slots=True)
class SourceXpConfig:
    variables: tuple[str, ...] = ()
    expression: str | None = None
    source_name: str = ""
    index_path: Path = Path()
    _tree: ast.Expression | None = None

    @property
    def is_configured(self) -> bool:
        return self.expression is not None

    @classmethod
    def from_markdown(cls, content: str, source_name: str, index_path: Path) -> SourceXpConfig:
        """Read the optional leading YAML front matter of an index README."""
        if not content.startswith("---\n") and not content.startswith("---\r\n"):
            return cls(source_name=source_name, index_path=index_path)

        lines = content.splitlines()
        try:
            closing = next(i for i, line in enumerate(lines[1:], 1) if line in {"---", "..."})
        except StopIteration as exc:
            raise XpExpressionError(f"{source_name}:{index_path}: unclosed YAML front matter") from exc

        try:
            data = yaml.safe_load("\n".join(lines[1:closing])) or {}
        except yaml.YAMLError as exc:
            raise XpExpressionError(f"{source_name}:{index_path}: invalid YAML front matter: {exc}") from exc
        if not isinstance(data, dict):
            raise XpExpressionError(f"{source_name}:{index_path}: YAML front matter must be a mapping")

        has_args = "args" in data
        has_expr = "expr" in data
        has_legacy = "var" in data or "xp" in data
        if has_legacy:
            raise XpExpressionError(
                f"{source_name}:{index_path}: YAML fields 'var'/'xp' are not supported; use 'args'/'expr'"
            )
        if not has_args and not has_expr:
            return cls(source_name=source_name, index_path=index_path)
        if has_args != has_expr:
            raise XpExpressionError(
                f"{source_name}:{index_path}: YAML fields 'args' and 'expr' must be declared together"
            )

        variables = data["args"]
        expression = data["expr"]
        if not isinstance(variables, list) or not all(isinstance(item, str) for item in variables):
            raise XpExpressionError(f"{source_name}:{index_path}: 'args' must be a list of variable names")
        if not isinstance(expression, str):
            raise XpExpressionError(f"{source_name}:{index_path}: 'expr' must be a string formula")
        if not variables:
            raise XpExpressionError(f"{source_name}:{index_path}: 'args' must not be empty")
        if len(set(variables)) != len(variables) or any(_IDENTIFIER.fullmatch(name) is None for name in variables):
            raise XpExpressionError(f"{source_name}:{index_path}: 'args' contains an invalid or duplicate variable name")

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise XpExpressionError(f"{source_name}:{index_path}: invalid XP formula {expression!r}: {exc.msg}") from exc
        config = cls(tuple(variables), expression, source_name, index_path, tree)
        config._validate_tree()
        return config

    def _context(self, task_key: str | None = None, line_number: int | None = None) -> str:
        location = f"{self.source_name}:{self.index_path}"
        if line_number is not None:
            location += f":{line_number}"
        if task_key:
            location += f" task @{task_key}"
        return location

    def _validate_tree(self) -> None:
        if self._tree is None:
            return
        allowed_binops = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
        allowed_unaryops = (ast.UAdd, ast.USub)
        for node in ast.walk(self._tree):
            if isinstance(node, ast.Expression | ast.Load | ast.operator | ast.unaryop):
                continue
            if isinstance(node, ast.BinOp) and isinstance(node.op, allowed_binops):
                continue
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, allowed_unaryops):
                continue
            if isinstance(node, ast.Name):
                if node.id not in self.variables:
                    raise XpExpressionError(
                        f"{self._context()}: XP formula references undeclared variable {node.id!r}"
                    )
                continue
            if isinstance(node, ast.Constant) and isinstance(node.value, int | float) and not isinstance(node.value, bool):
                continue
            raise XpExpressionError(f"{self._context()}: XP formula contains unsupported syntax: {type(node).__name__}")

    def calculate(self, values: dict[str, float], task_key: str, line_number: int) -> float:
        if not self.is_configured:
            # Simple repositories do not need to introduce a metric just to
            # make evaluable tasks contribute to progress.
            return 1.0
        missing = [name for name in self.variables if name not in values]
        if missing:
            raise XpExpressionError(f"{self._context(task_key, line_number)}: missing variable(s): {', '.join(missing)}")
        try:
            result = self._evaluate(self._tree.body, values) if self._tree is not None else 0.0
        except ZeroDivisionError as exc:
            raise XpExpressionError(f"{self._context(task_key, line_number)}: division by zero in XP formula") from exc
        except (OverflowError, TypeError, ValueError) as exc:
            raise XpExpressionError(f"{self._context(task_key, line_number)}: XP formula produced an invalid numeric value") from exc
        if isinstance(result, complex) or not math.isfinite(result):
            raise XpExpressionError(f"{self._context(task_key, line_number)}: XP formula produced a non-finite value")
        return float(result)

    def _evaluate(self, node: ast.expr, values: dict[str, float]) -> float:
        if isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, int | float) and not isinstance(value, bool):
                return float(value)
            raise AssertionError("formula tree was not validated")
        if isinstance(node, ast.Name):
            return values[node.id]
        if isinstance(node, ast.UnaryOp):
            value = self._evaluate(node.operand, values)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left, values)
            right = self._evaluate(node.right, values)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Pow):
                return left ** right
        raise AssertionError("formula tree was not validated")
