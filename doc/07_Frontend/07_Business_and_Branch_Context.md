# Business and Branch Context

**Document ID:** FA-07
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `06_Role_Permission_and_Access_Control_UI.md`
**Next Document:** `08_Dashboard_Architecture.md`

---

# 1. Purpose

This document defines how the Frontend manages Business and Branch context.

The system is multi-tenant and multi-Branch.

The Frontend must always know which:

* Business;
* Branch;
* employee context;
* permissions;
* subscription state;
* device context

are currently active.

The primary principle is:

> UI context determines what the user is currently viewing and operating on; Backend authorization determines what the user is actually allowed to access or modify.

---

# 2. Context Hierarchy

The Frontend follows this hierarchy:

```text
Platform
   ↓
Business
   ↓
Branch
   ↓
Employee
   ↓
Operational Context
```

For normal Business users:

```text
Business
   ↓
Authorized Branches
   ↓
Active Branch
```

Super Admin operates under a separate platform-level context.

---

# 3. Business Context

Business context identifies the currently active restaurant/business network.

Conceptually:

```text
Business Context
├── business_id
├── business_name
├── status
├── subscription_state
└── available_branches
```

The Backend remains authoritative for all values.

---

# 4. Branch Context

Branch context identifies the operational Branch currently selected by the employee.

Conceptually:

```text
Branch Context
├── branch_id
├── branch_name
├── status
├── timezone
├── currency/configuration
└── operational state
```

Only authorized Branches may be selected.

---

# 5. Active Context

The Frontend should expose a centralized active context:

```text
Active Context
├── Business
├── Branch
├── Employee
├── Permissions
├── Subscription
├── Device
└── Offline State
```

Feature modules should consume this centralized context rather than maintaining independent Business/Branch selections.

---

# 6. Context Initialization

After authentication:

```text id="n8k4p2"
Authentication
      ↓
Load Business
      ↓
Load Authorized Branches
      ↓
Determine Active Branch
      ↓
Load Permissions
      ↓
Load Subscription
      ↓
Load Branch Configuration
      ↓
Application Ready
```

No Branch-dependent feature should initialize before the required Branch context is established.

---

# 7. Single Branch Employee

If an employee has access to exactly one Branch, the Frontend may automatically select it.

Example:

```text
Business: FastFood Demo
Branch: Chilanzar
```

The user should not be forced to manually select the same Branch every time unless policy requires it.

---

# 8. Multi-Branch Employee

If an employee has access to multiple Branches, the Frontend should provide an explicit Branch selector.

Example:

```text
Business: FastFood Demo

Branch
[ Chilanzar ▼ ]
```

The selector should display only authorized Branches.

---

# 9. Branch Selector

The Branch selector should clearly show:

* Branch name;
* optionally Branch code;
* current selection;
* availability/status where useful.

Example:

```text
Branches

✓ Chilanzar
  Yunusabad
  Sergeli
```

Unauthorized Branches must not be selectable.

---

# 10. Business Selector

If the authenticated user can access multiple Businesses, the Frontend may provide a Business selector.

Example:

```text
Business

✓ FastFood Demo
  Burger House
  Pizza Network
```

Business switching must reinitialize all Business-scoped state.

---

# 11. Business Switching

Business switching follows:

```text id="x7m3q9"
Current Business
      ↓
Validate target Business
      ↓
Clear Business-scoped state
      ↓
Load target Business
      ↓
Load Branches
      ↓
Load Permissions
      ↓
Load Subscription
      ↓
Select Branch
      ↓
Reload application context
```

The previous Business state must not leak into the new Business.

---

# 12. Branch Switching

Branch switching follows:

```text id="v4p8n2"
Current Branch
      ↓
User selects another Branch
      ↓
Validate authorization
      ↓
Persist context change
      ↓
Clear Branch-scoped state
      ↓
Load new Branch configuration
      ↓
Recalculate permissions
      ↓
Reload Branch-dependent data
      ↓
Update UI
```

The transition should be explicit and predictable.

---

# 13. Branch Switch Confirmation

Normal Branch switching should not require confirmation if no destructive or unsaved action is active.

If there are unsaved changes:

```text
You have unsaved changes.

Switching Branch may discard them.

[Stay] [Switch Branch]
```

The application should protect user work.

---

# 14. Active POS State

Branch switching must be handled carefully while POS is active.

If the current POS screen has:

* an open Order;
* unsaved Order changes;
* pending local operation;

the UI must prevent accidental context switching where this could cause data loss or ambiguity.

---

# 15. POS Context Rule

A POS operational session must always have an explicit:

```text
Business
+
Branch
+
Employee
+
Device
+
Cash Session
```

where applicable.

The Frontend must not allow POS operations against an ambiguous Branch.

---

# 16. Cash Session Context

If a Cash Session is active:

```text
Business: FastFood Demo
Branch: Chilanzar
Cash Register: Register 1
Cash Session: #CS-1024
```

The UI should clearly identify the active Cash Session where relevant.

---

# 17. Branch Context and Cash Session

Changing Branch while a Cash Session is active must follow business rules.

The Frontend should not silently detach the employee from an active Cash Session.

Where switching is prohibited:

```text
Cash Session is active.

Close or transfer the Cash Session before changing Branch.
```

The Backend remains authoritative.

---

# 18. Branch Context and Permissions

Permissions are Branch-aware where applicable.

Example:

```text
Branch A
inventory.adjust → Yes

Branch B
inventory.adjust → No
```

After switching Branch, effective permissions must be recalculated.

---

# 19. Branch Context and Menu

Menu configuration is Branch-specific.

After Branch switch:

```text
Branch A
Burger → Active
Price → 30,000

Branch B
Burger → Inactive
Price → 32,000
```

The Frontend must reload the effective Branch menu and pricing context.

---

# 20. Branch Context and Inventory

Inventory data must always be scoped to the active Branch unless the specific feature intentionally operates at Business level.

A Branch switch must invalidate or replace the previous Branch inventory state.

---

# 21. Branch Context and Reports

Reports may be:

* Branch-specific;
* multi-Branch;
* Business-wide.

The UI must clearly identify the report scope.

Example:

```text
Sales Report
Scope: Branch A
Period: 1–30 September
```

---

# 22. Business-Wide Reports

Authorized employees may access Business-wide reports.

The UI should explicitly display:

```text
Scope: All authorized Branches
```

This prevents confusion between a single Branch and aggregated Business data.

---

# 23. Branch Scope Filter

Where a report or list supports Branch selection, the selector must follow the employee's authorization scope.

Example:

```text
Branch

[All authorized Branches]
[Chilanzar]
[Yunusabad]
```

The option must not expose unauthorized Branches.

---

# 24. Context Bar

The Application Shell should provide a clear context indicator.

Recommended:

```text
FastFood Demo
/
Chilanzar
```

or:

```text
Business: FastFood Demo
Branch: Chilanzar
```

The exact visual design follows the Design System.

---

# 25. Context Visibility

Business and Branch context should be visible on important operational pages.

Especially:

* POS;
* Orders;
* Cash;
* Inventory;
* Reports;
* Menu;
* Pricing;
* Attendance;
* Payroll.

---

# 26. Context in Detail Pages

A detail page should not rely only on navigation history to communicate scope.

Example:

```text
Order #10482

Branch: Chilanzar
Status: Preparing
```

This is especially important for cross-Branch administrative users.

---

# 27. Context in Forms

Branch-scoped forms should show their target Branch.

Example:

```text
Create Expense

Branch
Chilanzar

Amount
100,000

Comment
...
```

The user should not have to infer the Branch from hidden application state.

---

# 28. Business Context in Forms

Business-level configuration should clearly identify the Business.

Example:

```text
Menu Configuration

Business:
FastFood Demo
```

This is important for users with multiple Business access.

---

# 29. Context Switching and Unsaved Changes

When switching Business or Branch:

1. Check for unsaved changes.
2. Check for active operational workflows.
3. Warn when necessary.
4. Preserve safe local state where possible.
5. Perform context switch.
6. Clear stale scoped state.
7. Load new state.

---

# 30. Context State Categories

Frontend state should distinguish:

```text
Global UI State
Business State
Branch State
Session State
Feature State
Offline State
Synchronization State
```

Business and Branch state must not be mixed with generic UI state.

---

# 31. State Isolation

Branch-scoped state must contain enough identity to prevent accidental reuse.

Conceptually:

```text
cacheKey =
business_id + branch_id + resource + parameters
```

Business-scoped state may use:

```text
cacheKey =
business_id + resource + parameters
```

---

# 32. Business State Reset

When Business changes, invalidate:

* Branch list;
* active Branch;
* permissions;
* menu;
* pricing;
* inventory;
* Orders;
* Cash;
* reports;
* Business configuration;
* subscription state where applicable.

The exact invalidation set depends on feature ownership.

---

# 33. Branch State Reset

When Branch changes, invalidate or reload:

* Branch menu;
* Branch pricing;
* inventory;
* Orders;
* tables;
* Cash Session;
* attendance;
* Branch reports;
* Branch notifications;
* Branch configuration;
* Branch-specific permissions.

---

# 34. Stale Data Protection

The Frontend must not display stale Branch data as if it belongs to the newly selected Branch.

During transition:

```text
Switching Branch...
```

may be displayed.

The application should not mix:

```text
Branch A data
+
Branch B context
```

---

# 35. Context Loading

Recommended state:

```text
Context Status

Initializing
Loading
Ready
Switching
Error
```

The UI should provide meaningful feedback for non-instant transitions.

---

# 36. Context Loading Error

If Branch loading fails:

```text
Unable to load Branch information.

Please try again.
```

The application should not silently use the previous Branch as a substitute.

---

# 37. Context Recovery

When context initialization fails:

1. Keep authentication state if still valid.
2. Preserve safe session information.
3. Retry recoverable requests.
4. Avoid rendering invalid Branch-scoped data.
5. Provide a recovery action.

---

# 38. Context and Subscription

Business subscription state applies to Business-level functionality.

Example:

```text
Subscription:
READ_ONLY
```

The UI may then show:

```text
Viewing mode

Editing is unavailable until the subscription is active.
```

---

# 39. Branch Features Under Read-Only State

Read-only subscription state may still allow:

* viewing Branch data;
* reports;
* allowed exports;
* historical information.

Modification controls should be disabled or hidden according to UX policy.

---

# 40. Subscription and Branch Switching

Branch switching remains available if viewing multiple Branches is permitted.

The UI must not imply that READ_ONLY means the entire application is inaccessible.

---

# 41. Context and Employee Status

Employee status affects context.

For inactive or suspended employees:

```text
Employee access unavailable.
```

The application must not allow them to continue operating simply because the Branch was previously selected.

---

# 42. Context and Device

Device state may affect available operation.

Example:

```text
Device
Trusted
```

or:

```text
Device
Verification Required
```

Branch context must not bypass device trust requirements.

---

# 43. Offline Business Context

Offline operation must retain the last valid authorized Business and Branch context.

Example:

```text
Offline

Business: FastFood Demo
Branch: Chilanzar

Configuration:
Last valid snapshot
```

The client must not invent a new Business or Branch context while offline.

---

# 44. Offline Branch Switching

If offline Branch switching is supported:

* only previously authorized Branches may be selected;
* locally available valid configuration must exist;
* permissions must be based on the valid offline authorization snapshot;
* the device must not grant new Branch access.

If required local data is unavailable, switching must be blocked.

---

# 45. Offline Context Expiration

When offline authorization expires:

```text
Offline authorization expired.

Connect to the internet to continue.
```

The Frontend must not allow Branch switching to bypass expiration.

---

# 46. Synchronization and Context

After reconnecting:

```text
Reconnect
   ↓
Authenticate
   ↓
Validate Device
   ↓
Synchronize Transactions
   ↓
Refresh Business Context
   ↓
Refresh Branch Context
   ↓
Refresh Permissions
   ↓
Refresh Configuration
```

Transaction synchronization remains higher priority than configuration refresh.

---

# 47. Synchronization Context Conflict

If a local operation references a Branch that is no longer valid:

```text
Branch context conflict

This operation requires server-side review.
```

The Frontend should surface the conflict using the synchronization architecture.

---

# 48. Cross-Business Isolation

The Frontend must never reuse Business-scoped data between Businesses.

Examples of Business-scoped state:

* menu;
* product definitions;
* recipes;
* subscription;
* employee configuration;
* Business settings.

Switching Business must invalidate relevant caches.

---

# 49. Cross-Branch Isolation

The Frontend must never reuse Branch-scoped state between Branches.

Examples:

* stock;
* Orders;
* Cash;
* tables;
* Branch pricing;
* Branch availability;
* Branch attendance.

---

# 50. URL Context

Routes may contain Business or Branch identifiers when useful.

Example:

```text
/business/:businessId/branch/:branchId/orders
```

However:

> URL identifiers are navigation context, not authorization proof.

The Backend must validate them.

---

# 51. Deep Links

A deep link should preserve valid Business/Branch context.

Example:

```text
/orders/10482
```

The application should resolve the required Business/Branch context before rendering protected data.

---

# 52. Browser Back/Forward

Browser navigation must not silently produce invalid Business/Branch state.

If the user changes Branch and then presses Back:

* the application must restore the route safely;
* authorization must still be validated;
* stale data must not be shown as current.

---

# 53. Context Persistence

The last selected Branch may be persisted locally for convenience.

However:

* it is only a preference;
* authorization must be checked again;
* it must not override server state;
* it must not be used as proof of access.

---

# 54. Default Branch

The system may support a preferred Branch.

Possible priority:

```text
Explicit current Branch
      ↓
Previously selected authorized Branch
      ↓
Business default Branch
      ↓
First authorized Branch
```

The exact priority should be defined centrally.

---

# 55. Branch Status

A Branch may have a status such as:

```text
ACTIVE
INACTIVE
CLOSED
```

The Frontend should reflect Branch availability.

Inactive Branches should not be selected for new operational activity unless explicitly supported.

Historical Branch information may remain viewable where authorized.

---

# 56. Branch Deactivation

If a currently selected Branch becomes inactive:

```text
This Branch is no longer active.

Select another available Branch.
```

The Frontend must not automatically continue new operations against it.

---

# 57. Business Lifecycle

Business lifecycle may affect context:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

The Frontend should map lifecycle state to appropriate UI behavior.

Deleted Business data must not be presented as active data.

---

# 58. Context and Navigation

Navigation must be recalculated after Business/Branch changes.

Example:

```text
Branch A
Inventory
Cash
Tables
Reports

Switch to Branch B

Inventory
Orders
Reports
```

Only currently valid navigation should remain visible.

---

# 59. Context and Notifications

Notifications should respect Business and Branch scope.

A Branch A notification must not appear as a Branch B operational alert without clear scope.

Example:

```text
Low Stock

Branch: Chilanzar
Product: Chicken
```

---

# 60. Context and Audit

Important operations should include the current Business/Branch context in the Backend audit record.

The Frontend does not generate authoritative audit context independently.

---

# 61. Context and Search

Search results must respect the active scope.

A Branch-scoped search must not accidentally return another Branch's data.

Business-wide search must explicitly indicate its wider scope.

---

# 62. Context and Reports

The report header should expose scope:

```text
Sales Report
Business: FastFood Demo
Branch: Chilanzar
Period: 01–30 September
```

For multi-Branch:

```text
Scope: All authorized Branches
```

---

# 63. Context and Export

Exports must retain scope information.

Example filename:

```text
sales_chilanzar_2026-09.xlsx
```

The exact filename format is implementation-defined.

The exported data itself must be generated from authoritative Backend/report state.

---

# 64. Context and Payroll

Payroll may be:

* Business-level;
* Branch-level;
* employee-specific.

The Frontend must display the applicable scope.

Salary information must remain permission-controlled.

---

# 65. Context and Attendance

Attendance records should clearly identify Branch where Branch-scoped.

An employee working in multiple Branches must not have attendance records silently merged without proper scope.

---

# 66. Context and Menu/Pricing

Menu and pricing must be recalculated after Branch switching.

The Frontend must not continue showing Branch A's price configuration after Branch B becomes active.

---

# 67. Context and Inventory

Inventory values must be tied to the active Branch.

The UI must prevent ambiguous stock operations.

Example:

```text
Stock Adjustment

Branch: Chilanzar
Product: Chicken
Quantity: 20 kg
```

---

# 68. Context and Orders

Every Order view should be able to identify its Branch.

A multi-Branch employee viewing an Order should not have to infer the Branch from context alone.

---

# 69. Context and Cash

Cash operations must always identify:

* Branch;
* Cash Register;
* Cash Session.

The UI should make these values visible in relevant workflows.

---

# 70. Context and Tables

Hall/Table data is Branch-scoped.

Switching Branch must clear the previous Branch table state before loading the new state.

---

# 71. Context Switch Feedback

A Branch switch should provide immediate visual feedback:

```text
Switching to Yunusabad…
```

The transition should feel responsive even when data loading continues asynchronously.

---

# 72. Context Switch Performance

Targets:

| Metric                             |                                  Target |
| ---------------------------------- | --------------------------------------: |
| Branch selector interaction        |                             p95 ≤100 ms |
| Cached Branch switch               |                             p95 ≤300 ms |
| Normal Branch context load         |    p95 ≤1 s after required API response |
| Permission recalculation UI update |          ≤2 s after authoritative state |
| Business context switch            |        p95 ≤2 s under normal conditions |
| POS context restoration            | p95 ≤500 ms for locally available state |

These targets are frontend UX targets and do not override Backend SLOs.

---

# 73. Context Caching

Context data may be cached for performance.

Recommended strategy:

```text
Business Context
    ↓
Cached by Business UUID

Branch Context
    ↓
Cached by Business UUID + Branch UUID

Permission Context
    ↓
Cached by Business + Employee + Branch + version
```

The cache must not become an authorization authority.

---

# 74. Context Invalidation

Invalidate context when:

* logout;
* Business switch;
* Branch switch;
* employee change;
* permission change;
* subscription change;
* device revocation;
* relevant synchronization;
* Backend version change.

---

# 75. Context Loading Priority

Recommended priority:

```text
Authentication
   ↓
Business
   ↓
Branch
   ↓
Permissions
   ↓
Critical operational configuration
   ↓
Feature data
   ↓
Secondary/background data
```

POS-critical state should have priority over non-essential dashboard data.

---

# 76. Error Recovery

If Branch context fails to load:

1. Preserve valid authentication.
2. Keep previous context only until transition is safely resolved.
3. Do not submit new operations against an uncertain context.
4. Retry transient failures.
5. Allow user to select another authorized Branch where possible.

---

# 77. Accessibility

Business and Branch context controls must:

* have accessible labels;
* expose current selection;
* support keyboard navigation;
* support screen readers;
* provide visible focus;
* avoid color-only indication;
* announce context changes where useful.

Example:

```text
Branch changed to Yunusabad.
```

---

# 78. Mobile Context UI

On narrow screens:

```text
FastFood Demo
Yunusabad ▼
```

The context selector should remain easy to access without occupying excessive screen space.

POS may use a more compact context indicator.

---

# 79. AI-Agent Rules

AI agents modifying Business/Branch context UI must:

1. Read this document before modifying context behavior.
2. Read authentication architecture.
3. Read permission architecture.
4. Read offline architecture.
5. Never treat URL identifiers as authorization.
6. Never trust client-selected Business/Branch IDs.
7. Preserve Business isolation.
8. Preserve Branch isolation.
9. Recalculate permissions after Branch changes.
10. Reload Branch-scoped configuration.
11. Prevent stale data mixing.
12. Preserve unsaved work.
13. Preserve active Cash Session rules.
14. Preserve offline authorization boundaries.
15. Preserve synchronization priority.
16. Preserve subscription restrictions.
17. Preserve accessibility.
18. Preserve context performance targets.
19. Avoid duplicating context state across features.
20. Document any new context dependency.

---

# 80. System Invariants

The following invariants are mandatory:

1. Every authenticated Business operation has a valid Business context.
2. Branch-scoped operations have a valid Branch context.
3. Backend authorization is authoritative.
4. Client-selected Business IDs are not authorization proof.
5. Client-selected Branch IDs are not authorization proof.
6. Unauthorized Branches cannot be selected.
7. Business switching resets Business-scoped state.
8. Branch switching resets Branch-scoped state.
9. Business data cannot leak across Business contexts.
10. Branch data cannot leak across Branch contexts.
11. Permission state is recalculated after Branch changes.
12. Subscription state applies to the active Business.
13. Employee status affects access.
14. Device trust affects permitted operations.
15. Offline context is based on previously authorized state.
16. Offline mode cannot grant new Business access.
17. Offline mode cannot grant new Branch access.
18. Offline mode cannot extend authorization.
19. Client clock cannot extend offline authorization.
20. Transaction synchronization remains higher priority than configuration synchronization.
21. POS operations always have an unambiguous Branch context.
22. Cash operations identify Branch and Cash Session.
23. Inventory operations identify the correct Branch.
24. Orders retain their authoritative Branch identity.
25. Historical Orders are not rewritten by context switching.
26. Current Branch context cannot reinterpret historical transactions.
27. Menu configuration is reloaded after Branch switching.
28. Pricing configuration is reloaded after Branch switching.
29. Inventory state is reloaded after Branch switching.
30. Table state is reloaded after Branch switching.
31. Cash state is not silently transferred between Branches.
32. Active Cash Sessions are not silently detached.
33. Unsaved changes are protected during context switching.
34. Stale data must not be shown as current context data.
35. Context loading has explicit states.
36. Context loading failures cannot silently fall back to another Branch.
37. Branch deactivation prevents new unauthorized operational activity.
38. Business read-only state blocks modifying operations.
39. Historical data remains viewable where authorized.
40. Business-wide reports clearly indicate their scope.
41. Branch-specific reports clearly indicate their Branch.
42. Search respects active scope.
43. Exports preserve authoritative scope.
44. Notifications respect Business/Branch scope.
45. Audit records preserve authoritative Business/Branch context.
46. Context caches are not security authorities.
47. Cache keys preserve Business/Branch isolation.
48. Logout clears sensitive context.
49. Business switching clears previous Business-sensitive state.
50. Branch switching clears previous Branch-sensitive state.
51. Multi-Branch users can access only authorized Branches.
52. All-Branch access remains Business-scoped.
53. Super Admin platform scope remains separate.
54. Deep links require context validation.
55. Browser navigation cannot bypass authorization.
56. Context preferences are convenience only.
57. Preferred Branch cannot override authorization.
58. Authentication is established before Business context.
59. Business context is established before Branch context.
60. Branch context is established before Branch-dependent features.
61. Permission context depends on valid Business/Branch scope.
62. Subscription context depends on valid Business scope.
63. Device context remains associated with the authenticated device.
64. Offline Branch switching requires valid local authorization.
65. Offline Branch switching requires available valid local data.
66. Context conflicts are explicit.
67. Context synchronization cannot silently overwrite authoritative state.
68. Context switching must not duplicate business operations.
69. Context switching must remain responsive.
70. Context UI must remain accessible.
71. Context identity must remain visible on important operational screens.
72. Context must never be inferred solely from visual navigation history.
73. Context-dependent features must consume centralized context state.
74. Feature modules must not maintain conflicting active Branch state.
75. Context behavior must preserve historical integrity.
76. Context behavior must preserve security boundaries.
77. Context behavior must preserve offline continuity.
78. Context behavior must preserve POS usability.
79. Context behavior must preserve subscription enforcement.
80. Context behavior must remain reconstructable and auditable through Backend state.

---

# 81. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/05_Authentication_and_Session_UI.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/18_Offline-First_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/19_Synchronization_and_Conflict_UI.md`
* `docs/04_Architecture/07_Frontend/20_Frontend_State_Management.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`

### Database

* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`

---

# 82. Status

**Document:** `07_Business_and_Branch_Context.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `06_Role_Permission_and_Access_Control_UI.md`

**Next Document:** `08_Dashboard_Architecture.md`

