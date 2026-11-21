"""Blocks implementation written before a failing test: a Claude Code hook."""

import fnmatch
import json
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
        return Tests('red' if failed else 'green', _touched=False)

    def touched(self) -> Tests:
        """Returns the state after a change to a test."""
        return Tests(self._outcome, _touched=True)

    def refusal(self) -> str:
        """Returns why implementation may not change now, empty when it may."""
        if self._touched:
            return (
                'TDD: a test changed after the last test run. Run the tests and '
                'see it fail on an assertion before you change the implementation.'
            )
        if self._outcome == 'unknown':
            return (
                'TDD: no test run in this session yet. Write a failing test and '
                'run the tests before you change the implementation.'
            )
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
        path = self._relative()
        return (
            not self.test()
            and any(fnmatch.fnmatch(path, pattern) for pattern in IMPLEMENTATION)
            and not any(fnmatch.fnmatch(path, pattern) for pattern in GENERATED)
        )

    def test(self) -> bool:
        """Tells whether the write changes a test."""
        path = Path(self._relative())
        text = ''.join(
            str(self._arguments.get(key, ''))
            for key in ('content', 'new_string', 'edits')
        )
        return (
            'tests' in path.parts
            or path.name.startswith('test_')
            or bool(INLINE_TEST.search(text))
        )

    def new(self) -> bool:
        """Tells whether the write creates a file that does not exist yet."""
        return not self._absolute().exists()

    def _absolute(self) -> Path:
        """Returns the absolute path of the written file."""
        return Path(
            str(
                self._arguments.get('file_path')
                or self._arguments.get('notebook_path', ''),
            ),
        )

    def _relative(self) -> str:
        """Returns the path inside its project, the one that holds AGENTS.md."""
        absolute = self._absolute()
        for folder in absolute.parents:
            if (folder / 'AGENTS.md').is_file():
                return absolute.relative_to(folder).as_posix()
        return absolute.as_posix()


@final
class Transcript:
    """Tool calls of a Claude Code session and their results, read from its file."""

    def __init__(self, path: Path) -> None:
        """Keeps the path of the transcript."""
        self._path = path

    def tests(self) -> Tests:
        """Returns what the session has shown about its tests."""
        tests = Tests()
        runs: set[object] = set()
        for part in self._parts():
            if part.get('type') == 'tool_result' and part.get('tool_use_id') in runs:
                tests = tests.ran(failed=bool(part.get('is_error')))
            elif part.get('type') == 'tool_use':
                tests = self._used(part, tests, runs)
        return tests

    def _used(
        self,
        part: Mapping[str, object],
        tests: Tests,
        runs: set[object],
    ) -> Tests:
        """Returns the state after a tool call and remembers calls that run tests."""
        name = str(part.get('name'))
        arguments = part.get('input')
        if not isinstance(arguments, Mapping):
            return tests
        if name in SHELLS and TEST_RUN.search(str(arguments.get('command'))):
            runs.add(part.get('id'))
        if name in WRITES and Change(name, arguments).test():
            return tests.touched()
        return tests

    def _parts(self) -> Iterator[Mapping[str, object]]:
        """Yields every content part of every message of the transcript."""
        if not self._path.is_file():
            return
        for line in self._path.read_text(encoding='utf-8').splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = record.get('message') if isinstance(record, dict) else None
            content = message.get('content') if isinstance(message, dict) else None
            if isinstance(content, list):
                yield from (part for part in content if isinstance(part, dict))


@final
class Write:
    """Verdict on a write: implementation waits for a failing test."""

    def __init__(self, change: Change, transcript: Transcript) -> None:
        """Keeps the change and the session it belongs to."""
        self._change = change
        self._transcript = transcript

    def refusal(self) -> str:
        """Returns why the write is refused, empty when it is allowed."""
        if not self._change.implementation() or self._change.new():
            return ''
        return self._transcript.tests().refusal()


@final
class Hook:
    """Claude Code hook: reads the tool call from its input, answers on its output."""

    def __init__(self, request: str) -> None:
        """Keeps the JSON request of Claude Code."""
        self._request = request

    def answer(self) -> str:
        """Returns the JSON answer, empty when the write is allowed."""
        request = json.loads(self._request)
        tool = str(request.get('tool_name'))
        arguments = request.get('tool_input')
        if tool not in WRITES or not isinstance(arguments, Mapping):
            return ''
        verdict: Verdict = Write(
            Change(tool, arguments),
            Transcript(Path(str(request.get('transcript_path', '')))),
        )
        reason = verdict.refusal()
        if not reason:
            return ''
        return json.dumps({
            'hookSpecificOutput': {
                'hookEventName': 'PreToolUse',
                'permissionDecision': 'deny',
                'permissionDecisionReason': reason,
            },
        })


if __name__ == '__main__':
    sys.stdout.write(Hook(sys.stdin.read()).answer())
