# AI Use Cases and Capabilities

**Document ID:** AI-02
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/08_AI/01_AI_Architecture_Overview.md`

---

## 1. Purpose

This document defines the AI use cases and capabilities supported or planned for FastFood ERP.

The purpose is to establish:

* which business problems AI may solve;
* which AI capabilities are currently relevant;
* what data each capability may consume;
* what type of result it produces;
* whether the result is informational, predictive or recommendational;
* whether processing is synchronous or asynchronous;
* what the AI capability is explicitly prohibited from doing.

This document defines **AI capability scope**, not detailed model implementation.

Model selection, data preparation, training, inference, security, monitoring and deployment are defined in separate AI architecture documents.

---

## 2. AI Capability Philosophy

FastFood ERP uses AI to improve business understanding and decision-making.

The primary AI value areas are:

1. Forecasting
2. Inventory intelligence
3. Anomaly detection
4. Business insights
5. Recommendations
6. Natural-language business assistance

The system does not use AI merely because an operation can technically be automated.

AI should be introduced where it provides measurable value beyond deterministic ERP rules.

---

## 3. AI Capability Boundary

The overall relationship is:

```text
ERP
 │
 │ Authoritative Data
 ▼
AI
 │
 ├── Prediction
 ├── Detection
 ├── Insight
 └── Recommendation
 │
 ▼
Human / ERP Rule
 │
 ▼
Business Action
```

AI does not become the authoritative source of:

* orders;
* payments;
* inventory;
* payroll;
* permissions;
* subscriptions;
* historical transactions;
* financial totals.

---

## 4. Capability Classification

Every AI capability should be classified into one of the following categories.

### 4.1. Predictive

Attempts to estimate a future or unknown value.

Examples:

* tomorrow's demand;
* expected stock depletion;
* expected sales.

### 4.2. Analytical

Finds patterns in existing data.

Examples:

* unusual sales;
* branch performance patterns;
* product trends.

### 4.3. Recommendational

Suggests a possible action.

Examples:

* purchase quantity;
* preparation quantity;
* replenishment timing.

### 4.4. Generative

Produces natural-language content.

Examples:

* report summaries;
* explanations;
* business answers;
* natural-language recommendations.

### 4.5. Classification

Assigns a category or state.

Examples:

* normal/anomalous;
* low/medium/high demand;
* operational risk level.

---

# 5. Capability Overview

The initial AI capability set is:

| Capability                          | Type                  | Priority | Initial Mode |
| ----------------------------------- | --------------------- | -------: | ------------ |
| Sales Forecasting                   | Predictive            |     High | Batch        |
| Product Demand Forecasting          | Predictive            |     High | Batch        |
| Inventory Demand Prediction         | Predictive            |     High | Batch        |
| Purchase Recommendation             | Recommendational      |     High | Batch        |
| Stock Depletion Prediction          | Predictive            |     High | Batch        |
| Inventory Anomaly Detection         | Analytical            |     High | Batch        |
| Cash/Refund Anomaly Detection       | Analytical            |   Medium | Batch        |
| Sales Anomaly Detection             | Analytical            |   Medium | Batch        |
| Branch Performance Insights         | Analytical            |     High | Batch        |
| Product Performance Insights        | Analytical            |     High | Batch        |
| Business Recommendations            | Recommendational      |   Medium | Batch        |
| Natural-Language Business Assistant | Generative            |   Medium | Online       |
| Report Explanation                  | Generative            |   Medium | Online/Batch |
| AI Notification Enrichment          | Generative/Analytical |   Medium | Async        |

Priority may change after actual product usage and measurable business value.

---

# 6. Sales Forecasting

## 6.1. Purpose

Predict future sales for a Business or Branch.

Possible forecasting dimensions include:

* total sales;
* order count;
* product quantity;
* revenue-related metrics;
* time-based demand.

The first implementation should prefer metrics with reliable historical data.

## 6.2. Input Data

Possible inputs include:

* historical Orders;
* Order Items;
* timestamps;
* Branch;
* Product;
* quantity;
* historical menu availability;
* historical price;
* discounts where relevant;
* seasonality;
* day of week;
* holidays where supported.

Historical values must use their historical configuration and transaction snapshots.

## 6.3. Output

Example:

```text
Branch: A

Tomorrow's expected orders:
320

Expected range:
285–355

Confidence:
Medium
```

The exact output format depends on the selected model.

## 6.4. Constraints

Sales forecasting:

* does not create Orders;
* does not change prices;
* does not modify menu configuration;
* does not guarantee future sales.

---

# 7. Product Demand Forecasting

## 7.1. Purpose

Predict demand for individual Products.

Example:

```text
Product:
Chicken Burger

Forecast:
180 units

Forecast horizon:
Tomorrow
```

## 7.2. Use Cases

Demand forecasting may support:

* preparation planning;
* ingredient planning;
* purchasing;
* staffing insights;
* branch planning.

## 7.3. Important Context

The model should consider historical availability.

A Product with zero sales because it was unavailable should not automatically be interpreted as zero customer demand.

The AI data pipeline must distinguish:

```text
No demand
```

from:

```text
Product unavailable
```

where sufficient data exists.

---

# 8. Ingredient Demand Forecasting

Ingredient demand can be derived from:

* Product demand;
* Recipe Versions;
* historical consumption;
* waste/shrinkage;
* preparation patterns.

The architecture should support:

```text
Product Demand
      ↓
Recipe Version
      ↓
Ingredient Demand
```

For semi-finished products:

```text
Finished Product
      ↓
Semi-Finished Product
      ↓
Raw Materials
```

The AI must use the correct historical/effective Recipe Version for the relevant data.

AI must not modify Recipes.

---

# 9. Stock Depletion Prediction

## 9.1. Purpose

Estimate when current stock may become insufficient.

Example:

```text
Ingredient:
Chicken

Current stock:
120 kg

Predicted depletion:
~2.5 days
```

The prediction should consider:

* current stock;
* historical consumption;
* expected demand;
* recipe requirements;
* known operational patterns.

## 9.2. Result

Possible result states:

```text
SAFE
WATCH
LIKELY_SHORTAGE
UNKNOWN
```

The result is informational/predictive.

It does not perform inventory transactions.

---

# 10. Purchase Recommendation

## 10.1. Purpose

Recommend how much of an ingredient or product should be purchased.

Example:

```text
Ingredient:
Chicken

Recommended purchase:
180 kg

Reason:
Expected demand + current stock + historical consumption
```

## 10.2. Inputs

Potential inputs include:

* current stock;
* expected demand;
* historical consumption;
* supplier lead time where available;
* safety stock configuration;
* waste/shrinkage;
* open purchase information where supported.

## 10.3. Output

The AI may produce:

```text
Recommended Quantity
Reason
Confidence
Expected Coverage
```

## 10.4. Boundary

AI recommendation does not:

* create a purchase transaction automatically;
* change stock;
* create an inventory adjustment;
* modify supplier records.

An authorized user or deterministic ERP workflow performs the actual action.

---

# 11. Preparation Recommendation

AI may recommend preparation quantities for products or semi-finished products.

Example:

```text
Expected evening demand:
140 units

Current prepared quantity:
70 units

Suggested preparation:
70 additional units
```

This is particularly relevant for:

* semi-finished products;
* products with preparation lead time;
* predictable daily demand.

The recommendation must remain subject to actual stock and operational constraints.

---

# 12. Inventory Anomaly Detection

## 12.1. Purpose

Detect unusual inventory behavior.

Potential signals include:

* unexpected consumption;
* unusual variance;
* unusual waste;
* abnormal adjustment frequency;
* unexpected stock movement;
* unusual branch-level consumption.

## 12.2. Result

Example:

```text
Inventory anomaly detected

Product:
Chicken

Branch:
Branch A

Observed behavior:
Higher-than-normal consumption

Risk:
Medium
```

AI does not determine that fraud or misconduct definitely occurred.

The result is an anomaly signal requiring appropriate review.

---

# 13. Sales Anomaly Detection

AI may detect unusual sales patterns.

Examples:

* sudden sales decrease;
* unusually high sales;
* unusual product mix;
* abnormal order volume;
* unusual time-of-day pattern.

The system should distinguish between:

```text
Anomaly
```

and:

```text
Confirmed business problem
```

AI identifies unusual behavior; it does not automatically establish the cause.

---

# 14. Cash and Refund Anomaly Detection

AI may analyze authorized financial activity for unusual patterns.

Potential signals:

* unusually large refunds;
* unusually frequent refunds;
* unusual discount patterns;
* abnormal cash discrepancy frequency;
* unusual cashier-level patterns.

Existing deterministic business rules remain authoritative.

For example, if the ERP already defines:

```text
Refund > configured threshold
```

as an alert condition, AI does not replace that rule.

AI may add:

```text
This refund pattern is unusual compared with historical behavior.
```

---

# 15. Branch Performance Insights

AI may analyze Branch-level performance.

Potential insights include:

* sales trend;
* order trend;
* product performance;
* stock efficiency;
* refund pattern;
* inventory variance;
* demand changes.

Example:

```text
Branch A

Sales:
↑ 12%

Order count:
↑ 8%

Refund frequency:
↑ 18%

AI Insight:
Refund activity increased faster than sales.
```

The underlying metrics remain authoritative ERP/reporting data.

AI provides interpretation.

---

# 16. Product Performance Insights

AI may analyze Product performance.

Potential dimensions:

* sales volume;
* demand trend;
* price;
* discount frequency;
* availability;
* stock consumption;
* branch distribution.

Example:

```text
Product:
Chicken Burger

Observation:
Demand increased consistently over the last four weeks.

Recommendation:
Consider increasing preparation capacity.
```

AI must not automatically change the Product configuration.

---

# 17. Business Performance Insights

AI may provide Business-level insights based on authorized aggregated data.

Examples:

* strongest branches;
* weakest branches;
* demand changes;
* product trends;
* inventory risks;
* operational anomalies.

Cross-Branch analysis is permitted only when the user has appropriate Business-level or all-Branch authority.

AI must never infer that a user may access all Branches merely because the AI model has access to them.

---

# 18. Business Recommendations

AI may combine multiple signals to produce recommendations.

Example:

```text
Observation:
Demand is increasing.

Stock:
Low.

Recommendation:
Increase purchase quantity before the weekend.
```

Recommendations should provide supporting context where possible.

A recommendation should not be presented as a guaranteed optimal decision.

---

# 19. Recommendation Priority

Recommendations may have a priority such as:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Priority must not be confused with certainty.

For example:

```text
High Priority + Low Confidence
```

is possible when the potential business impact is high but the prediction is uncertain.

The UI should represent these dimensions separately where appropriate.

---

# 20. Natural-Language Business Assistant

The system may provide a natural-language assistant for authorized users.

Example questions:

> "Bugun qaysi filialda savdo eng past?"

> "Ertaga qaysi mahsulotlarga talab ko‘proq bo‘ladi?"

> "O‘tgan haftaga nisbatan savdo qanday o‘zgargan?"

The assistant should retrieve data through authorized application capabilities rather than unrestricted database access.

---

# 21. Natural-Language Query Types

The initial assistant should focus on business questions that can be mapped to known ERP data.

Examples:

### Reporting

* today's sales;
* monthly sales;
* order count;
* branch comparison.

### Inventory

* current stock;
* low-stock items;
* expected shortage.

### Products

* best-selling products;
* declining products;
* demand trends.

### Operations

* unusual refunds;
* branch anomalies;
* operational changes.

The assistant should not claim to know information that is unavailable from authorized data.

---

# 22. Report Explanation

AI may explain an existing report.

Example:

```text
Report:
Branch sales decreased 9%.

AI explanation:
The main decline occurred during evening hours,
while lunch sales remained relatively stable.
```

The report itself remains authoritative.

AI explanation is an additional interpretation layer.

---

# 23. AI-Generated Summaries

AI may summarize:

* daily reports;
* weekly reports;
* monthly reports;
* branch performance;
* inventory risks;
* operational events.

The summary must not replace the underlying report.

Users must be able to access the original authoritative metrics.

---

# 24. AI Notification Enrichment

AI may enrich deterministic notifications.

Example:

```text
Deterministic event:
Stock below threshold.

AI enrichment:
Based on recent demand, the ingredient may
reach critical shortage within approximately two days.
```

The deterministic alert remains active even if AI enrichment fails.

---

# 25. AI Alert Generation

AI may generate additional alerts when configured.

Examples:

* unusual demand;
* predicted stock shortage;
* unusual branch behavior;
* unusual refund pattern.

AI-generated alerts should contain:

* alert type;
* generation time;
* Business/Branch scope;
* confidence where applicable;
* explanation where useful;
* freshness;
* model information where applicable.

---

# 26. AI Capabilities Not Included in Initial Scope

The following are not part of the initial AI architecture scope unless separately approved:

* autonomous cash management;
* autonomous payment approval;
* autonomous refund approval;
* autonomous payroll modification;
* autonomous inventory adjustment;
* autonomous price modification;
* autonomous menu modification;
* autonomous employee permission changes;
* autonomous subscription changes;
* autonomous financial correction;
* unrestricted ERP database querying by LLM;
* customer-facing AI chatbot;
* autonomous purchasing execution.

These may be considered as future capabilities only through explicit business and system analysis.

---

# 27. Customer-Facing AI

Customer-facing AI is currently out of scope.

The current AI architecture is primarily intended for:

* Owner;
* Manager;
* authorized Business employees.

Customer-facing AI may be introduced later as a separate product capability.

---

# 28. AI and Employee Roles

AI capabilities depend on employee authorization.

Examples:

### Owner

May access:

* Business-level insights;
* Branch comparison;
* financial insights;
* inventory recommendations;
* forecasting.

### Manager

May access only the Branches and capabilities allowed by permissions.

### Cashier

May have limited access to operational AI information if explicitly permitted.

### Cook

May receive preparation-related recommendations if explicitly permitted.

The role itself does not automatically grant every AI capability.

---

# 29. AI Capability Access Model

AI access follows:

```text
Employee
   ↓
Business Context
   ↓
Branch Scope
   ↓
Role Permission
   ↓
Employee Override
   ↓
Subscription Entitlement
   ↓
AI Capability
```

The AI layer must receive the effective authorization context from the application security architecture.

---

# 30. AI Capability and Business Scope

Capabilities may operate at different scopes.

### Business Scope

Examples:

* overall sales forecast;
* Business-wide product trends;
* Branch comparison.

### Branch Scope

Examples:

* branch demand;
* branch stock risk;
* branch anomaly detection.

### Product Scope

Examples:

* product demand;
* product performance.

### Employee Scope

Used only where explicitly authorized and appropriate.

Sensitive employee analytics require additional access control and privacy consideration.

---

# 31. AI Capability Data Freshness

Different capabilities require different freshness.

| Capability                      | Expected Freshness |
| ------------------------------- | ------------------ |
| Real-time/simple anomaly signal | Minutes            |
| Operational insight             | Minutes/Hours      |
| Daily demand forecast           | Daily              |
| Purchase recommendation         | Hours/Daily        |
| Weekly trend analysis           | Daily/Weekly       |
| Monthly business insight        | Daily/Monthly      |
| Historical analysis             | Report-dependent   |

Exact SLOs are defined in:

`28_AI_Deployment_Performance_and_SLO.md`

---

# 32. AI Processing Priority

AI workloads should have priority classes.

Example:

```text
Priority 1
Operational anomaly / critical shortage signal

Priority 2
Daily forecasting

Priority 3
Recommendations

Priority 4
Historical analysis

Priority 5
Large language summaries / non-critical analysis
```

Priority must not cause AI workloads to starve core ERP workers.

---

# 33. AI Result Expiration

Each AI capability should define whether its result expires.

Examples:

```text
Demand Forecast
→ expires when forecast period passes

Stock Prediction
→ expires when significant inventory state changes

Business Insight
→ expires after relevant data changes

Report Summary
→ tied to report version
```

Expired results must not be silently represented as current information.

---

# 34. AI Result Feedback

Users may interact with AI results using actions such as:

* Accept;
* Reject;
* Not useful;
* Incorrect;
* Dismiss;
* Review later.

Feedback may be used to improve evaluation.

Feedback does not automatically modify the underlying ERP data.

---

# 35. AI Capability Dependencies

AI capabilities may depend on existing ERP domains.

Example:

```text
Demand Forecast
 ├── Orders
 ├── Order Items
 ├── Branch
 ├── Product
 └── Historical Availability
```

Inventory recommendation:

```text
Purchase Recommendation
 ├── Current Stock
 ├── Historical Consumption
 ├── Demand Forecast
 ├── Recipe
 ├── Recipe Version
 ├── Lead Time
 └── Safety Stock
```

Anomaly detection:

```text
Inventory Anomaly
 ├── Inventory Transactions
 ├── Stock
 ├── Historical Baseline
 └── Branch
```

---

# 36. AI Capability Independence

Each AI capability should be independently replaceable where practical.

For example:

```text
Demand Forecasting
      ↓
Model A
```

may later become:

```text
Demand Forecasting
      ↓
Model B
```

without changing the Order or Inventory domain.

The capability contract remains stable while the model implementation changes.

---

# 37. AI Capability Lifecycle

Each capability follows:

```text
Proposed
   ↓
Experimental
   ↓
Evaluated
   ↓
Approved
   ↓
Production
   ↓
Monitored
   ↓
Deprecated
   ↓
Retired
```

Not every experimental AI capability must reach production.

---

# 38. AI Capability Evaluation

Before production, a capability should have:

* defined business objective;
* defined input data;
* defined output;
* measurable success criteria;
* acceptable error range;
* security assessment;
* performance expectations;
* fallback behavior;
* monitoring requirements;
* responsible owner.

A model with high technical accuracy but low business value should not automatically be deployed.

---

# 39. AI Capability Success Criteria

Success should be evaluated using both technical and business metrics.

Examples:

### Forecasting

* forecast error;
* forecast coverage;
* stockout reduction;
* preparation waste reduction.

### Recommendations

* recommendation acceptance rate;
* recommendation usefulness;
* inventory improvement.

### Anomaly Detection

* detection precision;
* false-positive rate;
* review usefulness.

### LLM

* answer correctness;
* groundedness;
* authorization correctness;
* hallucination rate;
* response latency.

---

# 40. AI Does Not Replace Deterministic Rules

FastFood ERP already contains deterministic business rules.

Examples:

```text
Stock < required quantity
        ↓
Order blocked
```

AI should not replace this with:

```text
AI thinks stock is probably enough
        ↓
Order allowed
```

Likewise:

```text
Refund permission
```

must remain a deterministic authorization rule.

AI may detect unusual refund behavior, but the permission system remains authoritative.

---

# 41. AI and Historical Data

AI analysis of historical data must preserve historical context.

For example:

If Product price was:

```text
30,000
```

when an Order was created, later changing the Product price to:

```text
35,000
```

must not cause historical AI analysis to reinterpret the original Order as 35,000.

AI must use the historical transaction snapshot.

The same principle applies to:

* Recipe Versions;
* menu configuration;
* Branch price overrides;
* discounts;
* payment data;
* inventory deductions.

---

# 42. AI and Configuration Changes

Configuration changes may affect future AI processing.

Examples:

* new Product;
* new Recipe Version;
* new price;
* Branch activation/deactivation;
* menu availability.

Historical AI results remain associated with their original data/model context.

New processing uses the latest valid configuration according to ERP rules.

---

# 43. AI and Data Quality

AI results depend on data quality.

The AI system should detect or expose relevant data-quality problems such as:

* insufficient history;
* missing observations;
* inconsistent data;
* excessive missing values;
* unavailable Product;
* changed Recipe;
* insufficient Branch activity.

When data is insufficient, the system should prefer:

```text
INSUFFICIENT_DATA
```

over generating a misleading prediction.

---

# 44. AI Result States

A common result state model may include:

```text
PENDING
PROCESSING
READY
STALE
EXPIRED
FAILED
UNAVAILABLE
INSUFFICIENT_DATA
```

The exact state set may be specialized per capability.

---

# 45. AI Explainability

Where practical, AI results should provide a human-readable explanation.

For example:

```text
Recommendation:
Purchase 180 kg chicken.

Main factors:
- expected demand increase;
- current stock;
- recent consumption;
- safety stock.
```

Explanations must not invent reasons that were not actually used by the model or processing pipeline.

---

# 46. AI Result Source Transparency

Users should be able to distinguish:

```text
ERP Fact
```

from:

```text
AI Prediction
```

and:

```text
AI Recommendation
```

Example:

```text
Current stock: 120 kg
[ERP]

Predicted demand: 95 kg
[AI]

Recommended purchase: 80 kg
[AI]
```

This distinction is required for informed business decisions.

---

# 47. AI Capability Security Boundary

Each capability must define:

* allowed users;
* allowed Business scope;
* allowed Branch scope;
* permitted data;
* prohibited data;
* external provider policy;
* audit requirements.

A general-purpose AI assistant must not automatically inherit access to every AI capability.

---

# 48. AI Capability Cost Boundary

Capabilities may have different resource costs.

For example:

```text
Simple anomaly scoring
→ Low cost

Daily forecasting
→ Medium cost

Large historical analysis
→ Higher cost

LLM analysis
→ Variable cost
```

The system should prioritize capabilities that provide measurable business value relative to their cost.

---

# 49. Initial Capability Roadmap

The recommended implementation priority is:

### Phase 1 — Core Intelligence

1. Product Demand Forecasting
2. Sales Forecasting
3. Stock Depletion Prediction
4. Inventory Anomaly Detection
5. Purchase Recommendation

### Phase 2 — Business Intelligence

6. Branch Performance Insights
7. Product Performance Insights
8. Sales Anomaly Detection
9. Business Recommendations

### Phase 3 — LLM

10. Natural-Language Business Assistant
11. Report Explanation
12. AI-generated Summaries

### Phase 4 — Advanced Intelligence

13. AI Notification Enrichment
14. Advanced cross-domain recommendations
15. Additional predictive capabilities

The roadmap is not a commitment to implement every capability immediately.

---

# 50. Initial Out-of-Scope AI Capabilities

The following remain outside the initial implementation:

* customer-facing conversational AI;
* autonomous procurement;
* autonomous pricing;
* autonomous discounting;
* autonomous refund approval;
* autonomous payroll decisions;
* autonomous employee management;
* autonomous permission management;
* autonomous cash management;
* autonomous inventory correction.

These require separate business analysis and explicit approval before implementation.

---

# 51. System Invariants

The following invariants apply to AI use cases and capabilities:

1. Every AI capability must have a defined business purpose.
2. AI capability output must have a defined type.
3. AI predictions are not authoritative ERP facts.
4. AI recommendations are not authoritative business actions.
5. AI insights do not replace authoritative reports.
6. AI cannot bypass employee permissions.
7. AI cannot bypass Business scope.
8. AI cannot bypass Branch scope.
9. AI cannot bypass subscription entitlement.
10. AI cannot modify historical ERP transactions.
11. AI cannot directly modify authoritative inventory state.
12. AI cannot directly modify authoritative financial state.
13. AI cannot approve payments.
14. AI cannot approve refunds unless a future explicitly approved workflow defines such capability.
15. AI cannot modify payroll autonomously.
16. AI cannot modify employee permissions.
17. AI cannot modify subscription state.
18. Core ERP operation must not depend on AI availability.
19. Offline POS operation must not depend on AI availability.
20. AI capabilities must use authorized data.
21. Insufficient data must not be represented as a confident prediction.
22. AI results must have defined freshness semantics where applicable.
23. Historical AI results must remain attributable to their original model/configuration.
24. AI result explanations must not invent unsupported causes.
25. AI-generated content must be distinguishable from ERP facts.
26. AI capability access must follow the effective authorization context.
27. AI-generated notifications must not suppress deterministic ERP alerts.
28. AI recommendations must pass ERP validation before controlled business action.
29. AI capability failure must degrade gracefully.
30. AI resource usage must remain bounded.
31. Production AI capabilities must have measurable evaluation criteria.
32. Production AI capabilities must have monitoring requirements.
33. AI capabilities must have defined ownership.
34. Experimental capabilities must not silently enter production.
35. AI capability replacement must not require modification of authoritative ERP history.
36. AI capability implementation must remain replaceable where practical.
37. AI must not be introduced solely for automation when deterministic logic is safer and sufficient.
38. High-impact AI recommendations require appropriate human or ERP-rule control.
39. AI capability data must respect Business data lifecycle rules.
40. AI use cases must provide measurable business value or operational benefit.

---

# 52. Related Documents

### AI Architecture

* `docs/04_Architecture/08_AI/01_AI_Architecture_Overview.md`
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

### Related ERP Architecture

* `docs/04_Architecture/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/04_Architecture/05_Database/18_Employee_Attendance_and_Payroll_Data_Model.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`

### Backend

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Frontend

* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/16_Reports_and_Dashboard_UI.md`
* `docs/04_Architecture/07_Frontend/17_Notifications_and_Alerts_UI.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`

---

# 53. Status

**Document Status:** Proposed.

**AI Architecture Sequence:** Frozen at 28 documents.

**Completed:** `01_AI_Architecture_Overview.md`

**Current Document:** `02_AI_Use_Cases_and_Capabilities.md`

**Next Document:** `03_AI_Boundaries_and_Non_AI_Decisions.md`

