# Cookbook

Step-by-step recipes for the typical tasks of `AGENTS.md`. The example
modules `catalog` and `orders` show every step inside the monolith in real
code; copy their shape, not their names.

Every recipe starts and ends the same way:

- **Start**: an Issue approved by the human (for a change of behaviour),
  a branch and a worktree from `develop`, the acceptance criteria as a list
  of tests and the human's "ok".
- **Each behaviour**: red (one failing test, its failure line in the
  chat), green (the least code), refactor; commits `test` → `feat|fix` →
  `refactor`.
- **End**: `make patterns` when an object names a pattern, `make check`
  green, the `pattern-reviewer` subagent, a pull request to `develop`, and
  the question who merges it.

Run `/patterns` before writing a new object: an existing one may already
do the job or only need a decorator.

## Add an HTTP endpoint to `core`

Example: `POST /api/v1/orders/` in `server/apps/orders/`.

1. Value objects in `logic/value_objects.py`: the request and the response
   as frozen `msgspec.Struct`, validated on construction (`OrderDraft`,
   `Order`).
2. Red: an API test in `tests/test_apps/test_<app>/test_api/` that posts
   through the Django test client and checks the status code and the body;
   then one test per error status.
3. A use case object in `logic/usecases/<name>.py` (`place_order.PlaceOrder`):
   a frozen `attrs` class that receives its collaborators as protocols from
   `logic/` (`Prices`, `Orders`) and raises domain errors
   (`ProductNotOnSaleError`).
4. Implementations of the protocols in `infra/` (`orders.StoredOrders`),
   with every network call bounded by a timeout from settings.
5. Build and bind them by hand in `server/composition/<app>.py`, called
   from the composition root `server/implemented.py`:
   `container.register(place_order.PlaceOrder, instance=place_order.PlaceOrder(catalog.CatalogPrices(facade), stored))`.
6. A `dmr` controller in `api/views.py`: `HasContainer` and
   `Controller[StrictMsgspecSerializer]`, the handler resolves the use case,
   `@modify(extra_responses=[...])` declares every error status, and
   `handle_error` maps each domain error to its status.
7. Route it in `api/urls.py` (`dmr.routing.Router`) and include the router
   in `server/urls.py` under `router_v1`.
8. `make core`: schemathesis and tracecov must cover the new operation and
   each declared response.

## Add a page

Example: the product page `GET /products/<id>/` in `server/apps/catalog/`.

1. Red: a page test in `tests/test_apps/test_<app>/test_views/` with the
   Django test client: the status code and the texts a visitor must see
   (`test_product_pages.py`); one test per error status.
2. The data comes from a use case in `logic/usecases/`, as for an endpoint;
   a page never reads models directly.
3. A Django view in `views/pages.py`: `HasContainer` first, then `View`;
   `get` (and `post` for a form) resolves the use case and renders a
   template; a domain error becomes `Http404` or a page with its status.
   Amounts of money go through `server.common.money.Cents`.
4. The template in `templates/<app>/<page>.html` extends
   `layout/base.html` and fills `content` (and `title`). It is styled with
   the components and tokens of `docs/design-system.md` plus Tailwind
   layout utilities; forms carry `{% csrf_token %}`, labels and HTML
   validation (`required`, `min`), and work without JavaScript.
5. Route it in `views/urls.py` and include the list in `server/urls.py`
   with the namespace of the module:
   `path('', include((catalog_page_urls.urlpatterns, 'catalog')))`.
6. `make up` shows it at once: `core-css` rebuilds the stylesheet when a
   template uses a new class; `make css` builds it once.

## Translate the site

Django i18n is on (`LocaleMiddleware`, `LOCALE_PATHS = ('locale/',)`);
the template speaks English only.

1. `LANGUAGES` and `LANGUAGE_CODE` in
   `server/settings/components/common.py` list the languages of the site,
   the default one in `LANGUAGE_CODE`.
2. Pages go inside `i18n_patterns(...)` in `server/urls.py`, so every
   page lives under its language (`/ru/`, `/en/`); the HTTP API, the
   admin and health checks stay outside it.
3. The language switcher is a form in `layout/base.html` that posts
   `language` and `next` to `set_language`
   (`path('i18n/', include('django.conf.urls.i18n'))`, outside
   `i18n_patterns`): it works without JavaScript and stays on the same
   page.
4. Texts of templates and code go through `{% translate %}` and
   `gettext_lazy`; `docker compose run --rm web python manage.py
   makemessages -l <language>` writes `locale/<language>/LC_MESSAGES/django.po`.
   Commit the `.po` files only: the entrypoint of every `core` container
   compiles the stale ones into `.mo`, which git ignores.
5. Content that staff edit in the admin keeps one field per language
   (`name_ru`, `name_en`), without a new dependency; `infra/` maps them
   into one value object of `logic/` that returns the text for a
   language.
6. Tests: `reverse()` of a page follows the active language of the
   thread, which a request to another language in an earlier test leaves
   behind, and pytest-randomly changes the order. Reverse page URLs inside
   `translation.override('<language>')`, never bare.

## Add a web component

Example: `site-total`, the live total of the product page.

1. The page first: render with the server everything the component
   needs (the price, the quantity field, the `<output>` with the
   total for one item) inside `<site-<thing> data-or-attributes>`; the
   page must work without JavaScript. Pin that markup in a page test.
2. Red: a browser test in `tests/browser/` with Playwright
   (`page.get_by_label(...).fill(...)`, `expect(...).to_have_text(...)`)
   against the running system: `make up`, then `make browser`.
3. Green: `server/common/django/static/components/site-<thing>.js`, a
   class that extends `HTMLElement`, works in `connectedCallback`, uses
   Web APIs (`Intl`, `localStorage`, `fetch`, `dialog`) and ends with
   `customElements.define('site-<thing>', ...)`. No imports but relative
   ones, no libraries.
4. Load it from the template:
   `<script type="module" src="{% static 'components/site-<thing>.js' %}"></script>`
   in the `scripts` block.
5. `make js` (Biome) and `make core` (`scripts/components.py`) must be
   green.

## Add a Django app

1. `make module NAME=<app>`: it refuses a name of a technical layer or an
   existing module, creates `server/apps/<app>/` with `public/`,
   `logic/usecases/`, `infra/`, `api/`, `views/`, `migrations/` and
   `models.py`, and adds `'server.apps.<app>'` to `INSTALLED_APPS`.
2. Delete the layers the module will not need before the pull request.
3. Include its router in `server/urls.py`, and its pages when it has
   `views/` (see "Add a page").
4. The contracts in `services/core/.importlinter` cover every app through
   `server.apps.*`; `lint-imports` (in `make core`) proves the new app
   imports downwards only, and from other apps only their `public/`, from
   its `infra/`.
5. Tests mirror the app in `tests/test_apps/test_<app>/`.

## Use another module

Example: `orders` prices an order with the `Catalog` facade of `catalog`.

1. The called module exposes a coarse facade in `public/`: a protocol, the
   transfer objects it returns and the errors it raises
   (`catalog.public.products`: `Catalog`, `Product`, `UnknownProductError`).
   Its `infra/` or `logic/` implements it (`StoredProducts`).
2. The caller declares what it needs as its own protocol in `logic/`, in
   its own words, with its own errors (`Prices`, `ProductNotOnSaleError`);
   its use cases depend only on that (`PlaceOrder`), and a fake proves them.
3. An adapter in the `infra/` of the caller implements the protocol with
   the facade and translates its errors (`CatalogPrices`); it is the only
   place that imports the `public/` of the other module, and the one that
   becomes a gRPC client when that module leaves.
4. Keep the other module's entities by id (`Order.product` is a
   `UUIDField`, never a foreign key), and copy what must not change later
   (the total an order was sold at).
5. Wire the adapter with the facade in `server/composition/orders.py`;
   `server/implemented.py` hands it the facade that
   `server/composition/catalog.py` builds.

## Move a computation to Rust inside the monolith

Example: the catalog search ranks names in Rust
(`services/core/native`, Python module `ranking`). Only for work where
Python is measurably too slow; everything else stays in Python.

1. Red/green in Rust: an object in `src/domain/` with unit tests next to
   it (`Phrase` and `Resembled` in `phrase.rs`); `make rust` checks the
   crate (fmt, clippy with and without the `python` feature, 100% line
   coverage, `eo-lint`, cargo-deny) and `make mutants` mutates it.
2. The binding in `src/python.rs`, compiled only with the `python`
   feature: a `#[pyclass(frozen)]` adapter with `#[new]` and
   `__call__` (callable like a use case), exported by a declarative
   `#[pymodule] mod`. Keep it free of logic: cargo-mutants skips it
   (`.cargo/mutants.toml`), the Python tests of the adapter cover it.
3. Types for Python in `ranking.pyi` next to `Cargo.toml`.
4. The image of `core` builds the wheel with maturin in the stage
   `native_build` and installs it; nothing to do by hand.
5. In the module: a protocol in `logic/` (`Similarity`), the use case
   tested with a fake (`SearchProducts`), the adapter in `infra/`
   (`RustSimilarity`) tested against the real extension, bound in
   `server/composition/<module>.py`.

## Add a Rust service

1. Contract first: `proto/<name>/v1/<name>.proto`, package `<name>.v1`,
   service `<Name>Service`. The `contracts` crate compiles every `.proto`
   in `proto/` by itself and exposes it as `contracts::<name>::v1`.
2. `services/<name>/Cargo.toml`: every dependency, `contracts` and
   dev-dependencies included, comes from `[workspace.dependencies]`
   (`.workspace = true`; add a missing one there first, with
   `contracts = { path = "contracts" }`), and `[lints] workspace = true`.
   Add the crate to `members` in the root `Cargo.toml`.
3. Layers under `src/`: `domain/` (newtypes, traits, errors; no I/O, rule
   EO010), `infra/` (adapters to NATS, sqlx, gRPC clients, settings),
   `api/` (tonic and axum entrypoints), `lib.rs` exposing them, and
   `main.rs` as the composition root that reads settings from the
   environment and wires the objects.
4. Red/green per behaviour: unit tests next to the code
   (`#[cfg(test)] mod tests`), fakes of the domain traits (an in-memory
   implementation of the trait), integration tests in `tests/` with
   testcontainers.
5. A `Dockerfile` in `services/<name>/`: build stage with
   `protobuf-compiler`, a non-root runtime user, `HEALTHCHECK` against the
   health route of axum.
6. A service in `compose.yml` with its environment; services that call it
   wait for `condition: service_healthy`. It publishes no ports: only
   `core` is public.
7. Its client in `core`: `make proto`, then an adapter in `infra/` of the
   app that calls it (see "Add a gRPC method").
8. `make rust`, `make e2e`.

## Add a gRPC method

1. Add the method and its `<Method>Request` and `<Method>Response`
   messages to `proto/<service>/v<N>/<service>.proto`: an additive change
   stays in the same version, a breaking one goes to `v<N+1>`. Never reuse
   a field number; mark removed fields `reserved`.
2. `make proto` and commit the regenerated `services/core/server/contracts/`
   together with the `.proto` change.
3. Server side, red/green: a test through the tonic service in `api/`, the
   behaviour in `domain/`, the translation between protobuf and domain
   types in `api/` or `infra/`.
4. Client side in `core`, red/green: an adapter in `infra/` that maps gRPC
   status codes to domain errors and uses a timeout from settings, tested
   against an in-process fake server in `tests/plugins/<app>/`. The first
   client brings `grpcio` and `protobuf` into the dependencies of `core`.

## Add an event between modules

Example: `orders` publishes `orders.v1.order_placed`, `catalog` records a
sale.

1. The fact in `public/events.py` of the publisher: a frozen
   `msgspec.Struct` named in the past tense with a UUIDv7 `id`
   (`OrderPlaced`), and its topic as a constant named like the future NATS
   subject (`ORDER_PLACED = 'orders.v1.order_placed'`).
2. The publisher writes it with `Outbox.add(topic, fact)` inside the
   `transaction.atomic()` that writes the change (`StoredOrders.add`); the
   query snapshot of the test shows both inserts inside one savepoint.
3. The subscriber in the `infra/` of the other module implements
   `Subscriber.receive(envelope)`: it converts the payload into the fact
   and writes under the event id, so a second delivery changes nothing
   (`RecordedSales`, `get_or_create` by the event id). Importing
   `public/events.py` of the publisher is a subscription, not a call, for
   `make architecture`.
4. Register the subscriber for the topic in `server/composition/outbox.py`.
   `core-relay` (`manage.py relay_events`) delivers each event after commit
   in a transaction of its own and removes it; a subscriber that raises
   leaves the event for the next run.
5. `make e2e` proves the order reaches the catalog through `core-relay`.

## Add an event of an extracted service

1. A message named as a fact in the past tense in the `.proto` file of the
   publisher (`Greeted`); the subject is `<service>.v<N>.<event>` in snake
   case (`hello.v1.greeted`). `make proto`.
2. Publisher in Rust: the domain owns the event type and a trait,
   `infra/` implements it with `async-nats` and translates the event into
   protobuf; an in-memory fake proves the use case publishes it.
3. Publish only after the data it reports is committed: after `commit()`
   in sqlx; in `core` through the outbox (see above).
4. Consumer in `core`: protocols in `logic/`, a use case that reads them,
   adapters in `infra/` with `nats-py`, a management command as the
   entrypoint and a Compose service that runs it, next to a `nats` service
   with JetStream.
5. Make the consumer idempotent: JetStream may deliver an event again, so
   record the event id in the same transaction as the write and skip ids
   already seen.
6. `make e2e` proves the event travels through every service.

## Extract a module into a service

Only when a split criterion of `AGENTS.md` holds and the human agreed;
name the criterion in the Issue. The module leaves by Strangler Fig: a
service grows next to `core`, the facade of the module switches to it one
operation at a time, and the old code goes only when nothing reaches it.
Each step below is a pull request of its own and leaves the system
working, so the extraction can stop or roll back at any step.

Example: `catalog` leaves the monolith; `orders` keeps asking the
`Catalog` facade for prices and never learns where the answer comes from.

### 1. Make sure the module is ready to leave

- Other modules reach it only through its `public/` package, from their
  `infra/` adapters (`CatalogPrices`); `make architecture` is green.
- What other modules need from it comes through the facade or its events;
  nothing reads its tables or joins them.
- Fix what fails inside the monolith first: extraction does not repair
  boundaries, it freezes them.

### 2. Contract from the public package

`proto/catalog/v1/catalog.proto` maps the public package one to one:

| `public/` of the module | `proto/` |
|-------------------------|----------|
| facade `Catalog` | `service CatalogService` |
| method `product(identifier)` | `rpc Product(ProductRequest) returns (ProductResponse)` |
| transfer object `Product` | `message Product`, a UUID as `string` |
| `UnknownProductError` | status `NOT_FOUND` |
| a fact the module publishes or consumes (`OrderPlaced`) | a message named as the fact, subject `orders.v1.order_placed` |

`make proto` checks it with buf and generates the Python code; commit
`services/core/server/contracts/` with the `.proto` file. The `contracts`
crate compiles it by itself. From now on `make contracts` runs
`buf breaking` against `develop`.

### 3. The service, without traffic

Follow "Add a Rust service". Add what the service needs to
`[workspace.dependencies]` once, with `cargo add` versions: `tokio`,
`tonic`, `axum`, `async-nats`, `sqlx` (features `postgres`,
`runtime-tokio`, `macros`, `uuid`), `tracing`, `tracing-subscriber`
(`json`, `env-filter`), `thiserror`, `anyhow`, `contracts = { path =
"contracts" }`, and `testcontainers-modules` (`nats`, `postgres`) for
tests. They are the agreed stack; show the list to the human anyway.

`main.rs` is the composition root: it reads settings, connects with a
timeout, serves gRPC and the health check, and stops on a signal. A secret
such as `DATABASE_URL` has no default: the service fails at start without
it.

```rust
//! Entry point of the catalog service.

use std::time::Duration;

use catalog::api::endpoint::Products;
use catalog::api::health::{Health, Routes};
use catalog::infra::setting::{Env, Setting};
use contracts::catalog::v1::catalog_service_server::CatalogServiceServer;
use sqlx::postgres::PgPoolOptions;

/// Composition root: wires the catalog service and serves gRPC and health checks.
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt().json().init();
    let pool = PgPoolOptions::new()
        .acquire_timeout(Duration::from_secs(Env::new("DATABASE_TIMEOUT", "5").value().parse()?))
        .connect(&std::env::var("DATABASE_URL")?)
        .await?;
    sqlx::migrate!().run(&pool).await?;
    let grpc = Env::new("CATALOG_GRPC_ADDR", "0.0.0.0:50051").value().parse()?;
    let http = tokio::net::TcpListener::bind(Env::new("CATALOG_HTTP_ADDR", "0.0.0.0:8080").value())
        .await?;
    let stop = || async {
        if let Err(error) = tokio::signal::ctrl_c().await {
            tracing::error!(%error, "cannot listen for the shutdown signal");
        }
    };
    tokio::try_join!(
        async {
            tonic::transport::Server::builder()
                .add_service(CatalogServiceServer::new(Products::new(pool)))
                .serve_with_shutdown(grpc, stop())
                .await
                .map_err(anyhow::Error::from)
        },
        async {
            axum::serve(http, Health.router())
                .with_graceful_shutdown(stop())
                .await
                .map_err(anyhow::Error::from)
        },
    )?;
    Ok(())
}
```

The health check is an object behind a trait, like everything else:

```rust
/// Health check that answers `ok` on `/health`.
#[derive(Debug, Clone, Copy, Default)]
pub struct Health;

impl Routes for Health {
    fn router(&self) -> Router {
        Router::new().route("/health", get(|| async { "ok" }))
    }
}
```

`services/catalog/Dockerfile` builds the whole workspace context, because
the crate needs `proto/` and `contracts/`:

```dockerfile
FROM rust:1-slim-bookworm AS build

RUN apt-get update \
  && apt-get install --no-install-recommends -y protobuf-compiler \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY Cargo.toml Cargo.lock ./
COPY proto ./proto
COPY contracts ./contracts
COPY tools ./tools
COPY services/catalog ./services/catalog

RUN --mount=type=cache,target=/usr/local/cargo/registry \
  --mount=type=cache,target=/src/target \
  cargo build --release --locked -p catalog \
  && cp target/release/catalog /usr/local/bin/catalog


FROM debian:bookworm-slim AS runtime

RUN apt-get update \
  && apt-get install --no-install-recommends -y ca-certificates curl \
  && rm -rf /var/lib/apt/lists/* \
  && useradd --system --uid 1000 catalog

COPY --from=build /usr/local/bin/catalog /usr/local/bin/catalog

USER catalog
EXPOSE 50051 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=10 \
  CMD curl -fsS http://localhost:8080/health || exit 1
ENTRYPOINT ["catalog"]
```

Add its directory to the `docker` entry of `.github/dependabot.yml`.

In `compose.yml`: the service, its own database, and NATS with JetStream.
None of them publishes ports; `core` reaches the service by its name.
Passwords come from `services/catalog/config/.env`, created from a
committed `config/.env.template` with placeholders by the `env` target of
the `Makefile`, extended like the line of `core`.

```yaml
  nats:
    image: "nats:2-alpine"
    restart: unless-stopped
    logging: *logging
    command: ["--jetstream", "--http_port", "8222"]
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8222/healthz"]
      interval: 5s
      timeout: 3s
      retries: 10

  catalog-db:
    image: "postgres:18-alpine"
    restart: unless-stopped
    logging: *logging
    env_file: ./services/catalog/config/.env
    volumes:
      - catalog-data:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 5s
      timeout: 30s
      retries: 5

  catalog:
    build:
      context: .
      dockerfile: ./services/catalog/Dockerfile
    image: "catalog:dev"
    restart: unless-stopped
    logging: *logging
    env_file: ./services/catalog/config/.env
    environment:
      NATS_URL: nats://nats:4222
      RUST_LOG: info
    depends_on:
      catalog-db:
        condition: service_healthy
      nats:
        condition: service_healthy
```

with `catalog-data:` under `volumes:`. `core` gets `CATALOG_GRPC_ADDR: catalog:50051` and `NATS_URL:
nats://nats:4222` in its environment and waits for both with
`condition: service_healthy`. `make architecture` checks that only `core`
publishes ports and that each database serves one deployable.

The schema of the service starts as a copy of the tables of the module, in
plain SQL (`sqlx migrate add`, see "Add a model and a migration"). Red,
green and refactor as usual: the domain in `src/domain/` at 100% coverage,
the endpoint in `src/api/`, queries in `src/infra/` with `sqlx::query!`.

### 4. Copy the data and keep the copy in sync

`core` stays the source of truth during this step; the service only
follows it.

1. Every change of the tables of the module already writes an event to
   the outbox; add the missing ones inside the monolith first
   (`ProductAdded`, `ProductRepriced`), each with a test.
2. `core` publishes these topics to NATS. A subscriber of the relay in
   `server/common/outbox/` sends the payload of the event as the protobuf
   message of the contract to JetStream, with the event id as
   `Nats-Msg-Id` and a timeout from settings, and registers for each topic
   in `server/composition/outbox.py`. It publishes while the relay holds
   the lock of that one outbox row, the only network call allowed inside a
   transaction (see "Data integrity" in `AGENTS.md`); a repeat after a
   failed commit is dropped by JetStream deduplication.
3. The service keeps a stream for its subjects and a durable consumer, and
   writes its copy idempotently: the event id is written in the same
   transaction as the change, and an id it has seen is skipped.
4. Existing rows: a management command of the module in `core` writes one
   event per row to the outbox, so old and new data reach the service
   along one path.

`make e2e` checks that a product added through `core` appears in the
service.

### 5. Switch reads, one operation at a time

1. An adapter of the facade in `server/apps/catalog/infra/remote.py`
   implements `Catalog` over gRPC: the address and the timeout come from
   settings (`CATALOG_GRPC_ADDR`, `CATALOG_GRPC_TIMEOUT` in
   `server/settings/components/services.py` and `config/.env.template`),
   and status codes become the errors of `public/`.

   ```python
   @final
   @attrs.define(slots=True, frozen=True)
   class RemoteCatalog:
       """Adapter: asks the catalog service for products over gRPC."""

       _settings: LazySettings

       def product(self, identifier: UUID) -> Product:
           """Returns the product with the id or raises UnknownProductError."""
           with grpc.insecure_channel(self._settings.CATALOG_GRPC_ADDR) as channel:
               try:
                   found = catalog_pb2_grpc.CatalogServiceStub(channel).Product(
                       catalog_pb2.ProductRequest(id=str(identifier)),
                       timeout=self._settings.CATALOG_GRPC_TIMEOUT,
                   )
               except grpc.RpcError as exc:
                   if exc.code() == grpc.StatusCode.NOT_FOUND:
                       raise UnknownProductError(identifier) from exc
                   raise CatalogUnavailableError(str(exc)) from exc
           return Product(
               id=UUID(found.product.id),
               name=found.product.name,
               price_cents=found.product.price_cents,
               sold=found.product.sold,
           )
   ```

   `grpcio` and `protobuf` join the dependencies of `core` (`poetry add`,
   with `types-grpcio` and `types-protobuf` in the dev group), after the
   human agrees. An unavailable service is an error of `public/` too
   (`CatalogUnavailableError`), which the HTTP API of each caller answers
   with 503.
2. Its tests run against an in-process fake of the service in
   `tests/plugins/catalog/`: a servicer that answers like the real one,
   served on a free local port, with fixtures that point the settings at
   it, at a slow one and at a closed port.

   ```python
   @contextmanager
   def _serving(servicer: catalog_pb2_grpc.CatalogServiceServicer) -> Generator[str]:
       """Serves a fake catalog service on a free local port."""
       server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
       catalog_pb2_grpc.add_CatalogServiceServicer_to_server(servicer, server)
       port = server.add_insecure_port('127.0.0.1:0')
       server.start()
       try:
           yield f'127.0.0.1:{port}'
       finally:
           server.stop(grace=_GRACE).wait()
   ```

3. `server/composition/catalog.py` binds the facade to `RemoteCatalog`.
   When the facade has more than one operation, an object that implements
   it takes each operation from either the stored or the remote
   implementation, and the next pull request moves the next operation.
4. `make e2e`: an order placed through `core` now prices its product
   through the service.

### 6. Switch writes

1. One deploy per write operation: the use case of `core` calls the
   service, and from that deploy on the service owns the data of that
   operation. `core` stops writing those rows; the events of step 4 for
   them stop with it.
2. The service publishes its facts itself, only after `commit()`, to
   JetStream with the event id as `Nats-Msg-Id` (see "Add an event of an
   extracted service").
3. Subscribers of the module inside `core` move with it: the service
   consumes `orders.v1.order_placed` from NATS instead of `RecordedSales`,
   and the topic gets the NATS subscriber of step 4 in
   `server/composition/outbox.py`.
4. Modules of `core` that react to the facts of the service get a
   consumer: a management command with a durable JetStream consumer, its
   own Compose service built from the image of `core`, idempotent by
   event id.

### 7. Delete the module from `core`

When nothing goes through its local code any more:

1. One pull request deletes `logic/`, the stored implementations in
   `infra/`, `admin.py`, the subscribers and their tests. The module keeps
   `public/`, `infra/remote.py` and `api/`: only `core` is public, so the
   HTTP API of the module stays in `core` and calls the service through
   the facade.
2. A second pull request, opened as a draft and made ready only after the
   first one is in production, drops the tables of the module (a contract
   migration, see "Migrations" in `AGENTS.md`).
3. `make patterns`, `docs/architecture.md`, `README.md` and the process
   table of `AGENTS.md` describe the new service.

### 8. Checks at every step

`make contracts` (buf breaking), `make architecture` (ports, databases,
calls between modules), `make rust` and `make mutants` (the service at
100% in `src/domain/`, zero surviving mutants), `make core`, and
`make e2e` with a request that goes through the service.

## Add a model and a migration

Django:

1. Change `models.py`, then
   `docker compose run --rm web python manage.py makemigrations <app>`;
   one logical change per migration.
2. Backward compatible only (expand → deploy → contract): a new table, a
   nullable column or one with a default, a backfill; never a `DROP`, a
   rename, `SET NOT NULL` or a new `UNIQUE` together with the code that
   stops using the old shape.
3. Reversible where feasible: `RunPython` with `reverse_code`.
4. A large backfill raises its own limits for its transaction:
   `migrations.RunSQL("SET LOCAL lock_timeout = '30s'")` before it.
5. Red/green for the code that uses the model; `make core` runs the
   migration linters, `makemigrations --check` and migration tests.

Rust (sqlx):

1. `sqlx migrate add <name>` in the crate of the service; plain SQL, the
   same rules as Django.
2. Start the migration with `SET LOCAL lock_timeout = '5s';` and
   `SET LOCAL statement_timeout = '15s';`.
3. Write a `down` file where the change can be undone.
4. Queries only with `sqlx::query!` and `sqlx::query_as!`, mapped into
   immutable domain objects in `infra/`.

## Remove the example

Once the first real module exists, in its own pull request:

1. `services/core/server/apps/catalog/` and `server/apps/orders/`, their
   lines in `INSTALLED_APPS`, their API routers and page routes in
   `server/urls.py`, `server/composition/catalog.py` and `orders.py`
   with their calls in `server/implemented.py`, the `OrderPlaced`
   subscription in `server/composition/outbox.py`, their tests in
   `tests/test_apps/test_catalog/` and `tests/test_apps/test_orders/`.
2. The `images` service, unless the product keeps photos:
   `services/images/` and its workspace member, `proto/images/` and the
   generated `server/contracts/images/` (`make proto`), the service and
   `IMAGES_GRPC_ADDR` in `compose.yml`, `server/settings/components/services.py`
   with its line in `server/settings/__init__.py` and the `IMAGES_*` lines
   of `config/.env.template`, `grpcio`, `protobuf` and their stubs
   (`poetry remove`), the Docker directory in `.github/dependabot.yml`.
3. The Rust extension module, unless the product needs heavy computation:
   `services/core/native/`, the `native_build` stage and the wheel lines
   of `docker/django/Dockerfile`, the `NATIVE` lines of the `Makefile`,
   its Dependabot directory, `ranking` in `known_first_party` of
   `pyproject.toml`, the `target-lexicon` exception of `deny.toml` and
   the `exclude` of the root `Cargo.toml`.
4. The checks that walk the example, rewritten for the new module, not
   only pointed at it: the requests of `scripts/e2e.sh`, the product page
   of `tests/browser/` (the theme switcher stays unless the product drops
   it), and the tests of the architecture checks that build their
   registries from the real `server.apps.catalog` and `orders`
   (`tests/test_scripts/test_keys.py`, `test_relations.py`,
   `test_facade_transactions.py`).
5. `make patterns`, `make check`.
