# Test-driven development

All code in this repository is written test-first. This is not a wish:
CI and the agent hook check it.

## The cycle

1. **Red.** Write one small test for the next piece of behaviour.
   Run it and **see it fail** for the expected reason (an assertion, not a
   typo or a missing import). A test you have not seen fail proves nothing.
2. **Green.** Write the minimum code that makes this test pass. No code for
   cases that no test asks for yet. Run the tests: all green.
3. **Refactor.** Clean up the code and the tests while everything stays
   green: names, duplication, Elegant Objects rules (`docs/elegant-objects.md`).
   Run the tests again.

Repeat. Each cycle takes minutes, not hours.

## Rules

- **No production code without a failing test first.** This includes
  bug fixes: first a test that reproduces the bug, then the fix.
- **One behaviour per test.** The test name says what the object does:
  `refuses_blank_names`, `test_greeting_hello_is_down`.
- **Test behaviour through the public interface** (traits, protocols, HTTP
  API), not private details. Then refactoring does not break tests.
- **Fakes over mocks.** Prefer a real small implementation of the same
  interface (an in-memory implementation of a protocol or a trait, an
  in-process fake gRPC server) to mocking libraries.
  Elegant Objects make this easy: every collaborator is an interface.
- **Contract first.** For a new gRPC method: change `proto/`, run
  `make proto`, write the failing test on both sides, then implement.
- **Never weaken a test or a threshold** to get green.

## Where tests live

| Code | Tests | Run |
|------|-------|-----|
| Rust services | `#[cfg(test)] mod tests` next to the code; `tests/` for integration tests | `cargo test -p <crate>` |
| Django `core` | `services/core/tests/`, mirroring `server/` | `make core` (or `pytest` in the container) |
| Whole system | `scripts/e2e.sh` | `make e2e` |

## How it is enforced

| Check | Where | What it catches |
|-------|-------|-----------------|
| **TDD hook** (`scripts/tdd_hook.py`, `.claude/settings.json`) | every file write of the AI agent | implementation changed before a changed test was run and seen failing |
| **Coverage**: pytest-cov (Python), cargo-llvm-cov (Rust); 100% in `logic/` and `src/domain/`, 80% overall | CI, `make check` | code that no test executes |
| **Mutation testing**: mutmut (Python), cargo-mutants (Rust) | CI, `make mutants` | tests that execute code but would not notice if it broke |
| schemathesis + tracecov | CI | API behaviour that differs from the OpenAPI schema |

Coverage says a line was *run* by tests. Mutation testing says the tests
would *fail* if that line were wrong: it changes the code (`>` to `>=`,
`true` to `false`, deletes a call) and expects at least one test to fail.
A surviving mutant means a missing or weak test: write it, in TDD style.

## The TDD hook

`scripts/tdd_hook.py` runs before every file write of Claude Code
(`.claude/settings.json`). It reads the session transcript, a plain file,
and follows two facts: the outcome of the last test run (`make core`,
`make rust`, `pytest`, `cargo test` and the like) and whether a test
changed after it. It needs only `python3`: no packages, no network, no
model call. A write to implementation code (`services/*/src`,
`tools/*/src`, `services/core/server`, without settings, migrations,
generated code and entry points) is refused when:

- no test has run in the session yet: write a failing test and run it;
- a test changed after the last run: run it and see it fail first.

Everything else passes: a new file (the empty skeleton of the red step),
a change after a failing run (green) or after a passing run with no test
changed since (refactor), and any test, including a Rust test written in
place under `#[cfg(test)]`. The hook cannot tell new behaviour from a
refactoring on green; coverage and mutation testing in CI catch code that
no test asked for.

Run the agent **where the code lives**: on Linux/macOS, or *inside* WSL on
Windows (`claude` in the Ubuntu terminal, or VS Code with the WSL
extension). `scripts/tdd-hook.sh` reports at session start when the guard
is off: when `python3` is missing, or when Claude Code runs on Windows
while the project is inside WSL. Other agents (Codex) follow the same
rules by hand; CI still applies to them. `make hooks` lints and tests the
hook.

## Exclusions

The only code excluded from coverage and mutation testing is code that
cannot be unit-tested by nature and is covered by `make e2e` instead:
composition roots (`main.rs`, `build.rs`), excluded in the tool
configuration (`RUST_COVERAGE_IGNORE` in the `Makefile`), never with a
directive.
