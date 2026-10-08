# Frontend Architecture

**Document ID:** ARCH-05
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the frontend architecture of FastFood ERP.

The frontend provides the user interface for:

* POS operations;
* order management;
* cash sessions;
* inventory;
* menu and pricing;
* employees and permissions;
* payroll;
* reports;
* notifications;
* configuration;
* synchronization;
* offline operation.

The frontend must provide a simple and fast user experience while preserving the security and architectural boundaries enforced by the backend.

The frontend is not the source of truth for business rules.

---

# 2. Frontend Architecture Principles

The frontend follows these principles:

1. **Backend authority**
2. **Feature-based organization**
3. **Permission-aware UI**
4. **Branch-aware UI**
5. **Offline-first where required**
6. **Fast POS interaction**
7. **Minimal unnecessary network requests**
8. **Clear state ownership**
9. **Predictable navigation**
10. **Reusable UI components**
11. **Explicit API contracts**
12. **Historical integrity**
13. **No business-rule duplication**
14. **Responsive operation**
15. **Graceful failure**
16. **Testability**
17. **Accessibility where practical**

The frontend should remain simple even when the backend domain model is complex.

---

# 3. Frontend Architectural Position

The frontend communicates with the backend through defined API contracts.

Conceptually:

```text id="q4f1mx"
User
  ↓
Frontend UI
  ↓
Frontend Application Logic
  ↓
API Client / Offline Client
  ↓
Backend API
  ↓
Application Layer
  ↓
Domain Layer
```

The frontend must not communicate directly with the database.

---

# 4. Frontend Responsibilities

The frontend is responsible for:

* displaying application state;
* collecting user input;
* local form validation;
* navigation;
* permission-aware visibility;
* branch selection;
* device status;
* offline status;
* synchronization status;
* local drafts where supported;
* API communication;
* optimistic UI only where safe;
* displaying errors;
* displaying notifications;
* managing user interaction state.

The frontend is not responsible for authoritative business decisions.

---

# 5. Frontend Must Not

The frontend must not be treated as the authoritative source for:

* permissions;
* subscription entitlement;
* inventory availability;
* payment validity;
* cash session validity;
* order acceptance;
* refund authorization;
* payroll authorization;
* data deletion;
* synchronization conflict resolution.

The backend must validate all important operations.

---

# 6. Application Structure

The frontend should be organized by business feature rather than only by technical type.

A conceptual structure is:

```text id="s1f2x9"
frontend/
├── app/
├── core/
├── shared/
├── features/
│   ├── authentication/
│   ├── dashboard/
│   ├── orders/
│   ├── cash/
│   ├── inventory/
│   ├── menu/
│   ├── kitchen/
│   ├── payments/
│   ├── employees/
│   ├── payroll/
│   ├── reports/
│   ├── notifications/
│   ├── audit/
│   ├── synchronization/
│   ├── configuration/
│   └── devices/
└── offline/
```

The exact framework may be selected separately.

---

# 7. App Shell

The App Shell provides the common application structure.

It may contain:

```text id="2wq8sn"
App Shell
├── Top Bar
├── Business Context
├── Branch Context
├── Navigation
├── Notification Area
├── Sync Status
├── Main Content
└── Global Error Area
```

The App Shell should remain lightweight.

POS screens may use a specialized layout optimized for speed.

---

# 8. Navigation Architecture

Navigation is permission-aware.

A navigation item should be displayed only when the user may reasonably access the corresponding feature.

However:

```text id="v0f9mb"
Hidden Navigation
        ≠
Security
```

The backend must still enforce authorization.

---

# 9. Navigation Scope

Navigation may depend on:

* Employee role;
* Employee permissions;
* Branch scope;
* Subscription entitlement;
* feature availability;
* application state.

Example:

```text id="q4m7wy"
Owner
 ├── Dashboard
 ├── Orders
 ├── Inventory
 ├── Employees
 ├── Payroll
 ├── Reports
 └── Configuration

Cashier
 ├── POS
 ├── Orders
 └── Cash Session
```

The exact navigation is permission-driven rather than hard-coded by role name.

---

# 10. Role and Permission UI

The frontend should use effective permissions supplied by the backend.

Conceptually:

```text id="9br6a8"
Role Permission
      +
Employee Override
      +
Branch Scope
      +
Subscription Entitlement
      ↓
Effective Permission
```

The frontend consumes the resulting authorization context.

It must not independently recreate the complete permission algorithm.

---

# 11. Permission-Aware Components

Components may receive permission state.

Examples:

```text id="u6qk2x"
canCreateOrder
canModifyOrder
canRefund
canAdjustInventory
canManageEmployees
canViewPayroll
canViewReports
```

A permission-aware component may:

* display;
* hide;
* disable;
* require confirmation.

The backend remains authoritative.

---

# 12. Branch Context

The active Branch is part of the frontend application context.

The frontend should clearly display:

```text id="9y4z5u"
Business
Branch
Employee
Device
```

The active branch must not be ambiguous during operational work.

---

# 13. Branch Switching

Branch switching must be explicit.

When a user switches branches, the frontend should:

1. validate the selected branch;
2. update active context;
3. refresh effective permissions;
4. refresh branch configuration;
5. refresh relevant menu/pricing;
6. refresh operational state;
7. update offline authorization where applicable.

A branch switch must not silently retain stale branch-specific state.

---

# 14. Branch Switch During Active Work

If the user is inside a sensitive workflow, the frontend should prevent accidental context changes.

Examples:

* active payment;
* cash session transition;
* order modification;
* inventory adjustment.

The UI should either:

* finish the operation;
* safely cancel the local operation;
* request confirmation before switching.

The backend remains the final authority.

---

# 15. Business Context

A user normally belongs to one active Business context.

All frontend API requests must carry or derive the correct Business context.

The frontend must not allow arbitrary Business UUID changes through user-editable fields.

Business context is established from authenticated application state.

---

# 16. Authentication UI

Authentication is separate from authorization.

The frontend handles:

* login;
* session state;
* logout;
* authentication errors;
* re-authentication where required;
* device registration flow.

The frontend must not store sensitive credentials unnecessarily.

---

# 17. Session State

Frontend session state may contain:

```text id="0h7z5f"
Authenticated Employee
Business Context
Active Branch
Effective Permissions
Subscription State
Device State
Offline Authorization State
```

Only the minimum required information should be kept locally.

---

# 18. Device State

The frontend must expose the relevant device status.

Examples:

```text id="3bq4c9"
Trusted
Pending Registration
Revoked
Offline Authorized
Offline Authorization Expired
```

A revoked device must not appear as available for offline operation.

---

# 19. POS Architecture

POS is the highest-priority frontend workflow.

The POS interface must optimize:

* speed;
* large touch targets;
* keyboard/mouse operation;
* minimal navigation;
* clear totals;
* quick product selection;
* quick quantity changes;
* quick payment;
* clear order status;
* offline continuity.

The POS must not inherit unnecessary complexity from administrative screens.

---

# 20. POS Layout

A conceptual POS layout is:

```text id="y8p1qa"
┌───────────────────────────────────────────┐
│ Branch | Cashier | Session | Connection  │
├───────────────────┬───────────────────────┤
│ Product / Menu    │ Current Order         │
│                   │                       │
│ Categories        │ Items                 │
│ Products          │ Quantity              │
│                   │ Modifiers             │
│                   │ Total                 │
├───────────────────┴───────────────────────┤
│ Order Type | Table | Payment | Actions    │
└───────────────────────────────────────────┘
```

The exact visual design may change.

The interaction model should remain simple.

---

# 21. Order Type UI

Current order types:

* Hall / Dine-in;
* Takeaway.

Phone Delivery remains future scope.

The frontend should not expose unsupported order types as active operational options.

---

# 22. Table UI

For Dine-in operations, the frontend should clearly show:

```text id="3s7k9d"
Available
Busy
```

Where required, table information may include:

* table number;
* hall;
* active visit;
* open orders;
* primary waiter;
* current operational state.

Paid historical orders must not make a table appear Busy.

---

# 23. Order Draft

Draft orders are local working state.

Draft behavior:

* fully editable;
* no inventory deduction;
* no kitchen notification;
* no table occupancy;
* no payment;
* no operational acceptance.

The frontend may autosave draft state locally for active UI continuity.

However, a draft is not guaranteed to survive device restart.

---

# 24. Order Acceptance UI

The frontend should clearly distinguish:

```text id="6x8r0j"
Draft
```

from:

```text id="g5t2p1"
Accepted
```

Acceptance is a server-authoritative business operation.

The frontend must not mark an order as Accepted before successful backend confirmation.

---

# 25. Order Acceptance Failure

If the backend rejects acceptance because stock is insufficient:

```text id="v6f0qk"
Order remains Draft
```

The frontend must display the relevant failure without corrupting the order.

Possible causes include:

* insufficient stock;
* invalid table state;
* permission failure;
* subscription restriction;
* concurrency conflict;
* device authorization failure.

---

# 26. Accepted Order UI

After acceptance, the frontend should show:

* order number;
* order UUID where appropriate internally;
* order type;
* table;
* waiter;
* status;
* payment state;
* items;
* totals;
* relevant kitchen state.

The UI must distinguish operational status from payment status.

---

# 27. Order Status UI

Current operational lifecycle:

```text id="k2s7m1"
Draft
  ↓
Accepted
  ↓
Preparing
  ↓
Ready
  ↓
Served
```

There is no `Completed` order state.

Payment status is displayed separately.

---

# 28. Accepted Order Modification

The frontend should distinguish:

### Existing Item Modification

An existing accepted order item may be modified according to permission and backend rules.

### New Product

Adding a new product after acceptance creates a separate operational order/ticket linked to the original order context.

The UI must not incorrectly merge a new operational ticket into the original accepted transaction.

---

# 29. Inventory Return Prompt

When reducing or removing an accepted item, the UI may ask:

```text id="z0h7nd"
Return inventory?
```

The backend remains authoritative.

If the user chooses to return inventory:

* backend validates;
* inventory is returned;
* modification succeeds only if the complete transaction succeeds.

If the user chooses not to return inventory:

* order modification follows the corresponding business rule;
* the decision is recorded.

---

# 30. Payment UI

Payment should be a focused workflow.

Supported methods:

* Cash;
* Card;
* Debt;
* Mixed.

The UI must clearly show:

```text id="8h1xk0"
Order Total
Paid
Remaining
Payment Method
Amount
Change / Overpayment
```

---

# 31. Partial Payment

The frontend should show:

```text id="x6f8ap"
Total:       100
Paid:         60
Remaining:    40
```

The order is not fully paid until the total amount is settled.

---

# 32. Mixed Payment

Mixed payment allows multiple payment portions.

Example:

```text id="u4q2mz"
Cash:  60
Card:  40
--------------
Total: 100
```

The backend stores the logical payment and its portions.

The frontend should not create multiple independent orders for split payment.

---

# 33. Cash Payment and Change

The cashier enters the amount received.

The frontend calculates the expected change for usability.

The backend validates the final financial operation.

If the customer gives more than the order total, the frontend must clearly display the excess and request confirmation where required.

---

# 34. Overpayment UI

Overpayment should be clearly distinguished from ordinary change.

Example:

```text id="z4v6p0"
Order Total:      90
Customer Gives:  100
Excess:           10
```

After confirmation, the backend records the excess according to the financial rules.

Reports retain attribution to the relevant cashier and waiter where applicable.

---

# 35. Debt Payment UI

Debt operations should show:

* customer identity;
* phone;
* outstanding balance;
* selected debt orders;
* repayment amount;
* remaining balance.

The frontend must not expose customers outside the authorized Business context.

---

# 36. Refund UI

Refunds require explicit permission.

The UI should require:

* refund type;
* amount/item/quantity;
* refund method;
* reason;
* confirmation.

Refunds are separate financial operations.

The frontend must not assume that refund automatically returns inventory.

---

# 37. Cash Session UI

Cash Session screens should clearly display:

```text id="n2h7q0"
Register
Cashier
Session
Opening Cash
Expected Cash
Actual Cash
Difference
Status
```

Expected cash should remain hidden until the cashier has entered the physical cash count where required.

---

# 38. Cash Session Close

Closing flow:

```text id="9k4f3m"
Close Session
    ↓
Enter Physical Cash
    ↓
Show Expected / Actual / Difference
    ↓
Comment if Required
    ↓
Confirm
    ↓
Backend Close
```

The frontend must not allow reopening a closed session as an active session.

---

# 39. Cash Handover UI

Handover should clearly distinguish:

```text id="w3g5p1"
Previous Session
```

from:

```text id="j7q9k2"
New Session
```

The physical register remains the same.

The new Cash Session receives a new UUID.

Open orders continue.

---

# 40. Handover Confirmation

The incoming cashier should see:

* opening cash amount;
* relevant handover information;
* active orders;
* register identity;
* new session information.

The previous session's discrepancy remains attributed to the previous session.

---

# 41. Inventory UI

Inventory screens should support:

* stock overview;
* low stock;
* out of stock;
* purchases;
* stock movements;
* adjustments;
* discrepancies;
* recipes;
* semi-finished products;
* warehouses.

The UI must distinguish current stock from historical movements.

---

# 42. Inventory Adjustment

Manual stock adjustment requires explicit permission.

The UI should require:

* product;
* quantity;
* direction;
* reason;
* comment;
* confirmation.

The backend validates the final operation.

---

# 43. Inventory Discrepancy

When a count differs from system stock, the frontend should first show:

```text id="p8y2s0"
System Quantity
Counted Quantity
Difference
```

The adjustment should occur only after authorized confirmation.

The original discrepancy remains in history.

---

# 44. Recipe UI

Recipe screens should support:

* raw materials;
* semi-finished products;
* finished products;
* quantities;
* proportions;
* recipe versions;
* approval state;
* effective version.

Historical recipes must remain accessible where permission allows.

---

# 45. Menu and Pricing UI

Menu screens should separate:

```text id="m4q6x2"
Product
Category
Price
Branch Availability
Recipe
Set
Status
```

Price changes must not rewrite historical orders.

The frontend should show effective/current versions clearly.

---

# 46. Set UI

Sets are separate from recipes.

A Set has:

* its own price;
* stable component composition;
* configuration/version;
* activation boundary.

The UI must not imply that Set components can be freely substituted during order entry.

---

# 47. Employee UI

Employee screens may include:

* employee list;
* status;
* branches;
* roles;
* permissions;
* overrides;
* attendance;
* salary configuration.

Employee history must remain available after deactivation.

---

# 48. Permission Management UI

Permission management should visually distinguish:

```text id="6t8p3q"
Role Permission
Employee Override
Branch Scope
```

The frontend should make the resulting effective permission understandable.

It must not allow a Manager to grant permissions beyond the Manager's own authority.

The backend enforces this rule.

---

# 49. Payroll UI

Payroll screens should include:

* employee;
* period;
* salary model;
* calculation;
* bonuses;
* status;
* finalization;
* correction history.

Finalized payroll must be treated as historical state.

Corrections should be separate operations.

---

# 50. Reports UI

Reports should provide:

* report type;
* period;
* branch scope;
* version;
* creation time;
* creator/system source;
* status;
* export action.

Report versions should be clearly distinguished.

---

# 51. Report Version UI

Example:

```text id="r3n8x1"
Sales Report
Period: August 2026

Version 1
Version 2
Version 3
```

Each version represents an immutable historical snapshot.

The frontend must not overwrite an existing report version.

---

# 52. Excel Export UI

Export states may include:

```text id="q1h6m9"
Requested
Processing
Ready
Failed
Expired
```

Large exports should execute in the background.

The POS should never wait for an Excel export.

---

# 53. Notification UI

Notifications may be:

* Info;
* Warning;
* Critical.

The frontend should show important notifications without blocking ordinary POS operations unless a separate business rule explicitly requires blocking.

Notifications are scoped to the user's authorized Business and Branch context.

---

# 54. Notification State

Per-recipient state may include:

```text id="d7v2k4"
Unread
Read
Resolved
Expired
Failed
```

Reading a notification does not delete its history.

---

# 55. Audit UI

Audit screens should support authorized filtering by:

* date;
* employee;
* branch;
* event;
* entity;
* transaction;
* device;
* Cash Session;
* source;
* result.

Audit records are read-only.

Export is permission-controlled and auditable.

---

# 56. Configuration UI

Configuration screens should clearly distinguish:

```text id="j4q8v6"
Draft
Pending Approval
Approved
Active
Inactive
Archived
```

The UI should show:

* current version;
* previous version;
* effective date/session;
* creator;
* approver;
* change reason.

---

# 57. Configuration Concurrency

If a user attempts to modify stale configuration:

```text id="m9x2q7"
Current Version: 8
User Loaded:    7
```

the frontend should notify the user that the configuration has changed.

The backend must reject unsafe stale updates.

The user may reload and retry.

---

# 58. Subscription UI

Subscription state should be visible to authorized users.

Possible states:

```text id="c8p5r1"
Active
Grace Period
Expired / Read-Only
Deletion Eligible
Deleting
Deleted
```

The frontend should show remaining time using server-provided authoritative timestamps.

---

# 59. Read-Only Mode

After subscription expiry, the frontend may enter read-only mode.

Allowed actions depend on backend policy and permission.

The UI should:

* disable modification controls;
* preserve data visibility;
* allow authorized reports;
* allow permitted Excel exports;
* show subscription status;
* show reactivation information.

The backend must enforce the restriction.

---

# 60. Offline Architecture

Offline support is a first-class frontend capability.

Conceptually:

```text id="0w6p8z"
UI
 ↓
Application State
 ↓
Local Persistence
 ↓
Offline Queue
 ↓
Synchronization Engine
 ↓
Backend API
```

Offline operation is only available to trusted authorized devices.

---

# 61. Local Storage

The frontend may persist:

* eligible operational data;
* configuration versions;
* offline authorization;
* pending synchronization events;
* local transaction results;
* required notification state.

Sensitive local data must be encrypted.

The exact storage technology is defined separately in technology architecture.

---

# 62. Offline Authorization

Offline authorization is provided by the backend.

The frontend verifies the locally available authorization package as required by the implementation.

It must enforce:

* expiry;
* device identity;
* Business;
* Branch;
* Employee;
* permission;
* subscription bounds.

Offline authorization must not be user-editable.

---

# 63. Offline UI Indicator

The application should always make connectivity state understandable.

Example:

```text id="x4p8k2"
● Online
● Offline
↻ Syncing
! Sync Conflict
✓ Synced
```

The indicator should not unnecessarily interrupt POS operation.

---

# 64. Offline Operation Rules

When offline:

* eligible operations continue;
* unsupported operations are clearly unavailable;
* local UUIDs are generated;
* operations enter the sync queue;
* local results are shown;
* synchronization occurs when connectivity returns.

The UI must never imply server confirmation before synchronization succeeds.

---

# 65. Sync Queue UI

The user should be able to see synchronization status where appropriate.

Example:

```text id="u5r9m3"
Pending:   8
Syncing:   2
Synced:   120
Conflict:  1
Failed:    0
```

The exact UI may be simplified for ordinary POS users.

Administrative users may receive more detailed information.

---

# 66. Synchronization Priority

The frontend should synchronize dependencies in the required order.

Example:

```text id="q6n2v8"
Order Creation
    ↓
Order Acceptance
    ↓
Payment
```

Configuration synchronization should not invalidate pending transaction dependencies.

Transaction synchronization has priority over configuration synchronization where required.

---

# 67. Sync Failure

Temporary network failure should not delete local pending operations.

The queue must remain durable.

The UI should indicate:

```text id="p7m4x1"
Waiting for connection
```

rather than showing the operation as lost.

---

# 68. Sync Conflict UI

A conflict should be clearly distinguishable from a technical failure.

Example:

```text id="z2k8q4"
Sync Conflict
Order #123
Reason: Current server state differs
Action: Review
```

Only authorized users may resolve conflicts.

---

# 69. Conflict Resolution UI

Conflict resolution should show enough information for an authorized user to make a decision.

Possible information:

* local state;
* server state;
* operation;
* timestamp;
* employee;
* device;
* affected entity;
* reason.

The resolution action must require appropriate permission.

---

# 70. Offline Drafts

Draft state may be stored locally for active UI continuity.

However:

* Draft does not reserve inventory;
* Draft does not occupy tables;
* Draft does not notify kitchen;
* Draft is not payment-ready until accepted.

If a device restart causes a draft to disappear, the system must not create an invalid operational record.

---

# 71. Offline Order Acceptance

When offline, the frontend may allow acceptance if:

* device is trusted;
* offline authorization is valid;
* employee is authorized;
* subscription bounds permit it;
* required local data exists.

The operation receives a UUID and enters the synchronization queue.

The server validates the transaction when synchronized.

---

# 72. Offline Payment

The frontend may record eligible offline payments.

It must distinguish:

```text id="n8y3p5"
ERP Payment Recorded Offline
```

from:

```text id="h6q1v9"
External Card Processor Authorization
```

An offline ERP record must not be presented as confirmed external card authorization unless such confirmation actually exists.

---

# 73. Offline Cash Session

Trusted devices may perform eligible cash operations offline.

The UI must maintain:

* Cash Session UUID;
* register identity;
* cashier identity;
* opening amount;
* cash operations;
* local transaction state.

Synchronization must preserve the original session UUID.

---

# 74. Offline Employee Status

If an employee becomes inactive on the server while a device is offline, the device may have stale local information.

The server must reject unauthorized post-deactivation operations during synchronization.

The frontend should then update local authorization state.

---

# 75. Offline Subscription Expiry

Offline authorization must have a bounded lifetime.

When it expires:

```text id="y2p8k5"
Offline Modification
        ↓
Blocked
```

The frontend should show that the device must reconnect for updated authorization.

The user must not be able to extend offline validity locally.

---

# 76. API Client Architecture

All backend communication should go through a centralized API client layer.

Conceptually:

```text id="g3q7m1"
Feature
  ↓
Application Service
  ↓
API Client
  ↓
HTTP Transport
  ↓
Backend
```

Features should not independently implement authentication headers, retry behavior, or error parsing.

---

# 77. API Client Responsibilities

The API client may handle:

* authentication metadata;
* request serialization;
* response parsing;
* correlation IDs;
* retry classification;
* network error detection;
* API version;
* common error mapping.

Business-specific decisions remain outside the transport layer.

---

# 78. API Error Handling

The frontend should map backend errors into user-understandable states.

Example:

```text id="x5v9q2"
Backend:
StockInsufficient

Frontend:
"Insufficient stock to accept this order."
```

Internal server details must not be shown to the user.

---

# 79. Optimistic UI

Optimistic updates should be used carefully.

Suitable examples:

* local navigation state;
* non-critical display state;
* notification read state where safely reversible.

Avoid optimistic assumptions for:

* payment completion;
* order acceptance;
* inventory deduction;
* cash session closing;
* refunds;
* payroll finalization.

For these, backend confirmation is required.

---

# 80. State Management

Frontend state should be separated conceptually into:

```text id="r8k3v5"
Server State
UI State
Session State
Local Operational State
Offline Queue State
```

These categories must not be mixed unnecessarily.

---

# 81. Server State

Server state includes:

* orders;
* inventory;
* employees;
* payments;
* reports;
* configuration;
* subscription;
* notifications.

The backend is authoritative.

The frontend may cache server state but must know when it becomes stale.

---

# 82. UI State

UI state includes:

* modal visibility;
* selected tab;
* form input;
* active dialog;
* sorting;
* filters;
* temporary selections.

UI state normally does not need persistence.

---

# 83. Session State

Session state includes:

* authenticated employee;
* Business;
* Branch;
* permission context;
* device state;
* subscription state.

Session state should be refreshed when authorization context changes.

---

# 84. Local Operational State

Local operational state may include:

* active order draft;
* temporary POS selections;
* unsent local operations;
* local sync status.

This state must follow offline persistence rules.

---

# 85. Component Architecture

Reusable components should be divided into:

```text id="v7m2p9"
Design Components
Business Components
Feature Components
Page Components
```

Examples:

### Design Components

* Button;
* Input;
* Modal;
* Table;
* Badge.

### Business Components

* MoneyDisplay;
* PermissionGuard;
* BranchSelector;
* OrderStatus;
* StockStatus.

### Feature Components

* OrderEditor;
* CashSessionPanel;
* RecipeEditor;
* PayrollCalculator.

---

# 86. Shared Components

Shared components must remain generic.

A shared component should not silently depend on a specific domain module.

Bad:

```text id="d1v6q4"
Shared Button
    ↓
Knows Cash Session Rules
```

Preferred:

```text id="s4k8n2"
Shared Button
    ↓
Generic UI Behavior
```

Business logic belongs to feature/application layers.

---

# 87. Forms

Forms should provide immediate local validation.

Examples:

* required fields;
* number ranges;
* valid UUIDs where applicable;
* valid dates;
* valid quantities.

However, successful local validation does not mean the operation is authorized or valid on the server.

---

# 88. Double Submission Protection

The frontend should prevent accidental duplicate submission.

For example:

```text id="p3q7x1"
Submit Payment
     ↓
Disable Submit
     ↓
Wait for Result
```

This improves UX.

However, frontend protection is not sufficient.

Backend idempotency remains required.

---

# 89. Loading States

Every asynchronous operation should have a clear state.

Examples:

```text id="y5m8q2"
Idle
Loading
Success
Error
Conflict
Retrying
```

The UI should avoid ambiguous states such as an action appearing permanently clickable while a request is still processing.

---

# 90. Error Recovery UI

Where retry is safe, provide a retry action.

Example:

```text id="m2q7v5"
Report Generation Failed

[Retry]
```

For business conflicts, provide a review/resolution path rather than blindly retrying.

---

# 91. Critical Operation Confirmation

Confirmation should be used for high-impact operations.

Examples:

* refund;
* cash session close;
* inventory adjustment;
* employee deactivation;
* permission changes;
* destructive lifecycle operations.

Routine POS actions should not be overloaded with unnecessary confirmation dialogs.

---

# 92. Accessibility

The frontend should support:

* keyboard navigation;
* visible focus;
* readable labels;
* sufficient contrast;
* clear status indicators;
* accessible form errors;
* appropriate touch targets.

POS-specific optimizations must not make basic interaction inaccessible.

---

# 93. Responsive Design

The administrative interface should support common:

* desktop;
* laptop;
* tablet

screen sizes.

POS should prioritize:

* standard office/POS monitors;
* keyboard/mouse;
* touch where available.

The frontend should not require high-end hardware.

---

# 94. Performance Architecture

Frontend performance priorities:

1. POS interaction speed;
2. fast initial navigation;
3. minimal unnecessary API requests;
4. efficient rendering;
5. controlled local storage;
6. background synchronization;
7. lazy loading of heavy administrative features.

Heavy report pages must not slow down POS pages.

---

# 95. Feature Loading

Large features may be loaded on demand.

Examples:

```text id="k8p4s2"
Reports
Payroll
Audit
Configuration
```

The POS interface should not need to load the complete administrative application before becoming usable.

---

# 96. Data Fetching

Frontend data fetching should use:

* explicit query keys;
* scoped Business/Branch context;
* controlled caching;
* invalidation after mutations;
* pagination.

After a successful mutation, only affected data should be refreshed where practical.

---

# 97. Cache Boundaries

Frontend cache must respect:

* Business;
* Branch;
* Employee;
* permission context;
* configuration version.

A cache entry from Branch A must never be reused as Branch B state.

---

# 98. Frontend Security

Frontend security measures include:

* secure session handling;
* protected routes;
* permission-aware UI;
* device status;
* safe local storage;
* encrypted offline data;
* controlled file access;
* no sensitive data in URLs where avoidable.

Frontend security is complementary to backend security.

It is not a replacement for server-side authorization.

---

# 99. Sensitive Data Handling

The frontend should minimize storage of:

* authentication secrets;
* sensitive employee information;
* financial information;
* protected configuration;
* offline authorization material.

Data stored locally must have a defined retention purpose.

---

# 100. Logout Behavior

Logout should clear the active frontend session.

If a Cash Session remains open:

```text id="f7x2m8"
Logout
  ↓
Cash Session remains Open
```

Logout must not automatically close the Cash Session.

The next authorized cashier performs the appropriate handover/new session process.

---

# 101. Reauthentication

Reauthentication may be required for sensitive operations depending on security policy.

Examples:

* privileged correction;
* employee permission changes;
* sensitive configuration;
* deletion-related actions.

Reauthentication must not be required for every ordinary POS operation unless explicitly justified.

---

# 102. Frontend Event Handling

The frontend may react to backend events through supported mechanisms.

Examples:

* notification received;
* synchronization result;
* session state change;
* configuration update.

Frontend events update presentation state.

They must not bypass backend authorization.

---

# 103. Real-Time Updates

Where real-time updates are required, the frontend may use:

* polling;
* server-sent events;
* WebSocket;
* another supported mechanism.

The choice is a technology decision.

Real-time communication must not become a second source of truth.

---

# 104. Offline and Online State Transition

The frontend must handle:

```text id="j6p3q9"
Online
  ↓
Network Lost
  ↓
Offline
  ↓
Network Restored
  ↓
Syncing
  ↓
Synced / Conflict / Failed
  ↓
Online
```

Transitions must not discard pending operations.

---

# 105. App Restart

After frontend restart:

* authenticated session should follow the selected authentication policy;
* pending offline operations must remain durable;
* sync queue must be restored;
* local configuration must remain version-aware;
* invalid offline authorization must not be reused.

---

# 106. Local Storage Failure

If encrypted local storage becomes unavailable or corrupted:

* the application must not silently fabricate state;
* pending operations must not be marked as synchronized;
* the user should receive a clear recovery message;
* safe recovery or re-registration should be required where necessary.

---

# 107. Frontend and Historical Integrity

The frontend must never modify historical records directly.

For example:

```text id="n4q8z2"
Original Payment
      ↓
Payment Revision / Correction
```

The UI should display the correction history rather than rewriting the original record.

The same principle applies to:

* cash sessions;
* inventory;
* reports;
* payroll;
* configuration;
* audit history.

---

# 108. Frontend and Subscription Lifecycle

The frontend should react to server-provided subscription state.

Example:

```text id="v9x4k6"
Active
   ↓
Grace Period
   ↓
Expired / Read-Only
   ↓
Deletion Eligible
```

The frontend must not independently calculate permanent deletion eligibility.

The backend remains authoritative.

---

# 109. Frontend and Data Deletion

When a Business is deleted:

* local authorization becomes invalid;
* local operational data must be cleaned according to policy;
* pending synchronization must not resurrect the Business;
* the frontend must block further access.

The frontend must not attempt to recreate deleted server state.

---

# 110. Frontend Testing

Testing should include:

### Component Tests

UI behavior and reusable components.

### Feature Tests

POS, inventory, payments, employees, reports.

### State Tests

Offline, synchronization, permissions, subscription states.

### Integration Tests

Frontend ↔ API contracts.

### End-to-End Tests

Critical business workflows.

---

# 111. Critical Frontend Test Scenarios

At minimum:

```text id="s8m3q7"
Login
Branch Switch
Permission Change
Order Creation
Order Acceptance
Order Modification
Payment
Mixed Payment
Overpayment
Refund
Cash Session Open
Cash Session Close
Cash Handover
Inventory Adjustment
Recipe Approval
Price Activation
Report Generation
Excel Export
Subscription Expiry
Offline Order
Offline Payment
Offline Cash Session
Sync Recovery
Sync Conflict
Device Revocation
```

---

# 112. Frontend Anti-Patterns

The following patterns are prohibited:

### Business Logic in UI Components

```text id="x3q7m9"
Button Click
    ↓
Complex Inventory Algorithm
```

### Frontend-Only Authorization

```text id="z6p2k8"
Hidden Button
    =
Authorized
```

### Direct Database Access

```text id="j5v8q1"
Frontend
    ↓
Database
```

### Uncontrolled Global State

```text id="m7q2x4"
Everything Stored in One Global Object
```

### Unscoped Cache

```text id="q9k3v6"
Branch A Data
    ↓
Branch B UI
```

### Silent Sync Conflict

```text id="b4x8n1"
Local Data
    ↓
Server Data
    ↓
Silent Overwrite
```

### Infinite Retry

```text id="r2v7m5"
Failed Request
    ↓
Retry Forever
```

---

# 113. Frontend Data Flow

Standard online operation:

```text id="u8m4q2"
User Action
    ↓
Feature Component
    ↓
Application/Feature Logic
    ↓
API Client
    ↓
Backend
    ↓
Response
    ↓
Server State Update
    ↓
UI Update
```

---

# 114. Frontend Offline Data Flow

Offline operation:

```text id="p6x3k8"
User Action
    ↓
Feature Component
    ↓
Local Validation
    ↓
Local Operational State
    ↓
Encrypted Local Storage
    ↓
Offline Queue
    ↓
Synchronization
    ↓
Backend Validation
    ↓
Synced / Conflict / Failed
    ↓
UI Update
```

---

# 115. Frontend Architecture Boundaries

The frontend must maintain the following boundaries:

| Responsibility                |        Frontend |       Backend |
| ----------------------------- | --------------: | ------------: |
| UI rendering                  |             Yes |            No |
| Navigation                    |             Yes |            No |
| Form validation               |             Yes |           Yes |
| Permission display            |             Yes |           Yes |
| Authorization                 |              No |           Yes |
| Business rules                |              No |           Yes |
| Inventory authority           |              No |           Yes |
| Payment authority             |              No |           Yes |
| Cash authority                |              No |           Yes |
| Subscription authority        |              No |           Yes |
| Offline queue                 |             Yes |           Yes |
| Synchronization validation    |              No |           Yes |
| Conflict presentation         |             Yes |           Yes |
| Conflict resolution authority |              No |           Yes |
| Historical integrity          |         Display |       Enforce |
| Audit creation                | Request/context | Authoritative |
| Report generation             | Request/display |           Yes |

---

# 116. Frontend Architecture Completion Criteria

The frontend architecture is considered complete when:

* feature boundaries are clear;
* navigation is permission-aware;
* Business and Branch context are explicit;
* POS is optimized for speed;
* order and payment state are separated;
* cash sessions are clearly represented;
* offline operation is supported where required;
* synchronization status is visible;
* conflicts are explicit;
* backend remains authoritative;
* local state is properly separated;
* cache is tenant/branch scoped;
* sensitive local data is protected;
* subscription read-only mode is supported;
* reports do not block POS;
* frontend tests cover critical workflows;
* the frontend can operate without requiring high-end hardware.

---

# 117. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`

### System Analysis

* `docs/02_System_Analysis/02_Application_Structure_and_Navigation.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`

### Domain Analysis

* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`

### Architecture

* `docs/04_Architecture/01_System_Architecture.md`
* `docs/04_Architecture/02_Application_Layer_Architecture.md`
* `docs/04_Architecture/03_Domain_Module_Architecture.md`
* `docs/04_Architecture/04_Backend_Architecture.md`

---

# 118. Next Architecture Document

The next architecture document is:

`docs/04_Architecture/06_API_Architecture.md`

It will define:

* API boundaries;
* endpoint organization;
* resource naming;
* command/query endpoints;
* request/response contracts;
* authentication;
* authorization;
* Business and Branch scoping;
* idempotency;
* pagination;
* filtering;
* API errors;
* versioning;
* offline synchronization API;
* report/export API;
* API security;
* API performance.

