# Provenway — Build Plan
**Version 2.0 | June 2026**
*Based on Provenway Engineering Documentation v1.0 and Project Documentation.*
*Joy is the sole developer. Clinton (CEO) is the Product Owner. The Engineering Doc is the authoritative spec for all schema, API, and permission details — this plan tells you what to build in what order and what "done" means at each step.*

---

## Team

| Role | Person | Responsibility |
|---|---|---|
| Developer (full-stack) | Joy | Everything: Django backend, React frontend, deployment, QA |
| CEO / Product Owner | Clinton | Product decisions, user outreach, beta cohort recruitment, content seeding, launch |

> **Solo developer reality check:** This is a 6–9 month build at serious hours. The phases below are sequenced so you are never building the wrong thing first and never blocked waiting on yourself. Do not run parallel tracks — you are one person. Finish each week's backend before starting that week's frontend.

---

## Day 1 Setup (Before Writing Any Business Logic)

- [ ] GitHub monorepo: `provenway/` with `backend/` and `frontend/` subdirectories
- [ ] Render account — Web Service (backend) + PostgreSQL + Redis
- [ ] Vercel account — frontend
- [ ] Cloudinary account — free tier, **create a signed upload preset immediately**
- [ ] Resend account — transactional email
- [ ] Sentry — free tier, error tracking from day 1
- [ ] PostHog — free tier, product analytics (you need to know if users come back)
- [ ] Linear or Notion — task board, one ticket per checklist item below
- [ ] GitHub Actions CI: test + lint on every PR, auto-deploy to staging on merge to `main`

**Build order rule:** Backend first, frontend second, for every feature. Test every endpoint in Postman before building the UI for it.

---

## Phase 1: Foundation (Weeks 1–8)

**Goal:** Auth, profiles, and the build log working end-to-end. Deployed on real infrastructure. Clinton recruits 20–50 real users to test it.

The single question Phase 1 answers: *will real construction professionals actually log their work?* Nothing in Phase 2 matters if the answer is no.

---

### Week 1–2: Infrastructure + Auth

**Backend**
- [ ] Django project scaffolded — split settings: `provenway/settings/base.py`, `development.py`, `production.py`, `test.py`
- [ ] `core/` base models: `UUIDModel`, `TimestampedModel`, `SoftDeleteModel` — everything inherits from these
- [ ] Custom User model (`apps/authentication/models.py`) — **do this before any other migration, you cannot cleanly change it later**
  - UUID PK, email (unique), phone (nullable), password_hash, display_name, headline, bio, location_text, location_lat/lng, avatar_url, is_verified, is_active, subscription_tier ENUM, created_at, updated_at
  - *Full schema: Engineering Doc §3.2.1*
- [ ] `user_disciplines` join table
- [ ] JWT auth endpoints (djangorestframework-simplejwt):
  - `POST /auth/register/` — email + password, triggers verification email
  - `POST /auth/verify-email/` — 24-hour token
  - `POST /auth/login/` — returns access (15-min TTL) + refresh (30-day TTL) tokens
  - `POST /auth/token/refresh/`
  - `POST /auth/logout/` — revokes refresh token
  - `POST /auth/password-reset/request/`
  - `POST /auth/password-reset/confirm/`
  - *Full spec: Engineering Doc §5.2 Auth endpoints*
- [ ] `auth_tokens` table — hashed refresh tokens, revoked_at field
- [ ] Email verification via Resend API (not Django's default SMTP)
- [ ] Rate limiting on auth endpoints: 10 req/min per IP (use `django-ratelimit`)
- [ ] Deployed to Render staging — CI auto-deploys on merge to `main`

**Frontend**
- [ ] React.js project (Create React App or Vite) — **not Next.js, per your stack choice**
  - `src/pages/` — auth pages: `Login.jsx`, `Register.jsx`, `ResetPassword.jsx`
  - `src/components/` — shared UI components
  - `src/hooks/` — `useAuth.js`, etc.
  - `src/lib/api/` — `apiClient.js` (fetch wrapper with auth headers + token refresh)
  - `src/stores/` — Zustand: `authStore.js`
  - `src/utils/` — date formatters, image URL helpers
- [ ] Auth pages with real API calls to Django
- [ ] JWT token handling: store access token in memory, refresh token in HttpOnly cookie
- [ ] Protected route wrapper — redirect to login if not authenticated
- [ ] Deployed to Vercel

**Definition of Done:** Register → verify email → login → reach dashboard. Full flow works in browser. Postman collection covers all auth endpoints with passing tests.

---

### Week 2–3: User Profiles

**Backend**
- [ ] `apps/profiles/` — serializers + views:
  - `GET /users/me/` — own profile (full data)
  - `PATCH /users/me/` — update own profile (explicit field whitelist, never `__all__`)
  - `GET /users/{id}/` — public profile (visibility-appropriate fields)
- [ ] Avatar upload: **direct-to-Cloudinary via signed upload preset** — Django only issues the signed params, never receives the file bytes
- [ ] Contact visibility settings: email/phone shown to connections-only or hidden (`FR-PROF-06`)
- [ ] `IsOwnerOrReadOnly` permission class in `core/permissions.py`

**Frontend**
- [ ] Profile page (`/profile/:id`) — view mode
- [ ] Profile edit form — name, headline, bio, location, disciplines (multi-select from taxonomy), avatar upload direct to Cloudinary
- [ ] `VerifiedBadge` component, `DisciplineTags` component

**Definition of Done:** User signs up, fills profile, uploads photo, and their profile is publicly viewable at `/profile/:id`.

---

### Week 3–5: Build Log — Projects

**Backend**
- [ ] `apps/build_log/` — Project model:
  - UUID PK, owner_id (FK → users), title, description, location_text + lat/lng, status ENUM (active/completed/paused/cancelled), visibility ENUM (public/connections/private), start_date, end_date, is_deleted, created_at
  - *Full schema: Engineering Doc §3.2.3*
- [ ] `project_disciplines` join table
- [ ] CRUD endpoints:
  - `POST /projects/`
  - `GET /projects/` — list with filters (owner, status, discipline)
  - `GET /projects/{id}/` — visibility enforced
  - `PATCH /projects/{id}/` — owner only
  - `DELETE /projects/{id}/` — soft delete, owner only
- [ ] `ProjectVisibilityPermission` — enforces public/connections/private at object level

**Frontend**
- [ ] Project creation form (title, disciplines, location, status, visibility, start date)
- [ ] Project listing on profile page
- [ ] Project detail page `/projects/:id`
- [ ] `ProjectCard` component

**Definition of Done:** Owner creates, edits, deletes a project. Private project returns 404 to non-owner (not 403 — don't confirm existence).

---

### Week 3–6: Build Log — Updates + Photos
*(Start this in Week 4 once Project CRUD backend is done — runs overlapping with Week 3–5 frontend)*

This is the core differentiator. Build it carefully.

**Backend**
- [ ] `ProjectUpdate` model:
  - UUID PK, project_id, author_id, title, body (rich text, sanitised), entry_type ENUM (milestone/daily_log/issue/inspection/phase_complete), **entry_date** (DATE — the actual work date), geotag_lat/lng, exif_metadata (JSONB), is_deleted, **created_at** (server-set, never client-set)
  - **Critical:** `created_at` and `entry_date` are different fields for a reason. Never let the client set `created_at`.
- [ ] `UpdatePhoto` model: update_id, cloudinary_public_id, url, sequence_order (0–9 max)
- [ ] CRUD endpoints for updates (`/projects/{id}/updates/`) — *see Engineering Doc §5.2 Build Log*
- [ ] Cloudinary direct upload for photos — Django issues signed params only
- [ ] Celery task: `process_image_metadata` — extract EXIF from uploaded photos, store in `exif_metadata`
  - This requires Redis (for Celery broker) — set up Redis on Render now
- [ ] Index: `project_id + entry_date DESC` for timeline queries

**Frontend**
- [ ] Update creation form: title, body (use Quill or Tiptap for rich text), entry type selector, date picker for `entry_date`, photo uploader (max 10, direct to Cloudinary, progress indicator)
- [ ] Timeline view on project page — reverse-chronological, filterable by entry type
- [ ] `UpdateTimeline`, `UpdateEntry`, `PhotoGrid` components

**Definition of Done:** User logs a dated update with photos. Timeline renders correctly. Photos served from Cloudinary CDN. Server `created_at` is not overridable from the client.

---

### Week 5–6: Follow / Unfollow

**Backend**
- [ ] `follows` table: composite PK (follower_id, following_id), created_at
- [ ] `blocks` table
- [ ] Endpoints:
  - `POST /users/{id}/follow/`
  - `DELETE /users/{id}/follow/`
  - `GET /users/{id}/followers/`
  - `GET /users/{id}/following/`

**Frontend**
- [ ] Follow/unfollow button on profile pages
- [ ] Optimistic UI update (increment count immediately, rollback on API failure)
- [ ] Follower / following counts on profile header

**Definition of Done:** User A follows User B. Count updates instantly. Unfollow removes correctly.

---

### Week 6–7: Directory Search

**Backend**
- [ ] `GET /users/` — query params: `q`, `discipline`, `location`, `is_verified`
- [ ] PostgreSQL Full-Text Search using Django's `SearchVector` on `display_name + headline + bio`
- [ ] Composite index: `subscription_tier, is_verified`
- [ ] Offset-based pagination

**Frontend**
- [ ] Search page `/search` — text input + filter panel (discipline dropdown, location, verified toggle)
- [ ] Results list using `ProfileCard` component
- [ ] Loading skeleton + empty state

**Definition of Done:** Search "civil engineer Nairobi" returns filtered, paginated results with verified badge visible.

---

### Week 7–8: Home Feed

**Backend**
- [ ] `GET /feed/` — updates from followed users, reverse-chronological, cursor-paginated
- [ ] Query: `project_updates WHERE author_id IN followed users` + visibility check
- [ ] Index: `author_id + created_at DESC`
- [ ] `GET /feed/trending/` — public updates, by recency, for logged-out users

**Frontend**
- [ ] Feed page `/feed` — infinite scroll (cursor-based), `UpdateEntry` cards
- [ ] Empty state: "Follow professionals to see their updates"
- [ ] Trending feed on landing page (logged-out)

**Definition of Done:** After following 3 users, feed shows their updates in order. Scroll loads next page without duplicates.

---

### Week 8: Permission Audit + Beta Launch

**Permission Audit (do not skip)**
- [ ] Every endpoint checked against the permission matrix (*Engineering Doc §2.5 and §4.3.2*)
- [ ] Test suite for permission failures: 401, 403, 404 (hidden resource)
- [ ] Specific cases:
  - Private project → 404 to non-owner
  - Connection-only project → visible only to mutual followers
  - Cannot PATCH another user's profile
  - Cannot delete another user's project or update
- [ ] OWASP ZAP basic scan on staging — fix all critical/high findings

**Beta Launch**
- [ ] Clinton recruits 20–50 real construction professionals
- [ ] Each user onboarded: profile complete + at least 1 project + 1 update logged
- [ ] Observe: do they log a second update without being prompted? (Track in PostHog)
- [ ] Collect feedback: upload friction, mobile experience, missing fields

**Phase 1 done when:** 20+ real users are active with real project updates logged.

---

## Phase 2: Full Feature Build (Weeks 9–20)
**You are one developer. Do not run parallel tracks. Build each track sequentially, backend-first within each.**

Prioritised order below is based on: user value, dependency order, and revenue impact.

---

### Track A — Notifications (Weeks 9–11)
*Build this first in Phase 2 — every later feature (messaging, jobs, tenders, co-signs) generates notifications.*

| Week | Deliverable |
|---|---|
| 9 | `apps/notifications/`: Notification model, type ENUM (follow, message, application, endorsement, profile_view, cosign_request). Celery async task `create_notification` |
| 9–10 | Endpoints: `GET /notifications/`, `POST /notifications/{id}/read/`, `POST /notifications/read-all/`, `GET+PATCH /notifications/preferences/` |
| 10 | Frontend: notification centre, unread badge count |
| 10–11 | Email digest: Celery Beat cron at 6 AM EAT via Resend |
| 11 | WebSocket push for real-time badge: `wss://.../ws/notifications/` (Django Channels + Redis) |

*Ref: Engineering Doc §4.4, §4.5, §5.2 Notifications*

---

### Track B — Messaging (Weeks 11–14)

| Week | Deliverable |
|---|---|
| 11–12 | `apps/messaging/`: Conversation, ConversationParticipant, Message models. DRF API: `GET /conversations/`, `POST /conversations/`, `GET /conversations/{id}/messages/`, `POST /conversations/{id}/messages/` |
| 12–13 | Django Channels WebSocket consumer (`consumers.py`) + Redis channel layer. Route: `wss://.../ws/chat/{conversation_id}/` |
| 13–14 | Frontend: ConversationList, MessageThread, MessageInput. Real-time via WebSocket. File attachment. Soft-delete (sender only, within 1 hour). |

*Ref: Engineering Doc §4.4, §5.2 Messaging*

---

### Track C — Professional Verification (Weeks 14–15)

| Week | Deliverable |
|---|---|
| 14 | `verification_credentials` model. `POST /credentials/`, `GET /credentials/me/`. Admin review queue: `GET /admin/verification-queue/`, `POST /admin/verification-queue/{id}/review/` |
| 15 | Frontend: credential upload form, status display. `VerifiedBadge` wired to `is_verified` flag on profile. |

---

### Track D — Co-Signatures (Weeks 15–16)

| Week | Deliverable |
|---|---|
| 15 | `update_cosignatures` model. `POST /projects/{id}/updates/{uid}/cosign/` (invite), `POST .../cosign/confirm/` (confirm/decline). Notification to invitee. |
| 16 | Frontend: co-sign invite button on update entries. `CoSignBadge` component. Pending/confirmed display. |

---

### Track E — Project Collaboration Board (Weeks 16–17)

| Week | Deliverable |
|---|---|
| 16 | Project opportunity model (scope, disciplines, budget, location, timeline). `POST /project-board/`, `GET /project-board/` with filters |
| 16–17 | Application workflow: apply, shortlist, interview, offer, accept. API + frontend (opportunity card, discovery page, application modal with build log entry selector) |

---

### Track F — Job Board + Recruitment (Weeks 17–18)

| Week | Deliverable |
|---|---|
| 17 | `organisations`, `org_members`, `jobs`, `job_applications` models — *Engineering Doc §3.2.4*. Job board API: `GET /jobs/`, `POST /jobs/`, `POST /jobs/{id}/apply/` |
| 18 | Application tracking (ATS kanban): `GET /jobs/{id}/applications/`, `PATCH /jobs/{id}/applications/{aid}/`. Frontend: JobCard, job board page, application form, recruiter board |

---

### Track G — Tender Marketplace (Weeks 18–19)

| Week | Deliverable |
|---|---|
| 18 | `tenders` + `tender_bids` models — *Engineering Doc §3.2.5*. Tender API: `GET /tenders/`, `POST /tenders/`, `POST /tenders/{id}/bid/`, `GET /tenders/{id}/bids/`, `POST /tenders/{id}/award/` |
| 19 | Frontend: TenderCard, tender listing, bid submission modal, bid comparison view for tender owner |

---

### Track H — Portfolio PDF Export (Week 19)

| Week | Deliverable |
|---|---|
| 19 | Celery task `generate_portfolio_pdf` (WeasyPrint): project title, all updates chronologically, photos, cosignature badges, QR code → stored in Cloudinary |
| 19 | `GET /projects/{id}/export-pdf/` (async → returns task_id). `GET /tasks/{task_id}/` to poll. Frontend: export button + progress + download link |

---

### Track I — Admin Panel (Week 20)

| Week | Deliverable |
|---|---|
| 20 | Custom Django Admin: user management (ban, deactivate, set subscription tier), content moderation queue, verification queue |
| 20 | Analytics API `GET /admin/analytics/`: DAU/MAU, posting rates, subscription MRR |
| 20 | Report queue: `GET /admin/reports/`, `POST /admin/reports/{id}/action/` |
| 20 | React admin dashboard at `/admin` (separate layout, staff-only guard) |

---

### Track J — Billing (Weeks 21–23)
*Build last. Do not charge users before the product has proven value.*

| Week | Deliverable |
|---|---|
| 21 | M-Pesa Daraja API: STK Push for KES subscriptions. Idempotent webhook handler. Celery task `sync_subscription_status`. |
| 22 | Stripe for USD/international. Webhook handler. |
| 23 | Subscription tier enforcement wired across all Pro/Pro+/Firm gated features. Free user hitting gated endpoint → 402 with upgrade prompt. |

*Ref: Engineering Doc §2.3 Subscription Model*

---

## Phase 3: Launch Readiness (Weeks 21–24)

| Activity | Owner | Definition of Done |
|---|---|---|
| Recruit 50–150 launch-cohort professionals | Clinton | Real professionals signed up; project board + job board seeded with genuine postings |
| Mobile QA — iOS Safari + Android Chrome on 3G throttle | Joy | Upload, feed, messaging all work under throttled connection |
| OWASP ZAP scan + full permission audit | Joy | All critical/high findings resolved |
| Kenya DPA 2019 legal review | Clinton + legal advisor | Privacy policy live; `/users/me/data-export/` and `DELETE /users/me/` verified |
| Onboarding flow — guided first-project creation | Joy | New user completes first update in first session (tracked in PostHog) |
| Custom domain | Clinton | provenway.co.ke or provenway.com → Vercel + Render |
| Transactional email polish | Joy | Verification, welcome, digest — tested on Gmail, Outlook, Apple Mail |
| Lighthouse ≥ 80 mobile on: profile, feed, project timeline | Joy | Measured and documented |
| Public launch | Clinton | LinkedIn + industry WhatsApp groups + institution outreach |

---

## Clinton's Role During the Build

Clinton is not building. Clinton is:

1. **Weeks 1–8:** Recruiting the closed beta cohort — 20–50 real construction professionals lined up before Week 8. Start now using existing network (Neptune Multi Services, Cilneod Kenya contacts).
2. **Weeks 16–20:** Seeding the project board and job board with genuine postings before launch. These features are empty and useless without real content on day one.
3. **Throughout:** Product decisions and QA sign-off on each phase's Definition of Done — the "is this right for real users?" call is Clinton's, not Joy's.
4. **Weeks 20–24:** Kenya DPA legal review engagement, domain setup, launch announcement.

---

## Architecture Decisions — Fixed, Don't Revisit

| Decision | Reference |
|---|---|
| Monolithic-first, no microservices at launch | Engineering Doc §4.1 |
| UUID primary keys on all tables | Engineering Doc §3.1 |
| Soft deletes (`is_deleted + deleted_at`) on all user-generated content | Engineering Doc §3.1 |
| `created_at` server-set; `entry_date` user-set — never conflate | Engineering Doc §3.2.3 |
| Direct-to-Cloudinary upload — Django never receives file bytes | Engineering Doc §4.2.2 |
| Optimistic UI for follow/unfollow — rollback on API failure | Engineering Doc §4.2.2 |
| PostgreSQL FTS at launch → Elasticsearch at 50k+ users | Engineering Doc §4.1, §7.2 |
| Redis channel layer from day 1 for Django Channels | Engineering Doc §4.4 |
| JWT RS256; 15-min access token; 30-day refresh with rotation | Engineering Doc §6.2 |
| Explicit field whitelist on every DRF serializer — never `__all__` | Engineering Doc §6.1 |
| React.js (not Next.js) for frontend | Joy's stack choice |

---

## Red Lines
*If any of these are skipped, the build is not actually done.*

- Custom User model created before any other migration
- Object-level permissions audited and tested before beta (Week 8)
- `created_at` is server-set on project updates — client can never set it
- File bytes never pass through Django — direct-to-Cloudinary only
- Resend (not Django default SMTP) for all transactional email
- Redis configured on Render before building Celery or Django Channels
- Kenya DPA legal review before any real user data is collected at scale
- Billing is built last — after Phase 1 beta proves the core habit

---

*Engineering Doc v1.0 is the authoritative reference for all schema, API specs, permission classes, folder structure, and scaling decisions. This plan is the sequence. That doc is the detail.*
