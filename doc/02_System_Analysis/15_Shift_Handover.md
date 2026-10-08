# Shift Handover

**Document ID:** SA-15
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for cashier shift handover.

Shift handover transfers operational responsibility from one cashier to another while preserving the historical identity of the previous Cash Session and creating a new Cash Session for the incoming cashier.

The process must preserve:

* cash accountability;
* Order continuity;
* payment history;
* cashier identity;
* Device identity;
* Cash Register identity;
* audit history;
* Branch context.

---

## 2. Scope

This document covers:

* handover initiation;
* previous cashier session closing;
* physical cash counting;
* discrepancy handling;
* incoming cashier authentication;
* cash acceptance;
* new Cash Session creation;
* opening cash;
* open Orders during handover;
* payment transition;
* trusted devices;
* offline handover;
* audit;
* notifications;
* synchronization;
* concurrency;
* failure recovery.

---

## 3. Core Handover Model

The standard handover flow is:

```text id="h8p3m6"
Previous Cashier
      ↓
Close Previous Cash Session
      ↓
Count / Accept Cash
      ↓
New Cashier Authenticates
      ↓
Open New Cash Session
      ↓
Continue Operations
```

The physical Cash Register remains the same.

The Cash Session changes.

---

## 4. Identity Separation

The system must distinguish:

* Previous Employee UUID;
* New Employee UUID;
* Previous Cash Session UUID;
* New Cash Session UUID;
* Cash Register UUID;
* Previous Device UUID;
* New Device UUID.

Handover must never replace the identity of the previous session with the identity of the new cashier.

---

## 5. Previous Cashier

The previous cashier remains the owner of the previous Cash Session.

All operations performed before session closure remain associated with:

* previous cashier;
* previous Cash Session;
* relevant Device;
* Cash Register;
* Branch.

This history remains immutable.

---

## 6. Closing Previous Cash Session

The previous cashier must close the active Cash Session before the handover is completed.

The closing process follows the Cash Session rules:

1. Cashier initiates close.
2. Physical cash is counted.
3. Actual cash amount is entered.
4. Expected amount is calculated.
5. Difference is shown.
6. Required comment/reason is collected.
7. Session close is committed.

The session then becomes Closed.

---

## 7. Physical Cash Count

The physical cash count is performed by the cashier responsible for the previous session.

The system does not expose expected cash before the actual physical count is entered.

After entry, the system displays:

* expected cash;
* actual cash;
* difference;
* relevant payment totals;
* Order count;
* required session information.

---

## 8. Handover Discrepancy

If the previous session has a shortage or overage:

* the discrepancy remains attached to the previous Cash Session;
* it remains associated with the previous cashier;
* the incoming cashier does not automatically inherit the discrepancy.

The discrepancy cannot be silently transferred to the new session.

---

## 9. Incoming Cashier Authentication

The incoming cashier must authenticate using their own employee account.

The system validates:

* employee identity;
* employee status;
* Business;
* Branch;
* role and permissions;
* subscription entitlement;
* trusted device status where required.

A shared operational employee account must not be used for normal handover.

---

## 10. Incoming Cashier Permissions

Authentication alone does not grant permission to operate the Cash Register.

The system calculates effective permissions from:

* Role Permission;
* Employee Override;
* Branch Scope;
* Subscription Entitlement.

The incoming cashier may only perform operations allowed by their effective permissions.

---

## 11. Cash Acceptance

After the previous session is closed, the incoming cashier counts and accepts the physical cash available for the new session.

The incoming cashier records the amount that becomes the opening cash of the new Cash Session.

The system must preserve the previous session's closing amount separately.

---

## 12. New Cash Session

The handover creates a new Cash Session.

The new session receives:

* new Cash Session UUID;
* new cashier identity;
* new opening timestamp;
* new opening cash amount;
* same Business;
* same Branch;
* same Cash Register.

The previous session UUID is not reused.

---

## 13. Cash Register Continuity

The physical Cash Register remains unchanged.

Therefore:

```text id="c6v2n8"
Cash Register R1

Session A → Cashier A → Closed
Session B → Cashier B → Open
```

The Cash Register is the continuous physical operational resource.

The Cash Session is the accounting responsibility period.

---

## 14. Open Orders

Open Orders are not closed or recreated during handover.

Their:

* Order UUID;
* Table Visit/Session;
* Order items;
* price snapshot;
* operational state;
* original actor history

remain unchanged.

The incoming cashier may continue the Order according to their permissions.

---

## 15. Order Cash Session Relationship

An Order does not belong permanently to one Cash Session.

Instead, financial and operational actions are associated with the Cash Session in which they occur.

Example:

```text id="m5q9r3"
Order O1
   ↓
Accepted by Cashier A
   ↓
Cash Session A

Later Payment
   ↓
Cashier B
   ↓
Cash Session B
```

The Order UUID remains O1.

---

## 16. Historical Actor Preservation

Handover must not rewrite historical actors.

For example:

```text id="v4p8k2"
Order Accepted
Actor: Cashier A
Session: A

Payment
Actor: Cashier B
Session: B
```

Both records remain visible in history.

---

## 17. Payment Before Handover

A payment completed before the previous Cash Session closes belongs to the previous Cash Session.

The system must not move the payment to the new session merely because the Order remains open.

---

## 18. Payment After Handover

A payment completed after the new Cash Session opens belongs to the new Cash Session.

The system uses the active session context at the time of the successful payment operation.

---

## 19. Payment During Transition

A payment request that overlaps the session transition must not be silently assigned to an incorrect session.

The system must ensure that the payment is associated with a valid active Cash Session.

If the session context becomes invalid during processing, the operation is rejected or remains pending until the correct session context is established.

The payment must not be duplicated.

---

## 20. Cash Session Transition Atomicity

The transition from:

```text
Previous Session = Open
```

to:

```text
Previous Session = Closed
New Session = Open
```

must be protected against conflicting concurrent operations.

The system must not allow a state where two conflicting active sessions exist for the same applicable Cash Register/Branch context.

---

## 21. Handover Concurrency

If two users attempt to perform handover simultaneously:

* server-side concurrency control determines the first successful transition;
* later conflicting requests are rejected;
* clients refresh their session state.

The system must rely on authoritative server state rather than client assumptions.

---

## 22. Logout During Handover

Logout does not automatically close the session.

If the previous cashier logs out before completing handover:

* the session remains Open;
* no new session is automatically created;
* another authorized user may continue the handover;
* Owner or authorized employee may force-close if necessary.

All such actions are audited.

---

## 23. Force Close

Force close is an administrative recovery mechanism.

It may be used by:

* Owner;
* authorized Manager;
* another explicitly authorized role.

Force close requires a reason.

It must record:

* actor;
* timestamp;
* session;
* reason;
* Device;
* result.

Force close does not erase the original session history.

---

## 24. Handover and Table State

Handover does not reset table state.

Table occupancy remains governed by:

* Table Visit/Session;
* active Orders;
* operational Order state.

The incoming cashier sees the current table state according to their permissions.

---

## 25. Handover and Waiter State

Handover does not change waiter assignment.

Primary Waiter remains attached to the relevant Order/table context.

Temporary assisting waiter relationships remain unchanged unless explicitly modified by an authorized operation.

---

## 26. Handover and Kitchen

Handover does not reset kitchen processing.

Kitchen statuses continue independently.

For example:

```text id="q7n3m5"
Order
  ↓
Preparing
  ↓
Cashier Handover
  ↓
Still Preparing
```

The new cashier can continue permitted Order operations.

---

## 27. Handover and Inventory

Handover does not reset inventory.

Existing inventory deductions remain associated with their original Orders and transactions.

New Order acceptance after handover uses the new cashier/session context.

No inventory transaction is duplicated because of the handover.

---

## 28. Handover and Reports

Reports must preserve the separation between:

* previous cashier/session;
* new cashier/session.

A report may show:

* previous session totals;
* new session totals;
* combined Branch totals;
* Order activity across both sessions.

Historical transactions must remain attributable to the correct session.

---

## 29. Handover Discrepancy Notification

If the previous session has a relevant shortage or overage, the configured notification rules may notify the Owner or other authorized recipient.

The notification must identify the previous session and cashier.

The incoming cashier is not treated as responsible for the previous discrepancy merely because they accepted the physical cash.

---

## 30. Opening Cash for New Session

The new cashier enters the physical cash available at the beginning of the new session.

This becomes the new session's opening cash.

The system must not automatically overwrite the previous session's actual closing cash.

Both values remain separately available.

---

## 31. Cash Acceptance Confirmation

The incoming cashier must explicitly confirm acceptance of the physical opening cash according to the configured workflow.

The system records:

* accepted amount;
* cashier;
* timestamp;
* Cash Session;
* Device;
* Branch;
* Cash Register.

---

## 32. Cash Transfer Between Sessions

The handover process does not merge two Cash Sessions.

Conceptually:

```text id="w8m4p1"
Previous Session
Closing Result
       ↓
Physical Cash Handover
       ↓
New Session
Opening Cash
```

The closing result and opening amount remain separate records.

---

## 33. Handover Difference

If the previous session's closing actual cash and the new session's opening cash differ, the system must preserve both values.

The difference must not silently modify the previous session's shortage/overage.

Where configured, the discrepancy may create an alert or require an authorized explanation.

---

## 34. Handover Completion

Handover is complete only when:

1. Previous session is Closed.
2. Incoming cashier is authenticated.
3. Incoming cashier has required permission.
4. Physical cash is counted/accepted.
5. New Cash Session is created.
6. Opening cash is recorded.
7. Required audit events are committed.

After completion, the new cashier can continue normal operations.

---

## 35. Failed Handover

If any required core step fails:

* the affected transaction is rolled back;
* the previous session is not incorrectly marked Closed unless the close operation itself successfully committed;
* no duplicate new Cash Session is created;
* the user receives a business-safe error.

Retry must use idempotent operations.

---

## 36. Partial Failure

The system must protect against partial handover states.

For example, it must prevent:

```text
Previous Session Closed
+
New Session Created Twice
```

or:

```text
New Session Open
+
No Valid Previous Session Result
```

Where operations are separated by explicit business transactions, each state must remain valid and recoverable.

---

## 37. Handover Idempotency

A handover request must have a unique operation UUID where retry is possible.

If the same request is submitted repeatedly:

* the first result is preserved;
* later identical requests return the existing result;
* duplicate sessions are not created.

---

## 38. Offline Handover

Offline handover is allowed only on a trusted device with valid offline authorization.

The authorization must permit:

* the relevant employee;
* the Branch;
* the Cash Register;
* session operation;
* the applicable offline time window;
* subscription entitlement.

---

## 39. Offline Handover Identity

Offline handover preserves:

* previous Cash Session UUID;
* new Cash Session UUID;
* Cash Register UUID;
* previous Employee UUID;
* new Employee UUID;
* Device UUID.

Synchronization must not replace these identities.

---

## 40. Offline Handover Synchronization

Offline handover events are queued locally.

The synchronization process:

1. preserves original UUIDs;
2. preserves event order;
3. validates dependencies;
4. validates employee status;
5. validates permissions;
6. validates Branch and Cash Register;
7. validates session state;
8. applies idempotency;
9. records conflicts explicitly.

POS operations continue while synchronization runs in the background.

---

## 41. Offline Handover Conflict

A conflict may occur when the server state differs from the offline state.

Example:

```text id="z6q2m9"
Offline:
Cashier B opens Session B

Server:
Session A was already closed
and Session B was opened elsewhere
```

The system must not silently create another active session.

The event becomes a synchronization conflict requiring authorized resolution where applicable.

---

## 42. Conflict Resolution

Handover conflicts preserve:

* original offline event;
* server state;
* conflict reason;
* resolution decision;
* resolving actor;
* timestamp;
* resulting state.

Resolution is a separate auditable event.

---

## 43. Employee Status During Handover

If the incoming employee becomes inactive before the new session is successfully opened:

* the session opening must be rejected;
* no new active Cash Session may be created for that employee.

If employee status changes after session opening, normal active-session rules apply.

---

## 44. Permission Changes During Handover

The server evaluates the current effective permission at the point of each important operation.

A permission change during the handover process may cause a later step to fail.

The system must not rely only on permissions loaded when the workflow started.

---

## 45. Subscription Expiry During Handover

Subscription entitlement is checked server-side.

If the Business becomes read-only before a modifying handover operation completes:

* the modifying operation is rejected;
* existing historical sessions remain available;
* no offline operation may bypass the entitlement restriction.

---

## 46. Handover Audit

Important handover events must be audited.

Audit events include:

* handover initiation;
* previous session close;
* physical cash count;
* discrepancy;
* incoming cashier authentication;
* cash acceptance;
* new session creation;
* force close;
* offline handover;
* synchronization conflict;
* conflict resolution.

---

## 47. Handover Audit Context

Audit records should contain:

* Event UUID;
* Business UUID;
* Branch UUID;
* Cash Register UUID;
* previous Cash Session UUID;
* new Cash Session UUID;
* previous Employee UUID;
* new Employee UUID;
* Device UUID;
* Transaction UUID where applicable;
* timestamp;
* old state;
* new state;
* reason;
* source;
* result.

---

## 48. Notifications

Handover-related notifications may include:

* shortage;
* overage;
* force close;
* failed handover;
* important synchronization conflict.

Routine successful handover does not need to generate unnecessary notifications.

Notifications must not block the handover transaction.

---

## 49. Handover and Report Versioning

If a handover-related correction changes a finalized report:

* a new report version is created;
* the previous report version remains immutable;
* the correction is linked to the new version.

A normal handover alone does not rewrite previous report versions.

---

## 50. Security

The system must ensure that:

* previous cashier cannot impersonate incoming cashier;
* incoming cashier uses their own account;
* device trust does not grant employee permissions;
* Branch scope is enforced;
* Cash Register scope is enforced;
* offline authorization is bounded;
* session identities cannot be replaced;
* audit records cannot be modified.

---

## 51. Performance

Handover must remain suitable for normal POS hardware.

The system must not block the workflow because of:

* report generation;
* notification delivery;
* synchronization;
* audit querying;
* unrelated background jobs.

Heavy work must run asynchronously.

---

## 52. Error Handling

Handover errors are classified as:

* Validation Error;
* Authentication Error;
* Authorization Error;
* Conflict;
* Business Rule Violation;
* Temporary Infrastructure Error;
* Permanent Failure.

User-facing messages must remain business-safe.

Technical diagnostics remain in structured logs.

Retryable requests must use idempotency.

---

## 53. Transaction Boundaries

The following operations must be atomic where they represent one core transaction:

* closing the previous session;
* recording the final cash count;
* creating the new session;
* recording new opening cash;
* confirming the applicable handover state.

Secondary operations such as notifications and report generation must not roll back the committed core handover.

---

## 54. Historical Integrity

The system must preserve the complete handover history.

The following must remain traceable:

```text id="j4p8n2"
Previous Cashier
      ↓
Previous Cash Session
      ↓
Closing Cash
      ↓
Discrepancy
      ↓
Physical Handover
      ↓
New Cashier
      ↓
New Cash Session
      ↓
Opening Cash
```

No step may be silently overwritten.

---

## 55. System Invariants

The following invariants apply to Shift Handover:

1. A handover changes cashier/session responsibility, not Cash Register identity.
2. The previous Cash Session remains historically tied to the previous cashier.
3. The previous Cash Session is closed before normal handover completion.
4. A Closed Cash Session is not reopened as an active session.
5. The new cashier authenticates with their own account.
6. Authentication does not itself grant Cash Register permission.
7. Effective permission includes role, override, Branch scope and subscription entitlement.
8. The new cashier receives a new Cash Session UUID.
9. The previous Cash Session UUID is never reused.
10. The physical Cash Register remains the same during normal handover.
11. The previous session's discrepancy remains attached to the previous session.
12. The incoming cashier does not automatically inherit the previous discrepancy.
13. The incoming cashier explicitly accepts physical opening cash.
14. The new opening cash is recorded separately from the previous closing cash.
15. Closing cash and opening cash are not silently merged into one historical value.
16. Open Orders remain open during handover.
17. Order UUIDs do not change during handover.
18. Table Visits do not reset during handover.
19. Waiter assignments do not reset during handover.
20. Kitchen statuses do not reset during handover.
21. Inventory does not reset during handover.
22. Payments before transition belong to the previous Cash Session.
23. Payments after transition belong to the new Cash Session.
24. Payment during transition must have a valid session context.
25. Handover concurrency is enforced server-side.
26. Conflicting concurrent handovers are rejected.
27. Logout does not automatically close the previous session.
28. Force close requires authorization and audit.
29. Force close does not erase previous session history.
30. A failed handover must not create duplicate sessions.
31. Handover retries are protected by idempotency.
32. Offline handover requires trusted-device authorization.
33. Offline handover preserves original UUIDs.
34. Offline synchronization validates the current server state.
35. Offline conflicts are explicit.
36. Conflict resolution is separately audited.
37. Employee status is validated during important handover steps.
38. Permission changes may affect later handover steps.
39. Subscription entitlement is checked server-side.
40. Offline handover cannot bypass subscription restrictions.
41. Important handover operations are audited.
42. Handover notifications do not block the core transaction.
43. Handover does not automatically create a new report version.
44. Relevant post-handover corrections may create new report versions.
45. Historical actor and session context remains immutable.
46. Business and Branch isolation applies throughout the handover.
47. Device identity is retained for every relevant handover event.
48. Cash Register identity remains distinct from Cash Session identity.
49. Previous and new session identities remain separately reportable.
50. Core handover state changes are atomic.
51. Secondary failures do not roll back committed handover state.
52. Background synchronization does not block normal POS operation.
53. A valid new Cash Session cannot exist without a valid Branch and Cash Register context.
54. A new session cannot be created for an inactive employee.
55. Handover must not silently transfer financial responsibility between employees.
56. Physical cash acceptance and session opening remain traceable.
57. Handover history remains available after later corrections.
58. Technical failures must not result in a false successful handover state.

---

## 56. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/12_Debt_and_Payment_Allocation.md`
* `docs/02_System_Analysis/13_Discounts_Refunds_and_Corrections.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 57. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `15_Shift_Handover.md`

**Next Document:** `16_Inventory_Transaction_System.md`

