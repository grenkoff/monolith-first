"""Blocks implementation written before a failing test: a Claude Code hook."""

import re
import sys
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Protocol, final

IMPLEMENTATION: Final = (
    'services/*/src/*.rs',
    'tools/*/src/*.rs',
    'services/core/server/*.py',
)
GENERATED: Final = (
    'services/core/server/contracts/*',
    'services/core/server/settings/*',
    '*/migrations/*',
    '*/main.rs',
    '*/build.rs',
)
TEST_RUN: Final = re.compile(
    r'\b(make\s+(core|rust|check|e2e|mutants|hooks)'
    r'|pytest|unittest|cargo\s+(test|llvm-cov|nextest|mutants))\b',
)
INLINE_TEST: Final = re.compile(r'#\[(test|cfg\(test\))\]')
WRITES: Final = frozenset(('Write', 'Edit', 'MultiEdit', 'NotebookEdit'))
SHELLS: Final = frozenset(('Bash', 'PowerShell'))


class Verdict(Protocol):
    """Decision on one write of the agent."""

    def refusal(self) -> str:
        """Returns why the write is refused, empty when it is allowed."""


@final
@dataclass(frozen=True, slots=True)
class Tests:
    """What the session has shown about its tests so far."""

    _outcome: str = 'unknown'
    _touched: bool = False

    def ran(self, *, failed: bool) -> Tests:
        """Returns the state after a test run."""
        return self

    def touched(self) -> Tests:
        """Returns the state after a change to a test."""
        return self

    def refusal(self) -> str:
        """Returns why implementation may not change now, empty when it may."""
        return ''


@final
class Change:
    """A file write the agent is about to make."""

    def __init__(self, tool: str, arguments: Mapping[str, object]) -> None:
        """Keeps the tool and its arguments."""
        self._tool = tool
        self._arguments = arguments

    def implementation(self) -> bool:
        """Tells whether the write changes implementation code."""
        return False

    def test(self) -> bool:
        """Tells whether the write changes a test."""
        return False

    def new(self) -> bool:
        """Tells whether the write creates a file that does not exist yet."""
        return False


@final
class Transcript:
    """Tool calls of a Claude Code session and their results, read from its file."""

    def __init__(self, path: Path) -> None:
        """Keeps the path of the transcript."""
        self._path = path

    def tests(self) -> Tests:
        """Returns what the session has shown about its tests."""
        return Tests()

    def _parts(self) -> Iterator[Mapping[str, object]]:
        """Yields every content part of every message of the transcript."""
        yield from ()


@final
class Write:
    """Verdict on a write: implementation waits for a failing test."""

    def __init__(self, change: Change, transcript: Transcript) -> None:
        """Keeps the change and the session it belongs to."""
        self._change = change
        self._transcript = transcript

    def refusal(self) -> str:
        """Returns why the write is refused, empty when it is allowed."""
        return ''


@final
class Hook:
    """Claude Code hook: reads the tool call from its input, answers on its output."""

    def __init__(self, request: str) -> None:
        """Keeps the JSON request of Claude Code."""
        self._request = request

    def answer(self) -> str:
        """Returns the JSON answer, empty when the write is allowed."""
        return ''


if __name__ == '__main__':
    sys.stdout.write(Hook(sys.stdin.read()).answer())
