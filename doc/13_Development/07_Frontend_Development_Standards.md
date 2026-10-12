# 07. Frontend Development Standards

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the coding and engineering standards for the FastFood ERP frontend.

The frontend is responsible for presenting approved business capabilities to users, collecting valid input, communicating with backend services, displaying system state, and providing a predictable user experience.

The frontend must remain:

* maintainable;
* consistent;
* responsive;
* accessible;
* secure by design;
* efficient;
* testable;
* compatible with backend contracts;
* suitable for branch and offline workflows.

The frontend is not the authoritative source for security or business rules.

---

# 2. Scope

These standards apply to:

* pages;
* layouts;
* components;
* forms;
* tables;
* dashboards;
* POS interfaces;
* inventory screens;
* recipe screens;
* menu management;
* employee management;
* permissions;
* payroll;
* reports;
* subscription interfaces;
* notifications;
* offline functionality;
* synchronization UI;
* API integration;
* client-side state;
* routing;
* frontend validation;
* error handling;
* accessibility;
* frontend testing;
* performance;
* configuration.

---

# 3. Core Principles

The frontend follows these principles:

1. The backend is the authority for business rules.
2. The frontend must reflect approved product behavior.
3. Components should have clear responsibilities.
4. Business logic should not be unnecessarily embedded in UI components.
5. API contracts must be treated as explicit boundaries.
6. Client-side validation improves usability but does not replace server validation.
7. Permissions must control the user interface without becoming the security boundary.
8. Loading, error, empty, and success states must be intentionally designed.
9. Offline behavior must be explicit to the user.
10. Shared state should be introduced only when needed.
11. Local state should remain local when possible.
12. UI consistency is part of maintainability.
13. Accessibility should be considered during implementation, not after completion.
14. Performance should be measured before complex optimization.
15. Tests should protect important user behavior.
16. Sensitive information must not be unnecessarily stored or exposed in the browser.
17. Frontend code must remain compatible with the approved backend contracts.
18. Components should be reusable when their behavior is genuinely shared.
19. Abstraction should not be introduced merely for abstraction's sake.
20. The interface must make important business states understandable to users.

---

# 4. Conceptual Frontend Architecture

The frontend should follow clear responsibility boundaries.

A conceptual structure is:

```text id="1y7y3r"
frontend/
├── app/
├── pages/
├── features/
├── components/
├── layouts/
├── services/
├── state/
├── hooks/
├── forms/
├── types/
├── utils/
├── assets/
└── tests/
```

The exact physical structure may evolve.

The important requirement is that responsibilities remain understandable.

---

# 5. Application Layer

The application layer manages frontend-wide concerns such as:

* application initialization;
* routing;
* authentication state;
* global providers;
* theme;
* global configuration;
* top-level error boundaries;
* global notifications.

It should not become a dumping ground for feature-specific logic.

---

# 6. Pages

Pages represent navigable application areas.

Examples include:

```text id="1g4v2c"
Dashboard
Orders
Cash Register
Inventory
Recipes
Menu
Employees
Payroll
Reports
Subscription
Settings
```

A page should coordinate its feature components rather than contain every implementation detail directly.

---

# 7. Features

Feature modules should contain behavior that belongs to a specific business capability.

Examples:

```text id="q5b2p3"
orders/
inventory/
recipes/
cash/
employees/
payroll/
reports/
subscriptions/
```

A feature may contain:

* components;
* API functions;
* hooks;
* local state;
* validation;
* types;
* tests.

This keeps business-oriented frontend behavior close to the feature that owns it.

---

# 8. Components

Components should have clear responsibilities.

Examples:

```text id="m4k6y9"
OrderTable
OrderStatusBadge
InventoryQuantityInput
RecipeIngredientList
CashRegisterSummary
BranchSelector
PermissionMatrix
```

Avoid components that independently manage:

* unrelated business features;
* global application state;
* many unrelated API calls;
* multiple unrelated workflows.

Large components should be decomposed when the separation improves understanding and testing.

---

# 9. Component Responsibility

A component should answer a clear question:

> What part of the interface does this component own?

Good:

```text id="p4y8w2"
OrderStatusBadge
```

Its responsibility is displaying order status.

Less desirable:

```text id="j7n1m5"
OrderManagementEverything
```

containing:

* order loading;
* inventory deduction;
* payment;
* employee permissions;
* reporting;
* navigation;
* notifications.

---

# 10. Reusable Components

Reusable components should be created when behavior or presentation is genuinely shared.

Good candidates include:

* buttons;
* dialogs;
* tables;
* form controls;
* status badges;
* date selectors;
* pagination;
* notification elements.

Do not create a generic abstraction merely because two components look similar.

Similar appearance does not always mean identical responsibility.

---

# 11. Design System Consistency

The frontend should use consistent patterns for:

* spacing;
* typography;
* buttons;
* inputs;
* dialogs;
* tables;
* status indicators;
* notifications;
* validation messages;
* loading states;
* empty states.

If a shared design system exists, new components should use it rather than creating competing patterns.

---

# 12. Naming Standards

Names should communicate UI or business meaning.

Prefer:

```text id="7c4z9x"
OrderList
CreateOrderDialog
InventoryAdjustmentForm
RecipeApprovalButton
BranchPermissionTable
```

Avoid:

```text id="j2q6r0"
Thing
Box
DataComponent
Helper
Manager
Stuff
```

Feature-specific names are preferred when they make responsibility clearer.

---

# 13. File Naming

Frontend file naming should remain consistent throughout the project.

The exact convention depends on the chosen frontend technology, but it must be documented and applied consistently.

Examples:

```text id="b7p4v2"
OrderList.tsx
orderApi.ts
useOrder.ts
orderTypes.ts
```

or the equivalent convention adopted by the project.

Do not mix multiple naming conventions without a justified reason.

---

# 14. Routing

Routes should represent application capabilities and remain understandable.

Routes should not expose sensitive internal implementation details unnecessarily.

Routing should account for:

* authentication;
* authorization;
* branch scope;
* subscription restrictions;
* not-found behavior;
* loading state;
* error state.

Frontend route guards improve UX but do not replace backend authorization.

---

# 15. Authentication State

The frontend should maintain authentication state consistently.

It should distinguish between:

```text id="2z3w6k"
Unauthenticated
Authenticated
Authentication Loading
Authentication Error
Session Expired
```

The UI should respond appropriately to each state.

---

# 16. Authorization-Aware UI

The frontend should use permission information to improve the interface.

For example:

```text id="q0v8a1"
No permission
    ↓
Hide or disable restricted action
```

However:

```text id="z4k7r2"
UI restriction ≠ security boundary
```

The backend must still enforce authorization.

---

# 17. Permission Visibility

Permission-aware UI should avoid creating confusing interfaces.

When a user cannot perform an operation, the UI may:

* hide the action;
* disable the action;
* show a restricted state;
* explain why access is unavailable.

The selected behavior should follow the approved UX rules for the feature.

Do not expose unnecessary implementation details about authorization.

---

# 18. Branch Context

When the user operates within a branch context, the active branch should be visually clear.

The frontend should prevent accidental confusion between:

```text id="0v5c8m"
Current Branch
All Branches
```

Where all-branch access exists, the UI must clearly distinguish it from a single branch.

Branch selection must not be treated as proof of authorization.

---

# 19. Tenant Context

The frontend should always operate within the authenticated tenant context.

Client state must not allow users to casually switch to another tenant identifier and gain access.

Tenant authorization remains a backend responsibility.

---

# 20. API Integration

API communication should be centralized through appropriate service or client abstractions.

Avoid scattering raw HTTP calls throughout UI components.

Prefer:

```text id="5t5c0n"
Component
    ↓
Feature Hook / Service
    ↓
API Client
    ↓
Backend
```

rather than:

```text id="2f3b8x"
Component
    ↓
raw HTTP request
    ↓
business processing
```

---

# 21. API Contracts

Frontend code must follow the approved API contract.

Do not assume fields exist because they "probably" exist.

API types should be derived from or kept synchronized with the approved contract where tooling permits.

Contract changes must follow the API development workflow.

---

# 22. API Error Handling

The frontend should translate backend errors into appropriate user-facing behavior.

It should distinguish between:

* validation errors;
* authorization failures;
* authentication expiration;
* not found;
* business conflicts;
* server failures;
* network failures;
* offline state.

Avoid showing raw server exceptions to users.

---

# 23. Error Messages

User-facing errors should be:

* understandable;
* actionable where possible;
* concise;
* consistent.

Avoid:

```text id="w0b7m4"
500 Internal Server Error
```

as the only user-facing explanation.

Avoid exposing:

* stack traces;
* database errors;
* internal paths;
* SQL;
* secret values;
* infrastructure details.

---

# 24. Loading States

Every asynchronous UI operation should have an intentional loading state when the user could otherwise be uncertain about what is happening.

Examples:

* page loading;
* table loading;
* button submission;
* modal loading;
* report generation;
* synchronization;
* file upload.

Avoid freezing the entire application when only one component is loading.

---

# 25. Empty States

Empty data is not automatically an error.

Examples:

```text id="k1m8t2"
No orders today
No recipes created
No employees assigned to this branch
No inventory movements found
```

Empty states should distinguish between:

* genuinely empty data;
* data still loading;
* filtered-out data;
* unavailable data due to permissions;
* failed data retrieval.

---

# 26. Success States

Important operations should provide appropriate confirmation.

Examples:

* order created;
* payment completed;
* recipe approved;
* inventory adjusted;
* register closed;
* employee added.

Success feedback should be proportional to the importance of the operation.

Avoid excessive notifications for routine actions.

---

# 27. Forms

Forms should:

* use clear labels;
* validate appropriate fields;
* preserve user input when possible;
* show actionable errors;
* prevent accidental duplicate submission;
* indicate required fields;
* handle loading state;
* respect permissions.

Forms must not rely only on client validation.

---

# 28. Client-Side Validation

Client-side validation should improve usability.

Examples:

```text id="a8w6c2"
Required field
Invalid email format
Invalid numeric format
Quantity must be positive
Date is outside allowed range
```

However, server-side validation remains authoritative.

The frontend must correctly handle server-side validation failures even when local validation passes.

---

# 29. Financial Input

Financial forms require additional care.

Examples include:

* price;
* discount;
* payment;
* refund;
* salary;
* cash count.

The UI should:

* use appropriate numeric input;
* avoid ambiguous decimal formatting;
* display currency clearly;
* prevent accidental repeated submission;
* show confirmation where required.

The frontend must not be the authoritative source for monetary calculations.

---

# 30. Inventory Input

Inventory quantity inputs should clearly distinguish:

* quantity;
* unit;
* available stock;
* requested quantity;
* adjustment quantity.

The interface should make it difficult to confuse:

```text id="z9u4c3"
kg
g
liter
ml
piece
```

where unit differences affect business correctness.

---

# 31. Recipe UI

Recipe interfaces should clearly communicate:

* product;
* recipe version;
* ingredients;
* quantities;
* semi-finished dependencies;
* approval state;
* active/inactive state;
* branch applicability.

Changing a recipe should not make users believe that historical orders automatically use the new recipe.

---

# 32. Order and POS UI

POS interfaces should prioritize:

* speed;
* clarity;
* minimal unnecessary navigation;
* visible order state;
* clear payment state;
* clear branch/register context.

Critical operations should provide appropriate confirmation without creating unnecessary friction.

---

# 33. Duplicate Submission Prevention

Actions such as:

* payment;
* order creation;
* refund;
* cash closing;
* recipe approval;

should prevent accidental repeated submission at the UI level.

For example:

```text id="z2x8q0"
User clicks
    ↓
Action enters processing state
    ↓
Button becomes non-repeatable
    ↓
Backend processes operation
    ↓
UI receives result
```

This is a usability mechanism.

The backend must still enforce idempotency where required.

---

# 34. Dialogs and Confirmation

Confirmation dialogs should be used for actions with meaningful consequences.

Examples:

* refund;
* deleting or archiving important data;
* closing a register;
* approving a recipe;
* changing permissions;
* disabling a product.

Do not add confirmation dialogs to every action.

Excessive confirmation creates user fatigue.

---

# 35. Destructive Actions

Destructive or irreversible actions should be visually and behaviorally distinct.

Where the business model requires archiving rather than deletion, the UI should prefer:

```text id="u5c9q1"
Archive
```

over:

```text id="q8y7r2"
Delete permanently
```

unless permanent deletion is explicitly allowed.

---

# 36. Tables

Tables should provide:

* clear column names;
* appropriate formatting;
* loading state;
* empty state;
* error state;
* pagination where required;
* sorting where useful;
* filtering where useful;
* row-level actions consistent with permissions.

Do not load unlimited records merely because the backend endpoint allows it.

---

# 37. Reports

Reports should distinguish:

* loading;
* no data;
* filtered data;
* unavailable data;
* failed generation.

Large reports should avoid unnecessarily blocking the entire interface.

If generation is asynchronous, the UI should communicate progress or state appropriately.

---

# 38. Dashboard Standards

Dashboards should prioritize actionable information.

Examples include:

* low stock;
* subscription status;
* salary due;
* large refunds;
* inventory variance;
* branch loss;
* operational warnings.

Do not overload dashboards with every available metric.

The dashboard should help the user understand what requires attention.

---

# 39. Notifications

Notifications should be:

* meaningful;
* concise;
* non-duplicative;
* appropriately prioritized.

Critical notifications should remain distinguishable from informational messages.

Avoid repeatedly showing the same notification for the same unchanged condition.

---

# 40. Date and Time Display

The frontend should display dates and times consistently.

Reports must clearly communicate the relevant date range and branch context.

Avoid ambiguous formats where:

```text id="2v6q7p"
03/04/2026
```

could be interpreted differently.

Use the project's standardized date and time formatting.

---

# 41. Time Zones

The frontend should respect the application's approved timezone model.

A timestamp from the backend must not be arbitrarily reinterpreted using the browser's timezone if the business operation is branch-local.

Branch-local business dates should remain clear.

---

# 42. Offline UX

Offline operation must be visible to the user.

The interface should distinguish:

```text id="h2f9r1"
Online
Offline
Synchronizing
Synchronization Failed
Synchronization Complete
```

The user should understand whether an operation:

* was accepted locally;
* is waiting for synchronization;
* has reached the server;
* failed and requires attention.

---

# 43. Offline Data

Offline-capable screens should use only data explicitly designed for local availability.

Do not assume that every server-side dataset is safely available offline.

Sensitive data should receive additional protection.

---

# 44. Synchronization UX

Synchronization status should be understandable without exposing implementation details.

Useful information may include:

* pending operations;
* synchronization progress;
* successful synchronization;
* conflict requiring attention;
* retry state.

The UI must not claim that a transaction is server-confirmed when it is only locally stored.

---

# 45. Offline Permissions

The frontend should respect the permissions available to the current offline session.

However, offline authorization must also follow the approved security architecture.

A user should not gain new privileges simply because the device is offline.

---

# 46. State Management

State should be categorized intentionally.

Typical categories include:

```text id="g8c4w6"
Local UI State
Form State
Server State
Session State
Global Application State
Offline State
```

Do not place all state into one global store.

---

# 47. Local State

Use local component state when the data is relevant only to that component or interaction.

Examples:

* dialog open/closed;
* selected tab;
* temporary input;
* expanded row.

Do not promote local state to global state without a real need.

---

# 48. Server State

Server-owned data should be treated as server state.

Examples:

* orders;
* employees;
* inventory;
* reports;
* recipes;
* subscriptions.

The frontend should avoid creating multiple independent sources of truth for the same server data.

---

# 49. Global State

Global state should be reserved for genuinely cross-application concerns.

Examples:

* authenticated session;
* active tenant context;
* global UI settings;
* application-level notifications.

Do not place every API response into global state.

---

# 50. State Synchronization

When server data changes, dependent UI state should be updated predictably.

Avoid stale copies of important business data.

For example:

```text id="y0v9t2"
Server Order
    ↓
Order List
Order Details
Dashboard
```

should have a defined refresh or cache-invalidation strategy.

---

# 51. Derived State

Do not store data that can reliably be calculated from existing state unless there is a justified performance reason.

Prefer:

```text id="f5v8p4"
total = quantity × price
```

to storing a second independent value when the backend remains the authoritative source for the actual business calculation.

Frontend-derived values are presentation helpers, not financial authority.

---

# 52. Client-Side Business Logic

Some UI behavior may legitimately use business concepts.

For example:

* showing available filters;
* calculating preview totals;
* displaying status labels.

However, the frontend must not become the only implementation of critical business rules.

Important rules must remain enforceable by the backend.

---

# 53. API Mutation Flow

A typical mutation should follow:

```text id="2o6k9v"
User Action
    ↓
Local Validation
    ↓
Permission-Aware UI
    ↓
API Request
    ↓
Loading State
    ↓
Backend Result
    ↓
Success / Error State
    ↓
State Refresh or Update
```

This flow should remain predictable.

---

# 54. Request Cancellation

Long-running or obsolete requests should be cancellable where appropriate.

Examples:

* search;
* report filters;
* autocomplete;
* route changes.

Do not allow stale responses to overwrite newer state.

---

# 55. Search and Filtering

Search interfaces should:

* debounce where appropriate;
* indicate loading;
* handle no results;
* preserve filters when useful;
* avoid excessive requests.

Search should not trigger a backend request on every keystroke unless that behavior is intentional and controlled.

---

# 56. Frontend Performance

Performance should be considered without premature complexity.

Important areas include:

* initial load;
* bundle size;
* rendering;
* large tables;
* dashboards;
* images;
* network requests;
* state updates.

Optimize based on measurement.

---

# 57. Large Lists

Large collections should use appropriate techniques such as:

* pagination;
* incremental loading;
* virtualization where justified;
* server-side filtering.

Do not render thousands of complex rows unnecessarily.

---

# 58. Network Efficiency

Avoid unnecessary API requests.

Examples of avoidable behavior:

```text id="0xj9k5"
Page load
→ request
→ request
→ request
→ duplicate request
→ duplicate request
```

Use appropriate caching or request coordination where useful.

Do not sacrifice correctness for fewer requests.

---

# 59. Images and Assets

Images should be:

* appropriately sized;
* optimized;
* lazy-loaded where useful;
* given meaningful alternative text where applicable.

Do not load large original assets when a smaller version is sufficient.

---

# 60. Accessibility

Frontend components should consider accessibility from the beginning.

Important areas include:

* keyboard navigation;
* focus management;
* labels;
* semantic elements;
* readable contrast;
* accessible form errors;
* dialog behavior;
* screen-reader semantics where applicable.

Accessibility should not be treated as purely cosmetic.

---

# 61. Keyboard-Heavy POS Usage

POS interfaces may require efficient keyboard and interaction patterns.

Where appropriate:

* keyboard navigation;
* predictable focus;
* shortcuts;
* rapid item selection;

may improve operational speed.

Shortcuts must not conflict with accessibility or create accidental financial actions.

---

# 62. Responsive Behavior

The frontend should support the devices and screen sizes defined by the product requirements.

Responsive design should preserve:

* important actions;
* readable data;
* usable forms;
* operational visibility.

Do not simply shrink complex desktop interfaces until they become unusable.

---

# 63. Browser Storage

Browser storage should be used carefully.

Do not store sensitive data in local storage merely for convenience.

Before storing data client-side, determine:

* sensitivity;
* lifetime;
* encryption requirements;
* logout behavior;
* multi-user device risk;
* offline requirements.

---

# 64. Tokens and Session Data

Authentication tokens and session information must follow the approved security architecture.

Frontend developers must not independently invent token storage mechanisms.

Never expose tokens through:

* logs;
* analytics;
* URLs;
* error messages;
* debug panels.

---

# 65. Environment Configuration

Frontend environment configuration should not contain secrets that must remain confidential.

Anything shipped to the browser should be assumed visible to the user.

Public configuration and private server secrets must remain separate.

---

# 66. Feature Flags

Feature flags should:

* have clear ownership;
* have defined behavior when disabled;
* avoid leaving inaccessible dead code indefinitely;
* not be treated as security controls.

A frontend feature flag may hide UI.

It must not be used as the only mechanism for restricting backend functionality.

---

# 67. Subscription-Based Features

When a feature is unavailable because of subscription restrictions, the UI should clearly communicate the state where appropriate.

For example:

```text id="f6p4j0"
Feature unavailable
Subscription requires an enabled plan
```

However, the backend must independently enforce the restriction.

---

# 68. Error Boundaries

Unexpected frontend failures should be contained where the framework supports error boundaries.

A single broken component should not unnecessarily destroy the entire application.

The UI should provide a safe recovery path where possible.

---

# 69. Security and Rendering

Do not render untrusted content as executable markup.

User-provided values such as:

* names;
* comments;
* delivery addresses;
* notes;

must be safely escaped according to the frontend framework.

Avoid unnecessary raw HTML rendering.

---

# 70. Forms and Unsaved Changes

For important forms, the UI should consider unsaved changes.

Where appropriate, warn the user before:

* leaving the page;
* closing a dialog;
* switching context.

Do not interrupt trivial forms with excessive warnings.

---

# 71. Confirmation of Important Operations

The frontend should make important transitions visible.

Examples:

```text id="q7f1y2"
Register Closed
Refund Submitted
Recipe Approved
Inventory Adjusted
Employee Permission Updated
```

Users should not need to infer success merely because a button stopped loading.

---

# 72. Testing Strategy

Frontend testing should protect user-visible behavior.

Important test levels include:

```text id="0v8k3j"
Unit
Component
Feature
Integration
End-to-End
```

The exact distribution should follow the broader testing architecture.

---

# 73. Component Tests

Component tests should verify:

* rendering;
* user interaction;
* validation;
* state changes;
* loading;
* error;
* empty;
* permission-aware behavior.

Avoid tests that only verify implementation details.

Prefer testing observable behavior.

---

# 74. Integration Tests

Integration tests should verify interactions between:

* components;
* state management;
* API clients;
* routing;
* forms;
* feature modules.

Examples:

```text id="2u7v5q"
Create Order
    ↓
API request
    ↓
Success
    ↓
Order list updated
```

---

# 75. End-to-End Tests

Critical workflows should have end-to-end coverage where appropriate.

Examples:

* login;
* create order;
* payment;
* register close;
* inventory adjustment;
* recipe approval;
* employee permission update;
* offline synchronization.

Not every UI detail requires end-to-end testing.

---

# 76. Test Selectors

Test selectors should be stable and intentional.

Avoid relying heavily on:

* CSS class names;
* generated DOM structure;
* visual layout;
* fragile element positions.

Prefer semantic roles, accessible labels, or dedicated test identifiers where appropriate.

---

# 77. Mocking

Mocks should represent meaningful boundaries.

Good candidates include:

* external APIs;
* payment providers;
* AI services;
* notification providers;
* unavailable infrastructure.

Avoid mocking the component's own behavior so heavily that tests no longer verify real user behavior.

---

# 78. Frontend Error Recovery

The UI should provide appropriate recovery mechanisms.

Examples:

```text id="r8m4q1"
Retry
Refresh
Reconnect
Return to previous page
Restore draft
```

The appropriate action depends on the failure.

Do not automatically retry sensitive operations such as payments without an idempotency-safe strategy.

---

# 79. Accessibility and Testing

Important accessibility behavior should be tested where practical.

Examples:

* keyboard access;
* form labels;
* focus movement;
* dialog closure;
* error announcements;
* disabled states.

---

# 80. Internationalization Readiness

If localization is planned, user-facing strings should not be scattered in ways that make future translation difficult.

Business terminology should remain consistent across the application.

Do not use different labels for the same concept without a reason.

---

# 81. Frontend Documentation

Frontend behavior that is architecturally or operationally significant should be documented.

Examples:

* offline behavior;
* state architecture;
* shared component rules;
* routing conventions;
* permission-aware UI;
* feature flag behavior;
* synchronization UX.

Documentation should explain decisions, not repeat obvious code.

---

# 82. Code Review Standards

Frontend PRs should be reviewed for:

* component responsibility;
* state ownership;
* API usage;
* permission handling;
* loading/error states;
* accessibility;
* performance;
* test coverage;
* responsive behavior;
* consistency with design patterns.

Reviewers should prioritize correctness and maintainability over personal stylistic preference.

---

# 83. Frontend Change Checklist

Before considering a frontend change complete:

### Architecture

* [ ] Responsibility is in the correct feature/component.
* [ ] State ownership is appropriate.
* [ ] API communication uses approved abstractions.
* [ ] No unnecessary global state was introduced.

### UI

* [ ] Loading state exists where required.
* [ ] Error state exists where required.
* [ ] Empty state exists where required.
* [ ] Success feedback is appropriate.
* [ ] Important actions are clear.
* [ ] Destructive actions are appropriately protected.

### Permissions

* [ ] Restricted UI is handled appropriately.
* [ ] Branch context is clear.
* [ ] Tenant context is preserved.
* [ ] Backend authorization remains authoritative.

### Forms

* [ ] Client validation is implemented where useful.
* [ ] Server validation errors are handled.
* [ ] Duplicate submission is prevented.
* [ ] Important unsaved changes are considered.

### API

* [ ] Approved API contract is followed.
* [ ] Errors are mapped safely.
* [ ] Stale responses cannot overwrite current state.
* [ ] Request cancellation is considered where relevant.

### Offline

* [ ] Offline state is visible where applicable.
* [ ] Synchronization state is understandable.
* [ ] Local-only state is not presented as server-confirmed.
* [ ] Retry behavior is safe.

### Performance

* [ ] Unnecessary requests are avoided.
* [ ] Large lists are bounded or paginated.
* [ ] Images/assets are appropriately handled.
* [ ] Performance-impacting changes are justified.

### Accessibility

* [ ] Keyboard navigation is considered.
* [ ] Inputs have clear labels.
* [ ] Focus behavior is appropriate.
* [ ] Error states are understandable.

### Testing

* [ ] Component tests are updated where appropriate.
* [ ] Feature/integration tests cover important behavior.
* [ ] Critical workflows have appropriate end-to-end coverage.

---

# 84. Frontend Anti-Patterns

## 84.1 Frontend-Only Security

```text id="x5f1p8"
Hide button
=
Secure operation
```

This is incorrect.

---

## 84.2 Fat Components

A single component containing:

* API calls;
* complex state;
* business rules;
* form management;
* navigation;
* reporting;
* unrelated UI;

should be treated as a design warning.

---

## 84.3 Global Store for Everything

Putting every API response and temporary UI value into global state increases complexity and makes state ownership unclear.

---

## 84.4 Raw API Calls Everywhere

Scattering direct HTTP requests across components makes:

* error handling;
* testing;
* contract changes;
* authentication;
* retries;

harder to control.

---

## 84.5 Silent Failures

Avoid:

```text id="j9n3x0"
request failed
→ nothing happens
```

The user should receive an appropriate indication of failure.

---

## 84.6 Infinite Loading

Every loading state must have a defined path to:

```text id="3m5k8p"
Success
Error
Empty
Cancellation
```

where applicable.

---

## 84.7 Duplicate Business Logic

Do not implement critical business rules independently in multiple screens.

---

## 84.8 Unbounded Rendering

Do not render very large datasets when pagination or virtualization is appropriate.

---

## 84.9 Stale State

Do not allow an older API response to overwrite newer user state.

---

## 84.10 Hard-Coded Secrets

Anything shipped to the browser must be considered public.

Frontend code must never contain confidential backend credentials.

---

# 85. Relationship with Other Development Documents

This document defines frontend coding and engineering standards.

It works together with:

* `01_Development_Architecture_Overview.md`;
* `02_Repository_Structure_and_Conventions.md`;
* `04_Commit_Message_and_Change_Standards.md`;
* `05_Pull_Request_and_Code_Review_Process.md`;
* `06_Backend_Development_Standards.md`;
* `09_API_Development_and_Contract_Change_Workflow.md`;
* `10_Documentation_First_Development_Workflow.md`;
* `13_Testing_and_Debugging_Workflow.md`;
* `14_Dependency_and_Package_Management.md`;
* `15_Configuration_and_Feature_Flag_Development.md`;
* `16_AI_Assisted_Development_Guidelines.md`;
* `18_Development_Guardrails_and_Quality_Rules.md`.

Frontend behavior must also remain consistent with the approved business, system, security, architecture, API, and testing documentation.

---

# 86. Frontend Development Invariants

The following rules are mandatory project invariants:

1. The backend remains the authority for business rules.
2. The frontend must never be the only security boundary.
3. Components must have clear responsibilities.
4. Business features should have clear ownership.
5. Shared components must have genuinely shared responsibility.
6. Global state must be used only where justified.
7. Server state must not be confused with local UI state.
8. API communication must follow approved contracts.
9. Raw API calls should not be unnecessarily scattered across components.
10. Authentication state must be handled explicitly.
11. Permission-aware UI must not replace backend authorization.
12. Tenant context must remain isolated.
13. Branch context must remain clear.
14. Loading states must be intentional.
15. Error states must be intentional.
16. Empty states must be distinguished from failures.
17. Important operations must provide appropriate success feedback.
18. Duplicate submissions must be prevented at the UI level where practical.
19. Backend idempotency remains authoritative for retry-sensitive operations.
20. Client validation must not replace server validation.
21. Financial calculations must not rely solely on frontend values.
22. Inventory rules must not be enforced only by the frontend.
23. Offline state must be visible when relevant.
24. Local-only operations must not be presented as server-confirmed.
25. Synchronization state must be understandable.
26. Sensitive data must not be unnecessarily stored in browser storage.
27. Frontend secrets must never be embedded in client code.
28. Large collections must be appropriately bounded.
29. Performance optimization must be evidence-based.
30. Accessibility must be considered during implementation.
31. Important user behavior must be covered by appropriate tests.
32. Critical workflows should have end-to-end coverage where justified.
33. User-facing errors must not expose internal implementation details.
34. Stale asynchronous responses must not overwrite current state.
35. Feature flags must not be treated as security controls.
36. Subscription restrictions must also be enforced by the backend.
37. Destructive operations must follow approved business rules.
38. Frontend terminology must remain consistent with the domain model.
39. UI behavior must remain traceable to approved product requirements.
40. Frontend code must remain understandable, testable, and maintainable.

---

# 87. Final Principle

The FastFood frontend is the user's operational interface to the system.

It should make correct operations clear and efficient while making system state understandable.

The frontend should communicate:

```text id="v1q5b8"
What can I do?
        ↓
What state is the system in?
        ↓
What is happening now?
        ↓
Did the operation succeed?
        ↓
If not, what can I do next?
```

At the same time, the frontend must never assume that hiding an action makes that action secure.

The backend remains the authority for:

* permissions;
* business rules;
* financial correctness;
* inventory correctness;
* tenant isolation;
* branch isolation;
* subscription enforcement;
* data integrity.

**Final rule:**

> The frontend should make the correct workflow obvious, the system state understandable, and the user interaction efficient—while leaving authoritative business and security enforcement to the backend.

