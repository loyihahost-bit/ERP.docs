# Frontend State Management and Data Flow

**Document ID:** FA-22
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`

---

## 1. Purpose

This document defines the frontend state management and data flow architecture for FastFood ERP.

The frontend must provide predictable, fast and secure state handling while keeping business logic authoritative on the backend.

The architecture must support:

* authentication;
* Business and Branch context;
* permissions;
* subscription entitlement;
* POS operations;
* Orders;
* Cash Sessions;
* Inventory;
* Menu and Pricing;
* Settings;
* Notifications;
* Reports;
* Offline operation;
* Synchronization;
* configuration versioning;
* optimistic concurrency;
* audit/history;
* cache;
* error recovery.

The frontend must not become a second source of truth for business rules.

---

## 2. Architectural Principle

The frontend follows this principle:

```text
User Action
    ↓
UI Event
    ↓
Application Action / Command
    ↓
State Update / Request
    ↓
API
    ↓
Backend Business Validation
    ↓
Authoritative Result
    ↓
State Update
    ↓
UI
```

The frontend may provide immediate local feedback, but the backend remains authoritative for business decisions.

---

## 3. State Categories

Frontend state is divided into explicit categories.

```text
Frontend State
│
├── Server State
├── Session State
├── Context State
├── UI State
├── Form State
├── Local/Offline State
├── Derived State
└── Temporary Operation State
```

Each category must have a clearly defined owner.

---

## 4. Server State

Server state represents data owned by the backend.

Examples:

* Products;
* Categories;
* Menu;
* Prices;
* Branch configuration;
* Employees;
* Orders;
* Cash Sessions;
* Inventory;
* Payments;
* Reports;
* Notifications;
* Audit records;
* Subscription;
* Configuration versions.

Server state must not be treated as permanently authoritative inside the browser.

The frontend maintains a synchronized representation of server state.

---

## 5. Session State

Session state represents the currently authenticated operational session.

Examples:

* authenticated employee;
* authentication status;
* access token/session metadata;
* current device;
* session expiration;
* authentication method;
* offline authorization status.

Sensitive authentication material must not be exposed unnecessarily to UI components.

---

## 6. Business Context State

The active Business context identifies which Business the user is currently operating within.

The frontend may display the selected Business but the backend must independently validate the Business context.

Business context includes:

```text
business_id
business_name
subscription_state
business_timezone
business_currency
business_permissions
```

The client-provided `business_id` must never be considered sufficient authorization.

---

## 7. Branch Context State

Branch context identifies the operational Branch currently selected by the employee.

Example:

```text
Current Business
      ↓
Current Branch
      ↓
Branch Permissions
      ↓
Branch Configuration
      ↓
Branch Menu
      ↓
Branch POS State
```

Changing Branch must invalidate or refresh all Branch-scoped state that may differ.

---

## 8. Branch Context Switching

When Branch context changes, the frontend must:

1. stop using previous Branch-scoped operational state;
2. update active Branch context;
3. recalculate visible permissions;
4. refresh Branch configuration;
5. refresh Branch menu/pricing;
6. refresh relevant inventory state;
7. refresh POS-specific state where required;
8. clear incompatible temporary state;
9. load the new Branch state.

The previous Branch state must not accidentally appear as current Branch data.

---

## 9. Permission State

Permissions are server-derived state.

Frontend permissions may be cached for UI rendering, but they are not a security boundary.

The frontend may use permissions to:

* hide unavailable actions;
* disable buttons;
* filter navigation;
* display read-only screens;
* prevent unnecessary requests.

The backend must always revalidate authorization.

---

## 10. Permission State Refresh

Permission-related state must be refreshed when:

* employee logs in;
* Business changes;
* Branch changes;
* employee permissions change;
* employee role changes;
* employee becomes inactive;
* device trust changes where relevant;
* subscription entitlement changes;
* session is refreshed.

Stale permission state must not be used to authorize a sensitive operation.

---

## 11. Subscription State

Subscription state determines whether modifying functionality is available.

Typical states:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

When the Business is `READ_ONLY`:

* viewing remains available;
* permitted exports remain available;
* configuration changes are disabled;
* modifying operations are blocked by backend authorization.

Frontend state must reflect the current entitlement but must not attempt to bypass it.

---

## 12. Server State Ownership

Every server entity must have a clear frontend ownership boundary.

Example:

```text
products/
    → Product server state

orders/
    → Order server state

inventory/
    → Inventory server state

settings/
    → Configuration server state
```

Feature modules should not independently maintain conflicting copies of the same authoritative entity.

---

## 13. Single Source of Frontend Truth

For a given entity, the frontend should maintain one canonical normalized representation where practical.

For example:

```text
Product ID
    ↓
Product Entity
    ↓
Menu references Product ID
POS references Product ID
Order UI references Product snapshot
```

Different screens may derive views from the same underlying state.

---

## 14. Historical Transaction State

Order and financial snapshots must not be replaced by current Product state.

For example:

```text
Current Product Price = 35,000

Historical Order Item Price = 30,000
```

The Order Item snapshot remains 30,000.

Frontend state must preserve this distinction.

---

## 15. Derived State

Derived state is calculated from authoritative state.

Examples:

* Order total;
* remaining payment amount;
* filtered Product list;
* permission visibility;
* dashboard counters;
* inventory warning state;
* current navigation items.

Derived state should not be persisted unless there is a strong architectural reason.

---

## 16. Derived State Rule

A value should be derived instead of duplicated when it can be deterministically calculated from existing state.

For example:

```text
Order Items
   ↓
Subtotal
   ↓
Discount
   ↓
Final Total
```

The frontend may calculate temporary display values, but the backend remains authoritative for financial totals.

---

## 17. UI State

UI state represents temporary presentation behavior.

Examples:

* selected tab;
* modal visibility;
* expanded section;
* active filter;
* sort order;
* selected row;
* sidebar state;
* loading indicator;
* confirmation dialog;
* error banner.

UI state must not be mixed with server state unnecessarily.

---

## 18. Form State

Form state is temporary state belonging to a specific editing workflow.

Examples:

* Employee form;
* Product form;
* Price configuration form;
* Recipe form;
* Branch settings form.

Form state should remain local to the relevant feature unless multiple screens genuinely need it.

---

## 19. Unsaved Changes

Critical configuration forms must track unsaved changes.

Example state:

```text
CLEAN
DIRTY
SAVING
SAVED
ERROR
CONFLICT
```

Navigation away from a dirty critical form should warn the user.

---

## 20. Temporary Operation State

Long-running or asynchronous operations should have explicit state.

Example:

```text
IDLE
↓
STARTING
↓
PROCESSING
↓
SUCCESS / FAILURE
```

This applies to:

* XLSX export;
* report generation;
* synchronization;
* configuration save;
* file upload;
* large imports;
* background operations.

---

## 21. Request State

Network operations should not be represented by a single generic `loading=true`.

Where useful, the frontend should distinguish:

```text
IDLE
LOADING
SUCCESS
ERROR
RETRYING
CANCELLED
```

This prevents unrelated operations from incorrectly affecting each other's UI.

---

## 22. Query State

Server queries should maintain:

* request parameters;
* result;
* loading state;
* error state;
* timestamp/version where useful;
* pagination state;
* stale state.

Example:

```text
Products Query
├── filters
├── sort
├── cursor
├── data
├── isLoading
├── isFetching
├── error
└── lastUpdated
```

---

## 23. Mutation State

Mutations represent operations that modify backend state.

Examples:

* create Order;
* accept Order;
* add payment;
* close Cash Session;
* update Product;
* change price;
* approve Recipe;
* update configuration.

Mutation state should be isolated from unrelated queries.

---

## 24. Mutation Lifecycle

A typical mutation follows:

```text
User Action
    ↓
Validate Local Input
    ↓
Create Operation UUID
    ↓
Send Command
    ↓
Backend Validation
    ↓
Success / Conflict / Error
    ↓
Update State
    ↓
Invalidate / Refresh Related Queries
```

---

## 25. Operation UUID

Retryable modifying commands should carry an operation UUID.

The frontend must generate the operation UUID before sending the command when required by the API contract.

The same operation UUID must be reused when safely retrying the same operation.

A new operation UUID must not be generated for an identical retry of the same command.

---

## 26. Optimistic Updates

Optimistic updates may be used only where incorrect temporary UI state is safe.

Suitable examples may include:

* opening/closing simple UI sections;
* local filters;
* temporary presentation state.

Business-critical operations should normally wait for authoritative backend confirmation.

Examples that should not rely on unsafe optimistic updates:

* payment;
* inventory deduction;
* Cash Session closing;
* refund;
* financial correction;
* configuration approval.

---

## 27. POS State

POS requires a specialized state model because speed is critical.

POS state may include:

```text
Current Order
Order Items
Selected Product
Quantity
Modifiers
Discount
Payment State
Table
Order Type
Cash Session
Print Status
Sync Status
```

POS state should avoid unnecessary global state updates.

---

## 28. POS State Separation

POS state should distinguish:

```text
Draft Order State
      ≠
Server Order State
      ≠
Payment State
      ≠
Print State
      ≠
Synchronization State
```

A printer failure must not make an accepted Order appear unaccepted.

A synchronization failure must not make a locally committed offline transaction disappear.

---

## 29. Order Draft State

Before submission, the Order draft may be maintained locally.

Example:

```text
Product Selection
      ↓
Draft Order
      ↓
Local Validation
      ↓
Submit
      ↓
Server Validation
      ↓
Authoritative Order
```

Draft state must not be confused with a committed Order.

---

## 30. Order Snapshot State

Once an Order Item is accepted by the backend, its relevant snapshot must be represented explicitly.

Examples:

* price;
* quantity;
* discount;
* applicable configuration;
* Recipe Version where relevant;
* Set Version where relevant.

Current Product configuration must not overwrite these values.

---

## 31. Cash Session State

Cash Session state is operationally critical.

Frontend representation should distinguish:

```text
NOT_STARTED
OPENING
OPEN
CLOSING
CLOSED
ERROR
OFFLINE_PENDING_SYNC
```

The backend remains authoritative for the final Cash Session state.

---

## 32. Inventory State

Inventory state should distinguish:

* available stock;
* reserved/operationally unavailable state where applicable;
* low-stock state;
* out-of-stock state;
* loading state;
* synchronization state.

Final inventory deductions must always come from authoritative backend transactions.

---

## 33. Configuration State

Configuration state should include:

```text
CURRENT
PENDING
EFFECTIVE
SUPERSEDED
CONFLICT
READ_ONLY
```

For settings that become effective at the next Cash Session, the frontend should clearly distinguish current configuration from pending configuration.

---

## 34. Configuration Version Tracking

Frontend configuration state should retain the version used when editing.

Example:

```text
Loaded Version: 17
User edits
       ↓
Save with expected_version = 17
       ↓
Server
       ↓
Version 18
```

If the server is already at version 18, the request must be treated as a conflict.

---

## 35. Conflict State

Important conflicts should have explicit frontend state.

Example:

```text
CONFLICT
├── localVersion
├── serverVersion
├── changedBy
├── changedAt
├── localChanges
└── serverChanges
```

The UI should allow the user to review the conflict and intentionally continue.

---

## 36. No Silent Last-Write-Wins

The frontend must never silently replace a newer server configuration with an older local copy.

Conflict resolution must be explicit.

Historical values must remain available where required.

---

## 37. Cache State

Frontend cache is an optimization layer.

It may contain:

* Products;
* Categories;
* Menu;
* Configuration;
* Permissions;
* Reference data;
* recent queries.

Cache must never become the final authority for:

* payment;
* cash;
* inventory deduction;
* financial correction;
* historical transactions;
* deletion;
* subscription lifecycle.

---

## 38. Cache Invalidation

After a successful mutation, related cached state must be invalidated or updated.

Example:

```text
Price Change
   ↓
Price Mutation Success
   ↓
Invalidate Product Price
   ↓
Invalidate Branch Menu
   ↓
Refresh affected POS data
```

Invalidation must be scoped to the relevant Business and Branch.

---

## 39. Cache Isolation

Cache keys must include the necessary scope.

Example:

```text
business:{business_id}:products
business:{business_id}:branch:{branch_id}:menu
business:{business_id}:branch:{branch_id}:pricing
```

A Branch A cache entry must never be reused for Branch B.

A Business A cache entry must never be reused for Business B.

---

## 40. Stale Data

The frontend should be able to identify potentially stale data.

Possible states:

```text
FRESH
STALE
REFETCHING
OFFLINE
UNKNOWN
```

Stale data may remain visible for non-critical read operations while a refresh is performed.

Critical actions require authoritative validation.

---

## 41. Offline State

Offline state is separate from ordinary network error state.

Example:

```text
ONLINE
CONNECTING
OFFLINE
RECONNECTING
SYNCING
SYNC_ERROR
```

The user must be able to distinguish:

* internet unavailable;
* backend unavailable;
* synchronization pending;
* synchronization failed.

---

## 42. Offline Local State

Offline-capable features may maintain local state for:

* authorized POS operations;
* trusted-device configuration;
* local Order drafts;
* accepted offline transactions;
* synchronization queue;
* synchronization results.

Local offline state must be encrypted and bound to the trusted device according to the security architecture.

---

## 43. Offline Transaction Queue

Offline modifying operations should be represented explicitly.

Example:

```text
PENDING
   ↓
UPLOADING
   ↓
ACCEPTED
   ├── SERVER_APPLIED
   └── ALREADY_APPLIED
   ↓
COMPLETED
```

Failure states:

```text
RETRYABLE_FAILURE
CONFLICT
REJECTED
EXPIRED
```

---

## 44. Synchronization State

Synchronization state should be observable without exposing unnecessary technical complexity.

The UI may show:

* pending operations;
* synchronization progress;
* last successful synchronization;
* failed operations;
* conflicts requiring attention.

Normal POS workflows should not be blocked unnecessarily by background synchronization.

---

## 45. Transaction Synchronization Priority

When reconnecting:

```text
Offline Transactions
        ↓
Transaction Synchronization
        ↓
Configuration Synchronization
        ↓
Cache Refresh
```

This preserves historical transaction integrity.

---

## 46. Synchronization Result Handling

The frontend must process synchronization results individually when the backend supports partial success.

Example:

```text
Batch 100 operations

95 → accepted
3  → retryable
1  → conflict
1  → rejected
```

The frontend must not mark the entire batch as failed when individual operations succeeded.

---

## 47. Authentication State

Authentication state should explicitly represent:

```text
UNKNOWN
AUTHENTICATING
AUTHENTICATED
SESSION_EXPIRED
REAUTH_REQUIRED
LOGGED_OUT
AUTH_ERROR
```

The application must not assume authentication merely because local UI state says `authenticated`.

---

## 48. Session Expiration

When the backend reports session expiration:

1. stop protected operations;
2. preserve safe local form state where possible;
3. request re-authentication if supported;
4. redirect to authentication UI when necessary;
5. avoid losing unsaved user work unnecessarily.

Sensitive state must not remain accessible after logout.

---

## 49. Logout

Logout should clear:

* authenticated session state;
* active Business/Branch context;
* permission-derived state;
* sensitive cached data;
* temporary operational state;
* protected offline access state according to security policy.

Logout does not automatically mean Cash Session closure.

---

## 50. Global Application State

Only genuinely global state should live at application level.

Suitable examples:

* authentication;
* current Business;
* current Branch;
* device state;
* subscription entitlement;
* global UI preferences;
* connectivity state.

Feature-specific state should remain inside the relevant feature.

---

## 51. Feature State

Each major feature should own its local state boundaries.

Example:

```text
features/
├── pos/
├── orders/
├── inventory/
├── products/
├── menu/
├── cash/
├── reports/
└── settings/
```

A feature should not directly mutate another feature's internal state.

Communication should use shared application services, queries, commands or domain events where appropriate.

---

## 52. Cross-Feature Data Flow

Example:

```text
Menu Price Change
       ↓
Configuration Mutation
       ↓
Backend Success
       ↓
Configuration Event / Cache Invalidation
       ↓
POS Price Query Refresh
       ↓
New Order uses new effective price
```

Existing Order Item snapshots remain unchanged.

---

## 53. Domain Events in Frontend

Frontend events may be used for coordination between independent UI features.

Examples:

```text
ORDER_ACCEPTED
PAYMENT_COMPLETED
CASH_SESSION_OPENED
CASH_SESSION_CLOSED
CONFIGURATION_UPDATED
BRANCH_CHANGED
SYNC_COMPLETED
SYNC_CONFLICT
```

Frontend events must not replace backend business events.

---

## 54. Event Handling

Events should be:

* explicit;
* typed;
* scoped;
* predictable;
* idempotent where applicable.

An event handler must not accidentally trigger an infinite update loop.

---

## 55. Query Invalidation

When a mutation changes server data, only affected queries should be invalidated where practical.

Example:

```text
Product Price Update
        ↓
Invalidate:
    Product Detail
    Branch Menu
    Pricing Query

Do not invalidate:
    Payroll
    Attendance
    Audit lists unrelated to the Product
```

This protects frontend performance.

---

## 56. Pagination State

Large lists should use pagination.

State should include:

* page/cursor;
* filters;
* sort;
* total metadata where available;
* loading state;
* next/previous availability.

Cursor pagination should be preferred for large or frequently changing datasets where supported by the backend.

---

## 57. Search State

Search input state and server query state should be separated.

Example:

```text
User Input
   ↓
Debounce
   ↓
Search Query
   ↓
Server Result
```

A user typing a new search term must not unnecessarily cancel or corrupt unrelated data.

POS product search should remain optimized for fast interaction.

---

## 58. Filter State

Filters should be represented as typed state.

Example:

```text
date_from
date_to
branch_id
status
employee_id
category_id
```

Invalid filter combinations should be rejected locally where possible.

Backend validation remains authoritative.

---

## 59. Sorting State

Sorting state should use an explicit model:

```text
field
direction
```

Only supported backend sorting fields may be submitted.

The frontend must not construct arbitrary SQL-like expressions.

---

## 60. Report State

Reports may have longer-running states:

```text
IDLE
LOADING
READY
GENERATING
EXPORTING
ERROR
```

Large report generation should not block the main UI.

XLSX exports should use the backend asynchronous export mechanism.

---

## 61. Notification State

Notification state should distinguish:

* unread count;
* notification list;
* loading;
* read/unread changes;
* synchronization;
* errors.

Reading a notification should not grant any permission.

---

## 62. Audit and History State

Audit/history screens should use server-side filtering and pagination.

Frontend state may include:

* selected event;
* filters;
* date range;
* entity type;
* actor;
* Branch;
* result;
* expanded detail.

Large audit datasets must not be loaded entirely into browser memory.

---

## 63. State Persistence

Only state that must survive page reload or offline operation should be persisted.

Suitable examples:

* selected non-sensitive UI preferences;
* offline transaction queue;
* trusted-device-bound offline state;
* limited navigation preferences.

Do not persist sensitive server data unnecessarily.

---

## 64. Sensitive State

Sensitive state includes:

* authentication credentials;
* session secrets;
* offline authorization material;
* financial information where unnecessary;
* private employee information.

Sensitive data must use the security-approved storage mechanism.

Frontend components should receive only the minimum data required.

---

## 65. Local Storage Rule

Browser persistence must not automatically become the default state-management mechanism.

The architecture must distinguish:

```text
Memory State
Cache State
Persistent Local State
Secure Offline State
Server State
```

Each has a different lifecycle.

---

## 66. State Hydration

Application startup should follow a predictable sequence.

```text
Application Start
      ↓
Load Environment/Static Configuration
      ↓
Initialize Secure Session
      ↓
Validate Authentication
      ↓
Load Business Context
      ↓
Load Branch Context
      ↓
Load Permissions/Entitlements
      ↓
Initialize Feature State
      ↓
Render Application
```

Offline startup follows the approved trusted-device flow.

---

## 67. Initial Loading

The frontend should avoid blocking the entire application while unrelated data loads.

For example:

```text
Application Shell
   ↓
Authentication
   ↓
Context
   ↓
Core Navigation
   ↓
Feature Data
```

Independent feature data may load progressively.

---

## 68. Loading Boundaries

Loading indicators should exist at meaningful boundaries.

Examples:

* page-level;
* table-level;
* card-level;
* form-level;
* action-level.

A single full-screen spinner should not be used for every request.

---

## 69. Error State

Every important stateful operation must have an explicit error state.

Error categories should align with backend error contracts:

```text
VALIDATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
BUSINESS_RULE_VIOLATION
TEMPORARY_ERROR
PERMANENT_FAILURE
NETWORK_ERROR
OFFLINE
```

---

## 70. Error Recovery

Recovery should depend on error type.

Examples:

```text
401 → Re-authenticate

403 → Show access restriction

409 → Refresh/review conflict

Temporary Error → Retry

Validation Error → Correct form

Offline → Queue if operation supports offline mode
```

The frontend must not retry unsafe operations blindly.

---

## 71. Retry Policy

Automatic retry is allowed only for operations that are:

* known to be retryable;
* safe or idempotent;
* not rejected by business rules;
* not caused by authorization failure.

Payment, refund and other financial commands must follow explicit API idempotency behavior.

---

## 72. Race Conditions

The frontend must protect against stale responses.

Example:

```text
Request A → Product search: "bur"
Request B → Product search: "burger"

B returns first
A returns later
```

The UI must not replace the newer result with the older response.

---

## 73. Request Cancellation

Requests that are no longer relevant may be cancelled where supported.

Examples:

* old search requests;
* navigation-away requests;
* abandoned report previews.

Cancellation must not be treated as a business operation failure.

---

## 74. Concurrent Mutations

Multiple UI actions against the same resource must be handled deliberately.

Example:

```text
User A → Price Version 10
User B → Price Version 10

User A → Version 11
User B → Conflict
```

The frontend must show the conflict instead of silently overwriting Version 11.

---

## 75. State Reset Rules

State must be reset when its security or scope boundary changes.

Examples:

```text
Logout
→ clear protected state

Business change
→ clear Business-scoped temporary state

Branch change
→ clear Branch-scoped temporary state

Employee change
→ refresh permissions

Subscription change
→ refresh entitlement
```

---

## 76. Business Isolation in State

Frontend state must never reuse data across Businesses.

All Business-scoped query/cache/state identifiers must include Business context where required.

A Business switch should invalidate incompatible cached state.

---

## 77. Branch Isolation in State

Branch-scoped data must include Branch identity.

Example:

```text
branch:A:menu
branch:B:menu
```

The UI must never display Branch A inventory as Branch B inventory.

---

## 78. Device Context

Device state may include:

* device UUID;
* trust status;
* offline authorization status;
* last synchronization;
* device status.

Device UUID itself is not authentication.

---

## 79. Connectivity State

Connectivity should be represented independently from application errors.

Example:

```text
ONLINE
DEGRADED
OFFLINE
RECONNECTING
```

A successful internet connection does not automatically mean that the backend is healthy.

Where possible, backend health and network connectivity should be distinguished.

---

## 80. Offline UI Rules

When offline:

* show clear offline status;
* allow only supported offline operations;
* show pending synchronization;
* prevent unsupported operations;
* do not pretend that server state has been updated;
* preserve transaction status accurately.

---

## 81. Sync Conflict UI

Synchronization conflicts must be visible when user action is required.

The UI should show:

* affected operation;
* conflict type;
* local state;
* server state;
* required action;
* result after resolution.

The user must not be forced to understand internal synchronization identifiers.

---

## 82. State Consistency

Frontend consistency has three levels:

```text
Local UI Consistency
       ↓
Server Synchronization Consistency
       ↓
Business Transaction Consistency
```

Business transaction consistency is always determined by the backend.

---

## 83. State Update Ordering

When a mutation succeeds:

1. accept authoritative response;
2. update the affected entity;
3. update derived state;
4. invalidate affected queries;
5. publish relevant frontend event;
6. update notifications where applicable.

The UI must not update dependent state before authoritative confirmation when doing so could mislead the user.

---

## 84. Server Response as Authority

When a mutation response contains normalized or corrected data, the frontend should use the server result.

Example:

```text
Client sends:
price = 30000

Server returns:
price = 30000
version = 18
effective_session = 42
```

The frontend must use the authoritative version/effective metadata returned by the server.

---

## 85. Data Flow for Read Operations

Typical read flow:

```text
Component
   ↓
Feature Query
   ↓
Cache Check
   ↓
Cached Data?
 ┌───────┴───────┐
Yes              No
 ↓                ↓
Render        API Request
                  ↓
             Backend
                  ↓
             Validate Scope
                  ↓
              Database
                  ↓
             API Response
                  ↓
             Update Cache
                  ↓
                UI
```

---

## 86. Data Flow for Write Operations

Typical write flow:

```text
User Action
   ↓
Local Validation
   ↓
Permission/Entitlement UI Check
   ↓
Create Operation UUID
   ↓
API Command
   ↓
Authentication
   ↓
Authorization
   ↓
Business Validation
   ↓
Transaction
   ↓
Authoritative Result
   ↓
Frontend State Update
   ↓
Cache Invalidation
   ↓
UI Confirmation
```

---

## 87. Offline Write Flow

```text
User Action
   ↓
Local Validation
   ↓
Offline Authorization Check
   ↓
Create Operation UUID
   ↓
Encrypted Local Persistence
   ↓
Immediate Local Result
   ↓
Pending Sync
   ↓
Reconnect
   ↓
Server Validation
   ↓
Apply / Reject / Conflict
   ↓
Sync Result
   ↓
Final State
```

---

## 88. State Machine Discipline

Important frontend states should use explicit state machines rather than unrelated booleans.

Avoid:

```text
isLoading
isSaving
hasError
isOffline
isConflict
```

when combinations can become contradictory.

Prefer:

```text
status = "saving"
```

with separate contextual metadata where necessary.

---

## 89. Boolean State Rule

Multiple booleans may be used for independent concerns.

For mutually exclusive states, use an explicit enum/state machine.

This reduces impossible states such as:

```text
isLoading = true
isSaved = true
isError = true
```

at the same time.

---

## 90. State Naming

State names must describe meaning rather than implementation.

Prefer:

```text
currentBranch
selectedProduct
cashSessionStatus
syncStatus
configurationVersion
```

Avoid:

```text
data1
tempData
flag2
currentStuff
```

---

## 91. State Ownership Rule

Every important state variable must have an identifiable owner.

Example:

```text
Authentication → application/session layer

Current Branch → application context

Order Draft → POS feature

Product Query → Product feature/query layer

Modal Visibility → component/UI state
```

Duplicated ownership should be avoided.

---

## 92. State Mutation Rule

Components should not directly mutate shared state.

Preferred:

```text
Component
   ↓
Action / Command
   ↓
State Layer
```

This makes state changes traceable and testable.

---

## 93. API Contract Integration

Frontend state types must correspond to API contracts.

API changes must not be silently adapted through scattered component-specific transformations.

Mapping should occur at a defined boundary where necessary.

---

## 94. DTO Mapping

Backend DTOs and frontend view models may differ.

Example:

```text
API DTO
   ↓
Mapper
   ↓
Frontend Model
   ↓
UI
```

This protects UI components from backend transport details.

---

## 95. API Error Mapping

Backend error codes should be mapped centrally.

Example:

```text
CONFLICT
   ↓
ConflictError
   ↓
Conflict UI

SUBSCRIPTION_READ_ONLY
   ↓
ReadOnlyState
   ↓
Read-only UI
```

Feature components should not independently parse raw HTTP responses.

---

## 96. State and Permissions

UI visibility should use permission-derived selectors.

Example:

```text
canEditPrice
canRefund
canCloseCashSession
canViewRecipe
```

These are derived permissions, not independent security rules.

---

## 97. State and Subscription

Entitlement selectors may expose:

```text
canModify
canExport
canUseFeature
isReadOnly
```

Backend authorization remains authoritative.

---

## 98. State and Audit

Frontend state changes that trigger important backend operations should preserve operation context where relevant.

The frontend should provide:

* operation UUID;
* request context where API contract requires;
* reason/comment;
* selected Business/Branch context.

The backend creates authoritative audit records.

---

## 99. State and Notifications

Important backend events may update notification state.

Example:

```text
Inventory Variance
    ↓
Backend Event
    ↓
Notification
    ↓
Frontend Notification State
    ↓
Unread Badge
```

Notifications should not be fabricated by the frontend for authoritative business events.

---

## 100. State and Reports

Reports should use server-generated authoritative data.

Frontend filters may control query parameters but must not reconstruct financial reports from incomplete client state.

---

## 101. State and File Operations

File uploads/downloads/exports should maintain independent operation state.

Example:

```text
Export Request
   ↓
QUEUED
   ↓
PROCESSING
   ↓
READY
   ↓
DOWNLOAD
```

Large files should not be loaded into frontend memory unnecessarily.

---

## 102. Background Operation State

Background jobs should expose user-friendly state.

Internal queue implementation details should not leak into ordinary UI.

Instead of:

```text
Redis worker 17 retry 2
```

the user should see:

```text
Export is being prepared.
```

Detailed technical information may remain available to administrators through appropriate diagnostics.

---

## 103. State Persistence Boundaries

State persistence must respect lifecycle boundaries.

Examples:

```text
Logout
→ clear session-bound state

Business deletion
→ no restoration from frontend cache

Subscription read-only
→ block modifications

Branch switch
→ discard incompatible Branch temporary state

Device revocation
→ invalidate protected offline state
```

---

## 104. Memory Management

The frontend must avoid unbounded state growth.

Examples:

* paginate large lists;
* limit cached history;
* release unused feature state where practical;
* avoid storing entire reports unnecessarily;
* avoid duplicate copies of large datasets.

---

## 105. POS Memory Strategy

POS should keep only the data necessary for rapid operation.

Large historical datasets should not be loaded into the POS state.

Examples:

```text
Menu
Products
Current Order
Current Cash Session
Required configuration
Pending offline transactions
```

Historical reports remain separate.

---

## 106. Performance Targets

The frontend state architecture should target:

| Metric                                      |                                        Target |
| ------------------------------------------- | --------------------------------------------: |
| Local state update                          |                                   p95 ≤ 16 ms |
| Local selector/derived calculation          |                                   p95 ≤ 16 ms |
| UI response after user action               |                                  p95 ≤ 100 ms |
| Local navigation                            |                                  p95 ≤ 100 ms |
| POS product search                          |                                  p95 ≤ 150 ms |
| Cached server-state read                    |                                   p95 ≤ 50 ms |
| Normal server query rendering               |                                  p95 ≤ 300 ms |
| State hydration after authenticated startup |                                   p95 ≤ 1.5 s |
| Branch context switch UI response           | p95 ≤ 300 ms after required data is available |
| Conflict rendering                          |                                  p95 ≤ 300 ms |
| Offline queue insertion                     |                                   p95 ≤ 50 ms |
| State-related fatal UI errors               |                            < 0.1% of sessions |

These targets apply under normal supported hardware and network conditions.

---

## 107. State Performance Rules

The frontend must:

* avoid unnecessary global re-renders;
* use selective subscriptions;
* memoize expensive derived calculations where justified;
* paginate large datasets;
* avoid storing duplicate large objects;
* avoid unnecessary cache invalidation;
* keep POS state lightweight;
* process synchronization incrementally;
* avoid blocking the main thread with heavy computation.

---

## 108. Main Thread Protection

The browser main thread must remain responsive.

Heavy work such as:

* large report transformation;
* large XLSX processing;
* large synchronization batches;
* expensive data transformations

should be delegated to backend jobs or Web Workers where appropriate.

---

## 109. Synchronization UI Performance

Synchronization must not freeze POS interaction.

Sync processing should:

* run incrementally;
* process bounded batches;
* yield to normal UI work;
* expose progress only where useful;
* retry safely;
* preserve operation ordering requirements.

---

## 110. State Testing

State architecture must be tested at several levels.

### Unit Tests

Test:

* reducers/state transitions;
* selectors;
* derived state;
* validation;
* mappers;
* error mapping;
* permission selectors.

### Integration Tests

Test:

* API → state;
* mutation → cache invalidation;
* Branch switch → state reset;
* logout → protected state cleanup;
* sync → final state.

### End-to-End Tests

Test:

* login;
* Branch switching;
* POS order;
* payment;
* Cash Session;
* offline operation;
* synchronization;
* configuration conflict;
* subscription read-only behavior.

---

## 111. State Invariants

The following invariants apply to frontend state management:

1. Backend remains authoritative for business decisions.
2. Frontend state is not a security boundary.
3. Business-scoped state cannot cross Business boundaries.
4. Branch-scoped state cannot cross Branch boundaries.
5. Authentication state is explicit.
6. Logout clears protected session state.
7. Branch switching clears incompatible Branch-scoped temporary state.
8. Business switching clears incompatible Business-scoped temporary state.
9. Permissions are server-derived.
10. Subscription entitlement is server-derived.
11. Client permissions never replace backend authorization.
12. Current Product state does not overwrite historical Order snapshots.
13. Current Product price does not overwrite historical Order prices.
14. Financial totals remain backend-authoritative.
15. Inventory deductions remain backend-authoritative.
16. Cash Session state remains backend-authoritative.
17. Payment state remains backend-authoritative.
18. Refund state remains backend-authoritative.
19. Important mutations use operation UUIDs where required.
20. Safe retries reuse the same operation UUID.
21. Unsafe mutations are not blindly retried.
22. Optimistic updates are not used to fake financial success.
23. Configuration versions are tracked during editing.
24. Stale configuration updates become conflicts.
25. Silent last-write-wins is prohibited for important configuration.
26. Cache is not authoritative.
27. Cache keys contain required Business scope.
28. Branch cache is Branch-isolated.
29. Cache invalidation follows successful mutations.
30. Offline state is distinct from ordinary network failure.
31. Offline operations require valid trusted-device authorization.
32. Offline transactions are persisted safely.
33. Offline transaction synchronization precedes configuration synchronization.
34. Partial synchronization results are handled individually.
35. Sync conflicts remain visible until resolved.
36. Stale responses cannot overwrite newer query results.
37. Search state and server query state are distinct.
38. Large lists use pagination.
39. Audit/history data is not loaded entirely into browser memory.
40. Reports remain server-authoritative.
41. Large exports are asynchronous.
42. Background operations do not block normal POS interaction.
43. UI state is not unnecessarily mixed with server state.
44. Form state remains local where practical.
45. Critical forms track unsaved changes.
46. Critical configuration saves are explicit.
47. State ownership is identifiable.
48. Shared state is mutated through controlled actions.
49. Components do not directly mutate shared state.
50. API DTO mapping occurs at a defined boundary.
51. Raw backend errors are not parsed independently by every component.
52. Permission selectors describe UI capability, not security authority.
53. Entitlement selectors describe UI availability, not security authority.
54. Device UUID is not treated as authentication.
55. Session expiration is handled explicitly.
56. Re-authentication does not automatically close Cash Sessions.
57. Protected state is cleared after logout.
58. Device revocation invalidates protected offline state according to policy.
59. Subscription read-only state disables modification UI.
60. Read-only UI cannot bypass backend restrictions.
61. State hydration follows a predictable startup sequence.
62. Unrelated data does not block initial application rendering unnecessarily.
63. Full-screen loading is not used for every request.
64. Loading state is scoped to the relevant operation.
65. Error state is explicit.
66. Error recovery depends on error type.
67. Temporary errors may be retried when safe.
68. Authorization errors are not blindly retried.
69. Validation errors are not blindly retried.
70. Conflicts require explicit handling.
71. Network connectivity and backend availability are distinguishable where possible.
72. Offline mode does not pretend that server state has been updated.
73. Synchronization status is visible where user action is required.
74. Frontend events do not replace backend domain events.
75. Frontend event handlers are bounded and predictable.
76. Query invalidation is scoped.
77. State reset occurs at security/context boundaries.
78. Sensitive state is persisted only when required.
79. Local persistence uses approved security mechanisms.
80. State growth is bounded.
81. Large datasets are not unnecessarily duplicated.
82. POS state remains lightweight.
83. Heavy computation does not unnecessarily block the main thread.
84. Synchronization does not freeze POS interaction.
85. UI state updates should remain within defined performance targets.
86. State hydration should remain within defined startup targets.
87. State-related fatal UI errors remain below the defined threshold.
88. State transitions are deterministic.
89. Mutually exclusive states use explicit state machines.
90. Impossible state combinations should be prevented.
91. State names describe business/UI meaning clearly.
92. Feature modules own their internal state.
93. Cross-feature communication uses defined boundaries.
94. API contracts define expected server state shape.
95. Server responses can correct local assumptions.
96. Historical data remains reconstructable.
97. Current configuration cannot reinterpret historical transactions.
98. Offline data cannot bypass subscription restrictions.
99. Frontend cache cannot resurrect deleted Business data.
100. Frontend state must never override server-authoritative lifecycle state.
101. Security-sensitive state must not be exposed unnecessarily.
102. State updates must be attributable to an operation where required.
103. State persistence must respect Business and Branch scope.
104. State must remain compatible with the backend synchronization model.
105. Frontend state management must preserve historical integrity over UI convenience.

---

## 112. Recommended Frontend Structure

The state architecture may be organized as:

```text
frontend/
└── src/
    ├── app/
    │   ├── providers/
    │   ├── routing/
    │   ├── session/
    │   ├── context/
    │   ├── connectivity/
    │   └── state/
    │
    ├── core/
    │   ├── api/
    │   ├── auth/
    │   ├── cache/
    │   ├── errors/
    │   ├── events/
    │   ├── permissions/
    │   ├── subscriptions/
    │   └── synchronization/
    │
    ├── features/
    │   ├── pos/
    │   │   ├── state/
    │   │   ├── queries/
    │   │   ├── mutations/
    │   │   └── selectors/
    │   ├── orders/
    │   ├── cash/
    │   ├── inventory/
    │   ├── products/
    │   ├── menu/
    │   ├── reports/
    │   ├── notifications/
    │   └── settings/
    │
    ├── shared/
    │   ├── components/
    │   ├── types/
    │   ├── validation/
    │   └── utilities/
    │
    └── offline/
        ├── storage/
        ├── queue/
        ├── synchronization/
        ├── conflict/
        └── security/
```

---

## 113. State Management Technology

The exact state-management library is an implementation decision and must not change the architectural rules defined here.

The selected technology must support:

* predictable state transitions;
* server-state caching;
* query invalidation;
* mutation lifecycle;
* offline persistence where required;
* selective subscriptions;
* testability;
* TypeScript compatibility;
* low runtime overhead.

The architecture should avoid introducing multiple overlapping state-management libraries without a clear responsibility boundary.

---

## 114. Recommended State Layers

The frontend should conceptually maintain:

```text
Application State
       ↓
Feature State
       ↓
Server Query/Cache State
       ↓
Local UI/Form State
       ↓
Offline Persistent State
```

Each layer must have a defined purpose.

---

## 115. AI-Agent Development Rules

AI-assisted development must follow the state ownership architecture.

An AI coding agent must not:

* create duplicate global stores without justification;
* put server state into arbitrary component state;
* bypass query/cache boundaries;
* directly mutate shared state;
* introduce hidden persistence;
* store sensitive credentials in local storage;
* bypass Business/Branch scope;
* implement frontend-only authorization;
* silently ignore conflicts;
* replace historical snapshots with current data.

Before changing state architecture, the agent should inspect:

```text
Frontend Architecture
Project Structure
API Contract
Authentication
Business/Branch Context
Offline/Sync
Relevant Feature Document
```

---

## 116. Change Management

A state-management change should identify:

* affected state category;
* state owner;
* affected features;
* API contract impact;
* cache impact;
* offline impact;
* synchronization impact;
* permission impact;
* subscription impact;
* testing requirements;
* performance impact.

Large state architecture changes should be documented through an ADR when they introduce a new architectural pattern.

---

## 117. Relationship with Backend

The frontend state architecture directly depends on:

* Backend API contracts;
* authentication/authorization architecture;
* transaction management;
* cache architecture;
* synchronization architecture;
* audit/history architecture;
* configuration/versioning;
* database consistency rules.

The frontend must not independently redefine backend business rules.

---

## 118. Relationship with Offline Architecture

Offline frontend state must remain compatible with:

* trusted device;
* signed offline authorization;
* offline grace period;
* encrypted local storage;
* operation UUID;
* synchronization queue;
* partial synchronization;
* conflict resolution;
* clock rollback detection;
* subscription restrictions.

The frontend must not create a separate offline business model.

---

## 119. Relationship with Historical Integrity

Frontend state must preserve historical integrity by distinguishing:

```text
Current State
      ≠
Pending State
      ≠
Historical Snapshot
      ≠
Offline Pending Transaction
```

This distinction is mandatory for:

* Orders;
* prices;
* payments;
* refunds;
* inventory;
* recipes;
* Sets;
* configuration;
* Cash Sessions;
* reports.

---

## 120. Final Architectural Principles

The FastFood ERP frontend state architecture follows these principles:

1. Backend is authoritative.
2. Frontend state is organized by responsibility.
3. Server state is different from UI state.
4. Business and Branch scopes are explicit.
5. Permissions and entitlements are server-derived.
6. Cache is optimization only.
7. Financial operations are authoritative and transaction-based.
8. Historical snapshots are never silently replaced.
9. Offline state is explicit and secure.
10. Synchronization is observable and recoverable.
11. Important conflicts are explicit.
12. Retry behavior is controlled by idempotency.
13. POS state is lightweight and performance-oriented.
14. Large data is paginated and bounded.
15. State ownership is clear.
16. Shared state changes are traceable.
17. Sensitive state is minimized.
18. State persistence follows lifecycle boundaries.
19. UI must not pretend that an operation succeeded before authoritative confirmation.
20. Frontend architecture must preserve the correctness, security and historical integrity of the FastFood ERP backend.

---

## Related Documents

### Frontend

* `docs/04_Architecture/07_Frontend/01_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/02_Frontend_Project_Structure.md`
* `docs/04_Architecture/07_Frontend/03_Design_System_and_UI_Principles.md`
* `docs/04_Architecture/07_Frontend/04_Application_Layout_and_Navigation.md`
* `docs/04_Architecture/07_Frontend/05_Authentication_and_Session_UI.md`
* `docs/04_Architecture/07_Frontend/06_Role_Permission_and_Access_Control_UI.md`
* `docs/04_Architecture/07_Frontend/07_Business_and_Branch_Context.md`
* `docs/04_Architecture/07_Frontend/08_Dashboard_Architecture.md`
* `docs/04_Architecture/07_Frontend/09_POS_Frontend_Architecture.md`
* `docs/04_Architecture/07_Frontend/10_Order_Management_UI.md`
* `docs/04_Architecture/07_Frontend/11_Cash_Register_and_Cash_Session_UI.md`
* `docs/04_Architecture/07_Frontend/12_Inventory_and_Warehouse_UI.md`
* `docs/04_Architecture/07_Frontend/13_Products_Recipes_and_Sets_UI.md`
* `docs/04_Architecture/07_Frontend/14_Menu_and_Pricing_UI.md`
* `docs/04_Architecture/07_Frontend/15_Attendance_and_Payroll_UI.md`
* `docs/04_Architecture/07_Frontend/16_Reports_and_Dashboard_UI.md`
* `docs/04_Architecture/07_Frontend/17_Notifications_and_Alerts_UI.md`
* `docs/04_Architecture/07_Frontend/18_Audit_and_History_UI.md`
* `docs/04_Architecture/07_Frontend/19_Subscription_and_Entitlement_UI.md`
* `docs/04_Architecture/07_Frontend/20_Offline_Mode_and_Synchronization_UI.md`
* `docs/04_Architecture/07_Frontend/21_Settings_and_Business_Configuration_UI.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`

### Database

* `docs/04_Architecture/05_Database/02_Database_Architecture.md`
* `docs/04_Architecture/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/04_Architecture/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/04_Architecture/05_Database/23_Configuration_Data_Model.md`
* `docs/04_Architecture/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/04_Architecture/05_Database/30_Database_Invariants_and_Guardrails.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

---

## Status

**Frontend Architecture:** Proposed

**Version:** 1.0

**Current Document:** `22_Frontend_State_Management_and_Data_Flow.md`

**Previous Document:** `21_Settings_and_Business_Configuration_UI.md`

**Next Document:** `23_Frontend_API_Client_and_Data_Access_Architecture.md`

