# Operations Invariants and Guardrails

**Document ID:** OPS-20
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Category:** Operations
**Repository Path:** `doc/14_Operations/20_Operations_Invariants_and_Guardrails.md`

---

## 1. Purpose

This document defines the mandatory operational invariants, safety boundaries, and guardrails that apply across the FastFood ERP production environment.

Its purpose is to ensure that routine operations, incident response, releases, infrastructure changes, recovery procedures, and administrative actions preserve:

* Business data integrity.
* Restaurant-network and branch isolation.
* Financial correctness.
* Inventory consistency.
* Authentication and authorization.
* Service reliability.
* Offline transaction integrity.
* Backup and recovery readiness.
* Subscription and data-lifecycle correctness.
* Operational accountability.
* Sustainable resource utilization.
* Auditability and evidence preservation.

These rules apply to human operators, administrators, developers performing operational actions, automated jobs, deployment processes, background workers, and AI-assisted operational tools.

## 2. Scope

This document applies to all production operations and any nonproduction activity that could affect production systems, production data, security, or recovery readiness.

It covers:

1. Business-critical data protection.
2. Identity, access, and tenant isolation.
3. Orders, payments, inventory, and cash registers.
4. Offline operation and synchronization.
5. Infrastructure and dependency management.
6. Monitoring, alerting, and incident response.
7. Backup, restore, and disaster recovery.
8. Releases, migrations, and configuration changes.
9. Subscription enforcement and data lifecycle.
10. File storage and document management.
11. Background jobs, queues, and schedulers.
12. AI runtime and automated decisions.
13. Capacity, cost, and resource controls.
14. Audit evidence and operational accountability.
15. Exception management and policy enforcement.

Detailed procedures remain in their respective Operations documents. This document defines the cross-cutting rules those procedures must obey.

## 3. Normative Language

The following terms have specific meanings.

* **MUST:** A mandatory requirement. It cannot be bypassed through ordinary operational discretion.
* **MUST NOT:** A prohibited action.
* **SHOULD:** A strong recommendation. Any deviation requires a documented reason and risk assessment.
* **SHOULD NOT:** An action to avoid unless a documented exception justifies it.
* **MAY:** An optional action permitted when applicable controls are satisfied.

A requirement marked MUST or MUST NOT may only be changed through the project's formally approved policy or architecture change process, where the requirement is legitimately changeable.

Emergency conditions do not automatically authorize violating a mandatory safety boundary.

## 4. Relationship with Other Documents

This document is the cross-cutting operational guardrail reference.

It must remain consistent with:

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
* `14_AI_Runtime_Operations.md`
* `15_File_Storage_and_Document_Operations.md`
* `16_Subscription_and_Data_Lifecycle_Operations.md`
* `17_Security_Operations.md`
* `18_Release_and_Change_Operations.md`
* `19_Capacity_Cost_and_Resource_Operations.md`

Architecture, business requirements, security policies, and approved decisions define the system-specific constraints that operations must preserve.

If documents conflict, operators MUST NOT resolve the conflict by choosing whichever procedure is easiest or fastest. They must follow the approved documentation governance process, assess immediate risks, and obtain an authoritative decision from the responsible owner.

Where a conflict creates a material risk to data integrity, security, or financial correctness, the affected action MUST be paused until a safe, authorized path is established.

## 5. Foundational Operational Principles

### 5.1 Protect authoritative business state

The system's authoritative business records must remain consistent across services, databases, queues, caches, files, and offline clients.

A dashboard, cached value, notification, log entry, or AI prediction must not be treated as proof that an authoritative transaction completed.

### 5.2 Fail safely

When a critical precondition cannot be verified, the system or operator must avoid irreversible actions until the uncertainty is resolved.

Failing safely does not always mean shutting down the entire service. It means restricting the affected operation or capability while preserving safe and authorized functionality where possible.

### 5.3 Preserve accountability

Every material production action must have an identifiable actor or accountable automation identity, an authorized purpose, and sufficient evidence to reconstruct what happened.

### 5.4 Minimize blast radius

An operational action must affect only the intended resources, tenants, branches, environments, or records.

Broad changes require broader validation and stronger approval.

### 5.5 Verify outcomes

A successful command, deployment, restart, API response, or job execution does not independently prove that the intended business outcome is correct.

Recovery and completion must be established through relevant technical and business checks.

## 6. Identity, Access, and Tenant Isolation

All operational activities MUST follow these rules:

1. Every user and automation identity MUST use authorized access.
2. Privileged access MUST be limited to the minimum permissions necessary.
3. Shared administrative credentials MUST NOT be used where accountable individual or service identities are supported.
4. Production access MUST be separated from ordinary development access according to the approved access model.
5. Tenant and branch authorization MUST be enforced by trusted server-side controls.
6. A client-supplied tenant ID, branch ID, file ID, object ID, or URL MUST NOT independently establish authorization.
7. Operational tooling MUST preserve tenant and branch isolation.
8. Emergency access MUST be restricted, accountable, and reviewed.
9. Credentials, tokens, private keys, and secrets MUST NOT be written to ordinary logs, tickets, or incident reports.
10. Access grants and revocations MUST be recorded and verified where auditability is required.

An operational shortcut MUST NOT bypass tenant isolation, role permissions, authentication, or authorization, even during an incident.

If isolation cannot be verified, the affected cross-tenant or cross-branch action MUST be blocked until the access boundary is established.

## 7. Business Data Integrity

### 7.1 General data rules

11. Authoritative business records MUST NOT be changed outside approved business and data-management procedures.
12. Business records MUST NOT be deleted merely to simplify troubleshooting.
13. Destructive data operations MUST have a verified target, an authorized purpose, and an appropriate recovery or irreversibility assessment.
14. Data migrations MUST preserve required records, relationships, constraints, and historical meaning.
15. Data repair MUST be traceable to the original issue, the intended correction, the approval where required, and the resulting state.
16. Duplicate processing MUST be prevented or safely detected for operations that can create financial or inventory effects.
17. Uncertain transaction outcomes MUST be investigated before a potentially duplicating retry.
18. Logs and caches MUST NOT be treated as substitutes for authoritative records.

### 7.2 Orders and payments

19. Accepted orders MUST NOT be silently discarded during deployment, recovery, queue processing, or synchronization.
20. Payment and refund operations MUST follow their authorized business workflows.
21. A timeout or missing response MUST NOT be interpreted automatically as proof that a payment or refund failed.
22. Repeated payment or refund attempts MUST use the applicable idempotency, reconciliation, or duplicate-prevention controls.
23. Financial discrepancies MUST be investigated and documented rather than concealed through arbitrary record edits.
24. A technical rollback MUST NOT be assumed to reverse external payment-provider effects or other irreversible business actions.

### 7.3 Inventory and recipes

25. Inventory operations MUST preserve the approved stock-integrity rules, including the prohibition on negative stock.
26. Inventory adjustments MUST follow authorized correction procedures and retain required evidence.
27. Recipe changes and historical recipe records MUST follow the approved approval, versioning, and archival rules.
28. Inventory deductions MUST NOT be repeated merely because a response, notification, or downstream job is missing.
29. Inventory reconciliation MUST consider pending and offline transactions before declaring a discrepancy resolved.

### 7.4 Cash registers and financial reconciliation

30. Cash-register opening, closing, handover, correction, and reopening MUST follow their authorized procedures.
31. Required cashier confirmation, shortage handling, and approval controls MUST NOT be bypassed for convenience.
32. Financial history MUST NOT be silently overwritten to make reports appear consistent.
33. Corrections MUST retain sufficient information to identify the original state, corrected state, actor, reason, and applicable approval.
34. Technical service recovery MUST NOT be treated as proof that cash balances or financial records are reconciled.

## 8. Offline Operation and Synchronization

Offline operation is a supported business condition and MUST be treated as a first-class operational concern.

35. Accepted offline transactions MUST be preserved until their synchronization and reconciliation obligations are satisfied.
36. Synchronization MUST use the approved identity, idempotency, ordering, and conflict-resolution mechanisms.
37. Retrying synchronization MUST NOT create duplicate orders, payments, stock deductions, or cash-register effects.
38. A device MUST NOT be allowed to bypass required authorization merely because it is offline.
39. New-device enrollment and access MUST follow the approved device-verification rules.
40. Conflicting offline and server-side records MUST be resolved using approved business rules rather than arbitrary last-write-wins behavior where that would corrupt business meaning.
41. A recovery procedure MUST account for transactions created or queued during the outage.
42. Operators MUST NOT clear local transaction queues as a generic troubleshooting measure without an approved, verified recovery process.
43. Offline recovery MUST be rate-limited or otherwise controlled when unrestricted synchronization could overload production dependencies.

A branch returning online does not prove that all its transactions have been synchronized correctly. Recovery completion requires appropriate reconciliation evidence.

## 9. Production Infrastructure and Dependencies

44. Production infrastructure changes MUST follow the approved change-management procedure, except for explicitly authorized emergency actions.
45. Resource changes MUST consider downstream limits and dependencies.
46. Application instances MUST NOT be scaled blindly when the database or another shared dependency is already saturated.
47. Service restarts MUST NOT be treated as a complete resolution without verifying the original failure condition and business impact.
48. Infrastructure cleanup MUST NOT remove resources whose ownership, dependencies, retention obligations, or recovery purpose remain uncertain.
49. Production secrets MUST be managed through approved secret-handling mechanisms.
50. Configuration changes MUST be validated for compatibility, security, and operational impact.
51. Critical services MUST have documented health checks and meaningful recovery criteria.
52. Shared infrastructure changes MUST account for their potential impact on every dependent service and tenant.

If a dependency fails, the response must follow the approved degradation behavior. It must not silently corrupt data or falsely report that a critical business transaction succeeded.

## 10. Database, Cache, and Queue Guardrails

53. Database schema changes MUST follow approved migration procedures.
54. Destructive migrations MUST include explicit impact assessment and a recovery strategy appropriate to the change.
55. Database backups MUST NOT be assumed restorable without the required verification.
56. Connection-pool changes MUST consider aggregate connection consumption across all relevant processes.
57. Long-running transactions, lock contention, and query saturation MUST be investigated before adding concurrency.
58. Cache invalidation MUST preserve business correctness and authorization.
59. Cache data MUST NOT override authoritative business state unless the architecture explicitly defines and safeguards that behavior.
60. Background jobs with business effects MUST be idempotent or equivalently protected against repeated execution.
61. Retry policies MUST be bounded and designed to avoid retry storms.
62. Permanently failed jobs MUST remain observable and subject to an approved investigation or reconciliation process.
63. Scheduler execution MUST be coordinated where duplicate execution could produce harmful effects.
64. Queue draining and backlog recovery MUST respect downstream capacity and transaction dependencies.

An empty queue is not proof that every job completed correctly. Failed, discarded, duplicate, and partially completed jobs must be accounted for where relevant.

## 11. Monitoring, Alerts, and Incidents

65. Critical production services MUST have monitoring appropriate to their operational risks.
66. Monitoring MUST distinguish technical health from business correctness.
67. Alerts MUST have an actionable response path or a documented informational purpose.
68. Alert acknowledgement MUST NOT be confused with resolution.
69. Incident severity MUST reflect actual or credible potential business, security, data-integrity, or availability impact.
70. Material incidents MUST have an accountable incident owner.
71. Incident actions MUST preserve sufficient evidence for investigation and follow-up.
72. Security incidents MUST follow the approved security incident process.
73. Customer or stakeholder communications MUST distinguish confirmed facts from estimates and unverified hypotheses.
74. Incident closure MUST require appropriate recovery verification and documented unresolved risks.
75. Repeated incidents MUST be reviewed for systemic causes and corrective actions.

Operators MUST NOT suppress an alert solely because it is inconvenient or exposes an unresolved operational problem.

Monitoring may be adjusted to correct false positives, but the change must preserve adequate detection coverage and be documented where material.

## 12. Backup, Restore, and Disaster Recovery

76. Critical business data MUST be covered by the approved backup and recovery strategy.
77. Backup completion status MUST NOT be treated as proof that a restore will succeed.
78. Restore tests MUST verify technical consistency and the business records relevant to the recovery scenario.
79. Recovery objectives MUST be based on approved requirements and demonstrated capability.
80. Production restoration MUST follow the authorized restore procedure.
81. Recovery-point selection MUST consider data consistency, business impact, and known missing transactions.
82. Disaster recovery MUST prevent conflicting authoritative writers and uncontrolled split-brain operation.
83. Traffic MUST NOT be switched to a recovery environment until the required validation and authorization conditions are met.
84. Recovery completion MUST account for database state, files, dependencies, permissions, and critical business workflows as applicable.
85. Failback MUST be treated as a controlled change with its own validation and recovery plan.
86. Backup retention MUST follow approved retention and legal or business requirements.
87. Restored data MUST remain protected by the required access controls and security configuration.

A recovered server is not necessarily a recovered business system. The authoritative data state and critical workflows must be validated before declaring full recovery.

## 13. Release and Change Guardrails

88. Production releases MUST have a traceable change record and required approvals.
89. Release artifacts MUST be identifiable and verified according to the approved build and integrity process.
90. Deployments MUST consider compatibility between frontend, backend, database schema, workers, schedulers, and offline clients.
91. Database migrations MUST account for old and new application versions when rolling deployment or rollback requires compatibility.
92. Feature flags MUST NOT replace authentication or authorization.
93. Rollback MUST NOT be assumed to reverse irreversible database changes or external side effects.
94. Emergency changes MUST be recorded, validated, and reviewed according to the emergency change process.
95. Deployment success MUST NOT be declared solely from a successful command or pipeline status.
96. Post-release verification MUST cover critical technical and business behavior appropriate to the change.
97. Failed releases MUST be contained using the approved rollback, roll-forward, or recovery strategy.
98. Changes that weaken a mandatory guardrail MUST NOT be deployed without an approved policy change and required risk controls.

## 14. Subscription and Data Lifecycle

99. Subscription restrictions MUST follow the approved subscription state and entitlement model.
100. A subscription-expiry event MUST NOT be treated as authorization to immediately delete customer data.
101. The approved retention period and eligibility calculation MUST be applied consistently.
102. Destructive lifecycle jobs MUST revalidate current eligibility immediately before the destructive operation.
103. Reactivation, legal holds, and other applicable lifecycle exceptions MUST be checked before deletion.
104. Lifecycle jobs MUST be idempotent or otherwise protected against duplicate and concurrent execution.
105. Partial deletion MUST be observable and reconciled.
106. A deletion process MUST NOT claim complete deletion if retained backups or other governed copies remain.
107. Access restrictions MUST NOT be implemented by corrupting, arbitrarily deleting, or rewriting customer records.
108. Lifecycle policy uncertainty MUST block the destructive operation until the rule is clarified.

Data lifecycle operations MUST remain consistent with `16_Subscription_and_Data_Lifecycle_Operations.md` and `15_File_Storage_and_Document_Operations.md`.

## 15. File and Document Guardrails

109. Private files MUST remain private by default.
110. File identifiers and storage paths MUST NOT independently grant access.
111. Uploads MUST pass the required validation and security checks before becoming available.
112. File access MUST enforce tenant, branch, role, and record-level authorization as applicable.
113. Cleanup MUST verify ownership, lifecycle eligibility, retention holds, and required dependencies.
114. File metadata and content MUST be reconciled after relevant restore or migration operations.
115. File migrations MUST NOT delete the source before the destination has been verified according to the approved migration procedure.
116. Public exposure MUST NOT be used as a shortcut for troubleshooting private file access.
117. File storage pressure MUST NOT justify deleting required business documents or recovery evidence.

## 16. AI and Automated Decision Guardrails

118. AI output MUST NOT independently override authoritative ERP business state.
119. AI model artifacts MUST be identified and verified according to the approved deployment process.
120. AI runtime health MUST be assessed separately from model quality.
121. AI failures MUST follow the documented fallback or degradation policy.
122. Optional AI workloads MUST NOT be allowed to exhaust resources required by core ERP operations.
123. AI-assisted operational recommendations MUST remain subject to the required human approval and access controls.
124. AI-generated explanations MUST NOT be treated as verified incident evidence without supporting observations.
125. AI rollback MUST NOT be assumed to reverse business actions already performed using earlier model outputs.
126. Model updates MUST be evaluated for resource impact, compatibility, and operational risk.
127. AI systems MUST preserve tenant and branch isolation and applicable data-handling requirements.

## 17. Capacity, Cost, and Resource Guardrails

128. Capacity decisions MUST be based on measured behavior or documented assumptions.
129. Critical resources MUST have appropriate capacity monitoring and an accountable owner.
130. Scaling MUST consider the capacity of downstream dependencies.
131. Automatic scaling MUST have defined bounds and failure behavior.
132. Cost optimization MUST NOT bypass security, data integrity, retention, or recovery requirements.
133. Required backups MUST NOT be disabled solely to reduce cost.
134. Shared-cost allocation MUST distinguish estimates from directly measured values.
135. Resource removal MUST include ownership and dependency checks.
136. Nonproduction resource cleanup MUST follow documented lifecycle controls.
137. Cost anomalies MUST be investigated before being attributed to normal growth.
138. Capacity claims MUST identify their validated workload and test conditions.
139. Offline recovery and queue catch-up MUST remain within safe resource limits.
140. Material resource changes MUST be validated and recorded.

These rules are consistent with `19_Capacity_Cost_and_Resource_Operations.md`.

## 18. Logging, Audit, and Evidence

141. Material operational actions MUST be attributable to an actor or accountable automation identity.
142. Audit evidence MUST be protected against unauthorized alteration and access.
143. Logs MUST NOT contain unnecessary secrets or sensitive customer information.
144. Evidence retention MUST follow approved security, operational, and business requirements.
145. Operational records MUST distinguish confirmed facts, estimates, assumptions, and unresolved questions.
146. Material manual corrections MUST have sufficient justification and traceability.
147. Missing evidence MUST be acknowledged rather than replaced with invented certainty.
148. Incident and recovery reports MUST record known limitations and remaining risks.
149. Access to evidence MUST follow least-privilege principles.
150. Operational reports MUST NOT claim that a control, backup, recovery, or deletion succeeded without sufficient supporting evidence.

## 19. Emergency Operations

Emergency actions exist to reduce immediate harm. They do not remove accountability or make unsafe actions acceptable.

Before an emergency action, the operator MUST establish, to the extent reasonably possible:

* The immediate problem and affected scope.
* The operator's authority.
* The intended action and expected benefit.
* The most important risks.
* The expected effect on data integrity and security.
* The safest available alternative.
* The conditions for stopping or reversing the action.

When prior approval is impractical, the approved emergency procedure may permit a narrowly scoped action by an authorized responder. Such action MUST be recorded and reviewed afterward.

An emergency MUST NOT be used as a general justification to:

* Bypass tenant isolation.
* Expose secrets or private data.
* Falsify business records.
* Delete uncertain data.
* Disable essential security controls without an approved containment strategy.
* Perform unverified financial corrections.
* Start conflicting authoritative writers.
* Conceal an operational mistake.

If an action cannot be performed safely, the operator must contain the affected capability, escalate, and obtain an authorized decision.

## 20. Exceptions and Policy Changes

### 20.1 Exception eligibility

An exception may be considered only when:

* The affected rule is legally and architecturally eligible for exception.
* The business need is documented.
* The risk is assessed.
* An authorized owner approves it.
* The scope and duration are limited.
* Compensating controls are identified.
* Validation and monitoring requirements are defined.
* The exception has an expiration or review date where applicable.

An exception MUST NOT override a requirement that is legally mandatory or a safety boundary that the architecture explicitly prohibits bypassing.

### 20.2 Exception record

Each approved exception must include:

* Exception ID.
* Requester and accountable owner.
* Rule or document affected.
* Reason for the exception.
* Systems, tenants, branches, or environments in scope.
* Risk assessment.
* Approval record.
* Compensating controls.
* Start and expiration dates.
* Monitoring and verification requirements.
* Revocation conditions.
* Closure evidence.

### 20.3 Expiration and revocation

Expired exceptions MUST NOT continue automatically.

The responsible owner must verify whether the exception is still needed, renew it through the approved process, or remove it.

If an exception creates an unexpected security, data-integrity, financial, or availability risk, it must be restricted or revoked according to the incident and change-management procedures.

## 21. Guardrail Enforcement

Guardrails should be enforced through a combination of:

* Application validation and authorization.
* Database constraints and transaction boundaries.
* Automated tests.
* Deployment checks.
* Configuration validation.
* Access controls.
* Monitoring and alerting.
* Approved runbooks.
* Audit trails.
* Operational reviews.

Documentation alone is insufficient for high-risk rules that can reasonably be enforced technically.

Where technical enforcement is not yet available, the responsible owner must document the manual control, its verification method, and the plan for addressing the gap.

A missing automated control does not make the underlying requirement optional.

## 22. Guardrail Violation Response

When a mandatory invariant is violated or suspected to be violated:

1. **Contain:** Prevent additional harm using the safest authorized action.
2. **Assess:** Identify affected systems, records, tenants, branches, and business workflows.
3. **Preserve:** Retain relevant logs, audit records, transaction identifiers, and other evidence.
4. **Escalate:** Notify the accountable owner and incident responders according to severity.
5. **Correct:** Apply an approved repair, reconciliation, rollback, or recovery procedure.
6. **Verify:** Confirm technical state and relevant business outcomes.
7. **Document:** Record the timeline, impact, cause, decisions, and remaining uncertainty.
8. **Prevent recurrence:** Assign corrective actions, owners, and completion criteria.

A violation MUST NOT be hidden by changing monitoring thresholds, deleting logs, editing reports, or closing an incident without adequate evidence.

If customer data or financial records may have been affected, the response must explicitly document what is known, what remains uncertain, and what verification is still required.

## 23. Operational Readiness Checklist

Before approving a production operating model or a material operational change, verify:

* [ ] Critical resources and services have accountable owners.
* [ ] Tenant and branch isolation are enforced.
* [ ] Privileged access and emergency access are controlled.
* [ ] Orders, payments, refunds, and inventory have safe retry and reconciliation behavior.
* [ ] Offline transaction preservation and synchronization are defined.
* [ ] Database, queue, and scheduler operations preserve transaction correctness.
* [ ] Monitoring covers critical technical and business failure conditions.
* [ ] Incident and escalation procedures are available.
* [ ] Backups and restore procedures are verified.
* [ ] Disaster recovery prevents conflicting authoritative writers.
* [ ] Releases and migrations have compatibility and recovery controls.
* [ ] Subscription and data deletion rules are enforced.
* [ ] File access and lifecycle operations preserve authorization and retention.
* [ ] AI workloads cannot override authoritative business state.
* [ ] Capacity and cost controls preserve essential reliability.
* [ ] Operational actions produce appropriate audit evidence.
* [ ] Exceptions are approved, scoped, and time-bound.
* [ ] Violations have a defined containment and remediation process.
* [ ] Related documents remain consistent and discoverable.

## 24. Compliance Review

The Operations owner must establish a review process appropriate to the platform's risk and maturity.

The review must assess:

* Whether the invariants remain accurate.
* Whether the relevant controls exist.
* Whether technical enforcement is sufficient.
* Whether manual controls are being performed.
* Whether incidents reveal repeated guardrail violations.
* Whether exceptions remain valid.
* Whether related documents conflict.
* Whether corrective actions have been completed and verified.

Reviews must be performed after material incidents or architecture changes and at the scheduled documentation review interval.

Findings must be recorded with a severity, accountable owner, target date, and acceptance criteria.

## 25. Mandatory Summary of Non-Negotiable Rules

The following rules summarize the platform's highest-priority operational boundaries:

1. Never bypass tenant or branch authorization.
2. Never treat an uncertain transaction outcome as proof of failure.
3. Never retry a business-changing operation without appropriate duplicate protection.
4. Never silently discard accepted offline transactions.
5. Never permit negative stock contrary to the approved inventory rules.
6. Never modify financial history to conceal a discrepancy.
7. Never treat a successful restart or deployment as proof of business recovery.
8. Never assume a backup is restorable without the required verification.
9. Never permit conflicting authoritative writers during recovery.
10. Never perform destructive data lifecycle operations without verifying eligibility.
11. Never expose private files as a troubleshooting shortcut.
12. Never let optional AI workloads compromise core ERP operations.
13. Never reduce costs by bypassing required security, backup, or retention controls.
14. Never hide a guardrail violation or remove evidence to make an incident appear resolved.
15. Never claim successful recovery, deletion, reconciliation, or compliance without sufficient evidence.

These summary rules do not replace the full requirements in this document or the detailed procedures in the linked Operations documents.

## 26. Acceptance Criteria

This document is considered operationally implemented when:

* Mandatory invariants are incorporated into relevant runbooks and operational reviews.
* Critical rules are technically enforced where reasonably possible.
* Manual controls have named owners and verification methods.
* Exception handling is documented and auditable.
* Guardrail violations trigger containment, investigation, and corrective action.
* Related Operations documents remain consistent with these requirements.
* The team can demonstrate compliance through technical evidence, operational records, or verified control execution.

**End of Document**

