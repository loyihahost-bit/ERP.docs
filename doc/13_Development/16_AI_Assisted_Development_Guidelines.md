# 16. AI-Assisted Development Guidelines

**Document:** `16_AI_Assisted_Development_Guidelines.md`
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines how AI coding tools may be used safely and effectively during software development.

It establishes rules for:

* AI-assisted coding;
* code generation;
* code modification;
* refactoring;
* debugging;
* test generation;
* documentation generation;
* dependency recommendations;
* architecture assistance;
* AI context management;
* generated-code validation;
* security review;
* code review;
* testing;
* Git and pull requests;
* sensitive information handling;
* hallucination prevention;
* production safety.

The goal is to use AI as an engineering assistant while keeping humans responsible for correctness, architecture, security, business behavior, and final decisions.

---

## 2. Scope

This document applies to developers using:

* AI coding assistants;
* AI-powered IDE features;
* code-generation systems;
* repository-aware AI tools;
* conversational coding agents;
* AI debugging tools;
* AI refactoring tools;
* AI documentation assistants;
* AI test-generation tools.

It applies to:

* backend code;
* frontend code;
* database code;
* API code;
* infrastructure code;
* configuration;
* tests;
* documentation;
* scripts;
* automation;
* AI/ML integration code.

---

## 3. Core Principle

AI-generated code is treated as **untrusted generated input until validated**.

The engineering model is:

```text
Human intent
    ↓
AI assistance
    ↓
Generated proposal
    ↓
Human understanding
    ↓
Validation
    ↓
Testing
    ↓
Code review
    ↓
Approved implementation
```

AI must not become an uncontrolled source of production behavior.

---

## 4. Human Responsibility

Developers remain responsible for:

* understanding generated code;
* validating correctness;
* checking architecture;
* checking security;
* checking business rules;
* checking data integrity;
* running tests;
* reviewing dependencies;
* reviewing configuration;
* approving changes.

The statement:

> "The AI generated it."

is never sufficient justification for incorrect behavior.

---

## 5. AI Is an Assistant, Not an Authority

AI may provide:

* suggestions;
* implementations;
* alternatives;
* explanations;
* hypotheses;
* test cases;
* documentation drafts.

AI does not automatically determine:

* project architecture;
* business requirements;
* security policy;
* legal requirements;
* production readiness;
* database correctness;
* API compatibility;
* dependency trustworthiness.

Authoritative project decisions come from approved project documentation and engineering review.

---

## 6. Source of Truth

When using AI in the project, the source-of-truth hierarchy should be:

```text
Approved requirements
        ↓
Approved domain/system analysis
        ↓
Approved architecture
        ↓
Approved ADRs
        ↓
Approved technical documentation
        ↓
Existing validated implementation
        ↓
AI suggestions
```

AI suggestions must not silently override higher-level project decisions.

---

## 7. Context Before Code

AI should receive sufficient project context before generating significant code.

Relevant context may include:

* requirements;
* architecture;
* domain rules;
* API contracts;
* database model;
* security rules;
* testing requirements;
* existing implementation;
* related documentation.

The more significant the change, the more important correct context becomes.

---

## 8. Avoiding Context Guessing

AI must not be expected to guess:

* business rules;
* permission rules;
* tenant boundaries;
* branch boundaries;
* subscription behavior;
* database invariants;
* API contracts.

If the required context is missing, the developer should provide it or ask the AI to identify assumptions explicitly.

---

## 9. Explicit Assumptions

When AI must work with incomplete information, assumptions should be visible.

Example:

```text
Assumption:
The operation is branch-scoped and requires Manager permission.
```

Hidden assumptions are dangerous because generated code may encode them as permanent behavior.

---

## 10. AI Task Classification

AI-assisted changes should be classified by risk.

### Low Risk

Examples:

* formatting;
* simple documentation;
* repetitive test scaffolding;
* trivial refactoring.

### Medium Risk

Examples:

* business logic;
* API changes;
* database queries;
* frontend state changes;
* dependency updates.

### High Risk

Examples:

* authentication;
* authorization;
* financial logic;
* inventory deduction;
* synchronization;
* encryption;
* migrations;
* subscription enforcement;
* security controls;
* production infrastructure.

Higher-risk tasks require stronger human review.

---

## 11. AI-Assisted Architecture Work

AI may help with:

* alternative designs;
* trade-off analysis;
* dependency analysis;
* architecture review;
* identifying missing concerns.

AI-generated architecture must be evaluated against:

* project requirements;
* existing architecture;
* scalability;
* performance;
* security;
* maintainability;
* operational constraints.

Significant architectural decisions must still be recorded through the ADR process.

---

## 12. AI-Assisted Business Logic

AI may generate business logic, but business rules must come from approved requirements and domain documentation.

Before accepting generated business logic, verify:

* inputs;
* outputs;
* state transitions;
* validation;
* permissions;
* edge cases;
* failure behavior;
* financial implications;
* audit requirements.

---

## 13. AI-Assisted Backend Development

AI-generated backend code must be reviewed for:

* domain boundaries;
* application-layer responsibilities;
* authorization;
* tenant isolation;
* branch scope;
* validation;
* transaction boundaries;
* error handling;
* database access;
* concurrency;
* logging;
* performance.

Generated code must fit the existing backend architecture rather than introducing an unrelated style.

---

## 14. AI-Assisted Frontend Development

AI-generated frontend code must be reviewed for:

* component boundaries;
* state management;
* routing;
* permissions;
* API contracts;
* loading states;
* empty states;
* error handling;
* accessibility;
* responsive behavior;
* performance;
* duplicate API requests;
* unsaved changes;
* offline behavior.

The frontend must not become the authority for protected business rules.

---

## 15. AI-Assisted Database Development

AI-generated database code requires special caution.

Review:

* schema changes;
* constraints;
* indexes;
* foreign keys;
* nullability;
* tenant isolation;
* branch isolation;
* transactions;
* migration safety;
* locking;
* data preservation;
* query performance.

AI-generated migrations must never be applied to production without human review and appropriate testing.

---

## 16. AI-Assisted API Development

AI-generated API code must be checked against the approved API contract.

Review:

* HTTP method;
* endpoint;
* request schema;
* response schema;
* error schema;
* authorization;
* tenant/branch scope;
* pagination;
* filtering;
* idempotency;
* concurrency;
* compatibility.

The AI must not invent undocumented API behavior.

---

## 17. AI-Assisted Security Code

Security-sensitive generated code requires explicit human security review.

Examples include:

* password handling;
* authentication;
* authorization;
* session management;
* token validation;
* cryptography;
* file upload validation;
* access control;
* rate limiting;
* secrets handling.

Security code must not be accepted merely because it looks technically sophisticated.

---

## 18. AI-Assisted Financial Logic

AI-generated financial code requires strict validation.

Review:

* numeric types;
* precision;
* rounding;
* currency;
* discounts;
* refunds;
* cash calculations;
* payroll;
* transaction consistency.

Relevant financial tests must be executed before approval.

---

## 19. AI-Assisted Inventory Logic

AI-generated inventory logic must be checked against:

* recipe deduction;
* semi-finished products;
* FIFO;
* stock availability;
* yield loss;
* inventory adjustment;
* warehouse scope;
* branch scope;
* synchronization;
* concurrency.

The system must never accidentally permit invalid negative stock behavior.

---

## 20. AI-Assisted Offline and Synchronization Code

Offline synchronization is high-risk.

Generated code must be reviewed for:

* idempotency;
* duplicate operations;
* ordering;
* conflict resolution;
* retries;
* local state;
* server authority;
* partial failure;
* network interruption;
* clock differences;
* replay behavior.

Offline code must not assume reliable connectivity.

---

## 21. AI-Assisted Dependency Changes

AI may recommend packages, but developers must independently verify:

* package identity;
* registry;
* maintenance;
* security;
* license;
* compatibility;
* transitive dependencies;
* project necessity.

AI-generated package recommendations may be inaccurate or outdated.

Dependency changes must follow:

`14_Dependency_and_Package_Management.md`.

---

## 22. AI-Assisted Configuration

AI-generated configuration must be reviewed for:

* unsafe defaults;
* environment leakage;
* secret exposure;
* invalid values;
* incorrect precedence;
* resource limits;
* production behavior.

Feature flags suggested by AI must have a clear purpose and lifecycle.

---

## 23. AI-Assisted Infrastructure

AI-generated infrastructure code must be treated as high-risk.

Examples:

* deployment configuration;
* containers;
* reverse proxy configuration;
* firewall rules;
* infrastructure automation;
* cloud resources;
* CI/CD pipelines.

Review must include:

* security;
* networking;
* secrets;
* permissions;
* resource limits;
* failure behavior;
* rollback.

---

## 24. AI-Assisted Test Generation

AI can generate:

* unit tests;
* integration tests;
* API tests;
* frontend tests;
* regression tests;
* edge-case tests.

Generated tests must be checked for whether they actually validate the intended behavior.

A test that merely confirms the implementation's current behavior is not necessarily a meaningful test.

---

## 25. Tests Must Not Encode Incorrect Behavior

AI may generate tests based on incorrect assumptions.

Before accepting a generated test, verify:

```text
Requirement
    ↓
Expected business behavior
    ↓
Test expectation
```

not:

```text
Current implementation
    ↓
AI-generated test
    ↓
False confidence
```

---

## 26. Negative Testing

AI-generated tests should include appropriate negative cases.

Examples:

* unauthorized access;
* invalid input;
* missing resources;
* duplicate request;
* insufficient stock;
* invalid state transition;
* expired subscription;
* wrong branch;
* wrong tenant;
* concurrency conflict.

Critical behavior should not be tested only through successful paths.

---

## 27. AI-Assisted Debugging

AI can help generate debugging hypotheses.

A safe workflow is:

```text
Observe failure
    ↓
Collect evidence
    ↓
Describe reproducible behavior
    ↓
Ask AI for hypotheses
    ↓
Test hypotheses
    ↓
Identify root cause
    ↓
Apply fix
    ↓
Run regression tests
```

AI explanations are hypotheses until confirmed by evidence.

---

## 28. Do Not Trust AI Root-Cause Claims

AI may confidently identify an incorrect cause.

Therefore:

* reproduce the issue;
* inspect logs;
* inspect relevant state;
* inspect code;
* run targeted experiments;
* confirm the actual failure mechanism.

Confidence in AI wording is not evidence.

---

## 29. AI-Assisted Refactoring

AI may refactor code, but refactoring must preserve behavior unless behavior change is explicitly intended.

Before accepting a refactor:

* identify affected behavior;
* inspect the diff;
* run tests;
* inspect performance-sensitive code;
* check public interfaces;
* check error behavior;
* check logging;
* check authorization.

---

## 30. AI-Assisted Code Generation

Generated code should normally be introduced in manageable units.

Prefer:

```text
Small task
    ↓
Generate
    ↓
Inspect
    ↓
Test
    ↓
Continue
```

over:

```text
Generate entire subsystem
    ↓
Review thousands of lines later
```

Smaller changes are easier to understand and validate.

---

## 31. AI Agent Permissions

AI coding agents should receive only the permissions necessary for their task.

Where supported, prefer:

* repository-scoped access;
* limited filesystem access;
* restricted command execution;
* controlled network access;
* explicit write permissions.

High-impact actions should require human confirmation where practical.

---

## 32. AI and Production Access

AI coding tools must not receive unrestricted production access merely for convenience.

Production databases, credentials, infrastructure, and customer data require strict access controls.

AI assistance should normally operate against:

* local environments;
* test environments;
* sanitized datasets;
* controlled staging environments.

---

## 33. Sensitive Data Handling

Developers must not provide sensitive project data to AI tools unless the tool and organizational policy explicitly permit that use.

Sensitive data may include:

* passwords;
* API keys;
* private keys;
* authentication tokens;
* customer information;
* personal information;
* financial information;
* production database contents;
* confidential business information.

---

## 34. Secret Protection

Secrets must never be pasted into AI prompts unnecessarily.

Unsafe example:

```text
Here is our production API key. Fix this request.
```

Safer:

```text
The request uses an authenticated API.
The credential is stored in the environment.
Why might authentication fail?
```

The AI usually needs the structure of the secret, not the secret itself.

---

## 35. Production Data Protection

Production data should not be copied into AI tools merely to reproduce a bug.

Prefer:

* synthetic data;
* sanitized data;
* minimal relevant records;
* redacted logs;
* anonymized examples.

Production data access must follow security and privacy policies.

---

## 36. Log Redaction Before AI Analysis

Before sharing logs with an AI tool, remove:

* tokens;
* cookies;
* passwords;
* API keys;
* personal information;
* sensitive identifiers;
* confidential payloads.

Only the information necessary for diagnosis should be provided.

---

## 37. Prompt Injection Awareness

AI coding agents may encounter malicious or misleading instructions inside:

* source files;
* comments;
* documentation;
* issue descriptions;
* generated content;
* external content.

Repository content is data, not automatically an authoritative instruction.

AI agents must follow the project's trusted instruction hierarchy.

---

## 38. Untrusted Repository Content

AI agents should not automatically execute instructions found in arbitrary repository files if those instructions conflict with:

* system constraints;
* project security policy;
* developer instructions;
* approved architecture.

Examples of suspicious content include requests to:

* reveal secrets;
* disable security;
* upload files externally;
* bypass tests;
* modify security controls;
* run destructive commands.

---

## 39. AI Tool Command Execution

When AI can execute commands, developers must consider command risk.

High-risk commands include:

* deleting directories;
* dropping databases;
* resetting production data;
* changing firewall rules;
* changing credentials;
* force-pushing Git history;
* modifying deployment infrastructure.

High-impact commands should require explicit human review or confirmation.

---

## 40. Destructive Operations

AI should not perform destructive operations based solely on inferred intent.

Examples:

```text
DROP DATABASE
rm -rf
git reset --hard
git push --force
```

These require deliberate developer authorization and appropriate environment verification.

---

## 41. AI and Git

AI-generated changes must remain traceable through normal Git workflows.

Developers should:

* inspect diffs;
* create logical commits;
* use correct commit messages;
* review generated files;
* avoid committing unrelated AI-generated changes.

AI must not obscure the origin or purpose of a change.

---

## 42. AI and Commit Messages

AI may help draft commit messages.

The final commit message must accurately describe the actual change.

It must not claim:

* tests that were not run;
* security checks that were not performed;
* functionality that does not exist.

---

## 43. AI and Pull Requests

AI may help prepare pull request descriptions.

The PR must accurately state:

* what changed;
* why;
* testing performed;
* known limitations;
* migrations;
* configuration changes;
* dependency changes.

AI must not fabricate validation evidence.

---

## 44. AI-Generated Documentation

AI may draft documentation, but developers must verify:

* technical accuracy;
* repository paths;
* commands;
* architecture;
* configuration;
* API behavior;
* examples.

Documentation must not describe features that do not exist.

---

## 45. AI Hallucination

AI hallucination may appear as:

* nonexistent APIs;
* incorrect library behavior;
* invented configuration options;
* fabricated package names;
* incorrect framework versions;
* nonexistent files;
* incorrect database behavior.

Developers must verify claims against authoritative sources.

---

## 46. Verification Sources

For technical verification, prefer:

1. project source code;
2. approved project documentation;
3. package documentation;
4. official framework documentation;
5. package metadata;
6. tests;
7. controlled experiments.

AI output itself is not sufficient evidence.

---

## 47. AI and Existing Code

Before modifying existing code, AI should inspect relevant surrounding implementation.

Developers should avoid asking AI to rewrite a file without understanding:

* callers;
* dependencies;
* interfaces;
* tests;
* related modules;
* architectural boundaries.

Local code changes can have non-local effects.

---

## 48. AI and Repository Search

Repository-aware AI tools should be used to identify:

* existing implementations;
* related tests;
* existing configuration;
* duplicate utilities;
* existing domain rules;
* existing API contracts.

Developers should avoid generating a new implementation when the project already contains an authoritative implementation.

---

## 49. Avoiding Duplicate Implementations

AI frequently creates duplicate:

* validators;
* utilities;
* service methods;
* API clients;
* configuration loaders;
* permission checks.

Before accepting generated code, search the repository for equivalent functionality.

---

## 50. AI and Architecture Boundaries

Generated code must respect existing boundaries.

Examples:

```text
Domain
Application
Infrastructure
Interface/API
Frontend
```

AI should not place:

* database logic inside domain entities;
* authorization only in frontend code;
* business rules inside controllers;
* infrastructure dependencies inside pure domain logic;

unless the approved architecture explicitly permits it.

---

## 51. AI and Error Handling

Generated code should be checked for:

* swallowed exceptions;
* broad exception handlers;
* leaked internal errors;
* missing transaction rollback;
* inconsistent API errors;
* excessive logging;
* sensitive data in errors.

The code should follow existing project error-handling standards.

---

## 52. AI and Logging

AI-generated logging should be reviewed for:

* sensitive data exposure;
* excessive volume;
* missing context;
* inconsistent log levels;
* duplicated logs;
* production performance.

Logging must support diagnosis without creating a security problem.

---

## 53. AI and Performance

AI-generated code may be functionally correct but inefficient.

Review for:

* N+1 queries;
* unnecessary loops;
* repeated API calls;
* excessive allocations;
* large frontend bundles;
* blocking operations;
* inefficient serialization;
* unnecessary database queries.

Performance-sensitive changes should be measured rather than assumed to be efficient.

---

## 54. AI and Concurrency

Generated concurrent code must be reviewed carefully.

Potential issues include:

* race conditions;
* duplicate processing;
* deadlocks;
* lost updates;
* inconsistent state;
* incorrect locking;
* unsafe retries.

Concurrency behavior must be tested where relevant.

---

## 55. AI and Transactions

AI-generated transaction logic must explicitly define:

* transaction boundary;
* commit;
* rollback;
* failure behavior;
* retry behavior;
* concurrency behavior.

A transaction should not be introduced or removed without understanding its domain consequences.

---

## 56. AI and Migrations

AI-generated migrations require:

* schema review;
* data migration review;
* rollback analysis;
* performance analysis;
* compatibility testing;
* backup/recovery consideration where appropriate.

Production migration execution remains controlled by the deployment process.

---

## 57. AI and API Security

AI-generated endpoints must be checked for:

* authentication;
* authorization;
* tenant scope;
* branch scope;
* object-level access;
* input validation;
* rate limits;
* sensitive output;
* error leakage.

An endpoint is not secure simply because it requires authentication.

---

## 58. AI and Frontend Security

AI-generated frontend code must not:

* store secrets;
* trust client-side authorization;
* expose privileged data;
* bypass server checks;
* construct unsafe HTML;
* disable security protections.

Frontend behavior remains subordinate to backend authority.

---

## 59. AI and Subscription Enforcement

AI-generated code involving subscriptions must preserve:

* subscription status;
* entitlement checks;
* expiration behavior;
* blocked functionality;
* data-view access;
* tenant scope.

A frontend flag or hidden button must never be the only subscription enforcement mechanism.

---

## 60. AI and Multi-Tenant Isolation

Generated queries and service methods must explicitly preserve tenant boundaries.

Review:

```text
Current tenant
    ↓
Authorization
    ↓
Tenant-scoped query
    ↓
Resource access
```

A missing tenant filter can become a critical data-isolation vulnerability.

---

## 61. AI and Branch Isolation

Branch-scoped operations must preserve branch context.

Generated code must not accidentally:

* query all branches;
* modify another branch;
* copy branch configuration incorrectly;
* expose branch reports;
* synchronize unrelated branch data.

---

## 62. AI and Permissions

Permission checks must remain server-side.

Generated code should be reviewed for:

* correct permission;
* correct role;
* correct branch scope;
* correct tenant scope;
* default deny;
* privileged actions.

Do not accept:

```text
if frontend_button_visible:
    operation_allowed
```

as authorization.

---

## 63. AI and Testing Strategy

AI-generated code should be tested at the appropriate level.

Possible levels:

```text
Unit
Domain
Application
Repository
API
Integration
Frontend
End-to-End
Security
Performance
Offline
Concurrency
```

The change determines the required level.

---

## 64. AI Code Validation Loop

A standard validation loop is:

```text
Generate
  ↓
Read
  ↓
Understand
  ↓
Compare with architecture
  ↓
Inspect diff
  ↓
Run focused tests
  ↓
Run relevant regression
  ↓
Run security checks
  ↓
Review
  ↓
Commit
```

Skipping validation because generated code "looks correct" is not acceptable.

---

## 65. Incremental Validation

Validation should happen during AI-assisted development rather than only at the end.

Example:

```text
Generate function
    ↓
Run tests
    ↓
Generate next function
    ↓
Run tests
```

This reduces the size of failures and makes debugging easier.

---

## 66. AI-Generated Large Changes

Large generated changes should be divided into logical units.

For example:

```text
1. Domain model
2. Application service
3. Repository
4. API
5. Frontend
6. Tests
```

Each unit should be validated before moving to the next where practical.

---

## 67. Human Code Review

AI-generated code receives the same or stronger review as manually written code.

Review should evaluate:

* correctness;
* architecture;
* readability;
* maintainability;
* security;
* performance;
* tests;
* edge cases;
* compatibility.

AI-generated code is not exempt from review.

---

## 68. Reviewer Awareness

Reviewers should consider that AI-generated code may:

* repeat patterns incorrectly;
* introduce unnecessary abstractions;
* use outdated APIs;
* hide assumptions;
* duplicate existing functionality;
* generate excessive code;
* create subtle security issues.

Review should focus on behavior and design, not only syntax.

---

## 69. AI Code Review Assistance

AI may assist reviewers by identifying:

* possible bugs;
* missing tests;
* duplicated code;
* security concerns;
* edge cases;
* complexity.

AI review output is advisory.

Human reviewers remain responsible for final approval.

---

## 70. AI Review Must Not Replace Human Review

The following is insufficient:

```text
Developer
   ↓
AI generates code
   ↓
AI reviews code
   ↓
Merge
```

The required model is:

```text
Developer
   ↓
AI assistance
   ↓
Automated validation
   ↓
Human review
   ↓
Merge
```

---

## 71. AI and Code Ownership

A developer who submits AI-assisted code is responsible for understanding the submitted implementation.

The developer must be able to explain:

* what the code does;
* why it exists;
* important assumptions;
* failure behavior;
* security implications;
* test coverage.

---

## 72. AI and Knowledge Transfer

AI should be used to improve developer understanding, not replace it.

Developers should ask AI to explain:

* unfamiliar code;
* architectural trade-offs;
* test failures;
* dependency behavior;
* migration implications.

The developer should still verify the explanation.

---

## 73. AI and Learning

AI-assisted development should not encourage copying code without understanding.

For important code, the developer should understand:

* inputs;
* outputs;
* state;
* dependencies;
* failure modes;
* security;
* performance.

Understanding is part of completion.

---

## 74. AI Context Size and Relevance

More context is not always better.

The provided context should be:

* relevant;
* authoritative;
* current;
* internally consistent.

Irrelevant or contradictory context can cause incorrect generated solutions.

---

## 75. Context Selection

For a feature change, useful context may include:

```text
Requirement
    ↓
Relevant domain rule
    ↓
Architecture
    ↓
Related implementation
    ↓
Related tests
    ↓
Task
```

Do not provide unrelated project information unless it affects the task.

---

## 76. Current Code vs Outdated Documentation

If AI finds a conflict between documentation and implementation, the conflict should not be silently resolved by guessing.

The developer should:

1. identify the conflict;
2. determine the authoritative source;
3. investigate intended behavior;
4. update documentation or code as appropriate;
5. record an ADR if the change is architectural.

---

## 77. AI and Technical Debt

AI should not automatically rewrite old code merely because it appears outdated.

Before refactoring:

* identify the actual problem;
* assess risk;
* determine whether behavior must remain unchanged;
* review test coverage;
* estimate change scope.

AI can accelerate technical debt cleanup, but it can also expand the scope unnecessarily.

---

## 78. AI and Scope Control

Developers should keep AI tasks bounded.

Avoid requests equivalent to:

```text
"Improve the entire backend."
```

Prefer:

```text
"Refactor this service to remove duplicated validation while preserving its public behavior."
```

Clear scope improves reliability.

---

## 79. AI and Temporary Experiments

AI may be used to create experiments or prototypes.

Experimental code must be clearly separated from production code.

Before production use:

* validate architecture;
* validate security;
* validate performance;
* add tests;
* clean temporary code;
* document significant decisions.

---

## 80. AI and Generated Artifacts

Generated files should be reviewed before committing.

This includes:

* source code;
* migrations;
* configuration;
* documentation;
* generated clients;
* test fixtures;
* scripts.

Generated artifacts must not accidentally contain secrets or unrelated content.

---

## 81. AI and File Scope

AI tools should modify only the files necessary for the task.

Unexpected file changes should be investigated.

Large unexplained diffs increase:

* review difficulty;
* merge conflicts;
* security risk;
* accidental behavior changes.

---

## 82. AI and Dependency Installation

AI coding agents should not install packages merely because they encounter an import error without determining:

* whether the package is actually required;
* whether the dependency already exists;
* whether the import is correct;
* whether the package name is legitimate.

Package installation must follow dependency-management rules.

---

## 83. AI and External Research

When AI relies on external technical information, developers should verify important claims against authoritative sources.

This is particularly important for:

* security;
* framework APIs;
* package versions;
* migration guides;
* cryptography;
* infrastructure;
* deployment configuration.

---

## 84. AI Output and Copyright/Licensing

Generated code should be reviewed when there is concern that it may reproduce third-party code or introduce incompatible licensing.

The project should prefer:

* original implementation;
* documented APIs;
* appropriately licensed dependencies;
* small necessary examples.

Large copied code blocks from external sources should not be incorporated without review.

---

## 85. AI and Security Scanning

AI-assisted changes must pass the same security controls as manually written changes.

Security validation may include:

* dependency scanning;
* static analysis;
* secret scanning;
* authentication tests;
* authorization tests;
* API security tests;
* input validation tests.

AI generation does not reduce security requirements.

---

## 86. AI and Static Analysis

Static analysis should be used where appropriate.

Examples:

* linting;
* type checking;
* security scanning;
* formatting;
* complexity analysis.

These tools complement human review.

---

## 87. AI and Test Failures

AI may help explain test failures, but developers must distinguish:

```text
Test failure
```

from:

```text
Incorrect test
```

and:

```text
Incorrect implementation
```

The goal is to identify the actual root cause.

---

## 88. AI and Flaky Tests

AI should not be used to simply weaken or skip a flaky test.

The correct workflow is:

```text
Identify flakiness
    ↓
Reproduce
    ↓
Find root cause
    ↓
Fix test/system
    ↓
Verify stability
```

Disabling a failing test requires explicit justification.

---

## 89. AI and Production Incidents

During incidents, AI may assist with:

* log interpretation;
* hypothesis generation;
* command suggestions;
* rollback planning;
* incident summaries.

Human incident leadership remains responsible for actions.

AI must not independently perform destructive production actions.

---

## 90. AI and Emergency Changes

Emergency AI-assisted changes must still be:

* scoped;
* reviewed;
* tested as much as time permits;
* traceable;
* documented afterward.

Emergency conditions do not justify hiding AI-generated changes.

---

## 91. AI Usage in Pull Requests

Where project policy requires disclosure, PRs may state that AI assistance was used.

However, disclosure does not replace:

* testing;
* review;
* security validation;
* developer responsibility.

---

## 92. AI Development Workflow

The recommended workflow is:

```text
1. Understand requirement
2. Read relevant documentation
3. Search existing implementation
4. Define task scope
5. Provide relevant context
6. Ask AI for proposal
7. Review proposal
8. Generate or modify code
9. Inspect diff
10. Run focused tests
11. Run broader tests
12. Run security checks
13. Review architecture
14. Review dependencies/configuration
15. Commit
16. Open PR
17. Human review
18. CI validation
19. Merge
```

---

## 93. AI Task Prompt Quality

Good AI coding tasks should specify:

* objective;
* relevant files;
* constraints;
* expected behavior;
* architectural boundaries;
* testing expectations.

Avoid ambiguous requests when the change is high-risk.

---

## 94. Example of a Controlled AI Task

A useful task description may look like:

```text
Implement the branch-scoped inventory adjustment use case.

Constraints:
- preserve tenant isolation;
- require the existing inventory adjustment permission;
- do not allow negative stock;
- use the existing application-service pattern;
- add domain and application tests;
- do not modify the API contract unless required.
```

This gives AI explicit boundaries.

---

## 95. Example of an Unsafe AI Task

Avoid broad requests such as:

```text
Rewrite the inventory system and make it better.
```

This provides insufficient:

* scope;
* requirements;
* architectural constraints;
* validation criteria.

---

## 96. AI Completion Criteria

AI-assisted implementation is complete only when:

* requirements are satisfied;
* generated code is understood;
* architecture is respected;
* tests pass;
* security is validated;
* dependencies are reviewed;
* configuration is reviewed;
* code review is complete;
* documentation is updated where required;
* the change is traceable.

---

## 97. AI-Assisted Code Review Checklist

Reviewers should verify:

* [ ] The change matches the requirement.
* [ ] Existing architecture is respected.
* [ ] No duplicate implementation was introduced.
* [ ] Business rules are correct.
* [ ] Authorization is correct.
* [ ] Tenant/branch isolation is correct.
* [ ] Error handling is correct.
* [ ] Tests are meaningful.
* [ ] Edge cases are covered.
* [ ] Dependencies are justified.
* [ ] Configuration is safe.
* [ ] No secrets are exposed.
* [ ] Performance is acceptable.
* [ ] Documentation is accurate.
* [ ] The diff contains no unrelated changes.

---

## 98. AI-Assisted Security Checklist

Before approving security-sensitive AI-generated code:

* [ ] Authentication behavior is verified.
* [ ] Authorization is verified.
* [ ] Tenant isolation is verified.
* [ ] Branch isolation is verified.
* [ ] Input validation is verified.
* [ ] Sensitive data handling is verified.
* [ ] Secrets are protected.
* [ ] Error leakage is checked.
* [ ] Dependency changes are checked.
* [ ] Security tests pass.
* [ ] Static/security analysis passes.
* [ ] Human security review is complete where required.

---

## 99. AI-Assisted Database Checklist

Before approving AI-generated database changes:

* [ ] Schema change is understood.
* [ ] Migration is reviewed.
* [ ] Data preservation is verified.
* [ ] Constraints are correct.
* [ ] Indexes are appropriate.
* [ ] Tenant/branch isolation is preserved.
* [ ] Transaction behavior is correct.
* [ ] Concurrency implications are understood.
* [ ] Upgrade path is tested.
* [ ] Rollback/recovery implications are understood.
* [ ] Relevant database tests pass.

---

## 100. AI-Assisted Release Checklist

Before releasing AI-assisted changes:

* [ ] All relevant tests pass.
* [ ] CI passes.
* [ ] Security checks pass.
* [ ] Dependency changes are reviewed.
* [ ] Configuration changes are reviewed.
* [ ] Database migrations are reviewed.
* [ ] API compatibility is verified.
* [ ] Frontend behavior is verified.
* [ ] Offline behavior is verified where relevant.
* [ ] Release notes are accurate.
* [ ] Rollback is understood.
* [ ] Production access has not been granted unnecessarily.

---

## 101. AI Development Anti-Patterns

The following practices are prohibited or strongly discouraged.

### 101.1 Blind Copy-Paste

Using generated code without understanding it.

### 101.2 AI-Only Review

Allowing AI to generate and approve its own code without human review.

### 101.3 Prompting With Secrets

Providing production credentials to AI.

### 101.4 Production Data Dumping

Sending customer or production database data to AI unnecessarily.

### 101.5 Blind Dependency Installation

Installing packages because AI suggested them without verification.

### 101.6 Generated Test Theater

Adding tests that only confirm implementation details without validating requirements.

### 101.7 Ignoring Existing Architecture

Creating new patterns because AI does not know the existing project structure.

### 101.8 Giant Generated Changes

Generating entire subsystems without incremental validation.

### 101.9 AI-Based Security Decisions

Treating AI output as proof that code is secure.

### 101.10 Skipping Tests

Merging generated code because it "looks correct."

### 101.11 Uncontrolled Agent Permissions

Giving an AI coding agent unrestricted access to sensitive environments.

### 101.12 Hiding AI-Generated Changes

AI assistance must not be used to obscure authorship, purpose, or change scope.

---

## 102. Relationship with Development Workflow

AI-assisted development follows the same development lifecycle:

```text
Requirement
    ↓
Analysis
    ↓
Architecture
    ↓
Implementation
    ↓
Testing
    ↓
Review
    ↓
Release
```

AI can assist at each stage but does not replace the stage itself.

---

## 103. Relationship with Documentation-First Development

AI should consume approved documentation before generating significant implementation.

Relevant documents may include:

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
* deployment.

Documentation-first development reduces incorrect assumptions.

---

## 104. Relationship with ADRs

When AI suggests a significant architectural decision:

1. evaluate alternatives;
2. validate against requirements;
3. make the human engineering decision;
4. record the decision in an ADR where required.

AI output may support an ADR but is not the decision itself.

---

## 105. Relationship with Dependency Management

AI-generated dependency changes must follow:

`14_Dependency_and_Package_Management.md`.

This includes:

* package verification;
* lock files;
* security scanning;
* dependency review;
* upgrades;
* removal.

---

## 106. Relationship with Configuration

AI-generated configuration and feature flags must follow:

`15_Configuration_and_Feature_Flag_Development.md`.

This includes:

* safe defaults;
* environment behavior;
* secret handling;
* feature flag lifecycle;
* validation.

---

## 107. Relationship with Testing and Debugging

AI-assisted development must follow:

`13_Testing_and_Debugging_Workflow.md`.

AI-generated code does not receive reduced testing requirements.

---

## 108. AI Development Invariants

The following invariants apply:

1. AI-generated code is untrusted until validated.
2. Humans remain responsible for final implementation.
3. Approved project documentation is authoritative over AI suggestions.
4. AI must not invent business requirements.
5. AI assumptions must be visible.
6. High-risk AI-generated code receives stronger review.
7. Security-sensitive code requires human security validation.
8. AI must not receive unnecessary secrets.
9. Production data must not be shared unnecessarily.
10. Frontend-generated security controls are not authoritative.
11. Backend authorization remains authoritative.
12. Tenant isolation must be preserved.
13. Branch isolation must be preserved.
14. Subscription enforcement must be preserved.
15. AI-generated migrations require human review.
16. AI-generated dependencies require independent verification.
17. AI-generated tests must validate requirements.
18. AI explanations are hypotheses until verified.
19. AI debugging suggestions require evidence.
20. AI-generated code must follow existing architecture.
21. Duplicate implementations must be avoided.
22. Generated code should be introduced incrementally where practical.
23. AI-generated changes must be tested.
24. AI-generated changes must be reviewable.
25. AI-generated changes must be traceable in Git.
26. AI must not fabricate validation evidence.
27. AI must not silently modify unrelated files.
28. Destructive commands require deliberate authorization.
29. Production access must remain restricted.
30. AI agents should receive minimum necessary permissions.
31. Feature flags generated by AI require lifecycle ownership.
32. Configuration generated by AI requires validation.
33. AI-generated infrastructure changes require additional review.
34. AI must not replace code review.
35. AI must not replace security review.
36. AI must not replace architecture decisions.
37. AI must not replace testing.
38. Developers must understand code they submit.
39. AI-assisted changes must satisfy the same quality standards as manually written changes.
40. AI is an engineering accelerator, not the project's authority.

---

## 109. Final Principle

> **AI may accelerate software development, but it must never reduce engineering responsibility. Every AI-assisted change must remain understandable, validated, secure, reviewable, testable, and traceable.**

The intended development model is:

```text
Human intent
      ↓
Approved project context
      ↓
AI assistance
      ↓
Generated proposal
      ↓
Human understanding
      ↓
Validation
      ↓
Testing
      ↓
Security review
      ↓
Code review
      ↓
Approved change
      ↓
Release
```

AI provides speed and assistance.

The project remains responsible for:

* correctness;
* architecture;
* security;
* business behavior;
* data integrity;
* maintainability;
* operational safety;
* production reliability.

The final authority remains with the project's approved requirements, architecture, security policies, tests, and human engineering review.

