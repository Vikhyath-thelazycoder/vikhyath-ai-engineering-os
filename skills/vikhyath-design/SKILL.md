---
name: vikhyath-design
description: UI/UX and visual design work — direction, design systems, typography, motion, native mobile — through the routed design capabilities, the UI/UX Pro Max engine and local design-token checks.
---

# Vikhyath Design

1. **Route:** `vikhyath route "<request>" --paths <files…>` and load only what it selects with
   `vikhyath context <id>…` (mobile/native requests load the merged native-mobile rules in `design/frontend`).
2. **Decisions first:** `vikhyath decide list --kind design`; keep to recorded brand and system decisions, and
   record new ones with `vikhyath decide add --kind design …`.
3. **Engine** (read-only unless persisted):
   `vikhyath design search "<query>" --domain style|color|typography|ux …`,
   `vikhyath design system "<product + tone>" [--persist]` (writes `design-system/` in this project only).
4. **Verify locally:** `vikhyath design check` (accent hues, grey families, radii, fonts against
   `config/design.yaml`) plus the project's component/a11y tests. Never verify by screenshot or browser; report
   look-and-feel judgements as NOT_TESTED for the user to confirm.

Design requests do not activate engineering or SEO capabilities unless the route selects them.
