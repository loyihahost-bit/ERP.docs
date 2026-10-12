# Offline Authorization and Synchronization Security

## Document Metadata

* **Document ID:** SEC-09
* **Status:** Accepted
* **Version:** 1.0
* **Scope:** FastFood ERP
* **Parent:** `docs/11_Security/README.md`
* **Previous:** `08_Trusted_Device_and_Device_Security.md`
* **Next:** `10_Data_Security_and_Data_Classification.md`

---

## 1. Purpose

This document defines the security policy for FastFood ERP operations performed while a branch device is temporarily offline.

The purpose is to ensure that offline operation does not become an alternative path around normal security controls.

The policy covers:

* offline authentication;
* offline authorization;
* offline credentials;
* device-bound authentication state;
* offline operation signatures;
* operation integrity;
* replay protection;
* sequence protection;
* clock and timestamp tampering;
* synchronization authentication;
* synchronization authorization;
* conflict handling;
* duplicate detection;
* revoked identities and devices;
* subscription state limitations;
* compromised offline devices;
* recovery after reconnection.

This document defines **security requirements and boundaries**, not implementation-specific cryptographic algorithms, frameworks, libraries, or storage technologies.

---

# 2. Scope

This policy applies to FastFood ERP functionality that may continue operating when a branch temporarily loses connectivity.

It includes:

* POS operations;
* cashier operations;
* order creation and modification;
* payment-related offline actions where explicitly supported;
* inventory operations;
* recipe-related operational actions;
* attendance where offline operation is permitted;
* branch configuration cached for offline use;
* employee authentication on trusted offline devices;
* locally queued operations;
* synchronization;
* synchronization retries;
* conflict resolution;
* offline audit events.

It applies to:

* branch devices;
* POS terminals;
* cashier devices;
* kitchen-related operational devices where applicable;
* trusted employee sessions;
* synchronization services;
* background synchronization processes.

It does not replace:

* identity security;
* authentication security;
* authorization security;
* trusted device security;
* tenant isolation;
* branch isolation;
* deployment security.

Those policies remain authoritative.

---

# 3. Security Model

Offline security follows this model:

```text
Human Identity
      +
Device Identity
      +
Business/Tenant Context
      +
Branch Context
      +
Cached Authorization
      +
Offline Authentication State
      +
Operation Integrity
      +
Replay Protection
      +
Synchronization Security
      ↓
Offline Security Decision
```

An offline device must never be treated as inherently trusted simply because it was previously connected.

Offline trust is:

* explicitly established;
* limited in scope;
* limited in time;
* bound to a trusted device;
* bound to the business and branch;
* revocable when connectivity returns;
* unable to grant permissions beyond the last authorized state.

---

# 4. Offline Security Principles

## 4.1 Offline Is a Limited Operating Mode

Offline mode is an operational continuity mechanism, not a separate security model.

The same fundamental security principles continue to apply:

* deny by default;
* least privilege;
* branch isolation;
* business isolation;
* explicit authorization;
* device trust;
* operation integrity;
* auditability;
* limited privilege;
* controlled synchronization.

---

## 4.2 Offline Capability Must Be Explicit

A function must not automatically become available offline merely because it works online.

Each operation must have an explicit offline security policy.

An operation may be:

* allowed offline;
* allowed offline with restrictions;
* queued for later synchronization;
* read-only offline;
* prohibited offline.

---

## 4.3 Offline Authorization Is Not Permanent Authorization

Cached authorization represents a previously valid authorization state.

It must not be interpreted as permanent permission.

If an employee:

* loses a permission;
* changes branch;
* is deactivated;
* is removed from the business;
* has their device revoked;
* loses access due to subscription state;

the system must apply the strongest available restriction.

Offline operation cannot guarantee immediate revocation while disconnected.

This limitation must be explicitly accepted by the security model.

---

# 5. Offline Authentication

## 5.1 Offline Authentication Requirement

Offline authentication may be permitted only on a device that has previously established a trusted authentication state.

An unknown device must not gain offline access simply because it knows an employee identifier.

---

## 5.2 Cached Authentication State

The device may retain a protected representation of the employee's previously validated authentication state.

The cached state must be:

* protected from unauthorized extraction;
* bound to the trusted device;
* bound to the business;
* bound to the appropriate branch scope;
* associated with an expiration or validity policy;
* revocable when connectivity returns.

---

## 5.3 Offline Credential Protection

Offline authentication data must not expose reusable credentials in recoverable form.

The system must not rely on storing:

* plaintext passwords;
* reusable authentication secrets;
* unrestricted long-lived session credentials.

Offline authentication material must have a limited purpose and scope.

---

## 5.4 Offline Login Restrictions

Offline login must respect the device's previously established security boundary.

The system must not allow an offline user to:

* register a new trusted device;
* expand branch access;
* create unrestricted administrative access;
* change security ownership;
* create privileged identities;
* bypass required authorization.

---

# 6. Offline Session Security

Offline sessions must remain subject to security expiration rules.

A disconnected device must not be able to maintain unlimited privileged access indefinitely.

Offline session policies should distinguish between:

* normal operational sessions;
* privileged actions;
* sensitive administrative actions.

The more sensitive the operation, the stronger the requirement for recent authentication or connectivity.

---

# 7. Offline Authorization

## 7.1 Cached Permission State

The device may cache only the permissions required for approved offline operations.

The cached authorization state must include enough context to determine:

* employee identity;
* business;
* branch;
* role;
* functional permission;
* resource scope;
* offline capability.

---

## 7.2 Authorization Decision

An offline authorization decision must follow the same conceptual chain used online:

```text
Identity
→ Business
→ Branch Scope
→ Role
→ Permission
→ Resource Scope
→ Action
→ Offline Policy
```

The offline policy is an additional constraint.

Offline mode may reduce capability but must never expand it.

---

## 7.3 Permission Changes During Offline Period

If a permission changes while a device is disconnected, the device may temporarily operate using the last valid cached state.

After reconnection:

1. the current authorization state must be refreshed;
2. queued operations must be evaluated against synchronization policy;
3. revoked future operations must not continue;
4. unauthorized queued operations must be rejected or isolated according to the conflict policy.

Previously valid and properly authorized operations must not be silently rewritten merely because the employee's permissions changed later.

---

# 8. Offline Operation Identity

Every security-sensitive offline operation must have a unique operation identity.

The operation identity must allow the system to distinguish:

* one legitimate operation;
* a duplicate submission;
* a retry;
* a replay;
* an altered operation;
* an operation originating from another device.

An operation identity must not rely only on a human-readable order number.

The system must maintain a distinction between:

* business-visible identifiers;
* database identifiers;
* synchronization identifiers;
* operation identifiers.

---

# 9. Offline Operation Integrity

Offline operations must be protected against unauthorized modification between creation and synchronization.

The security model must provide a mechanism for establishing that:

* the operation originated from an authorized device;
* the operation was created under an authorized identity;
* the operation belongs to the correct business and branch;
* the operation has not been altered;
* the operation has not been detached from its original context.

The integrity mechanism must be bound to the operation context.

At minimum, the security context must cover:

* operation identity;
* originating device;
* employee identity;
* business;
* branch;
* operation type;
* operation data;
* creation time;
* sequence information;
* authorization context.

---

# 10. Offline Signatures and Integrity Proof

Where an offline operation requires cryptographic proof, the proof must be associated with the trusted device and its authorized identity context.

An offline signature must not be treated as proof of unrestricted authority.

It proves, according to the system's trust model, that the operation was produced under an established offline security context.

The server must still validate:

* device status;
* identity status;
* business ownership;
* branch scope;
* operation type;
* authorization policy;
* validity period;
* replay state;
* synchronization state.

A valid signature must never bypass server-side authorization.

---

# 11. Replay Protection

## 11.1 Replay Threat

An attacker may attempt to submit an already accepted offline operation again.

Examples include:

* replaying a payment operation;
* replaying an inventory deduction;
* replaying an order creation;
* replaying a refund-related action;
* replaying an attendance event;
* replaying an old synchronization request.

Replay protection is therefore mandatory for security-sensitive offline operations.

---

## 11.2 Replay Detection

The system must be able to detect duplicate operations using a combination of operation identity and synchronization state.

The system must distinguish:

```text
New operation
Retry of same operation
Duplicate operation
Modified replay
Expired operation
Invalid operation
```

---

## 11.3 Idempotency

Synchronization must be designed so that retrying the same legitimate operation does not create an unintended second business effect.

For example:

```text
Offline Operation
      ↓
Sync Attempt #1
      ↓
Server accepts operation
      ↓
Response lost
      ↓
Sync Attempt #2
      ↓
Server recognizes same operation
      ↓
No second business effect
```

---

## 11.4 Replay of Modified Operations

Changing the contents of an already-known operation must cause integrity validation to fail.

The system must not treat a changed operation as the original operation.

---

# 12. Sequence and Ordering Protection

Offline operations may be created while disconnected and synchronized later.

Where operation ordering matters, the synchronization model must preserve sufficient sequence information to determine whether operations are:

* ordered correctly;
* duplicated;
* missing;
* delayed;
* conflicting.

Sequence information must not be treated as a substitute for authorization.

It exists to support integrity and synchronization correctness.

---

# 13. Clock and Timestamp Security

## 13.1 Clock Tampering Threat

A user may attempt to change the device clock to manipulate:

* session expiration;
* offline validity periods;
* attendance records;
* transaction timestamps;
* synchronization ordering;
* business reporting;
* subscription-related behavior.

Therefore, local device time must not be treated as an authoritative security source.

---

## 13.2 Trusted Time

When connected, server-controlled time is authoritative.

During offline operation, the device may use its local clock for operational continuity, but the system must recognize that local time is potentially untrusted.

---

## 13.3 Clock Rollback Detection

The system should detect suspicious changes such as:

```text
Known Time
   ↓
Device disconnected
   ↓
Local time moves backwards significantly
   ↓
Offline security state becomes suspicious
```

Suspicious clock behavior may cause:

* sensitive operations to be blocked;
* offline validity to be shortened;
* synchronization to require additional validation;
* the device to require reconnection before privileged operations continue.

---

## 13.4 Timestamp Trust Levels

Timestamps should be treated according to their source.

Possible trust levels include:

1. server-confirmed time;
2. previously observed trusted time;
3. device-generated offline time;
4. externally supplied timestamp.

Lower-trust timestamps must not override stronger server-side evidence.

---

# 14. Offline Validity Windows

Offline access must have a defined validity boundary.

The validity policy should consider:

* last successful synchronization;
* last successful authentication;
* device trust state;
* employee status;
* business status;
* branch assignment;
* sensitivity of the operation;
* maximum permitted offline duration.

Offline validity must not become unlimited merely because the device remains powered on.

---

# 15. Subscription State and Offline Operation

Subscription status may change while a branch is offline.

Because the device cannot immediately obtain the latest platform state, a controlled grace mechanism may be required for operational continuity.

However:

* offline mode must not permanently bypass subscription restrictions;
* the device must not extend subscription validity indefinitely;
* restricted functions must remain subject to the previously established offline policy;
* synchronization must reconcile the actual subscription state after reconnection.

If the subscription has expired during the offline period, the server becomes authoritative once connectivity is restored.

---

# 16. Synchronization Security Model

Synchronization is treated as a security boundary.

```text
Offline Device
      ↓
Authenticated Sync Channel
      ↓
Device Validation
      ↓
Business Validation
      ↓
Branch Validation
      ↓
Identity Validation
      ↓
Operation Integrity Validation
      ↓
Replay Validation
      ↓
Authorization Validation
      ↓
Conflict Validation
      ↓
Commit / Reject / Quarantine
```

Successful network connectivity alone is not sufficient to accept synchronization data.

---

# 17. Synchronization Authentication

A synchronization request must establish the identity of the originating device and its authorized system context.

The server must be able to determine:

* which device sent the request;
* which business owns the device;
* which branch owns the device;
* which employee or service context produced the operation;
* whether the device is still trusted.

A device must not synchronize data under another device's identity.

---

# 18. Synchronization Authorization

Synchronization must verify that the sender is authorized to submit the relevant operation.

The system must not assume:

> "The operation was created while the user was authorized, therefore it can always be accepted."

Instead, the server must apply the appropriate synchronization policy.

For each operation it must determine whether to:

* accept;
* reject;
* partially accept where explicitly safe;
* defer;
* quarantine for review.

---

# 19. Synchronization Data Boundaries

Synchronization must preserve:

* business isolation;
* branch isolation;
* employee scope;
* resource ownership;
* device ownership.

A synchronization package must never be able to cause data from one business or branch to be written into another security context.

This applies to:

* orders;
* payments;
* inventory;
* recipes;
* employees;
* attendance;
* cash registers;
* configuration;
* reports;
* audit events.

---

# 20. Synchronization Integrity

Synchronization data must be validated before it changes authoritative data.

Validation must cover:

* message integrity;
* operation identity;
* source device;
* source business;
* source branch;
* operation type;
* operation sequence;
* authorization context;
* duplicate status;
* validity period;
* required dependencies;
* business rules;
* current security state.

Failure of any mandatory security validation must prevent unauthorized state changes.

---

# 21. Conflict Security

Offline operation creates the possibility that multiple devices independently modify related business state.

Conflicts must not be resolved using security-unsafe assumptions.

The system must distinguish between:

* harmless operational conflicts;
* authorization conflicts;
* integrity conflicts;
* financial conflicts;
* inventory conflicts;
* ownership conflicts.

Security-sensitive conflicts must not automatically favor the newest client operation.

---

# 22. Financial and Inventory Synchronization

Financial and inventory operations require stronger protection because incorrect replay or duplication can directly change business value.

Examples include:

* payment;
* refund;
* cash adjustment;
* inventory receipt;
* inventory deduction;
* stock adjustment;
* purchase entry.

Such operations must have strong:

* operation identity;
* integrity validation;
* replay protection;
* authorization validation;
* auditability.

Synchronization must never create duplicate financial or inventory effects because of a retry.

---

# 23. Offline Cash Register Security

Offline cashier operation must remain associated with the correct:

* branch;
* cash register;
* cashier;
* register session;
* device.

The customer-facing short register number must not be used as the sole security identifier.

The system must retain authoritative internal identifiers for:

* register;
* register session;
* cashier;
* device;
* operation.

Offline register operations must not silently cross register sessions.

---

# 24. Offline Order Security

An offline order must preserve:

* branch ownership;
* originating device;
* cashier identity;
* order identity;
* order type;
* item information;
* operation history;
* creation context.

When synchronized, the server must prevent:

* duplicate order creation;
* cross-branch order insertion;
* unauthorized order modification;
* replayed payment effects;
* altered order history.

---

# 25. Offline Inventory Security

Offline inventory operations must remain tied to the originating branch and authorized inventory scope.

The synchronization process must validate:

* product identity;
* warehouse scope;
* branch scope;
* operation identity;
* quantity integrity;
* source information;
* operation ordering;
* duplicate state.

Offline synchronization must not permit negative inventory merely because the device was disconnected.

Existing inventory rules remain authoritative.

---

# 26. Offline Audit Events

Security-relevant offline actions must preserve enough information for later audit.

Audit information should identify:

* employee;
* device;
* business;
* branch;
* operation;
* local creation context;
* synchronization state;
* server acceptance/rejection;
* security validation result.

The system must distinguish between:

* event creation time;
* synchronization time;
* authoritative server processing time.

---

# 27. Failed Synchronization

A synchronization failure must not result in silent data loss or unauthorized repeated effects.

Failures should be categorized, for example:

* temporary network failure;
* authentication failure;
* device revoked;
* identity revoked;
* authorization failure;
* integrity failure;
* replay detected;
* expired operation;
* business/branch mismatch;
* conflict;
* invalid business state.

Retryable failures and permanent security failures must be distinguished.

---

# 28. Rejected and Quarantined Operations

Security-sensitive invalid operations must not simply disappear.

Where appropriate, rejected operations should retain enough information to support:

* audit;
* investigation;
* user notification;
* operational correction.

Quarantined operations must not affect authoritative business state until explicitly resolved.

---

# 29. Device Revocation While Offline

A device cannot immediately learn about revocation while disconnected.

Therefore, the security model must recognize a revocation propagation delay.

When connectivity returns:

1. device trust must be revalidated;
2. revoked devices must be prevented from further synchronization;
3. queued operations must be evaluated;
4. unauthorized operations must not be accepted;
5. security events must be recorded.

Offline capability must never be interpreted as immunity from revocation.

---

# 30. Employee Revocation While Offline

If an employee is deactivated or loses access while the device is offline, the device may not immediately know.

After reconnection:

* the employee's current identity state becomes authoritative;
* future access must follow the current state;
* queued operations must be evaluated according to their original authorization context and operation policy;
* new unauthorized operations must be rejected.

The system must distinguish between:

```text
Operation authorized when created
```

and:

```text
Operation attempted after authorization was revoked
```

---

# 31. Synchronization After Device Replacement

A replacement device must not automatically inherit another device's offline queue or security identity.

Pending operations must remain bound to their originating device context.

If recovery of pending operations is supported, the recovery process must explicitly establish:

* ownership;
* business;
* branch;
* source device;
* operation integrity;
* authorization;
* recovery authorization.

Device replacement must not become a mechanism for bypassing device revocation.

---

# 32. Offline Data Protection

Locally stored offline data must be treated as sensitive business data.

The system should minimize the amount of data retained offline.

Offline storage should follow:

* least data;
* least privilege;
* limited retention;
* business/branch isolation;
* protected storage;
* controlled deletion;
* secure lifecycle handling.

A device should not receive all business data merely because it can operate offline.

---

# 33. Synchronization and Tenant Isolation

Synchronization must preserve the tenant isolation requirements defined by `04_Business_and_Tenant_Isolation_Security.md`.

A synchronization payload must never be accepted solely because its identifiers appear valid.

The authoritative context must determine:

```text
Source Device
→ Business
→ Branch
→ Resource Ownership
→ Operation
```

Any mismatch is a security failure.

---

# 34. Synchronization and Branch Isolation

Synchronization must also preserve the branch authorization model defined by `05_Branch_and_Scope_Isolation_Security.md`.

A device assigned to Branch A must not submit an operation that causes an unauthorized write to Branch B.

Multi-branch employees remain subject to their current authorization scope.

Offline cached scope must never create new branch access.

---

# 35. Synchronization and Authorization

The authorization model from `07_Authorization_and_Permission_Security.md` remains authoritative.

Offline mode does not create a separate permission hierarchy.

The effective decision is:

```text
Current Security Context
+
Original Offline Authorization Context
+
Operation Policy
+
Synchronization Policy
```

The strongest applicable restriction wins.

---

# 36. Synchronization and Device Trust

The device security model from `08_Trusted_Device_and_Device_Security.md` remains authoritative.

Synchronization must validate device trust before accepting security-sensitive operations.

A device that becomes:

* revoked;
* expired;
* replaced;
* compromised;
* unauthorized;

must not continue synchronization as though its previous trust state were permanent.

---

# 37. Threat Model

The offline security model must consider at least the following threats:

| Threat                         | Security Objective             |
| ------------------------------ | ------------------------------ |
| Stolen offline device          | Prevent unauthorized use       |
| Copied offline credentials     | Prevent credential reuse       |
| Modified offline operation     | Detect integrity violation     |
| Replayed operation             | Prevent duplicate effect       |
| Changed device clock           | Prevent timestamp manipulation |
| Fake synchronization request   | Reject unauthenticated source  |
| Cross-branch synchronization   | Preserve branch isolation      |
| Cross-business synchronization | Preserve tenant isolation      |
| Revoked employee reconnecting  | Enforce current identity state |
| Revoked device reconnecting    | Enforce current device state   |
| Duplicate synchronization      | Preserve idempotency           |
| Modified queued operation      | Detect tampering               |
| Device replacement abuse       | Prevent trust transfer         |
| Offline privilege expansion    | Preserve least privilege       |
| Subscription bypass            | Preserve subscription security |
| Conflicting offline operations | Protect authoritative state    |

---

# 38. Security Monitoring

The system should monitor security-relevant offline events such as:

* repeated synchronization failures;
* replay attempts;
* invalid operation signatures/integrity proofs;
* suspicious clock changes;
* revoked device synchronization attempts;
* revoked employee synchronization attempts;
* cross-branch attempts;
* cross-business attempts;
* unusual synchronization volume;
* repeated duplicate submissions;
* abnormal offline duration;
* repeated integrity failures.

Monitoring must prioritize meaningful security events rather than generating excessive operational noise.

---

# 39. Incident Response

Potential offline compromise should be treated as a security incident when evidence indicates:

* credential compromise;
* device compromise;
* operation tampering;
* repeated replay attempts;
* unauthorized synchronization;
* cross-tenant or cross-branch access;
* manipulation of financial or inventory operations.

Response may include:

* device revocation;
* identity revocation;
* session invalidation;
* synchronization blocking;
* operation quarantine;
* audit review;
* financial/inventory reconciliation;
* security investigation.

---

# 40. Performance and Availability

Offline security must support branch continuity without requiring excessive hardware resources.

Security controls should therefore:

* minimize unnecessary synchronization traffic;
* avoid repeated full-data validation where unnecessary;
* support incremental synchronization;
* use bounded local queues;
* avoid unbounded offline data retention;
* keep authorization data compact;
* avoid expensive operations for routine POS actions.

Security must not be weakened simply to improve performance.

---

# 41. Failure-Safe Rules

When security state is uncertain:

* do not grant new permissions;
* do not trust unknown devices;
* do not accept altered operations;
* do not accept duplicate operations;
* do not cross business boundaries;
* do not cross branch boundaries;
* do not silently discard security failures;
* do not treat client timestamps as authoritative;
* do not convert synchronization failure into authorization success.

Where operational continuity is possible without violating security, the system may continue in a restricted mode.

---

# 42. Security Invariants

The following invariants are mandatory.

### INV-01 — Offline Access Is Explicit

Only explicitly supported functions may operate offline.

### INV-02 — Offline Does Not Expand Authorization

Offline mode must never grant permissions unavailable online.

### INV-03 — Trusted Device Required

Offline authentication must be restricted to previously trusted devices.

### INV-04 — Device-Bound Security

Offline credentials and operation security context must remain bound to the originating device.

### INV-05 — Business Isolation

Offline operations must remain bound to their originating business.

### INV-06 — Branch Isolation

Offline operations must remain within the authorized branch scope.

### INV-07 — Operation Identity

Security-sensitive offline operations must have unique operation identities.

### INV-08 — Operation Integrity

Tampered operations must not be accepted.

### INV-09 — Replay Protection

A legitimate offline operation must not create duplicate business effects when submitted repeatedly.

### INV-10 — Server Authority

The server becomes authoritative whenever connectivity is restored.

### INV-11 — Time Is Not Fully Trusted

Local device time must not independently establish authoritative security state.

### INV-12 — Revocation

Device and identity revocation must take effect when the device reconnects.

### INV-13 — No Trust Transfer

Replacing a device must not automatically transfer the old device's trust.

### INV-14 — Authorization Revalidation

Synchronization must revalidate security context before authoritative state changes.

### INV-15 — Auditability

Security-relevant offline operations must remain traceable.

### INV-16 — Financial Integrity

Offline synchronization must not create duplicate or unauthorized financial effects.

### INV-17 — Inventory Integrity

Offline synchronization must not bypass inventory authorization or inventory integrity rules.

### INV-18 — Fail Securely

Uncertain security state must result in restriction, rejection, or controlled quarantine rather than unrestricted acceptance.

---

# 43. Relationships With Other Security Documents

This document depends on and extends the following policies:

```text
SEC-03 Identity and Access Security
        ↓
SEC-06 Authentication Security Standards
        ↓
SEC-07 Authorization and Permission Security
        ↓
SEC-08 Trusted Device and Device Security
        ↓
SEC-09 Offline Authorization and Synchronization Security
```

It also depends on:

* `04_Business_and_Tenant_Isolation_Security.md`
* `05_Branch_and_Scope_Isolation_Security.md`

Offline synchronization must not redefine any of these boundaries.

It extends them into the disconnected operating environment.

---

# 44. Security Acceptance Criteria

The system is compliant with this policy only if:

1. Offline operation is explicitly limited to approved functions.
2. Unknown devices cannot establish unrestricted offline access.
3. Offline authentication is bound to a previously trusted security context.
4. Cached authorization cannot expand user privileges.
5. Offline operations have unique identities.
6. Operation integrity can be validated.
7. Replayed operations cannot create duplicate business effects.
8. Modified operations are detected or rejected.
9. Local device time cannot independently establish authoritative security state.
10. Offline validity has a defined boundary.
11. Synchronization authenticates the originating device.
12. Synchronization validates business and branch ownership.
13. Synchronization validates authorization.
14. Revoked devices cannot continue synchronization after reconnection.
15. Revoked identities cannot continue unauthorized activity after reconnection.
16. Device replacement cannot silently transfer trust.
17. Financial operations are protected against duplicate synchronization.
18. Inventory operations remain within branch and authorization boundaries.
19. Synchronization failures do not silently create unauthorized state.
20. Security-relevant offline events remain auditable.
21. Tenant and branch isolation remain intact during synchronization.
22. Uncertain security states fail safely.

---

# 45. Final Security Rules

FastFood ERP offline operation follows these final rules:

1. **Offline is a controlled continuity mode, not a security bypass.**
2. **Only explicitly approved operations may work offline.**
3. **Offline authentication is available only within an established trusted-device context.**
4. **Cached authorization can preserve existing capability but cannot create new capability.**
5. **Every security-sensitive offline operation must be uniquely identifiable.**
6. **Operation integrity must be verifiable.**
7. **Replay protection is mandatory for state-changing operations.**
8. **Local device time is never the final authority for security state.**
9. **Synchronization is a security boundary, not merely a data-transfer mechanism.**
10. **Every synchronized operation must be validated against business, branch, identity, device, authorization, integrity, and replay rules.**
11. **Server-side state becomes authoritative after reconnection.**
12. **Device and identity revocation must be enforced when connectivity returns.**
13. **Offline synchronization must preserve tenant and branch isolation.**
14. **Financial and inventory operations require strong integrity and duplicate protection.**
15. **Rejected security-sensitive operations must not silently disappear.**
16. **Device replacement must never automatically transfer trust.**
17. **Security uncertainty must result in restriction, rejection, or controlled quarantine.**
18. **Offline capability must remain bounded by security, authorization, and business policy.**

Offline functionality is therefore considered secure only when it preserves the same fundamental identity, authorization, ownership, integrity, and audit boundaries as the connected system while explicitly accounting for delayed revocation, untrusted local time, temporary connectivity loss, and delayed synchronization.

