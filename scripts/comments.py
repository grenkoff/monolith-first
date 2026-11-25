"""Reports comments and tool directives on the lines a branch adds."""

import fnmatch
import io
import re
import sys
import tokenize
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Final, Protocol, final

GENERATED: Final = (
    'services/core/server/contracts/*',
    '*/migrations/*',
    'docs/patterns.md',
    'CHANGELOG.md',
)
HUNK: Final = re.compile(r'^@@ -\S+ \+(\d+)(?:,(\d+))? @@')
HASH: Final = re.compile(r'^\s*#(?!!)|\s#(\s|$)')
SLASH: Final = re.compile(
    r'(^|\s)//(?![/!])|(^|\s)/\*|#!?\[(allow|expect|rustfmt::skip)\b',
)
TEMPLATE: Final = re.compile(r'\{#|\{%-?\s*comment\b|<!--')
HASH_SUFFIXES: Final = frozenset(
    ('.sh', '.yml', '.yaml', '.toml', '.cfg', '.ini', '.template'),
)
HASH_NAMES: Final = frozenset(
    ('Dockerfile', 'Makefile', '.gitignore', '.dockerignore'),
)
SLASH_SUFFIXES: Final = frozenset(('.rs', '.js', '.proto'))


class Marks(Protocol):
    """Lines of a source text that hold a comment or a tool directive."""

    def lines(self, text: str) -> frozenset[int]:
        """Returns the numbers of the lines with a comment or a directive."""


@final
class PythonMarks:
    """Strategy: comments of Python found by its own tokenizer."""

    def lines(self, text: str) -> frozenset[int]:
        """Returns the numbers of the lines with a comment."""
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        return frozenset(
            token.start[0] for token in tokens if token.type == tokenize.COMMENT
        )


@final
@dataclass(frozen=True, slots=True)
class PatternMarks:
    """Strategy: comments found by a pattern on every line."""

    _pattern: re.Pattern[str]

    def lines(self, text: str) -> frozenset[int]:
        """Returns the numbers of the lines that match the pattern."""
        return frozenset(
            number
            for number, line in enumerate(text.splitlines(), start=1)
            if self._pattern.search(line)
        )


@final
@dataclass(frozen=True, slots=True)
class NoMarks:
    """Strategy: a file that is generated or has no comments to look for."""

    def lines(self, text: str) -> frozenset[int]:
        """Returns no lines."""
        return frozenset()


@final
@dataclass(frozen=True, slots=True)
class Kind:
    """Factory: the strategy that finds comments in a file by its path."""

    _path: str

    def marks(self) -> Marks:
        """Returns the strategy for the file."""
        path = PurePosixPath(self._path)
        if any(fnmatch.fnmatch(self._path, pattern) for pattern in GENERATED):
            return NoMarks()
        if path.suffix == '.py':
            return PythonMarks()
        if path.suffix in SLASH_SUFFIXES:
            return PatternMarks(SLASH)
        if path.suffix in HASH_SUFFIXES or path.name in HASH_NAMES:
            return PatternMarks(HASH)
        if path.suffix == '.html':
            return PatternMarks(TEMPLATE)
        return NoMarks()


@final
class Additions:
    """Lines that a unified diff adds, by file."""

    def __init__(self, diff: str) -> None:
        """Keeps the text of the diff."""
        self._diff = diff

    def lines(self) -> dict[str, frozenset[int]]:
        """Returns the numbers of the added lines of every file."""
        added: dict[str, set[int]] = {}
        path = ''
        for line in self._diff.splitlines():
            if line.startswith('+++ '):
                path = line.removeprefix('+++ b/') if line != '+++ /dev/null' else ''
                continue
            hunk = HUNK.match(line)
            if hunk and path:
                start, count = int(hunk[1]), int(hunk[2] or '1')
                added.setdefault(path, set()).update(range(start, start + count))
        return {name: frozenset(numbers) for name, numbers in added.items() if numbers}


@final
class Report:
    """Comments and tool directives on the added lines of files."""

    def __init__(
        self,
        texts: Mapping[str, str],
        added: Mapping[str, frozenset[int]],
    ) -> None:
        """Keeps the texts of the files and their added lines."""
        self._texts = texts
        self._added = added

    def problems(self) -> Iterator[str]:
        """Yields one line per comment or directive that was added."""
        for path, text in sorted(self._texts.items()):
            found = Kind(path).marks().lines(text) & self._added.get(path, frozenset())
            for number in sorted(found):
                yield f'{path}:{number}: comment or tool directive'


if __name__ == '__main__':
    added = Additions(sys.stdin.read()).lines()
    texts = {path: Path(path).read_text(encoding='utf-8') for path in added}
    problems = list(Report(texts, added).problems())
    sys.stdout.write(''.join(f'{problem}\n' for problem in problems))
    sys.exit(1 if problems else 0)
