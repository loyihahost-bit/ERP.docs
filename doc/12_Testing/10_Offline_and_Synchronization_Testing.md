# Offline and Synchronization Testing

**Document ID:** TEST-10
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`

---

## 1. Purpose

This document defines the testing architecture and mandatory testing rules for FastFood offline operation and synchronization.

FastFood must continue supporting critical branch operations when the branch temporarily loses connectivity. Offline operation introduces additional correctness risks because the device and server may temporarily hold different states.

The purpose of this document is to verify that:

* authorized devices can operate safely while offline;
* unauthorized devices cannot obtain offline access;
* offline operations remain within the correct business and branch scope;
* operations are preserved correctly while disconnected;
* synchronization eventually produces the correct server state;
* duplicate operations do not create duplicate business effects;
* retries are safe;
* replayed operations are rejected or safely ignored;
* conflicts are detected and handled according to business rules;
* financial and inventory integrity is preserved;
* device replacement and revocation remain safe;
* synchronization failures do not silently lose business operations;
* partial synchronization can recover safely;
* offline and online behavior converge to an acceptable final state.

Offline testing is a critical part of the FastFood testing architecture. It is not an optional compatibility test.

---

# 2. Scope

This document covers testing of:

* offline authentication;
* offline authorization;
* trusted device behavior;
* branch context;
* offline operation creation;
* local operation persistence;
* synchronization;
* synchronization batches;
* operation ordering;
* operation identifiers;
* idempotency;
* retries;
* duplicate delivery;
* replay attempts;
* conflict detection;
* conflict resolution;
* partial synchronization;
* rejected operations;
* quarantined operations;
* network interruption;
* network recovery;
* device restart;
* application restart;
* clock differences;
* device replacement;
* device revocation;
* subscription validity during offline operation;
* orders;
* payments;
* cash sessions;
* inventory;
* recipes;
* refunds;
* audit records;
* notifications and derived effects;
* reconciliation;
* synchronization observability;
* synchronization performance and stability.

This document does not redefine the security policy for offline authorization. Security policy is defined by the Security documentation, especially:

`docs/11_Security/09_Offline_Authorization_and_Synchronization_Security.md`

This document defines how those requirements are verified through testing.

---

# 3. Testing Objectives

Offline and synchronization testing must prove five major properties.

## 3.1 Safety

An offline device must not perform operations outside its authorized business, branch, employee, or functional scope.

## 3.2 Durability

A successfully accepted offline operation must not disappear because of:

* application restart;
* device restart;
* temporary network loss;
* synchronization failure;
* retry;
* server restart;
* worker restart.

## 3.3 Idempotency

Repeating the same synchronization request must not repeat the business effect.

For example:

```text
One offline payment
        ↓
Sync
        ↓
Network timeout
        ↓
Client retries
        ↓
Server receives operation again
```

The final financial effect must represent one payment, not two.

## 3.4 Integrity

Synchronization must preserve business invariants.

Examples:

* no negative stock;
* no duplicate payment;
* no duplicate order completion;
* no unauthorized branch update;
* no invalid cash balance;
* no duplicated refund;
* no invalid recipe deduction.

## 3.5 Convergence

When synchronization succeeds and no unresolved conflict remains, the local and server representations must converge to the correct business state.

---

# 4. Offline Testing Model

Offline testing uses the following conceptual model:

```text
                    ┌─────────────────────┐
                    │       Server        │
                    │                     │
                    │ Authoritative State │
                    └──────────┬──────────┘
                               │
                         Synchronization
                               │
                    ┌──────────▼──────────┐
                    │   Trusted Device    │
                    │                     │
                    │ Local Offline State │
                    └─────────────────────┘
```

During normal operation:

```text
Online
Device → Server → Result
```

During offline operation:

```text
Device → Local State
          ↓
      Local Queue
          ↓
       Later Sync
          ↓
        Server
```

The test architecture must therefore verify both:

1. local behavior while disconnected;
2. reconciliation behavior when connectivity returns.

---

# 5. Test State Model

Offline tests should explicitly control connectivity state.

Recommended states:

```text
ONLINE
   ↓
NETWORK_LOST
   ↓
OFFLINE
   ↓
NETWORK_AVAILABLE
   ↓
SYNCING
   ↓
SYNC_COMPLETED
```

Failure states must also be tested:

```text
SYNCING
   ↓
PARTIAL_FAILURE
   ↓
RETRY_PENDING
   ↓
SYNCING
```

and:

```text
SYNCING
   ↓
OPERATION_REJECTED
   ↓
QUARANTINED / RESOLUTION_REQUIRED
```

The exact implementation may differ, but observable behavior must satisfy the same guarantees.

---

# 6. Offline Authentication Testing

Offline authentication must be tested independently from normal online authentication.

## 6.1 Valid Offline Authentication

Verify that:

* a previously authorized user can authenticate according to the offline policy;
* the device is trusted;
* the business context is correct;
* the branch context is correct;
* the offline validity window is respected;
* the user's permissions remain valid;
* authentication succeeds without network access.

## 6.2 Invalid Offline Authentication

Test:

* unknown user;
* disabled user;
* revoked user;
* expired offline credentials;
* revoked device;
* unknown device;
* wrong business;
* wrong branch;
* invalid authentication state;
* expired offline authorization.

The system must fail safely.

## 6.3 New Device Offline

A new device must not obtain offline access merely because the user knows valid credentials.

Test:

```text
New Device
   ↓
No Previous Trust
   ↓
Network Unavailable
   ↓
Offline Login Attempt
   ↓
Rejected
```

This is a mandatory test.

---

# 7. Offline Authorization Testing

Authentication success must not automatically imply unlimited offline authorization.

Test:

* permitted operation;
* forbidden operation;
* branch-restricted operation;
* role-restricted operation;
* resource-restricted operation;
* expired permission;
* revoked permission;
* permission changed while device was offline;
* user removed from branch;
* device revoked while offline.

The test suite must verify that offline authorization follows the approved offline policy and does not bypass normal permission boundaries.

---

# 8. Trusted Device Testing

Device trust must be tested separately from user identity.

## 8.1 Trusted Device

Verify that an approved device can:

* enter offline mode;
* retain only permitted offline data;
* create permitted operations;
* queue operations;
* synchronize later.

## 8.2 Revoked Device

Test:

```text
Trusted Device
      ↓
Device Revoked
      ↓
Network reconnects
      ↓
Revocation received
      ↓
Offline access disabled
```

The system must not continue treating the device as permanently trusted.

## 8.3 Device Replacement

Test:

1. old device has pending offline operations;
2. old device is replaced;
3. new device is registered;
4. old device is revoked;
5. pending operations are synchronized or safely resolved;
6. no duplicate business effect is created.

## 8.4 Device Data Isolation

A replacement device must not automatically inherit another device's local operation queue unless the transfer is explicitly supported and authorized.

---

# 9. Local Offline Operation Testing

Every supported offline operation must be tested for local correctness.

At minimum:

* order creation;
* order modification;
* order status changes;
* payment;
* cash session operations;
* inventory-related operations where supported;
* recipe-related operations where supported;
* permitted employee operations;
* permitted configuration operations;
* audit events.

Each offline operation should have a test verifying:

```text
Input
  ↓
Authorization
  ↓
Business Validation
  ↓
Local State Update
  ↓
Operation Recorded
  ↓
Operation Available for Synchronization
```

A local success must not be reported if the operation was not durably recorded according to the offline design.

---

# 10. Offline Order Testing

Offline order processing is one of the highest-priority synchronization scenarios.

Test:

* create order offline;
* add products;
* change quantities;
* remove products;
* apply valid discounts;
* calculate final amount;
* accept order;
* update item status where supported;
* complete payment;
* close order;
* synchronize complete order.

Verify that the server receives the correct final business meaning.

---

# 11. Offline Payment Testing

Offline payments require especially strict testing.

Test:

* one successful offline payment;
* repeated payment submission;
* application restart after payment;
* device restart after payment;
* network loss immediately after local acceptance;
* network recovery during synchronization;
* server acknowledgment lost after processing;
* retry after timeout;
* duplicate synchronization request.

The most important invariant is:

> One accepted payment operation must produce one financial effect.

A timeout must never be interpreted as proof that the payment was not processed.

---

# 12. Offline Cash Session Testing

Cash session behavior must be tested across connectivity changes.

Test:

* open cash session while offline;
* perform orders while offline;
* accept payments;
* perform permitted corrections;
* hand over cash where supported;
* close cash session offline;
* reconnect;
* synchronize session operations;
* generate final server-side report.

Verify:

* opening state;
* closing state;
* cashier identity;
* branch identity;
* persistent session identity;
* customer-facing session number;
* cash movements;
* discrepancy;
* correction count;
* final report.

Offline synchronization must not create two cash sessions from one original session.

---

# 13. Offline Inventory Testing

Inventory synchronization must preserve stock integrity.

Test:

* offline sale;
* offline recipe deduction;
* multiple offline sales;
* insufficient stock;
* stock reaching zero;
* repeated operation;
* synchronization after several operations;
* conflicting stock changes;
* rejected inventory operation.

The system must never silently produce negative stock where the business rules prohibit it.

Example:

```text
Initial Stock = 10

Device A offline:
Sell 7

Device B offline:
Sell 6

Both reconnect
```

The test must verify that the final result follows the defined inventory conflict policy rather than silently producing an invalid stock state.

---

# 14. Recipe and Semi-Finished Product Synchronization

Where recipe-related operations are supported offline, test:

* recipe version known by device;
* sale using existing recipe;
* ingredient deduction;
* semi-finished product dependency;
* recipe version changes while device is offline;
* synchronization using an outdated recipe;
* rejected operation when the recipe is no longer valid.

The test must verify that synchronization does not silently reinterpret an old operation using a different business rule.

Historical operations must preserve their original business meaning according to the approved versioning model.

---

# 15. Synchronization Queue Testing

The local synchronization queue is a critical reliability boundary.

Test:

* operation added to queue;
* queue survives application restart;
* queue survives device restart;
* queue preserves required ordering;
* successfully synchronized operation is acknowledged;
* acknowledged operation is not repeatedly applied;
* failed operation remains available for retry where appropriate;
* permanently rejected operation is separated from retryable operations;
* queue corruption or invalid operation is handled safely.

A successful local operation must not disappear simply because synchronization is temporarily unavailable.

---

# 16. Operation Identity Testing

Every synchronization operation must be uniquely identifiable according to the system's synchronization model.

Test:

* unique operation ID;
* repeated submission with same operation ID;
* different operations with different IDs;
* operation ID collision handling;
* operation ID persistence across retries;
* operation ID persistence across application restart;
* operation ID persistence across device restart.

The same operation must retain its identity throughout its lifecycle.

---

# 17. Idempotency Testing

Idempotency is mandatory for synchronization.

Test the same operation:

* once;
* twice;
* three times;
* after timeout;
* after lost acknowledgment;
* after application restart;
* after device restart;
* through repeated network retries;
* through duplicated synchronization batches.

Expected result:

```text
N deliveries of the same operation
                ↓
       One business effect
```

This must be verified for high-risk operations including:

* payments;
* refunds;
* cash movements;
* order completion;
* inventory deductions;
* employee-affecting operations where applicable.

---

# 18. Retry Testing

Retry behavior must distinguish between temporary and permanent failures.

## Retryable examples

* temporary network failure;
* server unavailable;
* timeout;
* temporary queue failure;
* temporary dependency failure.

## Non-retryable examples

* unauthorized operation;
* invalid branch;
* revoked device;
* invalid operation structure;
* permanently invalid business state.

Test:

```text
Operation
   ↓
Temporary Failure
   ↓
Retry
   ↓
Success
```

and:

```text
Operation
   ↓
Permanent Rejection
   ↓
No Infinite Retry
   ↓
Rejected / Quarantined
```

The system must not endlessly retry an operation that can never succeed.

---

# 19. Network Interruption Testing

Network interruption must be simulated at different moments.

Test network loss:

* before local operation;
* during local operation;
* immediately after local acceptance;
* during queue creation;
* during synchronization;
* after server processing;
* before acknowledgment;
* between synchronization batches;
* during retry.

The expected outcome must be deterministic and observable.

---

# 20. Partial Synchronization Testing

Synchronization may fail after only part of the queued operations has been processed.

Example:

```text
Queue:
A
B
C
D
E

Sync:
A → Success
B → Success
C → Success
D → Timeout
E → Not processed
```

Test that:

* A, B, C are not processed again unnecessarily;
* D can safely retry;
* E remains available;
* order dependencies are preserved;
* no operation is silently lost;
* final synchronization can continue.

---

# 21. Batch Synchronization Testing

Test synchronization with:

* one operation;
* small batches;
* large valid batches;
* mixed successful and rejected operations;
* duplicate operations;
* dependent operations;
* unrelated operations;
* partially processed batches.

Batch size must not change business correctness.

---

# 22. Ordering Testing

Some operations depend on previous operations.

Example:

```text
Create Order
      ↓
Add Payment
      ↓
Complete Order
```

The test suite must verify that synchronization does not incorrectly reorder dependent operations.

Test:

* correct order;
* delayed operation;
* duplicated operation;
* missing predecessor;
* predecessor rejected;
* dependent operation arriving first.

If an operation depends on another operation that is not available, the system must follow the defined dependency/rejection policy rather than creating an invalid state.

---

# 23. Replay Testing

Replay testing verifies that previously processed operations cannot be reused to create additional business effects.

Test:

1. process operation;
2. synchronize successfully;
3. capture the same operation;
4. replay it;
5. synchronize again.

Expected result:

* no duplicate business effect;
* no duplicate payment;
* no duplicate inventory deduction;
* no duplicate refund;
* appropriate audit information where required.

Replay tests must include both accidental duplicates and malicious/restricted replay scenarios.

---

# 24. Conflict Testing

Offline devices can legitimately produce conflicting changes.

Examples:

```text
Device A: Product quantity → 5
Device B: Product quantity → 7
```

or:

```text
Device A: Stock deduction
Device B: Stock deduction
```

or:

```text
Device A: Update order
Device B: Complete order
```

Conflict tests must verify:

* conflict detection;
* conflict classification;
* deterministic resolution where automatic resolution is allowed;
* rejection where automatic resolution is unsafe;
* preservation of financial/inventory integrity;
* auditability;
* user-visible resolution state when manual resolution is required.

The test suite must never assume that "last synchronization wins" is automatically safe.

---

# 25. Business-Critical Conflict Scenarios

Special tests are required for:

### Orders

* same order changed on multiple devices;
* one device completes while another modifies;
* duplicate completion;
* conflicting status changes.

### Inventory

* concurrent offline sales;
* concurrent stock adjustments;
* conflicting inventory counts;
* stock reaching zero;
* recipe deduction conflicts.

### Cash

* conflicting cash session operations;
* duplicate cash movement;
* closing session on multiple devices;
* handover conflicts.

### Refunds

* duplicate refund;
* refund against already refunded order;
* refund while original order is being modified offline.

These scenarios must be tested more deeply than ordinary data updates.

---

# 26. Subscription and Offline Validity Testing

Offline operation must respect subscription-related rules.

Test:

* subscription active before disconnect;
* device goes offline;
* valid offline period continues;
* offline validity expires;
* restricted functionality after expiration;
* reconnect after expiration;
* synchronization after expiration;
* pending operations created before expiration;
* operations created after offline authorization expires.

The test suite must distinguish between:

* operations that were validly created before expiration;
* operations created after authorization expired;
* synchronization performed after expiration.

The final behavior must follow the approved subscription and offline authorization policy.

---

# 27. Clock and Time Testing

Offline devices may have incorrect or different clocks.

Test:

* correct clock;
* clock behind server;
* clock ahead of server;
* large clock difference;
* clock changed while offline;
* daylight-saving/time-zone boundary where applicable;
* timestamp created offline and synchronized later.

Business correctness must not depend blindly on an untrusted device clock.

Time-related rejection must be deterministic and auditable.

---

# 28. Server State Changed While Device Is Offline

The server may change while a device is disconnected.

Examples:

* employee disabled;
* employee permission changed;
* device revoked;
* branch assignment changed;
* product archived;
* recipe changed;
* price changed;
* subscription changed;
* inventory changed.

Test the device reconnecting after each condition.

The synchronization process must not silently bypass the newer server-side state.

---

# 29. Rejected Operations

An operation may be rejected during synchronization.

Test:

```text
Offline Operation
       ↓
Synchronization
       ↓
Server Validation
       ↓
Rejected
```

Verify:

* rejection reason is represented safely;
* rejected operation is not repeatedly applied;
* dependent operations are handled correctly;
* local state is reconciled;
* user can understand that synchronization did not complete normally;
* audit information is preserved;
* financial or inventory discrepancies are not hidden.

Rejected operations must never simply disappear from the local queue.

---

# 30. Quarantined Operations

Operations requiring investigation or manual resolution must be isolated from ordinary retry processing.

Test:

* operation enters quarantine;
* ordinary synchronization continues where safe;
* quarantined operation is not repeatedly executed;
* operator can identify affected operation;
* final resolution is recorded;
* resolved operation cannot accidentally execute twice.

Quarantine behavior is particularly important for:

* financial conflicts;
* inventory conflicts;
* security-related rejection;
* invalid device state;
* corrupted operation data.

---

# 31. Application Restart Testing

Test application restart:

* before offline operation;
* after offline operation;
* with pending synchronization;
* during synchronization;
* after partial synchronization;
* after rejected operation;
* after successful synchronization.

Expected result:

* pending operations remain durable;
* processed operations remain recognized;
* no duplicate business effect occurs;
* synchronization can safely resume.

---

# 32. Device Restart Testing

Repeat the same scenarios across a complete device restart.

Special attention must be given to:

* local queue persistence;
* operation identifiers;
* synchronization state;
* authentication state;
* trusted device state;
* local business state.

---

# 33. Server Restart During Synchronization

Test:

```text
Device → Sync
          ↓
       Server Restart
          ↓
       Connection Lost
          ↓
         Retry
```

Verify:

* already committed operations remain committed;
* incomplete operations can safely retry;
* duplicate delivery is safe;
* server recovery does not corrupt synchronization state.

---

# 34. Synchronization Reconciliation

After synchronization, the test suite must compare relevant states.

Example:

```text
Local Expected State
        ↓
Synchronization
        ↓
Server State
        ↓
Reconciliation
```

Reconciliation must verify business meaning rather than only raw record equality.

Examples:

* order total;
* payment state;
* cash balance;
* stock quantity;
* inventory movement history;
* order status;
* audit history.

Different technical representations may be acceptable if the final business state is equivalent.

---

# 35. Offline Audit Testing

Test that important offline actions remain traceable after synchronization.

Audit evidence should allow the system to establish, where applicable:

* who performed the action;
* which device performed it;
* which business it belonged to;
* which branch it belonged to;
* when it was created;
* when it synchronized;
* whether it succeeded;
* whether it was rejected;
* whether it was retried;
* whether it was resolved.

Offline operation timestamps must not incorrectly replace synchronization timestamps.

---

# 36. Tenant and Branch Isolation Testing

Offline synchronization must never cross business boundaries.

Test:

* Device A belongs to Business A;
* Device B belongs to Business B;
* queued operation from A submitted in B context;
* wrong branch identifier;
* wrong business identifier;
* manipulated resource identifier;
* replay of another device's operation.

Expected result:

```text
Wrong Context
     ↓
Rejected
     ↓
No Business Effect
```

This is a mandatory security and data-integrity test category.

---

# 37. Data Loss Testing

Simulate:

* sudden application termination;
* device restart;
* storage interruption where testable;
* synchronization timeout;
* server outage;
* network switching;
* partial batch completion.

The test must determine whether any accepted operation can disappear without a detectable failure state.

Silent data loss is a release-blocking defect for critical offline operations.

---

# 38. Data Corruption Testing

Test invalid or corrupted local synchronization records where safely reproducible.

Examples:

* missing operation ID;
* invalid operation type;
* invalid payload;
* invalid branch context;
* malformed timestamp;
* missing dependency;
* inconsistent local status.

Expected behavior:

* operation is rejected or quarantined;
* corruption does not affect unrelated operations;
* no invalid business effect is created;
* diagnostic information is available without exposing sensitive data.

---

# 39. Offline Security Regression Testing

Offline testing must include regression tests for:

* authentication bypass;
* authorization bypass;
* branch isolation bypass;
* tenant isolation bypass;
* device trust bypass;
* replay;
* operation tampering;
* identifier manipulation;
* stale authorization;
* revoked device;
* revoked employee;
* expired offline access.

Security testing must remain aligned with:

`docs/11_Security/09_Offline_Authorization_and_Synchronization_Security.md`

---

# 40. Test Data Architecture

Offline tests require deterministic test data.

Test fixtures should define:

* business;
* branches;
* employees;
* roles;
* permissions;
* trusted devices;
* products;
* recipes;
* ingredients;
* stock;
* prices;
* orders;
* cash sessions;
* subscription state;
* synchronization operations.

Each scenario must clearly identify the expected authoritative state.

---

# 41. Multi-Device Test Matrix

A representative test matrix should include:

| Scenario               | Device A | Device B | Network  | Expected Result          |
| ---------------------- | -------- | -------- | -------- | ------------------------ |
| Normal sync            | Offline  | Online   | Restored | A synchronizes           |
| Duplicate operation    | Offline  | —        | Restored | One business effect      |
| Stock conflict         | Offline  | Offline  | Restored | Conflict policy applied  |
| Order conflict         | Offline  | Offline  | Restored | Valid final state        |
| Device revoked         | Offline  | —        | Restored | Device access restricted |
| New device             | Offline  | —        | Offline  | Login rejected           |
| Partial sync           | Offline  | —        | Unstable | Safe retry               |
| Server restart         | Syncing  | —        | Unstable | Safe recovery            |
| Replay                 | Synced   | —        | Restored | No duplicate effect      |
| Expired offline access | Offline  | —        | Restored | Policy enforced          |

The exact matrix may expand as new offline-supported functionality is introduced.

---

# 42. Test Layers

Offline behavior should not be tested only through E2E tests.

## Unit and Domain Tests

Verify:

* synchronization state transitions;
* operation classification;
* retry classification;
* conflict classification;
* business invariants;
* idempotency decisions.

## Application Tests

Verify:

* offline use-case orchestration;
* operation creation;
* synchronization workflow;
* rejection handling;
* retry handling;
* authorization context.

## Integration Tests

Verify:

* local persistence;
* synchronization transport;
* server application boundary;
* queue/worker interaction;
* transaction behavior;
* real database persistence.

## End-to-End Tests

Verify:

* actual POS offline workflow;
* network loss and recovery;
* synchronization;
* final order/payment/cash/inventory state.

No single test layer is sufficient by itself.

---

# 43. Relationship to Concurrency Testing

Offline synchronization can produce concurrency-like conditions.

However, this document focuses on:

* disconnected state;
* synchronization;
* retries;
* replay;
* conflicts caused by delayed state.

Detailed concurrent execution and race-condition testing is defined in:

`docs/12_Testing/11_Concurrency_and_Consistency_Testing.md`

Offline tests should reference concurrency tests rather than duplicate the entire concurrency strategy.

---

# 44. Relationship to Financial Testing

Offline payment, cash, and refund scenarios are high-risk financial operations.

Detailed financial testing is defined in:

`docs/12_Testing/12_Financial_and_Cash_Testing.md`

Offline tests must still verify the complete synchronization path for financial operations.

---

# 45. Relationship to Inventory Testing

Offline inventory scenarios must be integrated with:

`docs/12_Testing/13_Inventory_and_Recipe_Testing.md`

The offline suite focuses on synchronization behavior while inventory tests define the deeper inventory and recipe business rules.

---

# 46. Relationship to Security Testing

Offline authorization and device security policies are defined in:

`docs/11_Security/08_Trusted_Device_and_Device_Security.md`

and:

`docs/11_Security/09_Offline_Authorization_and_Synchronization_Security.md`

TEST-10 verifies those policies through executable test scenarios.

---

# 47. Observability During Tests

Synchronization tests should capture enough evidence to diagnose failures.

Where available, test evidence should include:

* operation ID;
* device identity;
* business/branch context;
* local operation timestamp;
* synchronization timestamp;
* synchronization attempt;
* result;
* rejection reason;
* retry state;
* conflict state;
* final business state.

Sensitive data must not be unnecessarily included in test logs.

---

# 48. Performance Testing

Offline synchronization must remain practical for branch hardware.

Performance tests should measure:

* local operation creation time;
* local queue processing;
* synchronization throughput;
* batch synchronization;
* retry overhead;
* duplicate detection;
* conflict processing;
* recovery after long offline periods.

Performance tests must use realistic branch workloads.

Correctness must never be sacrificed for synchronization speed.

---

# 49. Long Offline Period Testing

Test devices that remain offline for:

* short periods;
* several hours;
* one business day;
* multiple business days where supported;
* near the maximum supported offline validity period.

Verify:

* queue growth;
* local storage behavior;
* authorization validity;
* synchronization duration;
* conflict volume;
* memory/resource usage;
* eventual convergence.

---

# 50. Large Queue Testing

Test a device returning online with a large number of pending operations.

Verify:

* synchronization remains stable;
* batches are processed safely;
* duplicate protection remains correct;
* failures do not corrupt the remaining queue;
* the UI remains usable;
* the server remains protected from excessive load.

---

# 51. Flaky Network Testing

Simulate unstable connectivity:

```text
Online
  ↓
Offline
  ↓
Online
  ↓
Offline
  ↓
Online
```

and:

```text
Connected
   ↓
High latency
   ↓
Timeout
   ↓
Reconnect
```

The synchronization system must remain safe under repeated network transitions.

---

# 52. Critical Offline Test Suite

The following scenarios should be part of the mandatory critical regression suite:

1. valid trusted-device offline login;
2. new-device offline login rejection;
3. offline order creation;
4. offline payment;
5. offline cash session;
6. application restart with pending operations;
7. device restart with pending operations;
8. synchronization after network recovery;
9. duplicate synchronization request;
10. lost server acknowledgment;
11. partial synchronization;
12. retry after temporary failure;
13. permanent rejection;
14. replayed operation;
15. stock conflict;
16. order conflict;
17. device revocation;
18. expired offline authorization;
19. tenant/branch isolation violation attempt;
20. final reconciliation.

These tests are release-blocking when they reveal business-integrity or security defects.

---

# 53. CI Testing Strategy

Offline tests should be divided into appropriate CI layers.

## Fast CI

Run:

* state-transition tests;
* operation identity tests;
* idempotency tests;
* retry classification;
* conflict classification;
* authorization logic.

## Integration CI

Run:

* local persistence;
* synchronization;
* database transactions;
* queue behavior;
* partial synchronization;
* retry behavior.

## E2E CI

Run:

* critical POS offline workflows;
* network interruption;
* synchronization;
* payment;
* cash session;
* inventory;
* device lifecycle.

## Release Testing

Run:

* full offline regression;
* multi-device conflict scenarios;
* long offline scenarios;
* device replacement;
* subscription validity;
* performance and recovery tests.

---

# 54. Failure Classification

Offline test failures should be classified at least as:

### Data Loss

An accepted operation disappears.

**Severity:** Critical.

### Duplicate Business Effect

One operation produces multiple effects.

**Severity:** Critical.

### Security Boundary Violation

Unauthorized operation is accepted.

**Severity:** Critical.

### Financial Integrity Failure

Payment, refund, cash, or financial state becomes incorrect.

**Severity:** Critical.

### Inventory Integrity Failure

Stock becomes invalid or deductions are duplicated/lost.

**Severity:** Critical.

### Synchronization Failure

Valid operation cannot synchronize but remains recoverable.

**Severity:** High.

### Conflict Handling Failure

Conflict is incorrectly resolved or silently ignored.

**Severity:** High.

### Observability Failure

Synchronization state cannot be diagnosed.

**Severity:** Medium/High depending on impact.

---

# 55. Flaky Offline Tests

Offline tests are especially vulnerable to accidental nondeterminism.

Avoid:

* arbitrary sleeps;
* uncontrolled network timing;
* real external services;
* real device clock dependence;
* uncontrolled retry timing;
* shared synchronization queues;
* shared databases between parallel scenarios.

Network conditions, time, synchronization state, and test data should be controllable.

A test that passes only because a retry happened at the "right" time is not reliable.

---

# 56. Test Environment Requirements

A proper offline test environment should allow controlled simulation of:

* online state;
* offline state;
* intermittent network;
* high latency;
* timeout;
* server unavailable;
* server restart;
* database failure where relevant;
* synchronization retry;
* duplicate requests;
* device restart;
* application restart;
* clock differences.

Real POS hardware may be used for selected release validation, but most offline behavior must remain testable in deterministic automated environments.

---

# 57. Regression Requirements

Every discovered synchronization defect should result in a regression test when practical.

Examples:

```text
Bug:
Payment duplicated after lost acknowledgment.

Required regression:
Process payment
→ Lose acknowledgment
→ Retry same operation
→ Verify one payment
```

or:

```text
Bug:
Offline operation crossed branch boundary.

Required regression:
Create operation for Branch A
→ Submit under Branch B
→ Verify rejection
→ Verify no Branch B state change
```

The regression suite must protect against recurrence.

---

# 58. Change Impact Testing

Changes affecting any of the following require offline testing impact analysis:

* order state;
* payment;
* refund;
* inventory;
* recipes;
* cash sessions;
* permissions;
* trusted devices;
* authentication;
* subscription;
* API contracts;
* database schema;
* synchronization protocol;
* operation identifiers;
* queue behavior;
* retry behavior;
* conflict handling;
* background workers;
* offline storage.

A change to an online workflow must be evaluated for offline consequences.

---

# 59. Mandatory Offline Testing Invariants

The following invariants are mandatory:

1. A trusted device must not automatically receive unlimited authority.
2. A new device must not obtain offline access without the required trust state.
3. Offline operations must remain within the correct business and branch scope.
4. Accepted offline operations must not silently disappear.
5. Synchronization must be idempotent.
6. Replaying an already processed operation must not duplicate its business effect.
7. Temporary failures must remain retryable where appropriate.
8. Permanent failures must not enter infinite retry loops.
9. Partial synchronization must be recoverable.
10. Dependent operations must not create invalid state when prerequisites are missing or rejected.
11. Financial operations must not be duplicated.
12. Inventory deductions must not be duplicated.
13. Negative stock must not be silently introduced where prohibited.
14. Device revocation must eventually prevent further unauthorized operation.
15. Expired offline authorization must not silently continue indefinitely.
16. Tenant and branch isolation must remain enforced during synchronization.
17. Conflicts must not be silently resolved using an unsafe generic rule.
18. Rejected operations must remain observable and recoverable or explicitly finalized.
19. Device and application restarts must not corrupt pending synchronization.
20. Server restart must not cause duplicate business effects.
21. Final synchronization must produce the correct business state.
22. Critical synchronization failures must be detectable.
23. Synchronization correctness must take priority over synchronization speed.
24. Security controls must not be bypassed merely because the device is offline.
25. Every critical offline defect must have regression coverage.

---

# 60. Acceptance Criteria

TEST-10 is considered successfully implemented when:

* offline authentication scenarios are covered;
* offline authorization scenarios are covered;
* trusted and untrusted device scenarios are covered;
* local operation persistence is tested;
* synchronization success and failure are tested;
* retries are tested;
* duplicate delivery is tested;
* replay is tested;
* partial synchronization is tested;
* conflicts are tested;
* rejected and quarantined operations are tested;
* network interruption is tested;
* application/device restart is tested;
* server restart is tested;
* subscription/offline validity is tested;
* order/payment/cash workflows are covered;
* inventory and recipe synchronization is covered;
* tenant and branch isolation is verified;
* reconciliation is verified;
* critical offline tests run in CI;
* release-blocking invariants are enforced;
* synchronization defects generate regression tests.

---

# 61. Final Rule

FastFood offline operation must be treated as a distributed-system boundary rather than simply a local version of the online application.

The central testing rule is:

> An offline operation is not considered correct merely because it works locally. It is correct only when the operation remains authorized, durable, idempotent, traceable, safely synchronized, and results in the correct final business state.

Offline testing therefore covers the complete lifecycle:

```text
Authenticate
    ↓
Authorize
    ↓
Operate Offline
    ↓
Persist Locally
    ↓
Queue Operation
    ↓
Network Recovery
    ↓
Authenticate Sync
    ↓
Validate Operation
    ↓
Detect Duplicate / Replay / Conflict
    ↓
Apply Safely
    ↓
Acknowledge
    ↓
Reconcile
    ↓
Correct Final State
```

No critical offline workflow is considered production-ready until this complete lifecycle has been verified.

