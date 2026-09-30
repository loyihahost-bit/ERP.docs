# Menu and Pricing

**Document ID:** FF-BA-013
**Status:** Draft
**Version:** 1.0
**Scope:** Business Analysis
**Parent Document:** `01_Product_Overview.md`

---

## 1. Purpose

This document defines the business requirements for menu management, product availability in menus, global and branch-level menu configuration, product pricing, branch-specific price overrides, and optional product images.

The menu system must allow a business to maintain a consistent central product catalog while giving authorized users control over which products are available at individual branches.

---

## 2. Menu Model

The system uses a central business-level menu configuration.

The menu contains the products that the business can make available for sale.

A branch may use a permitted subset of the global menu.

The menu system must distinguish between:

* product existence;
* global menu configuration;
* branch menu availability;
* product operational availability;
* pricing.

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

---

## 4. Global Menu

The global menu represents the business-level menu configuration.

Authorized users may manage:

* menu categories;
* products;
* product ordering;
* product visibility;
* product activation;
* optional product images.

The global menu provides the common structure from which branch menus can be configured.

---

## 5. Branch Menu

Each branch may have its own active menu based on the business's global menu.

A branch menu determines which permitted products can be sold at that branch.

A product can therefore be:

* available globally but disabled at a branch;
* available globally and active at a branch;
* temporarily unavailable at a branch.

Branch menu configuration must not create an independent product identity.

---

## 6. Branch Menu Permission

Only authorized employees may modify branch menu availability.

The permission system determines whether an employee can:

* view menu configuration;
* activate products;
* deactivate products;
* change branch menu configuration;
* change pricing where permitted.

Menu access must respect branch scope.

An employee authorized for one branch must not automatically gain control over another branch's menu.

---

## 7. Menu Categories

The menu may be organized into categories.

Categories help employees find products efficiently during order entry.

The business may configure its own categories according to its operational needs.

A product may belong to the appropriate configured category.

Category configuration should remain lightweight and easy to manage.

---

## 8. Product Activation

A product may be active or inactive.

An inactive product must not normally be available for new order entry.

Deactivating a product does not delete:

* the product;
* its recipe;
* inventory history;
* previous orders;
* historical reports.

Historical transactions must remain intact.

---

## 9. Product Availability vs Menu Status

Product menu status and operational availability are separate concepts.

For example:

```text id="8k8s1p"
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

For example, if required equipment is broken, the product may be marked unavailable without deleting it from the system.

---

## 10. Equipment Broken Availability

The system must support a temporary product availability state for operational problems.

One supported reason is:

**Equipment Broken**

When this state is active, the product may be prevented from being used in new orders according to the applicable business rules.

The product itself remains intact.

Its:

* recipe;
* price;
* historical orders;
* inventory relationships;
* reports

must remain preserved.

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
* historical orders.

---

## 13. Product Visibility

Products may be hidden from normal menu interfaces when they are not intended for sale.

Visibility is separate from historical existence.

A hidden product must remain available for authorized management and historical purposes where appropriate.

---

## 14. Product Price

Each sellable product must have a configured price.

The price used during order processing must be clearly associated with the relevant product and branch context.

The current business model uses prices that already include applicable taxes.

A separate tax-detail engine is not currently required.

---

## 15. Global Price

The business may define a global/default price for a product.

The global price provides the standard price used by branches unless a permitted branch-specific override exists.

Changes to the global price must not silently rewrite historical order prices.

Historical orders retain the price that applied when the order was processed.

---

## 16. Branch-Specific Price Override

A branch may use a different price from the global product price when authorized.

Branch-specific price override requires the appropriate permission.

Example:

```text id="h4c6rm"
Global Product Price
        ↓
Branch Override Allowed?
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
* applied price;
* applicable discounts;
* final order amount.

This ensures historical reports remain consistent.

---

## 19. Price Changes and Open Orders

If a product price changes while an order is already open, the system must preserve a consistent price for the existing order.

The order must not unexpectedly change simply because the central product price was later modified.

The exact technical mechanism for price snapshots belongs to the system design documentation.

---

## 20. Recipe Changes and Pricing

Recipe configuration and product pricing are related but separate business concepts.

A recipe change may affect future product cost and may affect configured pricing where the business chooses to update the product price.

The system must not automatically rewrite historical order prices because a recipe was changed.

Detailed recipe rules are defined in:

`12_Products_and_Recipes.md`

---

## 21. Price and Order Customization

Supported order customizations may affect the final order price.

For example:

* removing a priced recipe component may reduce the price;
* adding a supported extra may increase the price.

The final price must be recorded as part of the order.

Later menu price changes must not modify completed historical orders.

Detailed customization rules are defined in:

`08_POS_and_Order_Management.md`

---

## 22. Discounts

Discounts are supported as part of order processing.

A discount affects the order price according to the applicable business rules and permissions.

Discounts must not modify the underlying global or branch product price.

For example:

```text id="r9r7fb"
Product Price
      ↓
Order
      ↓
Discount
      ↓
Final Order Amount
```

Detailed discount rules are defined in:

`14_Payments_Discounts_and_Refunds.md`

---

## 23. Menu and Inventory Relationship

Menu availability does not guarantee inventory availability.

A product may be active in the menu while the required inventory is temporarily insufficient.

However, an order requiring unavailable inventory must not create negative stock.

The inventory system must check required stock when the relevant operation is performed.

Detailed inventory rules are defined in:

`11_Inventory_and_Warehouse.md`

---

## 24. Menu and Recipe Relationship

A product intended for normal sale may have an approved recipe.

Recipe approval and menu activation are separate business steps.

A product must not use an unapproved recipe for normal operations.

The menu should use the currently approved recipe configuration.

Detailed recipe approval rules are defined in:

`12_Products_and_Recipes.md`

---

## 25. Menu and Branch Activation

A typical product activation flow is:

```text id="3f9wby"
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
Product Available for Sale
```

Not every product must pass through the same operational sequence if a recipe is not applicable.

---

## 26. Menu Changes

Menu changes may include:

* activating a product;
* deactivating a product;
* changing category;
* changing display order;
* changing product image;
* changing global price;
* changing branch price;
* changing branch availability.

Important configuration changes must be traceable.

Historical transactions must not be rewritten because the menu changed later.

---

## 27. Menu Change Permissions

The permission system must determine who can change menu configuration.

Permissions may be separated for:

* viewing the menu;
* managing products;
* managing categories;
* changing prices;
* changing branch menu availability;
* managing product images.

The system must not assume that every employee who can process orders can modify menu configuration.

---

## 28. Owner and Manager Access

The Owner may configure menu-related permissions for employees.

A Manager may manage menu functions only when the Owner has granted the relevant permission.

A Manager's authority remains limited by:

* assigned permissions;
* branch scope;
* business scope;
* subscription entitlement.

A Manager cannot use menu permissions to bypass other business security rules.

---

## 29. Offline Menu Usage

Authorized trusted devices may use the latest valid menu configuration while operating offline.

The offline device must preserve the menu state that was valid under its offline authorization.

Offline operation must not allow unauthorized menu modification.

If menu configuration changes while a device is offline, the device may temporarily continue using its valid offline configuration until synchronization or configuration refresh occurs.

The server becomes authoritative after reconnection.

---

## 30. Menu Synchronization

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

---

## 31. Business and Branch Isolation

Menu data must be isolated by business.

Branch-specific menu configuration must be isolated by branch.

Employees must only see or modify menu information within their authorized scope.

Exports, reports, offline data, background operations, and synchronization must follow the same isolation rules.

---

## 32. Subscription and Menu Access

Menu functionality is subject to the business subscription.

Employee permissions are a separate control layer.

A user may perform a menu operation only when:

1. the subscription allows the relevant functionality; and
2. the employee has the required permission.

When the subscription expires, modifying functions are blocked according to the subscription lifecycle rules.

Historical menu and product information remains viewable during the applicable read-only period.

---

## 33. Product Archive

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

## 34. Historical Price Information

The system must preserve relevant historical pricing information.

Historical information may be required to understand:

* completed orders;
* reports;
* price changes;
* branch-specific overrides;
* discounts;
* refunds.

Changing the current price must not destroy the ability to determine which price applied to a historical order.

---

## 35. Auditability

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
* reason/comment where required.

Important changes must not be silently overwritten.

---

## 36. Reporting

Menu and pricing information may be used in reports including:

* product sales;
* branch sales;
* price history;
* menu availability;
* product configuration;
* order reports.

Reports must use the applicable historical order price rather than the current product price when analyzing completed historical transactions.

---

## 37. Performance Requirements

Menu operations must remain fast enough for normal POS usage.

The system should avoid unnecessary loading of:

* inactive products;
* irrelevant branch products;
* unauthorized data;
* unnecessary image data.

Menu configuration must not introduce noticeable delays into normal order entry.

The system should remain usable on lightweight restaurant hardware.

---

## 38. Business Rules Summary

| Area                   | Rule                                        |
| ---------------------- | ------------------------------------------- |
| Global menu            | Managed at business level                   |
| Branch menu            | Branch-specific availability                |
| Product types          | Raw, semi-finished, finished                |
| Product activation     | Separate from product existence             |
| Product availability   | Separate from menu activation               |
| Equipment Broken       | Supported temporary unavailable state       |
| Product images         | Optional                                    |
| Categories             | Configurable                                |
| Display order          | Configurable                                |
| Global price           | Default business price                      |
| Branch price           | Optional authorized override                |
| Branch price scope     | Applies only to that branch                 |
| Taxes                  | Included in product price for current scope |
| Tax engine             | Not currently required                      |
| Historical price       | Must be preserved                           |
| Discounts              | Applied at order level                      |
| Recipe relationship    | Approved recipe required where applicable   |
| Inventory relationship | Stock checked during operation              |
| Offline menu           | Latest valid configuration available        |
| Permissions            | Role and scope based                        |
| Subscription           | Separate from employee permissions          |
| Product archive        | Used when historical relationships exist    |
| Audit                  | Important changes preserved                 |

---

## 39. Business Boundaries

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

## 40. Related Documents

* `01_Product_Overview.md`
* `03_Subscription_and_Tariffs.md`
* `04_Tenant_and_Branch_Management.md`
* `05_Users_Roles_and_Permissions.md`
* `07_Offline_Operation_and_Synchronization.md`
* `08_POS_and_Order_Management.md`
* `11_Inventory_and_Warehouse.md`
* `12_Products_and_Recipes.md`
* `14_Payments_Discounts_and_Refunds.md`
* `16_Reports_and_Dashboards.md`
* `17_Notifications_and_Alerts.md`
* `18_Audit_and_Change_History.md`
* `20_Business_Rules.md`

