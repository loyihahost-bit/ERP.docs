# 18. Development Guardrails and Quality Rules

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the mandatory development guardrails and quality rules for the FastFood ERP project.

Its purpose is to establish clear boundaries for development so that implementation does not silently violate:

* business requirements;
* approved architecture;
* domain rules;
* database integrity;
* API contracts;
* frontend behavior;
* security boundaries;
* testing requirements;
* deployment constraints;
* operational requirements;
* documentation decisions.

These rules apply to developers, reviewers, technical leads, and AI-assisted development workflows.

The document is intentionally enforcement-oriented.

Other development documents explain **how** specific development activities are performed.

This document defines **what must not be violated**.

---

# 2. Scope

These guardrails apply to:

* backend development;
* frontend development;
* database development;
* API development;
* background workers;
* scheduled jobs;
* offline synchronization;
* AI-related development;
* configuration;
* feature flags;
* dependencies;
* developer tooling;
* tests;
* documentation;
* Git changes;
* pull requests;
* release preparation;
* maintenance and refactoring.

They apply to both new functionality and changes to existing functionality.

---

# 3. Guardrail Hierarchy

When development decisions conflict, the following hierarchy applies:

```text
1. Explicit safety and security requirements
        ↓
2. Approved business requirements
        ↓
3. Approved system/domain rules
        ↓
4. Accepted architecture decisions
        ↓
5. Database/API/security contracts
        ↓
6. Development standards
        ↓
7. Local implementation preferences
```

Lower-level preferences must not override higher-level constraints.

If two accepted documents conflict, the conflict must be resolved explicitly.

Developers must not silently choose whichever rule is easier to implement.

---

# 4. Core Quality Principles

The project follows these principles:

1. Correctness is more important than implementation speed.
2. Security is part of correctness.
3. Data integrity is part of correctness.
4. Business behavior must be explicit.
5. The backend remains authoritative for protected business rules.
6. Database constraints must protect critical invariants where appropriate.
7. Tests must demonstrate important behavior.
8. Documentation and implementation must remain consistent.
9. Every meaningful change must be reviewable.
10. Automation must not hide failures.
11. Simplicity is preferred over unnecessary complexity.
12. Performance must be considered without sacrificing correctness.
13. Historical and financial data must be treated as valuable records.
14. Tenant and branch boundaries must never be accidental.
15. Destructive behavior must be explicit and controlled.
16. AI-generated code is untrusted until validated.
17. Technical shortcuts must not silently become architecture.
18. Temporary solutions must have an explicit lifecycle.
19. Existing behavior must not be changed unintentionally.
20. The system must fail safely.

---

# 5. Rule Classification

Development rules are classified as:

### Mandatory

Must always be followed unless an accepted decision explicitly changes the rule.

### Conditional

Must be followed when the relevant scenario applies.

### Advisory

Recommended when practical but may be overridden with a documented reason.

This document primarily defines mandatory and conditional rules.

---

# 6. No Unapproved Business Rules

Developers must not invent business behavior during implementation without documenting the decision.

Examples include:

* inventing a new order status;
* changing refund behavior;
* changing stock deduction logic;
* changing subscription restrictions;
* changing payroll calculation;
* changing branch permissions;
* changing recipe approval behavior.

If the requirement is ambiguous:

```text
Ambiguity
   ↓
Analysis
   ↓
Decision
   ↓
Documentation
   ↓
Implementation
```

Do not silently convert an assumption into system behavior.

---

# 7. Documentation-First Rule

Meaningful functionality must be understood and documented before implementation.

The expected sequence is:

```text
Requirement
    ↓
Analysis
    ↓
Domain understanding
    ↓
Architecture/design
    ↓
Documentation
    ↓
Implementation
    ↓
Testing
    ↓
Review
```

The appropriate documentation does not need to be large.

The rule is about establishing the intended behavior before code becomes the source of accidental design.

---

# 8. Existing Documentation Must Be Checked First

Before changing functionality, developers must inspect relevant existing documentation.

Do not create a competing design when an accepted document already defines the behavior.

Before implementation, check:

* business analysis;
* system analysis;
* domain analysis;
* architecture;
* database;
* backend;
* frontend;
* API;
* security;
* testing;
* deployment;
* development;
* operations;
* ADRs.

---

# 9. Single Source of Truth

Important rules must have a clear source of truth.

Do not maintain the same business rule independently in:

* frontend;
* backend;
* database;
* documentation;
* scripts;
* configuration;

without defining ownership.

For example, a frontend may display whether an action is allowed, but protected authorization must remain server-side.

---

# 10. Architecture Boundary Rule

Implementation must respect accepted architecture boundaries.

Developers must not introduce dependencies that bypass architectural layers merely because the shortcut is convenient.

Examples of prohibited shortcuts include:

* frontend directly accessing the database;
* domain code depending on infrastructure implementation details;
* unrelated modules directly modifying another module's persistence state;
* bypassing application services for protected business operations.

Architecture-significant exceptions require explicit review.

---

# 11. Backend Authority Rule

The backend is authoritative for protected business behavior.

Frontend validation improves user experience but does not establish security or business authority.

The backend must validate where applicable:

* permissions;
* tenant scope;
* branch scope;
* resource ownership;
* financial operations;
* inventory operations;
* recipe changes;
* subscription restrictions;
* state transitions;
* sensitive configuration changes.

---

# 12. Tenant Isolation Rule

A request must never access another restaurant network's data merely because an identifier is known.

Tenant context must be established and enforced server-side.

Tenant isolation must apply to:

* reads;
* writes;
* updates;
* deletes;
* reports;
* exports;
* background jobs;
* files;
* caches;
* search;
* synchronization.

An identifier must never be treated as sufficient proof of access.

---

# 13. Branch Isolation Rule

Branch-specific resources must respect branch scope.

A user authorized for one branch must not automatically gain access to another branch.

Cross-branch operations require explicit authorization.

Branch scope must be consistently enforced across:

* APIs;
* database queries;
* reports;
* inventory;
* employees;
* cash registers;
* orders;
* menus;
* recipes;
* expenses;
* synchronization;
* background jobs.

---

# 14. Authorization Rule

Authorization must be enforced server-side.

The effective permission model is conceptually:

```text
Identity
   ↓
Tenant
   ↓
Branch Scope
   ↓
Role
   ↓
Functional Permission
   ↓
Resource Scope
   ↓
Action
```

Default behavior must be deny-by-default for protected operations.

Frontend visibility is not authorization.

---

# 15. Authentication Rule

Authentication must establish who is making a request.

Authentication must not be treated as proof that the user can perform every action.

Authentication and authorization must remain separate concepts.

Sensitive authentication changes require appropriate security controls.

---

# 16. Sensitive Operation Rule

Sensitive operations require stronger validation where appropriate.

Examples include:

* refunds;
* cash corrections;
* register reopening;
* permission changes;
* salary changes;
* recipe approval;
* inventory adjustments;
* subscription administration;
* sensitive configuration changes.

The implementation must follow the approved business and security model.

---

# 17. Financial Integrity Rule

Financial operations must preserve:

* amount correctness;
* transaction consistency;
* auditability;
* authorization;
* historical meaning.

Developers must not use floating-point shortcuts where they can cause monetary precision problems.

Financial calculations must have defined rounding behavior.

Refunds, payments, discounts, expenses, payroll, and cash operations must be tested at appropriate levels.

---

# 18. Inventory Integrity Rule

Inventory must not silently become negative.

Developers must not bypass the approved stock validation logic merely to allow an order to continue.

Inventory operations must preserve:

* quantity;
* unit;
* product relationship;
* branch/warehouse scope;
* source;
* cost where applicable;
* FIFO behavior;
* adjustment history;
* recipe dependencies.

---

# 19. Recipe Integrity Rule

Recipe changes must respect the approved lifecycle.

Developers must not:

* silently modify historical recipe behavior;
* delete recipes that must be archived;
* bypass approval;
* expose restricted recipe data;
* modify recipe components without permission.

Historical operations must remain understandable even when a recipe changes later.

---

# 20. Historical Data Rule

Historical records must not be changed merely to reflect current configuration.

Examples include:

* old orders;
* completed payments;
* previous cash register sessions;
* historical inventory adjustments;
* approved recipes;
* historical payroll;
* completed reports.

Current configuration and historical truth are different concepts.

When historical interpretation must remain stable, the required snapshot or versioning behavior must be preserved.

---

# 21. Deletion Rule

Permanent deletion must be exceptional.

Prefer:

```text
Active
   ↓
Archived
```

when historical relationships or auditability require preservation.

Before deleting data, developers must determine:

* whether the data is historical;
* whether other records reference it;
* whether reporting depends on it;
* whether legal/security requirements apply;
* whether archival is required.

---

# 22. Database Integrity Rule

Critical invariants should be protected at the appropriate database level.

Where applicable, use:

* foreign keys;
* unique constraints;
* check constraints;
* not-null constraints;
* transactions;
* indexes;
* appropriate isolation/concurrency controls.

Application validation alone must not be assumed sufficient for every critical invariant.

---

# 23. Migration Rule

Database schema changes must be performed through controlled migrations.

Developers must not manually alter shared database schemas and treat the manual change as the project source of truth.

Migrations must consider:

* existing data;
* upgrade path;
* rollback/recovery;
* compatibility;
* production scale;
* concurrent application versions.

---

# 24. Migration Safety Rule

Destructive schema changes require special review.

Prefer:

```text
Expand
   ↓
Migrate
   ↓
Adopt
   ↓
Contract
```

when compatibility requires it.

Dropping columns, tables, indexes, or data must never be treated as a routine refactor.

---

# 25. API Contract Rule

APIs are contracts.

Developers must not change API behavior casually.

Before changing an API, determine whether the change affects:

* clients;
* frontend;
* mobile or future clients;
* integrations;
* offline synchronization;
* tests;
* documentation.

Breaking changes require explicit handling.

---

# 26. API Validation Rule

API endpoints must validate:

* input shape;
* required fields;
* types;
* allowed values;
* authorization;
* tenant scope;
* branch scope;
* resource ownership;
* state transitions;
* business rules.

Client-side validation is supplementary.

---

# 27. API Error Rule

API errors must be predictable.

Errors should:

* use appropriate status semantics;
* provide stable application-level meaning where required;
* avoid leaking secrets or internal implementation details;
* allow clients to distinguish validation, authorization, conflict, and server failures.

Internal stack traces must not be exposed to ordinary clients.

---

# 28. Idempotency Rule

Operations that may be retried must have defined retry behavior.

This is particularly important for:

* payments;
* order submission;
* synchronization;
* background jobs;
* external integrations.

A repeated request must not accidentally create duplicate financial or operational effects.

---

# 29. Concurrency Rule

Developers must assume that two operations may happen concurrently.

Critical workflows must not rely on:

```text
read
↓
assume unchanged
↓
write
```

without considering concurrent modification.

Concurrency-sensitive areas include:

* inventory;
* cash registers;
* refunds;
* order state;
* synchronization;
* permissions;
* subscriptions.

---

# 30. Transaction Rule

Related state changes that must succeed or fail together must use an appropriate transaction boundary.

A transaction must not be unnecessarily broad.

Transactions must not be used as a substitute for understanding business consistency.

---

# 31. Offline Rule

Offline functionality must preserve the same business invariants as online operation wherever the architecture permits.

Offline data must not be treated as automatically trusted.

Synchronization must consider:

* authentication state;
* authorization scope;
* duplicate operations;
* ordering;
* retries;
* conflicts;
* idempotency;
* data integrity.

---

# 32. Synchronization Rule

Synchronization must never silently discard meaningful business data.

Conflict handling must be explicit.

A sync failure must be observable and recoverable.

The system must distinguish between:

```text
Not synchronized
Failed
Rejected
Applied
Conflict
```

when the business workflow requires those distinctions.

---

# 33. Frontend Authority Boundary

Frontend code may control:

* presentation;
* interaction;
* local state;
* optimistic UX where safe;
* client-side validation;
* navigation.

Frontend code must not be trusted to enforce:

* authorization;
* tenant isolation;
* branch isolation;
* financial correctness;
* inventory correctness;
* subscription enforcement.

---

# 34. Frontend State Rule

Do not duplicate server state unnecessarily.

State should have clear ownership.

Prefer:

```text
Server state
Local UI state
Form state
Derived state
```

over multiple competing copies of the same business state.

Derived values should not become independently editable state unless there is a deliberate reason.

---

# 35. Duplicate Submission Rule

User actions that can create duplicate effects must be protected.

Examples:

* submitting an order twice;
* paying twice;
* applying a refund twice;
* approving a recipe twice;
* submitting the same synchronization operation.

Use appropriate:

* idempotency;
* disabled states;
* request state;
* server-side protection;
* transaction logic.

---

# 36. Error Handling Rule

Errors must be handled deliberately.

Do not:

* silently swallow exceptions;
* return fake success;
* hide failed database writes;
* convert unexpected failures into successful business operations;
* log sensitive data to simplify debugging.

Errors should be:

1. detected;
2. classified;
3. logged appropriately;
4. exposed to the correct layer;
5. recovered or surfaced safely.

---

# 37. Logging Rule

Logs must provide useful diagnostic information without exposing sensitive data.

Do not log:

* passwords;
* authentication tokens;
* private keys;
* unnecessary personal data;
* sensitive customer information;
* production secrets.

Logs should contain sufficient context to investigate important failures.

---

# 38. Secret Handling Rule

Secrets must never be committed to source control.

Examples:

* API keys;
* database passwords;
* private keys;
* authentication secrets;
* production credentials.

Use approved environment/configuration/secret-management mechanisms.

Example files may contain placeholders, never real secrets.

---

# 39. Configuration Rule

Configuration must be explicit.

Do not hard-code environment-specific behavior into application logic when configuration is appropriate.

Avoid:

```text
if production:
    special hidden behavior
```

unless the behavior is deliberately defined and documented.

---

# 40. Feature Flag Rule

Feature flags must not become permanent undocumented architecture.

Every significant feature flag should have:

* purpose;
* owner;
* default behavior;
* applicable environments;
* rollout behavior;
* removal condition.

Security and authorization must not depend solely on frontend feature flags.

---

# 41. Dependency Rule

Dependencies must have a reason.

Before adding a dependency, consider:

* existing alternatives;
* security;
* maintenance;
* license;
* size;
* performance;
* compatibility;
* operational impact.

Unused dependencies must be removed.

Dependency upgrades must be controlled.

---

# 42. Third-Party Code Rule

Third-party code must not be trusted automatically.

Validate:

* source;
* version;
* integrity;
* security;
* compatibility;
* license requirements.

Downloaded scripts must not be executed blindly.

---

# 43. Formatting Rule

Code must follow repository formatting rules.

Developers should use automated formatting where available.

Formatting differences must not become a recurring review issue.

Large formatting changes should normally be separated from behavioral changes.

---

# 44. Linting Rule

Linting must be treated as an engineering signal.

Developers must not:

* disable linting globally to avoid failures;
* add broad ignores without justification;
* suppress warnings without understanding them.

Exceptions must be narrow and documented where necessary.

---

# 45. Testing Rule

Meaningful code changes require appropriate tests.

The required test level depends on risk.

Possible levels include:

```text
Unit
Domain
Application
Repository
API
Integration
End-to-End
Offline/Sync
Concurrency
Security
Performance
```

Not every change requires every level.

Critical workflows require stronger validation.

---

# 46. Test Quality Rule

A test must validate meaningful behavior.

Avoid tests that only prove:

* a function was called;
* a mock returned the expected value;
* code executed without exception;

when the actual business behavior is not validated.

Tests should fail when the relevant behavior is broken.

---

# 47. Test Isolation Rule

Tests must not depend unintentionally on:

* developer machine state;
* execution order;
* another test;
* external production services;
* previous local database state.

Tests should clean up or isolate mutable state appropriately.

---

# 48. Flaky Test Rule

Flaky tests must not be normalized.

A flaky test must be:

1. reproduced;
2. investigated;
3. classified;
4. fixed, isolated, or replaced.

Disabling a failing test requires explicit justification and follow-up.

---

# 49. Security Testing Rule

Security-sensitive changes require security validation.

Relevant areas include:

* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* file access;
* API access;
* session/device trust;
* sensitive operations;
* secrets;
* data exposure.

A feature is not considered complete if it works functionally but violates a security boundary.

---

# 50. Performance Rule

Performance optimization must not bypass correctness.

Do not:

* remove validation merely to improve speed;
* weaken transactions without understanding consistency;
* disable security checks;
* cache data across tenant boundaries;
* use stale financial or inventory state without an approved design.

Optimize based on evidence.

---

# 51. Caching Rule

Cached data must respect:

* tenant scope;
* branch scope;
* authorization;
* invalidation;
* freshness;
* consistency requirements.

Never use a shared cache key that can return one tenant's protected data to another tenant.

---

# 52. Background Job Rule

Background jobs must be:

* retry-aware;
* idempotent where required;
* observable;
* scoped to the correct tenant and branch;
* safe against duplicate execution.

A worker must not assume that the request context from which a job originated is still valid.

---

# 53. Scheduler Rule

Scheduled jobs must have:

* clear ownership;
* defined frequency;
* safe retry behavior;
* duplicate-execution protection where necessary;
* failure visibility.

A scheduler must not silently create duplicate financial or operational effects.

---

# 54. AI Development Rule

AI-generated code is untrusted until reviewed and validated.

Developers must verify:

* architecture;
* business behavior;
* security;
* data handling;
* performance;
* dependencies;
* tests;
* error handling.

AI output must never be merged solely because it looks plausible.

---

# 55. AI and Sensitive Data Rule

Do not provide AI tools with:

* production secrets;
* passwords;
* private keys;
* unnecessary personal data;
* confidential credentials;
* sensitive production database dumps.

Use sanitized or synthetic data when possible.

---

# 56. Git Rule

Every meaningful change must be traceable in Git.

Developers must not:

* commit secrets;
* commit generated temporary files unnecessarily;
* rewrite shared history casually;
* hide unrelated changes inside a feature branch;
* merge unreviewed work into protected branches.

---

# 57. Commit Rule

Commits should be:

* meaningful;
* focused;
* traceable;
* reviewable.

Avoid commits that combine unrelated:

* features;
* refactors;
* formatting migrations;
* dependency upgrades;
* documentation rewrites.

---

# 58. Pull Request Rule

A pull request must explain the change sufficiently for review.

Reviewers must be able to determine:

* what changed;
* why;
* affected areas;
* validation performed;
* risks;
* migration implications;
* security implications where relevant.

---

# 59. Review Rule

Code review must evaluate more than syntax.

Reviewers should consider:

```text
Correctness
Security
Architecture
Data integrity
Performance
Testing
Maintainability
Compatibility
Operational impact
Documentation
```

A reviewer must not approve code merely because tests pass.

---

# 60. Change Scope Rule

A change should remain within its intended scope.

If implementation reveals an unrelated issue:

* document it;
* create a separate task/change when appropriate;
* avoid silently expanding the current change.

Exceptions are appropriate when leaving the issue unresolved would make the current change unsafe or incorrect.

---

# 61. Refactoring Rule

Refactoring must preserve behavior unless a behavior change is explicitly intended.

Prefer:

```text
Refactor
   ↓
Tests remain valid
   ↓
Behavior remains stable
```

over combining hidden behavior changes with structural cleanup.

---

# 62. Technical Debt Rule

Technical debt must be visible.

Do not hide shortcuts as permanent architecture.

If a temporary implementation is required, define:

* why;
* limitation;
* risk;
* intended replacement;
* ownership where appropriate.

---

# 63. Debugging Rule

When a test or application fails, investigate the root cause.

Do not:

* suppress the error;
* weaken the test without reason;
* add arbitrary retries;
* ignore the failure;
* change unrelated code until the test passes.

The objective is to understand the failure.

---

# 64. Data Migration Rule

Data migrations must preserve business meaning.

Before transforming existing data, determine:

* old meaning;
* new meaning;
* mapping;
* invalid cases;
* rollback/recovery;
* verification.

Never assume that a syntactically valid migration is semantically correct.

---

# 65. Import/Export Rule

Import and export functionality must respect:

* authorization;
* tenant scope;
* branch scope;
* validation;
* duplicate handling;
* error reporting;
* data integrity.

Imported data must not bypass normal business invariants.

Exports must not expose data outside the requester's scope.

---

# 66. File Handling Rule

Uploaded files must be treated as untrusted input.

Validate:

* type;
* size;
* name;
* storage location;
* access permissions.

Do not trust client-provided file metadata.

Protected files must be accessed through authorized application paths.

---

# 67. Subscription Rule

Subscription restrictions must be enforced server-side.

When functionality is blocked due to subscription state:

* blocked operations must actually be denied;
* permitted data access must remain consistent with the business rule;
* developers must not bypass restrictions through alternative APIs or direct UI routes.

Subscription behavior must remain consistent across clients and background operations.

---

# 68. Offline New-Device Rule

Offline operation must not become a mechanism for bypassing device or authentication controls.

A device that has not been appropriately trusted or authorized must not gain unrestricted offline access simply because network connectivity is unavailable.

---

# 69. Branch Device Rule

Device-specific protections must not rely solely on client-side identifiers.

Trusted-device behavior must be validated according to the approved security model.

---

# 70. Financial and Inventory Auditability Rule

Changes to financially or operationally significant records must remain explainable.

Where required, preserve:

* actor;
* time;
* affected resource;
* old state;
* new state;
* reason;
* approval;
* related operation.

Do not remove audit information merely to simplify implementation.

---

# 71. Notification Rule

Notifications must represent meaningful business events.

Do not create excessive notifications merely because a technical event occurred.

Examples of meaningful events include:

* subscription ending;
* large refund;
* cash shortage;
* significant inventory variance;
* salary due;
* branch loss;
* important approval requirement.

Routine internal implementation details should not automatically become owner-facing notifications.

---

# 72. UI State Rule

Important frontend states must be explicit.

At minimum, relevant screens should correctly handle:

```text
Loading
Empty
Success
Validation error
Authorization failure
Business conflict
Network failure
Unexpected failure
```

A blank screen must not be used as an implicit error state.

---

# 73. Accessibility and Usability Rule

User interfaces should remain usable for supported users and workflows.

Do not sacrifice critical usability for visual complexity.

Important actions should be understandable.

Destructive operations must be distinguishable from routine operations.

---

# 74. Documentation Consistency Rule

When implementation changes an established behavior, affected documentation must be reviewed.

Do not allow:

```text
Documentation → behavior A
Implementation → behavior B
```

to persist silently.

If the behavior is intentionally changed, update the appropriate source of truth.

---

# 75. ADR Rule

Architecture-significant decisions require ADR consideration.

Examples include decisions affecting:

* system boundaries;
* data ownership;
* infrastructure;
* major technology choices;
* synchronization architecture;
* security architecture;
* scaling model;
* significant API strategy.

Do not hide architecture decisions inside ordinary implementation commits.

---

# 76. Tooling Rule

Developer tools must:

* be reproducible;
* fail visibly;
* protect destructive operations;
* avoid unnecessary production access;
* respect repository architecture;
* have clear ownership;
* remain maintainable.

Tooling must not silently modify unrelated project state.

---

# 77. Local Environment Rule

Local development must remain isolated from production.

Developers must not use production data or credentials as ordinary local development dependencies.

Development environments should use:

* local resources;
* synthetic data;
* sanitized data where explicitly approved.

---

# 78. Production Data Rule

Production data must not be copied into local environments casually.

If production-derived data is ever required for diagnosis, it must follow approved security and privacy controls.

Sensitive information should be minimized or sanitized.

---

# 79. Environment Parity Rule

Local development does not need to be identical to production.

However, differences that can affect correctness must be understood.

Examples include:

* database versions;
* cache behavior;
* queue behavior;
* authentication;
* network behavior;
* filesystem behavior.

---

# 80. Dependency and Environment Reproducibility

A new developer should be able to establish a valid development environment using documented project instructions.

Environment setup must not depend on undocumented personal machine configuration.

---

# 81. No Hidden Global State

Application behavior must not depend on undocumented global state such as:

* developer-specific files;
* arbitrary environment variables;
* global packages;
* manual database changes;
* hidden services;
* personal configuration.

If a dependency is required, document and automate it where practical.

---

# 82. No Silent Fallbacks

Fallback behavior must be deliberate.

Avoid:

```text
database unavailable → silently use fake data
authorization failed → silently allow operation
payment failed → report success
configuration missing → use insecure default
```

A safe failure is better than an incorrect success.

---

# 83. Default-Secure Rule

When a protected capability is ambiguous or unavailable, default toward the safer behavior.

Examples:

```text
Unknown permission → deny
Unknown tenant → reject
Invalid token → reject
Unknown branch scope → reject
Invalid subscription state → block protected action
```

Exceptions require explicit business design.

---

# 84. No Security by Obscurity

Do not rely on:

* hidden URLs;
* random identifiers;
* frontend-only hidden buttons;
* undocumented endpoints;
* obscure parameter names.

Protected resources require actual authorization.

---

# 85. No Direct Database Bypass

Application code must not introduce ad-hoc database access that bypasses:

* authorization;
* business rules;
* audit requirements;
* transaction boundaries;
* domain invariants.

Administrative or migration tooling may access data directly only within its explicitly defined responsibility.

---

# 86. No Untracked Schema Changes

Developers must not rely on manual schema modifications that are absent from migrations.

A clean environment must be able to reproduce the expected schema.

---

# 87. No Unreviewed Production Behavior

Changes affecting production behavior must pass the required review and validation process.

Local success is not production readiness.

---

# 88. Release Readiness Rule

Before release, the change must have:

* approved implementation;
* appropriate tests;
* required migrations;
* required documentation;
* security validation where relevant;
* compatibility review;
* deployment considerations;
* rollback/recovery considerations.

---

# 89. Rollback Rule

Changes must have a reasonable recovery strategy.

The appropriate strategy may be:

* code rollback;
* configuration rollback;
* feature disablement;
* migration recovery;
* compensating operation;
* forward fix.

Rollback must not be assumed to mean simply reversing a Git commit.

---

# 90. Emergency Change Rule

Emergency changes may reduce normal process overhead but must not intentionally bypass:

* security;
* data integrity;
* tenant isolation;
* financial correctness.

After an emergency change:

1. record what happened;
2. validate the change;
3. document the reason;
4. perform required follow-up review;
5. update architecture/documentation if necessary.

---

# 91. Quality Over Convenience

The easiest implementation is not automatically the correct implementation.

Developers must reject shortcuts that create:

* security vulnerabilities;
* data corruption;
* architectural coupling;
* hidden business behavior;
* difficult migrations;
* unreliable tests;
* unmaintainable code.

---

# 92. Simplicity Rule

Prefer the simplest design that satisfies:

* business requirements;
* architecture;
* security;
* reliability;
* performance;
* maintainability.

Do not introduce:

* microservices without a real need;
* abstraction layers without responsibility;
* complex caching without evidence;
* generic frameworks for one use case;
* unnecessary asynchronous processing.

---

# 93. Abstraction Rule

Abstractions should represent stable concepts.

Do not create abstractions merely to avoid writing a few lines of code.

A useful abstraction should reduce meaningful duplication or isolate a real boundary.

---

# 94. Duplication Rule

Not all duplication must be removed immediately.

Prefer intentional duplication over a premature abstraction that couples unrelated domains.

Refactor when the duplicated behavior represents a genuinely shared responsibility.

---

# 95. Naming Rule

Names must reflect domain meaning.

Avoid ambiguous names such as:

```text
data
item
process
thing
manager
helper
utils
temp
```

when more precise domain terminology exists.

Naming must remain consistent with approved domain terminology.

---

# 96. Comments Rule

Comments should explain **why**, not merely repeat **what** the code does.

Useful comments explain:

* non-obvious business reasoning;
* compatibility requirements;
* unusual constraints;
* important security decisions;
* temporary workarounds.

Comments must not contradict current behavior.

---

# 97. Dead Code Rule

Unused code must not remain indefinitely.

Remove:

* obsolete feature implementations;
* unused configuration;
* unused dependencies;
* unreachable branches;
* obsolete feature flags;
* dead scripts.

If code must remain temporarily, its lifecycle should be understood.

---

# 98. Experimental Code Rule

Experimental code must be clearly isolated from production paths.

Do not allow experiments to become accidental production dependencies.

Experiments should have:

* clear purpose;
* limited scope;
* known cleanup path.

---

# 99. Generated Code Rule

Generated code must have an identifiable source and generation process.

Do not manually modify generated output if regeneration will overwrite the changes.

---

# 100. Quality Gate

A meaningful change is not complete until all applicable gates pass:

```text
Requirements understood
        ↓
Documentation/design aligned
        ↓
Implementation complete
        ↓
Security considered
        ↓
Tests pass
        ↓
Static checks pass
        ↓
Review complete
        ↓
Documentation updated
        ↓
Release impact understood
```

Not every change requires every gate at equal depth, but no applicable gate may be silently skipped.

---

# 101. Definition of Done

A development change is considered complete only when:

* intended behavior is implemented;
* unintended behavior is not introduced;
* required documentation is aligned;
* security boundaries are preserved;
* data integrity is preserved;
* appropriate tests pass;
* code quality checks pass;
* required review is complete;
* migration impact is understood;
* configuration impact is understood;
* operational impact is understood;
* unresolved risks are documented.

---

# 102. Developer Quality Checklist

Before considering a change complete:

### Requirements

* [ ] Requirement is understood.
* [ ] Existing documentation was checked.
* [ ] No undocumented business assumption was introduced.

### Architecture

* [ ] Architecture boundaries are respected.
* [ ] No unnecessary coupling was introduced.
* [ ] Architecture-significant decisions were documented.

### Security

* [ ] Authentication is appropriate.
* [ ] Authorization is server-side.
* [ ] Tenant scope is enforced.
* [ ] Branch scope is enforced.
* [ ] Sensitive data is protected.
* [ ] No secrets are committed.

### Data

* [ ] Database invariants are preserved.
* [ ] Migrations are controlled.
* [ ] Historical data remains meaningful.
* [ ] Financial data remains correct.
* [ ] Inventory remains correct.

### API

* [ ] Contract remains compatible or change is explicitly handled.
* [ ] Validation is complete.
* [ ] Errors are predictable.
* [ ] Retry/idempotency behavior is understood.

### Frontend

* [ ] UI reflects actual server state.
* [ ] Important states are handled.
* [ ] Duplicate actions are protected.
* [ ] Authorization is not delegated to UI.

### Testing

* [ ] Appropriate tests exist.
* [ ] Critical workflows are validated.
* [ ] Tests are isolated.
* [ ] No failures are hidden.

### Tooling

* [ ] Formatting passes.
* [ ] Linting passes.
* [ ] Static checks pass.
* [ ] Developer automation behaves correctly.

### Documentation

* [ ] Relevant documentation is updated.
* [ ] ADRs are updated or created when required.
* [ ] No conflicting source of truth remains.

### Release

* [ ] Deployment impact is understood.
* [ ] Recovery strategy is understood.
* [ ] Configuration impact is understood.
* [ ] Operational impact is understood.

---

# 103. Reviewer's Guardrail Checklist

Reviewers should ask:

1. Does the implementation match the documented requirement?
2. Does it respect architecture boundaries?
3. Can another tenant access this data?
4. Can another branch access this data?
5. Can the client bypass the intended rule?
6. Can the operation execute twice incorrectly?
7. What happens if the database operation partially fails?
8. What happens during concurrent execution?
9. What happens offline?
10. What happens during synchronization?
11. What happens when subscription access is blocked?
12. What happens when a dependency is unavailable?
13. What happens when the user lacks permission?
14. What happens when input is malformed?
15. What happens when a background job retries?
16. What happens when the operation fails halfway through?
17. Is historical data still meaningful?
18. Are financial and inventory invariants preserved?
19. Are tests proving the actual business behavior?
20. Is the implementation more complex than necessary?

---

# 104. Guardrail Exceptions

Exceptions are allowed only when there is a legitimate engineering reason.

An exception should identify:

* rule being violated;
* reason;
* affected scope;
* risk;
* mitigation;
* duration if temporary;
* approval where required.

Temporary exceptions must not become permanent simply because they were forgotten.

---

# 105. Guardrail Enforcement

Guardrails should be enforced at the strongest practical level.

Possible enforcement mechanisms include:

```text
Documentation
   ↓
Code review
   ↓
Automated linting
   ↓
Static analysis
   ↓
Tests
   ↓
CI checks
   ↓
Database constraints
   ↓
Runtime authorization
```

The most important invariants should not depend solely on developer discipline.

---

# 106. Relationship to Other Development Documents

This document is the final guardrail layer for `docs/13_Development`.

It complements:

* `01_Development_Architecture_Overview.md`
* `02_Repository_Structure_and_Conventions.md`
* `03_Git_Branching_and_Version_Control_Strategy.md`
* `04_Commit_Message_and_Change_Standards.md`
* `05_Pull_Request_and_Code_Review_Process.md`
* `06_Backend_Development_Standards.md`
* `07_Frontend_Development_Standards.md`
* `08_Database_Development_and_Migration_Workflow.md`
* `09_API_Development_and_Contract_Change_Workflow.md`
* `10_Documentation_First_Development_Workflow.md`
* `11_ADR_and_Architecture_Decision_Workflow.md`
* `12_Local_Development_Environment.md`
* `13_Testing_and_Debugging_Workflow.md`
* `14_Dependency_and_Package_Management.md`
* `15_Configuration_and_Feature_Flag_Development.md`
* `16_AI_Assisted_Development_Guidelines.md`
* `17_Developer_Tooling_and_Automation.md`

It also depends conceptually on:

* `docs/01_Business_Analysis`
* `docs/02_System_Analysis`
* `docs/03_Domain_Analysis`
* `docs/04_Architecture`
* `docs/05_Database`
* `docs/06_Backend`
* `docs/07_Frontend`
* `docs/08_AI`
* `docs/09_API`
* `docs/10_Deployment`
* `docs/11_Security`
* `docs/12_Testing`
* `docs/14_Operations`
* `docs/15_Future`

This document does not replace those sections.

It establishes the development guardrails that ensure implementation remains consistent with them.

---

# 107. Development Guardrail Invariants

The following invariants are mandatory unless explicitly superseded by an accepted decision.

1. No unapproved business rule may be introduced.
2. Existing accepted documentation must be checked before meaningful implementation changes.
3. Important behavior must have a clear source of truth.
4. Architecture boundaries must not be bypassed for convenience.
5. Backend authorization is authoritative.
6. Tenant isolation is mandatory.
7. Branch isolation is mandatory where branch scope applies.
8. Authentication and authorization must remain separate.
9. Sensitive operations require appropriate authorization.
10. Financial calculations must preserve monetary correctness.
11. Inventory must not silently become negative.
12. Recipe lifecycle rules must not be bypassed.
13. Historical records must remain meaningful.
14. Permanent deletion must be deliberate.
15. Critical database invariants must be protected at the appropriate level.
16. Schema changes must use controlled migrations.
17. Destructive migrations require special handling.
18. APIs are contracts and must evolve deliberately.
19. API validation must be server-side.
20. Retry-sensitive operations must have defined idempotency behavior.
21. Concurrency must be considered for shared state.
22. Related atomic operations must use appropriate transaction boundaries.
23. Offline workflows must preserve applicable business invariants.
24. Synchronization must not silently discard meaningful data.
25. Frontend behavior must not be treated as a security boundary.
26. Duplicate business effects must be prevented.
27. Errors must not be silently swallowed.
28. Sensitive information must not be unnecessarily logged.
29. Secrets must never be committed.
30. Configuration must remain explicit and reproducible.
31. Feature flags must not bypass security.
32. Dependencies must have a justified purpose.
33. Third-party code must be treated as untrusted until reviewed.
34. Formatting must remain deterministic.
35. Linting must remain actionable.
36. Meaningful changes require appropriate tests.
37. Tests must validate behavior rather than implementation details alone.
38. Tests must remain isolated and reproducible.
39. Flaky tests must be investigated.
40. Security-sensitive changes require security validation.
41. Performance optimizations must not weaken correctness or security.
42. Caches must respect tenant and branch boundaries.
43. Background jobs must be retry-safe where necessary.
44. Scheduled jobs must prevent harmful duplicate effects.
45. AI-generated code must be reviewed and validated.
46. AI tools must not receive unnecessary secrets or sensitive production data.
47. Git history must remain traceable.
48. Commits must remain meaningful and reviewable.
49. Pull requests must provide sufficient change context.
50. Code review must evaluate correctness, security, architecture, and maintainability.
51. Changes should remain within intended scope.
52. Refactoring must not silently change behavior.
53. Technical debt must remain visible.
54. Debugging must target root causes.
55. Data migrations must preserve business meaning.
56. Imports and exports must respect authorization and data boundaries.
57. Uploaded files must be treated as untrusted input.
58. Subscription restrictions must be enforced server-side.
59. Offline operation must not bypass device or authentication controls.
60. Financial and inventory changes must remain explainable.
61. Notifications must represent meaningful business events.
62. Important frontend states must be explicit.
63. Documentation must remain consistent with implementation.
64. Architecture-significant decisions must be recorded appropriately.
65. Developer tooling must fail visibly and safely.
66. Local environments must remain isolated from production.
67. Production data must not be used casually in development.
68. Hidden global state must not determine application correctness.
69. Missing or invalid security information must fail safely.
70. Security must not rely on obscurity.
71. Direct database bypasses must not circumvent business rules.
72. Schema changes must not depend on untracked manual modifications.
73. Production behavior must not be released without appropriate validation.
74. Every meaningful change must have a recovery strategy appropriate to its risk.
75. Emergency changes require follow-up documentation and validation.
76. Convenience must not override correctness.
77. Complexity must have a justified purpose.
78. Abstractions must represent meaningful boundaries.
79. Domain terminology must remain consistent.
80. Dead code and obsolete configuration must not accumulate indefinitely.
81. Experimental code must remain isolated.
82. Generated code must have a known source.
83. Quality gates must not be silently skipped.
84. Completion requires both implementation and validation.
85. Guardrail exceptions must be explicit.
86. Important guardrails should be enforced automatically where practical.
87. Development quality is a system responsibility, not only an individual responsibility.

---

# 108. Final Principle

Development guardrails exist to prevent locally convenient decisions from becoming system-wide defects.

The project should allow developers to move quickly **inside safe boundaries**, while making it difficult to accidentally violate business correctness, security, data integrity, architecture, or operational reliability.

The governing principle is:

> **Build only what is understood, enforce critical rules at the correct boundary, validate meaningful behavior, preserve data and security invariants, and never use convenience as a reason to weaken system correctness.**

