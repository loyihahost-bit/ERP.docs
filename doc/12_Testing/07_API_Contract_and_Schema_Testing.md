# 07 — API Contract and Schema Testing

**Document ID:** TEST-07
**Status:** Accepted
**Version:** 1.0
**Parent:** `docs/12_Testing/README.md`
**Depends On:** TEST-01, TEST-02, TEST-05, TEST-06
**Related:** TEST-08, TEST-09, TEST-10, TEST-14, TEST-19

---

## 1. Purpose

This document defines the testing architecture for the FastFood API contract.

It establishes how the system verifies that:

* API requests conform to defined contracts;
* API responses conform to defined schemas;
* OpenAPI documentation remains synchronized with actual behavior;
* clients can rely on documented request and response structures;
* API changes remain compatible with existing clients;
* validation errors use stable and predictable structures;
* pagination, filtering, sorting, identifiers, timestamps, quantities, monetary values, and status fields are represented consistently;
* malformed or unsupported requests are rejected predictably;
* API contract regressions are detected before release;
* internal implementation changes do not unintentionally change the external API contract.

This document focuses on **what the API promises and how that promise is tested**.

It does not define the API implementation architecture itself.

---

# 2. Testing Boundary

API contract testing sits between application behavior and external consumers.

The boundary is:

```text
Domain Rules
     ↓
Application / Use Case
     ↓
API Contract
     ↓
HTTP Request / Response
     ↓
External Client
```

Testing at this layer verifies that application behavior is correctly exposed through the public API boundary.

The API contract layer must not become responsible for proving every underlying business rule.

For example:

* domain tests prove that a refund rule is correct;
* application tests prove that the refund use case is orchestrated correctly;
* repository tests prove persistence behavior;
* API contract tests prove that the refund endpoint accepts and returns the documented structures correctly;
* end-to-end tests prove the complete user-visible workflow.

---

# 3. Core Testing Principles

API contract testing follows these principles.

## 3.1 The Contract Is Testable

The API contract must be treated as a testable system artifact.

A documented endpoint is not considered reliable merely because:

* the server starts;
* the endpoint returns HTTP 200;
* one successful request works.

The contract must also be verified for:

* valid requests;
* invalid requests;
* boundary values;
* response schemas;
* error responses;
* optional fields;
* nullable fields;
* enumerations;
* pagination;
* compatibility;
* content types;
* serialization;
* versioning;
* authorization-related response behavior where contractually relevant.

---

## 3.2 OpenAPI Must Represent the Real API

Where OpenAPI is the authoritative API description, automated testing must detect meaningful differences between:

```text
OpenAPI Contract
       ↕
Actual API Behavior
```

The following are contract defects:

* documented endpoint does not exist;
* implemented endpoint is undocumented;
* documented request field is rejected unexpectedly;
* required field is actually optional;
* optional field is actually required;
* response contains an incompatible type;
* documented status code is not produced when expected;
* undocumented breaking response change is introduced;
* documented error schema differs from actual error output.

OpenAPI must not become a manually maintained description that is allowed to drift indefinitely from the running API.

---

# 4. API Contract as a Compatibility Boundary

The API is a boundary between independently changing components.

Consumers may include:

* web frontend;
* POS clients;
* branch devices;
* offline synchronization clients;
* administrative interfaces;
* integrations;
* external services;
* future mobile clients;
* reporting or operational tools.

Therefore, an API change must be evaluated according to consumer compatibility.

A change is not safe merely because the server implementation still works internally.

---

# 5. Contract Test Layers

API contract testing should use several complementary layers.

## 5.1 Schema Validation

Verifies that requests and responses conform to defined schemas.

Examples:

* required fields;
* field types;
* formats;
* nullable values;
* enum values;
* nested objects;
* arrays;
* object structure;
* additional-property policy.

---

## 5.2 Endpoint Contract Tests

Verify that each important endpoint behaves according to its documented contract.

Typical checks include:

* HTTP method;
* path;
* request structure;
* authentication requirement;
* expected status code;
* response content type;
* response schema;
* error schema.

---

## 5.3 Consumer Contract Testing

Where independently developed consumers depend on the API, contract testing may verify that provider behavior satisfies consumer expectations.

The goal is to detect:

```text
Provider Change
      ↓
Consumer Contract Break
```

before deployment.

Consumer contracts must not redefine the complete API specification.

They should capture the subset of behavior the consumer actually depends on.

---

## 5.4 Provider Contract Verification

The API provider must verify that implemented endpoints satisfy the authoritative contract.

This is especially important when:

* multiple clients exist;
* API versions coexist;
* generated clients are used;
* external integrations exist;
* frontend and backend are released independently.

---

# 6. OpenAPI Contract Testing

OpenAPI should be treated as a versioned contract artifact.

Tests should verify, where applicable:

* paths;
* methods;
* parameters;
* request bodies;
* response bodies;
* status codes;
* schemas;
* formats;
* enums;
* authentication requirements;
* content types;
* pagination structures;
* error structures.

The contract should be checked during CI rather than only during manual review.

---

# 7. Request Schema Testing

Every request schema should be tested for both accepted and rejected inputs.

## 7.1 Required Fields

Tests must verify:

```text
Required field present  → accepted when otherwise valid
Required field absent   → rejected
```

Examples include:

* product identifier;
* quantity;
* payment amount;
* branch identifier where required;
* employee identifier;
* recipe identifier;
* operation identifier.

The exact fields depend on the endpoint contract.

---

## 7.2 Optional Fields

Optional fields must be tested in at least these states:

```text
Field omitted
Field present with valid value
Field present with boundary value
```

If `null` is allowed, it must be tested separately from omission.

These states must not be treated as equivalent unless the contract explicitly defines them as equivalent.

---

## 7.3 Nullable Fields

A schema that permits:

```text
null
```

must be distinguished from a schema where the field may simply be absent.

Tests should verify the intended behavior.

---

## 7.4 Field Types

Tests must verify the documented type.

Examples:

```text
string
integer
number
boolean
array
object
null
```

The API must not silently change a field from one type to another.

For example:

```text
quantity: integer
```

must not unexpectedly become:

```text
quantity: string
```

---

# 8. Format Testing

Where the contract defines formats, they must be tested.

Examples include:

* UUID-like identifiers;
* date;
* date-time;
* email-like values;
* numeric formats;
* decimal values;
* structured identifiers.

Tests must verify both valid and invalid formats.

---

# 9. Monetary and Quantity Representation

Financial and inventory-related API fields require particular contract stability.

Examples:

* prices;
* payment amounts;
* discounts;
* cash totals;
* inventory quantities;
* recipe quantities;
* stock adjustments.

Tests must verify:

* documented representation;
* precision;
* scale where applicable;
* serialization;
* deserialization;
* zero values;
* boundary values;
* negative values where explicitly permitted;
* rejection of invalid values.

The API contract must not silently introduce floating-point representation where the system's financial contract requires a precise representation.

The exact financial calculation rules belong to domain and application testing.

This document verifies that the API representation remains compatible with those rules.

---

# 10. Enum and Status Testing

API enums are compatibility-sensitive.

Examples may include:

* order status;
* payment status;
* employee status;
* subscription status;
* inventory status;
* device status.

Tests must verify documented values.

When a new enum value is introduced, compatibility must be evaluated for existing clients.

A client that cannot safely process newly introduced values must not be assumed to remain compatible.

Therefore, enum changes require explicit compatibility review.

---

# 11. Request Validation Testing

Invalid requests must produce predictable contract behavior.

Test categories include:

* missing required field;
* wrong type;
* invalid format;
* invalid enum;
* invalid value range;
* malformed JSON;
* empty body;
* unexpected content type;
* invalid query parameter;
* invalid path parameter;
* invalid pagination parameters;
* invalid filter values;
* invalid sort fields.

Tests must verify the externally observable result.

The exact internal validation mechanism is outside this document.

---

# 12. Unknown and Additional Fields

The contract must explicitly define how unknown request fields are handled.

Possible policies include:

```text
Reject unknown fields
```

or:

```text
Ignore unknown fields
```

The selected behavior must be consistent with the API contract.

Tests must prevent accidental changes between these behaviors.

For sensitive or high-risk operations, unexpected input must not silently change business behavior.

---

# 13. Response Schema Testing

Response testing must verify more than HTTP status codes.

For each important response, tests should verify:

* content type;
* top-level structure;
* required fields;
* field types;
* nullable fields;
* nested objects;
* arrays;
* enum values;
* pagination metadata;
* identifiers;
* timestamps;
* monetary representation;
* quantity representation.

Example:

```text
HTTP 200
    ↓
Content-Type
    ↓
Response Schema
    ↓
Required Fields
    ↓
Field Types
    ↓
Nested Structures
```

---

# 14. Response Compatibility

Existing response consumers must not unexpectedly receive incompatible changes.

Potential breaking changes include:

* removing a required field;
* changing a field type;
* changing an enum incompatibly;
* changing object structure;
* changing a scalar into an object;
* changing an array into an object;
* changing a documented status code;
* changing the meaning of a field without versioning or compatibility handling.

Adding an optional response field may be compatible in many clients, but compatibility must still be evaluated against actual consumer behavior.

---

# 15. Error Contract Testing

Errors are part of the API contract.

The API must define predictable error structures where applicable.

Tests should cover:

* validation errors;
* authentication failures;
* authorization failures;
* resource-not-found responses;
* conflict responses;
* unsupported operations;
* malformed requests;
* rate or abuse-limit responses where exposed;
* server-side failure responses.

Error tests should verify:

* HTTP status;
* error structure;
* stable machine-readable error identifier where defined;
* field-level validation information where defined;
* absence of sensitive internal information.

Internal exception names, stack traces, database details, credentials, and infrastructure information must not become accidental API contract fields.

---

# 16. HTTP Status Code Testing

Status codes are part of the external contract.

Tests must verify that endpoints use the documented status codes for important outcomes.

Examples:

```text
Successful creation
Successful retrieval
Successful update
Successful deletion/archive where applicable
Validation failure
Authentication failure
Authorization failure
Not found
Conflict
Unsupported operation
Server failure
```

The exact status code depends on the endpoint contract.

Tests should detect accidental changes caused by implementation refactoring.

---

# 17. Content-Type Testing

API endpoints must consistently handle documented content types.

Tests should cover:

* supported request content type;
* unsupported content type;
* supported response content type;
* malformed body under a supported content type.

For JSON APIs, tests should verify that JSON serialization remains compatible.

File upload/download endpoints require separate contract tests for:

* content type;
* metadata;
* size-related behavior;
* response structure;
* download behavior.

Detailed file security is defined by the Security documentation and is not duplicated here.

---

# 18. Path, Query, and Header Contract Testing

API contracts may expose parameters through:

* path parameters;
* query parameters;
* request headers;
* request bodies.

Each parameter location must be tested according to its contract.

Examples:

```text
/orders/{order_id}
```

```text
/orders?branch_id=...
```

```text
X-Request-ID
```

The exact header names depend on the API specification.

Tests must verify:

* required/optional status;
* type;
* format;
* allowed values;
* invalid values;
* missing values;
* duplicate values where relevant.

---

# 19. Pagination Contract Testing

List endpoints must have stable pagination behavior.

Tests should verify:

* default page size;
* maximum page size;
* requested page size;
* page boundaries;
* empty result sets;
* first page;
* final page;
* pagination metadata;
* stable ordering where required;
* invalid pagination parameters.

If cursor-based pagination is used, tests must also verify:

* valid cursor;
* invalid cursor;
* expired cursor if applicable;
* repeated cursor;
* ordering consistency.

The exact pagination algorithm belongs to API implementation and data-access architecture.

This document verifies its external contract.

---

# 20. Filtering and Sorting Contract Testing

List endpoints must test documented filtering and sorting parameters.

Tests should verify:

* valid filters;
* invalid filters;
* valid sort fields;
* invalid sort fields;
* ascending/descending behavior;
* combinations of supported filters;
* empty results;
* pagination combined with filtering and sorting.

Unsupported arbitrary query parameters must not accidentally become functional API behavior.

---

# 21. Identifier Contract Testing

Identifiers are externally visible API values.

Tests should verify:

* valid identifiers;
* invalid identifiers;
* malformed identifiers;
* nonexistent identifiers;
* correct serialization;
* consistent representation across endpoints.

Tests must also ensure that changing an internal database identifier format does not accidentally break the public API contract.

The exact identifier generation and database strategy belong to other architecture documents.

---

# 22. Date and Time Contract Testing

Date and time fields require explicit compatibility tests.

Tests should verify:

* documented representation;
* timezone behavior;
* date-only values;
* date-time values;
* serialization;
* parsing;
* boundary dates;
* daylight-saving behavior where relevant to supported regions;
* invalid date/time values.

API tests must not rely on the local timezone of the machine running the tests.

Test environments must use controlled and deterministic time.

---

# 23. API Contract and Business Context

Many FastFood API resources are scoped by:

```text
Business / Tenant
        ↓
Branch
        ↓
Resource
```

Contract tests should verify that the API representation correctly expresses required context.

Examples include:

* branch identifiers;
* business identifiers where exposed;
* resource identifiers;
* scope-related request fields;
* response metadata.

The security documentation defines authorization and isolation policy.

API contract testing verifies that the public API correctly represents the required boundary and does not accidentally expose incompatible structures.

---

# 24. Authorization-Related Contract Testing

Authorization implementation belongs to the Security architecture.

However, API contract tests should verify externally observable authorization outcomes.

Examples:

```text
Unauthenticated request
        ↓
Documented authentication response
```

```text
Authenticated but unauthorized request
        ↓
Documented authorization response
```

```text
Authorized request
        ↓
Documented successful response
```

These tests verify the API boundary.

Detailed privilege, role, tenant, and branch authorization testing belongs to TEST-14.

---

# 25. Idempotency Contract Testing

Where an API operation supports idempotency, the idempotency behavior is part of the contract.

Tests should verify:

```text
First request
    ↓
Operation performed

Repeated request with same idempotency identity
    ↓
No unintended duplicate operation
```

Tests should cover:

* repeated identical requests;
* repeated requests after timeout;
* same idempotency identity with different payload;
* concurrent duplicate requests where applicable;
* failed first attempts;
* retry behavior.

The underlying concurrency implementation belongs to TEST-11.

API testing verifies the external contract.

---

# 26. API Versioning and Compatibility

API versioning must be tested as a compatibility policy.

Where multiple versions exist, tests must verify:

* version availability;
* version-specific schemas;
* version-specific behavior;
* supported clients;
* deprecation behavior;
* removal policy;
* compatibility boundaries.

A breaking change must not be introduced into an existing supported contract without an approved compatibility strategy.

---

# 27. Backward Compatibility

Backward compatibility testing asks:

> Can an existing supported client continue to communicate with the new API?

Potential breaking changes include:

* removed fields;
* renamed fields;
* changed types;
* changed requiredness;
* changed enum behavior;
* changed status codes;
* changed error structures;
* changed authentication contract;
* changed pagination structure;
* changed identifier format.

Compatibility testing must be based on the actual supported client contract rather than assumptions.

---

# 28. Forward Compatibility

Where appropriate, API clients should be tested against compatible server evolution.

Examples include:

* additional optional response fields;
* new non-breaking metadata;
* newly introduced optional request capabilities.

Clients should not fail merely because the server adds a field that the client does not need, unless the contract explicitly requires strict schemas.

The supported compatibility policy must be explicit.

---

# 29. Consumer Contract Testing

Consumer-driven contract tests may be used when multiple independently released clients exist.

Examples:

```text
Frontend → Backend API
POS Client → Backend API
Integration → Backend API
```

A consumer contract should identify:

* endpoint;
* request expectations;
* required response fields;
* expected status;
* required error behavior.

Consumer contracts must not encode accidental implementation details.

---

# 30. Provider Verification

The API provider must verify every supported consumer contract during CI or an appropriate release stage.

A provider change must not be released if it breaks a supported consumer contract unless:

* the consumer is intentionally migrated;
* compatibility is preserved;
* the breaking change is versioned;
* the change is explicitly approved.

---

# 31. Generated Client Testing

If API clients are generated from OpenAPI, generated-client compatibility must be tested.

Tests should verify:

* generated request models;
* generated response models;
* enum handling;
* nullable fields;
* date/time handling;
* numeric representation;
* required fields;
* API version compatibility.

Generated clients must not be treated as proof that the server implementation is correct.

They only prove that the contract can be consumed according to the generated representation.

---

# 32. Contract Drift Detection

Contract drift occurs when:

```text
Documented Contract ≠ Actual API Behavior
```

Drift detection should be automated where practical.

Examples:

```text
OpenAPI schema
      ↓
Contract validation
      ↓
Running API
      ↓
Observed response
```

The CI pipeline should detect meaningful differences.

Contract drift must be treated as a defect unless explicitly approved.

---

# 33. Negative Contract Testing

Negative API testing is mandatory.

Important negative categories include:

* missing fields;
* wrong field types;
* malformed JSON;
* invalid identifiers;
* invalid enum;
* invalid quantity;
* invalid monetary value;
* invalid date;
* invalid pagination;
* invalid filter;
* unsupported method;
* unsupported content type;
* unauthorized request;
* forbidden request;
* nonexistent resource;
* conflicting request;
* duplicate/idempotent request;
* oversized request where limits are contractual.

The purpose is to verify predictable rejection rather than merely successful execution.

---

# 34. Serialization and Deserialization Testing

Serialization is part of the contract.

Tests must verify:

```text
Internal Value
    ↓
API Representation
```

and:

```text
API Representation
    ↓
Internal Input
```

Important areas include:

* dates;
* timestamps;
* decimal values;
* quantities;
* identifiers;
* booleans;
* enums;
* null values;
* nested objects;
* arrays.

A value that is correct internally but incorrectly serialized is an API defect.

---

# 35. Schema Evolution Testing

Every schema change should be classified.

### Usually lower risk

Examples may include:

* adding optional request fields;
* adding optional response fields;
* adding non-breaking metadata.

### Potentially breaking

Examples include:

* removing fields;
* changing field types;
* changing requiredness;
* changing enum behavior;
* changing response structure;
* changing status codes;
* changing meaning.

The classification must be confirmed against actual consumers and compatibility policy.

---

# 36. Compatibility Matrix

For important APIs, maintain a compatibility matrix similar to:

| Contract | Current Provider | Supported Client | Compatibility |
| -------- | ---------------- | ---------------- | ------------- |
| API V1   | Current          | Web              | Required      |
| API V1   | Current          | POS              | Required      |
| API V1   | Current          | Offline Client   | Required      |
| API V1   | Current          | Integration      | If supported  |
| API V2   | Current          | New Clients      | If introduced |

The exact supported combinations depend on the release strategy.

The matrix must be updated when:

* a new client is introduced;
* an API version changes;
* a client is deprecated;
* a breaking change is approved.

---

# 37. Contract Test Data

API contract tests should use controlled and deterministic data.

Test data should cover:

* valid minimal request;
* valid complete request;
* boundary values;
* empty collections;
* large but permitted collections;
* missing resources;
* archived resources;
* different branch contexts;
* different resource states;
* invalid values.

Tests must not depend on uncontrolled production data.

Sensitive production data must not be copied into test environments without an approved data-protection process.

---

# 38. Deterministic API Tests

Contract tests must not depend on:

* current wall-clock time;
* local machine timezone;
* random uncontrolled identifiers;
* external service availability;
* production data;
* execution order.

Where the API contract contains time-sensitive values, tests must control the test clock or use deterministic fixtures.

---

# 39. External Integration Contracts

External integrations may have their own contracts.

Examples may include:

* payment providers;
* identity providers;
* government services;
* messaging services;
* delivery services;
* third-party APIs.

Contract tests should verify the boundary that FastFood owns.

External systems must not be treated as permanently available.

Failure behavior should be tested where it affects the FastFood API contract.

Detailed external integration architecture belongs to the relevant integration and application documentation.

---

# 40. Webhook Contract Testing

If FastFood exposes or consumes webhooks, webhook schemas must be tested as API contracts.

Tests should verify:

* event type;
* event identifier;
* payload schema;
* timestamp;
* resource identifier;
* version;
* retry behavior where contractual;
* duplicate delivery behavior where contractual;
* invalid payload handling.

Webhook contracts should be versioned independently where necessary.

---

# 41. API Documentation Testing

Documentation quality is part of contract quality.

Tests or CI checks should detect:

* undocumented endpoints;
* undocumented required parameters;
* schema mismatches;
* invalid examples;
* invalid enum values;
* broken references;
* inconsistent response schemas;
* stale version declarations.

Examples in API documentation should themselves be contract-valid.

An example that cannot be parsed or accepted according to the documented contract is a documentation defect.

---

# 42. Contract Test Organization

Tests should be organized by externally meaningful API boundary.

A logical structure may be:

```text
tests/
└── api/
    ├── contracts/
    ├── schemas/
    ├── endpoints/
    ├── errors/
    ├── compatibility/
    ├── consumers/
    └── fixtures/
```

The exact repository structure may differ.

The important requirement is that contract tests remain distinguishable from:

* domain tests;
* application tests;
* repository tests;
* full E2E tests.

---

# 43. Contract Test Naming

Names should describe the externally observable contract.

Good:

```text
creates_order_with_valid_request
rejects_order_when_quantity_has_invalid_type
returns_documented_order_response
returns_validation_error_for_missing_product_id
preserves_supported_order_response_schema
```

Avoid names based only on implementation details:

```text
calls_serializer_x
uses_handler_y
invokes_internal_method_z
```

The test should communicate what a client can rely upon.

---

# 44. Test Matrix

Important API contract tests should cover:

| Area             | Required Coverage                  |
| ---------------- | ---------------------------------- |
| HTTP method      | Supported and unsupported methods  |
| Path             | Valid and invalid paths            |
| Request schema   | Required, optional, nullable       |
| Types            | Valid and invalid types            |
| Formats          | Valid and invalid formats          |
| Enums            | Supported and unsupported values   |
| Query parameters | Valid, invalid, boundary           |
| Headers          | Required, optional, invalid        |
| Response schema  | Required fields and types          |
| Errors           | Stable error contract              |
| Status codes     | Documented outcomes                |
| Pagination       | Boundaries and invalid values      |
| Filtering        | Valid and invalid filters          |
| Sorting          | Valid and invalid fields           |
| Serialization    | Dates, decimals, identifiers       |
| Compatibility    | Supported client contracts         |
| Versioning       | Supported versions                 |
| Idempotency      | Repeated requests where applicable |
| OpenAPI          | Documentation/runtime alignment    |
| Negative paths   | Malformed and rejected requests    |

---

# 45. Relationship to Other Testing Documents

## TEST-03 — Unit Testing

Unit testing verifies isolated components.

API contract testing does not replace unit tests.

---

## TEST-04 — Domain Testing

Domain testing verifies business rules and invariants.

API tests verify that those behaviors are represented correctly at the HTTP boundary.

---

## TEST-05 — Application and Use Case Testing

Application tests verify workflow orchestration.

API tests verify how those workflows are exposed to external consumers.

Example:

```text
TEST-05
"Refund use case performs the correct application workflow."

TEST-07
"Refund endpoint accepts and returns the documented API contract."
```

---

## TEST-06 — Repository and Database Integration Testing

Repository tests verify persistence.

API contract tests should not attempt to prove database correctness.

---

## TEST-08 — Integration Testing

Integration testing verifies interactions between larger subsystems.

API contract tests establish the correctness of one important external boundary that integration tests may depend upon.

---

## TEST-09 — End-to-End and POS Testing

E2E testing verifies complete user-visible workflows.

API contract tests should be faster and more focused.

---

## TEST-10 — Offline and Synchronization Testing

Offline clients may depend heavily on API contracts during synchronization.

Contract testing must ensure that synchronization endpoints preserve their documented request/response structures.

---

## TEST-14 — Authentication, Authorization and Security Testing

TEST-14 performs deeper security behavior testing.

TEST-07 only verifies externally observable API contract behavior related to authentication and authorization.

---

## TEST-19 — CI Quality Gates and Release Testing

Contract tests should be integrated into CI and release gates according to risk and endpoint criticality.

---

# 46. FastFood-Critical API Contract Areas

The following areas require stronger contract coverage because they affect core business integrity.

## 46.1 Orders

Verify:

* order creation;
* order retrieval;
* order status;
* item structures;
* quantities;
* pricing representation;
* payment state;
* branch context.

---

## 46.2 Payments and Refunds

Verify:

* monetary representation;
* payment status;
* refund request structure;
* refund result;
* documented errors;
* idempotency where supported.

---

## 46.3 Cash Register

Verify:

* register opening;
* register state;
* register closing;
* handover;
* discrepancy representation;
* correction responses.

---

## 46.4 Inventory

Verify:

* product identifiers;
* quantities;
* stock state;
* inventory movement structures;
* adjustment responses;
* pagination/filtering;
* archive state.

---

## 46.5 Recipes

Verify:

* recipe structure;
* ingredient relationships;
* quantities;
* semi-finished product representation;
* recipe status;
* approval-related response structures.

---

## 46.6 Employees and Permissions

Verify:

* employee representation;
* role data;
* branch scope representation;
* permission structures;
* validation and error responses.

Detailed permission correctness belongs to TEST-14 and domain/application tests.

---

## 46.7 Subscription State

Verify:

* subscription status representation;
* expiration information;
* feature availability information where exposed;
* blocked-function responses;
* deletion/archive state where exposed.

The underlying subscription policy is defined elsewhere.

---

# 47. API Contract Failure Classification

Contract test failures should be classified.

### Category A — Documentation Defect

The implementation is correct but the contract is stale.

### Category B — Implementation Contract Defect

The implementation violates the approved contract.

### Category C — Intentional Contract Change

The API contract intentionally changed and has completed compatibility review.

### Category D — Consumer Compatibility Defect

A supported client contract is broken.

### Category E — Test Defect

The test does not represent the approved contract.

The correct classification must be established before changing tests.

Tests must not simply be weakened to make a failing build pass.

---

# 48. CI Integration

Contract tests should be integrated into CI.

A recommended progression is:

```text
Code Change
    ↓
Unit Tests
    ↓
Domain Tests
    ↓
Application Tests
    ↓
Repository Tests
    ↓
API Contract Tests
    ↓
Integration Tests
    ↓
E2E / Critical Workflow Tests
    ↓
Release Validation
```

Fast contract checks should run early.

More expensive provider/consumer or environment-dependent contract tests may run at later CI stages.

---

# 49. Contract Release Gates

A release must not proceed when a supported API contract is broken unless the change has an approved migration strategy.

Blocking examples:

* required response field removed;
* response type changed incompatibly;
* required request field unexpectedly introduced;
* supported status code changed;
* supported client contract broken;
* OpenAPI contract cannot be validated;
* documented endpoint is missing;
* actual response violates the approved schema.

---

# 50. Compatibility Review Checklist

Before approving an API contract change, verify:

* [ ] Is the change documented?
* [ ] Is OpenAPI updated?
* [ ] Is the change backward compatible?
* [ ] Which clients consume the affected endpoint?
* [ ] Are request schemas affected?
* [ ] Are response schemas affected?
* [ ] Are required fields affected?
* [ ] Are enums affected?
* [ ] Are status codes affected?
* [ ] Are error responses affected?
* [ ] Are pagination/filtering contracts affected?
* [ ] Are identifiers affected?
* [ ] Are date/time representations affected?
* [ ] Are monetary/quantity representations affected?
* [ ] Are API versions affected?
* [ ] Are consumer contracts updated where intentionally required?
* [ ] Are contract tests updated?
* [ ] Has regression testing been performed?
* [ ] Has release impact been reviewed?

---

# 51. Mandatory API Contract Rules

The following rules are mandatory.

1. Every supported public API must have a defined contract.
2. OpenAPI must remain synchronized with the approved API behavior where OpenAPI is the authoritative contract.
3. Request schemas must be tested for valid and invalid inputs.
4. Response schemas must be tested for valid structure and types.
5. Error responses are part of the API contract.
6. HTTP status codes are contract behavior and must be tested.
7. Required, optional, and nullable fields must be explicitly distinguished.
8. Enum changes require compatibility review.
9. Monetary and quantity representations must remain contract-stable.
10. Date/time representations must be deterministic and explicitly defined.
11. Pagination, filtering, and sorting behavior must be contract-tested where exposed.
12. Supported client contracts must be protected against unintended breaking changes.
13. Intentional breaking changes require an explicit compatibility and migration strategy.
14. Contract tests must include negative cases.
15. API contract tests must not be replaced by successful-response smoke tests.
16. Contract tests must not depend on uncontrolled production data.
17. Tests must not be weakened merely to accommodate an undocumented implementation change.
18. API contract changes must be reflected in documentation and relevant tests.
19. Contract verification must be part of CI for supported APIs.
20. Security-sensitive internal details must never become accidental API error or response fields.

---

# 52. API Contract Invariants

The following invariants must remain true.

### Contract Invariant 1

Every supported endpoint has an authoritative contract.

### Contract Invariant 2

Actual supported responses conform to their documented schemas.

### Contract Invariant 3

Required fields cannot silently become optional or vice versa.

### Contract Invariant 4

Field types cannot change incompatibly without compatibility handling.

### Contract Invariant 5

Error responses remain structurally predictable.

### Contract Invariant 6

Supported clients cannot be unintentionally broken by server changes.

### Contract Invariant 7

OpenAPI cannot silently diverge from the approved API behavior.

### Contract Invariant 8

Financial and inventory-related representations remain precise and stable.

### Contract Invariant 9

API tests remain deterministic and independent from uncontrolled production state.

### Contract Invariant 10

Contract changes are tested before release.

---

# 53. Acceptance Criteria

This document is considered correctly implemented when:

* API contracts have explicit ownership;
* OpenAPI is treated as a testable artifact where applicable;
* request schemas are tested;
* response schemas are tested;
* error contracts are tested;
* status codes are tested;
* invalid requests are tested;
* compatibility rules are explicit;
* consumer contracts can be verified where required;
* schema evolution is reviewed;
* critical FastFood APIs have stronger contract coverage;
* contract drift can be detected;
* CI includes appropriate contract gates;
* API documentation and tests evolve together.

---

# 54. Final Testing Rule

The API must be treated as a **stable external contract**, not merely as a collection of HTTP handlers.

A successful API test does not mean only:

```text
"The endpoint returned 200."
```

It means:

```text
Request
   ↓
Accepted According to Contract
   ↓
Application Behavior
   ↓
Documented Response
   ↓
Correct Schema
   ↓
Correct Status
   ↓
Compatible With Supported Consumers
```

The core rule is:

> **The API contract must remain explicit, testable, documented, and compatible with every supported consumer.**

Business correctness is established by domain and application tests. Persistence correctness is established by repository and database tests. Complete workflow correctness is established by integration and E2E tests.

**TEST-07 exists to ensure that the boundary connecting those behaviors to external consumers remains correct and stable.**

