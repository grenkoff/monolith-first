SHELL := /bin/bash
.DEFAULT_GOAL := help
CORE := services/core
NATIVE := $(CORE)/native
COMPOSE := env UID=$(shell id -u) GID=$(shell id -g) docker compose
PYTHON_VERSION := $(shell cat $(CORE)/.python-version)
POETRY_VERSION := $(shell sed -n "s/.*POETRY_VERSION=\([0-9.]*\).*/\1/p" $(CORE)/docker/django/Dockerfile)
RUST_COVERAGE_IGNORE := '(^|/)(main|build)\.rs$$'
GENERATED := $(CORE)/server/contracts docs/patterns.md
CONTRACTS := $(shell find proto -name '*.proto' 2>/dev/null)
DEVELOP_CONTRACTS := $(shell git ls-tree -r --name-only origin/develop -- proto 2>/dev/null | grep '\.proto$$')
LOCKED = $(shell grep -A1 '^name = "$(1)"' $(CORE)/poetry.lock | sed -n 's/^version = "\(.*\)"/\1/p')
UVX := uvx -q --python $(PYTHON_VERSION)
PLAYWRIGHT := 1.64.1

.PHONY: help
help:
	@printf '%s\n' \
	  'make doctor        check that the required tools are installed' \
	  'make setup         install the Rust toolchain and the core venv' \
	  'make env           create services/core/config/.env from the template' \
	  'make proto         buf lint and format, regenerate Python gRPC code from proto/' \
	  'make patterns      regenerate docs/patterns.md from the code' \
	  'make contracts     proto, patterns, buf breaking against develop, no diff' \
	  'make architecture  module boundaries and services: no distributed monolith' \
	  'make rust          fmt, clippy, tests, coverage (80%, 100% in domain), eo-lint, cargo-deny' \
	  'make core          wemake-django-template CI for core in Docker' \
	  'make ty            second type checker for core (non-blocking)' \
	  'make mutants       mutation testing for Rust and core' \
	  'make security      gitleaks, cargo-deny advisories, pip-audit' \
	  'make duplicates    clones: repeated blocks of Python and Rust' \
	  'make hooks         lint, type check and test the agent hooks and browser tests' \
	  'make js            Biome: lint and format check of the web components' \
	  'make browser       Playwright: the web components in Chromium (system up)' \
	  'make css           build the stylesheet of core once (Tailwind CLI)' \
	  'make module        create a module of core: make module NAME=bookings' \
	  'make up            start the whole system' \
	  'make down          stop the whole system' \
	  'make e2e           check a request through every service' \
	  'make commitlint    check commit messages (Conventional Commits)' \
	  'make changelog     write CHANGELOG.md for VERSION=vYYYY.MM.DD (git-cliff)' \
	  'make release-notes print the notes of the latest release' \
	  'make check         everything CI runs'

.PHONY: doctor
doctor:
	./scripts/doctor.sh

.PHONY: module
module:
	@test -n "$(NAME)" || { echo 'usage: make module NAME=<module>'; exit 1; }
	python3 scripts/scaffold.py $(NAME)

.PHONY: css
css: env
	$(COMPOSE) run --rm --no-deps core-css --minify \
	  --input=server/common/django/styles/site.css \
	  --output=server/common/django/static/site/site.css

.PHONY: setup
setup: env
	rustup show active-toolchain || rustup toolchain install
	cd $(CORE) && POETRY_VIRTUALENVS_IN_PROJECT=true POETRY_VIRTUALENVS_USE_POETRY_PYTHON=true \
	  uvx --python $(PYTHON_VERSION) poetry==$(POETRY_VERSION) sync

.PHONY: env
env:
	@test -f $(CORE)/config/.env || ( \
	  cp $(CORE)/config/.env.template $(CORE)/config/.env && \
	  sed -i "s/__CHANGEME__/$$(head -c 48 /dev/urandom | base64 | tr -d '/+=')/" $(CORE)/config/.env && \
	  echo "created $(CORE)/config/.env" )

.PHONY: proto
proto:
ifneq ($(CONTRACTS),)
	buf lint
	buf format --diff --exit-code
endif
	./scripts/proto.sh

.PHONY: contracts
contracts: proto patterns
ifneq ($(and $(CONTRACTS),$(DEVELOP_CONTRACTS)),)
	buf breaking --against "$$(git rev-parse --path-format=absolute --git-common-dir)#ref=origin/develop"
endif
	git add --intent-to-add $(GENERATED)
	git diff --exit-code -- $(GENERATED)

.PHONY: architecture
architecture: env
	cd $(CORE) && $(COMPOSE) build web
	$(COMPOSE) config --format json | \
	  (cd $(CORE) && $(COMPOSE) run --rm --no-deps -T web ./docker/django/architecture.sh)

.PHONY: patterns
patterns:
	cargo run -q -p eo-lint --bin patterns --locked -- services tools > docs/patterns.md

.PHONY: rust
rust:
	cargo fmt --all --check
	cargo fmt --manifest-path $(NATIVE)/Cargo.toml --check
	cargo clippy --workspace --all-targets --locked
	cargo clippy --manifest-path $(NATIVE)/Cargo.toml --all-targets --all-features --locked
	cargo llvm-cov --workspace --locked \
	  --ignore-filename-regex $(RUST_COVERAGE_IGNORE) --fail-under-lines 80
	./scripts/domain-coverage.sh
	cd $(NATIVE) && cargo llvm-cov --locked --fail-under-lines 100
	cargo run -q -p eo-lint -- services tools
	cargo machete
	cargo deny --locked check
	cargo deny --manifest-path $(NATIVE)/Cargo.toml --locked --all-features check

.PHONY: security
security: env
	gitleaks git --no-banner --redact .
	cargo deny --locked check advisories
	cd $(CORE) && $(COMPOSE) build web && \
	  $(COMPOSE) run --rm --no-deps web pip-audit --desc

.PHONY: duplicates
duplicates:
	cargo run -q -p clones --locked -- services tools contracts scripts

.PHONY: hooks
hooks:
	$(UVX) ruff@$(call LOCKED,ruff) check --no-fix scripts tests/browser
	$(UVX) ruff@$(call LOCKED,ruff) format --check scripts tests/browser
	cd scripts && $(UVX) --with pytest==$(call LOCKED,pytest) mypy@$(call LOCKED,mypy) --strict .
	cd tests/browser && $(UVX) --with pytest==$(call LOCKED,pytest) \
	  --with playwright==$(PLAYWRIGHT) mypy@$(call LOCKED,mypy) --strict .
	cd scripts && $(UVX) pytest@$(call LOCKED,pytest) -q -p no:cacheprovider

.PHONY: js
js:
	biome ci

.PHONY: browser
browser:
	docker build -q -t monolith-first-browser \
	  --build-arg PLAYWRIGHT=$(PLAYWRIGHT) \
	  --build-arg PYTEST=$(call LOCKED,pytest) tests/browser
	docker run --rm --network host --user "$$(id -u):$$(id -g)" \
	  -e HOME=/tmp -e CORE_URL="$${CORE_URL:-http://localhost:8000}" \
	  -v "$$PWD/tests/browser:/tests:ro" monolith-first-browser \
	  python -m pytest -q -p no:cacheprovider

.PHONY: mutants
mutants: mutants-rust mutants-core

.PHONY: mutants-rust
mutants-rust:
	cargo mutants --workspace
	cargo mutants --dir $(NATIVE)

.PHONY: mutants-core
mutants-core: env
	cd $(CORE) && $(COMPOSE) build web && \
	  $(COMPOSE) run --rm web ./docker/django/mutants.sh

.PHONY: core
core: env
	cd $(CORE) && $(COMPOSE) build web && \
	  $(COMPOSE) run --rm web ./docker/django/ci.sh

.PHONY: ty
ty: env
	cd $(CORE) && $(COMPOSE) build web && \
	  $(COMPOSE) run --rm --no-deps web ty check

.PHONY: up
up: env
	$(COMPOSE) up --build --detach --wait --wait-timeout 300

.PHONY: down
down:
	$(COMPOSE) down --volumes

.PHONY: e2e
e2e: up
	./scripts/e2e.sh
	$(MAKE) browser

.PHONY: commitlint
commitlint:
	git log -z --format=%B $(or $(RANGE),-1) | cargo run -q -p commit-lint --locked

.PHONY: changelog
changelog:
	@test -n "$(VERSION)" || { echo 'usage: make changelog VERSION=vYYYY.MM.DD'; exit 1; }
	git-cliff --tag $(VERSION) --output CHANGELOG.md

.PHONY: release-notes
release-notes:
	@git-cliff --latest --strip header

.PHONY: check
check: commitlint security contracts architecture hooks js duplicates rust core mutants e2e
	$(MAKE) down
