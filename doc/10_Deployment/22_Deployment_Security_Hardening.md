# Deployment Security Hardening

**Document ID:** DEP-22
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/10_Deployment/README.md`
**Previous Document:** `21_Deployment_Monitoring_Health_Checks_and_Alerting.md`
**Next Document:** To be defined

---

# 1. Purpose

This document defines the production deployment security hardening requirements for FastFood ERP.

The purpose is to ensure that production infrastructure, operating systems, runtime environments, network services, application processes, databases, deployment mechanisms, and supporting services are configured according to a secure production baseline.

Security hardening must reduce:

* unauthorized access;
* privilege escalation;
* unnecessary network exposure;
* service compromise;
* credential theft;
* secret leakage;
* lateral movement;
* data exposure;
* malicious configuration changes;
* insecure deployment behavior;
* persistence after compromise.

Security hardening must not introduce unnecessary complexity or performance overhead that would make FastFood ERP unsuitable for its target infrastructure.

---

# 2. Scope

This document covers production hardening for:

* operating systems;
* application servers;
* runtime environments;
* reverse proxies;
* API services;
* frontend delivery;
* PostgreSQL;
* background workers;
* schedulers;
* queues;
* caches where applicable;
* network configuration;
* firewalls;
* service isolation;
* process privileges;
* SSH and administrative access;
* secrets;
* TLS;
* file permissions;
* system updates;
* logging;
* security monitoring;
* deployment artifacts;
* backups;
* recovery environments;
* branch synchronization;
* offline operation;
* production configuration;
* incident containment.

This document does not replace the application security architecture.

It defines deployment and infrastructure security controls that support the overall FastFood ERP security model.

---

# 3. Security Objectives

Production deployment must provide:

1. Least privilege.
2. Minimal attack surface.
3. Controlled network exposure.
4. Strong administrative access control.
5. Service isolation.
6. Protected secrets.
7. Secure communication.
8. Controlled filesystem access.
9. Secure database access.
10. Auditable administrative actions.
11. Secure deployment artifacts.
12. Timely security updates.
13. Secure backups.
14. Controlled recovery environments.
15. Monitoring of security-relevant events.
16. Safe failure behavior.
17. Protection against lateral movement.
18. Protection of tenant and branch data.

---

# 4. Security Principles

FastFood ERP production infrastructure follows these principles:

1. Expose only required services.
2. Do not run unnecessary services.
3. Do not run application services as root.
4. Use least-privileged service accounts.
5. Separate administrative access from application access.
6. Keep PostgreSQL private.
7. Keep internal services private.
8. Protect secrets outside source code.
9. Encrypt network traffic where appropriate.
10. Use secure defaults.
11. Disable unnecessary protocols and features.
12. Patch supported operating-system components.
13. Monitor security-relevant changes.
14. Preserve audit evidence.
15. Keep security controls lightweight enough for the target hardware.
16. Prefer simple controls that are easy to verify.
17. Do not rely on obscurity.
18. Do not assume the internal network is trusted.
19. Treat deployment artifacts as security-sensitive.
20. Rebuild compromised infrastructure from trusted sources rather than trusting an uncertain environment.

---

# 5. Production Security Boundary

The production environment should be treated as a controlled security boundary.

A conceptual deployment structure is:

```text
Internet
   |
   v
[Firewall / Network Boundary]
   |
   v
[Reverse Proxy / TLS Entry]
   |
   v
[Application/API Layer]
   |
   +------> [Worker]
   |
   +------> [Scheduler]
   |
   +------> [Queue/Cache]
   |
   v
[PostgreSQL]
```

Only components that must receive external traffic should be externally reachable.

---

# 6. Public Exposure

The production environment should expose only required public endpoints.

Typically:

```text
HTTPS
  |
  v
Reverse Proxy
  |
  v
Application
```

PostgreSQL, queues, internal worker interfaces, administrative services, and internal monitoring interfaces should not be directly exposed to the public Internet unless there is an explicitly justified and protected requirement.

---

# 7. Network Segmentation

Where infrastructure permits, services should be separated into logical network zones.

Recommended conceptual separation:

```text
Public Zone
    |
    v
Application Zone
    |
    v
Data Zone
```

Administrative access should use a separate controlled path.

The exact network implementation may vary by deployment environment.

---

# 8. Firewall Policy

The production firewall should follow a deny-by-default approach.

Only required traffic should be allowed.

Conceptually:

```text
Inbound
  |
  +--> Required HTTPS
  |
  +--> Controlled Administration
  |
  +--> Required Internal Services
  |
  +--> Deny Everything Else
```

Outbound traffic should also be controlled where practical.

---

# 9. Port Exposure

Every exposed port must have a documented purpose.

For each production port:

* identify the service;
* identify the expected source;
* identify the expected destination;
* determine whether public exposure is required;
* document why the port exists.

Unused ports should be closed.

---

# 10. Reverse Proxy Hardening

The reverse proxy is a primary production security boundary.

It should:

* terminate TLS where appropriate;
* reject invalid requests;
* limit unnecessary methods;
* apply request-size limits;
* enforce appropriate timeout values;
* protect upstream services from direct exposure;
* preserve required security headers;
* avoid exposing internal server details.

---

# 11. TLS

Production external communication should use HTTPS.

TLS configuration should:

* use supported protocol versions;
* disable obsolete protocols;
* use trusted certificates;
* protect private keys;
* renew certificates before expiration;
* monitor certificate validity.

Internal encryption requirements depend on the trust boundary and deployment architecture.

---

# 12. TLS Certificate Management

Certificates should be:

* managed through a controlled process;
* monitored for expiration;
* replaced without unnecessary downtime;
* stored securely;
* accessible only to required services.

Certificate private keys must not be committed to source control.

---

# 13. HTTP Security

Production HTTP configuration should include appropriate security controls.

Where applicable:

* HTTPS redirection;
* secure cookies;
* appropriate `SameSite` configuration;
* HSTS where appropriate;
* content security controls;
* clickjacking protection;
* MIME-sniffing protection.

Security headers must be selected according to application behavior rather than copied blindly.

---

# 14. Operating System Hardening

The production operating system should use a minimal supported installation.

Remove or disable:

* unnecessary packages;
* unnecessary services;
* unused network daemons;
* obsolete protocols;
* unnecessary user accounts;
* unused administrative interfaces.

The objective is to reduce attack surface.

---

# 15. OS Update Policy

Operating-system security updates should be applied according to a controlled maintenance process.

Updates should be:

* monitored;
* tested where practical;
* prioritized according to severity;
* deployed through controlled procedures;
* verified after installation.

Critical security updates may require accelerated deployment.

---

# 16. Security Patch Priority

Recommended priority:

### Critical

Immediate or accelerated response.

### High

Prompt scheduled deployment.

### Medium

Normal maintenance cycle.

### Low

Planned maintenance.

Actual response time should consider:

* exploitability;
* exposure;
* affected component;
* available mitigation;
* business impact.

---

# 17. Kernel and Runtime Security

The production environment should use supported operating-system kernels and runtime components.

Where supported by the platform, enable security mechanisms such as:

* process isolation;
* filesystem permissions;
* mandatory access controls;
* address-space protections;
* secure kernel defaults.

Security features must be tested before production activation when they could affect application behavior.

---

# 18. Administrative Accounts

Production administrative access must use individual accounts.

Shared administrative accounts should be avoided.

Each administrator should have:

* unique identity;
* appropriate privilege;
* authenticated access;
* auditable activity.

Administrative access must not depend on a single untracked account.

---

# 19. Root Access

Direct root access should be restricted.

Applications and normal operational services must not run as root.

Administrative escalation should be controlled and auditable.

---

# 20. SSH Hardening

Where SSH is used:

* use key-based authentication;
* disable unnecessary authentication mechanisms;
* restrict administrative access;
* avoid direct root login;
* use individual administrator accounts;
* monitor authentication attempts;
* remove unused accounts and keys.

SSH should not be publicly accessible unless required.

Where public exposure is required, additional network restrictions should be considered.

---

# 21. SSH Key Management

SSH keys must be:

* individually assigned;
* protected;
* rotated or revoked when required;
* removed when access is no longer needed.

Lost or compromised keys must be revoked immediately.

Private keys must never be stored in application repositories.

---

# 22. Administrative Access Control

Administrative access should be limited by:

* identity;
* role;
* network source;
* authentication strength;
* required privilege.

Production administration should not be available to ordinary application users.

---

# 23. Service Accounts

Each service should use a dedicated service identity where practical.

Examples:

* API service;
* worker service;
* scheduler;
* monitoring agent.

Service accounts should have only the permissions required for their function.

---

# 24. Service Isolation

Services should be isolated from one another.

Conceptually:

```text
API
 |
 +--> API permissions only

Worker
 |
 +--> Worker permissions only

Scheduler
 |
 +--> Scheduler permissions only

PostgreSQL
 |
 +--> Database permissions only
```

A compromised API process should not automatically obtain administrative access to the operating system.

---

# 25. Process Privileges

Application processes should:

* run under non-root identities;
* have restricted filesystem permissions;
* access only required directories;
* use controlled environment variables;
* avoid unnecessary Linux capabilities;
* avoid privileged ports where possible.

---

# 26. Filesystem Hardening

Application directories should be separated into:

* executable/application files;
* configuration;
* writable runtime data;
* logs;
* temporary files.

The application should not have write access to its own executable source or deployment artifacts unless required.

---

# 27. Writable Directories

Writable directories should be minimized.

Examples of legitimate writable locations may include:

* temporary runtime files;
* controlled upload storage;
* generated reports;
* logs where applicable.

User-controlled uploads must not automatically become executable files.

---

# 28. Upload Security

Where file uploads are supported:

* validate file type;
* validate size;
* use safe storage locations;
* generate controlled filenames;
* prevent path traversal;
* prevent executable interpretation;
* restrict access;
* scan or validate content where appropriate.

Uploads should not be stored directly inside executable application directories.

---

# 29. Configuration Security

Production configuration must be separated from source code where secrets are involved.

Configuration should be:

* versioned where appropriate;
* validated;
* access-controlled;
* auditable;
* environment-specific.

Secrets must not be hardcoded.

---

# 30. Secret Management

Secrets include:

* database passwords;
* API keys;
* signing keys;
* TLS private keys;
* authentication secrets;
* integration credentials.

Secrets should be stored in a secure secret-management mechanism or protected deployment configuration.

They must not be committed to Git.

---

# 31. Secret Exposure Prevention

Secrets must not appear in:

* source code;
* logs;
* error messages;
* monitoring dashboards;
* screenshots;
* deployment records;
* public configuration;
* health-check responses.

---

# 32. Secret Rotation

Production credentials should support controlled rotation.

Rotation should consider:

* database credentials;
* application signing keys;
* external integration credentials;
* administrative credentials;
* TLS certificates.

Rotation must be tested so that it does not unexpectedly interrupt active services.

---

# 33. Database Security

PostgreSQL is a critical security boundary.

Database hardening should include:

* private network exposure;
* strong authentication;
* least-privilege roles;
* restricted connections;
* controlled administrative access;
* secure backups;
* encrypted connections where required;
* auditability of privileged actions.

---

# 34. PostgreSQL Network Exposure

PostgreSQL should not normally be directly reachable from the public Internet.

Expected pattern:

```text
Internet
   X
   |
PostgreSQL

Application
   |
   v
PostgreSQL
```

Only authorized application or administrative sources should reach the database.

---

# 35. Database Roles

Separate database roles should be used for different responsibilities where practical.

Examples:

* application runtime;
* migration;
* administrative maintenance;
* backup/recovery.

The application runtime role should not automatically possess unrestricted schema-administration privileges.

---

# 36. Migration Privileges

Database migration privileges should be separated from normal application privileges where practical.

This reduces the impact of an application compromise.

Migration execution must follow `DEP-15`.

---

# 37. Database Password Security

Database credentials must:

* use strong secrets;
* be stored securely;
* not appear in source control;
* be rotated according to security policy;
* be revoked when no longer required.

---

# 38. Database Backup Security

Backups must be treated as sensitive production data.

Protect backups with:

* access control;
* encryption;
* integrity validation;
* retention policy;
* independent storage;
* audit logging.

Backup security is part of the disaster recovery security boundary.

---

# 39. Backup Access

Only authorized recovery or operational identities should access production backups.

A compromised application server should not automatically have unrestricted access to all historical backups.

Where practical, backup credentials should be isolated from application runtime credentials.

---

# 40. Runtime Hardening

Application runtime environments should use:

* supported runtime versions;
* minimal dependencies;
* pinned or controlled dependency versions;
* secure configuration;
* non-root execution;
* restricted filesystem access;
* controlled network access.

---

# 41. Dependency Security

Production dependencies should be:

* identified;
* version controlled;
* reviewed;
* updated through controlled releases;
* monitored for known security vulnerabilities.

Unused dependencies should be removed.

---

# 42. Dependency Installation

Production servers should not install arbitrary packages directly during normal application startup.

Application artifacts should be built through the controlled deployment process.

This improves:

* reproducibility;
* security;
* auditability;
* rollback capability.

---

# 43. Application Artifact Security

Deployment artifacts should be:

* built from controlled source;
* versioned;
* traceable to a commit or release;
* protected against unauthorized modification;
* verified before deployment where practical.

The production server should not compile arbitrary application code as part of ordinary startup unless explicitly required.

---

# 44. Deployment Credentials

Deployment credentials must be separated from application runtime credentials.

A compromised application should not automatically be able to deploy a new version.

---

# 45. CI/CD Security

The deployment pipeline should follow least privilege.

Pipeline credentials should have access only to required resources.

The pipeline should:

* authenticate securely;
* protect secrets;
* verify artifacts;
* record deployment actions;
* prevent unauthorized production deployment.

---

# 46. Production Deployment Authorization

Production deployment should require appropriate authorization.

Depending on the deployment process, controls may include:

* protected branches;
* release approval;
* deployment identity;
* environment protection;
* audit records.

The exact mechanism may vary by tooling.

---

# 47. Source Control Security

Source repositories should protect:

* production configuration;
* secrets;
* signing keys;
* database credentials;
* private certificates.

Security-sensitive files must be excluded through appropriate repository controls.

---

# 48. Git Repository Protection

Production source repositories should use appropriate protections such as:

* protected production branches;
* controlled merge permissions;
* review requirements;
* secret scanning where available;
* dependency scanning where available.

These controls support deployment security but do not replace production runtime hardening.

---

# 49. Environment Separation

Production, staging, and development environments should be logically separated.

Production credentials must not be reused in development.

Development systems must not receive unrestricted production secrets.

---

# 50. Staging Security

Staging should resemble production security controls where practical.

This allows security configuration to be tested before production.

However, production credentials and sensitive production data should remain protected.

---

# 51. Production Network Egress

Outbound traffic should be controlled where practical.

The application should not have unrestricted access to arbitrary Internet destinations unless required.

This reduces the impact of:

* compromised application code;
* malicious dependencies;
* server compromise;
* data exfiltration.

---

# 52. External Integrations

External services should be explicitly identified.

Examples may include:

* payment services;
* notification services;
* identity services;
* future online ordering integrations.

Each integration should have:

* known destination;
* controlled credentials;
* required network access;
* timeout limits;
* logging;
* failure handling.

---

# 53. Network Timeouts

External connections should have bounded:

* connection timeout;
* read timeout;
* retry count;
* total operation time.

Unbounded retries can create denial-of-service conditions inside the application.

---

# 54. Retry Security

Retries should be:

* bounded;
* preferably exponential/backoff where appropriate;
* idempotent where possible;
* observable.

Do not blindly retry financial or inventory operations unless their idempotency guarantees are established.

---

# 55. Internal Service Communication

Internal services should authenticate where required by the architecture.

Internal network access alone should not automatically imply unrestricted trust.

Services should validate:

* caller identity;
* expected credentials;
* request integrity;
* authorization.

---

# 56. Queue Security

Queues should be private.

Access should be limited to:

* authorized producers;
* authorized consumers;
* administrators where required.

Queue credentials must not be exposed to frontend clients.

---

# 57. Cache Security

Where caching is used:

* keep the cache private;
* restrict network access;
* protect credentials;
* avoid storing sensitive information unnecessarily;
* define expiration behavior.

Sensitive session or authentication data requires appropriate protection.

---

# 58. Monitoring Security

Monitoring infrastructure is itself sensitive.

Protect:

* metrics;
* logs;
* traces;
* dashboards;
* alert configuration;
* monitoring credentials.

Public users should not have unrestricted access to internal operational telemetry.

---

# 59. Health Endpoint Security

Public health endpoints should expose minimal information.

Avoid exposing:

* database names;
* internal hostnames;
* credentials;
* dependency connection strings;
* filesystem paths;
* internal IP addresses;
* detailed stack traces.

Detailed health endpoints should be restricted.

---

# 60. Error Response Security

Production error responses should not expose:

* stack traces;
* SQL statements;
* filesystem paths;
* secret values;
* internal network details;
* framework debug pages.

Detailed diagnostics belong in protected logs.

---

# 61. Debug Mode

Production debug modes must be disabled unless there is an explicitly controlled temporary diagnostic requirement.

Debug mode can expose sensitive implementation information.

Any temporary diagnostic activation must:

* be authorized;
* be time-limited;
* be monitored;
* be disabled after investigation.

---

# 62. Application Debugging

Production troubleshooting should prefer:

* logs;
* metrics;
* traces;
* controlled diagnostics;
* safe health endpoints.

Do not enable broad debug behavior simply because troubleshooting is difficult.

---

# 63. Session and Cookie Security

Where browser sessions are used:

* use HTTPS;
* use secure cookies;
* use appropriate `HttpOnly`;
* use appropriate `SameSite`;
* define reasonable expiration;
* invalidate sessions when required.

Exact settings depend on the authentication architecture.

---

# 64. Authentication Infrastructure

Authentication services must be protected from:

* credential brute force;
* session theft;
* unauthorized administrative access;
* insecure transport.

Authentication failures should be monitored according to `DEP-21`.

---

# 65. Administrative API Security

Administrative APIs should require appropriate authentication and authorization.

Do not expose privileged deployment or operational endpoints to ordinary application users.

---

# 66. Internal Administrative Endpoints

Internal endpoints such as:

* deployment controls;
* detailed health;
* metrics;
* diagnostics;
* worker controls;

should be restricted to authorized operational access.

---

# 67. Rate Limiting

Production services should use appropriate rate limiting for exposed endpoints.

Rate limiting should protect against:

* brute force;
* abusive requests;
* accidental request storms;
* resource exhaustion.

Rate limits should not interfere with legitimate restaurant operations.

---

# 68. Request Size Limits

Production entry points should enforce reasonable limits for:

* request body;
* uploaded files;
* headers;
* URL length where appropriate.

Limits reduce resource-exhaustion risk.

---

# 69. Timeout Hardening

Set appropriate timeouts for:

* reverse proxy;
* API requests;
* database connections;
* external services;
* queue operations;
* worker jobs.

Timeout values should reflect actual business operations.

---

# 70. Denial-of-Service Considerations

Security hardening should reduce unnecessary resource consumption.

Controls may include:

* connection limits;
* request limits;
* rate limiting;
* timeouts;
* worker concurrency limits;
* queue limits;
* database connection limits.

These controls must be tuned to preserve normal restaurant operations.

---

# 71. Process Resource Limits

Where supported, production services should use appropriate limits for:

* memory;
* CPU;
* open files;
* process count;
* worker count.

Resource limits can prevent one compromised or malfunctioning service from exhausting the entire server.

---

# 72. Service Restart Policy

Services should have controlled restart behavior.

Automatic restart can improve availability, but repeated failures must be visible through monitoring.

A service must not restart indefinitely without generating an alert.

---

# 73. Temporary Files

Temporary files should:

* use controlled directories;
* have appropriate permissions;
* be cleaned according to operational requirements;
* not contain secrets unnecessarily.

---

# 74. System Logging

Operating-system security events should be logged where practical.

Examples:

* authentication attempts;
* privilege escalation;
* service changes;
* configuration changes;
* firewall changes;
* SSH activity.

Logs must be protected against unauthorized modification.

---

# 75. Time Synchronization

Production systems should maintain reliable time synchronization.

Accurate time is important for:

* authentication;
* TLS;
* logs;
* deployment events;
* audit records;
* synchronization;
* incident investigation.

---

# 76. File Integrity

Where practical, critical production files should be protected against unauthorized modification.

Important areas include:

* application artifacts;
* configuration;
* service definitions;
* deployment scripts;
* security configuration.

---

# 77. Configuration Drift

Production configuration should be controlled.

Detect unexpected changes to:

* firewall rules;
* service definitions;
* application configuration;
* database configuration;
* operating-system security settings.

Configuration drift can create security vulnerabilities.

---

# 78. Infrastructure as Code

Where infrastructure automation is used, production infrastructure definitions should be version controlled.

This supports:

* reproducibility;
* review;
* audit;
* recovery;
* configuration consistency.

This is particularly important for `DEP-20`.

---

# 79. Immutable or Rebuildable Infrastructure

Where practical, production services should be deployable from known artifacts and configuration.

If compromise occurs, the preferred strategy should be:

```text
Identify Compromise
      |
      v
Contain
      |
      v
Preserve Evidence
      |
      v
Rebuild Trusted Environment
      |
      v
Restore Trusted Data
      |
      v
Validate
      |
      v
Resume
```

This aligns with disaster recovery requirements.

---

# 80. Security Incident Isolation

When a production server is suspected of compromise:

1. contain access;
2. prevent further unauthorized activity;
3. preserve relevant evidence;
4. determine affected components;
5. rotate compromised credentials;
6. rebuild from trusted sources;
7. restore trusted data;
8. validate security;
9. resume service gradually.

Do not assume that restarting a compromised process makes the environment trusted.

---

# 81. Credential Compromise

If credentials are suspected to be compromised:

* revoke them;
* rotate them;
* identify affected services;
* inspect access logs;
* determine possible data exposure;
* update dependent services;
* verify recovery.

---

# 82. Production Security and Deployment Recovery

A deployment rollback does not automatically resolve a security compromise.

If the release introduced a security vulnerability:

```text
Rollback Application
        +
Investigate Vulnerability
        +
Rotate Affected Secrets
        +
Verify Infrastructure
```

may all be required.

---

# 83. Security Monitoring After Deployment

After deployment, monitor:

* authentication failures;
* authorization failures;
* unexpected administrative activity;
* unusual network traffic;
* unexpected process behavior;
* unexpected file changes;
* resource spikes;
* new outbound destinations.

Security anomalies should be correlated with deployment changes.

---

# 84. Security Verification During Deployment

A production deployment should verify:

* correct service user;
* correct file permissions;
* correct network exposure;
* correct TLS configuration;
* correct secret loading;
* correct database access;
* correct health endpoint exposure;
* debug mode disabled;
* expected application artifact;
* expected configuration version.

---

# 85. Deployment Security Checklist

Before deployment:

* [ ] Production artifact is trusted.
* [ ] Deployment source is known.
* [ ] Dependencies are reviewed.
* [ ] Secrets are available through secure mechanisms.
* [ ] Production credentials are not embedded in artifacts.
* [ ] Firewall rules are correct.
* [ ] Database is not unintentionally exposed.
* [ ] Administrative access is available to authorized operators.
* [ ] Monitoring is active.
* [ ] Backup/recovery procedures are available.

---

# 86. Post-Deployment Security Checklist

After deployment:

* [ ] Application runs under the correct service account.
* [ ] No unnecessary privileged process is running.
* [ ] Public ports remain correct.
* [ ] Internal services remain private.
* [ ] TLS is valid.
* [ ] Debug mode is disabled.
* [ ] Health endpoints expose no sensitive information.
* [ ] Database connectivity works with expected privileges.
* [ ] Logs contain no secrets.
* [ ] Security monitoring is active.
* [ ] No unexpected configuration change is detected.

---

# 87. Database Security Verification

After database-related deployment changes:

* [ ] PostgreSQL remains private.
* [ ] Application role has expected privileges.
* [ ] Migration role is not unnecessarily used by runtime.
* [ ] Database authentication works.
* [ ] Unexpected database roles do not exist.
* [ ] Backup status remains healthy.
* [ ] Monitoring remains active.

---

# 88. Network Security Verification

After network changes:

* [ ] Required public ports are reachable.
* [ ] Unrequired ports are blocked.
* [ ] PostgreSQL remains protected.
* [ ] Internal services remain protected.
* [ ] Administrative access remains restricted.
* [ ] Required outbound integrations work.
* [ ] Unexpected outbound access is not introduced.

---

# 89. Runtime Security Verification

After runtime changes:

* [ ] Supported runtime version is active.
* [ ] Application process is non-root.
* [ ] File permissions are correct.
* [ ] Required dependencies are installed.
* [ ] Unnecessary dependencies are absent where practical.
* [ ] Application artifact matches expected release.
* [ ] Debug features are disabled.

---

# 90. Secret Security Verification

After deployment:

* [ ] Required secrets load successfully.
* [ ] No secrets appear in logs.
* [ ] No secrets appear in public configuration.
* [ ] No secret files are unnecessarily exposed.
* [ ] Expired credentials are not used.
* [ ] Rotated credentials are active where required.

---

# 91. Security Monitoring Alerts

Security-related alerts should include:

### Critical

* suspected production compromise;
* privileged account compromise;
* unauthorized production deployment;
* exposed database;
* confirmed secret compromise.

### High

* unusual administrative access;
* repeated privilege escalation failures;
* unexpected configuration changes;
* abnormal authentication activity.

### Medium

* repeated failed login attempts;
* unexpected service configuration change;
* unusual network behavior requiring investigation.

---

# 92. Security Alert Correlation

Security alerts should be correlated with:

* deployment version;
* deployment timestamp;
* administrator identity;
* configuration change;
* infrastructure change.

This helps determine whether a security event was:

* expected;
* deployment-related;
* accidental;
* malicious.

---

# 93. Security and Monitoring Integration

`DEP-21` defines operational monitoring.

`DEP-22` adds security-specific hardening and monitoring requirements.

The relationship is:

```text
DEP-22
Security Controls
      |
      v
DEP-21
Monitoring
      |
      v
Detection
      |
      v
DEP-17 / DEP-20
Recovery
```

---

# 94. Security and High Availability

Security controls must not unintentionally create a single point of failure.

For example:

* certificate renewal must be reliable;
* authentication infrastructure must be recoverable;
* firewall configuration must be documented;
* administrative access must have a controlled recovery path.

This must remain consistent with `DEP-19`.

---

# 95. Security and Disaster Recovery

Recovery environments must receive equivalent security controls.

A disaster recovery environment must not become a security shortcut.

Before restoring production traffic:

* network controls must be active;
* secrets must be protected;
* administrative access must be restricted;
* monitoring must be active;
* database access must be protected;
* security validation must pass.

This follows `DEP-20`.

---

# 96. Security and Backup Recovery

Backups must be restored into a controlled environment.

Do not expose restored databases publicly during recovery testing.

Recovery testing should validate:

* data integrity;
* access controls;
* database roles;
* application credentials;
* network restrictions.

---

# 97. Security and Offline Branches

Offline branch operation introduces additional security considerations.

Branch environments should:

* protect local data;
* restrict local administrative access;
* protect stored credentials;
* protect synchronization credentials;
* retain transaction integrity;
* reject unauthorized synchronization.

Offline operation must not bypass authorization rules.

---

# 98. Branch Synchronization Security

Synchronization must protect against:

* duplicate transactions;
* unauthorized branch identity;
* forged transactions;
* replay;
* altered payloads;
* cross-branch data access.

Synchronization should use appropriate authentication and integrity controls.

---

# 99. Synchronization Credentials

Each branch or synchronization client should use controlled credentials or identity mechanisms.

Credentials must be:

* protected;
* revocable;
* associated with the intended branch/device where appropriate;
* monitored.

A branch credential must not provide unrestricted access to unrelated branches.

---

# 100. Replay Protection

Synchronization must protect against accidental or malicious replay.

The system should use appropriate mechanisms such as:

* client transaction IDs;
* idempotency keys;
* unique constraints;
* sequence information;
* authenticated synchronization requests.

This remains consistent with the synchronization rules defined elsewhere.

---

# 101. Device Security

New or unfamiliar devices should be subject to the existing controlled verification process.

Offline devices that cannot securely establish required identity should not be allowed unrestricted new access.

The security model should remain simple enough for restaurant operations.

---

# 102. Printer and Peripheral Security

Where printers or local peripherals are connected:

* restrict network exposure;
* avoid unnecessary public access;
* use trusted local network paths;
* prevent arbitrary Internet access where not required.

Printer connectivity problems must not require exposing internal services publicly.

---

# 103. Production Security Baseline

A production server baseline should include:

```text
Supported OS
+
Minimal Installed Services
+
Firewall
+
Restricted Administrative Access
+
Non-Root Application
+
Private Database
+
Protected Secrets
+
TLS
+
Monitoring
+
Auditing
+
Controlled Updates
```

---

# 104. Security Configuration Baseline

A versioned security baseline should define:

* required ports;
* required services;
* service accounts;
* file permissions;
* administrative access;
* TLS requirements;
* database exposure;
* logging;
* monitoring;
* backup security;
* patch expectations.

---

# 105. Baseline Drift Detection

Security configuration should periodically be compared with the approved baseline.

Unexpected differences should generate an operational/security event.

---

# 106. Production Hardening Review

Hardening should be reviewed after:

* major OS changes;
* infrastructure changes;
* new public services;
* new external integrations;
* major runtime upgrades;
* architecture changes;
* security incidents.

---

# 107. Security Testing

Production hardening should be tested using controlled environments where practical.

Testing should include:

* port exposure;
* unauthorized access;
* privilege restrictions;
* TLS;
* secret handling;
* database access;
* health endpoint exposure;
* configuration permissions;
* deployment artifact integrity.

---

# 108. Vulnerability Scanning

Where available, production artifacts and infrastructure should be checked for known vulnerabilities.

Scanning should cover, as appropriate:

* OS packages;
* runtime dependencies;
* application dependencies;
* container images where used;
* infrastructure configuration.

Scanning results should be evaluated according to risk.

---

# 109. Security Scan Limitations

Automated scanners are not proof of complete security.

A clean scan does not guarantee:

* correct authorization;
* secure business logic;
* safe deployment;
* correct tenant isolation;
* correct synchronization security.

Security scanning complements, but does not replace, architectural and operational controls.

---

# 110. Penetration Testing

Where appropriate, controlled security testing should evaluate:

* public attack surface;
* authentication;
* authorization;
* tenant isolation;
* API security;
* deployment exposure;
* infrastructure configuration.

Testing must be authorized and must avoid disrupting production restaurant operations.

---

# 111. Security Incident Evidence

During a suspected compromise, preserve:

* relevant logs;
* deployment records;
* configuration changes;
* authentication records;
* network events;
* affected artifacts.

Evidence should be protected from unauthorized modification.

---

# 112. Security Incident Recovery

Security recovery should follow:

```text
Detect
  |
  v
Contain
  |
  v
Preserve Evidence
  |
  v
Assess Scope
  |
  v
Rotate Credentials
  |
  v
Rebuild Trusted Infrastructure
  |
  v
Restore Trusted Data
  |
  v
Validate Security
  |
  v
Resume Service
  |
  v
Monitor Closely
```

This is aligned with `DEP-20`.

---

# 113. Security Recovery Verification

After recovery:

* verify administrative access;
* verify service accounts;
* verify firewall;
* verify TLS;
* verify database roles;
* verify secrets;
* verify application artifact;
* verify monitoring;
* verify backups;
* verify branch synchronization.

Do not declare recovery complete before these checks pass.

---

# 114. Security Hardening and Performance

Security controls should be selected with the target deployment environment in mind.

FastFood ERP is intended to remain usable without requiring unnecessarily powerful hardware.

Therefore:

* avoid excessive background security scanning;
* avoid expensive health checks;
* avoid unnecessary encryption overhead where the trust boundary does not require it;
* avoid excessive logging;
* avoid unnecessary network proxies;
* use lightweight controls where equivalent protection is available.

Security must be strong without becoming operationally impractical.

---

# 115. Security Hardening and Availability

Security controls must not create avoidable outages.

Examples:

* certificate renewal must be monitored;
* firewall changes must be validated;
* secret rotation must be coordinated;
* authentication dependencies must be recoverable;
* security updates should be tested where practical.

Security changes should follow controlled deployment procedures.

---

# 116. Security Change Management

Security configuration changes should be treated as production changes.

Examples:

* firewall rules;
* SSH configuration;
* TLS configuration;
* database permissions;
* service accounts;
* secret rotation;
* OS security settings.

Changes should be:

* documented;
* reviewed where required;
* deployed through controlled processes;
* monitored after deployment.

---

# 117. Security Rollback

Security configuration changes should have a recovery strategy.

Before applying a potentially disruptive security change:

* record current configuration;
* validate the replacement configuration;
* preserve administrative recovery access;
* define rollback steps.

A firewall or authentication change must not lock all authorized administrators out without a recovery path.

---

# 118. Security Deployment Gates

Security-sensitive deployments should pass:

### Gate 1 — Artifact

Trusted artifact confirmed.

### Gate 2 — Configuration

Security configuration validated.

### Gate 3 — Access

Administrative and service access verified.

### Gate 4 — Network

Expected exposure verified.

### Gate 5 — Runtime

Non-root and permission model verified.

### Gate 6 — Secrets

Secrets loaded securely.

### Gate 7 — Monitoring

Security monitoring active.

### Gate 8 — Operational

Critical business functions remain available.

---

# 119. Security Verification Sequence

The recommended sequence is:

```text
Deploy
  |
  v
Verify Artifact
  |
  v
Verify Configuration
  |
  v
Verify Service Identity
  |
  v
Verify Network Exposure
  |
  v
Verify TLS
  |
  v
Verify Database Access
  |
  v
Verify Secrets
  |
  v
Verify Monitoring
  |
  v
Verify Business Functions
  |
  v
Accept Deployment
```

---

# 120. Security Failure Criteria

Security deployment verification fails when:

* unexpected public ports are exposed;
* application runs with excessive privileges;
* secrets are exposed;
* database becomes publicly accessible;
* TLS configuration is invalid;
* administrative access is uncontrolled;
* debug mode is enabled unexpectedly;
* security monitoring is unavailable;
* unauthorized service access is possible;
* tenant or branch isolation is compromised.

---

# 121. Security Hardening Checklist

## Operating System

* [ ] Supported OS version.
* [ ] Security updates applied.
* [ ] Unnecessary services removed or disabled.
* [ ] Administrative accounts reviewed.
* [ ] Root access restricted.
* [ ] SSH hardened.
* [ ] Time synchronization active.

## Network

* [ ] Firewall active.
* [ ] Required ports documented.
* [ ] Unnecessary ports blocked.
* [ ] Database private.
* [ ] Internal services private.
* [ ] Administrative access restricted.
* [ ] Outbound access controlled where practical.

## Application

* [ ] Application runs as non-root.
* [ ] Debug mode disabled.
* [ ] File permissions restricted.
* [ ] Upload directories protected.
* [ ] Runtime dependencies controlled.
* [ ] Error responses do not expose internals.

## Database

* [ ] PostgreSQL private.
* [ ] Application role restricted.
* [ ] Migration privileges controlled.
* [ ] Database credentials protected.
* [ ] Backups protected.
* [ ] Database monitoring active.

## Secrets

* [ ] No secrets in source control.
* [ ] Secrets loaded securely.
* [ ] Secrets excluded from logs.
* [ ] Rotation procedure available.
* [ ] Compromised credentials can be revoked.

## Deployment

* [ ] Artifact verified.
* [ ] Deployment identity controlled.
* [ ] Production deployment authorized.
* [ ] CI/CD credentials restricted.
* [ ] Configuration changes audited.

## Monitoring

* [ ] Security alerts active.
* [ ] Health monitoring active.
* [ ] Logs protected.
* [ ] Audit records available.
* [ ] Deployment correlation available.

---

# 122. Production Security Readiness

Production security readiness requires:

* hardened operating system;
* controlled administrative access;
* restricted network exposure;
* protected database;
* non-root application execution;
* protected secrets;
* secure TLS;
* controlled deployment artifacts;
* monitoring;
* security alerting;
* backup protection;
* recovery procedures;
* configuration baseline.

---

# 123. Operational Security Review

Before accepting a new production environment, verify:

```text
Who can access it?
        |
What can they access?
        |
Which ports are exposed?
        |
Which services are running?
        |
Which credentials exist?
        |
Where are secrets stored?
        |
Where is data stored?
        |
How is activity monitored?
        |
How is compromise recovered?
```

Every question should have a documented answer.

---

# 124. Periodic Security Review

Security hardening should be reviewed periodically and after significant infrastructure changes.

Review:

* OS packages;
* open ports;
* accounts;
* SSH keys;
* service privileges;
* database roles;
* secrets;
* TLS;
* firewall;
* dependencies;
* backups;
* monitoring;
* configuration drift.

---

# 125. Security Ownership

Production security responsibilities should be clearly assigned across:

* infrastructure administration;
* deployment;
* database administration;
* application operations;
* security response.

No critical security control should depend on an undocumented individual procedure.

---

# 126. Security Documentation

Production security configuration should be documented sufficiently for an authorized operator to:

* understand the environment;
* identify exposed services;
* recover administrative access;
* rotate credentials;
* rebuild infrastructure;
* restore services;
* verify security after recovery.

---

# 127. Security and Operational Simplicity

FastFood ERP should prefer:

```text
Strong
+
Simple
+
Auditable
+
Recoverable
```

over:

```text
Complex
+
Difficult to Operate
+
Difficult to Recover
```

Security controls that cannot be reliably operated are not effective security controls.

---

# 128. Core Security Invariants

The following rules are mandatory:

1. Production services must use least privilege.
2. Application processes must not run as root.
3. PostgreSQL must not be publicly exposed by default.
4. Internal services must remain private.
5. Only required network ports may be exposed.
6. Administrative access must be controlled.
7. Shared administrative accounts should be avoided.
8. Production secrets must not be committed to source control.
9. Secrets must not appear in logs or health responses.
10. Production debug mode must remain disabled.
11. TLS private keys must be protected.
12. Database runtime privileges must be limited.
13. Migration privileges should be separated from runtime privileges where practical.
14. Backups must be protected as sensitive data.
15. Deployment credentials must be separated from application credentials.
16. Production environments must be separated from development environments.
17. Security changes must be controlled and auditable.
18. Security monitoring must remain active during deployments.
19. Security incidents require containment and trusted recovery.
20. A restart does not make a compromised environment trusted.
21. Compromised credentials must be revoked and rotated.
22. Recovery environments must receive production-equivalent security controls.
23. Offline operation must not bypass authorization.
24. Branch synchronization must verify identity and integrity.
25. Security controls must be compatible with the target hardware and performance requirements.
26. Security configuration must be periodically reviewed.
27. Unexpected security configuration drift must be investigated.
28. Production deployment must include security verification.
29. Security failures affecting data integrity or access control must block deployment completion.
30. Security must remain recoverable as well as preventive.

---

# 129. Relationship With DEP-21

`DEP-21_Deployment_Monitoring_Health_Checks_and_Alerting.md` defines:

* health checks;
* readiness;
* deployment monitoring;
* operational metrics;
* alerts;
* deployment verification.

`DEP-22` defines the security controls that those monitoring mechanisms must observe.

The two documents therefore work together:

```text
DEP-22
Security Hardening
      |
      v
DEP-21
Security + Operational Monitoring
      |
      v
Detection
      |
      v
DEP-17 / DEP-20
Recovery
```

---

# 130. Relationship With DEP-15

`DEP-15` defines database migration safety.

`DEP-22` adds security requirements for:

* migration privileges;
* database access;
* migration credentials;
* database network exposure;
* migration auditability.

Database changes must continue to follow `DEP-15`.

---

# 131. Relationship With DEP-16

`DEP-16` defines release and zero-downtime deployment.

`DEP-22` ensures that:

* rolling deployment does not expose unnecessary services;
* mixed-version operation remains secure;
* deployment access is controlled;
* security configuration remains consistent across instances.

---

# 132. Relationship With DEP-17

`DEP-17` defines release rollback and recovery.

`DEP-22` adds:

* secure rollback;
* credential recovery;
* configuration recovery;
* security incident distinction;
* trusted environment requirements.

A security compromise may require more than application rollback.

---

# 133. Relationship With DEP-18

`DEP-18` defines scaling and capacity architecture.

Security controls must scale with the deployment.

New instances must inherit:

* security configuration;
* service identity;
* network restrictions;
* monitoring;
* secrets policy.

Scaling must not create accidental security gaps.

---

# 134. Relationship With DEP-19

`DEP-19` defines high availability and failure isolation.

Security hardening must not introduce unnecessary single points of failure.

Failover environments must preserve:

* network controls;
* authentication;
* secrets;
* TLS;
* database security;
* monitoring.

---

# 135. Relationship With DEP-20

`DEP-20` defines disaster recovery and business continuity.

`DEP-22` requires recovery environments to be secured before production traffic is restored.

The recovery sequence should include:

```text
Recover Infrastructure
        |
        v
Apply Security Baseline
        |
        v
Restore Trusted Data
        |
        v
Validate Security
        |
        v
Validate Application
        |
        v
Restore Traffic
```

---

# 136. Final Production Security Model

The target production security model is:

```text
                         Internet
                            |
                            v
                    [Firewall / Edge]
                            |
                            v
                    [TLS / Reverse Proxy]
                            |
                            v
                     [Application API]
                       /          \
                      /            \
                     v              v
                [Workers]      [Scheduler]
                     \              /
                      \            /
                       v          v
                       [Internal Services]
                              |
                              v
                         [PostgreSQL]
                              |
                              v
                       [Protected Backups]
```

Administrative access follows a separate controlled path.

Monitoring and security telemetry remain protected from public exposure.

---

# 137. Final Security Acceptance Criteria

A production deployment is security-accepted only when:

* the expected artifact is deployed;
* the operating system is within the supported security baseline;
* unnecessary services are disabled;
* network exposure matches the approved design;
* application processes use appropriate privileges;
* PostgreSQL remains protected;
* secrets are securely loaded;
* TLS is valid;
* debug mode is disabled;
* health endpoints expose no sensitive information;
* monitoring is active;
* security alerts are active;
* deployment access is auditable;
* no critical security configuration drift is detected.

---

# 138. Document Completion Criteria

This document is considered implemented when the production deployment process provides:

* documented OS hardening;
* documented network hardening;
* controlled administrative access;
* service isolation;
* least-privilege service accounts;
* secure PostgreSQL configuration;
* secure secret handling;
* TLS management;
* deployment artifact protection;
* dependency security controls;
* monitoring and security alerting;
* backup security;
* recovery security;
* configuration baseline;
* security verification;
* security incident recovery procedure.

---

# 139. Final Rules

FastFood ERP production deployment security follows these final rules:

1. Minimize the attack surface.
2. Expose only required services.
3. Keep internal services private.
4. Keep PostgreSQL private.
5. Use least privilege.
6. Do not run application services as root.
7. Protect administrative access.
8. Protect secrets.
9. Protect deployment credentials.
10. Use secure TLS configuration.
11. Disable production debug features.
12. Control filesystem permissions.
13. Control outbound network access where practical.
14. Use bounded timeouts and retries.
15. Protect queues and caches.
16. Protect monitoring infrastructure.
17. Secure offline branch synchronization.
18. Protect backups.
19. Keep environments separated.
20. Control configuration drift.
21. Patch supported components.
22. Monitor security-relevant events.
23. Verify security after every relevant deployment.
24. Treat security incidents differently from ordinary release failures.
25. Rebuild compromised environments from trusted sources.
26. Rotate compromised credentials.
27. Secure disaster recovery environments.
28. Test security controls periodically.
29. Keep security controls operationally simple.
30. Never trade away critical data, access-control, or credential security merely for deployment convenience.

---

# 140. Summary

`DEP-22` establishes the production security baseline for FastFood ERP deployment infrastructure.

The central principle is:

```text
Secure Deployment
        =
Secure Infrastructure
+
Secure Runtime
+
Secure Network
+
Secure Services
+
Secure Database
+
Secure Secrets
+
Secure Deployment Process
+
Security Monitoring
+
Recoverable Security
```

Production security is not limited to application code.

The operating system, network, runtime, database, deployment pipeline, credentials, monitoring system, backups, and recovery environment must all participate in the security model.

The final goal is a production environment that is:

```text
Hardened
+
Least Privileged
+
Minimally Exposed
+
Monitored
+
Auditable
+
Recoverable
```

while remaining practical for FastFood ERP's multi-branch, online/offline, performance-conscious operating model.

