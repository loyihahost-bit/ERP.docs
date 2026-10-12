# 04. Commit Message and Change Standards

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the commit message and change standards for the FastFood ERP project.

It establishes how developers should:

* structure Git commits;
* describe changes clearly;
* keep commits focused and reviewable;
* connect implementation changes to requirements, decisions, tests, and releases;
* identify high-risk changes;
* document breaking changes;
* handle migrations and other operationally significant changes;
* preserve a reliable project history.

The goal is not merely to create readable Git history.

The goal is to make every meaningful code change understandable, traceable, reviewable, testable, and recoverable.

---

## 2. Scope

These standards apply to all project changes committed to the repository, including:

* backend changes;
* frontend changes;
* database changes;
* API changes;
* infrastructure changes;
* configuration changes;
* security changes;
* AI-related changes;
* tests;
* documentation;
* scripts and developer tooling;
* dependency changes;
* deployment-related changes;
* bug fixes;
* refactoring;
* performance changes.

They apply regardless of whether the change is written manually or with AI-assisted development.

---

## 3. Core Principles

The project follows these commit principles:

1. Every meaningful change must have a clear purpose.
2. A commit should represent one logical change whenever practical.
3. Commit messages must explain what changed and why.
4. Commits must be understandable without inspecting every changed line.
5. Large unrelated changes must not be combined into one commit.
6. Commit history must support change tracing.
7. High-risk changes require stronger traceability.
8. Tests must accompany behavior changes whenever applicable.
9. Documentation must accompany changes that affect documented behavior or architecture.
10. Architecture decisions must be recorded through ADRs when required.
11. Database changes must remain traceable to their migrations.
12. API contract changes must remain traceable to the affected contract and tests.
13. Security-sensitive changes must identify their security impact.
14. Financial and inventory behavior changes require explicit verification.
15. Breaking changes must never be hidden inside generic commit messages.
16. Commit messages must describe project behavior, not personal activity.
17. Commit history must remain useful for future debugging and maintenance.
18. Generated files must not obscure the actual source change.
19. Reverts must clearly identify the change being reverted.
20. The final repository history must provide enough evidence to understand how the system evolved.

---

# 4. Commit Message Standard

## 4.1 Required Structure

Commits should follow this structure:

```text
<type>(<scope>): <short description>

<body>

<footer>
```

The body and footer are optional for simple changes.

The first line is required.

Example:

```text
fix(inventory): prevent negative stock after concurrent deduction
```

Example with additional context:

```text
fix(inventory): prevent negative stock after concurrent deduction

Stock deduction now validates the current available quantity
inside the protected transaction boundary.

This prevents two concurrent orders from consuming the same
inventory quantity.

Refs: INV-042
Tests: inventory/concurrent_deduction
```

---

# 5. Commit Types

The following commit types are standard.

## 5.1 `feat`

Used when introducing new functionality.

```text
feat(menu): add branch-specific menu activation
```

---

## 5.2 `fix`

Used when correcting incorrect existing behavior.

```text
fix(pos): prevent duplicate order submission
```

---

## 5.3 `refactor`

Used when changing internal structure without intentionally changing externally observable behavior.

```text
refactor(order): separate order validation from persistence
```

A refactor must not be used to hide behavior changes.

If behavior changes, the commit must be classified accordingly.

---

## 5.4 `perf`

Used for performance improvements where behavior should remain equivalent.

```text
perf(reporting): reduce branch report query count
```

Performance claims should be supported by appropriate measurements or tests when meaningful.

---

## 5.5 `test`

Used when adding or improving tests without changing production behavior.

```text
test(cash): add register handover consistency cases
```

If a test is added together with a production bug fix, it is normally preferable to keep the fix and its directly related regression test together.

---

## 5.6 `docs`

Used for documentation-only changes.

```text
docs(security): clarify branch permission boundaries
```

---

## 5.7 `build`

Used for build-system or dependency-related changes.

```text
build(backend): update Python dependency lock file
```

---

## 5.8 `ci`

Used for continuous integration changes.

```text
ci(testing): add migration verification to quality gate
```

---

## 5.9 `chore`

Used for maintenance changes that do not represent product behavior.

```text
chore(repo): remove obsolete development script
```

---

## 5.10 `revert`

Used when intentionally reverting a previous change.

```text
revert(inventory): revert stock reservation change
```

The commit body should identify the reverted commit and explain why the reversal is necessary.

---

# 6. Commit Scope

The scope identifies the primary area affected by the commit.

Typical scopes may include:

```text
auth
security
tenant
branch
employee
permission
pos
order
payment
cash
inventory
recipe
menu
pricing
report
payroll
attendance
subscription
offline
sync
api
frontend
backend
database
migration
ai
deployment
testing
docs
config
```

Scopes are not an unlimited fixed vocabulary.

A new scope may be introduced when an existing scope does not accurately describe the change.

The scope must represent the primary responsibility affected by the commit.

Avoid meaningless scopes such as:

```text
misc
stuff
changes
work
code
update
```

---

# 7. Commit Subject Rules

The subject line should:

* be concise;
* describe the actual change;
* use imperative-style wording;
* avoid unnecessary punctuation;
* avoid vague descriptions;
* avoid personal activity descriptions.

Prefer:

```text
fix(cash): limit register correction attempts
```

Avoid:

```text
fixed some cash issue
```

Prefer:

```text
feat(recipe): add semi-finished product dependencies
```

Avoid:

```text
added recipe stuff
```

Prefer:

```text
docs(development): define commit traceability rules
```

Avoid:

```text
updated docs
```

---

# 8. The Commit Body

The body should be used when the subject alone does not adequately explain the change.

It should answer relevant questions such as:

* What problem existed?
* Why was the change necessary?
* What behavior changed?
* What important constraints apply?
* What compatibility implications exist?
* What operational consequences exist?

Example:

```text
fix(cash): require confirmation after register handover

The incoming cashier must confirm the counted cash before the
handover can become final.

This prevents an unconfirmed handover from being treated as
completed by the reporting layer.

Tests: cash/handover_confirmation
```

The body should explain reasoning rather than repeat the subject.

---

# 9. Atomic Commits

A commit should represent one coherent logical change.

An atomic commit may contain multiple files when those files are required for the same change.

For example, the following can belong to one commit:

```text
backend/
frontend/
tests/
docs/
```

if they collectively implement and verify one logical behavior change.

Atomic does not mean "one file per commit."

Atomic means:

> The commit represents one understandable unit of change.

---

# 10. Avoid Unrelated Changes

Do not combine unrelated work merely because it happens to be modified at the same time.

Avoid:

```text
feat(order): add delivery status

- change delivery status
- reformat unrelated backend files
- rename unrelated variables
- update unrelated documentation
- modify CI configuration
```

Separate unrelated changes into appropriate commits.

This improves:

* review quality;
* debugging;
* reverting;
* cherry-picking;
* release analysis;
* historical understanding.

---

# 11. Implementation and Test Changes

When a production behavior changes, the related test should normally be included in the same logical change.

Example:

```text
fix(inventory): block deduction when stock is insufficient
```

The same commit may contain:

```text
production implementation
+
regression test
```

This creates a direct relationship between the behavior and its verification.

Tests should not be separated merely to make commit statistics look cleaner.

---

# 12. Documentation Traceability

Changes affecting documented behavior must keep documentation synchronized.

For example, if a change modifies:

* permission behavior;
* subscription behavior;
* offline behavior;
* recipe rules;
* cash correction rules;
* branch isolation;
* API behavior;
* deployment behavior;

the relevant documentation must be reviewed.

The commit may reference the documentation or architecture decision:

```text
fix(permission): enforce branch-specific manager scope

Refs: SEC-08
Docs: 11_Security/08_Authorization_and_Permission_Model.md
Tests: auth/branch_scope
```

The exact reference identifiers should match the project's actual tracking system.

---

# 13. Requirement Traceability

Meaningful product changes should be traceable through the development lifecycle.

The preferred relationship is:

```text
Requirement
    ↓
Analysis
    ↓
Architecture / ADR
    ↓
Implementation Commit
    ↓
Tests
    ↓
Pull Request
    ↓
Release
```

A commit does not need to repeat the entire requirement.

It should provide enough references to connect the change to the relevant project artifacts.

---

# 14. Issue and Requirement References

Where the project uses issue or requirement identifiers, commits should reference them.

Example:

```text
feat(order): add phone delivery order type

Refs: ORD-021
```

For a completed requirement:

```text
feat(subscription): enforce expired feature restrictions

Closes: SUB-014
```

References must use the actual project identifier.

Do not invent identifiers merely to make a commit appear traceable.

---

# 15. ADR References

Architecture-significant changes should reference the relevant ADR.

Example:

```text
refactor(auth): move authorization evaluation to application boundary

Refs: ADR-014
```

If an existing ADR no longer represents the current architecture, the architecture decision process must be followed rather than silently changing the implementation.

---

# 16. Breaking Changes

Breaking changes must be explicitly identified.

Example:

```text
feat(api)!: replace legacy order status representation

BREAKING CHANGE:
The previous numeric order status values are no longer accepted
by the API.

Migration guidance is documented in the API contract documentation.
```

The breaking change must not be hidden inside a generic:

```text
fix(api): update order status
```

Breaking changes may include:

* API contract changes;
* database compatibility changes;
* permission behavior changes;
* configuration changes;
* authentication behavior changes;
* synchronization protocol changes;
* frontend/backend contract changes;
* deployment requirements;
* external integration changes.

---

# 17. Database and Migration Changes

Database changes require additional traceability.

A database-related commit should identify the migration impact where useful.

Example:

```text
feat(inventory): add stock movement source tracking

The stock movement model now records whether inventory was bought
ready or prepared inside a branch.

Refs: INV-031
Migration: 0042_add_stock_source
Tests: inventory/stock_source
```

Migration files must remain synchronized with the application behavior they support.

Do not modify an already-applied production migration merely to make its contents look cleaner.

Create a new migration when the deployed schema must change.

---

# 18. API Changes

API changes require special attention because clients may depend on the existing contract.

Examples of significant API changes include:

* adding required fields;
* removing fields;
* changing field meaning;
* changing validation;
* changing authorization;
* changing response structures;
* changing status codes;
* changing pagination behavior;
* changing synchronization contracts.

Example:

```text
feat(api): add branch scope to employee report endpoint

The endpoint now requires an explicit branch scope for users
without all-branch reporting permission.

Refs: REP-018
Tests: api/employee_report_scope
```

Breaking API changes must explicitly use the breaking-change mechanism.

---

# 19. Security-Sensitive Changes

Security changes require clear identification.

Examples include:

* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* session handling;
* trusted devices;
* offline authentication;
* encryption;
* secrets;
* audit logging;
* file access;
* privileged operations.

Example:

```text
fix(security): reject cross-branch resource access

Resource authorization now validates the requested branch against
the authenticated user's effective branch scope.

Refs: SEC-017
Tests: security/cross_branch_access
```

Security behavior must never rely only on frontend restrictions.

---

# 20. Financial Changes

Financial and cash-related commits require additional care.

Examples include:

* payment calculation;
* discounts;
* refunds;
* cash register opening;
* cash register closing;
* handover;
* shortage handling;
* correction limits;
* payroll;
* financial reporting.

Example:

```text
fix(cash): enforce maximum register correction attempts

Register corrections are limited to the defined correction count.
After the limit is reached, the normal correction path is blocked.

Refs: CASH-009
Tests: cash/correction_limit
```

Financial changes should include relevant test evidence.

---

# 21. Inventory and Recipe Changes

Inventory and recipe changes may affect stock correctness and business operations.

Examples include:

* stock deduction;
* FIFO behavior;
* stock adjustment;
* recipe versions;
* semi-finished products;
* ingredient dependencies;
* yield loss;
* shopping calculations;
* insufficient stock handling.

Example:

```text
fix(inventory): prevent negative stock during concurrent orders

Inventory deduction now protects the quantity validation and
deduction as one consistency boundary.

Refs: INV-044
Tests: inventory/concurrent_orders
```

A commit must not introduce negative stock behavior unless an explicitly approved business rule changes the existing policy.

---

# 22. Offline and Synchronization Changes

Offline behavior requires explicit traceability because local and server state may temporarily diverge.

Example:

```text
fix(sync): preserve transaction identity during retry

Retries now reuse the same client transaction identifier so that
the server can recognize duplicate submissions.

Refs: OFF-012
Tests: sync/retry_idempotency
```

Changes affecting:

* idempotency;
* transaction identity;
* conflict resolution;
* synchronization ordering;
* offline permissions;
* local state;
* retry behavior;

must receive appropriate testing and review.

---

# 23. Configuration Changes

Configuration changes should clearly identify their operational impact.

Example:

```text
chore(config): add explicit worker concurrency setting
```

If configuration changes alter security, performance, financial behavior, or deployment requirements, the commit should state the impact.

---

# 24. Dependency Changes

Dependency updates should explain why they are required when the reason is not obvious.

Example:

```text
build(backend): upgrade ORM dependency for security patch

The dependency update addresses the approved security advisory
without changing the application data model.

Tests: backend/integration
```

Avoid grouping unrelated dependency upgrades with feature work unless there is a clear reason.

---

# 25. AI-Assisted Development

AI-assisted changes follow the same commit standards as manually written changes.

The developer remains responsible for:

* understanding the change;
* validating correctness;
* checking security implications;
* checking architectural consistency;
* running appropriate tests;
* reviewing generated code;
* confirming documentation consistency.

Do not use commit messages such as:

```text
ai generated code
```

or:

```text
copilot changes
```

AI tool usage is not the purpose of the change.

The commit must describe the actual engineering change.

---

# 26. Generated Files

Generated files should not obscure the source change.

When generated output is intentionally committed, the commit should make the relationship clear.

Example:

```text
build(frontend): regenerate production asset manifest
```

Do not commit:

* temporary debugging output;
* local caches;
* editor metadata;
* secrets;
* local environment files;
* generated artifacts that are explicitly excluded by repository policy.

---

# 27. Formatting-Only Changes

Formatting-only changes should be isolated when they are large enough to interfere with functional review.

Example:

```text
chore(backend): apply formatter to service modules
```

Avoid combining large formatting changes with complex behavioral changes.

This allows reviewers to distinguish:

```text
actual behavior change
```

from:

```text
mechanical formatting
```

---

# 28. Refactoring Standards

Refactoring commits should preserve behavior unless the behavior change is explicitly part of the commit.

Prefer:

```text
refactor(order): extract order validation service
```

Avoid:

```text
refactor(order): improve order system
```

If a refactor also changes behavior, the commit should either:

1. separate the behavioral change into another commit; or
2. clearly describe the behavior change.

---

# 29. Revert Standards

A revert must be explicit.

Example:

```text
revert(sync): revert transaction retry optimization
```

Body:

```text
This reverts commit <commit-id> because the optimization causes
duplicate synchronization under offline retry conditions.

The original implementation will remain until the synchronization
behavior is corrected and retested.
```

A revert is a deliberate engineering change and must be reviewed accordingly.

---

# 30. Amend and Reword

Before a commit is shared through the collaborative workflow, developers may clean up:

* incorrect messages;
* accidental temporary commits;
* incomplete descriptions;
* unnecessary commit fragmentation.

Once history is shared and relied upon, rewriting it must follow the project's Git workflow and repository protection rules.

Do not rewrite shared history merely to make the history look aesthetically cleaner.

---

# 31. Commit Granularity

Commits should be large enough to represent meaningful work but small enough to remain understandable.

Avoid both extremes.

### Too small

```text
add variable
fix typo
rename function
add import
add test
```

when all belong to one logical change.

### Too large

```text
implement entire restaurant system
```

containing unrelated functionality.

A useful commit normally represents one reviewable engineering decision or one coherent implementation step.

---

# 32. Commit Quality Criteria

A high-quality commit should allow another developer to answer:

1. What changed?
2. Where did it change?
3. Why was it changed?
4. What business or technical behavior is affected?
5. What requirements or decisions does it relate to?
6. Was the change tested?
7. Does it introduce compatibility or migration concerns?
8. Does it require documentation updates?
9. Does it introduce security, financial, inventory, or synchronization risk?

Not every simple commit needs to explicitly answer all nine questions in its message.

The repository history as a whole must make these relationships recoverable.

---

# 33. Commit Traceability Metadata

Where useful, commits may use structured footer fields such as:

```text
Refs: ORD-021
Closes: ORD-021
Tests: order/creation
Docs: 06_Backend/...
ADR: ADR-014
Migration: 0042_add_stock_source
```

Only metadata that is actually meaningful should be included.

Do not add artificial metadata simply to make a commit appear more formal.

---

# 34. Change Risk Indicators

Commit messages should make significant risk visible.

Higher-risk changes commonly include:

* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* cash;
* payment;
* refunds;
* payroll;
* inventory;
* recipes;
* offline synchronization;
* database migrations;
* API contracts;
* subscription enforcement;
* security controls;
* deployment behavior;
* backup or recovery behavior.

For these changes, the commit should provide enough context for reviewers to identify the affected boundary.

Example:

```text
fix(subscription): enforce feature restrictions after expiry

Expired subscriptions can no longer access restricted operations,
while permitted historical data remains viewable.

Refs: SUB-022
Tests: subscription/expired_access
Docs: 11_Security/...
```

---

# 35. Commit and Release Traceability

Important changes must remain traceable from implementation to release.

The expected chain is:

```text
Requirement
    ↓
Issue / Analysis Reference
    ↓
Commit
    ↓
Pull Request
    ↓
Test Evidence
    ↓
Release
    ↓
Deployment
```

For high-risk changes, the chain may additionally include:

```text
ADR
Migration
Security Review
Operational Readiness
Rollback Plan
```

The exact artifacts depend on the change.

---

# 36. Commit History and Debugging

Commit history is an engineering diagnostic tool.

A useful history should help developers:

* identify when behavior changed;
* identify why it changed;
* locate related tests;
* identify affected architecture decisions;
* identify migrations;
* understand regressions;
* determine which release introduced a behavior;
* safely revert a problematic change.

Therefore, commit quality is part of system maintainability.

---

# 37. Commit Checklist

Before committing, the developer should verify:

### Purpose

* [ ] The commit has one clear logical purpose.
* [ ] The subject accurately describes the change.
* [ ] The scope is meaningful.

### Implementation

* [ ] No unrelated changes are included.
* [ ] Temporary debugging code is removed.
* [ ] Secrets are not included.
* [ ] Production data is not included.

### Testing

* [ ] Relevant tests were added or updated.
* [ ] Relevant tests were executed.
* [ ] Regression behavior is covered where appropriate.

### Documentation

* [ ] Affected documentation was reviewed.
* [ ] Architecture changes have an ADR when required.
* [ ] API changes are reflected in the relevant contract documentation.

### Traceability

* [ ] Relevant requirement or issue is referenced.
* [ ] Relevant ADR is referenced when applicable.
* [ ] Migration information is included when useful.
* [ ] Breaking changes are explicitly identified.

### Risk

* [ ] Security impact was considered.
* [ ] Financial impact was considered where applicable.
* [ ] Inventory impact was considered where applicable.
* [ ] Offline/synchronization impact was considered where applicable.
* [ ] Compatibility impact was considered.

---

# 38. Examples

## 38.1 Simple Feature

```text
feat(menu): allow branch-specific menu activation
```

## 38.2 Bug Fix

```text
fix(pos): prevent duplicate order submission
```

## 38.3 Complex Bug Fix

```text
fix(inventory): prevent negative stock during concurrent orders

Stock availability validation and deduction now execute within
the same consistency boundary.

Refs: INV-044
Tests: inventory/concurrent_orders
```

## 38.4 Security Change

```text
fix(security): reject cross-branch resource access

Authorization now validates the requested resource against the
user's effective branch scope.

Refs: SEC-017
Tests: security/cross_branch_access
```

## 38.5 Database Change

```text
feat(inventory): record stock movement source

Stock movements now distinguish inventory bought ready from
inventory prepared inside a branch.

Refs: INV-031
Migration: 0042_add_stock_source
Tests: inventory/stock_source
```

## 38.6 API Breaking Change

```text
feat(api)!: replace legacy order status representation

BREAKING CHANGE:
The legacy numeric order status representation is no longer
accepted by the API.

Migration guidance is documented in the API contract.

Refs: API-027
Tests: api/order_status
```

## 38.7 Documentation

```text
docs(development): define commit traceability standards
```

## 38.8 Refactoring

```text
refactor(order): separate validation from persistence
```

## 38.9 Performance

```text
perf(reporting): reduce repeated branch statistics queries
```

## 38.10 Revert

```text
revert(sync): revert retry optimization

This reverts commit <commit-id> because the optimization can
produce duplicate synchronization under offline retry conditions.
```

---

# 39. Anti-Patterns

The following commit messages are unacceptable for meaningful project changes:

```text
update
```

```text
changes
```

```text
fix
```

```text
final
```

```text
final fix
```

```text
test
```

```text
new version
```

```text
working
```

```text
small changes
```

```text
many fixes
```

```text
AI generated
```

```text
everything
```

These messages do not provide sufficient engineering information.

---

# 40. Relationship with Other Development Documents

This document defines commit and change-history standards.

It does not replace:

* `03_Git_Branching_and_Version_Control_Strategy.md` for branch strategy;
* `05_Pull_Request_and_Code_Review_Process.md` for pull requests and review;
* `08_Database_Development_and_Migration_Workflow.md` for database development;
* `09_API_Development_and_Contract_Change_Workflow.md` for API development;
* `10_Documentation_First_Development_Workflow.md` for documentation-first development;
* `11_ADR_and_Architecture_Decision_Workflow.md` for architecture decisions;
* `13_Testing_and_Debugging_Workflow.md` for testing and debugging;
* `18_Development_Guardrails_and_Quality_Rules.md` for mandatory development guardrails.

These documents form one development control system.

---

# 41. Commit Standards Invariants

The following rules are mandatory project invariants:

1. Every meaningful commit must have a clear purpose.
2. Every commit must have a meaningful subject.
3. Commit subjects must describe the actual change.
4. Unrelated changes must not be intentionally grouped together.
5. Commit scope must identify the primary affected area.
6. Commit messages must not contain misleading descriptions.
7. High-risk changes must provide sufficient context.
8. Breaking changes must be explicitly identified.
9. Database changes must remain migration-traceable.
10. API changes must remain contract-traceable.
11. Security-sensitive changes must remain security-traceable.
12. Financial changes must remain financially traceable.
13. Inventory changes must remain inventory traceable.
14. Offline synchronization changes must remain synchronization traceable.
15. Architecture-significant changes must reference or create the appropriate ADR.
16. Production behavior changes must have appropriate test evidence.
17. Documentation must remain synchronized with documented behavior.
18. AI-assisted changes follow the same quality standards as manually written changes.
19. Secrets and production data must never be committed.
20. Generated artifacts must not hide source changes.
21. Formatting-only changes should not obscure behavioral changes.
22. Reverts must identify the change being reverted.
23. Shared history must not be rewritten without an approved reason.
24. Commit history must support debugging and maintenance.
25. Commit history must support release traceability.
26. Commit metadata must not be fabricated.
27. Developers remain responsible for the correctness of their commits.
28. Commit quality is part of software quality.
29. Traceability must connect requirements, implementation, tests, and releases.
30. The repository history must remain understandable to future maintainers.

---

# 42. Final Principle

A Git commit is not merely a saved snapshot of code.

It is an engineering record.

Every meaningful commit should help future developers understand:

```text
what changed
    ↓
why it changed
    ↓
what it affects
    ↓
how it was verified
    ↓
what decision or requirement it belongs to
    ↓
which release contains it
```

The project therefore treats commit quality and change traceability as part of the engineering system, not as optional documentation.

**Final rule:**

> Every meaningful change must leave behind a clear, reviewable, testable, and traceable engineering record.

