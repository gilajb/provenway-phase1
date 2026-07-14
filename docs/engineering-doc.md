# PROVENWAY — Engineering Documentation v1.0

*Construction Industry Professional Network — Complete Engineering Documentation Package*
*SRS · PRD · System Design · Database Design · API Design · Security Architecture · Development Roadmap*
*Version 1.0 — June 2026 — Confidential & Proprietary*

---

## 1. Software Requirements Specification (SRS)

### 1.1 Introduction & Purpose

This Software Requirements Specification defines the complete functional and non-functional requirements for Provenway — a construction-industry professional network combining verified proof-of-work portfolios, project collaboration, industry networking, recruitment, and tender/project marketplaces. This document serves as the authoritative contract between product stakeholders and the engineering team.

### 1.2 Scope

Provenway targets construction professionals across East Africa (initial launch: Kenya/Nairobi) and is architected for scale to 1 million+ users globally. The platform is web-first with mobile-responsive design, built on React.js + Django + PostgreSQL.

### 1.3 User Types & Personas

| User Type | Primary Goal | Key Pain Point | Tier |
|---|---|---|---|
| Architect | Build a portfolio of completed designs | Static LinkedIn profile doesn't show process | Professional |
| Civil Engineer | Document structural calculations and site progress | No verifiable proof of site experience | Professional |
| Structural Engineer | Showcase structural designs and load analyses | Can't differentiate self from generalists | Professional |
| Quantity Surveyor | Display BOQs, cost reports, and savings delivered | Credentials hard to verify without firm backing | Professional |
| Contractor | Win tenders and show track record of delivery | No trust signal beyond word-of-mouth | Operator |
| Site Supervisor | Log daily site activities and milestones | No digital record of hands-on supervision | Operator |
| Project Manager | Demonstrate on-time, on-budget delivery | PM skill is abstract without evidence | Operator |
| Interior Designer | Showcase before/after transformations | Instagram is too informal; no professional context | Creative |
| MEP Engineer | Document systems installed and commissioning | Highly specialised — invisible on generic networks | Technical |
| Construction Firm | Source talent, post tenders, vet subcontractors | CVs and interviews are slow and gameable | Organisation |
| Property Developer | Find verified professionals for new projects | No reliable vetting mechanism | Organisation |
| Recruiter | Search verified candidates with proven track records | LinkedIn profiles are unverifiable self-reports | Commercial |

### 1.4 Complete Feature Inventory

#### 1.4.1 Core Platform — Identity & Networking

- Account registration with email verification and phone OTP (M-Pesa number)
- Social OAuth: Google, LinkedIn import
- Rich user profiles: role, disciplines, certifications, location, bio, skills matrix
- Professional credential submission (uploaded licence/certificate + admin verification queue)
- Follow / unfollow users; mutual-follow = connection
- Searchable professional directory with filters: discipline, location, verified status, availability
- Home feed: chronological project updates from followed users + algorithmically surfaced posts
- Profile view analytics (who viewed, when — gated behind Pro tier)
- Endorsement system: peers co-sign specific project update entries
- Recommendation letters (text, linked to a specific project)

#### 1.4.2 Build Log — Proof-of-Work Portfolio

- Project creation: title, discipline, location, client (optional), status (active/completed), visibility (public/private/connections)
- Dated update entries within a project: text narrative, up to 10 photos per entry, geotag, weather stamp
- Entry types: milestone, daily log, issue/resolution, inspection passed, phase complete
- Timeline view: chronological, filterable by type, downloadable as PDF portfolio
- Peer co-signature on entries (optional): another Provenway user attests they witnessed or contributed
- Project completion certificate: generated PDF with QR code linking to live build log
- Import from existing projects: bulk upload via CSV template
- Build log embed: public iframe for external portfolio websites

#### 1.4.3 Project Collaboration Board

- Post a project opportunity: scope, disciplines required, budget range, location, timeline
- Project discovery: filter by discipline, budget, location, duration
- Application workflow: professionals apply with proposal + relevant build log entries
- Project owner shortlisting, interview scheduling, offer, and acceptance flow
- Multi-party project rooms: shared updates, files, and messaging for active teams
- Milestone tracker: linked to build log entries for real-time progress visibility

#### 1.4.4 Recruitment Marketplace

- Job board: full-time, contract, freelance, graduate listings
- Structured job application: CV upload, build log portfolio link, cover letter
- Application tracking: kanban-style status board (applied → reviewed → shortlisted → offered → hired)
- Recruiter dashboard: search profiles, save candidates, bulk messaging
- Job alerts: email + in-app for matched criteria
- Salary benchmarking data (crowdsourced, anonymised)
- Graduate/internship section with institution partner integrations

#### 1.4.5 Tender Marketplace

- Tender posting: project description, disciplines required, BOQ, deadline, estimated value
- Tender discovery: filter by value, location, discipline, deadline
- Bid submission: structured bid form with supporting documents + build log evidence
- Bid evaluation tools: comparison matrix, build log verification links
- Awarded/closed tender announcements
- Tender alert subscriptions

#### 1.4.6 Messaging & Notifications

- Private direct messaging (1:1 and group)
- Project-room threaded messaging with file attachments
- Notification centre: follows, messages, applications, endorsements, profile views, tender awards
- Email digest: daily/weekly configurable
- Push notifications (PWA)

#### 1.4.7 Professional Verification

- Document submission: scanned registration certificate, government ID, professional body membership
- Admin review queue with approve/reject/request-more-info workflow
- Verified badge: displayed on profile, search results, and build log entries
- Employer verification: firm confirms a professional worked on their project
- Institution partnerships: universities and professional bodies bulk-verify graduates/members

#### 1.4.8 Admin & Platform Operations

- Admin panel: user management, moderation queue, verification queue, platform analytics
- Content moderation: report abuse, flag fake entries, review queue
- Feature flags: roll out features by user segment or subscription tier
- Analytics dashboard: DAU/MAU, feature adoption, posting frequency, retention cohorts
- Financial dashboard: subscription revenue, transaction fees, payout queue

### 1.5 User Stories

**Professional Users**

- As a civil engineer, I want to log a dated site update with photos so that my future clients can see timestamped evidence of my hands-on experience.
- As a quantity surveyor, I want to share my completed BOQ as a project milestone so that recruiters can verify my cost-management capability.
- As a site supervisor, I want to add peer co-signatures to my daily logs so that my entries are independently corroborated.
- As an architect, I want to export my build log as a PDF portfolio so that I can submit it with tender applications.
- As a contractor, I want to post a tender and receive bids from verified professionals so that I can confidently subcontract work.
- As a graduate architect, I want my university to bulk-verify my degree on Provenway so that I have an instant trust signal when entering the job market.

**Organisation Users**

- As a construction firm, I want to search profiles filtered by 'Verified Structural Engineer within 50km of Nairobi' so that I can shortlist candidates faster than posting a job and waiting.
- As a property developer, I want to post a project opportunity and review applicants' build logs so that I hire based on proven, timestamped evidence rather than CV claims.
- As a recruiter, I want to save candidate profiles and send bulk InMail-style messages so that I can manage my pipeline from one place.

### 1.6 Functional Requirements

**FR-AUTH: Authentication**

| ID | Requirement | Priority |
|---|---|---|
| FR-AUTH-01 | System shall support email/password registration with email verification link (24-hour expiry) | Must |
| FR-AUTH-02 | System shall support Google OAuth2 sign-in | Must |
| FR-AUTH-03 | System shall support LinkedIn OAuth2 with profile import | Should |
| FR-AUTH-04 | System shall enforce password complexity: min 8 chars, 1 uppercase, 1 number | Must |
| FR-AUTH-05 | System shall support phone OTP (Africa's Talking / Twilio) as 2FA | Should |
| FR-AUTH-06 | System shall issue JWT access tokens (15-min TTL) and refresh tokens (30-day TTL) | Must |
| FR-AUTH-07 | System shall allow password reset via email token (1-hour expiry) | Must |
| FR-AUTH-08 | System shall log all auth events (login, failed attempt, password change) to audit log | Must |

**FR-PROFILE: User Profiles**

| ID | Requirement | Priority |
|---|---|---|
| FR-PROF-01 | System shall allow users to set: display name, headline, bio (max 500 chars), location, website URL | Must |
| FR-PROF-02 | System shall allow multi-select of professional disciplines from a controlled taxonomy | Must |
| FR-PROF-03 | System shall allow upload of profile photo (max 5MB, JPEG/PNG/WEBP) | Must |
| FR-PROF-04 | System shall display verification badge when admin approves submitted credentials | Must |
| FR-PROF-05 | System shall record and display profile view count to profile owner (Pro+ tier) | Should |
| FR-PROF-06 | System shall support contact visibility settings: email/phone shown to connections-only, Pro hirers, or hidden | Must |

**FR-LOG: Build Log**

| ID | Requirement | Priority |
|---|---|---|
| FR-LOG-01 | System shall allow users to create a Project with: title, discipline tags, location (lat/lng + text), status, visibility, start date | Must |
| FR-LOG-02 | System shall allow users to create an Update entry within a Project with: title, body text (rich text), up to 10 photos, entry type, date | Must |
| FR-LOG-03 | System shall store photo EXIF data (where available) for geolocation and timestamp verification | Should |
| FR-LOG-04 | System shall display updates in reverse-chronological timeline on project page | Must |
| FR-LOG-05 | System shall allow users to invite a co-signer to an Update; co-signer must confirm via in-app notification | Should |
| FR-LOG-06 | System shall generate a shareable, QR-coded PDF of a project's full build log on demand | Should |
| FR-LOG-07 | System shall enforce visibility rules: private projects hidden from search and feed; connection-only visible only to followers who are also connected | Must |

### 1.7 Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| Performance | API p95 response time (non-media) | < 300ms |
| Performance | Feed initial load (mobile, 3G) | < 3 seconds |
| Performance | Image upload (10MB file) | < 8 seconds |
| Availability | Platform uptime SLA | 99.5% (MVP); 99.9% (Scale) |
| Scalability | Concurrent users supported at launch | 10,000 |
| Scalability | Target concurrent users at Year 2 | 100,000 |
| Scalability | Architecture must support | 1,000,000 registered users |
| Security | All data in transit encrypted | TLS 1.3 minimum |
| Security | All passwords hashed | bcrypt, cost factor ≥ 12 |
| Security | PII at rest encrypted | AES-256 |
| Security | OWASP Top 10 mitigated | Verified by pre-launch pentest |
| Compliance | Kenya Data Protection Act 2019 | Full compliance before user data collected |
| Compliance | GDPR (EU users future) | Privacy-by-design architecture from day 1 |
| Accessibility | WCAG 2.1 Level AA | All core user flows |
| Internationalisation | Currency support | KES (launch), USD, UGX, TZS |
| Internationalisation | Language | English (launch), Swahili (Q2 post-launch) |
| Reliability | RTO (Recovery Time Objective) | < 4 hours |
| Reliability | RPO (Recovery Point Objective) | < 1 hour |

---

## 2. Product Requirements Document (PRD)

### 2.1 Product Vision

Provenway is the professional trust layer for the construction industry — where dated, photographic, peer-corroborated build logs replace self-reported CVs as the primary hiring and collaboration signal.

### 2.2 Success Metrics

| Metric | MVP Target (Month 6) | Growth Target (Month 18) |
|---|---|---|
| Registered professionals | 500 | 10,000 |
| Monthly Active Users (MAU) | 200 | 4,000 |
| Build log entries posted/month | 1,000 | 25,000 |
| Retention (D30) | 25% | 40% |
| Project board postings/month | 20 | 300 |
| Job board postings/month | 10 | 200 |
| Tender postings/month | 5 | 100 |
| Paid subscribers (B2B) | 2 firms | 30 firms |
| MRR | KES 20,000 | KES 500,000 |

### 2.3 Subscription Model

| Plan | Target User | Price (KES/mo) | Price (USD/mo) | Key Features |
|---|---|---|---|---|
| Free | Individual professionals | 0 | 0 | 3 active projects, 50 updates/month, basic search, 1 job application/week |
| Professional | Active individual professionals | 500 | 4 | Unlimited projects & updates, profile analytics, PDF portfolio export, 10 job apps/week, build log co-signatures |
| Pro+ | Senior/independent professionals | 1,200 | 9 | All Pro + priority search placement, verified badge fast-track, tender applications (5/month), embed widget |
| Firm — Starter | Small construction firms (≤10 staff) | 4,000 | 30 | 3 recruiter seats, job board postings (5/month), project board postings (3/month), candidate search |
| Firm — Growth | Mid-size firms (11–50 staff) | 12,000 | 90 | 10 recruiter seats, unlimited job/project postings, tender postings (10/month), ATS integration, API access |
| Firm — Enterprise | Large firms & developers | Custom | Custom | Unlimited seats, dedicated CSM, SLA, data export, white-label options, bulk verification |

### 2.4 Monetisation Strategy

| Stream | Description | Launch Timing | Revenue Potential |
|---|---|---|---|
| B2B Firm Subscriptions | Monthly/annual plans for construction firms, developers, recruiters | Month 3 (post-MVP cohort) | High — recurring, predictable |
| Pro Individual Subscriptions | Freemium upgrade for power-user professionals | Month 4 | Medium — needs scale to matter |
| Tender Listing Fees | KES 500–2,000 per tender posted above free tier | Month 6 | Medium — transactional |
| Job Boost / Featured Listing | Premium placement in job/tender search results | Month 6 | Medium |
| Verification Fast-Track Fee | KES 200–500 to prioritise credential review (optional) | Month 4 | Low-medium |
| Project Board Commission | 2–5% of project value on completed transactions (future) | Year 2 | High — but requires trust infrastructure |
| Grants & Accelerator Funding | Development-narrative fit: closing Africa construction talent gap | Immediate | High near-term — non-recurring |
| Enterprise Partnerships | Institution integrations, industry body bulk licensing | Month 9 | High — long sales cycle |
| Advertising (Supplier) | Targeted material supplier ads to project owners | Year 2 only | Low — deferred; trust risk if early |

### 2.5 Permission System

| Resource | Public (logged out) | Free User | Pro/Pro+ | Firm | Admin |
|---|---|---|---|---|---|
| View public profiles | ✓ | ✓ | ✓ | ✓ | ✓ |
| View build log (public projects) | ✓ | ✓ | ✓ | ✓ | ✓ |
| View private projects | ✗ | Connections only | Connections only | ✗ | ✓ |
| Post build log entries | ✗ | ✓ (capped) | ✓ unlimited | N/A | ✓ |
| Apply to jobs | ✗ | 1/week | 10/week | N/A | ✓ |
| Post jobs | ✗ | ✗ | ✗ | ✓ | ✓ |
| Post tenders | ✗ | ✗ | Pro+ (5/mo) | ✓ | ✓ |
| Access recruiter search | ✗ | ✗ | Basic | Full | ✓ |
| Export PDF portfolio | ✗ | ✗ | ✓ | N/A | ✓ |
| View profile analytics | ✗ | ✗ | ✓ | N/A | ✓ |
| Admin panel | ✗ | ✗ | ✗ | ✗ | ✓ |

---

## 3. Database Design

### 3.1 Design Principles

- PostgreSQL as the single source of truth — relational integrity enforced at DB level
- Row-level security patterns enforced in application layer (DRF permissions)
- Soft deletes (is_deleted flag + deleted_at timestamp) for all user-generated content
- UUID primary keys throughout — prevents enumeration attacks and supports future sharding
- Audit timestamps: created_at, updated_at on all tables using auto-now fields
- JSON fields for flexible metadata (e.g., update entry EXIF data) — only where schema flexibility genuinely needed

### 3.2 Core Database Schema

#### 3.2.1 Users & Authentication

| Table | Column | Type | Constraints / Notes |
|---|---|---|---|
| users | id | UUID | PK, default gen_random_uuid() |
| users | email | VARCHAR(255) | UNIQUE, NOT NULL, indexed |
| users | phone | VARCHAR(20) | UNIQUE, nullable |
| users | password_hash | VARCHAR(255) | bcrypt, NOT NULL |
| users | display_name | VARCHAR(100) | NOT NULL |
| users | headline | VARCHAR(200) | nullable |
| users | bio | TEXT | max 500 chars (app validation) |
| users | location_text | VARCHAR(200) | nullable |
| users | location_lat | DECIMAL(9,6) | nullable |
| users | location_lng | DECIMAL(9,6) | nullable |
| users | avatar_url | VARCHAR(500) | Cloudinary URL |
| users | is_verified | BOOLEAN | DEFAULT false — admin sets true |
| users | is_active | BOOLEAN | DEFAULT true |
| users | subscription_tier | ENUM | free / professional / pro_plus |
| users | created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() |
| users | updated_at | TIMESTAMPTZ | NOT NULL, auto-updated |
| user_disciplines | user_id | UUID | FK → users.id |
| user_disciplines | discipline | ENUM | architect, civil_engineer, structural_engineer, qs, contractor, site_supervisor, project_manager, interior_designer, mep_engineer |
| auth_tokens | id | UUID | PK |
| auth_tokens | user_id | UUID | FK → users.id |
| auth_tokens | token_hash | VARCHAR(255) | hashed refresh token |
| auth_tokens | expires_at | TIMESTAMPTZ | NOT NULL |
| auth_tokens | revoked_at | TIMESTAMPTZ | nullable — set on logout |
| verification_credentials | id | UUID | PK |
| verification_credentials | user_id | UUID | FK → users.id |
| verification_credentials | document_type | ENUM | licence / degree / membership / id |
| verification_credentials | document_url | VARCHAR(500) | Cloudinary URL |
| verification_credentials | status | ENUM | pending / approved / rejected |
| verification_credentials | reviewed_by | UUID | FK → users.id (admin) |
| verification_credentials | reviewed_at | TIMESTAMPTZ | nullable |

> **Note (from live build):** In the actual implementation, `Profile` (one-to-one with `User`) is the single source of truth for `bio`, `location_text`, `location_lat`, `location_lng`, `avatar_url`, and `disciplines` — not the `users` table directly. These fields were migrated off `User` onto `Profile` via migrate-then-drop migrations. `disciplines` is a flat list of strings, not a list of objects. See CLAUDE.md / memory for current status.

#### 3.2.2 Networking

| Table | Column | Type | Constraints / Notes |
|---|---|---|---|
| follows | follower_id | UUID | FK → users.id, PK (composite) |
| follows | following_id | UUID | FK → users.id, PK (composite) |
| follows | created_at | TIMESTAMPTZ | NOT NULL |
| blocks | blocker_id | UUID | FK → users.id |
| blocks | blocked_id | UUID | FK → users.id |
| endorsements | id | UUID | PK |
| endorsements | endorser_id | UUID | FK → users.id |
| endorsements | endorsee_id | UUID | FK → users.id |
| endorsements | skill_or_project | VARCHAR(200) | What is being endorsed |
| endorsements | project_update_id | UUID | FK → project_updates.id, nullable |
| endorsements | message | TEXT | optional text |
| endorsements | created_at | TIMESTAMPTZ | NOT NULL |

> **Note (from live build):** `Follow` uses a UUID surrogate PK + `UniqueConstraint` + `CheckConstraint` (self-follow prevention) instead of a composite PK, since Django 5.0 doesn't support multi-column PKs. `blocks` and `endorsements` are deferred (not yet built).

#### 3.2.3 Build Log — Projects & Updates

| Table | Column | Type | Constraints / Notes |
|---|---|---|---|
| projects | id | UUID | PK |
| projects | owner_id | UUID | FK → users.id, NOT NULL |
| projects | title | VARCHAR(200) | NOT NULL |
| projects | description | TEXT | nullable |
| projects | location_text | VARCHAR(300) | nullable |
| projects | location_lat | DECIMAL(9,6) | nullable |
| projects | location_lng | DECIMAL(9,6) | nullable |
| projects | status | ENUM | active / completed / paused / cancelled |
| projects | visibility | ENUM | public / connections / private |
| projects | start_date | DATE | nullable |
| projects | end_date | DATE | nullable |
| projects | is_deleted | BOOLEAN | DEFAULT false |
| projects | created_at | TIMESTAMPTZ | NOT NULL |
| project_disciplines | project_id | UUID | FK → projects.id |
| project_disciplines | discipline | ENUM | Same taxonomy as user_disciplines |
| project_updates | id | UUID | PK |
| project_updates | project_id | UUID | FK → projects.id, NOT NULL |
| project_updates | author_id | UUID | FK → users.id, NOT NULL |
| project_updates | title | VARCHAR(200) | NOT NULL |
| project_updates | body | TEXT | Rich text, sanitised |
| project_updates | entry_type | ENUM | milestone / daily_log / issue / inspection / phase_complete |
| project_updates | entry_date | DATE | NOT NULL — the actual work date |
| project_updates | geotag_lat | DECIMAL(9,6) | nullable |
| project_updates | geotag_lng | DECIMAL(9,6) | nullable |
| project_updates | exif_metadata | JSONB | raw EXIF from uploaded photos |
| project_updates | is_deleted | BOOLEAN | DEFAULT false |
| project_updates | created_at | TIMESTAMPTZ | NOT NULL — server timestamp (separate from entry_date) |
| update_photos | id | UUID | PK |
| update_photos | update_id | UUID | FK → project_updates.id |
| update_photos | cloudinary_public_id | VARCHAR(300) | NOT NULL |
| update_photos | url | VARCHAR(500) | CDN URL |
| update_photos | sequence_order | SMALLINT | 0-9 |
| update_cosignatures | id | UUID | PK |
| update_cosignatures | update_id | UUID | FK → project_updates.id |
| update_cosignatures | cosigner_id | UUID | FK → users.id |
| update_cosignatures | status | ENUM | pending / confirmed / declined |
| update_cosignatures | confirmed_at | TIMESTAMPTZ | nullable |

> **Note (from live build):** `ProjectDiscipline` uses a UUID surrogate PK for the same Django 5.0 multi-column PK reason as `Follow`. `update_cosignatures` is deferred to a future track.

#### 3.2.4 Recruitment Marketplace

| Table | Column | Type | Constraints / Notes |
|---|---|---|---|
| organisations | id | UUID | PK |
| organisations | name | VARCHAR(200) | NOT NULL |
| organisations | type | ENUM | firm / developer / institution / recruiter_agency |
| organisations | description | TEXT | nullable |
| organisations | logo_url | VARCHAR(500) | nullable |
| organisations | verified | BOOLEAN | DEFAULT false |
| org_members | org_id | UUID | FK → organisations.id |
| org_members | user_id | UUID | FK → users.id |
| org_members | role | ENUM | owner / admin / recruiter / member |
| jobs | id | UUID | PK |
| jobs | org_id | UUID | FK → organisations.id |
| jobs | posted_by | UUID | FK → users.id |
| jobs | title | VARCHAR(200) | NOT NULL |
| jobs | description | TEXT | NOT NULL |
| jobs | job_type | ENUM | full_time / contract / freelance / graduate / internship |
| jobs | location_text | VARCHAR(300) | nullable |
| jobs | is_remote | BOOLEAN | DEFAULT false |
| jobs | salary_min | DECIMAL(12,2) | nullable, KES |
| jobs | salary_max | DECIMAL(12,2) | nullable, KES |
| jobs | disciplines_required | JSONB | Array of discipline enums |
| jobs | status | ENUM | draft / active / closed / filled |
| jobs | expires_at | TIMESTAMPTZ | nullable |
| jobs | created_at | TIMESTAMPTZ | NOT NULL |
| job_applications | id | UUID | PK |
| job_applications | job_id | UUID | FK → jobs.id |
| job_applications | applicant_id | UUID | FK → users.id |
| job_applications | cv_url | VARCHAR(500) | Cloudinary PDF URL |
| job_applications | cover_letter | TEXT | nullable |
| job_applications | portfolio_project_ids | JSONB | Array of project UUIDs highlighted |
| job_applications | status | ENUM | submitted / reviewed / shortlisted / offered / hired / rejected |
| job_applications | created_at | TIMESTAMPTZ | NOT NULL |

*Not yet scaffolded as of the latest build session.*

#### 3.2.5 Tender Marketplace

| Table | Column | Type | Constraints / Notes |
|---|---|---|---|
| tenders | id | UUID | PK |
| tenders | posted_by_user | UUID | FK → users.id |
| tenders | posted_by_org | UUID | FK → organisations.id, nullable |
| tenders | title | VARCHAR(200) | NOT NULL |
| tenders | description | TEXT | NOT NULL |
| tenders | disciplines_required | JSONB | Array of discipline enums |
| tenders | location_text | VARCHAR(300) | nullable |
| tenders | estimated_value_min | DECIMAL(14,2) | nullable, KES |
| tenders | estimated_value_max | DECIMAL(14,2) | nullable, KES |
| tenders | boq_document_url | VARCHAR(500) | Cloudinary PDF URL, nullable |
| tenders | submission_deadline | TIMESTAMPTZ | NOT NULL |
| tenders | status | ENUM | open / closed / awarded / cancelled |
| tenders | awarded_to | UUID | FK → users.id or org, nullable |
| tenders | created_at | TIMESTAMPTZ | NOT NULL |
| tender_bids | id | UUID | PK |
| tender_bids | tender_id | UUID | FK → tenders.id |
| tender_bids | bidder_user_id | UUID | FK → users.id |
| tender_bids | bid_amount | DECIMAL(14,2) | KES |
| tender_bids | bid_document_url | VARCHAR(500) | Cloudinary PDF |
| tender_bids | portfolio_project_ids | JSONB | Array of project UUIDs as evidence |
| tender_bids | notes | TEXT | nullable |
| tender_bids | status | ENUM | submitted / shortlisted / awarded / rejected |
| tender_bids | created_at | TIMESTAMPTZ | NOT NULL |

*Not yet scaffolded as of the latest build session.*

#### 3.2.6 Messaging & Notifications

| Table | Column | Type | Constraints / Notes |
|---|---|---|---|
| conversations | id | UUID | PK |
| conversations | type | ENUM | direct / project_room |
| conversations | project_id | UUID | FK → projects.id, nullable (for project rooms) |
| conversations | created_at | TIMESTAMPTZ | NOT NULL |
| conversation_participants | conversation_id | UUID | FK → conversations.id |
| conversation_participants | user_id | UUID | FK → users.id |
| conversation_participants | joined_at | TIMESTAMPTZ | NOT NULL |
| messages | id | UUID | PK |
| messages | conversation_id | UUID | FK → conversations.id |
| messages | sender_id | UUID | FK → users.id |
| messages | body | TEXT | NOT NULL (plaintext; rich text in v2) |
| messages | attachment_url | VARCHAR(500) | Cloudinary, nullable |
| messages | is_deleted | BOOLEAN | DEFAULT false |
| messages | created_at | TIMESTAMPTZ | NOT NULL |
| notifications | id | UUID | PK |
| notifications | user_id | UUID | FK → users.id (recipient) |
| notifications | type | ENUM | follow / message / application / endorsement / profile_view / tender_award / cosign_request |
| notifications | actor_id | UUID | FK → users.id (who triggered), nullable |
| notifications | entity_type | VARCHAR(50) | jobs / projects / tenders / messages |
| notifications | entity_id | UUID | FK to relevant entity |
| notifications | is_read | BOOLEAN | DEFAULT false |
| notifications | created_at | TIMESTAMPTZ | NOT NULL |

*Not yet scaffolded as of the latest build session.*

### 3.3 Entity Relationship Overview

| Entity A | Relationship | Entity B | Cardinality | Join Table |
|---|---|---|---|---|
| User | has many | Projects | 1:N | — |
| Project | has many | ProjectUpdates | 1:N | — |
| ProjectUpdate | has many | UpdatePhotos | 1:N | — |
| ProjectUpdate | has many | CoSignatures | 1:N | update_cosignatures |
| User | follows many | Users | M:N | follows |
| User | blocks | Users | M:N | blocks |
| User | endorses | Users (via Updates) | M:N | endorsements |
| User | belongs to many | Organisations | M:N | org_members |
| Organisation | posts many | Jobs | 1:N | — |
| Job | has many | JobApplications | 1:N | — |
| User | applies to | Jobs | M:N | job_applications |
| Organisation | posts many | Tenders | 1:N | — |
| Tender | has many | TenderBids | 1:N | — |
| User | bids on | Tenders | M:N | tender_bids |
| User | participates in | Conversations | M:N | conversation_participants |
| Conversation | has many | Messages | 1:N | — |
| User | receives many | Notifications | 1:N | — |

### 3.4 Key Indexes

| Table | Index Columns | Type | Purpose |
|---|---|---|---|
| users | email | UNIQUE B-tree | Auth lookup |
| users | location_lat, location_lng | B-tree composite | Geographic search |
| users | subscription_tier, is_verified | B-tree composite | Recruiter filter queries |
| follows | follower_id, following_id | UNIQUE B-tree | Follow status check |
| follows | following_id | B-tree | Follower count |
| projects | owner_id, status | B-tree composite | Profile project listing |
| projects | visibility, is_deleted | B-tree composite | Feed query |
| project_updates | project_id, entry_date DESC | B-tree composite | Timeline display |
| project_updates | author_id, created_at DESC | B-tree composite | Feed generation |
| jobs | status, created_at DESC | B-tree composite | Job board listing |
| tenders | status, submission_deadline | B-tree composite | Tender listing |
| notifications | user_id, is_read, created_at DESC | B-tree composite | Notification badge + list |
| messages | conversation_id, created_at DESC | B-tree composite | Message thread loading |

---

## 4. System Design Document

### 4.1 High-Level Architecture

Provenway uses a monolithic-first architecture that is structured for incremental service extraction as load demands. This is the correct decision for a pre-revenue product: premature microservices add deployment complexity, latency, and operational burden without proportional benefit at early scale.

| Layer | Technology | Hosting | Rationale |
|---|---|---|---|
| Frontend | React.js (Next.js for SSR) | Vercel | Mobile-first SSR for 3G performance; zero-config deploys |
| Backend API | Django 5.x + Django REST Framework | Render (Web Service) | Batteries-included: auth, ORM, admin, validation; familiar to most Python engineers |
| Real-time | Django Channels + Redis | Render + Redis Cloud (free tier → paid) | WebSocket messaging and live notifications without a separate service |
| Database | PostgreSQL 16 | Render (Managed DB) → AWS RDS (scale) | Relational integrity; excellent Django ORM support; strong JSON(B) support |
| Cache | Redis | Redis Cloud / Render Redis | Session store, feed cache, rate limiting, WebSocket channel layer |
| Media Storage | Cloudinary | Cloudinary CDN | Image transformation, optimisation, and CDN delivery in one; direct upload from browser |
| Search | PostgreSQL Full-Text Search (FTS) → Elasticsearch | Render (FTS) → Elastic Cloud (scale) | PG FTS sufficient to 50k users; migrate to Elasticsearch at scale |
| Email | Resend (transactional) | Resend API | Modern API, generous free tier, excellent deliverability |
| SMS / OTP | Africa's Talking | AT API | Kenya-first; MPESA integration; SMS OTP and notifications |
| Payments | M-Pesa Daraja API + Stripe | Direct API | M-Pesa for KES subscriptions; Stripe for USD/international |
| Monitoring | Sentry (errors) + PostHog (analytics) | SaaS | Error tracking from day 1; product analytics for retention metrics |
| CI/CD | GitHub Actions | GitHub | Automated test → lint → deploy pipeline on merge to main |

> **Note (from live build):** Frontend actually built with Vite (not Next.js) per developer's stack choice — see Build Plan. Sentry is installed but not yet initialized; WhiteNoise is present but needs middleware wiring.

### 4.2 Frontend Architecture

#### 4.2.1 Directory Structure

| Path | Contents |
|---|---|
| src/app/ | Next.js App Router pages and layouts |
| src/app/(auth)/ | Login, register, reset-password pages (no main nav) |
| src/app/(main)/ | Authenticated app shell: feed, profile, projects, jobs, tenders, messages |
| src/app/admin/ | Admin panel pages (separate layout, admin-only) |
| src/components/ui/ | Primitive design-system components: Button, Input, Modal, Card, Avatar, Badge |
| src/components/layout/ | Navbar, Sidebar, MobileNav, PageWrapper |
| src/components/build-log/ | ProjectCard, UpdateTimeline, UpdateEntry, PhotoGrid, CoSignBadge |
| src/components/marketplace/ | JobCard, TenderCard, ApplicationModal, BidModal |
| src/components/messaging/ | ConversationList, MessageThread, MessageInput, PresenceIndicator |
| src/components/profile/ | ProfileHeader, VerifiedBadge, DisciplineTags, SkillsMatrix, StatCards |
| src/hooks/ | useAuth, useProfile, useFeed, useMessaging, useSubscription |
| src/lib/api/ | Typed API client: apiClient.ts wrapping fetch with auth headers and error handling |
| src/lib/auth/ | JWT decode, token refresh logic, auth context |
| src/stores/ | Zustand stores: authStore, feedStore, messagingStore, notificationStore |
| src/types/ | TypeScript interfaces mirroring backend serializer outputs |
| src/utils/ | Date formatters, image URL builders, discipline label maps |
| public/ | Static assets: logo, favicons, PWA manifest |

> **Note:** This directory layout describes the original Next.js concept. The actual `provenway-frontend` is Vite-based — see repo for the real structure (CSS Modules, TanStack Query, etc.)

#### 4.2.2 Key Frontend Decisions

- SEO for build logs is important for public profile indexability
- Client components only for interactive elements: feed, messaging, project update forms
- Image uploads: direct-to-Cloudinary via signed upload preset (never route file bytes through Django)
- WebSocket connection via native WebSocket or socket.io-client to Django Channels for messaging
- Optimistic UI updates for follow/unfollow, likes, and notification read — queue rollback on API failure
- PWA manifest + service worker for offline-capable project update drafts and push notifications

### 4.3 Backend Architecture

#### 4.3.1 Django App Structure

| App / Module | Responsibility |
|---|---|
| provenway/settings/ | Base, development, production, and test settings (split per environment) |
| apps/authentication/ | Custom user model, JWT auth, OAuth, registration, verification email, OTP |
| apps/profiles/ | User profile serializers/views, discipline management, profile analytics |
| apps/networking/ | Follow/unfollow, block, endorsements, connection graph queries |
| apps/build_log/ | Project CRUD, ProjectUpdate CRUD, photo handling, co-signature workflow, PDF export |
| apps/recruitment/ | Jobs CRUD, JobApplication CRUD, ATS status workflow, recruiter search |
| apps/tenders/ | Tender CRUD, TenderBid CRUD, bid comparison, award workflow |
| apps/organisations/ | Organisation CRUD, member management, subscription billing hooks |
| apps/messaging/ | Conversation/Message models + DRF views; WebSocket consumer via Channels |
| apps/notifications/ | Notification model, async creation (Celery task), WebSocket push |
| apps/verification/ | Credential submission, admin review queue, verified badge logic |
| apps/feed/ | Home feed query logic: followed-user updates, discovery injection |
| apps/search/ | Cross-model search: profiles, projects, jobs, tenders via PG FTS |
| apps/admin_panel/ | Custom Django Admin extensions + analytics API for admin dashboard |
| apps/billing/ | Subscription plan management, M-Pesa webhook handler, Stripe webhook handler |
| core/ | Shared base models (UUIDModel, TimestampedModel, SoftDeleteModel), permissions, pagination, exceptions |
| celery_app.py | Celery configuration for async tasks: email sending, PDF export, notification batching |

#### 4.3.2 Permission Architecture

| Permission Class | Scope | Enforcement Point |
|---|---|---|
| IsAuthenticatedOrReadOnly | Global default | DRF default permission class |
| IsOwnerOrReadOnly | Project, Update, Job, Tender resources | Custom DRF permission — checks obj.owner_id == request.user.id |
| IsVerifiedUser | Co-signature creation, tender posting | Custom DRF permission — checks user.is_verified |
| IsOrgMemberWithRole | Org admin actions, job posting | Custom — checks org_members table for correct role |
| IsProfessionalTier | Pro/Pro+ gated features | Custom — checks user.subscription_tier in [professional, pro_plus] |
| IsFirmTier | Recruiter search, firm dashboard | Custom — checks org subscription tier |
| IsAdminUser | Admin panel endpoints | Django's IsAdminUser or custom staff check |
| ProjectVisibilityPermission | Reading private/connection projects | Object-level — checks project.visibility vs follower graph |

> **Note (from live build):** In practice, `visible_projects_q()` and `user_can_view_project()` in `apps/projects/permissions.py` are the single authoritative source for visibility logic, used across list, detail, feed, and build log surfaces (not just object-level checks per-endpoint).

### 4.4 Real-Time Architecture (Django Channels)

| Event | Channel Group | Consumer Action | Clients Updated |
|---|---|---|---|
| New message sent | chat_{conversation_id} | Broadcast message payload | All conversation participants |
| User online/offline | presence_{user_id} | Update presence store in Redis | Contacts viewing that user's profile |
| New notification | notifications_{user_id} | Push notification payload | Recipient only |
| Co-sign request | notifications_{user_id} | Push co-sign request event | Co-signer only |
| Tender bid received | notifications_{user_id} | Push bid received event | Tender owner only |

*Not yet built as of the latest session — deferred with messaging/notifications tracks.*

### 4.5 Async Task Architecture (Celery)

| Task | Trigger | Queue | Notes |
|---|---|---|---|
| send_verification_email | User registration | email | Resend API, retry x3 |
| send_notification_email_digest | Daily cron (6 AM EAT) | email | Batch unread notifications |
| generate_portfolio_pdf | User requests export | pdf_export | WeasyPrint or reportlab; store in Cloudinary |
| process_image_metadata | Photo upload | media | Extract EXIF, store in update_photos.exif_metadata |
| create_notification | Follow, application, message, etc. | notifications | Decouple notification creation from request cycle |
| sync_subscription_status | M-Pesa / Stripe webhook | billing | Update user subscription_tier |
| index_search_document | User/Project/Job/Tender created/updated | search | Update Elasticsearch index (at scale) |

> **Note (from live build):** Celery is wired via `core/apps.py:ready()` (Windows-safe, avoids circular import on `provenway/__init__.py`). EXIF extraction currently runs synchronously, not yet via Celery — deferred.

---

## 5. API Design

### 5.1 API Conventions

- Base URL: `https://api.provenway.com/v1/`
- All responses: JSON. Errors follow RFC 7807 (Problem Details for HTTP APIs)
- Authentication: Bearer token (JWT) in Authorization header
- Pagination: cursor-based for feeds; offset-based for search results
- Rate limiting headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- Versioning: URL path (/v1/, /v2/) — never breaking changes within a version

> **Note (from live build):** Feed pagination uses a hand-rolled keyset paginator encoding `(created_at, id)` as a composite cursor — DRF's built-in cursor pagination only encodes the first ordering field, which is unsafe when timestamps collide.

### 5.2 API Endpoint Reference

**Authentication**

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| POST | /auth/register/ | No | Register with email + password |
| POST | /auth/verify-email/ | No | Verify email via token |
| POST | /auth/login/ | No | Returns access + refresh tokens |
| POST | /auth/token/refresh/ | Refresh token | Returns new access token |
| POST | /auth/logout/ | Yes | Revokes refresh token |
| POST | /auth/password-reset/request/ | No | Sends reset email |
| POST | /auth/password-reset/confirm/ | No | Sets new password via token |
| POST | /auth/otp/request/ | Yes | Sends SMS OTP |
| POST | /auth/otp/verify/ | Yes | Verifies OTP, sets 2FA enabled |
| GET | /auth/oauth/google/ | No | Initiates Google OAuth flow |
| GET | /auth/oauth/google/callback/ | No | Google OAuth callback |

**Users & Profiles**

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /users/me/ | Yes | Get own profile |
| PATCH | /users/me/ | Yes | Update own profile fields |
| GET | /users/{id}/ | Optional | Get public profile (or full if owner/connection) |
| GET | /users/ | Optional | Search directory (query, discipline, location, verified) |
| POST | /users/{id}/follow/ | Yes | Follow a user |
| DELETE | /users/{id}/follow/ | Yes | Unfollow a user |
| GET | /users/{id}/followers/ | Optional | List followers (paginated) |
| GET | /users/{id}/following/ | Optional | List following (paginated) |
| POST | /users/{id}/block/ | Yes | Block a user |
| GET | /users/me/analytics/ | Pro+ only | Profile view stats |
| POST | /credentials/ | Yes | Submit verification document |
| GET | /credentials/me/ | Yes | Get own credential submissions + status |

**Build Log — Projects**

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /projects/ | Optional | List/search projects (public + own private) |
| POST | /projects/ | Yes | Create a project |
| GET | /projects/{id}/ | Optional | Get project + updates (visibility enforced) |
| PATCH | /projects/{id}/ | Owner | Update project metadata |
| DELETE | /projects/{id}/ | Owner | Soft-delete project |
| GET | /projects/{id}/updates/ | Optional | List updates for a project |
| POST | /projects/{id}/updates/ | Owner | Add a new update entry |
| GET | /projects/{id}/updates/{uid}/ | Optional | Get single update |
| PATCH | /projects/{id}/updates/{uid}/ | Owner | Edit update (within 24h of creation) |
| DELETE | /projects/{id}/updates/{uid}/ | Owner | Soft-delete update |
| POST | /projects/{id}/updates/{uid}/photos/ | Owner | Upload photos to update (presigned Cloudinary) |
| POST | /projects/{id}/updates/{uid}/cosign/ | Yes (not owner) | Request co-signature from another user |
| POST | /projects/{id}/updates/{uid}/cosign/confirm/ | Co-signer | Confirm or decline co-signature |
| GET | /projects/{id}/export-pdf/ | Owner/Pro | Generate portfolio PDF (async — returns task ID) |
| GET | /tasks/{task_id}/ | Yes | Poll Celery task status (for PDF export) |

**Feed**

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /feed/ | Yes | Home feed: updates from followed users, cursor-paginated |
| GET | /feed/discover/ | Yes | Discovery feed: algorithmic, popular updates outside network |
| GET | /feed/trending/ | Optional | Trending projects (public, no auth required) |

*`/feed/discover/` and `/feed/trending/` are explicitly deferred as of the latest session.*

**Recruitment & Tenders**

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /jobs/ | Optional | List/search jobs |
| POST | /jobs/ | Firm tier | Post a job |
| GET | /jobs/{id}/ | Optional | Get job detail |
| PATCH | /jobs/{id}/ | Poster/Org admin | Update job |
| POST | /jobs/{id}/apply/ | Yes (Pro rate limit) | Submit application |
| GET | /jobs/{id}/applications/ | Recruiter | List applications for a job |
| PATCH | /jobs/{id}/applications/{aid}/ | Recruiter | Update application status |
| GET | /tenders/ | Optional | List/search tenders |
| POST | /tenders/ | Yes (Pro+ or Firm) | Post a tender |
| GET | /tenders/{id}/ | Optional | Get tender detail |
| POST | /tenders/{id}/bid/ | Yes (Pro+) | Submit a bid |
| GET | /tenders/{id}/bids/ | Tender owner | List bids |
| POST | /tenders/{id}/award/ | Tender owner | Award tender to a bidder |

*Not yet built as of the latest session.*

**Messaging**

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /conversations/ | Yes | List conversations for current user |
| POST | /conversations/ | Yes | Create direct conversation with user |
| GET | /conversations/{id}/messages/ | Participant | Get messages (cursor-paginated, newest last) |
| POST | /conversations/{id}/messages/ | Participant | Send a message (also via WebSocket) |
| DELETE | /messages/{id}/ | Sender (within 1h) | Soft-delete a message |
| WS | wss://api.provenway.com/ws/chat/{conversation_id}/ | JWT in query param | Real-time message socket |
| WS | wss://api.provenway.com/ws/notifications/ | JWT in query param | Real-time notification socket |

*Not yet built as of the latest session.*

**Notifications**

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /notifications/ | Yes | List notifications (unread first, paginated) |
| POST | /notifications/{id}/read/ | Yes | Mark single notification as read |
| POST | /notifications/read-all/ | Yes | Mark all as read |
| GET | /notifications/preferences/ | Yes | Get email/push notification preferences |
| PATCH | /notifications/preferences/ | Yes | Update notification preferences |

*Not yet built as of the latest session.*

**Admin**

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| GET | /admin/users/ | Admin | User management list + filters |
| PATCH | /admin/users/{id}/ | Admin | Ban, deactivate, set subscription tier |
| GET | /admin/verification-queue/ | Admin | Pending credential reviews |
| POST | /admin/verification-queue/{id}/review/ | Admin | Approve / reject / request-info |
| GET | /admin/analytics/ | Admin | Platform metrics: DAU, MAU, posting rates, subscription MRR |
| GET | /admin/reports/ | Admin | Content moderation report queue |
| POST | /admin/reports/{id}/action/ | Admin | Dismiss / remove content / warn user |

*Not yet built as of the latest session — no admin ban endpoint exists yet.*

---

## 6. Security Architecture

### 6.1 Threat Model

| Threat | OWASP Category | Mitigation |
|---|---|---|
| SQL Injection via API inputs | A03: Injection | Django ORM parameterised queries everywhere; no raw SQL without explicit review |
| XSS via rich text update bodies | A03: Injection | Bleach/DOMPurify sanitisation on both client (React) and server; whitelist-only HTML tags |
| CSRF on state-changing endpoints | A01: Broken Access Control | SameSite=Strict cookie; CSRF token for session-based requests; JWT for API clients |
| Broken object-level authorisation | A01 | Explicit IsOwnerOrReadOnly + ProjectVisibilityPermission on every object endpoint; no implicit row access |
| Credential stuffing / brute force | A07: Auth Failures | Rate limiting: 5 failed logins → 15-min lockout; CAPTCHA on register/login |
| Insecure file uploads (malware, SSRF) | A05: Security Misconfiguration | Cloudinary scans uploads; backend validates file type + size before issuing upload preset; no URL-based uploads from users |
| Sensitive data exposure (PII) | A02 | Contact fields opt-in visibility; DB fields encrypted at rest (AES-256 via Render); HTTPS enforced (HSTS) |
| JWT token theft | A07 | Short-lived access tokens (15 min); refresh token rotation; revocation list in Redis |
| Enumeration attacks (user IDs) | A01 | UUID primary keys; no sequential ID in any API response |
| Mass assignment via PATCH body | A08: Software/Data Integrity | DRF serializers with explicit 'fields' whitelist on every PATCH endpoint; never allow __all__ |
| Admin panel exposure | A05 | Admin endpoints behind /admin/ with additional IsStaffUser check + IP allowlist in production |
| Fake build log entries (backdated) | Trust/Integrity | created_at set by server (never client); entry_date editable but server-timestamped; pattern detection flagged for review |

> **Note (from live build — Session 16 security audit):** Full permission audit completed. Two bug classes found and fixed: (1) moderation bypass — banned user project content was visible despite profile being hidden, fixed centrally in `visible_projects_q()`; (2) three write endpoints lacked rate limiting, fixed via `core/ratelimiting.py`. Deferred: banned users in social graph lists, JWT force-revoke on ban (needs Redis blocklist + admin ban endpoint), Django admin IP allowlist (infra config). 147 tests passing.

### 6.2 Authentication Security

- Passwords: bcrypt with cost factor 12 minimum (upgrade to Argon2 at scale)
- JWT: RS256 signing (asymmetric) in production; HS256 in dev — public key verifiable by frontend without server round-trip
- Refresh tokens: stored as hashed SHA-256 in auth_tokens table; issued once per login; rotated on every refresh
- Token revocation: Redis blocklist checked on every authenticated request (planned — not yet implemented for force-revoke on ban)
- Rate limiting on auth endpoints: 10 requests/minute per IP; 5 failed attempts triggers exponential backoff
- All auth events written to immutable audit_log table (user_id, event_type, ip_address, user_agent, timestamp)

### 6.3 Data Privacy (Kenya Data Protection Act 2019 Compliance)

| Obligation | Implementation |
|---|---|
| Lawful basis for processing | Consent collected on registration; purpose stated in Privacy Policy; contact fields require explicit opt-in |
| Data subject rights (access, correction, deletion) | API endpoints: GET /users/me/data-export/ (full data export), DELETE /users/me/ (account + data deletion within 30 days) |
| Data minimisation | Only collect fields with a stated product purpose; phone number optional at registration |
| Retention policy | Deleted accounts: PII anonymised after 30-day grace period; logs retained 12 months then purged |
| Data breach notification | Incident response plan: notify Kenya DPC within 72 hours of discovery; affected users within 96 hours |
| Third-party processors | Cloudinary (media), Resend (email), Africa's Talking (SMS) — DPA clauses in place before launch |
| Cross-border transfers | EU/US transfers covered by SCCs; Cloudinary EU region option for GDPR future readiness |

### 6.4 Infrastructure Security

- All traffic: HTTPS enforced via Vercel and Render; HSTS header with 1-year max-age
- Secrets: environment variables in Render/Vercel secrets store; never in codebase or logs
- Dependency scanning: Dependabot on GitHub for CVE alerts; weekly automated scan
- Container security: Render managed containers; no custom Docker exposure
- Database: Render managed PostgreSQL with automated backups (daily, 7-day retention); connection via SSL only
- Admin panel: additional IP allowlist restriction in production (Render environment variable) — **not yet configured**
- Pre-launch penetration test: schedule with a Kenya-based or remote security firm before public launch

---

## 7. Scalability Plan

### 7.1 Scaling Tiers

| Tier | User Base | Architecture | Key Changes from Previous Tier |
|---|---|---|---|
| Launch | 0 – 5,000 registered | Render Web Service (1 instance) + Render PostgreSQL (starter) + Redis Cloud free | None — baseline deployment |
| Growth | 5,000 – 50,000 | Render auto-scale (2–4 instances) + Render PostgreSQL (standard) + Redis Cloud (paid) | Add database read replica; move to Elasticsearch for search; CDN cache for profile pages |
| Scale | 50,000 – 250,000 | Render pro / AWS ECS Fargate (multi-AZ) + AWS RDS PostgreSQL (multi-AZ) + ElastiCache Redis | Extract notification service; separate async worker fleet; S3 + CloudFront for static assets |
| Expansion | 250,000 – 1,000,000 | AWS ECS Fargate (multi-region) + Aurora PostgreSQL + ElastiCache + Elasticsearch Service | Feed service extracted; global CDN; sharding strategy for project_updates; gRPC inter-service |

### 7.2 Performance Bottleneck Forecast

| Bottleneck | Anticipated at | Mitigation |
|---|---|---|
| Home feed generation (SELECT * from followed-user updates) | ~5,000 MAU | Pre-compute feed into Redis sorted set on update creation (fan-out on write) |
| Profile page load (N+1 queries on projects + updates) | ~2,000 concurrent users | DRF select_related/prefetch_related; add Redis cache layer for profile data (5-min TTL) |
| Image storage costs (Cloudinary) | ~10,000 updates/month with photos | Set Cloudinary transformation policies: max 1200px width, 80% JPEG quality; implement lazy loading |
| Full-text search degradation (PostgreSQL FTS) | ~50,000 profiles/projects indexed | Migrate search to Elasticsearch; async index updates via Celery |
| WebSocket connections at scale | ~10,000 concurrent connections | Horizontal scale Django Channels workers; Redis Cluster for channel layer |
| PDF export queue saturation | ~500 exports/hour | Dedicate separate Celery queue + worker pool; cache exported PDFs in Cloudinary for 24h |
| Database write pressure (project_updates) | ~500,000 rows/month | Table partitioning by created_at month; archive old partitions to read replica |

---

## 8. Development Roadmap

*Superseded in day-to-day use by `build-plan.md`, which sequences this roadmap into weekly deliverables for a solo developer. This section remains the source for team composition, phase goals, and folder structure reference.*

### 8.1 Team Composition Required (original org-scale plan)

| Role | Weeks 1–8 (Foundation) | Weeks 6–18 (Full Build) | Post-Launch |
|---|---|---|---|
| Backend Lead (Django/PostgreSQL) | Full-time — highest priority hire | Full-time | Full-time |
| Frontend Lead (React/Next.js) | Full-time | Full-time | Full-time |
| Product Designer (UI/UX) | Full-time Weeks 1–4, part-time after | Part-time | Part-time |
| Founder/Product Owner (Clinton) | Product decisions, industry input | Validation & GTM | GTM & BD |
| Growth/Community Role | Not yet needed | Part-time from Week 10 | Full-time post-launch |
| Legal/Compliance Advisor | Retained from Week 1 (DPA review) | As needed | Quarterly |

> **Note:** In practice, Provenway is being built by Joy as sole developer with Clinton as Product Owner — see `build-plan.md` for the real team structure and sequencing.

### 8.6 Folder Structure

**Backend (Django)**

| Path | Contents |
|---|---|
| provenway-backend/ | Root |
| provenway/ | Django project package: settings/, urls.py, wsgi.py, asgi.py, celery_app.py |
| provenway/settings/ | base.py, development.py, production.py, test.py |
| apps/authentication/ | models.py, serializers.py, views.py, urls.py, permissions.py, tasks.py |
| apps/profiles/ | models.py, serializers.py, views.py, urls.py |
| apps/networking/ | models.py (Follow, Block, Endorsement), serializers.py, views.py, urls.py |
| apps/build_log/ | models.py (Project, ProjectUpdate, UpdatePhoto, CoSignature), serializers.py, views.py, urls.py, tasks.py (PDF export), services.py |
| apps/recruitment/ | models.py (Organisation, OrgMember, Job, JobApplication), serializers.py, views.py, urls.py |
| apps/tenders/ | models.py (Tender, TenderBid), serializers.py, views.py, urls.py |
| apps/messaging/ | models.py (Conversation, Participant, Message), serializers.py, views.py, urls.py, consumers.py (Channels), routing.py |
| apps/notifications/ | models.py, serializers.py, views.py, urls.py, consumers.py, tasks.py |
| apps/verification/ | models.py, serializers.py, views.py, urls.py |
| apps/feed/ | services.py (feed query logic), views.py, urls.py |
| apps/search/ | views.py, urls.py, services.py, documents.py (ES index definitions) |
| apps/billing/ | views.py (webhook handlers), services.py, urls.py |
| apps/admin_panel/ | views.py (analytics API), urls.py, admin.py (Django Admin extensions) |
| core/ | models.py (UUIDModel, TimestampedModel, SoftDeleteModel), permissions.py, pagination.py, exceptions.py, utils.py |
| tests/ | Mirrored structure: tests/apps/build_log/test_views.py, etc. |
| requirements/ | base.txt, development.txt, production.txt |
| .github/workflows/ | ci.yml (test + lint), deploy.yml (push to Render on main merge) |

**Frontend (actual: Vite, not Next.js — see `build-plan.md` for the real structure)**

| Path | Contents |
|---|---|
| provenway-frontend/ | Root |
| src/pages/ | Route-level pages |
| src/components/ | ui/, layout/, build-log/, marketplace/, messaging/, profile/, admin/ |
| src/hooks/ | useAuth.js, useProfile.js, useFeed.js, useDirectorySearch.js, useInfiniteScroll.js, etc. |
| src/lib/api/ | apiClient.js (fetch wrapper with auth headers + token refresh) |
| src/stores/ | Zustand: authStore.js, feedStore.js, messagingStore.js, notificationStore.js |
| src/utils/ | dates.js, disciplines.js, imageUrl.js, formatCurrency.js |
| public/ | icons/, logo.svg, manifest.json, sw.js (service worker) |

---

## 9. Technical Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Build log habit doesn't stick with real users | High | Critical | Design onboarding to produce first entry in <5 minutes; observe D7 retention before building further features; co-signature social pressure helps |
| Two-sided cold start on project/job/tender boards | High | High | Founder personally recruits and seeds initial postings; growth role dedicated to this; full feature set available from day 1 so early users have incentive to stay |
| Founder bandwidth overextension | Very High | Critical | Provenway build must be led by a dedicated technical resource — not founder engineering hours |
| Object-level permission misconfiguration (data leak) | Medium | Critical | Explicit permission audit as named Phase 1 milestone; automated permission tests in CI |
| Django Channels WebSocket scaling under load | Medium | High | Redis channel layer from day 1; horizontal scale Channels workers before 1,000 concurrent connections |
| Cloudinary cost growth with photo-heavy usage | Medium | Medium | Set transformation policies (resize on upload); implement lazy loading; monitor costs weekly |
| Fake/backdated build log entries undermining trust | Medium | High | Server-set created_at timestamp; pattern detection flagged for moderation; co-signature as optional corroboration; explicit disclaimer that platform shows logged activity, not verified licensure |
| Elasticsearch migration complexity at scale | Low-Medium | Medium | Use PostgreSQL FTS from day 1 (same query interface); ES migration is additive, not destructive |
| M-Pesa Daraja API reliability for subscription billing | Medium | Medium | Implement idempotent webhook handling; retry queue in Celery; fallback to Stripe for failed M-Pesa transactions |
| Kenya DPA 2019 non-compliance before user data collected | Low (if acted on) | Critical | Retain legal advisor early; DPA review is a Phase 1 prerequisite, not a post-launch fix |
| No professional licensing verification exposes platform to liability | Medium | High | Clear product copy: 'Provenway shows logged activity, not verified licensure'; verified badge covers identity + credential document, not licensing authority check |

---

## 10. Recommended MVP & Full Product Roadmap

### 10.1 MVP Definition (Weeks 1–8 output)

The MVP is NOT a stripped-down proof-of-concept. It is the complete core identity and build log platform, deployed on real infrastructure, shared across all users, with real authentication and real persistence. It deliberately excludes the marketplace features (jobs, tenders, project board) and real-time messaging — not because those are less important, but because the single most important open question (will professionals actually log their work?) must be answered first.

| Feature | MVP (Weeks 1–8) | Full Product (Weeks 1–20) |
|---|---|---|
| Authentication (email + Google OAuth) | ✓ | ✓ |
| User profiles (bio, disciplines, location, avatar) | ✓ | ✓ |
| Project creation + management | ✓ | ✓ |
| Dated update entries with photos (build log) | ✓ | ✓ |
| Follow / unfollow | ✓ | ✓ |
| Directory search (name, discipline, location) | ✓ | ✓ |
| Home feed (updates from followed users) | ✓ | ✓ |
| Object-level permissions + security hardening | ✓ | ✓ |
| Real-time messaging | ✗ | ✓ |
| Notifications (in-app + email) | Partial (email only) | ✓ (real-time + email digest) |
| Project collaboration board | ✗ | ✓ |
| Job board + ATS | ✗ | ✓ |
| Tender marketplace | ✗ | ✓ |
| Professional verification + badge | ✗ | ✓ |
| Co-signature on update entries | ✗ | ✓ |
| PDF portfolio export | ✗ | ✓ |
| Admin panel with moderation + analytics | Basic Django admin only | ✓ Full custom panel |
| M-Pesa + Stripe subscription billing | ✗ | ✓ |
| Endorsements / recommendations | ✗ | ✓ |
| Organisation profiles + recruiter dashboard | ✗ | ✓ |

### 10.2 Strategic Sequencing Rationale

- Phase 1 (MVP) proves the core habit: if professionals don't log work in the MVP, no marketplace feature fixes that.
- Phase 2 parallel tracks (org-scale plan) allow marketplace features to ship together rather than one by one — in the solo-dev build these become sequential tracks instead (see `build-plan.md`).
- Billing is deferred deliberately: asking for money before the product has proven value is a retention risk and a trust risk.
- Verification ships after MVP because it requires an admin workflow that's premature to build for a small user base.
- The tender marketplace is the last marketplace feature: highest complexity (two-sided, high-value, document-heavy), lowest urgency for a first-launch cohort of individual professionals.

### 10.3 Year 2 Roadmap (Post Product-Market Fit)

| Feature / Initiative | Strategic Value | Prerequisites |
|---|---|---|
| Native mobile app (React Native) | Site-based professionals prefer native push notifications and offline draft capability | Stable API; PWA adoption data |
| Supplier/materials marketplace | Construction supply chain integration; new revenue stream (listing fees + affiliate) | 200+ active firm accounts |
| Project value transaction fee | 2–5% fee on project-board engagements above threshold | Escrow/payment infrastructure; legal review |
| AI-powered candidate matching | Recruiter searches matched to build logs via embedding similarity | Sufficient indexed build log data (~50k entries) |
| Swahili + French localisation | East + West Africa expansion | Product-market fit in Kenya first |
| Professional body integrations (ERB, AAK) | Bulk member verification; institutional distribution | Verified badge in production; BD relationships |
| API for third-party ATS integration | Sell data access to enterprise recruitment platforms | Firm — Enterprise tier stable |
| Salary benchmarking (anonymised aggregate) | High-value data product for professionals and firms | 50,000+ salary data points collected |
| West Africa launch (Nigeria, Ghana) | 10x TAM expansion | Playbook validated in Kenya; Nigeria-specific M-Pesa equivalent (Flutterwave/Paystack) |

---

*© 2026 Provenway. All rights reserved.*
