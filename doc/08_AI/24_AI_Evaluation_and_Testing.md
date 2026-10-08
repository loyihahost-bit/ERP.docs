# AI Evaluation and Testing

**Document ID:** AI-24
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_AI/README.md`

---

## 1. Purpose

This document defines the architecture for evaluating and testing AI capabilities in FastFood ERP.

The objective is to ensure that AI functionality is:

* technically reliable;
* statistically meaningful;
* reproducible where possible;
* safe for production;
* compatible with ERP business rules;
* isolated by Business and Branch;
* resistant to regressions;
* observable after deployment;
* suitable for human approval where required.

AI testing must not be limited to checking whether a model executes successfully.

The system must verify:

```text
Data
  ↓
Features
  ↓
Model
  ↓
Inference
  ↓
Output
  ↓
Business Interpretation
  ↓
Governance
  ↓
ERP Integration
```

---

# 2. Scope

This document covers:

* AI unit testing;
* data validation;
* feature validation;
* model evaluation;
* offline evaluation;
* online evaluation;
* regression testing;
* integration testing;
* API testing;
* inference testing;
* LLM testing;
* prompt testing;
* guardrail testing;
* security testing;
* adversarial testing;
* Business/Branch isolation testing;
* performance testing;
* load testing;
* reliability testing;
* drift evaluation;
* recommendation evaluation;
* anomaly detection evaluation;
* forecasting evaluation;
* human evaluation;
* governance evaluation;
* production monitoring;
* release gates;
* rollback criteria;
* test datasets;
* evaluation datasets;
* experiment lineage.

---

# 3. Core Principle

AI functionality must pass both:

1. **Technical correctness**
2. **Business safety and usefulness**

A model that produces technically valid output but violates ERP rules is not production-ready.

Likewise, a model with good statistical metrics is not automatically safe for production.

---

# 4. Testing Layers

AI testing is divided into the following layers:

```text
Layer 1  Data Validation
Layer 2  Feature Validation
Layer 3  Model Validation
Layer 4  Inference Validation
Layer 5  Business Rule Validation
Layer 6  API / Integration Validation
Layer 7  Security Validation
Layer 8  Governance Validation
Layer 9  Performance Validation
Layer 10 Production Evaluation
```

Each layer has a separate responsibility.

---

# 5. Test Pyramid

The AI test strategy follows:

```text
              Production Evaluation
                    ↑
             End-to-End Tests
                    ↑
          Integration / API Tests
                    ↑
          Model / Inference Tests
                    ↑
          Feature / Data Tests
                    ↑
               Unit Tests
```

Large expensive tests should not replace lower-level deterministic tests.

---

# 6. Test Environment Separation

AI evaluation environments should be separated:

* Development;
* Testing;
* Evaluation;
* Staging;
* Production.

Production data must not automatically become available to development or testing environments.

Sensitive production data requires controlled access and appropriate anonymization or aggregation.

---

# 7. Dataset Types

The AI architecture should distinguish:

### Training Dataset

Used to train models.

### Validation Dataset

Used during model development and tuning.

### Test Dataset

Used for final evaluation.

### Regression Dataset

Used to detect degradation between model versions.

### Golden Dataset

Stable examples with expected behavior.

### Adversarial Dataset

Designed to expose unsafe or incorrect behavior.

### Production Evaluation Dataset

Representative approved production samples.

These datasets must not be confused with each other.

---

# 8. Dataset Versioning

Every important evaluation dataset must have:

* Dataset UUID;
* Dataset version;
* creation timestamp;
* source;
* feature version;
* transformation version;
* schema version;
* sampling method;
* creator;
* validation status.

Historical evaluation must remain linked to the exact dataset version.

---

# 9. Dataset Leakage Prevention

Evaluation data must not unintentionally leak into training.

The system should detect:

* duplicate records;
* overlapping identifiers;
* temporal leakage;
* future information;
* derived target leakage;
* feature leakage.

A model with evaluation leakage must not be treated as reliably evaluated.

---

# 10. Temporal Evaluation

For time-dependent ERP predictions, temporal splits should be preferred.

Example:

```text
Historical Period
      ↓
Training

Later Period
      ↓
Validation

Future Period
      ↓
Test
```

This better represents real production conditions.

---

# 11. Business Isolation Testing

AI tests must verify tenant isolation.

Example:

```text
Business A Data
      ↓
AI Request
      ↓
Business A Result
```

The result must never include Business B information.

Cross-Business leakage tests are mandatory for production AI capabilities.

---

# 12. Branch Isolation Testing

Branch-scoped AI functionality must be tested against:

* correct Branch;
* wrong Branch;
* multiple authorized Branches;
* unauthorized Branch;
* Branch switching;
* stale Branch context.

A Branch-scoped model or feature must not silently use another Branch's data.

---

# 13. Authorization Testing

AI endpoints and capabilities must verify:

* authentication;
* employee status;
* role;
* permission;
* Branch scope;
* Business scope;
* subscription entitlement;
* governance requirements.

AI output must never grant additional authority.

---

# 14. Model Unit Tests

Model-related deterministic logic should be unit tested.

Examples:

* input preprocessing;
* normalization;
* feature transformation;
* output parsing;
* threshold calculation;
* confidence calculation;
* post-processing;
* schema conversion.

Model weights themselves are evaluated through model evaluation rather than ordinary unit tests.

---

# 15. Feature Tests

Every production feature transformation should have tests for:

* expected values;
* missing values;
* null handling;
* zero values;
* negative values where invalid;
* boundary values;
* unit consistency;
* time windows;
* Branch scope;
* Business scope.

---

# 16. Feature Reproducibility

The same feature version and same source state should produce the same feature result where deterministic behavior is expected.

Unexpected variation must be detectable.

---

# 17. Data Quality Gates

Before model evaluation, data quality checks should validate:

* completeness;
* validity;
* consistency;
* uniqueness;
* freshness;
* schema;
* range;
* distribution.

A failed data-quality gate should prevent unreliable model evaluation from being promoted.

---

# 18. Forecasting Evaluation

Demand forecasting models should be evaluated using appropriate metrics.

Possible metrics include:

* MAE;
* RMSE;
* MAPE where appropriate;
* WAPE;
* bias;
* forecast error distribution.

Metric selection must reflect the business use case.

---

# 19. Forecasting Business Evaluation

A forecasting model should also be evaluated against operational outcomes.

Examples:

* stock-out reduction;
* overstock reduction;
* purchasing efficiency;
* forecast stability;
* seasonal performance.

A lower mathematical error does not automatically mean better business performance.

---

# 20. Inventory Intelligence Evaluation

Inventory AI should be evaluated for:

* stock-out prediction;
* demand estimation;
* purchasing recommendations;
* abnormal consumption;
* inventory variance signals.

False positives and false negatives should be tracked separately.

---

# 21. Anomaly Detection Evaluation

Anomaly detection should consider:

* precision;
* recall;
* false positive rate;
* false negative rate;
* detection delay;
* anomaly severity classification.

Where labeled data is limited, human-reviewed samples may be used for evaluation.

---

# 22. Recommendation Evaluation

Recommendations should be evaluated using:

* recommendation accuracy;
* relevance;
* acceptance rate;
* rejection rate;
* business outcome;
* stale recommendation rate.

Acceptance rate alone must not be interpreted as model quality.

---

# 23. Business Impact Evaluation

Where practical, AI features should be evaluated against business outcomes.

Examples:

```text
AI Recommendation
      ↓
Human Decision
      ↓
ERP Action
      ↓
Observed Outcome
```

The evaluation should distinguish correlation from proven causation.

---

# 24. Classification Evaluation

Classification models should use appropriate metrics such as:

* accuracy;
* precision;
* recall;
* F1;
* specificity;
* ROC-AUC;
* PR-AUC.

For imbalanced business events, accuracy must not be used as the only metric.

---

# 25. Threshold Evaluation

Classification thresholds must be evaluated separately from model quality.

Changing a threshold may change:

* false positives;
* false negatives;
* operational workload;
* business risk.

Threshold configuration must be versioned.

---

# 26. Confidence Evaluation

Confidence scores should be evaluated for:

* calibration;
* stability;
* distribution;
* relationship with actual correctness.

High confidence must not be assumed to mean correctness.

---

# 27. Calibration Testing

Where confidence is exposed to users or governance logic, calibration should be evaluated.

For example:

```text
Predicted confidence ≈ observed correctness
```

Poorly calibrated confidence should not be used as the sole decision criterion.

---

# 28. Model Robustness

Models should be tested against:

* missing data;
* noisy data;
* unusual values;
* seasonal changes;
* distribution changes;
* partial data;
* stale data;
* unexpected categories.

The system must fail safely when required input conditions are not satisfied.

---

# 29. Boundary Testing

AI inputs should be tested at:

* minimum valid value;
* maximum valid value;
* zero;
* empty;
* null;
* invalid type;
* invalid range.

No input should produce:

* NaN;
* Infinity;
* malformed output;
* undefined business state.

---

# 30. Output Schema Testing

AI outputs must conform to the expected schema.

Tests should validate:

* required fields;
* types;
* ranges;
* enum values;
* identifiers;
* timestamps;
* confidence;
* model metadata.

Invalid model output must be rejected before entering authoritative application logic.

---

# 31. Inference Contract Testing

Inference requests should have contract tests between:

```text
Application
→ AI Runtime
→ Model
→ Output Validator
```

Model version changes must not silently break the application contract.

---

# 32. Model Compatibility Testing

Before deployment, verify compatibility between:

* model version;
* feature version;
* input schema;
* output schema;
* runtime;
* dependency versions;
* deployment environment.

Incompatible models must fail the release gate.

---

# 33. Model Regression Testing

Every new production model must be compared with the previous approved model.

The comparison should include:

* core metrics;
* business metrics;
* critical slices;
* latency;
* resource usage;
* failure rate;
* output distribution.

A new model must not be accepted merely because one aggregate metric improved.

---

# 34. Champion vs Challenger

The current production model is the **Champion**.

A candidate model is the **Challenger**.

Evaluation should compare:

```text
Champion
   ↕
Challenger
```

The challenger becomes production only after passing the required gates.

---

# 35. Slice-Based Evaluation

Model performance should be evaluated across meaningful segments.

Examples:

* Branch;
* product category;
* day of week;
* time of day;
* high-volume vs low-volume periods;
* seasonal period.

A strong aggregate score must not hide severe degradation in an important segment.

---

# 36. Small-Data Branches

Branches with insufficient data must be handled explicitly.

The system may:

* use shared model;
* use Business-level model;
* use fallback model;
* use deterministic business rules.

A branch must not receive an unreliable custom model merely because it has its own data scope.

---

# 37. Cold-Start Evaluation

AI features must define behavior when:

* Business has no historical data;
* Branch is new;
* Product is new;
* category is new;
* insufficient observations exist.

Cold-start behavior must be tested separately.

---

# 38. Missing Data Evaluation

Models must be tested when expected data is missing.

Possible behavior:

* fallback;
* partial prediction;
* request for more data;
* safe rejection.

The system must not silently fabricate missing ERP data.

---

# 39. Stale Data Evaluation

AI inputs should include freshness requirements where relevant.

Tests must verify behavior when data is:

* current;
* slightly stale;
* outside acceptable freshness;
* unavailable.

---

# 40. LLM Evaluation

LLM functionality requires evaluation beyond traditional ML metrics.

Testing should include:

* factual correctness;
* instruction following;
* scope adherence;
* data privacy;
* hallucination;
* tool usage;
* refusal behavior;
* structured output;
* consistency;
* prompt injection resistance.

---

# 41. Prompt Regression Testing

Every important prompt version should be tested against a golden dataset.

Example:

```text
Prompt V1
   ↓
Golden Dataset
   ↓
Expected Behavior

Prompt V2
   ↓
Same Dataset
   ↓
Compare
```

Prompt changes must not silently degrade critical behavior.

---

# 42. Prompt Golden Dataset

Golden prompts should represent:

* normal user requests;
* ambiguous requests;
* edge cases;
* authorization-sensitive requests;
* Business/Branch scope;
* sensitive-data requests;
* invalid requests;
* expected refusals.

---

# 43. Prompt Injection Testing

LLM systems must be tested against:

* direct prompt injection;
* indirect prompt injection;
* malicious product descriptions;
* malicious uploaded documents;
* malicious retrieved content;
* tool manipulation;
* instruction hierarchy attacks.

The expected result is safe rejection or controlled behavior.

---

# 44. Tool-Use Testing

AI tool use must be tested for:

* correct tool selection;
* correct parameters;
* authorization;
* invalid parameters;
* unauthorized tools;
* repeated calls;
* recursive calls;
* tool failure;
* tool timeout.

The model must not gain authority through tool selection.

---

# 45. Tool Boundary Testing

Tests must verify that the LLM cannot:

* bypass API authorization;
* access raw database tables;
* access another Business;
* change restricted configuration;
* execute unauthorized financial operations.

---

# 46. Structured Output Testing

LLM structured outputs should be validated against schemas.

Invalid responses should trigger:

* rejection;
* retry where safe;
* fallback;
* user-facing explanation.

---

# 47. Hallucination Testing

LLM responses should be evaluated for unsupported claims.

Examples:

* invented sales;
* invented stock;
* invented employees;
* invented prices;
* invented reports;
* invented ERP transactions.

The assistant must distinguish:

```text
Known ERP Fact
Prediction
Recommendation
Unknown
```

---

# 48. Numerical Accuracy Testing

AI-generated numbers must be validated when derived from ERP data.

For example:

```text
ERP Revenue = 100,000
AI Response = 100,000
```

The application should validate authoritative numbers rather than trusting generated text.

---

# 49. AI vs ERP Fact Testing

A test must verify that current ERP values remain authoritative.

If:

```text
ERP Stock = 20
AI Prediction = 15
```

the system must not present 15 as current stock.

---

# 50. Guardrail Evaluation

Guardrails should be evaluated using:

* allowed cases;
* rejected cases;
* ambiguous cases;
* adversarial cases;
* sensitive cases.

Metrics may include:

* false allow rate;
* false block rate;
* detection rate;
* latency.

---

# 51. Guardrail False Allow

A critical security metric is:

**False Allow Rate**

This measures cases where a prohibited operation is incorrectly allowed.

For high-risk operations:

**False Allow Rate must be 0% in release-gate test suites.**

---

# 52. Guardrail False Block

False blocking should also be monitored.

Excessive false blocks reduce usability.

The target must be business-specific rather than universally fixed.

---

# 53. Governance Testing

AI governance must be tested for:

* correct classification;
* approval requirement;
* approver authorization;
* approval expiry;
* rejection;
* cancellation;
* supersession;
* revalidation;
* duplicate execution prevention.

---

# 54. Approval Testing

Tests must verify:

```text
AI Result
   ↓
Approval Required
   ↓
Unauthorized Employee
   ↓
Rejected
```

and:

```text
AI Result
   ↓
Approval Required
   ↓
Authorized Employee
   ↓
Approved
   ↓
ERP Use Case
```

---

# 55. Approval Replay Testing

An old approval must not automatically authorize a new operation.

Example:

```text
Approval V1
      ↓
Operation V1

New Operation V2
      ↓
Requires new validation
```

---

# 56. Governance Race Conditions

Concurrent approvals and execution attempts must be tested.

Examples:

* two users approve;
* approval expires during execution;
* cancellation races with execution;
* model changes after approval;
* configuration changes after approval.

The application must preserve deterministic authoritative state.

---

# 57. AI Security Testing

AI security tests should cover:

* authentication bypass;
* authorization bypass;
* tenant isolation;
* Branch isolation;
* prompt injection;
* data exfiltration;
* tool abuse;
* provider manipulation;
* malicious artifacts;
* model supply-chain risks;
* secret leakage.

---

# 58. Model Artifact Security Testing

Model artifacts must be tested for:

* checksum validity;
* trusted source;
* dependency compatibility;
* unexpected executable behavior;
* incompatible runtime requirements.

Untrusted model artifacts must not be loaded into production runtime.

---

# 59. Data Privacy Testing

Tests should verify that AI output does not expose unauthorized:

* employee information;
* customer delivery information;
* Business data;
* Branch data;
* secrets;
* internal configuration.

---

# 60. Cross-Tenant Leakage Testing

A dedicated regression suite should attempt to make AI retrieve another Business's information.

Expected result:

```text
Access Denied
```

No partial or indirect leakage is acceptable.

---

# 61. Offline AI Testing

Where offline AI is supported, test:

* offline authorization;
* stale model;
* stale configuration;
* expired authorization;
* synchronization;
* duplicate event;
* clock rollback;
* Business deletion;
* subscription expiry;
* Branch switching.

---

# 62. Offline Model Version Testing

An offline device may have Model Version A while the server uses Version B.

The system must preserve the fact that:

```text
Offline Prediction → Model A
Server Current Model → Model B
```

Synchronization must not rewrite the historical model identity.

---

# 63. Synchronization Testing

AI synchronization tests should cover:

* success;
* partial success;
* duplicate events;
* stale events;
* conflict;
* retry;
* timeout;
* invalid authorization;
* deleted Business;
* read-only Business.

---

# 64. AI API Testing

AI APIs must be tested for:

* authentication;
* authorization;
* request schema;
* response schema;
* pagination;
* filtering;
* rate limits;
* idempotency;
* timeouts;
* cancellation;
* error contracts.

---

# 65. Idempotency Testing

The same idempotency key with the same request should produce one logical operation.

The same idempotency key with different payload must be rejected.

---

# 66. API Error Testing

AI APIs should return deterministic error categories.

Examples:

```text
Validation Error
Authorization Error
Entitlement Error
Conflict
Rate Limit
Timeout
Provider Error
Model Error
Infrastructure Error
```

Internal stack traces and secrets must not be exposed.

---

# 67. Performance Testing

AI performance tests should evaluate:

* inference latency;
* model loading;
* feature retrieval;
* context assembly;
* guardrails;
* output validation;
* API latency;
* queue latency;
* worker throughput.

---

# 68. Performance Targets

Target SLOs:

| Operation                         |       Target |
| --------------------------------- | -----------: |
| Lightweight synchronous inference | p95 ≤ 500 ms |
| Standard AI API                   |  p95 ≤ 1.5 s |
| Context assembly                  | p95 ≤ 500 ms |
| Input validation                  | p95 ≤ 200 ms |
| Output validation                 | p95 ≤ 500 ms |
| Model resolution from cache       | p95 ≤ 100 ms |
| AI job creation                   | p95 ≤ 200 ms |
| Audit event retrieval             | p95 ≤ 500 ms |
| AI runtime availability           |      ≥ 99.5% |

These targets are architectural targets and may be refined after production measurement.

---

# 69. Load Testing

Load tests should simulate:

* concurrent POS users;
* multiple Branches;
* concurrent AI requests;
* scheduled AI jobs;
* model loading;
* recommendation retrieval;
* LLM requests.

AI load must not degrade critical ERP operations beyond defined ERP SLOs.

---

# 70. Resource Exhaustion Testing

Test behavior when:

* CPU is saturated;
* memory is low;
* queue is full;
* model cache is full;
* provider rate limit is reached;
* GPU is unavailable.

Expected behavior should include:

* backpressure;
* bounded retries;
* fallback;
* graceful degradation.

---

# 71. Timeout Testing

Test:

* model timeout;
* provider timeout;
* feature timeout;
* database timeout;
* queue timeout.

A timeout must not leave an ambiguous authoritative ERP transaction.

---

# 72. Retry Testing

Retries must be bounded.

Test:

* transient failure;
* repeated failure;
* retry exhaustion;
* dead-letter behavior;
* duplicate prevention.

---

# 73. Circuit Breaker Testing

Where circuit breakers are used, test:

```text
Healthy
 ↓
Failure Threshold
 ↓
Open
 ↓
Recovery Test
 ↓
Half-Open
 ↓
Healthy
```

The AI failure must not block unrelated ERP operations.

---

# 74. Fallback Testing

Fallback behavior must be explicitly tested.

Examples:

* AI unavailable → deterministic rule;
* forecast unavailable → previous approved forecast;
* recommendation unavailable → no recommendation;
* LLM unavailable → standard UI/help;
* anomaly model unavailable → monitoring continues without AI alert.

Fallback must never invent authoritative data.

---

# 75. Model Loading Testing

Model deployment tests should verify:

* artifact retrieval;
* checksum;
* dependency compatibility;
* warm-up;
* readiness;
* traffic activation;
* rollback.

A model must not receive production traffic before readiness checks pass.

---

# 76. Deployment Testing

Deployment tests should cover:

* staging deployment;
* canary;
* full deployment;
* rollback;
* configuration compatibility;
* health checks;
* model version selection.

---

# 77. Canary Evaluation

Canary releases should evaluate:

* latency;
* errors;
* output distribution;
* business metrics;
* security events;
* model-specific metrics.

Canary failure must trigger rollback or controlled disablement according to policy.

---

# 78. Shadow Evaluation

Where appropriate, a challenger model may run in shadow mode.

Its result must not affect ERP operations.

Example:

```text
Production Request
   ├── Champion → User/ERP
   └── Challenger → Evaluation Only
```

---

# 79. Production Evaluation

Production evaluation should monitor:

* model quality;
* data drift;
* prediction drift;
* latency;
* failures;
* recommendation acceptance;
* false positives;
* business outcomes.

Production monitoring must not modify authoritative ERP data automatically.

---

# 80. Drift Evaluation

The system should evaluate:

### Data Drift

Input distribution changes.

### Feature Drift

Feature behavior changes.

### Prediction Drift

Model output distribution changes.

### Concept Drift

Relationship between input and target changes.

Drift detection should generate signals, not automatically declare the model invalid without defined policy.

---

# 81. Drift Thresholds

Drift thresholds must be versioned.

The system should record:

* threshold;
* metric;
* evaluation period;
* model version;
* feature version;
* result.

---

# 82. Production Regression

Production evaluation should compare current performance with:

* previous model;
* approved baseline;
* expected business range.

Unexpected degradation should generate an alert.

---

# 83. AI Incident Testing

AI incident scenarios should be tested.

Examples:

* wrong model deployed;
* model output schema changed;
* provider outage;
* prompt regression;
* cross-Business leakage;
* excessive false positives;
* high latency;
* feature pipeline failure.

---

# 84. Rollback Testing

Rollback must be tested before production use.

The system must verify:

* previous model remains available;
* routing changes correctly;
* new model stops receiving traffic;
* historical predictions remain unchanged;
* audit records remain intact.

---

# 85. Kill Switch Testing

AI capabilities with emergency disablement must be tested.

Example:

```text
AI Capability
    ↓
Emergency Disable
    ↓
AI Stops
    ↓
Core ERP Continues
```

The kill switch must not disable POS, payment, inventory or authentication unless the specific capability itself is part of those systems.

---

# 86. Human Evaluation

Some AI outputs require human evaluation.

Human reviewers may assess:

* correctness;
* relevance;
* safety;
* clarity;
* usefulness;
* policy compliance.

Human evaluation results must be versioned and attributable.

---

# 87. Human Evaluation Dataset

Human-reviewed examples should identify:

* sample UUID;
* model version;
* prompt version where applicable;
* reviewer;
* evaluation criteria;
* score;
* timestamp.

---

# 88. Reviewer Independence

Where required by governance, the person who created a model or prompt should not be the sole approver of its production evaluation.

Segregation-of-duties rules apply.

---

# 89. Evaluation Reproducibility

Evaluation runs should preserve:

* dataset version;
* model version;
* feature version;
* prompt version;
* evaluation code version;
* configuration version;
* runtime version;
* random seed where applicable.

This allows results to be reproduced or investigated.

---

# 90. Evaluation Run Identity

Every evaluation run should have:

* Evaluation UUID;
* experiment UUID where applicable;
* model version;
* dataset version;
* start time;
* completion time;
* status;
* metrics.

---

# 91. Evaluation Run States

Suggested lifecycle:

```text
CREATED
  ↓
QUEUED
  ↓
RUNNING
  ↓
COMPLETED
```

Alternative terminal states:

```text
FAILED
CANCELLED
INVALIDATED
```

Completed evaluation results must remain immutable.

---

# 92. Evaluation Result Immutability

Once an evaluation is completed, its result must not be silently changed.

If a correction is required:

```text
Evaluation V1
    ↓
Correction / Re-evaluation
    ↓
Evaluation V2
```

---

# 93. Evaluation Approval

Production deployment should require an approved evaluation result.

The approval must identify:

* evaluator;
* evaluation run;
* model version;
* policy;
* decision;
* timestamp.

---

# 94. Release Gate

A production AI model must pass all required gates:

```text
Data Quality
      ↓
Feature Validation
      ↓
Model Evaluation
      ↓
Regression Evaluation
      ↓
Security Testing
      ↓
Governance Review
      ↓
Performance Testing
      ↓
Approval
      ↓
Deployment
```

---

# 95. Release Gate Failure

A failed gate must prevent production deployment unless an explicitly authorized exception process exists.

Exceptions must be:

* documented;
* approved;
* time-bounded;
* auditable;
* risk-assessed.

---

# 96. Critical Release Gates

The following are mandatory for production:

* Business isolation;
* Branch authorization;
* output schema;
* model compatibility;
* security validation;
* governance validation;
* required regression tests;
* required performance tests.

---

# 97. High-Risk AI Release

High-risk AI capabilities require stronger validation.

Examples:

* financial recommendations;
* inventory adjustments;
* payroll-related intelligence;
* security decisions;
* pricing recommendations.

Where the AI result can influence a high-risk ERP operation, governance approval must be satisfied.

---

# 98. Prohibited Autonomous Action Testing

The test suite must explicitly verify that AI cannot autonomously:

* delete a Business;
* modify permissions;
* deactivate employees;
* execute refunds;
* change payroll;
* adjust inventory;
* publish prices;
* approve recipes;
* modify subscription state;
* change security policy.

These tests must be release-blocking.

---

# 99. Negative Testing

AI testing must include prohibited scenarios.

Examples:

```text
Unauthorized Request
→ Reject

Wrong Branch
→ Reject

Wrong Business
→ Reject

Expired Subscription
→ Reject

Expired Approval
→ Reject

Invalid Model
→ Reject

Invalid Output
→ Reject
```

---

# 100. Chaos Testing

Where appropriate, AI infrastructure may be tested under controlled failures:

* worker termination;
* provider outage;
* queue interruption;
* model cache loss;
* database connection loss;
* network delay;
* partial synchronization.

Core ERP continuity must remain intact.

---

# 101. Recovery Testing

After failure, test:

* retry;
* recovery;
* duplicate prevention;
* state reconstruction;
* audit integrity;
* model availability;
* queue recovery.

---

# 102. Backup and Restore Testing

AI metadata and required historical lineage must be included in backup/restore validation.

Restore tests must verify:

* model metadata;
* evaluation history;
* audit history;
* governance history;
* lineage references.

Large model artifacts may use separate artifact backup procedures.

---

# 103. Security Regression

Security AI tests should run continuously for important releases.

Examples:

* prompt injection;
* authorization bypass;
* cross-tenant leakage;
* sensitive data leakage;
* tool abuse;
* malformed model artifact.

---

# 104. Dependency Regression

AI runtime dependencies must be tested for compatibility.

Changes to:

* Python packages;
* model runtime;
* inference engine;
* tokenizer;
* provider SDK;
* system libraries

must not be deployed without compatibility validation.

---

# 105. Model Supply Chain Testing

The system should validate:

* artifact checksum;
* trusted source;
* model version;
* dependency versions;
* provenance.

Unknown or modified artifacts must fail validation.

---

# 106. LLM Provider Regression

When an external LLM provider changes:

* provider adapter tests;
* golden prompt tests;
* structured output tests;
* safety tests;
* latency tests

must be re-evaluated where relevant.

The application must not assume provider behavior remains unchanged.

---

# 107. Token and Cost Evaluation

LLM evaluation may include:

* token usage;
* response length;
* latency;
* provider cost;
* retry rate.

Cost regressions should be detected before large-scale production rollout.

---

# 108. AI Evaluation Metrics Registry

Evaluation metrics should be defined centrally.

Each metric should have:

* metric UUID;
* name;
* definition;
* calculation method;
* applicable AI capability;
* version;
* threshold where applicable.

Metric definition changes must be versioned.

---

# 109. Metric Comparability

Two evaluation results must not be compared as equivalent if:

* metric definitions differ;
* datasets differ materially;
* target definitions differ;
* evaluation windows differ.

The system should preserve the context needed for correct comparison.

---

# 110. Evaluation Thresholds

Thresholds should be explicit.

Example:

```text
Metric
Required Threshold
Observed Value
Pass/Fail
```

A threshold change must be audited and versioned.

---

# 111. Evaluation Reports

Evaluation reports should contain:

* evaluation UUID;
* model version;
* dataset version;
* metrics;
* thresholds;
* pass/fail;
* evaluator;
* runtime;
* environment;
* timestamp;
* known limitations.

---

# 112. Evaluation Report Immutability

Approved evaluation reports must remain immutable.

Corrections create a new version or correction record.

---

# 113. Evaluation Limitations

Every production AI evaluation should document relevant limitations.

Examples:

* insufficient data;
* cold-start;
* seasonal coverage;
* missing labels;
* external provider variability;
* limited Branch coverage.

The system must not present incomplete evaluation as universal proof of quality.

---

# 114. Test Data Privacy

Test and evaluation data must follow privacy requirements.

Possible controls:

* anonymization;
* pseudonymization;
* aggregation;
* masking;
* synthetic data.

Production-sensitive data must not be copied unnecessarily.

---

# 115. Synthetic Data

Synthetic data may be used for:

* edge cases;
* rare events;
* security testing;
* load testing;
* privacy-safe development.

Synthetic data must be clearly identified and must not be mistaken for production observations.

---

# 116. Test Data Isolation

Test datasets must not accidentally enter production.

Dataset environment metadata should identify:

* DEVELOPMENT;
* TEST;
* EVALUATION;
* STAGING;
* PRODUCTION.

---

# 117. Test Automation

Where practical, AI tests should run automatically in CI/CD.

Automatic gates should include:

* schema;
* unit;
* integration;
* security;
* regression;
* performance smoke tests.

Expensive model evaluations may run asynchronously before release approval.

---

# 118. CI/CD AI Gate

A production deployment should not proceed if mandatory automated AI gates fail.

Example:

```text
Code Change
    ↓
Automated Tests
    ↓
AI Regression
    ↓
Security Tests
    ↓
Evaluation
    ↓
Approval
    ↓
Deploy
```

---

# 119. Test Flakiness

AI tests may be nondeterministic.

The system should distinguish:

* deterministic failure;
* expected stochastic variation;
* infrastructure failure;
* provider variation.

Retries must not hide genuine regressions.

---

# 120. Statistical Significance

Where model comparison depends on statistical inference, the evaluation should consider:

* sample size;
* confidence interval;
* variance;
* practical significance.

A tiny statistically significant improvement may not justify operational risk.

---

# 121. Business Significance

Evaluation must consider whether improvement is meaningful for the business.

Example:

```text
Metric Improvement = 0.2%
Operational Cost = significantly higher
```

The model should not automatically be preferred.

---

# 122. Evaluation by Business Risk

Evaluation strictness should increase with potential business impact.

```text
Low Risk
→ Standard Evaluation

Medium Risk
→ Extended Evaluation

High Risk
→ Extended + Human Review + Governance Approval

Prohibited
→ Must Not Deploy
```

---

# 123. Evaluation and Human Approval

Evaluation approval is separate from business transaction approval.

A model can be approved for production without being authorized to perform a specific ERP action.

---

# 124. Evaluation and Model Registry

Only model versions that pass required evaluation should become eligible for production deployment.

The Model Registry should reference:

* evaluation UUID;
* approval;
* deployment status.

---

# 125. Evaluation and Prompt Registry

Prompt versions used by production LLM capabilities should reference relevant evaluation results.

A prompt change may require re-evaluation even when the underlying model is unchanged.

---

# 126. Evaluation and Governance Registry

Governance policies should define which evaluation level is required for each AI capability.

Example:

```text
Informational
→ Standard

Advisory
→ Standard + Safety

High-Risk
→ Extended + Human Review

Prohibited
→ No Production Deployment
```

---

# 127. Evaluation and Audit

Evaluation events must integrate with AI Audit.

The system should preserve:

```text
Evaluation
→ Approval
→ Deployment
→ Production Result
```

This provides model lifecycle traceability.

---

# 128. Evaluation and Incident Response

If production monitoring discovers a severe issue:

1. identify affected model;
2. identify deployment;
3. identify evaluation;
4. identify affected predictions;
5. assess business impact;
6. disable or rollback if required;
7. create incident record;
8. re-evaluate model.

---

# 129. Model Retirement Trigger

A model may require retirement when:

* performance degrades;
* drift exceeds threshold;
* security issue discovered;
* dependency becomes unsupported;
* business requirement changes;
* better approved model replaces it.

Retirement must not remove historical evaluation records.

---

# 130. Evaluation History Retention

Evaluation history should generally be retained longer than temporary technical logs.

Production model evaluations must remain available for the period required to reconstruct why a model was deployed.

---

# 131. Evaluation Storage

Evaluation metadata may be stored in PostgreSQL.

Large artifacts such as:

* confusion matrices;
* large datasets;
* model evaluation files;
* plots;
* notebooks;
* reports

should use appropriate artifact storage.

---

# 132. Evaluation Artifact Integrity

Evaluation artifacts should have:

* artifact reference;
* checksum;
* version;
* creation timestamp.

Modified artifacts must be detectable.

---

# 133. Evaluation Access

Evaluation results may be restricted according to:

* Business;
* Branch;
* AI permissions;
* model management permissions;
* governance permissions.

Sensitive evaluation information must not be universally visible.

---

# 134. Evaluation API

Evaluation APIs should support:

* create evaluation;
* start evaluation;
* retrieve status;
* retrieve metrics;
* compare models;
* approve evaluation;
* reject evaluation;
* retrieve report.

Long-running evaluations must use asynchronous jobs.

---

# 135. Evaluation API Performance

Target:

* evaluation creation p95 ≤200 ms;
* evaluation status p95 ≤200 ms;
* evaluation metadata retrieval p95 ≤500 ms;
* evaluation comparison p95 ≤1 s for normal comparison sizes.

Large reports remain asynchronous.

---

# 136. Evaluation Job Management

Long-running evaluations should support:

* queue;
* progress;
* retry;
* cancellation;
* timeout;
* dead-letter;
* resource limits.

Cancellation must not leave an evaluation incorrectly marked as completed.

---

# 137. Evaluation Resource Limits

Evaluation jobs must have limits for:

* CPU;
* memory;
* GPU;
* runtime;
* dataset size;
* concurrency.

One evaluation must not starve production AI inference.

---

# 138. Production Isolation

Evaluation workloads must not consume resources required for critical production AI or ERP operations.

Priority should generally be:

```text
Core ERP
   ↓
Production AI
   ↓
Operational AI Jobs
   ↓
Evaluation
   ↓
Experiments
```

---

# 139. Test Environment Hardware

The AI architecture should support CPU-first evaluation where practical.

GPU usage should be introduced when justified by:

* model size;
* training requirements;
* evaluation time;
* business value.

The system should not require expensive hardware for ordinary ERP operation.

---

# 140. Testability Principle

Every AI capability must expose enough controlled boundaries to allow testing.

Examples:

* deterministic input;
* model version selection;
* feature version selection;
* configuration version;
* mock provider;
* mock inference;
* test Business;
* test Branch;
* controlled clock;
* controlled authorization context.

---

# 141. External Provider Mocking

Tests must be able to run without depending on external AI providers.

Provider adapters should support test doubles or mocked responses.

This prevents:

* unstable tests;
* unnecessary cost;
* external outages affecting CI;
* accidental production calls.

---

# 142. No Real Secrets in Tests

Test environments must never require production:

* API keys;
* database credentials;
* authentication secrets;
* encryption keys.

Secrets must be supplied through secure environment mechanisms where required.

---

# 143. AI Evaluation Invariants

The following invariants apply:

1. Production AI models must pass required evaluation gates.
2. Evaluation results are versioned.
3. Completed evaluations are immutable.
4. Evaluation datasets are versioned.
5. Model versions are immutable.
6. Feature versions are identifiable.
7. Prompt versions are identifiable where applicable.
8. Evaluation runs have unique identities.
9. Training data must not leak into test data unintentionally.
10. Temporal leakage must be detected for time-dependent models.
11. Business isolation is mandatory.
12. Branch isolation is mandatory where Branch scope applies.
13. Authorization must be tested independently of model behavior.
14. AI output cannot grant authorization.
15. Invalid output must not enter authoritative ERP logic.
16. Historical evaluation must not depend on current model configuration.
17. Regression testing is required for production model changes.
18. Champion/challenger comparisons preserve both model identities.
19. Slice-based evaluation is required where meaningful.
20. Aggregate metrics must not hide critical segment failures.
21. Cold-start behavior must be explicitly evaluated.
22. Missing-data behavior must be explicitly evaluated.
23. Stale-data behavior must be explicitly evaluated.
24. Confidence must not be treated as authority.
25. Thresholds are versioned.
26. LLM prompts require regression testing.
27. Prompt injection testing is required for governed LLM capabilities.
28. Tool authorization must be tested.
29. Structured LLM output must be schema-validated.
30. Hallucinated ERP facts must be detected.
31. Numerical AI outputs must be validated where authoritative values exist.
32. Guardrail false-allow behavior must be tested.
33. High-risk prohibited actions must have release-blocking negative tests.
34. Governance approval requirements must be tested.
35. Approval replay must be prevented.
36. Expired approval must not authorize execution.
37. Concurrent approval operations must be deterministic.
38. Cross-tenant leakage tests must be release-blocking.
39. Sensitive data leakage must be tested.
40. Offline AI behavior must be tested where supported.
41. Offline model identity must remain historical.
42. Synchronization must preserve AI operation identity.
43. Duplicate synchronization must not create duplicate authoritative history.
44. API contracts must be tested.
45. Idempotency must be tested.
46. Rate limits must be tested.
47. Timeout behavior must be tested.
48. Retry behavior must be bounded.
49. Circuit breaker behavior must be tested where used.
50. Fallback behavior must be explicit.
51. Fallback must not invent authoritative ERP data.
52. Model artifact integrity must be validated.
53. Dependency compatibility must be tested.
54. Provider changes require regression evaluation where behavior may change.
55. Production deployment requires model readiness validation.
56. Canary deployments must be evaluated.
57. Shadow models must not affect authoritative ERP state.
58. Kill switches must preserve core ERP operation.
59. Drift thresholds are versioned.
60. Production degradation must be observable.
61. Model incidents must be traceable to deployments.
62. Rollback must preserve historical predictions.
63. Evaluation approval is separate from ERP transaction approval.
64. Evaluation artifacts are integrity-protected.
65. Evaluation reports are immutable after approval.
66. Corrections create new evaluation history.
67. Evaluation access is permission-controlled.
68. Evaluation exports are auditable.
69. Evaluation data follows privacy controls.
70. Synthetic data is clearly identified.
71. Test data must not accidentally enter production.
72. Automated CI gates must enforce mandatory tests.
73. Flaky tests must not hide regressions.
74. Statistical significance and practical significance should both be considered.
75. Business impact must be considered for important AI capabilities.
76. Evaluation rigor increases with business risk.
77. Prohibited autonomous capabilities must not be deployed.
78. Production evaluation continues after deployment.
79. Evaluation history remains available after model retirement.
80. Model retirement does not delete evaluation history.
81. Evaluation jobs are resource-limited.
82. Evaluation workloads must not starve production AI.
83. Core ERP operations remain independent of AI evaluation.
84. Evaluation failures must not modify ERP state.
85. External provider calls are isolated from ordinary tests.
86. Production secrets are never used in tests.
87. Test environments are isolated.
88. Evaluation environments preserve necessary lineage.
89. Evaluation runs identify their runtime environment.
90. Evaluation comparisons require comparable metric definitions.
91. Threshold changes are auditable.
92. Evaluation metrics have stable definitions.
93. Evaluation datasets preserve sampling context.
94. Human evaluation is attributable.
95. Reviewer independence applies where required.
96. AI recommendations remain distinguishable from human decisions.
97. Model outputs remain distinguishable from ERP facts.
98. Evaluation cannot grant production authority.
99. Passing evaluation does not permit unauthorized ERP actions.
100. Evaluation results do not become ERP transactions.
101. AI audit preserves evaluation lineage.
102. Evaluation results can be correlated with deployment.
103. Production incidents can be correlated with evaluation.
104. Model rollback remains auditable.
105. Historical evaluation cannot be silently overwritten.
106. Evaluation metadata remains queryable.
107. Evaluation API is access-controlled.
108. Long-running evaluation uses asynchronous processing.
109. Evaluation cancellation is deterministic.
110. Evaluation retries are idempotent.
111. Dead-letter evaluations remain identifiable.
112. Evaluation artifact deletion follows retention policy.
113. Evaluation storage does not become uncontrolled duplicate ERP storage.
114. Model evaluation does not require expensive hardware for ordinary ERP operation.
115. Production AI performance remains protected during evaluation.
116. Evaluation SLOs are observable.
117. Security regression testing remains continuous for important changes.
118. Evaluation must distinguish technical correctness from business usefulness.
119. Evaluation must distinguish model quality from business authorization.
120. Evaluation architecture must preserve historical integrity.

---

# 144. Performance and SLO Summary

| Area                             |       Target |
| -------------------------------- | -----------: |
| Evaluation creation              | p95 ≤ 200 ms |
| Evaluation status retrieval      | p95 ≤ 200 ms |
| Evaluation metadata retrieval    | p95 ≤ 500 ms |
| Normal model comparison          |    p95 ≤ 1 s |
| Lightweight inference            | p95 ≤ 500 ms |
| Standard AI API                  |  p95 ≤ 1.5 s |
| AI runtime availability          |      ≥ 99.5% |
| High-risk unauthorized AI action |            0 |
| Cross-Business data leakage      |            0 |
| Prohibited autonomous action     |            0 |

Long-running evaluation itself is asynchronous and is not subject to interactive API latency targets.

---

# 145. Failure Recovery

Evaluation failures must follow:

```text
Failure
  ↓
Classify
  ↓
Retry if transient
  ↓
Resume or restart
  ↓
Dead Letter if exhausted
  ↓
Audit
  ↓
Investigate
```

A failed evaluation must never be represented as a successful evaluation.

---

# 146. Architecture Integration

The evaluation architecture integrates with:

```text
AI Data Architecture
        ↓
AI Feature Architecture
        ↓
AI Training / Experimentation
        ↓
AI Model Registry
        ↓
AI Inference Runtime
        ↓
AI Governance
        ↓
AI Audit
        ↓
AI Deployment
        ↓
Production Monitoring
```

Evaluation is a lifecycle gate, not a one-time development activity.

---

# 147. Related Documents

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
* `docs/04_Architecture/07_AI/17_AI_Pipeline_and_Background_Processing.md`
* `docs/04_Architecture/07_AI/18_AI_Backend_and_API_Integration.md`
* `docs/04_Architecture/07_AI/19_AI_Frontend_and_User_Experience.md`
* `docs/04_Architecture/07_AI/20_AI_Offline_and_Synchronization_Architecture.md`
* `docs/04_Architecture/07_AI/21_AI_Security_and_Data_Privacy.md`
* `docs/04_Architecture/07_AI/22_AI_Governance_and_Human_Approval.md`
* `docs/04_Architecture/07_AI/23_AI_Audit_and_History_Architecture.md`

### Backend

* `docs/04_Architecture/06_Backend/17_Backend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### Frontend

* `docs/04_Architecture/08_Frontend/29_Frontend_Testing_and_Quality_Assurance_Architecture.md`
* `docs/04_Architecture/08_Frontend/26_Frontend_Error_Handling_and_Recovery_Architecture.md`

### System Analysis

* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

# 148. Final Architectural Principle

AI evaluation is not simply a model accuracy check.

The production standard is:

```text
Correct Data
    ↓
Correct Features
    ↓
Correct Model
    ↓
Correct Inference
    ↓
Correct Output
    ↓
Correct Security
    ↓
Correct Governance
    ↓
Acceptable Performance
    ↓
Acceptable Business Impact
    ↓
Approved Production Deployment
```

A model is production-ready only when its technical quality, business usefulness, security, governance and operational behavior have all passed the required evaluation gates.

**AI evaluation determines whether an AI capability is fit for use.
AI governance determines what the capability is allowed to do.
AI audit records what actually happened.
ERP remains the final authoritative system.**

