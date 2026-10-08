# Cash Domain

**Document ID:** DA-07
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Cash domain manages the physical cash operation of a Branch.

It is responsible for:

* Cash Register identity;
* Cash Session lifecycle;
* opening cash;
* cash receipts;
* physical cash counting;
* expected vs actual cash;
* discrepancies;
* cashier handover;
* corrections;
* session closure;
* cash-related audit history;
* cash concurrency.

The Cash domain does not own:

* Orders;
* payment definitions;
* inventory;
* employee permissions;
* reports;
* subscription state.

Those domains interact with Cash through explicit boundaries.

---

# 2. Cash Model

The current operational model is:

```text id="v5p2r8"
Business
   ↓
Branch
   ↓
Cash Register
   ↓
Cash Sessions
```

The current business assumption is one primary Cash Register per Branch.

The architecture must not prevent future support for multiple registers.

---

# 3. Cash Register

A Cash Register represents the physical or logical register used by a Branch.

A Cash Register has a stable UUID.

It belongs to exactly one Branch.

The Cash Register identity remains stable even when:

* cashier changes;
* cash session changes;
* device changes;
* cash handover occurs.

---

# 4. Cash Register vs Device

Cash Register and Device are different concepts.

```text id="j8n3w6"
Cash Register
      │
      └── Physical operational register

Device
      │
      └── Trusted computer/device
```

A device may be replaced without changing the Cash Register identity.

Historical sessions retain the original Device UUID where applicable.

---

# 5. Cash Session

A Cash Session represents one operational cashier session for a Cash Register.

Each Cash Session has a stable UUID.

Conceptually:

```text id="m7q4p1"
Cash Register
   ├── Session A
   ├── Session B
   ├── Session C
   └── ...
```

A Cash Session belongs to:

* one Business;
* one Branch;
* one Cash Register;
* one cashier context.

---

# 6. Cash Session Lifecycle

The logical lifecycle is:

```text id="r4c8k2"
Created
   ↓
Open
   ↓
Closing / Count
   ↓
Closed
```

A closed Cash Session never returns to the Open state.

Corrections are separate operations.

---

# 7. Opening Cash Session

Opening a Cash Session requires:

* authenticated employee;
* appropriate permission;
* valid Branch access;
* valid Cash Register;
* no conflicting active session;
* valid subscription state;
* valid device context where required.

The opening cash amount is recorded when the session is opened.

---

# 8. One Active Session

The current business model permits one active Cash Session per Cash Register.

If two requests attempt to open a session concurrently:

```text id="x7m2q4"
Request A → succeeds
Request B → rejected
```

The server must enforce this constraint atomically.

The client must not be relied upon to prevent duplicate sessions.

---

# 9. Multiple Devices

The same cashier may use multiple trusted devices during one Cash Session.

All devices operate against the same Cash Session UUID.

This does not create multiple Cash Sessions.

---

# 10. Cash Session and Cashier

The Cash Session identifies the cashier responsible for the session.

When cashier responsibility changes:

```text id="t4v8n2"
Previous Cashier
      ↓
Close Previous Session
      ↓
New Cashier Authenticates
      ↓
Count / Accept Cash
      ↓
New Cash Session
```

The previous Cash Session remains permanently closed.

---

# 11. Opening Amount

The opening amount is the physical cash amount assigned to the new Cash Session.

The opening amount must be recorded with:

* amount;
* currency;
* cashier;
* Branch;
* Cash Register;
* timestamp;
* device context;
* session UUID.

---

# 12. Cash Receipts

Cash receipts originate from successful cash payments.

The Cash domain must not independently invent payment amounts.

The Payment domain records the financial transaction.

Cash receives the applicable cash impact through a controlled domain interaction.

---

# 13. Cash vs Card

Physical cash counting applies only to cash.

Card payments are recorded separately.

Therefore:

```text id="g6r2m9"
Cash Session
├── Physical Cash
└── Derived Card Totals
```

Card totals may appear in reports but do not enter the physical cash count.

---

# 14. Debt Payments

Debt payments may have cash impact when the repayment method is cash.

The Cash domain records the physical cash effect.

Debt allocation remains owned by the Debt/Payment domain.

---

# 15. Mixed Payments

A Mixed payment may contain multiple portions.

Only the cash portion affects physical cash.

Example:

```text id="p3k8w5"
Order = 100,000

Cash = 60,000
Card = 40,000

Cash Session impact = +60,000
```

The complete financial transaction remains owned by Payment.

---

# 16. Overpayment

If a customer gives more cash than the Order amount and the excess is confirmed:

* the Order receives the required payment amount;
* excess becomes a separate overpayment/additional income;
* the excess is attributed to the Business/Branch;
* cashier attribution is preserved;
* waiter attribution is preserved where applicable;
* the physical cash increase includes the full accepted amount.

The Cash domain reflects the physical cash.

The Payment domain owns the financial meaning.

---

# 17. Change Given to Customer

Cashier workflow requires:

1. Calculate required change.
2. Give full change to the customer.
3. Enter the final accepted amount.
4. If the entered amount exceeds the Order amount, request confirmation.
5. Confirmed excess is recorded as overpayment/additional income.

The Cash domain records the resulting physical cash movement.

---

# 18. Expected Cash

Expected cash is calculated from the Cash Session's valid cash movements.

Conceptually:

```text id="k7p4s1"
Expected Cash
=
Opening Cash
+
Cash Receipts
+
Cash Debt Repayments
+
Confirmed Cash Income
-
Cash Refunds
-
Other Valid Cash Outflows
±
Approved Cash Corrections
```

The exact ledger components are owned by the financial/payment and cash models.

---

# 19. Physical Cash Count

When closing a Cash Session, the cashier physically counts the available cash.

The system should not expose the expected amount before the cashier enters the actual amount.

This reduces the risk of simply matching the expected value.

---

# 20. Actual Cash

The cashier enters the actual physical cash amount.

After entry, the system calculates:

```text id="q8r1m5"
Difference
=
Actual Cash
-
Expected Cash
```

The result may be:

* zero;
* shortage;
* overage.

---

# 21. Zero Difference

If:

```text
Actual Cash = Expected Cash
```

the session closes normally.

The closing record remains immutable after closure.

---

# 22. Shortage

If:

```text
Actual Cash < Expected Cash
```

the session has a shortage.

The shortage must be preserved as part of the session history.

Where configured, the system sends a notification to:

* Owner;
* authorized Manager;
* other configured recipients.

---

# 23. Overage

If:

```text
Actual Cash > Expected Cash
```

the session has an overage.

The overage is preserved as a financial discrepancy.

It must not be silently absorbed into another transaction.

---

# 24. Closing Comment

The cashier may be required to provide a closing comment according to business configuration.

The comment may explain:

* shortage;
* overage;
* unusual event;
* operational issue;
* other relevant context.

A comment does not change the underlying financial difference.

---

# 25. Session Closure

Closing a session must:

1. Validate authorization.
2. Prevent conflicting financial operations where required.
3. Determine expected cash.
4. Collect physical cash amount.
5. Calculate difference.
6. Persist closing result.
7. Persist applicable audit events.
8. Generate required notifications.
9. Mark the session Closed.

Once closed, the session cannot become Open again.

---

# 26. Closing vs Open Orders

Open/unpaid Orders may exist when a cashier session is closed.

They are not deleted.

During handover, open Orders remain operational and may be continued by the new cashier according to permissions.

Their Order UUID does not change.

---

# 27. Payment During Handover

If a payment request arrives while a cashier transition is occurring, it must not be ambiguously assigned.

The system must resolve the session boundary explicitly.

A payment that cannot be safely assigned during the transition remains pending until the transition is complete and is then associated with the valid Cash Session.

Duplicate payment creation must be prevented.

---

# 28. Shift Handover

Cash handover is a controlled transition between Cash Sessions.

The sequence is:

```text id="y5q8n3"
Previous Cashier
       ↓
Close Previous Cash Session
       ↓
New Cashier Authentication
       ↓
Physical Cash Count
       ↓
Accept Opening Cash
       ↓
Open New Cash Session
```

The physical Cash Register remains the same.

The Cash Session UUID changes.

---

# 29. Handover Discrepancy

A discrepancy discovered during handover belongs to the previous Cash Session.

The new cashier does not automatically inherit the previous cashier's shortage or overage.

The previous session remains historically responsible for its result.

---

# 30. Handover Cash Acceptance

The new cashier accepts the physical cash amount as the opening amount of the new Cash Session.

This creates a clear boundary:

```text id="n1c6v7"
Previous Session Closing Cash
            ↓
New Session Opening Cash
```

The two records remain separate.

---

# 31. Session Logout

Logging out does not automatically close the Cash Session.

If a cashier logs out while the session remains open:

* the session remains Open;
* another authorized cashier may perform a handover;
* Owner/authorized Manager may force-close when required;
* force-close is audited.

There is no automatic close merely because of logout.

---

# 32. Force Close

Force-close is an administrative recovery operation.

It must:

* require appropriate authorization;
* preserve the current session state;
* record actor;
* record reason;
* record timestamp;
* create an audit event.

Force-close does not reopen the session later.

---

# 33. Cash Corrections

Closed sessions cannot be reopened.

If an error must be corrected:

```text id="h4m8q2"
Closed Session
      ↓
Correction Transaction
      ↓
Original Session Remains Immutable
```

A correction stores:

* original value;
* corrected value;
* reason;
* actor;
* timestamp;
* authorization context.

---

# 34. Correction Limit

The current business rule permits:

* maximum 3 ordinary corrections per session;
* one additional correction after privileged authorization.

The privileged authorization is consumed by that additional correction.

After the correction allowance is exhausted:

* the session remains closed;
* ordinary correction is rejected;
* administrative intervention is required.

---

# 35. Correction Does Not Rewrite History

Corrections must not modify the original closed-session record in place.

Instead:

```text id="f8n2k6"
Original Session Result
        +
Correction Record
        ↓
Current Derived Result
```

This preserves historical reconstruction.

---

# 36. Offline Cash Session

Trusted devices may support Cash Session operations offline within their valid offline authorization.

Offline Cash Session identity remains stable.

A locally created Cash Session keeps its UUID when synchronized.

The server must not replace it with a different session identity.

---

# 37. Offline Handover

Offline handover is allowed only when:

* the device is trusted;
* offline authorization is valid;
* the employee has required permission;
* the Cash Register context is valid;
* the operation satisfies local business rules.

The handover is synchronized later and remains idempotent.

---

# 38. Offline Closing

An offline Cash Session may be closed if permitted by the offline authorization.

The device records:

* expected cash;
* actual cash;
* difference;
* cashier;
* Branch;
* Cash Register;
* Device;
* timestamps;
* Session UUID.

The server revalidates the closure during synchronization.

---

# 39. Offline Conflict

If synchronization discovers a conflicting Cash Session state:

* the server does not silently overwrite the existing session;
* the event remains identifiable;
* a synchronization conflict may be created;
* authorized resolution is required;
* the original offline state remains preserved.

---

# 40. Cash and Inventory

Cash operations do not directly manipulate inventory.

An Order may cause both:

* inventory movement;
* cash/payment movement.

These are separate domain responsibilities coordinated through transactional boundaries.

---

# 41. Cash and Payment

Payment owns financial payment identity.

Cash owns physical cash-session impact.

A successful cash payment must produce the appropriate Cash impact.

The two domains must remain distinguishable so that:

* payment corrections;
* cash corrections;
* refunds;
* discrepancies

can be represented correctly.

---

# 42. Cash and Refund

A cash refund decreases physical cash when it is actually paid from the Cash Session.

The Refund operation remains owned by the Payment domain.

Cash records the physical cash movement.

---

# 43. Cash and Reports

Cash reports may include:

* opening cash;
* cash receipts;
* cash refunds;
* cash outflows;
* expected cash;
* actual cash;
* shortage;
* overage;
* corrections;
* cashier;
* Cash Session;
* Branch;
* Cash Register.

Report generation is owned by the Report domain.

---

# 44. Cash and Audit

Important Cash operations must be auditable.

Examples:

* session opened;
* session closed;
* handover completed;
* force-close;
* correction;
* discrepancy;
* privileged correction authorization.

Routine cash calculations do not need separate audit events when the underlying transaction is already fully auditable.

---

# 45. Cash Concurrency

Cash operations require strong concurrency control.

Important races include:

* two sessions opening simultaneously;
* payment during session closure;
* payment during handover;
* correction during reporting;
* handover during synchronization.

The Cash domain must expose transactional boundaries required to prevent ambiguous session assignment.

---

# 46. Cash Register Availability

A Cash Register must have a clear operational state.

At minimum:

```text id="z2q5v7"
Available
In Active Session
Unavailable
```

The exact state model may be refined during Architecture Analysis.

---

# 47. Cash Register Unavailability

If the Cash Register is unavailable:

* new Cash Sessions cannot be opened through it;
* existing historical sessions remain accessible;
* alternative operational handling follows future multi-register rules if supported.

A printer/device failure alone does not necessarily make the Cash Register unavailable.

---

# 48. Aggregate Boundaries

The Cash domain should contain:

* Cash Register;
* Cash Session;
* cash-session-specific state;
* cash correction state.

It should not contain:

* Order;
* Payment;
* Inventory;
* Employee;
* Subscription;
* Report.

These domains communicate through identifiers and domain operations.

---

# 49. Domain Services

Potential Cash domain services include:

```text id="c3v8n4"
Cash Session Opening Service
Cash Session Closing Service
Cash Handover Service
Cash Counting Service
Cash Correction Service
Cash Discrepancy Service
Cash Context Resolver
```

These are logical services, not mandatory separate applications.

---

# 50. Domain Events

Potential events include:

```text id="m8p2s6"
CashRegisterCreated
CashRegisterActivated
CashRegisterUnavailable
CashSessionOpened
CashSessionClosingStarted
CashSessionClosed
CashHandoverStarted
CashHandoverCompleted
CashDiscrepancyDetected
CashCorrectionCreated
CashForceClosed
```

Events represent facts.

The Cash domain remains authoritative for Cash Session state.

---

# 51. Cash Invariants

### Identity

1. Every Cash Register has one stable UUID.
2. Every Cash Register belongs to exactly one Branch.
3. Every Cash Session has one stable UUID.
4. Every Cash Session belongs to one Cash Register.
5. Every Cash Session belongs to one Branch.
6. Cash Register identity does not change during cashier handover.

### Sessions

7. Only authorized employees may open Cash Sessions.
8. Only one active session may exist per Cash Register under the current model.
9. Concurrent session opening must be resolved atomically.
10. A closed Cash Session cannot become Open again.
11. Logout does not automatically close a Cash Session.
12. Force-close is an explicit administrative operation.

### Cash

13. Opening cash is recorded when a session opens.
14. Physical cash count applies to cash, not card totals.
15. Expected cash is calculated from valid cash movements.
16. Actual cash is entered by the cashier.
17. Difference equals actual cash minus expected cash.
18. Shortage is preserved.
19. Overage is preserved.
20. Cash discrepancies cannot be silently discarded.

### Payments

21. Cash receives physical impact from successful cash payments.
22. Card payments do not increase physical cash.
23. Only the cash portion of Mixed payments affects physical cash.
24. Cash debt repayment affects physical cash when paid in cash.
25. Confirmed overpayment affects physical cash.

### Handover

26. Cashier handover closes the previous session.
27. Handover creates a new Cash Session UUID.
28. Physical Cash Register identity remains unchanged.
29. Previous-session discrepancy remains attributed to the previous session.
30. New cashier does not inherit previous discrepancy automatically.
31. Open Orders survive cashier handover.
32. Order UUIDs do not change during handover.

### Corrections

33. Closed sessions are corrected through separate correction transactions.
34. Original closed-session results remain immutable.
35. Every correction requires appropriate authorization.
36. Corrections preserve original and new values.
37. Corrections preserve actor, timestamp, and reason.
38. Correction limits are enforced server-side.
39. Privileged correction authorization is consumed when used.
40. Exhausted correction allowance requires administrative intervention.

### Offline

41. Offline Cash Sessions require valid trusted-device authorization.
42. Offline Cash Session UUIDs remain unchanged after synchronization.
43. Offline handover is subject to the same security constraints.
44. Offline closure is revalidated by the server.
45. Conflicting offline Cash state is never silently overwritten.

### Historical Integrity

46. Historical Cash Sessions remain reconstructable.
47. Device identity is preserved in historical context.
48. Cashier identity is preserved in historical context.
49. Cash corrections do not erase original state.
50. Cash discrepancies remain historically attributable.

### Concurrency

51. Session opening is concurrency-safe.
52. Payment/session transition races are explicitly resolved.
53. Duplicate session operations are idempotent where applicable.
54. Network retries must not create duplicate Cash Sessions.
55. Synchronization must not create duplicate cash movements.

### Security

56. Cash operations require authentication.
57. Cash operations require applicable permissions.
58. Branch scope is validated server-side.
59. Device trust is validated where required.
60. Subscription entitlement is enforced where applicable.

---

# 52. Completion Criteria

The Cash domain is considered complete when:

* Cash Register identity is defined;
* Cash Session lifecycle is defined;
* opening and closing are defined;
* physical cash counting is defined;
* discrepancy handling is defined;
* cashier handover is defined;
* force-close is defined;
* correction rules are defined;
* offline behavior is defined;
* payment relationship is defined;
* refund relationship is defined;
* reporting boundary is defined;
* audit boundary is defined;
* concurrency rules are defined;
* aggregate boundaries are clear.

---

## Related Documents

### Previous

* `docs/03_Domain_Analysis/README.md`
* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`

### System Analysis

* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/15_Shift_Handover.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Report_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/05_Database/`

