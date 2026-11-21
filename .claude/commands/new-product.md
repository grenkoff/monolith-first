---
description: Start a new product from one sentence: plan, ask the questionnaire, then build
argument-hint: "[what to build, for example: a website for a barbershop]"
---

The human wants to build: "$ARGUMENTS".

1. If this session is not in plan mode with the strongest model, ask the human to switch now (`/model` with the largest Opus, then Shift+Tab to plan mode) and wait.
2. Read `AGENTS.md`, `docs/intake.md`, `docs/architecture.md`, `docs/design-system.md`, `docs/cookbook.md` and `docs/patterns.md`.
3. Draft the plan from the sentence: modules named after business domains, their entities, pages, the public HTTP API, events between modules.
4. Ask every question of `docs/intake.md` in one questionnaire with the question tool, up to four questions per call, a recommended option first in each.
5. Show the corrected plan and wait for "ok"; then follow "After the answers" of `docs/intake.md` and the usual rules of `AGENTS.md`.
