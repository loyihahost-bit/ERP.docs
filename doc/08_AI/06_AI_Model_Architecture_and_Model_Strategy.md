# AI Model Architecture and Model Strategy

**Document ID:** AI-06
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/08_AI/README.md`

---

## 1. Purpose

This document defines the architecture and strategy for selecting, developing, versioning, deploying and operating AI models within FastFood ERP.

The main objectives are:

* appropriate model selection for each AI use case;
* separation of model logic from ERP business logic;
* reproducible model lifecycle;
* model versioning;
* model and feature compatibility;
* explainable model behavior where required;
* controlled model deployment;
* safe model rollback;
* resource-efficient AI operation;
* protection of ERP performance;
* Business and Branch isolation.

The model layer is a derived intelligence layer.

It does not become the authoritative source of ERP business state.

---

# 2. Scope

This document covers:

* model architecture;
* model categories;
* model selection;
* forecasting models;
* classification models;
* anomaly detection models;
* recommendation models;
* ranking models;
* NLP/LLM model boundary;
* baseline models;
* model training;
* model validation;
* model versioning;
* model registry;
* feature compatibility;
* model packaging;
* model serving;
* model deployment;
* model rollback;
* model lifecycle;
* model resource management;
* model selection criteria;
* cold-start strategy;
* Business/Branch scope;
* model metadata;
* model reproducibility;
* model security;
* model performance requirements.

---

# 3. Architectural Position

The model layer sits between prepared AI data and AI inference.

```text
Authoritative ERP
       ↓
AI Data Architecture
       ↓
Data Preparation / Features
       ↓
Model
       ↓
Inference
       ↓
Output Validation
       ↓
AI Result
       ↓
ERP Application / UI
```

The model must not directly modify authoritative ERP state.

---

# 4. Core Principle

The central principle is:

> **Models interpret data; ERP determines business truth.**

Therefore:

```text
Model Prediction
      ≠
ERP Fact
```

and:

```text
Model Recommendation
      ≠
ERP Command
```

---

# 5. Model Authority

Models operate within the authority levels defined by AI architecture.

### Level 0 — Informational

Model output explains or summarizes information.

### Level 1 — Predictive

Model predicts future or unknown values.

### Level 2 — Recommendational

Model recommends an action.

### Level 3 — Controlled Action

Future capability requiring explicit authorization and deterministic ERP validation.

Current architecture primarily supports Levels 0–2.

---

# 6. Model Categories

FastFood ERP may use:

1. Forecasting Models
2. Regression Models
3. Classification Models
4. Anomaly Detection Models
5. Ranking Models
6. Recommendation Models
7. Clustering Models
8. Time-Series Models
9. NLP Models
10. LLMs
11. Hybrid Models
12. Rule + Model Systems

---

# 7. Model Selection Principle

The simplest model that reliably solves the business problem should be preferred.

The system should not select a complex model merely because it is technically advanced.

Priority:

```text
Business Value
    ↓
Correctness
    ↓
Reliability
    ↓
Explainability
    ↓
Operational Cost
    ↓
Complexity
```

---

# 8. Baseline First

Every important predictive use case should have a baseline.

Example:

```text
Naive Forecast
      ↓
Statistical Model
      ↓
Machine Learning Model
      ↓
Advanced Model
```

A complex model should only replace a baseline when it demonstrates meaningful improvement.

---

# 9. Baseline Models

Possible baselines include:

* last-value;
* moving average;
* seasonal naive;
* historical weekday average;
* exponential smoothing;
* simple linear model.

Baseline models are important for:

* benchmarking;
* fallback;
* regression detection;
* cold-start support.

---

# 10. Model Selection Criteria

Model selection should consider:

* prediction accuracy;
* business usefulness;
* data availability;
* training cost;
* inference latency;
* memory usage;
* explainability;
* maintenance complexity;
* drift sensitivity;
* cold-start behavior;
* failure behavior.

---

# 11. Forecasting Models

Forecasting models may be used for:

* product demand;
* inventory depletion;
* Branch sales;
* purchase planning;
* sales trends.

Possible model families:

* moving average;
* exponential smoothing;
* ARIMA-family models;
* gradient boosting;
* tree-based regression;
* temporal neural networks;
* other specialized time-series models.

The architecture does not mandate one algorithm.

---

# 12. Demand Forecasting

Demand forecasting should predict expected demand rather than blindly predict observed sales.

Important inputs may include:

* historical sales;
* stock availability;
* price;
* discounts;
* day of week;
* seasonality;
* menu availability;
* Branch context;
* holidays;
* operating hours.

---

# 13. Stockout-Aware Forecasting

A model must distinguish:

```text
Low Sales
```

from:

```text
Low Sales Because Product Was Unavailable
```

Stock availability features should therefore be available to the model where applicable.

---

# 14. Forecast Horizon

Forecast models should explicitly define:

* forecast horizon;
* prediction interval;
* aggregation period.

Examples:

```text
Next 1 day
Next 3 days
Next 7 days
Next 14 days
```

The horizon is model-specific.

---

# 15. Forecast Output

A forecast may contain:

```text
predicted_value
lower_bound
upper_bound
confidence
model_version
feature_version
generated_at
```

Not every model must provide statistical intervals, but uncertainty should be represented where technically appropriate.

---

# 16. Regression Models

Regression may be used for:

* expected sales;
* expected demand;
* expected inventory consumption;
* estimated operational metrics.

Regression outputs must remain clearly identified as predictions.

---

# 17. Classification Models

Classification may be used for:

* anomaly categories;
* risk classification;
* product demand states;
* operational state prediction.

Example:

```text
Normal
Unusual
High Risk
```

Classification labels must be documented and versioned.

---

# 18. Anomaly Detection Models

Anomaly detection may identify unusual:

* refunds;
* discounts;
* sales;
* inventory adjustments;
* cash discrepancies;
* order patterns.

An anomaly score does not automatically mean fraud or misconduct.

---

# 19. Anomaly Model Strategy

Possible approaches:

* statistical thresholds;
* z-score based methods;
* isolation-based models;
* clustering;
* autoencoder-based methods;
* hybrid rules + ML.

Deterministic high-risk business rules remain outside the model.

---

# 20. Rule + Model Architecture

Some AI capabilities should combine deterministic rules with ML.

Example:

```text
ERP Data
   ↓
Deterministic Eligibility
   ↓
AI Model
   ↓
Output Validation
   ↓
AI Result
```

This prevents models from operating outside permitted business boundaries.

---

# 21. Recommendation Models

Recommendation models may suggest:

* purchase quantities;
* products requiring attention;
* menu optimization opportunities;
* inventory actions;
* operational insights.

The recommendation remains advisory unless explicitly approved and executed through ERP workflows.

---

# 22. Recommendation Constraints

Recommendations must respect:

* Business scope;
* Branch scope;
* subscription;
* inventory state;
* permissions;
* Product state;
* Recipe constraints;
* operational rules.

The model must not recommend impossible ERP operations.

---

# 23. Ranking Models

Ranking models may rank:

* products requiring attention;
* likely stockout Products;
* important alerts;
* Branch performance issues;
* purchase priorities.

Ranking should optimize usefulness rather than merely prediction accuracy.

---

# 24. Clustering

Clustering may be used for exploratory analysis such as:

* Product behavior groups;
* Branch behavior groups;
* sales pattern groups.

Clusters are analytical constructs.

They do not create new ERP entities.

---

# 25. NLP Models

NLP models may process:

* natural-language questions;
* report explanations;
* business summaries;
* controlled text queries.

NLP outputs must remain within authorization and ERP context.

---

# 26. LLM Boundary

LLMs are not authoritative business engines.

They may:

* interpret user questions;
* summarize approved data;
* explain reports;
* generate natural-language recommendations;
* transform structured results into readable text.

They may not independently modify ERP state.

---

# 27. Hybrid Model Architecture

A single AI capability may combine multiple model types.

Example:

```text
Time-Series Model
       ↓
Demand Forecast
       ↓
Rule Engine
       ↓
Recommendation Model
       ↓
LLM Explanation
```

Each layer has a separate responsibility.

---

# 28. Model Responsibility Separation

A model should have one clearly defined primary purpose.

Avoid one model becoming responsible for:

* forecasting;
* authorization;
* transaction execution;
* financial calculation;
* business rule enforcement.

These responsibilities belong to different architectural layers.

---

# 29. Deterministic Calculations

Deterministic calculations should not be replaced by ML where exact computation is required.

Examples:

* Order total;
* payment amount;
* stock deduction;
* payroll calculation;
* cash discrepancy;
* subscription expiry;
* permission evaluation.

AI may explain these results but does not calculate authoritative values.

---

# 30. Model Input Contract

Every production model must define an input contract.

Minimum metadata:

```text
model_input_schema
feature_versions
scope
timestamp
required_features
optional_features
missing_value_policy
```

---

# 31. Model Output Contract

Every production model must define an output contract.

Example:

```text
prediction
confidence
model_version
feature_version
generated_at
data_quality
```

The exact fields depend on model type.

---

# 32. Model Versioning

Every production model must have an immutable version.

Example:

```text
demand-forecast-v1
demand-forecast-v2
demand-forecast-v3
```

A deployed model version must never be silently replaced.

---

# 33. Model Identity

A model should have:

```text
model_uuid
model_name
model_version
model_type
use_case
status
```

The model identity is separate from the prediction result identity.

---

# 34. Model Registry

The architecture should maintain a Model Registry containing:

* model identity;
* version;
* model type;
* feature dependencies;
* training dataset;
* evaluation results;
* artifact location;
* deployment status;
* created timestamp;
* approval state;
* owner;
* resource requirements.

---

# 35. Model Lifecycle

A model follows:

```text
DRAFT
  ↓
TRAINING
  ↓
EVALUATION
  ↓
VALIDATED
  ↓
APPROVED
  ↓
DEPLOYED
  ↓
DEPRECATED
  ↓
RETIRED
```

Exact implementation states may be simplified but lifecycle semantics must remain.

---

# 36. Model Approval

A production model must not become active merely because training completed successfully.

Production activation requires:

* validation;
* evaluation;
* compatibility check;
* security review where applicable;
* deployment approval.

---

# 37. Model Artifact

A model artifact may contain:

* trained weights;
* architecture;
* preprocessing references;
* metadata;
* dependency information;
* model signature.

Artifacts must be immutable after activation.

---

# 38. Model Reproducibility

A production model should be reproducible from:

* source code version;
* dataset version;
* feature versions;
* training configuration;
* dependency versions;
* model artifact;
* random seed where applicable.

Exact bit-level reproducibility is not always mandatory, but training provenance must be preserved.

---

# 39. Dataset Compatibility

A model must identify the dataset used during training.

Example:

```text
Model:
demand-v3

Dataset:
demand-training-v8

Features:
sales-v2
inventory-v1
calendar-v1
```

---

# 40. Feature Compatibility

A model must only consume compatible feature versions.

If a required feature changes semantically, the model must be:

* retrained;
* explicitly validated;
* or rejected from deployment.

---

# 41. Training/Serving Compatibility

The model serving environment must use the same semantic preprocessing as training.

Training-serving skew must be detected.

---

# 42. Model Evaluation

Evaluation should consider:

### Technical Metrics

* MAE;
* RMSE;
* MAPE where appropriate;
* precision;
* recall;
* F1;
* ROC-AUC;
* PR-AUC;
* calibration.

### Business Metrics

* stockout reduction;
* forecast usefulness;
* purchase planning quality;
* false-alert reduction;
* operational time saved.

The correct metric depends on the model.

---

# 43. Forecast Evaluation

Forecasting should commonly evaluate:

* MAE;
* RMSE;
* WAPE;
* MASE;
* bias;
* service-level impact.

MAPE should not be used blindly when actual demand may be zero.

---

# 44. Classification Evaluation

Classification may use:

* precision;
* recall;
* F1;
* ROC-AUC;
* PR-AUC;
* confusion matrix;
* calibration.

Threshold selection should consider business consequences.

---

# 45. Anomaly Evaluation

Anomaly models should evaluate:

* precision;
* recall where labels exist;
* false-positive rate;
* alert volume;
* confirmed useful anomaly rate.

When ground truth is unavailable, operational review may be used as supplementary evaluation.

---

# 46. Recommendation Evaluation

Recommendation models may evaluate:

* acceptance rate;
* usefulness;
* conversion where applicable;
* avoided stockout;
* reduced waste;
* operational impact.

The evaluation must not reward recommendations merely because they increase system activity.

---

# 47. Business Impact

Model selection should ultimately consider business value.

Example:

```text
Model A
MAE = 10

Model B
MAE = 9

```

If Model B requires 10× more resources without meaningful operational benefit, Model A may remain preferable.

---

# 48. Model Benchmarking

Models should be compared against:

* baseline;
* previous production model;
* candidate models.

A candidate should demonstrate measurable improvement before replacing the production model.

---

# 49. Champion / Challenger

For important models:

```text
Champion
    ↓
Current Production Model

Challenger
    ↓
Candidate Model
```

The challenger may run in shadow mode before activation.

---

# 50. Shadow Inference

A challenger model may receive production-like inputs without affecting user-visible decisions.

Example:

```text
Production Request
       ↓
 ┌───────────────┐
 ↓               ↓
Champion      Challenger
 ↓               ↓
User Result    Evaluation Only
```

This allows safe comparison.

---

# 51. A/B Testing

Where appropriate, model variants may be evaluated through controlled experimentation.

A/B testing must preserve:

* Business isolation;
* Branch scope;
* experiment assignment;
* reproducibility;
* auditability.

The detailed experimentation architecture is defined separately.

---

# 52. Canary Deployment

A new model may be deployed to a small controlled percentage of eligible workloads before broader activation.

Example:

```text
New Model
   ↓
Small Scope
   ↓
Observe
   ↓
Expand
```

---

# 53. Rollback

Every production model deployment must have a rollback path.

Rollback should restore the previously validated model version.

Example:

```text
v3 active
 ↓
v4 deployed
 ↓
Problem detected
 ↓
v3 restored
```

Rollback must not modify historical ERP data.

---

# 54. Prediction Versioning

Predictions should retain:

```text
prediction_uuid
model_uuid
model_version
feature_version
generated_at
scope
input_reference
```

This allows historical AI results to be understood later.

---

# 55. Prediction Immutability

Once an AI result has been persisted as a historical result, it should not be silently overwritten.

A newer prediction should create a new prediction result/version.

---

# 56. Prediction Supersession

For repeated predictions:

```text
Prediction v1
      ↓
Prediction v2
      ↓
Prediction v3
```

the system should identify which result is current and which are historical.

---

# 57. Model Freshness

Each production model should have an expected refresh/training cadence.

Example:

```text
Demand Model:
retrain weekly
```

The exact schedule depends on data volume and drift.

---

# 58. Retraining Strategy

Retraining may be:

* scheduled;
* triggered by drift;
* triggered by performance degradation;
* triggered by significant business changes;
* manually initiated.

Retraining must pass the same validation gates as a new model.

---

# 59. Retraining Trigger

A retraining trigger should not automatically cause deployment.

Correct flow:

```text
Drift Detected
     ↓
Retraining
     ↓
Evaluation
     ↓
Validation
     ↓
Approval
     ↓
Deployment
```

---

# 60. Model Drift

Model monitoring may detect:

* feature drift;
* prediction drift;
* performance drift;
* data quality degradation;
* business behavior change.

Drift does not automatically mean the model is wrong.

It is a signal for investigation.

---

# 61. Concept Drift

Business behavior may change.

Examples:

* menu changes;
* new Branch;
* price changes;
* customer behavior changes;
* seasonal changes;
* operational policy changes.

The model strategy must account for these changes.

---

# 62. Model Freshness vs Accuracy

A newer model is not automatically better.

Deployment decisions should consider:

* evaluation results;
* recent performance;
* business impact;
* stability;
* resource cost.

---

# 63. Cold Start Strategy

For new Businesses, Branches or Products:

1. use baseline models;
2. use hierarchical features;
3. use category-level patterns;
4. use Business-level patterns where available;
5. identify insufficient-data state.

A model must not pretend to have sufficient historical evidence.

---

# 64. New Product Strategy

New Products may use:

```text
Product
   ↓
Category
   ↓
Branch
   ↓
Business
```

hierarchical information when product-level history is insufficient.

---

# 65. New Branch Strategy

New Branches may initially use:

* Business-level patterns;
* comparable Branch patterns;
* category patterns;
* baseline forecasts.

Branch-specific modeling should begin when sufficient data exists.

---

# 66. New Business Strategy

A new Business may have no historical data.

The AI system should return:

```text
insufficient_history
```

or use explicitly defined global/business-independent baselines.

It must not fabricate historical behavior.

---

# 67. Model Resource Strategy

Model selection must consider available hardware.

The initial architecture should prefer models that can operate within reasonable CPU/memory limits.

GPU-dependent models should be introduced only where business value justifies operational complexity.

---

# 68. CPU-First Principle

For many ERP AI workloads:

* forecasting;
* tabular prediction;
* anomaly detection;
* ranking

should prefer CPU-compatible models where practical.

---

# 69. GPU Usage

GPU infrastructure may be used for:

* large LLMs;
* computer vision if introduced;
* expensive deep-learning workloads.

GPU usage must be isolated from core ERP infrastructure where practical.

---

# 70. Model Serving Modes

Models may be served through:

### Synchronous

For low-latency inference.

### Asynchronous

For expensive predictions.

### Batch

For periodic predictions.

### Hybrid

Depending on use case.

---

# 71. Synchronous Model Use

Synchronous inference is appropriate when:

* latency requirement is low;
* model is lightweight;
* inference does not block critical ERP transactions.

Example:

```text
User Request
 ↓
Feature Lookup
 ↓
Model
 ↓
Result
```

---

# 72. Asynchronous Model Use

Asynchronous inference is preferred when:

* inference is expensive;
* result is not needed immediately;
* large datasets are involved.

Example:

```text
ERP Event
 ↓
AI Queue
 ↓
Model
 ↓
AI Result
 ↓
Notification/Dashboard
```

---

# 73. Batch Inference

Batch inference may generate:

* daily demand forecasts;
* Branch insights;
* product rankings;
* inventory recommendations.

Batch jobs must be isolated from core transaction processing.

---

# 74. Model Latency Targets

Initial targets:

| Workload                                |       Target |
| --------------------------------------- | -----------: |
| Lightweight synchronous model inference | p95 ≤ 500 ms |
| Standard AI API response excluding LLM  |  p95 ≤ 1.5 s |
| Batch daily prediction generation       |     ≤ 30 min |
| Standard Branch forecast generation     |      ≤ 5 min |
| Model health check                      |        ≤ 1 s |

These targets are initial architecture targets.

---

# 75. Model Availability

AI model availability should not become an ERP availability dependency.

If the model is unavailable:

```text
ERP continues
AI result unavailable
```

is preferable to:

```text
ERP operation blocked
```

---

# 76. Model Timeout

Every synchronous model invocation must have a timeout.

When timeout occurs:

* request should fail gracefully;
* ERP transaction should remain valid;
* fallback may be used if explicitly defined;
* timeout should be observable.

---

# 77. Model Retry

Retries should only occur when safe.

For deterministic inference, retries may be allowed.

For expensive operations, retry limits should prevent resource amplification.

---

# 78. Model Circuit Breaker

If a model service repeatedly fails:

```text
Healthy
  ↓
Degraded
  ↓
Circuit Open
  ↓
Recovery Test
  ↓
Healthy
```

Core ERP operations must remain unaffected.

---

# 79. Model Isolation

AI model workloads should be isolated from:

* POS workers;
* payment processing;
* inventory transactions;
* authentication;
* synchronization.

---

# 80. Model Security

Models and artifacts must be protected from:

* unauthorized replacement;
* malicious artifacts;
* unauthorized access;
* dependency vulnerabilities;
* prompt injection where LLMs are involved;
* model theft where applicable.

---

# 81. Model Artifact Validation

Before deployment:

* artifact integrity must be verified;
* expected model signature must be validated;
* dependency compatibility must be checked;
* model input/output contract must be validated.

---

# 82. Model Dependency Management

Model runtime dependencies must be pinned or controlled.

Uncontrolled dependency changes must not silently alter model behavior.

---

# 83. Model Isolation from ERP Database

Models should not have unrestricted direct write access to the ERP database.

Preferred:

```text
Model
 ↓
AI Application Layer
 ↓
Validated AI Result
 ↓
ERP Application Layer
```

---

# 84. Model Access to Data

Models should receive only required feature inputs.

They should not receive:

* passwords;
* authentication secrets;
* session credentials;
* unnecessary personal data;
* unrelated Business data.

---

# 85. Business Isolation

Every model inference request must contain sufficient scope information.

Example:

```text
business_uuid
branch_uuid
```

where applicable.

The model service must not infer scope from user-controlled natural language alone.

---

# 86. Permission Boundary

Authorization is performed before model data access.

Example:

```text
User
 ↓
Authentication
 ↓
Authorization
 ↓
Business/Branch Scope
 ↓
Feature Access
 ↓
Model
```

The model itself is not the authorization authority.

---

# 87. Subscription Boundary

AI capabilities must respect subscription entitlement.

If AI is not included in a Business tariff:

* model access is blocked;
* existing allowed historical results may remain viewable;
* AI workers must not bypass entitlement.

---

# 88. Model Logging

Production model requests should log appropriate metadata:

* request UUID;
* model version;
* feature version;
* Business scope;
* Branch scope where applicable;
* latency;
* result status;
* error type.

Sensitive raw feature values should not be logged unnecessarily.

---

# 89. Model Metrics

Operational metrics should include:

* inference count;
* inference latency;
* error rate;
* timeout rate;
* model version distribution;
* queue depth;
* resource consumption;
* prediction freshness.

---

# 90. Model Cost Tracking

Where model usage has meaningful cost, track:

* inference count;
* compute time;
* token usage for LLMs;
* GPU usage;
* external provider cost.

Cost tracking is especially important for SaaS subscription planning.

---

# 91. Model Resource Quotas

The AI architecture may enforce quotas such as:

* inference requests;
* batch jobs;
* LLM tokens;
* model compute time.

Quotas must respect subscription limits where applicable.

---

# 92. Model Failure Handling

Model failure must produce a controlled result.

Examples:

```text
MODEL_UNAVAILABLE
MODEL_TIMEOUT
INVALID_INPUT
FEATURE_UNAVAILABLE
INCOMPATIBLE_MODEL
INSUFFICIENT_DATA
```

The system must not convert technical failure into a fabricated prediction.

---

# 93. Model Fallback

Fallbacks may include:

* previous valid prediction;
* baseline model;
* simpler model;
* no-result state.

Fallback selection must be explicitly defined per use case.

---

# 94. Fallback Disclosure

If a fallback model produced the result, the system should preserve that information.

Example:

```text
prediction_source = baseline
```

This prevents users from assuming the primary model generated the result.

---

# 95. Model Result Confidence

Confidence must be interpreted according to model type.

A confidence value must not be presented as a universal probability of correctness unless statistically justified.

---

# 96. Model Calibration

Where probabilities are shown, calibration should be evaluated.

Examples:

* probability of anomaly;
* classification probability;
* risk score.

Poorly calibrated probabilities should not be presented as precise probabilities.

---

# 97. Model Explainability

Explainability requirements depend on use case.

Higher-impact recommendations should provide understandable reasoning where technically possible.

Example:

```text
Demand increased because:
- recent sales increased;
- weekend pattern detected;
- stock availability remained high.
```

The explanation must not invent causal claims unsupported by the model/data.

---

# 98. Feature Attribution

Where appropriate, models may provide:

* feature importance;
* SHAP-like attribution;
* contribution ranking.

These are explanatory signals, not necessarily causal explanations.

---

# 99. Causal Claims

The system must distinguish:

```text
Correlation / model contribution
```

from:

```text
Causation
```

AI should not claim that a variable caused an outcome without appropriate causal evidence.

---

# 100. Model Governance

Model governance covers:

* model ownership;
* approval;
* versioning;
* deployment;
* monitoring;
* rollback;
* retirement;
* audit.

Governance is especially important for models influencing financial or operational decisions.

---

# 101. Model Retirement

A model may be retired when:

* replaced by a better model;
* no longer used;
* data source removed;
* capability removed;
* operational cost becomes unjustified.

Retirement must preserve historical model references.

---

# 102. Historical Model Reproducibility

Historical AI results should remain understandable after model retirement.

At minimum:

```text
model_name
model_version
feature_version
generated_at
```

must remain identifiable.

---

# 103. Model Change Audit

Important model changes should be auditable:

* created;
* trained;
* validated;
* approved;
* deployed;
* rolled back;
* deprecated;
* retired.

---

# 104. Model Configuration

Runtime configuration should be separated from model artifact where appropriate.

Examples:

* threshold;
* forecast horizon;
* batch size;
* timeout;
* resource limits.

Configuration changes must be versioned when they alter model semantics.

---

# 105. Threshold Versioning

Classification/anomaly thresholds can materially change behavior.

Therefore:

```text
Model v2
Threshold v3
```

may need independent version tracking.

---

# 106. Model and Rule Interaction

When a model output is combined with deterministic rules:

```text
Model Score
    ↓
Rule Validation
    ↓
Allowed Result
```

the final business behavior must remain deterministic where required.

---

# 107. AI Result vs ERP Action

For recommendation workflows:

```text
Model
 ↓
Recommendation
 ↓
Human / Authorized Workflow
 ↓
ERP Validation
 ↓
ERP Action
```

The model should not bypass the final ERP validation.

---

# 108. Multi-Branch Models

A model may be:

### Business-Specific

Trained for one Business.

### Shared

Used across multiple Businesses.

### Hybrid

Shared model with Business-specific features/calibration.

The selected approach must preserve tenant isolation.

---

# 109. Shared Model Strategy

Shared models may improve cold-start behavior and reduce training cost.

However:

* Business-specific data must remain isolated;
* inference scope must remain correct;
* model behavior must be monitored for Business differences.

---

# 110. Business-Specific Fine-Tuning

Business-specific training should be introduced only when:

* sufficient data exists;
* measurable benefit exists;
* operational cost is justified.

It should not be the default architecture.

---

# 111. Branch-Specific Models

Branch-specific models should be used only when enough data exists.

Otherwise, hierarchical or shared models are preferred.

---

# 112. Model Hierarchy

A possible strategy:

```text
Global Baseline
      ↓
Shared Model
      ↓
Business Calibration
      ↓
Branch Context
      ↓
Product Context
```

The exact implementation depends on model type.

---

# 113. Model Personalization

Personalization must not violate:

* tenant isolation;
* privacy;
* authorization;
* historical integrity.

---

# 114. Model Transfer

Model transfer between Businesses must not expose:

* raw source data;
* Business-identifiable records;
* confidential configurations.

Only approved model artifacts or aggregated representations may be shared.

---

# 115. Model Training Data Privacy

Training pipelines should minimize personal data.

Where aggregate business behavior is sufficient, individual employee or customer information should not be included.

---

# 116. External Model Providers

External AI providers may be used only through controlled integration boundaries.

The model architecture must define:

* provider;
* model;
* data sent;
* retention;
* security;
* cost;
* fallback.

---

# 117. External Model Independence

The ERP must not become dependent on a single external AI provider for core ERP functionality.

Provider failure must degrade AI functionality rather than ERP functionality.

---

# 118. Open-Source vs Managed Models

Model selection may consider:

### Managed Provider

Advantages:

* simpler operations;
* fast access to advanced models.

Risks:

* external dependency;
* cost;
* data transfer;
* provider changes.

### Self-Hosted

Advantages:

* greater control;
* predictable data boundary.

Risks:

* infrastructure;
* maintenance;
* GPU requirements.

The choice is use-case specific.

---

# 119. Model Strategy by AI Capability

Recommended initial mapping:

| Capability                 | Preferred Initial Strategy     |
| -------------------------- | ------------------------------ |
| Demand Forecasting         | Statistical / ML baseline      |
| Inventory Prediction       | Statistical / ML               |
| Sales Forecasting          | Time-Series / ML               |
| Inventory Anomaly          | Statistical + ML               |
| Cash/Refund Anomaly        | Rule + anomaly model           |
| Product Insights           | Aggregation + ML               |
| Purchase Recommendation    | Forecast + deterministic rules |
| Business Insights          | ML + deterministic analytics   |
| Report Explanation         | Controlled LLM                 |
| Natural-Language Assistant | LLM + tool layer               |

This is a strategy, not a mandatory algorithm selection.

---

# 120. Initial Model Complexity

The initial AI architecture should favor:

* classical ML;
* statistical forecasting;
* lightweight anomaly detection;
* controlled LLM integration.

Deep learning should be introduced only where measurable benefit exists.

---

# 121. Model Strategy Evolution

The architecture may evolve:

```text
Baseline
   ↓
Classical ML
   ↓
Advanced ML
   ↓
Deep Learning
```

Each transition requires evidence that the added complexity provides value.

---

# 122. Model Development Environment

Training environments should be isolated from production ERP runtime.

Development and experimentation must not have unrestricted production write access.

---

# 123. Production Model Promotion

Recommended promotion:

```text
Development
   ↓
Evaluation
   ↓
Validation
   ↓
Staging
   ↓
Shadow
   ↓
Canary
   ↓
Production
```

Not every model requires every stage, but production-impacting models should use appropriate controls.

---

# 124. Model Artifact Storage

Model artifacts should be stored separately from transactional ERP records.

Metadata may remain in the application database while large artifacts may use object storage.

---

# 125. Model Artifact Retention

Retention should consider:

* active models;
* historical production models;
* reproducibility;
* storage cost;
* Business deletion;
* governance requirements.

---

# 126. Model Packaging

A production model package should contain enough metadata to identify:

```text
model
version
features
runtime
dependencies
input schema
output schema
```

---

# 127. Model Runtime Compatibility

The serving environment must validate:

* runtime version;
* dependency versions;
* hardware requirements;
* input schema;
* output schema.

---

# 128. Model Health Check

A deployed model service should support a health check that verifies:

* process availability;
* model loaded;
* required dependencies available;
* compatible model artifact;
* inference readiness.

---

# 129. Model Readiness

A model service should not be considered ready merely because the process is running.

Readiness requires:

```text
Service Running
+
Model Loaded
+
Artifact Valid
+
Dependencies Ready
```

---

# 130. Model Warmup

Models may require warmup.

Warmup must not block core ERP startup.

Model services may initialize independently.

---

# 131. Model Memory Management

Model serving must control memory usage.

Large models should not be loaded into every ERP worker process unnecessarily.

---

# 132. Model Worker Isolation

Where appropriate:

```text
ERP Workers
     |
     +---- AI Service
             |
             +---- Model Worker
```

AI compute should be isolated from transactional workers.

---

# 133. Model Queueing

Expensive inference may use the AI queue architecture.

Queue jobs must include:

* request UUID;
* Business scope;
* Branch scope where applicable;
* model version;
* feature version;
* priority;
* retry information.

---

# 134. Model Priority

Core AI tasks may have priority levels.

Example:

```text
High:
User-requested forecast

Normal:
Scheduled forecast

Low:
Historical backfill
```

Priority must never override authorization.

---

# 135. Model Job Idempotency

AI jobs must be idempotent where retries are possible.

Repeated execution should not create duplicate logical AI results.

---

# 136. Model Job Cancellation

Long-running AI jobs should support controlled cancellation where practical.

Cancellation must leave the system in a consistent state.

---

# 137. Model Data Freshness

A model prediction must record the freshness of the features it consumed.

Example:

```text
features_as_of = 2026-10-05T10:00
prediction_created = 2026-10-05T10:04
```

---

# 138. Prediction Validity Window

Some predictions may become stale.

Example:

```text
Forecast generated at 10:00
Valid until 18:00
```

The validity window must be defined by the use case.

---

# 139. Stale Prediction Handling

A stale prediction should be:

* refreshed;
* marked stale;
* replaced;
* or hidden according to use-case rules.

It must not silently appear current.

---

# 140. Model Result Storage

Stored AI results should include sufficient provenance:

```text
prediction_uuid
business_uuid
branch_uuid
model_uuid
model_version
feature_version
created_at
valid_until
quality_status
```

---

# 141. Model Result Scope

AI results must preserve the scope they were generated for.

A Branch-specific prediction must not be displayed as a Business-wide prediction.

---

# 142. Model Result Authorization

Before displaying a historical AI result, the system must re-evaluate current user authorization where required.

Historical existence does not grant access.

---

# 143. Model Result and Subscription

Subscription restrictions apply to AI capabilities.

If a Business becomes read-only:

* historical allowed AI results may remain viewable;
* new AI generation may be blocked;
* background AI jobs must respect entitlement.

---

# 144. Model Result and Deletion

Business deletion must remove or anonymize Business-specific model results according to lifecycle rules.

External provider copies must be handled according to the provider integration policy.

---

# 145. Model Strategy Documentation

Each production model should have a model card or equivalent documentation containing:

* purpose;
* intended use;
* prohibited use;
* input data;
* output;
* metrics;
* limitations;
* known failure modes;
* training data period;
* feature versions;
* deployment status.

---

# 146. Model Limitations

Every model must document important limitations.

Examples:

* insufficient history;
* stockout bias;
* seasonal instability;
* rare events;
* sparse Product sales;
* Branch changes.

---

# 147. Model Risk Classification

Models may be classified:

### Low Risk

Informational summaries and low-impact predictions.

### Medium Risk

Operational recommendations.

### High Risk

Models influencing financial, personnel, security or other sensitive decisions.

High-risk models require stronger validation and governance.

---

# 148. High-Risk Model Rule

High-risk AI must not independently execute irreversible ERP actions.

The current architecture requires:

```text
AI
 ↓
Recommendation
 ↓
Authorized Human / Deterministic Workflow
 ↓
ERP Validation
```

---

# 149. Model Change Risk

Model changes must consider:

* metric improvement;
* behavior change;
* business impact;
* false-positive changes;
* false-negative changes;
* resource impact.

Higher-risk changes require stronger validation.

---

# 150. Model Deployment SLOs

Initial architecture targets:

| Operation                      |       Target |
| ------------------------------ | -----------: |
| Model readiness check          |        ≤ 1 s |
| Lightweight model inference    | p95 ≤ 500 ms |
| Standard model inference       |  p95 ≤ 1.5 s |
| Model rollback initiation      |      ≤ 5 min |
| Model metadata lookup          | p95 ≤ 100 ms |
| AI service availability target |      ≥ 99.5% |

These are AI-layer targets and do not reduce ERP availability requirements.

---

# 151. ERP Independence SLO

AI failure must not reduce availability of:

* authentication;
* POS;
* orders;
* payments;
* cash sessions;
* inventory;
* synchronization.

AI is an optional derived capability from the ERP availability perspective.

---

# 152. Model Resource Limits

Every production model should have defined:

* CPU requirement;
* memory requirement;
* GPU requirement if any;
* maximum concurrency;
* timeout;
* queue priority.

---

# 153. Model Capacity Planning

Capacity planning should consider:

* Businesses;
* Branches;
* Products;
* inference frequency;
* model size;
* batch frequency;
* training frequency.

The system should scale AI independently from core ERP where required.

---

# 154. Model Cost Optimization

Optimization priorities:

1. avoid unnecessary inference;
2. cache reusable results;
3. batch where appropriate;
4. use lightweight models where sufficient;
5. limit expensive LLM calls;
6. scale resources according to actual demand.

---

# 155. Model Security and Supply Chain

Production model dependencies should be scanned and controlled.

Model artifacts must not be loaded from arbitrary untrusted sources.

---

# 156. Model Input Validation

Before inference:

* required features must exist;
* types must match;
* ranges must be valid;
* scope must match;
* feature versions must match;
* freshness must satisfy requirements.

Invalid input must fail safely.

---

# 157. Model Output Validation

After inference:

* output schema must be valid;
* numeric values must be finite;
* ranges must be valid;
* scope must match;
* confidence must be valid where applicable;
* model version must be attached.

---

# 158. Invalid Model Output

If a model produces invalid output:

```text
Model
 ↓
Output Validation
 ↓
Invalid
 ↓
Reject
```

The invalid output must not become an ERP fact.

---

# 159. Model and Audit

Important model lifecycle events should be auditable.

Examples:

* model activation;
* deployment;
* rollback;
* threshold change;
* approval;
* retirement.

Prediction generation itself should retain provenance appropriate to the use case.

---

# 160. Model Architecture and Offline Operation

Offline ERP operations must not depend on cloud AI models.

Offline AI, if introduced later, must be explicitly designed and must not bypass:

* authorization;
* subscription;
* Business scope;
* synchronization rules.

---

# 161. Local Model Use

Small local models may be introduced for:

* local classification;
* limited offline assistance;
* low-latency UI features.

Local model output remains non-authoritative.

---

# 162. Server Model Authority

When local and server model outputs differ:

```text
Server AI Result
```

is authoritative for the server-side AI result.

The conflict must not modify ERP transaction state automatically.

---

# 163. Model Strategy and Documentation-First Architecture

Every production model must have corresponding architecture documentation before production activation.

At minimum:

* model purpose;
* input;
* output;
* feature dependencies;
* evaluation;
* deployment;
* rollback;
* limitations.

---

# 164. Model Change Management

Model changes should follow:

```text
Requirement
 ↓
Model Design
 ↓
Feature Compatibility
 ↓
Training
 ↓
Evaluation
 ↓
Validation
 ↓
Approval
 ↓
Deployment
 ↓
Monitoring
```

---

# 165. Model Change Rollback

If deployment causes unacceptable behavior:

```text
Current Model
      ↓
Incident
      ↓
Rollback
      ↓
Previous Validated Model
      ↓
Investigation
```

Rollback should be operationally simple.

---

# 166. Model Architecture Anti-Patterns

The following are prohibited:

### 166.1. AI as ERP Authority

```text
AI
 ↓
Direct DB Update
```

### 166.2. Model as Permission Engine

```text
LLM
 ↓
Permission Decision
```

### 166.3. Training on Future Data

```text
Future
 ↓
Past Prediction
```

### 166.4. Silent Model Replacement

```text
v1
 ↓
overwrite
 ↓
v2
```

### 166.5. AI Blocking POS

```text
AI unavailable
 ↓
POS unavailable
```

These patterns violate the architecture.

---

# 167. Recommended Model Architecture

The preferred architecture is:

```text
                 ┌──────────────────────┐
                 │   Authoritative ERP  │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │   AI Data Layer      │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │ Feature Engineering  │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │    Model Registry    │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │    Model Runtime     │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │ Output Validation    │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │    AI Result         │
                 └──────────┬───────────┘
                            ↓
                 ┌──────────────────────┐
                 │ ERP / Frontend       │
                 └──────────────────────┘
```

---

# 168. Model Strategy Summary

The initial FastFood ERP AI strategy is:

1. Start with reliable baselines.
2. Prefer classical/statistical models where sufficient.
3. Use ML where measurable benefit exists.
4. Use LLMs primarily for language interaction and explanation.
5. Keep model responsibilities narrow.
6. Version every production model.
7. Version model dependencies.
8. Validate training/serving compatibility.
9. Preserve prediction provenance.
10. Make rollback easy.
11. Keep AI isolated from ERP transactions.
12. Respect Business and Branch boundaries.
13. Treat AI outputs as derived information.
14. Never allow model failure to stop core ERP.
15. Increase model complexity only when justified by measurable value.

---

# 169. System Invariants

The following invariants apply to AI Model Architecture and Model Strategy:

1. ERP remains the authoritative business system.
2. AI models are derived systems.
3. Models cannot directly become ERP authority.
4. Models cannot bypass ERP authorization.
5. Models cannot directly modify authoritative ERP state.
6. Every production model has a stable identity.
7. Every production model has an immutable version.
8. Model artifacts are immutable after activation.
9. Model input contracts are explicit.
10. Model output contracts are explicit.
11. Feature dependencies are versioned.
12. Model-feature compatibility is validated.
13. Training and serving semantics must remain compatible.
14. Future-data leakage is prohibited.
15. Training datasets must preserve point-in-time correctness.
16. Baselines should exist for important predictive use cases.
17. Complex models must demonstrate meaningful benefit.
18. Model selection considers business value, not only technical metrics.
19. Forecast horizons are explicit.
20. Model outputs are clearly identified as predictions.
21. Recommendations are not automatically ERP actions.
22. Anomaly scores do not automatically mean misconduct.
23. Correlation must not automatically be presented as causation.
24. Model confidence must not be misrepresented as certainty.
25. High-risk models cannot independently execute irreversible actions.
26. Model activation requires validation and approval.
27. Model rollback must be possible.
28. Model deployment must be observable.
29. Model lifecycle changes are auditable.
30. Historical model references remain reconstructable.
31. Prediction provenance must be retained where required.
32. Prediction results must retain model version.
33. Prediction results must retain feature version.
34. Stale predictions must be identifiable.
35. Model freshness requirements are use-case specific.
36. Model failure must not block core ERP.
37. Model timeout must not rollback unrelated ERP transactions.
38. AI workloads must not exhaust ERP resources.
39. AI workers must be isolated from critical ERP workers where necessary.
40. Expensive AI workloads must use controlled queues or batch processing where appropriate.
41. Model retries must be bounded.
42. Model jobs must be idempotent where retries are possible.
43. Invalid model output must be rejected.
44. NaN and Infinity must not become production AI results.
45. Model input validation is mandatory.
46. Model output validation is mandatory.
47. Business scope is mandatory for tenant-specific inference.
48. Branch scope is mandatory for Branch-specific inference.
49. A model must not infer authorization from natural-language input.
50. Subscription entitlement must be enforced before model access.
51. Offline operation cannot bypass model authorization.
52. Local AI output is non-authoritative.
53. Server AI results remain authoritative within the AI result layer.
54. Shared models must not expose Business data.
55. Business-specific training must preserve tenant isolation.
56. Personal data must be minimized.
57. External model providers receive only approved data.
58. External provider failure must not stop ERP.
59. Model dependencies must be controlled.
60. Model artifacts must be integrity-checked.
61. Model runtime compatibility must be validated.
62. Model resource requirements must be documented.
63. Model capacity must be monitored.
64. Model cost must be observable where material.
65. Model thresholds must be versioned when behavior changes.
66. Model configuration changes must be controlled.
67. Model evaluation must include business-relevant metrics.
68. Model candidates must be compared with production baselines.
69. Production model changes must be controlled.
70. Shadow/canary deployment should be used where justified.
71. Model retirement must preserve historical references.
72. Feature removal must consider model dependencies.
73. Model retraining does not automatically imply deployment.
74. Drift detection does not automatically trigger production activation.
75. New Businesses may return insufficient-data state.
76. New Products may use approved hierarchical fallback strategies.
77. New Branches may use shared or Business-level models when appropriate.
78. AI model complexity must remain justified by business value.
79. AI inference must not silently invent missing business data.
80. Model fallback behavior must be explicit.
81. Fallback model usage must be identifiable.
82. Model explanations must not invent unsupported causal claims.
83. Feature attribution is explanatory, not automatically causal.
84. Model outputs remain separate from ERP facts.
85. AI results must preserve historical integrity.
86. Model changes must not rewrite ERP history.
87. Model predictions must not rewrite historical transactions.
88. AI model architecture must remain independently scalable.
89. AI service degradation must not reduce ERP correctness.
90. The model layer must remain replaceable without redesigning the authoritative ERP.

---

# 170. Related Documents

## AI

* `docs/04_Architecture/08_AI/01_AI_Architecture_Overview.md`
* `docs/04_Architecture/08_AI/02_AI_Use_Cases_and_Capabilities.md`
* `docs/04_Architecture/08_AI/03_AI_Boundaries_and_Non_AI_Decisions.md`
* `docs/04_Architecture/08_AI/04_AI_Data_Architecture.md`
* `docs/04_Architecture/08_AI/05_AI_Data_Preparation_and_Feature_Engineering.md`
* `docs/04_Architecture/08_AI/07_AI_Training_and_Evaluation_Architecture.md`
* `docs/04_Architecture/08_AI/08_AI_Inference_and_Serving_Architecture.md`
* `docs/04_Architecture/08_AI/09_AI_Forecasting_and_Prediction_Architecture.md`
* `docs/04_Architecture/08_AI/10_AI_Anomaly_Detection_Architecture.md`
* `docs/04_Architecture/08_AI/11_AI_LLM_and_Natural_Language_Architecture.md`
* `docs/04_Architecture/08_AI/12_AI_Prompt_Context_and_Guardrails.md`
* `docs/04_Architecture/08_AI/13_AI_Recommendation_Architecture.md`
* `docs/04_Architecture/08_AI/14_AI_Model_Monitoring_and_Drift_Architecture.md`
* `docs/04_Architecture/08_AI/16_AI_Feature_and_Model_Registry.md`
* `docs/04_Architecture/08_AI/17_AI_Job_and_Pipeline_Architecture.md`
* `docs/04_Architecture/08_AI/19_AI_Output_Validation_and_Confidence.md`
* `docs/04_Architecture/08_AI/20_AI_Explainability_and_Interpretability.md`
* `docs/04_Architecture/08_AI/21_AI_Security_and_Data_Privacy.md`
* `docs/04_Architecture/08_AI/22_AI_Governance_and_Human_Approval.md`
* `docs/04_Architecture/08_AI/24_AI_Cost_and_Resource_Management.md`
* `docs/04_Architecture/08_AI/25_AI_Failure_Recovery_and_Resilience.md`
* `docs/04_Architecture/08_AI/26_AI_Deployment_and_Runtime_Architecture.md`
* `docs/04_Architecture/08_AI/27_AI_Testing_and_Quality_Assurance.md`
* `docs/04_Architecture/08_AI/28_AI_Operations_and_Observability.md`

## Backend

* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

## Database

* `docs/04_Architecture/07_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/04_Architecture/07_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/07_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/07_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/04_Architecture/07_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/04_Architecture/07_Database/30_Database_Invariants_and_Guardrails.md`

## Frontend

* `docs/04_Architecture/05_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/05_Frontend/16_Reports_and_Dashboard_UI.md`
* `docs/04_Architecture/05_Frontend/17_Notifications_and_Alerts_UI.md`
* `docs/04_Architecture/05_Frontend/20_Offline_Mode_and_Synchronization_UI.md`

---

# 171. Status

**AI Architecture Sequence:** Frozen at 28 documents.

**Completed AI Documents:** 01–06.

**Current Document:** `06_AI_Model_Architecture_and_Model_Strategy.md`

**Document Status:** Proposed v1.0

**Next Document:** `07_AI_Training_and_Evaluation_Architecture.md`

