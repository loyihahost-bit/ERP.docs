# Authentication and Trusted Devices

**Document ID:** BA-06
**Status:** Accepted
**Version:** 2.0
**Scope:** Authentication, employee sessions, device trust, and offline authorization
**Parent Document:** `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`

## 1. Purpose

This document defines the business requirements for employee authentication, employee sessions, device identity, trusted devices, device verification, and offline authorization.

The authentication model must protect restaurant operations without creating unnecessary friction for employees or reducing POS performance.

The system must clearly distinguish between:

* Employee identity;
* Authentication session;
* Device identity;
* Trusted-device status;
* Business scope;
* Branch scope;
* User permissions;
* Subscription entitlement;
* Offline authorization.

Authentication confirms **who the employee is**.

Permissions determine **what the employee may do**.

Branch scope determines **where the employee may operate**.

Subscription entitlement determines **which subscribed functionality and capacity are available**.

Device trust determines **whether the device is authorized to participate in the supported operational environment, including offline operation**.

---

## 2. Authentication Model

Every employee must authenticate using their own account.

An employee account must not be shared between employees as the normal operating model.

The system must associate authenticated activity with the employee who performed it.

Authentication alone must not grant access to functions that the employee does not have permission to use.

The effective authorization of an employee depends on:

**Employee Identity + Authentication Session + Device Authorization + Permissions + Branch Scope + Subscription Entitlement**

Additional business rules may further restrict an operation.

---

## 3. Employee Identity

Each employee must have a unique identity within the Business.

The employee identity remains associated with historical records even when the employee is deactivated.

Historical records must not become anonymous because an employee account is deactivated.

Employee identity may appear in:

* Orders;
* Cash sessions;
* Cash register operations;
* Shift handovers;
* Corrections;
* Refunds;
* Cancellations;
* Payments;
* Inventory operations;
* Recipe and menu changes;
* Permission changes;
* Reports;
* Audit history;
* Other Business actions.

Employees must not be able to impersonate another employee through normal application functionality.

---

## 4. Employee Login

Employees authenticate through their assigned account credentials.

A successful login creates an authenticated session.

The system must validate, directly or through valid authorization data:

* Employee identity;
* Business membership;
* Account status;
* Relevant Branch scope;
* Current permissions;
* Device authorization;
* Subscription state.

A valid password alone must not be treated as sufficient authorization for sensitive operations.

Authentication must not bypass:

* permission restrictions;
* Branch scope;
* subscription restrictions;
* Business isolation;
* operational business rules.

---

## 5. Authentication Session

Every authenticated session must be associated with:

* Employee;
* Business;
* Authorized Branch scope;
* Device;
* Session state.

Important operations must be traceable to the authenticated employee session.

The system must not silently transfer an authenticated session from one employee to another.

When a different employee begins working on the same device:

* the previous employee must no longer be treated as the active employee;
* the new employee must authenticate using their own account;
* subsequent operations must be attributed to the new employee.

A shared device does not imply a shared employee identity.

---

## 6. Device Identity

Each device used by the ERP must have a distinct device identity.

Device identity allows the system to distinguish between:

* Unknown devices;
* Registered devices;
* Trusted devices;
* Revoked devices;
* Devices requiring verification.

Device identity must not replace employee identity.

A trusted device does not automatically grant:

* access to every employee;
* access to every Branch;
* access to every Business;
* every permission;
* subscription entitlement.

---

## 7. New Device Registration

A previously unknown device must complete its initial registration while online.

A new device must **not** be allowed to establish its first trusted status while completely offline.

The initial registration must verify that:

* the device is being introduced into the authorized Business environment;
* the device is permitted to operate;
* the relevant Business context is known;
* the required verification has succeeded.

After successful verification, the device may become a Trusted Device.

The system must record the relationship between:

* Business;
* relevant Branch scope where applicable;
* device;
* authorized employee context;
* trust status;
* registration event;
* registration time.

---

## 8. Device Verification

When a new device requires verification, the system must use an authorization mechanism controlled by an authorized Business user.

The verification process must confirm that the device is legitimately being introduced into the Business environment.

The exact verification mechanism and code format are implementation details.

Verification must not normally be required for every ordinary POS operation.

Security should be established at device registration rather than repeatedly interrupting normal order processing.

---

## 9. Trusted Device

A Trusted Device is a device that has successfully completed the required online registration and verification process.

A Trusted Device may receive the authorization required for supported offline operation.

Trusted status does not mean unlimited access.

The following remain independently enforced:

* Employee permissions;
* Branch scope;
* Subscription restrictions;
* Business isolation;
* Operational business rules;
* Audit requirements.

Therefore:

**Trusted Device ≠ Authorized Employee**

and

**Trusted Device ≠ Unlimited Access**

---

## 10. Trusted Device Scope

Trusted-device authorization must be scoped to the relevant Business environment.

A device trusted for one Business must not automatically become trusted for another Business.

A device trusted for one Branch must not automatically gain unrestricted access to another Branch.

Where an employee has access to multiple Branches, device trust must still respect the employee's actual Branch permissions.

The device is a security context, not a replacement for authorization.

---

## 11. Trusted Device and Employee Relationship

A Trusted Device does not permanently belong to one employee unless the Business explicitly defines such a restriction.

Multiple authorized employees may use the same approved Business device.

Each employee must still authenticate using their own account.

Therefore:

**Trusted Device = Authorized Hardware Context**

**Employee Session = Authenticated Person**

This distinction is required for shared POS computers.

---

## 12. Trusted Device Revocation

An authorized Owner must be able to revoke a Trusted Device.

Revocation may be required when:

* a device is lost;
* a device is replaced;
* a device is no longer used by the Business;
* unauthorized use is suspected;
* the device should no longer receive offline authorization;
* the device is otherwise no longer trusted.

A revoked device must not receive new offline authorization.

Where technically possible, revocation must take effect when the device reconnects to the server.

Trusted-device revocation must be recorded in audit history.

---

## 13. Device Re-registration

A revoked device may be registered again through the normal authorized registration process if the Business decides to reuse it.

Re-registration must not erase the previous device history.

A new registration event must be recorded.

The system must retain the history of:

* previous trust;
* revocation;
* subsequent registration;
* current trust state.

---

## 14. Offline Authorization

Offline operation is permitted only for a device that has:

1. previously completed the required online registration;
2. successfully become trusted;
3. received valid offline authorization;
4. remained within the authorization validity period.

An unknown device must not begin ERP operation offline.

Offline authorization exists to maintain Business continuity, not to bypass server-side security.

---

## 15. Offline Authorization Properties

Offline authorization must be:

* Cryptographically protected;
* Time-bounded;
* Associated with the authorized Business;
* Associated with the relevant device;
* Associated with the relevant employee or authorization context;
* Subject to Branch restrictions;
* Subject to permission restrictions;
* Subject to subscription rules;
* Protected against unauthorized modification;
* Protected against replay.

The exact cryptographic implementation belongs to the Security and Architecture documents.

---

## 16. Signed Offline Authorization

Offline authorization must contain sufficient protected information for the device to verify that it was legitimately issued.

Ordinary users must not be able to safely modify the authorization to extend or broaden its authority.

The system must be able to detect invalid or modified authorization data.

When the device reconnects, the server must validate the authorization and synchronization state.

The exact cryptographic algorithm, key-management method, and signature implementation are technical decisions.

---

## 17. Time-Bounded Authorization

Offline authorization must have a defined validity period.

The system must not issue indefinitely valid offline authorization.

When offline authorization reaches its validity boundary, the device must require the appropriate online synchronization or reauthorization process before continuing operations that require valid authorization.

The exact offline authorization duration is a Security/Architecture configuration decision rather than a fixed Business Analysis value.

---

## 18. Clock Manipulation Protection

Offline operation must account for attempts to manipulate the device clock in order to extend authorization validity.

The system should detect:

* suspicious backward clock changes;
* suspicious forward clock changes;
* inconsistent time progression;
* other signs of clock tampering.

Clock manipulation must not silently extend offline authorization.

The exact detection mechanism belongs to the Security and Architecture documents.

---

## 19. Replay Protection

Offline authorization and synchronization must be protected against replay.

The same Business transaction must not be accepted repeatedly simply because the same transaction or authorization data is submitted multiple times.

Every transaction has its own UUID.

The existing transaction UUID must be used for idempotent synchronization and duplicate protection.

A separate Client Transaction ID is not required for this purpose.

---

## 20. Transaction UUID and Idempotency

Transaction UUIDs must remain globally unique within the relevant system context.

When an offline transaction is synchronized:

1. the server receives the transaction UUID;
2. the server determines whether the transaction has already been processed;
3. a previously accepted transaction must not be processed again;
4. a retry of the same transaction must produce an idempotent result;
5. duplicate processing must not create duplicate orders, payments, inventory deductions, or other side effects.

The UUID identifies the transaction.

It does not replace employee, device, Business, Branch, or session identity.

---

## 21. Cashier Security Model

The authentication model must protect against misuse of cashier accounts without making normal POS operation unnecessarily complicated.

The system must not require a new verification code for every order or ordinary POS action.

Important actions should instead be traceable through the combination of:

* Employee account;
* Authenticated session;
* Cash session;
* Device identity;
* Branch;
* Permissions;
* Transaction UUID;
* Audit history.

This provides accountability while preserving normal cashier workflow.

---

## 22. Authentication and Cash Session

Authentication and cash-session responsibility are separate concepts.

A logged-in cashier is not automatically considered the responsible cashier for every open cash session.

Cash-session rules determine:

* who opened the session;
* who is responsible for the session;
* who may perform permitted cash operations;
* who performs handover;
* who closes the session;
* which employee is associated with the cash session.

Authentication identifies the employee performing an action.

The Cash Register and Cash Sessions document determines cash-session responsibility.

---

## 23. Shared POS Computer

The current operating model supports one primary POS/cashier computer per Branch.

Multiple authorized employees may use the same computer.

When employee responsibility changes:

* the previous employee session must end according to the authentication/session rules;
* the next employee must authenticate using their own account;
* the device identity remains the same;
* the employee identity changes;
* the new operations are attributed to the new employee.

The device itself does not become the employee.

---

## 24. Offline Employee Authentication

A previously authorized employee may operate on a Trusted Device during an approved offline period.

Offline authentication must continue to respect the employee's valid authorization state available to the device.

Offline operation must not allow an employee to gain permissions that were not previously authorized.

The device must retain enough protected authorization information to identify the authorized employee context.

When the device reconnects, the server becomes authoritative.

---

## 25. Employee Deactivation and Offline Access

If an employee is deactivated while their device is offline, the device may temporarily contain previously issued offline authorization.

The system must not treat this temporary state as a permanent permission.

When the device reconnects:

* the server becomes authoritative;
* the employee's current account status is checked;
* synchronization is validated;
* future unauthorized operations are blocked.

The detailed synchronization behavior is defined in the Offline Operation and Synchronization document.

---

## 26. Permission Changes While Offline

If an employee's permissions change while their device is offline, the device may temporarily continue operating according to valid offline authorization already issued to it.

This does not permanently preserve the old permission state.

After reconnection:

* the server determines the current permission state;
* synchronization is validated;
* updated authorization is delivered;
* operations no longer permitted must be blocked.

Offline mode must never become a permanent method for avoiding permission changes.

---

## 27. Branch Scope While Offline

Offline authorization must preserve the applicable Branch scope.

An employee authorized for Branch A must not use offline mode to create transactions for Branch B unless Branch B is also included in the employee's valid authorization.

Branch scope must remain enforced during:

* order creation;
* order modification;
* payment;
* inventory operations;
* cash operations;
* other supported offline actions.

---

## 28. Subscription Interaction

Trusted-device status does not bypass subscription restrictions.

If a Business subscription expires:

* Trusted Devices remain identifiable;
* employees remain identifiable;
* existing data remains protected;
* subscription restrictions continue to apply;
* modifying functions become unavailable according to the subscription lifecycle rules.

A Trusted Device must not continue unrestricted operation simply because it was previously trusted.

---

## 29. Subscription State During Offline Operation

Offline authorization does not create an independent subscription.

A device cannot use previously issued offline authorization as a mechanism to permanently bypass an expired subscription.

When synchronization occurs, the server validates the current subscription state.

If a transaction conflicts with the authoritative subscription state, synchronization must apply the relevant business and synchronization rules.

The detailed handling of already-authorized offline transactions is defined in the Offline Operation and Synchronization document.

---

## 30. Business and Branch Isolation

Authentication and device authorization must respect tenant isolation.

An employee authenticated for Business A must not gain access to Business B simply because the same device is trusted.

Likewise, authorization for one Branch must not silently expose another Branch's restricted data.

This applies to:

* online operation;
* offline operation;
* synchronization;
* reports;
* exports;
* background processing;
* cached data;
* local device data.

---

## 31. Local Offline Data Protection

Data stored locally for offline operation must be protected from ordinary direct access.

Offline Business data must not be stored as openly readable local files.

Local storage must use appropriate encryption and secure credential handling.

The purpose is to reduce the risk of exposing Business data if a device is:

* lost;
* stolen;
* accessed by an unauthorized person;
* inspected outside the ERP application.

The exact encryption technology belongs to the Security and Architecture documents.

---

## 32. Local Data Scope

Local offline storage must contain only the data required for the authorized operational scope.

The system should avoid unnecessarily storing:

* unrelated Business data;
* unrelated Branch data;
* unnecessary employee information;
* data outside the device's authorized operational context.

Local storage must not become a mechanism for obtaining broader access than the employee or device is authorized to have.

---

## 33. Synchronization After Reconnection

When an offline device reconnects:

1. The device establishes a secure connection.
2. The server authenticates the device.
3. The current Business and Branch context is verified.
4. Offline transactions are submitted.
5. Transaction UUIDs are checked for duplicate processing.
6. Employee identity is validated.
7. Permissions are validated.
8. Subscription state is validated.
9. Business rules are validated.
10. Accepted transactions are committed.
11. Rejected transactions are returned with an appropriate reason.
12. The device receives current authorization state.
13. Relevant local authorization is updated or invalidated.

Synchronization must not silently modify or delete historical transaction information.

---

## 34. Server Authority After Reconnection

After reconnection, the server becomes authoritative for:

* employee status;
* permissions;
* Branch scope;
* subscription state;
* Business membership;
* device trust;
* transaction acceptance;
* synchronization state.

The client must not permanently override authoritative server state.

---

## 35. Authentication and Reports

Authentication context must remain available for report access.

Report access must respect:

* Employee identity;
* Business;
* Branch scope;
* permissions;
* subscription state.

A trusted device must not allow a user to obtain reports outside their authorized scope.

Offline report data, where supported, must also respect the same scope.

---

## 36. Authentication and Notifications

Security-sensitive notifications may be associated with:

* employee;
* Business;
* Branch;
* device;
* event.

Notifications must not expose restricted information to employees who lack the relevant access.

Device trust does not automatically grant access to Branch-wide or Business-wide notifications.

---

## 37. Device and Audit History

Important security-sensitive device events must be recorded in audit history.

Examples include:

* device registration;
* device verification;
* Trusted status granted;
* Trusted status revoked;
* device re-registration;
* offline authorization issued;
* offline authorization renewed;
* authorization state changed;
* suspicious clock events;
* synchronization security events;
* invalid authorization detected.

Audit records should identify:

* actor;
* device;
* Business;
* Branch where applicable;
* event;
* previous state where applicable;
* new state where applicable;
* timestamp;
* relevant reason or source.

Audit history must not be silently overwritten.

---

## 38. Device Lifecycle

A device may move through states such as:

**Unknown → Registered → Trusted → Revoked**

A revoked device may later be registered again through the normal authorized process.

Re-registration must create a new auditable event.

Previous device history must remain preserved.

---

## 39. Authentication Failure Handling

Repeated authentication failures must not expose sensitive information.

The system should apply appropriate protection against abusive authentication attempts.

Exact:

* rate limits;
* lockout thresholds;
* credential policies;
* session/token controls

belong to the Security and Architecture documents.

The Business requirement is that authentication security must not be weakened merely to simplify POS operation.

---

## 40. Session Termination

An employee session must be terminated or invalidated when required by:

* explicit logout;
* account deactivation;
* security revocation;
* device revocation;
* session expiration;
* other security events.

A terminated session must not continue to perform unauthorized operations.

Offline authorization is separately controlled and must not be treated as an indefinitely valid online session.

---

## 41. Device Revocation and Offline Data

Revoking a device must prevent it from receiving new authorization.

Existing local data must remain protected.

The device must not be considered authorized merely because old offline data remains locally stored.

When the device reconnects, the server must validate the device's current state.

The detailed secure cleanup or invalidation process belongs to Security and Operations documentation.

---

## 42. Authentication Performance

Authentication and device trust must not noticeably slow normal restaurant operations.

The design must support ordinary restaurant/POS hardware.

Security mechanisms should operate efficiently in the background where possible.

Security must not be achieved by adding unnecessary confirmation steps to every normal employee action.

---

## 43. Security Principles

The authentication model follows these principles:

1. **Identity is personal** — employees use their own accounts.
2. **Trust is device-specific** — a Trusted Device is not universally trusted.
3. **Authentication is separate from authorization** — login does not equal permission.
4. **Branch scope is separate from identity** — an employee may have different access by Branch.
5. **Subscription is separate from permission** — subscription restrictions remain effective.
6. **Offline mode is controlled** — only authorized Trusted Devices may operate offline.
7. **Offline authorization is temporary** — it cannot become an indefinite security bypass.
8. **Server remains authoritative** — current authorization is determined by the server after reconnection.
9. **UUID-based idempotency is required** — duplicate synchronization must not duplicate business transactions.
10. **Historical actions remain traceable** — important actions retain employee and device identity.
11. **Local offline data is protected** — cached data must not be openly accessible.
12. **Security must not unnecessarily slow POS operations.**

---

## 44. Business Rules Summary

| Area                           | Rule                                                   |
| ------------------------------ | ------------------------------------------------------ |
| Employee login                 | Every employee uses an individual account              |
| Shared employee accounts       | Not permitted as the normal operating model            |
| Employee identity              | Preserved in historical records                        |
| New device                     | Must initially connect online                          |
| Device verification            | Required before becoming trusted                       |
| Trusted Device                 | Allows authorized offline operation                    |
| Trusted-device scope           | Limited to authorized Business/Branch context          |
| Owner device revocation        | Supported                                              |
| Offline authorization          | Cryptographically protected and time-bounded           |
| Offline authorization scope    | Business, Branch, employee/device and permission aware |
| Clock manipulation             | Must not extend authorization                          |
| Replay protection              | Required                                               |
| Transaction identity           | Existing transaction UUID is used                      |
| Separate Client Transaction ID | Not required                                           |
| Password alone                 | Does not grant unrestricted access                     |
| Permissions                    | Remain independently enforced                          |
| Branch scope                   | Remains independently enforced                         |
| Subscription                   | Cannot be bypassed through device trust                |
| Offline data                   | Must be encrypted/protected                            |
| Unknown device offline         | Not allowed                                            |
| Server after reconnection      | Authoritative                                          |
| Device revocation              | Prevents new offline authorization                     |
| Employee deactivation          | Historical identity preserved                          |
| Permission changes             | Must become authoritative after reconnection           |
| Tenant isolation               | Always enforced                                        |
| Audit                          | Security-sensitive device events recorded              |
| Performance                    | Security must not noticeably slow POS                  |

---

## 45. Business Analysis Boundary

This document defines business requirements for authentication and Trusted Devices.

The following are intentionally left for later technical documentation:

* password hashing algorithm;
* session/token technology;
* cryptographic algorithms;
* key management;
* exact verification-code format;
* exact offline authorization duration;
* device fingerprint implementation;
* encryption implementation;
* secure storage technology;
* clock-tampering detection algorithm;
* replay-protection implementation;
* network security protocols;
* session expiration implementation;
* credential recovery implementation.

These technical decisions must preserve the business rules defined in this document.

---

## Related Documents

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/02_Business_Model.md`
* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/10_Shift_Handover.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`
* `docs/04_Architecture`
* `docs/06_Backend`
* `docs/10_Deployment`
* `docs/11_Security`

