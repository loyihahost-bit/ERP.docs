# 05. Pull Request and Code Review Process

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the Pull Request (PR), code review, approval, and merge process for the FastFood ERP project.

The purpose is to ensure that every meaningful code change is:

* understandable;
* reviewable;
* technically correct;
* architecturally consistent;
* appropriately tested;
* secure;
* traceable;
* ready for integration.

A Pull Request is not only a Git operation.

It is the primary engineering control point between implementation and integration.

---

## 2. Scope

These rules apply to changes involving:

* backend code;
* frontend code;
* database schema and migrations;
* API contracts;
* security;
* authentication and authorization;
* inventory;
* recipes;
* menu and pricing;
* POS;
* orders and payments;
* cash operations;
* payroll;
* offline synchronization;
* AI services;
* infrastructure;
* configuration;
* dependencies;
* tests;
* documentation;
* deployment-related changes.

The process applies to normal development changes and, with appropriate simplification, emergency changes.

---

# 3. Core Principles

The project follows these PR principles:

1. Meaningful changes should be integrated through a Pull Request.
2. A PR must have a clear purpose.
3. A PR should represent one coherent change.
4. Review must evaluate behavior, not only code style.
5. Reviewers must verify architectural consistency.
6. Tests are part of the change, not an optional afterthought.
7. CI checks must pass before normal merge.
8. Required approvals must be obtained before merge.
9. Authors must respond to review findings.
10. Reviewers must not approve code they do not understand sufficiently.
11. Security-sensitive changes require appropriate security review.
12. High-risk financial and inventory changes require stronger verification.
13. Breaking changes must be explicitly identified.
14. Database changes must be migration-safe.
15. API changes must preserve the approved contract strategy.
16. Merge must preserve repository history and traceability.
17. Review must not become a substitute for automated testing.
18. Automated checks must not become a substitute for engineering judgment.
19. Emergency changes may use an expedited path but must retain traceability.
20. The final merged state must be a state the project is willing to maintain.

---

# 4. Pull Request Lifecycle

The standard lifecycle is:

```text
Development Branch
       ↓
Local Validation
       ↓
Commit Preparation
       ↓
Push Branch
       ↓
Open Pull Request
       ↓
Automated Checks
       ↓
Reviewer Assignment
       ↓
Code Review
       ↓
Author Updates
       ↓
Re-review
       ↓
Approval
       ↓
Final Checks
       ↓
Merge
       ↓
Post-merge Verification
```

Not every PR requires multiple review cycles.

However, a PR must not bypass required controls simply because the change is small.

---

# 5. PR Creation Requirements

A Pull Request should be opened when the branch contains a coherent reviewable change.

Before opening the PR, the developer should verify:

* the branch is based on the correct project state;
* unrelated changes are excluded;
* commits have meaningful messages;
* tests have been run;
* relevant documentation has been reviewed;
* required migrations exist;
* generated files are intentional;
* secrets are not present;
* local debugging artifacts are removed;
* the change is ready for another developer to inspect.

A PR should not be opened merely to transfer unfinished work unless the repository explicitly uses Draft PRs for that purpose.

---

# 6. Draft Pull Requests

Draft PRs may be used when work is not ready for final review.

A Draft PR may be useful for:

* early architectural feedback;
* complex feature development;
* dependency-risk evaluation;
* uncertain implementation direction;
* large changes requiring staged review.

A Draft PR must clearly indicate that it is not ready for merge.

A Draft PR must not be treated as approval to bypass normal testing or review requirements.

---

# 7. PR Title Standard

PR titles should clearly describe the change.

Prefer:

```text id="m9dz6n"
Add branch-specific menu activation
```

```text id="e0z0ax"
Prevent negative inventory during concurrent orders
```

```text id="hl3b5m"
Enforce branch scope in employee reports
```

Avoid:

```text id="yypbvv"
Changes
```

```text id="jq1k3n"
Fix stuff
```

```text id="f9g1g5"
Update
```

```text id="36p6xq"
Final version
```

The PR title should remain understandable when viewed in:

* Git history;
* release notes;
* change logs;
* project dashboards.

---

# 8. PR Description

Every non-trivial PR should explain the change sufficiently for a reviewer to understand it without reconstructing the entire development process.

A recommended structure is:

```text id="twv4h8"
## Summary

What changed and why?

## Scope

Which parts of the system are affected?

## Business Impact

What user or business behavior changes?

## Technical Impact

What architectural or implementation behavior changes?

## Testing

What tests were added or executed?

## Documentation

Which documents were updated?

## Database

Are migrations included?

## API

Does the API contract change?

## Security

Are authentication, authorization, isolation, or sensitive data affected?

## Risks

What could fail or require special attention?

## Traceability

Requirement / Issue:
ADR:
Related documentation:
```

Not every section is required for every PR.

The description should contain the information necessary for the change.

---

# 9. PR Scope

A PR should be small enough to review effectively while remaining logically complete.

A PR may include multiple files and layers when they implement one feature.

For example:

```text id="q6b6c7"
Backend
Frontend
Tests
Documentation
Migration
```

may belong to one PR if all changes implement the same business requirement.

A PR should not combine unrelated work such as:

```text id="9t2w9g"
Inventory feature
+
unrelated authentication refactor
+
frontend redesign
+
dependency cleanup
```

unless there is a documented architectural reason.

---

# 10. Large Pull Requests

Large changes should be divided when practical.

Possible strategies include:

* separating preparation refactoring from behavior changes;
* splitting backend and frontend work when they can be safely integrated independently;
* introducing infrastructure support before enabling behavior;
* separating migration preparation from application activation;
* using stacked PRs when supported by the workflow.

The goal is not to minimize file count.

The goal is to minimize review complexity while preserving a safe integration sequence.

---

# 11. Reviewer Selection

Reviewers should be selected based on the affected area and required expertise.

Examples:

| Change         | Appropriate Review Focus              |
| -------------- | ------------------------------------- |
| Authentication | Security                              |
| Authorization  | Security + domain behavior            |
| Inventory      | Inventory/domain correctness          |
| Recipes        | Recipe/domain correctness             |
| Cash           | Financial correctness                 |
| Payroll        | Financial/domain correctness          |
| API            | API contract                          |
| Database       | Data integrity                        |
| Offline sync   | Consistency and synchronization       |
| Frontend       | UI behavior and frontend architecture |
| AI             | Model/inference behavior              |
| Deployment     | Infrastructure/operations             |

A reviewer should not be selected solely because they are available.

The reviewer must have sufficient context or access to the relevant project documentation.

---

# 12. Required Approvals

Normal changes should not be merged until the required approval level has been reached.

Approval requirements should be determined by:

* change risk;
* affected subsystem;
* security impact;
* financial impact;
* database impact;
* API compatibility;
* architectural significance.

A simple low-risk documentation change may require one appropriate reviewer.

A high-risk security, financial, or architecture change may require additional review.

---

# 13. Author Responsibilities

The PR author is responsible for:

* explaining the change;
* providing sufficient context;
* ensuring tests are appropriate;
* responding to review comments;
* updating the implementation when required;
* keeping the PR focused;
* updating documentation;
* identifying risks;
* identifying breaking changes;
* resolving conflicts;
* ensuring the final PR state remains valid.

Opening a PR does not transfer responsibility for correctness to the reviewer.

The author remains responsible for the change.

---

# 14. Reviewer Responsibilities

A reviewer should evaluate the change from an engineering perspective.

The reviewer should consider:

### Correctness

* Does the implementation do what it claims?
* Are edge cases handled?
* Can invalid states be produced?

### Architecture

* Does the change respect architectural boundaries?
* Is responsibility placed in the correct layer?
* Does it create unnecessary coupling?

### Security

* Can authorization be bypassed?
* Is tenant or branch isolation preserved?
* Are sensitive data and secrets handled correctly?

### Data Integrity

* Can inconsistent data be created?
* Are transactions and concurrency handled correctly?
* Are migrations safe?

### Business Rules

* Does the behavior match approved business requirements?
* Does it preserve existing business constraints?

### Testing

* Are important paths covered?
* Is regression behavior tested?
* Are failure conditions tested where appropriate?

### Maintainability

* Is the code understandable?
* Does it introduce unnecessary complexity?
* Will future developers understand the implementation?

---

# 15. Review Priorities

Reviewers should prioritize issues in this order:

1. Security vulnerabilities.
2. Data corruption or integrity problems.
3. Financial correctness.
4. Business rule violations.
5. Authorization and isolation problems.
6. Concurrency and synchronization failures.
7. API compatibility problems.
8. Production reliability risks.
9. Significant performance problems.
10. Maintainability concerns.
11. Style and minor readability issues.

Style should not distract from critical correctness problems.

---

# 16. Review Comment Severity

Review comments should communicate importance clearly.

A practical classification is:

### Blocking

The PR must not be merged until the issue is resolved.

Examples:

* security vulnerability;
* incorrect financial calculation;
* data corruption risk;
* broken authorization;
* invalid migration;
* serious concurrency bug;
* known production failure.

### Important

The issue should normally be resolved before merge, but may require engineering judgment.

Examples:

* significant maintainability issue;
* missing important test;
* unclear business behavior;
* problematic API design.

### Suggestion

A non-blocking improvement.

Examples:

* readability;
* naming;
* minor simplification;
* optional refactoring.

### Question

Used when clarification is needed.

A question is not automatically a request for change.

---

# 17. Review Comments Must Be Specific

Prefer:

```text
This check validates the user's branch on the frontend,
but the API does not enforce the same scope. A direct API request
could therefore access another branch's resource.
```

Avoid:

```text
Security issue.
```

Prefer:

```text
This query can return duplicate rows when two inventory deductions
are processed concurrently. Please verify the transaction boundary.
```

Avoid:

```text
Concurrency?
```

Review comments should explain enough context for the author to act correctly.

---

# 18. Review and Business Rules

Reviewers must verify important business invariants.

Examples include:

### Inventory

* Negative stock must not be introduced.
* Insufficient inventory must be handled according to the approved rule.
* Recipe dependencies must remain consistent.

### Cash

* Register state must remain consistent.
* Correction limits must remain enforced.
* Handover confirmation must remain reliable.

### Permissions

* Server-side authorization must remain authoritative.
* Branch scope must not be bypassed.
* Tenant isolation must remain intact.

### Subscription

* Expired functionality must be restricted according to the approved policy.
* Allowed historical data access must remain available where required.

### Offline

* Retries must not create duplicate business transactions.
* Synchronization must preserve transaction identity.
* Conflicts must follow the approved synchronization policy.

---

# 19. Automated Checks

Automated checks should normally run before merge.

Typical checks include:

```text id="t9y1dy"
Formatting
Linting
Type checking
Unit tests
Domain tests
Integration tests
API contract tests
Frontend tests
Migration checks
Security checks
Build checks
```

The exact checks depend on the affected area.

A PR should not be merged simply because it received human approval if required automated checks are failing.

---

# 20. Failed CI Checks

When CI fails, the author should determine whether the failure is:

1. caused by the PR;
2. caused by an existing repository problem;
3. caused by infrastructure;
4. caused by a flaky test.

PR-related failures must be fixed before normal merge.

Infrastructure or flaky failures should be investigated and documented rather than ignored.

Disabling a check merely to obtain a green PR is not acceptable.

---

# 21. Review Changes After Approval

If the author changes the implementation after approval, the reviewer must determine whether another review is required.

Significant changes after approval include:

* changing business behavior;
* modifying security logic;
* changing database migrations;
* changing API contracts;
* changing concurrency logic;
* changing financial calculations;
* changing synchronization behavior.

Approval must represent the code that is actually being merged.

An approval for an earlier version must not be treated as automatic approval for a substantially different final version.

---

# 22. Resolving Review Comments

The author should:

1. understand the review comment;
2. make the required change when appropriate;
3. add or update tests;
4. respond to the comment;
5. request re-review when necessary.

A comment should not be marked resolved merely because it is inconvenient.

The author and reviewer should reach a clear technical conclusion.

---

# 23. Disagreement During Review

Technical disagreement should be resolved using project evidence.

Preferred sources include:

1. accepted business requirements;
2. system/domain analysis;
3. architecture documentation;
4. ADRs;
5. security policies;
6. database/API contracts;
7. testing requirements;
8. established development standards.

Personal preference should not override an accepted project decision.

If the existing decision is inadequate, the appropriate architecture or analysis process should be used to change it.

---

# 24. Architecture-Significant PRs

A PR that changes architecture should not silently introduce a new architectural pattern.

Examples include:

* introducing a new service boundary;
* changing domain ownership;
* changing data ownership;
* introducing a new integration mechanism;
* changing synchronization architecture;
* changing authentication architecture;
* changing deployment topology.

Such changes require appropriate documentation and, where applicable, an ADR.

The PR should reference the relevant ADR.

Example:

```text id="qj5f74"
Architecture:
ADR-021
```

---

# 25. Database PRs

Database-related PRs require additional review.

Reviewers should verify:

* migration correctness;
* schema compatibility;
* indexes;
* constraints;
* foreign keys;
* data integrity;
* transaction implications;
* migration ordering;
* rollback or recovery considerations;
* production data volume implications.

Special care is required for:

* large tables;
* destructive changes;
* column removal;
* constraint changes;
* data transformations;
* index creation;
* changes affecting synchronization.

---

# 26. API PRs

API-related PRs should verify:

* request schema;
* response schema;
* validation;
* authorization;
* error behavior;
* status codes;
* compatibility;
* pagination;
* idempotency;
* documentation;
* contract tests.

If an API change is breaking, the PR must explicitly identify it.

---

# 27. Security-Sensitive PRs

Security-sensitive PRs should receive appropriate security review.

Examples include:

* authentication;
* authorization;
* tenant isolation;
* branch permissions;
* trusted devices;
* offline authentication;
* session management;
* encryption;
* secrets;
* audit logging;
* file access;
* privileged operations.

Reviewers should assume that frontend restrictions are insufficient and verify server-side enforcement.

---

# 28. Financial PRs

Financial changes should receive additional scrutiny.

Reviewers should verify:

* calculation correctness;
* rounding;
* payment state transitions;
* refund authorization;
* cash register consistency;
* correction limits;
* payroll calculations;
* report consistency;
* concurrency behavior.

Tests should cover important success and failure cases.

---

# 29. Inventory and Recipe PRs

Inventory and recipe changes should verify:

* stock deduction;
* stock availability;
* recipe dependencies;
* semi-finished products;
* FIFO behavior;
* yield loss;
* inventory adjustment;
* stock discrepancy;
* shopping calculations;
* archived recipe behavior;
* concurrent operations.

The review must ensure that changes do not silently violate inventory invariants.

---

# 30. Offline and Synchronization PRs

Offline changes require special review because the system may operate without immediate server communication.

Reviewers should consider:

* retry behavior;
* duplicate submission;
* transaction identity;
* ordering;
* conflict handling;
* local authorization;
* stale state;
* synchronization recovery;
* partial failure.

Tests should include relevant offline and reconnect scenarios.

---

# 31. Frontend PRs

Frontend review should verify:

* behavior;
* state management;
* permission visibility;
* loading states;
* error states;
* offline behavior;
* accessibility where applicable;
* API contract usage;
* performance;
* responsive behavior where required.

Frontend restrictions must not be treated as the primary authorization mechanism.

---

# 32. AI-Related PRs

AI-related changes should identify:

* model changes;
* model version;
* inference behavior;
* input/output contract;
* performance implications;
* resource requirements;
* fallback behavior;
* failure handling;
* test evidence.

An AI model update should not be treated as a simple dependency update when it changes production behavior.

---

# 33. Documentation PRs

Documentation changes should be reviewed for:

* correctness;
* consistency;
* cross-links;
* terminology;
* version/status;
* architectural alignment;
* duplication.

Documentation must not contradict accepted system decisions.

---

# 34. Dependency PRs

Dependency changes should be reviewed for:

* security advisories;
* compatibility;
* license implications;
* transitive dependencies;
* performance;
* breaking changes;
* lock file consistency.

A dependency upgrade should not be merged solely because a newer version exists.

---

# 35. Merge Preconditions

A normal PR should satisfy all applicable conditions before merge:

* [ ] PR purpose is clear.
* [ ] Scope is coherent.
* [ ] Required reviewers have reviewed the change.
* [ ] Required approvals are present.
* [ ] Blocking review comments are resolved.
* [ ] Required CI checks pass.
* [ ] Tests are sufficient.
* [ ] Documentation is synchronized.
* [ ] Database migrations are valid.
* [ ] API compatibility has been checked.
* [ ] Security impact has been reviewed.
* [ ] Breaking changes are identified.
* [ ] Required ADRs exist.
* [ ] No secrets or production data are included.
* [ ] Final branch state is reviewed.

---

# 36. Merge Strategy

The repository should use a controlled merge strategy that preserves useful history.

The exact GitHub merge mechanism may be configured according to repository needs.

Possible strategies include:

* squash merge;
* merge commit;
* rebase merge.

The selected strategy must remain consistent with the project's branch and release workflow.

The merge strategy should prioritize:

* traceability;
* clean history;
* reliable rollback;
* release analysis;
* understandable commit relationships.

---

# 37. Squash Merge

Squash merge may be preferred when a development branch contains temporary or iterative commits that do not provide useful permanent history.

For example:

```text id="nqwywv"
wip
fix review
fix tests
rename
final fix
```

may become one meaningful integration commit.

However, the final commit must follow the commit standards defined in:

`04_Commit_Message_and_Change_Standards.md`

Squashing must not remove important traceability information.

---

# 38. Merge Commit

A merge commit may be appropriate when preserving branch history is useful.

Examples include:

* complex release branches;
* long-running integration branches;
* coordinated changes;
* situations where branch topology itself provides useful history.

The merge must still preserve a clear and reviewable final state.

---

# 39. Rebase Merge

Rebase-based integration may be used when repository policy allows it and history can remain understandable.

Developers must not use rebasing to hide meaningful development history when that history is required for traceability.

Shared-history rewriting must follow the rules defined by the Git branching strategy.

---

# 40. Direct Push to Protected Branches

Direct pushes to protected stable branches should normally be disabled.

Normal changes should pass through:

```text id="qj1vvs"
Branch
  ↓
Pull Request
  ↓
Review
  ↓
Checks
  ↓
Approval
  ↓
Merge
```

Direct changes should be limited to explicitly authorized emergency procedures.

---

# 41. Emergency and Hotfix Changes

Emergency changes may require an expedited review process.

Examples:

* active security vulnerability;
* severe production failure;
* data corruption risk;
* critical payment failure;
* critical synchronization failure.

The emergency process may reduce the number of normal steps, but it must not remove traceability.

At minimum, the emergency change should have:

* clear reason;
* identified risk;
* appropriate authorization;
* focused implementation;
* relevant validation;
* post-change review;
* documentation or incident record where required.

The hotfix must be integrated back into the normal development/release history.

---

# 42. Merge Conflicts

When conflicts occur, the developer resolving the conflict is responsible for ensuring that the final result preserves the intended behavior.

Conflict resolution must not simply choose one side mechanically.

After conflict resolution:

* affected tests must be rerun;
* important business behavior must be reviewed;
* migrations must be checked;
* API contracts must be checked;
* security boundaries must be re-evaluated when relevant.

---

# 43. Stale Pull Requests

A PR may become stale when the target branch changes significantly.

The author should update the branch when necessary.

After a significant update, reviewers should verify that their previous conclusions still apply.

A previously approved PR should not be merged blindly after substantial conflict resolution or rebasing.

---

# 44. PR Size Guidance

There is no universal file-count limit.

Instead, consider:

* number of logical behaviors changed;
* architectural complexity;
* risk;
* number of reviewers required;
* test complexity;
* migration impact;
* API impact.

A small but security-critical PR may require more review than a large documentation PR.

Risk is more important than raw size.

---

# 45. Code Review Quality

A good review is:

* focused;
* evidence-based;
* respectful;
* technically specific;
* consistent with project decisions;
* proportional to risk.

A review is not:

* a personal style contest;
* a replacement for tests;
* a way to redesign unrelated parts of the system;
* a reason to delay unrelated work;
* approval based only on whether the code "looks fine."

---

# 46. Reviewer Independence

For high-risk changes, reviewers should provide an independent assessment rather than simply repeating the author's assumptions.

The reviewer should actively consider:

```text
What could go wrong?
What business invariant could be violated?
What happens under failure?
What happens concurrently?
What happens offline?
What happens with insufficient permissions?
What happens with stale data?
```

This mindset is especially important for:

* financial operations;
* inventory;
* synchronization;
* security;
* authentication;
* authorization;
* database changes.

---

# 47. Post-Merge Verification

After merge, appropriate verification should occur.

Depending on the change, this may include:

* CI validation;
* staging deployment;
* migration verification;
* smoke tests;
* API health checks;
* frontend build verification;
* synchronization checks;
* production monitoring.

A merge is not necessarily the end of the engineering lifecycle.

The final deployed behavior must also be verified.

---

# 48. Traceability

The PR should preserve the relationship:

```text id="h2o9p4"
Requirement
    ↓
Analysis
    ↓
Architecture / ADR
    ↓
Implementation
    ↓
Tests
    ↓
Pull Request
    ↓
Approval
    ↓
Merge
    ↓
Release
```

This allows future developers to determine:

* why the change exists;
* who reviewed it;
* what was tested;
* which requirements it implements;
* which architecture decision it follows;
* which release introduced it.

---

# 49. PR Checklist

Before requesting final review:

### Scope

* [ ] The PR has one clear purpose.
* [ ] Unrelated changes are excluded.
* [ ] The PR title is meaningful.
* [ ] The description explains the change.

### Code

* [ ] Code follows project architecture.
* [ ] No unnecessary complexity was introduced.
* [ ] No debugging code remains.
* [ ] No secrets are included.

### Testing

* [ ] Appropriate tests were added or updated.
* [ ] Relevant tests pass.
* [ ] Failure cases were considered.
* [ ] Regression cases are covered where appropriate.

### Documentation

* [ ] Relevant documentation is updated.
* [ ] ADR is created or referenced when necessary.
* [ ] API documentation is updated when required.

### Security

* [ ] Authentication impact was considered.
* [ ] Authorization impact was considered.
* [ ] Tenant isolation remains intact.
* [ ] Branch isolation remains intact.
* [ ] Sensitive data handling is correct.

### Data

* [ ] Database migrations are valid.
* [ ] Data integrity is preserved.
* [ ] Concurrency implications were considered.

### Business

* [ ] Financial rules are preserved.
* [ ] Inventory rules are preserved.
* [ ] Recipe rules are preserved.
* [ ] Offline behavior is preserved where applicable.
* [ ] Subscription restrictions are preserved where applicable.

### Review

* [ ] Required reviewers are assigned.
* [ ] Review comments are addressed.
* [ ] Final changes have been re-reviewed where necessary.
* [ ] Required approvals are present.

### Merge

* [ ] CI checks pass.
* [ ] Branch state is current enough.
* [ ] No blocking comments remain.
* [ ] The final state is ready for integration.

---

# 50. Anti-Patterns

The following practices are not acceptable for normal development:

### Merge without required review

```text
Open PR
↓
No review
↓
Merge
```

### Ignore failing checks

```text
CI failed
↓
Merge anyway
```

### Hide breaking behavior

```text
fix(api): small update
```

when the API contract actually breaks clients.

### Approve without understanding

```text
Looks fine
```

without meaningful inspection of a high-risk change.

### Review only formatting

Focusing on naming or formatting while missing:

* authorization failures;
* data corruption;
* financial errors;
* negative inventory;
* synchronization duplication.

### Resolve comments without resolution

Marking a blocking review comment resolved without actually addressing it.

### Add unrelated cleanup

Using a feature PR to introduce unrelated refactoring or formatting changes.

### Merge stale approval

Treating approval for an old implementation as approval for a substantially changed final version.

### Bypass protected branches

Directly pushing normal changes into stable branches.

---

# 51. Relationship with Other Development Documents

This document defines PR and review workflow.

It works together with:

* `03_Git_Branching_and_Version_Control_Strategy.md` for branch and version-control rules;
* `04_Commit_Message_and_Change_Standards.md` for commit quality and traceability;
* `06_Backend_Development_Standards.md` for backend implementation rules;
* `07_Frontend_Development_Standards.md` for frontend implementation rules;
* `08_Database_Development_and_Migration_Workflow.md` for database changes;
* `09_API_Development_and_Contract_Change_Workflow.md` for API changes;
* `10_Documentation_First_Development_Workflow.md` for documentation-first development;
* `11_ADR_and_Architecture_Decision_Workflow.md` for architecture decisions;
* `13_Testing_and_Debugging_Workflow.md` for testing and debugging;
* `18_Development_Guardrails_and_Quality_Rules.md` for mandatory development controls.

No document should be interpreted in isolation when a change crosses multiple engineering boundaries.

---

# 52. Pull Request Invariants

The following rules are mandatory project invariants:

1. Meaningful changes should normally enter stable branches through Pull Requests.
2. Every PR must have a clear purpose.
3. PR scope must remain coherent.
4. PR titles must describe the change accurately.
5. Non-trivial PRs must provide sufficient context.
6. Review must evaluate correctness, not only style.
7. Review must consider architectural consistency.
8. Required approvals must be obtained before normal merge.
9. Blocking review findings must be resolved.
10. Required automated checks must pass before normal merge.
11. Approval must correspond to the code that is actually merged.
12. Significant post-approval changes require appropriate re-review.
13. Security-sensitive changes require appropriate security review.
14. Financial changes require appropriate financial correctness review.
15. Inventory changes require appropriate inventory correctness review.
16. Database changes require migration review.
17. API changes require contract review.
18. Offline and synchronization changes require consistency review.
19. Architecture-significant changes require appropriate architecture documentation.
20. Breaking changes must be explicitly identified.
21. Authors remain responsible for their changes.
22. Reviewers must provide technically meaningful review.
23. CI failures must not be ignored merely to enable merging.
24. Protected stable branches must not receive normal direct pushes.
25. Emergency changes must retain traceability.
26. Merge conflict resolution must be validated.
27. Unrelated changes must not be hidden inside feature PRs.
28. Tests must accompany behavior changes where appropriate.
29. Documentation must remain synchronized with approved behavior.
30. The merged state must be safe, understandable, traceable, and maintainable.

---

# 53. Final Principle

A Pull Request is the controlled transition between development and integrated project state.

The project therefore treats:

```text
PR
+
Review
+
Automated Checks
+
Approval
+
Merge
```

as one engineering control system.

The objective is not to create bureaucracy.

The objective is to ensure that important changes are understood before they become part of the system.

**Final rule:**

> No meaningful change should become part of the stable system merely because the code works on one developer's machine; it must be appropriately reviewed, verified, approved, and traceable.

