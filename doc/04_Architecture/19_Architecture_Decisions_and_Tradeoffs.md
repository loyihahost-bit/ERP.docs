# Architecture Decisions and Trade-offs

**Document ID:** ARCH-19
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

---

## 1. Purpose

This document records the major architectural decisions made for FastFood ERP and explains the trade-offs behind them.

The purpose is to ensure that important architectural choices are:

* explicit;
* understandable;
* traceable;
* consistent across the system;
* maintainable over time;
* protected from accidental reversal;
* understandable to future developers and AI coding agents.

This document does not replace individual ADRs.

It provides a consolidated architectural decision map.

Detailed decisions that require independent lifecycle management should also be represented by dedicated ADR documents.

---

# 2. Decision Principles

Architecture decisions follow these principles:

1. Business correctness has priority over implementation convenience.
2. Security must not unnecessarily slow normal POS operations.
3. Historical integrity must be preserved.
4. PostgreSQL remains authoritative for server-side business state.
5. Offline operation is a first-class requirement.
6. Synchronization must be explicit and idempotent.
7. Critical financial and inventory operations require strong transactional consistency.
8. Secondary operations should be asynchronous where appropriate.
9. Infrastructure complexity must be justified.
10. Domain boundaries must remain explicit.
11. Technology choices must support maintainability.
12. Performance decisions must be measurable.
13. Reversible decisions should remain flexible.
14. Irreversible decisions require stronger review.
15. Architecture must support future scaling without requiring premature complexity.

---

# 3. Architecture Decision Summary

The major architectural decisions are:

| Area                     | Decision                                               |
| ------------------------ | ------------------------------------------------------ |
| Application architecture | Modular monolith                                       |
| Backend                  | Python + Flask                                         |
| Database                 | PostgreSQL                                             |
| Persistence              | SQLAlchemy + repositories/query services               |
| API                      | REST/HTTP                                              |
| API versioning           | `/api/v1`                                              |
| Domain organization      | Explicit business modules                              |
| Tenant model             | Multi-tenant SaaS                                      |
| Branch model             | Business → Branch                                      |
| Authorization            | Role + Employee Override + Branch Scope + Subscription |
| Device trust             | Separate device trust model                            |
| Offline                  | Trusted-device offline operation                       |
| Synchronization          | Explicit durable synchronization                       |
| Identity                 | UUID-based                                             |
| Transaction identity     | Transaction UUID                                       |
| Cache                    | Redis-compatible                                       |
| Background processing    | Queue + dedicated workers                              |
| Financial consistency    | Strong transactional consistency                       |
| Reporting                | Separate read/report processing                        |
| Historical integrity     | Immutable originals + corrections                      |
| Subscription expiry      | Read-only after expiry                                 |
| Data deletion            | Delayed permanent deletion after 60 days               |
| Deployment               | Simple Linux production deployment                     |
| Scaling                  | Horizontal application scaling                         |
| Microservices            | Not initially required                                 |

---

# 4. Modular Monolith Decision

## 4.1. Decision

FastFood ERP will initially be implemented as a **modular monolith**.

The application is deployed as one primary backend application while maintaining explicit domain and application boundaries.

## 4.2. Why

A modular monolith provides:

* simpler deployment;
* simpler debugging;
* simpler local development;
* simpler transactions;
* lower infrastructure requirements;
* easier consistency management;
* easier offline synchronization implementation;
* lower operational overhead.

The project already has many domains, but domain count alone does not justify microservices.

## 4.3. Trade-off

### Advantages

* strong transactional boundaries;
* fewer network calls;
* simpler database access;
* easier testing;
* easier deployment;
* lower infrastructure cost.

### Disadvantages

* modules share the same deployment unit;
* one application release may affect multiple modules;
* strict module boundaries must be enforced through architecture rather than network isolation.

## 4.4. Decision

The benefits outweigh the disadvantages for the current scale.

Module boundaries must remain strong so that future service extraction remains possible if justified.

---

# 5. PostgreSQL as Authoritative Database

## 5.1. Decision

PostgreSQL is the authoritative transactional database.

## 5.2. Why

FastFood ERP requires:

* ACID transactions;
* row-level locking;
* foreign keys;
* unique constraints;
* strong consistency;
* reliable concurrent inventory updates;
* financial transaction integrity;
* historical data preservation.

PostgreSQL provides these capabilities without introducing unnecessary distributed database complexity.

## 5.3. Trade-off

A relational database requires careful schema design and transaction management.

However, the complexity is appropriate because the product contains:

* money;
* inventory;
* cash;
* employees;
* permissions;
* historical records;
* subscription state.

Correctness is more important than schema flexibility.

---

# 6. REST API Decision

## 6.1. Decision

The primary client API uses REST over HTTPS.

## 6.2. Why

The system has:

* web clients;
* POS clients;
* management interfaces;
* offline synchronization;
* administrative operations.

REST provides a simple and well-understood interface for these clients.

## 6.3. Alternative: GraphQL

GraphQL was not selected as the primary API.

### Reason

The system requires strong command semantics for operations such as:

* accepting orders;
* creating payments;
* closing cash sessions;
* performing corrections;
* synchronizing offline transactions.

Explicit commands are often clearer than highly flexible queries.

GraphQL may be considered for specialized read use cases later.

---

# 7. UUID-Based Identity

## 7.1. Decision

Distributed entities use UUID-based identities.

## 7.2. Why

Offline operation requires entities to be created without an immediate database round trip.

Examples include:

* orders;
* payments;
* cash sessions;
* synchronization events;
* audit events.

UUIDs allow clients and servers to reference the same entity consistently.

## 7.3. Trade-off

UUIDs are larger than simple sequential integers and may have indexing/storage implications.

This is accepted because distributed identity and offline operation are more important than minimal identifier size.

Database indexing must be designed appropriately.

---

# 8. No Separate Client Transaction ID

## 8.1. Decision

The system uses a stable Transaction UUID instead of maintaining a separate Client Transaction ID.

## 8.2. Why

A transaction created offline already has a globally unique identity.

Using one stable identity simplifies:

* synchronization;
* retry handling;
* duplicate detection;
* audit;
* troubleshooting;
* reconciliation.

## 8.3. Trade-off

The system must ensure UUID generation is reliable.

This is considered simpler than maintaining two separate identities for the same transaction.

---

# 9. Offline-First Decision

## 9.1. Decision

Core branch operations must continue when connectivity is temporarily unavailable.

Offline operation is supported only on trusted devices with valid offline authorization.

## 9.2. Why

Restaurant operations cannot always stop because of:

* Internet outages;
* router failures;
* temporary ISP problems;
* branch network interruptions.

POS continuity is therefore a business requirement rather than an optional feature.

## 9.3. Trade-off

Offline operation introduces significant complexity:

* local persistence;
* synchronization;
* conflict handling;
* replay protection;
* clock validation;
* device trust;
* local encryption;
* stale configuration handling.

This complexity is accepted because online-only operation would violate an important business requirement.

---

# 10. Server Authority with Offline Operation

## 10.1. Decision

The server remains authoritative after synchronization.

Offline clients may temporarily execute authorized operations, but synchronization must validate them against current server state.

## 10.2. Why

Allowing clients to permanently override server state could cause:

* duplicate payments;
* negative inventory;
* conflicting cash sessions;
* invalid permissions;
* stale configuration;
* security bypasses.

## 10.3. Trade-off

Some legitimate offline operations may become conflicts after reconnection.

The system therefore uses explicit conflict resolution instead of silently accepting conflicting state.

---

# 11. Strong Consistency for Core Transactions

## 11.1. Decision

The following operations use strong transactional consistency:

* order acceptance;
* inventory deduction;
* payment creation;
* cash session state changes;
* critical corrections;
* inventory adjustments.

## 11.2. Why

These operations directly affect financial or operational truth.

For example:

```text
Order Accepted
    +
Inventory Deducted
```

must succeed or fail together.

## 11.3. Trade-off

Strong transactions may increase lock contention.

The solution is not to weaken correctness.

Instead:

* keep transactions short;
* use appropriate indexes;
* lock only required rows;
* avoid external network calls inside transactions;
* move secondary work to asynchronous processing.

---

# 12. Asynchronous Secondary Processing

## 12.1. Decision

Secondary operations use asynchronous processing where appropriate.

Examples:

* kitchen printing;
* notifications;
* report generation;
* large Excel exports;
* cleanup;
* subscription lifecycle jobs;
* synchronization retries.

## 12.2. Why

POS operations must not wait for slow external or computational work.

## 12.3. Trade-off

Asynchronous processing introduces eventual consistency.

The system therefore distinguishes:

```text
Core Transaction
```

from:

```text
Secondary Processing
```

A failed printer job must not roll back an already valid order transaction.

---

# 13. Outbox-Style Reliability

## 13.1. Decision

Important post-transaction events/jobs should use a durable outbox-style mechanism.

## 13.2. Why

Without an outbox, the following failure is possible:

```text
Database Commit
      ↓
Application Crash
      ↓
Event Never Published
```

The business transaction would succeed while the secondary action disappears.

The outbox prevents this gap.

## 13.3. Trade-off

Outbox processing requires:

* additional storage;
* background workers;
* retries;
* cleanup;
* idempotent consumers.

The reliability benefit justifies this complexity.

---

# 14. Redis as Cache/Queue Support

## 14.1. Decision

Redis-compatible infrastructure may be used for caching and initial queue support.

## 14.2. Why

It is:

* fast;
* widely supported;
* operationally simple;
* suitable for temporary state;
* suitable for rate limiting and queue support.

## 14.3. Critical Rule

Redis must never become the authoritative source for:

* orders;
* payments;
* inventory;
* cash;
* payroll;
* subscription state.

If Redis fails, correctness must remain intact.

---

# 15. No Distributed Event Platform Initially

## 15.1. Decision

A distributed event platform such as Kafka is not required initially.

## 15.2. Why

The initial architecture has:

* one modular backend;
* controlled branch count;
* limited initial infrastructure;
* no requirement for massive event throughput.

An internal outbox + queue architecture is sufficient.

## 15.3. Future Trigger

A distributed event platform may be considered if:

* event throughput becomes a measurable bottleneck;
* independent consumers require independent scaling;
* integration requirements grow significantly;
* operational requirements justify the additional infrastructure.

---

# 16. Domain Module Boundaries

## 16.1. Decision

The backend is divided into explicit business modules.

Examples:

* Order;
* Inventory;
* Payment;
* Cash;
* Menu;
* Employee;
* Reporting;
* Notification;
* Audit;
* Synchronization.

## 16.2. Why

The project has complex cross-domain relationships.

Without boundaries, the codebase could become a tightly coupled collection of CRUD operations.

## 16.3. Trade-off

Explicit boundaries require more design work.

This is accepted because maintainability and correctness are long-term priorities.

---

# 17. No Direct Cross-Domain Database Writes

## 17.1. Decision

A domain module must not directly modify another domain's authoritative state.

For example:

```text
Order Module
    ↓
Inventory Application Use Case
```

is preferred over:

```text
Order Module
    ↓
UPDATE inventory_table
```

## 17.2. Why

Direct cross-domain writes create hidden coupling.

They make:

* authorization;
* auditing;
* validation;
* synchronization;
* future service extraction

more difficult.

---

# 18. Historical Integrity Decision

## 18.1. Decision

Important historical records are not silently overwritten.

Original records remain available.

Corrections are represented separately.

## 18.2. Why

The system handles:

* money;
* inventory;
* cash;
* payroll;
* permissions;
* reports.

Historical reconstruction is therefore important.

## 18.3. Trade-off

The database contains more records because corrections and revisions are retained.

This storage cost is accepted.

---

# 19. Correction Instead of Destructive Editing

## 19.1. Decision

Sensitive finalized data is corrected through controlled correction operations.

Examples:

* payment correction;
* cash correction;
* inventory adjustment;
* report version;
* configuration revision.

## 19.2. Why

Destructive updates make it impossible to determine:

* what happened originally;
* who changed it;
* why it changed;
* when it changed.

## 19.3. Trade-off

Correction workflows require:

* additional UI;
* permissions;
* audit;
* additional database records.

This is intentional.

---

# 20. Subscription Read-Only State

## 20.1. Decision

After subscription expiry, business data remains accessible in read-only mode according to permissions.

Modification operations are blocked.

## 20.2. Why

Immediate deletion would be unsafe and could cause:

* data loss;
* business disruption;
* support problems;
* legal/operational issues.

The system therefore separates:

```text
Access to historical information
```

from:

```text
Permission to modify business state
```

---

# 21. Sixty-Day Data Lifecycle

## 21.1. Decision

If the subscription is not reactivated within 60 days after the exact expiry timestamp, the Business becomes eligible for permanent deletion.

## 21.2. Why

This provides:

* a recovery period;
* user warning time;
* predictable lifecycle behavior;
* operational cleanup.

## 21.3. Trade-off

The platform must retain inactive business data during the retention period.

This increases storage requirements but protects business continuity.

---

# 22. Trusted Device Model

## 22.1. Decision

Device trust is a separate security concept from employee permission.

A trusted device does not automatically grant access to business operations.

## 22.2. Why

The system must distinguish:

```text
Who is the employee?
```

from:

```text
Is this device trusted?
```

and:

```text
What may this employee do?
```

This separation improves security.

---

# 23. Three-Day Offline Grace Period

## 23.1. Decision

The default offline authorization grace period is three days where applicable.

## 23.2. Why

The period provides reasonable continuity during temporary Internet outages while limiting the security lifetime of offline authorization.

## 23.3. Trade-off

A longer period improves operational continuity but increases security exposure.

A shorter period improves security but increases operational dependency on connectivity.

Three days is the selected initial balance.

---

# 24. Permission Model

## 24.1. Decision

Effective authorization is determined by:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
```

## 24.2. Why

The system requires:

* reusable role templates;
* employee-specific exceptions;
* branch-specific permissions;
* tariff-based feature restrictions.

## 24.3. Trade-off

The model is more complex than simple role-based access control.

However, plain RBAC cannot adequately represent the required branch and subscription boundaries.

---

# 25. Manager Delegation Rule

## 25.1. Decision

A Manager cannot grant permissions beyond the authority available to that Manager.

## 25.2. Why

Otherwise, permission delegation could become a privilege escalation path.

Authorization must therefore consider both:

* what the Manager has;
* what the Manager is allowed to delegate.

---

# 26. Branch Isolation

## 26.1. Decision

Branch is a first-class operational boundary.

## 26.2. Why

Each branch has:

* inventory;
* cash sessions;
* employees;
* POS operations;
* offline devices;
* operational configuration.

Cross-branch access must therefore be explicit.

## 26.3. Trade-off

Branch-aware authorization and filtering increase query and permission complexity.

The benefit is strong tenant and branch isolation.

---

# 27. No Branch Inventory Transfer Initially

## 27.1. Decision

Branch-to-branch inventory transfer is outside the current scope.

## 27.2. Why

Transfer introduces additional complexity:

* source branch;
* destination branch;
* transfer lifecycle;
* in-transit inventory;
* synchronization;
* conflict handling;
* authorization.

It is intentionally excluded until a clear business requirement exists.

---

# 28. Order and Inventory Atomicity

## 28.1. Decision

Order acceptance and inventory deduction are one core transaction.

## 28.2. Why

The system must prevent:

```text
Order Accepted
+
Inventory Not Deducted
```

or:

```text
Inventory Deducted
+
Order Not Accepted
```

## 28.3. Trade-off

The transaction may hold inventory rows briefly.

This is accepted because correctness is more important than maximum theoretical concurrency.

---

# 29. Kitchen Printing as Secondary Processing

## 29.1. Decision

Kitchen printing is secondary to the core order transaction.

## 29.2. Why

Printer failures must not corrupt business state.

The order can remain valid even if:

* printer is offline;
* printer connection fails;
* paper is unavailable;
* print job fails.

The print operation is retried independently.

---

# 30. Payment and Order Separation

## 30.1. Decision

Payment state is separate from operational order lifecycle.

Payment does not automatically change:

```text
Accepted
Preparing
Ready
Served
```

## 30.2. Why

Operational fulfillment and financial settlement are different concerns.

This allows:

* payment before serving;
* partial payment;
* mixed payment;
* debt;
* refunds;
* operational status changes.

---

# 31. Cancellation and Refund Separation

## 31.1. Decision

Cancellation and refund are separate operations.

## 31.2. Why

Cancellation concerns operational order state.

Refund concerns financial reversal.

Combining them would make business behavior ambiguous.

---

# 32. No Automatic Inventory Return on Refund

## 32.1. Decision

Refund does not automatically return inventory.

## 32.2. Why

Financial reversal does not necessarily mean that physical goods are returned to stock.

For example:

* food may already be served;
* product may be discarded;
* product may be damaged.

Inventory adjustment must therefore be explicit.

---

# 33. Price Snapshot Decision

## 33.1. Decision

Open orders preserve the applicable price snapshot.

Future price changes do not silently modify existing orders.

## 33.2. Why

Historical financial correctness requires the order to retain the price applicable when the order was created/configured.

---

# 34. Configuration Effective Boundaries

## 34.1. Decision

Important configuration changes become effective at defined operational boundaries.

For example:

* recipe changes;
* price changes;
* Set changes.

These may become effective from the next Cash Session.

## 34.2. Why

Changing configuration in the middle of an active session can create inconsistent transactions.

The boundary provides deterministic behavior.

---

# 35. Report Versioning

## 35.1. Decision

Reports are versioned when relevant underlying data changes.

Previous versions remain immutable.

## 35.2. Why

Business reports may need to explain why a value changed after a correction.

A mutable report would destroy that history.

## 35.3. Trade-off

Storage and report-generation complexity increase.

This is accepted because financial and operational reporting requires historical integrity.

---

# 36. Report Generation Isolation

## 36.1. Decision

Heavy report generation is isolated from POS processing.

## 36.2. Why

A large report must not cause:

* slow order entry;
* delayed payment processing;
* inventory latency;
* POS timeout.

Reports use controlled read workloads and background workers when necessary.

---

# 37. No Arbitrary SQL Reporting

## 37.1. Decision

Normal users cannot execute arbitrary SQL for reporting.

## 37.2. Why

Arbitrary SQL creates:

* security risks;
* tenant isolation risks;
* performance risks;
* unpredictable queries;
* operational instability.

Reports use controlled definitions and queries.

---

# 38. XLSX as Current Export Format

## 38.1. Decision

Excel `.xlsx` is the supported business export format.

## 38.2. Why

The business requirements explicitly require Excel export.

Other formats are not required by the current scope.

---

# 39. Background Worker Isolation

## 39.1. Decision

Background workers are separated from interactive request processing.

## 39.2. Why

Background operations may be CPU-, memory-, or I/O-intensive.

They must not consume resources required by POS.

---

# 40. Resource Protection

The architecture uses:

* bounded worker concurrency;
* queue priorities;
* connection limits;
* request limits;
* pagination;
* bounded synchronization batches;
* background processing for large workloads.

This is preferred over simply increasing server hardware.

---

# 41. Bounded Synchronization Batches

## 41.1. Decision

Synchronization uses bounded batches, typically around:

```text
50–100 operations
```

subject to implementation and payload limits.

## 41.2. Why

Large synchronization batches increase:

* request size;
* memory usage;
* transaction duration;
* retry cost;
* failure scope.

Bounded batches provide safer recovery.

---

# 42. Partial Batch Success

## 42.1. Decision

A synchronization batch may partially succeed.

Each operation receives an explicit result.

Possible states include:

* Synced;
* Retrying;
* Conflict;
* Failed.

## 42.2. Why

One invalid operation should not force valid operations to be repeated.

---

# 43. Conflict Resolution

## 43.1. Decision

Synchronization conflicts are explicit records requiring authorized resolution when automatic resolution is unsafe.

## 43.2. Why

Silent conflict resolution can corrupt:

* inventory;
* payments;
* cash;
* order state;
* configuration.

The system therefore prefers explicit conflict state over silent overwrite.

---

# 44. Automatic Conflict Resolution Policy

Automatic resolution is allowed only when the business meaning is deterministic and safe.

Examples:

* duplicate request with the same transaction UUID;
* repeated acknowledgement;
* already-applied idempotent operation.

Financial or operational contradictions require explicit resolution.

---

# 45. No Silent Last-Write-Wins for Critical Data

## 45.1. Decision

Critical business state does not use generic last-write-wins conflict resolution.

## 45.2. Why

Last-write-wins can silently destroy valid information.

It is acceptable for selected non-critical metadata only if explicitly defined.

---

# 46. Technology Simplicity Decision

The architecture intentionally avoids unnecessary distributed infrastructure.

## 46.1. Why

The initial system is expected to operate at a controlled scale.

Complex infrastructure increases:

* deployment risk;
* maintenance burden;
* debugging difficulty;
* operational cost;
* security surface.

Simple infrastructure is therefore preferred until actual requirements prove otherwise.

---

# 47. Horizontal Application Scaling

## 47.1. Decision

The application should be stateless enough to support horizontal scaling.

Conceptually:

```text
Load Balancer
      |
 +----+----+
 |         |
App 1    App 2
 |         |
 +----+----+
      |
 PostgreSQL
```

## 47.2. Why

This provides a scaling path without requiring microservices.

---

# 48. Database Scaling Strategy

The initial strategy is:

1. optimize queries;
2. optimize indexes;
3. control transactions;
4. control connection pools;
5. optimize reports;
6. introduce read models where justified;
7. scale PostgreSQL vertically;
8. introduce replication where justified;
9. partition/archive large datasets where justified.

Premature database sharding is not required.

---

# 49. Cache-Aside Decision

The preferred caching strategy is cache-aside.

Conceptually:

```text
Application
    ↓
Cache lookup
    ↓
Miss
    ↓
PostgreSQL
    ↓
Cache
```

The database remains authoritative.

Cache invalidation must be explicit for configuration changes.

---

# 50. Cache Safety Decision

Core transactional state should not depend on cache availability.

The system must be able to fall back to PostgreSQL where practical.

This may temporarily reduce performance but must not change business correctness.

---

# 51. Security vs Performance Trade-off

Security controls must be applied according to risk.

High-value operations receive stronger controls:

* permissions;
* device trust;
* audit;
* server validation;
* correction authorization.

Routine low-risk operations should not require unnecessary repeated verification.

The goal is:

```text
Strong Security
+
Low Operational Friction
```

---

# 52. Audit vs Performance Trade-off

Important state-changing operations must be auditable.

Routine reads do not normally require full audit logging.

This avoids excessive audit volume while preserving accountability.

Sensitive administrative access may receive additional auditing.

---

# 53. Encryption vs Performance Trade-off

Sensitive data should be protected appropriately.

However, encryption must not be applied indiscriminately in a way that makes POS operations unnecessarily slow.

Encryption strategy should distinguish:

* data requiring encryption;
* data requiring hashing;
* public/non-sensitive data;
* data that only requires transport protection.

---

# 54. Offline Security vs Availability Trade-off

Offline operation creates a security boundary.

Longer offline authorization improves availability but increases risk.

Shorter authorization improves security but increases dependence on the network.

The selected initial balance is a bounded offline authorization period with cryptographic protection and server revalidation after reconnect.

---

# 55. Historical Integrity vs Storage Cost

Keeping:

* original records;
* corrections;
* report versions;
* configuration versions;
* audit records

requires more storage.

This cost is intentionally accepted.

The system prioritizes historical reconstruction over minimal database size.

---

# 56. Immediate Consistency vs Performance

Not every operation requires synchronous completion.

The architecture distinguishes:

### Strongly Consistent

* order acceptance;
* inventory deduction;
* payment;
* cash session state;
* critical correction.

### Eventually Consistent

* notification;
* printing;
* report generation;
* analytics;
* cleanup;
* background synchronization processing.

This prevents unnecessary blocking of POS workflows.

---

# 57. Operational Simplicity vs Future Scale

The architecture intentionally avoids overengineering for future scale.

Instead:

```text
Simple Initial Architecture
          ↓
Measured Growth
          ↓
Targeted Scaling
          ↓
Selective Technology Evolution
```

Future scalability remains possible without implementing future infrastructure prematurely.

---

# 58. Decision Reversibility

Architectural decisions are classified conceptually as:

### Easy to Reverse

* cache implementation;
* logging library;
* metrics library;
* frontend component library;
* some worker implementation details.

### Moderately Difficult to Reverse

* API conventions;
* ORM conventions;
* queue model;
* configuration model.

### Difficult to Reverse

* database model;
* tenant model;
* identity model;
* synchronization protocol;
* historical integrity model;
* core transaction boundaries.

Difficult decisions require stronger validation before implementation.

---

# 59. Architecture Decision Governance

A significant architecture change must answer:

1. What problem exists?
2. Why does the current architecture fail?
3. What alternatives were considered?
4. What are the security implications?
5. What are the performance implications?
6. What are the operational implications?
7. What migration is required?
8. What rollback is possible?
9. What existing documents are affected?
10. Is an ADR required?

---

# 60. Rejected Architecture Patterns

The following patterns are currently rejected:

### 60.1. Full Microservices from the Beginning

Rejected because infrastructure and distributed consistency costs are unnecessary at the current scale.

### 60.2. MongoDB as Primary Transaction Database

Rejected because the core system heavily depends on relational transactions, constraints, and financial consistency.

### 60.3. Client-Authoritative Offline State

Rejected because it creates security and consistency risks.

### 60.4. Last-Write-Wins for Critical Transactions

Rejected because it can silently lose business information.

### 60.5. Cache-Only Transaction State

Rejected because cache failure could cause data loss.

### 60.6. Queue as Permanent Storage

Rejected because queues are processing infrastructure, not authoritative business storage.

### 60.7. Direct Cross-Module Database Writes

Rejected because they create hidden coupling.

### 60.8. Automatic Destructive Corrections

Rejected because historical integrity must be preserved.

### 60.9. Arbitrary SQL Reporting

Rejected because of security and performance risks.

### 60.10. Kubernetes from the Beginning

Rejected because initial operational requirements do not justify the complexity.

---

# 61. Architecture Trade-off Matrix

| Decision              | Main Benefit           | Main Cost                    | Selected Because                |
| --------------------- | ---------------------- | ---------------------------- | ------------------------------- |
| Modular monolith      | Simplicity             | Shared deployment            | Current scale                   |
| PostgreSQL            | Strong consistency     | Relational schema complexity | Financial/inventory correctness |
| REST                  | Simplicity             | Less flexible than GraphQL   | Clear API commands              |
| UUIDs                 | Offline identity       | Larger identifiers           | Distributed identity            |
| Offline-first         | Operational continuity | Sync complexity              | Business requirement            |
| Server authority      | Security/correctness   | Conflict handling            | Data integrity                  |
| Strong transactions   | Correctness            | Locking                      | Financial/inventory safety      |
| Async workers         | POS performance        | Eventual consistency         | Operational responsiveness      |
| Redis cache           | Speed                  | Invalidation                 | Performance                     |
| Outbox                | Reliability            | Additional persistence       | Event delivery reliability      |
| Report versioning     | Historical integrity   | Storage                      | Reporting correctness           |
| Corrections           | Auditability           | More workflow                | Historical integrity            |
| 60-day retention      | Recovery               | Storage                      | Business safety                 |
| Modular domains       | Maintainability        | Design effort                | Long-term complexity            |
| Horizontal scaling    | Growth path            | Operational complexity       | Future scale                    |
| Simple infrastructure | Low operational burden | Less built-in distribution   | Initial requirements            |

---

# 62. Decision Consistency Rules

The following rules must always be preserved when introducing new technology:

1. New technology must not bypass authorization.
2. New technology must not bypass tenant isolation.
3. New technology must not bypass branch isolation.
4. New technology must not bypass subscription entitlement.
5. New technology must not bypass audit requirements.
6. New technology must not bypass domain validation.
7. New technology must not silently modify historical records.
8. New technology must not make offline synchronization non-deterministic.
9. New technology must not make critical operations non-idempotent.
10. New technology must not create an unbounded resource dependency.
11. New technology must have a clear failure mode.
12. New technology must have a recovery strategy.
13. New technology must have an observability strategy.
14. New technology must have a testing strategy.
15. New technology must have a rollback strategy where applicable.

---

# 63. Architecture Invariants

The following invariants are mandatory.

1. The architecture remains a modular monolith initially.
2. PostgreSQL remains authoritative.
3. Critical transactions remain atomic.
4. Financial operations remain idempotent.
5. Inventory operations remain concurrency-safe.
6. Offline transactions retain stable identity.
7. Synchronization remains explicit.
8. Synchronization remains idempotent.
9. Conflicts remain explicit when automatic resolution is unsafe.
10. Critical state does not use generic last-write-wins.
11. Domain boundaries remain explicit.
12. Cross-domain writes use defined application contracts.
13. Authentication remains separate from authorization.
14. Device trust remains separate from permissions.
15. Subscription entitlement remains separate from permissions.
16. Branch scope remains enforced.
17. Business isolation remains enforced.
18. Historical originals remain preserved.
19. Corrections remain separately represented.
20. Report versions remain immutable.
21. Configuration versions remain traceable.
22. Heavy background work remains isolated from POS.
23. Queue failure cannot corrupt committed transactions.
24. Cache failure cannot corrupt committed transactions.
25. Offline authorization remains bounded.
26. Offline authorization remains cryptographically protected.
27. Server revalidates synchronized operations.
28. Technology does not become the source of business rules.
29. Infrastructure complexity requires justification.
30. Major architectural changes require review.

---

# 64. Architecture Decision Lifecycle

Each major decision should follow:

```text
Problem
   ↓
Context
   ↓
Alternatives
   ↓
Evaluation
   ↓
Decision
   ↓
Trade-offs
   ↓
Implementation
   ↓
Validation
   ↓
Monitoring
   ↓
Reassessment if required
```

Architecture is not considered permanently correct merely because it was accepted.

Actual system behavior and operational data may justify future changes.

---

# 65. ADR Relationship

This document provides the consolidated architectural view.

Dedicated ADRs should be used for decisions with independent lifecycle requirements.

Potential ADR subjects include:

* backend technology;
* database technology;
* modular monolith;
* offline synchronization;
* trusted devices;
* report versioning;
* background processing;
* deployment strategy;
* future service extraction.

The exact ADR numbering must follow the repository's existing ADR policy.

---

# 66. Implementation Guidance

Before implementation of a major component, developers should verify:

```text
Business Requirement
        ↓
System Requirement
        ↓
Domain Responsibility
        ↓
Architecture Boundary
        ↓
Technology Choice
        ↓
Implementation
        ↓
Tests
```

A technology must never be selected first and then used to force the business model into an unsuitable shape.

---

# 67. Completion Criteria

Architecture Decisions and Trade-offs is considered complete when:

* major architecture choices are documented;
* alternatives are identified;
* important trade-offs are explicit;
* rejected approaches are documented;
* critical decisions have clear reasoning;
* offline architecture decisions are documented;
* consistency decisions are documented;
* historical integrity decisions are documented;
* scaling decisions are documented;
* security/performance trade-offs are documented;
* technology decisions are connected to architecture;
* future decision governance is defined.

---

# 68. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Domain Analysis

* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/18_Configuration_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/04_Backend_Architecture.md`
* `docs/04_Architecture/06_API_Architecture.md`
* `docs/04_Architecture/07_Database_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/11_Deployment_Architecture.md`
* `docs/04_Architecture/12_Event_and_Message_Architecture.md`
* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/14_Caching_Architecture.md`
* `docs/04_Architecture/15_Observability_and_Operations_Architecture.md`
* `docs/04_Architecture/16_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`
* `docs/04_Architecture/18_Technology_Selection.md`

---

# 69. Next Document

The next Architecture document is:

```text
docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md
```

It should consolidate the architectural guardrails that must remain true during implementation, code review, testing, deployment, and future architectural changes.

