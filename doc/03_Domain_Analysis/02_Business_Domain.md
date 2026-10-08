# Business Domain

**Document ID:** DA-02
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Business domain represents the restaurant or restaurant network that uses FastFood ERP.

A Business is the primary tenant boundary of the system.

This document defines:

* Business ownership;
* Business identity;
* Business lifecycle;
* Business configuration;
* Business-level settings;
* Business relationships;
* Business boundaries;
* Business-level invariants.

This document does not define database tables or API endpoints.

---

# 2. Business as the Tenant Boundary

Every customer organization is represented by one Business.

The Business is the root owner of tenant data.

```text id="g6eh2r"
Platform
   │
   └── Business
         │
         ├── Branches
         ├── Employees
         ├── Products
         ├── Recipes
         ├── Menu
         ├── Orders
         ├── Inventory
         ├── Cash
         ├── Payments
         ├── Payroll
         ├── Reports
         ├── Notifications
         └── Audit History
```

A Business must never access another Business's operational data.

---

# 3. Business Identity

A Business must have a stable unique identity.

The identity must be represented by a UUID.

The Business UUID must remain stable for the entire Business lifetime.

The UUID must not change because of:

* subscription renewal;
* tariff change;
* branch creation;
* owner change;
* configuration change;
* synchronization;
* migration;
* report generation.

The Business UUID is part of the security and tenant-isolation model.

---

# 4. Business Core Information

The Business domain should contain the minimum information required to identify and operate the tenant.

Conceptually:

```text id="i3kj6p"
Business
├── UUID
├── Name
├── Status
├── Contact Information
├── Business Settings
├── Created At
├── Updated At
└── Lifecycle Metadata
```

Additional information may be introduced later when justified by business requirements.

The domain should avoid storing unrelated operational data directly on the Business entity.

---

# 5. Business Ownership

A Business may have multiple Owners.

Owner access is represented through the Identity and Access domain.

Therefore:

```text id="4e7f2v"
Business
   │
   ├── Owner A
   ├── Owner B
   └── Owner C
```

The Business domain owns the concept that the organization exists.

The Identity and Access domain owns the relationship between employees and their authorization.

Owner count may be limited by the active Subscription entitlement.

A subscription downgrade must not silently delete existing Owners.

It may prevent creation of additional Owners until the Business becomes compliant with the new limit.

---

# 6. Business Lifecycle

The Business lifecycle must be distinguishable from the Subscription lifecycle.

A Business may exist while its subscription is:

* Active;
* Expired;
* Within deletion window;
* Deleting.

The Business itself should not be treated as deleted merely because the subscription expired.

Conceptually:

```text id="4lvj4c"
Business Created
      ↓
Operational
      ↓
Subscription Expired
      ↓
Read-Only
      ↓
Deletion Eligible
      ↓
Deleting
      ↓
Deleted
```

The exact lifecycle transition is coordinated with the Subscription and Data Lifecycle domains.

---

# 7. Business Status

Business status represents the operational lifecycle of the tenant.

The status must be distinguishable from:

* employee status;
* branch status;
* subscription status;
* device status;
* order status.

The domain must not overload one status field to represent all of these concepts.

---

# 8. Business Settings

Business-level settings represent configuration shared across the Business.

Examples may include:

* business name;
* default operational preferences;
* notification thresholds;
* allowed configuration defaults;
* payroll defaults;
* report preferences;
* other business-level configurable defaults.

Settings must not contain branch-specific state when that state belongs to the Branch domain.

---

# 9. Configuration Ownership

Business-level configuration is owned by the Business domain or the appropriate specialized configuration domain.

Examples:

```text
Business-level:
    notification thresholds
    business defaults
    global operational preferences

Branch-level:
    branch configuration
    branch availability
    branch-specific operational settings
```

The domain model must clearly distinguish global configuration from branch overrides.

---

# 10. Business and Branch Relationship

A Business may contain multiple Branches.

```text id="r8w6o4"
Business
   ├── Branch 1
   ├── Branch 2
   ├── Branch 3
   └── ...
```

Each Branch belongs to exactly one Business.

A Branch cannot be shared between Businesses.

The initial subscription model supports up to 10 branches depending on the selected tariff.

The architecture must not hard-code the number 10 into the domain model.

The actual limit comes from Subscription entitlement.

---

# 11. Business and Employees

Employees belong to a Business.

An employee may be assigned to:

* one Branch;
* multiple Branches;
* different permission scopes per Branch.

The Business domain establishes the tenant relationship.

The Identity and Access domain determines the employee's effective permissions.

Therefore:

```text id="7y8n7r"
Business
   │
   └── Employee
         ├── Identity
         ├── Roles
         ├── Overrides
         └── Branch Scopes
```

An employee must not belong to multiple Businesses through the same Business employee identity.

---

# 12. Business and Products

Products are Business-owned concepts.

A Business may define:

* products;
* product categories;
* recipes;
* sets;
* prices;
* menu configuration.

Branches may use Business-owned products according to branch menu configuration.

The Business domain owns the tenant relationship, while Product and Recipe owns the product behavior.

---

# 13. Business and Inventory

Inventory is operationally associated with Branches.

Therefore:

```text id="3zrvf7"
Business
   │
   └── Branch
         │
         └── Inventory
```

The Business owns the overall tenant context.

The Inventory domain owns stock state and stock movements.

The Business domain must not directly manipulate inventory quantities.

---

# 14. Business and Orders

Orders belong to a Business through their Branch.

Conceptually:

```text id="k7q7l4"
Business
   ↓
Branch
   ↓
Order
```

Every Order must contain sufficient tenant and branch context to enforce isolation.

At minimum, the operational context must be reconstructable through:

* Business;
* Branch;
* Employee;
* Device;
* Cash Session where applicable.

An order must never become detached from its Business.

---

# 15. Business and Cash

Cash operations are branch-scoped.

```text id="ayl8r7"
Business
   ↓
Branch
   ↓
Cash Register
   ↓
Cash Session
```

The Business owns the tenant boundary.

The Cash domain owns:

* register state;
* session state;
* cash totals;
* differences;
* handover;
* corrections.

---

# 16. Business and Payments

Payments belong to the Business through the related order and operational context.

Payment records must preserve enough context to prevent cross-business access.

The Payment domain owns payment state.

The Business domain only establishes tenant ownership.

---

# 17. Business and Reports

Reports are generated within a Business scope.

A report may be:

* Business-wide;
* Branch-scoped;
* employee-related;
* operationally filtered.

The Reporting domain owns report versions.

The Business domain owns the tenant boundary.

A report must never combine data from multiple Businesses.

---

# 18. Business and Audit

Every tenant-scoped audit event must identify its Business.

The Audit domain owns the audit event.

The Business domain provides the tenant context.

Audit queries must always enforce Business isolation.

Platform-level events may exist outside Business scope, such as:

* Business creation;
* tariff creation;
* platform administration.

---

# 19. Business and Notifications

Notifications may be Business-scoped or Branch-scoped.

Examples:

```text
Business-scoped:
    Subscription ending
    Employee limit reached
    Business-level configuration issue

Branch-scoped:
    Low stock
    Cash discrepancy
    Branch loss
    Branch inventory variance
```

The Notification domain owns notification state and delivery.

The Business domain owns the tenant boundary.

---

# 20. Business and Subscription

The relationship is:

```text id="bdx6ml"
Business
   │
   └── Subscription
          │
          ├── Tariff
          ├── Entitlements
          ├── Limits
          └── Lifecycle
```

Subscription does not redefine Business identity.

Subscription controls what the Business is currently entitled to use.

---

# 21. Subscription Expiration

When the subscription expires:

1. Business identity remains valid.
2. Existing data remains available.
3. Read operations remain available according to permissions.
4. Allowed report/history access remains available.
5. Allowed Excel exports remain available.
6. Modifying operations are blocked according to entitlement state.
7. Existing operational state is preserved.
8. Offline authorization cannot bypass the entitlement.
9. The deletion countdown begins from the exact `subscription_expired_at`.

The Business domain remains intact until the Data Lifecycle domain completes deletion.

---

# 22. Business Reactivation

If the Business subscription is reactivated within the allowed lifecycle period:

1. The existing Business UUID remains unchanged.
2. Existing Branch UUIDs remain unchanged.
3. Existing Employee UUIDs remain unchanged.
4. Existing Orders remain unchanged.
5. Existing Payments remain unchanged.
6. Existing Inventory history remains unchanged.
7. Existing Reports remain unchanged.
8. Existing Audit history remains unchanged.
9. Existing configuration history remains unchanged.
10. Normal modifying operations become available according to the new entitlement.

Reactivation is not treated as creation of a new Business.

---

# 23. Business Deletion

Business deletion is controlled by the Data Lifecycle domain.

Deletion must be:

* deliberate;
* background processed;
* observable;
* idempotent;
* retryable;
* tenant-isolated.

A partially completed deletion must not be reported as successfully completed.

After deletion, stale offline operations must not recreate or resurrect the Business.

---

# 24. Business-Level Data Isolation

Every tenant-owned operation must enforce Business scope.

This applies to:

* API requests;
* database queries;
* reports;
* exports;
* background jobs;
* notifications;
* synchronization;
* offline authorization;
* audit access;
* conflict resolution.

Business UUID must therefore be treated as a security boundary, not merely as a relational field.

---

# 25. Business-Level Authorization

Business ownership alone does not mean an employee can access all Business data.

Access requires:

```text id="8tyz0r"
Valid Employee Identity
        +
Required Permission
        +
Valid Branch Scope
        +
Active/Allowed Subscription Entitlement
        +
Valid Device Trust Where Required
```

Owner has broad Business-level authority according to the permission model.

Managers and other employees receive only their configured permissions.

---

# 26. Business-Level Configuration Changes

Important Business-level configuration changes must preserve:

* previous value;
* new value;
* effective time;
* actor;
* reason where required;
* configuration version;
* audit reference.

Historical operations must continue to reference their applicable historical configuration.

---

# 27. Business-Level Concurrency

Business-level changes may occur concurrently.

Examples:

* two Owners editing configuration;
* subscription update during configuration changes;
* employee limit downgrade while employee creation is occurring;
* Business deactivation while offline events are synchronizing.

The system must use explicit concurrency control.

A stale operation must not silently overwrite a newer valid state.

---

# 28. Business-Level Idempotency

Operations that may be retried must be idempotent where applicable.

Examples:

* Business creation;
* subscription transition;
* configuration update;
* offline synchronization;
* deletion jobs;
* report generation.

Repeated processing must not create duplicate Business entities or duplicate lifecycle effects.

---

# 29. Business and Offline Operation

Offline devices operate on behalf of a specific Business.

Offline authorization must contain enough context to establish:

* Business;
* Branch;
* Employee;
* Device;
* permission state;
* subscription entitlement;
* authorization validity period.

An offline device must never switch its Business context without an authorized online process.

---

# 30. Business Context During Synchronization

Every synchronized event must preserve its original Business UUID.

The server must validate:

1. Business exists;
2. Business is not deleted;
3. Event belongs to the Business;
4. Employee belongs to the Business;
5. Device belongs to the Business;
6. Branch belongs to the Business;
7. Event references belong to the same Business;
8. authorization remains valid;
9. event has not already been processed.

Cross-business synchronization must always be rejected.

---

# 31. Business and Historical Reconstruction

A Business's historical state should be reconstructable from:

* domain state;
* immutable transactions;
* audit history;
* report versions;
* configuration versions;
* correction records;
* lifecycle records.

Current Business settings must not be used to reinterpret historical transactions incorrectly.

---

# 32. Business Domain Invariants

The following invariants apply:

### Identity

1. Every Business has one stable UUID.
2. Business UUID never changes during the Business lifecycle.
3. Two Businesses cannot share the same identity.

### Tenant Isolation

4. Every tenant-owned resource belongs to exactly one Business.
5. Cross-business reads are forbidden.
6. Cross-business writes are forbidden.
7. Cross-business synchronization is forbidden.
8. Cross-business report generation is forbidden.

### Branch Ownership

9. Every Branch belongs to exactly one Business.
10. A Branch cannot move between Businesses through an ordinary operational action.
11. Branch-scoped data must remain inside its Business.

### Employee Ownership

12. Every employee identity belongs to one Business.
13. An employee cannot use one Business's identity to access another Business.
14. Employee permissions cannot escape Business scope.

### Subscription

15. Subscription entitlement belongs to the Business.
16. Subscription expiry does not delete Business data immediately.
17. Read-only state does not change Business identity.
18. Reactivation does not create a new Business.
19. Deletion eligibility is determined from the Business lifecycle and subscription lifecycle.

### Historical Integrity

20. Business-level historical records must remain reconstructable.
21. Configuration changes must not rewrite historical transactions.
22. Deletion lifecycle must not silently report incomplete deletion as complete.

### Offline and Synchronization

23. Offline events retain their original Business UUID.
24. Offline authorization cannot switch Business scope.
25. Synchronization must validate Business ownership.
26. Deleted Businesses cannot be resurrected by stale offline events.

### Security

27. Business UUID is a tenant-isolation boundary.
28. Frontend-provided Business scope is never trusted without server validation.
29. Business ownership does not automatically grant every permission.
30. Platform-level administration remains separate from ordinary Business operations.

---

# 33. Domain Services

The Business domain may require application/domain services for operations such as:

* Business creation;
* Business configuration update;
* Business lifecycle transition;
* Business reactivation validation;
* Business deletion coordination.

These services must not bypass Subscription, Identity, Audit, or Data Lifecycle rules.

---

# 34. Domain Events

Potential Business domain events include:

```text
BusinessCreated
BusinessConfigurationChanged
BusinessStatusChanged
BusinessReadOnlyEntered
BusinessReactivated
BusinessDeletionEligible
BusinessDeletionStarted
BusinessDeleted
```

Events represent domain facts.

They must not be treated as substitutes for authoritative Business state.

---

# 35. Aggregate Boundary

The Business entity is the root of tenant identity but must not become a giant aggregate containing every Business-owned object.

The following must remain separate aggregates/domains:

* Branch;
* Order;
* Cash Session;
* Inventory;
* Product;
* Recipe;
* Payment;
* Payroll;
* Report;
* Notification;
* Audit.

This prevents large Business-level transactions and protects POS performance.

---

# 36. Performance Considerations

The Business domain must not require loading the entire Business object graph for ordinary operations.

For example, accepting an Order should not require loading:

* every Branch;
* every Employee;
* every Product;
* every Report;
* complete Audit history.

Only the context required for the operation should be loaded and validated.

---

# 37. Security Considerations

Business scope must be enforced at multiple layers:

```text
Request
  ↓
Authentication
  ↓
Business Context
  ↓
Authorization
  ↓
Branch Scope
  ↓
Domain Rules
  ↓
Data Access
```

No single client-side check is sufficient.

---

# 38. Completion Criteria

The Business domain is considered defined when:

* Business is established as the primary tenant boundary;
* Business identity is stable;
* ownership is defined;
* Business lifecycle is defined;
* subscription relationship is defined;
* branch relationship is defined;
* employee relationship is defined;
* tenant isolation is defined;
* offline/synchronization behavior is defined;
* historical integrity is defined;
* deletion behavior is defined;
* aggregate boundaries prevent Business from becoming an oversized aggregate.

---

## Related Documents

### Previous

* `docs/03_Domain_Analysis/README.md`
* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Data_Lifecycle_Domain.md`

### Next Phase

* `docs/04_Architecture/`

