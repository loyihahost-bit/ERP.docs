# AI Forecasting and Demand Prediction

**Document ID:** AI-07
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/08_AI/README.md`

---

## 1. Purpose

This document defines the architecture and business behavior of forecasting and demand prediction capabilities within FastFood ERP.

The system must be able to estimate future demand for:

* Products;
* Product categories;
* Semi-finished products;
* Raw materials;
* Branches;
* Business-level sales.

Forecasting is an AI-assisted capability.

Forecast results are advisory and must not directly modify authoritative ERP state.

The ERP remains the source of truth for:

* inventory;
* orders;
* prices;
* recipes;
* purchasing;
* menu availability;
* cash;
* financial transactions.

The core principle is:

> AI predicts future demand; ERP determines and executes business state.

---

# 2. Scope

This document covers:

* demand forecasting;
* sales forecasting;
* inventory demand prediction;
* branch-level forecasting;
* product-level forecasting;
* raw-material demand estimation;
* semi-finished product demand estimation;
* forecast horizons;
* historical data preparation;
* stockout-aware forecasting;
* seasonality;
* promotions and discounts;
* menu availability;
* price changes;
* branch differences;
* new-product cold start;
* forecast confidence;
* forecast freshness;
* forecast versioning;
* forecast validation;
* forecast monitoring;
* forecast failure handling;
* forecast authorization;
* forecast explainability;
* offline considerations;
* subscription entitlement;
* performance and SLOs.

---

# 3. Forecasting Principles

The forecasting subsystem follows these principles:

1. ERP data is authoritative.
2. Forecasts are predictions, not facts.
3. Forecasts must be reproducible.
4. Forecast versions must be identifiable.
5. Historical data must not be silently rewritten.
6. Stockouts must not automatically be interpreted as low demand.
7. Menu availability must be considered.
8. Branch differences must be considered.
9. Price and discount changes may affect demand.
10. Forecast confidence must be represented.
11. Insufficient data must be explicitly reported.
12. AI failure must not block normal ERP operations.
13. Forecast generation must not block POS.
14. Business and Branch isolation must be preserved.
15. The simplest sufficiently accurate model is preferred.

---

# 4. Forecasting Hierarchy

Forecasting may be performed at several levels:

```text
Business
   ↓
Branch
   ↓
Category
   ↓
Product
   ↓
Recipe / Semi-Finished Product
   ↓
Raw Material
```

The system should prefer the lowest level for which sufficient reliable data exists.

For example:

```text
Product Forecast
      ↓
Recipe Consumption
      ↓
Semi-Finished Demand
      ↓
Raw Material Demand
```

This allows product sales predictions to support inventory planning.

---

# 5. Forecast Types

The system supports the following forecast types.

## 5.1. Sales Forecast

Predicts future sales volume or sales value.

Example:

```text
Tomorrow
Burger → 82 units
Pizza → 54 units
Lavash → 117 units
```

## 5.2. Product Demand Forecast

Predicts expected product quantity required during a future period.

## 5.3. Inventory Demand Forecast

Predicts expected consumption of inventory items.

## 5.4. Raw Material Demand Forecast

Uses product demand and recipes to estimate required raw materials.

## 5.5. Semi-Finished Demand Forecast

Estimates expected production/consumption of semi-finished products.

## 5.6. Branch Forecast

Predicts demand separately for each Branch.

## 5.7. Business Forecast

Aggregates Branch forecasts when a Business-level view is required.

---

# 6. Forecast Horizon

Forecasts may be generated for different horizons.

### Short-term

```text
1–7 days
```

Used primarily for:

* daily preparation;
* kitchen planning;
* inventory planning;
* purchasing reminders.

### Medium-term

```text
8–30 days
```

Used primarily for:

* procurement planning;
* staffing planning;
* inventory planning;
* Branch performance planning.

### Long-term

```text
31–90 days
```

Used primarily for:

* trend analysis;
* seasonal planning;
* strategic decisions.

Long-horizon forecasts must expose greater uncertainty.

The system must not present long-term forecasts with the same confidence as short-term forecasts.

---

# 7. Forecast Granularity

Forecasts should normally support:

* daily;
* weekly;
* monthly aggregation.

Daily forecasts are the primary operational forecasting unit.

Weekly and monthly forecasts may be derived from daily predictions or generated independently where appropriate.

The selected granularity must be stored with the forecast version.

---

# 8. Historical Data Sources

Forecasting may use the following authoritative ERP data:

* completed Orders;
* Order Items;
* historical quantities;
* historical selling prices;
* discounts;
* Product availability;
* Branch;
* category;
* recipe versions;
* inventory transactions;
* stockout periods;
* menu activation/deactivation;
* equipment availability;
* holidays;
* business calendar;
* operating hours.

Only data permitted by Business and Branch scope may be used.

---

# 9. Order Data Eligibility

Forecasting should primarily use valid historical sales.

The system should distinguish:

* completed sales;
* cancelled Orders;
* refunded Orders;
* partially refunded Orders;
* test transactions;
* corrections.

Invalid or non-representative transactions must not automatically be treated as normal demand.

The preprocessing layer must apply deterministic eligibility rules.

---

# 10. Stockout-Aware Forecasting

A critical forecasting rule is:

> Zero sales do not necessarily mean zero demand.

Example:

```text
Expected demand: 100
Available stock: 40
Actual sales: 40
```

The observed sales of 40 must not automatically be interpreted as demand of 40.

The forecasting system should identify periods where:

* stock was insufficient;
* Product was unavailable;
* equipment was unavailable;
* Branch was closed;
* Product was inactive.

Such periods may be:

* excluded;
* censored;
* weighted differently;
* reconstructed;
* explicitly marked.

The chosen treatment must be recorded in forecast metadata.

---

# 11. Menu Availability

Forecasting must account for whether a Product was actually available for sale.

A Product that was inactive for a period should not automatically be interpreted as having zero customer demand.

Example:

```text
Product:
Jan 1–10 → Active
Jan 11–20 → Inactive
Jan 21–31 → Active
```

The inactive period must be distinguishable from genuine zero demand.

---

# 12. Equipment Availability

Equipment outages may affect observed sales.

Example:

```text
Pizza oven unavailable
        ↓
Pizza sales decrease
```

The system should avoid learning that customers permanently stopped demanding pizza.

Equipment-related availability periods should therefore be represented as explanatory features or excluded from normal demand learning where appropriate.

---

# 13. Price Effects

Historical price is a possible forecasting feature.

Example:

```text
Price increases
      ↓
Demand may decrease
```

The model may use:

* historical price;
* price change;
* relative price;
* discount;
* promotion;
* Branch-specific price.

The model must not assume that price changes always cause a specific demand response.

Forecast output must remain predictive rather than claiming causality.

---

# 14. Discount and Promotion Effects

Discounts may temporarily change demand.

The forecasting system should distinguish:

```text
Normal sales
vs
Discounted sales
```

Where sufficient data exists, discount information may become a model feature.

Historical discount information must come from authoritative Order financial snapshots.

---

# 15. Seasonality

Forecasting should consider recurring patterns such as:

* day of week;
* week of month;
* month;
* season;
* holidays;
* special dates;
* business operating patterns.

Example:

```text
Monday ≠ Friday
Winter ≠ Summer
Normal day ≠ Holiday
```

Seasonality must be learned from available data rather than assumed universally.

---

# 16. Time Features

Possible temporal features include:

* date;
* day of week;
* weekend indicator;
* month;
* week number;
* holiday indicator;
* season;
* days since Product activation;
* days since price change;
* days since menu change.

Only relevant and validated features should be included in production models.

---

# 17. Branch-Level Differences

Different Branches may have substantially different demand.

Examples:

```text
Branch A → high lunch demand
Branch B → high evening demand
Branch C → low weekend demand
```

The forecasting system must not blindly apply one Branch's demand pattern to another.

Branch-aware features or hierarchical models may be used.

---

# 18. Business-Level Aggregation

Business-level forecasts may be calculated from Branch-level forecasts.

Example:

```text
Branch A → 100
Branch B → 80
Branch C → 120

Business Forecast → 300
```

Aggregation must preserve the underlying Branch scope.

Business-level forecast must not be used to expose another Business's information.

---

# 19. Product-Level Forecast

Product forecasting is the primary operational use case.

Example:

```text
Product: Chicken Burger

Next 7 days:
Day 1 → 80
Day 2 → 75
Day 3 → 91
Day 4 → 86
Day 5 → 104
Day 6 → 121
Day 7 → 115
```

Each prediction must have:

* Product;
* Branch;
* forecast period;
* generated timestamp;
* model version;
* forecast version;
* confidence information.

---

# 20. Category-Level Forecast

Category forecasts may be useful when individual Product history is insufficient.

Example:

```text
Burger Category
      ↓
Expected demand: 420 units
```

Category forecasts must not automatically be interpreted as exact Product quantities.

---

# 21. Raw Material Forecast

Raw-material demand may be derived from expected Product demand.

Example:

```text
Expected Burger Demand
        ↓
Recipe Version
        ↓
Required Meat
Required Bun
Required Sauce
        ↓
Raw Material Demand
```

Recipe versions must be historically correct.

The current Recipe must not be used to reinterpret historical sales.

---

# 22. Recipe-Aware Forecasting

If a Product uses a Recipe Version:

```text
Forecast Product Quantity
        ×
Recipe Component Quantity
        =
Expected Component Demand
```

Recipe yield and shrink/loss rules must be applied according to authoritative inventory configuration.

Forecast calculations must not modify actual inventory.

---

# 23. Semi-Finished Product Forecast

For semi-finished Products:

```text
Finished Product Demand
        ↓
Recipe dependency
        ↓
Semi-Finished demand
```

The forecast may estimate how much semi-finished Product should be prepared.

This remains a recommendation.

It must not automatically create inventory production transactions.

---

# 24. Forecast Output

A forecast result should contain at minimum:

* Forecast UUID;
* Business UUID;
* Branch UUID;
* Product UUID where applicable;
* forecast type;
* forecast period;
* predicted quantity;
* confidence information;
* model UUID;
* model version;
* feature/data version;
* generated timestamp;
* expiration/freshness metadata;
* forecast status.

---

# 25. Forecast Versioning

Forecasts must be versioned.

A new forecast generation must not silently overwrite an existing forecast.

Example:

```text
Forecast v1
   ↓
New data arrives
   ↓
Forecast v2
```

Both versions may remain available according to retention policy.

The currently active forecast must be explicitly identifiable.

---

# 26. Forecast Status

Forecasts may use states such as:

```text
GENERATING
READY
STALE
FAILED
SUPERSEDED
INSUFFICIENT_DATA
```

The exact implementation may simplify these states but must preserve the semantic distinction.

---

# 27. Forecast Freshness

Forecasts are time-sensitive.

A forecast must have freshness metadata.

Example:

```text
Generated:
2026-10-05 02:00

Valid for:
2026-10-05 → 2026-10-11
```

When a forecast becomes outdated, the system must identify it as stale rather than presenting it as current.

---

# 28. Forecast Regeneration

Forecasts may be regenerated when:

* new sales data becomes available;
* major stockout information changes;
* menu configuration changes materially;
* price configuration changes materially;
* model version changes;
* significant data correction occurs;
* scheduled retraining completes.

Regeneration must create a new forecast version.

---

# 29. Forecast Frequency

Operational forecasts should normally be generated at least daily.

Higher-frequency generation may be introduced later where business value justifies the resource cost.

Forecast generation must not compete with POS resources.

---

# 30. On-Demand Forecast

Authorized users may request a forecast manually.

The request must:

* validate permission;
* validate Business/Branch scope;
* validate subscription entitlement;
* validate required data availability;
* create a forecast job where computation is not lightweight.

The user interface should not require waiting for a long-running model.

---

# 31. Forecast Confidence

Every forecast should expose uncertainty information where supported.

Possible representations:

```text
Prediction: 100
Lower bound: 85
Upper bound: 118
Confidence: Medium
```

Confidence must not be interpreted as probability of correctness unless the model explicitly defines that meaning.

---

# 32. Insufficient Data

The system must explicitly identify insufficient data.

Example:

```text
Product created 5 days ago.
Historical data is insufficient.
```

The system must not produce a highly confident forecast merely to fill an empty field.

Possible output:

```text
Status: INSUFFICIENT_DATA
```

---

# 33. Cold Start Strategy

New Business, Branch or Product may have little historical data.

Possible strategies:

1. Business-level baseline;
2. Branch category baseline;
3. Similar Product baseline;
4. Hierarchical forecast;
5. Simple moving average;
6. Rule-based baseline;
7. Insufficient-data state.

The selected strategy must be deterministic and documented.

---

# 34. New Product Forecast

For a new Product:

```text
No Product history
        ↓
Category/Branch baseline
        ↓
Initial forecast
        ↓
Observed sales accumulate
        ↓
Product-specific model becomes possible
```

The system must not falsely represent a baseline estimate as a fully trained Product-specific model.

---

# 35. New Branch Forecast

For a new Branch, forecasting may use:

* Business-level historical patterns;
* similar Branches;
* category-level patterns;
* operating schedule;
* manually configured assumptions where allowed.

The system must clearly distinguish transferred/borrowed patterns from Branch-specific history.

---

# 36. Model Selection

Forecasting must support multiple model families.

Potential models include:

* moving average;
* weighted moving average;
* exponential smoothing;
* seasonal models;
* tree-based regression;
* gradient boosting;
* classical time-series models;
* neural networks;
* hierarchical forecasting;
* ensemble models.

The system must not require advanced models for every Product.

---

# 37. Baseline Models

Every production forecasting problem should have a baseline.

Examples:

```text
Naive forecast
Seasonal naive
Moving average
```

A complex model should be deployed only when it demonstrates meaningful improvement over an appropriate baseline.

---

# 38. Model Selection Criteria

Models should be evaluated using:

* forecast accuracy;
* stability;
* inference cost;
* training cost;
* data requirements;
* interpretability;
* maintenance complexity;
* cold-start behavior.

The most complex model is not automatically the best model.

---

# 39. Accuracy Metrics

Possible forecasting metrics include:

* MAE;
* RMSE;
* WAPE;
* MASE;
* sMAPE where appropriate.

The selected metric must match the business problem.

For sparse demand, metrics that behave poorly around zero must be used carefully.

---

# 40. Business Metrics

Technical model accuracy is not sufficient.

Business evaluation may include:

* stockout reduction;
* waste reduction;
* forecast usefulness;
* purchase planning accuracy;
* preparation accuracy;
* inventory variance reduction.

AI success must be evaluated against operational value as well as statistical metrics.

---

# 41. Forecast Bias

The system should monitor systematic overprediction and underprediction.

Example:

```text
Actual demand: 100
Forecast: 140

Repeated pattern → positive forecast bias
```

Persistent bias may trigger:

* investigation;
* recalibration;
* retraining;
* model replacement.

---

# 42. Outlier Handling

Historical demand may contain unusual events.

Examples:

* unusually large order;
* temporary promotion;
* equipment outage;
* branch closure;
* holiday;
* data correction.

Outliers must not automatically be deleted.

The preprocessing pipeline should classify or weight them according to documented rules.

---

# 43. Missing Data

Missing historical data must be detected.

The system should distinguish:

```text
No sales
vs
No data
vs
Product unavailable
vs
Branch closed
```

These states must not be blindly converted to zero.

---

# 44. Data Corrections

If authoritative historical sales are corrected:

1. correction is recorded by ERP;
2. AI data pipeline detects relevant change;
3. affected forecast becomes eligible for regeneration;
4. new forecast version is created.

The original forecast version remains historical.

---

# 45. Forecast and Inventory

Forecasting may inform inventory planning.

Example:

```text
Forecast Demand
      ↓
Expected Consumption
      ↓
Inventory Planning
      ↓
Purchase Recommendation
```

Forecasting itself must not:

* increase stock;
* decrease stock;
* create purchase transactions;
* modify warehouse quantities.

---

# 46. Forecast and Purchase Recommendation

Purchase Recommendation may consume forecasting output.

However:

```text
Forecast
   ↓
Recommendation
   ↓
Authorized Employee Decision
   ↓
ERP Purchase/Inventory Operation
```

The forecast must not directly trigger procurement.

---

# 47. Forecast and Menu Configuration

Menu changes may affect future demand.

If a Product is:

* activated;
* deactivated;
* made Branch-specific;
* removed from availability;

the forecasting system should account for the configuration's effective period.

Historical demand must remain historically valid.

---

# 48. Forecast and Price Configuration

Price changes may influence predictions.

The forecasting system should use the effective historical price applicable to the relevant period.

Current price must not be applied retroactively to historical sales.

---

# 49. Forecast and Discounts

Historical discount data may be used as a feature.

The forecast system should distinguish:

```text
Base demand
vs
Promotion-influenced demand
```

where enough historical information exists.

---

# 50. Forecast Explainability

Forecast results should provide understandable factors where possible.

Example:

```text
Expected demand increased because:
- Friday pattern is stronger;
- recent sales increased;
- Product is fully available;
- no recent stockout was detected.
```

Explanations must not claim causal certainty when the model only identifies predictive relationships.

---

# 51. Forecast Confidence and Explanation

A forecast explanation should be accompanied by confidence/freshness information where available.

Example:

```text
Forecast: 120 units
Confidence: Medium
Data freshness: 3 hours
Model: Demand-v4
```

This helps users understand whether the result is reliable enough for operational planning.

---

# 52. Branch Scope

A Branch user must only receive forecasts permitted by their Branch scope.

A user with Business-wide permission may view aggregated Business forecasts.

Branch data must never leak across Business boundaries.

---

# 53. Permission Model

Forecast access follows the general authorization model.

Possible permissions include:

* view forecasts;
* view Branch forecasts;
* view Business forecasts;
* request forecast;
* view forecast explanation;
* export forecast;
* manage forecasting configuration.

The exact permissions belong to the central permission architecture.

AI must never grant permissions.

---

# 54. Subscription Entitlement

Forecasting capabilities are subject to subscription entitlement.

When a Business becomes read-only:

* historical forecast data may remain viewable;
* existing forecast results may remain viewable;
* modifying AI configuration is blocked;
* new computationally expensive jobs may be blocked;
* permitted reports/exports remain available.

AI must not bypass subscription restrictions.

---

# 55. Offline Behavior

Forecast generation normally requires server-side AI infrastructure.

Offline POS devices must not depend on a live forecast to:

* create Orders;
* process payments;
* manage cash;
* synchronize transactions.

Previously synchronized forecast results may be cached locally for informational display where appropriate.

Offline devices must not generate authoritative forecast state.

---

# 56. Forecast Failure

If forecast generation fails:

```text
ERP continues normally
       ↓
Forecast status = FAILED
       ↓
Failure logged
       ↓
Retry according to job policy
```

A forecast failure must not block:

* POS;
* payment;
* inventory transaction;
* cash session;
* synchronization;
* authentication.

---

# 57. Stale Forecast Handling

If a fresh forecast is unavailable, the UI must clearly indicate that the result is stale.

The system may show:

```text
Last successful forecast:
Generated 18 hours ago
```

It must not silently present stale predictions as newly generated.

---

# 58. Forecast Job Architecture

Long-running forecast generation should run asynchronously.

Conceptually:

```text
ERP Data
   ↓
AI Data Preparation
   ↓
Forecast Job
   ↓
Model Inference
   ↓
Validation
   ↓
Forecast Version
   ↓
AI Storage
   ↓
ERP UI / Recommendations
```

Job execution belongs to the AI job/pipeline architecture.

---

# 59. Forecast Idempotency

Forecast generation jobs must support idempotency.

Repeated requests for the same:

* Business;
* Branch;
* Product;
* horizon;
* data version;
* model version;

must not create uncontrolled duplicate results.

A unique operation/job UUID should be used where appropriate.

---

# 60. Forecast Concurrency

Concurrent forecast jobs must not corrupt forecast state.

The system should avoid unnecessary duplicate computation.

Possible controls include:

* job keys;
* deduplication;
* model version locking;
* data version locking;
* distributed job coordination.

---

# 61. Forecast Data Lineage

Every production forecast should be traceable to:

```text
Forecast
   ↓
Model Version
   ↓
Feature Version
   ↓
Dataset/Data Snapshot
   ↓
Source ERP Data
```

This lineage is necessary for:

* debugging;
* reproducibility;
* audit;
* model evaluation;
* incident investigation.

---

# 62. Forecast Reproducibility

The system should be able to identify why a forecast was produced.

At minimum, it should retain:

* model version;
* feature version;
* data snapshot/version;
* forecast parameters;
* generation time;
* forecast horizon;
* Business/Branch scope.

Exact bit-for-bit reproducibility is preferred where technically practical but is not required if model/runtime nondeterminism is explicitly documented.

---

# 63. Forecast Retention

Forecast retention should follow AI data lifecycle policy.

Historical forecasts may be retained for:

* evaluation;
* model comparison;
* trend analysis;
* audit;
* debugging.

Retention must respect Business data deletion requirements.

When Business data is permanently deleted, associated forecast data must also become eligible for deletion according to lifecycle policy.

---

# 64. Forecast Monitoring

The system should monitor:

* forecast job success rate;
* generation duration;
* inference duration;
* stale forecast count;
* insufficient-data count;
* model accuracy;
* forecast bias;
* data freshness;
* data quality;
* resource consumption.

These metrics belong to AI observability.

---

# 65. Drift

Demand patterns may change over time.

Potential causes:

* customer behavior changes;
* new competitors;
* menu changes;
* pricing changes;
* seasonality;
* Branch relocation;
* operational changes.

The system should monitor data/model drift.

Drift does not automatically require retraining.

A documented threshold or evaluation process should determine the response.

---

# 66. Retraining Trigger

Retraining may be triggered by:

* scheduled interval;
* accuracy degradation;
* significant drift;
* major business configuration change;
* sufficient new data;
* model lifecycle policy.

Retraining must produce a new model version.

Existing model versions remain immutable.

---

# 67. Champion Model

The production model should have an explicitly identifiable champion version.

Example:

```text
Demand Model v4 → Champion
Demand Model v5 → Challenger
```

The champion is used for normal production forecasting until replaced.

---

# 68. Challenger Evaluation

A challenger model may be evaluated against the champion.

Evaluation may use:

* historical backtesting;
* shadow inference;
* controlled rollout.

A challenger must not automatically become production.

Promotion requires validation according to AI model governance.

---

# 69. Forecast Validation

Before a forecast becomes available to users, the system should validate:

* schema;
* numeric ranges;
* Business scope;
* Branch scope;
* Product validity;
* forecast horizon;
* model version;
* freshness;
* confidence metadata;
* impossible values.

Negative demand predictions must be rejected or safely transformed according to the selected model contract.

---

# 70. Business Rule Validation

AI output must also satisfy business constraints.

For example:

```text
Predicted demand < 0
        ↓
Invalid

Unknown Product
        ↓
Invalid

Deleted Business
        ↓
Invalid
```

AI output validation must occur before persistence or presentation.

---

# 71. Forecast Quantity Semantics

Forecast quantity represents expected demand, not guaranteed sales.

For example:

```text
Forecast = 100
```

does not mean:

```text
100 orders will definitely occur.
```

The UI and API must use terminology that prevents false certainty.

---

# 72. Forecast vs Actual

The system should allow comparison between:

```text
Forecast
vs
Actual Demand
```

Example:

```text
Forecast → 100
Actual   → 92
Error    → 8
```

This comparison is essential for continuous evaluation.

---

# 73. Forecast Evaluation Window

A forecast cannot be fully evaluated until its target period has passed.

Example:

```text
Forecast for Oct 10
        ↓
Oct 10 completes
        ↓
Actual demand available
        ↓
Forecast evaluation
```

Evaluation jobs should run asynchronously.

---

# 74. Forecast Evaluation Storage

Evaluation results should identify:

* forecast version;
* model version;
* Product;
* Branch;
* target period;
* predicted quantity;
* actual quantity;
* error;
* metric;
* evaluation timestamp.

This enables model comparison and monitoring.

---

# 75. Forecast Security

Forecast data may reveal commercially sensitive information.

Security controls must include:

* Business isolation;
* Branch authorization;
* encrypted transport;
* protected storage;
* controlled export;
* audit for sensitive operations.

Forecast data must not be exposed through unrestricted AI prompts or database access.

---

# 76. LLM Interaction

If an LLM explains a forecast:

```text
Forecast Service
      ↓
Validated Forecast
      ↓
Controlled Context
      ↓
LLM
      ↓
Explanation
```

The LLM must not independently query unrestricted ERP data.

The LLM must not modify forecast results.

Prompt injection must not bypass Business or Branch authorization.

---

# 77. Forecast Export

Authorized users may export forecast results where the subscription permits it.

Exports should contain:

* Business/Branch scope;
* forecast period;
* Product;
* predicted quantity;
* confidence information where available;
* model/forecast version where appropriate.

Sensitive exports should be auditable.

---

# 78. Performance Targets

Forecasting must not degrade core ERP performance.

Initial targets:

### Interactive forecast request

```text
p95 ≤ 1.5 seconds
```

for lightweight requests using already-computed results.

### Standard Branch forecast generation

```text
≤ 5 minutes
```

for the defined standard Branch workload.

### Daily batch forecasting

```text
≤ 30 minutes
```

for the standard Business/Branch workload.

### Forecast API availability

```text
≥ 99.5%
```

AI availability targets do not override the requirement that core ERP operations remain available even when AI is unavailable.

---

# 79. Resource Management

Forecast workloads should use controlled resources.

The system should support:

* CPU-first execution;
* worker concurrency limits;
* job priorities;
* Business-level quotas where needed;
* memory limits;
* execution timeouts;
* retry limits.

AI workloads must not starve:

* POS API;
* authentication;
* payment;
* synchronization;
* inventory transactions.

---

# 80. Forecast Priority

Operationally important forecasts may have higher priority.

Suggested priority:

```text
Critical ERP operations
        ↓
Transaction synchronization
        ↓
Operational AI forecasts
        ↓
Model evaluation
        ↓
Training
        ↓
Historical analytics
```

The exact worker policy belongs to the AI job architecture.

---

# 81. Forecast Audit

Important forecast operations should be auditable, including:

* manual forecast request;
* forecast configuration change;
* model promotion;
* forecast export;
* forecast override where permitted;
* forecast deletion under lifecycle policy.

Routine model inference does not necessarily require a full business audit event for every individual prediction if observability already provides sufficient traceability.

---

# 82. Forecast Override

A user may manually override a forecast only if a dedicated business feature explicitly permits it.

An override must:

* preserve the original AI forecast;
* record the new planning value;
* identify the actor;
* record timestamp;
* record reason;
* never modify the underlying model output.

The ERP must clearly distinguish:

```text
AI Forecast
vs
Human Planning Override
```

---

# 83. No Automatic Inventory Mutation

Forecasting must never directly execute:

```text
Stock increase
Stock decrease
Purchase creation
Production transaction
Recipe modification
```

These remain ERP-authoritative operations.

---

# 84. No Automatic Price Modification

Forecast results must not automatically modify:

* Product price;
* Branch price;
* discounts;
* markup.

Dynamic pricing, if introduced later, requires a separate approved architecture.

---

# 85. No Automatic Menu Modification

Forecasting must not automatically:

* activate Product;
* deactivate Product;
* change category;
* change Recipe;
* change Set;
* change Branch availability.

---

# 86. Forecast Data Quality

Before forecasting, the pipeline should check:

* duplicate transactions;
* missing dates;
* invalid quantities;
* impossible negative values;
* missing Product references;
* missing Branch references;
* inconsistent historical state;
* stockout metadata;
* Product availability;
* Business lifecycle state.

Bad data should produce a visible data-quality condition rather than silently generating misleading predictions.

---

# 87. Forecast Eligibility

A Product may be excluded from normal forecasting when:

* it is permanently archived;
* it lacks sufficient data;
* its historical data is invalid;
* its configuration makes forecasting meaningless.

The exclusion reason should be identifiable.

---

# 88. Archived Product Handling

Archived Products retain historical forecasts where required for historical analysis.

They must not automatically receive new operational forecasts.

Historical data must remain available according to lifecycle policy.

---

# 89. Subscription Expiry

After subscription expiry:

* existing forecast history may remain viewable;
* new expensive forecasting jobs may be restricted;
* forecast generation must respect subscription entitlement;
* offline clients cannot bypass restrictions.

Subscription enforcement remains an ERP authorization concern, not an AI decision.

---

# 90. Failure Recovery

If a forecast job fails:

1. Mark job as failed.
2. Preserve failure reason.
3. Do not publish invalid forecast.
4. Retry according to retry policy.
5. Alert if retry threshold is exceeded.
6. Keep previous valid forecast available if still useful.
7. Mark it stale when its freshness period expires.

---

# 91. Previous Forecast Fallback

If the newest forecast fails, the system may continue displaying the latest valid forecast with explicit stale/freshness status.

Example:

```text
Latest forecast generation → FAILED

Previous forecast:
Generated 16 hours ago
Status → STALE
```

The system must not hide the fact that the current generation failed.

---

# 92. Forecast Recovery After Data Correction

When corrected ERP data becomes available:

```text
ERP correction
     ↓
AI data pipeline
     ↓
Affected forecast detection
     ↓
Forecast regeneration
     ↓
New forecast version
```

The original forecast remains historical.

---

# 93. Cross-Business Isolation

Forecasting data must be strictly isolated by Business.

A forecast query must include Business scope.

Cross-Business model training must only use aggregated/anonymized data when explicitly permitted by architecture and data policy.

Business-specific raw operational data must not leak between tenants.

---

# 94. Shared Model vs Business-Specific Model

The system may use:

### Shared Model

One model trained across multiple Businesses using permitted data.

### Business-Specific Model

Model trained for a particular Business.

### Branch-Specific Model

Model trained for a particular Branch.

### Hierarchical Model

Shared/global patterns combined with Business/Branch-specific behavior.

The selection depends on:

* data volume;
* privacy;
* accuracy;
* cost;
* operational complexity.

---

# 95. Default Model Strategy

The default architecture should prefer:

```text
Shared baseline
      ↓
Branch-aware / Business-aware features
      ↓
Business-specific model when justified
      ↓
Branch-specific model only when sufficient data exists
```

This reduces cold-start problems and unnecessary model proliferation.

---

# 96. Forecast Lifecycle

A forecast follows:

```text
REQUESTED
   ↓
GENERATING
   ↓
VALIDATING
   ↓
READY
   ↓
STALE
   ↓
SUPERSEDED
```

Failure may occur during generation or validation:

```text
GENERATING → FAILED
VALIDATING → FAILED
```

Invalid forecasts must never become READY.

---

# 97. Forecast Architecture

The logical architecture is:

```text
                ERP
                 │
        Authoritative Data
                 │
                 ▼
        AI Data Preparation
                 │
                 ▼
       Feature / Data Version
                 │
                 ▼
       Forecasting Model
                 │
                 ▼
        Forecast Inference
                 │
                 ▼
       Output Validation
                 │
                 ▼
        Forecast Version
                 │
          ┌──────┴──────┐
          ▼             ▼
       Reports       Recommendations
          │             │
          └──────┬──────┘
                 ▼
              User
```

---

# 98. Integration Boundaries

Forecasting integrates with:

* ERP Order system;
* Inventory system;
* Product/Recipe system;
* Menu/Pricing system;
* Branch system;
* Subscription system;
* AI Data Architecture;
* AI Model Architecture;
* AI Training/Evaluation;
* AI Inference/Serving;
* AI Monitoring;
* AI Recommendation;
* Reporting.

Each integration must respect the authoritative boundary defined in AI-03.

---

# 99. Forecasting and Reports

Reports may display:

* historical sales;
* forecast demand;
* forecast vs actual;
* forecast accuracy;
* Branch comparison;
* Product demand trends.

Forecast data must be clearly distinguished from historical authoritative financial data.

A forecast must never be presented as actual revenue or actual sales.

---

# 100. Forecasting and Dashboard

Dashboard widgets may show:

* expected demand;
* top expected Products;
* expected stock pressure;
* forecast confidence;
* forecast freshness;
* forecast vs actual.

AI dashboard widgets must be clearly marked as predictive information.

---

# 101. User Experience

The UI should avoid unnecessary complexity.

Example:

```text
Burger
Expected tomorrow: 85
Confidence: High
Previous actual: 79
```

Advanced users may open details:

```text
Model
Forecast version
Data freshness
Confidence interval
Main predictive factors
```

The default POS workflow must not depend on opening AI screens.

---

# 102. Forecast Notifications

Forecasting may enrich notifications.

Examples:

```text
Expected demand is unusually high tomorrow.

Estimated demand:
+32% compared with normal Friday pattern.
```

Such notifications are informational.

They must not automatically modify inventory or purchasing.

---

# 103. Forecast Anomalies

Forecasting may identify unusual future demand.

Example:

```text
Expected demand:
150

Normal range:
80–110
```

The system may generate an insight.

This is not equivalent to an operational alert unless the notification system explicitly classifies it as such.

---

# 104. Forecast Data Lineage and Audit Relationship

Forecast lineage and ERP audit are separate concepts.

ERP audit records business actions.

AI lineage records:

* source data;
* model;
* features;
* inference;
* output version.

Both may be required to investigate an AI-related decision.

---

# 105. Testing Requirements

Forecasting must be tested at multiple levels.

### Unit tests

* feature calculation;
* aggregation;
* stockout handling;
* horizon calculation;
* validation;
* confidence formatting.

### Integration tests

* ERP → AI data pipeline;
* model → inference;
* forecast → recommendation;
* Business scope;
* Branch scope.

### Model tests

* baseline comparison;
* backtesting;
* accuracy;
* bias;
* drift;
* stability.

### Failure tests

* missing data;
* model failure;
* worker failure;
* timeout;
* invalid output;
* stale data.

---

# 106. Backtesting

Before production model promotion, historical backtesting should be performed.

Example:

```text
Historical period
      ↓
Simulated forecast point
      ↓
Prediction
      ↓
Actual demand
      ↓
Metric calculation
```

Backtesting must avoid using future information unavailable at the simulated forecast time.

---

# 107. Leakage Prevention

Forecast training and evaluation must prevent future-data leakage.

Examples of prohibited leakage:

* using future sales;
* using future inventory state;
* using future price;
* using future menu state;
* using future correction data.

Features must reflect the information that would actually have been available at prediction time.

---

# 108. Model Promotion Gate

A model may be promoted only if:

* data quality passes;
* evaluation passes;
* baseline comparison is acceptable;
* business metrics are acceptable where applicable;
* output validation passes;
* security requirements pass;
* resource requirements are acceptable;
* model artifact is versioned.

---

# 109. Forecast Security and Prompt Injection

Forecast data may be exposed through AI assistant interfaces.

The AI assistant must not accept user-provided instructions that attempt to:

* change Business scope;
* access another Branch;
* reveal another Business's forecast;
* modify forecast data;
* bypass subscription;
* expose protected model artifacts.

Authorization must be applied before context is supplied to the LLM.

---

# 110. Forecast Cost Control

Forecasting workloads must have predictable resource usage.

The system should track:

* number of forecast jobs;
* compute duration;
* inference count;
* model usage;
* storage;
* external provider usage where applicable.

High-cost workloads may be subject to quotas.

---

# 111. External Forecasting Providers

External AI/ML services may be used only through controlled adapters.

The ERP must not depend directly on an external provider's internal schema.

The adapter must define:

* request contract;
* response contract;
* timeout;
* retry policy;
* privacy restrictions;
* failure handling.

External provider failure must not block ERP operations.

---

# 112. Forecast Provider Fallback

Where technically practical:

```text
Primary Forecast Model
        ↓
Failure
        ↓
Validated Baseline Model
```

A fallback must be clearly identified.

The system must not present fallback output as if it came from the failed primary model.

---

# 113. Operational Invariants

The following invariants apply to forecasting:

1. ERP remains the source of truth.
2. Forecasts are non-authoritative.
3. Forecasts cannot directly modify inventory.
4. Forecasts cannot directly create purchases.
5. Forecasts cannot directly modify prices.
6. Forecasts cannot directly modify menus.
7. Forecasts cannot directly modify recipes.
8. Forecasts cannot directly modify orders.
9. Forecasts cannot directly modify payments.
10. Forecasts cannot directly modify payroll.
11. Forecasts are Business-scoped.
12. Branch forecasts are Branch-scoped.
13. Historical transaction data is not silently rewritten.
14. Stockout periods are distinguishable from zero demand.
15. Product inactivity is distinguishable from zero demand.
16. Branch closure is distinguishable from zero demand.
17. Equipment outage is distinguishable from normal demand.
18. Historical price is used for the relevant historical period.
19. Historical discounts remain historically accurate.
20. Historical Recipe Versions remain authoritative for historical calculations.
21. Forecasts have identifiable versions.
22. Model versions are immutable.
23. Feature/data versions are identifiable.
24. Forecast lineage is traceable.
25. Invalid forecast output cannot become READY.
26. Negative demand is rejected or handled according to model contract.
27. Insufficient data is explicitly represented.
28. Cold-start forecasts are identifiable as baseline/estimated outputs.
29. Stale forecasts are visibly identified.
30. Failed forecast generation does not block ERP.
31. Previous valid forecasts may remain available with stale status.
32. Forecast regeneration creates a new version.
33. Forecast evaluation uses completed target periods.
34. Forecast evaluation must prevent future-data leakage.
35. Model promotion requires validation.
36. Baseline comparison is required for production model evaluation.
37. Forecast confidence must not be represented as guaranteed correctness.
38. Forecast explanations must not claim unsupported causality.
39. LLMs cannot independently access unrestricted forecast data.
40. Prompt injection cannot bypass authorization.
41. Subscription restrictions apply to forecasting.
42. Offline POS does not depend on live forecasting.
43. AI jobs cannot block critical ERP workers.
44. Forecast resource usage is controlled.
45. Forecast jobs support idempotency.
46. Duplicate forecast computation should be minimized.
47. Forecast failures are observable.
48. Forecast model drift is monitored.
49. Forecast bias is monitored.
50. Forecast accuracy is monitored.
51. Business/Branch isolation is enforced during training and inference.
52. Cross-Business data sharing requires explicit policy authorization.
53. Forecast exports respect permissions.
54. Sensitive forecast exports are auditable.
55. Archived Products do not receive normal operational forecasts.
56. Historical forecasts may remain available according to retention policy.
57. Business deletion applies to associated forecast data.
58. Forecast output does not become an ERP transaction automatically.
59. Human planning overrides preserve the original AI forecast.
60. Forecasting must not reduce POS availability.
61. Forecast generation must not require powerful POS hardware.
62. Current configuration must not reinterpret historical demand.
63. Forecast results must identify their generation time.
64. Forecast results must identify their model version.
65. Forecast results must identify their scope.
66. Forecast results must identify their target period.
67. Forecast results must identify their freshness state.
68. Forecast data quality failures must be visible.
69. External AI provider failure must not block ERP.
70. Fallback forecasts must be identifiable.
71. Forecast history must remain reconstructable.
72. Forecast lineage must remain traceable.
73. Forecasting must remain subordinate to ERP business rules.
74. AI may predict demand, but ERP decides and executes business state.

---

# 114. Related Documents

### AI Architecture

* `docs/04_Architecture/08_AI/01_AI_Architecture_Overview.md`
* `docs/04_Architecture/08_AI/02_AI_Use_Cases_and_Capabilities.md`
* `docs/04_Architecture/08_AI/03_AI_Boundaries_and_Non_AI_Decisions.md`
* `docs/04_Architecture/08_AI/04_AI_Data_Architecture.md`
* `docs/04_Architecture/08_AI/05_AI_Data_Preparation_and_Feature_Engineering.md`
* `docs/04_Architecture/08_AI/06_AI_Model_Architecture_and_Model_Strategy.md`
* `docs/04_Architecture/08_AI/08_AI_Inference_and_Serving_Architecture.md`
* `docs/04_Architecture/08_AI/09_AI_Forecasting_and_Prediction_Architecture.md`
* `docs/04_Architecture/08_AI/10_AI_Anomaly_Detection_Architecture.md`
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

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/04_Architecture/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`

### Business and System Analysis

* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

---

# 115. Status

**AI Architecture Interview:** Completed for the current forecasting architecture scope.

**Document Status:** Proposed.

**Current Document:** `07_AI_Forecasting_and_Demand_Prediction.md`

**Previous Document:** `06_AI_Model_Architecture_and_Model_Strategy.md`

**Next Document:** `08_AI_Inference_and_Serving_Architecture.md`

**AI Architecture Sequence:** Frozen at 28 documents.

**AI Architecture Progress:** 07 / 28

