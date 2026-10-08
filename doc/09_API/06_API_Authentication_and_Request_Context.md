# API Authentication and Request Context

**Document ID:** API-06
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

# 1. Purpose

This document defines the API authentication architecture and the request context established for every authenticated API request in FastFood ERP.

The objective is to ensure that every request can be reliably associated with:

* an authenticated actor;
* a Business;
* a Branch where applicable;
* a trusted Device where applicable;
* a Cash Session where applicable;
* authentication state;
* subscription state;
* request identity;
* operation identity;
* authorization context.

Authentication establishes **who is making the request**.

Request context establishes **under which operational context the request is executed**.

Authorization determines **whether that actor may perform the requested operation** and is defined in detail by the authorization architecture.

---

# 2. Scope

This document covers:

* authentication principles;
* authentication methods;
* authenticated sessions;
* access tokens;
* refresh tokens;
* token validation;
* token expiration;
* credential handling;
* employee authentication;
* device authentication context;
* trusted devices;
* request identity;
* operation identity;
* Business context;
* Branch context;
* Cash Session context;
* subscription context;
* request context construction;
* server-authoritative context;
* client-provided context;
* authentication failure;
* session revocation;
* device revocation;
* employee deactivation;
* logout;
* token rotation;
* authentication caching;
* authentication observability;
* offline authentication relationship;
* authentication security invariants.

This document does not define detailed permission evaluation. That is covered by:

`07_API_Authorization_and_Scope_Enforcement.md`.

---

# 3. Authentication Principle

Every protected API operation must execute under an authenticated security context unless the endpoint is explicitly defined as public.

The API must never infer authentication from:

* a Business UUID;
* a Branch UUID;
* an Employee UUID;
* a Device UUID;
* a Cash Session UUID;
* a request parameter;
* a client-provided role;
* a client-provided permission.

Authentication must be established through the approved authentication mechanism.

---

# 4. Authentication vs Authorization

Authentication and authorization are separate concerns.

```text
Request
   ↓
Authentication
   ↓
Who is the actor?
   ↓
Request Context
   ↓
Authorization
   ↓
Is the actor allowed?
   ↓
Application Operation
```

Authentication failure must not be treated as authorization failure.

Authorization failure must not be treated as authentication success.

---

# 5. Protected API Principle

The default API behavior is:

```text
Endpoint
   ↓
Protected
```

unless the endpoint is explicitly classified as public.

Examples of potentially public operations are limited to infrastructure or platform requirements such as:

* health probes;
* service metadata required for infrastructure;
* explicitly public authentication initiation endpoints.

Business data endpoints must not become public accidentally.

---

# 6. Authentication Mechanism

The API uses token-based authentication for normal application requests.

The standard request form is:

```http
Authorization: Bearer <access_token>
```

The exact token technology is an implementation decision constrained by the security architecture.

The client must not send credentials repeatedly for every API request.

---

# 7. Access Token

An access token represents a short-lived authenticated session credential.

It allows the API to establish the authenticated identity without requiring the user's primary credentials on every request.

An access token must contain or resolve to sufficient information to establish:

* authenticated subject;
* session identity;
* token validity;
* expiration;
* authentication context.

The API must not treat arbitrary client-supplied token claims as authoritative without validation.

---

# 8. Access Token Lifetime

Access tokens must have bounded lifetime.

The lifetime should be short enough to reduce the impact of token theft while avoiding unnecessary POS authentication friction.

The exact lifetime is deployment/security configuration.

A longer-lived credential must not be used as a substitute for session management.

---

# 9. Refresh Token

Where long-lived authenticated sessions are required, refresh tokens may be used to obtain new access tokens.

Refresh tokens must:

* have bounded lifetime;
* be revocable;
* be associated with a session;
* be protected from unauthorized reuse;
* support rotation where required.

Refresh tokens must not be accepted as ordinary API access credentials.

---

# 10. Refresh Token Rotation

Refresh token rotation should be used for supported session types where security requires it.

Typical flow:

```text
Refresh Token A
      ↓
Token Refresh
      ↓
Access Token B
Refresh Token B
      ↓
Refresh Token A becomes invalid
```

Reuse of an invalidated refresh token must be treated as a security event when rotation is enabled.

---

# 11. Session Identity

An authenticated session must have a stable session identifier.

The session identifies the authentication context independently from:

* Business;
* Branch;
* Device;
* request;
* operation.

Example:

```text id="sessionidentity1"
Session
 ├── Employee
 ├── Device
 ├── Authentication Method
 ├── Created At
 ├── Last Activity
 └── Revocation State
```

---

# 12. Session State

Authentication sessions may use states such as:

```text id="sessionstates1"
ACTIVE
REVOKED
EXPIRED
```

The exact state model may be extended where required.

A revoked session must not become valid again merely because its access token has not yet expired.

---

# 13. Credential Handling

Primary authentication credentials must never be stored in plaintext.

The backend must use appropriate credential protection mechanisms for the selected authentication method.

Authentication secrets must not appear in:

* logs;
* audit records;
* API responses;
* error messages;
* analytics events;
* cache values.

---

# 14. Password Authentication

If password authentication is enabled for a user class, passwords must be:

* transmitted only over protected transport;
* securely hashed;
* salted using the selected password hashing mechanism;
* never recoverable as plaintext;
* excluded from logs.

The API must not expose password hashes to clients.

---

# 15. Authentication Attempt Handling

Authentication endpoints must protect against repeated credential attacks.

Controls may include:

* rate limiting;
* progressive delay;
* account/device security controls;
* suspicious activity detection.

The system must avoid creating unnecessary latency for normal authenticated POS operations.

---

# 16. Authentication Failure

Authentication failure must return an appropriate machine-readable error.

Typical cases include:

```text id="authfailure1"
Missing credentials
Invalid credentials
Expired token
Revoked session
Invalid token
Malformed token
Unsupported authentication method
```

The response must not reveal sensitive details that assist credential attacks.

---

# 17. HTTP Authentication Status

Authentication failures normally use:

```text id="authstatus1"
401 Unauthorized
```

The API must not use `403 Forbidden` for a request where the actor has not been successfully authenticated.

`403 Forbidden` is reserved for authenticated actors who are not authorized for the requested operation.

---

# 18. Authentication Headers

Protected requests normally use:

```http
Authorization: Bearer <access_token>
```

The API must not accept multiple ambiguous authentication mechanisms for the same endpoint without an explicit contract.

Alternative authentication mechanisms must be documented and security-reviewed.

---

# 19. Transport Security

Authentication credentials and tokens must only be transmitted over secure transport.

Production API communication must use HTTPS.

Plain HTTP must not be used for protected API traffic.

---

# 20. Token Validation

Every protected request must validate the access token according to the selected authentication architecture.

Validation must include, where applicable:

* token integrity;
* issuer;
* audience;
* expiration;
* not-before time;
* token type;
* session validity;
* revocation state where required.

A syntactically valid token is not automatically a valid authenticated session.

---

# 21. Token Claims

Token claims should contain only information necessary for authentication and request-context construction.

Sensitive or rapidly changing authorization state should not be permanently trusted from a token.

For example, employee deactivation must not remain ineffective merely because an old token contains an apparently valid employee identifier.

---

# 22. Server-Authoritative Identity

The server determines the authoritative authenticated actor.

The client must not be able to replace:

```text id="identityauthority1"
Authenticated Employee
```

by sending:

```json id="identityauthority2"
{
  "employee_id": "another-employee-uuid"
}
```

The request body must not override the authenticated subject.

---

# 23. Employee Context

For normal Business operations, the authenticated subject resolves to an Employee identity.

The request context may contain:

```text id="employeecontext1"
employee_id
employee_status
business_id
```

The exact fields depend on the operation.

An inactive Employee must not perform new protected business operations.

---

# 24. Super Admin Context

Super Admin operates at platform level.

Super Admin requests may have:

```text id="superadmincontext1"
actor_type = SUPER_ADMIN
business_id = optional
branch_id = optional
```

The absence of a Business context does not imply access to every Business.

Platform-level authority is determined by the authorization architecture.

---

# 25. Owner Context

Owner requests are associated with one or more Business contexts according to the authenticated user's actual Business membership.

An Owner may operate within authorized Branch contexts.

The API must not assume that Owner means unrestricted access to every resource.

---

# 26. Manager Context

Manager requests must resolve to the Business and Branch contexts available to the Manager.

The API must preserve the distinction between:

* identity;
* role;
* permissions;
* Branch scope.

Manager status alone must not grant permissions.

---

# 27. Cashier Context

Cashier requests may additionally require:

* Branch context;
* trusted Device context;
* Cash Session context.

For cash operations, the API must validate that the relevant Cash Session belongs to the authenticated operational context.

---

# 28. Waiter and Other Employee Context

Waiter, Cook and other employees use the same general authentication architecture.

The API must not create separate authentication mechanisms merely because operational permissions differ.

Differences are handled by authorization and operational context.

---

# 29. Business Context

A Business context identifies the tenant under which a request is executed.

Example:

```text id="businesscontext1"
Business Context
    ↓
Business UUID
```

The Business context must be derived from authoritative membership and resource relationships.

---

# 30. Branch Context

A Branch context identifies the operational Branch for a request.

Example:

```text id="branchcontext1"
Business
   ↓
Branch
```

A Branch context may be:

* explicitly selected by the user;
* resolved from a resource;
* required by the operation;
* absent for Business-level operations.

The API must determine which case applies.

---

# 31. Client-Provided Branch Context

The client may send a Branch identifier when the API contract requires explicit Branch selection.

For example:

```http
X-Branch-Id: <branch_uuid>
```

or a documented request field may identify the selected Branch.

However, this value is only a request hint.

The server must verify:

* Business membership;
* Employee Branch scope;
* Branch existence;
* Branch status;
* operation compatibility.

---

# 32. Branch Context Resolution

The server resolves Branch context using:

```text id="branchresolution1"
Authenticated Actor
      +
Requested Branch
      +
Resource Relationship
      ↓
Authoritative Branch Context
```

If the requested Branch is not authorized or does not belong to the relevant Business, the request is rejected.

---

# 33. Business Context Resolution

Business context may be resolved from:

1. authenticated membership;
2. explicit Business selection where supported;
3. resource ownership;
4. server-side relationship validation.

The client must not select an arbitrary Business by UUID and thereby obtain access.

---

# 34. Resource-Derived Context

Some requests do not need an explicit Branch header.

For example:

```text id="resourcederived1"
GET /api/v1/cash-sessions/{cash_session_id}
```

The server resolves:

```text
Cash Session
    ↓
Branch
    ↓
Business
```

and verifies that the authenticated actor may operate within that context.

---

# 35. Cash Session Context

A Cash Session context is required for operations that depend on an active cashier session.

Example:

```text id="cashcontext1"
Cashier
   ↓
Branch
   ↓
Cash Register
   ↓
Cash Session
```

The API must not accept an arbitrary Cash Session UUID without verifying its relationship to:

* Branch;
* Cash Register;
* Employee;
* current operational state.

---

# 36. Cash Session Selection

Where a Cash Session is already established as part of the authenticated POS context, the server may resolve it from the active session.

If the request also supplies a Cash Session identifier, the values must be consistent.

Conflicting context must be rejected.

---

# 37. Device Context

Trusted Device context identifies the client device from which the request originates.

The context may include:

```text id="devicecontext1"
device_id
device_status
trust_state
device_session
```

A Device UUID alone does not authenticate the device.

---

# 38. Trusted Device

A trusted device must be registered through the approved online process.

The server determines whether the Device is trusted.

The client must not be able to declare itself trusted by sending:

```text id="badtrust1"
trusted = true
```

---

# 39. Device and Employee Relationship

A trusted Device may be associated with one or more operational sessions according to the device model.

The API must verify that the current authenticated session is permitted to use the Device.

A revoked Device must not remain authorized through stale authentication state.

---

# 40. Device Revocation

Device revocation must invalidate or block relevant future requests.

Revocation must be reflected in:

* authentication checks;
* session validation;
* offline authorization;
* synchronization processing.

A cached Device state must not permanently override server revocation.

---

# 41. Request Identity

Every API request should receive a unique request ID.

Example:

```text id="requestid1"
X-Request-ID: <request_uuid>
```

If the client provides a request ID according to the API contract, the server must validate and safely handle it.

The request ID is used for:

* tracing;
* logs;
* error responses;
* operational diagnostics.

It is not an idempotency key.

---

# 42. Operation Identity

Operations that may be retried or must be uniquely identified may use an operation UUID.

Example:

```text id="operationid1"
X-Operation-Id: <operation_uuid>
```

The operation UUID identifies a logical operation.

It may be persisted for idempotency where required.

---

# 43. Request ID vs Operation UUID

These identifiers have different purposes.

```text id="requestoperation1"
Request ID
→ identifies one HTTP request

Operation UUID
→ identifies one logical business operation
```

A retry may create:

```text id="retryids1"
Request A → Request ID A
Request B → Request ID B

Same Operation UUID
```

when both requests represent the same logical operation.

---

# 44. Correlation ID

A correlation identifier may connect multiple related requests and background operations.

Example:

```text id="correlation1"
API Request
   ↓
Application Operation
   ↓
Outbox Event
   ↓
Background Job
   ↓
Notification
```

The correlation ID helps trace the complete workflow.

It must not replace the request ID or operation UUID.

---

# 45. Request Context Structure

The logical request context is:

```text id="requestcontext1"
Request Context
├── Request ID
├── Correlation ID
├── Operation ID (if applicable)
├── Authentication Session
├── Actor
├── Business
├── Branch (if applicable)
├── Device (if applicable)
├── Cash Session (if applicable)
├── Subscription State
└── Authorization Context
```

Not every request contains every field.

---

# 46. Request Context Construction

Request context should be constructed in a deterministic sequence:

```text id="contextconstruction1"
HTTP Request
   ↓
Request ID
   ↓
Authentication
   ↓
Authenticated Session
   ↓
Actor Resolution
   ↓
Business Resolution
   ↓
Branch Resolution
   ↓
Device Resolution
   ↓
Cash Session Resolution
   ↓
Subscription Context
   ↓
Authorization Context
   ↓
Application Use Case
```

The exact middleware/application boundary may vary, but the resulting context must be authoritative.

---

# 47. Context Immutability

Once the request context is established, protected identity fields must not be silently changed by downstream application code.

For example:

```text id="contextimmutable1"
Authenticated Employee
Business
Branch
Device
```

must remain stable for the request.

A new operational context must be explicitly established as a separate operation where required.

---

# 48. Context vs Request Body

The request body contains business input.

The request context contains security and execution context.

The API must not require clients to repeat authoritative context unnecessarily inside request bodies.

Example:

```json id="bodycontext1"
{
  "branch_id": "uuid",
  "employee_id": "uuid"
}
```

must not be used to override server-derived identity or scope.

---

# 49. Context vs Query Parameters

Query parameters may select data or filtering criteria.

They must not override authenticated identity.

For example:

```text id="querycontext1"
?employee_id=another_employee
```

does not make the request execute as that Employee.

---

# 50. Context vs Path Parameters

Path parameters identify target resources.

Example:

```text id="pathcontext1"
/orders/{order_id}
```

The Order determines its authoritative Business and Branch relationships.

The server validates that the authenticated actor can access that Order.

---

# 51. Subscription Context

The request context may include current subscription state.

Relevant states include:

```text id="subscriptioncontext1"
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

The exact lifecycle is defined by the subscription and data lifecycle architecture.

---

# 52. Subscription and Authentication

A valid authentication session does not automatically mean that the Business may perform all operations.

The request flow is:

```text id="authsubscription1"
Authentication
   ↓
Actor
   ↓
Business
   ↓
Subscription
   ↓
Authorization
   ↓
Operation
```

An expired Business may remain authenticated for read-only access where the business lifecycle allows it.

---

# 53. READ_ONLY Context

When a Business is in read-only state:

* authentication may remain valid;
* permitted read operations may continue;
* modifying operations must be blocked;
* allowed exports may continue.

The API must enforce this server-side.

---

# 54. DELETED Business

A permanently deleted Business must not remain operationally accessible through old authentication sessions.

Existing tokens must not resurrect access to deleted Business data.

---

# 55. Employee Status

Employee status is part of the security context.

An inactive Employee must not perform new protected business operations.

Existing tokens must not override current employee status.

---

# 56. Session Revocation

Sessions may be revoked because of:

* logout;
* administrator action;
* security incident;
* password/security credential change;
* device revocation;
* employee deactivation;
* Business lifecycle change.

Revoked sessions must fail future protected requests according to the revocation policy.

---

# 57. Logout

Logout should invalidate the relevant authenticated session or refresh-token chain.

The server must not rely solely on client-side token deletion.

Client-side token removal is useful but is not sufficient as the authoritative revocation mechanism where server-side sessions are maintained.

---

# 58. Multi-Device Sessions

An Employee may have multiple authenticated sessions on multiple trusted devices where permitted.

Sessions must be independently identifiable.

Revoking one session should not unintentionally revoke unrelated sessions unless the security policy explicitly requires global revocation.

---

# 59. Device-Specific Sessions

A session may be associated with a Device.

This allows the system to distinguish:

```text id="devicesessions1"
Employee
 ├── Device A → Session A
 └── Device B → Session B
```

Security events may therefore revoke one device/session without necessarily disabling all other sessions.

---

# 60. POS Authentication

POS authentication must prioritize both security and operational speed.

After initial secure authentication:

* short-lived request authentication should not require repeated password entry;
* trusted device state may reduce repeated verification;
* active Cash Session context may be reused within the authenticated session.

Security-sensitive changes still require appropriate verification.

---

# 61. Untrusted Device

An untrusted device must not receive trusted offline authorization.

The server may require an online verification or device registration process before the device becomes trusted.

The client cannot bypass this requirement.

---

# 62. Offline Authentication Boundary

Offline operation is not a replacement for initial authentication.

A device must first:

1. authenticate online;
2. become trusted;
3. receive valid offline authorization;
4. store the required protected local context.

A new device cannot bootstrap trusted offline access while completely offline.

---

# 63. Offline Authorization Context

Offline authorization may contain a signed, time-bounded authorization artifact.

It must define sufficient restrictions for:

* Employee;
* Business;
* Branch;
* Device;
* expiration;
* allowed offline capabilities.

The server remains authoritative after synchronization.

---

# 64. Offline Context Expiration

Offline authorization must expire according to the established offline policy.

Current default:

```text id="offlineexpiry1"
Offline authorization grace period = 3 days
```

Expiration must prevent further offline operations requiring authorization.

The device must not extend its own authorization lifetime.

---

# 65. Clock Rollback Protection

Offline authentication and authorization must consider device clock manipulation.

The client must not be able to extend offline authorization indefinitely by rolling the local clock backward.

Server synchronization provides authoritative time validation when connectivity returns.

---

# 66. Authentication Cache

Authentication-related state may be cached for performance.

Examples:

* validated session metadata;
* trusted Device state;
* short-lived authentication context.

Cached authentication state must have bounded lifetime.

---

# 67. Authentication Cache Invalidation

Authentication-related cache must be invalidated when relevant state changes, including:

* session revocation;
* Device revocation;
* Employee deactivation;
* Business deletion;
* security credential changes.

A stale cache must not preserve unauthorized access.

---

# 68. Authentication Cache Failure

If authentication cache is unavailable:

```text id="authcachefailure1"
Authentication Cache
       ↓
Unavailable
       ↓
Authoritative Session Validation
```

The API may become slower but must not bypass authentication.

---

# 69. Authorization Context Boundary

Authentication establishes the initial security context.

Authorization may enrich the context with:

* effective permissions;
* Branch scope;
* role;
* employee overrides;
* resource-specific access.

The detailed authorization process is defined in:

`07_API_Authorization_and_Scope_Enforcement.md`.

---

# 70. Context Propagation

The request context must be available to application services without requiring every method to independently parse HTTP headers.

The preferred flow is:

```text id="contextpropagation1"
HTTP Layer
   ↓
Request Context
   ↓
Application Command
   ↓
Domain / Infrastructure
```

Application services must not directly depend on HTTP request objects.

---

# 71. Context and Domain Layer

The Domain layer must not depend on:

* HTTP headers;
* access tokens;
* cookies;
* reverse proxy metadata;
* HTTP request objects.

Authentication and request context are infrastructure/application concerns.

Domain services receive only the information required to enforce domain rules.

---

# 72. Context and Audit

Important operations must propagate sufficient context for audit creation.

Audit context may include:

```text id="auditcontext1"
request_id
operation_id
actor_id
business_id
branch_id
device_id
cash_session_id
```

Only relevant fields should be stored.

---

# 73. Context and Outbox

When an operation produces an Outbox event, the event should retain relevant trace context.

Example:

```text id="outboxcontext1"
API Request
   ↓
Operation ID
   ↓
Database Transaction
   ↓
Outbox Event
   ↓
Background Worker
```

The event must not depend on an active HTTP request remaining available.

---

# 74. Context and Background Jobs

Background jobs must receive explicit execution context.

A background worker must not attempt to recover authentication from a user HTTP token.

A job should carry only the required authoritative context, such as:

* Business;
* Branch;
* actor where audit attribution requires it;
* operation ID;
* correlation ID.

---

# 75. Context and Notifications

Notifications generated by an API operation may carry the relevant Business, Branch and operation context.

Notification processing must remain asynchronous and must not block the core transaction.

---

# 76. Context and External Integrations

External integrations must not be allowed to impersonate an internal Employee merely by supplying an Employee UUID.

Integration authentication and actor mapping must be explicitly defined by the integration architecture.

---

# 77. Request Context Logging

Logs should include stable context identifiers where appropriate:

```text id="contextlogging1"
request_id
correlation_id
operation_id
business_id
branch_id
employee_id
device_id
```

Sensitive authentication credentials and token values must never be logged.

---

# 78. Context Privacy

Request context contains sensitive operational information.

It must not be exposed unnecessarily to:

* clients;
* logs;
* error messages;
* analytics;
* external integrations.

Only fields required for the specific purpose should be exposed.

---

# 79. Authentication Observability

Authentication monitoring should include:

* successful authentication count;
* failed authentication count;
* token validation failures;
* session revocations;
* Device revocations;
* refresh failures;
* suspicious authentication activity;
* authentication latency.

Metrics should avoid uncontrolled high-cardinality labels.

---

# 80. Authentication Rate Limiting

Authentication-related endpoints should have stricter rate limiting than ordinary authenticated API requests where appropriate.

Rate limiting should protect against:

* brute-force attacks;
* credential stuffing;
* token abuse;
* refresh abuse.

Rate limiting must not unnecessarily interfere with normal POS operation after authentication.

---

# 81. Authentication Error Information

Authentication failures must not reveal whether a specific credential component was correct when such detail would assist attackers.

For example, the API should avoid responses that distinguish unnecessarily between:

```text
Employee does not exist
Password is incorrect
```

when that distinction creates account enumeration risk.

---

# 82. Session Timeout

Sessions must have bounded lifetime and inactivity policy according to the security configuration.

POS workflows may require a different operational timeout from administrative interfaces.

Any longer POS session lifetime must remain protected by:

* trusted Device controls;
* employee authentication;
* session state;
* Branch scope;
* Cash Session rules.

---

# 83. Sensitive Operation Reauthentication

Certain operations may require stronger authentication or confirmation even when the user already has an active session.

Examples may include:

* security-sensitive Device changes;
* credential changes;
* privileged configuration operations;
* selected financial corrections.

Reauthentication requirements are defined by the security and authorization architecture.

---

# 84. Authentication and Cash Session

An authenticated Cashier does not automatically have an active Cash Session.

The system must distinguish:

```text id="authcashdistinction1"
Authenticated Employee
        ≠
Active Cash Session
```

Cash operations requiring a session must validate that a valid Cash Session exists.

---

# 85. Authentication and Branch Switching

When an Employee changes Branch context:

```text id="branchswitchauth1"
Authenticated Session
        ↓
New Branch Context
        ↓
Recalculate Scope
        ↓
Recalculate Authorization
```

Previous Branch permissions must not be carried over automatically.

---

# 86. Authentication and Device Switching

Changing the active Device must establish a valid Device context.

A Device UUID supplied by the client is not sufficient to authenticate the Device.

The new Device must pass the trusted-device security process.

---

# 87. Authentication and Business Switching

If an authenticated user can operate across multiple Businesses, selecting another Business must trigger server-side membership and authorization resolution.

The client cannot switch Business context merely by changing a UUID.

---

# 88. Authentication and Historical Resources

Access to historical resources still requires authentication and authorization.

Historical data must not be made public merely because it is immutable.

---

# 89. Authentication and Data Lifecycle

Business lifecycle state must be checked against the requested operation.

For example:

```text id="lifecycleauth1"
ACTIVE
→ normal authorized operations

READ_ONLY
→ permitted reads/exports

DELETING
→ restricted access

DELETED
→ no operational access
```

The exact lifecycle policy is defined by the subscription/data lifecycle architecture.

---

# 90. Authentication and API Versioning

Authentication behavior is part of the API contract.

A major API version may introduce a new authentication mechanism when required.

Within a supported major version:

* authentication headers remain stable;
* token semantics remain documented;
* failure semantics remain predictable;
* supported clients retain a migration path.

---

# 91. Authentication and Backward Compatibility

Security changes may require controlled compatibility exceptions.

A known insecure authentication behavior must not be preserved indefinitely solely for compatibility.

Where possible:

```text id="authmigration1"
Old Authentication
       ↓
Migration Period
       ↓
New Authentication
       ↓
Old Authentication Sunset
```

---

# 92. Authentication and OpenAPI

OpenAPI documentation must accurately describe authentication requirements.

Protected endpoints must declare their supported security requirements.

The documentation must not imply that a public endpoint is protected or that an unsupported authentication method is valid.

---

# 93. Authentication Request Flow

The standard protected request flow is:

```text id="authflow1"
HTTP Request
   ↓
TLS
   ↓
Request ID
   ↓
Authentication Header
   ↓
Token Validation
   ↓
Session Validation
   ↓
Actor Resolution
   ↓
Business Context
   ↓
Branch Context
   ↓
Device Context
   ↓
Cash Session Context
   ↓
Subscription Context
   ↓
Authorization
   ↓
Application Use Case
```

Not every request requires every context component.

---

# 94. Authentication Failure Flow

```text id="authfailflow1"
HTTP Request
   ↓
Authentication
   ↓
Invalid?
 ┌─┴─┐
Yes  No
 ↓    ↓
401   Request Context
```

Authentication failure must stop the protected operation before business execution.

---

# 95. Context Conflict

If request context contains conflicting information, the server must reject the request.

Examples:

```text id="contextconflict1"
Authenticated Business ≠ Requested Business

Authorized Branch ≠ Requested Branch

Active Cash Session ≠ Requested Cash Session

Authenticated Device ≠ Registered Device
```

The server must not silently choose one conflicting value.

---

# 96. Context Integrity

The final request context must represent a coherent relationship:

```text id="contextintegrity1"
Employee
   ↓
Business
   ↓
Branch
   ↓
Device
   ↓
Cash Session
```

where each relationship is applicable.

An invalid relationship must prevent execution of the operation.

---

# 97. Authentication Performance

Authentication must remain fast enough for POS workloads.

Target:

* authentication-related overhead p95 ≤ 100 ms;
* cached authentication/session lookup p95 ≤ 20 ms where caching is used.

Security checks must not be removed merely to meet performance targets.

---

# 98. Authentication Availability

Authentication infrastructure should support the API availability target.

Target:

**Monthly API availability ≥ 99.9%**

Authentication dependencies must be monitored independently so failures can be distinguished from general application failures.

---

# 99. Authentication Failure Recovery

Recovery should prioritize:

1. Preserve security.
2. Reject invalid credentials.
3. Restore authentication infrastructure.
4. Preserve active valid sessions where safely possible.
5. Restore Device/session validation.
6. Resume normal API operation.

Authentication infrastructure failure must not result in fail-open authorization.

---

# 100. Security-Critical Fail-Closed Principle

If the server cannot establish required authentication state with sufficient confidence, the protected operation must fail closed.

The system must never use:

```text id="failopen1"
Authentication unavailable
      ↓
Assume authenticated
```

Instead:

```text id="failclosed1"
Authentication unavailable
      ↓
Reject protected request
```

where authoritative validation is required.

---

# 101. Authentication and Cache Consistency

Authentication-related cache may be eventually consistent only where the security impact is explicitly bounded.

Revocation-sensitive state must use:

* explicit invalidation;
* short lifetime;
* authoritative validation;
* or another mechanism that prevents unacceptable stale authorization.

---

# 102. Authentication Security Events

Security-relevant authentication events should be recorded, including where applicable:

* successful login;
* failed login;
* session creation;
* session revocation;
* refresh token reuse;
* Device registration;
* Device revocation;
* suspicious authentication activity;
* privileged reauthentication.

Events must not contain secrets.

---

# 103. Authentication and Audit

Authentication events and business audit events are related but distinct.

Authentication logs/events describe:

```text
Who authenticated?
When?
From which Device/session?
What security event occurred?
```

Business audit records describe:

```text
What business operation changed?
Who performed it?
Which Business/Branch was affected?
```

The two systems must not be unnecessarily conflated.

---

# 104. Request Context and Idempotency

Where an operation uses idempotency, the idempotency record must be associated with the relevant authenticated and operational scope.

For example, the same operation UUID must not allow:

```text id="idempotencyscope1"
Business A
```

to be reused to create an effect in:

```text id="idempotencycrossscope1"
Business B
```

Scope is part of idempotency safety.

---

# 105. Request Context and Concurrency

Concurrency control must use authoritative resource context.

Authentication does not prevent:

* stale updates;
* concurrent configuration changes;
* inventory races;
* payment races.

Those are handled by the concurrency architecture.

---

# 106. Request Context and Offline Synchronization

Offline synchronization must reconstruct the authoritative operational context from the synchronization contract.

The server must validate:

* Device;
* Employee;
* Business;
* Branch;
* operation UUID;
* authorization;
* synchronization contract version.

A client must not be able to modify its offline context by changing payload identifiers.

---

# 107. Synchronization Context Failure

If an offline operation references an invalid or revoked context:

```text id="synccontextfail1"
Invalid Device
Invalid Employee
Invalid Business
Invalid Branch
Expired Offline Authorization
```

the operation must be rejected or placed into the appropriate reconciliation state according to synchronization rules.

It must not be executed under a different inferred context.

---

# 108. Context and External Request Headers

Only documented headers have semantic meaning.

Unknown client-provided security headers must not alter authorization.

The server must distinguish:

```text id="trustedheaders1"
Trusted server-derived metadata
```

from:

```text id="clientheaders1"
Untrusted client-provided values
```

especially when requests pass through proxies.

---

# 109. Proxy and Forwarded Identity

When the application runs behind a reverse proxy, forwarded client information must be trusted only from configured trusted proxies.

The API must not trust arbitrary client-provided forwarding headers for security decisions.

---

# 110. Authentication Data Storage

Authentication/session storage must follow the backend security architecture.

Stored authentication data should include only information required for:

* session validation;
* revocation;
* security monitoring;
* lifecycle management.

Secrets must be protected using appropriate mechanisms.

---

# 111. Authentication and Horizontal Scaling

Authentication must work across multiple backend instances.

A request authenticated by one instance must remain valid on another instance when the session/token is valid.

The architecture must not depend on process-local authentication state as the only source of truth.

---

# 112. Local Authentication Cache

Local in-process authentication caches may improve performance.

However:

* they must have bounded lifetime;
* revocation must be handled safely;
* one application instance must not become the sole authority;
* stale state must not create unacceptable security exposure.

---

# 113. Distributed Authentication State

Shared session or revocation state may use a distributed store where required.

Redis may be used as a performance mechanism, but it must not become the sole authoritative source for critical Business transactions.

Authentication architecture must define what happens when the distributed cache is unavailable.

---

# 114. Request Context Object

The backend should expose a structured application-level context object rather than passing raw HTTP objects into use cases.

Conceptually:

```text id="contextobject1"
RequestContext
├── request_id
├── correlation_id
├── operation_id
├── actor
├── session
├── business
├── branch
├── device
├── cash_session
├── subscription
└── authorization
```

Only applicable values are populated.

---

# 115. Context Validation Before Use Case

Before invoking a protected application use case, the API/application boundary must ensure that required context exists.

For example:

```text id="requiredcontext1"
Close Cash Session
→ Actor required
→ Business required
→ Branch required
→ Device required where applicable
→ Cash Session required
→ Authorization required
```

Missing required context must prevent execution.

---

# 116. Context Propagation to Repository

Repositories must receive the required Business/Branch scope explicitly or through a safe scoped data-access mechanism.

Repositories must not assume that a UUID alone guarantees scope.

Database queries must enforce the appropriate scope.

---

# 117. Context Propagation to External Services

When a background or external operation requires context, only the minimum necessary identifiers should be propagated.

Never propagate:

* access tokens;
* refresh tokens;
* passwords;
* unnecessary authentication secrets.

---

# 118. Context and Transaction Boundary

The request context is established before the core transaction.

The transaction may use:

* actor identity;
* Business;
* Branch;
* Device;
* Cash Session;
* operation ID.

The context itself does not replace transactional validation.

---

# 119. Context and Historical Attribution

When a transaction is created or changed, the system should retain the relevant actor and operational context required for historical attribution.

Depending on the operation this may include:

```text id="historicalcontext1"
employee_id
business_id
branch_id
device_id
cash_session_id
operation_id
```

Historical records must not depend on future session state.

---

# 120. Context and Business Deletion

When a Business enters deletion processing, active sessions must no longer permit prohibited operations.

During permanent deletion:

* active access must be restricted;
* authentication sessions must not resurrect the Business;
* synchronization must not recreate deleted Business state.

---

# 121. Context and Subscription Expiry

Subscription expiry must not invalidate authentication unnecessarily when read-only access remains permitted.

The request context may therefore represent:

```text id="expirycontext1"
Authenticated = true
Subscription = READ_ONLY
Mutation = prohibited
```

This distinction prevents unnecessary logout while preserving business rules.

---

# 122. Context and Employee Deactivation

Employee deactivation should not necessarily destroy historical attribution.

The employee identity remains referenced by historical records.

However, the deactivated employee must not perform new protected operations.

---

# 123. Authentication Documentation

Every authentication-related endpoint must document:

* authentication requirement;
* supported credential mechanism;
* required headers;
* session behavior;
* token expiration;
* refresh behavior where applicable;
* error semantics;
* rate limits where relevant.

---

# 124. Authentication Testing

Authentication tests must cover:

* valid credentials;
* invalid credentials;
* expired token;
* revoked token/session;
* invalid signature;
* invalid issuer/audience where applicable;
* inactive Employee;
* revoked Device;
* invalid Business context;
* invalid Branch context;
* invalid Cash Session context;
* subscription restrictions;
* logout;
* refresh;
* refresh token reuse where rotation is enabled;
* concurrent sessions;
* horizontal scaling;
* cache failure;
* authentication service failure.

---

# 125. Request Context Testing

Request context tests must verify:

```text id="contexttests1"
Employee → correct Business
Employee → correct Branch
Device → correct Employee/session
Cash Session → correct Branch/Register
Resource → correct Business/Branch
Subscription → correct Business
Operation → correct scope
```

Cross-Business and cross-Branch context substitution must always fail.

---

# 126. Authentication Release Checklist

Before releasing authentication changes:

```text id="authrelease1"
[ ] Authentication contract reviewed
[ ] Token validation tested
[ ] Session lifecycle tested
[ ] Refresh behavior tested
[ ] Revocation tested
[ ] Employee deactivation tested
[ ] Device revocation tested
[ ] Business lifecycle tested
[ ] Branch context tested
[ ] Cash Session context tested
[ ] Offline authorization tested
[ ] Cache failure tested
[ ] Horizontal scaling tested
[ ] Rate limiting tested
[ ] Audit/security events verified
[ ] OpenAPI security definitions updated
[ ] Backward compatibility reviewed
```

---

# 127. System Invariants

The following invariants apply to API Authentication and Request Context:

1. Protected API operations require successful authentication.
2. Public endpoints must be explicitly defined.
3. Business UUID alone never authenticates a caller.
4. Branch UUID alone never authenticates a caller.
5. Employee UUID alone never authenticates a caller.
6. Device UUID alone never authenticates a caller.
7. Cash Session UUID alone never authenticates a caller.
8. Authentication and authorization are separate concerns.
9. Authentication establishes the authenticated actor.
10. Authorization determines whether the actor may perform the operation.
11. Access tokens have bounded lifetime.
12. Refresh tokens are distinct from access tokens.
13. Refresh tokens are not accepted as ordinary API credentials.
14. Refresh tokens must be revocable.
15. Rotated refresh tokens must not be reusable where rotation is enabled.
16. Authentication credentials must never be stored in plaintext.
17. Authentication secrets must never be logged.
18. Protected authentication traffic requires secure transport.
19. Token integrity and validity must be verified server-side.
20. Token claims cannot override authoritative server state.
21. Inactive Employees cannot perform new protected operations.
22. Revoked sessions cannot remain valid merely because an access token has not expired.
23. Revoked Devices cannot remain trusted because of stale client state.
24. Business context is determined from authoritative relationships.
25. Branch context is determined from authoritative relationships.
26. Client-provided Business context is untrusted until validated.
27. Client-provided Branch context is untrusted until validated.
28. Client-provided Employee identity cannot override authenticated identity.
29. Client-provided Device identity cannot establish device trust.
30. Client-provided Cash Session identity cannot establish an active Cash Session.
31. Resource-derived Business and Branch relationships must be validated.
32. Conflicting security context must be rejected.
33. The final request context must represent a coherent operational relationship.
34. Request ID identifies an HTTP request.
35. Operation UUID identifies a logical operation where used.
36. Request ID and Operation UUID are not interchangeable.
37. Correlation ID may connect multiple related operations.
38. Request context must be established before protected application execution.
39. Protected identity context must remain stable during a request.
40. HTTP request objects must not be passed directly into the Domain layer.
41. Domain services must not depend on access tokens or HTTP headers.
42. Business and Branch scope must remain available to data-access operations.
43. Authentication does not replace transactional validation.
44. Authentication does not replace concurrency control.
45. Authentication does not replace authorization.
46. A valid authentication session does not guarantee subscription entitlement.
47. READ_ONLY Business state may permit authentication while blocking mutations.
48. Deleted Business state must not be resurrected by old authentication sessions.
49. Cashier authentication does not imply an active Cash Session.
50. Cash operations requiring a Cash Session must validate that session.
51. Branch switching requires server-side scope recalculation.
52. Business switching requires server-side membership validation.
53. Device switching requires valid Device trust.
54. Offline access requires prior online trust establishment.
55. New devices cannot bootstrap trusted offline access while completely offline.
56. Offline authorization must be signed or otherwise protected against unauthorized modification.
57. Offline authorization must be time-bounded.
58. Offline authorization must not be extended by client-side clock manipulation.
59. Offline synchronization must validate Device, Employee, Business and Branch context.
60. Invalid offline context must not be executed under another inferred context.
61. Authentication cache cannot bypass authentication.
62. Authentication cache must have bounded lifetime.
63. Revocation-sensitive cache must have safe invalidation or equivalent protection.
64. Authentication infrastructure must fail closed for security-critical validation.
65. Authentication cache failure may reduce performance but must not grant unauthorized access.
66. Authentication must support horizontal backend scaling.
67. Process-local authentication state must not be the sole authority for distributed sessions.
68. Security-sensitive authentication events should be auditable.
69. Authentication logs must not contain secrets.
70. Business audit and authentication security events are distinct concerns.
71. Background jobs must not depend on active HTTP authentication tokens.
72. Background jobs must receive explicit execution context.
73. External integrations cannot impersonate Employees using only Employee UUIDs.
74. Only documented request headers may influence security context.
75. Arbitrary forwarded headers must not be trusted for security decisions.
76. Reverse-proxy identity metadata is trusted only from configured trusted proxies.
77. Authentication behavior is part of the API contract.
78. Supported authentication changes require controlled migration.
79. Known insecure authentication behavior must not be preserved solely for compatibility.
80. Authentication requirements must be accurately represented in OpenAPI.
81. Authentication performance must remain compatible with POS requirements.
82. Security checks must not be removed solely to satisfy latency targets.
83. Session revocation must take effect within the defined security policy.
84. Historical attribution must not depend on future authentication session state.
85. Historical Employee identity may remain referenced after Employee deactivation.
86. Authentication state must not bypass Business lifecycle restrictions.
87. Authentication state must not bypass subscription restrictions.
88. Authentication state must not bypass Branch isolation.
89. Authentication state must not bypass Device trust requirements.
90. Authentication and request context must remain deterministic, testable and auditable.

---

# 128. Related Documents

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/02_API_Design_Principles_and_Standards.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/05_API_Resource_Model_and_Naming.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/21_API_Security_CORS_CSRF_and_Data_Protection.md`

### Backend

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`

### Database

* `docs/04_Architecture/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/04_Architecture/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/04_Architecture/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### Frontend

* `docs/04_Architecture/07_Frontend/05_Authentication_and_Session_UI.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/07_Frontend/24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`
* `docs/04_Architecture/07_Frontend/25_Frontend_Offline_Synchronization_and_Conflict_Resolution.md`

### AI

* `docs/04_Architecture/08_AI/18_AI_Backend_and_API_Integration.md`
* `docs/04_Architecture/08_AI/21_AI_Security_and_Data_Privacy.md`

---

# 129. Status

**API Architecture Section:** In Progress

**Document Status:** Proposed

**Current Document:** `06_API_Authentication_and_Request_Context.md`

**Previous Document:** `05_API_Resource_Model_and_Naming.md`

**Next Document:** `07_API_Authorization_and_Scope_Enforcement.md`

