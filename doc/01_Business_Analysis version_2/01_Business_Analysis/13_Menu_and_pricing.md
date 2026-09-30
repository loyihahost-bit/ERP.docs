# Menu and Pricing

**Document ID:** FF-BA-013
**Status:** Accepted
**Version:** 2.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for menu management, product availability, global and branch-level menu configuration, product pricing, branch-specific price overrides, order customization pricing, discounts, Sets, and optional product images.

The menu system must allow a business to maintain a consistent central product catalog while giving authorized users control over which products are available at individual branches.

Pricing and menu configuration must preserve historical integrity. Changes to current configuration must not silently rewrite historical orders or transactions.

---

## 2. Menu Model

The system uses a central business-level menu configuration.

The menu contains products that the business may make available for sale.

A branch may use a permitted subset of the global menu.

The menu system must distinguish between:

* product existence;
* global menu configuration;
* branch menu availability;
* product active/inactive state;
* operational availability;
* pricing;
* order-level discounts;
* order-level customization.

These are related but separate concepts.

---

## 3. Global Product Catalog

The business maintains a central product catalog.

Products in the catalog may include:

* raw materials;
* semi-finished products;
* finished products.

Only products appropriate for sale should normally be exposed through the sales menu.

The existence of a product in the catalog does not automatically mean that it is available for sale at every branch.

Product identity remains stable throughout its lifecycle.

---

## 4. Global Menu

The global menu represents the business-level menu configuration.

Authorized users may manage:

* menu categories;
* products;
* product ordering;
* product visibility;
* product activation;
* optional product images;
* global/default prices.

The global menu provides the common structure from which branch menus can be configured.

---

## 5. Branch Menu

Each branch may have its own active menu based on the business's global menu.

A branch menu determines which permitted products can be sold at that branch.

A product can therefore be:

* available globally but disabled at a branch;
* available globally and active at a branch;
* temporarily unavailable at a branch;
* inactive globally and therefore unavailable for normal branch sales.

Branch menu configuration must not create an independent product identity.

---

## 6. Branch Menu Permission

Only authorized employees may modify branch menu availability.

The permission system may determine whether an employee can:

* view menu configuration;
* activate products;
* deactivate products;
* change branch menu configuration;
* change pricing where permitted;
* manage categories;
* manage product images.

Menu access must respect branch scope.

An employee authorized for one branch must not automatically gain control over another branch's menu.

---

## 7. Menu Categories

The menu may be organized into categories.

Categories help employees find products efficiently during order entry.

The business may configure its own categories according to its operational needs.

Each product belongs to exactly one configured product/menu category.

Category configuration should remain lightweight and easy to manage.

Changing a category does not change:

* product identity;
* recipe;
* inventory;
* historical order data.

---

## 8. Product Activation

A product may be active or inactive.

An inactive product must not normally be available for new order entry.

Deactivating a product does not delete:

* the product;
* its recipe;
* inventory history;
* previous orders;
* historical reports;
* historical prices.

Historical transactions must remain intact.

---

## 9. Product Availability vs Menu Status

Product menu status and operational availability are separate concepts.

For example:

```text
Product exists
      ↓
Global menu enabled
      ↓
Branch menu enabled
      ↓
Operationally available
      ↓
Available for order
```

A product may be present in the menu but temporarily unavailable.

Operational unavailability must not require deleting or archiving the product.

---

## 10. Equipment Broken Availability

The system must support a temporary product availability state for operational problems.

One supported reason is:

**Equipment Broken**

When this state is active, the affected product or Set may be prevented from being used in new orders according to the applicable business rules.

The product itself remains intact.

Its:

* recipe;
* price;
* historical orders;
* inventory relationships;
* reports

must remain preserved.

Equipment Broken is an operational availability state, not deletion or archival.

---

## 11. Product Images

The business may optionally add product images.

Product images are not mandatory.

The image may be used in menu interfaces to help employees identify products quickly.

The system must not require an image for a product to be active.

Images must not affect:

* product identity;
* inventory;
* recipe calculation;
* pricing;
* order history.

---

## 12. Product Ordering

Authorized users may define the display order of menu products and categories.

The display order is a user-interface configuration.

Changing display order must not affect:

* product code;
* product identity;
* inventory;
* recipe;
* historical orders;
* price.

---

## 13. Product Visibility

Products may be hidden from normal menu interfaces when they are not intended for sale.

Visibility is separate from historical existence.

A hidden product must remain available for authorized management and historical purposes where appropriate.

A hidden product must not automatically be treated as deleted.

---

## 14. Product Price

Each sellable product must have a configured base price.

The price used during order processing must be clearly associated with:

* Business;
* Branch;
* Product;
* applicable price configuration.

The current business model uses prices that already include applicable taxes.

A separate tax-detail engine is not currently required.

Tax calculation by jurisdiction is outside the current scope.

---

## 15. Global Price

The business may define a global/default price for a product.

The global price provides the standard price used by branches unless a permitted branch-specific override exists.

Changes to the global price affect future applicable orders.

Changes to the global price must not silently rewrite historical order prices.

Historical orders retain the price that applied when the order was accepted or otherwise finalized according to the order lifecycle.

---

## 16. Branch-Specific Price Override

A branch may use a different price from the global product price when authorized.

Branch-specific price override requires the appropriate permission.

Example:

```text
Global Product Price
        ↓
Branch Override Exists?
        ↓
Yes → Branch Price
No  → Global Price
```

A branch price applies only to the relevant branch.

It must not modify the global product price.

---

## 17. Price Override Scope

A branch-specific price override must be associated with:

* Business;
* Branch;
* Product;
* Applicable price;
* Effective configuration;
* Relevant configuration history.

A price override in Branch A must not automatically affect Branch B.

Branch-specific pricing must respect employee branch scope and permissions.

---

## 18. Price Changes and Historical Orders

Changing a product price must affect future applicable orders.

It must not recalculate or rewrite completed historical orders.

Historical order records must retain:

* product;
* quantity;
* unit price;
* applicable discount;
* final order amount.

This ensures historical reports remain consistent.

---

## 19. Price Snapshot for Orders

When an order receives its applicable product price, the order must preserve the price used for that order.

The historical order must not depend on the current menu price for determining its original financial amount.

A later change to:

* global price;
* branch price;
* product configuration;
* recipe;
* Set configuration

must not change the historical price recorded in an existing historical order.

The technical implementation of price snapshots belongs to the System Analysis and Database documentation.

---

## 20. Price Changes and Open Orders

If a product price changes while an order is already open, the system must preserve a consistent price for the existing order.

The order must not unexpectedly change simply because the central product price was later modified.

The applicable price must be captured according to the defined order lifecycle and price snapshot rules.

---

## 21. Recipe Changes and Pricing

Recipe configuration and product pricing are related but separate business concepts.

A recipe change may affect future product cost and may affect configured pricing where the business chooses to update the product price.

The system must not automatically rewrite historical order prices because a recipe was changed.

Recipe changes become effective according to:

`12_Products_and_Recipes.md`

In particular, approved recipe changes become effective from the next applicable cash session.

---

## 22. Order Customization Pricing

Supported order customizations may affect the final order price.

Examples include:

* removing a priced recipe component;
* increasing a supported ingredient quantity;
* adding a supported extra.

The final calculated price must be recorded as part of the order.

The base product recipe and base product price must not be permanently modified by an individual customer order customization.

---

## 23. Removing a Recipe Component

When a supported recipe component is removed from an order unit:

* the base recipe remains unchanged;
* the inventory requirement for that component is reduced;
* the order customization is recorded;
* the price may be reduced if the component has an applicable price contribution.

The price reduction must follow the configured business pricing rule.

The change applies only to the affected order unit.

---

## 24. Increasing a Recipe Component

When a supported recipe component quantity is increased for an order unit:

* the base recipe remains unchanged;
* the additional quantity creates an additional inventory requirement;
* the additional stock must be available before acceptance;
* the applicable additional price must be calculated.

If the additional inventory is insufficient, the entire modification must be rejected.

No partial modification is allowed.

---

## 25. Custom Order Markup

The system supports a configurable markup for supported custom ingredient modifications.

The markup range is:

**0% to 100%**

The markup is applied to the applicable ingredient cost.

The business rule is:

```text
Final Custom Ingredient Price
=
Cost × (1 + Markup / 100)
```

For this calculation, the applicable cost reference is:

**Last Purchase Cost**

Example:

```text
Last Purchase Cost = 10,000
Markup = 20%

Final Custom Ingredient Price
= 10,000 × (1 + 20 / 100)
= 12,000
```

The markup must not modify the product's base recipe or global product price.

---

## 26. Unit-Level Customization

Each unit of the same product within one order may have different customization.

Example:

```text
2 × Lavash

Unit 1:
- normal sauce

Unit 2:
- no sauce
- extra meat
```

The system must calculate price and inventory effects for each customized unit independently where configurations differ.

The current business model does not require an **Apply to All** customization action.

---

## 27. Component Addition and Extras

Supported extras or add-ons may be added to an order.

When an extra is added:

* the order price must update according to the applicable pricing rule;
* inventory consumption must reflect the added quantity where applicable;
* the order must retain the customization history.

Extras do not automatically modify the base product recipe.

---

## 28. Component Swapping

The current system does not support direct component swapping.

For example:

```text
Remove A
Add B
```

must not automatically be treated as a recipe substitution mechanism.

Supported customization is based on:

* removing supported components;
* increasing supported component quantities;
* adding supported extras;
* comments for non-recipe changes.

Future customization models may expand this behavior if required.

---

## 29. Non-Recipe Changes

Not every operational customization requires a recipe modification.

If a requested change is not represented as a supported recipe component or extra, it may be recorded as an order comment.

Such a comment does not change:

* the official product recipe;
* the global recipe version;
* the product base price;
* the global menu configuration.

---

## 30. Discounts

Discounts are supported as part of order processing.

A discount affects the order price according to the applicable business rules and permissions.

Discounts must not modify:

* the global product price;
* the branch product price;
* the product recipe.

Example:

```text
Product Price
      ↓
Order
      ↓
Customization
      ↓
Discount
      ↓
Final Order Amount
```

Detailed discount rules are defined in:

`14_Payments_Discounts_and_Refunds.md`

---

## 31. Menu and Inventory Relationship

Menu availability does not guarantee inventory availability.

A product may be active in the menu while the required inventory is temporarily insufficient.

When the relevant order operation is performed, the inventory system must validate the required stock.

An operation requiring unavailable inventory must be blocked according to the inventory rules.

The system must never create negative stock.

Detailed inventory rules are defined in:

`11_Inventory_and_Warehouse.md`

---

## 32. Menu and Recipe Relationship

A product intended for normal sale may have an approved recipe.

Recipe approval and menu activation are separate business steps.

A product must not use an unapproved recipe for normal operations.

The menu should use the recipe version applicable to the current cash session.

Approved recipe changes become effective from the next applicable cash session.

Detailed recipe approval rules are defined in:

`12_Products_and_Recipes.md`

---

## 33. Menu and Branch Activation

A typical product activation flow is:

```text
Product Created
      ↓
Product Configured
      ↓
Recipe Approved (if required)
      ↓
Global Menu Available
      ↓
Branch Enabled
      ↓
Operationally Available
      ↓
Product Available for Sale
```

Not every product must pass through the same sequence if a recipe is not applicable.

Product activation, branch menu availability, and operational availability remain separate states.

---

## 34. Set Products in the Menu

A Set is a separate product configuration representing a bundle of component products.

A Set may be included in the global menu and enabled for selected branches.

A Set has:

* its own product identity;
* its own selling price;
* its own component configuration;
* its own availability state.

The Set is not a replacement for the recipes of its component products.

---

## 35. Set Pricing

A Set has its own selling price.

The Set selling price is independent from the individual component selling prices.

Changes to component product prices do not automatically rewrite historical Set order prices.

Historical Set orders retain their applicable Set price.

A Set may have branch-specific price override under the same permission model as other sellable products.

---

## 36. Set Composition and Pricing

A Set's component composition must remain stable for its applicable configuration.

The customer cannot replace one Set component with another product during normal order processing.

If the Set composition changes:

1. a new Set configuration/version is created;
2. the applicable approval is completed;
3. the new configuration becomes effective from the next applicable cash session;
4. future orders use the new configuration;
5. historical orders retain the previous configuration.

Underlying recipe changes of component products do not silently rewrite historical Set configurations.

---

## 37. Set Inventory Availability

When a Set is sold, inventory availability must be checked for its configured component products.

If any mandatory component required by the Set cannot be supplied, the Set sale must be blocked.

The system must not create negative inventory.

The inventory consumption relationship is:

```text
Set
 ↓
Component Product
 ↓
Applicable Recipe
 ↓
Inventory Requirement
```

Detailed Set inventory rules are defined in:

`11_Inventory_and_Warehouse.md`

---

## 38. Product and Set Unavailability

A product or Set may be temporarily unavailable because of:

* Equipment Broken;
* insufficient required inventory;
* branch menu deactivation;
* product inactive state;
* other explicitly supported operational availability states.

These states must not destroy product or Set history.

Inventory shortage and Equipment Broken are operational conditions and are distinct from archival.

---

## 39. Menu Changes

Menu changes may include:

* activating a product;
* deactivating a product;
* changing category;
* changing display order;
* changing product image;
* changing global price;
* changing branch price;
* changing branch availability;
* changing Set configuration.

Important configuration changes must be traceable.

Historical transactions must not be rewritten because the menu changed later.

---

## 40. Menu Change Permissions

The permission system must determine who can change menu configuration.

Permissions may be separated for:

* viewing the menu;
* managing products;
* managing categories;
* changing prices;
* changing branch menu availability;
* managing product images;
* managing Sets.

The system must not assume that every employee who can process orders can modify menu configuration.

Price override permission is separate from normal order-processing permission.

---

## 41. Owner and Manager Access

The Owner may configure menu-related permissions for employees.

A Manager may manage menu functions only when the Owner has granted the relevant permission.

A Manager's authority remains limited by:

* assigned permissions;
* branch scope;
* business scope;
* subscription entitlement.

A Manager cannot use menu permissions to bypass other business security rules.

---

## 42. Offline Menu Usage

Authorized trusted devices may use the latest valid menu configuration while operating offline.

The offline device must preserve the menu state that was valid under its offline authorization.

Offline operation must not allow unauthorized menu modification.

If menu configuration changes while a device is offline, the device may temporarily continue using its valid offline configuration until synchronization or configuration refresh occurs.

The server becomes authoritative after reconnection.

Offline operation must not bypass:

* subscription restrictions;
* employee permissions;
* branch scope;
* product availability rules.

---

## 43. Offline Pricing

Offline POS operation may use the latest valid pricing configuration available to the trusted device under its valid offline authorization.

The offline device must preserve the price configuration applicable to the transaction.

Offline order records must retain the price used when the transaction was accepted.

After synchronization, the server must validate the transaction against the applicable historical configuration.

A later price change must not cause an already accepted offline order to be repriced.

---

## 44. Menu Synchronization

Menu-related changes made through authorized offline operations, where supported, must synchronize with the central system.

Synchronization must preserve:

* business;
* branch;
* product;
* configuration change;
* responsible employee;
* device;
* timestamp;
* transaction or change identity.

Duplicate synchronization must not create duplicate configuration changes.

The server remains authoritative after synchronization.

Detailed synchronization rules are defined in:

`07_Offline_Operation_and_Synchronization.md`

---

## 45. Business and Branch Isolation

Menu data must be isolated by business.

Branch-specific menu configuration must be isolated by branch.

Employees must only see or modify menu information within their authorized scope.

Exports, reports, offline data, background operations, and synchronization must follow the same isolation rules.

A branch price or branch menu configuration must never leak into another branch.

---

## 46. Subscription and Menu Access

Menu functionality is subject to the business subscription.

Employee permissions are a separate control layer.

A user may perform a menu operation only when:

1. the subscription allows the relevant functionality; and
2. the employee has the required permission.

When the subscription expires, modifying functions are blocked according to the subscription lifecycle rules.

Historical menu and product information remains viewable during the applicable read-only period.

Offline operation must not bypass subscription restrictions.

---

## 47. Product Archive

Products that are no longer actively used should be archived rather than physically deleted when historical relationships exist.

Archiving must preserve:

* product identity;
* historical prices;
* historical orders;
* recipe history;
* inventory history;
* reports.

An archived product must not automatically become available for new orders.

---

## 48. Historical Price Information

The system must preserve relevant historical pricing information.

Historical information may be required to understand:

* completed orders;
* reports;
* price changes;
* branch-specific overrides;
* discounts;
* refunds;
* Set sales.

Changing the current price must not destroy the ability to determine which price applied to a historical order.

---

## 49. Price Configuration Effective Time

Price changes are configuration changes and must have a defined effective point.

A price change intended for future operations must not silently change an already accepted order.

Where a price change is configured during an active cash session, the system must preserve the existing order price snapshots.

The exact technical implementation of configuration versioning belongs to the System Analysis and Database documentation.

---

## 50. Auditability

Important menu and pricing changes must be traceable.

The system should preserve:

* actor;
* timestamp;
* business;
* branch where applicable;
* product;
* previous value;
* new value;
* action type;
* effective time;
* reason/comment where required.

Important changes must not be silently overwritten.

Historical price configurations must remain available where required for audit and reporting.

---

## 51. Reporting

Menu and pricing information may be used in reports including:

* product sales;
* branch sales;
* price history;
* menu availability;
* product configuration;
* order reports;
* discount reports;
* Set sales;
* branch price overrides.

Reports must use the applicable historical order price rather than the current product price when analyzing completed historical transactions.

---

## 52. Performance Requirements

Menu operations must remain fast enough for normal POS usage.

The system should avoid unnecessary loading of:

* inactive products;
* irrelevant branch products;
* unauthorized data;
* unnecessary image data.

Menu configuration must not introduce noticeable delays into normal order entry.

Price lookup and customization calculation must remain lightweight enough for normal POS hardware.

The system should remain usable on lightweight restaurant hardware.

---

## 53. Business Rules Summary

| Area                      | Rule                                        |
| ------------------------- | ------------------------------------------- |
| Global menu               | Managed at business level                   |
| Branch menu               | Branch-specific availability                |
| Product types             | Raw, semi-finished, finished                |
| Product category          | Exactly one category                        |
| Product activation        | Separate from product existence             |
| Product availability      | Separate from menu activation               |
| Equipment Broken          | Supported temporary unavailable state       |
| Product images            | Optional                                    |
| Categories                | Configurable                                |
| Display order             | Configurable                                |
| Global price              | Default business price                      |
| Branch price              | Optional authorized override                |
| Branch price scope        | Applies only to that branch                 |
| Taxes                     | Included in product price for current scope |
| Tax engine                | Not currently required                      |
| Historical price          | Must be preserved                           |
| Price snapshot            | Required for historical orders              |
| Discounts                 | Applied at order level                      |
| Recipe relationship       | Approved recipe required where applicable   |
| Recipe effective time     | Next applicable cash session                |
| Inventory relationship    | Stock checked during operation              |
| Negative stock            | Not allowed                                 |
| Custom component removal  | Supported                                   |
| Custom component increase | Supported                                   |
| Custom extras             | Supported                                   |
| Custom markup             | 0–100%                                      |
| Custom markup cost        | Last Purchase Cost                          |
| Custom markup formula     | `Cost × (1 + Markup / 100)`                 |
| Component swapping        | Not currently supported                     |
| Unit-level customization  | Supported                                   |
| Apply to All              | Not required                                |
| Set                       | Separate bundle product                     |
| Set price                 | Independent selling price                   |
| Set composition           | Versioned/stable                            |
| Set changes               | Effective next applicable cash session      |
| Set component swapping    | Not supported                               |
| Set unavailable component | Sale blocked                                |
| Offline menu              | Latest valid configuration available        |
| Offline pricing           | Latest valid configuration available        |
| Permissions               | Role, employee and branch scope based       |
| Subscription              | Separate from employee permissions          |
| Product archive           | Used when historical relationships exist    |
| Audit                     | Important changes preserved                 |
| Performance               | Lightweight and POS-friendly                |

---

## 54. Business Boundaries

The current Menu and Pricing scope does **not** define:

* online customer ordering;
* customer-facing mobile applications;
* customer-specific pricing;
* loyalty pricing;
* dynamic pricing;
* automatic competitor price matching;
* advanced promotion engines;
* tax calculation by jurisdiction;
* multi-currency pricing;
* supplier pricing;
* complex price books;
* customer CRM.

These capabilities may be considered in future documentation if business requirements justify them.

---

## 55. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `09_Cash_Register_and_Cash_Sessions.md`
* `10_Shift_Handover.md`
* `11_Inventory_and_Warehouse.md`
* `12_Products_and_Recipes.md`
* `14_Payments_Discounts_and_Refunds.md`
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`

