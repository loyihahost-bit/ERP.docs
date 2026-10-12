# On-Call and Escalation Management

**Document ID:** OPS-06
**File:** `06_On_Call_and_Escalation_Management.md`
**Status:** Accepted
**Version:** 1.0
**Parent:** `doc/14_Operations/README.md`

## 1. Purpose

This document defines how operational responsibility is assigned, how on-call coverage is organized, and how incidents are escalated to the appropriate people or teams.

The objective is to ensure that production incidents reach an authorized responder, receive timely attention, and remain accountable until they are resolved or formally transferred.

On-call and escalation procedures must be reliable without introducing unnecessary operational complexity.

## 2. Scope

This document covers:

* On-call coverage and scheduling.
* Primary and secondary responders.
* Operational ownership and responsibility boundaries.
* Alert acknowledgement and response expectations.
* Escalation triggers and levels.
* Failed contact and unavailable responders.
* Incident ownership transfer.
* Specialist and management escalation.
* Handover between shifts.
* On-call access and security requirements.
* Coverage validation and operational review.

Incident lifecycle and recovery procedures remain defined in `05_Incident_Management.md`.

## 3. Core Principles

All on-call and escalation processes MUST follow these principles:

1. Every production-critical service has a defined operational owner.
2. Every required coverage period has an explicit responder or documented fallback.
3. Critical alerts must not depend on a single person being available.
4. Acknowledgement does not mean the incident is resolved.
5. Escalation must be based on severity, impact, risk, and response progress.
6. Responsibility remains explicit until a transfer is accepted.
7. Responders must have the access and authority required for their assigned duties.
8. Emergency access must remain controlled and auditable.
9. On-call schedules and contact paths must be verified and maintained.
10. Escalation must reach someone able to make the required decision or perform the necessary action.
11. Handover must preserve context, pending work, and unresolved risks.
12. Coverage must be proportionate to business risk and operational capacity.

## 4. Definitions

**On-call:** An assigned operational responsibility to receive, assess, or respond to incidents during a defined coverage period.

**Primary responder:** The first designated responder for a service or incident category.

**Secondary responder:** The designated fallback when the primary responder is unavailable or needs assistance.

**Service owner:** The role or team accountable for the operational health of a service.

**Incident Owner:** The person coordinating a specific declared incident, as defined in `05_Incident_Management.md`.

**Acknowledgement:** Confirmation that an alert or escalation has been received and accepted for assessment.

**Escalation:** Transfer of an issue to a higher level of authority, a specialist, or an additional responder because the current response is insufficient or additional capability is needed.

**Handover:** An explicit transfer of operational responsibility from one person or team to another.

**Coverage gap:** A period or situation in which no valid responder or fallback can be reached through the approved process.

## 5. Service Ownership and Coverage Requirements

Each production-critical service MUST have a documented owner and an escalation path.

Coverage requirements should reflect the service's business impact and operating model.

Services and components that may require explicit ownership include:

* Backend APIs.
* Database infrastructure.
* Redis, queues, and cache services.
* Background workers and schedulers.
* Frontend delivery.
* File storage.
* AI runtime services.
* Offline synchronization.
* Subscription and data-lifecycle processing.
* Monitoring and alert delivery.
* Backup and disaster recovery capabilities.
* Security-sensitive infrastructure and integrations.

Not every component requires a separate dedicated on-call person. Related components may share an owner when the owner has the necessary competence and capacity.

Shared services require special attention because a single failure may affect multiple tenants or branches.

## 6. On-Call Roles

### 6.1 Primary Responder

The primary responder is responsible for:

* Receiving and assessing assigned alerts.
* Acknowledging incidents through the approved process.
* Determining whether immediate action is required.
* Initiating the relevant runbook.
* Declaring or reporting incidents when appropriate.
* Contacting additional responders when the issue exceeds their authority or expertise.
* Recording actions and handing over responsibility when necessary.

The primary responder must not delay escalation merely because they are expected to handle the initial response.

### 6.2 Secondary Responder

The secondary responder provides fallback coverage and additional assistance.

Responsibilities include:

* Taking responsibility when the primary responder is unavailable.
* Assisting with incidents that require additional expertise.
* Providing an alternative contact path.
* Supporting continuity during a major incident or coverage gap.

The secondary responder must know how to access the current runbooks, incident records, and approved escalation channels.

### 6.3 Service Owner

The service owner is accountable for the long-term operational readiness of the service.

Responsibilities include:

* Maintaining service ownership documentation.
* Defining required response competencies.
* Ensuring runbooks are available and current.
* Identifying appropriate primary and secondary coverage.
* Reviewing recurring operational failures.
* Ensuring critical access and recovery procedures are documented.
* Addressing gaps identified through incidents or exercises.

### 6.4 Incident Owner

The Incident Owner coordinates the response to a specific incident.

This role may be held by the primary responder, service owner, or another authorized person.

For major incidents, incident coordination should be separated from detailed technical investigation when staffing permits.

### 6.5 Escalation Authority

The escalation authority is the person or role authorized to make decisions beyond the responder's normal scope.

Depending on the incident, this may include approving:

* Emergency production changes.
* High-risk containment actions.
* Service isolation.
* Disaster recovery activation.
* Customer-impacting operational restrictions.
* Financial or data corrections.
* Security incident response actions.

Escalation authority must be documented for the relevant action categories.

## 7. Coverage Models

The organization SHOULD choose a coverage model based on service criticality, incident frequency, staffing, and contractual commitments.

Possible models include:

| Model                      | Description                                                                               | Appropriate use                                                    |
| -------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Business-hours coverage    | Response is organized during defined working hours, with a documented out-of-hours policy | Lower-risk services                                                |
| Extended coverage          | Coverage includes additional defined periods outside normal business hours                | Services with broader operational needs                            |
| Rotating on-call           | Responsibility rotates between qualified responders                                       | Production-critical services requiring ongoing coverage            |
| Shared specialist coverage | A specialist supports multiple services through a shared escalation path                  | Specialized database, security, or infrastructure responsibilities |
| Managed external coverage  | An approved provider supplies defined monitoring or response services                     | Where explicitly contracted and governed                           |

The selected model MUST be documented for each critical service.

Do not describe a service as continuously monitored or continuously supported unless the required staffing, alert routing, and escalation coverage actually exist.

## 8. On-Call Schedule Management

On-call schedules MUST identify:

* The coverage period.
* Primary responder.
* Secondary or fallback responder.
* Covered services or incident categories.
* Escalation authority.
* Approved contact methods.
* Applicable handover procedure.

Schedule changes must be recorded and communicated to the affected participants.

The service owner SHOULD verify that:

* Upcoming coverage is assigned.
* Responders are qualified for their responsibilities.
* Contact details are current.
* Required access remains available.
* Escalation channels are functioning.
* Leave, absence, or availability changes have an appropriate replacement.

A schedule entry without a reachable responder does not constitute valid coverage.

## 9. Alert Receipt and Acknowledgement

Alert delivery, grouping, deduplication, and severity classification are governed by `04_Alerting_and_Notification_Operations.md`.

For alerts requiring human action, the on-call process MUST distinguish between:

1. Alert delivered.
2. Alert acknowledged.
3. Incident assessed.
4. Response action started.
5. Incident resolved or responsibility transferred.

Acknowledgement confirms receipt and responsibility for the next response step. It does not establish that the alert is understood, that mitigation has started, or that the service has recovered.

Responders SHOULD record an initial assessment when the issue is not immediately understood.

If an alert is a false positive or requires no action, the responder should record the reason according to the approved alert-handling procedure.

## 10. Response Expectations

Response expectations MUST be defined according to service criticality and approved operational service objectives.

This document does not establish universal response-time guarantees.

For each alert class requiring human response, the operational configuration SHOULD define:

* Expected acknowledgement time.
* Expected initial assessment time.
* Escalation condition.
* Fallback contact.
* Required incident-record information.

Response expectations should distinguish between acknowledgement and meaningful progress.

An acknowledged alert that receives no assessment or action must not remain indefinitely assigned without escalation or a documented reason.

If a required response deadline is missed, the escalation procedure MUST be triggered.

## 11. Escalation Triggers

Escalation is required when the current responder cannot safely or effectively handle the issue.

Triggers include:

* A critical alert is not acknowledged within its configured response window.
* A responder is unavailable or unreachable.
* The issue exceeds the responder's permissions or technical expertise.
* Severity increases.
* Impact spreads to additional services, tenants, or branches.
* Data integrity or security is at risk.
* A mitigation attempt fails.
* Recovery is taking longer than the approved expectation.
* A required approval is unavailable.
* A service has no valid owner or current runbook.
* A coverage gap is discovered.
* An incident requires coordination across multiple teams.
* A high-risk action requires a higher authorization level.

Escalation should occur as soon as a known condition requires it. Responders must not wait for a timer to expire when immediate escalation is clearly necessary.

## 12. Escalation Levels

The organization SHOULD maintain a simple, documented escalation hierarchy.

### Level 1 — Primary Response

The primary responder receives the alert, assesses the issue, and begins the authorized response.

### Level 2 — Secondary or Specialist Response

Escalation to a secondary responder or specialist occurs when:

* The primary responder is unavailable.
* The issue requires additional expertise.
* Initial mitigation fails.
* The incident affects multiple services.
* The risk exceeds the primary responder's authority.

### Level 3 — Incident Coordination and Service Ownership

Escalation to the Incident Owner or service owner occurs when:

* The incident requires coordinated response.
* Business impact is significant.
* Multiple teams or service owners are involved.
* Recovery decisions require broader technical context.
* A major incident needs dedicated coordination.

### Level 4 — Management, Security, or Business Authority

Escalation to the relevant authority occurs when:

* A major business decision is required.
* Security or privacy risk requires specialized authority.
* Customer-impacting restrictions require approval.
* Disaster recovery activation requires authorization.
* Material financial, legal, contractual, or data-integrity risk requires a designated decision-maker.

These levels describe responsibility, not a requirement to contact every level sequentially. Critical incidents may require several levels to be engaged in parallel.

## 13. Escalation Routing

Escalation routing MUST be documented for each critical incident category.

The route should identify:

* Initial recipient.
* Fallback recipient.
* Specialist contacts.
* Incident coordination contact.
* Required decision-maker.
* Approved communication channel.

Routes may be organized by service, severity, or incident category.

Examples:

| Incident category                  | Initial route                                                  | Additional escalation                         |
| ---------------------------------- | -------------------------------------------------------------- | --------------------------------------------- |
| API or frontend failure            | Relevant service responder                                     | Service owner or incident coordinator         |
| Database availability or integrity | Database-qualified responder                                   | Incident coordinator and data authority       |
| Security compromise                | Authorized security responder                                  | Security authority and incident coordinator   |
| Financial inconsistency            | Authorized financial/business responder with technical support | Business authority and relevant service owner |
| Offline synchronization failure    | Synchronization or backend responder                           | Branch operations and data owner              |
| Backup or recovery failure         | Infrastructure or database responder                           | Recovery authority and incident coordinator   |
| Subscription lifecycle failure     | Subscription service responder                                 | Service owner and business authority          |

Routing must respect access boundaries. A recipient must receive only the information needed for their responsibility.

## 14. Failed Contact and Unavailable Responders

If the primary responder does not acknowledge an alert within the configured window, the system or responsible operator MUST initiate the documented fallback path.

The procedure SHOULD:

1. Attempt the approved primary contact method.
2. Escalate to the secondary responder when the response window expires or unavailability is known.
3. Engage the service owner or incident coordinator when the issue remains unowned.
4. Use the designated emergency path for critical incidents.
5. Record the coverage failure and corrective action.

Do not repeatedly contact an unavailable person while leaving the incident without an active responder.

If every designated responder is unavailable, follow the documented emergency ownership procedure. Critical coverage gaps must be reported to the responsible operational authority.

## 15. Responsibility Transfer and Handover

Responsibility transfer MUST be explicit.

A handover should include:

* Incident or alert identifier.
* Current severity and impact.
* Confirmed facts and unresolved questions.
* Actions completed and their results.
* Current risks and containment measures.
* Pending actions and deadlines.
* Access or approval requirements.
* Relevant logs, dashboards, runbooks, and evidence.
* Next planned step.
* Stakeholders who have already been informed.

The receiving responder should acknowledge acceptance of responsibility.

Until acceptance is confirmed, the current owner remains responsible for ensuring that the incident is not abandoned, unless an emergency policy explicitly assigns responsibility to another authority.

For scheduled on-call rotations, the outgoing and incoming responders SHOULD verify the handover of active incidents and unresolved high-priority alerts.

## 16. Escalation During Major Incidents

For a major incident:

* Engage the Incident Owner or assign one immediately.
* Contact relevant specialists based on the affected systems.
* Engage security or business authorities when required.
* Establish a shared response channel.
* Maintain a single authoritative incident timeline.
* Assign actions with clear ownership.
* Escalate failed mitigation or growing impact without delay.
* Record significant decisions and approvals.

The Incident Owner coordinates the response. Technical responders remain accountable for their assigned tasks and must communicate material findings and risks.

Escalation must not create competing instructions or uncoordinated production changes.

## 17. Emergency Authority and Access

On-call responsibilities MUST align with role-based authorization and approved access controls.

Responders may perform only actions permitted by their assigned role or an explicitly authorized emergency procedure.

Emergency access MUST:

* Be limited to the required scope.
* Use approved authentication mechanisms.
* Be time-limited where supported.
* Produce audit records.
* Avoid shared personal credentials.
* Be revoked or reviewed after the emergency.
* Preserve tenant and branch isolation.

An incident does not justify bypassing authentication, authorization, audit requirements, or data-integrity safeguards.

Where the assigned responder lacks sufficient access, escalation must reach an authorized person rather than relying on unauthorized workarounds.

## 18. On-Call Runbooks and Readiness

Every critical on-call path SHOULD have an appropriate runbook or documented response procedure.

A runbook should include:

* Purpose and scope.
* Symptoms and likely impact.
* Required access and permissions.
* Initial diagnostic checks.
* Safe mitigation steps.
* Prohibited or high-risk actions.
* Escalation triggers and contacts.
* Verification and recovery criteria.
* Evidence and reporting requirements.
* Related operational documents.

Runbooks must be version-controlled and updated after meaningful operational changes or incidents that reveal gaps.

Responders SHOULD be familiar with the procedures for the services they cover. Critical recovery steps should not depend solely on undocumented knowledge held by one individual.

## 19. On-Call Tooling and Contact Channels

Approved tooling may include:

* Alert delivery and acknowledgement systems.
* Incident-tracking systems.
* Team communication channels.
* Secure emergency contact methods.
* Monitoring dashboards.
* Runbook repositories.
* Access-management and audit systems.

Critical escalation must not depend on a single communication channel when a documented alternative is necessary for the risk level.

Contact information and routing configuration must be protected from unauthorized modification.

Changes to escalation tooling must be tested to verify that alerts reach the intended recipients and fallback paths work.

## 20. Coverage Gaps and Continuity

A coverage gap exists when a required operational responsibility has no reachable, qualified responder.

Coverage gaps MUST be recorded and addressed according to risk.

For a critical service, the responsible authority should establish a temporary fallback before relying on the affected coverage arrangement.

If complete coverage cannot be maintained:

* Document the affected period and services.
* Assess the resulting operational risk.
* Identify a temporary escalation authority.
* Notify the responsible owner.
* Apply approved risk-reduction measures.
* Define when normal coverage must be restored.

Do not imply that unattended monitoring provides human incident response.

## 21. On-Call Workload and Sustainability

On-call arrangements should be sustainable and proportionate to operational risk.

Service owners SHOULD review:

* Alert volume and relevance.
* Repeated overnight or out-of-hours interruptions.
* False-positive rates.
* Unnecessary escalation.
* Single-person dependencies.
* Missing automation or runbooks.
* Repeated incidents that should be prevented through engineering improvements.

The solution to excessive on-call workload should generally be better detection, alert quality, automation, resilience, or service design—not simply asking responders to absorb more interruptions.

Coverage changes must preserve required business and security protections.

## 22. Review and Audit

Operational owners SHOULD periodically review:

* Coverage schedules and fallback assignments.
* Reachability of escalation contacts.
* Escalation policy and response windows.
* Runbook completeness.
* Emergency access arrangements.
* Handover quality.
* Coverage gaps and failed contacts.
* Unnecessary escalation patterns.
* Incidents delayed by unclear ownership.
* Readiness of critical service owners.

Reviews should produce trackable corrective actions with owners and completion criteria.

High-risk gaps must be escalated through the operational governance process.

## 23. Relationships to Other Documents

This document works with:

* `03_Monitoring_and_Observability_Operations.md` — monitoring signals and operational visibility.
* `04_Alerting_and_Notification_Operations.md` — alert severity, routing, acknowledgement, and notification behavior.
* `05_Incident_Management.md` — incident lifecycle, ownership, response coordination, and closure.
* `07_Backup_Verification_and_Restore_Operations.md` — backup verification and restoration responsibilities.
* `08_Disaster_Recovery_Operations_Runbook.md` — disaster recovery activation and execution.
* `09_Database_Operations.md` — database ownership and operational recovery.
* `10_Redis_Queue_and_Cache_Operations.md` — Redis, queue, and cache incidents.
* `11_Backend_API_Operations.md` — backend and API operations.
* `13_Background_Worker_and_Scheduler_Operations.md` — worker and scheduler operations.
* `14_AI_Runtime_Operations.md` — AI runtime ownership and recovery.
* `16_Subscription_and_Data_Lifecycle_Operations.md` — subscription and data-lifecycle responsibilities.
* `17_Security_Operations.md` — security response and authorized containment.
* `18_Release_and_Change_Operations.md` — release interruption and emergency change procedures.
* `20_Operations_Invariants_and_Guardrails.md` — mandatory operational invariants.

## 24. On-Call and Escalation Invariants

The following rules are mandatory:

1. Every critical production service has a documented operational owner.
2. Required coverage periods have an explicit responder or fallback.
3. Coverage claims must reflect actual operational capability.
4. Critical alerts have a documented escalation path.
5. Primary and fallback contact details must be maintained.
6. Acknowledgement is not equivalent to resolution.
7. Response expectations are defined for alerts requiring human action.
8. Missed response expectations trigger escalation.
9. Known unavailability triggers escalation without unnecessary delay.
10. Severity and business impact determine escalation urgency.
11. Critical incidents may require parallel escalation.
12. Every active incident has an accountable owner.
13. Responsibility transfers must be explicit.
14. A handover must preserve unresolved risks and pending work.
15. The receiving owner should acknowledge responsibility.
16. The previous owner must not silently abandon an unaccepted handover.
17. Responders must remain within authorized access boundaries.
18. Emergency access must be auditable.
19. Tenant and branch isolation must remain enforced.
20. Escalation routes must identify the authority required for high-risk decisions.
21. Security incidents must reach the designated security authority.
22. Material financial and data-integrity risks must reach the appropriate owner.
23. Disaster recovery decisions must follow approved authority rules.
24. Critical runbooks must be accessible to authorized responders.
25. High-risk recovery procedures must not depend solely on undocumented knowledge.
26. Critical escalation must have an appropriate fallback contact path.
27. Contact-channel failures must be included in readiness reviews.
28. Coverage gaps must be recorded and addressed.
29. Critical coverage gaps must have an explicit temporary response arrangement.
30. Escalation must not produce conflicting, uncoordinated production changes.
31. The Incident Owner coordinates the incident while responders own assigned actions.
32. On-call schedules must be updated when responsibility changes.
33. Handover must include relevant incident records and evidence.
34. Sensitive incident information must be shared only with authorized recipients.
35. On-call tooling changes must be tested.
36. False-positive and unnecessary escalation patterns must be reviewed.
37. Excessive alert workload must trigger operational improvement.
38. Response windows must align with approved service objectives.
39. Coverage must be proportionate to service criticality.
40. Emergency procedures must not bypass authentication or authorization.
41. Service owners must address recurring operational readiness gaps.
42. High-risk corrective actions must remain trackable.
43. On-call responsibilities must not imply unsupported response guarantees.
44. Major incidents require coordinated ownership and communication.
45. Escalation must occur when the responder lacks necessary authority or expertise.
46. Recovery actions must follow the relevant authoritative runbook.
47. Responsibility for an unresolved incident must remain explicit.
48. Operational ownership and escalation configuration must be reviewable.
49. Coverage arrangements must support continuity across handovers.
50. Escalation must reach a person capable of making the required decision or performing the required action.

## 25. Final Principle

On-call and escalation management ensure that operational problems reach the right person, receive an appropriate response, and remain accountable until responsibility is explicitly transferred or the incident is resolved.

**Every critical incident must have a reachable response path, a clear owner, an appropriate escalation route, and a controlled handover process.**

