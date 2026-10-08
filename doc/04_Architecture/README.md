# Architecture

**Document ID:** ARCH-README
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `README.md`

## 1. Purpose

This directory defines the technical architecture of FastFood ERP.

Architecture translates the decisions made in:

```text
Business Analysis
        ↓
System Analysis
        ↓
Domain Analysis
        ↓
Architecture
        ↓
Database / Backend / Frontend / API / Deployment
```

Architecture documents define **how the system must be structured and how its major technical parts must work together**.

Architecture must preserve the business rules and system behavior already defined in previous analysis layers.

Architecture documents must not silently redefine business requirements.

If an architectural change requires changing an approved business or system rule, the affected source document and relevant ADR must also be updated.

---

# 2. Architecture Goals

FastFood ERP architecture must provide:

* clear module boundaries;
* strong tenant isolation;
* branch isolation;
* secure authentication and authorization;
* reliable offline operation;
* safe synchronization;
* historical integrity;
* strong consistency for critical transactions;
* controlled asynchronous processing;
* predictable failure recovery;
* acceptable performance on ordinary POS hardware;
* horizontal scalability;
* operational observability;
* maintainable code structure;
* safe database evolution;
* reliable backup and recovery;
* technology decisions that remain understandable and reversible where practical.

The architecture must support a multi-tenant SaaS product without introducing unnecessary distributed-system complexity.

---

# 3. Architectural Principles

## 3.1. Business Rules Are Authoritative

Architecture must implement approved business and system requirements.

Technical convenience must not silently change business behavior.

---

## 3.2. Server Is Authoritative

The server and PostgreSQL database are authoritative for current centralized system state.

Offline devices may create valid local transactions, but synchronization must validate them against server-side rules.

Offline operation does not create an alternative permanent source of truth.

---

## 3.3. Tenant Isolation

Every business is an isolated tenant.

Business data must never leak between tenants through:

* API requests;
* database queries;
* background jobs;
* reports;
* exports;
* cache;
* synchronization;
* notifications;
* audit records;
* offline packages.

---

## 3.4. Branch Isolation

Branches operate within a Business but maintain their own operational context.

Branch-scoped data must remain isolated according to permissions and business rules.

Cross-branch access must be explicit.

---

## 3.5. Historical Integrity

Historical records must not be silently overwritten.

Important changes must use:

* versioning;
* corrections;
* revisions;
* audit history;
* immutable snapshots.

Where deletion is required, it must follow the Data Lifecycle rules.

---

## 3.6. Security Without Excessive Friction

Security controls must protect the system without making normal POS operations unnecessarily slow.

Security must therefore be designed with:

* short operational paths;
* server-side authorization;
* trusted devices;
* offline authorization;
* encrypted local storage;
* strong password hashing;
* cryptographic signatures where required;
* auditability;
* rate limiting and resource protection.

---

## 3.7. Offline Continuity

A temporary network failure must not unnecessarily stop branch operations.

Trusted devices may continue permitted operations while offline according to:

* offline authorization;
* subscription state;
* employee permissions;
* branch scope;
* local configuration;
* local inventory state;
* synchronization rules.

---

## 3.8. Strong Consistency for Critical Transactions

The following operations require strong transactional protection:

* order acceptance;
* inventory deduction;
* payment creation;
* cash session operations;
* cash handover;
* critical corrections;
* inventory adjustments;
* important configuration changes.

Secondary operations may use asynchronous processing.

---

## 3.9. Idempotency

Retrying a request must not accidentally create duplicate business effects.

Important operations use stable UUID-based identities and idempotent processing.

Examples include:

* orders;
* payments;
* inventory transactions;
* cash sessions;
* synchronization events;
* reports;
* background jobs.

---

## 3.10. Explicit Conflict Resolution

Critical conflicts must not be silently resolved through generic last-write-wins behavior.

Conflicts must be:

1. detected;
2. recorded;
3. classified;
4. resolved according to the affected domain;
5. authorized when required;
6. audited.

---

# 4. Architecture Style

FastFood ERP uses a **modular monolith** as its primary application architecture.

The system is deployed as one main application while maintaining strong internal domain/module boundaries.

Conceptually:

```text
                    ┌─────────────────────┐
                    │      Clients        │
                    │ Web / POS / Offline │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     API Layer       │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
      ┌─────────────────┐             ┌─────────────────┐
      │ Application     │             │ Security /     │
      │ Services        │             │ Context        │
      └────────┬────────┘             └─────────────────┘
               │
               ▼
      ┌─────────────────────────────────────────────┐
      │              Domain Modules                 │
      │                                             │
      │ Business / Branch / Identity / Order        │
      │ Cash / Inventory / Payment / Menu           │
      │ Kitchen / Employee / Payroll / Reports      │
      │ Notification / Audit / Sync / Lifecycle     │
      │ Configuration / Device / Subscription      │
      └────────────────────┬────────────────────────┘
                           │
                           ▼
                  ┌───────────────────┐
                  │ Infrastructure    │
                  │ DB / Cache / Queue │
                  │ Storage / Printer  │
                  └───────────────────┘
```

The modular monolith is intentionally selected instead of starting with microservices.

---

# 5. Why Modular Monolith

The initial architecture prioritizes:

* simpler deployment;
* lower infrastructure requirements;
* simpler transactions;
* easier debugging;
* lower operational complexity;
* easier local development;
* faster development;
* strong module boundaries;
* future extraction capability.

The architecture must not depend on microservices for correctness.

If the product later requires service decomposition, modules should already have clear ownership boundaries.

---

# 6. Main Architectural Layers

FastFood ERP is organized into the following conceptual layers:

```text
Presentation
    ↓
API
    ↓
Application
    ↓
Domain
    ↓
Infrastructure
    ↓
Data / External Systems
```

## 6.1. Presentation Layer

Responsible for:

* user interface;
* POS screens;
* dashboards;
* forms;
* local offline UI;
* client-side validation;
* permission-aware navigation.

The frontend must not become the authoritative source of business rules.

---

## 6.2. API Layer

Responsible for:

* HTTP endpoints;
* authentication context;
* request validation;
* authorization checks;
* serialization;
* API error responses;
* idempotency handling;
* API versioning.

Current API namespace:

```text
/api/v1
```

---

## 6.3. Application Layer

Responsible for:

* use cases;
* orchestration;
* transaction boundaries;
* domain service invocation;
* authorization coordination;
* synchronization processing;
* background job coordination.

Application services must not contain uncontrolled business logic duplicated across endpoints.

---

## 6.4. Domain Layer

Responsible for:

* business rules;
* domain entities;
* aggregates;
* value objects;
* domain services;
* domain events;
* invariants.

Domain modules must own their important business behavior.

---

## 6.5. Infrastructure Layer

Responsible for:

* PostgreSQL;
* SQLAlchemy;
* Redis-compatible services;
* queues;
* background workers;
* file/object storage;
* printing infrastructure;
* external integrations;
* cryptographic infrastructure;
* logging and monitoring infrastructure.

Infrastructure must not redefine domain rules.

---

# 7. Domain Module Structure

The architecture recognizes the following major domains:

1. Business
2. Identity and Access
3. Subscription
4. Branch
5. Order
6. Cash
7. Inventory
8. Payment
9. Menu and Pricing
10. Kitchen
11. Employee and Payroll
12. Reporting
13. Notification
14. Audit
15. Synchronization
16. Data Lifecycle
17. Configuration
18. Device and Trust
19. Cross-Domain Coordination
20. System Infrastructure

The exact implementation structure may differ from the conceptual domain list, but ownership boundaries must remain clear.

---

# 8. Core Transaction Boundary

Critical operations must be atomic where business correctness requires it.

For example:

```text
Order Acceptance
      │
      ├── Validate order
      ├── Validate permission
      ├── Validate configuration
      ├── Validate inventory
      ├── Deduct inventory
      ├── Persist order state
      └── Commit transaction
```

Secondary processing happens after successful core persistence:

```text
Core Transaction
      │
      └── Commit
           │
           ├── Kitchen notification
           ├── Printer processing
           ├── Notification
           ├── Audit secondary processing
           └── Reporting update
```

A failure in secondary processing must not roll back a successful core transaction unless explicitly required by the domain rule.

---

# 9. Database Architecture

PostgreSQL is the authoritative transactional database.

Primary database principles:

* relational integrity;
* foreign keys;
* transactions;
* constraints;
* indexes;
* row-level concurrency protection where required;
* migration-based schema evolution;
* tenant and branch scoping;
* immutable historical records where required.

SQLAlchemy is used as the primary application database access layer.

Alembic is used for database migrations.

The database must not become an uncontrolled shared data-access layer between modules.

---

# 10. API Architecture

The API uses REST-style HTTP endpoints.

Current version:

```text
/api/v1
```

API design must provide:

* authentication;
* authorization;
* validation;
* tenant context;
* branch context;
* idempotency;
* deterministic errors;
* pagination;
* filtering;
* safe retries;
* version compatibility.

API endpoints must call application services rather than directly implementing complex domain logic.

---

# 11. Offline Architecture

Offline operation is a first-class architectural capability.

Trusted devices may temporarily operate without a network connection.

Offline architecture includes:

* device trust;
* offline authorization;
* encrypted local storage;
* local UUID identity;
* local transaction persistence;
* durable synchronization queue;
* synchronization validation;
* conflict detection;
* conflict resolution;
* replay protection;
* clock rollback detection.

New devices cannot begin normal offline operation before completing online registration and trust establishment.

---

# 12. Synchronization Architecture

Synchronization connects local offline state with server state.

Conceptual flow:

```text
Local Operation
      ↓
Durable Local Queue
      ↓
Pending
      ↓
Syncing
      ↓
Server Validation
      ↓
┌──────────────┬──────────────┬──────────────┐
│    Synced    │   Conflict   │    Failed    │
└──────────────┴──────────────┴──────────────┘
```

Synchronization must support:

* idempotency;
* dependency ordering;
* bounded batches;
* partial batch success;
* retry;
* conflict records;
* server-side validation;
* audit;
* multi-device synchronization.

Critical synchronization conflicts must never be silently discarded.

---

# 13. Security Architecture

Security is implemented across multiple layers.

Main controls include:

* employee authentication;
* role permissions;
* employee overrides;
* branch scope;
* subscription entitlement;
* trusted device;
* offline authorization;
* encrypted local storage;
* password hashing with Argon2id;
* TLS;
* cryptographic signatures;
* audit logging;
* rate limiting;
* resource protection;
* clock anomaly detection.

Authentication does not automatically grant authorization.

Device trust does not automatically grant permissions.

Subscription entitlement does not replace permission checks.

---

# 14. Event and Message Architecture

The system uses domain events and asynchronous processing where appropriate.

Events may trigger:

* notifications;
* kitchen processing;
* printing;
* report processing;
* audit processing;
* synchronization;
* background jobs.

Events must not replace transactional consistency for core operations.

The initial architecture does not require a distributed event platform such as Kafka.

An outbox-style reliability mechanism may be used where event delivery reliability is required.

---

# 15. Background Processing

Background workers handle operations that should not block normal POS workflows.

Examples:

* large reports;
* Excel exports;
* notifications;
* retries;
* synchronization;
* lifecycle processing;
* subscription transitions;
* deletion jobs;
* cleanup;
* heavy calculations.

Core POS operations must not depend unnecessarily on background workers.

If a worker is unavailable, the system must preserve the underlying transaction and provide a recoverable pending state where applicable.

---

# 16. Caching

Caching is an optimization layer, not an authoritative data source.

Primary cache principles:

* cache-aside where appropriate;
* explicit TTL;
* invalidation after relevant changes;
* tenant-aware keys;
* branch-aware keys;
* permission-aware access;
* no security bypass through cached data.

Critical transaction correctness must never depend solely on cache state.

Redis-compatible infrastructure may be used for:

* cache;
* short-lived coordination;
* queues;
* background processing support.

---

# 17. Observability

The system must provide sufficient operational visibility to diagnose failures.

Observability includes:

* structured logs;
* metrics;
* health checks;
* background job status;
* synchronization status;
* failed operations;
* database errors;
* resource usage;
* security events;
* audit events.

Important operations should be traceable through stable identifiers such as:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Order UUID;
* Payment UUID;
* Cash Session UUID;
* Transaction UUID;
* Report UUID;
* Job UUID.

Sensitive information must not be unnecessarily written to logs.

---

# 18. Scalability

The initial architecture targets a practical deployment model rather than premature distributed infrastructure.

The architecture must support future horizontal scaling.

Potential scaling path:

```text
Single Application
       ↓
Multiple Application Instances
       ↓
Load Balancer
       ↓
Shared PostgreSQL
       ↓
Dedicated Worker Instances
       ↓
Database Read Scaling / Additional Infrastructure
```

Scaling must not break:

* tenant isolation;
* transaction correctness;
* idempotency;
* synchronization;
* audit;
* historical integrity.

---

# 19. Performance Principles

POS performance is a major architectural requirement.

The system should minimize:

* unnecessary network round trips;
* expensive synchronous processing;
* excessive database queries;
* redundant permission calculations;
* unnecessary cache misses;
* blocking background operations.

Heavy work should be moved to background processing where business correctness permits it.

Security checks must remain efficient.

The system should run on ordinary POS and office hardware.

---

# 20. Failure and Recovery

Every important operation must have a defined failure behavior.

A failed operation must result in one of:

```text
Success
Safe Rejection
Recoverable Pending State
```

The system must avoid ambiguous outcomes such as:

```text
"Maybe it succeeded."
```

Idempotency and transaction identifiers must allow safe retry.

Recovery must preserve:

* financial integrity;
* inventory integrity;
* cash integrity;
* audit history;
* historical records;
* tenant isolation.

---

# 21. Technology Baseline

The approved initial technology direction is:

| Area                  | Technology / Approach              |
| --------------------- | ---------------------------------- |
| Backend               | Python                             |
| Web Framework         | Flask                              |
| API                   | REST / HTTP                        |
| API Version           | `/api/v1`                          |
| Database              | PostgreSQL                         |
| ORM / DB Access       | SQLAlchemy                         |
| Migrations            | Alembic                            |
| Cache / Queue Support | Redis-compatible                   |
| Background Processing | Dedicated Worker                   |
| Frontend              | Web Application                    |
| Offline Storage       | Encrypted Local Storage            |
| Password Hashing      | Argon2id                           |
| Transport Security    | TLS                                |
| Reverse Proxy         | Nginx or equivalent                |
| Application Server    | Gunicorn or equivalent WSGI server |
| Production OS         | Linux                              |
| Reporting Export      | XLSX                               |
| Monitoring            | Prometheus-compatible metrics      |
| Source Control        | Git                                |
| CI/CD                 | Automated pipeline                 |

Technology choices are documented in:

`18_Technology_Selection.md`

Technology changes must follow architecture governance and ADR rules.

---

# 22. Deployment Architecture

The initial deployment should remain operationally simple.

Conceptual production environment:

```text
Internet
   ↓
Reverse Proxy
   ↓
Application Server
   ↓
Flask Application
   ↓
PostgreSQL

Background Worker
   ↓
Queue / Redis-compatible service

Monitoring
   ↓
Logs + Metrics + Health Checks
```

Production deployment must include:

* secure configuration;
* secrets management;
* database backup;
* migration process;
* health checks;
* logging;
* monitoring;
* recovery procedures.

---

# 23. Data Lifecycle

Business data follows a controlled lifecycle:

```text
Active
   ↓
Expired / Read-Only
   ↓
Deletion Eligible
   ↓
Deleting
   ↓
Deleted
```

The default retention period after subscription expiry is 60 days.

Reactivation during the retention period restores the existing Business and its data.

After permanent deletion, the Business UUID must never be reused.

Data lifecycle rules are defined in:

`17_Failure_Recovery_Architecture.md`

and the corresponding Domain/System Analysis documents.

---

# 24. Architecture Decision Governance

Architecture decisions must be documented.

Important decisions should include:

* decision;
* context;
* alternatives;
* selected approach;
* reasons;
* trade-offs;
* consequences.

Architecture decisions must not be hidden only inside source code.

The main architecture decision document is:

`19_Architecture_Decisions_and_Tradeoffs.md`

Formal architecture changes may require a new ADR under:

```text
adr/
```

---

# 25. Architecture Invariants

The following rules are mandatory:

1. Tenant isolation must always be preserved.
2. Branch isolation must always be respected.
3. Server state is authoritative after synchronization.
4. Critical transactions must be atomic.
5. Critical operations must be idempotent.
6. Historical records must not be silently overwritten.
7. Permissions must be enforced server-side.
8. Device trust must not grant permissions.
9. Subscription entitlement must not replace authorization.
10. Offline operations must remain within offline authorization.
11. Offline synchronization must be idempotent.
12. Critical conflicts must be explicit.
13. Cache must not become the source of truth.
14. Background jobs must not silently lose business operations.
15. Secondary processing must not unnecessarily block POS.
16. Failed operations must have deterministic outcomes.
17. Database migrations must be backward-aware where required.
18. Security controls must not bypass business rules.
19. Architecture changes must be documented.
20. New modules must have clear ownership boundaries.

The complete invariant catalog is defined in:

`20_Architecture_Invariants_and_Guardrails.md`

---

# 26. Architecture Document Catalog

## 26.1. System Architecture

`01_System_Architecture.md`

Defines the overall system structure and major architectural boundaries.

## 26.2. Application Layer Architecture

`02_Application_Layer_Architecture.md`

Defines application services, use cases, orchestration, and application-layer responsibilities.

## 26.3. Domain Module Architecture

`03_Domain_Module_Architecture.md`

Defines domain module boundaries, ownership, dependencies, aggregates, services, and events.

## 26.4. Backend Architecture

`04_Backend_Architecture.md`

Defines backend implementation structure and runtime responsibilities.

## 26.5. Frontend Architecture

`05_Frontend_Architecture.md`

Defines frontend structure, state handling, navigation, POS architecture, and client responsibilities.

## 26.6. API Architecture

`06_API_Architecture.md`

Defines API organization, versioning, validation, authorization, errors, pagination, and idempotency.

## 26.7. Database Architecture

`07_Database_Architecture.md`

Defines database-level architecture and persistence boundaries.

## 26.8. Offline Architecture

`08_Offline_Architecture.md`

Defines offline operation, trusted devices, local storage, authorization, and offline limitations.

## 26.9. Synchronization Architecture

`09_Synchronization_Architecture.md`

Defines synchronization flow, ordering, retry, idempotency, and conflict handling.

## 26.10. Security Architecture

`10_Security_Architecture.md`

Defines system-wide security architecture and security boundaries.

## 26.11. Deployment Architecture

`11_Deployment_Architecture.md`

Defines production infrastructure, deployment topology, environments, and runtime components.

## 26.12. Event and Message Architecture

`12_Event_and_Message_Architecture.md`

Defines domain events, asynchronous messages, delivery reliability, and event boundaries.

## 26.13. Background Processing Architecture

`13_Background_Processing_Architecture.md`

Defines workers, queues, jobs, retries, scheduling, and background processing rules.

## 26.14. Caching Architecture

`14_Caching_Architecture.md`

Defines cache usage, invalidation, TTL, isolation, and cache consistency rules.

## 26.15. Observability and Operations Architecture

`15_Observability_and_Operations_Architecture.md`

Defines logging, metrics, health checks, operational visibility, and system diagnostics.

## 26.16. Scalability and Performance Architecture

`16_Scalability_and_Performance_Architecture.md`

Defines performance requirements, scaling strategy, resource protection, and future growth.

## 26.17. Failure Recovery Architecture

`17_Failure_Recovery_Architecture.md`

Defines failure classification, recovery behavior, retry, resilience, RTO/RPO, and recovery testing.

## 26.18. Technology Selection

`18_Technology_Selection.md`

Defines the selected technology stack and technology governance.

## 26.19. Architecture Decisions and Tradeoffs

`19_Architecture_Decisions_and_Tradeoffs.md`

Consolidates major architectural decisions and their trade-offs.

## 26.20. Architecture Invariants and Guardrails

`20_Architecture_Invariants_and_Guardrails.md`

Defines mandatory architecture rules that must be preserved during implementation and future changes.

---

# 27. Architecture Dependency Flow

The architecture documents should be understood in the following order:

```text
System Architecture
        ↓
Application Layer
        ↓
Domain Modules
        ↓
Backend / Frontend / API
        ↓
Database
        ↓
Offline / Synchronization
        ↓
Security
        ↓
Deployment
        ↓
Events / Background Processing
        ↓
Caching
        ↓
Observability
        ↓
Scalability / Performance
        ↓
Failure Recovery
        ↓
Technology Selection
        ↓
Architecture Decisions
        ↓
Architecture Invariants
```

The order represents conceptual dependency, not necessarily implementation order.

---

# 28. Relationship with Previous Documentation Layers

## Business Analysis

Defines:

> What the business needs.

Location:

```text
docs/01_Business_Analysis/
```

## System Analysis

Defines:

> What the system must do.

Location:

```text
docs/02_System_Analysis/
```

## Domain Analysis

Defines:

> Which domain concepts exist and how responsibilities are separated.

Location:

```text
docs/03_Domain_Analysis/
```

## Architecture

Defines:

> How the system is technically structured to satisfy those requirements.

Location:

```text
docs/04_Architecture/
```

## Database

Defines:

> How persistent data is structurally represented and protected.

Location:

```text
docs/05_Database/
```

---

# 29. Architecture Change Rules

When changing architecture:

1. Identify the affected architecture document.
2. Check related Domain Analysis documents.
3. Check System Analysis requirements.
4. Check Business Analysis rules.
5. Identify affected ADRs.
6. Identify affected database/API/backend/frontend documents.
7. Update dependent documentation.
8. Verify architecture invariants.
9. Review migration and backward-compatibility impact.
10. Record the final decision.

Architecture changes must not be made only in code.

---

# 30. AI Coding Agent Guardrails

AI coding agents working on FastFood ERP must follow the architecture documentation.

Agents must:

* read relevant architecture documents before implementing major changes;
* respect module ownership;
* avoid direct cross-domain database writes;
* preserve tenant and branch isolation;
* preserve idempotency;
* preserve historical integrity;
* preserve offline synchronization rules;
* preserve audit requirements;
* avoid introducing undocumented dependencies;
* avoid changing business behavior without approval;
* update documentation when architecture changes;
* create or update ADRs for significant architectural decisions.

Agents must not optimize for short code at the expense of architecture correctness.

---

# 31. Architecture Completion Criteria

The Architecture layer is considered complete when:

* all 20 architecture documents exist;
* architecture boundaries are defined;
* technology baseline is defined;
* database architecture is defined;
* API architecture is defined;
* offline architecture is defined;
* synchronization architecture is defined;
* security architecture is defined;
* deployment architecture is defined;
* failure recovery is defined;
* scalability and performance principles are defined;
* major architectural decisions are documented;
* architecture invariants are documented;
* downstream Database, Backend, Frontend, API, Security, Testing, and Deployment work can reference these documents without redefining architecture fundamentals.

---

# 32. Next Layer

After the Architecture layer, development documentation continues with:

```text
docs/05_Database/
```

The Database layer will translate the architecture and domain definitions into:

* database entities;
* relationships;
* keys;
* constraints;
* indexes;
* transactions;
* migrations;
* database integrity rules;
* backup and recovery structures.

The Database layer must not redefine approved domain ownership or business behavior.

---

# 33. Final Architecture Principle

FastFood ERP architecture follows one central principle:

> **The system may be technically complex internally, but its business operations must remain reliable, understandable, secure, and fast for everyday users.**

Architecture must therefore optimize for:

**Correctness + Security + Historical Integrity + Offline Continuity + Performance + Maintainability + Scalability**

without introducing unnecessary technical complexity.

---

## Related Documents

### Previous Layer

* `docs/01_Business_Analysis/README.md`
* `docs/02_System_Analysis/README.md`
* `docs/03_Domain_Analysis/README.md`

### Architecture

* `01_System_Architecture.md`
* `02_Application_Layer_Architecture.md`
* `03_Domain_Module_Architecture.md`
* `04_Backend_Architecture.md`
* `05_Frontend_Architecture.md`
* `06_API_Architecture.md`
* `07_Database_Architecture.md`
* `08_Offline_Architecture.md`
* `09_Synchronization_Architecture.md`
* `10_Security_Architecture.md`
* `11_Deployment_Architecture.md`
* `12_Event_and_Message_Architecture.md`
* `13_Background_Processing_Architecture.md`
* `14_Caching_Architecture.md`
* `15_Observability_and_Operations_Architecture.md`
* `16_Scalability_and_Performance_Architecture.md`
* `17_Failure_Recovery_Architecture.md`
* `18_Technology_Selection.md`
* `19_Architecture_Decisions_and_Tradeoffs.md`
* `20_Architecture_Invariants_and_Guardrails.md`

### Next Layer

* `docs/05_Database/`

