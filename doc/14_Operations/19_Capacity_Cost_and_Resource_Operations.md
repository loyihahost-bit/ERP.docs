# Capacity, Cost, and Resource Operations

**Document ID:** OPS-19
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Category:** Operations
**Repository Path:** `doc/14_Operations/19_Capacity_Cost_and_Resource_Operations.md`

---

## 1. Purpose

This document defines operational procedures for capacity planning, resource utilization monitoring, infrastructure cost management, and controlled system growth.

Its purpose is to ensure that the FastFood ERP platform remains reliable, responsive, secure, and financially sustainable as the number of restaurant networks, branches, employees, orders, inventory records, files, background jobs, and AI workloads increases.

Capacity and cost decisions must be based on measured behavior, documented requirements, workload forecasts, and verified operational evidence rather than assumptions alone.

This document applies to production infrastructure and supporting environments where resource consumption or cost can materially affect production readiness or service delivery.

## 2. Scope

This document covers:

* Infrastructure and application capacity planning.
* CPU, memory, storage, network, and connection utilization.
* Database, Redis, queue, worker, and scheduler capacity.
* Backend API and frontend delivery capacity.
* File storage and backup growth.
* AI inference and model-serving resource consumption.
* Infrastructure cost tracking and forecasting.
* Resource allocation and cost attribution.
* Scaling decisions and resource changes.
* Capacity alerts and resource-related incidents.
* Load-test evidence and capacity reviews.
* Cost optimization without compromising security or business correctness.

This document does not establish final infrastructure sizes, provider-specific prices, or guaranteed customer limits. These must be determined from the selected deployment architecture, approved service requirements, and measured workload.

## 3. Related Documents

This document must be maintained consistently with:

* `03_Monitoring_and_Observability_Operations.md`
* `05_Incident_Management.md`
* `07_Backup_Verification_and_Restore_Operations.md`
* `09_Database_Operations.md`
* `10_Redis_Queue_and_Cache_Operations.md`
* `11_Backend_API_Operations.md`
* `13_Background_Worker_and_Scheduler_Operations.md`
* `14_AI_Runtime_Operations.md`
* `15_File_Storage_and_Document_Operations.md`
* `16_Subscription_and_Data_Lifecycle_Operations.md`
* `17_Security_Operations.md`
* `18_Release_and_Change_Operations.md`

Relevant deployment, architecture, testing, subscription, and service-level requirement documents also apply.

If two documents define conflicting requirements, the conflict must be documented and resolved through the project's approved documentation and decision-making process.

## 4. Operational Principles

Capacity and cost operations must follow these principles:

1. **Measure before scaling.** Identify the actual bottleneck before changing resources.
2. **Protect business correctness.** Cost reductions must not compromise orders, payments, inventory, cash registers, or offline synchronization.
3. **Scale according to evidence.** Use measured utilization, latency, throughput, backlog, and growth trends.
4. **Keep resource ownership clear.** Every critical service and infrastructure resource must have an accountable owner.
5. **Separate capacity from availability.** A service can have sufficient CPU and memory while failing because of a database, network, dependency, or configuration problem.
6. **Distinguish usage from cost.** Increased consumption does not always produce a proportional cost increase, and fixed costs may remain when usage falls.
7. **Avoid premature optimization.** Optimize measured bottlenecks rather than adding unnecessary infrastructure.
8. **Preserve isolation.** Resource allocation and optimization must not weaken restaurant-network or branch-level data isolation.
9. **Plan for recovery workloads.** Backlogs and offline branches can generate temporary load spikes after an outage.
10. **Make changes reversible where possible.** Resource changes must have validation criteria and a recovery plan.

## 5. Capacity Ownership and Responsibilities

Operational ownership must be assigned according to the team's actual size and deployment model. One person may hold multiple responsibilities, but accountability must remain explicit.

| Responsibility       | Required duties                                                                                |
| -------------------- | ---------------------------------------------------------------------------------------------- |
| Operations owner     | Maintains the capacity plan, resource inventory, and review schedule.                          |
| Infrastructure owner | Manages compute, memory, storage, networking, and infrastructure configuration.                |
| Backend owner        | Reviews API throughput, latency, concurrency, and application resource consumption.            |
| Database owner       | Reviews database connections, query performance, storage, maintenance, and growth.             |
| Worker owner         | Reviews queues, background jobs, scheduler execution, and worker concurrency.                  |
| AI runtime owner     | Reviews inference capacity, model resource use, latency, and AI-specific costs.                |
| Security owner       | Reviews security implications of scaling, access, telemetry, and resource changes.             |
| Business owner       | Confirms business priorities, subscription constraints, and acceptable operational trade-offs. |

The project must identify who approves material infrastructure spending, capacity changes, emergency scaling, and cost-control actions.

Where no dedicated specialist exists, the designated operations owner must ensure that the responsibility is covered.

## 6. Resource Inventory

Maintain a current inventory of production resources.

The inventory must identify, where applicable:

* Resource name and unique identifier.
* Environment and deployment location.
* Resource type and purpose.
* Service or component using the resource.
* Resource owner.
* Configured size, quota, or capacity.
* Scaling behavior and limits.
* Availability and recovery dependencies.
* Monitoring and alert references.
* Billing category or cost attribution.
* Data classification and security requirements.
* Backup and retention requirements.
* Lifecycle status, including temporary or obsolete resources.

Resources may include:

* Virtual machines, containers, or managed compute services.
* Operating-system CPU and memory.
* PostgreSQL instances and storage.
* Redis instances.
* API processes and connection pools.
* Background workers and scheduled jobs.
* File and object storage.
* Backup repositories.
* Network bandwidth, transfer, and load-balancing services.
* AI model runtimes and accelerators, if used.
* Monitoring, logging, and tracing infrastructure.
* Development, testing, staging, and temporary environments.

Resources not currently used must be reviewed for safe removal. A resource must not be deleted merely because it appears idle; its ownership, dependencies, retention obligations, and recovery purpose must first be checked.

## 7. Capacity Planning Model

### 7.1 Workload dimensions

Capacity planning must consider more than the number of branches.

Relevant workload dimensions include:

* Active restaurant networks and branches.
* Concurrent users and active POS terminals.
* Orders created, updated, and completed per unit of time.
* Order complexity and the number of recipe components.
* Inventory movements and stock calculations.
* Cash-register openings, closings, and reconciliation operations.
* Report generation and export activity.
* Background jobs and scheduled tasks.
* File uploads, downloads, and retained document volume.
* API request rate and request complexity.
* Database reads, writes, transactions, and query concurrency.
* Offline transaction accumulation and synchronization volume.
* Subscription and data-lifecycle processing.
* AI inference request volume and model complexity.
* Administrative operations and bulk imports.

A branch with many concurrent cashiers and frequent inventory movements may create a different workload from a branch with low order volume. Capacity estimates must account for these differences.

### 7.2 Capacity baseline

Establish a baseline for each critical component using representative measurements.

The baseline should record:

* Normal and peak utilization.
* Request or transaction throughput.
* Response-time distribution, including tail latency.
* Error and timeout rates.
* Memory usage and growth behavior.
* Storage utilization and growth rate.
* Database connection and query behavior.
* Queue depth and oldest-job age.
* Network utilization and transfer volume.
* Cost over a defined reporting period.
* Relevant workload dimensions.

The baseline must identify the observation period, environment, workload assumptions, and measurement limitations.

A short observation period must not be treated as proof of long-term capacity.

### 7.3 Capacity limits

For each critical resource, define:

* Normal operating range.
* Warning threshold.
* Critical threshold.
* Hard capacity or configured quota.
* Expected growth.
* Time available to respond before exhaustion.
* Required response action.
* Escalation owner.

Thresholds must be based on system behavior, service requirements, and operational response time. Universal CPU or memory percentages must not be copied without validating their relevance to the deployed architecture.

### 7.4 Capacity headroom

Maintain sufficient headroom for expected peaks, short-lived spikes, routine maintenance, and recovery activities.

Headroom must be evaluated against:

* Peak traffic.
* Deployment and restart overhead.
* Database maintenance operations.
* Backup and restore activity.
* Queue catch-up after outages.
* Offline branch synchronization.
* Temporary reporting or import workloads.
* Failure of a component where the architecture requires remaining components to absorb its load.

Headroom is not an excuse to provision resources without justification. It must be supported by documented workload assumptions and periodically reviewed.

## 8. Resource Utilization Monitoring

### 8.1 Compute and CPU

Monitor, where supported:

* CPU utilization and saturation.
* Load average or equivalent scheduler indicators.
* CPU throttling for constrained workloads.
* Process-level CPU consumption.
* Request throughput and latency alongside CPU usage.
* Unexpected growth in resource consumption after releases.

High CPU utilization is not automatically a failure. Investigate whether it coincides with degraded latency, timeouts, queue growth, or missed operational targets.

If CPU usage increases, examine request volume, expensive queries, serialization, report generation, retries, background jobs, and AI inference before selecting a scaling action.

### 8.2 Memory

Monitor:

* Available and used memory.
* Application and worker process memory.
* Memory growth over time.
* Swap activity where applicable.
* Out-of-memory events.
* Container or process memory limits.
* Cache memory and eviction behavior.
* Memory consumption during imports, exports, reports, and model loading.

A steadily increasing memory footprint must be investigated even if immediate failures are not occurring.

Restarting a process may restore temporary headroom but does not prove that a memory leak or unbounded workload has been resolved.

### 8.3 Storage

Monitor:

* Total and available capacity.
* Growth rate.
* Database data and index size.
* Transaction logs and database maintenance requirements.
* File and document storage.
* Backup and snapshot storage.
* Temporary files and generated reports.
* Log and trace retention volume.
* Disk latency, throughput, and input/output saturation.
* Inode or equivalent file-system limits where applicable.

Estimate time to exhaustion from recent growth trends, while accounting for known events that may change those trends.

Storage cleanup must follow the applicable retention, backup, subscription lifecycle, and security requirements. Deleting business records or backups must never be used as an improvised capacity-management action.

### 8.4 Network

Monitor relevant network metrics, including:

* Throughput and bandwidth saturation.
* Request failures and timeouts.
* Connection establishment failures.
* Latency between application and dependencies.
* Data transfer costs where billed.
* Traffic spikes after deployment or recovery.
* Large uploads, exports, and offline synchronization batches.

Network problems must be distinguished from application and database bottlenecks before increasing compute capacity.

### 8.5 Connections and concurrency

Monitor:

* API request concurrency.
* Database connection pool utilization.
* Redis connections.
* Worker concurrency.
* File-transfer concurrency.
* External dependency connection limits.
* Queue consumers and scheduler overlap.

Connection pools must be sized against database and dependency limits, not configured independently on each application process.

Increasing application instances can multiply total database connections. The resulting aggregate must remain within a safe database connection budget.

## 9. Application and Dependency Capacity

### 9.1 Backend API

Review API capacity using:

* Request rate by endpoint or operation category.
* Latency distribution.
* Error and timeout rates.
* Concurrency and connection usage.
* CPU and memory consumption.
* Database time per request.
* External dependency time.
* Payload sizes and serialization overhead.
* Retry frequency and repeated requests.
* Expensive reports and bulk operations.

Separate routine POS operations from workloads that may consume significant resources, such as large reports, exports, imports, or administrative bulk actions.

Where necessary, use bounded concurrency, pagination, query optimization, background processing, or workload separation.

Do not move a synchronous business-critical operation into an asynchronous process without explicitly defining its consistency, confirmation, retry, and failure behavior.

### 9.2 PostgreSQL

Database capacity reviews must consider:

* CPU and memory.
* Connection limits and connection pool utilization.
* Query latency and execution plans.
* Slow-query frequency.
* Transaction duration.
* Lock waits and deadlocks.
* Read/write throughput.
* Table and index growth.
* Vacuum and analyze behavior.
* Transaction-log growth.
* Replication lag, if replication is used.
* Backup, restore, and maintenance workload.

When database pressure occurs, first identify whether the cause is inefficient queries, missing or inappropriate indexes, excessive connections, lock contention, high write volume, maintenance activity, or insufficient hardware.

Increasing database size may be necessary, but it must not replace investigation of avoidable query or transaction inefficiencies.

Capacity changes must preserve transaction integrity and the database's established backup and recovery requirements.

### 9.3 Redis and caching

Monitor:

* Memory consumption.
* Evictions.
* Hit and miss rates.
* Connection usage.
* Command latency.
* CPU consumption.
* Key growth and expiration behavior.
* Queue or stream usage, if applicable.
* Cache rebuild load.

Cache growth must have documented retention or eviction behavior. Cache invalidation must preserve correctness.

Cache entries must not be treated as the authoritative source for orders, payments, inventory, cash-register state, subscription status, or permissions unless the architecture explicitly establishes and safeguards that role.

If Redis is also used for queues or coordination, capacity and failure analysis must account for those responsibilities separately.

### 9.4 Background workers and schedulers

Monitor:

* Queue depth.
* Oldest pending job age.
* Job processing duration.
* Job success and failure rates.
* Retry rates.
* Dead-letter or permanently failed jobs, if supported.
* Worker CPU and memory.
* Scheduler execution delays.
* Concurrent job count.
* Dependency pressure created by workers.

A growing queue may indicate insufficient worker capacity, slow dependencies, failed jobs, an unexpectedly high job-production rate, or a scheduler problem.

Adding workers is appropriate only when the downstream database and dependencies can support the additional concurrency.

Business-changing jobs must be idempotent or use equivalent safeguards against duplicate effects. Scaling must not introduce duplicate order processing, inventory deductions, payments, or lifecycle deletions.

### 9.5 Frontend delivery

Where applicable, monitor:

* Static asset delivery latency.
* Asset transfer volume.
* Cache behavior.
* Frontend error rates.
* API latency as experienced by clients.
* Large bundle or asset growth.
* Resource consumption from report pages or large lists.

Frontend optimization must not weaken authentication, authorization, tenant isolation, or the reliability of offline POS behavior.

### 9.6 AI workloads

For AI-enabled components, monitor:

* Inference request rate.
* Inference latency.
* CPU, memory, and accelerator utilization where applicable.
* Model loading and initialization time.
* Queue depth and wait time.
* Batch size and concurrency.
* Failure, timeout, and fallback rates.
* Model artifact storage and transfer.
* Cost per workload unit where measurable.

AI workloads must have explicit resource boundaries so that optional inference cannot exhaust resources required by core ERP operations.

If AI processing degrades, the system must follow its documented fallback or degradation policy. Core order, payment, inventory, and cash-register correctness must not depend on an unverified AI result.

## 10. Infrastructure Cost Monitoring

### 10.1 Cost inventory

Track costs associated with the resources actually used by the deployment, including:

* Compute instances and containers.
* Managed database services or database-hosting infrastructure.
* Storage and backup retention.
* Network traffic and data transfer.
* Load balancing and networking services.
* Redis and other managed dependencies.
* Logging, monitoring, and tracing.
* AI inference and model-serving resources.
* Development, testing, staging, and temporary environments.
* Licenses and third-party services.
* Additional operational services required by the selected architecture.

Not every category will apply to every deployment. The inventory must identify applicable categories rather than assuming a specific cloud provider or technology stack.

### 10.2 Cost dimensions

Where billing and usage data permit, review cost by:

* Environment.
* Service or resource category.
* Restaurant network or subscription plan, when reliable attribution is available.
* Shared platform services.
* AI workload.
* Storage and retention category.
* Development and testing activity.
* Time period.
* Unit of business activity.

Useful normalized indicators may include:

* Infrastructure cost per active branch.
* Cost per completed order.
* Cost per API request.
* Cost per stored data volume.
* Cost per AI inference or processed workload unit.
* Cost per active subscription.

These are analytical indicators, not guaranteed prices. They must use clearly defined numerators, denominators, and time windows.

### 10.3 Shared and tenant-attributed costs

Shared infrastructure may serve multiple restaurant networks and branches.

When direct attribution is unavailable, use a documented allocation method based on measurable drivers such as request volume, storage consumption, processing time, or active usage.

Allocation estimates must be identified as estimates. They must not be presented as exact tenant-level costs when the underlying data does not support that claim.

Tenant-level cost attribution must not expose one customer's business information to another customer.

### 10.4 Cost baselines and budgets

Define a cost baseline for each production environment and material service category.

Where financially appropriate, establish:

* Expected monthly cost range.
* Approved budget.
* Warning and critical variance thresholds.
* Expected growth assumptions.
* Owner responsible for review.
* Approval requirements for material spending changes.
* Actions for unexpected charges.

Budgets and thresholds must be approved rather than invented from unverified assumptions.

Billing data can be delayed, estimated, adjusted, or incomplete. Cost alerts must account for those limitations and must not imply that reported usage always reflects final invoiced amounts.

### 10.5 Cost anomalies

Investigate unexpected cost increases by comparing:

1. The affected billing category and time period.
2. Resource inventory and configuration changes.
3. Traffic, transaction, and queue volume.
4. Storage and backup growth.
5. Logging and telemetry volume.
6. AI workload changes.
7. Failed-job and retry activity.
8. Deployment, recovery, or incident activity.
9. Provider billing adjustments, where applicable.

Do not assume that an increase in cost is caused by legitimate business growth.

Cost spikes may indicate runaway retries, unbounded logging, forgotten test resources, a storage-retention problem, unexpected traffic, or an operational incident.

## 11. Forecasting and Growth Planning

### 11.1 Forecast inputs

Forecasting should use:

* Historical resource utilization.
* Active subscriptions and branches.
* Expected branch growth.
* Order and API throughput.
* User concurrency.
* Data retention requirements.
* Storage growth.
* Queue processing volume.
* Backup growth.
* AI adoption and inference demand.
* Planned features and integrations.
* Expected seasonal or promotional peaks.

Separate observed facts from assumptions. Record the forecast period, uncertainty, and major dependencies.

### 11.2 Forecast scenarios

Maintain suitable scenarios for:

* Expected growth.
* Higher-than-expected business growth.
* Short-lived peak activity.
* Dependency degradation.
* Recovery after a significant outage.
* Offline branches reconnecting and synchronizing accumulated transactions.
* Increased reporting, import, or AI workload.

The platform initially targets restaurant networks with up to 10 branches, but that product assumption does not itself establish a proven capacity limit. The actual safe workload must be validated using representative load tests and production observations.

### 11.3 Forecast review

Review forecasts at a frequency appropriate to growth and risk, and after material changes such as:

* A significant increase in branches or subscriptions.
* A new high-volume feature.
* Database schema or query changes.
* A major architecture change.
* A change in retention policy.
* Introduction of a new AI model or workload.
* Repeated capacity alerts.
* A major incident or recovery event.

Forecasts must be revised when observed behavior materially differs from the assumptions.

## 12. Scaling and Resource Changes

### 12.1 Decision process

Before scaling a resource:

1. Identify the symptom and affected service.
2. Check monitoring data and recent changes.
3. Determine the likely bottleneck.
4. Check whether the bottleneck is capacity-related or caused by errors, contention, configuration, or dependency failure.
5. Estimate the impact of the proposed change.
6. Check downstream resource limits.
7. Review expected cost and security implications.
8. Select the smallest safe change that addresses the verified problem.
9. Define success criteria and a recovery plan.
10. Apply the approved change and verify the result.

### 12.2 Vertical scaling

Vertical scaling increases the resources assigned to an existing component.

Consider it when measurements show that the component is constrained by CPU, memory, storage throughput, or another resource that can be increased safely.

Before applying a vertical change, verify:

* Supported resource sizes and compatibility.
* Required restart or downtime.
* Available headroom during the change.
* Recovery and rollback options.
* Cost impact.
* Database, application, and dependency compatibility.

A larger instance is not a guaranteed solution to inefficient queries, lock contention, memory leaks, or external dependency failures.

### 12.3 Horizontal scaling

Horizontal scaling adds application instances, workers, or other parallel capacity where supported by the architecture.

Before increasing instance count, verify:

* Statelessness or correct shared-state handling.
* Session and authentication behavior.
* Load distribution.
* Database connection multiplication.
* Worker job concurrency and idempotency.
* Scheduler coordination.
* Shared storage and cache behavior.
* Rate limits and downstream quotas.
* Additional monitoring and operating costs.

Do not scale a component horizontally when doing so would create conflicting writers, duplicate scheduled execution, unsafe retries, or uncontrolled load on a shared dependency.

### 12.4 Automatic scaling

Automatic scaling may be used only when supported by the selected deployment architecture.

It must have:

* Documented scaling signals.
* Minimum and maximum resource limits.
* Cooldown or stabilization behavior.
* Appropriate access controls.
* Cost guardrails.
* Dependency-capacity checks.
* Monitoring and failure alerts.
* A safe response when scaling cannot keep up with demand.

Automatic scaling must not be assumed to prevent all overload. Scaling may fail because of quota limits, insufficient capacity, slow initialization, dependency bottlenecks, or a sudden traffic spike.

### 12.5 Capacity changes and releases

Resource changes that alter production behavior must follow the applicable change-management procedure in `18_Release_and_Change_Operations.md`.

Material changes must record the reason, approval, expected impact, cost implications, validation steps, and rollback or recovery plan.

Emergency scaling must be recorded retrospectively if prior approval was impractical under the approved emergency procedure.

## 13. Performance Budgets and Load Testing

### 13.1 Performance requirements

Define performance targets for critical workflows based on business requirements and measured system behavior.

Priority workflows include:

* Creating and accepting orders.
* Updating kitchen order status.
* Completing payment.
* Opening and closing cash registers.
* Inventory deduction and stock validation.
* Recipe and menu operations.
* Cash reconciliation.
* Critical owner dashboards and reports.
* Offline transaction synchronization.
* Subscription enforcement and lifecycle jobs.

Each performance target should identify the operation, measurement point, workload assumptions, acceptable latency, error expectations, and required consistency guarantees.

Final numeric targets must be established and approved through requirements and testing. This document does not invent service-level guarantees.

### 13.2 Load-test requirements

Load tests must use representative workflows and data volumes.

They should assess:

* Normal expected load.
* Expected peak load.
* Increased concurrency.
* Sustained operation.
* Sudden traffic increases.
* Dependency slowdown.
* Queue buildup and recovery.
* Database connection pressure.
* Large report and import workloads.
* Offline synchronization bursts.

Tests must measure both application behavior and downstream resource impact.

A load test is not sufficient if it measures only successful request throughput while ignoring data correctness, errors, tail latency, resource saturation, or queue growth.

### 13.3 Safe test execution

Load tests must run in an authorized environment with appropriate isolation.

Production load testing requires explicit approval, bounded traffic, monitoring, a stop condition, and an impact assessment. Test workloads must not create real customer charges, corrupt production data, or trigger destructive lifecycle actions.

Test results must record the software version, environment, workload profile, test duration, data assumptions, observed results, and known limitations.

### 13.4 Capacity acceptance

A capacity claim must be supported by evidence relevant to the claimed workload.

A successful short test does not prove unlimited scalability or long-term stability. Claims about branch count, concurrent users, orders per second, or response times must state their validated conditions and limitations.

## 14. Alerts and Escalation

Capacity and cost alerts must follow the common monitoring and alerting rules defined in the Operations documentation.

Potential alerts include:

* Sustained CPU saturation associated with service degradation.
* Low available memory or repeated out-of-memory events.
* Storage approaching a critical limit.
* Database connection pool exhaustion.
* Database query latency or lock contention above approved thresholds.
* Redis memory pressure or connection exhaustion.
* Growing queue backlog or excessive oldest-job age.
* Repeated worker or scheduler failures.
* Network saturation or abnormal transfer volume.
* AI inference saturation or resource exhaustion.
* Unexpected cost growth or budget variance.
* Forecasted resource exhaustion within the available response window.
* Sudden increases in logs, traces, backups, or stored files.

Each actionable alert must identify:

* Affected resource or service.
* Severity.
* Detection time.
* Relevant metric and threshold.
* Current impact, if known.
* Responsible owner.
* Initial diagnostic steps.
* Escalation path.
* Link or reference to the relevant runbook.

Thresholds must be calibrated to reduce both missed incidents and excessive false positives.

Cost alerts must not automatically trigger destructive actions unless a separately approved and tested control explicitly authorizes that behavior.

## 15. Capacity Incident Response

When capacity pressure threatens production behavior:

1. Acknowledge and classify the alert.
2. Identify affected services, branches, and business workflows.
3. Check recent deployments, configuration changes, traffic changes, and dependency health.
4. Determine whether the issue affects availability, latency, correctness, or data durability.
5. Apply approved containment or scaling actions.
6. Protect critical business operations and authoritative data.
7. Monitor downstream effects of each change.
8. Communicate material impact through the incident process.
9. Verify recovery using technical metrics and business-level checks.
10. Record evidence and follow-up actions.

If the system is overloaded, safe temporary measures may include reducing nonessential reporting concurrency, limiting expensive administrative workloads, pausing noncritical processing, or adding validated capacity.

Any degraded mode must follow approved business rules. It must not silently lose accepted orders, duplicate financial effects, bypass permissions, or violate inventory constraints.

### 15.1 Offline branch recovery

Branches may continue operating offline and later synchronize accumulated transactions.

Before increasing synchronization concurrency or batch sizes, verify:

* Server-side database headroom.
* API and worker capacity.
* Network constraints.
* Idempotency and duplicate protection.
* Conflict-resolution behavior.
* Ordering and transaction dependencies.
* Retry and backoff behavior.
* Branch-level data isolation.

A synchronization backlog must be drained at a safe rate. Maximizing catch-up speed is not more important than preserving transaction correctness and production stability.

### 15.2 Database pressure

If database capacity is the bottleneck:

* Review slow queries, connection usage, locks, and write throughput.
* Check whether workers or reports are competing with POS operations.
* Reduce unsafe concurrency where appropriate.
* Apply approved query or configuration changes.
* Scale the database only when the evidence supports that action.
* Verify transaction integrity and critical workflows after recovery.

Do not scale API instances blindly when the database is already saturated.

### 15.3 Cost incident

If cost increases unexpectedly:

* Confirm the affected category and time window.
* Identify the responsible resource or workload where possible.
* Check whether the increase threatens an approved budget or service continuity.
* Stop or reduce nonessential consumption only through an approved safe action.
* Preserve required backups, logs, audit evidence, and business data.
* Escalate according to financial impact and operational severity.
* Document the cause, corrective action, and prevention plan.

## 16. Cost Optimization Controls

Optimization must prioritize changes with measurable benefits and acceptable operational risk.

Potential actions include:

* Removing verified unused resources.
* Right-sizing overprovisioned services.
* Optimizing database queries and indexes.
* Limiting unnecessary polling and repeated requests.
* Improving cache behavior where correctness permits.
* Bounding retries and preventing retry storms.
* Controlling log and trace volume while preserving required evidence.
* Applying approved storage lifecycle policies.
* Optimizing backup retention within recovery requirements.
* Scheduling nonproduction resources when they are not needed.
* Reducing redundant data transfer.
* Separating optional AI workloads from critical ERP workloads.
* Improving worker efficiency and queue processing.
* Using suitable pagination and asynchronous processing for expensive operations.

Before adopting an optimization, document:

* Current baseline.
* Proposed change.
* Expected benefit.
* Functional and security risks.
* Validation method.
* Rollback or recovery plan.
* Observed outcome after implementation.

A proposed saving must not be reported as realized until actual usage or billing evidence supports it.

### 16.1 Prohibited shortcuts

Cost optimization must not:

* Disable required backups to reduce storage charges.
* Shorten required retention without approval.
* Remove audit records needed for accountability.
* Expose private files through public access.
* Disable tenant or branch authorization.
* Skip transaction validation.
* Disable critical monitoring without an approved replacement.
* Permit negative stock or duplicate financial effects.
* Automatically delete customer data outside the approved lifecycle.
* Remove recovery capacity without reviewing recovery objectives.
* Reduce essential POS capacity without evaluating business impact.

## 17. Storage and Data Growth

Data growth must be reviewed across:

* Orders and order history.
* Inventory movements and stock snapshots.
* Cash-register records and financial history.
* Audit logs.
* Employee and permission records.
* Uploaded files and generated reports.
* Database indexes and transaction logs.
* Backups and recovery copies.
* Monitoring and diagnostic data.
* AI model artifacts and inference-related data, where applicable.

Growth forecasts must account for required retention periods and deletion rules.

Subscription expiry and customer-data lifecycle processing must follow `16_Subscription_and_Data_Lifecycle_Operations.md`. Capacity pressure is not authorization to accelerate customer-data deletion.

Storage reclamation procedures must verify that data is eligible for removal, that required retention holds are respected, and that the intended result has been achieved.

## 18. Environment Management

Production, staging, testing, development, and temporary environments must be identified separately for capacity and cost reporting.

For each nonproduction environment, define:

* Business or engineering purpose.
* Owner.
* Expected usage period.
* Resource limits where appropriate.
* Data classification.
* Backup requirements.
* Availability expectations.
* Cleanup or shutdown criteria.
* Approval requirements for exceptions.

Nonproduction environments must not use production customer data unless an approved, secure process explicitly permits it.

Temporary environments must have a clear owner and lifecycle. Resources must not remain active indefinitely simply because no one remembers who created them.

Production and recovery resources must not be removed as unused without checking their operational purpose.

## 19. Resource Quotas and Fairness

Where resource quotas or per-tenant limits are implemented, they must be aligned with the approved subscription and service model.

Potential controls include:

* Concurrent request limits.
* Report-generation limits.
* Import size limits.
* Background job concurrency.
* File storage quotas.
* API rate limits.
* AI workload quotas.

These controls must have documented enforcement behavior and appropriate error handling.

Quota enforcement must not bypass authorization or allow one restaurant network to access another network's resources.

A tenant-specific limit must not create uncontrolled contention for shared resources. Conversely, global overload protection must not arbitrarily corrupt or discard valid tenant operations.

Subscription feature restrictions and resource quotas are distinct concepts. A subscription plan's enabled features do not automatically define a technically safe resource allocation unless that relationship has been explicitly designed and documented.

## 20. Evidence and Reporting

Maintain evidence sufficient to explain capacity decisions and cost changes.

Evidence may include:

* Resource inventory snapshots.
* Utilization dashboards and metric exports.
* Load-test reports.
* Capacity forecasts and assumptions.
* Cost reports and billing exports.
* Budget variance reports.
* Scaling and configuration change records.
* Incident timelines.
* Database and queue diagnostic summaries.
* Storage growth reports.
* Approval records.
* Post-change validation results.
* Cost optimization results.
* Follow-up actions and their status.

Evidence must be stored with suitable access control and retention.

Reports must distinguish observed measurements, estimates, forecasts, and assumptions. Sensitive credentials, access tokens, payment data, and unnecessary customer information must not be included in evidence.

## 21. Operational Review Schedule

The exact schedule must reflect deployment scale and risk. At minimum, establish the following review cadence:

| Frequency                       | Required activity                                                                                                                |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Continuous or near-real-time    | Monitor critical service health, saturation, errors, and actionable capacity alerts.                                             |
| Daily                           | Review unresolved critical capacity alerts, abnormal growth, queue backlog, and material cost anomalies where data is available. |
| Weekly                          | Review resource trends, recurring alerts, storage growth, and unresolved capacity risks.                                         |
| Monthly                         | Review cost, forecasts, environment inventory, resource allocation, and optimization opportunities.                              |
| Before material releases        | Review expected workload impact, resource requirements, migration impact, and rollback readiness.                                |
| After major incidents           | Review capacity contribution, recovery workload, cost impact, and corrective actions.                                            |
| Periodically, according to risk | Run representative load tests, review forecasts, and verify capacity assumptions.                                                |

A completed review must record its date, reviewer, findings, decisions, and assigned actions.

## 22. Standard Capacity Review Procedure

Use this procedure for scheduled reviews and material capacity concerns.

### Step 1: Establish the review scope

Identify the environment, time period, services, resource categories, and business workflows under review.

### Step 2: Collect measurements

Collect utilization, latency, throughput, errors, storage growth, queue behavior, and cost data relevant to the scope.

### Step 3: Compare with baselines

Compare current measurements against approved baselines, budgets, thresholds, and prior periods.

### Step 4: Identify the bottleneck or variance

Determine whether the main issue is insufficient capacity, inefficient behavior, abnormal workload, a dependency problem, or unexpected billing.

### Step 5: Evaluate options

Compare optimization, configuration changes, workload limits, and scaling options. Include cost, reliability, security, and recovery implications.

### Step 6: Approve the action

Obtain the required approval based on the risk and cost of the proposed change.

### Step 7: Apply the change

Use the approved change procedure and preserve a record of the configuration before and after the change.

### Step 8: Validate the outcome

Compare post-change measurements against the original baseline and verify affected business workflows.

### Step 9: Record and follow up

Record the result, remaining risks, cost impact, and corrective actions. Reopen the issue if the evidence does not demonstrate a safe outcome.

## 23. Operational Readiness Checklist

Before declaring capacity and cost operations ready, verify:

* [ ] Production resources have identified owners.
* [ ] Critical resources are included in monitoring.
* [ ] Capacity baselines and thresholds are documented.
* [ ] Database and connection limits are understood.
* [ ] Worker and queue limits are documented.
* [ ] Storage and backup growth are monitored.
* [ ] Infrastructure costs can be reviewed by relevant categories.
* [ ] Budget ownership and escalation are defined where applicable.
* [ ] Capacity forecasts state their assumptions.
* [ ] Load-test evidence supports material capacity claims.
* [ ] Scaling procedures include dependency checks.
* [ ] Cost-control actions cannot silently destroy business data.
* [ ] Offline synchronization has safe concurrency and retry behavior.
* [ ] AI workloads have appropriate resource boundaries.
* [ ] Resource changes follow change-management requirements.
* [ ] Incident procedures include capacity-related scenarios.
* [ ] Evidence is retained with appropriate access controls.
* [ ] Review findings produce tracked corrective actions.

## 24. Mandatory Operational Invariants

The following invariants are mandatory.

1. Every critical production resource must have an identified owner.
2. Material capacity decisions must be supported by measurements or explicitly documented assumptions.
3. Capacity thresholds must be appropriate to the deployed architecture.
4. Resource inventories must distinguish production and nonproduction resources.
5. Critical service health must not rely on CPU utilization alone.
6. Memory growth must be reviewed when it indicates possible instability.
7. Storage capacity and growth must be monitored.
8. Storage cleanup must follow approved retention and deletion policies.
9. Database connection budgets must account for all application instances and workers.
10. API scaling must not silently exhaust database connections.
11. Database capacity changes must preserve transaction integrity.
12. Query optimization must be considered when evidence indicates inefficient queries.
13. Cache behavior must not silently become the authoritative source of business state.
14. Redis capacity must account for its actual roles in the architecture.
15. Worker scaling must respect downstream dependency limits.
16. Business-changing jobs must be idempotent or equivalently protected against duplicate effects.
17. Queue growth must be evaluated using both depth and job age where available.
18. Scheduler scaling must not create uncontrolled duplicate execution.
19. AI workloads must not be allowed to exhaust resources required by critical ERP operations.
20. AI degradation must follow the documented fallback policy.
21. Cost reports must distinguish measured values from estimates.
22. Shared-cost allocation must document its method and limitations.
23. Cost anomalies must be investigated rather than automatically attributed to business growth.
24. Budget thresholds must have an assigned owner and response procedure.
25. Scaling changes must account for both direct and downstream costs.
26. Automatic scaling must have defined limits and failure handling.
27. Material resource changes must follow approved change controls.
28. Emergency resource changes must be documented and reviewed.
29. Load tests must not compromise production data or create unauthorized financial effects.
30. Capacity claims must state the conditions under which they were validated.
31. Critical POS workflows must be included in capacity validation.
32. Offline synchronization must preserve idempotency and transaction dependencies.
33. Synchronization backlog recovery must not destabilize normal production traffic.
34. Cost optimization must not bypass authentication or authorization.
35. Cost optimization must not disable required backups or audit evidence without approved policy changes.
36. Customer-data deletion must follow the approved subscription and lifecycle policy.
37. Resource removal must include dependency and ownership checks.
38. Temporary resources must have an owner and lifecycle.
39. Production and recovery resources must not be removed solely because they appear idle.
40. Telemetry reduction must preserve the evidence required for security and incident response.
41. Capacity alerts must identify an actionable owner or escalation path.
42. Alert thresholds must be reviewed when system behavior or architecture changes.
43. Capacity incidents must be validated using technical and business evidence.
44. Restarting a service must not be treated as proof that a capacity problem is resolved.
45. Resource changes must be evaluated for security and tenant-isolation impact.
46. Tenant-level cost reporting must not disclose another tenant's information.
47. Subscription feature restrictions and infrastructure resource quotas must remain conceptually distinct.
48. Cost savings must not be claimed as realized without supporting evidence.
49. Forecasts must be updated when actual workload materially differs from assumptions.
50. Capacity and cost reviews must result in documented decisions, tracked actions, or an explicit conclusion that no change is required.

## 25. Acceptance Criteria

This document is considered operationally implemented when:

* Resource inventory and ownership are established.
* Monitoring covers the critical resource categories used by the deployment.
* Capacity thresholds and escalation procedures are documented.
* Cost reporting and budget ownership are defined for applicable resources.
* Forecasts and load-test evidence support the platform's current workload assumptions.
* Scaling and resource-change procedures are approved.
* Storage, backup, database, queue, and AI capacity risks are reviewed.
* Offline recovery workloads have a documented capacity and safety strategy.
* Cost optimization follows security, data-integrity, and retention requirements.
* Capacity reviews and incidents produce auditable evidence and tracked actions.

The absence of a dedicated cloud-cost platform does not remove these requirements. Where automated tooling is unavailable, an approved manual process must provide equivalent operational visibility appropriate to the system's scale.

## 26. Document Maintenance

The Operations owner must review this document:

* After a material infrastructure or architecture change.
* After a significant capacity-related incident.
* When subscription or workload assumptions change.
* When resource allocation or cost ownership changes.
* When load-test results invalidate existing capacity assumptions.
* During the scheduled documentation review cycle.

Changes must preserve consistency with the related Operations, Architecture, Deployment, Security, and Testing documents.

**End of Document**

