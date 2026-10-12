# File Storage and Document Operations

**Document ID:** OPS-15
**File:** `15_File_Storage_and_Document_Operations.md`
**Status:** Accepted
**Version:** 1.0
**Parent:** `doc/14_Operations/README.md`
**Scope:** File storage operations, document access, upload and download reliability, retention, cleanup, backup, recovery, and storage security.

---

## 1. Purpose

This document defines operational procedures for storing, accessing, maintaining, cleaning up, and recovering files and documents used by the FastFood ERP platform.

Depending on the implemented product features, stored objects may include:

* Business documents and generated reports.
* Product and category images.
* Employee or business-related attachments.
* Imported spreadsheets and export files.
* Generated invoices or other operational documents.
* AI input or output files, where explicitly supported.
* Temporary processing files.
* Backup and recovery artifacts.

The exact file categories depend on the approved application architecture. This document does not assume a particular storage provider, filesystem, object-storage service, or document-management framework.

The objectives are to preserve data integrity, enforce authorized access, prevent cross-tenant exposure, control storage growth, and provide reliable recovery procedures.

## 2. Scope and Boundaries

This document covers:

1. Storage inventory and ownership.
2. File lifecycle and metadata.
3. Upload and download operations.
4. Access control and tenant isolation.
5. File validation and malware protection.
6. Retention and cleanup.
7. Storage capacity and performance.
8. Backup and recovery.
9. Incident handling.
10. Operational evidence and audit requirements.

Related operational documents:

* Database operations: `09_Database_Operations.md`.
* Background workers and cleanup jobs: `13_Background_Worker_and_Scheduler_Operations.md`.
* AI runtime operations: `14_AI_Runtime_Operations.md`.
* Subscription and data lifecycle: `16_Subscription_and_Data_Lifecycle_Operations.md`.
* Security operations: `17_Security_Operations.md`.
* Disaster recovery: `08_Disaster_Recovery_Operations_Runbook.md`.

Database records and file contents may be stored separately. Their consistency must be considered together during deletion, migration, backup, and recovery.

## 3. Core Operational Principles

### 3.1 Metadata and content consistency

A file may have both a storage object and a database record describing its owner, location, type, and lifecycle state.

Operations must prevent:

* Metadata pointing to a missing file.
* Untracked files remaining indefinitely.
* A deleted file remaining accessible through an old URL.
* A file being assigned to the wrong tenant or branch.
* Cleanup deleting content that is still referenced by a valid business record.

### 3.2 Private by default

Business documents and uploaded files must not be publicly accessible unless public access is explicitly required, approved, and limited to suitable content.

Knowledge of a storage path or object identifier must not grant access to private content.

### 3.3 Tenant and branch isolation

Every file access must be authorized against the relevant tenant, branch, business record, and user permissions.

Storage paths alone must not be treated as authorization boundaries.

### 3.4 Safe deletion

Permanent deletion must follow the approved retention and lifecycle policy.

Cleanup jobs must verify that a file is eligible for deletion before removing its content. Temporary storage must not become a route for accidentally deleting business records.

### 3.5 Recoverability

Critical files must have an appropriate recovery strategy. Backup completion alone is not proof that the file can be restored and correctly associated with its business metadata.

## 4. Storage Inventory

Maintain an inventory of production storage locations and file categories.

For each storage location, record:

* Storage identifier and purpose.
* Storage type and location.
* Responsible owner.
* File categories stored.
* Data classification.
* Access-control model.
* Encryption requirements.
* Retention policy.
* Capacity limits and monitoring.
* Backup and recovery arrangements.
* Dependencies and network access.
* Cleanup mechanism.
* Relevant service-level expectations.
* Incident escalation path.

The inventory must distinguish among:

* Persistent business files.
* Temporary files.
* Generated files that can be safely regenerated.
* Imported source files that must be retained.
* Backup and recovery artifacts.
* Logs and diagnostic attachments.

Do not classify a file as disposable solely because it was generated automatically. Some generated files may be required for audit, legal, or business purposes.

## 5. File Metadata and Lifecycle

### 5.1 Metadata requirements

Store the metadata required to manage and authorize files safely.

Depending on the file type, this may include:

* Unique file identifier.
* Tenant identifier.
* Branch identifier when applicable.
* Related business-record identifier.
* Storage object reference.
* Original display filename.
* Validated media type.
* File size.
* Upload timestamp.
* Uploading user or service identity.
* Integrity checksum.
* Lifecycle state.
* Retention classification.
* Processing or validation status.
* Creation and modification timestamps where relevant.

Avoid storing unnecessary personal information in metadata.

### 5.2 Logical lifecycle

A file lifecycle may include:

1. **Initiated** — upload or generation has started.
2. **Quarantined** — the file is awaiting validation or security scanning.
3. **Available** — validation succeeded and authorized access is permitted.
4. **Processing** — a background process is working on the file.
5. **Archived** — the file is retained but no longer part of routine active use.
6. **Deletion pending** — the file has been marked for deletion.
7. **Deleted** — the file is no longer available through the application.
8. **Failed** — upload, validation, or processing failed.

These are logical states. Implement them according to the actual storage and application architecture.

### 5.3 State transitions

* Files must not become available before required validation completes.
* Failed uploads must not be represented as completed uploads.
* Archived files must follow their defined access policy.
* Files marked for deletion must not be deleted if a valid retention hold applies.
* Deleted files must not remain accessible through application-controlled links.
* State transitions must be traceable when required by the file's risk and retention classification.

## 6. Upload Operations

### 6.1 Upload validation

Before a file becomes available, apply the validation appropriate to its category.

Controls may include:

* Authentication and authorization.
* Tenant and branch scope validation.
* File size limits.
* Allowed file types.
* File signature or content inspection.
* Malware scanning where required.
* Safe filename handling.
* Content validation for structured imports.
* Quarantine and processing status.
* Storage quota enforcement.

The declared filename extension or client-supplied MIME type must not be treated as sufficient proof of file content.

### 6.2 Upload workflow

The upload workflow should:

1. Authenticate the requester.
2. Authorize the intended operation and target business record.
3. Validate the target tenant and branch.
4. Apply size and type restrictions.
5. Store the upload in a controlled temporary or quarantine location where required.
6. Validate and scan the content according to policy.
7. Persist the file metadata and appropriate lifecycle state.
8. Make the file available only after required checks pass.
9. Record the outcome and relevant audit information.

The implementation must account for failures between storage and database operations.

### 6.3 Partial upload recovery

If an upload is interrupted:

* Determine whether the storage object was created.
* Determine whether metadata was committed.
* Avoid creating duplicate records during retries.
* Remove abandoned temporary content according to policy.
* Preserve a valid completed upload.
* Record repeated failures where operationally relevant.

Use idempotent upload identifiers or equivalent controls where duplicate submission is possible.

### 6.4 File naming

Use safe storage identifiers rather than trusting user-supplied filenames as storage paths.

Preserve the original filename only as metadata when needed. Sanitize it before display or download.

Prevent path traversal, unsafe path separators, control characters, and other filename-based attacks.

## 7. Download and File Access Operations

### 7.1 Authorization

Before serving a private file, validate:

* User or service identity.
* Relevant permissions.
* Tenant ownership.
* Branch scope where applicable.
* Relationship to the requested business record.
* File lifecycle and availability state.

Authorization must be enforced by the server or storage-access mechanism, not solely by the frontend.

### 7.2 Access mechanisms

Depending on the architecture, file access may use:

* An authenticated application endpoint.
* A private storage gateway.
* A short-lived signed URL.
* Another explicitly approved access mechanism.

Signed URLs, where used, must have limited scope and lifetime. Their permissions must be no broader than required.

Revocation requirements must account for the actual mechanism. Removing a database record may not immediately revoke an already issued URL.

### 7.3 Download behavior

Verify:

* Correct file retrieval.
* Appropriate content type.
* Safe content disposition.
* Correct access-control behavior.
* Expected file integrity where applicable.
* Appropriate caching directives.
* Correct handling of missing, archived, or deleted files.

Private documents must not be exposed through public caches.

### 7.4 Cross-tenant access tests

Operational and security verification must include attempts to access files using identifiers associated with another tenant or branch.

Changing a file identifier, URL, or request parameter must not grant unauthorized access.

## 8. File Type and Content Security

### 8.1 Allowed content

Define permitted file types according to the business function.

Do not allow unrestricted file uploads merely because the storage layer supports them.

### 8.2 Malware and unsafe content

Where required, scan uploaded files before making them available.

Quarantine files when:

* Scanning is pending.
* Scanning fails.
* The scanning service is unavailable and policy requires scanning.
* The file is flagged as unsafe.
* The file type or structure is unsupported.

The system must have a documented policy for unavailable scanning services. It must not silently treat an unscanned file as safe when scanning is required.

### 8.3 Spreadsheet imports

Imported spreadsheets can affect inventory, prices, employee data, or other business records.

For imports:

* Validate the expected schema.
* Check field types and value constraints.
* Validate the target tenant and branch.
* Preview or stage changes where the workflow requires it.
* Apply business rules before committing changes.
* Record import errors and the final outcome.
* Prevent partial processing from leaving business records inconsistent.

Spreadsheet content must be treated as untrusted input.

### 8.4 Document previews

If the application renders previews, use a safe rendering method suitable for the file type.

Do not execute uploaded scripts or active content as part of preview generation.

Preview failures must not make the original file publicly accessible or bypass authorization.

## 9. Storage Capacity and Performance

### 9.1 Capacity monitoring

Monitor, as applicable:

* Total storage consumption.
* Free disk space.
* Object count.
* Upload and download error rates.
* File size distribution.
* Storage growth rate.
* Temporary and quarantined storage usage.
* Cleanup backlog.
* Request latency.
* Storage request limits or rate limits.
* Backup storage consumption.

### 9.2 Capacity planning

Estimate storage needs using observed upload rates, file retention, average file sizes, generated artifacts, and backup requirements.

Distinguish active business storage from temporary data and backups.

Before increasing capacity, investigate abnormal growth, repeated uploads, failed cleanup jobs, and unexpected generated-file accumulation.

### 9.3 Large files

Apply suitable limits and transfer strategies for large files.

Depending on the architecture, these may include streaming, multipart uploads, bounded concurrency, resumable uploads, or asynchronous processing.

Avoid loading unnecessarily large files fully into application memory.

### 9.4 Resource protection

File operations must not exhaust resources needed by POS and backend APIs.

Use bounded concurrency and timeouts for uploads, downloads, scanning, conversion, and cleanup.

Large exports or document-generation workloads should be isolated where appropriate.

## 10. Retention, Archiving, and Cleanup

### 10.1 Retention policy

Define retention by file category and business purpose.

The policy must account for:

* Business requirements.
* Audit and legal obligations.
* Contractual requirements.
* Security and privacy obligations.
* Subscription lifecycle.
* Backup retention.
* Whether the file can be regenerated.
* Whether the file is referenced by another record.

Do not apply one global retention period to all file categories without an approved rationale.

### 10.2 Cleanup job design

Automated cleanup jobs must:

1. Identify candidates using the approved policy.
2. Verify ownership and scope.
3. Check references and retention holds.
4. Confirm that the file is still eligible.
5. Mark or stage the deletion where required.
6. Delete content using the approved mechanism.
7. Update metadata consistently.
8. Record success or failure.
9. Support safe retries.
10. Report unresolved discrepancies.

Use bounded batches to prevent cleanup jobs from exhausting database, CPU, or storage resources.

### 10.3 Orphaned files

An orphaned file may exist in storage without a valid metadata reference. A metadata record may also reference missing content.

Reconciliation must identify both conditions.

Before deleting an orphan:

* Verify that it is not part of an active upload.
* Check for valid references not represented in the expected metadata index.
* Consider replication or delayed consistency where applicable.
* Confirm that no recovery or retention hold applies.
* Record the cleanup decision.

Do not automatically delete every unreferenced object without a validated grace period and safe ownership checks.

### 10.4 Failed cleanup

When cleanup fails:

* Preserve the file's actual state accurately.
* Avoid reporting deletion as complete.
* Record the failure category.
* Retry only according to the approved policy.
* Alert when the backlog or delay exceeds the defined operational limit.
* Reconcile metadata and content before manual intervention.

### 10.5 Subscription-related deletion

Files associated with a restaurant network must follow the platform's subscription and data lifecycle policy.

Before permanent deletion, revalidate:

* Tenant identity.
* Applicable expiration and waiting-period rules.
* Current subscription and account state.
* Reactivation status.
* Retention holds.
* Approved deletion scope.
* Related business records and required dependencies.

A stale deletion job must not delete files after the account becomes ineligible for deletion.

Follow `16_Subscription_and_Data_Lifecycle_Operations.md`.

## 11. Backup and Recovery

### 11.1 Backup scope

The backup strategy must identify which items require protection:

* File content.
* File metadata.
* Storage configuration.
* Access-control configuration.
* Encryption and key-management dependencies.
* Required indexes or manifests.
* Relationships between files and business records.

The strategy must define recovery objectives for critical file categories.

### 11.2 Consistency between metadata and content

Database and file storage backups may be taken at different times.

The recovery procedure must account for this difference and prevent restored metadata from pointing to unavailable files or restored files from becoming incorrectly associated with business records.

Where required, use manifests, consistent snapshots, versioning, replication, or another approved coordination mechanism.

### 11.3 Recovery procedure

During a file recovery:

1. Identify the affected storage location and file categories.
2. Determine the scope and recovery point.
3. Confirm authorization and incident ownership.
4. Identify the verified backup or recoverable version.
5. Restore to an approved recovery location where practical.
6. Verify artifact integrity.
7. Restore or reconcile metadata.
8. Verify tenant and branch ownership.
9. Confirm access controls and encryption.
10. Test retrieval through the application.
11. Reconcile missing and orphaned records.
12. Record the result and any residual gaps.

Avoid overwriting healthy production content during an unverified recovery.

### 11.4 Recovery validation

Recovery must verify:

* Expected files exist.
* Integrity checks pass where available.
* Metadata references are valid.
* Authorized users can retrieve permitted files.
* Unauthorized users cannot retrieve them.
* File associations and tenant boundaries are correct.
* Required files are not silently missing.
* Retention and deletion states remain correct.

A successful storage restore command is not sufficient proof of application-level recovery.

### 11.5 Versioning and soft deletion

Where supported, object versioning or soft deletion may improve recovery.

These mechanisms do not replace retention management. Old versions may contain sensitive data and must have explicit access and cleanup rules.

## 12. Migration and Storage Changes

Storage migrations may include moving between directories, disks, storage providers, or object-storage namespaces.

Before migration:

1. Inventory the source and target.
2. Confirm capacity and permissions.
3. Verify encryption and access controls.
4. Define the migration and rollback plan.
5. Identify how writes will be coordinated during migration.
6. Verify metadata and content consistency.
7. Test representative downloads and uploads.
8. Confirm that application references remain valid.
9. Monitor failures and latency.
10. Retain the old copy until verification and rollback requirements are satisfied.

Do not remove the original data merely because the copy operation completed.

Any migration that changes file identifiers, URLs, or authorization mechanisms must include compatibility and access-control testing.

## 13. Troubleshooting Procedures

### 13.1 Upload failures

Check:

* Authentication and authorization.
* File size and type limits.
* Network interruption.
* Storage availability and permissions.
* Quarantine or scanning status.
* Application and proxy timeouts.
* Storage quota.
* Metadata transaction errors.
* Whether the upload completed despite a client timeout.

Do not blindly retry if the original upload may already exist.

### 13.2 Download failures

Check:

* File metadata and lifecycle state.
* Storage object existence.
* Tenant and branch authorization.
* Signed URL validity where applicable.
* Storage permissions.
* Proxy or cache behavior.
* Encryption key availability.
* Content delivery errors.

Do not make a private object public as a troubleshooting shortcut.

### 13.3 File exists but application reports it missing

Check the metadata reference, storage namespace, object version, environment configuration, and recent migrations.

Verify whether the object is present but inaccessible, incorrectly referenced, or genuinely missing.

Reconcile the metadata and storage state using the approved recovery procedure.

### 13.4 Application references a missing file

Identify the affected business records and the missing file's role.

Determine whether the content can be restored from a verified backup or regenerated safely.

Do not silently replace an important original document with an unrelated file or empty placeholder.

### 13.5 Storage is nearly full

1. Confirm current usage and growth rate.
2. Identify the largest storage categories.
3. Check temporary files, failed uploads, and cleanup backlog.
4. Identify expired files eligible for removal.
5. Verify retention holds and ownership.
6. Apply safe cleanup or capacity expansion.
7. Monitor storage usage and application errors.

Do not delete business records or backups indiscriminately to free space.

### 13.6 Cleanup job deletes or threatens valid files

Stop or pause the affected cleanup process using the approved operational procedure.

Preserve logs and candidate lists. Determine whether deletion was only scheduled, logically applied, or physically completed.

Restore affected files where possible, reconcile metadata, assess business impact, and correct the eligibility logic before restarting cleanup.

### 13.7 Suspected unauthorized access

Follow the security incident process.

Preserve access logs and relevant metadata, restrict the affected access path, review issued access URLs or tokens where applicable, and identify the affected tenants and files.

Do not expose the affected documents further during investigation.

## 14. Security Operations

### 14.1 Least privilege

Use separate permissions for upload, download, cleanup, scanning, backup, and recovery where practical.

Service identities must have only the storage permissions required for their responsibilities.

### 14.2 Encryption

Apply encryption in transit and at rest according to the data classification and approved infrastructure design.

Protect encryption keys separately from the stored content and document the recovery dependencies.

### 14.3 Access logging

Record relevant access and administrative events according to the audit policy, including:

* Sensitive file downloads.
* Permission changes.
* Public-access configuration changes.
* Deletion and recovery actions.
* Bulk exports.
* Manual storage interventions.

Avoid recording the full contents of files in operational logs.

### 14.4 Temporary access

Temporary access mechanisms must have limited scope, appropriate expiration, and protection against unintended sharing.

If an access mechanism cannot be revoked immediately, its risk and expiration behavior must be documented.

### 14.5 Separation of environments

Production files must not be copied into development or testing environments unless explicitly authorized and appropriately protected.

Where realistic test data is required, use sanitized or synthetic content whenever feasible.

## 15. Operational Evidence

For significant storage incidents, migrations, cleanup operations, or recoveries, retain applicable evidence:

* Storage location and object identifiers.
* Affected tenant and branch scope.
* Relevant metadata references.
* File integrity results.
* Cleanup candidate and outcome records.
* Backup and restore references.
* Operator and approval details.
* Timestamps and relevant error summaries.
* Access-control verification results.
* Reconciliation findings.
* Corrective actions and ownership.

Evidence must follow the approved retention and access-control policy.

## 16. Operational Readiness Checklist

### Routine operation

* [ ] Storage inventory is current.
* [ ] Access controls are enforced.
* [ ] Capacity and growth are monitored.
* [ ] Upload validation is active.
* [ ] Cleanup jobs are bounded and monitored.
* [ ] Retention rules are documented.
* [ ] File and metadata consistency is monitored.
* [ ] Sensitive access is logged appropriately.

### Before cleanup or migration

* [ ] Scope and eligibility rules are verified.
* [ ] References and retention holds are checked.
* [ ] Backup or recovery requirements are satisfied.
* [ ] The operation can be safely retried.
* [ ] Impact and rollback limits are understood.
* [ ] Required authorization is recorded.

### After recovery

* [ ] Expected files are restored.
* [ ] Integrity checks pass.
* [ ] Metadata references are reconciled.
* [ ] Tenant and branch boundaries are verified.
* [ ] Application-level retrieval succeeds.
* [ ] Unauthorized access remains blocked.
* [ ] Missing and orphaned content is assessed.
* [ ] Recovery evidence is recorded.

## 17. Related Documents

* `README.md` — Operations documentation index.
* `03_Monitoring_and_Observability_Operations.md` — Monitoring and observability.
* `05_Incident_Management.md` — Incident handling and recovery.
* `07_Backup_Verification_and_Restore_Operations.md` — Backup verification and restore drills.
* `08_Disaster_Recovery_Operations_Runbook.md` — Disaster recovery.
* `09_Database_Operations.md` — Database operations.
* `13_Background_Worker_and_Scheduler_Operations.md` — Cleanup workers and scheduled tasks.
* `14_AI_Runtime_Operations.md` — AI runtime and AI file handling.
* `16_Subscription_and_Data_Lifecycle_Operations.md` — Subscription and data lifecycle.
* `17_Security_Operations.md` — Security operations.
* `18_Release_and_Change_Operations.md` — Release and change management.
* `20_Operations_Invariants_and_Guardrails.md` — Mandatory operational guardrails.

## 18. Mandatory Operational Invariants

1. Every production storage location must have a documented purpose and owner.
2. Every important file category must have a defined retention policy.
3. Private business files must not be publicly accessible by default.
4. File identifiers and storage paths must not substitute for authorization.
5. Tenant isolation must be enforced for file operations.
6. Branch-specific file access must follow branch permissions.
7. File metadata and content consistency must be considered together.
8. Files must not become available before required validation completes.
9. Client-provided filenames must not control unsafe storage paths.
10. Declared MIME types and extensions must not be trusted alone.
11. Upload size and content restrictions must be enforced.
12. Required malware scanning must not be silently bypassed.
13. Failed uploads must not be represented as completed.
14. Upload retries must account for possible prior completion.
15. Private files must not be exposed through shared public caches.
16. Temporary access links must have controlled scope and lifetime.
17. Revocation limitations must be documented for issued access links.
18. Sensitive downloads and administrative actions must follow audit policy.
19. File operations must use bounded resource consumption.
20. Large files must not be loaded unnecessarily into application memory.
21. Spreadsheet imports must be validated before business records are modified.
22. Preview generation must not execute untrusted active content.
23. Cleanup must verify eligibility before deletion.
24. Cleanup must respect retention holds.
25. Cleanup must verify ownership and tenant scope.
26. Orphaned files must not be deleted without a validated procedure.
27. Metadata must not claim successful deletion before the required operation completes.
28. Cleanup jobs must be safe to retry.
29. Permanent deletion must follow the approved data lifecycle policy.
30. Subscription-related deletion must revalidate current eligibility.
31. Reactivation must be considered before subscription-related deletion.
32. File and database recovery must account for inconsistent backup times.
33. Restored files must be checked for integrity where supported.
34. Restored metadata must reference the correct content.
35. Recovery must preserve tenant and branch ownership.
36. Storage restoration must not expose private files.
37. Healthy production content must not be overwritten by unverified recovery.
38. Migrations must preserve references and authorization.
39. Original content must not be removed before migration verification.
40. Backup retention must account for sensitive historical file versions.
41. Production files must not be copied into lower environments without authorization.
42. Encryption keys must be protected and their recovery dependencies documented.
43. Storage exhaustion must not be resolved through indiscriminate deletion.
44. Suspected unauthorized access must trigger the security incident process.
45. File recovery must verify application-level access.
46. Generated files must not be considered disposable solely because they can be regenerated.
47. Manual storage changes must be authorized and traceable.
48. Operational evidence must not unnecessarily reproduce sensitive file contents.
49. Storage procedures must be reviewed when the architecture or retention policy changes.
50. Any storage operation that risks unauthorized disclosure, irreversible data loss, or cross-tenant access must stop until a safe path is established.

## 19. Acceptance Criteria

This document is accepted for operational use when:

* Storage locations and file categories are inventoried.
* Upload and download authorization is documented.
* Validation and file-security controls are defined.
* Retention, cleanup, and deletion safeguards are established.
* Backup and recovery procedures include metadata consistency.
* Storage capacity and performance are monitored.
* Tenant and branch isolation requirements are explicit.
* Operational troubleshooting and evidence requirements are documented.
* Related security, database, lifecycle, and disaster-recovery documents remain consistent.

**End of document.**

