# Security Operations

**Document ID:** OPS-17
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Category:** Operations
**Audience:** Security Engineers, Operations Engineers, Backend Engineers, Database Administrators, Incident Responders, System Administrators

## 1. Purpose

This document defines the operational procedures for security monitoring, security incident response, production hardening, privileged access management, vulnerability handling, and security verification.

Its objectives are to:

* Detect and investigate suspicious activity.
* Protect customer, employee, financial, inventory, and operational data.
* Enforce tenant and branch isolation.
* Reduce the attack surface of production infrastructure.
* Manage security vulnerabilities and configuration weaknesses.
* Respond to compromised credentials, unauthorized access, and suspected data exposure.
* Preserve evidence while containing security incidents.
* Verify that security controls remain effective after deployments, configuration changes, and recovery operations.

This document establishes operational requirements without mandating a specific cloud provider, security vendor, framework, or infrastructure topology.

## 2. Scope

This document covers:

* Security monitoring and logging.
* Authentication and authorization operations.
* Privileged and emergency access.
* Production infrastructure hardening.
* Secrets and credential management.
* Vulnerability and patch management.
* Dependency and artifact security.
* Network and service exposure.
* API abuse and suspicious traffic.
* Database, file-storage, and backup security.
* Security incident response.
* Security verification after releases and recovery.
* Security evidence, reporting, and continuous improvement.

Application security design and detailed implementation requirements remain governed by the relevant documents in `doc/11_Security`.

## 3. Related Documents

Maintain this document consistently with:

* `01_Operations_Architecture_Overview.md`
* `02_Production_Operations_Runbook.md`
* `03_Monitoring_and_Observability_Operations.md`
* `04_Alerting_and_Notification_Operations.md`
* `05_Incident_Management.md`
* `06_On_Call_and_Escalation_Management.md`
* `07_Backup_Verification_and_Restore_Operations.md`
* `08_Disaster_Recovery_Operations_Runbook.md`
* `09_Database_Operations.md`
* `10_Redis_Queue_and_Cache_Operations.md`
* `11_Backend_API_Operations.md`
* `12_Frontend_Operations.md`
* `13_Background_Worker_and_Scheduler_Operations.md`
* `15_File_Storage_and_Document_Operations.md`
* `16_Subscription_and_Data_Lifecycle_Operations.md`
* `18_Release_and_Change_Operations.md`
* `20_Operations_Invariants_and_Guardrails.md`

Relevant security design documents in `doc/11_Security`, incident procedures in `doc/14_Operations/05_Incident_Management.md`, and deployment procedures in `doc/10_Deployment` must also be followed.

## 4. Security Operations Principles

### 4.1 Least Privilege

Every user, service, worker, and operational tool must have only the permissions required for its assigned responsibilities.

Privileges must be reviewed periodically and revoked when no longer required.

### 4.2 Defense in Depth

Security must not depend on a single control.

Authentication, authorization, tenant isolation, network restrictions, secrets management, monitoring, and recovery safeguards must work together.

### 4.3 Verify Before Trusting

A successful login does not automatically authorize every action.

Authorization must be evaluated using the current identity, role, branch scope, tenant scope, subscription restrictions, and applicable business rules.

### 4.4 Preserve Evidence

Security investigations must preserve relevant records without unnecessarily exposing sensitive information or destroying evidence.

### 4.5 Secure by Default

New services, endpoints, infrastructure resources, files, and integrations must begin with the minimum required exposure and privileges.

### 4.6 Operational Safety

Security controls must protect business integrity and availability. Emergency actions must be proportionate to the risk and must not silently corrupt orders, payments, inventory, payroll, or cash-register records.

## 5. Security Ownership and Responsibilities

| Role                   | Responsibilities                                                                       |
| ---------------------- | -------------------------------------------------------------------------------------- |
| Security Owner         | Maintains security operational policy and risk decisions                               |
| Security Engineer      | Investigates security signals, coordinates response, and validates controls            |
| Operations Engineer    | Maintains infrastructure security, monitoring, and operational access                  |
| Backend Engineer       | Maintains API authorization, application safeguards, and secure service behavior       |
| Database Administrator | Protects database access, backups, integrity, and auditability                         |
| Release Owner          | Verifies security requirements before and after production releases                    |
| Incident Commander     | Coordinates major security incidents and response priorities                           |
| Business/Data Owner    | Evaluates business impact, retention requirements, and approved customer communication |
| Support Team           | Follows identity-verification procedures and escalates suspected security incidents    |

A person may perform multiple roles in a small team, but critical actions must still have appropriate authorization, accountability, and independent review where feasible.

## 6. Security Monitoring

### 6.1 Monitoring Objectives

Security monitoring must identify suspicious activity, control failures, unauthorized changes, and potential compromise.

Monitoring should cover:

* Authentication failures and suspicious login patterns.
* Unusual session creation or privilege use.
* Repeated authorization failures.
* Attempts to access another tenant or branch.
* Changes to roles, permissions, and privileged accounts.
* Unexpected API traffic or abuse patterns.
* Unusual refund, payment, cash-register, or inventory activity.
* Database and file-storage access anomalies.
* Secrets or credentials exposed through logs or configuration.
* Changes to security-sensitive configuration.
* Unexpected service exposure or firewall changes.
* Vulnerability scanner findings and security patch status.
* Backup and recovery control failures.
* Suspicious background-worker or scheduler activity.
* Unexpected changes to subscription restrictions or deletion jobs.

Monitoring must distinguish security signals from ordinary operational errors while retaining enough context for investigation.

### 6.2 Required Security Events

Where applicable, record events such as:

* Successful and failed authentication.
* Account lockout or other protective action.
* Password, credential, or multi-factor authentication changes.
* Session revocation.
* Privileged access grants and removals.
* Role and permission changes.
* Sensitive administrative actions.
* Tenant or branch authorization failures.
* Security configuration changes.
* File upload rejection for security reasons.
* Repeated rate-limit or abuse-control triggers.
* Secrets rotation.
* Security incident containment actions.
* Changes to retention holds and deletion permissions.
* Audit-log configuration or access changes.

Event coverage must be reviewed against the actual architecture and risk profile.

### 6.3 Log Quality

Security logs must be:

* Timestamped using a consistent time source.
* Attributable to a user, service, or authorized system actor where possible.
* Associated with a request, session, or operation identifier where appropriate.
* Sufficient to reconstruct the relevant action and authorization decision.
* Protected against unauthorized modification and deletion.
* Retained according to approved security and privacy policies.
* Searchable by authorized incident responders.

Logs must not contain plaintext passwords, session tokens, API secrets, private keys, or unnecessary sensitive payloads.

### 6.4 Monitoring Integrity

Security monitoring is itself a protected system.

Changes to alert rules, audit settings, logging permissions, and security monitoring integrations must be authorized and recorded.

Alert delivery failures, missing log streams, unexpected logging gaps, and disabled monitoring must generate appropriate operational signals.

An absence of alerts must not be treated as proof that no attack occurred.

## 7. Alerting and Triage

### 7.1 Severity Classification

Use the incident severity model established in `04_Alerting_and_Notification_Operations.md` and `05_Incident_Management.md`.

Security triage must consider:

* Whether unauthorized access is confirmed or suspected.
* The sensitivity and scope of potentially exposed data.
* Whether tenant boundaries may have been crossed.
* Whether privileged credentials may be compromised.
* Whether business records may have been altered.
* Whether the attack is ongoing.
* Whether containment could disrupt essential operations.
* Whether mandatory reporting or notification obligations may apply.

### 7.2 High-Priority Security Signals

Examples include:

* Confirmed cross-tenant data access.
* Unauthorized privileged-account activity.
* Suspected production-secret compromise.
* Evidence of unauthorized database modification.
* Unexpected access to sensitive files or backups.
* Security controls being disabled without authorization.
* Repeated unauthorized actions affecting multiple tenants.
* Suspected compromise of a production server or deployment identity.
* Unauthorized deletion of business records.
* Evidence of tampering with audit evidence.

These signals require prompt investigation and escalation according to impact and the incident-response policy.

### 7.3 Triage Procedure

1. Confirm the alert source and timestamp.
2. Identify affected systems, accounts, tenants, and branches.
3. Determine whether the event is ongoing.
4. Preserve relevant logs and audit evidence.
5. Assess likely confidentiality, integrity, and availability impact.
6. Check related events across application, infrastructure, database, and storage layers.
7. Assign severity and an incident owner.
8. Contain the activity when justified.
9. Record decisions and unresolved uncertainty.
10. Verify that the suspected threat is no longer active before closure.

A security alert must not be dismissed solely because the triggering request returned an error.

## 8. Authentication and Session Operations

### 8.1 Identity Verification

Administrative and support actions must use approved identity-verification procedures.

Support staff must not bypass authentication or reveal protected account information merely because a requester claims to own the account or restaurant network.

### 8.2 Session Security

Operational controls must support, as appropriate:

* Session expiry.
* Revocation of sessions after credential compromise.
* Revalidation of privileges after sensitive changes.
* Invalidation of stale authorization context.
* Secure handling of session identifiers.
* Protection against session fixation and theft according to application security requirements.

A permission change must take effect within the defined authorization consistency window.

### 8.3 Unfamiliar Devices

Where the application requires verification for unfamiliar devices, that process must be monitored and resistant to abuse.

Device identifiers alone must not be treated as strong proof of identity.

Offline devices must follow the approved device-registration and synchronization rules. An unverified device must not gain privileged production access merely because it can communicate with a branch network.

### 8.4 Credential Compromise

When a credential may be compromised:

1. Identify the credential owner and associated privileges.
2. Revoke or rotate the credential through the approved mechanism.
3. Revoke active sessions or tokens where appropriate.
4. Review recent activity for unauthorized actions.
5. Identify dependent services and scheduled jobs.
6. Update affected services without exposing replacement secrets.
7. Verify that the old credential no longer works.
8. Record the incident and follow-up actions.

Credential rotation must not leave dependent services in an unverified or partially operational state.

## 9. Authorization and Tenant Isolation

### 9.1 Authorization Boundaries

Authorization must consider all relevant boundaries:

* Restaurant network or tenant.
* Branch.
* User role.
* Explicit user permissions.
* Resource ownership.
* Subscription status and feature limits.
* Record lifecycle state.
* Sensitive-action approval requirements.

Frontend restrictions are not a substitute for server-side authorization.

### 9.2 Tenant and Branch Isolation Monitoring

Monitor for:

* Requests containing mismatched tenant or branch identifiers.
* Attempts to access records outside the user's scope.
* Inconsistent tenant identifiers in database queries or job payloads.
* Cross-tenant file-access attempts.
* Unauthorized export or report access.
* Background jobs executing with broader scope than required.
* Cache keys or shared resources that may expose data across tenants.

A suspected cross-tenant access event must be treated as a potential security incident even if the full extent is not yet known.

### 9.3 Verification After Changes

Security-sensitive releases must test:

* Authorized access to the intended tenant and branch.
* Denial of access to unauthorized tenants and branches.
* Permission changes taking effect as expected.
* Subscription restrictions applying to API and background operations.
* Export and file-access authorization.
* Audit records for denied and privileged actions.

## 10. Privileged Access Management

### 10.1 Administrative Accounts

Administrative accounts must be individually attributable and protected with stronger controls appropriate to their impact.

Shared administrator accounts should be avoided. Where a shared technical identity is unavoidable, its use must be restricted, monitored, and attributable through additional audit evidence.

### 10.2 Privilege Grants

A privileged-access request must specify:

* Requester and intended operator.
* Business or operational reason.
* Required permission and scope.
* Target environment and tenant scope, if applicable.
* Duration or expiry.
* Required approval.
* Verification and revocation plan.

Permanent broad access must not be granted solely for convenience.

### 10.3 Emergency Access

Emergency access must be restricted to documented scenarios.

Requirements:

* Strong authentication.
* Explicit authorization.
* Minimal necessary scope.
* Time limitation where feasible.
* Immediate audit recording.
* Post-use review.
* Prompt privilege revocation.

Emergency access must not become an undocumented alternative to normal access management.

### 10.4 Access Reviews

Review privileged access periodically and after:

* Staff role changes.
* Staff departure.
* Security incidents.
* Infrastructure migrations.
* Changes in operational ownership.
* Introduction of new services or external integrations.

Remove obsolete access promptly.

## 11. Production Infrastructure Hardening

### 11.1 General Requirements

Production systems must follow an approved hardening baseline.

The baseline should cover:

* Operating-system security updates.
* Removal or disabling of unnecessary services.
* Restricted network exposure.
* Host firewall rules.
* Secure remote administration.
* Administrative account management.
* File and directory permissions.
* Service-account privileges.
* Time synchronization.
* Log forwarding and retention.
* Endpoint or host security controls where appropriate.
* Secure configuration and startup behavior.
* Recovery access and emergency procedures.

The baseline must be compatible with the actual deployment architecture.

### 11.2 Network Exposure

Only required services should be reachable from each network boundary.

Operational review must verify:

* Publicly exposed ports.
* Administrative access restrictions.
* Reverse-proxy and application-service boundaries.
* Database and cache network accessibility.
* Internal worker and scheduler exposure.
* Firewall and security-group rules.
* TLS configuration for relevant network connections.
* Unintended development or diagnostic endpoints.

Databases, caches, and internal administrative interfaces must not be exposed publicly without an explicitly approved and secured design.

### 11.3 Server and Service Accounts

Application services should not run with unnecessary operating-system or database privileges.

Where feasible:

* Use dedicated service identities.
* Restrict write access to required paths.
* Separate deployment and runtime permissions.
* Prevent services from modifying their own trusted executable artifacts.
* Restrict interactive login for service identities.
* Rotate credentials using the approved process.
* Monitor unexpected privilege escalation.

### 11.4 Configuration Hardening

Production configuration must:

* Disable debug modes and development-only features.
* Prevent detailed internal errors from being exposed to users.
* Use secure defaults.
* Restrict administrative interfaces.
* Avoid embedded credentials.
* Apply approved TLS and cookie settings.
* Configure security headers where appropriate.
* Restrict cross-origin access to approved origins.
* Keep error reporting free of secrets and sensitive payloads.

Configuration must be validated before rollout and checked after deployment.

## 12. Secrets and Key Management

### 12.1 Secret Handling

Secrets include database credentials, API keys, signing keys, access tokens, private keys, and other authentication material.

Requirements:

* Do not commit secrets to source control.
* Do not include secrets in container images or frontend bundles.
* Do not place secrets in ordinary application logs.
* Restrict secret access to authorized identities.
* Use an approved secret-delivery mechanism appropriate to the deployment.
* Separate secrets by environment and purpose.
* Limit secret exposure in CI/CD systems.
* Monitor changes to critical secret configuration.

### 12.2 Rotation

Secret rotation must have an explicit procedure covering:

1. Authorization and scheduling.
2. Creation or issuance of the replacement credential.
3. Controlled distribution to dependent services.
4. Application of the replacement.
5. Verification of service operation.
6. Revocation of the old credential.
7. Verification that the old credential no longer works.
8. Audit recording and failure handling.

Where emergency rotation is required, prioritize containment while preserving enough operational capacity to investigate and recover.

### 12.3 Signing and Encryption Keys

Key rotation must consider data compatibility, token validity, encrypted data access, backup restoration, and rollback behavior.

Old keys must not be destroyed until required migration, retention, and recovery obligations are satisfied.

Key access and key-management events must be auditable.

## 13. Vulnerability and Patch Management

### 13.1 Vulnerability Sources

Security findings may originate from:

* Operating-system advisories.
* Application dependency scanners.
* Static analysis.
* Container or artifact scanning.
* Infrastructure configuration checks.
* External security reports.
* Penetration testing.
* Incident investigations.
* Vendor notifications.
* Internal code review.

All relevant findings must be recorded in an approved tracking system.

### 13.2 Prioritization

Prioritize remediation using severity, exploitability, exposure, available mitigations, affected assets, and business impact.

Internet-exposed critical vulnerabilities and vulnerabilities known to be actively exploited require urgent assessment.

A finding must not be considered harmless solely because its scanner severity is low if the affected component protects sensitive tenant data or privileged operations.

### 13.3 Remediation Workflow

1. Identify affected assets and versions.
2. Validate the finding and its applicability.
3. Assess exploitability and business impact.
4. Assign an owner and target remediation time.
5. Select an appropriate fix or mitigation.
6. Test the change.
7. Deploy through the approved release process.
8. Verify the vulnerability is resolved or adequately mitigated.
9. Record evidence and any accepted residual risk.
10. Reassess after material changes.

### 13.4 Exceptions

Risk acceptance must be explicit, scoped, time-limited where feasible, and approved by the authorized owner.

The record must include the reason for the exception, compensating controls, expiry or review date, and remediation plan.

An exception must not silently become permanent.

## 14. Dependency, Build, and Artifact Security

### 14.1 Dependency Controls

Production dependencies must come from approved sources and follow the project's dependency-management process.

Operational controls should include:

* Dependency inventory.
* Vulnerability scanning.
* Lockfile consistency.
* Review of unexpected dependency changes.
* Removal of unused dependencies.
* Verification of release provenance where supported.
* Timely handling of abandoned or compromised packages.

### 14.2 Build Artifacts

Release artifacts must be traceable to an approved source revision and build process.

Where supported, maintain artifact checksums, provenance records, and integrity verification.

Production must not run unreviewed local builds or unknown artifacts without an approved emergency procedure.

### 14.3 Compromised Dependency Response

If a dependency is suspected of compromise:

1. Identify affected versions and deployed artifacts.
2. Determine where and when they were used.
3. Preserve build and deployment evidence.
4. Assess potential secret exposure and unauthorized execution.
5. Contain affected releases or services.
6. Build and verify a trusted replacement.
7. Rotate potentially exposed credentials.
8. Investigate suspicious activity.
9. Record remediation and residual risk.

Replacing a package alone does not prove that a compromised environment is clean.

## 15. API Abuse and Application Threats

### 15.1 Abuse Monitoring

Monitor for suspicious request patterns, including:

* Repeated authentication failures.
* Credential-stuffing indicators.
* Excessive requests from an account or source.
* Enumeration of identifiers.
* Repeated authorization failures.
* Unexpected export volume.
* Large or unusual upload attempts.
* Invalid payload patterns.
* Repeated attempts to bypass subscription restrictions.
* Unusual administrative operations.
* Requests associated with automated abuse.

Monitoring must account for legitimate restaurant traffic spikes and shared network environments.

### 15.2 Rate Limits and Protective Controls

Rate limits, request-size limits, timeouts, and abuse controls must be configured according to the service's needs.

Controls must avoid unnecessarily disrupting legitimate POS operations, branch synchronization, and essential administrative actions.

Security exceptions must be narrow, documented, and temporary where possible.

### 15.3 Input and File Handling

Follow the approved application-security controls for:

* Input validation.
* Output encoding.
* Parameterized database access.
* Upload validation.
* File type and size restrictions.
* Malware scanning where appropriate.
* Archive extraction safeguards.
* Safe file delivery.
* Protection against server-side request forgery and other applicable threats.

Do not disable input or upload safeguards merely to resolve a production support issue.

## 16. Database, Cache, Queue, and Storage Security

### 16.1 Database

Database security operations must verify:

* Restricted network access.
* Least-privilege database accounts.
* Protected credentials.
* Encrypted connections where required.
* Auditable privileged actions.
* Backup access restrictions.
* Secure migration execution.
* Appropriate handling of production data during testing and troubleshooting.

Production data must not be copied into less-protected environments without an approved data-handling procedure.

### 16.2 Cache and Queue

Redis, queues, and other shared infrastructure must be protected against unauthorized access.

Operational controls must include:

* Network restrictions.
* Authentication and access control appropriate to the technology.
* Restricted administrative commands.
* Protection of sensitive queue payloads.
* Safe handling of delayed and repeated jobs.
* Review of authorization context in worker messages.
* Credential rotation.
* Monitoring for unusual access or data exposure.

A queue message must not be treated as proof that the originating user's permissions remain valid.

### 16.3 File Storage

File storage must enforce authorization independently of filenames, object identifiers, and frontend visibility.

Verify:

* Private-by-default storage where applicable.
* Tenant-scoped access.
* Controlled download authorization.
* Safe upload and processing.
* Restricted storage credentials.
* Secure temporary files.
* Retention and deletion controls.
* Backup protection.
* Access logging appropriate to risk.

See `15_File_Storage_and_Document_Operations.md`.

## 17. Security of Offline and Branch Devices

Branch devices may operate during connectivity interruptions and require a separate operational security model.

Requirements:

* Device registration must follow the approved identity process.
* Local data must be limited to what the device requires.
* Local storage must be protected according to device capability and data sensitivity.
* Credentials must not be shared through informal channels.
* Unfamiliar devices must not receive privileged access automatically.
* Revoked or compromised devices must be blocked from future synchronization.
* Offline records must be authenticated, integrity-checked, and reconciled.
* Local clocks and device identifiers must not be treated as sufficient proof of authorization.
* Security-relevant synchronization failures must be recorded.
* Device replacement and retirement must include credential revocation and local-data handling.

A compromised branch device must not be allowed to modify arbitrary tenants or branches after reconnecting.

## 18. Security Incident Response

### 18.1 Response Phases

Security incidents must follow the incident lifecycle:

1. Detection.
2. Triage.
3. Incident declaration.
4. Evidence preservation.
5. Containment.
6. Eradication.
7. Recovery.
8. Security verification.
9. Post-incident review.
10. Corrective-action tracking.

Use `05_Incident_Management.md` for the general incident process and the specific procedures below for security-focused response.

### 18.2 Initial Response

When a credible security incident is suspected:

1. Record the initial signal and timestamp.
2. Assign an incident owner.
3. Identify affected systems and data boundaries.
4. Preserve relevant logs, audit records, and deployment information.
5. Determine whether the activity is ongoing.
6. Select containment actions proportionate to the threat.
7. Notify the appropriate security and operational responders.
8. Establish a documented timeline of decisions and actions.

Do not delay reasonable containment while waiting for complete certainty when the potential impact is severe.

### 18.3 Containment Options

Depending on the incident, containment may include:

* Revoking compromised credentials or sessions.
* Disabling a compromised account or service identity.
* Restricting a vulnerable endpoint.
* Blocking malicious traffic.
* Isolating an affected host.
* Suspending a compromised integration.
* Pausing affected background jobs.
* Enabling the deletion emergency stop.
* Restricting sensitive administrative actions.
* Disabling a compromised release or routing traffic away from it.

Containment must account for essential business continuity and preserve evidence where feasible.

Do not shut down unrelated tenant operations without an impact-based justification.

### 18.4 Eradication and Recovery

Before restoring normal operation:

* Identify and address the root cause.
* Remove unauthorized access.
* Replace compromised secrets.
* Patch or reconfigure affected components.
* Verify the integrity of trusted artifacts.
* Assess unauthorized data changes.
* Restore from a verified source when necessary.
* Confirm tenant and branch isolation.
* Verify audit and monitoring functionality.
* Monitor for recurrence.

A restart, password change, or deployment rollback alone is not proof that an incident has been resolved.

### 18.5 Data Exposure Assessment

When unauthorized data access is suspected, determine:

* What data may have been accessed.
* Which tenants, branches, users, or business records were affected.
* The time window of exposure.
* Whether data was modified, exported, or deleted.
* Which evidence supports confirmed versus suspected impact.
* Whether legal, contractual, or regulatory notification obligations apply.

Only authorized owners should approve external incident statements or required notifications.

Do not make unsupported claims that no data was exposed.

## 19. Security Incident Scenarios

### 19.1 Suspected Cross-Tenant Access

1. Treat the event as a high-priority security investigation.
2. Identify the affected endpoint, resource, tenant, and branch.
3. Preserve authorization and request logs.
4. Restrict the faulty access path if necessary.
5. Determine whether the event involved reading, modification, export, or deletion.
6. Verify isolation across API, database, cache, file storage, and background jobs.
7. Patch and test the root cause.
8. Re-enable affected functionality only after verification.

### 19.2 Compromised Administrator Account

1. Revoke active sessions and credentials.
2. Restrict the account and review privilege grants.
3. Identify recent privileged operations.
4. Check for unauthorized role changes, exports, configuration changes, and deletions.
5. Rotate dependent credentials if exposure is plausible.
6. Recover affected state through approved procedures.
7. Restore access only after identity verification and remediation.

### 19.3 Suspected Secret Leak

1. Identify the exposed secret and its privileges.
2. Determine whether it reached source control, logs, artifacts, or external systems.
3. Revoke or rotate it.
4. Identify all dependent services.
5. Verify that the old secret no longer works.
6. Investigate potential use during the exposure window.
7. Remove the exposure from accessible locations where feasible.
8. Preserve the incident evidence and remediation record.

Removing a secret from the latest source revision does not prove that it is no longer exposed in history, logs, or artifacts.

### 19.4 Unauthorized Data Modification

1. Identify affected records and the time window.
2. Preserve database, application, and audit evidence.
3. Restrict the compromised write path.
4. Determine whether legitimate newer transactions depend on the affected records.
5. Recover or reconcile data using an approved method.
6. Validate financial totals, inventory balances, order state, and related records.
7. Verify that the attacker cannot repeat the modification.

Do not restore an entire database snapshot without evaluating the risk of overwriting legitimate newer transactions.

### 19.5 Ransomware or Host Compromise

1. Activate the appropriate incident-response and escalation process.
2. Isolate affected systems when justified.
3. Protect unaffected backups and recovery credentials.
4. Avoid destroying evidence through unnecessary cleanup or rebuilding.
5. Assess credential and lateral-movement exposure.
6. Use the disaster-recovery process if required.
7. Restore only from verified trusted sources.
8. Verify data integrity and security controls before returning systems to service.

## 20. Security Verification After Release or Recovery

Security verification is required after changes that affect trust boundaries or security-sensitive behavior.

Examples include:

* Authentication or authorization changes.
* Role and permission updates.
* Tenant-isolation changes.
* API routing or middleware changes.
* Database privilege changes.
* Secret rotation.
* Firewall or network configuration changes.
* Dependency upgrades.
* File-storage changes.
* Subscription lifecycle changes.
* Backup restoration or disaster recovery.
* Emergency incident remediation.

Verification must include relevant negative tests, not only successful authorized access.

The release or recovery owner must record the verification outcome and unresolved risks.

## 21. Operational Evidence and Reporting

Security operations must produce evidence sufficient to support investigations, reviews, and audit requirements.

Evidence may include:

* Security alerts and triage records.
* Incident timelines.
* Relevant audit logs.
* Access-review results.
* Vulnerability findings and remediation records.
* Patch and configuration verification.
* Secret-rotation evidence.
* Security test results.
* Release and deployment records.
* Recovery verification.
* Approved risk exceptions.
* Corrective-action tracking.

Evidence must be protected from unauthorized modification and access.

Reports should distinguish:

* Confirmed facts.
* Suspected activity.
* Unverified hypotheses.
* Completed actions.
* Outstanding risks.
* Required follow-up.

Avoid collecting unnecessary sensitive information merely because it might be useful in a future investigation.

## 22. Routine Security Operations Schedule

The exact frequency must be defined by the approved operational risk policy and system capabilities.

| Activity                             | Required cadence                                                         |
| ------------------------------------ | ------------------------------------------------------------------------ |
| Review critical security alerts      | Continuously through the established alerting and escalation process     |
| Check security-monitoring health     | Routine operational checks and after relevant changes                    |
| Review privileged-access changes     | After sensitive changes and during periodic access reviews               |
| Review critical vulnerabilities      | Promptly after detection or relevant advisories                          |
| Apply security updates               | According to approved severity-based targets                             |
| Review exposed network services      | Periodically and after infrastructure changes                            |
| Verify backup access controls        | During backup verification and security reviews                          |
| Test incident-response procedures    | Periodically and after significant process changes                       |
| Verify tenant-isolation controls     | In relevant security tests and after authorization changes               |
| Review risk exceptions               | At the documented expiry or review date                                  |
| Review security incidents and trends | After incidents and during periodic security reviews                     |
| Verify production hardening          | At provisioning, after significant changes, and during scheduled reviews |

A schedule must have an owner and evidence of completion. An activity that has no recorded owner or completion evidence must not be assumed to have occurred.

## 23. Security Operations Readiness Checklist

* [ ] Security ownership and escalation paths are documented.
* [ ] Relevant security events are logged.
* [ ] Logs exclude secrets and unnecessary sensitive payloads.
* [ ] Monitoring and alert delivery are verified.
* [ ] Tenant and branch isolation controls are tested.
* [ ] Privileged accounts are individually attributable where feasible.
* [ ] Emergency access is restricted and auditable.
* [ ] Secrets are centrally controlled through an approved mechanism.
* [ ] Credential rotation procedures are documented and tested.
* [ ] Production services use least-privilege identities.
* [ ] Publicly exposed ports and services are reviewed.
* [ ] Debug and development-only features are disabled in production.
* [ ] Vulnerability findings have owners and remediation targets.
* [ ] Release artifacts are traceable to approved source and build processes.
* [ ] Database, cache, queue, and storage access is restricted.
* [ ] Offline device and synchronization security is defined.
* [ ] Security incident procedures are available to responders.
* [ ] Containment and recovery steps have been tested.
* [ ] Data exposure assessment and notification ownership are documented.
* [ ] Backup and disaster-recovery procedures preserve security controls.
* [ ] Post-release security verification is required where applicable.
* [ ] Security exceptions are approved and reviewed.
* [ ] Evidence retention and access controls are defined.
* [ ] Corrective actions are tracked through completion.

## 24. Mandatory Security Operations Invariants

1. Production security controls must have documented ownership.
2. Least privilege must apply to users, services, workers, and operators.
3. Authentication must not substitute for authorization.
4. Tenant isolation must be enforced server-side.
5. Branch permissions must be evaluated at applicable authorization boundaries.
6. Subscription restrictions must not be bypassed by background jobs.
7. Security-sensitive actions must be attributable.
8. Security logs must not contain plaintext credentials or tokens.
9. Monitoring configuration must be protected against unauthorized changes.
10. Missing monitoring data must not be interpreted as proof of safety.
11. High-impact security signals must follow documented escalation paths.
12. Security incidents must preserve relevant evidence where feasible.
13. Containment actions must be proportionate to the assessed threat.
14. Recovery must not begin normal operation before required verification.
15. A service restart alone must not establish that a compromise is resolved.
16. Privileged access must be explicitly authorized.
17. Emergency access must be limited, recorded, and reviewed.
18. Obsolete access must be revoked promptly.
19. Production network exposure must be limited to approved services.
20. Administrative interfaces must have appropriate access restrictions.
21. Debug-only features must not be unintentionally enabled in production.
22. Secrets must not be embedded in frontend assets or public artifacts.
23. Secret rotation must include dependent-service verification.
24. Old credentials must be revoked when rotation is complete.
25. Critical vulnerabilities must be assessed and prioritized promptly.
26. Risk exceptions must be explicit and reviewed.
27. Dependency changes must follow the approved development and release process.
28. Production artifacts must be traceable to trusted build inputs.
29. Compromised dependencies require impact assessment beyond package replacement.
30. API abuse controls must protect legitimate business operations.
31. File access must be authorized independently of filenames and object identifiers.
32. Database privileges must be restricted to required operations.
33. Cache and queue infrastructure must not be publicly exposed without approved safeguards.
34. Queue messages must not be trusted as proof of current authorization.
35. Offline devices must not gain privileged access solely from device identifiers.
36. Offline synchronization must preserve tenant isolation and record integrity.
37. Suspected cross-tenant access must be investigated as a security incident.
38. Credential compromise must trigger appropriate revocation and activity review.
39. Unauthorized data modification must be reconciled using an integrity-preserving procedure.
40. Backup and recovery credentials must be protected from compromised production systems where feasible.
41. Restored systems must receive appropriate security verification before production use.
42. Security-sensitive releases must include relevant negative authorization tests.
43. Security evidence must be access-controlled and retained under approved policy.
44. External incident communications must be authorized and evidence-based.
45. Security metrics must avoid unnecessary sensitive or high-cardinality labels.
46. Alert suppression must not silently disable required security detection.
47. Emergency stop mechanisms must be authorized and auditable.
48. Corrective actions must have owners and tracked completion.
49. Changes to security controls must follow documented change management.
50. Any suspected violation of tenant isolation, privileged access, or data integrity must be evaluated promptly for incident escalation.

## 25. Acceptance Criteria

This document is operationally complete when:

* Security monitoring, alerting, and triage responsibilities are defined.
* Authentication, authorization, and tenant-isolation controls have operational verification procedures.
* Production hardening and secrets management have documented processes.
* Vulnerability findings are prioritized, assigned, and tracked.
* Security incidents can be contained, investigated, and recovered from using approved runbooks.
* Security evidence is protected and available to authorized responders.
* Security verification is included in relevant release and recovery workflows.
* The readiness checklist in Section 23 is used before production approval.
* The mandatory invariants in Section 24 are preserved through implementation, testing, and operations.

**End of Document**

