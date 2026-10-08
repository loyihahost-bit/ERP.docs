# API External Integration and Webhook Architecture

**Document ID:** API-22
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/09_API/README.md`

---

## 1. Purpose

This document defines the architecture for external integrations and webhook processing in FastFood ERP.

The API must provide a controlled integration boundary between FastFood ERP and external systems without allowing external dependencies to become an uncontrolled part of core Business transactions.

The architecture covers:

* outbound API integrations;
* inbound webhooks;
* external providers;
* provider authentication;
* API credentials;
* webhook signatures;
* webhook replay protection;
* idempotency;
* retries;
* timeouts;
* circuit protection;
* asynchronous integration processing;
* external payment providers;
* notification providers;
* storage providers;
* future integrations;
* integration configuration;
* external event mapping;
* failure recovery;
* reconciliation;
* audit;
* security;
* Business and Branch isolation;
* performance;
* observability.

---

# 2. Integration Principles

The integration architecture follows these principles:

1. External systems are not authoritative for FastFood Business state unless explicitly defined by a domain integration contract.
2. PostgreSQL remains authoritative for FastFood transactional state.
3. External services must not directly modify Business state.
4. External API calls should not unnecessarily block core POS transactions.
5. Webhooks must be authenticated.
6. Webhook processing must be idempotent.
7. External events must have replay protection where duplicate effects are possible.
8. External failures must be isolated from core Business transactions.
9. External credentials must never be exposed to ordinary frontend clients.
10. External integrations must be scoped to Business and Branch where applicable.
11. External provider state must be reconciled when outcomes are uncertain.
12. Retries must be bounded.
13. Timeouts must be bounded.
14. Integration operations must be observable.
15. Integration configuration must be versionable where operational behavior changes.
16. Important external operations must be auditable.
17. Integration processing must remain compatible with offline operation.
18. External integrations must not bypass authorization.
19. External integrations must not bypass subscription restrictions.
20. Simplicity is preferred when multiple integration strategies provide equivalent correctness.

---

# 3. Integration Boundary

The integration boundary is:

```text
FastFood ERP
    │
    ├── Application
    │      ↓
    │   Integration Use Case
    │      ↓
    │   Integration Service
    │      ↓
    │   External Provider
    │
    └── Webhook API
           ↓
        Signature Verification
           ↓
        Event Validation
           ↓
        Idempotency
           ↓
        Integration Processing
           ↓
        Application Use Case
           ↓
        PostgreSQL
```

External providers must never receive direct database access.

---

# 4. External Integration Categories

Initial architecture supports:

```text
1. Payment Providers
2. Notification Providers
3. Email Providers
4. SMS Providers
5. File/Object Storage Providers
6. Authentication/Identity Providers where required
7. External Reporting/Accounting integrations where later approved
8. Future Delivery/Ordering integrations
9. Future Government or Regulatory integrations
```

Only explicitly approved integrations should be enabled.

---

# 5. Current Integration Scope

The initial system does not require every integration category.

The architecture must support future integration without requiring major restructuring.

Current likely integrations include:

* payment provider;
* email/SMS provider where needed;
* object/file storage;
* notification delivery;
* future external ordering channels.

Online ordering and customer-facing integrations remain outside the current core Business scope.

---

# 6. Integration Ownership

The Application layer owns Business integration use cases.

The Integration layer owns provider-specific communication.

Example:

```text
Application
    ↓
ProcessPaymentUseCase
    ↓
PaymentProviderService
    ↓
Provider Adapter
    ↓
External API
```

The Domain layer must not depend directly on provider-specific HTTP clients.

---

# 7. Provider Adapter

Each external provider should be isolated behind an adapter/interface.

Example:

```text
PaymentProvider
├── create_payment()
├── get_payment_status()
├── cancel_payment()
└── refund_payment()
```

Provider-specific implementation:

```text
ProviderAAdapter
ProviderBAdapter
```

The Application layer should depend on the abstraction rather than a concrete provider.

---

# 8. Provider Independence

The Business domain must not depend on provider-specific concepts where avoidable.

For example:

```text
FastFood Payment
```

should not become:

```text
ProviderA Payment Object
```

The integration layer maps provider-specific states into FastFood domain states.

---

# 9. External Provider Identity

External identifiers must be stored separately from internal resource UUIDs.

Example:

```text
FastFood Payment UUID
        ≠
Provider Payment ID
```

Both may be associated through an integration record.

---

# 10. Integration Mapping

Integration records may contain:

```text
integration_id
provider
provider_resource_type
provider_resource_id
business_id
branch_id
internal_resource_type
internal_resource_id
status
created_at
updated_at
```

The mapping must remain scoped to the correct Business.

---

# 11. Business Isolation

External integrations must be Business-scoped.

Provider credentials belonging to Business A must never be used for Business B.

Example:

```text
Business A
    ↓
Provider Account A

Business B
    ↓
Provider Account B
```

A provider account may be shared only when the Business explicitly uses a platform-owned integration model.

---

# 12. Branch Isolation

Where a provider configuration is Branch-specific, the integration must include Branch scope.

Example:

```text
Business
├── Branch A → Provider Configuration A
└── Branch B → Provider Configuration B
```

A Branch A webhook must not modify Branch B state.

---

# 13. Integration Configuration

Integration configuration may include:

* provider;
* enabled state;
* Business;
* Branch;
* external account identifier;
* supported operations;
* environment;
* configuration version;
* status;
* timestamps.

Secrets must be stored separately from ordinary configuration.

---

# 14. Integration States

An integration may use states such as:

```text
DISABLED
CONFIGURED
ACTIVE
DEGRADED
SUSPENDED
REVOKED
```

The exact implementation may simplify these states, but the operational state must remain explicit.

---

# 15. Integration Enablement

An integration must not become operational merely because credentials exist.

Activation should validate:

* Business scope;
* permission;
* provider configuration;
* credential validity where possible;
* supported capabilities;
* environment;
* security requirements.

---

# 16. Integration Permissions

Integration configuration requires explicit permissions.

Examples:

```text
integration.view
integration.configure
integration.activate
integration.disable
integration.test
integration.rotate_credentials
```

Only authorized users may change integration settings.

---

# 17. Owner and Super Admin Boundaries

Business Owners may configure integrations allowed for their Business.

Super Admin may manage platform-level integrations and provider availability.

Super Admin must not automatically gain access to Business secrets unless explicitly required and authorized by platform security policy.

---

# 18. Credential Storage

External credentials must be stored securely.

Examples:

* API keys;
* OAuth client secrets;
* access tokens;
* refresh tokens;
* provider signing secrets;
* webhook secrets;
* private certificates.

They must not be stored as ordinary plaintext Business configuration.

---

# 19. Credential Encryption

Sensitive integration credentials should be encrypted at rest.

The encryption mechanism must use managed or securely protected keys.

Application logs must never contain plaintext credentials.

---

# 20. Credential Rotation

The system must support controlled credential rotation.

Rotation should allow:

```text
Current Credential
       ↓
New Credential
       ↓
Validation
       ↓
Activation
       ↓
Old Credential Revocation
```

Where provider behavior allows overlapping credentials, overlap may be used to reduce downtime.

---

# 21. Credential Revocation

When credentials are revoked:

* future outbound requests must stop using them;
* cached credentials must be invalidated;
* queued jobs must revalidate integration state;
* active workflows must handle provider rejection safely.

Credential revocation must not corrupt internal Business state.

---

# 22. Environment Separation

External provider credentials must be environment-specific.

Example:

```text
Development
→ Sandbox Provider

Staging
→ Sandbox/Test Provider

Production
→ Production Provider
```

Production credentials must never be used in development or testing environments.

---

# 23. Sandbox Providers

Where a provider supports a sandbox/test environment, the integration architecture should support it.

Sandbox configuration must remain clearly separated from production configuration.

Test requests must never accidentally create real financial effects.

---

# 24. Outbound Integration Flow

Standard outbound flow:

```text
Application Use Case
       ↓
Validate Business State
       ↓
Commit Core Transaction if appropriate
       ↓
Create Integration Job / Outbox Event
       ↓
Worker
       ↓
Load Integration Configuration
       ↓
Provider Adapter
       ↓
External API
       ↓
Provider Result
       ↓
Persist Integration Result
       ↓
Audit / Event
```

External communication should normally happen outside the core transaction.

---

# 25. Core Transaction Isolation

External API calls should not normally occur inside the core PostgreSQL transaction.

Avoid:

```text
BEGIN
 ↓
Update Order
 ↓
Call External API
 ↓
Wait
 ↓
COMMIT
```

Prefer:

```text
BEGIN
 ↓
Update Order
 ↓
Create Outbox Event
 ↓
COMMIT
 ↓
Worker
 ↓
External API
```

---

# 26. Why External Calls Are Outside Core Transactions

External calls may:

* timeout;
* become unavailable;
* return slowly;
* return uncertain results;
* fail after accepting the request.

Keeping them outside core transactions protects:

* database connections;
* row locks;
* POS latency;
* transaction duration;
* Business consistency.

---

# 27. Outbox Integration

Important outbound integration events should use the existing Outbox architecture.

Example:

```text
Business Transaction
      +
Integration Event
      ↓
Atomic Database Commit
      ↓
Outbox Worker
      ↓
External Provider
```

The Outbox record provides durable intent for asynchronous processing.

---

# 28. Outbox Event Identity

Each outbound integration event should have a unique identity.

Example:

```text
event_uuid
operation_uuid
business_id
branch_id
integration_id
event_type
aggregate_type
aggregate_id
created_at
```

Duplicate event processing must not create duplicate external effects where the provider supports idempotency.

---

# 29. Provider Idempotency

Outbound state-changing requests should use provider-supported idempotency mechanisms where available.

Example:

```http
Idempotency-Key: <operation_uuid>
```

The same logical operation should not create duplicate provider-side effects.

---

# 30. Internal and External Idempotency

Two layers may be required:

```text
FastFood Idempotency
        +
Provider Idempotency
```

Internal idempotency prevents duplicate FastFood effects.

Provider idempotency prevents duplicate external effects.

They solve different failure scenarios.

---

# 31. External Operation Identity

An external operation should be traceable through:

```text
Request ID
Operation UUID
Outbox Event UUID
Integration ID
Provider Request ID
Provider Resource ID
```

Not every integration exposes every identifier.

Available identifiers should be preserved.

---

# 32. Request ID Propagation

Where supported, FastFood may send a correlation identifier to the provider.

Example:

```text
X-Correlation-ID
```

The provider's returned request/reference ID should also be recorded.

Sensitive credentials must never be included in correlation metadata.

---

# 33. Timeouts

Every outbound integration request must have a bounded timeout.

Examples:

```text
connect timeout
read timeout
total operation timeout
```

The exact values depend on provider behavior.

No external call may wait indefinitely.

---

# 34. Timeout Classification

An external timeout may mean:

```text
Request definitely failed
```

or:

```text
Provider may have accepted request
```

The application must distinguish known failure from uncertain outcome.

---

# 35. Uncertain External Outcome

Example:

```text
FastFood
   ↓
Payment Provider
   ↓
Request sent
   ↓
Network timeout
```

The system must not automatically assume:

```text
Payment failed
```

because the provider may have processed it.

The operation should enter a reconciliation state where appropriate.

---

# 36. Retry Strategy

Retries must be:

* bounded;
* delayed;
* operation-aware;
* idempotency-safe.

Possible strategy:

```text
Attempt 1
   ↓
short delay
   ↓
Attempt 2
   ↓
longer delay
   ↓
Attempt 3
   ↓
reconciliation / FAILED
```

Exact retry counts and delays are provider-specific configuration.

---

# 37. Retryable Failures

Potentially retryable:

* connection failure;
* temporary DNS failure;
* timeout;
* HTTP 502;
* HTTP 503;
* HTTP 504;
* provider-specific temporary error.

Not normally retryable:

* invalid credentials;
* invalid request;
* insufficient permissions;
* unsupported operation;
* permanently rejected payment.

---

# 38. Exponential Backoff

Retry delays should normally use bounded exponential backoff.

Example:

```text
Attempt 1 → immediate
Attempt 2 → short delay
Attempt 3 → longer delay
```

Jitter should be considered to avoid synchronized retries across many Businesses.

---

# 39. Retry Limit

Retries must have a maximum attempt count.

Unlimited retry loops are prohibited.

After the limit:

```text
FAILED
```

or:

```text
RECONCILIATION_REQUIRED
```

may be recorded depending on whether the external outcome is known.

---

# 40. Circuit Protection

Circuit breaking may be used for unstable providers.

Example:

```text
Healthy
   ↓
Repeated Failures
   ↓
OPEN
   ↓
No unnecessary requests
   ↓
Recovery Test
   ↓
HALF-OPEN
   ↓
Healthy
```

Circuit protection is an optimization and resilience mechanism.

It must not bypass Business correctness.

---

# 41. Provider Rate Limits

External providers may enforce their own rate limits.

The integration layer should detect:

```text
HTTP 429
```

or provider-specific equivalent.

The system should respect:

```text
Retry-After
```

where provided.

---

# 42. Provider Quotas

Integration architecture should account for:

* request quotas;
* daily limits;
* monthly limits;
* transaction limits;
* concurrency limits.

Business-level limits may also be required.

---

# 43. Queue Isolation

External integration jobs should use controlled queues.

Heavy provider traffic must not starve:

* synchronization;
* critical notifications;
* other Business operations.

Provider-specific queues may be used where necessary.

---

# 44. Integration Job Priority

Recommended priority:

```text
Critical Business integration
        ↓
Normal integration
        ↓
Bulk / reconciliation
```

POS core operations remain higher priority than external background processing.

---

# 45. Webhook Architecture

Inbound webhook flow:

```text
External Provider
       ↓
HTTPS
       ↓
Webhook Endpoint
       ↓
Request Validation
       ↓
Signature Verification
       ↓
Replay Protection
       ↓
Webhook Idempotency
       ↓
Persist Event
       ↓
Return Provider Response
       ↓
Asynchronous Processing
       ↓
Application Use Case
```

Webhook processing should normally acknowledge the provider quickly after safe event persistence.

---

# 46. Webhook Endpoint

Webhook endpoints should be dedicated to the provider/event contract.

Example:

```text
POST /api/v1/integrations/{integration_id}/webhooks/{provider}
```

Provider-specific routes may be used where required.

The route must not expose internal Business operation endpoints directly.

---

# 47. Webhook Authentication

Webhook requests must be authenticated using provider-supported mechanisms.

Preferred mechanisms include:

* HMAC signature;
* asymmetric signature;
* provider-issued verification token;
* mTLS where justified.

A webhook must not be trusted merely because it originates from a known IP address.

---

# 48. Webhook Signature Verification

When HMAC is used, the system should:

1. read the raw request body;
2. obtain the configured secret;
3. calculate the expected signature;
4. compare signatures using constant-time comparison;
5. validate timestamp if provided;
6. reject invalid signatures.

Signature verification must occur before Business processing.

---

# 49. Raw Body Requirement

Webhook signature validation may require the original raw request body.

Middleware must not modify the body before signature verification if the provider signs the exact payload.

---

# 50. Webhook Timestamp Validation

If a provider includes a signed timestamp, the API should validate an acceptable time window.

Example:

```text
Signed timestamp
      ↓
Allowed clock skew/window
      ↓
Accept or reject
```

This reduces replay risk.

---

# 51. Webhook Replay Protection

Webhook events must be protected against duplicate delivery.

Provider event identifiers should be stored where available.

Example:

```text
provider_event_id
```

A previously processed event must not create another Business effect.

---

# 52. Webhook Idempotency Record

A webhook idempotency record may contain:

```text
provider
integration_id
provider_event_id
event_type
received_at
processed_at
processing_status
payload_hash
result
```

The exact payload should only be retained according to data-retention requirements.

---

# 53. Duplicate Webhook

If the same webhook is received again:

```text
Already Processed
```

The API should return an appropriate successful acknowledgement where the provider expects retry suppression.

It must not repeat the Business operation.

---

# 54. Webhook Response Timing

Webhook endpoints should return quickly after:

* authentication;
* validation;
* idempotency persistence;

when asynchronous processing is safe.

Long Business processing should not unnecessarily block the provider's HTTP request.

---

# 55. Webhook Processing

Recommended:

```text
Receive
 ↓
Verify
 ↓
Persist
 ↓
Acknowledge
 ↓
Queue
 ↓
Process
```

The webhook endpoint should not perform large reports, external calls or long-running Business workflows synchronously.

---

# 56. Webhook Transaction

Persisting a webhook event and its processing state should use a transactional boundary.

Example:

```text
BEGIN
 ↓
Validate event identity
 ↓
Persist Webhook Event
 ↓
Create Processing Job
 ↓
COMMIT
 ↓
Return acknowledgement
```

This prevents an acknowledged event from being silently lost.

---

# 57. Webhook Processing State

Possible states:

```text
RECEIVED
VALIDATED
QUEUED
PROCESSING
PROCESSED
FAILED
RECONCILIATION_REQUIRED
IGNORED
```

The exact state model may be simplified.

---

# 58. Webhook Failure

If asynchronous processing fails after the webhook has been persisted:

* the provider should not necessarily receive repeated delivery;
* internal retry should process the stored event;
* failure must remain observable;
* the event must not be silently discarded.

---

# 59. Webhook Retry

Webhook processing retries should use:

* bounded attempts;
* exponential backoff;
* idempotency;
* failure classification.

Provider delivery retry and internal processing retry are separate mechanisms.

---

# 60. Provider Delivery Retry

If the webhook endpoint returns a failure before the event is safely accepted, the provider may retry.

The endpoint must therefore be designed so that:

```text
same event
→ safe repeated delivery
```

---

# 61. Webhook Ordering

Providers may deliver events out of order.

The integration layer must not assume that:

```text
Event A
```

always arrives before:

```text
Event B
```

when the provider does not guarantee ordering.

---

# 62. Webhook Event Version

Where supported, store the provider event version/schema version.

This allows processing logic to distinguish:

```text
Provider Event v1
Provider Event v2
```

without silently interpreting incompatible payloads.

---

# 63. Webhook Schema Validation

Incoming webhook payloads must be validated for:

* required fields;
* types;
* provider event type;
* identifiers;
* timestamp;
* signature metadata;
* schema version where applicable.

Validation must occur before Business processing.

---

# 64. Unknown Webhook Events

Unknown but authenticated events should be handled safely.

Possible behavior:

```text
Receive
 ↓
Verify
 ↓
Persist
 ↓
Mark IGNORED / UNSUPPORTED
 ↓
Alert or metric if appropriate
```

The endpoint must not interpret unknown events as successful Business commands.

---

# 65. Malformed Webhooks

Malformed or invalidly authenticated webhooks should be rejected.

The response should not expose internal implementation details.

The event should be observable for security monitoring where appropriate.

---

# 66. Payment Provider Integration

Payment providers are a high-risk integration category.

The payment architecture must distinguish:

```text
FastFood Payment
Provider Payment
Provider Transaction
Provider Settlement
```

These are not automatically identical concepts.

---

# 67. Payment Provider State

Provider states must be mapped into internal states.

Example:

```text
Provider:
AUTHORIZED

FastFood:
PENDING / AUTHORIZED
```

Exact mappings depend on provider contract.

Provider-specific states must not leak unnecessarily into core domain logic.

---

# 68. Payment Provider Uncertain State

If provider response is uncertain:

```text
TIMEOUT
NETWORK FAILURE
UNKNOWN
```

the payment must not be blindly marked failed.

The system should:

* query provider status;
* receive a webhook;
* perform reconciliation;
* or mark the payment as requiring reconciliation.

---

# 69. Payment Reconciliation

Payment reconciliation may compare:

```text
FastFood Payment
vs
Provider Payment
```

using:

* provider transaction ID;
* operation UUID;
* amount;
* currency;
* Business;
* timestamp;
* status.

Reconciliation must not silently modify historical financial state.

---

# 70. Payment Refund Integration

External refunds must use separate operation identity.

Example:

```text
FastFood Refund UUID
≠
Provider Refund ID
```

Refund requests must be idempotent.

Provider timeout may require reconciliation.

---

# 71. Payment Webhooks

Payment webhooks should be authenticated and mapped through:

```text
Provider Event
 ↓
Provider Transaction
 ↓
Integration Mapping
 ↓
FastFood Payment
 ↓
Application Use Case
```

The webhook must not directly update database rows outside the Application boundary.

---

# 72. Notification Provider Integration

Notification providers may include:

* email;
* SMS;
* future messaging providers.

Notification delivery must be asynchronous.

A failed notification must not rollback the Business transaction that triggered it.

---

# 73. Notification Delivery States

Possible states:

```text
PENDING
SENT
DELIVERED
FAILED
RETRYING
EXPIRED
```

Provider capabilities determine which states are available.

---

# 74. Notification Idempotency

The same notification operation should not unintentionally send duplicate messages.

Deduplication may use:

```text
Business
Notification Type
Source Event
Recipient
Operation UUID
```

The exact deduplication strategy depends on the notification type.

---

# 75. Email Integration

Email providers must be isolated behind an adapter.

The system should store:

* provider message ID;
* delivery state;
* failure reason;
* timestamps.

The system should not store unnecessary provider payloads.

---

# 76. SMS Integration

SMS integrations must account for:

* provider rate limits;
* delivery status;
* regional restrictions;
* duplicate prevention;
* cost controls.

SMS failure must not rollback core Business state.

---

# 77. Storage Integration

Object storage may be used for:

* product images;
* report exports;
* documents;
* generated files;
* backups where separately configured.

The API must use logical File IDs rather than exposing provider storage paths.

---

# 78. Storage Provider Boundary

Application code should use a storage abstraction:

```text
ObjectStorage
├── put()
├── get()
├── delete()
├── exists()
└── generate_download_reference()
```

Provider-specific APIs remain inside infrastructure.

---

# 79. Signed Download URLs

Where object storage supports signed URLs, they may be used for controlled downloads.

Signed URLs must:

* expire;
* be scoped to the specific object;
* not grant unrelated storage access;
* not bypass Business authorization before issuance.

---

# 80. Signed Upload URLs

Signed upload URLs may be used where large uploads require direct-to-storage behavior.

Before issuing one, the API must validate:

* authentication;
* Business;
* Branch where applicable;
* permission;
* file type;
* file size;
* destination scope.

---

# 81. Storage Webhooks

If storage providers send events, they must use the same webhook security model:

* signature verification;
* event identity;
* replay protection;
* idempotency;
* asynchronous processing.

---

# 82. Integration Test Endpoint

An integration may provide a test operation such as:

```text
POST /api/v1/integrations/{id}/test
```

The test must:

* validate permission;
* avoid real financial effects;
* use sandbox/test APIs where possible;
* avoid modifying Business state unnecessarily.

---

# 83. Integration Health

The system should expose integration health internally.

Possible states:

```text
HEALTHY
DEGRADED
UNAVAILABLE
MISCONFIGURED
AUTHENTICATION_FAILED
RATE_LIMITED
```

Health state is operational information and does not automatically represent Business transaction state.

---

# 84. Provider Health Checks

Health checks must not create harmful external traffic.

Use lightweight provider-supported checks where available.

Do not continuously poll expensive provider endpoints merely to determine health.

---

# 85. Integration Failure Isolation

An external provider failure must not normally stop:

* local Order creation;
* local inventory operations;
* local Cash Session operations;
* local reporting;
* offline operation.

If a specific Business operation fundamentally requires the provider, that operation may become unavailable while unrelated operations remain functional.

---

# 86. External Failure and POS

Example:

```text
Payment Provider unavailable
        ↓
Cash Payment remains available
        ↓
Local Order operations continue
```

provided the Business rules permit cash payment.

The API must not unnecessarily disable the entire POS because one external service is unavailable.

---

# 87. External Failure and Offline Mode

Offline mode must not depend on real-time external API availability.

For example:

```text
Internet unavailable
        ↓
Local authorized POS operation
        ↓
Local transaction
        ↓
Synchronization later
```

Provider-dependent operations must follow their specific offline restrictions.

---

# 88. Integration and Subscription

External integrations are subject to Business subscription entitlement.

When the Business becomes `READ_ONLY`:

* allowed historical integration data may remain viewable;
* new configuration changes are blocked;
* prohibited outbound operations are blocked;
* queued Jobs must revalidate entitlement before execution.

---

# 89. Deleted Business

When a Business becomes `DELETED`:

* new integration operations are rejected;
* webhook processing must not resurrect the Business;
* queued integration Jobs must stop;
* provider callbacks must not recreate Business state;
* integration credentials must no longer authorize Business operations.

---

# 90. Webhook and Deleted Business

A delayed webhook may arrive after Business deletion.

The system must:

```text
Verify webhook
 ↓
Resolve integration
 ↓
Check Business lifecycle
 ↓
Reject / archive safely
```

It must never recreate deleted Business state.

---

# 91. Webhook and Read-Only Business

For `READ_ONLY` Businesses:

* webhook receipt may be retained for reconciliation;
* mutation of prohibited Business state must be blocked;
* historical/event information may be retained according to lifecycle policy.

A webhook must not bypass subscription restrictions.

---

# 92. Integration Audit

Important integration events should be auditable.

Examples:

* integration enabled;
* integration disabled;
* credential rotation;
* integration test;
* provider failure;
* webhook verification failure;
* payment reconciliation;
* external refund;
* integration configuration change.

---

# 93. Audit Context

Integration audit records should include, where applicable:

```text
event_uuid
operation_uuid
business_id
branch_id
employee_id
device_id
integration_id
provider
external_reference
event_type
result
timestamp
```

Secrets must never be included.

---

# 94. Webhook Audit

Webhook audit/operational records may include:

* provider;
* integration;
* provider event ID;
* event type;
* verification result;
* processing result;
* timestamps;
* failure category.

Raw sensitive payloads should not automatically be copied into audit records.

---

# 95. External Event Storage

Raw webhook payloads may be stored when required for:

* reconciliation;
* debugging;
* legal/audit requirements;
* provider support.

Retention must be bounded.

Sensitive fields should be minimized or protected.

---

# 96. Payload Encryption

Sensitive external payloads should be encrypted at rest where required by data classification.

Webhook secrets and credentials require stronger protection than ordinary event metadata.

---

# 97. External Data Minimization

Do not persist provider data merely because it is available.

Store only what is needed for:

* Business operation;
* reconciliation;
* audit;
* support;
* legal/retention requirements.

---

# 98. External Data Mapping

Provider payloads should be mapped into controlled internal DTOs.

Do not expose raw provider payloads directly to frontend clients.

This prevents external schema changes from silently becoming public API changes.

---

# 99. Provider Schema Changes

Provider APIs may change independently.

The integration adapter must isolate provider-specific schema changes.

If a provider changes:

```text
Provider JSON
```

only the provider adapter and related integration contract should need modification where possible.

---

# 100. Integration Versioning

Integration contracts should identify:

* provider;
* provider API version;
* internal integration version;
* supported capabilities.

Example:

```text
Provider API v3
FastFood Integration Adapter v2
```

Provider upgrades should be tested before activation.

---

# 101. Capability Discovery

Where providers expose capabilities, the integration layer may determine:

* payment support;
* refund support;
* webhook support;
* status query;
* currency support;
* sandbox support.

Unsupported capabilities must be rejected explicitly.

---

# 102. Integration Configuration Versioning

Important integration configuration changes should be versioned where they affect operational behavior.

Examples:

* provider account;
* payment routing;
* webhook secret;
* Branch mapping;
* notification configuration.

Historical integration events should retain enough context to determine which configuration was active.

---

# 103. Integration Concurrency

Concurrent integration configuration changes must use optimistic concurrency.

Example:

```text
Configuration Version 5
        ↓
User A updates
        ↓
Version 6

User B still editing Version 5
        ↓
409 CONFLICT
```

Silent overwrite is prohibited.

---

# 104. Integration Job Concurrency

The same external operation must not be executed concurrently when doing so could create duplicate effects.

Use:

* idempotency;
* operation locks;
* provider idempotency;
* unique constraints.

Redis may coordinate but must not replace database correctness.

---

# 105. Webhook Concurrency

The same webhook event may arrive concurrently.

The database must enforce unique event identity where appropriate.

Example:

```text
provider + integration_id + provider_event_id
```

must be uniquely constrained when provider guarantees event IDs are unique within that scope.

---

# 106. External Provider Authentication

Outbound requests may use:

* API key;
* OAuth 2.0;
* signed request;
* mTLS;
* provider-specific authentication.

Credentials must be injected securely by the integration infrastructure.

---

# 107. OAuth Integration

Where OAuth is required:

* authorization state must be protected;
* redirect URIs must be explicit;
* state/nonce mechanisms must be used where applicable;
* authorization codes must not be logged;
* refresh tokens must be securely stored;
* token rotation/revocation must be supported where provider allows.

---

# 108. OAuth Callback

OAuth callbacks must validate:

* expected Business/integration context;
* state;
* provider;
* authorization result;
* callback freshness where applicable.

A callback must not attach credentials to the wrong Business.

---

# 109. SSRF Protection

If the system accepts external URLs for integration configuration, it must protect against Server-Side Request Forgery.

The API must not allow arbitrary internal network access through user-controlled URLs.

Possible controls:

* allowlisted domains;
* scheme restrictions;
* DNS/IP validation;
* private network blocking;
* redirect validation;
* outbound network policy.

---

# 110. URL Validation

External URLs should allow only required schemes, typically:

```text
https://
```

Plain:

```text
file://
```

or other dangerous schemes must not be accepted unless explicitly required and safely isolated.

---

# 111. Redirect Protection

External HTTP clients should validate redirects.

A trusted public URL must not silently redirect to:

* private network;
* localhost;
* cloud metadata service;
* internal administration endpoint.

---

# 112. Integration Network Isolation

External integration workers may be isolated from internal infrastructure where practical.

They should not have unnecessary access to:

* PostgreSQL;
* internal administration services;
* private infrastructure endpoints.

Network restrictions complement application-level security.

---

# 113. Provider Response Validation

External responses must be treated as untrusted input.

The system must validate:

* response schema;
* identifiers;
* amounts;
* currency;
* state;
* signatures where applicable.

The provider response must not automatically override internal state without domain validation.

---

# 114. External Amount Validation

For financial integrations, the server must compare provider values against expected Business operation values.

Example:

```text
Expected:
25,000 UZS

Provider:
250,000 UZS

Result:
Rejected / Reconciliation Required
```

Client or provider values cannot silently redefine the authoritative Order amount.

---

# 115. Currency Validation

External payment responses must validate currency.

A provider response in an unexpected currency must not be accepted as a successful payment for the original transaction.

---

# 116. External Status Mapping

Provider statuses should be mapped through an explicit mapping table.

Example:

```text
Provider Status
      ↓
Integration Mapping
      ↓
FastFood Status
```

Unknown provider statuses must not automatically map to successful Business states.

---

# 117. Unknown Provider Status

If a provider introduces an unknown status:

```text
Unknown
 ↓
Do not assume success
 ↓
Mark for reconciliation / unsupported state
 ↓
Alert
```

This prevents silent semantic errors after provider changes.

---

# 118. External Integration Observability

Metrics should include:

```text
integration_request_count
integration_success_count
integration_failure_count
integration_timeout_count
integration_retry_count
integration_rate_limit_count
webhook_received_count
webhook_verified_count
webhook_rejected_count
webhook_duplicate_count
webhook_processing_failure_count
reconciliation_count
```

Metrics must use low-cardinality labels.

---

# 119. Provider-Level Metrics

Provider metrics may be grouped by:

```text
provider
operation_type
result_category
environment
```

Avoid arbitrary Business UUIDs as metric labels.

---

# 120. Integration Logging

Integration logs should include:

```text
request_id
operation_uuid
integration_id
provider
operation_type
business_id
branch_id
provider_request_id
provider_resource_id
result
latency
```

Secrets and sensitive payloads must be excluded.

---

# 121. External Request Logging

Do not log full external request bodies when they may contain:

* payment credentials;
* tokens;
* personal data;
* provider secrets;
* financial information.

Use controlled structured fields instead.

---

# 122. Webhook Security Logging

Webhook security failures should record enough information to investigate:

* provider;
* integration;
* event ID where available;
* verification result;
* timestamp;
* source information where safe;
* request ID.

Never log webhook secrets.

---

# 123. Integration Alerts

Alerts should be considered for:

* provider outage;
* repeated authentication failures;
* repeated webhook signature failures;
* high retry rate;
* reconciliation backlog;
* payment uncertainty;
* integration queue backlog;
* abnormal provider response changes.

---

# 124. Reconciliation

Reconciliation is required when FastFood and an external provider may disagree.

Examples:

```text
FastFood:
PAYMENT_PENDING

Provider:
COMPLETED
```

or:

```text
FastFood:
REFUND_PENDING

Provider:
FAILED
```

The reconciliation process must determine the authoritative result according to the integration contract.

---

# 125. Reconciliation Jobs

Reconciliation should run asynchronously.

Possible triggers:

* provider webhook;
* timeout;
* scheduled reconciliation;
* operator request;
* detected inconsistency.

Reconciliation must be idempotent.

---

# 126. Reconciliation Authority

Reconciliation must not blindly trust either side.

It should use:

* provider evidence;
* internal transaction;
* operation identity;
* expected amount;
* currency;
* Business scope;
* provider status;
* timestamps.

The final Business state is established through the Application/Domain rules.

---

# 127. Reconciliation History

Reconciliation decisions must preserve:

* original state;
* detected discrepancy;
* provider evidence;
* resolving operation;
* actor/system source;
* timestamp;
* final state.

Historical records must not be silently overwritten.

---

# 128. Manual Reconciliation

Some external discrepancies may require authorized manual resolution.

Manual reconciliation requires:

* explicit permission;
* reason;
* audit;
* immutable correction history.

Ordinary users must not manually force financial success merely because a provider state is unclear.

---

# 129. External Integration Failure States

Integration operations may use:

```text
PENDING
SENT
CONFIRMED
FAILED
RETRYING
UNKNOWN
RECONCILIATION_REQUIRED
CANCELLED
```

These states are integration states and must not automatically replace core domain states.

---

# 130. Integration Cancellation

Cancellation may be supported when the provider supports it.

A cancellation request must be:

* authorized;
* idempotent;
* concurrency-safe;
* provider-aware.

If cancellation outcome is uncertain, reconciliation is required.

---

# 131. Integration and Notifications

External provider failures may generate internal notifications.

Example:

```text
Payment Provider Unavailable
        ↓
Operational Alert
        ↓
Owner / authorized employee
```

The notification must not itself become the authoritative integration state.

---

# 132. Integration and Audit

Provider communication and Business state changes should remain separately traceable.

Example:

```text
Integration Event
     ↓
Payment Provider Response
     ↓
Application Decision
     ↓
Business Payment State
     ↓
Audit Event
```

---

# 133. Integration and Historical Integrity

Provider changes must not rewrite historical Business data.

Examples:

```text
Current Provider Price
≠
Historical Order Price
```

```text
Current Provider Configuration
≠
Historical Payment Configuration
```

Historical transaction snapshots remain authoritative.

---

# 134. External Provider Downtime

Provider downtime must result in controlled degradation.

The system should:

* detect failure;
* stop unnecessary retries;
* queue safe operations;
* notify operators;
* preserve local Business operations where possible;
* reconcile later.

---

# 135. Integration Backpressure

When provider capacity is reduced:

* queue work;
* limit concurrency;
* apply provider rate limits;
* prioritize critical operations;
* prevent unlimited backlog.

---

# 136. Integration Queue Limits

Queues must have bounded operational behavior.

The system must prevent unlimited:

* pending Jobs;
* retry attempts;
* webhook backlog;
* reconciliation events.

When limits are reached, the system must apply controlled backpressure and alert operators.

---

# 137. External Integration and POS Performance

External integrations must not unnecessarily increase core POS latency.

Initial target:

| Operation                             |   Target |
| ------------------------------------- | -------: |
| Integration configuration read p95    | ≤ 200 ms |
| Integration configuration update p95  | ≤ 300 ms |
| Integration test request p95          | ≤ 500 ms |
| Webhook acknowledgement p95           | ≤ 300 ms |
| Outbound integration job creation p95 | ≤ 300 ms |
| Reconciliation job creation p95       | ≤ 300 ms |
| Normal webhook persistence p95        | ≤ 200 ms |

Actual provider processing time is excluded from internal API latency targets where processing is asynchronous.

---

# 138. Webhook Availability

Initial webhook API availability target:

**≥ 99.9% monthly**

Webhook processing must remain safe during:

* worker failures;
* Redis failure;
* temporary provider outage;
* database contention.

---

# 139. Webhook Acknowledgement

The webhook endpoint should acknowledge only after the event is safely accepted according to its persistence policy.

An event that was not safely recorded must not receive a success response merely to reduce provider retries.

---

# 140. Integration Testing

Every integration should have tests for:

* authentication;
* credential handling;
* successful request;
* invalid request;
* timeout;
* provider failure;
* provider rate limit;
* duplicate request;
* retry;
* uncertain outcome;
* reconciliation;
* webhook signature;
* replay;
* duplicate webhook;
* out-of-order events;
* unknown event;
* provider schema change;
* Business isolation;
* Branch isolation.

---

# 141. Webhook Security Testing

Webhook tests must verify:

```text
Valid signature
Invalid signature
Missing signature
Expired timestamp
Replay event
Duplicate event
Modified payload
Wrong integration
Wrong Business
Wrong Branch
Unknown event
Malformed payload
```

---

# 142. Integration Contract Testing

Provider adapters should use contract tests where provider documentation or sandbox behavior allows.

Tests should validate:

* request structure;
* authentication;
* response mapping;
* error mapping;
* webhook schema;
* provider state mapping.

---

# 143. Sandbox Testing

Financial integrations should use provider sandbox environments for automated tests whenever available.

Production credentials must not be used in automated CI tests.

---

# 144. Failure Injection

Critical integrations should be tested under:

* network timeout;
* DNS failure;
* HTTP 500;
* HTTP 503;
* HTTP 429;
* malformed response;
* delayed response;
* duplicate response;
* provider outage.

The system must recover without corrupting Business state.

---

# 145. Security Testing

Integration security testing should include:

* secret leakage;
* SSRF;
* webhook signature bypass;
* replay;
* credential misuse;
* cross-Business integration access;
* cross-Branch access;
* malicious provider payload;
* oversized webhook;
* malformed external response.

---

# 146. External Integration Documentation

Every integration must document:

* provider;
* purpose;
* supported operations;
* authentication method;
* credential requirements;
* Business/Branch scope;
* outbound endpoints;
* inbound webhook endpoints;
* event types;
* idempotency;
* retries;
* timeout;
* reconciliation;
* failure behavior;
* rate limits;
* data retention;
* audit requirements.

---

# 147. Integration Lifecycle

Recommended lifecycle:

```text
Defined
   ↓
Configured
   ↓
Validated
   ↓
Active
   ↓
Degraded / Suspended
   ↓
Disabled / Revoked
```

Historical integration events remain available according to retention rules.

---

# 148. Integration Deactivation

When an integration is disabled:

* new outbound operations are blocked;
* queued operations are revalidated;
* webhook behavior follows provider-specific policy;
* historical integration records remain;
* credentials may be revoked or retained securely according to policy.

---

# 149. Integration Deletion

Deleting an integration configuration must not delete historical Business transactions.

Historical mappings may be archived rather than physically removed when required for audit/reconciliation.

---

# 150. Integration and Data Lifecycle

When Business data becomes eligible for deletion:

* integration credentials must be revoked or destroyed according to lifecycle policy;
* queued Jobs must stop;
* webhook events must not recreate Business state;
* provider mappings may be retained only where required by retention policy;
* sensitive credentials must not survive Business deletion unnecessarily.

---

# 151. API Security Boundary

External integration endpoints remain protected by the general API security architecture.

They must follow:

* HTTPS;
* CORS policy where browser access is relevant;
* authentication;
* authorization;
* request limits;
* structured errors;
* logging;
* monitoring.

Webhook endpoints use provider-specific authentication in addition to normal transport security.

---

# 152. Integration Error Categories

Integration errors should be classified as:

```text
CONFIGURATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
VALIDATION_ERROR
PROVIDER_REJECTION
RATE_LIMITED
TIMEOUT
NETWORK_ERROR
PROVIDER_UNAVAILABLE
UNKNOWN_PROVIDER_STATE
WEBHOOK_VERIFICATION_FAILED
WEBHOOK_REPLAY
DUPLICATE_EVENT
RECONCILIATION_REQUIRED
INTERNAL_ERROR
```

The API should expose safe stable error codes where applicable.

---

# 153. Integration Error Handling

Provider-specific errors should be mapped to internal error categories.

Do not expose raw provider stack traces or internal provider implementation details to ordinary clients.

Provider reference information may be included where safe and useful.

---

# 154. External Error Retryability

The integration layer should classify errors as:

```text
DO_NOT_RETRY
RETRY
RETRY_WITH_BACKOFF
RECONCILIATION_REQUIRED
USER_ACTION_REQUIRED
```

The classification depends on provider semantics.

---

# 155. Integration and API Errors

External provider failure should not automatically become:

```text
500 INTERNAL_ERROR
```

when the API can safely expose a more meaningful stable state such as:

```text
SERVICE_UNAVAILABLE
PAYMENT_PENDING
RECONCILIATION_REQUIRED
INTEGRATION_MISCONFIGURED
```

The public error contract remains defined in:

`09_API_Error_Handling_and_Error_Codes.md`

---

# 156. External Integration and Async Jobs

Long-running integrations should use the existing Job architecture.

Example:

```text
POST /api/v1/integrations/{id}/sync
        ↓
202 Accepted
        ↓
Job
        ↓
Provider
        ↓
Result
```

Job authorization and Business scope remain mandatory.

---

# 157. Integration and Bulk Operations

Bulk external operations must be bounded.

Examples:

* bulk notification;
* bulk synchronization;
* provider reconciliation.

Bulk provider calls must respect provider rate limits and Business isolation.

---

# 158. Integration and Caching

Safe integration metadata may be cached.

Examples:

* provider capabilities;
* non-sensitive configuration metadata;
* provider API version.

Credentials and security-sensitive authorization state must use bounded, revocation-safe handling.

---

# 159. Integration and Configuration Cache

If integration configuration is cached:

```text
Database
   ↓
Authoritative Configuration
   ↓
Cache
```

Changes must invalidate or version cached configuration.

Queued Jobs must revalidate the current configuration before performing sensitive external operations.

---

# 160. Integration and Subscription Cache

Cached subscription state must not allow an expired Business to continue prohibited external operations indefinitely.

Workers must revalidate entitlement before important queued operations.

---

# 161. Integration and Device Context

For POS-originated integrations, device context may be retained:

```text
Business
Branch
Employee
Device
Cash Session
Operation
```

This supports audit and troubleshooting.

Device UUID alone must never authorize an external integration.

---

# 162. Integration and Offline Transactions

Offline-created transactions may later trigger external integrations after synchronization.

Example:

```text
Offline Order
    ↓
Sync
    ↓
Authoritative Order
    ↓
Integration Event
    ↓
External Provider
```

The integration must not execute prematurely based solely on untrusted local state.

---

# 163. Offline Payment Restrictions

Provider-dependent payment operations must follow the financial API policy.

A transaction created offline must not claim successful external payment merely because the client recorded a local payment state.

External confirmation remains authoritative according to the provider integration contract.

---

# 164. External Integration and Audit Context

Every important integration operation should be traceable to:

```text
Business
Branch
Employee
Device
Operation
Integration
Provider
External Reference
```

Where a system-generated operation has no direct employee, the actor should be recorded as:

```text
SYSTEM
```

with the originating event preserved.

---

# 165. External Integration and Historical Reports

Historical reports must use the Business transaction state and historical integration snapshots required by the report definition.

Current provider configuration must not rewrite historical reports.

---

# 166. External Integration and Notifications

Integration failures may generate internal alerts.

Examples:

* payment provider unavailable;
* webhook verification failures;
* reconciliation backlog;
* provider credential expiration.

Notifications remain informational and do not replace integration state.

---

# 167. Operational Controls

Authorized operators may need to:

* disable an integration;
* pause an integration queue;
* retry failed integration Jobs;
* trigger reconciliation;
* rotate credentials;
* inspect provider health;
* inspect webhook processing state.

These controls must themselves be permission-controlled and audited.

---

# 168. Emergency Integration Disablement

The system should support rapid disablement of a compromised integration.

Emergency disablement should:

* prevent new outbound requests;
* reject or safely retain inbound events;
* stop queued sensitive operations;
* preserve historical records;
* generate an audit/security event.

---

# 169. Provider Credential Compromise

If provider credentials are suspected to be compromised:

1. Disable integration.
2. Revoke provider credentials.
3. Rotate credentials.
4. Review integration logs.
5. Review affected operations.
6. Reconcile financial state where necessary.
7. Re-enable only after validation.

The process must be auditable.

---

# 170. Webhook Secret Compromise

If a webhook signing secret is compromised:

* rotate the secret;
* invalidate old verification state where supported;
* monitor suspicious events;
* reject invalid signatures;
* review recent webhook events;
* reconcile affected Business state.

---

# 171. Integration Disaster Recovery

Integration state must be recoverable from authoritative storage.

Redis or temporary queue state must not be the only record of an important external operation.

Outbox, webhook event records and integration mappings should survive infrastructure restarts according to their retention requirements.

---

# 172. Provider Data Loss

If an external provider loses or cannot return historical data, FastFood must retain its own authoritative Business transaction history.

Provider data must not be the sole source for historical Business accounting.

---

# 173. Integration Recovery

After provider recovery:

```text
Provider Available
      ↓
Retry safe operations
      ↓
Process queued events
      ↓
Run reconciliation
      ↓
Resolve uncertain states
      ↓
Return to normal
```

Recovery must be bounded and observable.

---

# 174. Integration Performance SLO

Initial integration SLOs:

| Metric                                |          Target |
| ------------------------------------- | --------------: |
| Integration configuration read p95    |        ≤ 200 ms |
| Integration configuration update p95  |        ≤ 300 ms |
| Integration test request p95          |        ≤ 500 ms |
| Webhook acknowledgement p95           |        ≤ 300 ms |
| Webhook persistence p95               |        ≤ 200 ms |
| Outbound integration job creation p95 |        ≤ 300 ms |
| Reconciliation job creation p95       |        ≤ 300 ms |
| Normal webhook processing start       |           ≤ 5 s |
| Critical reconciliation start         |          ≤ 30 s |
| API availability                      | ≥ 99.9% monthly |

External provider response latency is not included in asynchronous internal API SLOs.

---

# 175. Integration Resource Limits

The system must enforce bounds on:

* outbound request concurrency;
* webhook body size;
* webhook processing time;
* retry count;
* queue depth;
* reconciliation backlog;
* provider API calls;
* stored raw payload size;
* integration configuration size.

---

# 176. API Integration Guardrails

The implementation must prohibit:

* direct provider calls from frontend clients using Business secrets;
* direct database access by external providers;
* external API calls inside long-lived core transactions;
* unbounded retries;
* unbounded webhook processing;
* unauthenticated webhooks;
* missing replay protection;
* trusting provider payloads without validation;
* trusting provider status without mapping;
* provider credentials in logs;
* provider credentials in frontend responses;
* provider credentials in ordinary configuration storage;
* cross-Business provider credential reuse;
* cross-Branch integration state mutation;
* webhook-driven resurrection of deleted Business data;
* provider failure causing unrelated POS failure;
* raw provider payloads becoming public API contracts;
* silent reconciliation of uncertain financial outcomes.

---

# 177. Integration Architecture Invariants

The following invariants apply to External Integration and Webhook Architecture:

1. External providers do not receive direct PostgreSQL access.
2. PostgreSQL remains authoritative for FastFood transactional state.
3. External providers do not directly modify Business state.
4. Provider-specific logic remains inside integration adapters.
5. Domain logic does not depend directly on provider-specific HTTP clients.
6. Internal resource UUIDs are separate from provider resource IDs.
7. Provider IDs are scoped to their integration context.
8. Business integration credentials are isolated by Business.
9. Branch-specific integration state is isolated by Branch.
10. Integration configuration requires authorization.
11. Integration secrets are stored securely.
12. Integration secrets are not returned to ordinary frontend clients.
13. Integration secrets are never logged.
14. Production credentials are isolated from development credentials.
15. Sandbox and production environments remain separated.
16. Integration activation requires validation.
17. Integration state is explicit.
18. Outbound state-changing operations use idempotency where supported.
19. Internal idempotency and provider idempotency remain separate concerns.
20. Outbound integration events have unique internal identity.
21. Important outbound events use durable Outbox processing.
22. External calls do not unnecessarily block core transactions.
23. External calls have bounded timeouts.
24. External retries are bounded.
25. External retries use backoff where appropriate.
26. External retry loops are never unlimited.
27. External rate limits are respected.
28. Provider failures are isolated from unrelated POS operations.
29. Circuit protection may reduce unnecessary provider traffic.
30. Circuit protection does not replace Business correctness.
31. Unknown provider outcomes are not automatically treated as failure.
32. Unknown provider outcomes are reconciled where required.
33. Provider responses are treated as untrusted input.
34. Provider response schemas are validated.
35. Provider amounts are validated against expected Business values.
36. Provider currency is validated.
37. Provider statuses are mapped explicitly.
38. Unknown provider statuses are not assumed successful.
39. Webhooks use HTTPS.
40. Webhooks require provider authentication.
41. Webhook signatures are verified before Business processing.
42. Webhook raw payload is preserved when required for signature verification.
43. Webhook signatures use secure comparison.
44. Webhook timestamps are validated where provided.
45. Webhook replay protection is implemented where duplicate effects are possible.
46. Provider event IDs are stored where available.
47. Duplicate webhook events do not duplicate Business effects.
48. Webhook events are persisted safely before acknowledgement where required.
49. Webhook processing is normally asynchronous after safe persistence.
50. Webhook endpoint processing is bounded.
51. Webhook retries are separate from internal processing retries.
52. Webhook events may arrive out of order.
53. Webhook processing does not assume ordering unless guaranteed.
54. Unknown webhook events are handled safely.
55. Malformed webhook events are rejected.
56. Webhook secrets are never logged.
57. Webhook payloads are validated before Business processing.
58. Webhook processing cannot bypass authorization.
59. Webhook processing cannot bypass subscription restrictions.
60. Webhook processing cannot resurrect deleted Business state.
61. Payment provider operations have explicit internal and external identities.
62. Payment provider uncertain outcomes require reconciliation.
63. Refund provider operations are idempotent.
64. Notification provider failures do not rollback core Business transactions.
65. Storage provider paths are not exposed as authoritative File identifiers.
66. Signed download URLs are bounded and scoped.
67. Signed upload URLs are authorization-controlled.
68. Storage provider events use webhook security rules.
69. OAuth callbacks validate state and integration context.
70. OAuth credentials are stored securely.
71. External URLs are validated against SSRF risks.
72. External redirects are controlled.
73. Integration workers do not have unnecessary internal network access.
74. External provider responses cannot directly override internal state.
75. Integration configuration changes use concurrency protection.
76. Integration configuration history is preserved where required.
77. Integration Jobs revalidate important Business state before execution.
78. Integration Jobs respect subscription entitlement.
79. Integration Jobs stop for deleted Business state.
80. Integration queues are bounded.
81. Integration concurrency is bounded.
82. Reconciliation Jobs are bounded and idempotent.
83. Reconciliation decisions are auditable.
84. Manual reconciliation requires authorization.
85. Manual reconciliation does not rewrite original historical state.
86. Provider downtime causes controlled degradation.
87. Provider downtime does not unnecessarily disable unrelated POS operations.
88. Offline POS does not depend on real-time external provider availability.
89. Offline-created transactions do not claim unverified external success.
90. External integrations remain compatible with offline synchronization.
91. Integration failures are observable.
92. Integration metrics use low-cardinality labels.
93. Integration logs exclude secrets.
94. Integration logs preserve useful correlation context.
95. Important integration events are auditable.
96. Audit records do not contain provider secrets.
97. Raw provider payload retention is bounded.
98. Sensitive external payloads are protected at rest.
99. Provider schema changes are isolated by adapter boundaries.
100. Provider API versions are explicitly tracked where relevant.
101. Integration capability support is explicit.
102. Unsupported provider capabilities are rejected safely.
103. Integration health is observable.
104. Provider health checks are bounded.
105. Integration configuration tests do not create unintended financial effects.
106. Production provider credentials are never used in automated tests.
107. Sandbox environments are used where available.
108. Failure injection is performed for critical integrations.
109. Security testing covers webhook verification.
110. Security testing covers replay protection.
111. Security testing covers cross-Business integration isolation.
112. Security testing covers cross-Branch integration isolation.
113. Security testing covers credential leakage.
114. Security testing covers SSRF protection.
115. Integration API errors use stable internal classifications.
116. Raw provider errors are not blindly exposed to clients.
117. Integration state remains distinguishable from Business domain state.
118. Current provider configuration does not rewrite historical transactions.
119. Historical payment state remains protected.
120. Historical Order prices remain protected.
121. Historical refund state remains protected.
122. Historical integration mappings remain recoverable where required.
123. Business subscription restrictions apply to integrations.
124. READ_ONLY Business state blocks prohibited integration mutations.
125. DELETED Business state cannot be resurrected by provider events.
126. Credential revocation stops future outbound usage.
127. Credential rotation is auditable.
128. Webhook secret rotation is supported where required.
129. Emergency integration disablement is supported.
130. Integration compromise can be isolated without disabling unrelated Business operations.
131. External integrations do not become a hidden source of Business authority.
132. Provider IDs never replace internal resource identity.
133. External event IDs are not treated as authorization credentials.
134. Provider response success does not automatically mean Business success.
135. Business rules remain authoritative over external responses.
136. Financial reconciliation preserves original state and decision history.
137. External operations remain traceable through available correlation identifiers.
138. Integration processing remains compatible with horizontal scaling.
139. Integration state survives application restart according to retention requirements.
140. Redis is not the sole authoritative record of an integration operation.
141. Temporary queue state is not the sole record of important external events.
142. Outbox events survive transient worker failures.
143. Webhook events survive transient worker failures.
144. Integration recovery is observable.
145. Provider recovery does not cause uncontrolled request storms.
146. Backpressure protects the system from provider degradation.
147. Integration processing must not starve critical POS workloads.
148. Integration SLOs are measurable.
149. Integration security controls remain within defined performance targets.
150. External integration architecture preserves Business and Branch isolation.
151. External integration architecture preserves historical integrity.
152. External integration architecture preserves financial correctness.
153. External integration architecture preserves offline correctness.
154. External integration architecture preserves auditability.
155. External integration architecture preserves API contract stability.
156. External integration architecture does not expose provider-specific schemas unnecessarily.
157. External integration architecture supports controlled provider replacement.
158. External integration architecture supports multiple providers where justified.
159. Simplicity is preferred when equivalent integration safety can be achieved.
160. External integrations must remain subordinate to FastFood ERP Business authority.

---

# 178. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/06_Authentication_and_Trusted_Devices.md`
* `docs/02_System_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/02_System_Analysis/08_POS_and_Order_Management.md`
* `docs/02_System_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/02_System_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Backend Architecture

* `docs/04_Architecture/06_Backend/09_Events_Outbox_and_Background_Jobs.md`
* `docs/04_Architecture/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/04_Architecture/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/06_Backend/15_Backend_File_Storage_and_Document_Management.md`
* `docs/04_Architecture/06_Backend/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/06_Backend/20_Backend_Operations_and_Incident_Management_Architecture.md`
* `docs/04_Architecture/06_Backend/22_Backend_Data_Consistency_and_Reconciliation_Architecture.md`
* `docs/04_Architecture/06_Backend/25_Backend_Queue_and_Worker_Architecture.md`

### Database

* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/25_Database_Integrity_and_Constraints.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### API Architecture

* `docs/04_Architecture/09_API/01_API_Architecture_Overview.md`
* `docs/04_Architecture/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/04_Architecture/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/04_Architecture/09_API/09_API_Error_Handling_and_Error_Codes.md`
* `docs/04_Architecture/09_API/10_API_Idempotency_and_Concurrency.md`
* `docs/04_Architecture/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/04_Architecture/09_API/20_API_Async_Jobs_Bulk_and_Batch_Operations.md`
* `docs/04_Architecture/09_API/21_API_Security_CORS_CSRF_and_Data_Protection.md`
* `docs/04_Architecture/09_API/23_API_OpenAPI_Contract_Testing_and_Documentation.md`
* `docs/04_Architecture/09_API/24_API_Performance_Observability_and_SLO.md`

---

# 179. Status

**API Architecture Section:** In Progress.

**Document Status:** Proposed.

**Current Document:** `22_API_External_Integration_and_Webhook_Architecture.md`

**Previous Document:** `21_API_Security_CORS_CSRF_and_Data_Protection.md`

**Next Document:** `23_API_OpenAPI_Contract_Testing_and_Documentation.md`

---

## Final Principle

> External integrations must remain controlled adapters around FastFood ERP, not alternative sources of Business authority. Every outbound request and inbound webhook must be authenticated, bounded, observable and retry-safe, while uncertain external outcomes must be reconciled without compromising financial correctness, historical integrity, Business isolation or POS availability.

