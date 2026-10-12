# Multi-Cash-Register Evolution

**Document ID:** FUT-03
**Status:** Accepted
**Version:** 1.0
**Section:** 15_Future
**Last Updated:** 2026-10-09

## 1. Purpose

This document describes how the FastFood ERP platform may evolve from one cash register per branch to multiple cash registers within the same branch.

The purpose is to preserve a clear future evolution path without introducing multi-register requirements into the current implementation.

This document identifies potential business workflows, data ownership considerations, reconciliation requirements, concurrency risks, and migration concerns that must be evaluated before multi-register operation is approved.

This document does not authorize implementation.

## 2. Current Baseline

The current approved operating model is:

* Each branch operates one cash register.
* A cashier manually opens and closes the register.
* Register activity is associated with the responsible cashier.
* Each cashier receives an appropriate register report.
* The customer-facing register opening and closing number is three digits and resets according to the existing opening/closing cycle.
* Persistent database identifiers remain separate from the customer-facing number.
* Register closing includes a cashier comment, report generation, and Owner notification.
* Cash handover requires incoming-cashier confirmation and a cash count.
* Shortages trigger notifications to the previous cashier and Owner.
* Recount and confirmation are required where applicable.
* Corrections are limited under the established correction policy, with privileged reopening after the limit.
* Register activity must remain auditable.
* Offline branch operation and subsequent synchronization remain supported.

These are current requirements and MUST NOT be changed merely because this Future document describes multiple registers.

## 3. Future Objective

A future multi-register capability may allow a branch to operate multiple independently identified registers.

Possible use cases include:

* Separate checkout counters in a larger restaurant.
* A dedicated takeaway counter.
* A separate cashier for delivery orders.
* Additional checkout capacity during busy periods.
* Separate cash-handling responsibilities within the same branch.

These are examples of potential business needs, not approved requirements.

The actual scope MUST be established through Business Analysis before implementation.

## 4. Goals and Non-Goals

### 4.1 Potential Goals

A future design may aim to:

* Identify each register independently.
* Track opening and closing sessions per register.
* Associate each transaction with the responsible register and cashier.
* Reconcile cash separately for each register.
* Produce register-level and branch-level financial reports.
* Support controlled cashier handover.
* Preserve branch-level inventory and order integrity.
* Support offline transactions and synchronization without duplication.
* Allow authorized employees to access only permitted registers and branches.

### 4.2 Non-Goals

This document does not require:

* Multiple registers today.
* Simultaneous register sessions for one cashier.
* Shared cash drawers across registers.
* A separate database for each register.
* A separate service for register management.
* Automatic cash transfers between registers.
* Independent inventory per register.
* New hardware purchases.
* A new subscription tariff.
* A specific implementation framework or database schema.

Each item requires separate evaluation if it becomes relevant.

## 5. Register Identity and Ownership

A future multi-register model MUST distinguish the following concepts:

* **Business:** the restaurant network or tenant.
* **Branch:** the operational location.
* **Register:** an identifiable checkout and cash-handling unit within a branch.
* **Register session:** one opening-to-closing operating cycle for a register.
* **Cashier assignment:** the authorized employee responsible for a register or session.
* **Transaction:** an order, payment, refund, or other financial event associated with the relevant business workflow.
* **Handover:** a controlled transfer of responsibility between authorized employees.

These concepts MUST remain logically distinguishable even if the eventual implementation uses a small number of database tables.

A register MUST belong to exactly one authorized branch within the appropriate business boundary.

Register identifiers MUST NOT be used as substitutes for tenant or branch authorization.

## 6. Register Session Lifecycle

A potential future session lifecycle may include:

1. Register is configured and available.
2. Authorized cashier requests opening.
3. Opening conditions are validated.
4. A new register session is created.
5. Transactions are associated with the active session.
6. The cashier requests closing.
7. Closing totals and cash counts are recorded.
8. Variances are evaluated and documented.
9. Required confirmations and approvals are completed.
10. The session is closed and its report is preserved.

This sequence is illustrative and MUST be validated against the existing register lifecycle before implementation.

The final state machine must explicitly define which actions are allowed during opening, active operation, closing, correction, reopening, and handover.

A closed session MUST NOT silently accept new transactions.

Any exceptional reopening MUST be authorized, recorded, and reconciled.

## 7. Cashier Assignment and Handover

Multiple registers introduce additional assignment questions.

Future analysis MUST determine:

* Whether one cashier may operate multiple registers.
* Whether one register may have multiple authorized cashiers during a shift.
* Whether cashier assignment is exclusive or time-bounded.
* Whether handover is allowed while orders or payments are still being processed.
* Whether the incoming cashier must count and confirm the cash.
* Who receives shortage and overage notifications.
* Which roles may correct a completed session.
* Which conditions require privileged reopening.

Cash responsibility MUST be explicit and auditable.

The system MUST NOT infer financial responsibility solely from the employee who is currently logged in.

If one employee operates more than one register, reports and permissions MUST still distinguish the corresponding register sessions.

## 8. Transaction and Payment Association

Before multi-register operation is approved, every applicable financial event MUST have a clearly defined association with its register and session.

The analysis MUST cover:

* Order acceptance.
* Payment authorization and completion.
* Split payments, if supported.
* Refunds.
* Payment failures and uncertain outcomes.
* Voids and corrections.
* Cash movements, if supported.
* Handover and session closure.
* Offline-created transactions and later synchronization.

The final model MUST distinguish order identity from register-session identity.

A transaction MUST NOT be counted twice because it was retried, synchronized, or reassigned.

A register change MUST NOT silently change the historical owner of an already completed financial transaction.

If a payment provider confirms a result after a timeout, the system MUST reconcile the actual outcome before attempting another financial action.

## 9. Cash Reconciliation

A future multi-register capability MUST define reconciliation at more than one level where required.

### 9.1 Register-Level Reconciliation

Each register session may require:

* Opening cash balance.
* Recorded cash receipts.
* Approved cash movements.
* Refunds and other permitted adjustments.
* Expected closing cash.
* Actual counted cash.
* Variance amount.
* Cashier explanation.
* Required confirmation or approval.
* Final session status.

The exact formula and treatment of each transaction category MUST be defined in the authoritative financial requirements before implementation.

### 9.2 Branch-Level Reconciliation

A branch-level report may aggregate eligible register-session results.

Aggregation MUST preserve the underlying register and session identities so that differences can be traced.

A branch total MUST NOT conceal a shortage in one register by silently offsetting it against an unexplained surplus in another.

Cash transfers between registers, if ever supported, MUST be recorded as explicit, linked movements with appropriate authorization and confirmation.

## 10. Register Numbering and Identification

The current customer-facing three-digit opening/closing number and its reset behavior remain part of the existing model.

A future multi-register design MUST determine whether this number is scoped to:

* A register.
* A branch.
* A register session.
* A customer-facing receipt sequence.

The decision MUST preserve unambiguous references for employees, reports, and support investigations.

The customer-facing number MUST NOT replace the persistent internal identifier.

If numbering can repeat across registers or sessions, the user interface, receipts, reports, and support workflows MUST provide enough context to distinguish the relevant record.

Numbering rules MUST be documented before implementation; they MUST NOT be inferred from the database primary key.

## 11. Orders, Kitchen Workflows, and Inventory

Register evolution MUST preserve existing order and inventory rules.

Before implementation, determine:

* Whether an order remains associated with the register that accepted it.
* Whether an authorized cashier may complete payment at another register.
* How register identity is represented in order and payment history.
* How open orders behave when a register session closes.
* Whether kitchen routing is affected by register assignment.
* How refunds are associated with the original order and financial records.
* How offline transactions are attributed after synchronization.

Inventory remains governed by the approved recipe and stock rules.

A new register MUST NOT create independent stock availability or permit negative stock merely because multiple checkout points exist.

The architecture MUST distinguish the checkout point from the authoritative branch inventory.

## 12. Offline Operation and Synchronization

Offline operation is a current requirement.

A future multi-register implementation MUST NOT weaken transaction integrity when multiple devices operate offline.

The design MUST evaluate:

* Stable device and transaction identifiers.
* Register identity and session identity during offline operation.
* Prevention of duplicate transaction submission.
* Reconciliation of delayed payment results.
* Conflicting register configuration changes.
* Session closure while devices remain offline.
* Cashier handover when synchronization is incomplete.
* Recovery after a device restart or network interruption.
* Server-side validation after reconnection.

The system MUST NOT assume that synchronized events arrive in creation order.

The system MUST NOT automatically resolve conflicting financial events by silently overwriting one record with another.

The rules for accepting, rejecting, or reconciling transactions after an offline session has changed state MUST be explicitly approved.

If safe operation cannot be guaranteed under a specific offline scenario, the system MUST define a controlled restriction and a clear user-visible explanation before that scenario is supported.

## 13. Permissions and Auditability

Future multi-register operation MUST use server-side authorization.

Potential permission dimensions include:

* Branch access.
* Register access.
* Session opening.
* Session closing.
* Cashier assignment.
* Handover confirmation.
* Refund authorization.
* Financial correction.
* Privileged reopening.
* Register configuration.
* Cross-register reporting.
* Branch-level reconciliation.

These are candidate dimensions, not a requirement to create a separate permission for every action.

The final permission model SHOULD remain understandable and consistent with the existing role and permission system.

Audit records MUST identify the relevant business, branch, register, session, actor, action, timestamp, and outcome where applicable.

Sensitive authentication data MUST NOT be recorded in audit logs.

## 14. Reporting and Notifications

A future reporting model may provide:

* Register-session reports.
* Cashier reports.
* Branch-level consolidated reports.
* Register variance reports.
* Handover records.
* Refund and correction summaries.
* Unclosed-session alerts.
* Offline synchronization exceptions.

Reports MUST distinguish source transactions from derived aggregates.

Branch-level totals MUST be traceable to the underlying register sessions and transactions.

Notification rules MUST define the responsible recipient, severity, deduplication behavior, and acknowledgement requirements where applicable.

Adding multiple registers MUST NOT automatically cause every routine event to notify the Owner.

Existing operational notification principles should remain in effect.

## 15. Subscription and Capacity Implications

A future commercial model may consider whether register count is limited by subscription plan.

No new register-based tariff or entitlement is introduced by this document.

If register count becomes plan-dependent, the approved design MUST define:

* What counts as a configured register.
* What counts as an active register.
* How disabled or archived registers are treated.
* What happens when a plan limit is reached.
* How subscription expiration affects register operation.
* How existing transaction records remain accessible.
* How plan changes affect existing register sessions.

Subscription enforcement MUST remain server-side and consistent with the approved lifecycle rules.

Register-count restrictions MUST NOT silently make existing financial records inaccessible.

## 16. Migration and Compatibility

If the platform later adopts multi-register support, the migration MUST preserve existing branch and register history.

Before migration, the team MUST determine:

* How the existing single register is represented in the new model.
* How historical transactions are associated with that register.
* How historical opening/closing numbers are preserved.
* Whether old clients or devices require compatibility support.
* Whether API contracts or reports change.
* Whether migration requires downtime or staged deployment.
* How the migration is verified and recovered if it fails.

Existing transactions MUST NOT be assigned to arbitrary new registers merely to satisfy a new schema.

Historical values MUST remain traceable and must not be fabricated where the original data does not support the mapping.

Database migration MUST follow approved deployment, backup, testing, and recovery procedures.

## 17. Monitoring and Operations

A production implementation may require monitoring for:

* Registers that cannot open or close.
* Sessions left open unexpectedly.
* Unreconciled cash variances.
* Failed or delayed transaction synchronization.
* Duplicate payment or transaction attempts.
* Register configuration errors.
* Unauthorized register access.
* Excessive register contention.
* Branch-level reconciliation failures.

Thresholds MUST be based on approved business rules and measured operational behavior.

Operational procedures MUST cover register recovery, session reconciliation, device replacement, access revocation, incident investigation, and safe resumption.

Restarting a device or service MUST NOT be treated as proof that financial state has been reconciled.

## 18. Risks and Trade-Offs

Potential benefits include greater checkout capacity, clearer responsibility separation, and more flexible branch operations.

Potential costs and risks include:

* More complex session and cashier assignment rules.
* Increased reconciliation effort.
* Ambiguous financial responsibility.
* More complex reporting and permissions.
* Device coordination and offline synchronization risks.
* Greater support and testing requirements.
* Additional subscription or configuration complexity.
* More difficult migration and historical reporting.

The decision MUST compare these costs with a documented business need.

Multi-register support MUST NOT be adopted solely because it is common in other POS systems.

## 19. Approval Requirements

Before implementation, the initiative MUST:

1. Validate the business need.
2. Define register, session, and cashier ownership.
3. Approve session lifecycle and state transitions.
4. Define payment, refund, and cash-reconciliation behavior.
5. Define register numbering and historical traceability.
6. Define offline behavior and duplicate prevention.
7. Review tenant isolation and permission enforcement.
8. Review subscription and branch configuration implications.
9. Define reports, notifications, and audit requirements.
10. Evaluate migration and backward compatibility.
11. Define capacity, monitoring, and operational procedures.
12. Update authoritative requirements and relevant ADRs.
13. Establish acceptance criteria and test scenarios.
14. Obtain explicit approval before implementation.

## 20. Related Documents

Future documents:

* `01_Future_Roadmap_and_Evolution_Framework.md`
* `02_Deferred_Capabilities_and_Architecture_Reserve.md`
* `04_Scale_Beyond_Initial_Branch_Limits.md`
* `12_Future_Architecture_Guardrails.md`

Current documentation areas to review before implementation:

* Business Analysis.
* System Analysis.
* Domain Analysis.
* Architecture.
* Database.
* Backend.
* Frontend.
* API.
* Security.
* Testing.
* Deployment.
* Operations.

Specific document links SHOULD be added only after the target files have been verified.

## 21. Mandatory Invariants

1. One register per branch remains the current approved model.
2. This document does not authorize multi-register implementation.
3. A register MUST belong to one authorized branch.
4. Tenant isolation MUST remain mandatory.
5. Branch authorization MUST remain mandatory.
6. Register identity MUST be distinct from branch identity.
7. Register-session identity MUST be distinct from register identity.
8. Transaction identity MUST remain distinct from register-session identity.
9. Cash responsibility MUST be explicit and auditable.
10. Closed sessions MUST NOT silently accept new transactions.
11. Exceptional reopening MUST be authorized and audited.
12. Cashier assignment MUST NOT be inferred solely from the current login.
13. Financial transactions MUST NOT be counted twice.
14. Retries MUST NOT create duplicate payments or business transactions.
15. Uncertain payment outcomes MUST be reconciled before another financial action.
16. Completed transactions MUST retain historical traceability.
17. Register changes MUST NOT silently rewrite financial ownership.
18. Cash reconciliation MUST preserve register-level variance visibility.
19. Branch totals MUST remain traceable to their source records.
20. Cash transfers MUST be explicit if such transfers are approved.
21. Customer-facing register numbers MUST NOT replace persistent identifiers.
22. Numbering scope MUST be explicitly defined before implementation.
23. Existing numbering behavior MUST remain unchanged until an approved change.
24. Existing order and inventory rules MUST remain authoritative.
25. Register identity MUST NOT create independent inventory authority.
26. Negative stock MUST remain prohibited.
27. Recipe-based inventory deduction MUST remain authoritative.
28. Refunds MUST follow the approved authorization and audit workflow.
29. Offline operation MUST preserve transaction integrity.
30. Synchronization MUST NOT assume event arrival order equals creation order.
31. Conflicting financial events MUST NOT be silently overwritten.
32. Offline session closure MUST have explicitly defined behavior.
33. Server-side authorization MUST remain authoritative.
34. Privileged corrections MUST be traceable.
35. Cross-register reporting MUST require appropriate permission.
36. Subscription enforcement MUST remain server-side.
37. Register limits MUST NOT make historical financial records inaccessible.
38. Migration MUST preserve existing transaction history.
39. Unsupported historical mappings MUST NOT be fabricated.
40. API and client compatibility MUST be evaluated before rollout.
41. Monitoring MUST distinguish technical recovery from financial reconciliation.
42. Production operations MUST include safe register recovery procedures.
43. Additional infrastructure MUST be justified by the approved design.
44. Capacity assumptions MUST be validated against workload evidence.
45. Notification changes MUST preserve existing routing and deduplication principles.
46. Testing MUST cover concurrent operations and failure scenarios.
47. Implementation MUST follow approved release and change controls.
48. Multi-register approval MUST include business and operational acceptance criteria.
49. Current requirements MUST be updated before this capability becomes authoritative.
50. The Future section MUST NOT silently change the current single-register model.

## 22. Acceptance Criteria

This document is acceptable when:

* The current single-register model is explicitly preserved.
* The future register and session concepts are distinguishable.
* Cashier assignment, reconciliation, payments, and reporting risks are identified.
* Offline operation and transaction integrity are addressed.
* Security, subscription, migration, and operational implications are documented.
* Approval prerequisites are clear.
* No implementation technology or new infrastructure is mandated without justification.

## 23. Maintenance

Review this document when business requirements change, multi-register demand is validated, or relevant architecture and financial workflows are updated.

Any approved implementation MUST update the authoritative current documentation and preserve traceability to this Future document.

