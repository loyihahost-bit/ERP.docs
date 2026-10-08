# Audit and History UI

**Document ID:** FA-18
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

## 1. Purpose

This document defines the Frontend architecture and user interface behavior for Audit, History, Change History and Correction History in FastFood ERP.

The purpose of the Audit and History UI is to provide authorized users with a trustworthy view of important system and business changes.

The Frontend must make it possible to understand:

* what happened;
* when it happened;
* who performed the action;
* which Business was affected;
* which Branch was affected;
* which device was involved;
* which entity was affected;
* what the previous state was;
* what the new state was;
* why the change occurred;
* whether the operation succeeded;
* whether the change was later corrected.

The Frontend must never modify authoritative audit/history records.

Backend remains authoritative for audit and historical data.

---

# 2. Scope

This document covers:

* Audit Center;
* History Center;
* entity history;
* configuration history;
* financial history;
* inventory history;
* order history;
* cash history;
* payment history;
* refund history;
* payroll history;
* attendance history;
* permission history;
* device history;
* subscription history;
* synchronization history;
* correction history;
* audit event detail;
* before/after state;
* actor information;
* device context;
* Business/Branch scope;
* search;
* filtering;
* sorting;
* pagination;
* historical reconstruction;
* correction chains;
* audit access permissions;
* sensitive data protection;
* export;
* immutable records;
* offline behavior;
* synchronization;
* performance;
* accessibility;
* testing;
* observability.

---

# 3. Core Principles

Audit and History UI must follow these principles:

1. Historical information is read-only.
2. Audit records are immutable.
3. History must remain attributable.
4. Current state must not replace historical state.
5. Backend is authoritative.
6. Business isolation is mandatory.
7. Branch isolation is mandatory.
8. Permission checks are mandatory.
9. Historical records must not be silently hidden.
10. Sensitive information must be protected.
11. Correction must create traceable history.
12. UI must distinguish audit from ordinary history.
13. Users must be able to reconstruct important changes.
14. Historical information must not depend on current configuration.
15. Frontend must not independently reconstruct authoritative history.
16. Audit queries must not interfere with POS performance.

---

# 4. Audit vs History

Audit and History are related but distinct concepts.

### Audit

Audit answers:

> Who performed what action, when, where and with what result?

Examples:

* Product price changed;
* Permission changed;
* Cash Session closed;
* Refund created;
* Employee deactivated;
* Device revoked.

### History

History answers:

> How did the entity's state change over time?

Examples:

* Product price history;
* Recipe version history;
* Employee role history;
* Cash Session history;
* Order status history.

The UI should distinguish these concepts.

---

# 5. Audit Categories

The system may support categories such as:

```text id="v8c2m1"
BUSINESS_AUDIT
SECURITY_AUDIT
CONFIGURATION_AUDIT
FINANCIAL_AUDIT
INVENTORY_AUDIT
ORDER_AUDIT
ACCESS_AUDIT
DEVICE_AUDIT
SUBSCRIPTION_AUDIT
SYNCHRONIZATION_AUDIT
SYSTEM_AUDIT
EXPORT_AUDIT
LIFECYCLE_AUDIT
```

The exact enumeration remains Backend-authoritative.

---

# 6. History Categories

History may include:

* Product History;
* Recipe History;
* Set History;
* Menu History;
* Price History;
* Order History;
* Payment History;
* Refund History;
* Cash Session History;
* Inventory History;
* Employee History;
* Attendance History;
* Payroll History;
* Permission History;
* Device History;
* Subscription History;
* Configuration History;
* Report Version History.

---

# 7. Audit Center

Authorized users may access:

```text id="7h3m8q"
Audit
├── Overview
├── All Events
├── Configuration
├── Financial
├── Inventory
├── Orders
├── Access
├── Devices
├── Security
├── Synchronization
└── Lifecycle
```

Visible categories depend on permissions.

---

# 8. History Center

History may be accessed through:

* dedicated History Center;
* entity detail page;
* configuration page;
* report page;
* correction detail.

Example:

```text id="x2k7p4"
Product
   ├── Details
   ├── Pricing
   ├── Recipe
   └── History
```

---

# 9. Entity History

Entity detail pages should provide a History tab where appropriate.

Examples:

* Product;
* Order;
* Cash Session;
* Employee;
* Inventory Item;
* Recipe;
* Set;
* Payment.

The History tab must contain only history relevant to that entity.

---

# 10. Audit Event Identity

Every audit event should have a stable identifier.

Conceptually:

```text id="c7p1m9"
event_uuid
```

The Frontend uses this identifier for:

* detail navigation;
* deduplication;
* export;
* reconciliation;
* support references.

---

# 11. Operation Identity

Where available, the UI may display:

* operation UUID;
* request ID;
* correlation ID.

These identifiers are useful for troubleshooting.

They must not be treated as authorization credentials.

---

# 12. Audit Event Structure

Conceptually:

```text id="m9x4r2"
Event UUID
Operation UUID
Request ID
Category
Action
Result
Actor
Business
Branch
Device
Entity
Timestamp
Reason
Before
After
Source
```

The exact API contract remains Backend-authoritative.

---

# 13. Actor Information

Audit detail should display the responsible actor where available.

Example:

```text id="p3q7v1"
Actor
Employee: John Doe
Employee ID: EMP-1024
```

For system operations:

```text id="d5k8s2"
Actor
System
```

The Frontend must clearly distinguish employee and system actors.

---

# 14. Actor Identity Integrity

Historical actor information must come from the audit record.

The Frontend must not replace the historical actor with the employee's current name or role when this would change historical meaning.

---

# 15. Business Context

Audit detail should show:

```text id="n7f3c2"
Business
Main Restaurant Group
```

Business context is mandatory where applicable.

---

# 16. Branch Context

Branch-scoped events should display:

```text id="q5w8m1"
Branch
Chilanzar
```

Business-wide events may not have a Branch.

The UI should explicitly indicate:

```text id="t2k6p9"
Scope: Business
```

when appropriate.

---

# 17. Device Context

Important operational events may contain device information.

Example:

```text id="b4r9x2"
Device
POS-03
```

Device information is historical context.

The UI must not assume the device still exists.

---

# 18. Cash Session Context

Where applicable:

```text id="h7m2q5"
Cash Register
Register 01

Cash Session
Session #145
```

This helps reconstruct financial operations.

---

# 19. Order Context

Order-related audit events may show:

* Order number;
* Order UUID;
* Branch;
* Cash Session;
* Employee;
* Device.

The current Order state must not replace historical event information.

---

# 20. Audit Action

Audit detail should clearly display the action.

Examples:

```text id="w5r1k7"
PRICE_CHANGED
```

```text id="z2n8c4"
CASH_SESSION_CLOSED
```

```text id="m7q3p9"
EMPLOYEE_DEACTIVATED
```

Technical action codes may be accompanied by human-readable descriptions.

---

# 21. Audit Result

The UI should distinguish:

* SUCCESS;
* FAILURE;
* REJECTED;
* CONFLICT;
* CANCELLED.

Exact values remain Backend-authoritative.

---

# 22. Failed Operations

Failed operations may be retained for security or audit purposes.

Example:

```text id="s6f2x8"
Result: REJECTED
Reason: Unauthorized permission
```

A failed operation must not be displayed as a successful change.

---

# 23. Timestamp

Audit events must display their authoritative timestamp.

The UI may display:

```text id="j4m8q2"
2 minutes ago
```

with the exact timestamp available in detail.

---

# 24. Timezone

Audit timestamps must respect system timezone presentation rules.

The Frontend must distinguish:

* UTC technical timestamp;
* Business timezone;
* Branch timezone where applicable.

---

# 25. Reason

Where an operation requires a reason, the UI should display it.

Examples:

* refund reason;
* correction reason;
* price change reason;
* cash correction reason;
* inventory adjustment reason.

Historical reason must not be overwritten by a later reason.

---

# 26. Before and After State

Where Backend provides before/after data, the UI should show:

```text id="u8q3m7"
Before
Price: 30,000

After
Price: 32,000
```

The UI must clearly distinguish old and new values.

---

# 27. Before/After Security

Before/after information may contain sensitive data.

The Frontend must:

* respect permissions;
* mask restricted fields;
* avoid unnecessary exposure;
* never expose secret values.

---

# 28. Field-Level Changes

For configuration changes, the UI may display field-level differences.

Example:

```text id="x5p9k3"
Price
30,000 → 32,000

Category
Burgers → Main Dishes
```

Only fields supplied by Backend should be presented as authoritative changes.

---

# 29. Configuration History

Configuration history may include:

* menu;
* pricing;
* Branch configuration;
* Business configuration;
* permissions;
* subscription;
* dashboard defaults.

Configuration history must remain immutable.

---

# 30. Price History

Price history should display:

* Product;
* Branch;
* old price;
* new price;
* actor;
* timestamp;
* reason;
* effective configuration/version.

---

# 31. Recipe History

Recipe history should display:

* Recipe Version;
* status;
* creator;
* approver;
* approval time;
* components;
* effective period;
* archived/superseded state.

Historical Recipe Versions must remain distinguishable.

---

# 32. Set History

Set history may include:

* Set composition;
* price;
* configuration version;
* effective date/session boundary;
* actor;
* approval;
* superseded version.

---

# 33. Order History

Order history may include:

* creation;
* item addition;
* item modification;
* status changes;
* discount;
* payment;
* cancellation;
* refund;
* correction;
* synchronization events.

Historical Order Item snapshots remain authoritative.

---

# 34. Order Item History

Where supported, Order Item history should show:

```text id="f7k3q1"
Product
Quantity
Price
Discount
Status
Modifier
Timestamp
Actor
```

Historical values must not be replaced by current Product values.

---

# 35. Payment History

Payment history may include:

* payment created;
* payment completed;
* payment correction;
* refund;
* failed payment;
* reconciliation.

Payment history is read-only.

---

# 36. Refund History

Refund history should display:

* original transaction;
* refund amount;
* reason;
* actor;
* approval;
* timestamp;
* status.

Current Product price must never be used to reinterpret historical refund amounts.

---

# 37. Cash Session History

Cash Session history should include:

* opening;
* operations;
* handover;
* closing;
* expected cash;
* actual cash;
* discrepancy;
* correction.

Closed sessions remain historical records.

---

# 38. Cash Correction History

Corrections must be traceable.

Example:

```text id="q9w4m7"
Original
Expected: 1,500,000
Actual: 1,450,000

Correction
Actual: 1,470,000

Reason
Recount confirmed
```

The original record must remain available.

---

# 39. Inventory History

Inventory history may include:

* purchase;
* manual exit;
* recipe deduction;
* adjustment;
* inventory count;
* variance;
* correction;
* synchronization.

---

# 40. Inventory Transaction History

Each important transaction should show:

* Product;
* Warehouse;
* quantity;
* cost where permitted;
* source;
* actor;
* operation UUID;
* timestamp;
* reason.

---

# 41. FIFO History

Where FIFO information is visible, the UI should show historical layers without modifying them.

Example:

```text id="r8k3m2"
Layer
Created: 2026-10-01
Quantity: 20 kg
Cost: 42,000/kg
```

Historical layers are read-only.

---

# 42. Employee History

Employee history may include:

* creation;
* role assignment;
* Branch assignment;
* permission change;
* status change;
* deactivation;
* reactivation;
* salary configuration;
* attendance correction.

Sensitive employee information requires authorization.

---

# 43. Permission History

Permission history should clearly show:

```text id="k5q9x3"
Permission
inventory.adjust

Before
Denied

After
Granted

Actor
Owner

Branch
Branch A
```

---

# 44. Role History

Role changes should preserve:

* previous role;
* new role;
* actor;
* timestamp;
* Branch scope;
* reason where required.

Current role must not replace historical role information.

---

# 45. Device History

Device history may include:

* registration;
* verification;
* trust;
* revocation;
* offline authorization;
* security events.

Sensitive cryptographic information must never be displayed.

---

# 46. Subscription History

Subscription history may include:

* tariff changes;
* activation;
* expiry;
* read-only transition;
* deletion eligibility;
* deletion;
* reactivation.

Historical subscription state must remain attributable.

---

# 47. Synchronization History

Sync history may include:

* batch;
* operation;
* accepted;
* rejected;
* conflict;
* unknown result;
* retry;
* reconciliation.

---

# 48. Offline Operation History

Offline operations should retain:

* operation UUID;
* device;
* employee;
* Business;
* Branch;
* local timestamp;
* server acceptance;
* synchronization result.

The UI must distinguish local creation time from server processing time where both exist.

---

# 49. Correction History

Correction history is critical for historical integrity.

The UI should show:

```text id="m3v7k1"
Original
   ↓
Correction
   ↓
Correction Result
```

A correction must never appear as if the original transaction never existed.

---

# 50. Correction Chain

Where supported, the UI may display:

```text id="q7n4p2"
Original Event
     ↓
Correction #1
     ↓
Correction #2
     ↓
Final State
```

Each event remains separately identifiable.

---

# 51. Correction Limits

If the Backend imposes correction limits, the Frontend should display the current state.

The Frontend must not independently calculate or bypass correction limits.

---

# 52. Audit Search

Audit search may support:

* Event UUID;
* Operation UUID;
* actor;
* Branch;
* entity;
* action;
* category;
* result;
* date range.

---

# 53. History Search

History search may support:

* entity;
* entity ID;
* action;
* actor;
* date;
* version;
* Branch.

---

# 54. Search Scope

Search must remain within the authorized Business/Branch scope.

Search parameters must never be treated as authorization.

---

# 55. Filters

Recommended filters:

```text id="c6q2w8"
Business
Branch
Category
Action
Actor
Device
Entity
Result
Date Range
```

Available filters depend on permissions.

---

# 56. Date Range

Audit/history queries should support:

* Today;
* Yesterday;
* Last 7 Days;
* Last 30 Days;
* Custom Range.

Large historical ranges may require asynchronous export.

---

# 57. Sorting

Default:

**Newest first**

Supported sorting may include:

* timestamp;
* actor;
* action;
* category;
* entity.

Backend-supported sorting fields only.

---

# 58. Pagination

Audit/history lists must use pagination.

Cursor pagination is preferred for large datasets.

The Frontend must never load unlimited historical events.

---

# 59. Audit Detail Navigation

Clicking an audit event should open a detail view.

Possible layout:

```text id="x4m8q2"
Event Summary
     ↓
Context
     ↓
Actor
     ↓
Entity
     ↓
Before / After
     ↓
Reason
     ↓
Correction Chain
     ↓
Technical Metadata
```

---

# 60. Technical Metadata

Technical metadata may include:

* Event UUID;
* Operation UUID;
* Request ID;
* Correlation ID;
* source;
* device;
* synchronization information.

Technical metadata should be hidden or collapsed for ordinary users where appropriate.

---

# 61. Technical vs Business View

The UI may provide:

### Business View

Simple explanation of the change.

### Technical View

Detailed identifiers and synchronization metadata.

This prevents ordinary users from being overwhelmed by technical information.

---

# 62. Audit Source

Source may indicate:

* WEB;
* POS;
* OFFLINE;
* API;
* SYSTEM;
* BACKGROUND_JOB;
* SYNCHRONIZATION.

The exact enumeration is Backend-authoritative.

---

# 63. System Actor

System-generated operations must be displayed as:

```text id="q6m3p8"
Actor: System
```

The UI must not invent an employee actor.

---

# 64. Background Job Actor

Background operations may display:

```text id="w4k7n2"
Actor: System
Source: Background Job
```

---

# 65. Offline Actor Context

Offline-created operations should retain:

* employee;
* device;
* Branch;
* local source;
* synchronization status.

---

# 66. Audit Export

Authorized users may export audit/history data.

Export may support:

* XLSX;
* CSV where supported;
* other controlled formats.

The exact format remains Backend/API-authoritative.

---

# 67. Export Security

Audit exports may contain sensitive information.

The UI must enforce:

* export permission;
* Business scope;
* Branch scope;
* sensitive-data rules.

Backend remains authoritative.

---

# 68. Export Audit

Exporting audit/history data may itself create an audit event.

The Frontend should not assume that exporting audit data is invisible.

---

# 69. Historical Export

When exporting a historical report or version:

The UI must preserve:

* report version;
* scope;
* period;
* creation state.

Export must not silently regenerate the report from current data.

---

# 70. Audit Access Permissions

Example permission categories:

```text id="n3w7q1"
audit.view
audit.view_financial
audit.view_security
audit.view_inventory
audit.view_configuration
audit.export
history.view
history.view_sensitive
```

Actual permission names remain centralized.

---

# 71. Sensitive Audit Data

Sensitive fields may include:

* salary;
* personal employee data;
* security information;
* financial information;
* device metadata.

The UI should mask or omit restricted values.

---

# 72. Security Event Access

Security audit events should have stricter access control.

Security-sensitive metadata must not be visible to ordinary employees.

---

# 73. Audit Data and Subscription

Read-only subscription may allow:

* audit viewing;
* history viewing;
* allowed export.

Modifying historical data is never allowed.

---

# 74. Deletion Lifecycle

During Business deletion lifecycle:

* historical access follows Backend lifecycle;
* deleted Business history must not appear in normal application state;
* stale cache must not resurrect deleted records.

---

# 75. Audit Immutability

The UI must not provide:

* edit audit;
* delete audit;
* overwrite event;
* modify actor;
* modify timestamp;
* modify before/after state.

---

# 76. History Immutability

Historical records must be displayed as read-only.

Correction creates new historical state.

It does not rewrite the previous record.

---

# 77. Current State vs Historical State

Entity pages should clearly distinguish:

```text id="a5k8q2"
Current State

vs

Historical State
```

The current Product price must not be displayed as the historical price of an old event.

---

# 78. Historical Snapshot

When viewing an old event, the UI should use the snapshot supplied by Backend.

It should not dynamically populate historical fields from current entity data if that would alter historical meaning.

---

# 79. Historical Entity Detail

Where supported, the user may select:

**View entity as of this event**

The Backend must provide the historical state.

The Frontend must not attempt to reconstruct it from current state alone.

---

# 80. History Timeline

Entity history may use a timeline:

```text id="u7m3q9"
2026-10-05 18:42
Price changed
30,000 → 32,000
        ↓
2026-10-05 19:10
Product disabled
        ↓
2026-10-06 09:00
Product reactivated
```

Timeline entries remain immutable.

---

# 81. Timeline Accessibility

Timeline must provide a semantic alternative for screen readers.

Each event should have:

* date;
* action;
* actor;
* result;
* relevant details.

---

# 82. Audit Table

Audit table columns may include:

```text id="w3k7p9"
Date
Category
Action
Actor
Branch
Entity
Result
```

Technical identifiers may be available through detail view.

---

# 83. History Table

History table may include:

```text id="q8m2v5"
Date
Version
Change
Actor
Status
```

The exact columns depend on entity type.

---

# 84. Column Customization

Users may customize non-critical table columns where supported.

Mandatory audit context columns should not be hidden if they are required for understanding the record.

---

# 85. Empty State

Example:

```text id="f2p8n4"
No history is available for this entity.
```

This is not automatically an error.

---

# 86. Error State

Example:

```text id="r5q1m8"
History could not be loaded.
Try again.
```

The rest of the entity page should remain usable where possible.

---

# 87. Permission Error

If the user cannot access history:

```text id="m8k3q2"
You do not have permission to view this history.
```

The UI must not reveal restricted historical details.

---

# 88. Network Error

The UI may show cached safe history if available.

It must clearly indicate stale state.

---

# 89. Unknown Result

Read requests generally do not create unknown business state.

For export or action requests where the result is unknown:

The Frontend must reconcile using the operation identifier before retry.

---

# 90. Offline History

Previously cached history may be viewable offline if:

* authorized;
* locally available;
* not expired;
* properly protected.

The UI must show:

```text id="n4w7c2"
Offline — historical data may be stale.
```

---

# 91. Offline Audit Queries

New authoritative audit queries normally require online access.

The Frontend must not fabricate current audit results from incomplete local information.

---

# 92. Synchronization

Audit/history synchronization may include:

* audit events;
* history changes;
* read metadata where applicable;
* correction state.

Transactional synchronization remains higher priority.

---

# 93. Audit Sync Priority

The Frontend should not block POS operations while audit/history synchronization is running.

Audit synchronization should run through the normal background synchronization architecture.

---

# 94. Audit Event Arrival

If new audit events arrive while the Audit Center is open:

The UI may show:

```text id="x8m2q4"
5 new events
Refresh
```

Automatic insertion may be avoided when it would unexpectedly move the user's current table position.

---

# 95. History Refresh

When viewing an entity history:

The UI may show a refresh indicator if newer events are available.

---

# 96. Real-Time Audit Updates

Realtime audit updates may be used for:

* security events;
* critical system events;
* administrative monitoring.

Ordinary history does not necessarily require realtime updates.

---

# 97. Notification Integration

Important audit/security events may also produce notifications.

Example:

```text id="c4n7m2"
Security Alert
A device was revoked.

View Audit Event
```

The notification deep link must preserve authorization.

---

# 98. Dashboard Integration

Dashboard may expose:

* recent critical audit events;
* security alerts;
* important configuration changes.

The dashboard should not display the entire audit history.

---

# 99. Search Performance

Audit/history search should remain responsive.

Recommended Frontend targets:

* normal search result rendering p95 ≤500ms after API response;
* detail rendering p95 ≤300ms after API response;
* local filter interaction p95 ≤100ms.

Backend search SLOs remain authoritative.

---

# 100. Performance Targets

The Frontend should target:

| Operation                              |          Target |
| -------------------------------------- | --------------: |
| Audit Center initial interactive       |      p75 ≤ 2.0s |
| History tab initial interactive        |      p75 ≤ 1.5s |
| Audit list render after API response   |     p95 ≤ 500ms |
| History list render after API response |     p95 ≤ 500ms |
| Audit detail render                    |     p95 ≤ 300ms |
| History detail render                  |     p95 ≤ 300ms |
| Local filter feedback                  |     p95 ≤ 100ms |
| Pagination feedback                    |     p95 ≤ 100ms |
| Search result render                   |     p95 ≤ 500ms |
| Critical security event UI update      |            ≤ 2s |
| Audit export acknowledgement           |        p95 ≤ 1s |
| Fatal Audit/History UI error rate      | < 0.1% sessions |

---

# 101. Large History Handling

Large audit histories must use:

* cursor pagination;
* bounded page size;
* virtualized rendering where required;
* server-side filtering;
* server-side sorting.

---

# 102. No Full History Loading

The Frontend must never load an entire Business audit history into browser memory.

---

# 103. Cache

Audit/history cache may be used for:

* recently opened history;
* entity detail;
* safe filter metadata.

Cache must remain:

* Business-scoped;
* Branch-aware;
* permission-aware;
* bounded;
* non-authoritative.

---

# 104. Cache Invalidation

History cache should be invalidated when:

* a newer event arrives;
* entity context changes;
* Branch changes;
* Business changes;
* permission changes;
* lifecycle state changes.

---

# 105. Cache Security

Sensitive history should not remain accessible after permission removal.

Permission/context changes must invalidate or block cached access.

---

# 106. Business Isolation

Changing Business must:

1. clear incompatible audit/history state;
2. invalidate cache;
3. reload authorized filters;
4. reload report/history definitions;
5. reload data.

---

# 107. Branch Isolation

Changing Branch must:

1. update Branch context;
2. invalidate Branch-scoped history;
3. reload authorized events;
4. prevent stale Branch data from remaining visible.

---

# 108. Permission Changes

If an employee loses audit permission while viewing Audit Center:

* current access must be revalidated;
* restricted data must no longer be accessible;
* cached sensitive details must not remain available through navigation.

---

# 109. Employee Deactivation

Inactive employees must not perform new audit/history actions requiring active authorization.

Historical actor information remains unchanged.

---

# 110. Accessibility

Audit and History UI must support:

* keyboard navigation;
* semantic tables;
* accessible timeline;
* focus management;
* readable before/after differences;
* screen-reader labels;
* sufficient contrast;
* reduced motion.

---

# 111. Before/After Accessibility

Changes should not rely only on color.

Example:

```text id="x7m4q2"
Old value: 30,000
New value: 32,000
```

Labels such as:

* Previous;
* New;
* Added;
* Removed

should be available.

---

# 112. Keyboard Navigation

Users must be able to:

* filter;
* search;
* open event;
* navigate pages;
* inspect details;
* expand before/after;
* export.

---

# 113. Mobile Audit UI

Mobile should prioritize:

* event;
* actor;
* timestamp;
* Branch;
* result.

Technical metadata may be placed in expandable sections.

---

# 114. Desktop Audit UI

Desktop may use:

* wide audit table;
* detail drawer;
* split view;
* timeline.

The exact layout follows the Design System.

---

# 115. Audit Detail Drawer

A drawer may provide quick inspection without leaving the audit table.

However, deep technical details may use a dedicated detail page.

---

# 116. History Detail

Entity history should preserve the user's context.

Opening a historical event should not unexpectedly change the active Business or Branch.

---

# 117. Deep Links

History and audit entries may be directly linked.

The route must validate:

* authentication;
* Business;
* Branch;
* permission;
* entity existence;
* lifecycle.

---

# 118. URL Security

URLs must not contain unnecessary:

* personal data;
* salary;
* financial secrets;
* authentication data.

Entity IDs are navigation identifiers only.

---

# 119. Export Workflow

Export follows:

```text id="p8m3q6"
Audit/History
     ↓
Export Request
     ↓
Background Job
     ↓
File Generated
     ↓
Ready
     ↓
Download
```

Large exports must not block the UI.

---

# 120. Export Status

Possible states:

```text id="c5q8m2"
REQUESTED
PROCESSING
READY
FAILED
EXPIRED
```

Backend remains authoritative.

---

# 121. Export Download Security

Before download:

* authorization is checked;
* Business scope is checked;
* Branch scope is checked;
* export state is checked.

Expired or unauthorized files must not be downloaded.

---

# 122. Audit Export Audit

Exporting Audit/History data may itself produce an:

```text id="j4w8n2"
EXPORT_AUDIT
```

event.

The Frontend must not suppress or bypass this.

---

# 123. State Management

Audit/History state should distinguish:

* current scope;
* filters;
* query;
* events;
* detail;
* loading;
* error;
* freshness;
* export;
* synchronization.

---

# 124. Server State

Audit/history records should be managed as server state.

Examples:

* query cache;
* cursor pagination;
* invalidation;
* refetch.

---

# 125. Local UI State

Local state may include:

* selected event;
* expanded before/after;
* technical metadata visibility;
* table density;
* column visibility;
* filter drawer.

---

# 126. Historical Data State

Historical state must never be stored as mutable application state that can accidentally overwrite the current entity.

---

# 127. API Contract

The Frontend should use explicit contracts for:

* audit list;
* audit detail;
* history list;
* history detail;
* correction chain;
* export;
* filters;
* pagination.

---

# 128. API Evolution

API changes must preserve:

* event identity;
* actor identity;
* timestamps;
* scope;
* historical values;
* version identity.

---

# 129. Feature Flags

Feature flags may control:

* new history timeline;
* advanced filters;
* comparison UI;
* new audit visualization.

Feature flags cannot bypass:

* authorization;
* Business isolation;
* Branch isolation;
* audit immutability.

---

# 130. Testing Strategy

### Unit Tests

Test:

* event formatting;
* severity/result formatting;
* before/after transformation;
* filter state;
* pagination;
* cache keys;
* permission visibility.

### Component Tests

Test:

* audit table;
* history timeline;
* event detail;
* before/after view;
* correction chain;
* export controls.

### Integration Tests

Test:

* Business switching;
* Branch switching;
* permission changes;
* search;
* pagination;
* detail navigation;
* export.

### End-to-End Tests

Test:

* authorized Audit Center access;
* unauthorized access;
* Product history;
* Order history;
* Cash history;
* correction chain;
* export;
* offline cached history;
* reconnect;
* deleted Business.

---

# 131. Security Tests

Verify:

* cross-Business access is impossible;
* cross-Branch unauthorized history is impossible;
* restricted payroll history is protected;
* security audit is restricted;
* audit export authorization works;
* historical data cannot be modified through UI;
* deep links cannot bypass permission checks.

---

# 132. Historical Integrity Tests

Verify:

* historical price remains unchanged;
* historical Order Item remains unchanged;
* Recipe Version remains unchanged;
* Cash Session history remains unchanged;
* correction creates new event;
* old event remains visible;
* current state does not replace historical state.

---

# 133. Race Condition Tests

Test:

```text id="m7q2p9"
History Request A → Branch A
History Request B → Branch B

B completes first
A completes later
```

The stale A response must not overwrite Branch B state.

---

# 134. Realtime Tests

Test:

* duplicate events;
* out-of-order events;
* missed events;
* reconnect;
* new event while detail is open;
* Business switch during event delivery;
* Branch switch during event delivery.

---

# 135. Offline Tests

Test:

* cached history;
* stale indicator;
* permission removal;
* Business switch;
* Branch switch;
* reconnect;
* deleted Business;
* expired local data.

---

# 136. Observability

Frontend metrics should include:

* Audit Center load latency;
* History load latency;
* search latency;
* detail rendering latency;
* export failures;
* synchronization failures;
* authorization failures;
* stale cache usage;
* fatal UI errors.

Sensitive historical content must not be logged.

---

# 137. Error Classification

Errors should be classified as:

```text id="q8m4v1"
Validation Error
Authorization Error
Not Found
Conflict
Network Error
Timeout
Server Error
Synchronization Error
Unknown Result
```

---

# 138. Retry

Safe read operations may retry.

Export operations must respect operation identity.

Historical data must never be modified through automatic retry.

---

# 139. AI-Agent Development Rules

AI agents modifying Audit/History UI must:

1. read this document;
2. read Frontend Architecture;
3. read Business and Branch Context;
4. read Backend Audit and History Architecture;
5. read Database Audit and History Data Model;
6. read API contracts;
7. preserve immutable history;
8. preserve actor attribution;
9. preserve Business/Branch isolation;
10. preserve sensitive-data restrictions;
11. add tests;
12. update documentation.

---

# 140. Forbidden Frontend Patterns

The following are prohibited:

* editing audit events;
* deleting audit events;
* overwriting historical state;
* replacing historical actor with current actor;
* replacing historical price with current price;
* reconstructing authoritative history from current state;
* treating current configuration as historical truth;
* exposing restricted audit records;
* trusting URL IDs for authorization;
* loading unlimited history;
* storing unrestricted sensitive audit data;
* silently hiding historical corrections;
* silently resolving conflicts;
* using audit data as permission authority.

---

# 141. Recommended Feature Structure

```text id="w5q8m2"
frontend/
└── src/
    └── features/
        └── audit/
            ├── pages/
            ├── components/
            ├── queries/
            ├── filters/
            ├── history/
            ├── details/
            ├── corrections/
            ├── exports/
            ├── synchronization/
            └── types/
```

Entity-specific history may remain within its feature:

```text id="c7m3p8"
features/
├── products/
│   └── history/
├── orders/
│   └── history/
├── cash/
│   └── history/
├── inventory/
│   └── history/
├── employees/
│   └── history/
└── payroll/
    └── history/
```

Central Audit Center remains responsible for cross-entity audit browsing.

---

# 142. Dependency Rules

The Frontend must follow:

```text id="r8m2q5"
Audit Pages
   ↓
Audit Components
   ↓
Queries / Mutations
   ↓
API Contracts
```

Entity-specific history should remain owned by the corresponding feature.

Shared history components must not contain Business-specific rules.

---

# 143. Feature Boundary

Audit/History Frontend owns:

* presentation;
* filtering;
* searching;
* pagination;
* historical navigation;
* before/after visualization;
* correction-chain visualization;
* export interaction.

Backend owns:

* event creation;
* immutable persistence;
* historical truth;
* actor attribution;
* authorization;
* audit integrity;
* correction creation;
* retention;
* lifecycle.

---

# 144. System Invariants

The following invariants apply to Audit and History UI:

1. Audit records are read-only.
2. History records are read-only.
3. Backend is authoritative.
4. Audit identity is stable.
5. Operation identity is stable where provided.
6. Actor identity comes from historical data.
7. Historical actor must not be replaced by current employee data.
8. Historical timestamps are immutable.
9. Historical Branch context is preserved.
10. Historical Business context is preserved.
11. Historical device context is preserved where available.
12. Historical Cash Session context is preserved where available.
13. Historical Order context is preserved where available.
14. Before state is immutable.
15. After state is immutable.
16. Correction creates new history.
17. Correction does not erase original history.
18. Audit events cannot be edited from UI.
19. Audit events cannot be deleted from UI.
20. History cannot be silently overwritten.
21. Current state does not replace historical state.
22. Current Product price cannot reinterpret historical price.
23. Current Recipe cannot reinterpret historical Recipe Version.
24. Current employee role cannot reinterpret historical actor role.
25. Current Branch assignment cannot reinterpret historical Branch.
26. Business isolation is mandatory.
27. Branch isolation is mandatory.
28. Permission checks are mandatory.
29. Security audit requires restricted access.
30. Sensitive payroll history requires restricted access.
31. Sensitive financial history requires restricted access.
32. Export requires authorization.
33. Export may create audit records.
34. Audit export is itself auditable where required.
35. Deep links cannot bypass authorization.
36. URL identifiers are not authorization.
37. Audit search respects scope.
38. History search respects scope.
39. Pagination is mandatory for large history.
40. Unlimited history loading is prohibited.
41. Cursor pagination is preferred where supported.
42. Cache is non-authoritative.
43. Cache is Business-isolated.
44. Branch cache is Branch-isolated.
45. Permission changes invalidate restricted cache.
46. Business switching invalidates incompatible cache.
47. Branch switching invalidates incompatible cache.
48. Deleted Business data cannot be resurrected from cache.
49. Offline history is clearly marked as potentially stale.
50. Offline audit queries do not fabricate current server state.
51. Reconnection reconciles stale data.
52. Transaction synchronization has priority over audit/history synchronization.
53. Audit synchronization does not block POS operations.
54. Realtime events are deduplicated.
55. Realtime event order is not assumed to equal creation order.
56. Backend timestamps remain authoritative.
57. Empty history is not an error.
58. Loading state is distinct from empty state.
59. Permission error is distinct from not found.
60. Network error is distinct from empty state.
61. Historical detail uses authoritative snapshots.
62. Frontend does not reconstruct authoritative history from current data.
63. Before/after values are Backend-provided.
64. Sensitive values are masked where required.
65. Secrets are never displayed.
66. Technical metadata may be restricted.
67. System actors are clearly identified.
68. Background actors are clearly identified.
69. Offline source is clearly identified.
70. Synchronization result is clearly identified.
71. Correction chain is traceable.
72. Correction limit is Backend-authoritative.
73. History timeline is chronological according to authoritative timestamps.
74. Audit sorting is deterministic.
75. Search results remain scope-safe.
76. Historical exports preserve selected report/version context.
77. Export files require authorization at download time.
78. Expired exports cannot be downloaded.
79. Sensitive audit data is not unnecessarily logged.
80. Audit UI must remain responsive.
81. Large history must not freeze the browser.
82. Audit queries must not block POS.
83. Charts/timelines do not replace required exact values.
84. Accessibility is required.
85. Color is not the only indicator.
86. Before/after changes have textual meaning.
87. Keyboard navigation is supported.
88. Screen-reader users can understand history.
89. Mobile history remains readable.
90. Desktop history supports efficient investigation.
91. Feature flags cannot bypass audit security.
92. Feature flags cannot bypass Business isolation.
93. Feature flags cannot bypass Branch isolation.
94. Notification links to audit require authorization.
95. Dashboard audit widgets require authorization.
96. Permission changes must immediately affect UI access.
97. Deactivated employees cannot perform new restricted actions.
98. Subscription read-only does not allow historical modification.
99. Deletion lifecycle cannot be bypassed through history URLs.
100. Audit data cannot become permission authority.
101. History data cannot become transaction authority.
102. Audit data cannot become financial authority.
103. AI agents must preserve immutable history.
104. AI agents must preserve actor attribution.
105. AI agents must preserve Business isolation.
106. AI agents must preserve Branch isolation.
107. AI agents must preserve permission boundaries.
108. AI agents must preserve sensitive-data restrictions.
109. AI agents must add tests for history changes.
110. AI agents must update documentation for architecture changes.
111. Historical integrity has priority over UI convenience.
112. Auditability has priority over silent correction.
113. Correction must remain traceable.
114. Historical state must remain reconstructable.
115. Audit and History UI must remain simple for ordinary users.
116. Technical complexity must remain behind progressive disclosure.
117. Important changes must remain easy to investigate.
118. Historical records must remain trustworthy.
119. Audit data must remain attributable.
120. Audit and History Frontend must preserve the integrity of the overall ERP system.

---

# 145. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/15_Attendance_and_Payroll_UI.md`
* `docs/04_Architecture/07_Frontend/16_Reports_and_Dashboard_UI.md`
* `docs/04_Architecture/07_Frontend/17_Notifications_and_Alerts_UI.md`

### Backend

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/29_Database_Security.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 146. Status

**Document Status:** Proposed

**Version:** 1.0

**Document:** `18_Audit_and_History_UI.md`

**Previous Document:** `17_Notifications_and_Alerts_UI.md`

**Next Document:** `19_Subscription_and_Entitlement_UI.md`

