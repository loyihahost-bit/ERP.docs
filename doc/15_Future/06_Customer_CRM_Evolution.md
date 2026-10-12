# Customer CRM Evolution

**Document ID:** FUT-06
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Category:** Future Product Capabilities and Architecture

## 1. Purpose

This document defines the future evolution path for customer relationship management (CRM) in the FastFood ERP platform.

It describes how the platform may evolve from storing customer information required for individual orders to supporting customer profiles, order history, loyalty programs, customer preferences, and controlled customer engagement.

This document is a future planning record. It does not authorize immediate implementation or change the current system's authoritative requirements.

## 2. Scope

This document covers:

* Customer identity and profile management.
* Customer contact information and preferences.
* Customer order history.
* Customer search and duplicate detection.
* Loyalty points and rewards.
* Customer segmentation and business insights.
* Promotions and customer communication.
* Customer privacy, consent, and data retention.
* Tenant and branch access controls.
* Integration with online ordering, delivery, mobile applications, and messaging channels.
* Migration from the current order-related customer information model.

Advanced marketing automation, external CRM synchronization, and third-party loyalty networks remain optional future capabilities requiring separate evaluation.

## 3. Current Baseline

The current system does not require a comprehensive customer database for ordinary POS operations.

For delivery orders, customer contact information such as a phone number and delivery address may be recorded as part of the order.

Current order types include:

* Dine-in.
* Takeaway.
* Phone delivery.

The current order workflow is cashier-based. Online ordering and a dedicated customer-facing application are deferred capabilities.

Therefore:

1. An order must remain valid without a full customer profile unless an existing business rule requires customer information for its fulfillment.
2. Existing order records remain authoritative for their own historical customer and fulfillment information.
3. A future CRM must not require customer registration for every POS transaction.
4. Customer profiles must not become a dependency for normal cashier, kitchen, inventory, or register operations.
5. Existing permissions, tenant isolation, and data lifecycle requirements continue to apply.

## 4. Evolution Goals

A future CRM should help restaurant businesses:

* Recognize returning customers where appropriate.
* View customer-related order history within authorized business boundaries.
* Maintain accurate and useful contact information.
* Reduce accidental duplicate profiles.
* Support transparent loyalty and reward programs.
* Understand customer activity through aggregated reports.
* Provide relevant customer service.
* Manage consent and communication preferences.
* Protect customer information from unauthorized access.
* Keep CRM processing separate from critical POS operations where practical.

The design should remain understandable and operable for businesses with different sizes, staffing levels, and subscription plans.

## 5. Core CRM Principles

### 5.1 Optional customer identification

Customer identification should be optional for ordinary transactions unless a specific service or approved business rule requires it.

Cashiers must be able to complete eligible orders without searching for or creating a customer profile.

### 5.2 Tenant isolation

Every customer record must belong to a clearly defined data ownership scope.

A restaurant business must not access another independent business's customer profiles, contact details, history, or loyalty balances.

### 5.3 Explicit identity resolution

The system must not assume that two orders belong to the same person merely because they share a name, address, or device.

Phone numbers and other contact details may be shared, changed, mistyped, or reassigned.

Customer profile merging must be controlled and auditable.

### 5.4 Authoritative business records

CRM must not become an independent source of truth for order totals, payments, refunds, inventory changes, or register transactions.

Customer history should reference authoritative business records.

### 5.5 Privacy by design

Collect only information needed for an approved business purpose. Access, retention, export, and deletion must follow defined policies.

### 5.6 Incremental evolution

Customer profiles, order history, loyalty, segmentation, and marketing automation should be introduced as separately evaluated capabilities.

A loyalty engine or marketing platform must not be introduced solely because basic customer profiles are implemented.

## 6. Customer Identity and Profile

A future customer profile may include:

* A persistent internal customer identifier.
* Display name.
* Verified or unverified phone number.
* Optional email address.
* Preferred language, if needed.
* Optional saved delivery addresses.
* Customer communication preferences.
* Profile creation and update timestamps.
* Profile status.
* Relevant consent records.
* Links to authorized customer-related orders.

The final field set must be determined through business and privacy analysis.

### 6.1 Stable identifiers

The customer identifier must be generated and managed by the system. Contact information must not be used as the primary database identifier.

Changing a phone number or email address must not silently create a new identity or transfer ownership of historical records.

### 6.2 Contact verification

If phone or email verification is introduced, the system must distinguish verified contact information from unverified information.

Verification proves control of a contact channel at a particular time; it does not necessarily prove a person's legal identity.

Verification requirements should be proportionate to the operation being performed.

### 6.3 Profile status

Potential profile states include:

* Active.
* Restricted, where a documented business or security reason exists.
* Archived or deactivated.

The exact state model and its consequences require approval.

Deactivating a profile must not automatically delete authoritative financial or order records that must be retained under applicable policies.

### 6.4 Guest customers

The platform should preserve a guest-customer path for orders that do not require a persistent profile.

If a customer later creates a profile, historical orders must only be linked when the system has a reliable and authorized basis for doing so.

A phone-number match alone must not grant unrestricted access to historical order details.

## 7. Customer History

A future CRM may provide an authorized view of customer-related activity.

Potential history items include:

* Order references and dates.
* Order type and branch.
* Products purchased.
* Order totals from authoritative order records.
* Order status and fulfillment outcome.
* Discounts and applied rewards.
* Refunds and cancellations, where permitted.
* Loyalty point accrual and redemption.
* Customer service interactions, if separately approved.

### 7.1 History integrity

Historical order information must remain traceable to the original order and relevant financial records.

CRM must not rewrite historical order totals when a menu price changes or a customer profile is updated.

A refund or correction must be represented through the authoritative financial workflow rather than silently editing a customer's historical purchase.

### 7.2 Access control

Customer history may expose commercially sensitive and personal information.

Access should be limited by role, tenant, branch, and operational purpose.

The system must define whether a permitted employee can view:

* All customers belonging to the tenant.
* Customers associated with selected branches.
* Only customers required for current service tasks.
* Aggregated customer statistics without detailed contact information.

Permissions for viewing customer details should be separable from permissions for editing profiles, merging duplicates, managing loyalty, exporting data, and viewing sensitive history.

### 7.3 History retention

Customer history must follow the applicable retention and deletion rules.

Where business or legal requirements require retention of financial records, deleting or deactivating a customer profile must not corrupt those records.

The exact treatment of profile links, personal information, and retained historical records must be defined before implementing deletion workflows.

## 8. Customer Search and Duplicate Management

A future CRM may support search by customer identifier, verified phone number, name, or other approved attributes.

Search must respect tenant and branch permissions.

The design should account for:

* Different formatting of the same phone number.
* Incorrect or outdated contact information.
* Shared household or business phone numbers.
* Duplicate profile creation.
* Changes in customer contact details.
* Customers who prefer not to maintain a profile.

### 8.1 Duplicate detection

Duplicate detection may suggest potential matches, but it must not automatically merge records based on a weak match.

A match decision should consider the reliability of the available evidence and the impact on historical orders and loyalty balances.

### 8.2 Profile merging

If profile merging is approved, it must be a controlled operation with:

* Explicit permission.
* A documented reason.
* A review of linked orders and loyalty balances.
* Protection against double-counting points or transactions.
* An audit trail.
* A defined correction or recovery procedure.

Merging must not erase the original financial history or silently transfer one customer's data to another customer.

## 9. Loyalty Program Evolution

A future loyalty program may reward eligible customer purchases and allow customers to redeem benefits under defined rules.

Possible program models include:

* Points per eligible purchase.
* Tier-based benefits.
* Fixed-value rewards.
* Discounts after meeting defined conditions.
* Limited-time campaigns.
* Branch-specific offers.

These are alternatives for future evaluation, not approved current features.

### 9.1 Program configuration

A future loyalty configuration may define:

* Program status and effective dates.
* Eligible branches and products.
* Earning rules.
* Redemption rules.
* Point expiration, if applicable.
* Minimum redemption thresholds.
* Reward limits.
* Excluded transactions.
* Refund and cancellation behavior.
* Authorized administrators.

Program rules must be explicit and versioned where necessary so historical transactions can be interpreted correctly.

### 9.2 Loyalty ledger

If points or rewards are implemented, a ledger-based model should be evaluated.

Rather than treating the displayed balance as the only record, the system should preserve traceable events such as:

* Points earned.
* Points redeemed.
* Points reversed.
* Expired points, where supported.
* Administrative adjustments.
* Corrections related to refunds or cancelled orders.

Each event should have an authoritative reference, a reason where applicable, a timestamp, and an identifiable actor or system process.

The displayed balance should be derived from or reconciled against the authoritative ledger.

### 9.3 Earning and redemption integrity

Loyalty processing must prevent:

* Duplicate point awards for the same eligible purchase.
* Repeated redemption of the same balance.
* Negative or otherwise invalid balances, unless a separately approved model explicitly supports them.
* Unauthorized manual adjustments.
* Incorrect rewards after a refund or cancellation.
* Concurrent redemptions exceeding the available balance.

Points should be awarded only when the approved business conditions are satisfied.

The exact award trigger, such as payment completion or order completion, must be explicitly defined.

### 9.4 Refunds and cancellations

A refund or cancellation must trigger the appropriate loyalty correction under the approved program rules.

The system must not assume every refund requires the same point reversal. Partial refunds, redeemed rewards, promotional bonuses, and expired points may need distinct handling.

Corrections must be idempotent, auditable, and consistent with the financial record.

### 9.5 Offline operation

Loyalty features must not compromise offline POS operations.

Before allowing offline earning or redemption, the design must address stale balances, concurrent use across branches, duplicate synchronization, and conflicting transactions.

If safe offline redemption cannot be guaranteed, the system should disable that operation while offline and communicate the limitation clearly.

Offline loyalty behavior is not authorized by this document.

## 10. Customer Segmentation and Insights

A future CRM may support operationally useful customer segments based on approved and explainable criteria.

Examples include:

* Customers with recent purchases.
* Customers who have not purchased within a defined period.
* Frequent customers.
* Customers associated with a particular branch.
* Customers who have opted into relevant communications.
* Customers eligible for a specific loyalty benefit.

Segmentation must be based on data the business is authorized to process.

The system should distinguish aggregated reporting from lists containing identifiable customer information.

Customer segments must not automatically trigger communications or financial changes unless a separate approved workflow authorizes those actions.

Sensitive personal characteristics must not be inferred or used for inappropriate targeting.

## 11. Promotions and Customer Communication

Future CRM capabilities may support approved customer communications about orders, loyalty rewards, and promotions.

Communication channels could include SMS, email, messaging applications, push notifications, or other supported channels. No channel is selected by this document.

### 11.1 Transactional messages

Order confirmations, status updates, and service notifications should be governed separately from promotional messages.

The system should send transactional communications only when the relevant event is authoritative and the destination is appropriate for the order.

### 11.2 Marketing consent

Promotional communication must follow applicable legal requirements and documented consent or other approved lawful bases.

The system must distinguish:

* Permission or legal basis to process an order.
* Permission or legal basis for transactional communication.
* Consent or other lawful basis for marketing communication.
* Channel-specific communication preferences.

The exact consent model must be reviewed for the jurisdictions in which the platform operates.

Marketing opt-out must not disable necessary order-related communication where such communication remains permitted and required.

### 11.3 Message delivery

External message delivery may fail, be delayed, or produce uncertain results.

Message attempts should be traceable, retries should be bounded, and duplicate sends should be considered in the design.

Failure to deliver a marketing message must not alter the underlying order or loyalty transaction.

## 12. Customer Privacy and Data Governance

CRM increases the amount and sensitivity of customer information held by the platform.

A future implementation must define:

* Purpose and legal basis for each category of data.
* Required versus optional profile fields.
* Data access and export permissions.
* Retention and deletion periods.
* Customer correction procedures.
* Contact verification requirements.
* Consent records and withdrawal handling.
* Audit requirements.
* Protection of data in transit and at rest.
* Restrictions on logs, analytics, and external integrations.
* Procedures for incidents involving customer information.

### 12.1 Data minimization

Do not collect information simply because it may be useful later.

Saved addresses, birthdays, demographic details, preferences, and marketing profiles should only be introduced when a defined purpose and appropriate controls exist.

### 12.2 Data export

If customer data export is implemented, exports must be authorized, scoped, logged, and protected against accidental disclosure.

A user must not be able to export customer records across unauthorized tenants or branches.

### 12.3 Deletion and anonymization

Profile deletion, deactivation, and anonymization are distinct operations.

The implementation must define which personal information can be removed, which records must be retained, and how historical business records remain consistent.

Existing subscription-related data lifecycle rules must also be respected.

CRM must not silently extend data retention beyond approved periods.

## 13. Tenant, Branch, and Role Permissions

Customer records must have an explicit ownership and access model.

The architecture must determine whether profiles are tenant-wide, branch-scoped, or governed by a combination of ownership and access permissions.

If a customer purchases from several branches within the same tenant, the system must define when staff at one branch may view activity associated with another branch.

Permissions should distinguish at least the following capabilities where applicable:

* View customer profiles.
* Create profiles.
* Edit contact information.
* View detailed order history.
* View loyalty balances.
* Adjust loyalty points.
* Configure loyalty programs.
* Manage customer segments.
* Send promotional communications.
* Export customer data.
* Merge duplicate profiles.
* Archive or delete profiles.

The exact permission set must follow the platform's authoritative role and permission model.

Owner-level access must still respect tenant isolation. A role in one restaurant business must not grant access to a different tenant's customers.

## 14. Subscription and Commercial Entitlements

Customer CRM and loyalty may become tariff-controlled capabilities.

A future design may define entitlements for:

* Customer profile management.
* Detailed order history.
* Loyalty program configuration.
* Customer segmentation.
* Promotional communication.
* Advanced reporting.
* External CRM integrations.

The entitlement scope and limits require separate approval.

Subscription expiration must not corrupt customer identities, historical orders, loyalty ledgers, or financial records.

If a feature is disabled after subscription expiration, the platform must define which data remains viewable, which operations are blocked, and how pending customer obligations are handled.

For example, any already-issued loyalty reward or pending redemption must follow an approved policy rather than being silently discarded.

## 15. Integration with Other Future Capabilities

CRM may later integrate with:

* `05_Online_Ordering_Evolution.md`
* `07_Advanced_Delivery_Management.md`
* `08_Mobile_Customer_Application.md`
* `09_Messaging_and_Channel_Integrations.md`
* `10_Advanced_AI_and_Intelligent_Automation.md`

Integration should use documented interfaces and explicit authorization.

The customer identity model must not be duplicated independently in each channel.

However, a shared identity model does not mean every channel must have identical permissions or access to all customer information.

Each integration must define:

* Data ownership.
* Authentication and authorization.
* Data synchronization direction.
* Conflict resolution.
* Retry and idempotency behavior.
* Data retention.
* Failure handling.
* Audit requirements.

External CRM providers, marketing platforms, and loyalty networks are optional integrations and require separate security, cost, and architecture review.

## 16. Reporting and Analytics

Potential CRM reports include:

* Number of active customer profiles.
* New and returning customer counts.
* Customer order frequency.
* Aggregated order value by approved segment.
* Loyalty points earned and redeemed.
* Outstanding reward liabilities, if relevant to the approved accounting model.
* Reward expiration statistics.
* Customer retention trends.
* Promotional campaign delivery and redemption results.

Definitions must be consistent across reports. For example, the business must define what qualifies as an active customer and a returning customer.

Reports must not misrepresent gross sales, net sales, refunds, or loyalty discounts.

Aggregated reporting should be preferred when individual customer identities are not necessary.

Analytics must respect data retention, access control, and privacy requirements.

## 17. Performance and Scalability

CRM must not introduce unnecessary overhead into critical POS operations.

Before implementation, evaluate:

* Customer search frequency and query patterns.
* Expected profile and order-history volume.
* Indexing and pagination requirements.
* Tenant and branch filters.
* Concurrent loyalty transactions.
* Reporting workload.
* Data retention and archival growth.
* Export size and processing time.
* External integration latency.

Customer search should use appropriate indexed fields and bounded results.

Detailed order history should be paginated rather than returning an unlimited number of records.

Large reports and exports may require asynchronous processing if measured workload justifies it.

Additional services, databases, caches, or messaging infrastructure must not be introduced without an approved requirement and evidence that the existing architecture is insufficient.

No capacity or performance guarantee is established by this document.

## 18. Data Model Evolution

No database schema change is authorized by this document.

Potential future entities or structures include:

* Customer profile.
* Customer contact method.
* Customer address.
* Customer consent and communication preference.
* Customer-to-order association.
* Loyalty program and program version.
* Loyalty ledger entry.
* Reward definition and redemption.
* Customer segment definition.
* Campaign and communication delivery record.
* Profile merge or correction audit record.

These are conceptual candidates, not approved table names or mandatory entities.

Before implementation:

1. Inspect the existing order and customer-related data model.
2. Identify data that already exists within order records.
3. Decide the authoritative customer identity model.
4. Define uniqueness rules and duplicate handling.
5. Define tenant and branch ownership constraints.
6. Define consistency between orders, refunds, and loyalty events.
7. Define concurrency and idempotency requirements.
8. Define retention, anonymization, and deletion behavior.
9. Plan safe migrations and rollback.
10. Update authoritative database and domain documentation.

Existing orders must remain valid even if no customer profile is associated with them.

## 19. Testing Requirements

A future CRM implementation must include appropriate coverage for the following areas.

### 19.1 Profile management

* Create and update profiles.
* Verify and change contact information.
* Handle duplicate candidates.
* Deactivate and reactivate profiles where supported.
* Preserve existing orders when profile data changes.
* Handle guest orders correctly.

### 19.2 Authorization and privacy

* Cross-tenant access attempts.
* Cross-branch access restrictions.
* Unauthorized history access.
* Restricted customer data exports.
* Consent and marketing opt-out behavior.
* Retention and deletion workflows.
* Sensitive-data exposure in logs and error messages.

### 19.3 Loyalty integrity

* Eligible and ineligible purchases.
* Duplicate award prevention.
* Concurrent redemptions.
* Partial and full refunds.
* Cancellation and reversal processing.
* Manual adjustments and audit trails.
* Point expiration, if supported.
* Offline synchronization, if enabled.

### 19.4 Integration and resilience

* External provider failures.
* Duplicate webhook or event delivery.
* Delayed message delivery.
* Retry after an uncertain outcome.
* Migration compatibility.
* Recovery and reconciliation.

### 19.5 Regression

Existing POS orders, cash registers, inventory, recipes, subscription enforcement, reporting, and offline synchronization must continue to behave according to their authoritative requirements.

## 20. Implementation Readiness Checklist

Before a CRM capability is enabled in production, the project must approve the relevant items:

* [ ] Business goals and supported CRM capabilities.
* [ ] Customer identity and guest-customer model.
* [ ] Customer data ownership and tenant boundaries.
* [ ] Branch visibility rules.
* [ ] Profile fields and data minimization.
* [ ] Contact verification requirements.
* [ ] Order-history access rules.
* [ ] Duplicate detection and merge procedure.
* [ ] Loyalty program rules, if included.
* [ ] Loyalty ledger and refund behavior, if included.
* [ ] Marketing consent and communication preferences.
* [ ] Data retention, export, deletion, and anonymization.
* [ ] Role and permission updates.
* [ ] Subscription entitlements.
* [ ] Database migration and rollback.
* [ ] API and integration contracts.
* [ ] Security and privacy review.
* [ ] Monitoring and operational procedures.
* [ ] Functional, security, integrity, and regression tests.
* [ ] Updates to authoritative documentation.
* [ ] Required ADRs and implementation approval.

## 21. Decision and Governance

This document establishes a controlled future direction for CRM.

It does not:

* Authorize immediate CRM implementation.
* Require customer registration for every POS order.
* Approve automatic profile merging.
* Select a loyalty model or reward calculation.
* Approve marketing campaigns or a messaging provider.
* Mandate a third-party CRM platform.
* Authorize unrestricted sharing of customer information across branches.
* Change existing subscription, order, payment, inventory, or data-retention rules.

Each capability must be separately evaluated and approved before implementation.

The authoritative Business Analysis, System Analysis, Domain Analysis, Architecture, Database, Backend, Frontend, API, Security, Testing, Deployment, and Operations documents must be updated as applicable. Relevant architecture decisions must be recorded in ADRs.

## 22. Related Documents

* `01_Future_Roadmap_and_Evolution_Framework.md`
* `02_Deferred_Capabilities_and_Architecture_Reserve.md`
* `05_Online_Ordering_Evolution.md`
* `07_Advanced_Delivery_Management.md`
* `08_Mobile_Customer_Application.md`
* `09_Messaging_and_Channel_Integrations.md`
* `10_Advanced_AI_and_Intelligent_Automation.md`
* `12_Future_Architecture_Guardrails.md`
* `doc/11_Security/README.md`
* `doc/12_Testing/README.md`
* `doc/14_Operations/README.md`

The authoritative order, refund, inventory, permissions, subscription, and data lifecycle documentation must also be reviewed before implementation.

## 23. Core Invariants

1. CRM remains a future capability until separately approved.
2. Existing POS workflows must not require a customer profile unnecessarily.
3. Guest orders remain supported where current business rules permit them.
4. Customer identifiers must not depend on mutable contact information.
5. Tenant isolation applies to all customer data.
6. Branch access must follow explicit permissions.
7. Customer profile data must not replace authoritative order records.
8. Historical orders must remain interpretable after profile changes.
9. Contact matching alone must not grant access to customer history.
10. Profile merging must be controlled and auditable.
11. Duplicate detection must not silently merge identities.
12. Customer data collection must have a defined purpose.
13. Sensitive information must be protected in storage, transit, and logs.
14. Customer history must follow approved access and retention rules.
15. Financial history must not be corrupted by profile deletion.
16. Loyalty features require separately approved rules.
17. Loyalty balances must have traceable authoritative events.
18. Loyalty awards must not be duplicated by retries.
19. Loyalty redemptions must respect available balances and concurrency controls.
20. Refund and cancellation behavior must be defined for loyalty transactions.
21. Offline loyalty operations require explicit consistency rules.
22. Marketing communication must follow applicable consent and legal requirements.
23. Transactional and promotional communications must be distinguished.
24. Marketing opt-out must be handled according to approved policy.
25. Failed communication must not corrupt orders or loyalty records.
26. Customer segments must use authorized data.
27. Individual customer information must not be exposed through unauthorized reports.
28. CRM integrations must use controlled interfaces.
29. External integration events must be validated.
30. Customer-facing channels must not create independent sources of truth.
31. Subscription restrictions must not corrupt historical customer or financial data.
32. Customer search must be bounded and permission-aware.
33. Large histories and reports must be handled appropriately.
34. Data export must be authorized, scoped, and protected.
35. Deletion and anonymization must be explicitly defined.
36. Profile and order associations must preserve tenant boundaries.
37. Loyalty corrections must be idempotent and auditable.
38. Customer identity changes must not silently transfer ownership.
39. CRM must not degrade critical POS operations.
40. Performance claims must be based on measurements.
41. Additional infrastructure requires justification and approval.
42. Historical order totals must not change because of CRM edits.
43. Customer access must not rely on predictable identifiers alone.
44. Security and privacy reviews are required before production launch.
45. Operational monitoring must minimize personal data exposure.
46. Migrations must preserve existing order validity.
47. Third-party CRM integrations remain optional.
48. No specific loyalty model is selected by this document.
49. Future requirements must be reflected in authoritative documentation.
50. Implementation requires explicit approval and appropriate architecture decisions.

---

**End of Document**

