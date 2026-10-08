# Expenses and Financial Adjustments UI

**Document ID:** FA-31
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

## 1. Purpose

This document defines the frontend architecture for Business and Branch expense management and related financial adjustment workflows.

The frontend must provide a simple operational interface while preserving:

* Business and Branch scope;
* permission boundaries;
* historical integrity;
* financial traceability;
* auditability;
* correction history;
* offline safety where applicable;
* subscription restrictions.

The frontend must not become the authority for financial business rules.

The backend remains authoritative for:

* authorization;
* expense validation;
* financial calculations;
* Business/Branch isolation;
* subscription entitlement;
* historical integrity;
* correction permissions;
* audit records.

---

## 2. Scope

This document covers:

* expense list;
* expense creation;
* expense details;
* expense categories;
* Branch expenses;
* Business-level expense visibility;
* expense comments;
* expense corrections;
* expense history;
* financial adjustments;
* permission-aware UI;
* filtering;
* search;
* reporting integration;
* audit integration;
* offline behavior;
* synchronization;
* error handling;
* subscription restrictions;
* accessibility;
* performance.

---

## 3. Expense Model

The frontend represents an expense as a financial business record.

Conceptually:

```text
Business
   ↓
Branch
   ↓
Expense
   ├── Category
   ├── Amount
   ├── Date
   ├── Comment
   ├── Actor
   └── Audit History
```

Every Branch expense must remain associated with the correct Business and Branch.

---

## 4. Expense Ownership

Expenses are Business-scoped records with optional Branch scope according to the underlying business model.

A Branch expense must never become visible to another Business.

Branch-scoped expense information must respect the current employee's Branch permissions.

---

## 5. Expense Creation

The expense creation screen should provide only the fields required for the operation.

Typical fields:

* Branch;
* expense category;
* amount;
* expense date;
* comment;
* optional attachment where supported.

The exact fields are controlled by backend contract and business rules.

---

## 6. Expense Amount

The amount field must accept valid positive financial values.

Frontend validation should provide immediate feedback for:

* empty amount;
* zero amount;
* negative amount;
* invalid numeric format;
* excessive precision;
* unsupported currency.

Backend validation remains authoritative.

---

## 7. Monetary Input

Monetary values must use a consistent input component.

The component should:

* prevent accidental non-numeric input;
* support locale-appropriate formatting;
* preserve exact user intent;
* avoid floating-point display errors;
* clearly show currency where applicable.

The frontend must not use JavaScript floating-point arithmetic as the financial authority.

---

## 8. Expense Date

Expense date selection must be explicit.

The frontend must distinguish:

* expense business date;
* record creation timestamp;
* synchronization timestamp.

These values must not be silently substituted for one another.

---

## 9. Branch Selection

When the employee has access to multiple Branches, the UI must require an explicit Branch context where necessary.

The currently selected Branch must be clearly visible.

Changing Branch context must invalidate or reload Branch-scoped expense data.

---

## 10. Branch Scope Protection

The frontend must never assume that a user can create an expense for every visible Branch.

The UI should use permission and Branch context to reduce invalid operations.

The backend must perform the final authorization.

---

## 11. Expense Categories

Expense categories may include:

* rent;
* utilities;
* transportation;
* maintenance;
* supplies;
* salary-related expenses where applicable;
* marketing;
* other.

The exact category list is configuration-driven.

The frontend must not hard-code business-critical category rules.

---

## 12. Category Selection

Category selection should use a searchable/selectable control when the list becomes large.

The selected category must be represented by a stable identifier.

The frontend must not rely on category display names as identifiers.

---

## 13. Comment Requirement

Where business rules require a comment, the expense form must make the field mandatory.

The UI should clearly explain why the comment is required.

Backend validation remains authoritative.

---

## 14. Comment Content

Comments should support sufficient context for later review.

The frontend should:

* enforce maximum length;
* preserve entered text;
* prevent unsupported control characters where required;
* display validation feedback.

---

## 15. Expense List

The expense list should provide:

* date;
* Branch;
* category;
* amount;
* status where applicable;
* creator;
* creation time.

The list must remain usable with large datasets.

---

## 16. Expense Search

Search may support:

* category;
* comment;
* employee;
* expense identifier;
* Branch where authorized.

Search must use backend-supported query semantics.

---

## 17. Expense Filters

Filters may include:

* date range;
* Branch;
* category;
* amount range;
* creator;
* status.

Filters should be composable.

---

## 18. Date Range Filter

Date filtering should clearly distinguish:

* inclusive start date;
* inclusive end date.

The frontend must avoid timezone-induced date shifting.

Date-only business values should be handled as calendar dates.

---

## 19. Sorting

Supported sorting may include:

* newest;
* oldest;
* highest amount;
* lowest amount;
* category;
* Branch.

The frontend should use server-side sorting for large datasets.

---

## 20. Pagination

Expense lists should use server-side pagination when the dataset is large.

The frontend must preserve:

* current filter;
* sort;
* page/cursor;
* Branch context.

Changing a major filter should reset pagination appropriately.

---

## 21. Expense Detail

The expense detail screen should show:

* expense identifier;
* Business;
* Branch;
* category;
* amount;
* date;
* comment;
* creator;
* creation time;
* current state;
* correction/history information.

---

## 22. Expense Status

Where status is required, the UI must use backend-defined states.

Example:

```text id="exps21"
ACTIVE
CORRECTED
CANCELLED
```

The frontend must not invent unsupported statuses.

---

## 23. Expense Immutability

Historical expense records must not be silently overwritten.

If correction is allowed:

```text id="cor112"
Original Expense
      ↓
Correction
      ↓
New Financial State
```

The original state remains recoverable through history.

---

## 24. Expense Correction

Correction must be treated as a controlled operation.

The UI should require:

* authorized employee;
* correction reason;
* affected record;
* new value where applicable.

The backend determines whether correction is allowed.

---

## 25. Correction Confirmation

Before committing a correction, the frontend should display:

* original amount;
* corrected amount;
* difference;
* reason;
* affected Branch;
* resulting state.

The user must explicitly confirm the operation.

---

## 26. Correction Warning

Financial corrections should have a stronger confirmation UX than ordinary edits.

Example:

```text
Original amount: 500,000
New amount:      450,000
Difference:      -50,000

Reason:
Incorrect amount entered.

[Cancel] [Confirm Correction]
```

The exact UI depends on the design system.

---

## 27. No Silent Editing

The frontend must not present historical financial data as freely editable fields.

An authorized correction should be visually distinct from ordinary editing.

---

## 28. Financial Adjustment

A financial adjustment represents an authorized change to a financial state.

Examples may include:

* correction of an incorrect expense;
* approved adjustment;
* reconciliation-related adjustment.

Financial adjustment semantics must come from the backend domain model.

---

## 29. Adjustment Separation

The frontend should distinguish:

```text
Original Transaction
        +
Financial Adjustment
        =
Current Financial State
```

This preserves historical context.

---

## 30. Adjustment History

The UI should show the adjustment chain where available.

Example:

```text
Expense #1042
   ↓
Original: 500,000
   ↓
Correction: -50,000
   ↓
Current: 450,000
```

Each event should retain actor and timestamp information.

---

## 31. Audit Integration

Important expense operations should expose audit context where the user has permission.

Examples:

* created;
* corrected;
* cancelled;
* category changed where allowed;
* Branch context changed where permitted.

Audit data remains immutable.

---

## 32. Actor Information

Where appropriate, display:

* employee;
* role;
* timestamp.

The frontend must not expose sensitive authentication information.

---

## 33. Permission-Aware UI

The frontend must evaluate permissions before showing actions.

Examples:

```text
expense.view
expense.create
expense.correct
expense.cancel
expense.export
```

Exact permission identifiers are defined by the authorization architecture.

---

## 34. Hidden vs Disabled Actions

An action that the employee is never allowed to perform may be hidden.

An action that exists but is temporarily unavailable may be disabled with a reason.

The frontend must avoid misleading the user.

---

## 35. Permission Is Not Authority

Frontend permission checks improve UX only.

They are not a security boundary.

The backend must revalidate every protected operation.

---

## 36. Business Context

Expense screens must display the active Business context when useful.

The UI must never mix records from different Businesses.

---

## 37. Branch Context

Branch-scoped screens should clearly indicate the current Branch.

Example:

```text
Expenses
Branch: Chilonzor
```

When All Branches is selected, the UI must clearly indicate that aggregate/multi-Branch mode is active.

---

## 38. All-Branch View

Authorized users may view expenses across multiple Branches.

The list should provide a Branch column.

Branch-specific actions must remain correctly scoped.

---

## 39. Branch Switching

When Branch context changes:

1. clear stale Branch-specific data;
2. load the new Branch context;
3. recalculate permissions;
4. refresh available actions;
5. refresh expense data.

Previous Branch data must not remain visually active as if it belonged to the new Branch.

---

## 40. Expense Dashboard Summary

The expense section may provide summary information such as:

* total expenses;
* expense count;
* expenses by category;
* expenses by Branch;
* period comparison.

Summary data must come from authoritative backend calculations.

---

## 41. Expense Charts

Charts are optional and should be used only where they improve decision-making.

Potential views:

* expenses by category;
* expenses by Branch;
* expenses over time.

Charts must not replace the detailed expense table.

---

## 42. Reporting Integration

Expenses should integrate with Reports.

The frontend may provide:

```text
Expenses
   ↓
Report
   ↓
Detailed Expense Data
```

The report result must remain consistent with the authoritative expense dataset.

---

## 43. Export

Authorized employees may export expense data.

Export should support:

* current filters;
* selected Branch scope;
* selected date range.

The frontend should request export generation rather than constructing authoritative financial exports locally.

---

## 44. Export Progress

Large exports should provide a clear state:

```text
Preparing
   ↓
Generating
   ↓
Ready
   ↓
Download
```

The frontend must not block the entire application while a large export is generated.

---

## 45. Export Audit

Where required, expense exports should be auditable.

The frontend should pass sufficient request context for backend audit recording.

---

## 46. Expense Attachments

If attachments are supported, the UI should provide:

* file selection;
* supported file type indication;
* file size validation;
* upload progress;
* upload result;
* error state.

Backend file validation remains authoritative.

---

## 47. Attachment Security

The frontend must not assume an uploaded file is safe.

The backend must perform:

* MIME validation;
* size validation;
* malware/security validation where applicable;
* access control.

---

## 48. Offline Expense Creation

Offline expense creation should be supported only if the system-wide offline policy permits the operation.

If enabled:

* trusted device is required;
* offline authorization must be valid;
* operation UUID must be generated;
* data must be encrypted locally;
* transaction must enter synchronization queue.

---

## 49. Offline Restrictions

If offline expense creation is not safe or not permitted by the backend policy, the frontend must clearly disable it.

The frontend must never create an apparently successful local financial operation when the system has not authorized offline execution.

---

## 50. Offline Expense Queue

An offline expense operation should contain sufficient information to synchronize safely.

Conceptually:

```text
Operation UUID
Business UUID
Branch UUID
Employee UUID
Device UUID
Expense Payload
Created At
Schema Version
Sync Status
```

Exact storage schema belongs to the offline persistence architecture.

---

## 51. Expense Synchronization

Synchronization should preserve:

* original amount;
* original date;
* Branch;
* category;
* comment;
* actor;
* operation UUID.

The server remains authoritative.

---

## 52. Duplicate Prevention

Retrying an expense synchronization operation must not create a duplicate expense.

The backend idempotency mechanism is authoritative.

The frontend must preserve the original operation UUID during retries.

---

## 53. Synchronization Result

The UI should distinguish:

```text
Synced
Pending
Retrying
Conflict
Rejected
Failed
```

The exact states must match the synchronization architecture.

---

## 54. Conflict Handling

If an expense synchronization conflict occurs:

* preserve the local operation;
* show conflict state;
* explain the required action;
* do not silently overwrite server state.

Conflict resolution follows the system synchronization architecture.

---

## 55. Rejected Expense

If the server rejects an expense:

* mark it as rejected;
* preserve the operation record;
* display the reason where safe;
* do not silently retry permanent failures.

---

## 56. Subscription Restrictions

When subscription status becomes read-only:

* expense list remains available;
* historical expenses remain viewable;
* allowed exports remain available;
* new expense creation is blocked;
* corrections are blocked;
* modifying operations are blocked.

---

## 57. Offline Subscription Restriction

Offline authorization must not bypass subscription restrictions.

A stale client cannot create a modifying financial operation after its authorization has expired.

---

## 58. Expense Permissions During Read-Only

The UI must reflect both:

* employee permission;
* subscription entitlement.

Effective action:

```text
Employee Permission
        AND
Subscription Entitlement
        AND
Operational State
```

---

## 59. Loading State

Expense screens should use predictable loading states.

Examples:

* skeleton;
* spinner for short operations;
* progress indicator for large operations.

The UI must not appear frozen during legitimate backend operations.

---

## 60. Empty State

If there are no expenses:

```text
No expenses found for the selected period.
```

The empty state should distinguish:

* genuinely empty data;
* filters returning no results;
* data still loading;
* permission restriction.

---

## 61. Error State

Expense errors should use centralized frontend error handling.

Examples:

* validation error;
* authorization error;
* conflict;
* subscription restriction;
* temporary network error;
* permanent failure.

---

## 62. Retry

Temporary failures may expose a Retry action.

Retry must be safe and must not create duplicate financial records.

---

## 63. Unsaved Changes

If the expense form contains unsaved data and the user attempts to leave, the frontend should warn before discarding the input.

This warning must not appear when no meaningful changes exist.

---

## 64. Double Submission

Expense creation and correction actions must protect against accidental double submission.

The UI should:

* disable the submit action while request is pending;
* show progress;
* retain operation state.

Backend idempotency remains authoritative.

---

## 65. Confirmation UX

High-risk operations should require explicit confirmation.

Examples:

* correction;
* cancellation;
* large financial adjustment.

The frontend must not define business-specific “large amount” thresholds independently.

---

## 66. Keyboard and POS Usability

Where expenses are used on POS/office hardware, keyboard navigation should be supported.

Important controls should have:

* logical tab order;
* visible focus;
* keyboard activation.

---

## 67. Accessibility

Expense interfaces should meet the project's accessibility requirements.

Important requirements:

* labels for form controls;
* keyboard accessibility;
* sufficient contrast;
* accessible validation errors;
* accessible tables;
* accessible dialogs;
* screen-reader-friendly status messages.

---

## 68. Responsive Layout

Expense management must remain usable on:

* desktop;
* POS screens;
* laptops;
* tablets where supported.

Large tables should use controlled horizontal scrolling where necessary rather than breaking the entire page layout.

---

## 69. Performance

Expense screens should remain responsive even with large datasets.

Targets:

| Operation                     |      Target |
| ----------------------------- | ----------: |
| Expense list initial render   |  p95 ≤1.5 s |
| Local filter interaction      | p95 ≤100 ms |
| Expense detail open           | p95 ≤500 ms |
| Create/correction UI response | p95 ≤500 ms |
| Search response               | p95 ≤500 ms |
| Filter response               | p95 ≤500 ms |

Backend/API targets remain governed by backend SLOs.

---

## 70. Large Dataset Handling

The frontend must not load thousands of expenses unnecessarily.

Use:

* pagination;
* cursor pagination where appropriate;
* server-side filtering;
* server-side sorting;
* virtualized rendering where justified.

---

## 71. State Management

Expense state should remain separated into:

```text
Server State
Local UI State
Form State
Offline Transaction State
```

These must not be mixed into one uncontrolled global state.

---

## 72. Cache Strategy

Expense query caches may be used for:

* recent lists;
* filters;
* detail views.

However:

> Cached expense data is not authoritative financial state.

After mutations, affected caches must be invalidated or reconciled according to the data-flow architecture.

---

## 73. Financial Data Refresh

After a successful expense correction:

* affected detail view must update;
* list data must be refreshed/reconciled;
* summaries must be updated;
* stale cached totals must not remain visible.

---

## 74. Cross-Tab Behavior

If multiple browser tabs are supported, financial changes should not leave one tab showing obviously stale authoritative state.

Appropriate synchronization or invalidation mechanisms should be used.

---

## 75. Audit-Friendly UI

Financial history should be presented in a way that makes the sequence understandable.

Example:

```text
Created
  ↓
Corrected
  ↓
Adjusted
```

The UI must not flatten historical events into a single mutable record.

---

## 76. History Navigation

From an expense detail page, authorized users should be able to navigate to:

* correction history;
* audit event;
* related report;
* related export where permitted.

---

## 77. Expense Deletion

Ordinary expense deletion should not be available if it would destroy historical financial integrity.

Where business rules require removal, the UI should use the approved cancellation/correction mechanism instead.

---

## 78. Cancellation

If cancellation is supported:

* permission is required;
* reason may be required;
* confirmation is required;
* original record remains historically traceable.

---

## 79. Cancellation vs Correction

The UI must distinguish:

**Correction**

from

**Cancellation**.

They represent different business events and must not be represented by one generic “Edit” action.

---

## 80. Expense Detail Timeline

A timeline may be used to present important lifecycle events:

```text
Created
   ↓
Reviewed
   ↓
Corrected
   ↓
Cancelled
```

Only events actually returned by the backend should be displayed.

---

## 81. Notifications

Expense-related notifications may include:

* correction completed;
* correction rejected;
* financial adjustment completed;
* synchronization rejected;
* permission-related failure.

Notifications should follow the centralized notification architecture.

---

## 82. Notification Navigation

Expense notifications should deep-link to the relevant expense or adjustment where authorization permits.

If the employee no longer has access, the frontend must show an appropriate access message rather than exposing the record.

---

## 83. Security

The frontend must:

* never trust Branch identifiers supplied by UI state;
* never trust Business identifiers from editable client state;
* never expose unauthorized expenses;
* never treat hidden UI actions as authorization;
* never log sensitive financial information unnecessarily.

---

## 84. Data Masking

Where financial information requires restricted visibility, masking may be applied.

However, masking is a presentation control, not authorization.

---

## 85. Telemetry

Expense telemetry should contain only operationally necessary information.

Do not send:

* full comments;
* sensitive financial payloads;
* authentication data;
* unnecessary personal information.

---

## 86. Testing

Expense frontend testing must include:

### Unit

* amount validation;
* date handling;
* filters;
* selectors;
* permission checks;
* subscription state;
* correction calculations/display;
* cache invalidation.

### Component

* expense form;
* list;
* filters;
* detail;
* correction dialog;
* cancellation dialog;
* empty/error/loading states.

### Integration

* API client;
* permission response;
* subscription response;
* pagination;
* export;
* synchronization.

### E2E

* create expense;
* view expense;
* Branch switching;
* correction;
* cancellation;
* export;
* read-only subscription;
* offline expense flow where supported;
* synchronization failure;
* duplicate retry;
* authorization failure.

---

## 87. Security Testing

Tests must verify:

* Business isolation;
* Branch isolation;
* unauthorized correction;
* unauthorized cancellation;
* unauthorized export;
* stale permission handling;
* subscription restriction;
* offline authorization;
* duplicate submission;
* XSS-safe comment rendering.

---

## 88. Visual Regression

Important screens should be included in visual regression tests:

* expense list;
* expense form;
* expense detail;
* correction dialog;
* history timeline;
* empty state;
* error state.

---

## 89. Error Recovery

Recovery behavior should distinguish:

```text
Temporary Error
    → Retry

Conflict
    → Resolve

Authorization Error
    → Refresh / Request Access

Subscription Restriction
    → Read-only

Permanent Failure
    → Preserve Record + Explain
```

---

## 90. System Invariants

The following invariants apply to Expenses and Financial Adjustments UI:

1. Expense data is always Business-scoped.
2. Branch-scoped expenses remain associated with the correct Branch.
3. One Business cannot access another Business's expenses.
4. Branch context must be respected.
5. Frontend permission checks are not the security boundary.
6. Backend authorization is authoritative.
7. Subscription entitlement is authoritative.
8. Expense amounts must use the approved financial representation.
9. Frontend floating-point arithmetic is not the financial authority.
10. Expense date is distinct from creation timestamp.
11. Historical expense records are not silently overwritten.
12. Corrections preserve historical context.
13. Financial adjustments are distinct from original transactions.
14. Correction requires appropriate permission.
15. Cancellation requires appropriate permission where supported.
16. High-risk financial operations require explicit confirmation.
17. Double submission must not create duplicate financial records.
18. Operation UUIDs remain stable during retries.
19. Synchronization retries must remain idempotent.
20. Offline authorization cannot be extended by the frontend.
21. Offline operations cannot bypass subscription restrictions.
22. Offline operations cannot bypass employee permissions.
23. Offline financial records must remain recoverable.
24. Synchronization conflicts must not be silently resolved by last-write-wins.
25. Rejected operations must remain traceable.
26. Cached expense data is not authoritative.
27. Historical financial data cannot be reinterpreted by current configuration.
28. Expense exports use authoritative backend data.
29. Export operations may require audit.
30. Unauthorized users must not access expense details.
31. Unauthorized users must not access expense history.
32. Unauthorized users must not access expense exports.
33. Branch switching must invalidate stale Branch context.
34. Business switching must invalidate stale Business context.
35. Expense categories use stable identifiers.
36. Category display names are not authoritative identifiers.
37. Required comments must be validated.
38. Empty datasets must be distinguished from loading states.
39. Permission-restricted datasets must not be presented as empty data.
40. Temporary failures may be retried safely.
41. Permanent failures must not be blindly retried.
42. Financial corrections remain auditable.
43. Financial cancellations remain auditable.
44. Audit history is immutable.
45. Expense history must remain reconstructable.
46. Financial data must not be unnecessarily exposed through telemetry.
47. Comments must be rendered safely.
48. Attachments must not be trusted solely because frontend validation passed.
49. Frontend cannot bypass backend file validation.
50. Expense list must support large datasets without loading all records.
51. Server-side filtering is preferred for large datasets.
52. Server-side sorting is preferred for large datasets.
53. Expense UI must remain responsive on supported hardware.
54. POS/office workflows must not depend on expensive historical queries.
55. Subscription read-only state blocks modifying expense operations.
56. Historical expense viewing remains available in read-only state where permitted.
57. Allowed exports remain available in read-only state.
58. Current user context must remain visible where ambiguity is possible.
59. Branch-specific actions must never accidentally apply to another Branch.
60. Business-specific actions must never accidentally apply to another Business.
61. Expense correction must show enough information for informed confirmation.
62. Correction and cancellation must not be represented as generic unrestricted editing.
63. Financial adjustment history must preserve the original state.
64. Notifications must not expose unauthorized expense information.
65. Deep links must revalidate access.
66. Cached permissions cannot override server authorization.
67. Cached subscription state cannot override server entitlement.
68. Local expense state cannot override server financial state.
69. Frontend deployment must not destroy pending expense operations.
70. Local schema migration must preserve pending financial operations.
71. Synchronization must preserve original expense values.
72. Synchronization must preserve original actor context.
73. Synchronization must preserve original Branch context.
74. Synchronization must preserve operation identity.
75. Financial adjustment results must remain attributable.
76. Expense operations must remain observable.
77. Critical expense errors must be recoverable where technically possible.
78. Expense UI must support accessibility requirements.
79. Financial operations must not be confirmed solely through ambiguous UI state.
80. Expense history must remain consistent with audit history.
81. Expense reports must use authoritative financial data.
82. Frontend must not invent unsupported expense statuses.
83. Frontend must not invent unsupported financial adjustment rules.
84. Business rules remain centralized in backend/domain layers.
85. Expense UI must remain consistent with the general Frontend Design System.
86. Expense UI must remain consistent with general Error Handling architecture.
87. Expense UI must remain consistent with general Security architecture.
88. Expense UI must remain consistent with Offline and Synchronization architecture.
89. Expense UI must remain consistent with Reporting architecture.
90. Expense UI must remain consistent with Audit and History architecture.
91. Expense UI must remain consistent with Permission architecture.
92. Expense UI must remain consistent with Subscription architecture.
93. Expense UI must not introduce a second financial authority.
94. Expense UI must preserve historical integrity.
95. Expense UI must preserve Business isolation.
96. Expense UI must preserve Branch isolation.
97. Expense UI must preserve synchronization correctness.
98. Expense UI must preserve auditability.
99. Expense UI must preserve recoverability.
100. Expense UI must prioritize operational simplicity without weakening financial controls.

---

## Related Documents

### Business Analysis

* `docs/01_Business_Analysis/10_Expenses.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/18_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/15_Expenses_and_Financial_Operations.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Frontend

* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/16_Reports_and_Dashboard_UI.md`
* `docs/04_Architecture/07_Frontend/17_Notifications_and_Alerts_UI.md`
* `docs/04_Architecture/07_Frontend/18_Audit_and_History_UI.md`
* `docs/04_Architecture/07_Frontend/19_Subscription_and_Entitlement_UI.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/07_Frontend/22_Frontend_State_Management_and_Data_Flow.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `docs/04_Architecture/07_Frontend/24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`
* `docs/04_Architecture/07_Frontend/25_Frontend_Offline_Synchronization_and_Conflict_Resolution.md`
* `docs/04_Architecture/07_Frontend/26_Frontend_Error_Handling_and_Recovery_Architecture.md`
* `docs/04_Architecture/07_Frontend/27_Frontend_Performance_and_Optimization_Architecture.md`
* `docs/04_Architecture/07_Frontend/28_Frontend_Security_and_Client_Side_Protection_Architecture.md`
* `docs/04_Architecture/07_Frontend/29_Frontend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/07_Frontend/30_Frontend_Deployment_and_Runtime_Architecture.md`

### Backend

* `docs/04_Architecture/06_Backend/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/04_Architecture/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

---

## Status

**Frontend Architecture:** Proposed

**Version:** 1.0

**Current Document:** `31_Expenses_and_Financial_Adjustments_UI.md`

**Previous Document:** `30_Frontend_Deployment_and_Runtime_Architecture.md`

**Next Step:** Frontend `README.md` and final Frontend Architecture audit.

