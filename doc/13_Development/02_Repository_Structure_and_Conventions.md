# DEV-02 — Repository Structure and Conventions

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the repository structure, folder organization, naming conventions, file placement rules, and general repository organization standards for the FastFood ERP project.

The goal is to ensure that developers can:

* quickly locate relevant code;
* understand repository boundaries;
* add new functionality consistently;
* avoid arbitrary folder structures;
* preserve architectural boundaries;
* maintain predictable naming;
* keep tests close to the behavior they verify;
* distinguish source code from generated and temporary files;
* keep documentation and implementation organized;
* reduce unnecessary repository complexity.

This document defines **where things belong and how they are named**.

Detailed coding rules are defined in the backend and frontend development standards.

---

# 2. Scope

This document covers:

* repository organization;
* top-level directories;
* application source structure;
* backend structure;
* frontend structure;
* tests;
* database migrations;
* configuration;
* scripts and developer tooling;
* documentation;
* architecture decisions;
* generated files;
* temporary files;
* naming conventions;
* file placement;
* module boundaries;
* import boundaries;
* test placement;
* repository hygiene;
* prohibited structures;
* repository invariants.

It does not define:

* detailed backend coding style;
* detailed frontend coding style;
* Git branching strategy;
* commit message format;
* pull request workflow;
* database migration procedure;
* API contract design.

Those topics are defined by their dedicated development documents.

---

# 3. Repository Organization Principles

The repository should follow these principles:

1. **Predictability** — developers should know where a file belongs.
2. **Separation of Concerns** — unrelated responsibilities should remain separated.
3. **Architectural Alignment** — folder structure should support system architecture.
4. **Discoverability** — important functionality should be easy to locate.
5. **Minimal Duplication** — the same responsibility should not exist in multiple unrelated locations.
6. **Explicit Ownership** — each directory should have a clear purpose.
7. **Testability** — source structure should support isolated testing.
8. **Environment Safety** — development, testing, and production artifacts must not be mixed.
9. **Repository Hygiene** — generated and temporary files must not pollute source directories.
10. **Stable Naming** — names should remain predictable across the project.

---

# 4. Repository Boundaries

The project documentation repository and application repositories must remain conceptually distinct.

The documentation repository contains authoritative project documentation, architecture, analysis, ADRs, and development guidance.

The application repository contains executable application code and its directly associated development artifacts.

A repository must not become an uncontrolled mixture of:

* production source code;
* unrelated experiments;
* personal files;
* temporary debugging artifacts;
* generated build output;
* credentials;
* unrelated documentation.

---

# 5. High-Level Application Repository Structure

The exact physical repository structure may evolve as implementation progresses.

The baseline organization should follow this conceptual model:

```text
repository/
├── README.md
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── .env.example
│
├── backend/
├── frontend/
│
├── migrations/
│
├── tests/
│
├── scripts/
├── tools/
│
├── docs/
│
└── infrastructure/
```

Not every directory must exist from the first implementation stage.

A directory should be introduced when it has a real responsibility.

---

# 6. Root-Level Files

Root-level files should contain only repository-wide information or configuration.

Typical files include:

| File             | Purpose                                              |
| ---------------- | ---------------------------------------------------- |
| `README.md`      | Repository overview and developer entry point        |
| `AGENTS.md`      | Agent/developer working instructions                 |
| `CHANGELOG.md`   | Significant release/change history                   |
| `LICENSE`        | Project licensing information                        |
| `pyproject.toml` | Python project configuration and dependency metadata |
| `.gitignore`     | Files excluded from version control                  |
| `.env.example`   | Example environment configuration without secrets    |

Additional root files are allowed when they represent repository-wide tooling or standards.

Unrelated application files should not be placed at the root merely because it is convenient.

---

# 7. README.md

The root `README.md` should provide the repository entry point.

It should explain, as appropriate:

* what the project is;
* repository purpose;
* major components;
* local development entry point;
* important documentation;
* supported development workflow;
* basic setup;
* testing entry point;
* links to deeper documentation.

The README should remain concise enough to function as an entry point.

Detailed architecture should remain in the appropriate documentation.

---

# 8. AGENTS.md

`AGENTS.md` contains instructions intended for developers and AI coding agents working with the repository.

It may define:

* repository-specific rules;
* important commands;
* architecture constraints;
* directory-specific instructions;
* prohibited actions;
* testing expectations;
* documentation requirements;
* development workflow requirements.

Instructions should be specific and actionable.

Directory-specific `AGENTS.md` files may be introduced when a subtree has materially different rules.

More specific instructions should not silently contradict higher-level project rules.

---

# 9. Backend Structure

The backend should reflect the system's architectural boundaries rather than being organized only by technical file type.

A conceptual structure may be:

```text
backend/
├── app/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── interfaces/
│   └── shared/
│
└── ...
```

The exact framework-specific structure may evolve.

The important principle is that folder organization must preserve architectural responsibilities.

---

# 10. Domain Structure

Domain code should contain business concepts and business rules.

Conceptual examples:

```text
domain/
├── orders/
├── inventory/
├── recipes/
├── products/
├── pricing/
├── employees/
├── permissions/
├── cash/
├── payments/
├── subscriptions/
└── branches/
```

The final domain grouping should follow the approved domain model.

Domain folders should not become generic dumping grounds.

---

# 11. Application Structure

Application code coordinates use cases and workflows.

Conceptual examples:

```text
application/
├── orders/
├── inventory/
├── recipes/
├── payments/
├── cash/
├── employees/
├── reports/
└── subscriptions/
```

Application code may coordinate:

* domain operations;
* repositories;
* transactions;
* authorization checks;
* external operations;
* events;
* background work.

Business rules that belong to the domain should not be duplicated unnecessarily inside application services.

---

# 12. Infrastructure Structure

Infrastructure contains technical implementations required by the application.

Conceptual examples:

```text
infrastructure/
├── database/
├── cache/
├── messaging/
├── storage/
├── printing/
├── external_services/
└── configuration/
```

Infrastructure code must not become the default location for business rules simply because it interacts with external systems.

---

# 13. Interface Structure

Interfaces expose application capabilities to external consumers.

Conceptual examples:

```text
interfaces/
├── api/
├── web/
├── cli/
└── workers/
```

The exact structure depends on the implementation architecture.

API interface code should remain separate from domain logic.

---

# 14. Shared Code

Shared code should contain only genuinely cross-cutting functionality.

Examples may include:

* common primitives;
* common error types;
* shared utility abstractions;
* common identifiers;
* common infrastructure contracts.

A shared module must not become a dumping ground for unrelated functions.

Before placing code into `shared`, the developer should verify that it is actually shared.

---

# 15. Frontend Structure

The frontend should be organized around application responsibilities and user-facing features rather than arbitrary file types.

A conceptual structure is:

```text
frontend/
├── src/
│   ├── app/
│   ├── features/
│   ├── components/
│   ├── layouts/
│   ├── services/
│   ├── state/
│   ├── hooks/
│   ├── utils/
│   └── assets/
│
└── ...
```

The exact frontend framework may determine the final physical structure.

The structure should support:

* feature isolation;
* reusable components;
* predictable API access;
* state management;
* permission-aware UI;
* testing;
* maintainability.

---

# 16. Feature Organization

When a feature contains substantial frontend logic, related files should be grouped together.

For example:

```text
features/
└── orders/
    ├── components/
    ├── pages/
    ├── hooks/
    ├── services/
    ├── state/
    ├── types/
    └── tests/
```

This is preferred over scattering all order-related files across unrelated global folders when the feature is sufficiently large.

Small reusable elements may remain in shared component directories.

---

# 17. Shared Frontend Components

Reusable UI components should be placed in a shared location only when they are genuinely reusable.

Examples:

```text
components/
├── forms/
├── tables/
├── dialogs/
├── navigation/
├── feedback/
└── common/
```

A component used by only one feature should normally remain inside that feature.

This reduces accidental coupling.

---

# 18. Tests Directory

Tests should have a predictable relationship with the source code.

A conceptual structure is:

```text
tests/
├── unit/
├── domain/
├── application/
├── integration/
├── api/
├── e2e/
├── security/
├── performance/
├── resilience/
└── fixtures/
```

The exact organization may be refined as implementation develops.

Test classification should correspond to the testing architecture defined in `12_Testing`.

---

# 19. Test Placement Principle

Tests should be easy to locate from the behavior they verify.

A test should not be placed in an unrelated directory merely because that directory already exists.

For example:

```text
orders/
    implementation

tests/
    orders/
```

or a feature-local test structure may be used where appropriate.

The selected convention should remain consistent within the relevant project area.

---

# 20. Test Fixtures and Builders

Reusable test data should have a clear location.

Conceptual structure:

```text
tests/
└── fixtures/
    ├── orders/
    ├── inventory/
    ├── employees/
    └── subscriptions/
```

Fixtures should not contain hidden production behavior.

Test builders should create valid test objects without making tests dependent on unnecessary implementation details.

---

# 21. Database Migrations

Database migrations should be stored separately from ordinary application source code.

Baseline:

```text
migrations/
├── versions/
└── ...
```

Migration files must remain ordered and traceable.

Migration names should clearly communicate their purpose.

Example:

```text
2026_001_create_branch_tables
2026_002_add_cash_session_status
2026_003_add_recipe_versioning
```

The exact migration naming format may be determined by the selected migration tooling, but the naming must remain understandable.

Detailed migration workflow is defined in:

`08_Database_Development_and_Migration_Workflow.md`

---

# 22. Scripts

The `scripts/` directory is intended for repository-level development and operational helper scripts.

Examples:

```text
scripts/
├── setup/
├── development/
├── testing/
├── database/
└── maintenance/
```

Scripts should have a clear purpose and documented usage where necessary.

A script should not silently perform destructive actions.

Dangerous operations should require explicit confirmation or an explicit safe mode.

---

# 23. Tools

The `tools/` directory may contain developer tooling that is not part of the application runtime.

Examples:

* code generation helpers;
* repository analysis tools;
* documentation helpers;
* test utilities;
* development automation.

Tools must not be imported into production runtime code unless they are intentionally part of the product.

---

# 24. Infrastructure

Infrastructure-related configuration should be separated from application source code.

Conceptual examples:

```text
infrastructure/
├── development/
├── testing/
├── staging/
└── production/
```

Actual production infrastructure definitions must follow the deployment architecture.

Development repositories must not contain production secrets.

---

# 25. Documentation

Documentation should be organized according to its ownership and purpose.

Application repositories may contain developer-facing documentation such as:

```text
docs/
├── development/
├── api/
├── operations/
└── guides/
```

The authoritative project documentation repository remains the primary location for the complete architecture and analysis documentation.

Application repositories may link to it rather than duplicating the entire documentation set.

---

# 26. Architecture Decision Records

ADR files should remain in a predictable location.

Where ADRs are maintained inside the repository:

```text
adr/
├── ADR-001-...
├── ADR-002-...
└── ...
```

ADR naming should include:

* stable identifier;
* short descriptive title.

Example:

```text
ADR-001-Documentation-First-Development.md
ADR-002-Offline-Synchronization-Strategy.md
```

Detailed ADR workflow is defined in:

`11_ADR_and_Architecture_Decision_Workflow.md`

---

# 27. Configuration Files

Configuration should be separated according to responsibility.

Examples include:

```text
config/
├── development/
├── testing/
└── shared/
```

However, configuration should not be duplicated unnecessarily.

Environment-specific values should come from the appropriate environment mechanism.

Secrets must never be committed.

---

# 28. Environment Files

An example configuration may be committed:

```text
.env.example
```

Actual secret-bearing files such as:

```text
.env
.env.local
.env.production
```

must not be committed unless explicitly designed as non-secret configuration and approved by project policy.

The default repository should assume that `.env`-style local secret files are ignored.

---

# 29. Generated Files

Generated files must be clearly distinguished from manually maintained source files.

Examples may include:

* build output;
* generated API clients;
* generated schemas;
* compiled frontend assets;
* generated documentation;
* cache files.

Generated files should not be committed unless there is a documented reason.

If generated files are committed, the repository must define:

* how they are generated;
* which source is authoritative;
* when they must be regenerated;
* how generated output is validated.

---

# 30. Build and Cache Output

Temporary build and cache directories must not pollute the repository.

Examples include:

```text
__pycache__/
.pytest_cache/
node_modules/
dist/
build/
coverage/
.cache/
```

Whether a specific directory is ignored depends on the tooling used, but generated local artifacts should normally remain outside version control.

---

# 31. Temporary Files

Temporary development files must not be committed.

Examples:

```text
debug.log
dump.sql
test-output.txt
scratch.py
tmp/
```

If a temporary tool becomes permanently useful, it should be converted into an intentional repository tool with:

* a clear name;
* a clear purpose;
* documentation where needed;
* appropriate tests.

---

# 32. Naming Philosophy

Names should optimize for:

1. clarity;
2. consistency;
3. discoverability;
4. stable meaning;
5. low ambiguity.

Avoid names that require the reader to inspect implementation before understanding the purpose.

Prefer:

```text
cash_session
recipe_version
branch_permission
inventory_adjustment
```

over vague names such as:

```text
data
manager
helper
misc
thing
temp
common2
```

---

# 33. Directory Naming

Directory names should:

* use one consistent convention;
* represent a meaningful responsibility;
* avoid unnecessary abbreviations;
* remain stable;
* avoid generic names unless genuinely appropriate.

For Python-oriented backend directories, lowercase `snake_case` should be preferred.

Examples:

```text
inventory/
cash_sessions/
external_services/
```

---

# 34. Python Module Naming

Python modules should normally use lowercase `snake_case`.

Examples:

```text
cash_session.py
inventory_adjustment.py
recipe_service.py
branch_permission.py
```

Avoid inconsistent naming such as:

```text
CashSession.py
cashSession.py
cash-session.py
```

unless required by a specific external convention.

---

# 35. Python Package Naming

Python packages should normally use lowercase `snake_case`.

Examples:

```text
inventory/
recipes/
cash/
external_services/
```

Package names should communicate the responsibility of the package.

---

# 36. Class Naming

Classes should normally use `PascalCase`.

Examples:

```text
CashSession
InventoryAdjustment
RecipeVersion
BranchPermission
```

A class name should represent a meaningful concept rather than an implementation mechanism whenever possible.

---

# 37. Function and Method Naming

Functions and methods should normally use lowercase `snake_case`.

Examples:

```text
open_cash_session()
calculate_recipe_cost()
validate_branch_access()
create_inventory_adjustment()
```

Names should communicate the action or result.

Avoid vague names such as:

```text
do_it()
process()
handle()
run()
execute()
```

unless the surrounding context makes the meaning explicit and the generic name is genuinely appropriate.

---

# 38. Variable Naming

Variables should use clear, meaningful names.

Prefer:

```text
branch_id
cash_session_id
available_quantity
subscription_expires_at
```

over:

```text
id
data
value
obj
x
tmp
```

Short names may be appropriate for very small local scopes, but important business concepts should remain explicit.

---

# 39. Constant Naming

Constants should follow the language's established convention.

For Python, module-level constants should normally use uppercase `SNAKE_CASE`.

Examples:

```text
MAX_CASH_CORRECTIONS
DEFAULT_PAGE_SIZE
SESSION_NUMBER_DIGITS
```

Constants should represent genuine constants rather than values that should be configurable.

---

# 40. Type and Schema Naming

Types, DTOs, schemas, and similar structures should use names that identify their responsibility.

Examples:

```text
CreateOrderRequest
OrderResponse
InventoryAdjustmentRequest
CashSessionSummary
BranchPermission
```

Avoid ambiguous names such as:

```text
Data
RequestData
ResponseData
Object
Payload
```

unless the abstraction is genuinely generic.

---

# 41. API File Naming

API-related files should communicate the endpoint or domain responsibility.

Examples:

```text
orders.py
inventory.py
cash_sessions.py
employees.py
reports.py
```

Avoid grouping unrelated endpoints into a generic file such as:

```text
everything.py
misc.py
routes2.py
```

---

# 42. Database Naming

Database naming should remain consistent with the database architecture.

Names should clearly represent domain concepts.

Typical conventions should use:

* lowercase;
* `snake_case`;
* singular or plural convention consistently;
* explicit relationship names;
* meaningful constraint names.

The repository must not introduce inconsistent naming patterns across migrations.

Detailed database conventions are defined in the database documentation.

---

# 43. Frontend Naming

Frontend naming should follow the selected frontend framework's standard conventions while maintaining project-wide consistency.

Typical examples:

```text
OrderCard
OrderTable
CashSessionDialog
InventoryAdjustmentForm
```

Feature and folder names should remain consistent with backend domain terminology where the same concept is represented.

---

# 44. Domain Terminology

The same business concept should use the same name throughout the repository.

For example, if the approved domain terminology is:

```text
Cash Session
Branch
Recipe
Semi-Finished Product
Inventory Adjustment
Subscription
```

developers should not introduce unrelated synonyms such as:

```text
Register Session
Location
Formula
Intermediate Item
Stock Fix
Plan
```

unless the distinction represents a genuinely different concept.

Consistent terminology reduces misunderstandings between documentation, code, database, API, and UI.

---

# 45. Identifier Naming

Identifiers should distinguish between different identity concepts.

For example, the system may contain:

* persistent database identifiers;
* customer-facing numbers;
* transaction identifiers;
* synchronization operation identifiers;
* device identifiers.

These must not be represented by ambiguous names.

For example, a customer-facing three-digit cash-session number should not be confused with the persistent database identifier of the session.

---

# 46. File Naming

File names should:

* describe their purpose;
* follow the language/framework convention;
* avoid unnecessary abbreviations;
* avoid spaces;
* avoid ambiguous numbering unless numbering is part of the documentation convention.

Good examples:

```text
cash_session_service.py
inventory_adjustment_repository.py
order_status.py
recipe_version.py
```

Poor examples:

```text
service.py
helper.py
new.py
final.py
final2.py
test2.py
```

---

# 47. Avoiding Generic Folders

The following directories should not become dumping grounds:

```text
utils/
helpers/
common/
misc/
services/
managers/
```

Such directories may exist when they have a clearly defined architectural responsibility.

Before adding code to one of them, the developer should ask whether the code belongs to a more specific domain or feature.

---

# 48. Module Boundaries

A module should have a clear responsibility.

A module should not grow indefinitely simply because it started as the first place where a feature was implemented.

Warning signs include:

* hundreds of unrelated functions;
* unrelated domain concepts;
* multiple business areas in one module;
* excessive conditional branching;
* unrelated imports;
* difficult-to-test behavior.

When a module becomes difficult to understand, it should be evaluated for decomposition.

---

# 49. Import Boundaries

Imports should respect architecture.

Typical direction:

```text
Interface
   ↓
Application
   ↓
Domain

Infrastructure
   ↑
Application / infrastructure boundary
```

The exact dependency direction is defined by the architecture documentation.

The repository structure must not encourage circular dependencies.

Domain code should not casually depend on infrastructure implementation details.

---

# 50. Circular Dependencies

Circular dependencies should normally be treated as a design problem.

Developers should not solve them by:

* arbitrary lazy imports;
* hidden global state;
* moving unrelated code into `utils`;
* duplicating business logic.

The underlying dependency relationship should be reconsidered.

Exceptions require a clear technical reason and should remain understandable.

---

# 51. One Responsibility Per File

A file should generally have a coherent responsibility.

This does not mean every file must contain exactly one class or function.

It means unrelated responsibilities should not be grouped together merely to reduce file count.

For example, an order domain module may reasonably contain closely related order concepts.

It should not also contain unrelated payroll or subscription logic.

---

# 52. Avoiding Excessive Fragmentation

The opposite problem should also be avoided.

Do not create dozens of tiny files simply because every class could technically have its own file.

The goal is:

```text
Clear responsibility
+
Reasonable cohesion
+
Easy navigation
```

not maximum file count.

---

# 53. Test Naming

Test names should clearly describe the behavior being verified.

Examples:

```text
test_order_cannot_be_paid_twice
test_sale_is_blocked_when_required_ingredient_is_unavailable
test_manager_cannot_access_unassigned_branch
test_fourth_cash_correction_requires_privileged_reopen
```

Tests should describe behavior rather than implementation details whenever possible.

---

# 54. Test File Naming

Test files should make the tested subject obvious.

Examples:

```text
test_order_service.py
test_cash_session.py
test_inventory_adjustment.py
test_branch_authorization.py
```

The exact naming convention may follow the selected testing framework.

Consistency is more important than a single universal filename pattern.

---

# 55. Documentation File Naming

Documentation filenames should:

* be descriptive;
* remain stable;
* use consistent numbering when the documentation section uses ordered documents;
* avoid ambiguous names.

The project documentation repository uses ordered names such as:

```text
01_Development_Architecture_Overview.md
02_Repository_Structure_and_Conventions.md
```

This ordering is part of the documentation structure and should not be changed casually.

---

# 56. ADR File Naming

ADR filenames should use:

```text
ADR-NNN-Short-Descriptive-Title.md
```

Example:

```text
ADR-001-Documentation-First-Development.md
```

The identifier must remain stable even if the decision is later superseded.

---

# 57. No Personal or Machine-Specific Files

The repository must not contain personal development artifacts such as:

```text
notes_personal.md
my_test.py
desktop_backup/
screenshots/
private/
```

unless they are intentionally part of the project.

Machine-specific editor settings should be committed only when the project intentionally standardizes them.

---

# 58. Editor Configuration

Editor configuration may be committed when it improves team consistency.

Examples:

```text
.vscode/
.editorconfig
```

Only project-relevant configuration should be committed.

Personal preferences should not be forced on every developer unless intentionally standardized.

---

# 59. Formatting Configuration

Formatting and linting configuration should have a single authoritative location.

Do not create competing formatter configurations for the same source tree without a documented reason.

For example, if Python formatting is defined centrally, individual developers should not introduce incompatible formatting rules in subdirectories.

---

# 60. Configuration Precedence

When multiple configuration layers exist, their precedence must be explicit.

Typical hierarchy:

```text
Project Defaults
      ↓
Environment Configuration
      ↓
Runtime Configuration
```

The actual configuration architecture is defined elsewhere.

The repository should avoid hidden configuration sources.

---

# 61. Generated API or Schema Files

If API clients, schemas, or other artifacts are generated:

```text
source definition
       ↓
generation tool
       ↓
generated artifact
```

The source definition remains authoritative.

Generated output must not be manually edited unless the generation workflow explicitly permits it.

---

# 62. Dependency Lock Files

Dependency lock files should be committed when required for reproducible builds and environments.

The repository should have one clear source of truth for dependency versions.

Developers should not manually modify generated lock sections without understanding the dependency tool's behavior.

Detailed dependency policy is defined in:

`14_Dependency_and_Package_Management.md`

---

# 63. Case Sensitivity

Repository naming should avoid depending on case-sensitive filesystem behavior.

Do not create files whose names differ only by capitalization.

Avoid situations where:

```text
Order.py
order.py
```

both exist.

This prevents cross-platform development problems.

---

# 64. Path Length and Special Characters

Paths should remain portable.

Avoid:

* unnecessary deeply nested directories;
* spaces in technical paths;
* special characters;
* ambiguous punctuation;
* extremely long filenames.

Descriptive names should still remain practical.

---

# 65. Repository Hygiene

Before submitting a change, developers should check for:

* temporary files;
* debug output;
* generated artifacts;
* accidental secrets;
* unused imports;
* unused files;
* obsolete modules;
* accidental local configuration;
* unrelated changes.

The repository should remain clean after development work.

---

# 66. Deleting and Moving Files

When files are moved or renamed, developers should consider:

* imports;
* tests;
* documentation references;
* configuration;
* scripts;
* CI;
* generated files;
* deployment references.

A rename should not leave stale references behind.

---

# 67. Deprecated Code

Deprecated code should not remain indefinitely without a reason.

When code is intentionally retained for compatibility, it should have:

* a clear reason;
* known usage;
* an expected removal condition where practical.

Dead code should not be kept merely because removing it feels risky.

---

# 68. Experimental Code

Experimental code should be clearly isolated.

It should not silently become part of the production application.

Possible locations include:

```text
experiments/
prototypes/
```

only when such directories are intentionally supported by the repository.

Experimental code must not be imported into production code accidentally.

---

# 69. Debugging Code

Temporary debugging code must be removed before merge unless it is intentionally part of the product.

Examples of prohibited leftovers include:

* debug prints;
* hardcoded test identifiers;
* bypassed authorization;
* temporary database resets;
* disabled validation;
* forced success responses.

---

# 70. Secrets and Sensitive Files

The repository must never contain:

* passwords;
* API secrets;
* private keys;
* production credentials;
* database credentials;
* authentication tokens;
* real customer data;
* real payment credentials.

Example files should contain placeholders only.

Security requirements are defined in `11_Security`.

---

# 71. Real Production Data

Production data must not be copied into local development repositories merely for convenience.

If realistic test data is required, it should be:

* synthetic;
* appropriately anonymized;
* approved for the intended environment.

Testing data rules are defined in `12_Testing`.

---

# 72. Repository Growth

As the project grows, structure should evolve intentionally.

A directory should be split when:

* responsibilities become unclear;
* ownership becomes difficult;
* dependencies become tangled;
* tests become difficult to organize;
* navigation becomes difficult.

Structure should not be reorganized merely for cosmetic reasons.

---

# 73. Refactoring Repository Structure

Repository restructuring should consider:

* developer impact;
* import changes;
* CI impact;
* documentation references;
* deployment scripts;
* IDE configuration;
* test discovery;
* generated files.

Large structural changes should be reviewed as architectural or repository-level changes when appropriate.

---

# 74. Naming Consistency Across Layers

A concept should retain recognizable terminology across:

```text
Business Documentation
        ↓
Domain
        ↓
Database
        ↓
API
        ↓
Frontend
        ↓
Tests
```

Differences may exist because of technical conventions, but the underlying business meaning should remain clear.

For example:

```text
Business: Cash Session
Domain: CashSession
Database: cash_session
API: cash-session
Frontend: CashSession
Test: test_cash_session_...
```

This improves cross-layer discoverability.

---

# 75. Branch and Tenant Terminology

Because FastFood ERP is multi-business and multi-branch, repository naming must clearly distinguish:

* business/tenant;
* branch;
* user;
* employee;
* role;
* permission;
* resource scope.

Generic identifiers such as `company_id`, `location_id`, or `id` should not be introduced where they obscure the approved domain meaning.

---

# 76. Financial Terminology

Financial concepts must use explicit terminology.

Examples:

```text
payment
refund
cash_session
cash_handover
cash_correction
reconciliation
```

Avoid generic names such as:

```text
transaction
money
operation
adjustment
```

when they could refer to multiple different concepts.

---

# 77. Inventory Terminology

Inventory concepts should remain explicit.

Examples:

```text
ingredient
semi_finished_product
recipe
recipe_version
stock_movement
inventory_adjustment
purchase
warehouse
yield_loss
```

Naming must preserve the distinction between:

* raw ingredients;
* semi-finished products;
* ready products;
* recipes;
* stock movements;
* adjustments.

---

# 78. Offline and Synchronization Terminology

Offline functionality requires explicit naming because local and server state may differ.

Names should clearly distinguish concepts such as:

```text
sync_operation
sync_status
offline_queue
conflict
reconciliation
device
trusted_device
```

A generic `queue` or `status` should not obscure the actual responsibility when the distinction matters.

---

# 79. Status Naming

Status values should describe the actual state of the relevant entity.

Avoid reusing a generic status enumeration across unrelated domains merely because the values look similar.

For example:

```text
OrderStatus
CashSessionStatus
PaymentStatus
RecipeStatus
SubscriptionStatus
```

may represent different state machines.

---

# 80. Avoiding Magic Names

Names such as:

```text
manager
handler
processor
service
controller
helper
util
common
```

should be used only when they have a precise architectural meaning.

A more specific name is preferred when possible.

For example:

```text
OrderPaymentService
InventoryAdjustmentService
BranchPermissionChecker
RecipeApprovalService
```

is generally more discoverable than:

```text
Service
Helper
Manager
Processor
```

---

# 81. Repository Conventions for New Features

When adding a new feature, the developer should determine:

1. Which domain does it belong to?
2. Which application workflow does it belong to?
3. Which API interface exposes it?
4. Which frontend feature represents it?
5. Which database objects are required?
6. Which tests verify it?
7. Which documentation is affected?
8. Which configuration is required?
9. Which deployment impact exists?

The new feature should then be placed consistently with existing structure.

---

# 82. New Directory Rule

Before creating a new top-level directory, the developer should ask:

* Is the responsibility genuinely distinct?
* Could the existing structure contain it clearly?
* Will the new directory improve discoverability?
* Does it represent an architectural boundary?
* Will future developers understand why it exists?

New top-level directories should be intentional.

---

# 83. No Duplicate Sources of Truth

The repository should avoid maintaining the same authoritative information in multiple places.

Examples:

* dependency versions;
* API schemas;
* environment definitions;
* architecture decisions;
* generated models;
* configuration defaults.

When duplication is necessary, one source must be explicitly authoritative.

---

# 84. Repository Documentation Links

References between repository files should remain valid.

When moving or renaming a file:

* update internal links;
* update README references;
* update AGENTS instructions;
* update scripts if applicable;
* update CI references;
* update documentation indexes.

Broken documentation links should be treated as repository defects.

---

# 85. Repository Conventions and Architecture

Repository structure must support, not contradict, the architecture.

If architecture evolves, repository structure may need to evolve with it.

However, a folder rename alone must not be treated as an architecture change unless the underlying responsibility or dependency boundary changes.

---

# 86. Repository Invariants

The following rules are mandatory:

1. Every top-level directory must have a clear purpose.
2. Root-level files must represent repository-wide concerns.
3. Source code must not be mixed with temporary artifacts.
4. Generated files must be clearly controlled.
5. Secrets must never be committed.
6. Production data must not be committed.
7. Domain terminology must remain consistent.
8. Generic dumping-ground directories must be avoided.
9. Module responsibilities must remain understandable.
10. Circular dependencies should be avoided.
11. Architectural boundaries must be reflected in repository structure.
12. Tests must remain discoverable and organized.
13. Database migrations must remain traceable.
14. Configuration must be separated from source code appropriately.
15. Environment-specific secrets must remain outside version control.
16. File and directory names must follow established conventions.
17. Names must be meaningful enough to support navigation.
18. Case-sensitive naming conflicts must not be introduced.
19. Technical paths should remain portable.
20. Temporary debugging code must not be merged.
21. Experimental code must not accidentally become production code.
22. Deprecated code must have an intentional reason for retention.
23. New top-level directories require justification.
24. Duplicate sources of truth must be avoided.
25. Repository links must remain valid after structural changes.
26. Business concepts must retain recognizable terminology across layers.
27. Financial concepts must use explicit names.
28. Inventory and recipe concepts must remain distinguishable.
29. Offline and synchronization concepts must remain explicit.
30. Repository organization must remain consistent with the approved architecture.

---

# 87. Repository Structure Review Checklist

Before merging a structural change, review:

### Structure

* [ ] Is every new file in the correct directory?
* [ ] Is every new directory necessary?
* [ ] Does the structure match architectural boundaries?
* [ ] Are unrelated responsibilities separated?

### Naming

* [ ] Are names consistent?
* [ ] Are names descriptive?
* [ ] Are abbreviations avoided where unnecessary?
* [ ] Does domain terminology remain consistent?

### Source Control

* [ ] Are temporary files excluded?
* [ ] Are generated files handled correctly?
* [ ] Are secrets excluded?
* [ ] Is production data excluded?

### Dependencies

* [ ] Are imports consistent with architecture?
* [ ] Were circular dependencies avoided?
* [ ] Were stale references removed after moves?

### Tests

* [ ] Are tests located predictably?
* [ ] Are test names descriptive?
* [ ] Is test data organized appropriately?

### Documentation

* [ ] Were repository links updated?
* [ ] Were relevant documentation files updated?
* [ ] Was `AGENTS.md` updated if repository instructions changed?

---

# 88. Relationship to Other Development Documents

This document defines repository organization.

The following documents provide related detailed rules:

| Document | Relationship                                 |
| -------- | -------------------------------------------- |
| DEV-01   | Defines the overall development workflow     |
| DEV-03   | Defines Git branches and version control     |
| DEV-04   | Defines commit and change standards          |
| DEV-05   | Defines pull requests and code review        |
| DEV-06   | Defines backend development standards        |
| DEV-07   | Defines frontend development standards       |
| DEV-08   | Defines database development and migrations  |
| DEV-09   | Defines API development and contract changes |
| DEV-10   | Defines documentation-first development      |
| DEV-11   | Defines ADR workflow                         |
| DEV-12   | Defines local development environment        |
| DEV-13   | Defines testing and debugging                |
| DEV-14   | Defines dependencies and package management  |
| DEV-15   | Defines configuration and feature flags      |
| DEV-16   | Defines AI-assisted development              |
| DEV-17   | Defines developer tooling and automation     |
| DEV-18   | Defines development guardrails               |

---

# 89. Relationship to Other Documentation Sections

Repository conventions must remain consistent with:

* `01_Business_Analysis` — business terminology and approved requirements;
* `02_System_Analysis` — system behavior and boundaries;
* `03_Domain_Analysis` — domain terminology and business concepts;
* `04_Architecture` — architectural boundaries;
* `05_Database` — database structure and data conventions;
* `06_Backend` — backend architecture;
* `07_Frontend` — frontend architecture;
* `08_AI` — AI architecture and artifacts;
* `09_API` — API contracts;
* `10_Deployment` — deployment and runtime structure;
* `11_Security` — security boundaries;
* `12_Testing` — testing architecture.

Development structure must not contradict these authoritative sections.

---

# 90. Acceptance Criteria

This document is considered complete when:

* repository boundaries are defined;
* root-level organization is defined;
* backend structure principles are defined;
* frontend structure principles are defined;
* test organization is defined;
* migration organization is defined;
* scripts and tooling locations are defined;
* documentation and ADR locations are defined;
* configuration and environment file rules are defined;
* generated file handling is defined;
* temporary file handling is defined;
* naming conventions are defined;
* module and import boundaries are addressed;
* domain terminology consistency is defined;
* repository hygiene requirements are defined;
* secrets and production data restrictions are defined;
* repository restructuring principles are defined;
* repository invariants are defined;
* structural review criteria are defined.

---

# 91. Final Repository Rule

The repository should make the correct location for code obvious.

The primary rule is:

> **A developer should be able to understand where a new file belongs by understanding its responsibility, not by guessing where similar files happened to be placed previously.**

The repository structure must therefore remain:

```text
Predictable
    +
Consistent
    +
Architecturally Aligned
    +
Discoverable
    +
Testable
    +
Maintainable
```

Repository organization is not cosmetic. It is an engineering control that protects architecture, developer productivity, maintainability, and long-term project consistency.

