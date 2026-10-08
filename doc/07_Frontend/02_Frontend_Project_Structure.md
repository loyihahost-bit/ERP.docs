# Frontend Project Structure

**Document ID:** FA-02
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/07_Frontend/README.md`
**Previous Document:** `01_Frontend_Architecture.md`

---

## 1. Purpose

This document defines the physical and logical structure of the FastFood ERP Frontend codebase.

The structure must:

* support the modular frontend architecture;
* keep feature boundaries clear;
* prevent uncontrolled dependencies;
* support POS performance;
* support offline-first operation;
* support Business and Branch isolation;
* make permissions explicit;
* keep API and domain models separated;
* remain understandable for developers and AI agents;
* allow future growth without unnecessary complexity.

The project must remain a modular application rather than becoming a collection of unrelated components.

---

# 2. Architectural Structure

The Frontend is organized around the following major areas:

```text
Application Shell
      ↓
Features
      ↓
Entities
      ↓
Shared
```

Cross-cutting infrastructure:

```text
API
State
Synchronization
Configuration
```

Overall structure:

```text
frontend/
├── src/
│   ├── app/
│   ├── features/
│   ├── entities/
│   ├── shared/
│   ├── api/
│   ├── state/
│   ├── synchronization/
│   ├── configuration/
│   └── main.*
├── public/
├── tests/
└── package.json
```

---

# 3. Application Layer

The `app/` directory contains application-wide frontend infrastructure.

Recommended structure:

```text
src/app/
├── router/
├── providers/
├── shell/
├── guards/
└── initialization/
```

### `router/`

Responsible for:

* route definitions;
* route grouping;
* lazy-loaded feature routes;
* route metadata;
* navigation configuration.

### `providers/`

Contains application-wide providers such as:

* API provider;
* state provider;
* theme provider;
* localization provider;
* error boundary provider;
* query/cache provider.

### `shell/`

Contains the main application shell:

* sidebar;
* top navigation;
* branch selector;
* user menu;
* global notifications;
* page container;
* responsive shell behavior.

### `guards/`

Contains navigation/access guards.

Examples:

* authentication guard;
* permission guard;
* subscription guard;
* Business context guard;
* Branch context guard;
* device/offline guard.

### `initialization/`

Contains application startup logic.

Examples:

* loading configuration;
* restoring authenticated session;
* initializing local storage;
* loading Business/Branch context;
* initializing synchronization;
* registering service worker where applicable.

---

# 4. Features

The `features/` directory contains user-facing business capabilities.

Recommended structure:

```text
src/features/
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

Each feature owns its own UI workflow.

Example:

```text
features/orders/
├── pages/
├── components/
├── forms/
├── hooks/
├── queries/
├── mutations/
├── routes.*
├── types.*
└── index.*
```

Not every feature must contain every directory.

Directories should be created only when required.

---

# 5. Feature Responsibility

A feature is responsible for a complete user-facing capability.

For example:

```text
orders/
```

may contain:

* order list;
* order details;
* order status;
* order modification UI;
* refund request UI;
* order filters;
* order actions.

The feature should not directly own unrelated global infrastructure.

For example, an Order feature should not implement its own authentication system.

---

# 6. POS Feature

POS is a special high-performance feature.

Recommended structure:

```text
features/pos/
├── pages/
├── components/
├── product-search/
├── cart/
├── order/
├── payment/
├── tables/
├── delivery/
├── printer/
├── hooks/
├── queries/
├── mutations/
├── offline/
├── state/
├── types.*
└── index.*
```

POS should minimize unnecessary abstraction and rendering overhead.

The POS path must be optimized independently from administrative screens.

---

# 7. Entities

The `entities/` directory contains reusable representations of core business concepts.

Recommended structure:

```text
src/entities/
├── business/
├── branch/
├── employee/
├── product/
├── order/
├── inventory/
├── cash/
└── report/
```

Entities should contain reusable concepts, not complete page workflows.

For example:

```text
entities/product/
├── model.*
├── types.*
├── selectors.*
├── formatters.*
└── index.*
```

A Product entity may be used by:

* POS;
* menu;
* pricing;
* inventory;
* reports.

---

# 8. Entity vs Feature

The following rule applies:

```text
Entity = reusable business concept

Feature = user-facing business capability
```

Example:

```text
entities/product/
```

contains reusable Product representation.

```text
features/pos/
```

contains the workflow of selecting and selling Products.

A feature must not move complete business workflows into an entity merely for convenience.

---

# 9. Shared

The `shared/` directory contains reusable frontend primitives that do not belong to one specific business feature.

Recommended structure:

```text
src/shared/
├── ui/
├── forms/
├── hooks/
├── utils/
├── types/
├── validation/
└── formatting/
```

### `ui/`

Examples:

* Button;
* Modal;
* Dialog;
* Table;
* Dropdown;
* Tabs;
* Badge;
* Toast;
* Loading state;
* Empty state;
* Error state.

### `forms/`

Contains reusable form primitives.

### `hooks/`

Contains generic reusable hooks.

### `utils/`

Contains generic utilities.

### `types/`

Contains truly shared types.

### `validation/`

Contains reusable client-side validation helpers.

### `formatting/`

Contains:

* money formatting;
* date formatting;
* number formatting;
* status formatting.

---

# 10. Shared Dependency Rule

`shared/` must remain independent from business features.

This is prohibited:

```text
shared/
   ↓
features/orders/
```

Shared code must not depend on a specific feature.

This is allowed:

```text
features/orders/
   ↓
shared/
```

---

# 11. API Layer

The `api/` directory contains communication infrastructure with the Backend.

Recommended structure:

```text
src/api/
├── client/
├── contracts/
├── queries/
└── mutations/
```

### `client/`

Contains:

* HTTP client;
* authentication handling;
* request headers;
* request ID;
* operation ID;
* error normalization;
* retry policy where appropriate.

### `contracts/`

Contains API contract types and schemas.

### `queries/`

Contains read operations.

### `mutations/`

Contains write operations.

---

# 12. API and Feature Separation

Features must not implement raw HTTP calls throughout UI components.

Avoid:

```text
Button
  ↓
fetch(...)
```

Prefer:

```text
Component
   ↓
Feature Mutation
   ↓
API Layer
   ↓
Backend
```

This makes API behavior consistent and testable.

---

# 13. API Contract Authority

Frontend API contracts must reflect Backend API contracts.

The frontend must not invent server fields or business rules.

Client-side types may provide:

* UI-specific derived state;
* display formatting;
* local state.

They must not redefine authoritative Backend behavior.

---

# 14. State Management

The `state/` directory contains application-wide state categories.

Recommended structure:

```text
src/state/
├── session/
├── context/
├── offline/
└── ui/
```

### `session/`

Contains:

* authenticated employee;
* authentication state;
* session lifecycle.

### `context/`

Contains:

* current Business;
* current Branch;
* current device;
* current operational context.

### `offline/`

Contains:

* offline status;
* local authorization state;
* pending operation state;
* synchronization indicators.

### `ui/`

Contains truly global UI state.

Examples:

* sidebar state;
* global modal state;
* theme;
* global notification state.

---

# 15. State Ownership

State should be stored at the lowest appropriate level.

For example:

```text
Global:
Current Employee
Current Business
Current Branch
Offline State

Feature:
Order creation state
Inventory filter state
Report filter state

Component:
Modal open/close
Input focus
Temporary UI state
```

Avoid putting every state value into a global store.

---

# 16. Server State vs Client State

The Frontend must distinguish:

```text
Server State
Client/UI State
Offline State
Session State
```

Server state includes:

* Products;
* Orders;
* Inventory;
* Cash Sessions;
* Reports;
* Employees.

Client/UI state includes:

* selected tab;
* modal state;
* temporary filters;
* local visual preferences.

The same server object must not be duplicated into multiple unrelated global stores without justification.

---

# 17. Synchronization

The `synchronization/` directory contains offline synchronization infrastructure.

Recommended structure:

```text
src/synchronization/
├── queue/
├── sync/
├── conflicts/
└── storage/
```

### `queue/`

Contains pending operations.

### `sync/`

Contains synchronization orchestration.

### `conflicts/`

Contains conflict representation and UI-facing conflict state.

### `storage/`

Contains local persistence adapters.

---

# 18. Offline Storage

Offline-capable data must use the approved local storage mechanism.

The local storage layer must support:

* encryption where required;
* device binding;
* operation UUID;
* queued operations;
* configuration snapshots;
* synchronization metadata.

The frontend must not treat browser storage as authoritative.

---

# 19. Configuration

The `configuration/` directory contains frontend runtime/configuration definitions.

Recommended structure:

```text
src/configuration/
├── environment.*
├── routes.*
├── feature-flags.*
├── defaults.*
└── validation.*
```

Environment-specific values must not be hardcoded into feature components.

Business configuration must come from the Backend.

---

# 20. Routing Structure

Routes should be grouped by feature.

Conceptual structure:

```text
/
├── login
├── dashboard
├── pos
├── orders
├── cash
├── inventory
├── products
├── recipes
├── sets
├── menu
├── pricing
├── attendance
├── payroll
├── reports
├── notifications
└── administration
```

Routes must be protected according to:

* authentication;
* Business context;
* Branch context;
* permission;
* subscription state.

---

# 21. Lazy Loading

Large administrative features should be loaded lazily where practical.

Potential lazy-loaded areas:

* reports;
* payroll;
* administration;
* advanced inventory;
* configuration;
* audit/history.

POS must prioritize fast initial availability.

Lazy loading must not delay the core POS workflow unnecessarily.

---

# 22. Permission-Aware UI

The Frontend should hide or disable actions that the current employee cannot perform.

Example:

```text
Can View Product
Can Edit Product
Can Change Price
Can Apply Discount
Can Refund
Can Manage Employees
```

However:

> UI permission checks are not a security boundary.

The Backend must independently validate permissions.

---

# 23. Business and Branch Context

The active context should be centrally available.

Conceptual state:

```text
Current Context
├── Business
├── Branch
├── Employee
├── Device
└── Subscription
```

Changing Branch must trigger recalculation/reloading of:

* permissions;
* menu;
* pricing;
* operational configuration;
* Branch-specific data.

Old Branch state must not leak into the new Branch context.

---

# 24. Component Structure

Components should be organized by responsibility.

Example:

```text
features/menu/components/
├── MenuTable.*
├── MenuFilters.*
├── ProductAvailabilityToggle.*
├── PriceOverrideForm.*
└── MenuConfigurationDialog.*
```

Large components should be split when they contain multiple independent responsibilities.

However, components must not be fragmented merely for the sake of creating more files.

---

# 25. Forms

Forms should have:

* schema validation;
* clear error states;
* loading state;
* submit protection;
* permission awareness;
* server error handling;
* conflict handling where applicable.

Important mutation forms should prevent accidental duplicate submissions.

---

# 26. Query and Mutation Organization

Read operations and write operations should be clearly separated.

Example:

```text
features/products/
├── queries/
│   ├── listProducts.*
│   └── getProduct.*
└── mutations/
    ├── createProduct.*
    ├── updateProduct.*
    └── archiveProduct.*
```

Important commands should carry an operation UUID when required by the Backend contract.

---

# 27. Error Boundary Structure

Application-level error boundaries should protect the entire application.

Feature-level boundaries may protect independent areas.

Example:

```text
Application Error Boundary
        ↓
Feature Error Boundary
        ↓
Component
```

A non-critical feature failure should not unnecessarily terminate the entire POS application.

---

# 28. Loading State Structure

Loading states should distinguish:

* initial loading;
* background refresh;
* mutation processing;
* synchronization;
* offline processing.

The UI should not replace an already usable screen with a full-page loader for every background request.

---

# 29. Notification UI

Global notifications are handled through shared notification infrastructure.

Feature-specific events may produce:

* success message;
* warning;
* error;
* conflict;
* synchronization status.

Critical notifications must remain visible until acknowledged where required.

---

# 30. File and Export UI

Frontend file operations should use Backend-provided file references.

Examples:

* XLSX export;
* report download;
* uploaded image;
* document attachment.

The frontend must not assume that application-local filesystem paths are accessible.

File authorization remains server-side.

---

# 31. Testing Structure

Recommended test structure:

```text
tests/
├── unit/
├── integration/
├── component/
├── feature/
├── e2e/
└── offline/
```

### Unit

Tests:

* utilities;
* formatters;
* validators;
* pure state logic.

### Component

Tests:

* UI behavior;
* forms;
* interaction;
* accessibility basics.

### Feature

Tests complete feature workflows.

### E2E

Tests critical user journeys.

### Offline

Tests:

* operation queue;
* local persistence;
* synchronization;
* conflicts;
* recovery.

---

# 32. Test Placement

Small unit/component tests may live near their source files.

Example:

```text
ProductPriceForm.*
ProductPriceForm.test.*
```

Larger workflow tests should remain in the centralized `tests/` structure.

The project should use one consistent convention rather than mixing multiple styles without reason.

---

# 33. Naming Conventions

Names must be explicit and predictable.

Recommended:

```text
ProductList
ProductDetails
ProductPriceForm
OrderSummary
CashSessionCard
BranchSelector
```

Avoid meaningless names such as:

```text
Thing
Box
Helper
Manager
Stuff
CommonComponent
```

unless the meaning is genuinely clear from context.

---

# 34. File Naming

Use one project-wide naming convention.

Recommended:

```text
PascalCase
```

for component files where supported by the selected frontend framework.

Use descriptive names for:

* components;
* hooks;
* queries;
* mutations;
* schemas;
* types.

Do not use ambiguous abbreviations.

---

# 35. Barrel Exports

Barrel files such as:

```text
index.*
```

may be used to expose a module's public API.

They must not expose every internal implementation detail.

A feature should expose only what other modules are expected to use.

---

# 36. Public Module API

Each feature should have a clear public boundary.

Example:

```text
features/products/index.*
```

may export:

* ProductList;
* ProductDetails;
* product queries;
* product types intended for consumers.

Internal implementation should remain private.

This reduces accidental coupling.

---

# 37. Dependency Direction

The preferred dependency direction is:

```text
app
 ↓
features
 ↓
entities
 ↓
shared
```

Cross-cutting infrastructure is accessed through defined boundaries:

```text
features
 ↓
api
state
synchronization
```

Features should not depend directly on infrastructure implementation details.

---

# 38. Feature-to-Feature Dependencies

Direct feature-to-feature dependencies should be minimized.

For example:

```text
features/orders
   ↓
features/inventory
```

should not be the default architecture.

Prefer shared entities or application-level coordination.

If a direct dependency is necessary, it must be explicit and justified.

---

# 39. POS Isolation

POS must remain isolated from heavy administrative dependencies.

POS must not require loading:

* payroll;
* advanced reports;
* administration;
* audit history;
* large inventory reports

before the POS screen becomes usable.

This protects startup performance.

---

# 40. Offline Isolation

Offline infrastructure must remain separate from ordinary API concerns.

Conceptually:

```text
POS
 ↓
Application Data Layer
 ├── Online API
 └── Offline Storage
```

The POS should not contain duplicated business logic for online and offline modes.

Business rules remain defined by the Backend contract and approved frontend behavior.

---

# 41. Frontend Security Boundaries

Frontend code must never treat the following as secrets merely because they are hidden in the UI:

* permission decisions;
* Business IDs;
* Branch IDs;
* route names;
* feature flags.

Actual authorization remains Backend-side.

The Frontend must protect:

* session information;
* offline authorization;
* sensitive local data;
* tokens;
* operation metadata.

---

# 42. Performance Rules

Frontend implementation must avoid:

* unnecessary global re-renders;
* oversized initial bundles;
* uncontrolled polling;
* repeated API requests;
* unnecessary local storage writes;
* rendering huge lists without virtualization where required;
* expensive calculations on every render.

POS interaction should remain responsive.

Target:

```text
POS local interaction p95 ≤ 100 ms
```

---

# 43. Accessibility

All shared UI components should support:

* keyboard navigation;
* visible focus;
* semantic controls;
* accessible labels;
* appropriate contrast;
* error announcements;
* screen-reader compatible state.

POS should also support efficient keyboard operation where appropriate for desktop environments.

---

# 44. Internationalization

The Frontend should be structured so localization can be added without rewriting feature logic.

Text should not be scattered as hardcoded strings throughout business logic.

Recommended future structure:

```text
src/
└── localization/
    ├── uz/
    ├── ru/
    └── en/
```

The initial supported language configuration may be defined separately.

---

# 45. Date, Time and Currency

Frontend formatting must respect Business configuration.

The application must distinguish:

```text
UTC timestamp
Business timezone
Branch operational date
Displayed local date/time
```

Currency formatting must be centralized.

Financial values must not be represented through floating-point calculations when exact financial precision is required.

---

# 46. Build Structure

Production builds should separate:

* application code;
* static assets;
* environment configuration;
* service worker where used.

The production bundle should be optimized for:

* caching;
* compression;
* code splitting;
* lazy loading;
* fast initial load.

---

# 47. Public Directory

The `public/` directory contains static files that do not require normal application bundling.

Examples:

* icons;
* manifest;
* static branding assets;
* service worker assets where applicable.

Sensitive information must never be placed in `public/`.

---

# 48. Recommended Complete Structure

The recommended initial project structure is:

```text id="4u8p4r"
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
│   │
│   └── main.*
│
├── public/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── component/
│   ├── feature/
│   ├── e2e/
│   └── offline/
│
└── package.json
```

---

# 49. Anti-Patterns

The following structures are prohibited unless explicitly justified:

### Giant Components

```text
ProductPage
└── 2000+ lines of everything
```

### Generic Dump Folder

```text
src/
└── helpers/
    ├── everything.*
    └── random.*
```

### Global State for Everything

```text
globalStore
└── every piece of application state
```

### API Calls Inside UI Components

```text
Button
 └── fetch(...)
```

### Feature Logic Inside Shared

```text
shared/
└── orderBusinessLogic.*
```

### Direct Database-Like Thinking in Frontend

The frontend must not reproduce Backend persistence logic.

### Duplicate Business Rules

Online and offline paths must not implement two independently evolving versions of the same business rule.

---

# 50. AI-Agent Development Rules

AI agents modifying the Frontend must:

1. Read this document before creating new directories.
2. Check whether an existing feature already owns the required functionality.
3. Reuse existing entities before creating duplicate models.
4. Reuse shared components where appropriate.
5. Avoid moving business-specific code into `shared/`.
6. Respect feature boundaries.
7. Preserve API contract boundaries.
8. Preserve Business/Branch isolation.
9. Preserve offline synchronization behavior.
10. Preserve permission checks.
11. Preserve operation UUID/idempotency behavior.
12. Add tests for new behavior.
13. Update architecture documentation when structure changes materially.

An AI agent must not create a new architectural layer merely because it makes one task easier.

---

# 51. Structural Invariants

The following rules are mandatory:

1. `app/` contains application-wide frontend infrastructure.
2. `features/` contains user-facing business capabilities.
3. `entities/` contains reusable business concepts.
4. `shared/` contains generic reusable primitives.
5. `shared/` must not depend on features.
6. API calls are centralized through the API layer.
7. UI components must not directly implement raw HTTP communication.
8. Server state and UI state must remain distinguishable.
9. Global state must not contain every local UI value.
10. Business context is centrally managed.
11. Branch context is centrally managed.
12. Branch switching reloads Branch-scoped state.
13. Permission checks are available to UI components.
14. Backend authorization remains authoritative.
15. POS has a lightweight dependency path.
16. Administrative modules must not unnecessarily block POS startup.
17. Offline storage is not authoritative.
18. Synchronization is isolated from ordinary API infrastructure.
19. Pending operations use operation UUIDs.
20. Duplicate operations must be prevented.
21. API contracts are centralized.
22. Feature workflows remain inside their features.
23. Entity models remain reusable.
24. Shared modules remain business-agnostic.
25. Feature-to-feature dependencies are minimized.
26. Cross-feature communication must be explicit.
27. Large features may be lazy-loaded.
28. POS must prioritize fast startup.
29. Heavy reports must not block ordinary UI interaction.
30. Global error handling exists.
31. Feature-level recovery is supported where useful.
32. Loading states distinguish initial loading from background refresh.
33. Mutation states prevent accidental duplicate submissions.
34. Forms validate locally and handle server errors.
35. Permission-sensitive actions are reflected in UI.
36. UI permission checks are not security boundaries.
37. Authentication state is centrally managed.
38. Session expiration is handled consistently.
39. Offline state is globally observable.
40. Synchronization state is visible to users where necessary.
41. Conflict state is explicitly represented.
42. File access uses Backend-authorized references.
43. Sensitive data is not placed in public assets.
44. Environment configuration is not hardcoded in feature code.
45. Business configuration comes from the Backend.
46. Date/time formatting is centralized.
47. Currency formatting is centralized.
48. Localization must not require rewriting feature logic.
49. Shared UI components must support accessibility.
50. POS should support efficient keyboard interaction where applicable.
51. Production bundles must support code splitting.
52. Unnecessary global re-renders must be avoided.
53. Large collections must use appropriate rendering strategies.
54. Uncontrolled polling is prohibited.
55. Repeated API requests should be deduplicated where appropriate.
56. Client storage writes should be bounded.
57. Frontend must not silently modify authoritative financial values.
58. Frontend must not reinterpret historical transactions.
59. Frontend must not bypass subscription restrictions.
60. Frontend must not bypass Branch scope.
61. Frontend must not bypass Business scope.
62. Offline mode must not bypass authorization.
63. Trusted device state must be validated by Backend.
64. API errors must be normalized consistently.
65. Operation UUID handling must be consistent.
66. Tests must cover important workflows.
67. Offline workflows require dedicated testing.
68. E2E tests must cover critical user journeys.
69. Architectural changes must be documented.
70. AI agents must follow the documented dependency direction.

---

# 52. Performance SLOs

The following Frontend targets apply to the project:

| Metric                                                       |                      Target |
| ------------------------------------------------------------ | --------------------------: |
| Application shell interactive                                |                 p75 ≤ 2.5 s |
| Main authenticated route interactive                         |                 p75 ≤ 2.0 s |
| POS initial screen interactive                               |                 p75 ≤ 2.0 s |
| POS product search                                           |                p95 ≤ 150 ms |
| POS local interaction feedback                               |                p95 ≤ 100 ms |
| Normal API-driven list rendering                             | p95 ≤ 500 ms after response |
| Cached route transition                                      |                p95 ≤ 300 ms |
| Offline operation persistence                                |                p95 ≤ 200 ms |
| Synchronization UI update                                    |                       ≤ 2 s |
| Frontend fatal error rate                                    |             < 0.1% sessions |
| Client duplicate operation prevention                        |                    ≥ 99.99% |
| Unauthorized UI action prevention for known permission state |                        100% |
| Cross-Business client data isolation                         |                        100% |
| Critical frontend error detection                            |                      ≤ 60 s |

These are architecture targets and should be validated through testing and observability.

---

# 53. Relationship with Backend

Frontend depends on Backend contracts.

The relationship is:

```text
Frontend
   ↓
API Contract
   ↓
Backend Application
   ↓
Domain
   ↓
Database
```

Frontend must not duplicate authoritative Backend state management.

Backend remains responsible for:

* authorization;
* financial correctness;
* inventory correctness;
* order correctness;
* historical integrity;
* subscription enforcement;
* synchronization validation.

---

# 54. Relationship with Database

Frontend must not directly depend on database structure.

The frontend should consume API contracts rather than database models.

Therefore:

```text
Frontend
   ↓
API DTO / Contract
   ↓
Backend
   ↓
Database Model
```

Database schema changes should not automatically require frontend changes unless the API contract changes.

---

# 55. Relationship with Offline Architecture

Offline functionality is a first-class frontend capability.

The Frontend must support:

```text
Online
  ↓
API

Offline
  ↓
Local Storage
  ↓
Operation Queue
  ↓
Synchronization
```

The same user-facing workflow should remain understandable in both modes.

Offline-specific complexity should remain inside synchronization/storage boundaries rather than spreading across every feature.

---

# 56. Relationship with Security

Frontend security is complementary to Backend security.

Frontend provides:

* UI access control;
* session handling;
* secure local storage;
* safe token handling;
* offline state protection;
* secure rendering.

Backend provides final authorization.

No frontend-only security mechanism may be treated as sufficient for protecting business operations.

---

# 57. Relationship with Testing

Every new feature should have appropriate tests.

Critical FastFood workflows receive higher testing priority:

1. Authentication;
2. Branch switching;
3. POS;
4. Order creation;
5. Payment;
6. Cash session;
7. Inventory;
8. Offline operation;
9. Synchronization;
10. Conflict resolution;
11. Permissions;
12. Reports.

---

# 58. Status

**Document:** `02_Frontend_Project_Structure.md`

**Status:** Proposed

**Version:** 1.0

**Previous Document:** `01_Frontend_Architecture.md`

**Next Document:** `03_Design_System_and_UI_Principles.md`

**Frontend Architecture Documentation:** In Progress

