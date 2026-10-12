# Local Development Environment

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/13_Development/README.md`

---

## 1. Purpose

This document defines the standard local development environment for FastFood ERP developers.

It explains how a developer machine should be prepared, how local services should run, how environment configuration should be managed, and how developers should keep local development safe, reproducible, and consistent with the project architecture.

The goal is not to prescribe one specific operating system or hardware configuration.

The goal is to define the expected development environment and the rules that keep local development predictable.

---

# 2. Scope

This document covers:

* developer machine requirements;
* operating-system expectations;
* required development tools;
* source-code setup;
* Git configuration;
* backend runtime;
* frontend runtime;
* PostgreSQL;
* Redis;
* background workers;
* local scheduler;
* local API;
* local frontend;
* local file storage;
* environment variables;
* `.env` files;
* local configuration;
* development secrets;
* database initialization;
* migrations;
* seed data;
* test data;
* service startup;
* service shutdown;
* local networking;
* ports;
* browser configuration;
* debugging;
* logs;
* offline development;
* external integrations;
* local AI development;
* resource management;
* troubleshooting;
* environment consistency;
* developer onboarding;
* security requirements.

This document does not define production deployment architecture.

Production behavior belongs to the Deployment documentation.

---

# 3. Core Principles

Local development must follow these principles:

1. A developer must be able to recreate the environment from documented instructions.
2. Local configuration must not be treated as production configuration.
3. Secrets must never be committed to Git.
4. Development data must be clearly separated from production data.
5. Local services must use predictable configuration.
6. Developers should run only the services required for their current task.
7. Local environments should resemble production architecture where practical.
8. Development convenience must not weaken security assumptions.
9. Environment-specific behavior must be explicit.
10. Database schema changes must use migrations.
11. Local databases must be disposable and reproducible.
12. Seed data must not become an uncontrolled source of business state.
13. External integrations should support safe development modes where possible.
14. Offline behavior must be testable locally.
15. Developers must not depend on undocumented personal machine configuration.
16. Tool versions should be controlled where version differences can affect behavior.
17. Local development must not require production credentials.
18. Debugging must not expose sensitive information.
19. Resource-intensive services should be started only when required.
20. The local environment must support automated testing.

---

# 4. Development Environment Model

The conceptual local environment is:

```text
Developer Machine
│
├── Git
├── Backend Runtime
│   └── FastFood API
│
├── Frontend Runtime
│   └── Web Application
│
├── PostgreSQL
│
├── Redis
│
├── Background Worker
│
├── Scheduler
│
├── Local File Storage
│
├── Test Tools
│
└── Optional AI / Integration Services
```

Not every developer must run every component simultaneously.

The required services depend on the task.

---

# 5. Development Environment Layers

The local environment can be understood as several layers.

## 5.1 Host Layer

The developer's operating system and installed tools.

## 5.2 Runtime Layer

Language runtimes and package managers.

Examples:

* Python;
* Node.js;
* frontend package manager.

## 5.3 Application Layer

The FastFood backend and frontend.

## 5.4 Infrastructure Layer

Local infrastructure services:

* PostgreSQL;
* Redis;
* worker;
* scheduler;
* local file storage.

## 5.5 Test Layer

Automated tests and isolated test resources.

## 5.6 Integration Layer

Optional external systems and local mocks.

---

# 6. Supported Operating Systems

The project should support a defined set of development environments.

Linux should be treated as a first-class development environment.

Windows and macOS may also be supported when project tooling remains compatible.

The project should not depend on undocumented operating-system-specific behavior.

If an operating-system-specific setup is required, it must be documented.

---

# 7. Developer Machine Requirements

The project should define practical minimum and recommended requirements.

Conceptually:

### Minimum

A machine capable of running:

* IDE/editor;
* backend runtime;
* frontend development server;
* PostgreSQL;
* Redis;
* automated tests.

### Recommended

A machine with sufficient memory and CPU capacity to run:

* backend;
* frontend;
* PostgreSQL;
* Redis;
* worker;
* browser;
* tests;
* development tools.

AI development may require substantially more resources and should be treated separately.

The project should avoid unnecessarily high hardware requirements for ordinary ERP development.

---

# 8. Required Developer Tools

A standard developer environment normally includes:

* Git;
* code editor or IDE;
* Python;
* Python virtual environment tooling;
* Node.js;
* frontend package manager;
* PostgreSQL client;
* PostgreSQL server or equivalent local development service;
* Redis;
* browser;
* API testing tools;
* terminal;
* test runner;
* formatter;
* linter.

Additional tools may be required by individual development tasks.

---

# 9. Version Management

Tool versions should be controlled where differences can affect reproducibility.

The project should define or pin important versions for:

* Python;
* Node.js;
* frontend dependencies;
* backend dependencies;
* PostgreSQL compatibility;
* Redis compatibility.

Dependency versions should be defined by project configuration rather than relying on whichever version happens to be installed globally.

---

# 10. Python Environment

Backend development should use an isolated Python environment.

Recommended conceptual structure:

```text
project/
├── backend/
└── .venv/
```

or another project-approved location.

The virtual environment must not be committed to Git.

Developers should activate the environment before running backend commands.

Example:

```bash
source .venv/bin/activate
```

The exact environment setup should follow the project's dependency-management documentation.

---

# 11. Python Dependency Installation

Python dependencies must be installed from the project's declared dependency configuration.

Developers must not manually install arbitrary packages as a permanent environment requirement without updating project dependency definitions.

Dependency changes must follow:

`14_Dependency_and_Package_Management.md`

---

# 12. Frontend Runtime

The frontend requires a supported Node.js runtime and package manager.

The project should define the supported Node.js version using the appropriate project configuration.

Examples of version-management mechanisms may include:

* `.nvmrc`;
* `package.json` engine constraints;
* tool-specific version files.

The chosen mechanism should be consistent across the project.

---

# 13. Global Package Installation

Developers should avoid relying on globally installed project dependencies.

Prefer:

```text
project dependency
        ↓
project package manager
        ↓
reproducible local execution
```

Global tools may be used for general developer utilities, but project behavior should not depend on undocumented global packages.

---

# 14. Repository Setup

A new developer should be able to begin from the repository.

Conceptual workflow:

```text
Clone repository
      ↓
Read README.md
      ↓
Read AGENTS.md
      ↓
Read development documentation
      ↓
Install required runtimes
      ↓
Create local environment
      ↓
Install dependencies
      ↓
Configure environment variables
      ↓
Start local infrastructure
      ↓
Run migrations
      ↓
Load approved seed data
      ↓
Start backend
      ↓
Start frontend
      ↓
Run health checks
      ↓
Run tests
```

The exact commands belong in project onboarding documentation or scripts.

---

# 15. Git Configuration

Each developer should configure Git with:

* user identity;
* appropriate line-ending behavior;
* project-approved hooks where applicable;
* SSH or HTTPS authentication;
* signing configuration if required by project policy.

Developer-specific credentials must remain outside the repository.

---

# 16. Local Directory Hygiene

The repository should remain clean.

Generated local files must not be committed unless explicitly required.

Examples of files that normally remain local:

```text
.venv/
node_modules/
.env
coverage/
.cache/
logs/
tmp/
local database files
IDE settings not shared by the team
generated build output
```

The repository's `.gitignore` must protect common local artifacts.

---

# 17. Environment Configuration

The application must distinguish between code and environment-specific configuration.

Conceptually:

```text
Application Code
       +
Environment Configuration
       =
Runtime
```

Environment configuration may include:

* database connection;
* Redis connection;
* API URLs;
* local ports;
* debug settings;
* logging level;
* storage location;
* feature flags;
* integration mode;
* development-only options.

---

# 18. Environment Variables

Environment variables should be used for values that vary between environments or should not be hard-coded.

Examples:

```text
APP_ENV
DEBUG
DATABASE_URL
REDIS_URL
SECRET_KEY
API_BASE_URL
FRONTEND_BASE_URL
FILE_STORAGE_PATH
```

The exact variable names are defined by the application configuration.

---

# 19. `.env` Files

A local `.env` file may be used for development configuration when supported by the application.

Example:

```text
.env
.env.example
```

`.env` contains local values.

`.env.example` contains safe example values and documents required variables.

The real `.env` must not be committed.

---

# 20. `.env.example`

The project should maintain an `.env.example` containing all required configuration keys without real secrets.

Example:

```text
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql://...
REDIS_URL=redis://...

SECRET_KEY=change-me
```

The example file should be updated whenever required environment variables change.

---

# 21. Local Secrets

Local development should use development-only credentials.

Developers must not use:

* production database passwords;
* production API tokens;
* production signing keys;
* production encryption keys;
* production user credentials;
* production cloud credentials.

If a real external service is required, development credentials must be isolated from production credentials.

---

# 22. Secret Handling

Secrets must never be:

* committed to Git;
* embedded in source code;
* included in screenshots;
* copied into documentation;
* printed into logs;
* placed in test fixtures;
* sent to AI tools unnecessarily.

If a secret is accidentally committed, it must be treated as compromised and rotated according to the security process.

---

# 23. Environment Types

The project should distinguish at least:

```text
development
testing
staging
production
```

Local development normally uses:

```text
APP_ENV=development
```

Tests should use a separate testing configuration.

Production configuration must never be accidentally loaded into local development.

---

# 24. Local PostgreSQL

PostgreSQL is the primary local relational database service when PostgreSQL is part of the project architecture.

Local PostgreSQL should provide:

* a development database;
* a test database or isolated test database strategy;
* a development user;
* appropriate permissions.

Developers should not connect local application code directly to a production database.

---

# 25. Database Naming

Local database names should clearly identify their purpose.

Conceptual examples:

```text
fastfood_dev
fastfood_test
```

Names may vary according to project configuration.

The important rule is that development and testing data are clearly separated.

---

# 26. Database Initialization

A new local database should be initialized through documented project mechanisms.

Typical flow:

```text
Create database
      ↓
Configure connection
      ↓
Run migrations
      ↓
Load approved reference/seed data
      ↓
Run health checks
```

Developers should not manually modify the schema as a normal workflow.

---

# 27. Database Migrations

All schema changes must use the project's migration system.

The local workflow is:

```text
Change schema definition
      ↓
Create migration
      ↓
Review migration
      ↓
Apply migration locally
      ↓
Run tests
```

This follows:

`08_Database_Development_and_Migration_Workflow.md`

---

# 28. Local Database Reset

Developers should be able to reset a development database when necessary.

A reset may include:

* deleting the local database;
* recreating it;
* applying all migrations;
* loading approved seed data.

Reset operations must never target production resources.

---

# 29. Seed Data

Seed data should be controlled and reproducible.

Useful seed data may include:

* system roles;
* permissions;
* supported statuses;
* development reference data;
* sample branches;
* sample products;
* test recipes;
* sample employees.

Seed data should not become a substitute for proper test fixtures.

---

# 30. Test Data

Test data must be isolated from normal development data where practical.

Tests should be able to create predictable state.

Tests must not depend on:

* a developer's personal database state;
* manually created records;
* undocumented seed modifications;
* previous test execution.

---

# 31. Redis

Redis may be used locally for:

* caching;
* background job queues;
* temporary state;
* rate-limiting support;
* other architecture-approved purposes.

Local Redis configuration should be separate from production Redis.

---

# 32. Redis Data Isolation

Development Redis data must not be shared with production.

If multiple local projects share one Redis instance, they must use separate namespaces or databases where appropriate.

The project should prefer explicit isolation over implicit assumptions.

---

# 33. Background Workers

When the architecture uses asynchronous jobs, developers must be able to run a local worker.

Conceptually:

```text
Backend
   ↓
Queue
   ↓
Worker
   ↓
Job execution
```

Examples of background tasks may include:

* notifications;
* report generation;
* synchronization;
* scheduled maintenance;
* asynchronous integrations.

The exact worker technology belongs to the architecture and deployment documentation.

---

# 34. Local Scheduler

If scheduled jobs are part of the application, local development should provide a controlled scheduler mechanism.

Examples:

* subscription reminders;
* cleanup jobs;
* report generation;
* synchronization retries;
* maintenance tasks.

Developers should be able to run scheduled jobs manually for debugging.

---

# 35. Scheduler Safety

Local scheduled jobs must not accidentally affect external or production systems.

Development configuration should ensure:

* local database only;
* development credentials only;
* development notification targets;
* safe integration mode.

---

# 36. Local File Storage

If the application stores files, local development should use local storage unless an external storage service is specifically required.

Conceptually:

```text
Local Application
      ↓
Local Storage
      ↓
Development Files
```

Local files must not be mixed with production storage.

---

# 37. Uploaded Files

Development uploads should use non-sensitive sample files.

Developers must not use real customer or employee documents for ordinary local development.

Where possible, test fixtures should use synthetic data.

---

# 38. Backend Local Server

The backend should expose a predictable local address and port.

Conceptually:

```text
http://localhost:<backend-port>
```

The exact port should be defined by project configuration.

The backend should expose a development health endpoint or equivalent mechanism where appropriate.

---

# 39. Frontend Local Server

The frontend should run using the project's standard development server.

Conceptually:

```text
http://localhost:<frontend-port>
```

The frontend must point to the local backend unless a documented integration environment is intentionally used.

---

# 40. Local Service Ports

Each local service should have a predictable port.

Example conceptual configuration:

```text
Frontend       → local frontend port
Backend API    → local backend port
PostgreSQL     → 5432
Redis          → 6379
```

The actual application ports may differ.

Port conflicts should be solved through documented configuration rather than random machine-specific changes.

---

# 41. Local Network Model

The default development network should be local to the developer machine.

Conceptually:

```text
Browser
   ↓
Frontend
   ↓
Backend
   ↓
PostgreSQL / Redis
```

External network access should only be required for:

* dependency installation;
* approved external integrations;
* documentation;
* source control;
* optional AI services.

---

# 42. CORS

Local frontend/backend communication must use an explicit development CORS configuration when frontend and backend run on different origins.

Development CORS settings must not automatically become production CORS settings.

Broad unrestricted CORS should not be used as a permanent architecture solution.

---

# 43. Local Authentication

Local development should provide a safe authentication mechanism.

Developers may use:

* development users;
* seeded accounts;
* test identities;
* development authentication providers.

Production identity credentials must not be required for ordinary local development.

---

# 44. Local Authorization

Authorization must remain active during local development.

Developers should not disable authorization merely to simplify development.

Development users should have controlled roles and permissions.

This allows authorization behavior to be tested realistically.

---

# 45. Tenant and Branch Context

Local development must preserve the same conceptual isolation rules used by the application.

For example:

```text
Tenant
  ↓
Restaurant Network
  ↓
Branch
  ↓
User / Role
  ↓
Resource
```

Local development must not bypass tenant or branch boundaries simply because the environment is local.

---

# 46. Development Debug Mode

Debug mode may be enabled locally.

Debug mode may provide:

* detailed stack traces;
* development logs;
* debugging tools;
* automatic reload;
* additional diagnostics.

Debug mode must not be enabled in production.

Sensitive information must still be protected even during development.

---

# 47. Logging

Local logging should provide enough information for debugging without creating excessive noise.

Useful categories include:

* application errors;
* warnings;
* database errors;
* background job failures;
* synchronization failures;
* authentication failures;
* integration failures.

Sensitive values must be redacted.

---

# 48. Local Log Storage

Logs may be written to:

* terminal output;
* local log files;
* development logging systems.

Local log files should be excluded from Git unless intentionally required.

Developers should be able to clear local logs without affecting application state.

---

# 49. Error Debugging

A developer should be able to trace an error through:

```text
User Action
    ↓
Frontend
    ↓
API
    ↓
Application Logic
    ↓
Database / Queue / External Service
```

Correlation identifiers should be used where supported by the architecture.

---

# 50. Frontend Debugging

Frontend development should support:

* browser developer tools;
* network inspection;
* console diagnostics;
* component inspection where applicable;
* API request inspection;
* local state inspection;
* error boundary diagnostics.

Debugging output must not expose sensitive data unnecessarily.

---

# 51. Backend Debugging

Backend development should support:

* debugger breakpoints;
* structured logs;
* request inspection;
* database query inspection;
* worker debugging;
* exception tracing.

Developers should prefer reproducible debugging steps over undocumented manual modifications.

---

# 52. Database Debugging

Database debugging may include:

* SQL inspection;
* query plans;
* transaction inspection;
* migration verification;
* index inspection;
* constraint validation.

Database debugging must not bypass application rules when validating application behavior.

---

# 53. API Testing Locally

Developers should be able to test the local API independently of the frontend.

Possible tools include:

* project-provided API clients;
* command-line HTTP clients;
* API testing applications.

API tests should use local credentials and local data.

---

# 54. Local Offline Development

Offline behavior must be testable without depending entirely on real network failures.

Development tools should support scenarios such as:

```text
Online
  ↓
Disconnect
  ↓
Create local transaction
  ↓
Queue operation
  ↓
Reconnect
  ↓
Synchronize
  ↓
Verify result
```

The exact synchronization behavior is defined by the system architecture and relevant testing documentation.

---

# 55. Offline Environment Safety

Offline testing must not accidentally synchronize local test data into production or real external systems.

Local synchronization targets must be explicitly configured.

---

# 56. External Integrations

External services should have development-safe modes where possible.

Examples:

* sandbox APIs;
* mock services;
* local stubs;
* test accounts;
* fake payment providers.

Production integration credentials must not be required for routine local development.

---

# 57. Integration Mocks

Mocks may be used when:

* external service access is unavailable;
* tests must be deterministic;
* external calls are expensive;
* the service has no development environment;
* failure scenarios need controlled reproduction.

Mocks must not hide important integration behavior permanently.

Real integration tests should exist where required.

---

# 58. Local Notifications

Development notifications should be isolated from real users.

Examples:

* email;
* SMS;
* push notifications;
* internal alerts.

Development should preferably use:

* local notification viewers;
* sandbox providers;
* test addresses;
* disabled external delivery.

---

# 59. Payment Development

Payment integrations must use sandbox/test environments.

Developers must never test ordinary payment workflows against production payment credentials.

Financial test data must be clearly identified as non-production.

---

# 60. AI Development Environment

AI functionality may require additional resources or services.

Local AI development may use:

* local models;
* development inference services;
* remote development inference;
* mocked inference responses.

AI development must not require every developer to run large models locally if the project architecture does not require it.

---

# 61. AI Resource Isolation

AI workloads can consume significant CPU, memory, GPU, or storage resources.

Developers should run AI services only when required.

The ordinary ERP development environment should remain usable without unnecessary AI workloads.

---

# 62. Feature Flags

Feature flags may control functionality in local development.

Examples:

```text
ENABLE_AI
ENABLE_OFFLINE_SYNC
ENABLE_EXTERNAL_PAYMENT
ENABLE_BACKGROUND_WORKERS
```

Feature flags must have explicit defaults.

A development flag must not accidentally enable production-only functionality.

---

# 63. Configuration Hierarchy

Configuration should follow a predictable hierarchy.

Conceptually:

```text
Default Application Configuration
        ↓
Environment Configuration
        ↓
Local Development Configuration
        ↓
Runtime Overrides
```

The final configuration must be understandable.

Hidden configuration from IDE plugins or personal shell scripts should not be required for normal development.

---

# 64. Local Configuration Validation

The application should validate required configuration at startup.

For example:

```text
Missing DATABASE_URL
        ↓
Startup validation
        ↓
Clear configuration error
```

The application should fail clearly rather than producing obscure runtime failures later.

---

# 65. Development Health Checks

Developers should be able to verify:

* backend is running;
* database is reachable;
* Redis is reachable;
* migrations are current;
* frontend can reach backend;
* worker is running when required;
* scheduler is running when required.

A local health-check command or endpoint is recommended.

---

# 66. Service Startup Order

Where dependencies exist, services should start in a sensible order.

Conceptually:

```text
PostgreSQL
Redis
   ↓
Backend
   ↓
Worker / Scheduler
   ↓
Frontend
```

The frontend may technically start before the backend, but application functionality requires the backend.

Automated development scripts may manage service startup.

---

# 67. Service Shutdown

Developers should be able to stop local services cleanly.

Clean shutdown is important for:

* database integrity;
* worker state;
* temporary files;
* port availability;
* resource usage.

Force-killing services should be a recovery mechanism, not the normal workflow.

---

# 68. Local Resource Management

Developers should avoid running unnecessary services.

For example:

```text
Backend-only task
→ backend + database

API + worker task
→ backend + database + Redis + worker

Frontend task
→ frontend + backend when API integration is required

AI task
→ required AI service + application components
```

This reduces unnecessary CPU and memory consumption.

---

# 69. Local Performance

Development configuration may intentionally differ from production for speed.

Examples:

* reduced worker count;
* debug logging;
* development reload;
* smaller datasets.

However, developers must not assume local performance represents production performance.

Performance testing belongs to dedicated testing and production-readiness processes.

---

# 70. Local Database Performance

A local PostgreSQL database may run with lower resources than production.

Developers should not use local query timing alone to make production capacity decisions.

Production-scale performance should be validated in controlled performance environments.

---

# 71. Browser and Frontend Environment

Developers should use a supported modern browser.

Browser-specific behavior must be tested when the feature depends on:

* storage;
* printing;
* downloads;
* camera/device access;
* offline functionality;
* browser-specific APIs.

---

# 72. POS and Printing Development

POS development may require local printer testing.

When physical printers are unavailable, developers may use:

* print mocks;
* virtual printers;
* generated receipts;
* controlled test output.

Printer-specific behavior must be tested with real hardware before production release when hardware integration is affected.

---

# 73. Time and Date

Local development should use predictable date/time configuration.

Developers should test:

* business dates;
* timestamps;
* timezone conversion;
* end-of-day behavior;
* scheduled jobs;
* subscription expiration;
* reporting periods.

The application should not depend on the developer's machine timezone without explicit design.

---

# 74. Locale and Language

The local environment should support project-required locale behavior.

Developers should test:

* displayed dates;
* numbers;
* currencies;
* text encoding;
* multilingual content where supported.

Source code should remain consistently encoded.

---

# 75. Local Test Execution

Developers must be able to run:

* unit tests;
* domain tests;
* application tests;
* repository/database tests;
* API tests;
* integration tests;
* frontend tests;
* relevant end-to-end tests.

The exact testing workflow is defined in:

`13_Testing_and_Debugging_Workflow.md`

and the Testing documentation.

---

# 76. Clean Environment Validation

A development setup should be considered reproducible when a new environment can:

```text
Install dependencies
      ↓
Configure environment
      ↓
Create database
      ↓
Apply migrations
      ↓
Load seed data
      ↓
Start services
      ↓
Run tests
```

without relying on undocumented manual changes.

---

# 77. Developer Onboarding

The onboarding process should be short, deterministic, and documented.

A new developer should know:

1. where the repository is;
2. which runtimes are required;
3. how to install dependencies;
4. how to configure `.env`;
5. how to start PostgreSQL;
6. how to start Redis;
7. how to run migrations;
8. how to load seed data;
9. how to start backend;
10. how to start frontend;
11. how to run tests;
12. how to troubleshoot common problems.

---

# 78. Development Setup Automation

Repeated setup tasks should be automated where practical.

Possible mechanisms include:

* shell scripts;
* Makefile;
* task runner;
* container configuration;
* project CLI;
* development bootstrap scripts.

Automation should make the intended workflow easier without hiding important system behavior.

---

# 79. Local Containers

Containers may be used for local infrastructure services when beneficial.

For example:

```text
PostgreSQL container
Redis container
Optional supporting services
```

Containers are not mandatory for every local development task unless required by the architecture.

The project should avoid unnecessary container complexity.

---

# 80. Container and Native Service Consistency

If both native and containerized local services are supported, they should behave consistently enough that developers do not unknowingly test different architectures.

The supported path should be clearly documented.

---

# 81. Local Service Configuration Files

Local service configuration should remain separate from production configuration.

Examples:

```text
docker-compose.dev.yml
.env
config/development.*
```

The exact file structure depends on the project's tooling.

Production credentials and production infrastructure definitions must not be imported automatically.

---

# 82. Dependency Availability

Local development should not assume permanent internet access after dependencies are installed.

Where practical:

* dependencies should be lockable;
* package versions should be reproducible;
* local caches may be used;
* development scripts should fail clearly when network access is required.

This is particularly important for offline branch-related development and controlled developer environments.

---

# 83. Development Data Privacy

Development data should normally be synthetic.

If sanitized production-like data is required for debugging:

* it must be approved;
* sensitive fields must be removed or transformed;
* access must be controlled;
* the data must not be committed;
* the data must not be sent to external AI tools.

---

# 84. Production Data Prohibition

Developers must not connect ordinary local development tools to production databases or production storage.

Any exceptional production diagnostic access must follow the security and operations procedures.

Local configuration should make accidental production access difficult.

---

# 85. Local Security Boundaries

Development is less restrictive than production, but important security boundaries must remain active.

At minimum, local development should preserve:

* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* input validation;
* API contract validation;
* database constraints;
* audit-related behavior where applicable.

---

# 86. Development Caches

Local caches may be cleared freely when debugging cache-related problems.

A developer should be able to determine whether an issue is caused by:

* application state;
* database state;
* cache state;
* browser state.

Cache clearing should not require deleting unrelated development data.

---

# 87. Local Queue Recovery

Developers should be able to inspect and clear development queues.

Failed local jobs should be reproducible.

Queue cleanup must not affect external or production queues.

---

# 88. Common Local Problems

Typical problems include:

### Port already in use

Identify the process using the port and stop or reconfigure it.

### Database unavailable

Verify PostgreSQL is running and the connection configuration is correct.

### Redis unavailable

Verify Redis is running and `REDIS_URL` is correct.

### Migration failure

Inspect the migration and database state; do not manually modify the schema to hide the problem.

### Dependency mismatch

Verify the runtime version and lock/dependency configuration.

### Frontend cannot reach backend

Check:

* backend status;
* API URL;
* CORS;
* port;
* browser network errors.

### Worker not processing jobs

Check:

* Redis;
* worker process;
* queue configuration;
* job errors.

---

# 89. Environment Diagnostics

The project should provide a practical diagnostic method.

A developer should be able to determine:

```text
Application version
Python/Node version
Database connection
Redis connection
Environment type
Migration state
Configuration validity
```

without manually inspecting unrelated files.

---

# 90. Local Environment Reset

When the environment becomes inconsistent, developers should have a documented recovery path.

Conceptually:

```text
Stop services
      ↓
Remove local generated state
      ↓
Recreate virtual environment/dependencies if necessary
      ↓
Recreate development database if necessary
      ↓
Apply migrations
      ↓
Load seed data
      ↓
Restart services
      ↓
Run health checks
```

Reset procedures must clearly identify destructive local operations.

---

# 91. Development Environment and Git

Environment changes that affect the whole team should be committed as project configuration.

Examples:

* dependency changes;
* required environment variables;
* startup scripts;
* migration changes;
* shared tooling configuration.

Personal machine settings should remain local.

---

# 92. Environment Documentation Updates

When a developer introduces a new required local service or environment variable, documentation must be updated.

At minimum, review:

* `README.md`;
* `.env.example`;
* `AGENTS.md` if relevant;
* dependency documentation;
* local development documentation;
* relevant architecture documentation.

A new dependency must not exist only in one developer's machine.

---

# 93. Development Environment and CI

Local development and CI should use compatible commands where practical.

Example:

```text
Local:
run tests

CI:
run the same test command
```

Differences may exist because CI is isolated, but developers should be able to reproduce CI failures locally.

---

# 94. Development Environment and Deployment

Local development should reflect important production assumptions without reproducing the entire production environment.

For example:

```text
Local
├── PostgreSQL
├── Redis
├── Backend
├── Worker
└── Frontend

Production
├── Managed/Production PostgreSQL
├── Production Redis
├── Backend instances
├── Worker instances
├── Frontend delivery
└── Monitoring
```

The exact production topology belongs to the Deployment documentation.

---

# 95. Local Environment Completion Criteria

A developer environment is ready when:

* repository is cloned;
* required runtimes are installed;
* dependencies are installed;
* local configuration exists;
* secrets are local and non-production;
* database is available;
* migrations are applied;
* seed data is available when required;
* Redis is available when required;
* backend starts;
* frontend starts;
* required workers start;
* health checks pass;
* relevant tests pass.

---

# 96. Local Development Checklist

```text
[ ] Repository cloned
[ ] README.md reviewed
[ ] AGENTS.md reviewed
[ ] Required runtime versions installed
[ ] Python environment created
[ ] Frontend dependencies installed
[ ] Backend dependencies installed
[ ] .env created
[ ] .env.example reviewed
[ ] No production credentials used
[ ] PostgreSQL available
[ ] Development database created
[ ] Migrations applied
[ ] Seed data loaded if required
[ ] Redis available if required
[ ] Worker available if required
[ ] Scheduler available if required
[ ] Backend starts
[ ] Frontend starts
[ ] API reachable
[ ] Health checks pass
[ ] Tests run successfully
```

---

# 97. Developer Environment Invariants

The following rules are mandatory:

1. Local development must use isolated environment configuration.
2. Production credentials must not be required for normal local development.
3. Production databases must not be used as local development databases.
4. Local secrets must not be committed.
5. `.env` files containing secrets must remain ignored.
6. `.env.example` must document required variables.
7. Database schema changes must use migrations.
8. Local test state must be reproducible.
9. Seed data must be controlled.
10. Test data must not depend on personal database state.
11. PostgreSQL development data must be isolated.
12. Redis development data must be isolated.
13. Background workers must use development queues.
14. Schedulers must use development configuration.
15. External integrations must use safe development modes.
16. Payment testing must use sandbox/test environments.
17. Notifications must not accidentally reach real users.
18. Local authentication must remain enabled.
19. Local authorization must remain enabled.
20. Tenant isolation must remain testable locally.
21. Branch isolation must remain testable locally.
22. Debug mode must never be assumed safe for production.
23. Sensitive values must not appear in logs.
24. Local uploaded files must not contain unnecessary sensitive data.
25. AI tools must not receive secrets or sensitive development data unnecessarily.
26. Required local services must be documented.
27. Shared environment changes must be committed to project configuration.
28. Personal machine configuration must not become a hidden project dependency.
29. Local service ports must be documented or configurable.
30. Developers must be able to diagnose common environment failures.
31. Developers must be able to reset local development state safely.
32. Local and CI workflows should remain compatible.
33. Development environment setup must be reproducible.
34. Resource-heavy services should run only when required.
35. Local performance must not be treated as production performance evidence.
36. Production architecture must not be accidentally loaded into local development.
37. Local service shutdown must be safe.
38. Environment-specific behavior must be explicit.
39. New required dependencies must update documentation.
40. The local environment must support the project's testing strategy.

---

# 98. Relationship to Other Development Documents

This document depends on and supports:

### DEV-01 — Development Architecture Overview

Defines the overall development lifecycle.

### DEV-02 — Repository Structure and Conventions

Defines repository organization and environment-related files.

### DEV-03 — Git Branching and Version Control Strategy

Defines source-control behavior.

### DEV-06 — Backend Development Standards

Defines backend development practices.

### DEV-07 — Frontend Development Standards

Defines frontend development practices.

### DEV-08 — Database Development and Migration Workflow

Defines database schema and migration behavior.

### DEV-09 — API Development and Contract Change Workflow

Defines API development.

### DEV-10 — Documentation-First Development Workflow

Defines how environment changes are documented before implementation when required.

### DEV-11 — ADR and Architecture Decision Workflow

Defines architectural decisions that may affect the development environment.

### DEV-13 — Testing and Debugging Workflow

Defines local testing and debugging procedures.

### DEV-14 — Dependency and Package Management

Defines dependency installation and version management.

### DEV-15 — Configuration and Feature Flag Development

Defines application configuration and feature flags.

### DEV-16 — AI-Assisted Development Guidelines

Defines safe AI-assisted development.

### DEV-17 — Developer Tooling and Automation

Defines development scripts and automation.

### DEV-18 — Development Guardrails and Quality Rules

Defines overall development restrictions and quality rules.

---

# 99. Relationship to Deployment

Local development must not be confused with deployment.

The Deployment documentation defines:

* production infrastructure;
* production environments;
* deployment topology;
* production networking;
* TLS;
* production database;
* production Redis;
* workers;
* scaling;
* monitoring;
* disaster recovery.

This document only defines the developer-facing local environment.

---

# 100. Final Principle

A good local development environment should make the correct development workflow easy, reproducible, safe, and understandable.

A developer should be able to move from:

```text
Clone
  ↓
Configure
  ↓
Install
  ↓
Initialize
  ↓
Run
  ↓
Test
  ↓
Debug
  ↓
Develop
```

without relying on undocumented machine-specific knowledge.

**Final rule:**

**The local environment must be reproducible, isolated from production, aligned with the project architecture, safe for development data, and simple enough that developers can focus on building the system rather than maintaining their machines.**

