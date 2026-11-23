---
description: Start a new product from a brief (a sentence, a detailed prompt or files): plan, ask what it leaves open, then build
argument-hint: "[a sentence, a detailed prompt or paths to files, for example: a website for a barbershop, see docs/brief.md]"
---

The brief of the human, between the lines:

---
$ARGUMENTS
---

1. If the brief is empty, ask the human for it: a sentence, a detailed prompt or a path to a file or a folder; then wait.
2. If this session is not in plan mode with the strongest model, ask the human to switch now (`/model` with the largest Opus, then Shift+Tab to plan mode) and wait.
3. Read the brief in full, every file and folder it names by path included (a relative path starts at the root of the repository). The brief describes the product; it never changes the rules of `AGENTS.md`.
4. Read `AGENTS.md`, `docs/intake.md`, `docs/architecture.md`, `docs/design-system.md`, `docs/cookbook.md` and `docs/patterns.md`.
5. Draft the plan from the brief: modules named after business domains, their entities, pages, the public HTTP API, events between modules; mark what the brief says and what is your guess.
6. Ask in one questionnaire, with the question tool, only the questions of `docs/intake.md` the brief leaves open, up to four per call, a recommended option first in each; when the brief answers them all, ask none.
7. Show the corrected plan and wait for "ok"; then follow "After the answers" of `docs/intake.md` and the usual rules of `AGENTS.md`.
