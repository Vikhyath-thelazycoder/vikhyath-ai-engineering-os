# Domain model

| Domain | Purpose | Example capabilities | Main sources |
|---|---|---|---|
| engineering | Build and change software | architecture, backend, frontend, security, planning, review, release, debugging, completion, principles, simplicity | ECC, Addy, Agency, gstack, Unlazy, Karpathy, Ponytail |
| codebase | Understand an existing project first | repository-understanding, impact-analysis, code-search | Graphify, ECC |
| design | Visual and interaction design | design-direction, ux, design-system, frontend (incl. native mobile), motion, accessibility, typography, brand | Taste, Open Design, UI/UX Pro Max, Appllama |
| testing | Local test-first verification | local-verification, security, regression, performance, accessibility, release-verification, evidence | ECC, gstack, Addy |
| seo | Search and answer-engine visibility | auditing, technical, on-page, keyword-research, ai-search, entity, reporting, website-work | BeyondSEO |
| media | Launch material | launch-video, demo, presentation, showcase | Brag |
| observability | Events and risk detection | events, sessions, token-metrics, risk-detection | Beacon |

Rules that cross domains:

- New projects start with requirements (no codebase step); existing projects start with codebase impact analysis.
- Design, SEO and media requests never activate engineering unless the route selects it.
- Browser use exists only inside the SEO runtime (rendered captures, opt-in) and media rendering; it is never
  engineering verification.
- Engineering, codebase and testing routes carry the lifecycle (`config/lifecycle.yaml`).
