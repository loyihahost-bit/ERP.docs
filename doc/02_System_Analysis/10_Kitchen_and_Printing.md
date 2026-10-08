# Kitchen and Printing

**Document ID:** SA-10
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines the system behavior for kitchen operations, kitchen order notifications, kitchen printing, printer routing, print states, retry handling, and the relationship between kitchen processing and core POS transactions.

The objective is to ensure that accepted Orders are reliably communicated to the kitchen without allowing printer failures to corrupt or roll back the core business transaction.

---

## 2. Kitchen System Scope

The Kitchen system is responsible for:

* receiving accepted Order information;
* presenting kitchen-relevant Order items;
* tracking kitchen preparation status;
* routing Orders or items to configured printers;
* maintaining print state;
* recording print attempts;
* handling printer failures;
* supporting retry operations;
* preserving kitchen history.

The Kitchen system is not responsible for:

* creating payments;
* calculating cash sessions;
* directly changing inventory;
* authorizing discounts;
* changing the financial value of an Order.

---

## 3. Relationship to POS

The POS system is the source of the core Order transaction.

The general flow is:

```text id="k8p3w5"
POS
  ↓
Order Accepted
  ↓
Atomic Inventory Deduction
  ↓
Kitchen Event
  ↓
Kitchen Processing / Printing
```

The kitchen event is a secondary operation.

A failure in printing must not roll back an already successful Order acceptance and inventory transaction.

---

## 4. Accepted Order as Kitchen Trigger

An Order becomes eligible for kitchen processing after successful acceptance.

Acceptance requires successful completion of the core transaction, including required inventory deduction.

If inventory deduction fails:

```text id="s4n7c2"
Order Acceptance
      ↓
Inventory Validation
      ↓
FAIL
      ↓
Order remains unaccepted
      ↓
No Kitchen Event
```

Therefore, the kitchen must not receive an operational production event for an Order that was not successfully Accepted.

---

## 5. Kitchen Event

After successful Order acceptance, the system creates a kitchen event.

The event contains sufficient context to identify:

* Business;
* Branch;
* Order;
* Order items;
* relevant item quantities;
* table/order type;
* waiter context where applicable;
* Order number;
* timestamp;
* event UUID.

The kitchen event must be idempotent.

---

## 6. Kitchen Event Identity

Every kitchen event has a unique UUID.

The UUID prevents duplicate processing when:

* the POS retries;
* the network times out;
* a background worker retries;
* a printer request is repeated;
* synchronization occurs.

Repeated processing of the same kitchen event must not create duplicate business transactions.

---

## 7. Kitchen Notification vs Printer Output

Kitchen notification and printer output are related but separate concerns.

An accepted Order may be visible to a kitchen workstation even if a physical printer is unavailable.

Similarly, printer delivery may fail while the Order itself remains valid.

The system must therefore preserve the Order independently from its print state.

---

## 8. Kitchen Order View

The kitchen view should show relevant operational information such as:

* Order number;
* Order type;
* table where applicable;
* Order items;
* quantities;
* item modifications;
* extras;
* removals;
* notes/comments where permitted;
* preparation status;
* timestamps.

Financial information should only be shown where required by the configured workflow and permissions.

---

## 9. Order and Item Status

The Order lifecycle is:

```text id="p6m2r8"
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

`Cancelled` is a terminal cancellation outcome and is not part of the normal preparation progression.

Kitchen operations primarily work with:

* Accepted;
* Preparing;
* Ready;
* Served.

---

## 10. Preparing State

When kitchen processing begins, the relevant Order or item may move to `Preparing`.

The status change must be authorized according to the kitchen workflow.

The system records:

* previous status;
* new status;
* actor;
* timestamp;
* source/device where applicable.

---

## 11. Ready State

When preparation is complete, the relevant Order or item may move to `Ready`.

The system must preserve the status transition history.

Ready does not automatically mean:

* Paid;
* Served;
* Completed.

Payment and operational lifecycle remain independent.

---

## 12. Served State

`Served` represents that the operational Order has been served to the customer.

It is the final normal operational state.

There is no `Completed` state.

Payment completion does not automatically set an Order to Served.

---

## 13. Item-Level Kitchen Status

The system may track preparation status at item level where the business workflow requires it.

For example:

```text id="t5v8q1"
Order 125

Lavash × 2 → Preparing
Hotdog × 1 → Ready
```

Item-level status allows kitchen staff to process different products independently.

The Order remains traceable as one operational Order.

---

## 14. Item-Level Status and Order Status

The system may derive or display overall Order preparation state from its item states.

However, item-level state must not alter financial information automatically.

Changing an item from Preparing to Ready does not change:

* Order price;
* Payment;
* Inventory history;
* Discount;
* Cash Session.

---

## 15. Partial Preparation

Different items in the same Order may reach different preparation states.

The system must allow this where configured.

Example:

```text id="y3c7m2"
Order 125

Item A → Ready
Item B → Preparing
Item C → Preparing
```

This does not require splitting the Order into separate financial Orders.

---

## 16. Product-Based Printer Routing

Printers may be configured according to product or category.

Example:

```text id="h4n9x6"
Pizza Products
      ↓
Pizza Printer

Lavash Products
      ↓
Hot Food Printer

Drinks
      ↓
Drinks Printer
```

Routing is Branch-specific.

A product may therefore be printed on the printer assigned to its operational category or configured routing rule.

---

## 17. Multiple Kitchen Printers

A Branch may have multiple kitchen printers.

The system must support routing different products or categories to different printers.

The architecture must not assume that a Branch has only one printer.

---

## 18. Printer Configuration

Printer configuration may include:

* printer identity;
* Branch;
* printer type;
* connection information;
* active/inactive state;
* assigned products/categories;
* routing priority where required.

Printer configuration changes must not modify historical print records.

---

## 19. Printer Types

The system may support different physical printer configurations.

The exact transport mechanism is implementation-specific and may include:

* network printers;
* local/USB-connected printers;
* other supported POS printer interfaces.

The System Analysis does not require one specific hardware protocol.

---

## 20. Printer Availability

A printer may become unavailable because of:

* power failure;
* network failure;
* disconnected device;
* driver failure;
* paper or hardware issue;
* application communication failure.

Printer availability is independent of Order validity.

---

## 21. Print State

Each print request must have an explicit state.

The supported states are:

```text id="j7r2p5"
Pending
   ↓
Printing
   ↓
Printed
```

Failure path:

```text id="m6x4c9"
Pending / Printing
       ↓
     Failed
       ↓
   Retrying
       ↓
 Pending / Printing
```

The exact internal worker state may be implementation-specific, but the business-visible result must distinguish successful, pending and failed printing.

---

## 22. Print Attempt History

Every print attempt must be traceable.

The system should retain:

* Print Job UUID;
* Kitchen Event UUID;
* Order UUID;
* Printer UUID;
* attempt number;
* start time;
* completion time;
* result;
* failure reason where available.

This prevents repeated printer failures from becoming invisible.

---

## 23. Print Idempotency

A print operation must be protected against accidental duplicate processing.

Retrying the same print job must not unintentionally create multiple business Orders.

The system must distinguish:

* duplicate business transaction;
* repeated print attempt.

A print retry is not a new Order.

---

## 24. Printer Failure Must Not Roll Back POS

If an Order is successfully Accepted and inventory is successfully deducted, printer failure must not reverse the transaction.

Example:

```text id="c9v4k7"
Order Accepted
     ↓
Inventory Deducted
     ↓
Kitchen Event Created
     ↓
Printer Failure
     ↓
Order remains Accepted
Inventory remains deducted
Print Job = Failed
```

The system then provides retry/recovery mechanisms.

---

## 25. Retry Mechanism

Failed print jobs may be retried automatically or manually according to system policy.

Automatic retry should use bounded retry logic.

Manual retry requires appropriate permission where required.

A retry must reuse the original business context and Print Job identity or a controlled retry identity.

---

## 26. Retry Limit

Printer retries must be bounded.

After the configured retry limit is reached:

* Print Job remains `Failed`;
* failure is logged;
* authorized users can see the failure;
* appropriate notification may be generated;
* the Order remains valid.

The retry policy must not block POS operations.

---

## 27. Manual Retry

Authorized users may manually retry a failed print job.

Manual retry must:

* verify current printer configuration;
* verify Branch context;
* preserve original Order UUID;
* preserve original Kitchen Event UUID;
* record the retry actor;
* record the retry timestamp;
* preserve previous failures.

---

## 28. Printer Replacement

A failed printer may be replaced by another configured printer.

Replacing a printer does not modify:

* Order;
* inventory transaction;
* payment;
* Table Visit/Session;
* historical financial data.

A new printer may process a retry if authorized and correctly configured.

---

## 29. Printer Configuration Change

If routing configuration changes after an Order has already been accepted, the system must preserve the original print context.

A retry may use:

* the original printer, if still valid;
* an authorized replacement printer;
* the current valid routing configuration when the business explicitly retries through a new route.

Historical print attempts remain unchanged.

---

## 30. Duplicate Print Protection

The system must protect against duplicate printing caused by:

* POS retry;
* worker retry;
* lost network response;
* device restart;
* synchronization;
* manual retry.

Where duplicate physical printing cannot be technically prevented, the system must at minimum preserve print-job identity and attempt history so the duplicate can be identified.

---

## 31. Kitchen Event Failure

Creation of the kitchen event is part of the post-acceptance operational process.

If the secondary kitchen event delivery fails:

* the core Order transaction remains valid;
* inventory remains deducted;
* the failure is recorded;
* retry is scheduled;
* authorized users can inspect the failure.

The system must not silently lose the kitchen event.

---

## 32. Kitchen Event Recovery

A recoverable kitchen event failure should follow:

```text id="x5q8n3"
Pending
   ↓
Processing
   ↓
Failed
   ↓
Retry
   ↓
Processed
```

Retries use idempotency and preserve the original event context.

---

## 33. Offline Kitchen Operation

Offline POS operation may continue on trusted devices.

When an Order is Accepted offline:

* the local Order is retained;
* local inventory rules are applied;
* the local kitchen event is generated;
* local printer processing may occur if available;
* synchronization later sends the relevant event data to the server.

---

## 34. Offline Print

Offline printing may continue when the trusted device can communicate with the configured local printer.

A printer does not need Internet access if the local printing mechanism works independently.

However, offline printing must not be interpreted as server synchronization.

The local print state and server synchronization state are separate concerns.

---

## 35. Offline Kitchen Status

Authorized kitchen staff may update preparation statuses offline where permitted.

The local status change is stored as an event and synchronized later.

If the server state has changed meanwhile, the system creates a conflict rather than silently overwriting the server state.

---

## 36. Kitchen Status Conflict

A conflict may occur when:

```text id="d2m7v5"
Offline Device:
Preparing → Ready

Server:
Order already Cancelled
```

The server validates the event against the authoritative current state.

The system must not blindly apply an obsolete status transition.

The conflict is recorded and resolved according to the synchronization rules.

---

## 37. Kitchen and Cancellation

If an Order is cancelled after kitchen processing has started:

* the Order remains historically preserved;
* the cancellation is recorded;
* the kitchen must receive the relevant cancellation/update event where required;
* already printed output is not physically erased;
* the cancellation status is separately traceable.

Cancellation does not delete print history.

---

## 38. Kitchen and Order Modification

For permitted modifications:

* the original Order history remains preserved;
* changed items are represented by the appropriate operational event;
* the kitchen receives the necessary update or additional ticket;
* print history remains intact.

A modification must not silently rewrite an already printed kitchen ticket.

---

## 39. Removing or Reducing Items

If an Accepted Order item is removed or its quantity is reduced:

* the Order modification is audited;
* the inventory return decision is preserved;
* the kitchen receives the necessary operational update;
* the original print attempt remains historical.

The system must distinguish the original printed state from the new operational state.

---

## 40. Adding Products After Acceptance

A product added after an Order is already Accepted is represented by a new operational Order/ticket.

The new Order receives:

* its own Order UUID;
* its own kitchen event;
* its own print job(s);
* its own inventory transaction.

It remains linked to the same Table Visit/Session where applicable.

---

## 41. Kitchen Notes and Modifiers

Kitchen-relevant Order information may include:

* extras;
* removals;
* permitted comments;
* preparation instructions.

Such information must be captured in a structured or auditable form where it affects operational processing.

A kitchen note must not silently modify product price or inventory unless the corresponding business rule explicitly requires it.

---

## 42. Kitchen Visibility

Kitchen users should see only the information required for their operational responsibilities.

Access is controlled by:

* Employee identity;
* Role Permission;
* Employee Override;
* Branch Scope;
* Subscription Entitlement;
* Employee Status;
* Device authorization where applicable.

A trusted device does not independently grant kitchen permissions.

---

## 43. Branch Isolation

Kitchen data is Branch-scoped.

A kitchen user in Branch A must not automatically see or process Orders from Branch B.

Cross-branch access requires explicit authorization and valid Business context.

---

## 44. Subscription Entitlement

Kitchen functionality is subject to Business subscription entitlement.

If the subscription no longer includes a relevant modifying feature:

* new modifying operations are blocked;
* existing historical kitchen information remains viewable where permitted;
* offline authorization must not bypass the entitlement;
* server validation remains authoritative.

---

## 45. Kitchen Audit

Important kitchen operations must be auditable.

Examples include:

* status changes;
* cancellation events;
* item preparation changes;
* manual print retries;
* printer configuration changes;
* routing changes;
* conflict resolutions.

Audit context includes relevant:

* Event UUID;
* Business UUID;
* Branch UUID;
* Employee/System actor;
* Device UUID;
* Order UUID;
* Kitchen Event UUID;
* Printer UUID where applicable;
* timestamp;
* previous state;
* new state;
* reason where required;
* source.

---

## 46. Kitchen Notifications

Important kitchen failures may generate application notifications.

Examples:

* repeated printer failure;
* failed kitchen event;
* unresolved kitchen synchronization conflict.

Notifications must not block POS.

Notification failure must not roll back the core Order transaction.

---

## 47. Kitchen and Reporting

Reports may include:

* kitchen processing times;
* Order status history;
* printer failures;
* print attempts;
* failed kitchen events;
* cancellation events;
* item-level preparation states.

Reporting must use the authoritative historical data.

Heavy reports should run in the background.

---

## 48. Historical Integrity

The system must preserve:

* original Order state;
* Order item history;
* kitchen event history;
* print attempt history;
* printer configuration history where required;
* status transition history.

Historical records must not be silently overwritten.

---

## 49. Transaction Boundaries

The following distinction must remain explicit:

### Core transaction

Includes operations such as:

* Order acceptance;
* required inventory deduction;
* core Order state change.

### Secondary kitchen processing

Includes:

* kitchen event delivery;
* printer communication;
* print retry;
* kitchen notification.

A failure in secondary kitchen processing must not roll back a successfully committed core transaction.

---

## 50. Concurrency

Kitchen operations must support concurrent activity safely.

Examples:

* cashier accepts an Order while kitchen opens it;
* multiple kitchen users update different items;
* printer worker retries while another worker is processing;
* cashier modifies an Order while kitchen is processing it.

The system must use transaction isolation, locking, version checks or equivalent mechanisms appropriate to the operation.

Stale client state must not silently overwrite newer authoritative state.

---

## 51. Idempotent Kitchen Processing

Kitchen operations that can be retried must be idempotent.

The same event or request UUID must not produce duplicate business effects.

Repeated processing may return the previously recorded result.

---

## 52. Error Classification

Kitchen-related errors must be classified as:

* Validation Error;
* Authorization Error;
* Conflict;
* Business Rule Violation;
* Temporary Infrastructure Error;
* Permanent Failure.

The user-facing message must remain business-safe.

Technical diagnostic information belongs in structured logs.

---

## 53. Background Processing

Printer communication and heavy secondary processing should run asynchronously where appropriate.

Background workers must support:

* queueing;
* retry;
* retry limits;
* failure state;
* structured logging;
* idempotency;
* dependency ordering.

Worker failure must be recoverable.

---

## 54. Performance

Kitchen processing must not unnecessarily slow down POS.

The POS should not wait for:

* physical printer completion;
* slow printer communication;
* background report generation;
* non-critical kitchen notification delivery.

The system should return the core POS result as soon as the core transaction is safely committed.

---

## 55. System Invariants

The following invariants apply to Kitchen and Printing:

1. Only successfully Accepted Orders create normal kitchen processing events.
2. Failed inventory deduction prevents Order acceptance and therefore prevents the corresponding kitchen event.
3. Kitchen events have unique UUIDs.
4. Kitchen events are idempotent.
5. Printer failures do not roll back successful Order acceptance.
6. Printer failures do not automatically reverse inventory.
7. Print jobs have explicit states.
8. Print attempts are historically traceable.
9. Retrying a print does not create a new Order.
10. Multiple kitchen printers may exist in one Branch.
11. Printer routing is Branch-scoped.
12. Product/category routing may determine the target printer.
13. Printer configuration changes do not rewrite historical print attempts.
14. A replaced printer does not alter historical Orders.
15. Failed print jobs remain visible until resolved or retained according to policy.
16. Retry limits are bounded.
17. Manual retries are auditable.
18. Kitchen status changes are separate from payment status.
19. Payment completion does not automatically mark an Order Served.
20. There is no Completed Order state.
21. Item-level kitchen states may differ within one Order.
22. Item-level kitchen status changes do not automatically modify price.
23. Item-level kitchen status changes do not automatically modify payment.
24. Kitchen status changes do not independently perform inventory transactions.
25. Accepted Order modifications preserve historical print information.
26. Removing/reducing items preserves the original print history.
27. Adding a product after acceptance creates a separate operational Order/ticket.
28. Offline kitchen events remain locally traceable until synchronization.
29. Offline status changes are validated by the server during synchronization.
30. Offline conflicts are explicit and never silently overwritten.
31. Kitchen data is isolated by Business and Branch.
32. Employee permissions apply to kitchen operations.
33. Trusted Device status does not grant kitchen permissions.
34. Subscription entitlement applies to kitchen functionality.
35. Kitchen notifications do not block POS.
36. Notification failure does not roll back core transactions.
37. Background printer processing does not block POS.
38. Duplicate requests do not create duplicate business effects.
39. Core transaction failures roll back atomically.
40. Secondary kitchen failures do not roll back committed core transactions.
41. Historical Order and kitchen records remain traceable.
42. Audit records preserve important kitchen state changes.
43. Server state remains authoritative after synchronization.
44. Business correctness and historical integrity take priority over printer convenience.

---

## 56. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/09_Table_and_Waiter_Management.md`
* `docs/02_System_Analysis/11_Payment_System.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 57. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `10_Kitchen_and_Printing.md`

**Next Document:** `11_Payment_System.md`

