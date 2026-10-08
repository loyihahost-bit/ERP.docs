# Table and Waiter Data Model

**Document ID:** DB-14
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for:

* halls;
* tables;
* table availability;
* table visits;
* Dine-in Order relationships;
* primary Waiter assignment;
* assisting Waiter assignment;
* table occupancy;
* table grouping;
* cashier and waiter context;
* historical table state;
* concurrency;
* offline operation;
* synchronization;
* historical integrity.

The model must support fast POS table operations without allowing table state to become inconsistent with active Orders.

---

## 2. Design Principles

The Table and Waiter model follows these principles:

1. Tables belong to a Branch.
2. Halls belong to a Branch.
3. A Table cannot cross Branch boundaries.
4. Table identity is UUID-based.
5. Table codes/numbers are Branch-scoped.
6. Table occupancy is derived from active operational Orders.
7. Paid historical Orders do not keep a Table occupied.
8. Table Visits group Orders belonging to one customer visit.
9. A new visit starts a new Table Visit after the previous visit is released.
10. Orders retain their historical Table context.
11. Primary Waiter and assisting Waiter are separate concepts.
12. The Primary Waiter does not automatically change when another Waiter assists.
13. Waiter assignments are permission-controlled.
14. Historical waiter attribution must remain available.
15. Concurrent table operations must be protected.
16. Offline table operations must synchronize explicitly.
17. Table configuration changes must not rewrite historical Orders.
18. Table deletion is replaced by deactivation/archive where history exists.
19. The model must remain compatible with future table/layout features.
20. Table state must never be used to bypass Order authorization or payment rules.

---

## 3. Branch Ownership

Every Hall and Table belongs to exactly one Branch.

Conceptually:

```text
Business
   ↓
Branch
   ↓
Hall
   ↓
Table
```

Ownership must satisfy:

```text id="7c8b2m"
hall.business_id = branch.business_id
table.branch_id = hall.branch_id
```

Cross-Business and cross-Branch references are forbidden.

---

## 4. Hall Model

A Hall represents a logical dining area within a Branch.

Examples:

* Main Hall;
* VIP Hall;
* Terrace;
* Second Floor.

A Hall is not a financial or inventory entity.

Suggested fields:

```text id="k9r6ax"
Hall
----
id
business_id
branch_id
name
code
status
display_order
created_at
updated_at
```

---

## 5. Hall Lifecycle

A Hall may use:

```text id="3o2mwy"
ACTIVE
INACTIVE
ARCHIVED
```

A Hall should not be physically deleted when historical Tables or Orders depend on it.

Inactive Halls should not be used for new Table operations.

---

## 6. Hall Code

Hall codes may be used for administrative identification.

Default uniqueness:

```text id="p7m1dj"
UNIQUE (branch_id, code)
```

The code is not the permanent identity.

The Hall UUID remains authoritative.

---

## 7. Table Model

A Table represents a physical or logical customer seating location.

Suggested fields:

```text id="1q5v4n"
Table
-----
id
business_id
branch_id
hall_id
table_number
name
capacity
status
display_order
created_at
updated_at
```

Not every field is required to be exposed to the POS user.

---

## 8. Table Identity

Every Table has a UUID.

The UUID:

* is globally unique;
* remains stable;
* is never reused;
* is used by Orders and Table Visits;
* remains unchanged if the display number changes.

The visible Table Number is not the permanent identity.

---

## 9. Table Number

A Table Number is Branch-scoped.

Recommended uniqueness:

```text id="m9i5u4"
UNIQUE (branch_id, table_number)
```

The same number may exist in another Branch.

Example:

```text id="qv6l8x"
Branch A → Table 01
Branch B → Table 01
```

This is valid.

---

## 10. Table Capacity

Table capacity represents the configured seating capacity.

Conceptually:

```text id="8u0d3v"
capacity > 0
```

Capacity is informational for the current system.

The system does not automatically prevent an Order from exceeding configured capacity unless a future business rule explicitly requires it.

---

## 11. Table Status

Table configuration state may be:

```text id="a2r1kf"
ACTIVE
INACTIVE
ARCHIVED
```

Operational occupancy is separate.

Therefore:

```text id="8e1j9m"
configuration_status
```

must not be confused with:

```text id="6x3f0w"
occupancy_status
```

---

## 12. Occupancy Status

Occupancy may be represented as:

```text id="t9o7wx"
AVAILABLE
BUSY
```

The operational state is derived from active Orders/Table Visit state.

The database must not allow arbitrary manual occupancy values to contradict active Order state.

---

## 13. Busy Table Rule

A Table is Busy when it has at least one active operational Order belonging to the current Table Visit.

Conceptually:

```text id="q1z9f5"
Open Dine-in Order
        ↓
Table = BUSY
```

When no active operational Order remains:

```text id="v4m3ks"
Table = AVAILABLE
```

---

## 14. Paid Order and Occupancy

A fully paid historical Order does not by itself keep a Table Busy.

Example:

```text id="a9j5xq"
Order
Status = SERVED
Payment = PAID
        ↓
Does not keep Table occupied
```

The Table Visit may be closed according to the operational flow.

---

## 15. Table Visit

A Table Visit groups Orders belonging to one customer/table occupancy period.

Conceptually:

```text id="z6m8q3"
Table
  ↓
Table Visit
  ├── Order A
  ├── Order B
  └── Order C
```

This allows multiple operational Orders to belong to one customer visit while retaining separate Order identities.

---

## 16. Table Visit Identity

Each Table Visit has a UUID.

The UUID is:

* globally unique;
* permanent;
* never reused;
* independent from the Table Number;
* independent from Order UUID.

---

## 17. Table Visit Lifecycle

Suggested lifecycle:

```text id="x0b4rj"
OPEN
   ↓
CLOSING
   ↓
CLOSED
```

The exact operational transition may be simplified in implementation.

A closed Table Visit must not receive new Orders.

---

## 18. Starting a New Visit

When a Table is Available and a new Dine-in customer begins a session:

```text id="q5c9rm"
Create Table Visit
        ↓
Assign first Dine-in Order
        ↓
Table becomes Busy
```

A new visit must not reuse the previous Table Visit UUID.

---

## 19. New Visit After Release

After a Table is released:

```text id="1qk4bd"
Previous Visit
    CLOSED

New customer
    ↓
New Visit UUID
```

Historical Orders remain linked to the previous Visit.

---

## 20. Order Relationship

An Order may reference:

```text id="e4j7mw"
table_id
table_visit_id
```

For Dine-in Orders, the Table and Table Visit must belong to the same Branch.

Takeaway Orders normally do not require either reference.

---

## 21. Table Visit and Order Scope

The database must enforce:

```text id="9m8j2f"
table_visit.branch_id = order.branch_id
table_visit.table_id = order.table_id
```

Cross-Table and cross-Branch Order assignment is invalid.

---

## 22. Multiple Orders in One Visit

A Table Visit may contain multiple Orders.

Example:

```text id="w4z8b0"
Table Visit 100
 ├── Order 001
 ├── Order 002
 └── Order 003
```

This supports additional product tickets after the original Order has been accepted.

Each Order remains independently identifiable.

---

## 23. Main Bill Context

Multiple Orders in the same Table Visit may belong to one customer-facing bill context.

The database should support grouping without merging their identities.

The Order UUID remains the permanent transaction identity.

---

## 24. Waiter Model

A Waiter is an Employee with appropriate permissions.

The database does not need a separate independent person entity for Waiters.

Conceptually:

```text id="d7j1tc"
Employee
   ↓
Role / Permission
   ↓
Waiter capability
```

This avoids duplicating employee identity.

---

## 25. Primary Waiter

A Dine-in Order may have one Primary Waiter.

The Order may reference:

```text id="0y1g3f"
primary_waiter_id
```

The Primary Waiter is the main staff attribution for the Order.

---

## 26. Primary Waiter Scope

The Primary Waiter must:

* belong to the same Business;
* have access to the Order Branch;
* be active when assigned;
* satisfy required role/permission rules.

The database and application layer must enforce these conditions.

---

## 27. Assisting Waiter

A second Waiter may temporarily assist with an Order.

The assisting relationship must not replace the Primary Waiter.

Conceptual model:

```text id="7b4f6k"
Order
 ├── Primary Waiter
 └── Assisting Waiter
```

---

## 28. Assisting Waiter Assignment

The current business rule allows one assisting Waiter assignment.

Therefore, the database may use:

```text id="s9x2h7"
OrderAssistingWaiter
---------------------
id
order_id
waiter_id
assigned_by
assigned_at
removed_at
```

The exact implementation may instead use an assignment table with active-state uniqueness.

---

## 29. Assisting Waiter History

An assisting Waiter assignment should remain historically traceable.

If the assignment is removed, the system should retain:

* original Waiter;
* assigning actor;
* assignment timestamp;
* removal timestamp;
* removing actor where applicable.

---

## 30. Primary Waiter Changes

Changing the Primary Waiter is a controlled operation.

The system must retain the previous assignment through history/audit.

Changing the Primary Waiter must not rewrite historical Order creation attribution.

---

## 31. Waiter Assignment Authorization

Waiter assignment requires the appropriate permission.

A Waiter must not automatically assign themselves to arbitrary Orders unless the permission model explicitly allows it.

The normal authorization model applies:

```text id="2p4b8h"
Role Permission
+
Employee Override
+
Branch Scope
+
Subscription Entitlement
```

---

## 32. Waiter Branch Scope

An Employee may work in multiple Branches.

A Waiter may therefore have different access across Branches.

The database must not assume that an Employee is automatically authorized for every Branch of the Business.

---

## 33. Table Assignment Authorization

Assigning or changing a Table requires the appropriate Order/Table permission.

The database must validate:

* Order Branch;
* Table Branch;
* Table status;
* Table Visit state;
* employee authorization.

---

## 34. Table Reassignment

Moving an active Dine-in Order to another Table is a controlled operation.

The operation must preserve:

* original Table;
* new Table;
* actor;
* timestamp;
* reason if required;
* Table Visit relationship.

The database must not silently rewrite the original Table history.

---

## 35. Table Reassignment and Visit

If an Order is moved to another Table within the same Branch, the system must define whether:

* the existing Table Visit moves with the Order;
* or a new Visit context is created.

Default rule:

```text id="9e5g1a"
Same customer visit
    ↓
Table Visit remains the grouping context
```

The reassignment is recorded as a historical event.

---

## 36. Cross-Branch Table Movement

Moving an Order/Table Visit to another Branch is not supported.

The database must reject cross-Branch reassignment.

---

## 37. Table Merge

Table merging is not required in the current scope.

The database model should not introduce complex merge semantics unless explicitly added later.

Multiple Tables may still exist independently.

---

## 38. Table Split

Table splitting is not required in the current scope.

If future requirements introduce splitting, it must be designed as a controlled Table Visit/Order operation rather than direct destructive reassignment.

---

## 39. Table Deactivation

A Table may become:

```text id="q4h9c0"
INACTIVE
```

when temporarily unavailable.

Examples:

* maintenance;
* renovation;
* operational closure.

An inactive Table cannot receive a new Dine-in Order.

Existing historical Orders remain intact.

---

## 40. Table Archiving

A Table may be archived when permanently removed from normal operation.

Historical references remain valid.

Archived Tables must not appear as available POS destinations.

---

## 41. Hall Deactivation

A Hall may be deactivated.

Its Tables may remain historically accessible.

The system must prevent new Table assignments to inactive Halls.

---

## 42. Table Layout

The current database model does not require graphical coordinates.

Future layout information may be added through separate fields or a configuration entity.

Any layout metadata must not become part of the transaction identity.

---

## 43. Display Ordering

Halls and Tables may have `display_order`.

This is a UI ordering value.

Changing display order must not affect:

* Table UUID;
* Table Number;
* Orders;
* Table Visits;
* historical reports.

---

## 44. Table Code and Name

The visible Table Number or Name may change.

Historical Orders retain the relevant snapshot where required.

Current Table configuration is not sufficient to reconstruct historical display information.

---

## 45. Table Snapshot in Orders

An Order should retain enough historical Table information to reconstruct its original context.

Recommended snapshot fields may include:

```text id="8g3v2p"
table_id
table_number_snapshot
hall_id
hall_name_snapshot
```

The current Table record must not be required to display historical Orders correctly.

---

## 46. Waiter Snapshot

Historical Order data should preserve the relevant waiter identity.

Reports may resolve the Employee identity from historical references.

Where employee names are needed for immutable historical reconstruction, an appropriate snapshot may be stored.

Employee deactivation must not make historical reports unreadable.

---

## 47. Occupancy Query

POS must be able to determine available/busy Tables efficiently.

Recommended operational query:

```text id="c9m2k4"
SELECT tables
WHERE branch_id = current_branch
AND status = ACTIVE
AND NOT EXISTS (
    active operational order
)
```

The exact query may use a maintained current-state representation if necessary for performance.

---

## 48. Current-State Optimization

The system may maintain current Table Visit or occupancy state for fast POS reads.

If such a state is maintained:

* it is derived from authoritative Order/Visit transactions;
* it must be updated atomically with relevant changes;
* reconciliation must be possible;
* cache must not become authoritative.

---

## 49. Occupancy Consistency

The system must prevent:

```text id="3k7s2m"
Table = AVAILABLE
while an active operational Dine-in Order still occupies it
```

and:

```text id="f8x4q1"
Table = BUSY
without a valid active operational Order/Visit
```

unless the state is explicitly represented as a short-lived transition.

---

## 50. Concurrent Table Assignment

Two cashiers must not be able to successfully assign the same available Table to two independent new Table Visits at the same time.

The database must serialize the relevant operation.

Default behavior:

```text id="m1j5q7"
First successful assignment
        ↓
Table Visit created

Second assignment
        ↓
Rejected / refresh required
```

---

## 51. Concurrent Table Release

Table release must be safe against concurrent Order updates.

The database transaction must validate current Order/Visit state before closing the Table Visit.

---

## 52. Concurrent Waiter Assignment

Two employees must not silently overwrite the Primary Waiter assignment.

Optimistic concurrency or equivalent locking should be used.

Stale updates must be rejected.

---

## 53. Waiter Assignment History

The database should maintain an assignment history for:

* Primary Waiter;
* Assisting Waiter.

The history must preserve:

```text id="q8h4z0"
who
what
when
from
to
```

---

## 54. Offline Table Operations

Trusted devices may perform permitted Table operations offline.

Examples:

* create Table Visit;
* assign Order to Table;
* assign Waiter;
* release Table.

Offline operations require:

* valid offline authorization;
* current local configuration;
* UUID identity;
* durable local storage;
* synchronization.

---

## 55. Offline Table Conflict

If two offline devices assign the same Table independently:

```text id="4g2n8p"
Device A
   ↓
Table Visit A

Device B
   ↓
Table Visit B
```

The server must resolve the conflict explicitly.

The system must not silently merge or overwrite both visits.

---

## 56. Offline Server Authority

After synchronization:

```text id="c1v7k2"
Server authoritative state
        ↓
Accepted configuration
```

A rejected offline Table operation becomes a conflict or rejection record.

The original offline event remains historically traceable.

---

## 57. Synchronization Identity

Table Visits and waiter assignment events should have UUID identities where they can be created offline.

Repeated synchronization of the same UUID must be idempotent.

---

## 58. Table Configuration Synchronization

Changes to:

* Hall;
* Table;
* Table Number;
* Table status;
* display order

must synchronize as configuration changes.

Transaction synchronization must take precedence over configuration synchronization.

---

## 59. Stale Table Configuration

An offline device may temporarily display a Table that has since been deactivated.

When the transaction is synchronized, the server validates the Table configuration.

If the Table was no longer valid at the relevant transaction time, the operation becomes an explicit conflict/rejection.

---

## 60. Table Visit and Payment

A Table Visit may contain multiple Orders and multiple Payments.

Payment completion does not automatically define Table Visit closure unless the operational flow determines that no active Orders remain.

The Table becomes Available only when the active operational conditions are satisfied.

---

## 61. Table Visit and Cash Session

Orders within a Table Visit may span Cash Sessions because cashier handover can occur while the customer remains at the Table.

Therefore:

```text id="m5r2h1"
Table Visit
    ↓
Order(s)
    ↓
Multiple Cash Sessions
```

may be valid.

The database must not require one Table Visit to belong to one Cash Session.

---

## 62. Table Visit and Waiter

A Table Visit may retain a primary operational waiter context.

However, individual Orders may have their own Primary Waiter attribution.

This allows historical reporting at both:

* visit level;
* order level.

---

## 63. Suggested `halls` Fields

```text id="u8y2m6"
id
business_id
branch_id
code
name
status
display_order
created_at
updated_at
```

Recommended uniqueness:

```text id="3j9k5f"
UNIQUE (branch_id, code)
```

---

## 64. Suggested `tables` Fields

```text id="q2x7m1"
id
business_id
branch_id
hall_id
table_number
name
capacity
status
display_order
created_at
updated_at
```

Recommended uniqueness:

```text id="n7r4w3"
UNIQUE (branch_id, table_number)
```

---

## 65. Suggested `table_visits` Fields

```text id="p6v1c8"
id
business_id
branch_id
table_id
primary_waiter_id
status
opened_at
closed_at
created_by
closed_by
created_at
updated_at
```

---

## 66. Suggested `waiter_assignments` Fields

```text id="k3m9q2"
id
business_id
branch_id
order_id
waiter_id
assignment_type
assigned_by
assigned_at
removed_at
removed_by
created_at
```

Possible `assignment_type` values:

```text id="v8w4s1"
PRIMARY
ASSISTING
```

If Primary Waiter is stored directly on the Order, the assignment history table should still preserve historical changes.

---

## 67. Suggested `table_reassignment_history` Fields

```text id="t4n7b9"
id
order_id
table_visit_id
from_table_id
to_table_id
actor_id
reason
created_at
```

This is append-only.

---

## 68. Foreign Key Rules

Important ownership relationships include:

```text id="6v0p2r"
hall.branch_id → branch.id
table.branch_id → branch.id
table.hall_id → hall.id
table_visit.branch_id → branch.id
table_visit.table_id → table.id
```

Employee references must be Business/Branch compatible.

---

## 69. Table Visit Constraints

A Table Visit must:

* belong to exactly one Branch;
* reference one Table;
* reference a Table from the same Branch;
* have at most one active open state;
* not receive new Orders after closure.

---

## 70. Active Visit Uniqueness

A Branch/Table should not have multiple active Table Visits simultaneously.

Conceptually:

```text id="r3k7x9"
UNIQUE ACTIVE VISIT
(branch_id, table_id)
```

PostgreSQL partial unique indexes may be used.

---

## 71. Active Primary Waiter

An Order should have at most one active Primary Waiter assignment.

A database constraint or transactional service must enforce this.

Assisting Waiter is a separate relationship.

---

## 72. Active Assisting Waiter

The current business rule allows at most one active assisting Waiter per Order.

This may be enforced through a partial unique index over:

```text id="g6m2v8"
(order_id, assignment_type)
```

for active assignments.

---

## 73. Historical Assignment Preservation

Removing an active assignment must not delete the historical record.

The record receives:

* `removed_at`;
* `removed_by`.

Historical assignment rows remain immutable after closure except through a controlled correction process.

---

## 74. Table and Order Deletion

Normal deletion of Tables, Halls, or Visits is not allowed when historical Orders depend on them.

Archive/deactivate instead.

During Business deletion, dependent records are removed through the controlled Data Lifecycle process.

---

## 75. Reporting

The model supports reports for:

* sales by Table;
* sales by Hall;
* Table occupancy;
* Orders by Waiter;
* Waiter performance;
* Table Visit duration;
* active Tables;
* cancelled Orders by Table;
* historical Table activity.

Historical reports must use stored snapshots where required.

---

## 76. Audit

Important operations must generate audit events.

Examples:

* Table created;
* Table deactivated;
* Table archived;
* Table reassigned;
* Table Visit opened;
* Table Visit closed;
* Primary Waiter assigned;
* Primary Waiter changed;
* Assisting Waiter assigned;
* Assisting Waiter removed;
* offline conflict resolved.

Routine read operations do not normally require audit records.

---

## 77. Cache

Current Table occupancy may be cached.

Cache must never be authoritative.

After cache loss, current state must be reconstructable from authoritative database records.

---

## 78. Performance

Table and Waiter operations are high-frequency POS reads.

Therefore:

* active Tables must be indexed by Branch;
* active Table Visits must be efficiently queryable;
* active waiter assignments must be indexed;
* current occupancy must not require scanning all historical Orders;
* historical assignment data may remain append-only;
* reporting queries must not block POS transactions.

---

## 79. Transaction Boundaries

### Open Table Visit

```text id="1p5j6r"
Validate Table
Validate Branch
Validate Employee
Check active Visit
Create Visit
Commit
```

### Assign Order to Table

```text id="z8c4m2"
Validate Order
Validate Table
Validate Visit
Validate Branch
Persist assignment
Commit
```

### Assign Waiter

```text id="m2w6q8"
Validate Employee
Validate Branch Scope
Validate Permission
Persist assignment
Commit
```

### Close Table Visit

```text id="q7h3n1"
Validate no active operational Orders
Persist closure
Commit
```

---

## 80. Failure Handling

If Table Visit creation fails:

```text id="f6n8k3"
No partial Visit
```

If waiter assignment fails:

```text id="w3m9q5"
Existing valid waiter assignment remains unchanged
```

If table reassignment fails:

```text id="j4v7s2"
Original Table relationship remains valid
```

If printer failure occurs:

```text id="b8q1m6"
Table state is unaffected
```

If synchronization response is lost:

```text id="r5t2k9"
Retry using the same UUID
```

---

## 81. Security Requirements

The database model must support:

* Business isolation;
* Branch isolation;
* permission-controlled table operations;
* employee branch scope;
* trusted device context;
* offline authorization;
* audit;
* synchronization validation.

A trusted device does not independently grant access to Tables or Orders.

---

## 82. Historical Integrity

The following must remain reconstructable:

* Table UUID;
* Table Number at relevant time;
* Hall;
* Branch;
* Table Visit;
* Order relationship;
* Primary Waiter;
* assisting Waiter;
* assignment history;
* reassignment history;
* creation/closure timestamps.

Current Table configuration must not be required to reconstruct historical transactions.

---

## 83. Data Lifecycle

During subscription expiry:

* Tables remain readable;
* historical Visits remain readable;
* historical Waiter assignments remain readable;
* modifying configuration is restricted according to entitlement.

During Business deletion:

* Tables;
* Halls;
* Table Visits;
* Waiter assignment history

are removed according to dependency-aware lifecycle rules.

---

## 84. Indexing Strategy

Recommended indexes:

```text id="p8n4w7"
halls(branch_id, status, display_order)

tables(branch_id, status, display_order)
tables(branch_id, table_number)

table_visits(branch_id, table_id, status)
table_visits(table_id, opened_at)

waiter_assignments(order_id, assignment_type)
waiter_assignments(waiter_id, assigned_at)

table_reassignment_history(order_id, created_at)
```

Partial indexes should be considered for active records.

---

## 85. Cross-Domain Relationships

### Branch

Owns Halls and Tables.

### Order

References Table and Table Visit.

### Employee

Provides Waiter identity.

### Cash

Provides Cash Session context for related Orders.

### Payment

Determines financial settlement independently.

### Menu

Does not determine Table occupancy.

### Kitchen

Receives Order preparation events.

### Audit

Records important Table/Waiter changes.

### Synchronization

Transfers offline Table/Waiter operations.

### Configuration

Controls Hall/Table availability and display configuration.

### Reporting

Uses historical Table/Waiter relationships.

---

## 86. Database Invariants

The following invariants are mandatory:

1. Every Hall belongs to exactly one Branch.
2. Every Table belongs to exactly one Branch.
3. Every Hall belongs to exactly one Business.
4. Every Table belongs to exactly one Business.
5. Hall and Table Business ownership must match.
6. Table and Hall Branch ownership must match.
7. Table UUID is globally unique.
8. Hall UUID is globally unique.
9. Table Visit UUID is globally unique.
10. Table UUIDs are never reused.
11. Hall UUIDs are never reused.
12. Table Visit UUIDs are never reused.
13. Table Number is unique within a Branch.
14. Hall Code is unique within a Branch.
15. Table capacity must be positive.
16. Inactive Tables cannot receive new Orders.
17. Archived Tables cannot receive new Orders.
18. Inactive Halls cannot receive new Table Visits.
19. Archived Halls cannot receive new Table Visits.
20. A Table cannot belong to another Branch through reassignment.
21. A Table Visit belongs to exactly one Branch.
22. A Table Visit references a Table from the same Branch.
23. A Table Visit cannot be active for more than one Branch.
24. A Table cannot have multiple active Table Visits simultaneously.
25. A closed Table Visit cannot receive new Orders.
26. Dine-in Orders may reference a Table.
27. Takeaway Orders normally do not require a Table.
28. Order and Table Branch ownership must match.
29. Order and Table Visit Branch ownership must match.
30. Table Visit and Table identity must match.
31. Paid historical Orders do not by themselves keep a Table Busy.
32. Table occupancy must reflect active operational Orders/Visits.
33. Available Tables cannot have conflicting active Visits.
34. Busy Tables must have valid active operational context.
35. Primary Waiter belongs to the same Business as the Order.
36. Primary Waiter must have access to the Order Branch.
37. An Order has at most one active Primary Waiter.
38. An Order has at most one active Assisting Waiter under the current rule.
39. Primary Waiter and Assisting Waiter are separate relationships.
40. Assisting Waiter does not automatically replace Primary Waiter.
41. Waiter assignment requires appropriate authorization.
42. Waiter self-assignment cannot bypass permission rules.
43. Waiter assignment history is preserved.
44. Removing an assignment does not delete its history.
45. Changing Primary Waiter does not rewrite original Order creation attribution.
46. Table reassignment requires authorization.
47. Table reassignment must remain within the same Branch.
48. Table reassignment history is append-only.
49. Historical Table context must remain reconstructable.
50. Historical Waiter context must remain reconstructable.
51. Table Number changes do not change Table UUID.
52. Hall name changes do not change Hall UUID.
53. Display order changes do not alter transaction identity.
54. Table configuration changes do not rewrite historical Orders.
55. Table Visit remains the grouping context for a customer visit.
56. New customer visits use new Table Visit UUIDs.
57. Previous Table Visits are not reused.
58. Multiple Orders may belong to one Table Visit.
59. Multiple Cash Sessions may be associated with Orders in one Table Visit.
60. Cashier handover does not change Order UUID.
61. Cashier handover does not silently rewrite Table Visit history.
62. Cross-Branch Table movement is forbidden.
63. Table merge is not required by the current model.
64. Table split is not required by the current model.
65. Offline Table operations require valid offline authorization.
66. Offline Table operations use UUID-based identity.
67. Repeated synchronization of the same event is idempotent.
68. Offline conflicts must be explicit.
69. Server state is authoritative after synchronization.
70. Stale Table configuration must be validated during synchronization.
71. Transaction synchronization takes precedence over configuration synchronization.
72. Current occupancy state may be cached but cache is not authoritative.
73. Occupancy must be reconstructable after cache loss.
74. Concurrent Table assignments must be serialized.
75. First successful assignment wins when competing assignments target the same Table.
76. Concurrent Primary Waiter updates must not silently overwrite each other.
77. Stale waiter updates must be rejected.
78. Table Visit creation must be atomic.
79. Table Visit closure must validate current Order state.
80. Failed Table operations must not partially change authoritative state.
81. Subscription expiry does not delete Table history.
82. Subscription downgrade does not delete Table history.
83. Business deletion follows the controlled lifecycle.
84. Business deletion is dependency-aware.
85. Deletion operations are idempotent.
86. Deleted Table UUIDs are never reused.
87. Historical assignment records remain immutable.
88. Audit records remain separate from operational Table state.
89. Heavy reporting queries must not block normal POS Table operations.
90. Branch isolation applies to every Table and Waiter query.
91. Business isolation applies to every Table and Waiter query.
92. Device trust does not replace authorization.
93. Historical reports must not depend solely on current Table configuration.
94. Database constraints and application validation must enforce the same ownership boundaries.
95. Table state must never bypass Order state rules.
96. Waiter assignment must never bypass Employee lifecycle rules.
97. Table availability must not be used as proof of inventory or payment availability.
98. Current operational state must remain directly queryable for POS.
99. Historical state must remain available for required retention.
100. Table, Visit, and Waiter relationships must preserve transaction history without destructive rewriting.

---

## 87. Related Documents

### Database

* `02_Database_Architecture.md`
* `03_Tenant_and_Business_Data_Model.md`
* `04_Identity_and_Access_Data_Model.md`
* `05_Branch_and_Organizational_Data_Model.md`
* `07_Device_and_Trust_Data_Model.md`
* `13_Order_and_Order_Item_Data_Model.md`
* `16_Cash_Register_and_Cash_Session_Data_Model.md`

### Domain

* `05_Branch_Domain.md`
* `06_Order_Domain.md`
* `07_Cash_Domain.md`
* `12_Employee_and_Payroll_Domain.md`
* `20_Cross_Domain_Relationships_Domain.md`

### System Analysis

* `07_POS_and_Order_System.md`
* `09_Table_and_Waiter_Management.md`
* `14_Cash_Register_and_Cash_Session.md`
* `15_Shift_Handover.md`
* `27_System_Wide_Consistency_and_Concurrency.md`

### Architecture

* `07_Database_Architecture.md`
* `08_Offline_Architecture.md`
* `09_Synchronization_Architecture.md`
* `17_Failure_Recovery_Architecture.md`
* `20_Architecture_Invariants_and_Guardrails.md`

---

## 88. Final Rule

The Table and Waiter database model must provide a simple and fast POS experience while preserving historical context.

The central rules are:

```text id="v4j8p2"
Table identity is permanent.
Table occupancy reflects active operational state.
Table Visits define customer visit grouping.
Primary Waiter and Assisting Waiter are separate.
Historical Table and Waiter context must not be silently rewritten.
```

Table management must remain connected to Orders, Employees, Cash Sessions, Offline Synchronization, Audit, and Reporting through explicit and validated relationships.
