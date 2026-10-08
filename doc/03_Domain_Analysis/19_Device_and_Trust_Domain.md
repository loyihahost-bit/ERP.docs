# Device and Trust Domain

**Document ID:** DA-19
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/03_Domain_Analysis/README.md`

## 1. Purpose

The Device and Trust Domain manages trusted operational devices used by employees to access FastFood ERP.

The domain establishes whether a physical device is allowed to participate in business operations and whether it may continue authorized operation while temporarily offline.

The domain is responsible for device identity, registration, trust state, branch association, employee-device context, revocation, offline authorization support, and device security history.

Device trust does not replace employee authentication or authorization.

A trusted device only establishes that the device itself is an approved operational endpoint.

---

## 2. Domain Responsibility

The Device and Trust Domain is responsible for:

* device registration;
* device identity;
* trusted device lifecycle;
* business and branch association;
* employee-device association;
* device status;
* device revocation;
* offline authorization eligibility;
* offline authorization lifecycle;
* device security metadata;
* device-related audit information;
* synchronization of device state;
* device conflict handling;
* protection against unauthorized device reuse.

The domain does not determine business permissions.

Employee permissions remain the responsibility of the Identity and Access Domain.

---

## 3. Core Concepts

### 3.1. Device

A Device represents a physical or logical operational endpoint used to access the ERP.

A device has a stable Device UUID.

The Device UUID remains stable for the lifecycle of the registered device identity.

### 3.2. Trusted Device

A Trusted Device is a registered device explicitly authorized to participate in normal business operations.

Trust is scoped to the relevant Business and operational context.

### 3.3. Device Registration

Device Registration is the process through which a previously unknown device becomes known to the system.

Initial registration requires online connectivity.

A newly registered device does not automatically receive employee permissions.

### 3.4. Device Trust State

The conceptual trust states are:

```text
Pending Registration
       ↓
Registered
       ↓
Trusted
       ↓
Revoked
       ↓
Archived
```

The exact persistence model is defined later in the architecture and database phases.

### 3.5. Device Revocation

Revocation immediately prevents the device from being used for operations that require device trust.

Revocation does not delete historical transactions created by the device.

---

## 4. Device Identity

Each registered device has a unique Device UUID.

The Device UUID is used to associate operational activity with its originating device.

Relevant transactions may reference:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Register UUID;
* Cash Session UUID;
* Transaction UUID.

Device identity must remain distinguishable from:

* employee identity;
* browser/session identity;
* authentication session;
* cash session;
* transaction identity.

A Device UUID must not be reused for another physical device identity.

---

## 5. Device Registration

### 5.1. Initial Registration

A device that has never been registered must complete registration while online.

The registration process establishes:

1. device identity;
2. Business context;
3. Branch context where applicable;
4. trust state;
5. required security metadata;
6. initial authorization context.

### 5.2. Offline First Use

A new device cannot begin operational offline use before completing online registration and becoming trusted.

This prevents an unknown device from independently establishing an offline operational identity.

### 5.3. Registration Ownership

Device registration must be performed by an authorized user.

The employee performing registration must have the required permission to register or approve devices.

### 5.4. Registration History

Device registration history must preserve:

* device identity;
* Business;
* Branch where applicable;
* registering actor;
* registration timestamp;
* trust result;
* relevant security state;
* registration source.

---

## 6. Trust Model

Device trust is one layer of the overall security model.

The effective operational authorization conceptually requires:

```text
Employee Authentication
        +
Device Trust
        +
Employee Permission
        +
Branch Scope
        +
Subscription Entitlement
        +
Operational Rules
```

A trusted device does not allow an employee to perform operations for which the employee lacks permission.

Similarly, an authorized employee cannot use an untrusted or revoked device for operations requiring trusted-device status.

---

## 7. Business and Branch Scope

A device must have an explicit operational scope.

Depending on the business configuration, a trusted device may be associated with:

* one Branch;
* an approved multi-branch operational scope;
* a Business-level administrative context.

POS operational devices should normally operate within a Branch context.

A branch switch must trigger the normal:

* authentication checks;
* permission checks;
* branch scope checks;
* subscription entitlement checks;
* device trust checks.

Changing branch context must not silently expand device authority.

---

## 8. Device and Employee Association

A device may be used by multiple authorized employees.

The system must not permanently equate:

```text
Device = Employee
```

Instead:

```text
Device
   ↓
Trusted Operational Endpoint

Employee
   ↓
Authenticated User
```

The same trusted POS device may therefore be used by different authorized employees according to business workflow.

Employee identity must remain attached to every important operation.

---

## 9. Multiple Devices

A single employee may use multiple trusted devices when permitted.

For example:

```text
Employee A
 ├── Device 1
 ├── Device 2
 └── Device 3
```

Each device has its own Device UUID and trust state.

Revoking one device must not automatically revoke the employee's other trusted devices unless an explicit security policy requires it.

Likewise, revoking an employee must prevent that employee from using trusted devices even though the devices themselves remain registered.

---

## 10. Cash Session Context

Device trust interacts with Cash Sessions but does not own them.

A cash session belongs to:

```text
Branch
  ↓
Cash Register
  ↓
Cash Session
```

A Device may participate in a Cash Session.

Relevant operations should preserve:

* Device UUID;
* Employee UUID;
* Cash Register UUID;
* Cash Session UUID.

Multiple trusted devices may participate in the same cash session where business rules permit.

The Device Domain does not determine cash-session ownership.

---

## 11. Offline Authorization

Trusted devices may receive cryptographically protected offline authorization data.

Offline authorization must be:

* time-bounded;
* Business-aware;
* Branch-aware;
* Employee-aware where required;
* permission-aware;
* subscription-aware;
* device-aware;
* protected against replay;
* protected against unauthorized modification.

The offline authorization mechanism must not become a permanent offline credential.

### 11.1. Offline Authorization Expiry

Offline authorization has an explicit validity period.

The default business rule allows a 3-day grace period where applicable.

The exact authorization expiration timestamp must be evaluated against trusted server time information where available.

### 11.2. Offline Operation

A trusted device may continue eligible operations offline while:

* its trust remains valid;
* the employee remains authorized;
* required permissions remain valid;
* subscription constraints allow the operation;
* offline authorization remains valid;
* local security checks pass.

---

## 12. Device Revocation

An authorized administrator may revoke a trusted device.

Revocation may be required when:

* the device is lost;
* the device is stolen;
* the device is replaced;
* the device is compromised;
* the device should no longer operate;
* a security incident requires immediate invalidation.

After revocation:

* new operational actions requiring trust are blocked;
* offline authorization must no longer permit continued operation once revocation is known;
* synchronization must reject unauthorized post-revocation events;
* historical transactions remain intact.

### 12.1. Offline Revocation Limitation

A device that is completely offline cannot receive a revocation signal immediately.

Therefore server-side synchronization must revalidate device trust before accepting offline events.

A previously valid offline authorization must not override a later server-side revocation.

---

## 13. Device Replacement

Replacing a physical device creates a new device identity.

The replacement device must:

1. register online;
2. receive a new Device UUID;
3. pass the trust process;
4. receive appropriate operational authorization.

The old Device UUID must not be transferred to the replacement device.

Historical records must continue referencing the original Device UUID.

---

## 14. Device Security Metadata

The system may maintain security-related metadata required to identify and protect a device.

Conceptually this may include:

* Device UUID;
* Business UUID;
* Branch UUID;
* trust status;
* registration timestamp;
* last successful authentication;
* last successful synchronization;
* last known server interaction;
* revocation state;
* authorization expiration;
* security/version metadata.

The exact metadata set is defined during security and database design.

Sensitive device secrets must not be exposed through normal application responses.

---

## 15. Device State and Lifecycle

The conceptual lifecycle is:

```text
Pending Registration
        ↓
Registered
        ↓
Trusted
        ↓
Revoked
        ↓
Archived
```

A device may become inactive without being deleted.

Historical references to the device must remain valid.

Archived devices must not become operational again simply by reconnecting.

Reactivation, if ever required, must be an explicit controlled operation.

---

## 16. Device Trust and Authentication

Device trust does not authenticate the employee.

The following remain separate:

```text
Who is the employee?
        ↓
Authentication

What may the employee do?
        ↓
Authorization

Is this endpoint approved?
        ↓
Device Trust

Which branch may be accessed?
        ↓
Branch Scope
```

A valid device cannot impersonate another employee.

An authenticated employee cannot bypass device trust requirements by possessing valid credentials alone.

---

## 17. Device Trust and Permissions

The Device Domain must integrate with the Identity and Access Domain.

Effective operation permission is evaluated outside the Device Domain.

For example:

```text
Trusted Device
      +
Cashier Permission
      +
Correct Branch
      +
Active Subscription
      =
Allowed Cash Operation
```

Removing the Cashier permission must immediately prevent the operation even if the device remains trusted.

---

## 18. Device Trust and Subscription

Subscription state affects whether a trusted device may perform modifying operations.

After subscription expiry:

* trusted device status remains historical;
* read-only access may remain available according to permissions;
* modifying operations are blocked;
* offline authorization cannot bypass subscription restrictions.

Reactivation restores eligible operation according to the current subscription entitlement.

---

## 19. Device Trust and Data Lifecycle

Business deletion invalidates all devices belonging to that Business.

After Business deletion:

* device trust becomes invalid;
* offline authorization becomes unusable;
* pending offline events cannot resurrect the Business;
* synchronization requests are rejected;
* local business data must follow the applicable device-storage cleanup process.

A deleted Business UUID must never be reassigned to another Business.

---

## 20. Device Synchronization

Device state participates in synchronization.

Important synchronized state may include:

* device registration;
* trust state;
* revocation;
* authorization state;
* branch association;
* relevant security state.

Server state is authoritative for trust.

Offline device state may be temporarily stale but must be revalidated when connectivity returns.

### 20.1. Transaction Synchronization

Operational transaction synchronization and device configuration synchronization must preserve dependency ordering.

A transaction created by a device must not be accepted merely because the device was previously trusted.

The server must also validate:

* device state;
* employee state;
* permissions;
* branch scope;
* subscription;
* transaction validity.

---

## 21. Device Security Conflicts

A synchronization conflict may occur when:

* device was revoked after an offline operation;
* employee was deactivated;
* employee permission was removed;
* branch access changed;
* subscription expired;
* device registration state changed;
* Business entered deletion lifecycle.

Such conflicts must not silently overwrite server security state.

The conflict must be recorded and resolved according to the Synchronization Domain rules.

---

## 22. Device Audit

Important device operations must produce audit information.

Examples include:

* device registration;
* trust approval;
* trust rejection;
* revocation;
* restoration where supported;
* branch scope changes;
* security-sensitive device changes;
* offline authorization issuance;
* security conflicts;
* administrative device actions.

Audit records must preserve the responsible actor and relevant Device UUID.

Routine device usage does not require an audit event for every read operation.

---

## 23. Device History

Device history and audit history are related but different.

Device history describes the lifecycle and configuration of the device.

Audit history describes security-sensitive or state-changing actions performed against the system.

Historical device state must remain reconstructable where required for operational and security investigations.

---

## 24. Device and Offline Storage

Trusted devices may contain encrypted local operational data required for offline continuity.

Local storage must be logically associated with:

* Business;
* Branch;
* Device;
* relevant offline authorization context.

Local data must not be transferable to another Device UUID as a valid operational identity.

Device replacement must not automatically inherit another device's offline authorization.

---

## 25. Device Loss and Recovery

If a device is lost:

1. an authorized administrator revokes the device;
2. future server-side operations from that device are rejected;
3. pending offline operations are revalidated during synchronization;
4. the replacement device receives a new identity;
5. historical records remain associated with the lost device.

Device loss must not require deleting historical business data.

---

## 26. Concurrency

Device trust operations must be concurrency-safe.

Examples:

* two administrators attempting to revoke the same device;
* device registration submitted twice;
* simultaneous trust-state changes;
* revocation while an offline batch is synchronizing;
* employee deactivation while the device is active;
* branch access removal while a device is synchronizing.

The final state must be deterministic.

Duplicate registration or revocation requests must be idempotent where applicable.

---

## 27. Domain Services

Conceptual services may include:

### Device Registration Service

Registers a new device and establishes its initial lifecycle state.

### Device Trust Service

Approves, maintains, or changes device trust.

### Device Revocation Service

Revokes a device and invalidates its operational trust.

### Offline Authorization Service

Creates and validates protected offline authorization information.

### Device Scope Service

Determines Business and Branch scope associated with a device.

### Device Security Validation Service

Validates device state during authentication, operation, and synchronization.

### Device Recovery Service

Supports controlled replacement and recovery workflows.

These are logical services. Their final implementation boundaries belong to the Architecture phase.

---

## 28. Domain Events

Conceptual domain events include:

* `DeviceRegistered`
* `DeviceTrustGranted`
* `DeviceTrustRejected`
* `DeviceRevoked`
* `DeviceArchived`
* `DeviceScopeChanged`
* `OfflineAuthorizationIssued`
* `OfflineAuthorizationExpired`
* `DeviceSecurityConflictDetected`
* `DeviceSynchronizationValidated`
* `DeviceReplacementRegistered`

Events must not be interpreted as permission grants unless explicitly defined by the relevant domain.

---

## 29. Aggregate Boundary

The primary aggregate boundary is conceptually the **Device**.

The Device aggregate controls device-specific lifecycle invariants such as:

* identity;
* registration;
* trust state;
* revocation state;
* operational scope;
* device lifecycle transitions.

The aggregate does not own:

* employee permissions;
* Business subscription;
* Cash Sessions;
* Orders;
* Payments;
* Inventory.

Cross-domain rules are enforced through domain services, application services, domain events, and transactional boundaries as appropriate.

---

# 30. Domain Invariants

### Identity

1. Every device has a unique Device UUID.
2. A Device UUID cannot be reused for another device identity.
3. Device identity is separate from employee identity.
4. Device identity is separate from authentication session identity.
5. Device identity is separate from Cash Session identity.
6. Device identity is separate from Transaction UUID.
7. Historical transactions retain their original Device UUID.
8. Device identity must remain stable for the registered device lifecycle.

### Registration

9. New devices must register online.
10. Unregistered devices cannot begin operational offline use.
11. Device registration requires appropriate authority.
12. Duplicate registration must not create duplicate device identities.
13. Registration history must be preserved.
14. Registration must establish Business context.
15. Registration must establish applicable Branch context.
16. Registration must establish an initial trust state.

### Trust

17. A trusted device does not grant employee permissions.
18. An untrusted device cannot perform operations requiring trusted-device status.
19. A revoked device cannot perform new trusted operations.
20. Device trust is Business-aware.
21. Device trust is Branch-aware where applicable.
22. Device trust state must be explicitly represented.
23. Trust changes must be auditable.
24. Trust must not silently expand employee authority.

### Authentication and Authorization

25. Device trust does not replace employee authentication.
26. Employee authentication does not replace device trust.
27. Employee permissions remain controlled by the Identity and Access Domain.
28. Branch scope remains independently enforced.
29. Subscription entitlement remains independently enforced.
30. A trusted device cannot impersonate another employee.
31. An employee cannot use device trust to bypass permissions.
32. Security checks must be applied server-side for important operations.

### Offline

33. Offline operation requires a trusted device.
34. Offline operation requires valid offline authorization.
35. Offline authorization is time-bounded.
36. Offline authorization is Business-aware.
37. Offline authorization is Branch-aware.
38. Offline authorization is device-aware.
39. Offline authorization must respect employee permissions.
40. Offline authorization must respect subscription constraints.
41. Offline authorization must resist replay.
42. Offline authorization must be protected against unauthorized modification.
43. A new device cannot create its own valid offline authorization.
44. Offline authorization cannot permanently authorize a device.
45. Server-side revocation overrides stale offline trust state after synchronization.

### Revocation

46. Authorized users may revoke trusted devices.
47. Revocation must preserve historical transactions.
48. Revocation must invalidate future trusted operations.
49. Revocation must be represented in device history.
50. Revocation must be auditable.
51. A revoked device cannot regain trust merely by reconnecting.
52. Device replacement requires a new Device UUID.
53. Revocation of one device does not automatically revoke other devices unless explicitly required.
54. Employee deactivation independently invalidates that employee's operational access.

### Multi-Device

55. One employee may have multiple trusted devices.
56. One trusted device may be used by multiple authorized employees.
57. Each trusted device has an independent Device UUID.
58. Device state is not equivalent to employee state.
59. Device revocation is independent from other devices.
60. Device replacement must not inherit the old Device UUID.

### Cash Context

61. Device trust does not own Cash Sessions.
62. Cash Sessions retain participating Device UUIDs where applicable.
63. Multiple trusted devices may participate in one Cash Session where allowed.
64. Cash Session rules remain controlled by the Cash Domain.
65. Device identity must remain available for cash audit reconstruction.

### Subscription

66. Expired subscription cannot be bypassed through device trust.
67. Offline authorization cannot override subscription expiry.
68. Read-only access may remain available according to subscription rules.
69. Reactivation restores eligible device operations according to current entitlement.
70. Subscription lifecycle changes must be respected during synchronization.

### Synchronization

71. Server trust state is authoritative.
72. Offline device state may be temporarily stale.
73. Synchronization must revalidate device trust.
74. Duplicate device-state events must be handled idempotently.
75. Revoked-device events must not silently overwrite server state.
76. Security conflicts must be explicitly represented.
77. Device synchronization must respect Business isolation.
78. Device synchronization must respect Branch isolation.

### Data Lifecycle

79. Business deletion invalidates all associated device trust.
80. Deleted Business data cannot be resurrected through device synchronization.
81. Deleted Business UUIDs must not be reused.
82. Local device data must follow Business deletion requirements.
83. Historical device references must remain meaningful during permitted retention.
84. Device state must not survive Business deletion as an operational authorization.

### Audit and History

85. Important device lifecycle changes must be auditable.
86. Audit records must identify the Device UUID where applicable.
87. Device history must preserve lifecycle transitions.
88. Audit records must be immutable.
89. Security-sensitive device operations must preserve actor identity.
90. Device history and audit history must remain logically distinguishable.

### Concurrency and Reliability

91. Device registration must be concurrency-safe.
92. Device revocation must be concurrency-safe.
93. Concurrent trust changes must produce deterministic final state.
94. Device-state operations should be idempotent where applicable.
95. Synchronization retries must not create duplicate device identities.
96. Partial device synchronization must be recoverable.
97. Failed device operations must not silently change trust state.
98. Security-state changes must survive application restart.
99. Device lifecycle processing must not block normal POS operations unnecessarily.
100. Device security must remain enforceable on ordinary POS hardware.

---

## 31. Completion Criteria

The Device and Trust Domain is considered complete when:

* device identity is clearly separated from employee identity;
* Device UUID lifecycle is defined;
* online registration is defined;
* trusted-device lifecycle is defined;
* device revocation is defined;
* multi-device operation is defined;
* Business and Branch scope is defined;
* offline authorization boundaries are defined;
* subscription interaction is defined;
* employee permission interaction is defined;
* Cash Session interaction is defined;
* synchronization behavior is defined;
* security conflicts are defined;
* device history and audit responsibilities are defined;
* Business deletion behavior is defined;
* concurrency and idempotency requirements are defined;
* domain invariants are documented.

---

## 32. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Domain Analysis

* `docs/03_Domain_Analysis/01_Domain_Overview.md`
* `docs/03_Domain_Analysis/02_Business_Domain.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/04_Subscription_Domain.md`
* `docs/03_Domain_Analysis/05_Branch_Domain.md`
* `docs/03_Domain_Analysis/07_Cash_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/18_Configuration_Domain.md`

### Future Architecture

* `docs/04_Architecture/`
* `docs/05_Database/`
* `docs/06_Backend/`
* `docs/11_Security/`
* `docs/12_Testing/`
* `docs/14_Operations/`
* `adr/`

