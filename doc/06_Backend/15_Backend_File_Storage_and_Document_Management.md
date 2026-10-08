# Backend File Storage and Document Management

**Document ID:** BA-15
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/04_Architecture/README.md`

## 1. Purpose

This document defines the backend architecture for file storage and document management in FastFood ERP.

The primary objectives are:

* files must be stored securely;
* Business and Branch isolation must be preserved;
* file metadata must remain authoritative in PostgreSQL;
* binary file storage must remain replaceable;
* large files must not be stored directly in normal transactional tables;
* file operations must not unnecessarily slow POS operations;
* file access must respect permissions and subscription state;
* historical files must not be silently overwritten;
* file lifecycle must support replacement, archival and deletion;
* exports and generated documents must be handled asynchronously where appropriate.

The architecture must support the current SaaS deployment while remaining compatible with future object storage and horizontal scaling.

---

# 2. Scope

This document covers:

* file storage;
* document metadata;
* object storage;
* local filesystem storage;
* future S3-compatible storage;
* file ownership;
* Business scope;
* Branch scope;
* employee scope;
* file categories;
* upload;
* download;
* streaming;
* temporary files;
* generated reports;
* XLSX exports;
* product images;
* document versions;
* replacement;
* archival;
* deletion;
* access control;
* signed download URLs;
* file integrity;
* checksums;
* MIME type validation;
* size limits;
* malware scanning;
* storage quotas;
* subscription lifecycle;
* offline considerations;
* backup;
* recovery;
* observability;
* performance targets;
* SLOs;
* system invariants.

---

# 3. Storage Architecture

The initial architecture separates file metadata from binary content.

```text
Application
    │
    ├── File Metadata
    │       ↓
    │   PostgreSQL
    │
    └── File Content
            ↓
       Storage Adapter
            ↓
       File Storage
```

PostgreSQL stores authoritative metadata.

The storage backend stores binary content.

---

# 4. Storage Abstraction

Application code must not depend directly on a specific storage provider.

The backend should use a storage abstraction such as:

```text
FileStorage
├── put()
├── get()
├── stream()
├── exists()
├── delete()
├── copy()
└── get_temporary_access()
```

The exact interface may be refined during implementation.

Possible implementations:

```text
LocalFilesystemStorage
S3CompatibleStorage
ObjectStorageProvider
```

---

# 5. Initial Storage Strategy

For the initial deployment, local filesystem storage may be used if the application is deployed as a single backend instance.

However, the storage abstraction must allow migration to object storage without changing application-level file handling.

Recommended production direction for horizontal scaling:

```text
Application Instances
        ↓
Storage Adapter
        ↓
S3-Compatible Object Storage
```

---

# 6. PostgreSQL Role

PostgreSQL must store file metadata, not normally the binary file itself.

Example metadata:

```text
File UUID
Business UUID
Branch UUID
Owner Employee UUID
Category
Original Filename
Storage Key
MIME Type
Size
Checksum
Version
Status
Created At
Updated At
```

The database remains authoritative regarding whether a file exists and who may access it.

---

# 7. Binary Storage

Binary content should be stored outside normal transactional tables.

The storage object should be identified by an internal storage key.

Example:

```text
business/{business_uuid}/products/{file_uuid}/v1
```

The exact physical path must not be exposed as a security boundary.

---

# 8. Storage Key Design

Storage keys must be:

* deterministic where appropriate;
* collision-resistant;
* independent of user-provided filenames;
* Business-scoped;
* safe for object storage;
* version-aware where required.

User-provided filenames must never directly become authoritative storage paths.

---

# 9. Business Isolation

Every Business-owned file must be associated with a Business.

Example:

```text
Business A
 └── Product Image A

Business B
 └── Product Image B
```

A file belonging to Business A must never be accessible through Business B context.

Business isolation must be enforced at:

1. metadata query;
2. authorization;
3. storage access;
4. download generation.

---

# 10. Branch Isolation

Branch-scoped files must include Branch ownership.

Examples:

* Branch-specific documents;
* Branch reports;
* Branch operational files.

A Branch-scoped file must not become visible to another Branch without explicit authorization.

Business-global files may be available to authorized Branches.

---

# 11. File Ownership

Each file must have an explicit ownership model.

Possible scopes:

```text
BUSINESS
BRANCH
EMPLOYEE
SYSTEM
```

The scope determines who may access the file.

System-generated files may be owned by the system but remain associated with the relevant Business and/or Branch.

---

# 12. File Categories

The system should classify files.

Examples:

```text
PRODUCT_IMAGE
REPORT_EXPORT
XLSX_EXPORT
DOCUMENT
IMPORT_FILE
SYSTEM_GENERATED
AUDIT_ATTACHMENT
OTHER
```

Additional categories may be added later.

---

# 13. Product Images

Product images are relatively small files and may be stored in object storage or local storage through the same abstraction.

The database stores:

* file UUID;
* Product reference;
* storage key;
* MIME type;
* dimensions where required;
* size;
* checksum;
* status.

The Product itself remains authoritative in PostgreSQL.

---

# 14. Product Image Replacement

Replacing a Product image must not silently destroy historical file references where historical integrity requires preservation.

Recommended behavior:

```text
Old Image
    ↓
Archived
    ↓
New Image
    ↓
Active
```

The old file may later be physically deleted according to retention policy if no historical dependency remains.

---

# 15. File Versioning

Files that require historical integrity should use versions.

Example:

```text
Document
 ├── Version 1
 ├── Version 2
 └── Version 3
```

A new upload should create a new version rather than silently replacing an immutable historical version.

---

# 16. Immutable Generated Documents

Generated historical reports and report exports should be treated separately from temporary exports.

A completed report version is authoritative historical data.

A generated file associated with that report version must not be silently modified.

If a new representation is required, a new file/version should be generated.

---

# 17. Temporary Files

Temporary files include:

* intermediate report files;
* import staging files;
* temporary conversions;
* failed upload fragments;
* temporary generated documents.

Temporary files must have an expiration time.

They must not remain indefinitely.

---

# 18. Temporary File Cleanup

A background cleanup job should remove expired temporary files.

Cleanup must be:

* bounded;
* retryable;
* observable;
* idempotent.

Failure of cleanup must not corrupt authoritative metadata.

---

# 19. Upload Flow

Recommended upload flow:

```text
Client
  ↓
Authentication
  ↓
Authorization
  ↓
Business / Branch validation
  ↓
File validation
  ↓
Temporary storage
  ↓
Checksum / integrity validation
  ↓
Metadata transaction
  ↓
Committed file
```

For larger files, direct-to-object-storage upload may be introduced.

---

# 20. Upload Authorization

Before accepting an upload, the system must validate:

* authenticated employee;
* employee status;
* Business scope;
* Branch scope;
* permission;
* subscription entitlement;
* file category;
* size limit;
* MIME type;
* file extension;
* applicable business rules.

---

# 21. Upload and Transaction Boundaries

Binary upload must not unnecessarily remain inside a long database transaction.

Recommended pattern:

```text
Validate
   ↓
Upload / Stage File
   ↓
Create Metadata Transaction
   ↓
Commit
```

If metadata commit fails, staged content must be cleaned up asynchronously.

---

# 22. File Upload Failure

Possible failures include:

* network interruption;
* storage timeout;
* invalid file;
* size limit exceeded;
* permission denied;
* metadata transaction failure.

The system must not leave permanently orphaned files.

---

# 23. Orphan File Recovery

The system should periodically detect:

```text
Storage object exists
BUT
No valid PostgreSQL metadata
```

Such objects may be marked as orphaned and cleaned after a safe grace period.

The reverse condition must also be monitored:

```text
Metadata exists
BUT
Storage object missing
```

This is a storage integrity problem and must generate an operational alert.

---

# 24. File Integrity

Each stored file should have a checksum where practical.

Recommended:

```text
SHA-256
```

The checksum may be used to verify:

* upload integrity;
* duplicate detection;
* storage corruption;
* migration integrity;
* backup restoration.

---

# 25. Duplicate Files

Duplicate binary content may be detected using checksum.

However, deduplication must not violate:

* Business isolation;
* retention;
* authorization;
* historical integrity.

Physical deduplication must remain an implementation optimization rather than an ownership model.

---

# 26. MIME Type Validation

The system must not trust only the client-provided MIME type.

Validation should consider:

* extension;
* declared MIME type;
* file signature/content where appropriate.

For high-risk file categories, content inspection should be performed.

---

# 27. File Extension Validation

Allowed extensions should be defined per category.

Example:

```text
PRODUCT_IMAGE
→ jpg, jpeg, png, webp

XLSX_EXPORT
→ xlsx

DOCUMENT
→ approved document formats
```

The exact allowlist is configuration.

---

# 28. File Size Limits

Each category should have a bounded maximum size.

Example initial policy:

```text
Product Image      ≤ 10 MB
Normal Document    ≤ 25 MB
XLSX Export        ≤ 50 MB
Import File        ≤ 100 MB
```

These values are initial targets and may be changed through configuration based on actual requirements.

A request exceeding the applicable limit must be rejected before expensive processing where possible.

---

# 29. Large File Handling

Large files must not be loaded completely into application memory.

The system should use:

* streaming;
* bounded buffers;
* multipart upload where supported;
* temporary storage.

This is especially important for imports and generated reports.

---

# 30. Download Flow

Recommended flow:

```text
Client
  ↓
Authentication
  ↓
Authorization
  ↓
Metadata lookup
  ↓
Business / Branch validation
  ↓
Storage access
  ↓
Streaming response
```

The application must not expose raw storage credentials.

---

# 31. Download Authorization

Download authorization must verify:

* Business;
* Branch where applicable;
* employee;
* permission;
* file status;
* subscription state;
* document ownership;
* report/export ownership where applicable.

A valid file UUID alone must never grant access.

---

# 32. Signed URLs

For object storage, short-lived signed URLs may be used.

Example:

```text
Application
   ↓
Authorize
   ↓
Generate short-lived URL
   ↓
Client
   ↓
Object Storage
```

The URL must have:

* short expiration;
* restricted object;
* appropriate HTTP method;
* no unnecessary storage permissions.

---

# 33. Signed URL Security

A signed URL must not be treated as permanent authorization.

The URL should be short-lived.

Recommended initial lifetime:

```text
5–15 minutes
```

Sensitive documents may use shorter expiration.

---

# 34. File Streaming

For large files, streaming should be preferred over loading the entire object into memory.

The backend should support:

* bounded buffering;
* appropriate content headers;
* optional range requests where useful.

---

# 35. Range Requests

Range requests may be supported for large files.

They are useful for:

* large documents;
* resumable downloads;
* media-like files if added later.

Range support is not required for small product images.

---

# 36. File Deletion

Deletion must distinguish:

```text
Logical Deletion
Physical Deletion
```

Logical deletion changes metadata state.

Physical deletion removes binary storage content.

---

# 37. File States

Recommended file states:

```text
UPLOADING
ACTIVE
ARCHIVED
DELETED
FAILED
```

Temporary objects may have separate temporary metadata or lifecycle handling.

---

# 38. Archive Instead of Delete

Historical files should normally be archived rather than immediately physically deleted.

Examples:

* previous Product images;
* historical documents;
* report exports linked to historical records.

Physical deletion should happen only when lifecycle rules permit it.

---

# 39. Subscription Expiry

When a Business subscription expires:

* existing files remain accessible according to read-only rules;
* new modifying file operations are blocked where appropriate;
* permitted exports remain available;
* historical documents remain preserved.

Subscription expiry must not immediately delete files.

---

# 40. Business Deletion Lifecycle

When Business data reaches permanent deletion:

```text
ACTIVE
 ↓
READ_ONLY
 ↓
DELETION_ELIGIBLE
 ↓
DELETING
 ↓
DELETED
```

File storage must follow the same lifecycle.

---

# 41. Business Deletion

During Business deletion:

* metadata is removed or anonymized according to lifecycle policy;
* storage objects are deleted in bounded batches;
* failures are retried;
* progress is observable;
* deletion is idempotent.

Large storage deletion must not be performed as one enormous transaction.

---

# 42. Deletion and Backups

Deleting live Business data does not necessarily mean immediate destruction of all historical backup copies.

Backup retention follows the database backup and lifecycle policy.

The system must document this distinction.

---

# 43. File Retention

File retention may depend on category.

Examples:

```text
Temporary export
→ short retention

Historical report export
→ business/report retention

Product image
→ until no longer required

Audit attachment
→ audit retention policy
```

Retention must be explicit.

---

# 44. Storage Quotas

Business-level storage quotas may be enforced.

Possible quota dimensions:

* total storage;
* report export storage;
* document storage;
* image storage.

Quota enforcement must be server-side.

---

# 45. Storage Usage Calculation

Storage usage may be calculated asynchronously.

The system should not perform a full storage scan on every upload.

Recommended:

```text
File Metadata
   ↓
Stored Size
   ↓
Business Usage Aggregate
```

The aggregate is optimization data and can be reconciled against authoritative metadata.

---

# 46. Quota Race Conditions

Concurrent uploads must not bypass Business storage limits.

Quota enforcement should use an authoritative transactional counter or another concurrency-safe mechanism.

Final storage size remains tied to actual committed files.

---

# 47. File Metadata Model

A file metadata record should conceptually contain:

```text
File
├── id
├── business_id
├── branch_id
├── owner_type
├── owner_id
├── category
├── original_name
├── storage_key
├── mime_type
├── extension
├── size_bytes
├── checksum
├── version
├── status
├── created_by
├── created_at
├── updated_at
└── deleted_at
```

Exact database structure belongs to the Database Analysis phase.

---

# 48. Storage Provider Metadata

Provider-specific metadata should not leak into the domain model unnecessarily.

Examples:

* bucket;
* provider object ID;
* ETag;
* provider version ID.

These belong in infrastructure-level representations where possible.

---

# 49. File Naming

User-visible filename and storage object key are separate.

Example:

```text
User Filename:
menu-spring-2026.xlsx

Storage Key:
business/uuid/files/uuid/v1
```

This prevents filename collisions and unsafe path handling.

---

# 50. Path Traversal Protection

User-provided filenames must never be concatenated directly into filesystem paths.

The implementation must prevent:

```text
../
../../
absolute paths
special path traversal sequences
```

Storage keys must be generated by the application.

---

# 51. Filename Sanitization

Original filenames may be preserved for display.

However:

* unsafe characters must be sanitized for HTTP headers;
* control characters must be rejected;
* excessively long filenames must be truncated safely;
* the internal storage key remains independent.

---

# 52. File Access Logging

Important document access may be audited.

Audit may include:

```text
File UUID
Business UUID
Branch UUID
Employee UUID
Device UUID
Operation
Timestamp
Result
```

Not every static image request necessarily requires a heavy audit record.

The exact audit level depends on sensitivity.

---

# 53. Sensitive Documents

Sensitive files may require stronger controls.

Examples:

* payroll documents;
* security documents;
* private employee documents;
* sensitive reports.

Possible controls:

* stronger permission;
* shorter signed URL;
* download audit;
* no public caching;
* stricter retention.

---

# 54. Browser Cache Headers

Sensitive documents should use appropriate cache-control headers.

The backend must avoid accidentally making private Business documents publicly cacheable.

---

# 55. Public Files

FastFood ERP should not assume that uploaded files are public.

Default behavior:

**Private.**

A future public-file feature must be explicitly designed with separate authorization rules.

---

# 56. Product Image Access

Product images may be served more efficiently than sensitive documents.

If Product images are considered safe for broader authenticated access, they may use:

* CDN;
* public-like signed URLs;
* longer cache lifetime.

However, Business isolation must still be preserved if images are not globally public.

---

# 57. File Import

Import files should use a staging workflow:

```text
Upload
 ↓
Validate
 ↓
Store Staging File
 ↓
Parse
 ↓
Business Validation
 ↓
Preview / Result
 ↓
Commit Business Changes
 ↓
Archive/Delete Staging File
```

Import parsing must not directly mutate Business state before validation.

---

# 58. Import Security

Imported files must be validated for:

* file type;
* size;
* structure;
* expected columns;
* malicious content where applicable;
* Business scope.

The client must not control target Business identity through file content.

---

# 59. XLSX Export

XLSX export is generated asynchronously.

Recommended flow:

```text
Export Request
   ↓
Authorization
   ↓
Export Job
   ↓
Report Snapshot / Query
   ↓
XLSX Generation
   ↓
Storage
   ↓
Export File Metadata
   ↓
Notification
```

---

# 60. Export Ownership

An export file must be associated with:

* Business;
* Branch where applicable;
* requesting employee;
* report definition;
* report version or source state;
* creation time.

---

# 61. Export Expiration

Temporary exports should have a defined expiration.

Example:

```text
Temporary XLSX Export
→ 7–30 days
```

The exact retention should be configuration.

Historical report artifacts required for long-term audit should follow a separate retention policy.

---

# 62. File Access and Offline Mode

Offline POS should not depend on downloading arbitrary files from the server.

Only required offline assets should be synchronized.

Examples:

* authorized Product images;
* required configuration assets.

Large documents and reports should remain online-only unless explicitly supported.

---

# 63. Offline File Cache

Offline file cache must:

* be encrypted;
* be tied to trusted device;
* have bounded storage;
* follow offline authorization;
* support expiration;
* avoid storing unnecessary sensitive documents.

---

# 64. File Synchronization

Binary files should not normally be synchronized as part of every transaction batch.

Instead:

```text
Transaction Sync
     ↓
Metadata / Required Asset References
     ↓
Controlled File Sync
```

This prevents large binary transfers from blocking transactional synchronization.

---

# 65. Product Image Synchronization

Product images may be synchronized separately from transaction data.

The device should use the latest valid image available locally.

If an image is unavailable offline, the POS must still function.

Image availability must never block order creation.

---

# 66. File and Transaction Priority

File transfer must have lower priority than core transaction synchronization.

Priority:

```text
1. Order / Payment / Inventory Sync
2. Cash / Handover Sync
3. Configuration Sync
4. Required Asset Sync
5. Non-critical File Sync
```

---

# 67. File Storage and POS Performance

Product image loading must not block critical POS operations.

The POS should be able to:

* show a placeholder;
* use cached image;
* continue without image.

A missing image must never prevent Product sale when the Product is otherwise valid.

---

# 68. File Storage Performance Targets

Initial targets for a normal production deployment:

| Operation                           |                                   Target |
| ----------------------------------- | ---------------------------------------: |
| File metadata lookup                |                             p95 ≤ 100 ms |
| Small file metadata create          |                             p95 ≤ 150 ms |
| Product image upload ≤ 5 MB         | p95 ≤ 1.5 s excluding client upload time |
| Small document download ≤ 10 MB     |                p95 ≤ 1.5 s to first byte |
| Signed URL generation               |                             p95 ≤ 100 ms |
| Storage existence check             |                             p95 ≤ 200 ms |
| File metadata authorization check   |                             p95 ≤ 100 ms |
| XLSX export request acknowledgement |                             p95 ≤ 300 ms |
| Temporary-file cleanup operation    |                  p95 ≤ 500 ms per object |

These are initial engineering targets, not guarantees independent of network conditions.

---

# 69. File Storage SLO

For production:

**File metadata service availability target: 99.9% monthly.**

This applies to normal metadata operations excluding planned maintenance.

Object storage availability follows the selected storage provider's service characteristics.

---

# 70. Upload SLO

For files within configured limits:

* 99% of successful upload operations should complete within the target latency for the selected file class;
* upload failures caused by storage infrastructure should remain below 0.1% of requests;
* failed uploads must not create permanent orphan metadata.

Client network latency is outside the backend SLO.

---

# 71. Download SLO

For authorized small files:

* 99.9% of metadata authorization requests should succeed or return a deterministic authorization result;
* p95 time to first byte should remain ≤ 1.5 seconds under normal conditions;
* storage errors should be observable and retryable where safe.

Large-file transfer duration depends on file size and network bandwidth and is therefore not fixed by the backend latency SLO.

---

# 72. Export SLO

For normal XLSX exports:

* export request acknowledgement p95 ≤ 300 ms;
* job enqueue success ≥ 99.9%;
* export jobs must expose a deterministic status;
* failed jobs must be retryable where safe;
* users must not wait synchronously for large XLSX generation.

The actual generation duration depends on report size.

---

# 73. File Integrity SLO

The system should maintain:

**99.999%+ integrity for successfully committed file objects.**

Any detected mismatch between metadata checksum and stored content must generate an operational alert.

---

# 74. Orphan File SLO

Orphaned storage objects should be detected within:

**24 hours**

under normal cleanup/reconciliation scheduling.

They should be eligible for cleanup only after a safe grace period.

---

# 75. Missing Object SLO

A metadata record pointing to a missing storage object should be detected within:

**24 hours**

or immediately for critical file access paths where the failure is encountered.

Critical missing files should generate an alert without waiting for scheduled reconciliation.

---

# 76. Storage Usage SLO

Business storage usage calculations should normally become consistent within:

**5 minutes**

after successful file commit.

Usage calculation is derived operational data and is not the authoritative file existence state.

---

# 77. Deletion SLO

Temporary file cleanup should normally complete within:

**24 hours after expiration.**

Business deletion may take longer because deletion is intentionally performed in bounded background batches.

The deletion job must provide progress and retry information.

---

# 78. File Service Observability

Metrics should include:

```text
file_upload_count
file_upload_failure_count
file_download_count
file_download_failure_count
file_storage_latency
file_metadata_latency
file_size_bytes
file_integrity_failure_count
orphan_file_count
missing_object_count
storage_usage_bytes
cleanup_count
cleanup_failure_count
export_job_duration
```

Metrics must use low-cardinality labels.

Do not use raw:

* Business UUID;
* File UUID;
* Employee UUID

as unrestricted metric labels.

---

# 79. File Error Classification

File-related failures should be classified as:

```text
Validation Error
Authorization Error
Quota Error
Storage Error
Integrity Error
Conflict
Temporary Infrastructure Error
Permanent Failure
```

Example:

```text
Unsupported MIME Type
→ Validation Error

Business Has No Storage Permission
→ Authorization Error

Storage Provider Timeout
→ Temporary Infrastructure Error

Checksum Mismatch
→ Integrity Error
```

---

# 80. Retry Policy

Safe temporary storage operations may be retried.

Retry must use:

* bounded attempts;
* exponential backoff;
* jitter;
* operation identity where applicable.

A retry must not create duplicate metadata or duplicate business state.

---

# 81. File Idempotency

Upload commands that can be retried should use an operation UUID where appropriate.

Repeated requests must not create unintended duplicate logical files.

For explicit user requests to upload the same file again, creating a new file/version may be valid.

The distinction must be based on operation identity, not checksum alone.

---

# 82. Storage Provider Failure

If storage is temporarily unavailable:

* metadata operations that require binary storage may fail safely;
* unrelated POS operations must continue;
* cached Product images may continue to display;
* already committed Orders must remain unaffected.

Storage failure must not rollback unrelated business transactions.

---

# 83. Storage Migration

Migration between storage providers must be possible.

Recommended:

```text
Current Storage
      ↓
Migration Worker
      ↓
New Storage
      ↓
Checksum Verification
      ↓
Metadata Update
      ↓
Old Storage Cleanup
```

Migration must be resumable and idempotent.

---

# 84. Storage Migration Integrity

Every migrated object should be verified using:

* size;
* checksum;
* object existence.

Only after successful verification should the new storage location become authoritative.

---

# 85. Backup Strategy

File metadata must be included in database backups.

Binary storage must have an independent backup or replication strategy.

Database backup without binary storage backup is incomplete for file-dependent records.

---

# 86. Restore Strategy

A restore test must verify:

```text
PostgreSQL Metadata
+
Binary Storage
+
Storage Keys
+
Checksums
```

A restored metadata record pointing to unavailable files must be treated as an incomplete restore.

---

# 87. Disaster Recovery

Storage recovery should support:

* object restoration;
* metadata restoration;
* checksum verification;
* orphan detection;
* missing-object detection.

The recovery process must be documented and periodically tested.

---

# 88. Security

File storage security must include:

* authenticated access;
* authorization;
* Business isolation;
* Branch isolation;
* private-by-default storage;
* signed URLs where used;
* encrypted transport;
* encryption at rest where supported;
* secure storage credentials;
* no credentials in source code;
* no storage secrets in logs.

---

# 89. Encryption

Data in transit must use secure transport.

Sensitive stored files should use encryption at rest.

The application should not implement custom cryptography for normal storage encryption when the infrastructure provider offers established encryption mechanisms.

---

# 90. Storage Credentials

Storage credentials must be managed through the application's secret-management configuration.

Credentials must not be:

* committed to Git;
* stored in source code;
* returned in API responses;
* written into normal application logs.

---

# 91. Malware Scanning

For user-uploaded document categories where risk justifies it, files should pass malware scanning before becoming active.

Possible flow:

```text
Upload
 ↓
QUARANTINE
 ↓
Scan
 ↓
Clean
 ↓
ACTIVE
```

Unsafe files must not become available to other users.

---

# 92. Product Image Security

Product images should still undergo basic file validation.

At minimum:

* MIME validation;
* extension validation;
* size limit;
* content/signature validation where practical.

Image processing libraries must be kept patched.

---

# 93. Image Processing

Image resizing/compression should run outside core transactions.

Possible generated variants:

```text
original
thumbnail
medium
POS
```

The original may be preserved depending on retention requirements.

---

# 94. Image Processing Failure

If image processing fails:

* Product creation/configuration must not necessarily fail if the image is optional;
* the original file may remain quarantined or stored according to policy;
* the user must receive a clear result;
* retry should be possible.

---

# 95. File Access and Permissions

Permissions may include:

```text
file.view
file.upload
file.download
file.replace
file.archive
file.delete
file.export
```

Exact permission names belong to the centralized permission model.

---

# 96. Subscription Authorization

File operations must respect subscription state.

Example:

```text
ACTIVE
→ normal file operations

READ_ONLY
→ view/download allowed where policy permits
→ new modifying operations blocked

DELETING
→ normal user file operations blocked
```

---

# 97. Employee Deactivation

Inactive employees must not perform new file modifications.

Historical files created by the employee remain attributed to that employee.

---

# 98. Audit

Important file operations should create audit events:

* upload;
* replacement;
* archive;
* deletion;
* sensitive download;
* export generation;
* permission-sensitive access;
* storage migration;
* integrity failure.

The audit record must identify the responsible actor or system process.

---

# 99. Audit and File Content

Audit logs should normally store metadata about the file, not duplicate the binary content.

Example:

```text
File UUID
Operation
Employee UUID
Business UUID
Branch UUID
Timestamp
Result
```

---

# 100. File and Notification

File operations may trigger asynchronous notifications.

Examples:

* export ready;
* import failed;
* file scan failed;
* storage quota exceeded;
* document deletion scheduled.

Notification processing must not block the file transaction.

---

# 101. Background Jobs

Recommended file-related jobs:

```text
FileCleanupJob
FileIntegrityCheckJob
OrphanDetectionJob
StorageUsageJob
FileMigrationJob
ImageProcessingJob
MalwareScanJob
ExportGenerationJob
```

Each job must be:

* bounded;
* retryable;
* observable;
* idempotent where appropriate.

---

# 102. Job Priority

Recommended priority:

```text
Critical Integrity / Security
        ↓
Export / Required Operational Files
        ↓
Image Processing
        ↓
Cleanup
        ↓
Migration / Reconciliation
```

Heavy migration must not degrade POS.

---

# 103. File Storage and Caching

File metadata may be cached.

Binary files may use:

* CDN;
* browser cache;
* object storage cache;
* application cache

where appropriate.

However, authorization-sensitive metadata must remain server-authoritative.

---

# 104. Cache Invalidation

If file metadata is cached, changes such as:

* archive;
* deletion;
* replacement;
* permission change

must invalidate relevant cache entries.

A deleted file must not remain downloadable indefinitely because of stale metadata.

---

# 105. CDN

A CDN may be introduced for high-volume Product images.

The CDN must not become the authoritative source.

If CDN content is stale, the application must still be able to determine the current valid Product image.

---

# 106. File URL Stability

Internal storage URLs should not be treated as permanent public identifiers.

The application should expose logical file references rather than provider-specific paths.

This makes storage migration possible.

---

# 107. API Design

The API should expose operations such as:

```text
POST   /files
GET    /files/{file_id}
GET    /files/{file_id}/download
POST   /files/{file_id}/versions
POST   /files/{file_id}/archive
DELETE /files/{file_id}
```

Exact route names belong to the API design document.

Routes must remain thin and delegate to Application use cases.

---

# 108. Application Layer

Application use cases should handle:

* authorization;
* validation;
* file lifecycle;
* metadata transaction;
* storage orchestration;
* audit;
* background job dispatch.

Storage provider details must remain in Infrastructure.

---

# 109. Domain Layer

The Domain layer should contain business concepts such as:

* File;
* FileVersion;
* FileStatus;
* FileOwnership;
* RetentionPolicy where applicable.

The Domain must not depend directly on S3, filesystem APIs or HTTP.

---

# 110. Repository Layer

Repositories should handle metadata persistence.

Examples:

```text
FileRepository
FileVersionRepository
StorageMetadataRepository
```

Repositories must enforce validated Business/Branch scope.

---

# 111. Infrastructure Layer

Infrastructure may contain:

```text
storage/
├── interface.py
├── local_filesystem.py
├── object_storage.py
├── signed_urls.py
├── checksum.py
└── cleanup.py
```

Exact structure may evolve during implementation.

---

# 112. Performance Isolation

File operations must not consume unlimited resources from the main application.

Controls may include:

* upload concurrency limit;
* download concurrency limit;
* worker pool;
* file size limit;
* streaming;
* queue backpressure;
* separate export workers.

---

# 113. POS Protection

If file traffic becomes excessive, the system must prioritize:

```text
POS
Cash
Inventory
Payment
Synchronization
```

over:

```text
Large Downloads
Bulk Exports
Image Processing
Storage Migration
Cleanup
```

---

# 114. File Storage SLO Summary

Initial production SLO targets:

| SLO                                    |              Target |
| -------------------------------------- | ------------------: |
| File metadata service availability     |       99.9% monthly |
| Signed URL generation                  |        p95 ≤ 100 ms |
| Metadata lookup                        |        p95 ≤ 100 ms |
| Upload infrastructure failure rate     |              < 0.1% |
| Small-file download time to first byte |         p95 ≤ 1.5 s |
| Export request acknowledgement         |        p95 ≤ 300 ms |
| Storage usage convergence              |             ≤ 5 min |
| Orphan detection                       |              ≤ 24 h |
| Missing-object detection               |              ≤ 24 h |
| Temporary-file cleanup                 | ≤ 24 h after expiry |
| File integrity target                  |           ≥ 99.999% |

These targets should be validated and adjusted after production baseline measurements.

---

# 115. Performance Testing

Testing should include:

### Small File

* Product images;
* small documents.

### Medium File

* XLSX exports;
* normal documents.

### Large File

* imports;
* large exports.

### Concurrent Load

* multiple uploads;
* multiple downloads;
* simultaneous POS operations.

### Failure Load

* storage timeout;
* storage unavailable;
* interrupted upload;
* missing object;
* checksum mismatch.

---

# 116. Storage Load Testing

Storage tests must measure:

* upload latency;
* download latency;
* metadata latency;
* memory usage;
* CPU usage;
* network bandwidth;
* concurrent operations;
* queue backlog.

---

# 117. Acceptance Criteria

The implementation is acceptable when:

1. Files are separated from authoritative metadata.
2. Business isolation is enforced.
3. Branch isolation is enforced.
4. File access requires authorization.
5. Storage provider can be replaced through an adapter.
6. Large files do not require full-memory loading.
7. Upload failures do not create permanent uncontrolled orphan state.
8. File integrity can be verified.
9. Historical files can be archived/versioned.
10. Temporary files are automatically cleaned.
11. XLSX exports are asynchronous.
12. Storage failure does not corrupt unrelated transactions.
13. Subscription restrictions are respected.
14. Business deletion includes file storage.
15. File operations are observable.
16. Performance targets can be measured.
17. POS remains protected from heavy file workloads.

---

# 118. System Invariants

The following invariants apply to File Storage and Document Management:

1. PostgreSQL remains authoritative for file metadata.
2. Binary storage is not the source of authorization truth.
3. Every Business-owned file has a Business scope.
4. Branch-scoped files have an explicit Branch scope.
5. Cross-Business file access is prohibited.
6. Cross-Branch file access is prohibited unless explicitly authorized.
7. Files are private by default.
8. File UUID alone does not grant access.
9. Storage provider paths are not authorization boundaries.
10. User filenames are never authoritative storage keys.
11. Storage keys are application-generated.
12. Path traversal must be prevented.
13. File size limits are enforced server-side.
14. Allowed file types are validated server-side.
15. Client-provided MIME type is not blindly trusted.
16. Large files must not be loaded entirely into application memory.
17. Streaming is preferred for large downloads.
18. File metadata and binary content are logically separate.
19. File versions must be preserved where historical integrity requires them.
20. Historical files must not be silently overwritten.
21. Product image replacement must preserve required historical integrity.
22. Generated historical documents must remain immutable.
23. Temporary files have bounded lifetime.
24. Expired temporary files are cleaned automatically.
25. Cleanup failure does not corrupt authoritative metadata.
26. Orphan storage objects are detectable.
27. Missing storage objects are detectable.
28. Important files should have integrity checks.
29. Checksum mismatch is an integrity failure.
30. Storage credentials must never be exposed to clients.
31. Storage credentials must not be committed to source control.
32. Signed URLs are short-lived.
33. Signed URLs do not replace authorization.
34. Sensitive documents use stricter access controls where required.
35. File access must respect employee status.
36. File access must respect Business scope.
37. File access must respect Branch scope.
38. File access must respect permissions.
39. File modification must respect subscription entitlement.
40. READ_ONLY Businesses cannot perform blocked modifications.
41. Business deletion includes associated file storage.
42. File deletion is lifecycle-aware.
43. Logical deletion and physical deletion are separate concepts.
44. Physical deletion is performed safely and idempotently.
45. Backup policy must cover file metadata and binary storage.
46. Database restore without binary restore is considered incomplete for file-dependent data.
47. Storage migration must verify object integrity.
48. Storage migration must be resumable.
49. Storage migration must be idempotent.
50. File operations must not unnecessarily block core transactions.
51. File uploads must not hold long database transactions open.
52. File downloads must not hold database transactions open.
53. XLSX generation must be asynchronous.
54. Image processing must not block core transactions.
55. Malware scanning must complete before risky files become active where scanning is required.
56. Storage provider failure must not corrupt unrelated Business transactions.
57. Storage provider failure must not normally stop POS operations.
58. Heavy file processing must not starve POS resources.
59. File transfer priority is lower than core transaction synchronization.
60. Offline POS must not depend on arbitrary file downloads.
61. Product image absence must not block Product sale.
62. Offline file cache must be encrypted where sensitive data is stored.
63. Offline file cache must respect trusted-device authorization.
64. Offline file cache must respect expiration.
65. Cached file metadata must not override authoritative state.
66. Deleted files must not remain indefinitely accessible through stale cache.
67. CDN content is not authoritative.
68. File URLs must remain replaceable across storage migrations.
69. File metadata access should be auditable where sensitivity requires it.
70. File audit records must identify the responsible actor or system.
71. File binary content should not be duplicated unnecessarily inside audit records.
72. File quotas must be enforced server-side.
73. Concurrent uploads must not bypass storage quotas.
74. Storage usage aggregates are derived data and must be reconcilable.
75. File jobs must have bounded concurrency.
76. File jobs must not create unbounded queue growth.
77. Retry attempts must be bounded.
78. Temporary storage errors may be retried safely.
79. Repeated upload commands must be protected by idempotency where appropriate.
80. Explicitly requested new file versions remain distinguishable from retried operations.
81. File metadata changes must be atomic.
82. Secondary notifications must not roll back committed file metadata.
83. File cleanup must not delete active objects.
84. Historical documents must remain reconstructable.
85. Storage provider implementation must remain replaceable.
86. Domain logic must not depend on filesystem or object-storage APIs.
87. Application code should depend on storage abstractions.
88. Repository operations must preserve Business and Branch scope.
89. File SLOs must be measurable.
90. File integrity failures must be observable.
91. Missing objects must be observable.
92. Orphan objects must be observable.
93. Storage performance must not compromise security.
94. Storage performance must not compromise historical integrity.
95. File management must remain compatible with horizontal backend scaling.
96. File management must remain compatible with future object storage.
97. File lifecycle must remain compatible with Business lifecycle.
98. File retention must be explicit.
99. File deletion must not silently remove required historical evidence.
100. Correctness and security have priority over storage performance.

---

# 119. Recommended Backend Structure

```text
app/
├── application/
│   ├── files/
│   │   ├── upload.py
│   │   ├── download.py
│   │   ├── replace.py
│   │   ├── archive.py
│   │   └── delete.py
│   │
│   ├── reports/
│   └── exports/
│
├── domain/
│   └── file/
│       ├── entities.py
│       ├── value_objects.py
│       ├── policies.py
│       └── services.py
│
├── infrastructure/
│   ├── storage/
│   │   ├── interface.py
│   │   ├── local_filesystem.py
│   │   ├── object_storage.py
│   │   ├── signed_urls.py
│   │   ├── checksum.py
│   │   └── cleanup.py
│   │
│   ├── database/
│   └── monitoring/
│
├── background/
│   └── files/
│       ├── cleanup.py
│       ├── integrity.py
│       ├── migration.py
│       ├── image_processing.py
│       └── scanning.py
│
├── reporting/
└── shared/
```

Exact structure may be refined during implementation.

---

# 120. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/16_Reports_and_Dashboards.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`

### System Analysis

* `docs/02_System_Analysis/20_Reports_and_Report_Versioning.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/25_Subscription_and_Entitlement.md`
* `docs/02_System_Analysis/28_Background_Jobs_and_Recovery.md`
* `docs/02_System_Analysis/29_Error_Handling_and_Failure_Recovery.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Database

* `docs/05_Database/01_Database_Overview.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

### Backend

* `docs/06_Backend/01_Backend_Architecture.md`
* `docs/06_Backend/02_Backend_Project_Structure.md`
* `docs/06_Backend/07_Transaction_Management.md`
* `docs/06_Backend/10_Notifications_and_External_Integrations.md`
* `docs/06_Backend/11_Configuration_and_Environment_Management.md`
* `docs/06_Backend/14_Backend_Caching_and_Performance_Architecture.md`

---

# 121. Status

**Backend Architecture Document:** Completed.

**Document Status:** Accepted.

**Current Document:** `15_Backend_File_Storage_and_Document_Management.md`

**Next Document:** `16_Backend_Security_Hardening_and_Application_Security.md`

