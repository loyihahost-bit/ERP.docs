# Kitchen Domain

**Document ID:** DA-11
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/01_Domain_Overview.md`

## 1. Purpose

The Kitchen domain manages the operational preparation flow between accepted Orders and kitchen staff.

It is responsible for:

* kitchen-visible Order items;
* kitchen tickets;
* preparation status;
* item-level operational status;
* kitchen routing;
* printer routing;
* print jobs;
* print attempts;
* print failure and retry state;
* kitchen visibility;
* preparation completion;
* kitchen-related operational history.

The Kitchen domain does not own:

* Order financial state;
* Payment;
* Inventory;
* Product definitions;
* Cash Sessions;
* Employee permissions;
* Reports.

Those domains interact with Kitchen through explicit boundaries.

---

# 2. Kitchen Context

The logical relationship is:

```text id="k4m8q2"
Accepted Order
      ↓
Kitchen Ticket
      ↓
Kitchen Items
      ↓
Preparation
      ↓
Ready
```

The Order domain remains authoritative for the Order itself.

The Kitchen domain manages the preparation workflow.

---

# 3. Kitchen Trigger

Kitchen processing begins after an Order is successfully Accepted.

Order acceptance and inventory deduction must succeed before the kitchen receives the operational event.

Therefore:

```text id="r7v2n5"
Draft
  ↓
Stock Validation
  ↓
Inventory Deduction
  ↓
Order Accepted
  ↓
Kitchen Event
```

A failed inventory transaction must not create a valid kitchen preparation request.

---

# 4. Kitchen Event

The kitchen receives a secondary operational event after successful Order acceptance.

The Kitchen event must be idempotent.

If the same event is delivered more than once, it must not create duplicate kitchen tickets.

---

# 5. Kitchen Ticket

A Kitchen Ticket represents the preparation work generated from an accepted Order.

A ticket may contain:

* Ticket UUID;
* Order UUID;
* Branch;
* Cash Session context where applicable;
* source Device;
* creation time;
* relevant Order items;
* routing information;
* print state.

---

# 6. Kitchen Item

A Kitchen Item represents an individual product quantity requiring preparation.

The item retains a reference to its originating Order Item.

It may additionally contain:

* Product snapshot;
* quantity;
* modifiers;
* additions;
* removals;
* preparation notes;
* preparation status;
* routing destination.

The Kitchen Item does not become a new commercial Product.

---

# 7. Item-Level Status

The system supports item-level preparation status.

For example:

```text id="y6p3n8"
Lavash × 2 → Preparing
Hotdog × 1 → Ready
```

Different items in the same Order may therefore have different kitchen states.

---

# 8. Kitchen Status

The standard preparation flow is conceptually:

```text id="f8q2m4"
Pending
   ↓
Preparing
   ↓
Ready
```

The exact UI terminology may be configurable where already supported by the business.

The Kitchen domain must preserve valid state transitions.

---

# 9. Pending

Pending means the kitchen work exists but preparation has not started.

This may occur when:

* the ticket is newly created;
* the kitchen has not accepted the work;
* the item is waiting in the preparation queue.

Pending does not mean the Order is unpaid.

Payment and preparation state remain separate.

---

# 10. Preparing

Preparing means kitchen staff have started preparing the item.

The status change should preserve:

* actor where available;
* timestamp;
* Branch;
* Kitchen Item UUID.

---

# 11. Ready

Ready means the kitchen considers the item prepared and ready for the next operational step.

The Kitchen domain does not automatically mark the commercial Order as Served.

The Order lifecycle remains separately managed.

---

# 12. Served Boundary

Serving is an Order-level operational event.

Kitchen may report that items are Ready.

The Order domain may later transition the relevant Order context to Served.

This separation prevents kitchen staff from implicitly performing unrelated Order lifecycle operations.

---

# 13. Kitchen Visibility

Only products/items configured as kitchen-visible are sent to kitchen preparation workflows.

Products that do not require kitchen preparation may be excluded.

The visibility configuration belongs to the Product/Menu configuration model.

---

# 14. Product-Specific Visibility

Kitchen visibility may differ by Product.

For example:

```text id="c5m9r2"
Product A → Kitchen
Product B → Kitchen
Product C → No Kitchen
```

The Kitchen domain consumes the effective configuration.

It does not independently redefine Product visibility.

---

# 15. Printer Routing

A Branch may have multiple kitchen printers.

Routing may depend on:

* Product;
* Product Category;
* configured kitchen destination.

Example:

```text id="n8q4v6"
Pizza
  ↓
Pizza Printer

Lavash
  ↓
Lavash Printer

Drinks
  ↓
Drink Printer
```

The routing configuration is Branch-scoped.

---

# 16. Printer Identity

Each configured printer has a stable identity.

A printer configuration may include:

* Printer UUID;
* Branch;
* destination;
* routing rules;
* active/inactive state;
* connection configuration.

The exact technical connection mechanism belongs to Architecture/Deployment analysis.

---

# 17. Printer Failure

Printer failure must not roll back a successful ERP transaction.

For example:

```text id="w3m7p1"
Order Accepted
      ↓
Inventory Deducted
      ↓
Kitchen Event Created
      ↓
Printer Failure
```

The Order remains Accepted.

The print operation becomes a separate failed/ retryable operation.

---

# 18. Print Job

A Print Job represents an attempt to deliver a kitchen ticket to a printer.

It should retain:

* Print Job UUID;
* Kitchen Ticket UUID;
* Printer UUID;
* Branch;
* creation time;
* current state;
* attempt count;
* error information;
* last attempt time.

---

# 19. Print States

The logical print states are:

```text id="p9v4k7"
Pending
   ↓
Printing
   ↓
Printed
```

Failure may produce:

```text id="h2m8q5"
Failed
   ↓
Retrying
   ↓
Printed
```

A permanently failed job remains historically identifiable.

---

# 20. Print Attempt History

Every meaningful print attempt should be traceable.

The system may preserve:

* attempt number;
* timestamp;
* printer;
* result;
* error classification.

This supports operational troubleshooting without modifying the original Kitchen Ticket.

---

# 21. Retry

A failed print may be retried according to the configured retry policy.

Retry must be:

* bounded;
* idempotent;
* observable;
* independent from the core Order transaction.

Repeated retry must not create duplicate Orders or inventory movements.

---

# 22. Manual Retry

Authorized employees may manually retry a failed print.

The manual retry must operate on the existing Print Job/Kitchen Ticket.

It must not create another commercial Order.

---

# 23. Duplicate Printing

The system should distinguish:

* duplicate Print Job;
* repeated Print Attempt.

A retry of an existing Print Job is not automatically a new Kitchen Ticket.

The system must prevent accidental duplicate ticket creation from synchronization retries.

---

# 24. Kitchen Ticket Identity

Kitchen Ticket identity is independent from Order identity.

An Order may have:

* one primary Kitchen Ticket;
* additional operational tickets when the Order receives a new product after acceptance.

Each new operational ticket has its own identity while remaining linked to the original Order.

---

# 25. Post-Acceptance Product Addition

If a new Product is added after the Order has already been Accepted:

```text id="q7n3m8"
Existing Order
      +
New Product
      ↓
New Operational Ticket
      ↓
Kitchen Processing
```

The original Order identity remains unchanged.

The new kitchen work is independently identifiable.

---

# 26. Product Removal

Removing or reducing an accepted item follows the Order domain's modification rules.

Kitchen must receive the corresponding operational update.

The Kitchen domain must not independently decide inventory return.

Inventory return remains an Order/Inventory responsibility.

---

# 27. Kitchen Modification

If an accepted item changes before preparation is complete, the Kitchen state must reflect the latest valid operational instruction.

The exact modification behavior depends on the Order modification event received.

Historical kitchen actions must remain identifiable.

---

# 28. Already Prepared Item

If an item has already reached Ready, the Kitchen domain must not silently erase its preparation history.

Any later correction or cancellation must be represented as a separate operational event.

---

# 29. Kitchen and Payment

Kitchen preparation does not depend on payment completion under the current workflow.

The Order becomes kitchen-visible after successful acceptance.

Payment remains a separate financial operation.

Therefore:

```text id="s4m9q2"
Accepted
  ↓
Kitchen Preparation

Payment
  ↓
Financial Settlement
```

---

# 30. Kitchen and Inventory

Inventory deduction occurs before the kitchen event is considered valid.

Kitchen does not independently deduct inventory.

Kitchen only consumes the operational product/preparation information required for preparation.

---

# 31. Kitchen and Order

Order owns:

* Order identity;
* commercial items;
* Order lifecycle;
* table relationship;
* paymentability.

Kitchen owns:

* preparation workflow;
* kitchen tickets;
* preparation statuses;
* printer execution.

The two domains communicate through explicit events and references.

---

# 32. Kitchen and Menu

Menu/Pricing supplies:

* Product identity;
* kitchen visibility;
* category;
* effective configuration;
* preparation-related configuration.

Kitchen consumes the valid configuration snapshot for the relevant operation.

---

# 33. Kitchen and Employee

Kitchen actions may be attributed to an employee.

Examples:

* preparation started;
* preparation completed;
* manual print retry;
* kitchen correction.

Employee permission determines whether the employee may perform the action.

Kitchen does not own the permission model.

---

# 34. Branch Scope

Kitchen operations are Branch-scoped.

A kitchen employee or device must not access another Branch's kitchen tickets without explicit cross-Branch permission.

Printer routing must remain Branch-specific.

---

# 35. Offline Kitchen

Offline branches may continue supported kitchen operations using the latest valid synchronized configuration.

Offline kitchen actions require:

* trusted device;
* valid offline authorization;
* valid Branch context;
* appropriate permission.

---

# 36. Offline Kitchen Event

If an accepted Order is created offline:

1. Order is accepted locally.
2. Inventory is deducted locally according to offline rules.
3. Kitchen event is created locally.
4. Kitchen processing may continue.
5. The event is synchronized later.

The Kitchen event must retain its original UUID.

---

# 37. Offline Print

A trusted device may create a local print job where supported.

If printing is unavailable offline:

* the ERP transaction remains valid;
* the print job may remain Pending/Failed;
* synchronization/recovery may retry it later.

Print failure must not roll back Order acceptance.

---

# 38. Synchronization

Kitchen synchronization must be idempotent.

Repeated synchronization must not create:

* duplicate Kitchen Tickets;
* duplicate Print Jobs;
* duplicate preparation events.

Stable UUIDs and event identity are required.

---

# 39. Configuration Synchronization

Kitchen routing configuration follows normal configuration synchronization rules.

Transaction synchronization must be processed before newer configuration changes when dependency requires it.

A historical kitchen event must use the configuration applicable to its transaction context.

---

# 40. Kitchen Conflict

If two devices update the same Kitchen Item concurrently:

* the server remains authoritative;
* stale updates must not silently overwrite newer state;
* a conflict may be created where required;
* authorized resolution must preserve history.

The exact conflict strategy belongs to the Synchronization/Architecture phases.

---

# 41. Kitchen History

Kitchen history should preserve:

* ticket creation;
* item creation;
* status changes;
* preparation actor;
* timestamps;
* printer jobs;
* print attempts;
* failures;
* retries;
* manual operational actions.

Historical records must not be silently deleted.

---

# 42. Kitchen Notifications

Kitchen may produce operational conditions that are consumed by the Notification domain.

Examples may include:

* repeated printer failure;
* unresolved print failure;
* significant kitchen operational issue.

Notification lifecycle remains outside the Kitchen domain.

---

# 43. Kitchen Reporting

Reports may consume:

* preparation times;
* item status history;
* ticket counts;
* printer failures;
* retry counts;
* Branch kitchen performance.

Report generation remains owned by the Report domain.

---

# 44. Aggregate Boundaries

The Kitchen domain should conceptually contain:

* Kitchen Ticket;
* Kitchen Item;
* Kitchen Printer;
* Print Job;
* Print Attempt;
* Preparation Status.

It should not contain:

* Order aggregate;
* Payment;
* Inventory;
* Cash Session;
* Product master data;
* Employee permissions;
* Reports;
* Notifications.

---

# 45. Domain Services

Potential Kitchen domain services include:

```text id="u8m3q7"
Kitchen Ticket Creation Service
Kitchen Item Status Service
Kitchen Routing Service
Printer Selection Service
Print Job Service
Print Retry Service
Kitchen Conflict Resolver
```

These are logical domain services, not necessarily separate applications.

---

# 46. Domain Events

Potential events include:

```text id="x5n8p2"
KitchenTicketCreated
KitchenItemQueued
KitchenItemPreparing
KitchenItemReady
KitchenTicketUpdated
PrintJobCreated
PrintJobPrinted
PrintJobFailed
PrintJobRetrying
KitchenConflictDetected
```

Events represent facts that have already occurred.

---

# 47. Kitchen Invariants

### Order Integration

1. Kitchen processing begins only after successful Order acceptance.
2. Failed Order acceptance does not create a valid kitchen preparation event.
3. Kitchen events are idempotent.
4. Kitchen does not create or modify Orders directly.
5. Existing Order identity remains stable.
6. New post-acceptance Products may create separate operational tickets.
7. Kitchen preparation does not automatically mark an Order as Paid.
8. Kitchen preparation does not automatically mark an Order as Served.

### Items

9. Kitchen Items reference their originating Order Items.
10. Kitchen Item quantity is preserved.
11. Product configuration relevant to preparation is preserved.
12. Different items in one Order may have different preparation statuses.
13. Kitchen status changes preserve history.
14. Ready items retain their preparation history.
15. Invalid status transitions are rejected.

### Status

16. Pending represents queued preparation work.
17. Preparing represents active preparation.
18. Ready represents completed preparation.
19. Kitchen status is separate from Payment status.
20. Kitchen status is separate from Order financial state.

### Printing

21. Printer identity is Branch-scoped.
22. Printer routing is Branch-scoped.
23. Product/category routing follows approved configuration.
24. Printer failure does not roll back Order acceptance.
25. Print Jobs have stable UUIDs.
26. Print retries do not create new Orders.
27. Print retries do not duplicate inventory deductions.
28. Print attempts remain traceable.
29. Failed Print Jobs remain identifiable.
30. Manual retry requires appropriate authorization.

### Offline

31. Offline Kitchen operations require trusted-device authorization.
32. Offline Kitchen events retain stable UUIDs.
33. Offline Kitchen events synchronize idempotently.
34. Offline print failure does not invalidate the underlying Order.
35. Offline stale configuration cannot silently rewrite historical transactions.

### Synchronization

36. Duplicate Kitchen Events are prevented.
37. Duplicate Kitchen Tickets are prevented.
38. Duplicate Print Jobs are prevented.
39. Synchronization retries are idempotent.
40. Server remains authoritative after synchronization.
41. Conflicting Kitchen updates are explicitly represented where required.
42. Historical Kitchen state is not silently overwritten.

### Security

43. Kitchen operations require authentication.
44. Kitchen operations require applicable permission.
45. Branch scope is validated.
46. Device trust is validated for offline operation.
47. Subscription entitlement is respected where applicable.

### History

48. Kitchen Ticket history is reconstructable.
49. Kitchen Item status history is reconstructable.
50. Print attempt history is reconstructable.
51. Printer failure history is reconstructable.
52. Preparation actor history is preserved.
53. Configuration relevant to historical kitchen work remains identifiable.

### Performance

54. Kitchen updates must not block the core Order transaction unnecessarily.
55. Printing is treated as a secondary operation.
56. Printer retries run independently from the core POS workflow.
57. Kitchen processing must remain usable on ordinary Branch hardware.
58. Background print processing must not unnecessarily block cashier operations.

---

# 48. Completion Criteria

The Kitchen domain is considered complete when:

* Kitchen Ticket identity is defined;
* Kitchen Item identity is defined;
* preparation lifecycle is defined;
* item-level status is defined;
* kitchen visibility is defined;
* printer routing is defined;
* Print Job lifecycle is defined;
* print failure/retry is defined;
* post-acceptance product handling is defined;
* Order boundary is defined;
* Inventory boundary is defined;
* Menu configuration boundary is defined;
* offline behavior is defined;
* synchronization/conflict handling is defined;
* Branch/security scope is defined;
* historical integrity is defined;
* aggregate boundaries are clear.

---

## Related Documents

### Previous Domain Documents

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/09_Payment_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`

### Business Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/10_Kitchen_and_Printing.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Related Domain Documents

* `docs/03_Domain_Analysis/06_Order_Domain.md`
* `docs/03_Domain_Analysis/08_Inventory_Domain.md`
* `docs/03_Domain_Analysis/10_Menu_and_Pricing_Domain.md`
* `docs/03_Domain_Analysis/15_Audit_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`

### Future

* `docs/04_Architecture/`
* `docs/05_Database/`

