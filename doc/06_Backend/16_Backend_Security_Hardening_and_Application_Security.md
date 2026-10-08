# Backend Security Hardening and Application Security

**Document ID:** BA-16
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines backend security hardening and application security requirements for FastFood ERP.

The primary objective is:

> The backend must reject unauthorized, malformed, stale, replayed, cross-Business, cross-Branch and otherwise invalid operations by default while preserving normal POS performance.

Security must be implemented as a layered system.

The architecture must protect:

* Business data;
* Branch data;
* employee identities;
* permissions;
* authentication credentials;
* devices;
* offline authorization;
* Orders;
* Payments;
* Inventory;
* Cash Sessions;
* configuration;
* reports;
* files;
* audit records;
* synchronization;
* subscription state.

Security controls must not unnecessarily complicate normal cashier and POS workflows.

---

# 2. Scope

This document covers:

* security principles;
* threat model;
* defense in depth;
* secure defaults;
* authentication hardening;
* authorization hardening;
* Business isolation;
* Branch isolation;
* tenant isolation;
* session security;
* token security;
* password security;
* credential handling;
* trusted devices;
* offline authorization;
* synchronization security;
* request validation;
* input validation;
* output security;
* API security;
* idempotency;
* replay protection;
* concurrency security;
* rate limiting;
* brute-force protection;
* CSRF;
* CORS;
* security headers;
* TLS;
* secrets;
* encryption;
* cryptographic key management;
* logging;
* security audit;
* file security;
* SQL injection prevention;
* SSRF prevention;
* command injection prevention;
* path traversal;
* deserialization;
* dependency security;
* error handling;
* background job security;
* monitoring;
* incident response;
* backup security;
* data deletion;
* security testing;
* performance targets;
* security SLOs;
* security invariants.

---

# 3. Security Principles

The system follows these principles:

1. Deny by default.
2. Authenticate before authorization.
3. Authorize every protected operation.
4. Server-side validation is authoritative.
5. Client-provided identity and scope are never trusted.
6. Business isolation is mandatory.
7. Branch isolation is mandatory.
8. Permission checks are centralized.
9. Subscription entitlement is an authorization boundary.
10. Trusted device is a security boundary for offline operation.
11. PostgreSQL remains authoritative for transactional state.
12. Cache must never bypass security.
13. Security failures must fail closed.
14. Secrets must never be exposed in source code or logs.
15. Sensitive data must be encrypted where appropriate.
16. Security controls must be observable.
17. Historical audit data must not be silently modified.
18. Security mechanisms must not unnecessarily slow POS.
19. Security must be layered rather than dependent on one control.
20. Simplicity is preferred when equivalent security can be achieved with fewer moving parts.

---

# 4. Threat Model

The backend must assume that clients can be compromised or manipulated.

Potential attackers include:

* unauthorized external users;
* compromised employee accounts;
* malicious employees;
* former employees;
* compromised trusted devices;
* manipulated offline clients;
* modified API requests;
* replayed requests;
* stale synchronization requests;
* compromised integrations;
* automated brute-force clients;
* attackers attempting Business/Branch traversal;
* attackers attempting file access;
* attackers attempting privilege escalation.

The server must not rely on the client behaving correctly.

---

# 5. Security Boundaries

Important security boundaries are:

```text id="secbd1"
Internet / Client
        ↓
API Security Boundary
        ↓
Authentication
        ↓
Authorization
        ↓
Business / Branch Scope
        ↓
Application Use Case
        ↓
Domain Rules
        ↓
Transaction
        ↓
PostgreSQL
```

Additional boundaries exist for:

```text id="secbd2"
Trusted Device
Offline Authorization
Storage
Background Workers
External Integrations
Synchronization
```

---

# 6. Defense in Depth

No single security mechanism is sufficient.

For a sensitive operation, the system may validate:

```text id="defdepth1"
Authentication
+
Employee Status
+
Business Status
+
Branch Scope
+
Permission
+
Subscription Entitlement
+
Device Trust
+
Operation State
+
Business Rules
+
Concurrency
+
Audit
```

Not every operation requires every control, but the required controls must be explicit.

---

# 7. Secure Defaults

The default behavior must be secure.

Examples:

```text id="securedefault1"
Unknown Permission
→ DENY

Unknown Business
→ DENY

Unknown Branch
→ DENY

Invalid Employee
→ DENY

Invalid Device
→ DENY

Expired Authorization
→ DENY

Invalid Signature
→ DENY

Malformed Request
→ REJECT

Missing Scope
→ REJECT
```

Security must never depend on developers remembering to add an optional security check.

---

# 8. Authentication Boundary

Authentication answers:

> Who is making this request?

Authentication must establish a trusted employee or system identity before protected operations are executed.

Authentication context should include where applicable:

```text id="authctx1"
employee_id
business_id
branch_id
device_id
authentication_method
session_id
source
```

Client-provided context is not authoritative.

---

# 9. Employee Authentication

Employee authentication must validate:

* credentials;
* employee status;
* Business association;
* authentication state;
* session/token validity;
* device requirements where applicable.

Inactive or suspended employees must not authenticate for new operational activity.

---

# 10. Password Security

Passwords must:

* never be stored in plaintext;
* never be logged;
* never be returned through APIs;
* be stored using a modern adaptive password-hashing algorithm;
* use a unique salt;
* be verified server-side.

Recommended algorithms include:

* Argon2id;
* bcrypt where legacy compatibility requires it.

Argon2id should be preferred for new implementations.

---

# 11. Password Policy

Password policy should balance security and usability.

The system should enforce:

* reasonable minimum length;
* rejection of known compromised passwords where feasible;
* no maximum length that unnecessarily limits password managers;
* secure password reset;
* protection against brute force.

Password complexity rules should not become unnecessarily complicated.

---

# 12. Password Reset

Password reset must require a secure, short-lived, single-use reset mechanism.

Reset tokens must:

* be random;
* be time-limited;
* be single-use;
* be stored securely;
* not contain plaintext credentials;
* become invalid after successful use.

Password reset events should be security-audited.

---

# 13. Session Security

Authenticated sessions must be:

* uniquely identifiable;
* revocable;
* time-bounded;
* protected against fixation;
* associated with the authenticated identity.

Logout must invalidate the relevant session/token where the architecture requires server-side revocation.

Logout must not automatically close a Cash Session.

---

# 14. Token Security

If bearer tokens are used:

* tokens must be cryptographically unpredictable;
* token lifetime must be bounded;
* sensitive claims must be minimized;
* token transport must use TLS;
* revoked sessions must not remain valid indefinitely.

Do not place sensitive Business data unnecessarily inside tokens.

---

# 15. Token Claims

Tokens should contain only claims required for authentication and routing.

Authorization-sensitive state such as current permission configuration should remain server-controlled.

Example:

```text id="tokenclaims1"
employee_id
session_id
token_version
issued_at
expires_at
```

Avoid treating client-visible claims as authoritative Business or Branch scope.

---

# 16. Session Revocation

The system must support revocation for security-sensitive cases.

Examples:

* password compromise;
* employee deactivation;
* suspicious login;
* device compromise;
* security incident;
* explicit session termination.

Revocation should be fast enough to satisfy the security SLO.

---

# 17. Authentication Rate Limiting

Authentication endpoints must have rate limiting.

Protection should cover:

* password login;
* password reset;
* verification codes;
* trusted-device registration;
* sensitive re-authentication.

Rate limits should be based on appropriate identifiers such as:

* account;
* IP/network source;
* device;
* endpoint.

The system must avoid making normal POS usage unusable.

---

# 18. Brute-Force Protection

Repeated authentication failures should trigger controlled protection.

Possible mechanisms:

* progressive delay;
* temporary lock;
* rate limiting;
* security notification;
* additional verification.

Permanent account lockout should be used cautiously because it can itself become a denial-of-service vector.

---

# 19. Authentication Monitoring

Monitor:

* failed logins;
* successful logins;
* password reset requests;
* suspicious login patterns;
* repeated verification failures;
* device registration attempts;
* revoked device use.

Security monitoring must use low-cardinality metrics.

Detailed identities belong in security logs rather than metric labels.

---

# 20. Authorization Pipeline

Protected operations should follow a centralized authorization pipeline:

```text id="authpipe1"
Authenticate
    ↓
Employee Active?
    ↓
Business Active?
    ↓
Branch Scope Valid?
    ↓
Permission Valid?
    ↓
Subscription Entitlement?
    ↓
Trusted Device Requirement?
    ↓
Business Rule
    ↓
Concurrency Validation
    ↓
Execute
```

The exact sequence may vary for individual operations, but no required control may be skipped.

---

# 21. Permission Model

Authorization follows the established model:

```text id="perm1"
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

The resulting effective permission is calculated server-side.

---

# 22. Deny by Default

Unknown or missing permissions must result in denial.

The system must not interpret:

```text
permission = null
```

as:

```text
allow
```

---

# 23. Manager Privilege Boundary

Managers must not grant permissions beyond their own authority.

The server must validate:

* target permission;
* granting employee authority;
* Branch scope;
* Business scope;
* subscription limits.

The UI alone must never enforce this restriction.

---

# 24. Owner Privilege Boundary

Owner-level operations remain Business-scoped.

An Owner must not access another Business merely by manipulating:

```text
business_id
branch_id
employee_id
file_id
order_id
```

All references must be validated against authenticated Business scope.

---

# 25. Super Admin Boundary

Super Admin is a separate high-privilege platform role.

Super Admin operations must be isolated from ordinary Business employee permissions.

Super Admin access should require stronger security controls because compromise has platform-wide impact.

---

# 26. Business Isolation

Every Business-scoped query and command must enforce Business scope.

Example:

```text id="biziso1"
Authenticated Business = A

Requested Order = Business B

Result:
DENY / NOT FOUND
```

The system must not reveal whether the resource exists in another Business when that would disclose information.

---

# 27. Branch Isolation

Branch-scoped operations must validate Branch membership and permission.

Example:

```text id="branchiso1"
Employee
   ↓
Allowed Branch A

Request:
Branch B Inventory

Result:
DENY
```

---

# 28. Object-Level Authorization

Every protected object must be checked against the current security context.

This applies to:

* Orders;
* Payments;
* Cash Sessions;
* Inventory;
* Employees;
* Products;
* Recipes;
* Reports;
* Files;
* Notifications;
* Audit records.

A valid endpoint permission alone is not sufficient.

---

# 29. Insecure Direct Object Reference Prevention

The backend must not trust identifiers supplied by clients.

Example:

```text id="idor1"
GET /orders/{order_id}
```

must validate:

```text
Order.Business == Authenticated.Business
Order.Branch == Allowed Branch
Employee has required permission
```

---

# 30. Query-Level Scope Enforcement

Repository methods should support validated scope.

Example conceptual interface:

```text id="scope1"
get_order(
    order_id,
    business_id,
    branch_scope
)
```

A repository must not accidentally retrieve an object globally and rely on the caller to remember filtering later.

---

# 31. Business Context

Business context must be derived from authenticated security context.

The client must not be able to switch Business by sending another Business UUID.

Business switching, if ever supported for a privileged identity, must be an explicit authorized operation.

---

# 32. Branch Context

Branch switching must:

* validate employee assignment;
* recalculate effective permissions;
* load Branch configuration;
* invalidate/reload relevant cached context;
* update security context.

A previous Branch context must not leak into the new Branch.

---

# 33. Subscription as Security Boundary

Subscription state is an authorization boundary.

For READ_ONLY Businesses:

* allowed reads remain available;
* blocked modifications are denied;
* exports remain available where policy allows;
* offline authorization cannot bypass the restriction.

---

# 34. Security and Offline Authorization

Offline operation is allowed only for trusted devices with valid offline authorization.

Offline authorization must be:

* cryptographically signed;
* time-bounded;
* Business-bound;
* Branch-bound where applicable;
* device-bound;
* employee-bound where required;
* permission-aware;
* revocable through synchronization;
* protected against replay.

---

# 35. Offline Grace Period

The current offline authorization lifetime is:

**3 days.**

The value must be centralized in configuration and must not be duplicated throughout the codebase.

---

# 36. Offline Authorization Signature

The device must not be able to create or extend its own offline authorization.

Conceptually:

```text id="offsig1"
Server
  ↓
Create authorization
  ↓
Sign
  ↓
Trusted Device
  ↓
Verify signature locally
```

A modified authorization must fail verification.

---

# 37. Offline Authorization Claims

Offline authorization may contain:

```text id="offclaims1"
authorization_id
business_id
branch_scope
employee_id
device_id
permission_snapshot/version
issued_at
expires_at
configuration_version
signature
```

Only the minimum necessary information should be included.

---

# 38. Offline Replay Protection

Offline operations must use unique operation UUIDs.

The server must reject duplicate operations after synchronization.

The device must not be able to submit the same financial transaction repeatedly.

---

# 39. Offline Clock Manipulation

The client clock must not be considered fully trustworthy.

The system should detect:

* significant backward clock movement;
* inconsistent timestamps;
* impossible authorization timing;
* repeated offline periods inconsistent with server observations.

Clock anomalies may restrict further offline activity until revalidation.

---

# 40. Synchronization Authentication

Synchronization requests must authenticate:

* trusted device;
* employee/system identity;
* Business;
* Branch context where applicable.

Client-supplied identifiers must be cross-validated.

---

# 41. Synchronization Authorization

Every synchronized operation must be validated as if it were a normal authorized operation.

Offline status does not grant broader authority.

A transaction created offline with insufficient permission must be rejected or placed into a controlled conflict state according to the synchronization policy.

---

# 42. Synchronization Integrity

Synchronization must verify:

* operation UUID;
* device identity;
* authorization;
* Business scope;
* Branch scope;
* operation timestamp;
* dependency;
* signature where required;
* current lifecycle state;
* idempotency;
* business rules.

---

# 43. Replay Protection

Security-sensitive commands should be resistant to replay.

Controls include:

* operation UUID;
* idempotency record;
* nonce where required;
* timestamp/window validation;
* signature;
* transaction state validation.

---

# 44. Idempotency Security

Idempotency records must be scoped appropriately.

Example:

```text id="idemsec1"
Business
+
Operation UUID
+
Operation Type
```

A valid operation UUID from one Business must not be reused to affect another Business.

---

# 45. Request Validation

Every API request must validate:

* data type;
* required fields;
* allowed values;
* length;
* numeric range;
* identifier format;
* date/time validity;
* nested object structure.

Validation must occur before domain processing.

---

# 46. Input Validation

Input validation should use allowlists where possible.

Examples:

```text
Allowed enum values
Allowed file types
Allowed sort fields
Allowed report types
Allowed pagination limits
Allowed markup range
```

Do not accept arbitrary fields and silently ignore security-sensitive unknown fields.

---

# 47. Mass Assignment Protection

API clients must not be able to modify protected fields simply by including them in JSON.

Protected fields include potentially:

```text
business_id
branch_id
employee_id
role
permissions
subscription_state
approved_by
created_by
audit fields
financial state
```

Application commands should explicitly map accepted fields.

---

# 48. SQL Injection Prevention

The application must use parameterized queries or ORM query mechanisms.

Never construct SQL using direct string concatenation with user input.

Dynamic SQL must use allowlisted identifiers.

---

# 49. ORM Security

ORM usage does not automatically eliminate all security issues.

Developers must avoid:

* unsafe raw SQL;
* user-controlled SQL fragments;
* dynamic unvalidated ordering;
* unsafe filter expressions.

---

# 50. Dynamic Sorting

If API clients can specify sorting:

```text
?sort=created_at
```

the server must map allowed values to known columns.

It must not directly insert the client value into SQL.

---

# 51. Pagination Limits

Pagination must have bounded maximum values.

Example:

```text
page_size <= configured maximum
```

The client must not request unlimited records.

---

# 52. Request Body Limits

The API must enforce bounded:

* request body size;
* multipart size;
* JSON nesting;
* array length;
* field length.

This protects against resource exhaustion.

---

# 53. JSON Depth

Deeply nested JSON should be limited.

This reduces risks from:

* parser exhaustion;
* memory consumption;
* pathological payloads.

---

# 54. Regular Expression Security

User-controlled regular expressions must be avoided unless necessary.

If regex input is supported, the implementation must protect against catastrophic backtracking and excessive CPU consumption.

---

# 55. SSRF Protection

If the backend ever fetches a URL provided by a user, it must validate:

* scheme;
* hostname;
* destination IP;
* private network access;
* redirect targets;
* DNS resolution.

The backend must not allow arbitrary requests to internal infrastructure.

---

# 56. External URL Fetching

User-controlled URLs should not be fetched by the backend unless the feature explicitly requires it.

If required, use an allowlist of supported domains or destinations where practical.

---

# 57. Command Injection

User input must never be passed directly into shell commands.

If system commands are required:

* use fixed executable paths;
* pass arguments as structured arrays;
* validate input;
* avoid shell interpretation.

---

# 58. Path Traversal

All filesystem operations must use generated paths or safe path resolution.

User-controlled:

```text
filename
path
storage key
```

must never directly determine filesystem traversal.

---

# 59. Deserialization Security

The backend must avoid unsafe deserialization of untrusted data.

Only safe, controlled serialization formats should be accepted.

Arbitrary object deserialization is prohibited.

---

# 60. Pickle and Equivalent Formats

Untrusted files or API payloads must never be deserialized using unsafe executable-object formats such as unrestricted Python pickle.

---

# 61. YAML Security

If YAML is accepted, only safe loaders may be used.

Arbitrary object construction from untrusted YAML is prohibited.

---

# 62. XML Security

If XML processing is introduced, the parser must disable unsafe external entity behavior where applicable.

The system must protect against:

* XXE;
* entity expansion;
* resource exhaustion.

---

# 63. File Security

Uploaded files must follow the file-security architecture.

Controls include:

* size limit;
* type validation;
* extension validation;
* content validation;
* malware scanning where required;
* private-by-default access;
* authorization;
* storage isolation.

---

# 64. File Download Security

A file download must validate:

```text
Authentication
+
Business
+
Branch
+
Permission
+
File State
```

A predictable file URL must not make the file publicly accessible.

---

# 65. Signed URL Security

Signed URLs must:

* expire;
* be scoped to one object;
* use minimal permissions;
* not expose storage credentials;
* not be reusable indefinitely.

---

# 66. Security Headers

HTTP responses should use appropriate security headers.

Depending on frontend architecture, these may include:

* Content-Security-Policy;
* X-Content-Type-Options;
* Referrer-Policy;
* Strict-Transport-Security;
* frame protection through CSP/frame-ancestors where appropriate.

Headers must be compatible with the actual frontend deployment.

---

# 67. TLS

Production traffic must use HTTPS/TLS.

Plain HTTP must not be used for sensitive application traffic.

Redirect behavior should be configured at the trusted edge/proxy.

---

# 68. HSTS

HSTS may be enabled in production after confirming that all relevant application domains and subdomains are HTTPS-compatible.

The preload option should not be enabled casually.

---

# 69. CORS

CORS must use an explicit allowlist.

Avoid:

```text
Access-Control-Allow-Origin: *
```

for credentialed authenticated APIs.

Allowed origins must be environment-specific.

---

# 70. CSRF

If authentication uses cookies, CSRF protection must be enabled for state-changing operations.

Possible controls:

* SameSite cookies;
* CSRF token;
* Origin/Referer validation where appropriate.

If the API uses bearer tokens without browser cookies, the CSRF threat model differs, but other browser security controls still apply.

---

# 71. Cookie Security

If cookies are used:

* Secure;
* HttpOnly where appropriate;
* SameSite configured;
* bounded expiration.

Session cookies must not contain sensitive plaintext data.

---

# 72. Error Handling

Security-sensitive errors must not expose internal details.

Do not return:

* SQL statements;
* stack traces;
* filesystem paths;
* storage credentials;
* internal hostnames;
* secret configuration;
* database structure.

---

# 73. Error Response Model

External API errors should use controlled categories such as:

```text id="errsec1"
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
429 Too Many Requests
500 Internal Server Error
503 Service Unavailable
```

Exact API error schema belongs to the API architecture.

---

# 74. 404 vs 403

For resources where existence disclosure is sensitive, the backend may return `404 Not Found` rather than confirming that an unauthorized object exists.

The choice should be consistent for each resource category.

---

# 75. Security Logging

Security logs should capture important events such as:

* authentication failure;
* successful login;
* password reset;
* session revocation;
* device registration;
* device revocation;
* permission changes;
* privilege changes;
* suspicious requests;
* rate-limit events;
* authorization failures;
* offline authorization failure;
* synchronization security failure.

---

# 76. Security Logs vs Business Audit

Security logs and business audit records are separate concepts.

Security logs answer:

> What security event happened?

Business audit answers:

> What business state changed, who changed it, and why?

Both may reference the same request/operation IDs.

---

# 77. Sensitive Logging Restrictions

Never log:

* passwords;
* authentication tokens;
* refresh tokens;
* private keys;
* secret values;
* full payment credentials;
* raw authorization headers;
* full signed URLs containing sensitive credentials.

---

# 78. Identifier Logging

Logs may include:

* request ID;
* operation ID;
* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID

where necessary for investigation.

High-cardinality identifiers should not be used as unrestricted metrics labels.

---

# 79. Audit Integrity

Audit records must be:

* immutable;
* attributable;
* timestamped;
* Business-scoped;
* protected from normal employee modification.

Privileged administrative access to audit storage must itself be controlled and logged.

---

# 80. Security Event Severity

Security events may use:

```text id="sev1"
INFO
WARNING
HIGH
CRITICAL
```

Examples:

```text
Normal login
→ INFO

Repeated failed login
→ WARNING

Suspicious privilege escalation
→ HIGH

Detected compromised device
→ CRITICAL
```

---

# 81. Secrets Management

Secrets must be provided through secure configuration mechanisms.

Examples:

* database credentials;
* JWT/signing keys;
* encryption keys;
* storage credentials;
* SMTP credentials;
* external API credentials.

Secrets must not be hardcoded.

---

# 82. Secret Rotation

Security-sensitive keys and credentials must support rotation.

Rotation should be designed so that active systems can transition without unnecessary downtime.

---

# 83. Signing Key Rotation

Signing keys for:

* tokens;
* offline authorization;
* sensitive signatures

must support controlled rotation.

The system may need to recognize both current and previous keys during a migration window.

---

# 84. Encryption Keys

Encryption keys must not be stored together with encrypted sensitive data in an insecure way.

Key management should rely on established infrastructure where available.

Custom cryptographic key-management schemes should be avoided.

---

# 85. Data Encryption

Sensitive data should be protected according to its sensitivity.

Encryption may be required for:

* passwords through hashing rather than encryption;
* offline local storage;
* sensitive files;
* secrets;
* selected highly sensitive database fields.

Not all normal Business data requires application-level field encryption.

---

# 86. Password Hashing vs Encryption

Passwords must be hashed, not reversibly encrypted.

The application must never need to recover the original password.

---

# 87. Payment Data

The system should minimize storage of sensitive payment information.

Where external payment providers are used, provider tokens or references should be preferred over storing sensitive payment credentials.

---

# 88. Sensitive Employee Data

Employee-sensitive data must be protected by:

* scope;
* permission;
* audit;
* minimal exposure;
* secure storage;
* controlled exports.

---

# 89. Report Security

Reports may contain sensitive Business data.

Report access must validate:

* Business;
* Branch;
* permission;
* report scope;
* employee authority.

An exported XLSX file must inherit the appropriate access and retention rules.

---

# 90. Export Security

Export generation must not allow a user to bypass UI permissions.

The server must revalidate authorization at export request time.

---

# 91. Export File Access

An employee must not access another employee's private export merely by changing an export/file UUID.

The export file must be scoped to its owning Business and access policy.

---

# 92. Background Job Security

Background jobs must use explicit system identities.

A worker must not inherit arbitrary user privileges.

Example:

```text id="jobsec1"
System Job Identity
+
Explicit Business Scope
+
Explicit Operation Type
```

---

# 93. Job Input Validation

Background job payloads are untrusted internal data and must still be validated.

A malicious or corrupted queue message must not result in unrestricted access.

---

# 94. Queue Security

Queues should be protected from unauthorized producers and consumers.

Worker credentials must have minimum required permissions.

---

# 95. Retry Security

Retries must not accidentally bypass:

* authorization;
* subscription state;
* Business lifecycle;
* idempotency;
* concurrency rules.

A retry must revalidate necessary state.

---

# 96. Security and Cache

Cache must never be treated as an authorization bypass.

Security-sensitive cache entries must include relevant identity/version context.

Examples:

```text id="seccache1"
permissions:{employee}:{business}:{branch}:{version}
device:{device}:{version}
entitlement:{business}:{version}
```

---

# 97. Cache Failure

If security-sensitive cache is unavailable:

```text id="seccache2"
Cache Failure
   ↓
Authoritative Validation
```

Not:

```text
Cache Failure
   ↓
Allow
```

---

# 98. Cache Poisoning Protection

Cached values must originate only from trusted server-side sources.

Clients must not be able to directly write authorization or Business configuration cache entries.

---

# 99. Cache Isolation

Cache keys must preserve:

* Business;
* Branch;
* employee/identity where required;
* configuration version.

Cross-scope cache collision must be treated as a security defect.

---

# 100. Database Security

Database access must use:

* strong credentials;
* least privilege;
* encrypted transport where appropriate;
* network restrictions;
* controlled application roles;
* secure backups.

The application database user should not have unnecessary administrative privileges.

---

# 101. Database Least Privilege

The application role should not normally have permissions such as:

* database superuser;
* arbitrary server filesystem access;
* unrestricted administrative configuration.

Migration privileges may use a separate controlled identity.

---

# 102. Migration Security

Database migrations must be reviewed and version-controlled.

Destructive operations require additional scrutiny because they can affect historical integrity.

---

# 103. Database Backup Security

Backups must be:

* access-controlled;
* encrypted where appropriate;
* protected from unauthorized download;
* monitored;
* retained according to policy.

Backup access must be more restricted than ordinary Business access.

---

# 104. Backup Restore Security

Restore operations must be restricted to authorized operators.

Restored environments must not accidentally expose production secrets or public endpoints.

---

# 105. Dependency Security

Dependencies must be:

* version-pinned or constrained appropriately;
* regularly reviewed;
* scanned for known vulnerabilities;
* updated in controlled releases.

Security updates should be prioritized according to severity.

---

# 106. Python Package Security

The backend should use:

* lock files or reproducible dependency resolution;
* vulnerability scanning;
* controlled package sources;
* minimal dependencies.

Unused dependencies should be removed.

---

# 107. Container Security

If containers are used, images should:

* use minimal base images;
* avoid running as root where practical;
* be scanned for vulnerabilities;
* pin important base versions;
* avoid unnecessary OS packages.

---

# 108. Linux Runtime Hardening

Production hosts should use:

* least-privilege service users;
* restricted filesystem permissions;
* firewall/network restrictions;
* automatic security updates where operationally safe;
* SSH hardening;
* monitored system logs.

---

# 109. Reverse Proxy Security

The reverse proxy should provide:

* TLS termination;
* request-size limits;
* connection limits where appropriate;
* security headers;
* trusted proxy handling;
* basic abuse protection.

The application must not blindly trust arbitrary proxy headers.

---

# 110. Trusted Proxy Headers

Headers such as:

```text
X-Forwarded-For
X-Forwarded-Proto
```

must only be trusted from configured trusted proxies.

Clients must not be able to spoof security-relevant source information.

---

# 111. Request IDs

Every request should have a request ID.

The request ID must:

* be unique;
* be propagated through logs;
* not be treated as authentication;
* not be used as a secret.

---

# 112. Operation IDs

Business-changing operations should have an operation UUID where appropriate.

The operation ID supports:

* idempotency;
* tracing;
* synchronization;
* audit;
* incident investigation.

---

# 113. Security and Idempotency

Idempotency records must be protected against cross-Business reuse.

A duplicate request must return the previously established authoritative result where safe.

---

# 114. Concurrency Security

Security-sensitive operations must be protected against race conditions.

Examples:

* simultaneous permission change;
* employee deactivation during operation;
* simultaneous cash correction;
* simultaneous configuration update;
* simultaneous subscription state transition.

---

# 115. TOCTOU Protection

The system must avoid security checks that become invalid before the actual state change.

Example:

```text id="toctou1"
Check Permission
      ↓
State Changes
      ↓
Execute Without Revalidation
```

For sensitive operations, authorization and state validation must be coordinated with the transaction.

---

# 116. Permission Change Concurrency

If an employee's permission is revoked while an operation is being processed, the system must follow a defined transactional policy.

Critical operations must not silently bypass the newly effective restriction.

---

# 117. Employee Deactivation

Employee deactivation must invalidate or restrict:

* future authentication;
* active authorization;
* permission cache;
* device access where applicable;
* offline authorization where supported by synchronization.

Historical actions remain attributable to the employee.

---

# 118. Device Revocation

Device revocation must prevent further trusted-device authorization.

The device must not be able to register itself again without the required online verification.

---

# 119. Trusted Device Registration

New device registration must require online connectivity.

A first-time device must not establish trusted/offline status solely from offline information.

---

# 120. Device Verification

The system may require a verification code or equivalent confirmation for unfamiliar devices.

The verification mechanism must be:

* short-lived;
* single-use;
* rate-limited;
* auditable.

---

# 121. Device Identity

Device UUID identifies a device.

It is not itself an authentication credential.

The server must associate the device with authenticated and authorized identity.

---

# 122. Security and Printer Devices

Printers and local print agents should receive only the permissions required for printing.

A printer failure or compromised print agent must not gain authority over:

* Payments;
* Inventory;
* Cash;
* Employee management.

---

# 123. External Integrations

External providers must use least-privilege credentials.

Integrations should have:

* timeout;
* authentication;
* retry limits;
* request signing where required;
* idempotency;
* audit;
* error isolation.

---

# 124. Integration Secret Isolation

One integration's credentials must not grant access to unrelated integrations.

Secrets should be separately managed.

---

# 125. Webhook Security

If webhooks are introduced, they must validate:

* provider signature;
* timestamp;
* replay protection;
* event ID;
* expected provider;
* expected Business context.

Webhook processing must be idempotent.

---

# 126. Security Notifications

Important security events may trigger notifications.

Examples:

* suspicious login;
* device registration;
* device revocation;
* repeated failed login;
* privilege change;
* security policy violation.

Notifications must not contain secrets.

---

# 127. Security SLOs

Initial production security SLO targets:

| Security capability                           |                                            Target |
| --------------------------------------------- | ------------------------------------------------: |
| Protected API authorization decision          | p95 ≤ 100 ms excluding slow external dependencies |
| Authentication request                        |                    p95 ≤ 500 ms under normal load |
| Authorization cache invalidation              |                                            ≤ 30 s |
| Employee deactivation propagation             |                                     ≤ 30 s online |
| Device revocation propagation                 |                                     ≤ 30 s online |
| Critical security event ingestion             |                                           ≥ 99.9% |
| Security log availability                     |                                   ≥ 99.9% monthly |
| Rate-limit enforcement availability           |                                           ≥ 99.9% |
| Audit event creation for mandatory operations |                                          ≥ 99.99% |
| Duplicate operation rejection                 |                                          ≥ 99.99% |
| Cross-Business access prevention              |                                              100% |
| Cross-Branch unauthorized access prevention   |                                              100% |
| Invalid offline signature rejection           |                                              100% |
| Expired offline authorization rejection       |                                              100% |

Security correctness requirements are absolute even when latency SLOs are degraded.

---

# 128. Security Performance Targets

Security checks should be optimized so that normal POS operations do not experience unnecessary latency.

Initial target:

```text id="secperf1"
Authentication
→ p95 ≤ 500 ms

Normal authorization
→ p95 ≤ 100 ms

Cached authorization lookup
→ p95 ≤ 20 ms

Business / Branch scope validation
→ p95 ≤ 50 ms

Idempotency lookup
→ p95 ≤ 50 ms
```

These are backend targets under normal production conditions and should be validated through load testing.

---

# 129. Security Degradation Policy

If security infrastructure is degraded:

```text id="degrade1"
Security uncertainty
      ↓
Fail Closed
```

Examples:

* unable to validate critical signature;
* unable to establish required authorization;
* unknown device trust;
* unknown subscription state for a modification.

The system should reject the sensitive operation rather than guess.

---

# 130. Availability vs Security

Availability is not a reason to bypass security.

For example:

```text
Redis unavailable
→ PostgreSQL authorization lookup

Authorization service unavailable
→ reject sensitive operation if authoritative validation cannot be established
```

The system may degrade functionality rather than security.

---

# 131. Security Monitoring

Security monitoring should detect:

* authentication anomalies;
* authorization failures;
* privilege escalation;
* Business/Branch traversal attempts;
* abnormal synchronization;
* repeated idempotency conflicts;
* suspicious device behavior;
* excessive file access;
* unusual export activity;
* repeated rate-limit violations.

---

# 132. Security Alerts

Critical alerts may include:

```text id="alertsec1"
Compromised Trusted Device
Privilege Escalation Attempt
Repeated Cross-Business Access Attempts
Invalid Offline Signature
Mass Authentication Failure
Unexpected Admin Activity
Storage Credential Failure
Audit Integrity Failure
```

---

# 133. Incident Response

The system must support controlled response actions:

1. Identify event.
2. Contain affected identity/device.
3. Revoke sessions if required.
4. Revoke trusted device.
5. Disable affected credentials.
6. Preserve logs/audit.
7. Investigate.
8. Recover.
9. Verify.
10. Document incident.

---

# 134. Security Kill Switches

Where operationally justified, administrators may have controlled mechanisms to:

* revoke a device;
* disable an employee;
* disable an integration;
* disable a feature;
* suspend a Business.

These controls must be highly privileged and audited.

---

# 135. Feature Flags and Security

Feature flags must not be used as a replacement for authorization.

A feature flag answers:

> Is this feature enabled?

Permission answers:

> Is this employee allowed to perform it?

Both may be required.

---

# 136. Security Testing

Security testing must include:

### Authentication

* invalid credentials;
* brute force;
* session fixation;
* token expiration;
* revocation.

### Authorization

* privilege escalation;
* Business traversal;
* Branch traversal;
* object-level authorization.

### API

* malformed requests;
* mass assignment;
* rate limits;
* payload limits.

### Files

* path traversal;
* malicious file;
* unauthorized download;
* signed URL expiration.

### Offline

* signature manipulation;
* replay;
* clock rollback;
* expired authorization.

### Synchronization

* duplicate operation;
* invalid Business;
* invalid Branch;
* stale transaction;
* unauthorized operation.

---

# 137. Dependency Scanning

CI should perform automated dependency vulnerability scanning.

High-severity vulnerabilities should block release when the affected dependency is reachable and exploitable in the deployed configuration.

Exceptions must be documented.

---

# 138. Static Analysis

Static analysis should detect where practical:

* unsafe SQL;
* insecure subprocess usage;
* secret leakage;
* dangerous deserialization;
* path traversal;
* unsafe cryptography;
* common Python security issues.

---

# 139. Secret Scanning

CI must detect accidental committed secrets.

Examples:

* API keys;
* passwords;
* private keys;
* storage credentials;
* signing secrets.

Detected secrets must be revoked and rotated, not merely deleted from the latest commit.

---

# 140. Dynamic Security Testing

Staging environments should periodically run automated security tests against:

* authentication;
* authorization;
* API endpoints;
* file endpoints;
* synchronization endpoints.

Production testing must be controlled to avoid disruption.

---

# 141. Penetration Testing

Before major production launch and after major security architecture changes, targeted penetration testing should cover:

* tenant isolation;
* authentication;
* authorization;
* API;
* offline sync;
* file access;
* privilege escalation.

---

# 142. Security Regression Testing

Security tests must remain part of the regression suite.

A feature change must not silently remove:

* scope validation;
* authorization;
* audit;
* idempotency;
* security headers;
* input limits.

---

# 143. Security Code Review

Security-sensitive changes require focused review.

Examples:

* authentication;
* authorization;
* permission model;
* offline authorization;
* cryptography;
* file access;
* payment;
* subscription enforcement;
* Business isolation.

---

# 144. Secure Development Rules

Developers must:

* avoid secrets in source;
* use parameterized queries;
* validate inputs;
* use centralized authorization;
* use secure password hashing;
* avoid unsafe deserialization;
* avoid shell commands where possible;
* use storage abstractions;
* preserve Business/Branch scope;
* add security tests for new boundaries.

---

# 145. Security Documentation

Security-sensitive modules should document:

* trust boundary;
* threat;
* authorization requirement;
* data sensitivity;
* failure behavior;
* audit requirement;
* recovery behavior.

---

# 146. Security and Performance Review

Every major security optimization must evaluate:

* latency;
* CPU;
* database load;
* cache load;
* authorization correctness;
* Business isolation;
* Branch isolation;
* offline behavior.

Security must not be removed simply because it adds measurable cost.

---

# 147. Security and POS

Normal POS operations should avoid unnecessary repeated security challenges.

Recommended:

```text id="possec1"
Login
   ↓
Authenticated Session
   ↓
Fast Authorization
   ↓
POS Operation
```

Additional verification should be reserved for sensitive operations.

Examples:

* large refund;
* permission change;
* device registration;
* security-sensitive configuration.

---

# 148. Sensitive Re-Authentication

The system may require re-authentication or stronger verification for high-risk operations.

Examples:

* changing Owner permissions;
* registering trusted device;
* revoking security controls;
* changing critical Business settings.

Normal Product addition or ordinary order modification should not require repeated authentication.

---

# 149. Security and Cash Operations

Cash operations require strong authorization and concurrency controls.

Examples:

* opening session;
* closing session;
* correction;
* handover;
* reopening under exceptional privilege.

The system must combine authorization with authoritative Cash Session state.

---

# 150. Security and Inventory

Inventory security must prevent:

* unauthorized stock adjustment;
* unauthorized purchase modification;
* unauthorized recipe manipulation;
* negative-stock bypass;
* cross-Branch inventory access.

Final inventory validation remains transactional.

---

# 151. Security and Pricing

Pricing security must prevent:

* unauthorized price change;
* unauthorized Branch override;
* stale configuration overwrite;
* client-provided price manipulation.

The server calculates or validates authoritative pricing.

---

# 152. Security and Orders

Order security must prevent:

* unauthorized order access;
* unauthorized modification;
* duplicate payment;
* duplicate synchronization;
* price manipulation;
* cross-Branch order access.

Historical snapshots remain immutable.

---

# 153. Security and Reports

Reports must be scoped to authorized Business/Branch context.

An employee must not obtain another Business's data by manipulating:

* date;
* Branch UUID;
* report UUID;
* export UUID;
* query parameters.

---

# 154. Security and Audit

Audit events must themselves be protected.

Normal employees must not:

* edit audit records;
* delete audit records;
* rewrite historical audit data.

---

# 155. Security and Data Lifecycle

Business deletion must revoke:

* active sessions;
* device trust;
* offline authorization;
* modification access.

Stale synchronization requests must not resurrect deleted Business state.

---

# 156. Deletion Security

Deletion operations must be:

* authorized;
* explicit;
* auditable;
* idempotent;
* protected from accidental cross-Business execution.

Permanent deletion must not be triggered by a client request without the required lifecycle conditions.

---

# 157. Security and Backups

Backup data must remain protected after live Business deletion.

Backup access must not be available to ordinary Business employees.

Backup restoration must require privileged operational access.

---

# 158. Security and Observability

Security monitoring must not expose secrets.

Metrics should remain low-cardinality.

Logs should be structured.

Sensitive values should be redacted before logging.

---

# 159. Security Performance Budget

Security controls should consume only a bounded portion of normal API latency.

Initial target:

> Authentication and authorization controls should normally contribute no more than 100 ms p95 to an ordinary authenticated request, excluding external infrastructure failures.

For high-frequency POS requests, cached authorization and efficient scope validation should keep the security overhead substantially below this ceiling.

---

# 160. Security Availability Target

The application security subsystem should target:

**99.9% monthly availability**

for normal authentication and authorization infrastructure.

When the security subsystem cannot establish a required security decision, protected operations fail closed.

---

# 161. Security Incident Detection Target

Critical security events should become visible to operational monitoring within:

**60 seconds**

under normal infrastructure conditions.

---

# 162. Revocation Target

Online revocation of:

* employee access;
* trusted device;
* active session

should propagate within:

**30 seconds**

under normal operating conditions.

---

# 163. Audit Security Target

Mandatory audit events for critical business operations should be committed atomically with the corresponding business transaction where required.

Target:

**99.99%+ successful creation for mandatory audit events.**

A critical transaction must not be considered successfully committed if its required atomic audit record cannot be persisted.

---

# 164. Security Failure Recovery

Security failures should be recoverable without weakening controls.

Examples:

```text
Expired Token
→ Re-authenticate

Revoked Device
→ Online Verification

Invalid Offline Authorization
→ Synchronization / Re-registration

Stale Permission
→ Refresh Authorization Context

Rate Limit
→ Wait / Retry According to Policy
```

---

# 165. Security Architecture Guardrails

The implementation must prohibit:

* authorization only in frontend;
* client-controlled Business scope;
* client-controlled Branch authority;
* plaintext passwords;
* hardcoded secrets;
* unrestricted CORS;
* arbitrary SQL;
* unsafe deserialization;
* unrestricted file paths;
* permanent signed URLs;
* cache-based authorization bypass;
* offline self-issued authorization;
* unlimited request sizes;
* unlimited retries;
* silent privilege escalation;
* silent cross-Business access;
* audit deletion by ordinary employees.

---

# 166. Recommended Security Structure

```text id="secstruct"
app/
├── security/
│   ├── authentication/
│   ├── authorization/
│   ├── sessions/
│   ├── tokens/
│   ├── passwords/
│   ├── devices/
│   ├── offline/
│   ├── policies/
│   ├── rate_limit/
│   ├── csrf/
│   └── validation/
│
├── application/
├── domain/
├── infrastructure/
│   ├── crypto/
│   ├── logging/
│   ├── monitoring/
│   ├── storage/
│   └── external/
│
├── synchronization/
├── background/
└── shared/
```

Exact module names may be refined during implementation.

---

# 167. Security Review Checklist

Before production deployment, verify:

### Authentication

* [ ] Passwords are securely hashed.
* [ ] Sessions/tokens expire.
* [ ] Revocation works.
* [ ] Brute-force protection is enabled.

### Authorization

* [ ] Business scope is server-controlled.
* [ ] Branch scope is server-controlled.
* [ ] Object-level authorization exists.
* [ ] Manager authority boundaries are enforced.

### API

* [ ] Input validation exists.
* [ ] Request size limits exist.
* [ ] Pagination is bounded.
* [ ] CORS is restricted.
* [ ] CSRF is handled where applicable.

### Data

* [ ] SQL injection protections exist.
* [ ] Secrets are not stored in source.
* [ ] Sensitive logs are redacted.
* [ ] Backups are protected.

### Files

* [ ] File size limits exist.
* [ ] MIME/type validation exists.
* [ ] Path traversal is prevented.
* [ ] Signed URLs expire.
* [ ] Business/Branch authorization exists.

### Offline

* [ ] Device trust is validated.
* [ ] Offline authorization is signed.
* [ ] Offline authorization expires.
* [ ] Replay protection exists.
* [ ] Clock rollback detection exists.

### Operations

* [ ] Security monitoring exists.
* [ ] Critical alerts exist.
* [ ] Dependency scanning exists.
* [ ] Secret scanning exists.
* [ ] Security regression tests exist.

---

# 168. System Invariants

The following invariants apply to Backend Security Hardening and Application Security:

1. Authentication is required for protected operations.
2. Authorization is performed server-side.
3. Security defaults to deny.
4. Unknown permissions result in denial.
5. Client-provided Business scope is never authoritative.
6. Client-provided Branch scope is never authoritative.
7. Every protected object is checked against authorized scope.
8. Cross-Business access is prohibited.
9. Unauthorized cross-Branch access is prohibited.
10. Object UUID alone never grants authorization.
11. Super Admin and Business employee privilege boundaries remain separate.
12. Managers cannot grant permissions beyond their authority.
13. Employee status affects authorization.
14. Subscription entitlement affects modification authorization.
15. READ_ONLY Business state blocks prohibited modifications.
16. Offline authorization cannot bypass subscription restrictions.
17. Trusted device status is not equivalent to employee permission.
18. Device UUID alone is not authentication.
19. First-time device trust requires online verification.
20. Offline authorization is cryptographically protected.
21. Offline authorization is time-bounded.
22. Offline authorization is device-bound.
23. Offline authorization is Business-bound.
24. Offline authorization cannot be self-issued by a client.
25. Offline operations require replay protection.
26. Operation UUIDs must be unique within their security scope.
27. Duplicate operations must not create duplicate financial effects.
28. Synchronization does not grant additional permissions.
29. Stale synchronization cannot resurrect deleted Business state.
30. Client timestamps are not fully trusted.
31. Clock rollback must be detectable.
32. Passwords are never stored in plaintext.
33. Passwords are never logged.
34. Password reset tokens are short-lived.
35. Password reset tokens are single-use.
36. Authentication endpoints are rate-limited.
37. Brute-force protection is enabled.
38. Sessions are revocable.
39. Tokens are time-bounded.
40. Sensitive token claims are minimized.
41. Secrets are never hardcoded.
42. Secrets are never logged.
43. Security-sensitive keys support controlled rotation.
44. TLS protects production traffic.
45. CORS is explicitly controlled.
46. CSRF protection is used where applicable.
47. Security headers are configured appropriately.
48. Trusted proxy headers are accepted only from configured proxies.
49. SQL queries use parameterization.
50. User-controlled SQL fragments are prohibited.
51. Dynamic sorting uses an allowlist.
52. Request body sizes are bounded.
53. Pagination is bounded.
54. JSON nesting is bounded where necessary.
55. Mass assignment is prohibited.
56. Protected fields cannot be changed through arbitrary JSON fields.
57. Arbitrary object deserialization is prohibited.
58. Unsafe pickle-style deserialization of untrusted data is prohibited.
59. XML processing must prevent unsafe external entities where applicable.
60. User-controlled URLs cannot trigger unrestricted server-side requests.
61. SSRF protections apply where backend URL fetching exists.
62. Shell command execution is minimized.
63. User input is never directly interpreted as shell commands.
64. File paths are application-generated.
65. Path traversal is prohibited.
66. Uploaded files are validated.
67. Sensitive files are private by default.
68. Signed URLs are short-lived.
69. Signed URLs do not replace authorization.
70. File access respects Business scope.
71. File access respects Branch scope.
72. File access respects employee status.
73. File access respects permissions.
74. Cache cannot bypass authorization.
75. Cache cannot bypass Business isolation.
76. Cache cannot bypass Branch isolation.
77. Security-sensitive cache entries have bounded lifetime.
78. Security cache invalidation occurs after relevant security changes.
79. Cache failure results in authoritative validation or denial, not automatic authorization.
80. Redis failure cannot grant access.
81. Security logs do not contain credentials.
82. Security logs are separate from business audit where appropriate.
83. Mandatory business audit events remain immutable.
84. Critical audit records are atomically committed where required.
85. Background jobs use explicit system identities.
86. Background jobs do not inherit arbitrary user privileges.
87. Queue messages are validated.
88. Retries cannot bypass authorization.
89. Retries cannot bypass lifecycle restrictions.
90. Retries cannot bypass idempotency.
91. Database credentials use least privilege.
92. Migration privileges are controlled separately where appropriate.
93. Backups are access-controlled.
94. Backup restoration is restricted.
95. Dependency vulnerabilities are monitored.
96. Security-sensitive dependencies are reviewed.
97. CI performs secret scanning.
98. CI performs security/dependency checks.
99. Security-sensitive code receives focused review.
100. Security regressions are tested.
101. Security failures fail closed.
102. Security uncertainty never results in silent authorization.
103. Security monitoring is observable.
104. Critical security events are detected within the defined target.
105. Employee deactivation propagates within the defined target.
106. Device revocation propagates within the defined target.
107. Authentication and authorization performance remains within defined targets under normal load.
108. Security controls must not unnecessarily block normal POS operations.
109. Sensitive operations may require stronger authentication.
110. Ordinary POS operations should not require unnecessary repeated verification.
111. Payment security does not depend on client-provided financial state.
112. Inventory security does not depend on cached stock state.
113. Pricing security does not depend on client-provided price.
114. Historical data cannot be rewritten to simplify security processing.
115. Audit records cannot be silently deleted.
116. Business deletion revokes active access.
117. Device trust is revoked when required.
118. Security events are attributable to an actor or system identity.
119. Security metrics remain low-cardinality.
120. Security logs preserve request and operation correlation.
121. Incident response can revoke sessions.
122. Incident response can revoke devices.
123. Incident response can disable affected integrations.
124. Critical security controls remain operational during partial infrastructure failure.
125. Security architecture remains compatible with horizontal backend scaling.
126. Security architecture remains compatible with future object storage.
127. Security architecture remains compatible with offline synchronization.
128. Security architecture remains compatible with future external integrations.
129. Performance optimization must not weaken security.
130. Simplicity is preferred when equivalent security can be achieved with fewer mechanisms.
131. Security correctness has priority over availability when authoritative security state cannot be established.

---

# 169. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend

* `docs/06_Backend/01_Backend_Architecture.md`
* `docs/06_Backend/02_Backend_Project_Structure.md`
* `docs/06_Backend/06_Authentication_and_Authorization.md`
* `docs/06_Backend/07_Transaction_Management.md`
* `docs/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/06_Backend/11_Configuration_and_Environment_Management.md`
* `docs/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/06_Backend/15_Backend_File_Storage_and_Document_Management.md`

---

# 170. Status

**Backend Architecture Document:** Completed.

**Document Status:** Accepted.

**Current Document:** `16_Backend_Security_Hardening_and_Application_Security.md`

**Next Document:** `17_Backend_Testing_and_Quality_Assurance_Architecture.md`

