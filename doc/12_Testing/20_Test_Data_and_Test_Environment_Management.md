# TEST-20 — Test Data and Test Environment Management

**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`

---

## 1. Purpose

This document defines the architecture, policies, and operating rules for managing test data and test environments across the FastFood ERP testing lifecycle.

The purpose is to ensure that tests are:

* deterministic;
* reproducible;
* isolated;
* safe;
* representative of real business conditions;
* independent from production data;
* suitable for local development, CI, integration, E2E, performance, resilience, and release testing;
* compatible with security and privacy requirements;
* maintainable as the system evolves.

Testing quality depends not only on test code, but also on the correctness and reliability of the data and environment in which tests execute.

A test that passes only because of accidental shared state, stale fixtures, unrealistic data, or an incorrectly configured environment does not provide reliable evidence.

---

## 2. Scope

This document covers:

* test data lifecycle;
* synthetic test data;
* fixtures;
* factories and builders;
* seed/reference data;
* anonymization and pseudonymization;
* sensitive data protection;
* tenant and branch test isolation;
* financial test data;
* inventory and recipe test data;
* POS test data;
* offline and synchronization data;
* security test data;
* file and document test data;
* AI/model test datasets where applicable;
* database test environments;
* local development environments;
* CI environments;
* integration environments;
* E2E environments;
* staging and release-test environments;
* performance and resilience environments;
* environment provisioning;
* configuration management;
* environment drift;
* test data cleanup and reset;
* test data retention;
* reproducibility;
* access control;
* environment health;
* test artifacts and evidence.

This document does not replace:

* production deployment architecture;
* production data protection policy;
* security architecture;
* database architecture;
* deployment environment architecture;
* individual testing strategies defined by TEST-01 through TEST-19.

Instead, it defines the testing-specific data and environment requirements that those documents depend on.

---

# 3. Core Principles

## 3.1 Test Data Is Part of the Test System

Test data is not an incidental setup detail.

It is part of the testing architecture and must be versioned, controlled, reproducible, and understandable.

---

## 3.2 Production Data Is Not the Default Test Dataset

Production data must never be copied into test environments merely for convenience.

Synthetic data should be the default.

If production-derived data is ever required for a justified testing purpose, it must go through an approved data-protection process and must not expose unnecessary sensitive information.

---

## 3.3 Isolation Is Mandatory

Test environments and test datasets must be isolated from:

* production databases;
* production credentials;
* production queues;
* production payment systems;
* production customer data;
* production employee data;
* production devices;
* production printers;
* production external integrations.

A test must never accidentally modify production state.

---

## 3.4 Determinism

A test should produce the same result when executed under the same controlled conditions.

Test data should therefore control:

* timestamps;
* identifiers where necessary;
* random values;
* ordering;
* initial state;
* configuration;
* external dependencies;
* feature flags;
* subscription state;
* branch state.

---

## 3.5 Realistic Business Data

Synthetic data must still represent realistic business conditions.

For example, inventory tests should not use only trivial products.

They should include scenarios such as:

* raw ingredients;
* semi-finished products;
* recipes;
* recipe versions;
* FIFO stock;
* multiple stock batches;
* yield loss;
* low-stock thresholds;
* multiple warehouses;
* branch-specific inventory;
* insufficient stock.

---

## 3.6 No Shared Mutable Test State

Tests must not depend on mutable data created by another unrelated test.

Shared immutable reference data may be allowed where safe.

Shared mutable business state should generally be avoided.

---

## 3.7 Security Rules Apply to Test Environments

Test environments are not exempt from security requirements.

They must still protect:

* credentials;
* authentication data;
* employee information;
* payroll information;
* customer information;
* delivery information;
* financial data;
* device identities;
* API credentials;
* integration secrets;
* audit information.

---

# 4. Test Data Lifecycle

Test data follows a controlled lifecycle:

```text
Define
  ↓
Generate
  ↓
Validate
  ↓
Provision
  ↓
Use
  ↓
Verify
  ↓
Reset / Clean
  ↓
Retain or Destroy
```

Each stage has a defined responsibility.

---

## 4.1 Define

Before creating a dataset, the test purpose should be known.

Examples:

* POS checkout;
* refund;
* cash shortage;
* FIFO deduction;
* recipe modification;
* authorization testing;
* offline synchronization;
* performance testing;
* migration testing.

Data should be created according to the behavior being tested rather than randomly.

---

## 4.2 Generate

Data should preferably be generated through controlled:

* factories;
* builders;
* fixtures;
* seed scripts;
* deterministic generators;
* dataset generators.

Generation should produce valid data unless the test explicitly requires invalid or adversarial data.

---

## 4.3 Validate

Generated test data must satisfy the assumptions required by the test.

Validation may include:

* required relationships exist;
* tenant relationships are correct;
* branch relationships are correct;
* foreign keys are valid;
* recipes reference valid products;
* inventory quantities are valid;
* cash sessions are valid;
* permissions are correctly configured;
* subscription state is intentional.

---

## 4.4 Provision

Data should be inserted into the target environment using controlled mechanisms.

Provisioning must not depend on manually entering large amounts of data.

---

## 4.5 Use

Tests consume the prepared dataset.

Tests should clearly identify which data they own and which reference data they depend on.

---

## 4.6 Verify

After critical tests, the expected final state should be verified.

For example:

```text
Order Created
      ↓
Payment Completed
      ↓
Inventory Deducted
      ↓
Cash Updated
      ↓
Audit Recorded
```

The test should verify the complete intended state rather than only checking that an API returned success.

---

## 4.7 Reset or Clean

After execution, mutable state must be reset or removed according to the environment's lifecycle policy.

The reset mechanism may include:

* transaction rollback;
* database truncation;
* fixture cleanup;
* database recreation;
* schema recreation;
* environment replacement.

The selected strategy must preserve test isolation.

---

# 5. Test Data Categories

Test data should be classified according to its purpose.

## 5.1 Reference Data

Stable data required by many tests.

Examples:

* product categories;
* order types;
* status definitions;
* permission definitions;
* supported payment types;
* standard roles.

Reference data should be version-controlled.

---

## 5.2 Business Fixture Data

Data representing realistic business states.

Examples:

* restaurant network;
* branches;
* employees;
* menus;
* products;
* recipes;
* warehouses;
* inventory batches;
* orders;
* cash sessions.

---

## 5.3 Scenario Data

Data specifically created for one behavior.

Examples:

* an order requiring refund approval;
* a branch with insufficient stock;
* an employee with restricted permissions;
* an expired subscription;
* an offline device with pending operations.

---

## 5.4 Negative Test Data

Data intentionally violating expected rules.

Examples:

* invalid identifiers;
* missing required fields;
* invalid quantities;
* duplicate operations;
* unauthorized branch references;
* malformed files;
* invalid recipe relationships.

Negative data must be clearly marked so that it is not accidentally reused as valid business data.

---

## 5.5 Boundary Data

Data designed around limits.

Examples:

* zero quantity;
* minimum quantity;
* maximum allowed quantity;
* maximum page size;
* maximum import size;
* long names;
* large order counts;
* large inventory datasets;
* large synchronization queues.

---

## 5.6 Performance Data

Large datasets designed for:

* load testing;
* stress testing;
* soak testing;
* query performance;
* report generation;
* synchronization performance;
* import/export testing.

Performance data should represent realistic distributions rather than simply generating the same record repeatedly.

---

# 6. Fixtures, Factories, and Builders

## 6.1 Fixtures

Fixtures represent known starting states.

A fixture should be:

* deterministic;
* documented;
* minimal;
* reusable;
* isolated from unrelated scenarios.

Example:

```text
Restaurant
  └── Branch A
       ├── Cashier
       ├── Product
       ├── Recipe
       └── Inventory Batch
```

---

## 6.2 Factories

Factories generate test entities with sensible defaults.

Factories should allow tests to override only the values relevant to the scenario.

For example:

```text
create_product()
create_employee()
create_branch()
create_recipe()
create_inventory_batch()
create_order()
create_cash_session()
```

Defaults must represent valid business states.

---

## 6.3 Builders

Builders are useful when scenarios require complex state.

Example:

```text
OrderBuilder
  → branch
  → cashier
  → products
  → discount
  → payment
  → delivery information
  → final status
```

Builders should make important scenario assumptions visible.

---

## 6.4 Avoid Giant Fixtures

A single massive fixture containing the entire application state should not become the default for every test.

Large fixtures:

* hide dependencies;
* increase execution time;
* create coupling;
* make failures difficult to diagnose;
* encourage accidental shared state.

Tests should provision only what they need.

---

# 7. Synthetic Data

Synthetic data is the preferred source for automated testing.

Synthetic data should:

* resemble realistic production patterns;
* contain no real personal information;
* contain no real credentials;
* contain no production secrets;
* support edge cases;
* support realistic volume;
* remain reproducible where required.

Synthetic customer examples should use clearly artificial values.

---

# 8. Anonymization and Pseudonymization

## 8.1 General Rule

If data originating from a real environment is ever used for testing, sensitive information must be minimized and appropriately protected before entering the test environment.

---

## 8.2 Fields Requiring Special Protection

Examples include:

* customer phone numbers;
* delivery addresses;
* employee personal information;
* payroll information;
* authentication credentials;
* API tokens;
* device identifiers;
* financial information;
* private documents.

---

## 8.3 Anonymization

Anonymization should remove the ability to reasonably associate the data with a real person.

Examples:

```text
Real name → Synthetic name
Real phone → Synthetic phone
Real address → Synthetic address
Real identifier → Synthetic identifier
```

The transformed dataset must not preserve unnecessary identifying information.

---

## 8.4 Pseudonymization

Pseudonymization may be used when stable relationships are required for testing.

For example:

```text
Employee A → TEST_EMPLOYEE_001
Employee B → TEST_EMPLOYEE_002
```

Stable pseudonyms may preserve relationships while removing direct identity.

Pseudonymized data must still be treated as potentially sensitive if re-identification remains possible.

---

## 8.5 No Production Credentials

Production credentials must never be anonymized and reused.

They must not enter test environments at all.

---

# 9. Tenant and Branch Test Data Isolation

Test data must respect the same business boundaries as production.

A representative dataset may contain:

```text
Business A
 ├── Branch A1
 └── Branch A2

Business B
 └── Branch B1
```

Tests must verify that:

* Business A cannot access Business B;
* Branch A1 cannot access Branch A2 when the user is not authorized;
* Branch B1 cannot access Business A;
* reports remain correctly scoped;
* imports remain scoped;
* exports remain scoped;
* search remains scoped;
* background jobs preserve scope;
* offline synchronization preserves scope.

Cross-tenant and cross-branch datasets are mandatory for security testing.

---

# 10. POS Test Data

POS datasets should cover:

* cashier identities;
* branch assignment;
* cash sessions;
* customer-facing session numbers;
* persistent session identifiers;
* dine-in orders;
* takeaway orders;
* phone delivery orders;
* products;
* recipes;
* discounts;
* payments;
* refunds;
* kitchen statuses;
* printer routing;
* completed orders;
* cancelled or failed operations.

Critical POS tests must begin from a known state.

---

# 11. Financial Test Data

Financial datasets must support:

* successful payments;
* failed payments;
* duplicate payment attempts;
* refunds;
* refund approvals;
* large refunds;
* cash shortages;
* cash overages;
* cash handovers;
* recounts;
* correction limits;
* privileged reopen;
* historical financial records.

Financial test data must never rely on uncontrolled shared state.

The authoritative financial state must be independently verifiable.

---

# 12. Inventory and Recipe Test Data

Inventory datasets should include:

* raw ingredients;
* semi-finished products;
* ready products;
* recipe versions;
* recipe approval states;
* stock batches;
* FIFO ordering;
* yield loss;
* stock adjustments;
* inventory discrepancies;
* low-stock thresholds;
* shopping lists;
* prepared-in-branch products;
* bought-ready products;
* multiple warehouses;
* branch-specific stock.

Example dependency:

```text
Raw Ingredients
      ↓
Semi-Finished Product
      ↓
Recipe
      ↓
Menu Product
      ↓
Order
      ↓
Inventory Deduction
```

Tests should be able to verify the entire dependency chain.

---

# 13. Offline and Synchronization Test Data

Offline testing requires data representing both local and server state.

Datasets may include:

```text
Server State
      +
Device State
      +
Pending Operations
      +
Synchronization History
```

Test scenarios should include:

* no pending operations;
* one pending operation;
* multiple ordered operations;
* duplicate operations;
* failed operations;
* rejected operations;
* quarantined operations;
* conflicting changes;
* long offline periods;
* subscription changes while offline;
* revoked devices while offline;
* server-side changes while the device is offline.

The dataset must make operation ordering and expected final state explicit.

---

# 14. Security Test Data

Security testing requires intentionally constructed identities and relationships.

Examples:

```text
Owner
Manager
Cashier
Cook
Waiter
Restricted Employee
Revoked Employee
Untrusted Device
Trusted Device
Wrong Branch User
Wrong Tenant User
```

Datasets should support:

* horizontal privilege escalation;
* vertical privilege escalation;
* branch boundary testing;
* tenant boundary testing;
* resource ownership testing;
* revoked access;
* permission changes;
* device trust changes;
* offline authorization testing.

Security datasets must not contain real credentials.

---

# 15. File and Document Test Data

File testing should include:

* valid files;
* empty files;
* oversized files;
* malformed files;
* unsupported file types;
* duplicate files;
* corrupted files;
* malicious-content test samples where safely controlled;
* valid imports;
* invalid imports;
* large imports;
* export datasets.

Test files must be synthetic or otherwise approved for testing.

They must not contain real confidential business data unless explicitly authorized.

---

# 16. AI and Model Test Data

Where AI functionality exists, datasets should distinguish between:

* training data;
* validation data;
* evaluation data;
* regression datasets;
* production-like synthetic data.

Test datasets should have stable versions.

Model regression tests must be reproducible against a known dataset version.

Sensitive real-world data must not be introduced into AI testing without appropriate authorization and protection.

---

# 17. Database Test Environment

Database test environments should provide:

* isolated database instances or schemas where appropriate;
* controlled schema versions;
* reproducible migrations;
* test-only credentials;
* controlled seed data;
* transaction isolation;
* reset capability;
* deterministic baseline data.

Tests must verify both:

```text
Fresh Database
```

and:

```text
Existing Database
        ↓
Migration
        ↓
Expected New State
```

This is especially important for release and migration testing.

---

# 18. Local Development Environment

The local environment should allow developers to execute relevant tests without requiring production infrastructure.

It should provide:

* local application runtime;
* test database;
* test cache where required;
* test queue where required;
* synthetic test data;
* test configuration;
* safe external-service substitutes.

Local configuration must never default to production services.

---

# 19. CI Test Environment

CI environments must be isolated between independent executions where necessary.

CI should support:

* clean test databases;
* controlled fixtures;
* deterministic configuration;
* test-only credentials;
* isolated temporary files;
* isolated queues;
* isolated caches;
* predictable environment variables;
* test result collection.

Parallel jobs must not accidentally modify each other's state.

---

# 20. Integration Test Environment

Integration environments should use enough real infrastructure to validate subsystem boundaries.

Examples include:

* PostgreSQL;
* Redis;
* queue infrastructure;
* background workers;
* scheduler;
* API services;
* file storage;
* controlled external-service substitutes.

Integration environments should remain isolated from production.

---

# 21. E2E Environment

E2E environments must represent a realistic business environment while remaining deterministic.

They should include:

* business;
* branches;
* employees;
* permissions;
* menu;
* products;
* recipes;
* inventory;
* cash sessions;
* orders;
* payment test behavior;
* notification behavior;
* required printers or printer substitutes;
* offline-capable devices where applicable.

The environment should start from a known baseline.

---

# 22. Staging and Release-Test Environment

The release-test environment should resemble production architecture sufficiently to validate:

* deployment behavior;
* configuration;
* migrations;
* API compatibility;
* authentication;
* authorization;
* background processing;
* queues;
* cache;
* reports;
* performance;
* resilience;
* critical business workflows.

Production data should not be required to achieve production-like testing.

---

# 23. Performance and Load Environments

Performance testing requires controlled large datasets.

Datasets should represent realistic distributions such as:

* multiple businesses;
* multiple branches;
* many employees;
* many products;
* large inventories;
* many orders;
* long order histories;
* large reports;
* synchronization queues;
* file imports.

The dataset size must be recorded with the test results.

Example:

```text
Businesses: 100
Branches: 500
Products: 50,000
Orders: 5,000,000
Inventory Movements: 20,000,000
```

The exact values depend on the performance test objective.

---

# 24. Resilience Test Environment

Resilience and chaos testing require an environment where failures can be safely injected.

The environment must allow controlled failure of:

* application processes;
* PostgreSQL;
* Redis;
* queues;
* workers;
* scheduler;
* network connectivity;
* external dependencies;
* file storage;
* printers or peripheral devices.

Failure testing must never target production unless a separately authorized production resilience program explicitly exists.

---

# 25. Environment Configuration

Environment configuration should be separated from application logic.

Configuration should identify:

* environment type;
* database location;
* cache location;
* queue location;
* external dependency endpoints;
* feature flags;
* test-mode settings;
* logging behavior;
* data retention policy;
* resource limits.

Secrets must be provided through the approved secret-management mechanism rather than committed into test configuration.

---

# 26. Environment Drift

Test environments can become unreliable when their configuration diverges from the intended architecture.

Environment drift may include:

* outdated dependencies;
* incorrect database schema;
* stale configuration;
* missing services;
* incorrect permissions;
* incorrect environment variables;
* incompatible API versions;
* stale test data;
* outdated worker versions.

Environment health checks should detect important drift.

---

# 27. Environment Versioning

A test result should be traceable to:

* application version;
* database schema version;
* migration version;
* configuration version;
* test dataset version;
* test suite version;
* relevant model version;
* infrastructure/environment version where material.

This allows failures to be reproduced.

---

# 28. Test Environment Health Checks

Before executing critical suites, the environment should verify:

* database availability;
* schema compatibility;
* required tables;
* required reference data;
* queue availability;
* worker availability;
* cache availability;
* file storage;
* required test services;
* authentication configuration;
* test account availability;
* clock/time configuration.

An unhealthy environment should not produce a misleading successful test result.

---

# 29. Data Reset Strategies

Different test types may use different reset strategies.

## 29.1 Transaction Rollback

Useful for isolated database tests where all changes occur within one controlled transaction.

## 29.2 Dataset Cleanup

Useful where tests create resources that can be explicitly removed.

## 29.3 Database Recreation

Useful for strong isolation and reproducibility.

## 29.4 Environment Recreation

Useful for CI, release testing, resilience testing, and environments where state drift is unacceptable.

The reset strategy must be chosen according to the test's isolation requirements.

---

# 30. Test Data Retention

Test data should not remain indefinitely without purpose.

Retention should consider:

* reproducibility;
* debugging;
* audit evidence;
* security;
* storage cost;
* privacy;
* environment capacity.

Temporary data should be removed after its useful lifetime.

Important test evidence may be retained for the period required by the testing and release process.

---

# 31. Test Data Access Control

Access to test environments should follow least privilege.

Developers and automated processes should receive only the permissions necessary for their testing responsibilities.

Production access must remain separate.

Test credentials must not provide production privileges.

---

# 32. Test Data and Secrets Separation

Test data and secrets are different categories.

Test data may be version-controlled when safe.

Secrets must not be embedded in:

* fixtures;
* factories;
* seed files;
* test source code;
* committed configuration;
* test reports;
* screenshots;
* logs.

A test fixture containing a real credential is invalid even if the credential is intended only for testing.

---

# 33. Test Data and Auditability

Important test operations should be traceable to:

* test case;
* dataset;
* environment;
* application version;
* test execution;
* expected result;
* actual result.

For financial, security, migration, resilience, and release tests, evidence should be sufficient to reconstruct the test conditions.

---

# 34. Reproducibility

A failed test should be reproducible whenever practical.

Reproduction information should include:

```text
Test
+
Application Version
+
Environment Version
+
Dataset Version
+
Configuration
+
Input
+
Expected Result
+
Actual Result
```

Randomized tests should record their seed when reproducibility depends on randomness.

---

# 35. Invalid and Corrupted Data

Testing must intentionally include invalid states where the system is expected to reject them.

Examples:

* malformed database values where technically possible;
* invalid API payloads;
* invalid import rows;
* inconsistent synchronization operations;
* duplicate identifiers;
* invalid recipe references;
* invalid stock quantities;
* invalid financial amounts.

Such data must be introduced through controlled tests.

The production database must never be deliberately corrupted as part of ordinary testing.

---

# 36. Time and Date Test Data

Tests must control time where business behavior depends on it.

Important scenarios include:

* subscription expiration;
* two-month post-expiration deletion policy;
* salary due dates;
* attendance;
* cash session dates;
* order dates;
* inventory movement dates;
* FIFO ordering;
* report selected-day behavior;
* offline validity periods.

Tests should not depend on the actual machine clock unless testing real-time behavior intentionally.

---

# 37. Subscription Test Data

Subscription datasets should cover:

* active subscription;
* near-expiration subscription;
* expired subscription;
* blocked functionality;
* view-only data state;
* reactivation;
* prolonged expiration;
* scheduled deletion eligibility;
* branch/function limitations.

The test dataset must allow validation that blocked functionality does not accidentally become accessible through another interface.

---

# 38. Test Data for Archive and Deletion

Datasets should include:

* active records;
* archived records;
* records referenced by historical transactions;
* deletion-eligible records;
* records that must remain preserved.

Tests must verify that archival and deletion rules do not destroy required historical integrity.

---

# 39. Test Data for Imports and Exports

Import datasets should include:

* valid complete files;
* valid partial files;
* duplicate rows;
* invalid rows;
* missing fields;
* incorrect types;
* invalid branch references;
* unauthorized records;
* oversized datasets;
* mixed valid and invalid rows.

Export tests should verify:

* authorization;
* tenant scope;
* branch scope;
* field visibility;
* correct formatting;
* complete data;
* historical correctness.

---

# 40. Test Data for Reports

Report datasets should contain enough variation to verify:

* daily reports;
* branch reports;
* staff reports;
* menu reports;
* financial reports;
* inventory reports;
* selected-day reports;
* filtered reports;
* archived historical data.

A report test should not rely on a dataset containing only one record.

---

# 41. Parallel Test Execution

Parallel tests must not introduce data races through shared mutable state.

Acceptable strategies include:

* isolated databases;
* isolated schemas;
* unique test tenants;
* unique test branches;
* unique identifiers;
* isolated queues;
* isolated temporary storage.

A test that passes only when executed alone is considered unreliable until the shared-state dependency is understood and controlled.

---

# 42. Test Environment Naming

Environment names should clearly indicate their purpose.

Examples:

```text
local
ci
integration
e2e
staging
performance
resilience
```

Temporary environments should also have an identifiable owner or lifecycle marker.

---

# 43. Environment Ownership

Each persistent test environment should have a defined owner responsible for:

* configuration;
* availability;
* data lifecycle;
* access control;
* drift detection;
* reset procedures;
* incident handling.

Temporary environments should have an expiration or cleanup policy.

---

# 44. Test Data Ownership

Each reusable dataset should have a clear purpose and owner.

Ownership includes responsibility for:

* correctness;
* compatibility;
* updates;
* deprecation;
* documentation;
* security;
* cleanup.

Unused datasets should be removed rather than accumulating indefinitely.

---

# 45. CI Data Lifecycle

A typical CI execution should follow:

```text
Create Environment
      ↓
Apply Schema
      ↓
Load Reference Data
      ↓
Create Test Data
      ↓
Run Tests
      ↓
Collect Evidence
      ↓
Clean / Destroy Environment
```

CI should not depend on the state left by a previous pipeline execution.

---

# 46. Test Environment Failure Handling

If environment provisioning fails, tests must not be reported as successful.

Environment failures should be classified separately from application test failures.

Examples:

```text
Application Failure
Database Failure
Infrastructure Failure
Test Data Failure
Environment Configuration Failure
Test Runner Failure
```

This distinction improves diagnosis and prevents false conclusions.

---

# 47. Test Data and Security Testing Relationship

Security tests require carefully controlled identities and resource relationships.

Therefore, security test data must preserve:

```text
Identity
   ↓
Business
   ↓
Branch Scope
   ↓
Role
   ↓
Permission
   ↓
Resource Ownership
```

Changing test data can unintentionally change the security boundary.

Security datasets must therefore be treated as controlled test assets.

---

# 48. Test Data and Financial Integrity

Financial datasets must preserve the relationships required to calculate authoritative outcomes.

For example:

```text
Order Total
   ↓
Payment
   ↓
Cash Session
   ↓
Refund
   ↓
Financial Report
```

Changing one component without updating the intended dependent state can make a financial test invalid.

---

# 49. Test Data and Inventory Integrity

Inventory datasets must preserve:

```text
Product
   ↓
Recipe
   ↓
Ingredient
   ↓
Stock Batch
   ↓
FIFO
   ↓
Consumption
   ↓
Remaining Stock
```

The dataset must allow the expected inventory movement to be independently calculated.

---

# 50. Test Data and Offline Integrity

Offline datasets must represent both:

* local state;
* authoritative server state.

They must include enough information to determine:

* which operations were created offline;
* their order;
* their identity;
* their authorization;
* their synchronization status;
* their final server outcome.

---

# 51. Test Data and Concurrency

Concurrency tests should use datasets that expose contention.

Examples:

* two cashiers attempting conflicting operations;
* two payments for one order;
* two inventory deductions;
* simultaneous recipe modification;
* simultaneous permission changes;
* concurrent synchronization.

Data should be prepared so that the expected invariant is known before execution.

---

# 52. Test Data and Migration Testing

Migration tests require datasets representing:

* old schema state;
* realistic historical records;
* archived records;
* incomplete or legacy states where applicable;
* records near important constraints.

Migration testing should verify:

```text
Old Schema
   ↓
Migration
   ↓
New Schema
   ↓
Business Meaning Preserved
```

Historical financial, inventory, order, audit, and subscription data must remain semantically correct after migration.

---

# 53. Test Artifacts

Test execution may produce:

* logs;
* screenshots;
* API traces;
* database snapshots;
* reports;
* coverage data;
* performance measurements;
* failure dumps;
* synchronization traces;
* audit records.

Artifacts must not accidentally expose sensitive information.

Before retention or sharing, artifacts should be reviewed for:

* secrets;
* tokens;
* personal data;
* production identifiers;
* confidential business information.

---

# 54. Anti-Patterns

The following practices are prohibited or strongly discouraged:

### 54.1 Using Production Database Directly

Tests must never write ordinary test data into production.

### 54.2 Copying Production Data Without Protection

Raw production exports must not become default test fixtures.

### 54.3 Shared Mutable Global Fixtures

Unrelated tests must not depend on shared mutable state.

### 54.4 Hard-Coded Credentials

Credentials must not be stored in fixtures or test source.

### 54.5 Manual Permanent Test Data

Important automated tests should not depend on manually created records.

### 54.6 Stale Fixtures

Fixtures that no longer represent the current business model must be removed or updated.

### 54.7 Environment-Specific Hidden Assumptions

Tests must not silently depend on a developer's machine configuration.

### 54.8 Ignoring Environment Failures

Infrastructure failure must not be interpreted as application success.

### 54.9 Unrealistic Performance Data

Testing millions of identical records does not necessarily represent realistic production behavior.

### 54.10 Tests That Require Previous Tests

A test should not require another test to execute successfully first unless the dependency is explicitly part of the workflow being tested.

---

# 55. Test Data Review

Test data should be reviewed when:

* business rules change;
* database schema changes;
* new permissions are introduced;
* new branch-scoped resources are added;
* financial workflows change;
* inventory/recipe behavior changes;
* subscription rules change;
* offline synchronization changes;
* new external integrations are introduced;
* security boundaries change.

---

# 56. Change Impact

A change to test data architecture should trigger review of affected tests.

Examples:

| Change                   | Potential Impact                     |
| ------------------------ | ------------------------------------ |
| New required field       | Fixtures, factories, API tests       |
| New branch rule          | Security, E2E, integration data      |
| New recipe behavior      | Inventory and POS datasets           |
| New payment state        | Financial and E2E datasets           |
| New subscription state   | Subscription and authorization tests |
| New synchronization rule | Offline datasets                     |
| New permission           | Security datasets                    |
| Database migration       | Repository, migration, E2E datasets  |
| New report               | Report and fixture data              |
| New AI model             | Evaluation and regression datasets   |

---

# 57. Minimum Test Dataset

The project should maintain a small stable baseline dataset containing at least:

```text
1 Business
2 Branches
Multiple Employees
Multiple Roles
Multiple Permissions
Multiple Products
Raw Ingredients
Semi-Finished Product
Recipe
Multiple Stock Batches
Warehouse
Cash Session
Dine-In Order
Takeaway Order
Delivery Order
Payment
Refund Scenario
Discount
Archived Record
Offline Device
Pending Sync Operation
Multiple Tenant/Branch Boundaries
Subscription States
```

This baseline should remain intentionally small enough for fast tests while covering important relationships.

---

# 58. Extended Test Dataset

Specialized testing may use larger datasets containing:

* many businesses;
* many branches;
* large employee populations;
* large menus;
* large inventory histories;
* large order histories;
* extensive audit records;
* large synchronization queues;
* large import/export files.

Extended datasets should not replace the minimal baseline dataset.

---

# 59. Test Data Versioning

Important reusable datasets should have identifiable versions.

A test result should be able to state:

```text
Dataset: POS_BASELINE
Version: 1.x
Environment: E2E
Application: <release>
Schema: <migration version>
```

When a dataset changes in a behaviorally important way, its version should change.

---

# 60. Test Environment Reproducibility

A test environment should be reconstructable from controlled inputs.

At minimum, this should include:

```text
Application Artifact
+
Database Schema
+
Configuration
+
Test Dataset
+
Test Dependencies
```

Manual undocumented changes should not be required.

---

# 61. Mandatory Test Data Invariants

The following rules are mandatory:

1. Production data is not the default test data source.
2. Production credentials never enter test data.
3. Test data is isolated from production.
4. Test data must respect tenant boundaries.
5. Test data must respect branch boundaries.
6. Mutable state must not be shared unintentionally.
7. Critical datasets must be reproducible.
8. Financial datasets must support independent reconciliation.
9. Inventory datasets must support independent stock verification.
10. Recipe datasets must preserve dependency relationships.
11. POS datasets must support complete critical workflows.
12. Offline datasets must represent local and server state.
13. Security datasets must represent authorized and unauthorized identities.
14. Invalid data must be introduced deliberately.
15. Sensitive data must be minimized.
16. Real personal data must not be used without appropriate authorization and protection.
17. Test secrets must remain separate from test fixtures.
18. CI executions must not depend on previous CI state.
19. Test environments must be isolated according to their risk.
20. Environment configuration must be controlled.
21. Environment drift must be detectable.
22. Schema version must be known.
23. Dataset version must be traceable.
24. Environment health must be verified before critical testing.
25. Environment failures must not be reported as application successes.
26. Test data must have an explicit lifecycle.
27. Temporary test data must be cleaned or destroyed according to policy.
28. Important test evidence must remain traceable.
29. Performance datasets must represent realistic volume and distribution.
30. Migration datasets must preserve historical business meaning.
31. Parallel tests must not corrupt one another's data.
32. Test artifacts must not expose secrets or unnecessary sensitive information.
33. Test data changes must be reviewed when business behavior changes.
34. Test environments must not silently connect to production services.
35. Test environment recreation must be possible without undocumented manual steps.

---

# 62. Acceptance Criteria

This document is considered implemented when:

* test data has a defined lifecycle;
* reusable fixtures/factories/builders are available where appropriate;
* synthetic data is the default;
* sensitive data handling rules are established;
* tenant and branch isolation can be tested;
* POS test datasets exist;
* financial test datasets exist;
* inventory and recipe datasets exist;
* offline synchronization datasets exist;
* security test identities and relationships exist;
* invalid and boundary datasets exist;
* CI environments can create isolated test state;
* test environments have controlled configuration;
* environment health can be verified;
* database schema versions are traceable;
* dataset versions are traceable;
* test environments can be reset or recreated;
* production services are protected from test execution;
* test artifacts are handled safely;
* performance and resilience environments can use appropriate datasets;
* migration testing has representative data;
* test failures can be reproduced from recorded conditions.

---

# 63. Relationship to Other Testing Documents

This document supports the entire testing architecture.

### TEST-01 — Testing Architecture Overview

Defines the overall testing architecture that this document provides data and environments for.

### TEST-02 — Testing Strategy and Test Pyramid

Defines where tests execute; this document defines how their required data and environments are prepared.

### TEST-03 — Unit Testing Architecture

Uses small deterministic fixtures, builders, and generated values.

### TEST-04 — Domain Testing Architecture

Requires controlled business states for domain invariants.

### TEST-05 — Application and Use Case Testing

Requires realistic application-level entities and relationships.

### TEST-06 — Repository and Database Integration Testing

Requires isolated databases and controlled persistence data.

### TEST-07 — API Contract and Schema Testing

Requires valid, invalid, boundary, and authorization-aware API data.

### TEST-08 — Integration Testing Architecture

Requires integrated infrastructure and controlled test environments.

### TEST-09 — End-to-End and POS Testing

Requires realistic branch, employee, menu, inventory, cash, order, and payment data.

### TEST-10 — Offline and Synchronization Testing

Requires controlled local/server datasets and synchronization histories.

### TEST-11 — Concurrency and Consistency Testing

Requires datasets that expose conflicting simultaneous operations.

### TEST-12 — Financial and Cash Testing

Requires authoritative financial and cash-session test states.

### TEST-13 — Inventory and Recipe Testing

Requires product, recipe, batch, FIFO, production, and stock datasets.

### TEST-14 — Authentication, Authorization and Security Testing

Requires controlled identities, permissions, tenants, branches, devices, and resource ownership.

### TEST-15 — Frontend Testing Architecture

Requires predictable API responses, UI fixtures, and representative business state.

### TEST-16 — AI Model and Inference Testing

Requires versioned evaluation and regression datasets.

### TEST-17 — Performance, Load and SLO Testing

Requires large, realistic, controlled datasets and production-like test environments.

### TEST-18 — Resilience and Chaos Testing

Requires isolated environments where controlled failures can be introduced safely.

### TEST-19 — CI Quality Gates and Release Testing

Requires reproducible environments and datasets so that release evidence is trustworthy.

---

# 64. Final Test Data and Environment Rule

A test is trustworthy only when its data and execution environment are trustworthy.

Therefore:

> **No test result should be treated as reliable unless the test data, environment, configuration, schema, dependencies, and execution conditions are sufficiently controlled, isolated, reproducible, and traceable for the risk being tested.**

For FastFood ERP, this means test data and environments must preserve the same fundamental boundaries as the system itself:

```text
Business
   ↓
Branch
   ↓
Identity / Role / Permission
   ↓
Resource Ownership
   ↓
Business State
   ↓
Financial / Inventory / Order Effects
   ↓
Audit / History
```

The testing environment may differ from production in infrastructure scale and external integrations, but it must not silently change the business rules, security boundaries, data ownership model, or correctness expectations being tested.

