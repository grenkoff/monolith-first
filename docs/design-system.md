# Design system

Every page of the site is built from one design system, so a page added
later looks like the rest of the site in whichever theme the project
chose. The rules are in "Frontend" of [`AGENTS.md`](../AGENTS.md); this
page lists what the design system holds. `GET /design/` shows all of it
in every theme.

## Files

| File | What it holds |
|------|---------------|
| `services/core/server/common/django/styles/themes.css` | the themes: one block `[data-theme="<name>"]` per theme that sets every token |
| `services/core/server/common/django/styles/site.css` | Tailwind with its default palette, fonts, radii and shadows switched off, the tokens as Tailwind values, the components |
| `services/core/server/common/django/templates/layout/base.html` | the layout every page extends; `data-theme` on `<html>`; the blocks `home`, `navigation` and `footer` |
| `services/core/server/templates/site/layout.html` | the layout of the site: its navigation and footer links, extended by every page of a module |
| `services/core/server/common/django/templates/design/index.html` | the page `/design/` |
| `services/core/scripts/design.py` | the check run by `make core` |

## Tokens

A theme sets each token as a CSS variable `--ds-<token>`; Tailwind reads
them as its only values, so a template writes `bg-surface`,
`text-ink-muted`, `rounded-card`, `font-heading`, `shadow-card`.

| Token | Tailwind | Used for |
|-------|----------|----------|
| `surface` | `bg-surface` | background of the page |
| `surface-raised` | `bg-surface-raised` | cards, header, panels |
| `ink` | `text-ink` | text |
| `ink-muted` | `text-ink-muted` | secondary text |
| `line` | `border-line` | borders and dividers |
| `accent` | `bg-accent`, `text-accent` | primary actions, links |
| `accent-ink` | `text-accent-ink` | text on the accent |
| `danger` | `text-danger`, `border-danger` | errors |
| `font-body`, `font-heading` | `font-body`, `font-heading` | text and headings |
| `radius-control`, `radius-card` | `rounded-control`, `rounded-card` | buttons and fields, cards |
| `shadow-card` | `shadow-card` | raised elements |

Spacing, sizes, layout and responsive variants are the ones of Tailwind:
they carry no brand.

## Themes

| Theme | Look |
|-------|------|
| `classic` | white and slate, blue accent, serif headings, small radii |
| `warm` | cream and brown, terracotta accent, rounded type, pill buttons, soft shadows |
| `bold` | near black, lime accent, monospace headings, square corners, no shadows |

The site picks one with `DJANGO_THEME`; a value outside the list stops
the start. To add a theme, add its block to `themes.css` with every
token and its name to `SITE_THEMES` in
`server/settings/components/common.py`. To brand a theme for a project,
change its tokens, never the components.

## Components

| Class | What it is |
|-------|------------|
| `ds-container` | page width with side gutters |
| `ds-heading`, `ds-subheading` | headings |
| `ds-muted` | secondary text |
| `ds-link` | link |
| `ds-button` | primary action |
| `ds-button-quiet` | secondary action |
| `ds-card` | raised block |
| `ds-field` | label around a control |
| `ds-input` | text and number field |
| `ds-alert` | error message |
| `ds-price` | amount of money |
| `ds-header`, `ds-footer` | header and footer of the layout |

A new component is a class in `site.css` built only from tokens and
Tailwind utilities, shown on `/design/` in every theme.

## Checks

`python -m scripts.design` (in `make core`) fails when:

- a template uses a colour of the default Tailwind palette
  (`text-gray-600`, `bg-white`), an arbitrary value in brackets
  (`mt-[13px]`, `bg-[#fff]`) or a `style` attribute;
- a theme misses a token;
- text and its background in a theme have a contrast below 4.5:1 (WCAG
  AA): ink and muted ink on the surface, ink on raised surfaces, the
  accent on the surface, accent ink on the accent, danger on the surface.

Since Tailwind knows only the tokens, a palette class that slips through
generates no CSS at all.
