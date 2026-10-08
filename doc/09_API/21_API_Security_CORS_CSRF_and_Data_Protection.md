# API Security, CORS, CSRF and Data Protection

**Document ID:** API-21
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the API security architecture for FastFood ERP.

It establishes security requirements for:

* HTTP API protection;
* transport security;
* CORS;
* CSRF;
* authentication-related API boundaries;
* authorization enforcement;
* request protection;
* sensitive data handling;
* security headers;
* input and output protection;
* secret handling;
* Business isolation;
* Branch isolation;
* file and export protection;
* API logging;
* security monitoring;
* rate limiting;
* abuse prevention;
* browser security;
* offline API security boundaries.

The API must provide strong security without introducing unnecessary friction into normal POS operations.

---

# 2. Security Principles

The API follows these principles:

1. Security is enforced server-side.
2. Client-provided identity and scope values are never authoritative.
3. Authentication and authorization remain separate concerns.
4. Business isolation is mandatory.
5. Branch isolation is mandatory.
6. Sensitive data is minimized.
7. Secrets are never exposed through API responses or logs.
8. HTTPS is mandatory for production API traffic.
9. CORS is explicitly configured.
10. Cookie-based authentication requires CSRF protection.
11. Token-based authentication must still be evaluated for browser security risks.
12. Security failures fail closed.
13. Security controls must not depend on frontend enforcement.
14. Security controls must not be bypassed through offline synchronization.
15. Security controls must not be bypassed through cached data.
16. Security controls must not be bypassed through asynchronous workers.
17. Security events must remain observable.
18. Historical and audit records must remain protected.
19. Security mechanisms must remain compatible with POS performance requirements.
20. Simplicity is preferred when equivalent security can be achieved.

---

# 3. Security Boundary

The API security boundary is:

```text
Client
   ↓
HTTPS
   ↓
Reverse Proxy / Edge
   ↓
API Middleware
   ↓
Authentication
   ↓
Request Context
   ↓
Authorization
   ↓
Business / Branch Scope
   ↓
Application Use Case
   ↓
Domain
   ↓
Database
```

Every layer must enforce its own responsibility.

No single client-side control is considered sufficient security.

---

# 4. Defense in Depth

Security should be implemented through multiple independent controls.

Examples:

```text
TLS
 +
Authentication
 +
Authorization
 +
Business Scope
 +
Branch Scope
 +
Input Validation
 +
Rate Limiting
 +
Audit
 +
Database Constraints
 +
Monitoring
```

A failure in one non-authoritative security mechanism must not automatically create unrestricted access.

---

# 5. HTTPS

Production API traffic must use HTTPS.

Plain HTTP must not be accepted for authenticated API communication.

The deployment architecture should redirect or reject HTTP according to the infrastructure policy.

Sensitive information must never be transmitted over plaintext HTTP.

---

# 6. TLS Requirements

Production TLS configuration should:

* use modern TLS versions;
* disable obsolete protocols;
* use trusted certificates;
* renew certificates before expiration;
* protect private keys;
* avoid weak cryptographic configurations.

Exact TLS cipher configuration belongs to deployment/security hardening documentation.

---

# 7. TLS Termination

TLS may terminate at:

```text
Internet
   ↓
Reverse Proxy / Load Balancer
   ↓
Application
```

If the application trusts forwarded security headers or client information, only configured trusted proxies may provide those headers.

Untrusted clients must not be able to spoof:

* source IP;
* scheme;
* forwarded host;
* forwarded identity;
* forwarded protocol.

---

# 8. Forwarded Headers

Headers such as:

```text
X-Forwarded-For
X-Forwarded-Proto
X-Forwarded-Host
```

must only be trusted when received from configured trusted infrastructure.

The application must not blindly trust arbitrary client-supplied forwarded headers.

---

# 9. HSTS

Production browser-facing HTTPS services should use HTTP Strict Transport Security where appropriate.

Example policy:

```text
Strict-Transport-Security
```

The exact `max-age`, subdomain and preload policy must be selected according to deployment readiness.

HSTS must not be enabled carelessly before HTTPS is correctly deployed.

---

# 10. Security Headers

Browser-facing API responses may include appropriate security headers.

Potential headers include:

```text
Strict-Transport-Security
X-Content-Type-Options
Content-Security-Policy
Referrer-Policy
Permissions-Policy
Cache-Control
```

The exact set depends on whether the endpoint serves:

* API JSON;
* browser application content;
* file downloads;
* administrative pages.

---

# 11. Content-Type Protection

JSON APIs should explicitly return:

```text
Content-Type: application/json
```

The server should reject or safely handle unexpected content types.

The API must not interpret arbitrary uploaded content as executable application code.

---

# 12. CORS Purpose

CORS controls which browser origins may access the API through browser cross-origin requests.

CORS is not authentication.

CORS is not authorization.

CORS must never be used as the only protection for an API.

---

# 13. CORS Configuration

Production CORS should use an explicit allowlist.

Example:

```text
Allowed Origins:
https://app.example.com
https://admin.example.com
```

The production API should not use unrestricted:

```text
Access-Control-Allow-Origin: *
```

for authenticated browser APIs unless explicitly justified.

---

# 14. CORS Environment Separation

Development, staging and production environments should have separate CORS configurations.

Example:

```text
Development
→ localhost development origins

Staging
→ staging frontend origins

Production
→ production frontend origins
```

Development origins must not automatically become production origins.

---

# 15. Credentials and CORS

If browser requests use cookies or credentialed requests:

```text
Access-Control-Allow-Credentials: true
```

must only be used with trusted explicit origins.

Wildcard origins must not be combined with credentialed CORS behavior.

---

# 16. CORS Methods

Only required HTTP methods should be allowed.

Typical methods:

```text
GET
POST
PATCH
PUT
DELETE
OPTIONS
```

If an endpoint does not require a method, it should not be unnecessarily exposed.

---

# 17. CORS Headers

Allowed request headers should be explicitly defined where practical.

Examples:

```text
Authorization
Content-Type
X-Request-ID
X-Business-ID
X-Branch-ID
X-Device-ID
Idempotency-Key
If-Match
```

These headers remain context hints or protocol values and do not bypass server authorization.

---

# 18. CORS Preflight

The API must correctly handle `OPTIONS` preflight requests.

Preflight handling must not:

* create Business state;
* create financial transactions;
* modify permissions;
* bypass authentication requirements for actual requests.

---

# 19. CORS and Business Isolation

CORS configuration must never replace Business isolation.

For example:

```text
Allowed Origin
≠
Allowed Business
```

A valid frontend origin does not grant access to any Business.

The server must still validate:

* actor;
* Business;
* Branch;
* resource;
* permission.

---

# 20. CSRF Purpose

Cross-Site Request Forgery protection is required when browser authentication credentials are automatically attached to requests by the browser.

This is especially relevant to cookie-based authentication.

---

# 21. Cookie Authentication

If authentication uses cookies:

* cookies should use `Secure`;
* appropriate `HttpOnly` settings should be used;
* `SameSite` must be configured according to application requirements;
* CSRF protection is required for state-changing requests.

Authentication cookies must not be exposed unnecessarily to JavaScript.

---

# 22. CSRF Token

A CSRF protection mechanism should use a server-validated token for state-changing browser operations.

Possible approaches include:

* synchronizer token;
* double-submit cookie;
* framework-provided CSRF mechanism.

The selected mechanism must be documented and tested.

---

# 23. CSRF-Protected Methods

At minimum, CSRF protection applies to state-changing operations such as:

```text
POST
PUT
PATCH
DELETE
```

Safe read-only requests should not change Business state.

---

# 24. CSRF and Idempotency

CSRF protection and idempotency solve different problems.

CSRF answers:

> Did the request originate from an authorized browser interaction?

Idempotency answers:

> Should this retryable operation create another Business effect?

Both may be required for the same operation.

---

# 25. Token-Based Browser Authentication

If the browser uses a token model where credentials are not automatically attached by the browser, CSRF exposure may differ.

However, the implementation must still evaluate:

* token storage;
* XSS exposure;
* credential leakage;
* browser extensions;
* malicious scripts;
* origin policy;
* refresh-token handling.

Token-based authentication does not automatically mean “no browser security risk.”

---

# 26. XSS Protection

The API must avoid returning data that can unnecessarily become executable browser content.

The API should:

* encode/serialize safely;
* avoid unsafe HTML generation;
* validate rich-text fields;
* avoid storing executable script content;
* use appropriate content types.

Frontend rendering remains responsible for safe output handling as defined by frontend security architecture.

---

# 27. HTML Content

User-provided fields that may contain text such as:

* comments;
* expense descriptions;
* correction reasons;
* notification content;
* report notes

must not automatically be interpreted as trusted HTML.

If HTML is allowed for a specific feature, it must use explicit sanitization and a defined allowlist.

---

# 28. SQL Injection Protection

The API must never construct SQL directly from untrusted input.

Application and Repository layers must use:

* parameterized queries;
* ORM query parameters;
* validated filters;
* controlled sorting;
* controlled field selection.

Client-provided SQL expressions are prohibited.

---

# 29. Command Injection Protection

User input must never be directly passed to operating-system commands.

If an external command is unavoidable:

* use fixed executable paths;
* use argument arrays;
* validate inputs;
* restrict permissions;
* avoid shell interpretation.

---

# 30. Path Traversal Protection

File and path-related API inputs must not allow arbitrary filesystem access.

The API must never expose raw filesystem paths.

File access should use:

```text
File UUID
```

or another controlled logical identifier.

---

# 31. File Access Security

File download must validate:

* authentication;
* Business scope;
* Branch scope where applicable;
* employee permission;
* file state;
* expiration;
* resource relationship.

Knowing a File UUID is not sufficient access.

---

# 32. Export Security

Generated exports may contain sensitive Business data.

Therefore:

* export creation requires authorization;
* export access requires authorization;
* export metadata is scope-controlled;
* temporary files expire;
* downloads are audited where appropriate;
* raw storage paths are never exposed.

---

# 33. Sensitive API Data

API responses must never expose unnecessary:

* password hashes;
* access tokens;
* refresh tokens;
* private keys;
* signing secrets;
* database credentials;
* infrastructure credentials;
* internal filesystem paths;
* connection strings.

---

# 34. Data Minimization

API responses should contain only the data required by the client.

For example, a POS Product response should not automatically include:

* full Recipe history;
* audit history;
* internal cost calculations;
* unrelated employee information;
* internal security metadata.

---

# 35. Role-Based Data Exposure

A user may have access to a resource but not every field of that resource.

Example:

```text
Product
├── public operational fields
├── internal cost fields
├── recipe fields
└── audit fields
```

The API must return only fields authorized for the actor and use case.

---

# 36. Business Data Isolation

Every Business-scoped query must enforce Business scope.

Conceptually:

```text
WHERE business_id = authenticated_business_id
```

The actual implementation may use repository methods, domain context or database policies, but the Business boundary must be enforced.

---

# 37. Branch Data Isolation

Branch-scoped data must enforce Branch scope.

Example:

```text
Employee A
Branch A permission
```

must not automatically allow:

```text
Branch B data
```

even if the client supplies Branch B's UUID.

---

# 38. Cross-Business Protection

Cross-Business resource references must be rejected.

Example:

```text
Business A Order
+
Business B Product
```

must never be accepted merely because both UUIDs are valid.

The server must validate ownership and scope relationships.

---

# 39. Cross-Branch Protection

Cross-Branch operations must follow explicit Business rules.

For example, a Branch A cashier must not:

* modify Branch B cash sessions;
* alter Branch B inventory;
* change Branch B menu;
* access Branch B financial reports

unless explicitly authorized.

---

# 40. UUID Security

UUIDs provide resource identity but do not provide authorization.

The API must never assume:

```text
Valid UUID
=
Authorized Resource
```

Authorization and scope checks remain mandatory.

---

# 41. Enumeration Protection

Sensitive resources should use:

* UUIDs;
* bounded search;
* authorization;
* appropriate 404 behavior;
* rate limiting.

The API should avoid sequential identifiers for externally exposed sensitive resources where practical.

---

# 42. Request Size Limits

API requests must have bounded sizes.

Limits should apply to:

* JSON body;
* multipart upload;
* file upload;
* batch request;
* bulk request;
* synchronization batch.

The reverse proxy and application should enforce compatible limits.

---

# 43. JSON Depth and Complexity

The API should avoid accepting arbitrarily deep nested JSON.

Request validation should enforce:

* maximum nesting depth where practical;
* maximum array length;
* maximum object size;
* maximum string length.

This reduces parser and memory abuse.

---

# 44. File Upload Security

File uploads must validate:

* authenticated actor;
* Business scope;
* file size;
* allowed type;
* filename;
* extension;
* content characteristics;
* storage destination.

The original filename must not determine the storage path.

---

# 45. File Type Validation

File extension alone is not sufficient for security-sensitive uploads.

Where appropriate, the system should validate the actual file format/content.

Executable files should not be accepted where they are not required.

---

# 46. Uploaded File Isolation

Uploaded files should be stored outside executable application paths where possible.

The API must not allow uploaded content to become executable application code.

---

# 47. Secret Management

API secrets must be stored outside source code.

Examples:

* database credentials;
* JWT signing secrets;
* encryption keys;
* external provider credentials;
* storage credentials;
* webhook signing secrets.

Secrets should come from the environment or a dedicated secret-management system.

---

# 48. Secret Rotation

Security-sensitive secrets should support rotation.

Rotation must be designed so that:

* active clients do not unexpectedly fail where avoidable;
* old credentials have bounded validity;
* emergency rotation is possible.

---

# 49. Secret Exposure Prevention

Secrets must not appear in:

* API responses;
* normal logs;
* exception traces;
* audit payloads;
* metrics;
* exported reports;
* Job metadata.

---

# 50. Password Handling

If passwords are used:

* plaintext passwords must never be stored;
* password hashes must use an appropriate password hashing algorithm;
* password values must never be logged;
* authentication failure responses should avoid revealing whether an account detail is valid where enumeration is a concern.

The exact password policy belongs to authentication/security architecture.

---

# 51. Token Handling

Access and refresh tokens must:

* have bounded lifetime;
* be protected during transport;
* not appear in logs;
* not be included in ordinary audit records;
* be invalidated/revoked according to session policy.

---

# 52. Refresh Token Protection

Refresh tokens are high-value credentials.

They should have:

* bounded lifetime;
* revocation support;
* rotation where required;
* session association;
* secure storage appropriate to the client type.

---

# 53. API Authentication Errors

Authentication failures should not expose excessive information.

Avoid detailed responses such as:

```text
User exists but password is wrong.
```

Prefer stable security-safe errors.

Authentication details are defined further in:

`06_API_Authentication_and_Request_Context.md`

---

# 54. Authorization Errors

Authorization failures must not expose unnecessary information about protected resources.

The API may return:

```text
403 ACCESS_DENIED
```

or:

```text
404 RESOURCE_NOT_FOUND
```

according to the resource discovery policy.

---

# 55. Rate Limiting

Rate limiting protects the API from:

* brute force;
* credential abuse;
* enumeration;
* excessive synchronization;
* expensive reports;
* bulk abuse;
* file upload abuse.

Rate limits should be applied according to endpoint risk.

---

# 56. Rate Limit Dimensions

Rate limiting may consider:

```text
IP
Employee
Device
Business
Endpoint
Operation Type
```

The implementation must avoid relying on a single dimension.

For example, authenticated abuse should not be unrestricted merely because it originates from one trusted IP.

---

# 57. POS Rate Limiting

POS endpoints require special treatment.

Rate limits must not unnecessarily interrupt normal:

* Order creation;
* Order item updates;
* Order acceptance;
* Payment;
* Cash operations.

Limits should protect infrastructure while preserving normal branch workflows.

---

# 58. Authentication Rate Limiting

Authentication-related endpoints should have stronger protection against repeated failures.

Possible controls include:

* request limits;
* progressive delays;
* temporary blocking;
* device-aware controls;
* IP reputation where appropriate.

The API must avoid permanent account lockouts caused by trivial abuse where possible.

---

# 59. Synchronization Protection

Offline synchronization is a high-volume endpoint and must be protected against:

* oversized batches;
* repeated duplicates;
* invalid operation floods;
* unauthorized devices;
* expired offline authorization;
* cross-Business payloads.

Synchronization security is defined in:

`19_API_Offline_Synchronization_and_Reconciliation.md`

---

# 60. Offline Security Boundary

Offline authorization does not create permanent server authority.

The server must validate synchronized operations against:

* Business state;
* Branch state;
* employee state;
* device trust;
* offline authorization;
* operation identity;
* timestamps;
* domain rules.

---

# 61. Offline Device Trust

A device must be trusted before receiving offline authorization.

A new device must not bootstrap offline access without an online authorization process.

Device UUID alone is not authentication.

---

# 62. Offline Credential Expiration

Offline authorization must have a bounded lifetime.

Current default:

```text
3 days
```

The client must not extend its own authorization.

Server policy remains authoritative.

---

# 63. Clock Tampering

Offline authorization should protect against:

* clock rollback;
* invalid timestamps;
* replay;
* expired authorization.

Suspicious clock behavior should produce a security/reconciliation event according to the offline architecture.

---

# 64. API Replay Protection

State-changing requests must use:

* idempotency keys;
* operation UUIDs;
* version checks;
* domain state validation.

Replay of the same operation must not create duplicate financial or inventory effects.

---

# 65. Webhook Security

External webhooks must be authenticated.

Possible controls:

* signature verification;
* shared secret;
* timestamp validation;
* replay protection;
* provider identity verification.

Webhook endpoints must not trust a request merely because it reaches the public API.

Detailed external integration contracts are defined in:

`22_API_External_Integration_and_Webhook_Architecture.md`

---

# 66. Webhook Replay Protection

Webhook processing should retain enough identity to detect duplicate events.

Example:

```text
provider_event_id
```

or an equivalent immutable event identity.

Duplicate webhook delivery must not duplicate Business effects.

---

# 67. External API Credentials

External integration credentials must be stored securely.

They must not be:

* returned through API responses;
* exposed to ordinary frontend clients;
* logged;
* stored in Business-visible configuration unless explicitly encrypted and authorized.

---

# 68. API Logging Security

API logs should contain enough context for investigation:

```text
Request ID
Operation UUID
Endpoint
Method
Status
Latency
Business
Branch
Actor
Device
```

Sensitive values must be excluded.

---

# 69. Sensitive Request Fields

The following must never be logged in plaintext:

```text
password
access_token
refresh_token
secret
private_key
encryption_key
webhook_secret
authorization_header
```

Request bodies should be logged only through controlled structured metadata where necessary.

---

# 70. Error Logging

Production errors should log:

* request ID;
* operation ID;
* endpoint;
* exception category;
* internal stack trace in protected logs;
* Business/Branch context where safe.

The API response must not expose the internal stack trace.

---

# 71. Audit vs Security Logs

Security logs and Business audit records are different.

### Security Log

Answers:

> What security-relevant API activity occurred?

### Business Audit

Answers:

> What important Business state changed?

Both may reference:

* request ID;
* operation UUID;
* actor;
* Business;
* Branch.

---

# 72. Security Event Categories

Security monitoring should detect:

```text
AUTHENTICATION_FAILURE
AUTHORIZATION_FAILURE
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
DEVICE_REVOKED_ACCESS
EXPIRED_OFFLINE_AUTHORIZATION
REPLAY_ATTEMPT
RATE_LIMIT_EXCEEDED
SUSPICIOUS_ENUMERATION
INVALID_WEBHOOK_SIGNATURE
CSRF_FAILURE
INVALID_CORS_ORIGIN
```

---

# 73. Security Alerting

Alerts should be generated for meaningful patterns such as:

* repeated authentication failures;
* repeated authorization failures;
* abnormal cross-Business attempts;
* repeated invalid synchronization;
* unusual refund activity;
* repeated device violations;
* webhook signature failures;
* abnormal API error spikes.

Individual harmless failures should not necessarily trigger operational alerts.

---

# 74. Monitoring Cardinality

Security metrics should avoid unbounded labels.

Do not use arbitrary:

```text
employee_uuid
business_uuid
request_uuid
```

as metric labels without strong justification.

Detailed identifiers belong in logs/traces rather than high-cardinality metric dimensions.

---

# 75. Security Headers and API Caching

Sensitive responses should use appropriate cache controls.

Examples:

```text
Cache-Control: no-store
```

may be required for:

* authentication responses;
* sensitive employee data;
* financial data;
* security configuration.

Read-only public/reference resources may use bounded caching where safe.

---

# 76. Browser Cache Protection

Sensitive Business data must not be unintentionally stored in browser caches.

The API and frontend should coordinate cache policies for:

* financial data;
* employee data;
* reports;
* audit records;
* configuration;
* notifications.

---

# 77. ETag Security

ETag and conditional requests may improve performance.

However:

* ETag is not authorization;
* ETag must not reveal sensitive internal information;
* a valid ETag does not grant access to a resource.

---

# 78. API Response Filtering

The response layer must ensure that internal fields do not leak accidentally through generic ORM serialization.

Explicit DTOs/read models are preferred.

Avoid:

```text
return database_model_directly
```

when it can expose fields not intended for the API.

---

# 79. Mass Assignment Protection

Generic request-to-model mapping is prohibited for sensitive resources.

Clients must not be able to modify fields such as:

```text
business_id
created_by
created_at
approved_by
approved_at
configuration_version
audit_state
payment_state
cash_session_state
```

unless an explicit authorized command supports that behavior.

---

# 80. Client-Controlled Ownership Fields

The client must never directly assign authoritative ownership fields without server validation.

Examples:

```text
business_id
branch_id
employee_id
created_by
approved_by
device_id
cash_session_id
```

The server derives or validates these relationships.

---

# 81. Financial Data Protection

Financial APIs require strict protection.

The API must not trust client-provided:

* final Order total;
* payment state;
* refundable amount;
* cash balance;
* expected cash;
* inventory cost.

The server calculates or validates authoritative financial state.

---

# 82. Inventory Data Protection

The API must not trust:

```text
client_stock_quantity
client_available_quantity
client_final_stock
```

as authoritative inventory state.

Inventory operations must use server-side transactional validation.

---

# 83. Configuration Data Protection

Configuration APIs must enforce:

* permission;
* Business scope;
* Branch scope;
* optimistic concurrency;
* audit;
* approval where required.

Stale clients must not silently overwrite newer configuration.

---

# 84. Subscription Data Protection

Subscription state is an authorization boundary.

The API must not trust:

```text
client_subscription_status
client_expiry_date
client_tariff
```

The server must determine entitlement.

---

# 85. Business Deletion Protection

Deleted Business data must not become accessible through stale:

* API cache;
* Job;
* offline device;
* synchronization request;
* browser cache;
* file URL.

Deletion state must propagate through all relevant access paths.

---

# 86. Security and Background Jobs

Background workers must receive controlled execution context.

Workers must not reuse user access tokens unnecessarily.

Sensitive Jobs should use:

```text
Job ID
Business
Branch
Actor
Operation
Authorization context
```

and revalidate security-sensitive state where required.

---

# 87. Security and Cache

Cached authorization/configuration state must be:

* bounded;
* scope-aware;
* version-aware;
* invalidatable.

Cache failure must never result in fail-open authorization.

---

# 88. Security and Redis

Redis is not authoritative for:

* Business identity;
* permission ownership;
* financial state;
* inventory state;
* subscription authority.

Redis failures must not weaken authorization.

---

# 89. Security and Database Constraints

API security must be complemented by database constraints.

Examples:

* Business-scoped foreign keys;
* unique constraints;
* valid state relationships;
* non-negative inventory;
* immutable audit records;
* valid ownership relationships.

The database is a final integrity boundary, not a replacement for API authorization.

---

# 90. Security and Transactions

Security-sensitive state changes must occur inside appropriate transactions.

Example:

```text
Authorize
   ↓
Validate
   ↓
Transaction
   ↓
Business Change
   ↓
Audit / Outbox
   ↓
Commit
```

Security checks must not be separated from the authoritative operation in a way that creates a race condition.

---

# 91. Race Condition Protection

Examples requiring concurrency protection:

* permission changes;
* employee deactivation;
* refunds;
* payment;
* cash closing;
* device revocation;
* subscription state transitions;
* configuration changes.

The API must rely on optimistic concurrency, transactional locking or database constraints where appropriate.

---

# 92. Request Timeout Protection

API requests must have bounded execution time.

An attacker must not be able to consume unlimited:

* worker time;
* database connections;
* memory;
* external service calls.

Long operations should move to asynchronous Jobs.

---

# 93. Regular Expression Safety

Validation patterns must avoid catastrophic backtracking.

Complex user-controlled regular expressions must not be executed without appropriate safeguards.

---

# 94. Query Complexity Protection

Search/filter endpoints must prevent abusive queries through:

* bounded pagination;
* allowed filters;
* indexed fields;
* maximum date range where necessary;
* maximum search length;
* query timeout.

The client must not control arbitrary SQL expressions.

---

# 95. Report Security

Reports may contain sensitive Business information.

Report endpoints must enforce:

* Business scope;
* Branch scope;
* employee permission;
* report-type permission;
* subscription state;
* date-range limits where necessary.

Large report requests should be asynchronous.

---

# 96. Audit Security

Audit records are immutable.

The API must not expose mechanisms allowing ordinary clients to:

* edit audit events;
* delete audit events;
* rewrite historical attribution;
* alter original event timestamps.

Audit reads remain permission-controlled.

---

# 97. Historical Data Protection

Current configuration must never reinterpret:

* historical Order prices;
* historical payments;
* historical refunds;
* historical inventory deductions;
* historical Recipe Versions;
* historical Set configurations;
* historical report versions.

API security includes protection against unauthorized historical reinterpretation.

---

# 98. Data Retention

Security logs, audit records, files and Jobs follow separate retention policies.

Retention must consider:

* operational needs;
* audit requirements;
* Business lifecycle;
* privacy;
* storage cost.

Deleting temporary data must not delete required authoritative history.

---

# 99. Data Deletion

Business deletion must remove eligible data according to lifecycle policy.

Deletion must not be bypassed through:

* stale API sessions;
* Jobs;
* offline synchronization;
* cached responses;
* file links.

Deletion operations must be auditable.

---

# 100. Privacy by Design

API design should minimize collection and exposure of personal information.

For example:

* customer phone/address are stored only where required for current delivery orders;
* employee data is exposed according to role;
* unnecessary personal fields are not returned;
* logs avoid unnecessary personal data.

---

# 101. Data Classification

API data should be conceptually classified as:

```text
Public / Non-sensitive
Operational
Confidential
Sensitive
Security Secret
```

Examples:

```text
Menu name
→ Operational

Employee payroll
→ Confidential / Sensitive

Access token
→ Security Secret
```

The classification determines access, logging and caching policy.

---

# 102. Sensitive Data in URLs

Sensitive information should not be placed in:

* query strings;
* path segments;
* redirect URLs

when avoidable.

URLs may appear in:

* browser history;
* reverse proxy logs;
* monitoring;
* analytics.

Use request bodies or secure headers for sensitive values where appropriate.

---

# 103. Referrer Protection

Browser-facing responses should use an appropriate `Referrer-Policy`.

Sensitive API endpoints should avoid leaking sensitive URL information through browser navigation or external requests.

---

# 104. Security and API Documentation

OpenAPI documentation must not expose:

* production secrets;
* internal credentials;
* private infrastructure;
* hidden administrative endpoints without appropriate documentation controls.

Example values must be synthetic.

---

# 105. Security and Development Environments

Development environments must not use production credentials.

Production Business data must not be copied into development environments without approved protection and anonymization.

---

# 106. Security and Testing

Security tests must include:

* authentication bypass;
* authorization bypass;
* Business isolation;
* Branch isolation;
* CSRF;
* CORS;
* XSS-related payloads;
* SQL injection;
* path traversal;
* request size abuse;
* rate limiting;
* replay;
* idempotency;
* file access;
* webhook signature validation;
* token leakage;
* secret leakage.

---

# 107. Security Regression Testing

Security controls are release-blocking when they protect:

* Business isolation;
* Branch authorization;
* financial operations;
* authentication;
* privileged configuration;
* audit integrity;
* offline authorization.

A regression in these controls must block release.

---

# 108. API Security Performance

Security controls must remain compatible with POS performance.

Initial targets:

| Operation                               |   Target |
| --------------------------------------- | -------: |
| Authentication overhead p95             | ≤ 100 ms |
| Cached authorization lookup p95         |  ≤ 20 ms |
| Business/Branch scope validation p95    |  ≤ 50 ms |
| CSRF validation p95                     |  ≤ 10 ms |
| Request security validation p95         |  ≤ 20 ms |
| Normal security middleware overhead p95 |  ≤ 50 ms |

Targets exclude slow external dependencies.

---

# 109. API Availability

Initial target:

**≥ 99.9% monthly API availability**

Security failures must fail closed even during degraded infrastructure conditions.

Where an optional security cache is unavailable, authoritative security validation should be used where practical.

---

# 110. Security Degradation

Allowed degradation:

```text
Redis unavailable
→ authoritative validation

Cache unavailable
→ database fallback

Optional security analytics unavailable
→ core authorization continues
```

Not allowed:

```text
Authorization unavailable
→ allow request
```

or:

```text
Business scope unavailable
→ trust client Business ID
```

---

# 111. Incident Response

Security incidents should preserve:

* Request ID;
* Operation UUID;
* Job ID where applicable;
* Business;
* Branch;
* Actor;
* Device;
* timestamp;
* endpoint;
* security event.

Incident handling is defined further in backend operations/security architecture.

---

# 112. Security Monitoring

Important metrics include:

```text
authentication_failures
authorization_failures
scope_denials
csrf_failures
cors_rejections
rate_limit_events
replay_attempts
invalid_webhook_events
suspicious_file_access
security_event_count
```

Metrics must remain low-cardinality.

---

# 113. Security Alerts

Operational alerts may be triggered by:

* sudden authentication failure spikes;
* repeated cross-Business access attempts;
* repeated Branch scope violations;
* repeated device revocations;
* abnormal refund attempts;
* repeated CSRF failures;
* webhook signature failures;
* synchronization abuse;
* unusual file access patterns.

---

# 114. API Security Documentation

Each endpoint must document:

* authentication requirement;
* permission;
* Business scope;
* Branch scope;
* sensitive fields;
* idempotency requirement;
* CSRF requirements where relevant;
* rate limit category;
* response cache policy;
* audit behavior.

---

# 115. Security Change Management

Security-sensitive API changes must consider:

1. Authentication;
2. Authorization;
3. Business isolation;
4. Branch isolation;
5. Database constraints;
6. frontend behavior;
7. offline synchronization;
8. cache behavior;
9. background jobs;
10. external integrations;
11. audit;
12. performance.

A security change must not be reviewed only at the route level.

---

# 116. API Security Guardrails

The implementation must prohibit:

* HTTP-only production authentication;
* unrestricted authenticated CORS;
* wildcard credentialed CORS;
* cookie authentication without CSRF protection;
* client-controlled Business authorization;
* client-controlled Branch authorization;
* client-controlled payment state;
* client-controlled inventory state;
* client-controlled subscription state;
* raw filesystem paths in API responses;
* plaintext secrets;
* secrets in logs;
* direct SQL from request input;
* arbitrary SQL sorting/filtering;
* arbitrary command execution;
* unbounded request sizes;
* unbounded bulk requests;
* unbounded file uploads;
* fail-open authorization;
* cache-based authorization bypass;
* offline authorization extension by clients;
* asynchronous worker authorization bypass;
* direct modification of audit history.

---

# 117. Security Architecture Invariants

The following invariants apply to API Security, CORS, CSRF and Data Protection:

1. Production authenticated API traffic uses HTTPS.
2. TLS private keys remain protected.
3. Obsolete TLS configurations are disabled.
4. Forwarded security headers are trusted only from configured proxies.
5. CORS is not authentication.
6. CORS is not authorization.
7. Production authenticated CORS uses explicit origins.
8. Credentialed CORS does not use unrestricted wildcard origins.
9. Development CORS configuration does not automatically apply to production.
10. CORS does not bypass Business authorization.
11. CORS does not bypass Branch authorization.
12. CORS preflight does not mutate Business state.
13. Cookie authentication requires CSRF protection.
14. CSRF protects state-changing browser requests.
15. CSRF and idempotency remain separate controls.
16. Token authentication does not automatically eliminate browser security risks.
17. Security headers are applied according to endpoint context.
18. Sensitive responses use appropriate cache controls.
19. Passwords are never returned.
20. Passwords are never logged.
21. Access tokens are never logged.
22. Refresh tokens are never logged.
23. Private keys are never returned.
24. Secrets are not stored in source code.
25. Secrets are not exposed through API errors.
26. Secrets are not exposed through audit records.
27. Secrets are not exposed through metrics.
28. Sensitive data is minimized in API responses.
29. API responses are explicitly serialized.
30. ORM models are not blindly exposed as API responses.
31. Mass assignment is prohibited for sensitive fields.
32. Client cannot directly assign authoritative ownership fields.
33. Client Business UUID is never sufficient authorization.
34. Client Branch UUID is never sufficient authorization.
35. Client Employee UUID is never sufficient authentication.
36. Client Device UUID is never sufficient authentication.
37. Valid UUID does not imply authorization.
38. Business scope is enforced server-side.
39. Branch scope is enforced server-side.
40. Cross-Business references are rejected.
41. Cross-Branch access requires explicit authorization.
42. Sensitive resources use appropriate enumeration protection.
43. File UUID does not grant file access.
44. File paths are never exposed as authoritative storage identifiers.
45. File downloads are authorization-controlled.
46. Uploaded filenames do not determine storage paths.
47. Uploaded files cannot become executable application code.
48. Upload size is bounded.
49. Request body size is bounded.
50. JSON nesting and array complexity are bounded where required.
51. SQL injection protection uses parameterized queries.
52. Client-controlled SQL expressions are prohibited.
53. Command injection is prohibited.
54. Path traversal is prohibited.
55. Regular expression validation cannot introduce uncontrolled resource consumption.
56. Search queries are bounded.
57. Pagination is bounded.
58. Rate limiting is applied to abuse-sensitive endpoints.
59. POS rate limiting does not unnecessarily interrupt normal operations.
60. Authentication endpoints have stronger abuse protection.
61. Synchronization endpoints have bounded request limits.
62. Bulk endpoints have bounded request limits.
63. File uploads have bounded request limits.
64. Report generation has bounded resource limits.
65. Security failures fail closed.
66. Authorization cache failure does not create authorization.
67. Redis failure does not weaken security.
68. Cache data is never the authoritative security source.
69. Permission changes invalidate or bypass stale authorization state.
70. Employee deactivation prevents new unauthorized operations.
71. Device revocation prevents future unauthorized operations.
72. Subscription expiry cannot be bypassed through cached state.
73. READ_ONLY Business state blocks prohibited mutation.
74. DELETED Business state cannot be resurrected.
75. Offline authorization has bounded lifetime.
76. Offline clients cannot extend authorization lifetime.
77. Offline timestamps cannot override server authority.
78. Offline synchronization cannot bypass authorization.
79. Replay protection exists for retryable state-changing operations.
80. Duplicate financial effects are prevented.
81. Webhooks require authentication or signature verification.
82. Webhook replay protection is required where duplicate effects are possible.
83. External credentials are never exposed to ordinary frontend clients.
84. Background workers do not require user tokens unnecessarily.
85. Sensitive Jobs revalidate required security state.
86. Async workers cannot bypass Business scope.
87. Async workers cannot bypass Branch scope.
88. Async workers cannot bypass subscription restrictions.
89. Security events are observable.
90. Security metrics avoid uncontrolled cardinality.
91. Sensitive request values are not logged.
92. API error responses do not expose stack traces.
93. Internal exception details remain protected in server logs.
94. Business audit and security logs remain separate concepts.
95. Audit records are immutable.
96. Historical transaction data cannot be rewritten through API security gaps.
97. Current configuration cannot reinterpret historical financial data.
98. Financial values remain server-authoritative.
99. Inventory state remains server-authoritative.
100. Payment state remains server-authoritative.
101. Subscription state remains server-authoritative.
102. Database constraints complement API security.
103. Security-sensitive state changes use appropriate transactions.
104. Race conditions are protected through concurrency controls.
105. Long-running requests are bounded.
106. Long-running processing uses asynchronous Jobs where appropriate.
107. External calls have bounded timeouts.
108. External retries are bounded.
109. Unknown external outcomes require reconciliation.
110. Production development credentials are not reused.
111. Production Business data is not casually copied into development.
112. Security regression tests are release-blocking for critical boundaries.
113. Business isolation is a release-blocking security requirement.
114. Branch isolation is a release-blocking security requirement.
115. Financial authorization is a release-blocking correctness requirement.
116. Audit integrity is a release-blocking requirement.
117. Offline authorization integrity is a release-blocking requirement.
118. Security controls remain within defined performance targets.
119. Security monitoring must not become a high-cardinality data leak.
120. API security changes require cross-layer review.
121. Security design remains compatible with horizontal scaling.
122. Security design remains compatible with offline operation.
123. Security design remains compatible with asynchronous processing.
124. Security design remains compatible with caching.
125. Security design remains compatible with the modular monolith architecture.
126. Security must not be traded for cache hit rate.
127. Security must not be traded for POS convenience.
128. Security must not be traded for API performance without explicit risk review.
129. Security configuration must be environment-specific.
130. Security-sensitive configuration changes must be auditable.
131. CORS origins must be explicitly controlled.
132. CSRF policy must be explicitly documented.
133. Sensitive browser responses must have appropriate cache policy.
134. API documentation must not expose production secrets.
135. Security testing must include Business and Branch isolation.
136. Security testing must include authentication and authorization bypass.
137. Security testing must include CORS and CSRF.
138. Security testing must include replay and idempotency abuse.
139. Security testing must include file and export access.
140. Security testing must include request-size abuse.
141. Security testing must include rate-limit abuse.
142. Security testing must include webhook verification.
143. Security testing must include secret leakage detection.
144. Security incidents must preserve sufficient forensic context.
145. Security event attribution must preserve actor and device context where available.
146. Security controls must preserve historical integrity.
147. Security controls must preserve transaction correctness.
148. Security controls must preserve Business data confidentiality.
149. Security controls must preserve Branch data confidentiality.
150. Security architecture must fail safely under infrastructure degradation.
151. Security architecture must not rely on frontend-only controls.
152. Security architecture must not rely on CORS as access control.
153. Security architecture must not rely on UUID secrecy.
154. Security architecture must not rely on cache freshness alone for authorization.
155. Security architecture must not allow stale security state to authorize indefinitely.
156. Security architecture must support emergency credential rotation.
157. Security architecture must support device revocation.
158. Security architecture must support session revocation.
159. Security architecture must support controlled secret rotation.
160. Security architecture must preserve operational simplicity where equivalent security is available.

---

# 118. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/19_Attendance_and_Payroll.md`
* `docs/02_System_Analysis/22_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/04_Architecture/09_API/22_API_External_Integration_and_Webhook_Architecture.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

---

# 119. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `21_API_Security_CORS_CSRF_and_Data_Protection.md`

**Previous Document:** `20_API_Async_Jobs_Bulk_and_Batch_Operations.md`

**Next Document:** `22_API_External_Integration_and_Webhook_Architecture.md`

---

## Final Principle

> API security must be enforced by the server, preserve strict Business and Branch isolation, protect sensitive data, and fail closed. CORS, CSRF, authentication, authorization, rate limiting, validation, database constraints and audit must work together without becoming a performance bottleneck for normal POS operations.

