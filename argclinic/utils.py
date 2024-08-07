import contextlib
import hashlib
from typing import Iterator


INDENT = ' ' * 4


class Config:
    def __init__(self):
        self.min_python_ver = (3, 6)


class Output:
    def __init__(self) -> None:
        self.output: list[str] = []
        self._indent = INDENT
        self.level = 0

    @contextlib.contextmanager
    def indent(self, level: int = 1) -> Iterator[None]:
        self.level += level
        try:
            yield
        finally:
            self.level -= level

    def write(self, line: str = '', level: int = 0) -> None:
        level += self.level
        if level and line:
            line = self._indent * level + line
        self.output.append(line)


def hash_text(text: str) -> str:
    checksum = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return checksum[:16]
