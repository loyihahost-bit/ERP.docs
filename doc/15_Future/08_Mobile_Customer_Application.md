# Mobile Customer Application

**Document ID:** FUT-08
**Status:** Accepted
**Version:** 1.0
**Last Updated:** 2026-10-09
**Category:** Future Product Capabilities and Architecture

## 1. Purpose

This document defines the future evolution path for a customer-facing mobile application for the FastFood ERP platform.

The application may eventually allow customers to discover restaurant branches, browse menus, place orders, track fulfillment, manage customer profiles, use loyalty rewards, and receive relevant notifications.

This document is a future planning record. It does not authorize immediate implementation or change current authoritative requirements.

## 2. Scope

This document covers:

* Customer-facing mobile application goals.
* Supported customer journeys.
* Account registration and authentication.
* Branch discovery and menu browsing.
* Cart and online order submission.
* Order history and tracking.
* Customer profile and preferences.
* Loyalty and rewards integration.
* Delivery tracking and notifications.
* Mobile application security and privacy.
* API integration and backend responsibilities.
* Reliability, accessibility, performance, and release management.
* Integration with future CRM, online ordering, delivery management, and messaging capabilities.

The document does not select a mobile framework, operating-system target, payment provider, application store strategy, or third-party service.

## 3. Current Baseline

The current FastFood ERP supports restaurant operations through its existing POS and related workflows.

Current customer-facing capabilities do not require a dedicated mobile application. Orders are currently accepted through the cashier workflow, including dine-in, takeaway, and phone delivery.

Online ordering, advanced CRM, loyalty programs, and advanced delivery management are deferred capabilities described in their respective Future documents.

Therefore:

1. The mobile application is not required for the existing POS to operate.
2. Existing restaurant operations must not depend on customers installing an application.
3. Existing cashier-based order intake remains supported.
4. Mobile functionality must use approved backend business rules rather than independently implementing authoritative order, payment, inventory, or subscription logic.
5. No new infrastructure or external integration is required solely by this document.

## 4. Product Goals

A future mobile application should provide customers with a convenient and secure way to interact with participating restaurant businesses.

Potential goals include:

* Discover eligible restaurants and branches.
* Browse branch-specific menus and prices.
* Place and review online orders.
* View order status and relevant fulfillment updates.
* Access authorized order history.
* Manage customer profile information.
* Use eligible loyalty rewards.
* Save delivery information when supported and appropriate.
* Receive transactional notifications.
* Manage communication preferences.
* Access customer support information.

The application should be useful without requiring every future capability to be implemented at launch.

## 5. Product Boundaries

The customer application is a presentation and interaction channel, not an independent business system.

The backend remains authoritative for:

* Tenant and branch eligibility.
* Product availability.
* Pricing and discounts.
* Order validation and acceptance.
* Payment state.
* Inventory rules.
* Delivery eligibility and fulfillment state.
* Customer identity and permissions.
* Loyalty balances and transactions.
* Subscription-controlled business capabilities.

The application must not treat locally stored data, client-calculated prices, or user-visible status as proof that a business operation succeeded.

Every state-changing operation must be validated by the backend.

## 6. Potential Customer Journeys

A future application may support the following journeys.

### 6.1 Discover a restaurant

1. Open the application.
2. Search or browse participating restaurant businesses.
3. Select a restaurant and eligible branch.
4. Review service availability and menu information.
5. Select an available ordering method.

Location-based discovery, if supported, must require appropriate permission and provide a manual alternative.

### 6.2 Browse and order

1. Browse the selected branch's menu.
2. Select products and permitted customizations.
3. Add items to the cart.
4. Review current prices, discounts, fees, and total.
5. Provide required order and fulfillment details.
6. Submit the order.
7. Receive a clear submission result.
8. Follow the approved payment and order-acceptance process.

The final workflow must follow `05_Online_Ordering_Evolution.md`.

### 6.3 Track an order

1. Open an authorized order.
2. View its current confirmed state.
3. Review relevant preparation or delivery updates.
4. Receive notification of significant changes, where enabled.
5. Access support or cancellation options when permitted.

The application must distinguish a submitted order from an accepted, paid, prepared, dispatched, or completed order.

### 6.4 Manage a customer profile

Where CRM is enabled, a customer may view or update permitted profile fields, contact information, preferences, and saved addresses.

Changes must follow the backend's verification and authorization rules.

### 6.5 Use loyalty rewards

Where an approved loyalty program exists, a customer may view an eligible balance, available rewards, and relevant transaction history.

The application must obtain authoritative loyalty information from the backend and must not independently calculate or authorize redemptions.

## 7. Account and Authentication Model

The final account model must be approved before implementation.

Possible approaches include:

* Guest access for browsing and eligible ordering.
* Account registration using a verified contact method.
* Sign-in for order history and customer-specific features.
* Optional additional authentication for sensitive operations.

No single authentication method is selected by this document.

### 7.1 Guest access

Browsing and other low-risk functionality should not require account creation unless a specific business or security requirement justifies it.

If guest ordering is supported, the application must clearly explain which order information can be accessed without an account and how the customer can retrieve the result safely.

### 7.2 Account recovery

Account recovery must verify control of an approved recovery channel and protect against account enumeration and unauthorized access.

A verified phone number or email address should not automatically be treated as proof of legal identity.

### 7.3 Session management

The implementation must define:

* Session creation and expiration.
* Secure token storage.
* Logout behavior.
* Token revocation.
* Recovery after a lost device.
* Reauthentication for sensitive actions.
* Behavior after credentials or contact details change.

Authentication tokens must not be stored in insecure application storage or exposed through logs.

### 7.4 Shared devices

The application must consider customers using shared or borrowed devices.

It should provide clear logout behavior and avoid exposing sensitive customer history after a session ends.

## 8. Restaurant and Branch Discovery

The application may provide search, browsing, or location-assisted discovery.

Branch results must reflect authoritative backend rules, including:

* Restaurant and branch status.
* Service availability.
* Supported order types.
* Operating hours.
* Menu availability.
* Delivery coverage, if enabled.

Location permission must be optional when a manual branch-selection alternative can provide the required functionality.

The application must not silently change the selected branch during checkout.

A branch that cannot accept the requested service must be presented as unavailable or require explicit customer selection of another eligible branch.

## 9. Menu, Cart, and Pricing

The application must obtain menu information from authorized backend APIs.

It may cache menu information for display and responsiveness, but cached information must be clearly treated as potentially stale.

Before order submission, the backend must revalidate:

* Tenant and branch.
* Product activation and availability.
* Quantity and permitted customization.
* Current price.
* Discounts and eligibility.
* Applicable fees.
* Order total.
* Any required stock constraints.

The application must not be able to bypass price or availability rules by modifying local data or network requests.

If the order changes materially during checkout, the customer must receive a clear explanation and confirm the revised order before submission.

The cart is a temporary interaction state. The authoritative order is created and managed by the backend.

## 10. Order Submission and Reliability

Mobile networks can be interrupted, applications can be suspended, and customers may repeat actions when a response is delayed.

The application must be designed for these conditions.

Requirements include:

* A visible submission-in-progress state.
* Prevention of accidental repeated submission.
* Idempotent backend submission.
* A safe way to recover an uncertain result.
* Clear differentiation between failure and an unknown outcome.
* Recovery after application restart.
* Safe handling of interrupted payment workflows.

If the application cannot determine whether an order was created, it must not blindly create a new order. It should retrieve the existing result using an approved request or order reference.

Client-generated request identifiers may support correlation and idempotency, but they must not replace server-side identifiers or authorization.

The application must never claim success solely because a button was pressed or a request was sent.

## 11. Order History and Tracking

When CRM or authorized customer history is available, the application may show relevant orders.

The display may include:

* Order reference.
* Restaurant and branch.
* Order date.
* Products and quantities.
* Authoritative order total.
* Current order status.
* Fulfillment method.
* Payment status, where appropriate.
* Relevant refund or cancellation information.

The application must not expose an order merely because a user knows its identifier.

The backend must verify that the customer is authorized to access the order.

Historical orders must remain interpretable even if menu items, prices, customer profiles, or branch configurations later change.

Tracking updates must be derived from authoritative events. The application must distinguish a confirmed status from a stale or temporarily unavailable status.

## 12. Payments

Online payment support is a future capability.

The mobile application must not handle payment in a way that bypasses approved backend and provider controls.

Before implementation, the project must define:

* Supported payment methods.
* Payment authorization and confirmation behavior.
* Provider integration and callback validation.
* Handling of delayed, failed, or uncertain payment results.
* Cancellation and refund flows.
* Payment history visibility.
* Requirements for payment credentials and sensitive data.

No payment provider or payment sequence is selected by this document.

The application must not store sensitive payment credentials in ordinary application storage or logs.

Payment state must come from authoritative payment records rather than a client-side success screen.

## 13. Customer Profile and Preferences

If CRM is enabled, the application may allow customers to manage approved profile information.

Potential fields include:

* Display name.
* Verified contact methods.
* Preferred language.
* Saved delivery addresses.
* Communication preferences.
* Relevant account settings.

Only fields with a defined business purpose should be collected.

Profile updates must be validated by the backend. A change to contact information must not silently transfer ownership of existing orders or loyalty balances.

Saved addresses must be protected and available only to the authorized customer and permitted operational roles.

Customer profile capabilities are governed by `06_Customer_CRM_Evolution.md`.

## 14. Loyalty and Rewards

The application may provide a customer-facing interface for an approved loyalty program.

Potential features include:

* Viewing the current points balance.
* Reviewing eligible rewards.
* Viewing earned and redeemed points.
* Applying a permitted reward during checkout.
* Reviewing relevant program rules and expiration information.

All eligibility, calculation, reservation, redemption, and reversal rules must be enforced by the backend.

The application must not determine the authoritative balance independently.

Duplicate submissions must not award or redeem rewards more than once. Refunds and cancellations must follow the approved loyalty ledger rules.

Offline redemption must not be enabled unless an explicit design proves that balance consistency and duplicate prevention can be maintained.

## 15. Delivery and Location Features

If advanced delivery management is enabled, the application may support:

* Entering and managing delivery addresses.
* Viewing delivery eligibility.
* Receiving delivery status updates.
* Viewing approved delivery estimates.
* Accessing courier tracking when explicitly supported.

Location-based functionality must use the minimum permissions required.

Live courier tracking, if implemented, must follow the delivery platform's privacy, access, retention, and location-sharing policies.

The application must clearly distinguish estimated arrival information from confirmed fulfillment status.

A map or tracking provider outage must not prevent customers from accessing other available order information.

Delivery functionality is governed by `07_Advanced_Delivery_Management.md`.

## 16. Notifications

The application may support push notifications and other approved communication channels.

Potential notification events include:

* Order submission or acceptance.
* Preparation updates.
* Delivery assignment or progress.
* Order completion.
* Payment or refund updates.
* Relevant loyalty events.

The final notification policy must distinguish transactional messages from promotional messages.

Marketing notifications must follow applicable consent and communication-preference requirements.

Notifications must not expose sensitive order or customer information on a device lock screen by default without a deliberate, privacy-reviewed design.

Notification delivery is not proof that the customer received or read the message.

The application must handle notification permission being denied, disabled, or revoked without breaking the core ordering workflow.

## 17. API and Backend Integration

The application should communicate with the backend through documented, versioned, authenticated APIs appropriate to each operation.

The mobile client must not connect directly to the production database.

Backend APIs must enforce:

* Authentication and authorization.
* Tenant and branch isolation.
* Input validation.
* Rate limits and abuse protection.
* Idempotency for sensitive state-changing operations.
* Safe error responses.
* Audit logging where required.
* Version compatibility policies.

The client must not be trusted to provide authoritative prices, permissions, loyalty balances, payment status, or order state.

External integrations must be accessed through approved backend-controlled interfaces rather than embedding privileged credentials in the application.

## 18. Security and Privacy

A future mobile application expands the platform's attack surface and introduces device-specific risks.

The implementation must consider:

* Secure authentication and session handling.
* Protected local storage.
* Transport encryption.
* Appropriate API authorization.
* Token expiration and revocation.
* Account recovery abuse.
* Sensitive information in logs and crash reports.
* Rooted or compromised devices where relevant to the risk model.
* Dependency and application security updates.
* Deep-link validation.
* Secure handling of external redirects.
* Customer data access and deletion requests.
* Lost-device scenarios.
* Protection against unauthorized order enumeration.

Security controls should be proportionate to the information and operations exposed.

The application must not rely on hiding a UI control as the only authorization mechanism.

The backend must independently authorize every sensitive operation.

## 19. Local Storage and Offline Behavior

The application may cache limited information to improve usability.

Potential cached data includes:

* Public or previously retrieved menu information.
* Non-sensitive interface preferences.
* A temporary cart.
* A limited view of previously retrieved order information, if approved.

The implementation must define:

* Which data may be cached.
* Cache expiration and refresh behavior.
* Data removal on logout.
* Protection for any locally stored sensitive information.
* Behavior when account access is revoked.
* Handling of stale menu and price data.
* Whether a cart can be restored after a restart.

The application must not imply that a locally stored cart is an accepted order.

Offline order submission, payment processing, and loyalty redemption must not be assumed supported.

The existing offline POS capability remains independent of the customer application.

## 20. Accessibility and Usability

The application should be usable by customers with different levels of technical experience and accessibility needs.

The design should consider:

* Readable text and clear contrast.
* Screen-reader support.
* Accessible labels for controls.
* Predictable navigation.
* Clear validation messages.
* Error recovery without losing valid customer input.
* Support for the approved interface languages.
* Appropriate touch target sizes.
* Reduced-motion preferences where relevant.
* Clear loading, empty, success, and failure states.

Important business information, such as prices, fees, branch availability, and order status, must not depend only on color or animation.

The final accessibility and localization requirements must be reviewed before implementation.

## 21. Performance and Resource Usage

The application should remain responsive on supported devices and network conditions.

The design should consider:

* Application download size.
* Startup time.
* Menu loading and image transfer.
* API latency.
* Cache efficiency.
* Memory and battery use.
* Network interruptions.
* Pagination of order history.
* Image resizing and delivery.
* Crash and error rates.

Performance expectations must be defined and measured on representative devices and network conditions.

The application must not require powerful devices merely to browse menus or view order status.

Additional backend services or infrastructure must be justified by actual requirements and measurements.

No specific performance guarantee is established by this document.

## 22. Subscription and Capability Availability

The customer application may interact with multiple independent restaurant tenants, each with different enabled capabilities.

The backend must determine which features are available for the selected restaurant and branch.

Potential differences may include:

* Online ordering enabled or disabled.
* Supported order types.
* Loyalty availability.
* Delivery tracking availability.
* Customer account functionality.
* Available payment methods.

The application must not assume that all tenants support all features.

When a capability is disabled, the interface should explain the unavailable function where appropriate without exposing internal administrative or subscription information unnecessarily.

Subscription changes must not corrupt existing orders, payments, customer profiles, or loyalty records.

The exact customer-facing behavior during subscription expiration requires separate approval.

## 23. Analytics and Privacy

The application may collect limited operational telemetry to support reliability and usability improvements.

Potential events include:

* Application startup and crash.
* Menu loading outcome.
* Order submission outcome.
* API latency.
* Notification handling outcome.
* Supported feature usage.

Analytics must have a defined purpose, access policy, and retention period.

Customer identity, delivery address, authentication tokens, payment credentials, and other sensitive information must not be included in analytics events unless an explicitly approved and lawful requirement exists.

Aggregated measurements should be preferred when individual customer identification is unnecessary.

The system must distinguish operational telemetry from marketing tracking and apply the relevant consent and privacy rules.

## 24. Release and Compatibility Strategy

Before production release, the project must define:

* Supported mobile operating systems and versions.
* Distribution channels.
* Application signing and release credentials.
* Versioning policy.
* Backend API compatibility.
* Minimum supported application version.
* Security update procedures.
* Crash monitoring.
* Rollback or mitigation procedures.
* Customer support procedures.

Mobile applications may remain installed after a backend deployment, so API compatibility must be considered explicitly.

A new backend release must not assume every customer has immediately updated the application.

If an old application version must be blocked for a security or integrity reason, the system should provide a controlled upgrade or support message where possible.

Release and rollback procedures must not corrupt orders or payment records.

## 25. Testing Requirements

A future mobile application must include appropriate testing for the following areas.

### 25.1 Functional testing

* Restaurant and branch selection.
* Menu browsing and stale-data handling.
* Cart management and price validation.
* Order submission and status recovery.
* Authentication and account recovery.
* Customer profile updates.
* Order history access.
* Loyalty integration, if enabled.
* Notifications and permission changes.

### 25.2 Security testing

* Unauthorized API requests.
* Cross-tenant and cross-customer access attempts.
* Token storage and revocation.
* Deep-link and external redirect handling.
* Sensitive information in logs and crash reports.
* Local data removal on logout.
* Order enumeration and repeated submissions.

### 25.3 Reliability testing

* Network loss during submission.
* Application suspension or termination.
* Restart after an uncertain outcome.
* Delayed payment confirmation.
* Duplicate requests.
* Outdated application versions.
* Notification provider failure.
* Backend outage and recovery.

### 25.4 Compatibility and usability testing

* Supported devices and operating-system versions.
* Different screen sizes.
* Slow and unstable network conditions.
* Accessibility tools.
* Supported languages.
* Low-resource device behavior.

### 25.5 Regression testing

Existing cashier ordering, kitchen workflows, inventory, payments, refunds, register reconciliation, subscription enforcement, and offline synchronization must continue to satisfy their authoritative requirements.

## 26. Implementation Readiness Checklist

Before enabling the customer mobile application in production, the project must approve the relevant items:

* [ ] Product scope and supported customer journeys.
* [ ] Supported operating systems and devices.
* [ ] Guest and registered customer access model.
* [ ] Authentication, recovery, and session policies.
* [ ] Restaurant and branch discovery rules.
* [ ] Menu, pricing, and cart behavior.
* [ ] Online order submission and idempotency.
* [ ] Payment integration and recovery, if included.
* [ ] Order history and tracking authorization.
* [ ] CRM and profile integration, if included.
* [ ] Loyalty integration, if included.
* [ ] Delivery and location features, if included.
* [ ] Notification and marketing consent rules.
* [ ] Local storage and offline behavior.
* [ ] Security and privacy assessment.
* [ ] API compatibility and versioning.
* [ ] Accessibility and localization requirements.
* [ ] Performance and device compatibility targets.
* [ ] Release, monitoring, support, and rollback procedures.
* [ ] Database or backend migration requirements.
* [ ] Functional, security, reliability, and regression tests.
* [ ] Updates to authoritative documentation and ADRs.
* [ ] Explicit implementation approval.

## 27. Decision and Governance

This document defines a future direction for a customer-facing mobile application.

It does not:

* Authorize immediate implementation.
* Require customers to use a mobile application.
* Select a mobile development framework.
* Select a payment provider or notification provider.
* Require online ordering, CRM, loyalty, or advanced delivery to be implemented first.
* Mandate offline order submission.
* Require live location tracking.
* Override existing order, inventory, payment, security, subscription, or offline requirements.

The project must separately approve the product scope, technology choices, architecture, security model, and release plan.

When implementation is authorized, the relevant Business Analysis, System Analysis, Domain Analysis, Architecture, Database, Backend, Frontend, API, Security, Testing, Deployment, and Operations documentation must be updated. Relevant architecture decisions must be recorded in ADRs.

## 28. Related Documents

* `01_Future_Roadmap_and_Evolution_Framework.md`
* `02_Deferred_Capabilities_and_Architecture_Reserve.md`
* `05_Online_Ordering_Evolution.md`
* `06_Customer_CRM_Evolution.md`
* `07_Advanced_Delivery_Management.md`
* `09_Messaging_and_Channel_Integrations.md`
* `10_Advanced_AI_and_Intelligent_Automation.md`
* `12_Future_Architecture_Guardrails.md`
* `doc/11_Security/README.md`
* `doc/12_Testing/README.md`
* `doc/14_Operations/README.md`

The authoritative order, customer data, permissions, payment, subscription, and data lifecycle documentation must also be consulted before implementation.

## 29. Core Invariants

1. The customer mobile application remains deferred until separately approved.
2. Existing POS operations must not depend on the application.
3. The cashier-based order intake workflow remains supported.
4. The backend remains authoritative for business state.
5. Client-calculated prices must not be trusted.
6. Every order submission must be validated server-side.
7. Duplicate submissions must not create duplicate orders.
8. Uncertain submission outcomes must be recoverable safely.
9. Customer access must be authorized for each requested order.
10. Tenant and branch isolation must be preserved.
11. Customer identity must not be inferred solely from a contact value.
12. Guest access remains possible where approved.
13. Sensitive authentication tokens must be protected.
14. Account recovery must resist unauthorized access.
15. Local data must be handled according to approved security rules.
16. Logout and account revocation must follow defined data-removal rules.
17. Cached menu data must not bypass current validation.
18. Local cart contents must not be represented as an accepted order.
19. Payment state must come from authoritative payment records.
20. Payment retries must not create duplicate financial effects.
21. Loyalty balances and redemptions must be backend-controlled.
22. Offline loyalty redemption requires explicit consistency guarantees.
23. Order tracking must reflect authoritative events.
24. Customer-visible status must distinguish pending and confirmed states.
25. Location permissions must be proportionate to the feature.
26. Live tracking requires a separate privacy and operational review.
27. Notifications must not be treated as proof of delivery or reading.
28. Transactional and promotional communications must be distinguished.
29. Marketing preferences must follow approved consent and legal rules.
30. Customer profile fields must have defined purposes.
31. Customer data must follow retention and deletion policies.
32. External provider credentials must not be embedded as privileged client secrets.
33. APIs must enforce authorization independently of the user interface.
34. Client versions must be considered during backend releases.
35. Subscription differences must be handled without assuming universal capabilities.
36. Subscription changes must not corrupt committed business records.
37. Analytics must minimize personal and sensitive information.
38. Performance requirements must be measured on representative devices.
39. Accessibility and localization must be considered before launch.
40. Additional infrastructure requires justification and approval.
41. Mobile application failure must not corrupt order or inventory records.
42. Release rollback must preserve committed financial data.
43. Existing offline POS synchronization must remain correct.
44. Security testing must include local storage and API authorization.
45. Recovery must not create duplicate payments, orders, or rewards.
46. Customer data must not be exposed through notifications by default.
47. No particular mobile framework is selected by this document.
48. No specific payment or notification provider is selected by this document.
49. Future requirements must be reflected in authoritative documentation.
50. Implementation requires explicit approval and appropriate architecture decisions.

---

**End of Document**

