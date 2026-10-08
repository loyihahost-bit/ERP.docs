# System Analysis

**Document ID:** SA-README
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/01_Business_Analysis/README.md`

## 1. Purpose

System Analysis defines how the FastFood ERP system must behave in order to satisfy the business requirements established during Business Analysis.

Business Analysis defines:

> What does the business need?

System Analysis defines:

> What must the system do to satisfy those requirements?

This layer converts approved business requirements into:

* system behavior;
* application flows;
* entity states;
* state transitions;
* validation rules;
* authorization rules;
* concurrency rules;
* transaction boundaries;
* synchronization behavior;
* conflict resolution;
* error handling;
* recovery behavior;
* system-wide invariants.

System Analysis is the primary input for the following documentation layers:

* Domain Analysis;
* Architecture;
* Database;
* Backend;
* Frontend;
* API;
* Security;
* Testing;
* Deployment;
* Operations.

---

## 2. Scope

The System Analysis layer covers the following areas:

1. System context and boundaries
2. Application structure and navigation
3. Tenant, business and branch context
4. Authentication and authorization
5. Employees, roles and permissions
6. Trusted devices and security context
7. POS and order management
8. Order lifecycle and statuses
9. Table and waiter management
10. Kitchen and printing
11. Payment system
12. Debt and payment allocation
13. Discounts, refunds and corrections
14. Cash register and cash sessions
15. Shift handover
16. Inventory transactions
17. Products, recipes and Sets
18. Menu, pricing and configuration
19. Attendance and payroll
20. Reports and report versioning
21. Notifications and alerts
22. Audit and change history
23. Offline operation
24. Synchronization and conflict resolution
25. Subscription and entitlement
26. Data lifecycle and deletion
27. System-wide consistency and concurrency
28. Background jobs and recovery
29. Error handling and failure recovery
30. System invariants and consolidated rules

---

## 3. Relationship With Business Analysis

System Analysis does not replace Business Analysis.

Business requirements remain the source of business intent.

System Analysis defines the system behavior required to implement that intent.

For example:

**Business requirement:**

> Inventory must not become negative.

**System behavior:**

```text
Order Modification
        ↓
Stock Validation
        ↓
Sufficient Stock?
   ┌────┴────┐
   │         │
  Yes        No
   │         │
   ↓         ↓
Apply      Reject
Change     Entire
           Modification
```

The System Analysis document therefore does not redefine the business requirement. It defines the exact system behavior required to enforce it.

---

## 4. Analysis Principles

### 4.1. Business Rules Are Preserved

System Analysis must preserve all accepted Business Analysis decisions.

A system-level decision may refine an existing business requirement, but it must not silently contradict it.

If a technical decision changes an approved business rule, the affected Business Analysis document and relevant ADR must also be updated.

### 4.2. No Silent Data Loss

Important business data must not be silently deleted or overwritten.

Where correction is required, the system should create a new correction, revision or financial operation while preserving the original historical state.

This principle applies especially to:

* payments;
* refunds;
* cash discrepancies;
* inventory adjustments;
* reports;
* audit records;
* configuration changes;
* synchronization conflicts.

### 4.3. Server Authority

When the system is online, the server and authoritative database represent the current authoritative system state.

Offline operations are temporarily created on trusted devices and must be validated by the server during synchronization.

Server validation must not silently discard valid offline business transactions.

### 4.4. Offline Continuity

Temporary network failure must not unnecessarily stop permitted branch operations.

Offline operation is available only when all required conditions are satisfied, including:

* trusted device;
* valid offline authorization;
* active employee;
* valid permissions;
* valid branch scope;
* valid subscription entitlement;
* valid offline authorization period.

Offline capability must never become a mechanism for bypassing security or business rules.

### 4.5. Idempotency

Retrying the same business operation must not create duplicate business effects.

Important operations use UUID-based identity and idempotency protection.

This applies to:

* orders;
* payments;
* inventory transactions;
* synchronization events;
* background jobs;
* report generation;
* notifications;
* other retryable operations where duplicate execution could create an incorrect result.

### 4.6. Atomic Core Operations

Business-critical state changes must be atomic where they represent one logical operation.

For example, accepting an order and deducting its inventory must belong to the same core transaction.

```text
Order Accept
     ↓
Stock Validation
     ↓
Order State Change
     ↓
Inventory Deduction
```

If the core transaction fails, the related state changes must be rolled back.

### 4.7. Secondary Services Must Not Break Core Operations

Failure of a secondary service must not normally roll back a successfully completed core business transaction.

For example:

```text
Core Transaction
     │
     ├── Order + Inventory → SUCCESS
     │
     └── Kitchen Printing
              │
              ├── Printed
              └── Failed → Retry
```

Printer, notification and similar secondary failures are represented separately and retried according to their own recovery rules.

### 4.8. Business Correctness Over UI Convenience

Frontend convenience must never override business correctness.

Important validation must be performed by the backend/server, including:

* authorization;
* branch scope;
* subscription entitlement;
* inventory availability;
* payment rules;
* cash session state;
* entity state;
* concurrency constraints.

The frontend may provide early validation for usability, but it is not the authoritative enforcement layer.

---

## 5. System Context

The main system hierarchy is:

```text
Platform
    │
    └── Business / Tenant
           │
           ├── Branches
           │
           ├── Employees
           │
           ├── Roles / Permissions
           │
           ├── Devices
           │
           ├── Menu / Products / Recipes
           │
           ├── Inventory
           │
           ├── POS / Orders
           │
           ├── Cash Registers / Cash Sessions
           │
           ├── Payments
           │
           ├── Reports
           │
           ├── Notifications
           │
           └── Audit / History
```

The Business/Tenant boundary must be preserved across all system layers.

Tenant isolation applies to:

* API requests;
* database queries;
* background jobs;
* reports;
* exports;
* notifications;
* audit records;
* offline storage;
* synchronization;
* configuration.

No business user may access another business's operational data.

---

## 6. Operational Context

Most operational transactions are associated with a specific business and branch.

Where applicable, the system must also preserve:

* Employee;
* Device;
* Cash Register;
* Cash Session;
* Order;
* Payment;
* Transaction;
* Event.

This allows the system to answer:

* Who performed the operation?
* Which business was affected?
* Which branch was affected?
* Which device was used?
* Which cash register was involved?
* Which cash session was active?
* Which entity was changed?
* Which transaction caused the change?
* When did it occur?
* Was it performed online, offline or during synchronization?

---

## 7. Identity Model

The system uses UUID-based identities for important entities and transactions.

Important identifiers include:

* Business UUID
* Branch UUID
* Employee UUID
* Device UUID
* Cash Register UUID
* Cash Session UUID
* Order UUID
* Payment UUID
* Transaction UUID
* Event UUID
* Report UUID
* Notification UUID
* Audit Event UUID

Customer-facing identifiers may exist separately from internal UUIDs.

For example, an order may have a short customer-facing order number while its permanent system identity remains the Order UUID.

Customer-facing numbers must not be used as the primary identity of business transactions.

---

## 8. State and Lifecycle Model

Important entities must have explicit lifecycle states.

A valid state transition requires the relevant system checks to pass.

General model:

```text
Current State
      ↓
Validation
      ↓
Allowed?
   ┌──┴──┐
  Yes    No
   │      │
   ↓      ↓
New     Rejection
State
```

Validation may include:

* employee status;
* permission;
* branch scope;
* subscription entitlement;
* current entity state;
* inventory state;
* payment state;
* cash session state;
* concurrency/version;
* business rules.

Invalid state transitions must be rejected.

---

## 9. Authorization Model

Effective authorization is determined by the combined system context.

```text
Employee
    ↓
Role Permissions
    ↓
Employee Overrides
    ↓
Branch Scope
    ↓
Subscription Entitlement
    ↓
Current Entity State
    ↓
Business Rule
    ↓
Operation Allowed / Rejected
```

A trusted device does not grant permissions.

A device only establishes whether the device is authorized to participate in the relevant operational context.

An employee cannot grant permissions beyond their own authority.

---

## 10. Concurrency Model

The system uses different concurrency mechanisms according to the risk of the operation.

### 10.1. Critical Resources

Critical resources use authoritative server-side transaction control, locking, version checks or equivalent mechanisms.

Examples include:

* inventory stock;
* cash sessions;
* payment amounts;
* critical order transitions;
* unique session creation;
* other resources where concurrent changes could violate business integrity.

### 10.2. Non-Critical Resources

Where strict locking is unnecessary, optimistic concurrency and version validation may be used.

The objective is to prevent stale client state from silently overwriting newer authoritative state.

---

## 11. Transaction Boundaries

A logical business operation should be represented by a clearly defined transaction boundary.

For example:

```text
Order Acceptance
    │
    ├── Validate Order
    ├── Validate Inventory
    ├── Change Order State
    └── Deduct Inventory
```

These core operations must succeed or fail together.

Secondary operations may execute outside the core transaction:

```text
Core Transaction
      │
      ├── Kitchen Print
      ├── Notification
      └── Background Processing
```

Failure of a secondary operation must not incorrectly reverse a completed core transaction.

---

## 12. Error Model

The system uses the following main error categories:

1. Validation Error
2. Authorization Error
3. Conflict
4. Business Rule Violation
5. Temporary Infrastructure Error
6. Permanent Failure

Users should receive understandable business-level error messages.

Technical details such as:

* stack traces;
* database errors;
* internal service information;
* infrastructure details

must remain in technical logs and must not normally be exposed to operational users.

---

## 13. Retry and Recovery

Retry is permitted only when the operation is safe to retry or protected by idempotency.

General recovery model:

```text
Failure
   │
   ├── Rollback
   ├── Retry
   ├── Idempotency
   ├── Queue
   ├── Conflict Resolution
   └── Audit
```

Background operations must support:

* retry;
* retry limits;
* failure states;
* structured logging;
* recovery after worker failure.

A failed operation must not be represented as successful merely because the original request was accepted.

---

## 14. Offline and Synchronization Model

Offline operations are created locally on trusted devices.

A synchronization event contains sufficient context to identify and validate the original operation.

Typical event context includes:

* Event UUID;
* Transaction UUID;
* Entity UUID;
* Employee UUID;
* Device UUID;
* Branch UUID;
* Cash Session UUID where applicable;
* client timestamp;
* source;
* event payload.

General synchronization lifecycle:

```text
Pending
   ↓
Syncing
   ↓
Server Validation
   │
   ├── Synced
   ├── Retrying
   ├── Conflict
   └── Failed
```

Synchronization must preserve the original transaction identity.

A successful synchronization response must not cause the client to create a second business transaction.

---

## 15. Conflict Resolution

Conflicts must be explicit.

The system must not silently use last-write-wins for critical business data when that could cause data loss or financial/inventory inconsistency.

A conflict should contain:

* original operation;
* conflicting server state;
* affected entity;
* conflict reason;
* detected time;
* resolution status.

Resolution must be performed by an authorized user or system process according to the relevant business rule.

The resolution itself is a separate auditable event.

---

## 16. Reporting Model

Reports are generated for a defined:

* business;
* branch scope;
* report definition;
* period;
* data state.

Report generation uses a consistent transactional data snapshot.

A report version is immutable.

A new version is created when relevant underlying data changes.

For example:

```text
Report
   │
   ├── Version 1
   │
   ├── Version 2
   │
   └── Version 3
```

Previous versions remain available to authorized users.

Excel export represents the selected report version rather than recalculating an unrelated live state during download.

---

## 17. Audit Model

Important state-changing operations must create audit records.

Audit context includes, where applicable:

* Event UUID;
* Business UUID;
* Branch UUID;
* Actor;
* Device UUID;
* Cash Session UUID;
* Entity type;
* Entity UUID;
* Transaction UUID;
* timestamp;
* old state;
* new state;
* reason;
* result/status;
* source.

Sources may include:

* Online;
* Offline;
* Sync;
* System.

Audit records are immutable.

Corrections create new events and reference the original event where required.

---

## 18. Subscription and Entitlement

Subscription entitlement is a server-enforced system constraint.

The frontend may hide unavailable functionality, but backend validation remains authoritative.

Important modifying operations must verify:

```text
Employee
   ↓
Permission
   ↓
Branch Scope
   ↓
Subscription Entitlement
   ↓
Business Rule
   ↓
Operation
```

When a subscription expires:

* modifying operations are blocked;
* existing data remains accessible according to read-only rules;
* history remains accessible;
* permitted Excel exports remain available;
* offline operation cannot bypass the entitlement state.

Subscription downgrade must not destroy existing data.

---

## 19. Data Lifecycle

Business lifecycle:

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

The deletion countdown begins at the exact subscription expiration timestamp.

Current business rule:

**60 calendar days after subscription expiration.**

If the subscription is reactivated before permanent deletion begins, existing business data and configuration remain available.

Deletion must be:

* idempotent;
* auditable;
* retryable;
* safe against partial failure.

---

## 20. Background Processing

Background processing must be isolated from latency-sensitive POS operations.

Typical background operations include:

* heavy report generation;
* large Excel exports;
* synchronization;
* notification delivery;
* subscription lifecycle processing;
* deletion jobs;
* retryable infrastructure tasks.

Background jobs must not unnecessarily block:

* order creation;
* order acceptance;
* payment;
* cash operations;
* normal POS navigation.

---

## 21. Performance Principle

The system may contain a large number of features, but daily operational workflows must remain simple and fast.

The highest performance priority is given to:

* POS;
* order creation;
* order acceptance;
* payment;
* cash session operations;
* shift handover;
* inventory operations.

Security, audit and synchronization mechanisms must be designed so that they do not introduce unnecessary latency into normal POS operations.

---

## 22. System Invariants

The following invariants apply across the System Analysis layer:

1. Business data must remain tenant-isolated.
2. Branch scope must be enforced where applicable.
3. Permissions must be enforced server-side.
4. Trusted devices do not grant permissions.
5. Subscription entitlement must be enforced server-side.
6. Offline authorization must not bypass security or subscription restrictions.
7. Inventory must never become negative.
8. Critical inventory operations must be atomic.
9. Duplicate transactions must not create duplicate business effects.
10. Closed cash sessions must not become active sessions again.
11. Historical data must not be silently overwritten.
12. Corrections must preserve the original historical state.
13. Audit records must be immutable.
14. Report versions must be immutable.
15. Payment corrections must preserve payment history.
16. Refunds must remain separate financial operations.
17. Synchronization conflicts must not be silently overwritten.
18. Secondary service failure must not normally roll back a successful core transaction.
19. Background processing must not unnecessarily block POS operations.
20. Server restart must not corrupt committed business transactions.
21. Retryable operations must be protected by idempotency.
22. Failed background jobs must remain observable and recoverable.
23. Data deletion must support safe retry after partial failure.
24. Business correctness has priority over UI convenience.
25. Historical integrity has priority over silent last-write-wins behavior.
26. Security must not be bypassed through offline operation.
27. Core financial and inventory operations must remain auditable.
28. Important business actions must preserve actor and operational context.

---

## 23. Document Structure

The System Analysis documentation is organized as follows:

| Document                                        | Area                                            |
| ----------------------------------------------- | ----------------------------------------------- |
| `01_System_Context_and_Boundaries.md`           | System boundaries and external/internal context |
| `02_Application_Structure_and_Navigation.md`    | Application structure and navigation behavior   |
| `03_Tenant_Business_and_Branch_Context.md`      | Tenant, business and branch context             |
| `04_Authentication_and_Authorization.md`        | Authentication and authorization behavior       |
| `05_Employees_Roles_and_Permissions.md`         | Employee and permission behavior                |
| `06_Device_Trust_and_Security_Context.md`       | Trusted devices and operational security        |
| `07_POS_and_Order_System.md`                    | POS and order behavior                          |
| `08_Order_Lifecycle_and_Statuses.md`            | Order states and transitions                    |
| `09_Table_and_Waiter_Management.md`             | Tables, visits and waiter assignments           |
| `10_Kitchen_and_Printing.md`                    | Kitchen tickets and printer behavior            |
| `11_Payment_System.md`                          | Payments and payment lifecycle                  |
| `12_Debt_and_Payment_Allocation.md`             | Debt and debt repayment                         |
| `13_Discounts_Refunds_and_Corrections.md`       | Financial corrections                           |
| `14_Cash_Register_and_Cash_Session.md`          | Cash register and session behavior              |
| `15_Shift_Handover.md`                          | Cashier/session handover                        |
| `16_Inventory_Transaction_System.md`            | Inventory transactions                          |
| `17_Products_Recipes_and_Sets.md`               | Product, recipe and Set behavior                |
| `18_Menu_Pricing_and_Configuration.md`          | Menu and pricing behavior                       |
| `19_Attendance_and_Payroll.md`                  | Attendance and payroll                          |
| `20_Reports_and_Report_Versioning.md`           | Reports and immutable versions                  |
| `21_Notifications_and_Alerts.md`                | Notification lifecycle                          |
| `22_Audit_and_History.md`                       | Audit and historical records                    |
| `23_Offline_Operation.md`                       | Offline operation                               |
| `24_Synchronization_and_Conflict_Resolution.md` | Synchronization behavior                        |
| `25_Subscription_and_Entitlement.md`            | Subscription enforcement                        |
| `26_Data_Lifecycle_and_Deletion.md`             | Data lifecycle                                  |
| `27_System_Wide_Consistency_and_Concurrency.md` | Consistency and concurrency                     |
| `28_Background_Jobs_and_Recovery.md`            | Background processing                           |
| `29_Error_Handling_and_Failure_Recovery.md`     | Error and recovery behavior                     |
| `30_System_Invariants_and_Rules.md`             | Consolidated system invariants                  |

---

## 24. Documentation Dependency

The overall documentation dependency is:

```text
Business Analysis
       ↓
System Analysis
       ↓
Domain Analysis
       ↓
Architecture
       ↓
Database
       ↓
Backend
       ↓
Frontend
       ↓
API
       ↓
Security
       ↓
Testing
       ↓
Deployment / Operations
```

Lower-level documentation must not introduce behavior that contradicts approved System Analysis requirements.

If a later technical decision changes a system requirement, the affected System Analysis document must be updated and the relevant ADR must be created or updated.

---

## 25. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/README.md`
* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### Future Analysis Layers

* `docs/03_Domain_Analysis/`
* `docs/04_Architecture/`
* `docs/05_Database/`
* `docs/06_Backend/`
* `docs/07_Frontend/`
* `docs/09_API/`
* `docs/11_Security/`
* `docs/12_Testing/`

---

## 26. Status

**System Analysis Interview:** Completed through Q227.

**System Analysis Documentation:** In progress.

**Current Document:** `README.md`

**Next Document:** `01_System_Context_and_Boundaries.md`

