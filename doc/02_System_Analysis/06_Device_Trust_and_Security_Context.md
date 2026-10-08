# Device Trust and Security Context

**Document ID:** SA-06
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/02_System_Analysis/README.md`

## 1. Purpose

This document defines how FastFood ERP identifies, trusts and secures operational devices.

It establishes:

* device identity;
* device registration;
* trusted device state;
* employee-device relationship;
* Business and Branch context;
* device revocation;
* offline authorization;
* cryptographic protection;
* device-specific security checks;
* clock rollback detection;
* offline security boundaries;
* device behavior after trust changes.

The objective is to allow fast POS operation while preventing an untrusted or unauthorized device from bypassing employee, Branch, subscription or offline security rules.

---

## 2. Device Identity

Every registered device has a unique Device UUID.

The Device UUID identifies the logical application/device installation used for operational activities.

Device identity is used in:

* authentication context;
* orders;
* payments;
* cash sessions;
* inventory operations;
* synchronization;
* audit events;
* offline authorization;
* security events.

A Device UUID must not be treated as an employee identity.

---

## 3. Device and Employee Separation

A trusted device does not replace employee authentication.

The system distinguishes:

```text id="6y8k5w"
Employee Identity
        +
Device Identity
        +
Business Context
        +
Branch Context
        =
Operational Context
```

The same trusted device may be used by different authorized employees where the business process allows it.

Every operation must retain the actual Employee identity.

---

## 4. Device Registration

A new device must be registered while online.

Initial registration requires:

* authenticated employee;
* valid Business context;
* valid Branch context;
* device identity;
* required verification;
* successful server-side validation.

A device cannot become trusted solely through local configuration.

---

## 5. First-Time Device Use

A new device cannot perform normal offline operations before completing online registration.

The required sequence is:

```text id="m1r5jy"
New Device
    ↓
Online Authentication
    ↓
Device Registration
    ↓
Verification
    ↓
Trusted Device
    ↓
Operational Use
```

This prevents an unknown device from obtaining offline authority without server verification.

---

## 6. Trusted Device State

A device may have a state such as:

```text id="6qgq2j"
Unregistered
    ↓
Pending Verification
    ↓
Trusted
    ↓
Revoked
```

A revoked device cannot continue normal trusted-device operations.

The exact administrative UI may vary, but the server-side state remains authoritative.

---

## 7. Trusted Device Scope

Device trust is associated with the appropriate operational context.

Where Branch restrictions apply, the system must preserve the relevant Business and Branch relationship.

Device trust does not automatically grant:

* employee permissions;
* Owner permissions;
* Branch access;
* subscription entitlements.

Trust is one security condition, not the complete authorization decision.

---

## 8. Device Registration Verification

A new device requires an appropriate verification mechanism.

The verification process must establish that:

* the employee is authenticated;
* the employee is authorized to register a device;
* the device belongs to the correct Business context;
* the device is not already revoked or otherwise prohibited.

The exact verification method may be refined during Security and Architecture analysis.

The mechanism must remain simple enough for normal POS operation.

---

## 9. Device Revocation

An authorized user may revoke a trusted device.

Revocation may be required when:

* a device is lost;
* a device is replaced;
* unauthorized access is suspected;
* an employee leaves the business;
* the device is no longer trusted.

Revocation must be audited.

---

## 10. Revocation Effect

After revocation, the device must not receive new trusted authorization.

The server must treat the device as unauthorized for new protected operations.

Previously created valid offline operations are handled through synchronization and conflict rules rather than silently deleted.

Conceptually:

```text id="m4e3zq"
Device Revoked
      ↓
New Protected Operation
      ↓
Server Check
      ↓
Reject
```

---

## 11. Offline Revocation Limitation

A device that is disconnected cannot instantly receive a server-side revocation event.

Therefore offline authorization must be bounded by:

* validity period;
* authorization version;
* device identity;
* employee identity;
* Business;
* Branch;
* subscription entitlement;
* permission scope.

When the device reconnects, the server's current revocation state becomes authoritative.

---

## 12. Offline Authorization

Offline authorization is a temporary, cryptographically protected authorization state.

It allows trusted devices to continue permitted operations during temporary network loss.

Offline authorization must identify or bind to:

* Employee;
* Business;
* Branch;
* Device;
* permission scope;
* subscription entitlement;
* validity period;
* authorization/version information.

---

## 13. Offline Authorization Boundary

Offline authorization must not provide unlimited authority.

The device can operate only within the authorization that was validly issued.

For example:

```text id="w8f2yb"
Trusted Device
      ↓
Valid Offline Authorization
      ↓
Employee + Branch + Permissions
      ↓
Permitted Offline Operations
```

The device cannot use offline mode to:

* create new permissions;
* expand Branch scope;
* extend subscription indefinitely;
* register another device;
* bypass employee status;
* bypass business rules.

---

## 14. Cryptographic Protection

Offline authorization must be cryptographically protected against unauthorized modification.

The client must not be able to simply change values such as:

* expiry;
* Employee UUID;
* Business UUID;
* Branch UUID;
* permission scope;
* subscription entitlement;
* authorization version.

The exact cryptographic implementation is defined later in Architecture/Security documentation.

---

## 15. Offline Authorization Validity

Offline authorization has a defined validity boundary.

The system must verify:

* authorization is correctly signed/protected;
* Device UUID matches;
* Employee UUID matches;
* Business UUID matches;
* Branch context matches;
* authorization has not expired;
* entitlement remains within the authorized bounds;
* authorization version is valid.

Expired or invalid offline authorization must block protected offline modifications.

---

## 16. Subscription and Offline Authorization

Subscription entitlement is included in the offline authorization boundary.

This prevents a device from continuing unrestricted modifications after the Business subscription has expired.

Example:

```text id="6n1zpx"
Subscription
      ↓
Offline Entitlement
      ↓
Offline Authorization
      ↓
Permitted Operations
```

Offline authorization cannot extend beyond the permitted subscription boundary.

---

## 17. Employee Status and Offline Authorization

Employee status is also part of the offline authorization boundary.

If an employee becomes inactive while a device is offline, the device may temporarily operate only within the previously issued bounded authorization.

After reconnection:

* current employee status is checked;
* outdated authorization is reconciled;
* future unauthorized operations are blocked;
* synchronization conflicts are handled explicitly.

---

## 18. Branch Scope and Offline Authorization

Offline authorization is Branch-aware.

An employee authorized for Branch A cannot use the offline authorization to operate in Branch B unless Branch B was explicitly included in the valid authorization scope.

Branch switching while offline must remain within the authorized offline Branch scope.

---

## 19. Trusted Device and Multiple Employees

A trusted device may be used by multiple employees when the business process permits it.

Each employee must authenticate individually.

For example:

```text id="j2l2qk"
Trusted Device
   ├── Cashier A
   ├── Cashier B
   └── Manager C
```

Each operation retains the actual employee identity.

The device being trusted does not merge employee identities.

---

## 20. Multiple Devices for One Employee

One employee may use multiple trusted devices when authorized.

For example:

```text id="t2xw4e"
Employee A
   ├── Device 1
   ├── Device 2
   └── Device 3
```

Each device retains its own Device UUID.

Operations performed on different devices remain distinguishable in audit and synchronization data.

---

## 21. Multiple Devices in One Cash Session

The system permits the same cashier to use multiple trusted devices within the same Cash Session.

All operations must retain:

* Employee UUID;
* Device UUID;
* Cash Session UUID;
* Register UUID;
* Branch UUID.

This allows the system to distinguish which trusted device performed each operation without creating multiple cash sessions.

---

## 22. Device Context in POS Operations

Important POS transactions should preserve Device context.

For example:

```text id="q4f5kz"
Order
 ├── Employee UUID
 ├── Device UUID
 ├── Business UUID
 ├── Branch UUID
 ├── Register UUID
 └── Cash Session UUID
```

This context supports:

* audit;
* troubleshooting;
* synchronization;
* duplicate prevention;
* security investigation.

---

## 23. Device Context in Payments

Payment records should preserve Device context.

This is especially important for:

* offline payments;
* cash payments;
* payment corrections;
* synchronization;
* duplicate request detection.

A payment must not be attributed to an unrelated device.

---

## 24. Device Context in Inventory

Offline and online inventory operations should retain Device context.

This allows the system to identify:

* which device created the transaction;
* which employee performed it;
* which Branch was involved;
* whether it originated offline;
* how it was synchronized.

---

## 25. Device Context in Synchronization

Synchronization events must preserve Device UUID.

The server uses Device UUID to identify the source of an offline event.

Conceptually:

```text id="z8qk0x"
Offline Event
   ├── Event UUID
   ├── Transaction UUID
   ├── Device UUID
   ├── Employee UUID
   ├── Business UUID
   └── Branch UUID
```

The Device UUID is not sufficient by itself to authorize the event.

The server validates the complete context.

---

## 26. Device Context in Audit

Important events must include Device UUID where applicable.

This allows audit users to distinguish:

* employee;
* device;
* Branch;
* Cash Session;
* transaction.

The device identity remains historical even if the device is later revoked.

---

## 27. Device Security Events

Security-related device events should be recorded where relevant.

Examples:

* device registration;
* verification;
* trust granted;
* trust revoked;
* invalid offline authorization;
* clock anomaly;
* repeated authorization failure;
* synchronization security failure.

Security event retention and visibility follow the Audit and Security policies.

---

## 28. Clock Rollback Detection

Offline operation depends on time-bound authorization.

Therefore the system must detect suspicious clock changes.

Examples include:

```text id="knkq4y"
Last Known Time
      ↓
Current Device Time
      ↓
Unexpected Rollback
      ↓
Security Anomaly
```

A detected clock rollback must be recorded and evaluated.

It should not automatically cause destructive data loss.

The exact response may include:

* restricting certain offline operations;
* requiring online verification;
* marking authorization as suspicious;
* recording a security event.

---

## 29. Clock Tampering

The system should distinguish normal clock drift from suspicious manipulation.

Small differences may be tolerated according to configured security rules.

Significant backward movement or inconsistent timestamps may trigger additional validation.

Server time remains authoritative when the device reconnects.

---

## 30. Device Authentication vs Device Trust

Device authentication and device trust are separate concepts.

Authentication establishes that a device/session can communicate with the system.

Trust establishes that the device has been registered and approved for the required operational use.

Both may be required for protected offline operations.

---

## 31. Device Revocation and Active Sessions

Revoking a device does not silently delete its historical operations.

After revocation:

* new protected operations are rejected according to current connectivity/security state;
* pending offline operations may still be submitted for server validation;
* historical records remain preserved;
* security events are recorded.

The server decides whether each pending event is valid under the synchronization rules.

---

## 32. Device Replacement

When a device is replaced:

1. the new device is registered online;
2. the new device receives its own Device UUID;
3. required verification is completed;
4. the old device may be revoked;
5. historical operations remain associated with the old Device UUID.

Device replacement must not rewrite historical records.

---

## 33. Device Loss

If a trusted device is lost:

* it should be revoked as soon as possible;
* new trusted authorization must not be issued to it;
* historical data remains preserved;
* pending offline events are handled by synchronization validation.

The system must not rely on the user physically recovering the device before security controls can be applied.

---

## 34. Device Sharing

A trusted device may be shared operationally where the business permits it.

However, employee accounts must remain separate.

The system must never use device sharing as justification for:

* shared employee accounts;
* shared permissions;
* anonymous operations;
* removal of employee attribution.

---

## 35. Security Without Excessive Friction

Device security must not make normal POS operations unnecessarily slow.

The system should avoid requiring repeated device verification for every ordinary transaction when the trusted-device state remains valid.

Security controls should be concentrated around:

* registration;
* trust establishment;
* sensitive changes;
* revocation;
* offline authorization;
* suspicious security events.

---

## 36. Device Security and Performance

Security checks must be designed to work on ordinary POS/office hardware.

The system should avoid expensive operations during routine POS flows where they provide no meaningful additional protection.

Critical security checks must remain authoritative even when performance optimizations are used.

---

## 37. Device Trust and Permissions

Device trust does not change employee permissions.

For example:

```text id="7n0wkg"
Trusted Device
      +
Cashier
      +
Cashier Permissions
      =
Cashier Operations
```

It does not become:

```text id="v0w8o4"
Trusted Device
      +
Cashier
      +
Owner Permissions
```

unless the authenticated employee actually has those permissions.

---

## 38. Device Trust and Business Isolation

A trusted device belonging to Business A cannot be used to access Business B merely because the device is trusted.

Business context remains mandatory.

The server validates:

```text id="1s4w9a"
Device
   +
Employee
   +
Business
   +
Branch
```

before protected operations.

---

## 39. Device Trust and Branch Isolation

Similarly, trust does not automatically grant access to every Branch.

Branch scope remains part of authorization.

A trusted device may be valid for multiple Branches only when the employee and device authorization allow the relevant context.

---

## 40. Security During Synchronization

Synchronization must validate the security context of each offline event.

The server should verify:

* Device UUID;
* Employee UUID;
* Business UUID;
* Branch UUID;
* authorization validity;
* event identity;
* transaction identity;
* permission;
* employee status;
* subscription state;
* entity state.

Security validation failure must create an explicit failure or conflict state rather than silently accepting the event.

---

## 41. Security and Idempotency

Device-originated requests use UUID-based identity and idempotency.

If the same transaction or request is submitted more than once:

```text id="pr7l3m"
Same UUID
    ↓
Existing Result?
   ├── Yes → Return Existing Result
   └── No  → Process Once
```

This protects against duplicate effects caused by:

* network retries;
* connection loss;
* application restart;
* synchronization retries.

---

## 42. Security and Offline Storage

Offline operational data must be stored in encrypted local storage.

The local storage must protect sensitive operational data from casual extraction or modification.

The exact encryption implementation belongs to the Architecture/Security documentation.

Pending offline events must not be silently deleted to recover storage space.

If local storage becomes critically full:

* the user is warned;
* unsafe new offline operations may be blocked;
* pending data remains protected.

---

## 43. Security and Application Restart

Application restart must not silently create a new trusted device identity.

The device must retain its registered identity according to the secure device-storage model.

If secure device identity cannot be recovered safely, the application must require an appropriate online re-registration or recovery flow.

---

## 44. Security and Application Reinstallation

Application reinstallation may cause the local trusted-device state to become unavailable.

The system must not assume that a newly installed application is automatically trusted merely because it runs on the same physical computer.

The recovery path must establish trust through the normal online registration mechanism.

---

## 45. Security and Data Recovery

Restoring application data must not automatically restore unrestricted device trust.

Any restored offline authorization must remain cryptographically valid and bound to the correct:

* Device;
* Employee;
* Business;
* Branch;
* validity period;
* authorization version.

Invalid or unverifiable authorization must not be accepted.

---

## 46. Device Security and Subscription Expiration

When subscription entitlement expires:

* online modifying operations are rejected;
* offline authorization cannot extend beyond its permitted validity;
* read-only access follows subscription lifecycle rules;
* reconnection reconciles the device with the current subscription state.

Offline mode must never become a way to bypass subscription restrictions.

---

## 47. Device Security and Employee Deactivation

If an employee becomes inactive:

* new online protected operations are rejected;
* future offline authorization for that employee is not issued;
* previously issued bounded offline authorization is reconciled when the device reconnects;
* pending operations are validated individually.

Employee deactivation must not cause historical records to be deleted.

---

## 48. Security Incident Handling

Potential device security incidents should be represented explicitly.

Examples:

* invalid signature;
* invalid authorization version;
* unexpected clock rollback;
* revoked device attempting protected operation;
* Business mismatch;
* Branch mismatch;
* Employee mismatch;
* repeated synchronization security failure.

The system should record the event and apply the appropriate security response.

---

## 49. Administrative Device Management

Authorized administrative users may:

* view trusted devices;
* view device status;
* identify associated Business/Branch context;
* revoke devices;
* review relevant security events.

Device management must itself be permission-controlled and audited.

---

## 50. System Invariants

The following invariants apply to device trust and security context:

1. Every registered device has a unique Device UUID.
2. Device identity is separate from Employee identity.
3. Device trust does not grant employee permissions.
4. New devices must be registered online before normal offline use.
5. A new device cannot create its own trusted status locally.
6. Trusted devices remain subject to Business isolation.
7. Trusted devices remain subject to Branch scope.
8. Trusted devices remain subject to employee permissions.
9. Trusted devices remain subject to subscription entitlement.
10. An Employee may use multiple trusted devices.
11. Multiple employees may use one trusted device when business rules permit.
12. Employee identity remains separate even on shared devices.
13. The same cashier may use multiple trusted devices within one Cash Session.
14. Important operations preserve Device UUID.
15. Offline authorization is cryptographically protected.
16. Offline authorization is time-bounded.
17. Offline authorization is bound to relevant Employee, Business, Branch and Device context.
18. Offline authorization cannot create or expand permissions.
19. Offline authorization cannot indefinitely extend subscription access.
20. First-time offline use is prohibited before online registration.
21. Device revocation prevents new trusted authorization.
22. Device revocation does not delete historical operations.
23. Pending offline events are validated during synchronization.
24. Clock rollback or tampering is treated as a security anomaly.
25. Server time becomes authoritative after reconnection.
26. Device UUID remains historical after device revocation.
27. Application reinstallation does not automatically restore trust.
28. Restored local data does not automatically restore unrestricted trust.
29. Offline storage must be encrypted.
30. Pending offline events must not be silently deleted because of storage pressure.
31. UUID-based idempotency protects device-originated operations from duplicate effects.
32. Synchronization must validate the complete security context.
33. Device management is permission-controlled.
34. Important device security events are audited.
35. Security controls must not unnecessarily slow routine POS operations.
36. Device trust is one authorization condition and never the sole authorization decision.

---

## 51. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 52. Status

**System Analysis Interview:** Completed through Q227.

**Document Status:** Accepted.

**Current Document:** `06_Device_Trust_and_Security_Context.md`

**Next Document:** `07_POS_and_Order_System.md`

