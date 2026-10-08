# AI Frontend and User Experience

**Document ID:** AI-19
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_AI/README.md`

## 1. Purpose

This document defines the frontend architecture and user experience principles for AI-powered functionality in FastFood ERP.

The objective is to expose AI capabilities through a simple, predictable and safe user experience without making AI a mandatory part of normal ERP operations.

AI functionality must improve decision-making and operational visibility while preserving:

* ERP authority;
* Business and Branch isolation;
* permission boundaries;
* subscription entitlement;
* historical integrity;
* offline continuity;
* performance;
* explainability;
* human control.

The frontend must never treat AI output as automatically authoritative ERP data.

---

## 2. Scope

This document covers:

* AI frontend integration;
* AI navigation and feature placement;
* AI capability visibility;
* AI permissions;
* Business/Branch context;
* AI dashboards;
* predictions;
* recommendations;
* business insights;
* anomaly notifications;
* AI assistant;
* AI-generated explanations;
* asynchronous AI jobs;
* loading states;
* errors and recovery;
* confidence and freshness;
* provenance;
* approval workflows;
* human review;
* AI actions;
* offline behavior;
* caching;
* subscription restrictions;
* accessibility;
* responsive behavior;
* performance;
* frontend security;
* audit visibility.

---

## 3. Core UX Principle

AI must be useful without becoming intrusive.

The primary principle is:

> AI assists the user; the ERP remains the authoritative system.

AI must therefore not:

* replace normal POS workflows;
* block ordinary ERP operations;
* silently change ERP data;
* hide uncertainty;
* present predictions as facts;
* bypass permissions;
* bypass subscription restrictions;
* create unauthorized transactions.

---

## 4. AI as an Optional Capability

AI functionality is an additional capability of the ERP.

Core ERP functionality must continue to work if:

* AI service is unavailable;
* AI model is unavailable;
* AI request fails;
* AI provider is unavailable;
* AI quota is exhausted;
* AI feature is disabled;
* subscription does not include the AI capability.

For example:

```text
AI unavailable
      ↓
POS continues working
Inventory continues working
Cash Session continues working
Orders continue working
Reports continue working
```

AI failure must not become a core ERP failure.

---

## 5. AI UX Architecture

The frontend integrates AI through the Backend API.

```text
User
  ↓
Frontend
  ↓
Backend API
  ↓
AI Application Services
  ↓
AI Runtime / Pipeline
  ↓
AI Model / Provider
```

The frontend must not communicate directly with:

* model providers;
* model runtime;
* training infrastructure;
* feature stores;
* vector databases;
* internal AI workers.

All AI requests pass through the authoritative Backend boundary.

---

## 6. AI Feature Categories

The frontend may expose AI through:

1. Forecasts
2. Inventory intelligence
3. Purchasing recommendations
4. Business insights
5. Anomaly detection
6. Risk indicators
7. Natural-language assistant
8. Report explanations
9. Operational recommendations
10. AI-generated summaries

Each category must have a clear purpose.

AI functionality must not be added merely because an AI model exists.

---

## 7. AI Navigation

AI features may be exposed through:

* Dashboard;
* Reports;
* Inventory;
* Purchasing;
* Notifications;
* dedicated AI workspace;
* contextual assistant.

AI navigation visibility is determined by:

* subscription entitlement;
* employee permissions;
* Business/Branch scope;
* feature availability;
* frontend capability configuration.

The frontend must not show unavailable AI actions as if they were executable.

---

## 8. AI Workspace

A dedicated AI workspace may provide:

* business insights;
* forecasts;
* recommendations;
* anomalies;
* recent AI jobs;
* assistant;
* model/provenance information where appropriate.

The workspace must prioritize actionable information.

It must not become a technical model-management interface for ordinary employees.

---

## 9. Role-Based AI Visibility

AI visibility follows the same authorization architecture as the ERP.

The frontend may hide unavailable features for usability, but hiding is not authorization.

The Backend remains authoritative.

For example:

```text
Owner
→ Business AI insights
→ Branch comparison
→ Forecasts
→ Recommendations

Manager
→ permitted Branch AI information

Cashier
→ only permitted operational AI features

Cook
→ only relevant operational information
```

Exact visibility depends on configured permissions.

---

## 10. Business and Branch Context

AI screens must clearly identify the active context.

Example:

```text
Business: FastFood Network

Branch: Chilanzar

Forecast:
Next 7 days
```

When a user switches Branch:

* AI context must be recalculated;
* cached data must not leak from the previous Branch;
* pending requests must be associated with the original context;
* displayed recommendations must belong to the current scope.

Cross-Branch information requires explicit authorization.

---

## 11. AI Context Switching

A Branch switch must invalidate or replace context-sensitive AI UI state where necessary.

For example:

```text
Branch A selected
      ↓
AI forecast loaded
      ↓
User switches to Branch B
      ↓
Branch A forecast must not remain presented as Branch B data
```

The frontend should display a loading state or clearly preserve the previous result as historical context until the new context is loaded.

It must never relabel old data as belonging to the new Branch.

---

## 12. AI Dashboard Cards

AI dashboard cards may include:

* Sales Forecast;
* Stock Risk;
* Purchase Recommendation;
* Revenue Trend;
* Anomaly Alert;
* Waste Risk;
* Branch Comparison;
* Operational Insight.

Each card should provide:

* title;
* scope;
* period;
* result;
* confidence where applicable;
* freshness;
* source/provenance indicator;
* action or details link where appropriate.

---

## 13. AI vs ERP Facts

The UI must visually distinguish:

**ERP Fact**

from:

**AI Prediction / Recommendation / Interpretation**

For example:

```text
Actual Sales
1,240 orders

AI Forecast
1,310–1,380 orders
```

The frontend must not represent a forecast as if it were historical ERP data.

---

## 14. Confidence

When an AI output has a meaningful confidence measure, the frontend may display it.

Confidence must be explained in understandable terms.

Example:

```text
Forecast confidence: High

Expected demand:
1,300–1,400 units
```

The frontend must not imply that:

```text
80% confidence = 80% probability the prediction is correct
```

unless the underlying model and metric actually support that interpretation.

If confidence is not meaningful or properly calibrated, it should not be displayed.

---

## 15. Freshness

AI outputs must indicate their freshness where stale information could affect a decision.

Examples:

```text
Updated 8 minutes ago
```

or:

```text
Generated today at 09:20
```

For cached predictions, the UI may show:

```text
Cached result
```

where appropriate.

The frontend must not hide materially stale AI information.

---

## 16. AI Provenance

Where useful, the UI should provide a lightweight explanation of where an AI result came from.

Example:

```text
Based on:
- last 30 days of sales
- current inventory
- recent purchasing history
```

Detailed technical provenance remains available to authorized users where required.

Ordinary users should not be forced to understand model internals.

---

## 17. Forecast UX

Forecast screens may provide:

* historical values;
* forecast values;
* forecast period;
* confidence interval;
* model freshness;
* relevant factors;
* warnings.

Example:

```text
Historical
───────────────
Actual sales

Forecast
───────────────
Expected demand
```

Historical and forecast periods must be visually distinguishable.

The user must be able to identify the transition point.

---

## 18. Inventory Intelligence UX

AI inventory features may show:

* predicted stock-out risk;
* expected demand;
* suggested purchase quantity;
* unusual consumption;
* potential waste;
* inventory trend.

AI recommendations must not directly create purchase transactions.

For example:

```text
AI Recommendation

Tomato
Predicted demand: 42 kg
Current available: 18 kg
Suggested purchase: 30 kg

[Review]
```

The user remains responsible for accepting the recommendation.

---

## 19. Purchasing Recommendation UX

A recommendation may contain:

* Product;
* current stock;
* predicted demand;
* recommended quantity;
* expected period;
* reason;
* confidence;
* freshness.

The UI should allow the user to:

* review;
* accept;
* reject;
* ignore;
* open related inventory information.

Acceptance must create a normal ERP operation rather than directly mutating inventory through AI.

---

## 20. Recommendation Lifecycle

Frontend representation may follow:

```text
Generated
   ↓
Displayed
   ↓
Reviewed
   ↓
Accepted / Rejected / Ignored
```

Acceptance does not itself grant additional permission.

The resulting ERP operation must still pass normal authorization and business validation.

---

## 21. AI Anomaly UX

Anomalies should be presented as signals rather than unquestionable facts.

Example:

```text
Possible anomaly

Cash discrepancy is significantly higher
than the recent Branch pattern.

[View details]
```

The UI should provide:

* anomaly type;
* affected scope;
* period;
* severity;
* supporting evidence;
* confidence where meaningful;
* related ERP records.

The user must be able to inspect the underlying authoritative data.

---

## 22. Severity

AI alerts may use levels such as:

* Informational;
* Low;
* Medium;
* High;
* Critical.

Severity must not imply certainty.

A high-severity anomaly can still be a false positive.

---

## 23. AI Insights

AI business insights may summarize:

* sales changes;
* branch performance;
* inventory movement;
* product trends;
* unusual expenses;
* operational patterns.

Insights must distinguish:

```text
Observed fact
```

from:

```text
AI interpretation
```

For example:

```text
Observed:
Burger sales decreased 14%.

AI interpretation:
The decrease appears concentrated on weekdays.
```

The UI should avoid presenting the interpretation as proven causation.

---

## 24. AI Assistant

The AI assistant may provide natural-language interaction with ERP information.

Example:

```text
User:
Why did today's sales decrease?

Assistant:
Sales were lower mainly because...
```

The assistant must respect:

* Business scope;
* Branch scope;
* permissions;
* subscription;
* data access policy;
* context trust levels;
* tool authorization.

The assistant cannot reveal information outside the user's authorized scope.

---

## 25. Assistant Context Indicator

Where useful, the assistant UI should indicate the current context.

Example:

```text
AI Assistant
Branch: Chilanzar
Period: Today
```

This reduces accidental ambiguity.

If the user asks about another Branch without sufficient permission, the request must be rejected or limited by the Backend.

---

## 26. Assistant Answers and Facts

AI-generated answers must distinguish between:

* authoritative ERP facts;
* calculations;
* forecasts;
* recommendations;
* interpretations;
* uncertain statements.

For example:

```text
Actual:
Revenue = 12,400,000

Forecast:
Tomorrow's expected revenue = 11,800,000–12,700,000
```

The UI must not merge these into one indistinguishable value.

---

## 27. Assistant Tool Actions

If the assistant proposes an action, the UI must clearly distinguish:

```text
Recommendation
```

from:

```text
Action
```

The assistant must not silently execute important ERP operations.

Where an AI-assisted action is supported:

```text
AI recommendation
      ↓
User review
      ↓
Normal ERP action
      ↓
Authorization
      ↓
Validation
      ↓
Commit
```

---

## 28. High-Risk AI Actions

AI must not directly execute high-risk operations such as:

* changing Product prices;
* changing Recipes;
* modifying inventory quantities;
* creating financial transactions;
* issuing refunds;
* changing payroll;
* closing Cash Sessions;
* changing permissions;
* changing subscription state;
* deleting Business data.

Any supported workflow must use the ordinary ERP authorization and confirmation flow.

---

## 29. AI Job UX

Long-running AI operations must use asynchronous job UI.

Example:

```text
Generating forecast...

Status:
Queued → Running → Completed
```

The user may leave the page without losing the job.

The frontend retrieves job status through the Backend.

---

## 30. AI Job States

The frontend must support:

```text
CREATED
QUEUED
RUNNING
PAUSED
RETRY_PENDING
SUCCEEDED
FAILED
CANCEL_REQUESTED
CANCELLED
DEAD_LETTERED
```

Each state must have an appropriate user-facing representation.

Internal technical state names do not necessarily need to be exposed directly.

---

## 31. Progress Indicators

If reliable progress information exists, the UI may show it.

If exact progress cannot be measured, the UI must not display fabricated percentages.

Use:

```text
Processing...
```

instead of:

```text
73% complete
```

when the actual percentage is unknown.

---

## 32. AI Loading States

AI interfaces should provide clear loading states.

Recommended states:

* Loading;
* Preparing;
* Generating;
* Refreshing;
* Waiting for result.

The UI should avoid blocking unrelated ERP functionality during AI loading.

---

## 33. AI Failure UX

When an AI request fails, the UI should explain the result without exposing unnecessary infrastructure details.

Example:

```text
AI result is temporarily unavailable.

Your ERP data is safe.

[Retry]
```

Where a cached result remains valid:

```text
Latest available result:
Generated 25 minutes ago.

[Refresh]
```

---

## 34. Partial Failure

AI components must support partial failure.

For example:

```text
Dashboard

Sales report        ✓
Inventory report    ✓
AI forecast         —
AI unavailable
```

The entire dashboard must not fail because one AI card failed.

---

## 35. Retry Behavior

Retry behavior must be bounded.

The frontend should not repeatedly send failed AI requests automatically.

Automatic retry may be used only where the API contract permits it.

User-triggered retry must remain available where appropriate.

---

## 36. Stale Result Handling

A stale AI result may remain visible when useful, but must be labeled.

Example:

```text
Last successful forecast:
2 hours ago

Data may be outdated.
```

Critical decisions must not silently rely on stale results.

---

## 37. Subscription Restrictions

If the Business subscription does not include an AI feature:

* the feature may be hidden;
* or displayed as unavailable;
* historical AI results may remain viewable if policy permits;
* modifying/creating AI jobs must be blocked by Backend.

The frontend must never bypass subscription entitlement.

---

## 38. Read-Only Subscription

When the Business becomes read-only:

* AI-generated historical results may remain viewable according to retention rules;
* new AI jobs must not bypass the read-only state;
* AI recommendations must not create modifying ERP operations;
* cached data must not be used to circumvent subscription restrictions.

---

## 39. Permission Denied UX

Unauthorized AI functionality should produce a clear result.

Example:

```text
You do not have permission to view
AI insights for this Branch.
```

The UI must not reveal restricted data while explaining the denial.

---

## 40. Business Isolation

AI UI must preserve Business isolation.

The frontend must never:

* reuse another Business's AI result;
* display another Business's recommendation;
* expose another Business's job;
* use another Business's cached result.

Business UUID must be part of relevant frontend data state and API context.

---

## 41. Branch Isolation

Branch-scoped AI data must remain Branch-scoped.

A user with Branch A access must not receive Branch B AI results merely because:

* the result is cached;
* the user previously visited Branch B;
* a request was retried;
* the Branch context changed.

---

## 42. AI Cache Safety

Frontend caching must be non-authoritative.

Cache keys must include relevant scope and identity context.

At minimum, cache isolation should account for:

* Business;
* Branch where applicable;
* employee/session context where required;
* AI capability;
* model/pipeline version;
* time/freshness.

Sensitive AI responses should not be stored longer than necessary.

---

## 43. Offline AI Behavior

Offline mode must not assume that the device can generate new server-authoritative AI results.

Offline frontend may display:

* previously synchronized AI results;
* locally cached non-sensitive recommendations where permitted;
* clearly marked stale information.

The frontend must not represent offline cached AI output as current server state.

---

## 44. Offline AI Requests

If an AI request requires server access:

```text
Offline
   ↓
AI request unavailable
   ↓
Show last valid result or explain unavailable state
```

The request must not be silently treated as successful.

---

## 45. AI and POS UX

AI must not slow or block normal POS workflows.

The following must remain independently usable:

* order creation;
* order modification;
* payment;
* Cash Session;
* kitchen workflow;
* synchronization.

AI suggestions may appear contextually but must never interrupt critical POS actions unnecessarily.

---

## 46. AI in POS

AI features in POS must be limited to low-friction assistance.

Examples may include:

* product suggestions;
* demand-aware operational hints;
* anomaly indication.

AI must not introduce mandatory waiting before:

* adding an item;
* accepting an order;
* accepting payment;
* closing a transaction.

---

## 47. Accessibility

AI interfaces must follow the general frontend accessibility architecture.

Requirements include:

* keyboard accessibility;
* screen-reader compatible labels;
* sufficient contrast;
* non-color-only status indicators;
* accessible loading states;
* accessible error messages;
* accessible confidence/freshness information;
* responsive layout.

AI-generated content must remain readable at supported text sizes.

---

## 48. Responsive Design

AI interfaces must support:

* ordinary POS screens;
* office desktops;
* laptops;
* supported tablets where applicable.

Dense AI analytical screens may use responsive layouts.

Critical information must remain readable without excessive horizontal scrolling.

---

## 49. AI Visualization

Charts and visualizations may be used for:

* forecasts;
* historical vs predicted values;
* inventory trends;
* anomaly trends;
* branch comparisons.

Visualizations must clearly distinguish:

* actual;
* predicted;
* recommended;
* uncertain.

A chart must not visually imply certainty that the underlying model does not provide.

---

## 50. Explanation UX

AI explanations should answer:

1. What happened?
2. What does AI think may happen?
3. Why is this being shown?
4. What data influenced the result?
5. What can the user do next?

Explanations must remain concise by default.

Detailed information may be available through expandable sections.

---

## 51. AI Recommendation Detail

A recommendation detail view may include:

```text
Recommendation
───────────────
Product: Chicken

Suggested purchase: 25 kg

Reason:
Expected demand is higher than
current available stock.

Confidence: Medium

Data freshness:
18 minutes ago

[Review]
```

The UI must not claim that the recommendation is guaranteed to be correct.

---

## 52. Human Approval

AI output requiring business action must support human review where required.

Approval UI should clearly identify:

* AI recommendation;
* responsible employee;
* affected Business/Branch;
* proposed change;
* underlying ERP data;
* validation status.

Approval must result in a normal ERP operation.

---

## 53. Rejection

Users may reject recommendations where permitted.

Rejection may optionally include a reason.

The rejection must not alter authoritative ERP data.

Where learning feedback is collected, it must be handled through the AI feedback architecture.

---

## 54. Feedback

The frontend may provide:

* Helpful;
* Not helpful;
* Correct;
* Incorrect;
* Accept;
* Reject.

Feedback must not be interpreted automatically as authoritative business data.

Feedback may become AI training/evaluation data only through approved pipelines.

---

## 55. AI Output Copy

AI output must use careful language.

Preferred:

* “AI predicts...”
* “The system detected a possible anomaly...”
* “Recommended quantity...”
* “Based on recent data...”
* “The available data suggests...”

Avoid unsupported certainty such as:

* “This will definitely happen.”
* “This is certainly the cause.”
* “AI knows that...”

---

## 56. AI Numerical Integrity

Numerical values shown by the frontend must come from structured Backend responses where possible.

The frontend must not parse critical business numbers from free-form AI text when structured data is available.

Examples of structured fields:

```text
amount
quantity
percentage
date
forecast_range
confidence
currency
product_uuid
branch_uuid
```

This reduces formatting and interpretation errors.

---

## 57. Currency and Units

AI financial and inventory outputs must respect Business configuration.

Examples:

* currency;
* quantity unit;
* weight unit;
* volume unit.

The frontend must not silently convert or reinterpret units.

---

## 58. AI Date and Period Context

AI outputs must clearly identify their period.

Examples:

```text
Today
Next 7 days
September 2026
Last 30 days
```

The frontend must use the Business/Branch timezone and Backend-defined period boundaries.

Date ambiguity must be avoided.

---

## 59. AI Refresh

Where manual refresh is available:

* the current scope must be preserved;
* duplicate requests should be prevented where unnecessary;
* refresh must respect rate limits;
* the previous result may remain visible while the new result is loading.

The UI must not flicker unnecessarily.

---

## 60. AI Job Cancellation

Where supported, users may cancel long-running jobs.

Cancellation must be represented clearly:

```text
Cancel requested
      ↓
Cancelled
```

The frontend must not assume cancellation succeeded until confirmed by Backend.

---

## 61. AI History

Authorized users may view historical AI results where useful.

History may include:

* generation time;
* model version;
* pipeline version;
* scope;
* status;
* result;
* freshness;
* related ERP period.

Historical AI results must not overwrite newer results.

---

## 62. Model Version Visibility

Ordinary users do not need to see technical model identifiers by default.

Where provenance is important, the UI may expose:

```text
Model:
Demand Forecast v3
```

Technical details may be available in an advanced information panel for authorized users.

---

## 63. AI Audit Visibility

Users with appropriate permission may inspect relevant AI audit information.

The frontend may display:

* request;
* actor;
* scope;
* model;
* result;
* approval;
* action;
* timestamp.

Sensitive implementation details must remain restricted.

---

## 64. AI Security UX

The frontend must not:

* expose API keys;
* expose provider credentials;
* expose internal model endpoints;
* expose unrestricted tool identifiers;
* allow users to modify authorization context;
* trust client-provided Business/Branch scope.

The frontend is a presentation layer, not the security boundary.

---

## 65. Prompt Injection UX

User-provided content may contain instructions intended to manipulate the AI.

The frontend should not imply that all retrieved content is trusted.

Where relevant, the UI may identify content as:

```text
User-provided
Imported document
External content
System information
```

Security enforcement remains a Backend/application responsibility.

---

## 66. AI Error Classification

Frontend should map AI errors into understandable categories:

* Unauthorized;
* Feature unavailable;
* Validation error;
* Conflict;
* Rate limited;
* Temporary unavailable;
* Timeout;
* Job failed;
* Stale result;
* Provider unavailable.

Internal stack traces must never be shown to normal users.

---

## 67. Network Failure

When network connectivity is lost during an AI request:

* preserve existing UI state;
* show the request status;
* avoid duplicate submission;
* offer retry where safe;
* use cached results where allowed.

A network failure must not create the appearance that an AI action was successfully committed.

---

## 68. Duplicate Submission Protection

The frontend should prevent accidental duplicate AI job creation.

For example:

```text
Generate Forecast
      ↓
Generating...
      ↓
Button temporarily disabled
```

Backend idempotency remains authoritative.

Frontend prevention is only a usability layer.

---

## 69. AI State Management

AI frontend state should distinguish:

* current request;
* previous successful result;
* loading state;
* error state;
* job state;
* freshness;
* scope;
* model version;
* cache state.

A failed refresh must not unnecessarily destroy the last valid result.

---

## 70. AI Component Boundaries

Recommended frontend component boundaries:

```text
AI Workspace
├── AI Dashboard
├── Forecast View
├── Inventory Intelligence
├── Recommendation View
├── Anomaly View
├── Insight View
├── AI Assistant
├── AI Job Status
├── AI Result Card
├── AI Explanation
├── AI Confidence
├── AI Freshness
└── AI Feedback
```

Shared components should be reusable without embedding business-specific authorization logic.

---

## 71. Frontend Layering

AI frontend implementation should follow:

```text
Presentation
    ↓
Feature / Application State
    ↓
AI API Client
    ↓
Backend API
```

The frontend must not contain:

* model inference logic;
* authoritative business rules;
* permission enforcement;
* financial calculations that belong to Backend;
* inventory mutation logic.

---

## 72. API Client

The AI API client is responsible for:

* request serialization;
* response parsing;
* authentication/session integration;
* request correlation;
* idempotency;
* timeout handling;
* error mapping;
* cancellation;
* cache integration where permitted.

The API client must not bypass the common Backend API architecture.

---

## 73. Request Correlation

AI requests should have correlation information where supported.

The frontend may retain:

* request ID;
* job ID;
* correlation ID.

These identifiers help users and support staff trace asynchronous AI operations.

---

## 74. Long-Running Job Notifications

When an AI job completes asynchronously, the frontend may notify the user through the general notification architecture.

Example:

```text
Forecast completed.

[View result]
```

The notification must not reveal information outside the user's authorized scope.

---

## 75. AI Notifications

AI notifications may include:

* anomaly detected;
* forecast ready;
* recommendation available;
* AI job failed;
* AI service temporarily unavailable.

Notifications should not become excessive.

The user should be able to manage relevant notification preferences according to the general notification architecture.

---

## 76. AI Performance Targets

The frontend should preserve the following targets:

| Operation                                |       Target |
| ---------------------------------------- | -----------: |
| AI page initial shell                    |  p95 ≤ 1.5 s |
| AI result card render after data arrival | p95 ≤ 300 ms |
| AI job creation UI response              | p95 ≤ 300 ms |
| Job status refresh                       | p95 ≤ 300 ms |
| Recommendation detail open               | p95 ≤ 500 ms |
| Assistant message UI acknowledgement     | p95 ≤ 300 ms |
| Cached AI result display                 | p95 ≤ 200 ms |
| AI UI availability                       |      ≥ 99.5% |

These targets apply to frontend behavior and exclude unavoidable model inference latency where separately measured.

---

## 77. POS Performance Rule

AI must not introduce measurable blocking latency into critical POS operations.

AI functionality must be:

* asynchronous where possible;
* lazy-loaded where appropriate;
* independently failed;
* independently retried;
* independently cached.

Critical POS operations remain higher priority than AI rendering.

---

## 78. Frontend Resource Management

AI-heavy pages must avoid unnecessary resource consumption.

The frontend should:

* lazy-load heavy AI components;
* avoid loading large visualization libraries globally;
* limit concurrent AI requests;
* cancel obsolete requests;
* release unused result data;
* avoid unnecessary polling.

Polling intervals must be bounded and preferably replaced with the general notification/event architecture where available.

---

## 79. Mobile and Low-Power Considerations

Although desktop/POS is the primary environment, AI interfaces should remain usable on lower-powered devices.

Heavy AI processing must remain server-side unless an explicitly approved local inference capability exists.

The browser must not be required to run large models for ordinary ERP functionality.

---

## 80. AI and Frontend Security

Frontend AI state must not be considered trusted.

Any value received from the client must be revalidated by Backend.

This includes:

* Business UUID;
* Branch UUID;
* Product UUID;
* employee identity;
* AI capability;
* job ID;
* recommendation ID;
* approval request;
* model version.

---

## 81. AI Data Minimization

The frontend should receive only the information required for the current screen.

Sensitive or unnecessary AI context must not be transferred merely because it exists in the Backend.

Large historical datasets should remain server-side whenever possible.

---

## 82. Browser Storage

AI data stored locally must follow the general frontend storage policy.

Sensitive AI outputs should not be persisted unnecessarily.

Offline/local storage must:

* respect Business/Branch isolation;
* use approved encryption;
* have controlled retention;
* support invalidation;
* never become authoritative.

---

## 83. AI Result Export

Where AI results can be exported:

* export permission must be checked;
* Business/Branch scope must be preserved;
* exported data must identify AI-generated content where necessary;
* export must be audited according to the general export architecture.

Historical AI results must not be silently rewritten during export.

---

## 84. AI UX and Reports

AI explanations may be linked from reports.

For example:

```text
Daily Report
   ↓
AI Explanation
   ↓
Observed changes
   ↓
Possible contributing factors
```

The explanation must not alter the underlying report.

---

## 85. AI UX and Inventory

Inventory AI should link directly to authoritative inventory information.

For example:

```text
AI recommendation
      ↓
Product
      ↓
Current Stock
      ↓
Inventory Transactions
```

The AI result is explanatory/recommendational; the inventory ledger remains authoritative.

---

## 86. AI UX and Pricing

AI pricing suggestions, if enabled in future, must remain recommendations.

The frontend must not imply that an AI-suggested price is automatically applied.

Any price change must use the normal Menu/Pricing workflow, permissions, configuration versioning and effective Cash Session boundary.

---

## 87. AI UX and Payroll

AI payroll-related insights may be displayed only to authorized users.

AI must not directly change:

* salary;
* attendance;
* bonuses;
* payroll records.

Any supported change requires the ordinary Payroll workflow.

---

## 88. AI UX and Cash Operations

AI may provide anomaly or trend analysis for cash operations.

It must not:

* close a Cash Session;
* modify expected cash;
* modify actual cash;
* perform handover;
* approve a correction.

These remain ordinary ERP operations.

---

## 89. AI UX and Audit

Important AI interactions should be traceable where required.

Examples:

* recommendation accepted;
* recommendation rejected;
* AI-assisted action initiated;
* approval completed;
* AI job created;
* AI result exported.

Audit must identify the employee, Business, Branch, relevant AI object and resulting ERP operation where applicable.

---

## 90. AI Feedback and Learning

Feedback collected from users may be used to improve AI systems.

However:

* feedback is not automatically authoritative;
* feedback must be associated with the correct Business/Branch context;
* personal/sensitive data must be minimized;
* training use requires approved AI governance;
* historical ERP data must not be modified merely because feedback changes.

---

## 91. Feature Flags

AI UI features may be controlled through feature flags.

Feature flags can control:

* rollout;
* beta features;
* UI visibility;
* experimental components.

Feature flags must never replace:

* authorization;
* subscription entitlement;
* Business isolation;
* Branch isolation.

---

## 92. Progressive Rollout

New AI UI features may be released gradually.

Possible rollout:

```text
Internal
   ↓
Selected Business
   ↓
Selected Branch
   ↓
Broader rollout
```

The rollout mechanism must not expose a feature to an unauthorized Business.

---

## 93. AI UX Telemetry

Frontend telemetry may capture:

* screen load performance;
* request latency;
* AI job state;
* UI errors;
* feature usage;
* retry rate;
* recommendation interaction.

Telemetry must avoid unnecessarily storing:

* prompts containing sensitive data;
* full AI responses;
* secrets;
* unauthorized Business data.

---

## 94. AI Accessibility of Uncertainty

Uncertainty indicators must not depend only on color.

For example:

```text
High confidence
Medium confidence
Low confidence
```

should have text or accessible labels in addition to visual indicators.

---

## 95. AI Empty States

Empty AI states must be meaningful.

Examples:

```text
Not enough historical data
```

```text
No anomalies detected
```

```text
No recommendation is currently available
```

The frontend must distinguish these from:

```text
AI service unavailable
```

---

## 96. AI First-Use Experience

For users encountering AI for the first time, the UI may briefly explain:

* what the feature does;
* what data it uses;
* that AI results may be imperfect;
* who can access the information;
* how recommendations work.

The explanation should be concise.

---

## 97. AI Explainability Level

The frontend should support progressive disclosure:

```text
Summary
   ↓
Why?
   ↓
Supporting data
   ↓
Technical details
```

Ordinary users receive simple explanations.

Authorized advanced users may inspect additional provenance and model information.

---

## 98. AI UX Consistency

All AI features should use consistent patterns for:

* confidence;
* freshness;
* loading;
* errors;
* recommendations;
* approval;
* provenance;
* scope;
* status.

Users should not need to learn a different interaction model for every AI feature.

---

## 99. AI UX Invariants

The following invariants apply:

1. AI frontend functionality is optional.
2. Core ERP operation must continue without AI.
3. Frontend AI data comes through Backend APIs.
4. Frontend never communicates directly with AI providers.
5. Frontend never communicates directly with model runtime infrastructure.
6. Backend remains the security boundary.
7. Frontend hiding is not authorization.
8. Business isolation is mandatory.
9. Branch isolation is mandatory.
10. AI context follows the active authorized Business/Branch scope.
11. Branch switching cannot leak previous Branch AI data.
12. AI results are distinguishable from ERP facts.
13. Predictions are not presented as historical facts.
14. Recommendations are not presented as executed actions.
15. AI confidence is shown only when meaningful.
16. AI freshness is shown when staleness matters.
17. AI provenance must be available where decision context requires it.
18. Historical ERP data remains authoritative.
19. AI cannot directly mutate authoritative ERP state.
20. High-risk ERP operations require normal ERP workflows.
21. AI recommendations require human review where configured.
22. Accepting an AI recommendation does not bypass permission checks.
23. Rejecting an AI recommendation does not modify ERP state.
24. AI job creation is idempotent where required.
25. Duplicate submissions must be prevented where practical.
26. Long-running AI work uses asynchronous jobs.
27. Job status must be explicitly represented.
28. Fake progress percentages are prohibited.
29. AI failures must not fail the entire ERP page.
30. Partial AI failure is supported.
31. Cached AI results are non-authoritative.
32. Cache keys preserve Business/Branch isolation.
33. Stale AI results are clearly identified.
34. Offline AI results are clearly distinguished from current server results.
35. Offline mode cannot bypass AI authorization.
36. Offline mode cannot bypass subscription restrictions.
37. Subscription expiry blocks unauthorized AI modifications.
38. Permission denial must not expose restricted AI data.
39. AI assistant respects Backend authorization.
40. AI assistant cannot grant itself permissions.
41. Prompt instructions cannot override application authorization.
42. AI tool actions are controlled by Backend.
43. AI-generated numerical values should use structured responses where available.
44. Currency and units follow Business configuration.
45. AI periods follow Backend-defined date boundaries.
46. AI visualizations distinguish actual and predicted values.
47. AI charts must not imply unsupported certainty.
48. AI notifications must respect user authorization.
49. AI notifications must not expose restricted data.
50. AI history does not overwrite newer results.
51. Model version information is immutable for a generated result.
52. AI UI does not expose secrets.
53. AI UI does not expose internal provider credentials.
54. AI UI does not expose unrestricted internal endpoints.
55. Client-provided scope identifiers are never trusted by Backend.
56. AI local storage is non-authoritative.
57. Sensitive AI data is not stored locally unnecessarily.
58. AI export requires appropriate permission.
59. AI exports preserve scope.
60. AI exports are auditable where required.
61. AI explanations do not modify reports.
62. Inventory AI does not modify inventory directly.
63. Pricing AI does not modify prices directly.
64. Payroll AI does not modify payroll directly.
65. Cash AI does not modify cash state directly.
66. AI feedback does not automatically become authoritative ERP data.
67. AI feedback training use requires governance.
68. Feature flags cannot replace authorization.
69. Feature flags cannot replace subscription entitlement.
70. AI rollout preserves Business isolation.
71. AI telemetry must minimize sensitive data.
72. AI prompts and responses must not be logged unnecessarily.
73. Empty AI state is distinguishable from AI failure.
74. AI first-use explanation must not imply certainty.
75. AI uncertainty must be accessible without relying on color.
76. AI UX uses consistent status patterns.
77. AI loading must not block unrelated ERP operations.
78. AI requests have bounded concurrency.
79. Obsolete AI requests should be cancellable where practical.
80. AI polling must be bounded.
81. AI job completion can use the notification architecture.
82. AI job cancellation is not assumed successful until confirmed.
83. A failed refresh must not unnecessarily destroy the last valid result.
84. AI UI must preserve the user's current authorized context.
85. AI result scope must remain identifiable.
86. AI history must preserve generation time.
87. AI history must preserve relevant model/pipeline provenance.
88. AI output must not be silently relabeled after Branch switching.
89. AI frontend state must distinguish loading, success and error.
90. AI API errors must be mapped to understandable UI states.
91. Internal infrastructure errors must not be exposed to normal users.
92. AI UI must remain responsive on supported low-power devices.
93. Heavy AI computation remains server-side unless explicitly approved.
94. AI components should be lazy-loaded where appropriate.
95. AI libraries should not unnecessarily burden the core POS bundle.
96. AI rendering must not block critical POS workflows.
97. AI page performance must meet defined frontend targets.
98. AI availability target is independent from core ERP availability.
99. AI failure must not roll back committed ERP transactions.
100. AI UX must preserve the principle that the ERP is authoritative and AI is assistive.

---

## 100. Performance and SLO Summary

The AI frontend should meet the following baseline targets:

* AI page initial shell: **p95 ≤ 1.5 s**
* AI result card render after data arrival: **p95 ≤ 300 ms**
* AI job creation UI response: **p95 ≤ 300 ms**
* Job status refresh: **p95 ≤ 300 ms**
* Recommendation detail open: **p95 ≤ 500 ms**
* Assistant message acknowledgement: **p95 ≤ 300 ms**
* Cached AI result display: **p95 ≤ 200 ms**
* AI frontend availability: **≥ 99.5%**
* Critical POS workflow blocking caused by AI: **0**
* Fabricated AI progress values: **0**
* Unauthorized AI data exposures: **0**

These targets are complementary to the AI Backend/API and AI Runtime SLOs.

---

## 101. Related Documents

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

### Frontend Architecture

* `docs/04_Architecture/05_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/05_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/05_Frontend/16_Reports_and_Dashboard_UI.md`
* `docs/04_Architecture/05_Frontend/17_Notifications_and_Alerts_UI.md`
* `docs/04_Architecture/05_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/05_Frontend/22_Frontend_State_Management_and_Data_Flow.md`
* `docs/04_Architecture/05_Frontend/23_Frontend_API_Client_and_Data_Access_Architecture.md`
* `docs/04_Architecture/05_Frontend/24_Frontend_Offline_Storage_and_Local_Persistence_Architecture.md`
* `docs/04_Architecture/05_Frontend/25_Frontend_Offline_Synchronization_and_Conflict_Resolution.md`
* `docs/04_Architecture/05_Frontend/26_Frontend_Error_Handling_and_Recovery_Architecture.md`
* `docs/04_Architecture/05_Frontend/27_Frontend_Performance_and_Optimization_Architecture.md`
* `docs/04_Architecture/05_Frontend/28_Frontend_Security_and_Client_Side_Protection_Architecture.md`

### Backend and API

* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/04_Architecture/04_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/04_Architecture/04_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/04_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/04_Database/23_Configuration_Data_Model.md`

### Product and System Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## 102. Status

**AI Architecture Document:** 19 of 28

**Document Status:** Proposed

**Current Document:** `19_AI_Frontend_and_User_Experience.md`

**Previous Document:** `18_AI_Backend_and_API_Integration.md`

**Next Document:** `20_AI_Security_and_Privacy.md`

The AI frontend architecture is designed to remain assistive, scope-aware, permission-aware and independent from authoritative ERP operations.

