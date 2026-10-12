# 10 — Documentation-First Development Workflow

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the documentation-first development workflow for the FastFood ERP.

The purpose is to ensure that implementation is based on understood requirements, analyzed business behavior, approved architecture, and explicit technical decisions rather than undocumented assumptions.

The workflow establishes a controlled path from:

```text
Requirement
    ↓
Business Analysis
    ↓
System Analysis
    ↓
Domain Analysis
    ↓
Architecture
    ↓
Technical Design
    ↓
Implementation
    ↓
Testing
    ↓
Review
    ↓
Release
```

Documentation is treated as an engineering artifact, not as paperwork created after implementation.

---

# 2. Scope

This document covers:

* documentation-first principles;
* requirements capture;
* business analysis;
* system analysis;
* domain analysis;
* architecture documentation;
* technical design;
* implementation readiness;
* coding workflow;
* testing alignment;
* ADR usage;
* documentation ownership;
* change propagation;
* documentation synchronization;
* AI-assisted development;
* implementation traceability;
* review;
* completion criteria;
* documentation quality rules.

This document does not replace the detailed requirements, architecture, testing, security, deployment, or domain documents.

---

# 3. Core Principle

The system should be designed before it is implemented.

This does not mean every line of code must be designed in advance.

It means that the decisions necessary to safely implement a change must be understood before coding begins.

The required principle is:

> **Understand the problem, define the behavior, design the solution, then implement it.**

---

# 4. Why Documentation Comes First

Documentation-first development reduces:

* undocumented assumptions;
* inconsistent business behavior;
* duplicated decisions;
* architecture drift;
* accidental coupling;
* unnecessary rewrites;
* API inconsistencies;
* database mistakes;
* security omissions;
* incomplete testing.

It also allows developers and AI coding tools to understand the intended system before modifying the codebase.

---

# 5. Documentation Is Part of the System

Project documentation represents the intended system model.

It describes:

```text
Business Intent
      ↓
System Behavior
      ↓
Domain Model
      ↓
Architecture
      ↓
Technical Rules
      ↓
Implementation
```

Code is the executable realization of these decisions.

When code and documentation disagree, the disagreement must be resolved rather than ignored.

---

# 6. Documentation Hierarchy

The project documentation is organized by responsibility.

Conceptually:

```text
01_Business_Analysis
        ↓
02_System_Analysis
        ↓
03_Domain_Analysis
        ↓
04_Architecture
        ↓
05_Database
06_Backend
07_Frontend
08_AI
09_API
10_Deployment
11_Security
12_Testing
13_Development
14_Operations
15_Future
```

The exact document structure may evolve, but responsibility boundaries must remain clear.

---

# 7. Business Analysis

Business Analysis defines what the business needs.

It should answer questions such as:

* What problem is being solved?
* Who uses the system?
* What business processes exist?
* What outcomes are expected?
* What rules are mandatory?
* What constraints exist?
* What business terminology is used?
* What decisions have been accepted?

Business Analysis should avoid prematurely defining implementation details.

Example:

```text
Business requirement:
A branch must not sell a product when required stock is unavailable.
```

This is a business requirement.

It does not yet define:

* database tables;
* API endpoints;
* frontend components;
* Python classes.

---

# 8. System Analysis

System Analysis translates business requirements into system behavior.

It defines:

* actors;
* use cases;
* system workflows;
* states;
* inputs;
* outputs;
* system responsibilities;
* integration boundaries;
* operational scenarios;
* exceptions;
* offline behavior;
* permission interactions.

Example:

```text
Order
  ↓
Created
  ↓
Accepted
  ↓
Prepared
  ↓
Paid
  ↓
Archived
```

System Analysis should make expected behavior understandable before implementation.

---

# 9. Domain Analysis

Domain Analysis identifies the business concepts that the system must represent.

Examples:

```text
Restaurant
Branch
Employee
Product
Recipe
Recipe Version
Order
Order Item
Payment
Refund
Cash Register
Inventory Movement
Expense
Subscription
```

Domain Analysis should define:

* concepts;
* relationships;
* ownership;
* invariants;
* lifecycle;
* terminology;
* important business rules.

Domain Analysis should not become a database schema disguised as business documentation.

---

# 10. Architecture

Architecture defines how the system realizes approved behavior.

It should address:

* system boundaries;
* major components;
* application layers;
* communication;
* data ownership;
* deployment boundaries;
* security boundaries;
* scalability;
* offline behavior;
* integration patterns;
* reliability;
* operational responsibilities.

Architecture should not be created to solve undocumented requirements.

It should be derived from understood system behavior.

---

# 11. Technical Design

Technical design translates architecture into implementation-ready decisions.

Depending on the change, this may include:

* database schema;
* API contract;
* backend module boundaries;
* frontend feature structure;
* background jobs;
* cache behavior;
* synchronization behavior;
* AI integration;
* deployment configuration;
* test strategy.

Not every feature requires a separate technical design document.

The required level of detail depends on change complexity.

---

# 12. Requirements → Implementation Chain

Every meaningful feature should be traceable through the documentation hierarchy.

Conceptually:

```text
Business Requirement
        ↓
System Behavior
        ↓
Domain Concept
        ↓
Architecture Decision
        ↓
Technical Design
        ↓
Implementation
        ↓
Tests
```

This creates traceability.

A developer should be able to answer:

> Why does this code exist?

and:

> Which approved requirement or design decision does this behavior implement?

---

# 13. Documentation Status

Documentation should have an explicit status.

Typical statuses include:

```text
Draft
Under Review
Accepted
Superseded
Deprecated
```

For this project, accepted project documentation represents the current approved design unless explicitly superseded.

Code must not silently implement a contradictory design while the documentation remains accepted.

---

# 14. Draft vs Accepted

A draft document is exploratory.

An accepted document represents an approved project decision.

Before implementation of a significant feature:

```text
Draft
   ↓
Review
   ↓
Accepted
   ↓
Implementation
```

Implementation may begin before every document is perfect, but the decisions required for safe implementation must be accepted.

---

# 15. Open Questions

Documentation-first development does not require pretending that unknown decisions are already known.

Open questions should be recorded explicitly.

Example:

```text
Open Question:
Should branch managers be allowed to approve refunds above a configurable threshold?
```

An unresolved question should not be silently converted into a developer assumption.

Possible states:

```text
OPEN
DECIDED
DEFERRED
REJECTED
```

---

# 16. Decision Before Implementation

Before coding, identify decisions that materially affect implementation.

Examples:

* ownership;
* permissions;
* state transitions;
* data lifecycle;
* API behavior;
* schema structure;
* synchronization;
* concurrency;
* failure behavior;
* audit requirements.

If a decision can significantly change the implementation, it should be resolved or explicitly deferred before implementation.

---

# 17. Documentation-First Feature Workflow

The standard feature workflow is:

```text
1. Identify requirement
        ↓
2. Review existing documentation
        ↓
3. Identify affected business behavior
        ↓
4. Perform system analysis
        ↓
5. Identify domain impact
        ↓
6. Review architecture
        ↓
7. Identify technical changes
        ↓
8. Update required documentation
        ↓
9. Record architectural decisions
        ↓
10. Define tests
        ↓
11. Implement
        ↓
12. Validate against documentation
        ↓
13. Review
        ↓
14. Update documentation if implementation reveals approved changes
```

---

# 18. Start by Reading Existing Documentation

Developers must not begin by immediately editing code when working on a significant feature.

First identify:

* relevant requirements;
* existing domain rules;
* architecture;
* API contracts;
* database design;
* frontend behavior;
* security requirements;
* testing requirements;
* deployment implications.

This prevents solving an already-solved problem differently.

---

# 19. Search Before Creating New Documentation

Before creating a new document, determine whether the topic already exists.

Avoid creating duplicate sources of truth.

For example, if branch authorization is already defined in security documentation, a feature document should reference that rule instead of redefining it differently.

The preferred pattern is:

```text
One authoritative rule
        ↓
Referenced by related documents
```

not:

```text
Same rule
 ├── Document A
 ├── Document B
 └── Document C
```

---

# 20. Single Source of Truth

Each important decision should have one authoritative location.

Examples:

| Concern              | Primary Source    |
| -------------------- | ----------------- |
| Business requirement | Business Analysis |
| System workflow      | System Analysis   |
| Domain concept       | Domain Analysis   |
| Architecture         | Architecture docs |
| API contract         | API docs          |
| Database structure   | Database docs     |
| Security policy      | Security docs     |
| Testing strategy     | Testing docs      |
| Deployment behavior  | Deployment docs   |
| Development workflow | Development docs  |

Other documents should reference the authoritative source where possible.

---

# 21. Avoiding Documentation Duplication

Documentation duplication is dangerous because copies can diverge.

Avoid repeating complete rules when a reference is sufficient.

For example:

```text
See:
`11_Security/...`
```

may be preferable to copying the complete security policy into a development document.

Duplication is acceptable only when a short contextual summary materially improves understanding.

---

# 22. Change Impact Analysis

Before implementing a meaningful change, identify affected documentation.

Example:

```text
New Refund Approval Rule
        ↓
Business Analysis
        ↓
System Analysis
        ↓
Domain Analysis
        ↓
Security
        ↓
API
        ↓
Frontend
        ↓
Testing
```

Not every change affects every layer.

The developer should update only the relevant documentation.

---

# 23. Small Changes

Documentation-first does not mean creating documents for every small change.

A small implementation change may only require:

* existing documentation review;
* code change;
* tests;
* commit message.

Examples:

* fixing a typo;
* correcting a local implementation bug;
* improving an internal helper;
* refactoring without behavior change.

The required documentation effort should be proportional to change impact.

---

# 24. Significant Changes

A significant change may require updates to multiple documentation layers.

Examples:

* new business capability;
* new role;
* new permission model;
* new financial workflow;
* new inventory behavior;
* new API resource;
* new database ownership model;
* new synchronization behavior;
* architectural change;
* new integration.

These changes should not be implemented from an undocumented idea alone.

---

# 25. Documentation Change Before Code Change

When a change alters approved behavior, documentation should normally be updated before implementation.

Preferred sequence:

```text
Existing Design
      ↓
Change Analysis
      ↓
Documentation Update
      ↓
Approval
      ↓
Implementation
```

This ensures the developer implements the intended new behavior rather than the old behavior.

---

# 26. Code Change Reveals a Design Problem

Sometimes implementation reveals that the approved design is incomplete or technically unsuitable.

The developer must not silently change the architecture.

Instead:

```text
Implementation Discovery
        ↓
Identify Design Problem
        ↓
Update Analysis/Architecture
        ↓
ADR if required
        ↓
Approve Decision
        ↓
Continue Implementation
```

This preserves decision traceability.

---

# 27. Documentation and Code Conflicts

When documentation and code disagree, determine why.

Possible causes:

1. Code is wrong.
2. Documentation is outdated.
3. A decision changed but documentation was not updated.
4. The implementation contains an accidental behavior.
5. The documentation describes an incomplete design.

The disagreement must be explicitly resolved.

Do not automatically assume that existing code is the intended design.

---

# 28. Architecture Decision Records

ADRs are used for significant architectural decisions.

Examples:

* database ownership model;
* offline synchronization architecture;
* authentication model;
* tenant isolation strategy;
* event processing architecture;
* AI inference architecture;
* deployment architecture.

The ADR should record:

* context;
* problem;
* options;
* decision;
* consequences;
* status.

Implementation should follow the accepted architectural decision.

---

# 29. Documentation and ADR Relationship

An ADR records **why** an architectural decision was made.

Architecture documentation describes **what the architecture is**.

Development documentation describes **how developers work with it**.

These are complementary.

Example:

```text
ADR
↓
Why this architecture was chosen

Architecture Document
↓
What the architecture looks like

Development Document
↓
How developers implement within it
```

---

# 30. Requirements Traceability

Meaningful implementation should be traceable.

A practical traceability chain is:

```text
Requirement
↓
Analysis
↓
Design
↓
Code
↓
Test
↓
Release
```

Traceability may be represented through:

* issue identifiers;
* branch names;
* commits;
* pull requests;
* ADR references;
* document references;
* test names.

The exact mechanism may vary, but the relationship should remain discoverable.

---

# 31. Documentation and Testing

Testing should be derived from expected behavior.

The documentation defines:

```text
Expected behavior
```

Testing demonstrates:

```text
Actual behavior
```

Therefore:

```text
Requirement
   ↓
Expected Behavior
   ↓
Test Scenario
   ↓
Implementation
   ↓
Test Result
```

Tests should not be designed only around the current code implementation.

---

# 32. Documentation and Security

Security requirements must be considered before implementation.

Examples:

* who can access the feature;
* tenant scope;
* branch scope;
* role requirements;
* sensitive data;
* audit requirements;
* offline security;
* subscription restrictions.

Security cannot be added safely as a purely final-stage UI concern.

---

# 33. Documentation and Database Development

When a feature changes persistent data, the developer must review:

* domain model;
* database design;
* migration requirements;
* existing data;
* historical data;
* indexes;
* constraints;
* tenant/branch ownership.

The database migration should follow:

`08_Database_Development_and_Migration_Workflow.md`

---

# 34. Documentation and API Development

When a feature exposes or changes an API, the API contract must be defined.

The developer must identify:

* request;
* response;
* errors;
* authorization;
* compatibility;
* versioning;
* pagination;
* idempotency;
* consumer impact.

The API workflow is defined in:

`09_API_Development_and_Contract_Change_Workflow.md`

---

# 35. Documentation and Frontend Development

Frontend implementation should be derived from defined system behavior and API contracts.

Documentation should clarify:

* user workflow;
* permissions;
* states;
* validation;
* loading behavior;
* error behavior;
* offline behavior;
* destructive actions.

Frontend should not invent business rules that belong to the backend/domain.

---

# 36. Documentation and Offline Behavior

Offline behavior must be documented before implementation when a feature participates in offline operation.

Questions include:

* Can the feature work offline?
* What data is available locally?
* What operations can be queued?
* What happens when synchronization fails?
* What happens if the schema changes before synchronization?
* How are conflicts resolved?
* What does the user see while synchronization is pending?

Offline behavior must never be left as an accidental implementation detail.

---

# 37. Documentation and AI-Assisted Development

AI coding tools can accelerate implementation, but they must work from approved project context.

Recommended sequence:

```text
Approved Documentation
        ↓
Relevant Context
        ↓
AI-Assisted Implementation
        ↓
Human Review
        ↓
Tests
        ↓
Documentation Validation
```

AI tools must not be treated as the authority for product decisions.

---

# 38. AI Prompt Context

When using AI-assisted development, provide the relevant documentation rather than relying on a short natural-language description.

Useful context may include:

* `AGENTS.md`;
* relevant business analysis;
* system analysis;
* domain analysis;
* architecture;
* API contract;
* database design;
* security rules;
* testing requirements;
* relevant ADRs;
* development standards.

The goal is to reduce the chance of AI-generated code violating existing project decisions.

---

# 39. AI-Generated Design Decisions

AI may suggest:

* architecture;
* schema;
* API structures;
* libraries;
* patterns;
* implementation strategies.

Suggestions are not automatically project decisions.

A suggested change becomes authoritative only after the normal analysis and decision process.

---

# 40. Documentation Review

Documentation review should evaluate:

### Correctness

Does it describe the intended system?

### Completeness

Are important behaviors and constraints covered?

### Consistency

Does it conflict with other accepted documents?

### Scope

Does it belong in this document?

### Traceability

Can the decision be connected to its requirement or rationale?

### Maintainability

Will future developers understand it?

### Implementation readiness

Is there enough information to implement safely?

---

# 41. Documentation Quality Rules

Documentation should be:

* explicit;
* concise where possible;
* detailed where necessary;
* internally consistent;
* implementation-aware without becoming implementation-bound;
* free from unexplained contradictions;
* structured predictably;
* easy for developers and AI tools to consume.

Avoid:

* vague requirements;
* unexplained acronyms;
* contradictory rules;
* unnecessary repetition;
* undocumented assumptions;
* implementation details in business requirements;
* business rules hidden only in code.

---

# 42. Documentation Naming

Documentation filenames should communicate their purpose.

Preferred pattern:

```text
NN_Clear_Descriptive_Name.md
```

Examples:

```text
08_Database_Development_and_Migration_Workflow.md
09_API_Development_and_Contract_Change_Workflow.md
10_Documentation_First_Development_Workflow.md
```

Naming consistency improves navigation and AI-assisted discovery.

---

# 43. Documentation Structure

A development document should generally contain:

1. Purpose
2. Scope
3. Core principles
4. Detailed rules
5. Workflow
6. Validation/review criteria
7. Anti-patterns
8. Invariants
9. Relationships to other documents
10. Final principle

Not every document requires identical sections, but consistency is preferred.

---

# 44. Documentation Updates

When an accepted decision changes:

```text
Identify affected documents
        ↓
Update authoritative document
        ↓
Update references
        ↓
Update ADR if required
        ↓
Update implementation
        ↓
Update tests
```

A change is incomplete if code is updated but the accepted documentation remains incorrect.

---

# 45. Superseding Documentation

When a decision is replaced, do not silently delete its history when historical context matters.

Use explicit status such as:

```text
Superseded
```

and identify the replacement document or decision.

This preserves architectural history.

---

# 46. Documentation Versioning

Documents should contain version information where required by project standards.

A meaningful document change may require a version update.

Versioning should communicate document evolution rather than become unnecessary administrative overhead.

---

# 47. Documentation Change Categories

Documentation changes can be classified as:

### Editorial

No behavior or decision change.

Examples:

* grammar;
* formatting;
* wording clarification.

### Clarification

Makes existing behavior easier to understand without changing the decision.

### Behavioral

Changes system requirements or expected behavior.

### Architectural

Changes a significant design decision.

### Historical

Records or explains an already completed change.

Behavioral and architectural changes require stronger review than editorial changes.

---

# 48. Documentation-First Pull Request

A significant feature PR should make it possible to understand:

```text
What changed?
Why did it change?
Which documents define it?
How was it implemented?
How was it tested?
What compatibility impact exists?
```

Where relevant, the PR should reference:

* requirements;
* analysis;
* architecture;
* ADR;
* API contract;
* migration;
* tests.

---

# 49. Implementation Readiness Checklist

Before significant coding begins:

* [ ] Requirement is understood.
* [ ] Relevant existing documentation has been reviewed.
* [ ] Business behavior is defined.
* [ ] System workflow is defined.
* [ ] Domain impact is understood.
* [ ] Architecture impact is understood.
* [ ] API impact is identified.
* [ ] Database impact is identified.
* [ ] Security impact is identified.
* [ ] Offline impact is identified where relevant.
* [ ] Testing strategy is understood.
* [ ] Open blocking questions are resolved.
* [ ] Required ADRs are identified.
* [ ] Required documentation changes are accepted.

---

# 50. Documentation Validation After Implementation

After implementation, compare the result against the documentation.

Verify:

* expected workflow exists;
* permissions match;
* states match;
* API behavior matches;
* database behavior matches;
* error behavior matches;
* offline behavior matches;
* tests cover documented critical behavior.

The question is:

> Did we implement what was designed?

not merely:

> Does the code run?

---

# 51. Implementation Discovery Review

Implementation can reveal new information.

For example:

```text
Approved design
      ↓
Implementation
      ↓
Unexpected technical constraint
      ↓
Design reconsideration
```

The discovery must be documented when it changes an approved decision.

This prevents undocumented architecture drift.

---

# 52. Architecture Drift Prevention

Architecture drift occurs when implementation gradually becomes different from approved architecture.

Common causes:

* undocumented shortcuts;
* local exceptions;
* duplicated business rules;
* direct database access;
* bypassing service boundaries;
* frontend-owned business logic;
* undocumented API behavior;
* undocumented infrastructure dependencies.

Documentation-first development helps detect these differences early.

---

# 53. Technical Debt Documentation

Technical debt should be explicit when it affects architecture or future development.

A temporary implementation should not silently become permanent architecture.

Where appropriate, record:

* current limitation;
* reason;
* impact;
* intended future direction;
* conditions for removal.

Technical debt must not be used to justify violating critical security or data-integrity requirements.

---

# 54. Documentation and Refactoring

Refactoring without behavior change normally does not require business documentation changes.

However, architectural refactoring may require documentation updates.

Examples:

```text
Internal function rename
→ usually no documentation change

New application layer
→ architecture/development documentation may change

Database ownership model change
→ domain/architecture/database documentation must change
```

The distinction is behavioral and architectural impact, not merely code size.

---

# 55. Documentation and Bug Fixes

Bug fixes should first determine whether the bug represents:

### Implementation defect

Documentation is correct, code is wrong.

Then:

```text
Fix code
→ add tests
```

### Documentation defect

Documentation describes incorrect behavior.

Then:

```text
Update documentation
→ review decision
→ update implementation if necessary
→ update tests
```

### Requirement gap

The expected behavior was never defined.

Then:

```text
Analyze requirement
→ document decision
→ implement
→ test
```

---

# 56. Documentation and Release

A release should not introduce undocumented intended behavior.

Before release:

* relevant documentation is current;
* API contracts are current;
* migrations are documented;
* security changes are documented;
* operational changes are documented;
* ADRs are updated where required;
* release notes can explain meaningful behavior changes.

---

# 57. Documentation and Rollback

A deployment rollback does not necessarily mean documentation should be rolled back automatically.

Documentation represents approved system intent, while deployment state represents currently running software.

If a release is reverted:

```text
Running Code
↓
Previous Release
```

the documentation change may need to be marked or updated depending on whether the underlying decision itself was rejected or merely not yet deployed.

The distinction between **design state** and **runtime state** must remain clear.

---

# 58. Documentation Repository Hygiene

Documentation repositories must remain organized.

Rules include:

* one clear location per document;
* predictable filenames;
* no duplicate copies;
* no temporary drafts mixed with accepted documents;
* no generated build artifacts;
* no personal notes presented as official decisions;
* cross-references must remain valid;
* obsolete documents must have explicit status.

---

# 59. Documentation as AI Context

The project documentation should be structured so that an AI coding assistant can understand:

```text
What the system is
What the business requires
How the system behaves
How the architecture is organized
What rules must never be violated
How code should be changed
How changes are tested
```

AI tools should receive the smallest relevant set of authoritative documents rather than the entire repository when unnecessary.

This reduces conflicting context and improves implementation accuracy.

---

# 60. AI Context Selection

For a change involving inventory, for example, relevant context may include:

```text
Business Analysis
+
Inventory Domain Analysis
+
Database Design
+
Backend Standards
+
API Contract
+
Security Rules
+
Testing Rules
```

Unrelated documentation does not need to be included unless it affects the change.

Context selection should be deliberate.

---

# 61. Documentation-First Development Example

Consider a new feature:

> Manager can approve a refund within an allowed limit.

The process should be:

```text
Business Analysis
    ↓
Define refund approval requirement
    ↓
System Analysis
    ↓
Define approval workflow
    ↓
Domain Analysis
    ↓
Define refund and approval concepts
    ↓
Security
    ↓
Define who may approve
    ↓
API
    ↓
Define approval endpoint/contract
    ↓
Database
    ↓
Define required persistence
    ↓
Frontend
    ↓
Define user workflow
    ↓
Testing
    ↓
Define expected scenarios
    ↓
Implementation
```

This prevents a developer from independently inventing authorization, API, database, and UI behavior.

---

# 62. Documentation-First Development Example: Schema Change

For a new inventory field:

```text
Requirement
    ↓
Why is the field needed?
    ↓
Domain
    ↓
What does the field mean?
    ↓
Database
    ↓
How is it persisted?
    ↓
Migration
    ↓
How is existing data handled?
    ↓
Backend
    ↓
How is it used?
    ↓
API
    ↓
Should it be exposed?
    ↓
Frontend
    ↓
How is it displayed/edited?
    ↓
Testing
    ↓
How is correctness verified?
```

The database migration is therefore the result of an analyzed requirement, not the starting point.

---

# 63. Documentation-First Development Example: New Role

For a new employee role:

```text
Business Analysis
    ↓
Why does the role exist?
    ↓
System Analysis
    ↓
What can the role do?
    ↓
Security
    ↓
Which permissions are granted?
    ↓
Domain
    ↓
How is the role represented?
    ↓
API
    ↓
How is it managed?
    ↓
Frontend
    ↓
How is it configured?
    ↓
Testing
    ↓
How are authorization boundaries verified?
```

This prevents roles from becoming merely UI labels without defined authority.

---

# 64. Documentation Completion Criteria

Documentation-first work is complete when:

* the intended behavior is explicit;
* relevant documentation is updated;
* important decisions are recorded;
* architecture is consistent;
* implementation follows the approved design;
* tests verify important behavior;
* API contracts are synchronized;
* database changes are synchronized;
* security requirements are synchronized;
* required ADRs exist;
* cross-references remain valid;
* no known undocumented architectural divergence remains.

---

# 65. Documentation-First Invariants

The following rules are mandatory:

1. Significant development must begin from understood requirements.
2. Developers must review existing documentation before designing a new solution.
3. Existing authoritative decisions must not be silently overridden.
4. Business requirements must remain separate from implementation details.
5. System behavior must be explicitly defined for significant workflows.
6. Domain concepts must be understood before persistence structures are finalized.
7. Architecture must be based on approved requirements and analysis.
8. Significant implementation changes must have sufficient design context.
9. Open blocking decisions must not be hidden as developer assumptions.
10. Accepted documentation represents approved project intent.
11. Documentation and code conflicts must be explicitly resolved.
12. Important decisions must have a traceable source.
13. One authoritative source should exist for each major rule.
14. Duplicate sources of truth must be avoided.
15. Significant behavioral changes require documentation updates.
16. Significant architectural changes require architectural review.
17. ADRs must be used for significant architectural decisions.
18. API changes must follow the API contract workflow.
19. Database changes must follow the database migration workflow.
20. Security requirements must be considered before implementation.
21. Tests must verify documented expected behavior.
22. Implementation must not silently redefine business rules.
23. AI-generated suggestions are not project decisions until reviewed.
24. AI-assisted implementation must use relevant authoritative project context.
25. Code that contradicts accepted architecture must be investigated.
26. Implementation discoveries that change design must be documented.
27. Documentation effort must be proportional to change impact.
28. Small implementation changes should not create unnecessary documentation overhead.
29. Release-ready behavior must not contain undocumented intentional changes.
30. Documentation must remain useful to both human developers and AI-assisted development tools.
31. Historical architectural decisions should remain traceable.
32. Technical debt affecting architecture should be explicit.
33. Documentation must evolve with approved system behavior.
34. The final implementation must be validated against the intended design.
35. Documentation-first development exists to reduce uncertainty before code becomes expensive to change.

---

# 66. Relationship to Other Development Documents

This document works together with:

* `01_Development_Architecture_Overview.md`
* `02_Repository_Structure_and_Conventions.md`
* `03_Git_Branching_and_Version_Control_Strategy.md`
* `04_Commit_Message_and_Change_Standards.md`
* `05_Pull_Request_and_Code_Review_Process.md`
* `06_Backend_Development_Standards.md`
* `07_Frontend_Development_Standards.md`
* `08_Database_Development_and_Migration_Workflow.md`
* `09_API_Development_and_Contract_Change_Workflow.md`
* `11_ADR_and_Architecture_Decision_Workflow.md`
* `13_Testing_and_Debugging_Workflow.md`
* `18_Development_Guardrails_and_Quality_Rules.md`

It also depends on the broader project documentation hierarchy:

```text
Business Analysis
        ↓
System Analysis
        ↓
Domain Analysis
        ↓
Architecture
        ↓
Technical Documentation
        ↓
Development
        ↓
Testing
        ↓
Deployment
        ↓
Operations
```

This hierarchy must remain coherent.

---

# 67. Final Principle

Documentation-first development is not about writing documents instead of writing software.

It is about making important decisions before implementation becomes expensive to change.

The development process should therefore follow:

```text
Understand
    ↓
Analyze
    ↓
Decide
    ↓
Document
    ↓
Design
    ↓
Implement
    ↓
Test
    ↓
Review
    ↓
Release
```

**Code is the implementation of an understood and approved system design. Documentation-first development ensures that developers, reviewers, and AI-assisted tools are implementing the same system rather than independently inventing different versions of it.**

