# 17. Developer Tooling and Automation

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the architecture, standards, and development workflow for developer tooling and automation used by the FastFood ERP project.

It covers:

* development scripts;
* formatting;
* linting;
* static analysis;
* pre-commit checks;
* local automation;
* code-quality automation;
* test automation helpers;
* database and environment utilities;
* repository maintenance tools;
* developer workflow automation;
* CI-compatible developer checks;
* safe automation boundaries;
* tool configuration;
* failure handling;
* tool ownership and maintenance.

The purpose is to make repetitive development tasks reliable, reproducible, fast, and consistent without allowing automation to bypass architectural, security, testing, or review requirements.

---

# 2. Scope

This document applies to developer-facing tools and automation used during:

* local development;
* code formatting;
* linting;
* static analysis;
* testing;
* database development;
* API development;
* frontend development;
* repository maintenance;
* documentation validation;
* pre-commit validation;
* pull request preparation;
* CI preparation;
* release preparation.

It does not define:

* production deployment architecture;
* CI/CD architecture in full;
* application business rules;
* production runtime operations;
* security policy;
* testing strategy in full;
* database architecture in full.

Those responsibilities belong to the corresponding documentation sections.

---

# 3. Core Principles

Developer tooling follows these principles:

1. **Automation must support engineering rules, not replace them.**
2. **Tools must be reproducible.**
3. **Tool behavior must be documented.**
4. **Formatting should be deterministic.**
5. **Linting should identify actionable problems.**
6. **Automated checks must not hide real failures.**
7. **Local checks should align with CI checks.**
8. **Automation must be safe to run repeatedly.**
9. **Scripts must avoid destructive behavior by default.**
10. **Production credentials must never be required for ordinary development tooling.**
11. **Developer tools must respect repository architecture.**
12. **Tool configuration is part of the project source of truth.**
13. **Automation must fail clearly when prerequisites are missing.**
14. **Tools should reduce repetitive work without creating hidden behavior.**
15. **Generated artifacts must have explicit ownership and lifecycle.**
16. **Tooling changes must be reviewed like other code changes.**

---

# 4. Developer Tooling Model

Developer tooling is organized into several categories.

```text
Developer Tooling
│
├── Formatting
│   ├── Backend formatter
│   ├── Frontend formatter
│   └── Documentation formatting
│
├── Linting
│   ├── Backend linting
│   ├── Frontend linting
│   ├── Import rules
│   └── Configuration validation
│
├── Static Analysis
│   ├── Type checking
│   ├── Security analysis
│   ├── Dependency analysis
│   └── Architecture checks
│
├── Testing Tools
│   ├── Test runners
│   ├── Fixtures
│   ├── Test environment helpers
│   └── Coverage tools
│
├── Repository Scripts
│   ├── Setup
│   ├── Validation
│   ├── Database helpers
│   ├── Development server helpers
│   └── Maintenance
│
├── Git Automation
│   ├── Pre-commit
│   ├── Commit validation
│   └── Repository checks
│
└── Documentation Tools
    ├── Link validation
    ├── Structure validation
    └── Documentation consistency checks
```

The exact tools may change over time. The engineering responsibilities must remain stable.

---

# 5. Tool Selection Principles

A tool should be introduced when it provides meaningful engineering value.

Before adding a tool, consider:

* what problem it solves;
* whether an existing tool already solves the problem;
* whether it duplicates another check;
* execution time;
* maintenance cost;
* developer experience;
* CI compatibility;
* platform compatibility;
* security implications;
* configuration complexity;
* failure behavior.

A tool should not be added simply because it is popular.

---

# 6. Repository Tooling Location

Developer tools should have predictable locations.

A conceptual structure is:

```text
repository/
├── scripts/
│   ├── setup/
│   ├── development/
│   ├── database/
│   ├── testing/
│   ├── validation/
│   └── maintenance/
│
├── tools/
│   ├── lint/
│   ├── format/
│   ├── validation/
│   └── development/
│
├── backend/
├── frontend/
├── tests/
├── migrations/
├── docs/
├── infrastructure/
│
├── pyproject.toml
├── package.json
├── .pre-commit-config.yaml
└── AGENTS.md
```

The physical structure may evolve.

The important rule is that developer automation must have a discoverable and documented home.

---

# 7. Script Responsibilities

Scripts should perform explicit, narrowly defined tasks.

Examples include:

```text
scripts/
├── setup/
│   └── bootstrap-development
├── development/
│   ├── start-backend
│   ├── start-frontend
│   └── start-workers
├── database/
│   ├── migrate
│   ├── reset-development-db
│   └── seed-development-data
├── testing/
│   ├── run-unit-tests
│   └── run-integration-tests
├── validation/
│   ├── validate-repository
│   └── validate-documentation
└── maintenance/
    └── cleanup-development-artifacts
```

A script should have one clear purpose.

Avoid scripts that silently perform unrelated operations.

For example, a command named:

```text
setup-development
```

should not unexpectedly:

* delete databases;
* modify production resources;
* change Git history;
* install unrelated global software;
* overwrite developer configuration without warning.

---

# 8. Script Design

Scripts must be:

* deterministic;
* documented;
* idempotent where practical;
* safe by default;
* explicit about destructive operations;
* compatible with supported environments;
* clear about prerequisites;
* clear about failure;
* easy to inspect.

Scripts should return meaningful exit codes.

General convention:

```text
0 = success
non-zero = failure
```

A script must not return success when an important operation failed.

---

# 9. Destructive Script Operations

Destructive operations require explicit protection.

Examples:

* deleting development databases;
* removing generated files;
* resetting local state;
* deleting local queues;
* clearing caches;
* removing test data.

Prefer explicit commands such as:

```text
reset-development-db
```

over hiding destructive behavior inside:

```text
start-development
```

Dangerous operations should require deliberate developer intent.

Production resources must never be targeted by ordinary local development scripts.

---

# 10. Script Arguments and Configuration

Scripts should prefer explicit arguments and validated configuration.

For example:

```text
test --scope unit
test --scope integration
database migrate
database seed --environment development
```

Avoid scripts that depend on undocumented shell state.

Required configuration should be validated before execution.

If a required variable is missing, the script should report:

* the missing variable;
* why it is required;
* which environment is expected;
* how the developer can configure it.

Secrets must never be printed.

---

# 11. Cross-Platform Considerations

The project should define supported developer environments.

Where practical, tooling should work consistently across supported environments.

Platform-specific behavior should be isolated.

Avoid relying unnecessarily on:

* undocumented shell features;
* machine-specific paths;
* globally installed software;
* user-specific directories;
* platform-specific commands without alternatives.

If a platform-specific tool is required, the requirement must be documented.

---

# 12. Formatting

Formatting should be automated and deterministic.

Formatting exists to provide:

* consistent source layout;
* reduced review noise;
* predictable code structure;
* easier collaboration;
* simpler automated analysis.

Developers should not manually debate formatting decisions that can be enforced automatically.

---

# 13. Formatting Ownership

Each language or artifact type should have a defined formatting mechanism.

Conceptually:

```text
Python       → project-approved formatter
Frontend     → project-approved formatter
JSON         → deterministic formatter
YAML         → deterministic formatter
Markdown     → project-approved formatting rules
```

The actual tool may change.

The repository configuration is the source of truth.

---

# 14. Formatting Rules

Formatting tools should be configured centrally where practical.

Developers should not maintain personal formatting configurations that contradict the repository standard.

Formatting should be applied:

* before commit;
* before review;
* automatically where practical;
* consistently in CI.

Formatting-only changes should remain separate from unrelated behavioral changes when doing so improves reviewability.

---

# 15. Formatting and Generated Files

Generated files require explicit rules.

If generated files are committed:

* their generation process must be documented;
* formatting rules must be known;
* source files must remain authoritative;
* generated output must not become an accidental source of truth.

If generated files are not committed:

* they should normally be excluded from formatting and linting;
* regeneration must be reproducible.

---

# 16. Linting

Linting identifies code patterns that may indicate:

* defects;
* maintainability problems;
* architectural violations;
* unused code;
* unsafe patterns;
* inconsistent practices.

Linting is not a substitute for testing.

A clean lint result does not prove business correctness.

---

# 17. Linting Categories

Linting may cover:

```text
Code style
Imports
Unused code
Type-related problems
Potential bugs
Security-sensitive patterns
Complexity
Naming
Architecture boundaries
Frontend rules
Configuration errors
Documentation structure
```

Rules should be selected based on project value.

Avoid enabling large numbers of low-value warnings that developers learn to ignore.

---

# 18. Warning and Error Policy

Lint findings should have explicit severity.

Conceptually:

```text
Error
  → blocks completion

Warning
  → requires attention but may not block every workflow

Informational
  → optional guidance
```

Critical correctness or security rules should not be treated as optional warnings.

The severity model must be consistent across local and CI environments.

---

# 19. Static Analysis

Static analysis should complement:

* tests;
* code review;
* runtime validation;
* security review.

Potential checks include:

* type correctness;
* unreachable code;
* unsafe API usage;
* dependency vulnerabilities;
* import boundaries;
* configuration errors;
* suspicious patterns;
* complexity;
* architecture violations.

Static analysis must remain aligned with the project's actual architecture.

---

# 20. Type Checking

Where static typing is used, type checking should be part of normal development validation.

Developers should not suppress type errors without justification.

If suppression is necessary:

* the reason should be clear;
* the scope should be minimal;
* the suppression should not hide unrelated errors.

Global disabling of useful type checks is discouraged.

---

# 21. Architecture Validation

Developer tooling may enforce architectural boundaries.

Examples:

```text
Domain
  ↓
Application
  ↓
Infrastructure
```

and:

```text
Frontend
  ↓
API
  ↓
Application
  ↓
Domain
```

Tools should prevent accidental dependencies that violate documented architecture when such checks can be reliably automated.

Architecture validation does not replace architecture review.

---

# 22. Pre-Commit Validation

Pre-commit automation provides fast local feedback before changes enter shared history.

A typical flow is:

```text
Developer changes code
        ↓
Format
        ↓
Lint
        ↓
Static checks
        ↓
Focused tests
        ↓
Commit
```

Pre-commit checks should be:

* fast enough for normal development;
* deterministic;
* local;
* safe;
* reproducible.

---

# 23. Pre-Commit Responsibilities

Pre-commit checks may include:

* formatting;
* linting;
* import validation;
* syntax validation;
* secret detection;
* basic static analysis;
* documentation checks;
* small focused tests.

Heavy integration or end-to-end tests should generally remain outside ordinary pre-commit hooks unless execution time is acceptable.

---

# 24. Pre-Commit Failure

When a pre-commit check fails:

1. identify the failing tool;
2. inspect the reported problem;
3. fix the underlying issue;
4. rerun the failed check;
5. rerun broader checks when appropriate;
6. commit only after the expected checks pass.

Developers must not routinely bypass hooks to make a commit succeed.

Bypassing a check may be permitted only for an explicitly understood exceptional situation and must not become normal workflow.

---

# 25. Commit Hooks and CI

Local hooks and CI checks should overlap where useful.

The goal is:

```text
Local validation
      ↓
Pull request validation
      ↓
Release validation
```

not three unrelated validation systems.

Local checks should be optimized for speed.

CI should provide authoritative shared validation.

---

# 26. Test Automation Helpers

Developer tooling may provide commands for common testing tasks.

Examples:

```text
test
test-unit
test-domain
test-api
test-integration
test-e2e
test-offline
test-security
test-coverage
```

The exact command structure may differ.

Commands should map clearly to the testing architecture defined in `docs/12_Testing`.

---

# 27. Database Development Automation

Database scripts may provide:

* migration execution;
* migration status;
* development database initialization;
* test database initialization;
* seed loading;
* safe local reset;
* schema validation.

Database automation must respect:

* migration ordering;
* transaction behavior;
* data preservation;
* environment boundaries;
* test isolation.

A local reset command must never accidentally target production.

---

# 28. Development Environment Automation

Automation may simplify developer setup.

Examples:

```text
bootstrap-development
install-dependencies
initialize-development
start-backend
start-frontend
start-worker
check-environment
```

Setup automation should:

1. verify prerequisites;
2. install project dependencies;
3. configure local environment;
4. initialize required local services;
5. validate configuration;
6. report remaining manual steps.

Setup scripts should not silently create insecure production-like credentials.

---

# 29. Service Startup Automation

If multiple local services are required, a developer command may coordinate them.

For example:

```text
Backend
Frontend
PostgreSQL
Redis
Worker
Scheduler
```

The automation should clearly report:

* which services started;
* which ports are used;
* which service failed;
* where logs are available;
* how to stop services.

A failed dependency must not be presented as a healthy development environment.

---

# 30. Environment Validation

A validation command should be able to check common prerequisites.

Conceptually:

```text
check-environment
```

may validate:

* supported runtime versions;
* dependency availability;
* environment configuration;
* database connectivity;
* Redis connectivity;
* required local tools;
* migration state;
* frontend dependencies;
* backend dependencies.

Validation should distinguish:

```text
PASS
WARNING
FAIL
```

rather than hiding problems.

---

# 31. Documentation Automation

Developer tooling may validate documentation.

Possible checks include:

* broken internal links;
* duplicate filenames;
* missing required sections;
* invalid Markdown;
* inconsistent document references;
* stale index entries;
* ADR numbering conflicts;
* missing parent references.

Documentation automation should support the documentation-first workflow.

It must not automatically rewrite accepted architectural decisions without review.

---

# 32. Repository Validation

A repository validation command may check:

```text
Repository structure
Required files
Git state
Formatting
Linting
Type checks
Tests
Documentation links
Configuration
Generated artifacts
```

A conceptual command may be:

```text
validate-repository
```

The command should provide actionable output.

---

# 33. Automation Composition

Higher-level commands may compose smaller commands.

For example:

```text
validate
 ├── format-check
 ├── lint
 ├── type-check
 ├── unit-test
 └── documentation-check
```

Composition is useful when the underlying commands remain independently executable.

Avoid a single giant script that hides all individual operations.

---

# 34. Automation Output

Tool output should be:

* readable;
* actionable;
* deterministic;
* appropriately detailed;
* clear about success and failure.

Errors should identify:

1. what failed;
2. where it failed;
3. why it likely failed;
4. what command or action can help diagnose it.

Avoid output that contains secrets, tokens, passwords, or sensitive production data.

---

# 35. Logging for Developer Tools

Developer tooling may produce logs for complex operations.

Logs should help answer:

* what operation ran;
* what environment was targeted;
* what major steps completed;
* where execution failed.

Logs should not expose:

* passwords;
* authentication tokens;
* private keys;
* production secrets;
* sensitive customer information.

---

# 36. Caching

Developer tooling may use caches to improve speed.

Examples:

* dependency caches;
* build caches;
* test caches;
* lint caches.

Caching must not compromise correctness.

When cache state may cause misleading results, tools must provide a documented cache-clear mechanism.

Example:

```text
clean-development-cache
```

---

# 37. Parallel Automation

Independent checks may run in parallel when safe.

For example:

```text
Lint ─────────┐
Type check ───┼──→ Result
Docs check ───┤
Unit tests ───┘
```

Parallel execution must not introduce:

* shared-state races;
* database corruption;
* nondeterministic results;
* conflicting temporary files.

Tests that share mutable resources must use proper isolation.

---

# 38. Automation and Concurrency

Automation that modifies shared resources must consider concurrency.

Examples:

* two developers running database reset scripts;
* parallel test workers;
* multiple processes writing the same generated file;
* simultaneous migration commands;
* multiple automation commands using the same local port.

Tools should fail clearly rather than silently corrupt shared local state.

---

# 39. Dependency Management for Tools

Developer tools are dependencies too.

Tool versions should be controlled where reproducibility requires it.

Examples include:

* formatters;
* linters;
* test runners;
* static analyzers;
* pre-commit hooks;
* documentation validators.

A developer should not receive materially different results simply because a globally installed tool happens to be newer.

---

# 40. Tool Configuration

Tool configuration should live in version-controlled project configuration where practical.

Configuration should define:

* enabled rules;
* ignored paths;
* severity;
* formatting behavior;
* execution scope;
* compatibility;
* exceptions.

Configuration changes are code-quality changes and require review.

---

# 41. Ignored Paths

Tools should explicitly ignore files that should not be analyzed.

Typical examples may include:

```text
.git/
node_modules/
virtual environments/
build/
dist/
coverage/
temporary files/
generated artifacts/
local caches/
```

The exact list depends on the project.

Ignored paths must not accidentally hide source code that should be validated.

---

# 42. Tool Exceptions

Exceptions should be narrow.

A good exception explains:

* what is being excluded;
* why;
* what risk remains;
* whether the exception is temporary.

Avoid broad rules such as:

```text
ignore entire directory
disable all security checks
disable linting for backend
```

unless there is a documented architectural reason.

---

# 43. Automation and Security

Developer automation is part of the security boundary.

Scripts must:

* validate inputs;
* avoid shell injection risks;
* avoid arbitrary command execution from untrusted input;
* protect secrets;
* avoid production access;
* avoid unsafe default permissions;
* avoid downloading and executing unknown code without explicit intent.

External repositories, downloaded scripts, and generated commands must not automatically be treated as trusted.

---

# 44. Secret Detection

Developer tooling should detect accidental secret exposure where practical.

Possible targets include:

* API keys;
* tokens;
* passwords;
* private keys;
* credentials;
* connection strings.

Secret detection should operate before changes enter shared history where practical.

A detected secret must be treated as a security issue, not merely a formatting problem.

---

# 45. Production Safety

Ordinary developer tooling must not require production access.

The preferred model is:

```text
Local tooling
    ↓
Development resources
```

not:

```text
Local tooling
    ↓
Production resources
```

If an operational tool genuinely requires production access, it belongs under the operations/deployment security model and must have stronger controls.

---

# 46. AI-Assisted Tooling

AI may be used to:

* generate scripts;
* improve automation;
* diagnose tool failures;
* propose lint configuration;
* generate test commands;
* document scripts.

AI-generated automation must be reviewed before use.

Particular attention is required for scripts that:

* delete data;
* execute shell commands;
* modify Git history;
* alter databases;
* access credentials;
* install dependencies;
* modify infrastructure.

The rules in:

```text
16_AI_Assisted_Development_Guidelines.md
```

apply.

---

# 47. Automation and Git

Developer automation should integrate naturally with Git.

Possible commands include:

```text
check-working-tree
validate-commit
prepare-commit
validate-branch
```

Automation must not silently:

* rewrite unrelated files;
* create commits;
* push branches;
* delete branches;
* rewrite history.

Git-changing automation requires explicit developer intent.

---

# 48. Formatting Before Review

Before opening a pull request, developers should normally ensure:

```text
Format
   ↓
Lint
   ↓
Type/static checks
   ↓
Focused tests
   ↓
Broader tests as required
   ↓
Review
```

This reduces avoidable review noise.

---

# 49. Tooling in Pull Requests

Pull request automation should validate the same engineering rules that developers can reasonably validate locally.

Typical checks:

* formatting;
* linting;
* type checks;
* tests;
* security checks;
* documentation checks;
* migration checks;
* build validation.

CI remains authoritative because local environments can differ.

---

# 50. Tooling and Release Validation

Release automation may reuse developer tooling.

For example:

```text
validate
    ↓
release checks
    ↓
build
    ↓
release candidate
```

Release-specific validation must not depend solely on local tooling.

The deployment and release documentation remains authoritative for production release behavior.

---

# 51. Tooling Performance

Developer tools must balance correctness and speed.

Fast checks should run frequently.

Slow checks should run:

* on demand;
* before pull requests;
* in CI;
* before release;
* according to risk.

Do not make every commit wait unnecessarily for heavyweight operations.

At the same time, performance optimization must not remove important validation.

---

# 52. Incremental Validation

Tooling should support focused validation.

Examples:

```text
lint backend/orders
test orders
test inventory
check changed documentation
```

Focused validation helps developers iterate quickly.

Full validation remains necessary for appropriate changes.

---

# 53. Changed-File Detection

Automation may detect changed files and select relevant checks.

For example:

```text
Backend change
    → backend formatting
    → backend linting
    → relevant tests

Frontend change
    → frontend formatting
    → frontend linting
    → relevant tests

Migration change
    → migration validation
    → database tests
    → affected application tests
```

Changed-file detection must not incorrectly skip cross-cutting checks.

---

# 54. Failure Classification

Automation failures should be classified.

Examples:

```text
Code failure
Tool failure
Environment failure
Dependency failure
Configuration failure
Infrastructure failure
Test failure
Flaky behavior
```

Developers must not modify application code merely to make a broken tool pass.

The root cause should be identified first.

---

# 55. Flaky Tooling

Developer tooling should be deterministic.

Repeated execution with the same source and environment should normally produce the same result.

If a tool is flaky:

1. reproduce the problem;
2. identify the source;
3. isolate the failing component;
4. fix or replace the tool;
5. document any temporary workaround.

Flaky validation must not become accepted normal behavior.

---

# 56. Tool Maintenance

Developer tools require maintenance.

Maintenance includes:

* dependency updates;
* configuration updates;
* rule review;
* compatibility testing;
* performance review;
* security review;
* obsolete-tool removal.

Unused tools should be removed rather than left as confusing repository infrastructure.

---

# 57. Tool Ownership

Every important developer tool should have an identifiable ownership area.

Ownership means responsibility for:

* configuration;
* compatibility;
* failures;
* updates;
* documentation;
* removal when obsolete.

Ownership does not mean that only one developer may modify the tool.

---

# 58. Adding a New Tool

Before introducing a new tool, document:

```text
Problem
Why existing tools are insufficient
Expected benefit
Scope
Configuration
Developer impact
CI impact
Security impact
Maintenance cost
```

The tool should then be introduced through the normal development and review workflow.

Architecture-significant tooling decisions may require an ADR.

---

# 59. Removing a Tool

Before removing a tool:

1. identify its current uses;
2. identify dependent scripts;
3. identify CI usage;
4. identify documentation references;
5. confirm replacement or removal of the requirement;
6. remove obsolete configuration;
7. update documentation;
8. validate the resulting workflow.

Dead configuration should not remain after tool removal.

---

# 60. Tool Version Upgrades

Tool upgrades should be treated as controlled changes.

Consider:

* changed defaults;
* new warnings;
* removed rules;
* output changes;
* compatibility;
* performance;
* CI differences;
* developer workflow impact.

A formatter upgrade may create large diffs.

Such changes should be isolated when practical.

---

# 61. Large Formatting Changes

When changing formatting rules or formatter versions:

1. update configuration;
2. validate the new tool;
3. apply formatting consistently;
4. review the resulting diff;
5. separate mass formatting from behavioral changes when practical;
6. update CI and local instructions.

Do not mix a massive formatting migration with unrelated feature development unless necessary.

---

# 62. Generated Code and Automation

Generated source must have a known source.

For example:

```text
Source definition
      ↓
Generator
      ↓
Generated artifact
```

Developers must modify the source definition rather than manually editing generated output when regeneration would overwrite the change.

---

# 63. Automation Idempotency

Repeated execution should be safe whenever practical.

For example:

```text
setup-development
```

should not break an already configured environment merely because it is run twice.

For operations that cannot be idempotent, the behavior must be explicit.

---

# 64. Local State Cleanup

Automation may provide cleanup commands.

Examples:

```text
clean
clean-build
clean-cache
clean-test-data
```

Cleanup should be scoped clearly.

A generic:

```text
clean
```

must not unexpectedly delete valuable developer data.

---

# 65. Tooling and Offline Development

Developer tooling should support the project's offline-capable architecture without requiring production connectivity.

Offline-related development tools may help test:

* local synchronization;
* queued operations;
* conflict scenarios;
* network interruption;
* retry behavior.

The tooling itself must not assume that every application test has unrestricted network access.

---

# 66. Tooling and Performance Testing

Performance tools may provide:

* benchmark commands;
* load-test entry points;
* database profiling;
* frontend bundle analysis;
* API timing;
* worker timing.

Performance tooling must produce reproducible evidence where possible.

Performance results should not be treated as universal unless environment and test conditions are known.

---

# 67. Tooling and Observability

Developer tools may expose local diagnostics for:

* application logs;
* worker status;
* queue state;
* database connectivity;
* cache state;
* service health.

Local diagnostic tooling must respect sensitive-data restrictions.

---

# 68. Tooling and Error Recovery

Automation should provide safe recovery paths.

Examples:

```text
reset-test-environment
rebuild-local-assets
clear-development-cache
restart-local-services
recreate-test-database
```

Recovery commands must clearly distinguish:

```text
repair
reset
delete
```

so developers understand the consequences.

---

# 69. Automation Documentation

Every non-obvious tool or script should have documentation covering:

* purpose;
* command;
* prerequisites;
* expected output;
* failure behavior;
* environment;
* destructive behavior;
* recovery;
* ownership if necessary.

The repository README and development documentation should provide discoverability.

---

# 70. Developer Command Interface

Where practical, the project should provide a consistent command interface.

Conceptually:

```text
setup
start
stop
format
format-check
lint
type-check
test
validate
clean
database
docs
```

The exact interface may differ.

The objective is discoverability and consistency rather than a specific command framework.

---

# 71. Makefiles, Task Runners, and Wrappers

A project may use:

* Make;
* Python task runners;
* shell scripts;
* package manager scripts;
* task orchestration tools.

The chosen mechanism should be consistent.

Do not introduce multiple competing command systems without a clear reason.

For example, developers should not need to remember three different commands for the same validation workflow.

---

# 72. Environment-Aware Commands

Commands should clearly indicate the environment they target.

Prefer:

```text
database migrate --environment development
```

over commands whose target is ambiguous.

Production-targeting commands should not be exposed through ordinary developer shortcuts unless explicitly controlled.

---

# 73. Automation Safety Checks

High-risk commands should validate their target.

For example, a destructive database reset may verify:

```text
environment == development
```

before proceeding.

The safety check should fail closed.

---

# 74. Automation and Permissions

Developer tooling should operate with the minimum permissions necessary.

Avoid:

* unnecessary root privileges;
* administrator privileges;
* production credentials;
* broad filesystem access.

If elevated permissions are genuinely required, the reason must be documented.

---

# 75. Tooling and Dependency Installation

Automation that installs dependencies should use the project's approved dependency workflow.

It must not silently install:

* unrelated global packages;
* unapproved dependencies;
* unreviewed development services;
* arbitrary remote binaries.

Dependency changes remain subject to `14_Dependency_and_Package_Management.md`.

---

# 76. Tooling and Configuration

Automation should respect the configuration hierarchy defined by the project.

A useful conceptual order is:

```text
Project defaults
      ↓
Environment configuration
      ↓
Local developer overrides
      ↓
Explicit command arguments
```

Secrets must remain outside committed source where required.

---

# 77. Tooling and Feature Flags

Developer tools may support enabling or disabling development features.

However:

* feature flags must not bypass authorization;
* feature flags must not alter financial correctness;
* feature flags must not create hidden production behavior;
* production defaults must remain explicit.

Feature flag development follows:

```text
15_Configuration_and_Feature_Flag_Development.md
```

---

# 78. Tooling and Testing Evidence

Automation should make test results reproducible.

Useful output may include:

```text
Command
Environment
Tool version
Test scope
Result
Duration
Failure location
```

Evidence should be sufficient to understand what was actually validated.

---

# 79. Tooling and Code Review

Reviewers should evaluate developer tooling changes for:

* correctness;
* maintainability;
* security;
* reproducibility;
* developer experience;
* CI compatibility;
* destructive behavior;
* performance;
* documentation.

A script is production-quality engineering infrastructure even if it runs only on developer machines.

---

# 80. Anti-Patterns

Avoid:

### 80.1 Giant Utility Scripts

One script that performs setup, database reset, tests, formatting, deployment, and cleanup.

**Problem:** unclear responsibility and dangerous side effects.

### 80.2 Hidden Destructive Behavior

Commands that delete or reset resources without clear indication.

### 80.3 Global Tool Dependence

Relying on whatever tool version happens to be installed globally.

### 80.4 Ignoring Tool Failures

Continuing after a critical validation step fails.

### 80.5 Permanent Hook Bypasses

Treating skipped checks as normal development workflow.

### 80.6 Excessive Lint Rules

Creating so much noise that developers stop paying attention.

### 80.7 Duplicate Command Systems

Providing several unrelated ways to perform the same task.

### 80.8 Unreviewed Shell Execution

Executing downloaded or AI-generated commands without understanding them.

### 80.9 Production Access from Local Scripts

Allowing normal developer utilities to access production resources.

### 80.10 Tool Configuration Drift

Allowing local, CI, and repository configurations to disagree without justification.

---

# 81. Standard Developer Validation Workflow

A normal developer workflow should conceptually be:

```text
Change code
    ↓
Format
    ↓
Lint
    ↓
Static checks
    ↓
Focused tests
    ↓
Review local diff
    ↓
Commit
    ↓
Pull request
    ↓
CI validation
```

The exact commands may evolve.

The validation intent must remain.

---

# 82. Completion Criteria

Developer tooling work is complete when:

* the tool solves a clearly identified problem;
* configuration is version controlled where appropriate;
* supported environments are known;
* failure behavior is clear;
* security implications are reviewed;
* destructive operations are protected;
* dependencies are controlled;
* documentation is updated;
* local and CI behavior are compatible;
* relevant tests or validation pass;
* obsolete tooling is removed where applicable.

---

# 83. Change Checklist

Before merging tooling changes:

### Design

* [ ] Problem is clearly defined.
* [ ] Existing tools were considered.
* [ ] Scope is clear.
* [ ] Ownership is clear.

### Safety

* [ ] No unnecessary production access.
* [ ] Destructive actions are protected.
* [ ] Secrets are not exposed.
* [ ] Inputs are validated.
* [ ] Permissions are minimized.

### Quality

* [ ] Formatting is deterministic.
* [ ] Linting is actionable.
* [ ] Exit codes are correct.
* [ ] Failures are visible.
* [ ] Tool versions are controlled where necessary.

### Integration

* [ ] Pre-commit behavior is correct.
* [ ] CI behavior is compatible.
* [ ] Existing scripts still work.
* [ ] Documentation is updated.

### Validation

* [ ] Normal workflow tested.
* [ ] Failure workflow tested.
* [ ] Repeated execution tested where applicable.
* [ ] Destructive behavior tested safely.
* [ ] Cross-environment behavior considered.

---

# 84. Relationship to Other Development Documents

This document works with:

* `01_Development_Architecture_Overview.md` — overall development lifecycle;
* `02_Repository_Structure_and_Conventions.md` — repository organization;
* `03_Git_Branching_and_Version_Control_Strategy.md` — Git workflow;
* `04_Commit_Message_and_Change_Standards.md` — commit requirements;
* `05_Pull_Request_and_Code_Review_Process.md` — review workflow;
* `06_Backend_Development_Standards.md` — backend standards;
* `07_Frontend_Development_Standards.md` — frontend standards;
* `08_Database_Development_and_Migration_Workflow.md` — database changes;
* `09_API_Development_and_Contract_Change_Workflow.md` — API changes;
* `10_Documentation_First_Development_Workflow.md` — documentation-first workflow;
* `11_ADR_and_Architecture_Decision_Workflow.md` — architecture decisions;
* `12_Local_Development_Environment.md` — local environment;
* `13_Testing_and_Debugging_Workflow.md` — testing and debugging;
* `14_Dependency_and_Package_Management.md` — dependency management;
* `15_Configuration_and_Feature_Flag_Development.md` — configuration and feature flags;
* `16_AI_Assisted_Development_Guidelines.md` — AI-assisted development;
* `18_Development_Guardrails_and_Quality_Rules.md` — development guardrails.

It also relates to:

* `docs/12_Testing`;
* `docs/10_Deployment`;
* `docs/11_Security`;
* `docs/14_Operations`.

---

# 85. Development Tooling Invariants

The following rules are mandatory unless explicitly superseded by an accepted architecture decision.

1. Developer tooling must support documented engineering rules.
2. Tool configuration must be reproducible.
3. Tool versions must be controlled where reproducibility requires it.
4. Formatting must be deterministic.
5. Formatting must not silently change application behavior.
6. Linting must provide actionable findings.
7. Lint failures must not be silently ignored.
8. Static analysis must complement testing.
9. Pre-commit checks must remain reasonably fast.
10. CI must provide authoritative shared validation.
11. Local and CI validation must not intentionally contradict each other.
12. Scripts must have clear responsibilities.
13. Scripts must return meaningful exit codes.
14. Destructive scripts must require deliberate intent.
15. Production resources must not be targeted by ordinary development scripts.
16. Developer tools must not expose secrets.
17. Tool inputs must be validated.
18. Tool permissions must be minimized.
19. Repeated execution should be safe where practical.
20. Tool failures must be visible.
21. Automation must not hide application failures.
22. Generated files must have a known source of truth.
23. Generated artifacts must not become accidental source code.
24. Tool exceptions must be narrow and justified.
25. Ignored paths must not hide important source code.
26. Tool configuration changes require review.
27. Developer tooling dependencies are subject to dependency management.
28. Developer tooling must respect repository architecture.
29. Database tooling must respect environment boundaries.
30. Test tooling must preserve test isolation.
31. Automation must not bypass authorization or security controls.
32. AI-generated tooling must be reviewed before execution.
33. Downloaded scripts must not automatically be trusted.
34. Git-changing automation must require explicit intent.
35. Local automation must not silently rewrite unrelated work.
36. Documentation automation must not silently change accepted decisions.
37. Tooling failures must be classified before application code is changed.
38. Flaky tooling must be investigated rather than normalized.
39. Obsolete tools and configuration must be removed.
40. Important tooling behavior must be documented.
41. Developer tooling must remain maintainable.
42. Automation must optimize repetitive work without hiding system behavior.
43. High-risk commands must fail closed when safety conditions are not met.
44. Tooling must remain aligned with the project's development architecture.
45. Tooling must improve engineering consistency without becoming an uncontrolled source of complexity.

---

# 86. Final Principle

Developer tooling and automation are part of the engineering system, not merely developer conveniences.

The project should automate repetitive work, enforce consistent quality, provide fast feedback, and make development workflows reproducible while preserving human understanding and control.

The governing principle is:

> **Automate repetitive engineering work, make validation deterministic, keep failures visible, protect destructive operations, and never allow tooling to bypass architecture, security, testing, or review.**

