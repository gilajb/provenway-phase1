# Provenway

Construction-industry professional network with proof-of-work portfolios, targeting the Kenyan
market (LinkedIn-adjacent, sector-specific). Monorepo: Django 5 / DRF backend (`provenway-backend/`)
+ React/Vite frontend (`provenway-frontend/`). Dev environment: Windows / PowerShell / Python 3.12.

Solo developer. Work is session-scoped — one feature area per session, adjacent concerns are named
and explicitly deferred rather than built speculatively.

## Reference docs (read before starting new feature work)

- @docs/engineering-doc.md — authoritative schema, API, and permission spec (SRS/PRD/System
  Design/DB Design/API Design/Security/Roadmap). Sections cited as e.g. "§3.2.3" refer here.
- @docs/build-plan.md — the actual build sequence for a solo developer, phase-by-phase,
  with Definition of Done per week. This is the plan to follow day-to-day; the engineering doc
  is the detail reference.
- @docs/DESIGN.md — design tokens: colors, typography, spacing, component styling
  ("Architectural Precision" system — deep blues, coral accent, teal success, Inter typeface).

## Current backend status (apps fully/substantially built)

- `authentication` — custom User model (UUID PK, email login), JWT (RS256 prod / HS256 dev),
  email verification, password reset, rate limiting, AuthAuditLog. Celery wired via
  `core/apps.py:ready()` (not `provenway/__init__.py` — avoids Windows circular import).
- `profiles` — `Profile` (one-to-one with `User`) is the single source of truth for bio,
  location, avatar_url, disciplines. `disciplines` serializer field is a flat string list
  (`["x"]`), not `[{"discipline": "x"}]` — frontend consumers must match this shape.
- `projects` — full CRUD, soft-delete, visibility tiers. `visible_projects_q()` in
  `apps/projects/permissions.py` is the single authoritative visibility helper — route all
  surfaces (list, detail, feed, build log) through it rather than duplicating checks.
- `build_log` — ProjectUpdate + UpdatePhoto (max 10/update), 24h edit window anchored on
  server `created_at`, EXIF JSONB, rate limiting on uploads.
- `networking` — Follow model (UUID surrogate PK — Django 5.0 doesn't support composite PKs),
  mutual follow = connection.
- `feed` — cursor pagination uses a hand-rolled keyset paginator on `(created_at, id)` —
  DRF's built-in cursor pagination is unsafe for equal timestamps.
- Directory search — PostgreSQL FTS with GIN index, Haversine geo radius (no PostGIS).

Not yet built: jobs/tenders apps, messaging, notifications, co-signatures, admin ban endpoint +
JWT force-revoke, `/feed/discover/` and `/feed/trending/`, WhiteNoise middleware wiring, Sentry
initialization.

## Fixed architecture decisions — do not revisit

- UUID PKs everywhere; soft deletes (`is_deleted` + `deleted_at`) on user-generated content
- `created_at` is server-set, never client-set; `entry_date` is the user-set work date — keep separate
- Direct-to-Cloudinary upload — Django only issues signed upload params, never receives file bytes
- Explicit field whitelist on every DRF serializer — never `__all__`
- Composite PKs unsupported in Django 5.0 → UUID surrogate PK + `UniqueConstraint` instead
- `psycopg[binary]` (psycopg3), not `psycopg2-binary`, for Windows wheel compatibility
- React (Vite), not Next.js, for the frontend
- Shared permission/visibility helpers over per-endpoint duplication

## Conventions

- Backend: real PostgreSQL for migrations/tests (not SQLite/mocks); ruff + black; regression
  test required for every bug fix; non-obvious decisions documented inline as comments.
- Frontend: CSS Modules with `tokens.css` exclusively (no hardcoded values); reuse existing UI
  primitives; `vite build` + ESLint clean before delivery. `react/prop-types` warnings are a
  pre-existing baseline, not a regression to fix.
- Deliverable format: complete project zip (excluding `node_modules`, `dist`), preserving
  folder structure, after each session.

## Commands

<!-- Fill in your actual commands so Claude Code doesn't have to guess -->
- Backend: `cd provenway-backend && venv\Scripts\activate && python manage.py runserver`
- Backend tests: `cd provenway-backend && python manage.py test`
- Frontend: `cd provenway-frontend && npm run dev`
