# Cash Register and Cash Session UI

**Document ID:** FA-11
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `10_Order_Management_UI.md`
**Next Document:** `12_Inventory_and_Warehouse_UI.md`

---

# 1. Purpose

This document defines the Frontend architecture and user interface behavior for Cash Register and Cash Session management in FastFood ERP.

Cash operations are financially sensitive and must combine:

* simple daily operation;
* fast cashier workflow;
* clear financial state;
* controlled permissions;
* historical integrity;
* auditability;
* safe correction;
* offline continuity where supported.

The primary principle is:

> Cash UI must make the current cash state obvious while preventing accidental or unauthorized changes to historical financial state.

---

# 2. Scope

This document covers:

* Cash Register;
* Cash Session;
* session opening;
* session closing;
* expected cash;
* actual cash;
* cash discrepancy;
* cashier context;
* cash handover integration;
* cash correction;
* session history;
* session reports;
* permissions;
* notifications;
* offline behavior;
* synchronization;
* audit;
* security;
* performance;
* accessibility.

---

# 3. Cash Model

The operational hierarchy is:

```text id="cash101"
Business
   ↓
Branch
   ↓
Cash Register
   ↓
Cash Session
   ↓
Cash Operations
```

The current Business model normally uses one Cash Register per Branch.

The architecture must not prevent future support for multiple registers.

---

# 4. Cash Register

A Cash Register represents the physical/logical cash point.

Example:

```text id="cash214"
Branch:
Chilonzor

Cash Register:
Register 1

Status:
Active
```

The Register itself is not equivalent to a Cash Session.

---

# 5. Cash Session

A Cash Session represents one operational cash period.

Example:

```text id="cash325"
Session #1042

Cashier:
Employee 104

Opened:
09:02

Status:
OPEN
```

A Cash Session belongs to one Branch and one Cash Register.

---

# 6. Session States

The Frontend should represent at least:

```text id="cash436"
OPEN
CLOSING
CLOSED
```

The exact Backend state machine remains authoritative.

A closed Cash Session cannot be reopened through normal UI.

---

# 7. Active Cash Session

The active Cash Session should remain visible in POS and relevant operational screens.

Example:

```text id="cash547"
Register 1
Session #1042
OPEN
```

---

# 8. Cash Session Entry

Before opening a Cash Session, the UI should show:

* Branch;
* Cash Register;
* employee;
* current device;
* opening amount;
* relevant warnings.

---

# 9. Open Session

Recommended workflow:

```text id="cash658"
Select Cash Register
        ↓
Enter Opening Cash
        ↓
Validate
        ↓
Confirm
        ↓
Session Created
```

---

# 10. Opening Cash

The cashier enters the physical opening cash.

Example:

```text id="cash769"
Opening Cash

Amount:
500,000 UZS

[Open Session]
```

The value must be validated by the Backend.

---

# 11. Opening Confirmation

Before creating the session:

```text id="cash870"
Opening Cash

500,000 UZS

Register:
Register 1

Cashier:
Employee 104

[Cancel] [Open Session]
```

---

# 12. Opening Idempotency

Opening a Cash Session must be protected against duplicate submission.

Repeated clicks must not create multiple sessions for the same operation.

The operation UUID is the technical idempotency identity.

---

# 13. Opening Success

After successful opening:

```text id="cash981"
Cash Session #1042 opened

Opening Cash:
500,000 UZS
```

The POS may then become available according to the operational rules.

---

# 14. Opening Failure

Example:

```text id="cash192"
Cash Session could not be opened.

Reason:
Another active session already exists.

[Refresh]
```

The UI must reconcile with the current authoritative state.

---

# 15. Existing Active Session

If the employee already has an active Cash Session:

```text id="cash203"
Active Cash Session already exists.

Session #1042
Register 1

[Continue]
```

The UI must not create another session.

---

# 16. Register Availability

A Register may be:

```text id="cash314"
Active
Inactive
Unavailable
```

The UI must not allow session opening on an unavailable Register.

---

# 17. Cash Register Selection

If multiple Registers are supported in the future, only authorized Registers should be selectable.

Current deployments may normally expose one Register.

---

# 18. Branch Scope

Cash Register and Cash Session data must always respect Branch scope.

A cashier must not operate a Register belonging to another Branch unless explicitly authorized.

---

# 19. Business Scope

Cross-Business Cash access is prohibited.

The Frontend must not rely on hidden UI alone to enforce this.

---

# 20. Cashier Identity

Every Cash Session must clearly display the responsible employee.

Example:

```text id="cash425"
Cashier:
Employee 104
```

Employee identity must come from the authenticated operational context.

---

# 21. Device Context

Where relevant, the UI should display or retain device context.

Important cash operations must remain attributable to:

* employee;
* device;
* Branch;
* Register;
* Cash Session.

---

# 22. Session Dashboard

The active Cash Session screen may show:

```text id="cash536"
Session #1042

Opening Cash       500,000
Cash Sales       1,250,000
Cash Refunds        50,000
Cash Expenses       20,000
Expected Cash    1,680,000

[Handover]
[Close Session]
```

The exact financial calculation remains Backend-authoritative.

---

# 23. Expected Cash

Expected Cash is the authoritative expected amount at the relevant point.

The Frontend displays the value supplied by the Backend.

It must not independently become the financial source of truth.

---

# 24. Actual Cash

At session close, the cashier enters the physically counted cash.

Example:

```text id="cash647"
Expected Cash:
1,680,000 UZS

Actual Cash:
1,670,000 UZS
```

---

# 25. Discrepancy

The UI may show:

```text id="cash758"
Difference:
-10,000 UZS
```

The Backend remains authoritative for the final recorded discrepancy.

---

# 26. Shortage

Example:

```text id="cash869"
Cash shortage

Expected:
1,680,000

Actual:
1,670,000

Difference:
-10,000 UZS
```

The system should notify the relevant responsible parties according to notification rules.

---

# 27. Surplus

A surplus should also be recorded.

Example:

```text id="cash970"
Cash surplus

Expected:
1,680,000

Actual:
1,690,000

Difference:
+10,000 UZS
```

The UI must not silently normalize the difference to zero.

---

# 28. Closing Session

Recommended workflow:

```text id="cash181"
Active Session
      ↓
Close Session
      ↓
Count Cash
      ↓
Enter Actual Amount
      ↓
Review Difference
      ↓
Optional/Required Comment
      ↓
Confirm
      ↓
Session Closed
```

---

# 29. Close Button

Example:

```text id="cash292"
[Close Cash Session]
```

The action should be visible only when permitted.

---

# 30. Close Preconditions

Before closing, the UI should validate known local conditions such as:

* employee still authenticated;
* Branch context;
* Cash Session still open;
* no blocking active operation;
* no pending critical cash action.

Backend performs final validation.

---

# 31. Pending Orders

If there are unfinished Orders that may affect cash state, the UI should clearly warn the cashier.

Example:

```text id="cash303"
There are unfinished Orders.

Complete or safely resolve them before closing the Cash Session.
```

Exact blocking behavior follows Cash Session business rules.

---

# 32. Pending Payments

Pending payments should be clearly visible before closing when they affect Cash Session integrity.

---

# 33. Closing Count

Cash counting UI should be simple.

Example:

```text id="cash414"
Cash Count

Actual Cash:
[ 1,670,000 ]

Comment:
[________________]

[Confirm Close]
```

---

# 34. Denomination Counting

The architecture may support denomination counting later.

Example:

```text id="cash525"
100,000 × 10
50,000 × 8
20,000 × 3
10,000 × 1
```

If enabled, the Backend remains authoritative for the resulting total.

---

# 35. Simple Cash Count

The initial UI may use a single total amount field.

This matches the principle of keeping routine cashier workflows simple.

---

# 36. Closing Comment

A comment may be:

* required for discrepancy;
* required by Business policy;
* optional when there is no discrepancy.

The exact rule is configured by the system/business model.

---

# 37. Close Confirmation

Example:

```text id="cash636"
Close Session #1042?

Expected:
1,680,000 UZS

Actual:
1,670,000 UZS

Difference:
-10,000 UZS

Comment:
Cash shortage

[Cancel] [Confirm Close]
```

---

# 38. Close Success

After successful close:

```text id="cash747"
Cash Session #1042 closed.

Actual Cash:
1,670,000 UZS

Difference:
-10,000 UZS
```

The session becomes historical.

---

# 39. Closed Session

A closed Cash Session must not expose a normal Reopen action.

Example:

```text id="cash858"
Session #1042
CLOSED

[View Report]
[View History]
```

---

# 40. Correction

If a closed session requires correction, the UI must use a dedicated correction workflow.

The session itself is not silently reopened.

---

# 41. Correction Permission

Correction requires appropriate permission.

The Frontend must not expose privileged correction controls to unauthorized employees.

---

# 42. Correction Workflow

Recommended:

```text id="cash969"
Closed Session
      ↓
Request Correction
      ↓
Enter Reason
      ↓
Authorize
      ↓
Create Correction
      ↓
Audit
```

The exact authorization rules follow Cash Session and correction architecture.

---

# 43. Correction Limit

The Frontend must display correction restrictions where relevant.

If the configured correction limit is reached:

```text id="cash181"
Correction limit reached.

Additional correction requires privileged authorization.
```

The UI must not provide a normal workaround.

---

# 44. Historical Integrity

Correction must create a new state/event rather than rewriting the original closed session.

Historical values remain available.

---

# 45. Session History

The Cash Session list should display:

* Session number;
* Register;
* cashier;
* opened time;
* closed time;
* expected amount;
* actual amount;
* discrepancy;
* status.

---

# 46. Session Detail

Example:

```text id="cash292"
Session #1042

Cashier:
Employee 104

Opened:
09:02

Closed:
18:04

Opening:
500,000

Expected:
1,680,000

Actual:
1,670,000

Difference:
-10,000
```

---

# 47. Session Timeline

Where useful:

```text id="cash303"
09:02  Session opened
12:31  Handover
14:10  Cash correction
18:04  Session closed
```

Timeline data must come from authoritative history/audit sources.

---

# 48. Cash Handover Integration

Cash Handover is a separate operational workflow.

The Cash Session UI should provide access to the handover workflow where applicable.

Example:

```text id="cash414"
[Start Cash Handover]
```

---

# 49. Incoming Cashier

The incoming cashier must authenticate according to the established employee/session rules.

Example:

```text id="cash525"
Incoming Cashier

Employee:
Employee 118

[Confirm Identity]
```

---

# 50. Cash Count During Handover

The incoming cashier counts physical cash.

Example:

```text id="cash636"
Expected Handover Cash:
1,250,000 UZS

Actual Count:
1,240,000 UZS
```

---

# 51. Handover Difference

If a shortage occurs:

```text id="cash747"
Shortage:
-10,000 UZS
```

The relevant employee and responsible Owner/manager should receive notification according to configured rules.

---

# 52. Handover Confirmation

The workflow should require explicit confirmation.

Example:

```text id="cash858"
Confirm handover?

Cash:
1,240,000 UZS

[Reject] [Confirm]
```

---

# 53. Previous Cashier Notification

If a discrepancy exists, the outgoing cashier should receive the relevant notification.

---

# 54. Recount

The UI should support recount where required.

Example:

```text id="cash969"
Recount required

[Enter New Count]
```

---

# 55. Handover Finalization

After successful confirmation:

```text id="cash181"
Cash handover completed.

Incoming Cashier:
Employee 118

Transferred:
1,240,000 UZS
```

---

# 56. Handover and Session State

The Frontend must not assume that a handover automatically means a new Cash Session unless the Backend explicitly defines that behavior.

Session and handover states remain distinct concepts.

---

# 57. Cash-Only Principle

Cash handover should focus on actual physical cash.

The UI should not introduce unnecessary complexity into routine cash transfer.

---

# 58. Owner Notification

Owner notification is required according to the configured cash discrepancy rules.

The Owner does not necessarily need to approve every normal cash operation.

---

# 59. Notification Examples

Relevant notifications may include:

```text id="cash292"
Cash shortage
Cash surplus
Cash session closed
Correction request
Handover discrepancy
Privileged correction required
```

---

# 60. Cash Session Reports

The UI may provide:

* session summary;
* cashier report;
* discrepancy;
* handover history;
* correction history.

Heavy reports should not block active POS operations.

---

# 61. Export

Where permitted, session reports may be exported to XLSX.

Export must be handled through the reporting/export architecture rather than synchronous POS logic.

---

# 62. Permission Model

Cash permissions may include:

* open session;
* view session;
* close session;
* perform handover;
* view cash reports;
* initiate correction;
* approve privileged correction;
* view historical cash data.

Exact permission identifiers are defined centrally.

---

# 63. Permission-Aware UI

Unauthorized actions should be:

* hidden when irrelevant;
* disabled with explanation when useful;
* never presented as guaranteed authority.

Backend authorization remains authoritative.

---

# 64. Cash Session and Role

Different roles may have different cash capabilities.

Example:

```text id="cash303"
Cashier:
Open / Operate / Close

Manager:
View / Handover / Authorized Correction

Owner:
Full Business-level cash visibility
```

The actual permissions determine access.

---

# 65. Branch Scope

Cash UI must recalculate permissions and data after Branch switching.

A cashier must not retain another Branch's Register or Session state.

---

# 66. Branch Switching

If an active Cash Session exists:

* unsafe Branch switching should be blocked;
* or the user must complete the required session workflow;
* the UI must not silently move an active session to another Branch.

---

# 67. Business Switching

Business switching must invalidate incompatible:

* Cash Register;
* Cash Session;
* cash data;
* permissions.

---

# 68. Offline Cash Session

Offline behavior must follow the trusted-device and offline authorization architecture.

The Frontend may display locally known Cash Session state.

---

# 69. Offline Opening

A new Cash Session may only be opened offline if the Backend/System Analysis explicitly allows it within the offline authorization model.

The Frontend must not assume that offline opening is automatically permitted.

---

# 70. Offline Closing

If offline closing is supported:

* the operation receives an operation UUID;
* local state is persisted;
* actual cash is recorded locally;
* synchronization state is visible.

---

# 71. Offline Handover

If supported offline:

* incoming employee identity must be locally authorized;
* handover must remain within valid offline authorization;
* operation identity must be preserved;
* synchronization must reconcile the authoritative result.

---

# 72. Offline Restrictions

Offline mode cannot:

* grant new permissions;
* create a trusted device;
* extend authorization;
* bypass subscription restrictions;
* cross Business boundaries;
* cross unauthorized Branch boundaries.

---

# 73. Cash Synchronization

After reconnecting:

```text id="cash525"
Pending Cash Operation
        ↓
Server Validation
        ↓
Authoritative Result
        ↓
Local State Reconciliation
```

Cash operations must retain their original operation identity.

---

# 74. Duplicate Cash Operation Prevention

Repeated submission must not create duplicate:

* Cash Session;
* handover;
* correction;
* cash close.

---

# 75. Unknown Result

If a close request times out:

```text id="cash636"
Session close result is unknown.

Checking current session state...
```

The UI must reconcile before allowing another close attempt.

---

# 76. Cash Conflict

If another authorized operation changes the session before the current operation completes:

```text id="cash747"
Cash Session changed elsewhere.

Refresh the current session before continuing.
```

---

# 77. Concurrency

Cash operations are financially sensitive.

The Frontend should expect Backend conflict responses such as:

* conflict;
* already closed;
* already handed over;
* session unavailable;
* stale version.

The UI should not overwrite authoritative state.

---

# 78. Cash State Refresh

The active session UI should support manual refresh.

Automatic refresh may be used where it materially improves correctness.

---

# 79. Session Lock State

If the Backend reports that a sensitive operation is in progress:

```text id="cash858"
Cash operation in progress.

Please wait.
```

The UI must prevent duplicate local submission.

---

# 80. Financial Values

Cash values must use centralized money formatting.

Example:

```text id="cash969"
1,680,000 UZS
```

Do not use floating-point arithmetic for authoritative cash calculations.

---

# 81. Currency

Currency display must follow Business configuration.

Current deployment may use UZS.

The Frontend should not hard-code currency logic into individual components.

---

# 82. Cash Input

Cash amount fields should:

* accept numeric input;
* reject invalid characters;
* handle zero correctly;
* prevent negative values unless a specific operation supports them;
* display formatted values safely.

---

# 83. Decimal Handling

If the configured currency supports fractional values, the centralized money formatter must handle them consistently.

The cash UI must not independently define rounding rules.

---

# 84. Comment Input

Comment fields should have:

* clear labels;
* reasonable length limits;
* validation;
* accessible error messages.

---

# 85. Error Messages

Cash errors should explain:

1. What happened.
2. Why.
3. What the cashier should do.

Example:

```text id="cash181"
Session cannot be closed.

There is an active cash handover.

Complete the handover first.
```

---

# 86. Error Classification

The UI may map backend errors to:

* Validation Error;
* Authorization Error;
* Business Rule Violation;
* Conflict;
* Temporary Infrastructure Error;
* Permanent Failure.

---

# 87. Temporary Failure

Example:

```text id="cash292"
Connection temporarily unavailable.

Your cash operation has not been confirmed.
```

The UI should not claim success.

---

# 88. Recovery

Recovery may include:

* retry;
* refresh;
* operation reconciliation;
* conflict resolution;
* safe continuation.

Blind repeated submission is prohibited.

---

# 89. Cash Session Loading

The UI should distinguish:

```text id="cash303"
Loading Session
Refreshing Session
Closing Session
Synchronizing
```

---

# 90. Empty State

If there are no historical sessions:

```text id="cash414"
No Cash Sessions found.
```

This is not an error.

---

# 91. Historical Filtering

Cash Session history may filter by:

* date;
* Branch;
* Register;
* cashier;
* status;
* discrepancy.

Filters must respect permissions.

---

# 92. Historical Integrity

Closed sessions must remain reconstructable.

The UI must not offer a normal action that silently changes historical session values.

---

# 93. Audit Display

Authorized users may view:

* session opened;
* session closed;
* handover;
* correction;
* discrepancy;
* actor;
* device;
* timestamp.

---

# 94. Security Boundary

Cash UI must not expose:

* authentication secrets;
* tokens;
* internal security keys;
* unnecessary technical identifiers.

---

# 95. Sensitive Actions

Stronger authentication/re-authentication may be required for:

* privileged correction;
* high-value refund-related cash operations;
* exceptional session reopening mechanisms if any;
* administrative cash changes.

---

# 96. Session Reopen

Normal UI must not expose session reopening.

If the system provides a privileged recovery mechanism, it must be:

* explicitly authorized;
* audited;
* reason-based;
* separate from normal close/open flow.

---

# 97. POS Integration

POS should consume the active Cash Session context.

The Cash Session UI is responsible for session management, while POS is responsible for Order operations.

---

# 98. Payment Integration

Cash payment affects Cash Session according to Backend transaction rules.

The Frontend must not manually add payment amounts to expected cash as authoritative state.

---

# 99. Refund Integration

Cash refunds may affect expected cash.

The Order/Payment architecture determines the authoritative effect.

The Cash Session UI displays the resulting state.

---

# 100. Expense Integration

Cash expenses may affect expected cash where Business rules define them.

The Frontend must display the authoritative result.

---

# 101. Cash Session Performance

Targets:

* Session state load p95 ≤300 ms after API response.
* Cash action local feedback p95 ≤100 ms.
* Session close UI feedback p95 ≤100 ms.
* Active session context restoration p95 ≤500 ms.
* Historical session list p95 ≤300 ms after API response.

---

# 102. POS Priority

Cash Session refresh must not block routine POS local interaction unnecessarily.

Background refresh should be bounded.

---

# 103. Memory

Historical Cash Sessions must be paginated.

The Frontend must not retain unlimited session history in memory.

---

# 104. Accessibility

Cash UI must support:

* keyboard input;
* visible focus;
* semantic labels;
* screen reader announcements;
* readable financial values;
* accessible discrepancy indication;
* non-color status indicators;
* reduced motion.

---

# 105. Discrepancy Accessibility

A shortage must not be communicated only with red color.

Example:

```text id="cash525"
Shortage: -10,000 UZS
```

---

# 106. Confirmation Accessibility

Confirmation dialogs must:

* have clear titles;
* identify the action;
* identify financial consequence;
* expose Cancel/Confirm distinctly;
* preserve keyboard focus.

---

# 107. Cash Component Structure

Recommended:

```text id="cash636"
src/
└── features/
    └── cash/
        ├── components/
        │   ├── CashRegisterSelector.*
        │   ├── CashSessionHeader.*
        │   ├── CashSessionSummary.*
        │   ├── OpenSessionForm.*
        │   ├── CloseSessionForm.*
        │   ├── CashCountForm.*
        │   ├── CashDifference.*
        │   ├── HandoverEntry.*
        │   ├── HandoverConfirmation.*
        │   ├── SessionHistory.*
        │   ├── SessionTimeline.*
        │   ├── CashCorrectionDialog.*
        │   └── CashSyncIndicator.*
        ├── queries/
        ├── mutations/
        ├── selectors/
        ├── validation/
        ├── permissions/
        ├── offline/
        ├── synchronization/
        └── types.*
```

---

# 108. State Architecture

Cash UI state should be separated into:

```text id="cash747"
Cash Context
Cash Session State
Cash Count State
Handover State
Correction State
History Query State
Synchronization State
UI State
```

---

# 109. State Authority

Authoritative state:

* Cash Register;
* Cash Session;
* expected cash;
* actual cash;
* discrepancy;
* handover result;
* correction;
* cash transaction history.

Local UI state:

* form input;
* modal visibility;
* selected filter;
* loading state.

---

# 110. Cache

Cash Session cache may be used for performance.

However:

> Cached Cash state is never authoritative.

Final state must come from the Backend.

---

# 111. Cache Isolation

Cache keys must include:

* Business;
* Branch;
* Register;
* Session where applicable.

Cross-Business and cross-Branch cache leakage is prohibited.

---

# 112. Cache Invalidation

Cash cache should refresh/invalidate after:

* session open;
* session close;
* handover;
* correction;
* relevant payment;
* relevant refund;
* Branch switch;
* synchronization.

---

# 113. Testing

Tests should cover:

### Opening

* valid opening;
* duplicate opening;
* unavailable Register;
* unauthorized opening.

### Closing

* correct count;
* shortage;
* surplus;
* duplicate close;
* stale session.

### Handover

* valid incoming employee;
* incorrect count;
* shortage;
* recount;
* duplicate confirmation.

### Correction

* permission;
* reason;
* correction limit;
* privileged correction.

### Offline

* local operation;
* persistence;
* synchronization;
* duplicate prevention;
* conflict.

### Security

* Branch isolation;
* Business isolation;
* inactive employee;
* unauthorized correction;
* device restrictions.

---

# 114. Performance Testing

Performance tests should include:

* active POS workload;
* frequent session refresh;
* concurrent handover;
* large session history;
* slow network;
* temporary network failure;
* repeated close clicks;
* synchronization after offline operation.

---

# 115. Observability

The Frontend may track:

* session open latency;
* session close latency;
* handover latency;
* correction latency;
* sync latency;
* conflict rate;
* duplicate operation prevention;
* cash UI errors.

Telemetry must not unnecessarily expose financial or personal data.

---

# 116. Cash Invariants

The following invariants are mandatory:

1. Every Cash Register belongs to exactly one Branch.
2. Every Cash Session belongs to exactly one Branch.
3. Every Cash Session belongs to one Cash Register.
4. Cross-Business Cash access is prohibited.
5. Cross-Branch Cash access requires explicit authority.
6. Cash Session identity is stable.
7. Customer-facing identifiers are not technical identities.
8. Cash Session state is Backend-authoritative.
9. Cash Register state is Backend-authoritative.
10. Expected Cash is Backend-authoritative.
11. Actual Cash is Backend-authoritative after submission.
12. Discrepancy is Backend-authoritative.
13. Cashier identity is attributable.
14. Device context is retained where required.
15. Opening a session is idempotent.
16. Closing a session is idempotent.
17. Handover is idempotent.
18. Correction is idempotent.
19. Duplicate clicks cannot create duplicate cash operations.
20. Closed sessions cannot be normally reopened.
21. Historical sessions are not silently overwritten.
22. Corrections create new history rather than rewriting the original.
23. Correction requires permission.
24. Privileged correction requires stronger authorization where configured.
25. Correction limits cannot be bypassed through the UI.
26. Opening Cash is explicitly recorded.
27. Actual Cash is explicitly recorded.
28. Shortage remains visible.
29. Surplus remains visible.
30. Discrepancy is not silently normalized.
31. Cash count uses centralized money handling.
32. Frontend does not become cash financial authority.
33. Frontend does not independently recalculate authoritative expected cash.
34. Frontend does not independently recalculate authoritative discrepancy.
35. Payment effects are determined by Backend.
36. Refund effects are determined by Backend.
37. Expense effects are determined by Backend.
38. Cash Handover is distinct from Cash Session.
39. Cash Handover does not automatically imply a new session unless defined.
40. Incoming cashier identity is validated.
41. Handover confirmation is explicit.
42. Handover discrepancy remains attributable.
43. Recount does not erase the previous count.
44. Owner notification does not require Owner approval for every normal operation.
45. Branch switching cannot silently move an active Cash Session.
46. Business switching invalidates incompatible cash context.
47. Active Cash Session context remains visible.
48. POS uses the active Cash Session context.
49. POS cannot bypass Cash Session rules.
50. Offline mode cannot grant new cash authority.
51. Offline mode cannot create a trusted device.
52. Offline mode cannot extend authorization.
53. Offline mode cannot bypass subscription restrictions.
54. Offline Cash operations use operation UUIDs.
55. Offline Cash operations remain attributable.
56. Offline Cash operations remain synchronized.
57. Synchronization conflicts are explicit.
58. Unknown operation results are reconciled.
59. Non-idempotent cash operations are not blindly retried.
60. Cash cache is non-authoritative.
61. Cash cache preserves Business isolation.
62. Cash cache preserves Branch isolation.
63. Cache invalidation follows relevant cash changes.
64. Historical session queries are paginated.
65. Large session history is not loaded into memory at once.
66. Cash session filters respect authorization.
67. Direct session links validate authorization.
68. URL identifiers are not authorization evidence.
69. Loading states distinguish initial load and mutation.
70. Empty history is not an error.
71. Temporary errors provide recovery actions.
72. Financial values are centrally formatted.
73. Negative discrepancy is explicitly labeled.
74. Positive discrepancy is explicitly labeled.
75. Color is not the only discrepancy signal.
76. Keyboard input is supported.
77. Touch input is supported where POS hardware requires it.
78. Screen reader state is meaningful.
79. Reduced motion is respected.
80. Destructive actions use confirmation where appropriate.
81. Routine operations avoid unnecessary confirmation.
82. Error messages explain cause and recovery.
83. Sensitive technical details are not exposed to users.
84. Secrets are never displayed.
85. Sensitive financial data is not unnecessarily logged.
86. Cash UI remains responsive on ordinary POS hardware.
87. Session state load target is p95 ≤300 ms after API response.
88. Cash action local feedback target is p95 ≤100 ms.
89. Session close UI feedback target is p95 ≤100 ms.
90. Active session restoration target is p95 ≤500 ms.
91. Historical session list target is p95 ≤300 ms after API response.
92. Background work must not block routine POS operations.
93. Reporting must not block cash operations.
94. XLSX export must not block cash operations.
95. Synchronization must not block local UI responsiveness.
96. Cash operations remain attributable to the responsible employee.
97. Important cash operations retain device context.
98. Important cash operations retain operation identity.
99. Cash history remains reconstructable.
100. Correction history remains reconstructable.
101. Handover history remains reconstructable.
102. Session history remains reconstructable.
103. Branch identity remains reconstructable.
104. Business identity remains reconstructable.
105. Cash UI does not duplicate conflicting business rules.
106. Cash components use centralized API/data boundaries.
107. Cash components do not directly access persistence.
108. Cash UI does not silently alter historical state.
109. Security takes priority over client convenience.
110. Historical integrity takes priority over UI convenience.
111. Correctness takes priority over optimistic state when authoritative results conflict.
112. Cash architecture remains modular.
113. Cash architecture supports the current one-register-per-Branch model.
114. Cash architecture does not prevent future multi-register support.
115. Cash workflows remain simple for routine cashier operations.
116. Cash security must not create unnecessary friction.
117. Cash Session state remains explicit throughout the POS workflow.
118. The UI must never claim cash success before authoritative confirmation.
119. The UI must never claim a session is closed before authoritative confirmation.
120. The UI must never claim a handover is complete before authoritative confirmation.

---

# 117. Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/README.md`
* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/18_Offline-First_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/19_Synchronization_and_Conflict_UI.md`
* `docs/04_Architecture/07_Frontend/20_Frontend_State_Management.md`
* `docs/04_Architecture/07_Frontend/21_Frontend_API_and_Data_Layer.md`
* `docs/04_Architecture/07_Frontend/22_Frontend_Caching_and_Performance.md`
* `docs/04_Architecture/07_Frontend/23_Frontend_Security.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/17_Shift_Handover_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`

### System Analysis

* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/10_Shift_Handover.md`
* `docs/02_System_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 118. Status

**Document:** `11_Cash_Register_and_Cash_Session_UI.md`

**Status:** Proposed

**Version:** 1.0

**Frontend Architecture Documentation:** In Progress

**Previous Document:** `10_Order_Management_UI.md`

**Next Document:** `12_Inventory_and_Warehouse_UI.md`

