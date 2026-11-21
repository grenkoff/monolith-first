# monolith-first

A starting point for web projects built by AI agents and humans: a
**Django** modular monolith with server-rendered pages, **Python** and
**Rust** working together, a module moving into a **Rust** service only
when it has to, written in
[Elegant Objects](https://www.elegantobjects.org/) style and checked by
strict CI. Tell the agent "make me a website for a barbershop": it plans,
asks the key questions and builds a working version.

| | |
|---|---|
| Architecture | modular monolith first ([MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html)), modules leave as services step by step ([Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html)), see [docs/architecture.md](docs/architecture.md) |
| Monolith | Django from [wemake-django-template](https://github.com/wemake-services/wemake-django-template), API on [django-modern-rest](https://github.com/wemake-services/django-modern-rest), UUIDv7 identifiers |
| Python style | [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide), ruff, mypy strict, coverage (100% of domain logic), schemathesis |
| Extracted services | Rust: [axum](https://github.com/tokio-rs/axum), [tonic](https://github.com/hyperium/tonic), [async-nats](https://github.com/nats-io/nats.rs) |
| Rust style | Elegant Objects on 100%: clippy pedantic + [`eo-lint`](tools/eo-lint) |
| Communication | between modules: facades and an outbox of events; between services: gRPC contracts in [`proto/`](proto) ([buf](https://buf.build)) and events over [NATS](https://nats.io) |
| Frontend | Django templates, [Tailwind CSS](https://tailwindcss.com) limited to the tokens of one [design system](docs/design-system.md) with three themes (`/design/` shows them), web components in plain JavaScript and browser Web APIs; no JavaScript framework, no Node.js |
| Runtime | Docker Compose, PostgreSQL |

## Start a new project

```bash
gh repo create my-site --template grenkoff/monolith-first --private --clone
cd my-site
make doctor   # lists the tools that are missing
make setup    # installs the Rust toolchain and the core venv
make env      # creates services/core/config/.env
make up       # starts the site on http://localhost:8000
make e2e      # checks that an order reaches the catalog through the outbox
```

Then tell your AI agent what to build. It reads [`AGENTS.md`](AGENTS.md)
(Claude Code reads it through [`CLAUDE.md`](CLAUDE.md)).

## What is inside

```
proto/               gRPC contracts of extracted services (none yet)
contracts/           Rust crate generated from proto/
services/core/       the Django monolith (public HTTP API, admin, database)
tools/eo-lint/       Elegant Objects linter for Rust
tools/commit-lint/   commit message checker
tools/clones/        finder of repeated code
scripts/             code generation, checks, end-to-end check, agent hooks
docs/                architecture, coding rules, cookbook, patterns registry
.claude/             Claude Code hooks, commands and a review subagent
compose.yml          the whole system
```

The example flow: two modules inside `core`.

```
POST /api/v1/orders/ ─▶ orders ─facade─▶ catalog                     (one process)
                        orders ─outbox─▶ core-relay ─▶ catalog sales  (after commit)
```

Keep `catalog` and `orders` as a reference until your own modules exist,
then delete them. The Rust workspace, `eo-lint`, the `contracts` crate and
buf stay ready and checked in CI for the day a module has to leave the
monolith.

## Checks

`make check` runs everything that CI runs:

| Job | What it checks |
|-----|----------------|
| secrets | gitleaks over the whole history |
| commits | commit messages and pull request titles follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), one line |
| contracts | `buf lint`, `buf format`, breaking changes against `develop`, generated Python code and `docs/patterns.md` are up to date |
| rust | `cargo fmt`, clippy pedantic (warnings are errors), tests with line coverage of 80% overall and 100% in `src/domain/` (cargo-llvm-cov), `eo-lint`, cargo-machete, cargo-deny |
| rust-mutants | mutation testing with cargo-mutants: no mutant may survive |
| core | the full wemake-django-template pipeline: ruff, wemake-python-styleguide, import-linter, mypy, pytest with coverage of 80% overall and 100% in `logic/`, schemathesis + tracecov, Django deploy checks, migration linters, deptry, codespell, typos, yamllint; mutation testing with mutmut; plus [ty](https://github.com/astral-sh/ty) as a second, non-blocking type checker |
| tooling | lint, types and tests of the agent hooks; `clones` (duplicated Python and Rust code) |
| e2e | `docker compose up` and an order through the outbox to the catalog |

## Test-driven development

Code is written test-first, see [docs/tdd.md](docs/tdd.md). For AI agents
it is enforced by a hook of our own that refuses implementation until a
test has failed (run the agent where the code lives); for everyone by
coverage gates and mutation testing in CI. A second hook formats every
file the agent writes with ruff or rustfmt.

## Requirements

Linux, macOS or WSL2 with Docker, Rust (`rustup`), `protoc`,
[uv](https://docs.astral.sh/uv/), Python 3, buf, gitleaks, git-cliff and
the cargo tools listed in [`AGENTS.md`](AGENTS.md#developer-environment).
`make doctor` says what is missing. No Node.js.

## Documentation

- [Architecture](docs/architecture.md)
- [Elegant Objects rules](docs/elegant-objects.md)
- [Test-driven development](docs/tdd.md)
- [Design system](docs/design-system.md): tokens, three themes, components
- [Cookbook](docs/cookbook.md): step-by-step recipes for typical tasks
- [Design patterns registry](docs/patterns.md)
- [Rules for AI agents](AGENTS.md)
- [Django service](services/core/README.md)

## License

[MIT](LICENSE)
