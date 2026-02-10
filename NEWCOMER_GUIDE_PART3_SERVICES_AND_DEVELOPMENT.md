# Embrix O2X Platform - Newcomer's Guide (Part 3)
## Core Services, Business Flows & Development Guide

**Version**: 3.1.9-SNAPSHOT  
**Last Updated**: February 2026  
**Prerequisites**: Read Parts 1 and 2 first

---

## Table of Contents - Part 3

1. [Core Services Layer](#1-core-services-layer)
2. [Database Architecture](#2-database-architecture)
3. [Complete End-to-End Business Flows](#3-complete-end-to-end-business-flows)
4. [Development Environment Setup](#4-development-environment-setup)
5. [Common Development Tasks](#5-common-development-tasks)
6. [Testing Strategy](#6-testing-strategy)
7. [Troubleshooting & Debugging](#7-troubleshooting--debugging)
8. [Best Practices](#8-best-practices)

---

## 1. Core Services Layer

Core services are **thin wrappers** that expose business logic from `engine` via GraphQL APIs.

### 1.1 `service-billing` - Billing Operations

**Location:** `/core/service-billing`  
**Purpose:** Execute billing runs and charge generation

**Key Operations:**

**1. Billing Cycle Execution**
```graphql
mutation ExecuteBillingCycle {
  runBillingCycle(input: {
    billCycleDay: 1
    billingPeriodStart: "2024-01-01"
    billingPeriodEnd: "2024-01-31"
  }) {
    totalAccountsBilled
    totalChargesGenerated
    totalAmount
    errors {
      accountId
      errorMessage
    }
  }
}
```

**2. Proration Calculation**
```graphql
mutation CalculateProration {
  calculateProration(input: {
    subscriptionId: "SUB-123"
    startDate: "2024-01-16"
    endDate: "2024-01-31"
    monthlyCharge: 30.00
    prorationModel: DAYS_IN_MONTH
  }) {
    proratedAmount
    daysActive
    daysInPeriod
  }
}
# Result: {proratedAmount: 15.48, daysActive: 16, daysInPeriod: 31}
```

**3. Ad-Hoc Charge Creation**
```graphql
mutation CreateAdhocCharge {
  createCharge(input: {
    accountId: "ACC-1001"
    description: "Late Payment Fee"
    amount: 25.00
    chargeType: ADHOC
    billingDate: "2024-01-15"
  }) {
    id
    status
  }
}
```

### 1.2 `service-invoice` - Invoice Generation

**Location:** `/core/service-invoice`  
**Purpose:** Generate customer-facing invoice documents

**Key Operations:**

**1. Generate Invoice**
```graphql
mutation GenerateInvoice {
  generateInvoice(input: {
    accountId: "ACC-1001"
    billingPeriodStart: "2024-01-01"
    billingPeriodEnd: "2024-01-31"
    format: PDF
    templateName: "invoice_standard"
  }) {
    invoiceId
    pdfUrl
    totalAmount
  }
}
```

**Invoice Generation Process:**
```
[1] Retrieve Data
    ├─→ Account details
    ├─→ All charges for period
    ├─→ Tax calculations
    └─→ Payment history

[2] Apply Template
    ├─→ Select Thymeleaf template
    ├─→ Inject data into template
    └─→ Generate HTML

[3] Convert to PDF
    ├─→ iText processes HTML
    ├─→ Apply styling
    └─→ Generate PDF bytes

[4] Upload to S3
    ├─→ Bucket: {tenant}-invoices
    ├─→ Key: invoices/2024/01/ACC-1001/INV-2024-001.pdf
    └─→ Get public URL

[5] Update Database
    ├─→ invoice.pdfUrl = S3 URL
    └─→ invoice.status = SENT

[6] Send Notification
    └─→ Email to customer with download link
```

**2. Regenerate Invoice (Corrections)**
```graphql
mutation RegenerateInvoice {
  regenerateInvoice(input: {
    invoiceId: "INV-2024-001"
    reason: "Corrected tax calculation"
  }) {
    newInvoiceId
    pdfUrl
  }
}
```

### 1.3 `service-usage` - Usage Data Repository

**Location:** `/core/service-usage`  
**Purpose:** High-performance usage data storage and query layer

**Key Operations:**

**1. Query Usage Records**
```graphql
query GetUsage {
  searchUsageRecords(filter: {
    accountId: "ACC-1001"
    startDate: "2024-01-01"
    endDate: "2024-01-31"
    serviceType: VOICE_CALL
    status: RATED
  }) {
    records {
      startTime
      duration
      destination
      ratedAmount
    }
    totalRecords
    totalAmount
  }
}
```

**2. Usage Summary**
```graphql
query UsageSummary {
  getUsageSummary(input: {
    accountId: "ACC-1001"
    period: "2024-01"
  }) {
    voiceMinutes
    smsCount
    dataGB
    totalCharges
    quotaStatus {
      usageType
      used
      limit
      remaining
    }
  }
}
```

**3. Re-Rating (Corrections)**
```graphql
mutation ReRateUsage {
  reRateUsageRecords(input: {
    usageRecordIds: ["USAGE-001", "USAGE-002"]
    newRatingPlanId: "PLAN-CORRECTED"
    reason: "Applied correct pricing tier"
  }) {
    recordsUpdated
    totalAdjustment
  }
}
```

### 1.4 `service-mediation` - Usage Data Ingestion

**Location:** `/core/service-mediation`  
**Purpose:** Ingest and normalize raw usage data from network elements

**Mediation Process:**

```
[1] CDR File Detection
    ├─→ Network element places file on SFTP
    └─→ File: mcm_voice_20240115_001.csv

[2] File Ingestion
    ├─→ Download from SFTP
    ├─→ Parse file format
    └─→ Extract CDR records

[3] Normalization
    ├─→ Map vendor-specific fields to canonical format
    │   Network Field → Canonical Field
    │   ├─→ calling_number → sourceId
    │   ├─→ called_number → destination
    │   ├─→ call_start → startTime
    │   ├─→ call_duration → duration
    │   └─→ call_type → serviceType
    └─→ Validate data quality

[4] Enrichment
    ├─→ Lookup account by sourceId (IMSI, phone number, IP)
    ├─→ Lookup subscription
    ├─→ Classify call type (local, long distance, international)
    └─→ Add metadata

[5] Deduplication
    ├─→ Check if CDR already processed (by unique ID)
    └─→ Skip duplicates

[6] Storage
    ├─→ Insert into usage_record table
    └─→ Status: UNRATED

[7] Trigger Rating
    └─→ Push to USAGE queue for rating
```

**Mediation Example:**

**Raw CDR (Network Format):**
```csv
2024-01-15 10:30:00,5215551234567,5215557654321,00:10:00,VOICE
2024-01-15 10:35:00,5215551234567,5215557654322,00:05:30,VOICE
```

**Canonical Format:**
```json
{
  "id": "USAGE-2024-001",
  "accountId": "ACC-1001",
  "subscriptionId": "SUB-123",
  "sourceId": "5215551234567",
  "startTime": "2024-01-15T10:30:00Z",
  "endTime": "2024-01-15T10:40:00Z",
  "duration": 600,
  "volume": null,
  "destination": "5215557654321",
  "serviceType": "VOICE_CALL",
  "callType": "LOCAL",
  "ratedAmount": 0.00,
  "ratingPlanId": null,
  "status": "UNRATED",
  "billed": false,
  "created_date": "2024-01-15T11:00:00Z"
}
```

### 1.5 `service-payment` - Payment Management

**Location:** `/core/service-payment`  
**Purpose:** Payment method and transaction management

**Key Operations:**

**1. Process Manual Payment**
```graphql
mutation ProcessPayment {
  processPayment(input: {
    accountId: "ACC-1001"
    amount: 752.84
    paymentMethodId: "pm_stripe_12345"
    paymentType: CREDIT_CARD
    invoiceIds: ["INV-2024-001"]
  }) {
    paymentId
    status
    transactionId
  }
}
```

**Payment Processing Flow:**
```
[1] Validate Payment
    ├─→ Check payment amount > 0
    ├─→ Verify payment method active
    └─→ Validate account exists

[2] Call Payment Gateway
    ├─→ payment-gateway.processPayment()
    ├─→ External processor (Stripe, PayPal, bank)
    └─→ Receive transaction result

[3] Record Payment
    ├─→ Create payment record in database
    │   - payment_id: PAY-2024-001
    │   - amount: 752.84
    │   - external_transaction_id: ch_stripe_789
    │   - status: COMPLETED
    └─→ Payment date: now()

[4] Allocate to Invoices
    ├─→ Find invoices specified or oldest pending
    ├─→ For each invoice (oldest first):
    │   ├─→ Calculate allocation amount
    │   │   allocation = min(remaining_payment, invoice.balance)
    │   ├─→ Create payment_allocation record
    │   ├─→ Update invoice.amount_paid += allocation
    │   ├─→ Update invoice.balance -= allocation
    │   └─→ If invoice.balance == 0: invoice.status = PAID
    └─→ Remaining payment → account credit

[5] Update Account Balance
    ├─→ account.balance += payment.amount
    ├─→ Create balance_impact record for audit
    └─→ If balance was negative and now >= 0:
        trigger auto-resume (EP-5480)

[6] Notification
    ├─→ Send payment confirmation email
    └─→ Update customer portal
```

**2. Refund Payment**
```graphql
mutation RefundPayment {
  refundPayment(input: {
    paymentId: "PAY-2024-001"
    amount: 752.84
    reason: "Service cancelled"
  }) {
    refundId
    status
  }
}
```

### 1.6 `service-revenue` - Revenue Recognition

**Location:** `/core/service-revenue`  
**Purpose:** IFRS 15 / ASC 606 compliant revenue recognition

**Key Concepts:**

**1. Performance Obligation**
A promise to deliver a good or service to customer.

**Example:**
- Sell annual internet subscription for $1,200 upfront
- Performance obligation: Provide internet service for 12 months
- Revenue recognition: Recognize $100/month over 12 months

**2. Deferred Revenue**
Payment received but service not yet delivered.

**Example:**
```
Customer pays $1,200 on Jan 1 for annual subscription
    ↓
[Initial Recording]
    Debit: Cash $1,200
    Credit: Deferred Revenue (Liability) $1,200
    ↓
[Monthly Recognition - Feb 1]
    Debit: Deferred Revenue $100
    Credit: Revenue (Income) $100
    ↓
[Monthly Recognition - Mar 1]
    Debit: Deferred Revenue $100
    Credit: Revenue (Income) $100
    ↓
... (repeat for 12 months)
```

**Revenue Recognition Flow:**
```
[1] Charge Created
    └─→ service-billing creates charge for $1,200

[2] Analyze Revenue Model
    ├─→ Charge type: RECURRING
    ├─→ Recognition model: STRAIGHT_LINE
    └─→ Period: 12 months

[3] Create Deferred Revenue
    ├─→ deferred_revenue.total_amount = 1200.00
    ├─→ deferred_revenue.recognized_amount = 0.00
    ├─→ deferred_revenue.remaining_amount = 1200.00
    ├─→ recognition_start = 2024-01-01
    └─→ recognition_end = 2024-12-31

[4] Daily Recognition Job (runs nightly)
    ├─→ For each active deferred revenue:
    │   ├─→ Calculate daily amount: 1200 / 365 = 3.29
    │   ├─→ Create journal entry:
    │   │   Debit: Deferred Revenue 3.29
    │   │   Credit: Revenue 3.29
    │   ├─→ Update recognized_amount += 3.29
    │   └─→ Update remaining_amount -= 3.29
    └─→ Export to finance-gateway

[5] Monthly Reporting
    └─→ Revenue recognized in January: 3.29 * 31 = 101.99
```

**GraphQL Operations:**
```graphql
query GetRevenueSchedule {
  getRevenueSchedule(input: {
    chargeId: "CHG-2024-001"
  }) {
    totalAmount
    recognizedAmount
    remainingAmount
    recognitionStartDate
    recognitionEndDate
    monthlyBreakdown {
      month
      amount
    }
  }
}
```

### 1.7 `batch-process` - Background Jobs

**Location:** `/core/batch-process`  
**Purpose:** Long-running, resource-intensive batch jobs

**Key Jobs:**

**1. Daily Billing Cycle**
```groovy
@Scheduled(cron = "0 0 2 * * *")  // 2 AM daily
void executeDailyBillingCycle() {
    // Find accounts with bill_cycle_day = today
    Integer today = LocalDate.now().getDayOfMonth()
    List<Account> accounts = findAccountsByBillCycleDay(today)
    
    log.info("Starting billing for ${accounts.size()} accounts")
    
    // Process in parallel (thread pool)
    accounts.eachParallel { account ->
        try {
            billingService.billAccount(account)
        } catch (Exception e) {
            log.error("Billing failed for ${account.id}", e)
        }
    }
}
```

**2. Usage Rating Batch**
```groovy
@Scheduled(cron = "0 0 * * * *")  // Hourly
void processUnratedUsage() {
    // Find unrated usage records
    List<UsageRecord> unrated = findUnratedUsageRecords()
    
    log.info("Rating ${unrated.size()} usage records")
    
    // Process in batches of 1000
    unrated.collate(1000).each { batch ->
        usageService.rateUsageBatch(batch)
    }
}
```

**3. Revenue Recognition Batch**
```groovy
@Scheduled(cron = "0 0 1 * * *")  // 1 AM daily
void recognizeRevenue() {
    LocalDate today = LocalDate.now()
    
    // Find active deferred revenue
    List<DeferredRevenue> active = findActiveDeferredRevenue(today)
    
    active.each { deferredRevenue ->
        BigDecimal dailyAmount = deferredRevenue.totalAmount / 
            ChronoUnit.DAYS.between(
                deferredRevenue.recognitionStartDate,
                deferredRevenue.recognitionEndDate
            )
        
        // Create journal entry
        JournalEntry entry = createJournalEntry(
            debit: "Deferred Revenue",
            credit: "Revenue",
            amount: dailyAmount,
            reference: deferredRevenue.id
        )
        
        // Update deferred revenue
        deferredRevenue.recognizedAmount += dailyAmount
        deferredRevenue.remainingAmount -= dailyAmount
        save(deferredRevenue)
    }
}
```

**4. Payment File Processing**
```groovy
@Scheduled(cron = "0 */15 * * * *")  // Every 15 minutes
void processPaymentFiles() {
    // Check S3 for new payment files
    List<S3Object> files = s3Client.listObjects(
        bucket: "${tenant}-payments",
        prefix: "input/"
    )
    
    files.each { file ->
        if (!isProcessed(file.key)) {
            try {
                // Download file
                InputStream content = s3Client.getObject(file)
                
                // Parse CSV
                List<Payment> payments = parsePaymentFile(content)
                
                // Process each payment
                payments.each { payment ->
                    paymentService.processPayment(payment)
                }
                
                // Mark as processed
                markFileProcessed(file.key)
                
            } catch (Exception e) {
                log.error("Failed to process ${file.key}", e)
                alertSlack("#payment-errors", "Payment file failed: ${file.key}")
            }
        }
    }
}
```

---

## 2. Database Architecture

### 2.1 Schema Organization

PostgreSQL database organized into domain-specific schemas:

```
Database: coredb-{tenant}
├── core_engine (Shared Business Entities)
│   ├── account
│   ├── subscription
│   ├── address
│   ├── user
│   └── contact
├── core_oms (Order Management)
│   ├── order
│   ├── service_line
│   ├── order_activity
│   └── orchestration_state
├── core_billing (Financial Data)
│   ├── charge
│   ├── invoice
│   ├── payment
│   ├── payment_allocation
│   ├── balance_impact
│   └── bill_unit
├── core_pricing (Product Catalog)
│   ├── product
│   ├── price_offer
│   ├── discount
│   └── bundle
├── core_usage (High-Volume Usage)
│   ├── usage_record (partitioned by month)
│   ├── usage_accumulator
│   └── usage_quota
├── core_revenue (Financial Accounting)
│   ├── journal_entry
│   ├── deferred_revenue
│   └── performance_obligation
├── core_config (Configuration)
│   ├── tenant
│   ├── tenant_merchants
│   ├── oauth1_attributes
│   ├── oauth2_attributes
│   ├── finance_gateway_attributes
│   ├── payment_gateway_attributes
│   └── tax_gateway_attributes
└── core_mediation (Mediation Processing)
    ├── cdr_file
    ├── cdr_error
    └── mediation_stats
```

### 2.2 Key Tables Deep Dive

#### 2.2.1 account Table

```sql
CREATE TABLE core_engine.account (
    id VARCHAR(50) PRIMARY KEY,
    parent_account_id VARCHAR(50),                    -- For hierarchical accounts
    account_type VARCHAR(20) NOT NULL,                -- RESIDENTIAL, BUSINESS, WHOLESALE
    status VARCHAR(20) NOT NULL,                      -- ACTIVE, SUSPENDED, TERMINATED
    currency_code VARCHAR(3) DEFAULT 'USD',
    balance NUMERIC(19,4) DEFAULT 0,                  -- Current balance (positive = credit, negative = debt)
    credit_limit NUMERIC(19,4),                       -- Maximum credit allowed
    bill_cycle_day INTEGER,                           -- Day of month (1-31)
    payment_terms INTEGER DEFAULT 30,                 -- Days until payment due
    
    -- Metadata
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    created_by VARCHAR(50),
    modified_by VARCHAR(50),
    
    CONSTRAINT fk_parent_account FOREIGN KEY (parent_account_id) 
        REFERENCES core_engine.account(id)
);

CREATE INDEX idx_account_status ON core_engine.account(status);
CREATE INDEX idx_account_bill_cycle ON core_engine.account(bill_cycle_day);
CREATE INDEX idx_account_balance ON core_engine.account(balance) WHERE balance < 0;
```

**Business Rules:**
- `balance < 0` means customer owes money
- `balance > 0` means customer has credit
- `status = SUSPENDED` when `balance < -credit_limit`

#### 2.2.2 order Table

```sql
CREATE TABLE core_oms.order (
    id VARCHAR(50) PRIMARY KEY,                       -- ORD-2024-001
    account_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50),                              -- Who created the order
    type VARCHAR(50) NOT NULL,                        -- NEW, MODIFY, CANCEL, SUSPEND, RESUME
    status VARCHAR(50) NOT NULL,                      -- CREATED, PROVISIONING, COMPLETED, FAILED
    allowed_partial_fulfillment BOOLEAN DEFAULT false,
    
    -- Dates
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    completed_date TIMESTAMP,
    
    -- Flexible attributes
    extended_data JSONB,
    
    CONSTRAINT fk_order_account FOREIGN KEY (account_id) 
        REFERENCES core_engine.account(id)
);

CREATE INDEX idx_order_account ON core_oms.order(account_id);
CREATE INDEX idx_order_status ON core_oms.order(status);
CREATE INDEX idx_order_created ON core_oms.order(created_date);
CREATE INDEX idx_order_extended_data ON core_oms.order USING GIN (extended_data);
```

**JSONB Usage:**
```json
{
  "salesforce_opportunity_id": "OPP-12345",
  "installation_notes": "Customer prefers afternoon installation",
  "special_requirements": "Need ladder for roof access"
}
```

#### 2.2.3 invoice Table

```sql
CREATE TABLE core_billing.invoice (
    id VARCHAR(50) PRIMARY KEY,                       -- INV-2024-001
    account_id VARCHAR(50) NOT NULL,
    bill_unit_id VARCHAR(50),
    
    -- Dates
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    billing_period_start DATE NOT NULL,
    billing_period_end DATE NOT NULL,
    
    -- Amounts
    subtotal NUMERIC(19,4) NOT NULL,                  -- Charges before tax
    tax_total NUMERIC(19,4) DEFAULT 0,
    total_amount NUMERIC(19,4) NOT NULL,              -- subtotal + tax_total
    amount_paid NUMERIC(19,4) DEFAULT 0,
    balance NUMERIC(19,4) NOT NULL,                   -- total_amount - amount_paid
    
    -- Status
    status VARCHAR(20) NOT NULL,                      -- PENDING, SENT, PAID, OVERDUE
    
    -- Documents
    pdf_url TEXT,                                     -- S3 URL to PDF
    html_content TEXT,                                -- For email rendering
    
    -- Mexican CFDI
    uuid VARCHAR(100),                                -- Digital stamp UUID
    stamped_date TIMESTAMP,                           -- When stamped by PAC
    
    -- Metadata
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    
    CONSTRAINT fk_invoice_account FOREIGN KEY (account_id) 
        REFERENCES core_engine.account(id)
);

CREATE INDEX idx_invoice_account ON core_billing.invoice(account_id);
CREATE INDEX idx_invoice_status ON core_billing.invoice(status);
CREATE INDEX idx_invoice_due_date ON core_billing.invoice(due_date);
CREATE INDEX idx_invoice_period ON core_billing.invoice(billing_period_start, billing_period_end);
```

#### 2.2.4 usage_record Table (Partitioned)

```sql
-- Parent table
CREATE TABLE core_usage.usage_record (
    id VARCHAR(50),
    account_id VARCHAR(50) NOT NULL,
    subscription_id VARCHAR(50),
    
    -- Source
    source_id VARCHAR(100) NOT NULL,                  -- IMSI, phone number, IP address
    usage_date DATE NOT NULL,                         -- For partitioning
    
    -- Time
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration INTEGER,                                 -- Seconds
    volume BIGINT,                                    -- Bytes
    
    -- Classification
    destination VARCHAR(100),                         -- Called number, URL, etc.
    service_type VARCHAR(50) NOT NULL,                -- VOICE_CALL, SMS, DATA, VIDEO
    call_type VARCHAR(50),                            -- LOCAL, LONG_DISTANCE, INTERNATIONAL
    
    -- Rating
    rated_amount NUMERIC(19,4) DEFAULT 0,
    rating_plan_id VARCHAR(50),
    status VARCHAR(20) NOT NULL,                      -- UNRATED, RATED, BILLED, DISPUTED
    billed BOOLEAN DEFAULT false,
    
    -- Metadata
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id, usage_date)
) PARTITION BY RANGE (usage_date);

-- Monthly partitions
CREATE TABLE core_usage.usage_record_2024_01 
PARTITION OF core_usage.usage_record
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE core_usage.usage_record_2024_02 
PARTITION OF core_usage.usage_record
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Indexes on partitions
CREATE INDEX idx_usage_2024_01_account ON core_usage.usage_record_2024_01(account_id);
CREATE INDEX idx_usage_2024_01_status ON core_usage.usage_record_2024_01(status) WHERE billed = false;
```

**Partitioning Benefits:**
- Faster queries (scan only relevant month)
- Easier archival (drop old partitions)
- Better vacuum performance

### 2.3 Database Performance Optimizations

#### 2.3.1 Indexing Strategy

```sql
-- B-tree indexes for exact matches and ranges
CREATE INDEX idx_account_id ON invoice(account_id);
CREATE INDEX idx_created_date ON order(created_date);

-- Composite indexes for common query patterns
CREATE INDEX idx_invoice_account_status ON invoice(account_id, status);
CREATE INDEX idx_usage_account_date ON usage_record(account_id, usage_date);

-- Partial indexes for filtered queries
CREATE INDEX idx_unpaid_invoices ON invoice(account_id) 
WHERE status IN ('PENDING', 'OVERDUE');

CREATE INDEX idx_unrated_usage ON usage_record(account_id) 
WHERE billed = false AND status = 'RATED';

-- GIN indexes for JSONB
CREATE INDEX idx_order_extended_data ON order USING GIN (extended_data);
```

#### 2.3.2 Query Optimization Examples

**Find Overdue Invoices:**
```sql
-- Uses: idx_invoice_account_status
SELECT * FROM core_billing.invoice
WHERE account_id = 'ACC-1001'
  AND status = 'OVERDUE'
ORDER BY due_date ASC;
```

**Find Unbilled Usage:**
```sql
-- Uses: idx_unrated_usage (partial index)
SELECT * FROM core_usage.usage_record
WHERE account_id = 'ACC-1001'
  AND billed = false
  AND status = 'RATED';
```

**Query JSONB Data:**
```sql
-- Uses: idx_order_extended_data (GIN index)
SELECT * FROM core_oms.order
WHERE extended_data @> '{"salesforce_opportunity_id": "OPP-12345"}';
```

---

## 3. Complete End-to-End Business Flows

### 3.1 New Customer Signup to First Invoice

**Timeline: Day 1 to Day 30+**

```
=== DAY 1: Customer Signs Up ===

[1] Customer submits order via web portal
    └─→ Order: Internet 100Mbps + Equipment
    
[2] Salesforce CRM creates order
    └─→ GraphQL mutation to crm_gateway.createOrder()
    
[3] crm_gateway processes order
    ├─→ Validate account (credit check, address serviceable)
    ├─→ Create order in database (status: CREATED)
    └─→ Push to OMS queue
    
[4] Provisioning orchestrator processes
    ├─→ Assign equipment (ONT-12345)
    ├─→ Assign network resources (IP, VLAN)
    ├─→ Calculate taxes
    ├─→ Call provision_gateway
    └─→ Update order (status: PROVISIONING_INITIATED)
    
[5] provision_gateway calls Nokia
    ├─→ Configure ONT
    ├─→ Assign VLAN 100
    ├─→ Set speed limit 100Mbps
    └─→ Return provisioning request ID
    
=== DAY 2: Provisioning Complete ===

[6] Nokia sends callback
    └─→ Message to MCM_BILLING_OMS_RESPONSE queue
    
[7] ProvisioningResponseProcessor
    ├─→ Update order (status: PROVISIONED)
    ├─→ Update service line (provisioningId: NW-12345)
    └─→ Trigger billing
    
[8] Billing creation
    ├─→ Create subscription record
    │   - accountId: ACC-1001
    │   - priceOfferId: INTERNET-100M
    │   - monthlyCharge: 599.00
    │   - startDate: 2024-01-16 (mid-month)
    │   - nextBillingDate: 2024-02-01
    │   - status: ACTIVE
    ├─→ Calculate proration
    │   - Days active in January: 16
    │   - Prorated amount: (599 / 31) * 16 = 309.03
    ├─→ Create charge record
    │   - description: "Internet 100M (Jan 16-31)"
    │   - amount: 309.03
    │   - chargeType: RECURRING
    │   - status: BILLED
    └─→ Update service status to ACTIVE
    
[9] Invoice generation (immediate for new customers)
    ├─→ Create invoice
    │   - invoiceId: INV-2024-001
    │   - billingPeriodStart: 2024-01-16
    │   - billingPeriodEnd: 2024-01-31
    │   - subtotal: 309.03
    ├─→ Calculate taxes
    │   - Call tax-gateway
    │   - IVA 16%: 49.44
    │   - totalAmount: 358.47
    ├─→ Generate PDF
    │   - Apply template
    │   - Upload to S3
    │   - pdfUrl: s3://urbanos-invoices/.../INV-2024-001.pdf
    └─→ Update invoice (status: SENT)
    
[10] Customer notification
    ├─→ Email: "Welcome! Your service is active"
    ├─→ Invoice attached
    └─→ Due date: 2024-02-15 (30 days)
    
=== DAY 10: Customer Makes Payment ===

[11] Customer pays online (Stripe)
    └─→ GraphQL mutation: processPayment()
    
[12] service-payment processes
    ├─→ Call payment-gateway
    ├─→ Stripe charges card: $358.47
    ├─→ Create payment record
    │   - paymentId: PAY-2024-001
    │   - amount: 358.47
    │   - externalTransactionId: ch_stripe_789
    │   - status: COMPLETED
    ├─→ Allocate to invoice INV-2024-001
    │   - invoice.amountPaid: 358.47
    │   - invoice.balance: 0.00
    │   - invoice.status: PAID
    └─→ Update account balance
        - account.balance: 0.00 (was -358.47)
    
[13] Payment confirmation
    └─→ Email: "Payment received - Thank you!"
    
=== FEBRUARY 1: First Full Month Billing ===

[14] Batch process runs at 2 AM
    └─→ Find accounts with bill_cycle_day = 1
    
[15] Billing cycle for ACC-1001
    ├─→ Find active subscriptions
    │   - Internet 100M subscription
    ├─→ Generate recurring charge
    │   - description: "Internet 100M (Feb 1-28)"
    │   - amount: 599.00 (full month, no proration)
    │   - chargeType: RECURRING
    ├─→ Aggregate usage charges (if any)
    │   - None for fixed internet
    └─→ Calculate taxes
        - IVA 16%: 95.84
        - totalAmount: 694.84
        
[16] Invoice generation
    ├─→ Create invoice INV-2024-002
    ├─→ Generate PDF
    └─→ Update invoice (status: SENT)
    
[17] Customer notification
    ├─→ Email: "Your February invoice"
    └─→ Due date: 2024-03-02
```

### 3.2 Mobile Customer Usage Flow

**Timeline: Throughout the month**

```
=== USAGE GENERATION ===

[1] Customer makes phone calls throughout day
    ├─→ Call 1: 10 minutes to local number
    ├─→ Call 2: 5 minutes to local number
    └─→ Call 3: 20 minutes to long distance
    
[2] Mobile network generates CDRs
    └─→ CDR file created: mcm_voice_20240115.csv
    
=== HOURLY: CDR PROCESSING ===

[3] Network places file on SFTP
    └─→ /cdr/outbound/mcm_voice_20240115.csv
    
[4] service-mediation Camel route
    ├─→ from("sftp://cdr-server/outbound")
    └─→ to("activemq://MEDIATION")
    
[5] MediationProcessor
    ├─→ Download file
    ├─→ Parse CSV (1000 CDRs)
    └─→ Process each CDR:
    
[6] For each CDR:
    ├─→ Normalize data
    │   Raw: calling_number=5215551234567, duration=600
    │   Canonical: sourceId=5215551234567, duration=600
    ├─→ Identify account
    │   - Lookup by phone number → ACC-1001
    │   - Lookup subscription → SUB-123
    ├─→ Enrich
    │   - Classify: LOCAL call
    │   - Add metadata
    ├─→ Deduplicate
    │   - Check unique CDR ID
    │   - Skip if already processed
    └─→ Insert into usage_record
        - status: UNRATED
        
[7] Trigger rating
    └─→ Push batch to USAGE queue
    
=== HOURLY: USAGE RATING ===

[8] service-usage processes USAGE queue
    
[9] For each usage record:
    ├─→ Get customer's price offer
    │   - PLAN: Mobile Unlimited Voice
    │   - Included: 1000 minutes/month
    │   - Overage: $0.10/minute
    ├─→ Check usage accumulator
    │   - Usage so far this month: 450 minutes
    │   - This call: 10 minutes
    │   - New total: 460 minutes
    ├─→ Rate the call
    │   - 460 < 1000 (within quota)
    │   - Rated amount: $0.00
    ├─→ Update usage record
    │   - ratedAmount: 0.00
    │   - status: RATED
    └─→ Update accumulator
        - monthly_voice_minutes: 460
        
[10] Check quota threshold
    └─→ If > 80% of quota: Send notification
    
=== MONTH END: BILLING ===

[11] Billing cycle execution
    └─→ Aggregate usage charges
        SELECT SUM(rated_amount) 
        FROM usage_record 
        WHERE account_id = 'ACC-1001'
          AND usage_date BETWEEN '2024-01-01' AND '2024-01-31'
          AND billed = false
        Result: $5.00 (50 minutes overage * $0.10)
        
[12] Create invoice
    ├─→ Recurring charge: $50.00 (plan)
    ├─→ Usage charge: $5.00 (overage)
    ├─→ Subtotal: $55.00
    ├─→ Tax (16%): $8.80
    └─→ Total: $63.80
    
[13] Mark usage as billed
    └─→ UPDATE usage_record SET billed = true
```

### 3.3 Service Suspension and Auto-Resume Flow (EP-5480)

**Timeline: Payment overdue to service restoration**

```
=== INVOICE BECOMES OVERDUE ===

[1] Invoice INV-2024-003 due date: March 15
    └─→ Customer doesn't pay by due date
    
[2] Batch job runs daily (checks overdue invoices)
    ├─→ Find invoices where due_date < today AND status != PAID
    └─→ Update invoice (status: OVERDUE)
    
[3] Collections process
    ├─→ Send overdue notice
    └─→ If overdue > 15 days: Suspend service
    
[4] Auto-suspend order generation
    ├─→ Create SUSPEND order
    │   - type: SUSPEND
    │   - reason: CREDIT_LIMIT_EXCEEDED
    │   - services: [{lines: [{ action: SUSPEND }]}]
    └─→ Push to OMS queue
    
[5] Suspension orchestrator
    ├─→ Validate suspension request
    ├─→ Call provision_gateway
    └─→ provision_gateway calls network
        - Nokia API: suspendService(ACC-1001)
        - Service deactivated
        
[6] Customer notification
    └─→ Email: "Service suspended due to non-payment"
    
=== CUSTOMER MAKES PAYMENT ===

[7] Customer pays via bank transfer
    └─→ Bank generates payment file
    
[8] Payment file processing (next day)
    ├─→ Bank uploads: payments_20240330.csv
    ├─→ CRON job downloads file
    └─→ service-payment processes
    
[9] For payment record:
    ├─→ Reference: ACC-1001
    ├─→ Amount: $63.80
    ├─→ Find account: ACC-1001
    └─→ Find overdue invoices
    
[10] Payment allocation
    ├─→ Allocate $63.80 to INV-2024-003
    ├─→ invoice.amountPaid: 63.80
    ├─→ invoice.balance: 0.00
    ├─→ invoice.status: PAID
    └─→ account.balance: 0.00 (was -63.80)
    
[11] Auto-resume logic (EP-5480)
    ├─→ Check if account was suspended
    │   - Query: Find SUSPEND order for ACC-1001
    │   - suspendOrder.reason == CREDIT_LIMIT_EXCEEDED
    ├─→ Check if balance restored
    │   - account.balance >= 0: YES
    └─→ Generate RESUME order
        - type: RESUME
        - reason: PAYMENT_RECEIVED
        - services: [{lines: [{ action: RESUME }]}]
        
[12] Resume orchestrator
    ├─→ Validate resume request
    ├─→ Call provision_gateway
    └─→ provision_gateway calls network
        - Nokia API: resumeService(ACC-1001)
        - Service reactivated
        
[13] Customer notification
    ├─→ Email: "Service restored - Thank you for your payment"
    └─→ SMS: "Your service is now active"
```

---

## 4. Development Environment Setup

### 4.1 Prerequisites

**Required Software:**
```bash
# Java 8
java -version
# Output: java version "1.8.0_xxx"

# Maven 3.6+
mvn -version

# Docker
docker --version

# Git
git --version

# IDE (IntelliJ IDEA recommended)
# - Groovy plugin
# - GraphQL plugin
```

### 4.2 Infrastructure Setup

**Start All Infrastructure:**
```bash
# PostgreSQL
docker run -d \
    --name postgres10 \
    -p 5432:5432 \
    -e POSTGRES_USER=omsadmin \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=omsdevdb \
    postgres:10.5

# ActiveMQ
docker run -d \
    --name activemq \
    -e 'ACTIVEMQ_CONFIG_MINMEMORY=512' \
    -e 'ACTIVEMQ_CONFIG_MAXMEMORY=2048' \
    -p 8161:8161 \
    -p 61616:61616 \
    webcenter/activemq:5.14.3

# Redis
docker run -d \
    --name redis \
    -p 6379:6379 \
    redis:6.2

# HashiCorp Vault (dev mode)
docker run -d \
    --name vault \
    --cap-add=IPC_LOCK \
    -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' \
    -p 8200:8200 \
    vault

# Verify all running
docker ps
```

### 4.3 Vault Configuration

**Create Secrets:**
```bash
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=myroot

# Create secrets for crm_gateway
vault kv put secret/ctg-oms/dev \
    spring.datasource.url="jdbc:postgresql://localhost:5432/omsdevdb?stringtype=unspecified" \
    spring.datasource.username="omsadmin" \
    spring.datasource.password="password" \
    spring.activemq.broker-url="tcp://localhost:61616" \
    spring.activemq.user="admin" \
    spring.activemq.password="admin" \
    application.jwt.key="ctg-jwt-key" \
    application.oauth.clientId="congero" \
    application.oauth.secret="ctg-secret" \
    application.tenant="default-tenant"
```

### 4.4 Database Setup

**Run Migrations:**
```bash
cd engine

# Set environment variables
export DB_URL=jdbc:postgresql://localhost:5432/omsdevdb
export DB_USER=omsadmin
export DB_PASSWORD=password

# Run Flyway migrations
mvn flyway:migrate -Dspring.profiles.active=dev

# Verify
mvn flyway:info

# Output:
# +-----------+---------+---------------------+----------+
# | Version   | State   | Description         | Installed On |
# +-----------+---------+---------------------+----------+
# | 1         | Success | Create Schema       | 2024-01-15 |
# | 2         | Success | Create Enum Types   | 2024-01-15 |
# | 3         | Success | Create Config Tables| 2024-01-15 |
# ...
```

### 4.5 Build and Run

**Build Sequence (dependencies first):**
```bash
# 1. Build common
cd common
mvn clean install -DskipTests

# 2. Build engine
cd ../engine
mvn clean install -DskipTests

# 3. Build oms-component
cd ../oms-component
mvn clean install -DskipTests

# 4. Build gateway-common
cd ../gateway-common
mvn clean install -DskipTests

# 5. Build jobs-common
cd ../jobs-common
mvn clean install -DskipTests
```

**Run Services:**
```bash
# Run crm_gateway
cd crm_gateway
export VAULT_URI=http://localhost:8200
export VAULT_TOKEN=myroot
mvn spring-boot:run -Dspring.profiles.active=dev

# Application starts on http://localhost:8080
# GraphQL playground: http://localhost:8080/graphiql
```

### 4.6 Verify Setup

**Test Database Connection:**
```bash
docker exec -it postgres10 psql -U omsadmin -d omsdevdb

# Check tables
\dt core_engine.*
\dt core_oms.*
\dt core_billing.*

# Query test data
SELECT * FROM core_config.tenant;
```

**Test ActiveMQ:**
```
Open browser: http://localhost:8161
Login: admin/admin
Check Queues: Should see "OMS" queue (may be empty)
```

**Test GraphQL:**
```bash
curl -X POST http://localhost:8080/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'

# Should return: {"data":{"__schema":{"queryType":{"name":"Query"}}}}
```

---

**Summary of Part 3:**

You've learned:
1. ✅ Core services and their responsibilities
2. ✅ Database architecture and schema design
3. ✅ Complete end-to-end business flows
4. ✅ How to set up local development environment
5. ✅ Build sequence and dependencies

**All 3 Parts Complete!**

You now have a comprehensive understanding of:
- **Part 1**: Business purpose, architecture, multi-tenancy
- **Part 2**: Foundation libraries, gateways, technical deep dive
- **Part 3**: Core services, database, business flows, development

**Next Steps:**
1. Set up your local environment following Part 3
2. Explore the codebase using the structure from Parts 1-2
3. Try running a simple GraphQL query
4. Build a small feature or fix a bug
5. Write tests following the patterns described

**Welcome to Embrix O2X! 🚀**

