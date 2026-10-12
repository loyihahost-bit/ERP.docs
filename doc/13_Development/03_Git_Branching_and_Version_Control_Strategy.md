# DEV-03 — Git Branching and Version Control Strategy

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the Git branching and version control strategy for the FastFood ERP project.

The purpose is to provide a predictable and safe method for:

* developing features;
* fixing bugs;
* maintaining stable code;
* reviewing changes;
* merging work;
* preparing releases;
* maintaining release branches;
* handling urgent fixes;
* preserving project history;
* identifying released versions;
* supporting rollback and recovery.

Git is treated as an engineering control, not merely as a backup mechanism.

---

# 2. Scope

This document covers:

* version control principles;
* repository history;
* branch types;
* branch naming;
* branch lifecycle;
* feature development;
* bug fixes;
* release branches;
* hotfixes;
* merge rules;
* protected branches;
* branch synchronization;
* conflict resolution;
* tags;
* release versions;
* branch cleanup;
* history preservation;
* emergency changes;
* repository recovery;
* version control invariants.

This document does not define detailed commit-message syntax. That is defined in:

`04_Commit_Message_and_Change_Standards.md`

It also does not define the full pull request review process. That is defined in:

`05_Pull_Request_and_Code_Review_Process.md`

---

# 3. Version Control Principles

The project follows these principles:

1. **Every meaningful change is version controlled.**
2. **Stable branches must remain deployable or intentionally marked otherwise.**
3. **Development work should be isolated from stable code.**
4. **Changes must be traceable to their purpose.**
5. **Branches should have short and understandable lifetimes.**
6. **Release history must remain identifiable.**
7. **Production fixes must be traceable back to the released version.**
8. **Destructive history rewriting must be restricted.**
9. **Merges must preserve understandable project history.**
10. **Git must not be used to bypass testing, review, or release controls.**

---

# 4. Source of Truth

The Git repository is the authoritative source for versioned application code.

The following should normally be version controlled:

* application source;
* tests;
* database migrations;
* API schemas;
* configuration templates;
* development scripts;
* documentation maintained with the application;
* architecture decisions maintained with the application;
* dependency definitions;
* CI configuration;
* relevant infrastructure definitions.

The following must not be treated as source-controlled application artifacts:

* production secrets;
* personal credentials;
* temporary local files;
* private environment files;
* generated output unless intentionally versioned;
* local caches.

---

# 5. Branch Model

The baseline branch model is:

```text
main
 │
 ├── feature/*
 ├── fix/*
 ├── refactor/*
 ├── chore/*
 ├── release/*
 └── hotfix/*
```

The exact number of active branches should remain small.

Branches exist to isolate a meaningful unit of work, not to create unnecessary hierarchy.

---

# 6. Main Branch

`main` is the primary stable integration branch.

It represents the latest accepted state of the project.

The following rules apply:

* direct development commits should normally not be made;
* changes should arrive through the approved review process;
* required automated checks must pass;
* the branch should remain releasable unless explicitly documented otherwise;
* release tags are created from a verified release state;
* emergency changes must still be traceable.

`main` should not become a long-term experimental branch.

---

# 7. Feature Branches

Feature branches are used for new functionality.

Naming:

```text id="q5j0kz"
feature/<short-description>
```

Examples:

```text id="wq8a3f"
feature/order-modification
feature/recipe-approval
feature/branch-reports
feature/offline-order-sync
```

Feature branches should normally be created from the current development baseline, usually `main` unless another active integration branch is explicitly defined.

---

# 8. Bug Fix Branches

Bug fixes should use:

```text id="r4q9sw"
fix/<short-description>
```

Examples:

```text id="j2c7fa"
fix/cash-session-close
fix/inventory-deduction
fix/order-payment-duplicate
```

A bug fix branch should address a clearly defined defect.

Unrelated refactoring should not be mixed into the same branch unless required to safely correct the defect.

---

# 9. Refactoring Branches

Significant refactoring may use:

```text id="f7v3ac"
refactor/<short-description>
```

Examples:

```text id="k0x8nf"
refactor/order-domain-boundaries
refactor/repository-structure
refactor/permission-resolution
```

Refactoring should preserve externally expected behavior unless the change explicitly includes behavior modification.

Behavior changes should be separately identified.

---

# 10. Chore Branches

Non-feature engineering work may use:

```text id="m9q2zr"
chore/<short-description>
```

Examples:

```text id="d1w7ps"
chore/update-development-tools
chore/upgrade-test-dependencies
chore/ci-maintenance
```

A chore should not silently contain unrelated product behavior.

---

# 11. Release Branches

Release branches are used when a release needs stabilization independently from ongoing development.

Naming:

```text id="c7p4ym"
release/<version>
```

Examples:

```text id="r8x2va"
release/1.0.0
release/1.1.0
release/2.0.0
```

A release branch should contain only changes required to prepare the specified release.

Typical release branch activities include:

* release-specific bug fixes;
* documentation corrections;
* version metadata;
* migration validation;
* compatibility fixes;
* release configuration;
* release notes preparation.

New unrelated features should not normally be added to a release branch.

---

# 12. Release Branch Lifecycle

A release branch follows:

```text id="9e6w2p"
main
  ↓
release/1.2.0
  ↓
Release Validation
  ↓
Release Fixes
  ↓
Final Validation
  ↓
Tag 1.2.0
  ↓
Merge Back
```

The release branch exists only as long as stabilization requires.

After the release is completed:

* the release tag identifies the released state;
* release changes are synchronized back to the appropriate development branch;
* the release branch may be deleted.

---

# 13. Hotfix Branches

Hotfix branches are reserved for urgent corrections to a released version.

Naming:

```text id="m4r8te"
hotfix/<short-description>
```

Examples:

```text id="q8k2ls"
hotfix/payment-duplication
hotfix/security-authorization-bypass
hotfix/critical-migration
```

A hotfix should be used only when normal development flow cannot safely address the production issue within the required time.

---

# 14. Hotfix Lifecycle

Typical flow:

```text id="v9d5rc"
Released Tag
    ↓
hotfix/critical-problem
    ↓
Focused Fix
    ↓
Critical Testing
    ↓
Review
    ↓
Release New Patch Version
    ↓
Merge Fix Back
```

The hotfix must not become a permanent parallel development path.

---

# 15. Branch Naming Rules

Branch names should:

* use lowercase;
* use `kebab-case` for descriptions;
* identify the work type;
* remain concise;
* avoid personal names;
* avoid ticket numbers without useful context;
* avoid vague names.

Preferred:

```text id="5z6h0j"
feature/recipe-versioning
fix/cash-handover-confirmation
refactor/permission-resolution
```

Avoid:

```text id="rj8n3y"
my-branch
test
new
fix
branch1
zyod
work
```

---

# 16. Branch Lifetime

Branches should have limited lifetimes.

Long-lived branches increase:

* merge conflicts;
* divergence;
* integration risk;
* stale assumptions;
* duplicated work.

If a branch becomes long-lived, the developer should regularly synchronize it with the relevant integration baseline.

---

# 17. One Logical Change Per Branch

A branch should normally represent one logical unit of work.

For example:

```text id="1s4r9x"
feature/recipe-approval
```

should not also contain unrelated:

* payroll changes;
* dashboard redesign;
* dependency upgrades;
* unrelated bug fixes.

Exceptions are allowed when changes are technically inseparable.

---

# 18. Branch and Documentation Changes

If implementation changes documented behavior, the same logical work should include the necessary documentation updates or clearly trace them to a separate coordinated change.

A feature should not be considered complete while code and required documentation intentionally describe different behavior.

---

# 19. Branch and Database Changes

Database changes must remain synchronized with the branch containing the code that requires them.

A branch introducing a database-dependent feature should include the necessary migration and related tests.

The branch must not rely on undocumented manual database changes.

Detailed database workflow is defined in:

`08_Database_Development_and_Migration_Workflow.md`

---

# 20. Branch and API Changes

API contract changes should remain traceable to the branch implementing the change.

The branch should include, as appropriate:

* API schema changes;
* implementation;
* contract tests;
* compatibility handling;
* documentation.

Detailed API workflow is defined in:

`09_API_Development_and_Contract_Change_Workflow.md`

---

# 21. Creating a Branch

Before creating a new branch, the developer should:

1. synchronize with the relevant base branch;
2. ensure the working tree is understood;
3. identify the logical change;
4. choose the appropriate branch type;
5. use a descriptive name.

Example:

```text id="0g8q8x"
main
  ↓
feature/offline-order-sync
```

---

# 22. Synchronizing a Branch

Developers should periodically synchronize active branches with the relevant base branch when:

* the branch is long-lived;
* important architectural changes have landed;
* dependent API or database changes have changed;
* conflict risk is increasing.

Synchronization should not be used to hide conflicts or rewrite shared history carelessly.

---

# 23. Merge Strategy

The project should use a controlled merge strategy.

The selected merge method should prioritize:

* reviewability;
* traceability;
* understandable history;
* clean release identification;
* low risk of accidental duplication.

The exact merge mechanism may be standardized by repository tooling.

The important rule is that the resulting history must remain understandable.

---

# 24. Pull Request Before Merge

Normal feature, bug-fix, refactor, and chore branches should be merged through the pull request workflow.

The pull request should provide:

* purpose;
* relevant context;
* affected areas;
* tests;
* migration information when relevant;
* API impact when relevant;
* security considerations when relevant;
* documentation impact when relevant.

Detailed review rules are defined in:

`05_Pull_Request_and_Code_Review_Process.md`

---

# 25. Direct Push to Main

Direct pushes to `main` should normally be prohibited.

Exceptions may exist for:

* repository initialization;
* controlled administrative maintenance;
* emergency recovery;
* explicitly authorized repository administration.

Any exception must remain traceable.

---

# 26. Protected Branches

At minimum, `main` should be treated as a protected branch.

Protection should enforce, where supported:

* pull requests;
* required checks;
* review requirements;
* restricted force-push;
* restricted branch deletion;
* controlled administrative access.

The exact Git hosting configuration belongs to repository administration and deployment governance.

---

# 27. Required Checks Before Merge

A branch should satisfy applicable checks before merge.

Depending on the change, these may include:

* formatting;
* linting;
* type checking;
* unit tests;
* domain tests;
* application tests;
* repository tests;
* API contract tests;
* integration tests;
* security tests;
* frontend tests;
* E2E tests;
* migration validation.

The required depth depends on risk.

---

# 28. Merge Conflicts

Merge conflicts must be resolved deliberately.

The developer resolving a conflict must understand:

* what the current branch changed;
* what the target branch changed;
* whether the changes represent compatible behavior;
* whether documentation is affected;
* whether tests are affected;
* whether a database or API contract changed.

Conflict resolution must not simply select one side without understanding the behavior.

---

# 29. Conflict Resolution Validation

After resolving conflicts:

```text id="9y2wqa"
Resolve
  ↓
Review Changed Files
  ↓
Run Relevant Tests
  ↓
Review Diff
  ↓
Continue Merge
```

Critical business areas require additional validation.

These include:

* financial behavior;
* inventory;
* permissions;
* tenant isolation;
* branch isolation;
* offline synchronization;
* database migrations.

---

# 30. Rebase Policy

Rebase may be used for private branches when it improves local history or synchronization.

Rebase should not rewrite history that other developers are already depending on unless explicitly coordinated.

General rule:

> **Private history may be rewritten carefully; shared history should be treated as immutable.**

---

# 31. Force Push Policy

Force pushing is restricted.

Force push must not be used on protected shared branches.

On personal feature branches, a controlled force push may be acceptable after a rebase when:

* no other developer depends on the branch history;
* the branch is not protected;
* the developer understands the impact.

Safer force-push behavior should be preferred where supported.

---

# 32. Shared Branch History

Once a branch is actively shared, its history should be treated as shared state.

Developers should avoid:

* rewriting commits others have based work on;
* deleting shared branches unexpectedly;
* replacing history without coordination.

This reduces collaboration failures.

---

# 33. Merge vs Rebase

Both merge and rebase are tools, not goals.

Use the method that best preserves:

* traceability;
* reviewability;
* branch safety;
* understandable history.

Do not use rebase merely to make history visually perfect if it introduces collaboration risk.

---

# 34. Branch Cleanup

After a branch has been successfully merged and is no longer required:

* delete the remote branch when appropriate;
* delete the local branch;
* retain the commits through the merged history or release tag;
* preserve the pull request record.

Deleting an obsolete branch does not mean deleting project history.

---

# 35. Release Versioning

Released versions should use a predictable version format.

The project should use Semantic Versioning where applicable:

```text id="0h4z1c"
MAJOR.MINOR.PATCH
```

Examples:

```text id="4nq8vc"
1.0.0
1.1.0
1.1.1
2.0.0
```

The version must communicate the nature of the release.

---

# 36. Version Meaning

General interpretation:

### MAJOR

Used for incompatible changes that require a major version boundary.

### MINOR

Used for backward-compatible functionality additions.

### PATCH

Used for backward-compatible bug fixes and corrections.

The actual decision must consider API, database, client, deployment, and operational compatibility.

---

# 37. Pre-Release Versions

When required, pre-release versions may be used.

Examples:

```text id="d6p3w0"
1.2.0-alpha.1
1.2.0-beta.1
1.2.0-rc.1
```

Pre-release versions must not be treated as equivalent to stable production releases.

---

# 38. Git Tags

Every production release should be identified by an immutable Git tag.

Recommended format:

```text id="m9r2jc"
v1.0.0
v1.1.0
v1.1.1
```

Tags provide a stable reference to the exact source state used for a release.

---

# 39. Tagging Rules

A release tag should be created only after:

* release validation;
* required tests;
* migration validation;
* API compatibility validation where applicable;
* release approval;
* release version confirmation.

The tag should point to the exact release commit.

---

# 40. Release Traceability

For every production release, the project should be able to identify:

```text id="t2d7rx"
Release Version
      ↓
Git Tag
      ↓
Commit
      ↓
Pull Requests
      ↓
Changes
      ↓
Tests
      ↓
Deployment Artifact
```

This supports troubleshooting, auditing, rollback, and incident response.

---

# 41. Release Branch and Main Synchronization

When a release branch is used, release-specific changes must not remain isolated from future development.

After release completion:

```text id="j4v7qa"
release/1.2.0
       ↓
tag v1.2.0
       ↓
release changes
       ↓
main / active development baseline
```

The exact merge-back destination depends on the active branch model.

The important requirement is that necessary fixes are not accidentally lost.

---

# 42. Hotfix Versioning

A production hotfix should normally produce a new patch version.

Example:

```text id="8c1n4e"
v1.4.0
   ↓
critical defect
   ↓
v1.4.1
```

The new version must contain only the necessary correction and required validation.

---

# 43. Multiple Supported Releases

If multiple production versions are actively supported, each supported release may require its own maintenance branch.

Example:

```text id="p3x0t8"
main
 │
 ├── release/2.0
 └── release/1.9
```

This should be used only when there is a real support requirement.

Maintaining many release branches increases complexity and should not be done without justification.

---

# 44. Long-Term Release Branches

A release branch should become long-lived only when the project intentionally supports maintenance of that release line.

A long-lived release branch requires:

* clear ownership;
* defined supported version;
* defined security policy;
* controlled backports;
* documented end-of-support condition.

---

# 45. Backporting Fixes

When a bug affects multiple supported release lines, a fix may need to be backported.

Backporting must preserve:

* behavior correctness;
* compatibility with the target version;
* security requirements;
* database compatibility;
* test coverage.

A fix must not be copied blindly if the architecture differs between release lines.

---

# 46. Version Control and Database Migrations

Git history and database migration history are related but distinct.

A Git commit should identify the code change.

A migration should identify the schema change.

The repository must maintain a coherent relationship between:

```text id="8tw4bd"
Application Version
        ↓
Migration State
        ↓
Application Compatibility
```

A release must not be considered complete if the application and required database state are incompatible.

---

# 47. Version Control and API Compatibility

API changes should be traceable to the Git version that introduced them.

When compatibility is required, the project should preserve an appropriate transition period.

A release must not silently break required clients without an approved compatibility decision.

---

# 48. Version Control and Documentation

Documentation changes should be committed alongside the relevant implementation whenever practical.

This keeps:

```text id="b6m4h0"
Code
+
Documentation
+
Tests
```

aligned in the same development history.

When documentation intentionally changes separately, the relationship should remain clear.

---

# 49. Version Control and ADRs

Architecture decisions should be version controlled.

The Git history should allow developers to identify:

* when an architectural decision was introduced;
* which implementation followed it;
* whether it was later superseded.

An ADR should not be silently deleted simply because it is no longer current.

Superseded decisions remain part of architectural history.

---

# 50. Tags and Documentation

Release tags should correspond to a coherent documentation state.

If a release changes public behavior, the release should not intentionally point to documentation describing a different behavior.

---

# 51. Branching and Offline Development

Offline-capable application behavior does not imply that Git development must occur offline.

Developers may work locally without network access, but synchronization with the remote repository should happen before integration.

Offline application functionality and Git collaboration are separate concerns.

---

# 52. Branching and Security Changes

Security-sensitive changes should use especially controlled branches.

Examples:

```text id="1z6a7f"
fix/authentication-session
hotfix/authorization-bypass
feature/trusted-device-security
```

Security fixes should receive appropriate testing and review.

A developer must not create a hidden branch or bypass review merely because the change is security-sensitive.

---

# 53. Branching and Financial Changes

Financial changes require increased caution.

Examples:

* payment;
* refund;
* cash session;
* cash handover;
* correction limits;
* reconciliation;
* financial reporting.

Such changes should use focused branches and appropriate testing.

A branch name or commit history must make the affected behavior understandable.

---

# 54. Branching and Inventory Changes

Inventory changes should be isolated enough to verify:

* stock deduction;
* recipe behavior;
* FIFO;
* semi-finished products;
* yield loss;
* adjustments;
* no-negative-stock rules;
* synchronization.

Unrelated inventory changes should not be hidden inside generic refactoring branches.

---

# 55. Branching and Offline Synchronization Changes

Offline and synchronization changes may have cross-layer impact.

A branch may affect:

* local persistence;
* synchronization operations;
* idempotency;
* conflict handling;
* API behavior;
* background processing;
* auditability.

Such branches should be treated as higher-risk changes.

---

# 56. Branching and Permission Changes

Permission changes can affect tenant, branch, role, resource, and action boundaries.

Permission changes should therefore:

* use focused branches;
* include appropriate security tests;
* undergo appropriate review;
* remain traceable.

The branch must not combine permission changes with unrelated UI changes without a clear reason.

---

# 57. Emergency Changes

Emergency changes may require an accelerated path.

However:

> **Emergency does not mean undocumented or untraceable.**

At minimum, an emergency change should retain:

* reason;
* affected version;
* implementation;
* validation evidence;
* reviewer/approver where possible;
* release identifier;
* follow-up action where required.

Any temporary emergency workaround should have a defined follow-up if it creates technical debt.

---

# 58. Recovery from Incorrect Merge

If a merge introduces a defect:

1. identify the affected commit or release;
2. determine whether rollback or forward fix is safer;
3. protect production data integrity;
4. create a corrective change;
5. test the correction;
6. release through the appropriate process;
7. preserve the incident/change history.

Git history should not be rewritten merely to hide an incorrect merge.

---

# 59. Reverting Changes

Reverting a change should normally create a new version-controlled change rather than rewriting shared history.

A revert should:

* clearly identify what is being reversed;
* preserve the original history;
* pass appropriate tests;
* consider database and migration implications.

A database migration cannot always be safely “reverted” by simply reversing the Git commit.

Database recovery must follow the database migration and deployment strategy.

---

# 60. Git History as Evidence

Git history should be useful for answering:

* Who introduced this behavior?
* When was it introduced?
* Why was it introduced?
* Which release contained it?
* Which PR reviewed it?
* Which ADR supported it?
* Which tests were added?

Therefore, history should remain understandable rather than optimized only for visual appearance.

---

# 61. Repository Recovery

The repository should support recovery from:

* accidental local changes;
* deleted branches;
* failed merges;
* incorrect releases;
* corrupted development branches.

Important recovery references include:

* Git commits;
* tags;
* pull requests;
* release artifacts;
* deployment records.

Developers should not assume that deleting a branch means its history is irrecoverable.

---

# 62. Protected History

The following history should be treated as protected:

* released tags;
* production release commits;
* merged shared history;
* important architecture decisions;
* migration history.

History may be extended with corrective changes, but should not be rewritten simply to make it cleaner.

---

# 63. Branch Permissions

Repository access should follow the security model.

Not every developer should necessarily be allowed to:

* force push;
* delete protected branches;
* create release tags;
* publish releases;
* modify repository protection;
* bypass required checks.

Access should follow role and responsibility.

---

# 64. Version Control and AI-Assisted Development

AI-assisted development does not change Git responsibility.

AI-generated changes must still:

* belong to an intentional branch;
* be reviewable;
* pass tests;
* follow repository conventions;
* have appropriate documentation;
* preserve traceability.

AI tools must not create uncontrolled direct changes to stable branches.

---

# 65. Branch Cleanup Policy

After successful merge:

```text id="3u1w7p"
Merged Branch
     ↓
Verify Release/Integration State
     ↓
Delete Obsolete Branch
     ↓
Retain History
```

Branches should not be kept indefinitely without a purpose.

However, active release and maintenance branches must not be deleted while they remain supported.

---

# 66. Recommended Normal Workflow

The standard development flow is:

```text id="q1z6pc"
main
  ↓
Create feature/fix/refactor branch
  ↓
Implement
  ↓
Commit
  ↓
Push
  ↓
Open Pull Request
  ↓
Automated Checks
  ↓
Code Review
  ↓
Corrections
  ↓
Approval
  ↓
Merge
  ↓
Delete Branch
```

For releases:

```text id="4y7xqk"
main
  ↓
Create release branch
  ↓
Stabilize
  ↓
Release Validation
  ↓
Tag Version
  ↓
Deploy
  ↓
Merge Required Release Changes Back
  ↓
Close Release Branch
```

For emergencies:

```text id="j8f0ds"
Released Version
  ↓
Create Hotfix Branch
  ↓
Focused Correction
  ↓
Critical Testing
  ↓
Review
  ↓
Patch Release
  ↓
Deploy
  ↓
Merge Fix Back
```

---

# 67. Branch Decision Guide

| Change                        | Branch       |
| ----------------------------- | ------------ |
| New product behavior          | `feature/*`  |
| Bug correction                | `fix/*`      |
| Internal restructuring        | `refactor/*` |
| Developer/tooling maintenance | `chore/*`    |
| Release stabilization         | `release/*`  |
| Urgent production correction  | `hotfix/*`   |

If a change fits multiple categories, the developer should select the category that best represents its primary purpose.

---

# 68. Version Control Checklist

Before merging a branch:

### Branch

* [ ] Branch name is descriptive.
* [ ] Branch has one primary purpose.
* [ ] Branch is based on the correct baseline.
* [ ] Branch is sufficiently synchronized.

### Implementation

* [ ] Required implementation is complete.
* [ ] No unrelated changes are included.
* [ ] Database changes are included where required.
* [ ] API changes are included where required.
* [ ] Documentation is synchronized where required.

### Validation

* [ ] Relevant tests pass.
* [ ] Required CI checks pass.
* [ ] Security impact has been considered.
* [ ] Migration impact has been considered.
* [ ] Release impact has been considered.

### History

* [ ] Commits are understandable.
* [ ] No accidental secrets are present.
* [ ] No temporary artifacts are committed.
* [ ] No unsafe history rewrite has occurred.

---

# 69. Release Checklist

Before creating a release tag:

* [ ] Release branch or release baseline is identified.
* [ ] Version number is confirmed.
* [ ] Required tests pass.
* [ ] Database migrations are validated.
* [ ] API compatibility is validated where required.
* [ ] Security checks are complete.
* [ ] Release documentation is ready.
* [ ] Deployment requirements are known.
* [ ] Rollback/recovery considerations are known.
* [ ] Release approval is complete.
* [ ] Exact release commit is identified.
* [ ] Git tag is created from the verified state.

---

# 70. Version Control Invariants

The following rules are mandatory:

1. `main` is treated as a protected stable branch.
2. Significant development should occur on dedicated branches.
3. Branches should have one primary logical purpose.
4. Branch names must be descriptive.
5. Shared history must not be rewritten casually.
6. Protected branches must not be force-pushed.
7. Released tags must remain immutable.
8. Production releases must be identifiable by version and tag.
9. Release branches must contain only release-relevant changes.
10. Hotfix branches must remain focused.
11. Hotfixes must be synchronized back into active development.
12. Merges must pass required validation.
13. Merge conflicts must be resolved based on behavior, not blindly.
14. Rebase must not rewrite shared history without coordination.
15. Obsolete branches may be deleted without deleting their preserved history.
16. Database migrations must remain traceable to application changes.
17. API changes must remain traceable to their implementation.
18. Documentation changes must remain synchronized with documented behavior.
19. ADR history must remain preserved.
20. Production secrets must never enter Git history.
21. Production data must never be committed.
22. Temporary debugging artifacts must not be committed.
23. Emergency changes must remain traceable.
24. Reverts must preserve shared history.
25. Release versions must identify the exact source state.
26. Versioning must communicate compatibility impact.
27. Multiple supported release branches require explicit ownership.
28. AI-generated changes remain subject to normal Git controls.
29. Git must not be used to bypass review, testing, or security controls.
30. Version control history must remain useful as engineering evidence.

---

# 71. Relationship to Other Development Documents

| Document | Relationship                                 |
| -------- | -------------------------------------------- |
| DEV-01   | Defines the overall development workflow     |
| DEV-02   | Defines repository structure and naming      |
| DEV-04   | Defines commit messages and change standards |
| DEV-05   | Defines pull requests and code review        |
| DEV-08   | Defines database migration workflow          |
| DEV-09   | Defines API contract changes                 |
| DEV-10   | Defines documentation-first development      |
| DEV-11   | Defines ADR workflow                         |
| DEV-13   | Defines testing and debugging                |
| DEV-18   | Defines development guardrails               |

DEV-03 establishes the version-control lifecycle; it does not replace the detailed rules in those documents.

---

# 72. Relationship to Testing and Deployment

Git branching does not replace testing or deployment governance.

A branch being merged does not automatically mean that it is production-ready.

The lifecycle remains:

```text id="c5u2yp"
Branch
  ↓
Implementation
  ↓
Testing
  ↓
Review
  ↓
Integration
  ↓
Release Validation
  ↓
Deployment
```

Testing requirements are defined in `12_Testing`.

Deployment requirements are defined in `10_Deployment`.

---

# 73. Acceptance Criteria

This document is considered complete when:

* version control principles are defined;
* main branch policy is defined;
* feature/fix/refactor/chore branches are defined;
* release branches are defined;
* hotfix branches are defined;
* branch naming is defined;
* branch lifecycle is defined;
* merge policy is defined;
* protected branch rules are defined;
* conflict resolution rules are defined;
* rebase and force-push rules are defined;
* branch cleanup is defined;
* semantic versioning is defined;
* release tags are defined;
* release traceability is defined;
* hotfix versioning is defined;
* backporting is defined;
* emergency changes are addressed;
* repository recovery principles are defined;
* version-control invariants are defined.

---

# 74. Final Version Control Rule

The FastFood ERP Git strategy is based on the following principle:

> **Every meaningful change must be isolated, reviewable, traceable, testable, and connected to a known project state.**

The expected lifecycle is:

```text id="d6t4ak"
Create
  ↓
Develop
  ↓
Validate
  ↓
Review
  ↓
Merge
  ↓
Release
  ↓
Tag
  ↓
Maintain
```

Git history must provide a trustworthy record of how the system evolved.

The objective is not to create a complicated branching model.

The objective is to maintain a **simple, controlled, traceable, and recoverable development history** that supports safe development and reliable releases.

