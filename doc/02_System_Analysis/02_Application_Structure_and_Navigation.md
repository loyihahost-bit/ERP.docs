# Application Structure and Navigation

**Document ID:** SA-02
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the application structure and navigation behavior of FastFood ERP.

It establishes:

* the main application areas;
* navigation hierarchy;
* Business and Branch context;
* role-based visibility;
* permission-based access;
* operational versus administrative workflows;
* POS navigation principles;
* context preservation;
* unauthorized navigation behavior;
* navigation behavior during offline operation.

The goal is to keep a feature-rich ERP simple and fast for daily operational users while still providing complete management capabilities for authorized users.

---

## 2. Navigation Principles

The application must follow these principles:

1. Users see only functionality relevant to their permissions.
2. Business and Branch context must always be clear.
3. Daily operational workflows must require minimal navigation.
4. POS workflows must be optimized for speed.
5. Administrative functionality must not unnecessarily interfere with operational workflows.
6. Unauthorized features must not become accessible through direct URLs or manually constructed requests.
7. Frontend visibility is a usability mechanism, not the authoritative security mechanism.
8. Server-side authorization remains mandatory.
9. Navigation state must remain consistent after page refresh, reconnect or synchronization.
10. Offline mode must not expose functionality outside the device's authorized offline scope.

---

## 3. High-Level Application Structure

The application is logically divided into the following areas:

```text
FastFood ERP
│
├── Dashboard
│
├── POS
│   ├── Orders
│   ├── Tables
│   └── Active Operations
│
├── Sales
│   ├── Orders
│   ├── Payments
│   ├── Refunds
│   ├── Discounts
│   └── Debts
│
├── Cash
│   ├── Cash Register
│   ├── Current Session
│   ├── Handover
│   └── Cash Reports
│
├── Inventory
│   ├── Stock
│   ├── Warehouses
│   ├── Purchases
│   ├── Adjustments
│   ├── Inventory History
│   └── Shopping List
│
├── Products & Menu
│   ├── Products
│   ├── Recipes
│   ├── Sets
│   ├── Categories
│   ├── Menu
│   └── Pricing
│
├── Employees
│   ├── Employees
│   ├── Roles
│   ├── Permissions
│   ├── Attendance
│   └── Payroll
│
├── Reports
│
├── Notifications
│
├── Audit & History
│
└── Settings
    ├── Business
    ├── Branches
    ├── Devices
    ├── Subscription
    └── Configuration
```

The exact visible navigation depends on:

* employee permissions;
* branch scope;
* subscription entitlement;
* employee status;
* current operational context.

---

## 4. Application Context

After successful authentication, the application establishes the user's operational context.

The minimum context includes:

* Business;
* Employee;
* Branch scope;
* effective permissions;
* subscription entitlement;
* trusted device state.

Where relevant, the current context also includes:

* Cash Register;
* Cash Session;
* POS state;
* synchronization state.

Conceptually:

```text
Authentication
      ↓
Business Context
      ↓
Employee Context
      ↓
Branch Context
      ↓
Permissions
      ↓
Subscription Entitlement
      ↓
Application Navigation
```

---

## 5. Business Context

A user belongs to a Business context during normal operation.

All operational navigation must remain within that Business boundary.

The application must never rely on the client to determine the Business boundary.

The server establishes the authenticated Business context and validates every protected operation against it.

---

## 6. Branch Context

Branch context is required for branch-scoped operations.

A user with access to multiple branches may switch between permitted branches.

Example:

```text
Current Business
       │
       ├── Branch A
       ├── Branch B
       └── Branch C
```

After switching from Branch A to Branch B:

1. Branch-scoped data is refreshed.
2. Effective permissions are recalculated.
3. Branch-specific configuration is loaded.
4. Branch-specific menu state is loaded.
5. Branch-specific inventory is loaded.
6. Branch-specific cash context is loaded where applicable.
7. The UI must no longer display stale Branch A operational data.

Branch switching must not change the user's Business identity.

---

## 7. Branch Switching Rules

Branch switching is allowed only when the employee has access to the target Branch.

When branch switching occurs, the system must validate:

* employee status;
* Business membership;
* target Branch assignment;
* effective permissions;
* subscription entitlement.

A branch switch must not allow the employee to retain permissions that belong only to the previous Branch.

For example:

```text
Branch A
Manager Permission
      ↓
Switch to Branch B
      ↓
Recalculate Permissions
      ↓
Branch B Permission Set
```

The application must not simply reuse the previous branch's permission state.

---

## 8. Navigation Visibility

Navigation items are dynamically determined from the effective system context.

A feature may be visible only when:

* the employee has the required permission;
* the employee has the required branch scope;
* the feature is enabled by subscription;
* the employee is active;
* the feature is available in the current operational context.

Conceptually:

```text
Feature
  │
  ├── Permission?
  ├── Branch Scope?
  ├── Subscription?
  ├── Employee Active?
  └── Context Valid?
          │
          ▼
     Visible / Hidden
```

Hidden navigation is not considered an authorization mechanism.

The backend must still reject unauthorized requests.

---

## 9. Unauthorized Navigation

A user may attempt to access a protected route directly.

For example:

```text
User
 ↓
Direct URL / Protected API
 ↓
Authorization Check
 ↓
Unauthorized
```

The system must:

* reject the operation;
* avoid returning protected data;
* show an appropriate access-denied response;
* preserve application security.

The frontend should redirect the user to an appropriate permitted location when necessary.

---

## 10. Application Shell

The application shell should provide access to common system information without unnecessarily interrupting operational workflows.

Typical global elements include:

* current Business;
* current Branch;
* current Employee;
* notifications;
* synchronization state;
* device state;
* subscription/read-only status;
* account/session controls.

The application shell must remain lightweight for POS devices.

---

## 11. Operational Navigation vs Administrative Navigation

The application distinguishes between operational and administrative workflows.

### Operational

Examples:

* POS;
* orders;
* tables;
* payments;
* cash session;
* inventory operations.

These workflows prioritize:

* speed;
* minimal navigation;
* clear current state;
* large actionable controls where appropriate;
* low interaction overhead.

### Administrative

Examples:

* employee management;
* roles;
* recipes;
* reports;
* payroll;
* subscription;
* business configuration.

These workflows prioritize:

* detailed information;
* configuration;
* history;
* filtering;
* validation;
* auditability.

Administrative complexity must not unnecessarily propagate into POS workflows.

---

## 12. POS Navigation

POS is treated as a primary operational workspace.

A typical POS workflow is:

```text
POS
 ↓
Select Order Type
 ↓
Select Table if required
 ↓
Add Products
 ↓
Review Draft
 ↓
Accept
 ↓
Kitchen Processing
 ↓
Payment
```

POS users should not need to navigate through multiple administrative screens to perform routine order operations.

---

## 13. Draft Order Navigation

Draft orders are temporary working states.

A Draft:

* is fully editable;
* does not deduct inventory;
* does not reserve inventory;
* does not create kitchen work;
* does not make a table operationally Busy;
* may be lost if the device restarts.

The application must clearly distinguish Draft state from Accepted operational state.

```text
Draft
 ↓
Edit
 ↓
Accept
 ↓
Accepted
```

---

## 14. Order Navigation

Once an order is Accepted, its operational state becomes visible to relevant users according to permission.

The order interface may expose:

* order information;
* products;
* quantities;
* current status;
* table;
* primary waiter;
* temporary helping waiter;
* payment state;
* kitchen state;
* order history.

Important state changes must be performed through controlled actions rather than unrestricted field editing.

---

## 15. Table Navigation

Tables are accessed within the current Branch.

The table view should provide a clear distinction between:

* Free;
* Busy;
* historical activity.

A table is Busy when at least one open/unpaid order exists.

Paid orders remain available through history but do not keep the table Busy.

The table view must also allow authorized users to see all relevant orders belonging to the current table visit/session.

---

## 16. Waiter Navigation

Waiter assignments are shown within the relevant table/order context.

The system preserves:

* primary waiter;
* temporary helping waiter;
* assignment history where applicable.

A primary waiter may assign a second waiter to help with the table once according to the approved business rule.

The temporary assignment does not replace the primary waiter.

---

## 17. Payment Navigation

Payment is initiated from an eligible order.

The payment interface must provide the information required to complete the transaction safely, including:

* order total;
* amount already paid;
* remaining amount;
* payment method;
* payment portions where applicable;
* debt information where applicable;
* overpayment information where applicable.

Payment status must remain independent from the operational order lifecycle.

A completed payment does not automatically change the order to `Ready`, `Served` or another operational status.

---

## 18. Split Bill Navigation

Split bill is represented as multiple payment portions belonging to one order.

The system does not create separate orders merely because a customer wants to split payment.

Conceptually:

```text
One Order
    │
    ├── Payment Portion 1
    ├── Payment Portion 2
    └── Payment Portion 3
```

The backend preserves one Order UUID.

The UI may provide a convenient interface for selecting and completing the payment portions.

---

## 19. Cash Navigation

Cash-related navigation depends on the employee's permission and current Cash Session.

Typical flow:

```text
Cash
 ↓
Current Session
 ├── Opening
 ├── Transactions
 ├── Handover
 └── Closing
```

The application must clearly show whether the employee has:

* no active session;
* an active session;
* a pending handover;
* a closed historical session.

Closing a Cash Session does not reopen it.

---

## 20. Shift Handover Navigation

Handover is treated as a transition between Cash Sessions.

The navigation flow is:

```text
Previous Cashier
      ↓
Close Previous Session
      ↓
Cash Reconciliation
      ↓
New Cashier Authentication
      ↓
Cash Acceptance
      ↓
Open New Session
```

The physical Cash Register remains the same.

The Cash Session UUID changes.

Open/unpaid orders remain available to the new cashier according to permissions.

---

## 21. Inventory Navigation

Inventory navigation is divided into operational and informational actions.

Typical areas include:

* current stock;
* purchases;
* stock movements;
* inventory adjustments;
* discrepancies;
* shopping list;
* warehouse information.

Inventory operations must clearly distinguish:

* normal stock movement;
* purchase receipt;
* production;
* manual adjustment;
* correction;
* historical movement.

Negative stock must never be presented as a valid result.

---

## 22. Product and Recipe Navigation

Product and recipe management is primarily a Business/administrative workflow.

Typical navigation:

```text
Products
   ├── Product Details
   ├── Recipe
   ├── Set
   ├── Category
   └── History
```

Recipe-related changes may require approval according to permissions.

Archived products and previous recipe versions remain accessible through historical views where the employee has permission.

---

## 23. Menu and Pricing Navigation

Menu configuration is separated from POS operation.

Administrative users may manage:

* global menu;
* categories;
* branch availability;
* branch price overrides;
* product status;
* Set configuration.

Cashiers should not be given direct access to global pricing configuration unless explicitly granted the required permission.

Standard product price changes are not performed through normal cashier order operations.

---

## 24. Employee Navigation

Employee management includes:

* employee list;
* employee details;
* branch assignment;
* role;
* permissions;
* attendance;
* salary configuration;
* status;
* history.

Deactivating an employee does not remove historical records.

Inactive employees must not be able to perform new protected operations.

---

## 25. Reports Navigation

Reports are accessed according to:

* Business scope;
* Branch scope;
* report permission;
* subscription entitlement.

The report interface should support:

* period selection;
* branch selection where permitted;
* report type;
* report history;
* report version;
* Excel export.

Large reports and exports may be processed in the background.

POS must remain usable while report processing is running.

---

## 26. Notification Navigation

Notifications are accessible from the application shell and/or dedicated notification area.

Notifications have lifecycle states such as:

* Active;
* Read;
* Resolved;
* Expired.

Each notification must respect the employee's Business, Branch and permission scope.

A notification may provide a deep link to the relevant entity or screen when the employee is authorized to access it.

---

## 27. Audit and History Navigation

Audit and history views are administrative and permission-controlled.

Users may filter audit information by:

* date/time;
* employee;
* branch;
* event type;
* entity;
* transaction UUID;
* device;
* cash session;
* online/offline source;
* result/status.

Audit records remain immutable.

The UI must distinguish between:

* original event;
* correction;
* resulting event;
* related report version.

---

## 28. Subscription and Read-Only Navigation

When a Business enters read-only mode:

The application must preserve access to permitted information while disabling modifying functionality.

The UI should clearly indicate the read-only state.

Allowed examples:

* viewing data;
* viewing history;
* viewing reports;
* permitted Excel exports.

Blocked examples:

* creating new employees;
* changing menu;
* changing inventory;
* creating new orders;
* modifying business configuration.

Frontend visibility may reflect the read-only state, but the backend remains authoritative.

---

## 29. Offline Navigation

Offline mode must be visibly identifiable without obstructing normal POS operation.

The application should provide a compact indication such as:

```text
Online
```

or:

```text
Offline
Pending Sync: 7
```

The user should be able to identify whether the current operation is:

* online;
* offline;
* pending synchronization;
* conflicted;
* failed.

Offline state must not prevent permitted local operations merely because the application is waiting for synchronization.

---

## 30. Synchronization Navigation

Synchronization status is available to authorized users.

The UI may expose:

* last successful sync;
* pending events;
* retrying events;
* failed events;
* conflicts;
* device authorization state;
* configuration version.

Normal POS operation must continue while synchronization runs in the background.

Users with the appropriate permission may manually retry failed synchronization.

---

## 31. Context Preservation

The application should preserve relevant context during normal navigation.

Examples:

* selected Business;
* selected Branch;
* selected report period;
* selected table;
* selected order;
* selected inventory item.

However, stale context must not override authoritative server state.

After:

* branch switching;
* reconnect;
* synchronization;
* permission change;
* subscription state change;

the application must refresh affected context.

---

## 32. Permission Changes During Active Session

Permissions may change while an employee is already logged in.

For important operations, the server evaluates the employee's current effective permissions at the time of the operation.

Therefore:

```text
Old Permission
      ↓
Permission Changed
      ↓
New Operation
      ↓
Current Server Permission Check
```

The system must not assume that permissions from the initial login remain valid indefinitely.

The UI may refresh or request re-authentication when necessary, but server-side authorization remains authoritative.

---

## 33. Employee Status Changes

If an employee becomes inactive while a session is active:

* new protected operations must be rejected;
* the employee must not gain additional access through stale UI state;
* existing historical operations remain unchanged.

Offline operations created after the effective inactive time must not become valid merely because the device still contains an old authorization.

---

## 34. Error Navigation

Navigation-related errors must not expose technical implementation details.

Examples:

### Unauthorized

```text
Access Denied
```

### Missing Entity

```text
The requested item is no longer available.
```

### Conflict

```text
This information has changed. Please review the latest state.
```

### Subscription Restriction

```text
This feature is not available for the current subscription.
```

The exact UI wording may be refined during Frontend Analysis.

---

## 35. Navigation and Performance

Navigation must not introduce unnecessary loading delays into POS workflows.

The application should avoid:

* loading unrelated administrative data;
* loading large report datasets during POS startup;
* blocking POS navigation on background synchronization;
* loading unnecessary branch data;
* performing expensive calculations synchronously when they can be processed safely in the background.

Operational screens should load only the data required for the current workflow.

---

## 36. System Invariants

The following invariants apply to application navigation:

1. Navigation must respect the authenticated Business context.
2. Branch navigation must respect employee branch scope.
3. Permission-based visibility must not replace server-side authorization.
4. Unauthorized routes must not expose protected data.
5. Switching branches must recalculate effective permissions.
6. Branch switching must not mix stale data between branches.
7. POS must remain directly accessible to authorized operational users.
8. Draft orders must remain distinguishable from Accepted orders.
9. Payment navigation must preserve the separation between payment state and order operational state.
10. Split bills must preserve one Order UUID.
11. Cash handover must create a new Cash Session rather than reopen the previous one.
12. Read-only subscription state must be reflected in navigation.
13. Offline navigation must not expose unauthorized capabilities.
14. Synchronization must not block normal POS workflows.
15. Permission changes must be enforced on the next protected operation.
16. Employee deactivation must prevent new protected operations.
17. Historical data must remain accessible according to permission.
18. Navigation context must never override authoritative server state.

---

## 37. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/README.md`
* `docs/02_System_Analysis/01_System_Context_and_Boundaries.md`
* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`

---

## 38. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `02_Application_Structure_and_Navigation.md`

**Next Document:** `03_Tenant_Business_and_Branch_Context.md`

