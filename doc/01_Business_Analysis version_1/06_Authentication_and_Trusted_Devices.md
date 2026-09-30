# Authentication and Trusted Devices

**Document ID:** FF-BA-006
**Status:** Accepted
**Version:** 1.0
**Scope:** Authentication, employee sessions, device trust, and offline authorization
**Parent Document:** `01_Business_Analysis/05_Users_Roles_and_Permissions.md`

---

## 1. Purpose

This document defines the business requirements for employee authentication, device registration, trusted devices, and offline authorization.

The authentication model must protect restaurant operations without creating unnecessary friction for employees or reducing POS performance.

The system must distinguish between:

* Employee identity
* Authentication session
* Device identity
* Trusted device status
* Business and branch scope
* User permissions
* Subscription entitlement
* Offline authorization

Authentication confirms **who the employee is**.
Permissions determine **what the employee may do**.
Device trust determines **whether the device is authorized to operate within the system**.

---

## 2. Authentication Model

Every employee must authenticate using their own account.

An employee account must not be shared between employees.

The system must associate authenticated activity with the employee who performed it.

Authentication must not by itself grant access to functions that the employee does not have permission to use.

The effective authorization of an employee depends on:

**Employee Identity + Authentication Session + Device Authorization + Permissions + Branch Scope + Subscription Entitlement**

---

## 3. Employee Identity

Each employee must have a unique identity within the business.

The employee identity remains associated with historical records even when the employee is deactivated.

Historical records must not become anonymous because an employee account is deactivated.

Employee identity may appear in:

* Orders
* Cash sessions
* Cash register operations
* Corrections
* Refunds
* Permission changes
* Inventory operations
* Reports
* Audit history
* Other business actions

Employees must not be able to impersonate another employee through normal application functionality.

---

## 4. Employee Login

Employees authenticate through their assigned account credentials.

A successful login creates an authenticated session.

The system must verify, directly or through valid authorization data:

* Employee identity
* Business membership
* Account status
* Relevant branch scope
* Current permissions
* Device authorization
* Subscription state

A valid password alone must not be treated as sufficient authorization for sensitive operations.

---

## 5. Session Identity

Every authenticated session must be associated with:

* Employee
* Business
* Authorized branch scope
* Device
* Session state

Important operations must be traceable to the authenticated employee session.

The system must not silently transfer a session from one employee to another.

When a different employee begins working on the same device, the previous employee's session must no longer be treated as the active employee session.

---

## 6. Device Identity

Each device used by the ERP must have a distinct device identity.

The device identity allows the system to distinguish between:

* Known devices
* New devices
* Trusted devices
* Revoked devices
* Devices requiring verification

Device identity must not replace employee identity.

A trusted device does not automatically grant access to every employee or every branch.

---

## 7. New Device Registration

A previously unknown device must complete its initial registration while online.

A new device must not be allowed to establish its first trusted status while completely offline.

The registration process must verify that the device is authorized to operate for the relevant business.

After successful verification, the device may become a Trusted Device.

The system must record the relationship between:

* Business
* Branch scope
* Device
* Employee or authorized users
* Trust status
* Registration event

---

## 8. Device Verification

When a new device requires verification, the system must use a verification mechanism controlled by the authorized business user.

The verification process must confirm that the device is legitimately being introduced into the business environment.

The exact verification mechanism and code format are implementation details and must not be treated as business rules.

Verification must not be required for every normal order or ordinary POS action.

---

## 9. Trusted Device

A Trusted Device is a device that has successfully completed the required online registration and verification process.

A Trusted Device may receive the authorization required for supported offline operation.

Trusted status does not mean unlimited access.

The following remain independently enforced:

* Employee permissions
* Branch scope
* Subscription restrictions
* Business isolation
* Operational rules
* Audit requirements

---

## 10. Trusted Device Scope

Trusted device authorization must be scoped to the relevant business environment.

A device trusted for one business must not automatically become trusted for another business.

A device trusted for one branch must not automatically gain unrestricted access to other branches.

Where an employee has access to multiple branches, the device authorization must still respect the employee's actual branch permissions.

---

## 11. Trusted Device Revocation

An authorized Owner must be able to revoke a trusted device.

Revocation may be required when:

* A device is lost
* A device is replaced
* A device is no longer used by the business
* Unauthorized use is suspected
* The device should no longer have offline authorization

A revoked device must not receive new offline authorization.

Where technically possible, revocation must take effect as soon as the device reconnects to the server.

Trusted device revocation must be recorded in the audit history.

---

## 12. Offline Authorization

Offline operation is permitted only for a device that has previously completed the required online registration and received valid offline authorization.

An unknown device must not begin ERP operation offline.

Offline authorization must be:

* Cryptographically protected
* Time-bounded
* Associated with the authorized business environment
* Associated with the relevant device
* Subject to permission and branch restrictions

Offline authorization exists to allow business continuity, not to bypass server-side security.

---

## 13. Signed Offline Authorization

Offline authorization must contain sufficient protected information for the system to verify that it was legitimately issued.

The authorization must not be safely modifiable by ordinary users.

The system must be able to detect invalid or modified authorization data when the device operates offline or reconnects.

The exact cryptographic algorithm and implementation are technical architecture decisions and are outside this business analysis document.

---

## 14. Time-Bounded Authorization

Offline authorization must have a defined validity period.

The system must not allow an indefinitely valid offline authorization.

When the authorization reaches its validity boundary, the device must require the appropriate online synchronization or reauthorization process before continuing operations that require valid authorization.

The exact duration is an architecture and security configuration decision and must be defined separately.

---

## 15. Clock Manipulation Protection

Offline operation must account for attempts to manipulate the device clock in order to extend authorization validity.

The system should detect suspicious time changes and inconsistent time progression.

Detected clock manipulation must not silently extend offline authorization.

The exact detection mechanism is an implementation concern and must be defined in the security and architecture documentation.

---

## 16. Replay Protection

Offline authorization and synchronized operations must be protected against replay.

The same business transaction must not be accepted repeatedly simply because the same authorization or transaction data is submitted multiple times.

Every transaction already has its own UUID.

The server must use transaction UUIDs to support idempotent synchronization and prevent accidental duplicate processing.

A separate Client Transaction ID must not be introduced for this purpose.

---

## 17. Device and Employee Relationship

A Trusted Device does not belong permanently to one employee unless the business explicitly defines such a restriction.

Multiple authorized employees may use the same approved business device.

Each employee must still authenticate with their own account.

Therefore:

**Trusted Device ≠ Employee Identity**

The device establishes that the hardware is authorized.

The employee session establishes who is performing the action.

---

## 18. Cashier Security Model

The authentication model must protect against misuse of a cashier account without making normal POS operation unnecessarily complicated.

The system must not require a new PIN or verification code for every order.

Instead, important actions should be traceable through the combination of:

* Employee account
* Authenticated session
* Cash session
* Device identity
* Branch
* Permissions
* Transaction UUID
* Audit history

This provides accountability while preserving normal cashier workflow.

---

## 19. Cash Session Relationship

For cashier operations, authentication and cash-session authorization must remain separate concepts.

A logged-in cashier is not automatically considered the responsible cashier for an open cash session.

Cash-session rules defined in the Cash Register and Cash Sessions document must determine:

* Who opened the session
* Who accepted the cash register
* Who is responsible for the session
* Who may perform permitted operations
* Who closes the session

Authentication only identifies the employee performing the action.

---

## 20. Offline Employee Authentication

A previously authorized employee may operate on a trusted device during an approved offline period.

Offline authentication must continue to respect the employee's last valid authorization state available to the device.

Offline operation must not allow an employee to gain permissions that were not previously authorized.

When the device reconnects, the server becomes authoritative.

---

## 21. Permission Changes While Offline

If an employee's permissions are changed while their device is offline, the device may temporarily continue operating according to the valid offline authorization already issued to it.

After reconnection, the server must determine the employee's current authorization.

Any action that is no longer permitted must be blocked after the new authorization state is received.

Offline mode must never be used as a permanent mechanism for avoiding permission changes.

---

## 22. Subscription Interaction

Device trust does not bypass subscription restrictions.

If a business subscription expires:

* Trusted devices remain identifiable
* Employees remain identifiable
* Existing data remains protected
* Subscription restrictions still apply
* Modifying functions become unavailable according to the subscription lifecycle rules

A Trusted Device must not continue unrestricted operation simply because it was previously trusted.

---

## 23. Business and Branch Isolation

Authentication and device authorization must respect tenant isolation.

An employee authenticated for Business A must not gain access to Business B simply because the same device is trusted.

Likewise, authorization for one branch must not silently expose another branch's restricted data.

This rule applies to:

* Online operation
* Offline operation
* Synchronization
* Reports
* Exports
* Background processing
* Cached data
* Local device data

---

## 24. Local Offline Data Protection

Data stored locally for offline operation must be protected from ordinary direct access.

Offline business data must not be stored as openly readable local files.

Local storage must use appropriate encryption and secure credential handling.

The purpose is to reduce the risk of exposing restaurant data if a device is lost, stolen, or accessed outside the ERP application.

The exact encryption technology is defined in the Security and Architecture documentation.

---

## 25. Synchronization After Reconnection

When an offline device reconnects:

1. The device establishes a secure connection.
2. The server authenticates the device.
3. Offline transactions are submitted.
4. The server validates business and branch identity.
5. Transaction UUIDs are checked for duplicate processing.
6. Permissions and business rules are validated.
7. Accepted transactions are committed.
8. Rejected transactions are returned with an appropriate reason.
9. The device receives the current authorization state.

Synchronization must not silently modify or delete historical transaction information.

---

## 26. Audit Requirements

The system must maintain audit records for security-sensitive device events, including:

* Device registration
* Device verification
* Trusted status granted
* Trusted status revoked
* Offline authorization issued
* Relevant authorization changes
* Suspicious authorization or clock events
* Synchronization security events

Audit records must contain enough information to identify:

* Actor
* Device
* Business
* Branch, where applicable
* Event
* Previous state, where applicable
* New state, where applicable
* Timestamp

Audit history must not be silently overwritten.

---

## 27. Device Lifecycle

A device may move through states such as:

**Unknown → Registered → Trusted → Revoked**

A revoked device may be registered again through the normal authorized process if the business chooses to reuse it.

Re-registration must create an auditable event rather than erasing the previous device history.

---

## 28. Performance Requirements

Authentication and device trust must not noticeably slow normal restaurant operations.

The design must support ordinary restaurant hardware and should not require powerful computers for standard POS work.

Security mechanisms should operate efficiently in the background wherever possible.

Security must not be achieved by adding unnecessary confirmation steps to every normal employee action.

---

## 29. Security Principles

The authentication model follows these principles:

1. **Identity is personal** — employees use their own accounts.
2. **Trust is device-specific** — a trusted device is not universally trusted.
3. **Permission is separate from authentication** — login does not equal authorization.
4. **Subscription is separate from permission** — subscription restrictions remain effective.
5. **Offline mode is controlled** — only authorized trusted devices may operate offline.
6. **Server remains authoritative** — current authorization is determined by the server after reconnection.
7. **Historical actions remain traceable** — important actions retain employee and device identity.
8. **Security must not unnecessarily slow POS operations.**

---

## 30. Summary of Business Rules

| Area                  | Rule                                          |
| --------------------- | --------------------------------------------- |
| Employee login        | Every employee uses an individual account     |
| Shared accounts       | Not permitted as a normal operating model     |
| New device            | Must initially connect online                 |
| Device verification   | Required before becoming trusted              |
| Trusted device        | Allows authorized offline operation           |
| Trusted device scope  | Limited to authorized business/branch context |
| Revocation            | Owner can revoke trusted devices              |
| Offline authorization | Cryptographically protected and time-bounded  |
| Clock manipulation    | Must not extend authorization validity        |
| Replay protection     | Required                                      |
| Transaction identity  | Existing transaction UUID is used             |
| Password alone        | Does not grant unrestricted access            |
| Permissions           | Remain independently enforced                 |
| Subscription          | Cannot be bypassed through device trust       |
| Offline data          | Must be encrypted/protected                   |
| Reconnection          | Server becomes authoritative                  |
| Audit                 | Security-sensitive device events are recorded |
| Performance           | Security must not noticeably slow POS         |

---

## 31. Business Analysis Boundary

This document defines business requirements for authentication and trusted devices.

The following are intentionally left for later technical documentation:

* Password hashing algorithm
* Session/token technology
* Cryptographic algorithms
* Key management
* Exact verification-code format
* Exact offline authorization duration
* Device fingerprint implementation
* Encryption implementation
* Secure storage technology
* Clock-tampering detection algorithm
* Replay-protection implementation
* Network security protocols

These decisions must be documented in the relevant Security and Architecture documents without changing the business rules defined here.

---

## Related Documents

* `01_Business_Analysis/01_Product_Overview.md`
* `01_Business_Analysis/02_Business_Model.md`
* `01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `01_Business_Analysis/18_Audit_and_Change_History.md`
* `01_Business_Analysis/20_Business_Rules.md`
* `06_Backend`
* `10_Deployment`
* `11_Security`

