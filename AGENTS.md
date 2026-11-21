# Instructions for AI agents

## Purpose

This repository is a template for web projects built by AI agents under
human direction: a site or a web application with its pages, its HTTP API
and its admin. A new project starts as a copy of it
(`gh repo create <name> --template grenkoff/monolith-first`)
and keeps its stack, structure, rules and checks.

A project starts as a modular monolith: one Django service, `core`, made of
modules that can each become a separate service later with little effort,
and only for a concrete reason (see "Architecture"). Its pages are
rendered on the server and styled by one design system with three themes
to choose from (see "Frontend").

The project is polyglot: Python and Rust work together inside the monolith
(a Rust extension module) and across services (a Rust service behind gRPC).
See "Languages" for what is allowed and what is forbidden.

A new product starts from one sentence of the human ("make me a website
for a barbershop"): the agent plans, asks the key questions and then builds
a working version fast (see "A new product").

Roles:

- **The human** owns the product: sets tasks with a sentence in the chat,
  approves Issues, makes decisions, reviews pull requests, decides who
  merges each of them, releases to production.
- **The agent** implements tasks: turns a task into an Issue, shows its text
  to the human and creates it only after approval; writes tests and code,
  keeps every check green, opens pull requests, asks the human who merges
  each pull request, and asks the human whenever a decision is not covered
  by these rules.

These rules apply to every change in this repository and in every project
created from it. When a rule and a task conflict, stop and ask the human;
never break a rule silently.

## Getting started

Read before the first change, in this order:

1. this file;
2. `docs/architecture.md`: the monolith, its modules and how a module
   becomes a service;
3. `docs/elegant-objects.md`: object design rules;
4. `docs/tdd.md`: how code is written;
5. `services/core/README.md` and `services/core/docs/`: the Django service
   from wemake-django-template.

First steps in a new project created from the template (the agent performs
all of them, including the GitHub settings):

1. Install the tools (see "Developer environment") and run `make setup`.
2. Create the branches: `develop` from `main`, then rename `main` to
   `production`; make `production` the default branch.
3. Configure the repository: rebase merge only, delete branches after
   merge, protect `develop` and `production` (pull requests only, every
   required CI job green).
4. `make env`, then `make check`: everything must be green before the first
   task.
5. Replace the project name and description in `README.md`; keep the
   example (`catalog` and `orders`) until the first real module exists.

## Repository map

| Path | What it is |
|------|------------|
| `proto/` | gRPC contracts, the single source of truth between services |
| `contracts/` | Rust crate with the code generated from `proto/`; every Rust service depends on it |
| `services/core/` | the monolith: every module, the public HTTP API, admin, its database |
| `services/<name>/` | modules extracted into Rust services; none until a module has to leave |
| `tools/eo-lint/` | Elegant Objects linter for Rust |
| `scripts/` | code generation, end-to-end check, checks and agent hooks |
| `docs/` | architecture, Elegant Objects, TDD, patterns registry, cookbook |
| `.github/` | CI workflow, Dependabot |
| `.claude/` | Claude Code hooks, commands and subagents (see "Agent tools") |
| `compose.yml` | the whole system for `make up` |
| `Makefile` | every command, see "Commands" |
| `Cargo.toml` | the Rust workspace and its shared lints |

Never edit by hand, regenerate instead:

- `services/core/server/contracts/`: `make proto`;
- `docs/patterns.md`: `make patterns`;
- `CHANGELOG.md`: `make changelog`;
- `Cargo.lock`, `services/core/poetry.lock`, `package-lock.json`: change
  dependencies with `cargo`, `poetry`, `npm`;
- migrations in `services/core/server/apps/*/migrations/`: create with
  `makemigrations`, never edit one that was already applied.

Never commit: `target/`, `node_modules/`, `mutants/`, `mutants.out/`,
coverage reports, `services/core/config/.env` (all are in `.gitignore`).

## Stack

Changing anything in this table needs the human's approval.

| Area | Choice |
|------|--------|
| Monolith | Python 3.14, Django 6.1 from [wemake-django-template](https://github.com/wemake-services/wemake-django-template) |
| HTTP API | [django-modern-rest](https://github.com/wemake-services/django-modern-rest) (`dmr`) with `msgspec`; not DRF, not Django Ninja |
| Pages | Django templates rendered on the server |
| CSS | [Tailwind CSS](https://tailwindcss.com) v4 through its standalone CLI (no Node.js), themed by the tokens of the design system |
| Browser code | web components as plain JavaScript ES modules and browser Web APIs; no framework, no npm, no bundler |
| Rust in the monolith | an extension module built with [PyO3](https://pyo3.rs) and [maturin](https://www.maturin.rs), for heavy computation only |
| Python dependencies | Poetry (as wemake-django-template does) |
| Python checks | ruff, [wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide), mypy strict, ty (second, non-blocking), import-linter |
| Python tests | pytest, hypothesis, schemathesis + tracecov, mutmut |
| Extracted services | Rust (stable), one Cargo workspace; only for a module that leaves the monolith |
| Rust libraries | tokio, axum (HTTP), tonic + prost (gRPC), async-nats, thiserror, tracing |
| Rust database access | [sqlx](https://github.com/launchbadge/sqlx), see below |
| Rust checks | rustfmt, clippy pedantic, `eo-lint`, cargo-llvm-cov, cargo-mutants |
| Contracts | protobuf, checked by buf |
| Events | a transactional outbox in the monolith; NATS with JetStream once a service is extracted |
| Database | PostgreSQL: one for the monolith, one per extracted service that needs one |
| Identifiers | UUIDv7 (`uuid.uuid7()` in Python, `uuidv7()` in PostgreSQL) |
| Runtime | Docker Compose |
| CI and updates | GitHub Actions, Dependabot |
| Agent tooling | Probity (TDD hook), commitlint (Node.js, tooling only) |

Why sqlx for Rust services:

- plain SQL instead of an ORM: no Active Record, so database rows map to
  immutable objects and queries live in their own objects, as Elegant
  Objects requires;
- queries are checked against the real schema at compile time (`query!`,
  `query_as!`), so a typo or a type mismatch fails the build, not
  production;
- async on tokio, the runtime the services already use;
- migrations as plain SQL files with `sqlx migrate`, one tool for queries
  and schema.

## Architecture

The project follows
[MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html): it
starts as a modular monolith and moves a module into its own service only
when a split criterion below is met. Splitting is cheap only when the
monolith was built for it, so every module is kept ready to leave.

| Process | Language | Role |
|---------|----------|------|
| `core` | Python, Django | the monolith: every module, the only public HTTP API, auth, admin |
| `db` | — | PostgreSQL of `core` |
| `core-relay` | Python, Django | the same image as `core`: delivers events from the outbox after commit |
| `<name>` | Rust | a module extracted into its own service |
| `nats` | — | message broker, from the first extracted service on |

The template runs only `core`, `core-relay` and `db`. The Rust workspace,
`eo-lint`, the `contracts` crate and buf stay ready and checked in CI with
no service, so the first module that leaves starts from green tooling.

Modules of the monolith:

1. **A module is a Django app** in `server/apps/<module>/`, named after a
   business domain (`billing`, `catalog`), never after a technical layer
   (`auth`, `logging`, `utils`).
2. **Modules meet only through a public package**
   (`server/apps/<module>/public/`): the facade as a protocol, immutable
   transfer objects and events. Only the `infra/` of another module imports
   it; nothing else of a module is imported from outside it.
3. **Facades are coarse**: one call returns everything the caller needs. A
   module that often reads another's data keeps its own copy, updated by
   events.
4. **Synchronous calls go one level deep**: a module that other modules
   call never calls a third one synchronously; longer flows go through
   events.
5. **Each module owns its tables.** No foreign key, join or query reaches
   the tables of another module; it keeps their entities by id.
6. **A transaction stays inside one module.** A change that follows in
   another module comes through an event, so it is consistent eventually,
   not in the same transaction.
7. **Facts go through events**, written to the outbox in the transaction
   of the change and delivered after commit (see "Data integrity").
8. **Every entity has a UUIDv7 primary key** (`uuid.uuid7()`); ids in the
   HTTP API, events and the outbox are UUIDv7 too. They are made anywhere
   without coordination, sort by time and stay valid when a module leaves.
   Users too: the user model is `accounts.User`; refer to it through
   `settings.AUTH_USER_MODEL`, never `auth.User`.
9. **`server/common` knows no domain**: technical code only, never a module
   that others share.
10. **One PostgreSQL by default.** Another store (a search engine, a cache,
    ClickHouse) comes only when a module really needs it, and only that
    module uses it.
11. **Python in the monolith, Rust only where Python is too slow.** A
    module may call a Rust extension module (PyO3) for heavy computation,
    through a protocol in its `logic/` and an adapter in its `infra/`,
    like any other collaborator; no other language enters the monolith.

When to extract a module, only when at least one holds:

- several teams (15–20 or more developers) block each other in one codebase;
- one module needs far more resources than the rest;
- a module needs another stack (Rust for heavy computation);
- a module needs another reliability level or release cycle;
- building, testing or deploying the monolith became too slow;
- a module needs another kind of storage or puts another kind of load on it;
- a module must be isolated for security or compliance (payment data).

The opposite signal: when most tasks change several modules at once, the
boundaries are wrong; fix them inside the monolith before splitting.

A module leaves by the
[Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html)
pattern, never by a rewrite: the new service runs next to the monolith, the
facade of the module in `core` switches to a gRPC adapter one operation at
a time, and the old code is deleted only when nothing goes through it.

Extracted services:

1. **Only `core` is public.** Services are reachable only inside the Docker
   network; clients never call them directly.
2. **Requests go over gRPC, facts go over NATS.** Only `core` calls a
   service and waits for the answer; a service never calls another service
   synchronously, it reacts to events.
3. **Each service owns its data.** No service reads or writes another
   service's database; it asks `core` over gRPC or listens to events.
4. **Each service deploys alone.** Contracts stay backward compatible
   (see "Contracts"); no change needs two services deployed together.
5. **Services are stateless.** State lives in databases and NATS streams,
   so any container can be restarted or replicated.

The monolith and every service:

1. **Configuration only from environment variables** (12-factor); defaults
   suit local development, secrets have no defaults.
2. **Every process has a health check** used by Docker Compose and CI.
3. **Logs are structured** (structlog in Python, tracing in Rust) and go to
   stdout.

These rules keep out the distributed monolith: services split physically
but still coupled by synchronous call chains, a shared database, deploys in
lockstep, transactions across services or a split by technical layers
instead of business domains.

Machine-enforced by `make architecture`, a CI job of its own:

- import-linter: the layers of a module; only `infra` imports the
  `public` package of another module;
- `scripts/modules.py`: no chain or cycle of synchronous calls between
  modules (importing the `public/events.py` of another module is a
  subscription, not a call); no module named after a technical layer
  (`api`, `auth`, `common`, `core`, `helpers`, `infra`, `logging`,
  `shared`, `utils`);
- `scripts/relations.py`: no foreign key, one-to-one or many-to-many
  relation between models of two modules;
- `scripts/keys.py`: every model of a module has a UUIDv7 primary key
  (`UUIDField` with `default=uuid.uuid7`);
- `scripts/transactions.py`: no call to another module inside a
  transaction;
- `scripts/compose.py`: only `core` publishes ports; a database serves one
  deployable (services that run the same image count as one).

Two more checks run with the code they guard: `eo-lint` rule EO012
(`make rust`) rejects generated gRPC clients in service code outside
`tests/`, and `buf breaking` (`make contracts`) keeps contracts backward
compatible, so a service deploys alone.

## Contracts

Inside the monolith the public package of a module is its contract. Once a
module leaves, contracts in `proto/` are the single source of truth between
services, and a change that crosses a service boundary starts with the
contract.

Layout and naming:

- `proto/<service>/v<N>/<service>.proto`, package `<service>.v<N>`
  (`proto/hello/v1/hello.proto`, package `hello.v1`);
- gRPC: service `<Name>Service`, messages `<Method>Request` and
  `<Method>Response`;
- events: a message named as a fact in the past tense (`Greeted`),
  published to the NATS subject `<service>.v<N>.<event>` in snake case
  (`hello.v1.greeted`); the payload is that protobuf message.

Evolution:

1. Never change or reuse a field number; mark removed fields `reserved`.
2. Additive changes (new field, new method, new event) stay in the same
   version.
3. A breaking change goes to a new package `v<N+1>`; the old version keeps
   working until every client has moved, then it is removed in a separate
   pull request.
4. `buf lint` and `buf format` run in `make proto`; `make contracts` adds
   `buf breaking` against `develop` and runs in CI. A breaking change
   outside a new version fails the build.

Generated code:

- Python: `make proto` writes `services/core/server/contracts/`; commit it
  together with the `.proto` change, CI checks it is up to date.
- Rust: the `contracts` crate generates it at build time with
  `contracts/build.rs`; it is never committed and is the only place where
  generated Rust code lives, so lints of the workspace do not apply to it.
- Generated code is never edited by hand.

## Languages

| Language | Where |
|----------|-------|
| Python | the monolith `core`, scripts, checks and agent hooks |
| Rust | extension modules of the monolith, extracted services, our own tools (`eo-lint`) |
| JavaScript | only plain ES modules in the browser that define web components; never on the server, never in tooling |
| HTML, CSS | Django templates; CSS through Tailwind and the design system |
| SQL, protobuf | migrations and queries; contracts in `proto/` |

Forbidden, in the code and in the tooling alike:

- Go, Node.js, npm, Deno, Bun, TypeScript and anything that compiles to
  JavaScript;
- FastAPI, Flask and any web framework but Django;
- JavaScript frameworks and libraries: React, Angular, Vue, Svelte, Solid,
  Lit, Alpine, htmx, jQuery and the like;
- CSS frameworks but Tailwind, CSS preprocessors.

A tool that is needed and exists only for Node.js is replaced by a
standalone binary or by a script of our own in Python or Rust.

## Frontend

Pages are rendered by `core` with Django templates and work without
JavaScript; JavaScript only improves them (progressive enhancement).

1. **Browser Web APIs before code**: HTML elements and attributes first
   (`<dialog>`, `popover`, `<details>`, form validation, `loading="lazy"`),
   then CSS (View Transitions, `:has()`, container queries), then
   JavaScript with Web APIs (`fetch`, `IntersectionObserver`,
   `localStorage`). A library is never the answer.
2. **Web components** for any behaviour in the browser: one custom element
   per file in `static/components/`, a plain ES module with no imports
   from outside the project, named `<project>-<thing>`. A component reads
   its data from its attributes and its children, so the page works
   before it loads.
3. **One design system.** Every page is built from its components and
   styled only by its tokens (colours, fonts, spacing, radii, shadows) as
   Tailwind classes; no colour, size or font written by hand in a
   template. A new page therefore matches the rest of the site.
4. **Three themes.** The design system ships three themes on the same
   components; a project picks one in "A new product" and may let its
   visitors switch.
5. **Accessible by default**: semantic HTML, labels on every control,
   keyboard focus visible, contrast of the tokens checked.

Elegant Objects apply to JavaScript where the platform allows: a custom
element extends `HTMLElement`, as the platform dictates; everything else
follows the rules, comments and directives are forbidden as everywhere.

## A new product

When the human starts a product with one sentence ("make me a website for
a barbershop"), the agent:

1. **Plans first**: switches to plan mode with its strongest model (or
   asks the human to switch, when it cannot do it itself) and plans the
   product deeply before any code: modules, pages, data, events.
2. **Asks the key questions** in one questionnaire (`docs/intake.md`):
   what the product is for, its pages and entities, users and roles,
   languages of the site, which of the three themes, the brand (name,
   logo, colours) and contacts. Nothing else is asked later that the
   questionnaire could have asked.
3. **Builds a working version fast**: modules, pages and the theme from
   the generators and the cookbook, then removes the example; `make up`
   shows the site.

The usual rules apply from the first line of code: Issues, TDD, checks and
pull requests.

## Design principles

Judgement rules, applied to every change:

- **KISS**: the simplest thing that works; boring over clever.
- **YAGNI**: build only what the current task needs; no speculative
  abstraction, configuration or extension points.
- **Separation of concerns**: business logic, I/O and entrypoints live in
  different layers and depend in one direction only (see the layers below).
- **Fail fast**: invalid input or state raises (Python) or returns an
  error (Rust) at once; never continue with bad data.
- **Least astonishment**: code does what its name says and nothing more;
  no hidden side effects.
- **Boy Scout rule**: leave touched code cleaner than you found it, in the
  same pull request, without changing behaviour that is not covered by the
  task.
- **SOLID**: Elegant Objects make these natural: one reason to change per
  object, extension by wrapping objects (decorators) instead of editing
  them, any implementation usable wherever its interface is expected,
  narrow interfaces, dependencies injected through constructors.

Layers:

| Service | Layers, outer to inner | Enforced by |
|---------|------------------------|-------------|
| `core` (Python), in each module | `api` → `infra` → `models` → `logic` → `public`; only `infra` imports the `public` of another module | import-linter (`services/core/.importlinter`) |
| Extracted Rust services | `api` (tonic, axum) → `infra` (sqlx, async-nats) → `domain`; `main.rs` wires them | `eo-lint` rule EO010 |

`public` is the innermost layer of a module: it imports nothing else of its
module, so it maps one to one onto `proto/` when the module leaves. The
module implements its facade in `logic/` or `infra/` and binds it in
`server/composition/<module>.py`, which the composition root
`server/implemented.py` calls.

EO010: modules under `src/domain/` use no I/O crate (`tokio`, `tonic`,
`axum`, `sqlx`, `async_nats`, `prost`), no generated code from `contracts`
and nothing from `api` or `infra`. The domain defines traits and its own
types; `infra` implements the traits and translates the types into protobuf.

Size and complexity: wemake-python-styleguide in Python; in Rust clippy
`too_many_lines` (40), `too_many_arguments` (4), `cognitive_complexity`
(10) from `clippy.toml`.

A function that trips a limit does too much: split it. Never raise a limit
or silence it.

## Elegant Objects

We follow [Elegant Objects](https://www.elegantobjects.org/) by Yegor
Bugayenko. Details and examples: `docs/elegant-objects.md`.

- **Rust: every rule, always.** `eo-lint` and clippy check them in CI.
- **Python: every rule where Django and Pythonic style allow.** The
  framework wins only where it dictates the shape of the code (models,
  managers, `Meta`, settings, management commands); our own code follows
  the rules.

The rules in short:

1. Objects are named after what they are, not what they do: no `-er`/`-or`
   names (`Manager`, `Handler`, `Parser`, `Helper`, `Util`).
2. No getters and setters (`get_*`, `set_*`).
3. Objects are immutable (no `&mut self`; frozen `attrs`/`msgspec` in
   Python).
4. Every public method implements an interface (trait, `typing.Protocol`).
5. No procedures, utility classes or static methods.
6. No public fields; transfer objects at the API boundary are the only
   exception in Python.
7. No global state and no singletons; dependencies come through
   constructors.
8. Constructors only assign fields.
9. No reflection or type checks in business logic.
10. No `NULL`: absence is explicit (`Option`/`Result`, exceptions, empty
    collections).
11. Composition over inheritance; decorators over boolean flags.
12. Small objects: few fields, short methods.

There are no exemptions and no syntax to write one. When a framework or a
crate seems to leave no way to follow a rule, stop and ask the human with
options, reasoning and a recommendation (for example, wrap the foreign type
in an adapter object, or change the rule in `eo-lint` for everyone).

## Design patterns

Patterns from the Gang of Four catalogue are shared vocabulary and a
toolbox, never a target. The `pattern-reviewer` subagent (see "Agent
tools") gives advice and never blocks.

- **A pattern must earn its place**: it removes real duplication, decouples
  a real seam, or tames conditional logic that keeps growing.
  KISS and YAGNI break every tie.
- **Rule of three**: do not abstract before the third concrete case.
- **No speculative patterns**: a strategy with one implementation, a
  factory that makes one thing, an interface with one implementation and
  no test fake, indirection with one caller: delete it.
- **Prefer the lighter form** while it scales: a closure, a `match`/dict
  dispatch, a small value object.

Smell → pattern:

| Smell in the change | Pattern |
|---------------------|---------|
| a growing `if`/`match` on a type or mode choosing behaviour | Strategy: one object per behaviour behind a trait/protocol |
| repeated conditional construction | Factory as an object implementing a trait (never a static method) |
| an external API that does not fit our interfaces | Adapter |
| behaviour added around an object (retry, cache, logging, validation, politeness) | Decorator: wrap, do not edit |
| callers reach into a subsystem's internals | Facade |
| one fact must trigger several unrelated reactions | Observer: a NATS event |
| behaviour depends on a lifecycle status with transitions | State: one immutable object per state |
| operations that must be queued, replayed or undone | Command |

Forbidden by Elegant Objects, use instead:

- Singleton → one instance created in the composition root and injected;
- Template Method (inheritance) → Decorator or Strategy (composition);
- static factory methods → a factory object.

Where patterns are recorded:

- An object that implements a pattern starts its one-line docstring
  with the pattern name: a Python module or class; in Rust the `///` of
  a struct, an enum, a trait or a function, or the `//!` of a module:
  `/// Decorator: adds a polite ending to another greeting.`
- Allowed names: Decorator, Strategy, Adapter, Facade, Factory, Observer,
  State, Command, Composition root.
- `make patterns` generates `docs/patterns.md` (pattern → object → file)
  from the code. Never edit it by hand; commit it with the change.
- CI fails when `docs/patterns.md` is out of date or a docstring uses a
  name outside the list.
- Read `docs/patterns.md` before adding a pattern: reuse what exists.

## Language idioms

Write idiomatic code. Lintable recipes are checked in CI: ruff rule groups
in Python (`C4`, `PERF`, `PTH`, `RET`, `TRY`, `LOG`, `G`, `SIM`, `FURB`
and others in `services/core/pyproject.toml`) and clippy pedantic in Rust.
The rest is judgement; the `pattern-reviewer` subagent (see "Agent tools")
gives advice and never blocks.

Python and Django:

- **Queries**: no N+1 (`select_related`, `prefetch_related`); fetch only
  what is used (`values_list`, `only`); `exists()` and `count()` instead of
  loading rows; bulk operations for many rows.
- **Transfer objects**: frozen `msgspec.Struct` at the API boundary,
  frozen `attrs` classes inside.
- **Logging**: `structlog` with keyword fields
  (`log.info('greeting received', name=name)`), never f-strings in log
  messages and never `print`; `log.exception` inside `except`.
- **Collections**: comprehensions instead of loop-and-append; a plain loop
  when the body has side effects or does not read well as a comprehension.
- **Dispatch**: `match` for several branches on an enum, a `Literal` or a
  structure; `if` for two branches or ranges.
- **Paths**: `pathlib`, never `os.path`.

Rust:

- **Errors**: `thiserror` types per module, `?` to propagate; `anyhow`
  only in `main.rs`.
- **Iterators** instead of index loops; `collect` into the target type.
- **Exhaustive `match`**: no `_ =>` arm that hides a new variant of our own
  enums.
- **Borrowing**: take `&str`/`&[T]` in methods, `impl Into<String>` in
  constructors; clone only when ownership is really needed.
- **Newtypes** for domain values (an `Email`, not a `String`).
- **Async**: never block the runtime; CPU-heavy or blocking work goes to
  `spawn_blocking`.
- **Logging**: `tracing` with fields (`tracing::info!(%name, "greeted")`).
- **Database**: `sqlx::query!`/`query_as!` macros only, so every query is
  checked at compile time.

## General code rules

- **English only**: everything in the repository (code, identifiers,
  strings, docstrings, logs, error messages, file names, documentation,
  commits, pull requests, Issues).
- **Line length**: 88 in Python (the [Black default](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#line-length),
  found to give noticeably shorter files than 79 or 80, after Raymond
  Hettinger's ["Beyond PEP 8"](https://youtu.be/wf-BqAjZb8M?t=260)),
  100 in Rust (the [Rust style guide](https://doc.rust-lang.org/style-guide/)
  default). Formatters enforce it.
- **SQL in code** (raw Django SQL, `sqlx` macros) follows the same limit:
  break lines at `SELECT` columns, `FROM`, `JOIN`, `ON`, `WHERE`, `AND`,
  `VALUES`; never split a quoted literal.
- **Names**: full words, no abbreviations except well-known ones (`id`,
  `url`, `http`); booleans read as statements (`polite`, `expired`).
- **Errors**: specific types (exception classes in Python, `thiserror`
  enums in Rust); never a bare `except`, never swallow an error; every
  error either is handled or reaches the edge of the service, where it
  becomes an HTTP or gRPC status.
- **Timeouts**: every network call (gRPC, HTTP, NATS request, database)
  has an explicit timeout taken from settings.
- **Logs**: what happened and with which identifiers; never secrets,
  tokens, passwords or personal data.
- **No magic values**: numbers and strings with meaning become named
  constants or settings.

## DRY and dead code

- **DRY**: one piece of knowledge lives in one place; extract a shared
  object or constant instead of repeating it.
- **No false DRY**: code that only looks alike but changes for different
  reasons stays separate.
- **Delete dead code as you go**: unused functions, objects, imports,
  dependencies, settings, files. Version control remembers it.

Machine-enforced (`make check` and CI):

| What | Python | Rust |
|------|--------|------|
| unused imports and variables | ruff | rustc `unused` (denied) |
| unused functions, classes, methods | vulture | rustc `dead_code` (denied) |
| unused dependencies | deptry | cargo-machete |
| duplicated code | jscpd (both languages, from 8 lines) | jscpd |

vulture skips `server/settings/`, which Django reads by name. Other
framework entrypoints that look unused to vulture (view methods, admin
classes, management commands, model fields) go to `ignore_names` under
`[tool.vulture]` in `services/core/pyproject.toml`. cargo-machete ignores
only dependencies that generated code or a crate feature needs, listed
under `[package.metadata.cargo-machete]` of the crate. The agent asks the
human before adding a name to either list; never keep real dead code
alive through them.

## Data integrity

Each database is the source of truth for its service, and each module owns
its tables in it. Other modules, other services and NATS are outside any
transaction.

- **Atomicity**: a change that writes more than one row or table of one
  module as one logical unit runs in one transaction
  (`transaction.atomic()` in Django, `pool.begin()` … `commit()` in sqlx).
  Never leave a half-applied state. A transaction never writes the tables
  of two modules.
- **Consistency**: invariants live in the database (constraints, foreign
  keys inside a module, `CHECK`) and in value objects; a violation fails
  fast.
- **Isolation**: read-modify-write under possible concurrency re-reads
  the row with a lock inside the transaction
  (`select_for_update()` in Django, `SELECT … FOR UPDATE` in sqlx).
  Keep transactions short.
- **No I/O inside a transaction**: gRPC calls, HTTP requests and NATS
  publishing happen before the transaction or after it commits, never
  while it holds locks. The one exception is the outbox relay: it
  publishes an event to NATS while it holds the lock of that one outbox
  row, with the event id as `Nats-Msg-Id`, so JetStream drops a repeat
  after a failed commit.
- **Events through the outbox**: an event is written to the outbox table in
  the same transaction as the data it reports, so the two are committed or
  lost together; a relay delivers it only after commit, to the subscribers
  in the monolith and, once a service is extracted, to NATS. A service
  without an outbox publishes only after `commit()`.
- **Idempotent consumers**: the outbox relay and NATS JetStream may deliver
  an event again; handling the same event twice must not change the result
  (check by the UUIDv7 event id in the same transaction as the write).

Machine-enforced:

- Python: `services/core/scripts/transactions.py` (in `make check` and CI)
  rejects gRPC, HTTP and NATS calls and calls to the `public` package of
  another module inside `transaction.atomic()` and functions decorated
  with it; code passed to `transaction.on_commit` is allowed;
- Rust: `eo-lint` rule EO011 rejects an `.await` on anything but the
  transaction itself between `begin()` and `commit()`.

## Comments, docstrings and directives

**Comments are forbidden.** Nothing that the interpreter or compiler
ignores: no `#` comments in Python, no `//` and `/* */` in Rust, no
comments in configs, scripts, Dockerfiles, Compose files, workflows,
`.proto` files. If code needs a comment to be understood, rewrite it:
rename, extract an object, split the method, let the test describe the
behaviour.

**Docstrings are mandatory and one line long.** Every module, class,
function and method, private ones included, starts with exactly one line
that answers "what does it do?":

- Python: `"""Builds greetings with the hello service over gRPC."""`;
- Rust: `//!` for a module, `///` for an item
  (`/// Decorator: adds a polite ending to another greeting.`);
  these are documentation attributes, not comments.
- A pattern name goes first when the object implements one
  (see "Design patterns").
- Not required: test functions (their names describe the behaviour),
  empty `__init__.py`, migrations, generated code.

**Tool directives are forbidden**: `# noqa`, `# type: ignore`,
`# pragma: no cover`, `#[allow]`, `#[expect]`, `#[rustfmt::skip]` and the
like. Fix the cause instead. When there is truly no other way, stop and
ask the human with options, reasoning and a recommendation.

Existing comments and directives from wemake-django-template stay as they
are. When you change a line that carries one, delete it together with the
change; do not rewrite or shorten it.

Machine-enforced: ruff `D` rules and a one-line check for Python docstrings,
`missing_docs` (denied) and `eo-lint` for Rust doc lines, a comment and
directive scan over the diff in CI.

## Test-driven development

All code is written test-first. Details: `docs/tdd.md`.

Before the first test of a task, show the acceptance criteria as a list of
tests (3–8 lines) and wait for the human's "ok".

Then, for every unit of behaviour:

1. **Red**: write one test, run it, and show the real failure line in the
   chat. It must fail on an assertion or a status code, not on a missing
   import or type: create an empty skeleton first (a class or a function
   that returns a wrong value).
2. **Green**: write the minimum code that makes the test pass. Nothing
   "while I'm here": write it down and do it in a later cycle.
3. **Refactor**: only on green. Clean names, duplication and Elegant
   Objects rules; all checks of `make check` stay green.

Each cycle is three commits: `test(<scope>): …` → `feat|fix(<scope>): …`
→ `refactor(<scope>): …` (skip the last one when nothing needed
refactoring). Their order in the branch history is the proof of TDD; do
not squash them inside the branch. Pull requests are merged by rebase, so
the cycles stay in `develop` too.

Special cases:

- **A bug**: the first test reproduces it.
- **Refactoring without a change in behaviour**: first characterization
  tests that pin the current behaviour, then refactor commits.
- **Not test-first by nature**: migrations, configuration, generated code,
  documentation. Say so explicitly in the chat when skipping the cycle.

The Probity hook (`probity.config.ts`) blocks an implementation write that
has no failing test behind it; if it blocks, write the test.

## Tests

| Level | Python (`core`) | Rust | Runs in |
|-------|-----------------|------|---------|
| Unit | `services/core/tests/`, mirrors `server/` | `#[cfg(test)] mod tests` next to the code | `make core`, `make rust` |
| Integration | PostgreSQL from the Compose file of `core`; an in-process fake gRPC server and NATS once a service is extracted | `tests/` of the crate; NATS and PostgreSQL in Docker (testcontainers) | same |
| API contract | schemathesis + tracecov against the OpenAPI schema | — | `make core` |
| End-to-end | `scripts/e2e.sh` through every service | same | `make e2e` |
| Mutation | mutmut | cargo-mutants | `make mutants` |

Rules:

- **One behaviour per test**; the test name says what the object does
  (`refuses_blank_names`, `test_greeting_hello_is_down`).
- **Through the public interface**: traits, protocols, HTTP and gRPC APIs,
  never private details; refactoring must not break tests.
- **Fakes, not mocks**: a small real implementation of the same interface
  (`events::Memory`, the fake gRPC server). No `unittest.mock`, no
  `mockall`.
- **Deterministic**: no `sleep` to wait for something (wait for a signal or
  use a timeout), time and randomness come through injected objects, tests
  run in random order (pytest-randomly), network only to local fakes and
  containers.
- **Fast**: a unit test finishes in milliseconds; every test has a
  timeout (pytest-timeout).
- **Test file names** say what is tested, never an Issue number
  (`test_remote.py`, not `test_remote_42.py`).

Gates (CI fails below them; never lower a gate):

| Code | Coverage |
|------|----------|
| Domain logic: `server/apps/*/logic/` in Python, `src/domain/` in Rust | 100% of lines (and branches in Python) |
| Everything else | at least 80% overall |

Most defects live in a small share of the code: the domain rules. That
share is covered completely; glue and infrastructure get the 80% floor and
are also exercised by `make e2e`. Test-first code reaches far above 80%
anyway: the floor catches code written without tests, it is not a target.

- Mutation testing: zero surviving mutants in covered code; it is what
  proves the tests check behaviour, not just run lines.
- Composition roots (`main.rs`, `build.rs`) are excluded in the tool
  configuration, never with a directive.

## Typical tasks

Every task starts and ends the same way:

- **Start**: Issue approved by the human → branch from `develop` (see
  "Issues, branches, worktrees") → acceptance criteria as a test list,
  human says "ok".
- **End**: `make check` green → pull request to `develop` → ask the human
  who merges it.

Step-by-step recipes live in `docs/cookbook.md` (`/cookbook`); in short:

**Add an HTTP endpoint to `core`**
1. Value objects for the request and the response in `logic/value_objects.py`
   (frozen `msgspec.Struct`).
2. Red/green in `tests/test_apps/<app>/test_api/`: status codes, body,
   errors.
3. A use case object in `logic/usecases/`, collaborators as protocols in
   `logic/`, implementations in `infra/`, bound in
   `server/composition/<module>.py`.
4. A `dmr` controller in `api/views.py` with every error response declared
   (`modify(extra_responses=...)`), routed in `api/urls.py`.
5. schemathesis must pass for the new operation.

**Add a module**
1. `server/apps/<module>/`, named after a business domain, with
   `public/`, `logic/`, `infra/`, `api/`, `models.py` as needed; add it to
   `INSTALLED_APPS`.
2. Include its router in `server/urls.py`.
3. Nothing to add to `.importlinter`: its contracts cover every module
   through `server.apps.*`.

**Use another module**
1. Call its facade from `public/` through a protocol of your module in
   `logic/` and an adapter in `infra/`, bound in
   `server/composition/<module>.py`:
   the adapter is what becomes a gRPC client when that module leaves.
2. Need its data often: subscribe to its events and keep a copy.

**Add an event**
1. A transfer object named as a fact in the past tense (`OrderPlaced`) in
   `public/events.py` of the publisher, with a UUIDv7 id, and its topic
   named like the future NATS subject (`orders.v1.order_placed`).
2. The publisher writes it to the outbox in the transaction of the change;
   the subscriber handles it idempotently (see "Data integrity") and is
   registered for the topic in `server/composition/outbox.py`.

**Add a model and a migration**
1. Django: change `models.py` with a UUIDv7 primary key, `makemigrations`,
   one logical change per migration, backward compatible (see
   "Migrations").
2. Rust: `sqlx migrate add <name>`, plain SQL, same rules.

**Extract a module into a service** (only when a split criterion of
"Architecture" holds, and after the human agrees)
1. Contract first: `proto/<name>/v1/<name>.proto` from the public package
   of the module; the `contracts` crate compiles every `.proto` by
   itself.
2. `services/<name>/` with `src/domain/`, `src/infra/`, `src/api/`,
   `src/main.rs`, its own database; add it to the workspace `members`, a
   `Dockerfile` and a service with a health check in `compose.yml`.
3. Strangler Fig, one pull request per step (`docs/cookbook.md`): copy
   the data into the service through outbox events published to NATS,
   switch reads behind the facade to gRPC one operation at a time, then
   writes; delete the module from `core` when nothing goes through it,
   keeping its `public/`, its gRPC adapter and its HTTP API.

**Add a gRPC method** (to an extracted service)
1. Change `proto/` (an additive change, or a new version for a breaking
   one), `make proto`.
2. Red/green on the server side, then on the client side.

**Fix a bug**
1. A test that reproduces the bug (red), then the fix (green).

**Remove the example** (`catalog`, `orders`), once the first real module
exists, in its own pull request: modules, their composition, tests, the
requests of `scripts/e2e.sh`, `docs/patterns.md`.

## Migrations

Migrations run before the new code starts, while the old code still serves
traffic (`core-migrate` in Compose, the same on deploy). So every migration
must work with the code that is currently in production.

1. **Backward compatible only: expand → deploy → contract.**

   | Step | Pull request | Contents |
   |------|--------------|----------|
   | Expand | PR 1 | new table or column, backfill, code switched to the new one; the old object untouched |
   | Deploy | — | PR 1 reaches production |
   | Contract | PR 2 | only `DROP`, rename, `SET NOT NULL`, new `UNIQUE`; no code that depends on them |

   PR 2 is opened as a draft and becomes ready only after PR 1 is in
   production. Destructive changes never ship together with the code that
   stops using the old object.
2. **One logical change per migration**, one migration per pull request
   where possible.
3. **Never edit a migration that was applied anywhere** (including another
   developer's database or CI); write a new one.
4. **Reversible** where feasible (Django `reverse_code`, sqlx `down`
   files); an irreversible migration is a decision to ask the human about.
5. **Short locks**: every migration runs with `lock_timeout = 5s` and a
   statement timeout. In `core` every database connection has them
   (`DJANGO_DATABASE_LOCK_TIMEOUT`, `DJANGO_DATABASE_STATEMENT_TIMEOUT`);
   a sqlx migration starts with `SET LOCAL lock_timeout = '5s'` and
   `SET LOCAL statement_timeout`. A large backfill raises its own limits
   for its transaction with `SET LOCAL`. A migration that fails on
   `lock_timeout` is the right outcome: retry the deploy instead of
   blocking production. Before dropping a table, drop its foreign keys to
   busy tables first.
6. **One head**: two migrations with the same parent break the deploy.
   `makemigrations --check` in CI catches it; resolve with
   `makemigrations --merge` before merging into `develop`.
7. **In a release pull request**, list every migration as additive or
   contract (with the expand pull request it depends on). A contract
   migration whose expand step is not in production blocks the release.

Machine-enforced: `django-migration-linter` (`lintmigrations`) and
`django-safe-migrations` (`check_migrations`) from wemake-django-template,
`makemigrations --check`, migration tests (`django-test-migrations`).

## Security and supply chain

- **Secrets never enter the repository.** Keys, tokens and passwords come
  from environment variables; `config/.env` is ignored, only
  `config/.env.template` with placeholders is committed. gitleaks scans
  every pull request and the history in CI; a finding blocks the merge.
  If a secret ever lands in git, rotate it at once: deleting the commit
  does not help.
- **Validate at the boundary.** Every input from outside (HTTP, gRPC,
  events) is parsed into a strict value object first; nothing unvalidated
  goes deeper (`StrictMsgspecSerializer`, prost types, value objects).
- **Only `core` is exposed**; internal services listen inside the Docker
  network only.
- **Security lint stays on**: ruff `S` (bandit) in Python, clippy in Rust;
  never disable a rule to pass.
- **Vulnerable dependencies block the merge**: pip-audit for Python,
  cargo-deny for Rust (`deny.toml`: advisories, licenses, sources),
  `npm audit` for tooling. Fix by updating; when no fixed version exists,
  ask the human.
  - An unmaintained Rust crate blocks only when a crate of the workspace
    depends on it directly; deeper in the tree we cannot replace it.
  - Duplicate versions of a Rust crate are reported, not blocking: they
    come from upstream crates and cost build time, not safety.
  - `npm audit` runs through `scripts/npm-audit.mjs`: an advisory with no
    fixed version in a tool that never runs in the system may go to
    `npm-audit-allowlist.json` with its reason, only after the human
    agrees; the script fails once an allowed advisory is no longer
    reported, so the entry is removed as soon as a fix arrives.
- **Containers**: run as a non-root user, base images pinned to a version
  tag and updated by Dependabot.

## Dependencies

**As few dependencies as possible.** Each one is code we do not control,
a supply-chain risk and work on every update. Use the standard library,
the platform (Django, the browser Web APIs) and what the project already
has first; write a small piece ourselves rather than pull a package for
it; remove a dependency as soon as nothing needs it.

Adding a dependency:

- **Every new dependency needs the human's approval.** The agent proposes
  it with alternatives (including "write it ourselves" and "use what we
  already have"), the reasoning and a recommendation: maintenance, size,
  license, how much of it we need.
- Python: `poetry add` (`--group dev` for tooling), never `pip install`
  into the project.
- Rust: versions live once in the root `[workspace.dependencies]`; crates
  refer to them with `.workspace = true`.
- Node.js: tooling only, exact versions (`npm install --save-dev
  --save-exact`).
- Lock files (`poetry.lock`, `Cargo.lock`, `package-lock.json`) are always
  committed with the change that touches dependencies.

Updating:

- Dependabot opens update pull requests weekly. Never merge them on
  GitHub and never push an update straight to `develop`.
- Each update goes the usual way: a branch `chore/deps-<slug>` from
  `develop`, the change applied locally, one commit with the bot's pull
  request title and number as the only line
  (`ci(deps): bump actions/checkout from 5 to 7 (#1)`), `make check`,
  our own pull request to `develop`, ask the human who merges it. The bot
  closes its pull request once the change is in `develop`.
- A major version is a task like any other: read the changelog, run the
  full checks, fix what changed (a breaking API change may compile and
  still change behaviour; only tests catch it).
- Python itself: only patch versions arrive from Dependabot; change the
  Docker image, `requires-python` in `pyproject.toml`, `.python-version`
  and `poetry.lock` together. A minor or major Python version is a
  separate task.

Removing: unused dependencies fail CI (deptry, cargo-machete); remove a
dependency in the same change that stops using it.

## Issues, branches, worktrees

**No Issue, no branch.** Every change of behaviour (`feat`, `fix`,
`refactor`, `perf`) starts with an Issue, however small. Order before the
first line of code:

1. The human states the task in the chat.
2. The agent may investigate first (read code, run things): that is
   diagnosis, not code.
3. The agent drafts the Issue in English (see "Pull requests and Issues"),
   shows it, and creates it with `gh issue create` only after the human
   approves.
4. Then the branch and the worktree.

Changes that do not alter product behaviour (configuration, documentation,
CI, tooling, dependency updates) need no Issue; they still get their own
branch and pull request.

Branches:

- `<type>/<N>-<slug>` with an Issue (`feat/12-polite-greetings`,
  `fix/15-hello-timeout`); `<type>/<slug>` without one
  (`chore/deps-syn-3`, `docs/agents-rules`, `ci/gitleaks`).
- `<type>` is a Conventional Commits type; `<slug>` is short kebab-case
  English.
- Always from a fresh `develop`:
  `git fetch origin && git worktree add ../<project>-<N> -b <branch> origin/develop`.
- Never commit to `develop` or `production` directly; they change only
  through pull requests.
- Keep the branch rebased on `develop`; force-push only your own feature
  branch, with `--force-with-lease`.

Worktrees: one worktree per branch next to the main checkout, so several
tasks never share a working tree; remove it after the pull request is
merged (`git worktree remove`).

## Commits

- **[Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)**:
  `<type>(<scope>): <description>`.
  - types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`,
    `ci`, `chore`, `style`, `revert`;
  - scope: the service, app or area: `core`, `catalog`, `orders`,
    `eo-lint`, `proto`, `deps`, `ci`;
  - description: imperative mood, lowercase, no trailing period, the whole
    line within 100 characters;
  - breaking change: `!` after the scope (`feat(proto)!: remove greet v1`).
- **One line only**: no body, no footer.
- **No AI attribution anywhere**: no `Co-Authored-By` of any AI, no
  "Generated with …", no mention of AI tools. The human who runs the agent
  is the only author.
- **One logical change per commit**; a TDD cycle is the commits
  `test` → `feat|fix` → `refactor` (see "Test-driven development").
- **Every commit builds and passes linters**; tests may fail only in the
  `test(...)` commit of a red step. The last commit of a branch passes the
  whole `make check`.
- Stage files by name (`git add <paths>`), never `git add .` or `-A`, so
  nothing unrelated slips in.

commitlint checks every commit in CI (`commitlint.config.mjs`,
`make commitlint`).

## Pull requests and Issues

Both are written in English, for a human who must understand the point in
a minute. Up to about 15 lines; when it does not fit, cut, do not shrink
the font. Headings `###` or smaller only, never `#` or `##`.

- Write each paragraph and each list item on one line: GitHub shows every
  line break of an Issue or pull request body as a break, so wrapped text
  renders as a narrow column.
- Assign the human to every Issue and pull request the agent creates
  (`--assignee @me`).

**Issue** (drafted by the agent, created after the human approves):

- title: a plain sentence about the outcome
  (`Greetings fail with 500 when hello is down`);
- body: what does not work or is missing, and how it should behave;
  the cause in one line if it is already known;
- `### Acceptance criteria`: a checklist; each item becomes a test.

**Pull request**:

- target branch `develop` (release pull requests: see "Releases");
- title in Conventional Commits form, like a commit
  (`fix(greetings): return 503 when hello is down`);
- first line of the body: `Issue #N`, as a plain mention; no `Closes`
  keyword (see "Releases");
- then: what was broken or missing and what changed in behaviour;
  decisions and limits that the diff does not show (why this contract,
  this format, what was deliberately left out).

Never write in a pull request or an Issue: checks that were run (tests,
linters, coverage), how the cause was found, the history of the branch,
anything the diff already shows (renames, signatures, a list of files),
any mention of AI tools.

After each new commit in a branch with an open pull request, compare the
description with the diff and update it when the commit changed the
essence: behaviour, a contract, a limit, something deliberately left out.
Renames, formatting and review fixes that do not change the task are no
reason to touch it.

## Releases

Branches: `develop` collects finished work; `production` is what runs for
users. `production` is the default branch of the repository, so Issues
close when a release reaches it.

Versions are calendar tags: `vYYYY.MM.DD`; a second release on the same day
is `vYYYY.MM.DD.2`, a third `vYYYY.MM.DD.3` (never a hyphen: tools read it
as a pre-release).

A release:

1. Changelog: a branch `chore/release-<version>` from `develop`,
   `make changelog VERSION=<version>` (git-cliff with `cliff.toml`, built
   from Conventional Commits), a pull request to `develop`.
2. A pull request from `develop` to `production`, titled
   `chore(release): <version>`.
3. Its body lists every Issue finished since the previous release as
   `Closes #N`, one per line, in plain text (GitHub ignores keywords in
   backticks); collect them from the `Issue #N` lines of the feature pull
   requests merged into `develop` since the last release tag.
4. A `### Migrations` section classifies each migration as additive or
   contract (see "Migrations"); a contract migration whose expand step is
   not in production blocks the release.
5. CI green, the human approves.
6. Merge by fast-forward, never by rebase or squash (they rewrite commits
   and the two branches would diverge):
   `git push origin develop:production`; GitHub marks the pull request
   merged.
7. Tag and publish: `git tag <version>` on `production`, push it, and
   create a GitHub Release with the notes of this version
   (`gh release create <version> --notes "$(make release-notes)"`).
8. Check that every listed Issue is closed (`gh issue view <N> --json
   state`); close the rest by hand.

Feature pull requests target `develop` explicitly (`gh pr create --base
develop`); Dependabot targets `develop` (`target-branch` in
`.github/dependabot.yml`).

## Definition of done

A task is done only when all of these are true. Never call it done before.

1. Every acceptance criterion of the Issue has a test, and every test
   passes.
2. The branch history shows the TDD cycles (`test` → `feat|fix` →
   `refactor`).
3. `make check` is green locally on the last commit.
4. Contracts and generated code match (`make contracts` is green).
5. Documentation follows the change: `README.md`, `docs/`, this file when
   a rule or a command changed, `config/.env.template` for every new
   setting.
6. Migrations follow "Migrations"; a contract step is a separate pull
   request.
7. The pull request is open against `develop` with a description per
   "Pull requests and Issues", and CI on GitHub is green.
8. The human has been asked who merges it.

After the merge: remove the worktree and the local branch.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every pull request and
on every push to `develop` and `production`. Both branches are protected:
a pull request merges only with every required job green.

| Job | Checks |
|-----|--------|
| commits | commit messages and the pull request title (commitlint) |
| secrets | gitleaks over the changes and the history |
| contracts | `make contracts`: `buf lint`, `buf format`, `buf breaking`; generated code and `docs/patterns.md` up to date |
| architecture | `make architecture`: import-linter, calls and names of modules, relations between modules, UUIDv7 primary keys, calls to other modules inside transactions, ports and databases in Compose |
| rust | rustfmt, clippy, tests, coverage (80% overall, 100% in `domain/`), `eo-lint`, cargo-machete, cargo-deny |
| rust-mutants | cargo-mutants: zero survivors |
| core | the wemake-django-template pipeline (ruff, wemake-python-styleguide, mypy, import-linter, pytest, schemathesis, Django checks, migration linters, deptry), pip-audit, vulture, transaction check, coverage (80% overall, 100% in `logic/`), mutmut |
| core-ty | ty (non-blocking: reported, never fails the pull request) |
| tooling | `npm audit`, jscpd (duplication in Python and Rust) |
| e2e | `make up` and a request through every service |

When CI is red:

1. Read the failed step's log; reproduce it locally with the same `make`
   target.
2. Fix the code, never the check: do not skip, disable, lower or retry
   blindly.
3. A test that fails only sometimes is a bug: find the cause (time, order,
   a shared resource) and fix it.
4. A change to CI itself goes through a pull request like any code; a
   change that weakens a check needs the human's approval.

## Agent tools

Claude Code configuration for the project lives in `.claude/` and is
committed. It only automates the rules of this file: an agent without
these tools follows the same rules by hand.

| Tool | Where | What it does |
|------|-------|--------------|
| Probity hook | `.claude/settings.json`, `probity.config.ts` | blocks a write to implementation code that has no failing test behind it |
| Format hook | `.claude/settings.json`, `scripts/format-hook.sh` | after every edit formats the file: `ruff format` and `ruff check --fix` for Python, `rustfmt` for Rust |
| `/patterns` | `.claude/commands/patterns.md` | runs `make patterns` and shows `docs/patterns.md`, so an existing object is reused before a new one is written |
| `/cookbook` | `.claude/commands/cookbook.md`, `docs/cookbook.md` | step-by-step recipes: a new Rust service, a Django app, an endpoint, a gRPC method, an event, a migration |
| `pattern-reviewer` | `.claude/agents/pattern-reviewer.md` | a subagent that reviews the branch diff against Elegant Objects, the pattern registry and this file before a pull request is opened |

Phrases and what they mean:

- "start the server", "run the system" → `make up`;
- "stop it" → `make down`.

Rules:

1. Never disable, skip or edit a hook to get past it. When a hook blocks,
   do what it says (for Probity: write the failing test first).
2. Start long-running processes in the background and read their logs.
   Stop them when the task is done, unless the human asked to keep them.
3. A new command, hook or subagent is added through a pull request, and
   `docs/cookbook.md` or this file describes it.

## Developer environment

Supported systems: Linux, macOS, Windows 11 with WSL2. On Windows the
repository lives inside the WSL file system (`~/projects/...`), never
under `/mnt/c`: file watching, permissions and speed break there.

Required tools (`make doctor` checks them and prints what is missing):

| Tool | Used for |
|------|----------|
| Docker with Compose v2 | `make up`, `make core`, `make e2e`, testcontainers |
| GNU Make | every command |
| rustup (toolchain from `rust-toolchain.toml`) | Rust services and `eo-lint` |
| cargo-llvm-cov, cargo-mutants, cargo-deny, cargo-machete | Rust checks |
| protoc | builds the `contracts` crate from `proto/` |
| uv | installs Python and Poetry for the editor environment |
| Node.js (major version from `.nvmrc`, through nvm) and npm | Probity, commitlint, jscpd, git-cliff |
| buf | contracts |
| gitleaks | secret scanning |

Setup from a fresh clone:

1. `make env`: creates `services/core/config/.env` from the template.
2. `make setup`: installs the Node tooling, the Rust components and the
   Poetry environment of `core` for the editor.
3. `make up`: starts the system; `make e2e` proves it works.

Editor: VS Code settings and recommended extensions are committed in
`.vscode/`. Any other editor works if it uses the same formatters
(ruff, rustfmt) and the line lengths from "General code rules".

Versions are pinned in the repository (`rust-toolchain.toml`,
`.python-version`, `.nvmrc`, `package-lock.json`, `poetry.lock`,
`Cargo.lock`, image tags in `compose.yml`). The agent never upgrades a
tool on the machine to make a check pass; a version change goes through
"Dependencies".

## Commands

Every check and every routine action is a `make` target. `make help`
lists them. The agent uses these targets, not the tools behind them,
so local runs match CI.

| Command | What it does |
|---------|--------------|
| `make help` | lists all targets |
| `make doctor` | checks that the required tools are installed |
| `make env` | creates `services/core/config/.env` from the template |
| `make setup` | installs Node tooling, Rust components and the editor environment of `core` |
| `make proto` | checks the contracts with `buf` and regenerates the Python code |
| `make patterns` | regenerates `docs/patterns.md` |
| `make contracts` | `make proto` and `make patterns`, `buf breaking` against `develop`, fails when generated code or `docs/patterns.md` differ from the commit |
| `make architecture` | checks that no distributed monolith appears (see "Architecture") |
| `make rust` | rustfmt, clippy, tests, coverage, `eo-lint`, cargo-machete, cargo-deny |
| `make core` | the wemake-django-template pipeline for `core` inside Docker |
| `make ty` | ty for `core` (non-blocking) |
| `make mutants` | cargo-mutants and mutmut: zero survivors |
| `make security` | gitleaks, pip-audit, cargo-deny advisories, `npm audit` |
| `make duplicates` | jscpd over Python and Rust |
| `make up` / `make down` | starts / stops the whole system |
| `make logs` | follows the logs of the running system |
| `make e2e` | starts the system and sends a request through every service |
| `make commitlint` | checks the commits of the branch against Conventional Commits |
| `make changelog VERSION=<version>` | writes `CHANGELOG.md` with git-cliff for the next release |
| `make release-notes` | prints the notes of the latest release tag for the GitHub Release |
| `make check` | everything CI runs, in the same order |

A new routine action gets a target here and a line in this table in the
same pull request.

## Do not

Stack and architecture:

- Do not add another web framework, ORM, broker, database, package
  manager or language; nothing from the forbidden list of "Languages".
- Do not write JavaScript outside web components, and do not style a page
  past the design system (see "Frontend").
- Do not extract a module into a service without a split criterion from
  "Architecture" and the human's approval; do not add a language to the
  monolith beyond a Rust extension module.
- Do not reach into another module: import only its `public/` package;
  no foreign keys, joins or transactions across modules.
- Do not share a database between services; a service owns its schema.
- Do not expose internal services: only `core` is public. Services talk
  through gRPC contracts and NATS events from `proto/`, never through
  each other's database or internal HTTP.
- Do not import across layers the wrong way (`domain` never imports
  `api` or `infra`).

Code:

- Do not edit generated code (`services/core/server/contracts/`, the
  `contracts` crate); change `proto/` and run `make proto`.
- Do not write comments or tool directives; do not use mocks or `sleep`
  in tests.
- Do not leave dead code, commented-out code, `TODO` or debug output.

Checks:

- Do not weaken a linter, a rule, a coverage or mutation threshold, a
  timeout or a CI job to make a check pass.
- Do not disable or bypass a hook, and do not use `--no-verify`.

Git and GitHub:

- Do not push to `develop` or `production` directly; everything lands
  through a pull request (the release fast-forward is the only exception).
- Do not force-push, rewrite published history or delete a branch that
  is not yours without the human's approval.
- Do not merge a pull request without asking the human who merges it.
- Do not merge bot pull requests on GitHub.
- Do not add AI attribution anywhere.

Secrets and data:

- Do not commit secrets, `.env` files, keys, tokens or dumps; use
  `config/.env.template` for new settings.
- Do not put real personal data in tests, fixtures or logs.
- Do not run destructive commands against shared environments
  (dropping databases, deleting volumes, `docker system prune`) without
  the human's approval.

## When to ask the human

The agent decides alone everything these rules already decide. It stops
and asks when a decision is not in this file or changes it.

Always ask before:

1. Creating an Issue (show its text first).
2. Starting work on acceptance criteria (show the test list first).
3. Adding, removing or replacing a dependency (give alternatives).
4. Adding a tool directive, a name ignored by vulture or cargo-machete or
   any other exception to a rule.
5. Changing a rule, a threshold, a CI job or this file.
6. Changing a public contract in a breaking way (`proto/`, the HTTP API,
   a database schema in a contract step).
7. Merging a pull request (ask who merges it) and releasing.
8. Force-pushing, rewriting history, deleting branches, data, volumes or
   anything else that cannot be undone.
9. Doing anything outside the repository: GitHub settings, external
   services, messages to people. The settings listed in "Getting started"
   are the exception: the agent applies them itself.
10. Extracting a module into a service (name the split criterion that
    holds) or adding a store other than PostgreSQL.

Also ask when:

- the task is ambiguous or two rules conflict;
- the same check fails after two honest attempts to fix the cause;
- the work grows beyond the Issue.

How to ask: one question at a time, with the options, the reasoning for
each and a recommendation. Then wait. Silence is not approval, and an
approval covers only the action it was given for.

When the agent writes or changes a rule (this file, `docs/`, linter or CI
configuration), it shows the human in the chat the exact text it wrote,
in English as committed, together with a translation into the language
of the chat.
