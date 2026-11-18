# Contracts

gRPC contracts between `core` and the services extracted from it. A module that stays in the monolith needs none: its contract is its `public/` package.

Each contract lives in `proto/<service>/v<N>/<service>.proto` with the package `<service>.v<N>` (see "Contracts" in `AGENTS.md`). `make proto` checks every contract here with buf and generates the Python code in `services/core/server/contracts/`; the `contracts` crate generates the Rust code at build time. With no contract here, both stay empty and the checks pass.
