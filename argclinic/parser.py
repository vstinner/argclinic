import enum
import inspect
from typing import Callable


EMPTY = ""


class ParameterKind(enum.Enum):
    POSITIONAL_ONLY = inspect.Parameter.POSITIONAL_ONLY
    POSITIONAL_OR_KEYWORD = inspect.Parameter.POSITIONAL_OR_KEYWORD
    KEYWORD_ONLY = inspect.Parameter.KEYWORD_ONLY


class ParserParameter:
    def __init__(self, name: str,
                 *, type: str, kind: ParameterKind, default: str = EMPTY) -> None:
        self.name = name
        self.type = type
        self.kind = kind
        self.default = default


class ParserFunction:
    def __init__(self, name = "") -> None:
        self.name = name
        self.params: list[ParserParameter] = []
        self.doc = ""

    def add_doc_line(self, line):
        if self.doc:
            self.doc += "\n" + line
        else:
            self.doc = line

    def set_params_to_pos_only(self):
        for arg in self.params:
            arg.kind = ParameterKind.POSITIONAL_ONLY


class ParseFunction:
    def __init__(self) -> None:
        self.func = ParserFunction()
        self.param_kind = ParameterKind.POSITIONAL_OR_KEYWORD
        self._parse_func: Callable[[str], None] = self._parse_name

    def _parse_doc(self, line: str) -> None:
        self.func.add_doc_line(line)

    def _parse_arg(self, line: str) -> None:
        line = line.strip()
        if not line:
            self._parse_func = self._parse_doc
            return

        if line == "/":
            self.func.set_params_to_pos_only()
            return

        if line == "*":
            self.param_kind = ParameterKind.KEYWORD_ONLY
            return

        parts = line.split(': ', 1)
        if len(parts) == 1:
            raise ValueError(f"expect 'name: type' argument, got {line!r}")
        name, argtype = parts
        name = name.strip()
        argtype = argtype.strip()
        default = EMPTY

        parts = argtype.split(' = ', 1)
        if len(parts) > 1:
            argtype, default = parts
            argtype = argtype.strip()
            default = default.strip()

        arg = ParserParameter(name, type=argtype, kind=self.param_kind, default=default)
        self.func.params.append(arg)

    def _parse_empty_line(self, line: str) -> None:
        if line:
            raise ValueError(f"expect empty line, got: {line!r}")
        self._parse_func = self._parse_arg

    def _parse_name(self, line: str) -> None:
        self.func.name = line
        self._parse_func = self._parse_empty_line

    def parse(self, text, filename: str | None = None) -> ParserFunction:
        for lineno, line in enumerate(text.splitlines(), 1):
            try:
                self._parse_func(line)
            except Exception as exc:
                what = filename if filename else "<string>"
                raise Exception(f"failed to parse {what} at line {lineno}: {exc}")
        return self.func
