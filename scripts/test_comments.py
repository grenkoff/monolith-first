"""Tests of the report of comments and tool directives on added lines."""

import pytest

from comments import Additions, Report

_PROBLEM = 'comment or tool directive'


def _report(path: str, text: str, added: frozenset[int]) -> list[str]:
    """Returns the problems of one file with its added lines."""
    return list(Report({path: text}, {path: added}).problems())


def test_python_comment_on_an_added_line_is_reported() -> None:
    assert _report('a.py', 'x = 1  # note\n', frozenset({1})) == [
        f'a.py:1: {_PROBLEM}',
    ]


def test_comment_on_a_line_kept_from_before_passes() -> None:
    assert not _report('a.py', '# old\nx = 1\n', frozenset({2}))


def test_hash_inside_a_python_string_passes() -> None:
    assert not _report('a.py', "colour = '#ffffff'\n", frozenset({1}))


@pytest.mark.parametrize(
    'line',
    [
        'let x = 1; // note',
        '// note',
        '/* note */',
        '#[allow(dead_code)]',
        '#![expect(clippy::pedantic)]',
        '#[rustfmt::skip]',
    ],
)
def test_rust_comment_or_directive_is_reported(line: str) -> None:
    assert _report('src/a.rs', f'{line}\n', frozenset({1})) == [
        f'src/a.rs:1: {_PROBLEM}',
    ]


@pytest.mark.parametrize(
    'line',
    [
        '/// Builds greetings.',
        '//! The greeting module.',
        'let url = "https://example.com";',
        'let glob = "src/*/main.rs";',
    ],
)
def test_rust_documentation_and_strings_pass(line: str) -> None:
    assert not _report('src/a.rs', f'{line}\n', frozenset({1}))


@pytest.mark.parametrize(
    ('path', 'text'),
    [
        ('scripts/run.sh', 'echo hi  # note\n'),
        ('compose.yml', '# note\nservices: {}\n'),
        ('services/core/docker/django/Dockerfile', '# note\nFROM python\n'),
        ('Makefile', '# note\nall:\n'),
        ('static/components/site-x.js', '// note\n'),
        ('proto/a/v1/a.proto', '// note\n'),
        ('templates/a.html', '{# note #}\n'),
        ('templates/b.html', '<!-- note -->\n'),
    ],
)
def test_comment_in_other_sources_is_reported(path: str, text: str) -> None:
    assert _report(path, text, frozenset({1})) == [f'{path}:1: {_PROBLEM}']


@pytest.mark.parametrize(
    'text',
    [
        '#!/usr/bin/env bash\n',
        'if [ $# -eq 0 ]; then exit; fi\n',
        'colour: "#ffffff"\n',
    ],
)
def test_shebang_and_hash_in_code_pass(text: str) -> None:
    assert not _report('scripts/run.sh', text, frozenset({1}))


@pytest.mark.parametrize(
    'path',
    [
        'services/core/server/apps/catalog/migrations/0001_initial.py',
        'services/core/server/contracts/images/v1/images_pb2.py',
        'docs/notes.md',
    ],
)
def test_generated_and_unknown_files_pass(path: str) -> None:
    assert not _report(path, '# Generated\n', frozenset({1}))


def test_additions_of_a_diff_are_read() -> None:
    diff = (
        'diff --git a/a.py b/a.py\n'
        '--- a/a.py\n'
        '+++ b/a.py\n'
        '@@ -1,0 +2,2 @@\n'
        '+x = 1\n'
        '+y = 2\n'
        '@@ -9 +11 @@\n'
        '-z = 0\n'
        '+z = 3\n'
        '@@ -20,2 +22,0 @@\n'
        '-gone = 1\n'
        '-gone = 2\n'
        'diff --git a/old.py b/old.py\n'
        '--- a/old.py\n'
        '+++ /dev/null\n'
        '@@ -1 +0,0 @@\n'
        '-x = 1\n'
    )

    assert Additions(diff).lines() == {'a.py': frozenset({2, 3, 11})}
