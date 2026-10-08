# Frontend Deployment and Static Asset Delivery

**Document ID:** DEP-11
**Status:** Proposed
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/10_Deployment/README.md`
**Previous Document:** `docs/10_Deployment/10_Backend_API_Deployment_and_Runtime.md`
**Next Document:** `docs/10_Deployment/12_Background_Workers_and_Scheduler_Deployment.md`

---

## 1. Purpose

This document defines the deployment and static asset delivery architecture for the FastFood ERP frontend.

The frontend deployment architecture must:

* produce reproducible production artifacts;
* deliver the application efficiently to browsers and POS devices;
* support ordinary branch computers;
* preserve offline-capable functionality;
* use safe browser and CDN/proxy caching;
* prevent stale application versions from causing inconsistent behavior;
* support controlled releases;
* support rollback;
* isolate environments;
* avoid exposing secrets through frontend artifacts;
* remain compatible with the Backend API deployment architecture.

The frontend is treated as a deployable static application artifact rather than a server-authoritative Business data store.

---

# 2. Scope

This document covers:

* frontend build;
* production artifact generation;
* build reproducibility;
* environment configuration;
* static asset structure;
* HTML shell delivery;
* JavaScript and CSS delivery;
* image and font delivery;
* cache headers;
* browser cache;
* CDN;
* reverse proxy;
* cache invalidation;
* asset versioning;
* content hashing;
* service worker deployment;
* offline/PWA considerations;
* static storage;
* deployment atomicity;
* rolling frontend releases;
* frontend rollback;
* release compatibility;
* API compatibility;
* security;
* source maps;
* monitoring;
* frontend delivery SLOs;
* failure handling;
* runtime testing;
* deployment guardrails;
* frontend deployment invariants.

---

# 3. Deployment Position

The frontend is delivered independently from the Backend API runtime.

```text
Browser / POS Device
        ↓
DNS / TLS
        ↓
CDN / Reverse Proxy
        ↓
Frontend Static Assets
        ↓
Browser Application
        ↓
Backend API
```

The Backend API remains a separate runtime.

The frontend must not directly connect to PostgreSQL, Redis or other internal infrastructure.

---

# 4. Frontend Deployment Principles

The deployment follows these principles:

1. Frontend artifacts are immutable after publication.
2. A frontend deployment produces a uniquely identifiable release.
3. Build output must be reproducible.
4. Environment-specific configuration must be controlled.
5. Frontend artifacts must contain no secrets.
6. Hashed assets should be cacheable for long periods.
7. The HTML entry point must allow controlled version discovery.
8. Browser caching must not permanently pin an obsolete application shell.
9. Service worker caching must not become Business data authority.
10. Offline data remains governed by the frontend offline architecture.
11. CDN usage is an optimization layer.
12. Reverse proxy caching is an optimization layer.
13. PostgreSQL remains authoritative.
14. API authorization remains server-side.
15. Frontend deployment must remain compatible with supported API versions.
16. Rollback must be possible without rewriting Business data.
17. Static asset deployment must not depend on mutable shared application state.
18. Failed frontend deployment must not corrupt the previous release.
19. Security must not be weakened for caching performance.
20. Simplicity is preferred when multiple delivery strategies provide equivalent safety.

---

# 5. Frontend Application Model

The frontend is a browser-delivered application.

Production deployment generally consists of:

```text
HTML Shell
+
JavaScript Bundles
+
CSS Bundles
+
Images
+
Fonts
+
Static Metadata
+
Optional Service Worker
```

The exact framework and bundler are implementation details.

The deployment architecture must remain independent of a specific frontend framework.

---

# 6. Build Output

A successful production build should produce a versioned artifact such as:

```text
dist/
├── index.html
├── assets/
│   ├── app.<hash>.js
│   ├── vendor.<hash>.js
│   ├── app.<hash>.css
│   ├── logo.<hash>.svg
│   └── ...
├── manifest.webmanifest
└── sw.js
```

The exact file layout may differ.

The important property is that release assets are uniquely identifiable and immutable.

---

# 7. Build Environment

Production builds should run in a controlled build environment.

The build environment must define:

* runtime version;
* package manager version;
* dependency versions;
* build command;
* environment inputs;
* artifact output;
* build metadata.

The production server should normally serve a prebuilt artifact rather than compiling frontend source at request time.

---

# 8. Build Reproducibility

A frontend release should be reproducible from:

```text
Source Commit
+
Dependency Lock
+
Build Tool Version
+
Build Configuration
+
Approved Public Runtime Configuration
```

Two builds from the same controlled inputs should produce equivalent application behavior.

---

# 9. Dependency Locking

Frontend dependencies must use a controlled lock file.

Dependency installation in production should not silently resolve arbitrary new versions.

Dependency changes must be reviewable.

---

# 10. Build Validation

A production frontend build must fail when:

* dependencies cannot be resolved;
* required build configuration is missing;
* TypeScript/type validation fails where applicable;
* linting or static checks fail where configured;
* asset generation fails;
* required environment values are invalid;
* output integrity checks fail.

A partially generated artifact must not be published as a release.

---

# 11. Build Artifact Identity

Every frontend artifact should have a release identity.

Recommended metadata:

```text
Release ID
Build ID
Source Commit
Build Timestamp
Frontend Version
```

The artifact identity must be traceable to the source revision that produced it.

---

# 12. Artifact Immutability

Once a release artifact is published, the files belonging to that release should not be modified in place.

Incorrect:

```text
release-v10/
    app.js

later:
    app.js replaced with different content
```

Preferred:

```text
release-v10/
release-v11/
release-v12/
```

Each release remains identifiable.

---

# 13. Release Directory Strategy

A deployment may use release directories:

```text
frontend/
├── releases/
│   ├── release-001/
│   ├── release-002/
│   └── release-003/
│
└── current -> releases/release-003
```

The exact filesystem strategy is implementation-specific.

The important property is atomic activation and safe rollback.

---

# 14. Atomic Frontend Activation

The new frontend should become active through a controlled atomic switch where possible.

Conceptually:

```text
Current
  ↓
Prepare New Release
  ↓
Validate
  ↓
Switch Active Release
  ↓
Verify
```

The previous release should remain available until the new release is accepted.

---

# 15. Frontend Environment Separation

Separate deployment environments must use separate frontend artifacts or controlled environment configuration.

At minimum:

```text
Development
Test
Staging
Production
```

must not accidentally share:

* API credentials;
* API endpoints;
* analytics configuration;
* service worker scope;
* deployment storage.

---

# 16. Environment Configuration

Frontend configuration falls into two categories:

### Build-Time Public Configuration

Examples:

* API base URL;
* public application identifier;
* public feature configuration;
* public telemetry endpoint.

### Runtime Public Configuration

Where practical, selected public configuration may be injected at runtime so the same artifact can be promoted between environments.

No secret value belongs in either category.

---

# 17. Frontend Secrets

Frontend code is delivered to the browser.

Therefore anything included in:

* JavaScript;
* HTML;
* CSS;
* source maps;
* public runtime configuration;

must be considered observable by the client.

The frontend must never contain:

* database passwords;
* Redis credentials;
* private API keys;
* signing private keys;
* secret tokens;
* server credentials.

---

# 18. Public Configuration Principle

A value placed in frontend configuration must be considered public.

For example:

```text
PUBLIC_API_URL
```

is acceptable as public configuration.

A database password is not.

Frontend deployment must never rely on client-side secrecy.

---

# 19. API Endpoint Configuration

The frontend should use a controlled API base URL.

Conceptually:

```text
/api/v1
```

or an approved public API origin.

The frontend must not contain internal database or infrastructure addresses.

---

# 20. API Compatibility

A frontend release must identify the API compatibility expectations.

Conceptually:

```text
Frontend Release
        ↓
Supported API Contract
```

A frontend deployment must not assume that a breaking backend API change can be deployed independently.

---

# 21. API Version Compatibility

During controlled deployment, the frontend should remain compatible with the supported backend API version.

Where multiple backend versions temporarily coexist, frontend requests must remain valid across the supported transition period.

---

# 22. Static Asset Categories

Static assets may include:

```text
HTML
JavaScript
CSS
SVG
PNG
WebP
JPEG
Fonts
Web Manifest
Service Worker
```

Each category may use different caching rules.

---

# 23. HTML Shell

The HTML entry point is the application shell.

It is responsible for loading:

* CSS;
* JavaScript;
* application metadata;
* manifest where applicable;
* service worker registration where applicable.

The shell should remain lightweight.

---

# 24. HTML Cache Strategy

The HTML shell should use a short or revalidation-based caching strategy.

Preferred behavior:

```text
HTML
→ no-cache / must-revalidate
```

or another controlled strategy that allows clients to discover a newer release.

The HTML shell should not be cached indefinitely under a stable URL.

---

# 25. Hashed JavaScript Assets

JavaScript bundles should use content-based or release-specific hashes.

Example:

```text
app.8f1c21.js
```

When content changes:

```text
app.5ac901.js
```

The new filename allows long-lived caching without ambiguity.

---

# 26. Hashed CSS Assets

CSS assets should use the same immutable asset principle.

Example:

```text
app.12c92e.css
```

Changed content produces a new filename.

---

# 27. Static Asset Cache Strategy

Immutable hashed assets may use long cache lifetimes.

Typical strategy:

```text
Cache-Control:
public, max-age=31536000, immutable
```

The exact header may vary by asset type and deployment environment.

Only assets that are genuinely immutable should use this policy.

---

# 28. Non-Hashed Assets

Non-hashed mutable assets should use shorter caching or explicit revalidation.

Examples:

* `index.html`;
* runtime configuration;
* certain metadata files;
* service worker entry.

A mutable file must not be treated as permanently immutable.

---

# 29. Manifest Strategy

If a Web App Manifest is used:

* changes must be version-controlled;
* deployment behavior must be predictable;
* caching must not permanently pin incompatible metadata.

The manifest must not contain secrets.

---

# 30. Service Worker

If the frontend uses a service worker for offline functionality, the service worker becomes part of the deployment artifact.

The service worker must be:

* versioned;
* tested;
* deployed deliberately;
* monitored for update behavior.

---

# 31. Service Worker Authority

The service worker is not an authoritative Business data layer.

It must not become the authority for:

* payments;
* inventory;
* Cash Sessions;
* historical transactions;
* Business configuration;
* synchronization results.

Those remain governed by application and server architecture.

---

# 32. Service Worker Versioning

A new frontend release that changes service-worker-controlled behavior must produce a new service worker version.

Conceptually:

```text
Frontend Release 10
        ↓
Service Worker 10

Frontend Release 11
        ↓
Service Worker 11
```

The service worker must not continue serving incompatible application code indefinitely.

---

# 33. Service Worker Update Strategy

The update process should support:

```text
New Release Available
        ↓
Browser Detects New Worker
        ↓
Install New Worker
        ↓
Validate New Assets
        ↓
Activate According to Update Policy
        ↓
New Application Version
```

The exact activation behavior must be tested carefully for POS continuity.

---

# 34. Service Worker and Active POS Session

An update must not unexpectedly interrupt an active POS workflow.

The frontend should avoid automatically replacing the running application at a moment that could discard unsaved Order state.

A controlled update strategy must be used.

---

# 35. Offline Cache

Offline-capable data may be stored locally according to the frontend offline architecture.

Examples:

* authorized menu;
* product configuration;
* local application resources;
* pending synchronization data.

Local data must remain subject to:

* offline authorization;
* expiration;
* encryption;
* synchronization rules.

---

# 36. Offline Business Data

Offline storage may contain temporary or authorized Business information.

It must not be treated as a server-authoritative permanent copy.

After synchronization:

```text
Server
→ authoritative

Local
→ synchronized client state
```

---

# 37. Browser Storage and Static Caching

Browser HTTP cache and application local storage have different roles.

```text
HTTP Cache
→ static asset performance

IndexedDB / Local Storage where approved
→ application/offline state
```

They must not be mixed conceptually.

---

# 38. IndexedDB / Offline Storage

Where IndexedDB is used:

* schema versions must be controlled;
* migrations must be tested;
* stale records must be handled;
* storage size must be bounded where practical.

Static asset caching must not be used as a substitute for structured offline storage.

---

# 39. Static Asset Delivery

Static assets may be delivered through:

```text
Option A:
Browser
  ↓
Nginx
  ↓
Static Files

Option B:
Browser
  ↓
CDN
  ↓
Static Storage
```

Both are valid depending on deployment scale.

---

# 40. Nginx Static Delivery

Initial small deployments may use Nginx to serve static files directly.

Advantages:

* simple;
* low overhead;
* local network proximity to API host;
* easy deployment.

Static files should be served without passing through Flask.

---

# 41. CDN

A CDN may be introduced when measured traffic or geographic distribution justifies it.

The CDN should remain:

* non-authoritative;
* replaceable;
* compatible with hashed assets;
* isolated per environment.

---

# 42. CDN Authority

The CDN must never become the source of truth for frontend release identity.

The release artifact remains authoritative.

The CDN is a delivery/cache layer.

---

# 43. CDN Cache Key

CDN cache keys should consider:

* hostname;
* path;
* query string behavior where relevant;
* content variant where applicable.

Cache configuration must not allow one environment to serve assets from another environment.

---

# 44. Environment Isolation

The following must not share static asset namespaces accidentally:

```text
Production
Staging
Test
Development
```

A production browser must never receive staging assets because of cache collision.

---

# 45. CDN Cache Invalidation

Hashed assets reduce the need for expensive CDN purges.

Preferred:

```text
New Content
→ New Hash
→ New URL
```

This allows old assets to remain cached safely.

---

# 46. Mutable Asset Invalidation

For mutable files such as the HTML shell:

```text
Release
 ↓
Publish New HTML
 ↓
Invalidate / Revalidate
 ↓
Clients Discover New Asset URLs
```

The invalidation mechanism must be verified before release completion.

---

# 47. Cache Purge Failure

If a CDN purge fails:

* immutable old assets remain safe;
* the deployment should not assume clients immediately see the new HTML;
* monitoring must detect stale shell delivery;
* retry should occur where appropriate.

The release must not delete old assets prematurely.

---

# 48. Static Asset Availability

Static asset infrastructure should remain available independently from Backend API health where practical.

A temporary API failure should not prevent a browser from loading the frontend shell.

---

# 49. API Unavailability After Frontend Load

The frontend must handle Backend API unavailability gracefully.

The static application may load successfully while API operations remain temporarily unavailable.

The frontend should present appropriate operational state according to frontend architecture.

---

# 50. Static Server Failure

If the static delivery server fails:

```text
Single Static Server
→ Frontend unavailable until recovery

CDN / Redundant Delivery
→ Traffic may continue through healthy delivery path
```

The architecture should not claim high availability when only one static host exists.

---

# 51. Compression

Static text assets such as:

* JavaScript;
* CSS;
* HTML;
* SVG;

should use modern compression where supported.

Examples:

```text
Brotli
Gzip
```

The deployment may precompress assets when operationally useful.

---

# 52. Compression and CPU

Compression improves network performance but consumes CPU.

For immutable static assets, precompression or CDN edge compression may reduce repeated server-side CPU cost.

---

# 53. Image Optimization

Images should be optimized during build where practical.

The build process may generate:

* WebP;
* optimized PNG;
* optimized JPEG;
* responsive image variants.

The exact format depends on browser support and application requirements.

---

# 54. Image Caching

Hashed image assets may use long-lived immutable cache headers.

User-uploaded Business assets should use the dedicated file-storage architecture rather than being mixed with frontend build artifacts.

---

# 55. User-Uploaded Files

Business/user files must not be embedded permanently into the frontend deployment artifact.

Example:

```text
Frontend Build
≠
Business Upload Storage
```

This allows Business data and frontend releases to remain independently recoverable.

---

# 56. Font Delivery

Fonts should be:

* versioned;
* cacheable;
* limited to required families/weights;
* delivered through approved static infrastructure.

Unused fonts should not be included unnecessarily.

---

# 57. Cache-Control for Sensitive Data

Dynamic API responses and sensitive Business data must not be confused with static assets.

Static asset caching must never cause:

* one Business's API response to appear to another Business;
* authenticated API data to become public cache data.

---

# 58. API vs Static Cache Boundary

The delivery architecture must distinguish:

```text
Static:
app.js
app.css
logo.svg

Dynamic:
GET /api/v1/orders
GET /api/v1/inventory
```

Static CDN caching and API response caching follow different policies.

---

# 59. Frontend Authentication Boundary

Frontend deployment does not provide authorization.

A hidden page or disabled button is not a security mechanism.

The Backend API remains authoritative for:

* authentication;
* authorization;
* Business scope;
* Branch scope;
* subscription state.

---

# 60. Route Protection

Frontend routes may use client-side route guards for user experience.

However:

```text
Frontend Route Guard
≠
Server Authorization
```

Every protected API operation must still be authorized by the server.

---

# 61. Runtime Configuration Security

Public runtime configuration may be loaded from a generated file such as:

```text
/config.js
```

or equivalent.

The configuration must contain only non-secret values.

---

# 62. Runtime Configuration Cache

If runtime configuration is mutable:

* it must not be cached indefinitely;
* clients must be able to discover changes;
* the file must be versioned or revalidated as appropriate.

---

# 63. Runtime Configuration and Promotion

Where the same frontend artifact is promoted across environments, environment-specific public values may be injected at deployment time.

The system should avoid unnecessary rebuilds solely to change public environment endpoints where runtime injection is safe.

---

# 64. Frontend Release Compatibility

A frontend release must be tested against:

* current supported API version;
* expected authentication flow;
* offline synchronization protocol;
* supported Business configuration;
* required browser behavior.

---

# 65. Backend-Frontend Release Ordering

Release ordering must prevent an incompatible client/server combination.

When a change is backward compatible:

```text
Deploy Backend
   ↓
Deploy Frontend
```

may be safe.

For a breaking transition:

```text
Deploy Compatibility Layer
   ↓
Deploy Frontend
   ↓
Remove Legacy Backend Behavior
```

must be used.

The exact sequence depends on the change.

---

# 66. Frontend Rollout Strategy

For a simple static deployment:

```text
Build
 ↓
Validate
 ↓
Publish
 ↓
Switch Active Release
 ↓
Revalidate HTML
 ↓
Smoke Test
```

For CDN-backed deployment:

```text
Build
 ↓
Upload Immutable Assets
 ↓
Publish HTML
 ↓
Purge/Revalidate Mutable Shell
 ↓
Smoke Test
```

---

# 67. Pre-Publication Validation

Before making a new release active:

* all expected assets exist;
* HTML references existing hashed assets;
* manifest is valid where used;
* service worker is valid where used;
* asset hashes are correct;
* API endpoint configuration is correct;
* release metadata is present.

---

# 68. Broken Asset Prevention

The deployment must prevent:

```text
index.html
references app-v11.js

but CDN/static storage
contains only app-v10.js
```

All referenced immutable assets must be published before the new HTML becomes active.

---

# 69. Publish Order

The preferred publish sequence is:

```text
1. Build artifact
2. Validate artifact
3. Publish immutable assets
4. Verify asset availability
5. Publish/update HTML shell
6. Invalidate or revalidate HTML cache
7. Run smoke tests
8. Mark release active
```

Old immutable assets should remain available during the transition.

---

# 70. Rollback Order

Rollback should reverse the active shell rather than deleting historical assets.

```text
Current Release
   ↓
Mark Previous Release Active
   ↓
Invalidate/Revalidate HTML
   ↓
Verify
```

Old assets may remain cached and do not need to be deleted immediately.

---

# 71. Rollback Safety

Frontend rollback must not attempt to:

* modify Business data;
* undo API transactions;
* delete offline transaction queues;
* rewrite Orders;
* alter inventory history.

Frontend rollback is an application delivery operation only.

---

# 72. Service Worker Rollback

Service worker rollback requires additional care.

A browser may already have installed a newer service worker.

Therefore rollback must include:

* compatible worker behavior;
* tested update path;
* asset availability for the rollback release;
* controlled activation.

Simply changing the HTML file may not fully rollback client-side execution when a service worker controls the page.

---

# 73. Old Asset Retention

Previous releases should remain available for a controlled retention period.

This protects:

* cached HTML;
* active service workers;
* slow clients;
* rollback;
* browser tabs running older release versions.

---

# 74. Asset Garbage Collection

Old frontend release assets may be cleaned after the retention period.

Cleanup must consider:

* rollback window;
* service worker versions;
* browser cache behavior;
* CDN cache lifetime;
* deployment history.

Assets must not be deleted immediately after every release.

---

# 75. Frontend Release Retention

The deployment system should retain enough previous releases to support the defined rollback policy.

The exact number or duration is an operational configuration.

---

# 76. Cache Poisoning Protection

The deployment must prevent arbitrary clients from replacing static assets in shared caches.

Static storage and CDN origins must be write-protected.

Only the deployment system may publish production artifacts.

---

# 77. Cache Header Validation

Automated deployment tests should verify important headers such as:

```text
Cache-Control
Content-Type
ETag
Last-Modified
Content-Encoding
```

where applicable.

---

# 78. MIME Type Correctness

Static assets must be served with correct content types.

Examples:

```text
text/html
text/css
application/javascript
image/svg+xml
image/webp
font/woff2
```

Incorrect MIME types may cause browser failures.

---

# 79. Content Integrity

Where appropriate, deployment may use:

* content hashes;
* integrity metadata;
* release checksums.

The deployment pipeline must verify that published assets match the generated artifact.

---

# 80. Subresource Integrity

Subresource Integrity may be used for suitable externally hosted immutable assets.

The frontend must not rely on untrusted third-party JavaScript without explicit review.

---

# 81. Third-Party Assets

Third-party frontend assets should be minimized.

For external resources:

* origin must be known;
* availability must be considered;
* security impact must be reviewed;
* fallback should exist where practical.

A third-party asset failure must not unnecessarily prevent core ERP usage.

---

# 82. Source Maps

Source maps may be generated for debugging.

Production source maps should not automatically be exposed publicly when they reveal:

* internal source structure;
* sensitive implementation details;
* unnecessary application internals.

Preferred approach:

```text
Build
 ↓
Source Map
 ↓
Protected Error/Debug Storage
```

---

# 83. Build Artifact Security

Build artifacts must be checked for accidental inclusion of:

* secrets;
* `.env` files;
* private certificates;
* credentials;
* internal URLs;
* development-only debug code.

Artifact scanning should be part of CI/CD.

---

# 84. Development Code Exclusion

Production builds must exclude development-only behavior such as:

* debug consoles;
* mock data;
* development API endpoints;
* local test credentials;
* test-only routes.

---

# 85. Browser Compatibility

The frontend deployment must define supported browser versions.

Build targets and asset transpilation must match those supported environments.

Unsupported browsers should fail gracefully rather than silently corrupting data.

---

# 86. POS Hardware Compatibility

Frontend deployment should account for ordinary branch hardware.

The application should remain usable on supported POS/office computers without requiring unusually powerful hardware.

Heavy browser workloads should be minimized.

---

# 87. Initial Frontend Delivery Performance Targets

Initial deployment targets:

| Metric                                             |          Target |
| -------------------------------------------------- | --------------: |
| Static asset request p95 from delivery layer       |        ≤ 200 ms |
| HTML shell request p95 from delivery layer         |        ≤ 300 ms |
| Initial application boot on supported POS hardware |         ≤ 2.5 s |
| Static delivery availability                       | ≥ 99.9% monthly |
| Critical asset failure rate                        |          < 0.1% |

These targets must be measured under representative production conditions.

Client-side Internet conditions are outside the server-only latency measurement boundary.

---

# 88. Performance Monitoring

The deployment should monitor:

* HTML response latency;
* JavaScript asset latency;
* CSS asset latency;
* image latency;
* cache hit rate;
* cache miss rate;
* asset error rate;
* asset 404 rate;
* frontend release adoption;
* service worker update success where applicable.

---

# 89. Cache Hit Rate

Cache hit rate is useful but not the primary correctness metric.

A high cache hit rate is not acceptable if:

* obsolete HTML is served indefinitely;
* incompatible assets are referenced;
* environment isolation is broken;
* Business data is exposed.

---

# 90. Asset 404 Monitoring

Asset 404 rates should be monitored after each release.

A sudden increase often indicates:

* broken asset references;
* incomplete publication;
* premature cleanup;
* CDN propagation issue;
* incorrect HTML caching.

---

# 91. Release Adoption Monitoring

The deployment may monitor which frontend release versions are active.

This helps identify:

* clients remaining on old releases;
* service worker update problems;
* cache persistence problems;
* incomplete rollback.

---

# 92. Frontend Health Verification

Static deployment health checks should verify:

```text
HTML available
JavaScript entry available
CSS entry available
Manifest valid where applicable
Service Worker available where applicable
API configuration correct
Release ID correct
```

---

# 93. Frontend Smoke Tests

Post-deployment smoke tests should verify:

* application shell loads;
* JavaScript initializes;
* CSS loads;
* API endpoint is reachable;
* authentication page works;
* authenticated navigation works;
* Branch selection works;
* POS entry point loads.

Tests must use safe operations.

---

# 94. Offline Smoke Tests

When offline functionality is part of the release, deployment tests should also verify:

* application can load from approved local assets;
* authorized offline state remains available;
* local queue remains intact;
* service worker update does not delete valid pending transactions;
* synchronization can resume after connectivity returns.

---

# 95. Service Worker Update Testing

Every service-worker-affecting release should test:

```text
Old Version
 ↓
New Version Available
 ↓
New Worker Installation
 ↓
Activation
 ↓
Application Reload
 ↓
Offline Behavior
```

The test must include an interrupted or delayed update scenario.

---

# 96. Frontend Deployment Failure

If validation fails:

```text
Build Failure
   ↓
Do Not Publish Active Release
```

If publication fails:

```text
Partial Publication
   ↓
Keep Previous Release Active
```

A failed release must not replace a healthy release with an incomplete artifact.

---

# 97. CDN Failure

If CDN delivery fails:

* fallback to origin may be used where supported;
* static files remain available from the origin;
* API availability remains independent where possible.

The exact failover behavior depends on deployment topology.

---

# 98. Origin Failure

If the static origin is unavailable and no CDN redundancy exists:

* frontend delivery fails;
* Backend API may remain operational;
* users may receive cached assets only if the cache remains valid.

The architecture must not claim full frontend HA without redundant delivery infrastructure.

---

# 99. Stale HTML

If stale HTML is detected:

1. Verify cache headers.
2. Verify active release.
3. Verify CDN revalidation.
4. Verify service worker behavior.
5. Restore correct shell delivery.
6. Keep old immutable assets available.

Stale HTML must not result in deleting assets required by older clients.

---

# 100. Incomplete Asset Publication

If HTML references unavailable assets:

```text
Release must be marked failed
```

The previous release should remain active until the asset publication is complete.

---

# 101. Release Concurrency

Two frontend deployments must not modify the same active-release pointer concurrently without coordination.

Deployment tooling must prevent:

```text
Release A activating
and
Release B activating
```

without deterministic ordering.

---

# 102. Deployment Idempotency

Repeated deployment attempts for the same release must not create inconsistent state.

For example:

```text
Deploy Release 18
Retry Deploy Release 18
```

must result in one coherent Release 18 state.

---

# 103. Release Identity Collision

Two different frontend artifacts must never use the same release identity.

Release identifiers must be unique.

---

# 104. Frontend Release Metadata

The deployment may expose a safe release identifier to authorized operational tooling.

Example:

```text
Frontend Release:
2026.10.08-abc123
```

The exact format is implementation-specific.

---

# 105. Browser Cache and Rollback

Rollback must account for clients that still hold:

```text
HTML from Release N
Assets from Release N
Service Worker from Release N
```

Old releases must remain compatible for the defined transition period.

---

# 106. Multi-Version Browser Clients

Different users may temporarily run different frontend releases.

The backend must continue serving supported API contracts during the compatibility window.

Frontend release management must therefore be coordinated with API release management.

---

# 107. Frontend Deployment and Offline Clients

A POS device may remain offline for an extended period.

The deployment must not assume that every device immediately receives the newest frontend artifact.

Offline-compatible local state must remain usable according to the offline authorization policy.

---

# 108. Offline Release Update

When an offline POS device reconnects:

```text
Reconnect
 ↓
Check Frontend Release
 ↓
Validate Update Compatibility
 ↓
Download New Assets
 ↓
Preserve Pending Local Transactions
 ↓
Update Application
```

Pending synchronization data must never be deleted merely because a frontend release changed.

---

# 109. Frontend Update and Sync Queue

The frontend must treat the local synchronization queue as durable application state.

A frontend deployment must not:

* clear the queue;
* overwrite pending operations;
* change operation UUIDs;
* change transaction identity;
* discard unsynchronized Business operations.

---

# 110. Browser Storage Migration

If a frontend release changes local storage schema:

* migration must be versioned;
* migration must preserve valid pending transactions;
* failure must be recoverable;
* old state must not be silently discarded.

Storage migration is separate from static asset caching.

---

# 111. Offline Authorization and Frontend Release

A frontend update must not extend offline authorization lifetime.

Offline authorization remains governed by the security architecture.

Updating JavaScript or cached assets must not create additional authorization privileges.

---

# 112. Subscription State

Frontend caching must not cause an expired Business to retain modification capability.

The backend remains authoritative for:

* subscription entitlement;
* read-only state;
* modification restrictions.

UI state may be stale temporarily, but sensitive operations must be rejected server-side.

---

# 113. Branch Isolation

Frontend assets themselves may be globally shared because they are application code.

Business/Branch data loaded through the application must remain scope-isolated.

Static asset reuse must never imply data reuse.

---

# 114. Business Data and CDN

Business-specific API responses must not be unintentionally cached as public static content.

The CDN should cache frontend assets, not arbitrary authenticated Business responses unless a separate secure API-cache architecture explicitly permits it.

---

# 115. Custom Business Assets

Business-specific assets such as:

* restaurant logo;
* menu images;
* document files;

must use the controlled file/storage architecture.

They should not be baked into the core frontend release unless they are intentionally part of the product artifact.

---

# 116. Deployment Storage

Frontend artifacts may be stored in:

* server filesystem;
* object storage;
* artifact repository;
* CDN origin storage.

The selected storage must support:

* versioned releases;
* controlled access;
* immutable artifacts;
* retention;
* rollback.

---

# 117. Storage Permissions

Frontend release storage must be write-protected.

Only authorized deployment processes should publish production artifacts.

Public clients should have read access only through the intended delivery path.

---

# 118. Deployment Credentials

Deployment credentials must not be embedded in frontend builds.

Frontend artifacts must never contain:

* CDN write credentials;
* storage credentials;
* SSH credentials;
* deployment tokens.

---

# 119. CI/CD Integration

The frontend deployment pipeline should follow:

```text
Source
 ↓
Dependency Install
 ↓
Static Checks
 ↓
Build
 ↓
Artifact Validation
 ↓
Security Scan
 ↓
Publish Immutable Assets
 ↓
Publish HTML
 ↓
Smoke Test
 ↓
Mark Release Active
```

---

# 120. Build-Time Test Gate

The release should not be published if required checks fail.

Potential checks include:

* type checking;
* linting;
* unit tests;
* frontend integration tests;
* build validation;
* dependency audit;
* secret scanning;
* asset integrity.

---

# 121. Deployment Artifact Verification

Before publication, verify:

```text
[ ] Artifact exists
[ ] Release ID valid
[ ] HTML valid
[ ] Asset references valid
[ ] Hashes valid
[ ] No secrets detected
[ ] Public configuration valid
[ ] Service worker valid where used
[ ] Manifest valid where used
```

---

# 122. Staging Verification

The frontend should be deployed to staging before production where the release strategy requires it.

Staging should validate:

* production-like API integration;
* authentication;
* frontend routing;
* asset delivery;
* caching;
* service worker behavior;
* offline operation;
* browser compatibility.

---

# 123. Production Promotion

Production should promote an already validated artifact rather than rebuild from changing inputs at the last moment.

Preferred:

```text
Build Once
   ↓
Validate
   ↓
Promote Same Artifact
```

This improves traceability.

---

# 124. Build Promotion

The same artifact may be promoted:

```text
Test
 ↓
Staging
 ↓
Production
```

when runtime public configuration is injected separately and safely.

---

# 125. Build Rebuild Restriction

Production should not silently rebuild from source while deploying.

A production rebuild may produce a different artifact due to:

* dependency drift;
* build-tool drift;
* environment differences;
* external package changes.

Controlled artifact promotion is preferred.

---

# 126. Rollout Verification

After activation:

```text
HTML
 ↓
Assets
 ↓
Application Boot
 ↓
API Connection
 ↓
Smoke Tests
```

must be verified.

---

# 127. Release Rollback Trigger

Rollback should be considered when:

* HTML is broken;
* critical assets return errors;
* application boot fails;
* authentication flow is broken;
* POS entry point fails;
* service worker update corrupts application behavior;
* critical browser compatibility fails.

---

# 128. Rollback Does Not Undo Business State

Frontend rollback is not a Business rollback.

The system must never assume:

```text
Frontend rollback
→
Order rollback
```

These are independent operations.

---

# 129. Emergency Frontend Rollback

Emergency rollback should:

1. Activate known-good previous release.
2. Revalidate HTML.
3. Verify critical assets.
4. Run smoke tests.
5. Monitor release recovery.
6. Investigate failed release.

Historical frontend artifacts should remain available for investigation.

---

# 130. Operational Cleanup

Old frontend releases may be cleaned after the retention window.

Cleanup must not remove:

* currently active release;
* rollback target;
* assets required by supported service workers;
* assets inside the defined CDN cache safety window.

---

# 131. Frontend Deployment Observability

Deployment monitoring should include:

```text
Release ID
Asset Availability
HTML Availability
Asset 404 Rate
Asset 5xx Rate
Cache Hit Rate
Application Boot Errors
Service Worker Update Errors
Release Adoption
Rollback Events
```

---

# 132. Alerting

Alerts should cover:

* static delivery outage;
* critical asset 404 spike;
* critical asset 5xx spike;
* HTML shell failure;
* release verification failure;
* service worker update failure;
* unusual release adoption behavior.

---

# 133. Performance Regression

Each major frontend release should be compared with the previous baseline for:

```text
Bundle Size
HTML Size
Initial JavaScript
Initial CSS
Application Boot Time
Static Asset Latency
Cache Hit Rate
Browser Error Rate
```

A release that materially degrades POS usability should be investigated.

---

# 134. Bundle Size Control

Production bundles should remain bounded.

The build should avoid unnecessary inclusion of:

* unused libraries;
* duplicate dependencies;
* development tooling;
* large unused images;
* unnecessary localization data.

---

# 135. Code Splitting

Code splitting may be used so that:

* POS-critical code loads first;
* administrative pages load later;
* reports load on demand;
* heavy features do not block initial application boot.

The exact split is determined by frontend architecture.

---

# 136. POS Loading Priority

For FastFood ERP, frontend deployment should prioritize:

```text
Application Shell
   ↓
Authentication
   ↓
POS Core
   ↓
Menu / Order Functions
   ↓
Secondary Management Features
   ↓
Reports / Heavy Features
```

Large management modules should not unnecessarily delay POS startup.

---

# 137. Lazy Loading

Suitable candidates for lazy loading include:

* reports;
* advanced configuration;
* administrative dashboards;
* infrequently used management modules.

Critical POS interactions should remain fast.

---

# 138. Static Asset Prefetching

Prefetching may be used for predictable next-step assets.

However, excessive prefetching must not consume branch network bandwidth unnecessarily.

---

# 139. Network-Constrained Branches

Frontend deployment must account for slow or unstable branch Internet connections.

The architecture should minimize dependence on repeated downloads by using:

* immutable caching;
* offline storage;
* efficient bundles;
* controlled updates.

---

# 140. Deployment and Branch Internet Interruption

If a branch loses connectivity after loading the approved application:

* static application code should remain locally available;
* offline operation may continue within authorization limits;
* pending transactions remain in local storage;
* synchronization resumes later.

---

# 141. Frontend Availability During API Outage

The frontend shell may remain usable when the API is temporarily unavailable.

However, it must not fabricate successful Business operations.

For example:

```text
API unavailable
≠
Payment successful
```

The user interface must accurately distinguish local pending state from server-confirmed state.

---

# 142. Static Delivery Security

Static delivery should use:

* HTTPS;
* correct MIME types;
* controlled origins;
* secure headers;
* write-protected origin storage.

---

# 143. Security Headers

The deployment should apply appropriate frontend security headers according to the frontend architecture.

Potential controls include:

* Content-Security-Policy;
* X-Content-Type-Options;
* Referrer-Policy;
* frame restrictions;
* HSTS.

Exact policies are defined with the security architecture.

---

# 144. Content Security Policy Compatibility

A strict CSP must be compatible with:

* frontend framework;
* service worker;
* API communication;
* required third-party resources.

Unsafe script execution should not be enabled merely for deployment convenience.

---

# 145. CORS Relationship

Frontend static asset delivery and API CORS are separate concerns.

The frontend origin must be included in the Backend API's explicitly allowed origins where cross-origin API access is required.

---

# 146. Service Worker Scope Security

Service workers must use a narrowly controlled scope.

A service worker must not unintentionally control unrelated origins or application areas.

---

# 147. Cache Namespace Isolation

Static cache namespaces must distinguish environments.

Examples:

```text
production frontend
staging frontend
test frontend
```

must not share mutable shell cache entries unintentionally.

---

# 148. Release Cache Namespace

Where practical, release-specific asset namespaces should be used.

Example:

```text
/assets/release-12/app.abc123.js
```

The exact URL scheme is implementation-specific.

---

# 149. Deployment Concurrency Control

Deployment automation must prevent conflicting concurrent releases from corrupting the active frontend pointer.

A deployment lock or equivalent coordination mechanism may be used.

---

# 150. Frontend Deployment Invariants

The following invariants apply to Frontend Deployment and Static Asset Delivery:

1. Frontend releases are deployable artifacts.
2. Frontend artifacts are immutable after publication.
3. Each release has a unique identity.
4. Release identity is traceable to source.
5. Production artifacts are reproducible.
6. Production should promote validated artifacts rather than rebuild uncontrolled inputs.
7. Dependency versions are controlled.
8. Production builds must not silently resolve arbitrary dependency versions.
9. Failed builds are not published as active releases.
10. Partial artifacts are not activated.
11. HTML must not reference unavailable assets.
12. Immutable assets use versioned or hashed URLs.
13. Mutable assets are not treated as permanently immutable.
14. Hashed assets may use long-lived immutable caching.
15. HTML shell caching must allow controlled release discovery.
16. CDN is not authoritative application state.
17. Reverse proxy cache is not authoritative application state.
18. Browser cache is not authoritative Business state.
19. Service worker cache is not authoritative Business state.
20. Offline local storage is not server authority.
21. PostgreSQL remains the authoritative transactional source.
22. Frontend cannot authorize Business operations.
23. Backend authorization remains mandatory.
24. Business isolation remains server-side.
25. Branch isolation remains server-side.
26. Subscription restrictions remain server-side.
27. Frontend artifacts contain no server secrets.
28. Frontend public configuration is treated as public.
29. Database credentials are never included in frontend artifacts.
30. Redis credentials are never included in frontend artifacts.
31. Private signing keys are never included in frontend artifacts.
32. Deployment credentials are never included in frontend artifacts.
33. API internal addresses are not exposed unnecessarily.
34. Static files are not served through Business transaction logic.
35. Business uploads are not treated as frontend build artifacts.
36. Business-specific durable files use dedicated storage architecture.
37. Static assets may be shared between authorized clients because they contain application code.
38. Static asset sharing must not expose Business data.
39. Environment asset namespaces remain isolated.
40. Production and staging caches must not collide.
41. Immutable assets must be published before new HTML references them.
42. New HTML must not be activated before required assets are verifiably available.
43. Old immutable assets remain available during the rollback/cache transition window.
44. CDN purge failure does not invalidate authoritative release state.
45. Stale HTML must not trigger premature asset deletion.
46. Frontend rollback does not modify Business state.
47. Frontend rollback does not undo Orders.
48. Frontend rollback does not undo Payments.
49. Frontend rollback does not undo Inventory Transactions.
50. Frontend rollback does not delete synchronization queues.
51. Frontend deployment must preserve pending offline operations.
52. Frontend update must not change existing operation UUIDs.
53. Frontend update must not silently discard local transaction state.
54. Local storage migrations must be versioned.
55. Local storage migrations must preserve valid pending transactions.
56. Service worker updates must be versioned where behavior changes.
57. Service worker updates must be tested.
58. Service worker activation must not unnecessarily interrupt active POS work.
59. Service worker rollback must account for already-installed workers.
60. Offline authorization lifetime cannot be extended by frontend updates.
61. Frontend update cannot create new authorization privileges.
62. Subscription expiry cannot be bypassed through stale frontend cache.
63. Branch switching remains server-authorized.
64. Business switching remains server-authorized.
65. Static asset caching cannot bypass API authentication.
66. Static asset caching cannot bypass API authorization.
67. API responses are not treated as ordinary public static assets.
68. Sensitive API data must not be exposed through CDN cache.
69. Static deployment storage is write-protected.
70. Only authorized deployment processes publish production assets.
71. Public clients have read access only through intended delivery paths.
72. Cache headers are validated during deployment.
73. MIME types are validated.
74. Asset integrity is validated.
75. Release asset references are validated.
76. Build output is scanned for secrets.
77. Production debug code is excluded.
78. Development-only endpoints are excluded.
79. Test credentials are excluded.
80. Source maps do not expose unnecessary sensitive implementation information publicly.
81. Third-party frontend resources are controlled.
82. Third-party failure must not unnecessarily block core ERP functionality.
83. Frontend API compatibility must be reviewed before release.
84. Breaking backend API changes require compatibility planning.
85. Multiple frontend releases may temporarily coexist.
86. Backend compatibility must cover the supported frontend transition period.
87. Offline clients may remain on older frontend versions temporarily.
88. Offline clients must not lose valid local Business state because of a new server release.
89. Frontend releases remain compatible with supported offline synchronization protocols.
90. Static delivery remains independently observable from API availability.
91. Static asset errors are observable.
92. Asset 404 spikes are observable.
93. HTML shell failures are observable.
94. Service worker update failures are observable where applicable.
95. Release adoption is observable where supported.
96. Rollback events are observable.
97. Static delivery availability has a target of ≥ 99.9% monthly.
98. Static asset request p95 target is ≤ 200 ms from the delivery layer.
99. HTML shell request p95 target is ≤ 300 ms from the delivery layer.
100. Initial application boot target is ≤ 2.5 s on supported POS hardware under representative conditions.
101. Critical asset failure rate target is < 0.1%.
102. Performance targets are measured rather than assumed.
103. Bundle size is monitored.
104. Application boot time is monitored.
105. Cache hit rate is monitored.
106. Asset failure rate is monitored.
107. Browser error rate is monitored.
108. POS-critical code receives loading priority.
109. Heavy management features must not unnecessarily block POS startup.
110. Large reports should not unnecessarily block initial frontend boot.
111. Large feature bundles should be lazy-loaded where appropriate.
112. Network-constrained branches are considered in deployment design.
113. Reconnection behavior is considered in frontend updates.
114. Deployment concurrency must be controlled.
115. Two releases must not concurrently modify the active release state without coordination.
116. Repeated deployment of the same release is idempotent.
117. Release identifiers are not reused.
118. Old releases remain available for the defined rollback window.
119. Asset garbage collection respects rollback and cache safety windows.
120. Current active release is never removed by ordinary cleanup.
121. Deployment failure leaves the previous healthy release available.
122. Release activation occurs only after validation.
123. Smoke tests are required after production activation.
124. Offline smoke tests are required for offline-affecting changes.
125. Service worker changes require dedicated update testing.
126. Frontend static delivery does not depend on PostgreSQL availability.
127. Frontend static delivery does not depend on Redis availability.
128. Frontend static delivery does not execute core Business transactions.
129. Frontend runtime does not become a durable Business database.
130. Frontend runtime does not become a financial authority.
131. Frontend runtime does not become an inventory authority.
132. Frontend runtime does not become an authorization authority.
133. Frontend runtime does not become a subscription authority.
134. Frontend deployment remains compatible with the Backend API deployment architecture.
135. Frontend deployment remains compatible with the offline architecture.
136. Frontend deployment remains compatible with the modular monolith architecture.
137. Additional CDN or static infrastructure is introduced only when justified by measured need.
138. Simplicity is preferred when multiple delivery strategies provide equivalent correctness.
139. Correctness has priority over cache performance.
140. Security has priority over deployment convenience.
141. Historical integrity has priority over frontend optimization.

---

# 151. Recommended Initial Production Delivery

For a small deployment, the initial model may be:

```text
Browser / POS
      ↓
DNS / TLS
      ↓
Nginx
      ↓
Frontend Static Release
      ↓
Browser Application
      ↓
Backend API
```

Optional CDN:

```text
Browser
   ↓
CDN
   ↓
Static Origin
   ↓
Frontend Release
```

The CDN remains optional until measured traffic or geographic distribution justifies it.

---

# 152. Recommended Initial Cache Policy

Initial strategy:

```text
index.html
→ short cache / revalidation

Hashed JS
→ long-lived immutable cache

Hashed CSS
→ long-lived immutable cache

Hashed images
→ long-lived immutable cache

Fonts
→ long-lived cache when versioned

Service Worker
→ controlled revalidation/update strategy

Runtime public configuration
→ controlled revalidation
```

Exact headers remain deployment configuration.

---

# 153. Recommended Release Flow

```text
Developer Source
      ↓
CI Build
      ↓
Static Checks
      ↓
Frontend Tests
      ↓
Production Build
      ↓
Artifact Validation
      ↓
Security Scan
      ↓
Publish Immutable Assets
      ↓
Verify Assets
      ↓
Publish HTML Shell
      ↓
Invalidate / Revalidate Shell
      ↓
Production Smoke Test
      ↓
Release Active
```

---

# 154. Recommended Rollback Flow

```text
Current Release
      ↓
Detect Failure
      ↓
Activate Previous Known-Good Release
      ↓
Revalidate HTML
      ↓
Verify Static Assets
      ↓
Run Smoke Tests
      ↓
Monitor Recovery
```

Rollback must not modify Business transaction state.

---

# 155. Final Architecture Principle

The frontend deployment layer is a static application delivery system:

```text
Source
  ↓
Build
  ↓
Immutable Artifact
  ↓
Static Origin / CDN
  ↓
Browser
  ↓
Backend API
```

The key rule is:

> Frontend deployment may change, replace, cache, update or rollback application code without becoming the owner of Business state.

The deployment priorities remain:

**Correctness → Security → Offline Continuity → POS Usability → Delivery Performance → Scalability → Operational Simplicity**

---

## 156. Status

**Document Type:** Deployment Architecture

**Document ID:** `DEP-11`

**Document Status:** Proposed

**Version:** `1.0`

**Current Document:** `11_Frontend_Deployment_and_Static_Asset_Delivery.md`

**Previous Document:** `10_Backend_API_Deployment_and_Runtime.md`

**Next Document:** `12_Background_Workers_and_Scheduler_Deployment.md`

---

## 157. Related Documents

### Architecture

* `docs/04_Architecture/18_Backend_API_Design_and_Contract_Architecture.md`
* `docs/04_Architecture/14_Backend_Caching_and_Performance_Architecture.md`
* `docs/04_Architecture/15_Backend_File_Storage_and_Document_Management.md`
* `docs/04_Architecture/16_Backend_Security_Hardening_and_Application_Security.md`
* `docs/04_Architecture/17_Backend_Testing_and_Quality_Assurance_Architecture.md`

### Frontend Architecture

* `docs/07_Frontend/`
* Frontend offline storage and synchronization architecture
* Frontend API client architecture
* Frontend security architecture
* Frontend performance architecture
* Frontend testing architecture

### API

* `docs/09_API/01_API_Architecture_Overview.md`
* `docs/09_API/04_API_Versioning_and_Backward_Compatibility.md`
* `docs/09_API/06_API_Authentication_and_Request_Context.md`
* `docs/09_API/07_API_Authorization_and_Scope_Enforcement.md`
* `docs/09_API/19_API_Offline_Synchronization_and_Reconciliation.md`
* `docs/09_API/24_API_Performance_Observability_and_SLO.md`

### Deployment

* `docs/10_Deployment/01_Deployment_Architecture_Overview.md`
* `docs/10_Deployment/02_Deployment_Principles_and_Environment_Strategy.md`
* `docs/10_Deployment/03_Deployment_Topology_and_Runtime_Architecture.md`
* `docs/10_Deployment/04_Environment_Architecture_and_Configuration.md`
* `docs/10_Deployment/05_Secrets_and_Credential_Management.md`
* `docs/10_Deployment/06_Infrastructure_Architecture_and_Server_Provisioning.md`
* `docs/10_Deployment/07_Networking_DNS_TLS_and_Reverse_Proxy.md`
* `docs/10_Deployment/08_Database_Deployment_and_Runtime_Architecture.md`
* `docs/10_Deployment/09_Redis_Queue_and_Cache_Runtime_Architecture.md`
* `docs/10_Deployment/10_Backend_API_Deployment_and_Runtime.md`
* `docs/10_Deployment/12_Background_Workers_and_Scheduler_Deployment.md`
* `docs/10_Deployment/13_AI_Runtime_and_Model_Service_Deployment.md`
* `docs/10_Deployment/14_CI_CD_Pipeline_Architecture.md`
* `docs/10_Deployment/15_Database_Migration_and_Release_Deployment.md`
* `docs/10_Deployment/16_Release_Strategy_and_Zero_Downtime_Deployment.md`
* `docs/10_Deployment/17_Rollback_and_Release_Recovery.md`
* `docs/10_Deployment/18_Scaling_Load_Balancing_and_Capacity_Architecture.md`
* `docs/10_Deployment/19_High_Availability_and_Failure_Isolation.md`
* `docs/10_Deployment/20_Disaster_Recovery_and_Business_Continuity_Deployment.md`
* `docs/10_Deployment/21_Deployment_Monitoring_Health_Checks_and_Alerting.md`
* `docs/10_Deployment/22_Deployment_Security_Hardening.md`
* `docs/10_Deployment/23_Deployment_Testing_and_Production_Readiness.md`
* `docs/10_Deployment/24_Deployment_Governance_and_Change_Management.md`
* `docs/10_Deployment/25_Deployment_Architecture_Invariants_and_Guardrails.md`

