# AI Model Training and Experimentation

**Document ID:** AI-13
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/08_AI/README.md`

---

## 1. Purpose

This document defines the architecture and system behavior for AI model training, experimentation, evaluation, reproducibility and model promotion within FastFood ERP.

The purpose is to ensure that AI models are trained through controlled, reproducible and auditable processes rather than ad-hoc experimentation.

The system must be able to identify:

* which dataset was used;
* which feature version was used;
* which model architecture was used;
* which hyperparameters were used;
* which code/configuration version produced the model;
* which evaluation results were obtained;
* who or what initiated the experiment;
* whether the resulting model was approved;
* which model version is currently deployed.

---

# 2. Scope

This document covers:

* training datasets;
* dataset snapshots;
* feature versions;
* training pipelines;
* experiment runs;
* experiment metadata;
* model training;
* hyperparameters;
* random seeds;
* reproducibility;
* evaluation;
* validation;
* baseline comparison;
* model comparison;
* experiment artifacts;
* model candidates;
* model promotion;
* model registry integration;
* rollback;
* retraining;
* scheduled training;
* manual training;
* Business-specific training;
* shared model training;
* cold-start training;
* resource management;
* CPU/GPU strategy;
* training isolation;
* data privacy;
* Business isolation;
* auditability;
* failure handling;
* security;
* observability.

---

# 3. Core Principle

The primary principle is:

> **No AI model becomes production-ready merely because training succeeded.**

Training success, evaluation success and production approval are separate states.

```text
Dataset
   ↓
Feature Version
   ↓
Training Configuration
   ↓
Experiment
   ↓
Training Run
   ↓
Evaluation
   ↓
Validation
   ↓
Approval
   ↓
Model Registry
   ↓
Deployment
```

---

# 4. Training vs Inference

Training and inference are separate workloads.

### Training

Training:

* consumes historical data;
* generates model artifacts;
* may require significant CPU/GPU resources;
* may take minutes or hours;
* is normally asynchronous.

### Inference

Inference:

* consumes an approved model;
* produces predictions/recommendations/anomaly scores;
* must satisfy operational latency requirements;
* must not modify model parameters.

A production inference process must never train a model implicitly.

---

# 5. Production Model Immutability

A deployed model version is immutable.

The system must not modify the model artifact in place.

If a new model is required:

```text
Model v1
   ↓
Training
   ↓
Model v2 Candidate
   ↓
Evaluation
   ↓
Approval
   ↓
Model v2
```

A new model version must be created.

---

# 6. Experiment

An Experiment represents a controlled attempt to train or evaluate a model under a specific configuration.

An Experiment should identify:

* Experiment UUID;
* Business scope where applicable;
* model type;
* objective;
* dataset version;
* feature version;
* code version;
* configuration version;
* training parameters;
* created timestamp;
* creator/system source;
* status;
* result;
* related model candidate.

---

# 7. Experiment Status

Experiment lifecycle:

```text
CREATED
   ↓
QUEUED
   ↓
RUNNING
   ↓
EVALUATING
   ↓
COMPLETED
```

Failure path:

```text
RUNNING
   ↓
FAILED
```

Cancellation path:

```text
QUEUED / RUNNING
   ↓
CANCELLED
```

An experiment must not be considered successful merely because the training process exited without an infrastructure error.

---

# 8. Training Run

An Experiment may contain one or more Training Runs.

A Training Run represents one concrete execution of training.

Example:

```text
Experiment: Demand Forecasting v5

Run 1 → learning_rate=0.01
Run 2 → learning_rate=0.005
Run 3 → learning_rate=0.001
```

Each run must remain independently identifiable.

---

# 9. Training Run Identity

Every Training Run must have a unique UUID.

The identity must not depend only on:

* model name;
* timestamp;
* filename;
* process ID.

The UUID is the authoritative identifier for the training execution.

---

# 10. Dataset Snapshot

Training must use a reproducible dataset snapshot.

The system must not rely on a mutable query such as:

```text
SELECT * FROM orders WHERE ...
```

without recording the resulting dataset state.

The dataset version must identify the data state used for training.

---

# 11. Dataset Version

A Dataset Version should contain:

* Dataset UUID;
* version;
* source tables/data sources;
* time range;
* Business scope;
* Branch scope;
* filtering rules;
* excluded data;
* data preparation version;
* creation timestamp;
* row/sample count;
* checksum or content fingerprint.

---

# 12. Historical Data Integrity

Training must use historical transaction state as it existed according to authoritative ERP records.

AI training must not silently reconstruct historical data using current:

* prices;
* menu configuration;
* recipes;
* Branch configuration;
* employee permissions;
* subscription state.

Where historical configuration is relevant, the corresponding historical version must be used.

---

# 13. Data Leakage Prevention

Training pipelines must prevent future information from entering historical training features.

Examples of leakage include:

* future sales values;
* future stock movements;
* future price changes;
* future refunds;
* future inventory corrections;
* future report results.

The training pipeline must explicitly define the prediction cutoff time.

---

# 14. Prediction Cutoff

Every time-dependent training dataset must define:

```text
Prediction Cutoff
```

Data after the cutoff must not be used as model input for that prediction.

Target values may exist after the cutoff only when they are intentionally defined as the supervised learning target.

---

# 15. Train / Validation / Test Separation

Where applicable, datasets must be separated into:

* training set;
* validation set;
* test set.

For time-series problems, chronological separation is preferred.

Example:

```text
Historical Data

|------ Training ------|--- Validation ---|--- Test ---|
```

Random shuffling must not be used when it would cause temporal leakage.

---

# 16. Time-Series Evaluation

Forecasting models must preserve temporal ordering.

For example:

```text
2025 Q1 → Training
2025 Q2 → Validation
2025 Q3 → Test
```

The exact period depends on available data and prediction horizon.

---

# 17. Cross-Validation

Cross-validation may be used when appropriate.

For time-series models, time-aware validation must be used instead of ordinary random K-fold validation when random splitting would invalidate the evaluation.

The chosen validation strategy must be recorded.

---

# 18. Feature Version

A Training Run must identify the exact Feature Engineering version used.

Feature version includes:

* feature definitions;
* transformations;
* normalization;
* aggregation rules;
* missing-value handling;
* encoding;
* feature selection;
* time windows;
* feature dependencies.

Changing feature logic requires a new Feature Version.

---

# 19. Training Configuration

Training configuration must be versioned.

It may include:

* model architecture;
* learning rate;
* batch size;
* number of epochs;
* regularization;
* optimizer;
* loss function;
* early stopping;
* random seed;
* training window;
* feature configuration;
* target definition.

---

# 20. Hyperparameters

Hyperparameters must be recorded for every Training Run.

The system must never depend on undocumented runtime defaults for reproducibility.

Examples:

```text
learning_rate
batch_size
epochs
max_depth
n_estimators
regularization
dropout
window_size
```

---

# 21. Random Seed

Where randomness exists, the Training Run should record:

* random seed;
* framework seed;
* data sampling seed;
* relevant deterministic configuration.

If complete deterministic execution is impossible because of hardware/framework behavior, the system must document that limitation.

---

# 22. Code Version

Training must identify the code version used.

At minimum:

* repository revision;
* commit SHA or equivalent immutable version;
* training pipeline version.

A model artifact without identifiable training code provenance must not be promoted to production.

---

# 23. Environment Version

The training environment should identify:

* Python version;
* framework version;
* library versions;
* operating environment;
* CPU/GPU information where relevant;
* container/image version where applicable.

This information supports reproducibility and debugging.

---

# 24. Dependency Locking

Training dependencies should be pinned or otherwise reproducibly resolved.

A model must not depend on an uncontrolled floating dependency such as:

```text
package >= current_version
```

for critical production training.

---

# 25. Experiment Metadata

Experiment metadata must be stored separately from large model artifacts.

Metadata may include:

* parameters;
* metrics;
* status;
* timestamps;
* dataset reference;
* feature reference;
* code reference;
* model reference;
* resource usage;
* error information.

---

# 26. Experiment Artifact

A Training Run may generate:

* trained model;
* checkpoints;
* evaluation report;
* feature importance;
* confusion matrix;
* forecast metrics;
* plots;
* logs;
* configuration;
* model card draft.

Large artifacts must not be stored directly in transactional PostgreSQL tables.

---

# 27. Artifact Storage

Large model artifacts should be stored in dedicated object/file storage.

PostgreSQL stores:

* artifact identity;
* metadata;
* checksum;
* storage reference;
* version;
* lifecycle state.

The database remains authoritative for artifact metadata.

---

# 28. Artifact Integrity

Every production-bound model artifact must have an integrity mechanism such as a cryptographic checksum.

Example:

```text
Model Artifact
     ↓
SHA-256
     ↓
Artifact Fingerprint
```

A checksum mismatch must prevent model promotion or deployment.

---

# 29. Model Candidate

A successful Training Run may create a Model Candidate.

A Model Candidate is not automatically a production model.

Lifecycle:

```text
Training Run
   ↓
Model Candidate
   ↓
Evaluation
   ↓
Validation
   ↓
Approval
   ↓
Production Model
```

---

# 30. Baseline Model

Every important model problem should have a baseline where practical.

Examples:

* moving average;
* seasonal naive forecast;
* simple linear model;
* existing production model;
* deterministic business baseline.

A complex model should not be promoted without demonstrating meaningful value over an appropriate baseline.

---

# 31. Baseline Comparison

Evaluation should compare:

```text
Baseline
vs
Candidate Model
```

The comparison should include both technical and business metrics.

Example:

```text
Baseline WAPE: 21%
Candidate WAPE: 16%
```

A lower technical metric alone does not guarantee business usefulness.

---

# 32. Business Metric Evaluation

Model evaluation may include:

* stockout reduction;
* excess inventory reduction;
* forecast usefulness;
* recommendation acceptance;
* anomaly review usefulness;
* false alert reduction;
* operational time saved.

Business metrics must not be fabricated when actual measurements are unavailable.

---

# 33. Model Evaluation

Evaluation must consider:

* accuracy;
* stability;
* generalization;
* data coverage;
* failure cases;
* bias;
* confidence;
* operational cost;
* latency;
* resource consumption.

---

# 34. Model-Specific Metrics

Different model categories require different metrics.

### Forecasting

Possible metrics:

* MAE;
* RMSE;
* WAPE;
* MASE;
* bias;
* service-level impact.

### Classification

Possible metrics:

* precision;
* recall;
* F1;
* ROC-AUC;
* PR-AUC.

### Anomaly Detection

Possible metrics:

* precision at review threshold;
* false-positive rate;
* detection latency;
* confirmed anomaly rate.

### Recommendation

Possible metrics:

* precision@K;
* recall@K;
* acceptance rate;
* business impact.

The selected metrics must be documented per model type.

---

# 35. Evaluation Dataset Independence

The final test dataset must not be repeatedly used to tune the model.

Repeated test-set optimization can turn the test dataset into an implicit training dataset.

When this occurs, a new evaluation dataset should be established.

---

# 36. Experiment Comparison

Experiments should be comparable only when:

* the target is equivalent;
* evaluation methodology is equivalent;
* relevant dataset scope is known;
* metrics are comparable;
* configuration differences are identifiable.

The system must not compare incompatible metrics as though they were equivalent.

---

# 37. Experiment Reproducibility

A Training Run should be reproducible from recorded references:

```text
Dataset Version
+
Feature Version
+
Code Version
+
Training Configuration
+
Environment Version
+
Random Seed
```

The objective is to make the training result independently reconstructable.

---

# 38. Reproducibility Levels

The system may classify reproducibility as:

```text
FULL
PARTIAL
NOT_REPRODUCIBLE
```

`FULL` means the recorded information is sufficient to reproduce the training process within the supported deterministic boundaries.

---

# 39. Training Pipeline

Training should be executed through controlled pipeline stages:

```text
Data Selection
      ↓
Data Validation
      ↓
Feature Generation
      ↓
Dataset Split
      ↓
Training
      ↓
Evaluation
      ↓
Validation
      ↓
Candidate Creation
```

A failed stage must stop downstream promotion.

---

# 40. Data Validation Before Training

Training must validate:

* required fields;
* data types;
* missing values;
* duplicate records;
* invalid timestamps;
* impossible quantities;
* negative values where prohibited;
* Business scope;
* Branch scope;
* target availability.

Invalid data must not silently enter training.

---

# 41. Data Quality Threshold

Each training pipeline should define minimum data-quality thresholds.

Examples:

```text
Maximum missing-value ratio
Maximum duplicate ratio
Minimum historical coverage
Minimum target availability
Minimum Branch coverage
```

If thresholds are violated, the Training Run may enter:

```text
INSUFFICIENT_DATA
```

rather than producing a misleading model.

---

# 42. Cold Start

New Businesses, Branches and Products may not have enough historical data.

The system must support:

* shared/global model;
* generic baseline;
* category-level baseline;
* Business-level model when enough data exists;
* Branch-specific model when enough data exists.

The system must not force a Business-specific model when insufficient data exists.

---

# 43. Hierarchical Training Strategy

A model may use:

```text
Global / Shared Model
        ↓
Business Adaptation
        ↓
Branch Adaptation
```

The exact strategy depends on model type and data availability.

Raw Business data must not be mixed across unrelated Businesses without an explicit architecture and privacy decision.

---

# 44. Business Isolation

Training data must respect Business isolation.

A Business-specific Training Run must never include another Business's private transactional data.

Cross-Business aggregate training requires explicit approved architecture and must avoid exposing raw private data.

---

# 45. Branch Scope

A Training Run may be:

* Business-wide;
* Branch-specific;
* selected-Branch;
* global/shared.

The scope must be explicitly stored.

---

# 46. Employee Data

Employee-related training must minimize personal information.

Where employee identity is not necessary, anonymized or aggregated features should be preferred.

AI training must not create unsupported behavioral or integrity accusations.

---

# 47. Customer Data

Customer phone numbers and addresses are not default AI training features.

If customer-related data is ever required:

* necessity must be established;
* data must be minimized;
* authorization must be enforced;
* retention must be controlled.

---

# 48. Training on Historical Prices

Price-sensitive models must use the historical price applicable to the transaction period.

Current price must not be substituted into historical training data unless explicitly required by the model definition.

---

# 49. Training on Historical Inventory

Inventory models must account for historical stock availability where relevant.

Observed low sales may be caused by:

* low demand;
* stockout;
* menu inactivity;
* equipment failure;
* operational restriction.

The training pipeline should distinguish these conditions where possible.

---

# 50. Stockout-Aware Training

Demand forecasting should avoid treating stockout periods as normal zero-demand observations.

Where possible:

```text
Observed Sales
+
Stock Availability
+
Menu Availability
+
Operational Constraints
```

should be considered together.

---

# 51. Training on Historical Menu Configuration

Menu state may affect demand.

Training datasets may include:

* Product active state;
* Branch availability;
* price;
* category;
* Set configuration;
* equipment availability where relevant.

Historical configuration must be reconstructed correctly.

---

# 52. Training Trigger

Training may be triggered by:

* schedule;
* manual authorized action;
* data-volume threshold;
* model drift;
* performance degradation;
* new feature version;
* new model version;
* explicit retraining policy.

Training must not start merely because a user opened an AI screen.

---

# 53. Scheduled Training

Scheduled training should be asynchronous.

The scheduler must create a Training Job rather than executing long-running training inside a user-facing request.

---

# 54. Manual Training

Authorized users or system operators may request training.

Manual training requests must validate:

* authorization;
* Business scope;
* model type;
* subscription entitlement;
* resource availability;
* training policy.

---

# 55. Duplicate Training Prevention

The system should prevent unnecessary duplicate Training Runs for the same:

```text
Dataset Version
+
Feature Version
+
Model Configuration
+
Code Version
```

unless the experiment explicitly requires repeated runs.

---

# 56. Idempotent Training Requests

Training request creation must support idempotency.

Retrying the same request must not unintentionally create duplicate production candidates.

Training Run identity remains unique.

---

# 57. Training Queue

Training should run through a controlled queue/worker architecture.

Example:

```text
Training Request
      ↓
AI Training Queue
      ↓
Training Worker
      ↓
Artifact Storage
      ↓
Evaluation Worker
```

Training must not execute in the main web/API worker.

---

# 58. Resource Management

Training workloads must have explicit resource limits.

Controls may include:

* CPU limit;
* memory limit;
* GPU allocation;
* execution timeout;
* concurrency limit;
* disk quota;
* artifact quota.

---

# 59. CPU-First Strategy

CPU-based training is preferred where the model can achieve acceptable performance.

GPU usage should be introduced only when:

* training time materially benefits;
* model architecture requires it;
* operational value justifies it.

The ERP should not require a GPU for ordinary AI operation.

---

# 60. Training Concurrency

Training concurrency must be limited.

The system must protect:

* ERP API;
* PostgreSQL;
* Redis;
* background workers;
* object storage;
* POS operations.

AI training must not starve core ERP resources.

---

# 61. Training Isolation

Training should run in an isolated worker/runtime environment.

The training process must not have unrestricted access to:

* production database write operations;
* authentication tables;
* permission management;
* financial mutation endpoints;
* audit history modification;
* subscription modification.

---

# 62. Read-Only Training Data Access

Training pipelines should consume prepared datasets rather than directly modifying ERP data.

The training environment should have read-only access to source data where direct access is unavoidable.

---

# 63. No Production Mutation

Training must never:

* create orders;
* modify orders;
* create payments;
* modify payments;
* modify inventory;
* modify prices;
* modify payroll;
* modify permissions;
* modify subscriptions;
* modify audit history.

Training produces AI artifacts, not ERP transactions.

---

# 64. Experiment Artifact Naming

Artifact names should not be treated as authoritative identifiers.

Example:

```text
forecast_model_v7.pkl
```

is not sufficient identity.

The authoritative identity is:

```text
Model UUID
+
Model Version
+
Artifact Fingerprint
```

---

# 65. Artifact Format

Production model formats should be selected according to deployment requirements.

Possible formats include:

* serialized framework model;
* ONNX;
* safe tensor formats where applicable;
* other validated inference formats.

Unsafe arbitrary code execution formats should be avoided where practical.

---

# 66. Model Serialization Security

Loading a model artifact must not automatically execute untrusted arbitrary code.

Model artifacts must be:

* authenticated;
* integrity checked;
* validated;
* associated with trusted provenance.

---

# 67. Experiment Logs

Training logs should capture:

* run start;
* run end;
* stage;
* metrics;
* warnings;
* resource usage;
* failures;
* artifact creation;
* evaluation result.

Logs must avoid unnecessary sensitive business data.

---

# 68. Metrics Storage

Metrics should be stored in structured form.

Example:

```text
metric_name
metric_value
dataset_split
metric_version
timestamp
```

Free-form logs must not be the only source of model evaluation metrics.

---

# 69. Training Resource Metrics

The system should record:

* CPU time;
* memory peak;
* GPU time where applicable;
* training duration;
* dataset size;
* artifact size.

This supports cost and performance analysis.

---

# 70. Experiment Cost

Where infrastructure cost is measurable, Training Runs should record estimated resource cost.

Cost data should support:

* model comparison;
* training schedule optimization;
* resource budgeting.

Cost estimates must be clearly distinguished from actual billing data when applicable.

---

# 71. Evaluation Thresholds

Every production model type should define minimum evaluation criteria.

Example:

```text
Accuracy threshold
Latency threshold
Resource threshold
Business usefulness threshold
```

A model failing required criteria cannot be promoted automatically.

---

# 72. Approval

Training and evaluation do not automatically equal production approval.

Promotion requires:

* valid dataset;
* valid feature version;
* successful training;
* acceptable evaluation;
* required validation;
* security checks;
* artifact integrity;
* authorized approval where required.

---

# 73. Automated Approval

Low-risk model classes may use automated promotion if the model satisfies predefined deterministic criteria.

Automated approval rules must themselves be versioned and auditable.

---

# 74. Human Approval

Human approval should be required for model classes where incorrect behavior can materially affect business decisions.

Examples may include:

* high-impact financial anomaly models;
* employee-related risk models;
* models producing recommendations with significant operational impact.

AI must not approve itself.

---

# 75. Model Promotion

Promotion path:

```text
Candidate
   ↓
Validated
   ↓
Approved
   ↓
Registered
   ↓
Deployable
```

Deployment is a separate operational action.

---

# 76. Champion Model

For a model type, one model may be designated:

```text
CHAMPION
```

The Champion is the currently preferred approved model.

A Challenger may be evaluated against it.

---

# 77. Challenger Model

A Challenger is an approved candidate being evaluated against the Champion.

Possible strategies:

* offline comparison;
* shadow inference;
* limited rollout;
* canary;
* A/B evaluation where appropriate.

---

# 78. Shadow Evaluation

A Challenger may receive equivalent inference inputs without affecting authoritative ERP decisions.

The system records:

* prediction;
* latency;
* confidence;
* comparison;
* outcome when available.

Shadow results must not change user-visible authoritative ERP state.

---

# 79. Canary Deployment

A new model may be deployed to a limited scope first.

Example:

```text
Business A / Branch 1
        ↓
Canary
        ↓
Evaluation
        ↓
Broader Deployment
```

Canary scope must be explicitly defined.

---

# 80. Rollback

If a deployed model causes unacceptable behavior:

```text
Model v2
   ↓
Rollback
   ↓
Model v1
```

Rollback must restore the previous approved model reference without deleting Model v2 history.

---

# 81. Historical Prediction Integrity

Historical AI outputs must retain the model version that generated them.

The system must not reinterpret historical predictions using the current model.

---

# 82. Retraining

Retraining should create a new Training Run.

It must not overwrite:

* previous model;
* previous dataset version;
* previous metrics;
* previous experiment;
* previous prediction lineage.

---

# 83. Retraining Reasons

A retraining run may record a reason such as:

```text
SCHEDULED
DRIFT_DETECTED
PERFORMANCE_DEGRADATION
NEW_DATA
NEW_FEATURES
NEW_MODEL_VERSION
BUSINESS_REQUEST
INCIDENT_RECOVERY
```

---

# 84. Model Drift Trigger

Training may be triggered by detected model/data drift.

Drift detection itself must be monitored and versioned.

A drift signal does not automatically prove that a model is incorrect.

---

# 85. Experiment Rejection

An Experiment may be rejected because of:

* insufficient data;
* data leakage;
* poor evaluation;
* invalid feature version;
* security failure;
* artifact integrity failure;
* resource violation;
* business metric failure;
* reproducibility failure.

The rejection reason must be stored.

---

# 86. Failed Training

A failed Training Run must not create an active production model.

Failure information should include:

* stage;
* error classification;
* timestamp;
* retry count;
* resource state;
* relevant diagnostic reference.

---

# 87. Retry Policy

Retryable infrastructure failures may be retried.

Examples:

* worker interruption;
* temporary storage failure;
* temporary queue failure.

Non-retryable data/model errors should fail fast.

---

# 88. Retry Idempotency

A retry must not:

* duplicate production model versions;
* duplicate approval;
* overwrite artifacts;
* corrupt experiment state.

Each execution remains traceable.

---

# 89. Training Timeout

Training jobs must have maximum execution limits.

A job exceeding its allowed runtime must be terminated or moved to a controlled timeout state.

Timeouts must not leave the experiment falsely marked as successful.

---

# 90. Training Cancellation

Authorized operators may cancel a queued or running Training Run.

Cancellation must preserve experiment history.

A cancelled run must not be promoted.

---

# 91. Training Data Lifecycle

Training datasets must follow the same data lifecycle policies as the source data.

If Business data becomes:

```text
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

training jobs must respect the lifecycle state.

---

# 92. Deleted Business Data

When a Business is permanently deleted, AI datasets derived exclusively from that Business must be deleted or rendered non-identifiable according to the approved data lifecycle policy.

AI artifacts containing Business-specific information must also be evaluated for deletion.

---

# 93. Queued Job Revalidation

A queued Training Job must revalidate before execution:

* Business lifecycle;
* subscription entitlement where applicable;
* Business scope;
* data availability;
* authorization;
* model training policy.

A stale queued job must not bypass current restrictions.

---

# 94. Subscription Entitlement

AI training may depend on subscription entitlement.

When entitlement is removed:

* new training requests may be blocked;
* queued jobs must be revalidated;
* existing approved models may continue operating according to policy;
* historical AI results remain subject to lifecycle rules.

---

# 95. Offline Training

Offline POS devices must not independently train production AI models.

Offline devices may collect locally authorized operational data for synchronization.

Training occurs in the controlled server-side AI environment after data synchronization.

---

# 96. Synchronization and Training

Unsynchronized offline transactions must not be treated as globally complete training data.

After synchronization:

```text
Offline Transaction
      ↓
Server Validation
      ↓
Authoritative Data
      ↓
Dataset Generation
      ↓
Training
```

---

# 97. Configuration Changes and Training

Changes to:

* menu;
* prices;
* recipes;
* sets;
* Branch configuration

may affect training features.

The training dataset must identify the configuration state used.

---

# 98. Prompt/LLM Training Boundary

LLM prompt behavior must not be changed merely by modifying a production prompt during a model-training experiment.

Prompt versions and model versions are separate controlled artifacts.

The LLM architecture follows:

`12_AI_Prompt_Context_and_Guardrails.md`.

---

# 99. Experiment Security

Training infrastructure must protect:

* dataset access;
* model artifacts;
* experiment metadata;
* credentials;
* API keys;
* provider credentials.

Secrets must not be stored inside experiment parameters or model artifacts.

---

# 100. External Model Providers

If external AI providers are used for training:

* provider identity must be recorded;
* data transfer scope must be explicit;
* Business isolation must be preserved;
* privacy requirements must be satisfied;
* training usage must be auditable;
* provider retention behavior must be understood.

---

# 101. External Training Data Restrictions

Private Business data must not be sent to an external provider merely because a model could theoretically benefit from it.

The data transfer must have an approved architecture and valid purpose.

---

# 102. Model Card

Production-bound models should have a Model Card containing:

* purpose;
* scope;
* model type;
* training data;
* feature version;
* evaluation metrics;
* limitations;
* known failure cases;
* intended use;
* prohibited use;
* model version;
* approval state.

---

# 103. Experiment Report

Each completed important Experiment should produce a structured report containing:

* objective;
* dataset;
* features;
* model;
* parameters;
* evaluation;
* baseline comparison;
* resource usage;
* limitations;
* recommendation;
* final decision.

---

# 104. Explainability Artifacts

Where applicable, Training Runs may produce:

* feature importance;
* error distribution;
* residual analysis;
* confusion matrix;
* calibration analysis;
* forecast error by segment;
* anomaly threshold analysis.

These artifacts support validation and explainability.

---

# 105. Experiment Lineage

The system must support lineage:

```text
Data Version
    ↓
Feature Version
    ↓
Experiment
    ↓
Training Run
    ↓
Model Candidate
    ↓
Evaluation
    ↓
Approval
    ↓
Model Version
    ↓
Deployment
    ↓
Prediction
```

Every production prediction should be traceable to its model version.

---

# 106. Model Version Lineage

A Model Version should identify:

* Model UUID;
* model version;
* Training Run;
* Experiment;
* Dataset Version;
* Feature Version;
* Code Version;
* Environment Version;
* Artifact;
* evaluation;
* approval;
* deployment status.

---

# 107. Experiment Audit

Important experiment operations must be auditable.

Audit events may include:

* experiment creation;
* training start;
* training completion;
* training failure;
* evaluation;
* approval;
* rejection;
* promotion;
* deployment;
* rollback;
* cancellation.

---

# 108. Actor Attribution

Where a human initiates or approves an experiment, the system must retain:

* Employee UUID;
* Business UUID;
* Branch UUID where relevant;
* Device UUID where relevant;
* timestamp.

System-generated runs must identify the system/job source.

---

# 109. Experiment Authorization

Only authorized users/system processes may:

* create training jobs;
* access private training datasets;
* inspect sensitive experiment results;
* approve models;
* promote models;
* rollback production models.

---

# 110. Training Isolation from POS

Training must not block:

* order creation;
* payment;
* cash sessions;
* inventory operations;
* synchronization;
* authentication.

AI training is a background workload.

---

# 111. Training Performance Targets

The following are initial architecture targets:

| Operation                           |                                     Target |
| ----------------------------------- | -----------------------------------------: |
| Training job creation               |                               p95 ≤ 500 ms |
| Dataset validation request          | p95 ≤ 2 s for standard metadata validation |
| Experiment metadata lookup          |                               p95 ≤ 300 ms |
| Standard Branch forecast training   |                                   ≤ 30 min |
| Standard Business forecast training |                                   ≤ 60 min |
| Lightweight model training          |                                   ≤ 10 min |
| Training status update              |                               p95 ≤ 500 ms |
| Evaluation metadata retrieval       |                               p95 ≤ 500 ms |
| Artifact integrity validation       |         ≤ 30 s for standard model artifact |
| Training job availability           |                                    ≥ 99.5% |

These are architecture targets, not guarantees for arbitrarily large datasets or future model classes.

---

# 112. Resource SLO

AI training must operate within controlled resource budgets.

Training workloads should not consume resources required to maintain core ERP SLOs.

When resource pressure occurs:

```text
ERP Core
   ↓
Highest Priority

AI Training
   ↓
Lower Priority
```

Training may be delayed rather than degrading POS performance.

---

# 113. Training Observability

Metrics should include:

* queued jobs;
* running jobs;
* failed jobs;
* cancelled jobs;
* training duration;
* evaluation duration;
* CPU usage;
* memory usage;
* GPU usage;
* artifact size;
* dataset size;
* retry count;
* timeout count;
* promotion rate.

---

# 114. Experiment Monitoring

Monitoring should identify:

* unusually long training;
* abnormal resource consumption;
* repeated failure;
* data-quality degradation;
* unexpected metric changes;
* artifact corruption;
* evaluation regression.

---

# 115. Training Alerts

Alerts may be generated for:

* repeated Training Run failures;
* resource exhaustion;
* data leakage detection;
* significant evaluation regression;
* artifact integrity failure;
* training queue backlog;
* unauthorized training activity.

Alerts must be deduplicated and must not flood users.

---

# 116. Model Training and AI Cost Management

Training resource usage should feed into AI cost management.

The system should identify:

```text
Business
   ↓
Model
   ↓
Training Runs
   ↓
Resource Usage
   ↓
Estimated Cost
```

This supports subscription and resource planning.

---

# 117. Training Testing

Training pipelines must be tested at multiple levels:

### Unit

* feature transformation;
* dataset filtering;
* metric calculations;
* configuration validation.

### Integration

* dataset generation;
* artifact storage;
* experiment persistence;
* queue/worker integration.

### Model

* baseline comparison;
* evaluation;
* regression tests.

### Security

* Business isolation;
* artifact validation;
* authorization;
* secret protection.

### Failure

* timeout;
* worker crash;
* storage failure;
* retry;
* cancellation.

---

# 118. Golden Training Datasets

Critical model pipelines should maintain controlled golden datasets.

Golden datasets provide stable regression tests for:

* feature generation;
* model behavior;
* metric calculations;
* output format.

Golden datasets must not contain unnecessary production-sensitive data.

---

# 119. Training Regression

A new training pipeline version must be evaluated against previous known-good behavior.

Unexpected regression must block promotion where required.

---

# 120. Model Quality Regression

A newly trained model should not replace a Champion merely because it is newer.

Promotion should require evidence that:

* quality is acceptable;
* required business metrics are acceptable;
* operational cost is acceptable;
* safety constraints are satisfied.

---

# 121. Experiment Reproducibility Test

For critical model types, the system should periodically verify that the recorded Training Run can be reconstructed from its lineage metadata.

Failure to reproduce should be recorded.

---

# 122. Experiment Cleanup

Temporary training artifacts may be cleaned after the configured retention period.

The system must preserve required:

* experiment metadata;
* production model lineage;
* approval history;
* audit events;
* model cards.

Cleanup must not break production lineage.

---

# 123. Artifact Retention

Artifact retention should distinguish:

* temporary checkpoints;
* failed experiment artifacts;
* candidate artifacts;
* approved production models;
* retired production models.

Retention must follow storage and lifecycle policy.

---

# 124. Training Failure Recovery

Recovery may include:

```text
Failure
  ↓
Classify
  ↓
Retry if transient
  ↓
Resume/restart where supported
  ↓
Re-evaluate
  ↓
Reject or continue
```

Recovery must never silently convert a failed run into a successful run.

---

# 125. Training and Model Registry

The Model Registry is the authoritative registry for approved model versions.

Training creates candidates.

Model Registry records approved model identity and lifecycle.

Training must not directly change the active production model without the required promotion workflow.

---

# 126. Training and Deployment

Training and deployment are separate concerns.

```text
Training
   ↓
Evaluation
   ↓
Approval
   ↓
Registry
   ↓
Deployment
```

Deployment failures must not invalidate the historical Training Run.

---

# 127. Production Model Selection

Inference services must resolve the active model through the Model Registry or approved model configuration.

They must not simply load:

```text
latest_model.pkl
```

from storage.

---

# 128. Latest vs Active

The newest model is not necessarily the active model.

Example:

```text
v5 → newest
v4 → active
```

until v5 is approved and deployed.

---

# 129. Model Rollback Integrity

Rollback must preserve:

* Model v5;
* deployment attempt;
* rollback reason;
* actor/system;
* timestamp;
* previous active model;
* restored active model.

---

# 130. Training Governance

Training governance must ensure:

* reproducibility;
* data lineage;
* model lineage;
* controlled promotion;
* Business isolation;
* privacy;
* auditability;
* resource control.

---

# 131. System Invariants

The following invariants apply to AI Model Training and Experimentation:

1. Training is separate from inference.
2. Production inference never implicitly trains a model.
3. Every Experiment has a unique identity.
4. Every Training Run has a unique UUID.
5. Training Run identity is independent of filename.
6. Training uses a versioned dataset.
7. Training uses a versioned feature definition.
8. Training configuration is versioned.
9. Training code version is recorded.
10. Training environment version is recorded where required.
11. Random seed is recorded where applicable.
12. Prediction cutoff is defined for time-dependent datasets.
13. Future information must not leak into historical model inputs.
14. Train/validation/test separation is controlled.
15. Time-series models use time-aware evaluation where required.
16. Test data must not be repeatedly used for tuning.
17. Dataset scope is explicitly recorded.
18. Business-specific datasets cannot contain another Business's private data.
19. Branch scope is explicit.
20. Historical prices use historically applicable configuration where relevant.
21. Historical inventory state is not silently replaced by current state.
22. Stockout conditions must be distinguished where relevant.
23. Invalid data must not silently enter training.
24. Data-quality thresholds are defined for important pipelines.
25. Insufficient data must be represented explicitly.
26. Cold-start Businesses may use shared or baseline models.
27. Training requests are authorized.
28. Training jobs are idempotent where retries are possible.
29. Duplicate training must not create duplicate production models.
30. Training executes asynchronously.
31. Training does not run inside the normal API request path.
32. Training workers are isolated from ERP mutation capabilities.
33. Training cannot modify authoritative ERP state.
34. Training cannot modify permissions.
35. Training cannot modify subscriptions.
36. Training cannot modify audit history.
37. Training cannot modify financial transactions.
38. Training cannot modify inventory transactions.
39. Training cannot modify prices.
40. Production model artifacts are immutable.
41. Model artifacts have integrity validation.
42. Untrusted model artifacts must not be loaded as executable code.
43. Model Candidate is not automatically a Production Model.
44. Training success does not imply production approval.
45. Evaluation is separate from training.
46. Baseline comparison is required where applicable.
47. Business metrics may be considered in model promotion.
48. Evaluation metrics are stored structurally.
49. Evaluation methodology is versioned.
50. Incompatible experiments must not be compared as equivalent.
51. Reproducibility metadata is retained.
52. Model lineage is reconstructable.
53. Model versions are immutable.
54. Historical predictions retain their generating model version.
55. Retraining creates a new Training Run.
56. Retraining does not overwrite historical experiments.
57. Champion and Challenger states are explicit.
58. Newer does not automatically mean better.
59. Model promotion requires defined criteria.
60. High-risk models may require human approval.
61. AI cannot approve itself.
62. Shadow evaluation cannot modify authoritative ERP state.
63. Canary deployment scope is explicit.
64. Rollback does not delete the newer model history.
65. Training failures cannot create active models.
66. Retry behavior is controlled.
67. Retry cannot duplicate production promotion.
68. Training timeout results are explicit.
69. Cancellation preserves history.
70. Queued jobs are revalidated before execution.
71. Subscription restrictions apply to queued training jobs.
72. Business lifecycle restrictions apply to queued training jobs.
73. Deleted Business data must follow lifecycle deletion rules.
74. Offline devices cannot independently train production models.
75. Unsynchronized offline transactions are not authoritative training data.
76. Configuration changes relevant to features are versioned.
77. Prompt versions and model versions are separate artifacts.
78. Secrets must not be stored in experiment metadata.
79. External model providers require explicit data-transfer controls.
80. Private Business data must not be transferred externally without approved architecture.
81. Model Cards are maintained for production-bound models where required.
82. Experiment reports preserve important evaluation context.
83. Training artifacts are traceable to their Training Run.
84. Model Registry remains authoritative for approved production model identity.
85. Training cannot silently replace the active model.
86. Deployment is separate from training.
87. Rollback preserves deployment history.
88. Training resource usage is monitored.
89. AI training must not degrade core ERP SLOs.
90. ERP workloads have higher priority than AI training.
91. Training concurrency is controlled.
92. Training jobs have resource limits.
93. Training jobs have execution time limits.
94. Temporary artifacts may be cleaned without breaking production lineage.
95. Production model lineage must remain reconstructable.
96. Training pipeline changes require regression testing.
97. Golden datasets may be used for stable regression testing.
98. Model quality regression can block promotion.
99. Experiment audit events are immutable.
100. Human approval actions are attributable.
101. System-generated experiments identify their job source.
102. AI training remains advisory to ERP authority.
103. AI model training cannot bypass ERP security boundaries.
104. AI training cannot bypass Business isolation.
105. AI training cannot bypass subscription entitlement.
106. AI training cannot bypass data lifecycle policy.
107. AI training must fail safely.
108. AI training failure must not stop core ERP operations.
109. Model version selection must not rely solely on filename or timestamp.
110. Active model selection must be deterministic.
111. Model rollback must be auditable.
112. Training and experiment history must remain immutable.
113. AI model quality must be evaluated against appropriate baselines.
114. Model complexity must be justified by measurable value.
115. Resource cost must be considered for production model selection.
116. Training outputs must be validated before promotion.
117. A model artifact without sufficient provenance must not become production.
118. A model without an identifiable dataset/feature lineage must not be promoted.
119. A model must not be promoted when critical evaluation data is invalid.
120. The training system must preserve the distinction between experiment, candidate, approved model and deployed model.

---

# 132. Related Documents

### AI Architecture

* `docs/04_Architecture/08_AI/01_AI_Architecture_Overview.md`
* `docs/04_Architecture/08_AI/02_AI_Use_Cases_and_Capabilities.md`
* `docs/04_Architecture/08_AI/03_AI_Boundaries_and_Non_AI_Decisions.md`
* `docs/04_Architecture/08_AI/04_AI_Data_Architecture.md`
* `docs/04_Architecture/08_AI/05_AI_Data_Preparation_and_Feature_Engineering.md`
* `docs/04_Architecture/08_AI/06_AI_Model_Architecture_and_Model_Strategy.md`
* `docs/04_Architecture/08_AI/07_AI_Forecasting_and_Demand_Prediction.md`
* `docs/04_Architecture/08_AI/08_AI_Inventory_and_Purchasing_Intelligence.md`
* `docs/04_Architecture/08_AI/09_AI_Anomaly_Detection_and_Business_Risk.md`
* `docs/04_Architecture/08_AI/10_AI_Business_Insights_and_Recommendations.md`
* `docs/04_Architecture/08_AI/11_AI_LLM_and_Natural_Language_Architecture.md`
* `docs/04_Architecture/08_AI/12_AI_Prompt_Context_and_Guardrails.md`
* `docs/04_Architecture/08_AI/14_AI_Monitoring_and_Drift.md`
* `docs/04_Architecture/08_AI/16_AI_Model_Registry.md`
* `docs/04_Architecture/08_AI/17_AI_Jobs_and_Pipeline_Architecture.md`
* `docs/04_Architecture/08_AI/19_AI_Output_Validation.md`
* `docs/04_Architecture/08_AI/20_AI_Explainability_and_Transparency.md`
* `docs/04_Architecture/08_AI/21_AI_Security_and_Privacy.md`
* `docs/04_Architecture/08_AI/22_AI_Governance_and_Human_Approval.md`
* `docs/04_Architecture/08_AI/24_AI_Cost_and_Resource_Management.md`
* `docs/04_Architecture/08_AI/25_AI_Failure_Recovery.md`
* `docs/04_Architecture/08_AI/26_AI_Deployment_and_Runtime_Architecture.md`
* `docs/04_Architecture/08_AI/27_AI_Testing_and_Quality_Assurance.md`
* `docs/04_Architecture/08_AI/28_AI_Operations_and_Observability.md`

### Backend

* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/21_Backend_Disaster_Recovery_and_Business_Continuity_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/07_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/04_Architecture/07_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/07_Database/23_Configuration_Data_Model.md`
* `docs/04_Architecture/07_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/04_Architecture/07_Database/25_Database_Integrity_and_Constraints.md`
* `docs/04_Architecture/07_Database/29_Database_Security.md`
* `docs/04_Architecture/07_Database/30_Database_Invariants_and_Guardrails.md`

### Business and System Analysis

* `docs/01_Business_Analysis/`
* `docs/02_System_Analysis/`

---

# 133. Status

**AI Architecture Document:** Proposed
**Version:** 1.0
**Current Document:** `13_AI_Model_Training_and_Experimentation.md`

**Previous Document:** `12_AI_Prompt_Context_and_Guardrails.md`

**Next Document:** `14_AI_Monitoring_and_Drift.md`

