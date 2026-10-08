# API Configuration and Subscription Endpoints

**Document ID:** API-18
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the public API contract for Business configuration, Branch configuration, operational settings, configuration versions, subscription state and subscription entitlements in FastFood ERP.

The API must support:

* Business-level configuration;
* Branch-level configuration;
* operational settings;
* menu-related configuration;
* pricing-related configuration;
* printer routing configuration;
* order workflow configuration;
* dashboard/widget configuration;
* notification preferences where applicable;
* configuration versions;
* configuration approval;
* effective configuration;
* Cash Session configuration boundaries;
* subscription plans;
* subscription lifecycle;
* subscription entitlements;
* tariff limits;
* read-only subscription state;
* subscription expiry;
* deletion eligibility;
* configuration access after expiry;
* offline configuration synchronization;
* optimistic concurrency;
* auditability;
* Business and Branch isolation;
* historical integrity.

This document defines API contracts.

Generic API principles such as authentication, authorization, error formatting, pagination, idempotency and concurrency are defined by the preceding API architecture documents and are referenced rather than duplicated.

---

# 2. Scope

This document covers:

* configuration resources;
* Business configuration;
* Branch configuration;
* effective configuration;
* configuration versions;
* configuration changes;
* configuration approval;
* configuration activation;
* configuration scheduling;
* configuration history;
* menu-related configuration references;
* pricing-related configuration references;
* printer routing;
* order status configuration;
* order workflow configuration;
* dashboard configuration;
* widget configuration;
* operational preferences;
* subscription resources;
* subscription plans;
* subscription lifecycle;
* entitlement resolution;
* tariff limits;
* Branch limits;
* Employee limits;
* Owner limits;
* feature limits;
* subscription expiry;
* read-only mode;
* deletion eligibility;
* deletion lifecycle;
* subscription notifications;
* configuration access during read-only state;
* offline configuration;
* configuration synchronization;
* audit;
* observability;
* performance.

---

# 3. Architectural Position

Configuration and subscription APIs follow:

```text
Client
   ↓
API
   ↓
Authentication
   ↓
Authorization
   ↓
Business / Branch Scope
   ↓
Request Validation
   ↓
Application Use Case
   ↓
Configuration / Subscription Domain
   ↓
Repository
   ↓
PostgreSQL
   ↓
Outbox / Background Processing
   ↓
Cache / Notification / Synchronization
```

PostgreSQL remains authoritative.

Cache, frontend state and offline configuration are derived representations.

---

# 4. Configuration Resource Model

The configuration model is:

```text
Business
   │
   ├── Business Configuration
   │
   └── Branch
        └── Branch Configuration
              ↓
        Effective Configuration
```

Business-level configuration provides defaults.

Branch-level configuration may override permitted settings.

The effective configuration is resolved by the server.

---

# 5. Configuration Categories

Initial configuration categories include:

```text
BUSINESS_SETTINGS
BRANCH_SETTINGS
MENU_SETTINGS
PRICING_SETTINGS
ORDER_WORKFLOW
PRINTER_ROUTING
DASHBOARD_SETTINGS
WIDGET_SETTINGS
NOTIFICATION_SETTINGS
OPERATIONAL_SETTINGS
SECURITY_SETTINGS
```

Not every configuration category is necessarily exposed through one generic endpoint.

Domain-specific configuration endpoints should be preferred where business rules are significant.

---

# 6. Configuration Identity

Each important configuration state has a stable identity.

Example:

```json
{
  "id": "018f...",
  "version": 12,
  "business_id": "018f...",
  "branch_id": "018f...",
  "status": "EFFECTIVE"
}
```

Configuration identity is separate from:

* Business UUID;
* Branch UUID;
* Product UUID;
* Employee UUID;
* Subscription UUID.

---

# 7. Configuration Version

Operational configuration changes must be versioned where they affect system behavior.

A version may contain:

```text
Configuration UUID
Version Number
Business UUID
Branch UUID
Previous Version
Status
Created At
Effective At
Created By
Approved By
Reason
```

Historical versions remain available according to retention policy.

---

# 8. Configuration States

Initial configuration states:

```text
DRAFT
PENDING_APPROVAL
APPROVED
SCHEDULED
EFFECTIVE
SUPERSEDED
ARCHIVED
```

Not every configuration type requires every state.

The domain determines the applicable lifecycle.

---

# 9. Configuration Read

Business configuration:

```http
GET /api/v1/configuration/business
```

Branch configuration:

```http
GET /api/v1/configuration/branches/{branch_id}
```

Effective configuration:

```http
GET /api/v1/configuration/effective
```

The effective endpoint resolves the configuration for the authenticated Business/Branch context.

---

# 10. Effective Configuration

The server determines effective configuration using:

```text
Business Configuration
        ↓
Branch Override
        ↓
Configuration Version
        ↓
Subscription Entitlement
        ↓
Effective Operational State
```

The client must not independently calculate authoritative effective configuration.

---

# 11. Branch Configuration

Endpoint:

```http
GET /api/v1/branches/{branch_id}/configuration
```

Modification:

```http
PATCH /api/v1/branches/{branch_id}/configuration
```

The server validates:

* Business ownership;
* Branch scope;
* permission;
* configuration version;
* subscription entitlement;
* allowed fields.

---

# 12. Business Configuration

Endpoint:

```http
GET /api/v1/configuration/business
PATCH /api/v1/configuration/business
```

Only authorized Business-level actors may modify Business configuration.

Branch-scoped employees cannot modify Business-level settings merely because they can manage the Branch.

---

# 13. Configuration Scope

Every configuration change must identify its scope:

```text
BUSINESS
BRANCH
```

A Branch configuration change must never modify another Branch.

A Business configuration change may affect multiple Branches where the configuration is inherited.

---

# 14. Branch Override

A Branch may override a Business default only where the configuration type allows Branch overrides.

Example:

```text
Business:
Order Workflow = Standard

Branch A:
Order Workflow = Custom
```

Branch A's effective configuration uses its override.

Other Branches continue using the Business configuration.

---

# 15. Configuration Precedence

Where applicable, precedence is:

```text
1. Subscription Entitlement
2. Business Configuration
3. Branch Override
4. Operational State
```

The exact precedence may vary by configuration category.

Security restrictions and subscription restrictions always remain authoritative.

---

# 16. Configuration Version Read

Endpoint:

```http
GET /api/v1/configuration/versions
```

Filters may include:

```text
scope
branch_id
category
status
from
to
```

The endpoint uses bounded pagination.

---

# 17. Specific Configuration Version

Endpoint:

```http
GET /api/v1/configuration/versions/{version_id}
```

The response may include:

* configuration identity;
* version;
* scope;
* category;
* status;
* effective timestamp;
* creator;
* approver;
* reason;
* configuration representation.

Sensitive settings must be filtered according to authorization.

---

# 18. Configuration Change

Generic configuration updates may use:

```http
PATCH /api/v1/configuration/business
PATCH /api/v1/branches/{branch_id}/configuration
```

The API must not allow arbitrary unknown fields.

Allowed fields depend on configuration category and permission.

---

# 19. Domain-Specific Configuration Commands

Important configuration operations should use explicit commands.

Examples:

```http
POST /api/v1/configuration/versions/{version_id}/approve
POST /api/v1/configuration/versions/{version_id}/activate
POST /api/v1/configuration/versions/{version_id}/archive
```

This preserves clear authorization and audit boundaries.

---

# 20. Configuration Approval

Endpoint:

```http
POST /api/v1/configuration/versions/{version_id}/approve
```

The server validates:

* version state;
* actor permission;
* Business scope;
* Branch scope;
* subscription entitlement;
* approval requirements.

Approval must be auditable.

---

# 21. Configuration Activation

Endpoint:

```http
POST /api/v1/configuration/versions/{version_id}/activate
```

Activation must respect:

* approval requirements;
* configuration type;
* effective boundary;
* concurrency;
* current state.

An already superseded version cannot silently become effective.

---

# 22. Scheduled Configuration

Where required:

```http
POST /api/v1/configuration/versions/{version_id}/schedule
```

The request may contain:

```json
{
  "effective_at": "2026-10-08T00:00:00Z"
}
```

For POS-critical configuration, the system should prefer the defined Cash Session boundary where required rather than arbitrary timestamps.

---

# 23. Cash Session Configuration Boundary

Menu and pricing configuration follows the established rule:

> New menu and pricing configuration becomes operational from the next Cash Session.

Therefore, the API must not allow a configuration update to silently alter pricing for an already active Cash Session.

The effective configuration must remain identifiable.

---

# 24. Current Configuration

Endpoint:

```http
GET /api/v1/configuration/current
```

The response should provide a compact representation of the currently effective configuration for the selected context.

Example:

```json
{
  "business_id": "018f...",
  "branch_id": "018f...",
  "configuration_version": 12,
  "effective": true
}
```

---

# 25. Configuration ETag

Read-heavy configuration endpoints may expose ETag values.

Example:

```http
ETag: "configuration-12"
```

Clients may use:

```http
If-None-Match: "configuration-12"
```

ETag reduces unnecessary transfer.

It does not replace authorization.

---

# 26. Optimistic Concurrency

Configuration mutations should support version checking.

Example:

```http
If-Match: "12"
```

If the current version is 13:

```text
409 Conflict
STALE_VERSION
```

The server must not silently overwrite the newer version.

---

# 27. Configuration Conflict

A conflict may occur when:

* two employees edit the same configuration;
* an offline device has stale configuration;
* a Branch override was changed by another actor;
* subscription state changed while an operation was pending.

The API returns a structured conflict.

---

# 28. Configuration Conflict Response

Example:

```json
{
  "error": {
    "code": "STALE_VERSION",
    "message": "The configuration has changed.",
    "request_id": "01J...",
    "details": {
      "current_version": 13,
      "requested_version": 12
    }
  }
}
```

The client must refresh before continuing.

---

# 29. Menu Configuration Boundary

Menu and pricing endpoint details are defined in:

`15_API_Product_Menu_Recipe_and_Inventory_Endpoints.md`

Configuration APIs provide the broader configuration lifecycle.

They must not create a second competing pricing authority.

---

# 30. Order Workflow Configuration

The Business may configure Order statuses and workflow stages according to the established Business rules.

Example:

```text
NEW
ACCEPTED
PREPARING
READY
COMPLETED
CANCELLED
```

The API should expose the configured workflow without allowing clients to invent unauthorized states.

---

# 31. Order Workflow Read

Endpoint:

```http
GET /api/v1/configuration/order-workflow
```

Branch context may be included where Branch-specific workflow is supported.

The response may contain:

* enabled statuses;
* status order;
* stage visibility;
* per-item visibility configuration.

---

# 32. Order Workflow Update

Endpoint:

```http
PATCH /api/v1/configuration/order-workflow
```

The server validates:

* allowed statuses;
* valid transitions;
* permission;
* current version;
* Branch scope;
* subscription entitlement.

Workflow configuration must not directly force an existing Order into an invalid state.

---

# 33. Printer Routing Configuration

Endpoint:

```http
GET /api/v1/configuration/printer-routing
```

Modification:

```http
PATCH /api/v1/configuration/printer-routing
```

The configuration may map Product categories/types to printer destinations.

Example:

```text
Pizza
   ↓
Kitchen Printer A

Lavash
   ↓
Kitchen Printer B
```

Printer routing does not determine whether an Order is accepted.

---

# 34. Printer Failure

Printer failure must not rollback a committed Order.

The API may expose printer configuration and operational status, but printing remains a secondary effect.

---

# 35. Dashboard Configuration

Endpoint:

```http
GET /api/v1/configuration/dashboard
PATCH /api/v1/configuration/dashboard
```

Configuration may include:

* enabled widgets;
* default sections;
* ordering;
* visibility;
* dashboard preferences.

User-customizable dashboard state must remain separate from authoritative financial state.

---

# 36. Widget Configuration

Endpoint:

```http
GET /api/v1/configuration/widgets
PATCH /api/v1/configuration/widgets
```

The server must validate allowed widget identifiers.

A client cannot enable a feature that is unavailable under the Business subscription entitlement.

---

# 37. Notification Preferences

Where supported:

```http
GET /api/v1/configuration/notification-preferences
PATCH /api/v1/configuration/notification-preferences
```

Preferences may control:

* non-critical notifications;
* display preferences;
* optional alert categories.

Security-critical notifications must not be disabled by ordinary preference settings where policy requires mandatory delivery.

---

# 38. Operational Settings

Operational settings may include:

* Branch defaults;
* display preferences;
* order workflow options;
* operational thresholds;
* configurable non-financial behavior.

Financial and security rules must remain in Domain-controlled configuration.

---

# 39. Configuration Validation

Configuration requests must be validated at multiple levels.

API layer validates:

* structure;
* types;
* field presence;
* allowed enum values.

Application/Domain validates:

* Business rules;
* permission;
* configuration dependencies;
* state;
* effective boundary;
* subscription entitlement.

---

# 40. Configuration Dependencies

Some configuration values depend on other configuration.

Example:

```text
Set Configuration
        ↓
Product Availability
        ↓
Menu Configuration
```

The API must reject invalid combinations.

Partial configuration updates must not leave the authoritative system in an invalid state.

---

# 41. Atomic Configuration Changes

Configuration changes that must remain consistent are committed atomically.

Example:

```text
Update Configuration
       +
Create Configuration Version
       +
Audit
       +
Outbox Event
```

The core transaction commits these required records together.

---

# 42. Secondary Configuration Effects

After configuration commit:

* cache invalidation;
* notification;
* background synchronization;
* analytics;

may execute asynchronously.

Failure of these secondary effects must not rollback committed configuration.

---

# 43. Configuration Audit

Important configuration changes must contain:

```text
Event UUID
Business UUID
Branch UUID where applicable
Actor UUID
Device UUID
Configuration UUID
Previous Version
New Version
Reason
Timestamp
Result
```

Audit records remain immutable.

---

# 44. Configuration History

Endpoint:

```http
GET /api/v1/configuration/history
```

The API may expose historical configuration changes according to permission.

History must preserve:

* previous values;
* new values;
* actor;
* timestamp;
* version;
* reason.

Historical configuration cannot be silently overwritten.

---

# 45. Subscription Resource

Subscription represents the Business's commercial service state.

Example:

```json
{
  "id": "018f...",
  "business_id": "018f...",
  "plan_id": "018f...",
  "status": "ACTIVE",
  "starts_at": "2026-01-01T00:00:00Z",
  "expires_at": "2027-01-01T00:00:00Z"
}
```

The client cannot modify authoritative subscription status directly.

---

# 46. Subscription Plan

A Subscription Plan defines available commercial limits and features.

Example:

```text
Plan
 ├── Branch Limit
 ├── Employee Limit
 ├── Owner Limit
 ├── Feature Entitlements
 └── Other Commercial Limits
```

Plan administration is primarily a Super Admin capability.

---

# 47. Subscription Endpoints

Business-level subscription read:

```http
GET /api/v1/subscription
```

Entitlements:

```http
GET /api/v1/subscription/entitlements
```

Usage:

```http
GET /api/v1/subscription/usage
```

Plan information:

```http
GET /api/v1/subscription/plan
```

---

# 48. Subscription Mutation

Subscription mutation endpoints are normally restricted to authorized platform/business administration workflows.

Possible platform-level endpoints:

```http
POST /api/v1/admin/subscription-plans
PATCH /api/v1/admin/subscription-plans/{plan_id}
POST /api/v1/admin/businesses/{business_id}/subscription
```

These operations are outside ordinary Branch/POS employee authority.

---

# 49. Subscription Status

Initial lifecycle:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

The server is authoritative for lifecycle state.

---

# 50. Active Subscription

When:

```text
status = ACTIVE
```

normal entitled operations are available according to:

* permissions;
* Business limits;
* Branch scope;
* feature entitlements;
* operational state.

---

# 51. Read-Only Subscription

When subscription expires:

```text
ACTIVE
   ↓
READ_ONLY
```

The API blocks prohibited modifications.

Allowed operations may include:

* viewing existing data;
* viewing historical reports;
* authorized XLSX exports;
* reviewing configuration;
* reviewing employees;
* reviewing inventory;
* reviewing transaction history.

The exact entitlement remains server-controlled.

---

# 52. Read-Only Enforcement

Every modifying endpoint must validate subscription entitlement.

The API must not rely on frontend UI hiding buttons.

Example:

```text
POST /products
       ↓
Subscription = READ_ONLY
       ↓
403
SUBSCRIPTION_READ_ONLY
```

---

# 53. Subscription Expiry

Expiry is determined using server-controlled subscription state.

Client clocks must not determine whether the Business is active.

Offline devices cannot extend subscription validity.

---

# 54. Offline Subscription Behavior

Offline authorization contains a bounded validity period.

If the subscription becomes invalid according to server state, the next synchronization/online authorization must enforce the current subscription state.

The client must not manufacture a longer offline authorization period.

---

# 55. Subscription Entitlements

Entitlements may include:

```text
BRANCH_COUNT
EMPLOYEE_COUNT
OWNER_COUNT
FEATURE_ACCESS
REPORT_ACCESS
EXPORT_ACCESS
INVENTORY_FEATURES
PAYROLL_FEATURES
ADVANCED_REPORTS
```

The entitlement registry is server-controlled.

---

# 56. Entitlement Read

Endpoint:

```http
GET /api/v1/subscription/entitlements
```

Example:

```json
{
  "features": {
    "payroll": true,
    "advanced_reports": false,
    "inventory": true
  },
  "limits": {
    "branches": 5,
    "employees": 100,
    "owners": 3
  }
}
```

The response represents the effective entitlement for the current Business.

---

# 57. Usage

Endpoint:

```http
GET /api/v1/subscription/usage
```

Usage may include:

```json
{
  "branches": {
    "used": 3,
    "limit": 5
  },
  "employees": {
    "used": 42,
    "limit": 100
  },
  "owners": {
    "used": 2,
    "limit": 3
  }
}
```

The server remains authoritative for limit enforcement.

---

# 58. Limit Enforcement

The API must enforce limits server-side.

Examples:

```text
Create Branch
Create Employee
Create Owner
Enable Entitled Feature
```

If the limit is reached:

```text
409 Conflict
```

with an appropriate stable error code such as:

```text
SUBSCRIPTION_LIMIT_REACHED
```

The exact status mapping follows the common API error contract.

---

# 59. Feature Entitlement

Feature access must be evaluated before executing the corresponding use case.

Example:

```text
POST /payroll/...
        ↓
Payroll Entitlement
        ↓
Allowed / Denied
```

Frontend visibility is not sufficient.

---

# 60. Entitlement and Permissions

Both conditions may be required:

```text
Permission
    AND
Subscription Entitlement
```

A user cannot access a feature merely because they have a permission if the Business subscription does not include it.

Likewise, a subscribed feature does not grant permission to every employee.

---

# 61. Entitlement and Branch Scope

A feature entitlement may apply Business-wide while actual usage remains Branch-scoped.

Example:

```text
Payroll Feature
    ↓
Business entitled
    ↓
Employee permission
    ↓
Branch scope
```

All applicable authorization layers must succeed.

---

# 62. Subscription Renewal

Renewal changes subscription state according to the subscription lifecycle.

The API may expose renewal status:

```http
GET /api/v1/subscription
```

Payment/commerce processing is outside this document unless integrated through an approved external subscription provider.

---

# 63. Subscription Expiry Notification

The system may generate notifications such as:

```text
SUBSCRIPTION_EXPIRING
SUBSCRIPTION_READ_ONLY
```

Notification delivery is asynchronous.

Notification state does not determine subscription state.

---

# 64. Deletion Eligibility

If a Business remains inactive for the configured retention period:

```text
READ_ONLY
   ↓
DELETION_ELIGIBLE
```

Current Business rule:

**60 days after expiry without reactivation.**

The API may expose deletion eligibility:

```http
GET /api/v1/subscription
```

---

# 65. Deletion Lifecycle

The lifecycle may continue:

```text
DELETION_ELIGIBLE
        ↓
DELETING
        ↓
DELETED
```

Deletion is controlled by the data lifecycle architecture.

Normal Business users must not directly force permanent deletion through ordinary configuration APIs.

---

# 66. Deleted Business

When:

```text
status = DELETED
```

normal API access is blocked.

The Business must not be resurrected by modifying a subscription or configuration record.

Historical backup retention follows the data lifecycle and disaster recovery policies.

---

# 67. Configuration During Read-Only

When Business is `READ_ONLY`:

Allowed:

```text
GET configuration
GET configuration history
GET effective configuration
GET subscription
GET entitlements
GET reports
```

Blocked:

```text
PATCH configuration
POST configuration approval
POST configuration activation
POST configuration scheduling
```

unless explicitly allowed by the subscription policy.

---

# 68. Configuration During Deletion Eligibility

Once `DELETION_ELIGIBLE`:

* normal modification remains blocked;
* data may remain viewable according to lifecycle policy;
* deletion warnings may be exposed;
* export may remain available where permitted.

The API must not allow the client to cancel deletion by simply changing local state.

---

# 69. Super Admin Subscription APIs

Platform administration may use separate endpoints:

```http
GET    /api/v1/admin/subscription-plans
POST   /api/v1/admin/subscription-plans
GET    /api/v1/admin/subscription-plans/{id}
PATCH  /api/v1/admin/subscription-plans/{id}

GET    /api/v1/admin/businesses/{business_id}/subscription
PATCH  /api/v1/admin/businesses/{business_id}/subscription
```

These endpoints require platform-level authorization.

---

# 70. Plan Versioning

Changing a subscription plan should not silently rewrite the historical meaning of an existing subscription.

Where required, plans must be versioned.

Historical subscriptions retain sufficient information to determine the applicable commercial rules.

---

# 71. Entitlement Snapshot

Where a Business subscription changes, the system may create an entitlement snapshot.

This allows historical operations to remain explainable.

Current entitlement must not reinterpret completed historical transactions.

---

# 72. Subscription Concurrency

Subscription changes must use optimistic concurrency where required.

Example:

```http
If-Match: "7"
```

A stale subscription update returns:

```text
409 Conflict
STALE_VERSION
```

---

# 73. Subscription Idempotency

Retryable subscription mutation operations must use idempotency.

Examples:

```text
Plan assignment
Subscription activation
Subscription renewal
Subscription state transition
```

Duplicate requests must not create duplicate subscription effects.

---

# 74. Configuration Idempotency

Configuration mutations that may be retried must use operation identity.

Examples:

```text
Configuration update
Approval
Activation
Scheduling
Branch override
```

Repeated processing must not create duplicate configuration versions.

---

# 75. Configuration Synchronization

Configuration changes may need to synchronize to trusted offline devices.

The server publishes the authoritative configuration version.

Example:

```text
Configuration Version 13
        ↓
Outbox
        ↓
Synchronization
        ↓
Trusted Device
        ↓
Local Configuration Version 13
```

---

# 76. Offline Configuration Read

Offline devices may use:

```text
latest valid authorized local configuration
```

The local configuration is not authoritative.

The API provides the server version when connectivity is available.

---

# 77. Configuration Synchronization Endpoint

The general synchronization contract is defined in:

`19_API_Offline_Synchronization_and_Reconciliation.md`

Configuration APIs should expose sufficient version information for synchronization.

Example:

```json
{
  "configuration_version": 13,
  "updated_at": "2026-10-08T00:00:00Z"
}
```

---

# 78. Configuration Delta

Where useful, the server may provide configuration changes since a known version.

Example:

```http
GET /api/v1/configuration/changes?since_version=12
```

The server must determine whether delta synchronization is supported for the specific configuration category.

---

# 79. Configuration Snapshot

If delta synchronization is unsafe or too complex, the API may return a complete authorized configuration snapshot.

The simpler safe strategy should be preferred where performance remains acceptable.

---

# 80. Configuration Cache

Effective configuration may be cached.

However:

```text
PostgreSQL
   ↓
Authoritative Configuration
   ↓
Cache
```

not:

```text
Cache
   ↓
Authoritative Configuration
```

Cache invalidation follows:

`14_Backend_Caching_and_Performance_Architecture.md`

---

# 81. Subscription Cache

Subscription entitlement may use bounded caching.

However:

* expiry is security-sensitive;
* revocation must invalidate cache;
* stale entitlement must not authorize indefinitely.

The database remains authoritative.

---

# 82. Cache Failure

If configuration or subscription cache is unavailable:

```text
Cache Failure
     ↓
Authoritative Database
     ↓
Resolve State
```

The system may become slower.

It must not fail open.

---

# 83. Configuration Security

Configuration APIs must prevent:

* cross-Business access;
* cross-Branch modification;
* unauthorized feature activation;
* unauthorized pricing configuration;
* unauthorized printer changes;
* unauthorized workflow changes;
* unauthorized security setting changes.

---

# 84. Sensitive Configuration

Some configuration may be security-sensitive.

Examples:

* device trust rules;
* authentication settings;
* security policies;
* privileged operational settings.

These require stronger authorization and audit.

Sensitive values must not be returned to clients unless explicitly required.

---

# 85. Configuration Secrets

Secrets must not be stored or returned through ordinary configuration endpoints.

Examples:

```text
API keys
Private keys
Passwords
Database credentials
Signing secrets
```

Secret management follows the environment/security architecture.

---

# 86. Business Isolation

Every Business-scoped configuration operation must verify:

```text
Authenticated Actor
        ↓
Business Membership
        ↓
Requested Business
        ↓
Permission
```

Changing a Business UUID must never switch authorization context.

---

# 87. Branch Isolation

Every Branch-scoped configuration operation must verify:

```text
Business
   ↓
Branch
   ↓
Employee Branch Scope
   ↓
Permission
```

Branch A configuration cannot be modified through Branch B context.

---

# 88. Manager Authority

Managers may modify configuration only where:

* they have the permission;
* they have the relevant Branch scope;
* the configuration category permits Manager control;
* they do not exceed their own authority.

A Manager must not grant themselves or another employee authority they do not possess.

---

# 89. Owner Authority

Owner-level configuration includes:

* Business settings;
* Branch configuration;
* menu-related settings;
* pricing configuration;
* workflow configuration;
* dashboard defaults;
* operational settings;

subject to subscription entitlement and security policy.

---

# 90. Employee Configuration Scope

Cashiers, Waiters, Cooks and other employees receive only configuration access explicitly granted by permission.

Read access and modification access are separate.

---

# 91. Configuration API Error Codes

Relevant error codes include:

```text
CONFIGURATION_NOT_FOUND
CONFIGURATION_CATEGORY_INVALID
CONFIGURATION_FIELD_INVALID
CONFIGURATION_SCOPE_DENIED
CONFIGURATION_NOT_APPROVED
CONFIGURATION_NOT_EFFECTIVE
CONFIGURATION_ALREADY_ACTIVE
CONFIGURATION_ALREADY_ARCHIVED
STALE_VERSION
CONFIGURATION_CONFLICT
CONFIGURATION_DEPENDENCY_INVALID
SUBSCRIPTION_READ_ONLY
SUBSCRIPTION_EXPIRED
SUBSCRIPTION_LIMIT_REACHED
FEATURE_NOT_ENTITLED
SUBSCRIPTION_NOT_FOUND
SUBSCRIPTION_STATE_INVALID
SUBSCRIPTION_VERSION_CONFLICT
BUSINESS_SCOPE_DENIED
BRANCH_SCOPE_DENIED
ACCESS_DENIED
DUPLICATE_OPERATION
SERVICE_UNAVAILABLE
```

Canonical error formatting is defined by:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 92. Configuration Performance Targets

Initial targets:

| Operation                        |   Target |
| -------------------------------- | -------: |
| Effective configuration read p95 | ≤ 200 ms |
| Business configuration read p95  | ≤ 200 ms |
| Branch configuration read p95    | ≤ 200 ms |
| Configuration version read p95   | ≤ 250 ms |
| Configuration update p95         | ≤ 400 ms |
| Configuration approval p95       | ≤ 400 ms |
| Configuration activation p95     | ≤ 400 ms |
| Configuration history list p95   | ≤ 300 ms |
| Subscription read p95            | ≤ 200 ms |
| Entitlement read p95             | ≤ 100 ms |
| Subscription usage read p95      | ≤ 300 ms |

---

# 93. Subscription Performance

Subscription and entitlement evaluation should not unnecessarily slow normal POS requests.

Target:

* cached entitlement evaluation p95 ≤ **20 ms**;
* authoritative entitlement resolution p95 ≤ **100 ms**;
* subscription state validation overhead p95 ≤ **50 ms**.

Critical authorization decisions must prioritize correctness over latency.

---

# 94. Availability Target

Configuration and subscription APIs follow the platform availability target:

**≥ 99.9% monthly**

Security-sensitive subscription state must fail closed if authoritative entitlement state cannot be safely established.

---

# 95. Observability

Metrics should include:

```text
configuration_read_count
configuration_update_count
configuration_conflict_count
configuration_activation_count
configuration_approval_count
configuration_cache_hit_count
configuration_cache_miss_count
subscription_read_count
entitlement_evaluation_count
subscription_state_change_count
subscription_limit_denial_count
feature_entitlement_denial_count
```

Metrics must avoid uncontrolled Business/Branch UUID cardinality.

---

# 96. Audit

Important operations must create audit events:

* Business configuration change;
* Branch configuration change;
* configuration approval;
* configuration activation;
* configuration scheduling;
* security configuration change;
* subscription state change;
* plan assignment;
* entitlement change;
* privileged subscription operation.

Audit records are immutable.

---

# 97. Configuration Failure Recovery

If configuration update commits successfully but cache invalidation fails:

```text
Database
   ↓
Committed
   ↓
Cache Invalidation Retry
```

The committed configuration remains authoritative.

The system must not rollback committed configuration merely because cache invalidation failed.

---

# 98. Subscription Failure Recovery

If a subscription transition is committed but notification delivery fails:

```text
Subscription State
      ↓
Committed
      ↓
Notification Retry
```

Notification failure must not rollback the subscription transition.

---

# 99. Configuration Worker Recovery

If configuration synchronization fails:

* authoritative configuration remains in PostgreSQL;
* synchronization event remains retryable;
* trusted device retains its previous valid configuration;
* stale configuration must not be treated as current server state.

---

# 100. Configuration and Historical Integrity

Current configuration must never reinterpret historical:

* Orders;
* Order Item prices;
* Payments;
* Refunds;
* Inventory Transactions;
* Recipe Versions;
* Set configurations;
* Report Versions;
* Audit events.

---

# 101. Subscription and Historical Integrity

Subscription changes must not modify historical transactions.

For example:

```text
Plan A
   ↓
Historical Order
```

remains historically valid even if the Business later moves to Plan B.

---

# 102. Configuration Export

Where Business configuration export is supported, it should be treated as a read operation.

Export must:

* respect authorization;
* respect Business/Branch scope;
* identify configuration version;
* not expose secrets;
* preserve historical configuration where requested.

---

# 103. Configuration Import

Configuration import is outside the default simple configuration API unless explicitly introduced.

If implemented later, it must support:

* validation;
* version checking;
* preview;
* conflict detection;
* authorization;
* bounded payload;
* audit;
* idempotency.

A raw configuration replacement endpoint is prohibited.

---

# 104. Generic Configuration Replacement

The API must not expose:

```http
PUT /configuration
```

that blindly replaces the complete Business configuration.

Such an operation would create excessive concurrency and authorization risk.

Configuration categories should be updated through controlled contracts.

---

# 105. Subscription Plan Configuration

Plan configuration should be explicit.

Example:

```http
PATCH /api/v1/admin/subscription-plans/{plan_id}
```

Changes may include:

* Branch limit;
* Employee limit;
* Owner limit;
* feature entitlement.

Plan changes must preserve historical subscription meaning.

---

# 106. Plan Deactivation

A subscription plan may be deactivated for new assignments.

Deactivating a plan must not automatically delete historical subscriptions that used the plan.

Existing subscriptions follow their own lifecycle.

---

# 107. Subscription Entitlement Resolution

Effective entitlement is resolved from:

```text
Subscription
      ↓
Plan
      ↓
Plan Version
      ↓
Business State
      ↓
Effective Entitlements
```

The API returns the effective result.

Clients must not calculate entitlement themselves.

---

# 108. Entitlement Snapshot and Cache

A cached entitlement result may be used for performance.

It must be invalidated when:

* subscription changes;
* plan changes;
* Business state changes;
* relevant entitlement changes.

Security-sensitive stale entitlement must have bounded lifetime.

---

# 109. Configuration API and Frontend

The frontend should consume effective configuration rather than rebuilding Business rules locally.

For example:

```text
API
 ↓
Effective Order Workflow
 ↓
Frontend
 ↓
Display allowed states
```

The frontend remains a presentation layer.

Server validation remains mandatory.

---

# 110. Configuration API and POS

POS clients require compact configuration representations.

POS configuration responses should avoid:

* historical configuration;
* unrelated administrative settings;
* large audit data;
* unnecessary metadata.

The POS should receive only operationally required configuration.

---

# 111. Configuration API and Offline POS

Trusted devices may receive:

* effective menu configuration;
* pricing configuration;
* order workflow;
* printer routing;
* required operational settings.

The configuration must be signed/versioned according to the offline architecture.

---

# 112. Subscription API and Offline POS

Offline authorization must contain sufficient subscription-related restrictions.

The client cannot:

* extend expiry;
* enable unavailable features;
* bypass Branch limits;
* create new entitlement state.

Server synchronization remains authoritative.

---

# 113. Testing Requirements

The API must test:

### Configuration

* Business configuration read;
* Branch configuration read;
* effective configuration;
* configuration update;
* version conflict;
* approval;
* activation;
* scheduling;
* history;
* Business isolation;
* Branch isolation;
* Manager authority;
* Owner authority;
* read-only behavior;
* cache failure;
* synchronization.

### Subscription

* active subscription;
* expiry;
* READ_ONLY;
* DELETION_ELIGIBLE;
* DELETING;
* DELETED;
* entitlement resolution;
* usage limits;
* feature access;
* limit enforcement;
* plan changes;
* stale version;
* idempotency;
* subscription cache failure.

---

# 114. Security Testing

Security tests must verify:

* cross-Business configuration access;
* cross-Branch configuration access;
* unauthorized configuration changes;
* Manager privilege escalation;
* unauthorized subscription mutation;
* entitlement bypass;
* read-only bypass;
* deleted Business access;
* offline entitlement bypass;
* stale cache authorization;
* secret exposure.

---

# 115. Concurrency Testing

Concurrency tests must verify:

```text
Two configuration updates
Two approvals
Two activations
Two Branch overrides
Two subscription state transitions
Two plan updates
```

The system must prevent silent last-write-wins behavior for important configuration.

---

# 116. Historical Integrity Testing

Tests must verify:

```text
Configuration Version 1
      ≠
Configuration Version 2
```

and:

```text
Current Configuration
      ≠
Historical Order Configuration
```

and:

```text
Subscription Plan Change
      ≠
Historical Transaction Rewrite
```

---

# 117. Endpoint Summary

### Business and Branch Configuration

```text
GET    /configuration/business
PATCH  /configuration/business

GET    /branches/{branch_id}/configuration
PATCH  /branches/{branch_id}/configuration

GET    /configuration/current
GET    /configuration/effective
GET    /configuration/versions
GET    /configuration/versions/{version_id}
GET    /configuration/history
```

### Configuration Commands

```text
POST   /configuration/versions/{version_id}/approve
POST   /configuration/versions/{version_id}/activate
POST   /configuration/versions/{version_id}/schedule
POST   /configuration/versions/{version_id}/archive
```

### Operational Configuration

```text
GET    /configuration/order-workflow
PATCH  /configuration/order-workflow

GET    /configuration/printer-routing
PATCH  /configuration/printer-routing

GET    /configuration/dashboard
PATCH  /configuration/dashboard

GET    /configuration/widgets
PATCH  /configuration/widgets

GET    /configuration/notification-preferences
PATCH  /configuration/notification-preferences
```

### Subscription

```text
GET    /subscription
GET    /subscription/plan
GET    /subscription/entitlements
GET    /subscription/usage
```

### Platform Subscription Administration

```text
GET    /admin/subscription-plans
POST   /admin/subscription-plans
GET    /admin/subscription-plans/{plan_id}
PATCH  /admin/subscription-plans/{plan_id}

GET    /admin/businesses/{business_id}/subscription
PATCH  /admin/businesses/{business_id}/subscription
```

---

# 118. API Invariants

The following invariants apply to Configuration and Subscription APIs:

1. PostgreSQL remains authoritative for configuration state.
2. PostgreSQL remains authoritative for subscription state.
3. Cache is never authoritative configuration state.
4. Cache is never authoritative subscription state.
5. Client-provided Business UUID is never authoritative.
6. Client-provided Branch UUID is never authoritative.
7. Business configuration is Business-scoped.
8. Branch configuration is Branch-scoped.
9. Branch configuration cannot cross Business boundaries.
10. Branch configuration cannot silently modify another Branch.
11. Effective configuration is resolved by the server.
12. Clients must not independently become authoritative for effective configuration.
13. Important configuration changes are versioned.
14. Historical configuration versions remain immutable.
15. Configuration versions preserve historical identity.
16. Stale configuration updates are rejected.
17. Important configuration mutations use idempotency.
18. Duplicate configuration operations do not create duplicate effects.
19. Configuration approval is authorization-controlled.
20. Configuration activation is authorization-controlled.
21. Configuration scheduling is authorization-controlled.
22. Configuration state transitions are domain-controlled.
23. Arbitrary client-provided configuration states are not authoritative.
24. Business configuration may provide Branch defaults.
25. Branch overrides apply only where explicitly supported.
26. Branch overrides do not modify Business defaults.
27. Branch overrides do not modify other Branches.
28. Subscription entitlement is evaluated server-side.
29. Frontend feature visibility does not replace entitlement enforcement.
30. Permission and entitlement are separate controls.
31. Both permission and entitlement may be required.
32. Subscription expiry is server-controlled.
33. Client clocks cannot extend subscription validity.
34. Offline clients cannot extend subscription validity.
35. READ_ONLY subscription blocks prohibited modifying operations.
36. READ_ONLY subscription does not delete historical data.
37. DELETION_ELIGIBLE state does not allow normal Business modification.
38. DELETING state cannot be cancelled by ordinary configuration APIs.
39. DELETED Business cannot be resurrected through subscription APIs.
40. Subscription state transitions are auditable.
41. Subscription plan changes do not silently rewrite historical subscription meaning.
42. Historical transactions are not reinterpreted by current subscription plans.
43. Historical transactions are not reinterpreted by current configuration.
44. Menu and pricing authority remains in the dedicated Product/Menu API.
45. Configuration APIs must not create competing pricing authority.
46. POS-critical pricing configuration respects Cash Session boundaries.
47. Active Cash Sessions do not silently switch pricing configuration.
48. Effective configuration version remains identifiable.
49. Order workflow configuration cannot arbitrarily mutate existing Orders.
50. Invalid workflow configurations are rejected.
51. Printer configuration does not determine financial transaction success.
52. Printer failure does not rollback committed business state.
53. Dashboard configuration does not alter authoritative Business data.
54. Widget configuration cannot enable unavailable subscription features.
55. Security-critical notifications cannot be disabled through ordinary preferences where prohibited.
56. Configuration secrets are never returned through ordinary configuration endpoints.
57. Database credentials are never exposed through configuration APIs.
58. Private keys are never exposed through configuration APIs.
59. Sensitive configuration requires stronger authorization where applicable.
60. Manager authority cannot exceed the Manager's own permissions.
61. Managers cannot grant unauthorized configuration authority.
62. Owner configuration authority remains subject to subscription entitlement.
63. Employee configuration access is permission-controlled.
64. Read and write configuration permissions are distinct.
65. Configuration history remains auditable.
66. Configuration audit records are immutable.
67. Configuration commit occurs before secondary cache invalidation.
68. Cache invalidation failure does not rollback committed configuration.
69. Notification failure does not rollback committed subscription state.
70. Synchronization failure does not invalidate authoritative configuration.
71. Offline devices use the latest valid authorized local configuration.
72. Offline configuration is not server-authoritative.
73. Configuration synchronization cannot bypass Business scope.
74. Configuration synchronization cannot bypass Branch scope.
75. Configuration synchronization cannot bypass subscription restrictions.
76. Configuration delta responses remain version-aware.
77. Full configuration snapshots remain authorization-controlled.
78. ETag does not replace authorization.
79. Cached entitlement does not authorize indefinitely after expiry.
80. Revoked subscription state invalidates relevant entitlement cache.
81. Configuration cache keys preserve Business isolation.
82. Configuration cache keys preserve Branch isolation.
83. Subscription cache keys preserve Business isolation.
84. Report configuration cannot expose unauthorized data.
85. Export configuration cannot bypass file authorization.
86. Subscription limits are enforced server-side.
87. Branch limits are enforced server-side.
88. Employee limits are enforced server-side.
89. Owner limits are enforced server-side.
90. Feature entitlements are enforced server-side.
91. Plan deactivation does not delete historical subscriptions.
92. Subscription usage values are server-derived.
93. Subscription usage cannot be increased by client-provided counters.
94. Configuration updates are bounded.
95. Configuration payloads are validated.
96. Unknown configuration fields are rejected.
97. Configuration dependencies are validated.
98. Invalid partial configurations cannot be committed.
99. Atomic configuration changes remain transactionally consistent.
100. Secondary configuration effects cannot corrupt committed state.
101. Configuration performance remains within defined targets.
102. Subscription entitlement evaluation remains within defined targets.
103. Configuration APIs remain within the platform availability target.
104. Security-sensitive entitlement decisions fail closed.
105. Configuration failures are observable.
106. Subscription failures are observable.
107. Configuration conflicts are observable.
108. Subscription conflicts are observable.
109. High-cardinality Business UUIDs must not become uncontrolled metric labels.
110. API error codes remain stable.
111. Sensitive configuration values are filtered from responses.
112. Configuration API responses expose only authorized data.
113. Subscription API responses expose only authorized data.
114. Platform subscription administration is separated from ordinary Business operations.
115. Ordinary employees cannot mutate platform subscription plans.
116. Historical configuration cannot be silently overwritten.
117. Historical subscription state cannot be silently overwritten.
118. Configuration export does not expose secrets.
119. Configuration import is not an unrestricted raw replacement operation.
120. Performance optimization must not weaken security, subscription enforcement or historical integrity.

---

# 119. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/03_Subscription_and_Tariffs.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/17_Notifications_and_Alerts.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/11_Configuration_and_Environment_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/03_API_Layers_and_Request_Lifecycle.md`
* `docs/04_Architecture/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/08_API_Request_Validation_and_Response_Contracts.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/12_API_CRUD_and_Command_Endpoint_Architecture.md`
* `docs/04_Architecture/09_API/15_API_Product_Menu_Recipe_and_Inventory_Endpoints.md`
* `docs/04_Architecture/09_API/17_API_Report_File_and_Notification_Endpoints.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/04_Architecture/09_API/21_API_Security_CORS_CSRF_and_Data_Protection.md`

---

# 120. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `18_API_Configuration_and_Subscription_Endpoints.md`

**Previous Document:** `17_API_Report_File_and_Notification_Endpoints.md`

**Next Document:** `19_API_Offline_Synchronization_and_Reconciliation.md`

---

## Final Principle

> Configuration APIs must expose controlled, versioned and scope-aware operational configuration, while subscription APIs must enforce commercial entitlement and lifecycle state server-side. Neither client state nor cache may override authoritative configuration, subscription status, security boundaries or historical integrity.

