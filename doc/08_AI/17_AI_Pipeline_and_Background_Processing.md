# AI Pipeline and Background Processing

**Document ID:** AI-17
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_AI/README.md`

---

## 1. Purpose

This document defines the architecture for AI pipelines and background processing within FastFood ERP.

The system must support AI workloads that are too expensive, slow, periodic, or asynchronous to execute inside the normal ERP request/response lifecycle.

The architecture must ensure that:

* AI processing does not block core ERP operations;
* long-running workloads are executed asynchronously;
* AI jobs are retryable and idempotent;
* pipeline dependencies are explicit;
* partial failures are recoverable;
* Business and Branch isolation is preserved;
* subscription and authorization rules are revalidated before execution;
* model, feature and data versions remain traceable;
* background processing is resource-limited;
* historical processing and backfill are supported;
* failed jobs do not silently corrupt AI state.

The core principle is:

> AI processing is an asynchronous intelligence layer and must remain independent from authoritative ERP transaction correctness.

---

# 2. Scope

This document covers:

* AI jobs;
* background processing;
* AI pipelines;
* pipeline stages;
* job queues;
* workers;
* scheduling;
* event-driven processing;
* batch processing;
* pipeline dependencies;
* DAG execution;
* job priorities;
* concurrency;
* resource quotas;
* idempotency;
* retries;
* dead-letter handling;
* checkpoints;
* pause/resume;
* cancellation;
* backfill;
* replay;
* partial success;
* feature generation;
* inference jobs;
* training-related jobs;
* evaluation jobs;
* report/insight generation jobs;
* LLM jobs;
* Business/Branch isolation;
* subscription validation;
* authorization validation;
* model/feature/data version compatibility;
* transaction boundaries;
* Outbox integration;
* observability;
* failure recovery;
* performance and SLOs.

This document does not define the complete AI model lifecycle.

Model lifecycle is defined in:

`14_AI_Model_Registry_and_Versioning.md`

Inference execution is defined in:

`15_AI_Inference_and_Runtime_Architecture.md`

Feature computation and caching are defined in:

`16_AI_Feature_and_Caching_Architecture.md`

---

# 3. Core Principle

AI background processing must never become part of an authoritative ERP transaction unless explicitly required by a separately defined business rule.

For example:

```text id="pl001"
Order Paid
    ↓
ERP Transaction Commits
    ↓
Outbox Event
    ↓
AI Background Job
```

If the AI job fails:

```text id="pl002"
AI Job Failed
```

the already committed Order and Payment remain valid.

AI processing failure must not roll back the original ERP transaction.

---

# 4. AI Processing Model

The general architecture is:

```text id="pl003"
ERP / Scheduler / AI API
        ↓
Job Creation
        ↓
Queue
        ↓
Worker
        ↓
Pipeline Orchestrator
        ↓
Pipeline Stages
        ↓
Feature / Model / LLM / Analysis
        ↓
Validation
        ↓
AI Result
        ↓
Persistence / Notification / Report
```

Each stage must have a clearly defined responsibility.

---

# 5. AI Job

An AI Job represents one asynchronous unit of AI work.

A job should have:

* Job UUID;
* Business UUID;
* Branch UUID where applicable;
* Job Type;
* Priority;
* Status;
* Pipeline UUID where applicable;
* Pipeline Version;
* Feature Version references;
* Model Version references;
* Input reference;
* Output reference;
* correlation ID;
* idempotency key;
* creation timestamp;
* scheduled timestamp;
* started timestamp;
* completed timestamp;
* retry count;
* error state.

---

# 6. Job Lifecycle

A job may follow:

```text id="pl004"
CREATED
   ↓
QUEUED
   ↓
RUNNING
   ↓
SUCCEEDED
```

Failure path:

```text id="pl005"
RUNNING
   ↓
FAILED
   ↓
RETRY_PENDING
   ↓
QUEUED
```

Permanent failure:

```text id="pl006"
FAILED
   ↓
DEAD_LETTERED
```

Cancellation:

```text id="pl007"
QUEUED / RUNNING
   ↓
CANCEL_REQUESTED
   ↓
CANCELLED
```

Long-running jobs may additionally support:

```text id="pl008"
PAUSED
RESUMABLE
```

---

# 7. Job Types

The system should support multiple AI job categories.

Examples:

* feature computation;
* feature refresh;
* feature backfill;
* inference;
* batch inference;
* model evaluation;
* training;
* experiment execution;
* anomaly analysis;
* business insight generation;
* recommendation generation;
* LLM analysis;
* report enrichment;
* data quality analysis;
* model monitoring;
* drift analysis.

Each job type has its own resource and priority policy.

---

# 8. Job Type Contract

Every job type should define:

* input schema;
* output schema;
* required authorization;
* required subscription entitlement;
* allowed scope;
* resource limits;
* timeout;
* retry policy;
* idempotency strategy;
* observability requirements;
* failure policy.

Workers must not execute unknown or unregistered job types.

---

# 9. Pipeline

A pipeline is an ordered set of AI processing stages.

Example:

```text id="pl009"
ERP Data
   ↓
Feature Preparation
   ↓
Feature Validation
   ↓
Model Inference
   ↓
Output Validation
   ↓
Business Interpretation
   ↓
Result Persistence
```

A pipeline may contain:

* sequential stages;
* parallel stages;
* conditional stages;
* aggregation stages.

---

# 10. Pipeline Versioning

Production pipelines must be versioned.

Example:

```text id="pl010"
Demand Pipeline v1
Demand Pipeline v2
Demand Pipeline v3
```

A pipeline version identifies:

* stage definitions;
* dependency structure;
* feature contracts;
* model references;
* validation rules;
* output contract.

Changing operational behavior requires a new pipeline version.

---

# 11. Pipeline Lifecycle

Pipeline versions may follow:

```text id="pl011"
DRAFT
   ↓
TESTING
   ↓
VALIDATED
   ↓
APPROVED
   ↓
ACTIVE
   ↓
DEPRECATED
   ↓
RETIRED
```

Only approved and active pipelines may process production workloads.

---

# 12. Pipeline Stage

Each stage must have a defined contract.

A stage should specify:

* Stage UUID;
* stage type;
* input schema;
* output schema;
* dependencies;
* timeout;
* retry policy;
* resource requirements;
* idempotency behavior;
* failure behavior.

A stage must not rely on undocumented side effects from another stage.

---

# 13. Pipeline Dependency Graph

Pipeline stages form a directed dependency graph.

Example:

```text id="pl012"
             ┌→ Feature A ─┐
ERP Data ────┤             ├→ Model Input → Inference
             └→ Feature B ─┘
```

Dependencies must be explicit.

Circular dependencies are prohibited.

---

# 14. DAG Requirement

Complex pipelines should be represented as a Directed Acyclic Graph.

A valid pipeline:

```text id="pl013"
A → B → C
A → D → C
```

An invalid pipeline:

```text id="pl014"
A → B → C → A
```

The system must reject circular pipeline definitions before activation.

---

# 15. Pipeline Orchestration

The pipeline orchestrator is responsible for:

* dependency resolution;
* stage scheduling;
* state tracking;
* retries;
* checkpointing;
* cancellation;
* failure propagation;
* output routing;
* pipeline completion.

The orchestrator must not contain business logic that belongs to individual stages.

---

# 16. Queue Architecture

AI jobs should be processed through queues.

Example:

```text id="pl015"
Job Producer
     ↓
Queue
     ↓
Worker Pool
     ↓
Job Execution
```

Different job categories may use separate queues.

---

# 17. Queue Categories

Recommended logical queues:

```text id="pl016"
ai.interactive
ai.high_priority
ai.standard
ai.batch
ai.training
ai.backfill
ai.llm
ai.recovery
```

Exact physical queues may be simplified based on deployment scale.

---

# 18. Queue Priority

Jobs should have explicit priority.

Example:

```text id="pl017"
P0 Critical
P1 High
P2 Standard
P3 Background
P4 Backfill
```

Priority must not allow AI jobs to starve core ERP workers.

Core ERP transaction processing always has higher infrastructure priority than AI processing.

---

# 19. Worker Architecture

Workers execute individual jobs or pipeline stages.

A worker should:

1. receive a job;
2. validate job state;
3. validate Business state;
4. validate subscription;
5. validate authorization;
6. validate input;
7. execute stage;
8. validate output;
9. persist result;
10. update job state;
11. emit required events.

---

# 20. Worker Isolation

Workers should be isolated from one another.

A failed or resource-heavy job must not crash unrelated workers.

Where necessary, resource-heavy workloads should use separate worker pools.

Examples:

```text id="pl018"
CPU Worker Pool
GPU Worker Pool
LLM Worker Pool
Batch Worker Pool
Backfill Worker Pool
```

---

# 21. Worker Concurrency

Concurrency must be explicitly bounded.

Limits may apply to:

* global workers;
* Business;
* Branch;
* job type;
* model;
* pipeline;
* GPU;
* CPU;
* database connections.

Unlimited AI concurrency is prohibited.

---

# 22. Business Fairness

One Business must not monopolize the worker system.

Example:

```text id="pl019"
Business A → 500 backfill jobs
Business B → 5 interactive jobs
```

Business B's interactive jobs must still receive reasonable execution capacity.

Fair scheduling or per-Business quotas should be used.

---

# 23. Branch Fairness

Branch-scoped workloads may be independently limited.

A high-volume Branch must not prevent other Branches within the same Business from receiving required AI processing.

---

# 24. Job Admission Control

Before a job enters active execution, the system may check:

* subscription entitlement;
* Business state;
* Branch state;
* queue capacity;
* resource availability;
* concurrency limit;
* job validity.

Jobs that exceed limits should remain queued, delayed, or rejected according to policy.

---

# 25. Subscription Validation

AI job creation may check subscription entitlement.

However, queued jobs must also revalidate entitlement immediately before execution.

This prevents:

```text id="pl020"
Job Created
   ↓
Subscription Expires
   ↓
Old Job Executes
```

without authorization.

---

# 26. Business Lifecycle Validation

Workers must validate Business lifecycle state.

A job must not execute for a Business that is:

* DELETED;
* DELETING;
* otherwise prohibited by lifecycle rules.

READ_ONLY behavior depends on the specific AI capability.

---

# 27. Branch Lifecycle Validation

Branch-scoped jobs must verify that the Branch remains valid.

A job created for an inactive Branch must not blindly execute against current operational data.

Historical jobs may continue only when explicitly allowed.

---

# 28. Authorization Revalidation

Authorization at job creation is not sufficient.

The worker must revalidate:

* Business;
* Branch;
* employee authority where applicable;
* subscription;
* AI capability entitlement;
* requested operation.

This is especially important for delayed jobs.

---

# 29. Job Ownership

Every job must identify its source.

Possible sources:

```text id="pl021"
USER
SYSTEM
SCHEDULER
EVENT
PIPELINE
RECOVERY
BACKFILL
```

For user-created jobs, the initiating employee should be recorded.

---

# 30. Correlation

Jobs must support:

* correlation ID;
* causation ID;
* parent job ID;
* pipeline execution ID;
* stage execution ID.

This allows complete execution tracing.

---

# 31. Idempotency

Every retryable job must have an idempotency strategy.

Recommended identity:

```text id="pl022"
Business
+
Job Type
+
Operation UUID
+
Scope
+
Pipeline Version
```

Repeated delivery must not create duplicate authoritative AI results.

---

# 32. At-Least-Once Delivery

The queue system may provide at-least-once delivery.

Therefore workers must assume:

```text id="pl023"
Same Job
→
May be Delivered More Than Once
```

Worker execution must be safe under duplicate delivery.

---

# 33. Duplicate Execution

Duplicate execution may happen because of:

* worker crash;
* acknowledgement timeout;
* network interruption;
* retry;
* queue redelivery.

The result persistence layer must detect duplicate execution.

---

# 34. Idempotent Result Persistence

A result should be uniquely identifiable by the operation that produced it.

Example:

```text id="pl024"
Prediction:
Business
+
Model Version
+
Input Snapshot
+
Operation UUID
```

Duplicate writes must not create conflicting duplicate results.

---

# 35. Retry Policy

Retryable errors should use:

* exponential backoff;
* jitter;
* maximum attempts;
* timeout;
* failure classification.

Example:

```text id="pl025"
Attempt 1 → immediate
Attempt 2 → delayed
Attempt 3 → longer delay
Attempt 4 → final retry
```

Exact delays are configuration.

---

# 36. Retryable Errors

Typical retryable errors include:

* temporary database connection failure;
* temporary Redis failure;
* temporary external AI provider failure;
* network timeout;
* worker infrastructure failure;
* temporary resource exhaustion.

---

# 37. Non-Retryable Errors

Typical permanent errors include:

* invalid input;
* incompatible feature version;
* unauthorized operation;
* invalid model;
* invalid pipeline;
* corrupted artifact;
* unsupported schema;
* Business deleted.

These should not retry indefinitely.

---

# 38. Dead Letter Queue

Jobs that exceed retry limits should enter a Dead Letter state.

The system must preserve:

* Job UUID;
* Pipeline UUID/version;
* stage;
* Business;
* Branch;
* error class;
* error message;
* attempt count;
* timestamps;
* correlation ID.

DLQ jobs must remain inspectable.

---

# 39. DLQ Recovery

Authorized operators may:

* inspect;
* retry;
* cancel;
* requeue;
* mark permanently failed.

Retrying a DLQ job must create a traceable new execution attempt.

---

# 40. Checkpointing

Long-running pipelines should support checkpoints.

A checkpoint may contain:

* pipeline execution ID;
* stage;
* partition;
* completed entities;
* output references;
* feature version;
* model version;
* timestamp.

Checkpointing allows recovery without restarting the entire pipeline.

---

# 41. Batch Processing

Large AI workloads must use bounded batches.

Example:

```text id="pl026"
100,000 Products
        ↓
Batch 1
Batch 2
...
Batch N
```

Batch size must be configurable.

Large unbounded operations are prohibited.

---

# 42. Partial Success

A batch may partially succeed.

Example:

```text id="pl027"
Batch 100 items
→ 96 succeeded
→ 4 failed
```

The system should preserve successful results and isolate failed items where safe.

The entire batch should not necessarily be rolled back.

---

# 43. Partial Failure Policy

Partial failure handling must depend on stage semantics.

For independent feature computations:

```text successful items → persist
failed items → retry
```

For a strongly coupled model input:

```text missing required feature
→ inference blocked
```

---

# 44. Pipeline Transaction Boundary

AI pipeline stages should not use one giant database transaction across the entire pipeline.

Instead:

```text id="pl028"
Stage 1
  ↓
Commit
  ↓
Stage 2
  ↓
Commit
  ↓
Stage 3
  ↓
Commit
```

This prevents long-running transactions.

---

# 45. Core ERP Transaction Boundary

If an AI job is triggered by an ERP transaction:

```text id="pl029"
ERP Transaction
   ↓
Commit
   ↓
Outbox
   ↓
AI Job
```

AI processing must not be required for the ERP transaction to commit.

---

# 46. Outbox Integration

The preferred event-driven trigger is:

```text id="pl030"
ERP Domain Event
      ↓
Transactional Outbox
      ↓
Event Publisher
      ↓
AI Job Producer
      ↓
AI Queue
      ↓
AI Worker
```

This prevents event loss between database commit and job creation.

---

# 47. Event Deduplication

The AI job producer must tolerate duplicate events.

An event may result in:

```text id="pl031"
one event
→
one logical job
```

even if the physical event is delivered multiple times.

---

# 48. Event Ordering

Some AI pipelines depend on event ordering.

Where ordering matters, the system should use:

* entity key;
* sequence number;
* event timestamp;
* source version.

The system must not assume global event ordering.

---

# 49. Eventual Consistency

AI background processing is generally eventually consistent.

Example:

```text id="pl032"
Order Paid
      ↓
ERP Updated Immediately
      ↓
AI Feature Updated Later
```

This is acceptable unless a specific AI capability requires stronger freshness.

---

# 50. Job Scheduling

Jobs may be scheduled by:

* cron-like schedules;
* interval schedules;
* event triggers;
* manual requests;
* dependency completion;
* recovery triggers.

Scheduler state must be persistent enough to prevent accidental loss of scheduled work.

---

# 51. Scheduled Job Deduplication

If a scheduler restarts, it must not create uncontrolled duplicate jobs.

A scheduled job should use a deterministic execution identity.

Example:

```text id="pl033"
daily-demand-analysis
+
Business
+
2026-10-05
```

---

# 52. Misfire Handling

If a scheduled job was missed because the system was unavailable, policy must determine whether to:

* execute immediately;
* skip;
* execute once;
* execute all missed periods.

The policy must be explicit per job type.

---

# 53. Overlapping Schedules

A recurring job must define whether overlapping executions are allowed.

Examples:

```text id="pl034"
ALLOW_OVERLAP
SKIP_IF_RUNNING
QUEUE_NEXT
REPLACE_PREVIOUS
```

Default behavior should avoid uncontrolled overlapping expensive workloads.

---

# 54. Pipeline Parallelism

Independent pipeline stages may run in parallel.

Example:

```text id="pl035"
          ┌→ Feature A ─┐
Input ────┤             ├→ Inference
          └→ Feature B ─┘
```

Parallelism must remain resource-limited.

---

# 55. Pipeline Barrier

A downstream stage starts only after all required dependencies succeed.

Example:

```text id="pl036"
Feature A ─┐
Feature B ─┼→ Model Input
Feature C ─┘
```

If Feature B is mandatory and fails:

```text
Inference
   ↓
BLOCKED
```

---

# 56. Conditional Stages

Pipelines may contain conditional logic.

Example:

```text id="pl037"
Anomaly Score
     ↓
score > threshold?
   /       \
 Yes        No
 ↓          ↓
LLM        Finish
Analysis
```

Conditions must be deterministic and versioned.

---

# 57. Pipeline Timeout

Every pipeline and stage must have timeout limits.

A timeout must result in:

* stage failure;
* retry where allowed;
* checkpoint preservation where possible;
* final failure classification.

Workers must not remain occupied indefinitely.

---

# 58. Cancellation

Authorized users or system operators may cancel eligible jobs.

Cancellation must be cooperative where possible.

A cancellation request must not leave the system falsely reporting the job as successful.

---

# 59. Cancellation During Stage

If cancellation occurs during a stage:

* the stage should stop at a safe checkpoint;
* partial output must be marked appropriately;
* final job state becomes CANCELLED;
* incomplete output must not be treated as complete.

---

# 60. Pause and Resume

Long-running jobs may support pause/resume.

Pause should:

* prevent new work;
* preserve checkpoint;
* release unnecessary resources;
* keep state resumable.

Resume must revalidate:

* Business;
* subscription;
* authorization;
* model version;
* feature compatibility.

---

# 61. Replay

Replay means executing a historical pipeline again using defined versions.

Replay must explicitly identify:

* source dataset;
* pipeline version;
* feature versions;
* model version;
* execution time;
* reason.

Replay must not silently replace historical results.

---

# 62. Backfill

Backfill processes historical periods using a specified feature/pipeline version.

Example:

```text id="pl038"
Demand Pipeline v3
       ↓
Backfill
       ↓
2025-01 → 2026-01
```

Backfill must be:

* asynchronous;
* partitioned;
* rate-limited;
* resumable;
* observable.

---

# 63. Backfill Isolation

Backfill must not overload operational ERP resources.

Possible controls:

* low-priority queue;
* bounded database connections;
* limited concurrency;
* batch size;
* scheduling windows;
* read replicas where available.

---

# 64. Historical Reprocessing

Historical reprocessing must preserve the distinction between:

```text id="pl039"
Original Result
```

and:

```text
Reprocessed Result
```

A new execution must never silently rewrite the original lineage.

---

# 65. Pipeline Input Snapshot

Where reproducibility matters, the pipeline should use an input snapshot.

The snapshot may reference:

* source dataset;
* feature snapshot;
* ERP period;
* configuration version;
* model version.

This reduces ambiguity caused by changing live data during long-running processing.

---

# 66. Pipeline Output

Pipeline output must have an explicit contract.

Possible outputs:

* feature values;
* predictions;
* anomaly events;
* recommendations;
* insights;
* report data;
* LLM responses;
* evaluation metrics.

Output must pass validation before being published.

---

# 67. Output Validation

Before successful completion:

```text id="pl040"
Pipeline Output
     ↓
Schema Validation
     ↓
Business Validation
     ↓
Scope Validation
     ↓
Quality Validation
     ↓
Persist
```

Invalid output must not be published as valid AI state.

---

# 68. AI Recommendation Output

Recommendations are non-authoritative.

Example:

```text id="pl041"
AI:
"Buy approximately 30 kg of meat."
```

does not automatically create:

```text
Purchase
```

A normal authorized ERP workflow must execute any real business action.

---

# 69. LLM Background Jobs

LLM jobs may be asynchronous when:

* processing large context;
* generating reports;
* generating business summaries;
* analyzing anomalies;
* generating recommendations.

LLM jobs must use the guardrails defined in:

`12_AI_Prompt_Context_and_Guardrails.md`

---

# 70. LLM Job Context Revalidation

Before execution, the worker must rebuild or validate:

* Business context;
* Branch context;
* employee authorization;
* subscription entitlement;
* allowed tools;
* data freshness;
* prompt version.

A queued LLM job must not blindly reuse authorization from job creation time.

---

# 71. External AI Provider Jobs

When an external AI provider is used:

* request size must be bounded;
* timeout must be defined;
* retries must be controlled;
* sensitive data must be minimized;
* provider failures must be isolated;
* provider output must be validated.

External provider availability must not affect core ERP transaction processing.

---

# 72. Provider Retry

Retries to external AI providers must respect:

* provider rate limits;
* configured retry count;
* exponential backoff;
* circuit breaker;
* idempotency where supported.

Unbounded retries are prohibited.

---

# 73. Resource Quotas

AI processing should enforce quotas for:

* CPU;
* memory;
* GPU;
* tokens;
* external provider requests;
* database connections;
* queue depth;
* execution time.

Quotas may be defined globally and per Business.

---

# 74. Token Quotas

LLM workloads should enforce:

* maximum input tokens;
* maximum output tokens;
* maximum context size;
* maximum requests per period.

Token limits must prevent one Business from consuming disproportionate resources.

---

# 75. Cost Controls

AI jobs may have estimated resource/cost metadata.

Examples:

```text id="pl042"
estimated_cpu
estimated_memory
estimated_tokens
estimated_external_cost
```

Jobs exceeding configured limits may be delayed or rejected.

---

# 76. Resource Admission

Before expensive jobs start, the worker system may verify:

```text id="pl043"
Quota Available?
   ↓
Yes → Execute
No  → Queue / Reject
```

Admission control protects system stability.

---

# 77. Worker Autoscaling

If infrastructure supports autoscaling, worker pools may scale based on:

* queue depth;
* execution latency;
* CPU utilization;
* memory;
* GPU utilization;
* job priority.

Autoscaling must retain maximum limits.

---

# 78. GPU Workloads

GPU workers are optional.

GPU use should be justified by:

* model requirements;
* throughput requirements;
* latency requirements;
* cost analysis.

CPU execution remains the default where practical.

---

# 79. Database Connection Limits

AI workers must use separate or explicitly bounded database connection pools.

AI workloads must not consume all connections required by:

* API;
* POS;
* synchronization;
* authentication;
* reporting.

---

# 80. Queue Backpressure

If queues become overloaded:

```text id="pl044"
Queue Depth ↑
     ↓
Backpressure
     ↓
Delay / Throttle
```

The system should reduce low-priority processing before affecting interactive workloads.

---

# 81. Priority Inversion Prevention

A low-priority backfill must not hold resources required by high-priority inference.

Resource allocation must consider priority.

---

# 82. Pipeline State Persistence

Pipeline execution state must be persisted outside worker memory.

A worker restart must not destroy knowledge of:

* current stage;
* completed stages;
* pending stages;
* retry count;
* checkpoint;
* final state.

---

# 83. Worker Restart Recovery

If a worker crashes:

```text id="pl045"
Worker Crash
   ↓
Job Lease Expires
   ↓
Job Requeued
   ↓
Retry
```

The result must remain idempotent.

---

# 84. Job Lease

Long-running jobs may use a lease.

The worker periodically renews the lease.

If the lease expires:

```text id="pl046"
Job considered recoverable
```

and may be reassigned.

---

# 85. Zombie Job Prevention

A job must not remain permanently in:

```text
RUNNING
```

without heartbeat or lease renewal.

Monitoring should detect stale executions.

---

# 86. Pipeline Heartbeat

Long-running pipeline executions should report:

* current stage;
* progress;
* heartbeat timestamp;
* processed count;
* remaining count where known.

---

# 87. Progress Tracking

Where meaningful, jobs should expose progress:

```text id="pl047"
Processed: 6,500
Total: 10,000
Progress: 65%
```

Progress values must not be fabricated when total work is unknown.

---

# 88. Observability

The system should monitor:

* queue depth;
* queue wait time;
* job duration;
* stage duration;
* success rate;
* retry rate;
* failure rate;
* DLQ count;
* worker utilization;
* CPU;
* memory;
* GPU;
* token usage;
* external provider latency;
* pipeline completion rate.

---

# 89. Correlation and Tracing

Every pipeline execution should be traceable:

```text id="pl048"
Correlation ID
   ↓
Pipeline Execution
   ↓
Job
   ↓
Stage
   ↓
Model/Feature/LLM
```

This is required for troubleshooting.

---

# 90. Logging

Logs should include:

* Job UUID;
* Pipeline UUID/version;
* Stage UUID;
* Business UUID;
* Branch UUID where applicable;
* correlation ID;
* worker ID;
* status;
* duration;
* error class.

Sensitive input and feature values must not be logged by default.

---

# 91. Metrics Cardinality

Business and Branch identifiers should not be blindly inserted into high-cardinality metrics labels.

Where necessary:

* use logs/traces for detailed identity;
* use bounded metric dimensions;
* aggregate Business-level statistics.

---

# 92. Audit

The following operations should be auditable:

* manual pipeline execution;
* manual backfill;
* model/pipeline activation;
* cancellation of sensitive jobs;
* administrative retry;
* DLQ recovery;
* feature recomputation;
* AI configuration changes.

Routine worker heartbeats do not require audit events.

---

# 93. Failure Classification

Pipeline failures should be classified as:

* Validation Failure;
* Authorization Failure;
* Entitlement Failure;
* Dependency Failure;
* Data Quality Failure;
* Model Failure;
* Feature Failure;
* Provider Failure;
* Infrastructure Failure;
* Timeout;
* Resource Exhaustion;
* Permanent Logic Failure;
* Cancellation.

---

# 94. Failure Propagation

Failure propagation must respect dependency semantics.

If an optional stage fails:

```text id="pl049"
Optional Analysis
     ↓
Failed
     ↓
Pipeline may continue
```

If a required stage fails:

```text id="pl050"
Required Feature
     ↓
Failed
     ↓
Inference Blocked
```

---

# 95. Retry Isolation

Retrying one failed stage should not automatically rerun every successful stage.

Checkpointed results should be reused where safe.

---

# 96. Dependency Failure

If a dependency is unavailable:

```text id="pl051"
Pipeline
   ↓
Dependency unavailable
   ↓
WAITING / RETRY_PENDING
```

The system should avoid immediately marking the whole pipeline permanently failed for temporary dependency outages.

---

# 97. Circuit Breaker

External dependencies may use circuit breakers.

States:

```text id="pl052"
CLOSED
  ↓
OPEN
  ↓
HALF_OPEN
  ↓
CLOSED
```

Circuit breakers prevent repeated expensive failures.

---

# 98. Recovery Ordering

Recovery priority:

```text id="pl053"
Core ERP
    ↓
Interactive AI
    ↓
Standard AI
    ↓
Background AI
    ↓
Backfill
```

AI recovery must never compete equally with critical ERP recovery.

---

# 99. Feature Pipeline Integration

Feature pipelines integrate with:

`16_AI_Feature_and_Caching_Architecture.md`

Example:

```text id="pl054"
ERP Event
   ↓
Feature Job
   ↓
Feature Computation
   ↓
Validation
   ↓
Persistent Feature Storage
   ↓
Cache Refresh
```

---

# 100. Inference Pipeline Integration

Inference pipelines integrate with:

`15_AI_Inference_and_Runtime_Architecture.md`

Example:

```text id="pl055"
AI Job
   ↓
Feature Resolution
   ↓
Model Resolution
   ↓
Inference Runtime
   ↓
Output Validation
   ↓
Prediction Storage
```

---

# 101. Training Pipeline Integration

Training pipelines integrate with:

* `13_AI_Model_Training_and_Experimentation.md`
* `14_AI_Model_Registry_and_Versioning.md`

Training must produce versioned artifacts and evaluation results.

A successful training job must not automatically deploy a model to production.

---

# 102. Model Deployment Boundary

Pipeline processing may prepare a model for deployment.

Production deployment still requires:

* validation;
* approval;
* registry state;
* compatibility checks.

The pipeline must not bypass the Model Registry.

---

# 103. Feature Version Boundary

Feature pipelines may create new feature versions.

Production activation must follow:

```text id="pl056"
Feature Computation
   ↓
Validation
   ↓
Approval
   ↓
Activation
```

---

# 104. Configuration Dependency

AI pipelines may depend on:

* menu configuration;
* Branch configuration;
* Product configuration;
* Recipe version;
* price version;
* business settings.

The pipeline must identify relevant configuration versions when they affect semantics.

---

# 105. Historical Configuration

Historical pipelines must use appropriate historical configuration.

Current configuration must not silently reinterpret historical data.

---

# 106. Pipeline Input Consistency

When a pipeline uses multiple source datasets, it should identify their effective timestamps or versions.

Example:

```text id="pl057"
Orders @ T1
Inventory @ T1
Prices @ T1
```

is preferable to mixing incompatible states.

---

# 107. Pipeline Snapshot

For reproducible workloads, the pipeline may create an execution snapshot containing:

* source period;
* feature versions;
* model versions;
* configuration versions;
* pipeline version.

---

# 108. Pipeline Result Immutability

Important historical pipeline results should not be silently overwritten.

New processing creates:

* new execution;
* new result version;
* new lineage.

---

# 109. Result Publication

Pipeline results may be published to:

* feature storage;
* prediction storage;
* reports;
* dashboards;
* notification system;
* recommendation storage.

Publication must use defined contracts.

---

# 110. Notification Integration

AI completion or failure notifications should be asynchronous.

Example:

```text id="pl058"
AI Job Failed
    ↓
Outbox/Event
    ↓
Notification Worker
```

Notification failure must not invalidate the AI result.

---

# 111. Report Integration

AI-generated report enrichment must not modify authoritative report data without explicit architecture support.

Reports must distinguish:

```text
ERP Actual
AI Derived
AI Forecast
AI Recommendation
```

---

# 112. Dashboard Integration

Dashboard AI insights should be treated as derived content.

If AI data is unavailable:

```text id="pl059"
Dashboard
   ↓
AI unavailable
   ↓
Show normal ERP data
```

The dashboard must remain operational.

---

# 113. Offline Interaction

Offline ERP operation must not depend on background AI processing.

Queued AI jobs may continue on the server while a Branch device is offline.

After synchronization, the latest permitted AI results may become available.

---

# 114. Sync Integration

AI jobs triggered by synchronization must use the finalized server-side transaction state.

Example:

```text id="pl060"
Offline Order
    ↓
Synchronization
    ↓
Server Validation
    ↓
ERP Commit
    ↓
AI Event
    ↓
AI Job
```

AI processing must not run against unvalidated offline events.

---

# 115. Security

AI workers must use least-privilege access.

Workers should receive only the permissions required for their job type.

A worker must not have unrestricted:

* SQL access;
* filesystem access;
* network access;
* external provider access.

---

# 116. Tool Access

LLM pipeline stages must use approved tools only.

The worker must not allow an LLM to dynamically create unrestricted backend operations.

Tool authorization remains outside the LLM.

---

# 117. Secret Management

Secrets must not be stored in:

* job payloads;
* feature values;
* pipeline definitions;
* prompts;
* logs.

Secrets must come from the approved secret/configuration mechanism.

---

# 118. Payload Size

Job payloads should not contain large raw datasets when a reference is sufficient.

Prefer:

```text id="pl061"
Job
 ↓
Dataset Reference
```

instead of:

```text
Job
 ↓
Entire Dataset Payload
```

This reduces queue pressure and duplication.

---

# 119. Data References

Large inputs should reference:

* dataset ID;
* feature snapshot ID;
* file/object ID;
* report ID;
* query scope.

The worker retrieves the data using authorized access.

---

# 120. Job Payload Immutability

Once a job begins execution, its input contract should be immutable.

Changing inputs should create a new job or execution.

---

# 121. Job Result Versioning

If the same logical analysis is rerun:

```text id="pl062"
Execution 1
Execution 2
Execution 3
```

each execution remains identifiable.

The latest result may be selected for operational use, but historical executions remain traceable where required.

---

# 122. Pipeline Cache

Pipeline-level intermediate results may be cached when safe.

Cache keys must include:

* Business;
* Branch where applicable;
* pipeline version;
* stage version;
* input identity;
* relevant feature/model versions.

---

# 123. Intermediate Result Retention

Intermediate results should have shorter retention than important final outputs unless required for reproducibility.

Retention must follow data lifecycle rules.

---

# 124. Large Result Handling

Large AI outputs should be stored outside queue messages.

Use:

```text id="pl063"
Object/File Storage
        ↓
Result Reference
```

instead of embedding large payloads into job records.

---

# 125. Job Ordering

Some jobs require ordering by entity.

Example:

```text id="pl064"
Product A
Job 1
Job 2
Job 3
```

If Job 2 depends on Job 1, the system must enforce the dependency.

Global ordering should not be assumed.

---

# 126. Entity-Level Serialization

Where required, jobs for the same entity may be serialized.

Example:

```text id="pl065"
Business + Branch + Product
        ↓
One active feature update
```

This reduces conflicting writes.

---

# 127. Concurrency Conflict

If two jobs produce competing feature versions:

* version identity must determine validity;
* stale result must be rejected;
* newer result must remain authoritative for the derived feature state.

---

# 128. Worker Deployment

Workers may be deployed independently from API servers.

This allows:

* separate scaling;
* resource isolation;
* independent restart;
* workload-specific configuration.

---

# 129. Worker Health

Workers should expose:

* liveness;
* readiness;
* queue connectivity;
* dependency health;
* current workload;
* heartbeat.

Unhealthy workers should stop receiving new jobs.

---

# 130. Graceful Shutdown

During deployment or restart:

1. stop accepting new jobs;
2. finish safe current work;
3. checkpoint where required;
4. acknowledge completed jobs;
5. release leases;
6. shut down.

Long-running work should be requeued safely if it cannot finish.

---

# 131. Deployment Compatibility

Pipeline workers must support compatibility with:

* current job schema;
* pipeline versions;
* feature versions;
* model runtime versions.

Schema changes should use backward-compatible migration where possible.

---

# 132. Queue Schema Evolution

Job payload changes must be versioned.

Workers should identify payload version.

Old queued jobs must either:

* remain executable;
* be migrated safely;
* be rejected explicitly.

They must not fail because of silent schema assumptions.

---

# 133. Resource Protection During Deployment

Deployment must not restart every worker simultaneously if doing so would cause:

* queue loss;
* long execution interruption;
* excessive retries.

Rolling deployment is preferred.

---

# 134. Pipeline Testing

Pipeline testing should include:

* unit tests for stages;
* dependency tests;
* integration tests;
* retry tests;
* duplicate delivery tests;
* cancellation tests;
* checkpoint recovery tests;
* partial failure tests;
* backfill tests;
* resource limit tests;
* Business isolation tests;
* authorization tests.

---

# 135. Failure Injection

The system should test failures such as:

* worker crash;
* queue unavailable;
* database timeout;
* Redis unavailable;
* model runtime failure;
* external provider timeout;
* partial batch failure;
* stale feature;
* invalid model version.

---

# 136. Deterministic Testing

Important pipeline tests should use fixed:

* input datasets;
* feature versions;
* model versions;
* pipeline versions;
* configuration versions.

This improves reproducibility.

---

# 137. Test/Production Isolation

Test AI jobs must never access production Business data without explicit controlled mechanisms.

Test queues and production queues must be isolated.

---

# 138. Performance Targets

The AI background processing layer should target:

* job enqueue p95 ≤ 100 ms;
* queue admission decision p95 ≤ 100 ms;
* standard job pickup p95 ≤ 5 seconds;
* high-priority job pickup p95 ≤ 2 seconds under normal load;
* pipeline state update p95 ≤ 200 ms;
* checkpoint persistence p95 ≤ 500 ms;
* standard retry scheduling p95 ≤ 1 second;
* job status API p95 ≤ 200 ms;
* worker health check p95 ≤ 1 second;
* DLQ transition p95 ≤ 2 seconds after final failed attempt;
* standard background worker availability ≥ 99.5%;
* AI job execution success rate ≥ 99% excluding permanent input/business-rule failures.

These are architectural targets and should be validated against production workload.

---

# 139. Backpressure SLO

When AI workload exceeds configured capacity:

* interactive AI workloads should remain responsive where capacity exists;
* background workloads may be delayed;
* backfill workloads may be paused;
* core ERP workloads must remain unaffected.

AI queue saturation must not become an ERP outage.

---

# 140. Recovery SLO

After a worker failure:

* recoverable jobs should normally become eligible for reassignment within 30 seconds;
* stale worker leases should normally be detected within 30 seconds;
* checkpointed jobs should resume without repeating completed partitions where possible.

---

# 141. Data Integrity

AI pipeline processing must preserve:

* Business isolation;
* Branch isolation;
* feature lineage;
* model lineage;
* pipeline lineage;
* result versioning;
* idempotency.

---

# 142. Operational Controls

Authorized operators should be able to:

* inspect queues;
* inspect jobs;
* inspect pipeline executions;
* pause queues;
* resume queues;
* retry failed jobs;
* inspect DLQ;
* cancel jobs;
* trigger backfill;
* inspect resource usage;
* inspect failure patterns.

All sensitive administrative actions should be audited.

---

# 143. Emergency Stop

The system should support disabling selected AI workloads.

For example:

```text id="pl066"
AI Backfill
    ↓
DISABLED
```

while:

```text
ERP
    ↓
CONTINUES
```

Emergency stop must not disable core ERP operations.

---

# 144. AI Pipeline Availability

If AI infrastructure is unavailable:

```text id="pl067"
AI Pipeline DOWN
       ↓
ERP remains operational
```

Expected degradation:

* AI forecasts unavailable;
* recommendations delayed;
* AI reports delayed;
* anomaly analysis delayed.

Core ERP functionality must continue.

---

# 145. System Invariants

The following invariants apply to AI Pipeline and Background Processing:

1. AI processing is asynchronous unless explicitly defined otherwise.
2. AI background jobs must not block core ERP transactions.
3. ERP transactions remain authoritative.
4. AI jobs are derived processing units.
5. Every production job has a stable Job UUID.
6. Every retryable job has an idempotency strategy.
7. Duplicate job delivery is expected.
8. Duplicate delivery must not create conflicting duplicate results.
9. Job state is persisted outside worker memory.
10. Long-running jobs use checkpoints where practical.
11. Worker crashes must not permanently lose recoverable jobs.
12. Jobs must have explicit lifecycle states.
13. Jobs cannot remain RUNNING indefinitely without heartbeat or lease.
14. Every job type has an explicit contract.
15. Unknown job types cannot execute.
16. Production pipelines are versioned.
17. Pipeline versions are immutable after activation.
18. Production execution uses approved pipeline versions.
19. Pipeline dependency graphs must be acyclic.
20. Circular pipeline dependencies are prohibited.
21. Pipeline stage dependencies are explicit.
22. Required dependencies must complete before dependent stages.
23. Optional dependency failures may be handled according to stage policy.
24. Pipeline stages have explicit input and output contracts.
25. Pipeline stages have bounded execution time.
26. Pipeline stages have explicit retry policies.
27. Permanent failures do not retry indefinitely.
28. Repeated failures enter a recoverable failure state.
29. Dead-lettered jobs remain inspectable.
30. DLQ recovery is controlled and auditable.
31. Retry does not automatically rerun successful stages when checkpointing allows reuse.
32. AI pipeline transactions are bounded.
33. One giant transaction across a pipeline is prohibited.
34. ERP transaction commit does not depend on AI completion.
35. Outbox is preferred for ERP-triggered AI events.
36. Duplicate events are tolerated.
37. Event ordering is not assumed globally.
38. Event ordering is enforced only where business semantics require it.
39. Eventual consistency is acceptable for ordinary AI processing.
40. Feature freshness requirements remain explicit.
41. Model compatibility is validated before execution.
42. Feature compatibility is validated before execution.
43. Pipeline compatibility is validated before execution.
44. Business lifecycle is revalidated before job execution.
45. Subscription entitlement is revalidated before execution where required.
46. Authorization is revalidated before delayed execution.
47. Deleted Businesses cannot execute new AI jobs.
48. Stale jobs cannot recreate deleted Business data.
49. Inactive Branch jobs require explicit policy.
50. Business isolation applies to every AI job.
51. Branch isolation applies to Branch-scoped jobs.
52. One Business cannot monopolize worker capacity.
53. One Branch cannot monopolize Branch-scoped worker capacity.
54. AI concurrency is bounded.
55. AI resources are quota-controlled.
56. AI workloads cannot consume unrestricted database connections.
57. Core ERP database capacity has higher priority than AI processing.
58. Core ERP workers have higher infrastructure priority than AI workers.
59. Backfill is lower priority than interactive AI.
60. Backfill is resource-limited.
61. Large workloads use bounded batches.
62. Batch processing supports partial success where semantics allow it.
63. Failed partitions can be retried independently where safe.
64. Job payloads should reference large datasets instead of embedding them.
65. Job payloads are versioned.
66. Input contracts remain immutable after execution begins.
67. Important pipeline outputs are versioned.
68. Historical executions remain traceable where required.
69. Reprocessing does not silently overwrite original lineage.
70. Replay identifies pipeline/model/feature versions.
71. Backfill identifies historical scope.
72. Backfill is resumable where practical.
73. Cancellation cannot falsely report success.
74. Cancelled jobs remain distinguishable from failed jobs.
75. Paused jobs preserve resumable state where supported.
76. Resuming a job revalidates current authorization and entitlement.
77. Pipeline checkpoints identify completed work.
78. Checkpoints are persisted durably enough for recovery.
79. Worker leases prevent permanent zombie jobs.
80. Worker heartbeat detects stale execution.
81. Worker shutdown is graceful where practical.
82. Worker restart must not corrupt job state.
83. Pipeline state is externally persisted.
84. Pipeline output passes schema validation.
85. Pipeline output passes required business validation.
86. Invalid AI output cannot be published as valid state.
87. AI recommendations do not directly mutate ERP authoritative data.
88. AI-generated purchase suggestions do not automatically create purchases.
89. AI-generated price recommendations do not automatically change prices.
90. AI-generated inventory recommendations do not directly modify inventory.
91. LLM jobs follow the AI prompt and guardrail architecture.
92. LLM authorization is enforced outside the LLM.
93. External AI provider failure cannot block core ERP operations.
94. External provider retries are bounded.
95. External provider rate limits are respected.
96. Token usage is bounded.
97. Job resource usage is bounded.
98. Queue backpressure protects system stability.
99. Priority inversion is prevented where possible.
100. Low-priority AI workloads can be throttled.
101. AI worker pools may be isolated by workload type.
102. GPU workloads are optional and controlled.
103. CPU-first execution is preferred where practical.
104. Worker autoscaling has upper limits.
105. Queue saturation does not cause ERP outage.
106. Pipeline observability includes queue and execution metrics.
107. Sensitive payloads are not logged by default.
108. High-cardinality Business identifiers are not blindly used as metric labels.
109. Administrative AI operations are audited.
110. Routine worker heartbeats do not require audit events.
111. AI infrastructure failures are observable.
112. Feature failures are distinguishable from model failures.
113. Model failures are distinguishable from infrastructure failures.
114. Authorization failures are distinguishable from temporary failures.
115. Permanent failures are not endlessly retried.
116. Recovery order prioritizes core ERP over AI.
117. Recovery order prioritizes interactive AI over backfill.
118. Emergency stop can disable selected AI workloads.
119. Emergency stop does not disable core ERP.
120. AI dashboard enrichment is optional.
121. AI report enrichment is optional.
122. AI insight generation is optional.
123. Offline ERP operation does not depend on AI jobs.
124. Offline transactions are validated server-side before AI processing.
125. Synchronization events can trigger AI jobs only after authoritative server processing.
126. AI jobs cannot bypass synchronization validation.
127. Feature jobs follow Feature and Caching architecture.
128. Inference jobs follow Inference Runtime architecture.
129. Training jobs follow Training and Experimentation architecture.
130. Model activation follows Model Registry architecture.
131. Pipeline activation requires validation.
132. Pipeline lifecycle is auditable.
133. Job lifecycle is observable.
134. Job retry behavior is deterministic within configured policy.
135. Scheduled jobs are deduplicated.
136. Scheduler restart does not create uncontrolled duplicate executions.
137. Misfire behavior is explicit.
138. Overlapping schedule behavior is explicit.
139. Pipeline parallelism is bounded.
140. Pipeline barriers enforce required dependencies.
141. Conditional pipeline stages are versioned.
142. Pipeline input snapshots are used where reproducibility requires them.
143. Pipeline output lineage remains reconstructable.
144. AI processing remains independently scalable.
145. AI processing remains independently recoverable.
146. AI processing remains independently deployable where practical.
147. AI worker deployment does not require ERP downtime.
148. Queue schema evolution is controlled.
149. Worker compatibility with queued jobs is maintained.
150. AI background processing is an intelligence layer, not an ERP transaction layer.

---

# 146. Related Documents

### AI Architecture

* `docs/04_Architecture/07_AI/01_AI_Architecture_Overview.md`
* `docs/04_Architecture/07_AI/02_AI_Use_Cases_and_Capabilities.md`
* `docs/04_Architecture/07_AI/03_AI_Boundaries_and_Non_AI_Decisions.md`
* `docs/04_Architecture/07_AI/04_AI_Data_Architecture.md`
* `docs/04_Architecture/07_AI/05_AI_Data_Preparation_and_Feature_Engineering.md`
* `docs/04_Architecture/07_AI/06_AI_Model_Architecture_and_Model_Strategy.md`
* `docs/04_Architecture/07_AI/07_AI_Forecasting_and_Demand_Prediction.md`
* `docs/04_Architecture/07_AI/08_AI_Inventory_and_Purchasing_Intelligence.md`
* `docs/04_Architecture/07_AI/09_AI_Anomaly_Detection_and_Business_Risk.md`
* `docs/04_Architecture/07_AI/10_AI_Business_Insights_and_Recommendations.md`
* `docs/04_Architecture/07_AI/11_AI_LLM_and_Natural_Language_Architecture.md`
* `docs/04_Architecture/07_AI/12_AI_Prompt_Context_and_Guardrails.md`
* `docs/04_Architecture/07_AI/13_AI_Model_Training_and_Experimentation.md`
* `docs/04_Architecture/07_AI/14_AI_Model_Registry_and_Versioning.md`
* `docs/04_Architecture/07_AI/15_AI_Inference_and_Runtime_Architecture.md`
* `docs/04_Architecture/07_AI/16_AI_Feature_and_Caching_Architecture.md`

### Backend

* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/23_Configuration_Data_Model.md`
* `docs/04_Architecture/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/04_Architecture/05_Database/28_Database_Backup_and_Recovery.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### Business and System Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 147. Status

**AI Architecture Interview:** Completed through the current AI architecture sequence.

**Document Status:** Proposed.

**Current Document:** `17_AI_Pipeline_and_Background_Processing.md`

**Previous Document:** `16_AI_Feature_and_Caching_Architecture.md`

**Next Document:** The next document in the frozen AI architecture sequence.

