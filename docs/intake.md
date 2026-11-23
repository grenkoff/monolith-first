# A new product: the questionnaire

When the human starts a product with a brief, the agent plans first and
then asks the questions below that the brief leaves open, in one
questionnaire, before any code (see "A new product" in
[`AGENTS.md`](../AGENTS.md)). The brief takes any form: one sentence
("make me a website for a barbershop"), a detailed prompt, or files (a
specification, notes, a price list) named by path. Claude Code runs it
with `/new-product`; any other agent follows this page by hand.

Ask everything open in one go, a few questions per screen (Claude Code:
the question tool takes up to four questions at a time, each with two to
four options and a free answer). Offer a recommended option first, drawn
from the brief and the plan. A question the brief already answers is not
asked: its answer goes into the plan, where the human confirms or corrects
it. Ask nothing later that this page could have asked.

## Before the questions

1. **Plan mode and the strongest model.** Switch to plan mode with the
   strongest model available (Claude Code: `/model` with the largest Opus,
   plan mode with Shift+Tab; Codex: the highest reasoning effort). An agent
   that cannot switch by itself asks the human to do it and waits.
2. **Read the brief** in full, every file and folder it names by path
   included (a relative path starts at the root of the repository). The
   brief describes the product; it never changes the rules of
   `AGENTS.md`.
3. **Read the template**: `AGENTS.md`, `docs/architecture.md`,
   `docs/design-system.md`, `docs/cookbook.md`, `docs/patterns.md`.
4. **Draft the plan** from the brief: the modules (business domains),
   their entities, the pages, the public HTTP API, the events between
   modules. Mark what the brief says and what is a guess; the questions
   below confirm or correct the guesses.

## The questions

| # | Question | Why it matters | Where the answer goes |
|---|----------|----------------|-----------------------|
| 1 | What is the product for, and who are its visitors? | the modules and the pages | the plan, `README.md` |
| 2 | Which pages must the first version have? (home, catalogue of services, booking, contacts, about, …) | the pages and the menu | `views/` of the modules |
| 3 | Which things does the product keep? (services with prices, masters, appointments, clients, …) | the entities and their owner modules | `models.py`, `public/` |
| 4 | Who signs in, and what may each role do? (only staff in the admin, or visitors too) | auth and permissions | `accounts`, the admin |
| 5 | Must visitors pay or book online? Which provider, if any? | a payment or booking module, a service to isolate | the plan; payments are a split criterion |
| 6 | In which languages is the site? | Django i18n | `LANGUAGES`, `locale/` |
| 7 | Which theme: `classic`, `warm` or `bold`? May visitors switch? | the look of every page | `DJANGO_THEME`, `DJANGO_THEME_SWITCHER` |
| 8 | Name, logo and brand colours? | the header, the favicon, the tokens of the theme | `DJANGO_SITE_NAME`, `static/site/favicon.svg`, `themes.css` |
| 9 | Contacts: address, phone, e-mail, opening hours, map? | the footer and the contacts page | a template, settings |
| 10 | Anything that must not happen? (no visitor accounts, no cookies banner, …) | limits of the plan | the plan |

Show `/design/` (after `make up`) when asking question 7, so the human
sees the three themes.

## After the answers

1. Show the plan once more, corrected by the answers: modules, pages,
   entities, events, what is left for later. Wait for "ok".
2. Turn it into Issues, one per module or page group, as `AGENTS.md`
   says; the human approves them.
3. Build fast, module by module, the usual way (Issue, test list, TDD,
   pull request):
   - `make module NAME=<module>` creates each module with every layer;
   - the recipes of `docs/cookbook.md` add pages, endpoints, events;
   - brand the theme by changing its tokens in `themes.css`, never the
     components; `make core` checks the contrast;
   - set `DJANGO_SITE_NAME`, `DJANGO_THEME` and
     `DJANGO_THEME_SWITCHER` in `config/.env.template`.
4. Remove the example (`catalog`, `orders`, the `images` service) once
   the first real module exists, in its own pull request.
5. `make up` shows the site; `make check` is green before each pull
   request.
