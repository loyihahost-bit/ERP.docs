# AI Anomaly Detection and Business Risk

**Document ID:** AI-09
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/08_AI/README.md`

---

## 1. Purpose

This document defines the architecture for detecting unusual operational, financial, inventory and business patterns using AI.

The system may identify potentially abnormal behavior such as:

* unusual sales;
* unusual refunds;
* unusual discounts;
* unusual cash discrepancies;
* unusual inventory consumption;
* unexpected stock movement;
* unusual employee activity;
* unusual Branch performance;
* unusual purchasing behavior;
* unexpected demand changes;
* potential operational risks.

AI anomaly detection is an analytical capability.

An anomaly is not automatically a fraud finding, policy violation or business error.

The core principle is:

> AI identifies unusual patterns; ERP rules and authorized humans determine what they mean.

---

# 2. Scope

This document covers:

* anomaly detection;
* business risk signals;
* sales anomalies;
* order anomalies;
* payment anomalies;
* refund anomalies;
* discount anomalies;
* cash anomalies;
* inventory anomalies;
* purchasing anomalies;
* employee activity anomalies;
* Branch anomalies;
* operational anomalies;
* demand anomalies;
* multi-signal risk;
* anomaly scoring;
* confidence;
* severity;
* explainability;
* false positives;
* false negatives;
* historical baselines;
* peer comparison;
* anomaly lifecycle;
* risk aggregation;
* human review;
* audit;
* alerting;
* privacy;
* Business/Branch isolation;
* offline considerations;
* subscription entitlement;
* performance;
* failure recovery;
* testing.

---

# 3. Authoritative Boundary

AI anomaly detection does not establish authoritative business facts.

For example:

```text
AI:
"Unusual refund pattern detected."

ERP:
"Refund exists and was authorized."

Human:
"Review whether the activity is expected."
```

AI must not independently conclude:

* employee committed fraud;
* cashier stole money;
* customer committed fraud;
* inventory was stolen;
* manager violated policy;
* transaction is illegal;
* employee must be terminated.

These are business, legal or management decisions outside the anomaly model.

---

# 4. Anomaly Detection Principles

The system follows these principles:

1. Anomaly detection is advisory.
2. Anomaly does not mean error.
3. Anomaly does not mean fraud.
4. ERP remains the source of truth.
5. Deterministic business rules remain authoritative.
6. Historical context must be preserved.
7. Branch context must be preserved.
8. Business isolation must be enforced.
9. False positives must be expected and measurable.
10. False negatives must be monitored where possible.
11. Anomaly explanations must be understandable.
12. High-risk signals require human review.
13. AI failure must not block ERP operations.
14. AI must not bypass permissions.
15. AI must not bypass subscription restrictions.

---

# 5. Anomaly Categories

The system may detect anomalies in:

```text
Sales
Orders
Payments
Refunds
Discounts
Cash
Inventory
Purchasing
Employees
Branches
Operations
Demand
Configuration
Synchronization
```

Not every category must use the same model.

The appropriate detection method depends on the data.

---

# 6. Detection Methods

Possible methods include:

* statistical thresholds;
* rolling averages;
* standard deviation;
* z-score;
* seasonal baseline;
* time-series residuals;
* clustering;
* density-based methods;
* isolation-based methods;
* supervised classification where labeled data exists;
* autoencoders;
* change-point detection;
* peer-group comparison;
* rule + model hybrid detection.

The simplest sufficiently reliable method should be preferred.

---

# 7. Deterministic Rules vs AI Detection

Some conditions are deterministic and should not require AI.

Examples:

```text
Negative inventory
Unauthorized permission
Invalid payment state
Duplicate operation UUID
Closed Cash Session modification
```

These belong to ERP business rules.

AI should focus on patterns that are difficult to define deterministically.

---

# 8. Anomaly Event

A detected anomaly should produce an internal anomaly record containing at minimum:

* Anomaly UUID;
* Business UUID;
* Branch UUID where applicable;
* anomaly type;
* source entity;
* source transaction/event;
* detection timestamp;
* observed period;
* anomaly score;
* severity;
* confidence;
* model/version;
* explanation metadata;
* status.

---

# 9. Anomaly Score

The system may calculate an anomaly score.

Example:

```text
Score = 0.87
```

The score is model-specific.

It must not automatically be interpreted as:

```text
87% probability of fraud
```

unless the model has explicitly been trained and calibrated for that probability interpretation.

---

# 10. Severity

Anomaly severity may be represented as:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Severity should depend on:

* anomaly magnitude;
* financial impact;
* operational impact;
* confidence;
* affected entities;
* persistence;
* historical pattern;
* Business-defined thresholds.

Severity is an analytical classification, not an accusation.

---

# 11. Confidence

Confidence represents how strongly the system supports the anomaly signal.

Example:

```text
Anomaly Score: 0.88
Confidence: Medium
Severity: High
```

Score and confidence must remain separate concepts.

---

# 12. Sales Anomaly Detection

The system may detect unusual sales behavior such as:

* sudden sales spike;
* sudden sales drop;
* unusual Product mix;
* unexpected Branch sales pattern;
* unusually large transaction;
* unusual time-of-day behavior.

Example:

```text
Normal Friday:
100–130 orders

Observed:
260 orders
```

This may generate an anomaly signal.

The system must consider legitimate causes such as promotions or events.

---

# 13. Demand Anomaly

Demand anomalies may occur when actual demand differs significantly from expected demand.

Example:

```text
Forecast:
100

Actual:
185
```

Possible explanations include:

* promotion;
* event;
* holiday;
* Product change;
* sudden customer behavior;
* data error.

The system should identify the anomaly without automatically selecting the cause.

---

# 14. Order Anomaly

Possible order anomalies include:

* unusually large order;
* unusual order frequency;
* repeated cancellations;
* repeated modifications;
* unusual item combinations;
* unusual order timing;
* unusual order value.

The system should compare behavior against an appropriate baseline.

---

# 15. Payment Anomaly

Possible payment anomalies include:

* unusual payment amount;
* unusual payment method distribution;
* repeated payment failures;
* unusual payment timing;
* abnormal payment reversals.

Payment state remains authoritative in ERP.

AI only identifies unusual patterns.

---

# 16. Refund Anomaly

Refunds are a high-value anomaly category.

The system may identify:

* unusually high refund volume;
* unusually high refund value;
* repeated refunds by the same employee;
* unusual refund timing;
* unusual refund ratio;
* Branch refund deviation.

Example:

```text
Branch average:
2% refund ratio

Observed:
9%
```

This is a risk signal, not proof of wrongdoing.

---

# 17. Discount Anomaly

The system may detect:

* unusually frequent discounts;
* unusually high discount value;
* unusual discount timing;
* employee-level deviation;
* Branch-level deviation;
* unusual Product-specific discounts.

Discount permission remains deterministic.

Anomaly detection does not replace authorization checks.

---

# 18. Cash Anomaly

Possible cash anomalies include:

* repeated shortages;
* unusual shortage magnitude;
* unusual cash handover pattern;
* repeated correction;
* abnormal closing difference;
* Branch deviation;
* employee deviation.

Example:

```text
Typical discrepancy:
0–20,000

Observed:
350,000
```

The system may generate a high-risk signal.

The actual cash state remains authoritative.

---

# 19. Cash Handover Anomaly

The system may identify patterns such as:

* repeated shortage by same employee;
* repeated handover corrections;
* repeated recounts;
* unusual handover timing;
* abnormal difference compared with employee history.

The system must distinguish legitimate operational causes where available.

---

# 20. Inventory Anomaly

Possible inventory anomalies include:

* unexpected consumption;
* unusual stock decrease;
* abnormal variance;
* repeated adjustment;
* unusual waste;
* unusual Product-to-material ratio;
* unexpected recipe consumption.

Example:

```text
Expected consumption:
20 kg

Observed:
45 kg
```

Possible explanations may include:

* genuine demand;
* waste;
* recipe change;
* stock count error;
* operational issue.

AI should not automatically label the event as theft.

---

# 21. Inventory Adjustment Anomaly

Repeated manual inventory adjustments may be a risk signal.

The system may consider:

* frequency;
* magnitude;
* employee;
* Branch;
* Product;
* time;
* historical baseline.

Actual adjustment validity remains an ERP/business decision.

---

# 22. Purchasing Anomaly

Possible purchasing anomalies include:

* unusual purchase quantity;
* unusual purchase price;
* unusual supplier usage;
* sudden supplier change;
* unusually frequent purchases;
* purchase outside historical pattern.

The system should account for legitimate seasonal or operational changes.

---

# 23. Purchase Price Anomaly

Example:

```text
Historical purchase price:
10,000

New purchase price:
15,500
```

The system may flag a significant deviation.

It should consider:

* supplier;
* quantity;
* market conditions where available;
* Product quality;
* delivery conditions;
* historical price volatility.

---

# 24. Employee Activity Anomaly

AI may identify unusual operational patterns for an employee.

Possible signals:

* unusual number of refunds;
* unusual discounts;
* unusual corrections;
* unusual cash discrepancies;
* unusual order modifications;
* unusual activity outside normal schedule.

Employee anomaly detection must be handled carefully.

The system must not automatically classify an employee as dishonest.

---

# 25. Employee Baseline

Employee comparisons should normally use an appropriate historical baseline.

For example:

```text
Employee A:
Average refunds = 2/day

Observed:
15/day
```

The system may identify an anomaly.

However, a role change or temporary operational responsibility may explain it.

---

# 26. Role-Aware Detection

Employee activity should be interpreted according to role and permission scope.

A Cashier and Manager should not automatically share the same behavioral baseline.

The model may consider:

* role;
* Branch;
* shift;
* permission set;
* operational responsibility.

---

# 27. Branch Anomaly Detection

Branches may be compared against:

* their own history;
* similar Branches;
* Business-level baseline.

Example:

```text
Branch A:
Expected daily sales = 500

Observed:
190
```

The system may identify a Branch-level anomaly.

The model should consider:

* opening hours;
* menu;
* equipment;
* holidays;
* local operational conditions.

---

# 28. Peer Group Comparison

Peer comparison may be useful when enough data exists.

Possible peer groups:

* similar Branches;
* similar Product categories;
* similar employee roles;
* similar operating periods.

Peer comparison must not expose another Business's raw data.

---

# 29. Seasonal Baseline

Anomaly detection must consider seasonality.

For example:

```text
Friday sales
≠
Monday sales
```

An event that appears unusual against a daily average may be normal for a Friday.

---

# 30. Time-of-Day Baseline

Where data volume permits, the system may establish time-of-day patterns.

Example:

```text
12:00–14:00 → high demand
15:00–17:00 → low demand
```

Anomaly detection should account for expected operating patterns.

---

# 31. Multi-Signal Risk

Individual anomalies may be weak.

Multiple correlated signals may increase risk.

Example:

```text
High Refund Rate
       +
High Discount Rate
       +
Cash Shortage
       ↓
Elevated Business Risk Signal
```

This does not automatically prove misconduct.

It indicates that human review may be valuable.

---

# 32. Risk Aggregation

The system may aggregate related anomalies into a risk case.

Example:

```text
Risk Case
 ├── Refund anomaly
 ├── Discount anomaly
 └── Cash discrepancy
```

Risk aggregation should preserve each underlying anomaly.

---

# 33. Risk Score

A Business Risk Score may be calculated from validated anomaly signals.

Example:

```text
Risk Score: 72 / 100
```

The score must have documented semantics.

It must not be represented as a probability of fraud unless explicitly calibrated for that purpose.

---

# 34. Risk Categories

Possible categories include:

* Financial Risk;
* Inventory Risk;
* Operational Risk;
* Sales Risk;
* Cash Risk;
* Employee Activity Risk;
* Data Quality Risk;
* Security-related Risk.

A single anomaly may belong to more than one analytical category.

---

# 35. Risk Lifecycle

Risk cases may follow:

```text
DETECTED
   ↓
REVIEW_REQUIRED
   ↓
UNDER_REVIEW
   ↓
CONFIRMED
   ↓
RESOLVED
```

Alternative outcome:

```text
DETECTED
   ↓
DISMISSED
```

The meaning of `CONFIRMED` must be defined as a human/business review result, not AI proof.

---

# 36. Anomaly Lifecycle

Individual anomalies may use:

```text
DETECTED
OPEN
ACKNOWLEDGED
INVESTIGATING
RESOLVED
DISMISSED
EXPIRED
```

Historical anomaly records should remain available according to retention policy.

---

# 37. Human Review

High-risk anomalies should be reviewable by authorized employees.

The review workflow may include:

```text
AI Detection
      ↓
Risk Signal
      ↓
Authorized Reviewer
      ↓
Investigation
      ↓
Business Decision
```

The AI does not replace the reviewer.

---

# 38. Human Review Outcome

A reviewer may classify a detected anomaly as:

* legitimate;
* operational issue;
* data quality issue;
* expected event;
* requires correction;
* requires further investigation;
* confirmed business violation.

The classification belongs to the authorized human/business process.

---

# 39. Human Feedback

Review outcomes may become labeled data for future model improvement.

However:

* feedback must be validated;
* labels must not be blindly trusted;
* reviewer identity must be retained;
* label changes must be traceable.

---

# 40. False Positives

False positives are expected.

Example:

```text
Large refund spike
```

may be caused by:

* system outage;
* duplicate payment issue;
* legitimate campaign;
* customer service event.

The system should monitor false-positive rates.

---

# 41. False Negatives

Anomaly systems may miss abnormal activity.

The system should evaluate:

* known incidents;
* historical confirmed cases;
* detection coverage;
* delayed detection.

A high anomaly score does not guarantee detection of every risk.

---

# 42. Thresholds

Thresholds may be:

* global;
* Business-specific;
* Branch-specific;
* category-specific;
* model-specific.

Threshold changes must be controlled and versioned where they affect operational behavior.

---

# 43. Adaptive Thresholds

Where appropriate, AI may learn normal behavior dynamically.

However, adaptive thresholds must not become so permissive that abnormal behavior becomes the new baseline without detection.

Baseline adaptation must be monitored.

---

# 44. New Business Cold Start

A new Business may have insufficient historical data.

The system should use:

* deterministic thresholds;
* generic statistical baselines;
* gradually learned Business-specific baselines.

The system must clearly identify low-confidence anomaly results.

---

# 45. New Branch Cold Start

A new Branch may initially rely on:

* Business baseline;
* peer Branch baseline where authorized;
* generic operational baseline.

Branch-specific models should become active only when sufficient data exists.

---

# 46. New Employee Cold Start

A new employee should not immediately be judged against an unstable personal baseline.

The system may use:

* role baseline;
* Branch baseline;
* Business baseline.

Employee-specific detection should activate after sufficient history exists.

---

# 47. Data Quality Anomalies

AI may detect anomalies in the data itself.

Examples:

* unusual transaction volume;
* duplicate patterns;
* missing records;
* unexpected timestamp distribution;
* sudden quantity changes;
* inconsistent references.

Data quality anomalies should be distinguished from business anomalies.

---

# 48. Synchronization Anomalies

Offline synchronization may produce unusual patterns.

Examples:

* unexpected transaction burst;
* repeated retry;
* delayed synchronization;
* unusual operation ordering.

Synchronization validation remains authoritative.

AI may help identify patterns for investigation.

---

# 49. Security Relationship

Security events may use anomaly signals.

However, security-critical authorization must remain deterministic.

AI cannot replace:

* authentication;
* permission checks;
* trusted device verification;
* signed offline authorization;
* synchronization validation.

---

# 50. Offline Anomaly Detection

Offline clients may collect operational data normally.

Live AI anomaly analysis should generally occur after synchronization.

The device must not make authoritative security or financial decisions based on local AI anomaly scoring.

Previously synchronized anomaly information may be cached for display where appropriate.

---

# 51. Real-Time vs Batch Detection

Anomaly detection may operate in two modes.

### Near-real-time

Used for:

* high-value refund;
* suspicious cash event;
* unusual transaction;
* important operational signal.

### Batch

Used for:

* daily Branch analysis;
* employee patterns;
* inventory behavior;
* purchasing patterns;
* Business risk summaries.

The detection mode depends on business value and resource cost.

---

# 52. Critical Path Isolation

AI anomaly detection must not execute synchronously inside critical ERP transactions unless the operation is explicitly designed for lightweight detection.

The preferred pattern is:

```text
ERP Transaction
      ↓
Commit
      ↓
Event / Outbox
      ↓
Anomaly Detection
```

This prevents AI latency from blocking POS operations.

---

# 53. Event-Based Detection

Important business events may trigger anomaly analysis.

Examples:

* Order completed;
* Refund completed;
* Cash Session closed;
* Cash handover completed;
* Inventory adjustment;
* Purchase received;
* Employee action;
* Branch configuration change.

Events must come from authoritative ERP operations.

---

# 54. Batch Detection

Batch jobs may periodically analyze:

* daily sales;
* daily refunds;
* weekly inventory;
* employee activity;
* Branch performance.

Batch jobs must be idempotent and versioned.

---

# 55. Anomaly Versioning

Anomaly detection results must identify:

* model version;
* feature version;
* data snapshot/version;
* detection rule version where applicable.

A model change must not silently reinterpret historical anomalies.

---

# 56. Detection Model Lifecycle

Anomaly models follow the general model lifecycle:

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

Model versions are immutable.

---

# 57. Baseline Versioning

The system must version important baselines.

Example:

```text
Employee Refund Baseline v2
Branch Sales Baseline v5
Inventory Consumption Baseline v3
```

This helps reproduce why an anomaly was detected.

---

# 58. Anomaly Explanation

An anomaly should provide understandable evidence.

Example:

```text
Unusual refund activity detected.

Observed:
12 refunds

Typical Branch range:
2–5 refunds

Difference:
+140% above expected range
```

The explanation should avoid unsupported claims.

---

# 59. Risk Explanation

A risk case should show its contributing signals.

Example:

```text
Risk Level: High

Signals:
- Refund rate 4.2× Branch baseline
- Discount value 2.8× baseline
- Cash discrepancy above historical range
```

This is more useful than displaying only a single risk score.

---

# 60. Causal Claims

The anomaly system must not claim:

```text
"Employee caused the shortage."
```

unless the statement is supported by authoritative business investigation.

Preferred:

```text
"Cash discrepancy pattern is unusual for this employee and Branch."
```

---

# 61. Alerting

Important anomalies may generate notifications.

Examples:

* large refund anomaly;
* significant cash discrepancy;
* severe inventory variance;
* unusual Branch performance;
* repeated operational anomalies.

Notifications should contain:

* anomaly type;
* severity;
* affected entity;
* timestamp;
* explanation;
* recommended next step where appropriate.

---

# 62. Alert Deduplication

The same underlying event must not generate uncontrolled duplicate alerts.

The system should support:

* event UUID;
* anomaly key;
* deduplication window;
* correlation ID.

---

# 63. Alert Escalation

Persistent high-risk anomalies may escalate.

Example:

```text
Detected
   ↓
Notification
   ↓
No Review
   ↓
Escalation
```

Escalation must follow explicit business policy.

AI must not invent escalation authority.

---

# 64. Risk Aggregation by Branch

Business dashboards may summarize:

```text
Branch A → Low
Branch B → Medium
Branch C → High
```

The underlying anomaly signals must remain accessible to authorized users.

An aggregate score must not hide the evidence.

---

# 65. Risk Aggregation by Business

Business-level risk summaries may aggregate Branch signals.

The aggregation must:

* preserve Branch scope;
* preserve anomaly identity;
* avoid double counting;
* use versioned calculation rules.

---

# 66. Financial Risk

AI may identify patterns related to:

* refunds;
* discounts;
* cash discrepancies;
* unusual payment behavior;
* unusual purchase costs;
* unusual expenses.

These signals must remain separate from authoritative accounting calculations.

---

# 67. Inventory Risk

Inventory risk may include:

* stockout risk;
* excess stock;
* unusual consumption;
* repeated adjustments;
* unexplained variance;
* expiration risk.

Inventory intelligence from AI-08 may consume these anomaly signals.

---

# 68. Operational Risk

Operational risk may include:

* repeated equipment-related demand changes;
* unusual Branch downtime;
* unusual order processing delays;
* abnormal cancellation patterns;
* synchronization anomalies.

These signals are informational.

---

# 69. Employee Risk

Employee-related anomaly detection must be especially conservative.

The system should emphasize:

```text
Behavioral anomaly
```

rather than:

```text
Employee wrongdoing
```

Human review is required before consequential decisions.

---

# 70. Privacy

Anomaly detection may process employee activity and financial information.

The system must apply:

* least privilege;
* Business isolation;
* Branch scope;
* role-based access;
* data minimization;
* controlled retention;
* audit for sensitive access.

---

# 71. Sensitive Risk Data

Risk cases may contain commercially or operationally sensitive information.

Access should be limited to authorized users.

Risk data must not be exposed through:

* unrestricted API responses;
* unauthorized exports;
* LLM prompts;
* client-side logs.

---

# 72. LLM Integration

LLMs may explain anomaly results.

Flow:

```text
Validated Anomaly
      ↓
Authorized Context
      ↓
LLM
      ↓
Human-readable Explanation
```

The LLM must not:

* create an anomaly;
* change severity;
* resolve a risk;
* accuse an employee;
* change ERP state.

The authoritative anomaly result comes from the anomaly service.

---

# 73. Prompt Injection Protection

User prompts must not bypass:

* Business scope;
* Branch scope;
* employee privacy;
* risk permissions;
* subscription;
* audit controls.

LLM output must not become an authorization decision.

---

# 74. Recommendation Relationship

Anomaly detection may produce recommendations.

Example:

```text
Inventory anomaly
      ↓
Review stock count
```

The recommendation remains advisory.

The ERP workflow determines whether a correction is actually performed.

---

# 75. Forecast Relationship

Forecast deviations may become anomaly signals.

Example:

```text
Forecast:
100

Actual:
220

Anomaly:
High demand deviation
```

The system should distinguish:

* genuine demand change;
* stock availability issue;
* promotion;
* data quality problem.

---

# 76. Inventory Intelligence Relationship

Anomaly signals may influence inventory intelligence.

Example:

```text
Unusual consumption detected
        ↓
Purchase recommendation confidence reduced
```

The system should avoid extrapolating anomalous consumption blindly.

---

# 77. Recommendation Confidence Adjustment

An anomaly may reduce confidence in downstream AI recommendations.

Example:

```text
Normal inventory data
      ↓
High confidence

Anomalous inventory data
      ↓
Lower confidence
```

The mechanism must be deterministic and documented.

---

# 78. Risk Case Correlation

Related anomalies should be correlated where appropriate.

Example:

```text
Refund anomaly
      +
Discount anomaly
      +
Cash discrepancy
      ↓
Risk Case R-102
```

Correlation must not destroy individual anomaly records.

---

# 79. Investigation Notes

Authorized reviewers may add investigation notes.

Notes should preserve:

* author;
* timestamp;
* anomaly/risk reference;
* content;
* history of changes.

Important notes should be immutable or versioned according to audit architecture.

---

# 80. Resolution

A risk case may be resolved as:

* legitimate;
* operational issue;
* data correction;
* confirmed policy violation;
* unresolved;
* dismissed.

Resolution must be performed through the authorized business workflow.

---

# 81. No Automatic Punitive Action

AI anomaly detection must not automatically:

* deactivate employee;
* reduce salary;
* block cashier;
* delete transaction;
* reverse payment;
* modify inventory;
* suspend Branch.

Such actions require deterministic business rules or authorized human decisions.

---

# 82. Anomaly Data Retention

Anomaly and risk history must follow AI and ERP lifecycle policy.

Historical records may be retained for:

* investigation;
* model evaluation;
* audit;
* risk analysis;
* compliance where applicable.

Business deletion must apply to associated anomaly data.

---

# 83. Performance Targets

Initial targets:

### Lightweight anomaly lookup

```text
p95 ≤ 500 ms
```

### Near-real-time detection

```text
p95 ≤ 5 seconds
```

after the source event becomes available to the anomaly worker.

### Standard Branch batch analysis

```text
≤ 10 minutes
```

### Standard Business daily risk analysis

```text
≤ 30 minutes
```

### AI anomaly service availability

```text
≥ 99.5%
```

AI latency must not block critical ERP transactions.

---

# 84. Resource Management

The anomaly subsystem should support:

* worker concurrency limits;
* CPU-first execution;
* memory limits;
* timeouts;
* retry limits;
* job priorities;
* Business-level quotas where required.

Critical ERP workers have priority over AI analysis.

---

# 85. Failure Handling

If anomaly detection fails:

```text
ERP Transaction
      ↓
Committed normally
      ↓
Anomaly Detection Failed
      ↓
Retry / Monitoring
```

The transaction must not be rolled back merely because AI detection failed.

---

# 86. Previous Result Fallback

If new analysis fails, the system may display the previous valid anomaly/risk summary with explicit freshness information.

It must not appear as newly calculated.

---

# 87. Data Quality Failure

If source data is incomplete or inconsistent:

```text
Anomaly Status:
INSUFFICIENT_DATA
```

The system must avoid generating misleading high-confidence risk scores.

---

# 88. Monitoring

The anomaly subsystem should monitor:

* detection latency;
* job failure rate;
* anomaly volume;
* severity distribution;
* false-positive rate;
* review outcomes;
* dismissed anomalies;
* confirmed anomalies;
* model drift;
* baseline drift;
* resource consumption.

---

# 89. Model Evaluation

Anomaly models should be evaluated using:

* precision;
* recall where labels exist;
* false-positive rate;
* false-negative indicators;
* detection latency;
* reviewer usefulness;
* business impact.

For unsupervised models, evaluation may require a combination of expert review and synthetic/historical validation.

---

# 90. Model Drift

Behavioral patterns may change.

Examples:

* new menu;
* new Branch;
* new pricing;
* seasonal changes;
* new employees;
* operational changes.

The anomaly model must be monitored for drift.

Drift must not automatically trigger model replacement without evaluation.

---

# 91. Threshold Calibration

Thresholds should be calibrated using historical behavior and business impact.

High sensitivity may produce too many alerts.

Low sensitivity may miss meaningful anomalies.

The system should optimize for actionable signals rather than maximum anomaly volume.

---

# 92. Alert Fatigue

The system must avoid excessive notifications.

Controls may include:

* severity thresholds;
* deduplication;
* correlation;
* notification cooldown;
* aggregation;
* user-specific notification permissions.

The goal is:

> Fewer, higher-value alerts.

---

# 93. Testing

Testing must cover:

### Unit tests

* anomaly score;
* severity;
* thresholds;
* baseline calculation;
* risk aggregation;
* deduplication.

### Integration tests

* Order events;
* refund events;
* cash sessions;
* inventory;
* purchasing;
* notifications;
* audit.

### Model tests

* precision;
* recall;
* stability;
* drift;
* false positives.

### Security tests

* Business isolation;
* Branch isolation;
* employee privacy;
* unauthorized risk access;
* LLM boundary.

---

# 94. Scenario Testing

Important scenarios include:

1. Normal sales spike.
2. Genuine promotion.
3. Holiday demand.
4. Large legitimate refund event.
5. Unusual refund behavior.
6. Normal inventory adjustment.
7. Repeated inventory adjustment.
8. Equipment failure.
9. New Branch.
10. New employee.
11. New Product.
12. Seasonal demand.
13. Cash shortage.
14. Repeated cash shortages.
15. Unusual purchase price.
16. Supplier change.
17. Synchronization burst.
18. Data quality issue.

---

# 95. Historical Integrity

Historical anomaly results must remain linked to:

* source data state;
* model version;
* feature version;
* baseline version;
* detection rule version.

A later model must not silently rewrite historical anomaly conclusions.

---

# 96. Reprocessing

Historical data may be reprocessed for model evaluation.

Reprocessing must create a new analysis version.

The original production anomaly record must remain distinguishable.

---

# 97. Cross-Business Isolation

Anomaly models must enforce Business boundaries.

Shared models may learn generalized patterns only under approved data policy.

Raw tenant-specific anomaly records must not be exposed to another Business.

---

# 98. Cross-Branch Isolation

Branch-level anomaly information must remain Branch-scoped unless the user has authorized multi-Branch access.

Business-level aggregation may be shown only to authorized users.

---

# 99. Subscription Entitlement

After subscription expiry:

* existing anomaly history may remain viewable;
* existing risk cases may remain viewable;
* new expensive AI analysis may be restricted;
* configuration changes are blocked;
* exports remain available where permitted.

AI must not bypass subscription restrictions.

---

# 100. Export

Authorized users may export anomaly/risk information.

Exports may include:

* anomaly type;
* Branch;
* affected entity;
* severity;
* score;
* detection timestamp;
* status;
* resolution;
* explanation.

Sensitive employee-related exports should be restricted and auditable.

---

# 101. Audit Relationship

AI lineage records how an anomaly was detected.

ERP audit records what authorized users actually did.

For example:

```text
AI:
Refund anomaly detected.

ERP Audit:
Manager reviewed anomaly.

ERP:
Refund remains valid.
```

Both histories must remain distinct.

---

# 102. Architecture

The logical architecture is:

```text
                 ERP
                  │
            Business Events
                  │
          ┌───────┴────────┐
          ▼                ▼
    Historical Data     Real-time Events
          │                │
          └───────┬────────┘
                  ▼
          AI Data Preparation
                  │
                  ▼
       Baseline / Feature Layer
                  │
                  ▼
         Anomaly Detection
                  │
                  ▼
        Output Validation
                  │
          ┌───────┴────────┐
          ▼                ▼
       Anomaly          Risk Aggregation
          │                │
          └───────┬────────┘
                  ▼
             Notification
                  │
                  ▼
             Human Review
                  │
                  ▼
             ERP Decision
```

---

# 103. System Invariants

The following invariants apply to AI Anomaly Detection and Business Risk:

1. ERP remains the source of truth.
2. Anomaly detection is advisory.
3. An anomaly is not automatically an error.
4. An anomaly is not automatically fraud.
5. An anomaly is not automatically a policy violation.
6. AI cannot independently accuse an employee.
7. AI cannot independently punish an employee.
8. AI cannot independently block an employee.
9. AI cannot independently reverse transactions.
10. AI cannot independently modify inventory.
11. AI cannot independently modify cash.
12. AI cannot independently modify purchases.
13. AI cannot independently modify prices.
14. AI cannot independently modify permissions.
15. AI cannot bypass deterministic ERP rules.
16. Business isolation is mandatory.
17. Branch isolation is mandatory.
18. Employee-sensitive data is access controlled.
19. Anomaly results are versioned.
20. Model versions are identifiable.
21. Feature versions are identifiable.
22. Baseline versions are identifiable.
23. Detection rules are versioned where applicable.
24. Historical anomaly results are not silently rewritten.
25. Anomaly scores are not automatically probabilities.
26. Confidence and anomaly score remain separate.
27. Severity and anomaly score remain separate.
28. High-risk anomalies require appropriate human review.
29. Human review outcome is authoritative for business resolution.
30. Human overrides remain traceable.
31. Individual anomaly signals remain available after risk aggregation.
32. Risk aggregation must not destroy source anomaly history.
33. Related anomalies may be correlated without losing individual identity.
34. Alert deduplication must prevent uncontrolled duplicate notifications.
35. Alert fatigue must be controlled.
36. False positives are expected and monitored.
37. False negatives are monitored where measurable.
38. Seasonal behavior must be considered.
39. Role differences must be considered.
40. Branch-specific behavior must be considered.
41. New Business cold start must be explicit.
42. New Branch cold start must be explicit.
43. New Employee cold start must be explicit.
44. Insufficient data must be explicitly represented.
45. Data quality anomalies are distinguishable from business anomalies.
46. Security-critical decisions remain deterministic.
47. Offline clients cannot make authoritative anomaly decisions.
48. AI detection must not block critical ERP transactions.
49. Event-driven detection should normally occur after ERP commit.
50. Failed AI detection must not roll back committed ERP transactions.
51. Previous valid results may remain available with stale status.
52. Near-real-time detection has bounded latency.
53. Batch detection has bounded execution time.
54. AI resource usage is controlled.
55. Duplicate jobs are controlled through idempotency.
56. Concurrent jobs cannot corrupt anomaly state.
57. Historical reprocessing creates a new analysis version.
58. Forecast anomalies remain distinguishable from inventory anomalies.
59. Inventory anomalies remain distinguishable from financial anomalies.
60. Risk scores must have documented semantics.
61. Causal claims require supporting evidence.
62. LLMs cannot modify anomaly state.
63. LLMs cannot resolve risk cases.
64. Prompt injection cannot bypass authorization.
65. Sensitive anomaly data cannot be exposed through unrestricted prompts.
66. Sensitive exports respect permissions.
67. Subscription restrictions apply to anomaly analysis.
68. Business deletion applies to associated anomaly and risk data.
69. External AI provider failure must not block ERP.
70. Anomaly detection remains subordinate to ERP authority.
71. AI may identify unusual behavior; authorized humans and ERP rules determine what action, if any, follows.

---

# 104. Related Documents

### AI Architecture

* `docs/04_Architecture/08_AI/01_AI_Architecture_Overview.md`
* `docs/04_Architecture/08_AI/02_AI_Use_Cases_and_Capabilities.md`
* `docs/04_Architecture/08_AI/03_AI_Boundaries_and_Non_AI_Decisions.md`
* `docs/04_Architecture/08_AI/04_AI_Data_Architecture.md`
* `docs/04_Architecture/08_AI/05_AI_Data_Preparation_and_Feature_Engineering.md`
* `docs/04_Architecture/08_AI/06_AI_Model_Architecture_and_Model_Strategy.md`
* `docs/04_Architecture/08_AI/07_AI_Forecasting_and_Demand_Prediction.md`
* `docs/04_Architecture/08_AI/08_AI_Inventory_and_Purchasing_Intelligence.md`
* `docs/04_Architecture/08_AI/10_AI_LLM_and_Natural_Language_Architecture.md`
* `docs/04_Architecture/08_AI/11_AI_Prompt_Context_and_Guardrails.md`
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

### ERP Architecture

* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/04_Architecture/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/04_Architecture/05_Database/17_Shift_Handover_Data_Model.md`
* `docs/04_Architecture/05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/04_Architecture/05_Database/18_Employee_Attendance_and_Payroll_Data_Model.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`

### Business and System Analysis

* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

---

# 105. Status

**AI Architecture Interview:** Completed for the current anomaly detection and business risk scope.

**Document Status:** Proposed.

**Current Document:** `09_AI_Anomaly_Detection_and_Business_Risk.md`

**Previous Document:** `08_AI_Inventory_and_Purchasing_Intelligence.md`

**Next Document:** `10_AI_LLM_and_Natural_Language_Architecture.md`

**AI Architecture Sequence:** Frozen at 28 documents.

**AI Architecture Progress:** 09 / 28

