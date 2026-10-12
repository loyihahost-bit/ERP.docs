# Online Ordering Evolution

**Document ID:** FUT-05
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Category:** Future Architecture and Product Evolution

## 1. Purpose

This document defines the future evolution path for online ordering in the FastFood ERP platform.

It describes how customers may eventually browse restaurant menus, submit orders through online channels, track order progress, and receive order-related notifications.

This document is a future planning record. It does not authorize implementation or change current operational requirements.

## 2. Scope

This document covers:

* Customer-facing online menu access.
* Branch selection and service availability.
* Cart management and order submission.
* Menu pricing and availability validation.
* Order acceptance and rejection.
* Payment lifecycle integration.
* Kitchen and branch order routing.
* Customer notifications and order tracking.
* Security, privacy, abuse prevention, and operational support.
* Compatibility with offline branches, inventory, subscriptions, and future customer-facing applications.

This document does not select a payment provider, frontend framework, messaging provider, or implementation architecture.

## 3. Current Baseline

The current system accepts orders through the cashier workflow.

Current order types include:

* Dine-in.
* Takeaway.
* Phone delivery.

The cashier records the order using the current POS workflow. Accepted orders follow existing receipt-printing, kitchen-routing, order-status, payment, inventory, and archival rules.

Online ordering is a deferred capability.

Until a separate implementation decision is approved:

1. The cashier remains the authorized entry point for the current order intake workflow.
2. No public customer ordering endpoint is required by this document.
3. Existing POS behavior must not depend on online ordering being available.
4. Existing branch, menu, recipe, stock, payment, and subscription rules remain authoritative.

## 4. Evolution Goals

A future online ordering capability should:

* Allow customers to discover eligible branches and their available menus.
* Present accurate branch-specific prices and product availability.
* Prevent invalid, duplicate, or incorrectly priced orders.
* Route accepted orders to the correct branch and operational workflow.
* Integrate with existing kitchen preparation and inventory deduction rules.
* Provide clear order and payment states.
* Protect customer and business data.
* Support appropriate recovery when connectivity or external services fail.
* Avoid degrading existing cashier and kitchen operations.
* Allow future integration with CRM, delivery management, mobile applications, and messaging channels without requiring those capabilities now.

## 5. Potential Customer Channels

Online ordering may eventually be offered through one or more channels:

* A public restaurant ordering website.
* A mobile-friendly web application.
* A customer mobile application.
* A supported external ordering integration.
* A messaging channel, if separately approved.

These channels are alternatives or complementary entry points, not mandatory initial components.

A shared order domain model and validated order-submission process should be preferred over independently implementing business rules in every channel.

The final channel strategy requires a separate product and architecture decision.

## 6. Customer Ordering Journey

A future customer journey may follow these stages:

1. Open an ordering channel.
2. Select a restaurant or eligible branch.
3. Select the service type, such as takeaway or delivery.
4. Browse the branch's eligible menu.
5. Select products, quantities, and permitted customizations.
6. Review prices, discounts, applicable fees, and the order total.
7. Provide only the customer information required for the selected service.
8. Submit the order.
9. Receive an order reference and a clear submission status.
10. Complete payment if required by the approved payment policy.
11. Receive acceptance, preparation, and fulfillment updates when available.
12. Complete collection or delivery through the supported workflow.

The exact journey, mandatory fields, and payment sequence must be decided before implementation.

The interface must distinguish between an order being submitted, accepted by the branch, paid, prepared, and completed. These states must not be treated as interchangeable.

## 7. Branch Selection and Availability

Online ordering must resolve every order to one authorized restaurant tenant and one specific branch.

The future design must define:

* How customers discover eligible branches.
* Which service types each branch supports.
* How opening hours and temporary closures affect ordering.
* How delivery areas and service restrictions are determined.
* How branch-specific menu availability is presented.
* What happens when a branch becomes unavailable during checkout.
* Whether a customer may change branches before submitting an order.

A branch selection in the customer interface is not sufficient authorization by itself. The backend must validate the branch and tenant relationship for every submission.

An order must never be silently routed to another branch because the selected branch is unavailable.

## 8. Menu, Pricing, and Product Availability

The online menu must use authoritative business data rather than maintaining an independent source of truth for products and prices.

A future implementation must consider:

* Global menu definitions and permitted branch-level differences.
* Branch-specific prices and authorized price overrides.
* Product activation and deactivation.
* Product availability and temporary equipment-related restrictions.
* Approved recipe and menu changes.
* Discounts and eligible combinations.
* Permitted product customizations.
* Tax-inclusive pricing rules already established by the business.
* Availability changes between browsing and submission.

The backend must revalidate product eligibility, quantity, price, branch, and order total when the customer submits an order.

A price displayed earlier in the customer interface must not be trusted as the final authoritative price.

If a product becomes unavailable or its price changes before submission, the system must return a clear result and require the customer to review any material change before proceeding.

The system must not accept an order that violates the existing inventory rules, including the prohibition on negative stock.

## 9. Cart and Order Submission

The cart is a temporary customer interaction state. It is not the authoritative business order record.

The future implementation should distinguish:

* Cart contents.
* A submission attempt.
* A persisted order.
* An accepted operational order.
* A payment attempt or payment result.
* A fulfillment state.

Order submission must be designed for retries and unreliable networks.

Required safeguards include:

* A unique submission or idempotency key for each logical submission.
* Server-side validation of all submitted data.
* Protection against duplicate order creation.
* Protection against duplicate payment processing.
* Safe handling of browser refreshes and repeated button presses.
* A clear response when the submission outcome is unknown.
* A way to recover the existing result rather than blindly creating another order.

Client-generated identifiers may help correlate requests, but they must not replace authoritative server-side identifiers or authorization checks.

The system must not rely on a successful browser response as proof that an order or payment was persisted.

## 10. Order Acceptance and Rejection

The system must define when an online order becomes an accepted business commitment.

A future design should consider explicit states such as:

* Draft or cart.
* Submission pending.
* Awaiting branch decision, if manual confirmation is required.
* Accepted.
* Rejected.
* Cancellation requested.
* Cancelled.
* In preparation.
* Ready for collection or dispatch.
* Completed.

The final state model must be consistent with the existing order lifecycle and avoid duplicate or contradictory transitions.

The system must define:

* Whether acceptance is automatic or requires staff confirmation.
* How the branch is notified about incoming orders.
* Who may accept or reject an order.
* Which rejection reasons are available.
* How customers are informed of rejection.
* How payment authorization, capture, voiding, or refunding is handled when an order is rejected or cancelled.
* How timeouts and interrupted workflows are reconciled.

An order must not be marked as accepted solely because a customer submitted a form.

Financial reversals must follow the approved payment and refund policies. They must not silently alter cash-register records or bypass existing authorization requirements.

## 11. Payment Evolution

Online payments are a future integration point and are not authorized by this document.

Before implementation, the project must decide:

* Which payment methods are supported.
* Whether payment occurs before branch acceptance, after acceptance, or at another approved stage.
* Which payment provider or providers are appropriate.
* How payment status is reconciled with order status.
* How failed, delayed, cancelled, and uncertain payment results are handled.
* How refunds and partial refunds are authorized and audited.
* How provider callbacks are authenticated and processed.
* How reconciliation reports identify mismatches between payment and order records.

The system must treat payment provider responses as external inputs that require verification.

Payment callbacks and retries must be idempotent. Duplicate callbacks must not create duplicate financial effects.

Sensitive payment credentials and secrets must not be stored in ordinary order records or application logs. Card data handling must follow the applicable provider requirements and security obligations.

No payment provider or payment sequence is selected by this document.

## 12. Kitchen and Branch Integration

Accepted online orders should enter the existing branch order-processing workflow through an explicitly approved integration.

The integration must preserve:

* Correct tenant and branch ownership.
* Existing product and order status rules.
* Product-specific kitchen routing and printer configuration.
* Order numbering and persistent database identifiers.
* Inventory deduction based on the authoritative order lifecycle.
* Recipe and stock validation.
* Existing cancellation, refund, and audit controls.
* Appropriate staff visibility and permissions.

The implementation must define when stock is reserved or deducted, how rejected or cancelled orders affect stock, and how retries avoid repeated inventory changes.

These behaviors must follow the authoritative inventory and order-domain documentation.

An online order must not bypass kitchen workflow controls or automatically modify a recipe to make an unavailable product sellable.

## 13. Offline Branches and Connectivity Failures

Some branches must continue operating when their internet connection is unavailable.

Online ordering must not undermine the existing offline POS model.

The future design must explicitly define what happens when:

* A branch loses connectivity after a customer submits an order.
* The central service cannot confirm whether an order was persisted.
* A branch cannot receive incoming orders in real time.
* Menu or stock information is stale.
* Payment confirmation is delayed.
* An online order and an in-branch sale compete for limited stock.
* Synchronization retries occur after connectivity returns.

A customer-facing channel must not claim that a branch has accepted an order without authoritative confirmation.

If the branch cannot safely receive or process online orders, the system should disable online ordering for that branch or present a clear unavailability state.

Queued or retried operations must preserve idempotency and ordering consistency. Synchronization must not duplicate orders, payments, stock deductions, or refunds.

The exact offline-ordering behavior requires a separate approved design.

## 14. Delivery and Fulfillment

Online ordering may support collection, dine-in workflows where appropriate, and delivery.

Delivery management is separately covered by `07_Advanced_Delivery_Management.md`.

Before enabling delivery, the project must define:

* Delivery eligibility and service areas.
* Address validation and required contact information.
* Delivery fee calculation and disclosure.
* Estimated preparation and delivery times, including uncertainty.
* Assignment and responsibility for delivery fulfillment.
* Handling of failed delivery, customer unavailability, and cancellation.
* Proof of fulfillment, if required.
* Refund and complaint workflows.

The initial online-ordering implementation must not assume that advanced driver dispatch, live maps, route optimization, or external courier integrations already exist.

## 15. Customer Data and Privacy

Online ordering introduces additional customer-facing data processing.

The future implementation must collect only information necessary to fulfill the selected service.

Potential data includes:

* Customer name, when required.
* Contact phone number.
* Delivery address, when required.
* Order contents and history.
* Order and payment references.
* Customer communication preferences, where applicable.

Requirements include:

* Tenant and branch access isolation.
* Least-privilege access to customer information.
* Encryption in transit and appropriate protection at rest.
* Redaction of personal data from logs and monitoring.
* Defined retention and deletion rules.
* Restricted access to delivery addresses and contact details.
* Protection against unauthorized enumeration of orders.
* A safe process for customers to access their own order information.

Public order references must not act as sufficient authorization to access sensitive order details.

The existing subscription expiration and data lifecycle policies continue to apply. Future customer data must be covered by the approved retention, export, and deletion rules.

Consent, marketing preferences, and customer-profile retention must be defined before adding promotional messaging or CRM features.

## 16. API and Application Security

A future public ordering channel expands the externally reachable attack surface.

The design must consider:

* Public endpoint authentication requirements.
* Anonymous ordering abuse and automated submissions.
* Rate limits and request-size limits.
* Server-side validation and safe error messages.
* Cross-site request forgery protection where applicable.
* Cross-origin access controls.
* Secure session and token handling.
* Authorization for order status, cancellation, and customer details.
* Protection against insecure direct object references.
* Webhook authentication and replay protection.
* Dependency and application security checks.
* Audit trails for staff actions and sensitive state transitions.

Customer-facing endpoints must never expose internal administrative functions or permit customers to access another tenant's or customer's records.

Security controls must be proportionate to the measured risk and implemented without introducing unnecessary dependencies.

## 17. Availability, Performance, and Resilience

Online ordering must not degrade the core POS and kitchen workflows.

Before launch, the project must establish measurable service expectations based on actual workload and deployment capacity.

Evaluation should cover:

* Expected concurrent customers and order submission rates.
* Menu and pricing read load.
* Database transaction duration and contention.
* External payment provider latency.
* Branch order delivery latency.
* Notification delays.
* Retry and queue behavior, if asynchronous processing is approved.
* Database connection usage.
* Resource usage during peak ordering periods.

Caching may be considered for public menu reads, but authoritative validation must occur at order submission.

Cached data must not be used to bypass current branch, pricing, product availability, authorization, or subscription rules.

Retries must be bounded and safe. A slow external provider must not hold critical database transactions open unnecessarily.

Queues, separate services, and additional infrastructure must be introduced only when justified by measured needs and an approved architecture decision.

## 18. Subscription and Commercial Rules

Online ordering may become a subscription-controlled capability.

If introduced, entitlement rules must define:

* Which tariffs enable online ordering.
* Whether the capability is enabled per tenant, branch, or another approved scope.
* Any approved usage limits.
* Who can configure the capability.
* What happens when a subscription expires.
* How existing accepted orders are completed after expiry.
* How payment reconciliation, refunds, and customer communications remain available when needed.

A subscription restriction must not corrupt existing orders or financial records.

The system must not abruptly discard accepted orders, duplicate payments, or prevent required financial reconciliation merely because an entitlement changes.

Existing subscription and data lifecycle requirements remain authoritative.

## 19. Future CRM and Customer Channels

Online ordering may later integrate with customer CRM, mobile applications, messaging channels, and customer loyalty features.

Related planning documents include:

* `06_Customer_CRM_Evolution.md`
* `08_Mobile_Customer_Application.md`
* `09_Messaging_and_Channel_Integrations.md`

The ordering domain should expose controlled business capabilities that can be reused by approved channels.

Each channel must use the same authoritative rules for order validation, pricing, acceptance, payment, inventory, and fulfillment.

A customer identity or profile must not be created implicitly with broader permissions than the customer-facing feature requires.

CRM, loyalty, marketing automation, and mobile applications are not prerequisites for online ordering unless a future approved decision explicitly establishes that dependency.

## 20. Reporting and Auditability

A future implementation may introduce online-order-specific reporting, including:

* Submitted, accepted, rejected, and cancelled orders.
* Order volume by tenant and branch.
* Order source or channel.
* Order preparation and fulfillment durations.
* Payment reconciliation status.
* Cancellation and refund reasons.
* Failed submissions and repeated attempts.
* Customer support and operational incidents.

Reports must distinguish between order creation, acceptance, payment, and fulfillment.

Financial reports must use authoritative financial records rather than reconstructing revenue from customer interface events.

Audit records should capture important state transitions, actor identity where available, timestamps, relevant reasons, and correlation identifiers.

Reports and exports must respect tenant isolation, branch permissions, and data retention requirements.

## 21. Deployment and Operational Readiness

Before launch, the implementation must have documented:

* Configuration and secret management.
* Environment-specific settings.
* Public endpoint exposure and access controls.
* Payment provider configuration, if applicable.
* Monitoring and alerting.
* Error handling and customer-facing fallback states.
* Incident response and recovery procedures.
* Backup and restore implications.
* Release and rollback procedures.
* Support procedures for disputed or missing orders.
* Reconciliation procedures for uncertain payment outcomes.

Monitoring should cover the full order journey, from submission through acceptance and fulfillment, while avoiding unnecessary personal data collection.

A rollback must not erase accepted orders, reverse confirmed payments incorrectly, or leave inventory and order states inconsistent.

Operational readiness must be reviewed before enabling online ordering for real customers.

## 22. Data Model and Migration Considerations

No database schema change is authorized by this document.

A future design may require entities or fields for:

* Order source or channel.
* Customer contact and fulfillment details.
* Submission idempotency.
* External payment references and payment state.
* Customer-facing order tracking.
* Acceptance and rejection metadata.
* Delivery fulfillment state.
* Notification delivery status.

These are conceptual candidates, not approved table names or schema requirements.

Before implementation:

1. Review the existing order, payment, inventory, customer, and audit models.
2. Identify which information is already represented.
3. Avoid storing duplicate sources of truth.
4. Define uniqueness and idempotency constraints.
5. Define transaction boundaries and concurrency behavior.
6. Define tenant and branch ownership constraints.
7. Plan backward-compatible migrations and rollback behavior.
8. Define retention, export, and deletion behavior.
9. Update authoritative data model and API documentation.

Historical orders must remain interpretable after the feature is introduced. Existing POS orders must not be reclassified or altered incorrectly.

## 23. Testing Requirements

A future implementation must include, at minimum:

### Functional testing

* Branch selection and service eligibility.
* Menu and branch-specific pricing.
* Cart validation and product availability.
* Order submission and customer-visible status.
* Acceptance, rejection, cancellation, and fulfillment.
* Payment success, failure, and delayed confirmation.
* Customer notifications and order tracking.

### Data integrity testing

* Duplicate submission prevention.
* Duplicate callback and payment-effect prevention.
* Inventory deduction exactly once per applicable business transition.
* Correct cancellation and refund handling.
* Tenant and branch isolation.
* Concurrent orders for limited stock.
* Safe retry after an unknown submission outcome.

### Security testing

* Unauthorized order access.
* Cross-tenant and cross-customer access attempts.
* Abuse and rate-limit behavior.
* Input validation.
* Webhook authentication and replay attempts.
* Sensitive-data exposure in logs and error responses.

### Resilience testing

* Customer network interruption.
* Branch connectivity loss.
* Database or application restart during order processing.
* Delayed payment callbacks.
* Notification provider failure.
* Retry and reconciliation behavior.
* Recovery without duplicate financial or inventory effects.

### Regression testing

Existing cashier ordering, kitchen printing, inventory, register reconciliation, offline synchronization, permissions, subscriptions, and reporting must continue to work.

Testing must be proportionate to the implementation and follow the authoritative testing documentation.

## 24. Implementation Readiness Checklist

Online ordering must not be enabled until the following have been reviewed and approved:

* [ ] Product scope and supported customer channels.
* [ ] Branch eligibility and temporary unavailability behavior.
* [ ] Order acceptance and rejection rules.
* [ ] Order state machine and permitted transitions.
* [ ] Menu, pricing, discount, and stock validation.
* [ ] Payment methods and reconciliation rules, if applicable.
* [ ] Duplicate submission and retry protection.
* [ ] Kitchen routing and inventory integration.
* [ ] Offline branch behavior.
* [ ] Customer data, privacy, and retention requirements.
* [ ] Security threat assessment and authorization rules.
* [ ] Subscription entitlement behavior.
* [ ] Reporting and audit requirements.
* [ ] Monitoring, alerting, support, and incident procedures.
* [ ] Database migration and rollback plan.
* [ ] Functional, security, resilience, and regression test coverage.
* [ ] Required documentation updates.
* [ ] Required ADRs and implementation approval.

## 25. Decision and Governance

This document preserves online ordering as a future capability.

It does not:

* Authorize immediate implementation.
* Change the current cashier-based order intake process.
* Select a payment provider.
* Mandate a mobile application or messaging channel.
* Require microservices, queues, or a new infrastructure platform.
* Override existing order, inventory, security, subscription, or offline requirements.

When online ordering is prioritized, the team must create or update the relevant Business Analysis, System Analysis, Domain Analysis, Architecture, Database, Backend, Frontend, API, Security, Testing, Deployment, and Operations documentation.

Architecture decisions must be recorded in ADRs where appropriate. Conflicting existing requirements must be resolved explicitly rather than silently overridden.

## 26. Related Documents

* `01_Future_Roadmap_and_Evolution_Framework.md`
* `02_Deferred_Capabilities_and_Architecture_Reserve.md`
* `03_Multi_Cash_Register_Evolution.md`
* `04_Scale_Beyond_Initial_Branch_Limits.md`
* `06_Customer_CRM_Evolution.md`
* `07_Advanced_Delivery_Management.md`
* `08_Mobile_Customer_Application.md`
* `09_Messaging_and_Channel_Integrations.md`
* `12_Future_Architecture_Guardrails.md`
* `doc/11_Security/README.md`
* `doc/12_Testing/README.md`
* `doc/14_Operations/README.md`

The existing authoritative order, inventory, payment, subscription, and offline-operation documents must also be consulted before implementation.

## 27. Core Invariants

1. Online ordering remains deferred until separately approved.
2. The current cashier workflow remains supported.
3. Every order belongs to one authorized tenant and branch.
4. Customer-supplied branch identifiers are validated server-side.
5. Customer interfaces are not authoritative sources for prices or order state.
6. Every submission is validated against current business rules.
7. Repeated requests must not create duplicate orders.
8. Repeated callbacks must not create duplicate financial effects.
9. Inventory changes must follow authoritative order lifecycle rules.
10. Negative stock must not be introduced.
11. Order acceptance must be explicit and auditable.
12. Payment and fulfillment states must remain distinguishable.
13. Rejection and cancellation must follow approved financial rules.
14. Customer access must not expose another customer's order data.
15. Tenant and branch isolation must be preserved.
16. Public endpoints must not expose administrative operations.
17. Personal data collection must be limited to legitimate requirements.
18. Sensitive payment data must not be placed in ordinary logs.
19. Subscription expiry must not corrupt existing financial records.
20. Offline POS behavior must not depend on online ordering availability.
21. Online-order retries must be safe after uncertain network outcomes.
22. Stale menu data must not bypass server-side validation.
23. Branch unavailability must not cause silent reassignment.
24. Kitchen routing must follow approved branch configuration.
25. Product-specific printing rules must remain intact.
26. Recipe approval and access rules must remain intact.
27. Refund authorization must not be bypassed.
28. Audit trails must capture significant state transitions.
29. Reports must distinguish submission, acceptance, payment, and fulfillment.
30. External integrations must be treated as untrusted inputs until verified.
31. External provider failure must not silently corrupt internal records.
32. Recovery must not duplicate stock deductions or refunds.
33. Data retention and deletion rules must cover newly introduced customer data.
34. New customer channels must reuse authoritative business rules.
35. CRM and mobile applications must not become hidden prerequisites.
36. New infrastructure must be justified by approved requirements.
37. Performance claims must be supported by measurements and tests.
38. Migrations must preserve historical order meaning.
39. Rollbacks must preserve committed business and financial data.
40. Security controls must be proportionate to identified threats.
41. Order identifiers must not be treated as sufficient authorization.
42. The customer interface must clearly communicate uncertain outcomes.
43. Monitoring must minimize exposure of personal information.
44. Operational support procedures must exist before production launch.
45. Testing must cover duplicate submissions and concurrent stock changes.
46. Online ordering must not weaken existing register reconciliation.
47. No payment provider is selected by this document.
48. No particular application framework is mandated by this document.
49. Future requirements must be reflected in authoritative documentation.
50. Implementation requires explicit approval and appropriate architecture decisions.

---

**End of Document**

