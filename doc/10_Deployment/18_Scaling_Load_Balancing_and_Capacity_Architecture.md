# 18. Scaling, Load Balancing and Capacity Architecture

**Document ID:** DEP-18
**Status:** Accepted
**Version:** 1.0
**Scope:** FastFood ERP
**Parent Document:** `docs/10_Deployment/README.md`
**Previous Document:** `17_Rollback_and_Release_Recovery.md`
**Next Document:** To be defined

---

## 1. Purpose

Ushbu hujjat FastFood ERP uchun:

* horizontal scaling;
* vertical scaling;
* load balancing;
* application instance scaling;
* database scaling;
* worker scaling;
* offline synchronization scaling;
* cache scaling;
* capacity planning;
* infrastructure limits;
* scaling triggers;
* performance thresholds;
* resource protection;
* tenant/branch growth;
* deployment paytidagi scaling;
* scaling vaqtida availability va data integrity

qoidalarini belgilaydi.

Maqsad tizimni faqat hozirgi yuklama uchun emas, balki restaurant network, branch, employee, order, inventory, synchronization va reportlar soni oshganda ham boshqariladigan tarzda kengaytirishdir.

---

# 2. Architectural Position

FastFood ERP dastlab kichik yoki o‘rta infratuzilmada ishlashi mumkin.

Tizimning boshlang‘ich arxitekturasi ortiqcha murakkab distributed infrastructure talab qilmasligi kerak.

Scaling zarur bo‘lganda tizim quyidagi tartibda kengaytiriladi:

```text
Single Instance
      ↓
Vertical Scaling
      ↓
Application Replicas
      ↓
Load Balancer
      ↓
Dedicated Workers
      ↓
Database Optimization
      ↓
Read Scaling / Cache
      ↓
Further Infrastructure Separation
```

Har bir bosqich faqat real ehtiyoj va o‘lchangan bottleneck asosida joriy qilinadi.

Oldindan keraksiz distributed architecture yaratish majburiy emas.

---

# 3. Scaling Principles

FastFood ERP scaling quyidagi prinsiplar asosida ishlaydi.

## 3.1. Measure Before Scale

Resurs yetishmasligi taxmin bilan emas, monitoring ma'lumotlari bilan aniqlanadi.

Quyidagilar kuzatiladi:

* CPU;
* RAM;
* disk;
* disk I/O;
* database connections;
* database latency;
* request latency;
* request rate;
* error rate;
* worker utilization;
* queue depth;
* synchronization backlog;
* network throughput.

---

## 3.2. Scale the Bottleneck

Butun tizimni bir xil vaqtda kattalashtirish shart emas.

Masalan:

```text
High CPU
→ Application scaling

High DB CPU
→ Database optimization/scaling

High queue depth
→ Worker scaling

High sync backlog
→ Synchronization worker scaling

High disk I/O
→ Storage optimization/scaling
```

---

## 3.3. Correctness Before Capacity

Scaling hech qachon:

* transaction consistency;
* inventory correctness;
* payment correctness;
* cash register integrity;
* synchronization integrity;
* audit integrity

hisobiga amalga oshirilmasligi kerak.

Ko‘proq instance qo‘shish noto‘g‘ri concurrency modelini tuzatmaydi.

---

## 3.4. Stateless Application Preference

Application layer imkon qadar stateless bo‘lishi kerak.

Application instance lokal xotirasida quyidagilar authoritative state sifatida saqlanmasligi kerak:

* order state;
* inventory state;
* cash register state;
* employee permission state;
* subscription state;
* synchronization state;
* audit state.

Bular persistent authoritative storage orqali boshqariladi.

---

# 4. Scaling Dimensions

FastFood ERP bir nechta mustaqil o‘qda scale qilinadi.

```text
                    ┌─ Application
                    │
                    ├─ Workers
                    │
                    ├─ Database
                    │
                    ├─ Cache
                    │
                    ├─ Storage
                    │
                    └─ Synchronization
```

Har bir layer alohida bottleneck bo‘lishi mumkin.

---

# 5. Vertical Scaling

Vertical scaling mavjud server resurslarini oshirishdir.

Masalan:

```text
2 CPU / 4 GB RAM
        ↓
4 CPU / 8 GB RAM
        ↓
8 CPU / 16 GB RAM
```

## 5.1. CPU Scaling

CPU quyidagi holatlarda oshirilishi mumkin:

* application CPU doimiy yuqori;
* worker CPU yuqori;
* database CPU yuqori;
* request latency CPU bilan korrelyatsiya qilsa.

CPU utilization faqat qisqa spike asosida scale qilish uchun yetarli signal emas.

---

## 5.2. Memory Scaling

RAM quyidagi holatlarda oshiriladi:

* sustained memory pressure;
* swap usage;
* application memory growth;
* database cache pressure;
* worker memory exhaustion;
* OOM termination.

Application memory leak mavjud bo‘lsa, faqat RAM oshirish yakuniy yechim hisoblanmaydi.

---

## 5.3. Storage Scaling

Disk hajmi quyidagilar uchun hisoblanadi:

* database;
* transaction data;
* audit logs;
* application logs;
* backup;
* temporary files;
* synchronization metadata.

Disk usage kritik chegaraga yetishidan oldin capacity action boshlanishi kerak.

---

## 5.4. Vertical Scaling Advantages

* sodda;
* boshqarish oson;
* deployment arxitekturasi o‘zgarmaydi;
* debugging oson;
* kichik deploymentlar uchun mos.

---

## 5.5. Vertical Scaling Limits

Bitta serverga cheksiz tayanish mumkin emas.

Muammolar:

* hardware limit;
* single point of failure;
* maintenance downtime;
* network dependency;
* resource contention;
* failure blast radius.

Shuning uchun vertical scaling uzoq muddatli yagona scaling strategy emas.

---

# 6. Horizontal Scaling

Horizontal scaling bir nechta application instance ishlatishdir.

```text
                    Load Balancer
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
      App Node 1     App Node 2     App Node 3
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                     PostgreSQL
```

Horizontal scaling application layer uchun asosiy scale-out strategy hisoblanadi.

---

# 7. Application Instance Requirements

Horizontal scaling ishlashi uchun application instance'lar:

* bir xil release versiyasiga ega;
* mos schema bilan ishlaydigan;
* bir xil configuration policyga ega;
* authoritative state'ni shared storage orqali o‘qiydigan;
* local state'ga minimal bog‘liq;
* idempotent request handlingga ega

bo‘lishi kerak.

`DEP-15` va `DEP-16` da belgilangan compatibility qoidalari saqlanadi.

---

# 8. Load Balancer

Bir nechta application instance mavjud bo‘lganda load balancer ishlatiladi.

```text
Client
  ↓
Load Balancer
  ├── App 1
  ├── App 2
  └── App 3
```

Load balancer vazifalari:

* request distribution;
* health checking;
* unhealthy instance'ni trafficdan chiqarish;
* connection management;
* TLS termination;
* deployment paytida traffic boshqarish.

---

# 9. Load Balancing Strategy

Default strategy sifatida oddiy va predictabledistribution ishlatiladi.

Masalan:

```text
Round Robin
```

Agar request workload instance'lar orasida teng bo‘lmasa, keyinchalik:

* least connections;
* weighted distribution;
* latency-aware routing

kabi strategiyalar ko‘rib chiqilishi mumkin.

Strategiya real workload asosida tanlanadi.

---

# 10. Health Checks

Load balancer application instance'ni faqat process ishlayotganiga qarab healthy deb hisoblamasligi kerak.

Health model kamida quyidagilarni ajratishi kerak:

```text
Liveness
Readiness
Dependency Health
```

## 10.1. Liveness

Application process ishlayaptimi?

## 10.2. Readiness

Application request qabul qilishga tayyormi?

Masalan:

* required configuration mavjud;
* database connection ishlaydi;
* required dependencies mavjud.

## 10.3. Dependency Health

Dependency vaqtincha ishlamayotgan bo‘lsa, application o‘z holatini to‘g‘ri bildirishi kerak.

---

# 11. Unhealthy Instance Handling

Agar instance health check'dan yiqilsa:

```text
Healthy
   ↓
Unhealthy
   ↓
Remove from traffic
   ↓
Investigate / Restart / Replace
```

Load balancer unhealthy instance'ga yangi request yubormasligi kerak.

Existing connections esa graceful termination qoidalari asosida tugatiladi.

---

# 12. Graceful Shutdown

Application instance o‘chirilishidan oldin:

1. yangi request qabul qilish to‘xtatiladi;
2. existing requests tugatiladi;
3. active worker tasklar xavfsiz holatga keltiriladi;
4. connectionlar yopiladi;
5. instance shutdown qilinadi.

Graceful shutdown `DEP-16` release strategy bilan mos bo‘lishi kerak.

---

# 13. Session Management

Horizontal scaling uchun user session faqat bitta application instance RAM'iga bog‘lanmasligi kerak.

Preferred:

```text
Client
  ↓
Load Balancer
  ↓
Any App Instance
  ↓
Shared Session / Stateless Auth
```

Agar session state server-side bo‘lsa, shared session storage ishlatiladi.

---

# 14. Sticky Sessions

Sticky sessions default architecture sifatida tavsiya etilmaydi.

Sabablar:

* instance failure paytida session uzilishi;
* uneven load;
* scaling murakkablashishi;
* deployment murakkablashishi.

Sticky session faqat aniq texnik sabab bo‘lsa ishlatiladi.

---

# 15. Database Scaling

PostgreSQL tizimning authoritative transactional database'i bo‘lib qoladi.

Database scaling application scalingdan alohida ko‘riladi.

```text
Application
     ↓
PostgreSQL
```

Database bottleneck bo‘lsa, avval:

1. query optimization;
2. indexing;
3. connection management;
4. transaction optimization;
5. unnecessary queries reduction;
6. caching;
7. storage/I/O improvement

ko‘rib chiqiladi.

Keyin infrastructure scaling amalga oshiriladi.

---

# 16. Database Vertical Scaling

PostgreSQL uchun birinchi scaling yo‘li ko‘pincha vertical scaling bo‘ladi.

Resurslar:

* CPU;
* RAM;
* fast storage;
* IOPS;
* network.

Database scalingda RAM ayniqsa query va cache workloadiga sezilarli ta'sir qilishi mumkin.

---

# 17. Database Connection Capacity

Application instance'lar soni oshganda database connectionlar ham oshishi mumkin.

Masalan:

```text
1 instance × 20 connections = 20
5 instances × 20 connections = 100
10 instances × 20 connections = 200
```

Shuning uchun application replica sonini oshirishdan oldin database connection capacity tekshiriladi.

Connection pool limitlari nazoratsiz oshirilmasligi kerak.

---

# 18. Connection Pooling

Application database connection pool ishlatishi mumkin.

Pool quyidagilarni cheklaydi:

* maximum connections;
* idle connections;
* connection timeout;
* acquisition timeout;
* lifetime.

Maqsad database'ni application instance sonidan kelib chiqadigan connection storm'dan himoya qilishdir.

---

# 19. Read Scaling

Read-heavy workload oshganda read scaling ko‘rib chiqilishi mumkin.

Masalan:

```text
                 PostgreSQL Primary
                  /             \
                 /               \
          Write Traffic       Read Replica
                                ↑
                           Reporting Reads
```

Read replica faqat consistency talablari bunga imkon berganda ishlatiladi.

---

# 20. Strong Consistency Operations

Quyidagi operatsiyalar authoritative primary database orqali bajarilishi kerak:

* order creation;
* payment;
* inventory deduction;
* cash register operations;
* refund;
* stock adjustment;
* recipe approval;
* employee permission change;
* subscription state change;
* synchronization commit.

Read replica stale data qaytarishi mumkinligi sababli bu operatsiyalar uchun source of truth bo‘la olmaydi.

---

# 21. Reporting Scaling

Reports database workloadining katta qismini tashkil qilishi mumkin.

Og‘ir reportlar transactional requestlarga xalaqit bermasligi kerak.

Possible strategies:

```text
Transactional DB
       │
       ├── Operational Queries
       │
       └── Reporting Read Path
```

Keyinchalik:

* read replica;
* reporting database;
* precomputed aggregates;
* background report generation

qo‘llanishi mumkin.

---

# 22. Worker Scaling

Background jobs application request cycle'dan ajratiladi.

Masalan:

* notifications;
* report generation;
* synchronization;
* import processing;
* export processing;
* scheduled tasks;
* non-critical calculations.

Workerlar queue orqali scale qilinishi mumkin.

```text
Application
    ↓
Queue
    ↓
Worker 1
Worker 2
Worker 3
```

---

# 23. Queue-Based Scaling

Worker scalingning asosiy signalidan biri queue depth hisoblanadi.

Masalan:

```text
Queue depth ↑
     ↓
Processing latency ↑
     ↓
Worker capacity insufficient
     ↓
Add workers
```

Worker sonini oshirishdan oldin job concurrency xavfsizligi tekshiriladi.

---

# 24. Idempotent Jobs

Horizontal worker scaling uchun joblar imkon qadar idempotent bo‘lishi kerak.

Bir job:

```text
Worker A → attempts job
Worker B → retries same job
```

holatida duplicate business effect yaratmasligi kerak.

Ayniqsa:

* inventory;
* payments;
* synchronization;
* notifications;
* financial operations

uchun duplicate processingga qarshi protection talab qilinadi.

---

# 25. Synchronization Scaling

Offline branch synchronization alohida workload hisoblanadi.

```text
Offline Branch
      ↓
Sync Queue
      ↓
Sync Workers
      ↓
Central Database
```

Sync backlog oshganda:

* sync worker count;
* batch size;
* retry strategy;
* network capacity;
* conflict processing capacity

tekshiriladi.

---

# 26. Offline Branch Load

Branch offline ishlaganda keyinchalik katta sync burst paydo bo‘lishi mumkin.

Masalan:

```text
Branch Offline
     ↓
Many local transactions
     ↓
Connection Restored
     ↓
Sync Burst
```

Central system bunday burstni qabul qilishga tayyor bo‘lishi kerak.

Synchronization requestlari controlled batching va backpressure bilan ishlashi kerak.

---

# 27. Backpressure

Tizim o‘z imkoniyatidan yuqori yuklamani qabul qilmasligi kerak.

Agar queue yoki synchronization capacity to‘lsa:

```text
Accept Everything
      ❌
```

o‘rniga:

```text
Controlled Queueing
       ↓
Retry
       ↓
Backoff
       ↓
Capacity Recovery
```

ishlatiladi.

Backpressure data lossga olib kelmasligi kerak.

---

# 28. Cache Scaling

Cache performance yaxshilash uchun ishlatilishi mumkin.

Cache authoritative source emas.

Cache'da saqlanishi mumkin:

* frequently accessed configuration;
* read-heavy metadata;
* non-critical derived data;
* temporary session state.

Cache'da authoritative inventory yoki payment state saqlanmasligi kerak.

---

# 29. Cache Failure

Cache ishlamasa application:

```text
Cache unavailable
      ↓
Fallback to authoritative source
```

imkoniga ega bo‘lishi kerak, agar workload bunga imkon bersa.

Cache failure butun ERP'ni majburiy ravishda to‘xtatmasligi kerak.

---

# 30. Storage Scaling

Storage quyidagi kategoriyalarga bo‘linadi:

```text
Database Storage
Application Storage
Logs
Backups
Temporary Storage
```

Ularning capacity va retention policy alohida boshqariladi.

---

# 31. Log Growth

Loglar cheksiz o‘smasligi kerak.

Log lifecycle:

```text
Generate
  ↓
Collect
  ↓
Retain
  ↓
Rotate
  ↓
Archive/Delete
```

Production diskni loglar to‘ldirib yubormasligi kerak.

---

# 32. Capacity Planning

Capacity planning quyidagi asosiy birliklar bo‘yicha amalga oshiriladi:

* restaurant networks;
* branches;
* employees;
* concurrent users;
* orders/day;
* orders/minute;
* inventory transactions;
* synchronization events;
* reports;
* background jobs;
* database size;
* storage growth.

---

# 33. Primary Capacity Model

Capacity planning uchun quyidagi formula modeli ishlatiladi:

```text
Total Load =
  Active Users
  × Requests/User
  × Request Cost
```

Transactional workload uchun:

```text
Order Load =
  Orders/Day
  × Peak Concentration
  × Operations/Order
```

Database capacity esa:

```text
DB Load =
  Reads
  + Writes
  + Transactions
  + Background Queries
  + Reports
```

---

# 34. Peak Load

Average traffic asosida capacity rejalashtirish yetarli emas.

FastFood ERP uchun peak workload alohida hisoblanadi.

Peak davrlar:

* lunch;
* dinner;
* weekends;
* holidays;
* promotions;
* branch opening;
* salary/reporting periods.

---

# 35. Peak-to-Average Ratio

Capacity planningda peak-to-average ratio kuzatiladi.

```text
Peak Load
──────────────
Average Load
```

Ratio yuqori bo‘lsa:

* autoscaling;
* queueing;
* capacity buffer

ko‘proq talab qilinishi mumkin.

---

# 36. Capacity Headroom

Production system doim 100% resource utilization bilan ishlamasligi kerak.

Capacity headroom quyidagilar uchun kerak:

* traffic spike;
* deployment;
* background jobs;
* synchronization burst;
* failure recovery;
* monitoring overhead.

Target utilization environment va workloadga qarab belgilanadi.

---

# 37. Scaling Triggers

Scaling triggerlari ikki kategoriyaga bo‘linadi:

```text
Resource Trigger
Workload Trigger
```

---

# 38. Resource Triggers

Resource triggerlarga:

* sustained CPU pressure;
* sustained memory pressure;
* disk pressure;
* I/O pressure;
* database CPU pressure;
* connection saturation;
* network saturation

kiradi.

Qisqa spike avtomatik scaling uchun yagona signal bo‘lmasligi kerak.

---

# 39. Workload Triggers

Workload triggerlarga:

* request rate;
* concurrent users;
* queue depth;
* sync backlog;
* orders/minute;
* report generation backlog;
* API latency;
* database query latency

kiradi.

---

# 40. Latency-Based Trigger

Resource utilization normal bo‘lsa ham latency oshishi mumkin.

Shuning uchun:

```text
Low CPU + High Latency
```

holati alohida tekshiriladi.

Sabab:

* database locks;
* slow query;
* network latency;
* external service;
* connection pool exhaustion;
* queue delay

bo‘lishi mumkin.

---

# 41. Error-Based Trigger

Error rate oshishi scaling trigger bo‘lishi mumkin, lekin errorning sababini aniqlash kerak.

Masalan:

```text
500 errors ↑
```

avtomatik ravishda:

```text
Add servers
```

degani emas.

Bu:

* bug;
* database failure;
* dependency failure;
* configuration error;
* capacity issue

bo‘lishi mumkin.

---

# 42. Recommended Trigger Classification

| Signal                    | Possible Action                 |
| ------------------------- | ------------------------------- |
| CPU sustained high        | App/worker scaling              |
| RAM sustained high        | Memory optimization/scaling     |
| DB CPU high               | Query optimization / DB scaling |
| DB connections near limit | Pool tuning / DB capacity       |
| Queue depth high          | Worker scaling                  |
| Sync backlog high         | Sync scaling                    |
| Disk near limit           | Storage cleanup/scaling         |
| Latency high              | Bottleneck investigation        |
| Error rate high           | Incident investigation          |
| Network saturated         | Network capacity scaling        |

---

# 43. Scaling Thresholds

Exact thresholdlar deployment environmentga qarab belgilanadi.

Default operational guidance:

```text
Normal:
< 60% sustained resource utilization

Warning:
60–75%

High:
75–85%

Critical:
> 85% sustained
```

Bu qiymatlar qat'iy biznes qoidasi emas.

Real production benchmark natijalariga ko‘ra tuning qilinadi.

---

# 44. Database Thresholds

Database uchun quyidagilar alohida kuzatiladi:

* CPU;
* memory;
* active connections;
* connection wait;
* lock wait;
* transaction duration;
* slow queries;
* disk I/O;
* replication lag;
* storage utilization.

Database bottleneck aniqlanmasdan application replica sonini oshirish mumkin emas.

---

# 45. Auto Scaling

Auto scaling keyingi infrastructure bosqichida ishlatilishi mumkin.

Basic model:

```text
Load increases
      ↓
Metric threshold reached
      ↓
Add instance
      ↓
Health check
      ↓
Add to load balancer
```

Scale-down:

```text
Load decreases
      ↓
Sustained low utilization
      ↓
Graceful drain
      ↓
Remove instance
```

Scale-down active transactionsga zarar bermasligi kerak.

---

# 46. Scale-Out Cooldown

Auto scaling thrashingga yo‘l qo‘ymasligi kerak.

Masalan:

```text
Add instance
↓
Wait / observe
↓
Evaluate again
```

Bir necha daqiqalik qisqa fluctuation uchun:

```text
Add
Remove
Add
Remove
```

sikli yuzaga kelmasligi kerak.

---

# 47. Minimum and Maximum Instances

Production application uchun:

```text
min_instances
max_instances
```

chegaralari bo‘lishi kerak.

Maximum instance limit:

* database capacity;
* budget;
* downstream dependencies;
* queue capacity

bilan mos bo‘lishi kerak.

---

# 48. Scaling Does Not Bypass Limits

Masalan:

```text
10 App Instances
```

database maksimal:

```text
100 Connections
```

bo‘lsa, har instance uchun 20 connection berish noto‘g‘ri.

Scaling boshqa layer limitlarini hisobga olishi kerak.

---

# 49. Dependency Capacity

Application scalingda faqat application server hisoblanmaydi.

Dependency capacity:

```text
App
 ↓
DB
 ↓
Cache
 ↓
Queue
 ↓
External APIs
 ↓
Printers / Devices
```

ham hisobga olinadi.

---

# 50. External Service Limits

External API yoki service:

* rate limit;
* connection limit;
* request quota;
* timeout;
* retry policy

berishi mumkin.

Application scale-out external service'ga kutilmagan traffic burst yubormasligi kerak.

---

# 51. Printer Scaling

Printerlar application server scalingdan alohida ko‘riladi.

Branchdagi printer:

* local;
* network;
* USB/port based

bo‘lishi mumkin.

Printer requestlari application replica soniga bog‘liq bo‘lmasligi kerak.

Printing architecture duplicate printdan himoyalangan bo‘lishi kerak.

---

# 52. Branch-Level Capacity

Har bir branchning operational load'i alohida bo‘lishi mumkin.

Masalan:

```text
Branch A → 100 orders/day
Branch B → 2,000 orders/day
```

Shuning uchun tenant/branch workload isolation muhim.

Bir branchdagi workload boshqa branchlarning availability'ini buzmasligi kerak.

---

# 53. Tenant/Restaurant Isolation

Bitta restaurant networkning workloadi boshqa restaurant networklarga zarar yetkazmasligi kerak.

Resource control keyinchalik:

* query limits;
* job limits;
* report limits;
* synchronization limits;
* API rate limits

orqali kuchaytirilishi mumkin.

---

# 54. Large Tenant Protection

Juda katta tenant yoki branch tizimning umumiy capacity'sini egallab olmasligi kerak.

Potential controls:

```text
Per-tenant concurrency
Per-tenant queue capacity
Per-tenant report limits
Per-tenant sync rate
```

Limitlar biznes ehtiyojiga qarab konfiguratsiya qilinadi.

---

# 55. Subscription-Based Capacity

Subscription tariff funksional limitlarni belgilashi mumkin.

Masalan:

* branch count;
* employee count;
* enabled features.

Scaling architecture bu biznes limitlaridan alohida hisoblanadi.

Subscription yuqori bo‘lgani avtomatik ravishda unlimited infrastructure access degani emas.

---

# 56. Large Report Protection

Og‘ir reportlar:

* timeout;
* pagination;
* asynchronous generation;
* background queue;
* date range limits

bilan himoyalanishi mumkin.

Bitta report butun database capacity'sini egallamasligi kerak.

---

# 57. Import/Export Scaling

Excel import/export katta workload yaratishi mumkin.

Large import:

```text
Upload
 ↓
Validate
 ↓
Queue
 ↓
Process in batches
 ↓
Report result
```

Request lifecycle ichida millionlab recordsni synchronous processing qilish tavsiya etilmaydi.

---

# 58. Batch Processing

Large batch operationlarda:

* bounded batch size;
* transaction boundaries;
* progress tracking;
* retry;
* failure isolation

ishlatiladi.

Bitta katta transaction database locklarini uzoq ushlab turmasligi kerak.

---

# 59. Database Partitioning

Database juda katta bo‘lganda partitioning ko‘rib chiqilishi mumkin.

Potential candidates:

* large event tables;
* audit records;
* historical operational records;
* synchronization records.

Partitioning faqat real data volume va query pattern asosida joriy qilinadi.

---

# 60. Archival

Data growthni boshqarish uchun archival policy kerak bo‘lishi mumkin.

Masalan:

```text
Active Data
    ↓
Historical Data
    ↓
Archive
```

Archive qilish financial yoki audit talablariga zid bo‘lmasligi kerak.

---

# 61. Data Retention and Subscription Expiry

Subscription tugashi bilan data darhol o‘chirilmaydi.

Accepted business rule:

```text
Subscription Expired
        ↓
Functions Blocked
        ↓
Data Remains Viewable
        ↓
Reactivation Period
        ↓
If Not Reactivated
        ↓
Data Deletion Policy
```

Scaling architecture bu retention period davomida saqlanadigan data hajmini capacity planningga kiritishi kerak.

---

# 62. Backup Capacity

Scaling paytida backup size ham oshadi.

Capacity planning:

```text
Primary Data
+ Backup Storage
+ WAL / Recovery Data
+ Logs
```

ni hisobga oladi.

Backup infrastructure production storage bilan raqobatlashmasligi kerak.

---

# 63. Recovery Capacity

Scaling faqat normal operation uchun emas, recovery uchun ham rejalashtiriladi.

Masalan:

```text
Normal Load = 100
Recovery Load = 200
```

bo‘lishi mumkin.

Recovery paytida:

* backup restore;
* sync replay;
* queue processing;
* database recovery

qo‘shimcha resurs talab qiladi.

`DEP-17` recovery requirements bilan mos bo‘lishi kerak.

---

# 64. Deployment Capacity

Deployment vaqtida vaqtinchalik resource increase bo‘lishi mumkin.

Masalan:

```text
Old App
+
New App
+
Migration
```

bir vaqtning o‘zida ishlashi mumkin.

Shuning uchun deployment capacity normal capacity'dan alohida hisoblanadi.

---

# 65. Migration Capacity

`DEP-15` talablariga ko‘ra migration production database'ga qo‘shimcha load berishi mumkin.

Migrationdan oldin:

* CPU;
* memory;
* disk;
* I/O;
* lock;
* active transactions;
* replication;
* capacity headroom

tekshiriladi.

Migration production workloadni xavfli darajada bosib ketmasligi kerak.

---

# 66. Load Testing

Major capacity changes oldidan load testing bajarilishi mumkin.

Testlar:

* normal load;
* peak load;
* burst load;
* sustained load;
* synchronization burst;
* reporting load;
* concurrent cashier activity.

---

# 67. Performance Baseline

Productiondan oldin baseline yaratiladi.

Baseline quyidagilarni o‘z ichiga oladi:

```text
Requests/sec
p50 latency
p95 latency
p99 latency
Error rate
DB CPU
DB connections
Queue depth
Memory
CPU
```

Scaling decision baseline bilan taqqoslanadi.

---

# 68. Percentile Latency

Average latency yagona performance metric bo‘lmasligi kerak.

Kamida:

* p50;
* p95;
* p99

kuzatiladi.

Masalan:

```text
Average = 100 ms
p99 = 5 sec
```

bo‘lsa, tizim foydalanuvchilarning bir qismi uchun sekin ishlayotgan bo‘lishi mumkin.

---

# 69. Capacity Test Scenarios

Capacity test quyidagi scenario'larni qamrab olishi kerak:

### Scenario A — Normal

Oddiy branch workload.

### Scenario B — Peak

Lunch/dinner workload.

### Scenario C — Burst

Qisqa vaqt ichida ko‘p order.

### Scenario D — Multi-Branch

Bir nechta branch bir vaqtda faol.

### Scenario E — Offline Sync Burst

Bir nechta branch bir vaqtda sync qiladi.

### Scenario F — Reporting

Katta date range reportlar.

---

# 70. Failure During Scaling

Scaling vaqtida instance failure bo‘lishi mumkin.

Masalan:

```text
Scale Out
   ↓
New Instance
   ↓
Health Check Failed
```

Bunday instance trafficga qo‘shilmasligi kerak.

Existing healthy instances ishlashda davom etadi.

---

# 71. Scaling During Deployment

Scaling va deployment bir vaqtda sodir bo‘lishi mumkin.

`DEP-16` qoidalari bo‘yicha:

* version compatibility;
* health checks;
* graceful shutdown;
* schema compatibility

saqlanadi.

---

# 72. Scaling and Rollback

Agar release rollback qilinsa:

```text
Current Capacity
+
Old Version
```

kombinatsiyasi qo‘llab-quvvatlanishi kerak.

Rollback paytida instance sonini kamaytirish yoki oshirish release recovery'ni yomonlashtirmasligi kerak.

`DEP-17` recovery procedure bilan birgalikda ishlaydi.

---

# 73. Scaling State

Infrastructure controller quyidagi state'larni kuzatishi mumkin:

```text
Stable
Scaling Up
Stabilizing
Scaling Down
Degraded
Blocked
Recovery
```

Scaling state deployment/recovery state bilan conflict qilmasligi kerak.

---

# 74. Scaling Freeze

Quyidagi holatlarda avtomatik scale-down vaqtincha bloklanishi mumkin:

* active incident;
* database migration;
* recovery;
* rollback;
* severe synchronization backlog;
* infrastructure instability.

Scale-up esa incident mitigation uchun ruxsat etilishi mumkin.

---

# 75. Rate Limiting

Public/API endpoints uchun rate limiting capacity protection vositasi hisoblanadi.

Rate limit:

* authentication;
* import;
* reports;
* synchronization;
* API calls

uchun alohida bo‘lishi mumkin.

Rate limiting valid business trafficni asossiz bloklamasligi kerak.

---

# 76. Concurrency Limits

Har bir operation uchun concurrency limit bo‘lishi mumkin.

Masalan:

```text
Report generation = limited
Import jobs = limited
Sync jobs = controlled
```

Bu database va worker capacity'ni himoya qiladi.

---

# 77. Resource Priority

Capacity pressure paytida critical business operations yuqori priorityga ega.

Recommended priority:

```text
1. Authentication / Authorization
2. Order / Payment
3. Inventory correctness
4. Cash Register
5. Synchronization
6. Operational workflows
7. Reports
8. Non-critical background work
```

Priority implementation infrastructure va application layerga qarab farq qilishi mumkin.

---

# 78. Graceful Degradation

Capacity pressure paytida tizim barcha funksiyani birdan to‘xtatmasligi kerak.

Masalan:

```text
Critical Operations
        ↓
Remain Available

Heavy Reports
        ↓
Delayed / Queued
```

Bu model branch operational continuity'ni himoya qiladi.

---

# 79. No Silent Data Loss

Capacity exhaustion:

* order;
* payment;
* inventory;
* cash;
* synchronization

data lossiga olib kelmasligi kerak.

Agar request qabul qilinmasa, tizim aniq failure state qaytarishi kerak.

---

# 80. Timeout Policy

Har bir request yoki job cheksiz kutmasligi kerak.

Timeoutlar:

* HTTP request;
* DB connection;
* DB query;
* queue job;
* external API;
* synchronization

uchun alohida belgilanadi.

Timeout retry bilan birga duplicate operation yaratmasligi kerak.

---

# 81. Retry Policy

Retry faqat retry-safe operationlarda ishlatiladi.

Retry policy:

```text
Immediate retry
↓
Backoff
↓
Maximum attempts
↓
Dead-letter / failure state
```

Payment yoki inventory kabi operationlarda idempotency protection talab qilinadi.

---

# 82. Observability

Scaling architecture quyidagi observability qatlamlariga ega bo‘lishi kerak:

```text
Metrics
Logs
Traces
Alerts
Audit
```

---

# 83. Infrastructure Metrics

Minimum metrics:

* CPU;
* RAM;
* disk;
* I/O;
* network;
* instance count;
* health status.

---

# 84. Application Metrics

Minimum metrics:

* request rate;
* response latency;
* error rate;
* active requests;
* queue wait;
* worker utilization.

---

# 85. Business Metrics

Technical metrics bilan birga business workload ham kuzatiladi:

* orders/minute;
* orders/day;
* payments/minute;
* inventory transactions;
* active branches;
* active users;
* synchronization events.

Business metrics capacity planning uchun muhim signal hisoblanadi.

---

# 86. Database Metrics

Minimum:

* active connections;
* transaction rate;
* query latency;
* slow queries;
* lock waits;
* CPU;
* memory;
* I/O;
* storage;
* replication lag.

---

# 87. Alerting

Critical thresholdlar uchun alertlar bo‘lishi kerak.

Masalan:

```text
CPU Critical
DB Connection Saturation
Disk Critical
Queue Backlog
Sync Backlog
High Error Rate
High Latency
Replication Lag
```

Alertlar actionable bo‘lishi kerak.

---

# 88. Capacity Dashboard

Operations uchun capacity dashboard quyidagilarni ko‘rsatishi kerak:

```text
Current Load
Capacity
Headroom
Trend
Scaling State
Critical Dependencies
```

---

# 89. Capacity Forecasting

Capacity planning faqat current state emas, growth trendni ham hisobga oladi.

Masalan:

```text
Current:
100 branches

Forecast:
150 branches
```

Data growth, order growth va user growth alohida prognoz qilinadi.

---

# 90. Growth Model

Planning uchun kamida:

```text
Branches/month
Orders/branch/day
Users/branch
Storage/order
Transactions/order
```

kabi ko‘rsatkichlar yig‘iladi.

Keyinchalik forecast modeli real production data bilan yangilanadi.

---

# 91. Capacity Review

Capacity review:

* major release;
* major customer onboarding;
* branch growth;
* infrastructure change;
* sustained utilization increase

oldidan bajarilishi mumkin.

---

# 92. Scaling Decision Matrix

| Condition             | Default Action               |
| --------------------- | ---------------------------- |
| CPU high, DB normal   | Scale application            |
| DB CPU high           | Optimize/scale DB            |
| DB connections high   | Tune pool / DB               |
| Queue high            | Scale workers                |
| Sync backlog high     | Scale sync workers           |
| Disk high             | Storage action               |
| Report load high      | Separate/report optimization |
| Cache pressure        | Cache optimization           |
| Network high          | Network capacity             |
| High latency, low CPU | Investigate bottleneck       |
| High errors           | Incident investigation       |

---

# 93. Scaling Limits

Har bir deployment uchun explicit limits bo‘lishi kerak.

Limits:

* maximum application instances;
* maximum workers;
* maximum DB connections;
* maximum queue depth;
* maximum batch size;
* maximum report range;
* maximum import size;
* maximum synchronization concurrency.

Limits configuration orqali boshqarilishi mumkin.

---

# 94. Limit Enforcement

Limitga yetilganda:

```text
Accept Unlimited
      ❌
```

o‘rniga:

```text
Reject Safely
Queue
Throttle
Defer
```

mexanizmlaridan mos biri ishlatiladi.

Critical business data yo‘qotilmasligi kerak.

---

# 95. Multi-Region Scaling

Multi-region architecture dastlab majburiy emas.

U quyidagi ehtiyojlar paydo bo‘lganda ko‘rib chiqilishi mumkin:

* geographic expansion;
* regional latency;
* regulatory requirements;
* disaster recovery;
* very large user base.

Multi-region joriy etilganda data consistency va synchronization alohida architecture talab qiladi.

---

# 96. Multi-Region Warning

Multi-region oddiy horizontal scaling emas.

Quyidagilar murakkablashadi:

* database consistency;
* transactions;
* synchronization;
* failover;
* conflict resolution;
* latency;
* deployment;
* recovery.

Shuning uchun faqat real business requirement bo‘lsa joriy qilinadi.

---

# 97. Single Region Default

Default architecture:

```text
Users
  ↓
Load Balancer
  ↓
Application Instances
  ↓
Workers / Queue
  ↓
PostgreSQL
```

bitta primary region ichida ishlashi mumkin.

High availability talablariga qarab keyinchalik redundant components qo‘shiladi.

---

# 98. Cost Control

Scaling faqat technical performance emas, cost bilan ham boshqariladi.

Har bir scaling action uchun:

```text
Performance Benefit
vs
Infrastructure Cost
```

baholanadi.

Overprovisioning ham architecture muammosi hisoblanadi.

---

# 99. Scaling Safety Rules

Quyidagi qoidalar majburiy:

1. Scaling bottleneck o‘lchov bilan tasdiqlanadi.
2. Application scale-out database capacityni hisobga oladi.
3. Database connectionlar limitlanadi.
4. Critical transactional operations authoritative database orqali bajariladi.
5. Cache source of truth emas.
6. Workerlar idempotent processingni qo‘llab-quvvatlaydi.
7. Offline synchronization controlled load bilan ishlaydi.
8. Large reports transactional workloadni bloklamasligi kerak.
9. Scale-down graceful bo‘lishi kerak.
10. Scaling data integrityni buzmasligi kerak.
11. Capacity headroom saqlanadi.
12. Maximum limits belgilanadi.
13. Auto scaling thrashingdan himoyalanadi.
14. Recovery uchun qo‘shimcha capacity hisobga olinadi.
15. Migration va deployment capacity planningga kiritiladi.

---

# 100. Scaling Sequence

Default application scaling:

```text
Measure
  ↓
Identify Bottleneck
  ↓
Optimize
  ↓
Vertical Scale if Appropriate
  ↓
Add Application Replicas
  ↓
Introduce Load Balancer
  ↓
Scale Workers
  ↓
Optimize / Scale Database
  ↓
Add Read Scaling / Cache if Required
  ↓
Review Capacity Again
```

---

# 101. Operational Scaling Sequence

Capacity pressure aniqlanganda:

```text
1. Detect
2. Confirm
3. Identify Bottleneck
4. Protect Critical Workloads
5. Scale or Optimize
6. Health Check
7. Observe
8. Validate Business Operations
9. Update Capacity Baseline
10. Record Decision
```

---

# 102. Scaling Completion Criteria

Scaling operation tugallangan deb hisoblanadi, agar:

* target capacityga erishilgan;
* application healthy;
* database healthy;
* queue stable;
* synchronization backlog normal;
* latency acceptable;
* error rate normal;
* critical business operations ishlayotgan;
* monitoring active;
* no unexpected data integrity issue mavjud bo‘lmasa.

---

# 103. Audit and Change Record

Significant scaling changes yozib boriladi.

Record:

* date/time;
* reason;
* detected bottleneck;
* previous capacity;
* new capacity;
* metrics;
* operator;
* deployment/release;
* result;
* follow-up action.

Bu ma'lumot keyingi capacity planning uchun ishlatiladi.

---

# 104. Relationship With Other Deployment Documents

## DEP-15 — Database Migration and Release Deployment

Scaling paytida database migration:

* capacity;
* lock;
* I/O;
* connection;
* compatibility

talablariga amal qiladi.

---

## DEP-16 — Release Strategy and Zero-Downtime Deployment

Horizontal scaling:

* rolling deployment;
* health checks;
* graceful shutdown;
* mixed-version compatibility

bilan mos ishlaydi.

---

## DEP-17 — Rollback and Release Recovery

Scaling:

* rollback;
* recovery;
* incident response

jarayonlarini murakkablashtirmasligi kerak.

Recovery paytida capacity yetarli bo‘lishi kerak.

---

# 105. Related Architecture Areas

Ushbu hujjat quyidagi architecture areas bilan bog‘liq:

* application architecture;
* database architecture;
* API architecture;
* background jobs;
* synchronization;
* caching;
* observability;
* security;
* disaster recovery;
* performance testing;
* infrastructure operations.

---

# 106. Final Architecture Principle

FastFood ERP scaling strategiyasining asosiy prinsipi:

> **Avval bottleneckni o‘lcha, keyin optimallashtir, undan keyin kerakli layerni scale qil.**

Tizimni shunchaki ko‘proq server qo‘shish orqali emas, balki:

```text
Correctness
    ↓
Observability
    ↓
Optimization
    ↓
Capacity Planning
    ↓
Controlled Scaling
    ↓
Resilience
```

ketma-ketligida rivojlantirish kerak.

Scaling application availabilityni oshirishi mumkin, lekin u noto‘g‘ri data model, noto‘g‘ri transaction, inefficient query yoki noto‘g‘ri synchronization dizaynini avtomatik tuzatmaydi.

Shuning uchun FastFood ERP uchun scaling — alohida infrastructure feature emas, balki application, database, deployment, synchronization, recovery va operations architecture bilan birgalikda boshqariladigan tizim qobiliyatidir.

