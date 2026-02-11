# Embrix O2X Platform - Complete Database Architecture Guide

**Version**: 3.1.9-SNAPSHOT  
**Last Updated**: February 2026  
**Purpose**: Comprehensive guide to database structure, patterns, and operations

---

## Table of Contents

1. [High-Level ERD Overview](#high-level-erd-overview)
2. [Database Technology Overview](#database-technology-overview)
3. [Multi-Tenant Data Architecture](#multi-tenant-data-architecture)
4. [Schema Organization](#schema-organization)
5. [Complete Entity Reference](#complete-entity-reference)
6. [Relationships & Foreign Keys](#relationships--foreign-keys)
7. [Indexes & Performance](#indexes--performance)
8. [Partitioning Strategy](#partitioning-strategy)
9. [Database Migrations](#database-migrations)
10. [Data Access Patterns](#data-access-patterns)
11. [Backup & Recovery](#backup--recovery)

---

## High-Level ERD Overview

Before diving into schemas and individual tables, it helps to have a **mental model of the ERD**.  
The diagram below shows the main entities and how they connect (same content as the standalone ERD page).

<p style="margin: 16px 0;">
  <img src="ERD.png"
       alt="Embrix O2X Database ERD – High-Level Overview"
       style="display:block;max-width:100%;height:auto;border-radius:8px;border:1px solid #e5e7eb;box-shadow:0 8px 24px rgba(15,23,42,0.35);" />
</p>

At a high level, the ERD is organized around five core domains:

- **Customer & Identity**
  - `ACCOUNT` is the root entity. Almost everything ultimately hangs off an account.
  - `ADDRESS` and `USER` are children of `ACCOUNT` (billing/service addresses, login users).
  - An account:
    - *places* `ORDER`s
    - *owns* `SUBSCRIPTION`s
    - *is billed by* `INVOICE`s
    - *pays with* `PAYMENT`s
    - *generates* `USAGE_RECORD`s
    - *has* `BALANCE_IMPACT`s that track AR changes

- **Product, Pricing & Bundles**
  - `PRODUCT` defines what we sell (plans, add‑ons, bundles, usage products).
  - `PRICE_OFFER` defines how a product is priced (amount, frequency, status).
  - `BUNDLE` groups multiple products together; `DISCOUNT` attaches commercial discounts.
  - Relationships:
    - A `PRODUCT` is **priced by** many `PRICE_OFFER`s.
    - A `PRODUCT` can appear in many `SERVICE_LINE`s and `SUBSCRIPTION`s.
    - A `BUNDLE` **contains** multiple `PRODUCT`s; `DISCOUNT` **applies to** one or more `PRICE_OFFER`s.

- **Orders & Subscriptions**
  - `"ORDER"` represents a commercial order coming from CRM or self‑care.
  - `SERVICE_LINE` rows are the individual actions/items inside that order.
  - `SUBSCRIPTION` is the long‑lived contractual relationship that results from orders.
  - Supporting entities:
    - `ORCHESTRATION_STATE` tracks the current provisioning/billing workflow step.
    - `ORDER_ACTIVITY` logs status changes and audit history.
  - Key relationships:
    - An `ACCOUNT` **places** many `"ORDER"`s.
    - An `"ORDER"` **contains** many `SERVICE_LINE`s and is **tracked by** one `ORCHESTRATION_STATE`.
    - A `SUBSCRIPTION` belongs to an `ACCOUNT`, references a `PRODUCT`, and uses a specific `PRICE_OFFER`.

- **Billing, Invoicing & Accounts Receivable**
  - `CHARGE` is the atomic billing item produced by rating and billing runs.
  - `INVOICE` aggregates many `CHARGE`s into a customer‑facing bill.
  - `PAYMENT` records money received; `PAYMENT_ALLOCATION` ties payments to invoices/charges.
  - `BALANCE_IMPACT` keeps the running AR position in sync.
  - Relationships:
    - A `SUBSCRIPTION` **generates** many `CHARGE`s.
    - An `INVOICE` **aggregates** many `CHARGE`s.
    - A `PAYMENT` **allocates** to one or more invoices via `PAYMENT_ALLOCATION`.
    - Both `PAYMENT` and `CHARGE` create `BALANCE_IMPACT` rows that roll up to the `ACCOUNT`.

- **Usage, Mediation & Revenue Recognition**
  - `USAGE_RECORD` stores individual rated/ unrated events (CDRs).
  - `USAGE_ACCUMULATOR` and `USAGE_QUOTA` track buckets (e.g., data bundles, fair‑use limits).
  - `CDR_FILE` and `CDR_ERROR` model ingestion files and failed records.
  - `DEFERRED_REVENUE` and `JOURNAL_ENTRY` model revenue that is recognized over time.
  - Relationships:
    - A `SUBSCRIPTION` **consumes** many `USAGE_RECORD`s and is **tracked by** `USAGE_ACCUMULATOR`/`USAGE_QUOTA`.
    - A `CDR_FILE` **produces** many `USAGE_RECORD`s and may have `CDR_ERROR` rows.
    - A `CHARGE` may **defer** into `DEFERRED_REVENUE`, which is then **recognized by** multiple `JOURNAL_ENTRY` rows.

When reading the rest of this document, you can think in terms of these domains:

- Start from `ACCOUNT`.
- Follow orders → subscriptions → charges → invoices/payments.
- Connect usage (`USAGE_RECORD`) and revenue (`DEFERRED_REVENUE` / `JOURNAL_ENTRY`) back to those core entities.

---

## Database Technology Overview

### PostgreSQL Configuration

| Property | Value | Purpose |
|----------|-------|---------|
| **Database** | PostgreSQL | Primary RDBMS |
| **Version** | 10.5+ | Production version |
| **Hosting** | AWS RDS | Managed database service |
| **Instance** | `embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com` | Development endpoint |
| **Port** | 5432 | Default PostgreSQL port |
| **SSL Mode** | require | Encrypted connections |

### Data Access Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **ORM** | JOOQ | 3.11.10 → 3.19.15 | Type-safe SQL queries |
| **Migration** | Flyway | 5.2.4 → 10.21.0 | Version-controlled migrations |
| **Connection Pool** | HikariCP | Latest | High-performance pooling |
| **JDBC Driver** | PostgreSQL | 42.2.4 | Database connectivity |

### Connection Configuration

**Spring Boot Configuration**:
```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/coredb-urbanos?sslmode=require
    username: omsadmin
    password: ${DB_PASSWORD} # From Vault
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 50
      minimum-idle: 10
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      leak-detection-threshold: 60000
```

---

## Multi-Tenant Data Architecture

### Database-per-Tenant Pattern

**Architecture Principle**: Complete database isolation per tenant

**Benefits**:
- ✅ **Strong Data Isolation**: Zero risk of cross-tenant data leakage
- ✅ **Compliance**: Simplified audit trails and data residency
- ✅ **Customization**: Per-tenant schema modifications if needed
- ✅ **Performance**: No noisy neighbor problem
- ✅ **Scalability**: Independent scaling and optimization
- ✅ **Backup/Restore**: Granular per-tenant operations

**Drawbacks**:
- ⚠️ **Resource Overhead**: More database instances
- ⚠️ **Schema Changes**: Must apply to all tenant databases
- ⚠️ **Cross-Tenant Queries**: Not possible (by design)

### Tenant Database Mapping

| Tenant ID | Tenant Name | Database Name | Environment | Status |
|-----------|-------------|---------------|-------------|--------|
| TIDLT-100001 | coopeg-sbx | coredb-coopeg-sbx | Sandbox | Active |
| TIDLT-100002 | demo | coredb-demo | Demo | Active |
| TIDLT-100003 | dev | enginedevdb | Development | Active |
| TIDLT-100004 | shm | coredb-shm | Production | Active |
| TIDLT-100005 | urbanos | coredb-urbanos | Development | Active |
| TIDLT-100006 | coopeg-prd | coredb-coopeg-prd | Production | Active |
| TIDLT-100007 | coopegenergy | coredb-coopegenergy | Production | Active |

### Shared Configuration Schema

**`core_config` schema**: Shared across tenants for global configuration

**Tables**:
- `tenant` - Tenant master data
- `tenant_merchants` - Gateway configurations per tenant
- `oauth1_attributes` / `oauth2_attributes` - OAuth credentials
- `finance_gateway_attributes` - ERP integration settings
- `payment_gateway_attributes` - Payment processor settings
- `tax_gateway_attributes` - Tax provider settings
- `feature_flags` - Feature toggle configuration

**Storage**: Stored in separate shared database or centralized schema

---

## Schema Organization

### Schema Structure

Each tenant database contains 8 business schemas:

```
Tenant Database (e.g., coredb-urbanos)
├── core_engine         # Core domain entities
├── core_oms            # Order management
├── core_billing        # Financial transactions
├── core_pricing        # Product catalog
├── core_usage          # Usage data (high volume)
├── core_revenue        # Revenue recognition
├── core_config         # Configuration (tenant-specific)
└── core_mediation      # CDR processing
```

### Schema Responsibilities

| Schema | Purpose | Table Count | Key Characteristics |
|--------|---------|-------------|---------------------|
| **core_engine** | Core business entities | 15+ | Accounts, subscriptions, users |
| **core_oms** | Order lifecycle | 8+ | Orders, service lines, orchestration |
| **core_billing** | Financial operations | 12+ | Charges, invoices, payments |
| **core_pricing** | Product catalog | 10+ | Products, prices, bundles |
| **core_usage** | Usage records | 5+ | High-volume, partitioned |
| **core_revenue** | Accounting | 6+ | Deferred revenue, GL entries |
| **core_config** | Configuration | 10+ | Settings, attributes |
| **core_mediation** | CDR processing | 5+ | File tracking, errors |

---

## Complete Entity Reference

### 1. core_engine Schema

#### account (Customer Accounts)

**Purpose**: Customer account master records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Account ID (ACC-xxxxx) |
| parent_account_id | VARCHAR(50) | FK → account.id | Hierarchical accounts |
| account_number | VARCHAR(50) | UNIQUE | Customer-facing number |
| account_type | VARCHAR(20) | NOT NULL | INDIVIDUAL, BUSINESS |
| status | VARCHAR(20) | NOT NULL | ACTIVE, SUSPENDED, TERMINATED |
| balance | NUMERIC(19,4) | DEFAULT 0 | Current balance |
| credit_limit | NUMERIC(19,4) | | Credit limit |
| bill_cycle_day | INTEGER | | Billing cycle day (1-31) |
| currency_code | VARCHAR(3) | DEFAULT 'USD' | ISO currency code |
| created_date | TIMESTAMP | NOT NULL | Record creation |
| modified_date | TIMESTAMP | | Last modification |
| created_by | VARCHAR(50) | | User who created |
| modified_by | VARCHAR(50) | | User who modified |

**Indexes**:
```sql
CREATE INDEX idx_account_parent ON account(parent_account_id);
CREATE INDEX idx_account_status ON account(status);
CREATE INDEX idx_account_bill_cycle ON account(bill_cycle_day);
CREATE INDEX idx_account_number ON account(account_number);
```

**Business Rules**:
- Hierarchical support: `parent_account_id` allows account hierarchy
- Bill cycle day: 1-31, determines billing schedule
- Balance: Positive = credit, Negative = debt

---

#### subscription (Service Subscriptions)

**Purpose**: Active service subscriptions linking accounts to products

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Subscription ID (SUB-xxxxx) |
| account_id | VARCHAR(50) | FK → account.id | Account reference |
| product_id | VARCHAR(50) | FK → product.id | Product reference |
| price_offer_id | VARCHAR(50) | FK → price_offer.id | Pricing plan |
| subscription_number | VARCHAR(50) | UNIQUE | Display number |
| status | VARCHAR(20) | NOT NULL | ACTIVE, SUSPENDED, TERMINATED |
| start_date | DATE | NOT NULL | Subscription start |
| end_date | DATE | | Subscription end (NULL = ongoing) |
| next_billing_date | DATE | | Next billing date |
| billing_frequency | VARCHAR(20) | | MONTHLY, QUARTERLY, ANNUALLY |
| recurring_amount | NUMERIC(19,4) | | Recurring charge |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_subscription_account ON subscription(account_id);
CREATE INDEX idx_subscription_product ON subscription(product_id);
CREATE INDEX idx_subscription_status ON subscription(status);
CREATE INDEX idx_subscription_next_billing ON subscription(next_billing_date);
```

---

#### user (User Accounts)

**Purpose**: User authentication and authorization

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | User ID |
| username | VARCHAR(100) | UNIQUE, NOT NULL | Login username |
| password_hash | VARCHAR(255) | NOT NULL | BCrypt hash |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email address |
| account_id | VARCHAR(50) | FK → account.id | Associated account |
| role | VARCHAR(50) | NOT NULL | ADMIN, USER, CUSTOMER |
| status | VARCHAR(20) | NOT NULL | ACTIVE, LOCKED, EXPIRED |
| last_login | TIMESTAMP | | Last login timestamp |
| created_date | TIMESTAMP | NOT NULL | Record creation |

---

#### address (Addresses)

**Purpose**: Customer addresses (billing, service, shipping)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Address ID |
| account_id | VARCHAR(50) | FK → account.id | Account reference |
| address_type | VARCHAR(20) | NOT NULL | BILLING, SERVICE, SHIPPING |
| street_address | VARCHAR(255) | NOT NULL | Street address |
| city | VARCHAR(100) | NOT NULL | City |
| state | VARCHAR(50) | NOT NULL | State/Province |
| postal_code | VARCHAR(20) | NOT NULL | ZIP/Postal code |
| country | VARCHAR(3) | NOT NULL | ISO country code |
| is_default | BOOLEAN | DEFAULT false | Default address flag |
| validated | BOOLEAN | DEFAULT false | Address validation status |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_address_account ON address(account_id);
CREATE INDEX idx_address_type ON address(address_type);
CREATE INDEX idx_address_postal ON address(postal_code);
```

---

### 2. core_oms Schema

#### order (Order Records)

**Purpose**: Customer orders (new, change, disconnect)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Order ID (ORD-xxxxx) |
| account_id | VARCHAR(50) | FK → account.id | Account reference |
| order_number | VARCHAR(50) | UNIQUE | Display order number |
| order_type | VARCHAR(20) | NOT NULL | NEW_SERVICE, CHANGE, DISCONNECT |
| status | VARCHAR(20) | NOT NULL | CREATED, VALIDATED, PROVISIONING, COMPLETED, FAILED, CANCELLED |
| source_system | VARCHAR(50) | | Salesforce, Portal, API |
| external_order_id | VARCHAR(100) | | External system reference |
| extended_data | JSONB | | Flexible order attributes |
| error_message | TEXT | | Error details if failed |
| created_date | TIMESTAMP | NOT NULL | Order creation |
| completed_date | TIMESTAMP | | Order completion |

**Indexes**:
```sql
CREATE INDEX idx_order_account ON order(account_id);
CREATE INDEX idx_order_status ON order(status);
CREATE INDEX idx_order_type ON order(order_type);
CREATE INDEX idx_order_created ON order(created_date DESC);
CREATE INDEX idx_order_extended_data ON order USING GIN (extended_data);
```

**Status Flow**:
```
CREATED → VALIDATED → PROVISIONING → COMPLETED
                ↓
              FAILED
                ↓
            CANCELLED
```

---

#### service_line (Order Line Items)

**Purpose**: Individual services/products within an order

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Service line ID |
| order_id | VARCHAR(50) | FK → order.id | Parent order |
| product_id | VARCHAR(50) | FK → product.id | Product reference |
| price_offer_id | VARCHAR(50) | FK → price_offer.id | Pricing plan |
| quantity | INTEGER | DEFAULT 1 | Quantity ordered |
| action | VARCHAR(20) | NOT NULL | ADD, CHANGE, REMOVE |
| service_identifier | VARCHAR(100) | | Phone number, IP, etc. |
| status | VARCHAR(20) | NOT NULL | PENDING, PROVISIONED, FAILED |
| extended_data | JSONB | | Service-specific attributes |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_service_line_order ON service_line(order_id);
CREATE INDEX idx_service_line_product ON service_line(product_id);
CREATE INDEX idx_service_line_status ON service_line(status);
```

---

#### order_activity (Order Audit Trail)

**Purpose**: Track all order status changes and activities

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Activity ID |
| order_id | VARCHAR(50) | FK → order.id | Order reference |
| old_status | VARCHAR(20) | | Previous status |
| new_status | VARCHAR(20) | NOT NULL | New status |
| activity_type | VARCHAR(50) | NOT NULL | STATUS_CHANGE, PROVISIONING, ERROR |
| description | TEXT | | Activity description |
| performed_by | VARCHAR(50) | | User/system who performed |
| created_date | TIMESTAMP | NOT NULL | Activity timestamp |

**Indexes**:
```sql
CREATE INDEX idx_order_activity_order ON order_activity(order_id);
CREATE INDEX idx_order_activity_created ON order_activity(created_date DESC);
```

---

#### orchestration_state (Orchestration Tracking)

**Purpose**: Track order processing through orchestration pipeline

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | State ID |
| order_id | VARCHAR(50) | FK → order.id | Order reference |
| current_step | VARCHAR(50) | NOT NULL | OrderLoader, OrderValidator, etc. |
| step_status | VARCHAR(20) | NOT NULL | IN_PROGRESS, COMPLETED, FAILED |
| retry_count | INTEGER | DEFAULT 0 | Number of retries |
| error_details | TEXT | | Error information |
| last_updated | TIMESTAMP | NOT NULL | Last state update |

**Orchestration Steps**:
1. OrderLoader - Load order data
2. OrderValidator - Validate business rules
3. OrderProcessor - Execute business logic
4. OrderUpdater - Update order status
5. RouteHandler - Route to external systems

---

### 3. core_billing Schema

#### charge (Individual Charges)

**Purpose**: Billable charges (recurring, usage, one-time)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Charge ID (CHG-xxxxx) |
| account_id | VARCHAR(50) | FK → account.id | Account reference |
| subscription_id | VARCHAR(50) | FK → subscription.id | Subscription reference |
| invoice_id | VARCHAR(50) | FK → invoice.id | Invoice reference (NULL if unbilled) |
| charge_type | VARCHAR(20) | NOT NULL | RECURRING, ONE_TIME, USAGE, ADHOC, ADJUSTMENT |
| description | VARCHAR(255) | NOT NULL | Charge description |
| amount | NUMERIC(19,4) | NOT NULL | Charge amount |
| tax_amount | NUMERIC(19,4) | DEFAULT 0 | Tax amount |
| total_amount | NUMERIC(19,4) | NOT NULL | Amount + tax |
| billing_date | DATE | NOT NULL | Date charged |
| status | VARCHAR(20) | NOT NULL | PENDING, BILLED, CANCELLED |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_charge_account ON charge(account_id);
CREATE INDEX idx_charge_subscription ON charge(subscription_id);
CREATE INDEX idx_charge_invoice ON charge(invoice_id);
CREATE INDEX idx_charge_billing_date ON charge(billing_date);
CREATE INDEX idx_charge_status ON charge(status);
```

**Charge Types**:
- **RECURRING**: Monthly, quarterly, annual subscription fees
- **ONE_TIME**: Setup fees, hardware sales
- **USAGE**: Metered usage (calls, data, SMS)
- **ADHOC**: Manual charges
- **ADJUSTMENT**: Corrections, credits

---

#### invoice (Customer Invoices)

**Purpose**: Generated customer invoices

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Invoice ID (INV-xxxxx) |
| account_id | VARCHAR(50) | FK → account.id | Account reference |
| invoice_number | VARCHAR(50) | UNIQUE | Display invoice number |
| invoice_date | DATE | NOT NULL | Invoice generation date |
| due_date | DATE | NOT NULL | Payment due date |
| subtotal | NUMERIC(19,4) | NOT NULL | Pre-tax total |
| tax_total | NUMERIC(19,4) | NOT NULL | Total tax |
| total_amount | NUMERIC(19,4) | NOT NULL | Invoice total |
| amount_paid | NUMERIC(19,4) | DEFAULT 0 | Amount paid |
| balance | NUMERIC(19,4) | NOT NULL | Outstanding balance |
| status | VARCHAR(20) | NOT NULL | PENDING, SENT, PAID, OVERDUE, CANCELLED |
| pdf_url | VARCHAR(500) | | S3 URL for PDF |
| uuid | VARCHAR(36) | | CFDI UUID (Mexico) |
| cfdi_xml | TEXT | | CFDI XML (Mexico) |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_invoice_account ON invoice(account_id);
CREATE INDEX idx_invoice_number ON invoice(invoice_number);
CREATE INDEX idx_invoice_status ON invoice(status);
CREATE INDEX idx_invoice_due_date ON invoice(due_date);
CREATE INDEX idx_unpaid_invoices ON invoice(account_id) WHERE status IN ('PENDING', 'SENT', 'OVERDUE');
```

**Status Flow**:
```
PENDING → SENT → PAID
            ↓
        OVERDUE → PAID
            ↓
        CANCELLED
```

---

#### payment (Payment Transactions)

**Purpose**: Payment records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Payment ID (PAY-xxxxx) |
| account_id | VARCHAR(50) | FK → account.id | Account reference |
| payment_method_id | VARCHAR(50) | | Payment method reference |
| payment_number | VARCHAR(50) | UNIQUE | Display payment number |
| amount | NUMERIC(19,4) | NOT NULL | Payment amount |
| payment_date | DATE | NOT NULL | Payment date |
| payment_type | VARCHAR(20) | NOT NULL | CARD, ACH, WIRE, CASH, CHECK |
| external_transaction_id | VARCHAR(100) | | Gateway transaction ID |
| status | VARCHAR(20) | NOT NULL | PENDING, COMPLETED, FAILED, REFUNDED |
| notes | TEXT | | Payment notes |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_payment_account ON payment(account_id);
CREATE INDEX idx_payment_date ON payment(payment_date DESC);
CREATE INDEX idx_payment_status ON payment(status);
CREATE INDEX idx_payment_external ON payment(external_transaction_id);
```

---

#### payment_allocation (Payment-to-Invoice Allocation)

**Purpose**: Link payments to invoices

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Allocation ID |
| payment_id | VARCHAR(50) | FK → payment.id | Payment reference |
| invoice_id | VARCHAR(50) | FK → invoice.id | Invoice reference |
| allocated_amount | NUMERIC(19,4) | NOT NULL | Amount allocated |
| allocation_date | DATE | NOT NULL | Allocation date |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Business Rules**:
- One payment can be allocated to multiple invoices
- One invoice can receive allocations from multiple payments
- Sum of allocations cannot exceed payment amount

**Indexes**:
```sql
CREATE INDEX idx_payment_allocation_payment ON payment_allocation(payment_id);
CREATE INDEX idx_payment_allocation_invoice ON payment_allocation(invoice_id);
```

---

#### balance_impact (Account Balance Changes)

**Purpose**: Audit trail for all balance changes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Impact ID |
| account_id | VARCHAR(50) | FK → account.id | Account reference |
| impact_type | VARCHAR(20) | NOT NULL | CHARGE, PAYMENT, ADJUSTMENT, REFUND |
| amount | NUMERIC(19,4) | NOT NULL | Impact amount (+ or -) |
| old_balance | NUMERIC(19,4) | NOT NULL | Balance before |
| new_balance | NUMERIC(19,4) | NOT NULL | Balance after |
| reference_id | VARCHAR(50) | | Charge ID, Payment ID, etc. |
| description | VARCHAR(255) | | Impact description |
| created_date | TIMESTAMP | NOT NULL | Impact timestamp |

**Indexes**:
```sql
CREATE INDEX idx_balance_impact_account ON balance_impact(account_id);
CREATE INDEX idx_balance_impact_created ON balance_impact(created_date DESC);
CREATE INDEX idx_balance_impact_type ON balance_impact(impact_type);
```

---

### 4. core_pricing Schema

#### product (Product Catalog)

**Purpose**: Product/service definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Product ID (PROD-xxxxx) |
| product_code | VARCHAR(50) | UNIQUE | SKU/Product code |
| name | VARCHAR(255) | NOT NULL | Product name |
| description | TEXT | | Product description |
| product_type | VARCHAR(20) | NOT NULL | SERVICE, HARDWARE, SOFTWARE |
| category | VARCHAR(50) | | Product category |
| status | VARCHAR(20) | NOT NULL | ACTIVE, INACTIVE, DISCONTINUED |
| requires_provisioning | BOOLEAN | DEFAULT false | Needs network provisioning |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_product_code ON product(product_code);
CREATE INDEX idx_product_status ON product(status);
CREATE INDEX idx_product_category ON product(category);
```

---

#### price_offer (Pricing Plans)

**Purpose**: Pricing configuration for products

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Price offer ID |
| product_id | VARCHAR(50) | FK → product.id | Product reference |
| offer_code | VARCHAR(50) | UNIQUE | Pricing code |
| name | VARCHAR(255) | NOT NULL | Offer name |
| price | NUMERIC(19,4) | NOT NULL | Price amount |
| currency_code | VARCHAR(3) | DEFAULT 'USD' | Currency |
| billing_frequency | VARCHAR(20) | NOT NULL | MONTHLY, QUARTERLY, ANNUALLY |
| effective_date | DATE | NOT NULL | Offer start date |
| expiration_date | DATE | | Offer end date |
| status | VARCHAR(20) | NOT NULL | ACTIVE, INACTIVE, EXPIRED |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_price_offer_product ON price_offer(product_id);
CREATE INDEX idx_price_offer_code ON price_offer(offer_code);
CREATE INDEX idx_price_offer_effective ON price_offer(effective_date);
```

---

#### bundle (Product Bundles)

**Purpose**: Product bundles/packages

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Bundle ID |
| bundle_code | VARCHAR(50) | UNIQUE | Bundle code |
| name | VARCHAR(255) | NOT NULL | Bundle name |
| description | TEXT | | Bundle description |
| bundle_type | VARCHAR(20) | NOT NULL | FIXED, FLEXIBLE |
| status | VARCHAR(20) | NOT NULL | ACTIVE, INACTIVE |
| created_date | TIMESTAMP | NOT NULL | Record creation |

---

#### discount (Discounts & Promotions)

**Purpose**: Discount configuration

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Discount ID |
| discount_code | VARCHAR(50) | UNIQUE | Promo code |
| name | VARCHAR(255) | NOT NULL | Discount name |
| discount_type | VARCHAR(20) | NOT NULL | PERCENTAGE, FIXED_AMOUNT |
| discount_value | NUMERIC(19,4) | NOT NULL | Discount value |
| applicable_products | VARCHAR(500) | | Product IDs (comma-separated) |
| effective_date | DATE | NOT NULL | Start date |
| expiration_date | DATE | | End date |
| max_uses | INTEGER | | Usage limit |
| current_uses | INTEGER | DEFAULT 0 | Usage count |
| status | VARCHAR(20) | NOT NULL | ACTIVE, INACTIVE, EXPIRED |
| created_date | TIMESTAMP | NOT NULL | Record creation |

---

### 5. core_usage Schema

#### usage_record (Usage Data - Partitioned)

**Purpose**: High-volume usage records (CDRs)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Usage record ID |
| account_id | VARCHAR(50) | FK → account.id | Account reference |
| subscription_id | VARCHAR(50) | FK → subscription.id | Subscription reference |
| source_id | VARCHAR(100) | | Source identifier (phone, IP) |
| destination_id | VARCHAR(100) | | Destination (phone, URL) |
| usage_date | DATE | NOT NULL | Usage date (partition key) |
| start_time | TIMESTAMP | NOT NULL | Usage start time |
| duration | INTEGER | | Duration in seconds |
| volume | NUMERIC(19,4) | | Volume (MB, minutes, count) |
| service_type | VARCHAR(20) | NOT NULL | VOICE, DATA, SMS |
| rated | BOOLEAN | DEFAULT false | Rating complete |
| rated_amount | NUMERIC(19,4) | | Calculated charge |
| billed | BOOLEAN | DEFAULT false | Included in invoice |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Partitioning**:
```sql
-- Partitioned by month
CREATE TABLE usage_record_2026_01 PARTITION OF usage_record
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE usage_record_2026_02 PARTITION OF usage_record
FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
```

**Indexes (per partition)**:
```sql
CREATE INDEX idx_usage_account_2026_01 ON usage_record_2026_01(account_id);
CREATE INDEX idx_usage_subscription_2026_01 ON usage_record_2026_01(subscription_id);
CREATE INDEX idx_usage_date_2026_01 ON usage_record_2026_01(usage_date);
CREATE INDEX idx_usage_rated_2026_01 ON usage_record_2026_01(rated) WHERE rated = false;
CREATE INDEX idx_usage_billed_2026_01 ON usage_record_2026_01(billed) WHERE billed = false;
```

---

#### usage_accumulator (Aggregated Usage)

**Purpose**: Real-time usage accumulation for quota management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Accumulator ID |
| subscription_id | VARCHAR(50) | FK → subscription.id | Subscription reference |
| accumulator_type | VARCHAR(20) | NOT NULL | VOICE_MINUTES, DATA_GB, SMS_COUNT |
| accumulation_period | VARCHAR(20) | NOT NULL | MONTHLY, DAILY |
| period_start | DATE | NOT NULL | Period start date |
| period_end | DATE | NOT NULL | Period end date |
| accumulated_value | NUMERIC(19,4) | DEFAULT 0 | Accumulated usage |
| last_updated | TIMESTAMP | NOT NULL | Last update time |

**Business Use**: Track usage quotas and overage

**Indexes**:
```sql
CREATE INDEX idx_usage_accumulator_subscription ON usage_accumulator(subscription_id);
CREATE INDEX idx_usage_accumulator_period ON usage_accumulator(period_start, period_end);
```

---

#### usage_quota (Usage Quota Limits)

**Purpose**: Define usage quotas for subscriptions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Quota ID |
| subscription_id | VARCHAR(50) | FK → subscription.id | Subscription reference |
| quota_type | VARCHAR(20) | NOT NULL | VOICE_MINUTES, DATA_GB, SMS_COUNT |
| quota_limit | NUMERIC(19,4) | NOT NULL | Quota limit |
| warning_threshold | NUMERIC(19,4) | | Warning threshold (%) |
| action_on_exceed | VARCHAR(20) | NOT NULL | BLOCK, CHARGE, WARN |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Business Use**: Implement usage-based controls

---

### 6. core_revenue Schema

#### deferred_revenue (Deferred Revenue Tracking)

**Purpose**: Track deferred revenue for compliance (IFRS 15, ASC 606)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Deferred revenue ID |
| charge_id | VARCHAR(50) | FK → charge.id | Source charge |
| total_amount | NUMERIC(19,4) | NOT NULL | Total deferred amount |
| recognized_amount | NUMERIC(19,4) | DEFAULT 0 | Amount recognized |
| remaining_amount | NUMERIC(19,4) | NOT NULL | Amount remaining |
| recognition_start_date | DATE | NOT NULL | Recognition start |
| recognition_end_date | DATE | NOT NULL | Recognition end |
| recognition_method | VARCHAR(20) | NOT NULL | STRAIGHT_LINE, MILESTONE |
| status | VARCHAR(20) | NOT NULL | PENDING, IN_PROGRESS, COMPLETED |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Business Use**: Monthly revenue recognition processing

**Indexes**:
```sql
CREATE INDEX idx_deferred_revenue_charge ON deferred_revenue(charge_id);
CREATE INDEX idx_deferred_revenue_status ON deferred_revenue(status);
CREATE INDEX idx_deferred_revenue_dates ON deferred_revenue(recognition_start_date, recognition_end_date);
```

---

#### journal_entry (General Ledger Entries)

**Purpose**: Financial journal entries for ERP integration

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Journal entry ID |
| entry_date | DATE | NOT NULL | Entry date |
| entry_type | VARCHAR(20) | NOT NULL | REVENUE, EXPENSE, ADJUSTMENT |
| debit_account | VARCHAR(50) | NOT NULL | GL account (debit) |
| credit_account | VARCHAR(50) | NOT NULL | GL account (credit) |
| amount | NUMERIC(19,4) | NOT NULL | Entry amount |
| description | VARCHAR(255) | | Entry description |
| reference_id | VARCHAR(50) | | Invoice ID, Payment ID, etc. |
| posted | BOOLEAN | DEFAULT false | Posted to ERP |
| created_date | TIMESTAMP | NOT NULL | Record creation |

**Indexes**:
```sql
CREATE INDEX idx_journal_entry_date ON journal_entry(entry_date DESC);
CREATE INDEX idx_journal_entry_type ON journal_entry(entry_type);
CREATE INDEX idx_journal_entry_posted ON journal_entry(posted) WHERE posted = false;
```

---

### 7. core_mediation Schema

#### cdr_file (CDR File Tracking)

**Purpose**: Track CDR file ingestion

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | File ID |
| file_name | VARCHAR(255) | NOT NULL | Original file name |
| file_path | VARCHAR(500) | | S3/SFTP path |
| file_size | BIGINT | | File size in bytes |
| record_count | INTEGER | | Total records |
| processed_count | INTEGER | DEFAULT 0 | Processed records |
| error_count | INTEGER | DEFAULT 0 | Error records |
| status | VARCHAR(20) | NOT NULL | PENDING, PROCESSING, COMPLETED, FAILED |
| started_at | TIMESTAMP | | Processing start |
| completed_at | TIMESTAMP | | Processing end |
| created_date | TIMESTAMP | NOT NULL | File received |

**Indexes**:
```sql
CREATE INDEX idx_cdr_file_status ON cdr_file(status);
CREATE INDEX idx_cdr_file_created ON cdr_file(created_date DESC);
```

---

#### cdr_error (CDR Processing Errors)

**Purpose**: Track CDR processing errors

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Error ID |
| cdr_file_id | VARCHAR(50) | FK → cdr_file.id | File reference |
| line_number | INTEGER | | Line number in file |
| raw_data | TEXT | | Original CDR data |
| error_type | VARCHAR(50) | NOT NULL | INVALID_FORMAT, DUPLICATE, etc. |
| error_message | TEXT | | Error details |
| created_date | TIMESTAMP | NOT NULL | Error timestamp |

---

## Relationships & Foreign Keys

### Primary Relationships

**Account-Centric**:
```
account (1) ──< (N) subscription
account (1) ──< (N) order
account (1) ──< (N) invoice
account (1) ──< (N) payment
account (1) ──< (N) charge
account (1) ──< (N) address
account (1) ──< (N) user
account (1) ──< (N) usage_record
account (1) ──< (N) balance_impact
```

**Order Processing**:
```
order (1) ──< (N) service_line
order (1) ──< (N) order_activity
order (1) ──< (1) orchestration_state
```

**Billing & Payments**:
```
subscription (1) ──< (N) charge
invoice (1) ──< (N) charge
payment (1) ──< (N) payment_allocation
invoice (1) ──< (N) payment_allocation
charge (1) ──< (1) deferred_revenue
```

**Product Catalog**:
```
product (1) ──< (N) price_offer
product (1) ──< (N) subscription
product (1) ──< (N) service_line
price_offer (1) ──< (N) subscription
```

**Usage**:
```
subscription (1) ──< (N) usage_record
subscription (1) ──< (N) usage_accumulator
subscription (1) ──< (N) usage_quota
```

---

## Indexes & Performance

### Index Types

**B-Tree Indexes** (Default):
- Foreign keys (account_id, subscription_id, etc.)
- Status columns (frequently filtered)
- Date columns (range queries)

**Composite Indexes**:
```sql
-- Multi-column queries
CREATE INDEX idx_invoice_account_status ON invoice(account_id, status);
CREATE INDEX idx_charge_account_billing_date ON charge(account_id, billing_date);
```

**Partial Indexes**:
```sql
-- Filtered queries
CREATE INDEX idx_unpaid_invoices ON invoice(account_id) 
WHERE status IN ('PENDING', 'SENT', 'OVERDUE');

CREATE INDEX idx_unrated_usage ON usage_record(subscription_id) 
WHERE rated = false;
```

**GIN Indexes** (JSONB):
```sql
-- JSONB columns
CREATE INDEX idx_order_extended_data ON order USING GIN (extended_data);
CREATE INDEX idx_service_line_extended_data ON service_line USING GIN (extended_data);
```

### Performance Statistics

**Query Performance Targets**:
- Account lookup: < 50ms
- Invoice list: < 200ms
- Usage query: < 500ms
- Order search: < 300ms

---

## Partitioning Strategy

### Usage Record Partitioning

**Partition Key**: `usage_date` (monthly partitions)

**Benefits**:
- Faster queries (partition pruning)
- Easier archival (detach old partitions)
- Better vacuum performance
- Improved index maintenance

**Partition Management**:
```sql
-- Create next month's partition
CREATE TABLE usage_record_2026_03 PARTITION OF usage_record
FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Create indexes on new partition
CREATE INDEX idx_usage_account_2026_03 ON usage_record_2026_03(account_id);
-- ... other indexes

-- Archive old partition (after 24 months)
ALTER TABLE usage_record DETACH PARTITION usage_record_2024_01;
-- Move to archive table or delete
```

**Automated Partition Creation**:
- Scheduled job runs monthly
- Creates partition 2 months ahead
- Archives partitions older than 24 months

---

## Database Migrations

### Flyway Migration Structure

**Location**: `engine/src/main/resources/db/migration/`

**Naming Convention**: `V{version}__{description}.sql`

**Migration Sequence**:
```
V1__Create_Schema.sql
V2__Create_Enum_Types.sql
V3__Create_Config_Tables.sql
V4__Create_Engine_Tables.sql
V5__Create_OMS_Tables.sql
V6__Create_Billing_Tables.sql
V7__Create_Pricing_Tables.sql
V8__Create_Usage_Tables.sql
V9__Create_Revenue_Tables.sql
V10__Create_Mediation_Tables.sql
V11__Create_Indexes.sql
V12__Create_Foreign_Keys.sql
V13__Create_Views.sql
V14__Create_Functions.sql
V15__Create_Triggers.sql
V16__Initial_Config_Data.sql
```

### Migration Execution

**Automatic (Spring Boot)**:
```yaml
spring:
  flyway:
    enabled: true
    baseline-on-migrate: true
    locations: classpath:db/migration
    validate-on-migrate: true
```

**Manual**:
```bash
mvn flyway:migrate -Dspring.profiles.active=dev
mvn flyway:info     # Show migration status
mvn flyway:validate # Validate migration checksums
```

### Migration Best Practices

**DO**:
- ✅ Always write backward-compatible migrations
- ✅ Test migrations on dev/staging first
- ✅ Use transactions (BEGIN/COMMIT)
- ✅ Add descriptive comments
- ✅ Create indexes CONCURRENTLY in production

**DON'T**:
- ❌ Modify existing migrations (breaks checksums)
- ❌ Use DROP statements without extreme caution
- ❌ Run data migrations in peak hours
- ❌ Skip migration testing

---

## Data Access Patterns

### JOOQ Type-Safe Queries

**Example: Find Account with Subscriptions**:
```groovy
// Generated JOOQ classes
import static com.embrix.core.engine.db.tables.Account.ACCOUNT
import static com.embrix.core.engine.db.tables.Subscription.SUBSCRIPTION

class AccountRepository {
    @Autowired
    DSLContext dsl
    
    Account findAccountWithSubscriptions(String accountId) {
        def accountRecord = dsl
            .select()
            .from(ACCOUNT)
            .where(ACCOUNT.ID.eq(accountId))
            .fetchOne()
        
        if (!accountRecord) return null
        
        def subscriptions = dsl
            .select()
            .from(SUBSCRIPTION)
            .where(SUBSCRIPTION.ACCOUNT_ID.eq(accountId))
            .and(SUBSCRIPTION.STATUS.eq('ACTIVE'))
            .fetch()
        
        return mapToAccount(accountRecord, subscriptions)
    }
}
```

**Example: Complex Query with Joins**:
```groovy
def invoicesWithCharges = dsl
    .select(
        INVOICE.ID,
        INVOICE.INVOICE_NUMBER,
        INVOICE.TOTAL_AMOUNT,
        CHARGE.ID,
        CHARGE.DESCRIPTION,
        CHARGE.AMOUNT
    )
    .from(INVOICE)
    .leftJoin(CHARGE).on(CHARGE.INVOICE_ID.eq(INVOICE.ID))
    .where(INVOICE.ACCOUNT_ID.eq(accountId))
    .and(INVOICE.STATUS.in('PENDING', 'OVERDUE'))
    .orderBy(INVOICE.INVOICE_DATE.desc())
    .fetch()
```

**Example: Pagination**:
```groovy
def orders = dsl
    .select()
    .from(ORDER)
    .where(ORDER.ACCOUNT_ID.eq(accountId))
    .orderBy(ORDER.CREATED_DATE.desc())
    .limit(pageSize)
    .offset(pageNumber * pageSize)
    .fetch()
```

---

## Backup & Recovery

### Backup Strategy

**Automated Backups** (AWS RDS):
- Daily automated snapshots (7-day retention)
- 30-minute backup window (low-traffic period)
- Point-in-time recovery (up to backup retention period)

**Manual Backups**:
```bash
# On-demand snapshot
aws rds create-db-snapshot \
  --db-instance-identifier embrix-rds-urbanos \
  --db-snapshot-identifier urbanos-manual-$(date +%Y%m%d)

# Export to S3
aws rds export-db-snapshot-to-s3 \
  --snapshot-identifier urbanos-manual-20260211 \
  --s3-bucket-name embrix-backups \
  --iam-role-arn arn:aws:iam::123456789012:role/RDSExport
```

### Recovery Procedures

**Point-in-Time Recovery**:
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier embrix-rds-urbanos \
  --target-db-instance-identifier embrix-rds-urbanos-restore \
  --restore-time 2026-02-11T10:30:00Z
```

**Snapshot Restore**:
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier embrix-rds-urbanos-restore \
  --db-snapshot-identifier urbanos-manual-20260211
```

---

## Summary

### Database Architecture Highlights

- **Technology**: PostgreSQL 10.5+ with JOOQ for type-safe queries
- **Multi-Tenancy**: Database-per-tenant with complete isolation
- **Schema Organization**: 8 business schemas per tenant database
- **Entity Count**: 50+ tables across all schemas
- **Partitioning**: Monthly partitioning on high-volume usage_record table
- **Indexing**: B-tree, composite, partial, and GIN indexes for performance
- **Migrations**: Version-controlled via Flyway
- **Backup**: Automated daily snapshots with point-in-time recovery

### Key Performance Features

- Connection pooling via HikariCP (20-50 connections)
- Partitioned usage tables for fast queries
- Strategic indexing on foreign keys and filters
- JSONB for flexible attributes with GIN indexes
- Caching layer (Redis) for expensive queries

---

**For backend service integration details (engine hubs, gateways, transactions), see the Technical Deep Dive guide (`part2-technical-deep-dive.html`).**
