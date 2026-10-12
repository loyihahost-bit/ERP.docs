# Development

**Status:** Accepted
**Version:** 1.0
**Section:** `docs/13_Development`

---

## 1. Purpose

This directory defines the development standards, workflows, tools, and quality guardrails for the FastFood ERP project.

The development documentation translates approved requirements, architecture decisions, and technical designs into a controlled software development process.

The section covers:

* repository organization;
* Git workflow;
* commits and pull requests;
* backend and frontend development;
* database and API changes;
* documentation-first development;
* architecture decisions;
* local development;
* testing and debugging;
* dependency management;
* configuration and feature flags;
* AI-assisted development;
* developer tooling and automation;
* development guardrails and quality rules.

---

# 2. Development Documentation Map

| #      | Document                                                                                                     | Purpose                                                                                                                         |
| ------ | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| DEV-01 | [`01_Development_Architecture_Overview.md`](./01_Development_Architecture_Overview.md)                       | Defines the overall development lifecycle, development responsibilities, change flow, and engineering principles.               |
| DEV-02 | [`02_Repository_Structure_and_Conventions.md`](./02_Repository_Structure_and_Conventions.md)                 | Defines repository organization, naming conventions, module boundaries, and repository hygiene.                                 |
| DEV-03 | [`03_Git_Branching_and_Version_Control_Strategy.md`](./03_Git_Branching_and_Version_Control_Strategy.md)     | Defines branches, Git workflow, versioning, merge strategy, tags, and release traceability.                                     |
| DEV-04 | [`04_Commit_Message_and_Change_Standards.md`](./04_Commit_Message_and_Change_Standards.md)                   | Defines commit structure, commit quality, change traceability, and commit message standards.                                    |
| DEV-05 | [`05_Pull_Request_and_Code_Review_Process.md`](./05_Pull_Request_and_Code_Review_Process.md)                 | Defines pull requests, review responsibilities, approval rules, merge requirements, and review quality.                         |
| DEV-06 | [`06_Backend_Development_Standards.md`](./06_Backend_Development_Standards.md)                               | Defines backend implementation standards, layering, domain/application boundaries, error handling, and maintainability rules.   |
| DEV-07 | [`07_Frontend_Development_Standards.md`](./07_Frontend_Development_Standards.md)                             | Defines frontend architecture, components, state, API integration, UX states, performance, and frontend quality rules.          |
| DEV-08 | [`08_Database_Development_and_Migration_Workflow.md`](./08_Database_Development_and_Migration_Workflow.md)   | Defines database schema changes, migrations, data migrations, compatibility, testing, and database development workflow.        |
| DEV-09 | [`09_API_Development_and_Contract_Change_Workflow.md`](./09_API_Development_and_Contract_Change_Workflow.md) | Defines API development, contracts, compatibility, validation, errors, versioning, and API change workflow.                     |
| DEV-10 | [`10_Documentation_First_Development_Workflow.md`](./10_Documentation_First_Development_Workflow.md)         | Defines the documentation-first process from requirements and analysis through design, implementation, testing, and release.    |
| DEV-11 | [`11_ADR_and_Architecture_Decision_Workflow.md`](./11_ADR_and_Architecture_Decision_Workflow.md)             | Defines when and how architecture decisions are documented, reviewed, accepted, superseded, and traced.                         |
| DEV-12 | [`12_Local_Development_Environment.md`](./12_Local_Development_Environment.md)                               | Defines reproducible local development environments, configuration, local services, debugging, and developer setup.             |
| DEV-13 | [`13_Testing_and_Debugging_Workflow.md`](./13_Testing_and_Debugging_Workflow.md)                             | Defines local testing, debugging, failure investigation, test isolation, and development validation workflows.                  |
| DEV-14 | [`14_Dependency_and_Package_Management.md`](./14_Dependency_and_Package_Management.md)                       | Defines dependency selection, version control, lock files, updates, security, and package maintenance.                          |
| DEV-15 | [`15_Configuration_and_Feature_Flag_Development.md`](./15_Configuration_and_Feature_Flag_Development.md)     | Defines development configuration, environment behavior, feature flags, defaults, and configuration safety.                     |
| DEV-16 | [`16_AI_Assisted_Development_Guidelines.md`](./16_AI_Assisted_Development_Guidelines.md)                     | Defines safe and controlled use of AI coding tools, validation, review, security, and AI-generated code handling.               |
| DEV-17 | [`17_Developer_Tooling_and_Automation.md`](./17_Developer_Tooling_and_Automation.md)                         | Defines scripts, formatting, linting, static analysis, pre-commit checks, automation, and developer tooling.                    |
| DEV-18 | [`18_Development_Guardrails_and_Quality_Rules.md`](./18_Development_Guardrails_and_Quality_Rules.md)         | Defines mandatory development guardrails, quality rules, architectural boundaries, security rules, and completion requirements. |

---

# 3. Development Lifecycle

The development section follows this general lifecycle:

```text
Approved Requirement
        ↓
Business / System / Domain Analysis
        ↓
Architecture / Technical Design
        ↓
Documentation
        ↓
Development Planning
        ↓
Implementation
        ↓
Automated Validation
        ↓
Testing
        ↓
Code Review
        ↓
Integration
        ↓
Release Preparation
        ↓
Deployment
        ↓
Operations
```

Development documentation primarily governs the activities from development planning through release preparation.

---

# 4. Development Documentation Relationships

The documents are complementary.

They should be understood as a system rather than independent instructions.

```text
DEV-01
Development Architecture
        │
        ├── DEV-02 Repository
        ├── DEV-03 Git
        ├── DEV-04 Commits
        ├── DEV-05 Pull Requests
        │
        ├── DEV-06 Backend
        ├── DEV-07 Frontend
        ├── DEV-08 Database
        ├── DEV-09 API
        │
        ├── DEV-10 Documentation First
        ├── DEV-11 ADR
        │
        ├── DEV-12 Local Environment
        ├── DEV-13 Testing & Debugging
        ├── DEV-14 Dependencies
        ├── DEV-15 Configuration & Flags
        ├── DEV-16 AI-Assisted Development
        ├── DEV-17 Tooling & Automation
        │
        └── DEV-18 Guardrails & Quality Rules
```

---

# 5. Development Documentation Hierarchy

The development section sits below the project's higher-level product and technical documentation.

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
        ↓
10_Deployment
11_Security
12_Testing
        ↓
13_Development
        ↓
14_Operations
        ↓
15_Future
```

The development section does not redefine business requirements or architectural decisions.

It provides the controlled process for implementing them.

---

# 6. Source-of-Truth Rules

When implementing a change, developers should use the appropriate source of truth.

| Concern                     | Primary Source         |
| --------------------------- | ---------------------- |
| Business behavior           | `01_Business_Analysis` |
| System behavior             | `02_System_Analysis`   |
| Domain rules                | `03_Domain_Analysis`   |
| Architecture                | `04_Architecture`      |
| Database design             | `05_Database`          |
| Backend design              | `06_Backend`           |
| Frontend design             | `07_Frontend`          |
| AI architecture             | `08_AI`                |
| API contract                | `09_API`               |
| Deployment                  | `10_Deployment`        |
| Security                    | `11_Security`          |
| Testing                     | `12_Testing`           |
| Development workflow        | `13_Development`       |
| Runtime operations          | `14_Operations`        |
| Future/planned capabilities | `15_Future`            |
| Architecture decisions      | `ADR` documents        |

If a development discovery conflicts with an existing source of truth, the conflict must be resolved explicitly rather than silently overriding the existing decision.

---

# 7. Development Change Flow

A meaningful development change should normally follow:

```text
1. Identify requirement
        ↓
2. Search existing documentation
        ↓
3. Identify affected domains
        ↓
4. Identify architecture impact
        ↓
5. Identify database/API/security/testing impact
        ↓
6. Update documentation or create decision records if required
        ↓
7. Implement
        ↓
8. Run focused validation
        ↓
9. Run broader validation according to risk
        ↓
10. Review
        ↓
11. Merge
        ↓
12. Release when approved
```

---

# 8. Risk-Based Development

Not every change has the same risk.

Changes should be evaluated according to their potential impact.

### Lower-risk examples

* documentation typo;
* internal naming improvement;
* isolated UI styling;
* non-functional refactoring with strong test coverage.

### Medium-risk examples

* API response changes;
* database index changes;
* shared frontend components;
* dependency upgrades;
* permission-related UI behavior.

### High-risk examples

* financial logic;
* inventory logic;
* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* synchronization;
* database migrations;
* subscription enforcement;
* production configuration;
* security boundaries.

Higher-risk changes require stronger analysis and validation.

---

# 9. Quality Model

Development quality is evaluated across multiple dimensions:

```text
Correctness
    +
Security
    +
Data Integrity
    +
Architecture
    +
Testing
    +
Maintainability
    +
Performance
    +
Compatibility
    +
Operational Safety
    +
Documentation
```

A change should not be considered high quality merely because it compiles or passes a small number of tests.

---

# 10. Development Completion Model

A development change is considered complete when the applicable requirements have been satisfied:

```text
Requirement understood
        ↓
Design aligned
        ↓
Implementation complete
        ↓
Security considered
        ↓
Tests appropriate to risk
        ↓
Static validation
        ↓
Code review
        ↓
Documentation aligned
        ↓
Release impact understood
```

---

# 11. Guardrails

`18_Development_Guardrails_and_Quality_Rules.md` is the final enforcement-oriented document of this section.

It defines rules covering:

* business correctness;
* architecture boundaries;
* tenant isolation;
* branch isolation;
* authorization;
* financial integrity;
* inventory integrity;
* database integrity;
* API contracts;
* concurrency;
* offline synchronization;
* frontend authority boundaries;
* secrets;
* dependencies;
* testing;
* AI-assisted development;
* Git;
* code review;
* tooling;
* production safety;
* release readiness.

When a specific development document provides the detailed process and DEV-18 defines a mandatory guardrail, the guardrail must be respected.

---

# 12. Development and Testing

Development and testing are directly connected.

The development workflow determines when validation occurs.

The testing section determines how testing itself is architected.

```text
13_Development
      ↓
What developers must validate
      ↓
12_Testing
      ↓
How validation is designed and executed
```

The two sections must remain consistent.

---

# 13. Development and Security

Development must preserve the security architecture.

```text
13_Development
      ↓
Secure implementation
      ↓
11_Security
      ↓
Security policy and boundaries
```

Security must not be treated as a final review step only.

Security requirements must influence implementation from the beginning.

---

# 14. Development and Deployment

Development changes eventually become deployment artifacts.

```text
Development
    ↓
Build
    ↓
Release
    ↓
Deployment
```

Changes affecting:

* configuration;
* migrations;
* dependencies;
* infrastructure;
* runtime behavior;
* workers;
* scheduled jobs;

must consider the deployment architecture.

---

# 15. Development and Operations

Development must consider how software will behave after release.

Relevant concerns include:

* logging;
* monitoring;
* failure recovery;
* migrations;
* configuration;
* background jobs;
* scheduled tasks;
* operational diagnostics.

Development should not create functionality that cannot be reasonably operated.

---

# 16. AI-Assisted Development

AI tools may assist development, but they do not become the project's source of truth.

The developer remains responsible for:

* correctness;
* architecture;
* security;
* testing;
* dependencies;
* documentation;
* final implementation.

See:

`16_AI_Assisted_Development_Guidelines.md`

for detailed rules.

---

# 17. Developer Tooling

Developer tooling should automate repetitive validation without hiding failures.

Relevant tooling includes:

* formatters;
* linters;
* static analyzers;
* test runners;
* pre-commit hooks;
* repository validation;
* database helpers;
* documentation validation.

See:

`17_Developer_Tooling_and_Automation.md`

for detailed standards.

---

# 18. Development Guardrails

The most important development rules are:

1. Do not invent undocumented business behavior.
2. Do not bypass accepted architecture.
3. Do not rely on frontend-only security.
4. Do not bypass tenant or branch isolation.
5. Do not commit secrets.
6. Do not bypass critical business invariants.
7. Do not silently alter historical data.
8. Do not perform uncontrolled schema changes.
9. Do not introduce breaking API behavior without explicit handling.
10. Do not hide failures.
11. Do not normalize flaky tests.
12. Do not merge unreviewed meaningful changes.
13. Do not treat AI-generated code as trusted automatically.
14. Do not use production data casually in development.
15. Do not allow convenience to weaken security or data integrity.
16. Do not allow temporary shortcuts to become undocumented permanent architecture.

The complete rules are defined in DEV-18.

---

# 19. Recommended Developer Reading Order

For a developer joining the project:

```text
01 Development Architecture Overview
        ↓
02 Repository Structure and Conventions
        ↓
12 Local Development Environment
        ↓
03 Git Branching and Version Control
        ↓
04 Commit Message and Change Standards
        ↓
05 Pull Request and Code Review
        ↓
06 Backend / 07 Frontend
        ↓
08 Database / 09 API
        ↓
10 Documentation First
        ↓
11 ADR Workflow
        ↓
13 Testing and Debugging
        ↓
14 Dependencies
        ↓
15 Configuration and Feature Flags
        ↓
16 AI-Assisted Development
        ↓
17 Developer Tooling
        ↓
18 Guardrails and Quality Rules
```

Developers should also read the relevant technical documentation before modifying a specific subsystem.

---

# 20. Change Impact Map

When changing a subsystem, developers should consider the following relationships:

| Change              | Review                                                  |
| ------------------- | ------------------------------------------------------- |
| Business rule       | Business, System, Domain, Backend, API, Testing         |
| Backend logic       | Backend, Domain, API, Testing, Security                 |
| Frontend behavior   | Frontend, API, Testing, Security                        |
| Database schema     | Database, Backend, API, Deployment, Testing             |
| API contract        | API, Backend, Frontend, Testing, Security               |
| Authentication      | Security, Backend, API, Frontend, Testing               |
| Authorization       | Security, Backend, API, Frontend, Testing               |
| Inventory           | Domain, Database, Backend, Testing                      |
| Recipes             | Domain, Database, Backend, Frontend, Testing            |
| Cash/financial      | Domain, Database, Backend, Security, Testing            |
| Offline sync        | Architecture, Backend, API, Frontend, Database, Testing |
| Subscription        | Business, Backend, API, Security, Testing               |
| Dependency          | Development, Security, Deployment, Testing              |
| Configuration       | Development, Deployment, Security, Operations           |
| Feature flag        | Development, Frontend/Backend, Testing, Operations      |
| AI functionality    | AI, Backend, API, Security, Testing                     |
| Deployment behavior | Deployment, Development, Operations                     |
| Developer tooling   | Development, Security, CI/CD, Testing                   |

This table is a starting point, not a replacement for change impact analysis.

---

# 21. Document Status

All documents listed in this README are part of the accepted Development documentation set.

Current section status:

```text
DEV-01  Accepted
DEV-02  Accepted
DEV-03  Accepted
DEV-04  Accepted
DEV-05  Accepted
DEV-06  Accepted
DEV-07  Accepted
DEV-08  Accepted
DEV-09  Accepted
DEV-10  Accepted
DEV-11  Accepted
DEV-12  Accepted
DEV-13  Accepted
DEV-14  Accepted
DEV-15  Accepted
DEV-16  Accepted
DEV-17  Accepted
DEV-18  Accepted
```

---

# 22. Maintenance Rules

This README must be updated when:

* a development document is added;
* a development document is removed;
* a filename changes;
* a document is superseded;
* the development documentation structure changes;
* an important relationship changes.

The README should remain a reliable map of the section.

It must not become a duplicate copy of the detailed development rules.

---

# 23. Development Section Invariants

1. Every development document must have a clear purpose.
2. Every development document must have a stable filename.
3. The README must map all active development documents.
4. Development documents must not contradict accepted higher-level decisions.
5. Development documentation must remain connected to architecture.
6. Development workflow must remain documentation-first.
7. Meaningful changes must remain traceable.
8. Development rules must remain consistent with security requirements.
9. Development rules must remain consistent with testing requirements.
10. Development rules must remain compatible with deployment requirements.
11. Developer tooling must support, not bypass, development guardrails.
12. AI-assisted development must remain subject to human validation.
13. Development documentation must evolve when development practice changes.
14. Duplicate sources of truth must be avoided.
15. Important development decisions must remain historically traceable.

---

# 24. Final Principle

The Development section defines how approved system decisions become reliable software.

It does not replace business analysis, architecture, security, testing, or operations.

Instead, it connects them into a controlled engineering workflow:

> **Understand the requirement, respect the architecture, document the decision, implement deliberately, validate the behavior, review the change, and release only when the system remains correct, secure, maintainable, and operationally safe.**

