# 19. High Availability and Failure Isolation

**Document ID:** DEP-19
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/10_Deployment/README.md`
**Previous Document:** `18_Scaling_Load_Balancing_and_Capacity_Architecture.md`
**Next Document:** To be defined

---

# 1. Purpose

Ushbu hujjat FastFood ERP uchun High Availability (HA), failure isolation, redundancy va Single Point of Failure (SPOF) architecture qoidalarini belgilaydi.

Hujjat quyidagilarni aniqlaydi:

* High Availability prinsiplari;
* failure domainlar;
* component isolation;
* redundancy;
* application availability;
* database availability;
* worker availability;
* queue availability;
* cache failure;
* synchronization failure;
* network failure;
* infrastructure failure;
* dependency failure;
* Single Point of Failure analysis;
* graceful degradation;
* failover;
* recovery;
* blast radius;
* availability priorities;
* maintenance paytidagi availability;
* HA testing.

Maqsad tizimdagi bitta component yoki infrastructure failure butun FastFood ERP'ni keraksiz ravishda ishdan chiqarmasligini ta'minlashdir.

---

# 2. Architectural Position

FastFood ERP uchun HA quyidagi prinsip asosida quriladi:

```text
Failure
   ↓
Detect
   ↓
Isolate
   ↓
Continue if Possible
   ↓
Failover if Available
   ↓
Recover
   ↓
Verify
```

Har bir failure avtomatik ravishda butun tizim failure'iga aylanishi kerak emas.

---

# 3. High Availability Definition

High Availability faqat server doim ishlashi degani emas.

FastFood ERP uchun HA quyidagilarni anglatadi:

* critical operations imkon qadar available bo‘lishi;
* component failure isolation;
* redundant components mavjudligi;
* unhealthy instance trafficdan chiqarilishi;
* data integrity saqlanishi;
* failure paytida graceful degradation;
* recovery path mavjudligi;
* operational visibility;
* maintenance vaqtida minimal disruption.

---

# 4. Availability Priority

Barcha funksiyalar bir xil darajadagi availability talab qilmaydi.

Recommended priority:

```text
Tier 1 — Critical
    Order
    Payment
    Inventory correctness
    Cash register
    Authentication

Tier 2 — Operational
    Employee operations
    Menu
    Recipes
    Branch operations
    Synchronization

Tier 3 — Important
    Notifications
    Reports
    Imports
    Exports

Tier 4 — Non-critical
    Heavy analytics
    Derived dashboards
    Optional background processing
```

Tier 1 failure'i Tier 3 yoki Tier 4 failure'dan ustun recovery priorityga ega.

---

# 5. Availability vs Data Integrity

Availability data integritydan ustun qo‘yilmaydi.

Masalan:

```text
Database unavailable
        ↓
Continue payment blindly
        ❌
```

o‘rniga:

```text
Database unavailable
        ↓
Safe Failure / Supported Offline Mode
```

ishlatiladi.

Tizim "available" bo‘lishi uchun noto‘g‘ri transaction yaratmasligi kerak.

---

# 6. Failure Domains

Failure domain — bitta failure bir vaqtning o‘zida ta'sir qilishi mumkin bo‘lgan infrastructure yoki logical boundary.

FastFood ERP uchun failure domainlar:

```text
Device
Branch
Network
Application Instance
Worker
Queue
Database
Storage
Host
Availability Zone
Region
External Dependency
```

---

# 7. Failure Domain Hierarchy

```text
Region
 └── Availability Zone
      └── Host
           ├── Application
           ├── Worker
           └── Supporting Services

Branch
 ├── Local Network
 ├── POS Device
 ├── Printer
 └── Offline Storage
```

Failure domainlar bir-biridan imkon qadar mustaqil bo‘lishi kerak.

---

# 8. Failure Isolation Principle

Bitta component failure:

```text
Component Failure
       ↓
Smallest Possible Blast Radius
```

tamoyili bilan boshqariladi.

Masalan:

```text
Report Worker Failure
        ↓
Reports delayed
        ↓
Orders continue
```

bo‘lishi kerak.

Quyidagisi noto‘g‘ri:

```text
Report Worker Failure
        ↓
Entire ERP unavailable
```

---

# 9. Blast Radius

Blast radius — failure natijasida zarar ko‘rgan componentlar ko‘lami.

Misol:

```text
One Worker
→ One Job

One Application Instance
→ Requests routed elsewhere

One Branch Network
→ Branch offline mode

One Database
→ Potential Global Impact
```

Architecture eng katta blast radiusga ega componentlarni alohida himoyalashi kerak.

---

# 10. Redundancy Model

Redundancy uch asosiy turga bo‘linadi:

```text
Active-Active
Active-Passive
Local / Offline Fallback
```

Qaysi model ishlatilishi componentning business criticality va consistency talablariga bog‘liq.

---

# 11. Active-Active

Bir nechta instance bir vaqtda traffic qabul qiladi.

```text
              Load Balancer
              /     |     \
             ↓      ↓      ↓
           App1   App2   App3
```

Advantages:

* no single application instance dependency;
* better capacity;
* failure tolerance;
* rolling deployment support.

Application layer uchun preferred model.

---

# 12. Active-Passive

Bitta primary component ishlaydi, ikkinchisi standby bo‘ladi.

```text
Primary
   ↓
Standby
```

Failure bo‘lganda standby aktivlashtiriladi.

Bu model ayniqsa stateful components uchun qo‘llanishi mumkin.

---

# 13. Offline Fallback

Branch-level operation uchun offline capability redundancy'ning maxsus ko‘rinishidir.

```text
Central System
      ↓
Network Failure
      ↓
Branch Offline Mode
      ↓
Local Operations
      ↓
Network Restored
      ↓
Synchronization
```

Offline mode faqat oldindan belgilangan supported operations doirasida ishlaydi.

---

# 14. Application Availability

Application layer imkon qadar active-active bo‘lishi kerak.

```text
Load Balancer
     │
 ┌───┼────┐
 ↓   ↓    ↓
A1  A2   A3
```

Bitta application instance failure butun service failureiga olib kelmasligi kerak.

---

# 15. Application Instance Failure

Agar instance ishlamay qolsa:

1. health check failure aniqlaydi;
2. instance trafficdan chiqariladi;
3. boshqa healthy instance'lar trafficni qabul qiladi;
4. failed instance restart yoki replacement qilinadi;
5. recovery verified qilinadi.

Bu jarayon `DEP-16` deployment va `DEP-18` scaling qoidalariga mos bo‘ladi.

---

# 16. Load Balancer Failure

Load balancer o‘zi SPOF bo‘lishi mumkin.

Architecture:

```text
             Entry Layer
             /        \
            LB1       LB2
             \        /
              App Pool
```

Production HA talablariga qarab redundant entry layer ishlatilishi kerak.

Agar provider-managed HA load balancer ishlatilsa, provider redundancy modeli hujjatlashtiriladi.

---

# 17. Application Session Failure

Application instance failure user sessionni avtomatik ravishda yo‘q qilmasligi kerak.

Preferred architecture:

```text
Client
  ↓
Any Healthy Instance
  ↓
Shared / Stateless Session
```

Local-only session dependency HA'ni kamaytiradi.

---

# 18. Worker Availability

Background workerlar applicationdan mustaqil failure domain sifatida ko‘riladi.

```text
Queue
 ├── Worker 1
 ├── Worker 2
 └── Worker 3
```

Bitta worker failure:

```text
Worker 1 failed
      ↓
Worker 2/3 continue
```

bo‘lishi kerak.

---

# 19. Queue Availability

Queue critical background operations uchun muhim component hisoblanadi.

Queue failure:

* job acceptance;
* notifications;
* reports;
* synchronization;
* imports

ga ta'sir qilishi mumkin.

Queue critical bo‘lsa, uning persistence va recovery modeli aniq belgilanadi.

---

# 20. Queue Failure Isolation

Queue ishlamay qolsa:

```text
Queue Failure
     ↓
Background Processing Delayed
     ↓
Critical Synchronous Operations Continue
```

imkon qadar ta'minlanadi.

Queue failure transactional data'ni yo‘qotmasligi kerak.

---

# 21. Database as Critical Failure Domain

PostgreSQL FastFood ERP uchun eng muhim shared state component hisoblanadi.

Database failure blast radius katta:

```text
PostgreSQL Failure
        ↓
Many Application Functions Affected
```

Shuning uchun database availability boshqa componentlardan kuchliroq himoyalanadi.

---

# 22. Database Redundancy

Production architecture database redundancy'ni infrastructure imkoniyatiga qarab qo‘llashi mumkin.

Potential model:

```text
Primary
   │
   └── Standby
```

yoki provider-managed HA database.

Database failoverda:

* transaction integrity;
* connection recovery;
* application reconnect;
* replication state;
* data correctness

tekshiriladi.

---

# 23. Database Failover

Database failure aniqlanganda:

```text
Primary Failure
      ↓
Confirm Failure
      ↓
Promote Standby if Safe
      ↓
Reconnect Applications
      ↓
Verify Database
      ↓
Resume Traffic
```

Failover faqat data consistency va replication state xavfsiz bo‘lsa bajariladi.

---

# 24. Split-Brain Protection

Database HA architecture split-brain holatidan himoyalanishi kerak.

Bir vaqtning o‘zida ikki node authoritative primary sifatida ishlamasligi kerak.

```text
Primary A ─┐
           ├── ❌ Two Primaries
Primary B ─┘
```

Split-brain inventory, payment va order consistency uchun xavfli.

---

# 25. Database Replication Lag

Standby mavjud bo‘lsa, replication lag kuzatiladi.

```text
Primary
   ↓
Replication
   ↓
Standby
```

Lag katta bo‘lsa, failover xavfi oshadi.

Failover readiness replication health bilan bog‘lanadi.

---

# 26. Database Storage Failure

Database storage failure alohida failure domain sifatida ko‘riladi.

Protection:

* redundant storage;
* backup;
* WAL/recovery;
* standby;
* monitoring.

Storage failure primary database'ni ishdan chiqarsa recovery procedure `DEP-17` bilan boshqariladi.

---

# 27. Database Connection Failure

Application database connection yo‘qotsa:

```text
Connection Lost
     ↓
Controlled Reconnect
     ↓
Retry if Safe
```

Retry duplicate transaction yaratmasligi kerak.

Payment va inventory operations uchun idempotency talab qilinadi.

---

# 28. Database Failure and User Experience

Database unavailable bo‘lganda application:

* endless loading;
* silent failure;
* duplicate submission

qilmasligi kerak.

Userga aniq operation status ko‘rsatiladi.

---

# 29. Cache Failure

Cache critical source of truth bo‘lmasligi kerak.

```text
Cache Failure
     ↓
Fallback / Reduced Performance
```

Agar cache temporary unavailable bo‘lsa, application imkon qadar authoritative storage orqali ishlaydi.

---

# 30. Cache as Non-Critical Dependency

Cache failure:

```text
Performance degradation
```

bo‘lishi mumkin, lekin:

```text
Data corruption
```

ga olib kelmasligi kerak.

---

# 31. Storage Failure

Application storage failure:

* temporary files;
* generated reports;
* uploaded images;
* logs

ga ta'sir qilishi mumkin.

Business-critical transaction data primary database'dan alohida storage modelga bog‘lanmasligi kerak.

---

# 32. File Storage Redundancy

Agar user-uploaded yoki generated files business-critical bo‘lsa:

* durable storage;
* backup;
* replication;
* integrity checking

ko‘rib chiqiladi.

Temporary files esa qayta yaratish mumkin bo‘lgan kategoriya sifatida boshqariladi.

---

# 33. Network Failure

Network failure ikki asosiy darajada ko‘riladi:

```text
Central Network Failure
Branch Network Failure
```

---

# 34. Central Network Failure

Central infrastructure network failure:

```text
Users
   X
Central ERP
```

holatiga olib kelishi mumkin.

Agar network path redundant bo‘lsa, failover ishlatiladi.

Agar bo‘lmasa, recovery `DEP-17` orqali boshqariladi.

---

# 35. Branch Network Failure

Branch internet connection yo‘qotsa:

```text
Internet Lost
     ↓
Branch Offline Mode
     ↓
Local Operations
     ↓
Sync Later
```

Bu FastFood ERP uchun muhim availability requirement hisoblanadi.

---

# 36. Branch Failure Domain

Branch alohida failure domain sifatida qaraladi.

Bitta branchdagi:

* printer;
* POS device;
* local network;
* internet;
* local sync state

failure boshqa branchlarni to‘xtatmasligi kerak.

---

# 37. Branch Isolation

```text
Central ERP
 ├── Branch A
 ├── Branch B
 ├── Branch C
 └── Branch D
```

Branch A failure:

```text
Branch A ❌
Branch B ✓
Branch C ✓
Branch D ✓
```

bo‘lishi kerak.

---

# 38. Branch Local Availability

Branch internetdan uzilganda supported local functionality davom etishi mumkin.

Bunda:

* local transaction state;
* local sequence;
* local operational state;
* pending synchronization

ishonchli saqlanishi kerak.

---

# 39. Synchronization Failure

Synchronization failure:

```text
Branch
  ↓
Sync
  X
Central
```

holatida branch data yo‘qolmasligi kerak.

Pending sync records persistent bo‘lishi kerak.

---

# 40. Synchronization Retry

Sync failure:

```text
Attempt
  ↓
Failure
  ↓
Backoff
  ↓
Retry
  ↓
Success
```

modelida ishlaydi.

Infinite uncontrolled retry bo‘lmasligi kerak.

---

# 41. Synchronization Conflict

Offline branch va central system bir xil business objectni o‘zgartirgan bo‘lsa, conflict resolution qoidalari ishlaydi.

Conflict:

* silent overwrite;
* silent delete

orqali hal qilinmasligi kerak.

Critical conflict audit qilinadi.

---

# 42. Printer Failure

Printer failure operational component failure hisoblanadi.

```text
Printer Failure
      ↓
Printing unavailable
      ↓
Order System Continues if Supported
```

Printer failure database yoki payment failureiga aylanmasligi kerak.

Printer retry duplicate receipt chiqarmasligi kerak.

---

# 43. Device Failure

Cashier/POS device failure:

```text
Device A ❌
     ↓
Device B / Supported Recovery
```

modeli bilan boshqariladi.

Device identity va authorization qoidalari security architecture bilan mos bo‘lishi kerak.

---

# 44. Authentication Dependency Failure

Authentication service failure butun ERP uchun katta blast radiusga ega bo‘lishi mumkin.

Architecture:

* token validation;
* session validation;
* authorization

uchun dependency availabilityni hisobga oladi.

Security checkni bypass qilish HA yechimi hisoblanmaydi.

---

# 45. External Dependency Failure

External dependency ishlamasa application:

```text
External Service
       ↓
Failure
       ↓
Timeout
       ↓
Fallback / Queue / Safe Error
```

modelidan foydalanadi.

External service response kelmagani uchun request cheksiz kutmasligi kerak.

---

# 46. Timeout Isolation

External dependency uchun timeout bo‘lmasa:

```text
One Dependency
      ↓
Requests Block
      ↓
Workers Exhausted
      ↓
Entire Application Degrades
```

bo‘lishi mumkin.

Shuning uchun timeout failure isolationning asosiy vositalaridan biridir.

---

# 47. Circuit Breaker

Critical external dependency uchun circuit breaker ko‘rib chiqilishi mumkin.

Model:

```text
Closed
  ↓
Failure Threshold
  ↓
Open
  ↓
Cooldown
  ↓
Half-Open
  ↓
Recovered → Closed
```

Bu dependency failure'ni application bo‘ylab tarqalishidan himoya qiladi.

---

# 48. Dependency Bulkhead

Turli workloadlar alohida resource poolga ega bo‘lishi mumkin.

Masalan:

```text
Critical API Pool
Report Pool
Sync Pool
External Integration Pool
```

Report traffic critical order trafficini egallab olmasligi kerak.

---

# 49. Component Isolation

Componentlar imkon qadar quyidagi boundarylar bilan ajratiladi:

```text
Request Processing
Background Jobs
Synchronization
Reporting
Notifications
External Integrations
```

Bir componentning resource exhaustion'i boshqalar availability'ini buzmasligi kerak.

---

# 50. Reporting Isolation

Report subsystem:

```text
Heavy Report
     ↓
Reporting Resources
```

orqali boshqariladi.

Report query database'ni haddan tashqari band qilsa, operational transactionlar ta'sirlanmasligi kerak.

---

# 51. Notification Failure

Notification service failure:

```text
Notification Failure
      ↓
Notification Delayed
```

bo‘lishi mumkin.

Lekin:

```text
Order / Payment / Inventory Failure
```

ga aylantirilmasligi kerak.

Critical notificationlar uchun persistent queue ishlatilishi mumkin.

---

# 52. Email/SMS Failure

Email/SMS provider unavailable bo‘lsa:

* request timeout;
* retry;
* queue;
* failure record

ishlatiladi.

Transactionni external notification muvaffaqiyatiga bog‘lash tavsiya etilmaydi.

---

# 53. Single Point of Failure

SPOF — bitta component failure'i butun critical service failureiga olib keladigan architecture component.

FastFood ERP uchun SPOF analysis majburiy.

---

# 54. SPOF Analysis Matrix

| Component              | Failure Impact              |   SPOF Risk | Preferred Protection   |
| ---------------------- | --------------------------- | ----------: | ---------------------- |
| Application instance   | Service degradation         |         Low | Multiple instances     |
| Load balancer          | Global access loss          |        High | HA entry layer         |
| PostgreSQL primary     | Large global impact         |        High | DB HA/backup           |
| DB storage             | DB failure                  |        High | Redundant storage      |
| Worker                 | Background delay            |         Low | Multiple workers       |
| Queue                  | Background processing issue | Medium/High | Durable queue          |
| Cache                  | Performance degradation     |         Low | Fallback               |
| Branch internet        | Branch connectivity loss    |    Expected | Offline mode           |
| Printer                | Printing unavailable        |         Low | Operational fallback   |
| External API           | Feature degradation         |      Medium | Timeout/retry/fallback |
| Single host            | Multiple services loss      |        High | Multi-host deployment  |
| Single backup location | Recovery risk               |        High | Independent backup     |

---

# 55. Critical SPOFs

Quyidagilar productionda alohida tekshirilishi kerak:

1. database;
2. database storage;
3. load balancer/entry layer;
4. primary host;
5. network path;
6. authentication dependency;
7. backup storage.

---

# 56. Non-Critical SPOFs

Quyidagi componentlar SPOF bo‘lsa ham global availability uchun kritik bo‘lmasligi mumkin:

* individual worker;
* cache;
* report worker;
* notification worker;
* individual printer;
* individual branch device.

Ularning failure blast radius'i kichik bo‘lishi kerak.

---

# 57. SPOF Elimination Priority

SPOFlarni bartaraf etish priority:

```text
Critical Transaction Path
        ↓
Database
        ↓
Entry / Network
        ↓
Application
        ↓
Background Processing
        ↓
Optional Services
```

Eng katta business impactga ega SPOF birinchi bartaraf etiladi.

---

# 58. Redundancy Does Not Mean Duplicate Everything

Har bir componentni ikki yoki uch nusxaga ko‘paytirish majburiy emas.

Redundancy:

* business impact;
* failure probability;
* recovery time;
* cost;
* consistency requirement

asosida belgilanadi.

---

# 59. Cost-Aware HA

FastFood ERP boshlang‘ich deploymentida barcha HA komponentlarini maksimal darajada ko‘paytirish shart emas.

Masalan:

```text
Low Load
→ Simple Infrastructure

Growing Load
→ Application Redundancy

Critical Scale
→ Database HA

Large Enterprise Scale
→ More Advanced Failure Domains
```

HA bosqichma-bosqich rivojlantiriladi.

---

# 60. Availability Target

Availability target biznes criticality asosida belgilanadi.

Target faqat:

```text
99.99%
```

kabi raqam bilan emas, balki:

* allowed downtime;
* recovery time;
* critical operation availability;
* maintenance window

bilan baholanadi.

---

# 61. RTO

Recovery Time Objective — failure'dan keyin service qanchalik tez tiklanishi kerakligini bildiradi.

Masalan:

```text
Failure
 ↓
Recovery
 ↓
Service Restored
```

RTO har bir component uchun bir xil bo‘lishi shart emas.

---

# 62. RPO

Recovery Point Objective — recovery paytida qancha data yo‘qotish mumkinligini bildiradi.

FastFood ERP critical transactional data uchun RPO imkon qadar minimal bo‘lishi kerak.

Payment, inventory va cash data uchun data lossga juda qat'iy talab qo‘yiladi.

---

# 63. RTO/RPO Priority

| Area                | RTO Priority | RPO Priority |
| ------------------- | ------------ | ------------ |
| Payment             | Very High    | Very High    |
| Orders              | Very High    | Very High    |
| Inventory           | Very High    | Very High    |
| Cash Register       | Very High    | Very High    |
| Employee operations | High         | High         |
| Reports             | Medium       | Medium       |
| Notifications       | Medium       | Lower        |
| Derived analytics   | Lower        | Lower        |

Aniq targetlar disaster recovery architecture va production infrastructure bilan belgilanadi.

---

# 64. Graceful Degradation

Failure paytida system capability quyidagi darajalarga tushishi mumkin:

```text
Full Service
     ↓
Reduced Service
     ↓
Critical Operations Only
     ↓
Offline / Local Mode
     ↓
Unavailable
```

Maqsad darhol oxirgi holatga tushmaslik.

---

# 65. Critical Operation Protection

Capacity yoki dependency failure paytida:

```text
Order
Payment
Inventory
Cash Register
```

kabi critical operations boshqa non-critical workloadlardan himoyalanadi.

---

# 66. Failure Isolation by Priority

Agar report subsystem resource tugatsa:

```text
Reports ❌
Orders ✓
Payments ✓
Inventory ✓
```

Agar notification service ishlamasa:

```text
Notifications delayed
Operations continue
```

Agar cache ishlamasa:

```text
Performance reduced
Data remains authoritative
```

---

# 67. Failure Detection

Failure detection:

* health checks;
* metrics;
* logs;
* connection failures;
* queue state;
* database state;
* synthetic checks

orqali amalga oshiriladi.

Detection kechikishi recovery time'ni oshiradi.

---

# 68. Detection vs Recovery

Failure detection va recovery alohida tushunchalar:

```text
Failure
 ↓
Detect
 ↓
Classify
 ↓
Isolate
 ↓
Recover
 ↓
Verify
```

Faqat restart qilish recovery strategy hisoblanmaydi.

---

# 69. Automatic Recovery

Safe bo‘lgan failurelar uchun automatic recovery ishlatilishi mumkin:

* restart failed application instance;
* replace unhealthy worker;
* retry safe background job;
* remove unhealthy instance from load balancer.

Critical database failover kabi operationlar kuchli safety controls bilan boshqariladi.

---

# 70. Manual Recovery

Manual intervention talab qilishi mumkin bo‘lgan holatlar:

* data corruption;
* split-brain risk;
* failed migration;
* inconsistent synchronization;
* failed database recovery;
* security incident;
* ambiguous deployment state.

Bunday holatlarda uncontrolled automation xavfli.

---

# 71. Failure During Deployment

Deployment paytida failure:

```text
Old Version
   +
New Version
   +
Infrastructure Change
```

kombinatsiyasida yuz berishi mumkin.

`DEP-16` va `DEP-17`:

* compatibility;
* rollback;
* recovery;
* graceful traffic management

qoidalari bilan boshqaradi.

---

# 72. Failure During Scaling

Scaling operation failure:

```text
Scale Out
   ↓
New Node Failed
```

bo‘lsa, existing healthy nodes ishlashda davom etadi.

Failed node trafficga qo‘shilmaydi.

---

# 73. Failure During Migration

Migration failure:

```text
Migration Failure
      ↓
Stop / Recovery Decision
```

orqali boshqariladi.

HA migration xavfini yo‘q qilmaydi.

`DEP-15` migration safety qoidalari ustun hisoblanadi.

---

# 74. Failure During Database Failover

Database failover paytida application:

* connection errors;
* retry;
* transaction uncertainty

holatlariga tayyor bo‘lishi kerak.

Agar transaction commit statusi noma'lum bo‘lsa, blind retry qilinmasligi kerak.

---

# 75. Transaction Uncertainty

Masalan:

```text
Payment Request
     ↓
Database Commit
     ↓
Network Failure
     ↓
Client sees Error
```

Bu holatda payment muvaffaqiyatli yoki muvaffaqiyatsiz ekanini faqat client erroriga qarab aniqlab bo‘lmaydi.

Transaction status authoritative system orqali tekshiriladi.

---

# 76. Duplicate Prevention

HA va retry architecture duplicate business effects yaratmasligi kerak.

Critical operations uchun:

* idempotency key;
* transaction constraint;
* unique business identifier;
* state validation

ishlatilishi mumkin.

---

# 77. Failover and Idempotency

Failover:

```text
Request
 ↓
Primary
 ↓
Uncertain Result
 ↓
Failover
 ↓
Retry
```

holatiga olib kelishi mumkin.

Idempotency bo‘lmasa duplicate order/payment/inventory mutation xavfi mavjud.

---

# 78. Security During Failover

Failover security controlsni bypass qilmasligi kerak.

Failover paytida:

* authentication;
* authorization;
* tenant isolation;
* branch isolation;
* audit;
* device verification

saqlanishi kerak.

---

# 79. Tenant Isolation During Failure

Bir tenant failure boshqa tenant data'siga ta'sir qilmasligi kerak.

Failure handling:

```text
Tenant A Problem
       ↓
Tenant A degraded
       ↓
Tenant B continues
```

modelini imkon qadar saqlaydi.

---

# 80. Branch Isolation During Failure

Branch-level errors central applicationni global ravishda to‘xtatmasligi kerak.

```text
Branch A Sync Failure
        ↓
Branch A Pending
        ↓
Other Branches Continue
```

---

# 81. Recovery Verification

Failover yoki recovery tugagach:

* database health;
* application health;
* queue health;
* synchronization;
* transaction processing;
* inventory consistency;
* payment status;
* audit logs

tekshiriladi.

---

# 82. HA Testing

HA architecture productiondan oldin test qilinishi kerak.

Minimum tests:

1. application instance failure;
2. worker failure;
3. cache failure;
4. queue failure;
5. network interruption;
6. branch offline mode;
7. database failover;
8. storage failure;
9. dependency timeout;
10. deployment failure.

---

# 83. Failure Injection

Controlled failure injection orqali architecture tekshirilishi mumkin.

Misollar:

```text
Kill App Instance
Stop Worker
Block Network
Stop Queue
Simulate DB Failure
Delay External API
```

Testlar productiondan tashqari xavfsiz environmentda bajariladi.

---

# 84. Failover Test

Failover test quyidagilarni o‘lchaydi:

* detection time;
* failover time;
* reconnect time;
* data integrity;
* request recovery;
* user-visible impact;
* error rate.

---

# 85. Failure Drill

Periodic failure drill:

```text
Prepare
 ↓
Inject Failure
 ↓
Observe
 ↓
Recover
 ↓
Verify
 ↓
Document Findings
```

natijalari architecture va runbooklarni yangilash uchun ishlatiladi.

---

# 86. Recovery Documentation

Har bir major failure scenario uchun runbook bo‘lishi kerak.

Runbook:

* symptom;
* detection;
* immediate action;
* isolation;
* recovery;
* verification;
* escalation;
* rollback;
* post-incident review

qismlarini o‘z ichiga oladi.

---

# 87. Availability Monitoring

Monitoring quyidagilarni kuzatadi:

* service availability;
* application instance health;
* database health;
* queue health;
* sync health;
* external dependency health;
* branch connectivity.

---

# 88. Synthetic Monitoring

Critical user flowlar uchun synthetic check ishlatilishi mumkin:

```text
Login
 ↓
Open Application
 ↓
Read Operational Data
```

Critical transactional flowlar esa test environment va production monitoring siyosatiga qarab alohida nazorat qilinadi.

---

# 89. Availability Metrics

Asosiy metrics:

* uptime;
* downtime;
* incident frequency;
* MTTR;
* MTBF;
* failover success rate;
* health-check failures;
* recovery success rate.

---

# 90. MTTR

Mean Time To Recovery tizim failure'dan keyin recovery tezligini ko‘rsatadi.

HA architecture MTTRni kamaytirishga xizmat qiladi.

---

# 91. MTBF

Mean Time Between Failures infrastructure reliability trendini ko‘rsatadi.

MTBF oshishi:

* better hardware;
* better software;
* better deployment;
* better monitoring

natijasi bo‘lishi mumkin.

---

# 92. Maintenance Availability

Maintenance paytida:

* rolling deployment;
* graceful shutdown;
* redundant instance;
* failover

orqali service disruption kamaytiriladi.

`DEP-16` release strategy bilan mos bo‘lishi kerak.

---

# 93. Planned vs Unplanned Failure

### Planned

* deployment;
* migration;
* maintenance;
* infrastructure upgrade.

### Unplanned

* crash;
* hardware failure;
* network outage;
* database failure;
* external dependency outage.

Ikkalasi ham architecture tomonidan qo‘llab-quvvatlanadi.

---

# 94. Availability Budget

Agar availability target belgilanadigan bo‘lsa, downtime budget:

```text
Allowed Downtime
=
Availability Target
+
Measurement Period
```

asosida hisoblanadi.

Budget tugashiga yaqin reliability improvements priorityga chiqariladi.

---

# 95. HA Anti-Patterns

Quyidagilar tavsiya etilmaydi:

1. Bitta application instancega bog‘lanish.
2. Bitta load balancer node'ga bog‘lanish.
3. Bitta database storagega backup qilmasdan tayanish.
4. Cache'ni source of truth qilish.
5. Reportlarni critical transaction bilan bir xil resource poolga cheklovsiz qo‘shish.
6. External API'ni transaction completionga majburiy bog‘lash.
7. Infinite retry.
8. Blind retry.
9. Split-brain protection'siz database failover.
10. Health check'siz traffic routing.
11. Local application memoryda authoritative state saqlash.
12. Branch network failure'ini global outagega aylantirish.

---

# 96. HA Design Rules

FastFood ERP uchun quyidagi rules majburiy:

1. Critical application layer imkon qadar redundant bo‘ladi.
2. Application instance failure trafficni to‘liq to‘xtatmasligi kerak.
3. Database failure uchun documented recovery path bo‘ladi.
4. Critical data uchun backup va recovery mavjud bo‘ladi.
5. Branch network failure branch isolation bilan boshqariladi.
6. Offline mode data integrityni buzmasligi kerak.
7. Worker failure transactional operationsni to‘xtatmasligi kerak.
8. Cache authoritative source emas.
9. External dependency failure timeout va isolation bilan boshqariladi.
10. Critical operations non-critical workloadsdan himoyalanadi.
11. Failover security controlsni bypass qilmaydi.
12. HA duplicate transactions yaratmasligi kerak.
13. Failure blast radius imkon qadar kichik saqlanadi.
14. Major failure scenarios test qilinadi.
15. Recovery verification majburiy.

---

# 97. Failure Isolation Model

FastFood ERP uchun umumiy failure isolation:

```text
                         ┌───────────────┐
                         │ Central Entry │
                         └───────┬───────┘
                                 │
                         ┌───────┴───────┐
                         │ Load Balancer │
                         └───────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    ↓            ↓            ↓
                  App 1        App 2        App 3
                    │            │            │
                    └────────────┼────────────┘
                                 ↓
                          PostgreSQL HA
                                 │
                    ┌────────────┴────────────┐
                    ↓                         ↓
                 Queue                    Storage
                    │
             ┌──────┼──────┐
             ↓      ↓      ↓
          Worker  Worker  Worker

        Branch A       Branch B       Branch C
        Offline        Online         Online
```

Har bir layer o‘z failure boundary'siga ega bo‘lishi kerak.

---

# 98. Failure State Model

Componentlar quyidagi state'larda bo‘lishi mumkin:

```text
Healthy
   ↓
Degraded
   ↓
Unhealthy
   ↓
Isolated
   ↓
Recovering
   ↓
Verified
   ↓
Healthy
```

Agar recovery muvaffaqiyatsiz bo‘lsa:

```text
Recovering
   ↓
Failed
   ↓
Manual Recovery
```

---

# 99. Global Failure State

Butun system uchun:

```text
Healthy
Degraded
Partial Outage
Major Outage
Recovery
```

state'lari ishlatilishi mumkin.

Partial outage misoli:

```text
Reports unavailable
Orders available
```

Major outage:

```text
Core transaction system unavailable
```

---

# 100. Incident Escalation

Failure severityga qarab escalation:

```text
Component Issue
      ↓
Service Degradation
      ↓
Critical Service Impact
      ↓
Global Incident
```

Critical incidentlarda operations, infrastructure va development mas'ullari jalb qilinadi.

---

# 101. Post-Failure Review

Major failuredan keyin:

* root cause;
* contributing factors;
* detection;
* isolation;
* recovery;
* data integrity;
* downtime;
* user impact;
* SPOF findings

ko‘rib chiqiladi.

Agar architecture'da yangi weakness aniqlansa, tegishli ADR yoki architecture document yangilanadi.

---

# 102. Relationship With DEP-18

`18_Scaling_Load_Balancing_and_Capacity_Architecture.md` scalingni belgilaydi.

Ushbu hujjat esa scalingdan keyingi availability architecture'ni belgilaydi.

Asosiy farq:

```text
DEP-18
Capacity
Performance
Scaling
Load Distribution

DEP-19
Availability
Failure
Redundancy
Isolation
Failover
```

Ular birgalikda ishlaydi.

---

# 103. Relationship With DEP-15

`DEP-15` database migration va release deploymentni boshqaradi.

Migration:

* HA architecture;
* database failover;
* replication;
* capacity;
* lock behavior

bilan mos bo‘lishi kerak.

HA migration safety qoidalarini bekor qilmaydi.

---

# 104. Relationship With DEP-16

`DEP-16` release strategy va zero-downtime deploymentni belgilaydi.

HA architecture:

* rolling deployment;
* health checks;
* graceful shutdown;
* load balancing;
* mixed-version operation

uchun foundation beradi.

---

# 105. Relationship With DEP-17

`DEP-17` rollback va release recoveryni belgilaydi.

HA:

* failed instance isolation;
* service continuity;
* failover;
* recovery capacity

ni ta'minlashga yordam beradi.

Rollback yoki recovery paytida data integrity `DEP-17` qoidalari bilan boshqariladi.

---

# 106. Relationship With Disaster Recovery

High Availability va Disaster Recovery bir xil tushuncha emas.

### High Availability

Component failure vaqtida service continuity.

### Disaster Recovery

Katta infrastructure yoki data loss holatidan keyin systemni tiklash.

```text
HA
↓
Component Failure
↓
Fast Failover

DR
↓
Major Disaster
↓
Restore / Rebuild
```

HA DR o‘rnini bosmaydi.

---

# 107. HA vs Backup

Backup:

```text
Recovery Capability
```

beradi.

HA:

```text
Service Continuity
```

beradi.

Backup mavjudligi database failure'ni avtomatik ravishda HA qilmaydi.

---

# 108. HA vs Scaling

Scaling:

```text
More Capacity
```

beradi.

HA:

```text
More Failure Tolerance
```

beradi.

Ular bir-birini to‘ldiradi, lekin bir xil muammoni hal qilmaydi.

---

# 109. Final Architecture Principle

FastFood ERP uchun High Availability prinsipi:

> **Bitta component failure butun tizim failureiga aylanmasligi kerak; critical data esa availability uchun qurbon qilinmasligi kerak.**

Architecture:

```text
Redundancy
    ↓
Isolation
    ↓
Detection
    ↓
Failover
    ↓
Graceful Degradation
    ↓
Recovery
    ↓
Verification
```

ketma-ketligida ishlaydi.

HA'ning asosiy maqsadi barcha failure'larni yo‘q qilish emas. Asosiy maqsad — failure muqarrar bo‘lgan holatda uning **blast radiusini cheklash, critical operationsni himoya qilish, data integrityni saqlash va tizimni boshqariladigan tarzda tiklash**dir.

