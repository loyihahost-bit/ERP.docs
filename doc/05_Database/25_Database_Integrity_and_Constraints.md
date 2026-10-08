    # Database Integrity and Constraints

**Document ID:** DB-25
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/05_Database/README.md`

---

## 1. Purpose

This document defines the database-level integrity rules and constraints for FastFood ERP.

The database must protect critical business data from:

* invalid references;
* cross-business data leakage;
* cross-branch corruption;
* duplicate identities;
* invalid state combinations;
* negative inventory;
* invalid financial values;
* invalid lifecycle transitions;
* accidental historical modification;
* concurrent write conflicts;
* duplicate synchronization operations;
* inconsistent configuration versions.

Database constraints are a critical safety boundary.

They do not replace application-level business logic.

---

## 2. Scope

This document covers:

* Primary Keys;
* Foreign Keys;
* NOT NULL constraints;
* UNIQUE constraints;
* composite UNIQUE constraints;
* partial UNIQUE constraints;
* CHECK constraints;
* reference data;
* tenant isolation;
* branch isolation;
* ownership consistency;
* Product integrity;
* Recipe integrity;
* Set integrity;
* Inventory integrity;
* Order integrity;
* Payment integrity;
* Debt integrity;
* Cash Register integrity;
* Cash Session integrity;
* Shift Handover integrity;
* Attendance integrity;
* Payroll integrity;
* Configuration integrity;
* Audit integrity;
* Report integrity;
* Notification integrity;
* Offline and synchronization integrity;
* lifecycle and deletion integrity;
* monetary precision;
* quantity precision;
* timestamps;
* optimistic concurrency;
* transaction boundaries;
* database triggers;
* deferred constraints;
* migration compatibility;
* integrity testing.

---

# 3. Integrity Principles

The database must follow these principles:

1. Invalid references must not be persisted.
2. Required values must not be NULL.
3. Identity values must be unique within their required scope.
4. Business-owned records must remain associated with the correct Business.
5. Branch-owned records must remain associated with the correct Branch.
6. Cross-Business references must be prohibited.
7. Critical numeric values must have valid ranges.
8. Historical records must not be silently overwritten.
9. Duplicate operations must be prevented.
10. Critical concurrent operations must be protected.
11. Database constraints must remain understandable.
12. Business rules that cannot be represented safely as constraints must remain in application/domain logic.
13. Integrity failures must fail safely.
14. Integrity rules must remain testable.
15. Migrations must not silently weaken existing integrity.

---

# 4. Integrity Layers

FastFood ERP uses multiple integrity layers.

```text
Application / Domain Validation
        ↓
Transaction / Concurrency Rules
        ↓
Database Constraints
        ↓
PostgreSQL Storage
```

The layers have different responsibilities.

### Database layer

Protects structural integrity.

Examples:

* FK;
* NOT NULL;
* UNIQUE;
* CHECK;
* primary keys;
* exclusion constraints where justified.

### Application layer

Protects business semantics.

Examples:

* whether an employee has permission;
* whether a discount is allowed;
* whether a refund requires approval;
* whether a Product may currently be sold.

### Transaction layer

Protects atomic business operations.

Examples:

* Order acceptance + inventory deduction;
* payment + session update;
* cash session close;
* synchronization idempotency.

---

# 5. PostgreSQL Authority

PostgreSQL is the authoritative persistence layer.

The application must not assume that client-side validation is sufficient.

All important writes must pass through database integrity constraints.

Client validation may improve UX, but it must not be considered a security boundary.

---

# 6. Primary Key Strategy

Every persistent domain entity must have a stable primary key.

The preferred identity is UUID.

Example:

```text
business.uuid
branch.uuid
employee.uuid
product.uuid
order.uuid
payment.uuid
cash_session.uuid
```

Primary keys must:

* be NOT NULL;
* be unique;
* remain stable;
* not be reused.

---

# 7. UUID Stability

A UUID assigned to a domain entity must not change during the entity lifecycle.

Changing display names, codes, statuses or configuration does not change the UUID.

Historical records must continue referencing the original UUID.

---

# 8. UUID Reuse

Deleted Business UUIDs, Product UUIDs, Order UUIDs, Payment UUIDs and other historical identities must never be reused.

UUID generation must provide sufficient uniqueness.

---

# 9. Foreign Key Integrity

Foreign keys must be used whenever a persistent relationship requires database-level referential integrity.

Example:

```text
branch.business_uuid
    → business.uuid
```

A child record must not reference a nonexistent parent.

---

# 10. Foreign Key Deletion Policy

Foreign key deletion behavior must be explicitly selected.

The system must not rely on accidental database defaults.

Typical behavior:

```text
RESTRICT
NO ACTION
```

must be preferred for important historical entities.

---

# 11. Controlled Cascade

`ON DELETE CASCADE` may only be used for tightly bounded dependent records where deletion is explicitly safe.

Examples may include:

* temporary child records;
* ephemeral synchronization details;
* tightly coupled configuration children.

It must not be used for unrestricted Business-level deletion.

---

# 12. Business-Level Deletion

Business deletion must not be implemented as:

```sql
DELETE FROM business
WHERE uuid = ...;
```

with uncontrolled cascading.

Business deletion is a lifecycle operation governed by:

* deletion eligibility;
* retention;
* deletion job;
* dependency order;
* audit;
* verification;
* resumability.

---

# 13. NOT NULL

Required fields must use `NOT NULL`.

Examples:

```text
business.uuid
business.status
branch.business_uuid
branch.name
employee.business_uuid
employee.status
product.business_uuid
product.name
order.business_uuid
order.branch_uuid
order.status
```

Nullable fields must have a documented semantic meaning.

---

# 14. Nullable Field Rule

A field must not be nullable merely because the application does not currently populate it.

NULL should mean:

> value is genuinely unknown, unavailable, not applicable, or intentionally absent.

Empty strings must not be used as a replacement for NULL where NULL semantics are required.

---

# 15. UNIQUE Constraints

Unique constraints must protect identities that cannot legitimately duplicate.

Examples:

* Business slug/code;
* branch code within Business;
* employee login identifier where globally unique;
* device identifier;
* payment operation UUID;
* synchronization event UUID.

---

# 16. Composite UNIQUE Constraints

Composite uniqueness must be used when uniqueness depends on multiple dimensions.

Example:

```text
(branch_uuid, code)
```

A branch may have the same local code as another Branch.

Another example:

```text
(business_uuid, product_code)
```

---

# 17. Tenant-Scoped Uniqueness

Business-owned identifiers must generally be unique within Business.

Example:

```text
UNIQUE (business_uuid, code)
```

This prevents unrelated Businesses from affecting each other.

---

# 18. Branch-Scoped Uniqueness

Branch-local identifiers must generally use:

```text
UNIQUE (branch_uuid, code)
```

Examples:

* table number;
* local printer code;
* local warehouse code;
* local register code where applicable.

---

# 19. Partial UNIQUE Constraints

Partial unique indexes may be used when only active records must be unique.

Example:

```sql
CREATE UNIQUE INDEX ...
ON employee (...)
WHERE status = 'ACTIVE';
```

The exact usage must be justified for each entity.

---

# 20. CHECK Constraints

CHECK constraints should protect simple deterministic invariants.

Examples:

```text
amount >= 0
quantity > 0
markup_percent BETWEEN 0 AND 100
start_time < end_time
```

CHECK constraints must not contain complex business workflows.

---

# 21. Enum and Reference Values

Finite state values may be represented using:

* PostgreSQL enum;
* controlled reference tables;
* constrained text values.

The selected approach must remain migration-friendly.

For highly changeable business configuration, reference tables are preferred over rigid database enums.

---

# 22. Status Integrity

Status fields must contain only valid values.

Invalid arbitrary strings must not be accepted where a finite state model exists.

Example:

```text
Order:
DRAFT
ACCEPTED
PREPARING
READY
SERVED
CANCELLED
```

The exact lifecycle transitions remain application-level rules.

The database protects valid state values.

---

# 23. State Transition Integrity

A CHECK constraint alone must not attempt to encode every state transition.

For example:

```text
DRAFT → ACCEPTED
```

is a business operation.

The database may enforce that `status` is a valid state, while the application/service layer validates whether the transition is permitted.

---

# 24. Business Ownership

Every Business-owned record must be traceable to exactly one Business.

The relationship may be:

```text
Direct:
record.business_uuid

or

Indirect:
record.branch_uuid → branch.business_uuid
```

The ownership model must remain unambiguous.

---

# 25. Business Boundary Integrity

A record belonging to Business A must never reference a Business B parent.

Example:

```text
Order(Business A)
    ↓
Branch(Business A)
```

must be valid.

This must never be allowed:

```text
Order(Business A)
    ↓
Branch(Business B)
```

---

# 26. Cross-Business Foreign Keys

Where possible, cross-business integrity should be enforced at database level.

A simple FK is insufficient when the referenced table can belong to another Business.

For critical relationships, composite ownership-aware references should be considered.

Example:

```text
(branch_uuid, business_uuid)
    →
(branch.uuid, branch.business_uuid)
```

This prevents a Branch from being referenced across Business boundaries.

---

# 27. Business-Scoped Composite References

When tenant isolation is critical, related tables may include Business UUID even when it can technically be derived.

Example:

```text
order:
    uuid
    business_uuid
    branch_uuid
```

This controlled denormalization allows stronger database-level ownership validation.

---

# 28. Redundant Ownership Fields

Duplicated Business UUID fields are allowed when they materially improve:

* tenant isolation;
* query safety;
* indexing;
* authorization context;
* integrity enforcement.

The duplicated value must remain consistent with its parent.

---

# 29. Branch Ownership

Every Branch must belong to exactly one Business.

A Branch cannot exist without a Business.

A Branch cannot move between Businesses through a normal update.

If migration between Businesses is ever supported, it must be an explicit administrative operation with dedicated rules.

---

# 30. Employee Ownership

Every Employee must belong to exactly one Business.

Employee Branch assignments must reference Branches belonging to the same Business.

An Employee cannot be assigned to a Branch belonging to another Business.

---

# 31. Employee Branch Assignment

Employee-to-Branch relationships should use a dedicated association table.

Example:

```text
employee_branch
```

Recommended uniqueness:

```text
UNIQUE(employee_uuid, branch_uuid)
```

---

# 32. Employee Active State

Employee status must be constrained to valid lifecycle values.

Example:

```text
CREATED
ACTIVE
INACTIVE
```

The database must prevent arbitrary invalid status values.

---

# 33. Device Ownership

Every trusted Device must belong to exactly one Business.

If a Device is Branch-scoped, the Branch must belong to the same Business.

Invalid relationship:

```text
Device(Business A)
Branch(Business B)
```

---

# 34. Device Identity

A device identity must be unique according to its defined trust scope.

Device identifiers must not allow accidental duplication of a trusted device.

Revoked devices remain historically identifiable.

---

# 35. Subscription Ownership

A Subscription must belong to exactly one Business.

A Subscription must not reference a Branch-owned entity unless explicitly required by the model.

Subscription and Business lifecycle must remain separate concepts.

---

# 36. Subscription Entitlement Integrity

Entitlement data must reference valid:

* Business;
* tariff/plan;
* feature;
* effective period.

The database must not allow an entitlement with an invalid Business or feature reference.

---

# 37. Product Ownership

Every Product must belong to exactly one Business.

A Product must not be shared between Businesses.

---

# 38. Product Category Integrity

Every Product must belong to exactly one valid category.

The category must belong to the same Business.

Invalid:

```text
Product(Business A)
Category(Business B)
```

---

# 39. Product Category Uniqueness

Category names/codes should be unique according to Business scope.

Recommended:

```text
UNIQUE(business_uuid, code)
```

---

# 40. Product Identity Preservation

Changing:

* name;
* category;
* image;
* active state;
* price configuration

must not create a new Product identity unless the business explicitly creates a new Product.

---

# 41. Product Active State

Inactive Products may remain referenced by historical records.

Therefore historical FKs must not be removed merely because a Product becomes inactive.

---

# 42. Recipe Ownership

Every Recipe must belong to the same Business as its Product.

A Recipe cannot reference a Product belonging to another Business.

---

# 43. Recipe Version Ownership

Every Recipe Version must belong to exactly one Recipe.

Its Product relationship must remain consistent with the parent Recipe.

---

# 44. Recipe Version Number

Recipe version numbers must be unique within the Recipe.

Example:

```text
UNIQUE(recipe_uuid, version_number)
```

---

# 45. Recipe Component Integrity

A Recipe Component must reference a valid Product.

The component Product must belong to the same Business as the Recipe.

---

# 46. Recipe Self-Reference

Direct self-reference must be prohibited.

Example:

```text
Product A
Recipe A
    → Product A
```

must not be accepted when the product cannot legally consume itself.

---

# 47. Recipe Cycle Detection

Arbitrary recursive recipe cycles cannot reliably be prevented using simple CHECK constraints.

Cycle detection belongs to application/domain validation.

The database must still preserve ownership and reference integrity.

---

# 48. Recipe Quantity

Recipe component quantity must be greater than zero.

Recommended:

```text
quantity > 0
```

---

# 49. Recipe Unit Integrity

Recipe component units must be compatible with the Product's inventory unit model.

Conversion rules belong to domain logic.

The database protects the presence and validity of the stored unit representation.

---

# 50. Set Ownership

Every Set must belong to exactly one Business.

Set components must belong to the same Business.

---

# 51. Set Version Integrity

Set versions must:

* reference an existing Set;
* use unique version numbers;
* preserve historical versions.

Recommended:

```text
UNIQUE(set_uuid, version_number)
```

---

# 52. Set Component Integrity

A Set Component must reference a valid Product or valid permitted component type.

The database must prevent dangling component references.

---

# 53. Set Component Quantity

Set component quantity must be greater than zero.

---

# 54. Set Component Substitution

The database should not attempt to model arbitrary runtime substitution as a simple FK update.

Normal Set sale does not allow component substitution.

Any exceptional workflow must use an explicit business operation.

---

# 55. Inventory Ownership

Inventory records must be scoped to:

```text
Business
Branch
Warehouse
Product
```

according to the defined inventory model.

---

# 56. Warehouse Ownership

Every Warehouse must belong to exactly one Branch or Business scope according to its defined type.

A Branch Warehouse must reference a Branch belonging to the same Business.

---

# 57. Inventory Product Ownership

An Inventory Balance must not reference a Product belonging to another Business.

---

# 58. Inventory Quantity

Stored inventory quantity must not become negative.

At minimum:

```text
quantity >= 0
```

must be protected where the row represents current stock.

---

# 59. Inventory Transaction Quantity

Inventory movement quantities must be strictly positive.

Direction is represented separately.

Example:

```text
quantity > 0
direction = IN
```

or:

```text
quantity > 0
direction = OUT
```

---

# 60. Inventory Transaction Direction

Inventory movement direction must contain only valid values.

Example:

```text
IN
OUT
ADJUSTMENT
RETURN
PRODUCTION
CONSUMPTION
```

The exact list is controlled by the inventory model.

---

# 61. Inventory Balance and Transaction Relationship

Inventory Balance represents current state.

Inventory Transaction represents historical movement.

The system must not rewrite historical inventory transactions merely to correct the current balance.

---

# 62. Inventory Correction

Inventory correction must create a new transaction or correction record.

It must not silently overwrite the original movement.

---

# 63. Inventory Concurrency

Inventory decrement operations must use appropriate transaction locking.

A CHECK constraint alone cannot prevent two concurrent transactions from both consuming the same final stock.

---

# 64. Atomic Stock Decrement

The application must perform stock validation and decrement atomically.

Conceptually:

```sql
UPDATE inventory_balance
SET quantity = quantity - :requested
WHERE uuid = :inventory_uuid
  AND quantity >= :requested;
```

The affected-row count must be validated.

---

# 65. Order Ownership

Every Order must belong to exactly one Business.

Every Branch-linked Order must reference a Branch belonging to that Business.

---

# 66. Order Branch Integrity

An Order cannot move between Branches during normal lifecycle.

Branch changes must not be used to alter historical ownership.

---

# 67. Order Status

Order status must be constrained to the defined lifecycle states.

Example:

```text
DRAFT
ACCEPTED
PREPARING
READY
SERVED
CANCELLED
```

---

# 68. Order Item Ownership

Every Order Item must reference an existing Order.

Its Product/Set must belong to the same Business as the Order.

---

# 69. Order Item Product/Set Exclusivity

An Order Item must represent either:

* a Product;
* a Set;

but not both.

Conceptually:

```text
product_uuid IS NOT NULL
XOR
set_uuid IS NOT NULL
```

This is a suitable CHECK constraint.

---

# 70. Order Item Quantity

Order Item quantity must be greater than zero.

Historical quantity must not be silently changed after the financial transaction becomes authoritative.

---

# 71. Order Item Price

Order Item selling price must be stored as a historical snapshot.

It must not depend on the current Product price after creation.

---

# 72. Order Item Financial Values

Amounts must use appropriate monetary precision.

Recommended conceptual fields:

```text
unit_price
quantity
discount_amount
line_total
```

The database must prevent invalid negative values unless the field explicitly represents a signed adjustment.

---

# 73. Order Total

Order total must remain consistent with authoritative financial snapshots.

Derived totals may be recalculated by application logic.

Critical historical totals must not depend on current configuration.

---

# 74. Order Number

Customer-facing order numbers may reset per Cash Session.

Therefore uniqueness must use the appropriate scope.

Example:

```text
UNIQUE(cash_session_uuid, display_order_number)
```

---

# 75. Table Visit Integrity

A Table Visit/Session must belong to the same Branch as its Table.

An Order linked to a Table Visit must belong to the same Branch.

---

# 76. Table Number Uniqueness

Table identifiers must be unique within their Branch.

Example:

```text
UNIQUE(branch_uuid, table_number)
```

---

# 77. Payment Ownership

Every Payment must reference:

* Business;
* Branch;
* Order;
* actor context where required.

All referenced entities must belong to the same Business.

---

# 78. Payment Amount

Payment amount must be greater than zero unless a specific zero-value transaction type is explicitly supported.

---

# 79. Payment Method

Payment method must be constrained to supported values.

Current methods include:

```text
CASH
CARD
DEBT
MIXED
```

---

# 80. Payment Status

Payment status must contain only valid values.

Example:

```text
PENDING
COMPLETED
CANCELLED
```

Exact lifecycle may be expanded later.

---

# 81. Payment Idempotency

Every payment creation operation must have a unique operation identity.

Example:

```text
UNIQUE(payment_operation_uuid)
```

Repeated requests must not create duplicate payments.

---

# 82. Payment Order Consistency

A Payment may only reference an Order belonging to the same Business and Branch context.

---

# 83. Payment Session Consistency

When a Payment is associated with a Cash Session:

```text
Payment.Branch = CashSession.Branch
```

must hold.

---

# 84. Debt Customer Ownership

A Debt Customer belongs to one Business.

The same phone number may exist for multiple debt customers.

Therefore phone number must not necessarily be globally unique.

---

# 85. Debt Order Integrity

A debt record must reference:

* Business;
* Order;
* Debt Customer.

All must belong to the same Business.

---

# 86. Debt Repayment

Debt repayment amounts must be greater than zero.

Repayment cannot reference another Business.

---

# 87. Debt Balance

Debt balance must not become negative through ordinary repayment.

Concurrency must be handled at transaction level.

---

# 88. Refund Integrity

A Refund must reference the original Payment or Order transaction according to the domain model.

It must remain within the same Business.

---

# 89. Refund Amount

Refund amount must be:

```text
> 0
```

and must not exceed the refundable amount unless an explicit correction mechanism exists.

The latter is application-level validation.

---

# 90. Refund History

Original payment data must not be overwritten by refund processing.

Refund is a separate historical transaction.

---

# 91. Discount Integrity

Discount records must belong to the same Business and Order.

Discount amounts must not be negative.

Discount percentage, if stored, must have a valid range.

---

# 92. Custom Markup

Custom markup must satisfy:

```text
0 <= markup_percent <= 100
```

This may be protected by a CHECK constraint.

---

# 93. Cash Register Ownership

Every Cash Register belongs to exactly one Branch.

A Cash Register cannot reference a different Business through its Branch.

---

# 94. Cash Register Uniqueness

Current business assumptions use one primary Cash Register per Branch.

If only one active register is allowed, a partial unique constraint should enforce it.

Example:

```text
UNIQUE(branch_uuid)
WHERE active = true
```

If multiple registers become supported later, the constraint must be migrated explicitly.

---

# 95. Cash Session Ownership

Every Cash Session must belong to:

```text
Business
Branch
Cash Register
Cashier
```

The references must be ownership-consistent.

---

# 96. Active Cash Session

Only one active Cash Session may exist for a Branch/Register combination where the business model permits one active session.

A partial unique index should be preferred.

Conceptually:

```sql
UNIQUE(register_uuid)
WHERE status = 'OPEN';
```

---

# 97. Cash Session Amounts

Expected and actual cash values must use monetary precision.

Actual cash may be zero.

Negative physical cash is invalid.

---

# 98. Cash Session Difference

Difference may be:

```text
positive
zero
negative
```

because it represents:

```text
actual - expected
```

Therefore it must not use a generic `>= 0` constraint.

---

# 99. Cash Session Close

A closed Cash Session must not return to `OPEN`.

The database should prevent invalid final-state rewrites where possible.

Administrative correction must use a separate operation.

---

# 100. Cash Session Correction

Corrections must reference the original Cash Session.

The original closing result must remain historical.

---

# 101. Cash Session Correction Count

If correction count is stored directly, it must not be negative.

The maximum correction rule is primarily application/domain logic and authorization logic.

---

# 102. Shift Handover Integrity

A Handover must reference:

* previous Employee;
* next Employee;
* previous Cash Session;
* new Cash Session where applicable.

All must belong to the same Business and Branch.

---

# 103. Handover Employee Validation

The database must prevent a handover from referencing an Employee from another Business.

Branch assignment eligibility remains application-level validation.

---

# 104. Attendance Integrity

Attendance records must reference an Employee belonging to the same Business.

Branch-specific attendance must reference an Employee Branch assignment that belongs to the same Business.

---

# 105. Attendance Time Integrity

Where both timestamps exist:

```text
clock_in <= clock_out
```

must hold.

This may be represented using a CHECK constraint.

---

# 106. Payroll Ownership

Payroll records must belong to the same Business as their Employee.

Branch-specific payroll must remain within the Employee's authorized Branch scope.

---

# 107. Payroll Amounts

Payroll monetary values must use fixed precision.

Negative salary totals must not be allowed unless a separate correction/adjustment type explicitly represents negative adjustments.

---

# 108. Payroll Finalization

Finalized payroll records must not be silently overwritten.

Corrections must create a new record/version or explicit adjustment.

---

# 109. Configuration Ownership

Configuration records must reference the correct:

* Business;
* Branch where applicable;
* entity;
* creator.

---

# 110. Configuration Version Number

Configuration versions must be unique within their configuration stream.

Example:

```text
UNIQUE(configuration_uuid, version_number)
```

---

# 111. Configuration Version Chain

A version may reference its previous version.

The referenced previous version must belong to the same configuration stream.

Cross-stream version references are invalid.

---

# 112. Configuration Effective Time

Configuration timestamps must be valid.

Where both are stored:

```text
created_at <= effective_at
```

must hold.

---

# 113. Configuration State

Configuration state must contain only valid values.

Example:

```text
DRAFT
PENDING_APPROVAL
APPROVED
EFFECTIVE
SUPERSEDED
ARCHIVED
```

---

# 114. Configuration Historical Integrity

Effective historical configuration must not be deleted merely because a newer configuration exists.

---

# 115. Audit Event Identity

Every Audit Event must have a stable UUID.

Audit events must not be duplicated for the same operation where idempotency is required.

---

# 116. Audit Immutability

Audit records must be append-only.

Normal application operations must not:

* update old audit events;
* delete audit events;
* rewrite old event payloads.

---

# 117. Audit Actor

Every important audit event must identify either:

```text
Employee
```

or:

```text
SYSTEM
```

The actor model must be explicit.

---

# 118. Audit Business Ownership

Every Business audit event must contain the Business context.

Branch-scoped audit events must contain the Branch context where applicable.

---

# 119. Report Ownership

Every Report Version must reference its Business.

Branch-specific reports must reference the appropriate Branch.

---

# 120. Report Version Number

Report versions must be unique within the report stream.

Example:

```text
UNIQUE(report_uuid, version_number)
```

---

# 121. Report Immutability

Finalized Report Versions must not be updated.

If report data changes materially, a new version must be created.

---

# 122. Notification Ownership

Notifications must belong to a Business unless they are platform-level notifications.

Branch notifications must belong to a Branch of the same Business.

---

# 123. Notification Recipient Integrity

Notification recipients must reference valid Employees.

Recipient Employee and Notification Business must match.

---

# 124. Notification Read State

A recipient must not have duplicate read-state rows for the same Notification.

Recommended:

```text
UNIQUE(notification_uuid, employee_uuid)
```

---

# 125. Offline Operation Identity

Every offline operation must have a stable operation UUID.

This UUID is the idempotency identity.

---

# 126. Synchronization Event Identity

Synchronization events must use stable identifiers.

Repeated delivery of the same event must not create duplicate domain transactions.

---

# 127. Sync Event Business Ownership

Every synchronization event must identify the Business context.

The server must reject an event whose referenced entities belong to another Business.

---

# 128. Sync Event Device Ownership

A synchronization event referencing a Device must use a Device belonging to the same Business.

---

# 129. Sync Event Employee Ownership

A synchronization event referencing an Employee must use an Employee belonging to the same Business.

---

# 130. Sync Event State

Synchronization states must be constrained.

Example:

```text
PENDING
SYNCING
SYNCED
RETRYING
FAILED
CONFLICT
```

---

# 131. Sync Event Idempotency

A unique constraint must prevent duplicate processing of the same operation identity.

The application must still handle repeated requests safely.

---

# 132. Lifecycle Ownership

Business lifecycle fields must contain only valid states.

Example:

```text
ACTIVE
READ_ONLY
DELETION_ELIGIBLE
DELETING
DELETED
```

---

# 133. Lifecycle State Integrity

Lifecycle transitions are application-controlled.

The database protects valid state values but does not need to encode the complete transition graph in CHECK constraints.

---

# 134. Deletion Eligibility

Deletion eligibility must not be based only on client-provided timestamps.

Server-controlled timestamps must be used.

---

# 135. Retention Period

The configured lifecycle rule currently requires:

```text
60 days
```

between deletion eligibility and permanent deletion when the Business is not reactivated.

The actual job execution remains application/worker logic.

---

# 136. Deleted Business Integrity

A Business marked `DELETED` must not become active again through a normal update.

---

# 137. Deleted Business UUID

Deleted Business UUIDs must never be reused.

---

# 138. Lifecycle Write Protection

Background jobs must validate Business lifecycle before creating new Business-owned records.

A deleting/deleted Business must not receive new normal transactions.

---

# 139. Subscription vs Lifecycle

Subscription status and Business lifecycle status must not be merged into one field.

A Business may be:

```text
ACTIVE + subscription active
ACTIVE + subscription expired
READ_ONLY + subscription expired
DELETION_ELIGIBLE + subscription expired
```

according to the lifecycle model.

---

# 140. Soft Delete

Soft deletion fields must not be interpreted as permanent deletion.

Typical fields:

```text
archived_at
deleted_at
deactivated_at
```

have different meanings.

---

# 141. Archive Integrity

Archived entities may remain referenced by historical records.

The database must preserve those references.

---

# 142. Historical Records

Historical Order, Payment, Inventory, Cash Session, Payroll, Report and Audit records must remain structurally valid after configuration changes.

---

# 143. Historical Product References

Historical transactions may reference inactive Products.

Therefore Product FK deletion must generally be restricted.

---

# 144. Historical Employee References

Historical records may reference inactive Employees.

Employee deactivation must not break historical references.

---

# 145. Historical Price References

Historical transaction price snapshots must not depend on mutable current price tables.

---

# 146. Historical Recipe References

Inventory consumption must be able to identify the Recipe Version used at the time of the operation.

Recipe Version references must therefore remain valid historically.

---

# 147. Historical Configuration References

Historical transactions referencing configuration versions must not lose those versions through ordinary cleanup.

---

# 148. Monetary Data Type

Money must not use floating-point types.

Preferred:

```text
NUMERIC(p,s)
```

with precision selected according to business requirements.

---

# 149. Monetary Scale

All monetary fields representing currency values must use a consistent scale.

The database model must not mix incompatible monetary scales without explicit conversion.

---

# 150. Quantity Data Type

Inventory and recipe quantities should use fixed-precision numeric values where fractional quantities are required.

Example:

```text
NUMERIC(p,s)
```

is preferred over floating-point values.

---

# 151. Percentage Data Type

Percentages must use a defined precision.

Examples:

```text
markup_percent
discount_percent
shrink_percent
```

must not use uncontrolled floating-point representation.

---

# 152. Timestamp Standard

Persistent timestamps should use timezone-aware PostgreSQL timestamps.

Preferred:

```text
TIMESTAMPTZ
```

---

# 153. Server Time Authority

Critical timestamps must be generated or validated using server-controlled time.

Client timestamps may be retained as metadata but must not determine authoritative lifecycle behavior.

---

# 154. Created Timestamp

Persistent records should have:

```text
created_at
```

where historical creation time is relevant.

---

# 155. Updated Timestamp

Mutable configuration records may have:

```text
updated_at
```

Historical immutable records should not depend on continuously changing `updated_at`.

---

# 156. Optimistic Concurrency Version

Mutable configuration entities may contain:

```text
version
```

or equivalent revision number.

The update must validate the expected current version.

---

# 157. Stale Update Protection

Conceptually:

```sql
UPDATE configuration
SET ...
    version = version + 1
WHERE uuid = :uuid
  AND version = :expected_version;
```

Zero affected rows indicates a conflict.

---

# 158. No Silent Last-Write-Wins

Critical business configuration must not silently overwrite a newer version.

Conflict must be returned to the application.

---

# 159. Transaction Ownership

A domain service/use case should own the transaction boundary.

Lower-level repositories must not independently commit critical business operations.

---

# 160. Atomic Order Acceptance

Order acceptance and required inventory deduction must be atomic.

Either:

```text
Order Accepted
+
Inventory Deducted
```

or neither occurs.

---

# 161. Kitchen Event Separation

Kitchen notification/printing is secondary processing.

A printer failure must not roll back the committed Order + Inventory transaction.

---

# 162. Atomic Payment

Payment creation and required payment/session updates must be performed within the appropriate transaction boundary.

---

# 163. Cash Session Close

Cash Session close must atomically persist the authoritative closing state.

Secondary notifications and reports must not determine whether the close itself succeeds.

---

# 164. Inventory Purchase

Purchase receipt and stock increase must be consistent within the core inventory transaction.

---

# 165. Payroll Finalization

Payroll calculation snapshot and finalization state must be committed atomically.

Notifications may execute afterward.

---

# 166. Outbox Integrity

When an Outbox pattern is used, the core transaction and Outbox record must be committed atomically.

Conceptually:

```text
Business Change
+
Outbox Event
```

must succeed together.

---

# 167. Outbox Idempotency

Outbox events must have stable identities.

Workers must safely retry delivery without creating duplicate business effects.

---

# 168. Trigger Policy

Database triggers may be used for narrow structural guarantees.

Good candidates:

* immutable audit protection;
* updated timestamp maintenance;
* structural history protection;
* simple denormalized consistency.

Triggers must not contain large business workflows.

---

# 169. Trigger Avoidance

Business workflows should remain in application/domain services where they require:

* permissions;
* external calls;
* complex branching;
* notifications;
* configuration resolution;
* authorization;
* synchronization decisions.

---

# 170. Immutable Audit Trigger

An append-only audit table may use database-level protections against UPDATE/DELETE.

This provides an additional integrity layer beyond application permissions.

---

# 171. Generated Columns

Generated columns may be used for deterministic derived values.

Examples may include:

* normalized searchable values;
* deterministic signed totals;
* derived flags.

They must not replace complex domain calculations.

---

# 172. Deferred Constraints

Deferrable constraints may be used where a valid multi-step transaction temporarily violates a relationship before reaching its final valid state.

They should be used sparingly.

---

# 173. Immediate Constraints

Normal structural integrity constraints should remain immediate by default.

This makes invalid data fail as early as possible.

---

# 174. Constraint Naming

Database constraints must use predictable names.

Recommended pattern:

```text
pk_<table>
fk_<table>_<column>_<target>
uq_<table>_<columns>
ck_<table>_<rule>
```

Example:

```text
uq_order_cash_session_display_number
ck_order_item_product_or_set
```

---

# 175. Indexes for UNIQUE Constraints

Every important UNIQUE constraint must have an appropriate supporting index.

PostgreSQL normally creates indexes for UNIQUE constraints automatically.

Partial unique rules should use explicit unique indexes.

---

# 176. Foreign Key Indexing

Foreign key columns should generally be indexed when they are frequently used for:

* joins;
* deletion checks;
* tenant filtering;
* Branch filtering;
* synchronization;
* reporting.

---

# 177. Tenant Query Indexing

Business-scoped tables should normally support queries beginning with:

```text
business_uuid
```

where appropriate.

---

# 178. Branch Query Indexing

Branch-heavy operational tables should support:

```text
business_uuid
branch_uuid
```

access patterns where appropriate.

---

# 179. Constraint and Index Separation

A performance index must not be assumed to provide the same semantics as a required integrity constraint.

Integrity must be explicitly represented.

---

# 180. Database-Level Tenant Isolation

Where PostgreSQL Row-Level Security is adopted, policies must enforce Business isolation.

RLS must not be treated as the only authorization mechanism.

Application authorization remains required.

---

# 181. Application Tenant Context

Database queries must receive the correct Business context.

The application must not rely on users supplying Business UUID values manually.

Business context should be derived from authenticated/session context.

---

# 182. Branch Context

Branch context must be validated against:

* authenticated Employee;
* Employee Branch assignment;
* Business;
* permission;
* operation scope.

---

# 183. Background Worker Context

Background jobs must carry explicit Business context where the job is Business-owned.

A worker must never infer Business ownership from arbitrary client data.

---

# 184. Report Query Integrity

Report queries must always apply Business and Branch scope where required.

A reporting query must not accidentally aggregate multiple Businesses.

---

# 185. Export Integrity

Excel exports must use the same tenant and permission scope as the originating report.

---

# 186. Synchronization Integrity

Synchronization endpoints must validate all referenced identities against:

* Business;
* Device;
* Employee;
* Branch;
* subscription/lifecycle state.

---

# 187. Offline Event Rejection

An offline event must be rejected if its Business:

* is deleted;
* is deleting;
* is not authorized for the operation;
* has invalid device context.

---

# 188. Stale Configuration

A stale configuration update must not overwrite a newer server configuration.

---

# 189. Duplicate Synchronization

Repeated synchronization of the same operation UUID must not create duplicate:

* Orders;
* Payments;
* Inventory Transactions;
* Cash Sessions;
* Attendance;
* Payroll operations.

---

# 190. Referential Integrity During Deletion

Before deleting a parent record, all dependent historical references must be evaluated.

If historical integrity requires the parent, deletion must be blocked.

---

# 191. Deletion Dependency Graph

Permanent deletion must follow a dependency-aware sequence.

Example:

```text
Business
  ↓
Operational Children
  ↓
Historical Children
  ↓
Files / External References
  ↓
Business Record
```

The actual order is defined by the lifecycle/deletion system.

---

# 192. Shared Platform Data

Business deletion must never remove shared platform records such as:

* tariff definitions;
* feature definitions;
* global permission definitions;
* platform configuration.

---

# 193. Cross-Business Data Cleanup

Deletion jobs must operate only within the target Business scope.

A deletion job must never use a broad unscoped DELETE.

---

# 194. Bounded Deletion

Large deletion operations must be executed in bounded batches.

This prevents:

* excessive locks;
* long-running transactions;
* transaction log spikes;
* operational disruption.

---

# 195. Deletion Idempotency

Deletion jobs must be safe to retry.

If a batch was already completed, repeating the operation must not corrupt remaining data.

---

# 196. Deletion and Foreign Keys

Foreign key relationships must support controlled deletion.

Where `CASCADE` is unsafe, explicit dependency deletion must be performed.

---

# 197. Constraint Validation During Migration

New constraints should preferably be introduced using safe migration techniques.

For large existing tables:

1. validate existing data;
2. clean invalid rows;
3. add constraint using safe migration strategy;
4. validate;
5. enforce permanently.

---

# 198. Expand and Contract

Schema changes should generally follow:

```text
Expand
  ↓
Deploy compatible code
  ↓
Migrate data
  ↓
Validate
  ↓
Contract
```

Destructive schema changes must not be introduced before dependent application code is compatible.

---

# 199. Constraint Backward Compatibility

A new NOT NULL or CHECK constraint must not be deployed before all existing valid application paths satisfy it.

---

# 200. Migration Safety

Every migration must be:

* deterministic;
* reviewable;
* versioned;
* reversible where practical;
* tested;
* compatible with the deployment strategy.

---

# 201. Integrity Testing

Every critical constraint must have automated tests.

Tests should cover:

* valid insert;
* invalid insert;
* valid update;
* invalid update;
* duplicate insert;
* cross-Business reference;
* cross-Branch reference;
* concurrent operation;
* deletion behavior.

---

# 202. Tenant Isolation Tests

At minimum, tests must verify:

```text
Business A cannot reference Business B data.
Business A cannot read Business B operational rows.
Business A cannot modify Business B rows.
```

This must be tested at:

* repository;
* service;
* API;
* database integration level.

---

# 203. Branch Isolation Tests

Tests must verify:

```text
Branch A configuration
≠
Branch B configuration
```

unless an explicit Business-level configuration applies.

---

# 204. Inventory Integrity Tests

Tests must verify:

* no negative stock;
* concurrent last-unit sale;
* failed deduction rollback;
* duplicate deduction prevention;
* return transaction integrity;
* correction history.

---

# 205. Payment Integrity Tests

Tests must verify:

* duplicate payment rejection;
* cross-Business payment rejection;
* invalid amount rejection;
* refund boundary;
* debt repayment boundary;
* session ownership.

---

# 206. Cash Session Integrity Tests

Tests must verify:

* only one active session;
* concurrent session open;
* invalid close;
* closed session cannot reopen;
* correction does not rewrite original close;
* handover ownership.

---

# 207. Historical Integrity Tests

Tests must verify that changes to:

* Product price;
* Product name;
* Recipe;
* Set;
* category;
* menu availability;
* Employee status

do not corrupt historical transactions.

---

# 208. Synchronization Integrity Tests

Tests must verify:

* duplicate event;
* stale event;
* cross-Business event;
* revoked Device;
* inactive Employee;
* invalid Branch;
* conflict;
* retry after timeout.

---

# 209. Lifecycle Integrity Tests

Tests must verify:

```text
ACTIVE
→ READ_ONLY
→ DELETION_ELIGIBLE
→ DELETING
→ DELETED
```

and verify that:

* deleted Business cannot receive transactions;
* deletion jobs are idempotent;
* reactivation before deletion is possible where permitted;
* deleted UUID is never reused.

---

# 210. Constraint Error Handling

Database integrity failures must be translated into safe application errors.

Examples:

```text
UNIQUE violation
→ Conflict / Duplicate

FOREIGN KEY violation
→ Invalid Reference

CHECK violation
→ Validation Error

Optimistic Version Conflict
→ Conflict
```

Raw database error details must not be exposed to end users.

---

# 211. Security of Constraint Errors

Constraint errors must not reveal sensitive information about another Business.

For example, an error must not expose that a record exists in another tenant.

---

# 212. Constraint Monitoring

Production monitoring should identify repeated integrity failures.

Important categories:

* duplicate operations;
* FK violations;
* CHECK violations;
* optimistic conflicts;
* synchronization conflicts;
* stock concurrency failures.

---

# 213. Integrity Failure Principle

A failed integrity operation must not partially commit critical business state.

Core transaction failures must roll back the relevant transaction.

---

# 214. Secondary Failure Principle

Secondary processing failure must not roll back an already committed core transaction.

Examples:

```text
Order committed
Kitchen printer failed
```

The Order remains committed.

The print operation is retried separately.

---

# 215. Database Connection Integrity

Connection pool configuration must prevent excessive concurrent database load.

Application workers must respect configured database connection limits.

---

# 216. Transaction Timeout

Long-running transactions must be controlled.

Transactions must not remain open while waiting for:

* external APIs;
* printer responses;
* notifications;
* long background processing.

---

# 217. Lock Scope

Database locks must be held only for the minimum required transaction duration.

---

# 218. Deadlock Prevention

Transactions must access shared resources in predictable order.

Example:

```text
Business
→ Branch
→ Register
→ Session
→ Order
→ Inventory
```

The exact order depends on the operation.

---

# 219. Row-Level Locking

Row-level locking should be used for high-contention state such as:

* inventory balances;
* Cash Sessions;
* payment allocation;
* configuration versions.

---

# 220. Serializable Transactions

Serializable isolation should not be used globally by default.

It may be used selectively where business correctness requires it and performance remains acceptable.

---

# 221. Default Isolation

PostgreSQL's default isolation level is the baseline.

Specific high-contention operations may use explicit locks or stronger isolation.

---

# 222. Constraint vs Business Rule

The following should generally remain application/domain rules:

* permission checks;
* subscription entitlement;
* employee authority;
* approval workflow;
* discount approval;
* refund approval;
* recipe cycle validation;
* menu effective session logic;
* state transition authorization;
* offline authorization validity.

---

# 223. Database Constraint Responsibilities

The database should primarily guarantee:

```text
Identity
Reference
Ownership
Uniqueness
Basic State Validity
Numeric Validity
Historical Structure
Concurrency Guardrails
```

---

# 224. Application Responsibilities

The application should guarantee:

```text
Authorization
Workflow
Business Policy
Permission
Subscription Rules
Approval
Conflict Resolution
Configuration Selection
External Integration
```

---

# 225. Integrity Invariants

The following invariants apply to database integrity.

1. Every persistent domain entity has a stable identity.
2. Primary keys are never NULL.
3. Primary keys are unique.
4. UUID identities are never reused.
5. Required fields use NOT NULL.
6. Invalid foreign keys are rejected.
7. Business-owned records remain Business-scoped.
8. Branch-owned records remain Branch-scoped.
9. Cross-Business references are prohibited.
10. Cross-Branch references are prohibited where the relationship is Branch-scoped.
11. Business UUID cannot silently change.
12. Branch UUID cannot silently change ownership.
13. Employee belongs to exactly one Business.
14. Employee Branch assignments remain within the Employee Business.
15. Device belongs to exactly one Business.
16. Device Branch belongs to the same Business.
17. Subscription belongs to exactly one Business.
18. Product belongs to exactly one Business.
19. Product category belongs to the same Business as Product.
20. Product belongs to exactly one category.
21. Recipe belongs to the same Business as Product.
22. Recipe Version belongs to one Recipe.
23. Recipe Version numbers are unique within Recipe.
24. Recipe Components belong to the same Business.
25. Recipe quantities are positive.
26. Invalid direct recipe self-reference is rejected.
27. Recipe cycle detection is performed by domain logic.
28. Set belongs to one Business.
29. Set Version belongs to one Set.
30. Set Version numbers are unique.
31. Set component quantities are positive.
32. Inventory belongs to the correct Business and Branch.
33. Inventory balances cannot become negative.
34. Inventory movements have positive quantities.
35. Inventory direction values are valid.
36. Inventory corrections do not overwrite original movements.
37. Inventory concurrency is protected.
38. Order belongs to one Business.
39. Order Branch belongs to the same Business.
40. Order Branch does not silently change.
41. Order status is valid.
42. Order Item references a valid Order.
43. Order Item Product belongs to the Order Business.
44. Order Item Set belongs to the Order Business.
45. Order Item references either Product or Set.
46. Order Item does not reference both Product and Set.
47. Order Item quantity is positive.
48. Historical Order Item price is preserved.
49. Customer-facing order number is unique within its required session scope.
50. Table belongs to one Branch.
51. Table number is unique within Branch.
52. Payment belongs to the correct Business.
53. Payment references a valid Order.
54. Payment amount is valid.
55. Payment method is valid.
56. Payment status is valid.
57. Payment operation UUID is idempotent.
58. Payment cannot cross Business boundaries.
59. Payment Session belongs to the same Branch.
60. Debt Customer belongs to one Business.
61. Duplicate debt customer phone numbers are permitted.
62. Debt Order belongs to the same Business as Debt Customer.
63. Debt repayment amount is positive.
64. Debt balance cannot become negative through ordinary repayment.
65. Refund belongs to the same Business as its original transaction.
66. Refund amount is positive.
67. Refund does not rewrite the original payment.
68. Discount belongs to the same Business as Order.
69. Discount amount is valid.
70. Markup is between 0% and 100%.
71. Cash Register belongs to one Branch.
72. Active register uniqueness follows the configured model.
73. Cash Session belongs to one Register.
74. Cash Session belongs to the correct Branch.
75. Only one active Cash Session exists where the model requires it.
76. Physical cash cannot be negative.
77. Cash difference may be positive, zero, or negative.
78. Closed Cash Sessions remain historically closed.
79. Cash corrections do not rewrite the original close.
80. Handover references valid Employees.
81. Handover remains within Business.
82. Handover remains within Branch.
83. Attendance belongs to the correct Employee.
84. Attendance timestamps remain logically ordered.
85. Payroll belongs to the correct Business.
86. Payroll belongs to the correct Employee.
87. Payroll monetary values use fixed precision.
88. Finalized payroll is not silently overwritten.
89. Configuration belongs to the correct Business.
90. Branch configuration belongs to the correct Branch.
91. Configuration versions are uniquely numbered.
92. Configuration version chains remain within one configuration stream.
93. Configuration timestamps remain logically ordered.
94. Configuration state values are valid.
95. Historical configuration is not silently deleted.
96. Audit events have stable identities.
97. Audit events are append-only.
98. Audit events identify an actor or SYSTEM.
99. Audit events retain Business context.
100. Report versions belong to the correct Business.
101. Report versions are uniquely numbered.
102. Finalized report versions are immutable.
103. Notification belongs to the correct Business.
104. Branch notification belongs to the correct Branch.
105. Notification recipient belongs to the same Business.
106. Notification recipient state is unique per Notification and Employee.
107. Offline operations have stable operation UUIDs.
108. Synchronization operations are idempotent.
109. Synchronization events remain Business-scoped.
110. Synchronization Device belongs to the same Business.
111. Synchronization Employee belongs to the same Business.
112. Synchronization states are valid.
113. Business lifecycle states are valid.
114. Deleted Business cannot return to active state through normal updates.
115. Deleted Business UUID is never reused.
116. Business lifecycle and Subscription status remain separate.
117. Client time cannot determine authoritative lifecycle.
118. Permanent deletion is dependency-aware.
119. Permanent deletion is bounded.
120. Permanent deletion is idempotent.
121. Shared platform data is not deleted with a Business.
122. Historical references remain valid until controlled deletion.
123. Monetary fields do not use floating point.
124. Quantity fields use appropriate precision.
125. Percentage fields use defined precision.
126. Critical timestamps use timezone-aware storage.
127. Server time is authoritative for lifecycle operations.
128. Optimistic version checks protect mutable configuration.
129. Stale updates are rejected.
130. Critical configuration does not use silent last-write-wins.
131. Core business transactions are atomic.
132. Order acceptance and inventory deduction are atomic.
133. Payment operations are transactionally consistent.
134. Cash Session close is transactionally consistent.
135. Payroll finalization is transactionally consistent.
136. Outbox events commit with the core transaction.
137. Outbox processing is idempotent.
138. Database triggers remain limited to structural guarantees.
139. Complex business workflows remain outside database triggers.
140. Audit immutability may be additionally protected at database level.
141. Deferred constraints are used only where justified.
142. Constraint names follow a predictable convention.
143. Foreign key columns are indexed where required.
144. Tenant query paths are indexed.
145. Branch query paths are indexed.
146. Integrity constraints are explicit.
147. Tenant isolation is tested.
148. Branch isolation is tested.
149. Inventory concurrency is tested.
150. Payment idempotency is tested.
151. Cash Session concurrency is tested.
152. Historical integrity is tested.
153. Synchronization conflicts are tested.
154. Lifecycle transitions are tested.
155. Database errors are translated into safe application errors.
156. Integrity errors do not expose another Business's data.
157. Integrity failures roll back relevant core transactions.
158. Secondary processing failures do not roll back committed core transactions.
159. Database connection usage remains bounded.
160. Transactions do not remain open during external operations.
161. Lock scope remains minimal.
162. Deadlock-prone operations use predictable access order.
163. Row-level locking is used where contention requires it.
164. Serializable isolation is not enabled globally without justification.
165. PostgreSQL default isolation remains the baseline.
166. Permission checks remain application-level.
167. Subscription entitlement remains application-level.
168. Approval workflows remain application-level.
169. Recipe cycle validation remains domain-level.
170. Configuration selection remains domain-level.
171. Database integrity remains independent from UI validation.
172. Database constraints remain testable.
173. Migrations do not silently weaken integrity.
174. New constraints are introduced compatibly.
175. Historical data is not destroyed by configuration changes.
176. Archive is not treated as permanent deletion.
177. Soft deletion is not treated as historical correction.
178. Correction records preserve original state.
179. Business deletion never uses uncontrolled cascading.
180. Database integrity remains a mandatory safety boundary.

---

# 226. Recommended Constraint Categories by Table

| Table / Entity         | Recommended Integrity                               |
| ---------------------- | --------------------------------------------------- |
| Business               | PK, status CHECK, unique code                       |
| Branch                 | PK, Business FK, Business-scoped unique code        |
| Employee               | PK, Business FK, status CHECK                       |
| Employee Branch        | composite FK, composite UNIQUE                      |
| Device                 | PK, Business FK, device identity UNIQUE             |
| Subscription           | PK, Business FK, lifecycle constraints              |
| Product                | PK, Business FK, Category FK                        |
| Category               | PK, Business FK, scoped UNIQUE                      |
| Recipe                 | PK, Product FK, Business consistency                |
| Recipe Version         | PK, Recipe FK, version UNIQUE                       |
| Recipe Component       | PK, Recipe Version FK, Product FK, quantity CHECK   |
| Set                    | PK, Business FK                                     |
| Set Version            | PK, Set FK, version UNIQUE                          |
| Set Component          | PK, Set Version FK, Product FK                      |
| Warehouse              | PK, Branch/Business FK                              |
| Inventory Balance      | PK, Product FK, Warehouse FK, quantity CHECK        |
| Inventory Transaction  | PK, Product FK, quantity CHECK                      |
| Order                  | PK, Business FK, Branch FK, status CHECK            |
| Order Item             | PK, Order FK, Product/Set XOR CHECK, quantity CHECK |
| Table                  | PK, Branch FK, scoped UNIQUE                        |
| Payment                | PK, Order FK, operation UUID UNIQUE                 |
| Debt Customer          | PK, Business FK                                     |
| Debt Repayment         | PK, Debt Customer FK, amount CHECK                  |
| Refund                 | PK, original transaction FK, amount CHECK           |
| Cash Register          | PK, Branch FK, active uniqueness                    |
| Cash Session           | PK, Register FK, active uniqueness                  |
| Handover               | PK, Session/Employee FKs                            |
| Attendance             | PK, Employee FK, time CHECK                         |
| Payroll                | PK, Employee FK, amount CHECK                       |
| Configuration          | PK, Business/Branch FKs                             |
| Configuration Version  | PK, Configuration FK, version UNIQUE                |
| Audit Event            | PK, append-only protection                          |
| Report                 | PK, Business FK                                     |
| Report Version         | PK, Report FK, version UNIQUE                       |
| Notification           | PK, Business/Branch FK                              |
| Notification Recipient | composite UNIQUE                                    |
| Sync Operation         | PK, operation UUID UNIQUE                           |
| Lifecycle Job          | PK, Business FK, idempotency constraints            |

---

# 227. Recommended PostgreSQL Patterns

## 227.1. Positive Quantity

```sql
CHECK (quantity > 0)
```

Use for recipe components and inventory movement quantities.

---

## 227.2. Non-Negative Balance

```sql
CHECK (quantity >= 0)
```

Use for current inventory balances where negative stock is prohibited.

---

## 227.3. Markup Range

```sql
CHECK (
    markup_percent >= 0
    AND markup_percent <= 100
)
```

---

## 227.4. Product-or-Set Order Item

Conceptually:

```sql
CHECK (
    (product_uuid IS NOT NULL AND set_uuid IS NULL)
    OR
    (product_uuid IS NULL AND set_uuid IS NOT NULL)
)
```

---

## 227.5. Branch-Scoped Unique Value

```sql
UNIQUE (branch_uuid, code)
```

---

## 227.6. Business-Scoped Unique Value

```sql
UNIQUE (business_uuid, code)
```

---

## 227.7. One Active Cash Session

Conceptually:

```sql
CREATE UNIQUE INDEX ...
ON cash_session (cash_register_uuid)
WHERE status = 'OPEN';
```

---

## 227.8. Idempotency Key

Conceptually:

```sql
UNIQUE (operation_uuid)
```

The operation UUID must have the correct Business scope if the identity is not globally unique.

---

# 228. Constraint Design Rules

The database team must follow these rules:

1. Prefer simple constraints.
2. Prefer deterministic constraints.
3. Avoid hidden business workflows.
4. Avoid large trigger-based workflows.
5. Avoid cross-table triggers unless necessary.
6. Prefer explicit foreign keys.
7. Prefer composite ownership-aware references for critical tenant boundaries.
8. Prefer partial unique indexes for active-state uniqueness.
9. Use CHECK constraints for simple numeric/state invariants.
10. Use application logic for authorization.
11. Use transactions for atomic operations.
12. Use row locks for high-contention resources.
13. Keep historical records structurally valid.
14. Do not weaken tenant isolation for convenience.
15. Document every exceptional constraint.

---

# 229. Integrity and Performance

Constraints must protect correctness without unnecessarily slowing normal POS operations.

The database should avoid:

* expensive recursive triggers;
* unnecessary full-table validation during normal transactions;
* excessive synchronous reporting;
* long-running locks;
* large transactional scans.

POS operations must remain suitable for ordinary restaurant hardware.

---

# 230. Integrity and Scalability

The constraint model must support future expansion from the initial multi-branch deployment to larger Businesses.

The system must avoid assumptions that permanently limit:

* number of Branches;
* number of Products;
* number of Orders;
* number of Employees;
* number of Devices;
* number of inventory transactions.

---

# 231. Integrity and Historical Reconstruction

The database must preserve enough structural information to reconstruct important historical operations.

At minimum, the system must be able to identify:

* Business;
* Branch;
* Employee;
* Device;
* Order;
* Order Item;
* Product;
* Recipe Version where applicable;
* Payment;
* Cash Session;
* Inventory Transaction;
* configuration version;
* audit event.

---

# 232. Integrity and Corrections

Corrections must not destroy the original state.

The preferred pattern is:

```text
Original State
      ↓
Correction
      ↓
New State
```

rather than:

```text
Original State
      ↓
Overwrite
```

---

# 233. Integrity and Offline Operations

Offline operations are not exempt from database integrity.

When synchronized, every offline operation must pass server-side validation.

The server must be able to reject:

* invalid ownership;
* invalid permissions;
* stale configuration;
* duplicate operation;
* invalid lifecycle state;
* invalid stock;
* invalid payment;
* invalid Cash Session.

---

# 234. Integrity and Security

Database integrity contributes to security by preventing:

* cross-tenant references;
* unauthorized data relationships;
* duplicate financial operations;
* invalid lifecycle writes;
* historical tampering.

Application authorization remains mandatory.

---

# 235. Integrity and Backup Recovery

Backup restoration must preserve:

* primary keys;
* foreign keys;
* unique constraints;
* CHECK constraints;
* historical records;
* audit records;
* lifecycle states.

A restored database must not bypass normal integrity rules.

---

# 236. Integrity Verification After Recovery

After database recovery, integrity verification should include:

* foreign key validation;
* constraint validation;
* Business isolation checks;
* active Cash Session uniqueness;
* inventory consistency;
* synchronization idempotency;
* audit integrity.

---

# 237. Status

**Database Analysis:** Completed.

**Document Status:** Accepted.

**Current Document:** `25_Database_Integrity_and_Constraints.md`

**Next Document:** `26_Database_Indexes_and_Query_Strategy.md`

---

# 238. Related Documents

### Business Analysis

* `docs/01_Business_Analysis/01_Product_Overview.md`
* `docs/01_Business_Analysis/04_Tenant_and_Branch_Management.md`
* `docs/01_Business_Analysis/07_Offline_Operation_and_Synchronization.md`
* `docs/01_Business_Analysis/08_POS_and_Order_Management.md`
* `docs/01_Business_Analysis/09_Cash_Register_and_Cash_Sessions.md`
* `docs/01_Business_Analysis/14_Payments_Discounts_and_Refunds.md`
* `docs/01_Business_Analysis/18_Audit_and_Change_History.md`
* `docs/01_Business_Analysis/19_Data_Lifecycle_and_Deletion.md`
* `docs/01_Business_Analysis/20_Business_Rules.md`

### System Analysis

* `docs/02_System_Analysis/03_Tenant_Business_and_Branch_Context.md`
* `docs/02_System_Analysis/06_Device_Trust_and_Security_Context.md`
* `docs/02_System_Analysis/07_POS_and_Order_System.md`
* `docs/02_System_Analysis/14_Cash_Register_and_Cash_Session.md`
* `docs/02_System_Analysis/16_Inventory_Transaction_System.md`
* `docs/02_System_Analysis/18_Menu_Pricing_and_Configuration.md`
* `docs/02_System_Analysis/22_Audit_and_History.md`
* `docs/02_System_Analysis/23_Offline_Operation.md`
* `docs/02_System_Analysis/24_Synchronization_and_Conflict_Resolution.md`
* `docs/02_System_Analysis/26_Data_Lifecycle_and_Deletion.md`
* `docs/02_System_Analysis/27_System_Wide_Consistency_and_Concurrency.md`
* `docs/02_System_Analysis/30_System_Invariants_and_Rules.md`

### Domain Analysis

* `docs/03_Domain_Analysis/20_Cross_Domain_Relationships_Domain.md`
* `docs/03_Domain_Analysis/17_Data_Lifecycle_Domain.md`
* `docs/03_Domain_Analysis/18_Configuration_Domain.md`
* `docs/03_Domain_Analysis/16_Synchronization_Domain.md`

### Database

* `docs/05_Database/01_Database_Overview.md`
* `docs/05_Database/02_Database_Architecture.md`
* `docs/05_Database/03_Tenant_and_Business_Data_Model.md`
* `docs/05_Database/04_Identity_and_Access_Data_Model.md`
* `docs/05_Database/05_Branch_and_Organizational_Data_Model.md`
* `docs/05_Database/06_Subscription_and_Entitlement_Data_Model.md`
* `docs/05_Database/07_Device_and_Trust_Data_Model.md`
* `docs/05_Database/08_Product_and_Category_Data_Model.md`
* `docs/05_Database/09_Recipe_and_Recipe_Version_Data_Model.md`
* `docs/05_Database/10_Set_and_Set_Version_Data_Model.md`
* `docs/05_Database/11_Inventory_and_Warehouse_Data_Model.md`
* `docs/05_Database/12_Menu_and_Pricing_Data_Model.md`
* `docs/05_Database/13_Order_and_Order_Item_Data_Model.md`
* `docs/05_Database/14_Table_and_Waiter_Data_Model.md`
* `docs/05_Database/15_Payment_and_Debt_Data_Model.md`
* `docs/05_Database/16_Cash_Register_and_Cash_Session_Data_Model.md`
* `docs/05_Database/17_Shift_Handover_Data_Model.md`
* `docs/05_Database/18_Employee_Attendance_and_Payroll_Data_Model.md`
* `docs/05_Database/19_Notification_Data_Model.md`
* `docs/05_Database/20_Audit_and_History_Data_Model.md`
* `docs/05_Database/21_Report_and_Report_Version_Data_Model.md`
* `docs/05_Database/22_Offline_and_Synchronization_Data_Model.md`
* `docs/05_Database/23_Configuration_Data_Model.md`
* `docs/05_Database/24_Data_Lifecycle_and_Deletion_Data_Model.md`
* `docs/05_Database/26_Database_Indexes_and_Query_Strategy.md`
* `docs/05_Database/27_Database_Migrations_and_Change_Management.md`
* `docs/05_Database/28_Database_Backup_and_Recovery.md`
* `docs/05_Database/29_Database_Security.md`
* `docs/05_Database/30_Database_Invariants_and_Guardrails.md`

