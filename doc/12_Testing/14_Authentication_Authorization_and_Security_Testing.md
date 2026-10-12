# 14. Authentication, Authorization and Security Testing

**Document ID:** TEST-14
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`

---

## 1. Purpose

This document defines the testing architecture and mandatory testing requirements for authentication, authorization, permission enforcement, tenant isolation, branch isolation, trusted devices, privilege escalation prevention, and security-sensitive access control.

The purpose is to prove that:

* only valid identities can authenticate;
* authenticated identities receive only the access they are entitled to receive;
* tenant and business boundaries cannot be crossed;
* branch scope is correctly enforced;
* role permissions are correctly enforced;
* resource ownership is validated;
* privileged operations require appropriate authorization;
* permission changes take effect correctly;
* revoked access is actually revoked;
* offline authorization does not create unauthorized access;
* service and background identities cannot bypass security boundaries;
* direct API manipulation cannot bypass frontend restrictions;
* privilege escalation attempts fail safely;
* security failures do not expose protected information.

The central principle is:

> **Authentication proves who is acting; authorization determines what that identity may do; isolation determines which resources that identity may access.**

---

# 2. Scope

This document covers testing for:

* authentication;
* login;
* logout;
* failed authentication;
* account states;
* password and credential handling;
* session and token behavior;
* trusted devices;
* unfamiliar devices;
* privileged authentication;
* role-based authorization;
* functional permissions;
* branch permissions;
* tenant/business isolation;
* resource ownership;
* Owner permissions;
* Manager permissions;
* employee permissions;
* Super Admin boundaries;
* permission templates;
* permission changes;
* permission revocation;
* temporary access;
* emergency access;
* API authorization;
* direct request manipulation;
* object-level authorization;
* privilege escalation;
* horizontal privilege escalation;
* vertical privilege escalation;
* cross-tenant access;
* cross-branch access;
* offline authorization;
* synchronization authorization;
* background jobs;
* service identities;
* integrations;
* auditability of security-sensitive operations;
* security regression testing.

This document does not redefine the security policy itself. Security requirements are defined in:

* `03_Identity_and_Access_Security.md`
* `04_Business_and_Tenant_Isolation_Security.md`
* `05_Branch_and_Scope_Isolation_Security.md`
* `06_Authentication_Security_Standards.md`
* `07_Authorization_and_Permission_Security.md`
* `08_Trusted_Device_and_Device_Security.md`
* `09_Offline_Authorization_and_Synchronization_Security.md`
* `10_API_Security_Controls.md`

This document defines how those requirements must be tested.

---

# 3. Security Testing Principles

Authentication and authorization testing MUST follow these principles:

1. Security controls must be tested at the actual enforcement boundary.
2. Frontend restrictions alone are never sufficient evidence of authorization.
3. Every protected operation must be tested with both allowed and denied identities.
4. Tenant isolation must be tested independently from role permissions.
5. Branch isolation must be tested independently from tenant isolation.
6. Resource ownership must be tested independently from functional permission.
7. Privileged operations require explicit authorization tests.
8. Permission denial must fail safely.
9. Security errors must not reveal protected information.
10. Revoked access must stop working.
11. Permission changes must take effect according to the defined consistency model.
12. Offline authorization must not create a wider privilege scope than online authorization.
13. Background jobs and service identities must be tested as security principals.
14. Direct API requests must receive the same authorization decisions as normal application requests.
15. Identifier manipulation must not allow unauthorized resource access.
16. Security tests must include horizontal and vertical privilege escalation.
17. Security tests must include negative and adversarial scenarios.
18. Critical authorization behavior must be covered by regression tests.
19. Security tests must not depend only on HTTP status codes; the resulting data and side effects must also be verified.
20. Security correctness takes priority over convenience or performance.

---

# 4. Authentication and Authorization Boundary

The testing model must distinguish:

```text
Identity
   ↓
Authentication
   ↓
Business / Tenant Context
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

A successful authentication does not automatically grant access to a resource.

For example:

```text
Authenticated Employee
        ↓
Assigned to Branch 1
        ↓
Has Inventory View Permission
        ↓
Can view Branch 1 inventory
```

It does not imply:

```text
Can view Branch 2 inventory
```

unless the identity explicitly has the required scope.

---

# 5. Authentication Testing

Authentication tests verify that only valid identities can establish an authenticated state.

Tests must cover:

* valid credentials;
* invalid credentials;
* missing credentials;
* malformed credentials;
* disabled account;
* expired account;
* revoked access;
* incorrect verification code;
* expired verification code;
* repeated failed attempts;
* session establishment;
* logout;
* session invalidation;
* credential recovery;
* device verification where required.

## 5.1 Successful Authentication

A successful authentication test must verify:

* correct identity;
* correct business context;
* correct permitted branch context;
* correct session/authentication state;
* correct audit event where required.

## 5.2 Failed Authentication

Failed authentication must verify:

* no authenticated session is created;
* no protected resource is returned;
* no protected operation is executed;
* security-sensitive information is not disclosed.

---

# 6. Account State Testing

Each security-relevant account state must be tested.

Examples:

```text
Active
Disabled
Suspended
Revoked
Expired
Pending Verification
```

Tests must verify that prohibited states cannot authenticate or perform protected operations.

A previously valid session must also be tested against account revocation according to the session invalidation policy.

---

# 7. Session and Token Testing

Tests must verify:

* valid session access;
* expired session rejection;
* revoked session rejection;
* logout behavior;
* token/session misuse;
* access after credential or account revocation;
* access from an invalid device context where applicable.

A stale authentication artifact must not automatically grant continued authorization after access has been revoked.

---

# 8. Trusted Device Testing

Trusted device behavior must be tested separately from user identity.

The test model is:

```text
Human Identity
      +
Device Identity
      +
Business Context
      +
Branch Context
      +
Authentication State
      +
Authorization
```

Tests must cover:

* new device;
* verification of unfamiliar device;
* trusted device;
* revoked device;
* replaced device;
* expired trust;
* copied/cloned device identity;
* device belonging to another business;
* device belonging to another branch;
* offline device behavior.

A trusted device must not automatically receive unlimited business permissions.

---

# 9. Role Authorization Testing

The system must verify permissions according to the configured role and employee scope.

Relevant roles include:

* Super Admin;
* Owner;
* Manager;
* cook;
* waiter;
* other configured roles.

Tests must not assume that a role name alone determines all access.

Authorization must be evaluated according to the effective permission model.

---

# 10. Functional Permission Testing

Each protected function must have explicit positive and negative tests.

Example:

```text
Employee A:
Inventory View = Allowed
Inventory Adjustment = Denied
```

Tests:

```text
View inventory → Allowed
Adjust inventory → Denied
```

The test must verify both:

1. access decision;
2. absence of unauthorized side effects.

A denied adjustment must not modify stock.

---

# 11. Branch Permission Testing

Branch scope must be tested independently.

Example:

```text
Employee:
Branch 1 → Allowed
Branch 2 → Denied
```

Tests must verify:

* Branch 1 access succeeds;
* Branch 2 access fails;
* Branch 2 identifiers cannot be used to bypass authorization;
* Branch 2 data is not leaked through search;
* Branch 2 data is not leaked through reports;
* Branch 2 data is not leaked through exports;
* Branch 2 operations cannot be created indirectly.

Branch authorization must apply consistently across all relevant application boundaries.

---

# 12. Tenant and Business Isolation Testing

Tenant isolation is a mandatory security boundary.

Example:

```text
Business A
 └── Employee A

Business B
 └── Employee B
```

Employee A must never access Business B resources merely by knowing:

* an identifier;
* an order number;
* a product ID;
* an employee ID;
* a branch ID;
* a report ID;
* a file ID;
* an API endpoint;
* a URL;
* a database-generated identifier.

Tests must attempt direct identifier substitution.

Expected result:

```text
Access denied
+
No protected data
+
No unauthorized side effect
```

---

# 13. Resource Ownership Testing

Authorization must verify not only whether the user has a function permission, but also whether the requested resource belongs to the user's permitted scope.

Example:

```text
Permission:
View Orders = Allowed

Resource:
Order belongs to Branch 2

Employee:
Only Branch 1
```

Expected result:

```text
Denied
```

This prevents the following security error:

> "The employee has permission to view orders, therefore the employee may view every order."

Functional permission and resource scope are separate authorization dimensions.

---

# 14. Horizontal Privilege Escalation Testing

Horizontal escalation occurs when one identity accesses another identity's resources without obtaining a higher role.

Example:

```text
Employee A
        ↓
Attempts to access
Employee B's payroll information
```

Tests must cover:

* employee records;
* attendance;
* payroll;
* orders;
* inventory;
* reports;
* files;
* device records;
* notifications;
* audit information;
* branch resources.

The attacker remains at the same privilege level, but attempts to access another user's resources.

Expected result:

```text
Denied
```

---

# 15. Vertical Privilege Escalation Testing

Vertical escalation occurs when a lower-privileged identity attempts to perform a higher-privileged operation.

Examples:

```text
Employee
   ↓
Attempts to modify permissions
```

```text
Manager
   ↓
Attempts to perform Owner-only operation
```

```text
Owner
   ↓
Attempts to perform Super Admin-only platform operation
```

Tests must cover:

* role changes;
* permission changes;
* employee creation;
* privileged configuration;
* recipe approval;
* financial corrections;
* refund approval;
* subscription administration;
* tenant administration;
* platform configuration;
* security administration.

Every unauthorized escalation must be rejected.

---

# 16. Owner Authorization Testing

Owner access is broad but still bounded by the business model.

Tests must verify Owner access to authorized business operations such as:

* recipes;
* salaries;
* branch reports;
* role and permission management;
* page customization;
* business configuration.

Tests must also verify that Owner permissions do not unintentionally grant Super Admin platform authority.

An Owner must not automatically gain access to another business.

---

# 17. Manager Authorization Testing

Manager permissions must be tested according to explicitly assigned permissions.

A Manager may have permissions such as:

```text
Employee Management = Allowed
Inventory View = Allowed
Inventory Adjustment = Denied
```

Tests must verify each permission independently.

Manager access must not be inferred from the role name alone.

---

# 18. Permission Template Testing

The system supports role templates derived from employee permissions.

Tests must verify:

* creating a role template from valid permissions;
* applying the template;
* preserving intended permissions;
* preventing unauthorized permissions from being inherited;
* changing a template;
* effect on existing employees;
* effect on future employees;
* branch-specific scope.

A template must never silently expand an employee's authority beyond the intended scope.

---

# 19. Permission Change Testing

Permission changes are security-sensitive operations.

Tests must verify:

1. authorized administrator changes a permission;
2. new authorization state becomes effective;
3. revoked permission stops allowing the operation;
4. unauthorized administrator cannot modify permissions;
5. historical audit information is preserved.

Example:

```text
Before:
Inventory Adjustment = Allowed

Permission changed

After:
Inventory Adjustment = Denied
```

The test must verify actual behavior, not merely the stored permission record.

---

# 20. Permission Revocation Testing

Revocation must be tested as a first-class security event.

Cases include:

* employee removed from branch;
* employee disabled;
* role permission removed;
* device revoked;
* session revoked;
* Owner permission removed;
* Manager permission removed.

Tests must verify that access is no longer available according to the defined authorization propagation model.

Revocation tests must include both:

* new requests;
* already-established authentication/session states where applicable.

---

# 21. Latest-Command-Wins Permission Testing

The permission model allows updates to selected Managers or selected employees.

Where multiple permission changes affect the same identity, tests must verify the defined latest-command-wins behavior.

Example:

```text
Command 1:
Inventory = Allowed

Command 2:
Inventory = Denied
```

Expected final state:

```text
Inventory = Denied
```

The test must also verify that intermediate operations do not produce an unintended authorization window outside the defined consistency model.

---

# 22. API Authorization Testing

Authorization must be tested directly at the API boundary.

Tests must attempt:

* missing authentication;
* invalid authentication;
* valid authentication with insufficient permission;
* valid permission with wrong branch;
* valid branch with wrong resource;
* another tenant's resource;
* another employee's resource;
* manipulated identifiers;
* manipulated query parameters;
* manipulated path parameters;
* manipulated request body;
* unauthorized HTTP methods.

The frontend must not be treated as a security boundary.

---

# 23. Direct Request Manipulation

Security tests must assume that a malicious client can modify every client-controlled field.

Examples:

```text
branch_id
business_id
employee_id
order_id
product_id
role_id
permission_id
warehouse_id
report_id
```

Tests must verify that changing these values cannot bypass server-side authorization.

The system must derive or validate security context independently of untrusted client claims.

---

# 24. Object-Level Authorization Testing

Every resource endpoint must be tested for object-level authorization.

Example:

```text
GET /orders/{order_id}
```

Tests must verify:

```text
Own permitted order → Allowed
Same-tenant but unauthorized branch → Denied
Different tenant → Denied
Non-existent resource → Safe failure
```

Equivalent testing must be applied to:

* employees;
* orders;
* inventory;
* recipes;
* reports;
* files;
* devices;
* payroll;
* attendance;
* financial records.

---

# 25. Search and Enumeration Testing

Authorization must apply to search operations.

Tests must verify that a restricted identity cannot discover protected resources through:

* search;
* filtering;
* sorting;
* pagination;
* autocomplete;
* dropdowns;
* counts;
* reports;
* exports;
* identifiers.

For example, if an employee cannot view Branch 2 orders, searching for Branch 2 order numbers must not reveal them.

Enumeration must not become an alternative path around authorization.

---

# 26. Import and Export Authorization Testing

Import/export operations must receive the same authorization testing as normal CRUD operations.

Tests must verify:

* unauthorized export is denied;
* export scope is restricted correctly;
* Branch 1 employee cannot export Branch 2 data;
* one tenant cannot export another tenant's data;
* unauthorized import is denied;
* imported objects cannot bypass ownership rules;
* imported identifiers cannot create unauthorized relationships.

A valid file does not make an operation authorized.

---

# 27. Report Authorization Testing

Reports may contain aggregated or sensitive information and therefore require authorization testing.

Tests must verify:

* branch-scoped reports;
* employee reports;
* payroll reports;
* inventory reports;
* financial reports;
* audit reports;
* aggregated business reports.

A user who cannot access the underlying data must not obtain it indirectly through a report.

---

# 28. Financial Authorization Testing

Security tests must cover privileged financial operations such as:

* refunds;
* refund approval;
* cash correction;
* cash-session reopening;
* privileged reconciliation;
* financial exports.

Tests must verify:

```text
Unauthorized request
        ↓
Denied
        ↓
No financial side effect
```

Authorization must be verified independently from the financial business rules defined in `12_Financial_and_Cash_Testing.md`.

---

# 29. Inventory Authorization Testing

Inventory security tests must cover:

* stock viewing;
* stock adjustment;
* discrepancy correction;
* recipe modification;
* recipe approval;
* price modification;
* warehouse operations;
* inventory exports.

Tests must verify that a user with view permission cannot automatically perform modification operations.

---

# 30. Recipe Authorization Testing

Recipe access may be restricted by role.

Tests must verify:

* authorized recipe viewing;
* restricted recipe denial;
* recipe modification permission;
* recipe approval permission;
* branch/global menu permissions;
* archived recipe access;
* direct API attempts to modify restricted recipes.

A user who can use a product operationally must not automatically gain permission to inspect or modify restricted recipe details.

---

# 31. Device Authorization Testing

Device trust and user authorization must be tested separately.

Cases include:

```text
Trusted device + authorized user
Trusted device + unauthorized user
Untrusted device + authorized user
Revoked device + authorized user
Trusted device + wrong branch context
```

A trusted device must not override user authorization.

Likewise, a valid user must not automatically bypass required device verification.

---

# 32. Offline Authorization Testing

Offline authorization must follow the same security intent as online authorization.

Tests must verify:

* valid offline identity;
* valid trusted device;
* valid branch scope;
* valid cached permissions;
* permission expiration/revocation behavior;
* offline operation validity window;
* unauthorized offline operation;
* synchronization after authorization changes.

A device must not continue performing privileged offline operations beyond the permitted security window.

---

# 33. Synchronization Authorization Testing

Synchronization is a security boundary.

Tests must verify:

* operation identity;
* originating business;
* originating branch;
* originating device;
* originating user;
* authorization context;
* integrity;
* replay protection;
* rejected operations.

A synchronized operation from Branch 1 must not become a Branch 2 operation through client-side modification.

A rejected operation must not create a hidden business side effect.

---

# 34. Background Worker Authorization Testing

Background workers must be tested as independent security principals.

Tests must verify:

* worker identity;
* allowed operation;
* tenant context;
* branch context;
* resource scope;
* prohibited operations;
* failed authorization;
* retry behavior.

A background worker must not gain broader access merely because it operates internally.

---

# 35. Scheduler Authorization Testing

Scheduled jobs must be tested for correct scope.

Examples:

* subscription processing;
* notifications;
* inventory recommendations;
* report generation;
* cleanup;
* synchronization processing.

Tests must verify that a scheduled task processes only the intended business/branch/resource scope.

---

# 36. Service and Integration Authorization Testing

External integrations must be treated as limited identities.

Tests must verify:

* valid integration credential;
* invalid credential;
* revoked credential;
* allowed operation;
* prohibited operation;
* tenant scope;
* branch scope;
* resource scope;
* replay or repeated request;
* credential rotation.

An integration identity must not automatically receive human Owner permissions.

---

# 37. Privileged Operation Testing

The following operations require especially strong authorization tests:

* permission changes;
* role changes;
* Owner management;
* Super Admin operations;
* financial correction;
* cash-session reopening;
* refund approval;
* inventory correction;
* recipe approval;
* security configuration;
* device revocation;
* account recovery;
* subscription administration;
* data deletion or retention actions.

For each operation, tests must verify:

1. authorized identity succeeds;
2. unauthorized identity fails;
3. wrong branch fails;
4. wrong tenant fails;
5. manipulated identifiers fail;
6. no unauthorized side effect occurs;
7. audit information is produced where required.

---

# 38. Privilege Escalation Test Matrix

| Attack Type             | Example                                      | Expected Result             |
| ----------------------- | -------------------------------------------- | --------------------------- |
| Horizontal              | Employee A accesses Employee B data          | Denied                      |
| Horizontal              | Branch 1 employee accesses Branch 2 resource | Denied                      |
| Cross-tenant            | Business A accesses Business B resource      | Denied                      |
| Vertical                | Employee performs Manager operation          | Denied                      |
| Vertical                | Manager performs Owner-only operation        | Denied                      |
| Vertical                | Owner performs Super Admin operation         | Denied                      |
| Object-level            | Valid permission + foreign resource ID       | Denied                      |
| Parameter manipulation  | Replace branch ID                            | Denied                      |
| Role manipulation       | Change role in request body                  | Denied                      |
| Permission manipulation | Add permission in request                    | Denied                      |
| API bypass              | Direct protected endpoint call               | Same authorization decision |
| Offline bypass          | Expired/revoked offline privilege            | Denied                      |
| Device bypass           | Revoked device continues privileged action   | Denied                      |

---

# 39. Error and Information Disclosure Testing

Authorization failures must not reveal unnecessary protected information.

Tests must verify that denied requests do not expose:

* another tenant's data;
* another branch's data;
* existence of sensitive resources where policy prohibits disclosure;
* internal authorization rules;
* secrets;
* credentials;
* sensitive database information;
* privileged configuration.

Security errors must remain useful for legitimate clients while minimizing information leakage.

---

# 40. Audit Testing

Security-sensitive events must produce appropriate audit records.

Tests should cover:

* successful authentication;
* failed authentication;
* device verification;
* device revocation;
* permission change;
* role change;
* privileged action;
* authorization denial where required;
* refund approval;
* inventory correction;
* security configuration change;
* account deactivation;
* recovery action.

Audit tests must verify:

* correct actor;
* correct action;
* correct resource;
* correct business;
* correct branch where applicable;
* timestamp;
* outcome;
* sufficient context for investigation.

Audit records must not themselves expose unnecessary secrets.

---

# 41. Security Test Data

Security tests require controlled identities representing different authorization states.

A standard dataset should include:

```text
Business A
 ├── Branch 1
 │    ├── Owner A
 │    ├── Manager A1
 │    └── Employee A1
 │
 └── Branch 2
      └── Employee A2

Business B
 └── Branch 1
      └── Owner B
```

The dataset should also include:

* active identity;
* disabled identity;
* revoked identity;
* trusted device;
* untrusted device;
* revoked device;
* branch-specific permissions;
* all-branch permissions;
* restricted permissions;
* privileged permissions.

Tests must use deterministic identities and avoid sharing mutable security state between unrelated test cases.

---

# 42. Security Test Matrix

| Security Area         |    Unit |  Domain | Application | API/Integration |      E2E |
| --------------------- | ------: | ------: | ----------: | --------------: | -------: |
| Authentication rules  |     Yes |     Yes |         Yes |             Yes |      Yes |
| Role permissions      |     Yes |     Yes |         Yes |             Yes |      Yes |
| Branch isolation      | Limited |     Yes |         Yes |             Yes | Critical |
| Tenant isolation      | Limited |     Yes |         Yes |             Yes | Critical |
| Resource ownership    | Limited |     Yes |         Yes |             Yes | Critical |
| Privilege escalation  | Limited |     Yes |         Yes |        Critical | Critical |
| Device trust          |     Yes |     Yes |         Yes |             Yes |      Yes |
| Offline authorization | Limited |     Yes |         Yes |        Critical | Critical |
| API authorization     | Limited | Limited |         Yes |        Critical | Critical |
| Permission changes    |     Yes |     Yes |    Critical |        Critical |      Yes |
| Revocation            |     Yes |     Yes |    Critical |        Critical |      Yes |
| Audit behavior        | Limited |     Yes |         Yes |             Yes |      Yes |

The highest-risk authorization boundaries require multiple testing layers.

---

# 43. Critical Security Test Suite

The mandatory security regression suite should include at minimum:

1. Authenticate with valid credentials.
2. Reject invalid credentials.
3. Reject disabled/revoked identities.
4. Verify session expiration.
5. Verify logout/session invalidation.
6. Verify unfamiliar-device verification.
7. Verify revoked-device rejection.
8. Verify role permission enforcement.
9. Verify branch permission enforcement.
10. Verify tenant isolation.
11. Verify resource ownership.
12. Attempt horizontal privilege escalation.
13. Attempt vertical privilege escalation.
14. Manipulate branch identifiers.
15. Manipulate business identifiers.
16. Manipulate resource identifiers.
17. Manipulate role identifiers.
18. Manipulate permission identifiers.
19. Attempt direct API authorization bypass.
20. Attempt unauthorized report access.
21. Attempt unauthorized export.
22. Attempt unauthorized import.
23. Attempt unauthorized inventory adjustment.
24. Attempt unauthorized recipe modification.
25. Attempt unauthorized refund/financial correction.
26. Change a permission and verify the new state.
27. Revoke a permission and verify access stops.
28. Revoke a device and verify privileged access stops.
29. Test offline authorization boundaries.
30. Test synchronization authorization.
31. Test background-worker scope.
32. Test service/integration scope.
33. Verify privileged actions are auditable.
34. Verify denied operations create no unauthorized side effect.
35. Verify security failures do not expose protected information.

This suite should be part of the mandatory release security gate.

---

# 44. Negative Security Testing

Security testing must be predominantly negative in critical authorization areas.

For every important permission, tests should ask:

```text
What happens if the user does not have this permission?
```

For every important resource, tests should ask:

```text
What happens if the user has permission for the function
but not for this resource?
```

For every important branch, tests should ask:

```text
What happens if the user changes the branch identifier?
```

For every privileged operation, tests should ask:

```text
What happens if a lower-privileged identity calls it directly?
```

These tests are required even when the normal UI makes the operation inaccessible.

---

# 45. Frontend vs Server-Side Authorization Testing

Frontend visibility is not authorization evidence.

Example:

```text
Button hidden
```

does not prove:

```text
Operation protected
```

Tests must therefore call the underlying API/application boundary directly.

The following must be treated as untrusted:

* hidden buttons;
* disabled buttons;
* route restrictions;
* client-side role checks;
* client-side branch IDs;
* client-side permission state.

The authoritative authorization decision must be tested at the server-side enforcement boundary.

---

# 46. Security Regression Testing

Every confirmed authorization or isolation defect must result in a regression test where practical.

Examples:

```text
Bug:
Employee could access another branch through order ID.

Regression:
Use valid Employee A credentials and Branch 2 order ID.
Expected: denied.
```

```text
Bug:
Manager could modify permissions through direct API request.

Regression:
Call permission-management endpoint directly.
Expected: denied.
```

```text
Bug:
Revoked device continued offline privileged operations.

Regression:
Revoke device, perform offline privileged operation.
Expected: denied or quarantined according to offline policy.
```

Security regression tests must remain permanently protected from accidental removal.

---

# 47. Security Test Isolation

Security tests must not contaminate each other.

Each test should control:

* identity;
* roles;
* permissions;
* business;
* branches;
* devices;
* sessions;
* resources.

Tests must not rely on another test having previously:

* authenticated a user;
* created a permission;
* revoked a device;
* changed a role;
* created a session.

Security test isolation is especially important because shared authentication state can produce false positives.

---

# 48. Security Testing in CI

CI should execute security tests in multiple levels.

### Fast CI

Run:

* permission rule tests;
* role tests;
* authorization decision tests;
* isolation unit/domain tests.

### Integration CI

Run:

* API authorization;
* tenant isolation;
* branch isolation;
* object-level authorization;
* session/device behavior;
* permission changes.

### Release CI

Run:

* critical privilege escalation suite;
* critical tenant/branch isolation suite;
* offline authorization;
* synchronization authorization;
* privileged financial/inventory actions;
* security regression suite.

Critical security failures must block release.

---

# 49. Security Testing and Performance

Security tests must ensure that authorization checks remain correct under realistic load.

Performance testing should cover:

* many authenticated users;
* many branches;
* many permissions;
* large resource sets;
* large search results;
* concurrent authorization requests;
* high-frequency POS requests;
* synchronization requests;
* background jobs.

Performance optimization must not remove or weaken:

* tenant checks;
* branch checks;
* resource ownership checks;
* permission checks;
* device trust validation;
* audit requirements.

A faster unauthorized operation is still a security failure.

---

# 50. Security Failure Matrix

| Scenario                       | Expected Result                     |
| ------------------------------ | ----------------------------------- |
| Invalid credentials            | Authentication rejected             |
| Disabled identity              | Authentication rejected             |
| Revoked session                | Protected request rejected          |
| Revoked device                 | Device-protected operation rejected |
| Missing permission             | Operation denied                    |
| Wrong branch                   | Operation denied                    |
| Wrong tenant                   | Operation denied                    |
| Wrong resource owner           | Operation denied                    |
| Manipulated identifier         | Authorization still enforced        |
| Direct API call                | Same authorization rules apply      |
| Unauthorized import            | Rejected                            |
| Unauthorized export            | Rejected                            |
| Unauthorized privileged action | Rejected                            |
| Offline privilege expired      | Operation rejected/quarantined      |
| Unauthorized sync              | Rejected                            |
| Background task wrong scope    | Operation rejected                  |
| Service identity wrong scope   | Operation rejected                  |
| Denied operation               | No unauthorized side effect         |

---

# 51. Change Impact Testing

Changes to any of the following require authorization test review:

* authentication;
* session handling;
* roles;
* permissions;
* branch assignment;
* tenant context;
* device trust;
* API endpoints;
* resource identifiers;
* search;
* reports;
* imports;
* exports;
* offline operations;
* synchronization;
* background jobs;
* service identities;
* permission templates;
* employee management;
* financial permissions;
* inventory permissions;
* recipe permissions.

Security testing must be included in the change impact assessment even when the code change appears unrelated to authentication.

---

# 52. Relationship to Other Testing Documents

### `03_Unit_Testing_Architecture.md`

Defines isolated testing techniques used to test authorization rules.

### `04_Domain_Testing_Architecture.md`

Defines business-level security invariants that can be represented as domain rules.

### `05_Application_and_Use_Case_Testing.md`

Verifies authorization within real application workflows.

### `07_API_Contract_and_Schema_Testing.md`

Verifies the API contract, while this document verifies that API operations are correctly authorized.

### `08_Integration_Testing_Architecture.md`

Verifies authorization across subsystem boundaries.

### `09_End_to_End_and_POS_Testing.md`

Verifies security behavior in complete POS workflows.

### `10_Offline_and_Synchronization_Testing.md`

Defines the general offline/synchronization testing architecture.

### `11_Concurrency_and_Consistency_Testing.md`

Defines concurrency behavior that may affect permission changes and authorization state.

### `12_Financial_and_Cash_Testing.md`

Defines financial business correctness; this document verifies authorization around privileged financial operations.

### `13_Inventory_and_Recipe_Testing.md`

Defines inventory/recipe correctness; this document verifies access control around those operations.

### Security Section

The authoritative security policies are defined in `docs/11_Security/`.

Testing verifies those policies rather than redefining them.

---

# 53. Mandatory Security Invariants

The following are mandatory test invariants.

### Authentication

1. Invalid credentials cannot establish valid authentication.
2. Disabled or revoked identities cannot perform protected operations.
3. Expired authentication cannot be used indefinitely.
4. Logout/revocation behavior follows the defined security policy.
5. Device trust does not replace user authorization.

### Authorization

6. Authorization is deny-by-default.
7. Every protected operation requires appropriate authorization.
8. Functional permission alone does not bypass resource scope.
9. Client-provided authorization context cannot override server-side policy.
10. Unauthorized operations produce no unauthorized side effect.

### Tenant Isolation

11. A user cannot access another business's resources.
12. Resource identifiers cannot bypass tenant isolation.
13. Search cannot bypass tenant isolation.
14. Reports cannot bypass tenant isolation.
15. Imports and exports cannot bypass tenant isolation.

### Branch Isolation

16. Branch-scoped identities cannot access unauthorized branches.
17. Branch identifiers cannot override authorization.
18. Cross-branch operations require explicit authorization.
19. Branch isolation applies to reads and writes.

### Privilege Escalation

20. Lower-privileged identities cannot perform higher-privileged operations.
21. Same-level identities cannot access each other's protected resources.
22. Role identifiers cannot be manipulated to gain authority.
23. Permission identifiers cannot be manipulated to gain authority.
24. Direct API access cannot bypass role restrictions.

### Permission Lifecycle

25. Permission changes take effect according to the defined consistency model.
26. Revoked permissions cannot continue granting unauthorized access.
27. Role templates cannot silently grant excessive privileges.
28. Device revocation prevents prohibited device use.

### Offline and Services

29. Offline authorization does not exceed the user's permitted scope.
30. Synchronization cannot transform an unauthorized operation into an authorized one.
31. Background workers operate only within their assigned scope.
32. Service identities have only explicitly granted authority.

### Audit

33. Security-sensitive privileged operations are traceable.
34. Authorization failures do not expose unnecessary protected information.
35. Audit records cannot be used to bypass data-protection requirements.

### Release

36. Critical authorization and isolation tests are release-blocking.
37. Security regressions remain covered after fixes.
38. Security tests are not weakened to accommodate failing functionality.

---

# 54. Acceptance Criteria

This document is considered correctly implemented when:

* authentication behavior has positive and negative tests;
* account states are tested;
* sessions and revocation are tested;
* trusted-device behavior is tested;
* role permissions are tested;
* branch permissions are tested;
* tenant isolation is tested;
* resource ownership is tested;
* horizontal privilege escalation is tested;
* vertical privilege escalation is tested;
* direct API authorization bypass is tested;
* identifier manipulation is tested;
* search/report/import/export authorization is tested;
* privileged financial and inventory operations are tested;
* offline authorization is tested;
* synchronization authorization is tested;
* background and service identities are tested;
* permission changes and revocation are tested;
* security-sensitive actions are auditable;
* critical security tests run in CI/release validation;
* authorization failures produce no unauthorized side effects;
* security defects generate regression tests;
* critical security failures block release.

---

# 55. Final Security Testing Rule

Security testing is not complete merely because valid users can log in and normal roles appear to work.

The system must also prove that an identity cannot obtain authority through an unintended path.

The required security chain is:

```text
Who are you?
      ↓
Are you authenticated?
      ↓
Which business do you belong to?
      ↓
Which branches may you access?
      ↓
Which role do you have?
      ↓
Which function may you perform?
      ↓
Which resource may you access?
      ↓
Is this specific action allowed?
      ↓
Can the action create an unauthorized side effect?
```

The final acceptance condition is:

> **A security boundary is considered correctly tested only when authorized operations succeed, unauthorized operations fail, tenant and branch isolation remain intact, resource ownership is enforced, privilege escalation is prevented, revoked access stops working, and no alternative interface or execution path can bypass the same authorization rules.**

