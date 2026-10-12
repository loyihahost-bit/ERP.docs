# Deferred Capabilities and Architecture Reserve

**Document ID:** FUT-02
**Status:** Accepted
**Version:** 1.0
**Section:** 15_Future
**Last Updated:** 2026-10-09

## 1. Purpose

This document defines how deferred capabilities and architecture reserves are recorded and managed for the FastFood ERP platform.

Its purpose is to preserve reasonable future options without requiring the current system to implement, deploy, operate, or pay for capabilities that have not been approved.

The document identifies:

* Capabilities intentionally deferred from the current product scope.
* Existing architectural boundaries that should remain compatible with potential future extensions.
* Minimal design considerations that can prevent unnecessary future blockers.
* Decisions that must be revisited before a deferred capability is implemented.

This document does not authorize implementation of any deferred capability.

## 2. Core Principle

**Do not implement a future capability merely to make its eventual implementation easier.**

The current system MUST satisfy its approved requirements with the simplest architecture that meets business, security, reliability, performance, and operational needs.

Future compatibility SHOULD be preserved when it can be achieved through low-cost, justified decisions that do not compromise the current system.

A possible future feature is not sufficient justification for introducing:

* A new service.
* A new database or database cluster.
* A message broker.
* A distributed transaction mechanism.
* A new deployment environment.
* A new external integration.
* An abstraction without a current use case.
* Unnecessary configuration or permission complexity.
* Unmeasured performance optimization.
* Additional production infrastructure.

Any such addition requires a present, documented justification and the normal approval process.

## 3. Relationship with Current Requirements

The current product baseline remains authoritative.

This document MUST NOT modify requirements defined in:

* Business Analysis.
* System Analysis.
* Domain Analysis.
* Architecture.
* Database.
* Backend.
* Frontend.
* AI.
* API.
* Deployment.
* Security.
* Testing.
* Development.
* Operations.

If a deferred capability becomes necessary, the relevant current documents MUST be updated through an approved change process before the capability is treated as a current requirement.

The Future section is a planning and evolution reference, not an alternative requirements specification.

## 4. Capability Classification

Each deferred capability SHOULD use one of the following classifications.

### 4.1 Deferred

The capability is outside the current approved scope.

No implementation is required unless a future decision explicitly authorizes it.

### 4.2 Deferred — Business Validation Required

The business need, expected value, user workflow, or commercial model requires further validation.

Technical feasibility alone is insufficient to approve implementation.

### 4.3 Deferred — Architecture Investigation Required

The capability may affect domain boundaries, persistence, consistency, security, infrastructure, or deployment.

The relevant design must be evaluated before implementation.

### 4.4 Architecture Reserve

A limited design consideration is recorded to avoid an unnecessary future blocker.

An architecture reserve does not mean that a feature, service, interface, table, or integration must be implemented now.

### 4.5 Reconsideration Triggered

A documented event or measurable condition justifies reviewing the capability again.

A trigger initiates evaluation; it does not automatically authorize implementation.

## 5. Deferred Capability Register

The following register identifies planned future topics. These entries describe possibilities rather than commitments.

| Capability                                  | Current position                                  | Reconsideration focus                                                        |
| ------------------------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------------- |
| Multiple cash registers per branch          | One register per branch remains the current model | Cash ownership, shift handover, reconciliation, and device coordination      |
| More than 10 branches per business          | Initial scope remains up to 10 branches           | Measured capacity, subscription policy, tenant isolation, and administration |
| Online ordering                             | Deferred                                          | Order intake, menu availability, payment flow, and duplicate prevention      |
| Customer CRM and loyalty                    | Deferred                                          | Customer identity, privacy, consent, retention, and cross-branch rules       |
| Advanced delivery management                | Deferred                                          | Dispatch, delivery assignment, status transitions, and responsibility        |
| Customer mobile application                 | Deferred                                          | API boundaries, authentication, client compatibility, and support costs      |
| Telegram and other messaging channels       | Deferred                                          | Delivery guarantees, retries, duplicate messages, and data exposure          |
| Advanced AI and intelligent automation      | Deferred                                          | Data quality, measurable value, resource cost, fallback, and human oversight |
| Read replicas and multi-region architecture | Deferred                                          | Measured bottlenecks, consistency, recovery, and operational complexity      |

The detailed evolution documents for these capabilities are maintained separately under `doc/15_Future/`.

The register MUST be updated when the approved scope or the status of a capability changes.

## 6. Architecture Reserve Principles

Architecture reserves MUST be selective and evidence-based.

### 6.1 Preserve Clear Domain Boundaries

Current domain responsibilities SHOULD remain explicit.

Future features should be evaluated against the existing domain model rather than assuming that every future feature needs its own service or module.

A new domain boundary may be introduced when the business rules, ownership, consistency requirements, or operational benefits justify it.

### 6.2 Keep Business Rules Authoritative

Core business rules MUST remain enforced by the authoritative backend and domain logic.

Future clients, integrations, and AI features MUST NOT be treated as trusted authorities for:

* Order acceptance.
* Payment status.
* Inventory availability.
* Cash-register state.
* Employee permissions.
* Subscription entitlement.
* Tenant or branch access.

### 6.3 Preserve Tenant and Branch Isolation

All future capabilities MUST preserve tenant isolation and applicable branch-level access restrictions.

A future feature MUST NOT assume that an authenticated user can access every branch or business.

Cross-branch operations require explicit authorization and an approved business rule.

### 6.4 Prefer Explicit Configuration

When current requirements already support configurable behavior, new capabilities SHOULD use the existing configuration model where appropriate.

Do not introduce a generalized configuration engine solely to support hypothetical future requirements.

Configuration changes MUST NOT bypass authorization, validation, or audit requirements.

### 6.5 Avoid Premature Distribution

The current architecture SHOULD NOT be split into additional services solely because the product may grow.

Distributed architecture introduces network failures, deployment coordination, observability requirements, security boundaries, and data consistency challenges.

Service separation requires a documented benefit that justifies those costs.

### 6.6 Preserve Controlled Extensibility

Where a current requirement already needs variation, such as branch-specific permissions or configurable product behavior, the implementation SHOULD avoid unnecessary hardcoding that directly contradicts that requirement.

This does not require every component to be plugin-based, dynamically extensible, or independently deployable.

## 7. Minimal Data and API Considerations

Future compatibility MUST NOT be used as a reason to create speculative database schemas or APIs.

The following principles apply:

* Store data required by approved current workflows.
* Preserve existing tenant and branch ownership rules.
* Use stable identifiers where required by current data-integrity rules.
* Avoid relying on display labels as permanent identifiers.
* Keep business state transitions explicit.
* Validate ownership and permissions on the server.
* Version or evolve public API contracts when compatibility requirements justify it.
* Use migration procedures for approved schema changes.
* Avoid adding unused fields, tables, endpoints, or status values without a documented present requirement.

If a future capability requires a new data model, that model MUST be designed when the capability is approved and sufficiently understood.

A speculative data field is not automatically a useful architecture reserve.

## 8. Future Client and Channel Compatibility

Future web, mobile, online-ordering, or messaging clients may use the platform's approved interfaces.

The current implementation SHOULD avoid unnecessary coupling between presentation-specific code and authoritative business rules.

However:

* A mobile application is not required by this document.
* An online ordering API is not required by this document.
* A public integration platform is not required by this document.
* Additional authentication providers are not required by this document.
* A customer identity service is not required by this document.

When a future channel is approved, its authentication, authorization, rate limits, idempotency, compatibility, privacy, and failure handling MUST be evaluated explicitly.

## 9. Data and Integration Reserves

Future integrations may require new data exchange, events, callbacks, or external services.

Until a specific integration is approved:

* Do not create unused integration credentials.
* Do not expose internal endpoints for hypothetical partners.
* Do not collect customer information solely for an unapproved future feature.
* Do not introduce a message broker solely because asynchronous integrations may be useful later.
* Do not promise exactly-once external delivery without a defined and verifiable mechanism.
* Do not allow external systems to bypass the authoritative business workflow.

When an integration is approved, define ownership, authentication, authorization, validation, retries, idempotency, auditability, and failure recovery before production use.

## 10. Performance and Scaling Reserves

The platform MUST be designed to meet its current approved workload and reasonable operational expectations.

It MUST NOT assume that all future scaling mechanisms are required from the beginning.

Potential future mechanisms include:

* Read replicas.
* Additional worker capacity.
* Separate AI execution resources.
* Independent service scaling.
* Advanced caching.
* Multi-region deployment.
* Additional regional storage.
* Partitioning or sharding.

Each mechanism requires evidence that it addresses an actual or sufficiently established requirement.

Before introducing a scaling mechanism, evaluate:

1. The measured bottleneck.
2. The expected workload and growth.
3. The effect on data consistency.
4. The effect on failure recovery.
5. The operational and monitoring burden.
6. The recurring cost.
7. The security implications.
8. The migration and rollback strategy.

Increasing infrastructure capacity MUST NOT substitute for fixing an identified database, query, synchronization, or application bottleneck.

## 11. Security and Privacy Constraints

Future extensibility MUST NOT weaken current security requirements.

In particular:

* Tenant and branch isolation remains mandatory.
* Server-side authorization remains authoritative.
* Secrets MUST NOT be embedded in client applications.
* Sensitive information MUST NOT be added to logs without an approved need and safeguards.
* New customer data collection requires a justified purpose and appropriate controls.
* Data retention and deletion requirements MUST be evaluated before new data categories are introduced.
* External integrations MUST be treated as separate security boundaries.
* Future AI features MUST follow approved data-access and execution controls.

A future capability cannot justify postponing a security requirement that already applies to the current system.

## 12. Offline Operation and Synchronization

Offline branch operation is an established current requirement.

Future capabilities MUST be evaluated for their effect on offline workflows, synchronization, and transaction integrity.

New capabilities MUST NOT silently introduce:

* Loss of locally accepted transactions.
* Duplicate order or payment processing.
* Uncontrolled inventory changes.
* Conflicting cash-register state.
* Unauthorized synchronization.
* A dependency on continuous internet connectivity for existing offline workflows.

If a future capability cannot work offline, its limitations and user-visible behavior MUST be explicitly defined before approval.

Existing offline functionality MUST NOT be weakened merely to simplify a future integration.

## 13. Subscription and Commercial Constraints

The current subscription model remains authoritative.

Future capabilities may eventually become plan-dependent, but this document does not introduce new tariffs, entitlements, or pricing rules.

Before approving a plan-dependent capability, evaluate:

* Entitlement ownership and enforcement.
* Business and branch scope.
* Employee and role restrictions.
* Behavior after expiration.
* Reactivation behavior.
* Data retention and deletion implications.
* Auditability.
* Performance impact of entitlement checks.

Subscription restrictions MUST NOT be implemented only as frontend visibility rules.

Existing subscription expiration, read-only behavior, and approved data-lifecycle requirements MUST remain intact unless explicitly changed through the current requirements process.

## 14. Reconsideration Triggers

A deferred capability SHOULD be reconsidered when evidence indicates a meaningful change in need or feasibility.

Potential triggers include:

* Repeated customer requests supported by a clear business case.
* A documented limitation in the current operating model.
* Measured capacity constraints.
* An approved commercial requirement.
* A security or regulatory requirement.
* A verified reduction in implementation or operational cost.
* A dependency becoming available or obsolete.
* An incident demonstrating that a current boundary is insufficient.

Triggers MUST be documented where practical.

No trigger automatically authorizes implementation. The normal evaluation and approval workflow still applies.

## 15. Required Evaluation Before Implementation

Before a deferred capability becomes an implementation initiative, the responsible team MUST establish:

1. The business problem and expected value.
2. The affected users and workflows.
3. The current requirements that may change.
4. The affected domains, APIs, data models, and integrations.
5. The security and privacy impact.
6. The consistency and transaction-integrity requirements.
7. The offline behavior and synchronization implications.
8. The subscription and permission implications.
9. The deployment, monitoring, backup, and recovery requirements.
10. The expected resource and operational costs.
11. The migration and compatibility requirements.
12. The acceptance criteria and verification plan.
13. The approval authority and decision record.

Not every capability requires the same depth of investigation. The level of analysis MUST be proportionate to the impact and risk.

## 16. Relationship with Other Future Documents

This document provides common rules for the following capability documents:

* `01_Future_Roadmap_and_Evolution_Framework.md`
* `03_Multi_Cash_Register_Evolution.md`
* `04_Scale_Beyond_Initial_Branch_Limits.md`
* `05_Online_Ordering_Evolution.md`
* `06_Customer_CRM_Evolution.md`
* `07_Advanced_Delivery_Management.md`
* `08_Mobile_Customer_Application.md`
* `09_Messaging_and_Channel_Integrations.md`
* `10_Advanced_AI_and_Intelligent_Automation.md`
* `11_Advanced_Scaling_and_Multi_Region_Architecture.md`
* `12_Future_Architecture_Guardrails.md`

The documents MUST remain consistent with FUT-01 and the authoritative current documentation.

Where a capability-specific document describes a possible design, that design MUST be treated as a proposal until approved through the appropriate process.

## 17. Mandatory Invariants

1. Deferred capabilities MUST NOT be treated as current requirements.
2. Future documentation MUST NOT independently authorize implementation.
3. Current approved requirements remain authoritative.
4. Architecture reserves MUST have a justified purpose.
5. Speculative infrastructure MUST NOT be introduced without current justification.
6. Unused services MUST NOT be created solely for possible future growth.
7. Speculative database tables MUST NOT be added without an approved requirement.
8. Unused API endpoints MUST NOT be exposed for hypothetical clients.
9. Existing tenant isolation MUST remain mandatory.
10. Existing branch-level authorization MUST remain mandatory.
11. Server-side authorization MUST remain authoritative.
12. Core business rules MUST NOT depend on future client applications.
13. Core POS operations MUST NOT depend on optional future services.
14. Existing offline workflows MUST remain protected.
15. Transaction integrity MUST NOT be weakened for future extensibility.
16. Future scaling decisions MUST consider measured workload.
17. Additional infrastructure MUST have a documented benefit.
18. New dependencies MUST have an explicit operational owner.
19. New integrations MUST be evaluated as security boundaries.
20. New data collection MUST have a justified purpose.
21. New data categories MUST be evaluated for retention and deletion.
22. Future customer features MUST consider privacy and access controls.
23. Future AI MUST NOT override authoritative business state without an explicitly approved, controlled workflow.
24. Future AI failures MUST NOT compromise core ERP transaction integrity.
25. Subscription entitlements MUST NOT rely only on frontend controls.
26. Future plan-dependent capabilities MUST preserve approved subscription lifecycle behavior.
27. Future architecture proposals MUST identify their affected current documents.
28. Conflicts with current requirements MUST be resolved explicitly.
29. Approved changes MUST follow the established change-control process.
30. Database changes MUST include appropriate migration and verification plans.
31. API changes MUST evaluate compatibility with existing clients.
32. External delivery mechanisms MUST account for failures and duplicate processing.
33. Retry policies MUST NOT cause duplicate business transactions.
34. Multi-register evolution MUST evaluate cash reconciliation and ownership.
35. Branch-scale expansion MUST evaluate capacity and isolation.
36. Multi-region evolution MUST evaluate consistency and recovery.
37. New background processing MUST include idempotency and failure handling.
38. New caching MUST NOT bypass authorization or serve stale data in ways that violate business rules.
39. Security requirements MUST NOT be deferred when they already apply to current functionality.
40. Operational readiness MUST be evaluated before production release.
41. Monitoring requirements MUST be defined for approved production capabilities.
42. Backup and recovery implications MUST be evaluated for new persistent data.
43. Cost optimization MUST NOT undermine security or data integrity.
44. A reconsideration trigger MUST NOT equal implementation approval.
45. Rejected proposals SHOULD retain a traceable decision where material.
46. Superseded decisions MUST be clearly marked.
47. Capability-specific documents MUST remain consistent with FUT-01.
48. Implemented capabilities MUST be reflected in authoritative current documentation.
49. Documentation references MUST be validated before being considered complete.
50. The Future section MUST preserve options without imposing unapproved complexity on the current architecture.

## 18. Acceptance Criteria

This document is acceptable when:

* Deferred capabilities are clearly distinguished from current requirements.
* Architecture reserves are limited to justified design considerations.
* Current business and technical invariants are protected.
* Reconsideration and approval requirements are explicit.
* Security, offline operation, subscription behavior, and transaction integrity are addressed.
* Future capability documents can reference this document without duplicating its common rules.
* No future capability is implicitly approved by appearing in this register.

## 19. Maintenance

Review this document when:

* The current architecture or approved requirements change.
* The Future roadmap governance process changes.
* A deferred capability is approved for implementation.
* New evidence changes the validity of an architecture reserve.
* A documented reserve becomes unnecessary or introduces avoidable complexity.

Updates MUST preserve the distinction between future planning and current implementation requirements.

