# Frontend Architecture

**Document ID:** FA-01
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the frontend architecture for FastFood ERP.

The frontend must provide a fast, simple and reliable user experience for:

* POS operations;
* cashier workflows;
* branch management;
* inventory;
* products and recipes;
* menu and pricing;
* attendance and payroll;
* reports;
* dashboards;
* notifications;
* administration;
* offline operation;
* synchronization.

The frontend architecture must support the existing Business Analysis, System Analysis, Database and Backend architecture without duplicating business authority on the client.

The frontend is responsible for:

* presentation;
* user interaction;
* local UI state;
* client-side validation;
* local offline state where required;
* API communication;
* synchronization orchestration;
* optimistic UI where safe;
* error presentation;
* accessibility;
* performance.

The frontend is not authoritative for business rules.

---

# 2. Architectural Principles

The frontend follows these principles:

1. Server state is authoritative for online business data.
2. PostgreSQL remains the ultimate business source of truth.
3. Backend authorization is authoritative.
4. Frontend authorization is primarily a UX and navigation control.
5. Important business rules must be enforced by the backend.
6. Offline operation must be explicitly supported rather than accidentally tolerated.
7. POS workflows must remain fast and simple.
8. UI complexity must not reflect backend complexity unnecessarily.
9. Feature modules must remain independently understandable.
10. Shared components must remain small and reusable.
11. Global state must be minimized.
12. Remote server state must not be confused with local UI state.
13. Cache must never become business authority.
14. Historical data must be displayed without rewriting it.
15. Errors must be recoverable where possible.
16. Offline conflicts must be visible and understandable.
17. Sensitive data must not be unnecessarily persisted in the browser/device.
18. Accessibility must be considered from the beginning.
19. Performance must be measured rather than assumed.
20. Architecture must support future frontend scaling without requiring an immediate microfrontend architecture.

---

# 3. Frontend Architectural Style

The initial frontend should use a **modular application architecture**.

A single frontend application is preferred initially.

The architecture should not begin with multiple independently deployed microfrontends unless actual organizational or technical requirements justify them.

Conceptually:

```text
Frontend Application
│
├── Application Shell
│
├── Authentication
├── Business / Branch Context
├── Dashboard
├── POS
├── Orders
├── Cash
├── Inventory
├── Products
├── Recipes
├── Sets
├── Menu
├── Pricing
├── Attendance
├── Payroll
├── Reports
├── Notifications
├── Administration
├── Offline / Synchronization
│
├── Shared UI
├── Shared Utilities
└── API / Data Layer
```

---

# 4. Frontend Responsibility Boundary

The frontend owns:

```text
User Interaction
UI State
Navigation
Rendering
Form State
Local Validation
Client Cache
Offline UI State
Sync UI
Accessibility
Presentation
```

The backend owns:

```text
Authentication Authority
Authorization Authority
Business Rules
Financial Calculations
Inventory Authority
Order Authority
Cash Authority
Subscription Authority
Historical Integrity
Audit Authority
Concurrency
Idempotency
Lifecycle
```

The frontend must not attempt to replace the backend authority.

---

# 5. Backend Authority

The frontend may display:

```text
Can user perform X?
```

but the backend remains responsible for determining:

```text
Is user actually authorized to perform X?
```

For example:

```text
Frontend:
Hide "Delete" button

Backend:
Reject unauthorized delete request
```

Both are required.

Hiding a button is not a security mechanism.

---

# 6. Application Shell

The Application Shell provides the common application environment.

It is responsible for:

* application initialization;
* authentication restoration;
* Business context;
* Branch context;
* navigation;
* global notifications;
* theme;
* responsive layout;
* connection state;
* offline status;
* synchronization status;
* global error boundary;
* application version information.

The shell must remain lightweight.

---

# 7. Application Initialization

Application startup should follow a controlled sequence.

Recommended:

```text
Application Start
      ↓
Load Runtime Configuration
      ↓
Restore Authentication State
      ↓
Validate Session
      ↓
Load Business Context
      ↓
Load Branch Context
      ↓
Load Effective Permissions
      ↓
Load Required UI Configuration
      ↓
Initialize Offline Context
      ↓
Render Application
```

Not every resource must block initial rendering.

Non-critical data should load asynchronously.

---

# 8. Critical vs Non-Critical Initialization

Critical initialization includes:

* authentication state;
* active Business context;
* active Branch context where required;
* security/session state;
* minimum permission context.

Non-critical initialization may include:

* dashboard widgets;
* notification history;
* analytics;
* secondary reference data;
* historical reports.

The frontend must avoid unnecessary startup blocking.

---

# 9. Application Context

The frontend should maintain an explicit application context.

Conceptually:

```text
Application Context
├── Employee
├── Business
├── Branch
├── Device
├── Permissions
├── Subscription
├── Connectivity
├── Offline Authorization
└── Application Version
```

The context must be refreshed when relevant state changes.

---

# 10. Business Context

The current Business determines the tenant scope of the frontend.

The frontend must not trust a client-provided Business UUID as proof of access.

The backend validates Business access.

Frontend Business context is therefore:

* navigation context;
* data-loading context;
* display context;
* request context.

It is not an authorization authority.

---

# 11. Branch Context

Branch context must be explicit.

Example:

```text
Business
   ↓
Branch Selector
   ↓
Current Branch
   ↓
Branch-scoped UI
```

When Branch changes, the frontend must refresh:

* effective permissions;
* menu;
* pricing;
* inventory context;
* cash context;
* branch-specific dashboard data;
* branch-specific configuration.

Previous Branch state must not accidentally remain active.

---

# 12. Branch Switching

Branch switching must be treated as a context transition.

Recommended flow:

```text
Select Branch
    ↓
Validate availability
    ↓
Clear/invalidate branch-scoped state
    ↓
Load new Branch context
    ↓
Recalculate UI permissions
    ↓
Load Branch configuration
    ↓
Render Branch-specific UI
```

The frontend must not display stale Branch A data after switching to Branch B.

---

# 13. Permission Model

Frontend permission checks should follow the backend model:

```text
Role Permission
+
Employee Override
+
Branch Scope
+
Employee Status
+
Subscription Entitlement
+
Business Rules
```

The frontend uses effective permissions provided by the backend.

It should not independently reconstruct complex authorization rules.

---

# 14. Permission-Based UI

Permission checks may control:

* menu visibility;
* buttons;
* actions;
* routes;
* forms;
* data sections;
* sensitive fields.

Example:

```text
if user.can("inventory.adjust"):
    show adjustment action
```

However, backend validation remains mandatory.

---

# 15. Subscription-Based UI

Subscription state may affect:

* feature visibility;
* modification controls;
* export availability;
* administrative functions.

For a read-only Business:

```text
View → Allowed
Modify → Blocked
Export → Allowed where permitted
```

The frontend should communicate the reason for blocked functionality.

It must not attempt to bypass subscription restrictions.

---

# 16. Navigation Architecture

Navigation should be permission-aware.

Conceptually:

```text
Dashboard
POS
Orders
Cash
Inventory
Products
Recipes
Menu
Attendance
Payroll
Reports
Notifications
Administration
```

Only relevant modules should be shown to the current user.

However, direct URL navigation must still be rejected by backend authorization.

---

# 17. Route Protection

Protected routes should validate:

* authentication;
* application initialization;
* Business context;
* Branch context where required;
* effective permission;
* subscription state where relevant.

Route guards are a UX layer, not the final security boundary.

---

# 18. Feature Modules

Each major business area should be implemented as a feature module.

Example:

```text
features/
├── dashboard/
├── pos/
├── orders/
├── cash/
├── inventory/
├── products/
├── recipes/
├── sets/
├── menu/
├── pricing/
├── attendance/
├── payroll/
├── reports/
├── notifications/
└── administration/
```

Feature modules should own their:

* pages;
* components;
* state;
* API queries;
* validation;
* feature-specific utilities.

---

# 19. Shared UI Layer

Reusable UI should be placed in a shared layer.

Examples:

* Button;
* Input;
* Select;
* Modal;
* Drawer;
* Table;
* Pagination;
* Date picker;
* Currency input;
* Confirmation dialog;
* Toast;
* Status badge;
* Loading state;
* Empty state;
* Error state.

Shared components must not contain business-specific behavior unless explicitly designed as a reusable domain component.

---

# 20. Design System

The application should use a consistent design system.

It should define:

* typography;
* spacing;
* colors;
* borders;
* radius;
* shadows;
* states;
* form controls;
* buttons;
* tables;
* dialogs;
* notifications;
* responsive behavior.

The POS interface may use a specialized layout while still following the same design system.

---

# 21. UI Complexity Principle

Complex backend behavior must not automatically create complex UI.

For example:

```text
Backend:
Configuration Version
Optimistic Concurrency
Audit
Outbox
Synchronization
```

The user may only see:

```text
Price updated
```

unless a conflict actually occurs.

---

# 22. POS Frontend Priority

POS is the most performance-sensitive frontend area.

Priority:

1. Order creation;
2. Product search;
3. Product selection;
4. Order modification;
5. Payment;
6. Cash session;
7. Kitchen workflow;
8. Secondary information.

POS must minimize:

* unnecessary network requests;
* large component trees;
* expensive re-renders;
* blocking operations;
* unnecessary animations.

---

# 23. POS Layout

The POS interface should be optimized for:

* desktop;
* touchscreen;
* keyboard;
* mouse.

Typical structure:

```text
┌────────────────────────────────────────────┐
│ Branch / Cashier / Session / Status       │
├───────────────────┬────────────────────────┤
│ Categories        │ Current Order           │
│                   │                        │
│ Products          │ Items                  │
│                   │                        │
│                   │ Total                  │
├───────────────────┴────────────────────────┤
│ Payment / Actions / Order Controls         │
└────────────────────────────────────────────┘
```

The exact visual design belongs to the Design System and POS UI documents.

---

# 24. Product Search

Product search must be optimized for POS usage.

The frontend may use:

* local indexed data;
* memory cache;
* server search;
* prefix search;
* barcode/search input where supported.

The backend remains authoritative for final availability and price.

---

# 25. POS Local Data

Data required for fast POS operation may be cached locally.

Examples:

* products;
* categories;
* menu;
* prices;
* recipes required for modification;
* permitted configuration;
* branch information.

Local cache must be:

* scoped;
* encrypted where required;
* versioned;
* invalidatable;
* tied to trusted device/offline authorization.

---

# 26. Local Cache Authority

The frontend must never treat local cache as permanent authority.

For online operation:

```text
Server
   ↓
Authoritative
```

Local cache:

```text
Optimization
```

For offline operation:

```text
Last Valid Authorized Configuration
```

is used within the allowed offline period.

---

# 27. Offline-First Architecture

Offline operation is a first-class frontend capability for trusted devices.

The frontend must support:

* offline detection;
* local data access;
* local operation creation;
* operation queue;
* synchronization;
* retry;
* conflict display;
* synchronization status;
* offline authorization expiration.

---

# 28. Offline Operation Identity

Offline-created operations must use client-generated UUIDs.

Example:

```text
Operation UUID
Entity UUID
Device UUID
```

The frontend must never generate IDs that conflict with server-generated identities.

UUID generation must be cryptographically appropriate for uniqueness requirements.

---

# 29. Offline Operation Queue

Conceptually:

```text
User Action
   ↓
Validate Locally
   ↓
Create Operation UUID
   ↓
Persist Local Operation
   ↓
Update UI
   ↓
Wait for Connection
   ↓
Synchronize
```

The operation must remain durable across application restart where offline support requires it.

---

# 30. Offline UI State

The interface should clearly communicate:

```text
Online
Offline
Syncing
Sync Error
Conflict
Offline Authorization Expiring
Offline Authorization Expired
```

The user should not need technical knowledge to understand the current state.

---

# 31. Synchronization Status

The application shell should provide a compact synchronization indicator.

Example:

```text
Online
3 pending
Syncing...
Synced
1 conflict
```

Detailed synchronization information should be available separately.

---

# 32. Offline Authorization

Offline operation is allowed only for trusted devices with valid offline authorization.

The frontend must not allow a user to bypass an expired offline authorization.

Server-side validation remains authoritative during synchronization.

---

# 33. Offline Data Security

Sensitive offline data must be protected.

Where required:

* encrypted local storage;
* device binding;
* secure key handling;
* expiration;
* revocation;
* data minimization.

Browser/device storage must not contain unnecessary sensitive information.

---

# 34. State Architecture

Frontend state should be separated into categories.

Recommended:

```text
Server State
UI State
Session State
Application Context
Offline State
Form State
Derived State
```

These categories should not be mixed unnecessarily.

---

# 35. Server State

Server state includes:

* Products;
* Orders;
* Inventory;
* Employees;
* Reports;
* Notifications;
* Menu;
* Pricing;
* Cash sessions.

Server state should use a dedicated data-fetching/cache strategy.

It should not be duplicated unnecessarily into global UI state.

---

# 36. UI State

UI state includes:

* modal open/closed;
* selected tab;
* selected row;
* sidebar state;
* filters;
* temporary view state.

UI state should remain local to the relevant component or feature when possible.

---

# 37. Session State

Session state includes:

* authenticated employee;
* session expiration;
* current authentication status;
* current Business;
* current Branch;
* device state.

Security-sensitive session information must not be exposed unnecessarily to UI components.

---

# 38. Form State

Forms should maintain temporary state locally.

Examples:

* Employee form;
* Product form;
* Recipe form;
* Price form;
* Expense form.

Form state must not automatically become global application state.

---

# 39. Derived State

Derived state should be calculated from authoritative source state where practical.

Avoid storing duplicate values that can become inconsistent.

Example:

```text
Order Items
+
Prices
=
Displayed Total
```

The final financial amount must still be determined by backend business rules.

---

# 40. API Layer

Frontend API access must use a centralized API/data layer.

Feature components should not directly implement:

* authentication headers;
* retry logic;
* raw fetch handling;
* error mapping;
* request IDs;
* API versioning.

The API layer should centralize these concerns.

---

# 41. API Client Responsibilities

The API client may handle:

* base URL;
* authentication;
* request headers;
* request ID;
* operation UUID;
* serialization;
* response parsing;
* standard error mapping;
* timeout;
* retry for safe requests where appropriate.

Business-specific retry decisions belong to feature/application logic.

---

# 42. Operation UUID

Retryable commands should carry an operation UUID.

For example:

```text
POST /orders/accept

X-Operation-Id:
<UUID>
```

The frontend must preserve the same operation UUID when retrying the same logical operation.

A new user action must generate a new operation UUID.

---

# 43. Request Identification

Requests should include a client-generated request identifier where the API contract supports it.

The frontend should allow tracing:

```text
User Action
→ Request ID
→ Operation ID
→ Backend Transaction
→ Audit / Event / Job
```

---

# 44. API Error Mapping

Backend errors should be mapped into user-understandable states.

Examples:

```text
401 → Session expired
403 → You do not have permission
404 → Item not found
409 → Data changed; refresh required
422 → Invalid input
429 → Too many requests
5xx → Temporary server problem
```

Technical details should remain available for diagnostics without overwhelming the user.

---

# 45. Conflict UI

Concurrency conflicts must be understandable.

Example:

```text
"Bu ma'lumot boshqa foydalanuvchi tomonidan o'zgartirildi."

[Yangilash]
```

The frontend should not silently overwrite newer server state.

---

# 46. Optimistic UI

Optimistic UI may be used only where failure can be safely represented and rolled back.

Suitable examples:

* local UI toggle;
* notification read state;
* low-risk presentation state.

It should be used carefully for:

* inventory;
* cash;
* payment;
* financial state;
* historical configuration.

Authoritative financial state should not rely on unsafe optimistic assumptions.

---

# 47. Loading States

Every asynchronous operation should have an appropriate loading state.

However, loading indicators should not unnecessarily block unrelated UI.

Prefer:

```text
Local loading
```

over:

```text
Entire application loading
```

when possible.

---

# 48. Empty States

Empty states should distinguish:

* no data exists;
* filters returned no results;
* user lacks access;
* data is still loading;
* offline data unavailable.

These states should not be visually confused.

---

# 49. Error States

Feature-level errors should provide:

* understandable message;
* retry action where useful;
* relevant context;
* non-destructive recovery.

Global fatal errors should be handled by the application error boundary.

---

# 50. Error Boundary

The application should provide error boundaries around major feature areas.

A failure in:

```text
Reports
```

must not necessarily crash:

```text
POS
```

Feature isolation is therefore important.

---

# 51. Session Expiration

When a session expires:

1. preserve safe local form state where appropriate;
2. stop unauthorized API requests;
3. notify the user;
4. redirect to authentication;
5. do not silently discard important unsaved work.

Offline state must be handled separately.

---

# 52. Authentication UX

Authentication should remain fast.

Normal POS use should not require repeated authentication for every action.

Stronger authentication may be required for sensitive operations.

Examples:

* permission changes;
* security configuration;
* device trust;
* high-risk financial corrections.

---

# 53. Device Context

The frontend may display the current trusted device state.

Example:

```text
Trusted Device
Offline authorization:
Valid
Expires:
...
```

Device identity must not be treated as proof of authorization.

---

# 54. Cash Session UI

Cash session state must be visible.

Example:

```text
Cash Session
Status: OPEN
Cashier: ...
Opened: ...
Expected Cash: ...
```

Actions must depend on effective permission and backend state.

---

# 55. Order State

The frontend should represent the backend Order state machine.

Possible states may include:

```text
DRAFT
PENDING
ACCEPTED
PREPARING
READY
COMPLETED
CANCELLED
PAID
REFUNDED
```

The exact state set is defined by System Analysis and Order Lifecycle documents.

The frontend must not invent incompatible states.

---

# 56. Order Item State

Where item-level workflow exists, the UI should support per-item status.

Example:

```text
Lavash ×2
Preparing

Hotdog ×1
Ready
```

The frontend must use server-authoritative state.

---

# 57. Inventory UI

Inventory interfaces must clearly distinguish:

* stock quantity;
* reserved/required quantity where applicable;
* low stock;
* out of stock;
* adjustment;
* discrepancy;
* unavailable equipment.

The frontend must not display negative stock as a valid state when backend rules prohibit it.

---

# 58. Product and Recipe UI

Product UI should distinguish:

```text
Product
Recipe
Recipe Version
Menu Availability
Price
Inventory
```

A Product with historical usage must not expose a destructive delete operation where backend rules require archive.

---

# 59. Menu and Pricing UI

Menu UI should distinguish:

```text
Global Product
Branch Availability
Global Standard Price
Branch Override
Effective Configuration
```

The frontend must communicate effective configuration without exposing unnecessary versioning complexity.

---

# 60. Price Change UX

Price changes should clearly indicate:

* current price;
* new price;
* affected Branch;
* effective time/session boundary;
* permission requirements.

Existing Orders must visually retain their historical prices.

---

# 61. Historical Data UX

Historical data must be clearly identifiable.

Examples:

```text
Current Price
Historical Order Price
Current Recipe
Historical Recipe Version
Current Configuration
Historical Configuration
```

The interface must not make historical values appear as current values.

---

# 62. Reports UI

Reports may contain:

* filters;
* date range;
* Branch;
* employee;
* category;
* report version;
* export action.

Heavy reports should load asynchronously where appropriate.

---

# 63. Report Version UI

If a report has multiple versions, the UI should allow authorized users to understand:

* report period;
* version;
* creation time;
* reason;
* current/latest version.

Historical versions must remain immutable.

---

# 64. Export UI

For large exports:

```text
Request Export
    ↓
Export Job Created
    ↓
Processing
    ↓
Ready
    ↓
Download
```

The UI should not hold an HTTP request open unnecessarily.

---

# 65. Notifications UI

Notifications should support:

* unread/read;
* severity;
* timestamp;
* related entity;
* navigation to relevant feature.

Notifications must not grant permissions or perform unauthorized operations.

---

# 66. Dashboard Architecture

Dashboard widgets should be modular.

Example:

```text
Dashboard
├── Sales
├── Orders
├── Cash
├── Inventory
├── Employees
├── Payroll
├── Alerts
└── Branch Performance
```

Users may customize widget visibility where permitted.

---

# 67. Dashboard Performance

Dashboard must not load every available report simultaneously.

Use:

* lazy loading;
* parallel requests where safe;
* cached reference data;
* asynchronous widgets;
* independent error states.

One failed widget should not destroy the dashboard.

---

# 68. Frontend Caching

Caching should follow the backend caching architecture.

Cacheable examples:

* menu;
* product reference data;
* categories;
* permissions;
* Business configuration;
* Branch configuration.

Final authority remains the backend.

---

# 69. Cache Invalidation

Frontend cache should be invalidated when:

* Branch changes;
* Business changes;
* permission changes;
* configuration version changes;
* server indicates stale data;
* synchronization changes relevant data.

Cache invalidation must not cause historical data mutation.

---

# 70. Data Freshness

Different data types may have different freshness requirements.

Example:

```text
POS price/configuration:
high freshness

Dashboard:
moderate freshness

Historical reports:
versioned snapshot

Static reference data:
longer cache
```

Freshness policy should be explicit.

---

# 71. Performance Architecture

Frontend performance priorities:

1. POS interaction;
2. product search;
3. order manipulation;
4. payment;
5. cash operations;
6. normal navigation;
7. dashboards;
8. reports;
9. exports.

Heavy features must not block high-priority workflows.

---

# 72. Rendering Performance

The frontend should minimize:

* unnecessary re-renders;
* large DOM trees;
* expensive computations;
* duplicate API requests;
* unnecessary global state updates.

Lists should use pagination or virtualization when data size requires it.

---

# 73. Code Splitting

Feature modules should support lazy loading.

For example:

```text
Initial Bundle
   ↓
Authentication
Application Shell
Core POS
   ↓
Lazy Modules
Inventory
Reports
Payroll
Administration
```

High-value POS functionality should not wait for unrelated administrative modules.

---

# 74. Bundle Performance

The frontend should monitor:

* initial JavaScript size;
* route chunk size;
* compressed size;
* startup time;
* interaction latency;
* memory usage.

Unused dependencies should not be added unnecessarily.

---

# 75. Offline Bundle

The functionality required for trusted offline POS should be available locally.

Offline support must not depend on downloading a new application bundle while offline.

Application version compatibility must be considered during offline synchronization.

---

# 76. Frontend Security

Security controls include:

* secure authentication handling;
* protected routes;
* backend authorization;
* safe token handling;
* XSS prevention;
* CSRF protection where applicable;
* secure storage;
* dependency security;
* Content Security Policy where applicable;
* input validation;
* safe file handling.

The frontend must never embed privileged server secrets.

---

# 77. Token Storage

Authentication tokens should use the safest storage mechanism supported by the chosen architecture.

Long-lived sensitive tokens should not be casually stored in:

```text
localStorage
```

without a justified security design.

The final authentication mechanism must align with Backend Security architecture.

---

# 78. XSS Protection

The frontend must avoid unsafe HTML rendering.

User-provided content should be escaped or sanitized.

Raw HTML rendering requires explicit justification and sanitization.

---

# 79. File Upload Security

Frontend upload validation may check:

* file type;
* file size;
* extension;
* basic content expectations.

Backend validation remains mandatory.

The frontend must not assume a file is safe merely because its extension is valid.

---

# 80. Accessibility

Frontend accessibility should target practical WCAG-aligned behavior.

Requirements include:

* keyboard navigation;
* visible focus;
* semantic controls;
* accessible labels;
* sufficient contrast;
* screen-reader-compatible status;
* error messages;
* accessible dialogs;
* touch-friendly controls.

POS-specific touch controls must remain usable without sacrificing keyboard accessibility where practical.

---

# 81. Responsive Design

The system should support:

* desktop;
* laptop;
* tablet where relevant.

The POS is optimized primarily for desktop/touchscreen operational hardware.

Administrative pages should reflow rather than becoming unusable at narrower widths.

---

# 82. Browser Support

Supported browsers must be explicitly defined during implementation.

The application should prioritize modern Chromium-based browsers for initial POS deployment if that matches operational hardware.

Browser support decisions must be documented rather than assumed.

---

# 83. Frontend Testing

Testing should include:

### Unit Tests

* utilities;
* validators;
* state logic;
* formatting;
* permission helpers.

### Component Tests

* forms;
* tables;
* dialogs;
* permission-based UI;
* loading/error states.

### Integration Tests

* API interaction;
* authentication;
* Branch switching;
* synchronization;
* offline behavior.

### End-to-End Tests

* login;
* POS;
* order;
* payment;
* cash;
* inventory;
* menu;
* reports.

---

# 84. Offline Testing

Offline testing must verify:

* network loss;
* operation persistence;
* application restart;
* duplicate synchronization;
* sync failure;
* conflict;
* authorization expiration;
* clock rollback;
* device revocation;
* stale configuration.

---

# 85. Frontend Observability

The frontend should expose operational metrics where appropriate.

Examples:

* application load time;
* route load time;
* API latency;
* API error rate;
* JavaScript errors;
* synchronization failures;
* offline queue size;
* offline duration;
* cache hit rate;
* POS interaction latency.

Sensitive user data must not be included unnecessarily.

---

# 86. Error Monitoring

Client errors should contain:

* application version;
* browser information;
* route;
* feature;
* request ID;
* operation ID where available.

Avoid collecting unnecessary personal or sensitive information.

---

# 87. Frontend Release Version

Every frontend build should have a release/version identifier.

Example:

```text
Frontend Version: 1.4.2
```

The version should be available for diagnostics.

Offline clients should report their application version during synchronization where required.

---

# 88. Frontend and Backend Compatibility

Frontend and Backend versions must have a defined compatibility strategy.

The frontend must not assume that every deployment updates both sides atomically.

API contract changes should use:

* backward compatibility;
* versioning;
* migration periods;
* feature flags where appropriate.

---

# 89. Feature Flags

Feature flags may control:

* UI rollout;
* experimental features;
* gradual deployment.

Feature flags are not equivalent to:

* permissions;
* subscription entitlements;
* authorization.

Backend authorization remains authoritative.

---

# 90. Frontend Configuration

Environment-specific configuration may include:

* API base URL;
* application environment;
* public feature configuration;
* frontend release ID.

Secrets must not be placed into frontend configuration because frontend configuration is ultimately accessible to the client.

---

# 91. Build Architecture

The build should support:

```text
Development
Testing
Staging
Production
```

Each environment should have explicit configuration.

Production builds should:

* disable development debugging;
* optimize assets;
* generate source maps according to security policy;
* expose release version;
* use production API endpoints.

---

# 92. Deployment

The frontend may initially be deployed as static assets.

Possible architecture:

```text
Internet
   ↓
Nginx
   ↓
Frontend Static Assets
   +
API Proxy
   ↓
Backend
```

The frontend should not require a permanently running Node.js server if the selected frontend framework allows static deployment.

---

# 93. Deployment Safety

Frontend deployment must account for:

* browser cache;
* service worker versioning where used;
* API compatibility;
* offline clients;
* asset availability;
* rollback.

A deployment must not invalidate active offline POS clients unexpectedly.

---

# 94. Service Worker

A service worker may be used for:

* offline assets;
* offline application shell;
* caching.

However, service worker caching must be carefully versioned.

A stale service worker must not serve incompatible application code indefinitely.

---

# 95. Offline Version Compatibility

If an offline device runs an older frontend version:

* synchronization must remain compatible where supported;
* incompatible operations must be rejected safely;
* user must receive an understandable upgrade message when required.

The system must not silently corrupt data because of version mismatch.

---

# 96. Frontend Recovery

The frontend should support recovery from:

* API outage;
* temporary network loss;
* stale cache;
* failed synchronization;
* expired session;
* application error;
* incompatible configuration.

Recovery should prioritize preserving user work.

---

# 97. Unsaved Work

The frontend should prevent accidental loss of important user input.

For example:

* product form;
* recipe form;
* employee form;
* expense form;
* report filters.

Where practical, temporary local state may be preserved during:

* session expiration;
* route changes;
* recoverable errors.

Sensitive information must not be persisted unnecessarily.

---

# 98. Frontend Logging

Client logging should use structured events.

Example:

```text
event
timestamp
level
release
route
feature
request_id
operation_id
error_code
```

Do not log:

* passwords;
* authentication tokens;
* secrets;
* unnecessary personal data.

---

# 99. Internationalization

The frontend should be designed so that user-facing text can be localized.

Even if the initial production language is limited, hard-coded strings should be avoided where practical.

Business data should remain separate from translated UI labels.

---

# 100. Date and Time

The frontend must distinguish:

* UTC timestamps;
* Business timezone;
* Branch timezone;
* user display timezone where applicable.

Date-only values must not accidentally shift because of timezone conversion.

Financial and report dates must use the correct Business/Branch timezone defined by backend rules.

---

# 101. Currency

Currency display must follow Business configuration.

The frontend should use precise formatting.

It must not use floating-point arithmetic for authoritative financial calculations.

Displayed totals may be calculated for presentation, but final financial values come from backend-authoritative state.

---

# 102. Numeric Input

Numeric inputs should validate:

* decimal precision;
* minimum;
* maximum;
* required state;
* locale formatting.

Examples:

* price;
* quantity;
* percentage;
* markup;
* salary.

Backend validation remains mandatory.

---

# 103. Frontend Architecture Guardrails

The following are prohibited:

* business-critical logic only in frontend;
* frontend-only authorization;
* direct database access;
* secrets embedded in frontend;
* uncontrolled global state;
* cache as financial authority;
* silent conflict overwrite;
* arbitrary local modification of historical data;
* bypassing subscription restrictions;
* bypassing offline authorization;
* storing unnecessary sensitive data;
* unbounded offline queue;
* unbounded API retries;
* unnecessary microfrontend complexity.

---

# 104. Recommended Project Structure

Initial frontend structure:

```text
frontend/
├── src/
│   ├── app/
│   │   ├── router/
│   │   ├── providers/
│   │   ├── shell/
│   │   ├── guards/
│   │   └── initialization/
│   │
│   ├── features/
│   │   ├── dashboard/
│   │   ├── pos/
│   │   ├── orders/
│   │   ├── cash/
│   │   ├── inventory/
│   │   ├── products/
│   │   ├── recipes/
│   │   ├── sets/
│   │   ├── menu/
│   │   ├── pricing/
│   │   ├── attendance/
│   │   ├── payroll/
│   │   ├── reports/
│   │   ├── notifications/
│   │   └── administration/
│   │
│   ├── entities/
│   │   ├── business/
│   │   ├── branch/
│   │   ├── employee/
│   │   ├── product/
│   │   ├── order/
│   │   ├── inventory/
│   │   ├── cash/
│   │   └── report/
│   │
│   ├── shared/
│   │   ├── ui/
│   │   ├── forms/
│   │   ├── hooks/
│   │   ├── utils/
│   │   ├── types/
│   │   ├── validation/
│   │   └── formatting/
│   │
│   ├── api/
│   │   ├── client/
│   │   ├── contracts/
│   │   ├── queries/
│   │   └── mutations/
│   │
│   ├── state/
│   │   ├── session/
│   │   ├── context/
│   │   ├── offline/
│   │   └── ui/
│   │
│   ├── synchronization/
│   │   ├── queue/
│   │   ├── sync/
│   │   ├── conflicts/
│   │   └── storage/
│   │
│   ├── configuration/
│   └── main.*
│
├── public/
├── tests/
└── package.json
```

The exact framework-specific naming may change.

---

# 105. Dependency Direction

Recommended dependency direction:

```text
Feature
   ↓
Application / State / API
   ↓
Entities / Shared
```

Shared modules must not depend on high-level business features.

For example:

```text
shared/ui
```

must not depend on:

```text
features/payroll
```

---

# 106. Feature Independence

A feature should be removable or modified without requiring unrelated features to be rewritten.

For example:

```text
Reports
```

should not directly manipulate:

```text
POS internal state
```

unless an explicit shared contract exists.

---

# 107. Shared Entity Layer

Entities represent reusable client-side representations of business objects.

Examples:

* Business;
* Branch;
* Employee;
* Product;
* Order;
* Inventory;
* Cash Session;
* Report.

Entities should not become a duplicate backend domain model containing authoritative business rules.

---

# 108. Frontend Application Services

Complex client-side workflows may use application services.

Examples:

* Branch switching;
* Offline synchronization orchestration;
* POS order composition;
* export tracking;
* authentication restoration.

These services coordinate frontend behavior but do not replace backend business logic.

---

# 109. POS State Isolation

POS state should be isolated from unrelated application state.

A dashboard update should not cause unnecessary POS re-rendering.

This is important for performance.

---

# 110. Offline State Isolation

Offline synchronization state should be isolated from ordinary UI state.

Example:

```text
UI:
Current page

Offline:
Pending operations

Sync:
Processing state

Server:
Authoritative state
```

These must not be merged into one uncontrolled global state object.

---

# 111. Application-Level Error Recovery

The application shell should distinguish:

```text
Recoverable Feature Error
Temporary API Error
Authentication Error
Authorization Error
Conflict
Offline State
Fatal Application Error
```

Each should have an appropriate recovery strategy.

---

# 112. API Retry Policy

The frontend must not retry every request automatically.

Retry is appropriate mainly for:

* safe idempotent requests;
* known temporary network failures;
* explicit retryable API responses.

Mutating operations must reuse the same operation UUID when retried.

---

# 113. Network State

The frontend should distinguish:

```text
Browser says offline
```

from:

```text
Server unavailable
```

Browser connectivity indicators are not sufficient proof of backend availability.

The application may use a lightweight health/request mechanism where necessary.

---

# 114. Frontend SLO Targets

Initial frontend targets:

| Metric                                     |                          Target |
| ------------------------------------------ | ------------------------------: |
| Application shell interactive              |                     p75 ≤ 2.5 s |
| Main authenticated route interactive       |                     p75 ≤ 2.0 s |
| POS initial screen interactive             |                     p75 ≤ 2.0 s |
| POS product search response                |                    p95 ≤ 150 ms |
| POS local interaction feedback             |                    p95 ≤ 100 ms |
| Normal API-driven list rendering           |     p95 ≤ 500 ms after response |
| Route transition for cached feature        |                    p95 ≤ 300 ms |
| Frontend fatal error rate                  |                 < 0.1% sessions |
| Synchronization UI update                  |        ≤ 2 s after state change |
| Offline operation persistence              |                    p95 ≤ 200 ms |
| Client-side duplicate operation prevention |                        ≥ 99.99% |
| Unauthorized UI action prevention          | 100% for known permission state |
| Cross-Business client data isolation       |                            100% |
| Critical frontend error detection          |                          ≤ 60 s |

These are initial targets and must be validated through real device/browser testing.

---

# 115. POS Performance Target

Under normal supported hardware:

* Product search should feel immediate.
* Local button interaction should not visibly block.
* Adding an item should update the UI within approximately 100 ms where local state permits.
* Network-dependent operations should provide immediate feedback.
* Long-running operations must not freeze the POS interface.
* Background synchronization must not block normal POS interaction.

---

# 116. Testing and Performance Budgets

Frontend CI should monitor:

* bundle size;
* initial JavaScript;
* route chunks;
* test execution;
* lint errors;
* type errors;
* accessibility checks.

A significant performance regression should be treated as a quality issue rather than accepted silently.

---

# 117. Architecture Decision: Modular Monolith Frontend

The initial frontend architecture is a modular application rather than microfrontends.

Reason:

* smaller deployment complexity;
* shared design system;
* simpler authentication;
* simpler offline storage;
* simpler POS state;
* easier consistency;
* lower operational overhead.

Microfrontends may be reconsidered only when justified by actual scale or organizational boundaries.

---

# 118. Architecture Decision: Backend Authority

The frontend intentionally does not duplicate authoritative business rules.

Reason:

* prevents divergence;
* improves security;
* simplifies maintenance;
* protects offline synchronization;
* preserves historical integrity;
* reduces inconsistent calculations.

Client-side validation remains important for user experience, but server-side validation remains authoritative.

---

# 119. Architecture Decision: Offline-First POS

Offline support is treated as a dedicated frontend subsystem rather than a temporary workaround.

Reason:

* offline operation is a product requirement;
* trusted devices require local persistence;
* synchronization requires durable operation state;
* POS must continue operating during temporary connectivity loss.

---

# 120. Architecture Decision: Feature-Oriented Structure

The frontend uses feature-oriented modules with shared infrastructure.

Reason:

* easier maintenance;
* clearer ownership;
* reduced coupling;
* easier testing;
* better AI-agent navigation;
* simpler future scaling.

---

# 121. System Invariants

The following invariants apply to Frontend Architecture:

1. Backend remains the final authorization authority.
2. Frontend permission checks are not security boundaries.
3. Business context is explicit.
4. Branch context is explicit.
5. Branch switching invalidates or refreshes Branch-scoped state.
6. Cross-Business data must never be intentionally displayed.
7. Cross-Branch unauthorized data must never be intentionally displayed.
8. Subscription restrictions cannot be bypassed through UI.
9. Offline authorization cannot be bypassed through UI.
10. Historical financial values are not rewritten by frontend state.
11. Historical configuration is not silently replaced by current configuration.
12. Local cache is not authoritative for business state.
13. POS core state is isolated from unrelated global state.
14. Sensitive authentication data is minimized in client storage.
15. Secrets are never embedded in frontend builds.
16. Mutating retries preserve operation identity.
17. Duplicate user actions must not create uncontrolled duplicate requests.
18. Backend validation remains mandatory for all protected operations.
19. UI hides unauthorized actions where effective permission is known.
20. Direct route access does not bypass backend authorization.
21. Offline operations have durable local identity.
22. Offline operations remain traceable to the device.
23. Offline operations remain traceable to the Business.
24. Offline operations remain traceable to the Branch where applicable.
25. Offline operation queue is bounded.
26. Synchronization failures remain visible.
27. Synchronization conflicts remain visible.
28. The frontend does not silently overwrite server state after conflict.
29. Local optimistic state can be rolled back when required.
30. Financial operations do not depend on unsafe optimistic assumptions.
31. POS interaction must remain responsive during background work.
32. Background synchronization must not freeze the UI.
33. Large reports must not block POS.
34. Large exports must not block POS.
35. Dashboard failures must not crash POS.
36. Feature errors must be isolated where practical.
37. API errors are mapped into understandable states.
38. Session expiration is handled explicitly.
39. Authentication restoration is performed before protected application use.
40. Business and Branch context are refreshed when changed.
41. Permission changes invalidate relevant client state.
42. Configuration changes invalidate relevant cache.
43. Cached data has defined freshness behavior.
44. Cache invalidation does not modify historical data.
45. Client-generated UUIDs are unique enough for operation identity.
46. Operation UUIDs remain stable across retries of the same logical command.
47. New logical commands receive new operation UUIDs.
48. Browser connectivity status is not treated as proof of server availability.
49. API retries are bounded.
50. Mutating requests are not blindly retried without idempotency.
51. User input is preserved when safe during recoverable errors.
52. Sensitive form data is not unnecessarily persisted.
53. Client-side validation improves UX but does not replace backend validation.
54. Financial calculations shown to users do not redefine backend-authoritative amounts.
55. Currency formatting follows Business configuration.
56. Date/time display follows authoritative timezone rules.
57. Historical report versions remain identifiable.
58. Export jobs remain distinguishable from generated files.
59. Notification state remains distinct from queue execution state.
60. Print failure does not alter committed Order state.
61. Offline data is protected according to device security requirements.
62. Trusted-device state is not equivalent to authorization.
63. Application version is identifiable.
64. API compatibility is considered during frontend deployment.
65. Offline clients must be considered during deployment compatibility.
66. Service worker caching cannot silently serve incompatible application code indefinitely.
67. Feature flags do not replace permissions.
68. Feature flags do not replace subscription entitlements.
69. Shared components do not depend on feature-specific modules unnecessarily.
70. Shared modules remain generic and reusable.
71. Feature modules own feature-specific behavior.
72. Feature modules should minimize cross-feature coupling.
73. Frontend state categories remain separated.
74. Server state is not unnecessarily duplicated into global UI state.
75. UI state remains local where practical.
76. Form state remains temporary where practical.
77. Derived state is not duplicated unnecessarily.
78. Error boundaries isolate recoverable feature failures.
79. Global application failure remains observable.
80. Frontend errors contain sufficient diagnostic context without unnecessary sensitive data.
81. Client logs do not contain secrets.
82. Client logs do not contain authentication tokens.
83. Frontend performance is measured.
84. POS performance receives highest frontend priority.
85. Background processing must not consume all client resources.
86. Large lists use bounded rendering.
87. Large datasets use pagination or virtualization where required.
88. Feature modules may be lazy-loaded.
89. Unrelated features should not unnecessarily increase initial bundle size.
90. Offline POS assets must be locally available when required.
91. Queue and synchronization state must survive application restart where required.
92. Synchronization must remain compatible with backend idempotency.
93. Client synchronization must not bypass backend conflict resolution.
94. Client synchronization must not bypass lifecycle validation.
95. Client synchronization must not bypass subscription validation.
96. Client synchronization must not bypass device validation.
97. Client synchronization must not bypass Business/Branch scope validation.
98. Frontend deployment must preserve API compatibility.
99. Frontend rollback must be possible.
100. Frontend architecture must remain simple enough for the initial product scale.

---

# 122. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/05_Users_Roles_and_Permissions.md`
* `docs/01_Business_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/11_Inventory_and_Warehouse.md`
* `docs/01_Business_Analysis/12_Products_and_Recipes.md`
* `docs/01_Business_Analysis/13_Menu_and_Pricing.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/05_Employees_Roles_and_Permissions.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/08_Order_Lifecycle_and_Statuses.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/17_Products_Recipes_and_Sets.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Backend

* `docs/04_Architecture/06_Backend/01_Backend_Architecture.md`
* `docs/04_Architecture/06_Backend/06_Authentication_and_Authorization.md`
* `docs/04_Architecture/06_Backend/07_Transaction_Management.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/06_Backend/19_Backend_Deployment_and_Runtime_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/23_Backend_Audit_and_History_Architecture.md`
* `docs/04_Architecture/06_Backend/24_Backend_Search_and_Filtering_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/29_Database_Security.md`

### Architecture

* `docs/04_Architecture/README.md`

---

# 123. Status

**Frontend Architecture Document:** Completed

**Document:** `01_Frontend_Architecture.md`

**Document Status:** Proposed

**Frontend Architecture Scope:** Initial architecture defined

**Next Document:** `02_Frontend_Project_Structure.md`
    
