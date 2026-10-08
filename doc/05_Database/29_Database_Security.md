# Database Security

**Document ID:** DB-29
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

---

## 1. Purpose

This document defines the database security requirements for FastFood ERP.

The database is a critical system-of-record component and stores business, branch, employee, order, payment, cash, inventory, payroll, audit, configuration, synchronization and historical data.

The security model must protect:

* confidentiality;
* tenant isolation;
* data integrity;
* historical integrity;
* availability;
* authentication context;
* authorization boundaries;
* backup and recovery data;
* offline synchronization state;
* audit records.

Database security must not introduce unnecessary latency into normal POS operations.

---

## 2. Scope

This document covers:

* PostgreSQL security;
* database access control;
* application database credentials;
* connection security;
* tenant isolation;
* Business and Branch boundaries;
* database roles;
* least privilege;
* schema security;
* row-level security considerations;
* encryption;
* secret management;
* sensitive data protection;
* audit protection;
* backup security;
* migration security;
* offline synchronization security;
* database monitoring;
* administrative access;
* security incident handling;
* data lifecycle and deletion;
* security invariants.

---

## 3. Security Principles

The database security model follows these principles:

1. Least privilege.
2. Defense in depth.
3. Business isolation.
4. Branch scope enforcement.
5. Server authority.
6. Historical integrity.
7. Explicit authorization.
8. Secure defaults.
9. No trust based solely on client-provided identifiers.
10. No trust based solely on trusted-device status.
11. No direct application access to unrestricted database administration.
12. No silent cross-Business access.
13. No uncontrolled destructive deletion.
14. Security controls must remain compatible with offline operation.
15. Core POS transactions must remain fast.

---

## 4. PostgreSQL as the Authoritative Database

PostgreSQL is the authoritative transactional database for the initial system.

The application must treat PostgreSQL as the source of truth for:

* Orders;
* Order Items;
* Payments;
* Refunds;
* Cash Sessions;
* Inventory Transactions;
* Products;
* Recipes;
* Menu configuration;
* Employees;
* Permissions;
* Payroll;
* Audit Events;
* Configuration Versions;
* Synchronization state;
* Report Versions;
* Business lifecycle state.

Redis, local device databases, caches, generated XLSX files and client state are not authoritative.

---

## 5. Database Trust Boundary

The database must not trust arbitrary values supplied by clients.

The following must be validated by the application/server:

* Business UUID;
* Branch UUID;
* Employee UUID;
* Device UUID;
* Cash Register UUID;
* Cash Session UUID;
* Order UUID;
* Payment UUID;
* configuration version;
* synchronization event UUID;
* idempotency UUID.

Client-provided identifiers must be treated as references requiring authorization validation.

---

## 6. Database Access Architecture

The normal application flow is:

```text
Client
   ↓
API / Application Layer
   ↓
Authentication
   ↓
Authorization
   ↓
Service / Use Case
   ↓
Repository / Data Access Layer
   ↓
PostgreSQL
```

The client must never connect directly to PostgreSQL.

Database credentials must never be embedded in:

* frontend code;
* browser JavaScript;
* mobile client;
* POS configuration exposed to ordinary employees;
* public repositories;
* logs.

---

## 7. Database Roles

Database access should use separate PostgreSQL roles according to operational responsibility.

Recommended logical roles include:

```text
application_runtime
migration_operator
backup_operator
reporting_reader
database_admin
```

Exact PostgreSQL role names may differ by deployment.

Roles must not share unnecessary privileges.

---

## 8. Application Runtime Role

The application runtime role is used by the normal FastFood ERP application.

It should have only the privileges required to:

* read application data;
* insert application data;
* update permitted application data;
* execute required database functions;
* create required transaction records.

It must not normally have:

* PostgreSQL superuser privileges;
* database creation privileges;
* role creation privileges;
* arbitrary extension installation privileges;
* unrestricted access to system catalogs beyond required operation.

---

## 9. Migration Role

Database schema migrations require a more privileged database role than normal application execution.

The migration role may perform:

* table creation;
* column changes;
* index creation;
* constraint changes;
* database functions required by migrations;
* schema changes.

The migration role must not be used by normal application requests.

---

## 10. Backup Role

Backup operations must use a dedicated backup identity where practical.

The backup identity must have only the permissions required to perform backup operations.

Backup credentials must not be included in application runtime configuration.

---

## 11. Database Administrator

Database administrators may have elevated PostgreSQL privileges.

Administrative access must be:

* authenticated;
* authorized;
* restricted;
* auditable;
* preferably time-bounded where infrastructure supports it.

Database administrator credentials must never be used by the application runtime.

---

## 12. Superuser Restrictions

PostgreSQL superuser access must be restricted to infrastructure/database administration.

Application code must never require superuser privileges for normal operation.

Production superuser credentials must not be stored in:

* source code;
* `.env` files committed to Git;
* Docker images;
* frontend applications;
* CI logs;
* ordinary employee-accessible systems.

---

## 13. Credential Management

Database credentials must be stored using a secure secret-management mechanism appropriate to the deployment environment.

At minimum:

* credentials are external to source code;
* credentials are not logged;
* credentials are not returned by APIs;
* credentials can be rotated;
* production credentials are separate from development credentials.

---

## 14. Credential Rotation

Database credentials must support controlled rotation.

Credential rotation must not require storing the new credential in application source code.

Where practical:

```text
Old Credential
      ↓
New Credential Introduced
      ↓
Application Connections Rotated
      ↓
Old Credential Revoked
```

Rotation must be planned to avoid unnecessary POS downtime.

---

## 15. Connection Security

Application-to-database connections must use encrypted transport in production environments.

TLS should be used where the database is accessed over a network boundary.

The application must validate the expected database endpoint and certificate configuration.

Unencrypted remote PostgreSQL access is prohibited for production traffic.

---

## 16. Database Network Isolation

PostgreSQL should not be publicly exposed to the Internet.

Recommended architecture:

```text
Internet
   ↓
Application/API
   ↓
Private Network
   ↓
PostgreSQL
```

Firewall/security-group rules must restrict database access to approved application and administrative sources.

---

## 17. PostgreSQL Port Exposure

The PostgreSQL port must not be opened broadly to:

```text
0.0.0.0/0
```

unless a specific infrastructure design explicitly requires it and additional network controls protect access.

The preferred configuration is private network access.

---

## 18. Database Host Hardening

The database host must follow the deployment security baseline.

Controls should include:

* operating system security updates;
* restricted SSH access;
* firewall;
* minimal installed services;
* controlled administrative users;
* secure filesystem permissions;
* monitoring;
* time synchronization.

Database security depends on host security and must not assume PostgreSQL alone is sufficient.

---

## 19. Schema Ownership

Database objects should have controlled ownership.

Application runtime users should not automatically own all database objects.

Where practical:

```text
Schema Owner
    ↓
Migration Role
    ↓
Application Runtime Role
```

This prevents the application from freely altering its own security boundary.

---

## 20. Public Schema Restrictions

The PostgreSQL `public` schema must not be treated as an unrestricted application area.

Application schemas should be explicitly configured.

Unnecessary object creation privileges must be removed from runtime roles.

---

## 21. Extension Security

PostgreSQL extensions must be explicitly approved.

Only required extensions should be enabled.

Installing or changing extensions must require administrative or migration-level authorization.

Unapproved extensions must not be enabled merely for convenience.

---

## 22. Multi-Tenant Security

FastFood ERP is a multi-tenant SaaS system.

The primary tenant boundary is:

```text
Business
   ↓
Branch
   ↓
Business-owned operational data
```

A user from Business A must never access Business B data.

---

## 23. Business UUID Isolation

Business-owned records must contain or be traceable to a stable Business UUID where appropriate.

The Business UUID:

* is globally unique;
* is never reused;
* remains stable during the Business lifecycle;
* identifies the tenant boundary.

Business UUID must not be treated as a secret.

Knowing a Business UUID does not grant access.

---

## 24. Cross-Business References

Cross-Business references are prohibited unless explicitly defined as platform-level relationships.

Examples of prohibited relationships:

```text
Business A Order → Business B Product
Business A Payment → Business B Order
Business A Employee → Business B Branch
Business A Inventory → Business B Warehouse
```

Database constraints and application validation should prevent such relationships.

---

## 25. Branch Isolation

Branch scope is a secondary security boundary inside a Business.

A user may have:

* one Branch;
* multiple Branches;
* all-Branch authority.

The database access layer must enforce the effective Branch scope.

---

## 26. Branch Scope Validation

A request containing:

```text
business_uuid
branch_uuid
employee_uuid
```

must validate that:

```text
Employee belongs to Business
AND
Employee is authorized for Branch
AND
Branch belongs to Business
```

A matching UUID alone is insufficient.

---

## 27. Permission Does Not Cross Tenant Boundaries

A permission granted inside Business A cannot authorize access to Business B.

Even an Owner-level permission is limited to the relevant Business.

Super Admin is a separate platform-level authority and must not be implemented as an ordinary Business Owner.

---

## 28. Repository-Level Isolation

Repositories/data-access methods must require tenant context where appropriate.

Unsafe patterns such as:

```text
get_order(order_id)
```

should not be used for tenant-sensitive operations without additional authorization context.

Preferred logical behavior:

```text
get_order(
    business_uuid,
    branch_scope,
    order_uuid
)
```

The exact implementation may differ, but tenant context must be enforced.

---

## 29. Defense Against IDOR

The application must protect against Insecure Direct Object Reference (IDOR).

Changing:

```text
/order/UUID-A
```

to:

```text
/order/UUID-B
```

must not expose another Business's Order.

Authorization must be evaluated against the authenticated actor and tenant context.

---

## 30. UUID Security

UUIDs provide identity uniqueness but do not provide authorization.

The system must never use:

```text
UUID possession = permission
```

UUID validation and authorization remain separate operations.

---

## 31. Database-Level Tenant Guardrails

Application-level tenant filtering is mandatory.

Additional database-level guardrails should be used where practical.

Possible mechanisms include:

* foreign keys;
* composite foreign keys;
* check constraints;
* unique constraints;
* restricted views;
* controlled database functions;
* Row-Level Security where appropriate.

---

## 32. Row-Level Security

PostgreSQL Row-Level Security (RLS) may be used as an additional defense layer for highly sensitive tenant-scoped tables.

RLS must not be introduced blindly.

If enabled, the system must define:

* authenticated database/session tenant context;
* Business scope;
* Branch scope where required;
* administrative bypass behavior;
* migration behavior;
* background-job behavior;
* reporting behavior;
* connection-pool context reset.

Connection pooling must never allow tenant context from one request to leak into another request.

---

## 33. Connection Pool Tenant Context

If tenant context is stored in PostgreSQL session variables or similar mechanisms, the context must be explicitly set and reset for every request/transaction.

A pooled connection must never retain:

```text
Business A
```

context when reused for:

```text
Business B
```

This is a critical security invariant.

---

## 34. Background Jobs

Background jobs must carry explicit Business context where the operation is tenant-scoped.

A background worker must not assume that a previous task's tenant context is still valid.

Each job should validate:

* Business lifecycle;
* Business UUID;
* Branch UUID where applicable;
* authorization context;
* relevant entity ownership.

---

## 35. Report Access

Reports must enforce the same tenant and Branch security rules as operational data.

Generating a report must not bypass Business isolation.

A report generated for Business A must not contain Business B records.

---

## 36. XLSX Export Security

XLSX exports are data-exfiltration boundaries.

Export operations must validate:

* authenticated employee;
* Business;
* Branch scope;
* permission;
* subscription entitlement;
* requested period;
* report scope.

Generated files must not be treated as public files.

---

## 37. Sensitive Data Classification

The system should classify database data according to sensitivity.

Examples:

### High sensitivity

* authentication-related secrets;
* password hashes;
* trusted-device credentials;
* security tokens;
* payroll information;
* financial transaction information;
* audit data;
* synchronization authorization data.

### Business-sensitive

* inventory;
* recipes;
* pricing;
* employee records;
* operational reports.

### Lower sensitivity

* non-sensitive product descriptions;
* public-facing menu metadata.

Classification must guide access, logging and export behavior.

---

## 38. Password Storage

Passwords must never be stored in plaintext.

The database should store only a strong password hash generated using an approved password hashing algorithm.

Recommended algorithms include modern memory-hard password hashing mechanisms such as:

* Argon2id;
* an approved equivalent supported by the authentication stack.

The exact parameters must be centrally configurable and reviewed.

---

## 39. Password Hash Protection

Password hashes must not be returned through normal APIs.

They must not appear in:

* application logs;
* audit payloads;
* reports;
* XLSX exports;
* error messages.

---

## 40. Authentication Secrets

Authentication secrets must be separated from ordinary business data where practical.

Examples include:

* refresh tokens;
* session secrets;
* device credentials;
* signing keys.

Raw secret values must not be stored in audit records.

---

## 41. Trusted Device Data

Trusted-device records must not themselves grant unrestricted access.

A trusted device establishes that the device has been previously approved.

Every operation must still validate:

```text
Employee
+
Business
+
Branch
+
Permission
+
Device
+
Subscription
+
Operation State
```

---

## 42. Offline Authorization Security

Offline authorization is time-bounded and signed.

The database must store sufficient metadata to validate:

* device;
* Business;
* Branch scope;
* authorization version;
* issued time;
* expiry time;
* revocation state;
* authorization generation.

Offline authorization must not be permanent.

---

## 43. Offline Authorization Revocation

When a trusted device is revoked, the server must prevent new synchronization from that device.

Previously created offline events must still undergo normal server-side validation.

Device revocation must not automatically imply deletion of historical transactions.

---

## 44. Synchronization Security

Synchronization requests must validate:

* Device UUID;
* Business UUID;
* Branch scope;
* event UUID;
* event type;
* authorization state;
* Business lifecycle;
* schema/version compatibility;
* idempotency state;
* event dependencies.

---

## 45. Stale Offline Events

A restored or current server state must not accept stale offline events solely because they contain valid UUIDs.

Events must be validated against:

* current Business lifecycle;
* current synchronization generation;
* entity state;
* configuration version;
* authorization;
* conflict rules.

---

## 46. Recovery Generation

Database recovery may restore the system to an earlier state.

After disaster recovery, the system may need a new recovery/synchronization generation.

Example:

```text
Generation 41
    ↓
Database failure
    ↓
PITR restore
    ↓
Generation 42
```

Clients must recognize that the server state has entered a new recovery generation.

---

## 47. Preventing Replay After Recovery

Offline events that were already committed before the recovery point must not be duplicated after clients reconnect.

Idempotency records must therefore be included in database backups.

Recovery validation must verify synchronization and idempotency state.

---

## 48. Encryption at Rest

Database storage should use encryption at rest where supported by the deployment environment.

This may be implemented at:

* disk level;
* volume level;
* managed database storage level.

Database encryption at rest does not replace access control.

---

## 49. Backup Encryption

Database backups must be encrypted.

Backup encryption keys must be managed separately from ordinary backup storage.

A stolen backup file must not be sufficient to obtain plaintext business data.

---

## 50. Key Management

Encryption keys must be managed through a controlled secret/key-management process.

Keys should support:

* rotation;
* access control;
* versioning;
* revocation;
* recovery procedures.

Losing encryption keys can make backups unrecoverable, so key recovery must be part of disaster recovery planning.

---

## 51. Key Separation

Database encryption keys, backup encryption keys and application secrets should not all depend on one uncontrolled secret.

Compromise of one credential should not automatically compromise every security layer.

---

## 52. Encryption in Transit

The following network paths should use encrypted transport where applicable:

```text
Application → PostgreSQL
Application → Backup Storage
Database Administration → PostgreSQL
Worker → PostgreSQL
Synchronization Client → API
```

---

## 53. Audit Data Protection

Audit records are security-sensitive.

Audit records must be:

* immutable;
* protected from ordinary modification;
* access-controlled;
* backed up;
* attributable;
* searchable by authorized personnel.

Ordinary application users must not be able to delete audit records.

---

## 54. Audit Tampering Prevention

The application must not allow a user to:

* rewrite old audit events;
* delete audit events;
* alter actor identity;
* alter timestamps;
* change historical old/new values.

Corrections create new events.

---

## 55. Database Audit of Administrative Actions

Important database administrative actions should be logged at the infrastructure/database level where practical.

Examples:

* privileged login;
* schema modification;
* role modification;
* permission changes;
* backup operation;
* restore operation;
* security configuration change.

---

## 56. Backup Security

Backups are equivalent to copies of production data for security purposes.

Backup access must therefore follow strict access control.

Backups must be:

* encrypted;
* access-controlled;
* integrity-verified;
* retained according to policy;
* monitored;
* stored separately from the primary database host.

---

## 57. Backup Storage Isolation

Backups should not rely exclusively on the same host/storage as the production database.

Preferred model:

```text
Production PostgreSQL
        ↓
Backup Process
        ↓
Separate Backup Storage
        ↓
Optional Off-Site / Object Storage
```

---

## 58. Backup Credentials

Backup storage credentials must be separate from database application credentials.

Compromise of the application runtime account must not automatically provide unrestricted backup deletion privileges.

---

## 59. Backup Deletion Protection

Where infrastructure supports it, critical backups should use:

* immutable retention;
* object lock;
* WORM storage;
* delayed deletion;
* separate administrative approval.

This reduces the impact of ransomware or compromised administrative credentials.

---

## 60. Backup and Tenant Deletion

Deleting a Business from live production data does not necessarily erase its data from every existing backup immediately.

Backup retention is a separate lifecycle.

Therefore:

```text
Live Data Deletion
        ≠
Immediate Historical Backup Erasure
```

Backup retention and legal/privacy requirements must be coordinated.

---

## 61. Data Lifecycle Security

Business lifecycle states include:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

Database operations must respect the current lifecycle state.

---

## 62. READ_ONLY Security

When a Business becomes READ_ONLY:

* modifying business operations are blocked;
* historical data remains accessible according to permissions;
* reports remain available where permitted;
* exports remain available where permitted;
* offline clients must not bypass the restriction.

Database access must not allow the frontend to circumvent this rule.

---

## 63. DELETED Business Protection

A deleted Business must not become accidentally active through:

* stale offline events;
* synchronization retries;
* restored client state;
* old configuration;
* cached permissions;
* duplicate requests.

---

## 64. Business UUID Reuse

Business UUIDs must never be reused.

This prevents old references, backups, logs or offline events from accidentally becoming associated with a different Business.

---

## 65. Soft Deletion

Where historical integrity requires preservation, records should be archived/deactivated rather than physically deleted.

Examples:

* Products;
* Recipes;
* Set configurations;
* Employees;
* Orders;
* Payments;
* Cash Sessions;
* Audit Events.

Physical deletion must be restricted to data explicitly approved for lifecycle deletion.

---

## 66. Cascading Deletes

Business deletion must not rely on uncontrolled database-wide:

```text
ON DELETE CASCADE
```

for important historical domains.

Deletion must follow an explicit lifecycle process.

---

## 67. Database Migration Security

Schema migrations are privileged operations.

Every production migration must:

* be version-controlled;
* be reviewed;
* have a known migration identifier;
* be tested;
* consider rollback/recovery;
* have an appropriate backup/recovery point.

---

## 68. Destructive Migration Protection

Before destructive migrations such as:

* dropping columns;
* dropping tables;
* changing data meaning;
* irreversible transformations;

the system must have an appropriate recovery strategy.

A migration must not rely solely on an application-level rollback.

---

## 69. Expand/Contract Security

Schema changes should preferably follow:

```text
Expand
   ↓
Deploy Compatible Code
   ↓
Migrate Data
   ↓
Validate
   ↓
Contract
```

This reduces the risk of incompatible application/database states.

---

## 70. Migration Access Separation

Normal application credentials must not be able to perform arbitrary schema migrations.

Deployment systems should use dedicated migration credentials.

---

## 71. SQL Injection Protection

Application database access must use parameterized queries or ORM-generated parameter binding.

User input must never be concatenated directly into SQL.

Unsafe pattern:

```text
SELECT * FROM orders WHERE id = ' + user_input
```

must not be used.

---

## 72. Dynamic SQL

Dynamic SQL must be restricted to cases where it is necessary.

Identifiers used in dynamic SQL must be validated against an allowlist.

Values must use parameter binding.

---

## 73. ORM Security

SQLAlchemy usage must follow secure query construction.

The ORM does not automatically guarantee:

* tenant isolation;
* authorization;
* safe dynamic identifiers;
* correct Business scope.

These remain application responsibilities.

---

## 74. Database Function Security

Database functions must have controlled privileges.

Functions that perform privileged operations must validate required context where necessary.

Security-sensitive functions should not expose unrestricted dynamic SQL.

---

## 75. Search and Filtering

Search functionality must preserve tenant and Branch scope.

For example:

```text
Search Orders
```

must never become:

```text
Search All Orders in Database
```

unless the authenticated actor has explicit platform-level authority.

---

## 76. Error Message Security

Database errors must not expose sensitive internal details to ordinary users.

User-facing errors should not reveal:

* database passwords;
* connection strings;
* SQL statements containing secrets;
* internal filesystem paths;
* unrestricted schema details;
* PostgreSQL credentials.

Detailed errors may be logged securely for authorized operators.

---

## 77. Logging Security

Application/database logs must avoid sensitive data.

Do not log:

* passwords;
* raw authentication tokens;
* private signing keys;
* database credentials;
* complete sensitive payroll data;
* unnecessary payment details.

Logs must also preserve enough context for incident investigation.

---

## 78. Database Connection Strings

Connection strings containing credentials must never be written to ordinary application logs.

If connection configuration is displayed diagnostically, credentials must be redacted.

---

## 79. Payment Data

The ERP stores payment transaction information required by the business.

The database must not store unnecessary sensitive external payment credentials.

External card-processing integration is outside the current scope.

Only required payment metadata should be stored.

---

## 80. Payroll Security

Payroll information is restricted business-sensitive data.

Access must require appropriate:

* Business scope;
* Branch scope;
* employee permission;
* role;
* subscription entitlement.

Payroll data must not appear in unrelated reports or exports.

---

## 81. Recipe Security

Recipes may contain commercially sensitive information.

Recipe visibility may therefore be permission-controlled.

Database access must preserve the same permission model used by the application.

Recipe authorization must not be bypassed through direct entity lookup.

---

## 82. Pricing Security

Price configuration changes are security-sensitive.

Price modifications must validate:

* Business;
* Branch;
* Employee;
* permission;
* configuration version;
* subscription entitlement;
* effective state.

---

## 83. Configuration Concurrency Security

Important configuration changes must use optimistic concurrency/version validation.

If an employee updates stale configuration:

```text
Current Version = 8
Client Version = 7
```

the update must be rejected.

Silent last-write-wins behavior is prohibited for important business configuration.

---

## 84. Idempotency Security

Important transaction-changing operations must use operation UUIDs.

Examples:

* Order creation;
* Payment;
* Refund;
* Inventory adjustment;
* Configuration change;
* synchronization event.

Repeated requests must not create duplicate financial or inventory effects.

---

## 85. Idempotency Records

Idempotency records are security and integrity data.

They must be:

* persistent;
* transactionally consistent;
* backed up;
* tenant-scoped;
* protected from unauthorized deletion.

---

## 86. Transaction Atomicity

Security validation and core business changes must occur within the appropriate transaction boundary.

For critical operations:

```text
Validate
   ↓
Authorize
   ↓
Change Core State
   ↓
Persist Audit / Required State
   ↓
Commit
```

A partially committed financial operation must not result from an authorization failure.

---

## 87. Authorization Before Mutation

The system must validate authorization before performing protected database mutations.

Examples:

* price change;
* refund;
* inventory correction;
* payroll modification;
* permission modification;
* configuration change.

---

## 88. Server-Side Authorization

Frontend permission checks are usability controls only.

The server must perform the authoritative authorization check.

A hidden UI button must never be considered a security boundary.

---

## 89. Employee Deactivation

When an employee becomes inactive:

* new protected operations must be rejected;
* new authentication must be blocked;
* new configuration changes must be blocked;
* historical records remain attributable to the employee.

Existing historical transactions must not be rewritten.

---

## 90. Permission Changes

Permission changes must be effective according to the system's configuration rules.

Cached permission state must not remain valid indefinitely.

Security-sensitive permission changes should invalidate relevant cached authorization state.

---

## 91. Device Deactivation

A revoked device must not create new authorized synchronization events.

The server remains authoritative.

Historical events from the device remain part of history unless lifecycle rules explicitly remove them.

---

## 92. Session Security

Database connections and application sessions must have controlled lifetimes.

Connection pools must:

* limit maximum connections;
* recycle stale connections;
* prevent tenant context leakage;
* handle database failures safely.

---

## 93. Connection Pool Isolation

A connection returned to the pool must not retain:

* Business context;
* Branch context;
* temporary authorization context;
* security-related session variables.

Transaction-scoped state should be preferred where practical.

---

## 94. Database Lock Security

Security checks must not introduce uncontrolled long-running locks.

Core POS transactions should use targeted locking only where required.

Long-running administrative operations must not unnecessarily block:

* Order creation;
* Payment;
* Cash Session operations;
* Inventory deduction.

---

## 95. Denial of Service Protection

Database resources must be protected against excessive application requests.

Controls may include:

* API rate limits;
* connection pool limits;
* query timeouts;
* pagination;
* maximum export period;
* bounded background jobs.

---

## 96. Query Timeout

Queries that can accidentally run indefinitely should have appropriate timeout controls.

However, timeout values must be selected carefully so normal POS operations are not interrupted.

---

## 97. Export Resource Protection

Large exports must not consume all database resources.

Exports should:

* validate maximum allowed period;
* use asynchronous processing where appropriate;
* use efficient queries;
* avoid unnecessary locks;
* preserve tenant scope.

---

## 98. Reporting Isolation

Heavy reports should not interfere with core transactional operations.

Where required:

* asynchronous generation;
* optimized indexes;
* controlled transaction isolation;
* future read replicas

may be used.

---

## 99. Security and POS Performance

Database security controls must not make routine POS operations unnecessarily expensive.

Security checks should prefer:

* indexed Business/Branch lookups;
* efficient permission checks;
* cached non-authoritative metadata;
* short transactions;
* targeted locks.

---

## 100. Redis Security

Redis is not authoritative for database security.

Cached permissions or configuration must have expiration/invalidation rules.

A Redis compromise must not grant permanent database access.

---

## 101. Cache Invalidation

When security-sensitive state changes:

* employee deactivation;
* permission changes;
* device revocation;
* subscription restriction;
* Business lifecycle transition;

relevant cached authorization state must be invalidated.

---

## 102. Database Security Monitoring

The system should monitor:

* failed database connections;
* abnormal connection volume;
* privileged logins;
* failed authorization patterns;
* repeated cross-tenant access attempts;
* unusual export activity;
* backup failures;
* restore operations;
* migration execution;
* schema changes.

---

## 103. Cross-Tenant Access Detection

Repeated attempts to access another Business's identifiers may indicate:

* programming error;
* malicious behavior;
* compromised credentials.

Such events should be observable and, where appropriate, trigger security alerts.

---

## 104. Administrative Access Audit

Administrative database actions should be attributable to a specific administrator where infrastructure permits.

The system should preserve:

* administrator identity;
* timestamp;
* action;
* target;
* result;
* source;
* relevant reason/change ticket where applicable.

---

## 105. Security Incident Response

A suspected database compromise must follow a controlled incident process.

Initial actions:

1. Detect.
2. Contain.
3. Preserve evidence.
4. Revoke compromised credentials.
5. Assess affected scope.
6. Verify database integrity.
7. Restore or repair if required.
8. Rotate affected secrets.
9. Reconcile offline devices.
10. Review audit history.
11. Document the incident.

---

## 106. Compromised Application Credential

If an application database credential is compromised:

* revoke or rotate it;
* restrict database access;
* inspect database audit/logs;
* determine affected time window;
* identify possible mutations;
* verify audit/history;
* verify idempotency state;
* inspect Business/Branch boundaries;
* restore or repair only when necessary.

---

## 107. Compromised Backup Credential

If backup credentials are compromised:

* revoke them;
* protect existing backups;
* verify backup integrity;
* rotate encryption/access keys where required;
* inspect deletion attempts;
* create a clean backup;
* review access logs.

---

## 108. Ransomware Protection

Database backups must remain recoverable even if the production environment is compromised.

At least one backup copy should be protected from ordinary production credentials.

Immutable or separately controlled storage is preferred.

---

## 109. Backup Restore Security

Restores must be performed into controlled infrastructure.

A restored database must not automatically become production.

Recommended process:

```text
Backup
  ↓
Isolated Restore
  ↓
Integrity Validation
  ↓
Security Validation
  ↓
Application Compatibility Validation
  ↓
Production Cutover
```

---

## 110. Recovery Data Validation

After restore, validate:

* Business count;
* Branch count;
* employee state;
* active permissions;
* Orders;
* Payments;
* Cash Sessions;
* Inventory balances;
* Audit Events;
* Report Versions;
* configuration versions;
* synchronization state;
* idempotency records;
* Business lifecycle state.

---

## 111. Backup and Security Key Recovery

Database restoration is incomplete if required encryption keys or secrets are unavailable.

Disaster recovery must therefore include recovery of:

* backup encryption keys;
* database credentials;
* application secrets;
* signing keys;
* trusted-device verification keys;
* synchronization signing keys.

---

## 112. Security Testing

Database security must be tested at multiple levels.

Tests should include:

* cross-Business access;
* cross-Branch access;
* IDOR;
* unauthorized mutation;
* stale configuration update;
* replayed idempotency request;
* revoked device synchronization;
* READ_ONLY mutation;
* DELETED Business synchronization;
* SQL injection;
* privilege escalation;
* backup access;
* restore integrity.

---

## 113. Automated Security Tests

Security-critical tests should run automatically in CI where practical.

Examples:

```text
Business A user → Business B order → DENIED

Branch A employee → Branch B inventory → DENIED

Inactive employee → price change → DENIED

READ_ONLY business → product mutation → DENIED

Revoked device → synchronization → DENIED
```

---

## 114. Database Security Review

Security-sensitive schema changes must be reviewed for:

* tenant isolation;
* foreign keys;
* permissions;
* indexing;
* deletion behavior;
* audit implications;
* backup implications;
* synchronization implications.

---

## 115. Security Review Before Production

A production database change must not be deployed without considering:

1. Data exposure.
2. Tenant isolation.
3. Authorization.
4. Historical integrity.
5. Backup/recovery.
6. Migration safety.
7. Performance.
8. Auditability.

---

## 116. Data Exposure Through Foreign Keys

Foreign keys enforce integrity but do not automatically enforce authorization.

For example:

```text
order.branch_uuid
```

being valid does not mean the current employee may access that Branch.

Application authorization remains required.

---

## 117. Data Exposure Through Joins

Queries involving multiple tables must preserve the tenant boundary across all joins.

A query starting from a Business-scoped table must not accidentally join unrestricted records from another Business.

---

## 118. Secure Query Pattern

A secure query conceptually follows:

```text
Authenticated Actor
       ↓
Business Scope
       ↓
Branch Scope
       ↓
Permission
       ↓
Entity Ownership
       ↓
Database Query
```

Not:

```text
Entity UUID
       ↓
Database Query
```

---

## 119. Security and Historical Integrity

Security mechanisms must not modify historical data merely to enforce current permissions.

For example:

* employee deactivation does not change old Orders;
* Branch permission changes do not change old Payments;
* Product deactivation does not remove old Order Items;
* subscription expiry does not delete historical records.

---

## 120. Security and Audit Integrity

Authorization failures and important security events should be observable.

Security audit events must themselves be protected from modification.

---

## 121. Security and Data Lifecycle

Security controls must remain active throughout:

```text
ACTIVE
   ↓
READ_ONLY
   ↓
DELETION_ELIGIBLE
   ↓
DELETING
   ↓
DELETED
```

Deletion does not remove the requirement to protect remaining backup copies until their retention expires.

---

## 122. Security and Offline Operation

Offline operation does not create a separate security model.

It uses the same fundamental identity and authorization concepts:

```text
Employee
+
Trusted Device
+
Business
+
Branch
+
Permission
+
Offline Authorization
```

Offline authorization only permits operations within its defined validity.

---

## 123. Offline Data Encryption

Sensitive local database/storage on trusted POS devices must be encrypted.

Local storage must not be treated as trusted merely because the device is registered.

---

## 124. Offline Data Retention

Local offline data should be retained only as long as operationally necessary.

When synchronization succeeds, completed local records may be compacted or archived according to the offline storage policy.

Historical server records remain authoritative.

---

## 125. Offline Device Theft

If a trusted device is lost or stolen:

1. Revoke the device.
2. Invalidate its offline authorization.
3. Reject future synchronization.
4. Review recent activity.
5. Rotate credentials if necessary.
6. Investigate pending offline events.
7. Preserve historical transactions.

---

## 126. Security of Synchronization Metadata

Synchronization metadata such as:

* event UUID;
* sequence;
* synchronization generation;
* device UUID;
* timestamps;
* status;
* conflict state;

must be protected against unauthorized modification.

---

## 127. Clock Security

Offline authorization depends partly on time.

The system must detect suspicious clock rollback or time tampering where practical.

Server time remains authoritative after reconnection.

---

## 128. Database Time

Server-side timestamps should be generated from trusted server/database time for authoritative events.

Client timestamps may be retained as contextual metadata but must not override authoritative server timestamps.

---

## 129. Security of Financial Data

Financial records require strict mutation control.

The database must preserve:

* original payment;
* corrections;
* refunds;
* overpayments;
* debt;
* cash session associations.

Historical financial records must not be silently rewritten.

---

## 130. Security of Inventory Data

Inventory changes must be attributable to:

* Business;
* Branch;
* employee;
* device where applicable;
* source transaction;
* timestamp.

Unauthorized stock adjustments must be rejected.

---

## 131. Security of Payroll Data

Payroll mutation must require explicit permission.

Historical payroll records must remain attributable and auditable.

---

## 132. Security of Permission Data

Permission tables are security-critical.

Permission changes must be:

* authorized;
* validated;
* audited;
* version-aware where required.

An employee must not be able to grant themselves additional authority.

---

## 133. Manager Permission Boundary

A Manager cannot grant permissions beyond the authority available to that Manager.

This rule must be enforced server-side and must not depend only on frontend controls.

---

## 134. Owner Permission Boundary

Owners have broad Business-level authority but remain restricted to their Business.

Owner access must not cross Business boundaries.

---

## 135. Super Admin Boundary

Super Admin is a platform-level role.

Super Admin operations must be separated from ordinary Business operations.

Platform access must not be implemented by simply assigning every Business permission to the Super Admin.

---

## 136. Subscription Security

Subscription entitlement is part of authorization.

Protected operations must validate current entitlement.

Examples:

* creating additional Branches;
* creating employees beyond tariff limits;
* using restricted functions;
* modifying configuration.

---

## 137. Subscription Expiry

When a Business subscription expires:

* modifying operations are blocked according to entitlement rules;
* historical data remains protected;
* viewing remains available where permitted;
* exports remain available where permitted;
* offline devices cannot bypass restrictions.

---

## 138. Security of Tariff Limits

Tariff limits must be validated server-side.

Client-side counters are not authoritative.

Examples:

```text
Owner Count
Employee Count
Branch Count
Enabled Features
```

must be validated against authoritative subscription state.

---

## 139. Database Security and Performance

Security must not require full-table scans for ordinary POS operations.

Important security predicates should be supported by appropriate indexes.

Examples:

```text
business_uuid
branch_uuid
employee_uuid
device_uuid
order_uuid
payment_uuid
cash_session_uuid
```

where applicable.

---

## 140. Security Indexes

Security-related indexes must support common authorization paths.

Examples:

```text
Business → Branch
Business → Employee
Business → Device
Branch → Employee Scope
Business → Order
Branch → Order
Business → Audit Event
```

Indexes must be designed together with the query strategy document.

---

## 141. Database Security and Concurrency

Concurrent security-sensitive updates must use appropriate transaction isolation and locking.

Examples:

* permission changes;
* configuration changes;
* device revocation;
* subscription state;
* Business lifecycle transitions.

---

## 142. Atomic Security State Changes

A security-sensitive state transition should be atomic where practical.

For example:

```text
Revoke Device
+
Invalidate Authorization
+
Record Audit Event
```

must not leave the system in an ambiguous intermediate state.

---

## 143. Security Failure Behavior

If authorization validation fails, the protected operation must fail closed.

The system must not:

* partially apply the mutation;
* silently downgrade security;
* continue using stale permissions;
* fall back to unrestricted access.

---

## 144. Temporary Infrastructure Failure

If security-critical authorization state cannot be validated because the server is unavailable:

* online-only operations must fail safely;
* offline operations may continue only when valid offline authorization explicitly permits them.

The system must not treat infrastructure failure as authorization success.

---

## 145. Fail-Closed Principle

Security-sensitive decisions should use:

```text
Unknown Authorization → Deny
Unknown Tenant Context → Deny
Unknown Branch Scope → Deny
Unknown Device State → Deny
Unknown Subscription State → Deny
```

where the operation requires authoritative online validation.

---

## 146. Security Event Idempotency

Security operations such as device revocation or permission updates should be idempotent where retries are possible.

Repeated requests must not produce contradictory security states.

---

## 147. Security Configuration Versioning

Security-sensitive configuration changes should preserve:

* previous state;
* new state;
* actor;
* timestamp;
* version;
* reason where required.

---

## 148. Security Backup Requirements

Backups must include all data necessary to preserve security state, including:

* employee state;
* role assignments;
* permission overrides;
* device trust state;
* authorization generations;
* synchronization idempotency records;
* configuration versions;
* audit history;
* Business lifecycle state.

---

## 149. Security Restore Requirements

A restore must not accidentally:

* reactivate revoked employees;
* reactivate revoked devices;
* remove permission restrictions;
* reopen deleted Businesses;
* erase audit history;
* duplicate synchronization events.

Restore validation must explicitly check these states.

---

## 150. Database Security Invariants

The following invariants are mandatory:

1. The client never connects directly to PostgreSQL.
2. Production database credentials are never stored in frontend code.
3. Application runtime does not use PostgreSQL superuser privileges.
4. Database credentials are managed outside source code.
5. Production database network access is restricted.
6. Production database traffic uses encrypted transport where network boundaries require it.
7. Business UUIDs are globally unique.
8. Business UUIDs are never reused.
9. Business boundaries are enforced server-side.
10. Branch boundaries are enforced server-side.
11. UUID possession never grants authorization.
12. Trusted-device status never replaces permission validation.
13. Super Admin is separate from Business Owner authority.
14. Cross-Business references are prohibited unless explicitly defined.
15. Repository queries preserve Business scope.
16. Branch-scoped queries preserve Branch scope.
17. IDOR access is rejected.
18. Frontend authorization is never the only authorization layer.
19. Application runtime cannot arbitrarily modify database schema.
20. Migration privileges are separated from runtime privileges.
21. Backup privileges are separated from application privileges.
22. Backup storage credentials are separate from runtime credentials.
23. Backups are encrypted.
24. Backup integrity is verifiable.
25. Critical backups are protected against ordinary deletion where infrastructure supports it.
26. Audit records are immutable.
27. Audit records are backed up.
28. Passwords are never stored in plaintext.
29. Password hashes are never returned through normal APIs.
30. Authentication secrets are not written to logs.
31. Database credentials are not written to logs.
32. Tenant context cannot leak through pooled connections.
33. Background jobs must establish their own tenant context.
34. Security failures fail closed.
35. Unknown authorization does not become authorization success.
36. READ_ONLY Businesses cannot perform blocked mutations.
37. DELETED Businesses cannot be resurrected through synchronization.
38. Revoked devices cannot perform new authorized synchronization.
39. Offline authorization is time-bounded.
40. Offline authorization is signed.
41. Server time is authoritative for server-side events.
42. Client timestamps cannot override authoritative server timestamps.
43. Synchronization events require idempotency.
44. Idempotency state is backed up.
45. Recovery must preserve idempotency state.
46. Recovery must account for stale offline clients.
47. Recovery generation changes are handled explicitly.
48. Stale offline events cannot be replayed blindly after recovery.
49. Price changes require authorization.
50. Inventory corrections require authorization.
51. Refunds require authorization.
52. Payroll changes require authorization.
53. Permission changes require authorization.
54. Employees cannot grant themselves permissions.
55. Managers cannot grant permissions beyond their authority.
56. Subscription limits are validated server-side.
57. Subscription expiry cannot be bypassed through offline mode.
58. Database errors do not expose secrets to ordinary users.
59. Dynamic SQL identifiers are validated.
60. SQL values use parameter binding.
61. Security-sensitive mutations occur within appropriate transaction boundaries.
62. Authorization is validated before protected mutation.
63. Historical transactions are not rewritten for current authorization changes.
64. Employee deactivation does not rewrite historical transactions.
65. Device revocation does not delete historical transactions.
66. Permission changes do not rewrite historical records.
67. Current configuration does not reinterpret historical transactions.
68. Business deletion does not depend on uncontrolled cascading deletes.
69. Live-data deletion and backup retention are separate lifecycle processes.
70. Backup copies remain protected until their retention period expires.
71. Encryption keys are protected separately from encrypted data where practical.
72. Key loss must be considered in disaster recovery.
73. Administrative database access is restricted.
74. Administrative actions are auditable where infrastructure permits.
75. Database schema changes are version-controlled.
76. Destructive migrations have recovery protection.
77. Security-critical schema changes are reviewed.
78. Security-related indexes support common authorization queries.
79. Long-running security operations must not unnecessarily block POS transactions.
80. Security controls must not become a reason to bypass authorization.
81. Database runtime access is least-privileged.
82. Database roles are separated by responsibility.
83. PostgreSQL extensions are explicitly controlled.
84. Database network exposure is minimized.
85. Application secrets are not embedded in database queries.
86. Raw backup files are not exposed to ordinary employees.
87. XLSX exports enforce tenant and Branch scope.
88. Report generation preserves tenant isolation.
89. Payroll data is permission-protected.
90. Recipe data may be permission-protected.
91. Price configuration changes are audited.
92. Device trust changes are audited.
93. Permission changes are audited.
94. Business lifecycle changes are audited.
95. Security-sensitive configuration is versioned where required.
96. Security operations are idempotent where retries are possible.
97. Security state changes are atomic where practical.
98. Temporary infrastructure failures do not grant authorization.
99. Database restoration does not automatically reactivate revoked security state.
100. Security state remains attributable to the responsible actor or system process.

---

## 151. Security Operations Checklist

Before production deployment:

* [ ] PostgreSQL is not publicly exposed.
* [ ] TLS/network encryption is configured where required.
* [ ] Runtime database role is least-privileged.
* [ ] Migration role is separate.
* [ ] Backup role is separate.
* [ ] Superuser credentials are restricted.
* [ ] Database credentials are outside source control.
* [ ] Secrets are excluded from logs.
* [ ] Business isolation tests pass.
* [ ] Branch isolation tests pass.
* [ ] IDOR tests pass.
* [ ] SQL injection tests pass.
* [ ] Permission escalation tests pass.
* [ ] Device revocation tests pass.
* [ ] Offline authorization tests pass.
* [ ] READ_ONLY restrictions pass.
* [ ] DELETED Business synchronization tests pass.
* [ ] Backup encryption is verified.
* [ ] Restore procedure is tested.
* [ ] Audit integrity is verified.
* [ ] Database security monitoring is active.

---

## 152. Security Incident Checklist

When a database security incident is suspected:

1. Identify affected credentials.
2. Restrict access.
3. Preserve logs and audit evidence.
4. Rotate compromised credentials.
5. Check administrative activity.
6. Check cross-tenant access attempts.
7. Check suspicious mutations.
8. Check synchronization activity.
9. Check backup integrity.
10. Validate Business/Branch isolation.
11. Determine affected time range.
12. Repair or restore where required.
13. Reconcile offline devices.
14. Rotate affected signing/encryption secrets where required.
15. Document the incident.
16. Review and improve preventive controls.

---

## 153. Implementation Guidance

The implementation should use the following security layers:

```text
Authentication
      ↓
Business Context
      ↓
Branch Scope
      ↓
Role Permission
      ↓
Employee Override
      ↓
Subscription Entitlement
      ↓
Entity Ownership
      ↓
Database Query
      ↓
Database Constraints
```

No single layer should be treated as sufficient for the entire security model.

---

## 154. Security and Database Constraints

Database constraints should provide structural protection for:

* Business ownership;
* Branch ownership;
* foreign-key relationships;
* uniqueness;
* valid lifecycle states;
* required fields;
* impossible negative values where applicable.

Business rules that cannot be represented safely through constraints remain application/service responsibilities.

---

## 155. Security and Application Transactions

The service/use-case layer owns the business transaction boundary.

Security validation must occur within the same logical transaction where a race condition could otherwise allow unauthorized mutation.

---

## 156. Security and Outbox

Security-sensitive events that must be delivered asynchronously should use the existing transactional outbox pattern where appropriate.

The outbox must preserve:

* Business scope;
* Branch scope;
* event identity;
* event type;
* idempotency;
* security context.

---

## 157. Security and Background Processing

Background processing must never use unrestricted database access merely because it runs internally.

Each worker operation must still enforce:

* tenant scope;
* lifecycle;
* authorization context where applicable;
* idempotency;
* data ownership.

System-generated operations should use an explicit system actor identity.

---

## 158. System Actor

Operations performed automatically by the platform should be attributable to a system actor or explicit system source.

Examples:

* scheduled report;
* automatic low-stock notification;
* subscription lifecycle transition;
* deletion workflow;
* backup metadata registration;
* synchronization processing.

System actors must not be confused with ordinary employees.

---

## 159. Security Documentation

Database security changes must update relevant documentation and ADRs when they alter architectural behavior.

Important changes should reference:

* affected database document;
* architecture document;
* migration;
* security decision;
* operational impact.

---

## 160. Status

**Document Status:** Accepted
**Version:** 1.0
**Current Document:** `29_Database_Security.md`
**Previous Document:** `28_Database_Backup_and_Recovery.md`
**Next Document:** `30_Database_Invariants_and_Guardrails.md`

---

## Related Documents

### Database

* `docs/05_Database/01_Database_Overview.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/27_Database_Migrations_and_Change_Management.md`
* `docs/05_Database/28_Database_Backup_and_Recovery.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/18_Audit_and_Change_History.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`

### Architecture

* `docs/04_Architecture/13_Background_Processing_Architecture.md`
* `docs/04_Architecture/15_Observability_and_Operations_Architecture.md`
* `docs/04_Architecture/16_Scalability_and_Performance_Architecture.md`
* `docs/04_Architecture/17_Failure_Recovery_Architecture.md`

### ADR

* `adr/ADR-001-Documentation-First.md`

