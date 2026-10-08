# Device and Trust Data Model

**Document ID:** DB-07
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

## 1. Purpose

This document defines the database model for trusted devices and device-related security state.

It covers:

* device identity;
* Business and Branch scope;
* employee-device relationships;
* trusted device lifecycle;
* device registration;
* revocation;
* replacement;
* authentication sessions;
* offline authorization;
* device security metadata;
* synchronization;
* audit;
* Business deletion;
* device-related concurrency.

The model must ensure that device trust is separate from employee authorization.

---

# 2. Device Identity

## 2.1 Device

A `Device` represents a physical or logical client installation authorized to communicate with the FastFood ERP platform.

A device may be:

* POS computer;
* office computer;
* approved operational workstation;
* other supported ERP client.

The system does not treat a device as an employee.

---

## 2.2 Device UUID

Every Device has a stable UUID:

```text id="0bqj1c"
device.id
```

The UUID must be:

* globally unique;
* immutable;
* generated securely;
* never reused.

The UUID is the authoritative device identity.

---

# 3. Device Ownership Context

A Device must be associated with a Business before it can participate in trusted operational activity.

Conceptually:

```text id="m2i8xx"
Business
   ↓
Device
```

A Device must never be trusted across unrelated Businesses.

---

# 4. Branch Scope

A Device may be:

* Business-scoped;
* Branch-scoped;
* associated with one or more Branch contexts according to the supported device model.

The current operational model should prefer explicit Branch scope for POS devices.

Example:

```text id="8qbl1t"
Device A
   ↓
Business A
   ↓
Branch 1
```

A device trusted for Branch 1 must not automatically become trusted for Branch 2.

---

# 5. Device Lifecycle

Device lifecycle:

```text id="7l3w5g"
Registered
    ↓
Pending Trust
    ↓
Trusted
    ↓
Revoked
    ↓
Retired
```

Not every device must pass through every state.

A newly registered device must not be considered trusted until the trust operation is completed.

---

# 6. Device Registration

New devices must be registered through an online process.

The initial registration may capture:

* Device UUID;
* Business;
* Branch;
* device type;
* platform metadata;
* application version;
* registration time;
* registration actor;
* security metadata.

A device cannot perform first-time offline operation.

---

# 7. Trusted Device

A trusted device is a device explicitly authorized for operational use.

Trust may depend on:

* Business;
* Branch;
* Employee relationship;
* device state;
* security policy;
* subscription state.

Trust is not equivalent to permission.

---

# 8. Device Trust Relationship

The relationship between Employee and Device is many-to-many over time.

Conceptually:

```text id="4qk3ud"
Employee
    ↕
EmployeeDevice
    ↕
Device
```

This allows:

* one employee to use multiple devices;
* one trusted device to be used by multiple authorized employees;
* historical association changes.

---

# 9. EmployeeDevice

`EmployeeDevice` represents the relationship between an Employee and a Device.

Conceptual fields:

* `id`
* `employee_id`
* `device_id`
* `business_id`
* branch context where applicable
* status
* trusted_at
* revoked_at
* created_at
* updated_at

The relationship itself must have its own identity because trust can change independently of either Employee or Device.

---

# 10. Trust Scope

Trust may be scoped to:

* Business;
* Branch;
* employee-device relationship.

The system must not assume:

```text
Trusted Device = Global Access
```

Instead:

```text
Trusted Device
      +
Employee
      +
Branch
      +
Permissions
      +
Subscription
      ↓
Effective Operational Access
```

---

# 11. Device Trust and Authorization

Device trust does not grant:

* Owner permissions;
* Manager permissions;
* Cashier permissions;
* inventory permissions;
* payment permissions.

The employee must still have the required permission.

---

# 12. Device Registration Actor

Device registration should record who initiated or approved registration where applicable.

The actor may be:

* Owner;
* authorized Manager;
* authorized employee;
* SYSTEM for controlled automated processes.

The registration event should be auditable.

---

# 13. Device Metadata

The Device may store non-sensitive metadata such as:

* device type;
* operating system family;
* application version;
* device label;
* last seen timestamp;
* registration timestamp;
* last synchronization timestamp.

Hardware identifiers should be minimized.

Only metadata required for security and operations should be retained.

---

# 14. Sensitive Device Data

Sensitive device information must be:

* minimized;
* protected;
* access-controlled;
* excluded from ordinary reports where unnecessary.

Raw secrets must never be stored in plaintext.

Device credentials or signing keys must use secure storage mechanisms appropriate to the architecture.

---

# 15. Device Authentication

Device authentication and Employee authentication are separate concepts.

A valid device credential does not prove the identity of an Employee.

Likewise:

```text id="l7r9f1"
Employee authenticated
      ≠
Device trusted
```

Both may be required for operational access.

---

# 16. Authentication Session

An authenticated session may reference:

* Identity;
* Employee;
* Device;
* Business;
* Branch.

Conceptually:

```text id="5ew5db"
AuthenticationSession
 ├── Identity
 ├── Employee
 ├── Device
 ├── Business
 └── Branch
```

Session data is not the authoritative source of permissions.

---

# 17. Device and Cash Session

A trusted device may operate within a Cash Session.

Operational records may therefore contain:

```text id="9c9n7p"
Device UUID
Cash Session UUID
Employee UUID
Branch UUID
```

This allows transaction reconstruction.

A device may participate in multiple Cash Sessions over time.

---

# 18. Multiple Devices in One Cash Session

The same cashier may use multiple trusted devices within one Cash Session where allowed.

Example:

```text id="z4j4op"
Cash Session A
 ├── Device 1
 └── Device 2
```

This must not create duplicate Cash Sessions.

The Cash Session remains the authoritative operational grouping.

---

# 19. Offline Authorization

Trusted devices may receive cryptographically protected offline authorization.

Offline authorization must contain or securely bind to:

* Business;
* Branch;
* Employee;
* Device;
* permission scope;
* subscription state;
* issuance time;
* expiry time;
* authorization identifier;
* replay protection metadata.

The exact cryptographic format belongs to the Security Architecture.

---

# 20. Offline Authorization Storage

The authoritative database stores the server-side authorization state.

The actual offline credential/artifact may be stored on the trusted client in encrypted local storage.

The server must be able to:

* issue;
* revoke;
* expire;
* replace;
* validate;
* audit

offline authorization state.

---

# 21. Offline Authorization Validity

Offline authorization must be:

* time-bounded;
* device-bound;
* employee-aware;
* Business-aware;
* Branch-aware;
* permission-aware;
* subscription-aware.

Offline authorization must never become a permanent operational credential.

---

# 22. Offline Grace Period

The current system-wide offline authorization policy supports a bounded grace period of:

```text id="5v0qby"
3 days
```

This does not mean every offline credential must always remain valid for exactly three days.

The actual validity must follow the issued authorization and subscription policy.

---

# 23. Device Revocation

A device may be revoked by an authorized actor or by security automation.

Revocation must preserve the Device record.

Revocation should:

* prevent future trusted access;
* invalidate applicable offline authorization;
* invalidate or restrict device sessions where required;
* prevent new synchronization authorization;
* remain auditable.

---

# 24. Revocation State

Conceptually:

```text id="1z9b2x"
Trusted
   ↓
Revoked
```

A revoked Device must not silently return to Trusted state.

Re-trusting should be a new explicit authorization action.

---

# 25. EmployeeDevice Revocation

The relationship between an Employee and Device may be revoked without revoking the Device itself.

Example:

```text id="xv3f7s"
Device A
 ├── Employee A → Revoked
 └── Employee B → Active
```

This is useful when one employee leaves the Business while the device remains operational.

---

# 26. Device Replacement

If a physical device is replaced:

* the new device receives a new Device UUID;
* the old Device remains historical;
* old trust is not automatically transferred;
* new registration is required;
* new trust must be explicitly established.

Device UUID reuse is forbidden.

---

# 27. Lost or Compromised Device

If a device is lost or suspected compromised:

1. Device is revoked.
2. Relevant EmployeeDevice relationships are revoked.
3. Offline authorization becomes invalid.
4. Future synchronization is rejected.
5. Security event is audited.
6. A replacement device may be registered.

The system must not depend on the physical device being reachable to revoke its server-side trust.

---

# 28. Device Revocation During Offline Operation

If a device is revoked while it is offline:

* the device may temporarily contain previously issued offline credentials;
* the credential must still have a bounded validity period;
* synchronization after revocation must be rejected;
* the server must not accept unauthorized post-revocation transactions;
* explicit conflict handling applies to affected pending operations.

The exact security policy may reduce or immediately invalidate offline capability when risk requires it.

---

# 29. Employee Deactivation

When an Employee is deactivated:

* EmployeeDevice relationships remain historical;
* new authentication is blocked;
* offline authorization becomes invalid after the effective deactivation boundary;
* pending unauthorized offline operations are rejected or conflicted;
* device trust itself may remain valid for other authorized employees.

---

# 30. Branch Access Removal

If an Employee loses access to a Branch:

* Branch-scoped authorization is invalidated;
* offline authorization for that Branch becomes invalid;
* the Employee may remain active in other Branches;
* Device trust for unrelated Branch contexts remains governed separately.

---

# 31. Business Deactivation

If a Business becomes inactive or enters deletion lifecycle:

* trusted devices become unusable for new operations;
* authentication access is restricted;
* offline authorization cannot extend Business access;
* pending synchronization cannot create new Business state.

---

# 32. Business Deletion

When Business deletion becomes permanent:

* all Business devices become invalid;
* EmployeeDevice relationships are removed according to lifecycle rules;
* offline authorization is invalidated;
* active sessions are terminated or rendered unusable;
* device records are deleted as part of Business deletion.

Historical audit/deletion rules remain governed by the Data Lifecycle Domain.

---

# 33. Device Synchronization

Device records may participate in synchronization.

Synchronization may update:

* last synchronization time;
* authorization state;
* revocation state;
* configuration version;
* offline queue state.

Synchronization must not allow a client to modify authoritative trust state.

---

# 34. Device Configuration

The device may receive configuration relevant to its authorized scope.

Examples:

* Branch configuration;
* menu configuration;
* printer routing;
* operational settings;
* permission-aware UI configuration.

Configuration data is separate from device trust.

---

# 35. Device and Configuration Version

A device may store the latest synchronized configuration version.

Conceptually:

```text id="yr8t7c"
Device
   ↓
Configuration Version
```

The server remains authoritative.

A device must not use an outdated configuration to bypass a newer security restriction.

---

# 36. Device and Subscription

A trusted device remains subject to Business subscription state.

When subscription entitlement expires:

* trusted device does not bypass read-only restrictions;
* modifying operations are blocked;
* offline authorization cannot extend access beyond its validity;
* read-only access may remain available according to policy.

---

# 37. Device and Permissions

Permission state must be validated independently.

If an employee loses a permission:

* the device remains trusted;
* the EmployeeDevice relationship may remain active;
* the restricted operation is denied.

This prevents unnecessary device revocation for ordinary permission changes.

---

# 38. Device Security Events

Important device events should be auditable.

Examples:

* registration;
* trust approval;
* trust rejection;
* revocation;
* re-trust;
* replacement;
* suspicious activity;
* offline authorization issuance;
* offline authorization revocation;
* failed synchronization due to trust;
* Business deletion invalidation.

---

# 39. Device Audit Context

Audit events should include:

* Device UUID;
* Employee UUID where applicable;
* Business UUID;
* Branch UUID where applicable;
* actor;
* timestamp;
* event type;
* result;
* reason where required;
* Transaction UUID where applicable.

---

# 40. Device and Transaction Identity

Operational transactions must use their own UUID.

Device UUID identifies:

> Which device participated?

Transaction UUID identifies:

> Which operation is this?

They must never be confused.

The system does not use a separate Client Transaction ID.

---

# 41. Idempotency

Device synchronization must preserve transaction UUIDs.

If the same transaction is delivered multiple times:

```text id="1j4n8j"
Transaction UUID
       ↓
Already processed
       ↓
Do not create duplicate state
```

Device UUID alone is never sufficient for idempotency.

---

# 42. Device and Cash Session Integrity

A Device participating in a Cash Session must belong to the correct Business/Branch context.

The database must prevent incompatible relationships such as:

```text id="d6ylm1"
Device.Business != CashSession.Business
```

or:

```text id="7x3q2q"
Device.Branch != CashSession.Branch
```

where the Device is Branch-scoped.

---

# 43. Device and Employee Integrity

An EmployeeDevice relationship must preserve Business consistency:

```text id="c4ly7h"
Employee.business_id
      =
Device.business_id
```

Cross-Business EmployeeDevice relationships are forbidden.

---

# 44. Device and Branch Integrity

If EmployeeDevice is Branch-scoped:

```text id="w7x0xj"
EmployeeDevice.branch_id
      =
Employee's authorized Branch
```

The system must not create a trust relationship for a Branch the Employee cannot access.

---

# 45. Device Concurrency

Concurrent device trust operations must be safe.

Examples:

* two admins attempting to trust the same device;
* trust and revoke happening concurrently;
* replacement while old device is active;
* employee deactivation during authorization issuance.

The database must prevent contradictory final states.

---

# 46. Unique Constraints

Potential constraints include:

```text id="d2c4w8"
UNIQUE(device.id)

UNIQUE(employee_id, device_id, active_scope)

UNIQUE(device_id, business_id)
```

Exact constraints depend on whether a Device may have multiple Branch contexts simultaneously.

The physical schema must prevent duplicate active trust relationships.

---

# 47. Device State Versioning

Device state may use optimistic versioning.

Conceptual field:

```text id="s3u6z9"
version
```

State updates should reject stale writes where necessary.

This prevents a delayed client from overwriting a newer revocation.

---

# 48. Indexing

Important indexes should support:

* Device by Business;
* Device by Branch;
* Device by status;
* Device by last seen;
* EmployeeDevice by Employee;
* EmployeeDevice by Device;
* EmployeeDevice by Branch;
* active trust relationships;
* offline authorization state;
* revocation state;
* audit events by Device.

Indexes should be reviewed against real operational queries.

---

# 49. Device Data Retention

Device history should remain available for the required Business lifecycle.

When a Business is permanently deleted, device data is removed according to the Business Data Lifecycle.

Device records should not be independently deleted merely because a device is replaced.

---

# 50. Database vs Application Responsibilities

### Database responsibilities

* Device UUID integrity;
* Business/Branch references;
* EmployeeDevice relationships;
* lifecycle state;
* uniqueness;
* versioning;
* referential integrity.

### Application responsibilities

* registration workflow;
* trust approval;
* authentication;
* authorization;
* offline credential issuance;
* revocation workflow;
* security policy;
* device replacement;
* suspicious activity handling.

---

# 51. Security Requirements

The system must:

* never treat Device UUID as a secret;
* never rely on Device UUID alone for authentication;
* protect device credentials;
* invalidate revoked credentials;
* bind offline authorization to intended context;
* detect stale authorization;
* detect clock rollback where required;
* prevent replay;
* preserve audit history;
* prevent cross-Business device access.

---

# 52. Recommended Logical Entity Set

```text id="1r7i9n"
Business
   │
   ├── Device
   │     └── OfflineAuthorization
   │
   └── Employee
          └── EmployeeDevice
```

Supporting entities:

```text id="o8z2n1"
AuthenticationSession
DeviceSecurityEvent
DeviceTrustHistory
```

These may be implemented as separate tables depending on the final schema.

---

# 53. Suggested Core Fields

## Device

```text id
business_id
branch_id
device_type
name
status
application_version
platform_metadata
created_at
updated_at
last_seen_at
revoked_at
version
```

## EmployeeDevice

```text id
business_id
employee_id
device_id
branch_id
status
trusted_at
revoked_at
created_at
updated_at
version
```

## OfflineAuthorization

```text id
business_id
branch_id
employee_id
device_id
authorization_version
issued_at
expires_at
status
revoked_at
created_at
```

The final schema may use additional security-specific fields.

---

# 54. Core Invariants

The following invariants are mandatory:

1. Every Device has a unique UUID.
2. Device UUIDs are immutable.
3. Device UUIDs are never reused.
4. A Device belongs to one Business operational context.
5. A Device cannot be trusted across unrelated Businesses.
6. Device trust is separate from Employee authorization.
7. Device trust is separate from Subscription entitlement.
8. Device trust is separate from authentication identity.
9. New devices cannot perform first-time offline operation.
10. New devices must complete online registration.
11. Trust must be explicitly established.
12. Revoked devices cannot perform new trusted operations.
13. Revocation remains auditable.
14. Re-trust after revocation is explicit.
15. Device replacement creates a new Device UUID.
16. Old Device UUIDs are not reused.
17. EmployeeDevice relationships are historically attributable.
18. One device may be used by multiple authorized employees where allowed.
19. One employee may use multiple trusted devices.
20. EmployeeDevice scope must respect Business boundaries.
21. Branch-scoped trust must respect Branch authorization.
22. Trusted devices do not grant permissions.
23. Device authentication does not replace Employee authentication.
24. Employee deactivation invalidates employee operational access.
25. Branch access removal invalidates relevant Branch authorization.
26. Business deactivation restricts device operation.
27. Business deletion invalidates all Business devices.
28. Offline authorization is time-bounded.
29. Offline authorization is device-bound.
30. Offline authorization is Employee-aware.
31. Offline authorization is Business-aware.
32. Offline authorization is Branch-aware.
33. Offline authorization is permission-aware.
34. Offline authorization is subscription-aware.
35. Offline authorization cannot provide unlimited access.
36. Revoked device authorization cannot be used for successful synchronization.
37. Device UUID is not an authentication secret.
38. Transaction UUID is separate from Device UUID.
39. Device UUID is not a Client Transaction ID.
40. Duplicate synchronized transactions must be idempotently rejected.
41. Device state changes must be concurrency-safe.
42. Stale device writes must not overwrite newer revocations.
43. Cross-Business EmployeeDevice relationships are forbidden.
44. Cross-Business Device/CashSession relationships are forbidden.
45. Branch-scoped Device/CashSession relationships must match Branch scope.
46. Device history is preserved after replacement.
47. Device history is preserved after revocation.
48. Device security events are auditable.
49. Device trust changes are auditable.
50. Offline authorization changes are auditable.
51. Device records are not deleted during ordinary replacement.
52. Device deletion follows Business Data Lifecycle.
53. Client-controlled Device IDs cannot establish trust.
54. Client-controlled Branch IDs cannot establish trust.
55. Client-controlled Business IDs cannot establish trust.
56. Server state is authoritative for trust.
57. Server state is authoritative for revocation.
58. Server state is authoritative for Business/Branch ownership.
59. Device cache is not authoritative.
60. A device must never bypass subscription restrictions.
61. A device must never bypass employee permissions.
62. A device must never bypass Branch scope.
63. A device must never bypass Business lifecycle restrictions.
64. Pending offline data cannot resurrect a deleted Business.
65. Device synchronization must preserve Business isolation.
66. Device synchronization must preserve Branch isolation.
67. Device replacement cannot silently transfer trust.
68. Lost-device recovery requires explicit revocation/replacement.
69. Sensitive device credentials must not be stored in plaintext.
70. Device security metadata must be access-controlled.

---

## Related Documents

* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/04_Authentication_and_Authorization.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/03_Domain_Analysis/03_Identity_and_Access_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/19_Device_and_Trust_Domain.md`
* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/04_Architecture/06_API_Architecture.md`
* `docs/04_Architecture/08_Offline_Architecture.md`
* `docs/04_Architecture/09_Synchronization_Architecture.md`
* `docs/04_Architecture/10_Security_Architecture.md`
* `docs/04_Architecture/20_Architecture_Invariants_and_Guardrails.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/README.md`
* `adr/ADR-001-Documentation-First.md`

