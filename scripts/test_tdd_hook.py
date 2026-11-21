"""Tests of the TDD hook against transcripts of made-up sessions."""

import json
from pathlib import Path

import pytest

from tdd_hook import Hook

LOGIC = 'services/core/server/apps/catalog/logic/price.py'
TEST = 'services/core/tests/test_apps/test_price.py'
RUST = 'tools/clones/src/corpus.rs'
RUST_TEST = '#[test]\nfn works() {}'


class Session:
    """Made-up project and Claude Code session that the hook judges."""

    def __init__(self, root: Path) -> None:
        """Keeps the root of the project and starts an empty transcript."""
        self._root = root
        self._records: list[dict[str, object]] = []

    def create(self, *paths: str) -> Session:
        """Creates files of the project and returns the session."""
        for path in paths:
            target = self._root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('x = 1')
        return self

    def run(self, command: str, *, failed: bool) -> None:
        """Adds a shell command and its outcome to the transcript."""
        tool_id = f'call-{len(self._records)}'
        self._records.extend((
            self._use(tool_id, 'Bash', {'command': command}),
            {
                'type': 'user',
                'message': {
                    'content': [
                        {
                            'type': 'tool_result',
                            'tool_use_id': tool_id,
                            'is_error': failed,
                            'content': 'output',
                        },
                    ],
                },
            },
        ))

    def edit(self, path: str, new: str = 'z = 2') -> None:
        """Adds an edit of a file to the transcript."""
        arguments = {'file_path': str(self._root / path), 'new_string': new}
        self._records.append(
            self._use(f'call-{len(self._records)}', 'Edit', arguments),
        )

    def refusal(self, path: str, tool: str = 'Edit', new: str = 'z = 2') -> str:
        """Returns the reason the hook gives to refuse a write, empty if none."""
        transcript = self._root / 'session.jsonl'
        transcript.write_text(
            '\n'.join(json.dumps(record) for record in self._records),
        )
        key = 'content' if tool == 'Write' else 'new_string'
        request = {
            'hook_event_name': 'PreToolUse',
            'tool_name': tool,
            'tool_input': {'file_path': str(self._root / path), key: new},
            'transcript_path': str(transcript),
        }
        answer = Hook(json.dumps(request)).answer()
        if not answer:
            return ''
        output = json.loads(answer)['hookSpecificOutput']
        assert output['permissionDecision'] == 'deny'
        return str(output['permissionDecisionReason'])

    def _use(
        self,
        tool_id: str,
        tool: str,
        arguments: dict[str, str],
    ) -> dict[str, object]:
        """Returns a transcript record of a tool call."""
        return {
            'type': 'assistant',
            'message': {
                'content': [
                    {
                        'type': 'tool_use',
                        'id': tool_id,
                        'name': tool,
                        'input': arguments,
                    },
                ],
            },
        }


@pytest.fixture
def session(tmp_path: Path) -> Session:
    """Returns a project with code, tests and generated files."""
    return Session(tmp_path).create(
        'AGENTS.md',
        LOGIC,
        TEST,
        RUST,
        'tools/clones/src/main.rs',
        'services/core/server/apps/catalog/migrations/0001_initial.py',
        'services/core/server/settings/base.py',
    )


def test_refuses_an_edit_before_any_test_run(session: Session) -> None:
    assert 'run the tests' in session.refusal(LOGIC)


def test_allows_an_edit_after_a_failing_run(session: Session) -> None:
    session.edit(TEST)
    session.run('make core', failed=True)
    assert not session.refusal(LOGIC)


def test_allows_a_refactoring_on_green(session: Session) -> None:
    session.run('cargo test -p clones', failed=False)
    assert not session.refusal(RUST)


def test_refuses_an_edit_after_a_test_changed_without_a_run(
    session: Session,
) -> None:
    session.run('make core', failed=False)
    session.edit(TEST)
    assert 'see it fail' in session.refusal(LOGIC)


def test_counts_a_rust_test_written_in_place_as_a_test_change(
    session: Session,
) -> None:
    session.run('cargo test', failed=False)
    session.edit(RUST, new=RUST_TEST)
    assert 'see it fail' in session.refusal(RUST)


def test_allows_writing_a_rust_test_in_place(session: Session) -> None:
    assert not session.refusal(RUST, new=RUST_TEST)


def test_ignores_commands_that_run_no_tests(session: Session) -> None:
    session.run('pytest -q', failed=True)
    session.run('git status', failed=False)
    assert not session.refusal(LOGIC)


def test_allows_a_new_implementation_file_as_a_skeleton(
    session: Session,
) -> None:
    new = 'services/core/server/apps/catalog/logic/discount.py'
    assert not session.refusal(new, tool='Write')


def test_allows_tests_at_any_time(session: Session) -> None:
    assert not session.refusal(TEST)


@pytest.mark.parametrize(
    'path',
    [
        'AGENTS.md',
        'services/core/server/settings/base.py',
        'services/core/server/apps/catalog/migrations/0001_initial.py',
        'tools/clones/src/main.rs',
    ],
)
def test_ignores_files_that_are_not_implementation(
    session: Session,
    path: str,
) -> None:
    assert not session.refusal(path)


def test_lets_other_tools_through(session: Session) -> None:
    request = {'tool_name': 'Read', 'tool_input': {'file_path': LOGIC}}
    assert not Hook(json.dumps(request)).answer()
