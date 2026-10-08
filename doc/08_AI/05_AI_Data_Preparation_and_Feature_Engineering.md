# AI Data Preparation and Feature Engineering

**Document ID:** AI-05
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/08_AI/README.md`

---

## 1. Purpose

This document defines how FastFood ERP data is transformed from authoritative ERP data into datasets and features suitable for AI workloads.

The main objectives are:

* reliable AI input;
* reproducible feature calculation;
* Business and Branch isolation;
* historical integrity;
* data quality;
* incremental processing;
* feature versioning;
* prevention of data leakage;
* model-ready datasets;
* efficient processing;
* explainable data lineage.

The feature engineering layer must never modify authoritative ERP data.

---

# 2. Scope

This document covers:

* data preparation;
* extraction;
* normalization;
* cleaning;
* validation;
* aggregation;
* temporal features;
* sales features;
* inventory features;
* pricing features;
* recipe-related features;
* Branch features;
* anomaly features;
* employee/staffing features;
* feature versioning;
* feature lineage;
* feature freshness;
* missing data;
* outlier handling;
* data leakage prevention;
* train/validation/test separation;
* incremental feature computation;
* historical backfill;
* feature storage;
* feature invalidation;
* data quality monitoring;
* Business/Branch isolation;
* performance and SLOs;
* feature engineering invariants.

---

# 3. Architectural Position

The feature engineering layer sits between ERP data and AI models.

```text
Authoritative ERP
       ↓
Data Extraction
       ↓
Data Validation
       ↓
Normalization
       ↓
Aggregation
       ↓
Feature Engineering
       ↓
Feature Dataset
       ↓
Model Training / Inference
```

The feature engineering layer is a derived-data layer.

It is not part of the authoritative transaction path.

---

# 4. Source of Truth

The ERP remains the source of truth for:

* Orders;
* Order Items;
* Payments;
* Refunds;
* Inventory Transactions;
* Stock;
* Products;
* Recipes;
* Menu;
* Prices;
* Cash Sessions;
* Employees;
* Attendance;
* Payroll;
* Reports;
* Business configuration.

Feature engineering must consume these sources.

It must not create an alternative interpretation of authoritative business state.

---

# 5. Feature Engineering Principles

Feature engineering follows these principles:

1. Historical data must retain its original meaning.
2. Features must be deterministic where possible.
3. Feature definitions must be versioned when behavior changes.
4. Features must preserve Business scope.
5. Branch scope must be preserved where relevant.
6. Future information must never leak into historical features.
7. Missing data must not automatically become zero.
8. Invalid source data must not be silently corrected by AI.
9. Feature generation must be reproducible.
10. Feature processing must not block ERP transactions.
11. Derived features must have known freshness.
12. Feature lineage must remain traceable.
13. Sensitive data must be minimized.
14. Feature computation must be observable.
15. Features must remain compatible with model versions that consume them.

---

# 6. Source Data Extraction

Feature pipelines may obtain data through:

* controlled application services;
* database read models;
* event streams;
* outbox events;
* scheduled extraction;
* incremental change tracking;
* approved analytical queries.

Direct uncontrolled access to the production transaction layer is prohibited.

---

# 7. Extraction Boundary

The extraction layer should expose only data required for AI processing.

Example:

```text
Order
    ↓
Order AI Projection
    ↓
Feature Pipeline
```

rather than:

```text
AI
    ↓
Entire Order Database
```

This reduces:

* unnecessary data exposure;
* query load;
* accidental coupling;
* security risk.

---

# 8. Extraction Modes

Feature extraction may operate in several modes.

### 8.1. Initial Backfill

Used when a new AI capability is introduced.

```text
Historical ERP
    ↓
Backfill
    ↓
Feature Dataset
```

### 8.2. Incremental Processing

Used for newly committed data.

```text
Last Position
    ↓
New ERP Data
    ↓
Feature Update
```

### 8.3. Scheduled Recalculation

Used when features need periodic recomputation.

### 8.4. Full Rebuild

Used after major feature definition changes or recovery.

---

# 9. Incremental Processing

Incremental processing should be the default for operational AI pipelines.

The pipeline should maintain a processing position such as:

```text
last_processed_event
last_processed_timestamp
last_processed_transaction_id
```

The selected mechanism depends on the source architecture.

---

# 10. Idempotent Processing

Feature processing must be idempotent.

If the same source event is processed twice:

```text
Source Event
   ↓
Feature Update
```

must not create duplicate logical feature records.

Operation UUIDs or deterministic source keys should be used where appropriate.

---

# 11. Business Isolation

Every feature record must retain Business identity.

Minimum scope:

```text
business_uuid
```

Where Branch-specific:

```text
business_uuid
branch_uuid
```

A feature pipeline must never accidentally aggregate multiple Businesses together.

---

# 12. Branch Isolation

Branch-level features must be calculated independently.

Example:

```text
Business A

Branch A
 ├── Sales Features
 ├── Inventory Features
 └── Demand Features

Branch B
 ├── Sales Features
 ├── Inventory Features
 └── Demand Features
```

Business-level features may aggregate Branches only within the same Business.

---

# 13. Product Scope

Product-level features should preserve:

```text
business_uuid
branch_uuid
product_uuid
```

where the feature is Branch-specific.

Global Product features may omit Branch only when the calculation is explicitly Business-wide.

---

# 14. Time Semantics

Time is a fundamental part of feature engineering.

Every temporal feature must define:

* timezone;
* source timestamp;
* aggregation period;
* start boundary;
* end boundary;
* inclusive/exclusive behavior.

The Business/Branch operational timezone must be respected.

---

# 15. Historical Cutoff

When calculating a feature for time `T`, only data available at or before the permitted cutoff may be used.

Example:

```text
Feature date = 2026-10-01

Allowed:
2026-09-30 and earlier

Not allowed:
2026-10-02
```

This rule prevents future-data leakage.

---

# 16. Point-in-Time Correctness

Training features must be calculated as they would have been available at the prediction time.

Example:

```text
Prediction Time
      ↓
Available Data
      ↓
Feature
```

not:

```text
Entire Historical Dataset
      ↓
Feature
      ↓
Past Prediction
```

Point-in-time correctness is mandatory for predictive workloads.

---

# 17. Data Leakage

Feature engineering must explicitly prevent:

* future sales;
* future inventory;
* future prices;
* future refunds;
* future configuration;
* future Recipe changes;
* future Branch state;
* future labels.

from entering historical training features.

---

# 18. Data Leakage Example

Incorrect:

```text
Predict sales for Monday
        ↓
Feature uses Monday's final sales
```

Correct:

```text
Predict Monday sales
        ↓
Use information available before prediction cutoff
```

---

# 19. Transaction State Filtering

Feature pipelines must define which transaction states are included.

For sales forecasting, normally only authoritative completed/accepted sales should be counted.

Cancelled, rejected or invalid transactions must follow explicit business rules.

The feature definition must not arbitrarily count every stored Order record.

---

# 20. Refund Handling

Refunds must be treated according to the feature definition.

Possible approaches:

* gross sales;
* net sales;
* refund rate;
* refund amount.

A feature must explicitly define whether refunds are included.

Example:

```text
Net Sales
=
Completed Sales
-
Refund Amount
```

The exact business definition must be documented per feature.

---

# 21. Discount Handling

Discounts should be represented separately where useful.

Possible features:

```text
discount_rate
average_discount_amount
discounted_order_ratio
```

A discount must not be interpreted as a Product price change.

---

# 22. Price Features

Possible pricing features include:

* current effective price;
* historical price;
* average selling price;
* price change count;
* price change magnitude;
* Branch price deviation;
* discount-adjusted price.

Historical calculations must use historical price snapshots.

---

# 23. Sales Features

Examples:

```text
daily_units_sold
daily_order_count
daily_revenue
average_order_value
units_per_order
product_sales_share
category_sales_share
```

These features should use clearly defined aggregation periods.

---

# 24. Rolling Sales Features

Common rolling features include:

```text
rolling_3_day_units
rolling_7_day_units
rolling_14_day_units
rolling_30_day_units
```

The window must not include data after the feature cutoff.

---

# 25. Sales Velocity

Sales velocity may be calculated as:

```text
Sales Velocity
=
Units Sold / Time Period
```

Example:

```text
7-day units sold = 140

Daily velocity = 20 units/day
```

The unit and time period must be part of the feature definition.

---

# 26. Demand Features

Demand-related features may include:

* average daily demand;
* weekday demand;
* weekend demand;
* seasonal demand;
* recent demand trend;
* demand volatility;
* demand growth rate.

Demand features should distinguish actual observed sales from estimated demand where stockouts may have suppressed sales.

---

# 27. Stockout-Aware Demand

Observed sales may underestimate true demand when inventory was unavailable.

Example:

```text
Observed Sales = 10
Stock Available = 0 for several hours
```

The model should not automatically interpret this as low customer demand.

Stock availability may therefore become an important feature.

---

# 28. Inventory Features

Possible inventory features include:

```text
current_stock
average_stock
stock_velocity
days_of_stock_remaining
stockout_frequency
inventory_variance_rate
waste_rate
purchase_frequency
```

The exact definitions must follow the Inventory architecture.

---

# 29. Stock Depletion Feature

A basic depletion estimate may use:

```text
Days of Stock
=
Current Stock / Average Daily Consumption
```

The calculation must handle:

* zero consumption;
* missing consumption;
* insufficient historical period;
* stock adjustments;
* stockouts.

Division by zero must never produce invalid feature values.

---

# 30. Inventory Adjustment Features

Inventory adjustments may be represented as:

```text
adjustment_frequency
adjustment_quantity
adjustment_rate
variance_rate
```

These features can support anomaly detection.

AI must not automatically convert an anomaly into an inventory adjustment.

---

# 31. Waste Features

Possible waste-related features:

```text
waste_quantity
waste_rate
waste_cost
waste_frequency
```

Waste calculation must preserve the applicable Recipe and inventory context.

---

# 32. Recipe Features

Where permitted, Recipe-derived features may include:

* ingredient consumption;
* ingredient ratio;
* expected yield;
* production quantity;
* waste ratio;
* Recipe Version;
* component demand.

Historical inventory deductions must use the Recipe Version applicable at the time.

---

# 33. Recipe Version Awareness

A feature generated from Recipe data must identify the relevant Recipe Version where historical reconstruction requires it.

Changing the current Recipe must not rewrite historical feature meaning.

---

# 34. Menu Availability Features

Possible features:

```text
product_active
branch_product_active
availability_duration
menu_disable_frequency
```

These features can help explain sales changes.

A Product being inactive should not be interpreted automatically as zero customer demand.

---

# 35. Equipment Availability

Equipment-related availability may be used as a feature when the information exists.

Example:

```text
product_available = false
reason = equipment_failure
```

This helps distinguish:

* low demand;
* menu deactivation;
* inventory shortage;
* equipment failure.

---

# 36. Set Features

Set-related features may include:

* Set sales;
* component demand;
* Set availability;
* Set price;
* Set configuration version;
* component stock availability.

Historical Set configuration must be preserved.

---

# 37. Branch Features

Possible Branch-level features:

```text
daily_revenue
daily_order_count
average_order_value
refund_rate
stockout_rate
inventory_variance
product_count
active_product_count
```

Business-level aggregation must not mix data from unrelated Businesses.

---

# 38. Order Type Features

Order type may be useful:

```text
dine_in_ratio
takeaway_ratio
phone_delivery_ratio
```

These may help forecast demand patterns.

---

# 39. Temporal Features

Common temporal features:

```text
hour_of_day
day_of_week
day_of_month
week_of_year
month
quarter
is_weekend
is_holiday
```

Holiday features should use an approved calendar source.

---

# 40. Timezone Handling

Temporal features must use the appropriate Business/Branch timezone.

A server UTC timestamp must not automatically be interpreted as local business time.

The pipeline must define conversion rules explicitly.

---

# 41. Seasonality Features

Seasonality may include:

* weekday;
* weekend;
* month;
* season;
* holidays;
* special business periods.

Seasonality must be based on information that was available at the prediction cutoff.

---

# 42. Business Calendar

Where the Business has special operational periods, feature engineering may incorporate:

* closed days;
* special working hours;
* holidays;
* planned Branch closures.

Future information may only be used when the model is explicitly designed to use known future schedules.

---

# 43. Employee / Staffing Features

Approved staffing-related features may include:

```text
scheduled_employee_count
present_employee_count
shift_count
staffing_ratio
sales_per_employee
```

Individual employee identity should be excluded unless specifically required and authorized.

---

# 44. Payroll Features

AI may use aggregated labor cost features such as:

```text
daily_labor_cost
labor_cost_ratio
labor_cost_per_order
```

Payroll details should be minimized.

Individual salary information must not become a general-purpose model feature.

---

# 45. Cash Features

Approved cash-related features may include:

```text
cash_discrepancy_rate
refund_frequency
cash_session_count
average_session_difference
```

Security-sensitive cash information should not be unnecessarily exposed to AI.

---

# 46. Anomaly Features

Anomaly detection may use features such as:

* unusually high refund amount;
* unusual discount rate;
* unusual sales volume;
* unusual inventory adjustment;
* unusual cash discrepancy;
* unusual transaction frequency.

Anomaly features should describe the observation without automatically declaring misconduct.

---

# 47. Statistical Features

Possible statistical features include:

```text
mean
median
standard_deviation
variance
percentile
coefficient_of_variation
trend_slope
```

Definitions must be consistent across model versions.

---

# 48. Ratio Features

Ratio features must protect against zero denominators.

Example:

```text
refund_rate
=
refund_amount / sales_amount
```

If `sales_amount = 0`, the feature must use an explicitly defined representation such as:

* null;
* not applicable;
* separate zero-sales indicator.

It must not produce `Infinity` or `NaN`.

---

# 49. Missing Values

Missing values must be represented explicitly.

Possible strategies:

* null;
* imputation;
* missing indicator;
* default only where business meaning supports it.

The selected strategy must be part of the feature definition.

---

# 50. Zero Values

Zero is a valid business value when the business meaning is truly zero.

Examples:

```text
units_sold = 0
refund_amount = 0
discount_amount = 0
```

Zero must not be used as a generic replacement for missing data.

---

# 51. Outlier Handling

Outliers should not automatically be deleted.

The pipeline should distinguish between:

* valid unusual business activity;
* erroneous source data;
* operational anomalies;
* data entry errors.

Where possible, outlier handling should preserve the original value and create additional indicators.

Example:

```text
sales_value = 500000
sales_is_outlier = true
```

rather than silently replacing the value.

---

# 52. Source Data Correction

If source ERP data is incorrect:

```text
ERP Correction
    ↓
Authoritative State
    ↓
Feature Recalculation
```

Feature engineering must not directly alter the source record.

---

# 53. Normalization

Data normalization may include:

* unit normalization;
* timestamp normalization;
* identifier normalization;
* categorical normalization;
* numeric scaling where model-specific;
* currency normalization where required.

Normalization rules must be deterministic.

---

# 54. Units

Quantities must preserve their units.

Examples:

```text
kg
g
liter
ml
piece
```

A feature must not combine incompatible units.

Example:

```text
500 g
```

must not be treated as:

```text
500 kg
```

---

# 55. Currency

Financial features must use the applicable currency context.

The system must not silently mix different currencies.

If the product currently supports one Business currency, the feature definition should still preserve currency metadata where useful for future compatibility.

---

# 56. Categorical Encoding

Categorical ERP values may require model-specific representation.

Examples:

* order type;
* product category;
* Branch;
* Product type;
* availability state.

Encoding must remain consistent between training and inference.

---

# 57. Identifier Handling

ERP UUIDs may be used internally for joining and lineage.

Raw UUIDs should not automatically be exposed to external LLMs or user-facing AI output.

Model-specific encoding may use stable internal identifiers where necessary.

---

# 58. Feature Scaling

Numeric scaling should be performed only when required by the selected model.

Possible techniques:

* standardization;
* normalization;
* log transformation;
* robust scaling.

The transformation must be versioned.

---

# 59. Log Transformations

Skewed variables may use logarithmic transformations.

Example:

```text
log(1 + sales)
```

The transformation definition must be stored with the feature version.

Zero and invalid values must be handled explicitly.

---

# 60. Feature Interactions

Derived interaction features may combine multiple inputs.

Example:

```text
price_change × demand
stock_velocity × lead_time
refund_rate × order_count
```

Interaction definitions must remain documented and versioned.

---

# 61. Feature Selection

Only features with a defined business or model purpose should be included.

Avoid unnecessary feature accumulation.

The goal is:

> sufficient information, not maximum information.

---

# 62. Feature Registry

Production features should have a registry or equivalent metadata definition.

A feature definition should include:

* Feature UUID;
* name;
* description;
* source;
* formula;
* unit;
* scope;
* time window;
* freshness;
* version;
* status;
* owner;
* sensitivity classification.

---

# 63. Feature Definition Example

Example:

```text
Feature:
rolling_7_day_units_sold

Scope:
Business + Branch + Product

Source:
Order Items

Window:
Previous 7 completed local calendar days

Unit:
piece

Freshness:
≤ 15 minutes after source refresh

Version:
v1
```

---

# 64. Feature Versioning

A feature version must change when the semantic calculation changes.

Examples:

```text
rolling_7_day_units_sold v1
rolling_7_day_units_sold v2
```

A cosmetic metadata change may not require a new semantic version if it does not affect the calculation.

---

# 65. Feature Status

Possible feature states:

```text
DRAFT
TESTING
ACTIVE
DEPRECATED
RETIRED
```

Only `ACTIVE` features should normally be used in production inference.

---

# 66. Feature Compatibility

Model definitions must identify the feature versions they require.

Example:

```text
Model: demand-v3

Required Features:
sales_features-v2
inventory_features-v1
calendar_features-v1
```

A model must not silently consume incompatible feature definitions.

---

# 67. Training Dataset Construction

Training datasets should be constructed from versioned feature definitions.

Conceptually:

```text
Historical Source
      ↓
Point-in-Time Features
      ↓
Training Dataset
      ↓
Labels
      ↓
Model Training
```

---

# 68. Labels

Where supervised learning is used, labels must be generated separately from input features.

Example:

```text
Features:
Data available before 2026-10-01

Label:
Actual sales from 2026-10-01
```

The label must not leak into the input feature set.

---

# 69. Train / Validation / Test Separation

For time-dependent ERP data, temporal splitting should normally be preferred.

Example:

```text
Historical Period
│
├── Training
├── Validation
└── Test
```

Random splitting may produce future-data leakage for time-series problems.

---

# 70. Temporal Dataset Example

Example:

```text
2025-01 → 2026-06
Training

2026-07 → 2026-08
Validation

2026-09
Test
```

The exact periods depend on the model and available data.

---

# 71. Training Data Reproducibility

A training run should identify:

* dataset version;
* feature versions;
* source period;
* model version;
* training configuration;
* code version where applicable.

This allows later investigation.

---

# 72. Inference Feature Generation

Production inference should use the same semantic feature definitions as training.

Differences between training and inference pipelines must be minimized.

Example:

```text
Training:
rolling_7_day_units_v2

Inference:
rolling_7_day_units_v2
```

---

# 73. Training/Serving Skew

The system should detect differences between:

```text
Training Feature Definition
```

and:

```text
Production Feature Definition
```

A model should not be deployed when critical feature semantics are incompatible.

---

# 74. Feature Freshness Metadata

Each feature dataset should expose:

```text
source_data_timestamp
feature_computed_at
feature_version
```

This allows consumers to determine how current the feature is.

---

# 75. Feature Availability

If a feature cannot be calculated reliably:

* inference may be delayed;
* the model may use an approved fallback;
* the result may be marked lower confidence;
* the AI result may be unavailable.

The system must not silently substitute unrelated data.

---

# 76. Cold Start

New Businesses, Branches or Products may lack sufficient history.

The system should detect cold-start conditions.

Possible strategies:

* use Business-level historical patterns;
* use Branch-level patterns where sufficient;
* use category-level patterns;
* use approved default priors;
* return insufficient-data state.

The system must not present a low-confidence cold-start prediction as highly reliable.

---

# 77. New Product Features

A new Product may have:

```text
sales_history = insufficient
```

This is different from:

```text
sales_history = zero
```

The model must preserve the distinction.

---

# 78. New Branch Features

A new Branch may have insufficient historical data.

The feature pipeline should expose:

```text
branch_age
history_days_available
cold_start = true
```

where relevant.

---

# 79. Data Sufficiency

Each model may define minimum data requirements.

Example:

```text
Demand Forecast:
minimum_history_days = 30
```

The exact threshold is model-specific.

If requirements are not met, the AI system should return a controlled insufficient-data result.

---

# 80. Feature Freshness vs Completeness

A recent dataset may still be incomplete.

Example:

```text
Data timestamp = today 12:00
```

but the day is not finished.

Features must distinguish:

* complete period;
* partial period;
* delayed source;
* missing source.

---

# 81. Partial Period Handling

For daily features, incomplete current-day data should not automatically be treated as a complete day.

The feature definition must specify whether:

* current partial day is allowed;
* only completed days are used;
* partial values are normalized.

---

# 82. Holiday Data

Holiday calendars should be versioned where they affect model behavior.

A holiday feature should identify:

* calendar source;
* calendar version;
* date;
* applicable region/business context.

---

# 83. Branch Operating Hours

Operating hours may affect demand features.

Example:

```text
hours_open
sales_per_open_hour
```

Closed periods should not automatically be interpreted as zero demand.

---

# 84. Menu Availability and Demand

When a Product is disabled:

```text
sales = 0
```

does not necessarily mean:

```text
demand = 0
```

Feature engineering should preserve availability context.

---

# 85. Stockout and Demand Separation

When a Product has insufficient stock:

```text
observed_sales < potential_demand
```

may occur.

Demand models should therefore consider:

* stock availability;
* stockout duration;
* observed sales;
* historical demand.

---

# 86. Price Change and Demand

Price changes should be represented separately from sales.

Possible features:

```text
price_change_pct
days_since_price_change
current_price
historical_average_price
```

This allows models to distinguish price effects from demand changes.

---

# 87. Discount and Demand

Discounts may influence demand.

Possible features:

```text
discount_rate
discount_frequency
discounted_units_ratio
```

Discount features must not overwrite base Product price.

---

# 88. Recipe and Cost Features

Where permitted, cost-related features may include:

```text
last_purchase_cost
average_recipe_cost
estimated_unit_cost
cost_change_rate
```

Historical cost values must preserve their effective time.

---

# 89. Purchase Features

Inventory demand models may use:

```text
purchase_quantity
purchase_frequency
supplier_lead_time
days_since_purchase
purchase_cost
```

Only approved and available purchasing data should be used.

---

# 90. Supplier Data

If supplier information becomes part of AI capabilities, the pipeline must preserve:

* Business scope;
* supplier identity;
* Product relation;
* purchase history.

Supplier information should not be exposed unnecessarily to unrelated users.

---

# 91. Feature Aggregation Levels

Features may exist at:

```text
Business
Branch
Category
Product
Recipe
Ingredient
Order Type
Time Period
```

The aggregation level must be explicit.

---

# 92. Aggregation Compatibility

Features from different levels must not be combined incorrectly.

Example:

```text
Branch-level sales
+
Business-level stock
```

must not be treated as if they represent the same scope without explicit transformation.

---

# 93. Hierarchical Features

Hierarchical information may be useful:

```text
Business
  ↓
Branch
  ↓
Category
  ↓
Product
  ↓
Recipe
  ↓
Ingredient
```

The hierarchy must preserve valid parent-child relationships.

---

# 94. Feature Join Rules

Feature joins must use authoritative identifiers.

Examples:

```text
business_uuid
branch_uuid
product_uuid
recipe_version_uuid
date
```

Name-based joins should not be used where stable identifiers exist.

---

# 95. Deleted or Archived Entities

Archived Products and historical entities may remain valid for historical features.

Deletion or archival does not automatically mean historical data should disappear.

Feature logic must distinguish:

* currently active;
* archived;
* historically valid;
* deleted.

---

# 96. Product Identity

Product UUID must remain the stable identity across:

* menu changes;
* price changes;
* category changes;
* archival.

Feature engineering must not create a new Product identity for each price or menu change.

---

# 97. Recipe Identity

Recipe Version should be used when historical Recipe state matters.

A current Recipe must not be substituted into historical feature calculations.

---

# 98. Configuration Awareness

Feature calculations may depend on:

* menu configuration;
* price configuration;
* Branch configuration;
* Business configuration.

The applicable configuration version must be respected for historical periods.

---

# 99. Feature Store

If a dedicated feature store is introduced, it must provide:

* Business isolation;
* Branch isolation;
* feature versioning;
* freshness;
* lineage;
* access control;
* expiration;
* observability.

A feature store remains a derived system.

---

# 100. PostgreSQL Feature Storage

For initial architecture, PostgreSQL may store operational AI features when scale permits.

This can simplify:

* transactions;
* tenant isolation;
* lineage;
* reporting;
* development;
* operations.

A dedicated feature store may be introduced later if justified by workload.

---

# 101. Object Storage

Large training datasets may be stored in object storage.

Examples:

* Parquet;
* CSV where necessary;
* model-ready dataset files.

Object storage paths must preserve Business and dataset scope.

---

# 102. Dataset Naming

Dataset identifiers should be stable and versioned.

Example:

```text
demand-training-business-{business_uuid}-v4
```

The exact physical naming strategy may differ, but logical scope must remain explicit.

---

# 103. Feature Computation Scheduling

Feature computation may be:

* event-triggered;
* periodic;
* batch;
* on-demand.

Scheduling should depend on the feature's freshness requirement.

---

# 104. Event-Driven Feature Updates

Relevant ERP events may trigger incremental feature updates.

Examples:

```text
OrderCompleted
InventoryChanged
RefundCompleted
PriceChanged
MenuConfigurationChanged
CashSessionClosed
```

The originating ERP transaction must not wait for feature computation.

---

# 105. Scheduled Feature Updates

Scheduled jobs are suitable for:

* rolling windows;
* daily aggregations;
* demand features;
* periodic anomaly features;
* model-ready datasets.

Jobs must be retryable and observable.

---

# 106. Feature Recalculation

A feature may require recalculation when:

* source data was corrected;
* Recipe Version changed historically;
* price history was corrected;
* feature definition changed;
* source synchronization completed late.

Recalculation must be scoped to affected data where practical.

---

# 107. Dependency Graph

Feature definitions may have dependencies.

Example:

```text
Order Items
    ↓
Daily Sales
    ↓
Rolling 7-Day Sales
    ↓
Demand Trend
    ↓
Demand Forecast
```

The dependency graph should be known to the pipeline.

A failed upstream feature should prevent invalid downstream features from being treated as valid.

---

# 108. Feature Materialization

Features may be:

### Materialized

Precomputed and stored.

### Computed On Demand

Calculated at request time.

### Hybrid

Frequently used features are materialized while less frequent features are calculated on demand.

The choice should prioritize:

* latency;
* cost;
* freshness;
* simplicity.

---

# 109. Feature Cache

Frequently requested features may be cached.

Cache keys must include sufficient scope:

```text
business_uuid
branch_uuid
product_uuid
feature_version
time_window
```

Cached data must not cross authorization boundaries.

---

# 110. Feature Expiration

Features with limited freshness should have an expiration policy.

Example:

```text
Feature:
current_stock_velocity

TTL:
15 minutes
```

Expired features must not be presented as current.

---

# 111. Data Quality Rules

Feature pipelines should validate:

### Identity

* Business exists;
* Branch belongs to Business;
* Product belongs to Business;
* Recipe Version belongs to Product.

### Time

* timestamp valid;
* period valid;
* timezone valid.

### Numeric

* no unexpected negative values;
* no NaN;
* no Infinity;
* units compatible.

### Completeness

* required fields present.

---

# 112. Data Quality Score

A dataset may expose quality metadata such as:

```text
completeness_score
validity_score
freshness_score
consistency_score
```

The exact scoring method may vary.

AI consumers should be able to determine whether data quality is sufficient.

---

# 113. Feature Quality States

Possible states:

```text
VALID
PARTIALLY_VALID
STALE
INCOMPLETE
INVALID
UNAVAILABLE
```

Only appropriate states should be used for model inference.

---

# 114. Data Quality Alerts

The system should generate operational alerts when:

* source data stops arriving;
* feature refresh fails repeatedly;
* missing data exceeds threshold;
* invalid records increase;
* feature distribution changes unexpectedly.

Alerts should use the existing notification/observability architecture.

---

# 115. Feature Drift Monitoring

The pipeline should monitor important feature distributions.

Examples:

```text
mean
median
standard deviation
missing rate
percentiles
```

Significant changes may indicate:

* business behavior change;
* source issue;
* feature bug;
* model drift.

---

# 116. Feature Engineering Testing

Feature definitions require automated tests.

Tests should verify:

* formula correctness;
* time boundaries;
* timezone behavior;
* missing values;
* zero values;
* negative values;
* Business isolation;
* Branch isolation;
* historical cutoff;
* idempotency;
* version compatibility.

---

# 117. Point-in-Time Tests

For every time-dependent feature, tests should verify that future records cannot influence earlier feature values.

Example:

```text
Feature at T1
```

must remain unchanged when a transaction at:

```text
T2 > T1
```

is later inserted.

---

# 118. Leakage Tests

Automated tests should detect accidental use of:

* future sales;
* future inventory;
* future prices;
* future refunds;
* future configuration;
* future labels.

This is a mandatory model-data quality control.

---

# 119. Feature Contract Tests

A feature contract should define:

```text
name
type
unit
scope
nullability
range
freshness
version
```

Model pipelines should validate the contract before inference.

---

# 120. Feature Engineering Performance

Feature processing must not interfere with:

* POS;
* payment;
* cash sessions;
* inventory;
* authentication;
* synchronization.

Heavy processing should run asynchronously.

---

# 121. Feature Processing SLOs

Initial targets:

| Operation                                      |                               Target |
| ---------------------------------------------- | -----------------------------------: |
| Incremental feature update after source commit |                          p95 ≤ 5 min |
| Standard daily feature refresh                 |                             ≤ 15 min |
| Standard rolling-window recalculation          |                             ≤ 30 min |
| Initial Business historical backfill           | ≤ 2 hours for normal initial dataset |
| Feature contract validation                    |                            p95 ≤ 1 s |
| Feature lookup for inference                   |                         p95 ≤ 100 ms |
| Failed feature job detection                   |                              ≤ 1 min |

These are initial architecture targets and should be validated against production workloads.

---

# 122. Resource Isolation

Feature processing should use controlled resources.

AI feature jobs must not consume all:

* database connections;
* worker slots;
* CPU;
* memory;
* disk I/O.

The ERP transaction path always has priority.

---

# 123. Backpressure

When AI processing falls behind:

* queue depth should increase visibly;
* new AI jobs may be delayed;
* low-priority processing may be throttled;
* core ERP operations must remain unaffected.

The system must prefer delayed AI results over degraded POS performance.

---

# 124. Feature Pipeline Recovery

If a feature job fails:

```text
Failure
  ↓
Retry
  ↓
Recovery
  ↓
Feature Validation
  ↓
Resume
```

Repeated failure should move the feature job into an observable failed state.

---

# 125. Feature Checkpointing

Long-running feature jobs should support checkpoints where practical.

Example:

```text
Business A
 ├── Branch 1 ✓
 ├── Branch 2 ✓
 ├── Branch 3 ✗
```

Recovery should avoid unnecessarily repeating successfully processed work.

---

# 126. Historical Backfill Isolation

Historical backfills must be isolated from normal operational workloads.

Possible techniques:

* worker queues;
* scheduled low-priority jobs;
* read replicas if introduced later;
* controlled DB resource limits;
* batch processing.

The initial architecture should prefer simplicity before introducing unnecessary infrastructure.

---

# 127. Feature Rebuild

A complete feature rebuild may be required after:

* feature definition change;
* major source correction;
* migration;
* data recovery;
* model requirements change.

Rebuilds must produce a new feature version when semantic meaning changes.

---

# 128. Feature Rollout

New feature versions should follow controlled rollout:

```text
Draft
 ↓
Testing
 ↓
Shadow / Validation
 ↓
Active
 ↓
Old Version Deprecated
```

The old feature version should remain available while required by existing models.

---

# 129. Feature Deprecation

A feature should be deprecated before removal when:

* models no longer depend on it;
* reports no longer require it;
* retention period is complete.

Removing a feature must not break historical model reproducibility where required.

---

# 130. Feature Ownership

Each production feature should have an identifiable owner or responsible subsystem.

Ownership includes:

* definition;
* quality;
* documentation;
* versioning;
* lifecycle;
* incident response.

---

# 131. Feature Documentation

Every important feature should document:

* business meaning;
* technical calculation;
* source;
* scope;
* time window;
* unit;
* null behavior;
* freshness;
* version;
* dependencies;
* consumers.

---

# 132. Data Preparation for LLM

LLM workloads use different preparation techniques from numerical models.

Preparation may include:

* controlled document extraction;
* summarization;
* metadata tagging;
* chunking;
* permission metadata;
* Business/Branch scope;
* source references.

Raw ERP tables should not simply be inserted into LLM context.

---

# 133. Document Chunking

When documents are used for retrieval:

each chunk should retain:

* source document;
* source section;
* Business scope where applicable;
* Branch scope where applicable;
* permission scope;
* version;
* source timestamp.

---

# 134. Embedding Preparation

Embedding input should contain only approved textual content.

Sensitive or irrelevant information should be removed before embedding.

Embeddings must retain enough metadata for authorization filtering.

---

# 135. Embedding Versioning

Embeddings should identify:

* embedding model;
* embedding version;
* source version;
* creation time.

Changing the embedding model may require re-embedding.

---

# 136. Feature Engineering and AI Boundaries

Feature engineering may transform data but may not:

* approve a transaction;
* create an order;
* modify inventory;
* change a price;
* approve a refund;
* modify payroll;
* change permissions;
* alter subscription state.

Those actions remain ERP operations.

---

# 137. Human Interpretation

Feature values should not automatically be interpreted as facts about employee intent or misconduct.

For example:

```text
high_refund_rate
```

is a measurable feature.

It does not by itself mean:

```text
employee_fraud = true
```

Any high-impact interpretation requires separate rules and governance.

---

# 138. Feature Privacy

Feature datasets must not contain unnecessary personal information.

Where aggregation can achieve the same model objective, aggregation should be preferred.

---

# 139. Feature Export

Feature datasets should not normally be exposed directly to ordinary users.

If export is required:

* permission is required;
* Business scope is enforced;
* sensitive fields are filtered;
* export is audited where appropriate.

---

# 140. Feature Security

Feature storage must enforce:

* authentication;
* authorization;
* Business isolation;
* Branch isolation;
* encryption where required;
* secure transport;
* access logging;
* lifecycle controls.

---

# 141. Feature Lineage Example

Example:

```text
Demand Forecast
      ↓
rolling_7_day_units_sold v2
      ↓
daily_units_sold v1
      ↓
Order Items
      ↓
Completed Orders
      ↓
ERP Transaction
```

This lineage should be reconstructable for important production models.

---

# 142. Feature-to-Model Mapping

The system should know which models consume which features.

Example:

```text
demand-v3
 ├── rolling_7_day_units_sold-v2
 ├── rolling_30_day_units_sold-v1
 ├── stock_velocity-v1
 ├── price_change_pct-v1
 └── weekday_demand-v1
```

This mapping is important for safe feature changes.

---

# 143. Feature-to-Use-Case Mapping

Features should also identify their intended AI use cases.

Example:

```text
stock_velocity
 ├── Demand Forecasting
 ├── Stock Depletion Prediction
 └── Purchase Recommendation
```

A feature should not automatically be exposed to every AI capability.

---

# 144. AI Data Preparation Failure Boundary

A failure in data preparation must result in:

```text
Feature Unavailable
```

rather than:

```text
Invented Feature
```

The system must never generate fake business data to satisfy a model input requirement.

---

# 145. Fallback Features

Where a model supports fallbacks, the fallback must be explicitly defined.

Example:

```text
Branch Product Demand
        ↓
Insufficient History
        ↓
Category-level Demand
```

The system should indicate that a fallback was used.

---

# 146. Confidence Metadata

Where feature quality affects model confidence, the inference input may include:

```text
data_quality_score
history_days
missing_rate
freshness
```

The model or application can then appropriately communicate uncertainty.

---

# 147. Feature Freshness and User Interface

The frontend should be able to display freshness when relevant.

Example:

```text
Demand forecast
Updated: 12 minutes ago
```

This prevents users from assuming an old prediction is current.

---

# 148. Feature Pipeline Observability

Metrics should include:

* extraction latency;
* processing latency;
* records processed;
* records rejected;
* feature freshness;
* queue depth;
* failure count;
* retry count;
* data quality score;
* processing lag.

---

# 149. Feature Pipeline Audit

Important changes to feature definitions should be auditable.

Examples:

* feature created;
* feature changed;
* feature deprecated;
* feature activated;
* feature retired;
* feature source changed.

---

# 150. Feature Configuration Concurrency

Concurrent changes to feature definitions must use version checks.

A stale feature definition update must not silently overwrite a newer definition.

---

# 151. Feature Idempotency

Repeated feature processing must not create duplicate logical records.

This applies to:

* event processing;
* scheduled jobs;
* backfills;
* retries;
* recovery.

---

# 152. Feature Dataset Integrity

A dataset version must be internally consistent.

It must not mix:

```text
Feature V1
```

and:

```text
Feature V2
```

for the same semantic field unless explicitly defined.

---

# 153. Feature Compatibility Matrix

Production model deployment should validate:

```text
Model Version
        ↕
Feature Versions
        ↕
Dataset Version
```

An incompatible combination must be rejected.

---

# 154. Feature Lifecycle

A feature follows:

```text
DRAFT
  ↓
TESTING
  ↓
ACTIVE
  ↓
DEPRECATED
  ↓
RETIRED
```

Historical references must remain resolvable while required.

---

# 155. Feature Storage Lifecycle

Feature records may follow:

```text
CREATED
  ↓
VALIDATED
  ↓
ACTIVE
  ↓
SUPERSEDED
  ↓
EXPIRED
  ↓
DELETED
```

The exact states depend on the feature type.

---

# 156. Feature Deletion

Feature deletion must respect:

* model dependencies;
* historical reproducibility;
* Business deletion;
* retention requirements;
* dataset references.

Deleting a feature definition must not make required historical model metadata unintelligible.

---

# 157. Business Deletion

When a Business enters permanent deletion:

Business-specific:

* feature data;
* datasets;
* feature cache;
* embeddings;
* derived training records;

must follow the central lifecycle policy.

---

# 158. Shared Feature Datasets

Shared datasets require special handling.

If multiple Businesses contribute to a dataset:

* raw Business-identifiable records should not be exposed across tenants;
* deletion behavior must be defined;
* dataset rebuildability should be evaluated;
* anonymization/aggregation should be preferred where appropriate.

---

# 159. Data Preparation and Subscription

If subscription entitlement prevents AI processing:

* feature generation may stop;
* queued jobs must respect entitlement;
* cached results must respect visibility rules;
* offline devices must not bypass restrictions.

Historical data remains subject to lifecycle policy.

---

# 160. Feature Engineering and Security

Feature pipelines must treat source data as untrusted from a validation perspective even though it originates from ERP.

The pipeline should validate:

* identifiers;
* scope;
* types;
* ranges;
* timestamps;
* status;
* relationships.

---

# 161. Feature Engineering and Audit

Feature computation should retain enough metadata to answer:

* which source period was used;
* which feature version was used;
* when it was computed;
* which model consumed it;
* whether processing succeeded.

---

# 162. Feature Engineering and Recovery

Recovery priority:

1. authoritative ERP;
2. source projections;
3. dataset definitions;
4. feature definitions;
5. feature data;
6. model inputs;
7. derived outputs.

This keeps the system rebuildable.

---

# 163. Feature Engineering and Model Strategy

Feature engineering must remain independent from a specific model implementation where possible.

A feature should represent a stable business concept.

For example:

```text
rolling_7_day_units_sold
```

should not become:

```text
transformer_input_17
```

just because one model consumes it.

---

# 164. Model-Specific Transformations

Model-specific transformations may exist after shared business features.

```text
Business Feature
       ↓
Model-Specific Transformation
       ↓
Model Input
```

This keeps business semantics separate from model implementation details.

---

# 165. Feature Reuse

Features should be reusable across compatible AI use cases.

Example:

```text
daily_units_sold
```

may support:

* demand forecasting;
* product insights;
* Branch performance;
* anomaly detection.

Reuse must not violate scope or sensitivity rules.

---

# 166. Feature Duplication

Duplicate feature definitions should be avoided.

If two models require the same business metric, they should preferably reference the same feature definition.

---

# 167. Feature Naming

Feature names should be:

* deterministic;
* descriptive;
* stable;
* machine-readable;
* business understandable.

Example:

```text
rolling_7_day_units_sold
```

Avoid:

```text
feature_17
```

for shared production features.

---

# 168. Feature Units

Every numeric feature should define its unit where applicable.

Examples:

```text
units
UZS
kg
hours
percentage
count
days
```

Unit ambiguity is prohibited.

---

# 169. Percentage Features

Percentage values must define representation.

For example:

```text
refund_rate = 0.05
```

may mean 5%.

Alternatively:

```text
refund_rate = 5
```

may mean 5 percentage points.

The chosen representation must be consistent and documented.

---

# 170. Feature Precision

Financial and inventory features must preserve sufficient precision.

Rounding should happen only where business semantics require it.

AI preprocessing must not introduce avoidable rounding errors.

---

# 171. Feature Calculation Currency

Where financial calculations are performed:

* source currency;
* calculation currency;
* rounding rules

must be defined.

The feature pipeline must not silently convert currencies.

---

# 172. Feature Calculation Version

A semantic calculation change requires a new version.

Example:

```text
average_daily_demand-v1
average_daily_demand-v2
```

Both may coexist during migration.

---

# 173. Feature Migration

Feature migration should use controlled rollout.

Recommended:

```text
Old Feature
     ↓
New Feature
     ↓
Parallel Validation
     ↓
Model Migration
     ↓
Old Feature Deprecated
```

---

# 174. Feature Rollback

If a new feature version causes incorrect behavior:

* previous version may remain active;
* affected models may roll back;
* new predictions may be invalidated if necessary;
* historical data must remain attributable.

Rollback must not rewrite ERP history.

---

# 175. Feature Engineering and Reports

Reports may consume feature-derived AI results, but must distinguish:

```text
ERP Actual
```

from:

```text
AI Derived
```

Feature data must not overwrite report source facts.

---

# 176. Feature Engineering and Notifications

If a feature crosses an AI-defined threshold:

```text
Feature
 ↓
AI Model
 ↓
Recommendation/Anomaly
 ↓
Notification
```

The notification should reference the underlying AI result.

---

# 177. Feature Engineering and Human Approval

Features themselves do not require human approval for ordinary computation.

However, AI actions based on those features may require human approval according to governance rules.

---

# 178. Feature Engineering and Offline Operation

Offline-created data should not be incorporated into shared authoritative features until server synchronization validates it.

Local devices may calculate temporary local indicators if required for UX, but these are not authoritative AI features.

---

# 179. Local AI Features

If local/offline AI features are introduced:

* they must be explicitly marked local;
* they must not override server AI results;
* synchronization must reconcile them according to defined rules;
* sensitive data must remain protected.

---

# 180. Feature Engineering and Device Trust

Trusted device status does not automatically grant access to unrestricted feature data.

Device authorization and employee authorization remain separate controls.

---

# 181. Feature Engineering and Encryption

Sensitive feature data should use encryption at rest where required.

Sensitive feature transfers must use secure transport.

Encryption keys must be managed through the central security architecture.

---

# 182. Feature Access API

If features are exposed through an API, the API must enforce:

* authentication;
* Business scope;
* Branch scope;
* permission;
* subscription entitlement;
* feature status;
* freshness.

---

# 183. Feature API Response

A production feature response may include:

```text
feature_name
feature_version
value
unit
computed_at
source_timestamp
quality_status
```

Internal implementation details should not be exposed unnecessarily.

---

# 184. Feature Pipeline Documentation

Every production feature pipeline should document:

* inputs;
* transformations;
* outputs;
* dependencies;
* schedule;
* freshness;
* failure handling;
* retention;
* ownership.

---

# 185. Feature Engineering Checklist

Before activating a production feature, verify:

* [ ] source defined;
* [ ] Business scope defined;
* [ ] Branch scope defined;
* [ ] time semantics defined;
* [ ] unit defined;
* [ ] null behavior defined;
* [ ] zero behavior defined;
* [ ] outlier behavior defined;
* [ ] freshness defined;
* [ ] version assigned;
* [ ] lineage defined;
* [ ] tests created;
* [ ] leakage tests created;
* [ ] authorization reviewed;
* [ ] lifecycle defined;
* [ ] observability defined;
* [ ] rollback strategy defined.

---

# 186. System Invariants

The following invariants apply to AI Data Preparation and Feature Engineering:

1. Feature engineering never modifies authoritative ERP data.
2. ERP remains the source of truth.
3. Every tenant-scoped feature preserves Business identity.
4. Branch-scoped features preserve Branch identity.
5. Cross-Business aggregation is prohibited unless explicitly approved.
6. Historical features use point-in-time correct data.
7. Future information must not leak into historical features.
8. Feature definitions are deterministic where practical.
9. Feature semantics are versioned when they change.
10. Feature calculations preserve historical Recipe Versions where required.
11. Historical prices use historical price context.
12. Current prices do not rewrite historical features.
13. Product identity remains stable.
14. Archived Products may remain valid historical feature sources.
15. Missing data is not automatically treated as zero.
16. Zero is not automatically treated as missing.
17. Invalid numeric values such as NaN or Infinity are prohibited from production features.
18. Division by zero must be explicitly handled.
19. Incompatible units cannot be combined.
20. Currency context must be preserved.
21. Feature scope must be explicit.
22. Feature time windows must be explicit.
23. Feature freshness must be measurable.
24. Feature lineage must be traceable.
25. Feature versions must be identifiable.
26. Model-to-feature compatibility must be validated.
27. Training and inference semantics must remain compatible.
28. Training features must not contain future labels.
29. Temporal datasets must prevent future-data leakage.
30. Feature processing must be idempotent.
31. Retries must not create duplicate logical features.
32. Incremental processing must maintain a recoverable checkpoint.
33. Feature processing must not block core ERP transactions.
34. AI backpressure must not degrade POS performance.
35. Feature jobs must be observable.
36. Failed feature jobs must be recoverable.
37. Data quality failures must not produce fabricated values.
38. Insufficient data must be explicitly represented.
39. Cold-start conditions must be detectable.
40. Partial periods must not be confused with complete periods.
41. Stockouts must be distinguishable from low demand where required.
42. Product inactivity must not automatically mean zero demand.
43. Equipment failure must remain distinguishable from low demand.
44. Discounts remain separate from base Product price.
45. Inventory cost remains separate from selling price.
46. Recipe changes do not rewrite historical feature meaning.
47. Set configuration changes do not rewrite historical Set data.
48. Employee personal data must be minimized.
49. Payroll data must be minimized and permission-controlled.
50. Security-sensitive credentials are never feature inputs.
51. Feature caches preserve Business and Branch scope.
52. Feature API access follows authorization.
53. Feature exports follow authorization.
54. Feature storage follows lifecycle rules.
55. Business deletion applies to Business-owned feature data.
56. Shared datasets require explicit deletion/lifecycle handling.
57. AI feature data must not become a hidden second ERP.
58. Feature-derived values are not automatically authoritative facts.
59. Feature changes do not reinterpret historical predictions.
60. Feature rollback does not rewrite ERP history.
61. Feature rebuilds are isolated from critical ERP workloads.
62. Feature backfills are controlled and observable.
63. Feature dependencies are explicit.
64. Upstream feature failure prevents invalid downstream data from being treated as valid.
65. Feature quality state must be visible to AI consumers where relevant.
66. Feature freshness metadata must be preserved.
67. Feature definitions must document null and zero behavior.
68. Feature units must be explicit.
69. Feature precision must be sufficient for the business domain.
70. Feature transformations must be reproducible where required.
71. Dataset versions must be identifiable.
72. Training datasets must be reconstructable where practical.
73. AI-specific transformations remain separate from shared business features.
74. Shared features should not be duplicated without justification.
75. Feature naming must remain stable and descriptive.
76. Feature ownership must be identifiable.
77. Feature definition changes must be auditable.
78. Feature version changes must be controlled.
79. Feature deployment must validate model compatibility.
80. Feature deprecation must consider dependent models.
81. Retired features must not break required historical reproducibility.
82. Local/offline feature calculations are not authoritative server features.
83. Offline data becomes shared AI input only after authoritative synchronization.
84. Trusted device status does not bypass feature authorization.
85. External AI providers receive only approved feature data.
86. Feature data must remain protected during transport and storage.
87. Feature pipeline resource consumption must be controlled.
88. Feature refresh must not block POS.
89. AI freshness may be delayed when necessary to protect ERP correctness.
90. Feature engineering must preserve the boundary between business facts and AI-derived information.

---

# 187. Related Documents

## Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

## System Analysis

* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_System.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

## Database

* `docs/04_Architecture/07_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/04_Architecture/07_Database/08_Product_and_Category_Data_Model.md`
* `docs/04_Architecture/07_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/04_Architecture/07_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/04_Architecture/07_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/04_Architecture/07_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/07_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/07_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/07_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/04_Architecture/07_Database/30_Database_Invariants_and_Guardrails.md`

## Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/05_Repository_and_Data_Access.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

## AI

* `docs/04_Architecture/08_AI/01_AI_Architecture_Overview.md`
* `docs/04_Architecture/08_AI/02_AI_Use_Cases_and_Capabilities.md`
* `docs/04_Architecture/08_AI/03_AI_Boundaries_and_Non_AI_Decisions.md`
* `docs/04_Architecture/08_AI/04_AI_Data_Architecture.md`
* `docs/04_Architecture/08_AI/06_AI_Model_Architecture_and_Model_Strategy.md`
* `docs/04_Architecture/08_AI/07_AI_Training_and_Evaluation_Architecture.md`
* `docs/04_Architecture/08_AI/08_AI_Inference_and_Serving_Architecture.md`
* `docs/04_Architecture/08_AI/09_AI_Forecasting_and_Prediction_Architecture.md`
* `docs/04_Architecture/08_AI/10_AI_Anomaly_Detection_Architecture.md`
* `docs/04_Architecture/08_AI/11_AI_LLM_and_Natural_Language_Architecture.md`
* `docs/04_Architecture/08_AI/12_AI_Prompt_Context_and_Guardrails.md`
* `docs/04_Architecture/08_AI/13_AI_Recommendation_Architecture.md`
* `docs/04_Architecture/08_AI/14_AI_Model_Monitoring_and_Drift_Architecture.md`
* `docs/04_Architecture/08_AI/15_AI_Experimentation_and_A_B_Testing.md`
* `docs/04_Architecture/08_AI/16_AI_Feature_and_Model_Registry.md`
* `docs/04_Architecture/08_AI/17_AI_Job_and_Pipeline_Architecture.md`
* `docs/04_Architecture/08_AI/18_AI_Evaluation_Metrics_and_Benchmarking.md`
* `docs/04_Architecture/08_AI/19_AI_Output_Validation_and_Confidence.md`
* `docs/04_Architecture/08_AI/20_AI_Explainability_and_Interpretability.md`
* `docs/04_Architecture/08_AI/21_AI_Security_and_Data_Privacy.md`
* `docs/04_Architecture/08_AI/22_AI_Governance_and_Human_Approval.md`
* `docs/04_Architecture/08_AI/23_AI_External_Provider_Integration.md`
* `docs/04_Architecture/08_AI/24_AI_Cost_and_Resource_Management.md`
* `docs/04_Architecture/08_AI/25_AI_Failure_Recovery_and_Resilience.md`
* `docs/04_Architecture/08_AI/26_AI_Deployment_and_Runtime_Architecture.md`
* `docs/04_Architecture/08_AI/27_AI_Testing_and_Quality_Assurance.md`
* `docs/04_Architecture/08_AI/28_AI_Operations_and_Observability.md`

---

# 188. Status

**AI Architecture Sequence:** Frozen at 28 documents.

**Completed AI Documents:** 01–05.

**Current Document:** `05_AI_Data_Preparation_and_Feature_Engineering.md`

**Document Status:** Proposed v1.0

**Next Document:** `06_AI_Model_Architecture_and_Model_Strategy.md`

