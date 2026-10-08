# Backend Architecture

**Document ID:** BA-README
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This directory contains the complete Backend Architecture documentation for FastFood ERP.

The Backend is responsible for:

* business operations;
* authentication;
* authorization;
* Business and Branch isolation;
* application workflows;
* domain logic;
* database access;
* transactions;
* synchronization;
* background processing;
* notifications;
* reporting;
* audit and history;
* security;
* caching;
* search;
* deployment;
* operations;
* disaster recovery;
* data consistency;
* reconciliation.

The Backend is the authoritative execution layer for business rules.

The frontend must not replace Backend authority.

---

# 2. Backend Architectural Style

FastFood ERP uses a **Modular Monolith** as its initial Backend architecture.

The system is intentionally not split into microservices at the initial stage.

The main architecture is:

```text
Client
  ↓
API
  ↓
Application / Use Cases
  ↓
Domain
  ↓
Repository Interfaces
  ↓
Infrastructure
  ↓
PostgreSQL
```

Supporting infrastructure:

```text
Application
├── Background Jobs
├── Outbox / Events
├── Synchronization
├── Notifications
├── Reporting
├── File Storage
├── Cache
└── External Integrations
```

---

# 3. Backend Authority

The Backend is authoritative for:

* authentication;
* authorization;
* Business scope;
* Branch scope;
* subscription entitlement;
* order state;
* payment state;
* cash state;
* inventory state;
* pricing rules;
* configuration;
* historical data;
* audit records;
* synchronization validation;
* concurrency;
* idempotency;
* lifecycle;
* deletion;
* financial calculations.

The frontend may provide validation and UX controls, but the Backend remains authoritative.

---

# 4. Architectural Layers

The Backend is divided into the following logical layers:

```text
API
 ↓
Application
 ↓
Domain
 ↓
Repository Interfaces
 ↓
Infrastructure
```

Supporting layers:

```text
Security
Background
Synchronization
Reporting
Shared
```

### API

Responsible for:

* HTTP;
* request parsing;
* authentication integration;
* route handling;
* response serialization;
* API contracts.

API routes must remain thin.

### Application

Responsible for:

* use cases;
* workflow orchestration;
* authorization invocation;
* transaction boundaries;
* domain service coordination;
* repository coordination.

### Domain

Responsible for:

* business rules;
* entities;
* value objects;
* domain services;
* domain invariants.

### Repository

Responsible for:

* persistence abstraction;
* query execution;
* scope-aware data access.

Repositories do not own application transaction boundaries.

### Infrastructure

Responsible for:

* PostgreSQL;
* SQLAlchemy;
* Redis;
* storage;
* external integrations;
* cryptography;
* logging;
* infrastructure-specific implementations.

---

# 5. Core Architectural Rules

The following dependency direction is mandatory:

```text
API
 ↓
Application
 ↓
Domain
```

Infrastructure implements interfaces required by Application/Domain.

The Domain must not depend on:

* HTTP;
* SQLAlchemy;
* Redis;
* Flask/FastAPI-specific objects;
* filesystem implementation;
* external providers.

The API must not directly modify database state.

Repositories must not unexpectedly commit transactions.

---

# 6. Multi-Tenant Isolation

FastFood ERP uses:

```text
Business
   ↓
Branch
   ↓
Operational Data
```

Business UUID is the primary tenant isolation boundary.

Every Business-scoped operation must validate Business ownership.

Branch-scoped operations must validate:

```text
Business
+
Branch
+
Employee Scope
+
Permission
```

Cross-Business access is prohibited.

Unauthorized cross-Branch access is prohibited.

---

# 7. Authentication and Authorization

Authentication establishes:

```text
Who is the user?
```

Authorization establishes:

```text
What can the user do?
```

The authorization pipeline is conceptually:

```text
Authenticate
    ↓
Employee Status
    ↓
Business Status
    ↓
Branch Scope
    ↓
Permission
    ↓
Subscription Entitlement
    ↓
Device Rules
    ↓
Business Rules
    ↓
Execute
```

Trusted devices are part of security and offline operation.

A trusted device does not replace authorization.

---

# 8. Transaction Architecture

Application use cases own transaction boundaries.

Core operations must be atomic where required.

Examples:

* Order acceptance;
* payment;
* refund;
* cash session;
* inventory deduction;
* recipe approval;
* configuration changes;
* synchronization ingestion.

External operations must not normally execute inside core database transactions.

Examples:

* printing;
* email;
* notifications;
* report generation;
* file generation;
* external API calls.

These are handled after commit through background processing where appropriate.

---

# 9. Idempotency

Retryable operations use UUID-based operation identity.

Conceptually:

```text
operation_id
```

identifies one logical command.

Repeated delivery of the same operation must not create duplicate business effects.

Idempotency must be validated server-side.

---

# 10. Concurrency

The Backend uses different concurrency strategies depending on the domain.

### Optimistic Concurrency

Used primarily for:

* configuration;
* menu;
* pricing;
* administrative changes.

### Row-Level Locking

Used where required for:

* inventory;
* cash;
* financial state;
* other contention-sensitive resources.

### Database Constraints

Used for:

* uniqueness;
* idempotency;
* identity integrity;
* critical invariants.

Silent last-write-wins behavior is prohibited for important business configuration.

---

# 11. Offline-First Backend Integration

Trusted devices may operate offline within the defined authorization period.

The Backend validates synchronized operations for:

* device;
* employee;
* Business;
* Branch;
* operation UUID;
* authorization;
* subscription/lifecycle;
* timestamps;
* configuration;
* business rules.

Synchronization must not blindly trust client state.

The server remains authoritative after synchronization.

Transaction synchronization takes priority over configuration synchronization.

---

# 12. Background Processing

Long-running and secondary operations are handled asynchronously.

Examples:

* notifications;
* email;
* printing;
* report generation;
* XLSX export;
* synchronization processing;
* cleanup;
* subscription lifecycle;
* data deletion;
* reconciliation;
* cache invalidation.

Background processing must not block normal POS operation.

---

# 13. Outbox and Events

Important domain events may use an Outbox pattern.

Conceptually:

```text
Business Transaction
       ↓
Database State + Outbox Event
       ↓
Commit
       ↓
Worker
       ↓
External / Secondary Processing
```

The Outbox prevents committed business changes from being silently disconnected from required asynchronous processing.

---

# 14. Reporting

Reports use authoritative transactional data.

Large or expensive reports may be generated asynchronously.

Report versions are immutable.

Historical report versions must not be rewritten.

XLSX exports are generated through background processing where appropriate.

---

# 15. Audit and History

Audit and History are separate concepts.

### Audit

Answers:

```text
Who did what, when, where and from which device?
```

### History

Answers:

```text
What changed over time?
```

Both must preserve historical integrity.

Important audit/history records are immutable and append-oriented.

---

# 16. Search and Filtering

PostgreSQL is the primary search/query engine initially.

Search architecture supports:

* exact search;
* prefix search;
* partial search;
* filtering;
* sorting;
* pagination;
* cursor pagination;
* audit/history search.

A dedicated search engine should only be introduced when actual scale or functionality justifies it.

---

# 17. Caching

PostgreSQL remains authoritative.

Cache is an optimization layer.

Potential cache targets include:

* Business configuration;
* Branch configuration;
* menu;
* pricing;
* permissions;
* reference data;
* feature configuration;
* short-lived entitlement data.

Cache must never become authoritative for:

* final inventory deduction;
* cash state;
* payment state;
* historical state;
* idempotency;
* deletion state.

Redis is optional and non-authoritative.

---

# 18. Security

Backend security follows defense-in-depth principles.

Security boundaries include:

* authentication;
* authorization;
* Business isolation;
* Branch isolation;
* trusted devices;
* offline authorization;
* secure sessions/tokens;
* password hashing;
* rate limiting;
* input validation;
* SQL injection protection;
* file security;
* secret management;
* secure transport;
* audit;
* dependency security;
* security monitoring.

Security controls must not introduce unnecessary POS latency.

---

# 19. Performance

Performance priority:

```text
POS
 ↓
Cash
 ↓
Inventory
 ↓
Authentication
 ↓
Synchronization
 ↓
Business Management
 ↓
Reports
 ↓
Exports
 ↓
Cleanup
```

Initial important targets include:

* ordinary API p95 ≤ 300 ms;
* core POS command p95 ≤ 500 ms;
* authorization overhead p95 ≤ 100 ms;
* normal synchronization batch p95 ≤ 1 s;
* API availability ≥ 99.9%.

Exact targets are defined in the relevant architecture documents.

---

# 20. Error Handling

Backend errors must be classified consistently.

Major categories include:

```text
Validation Error
Authorization Error
Business Rule Violation
Conflict
Temporary Infrastructure Error
Permanent Failure
```

Errors must expose stable application error codes.

Internal infrastructure details must not unnecessarily leak to clients.

---

# 21. Configuration

Backend configuration is separated into:

* environment configuration;
* application configuration;
* secret configuration;
* infrastructure configuration;
* integration configuration;
* Business configuration;
* Branch configuration;
* feature configuration.

Secrets must not be stored in source control.

Business and Branch configuration is persisted as business data where appropriate.

---

# 22. API Architecture

The API must provide stable contracts between frontend and Backend.

API responsibilities include:

* authentication;
* request validation;
* authorization integration;
* use-case invocation;
* serialization;
* error mapping;
* pagination;
* idempotency;
* request tracing.

Business logic must remain outside API route handlers.

---

# 23. Deployment Architecture

Initial production deployment may use:

```text
Internet
   ↓
Nginx
   ↓
Gunicorn
   ↓
FastFood Backend
   ↓
PostgreSQL
```

Optional supporting services:

```text
Redis
Workers
Scheduler
File Storage
Backup Storage
```

PostgreSQL and Redis should not be publicly exposed.

The initial VPS deployment may use Linux systemd services.

Kubernetes is not required for the initial architecture.

---

# 24. Operations

Backend operations include:

* health checks;
* readiness checks;
* structured logging;
* metrics;
* monitoring;
* alerting;
* backup;
* restore testing;
* deployment validation;
* incident handling;
* reconciliation;
* capacity monitoring.

Production systems must provide enough observability to diagnose operational failures.

---

# 25. Disaster Recovery

The Backend must support recovery from:

* application failure;
* database failure;
* infrastructure failure;
* deployment failure;
* accidental data corruption;
* storage failure.

Initial targets:

```text
RPO ≤ 15 minutes
RTO ≤ 2 hours
```

where infrastructure capabilities support these targets.

Backups must be tested through actual restoration procedures.

---

# 26. Data Consistency

PostgreSQL is the primary authoritative data store.

Consistency mechanisms include:

* database constraints;
* transactions;
* row locks;
* optimistic concurrency;
* idempotency;
* audit;
* reconciliation;
* immutable history.

Secondary systems such as Redis, queues and file storage must not override authoritative database state.

---

# 27. Backend Documentation Map

The Backend documentation is organized into 25 architecture documents.

|  # | Document                                                               | Purpose                                   |
| -: | ---------------------------------------------------------------------- | ----------------------------------------- |
| 01 | `01_Backend_Architecture.md`                                           | Overall Backend architecture              |
| 02 | `02_Backend_Project_Structure.md`                                      | Project and package structure             |
| 03 | `03_Application_and_Use_Case_Layer.md`                                 | Application/use-case architecture         |
| 04 | `04_Domain_Service_and_Business_Logic.md`                              | Domain logic and services                 |
| 05 | `05_Repository_and_Data_Access.md`                                     | Repository and persistence boundary       |
| 06 | `06_Authentication_and_Authorization.md`                               | Authentication and authorization          |
| 07 | `07_Transaction_Management.md`                                         | Transaction and Unit of Work architecture |
| 08 | `08_Error_Handling_and_Exception_Architecture.md`                      | Error and exception architecture          |
| 09 | `09_Events_Outbox_and_Background_Jobs.md`                              | Events, Outbox and background processing  |
| 10 | `10_Notifications_and_External_Integrations.md`                        | Notifications and external systems        |
| 11 | `11_Configuration_and_Environment_Management.md`                       | Configuration and environment management  |
| 12 | `12_Reporting_and_Export_Architecture.md`                              | Reports and exports                       |
| 13 | `13_Backend_Health_Observability_and_Monitoring.md`                    | Health, monitoring and observability      |
| 14 | `14_Backend_Caching_and_Performance_Architecture.md`                   | Cache and performance                     |
| 15 | `15_Backend_File_Storage_and_Document_Management.md`                   | Files and document storage                |
| 16 | `16_Backend_Security_Hardening_and_Application_Security.md`            | Application security                      |
| 17 | `17_Backend_Testing_and_Quality_Assurance_Architecture.md`             | Testing and QA                            |
| 18 | `18_Backend_API_Design_and_Contract_Architecture.md`                   | API design and contracts                  |
| 19 | `19_Backend_Deployment_and_Runtime_Architecture.md`                    | Deployment and runtime                    |
| 20 | `20_Backend_Operations_and_Incident_Management_Architecture.md`        | Operations and incidents                  |
| 21 | `21_Backend_Disaster_Recovery_and_Business_Continuity_Architecture.md` | Disaster recovery and continuity          |
| 22 | `22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`       | Consistency and reconciliation            |
| 23 | `23_Backend_Audit_and_History_Architecture.md`                         | Audit and historical integrity            |
| 24 | `24_Backend_Search_and_Filtering_Architecture.md`                      | Search and filtering                      |
| 25 | `25_Backend_Queue_and_Worker_Architecture.md`                          | Queue and worker architecture             |

---

# 28. Recommended Reading Order

For developers and AI agents, the recommended reading order is:

```text
README
  ↓
01 Backend Architecture
  ↓
02 Project Structure
  ↓
03 Application Layer
  ↓
04 Domain Layer
  ↓
05 Repository/Data Access
  ↓
06 Authentication/Authorization
  ↓
07 Transactions
  ↓
08 Error Handling
  ↓
09 Events/Outbox/Background Jobs
  ↓
10 Notifications/Integrations
  ↓
11 Configuration
  ↓
12 Reporting/Exports
  ↓
13 Observability
  ↓
14 Caching/Performance
  ↓
15 File Storage
  ↓
16 Security
  ↓
17 Testing
  ↓
18 API Contracts
  ↓
19 Deployment
  ↓
20 Operations
  ↓
21 Disaster Recovery
  ↓
22 Consistency/Reconciliation
  ↓
23 Audit/History
  ↓
24 Search/Filtering
  ↓
25 Queue/Worker
```

---

# 29. AI Agent Guidance

AI agents working on the Backend must follow this order:

### Step 1 — Read Context

Read:

* this README;
* relevant Business Analysis document;
* relevant System Analysis document;
* relevant Database document;
* relevant Backend architecture document.

### Step 2 — Check Existing Decisions

Before creating new behavior, verify whether the requirement has already been decided.

Do not invent a conflicting rule.

### Step 3 — Respect Layer Boundaries

Do not:

* put business logic in API routes;
* access PostgreSQL directly from API handlers;
* put infrastructure logic in Domain;
* put authorization logic only in frontend;
* commit from repositories.

### Step 4 — Preserve Invariants

Before changing code, identify relevant invariants.

### Step 5 — Consider Cross-Cutting Concerns

For important changes evaluate:

* authentication;
* authorization;
* Business scope;
* Branch scope;
* subscription;
* transactions;
* idempotency;
* concurrency;
* audit;
* offline synchronization;
* performance;
* observability;
* error handling.

### Step 6 — Update Documentation

If implementation introduces a new architectural decision, update the relevant document and ADR when required.

---

# 30. Source of Truth Hierarchy

When documentation appears to conflict, use the following conceptual hierarchy:

```text
Business Requirements
        ↓
System Analysis
        ↓
Domain Analysis
        ↓
Architecture
        ↓
Database / Backend / Frontend Design
        ↓
Implementation
```

An implementation must not silently override a higher-level business requirement.

If a conflict is discovered, it should be explicitly resolved and documented.

---

# 31. Change Management

Architectural changes must be evaluated for impact on:

* Business requirements;
* System Analysis;
* Domain model;
* Database;
* Backend;
* Frontend;
* API contracts;
* Offline synchronization;
* Security;
* deployment;
* testing.

Significant architectural decisions should receive an ADR.

---

# 32. Backend Completion Criteria

The Backend Architecture documentation is considered complete when:

* all 25 documents exist;
* each document has a defined scope;
* cross-document dependencies are documented;
* Business/System/Database requirements are referenced;
* security boundaries are defined;
* transaction boundaries are defined;
* offline behavior is defined;
* consistency rules are defined;
* observability is defined;
* deployment is defined;
* recovery is defined;
* testing expectations are defined;
* performance/SLO expectations are defined;
* no major Backend architectural area is intentionally undocumented.

This README serves as the navigation and completeness index.

---

# 33. Backend Status

**Backend Architecture Documentation:** Complete

**Documents:** 25 + README

**Architecture Style:** Modular Monolith

**Primary Database:** PostgreSQL

**Cache:** Redis optional, non-authoritative

**Background Processing:** Queue/Worker architecture

**API:** Contract-driven

**Security:** Defense in depth

**Offline:** Trusted-device-first

**Synchronization:** UUID/idempotency + server-authoritative validation

**Deployment:** Nginx + Gunicorn + PostgreSQL + Workers initially

**Disaster Recovery:** Backup + Restore + RPO/RTO targets

**Historical Integrity:** Immutable audit/history

**Current Status:** Ready for Frontend Architecture

---

# 34. Related Documents

### Architecture

* `docs/04_Architecture/README.md`
* `docs/04_Architecture/01_Architecture_Principles.md`
* `docs/04_Architecture/02_System_Architecture.md`
* `docs/04_Architecture/03_Module_Boundaries.md`
* `docs/04_Architecture/04_Cross_Cutting_Concerns.md`

### Business Analysis

* `docs/01_Business_Analysis/README.md`

### System Analysis

* `docs/02_System_Analysis/README.md`

### Domain Analysis

* `docs/03_Domain_Analysis/README.md`

### Database

* `docs/05_Database/README.md`

### Frontend

* `docs/07_Frontend/README.md`

### Security

* `docs/11_Security/README.md`

### Testing

* `docs/12_Testing/README.md`

### Development

* `docs/13_Development/README.md`

### Operations

* `docs/14_Operations/README.md`

### ADR

* `adr/ADR-001-Documentation-First.md`

---

# 35. Status

**Document:** `docs/04_Architecture/06_Backend/README.md`

**Version:** 1.0

**Status:** Accepted

**Backend Architecture:** Complete

**Next Architecture Area:** Frontend

**Next Document:** `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`

