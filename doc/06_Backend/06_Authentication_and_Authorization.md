# Authentication and Authorization

**Document ID:** BE-06
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/06_Backend/README.md`

---

## 1. Purpose

This document defines the backend authentication and authorization architecture of FastFood ERP.

The system must distinguish clearly between:

* authentication;
* authorization;
* Business scope;
* Branch scope;
* employee status;
* role permissions;
* employee overrides;
* subscription entitlement;
* trusted device state;
* offline authorization.

Authentication answers:

> Who is this user?

Authorization answers:

> What is this user allowed to do in this context?

Neither authentication nor authorization may depend on frontend behavior.

---

# 2. Security Principle

The backend must follow:

> Authenticate first, authorize every protected operation, validate scope server-side, and never trust client-provided permissions.

The client may provide identifiers required to select a resource, but those identifiers do not prove access.

---

# 3. Authentication vs Authorization

### Authentication

Authentication establishes the identity of an employee.

Examples:

```text id="auth001"
Login
Session establishment
Token validation
Device recognition
Session expiration
Logout
```

### Authorization

Authorization determines whether the authenticated employee may perform an operation.

Examples:

```text id="auth002"
Can accept Order?
Can change Product price?
Can close Cash Session?
Can view recipes?
Can modify inventory?
```

These concerns must remain separate.

---

# 4. Identity Model

The authenticated operational identity is the Employee.

Conceptually:

```text id="auth003"
Business
   ↓
Employee
   ↓
Role
   ↓
Permissions
   ↓
Branch Scope
```

An Employee may belong to multiple Branches.

The same Employee may have different effective permissions in different Branch contexts.

---

# 5. Super Admin

Super Admin is a platform-level identity.

Super Admin is not treated as an ordinary Business employee.

Super Admin may manage:

* Business creation;
* subscription tariffs;
* platform limits;
* platform-level configuration.

Super Admin must not automatically receive access to a Business's operational data.

Operational Business access must be explicitly controlled by the platform security model.

---

# 6. Owner

Owner is a Business-level employee role.

Owner may manage Business resources according to:

* role permissions;
* employee overrides;
* Branch scope;
* subscription entitlement.

Multiple Owners may exist within one Business subject to subscription limits.

---

# 7. Manager

Manager permissions are limited by the permissions granted to that employee.

A Manager must not grant another employee a permission that the Manager does not possess.

This rule must be enforced server-side.

---

# 8. Employee Status

Authentication and authorization must validate employee status.

Possible states may include:

```text id="auth004"
ACTIVE
INACTIVE
SUSPENDED
```

Only an eligible status may authenticate or perform protected operations.

Historical actions performed before deactivation remain attributable to the original Employee.

---

# 9. Authentication Flow

The general online authentication flow is:

```text id="auth005"
Client
  ↓
Authentication Request
  ↓
Validate Credentials
  ↓
Resolve Employee
  ↓
Validate Employee Status
  ↓
Resolve Business Context
  ↓
Resolve Device Context
  ↓
Create Authenticated Session
  ↓
Return Authentication Result
```

The exact credential mechanism is defined by the Security documentation.

---

# 10. Credential Handling

Credentials must never be stored in plaintext.

The backend must store only secure credential representations appropriate to the authentication mechanism.

Passwords, where used, must be stored using a modern password hashing algorithm with an appropriate work factor.

Authentication secrets must not be written to application logs.

---

# 11. Password Authentication

If password-based authentication is enabled, the backend must:

1. Receive credentials over an encrypted transport.
2. Resolve the intended identity.
3. Verify the password hash.
4. Validate employee status.
5. Validate account restrictions.
6. Establish authenticated context.

Password verification must occur server-side.

---

# 12. Password Failure

Repeated failed authentication attempts should be protected against abuse.

The security system may use:

* rate limiting;
* temporary throttling;
* account protection;
* device/IP risk signals where appropriate.

Security controls must not make normal POS operation unnecessarily slow.

---

# 13. Session Model

Authenticated access should use a secure server-recognized session/token model.

The exact token format may be selected during Security Architecture.

The model must support:

* expiration;
* revocation;
* device association where applicable;
* employee identity;
* Business context;
* security validation.

---

# 14. Access Token Principle

An access credential should represent authenticated identity, not permanent authorization.

Permissions may change after login.

Therefore:

> Authorization must be evaluated against current authoritative state for protected operations.

The system must not assume that an old token permanently represents current permissions.

---

# 15. Token Claims

Where signed tokens are used, claims should contain only the information required for authentication/context.

Potential claims include:

```text id="auth006"
subject / employee_id
session_id
device_id
issued_at
expires_at
token_version
```

Sensitive business data should not be embedded unnecessarily.

---

# 16. Token Lifetime

Authentication credentials should have controlled lifetimes.

Short-lived access credentials are preferred for online API access.

Long-lived refresh mechanisms, if used, must support:

* rotation;
* revocation;
* device association;
* session invalidation.

Exact lifetimes are configuration/security-policy decisions.

---

# 17. Logout

Logout should invalidate the relevant authentication session or credential chain where server-side revocation is supported.

Logout must not:

* deactivate the employee;
* revoke the trusted device;
* close the Cash Session automatically unless explicitly required by business workflow.

An employee may log out while a Cash Session remains open.

---

# 18. Session Revocation

Sessions may need revocation when:

* employee is deactivated;
* device is revoked;
* security incident occurs;
* credentials are reset;
* Business access is removed;
* session is explicitly terminated.

Revocation must take effect for subsequent protected requests.

---

# 19. Device Context

The authentication system may associate an authenticated session with a trusted device.

Conceptually:

```text id="auth007"
Employee
   ↓
Authentication Session
   ↓
Trusted Device
   ↓
Business / Branch Context
```

A device being trusted does not grant additional permissions.

---

# 20. Trusted Device Principle

A trusted device is a security and offline capability boundary.

Trusted status means:

> This device has been previously registered and approved for the relevant Business security context.

It does not mean:

> This device can perform every operation.

Normal authorization still applies.

---

# 21. Device Registration

A new device must first connect online.

The system may require an explicit verification step before marking it trusted.

Example:

```text id="auth008"
New Device
   ↓
Online Authentication
   ↓
Device Registration
   ↓
Verification
   ↓
Trusted Device
```

A completely new device must not begin offline operation.

---

# 22. Device Identity

Each trusted device should have a stable device UUID.

The backend should associate the device with:

* Business;
* registration state;
* trust state;
* created time;
* last seen time;
* revocation state;
* relevant security metadata.

A device UUID is not itself authentication.

---

# 23. Device Revocation

A trusted device may be revoked.

After revocation:

```text id="auth009"
Device
   ↓
REVOKED
```

The device must not:

* authenticate as trusted;
* obtain new offline authorization;
* synchronize offline operations.

Already queued operations must still be processed according to the synchronization security rules rather than blindly accepted.

---

# 24. Branch Context

An employee may operate in one or more Branches.

The active Branch context must be validated.

Example:

```text id="auth010"
Employee
 ├── Branch A
 └── Branch B
```

The employee may switch Branch context only to an authorized Branch.

---

# 25. Branch Switching

When Branch context changes, the backend must recalculate:

* effective permissions;
* Branch scope;
* menu configuration;
* price configuration;
* operational resources.

The backend must not trust permissions calculated by the client.

---

# 26. Business Context

Every authenticated Business operation must resolve a valid Business context.

The system must verify:

```text id="auth011"
Authenticated Employee
        ↓
belongs to Business
        ↓
Business is valid
        ↓
Business lifecycle permits operation
```

A client-provided `business_id` cannot override the authenticated Business scope.

---

# 27. Multi-Business Access

If an identity is ever allowed to operate across multiple Businesses, each request must explicitly establish the active Business context and validate membership/authority.

One Business context must never leak into another.

---

# 28. Permission Model

Effective authorization follows:

```text id="auth012"
Role Permission
        +
Employee Override
        +
Branch Scope
        +
Employee Status
        +
Subscription Entitlement
        +
Operational Rules
```

The final authorization decision is server-side.

---

# 29. Role Permissions

A Role defines a reusable set of permissions.

Examples:

```text id="auth013"
orders.view
orders.create
orders.accept
orders.cancel
payments.record
cash.open
cash.close
inventory.view
inventory.adjust
recipes.view
recipes.modify
reports.view
```

Permissions should be granular enough to enforce meaningful business boundaries.

---

# 30. Employee Permission Override

An employee may receive an explicit permission override where the permission model allows it.

The override may:

* grant permission;
* deny permission.

The final precedence rules must be deterministic.

---

# 31. Permission Precedence

The effective permission should be calculated according to the centralized permission policy.

Conceptually:

```text id="auth014"
Base Role
   ↓
Employee Override
   ↓
Branch Scope
   ↓
Subscription Entitlement
   ↓
Final Decision
```

An employee override must never exceed Business or subscription-level security boundaries.

---

# 32. Permission Denial

Authorization must fail closed.

If required permission cannot be confidently established:

```text id="auth015"
Unknown
   ↓
DENY
```

The backend must not interpret missing permission data as permission granted.

---

# 33. Manager Delegation

A Manager may manage employees only within the authority granted to that Manager.

Example:

```text id="auth016"
Manager permissions:
    employees.add
    employees.view

Manager attempts:
    grant recipes.modify
```

If the Manager does not possess authority to grant `recipes.modify`, the operation must be rejected.

---

# 34. Permission Management

Permission changes are sensitive operations.

The backend must validate:

* actor identity;
* actor permission;
* target employee;
* target Business;
* target Branch scope;
* subscription limits;
* delegation authority.

Permission changes must be audited.

---

# 35. Subscription Entitlement

Authorization is not complete until subscription entitlement is checked where applicable.

Example:

```text id="auth017"
Permission = TRUE
Subscription = FALSE

Final:
DENY
```

A valid employee permission cannot bypass a subscription restriction.

---

# 36. Read-Only Subscription State

When Business becomes read-only:

Allowed may include:

* viewing existing data;
* historical reports;
* allowed exports;
* historical configuration access.

Blocked may include:

* creating Orders;
* changing prices;
* modifying inventory;
* changing employees;
* changing permissions;
* other modifying operations.

Exact capabilities follow subscription rules.

---

# 37. Offline Authorization

Offline operation is allowed only for previously trusted devices with valid offline authorization.

The offline authorization must be:

* signed;
* time-bounded;
* associated with Business;
* associated with Device;
* associated with relevant employee/security context;
* validated locally;
* validated again during synchronization.

---

# 38. Offline Grace Period

The current system uses a limited offline authorization window.

The current agreed grace period is:

**3 days.**

After the authorization expires, the device must not continue unrestricted offline operation.

---

# 39. Offline Permission Snapshot

Offline authorization may contain the permission state required for allowed offline operations.

However, it must not become a permanent permission source.

During synchronization, the server revalidates:

* employee status;
* Business lifecycle;
* device trust;
* operation authorization;
* domain rules.

---

# 40. Offline Business Lifecycle

Offline operations cannot bypass Business lifecycle restrictions.

For example:

```text id="auth018"
Business becomes READ_ONLY online
        ↓
Offline device continues generating modifications
        ↓
Sync
        ↓
Server validates lifecycle
        ↓
Modification rejected
```

Offline authorization is not a mechanism for bypassing subscription or lifecycle restrictions.

---

# 41. Clock Rollback

Offline security must detect suspicious local clock manipulation.

The device may track:

* last trusted server time;
* authorization issue time;
* authorization expiry;
* monotonic/local timing information where available.

Suspicious rollback must cause restricted behavior or synchronization rejection according to the security policy.

---

# 42. Authentication Context

The backend should construct a request authentication context similar to:

```text id="auth019"
AuthenticatedContext
    employee_id
    business_id
    branch_id
    device_id
    session_id
    authentication_method
    source
```

This context is passed to the Application Layer.

---

# 43. Authorization Pipeline

The standard protected-operation pipeline is:

```text id="auth020"
Request
  ↓
Authenticate
  ↓
Resolve Employee
  ↓
Validate Employee Status
  ↓
Resolve Business
  ↓
Validate Business Lifecycle
  ↓
Resolve Branch
  ↓
Validate Branch Scope
  ↓
Validate Permission
  ↓
Validate Subscription Entitlement
  ↓
Validate Device Requirements
  ↓
Execute Use Case
```

Business/domain validation continues after authorization.

---

# 44. Authentication Does Not Mean Authorization

A valid login is insufficient.

Example:

```text id="auth021"
Employee successfully logged in.

Employee:
    no inventory.adjust permission.

Request:
    adjust inventory.
```

Result:

```text
DENY
```

---

# 45. Resource-Level Authorization

Authorization should consider the resource being accessed.

Example:

```text id="auth022"
Employee:
    Branch A only

Request:
    Order from Branch B
```

Even if the employee has `orders.view`, the request must be rejected because the Branch scope is invalid.

---

# 46. Action-Level Authorization

Permissions should correspond to meaningful actions.

For example:

```text id="auth023"
orders.view
orders.create
orders.modify
orders.accept
orders.cancel
payments.record
payments.refund
cash.open
cash.close
cash.correct
```

Viewing an object does not automatically grant modification rights.

---

# 47. Sensitive Operations

Some operations require stronger authorization controls.

Examples:

* permission changes;
* price changes;
* inventory adjustments;
* refunds;
* Cash Session corrections;
* reopening/correction workflows;
* employee deactivation;
* recipe approval.

Additional verification may be introduced where justified by the Security Architecture.

---

# 48. Re-Authentication

Re-authentication may be required for high-risk operations.

Examples:

```text id="auth024"
Change sensitive credentials
Approve high-risk action
Perform privileged security operation
```

However, re-authentication should not be required for every normal POS operation.

POS speed remains a design requirement.

---

# 49. POS Security Principle

The normal cashier workflow should avoid unnecessary authentication friction.

After a valid authenticated/trusted context exists, ordinary operations should rely on:

* active session;
* employee identity;
* permission;
* Branch;
* device;
* Cash Session.

Security controls should remain lightweight for routine POS operations.

---

# 50. Cash Session Context

Cash-related authorization should consider:

```text id="auth025"
Employee
+
Branch
+
Cash Register
+
Cash Session
+
Permission
```

A valid employee login alone does not prove authority over another Branch's Cash Session.

---

# 51. Order Context

Order authorization should consider:

```text id="auth026"
Employee
+
Business
+
Branch
+
Order
+
Order State
+
Permission
```

For example, a cashier may have permission to create Orders but not to refund them.

---

# 52. Inventory Context

Inventory authorization should consider:

```text id="auth027"
Employee
+
Business
+
Branch
+
Warehouse
+
Inventory Permission
```

A permission to view inventory does not imply permission to adjust inventory.

---

# 53. Recipe Context

Recipe access may be restricted.

The backend must validate:

* employee permission;
* Business;
* Branch/all-Branch scope where applicable;
* Recipe operation;
* Recipe approval state.

Recipe visibility is not automatically granted to all employees.

---

# 54. Report Context

Report access should validate:

* Business;
* Branch scope;
* report permission;
* requested period;
* subscription entitlement.

A report query must not expose another Branch's information merely because the employee knows its identifier.

---

# 55. Export Authorization

Excel export is itself a protected operation where the exported data is sensitive.

The backend should validate:

```text id="auth028"
Can view data?
+
Can export data?
```

where the permission model distinguishes these capabilities.

Export operations should be auditable where required.

---

# 56. Authentication Events

Important authentication events should be recorded.

Examples:

```text id="auth029"
Login Success
Login Failure
Logout
Session Revoked
Password Changed
Device Registered
Device Revoked
Offline Authorization Issued
Offline Authorization Revoked
```

Security logs and business audit records may have different retention and access policies.

---

# 57. Audit vs Security Logs

Not every authentication event must become a business audit event.

Distinction:

### Business Audit

Records business state changes.

Example:

```text
Product price changed.
```

### Security Log

Records security events.

Example:

```text
Failed login.
```

Both may be required.

---

# 58. Sensitive Data Logging

Authentication logs must not contain:

* passwords;
* access tokens;
* refresh tokens;
* raw authentication secrets;
* private keys;
* complete credential payloads.

Identifiers should be logged only when operationally useful and permitted.

---

# 59. Rate Limiting

Authentication endpoints should be protected with rate limiting.

The system may apply limits based on:

* account;
* IP/network;
* device;
* endpoint;
* authentication method.

Rate limiting must not cause normal POS operations to become unnecessarily slow.

---

# 60. Session Security

Session credentials should be protected against:

* theft;
* replay;
* fixation;
* indefinite lifetime;
* unauthorized reuse.

Security controls should include appropriate:

* expiration;
* rotation;
* revocation;
* secure transport;
* storage protections.

---

# 61. Transport Security

Authentication credentials and protected API traffic must use encrypted transport.

The production deployment must not expose authentication endpoints over unencrypted transport.

---

# 62. CSRF / Browser Security

If browser cookie-based authentication is used, appropriate CSRF protection must be implemented.

If bearer-token authentication is used, token storage and browser security must follow the chosen architecture.

The final mechanism must be documented in the Security Architecture.

---

# 63. CORS

CORS must be explicitly configured.

The backend must not use unrestricted production origins such as:

```text
*
```

for authenticated operations unless there is a documented security reason.

---

# 64. API Authentication Middleware

Authentication should be implemented through centralized middleware/dependencies.

Individual API routes should not duplicate token parsing and employee lookup logic.

Preferred:

```text id="auth030"
Request
 ↓
Authentication Middleware
 ↓
AuthenticatedContext
 ↓
Application Use Case
```

---

# 65. Authorization Middleware

Authorization may be centralized through reusable policy/dependency mechanisms.

However, resource-specific authorization must remain available inside the Application Layer.

Example:

```text id="auth031"
Global permission check
        +
Order resource scope
```

Both may be necessary.

---

# 66. Fail-Closed Security

Security failures must fail closed.

Examples:

```text id="auth032"
Permission lookup unavailable
→ deny

Business context unresolved
→ deny

Device trust uncertain
→ deny

Invalid token
→ deny

Expired offline authorization
→ deny/restrict
```

The system must not convert uncertainty into permission.

---

# 67. Authorization Caching

Authorization data may be cached for performance only when the cache has a safe invalidation strategy.

Critical permission changes must take effect promptly.

The system must avoid long-lived authorization caches that allow revoked permissions to remain effective indefinitely.

---

# 68. Permission Change Propagation

When permissions change:

```text id="auth033"
Permission Updated
    ↓
Invalidate relevant authorization cache/session state
    ↓
Future request
    ↓
New authorization decision
```

Existing sessions must not indefinitely retain obsolete authority.

---

# 69. Employee Deactivation Propagation

When an employee becomes inactive:

```text id="auth034"
Employee Deactivated
    ↓
Invalidate/revoke relevant sessions
    ↓
Invalidate authorization state
    ↓
Reject future protected operations
```

Historical records remain unchanged.

---

# 70. Device Revocation Propagation

When a trusted device is revoked:

```text id="auth035"
Device Revoked
    ↓
Future online requests rejected
    ↓
New offline authorization blocked
    ↓
Queued synchronization validated
```

The system must not blindly trust previously issued device state after revocation.

---

# 71. Subscription Change Propagation

When Business subscription expires or becomes restricted:

```text id="auth036"
Subscription State Changed
    ↓
Authorization entitlement changes
    ↓
Modification requests blocked
```

The change must apply to both online operations and later offline synchronization.

---

# 72. Authentication and Synchronization

Synchronization requests must authenticate the device and establish the correct Business context.

The synchronization layer must not trust:

```text
business_id
employee_id
device_id
permission data
```

solely because they appear in the client payload.

They must be validated against trusted authentication/device state.

---

# 73. Operation Identity

Authentication context and operation identity are separate.

```text id="auth037"
employee_id
    = who performed the operation

operation_id
    = which logical operation was performed
```

Both may be required for audit and idempotency.

---

# 74. Source Context

Protected operations may originate from:

```text id="auth038"
ONLINE
OFFLINE_SYNC
BACKGROUND
ADMIN
SYSTEM
```

The source must not automatically grant authority.

A background job, for example, must have an explicit system authorization context.

---

# 75. System Operations

System/background operations should use explicit service identities or controlled execution context.

They must not impersonate arbitrary employees without an auditable reason.

When a background process acts because of a user operation, the original actor may be preserved as metadata.

---

# 76. Super Admin Security Boundary

Super Admin operations should use a separate high-privilege security boundary.

Super Admin credentials must not be treated as ordinary Owner credentials.

High-risk Super Admin operations may require stronger authentication and auditing.

---

# 77. Privilege Escalation Prevention

The backend must prevent:

* Manager granting unauthorized permissions;
* employee changing own role beyond authority;
* Branch-scoped employee modifying another Branch;
* employee changing own authorization boundary;
* client modifying Business context;
* offline device extending its own authorization;
* token claims being treated as authoritative permissions.

---

# 78. Authorization Decision Object

A centralized authorization mechanism may return a decision similar to:

```text id="auth039"
AuthorizationDecision
    allowed
    permission
    business_id
    branch_id
    reason
```

The reason may be logged internally but should not expose sensitive security information unnecessarily to clients.

---

# 79. Authorization Failure Responses

The API should expose controlled responses.

Examples:

```text
401 Unauthorized
    Invalid or missing authentication

403 Forbidden
    Authenticated but not authorized

404 Not Found
    Resource intentionally not revealed where appropriate

409 Conflict
    Valid request but concurrency/state conflict
```

Exact response semantics belong to the API contract.

---

# 80. Authentication and Domain Rules

Authentication does not replace domain validation.

Example:

```text id="auth040"
Authenticated cashier
        ↓
orders.accept permission
        ↓
Order.accept()
        ↓
Domain validates:
    correct state
    required items
    availability
    inventory rules
```

All layers remain necessary.

---

# 81. Authorization and Domain Rules

Permission alone does not make an operation valid.

Example:

```text id="auth041"
Employee:
    inventory.adjust = TRUE

Operation:
    adjust inactive/invalid inventory item
```

The request may still fail due to domain rules.

Authorization answers:

> May this employee attempt this operation?

Domain validation answers:

> Is this operation valid?

---

# 82. Security Context and Repositories

The Application Layer passes validated scope to repositories.

Repositories must not trust arbitrary client values.

Example:

```text id="auth042"
Validated:
    business_id = A
    branch_id = A1

Repository:
    query only within A / A1
```

---

# 83. Testing Authentication

Authentication tests should cover:

* valid login;
* invalid credentials;
* inactive employee;
* revoked session;
* expired credential;
* invalid token;
* device mismatch;
* Business mismatch;
* rate limiting;
* logout;
* session revocation.

---

# 84. Testing Authorization

Authorization tests should cover:

* role permission;
* employee override;
* denied override;
* Branch scope;
* all-Branch scope;
* Manager delegation;
* subscription restriction;
* inactive employee;
* revoked device;
* resource ownership;
* cross-Business access;
* cross-Branch access.

---

# 85. Testing Offline Authorization

Offline security tests should cover:

* valid authorization;
* expired authorization;
* wrong device;
* wrong Business;
* revoked device;
* employee deactivation;
* subscription restriction;
* clock rollback;
* duplicate operation;
* synchronization after authorization expiry.

---

# 86. Security Test Example

```text id="auth043"
Given:
    Employee belongs to Branch A
    Employee has inventory.view
    Employee does not have inventory.adjust

When:
    Employee requests inventory adjustment

Then:
    Authorization is denied
    No inventory state changes
    Security event may be recorded
```

---

# 87. Cross-Business Security Test

```text id="auth044"
Given:
    Employee belongs to Business A

When:
    Request targets Business B Product

Then:
    Request is denied
    Business B data is not returned
    No state is changed
```

---

# 88. Manager Delegation Test

```text id="auth045"
Given:
    Manager can manage employees
    Manager does not have recipes.modify

When:
    Manager attempts to grant recipes.modify

Then:
    Request is denied
    No permission change occurs
```

---

# 89. Subscription Test

```text id="auth046"
Given:
    Employee has menu.modify
    Business is READ_ONLY

When:
    Employee changes Product price

Then:
    Request is denied
    Existing configuration remains unchanged
```

---

# 90. Authentication Invariants

1. Authentication establishes employee/system identity.
2. Authentication does not automatically grant permissions.
3. Credentials are never stored in plaintext.
4. Authentication secrets are not logged.
5. Sessions have controlled lifetimes.
6. Sessions can be revoked where supported.
7. Inactive employees cannot perform new protected operations.
8. Revoked devices cannot obtain new offline authorization.
9. New devices require online registration before offline use.
10. Device trust does not grant business permissions.
11. Business context is validated server-side.
12. Branch context is validated server-side.
13. Client-provided identifiers do not prove authorization.
14. Authentication failure fails closed.
15. Security-sensitive operations are auditable.

---

# 91. Authorization Invariants

1. Every protected operation is authorized server-side.
2. Role permissions are not sufficient to bypass Branch scope.
3. Employee overrides cannot exceed system/security boundaries.
4. Managers cannot grant permissions beyond their authority.
5. Subscription entitlement participates in authorization.
6. Read permission does not automatically imply write permission.
7. Export access may be separately controlled.
8. Resource scope is validated.
9. Cross-Business access is prohibited.
10. Cross-Branch access is prohibited unless explicitly authorized.
11. Revoked employee authority takes effect for future operations.
12. Revoked device authority takes effect for future operations.
13. Offline authorization cannot bypass online subscription restrictions.
14. Offline synchronization revalidates authorization.
15. Unknown authorization state results in denial.
16. Authorization changes are propagated promptly.
17. Permission changes are auditable.
18. Privilege escalation is prohibited.
19. Authentication context and operation identity remain separate.
20. Authorization does not replace domain validation.

---

# 92. Performance Guardrails

Authentication and authorization must not unnecessarily slow POS operations.

The implementation should:

* avoid repeated expensive permission queries;
* use safe caching where appropriate;
* keep authorization checks lightweight;
* avoid external network calls for every POS operation;
* avoid repeated device verification when a trusted authenticated context already exists;
* invalidate cached authority promptly when security state changes.

Security must not be weakened merely for performance.

---

# 93. Security Guardrails

The following are prohibited:

1. Trusting frontend permissions.
2. Trusting client-provided Business ID.
3. Trusting client-provided Branch ID.
4. Treating device UUID as authentication.
5. Treating trusted device status as permission.
6. Permanent offline authorization.
7. Offline authorization extending itself.
8. Bypassing subscription restrictions offline.
9. Storing plaintext passwords.
10. Logging access tokens.
11. Logging passwords or authentication secrets.
12. Long-lived unrestricted sessions.
13. Silent privilege escalation.
14. Manager permission escalation.
15. Cross-Business resource access.
16. Cross-Branch resource access without authorization.
17. Authentication logic duplicated across API routes.
18. Authorization logic implemented only in the frontend.
19. Security uncertainty treated as authorization success.
20. Requiring unnecessary re-authentication for ordinary POS actions.

---

# 94. Recommended Backend Structure

The accepted backend structure includes:

```text id="auth047"
app/security/
├── authentication/
├── authorization/
├── tokens/
├── passwords/
├── devices/
├── offline/
└── policies/
```

Supporting authentication/session persistence belongs to Infrastructure where appropriate.

Application use cases consume the security abstractions rather than implementing authentication mechanics themselves.

---

# 95. Security Flow Summary

The complete protected operation flow is:

```text id="auth048"
Client
  ↓
Transport Security
  ↓
Authentication
  ↓
Authenticated Context
  ↓
Employee Status
  ↓
Business Context
  ↓
Branch Scope
  ↓
Permission
  ↓
Subscription Entitlement
  ↓
Device Requirements
  ↓
Application Use Case
  ↓
Domain Rules
  ↓
Repository / Transaction
  ↓
Audit / Outbox
  ↓
Response
```

No single layer is responsible for all security.

---

# 96. Related Documents

### Backend

* `README.md`
* `01_Backend_Architecture.md`
* `02_Backend_Project_Structure.md`
* `03_Application_and_Use_Case_Layer.md`
* `04_Domain_Service_and_Business_Logic.md`
* `05_Repository_and_Data_Access.md`
* `07_Transaction_Management.md`
* `16_Offline_and_Synchronization_Backend.md`
* `23_Backend_Concurrency_and_Idempotency.md`
* `24_Backend_Invariants_and_Guardrails.md`

### Database

* `../05_Database/04_Identity_and_Access_Data_Model.md`
* `../05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `../05_Database/07_Device_and_Trust_Data_Model.md`
* `../05_Database/20_Audit_and_History_Data_Model.md`
* `../05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `../05_Database/29_Database_Security.md`

### System Analysis

* `../02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `../02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `../02_System_Analysis/07_POS_and_Order_System.md`
* `../02_System_Analysis/23_Offline_Operation.md`
* `../02_System_Analysis/25_Subscription_and_Entitlement.md`
* `../02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `../02_System_Analysis/30_System_Invariants_and_Rules.md`

### Security

* `../11_Security/README.md`
* `../11_Security/01_Security_Architecture.md`

---

# 97. Status

**Authentication:** Backend security boundary

**Authorization:** Server-side and mandatory

**Identity:** Employee / controlled system identity

**Business Scope:** Required

**Branch Scope:** Required

**Role Permission:** Supported

**Employee Override:** Supported

**Subscription Entitlement:** Authorization boundary

**Trusted Device:** Security/offline boundary

**Offline Authorization:** Signed and time-bounded

**Offline Grace Period:** 3 days

**Frontend Authorization:** Non-authoritative

**Cross-Business Access:** Prohibited

**Privilege Escalation:** Prohibited

**Next Document:** `07_Transaction_Management.md`

