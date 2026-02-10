# Embrix O2X - Business Scenarios & Workflows

## Complete Guide to Real-World Use Cases and Business Operations

> **Target Audience**: Business analysts, product managers, sales engineers, implementation consultants, and new team members who need to understand what the platform actually does in production.

---

## Table of Contents

1. [Industry Context](#industry-context)
2. [Customer Self-Service Scenarios](#customer-self-service-scenarios)
3. [Order-to-Cash Complete Workflows](#order-to-cash-complete-workflows)
4. [Telecom-Specific Scenarios](#telecom-specific-scenarios)
5. [Multi-Tenant SaaS Operations](#multi-tenant-saas-operations)
6. [External System Integrations](#external-system-integrations)
7. [Advanced Business Rules](#advanced-business-rules)

---

## Industry Context

### What Embrix O2X Powers

Embrix O2X is an **enterprise-grade billing and order management platform** designed for:

- **Telecommunications Operators**: Mobile, VoIP, UCaaS, CCaaS providers
- **SaaS Companies**: B2B subscription services with complex pricing
- **Multi-Tenant Service Providers**: White-label solutions with per-tenant customization
- **Usage-Based Businesses**: Companies billing on consumption (data, voice, SMS, API calls)

### Core Value Proposition

| Challenge | Embrix O2X Solution |
|-----------|---------------------|
| Complex pricing models (tiered, volume, bundles) | Flexible pricing engine with multiple calculation types |
| Real-time usage rating | Prepaid and postpaid mediation with balance management |
| Multiple payment processors | Unified payment gateway supporting Braintree, PayPal, Apple Pay |
| Tax compliance | Integration with Avalara and built-in tax engine |
| Revenue recognition | GAAP-compliant deferred revenue and milestone-based recognition |
| Multi-currency operations | Native support with exchange rates and rounding rules |
| CRM/ERP integration | Pre-built gateways for Salesforce, QuickBooks, NetSuite, ServiceNow |

---

## Customer Self-Service Scenarios

### Scenario 1: B2B Customer Self-Registration

**Business Context**: A UCaaS provider offers three service tiers (Starter, Professional, Enterprise) with different features and pricing. Customers can sign up online with immediate service activation.

#### User Journey

1. **Discovery Phase**
   - Customer visits public site (`ui` module)
   - Views package comparison table (Starter $19/mo, Professional $49/mo, Enterprise Custom)
   - Clicks "Start Free Trial" or "Sign Up"

2. **Registration Flow** (`selfcare` module)

---

##### Step 1: Account Details

**Company Information**:
- Company name, industry, size
- Billing address (country, state, city, postal code, street)
- Primary contact (name, email, phone)

**API Call**: GraphQL `processNewAccount` with account data

---

##### Step 2: Payment Setup

**Payment Collection**:
- Credit card information collected securely
- Tokenization via Braintree Vault (PCI-compliant)
- No card data stored on Embrix servers

**Process**:
1. `BrainTreeVaultController` receives card data
2. Calls Braintree SDK
3. Returns secure payment token

**API Call**: 
- GraphQL permission: `ADD_CREDIT_CARD`
- Mutation: `manageAccount` with payment profile

---

##### Step 3: Package Selection

**Package Discovery**:
- Lists available packages via `searchPackages` query
- Shows package details:
  - Recurring price
  - Included bundles
  - Feature comparison

**Selection**:
- Customer selects **Professional package** + optional add-ons

---

##### Step 4: Service Configuration

**Bundle Selection**:

| Bundle Type | Example Selection |
|-------------|-------------------|
| Users | 100 users |
| Voice Minutes | 5,000 minutes/month |
| Features | Video conferencing enabled |

**API Calls**:
- `getBundleIdByPackageId` - Get available bundles
- `searchBundles` - Bundle details

**Configuration**:
- Service start date selection
- Billing cycle preference (e.g., 1st of month)

---

##### Step 5: Order Creation

**Backend Entities Created**:

1. **Account entity**
   - Account ID, name, status
   
2. **Order with OrderLines**
   - One OrderLine per bundle
   
3. **Subscription**
   - Linked to selected package
   - Status: PENDING
   
4. **Bill Unit**
   - Billing cycle configuration
   - First bill date
   
5. **Initial Invoice** (if applicable)
   - Prorated first month charge

**GraphQL Trigger Chain**:

```
processNewAccount mutation
  ↓
AccountService.create()
  ↓
OrderProcessService.submitMultiSubscriptionOrder()
  ↓
SubscriptionService.create()
  ↓
BillUnitService.create()
```

---

##### Step 6: Post-Registration Activities

**Automated Actions**:

1. **Welcome Email** sent to customer with:
   - Account credentials
   - Quick start guide
   - Support contact information

2. **Dashboard Redirect**:
   - Customer auto-logged into portal
   - First-time setup wizard displayed

3. **Service Provisioning**:
   - Order published to `provision_gateway`
   - ServiceNow work order created
   - Vendor systems configured

4. **Invoice Generation**:
   - First invoice created (prorated if mid-cycle)
   - Payment auto-charged if card on file
   - Billing cycle starts

---

#### Technical Flow: Complete Backend Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        REGISTRATION WORKFLOW                             │
└─────────────────────────────────────────────────────────────────────────┘

   ┌──────────────────┐
   │   Customer UI    │
   │ (selfcare/ui)    │
   └────────┬─────────┘
            │ GraphQL: processNewAccount
            │ (account data, card token, package selection)
            ▼
   ┌─────────────────────────────────────┐
   │  service-transactional              │ ◄─── GraphQL API Layer
   │  └─> AccountService.create()        │
   └──────────────┬──────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  engine → customerHub → PGAccountService                    │ ◄─── Business Logic
   │  ┌───────────────────────────────────────────────────────┐  │
   │  │  1. Creates Account entity                            │  │
   │  │     • accountId, name, address, status               │  │
   │  │  2. Creates Contact and BillingProfile               │  │
   │  │  3. Calls OrderProcessService                        │  │
   │  └───────────────────────────────────────────────────────┘  │
   └──────────────┬──────────────────────────────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  engine → customerHub → PGOrderProcessService               │
   │  ┌───────────────────────────────────────────────────────┐  │
   │  │  1. Creates Order entity                              │  │
   │  │     • orderType: NEW_SERVICE                         │  │
   │  │  2. Creates OrderLines (one per bundle)              │  │
   │  │  3. Creates OrderServices (billable services)        │  │
   │  │  4. Calls SubscriptionService.create()              │  │
   │  └───────────────────────────────────────────────────────┘  │
   └──────────────┬──────────────────────────────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  engine → customerHub → PGSubscriptionService               │
   │  ┌───────────────────────────────────────────────────────┐  │
   │  │  1. Creates Subscription entity                       │  │
   │  │     • status: PENDING, startDate, packageId          │  │
   │  │  2. Creates PriceUnits (pricing rules)               │  │
   │  │  3. Creates ServiceUnits (service details)           │  │
   │  │  4. Calls BillUnitService.create()                  │  │
   │  └───────────────────────────────────────────────────────┘  │
   └──────────────┬──────────────────────────────────────────────┘
                  │
                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │  engine → billingHub → PGBillUnitService                    │
   │  ┌───────────────────────────────────────────────────────┐  │
   │  │  1. Creates BillUnit                                  │  │
   │  │     • billingCycle, startDate, status               │  │
   │  │  2. Schedules first billing run                      │  │
   │  │  3. Publishes order to PROVISIONING queue           │  │
   │  └───────────────────────────────────────────────────────┘  │
   └──────────────┬──────────────────────────────────────────────┘
                  │ ActiveMQ: PROVISIONING queue
                  ▼
   ┌────────────────────────────────────┐
   │  crm_gateway                       │ ◄─── Order Router
   │  └─> OmsProcessor                  │
   │      └─> ProvisioningGateway       │
   │          Service.processProvisioning()│
   └──────────────┬─────────────────────┘
                  │ REST API call
                  ▼
   ┌────────────────────────────────────────────────────────────┐
   │  provision_gateway                                         │ ◄─── External Integration
   │  ┌──────────────────────────────────────────────────────┐  │
   │  │  1. Maps to vendor format (ServiceNow / Telecom)    │  │
   │  │  2. Creates service request                          │  │
   │  │  3. Provisions user accounts & DIDs                  │  │
   │  │  4. Configures trunk & endpoints                     │  │
   │  │  5. Returns provisioningId and status                │  │
   │  └──────────────────────────────────────────────────────┘  │
   └────────────────────────────────────────────────────────────┘

   Result: ✓ Account Created  ✓ Services Provisioned  ✓ Ready to Bill
```

---

### Scenario 2: Customer Pays Invoice with Stored Payment Method

**Business Context**: Monthly recurring invoice generated. Customer logs into self-care portal to pay.

#### User Journey: Step-by-Step Payment Flow

##### Step 1: Access Invoice

**Action**: Navigate to invoice dashboard

- Customer logs in to selfcare portal
- Navigates to **"Billing Data" → "View Bills"**
- **Permission check**: `VIEW_BILLS`, `VIEW_INVOICE`
- **API Call**: GraphQL query `searchBillInvoice` returns pending invoices

---

##### Step 2: Invoice Review

**Action**: Review invoice details before payment

**Invoice Information Displayed**:
- Invoice number, date, due date
- Recurring charges (subscriptions)
- Usage charges (if applicable)
- Taxes
- **Total amount due**

**API Call**: `getInvoiceById`, `searchInvoiceUnits`

---

##### Step 3: Make Payment

**Action**: Initiate payment process

1. Click **"Pay Now"** button
2. Navigate to **"Activity" → "Make Payment"**
3. Select invoice(s) to pay
4. Choose payment method:
   
   | Option | Description |
   |--------|-------------|
   | **Option A** | Use stored credit card (last 4 digits shown: •••• 1234) |
   | **Option B** | Add new credit card (requires tokenization) |

5. **API Call**: `searchPayment` to retrieve payment profiles

---

##### Step 4: Payment Processing

**Action**: Process payment securely

**If using new card**:
1. Tokenize card via Braintree Vault
2. **API**: POST to `payment-gateway/braintreevault/creditcard`
3. Receive secure payment token

**Apply payment**:
- **GraphQL mutation**: `applyPayment`
- **Parameters**:
  ```
  {
    accountId: "ACC-12345"
    amount: 26705.00
    currencyCode: "USD"
    paymentProfileId: "profile_xyz" OR cardToken: "tok_abc123"
    invoiceIds: ["INV-202602-00123"]
  }
  ```
- **Required Permission**: `APPLY_PAYMENT`

---

##### Step 5: Backend Processing Flow

**Complete Payment Processing Architecture**:

```
   ┌─────────────────────────────────────────────────────────────────┐
   │  Step 1: API Entry Point                                        │
   ├─────────────────────────────────────────────────────────────────┤
   │  service-transactional                                          │
   │  └─> applyPayment(GraphQL mutation)                            │
   └──────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  Step 2: Business Logic Layer                                   │
   ├─────────────────────────────────────────────────────────────────┤
   │  engine → arHub → PGPaymentService                              │
   │  ├─> Validates payment details                                  │
   │  ├─> Checks account status                                      │
   │  └─> Prepares canonical payment request                         │
   └──────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  Step 3: Payment Gateway                                        │
   ├─────────────────────────────────────────────────────────────────┤
   │  payment-gateway                                                │
   │  ├─> Maps canonical request to Braintree format                │
   │  ├─> Calls Braintree SDK: transaction.sale()                   │
   │  │    • amount: $26,705.00                                      │
   │  │    • paymentMethodToken: "card_xyz123"                       │
   │  │    • options: { submitForSettlement: true }                 │
   │  ├─> Receives Braintree response                                │
   │  └─> Maps to canonical response                                 │
   │       • transactionId: "brn_tx_abc123"                          │
   │       • status: "SUCCESS"                                        │
   │       • authCode: "AUTH123456"                                   │
   └──────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │  Step 4: Post-Processing                                        │
   ├─────────────────────────────────────────────────────────────────┤
   │  engine → arHub → PGPaymentService                              │
   │  ├─> Creates Payment entity                                     │
   │  │    • transactionId, amount, date                             │
   │  ├─> Creates PaymentAllocation                                  │
   │  │    • Links payment to invoice(s)                             │
   │  ├─> Updates Invoice status                                     │
   │  │    • OPEN → PARTIALLY_PAID or PAID                           │
   │  ├─> Updates Account balance                                    │
   │  │    • arBalance -= paid amount                                │
   │  ├─> If overpayment: creates credit balance                     │
   │  └─> Sends payment confirmation email                           │
   └─────────────────────────────────────────────────────────────────┘
```

---

##### Step 6: Payment Confirmation

**Customer Experience**:

1. **Success Message** displayed:
   - "Payment of $26,705.00 successfully processed"
   - Transaction ID shown
   - Updated balance displayed

2. **Receipt Generation**:
   - PDF receipt created via iText
   - Available for immediate download
   - **API**: `getObjectFileById` retrieves receipt

3. **Email Confirmation**:
   - Sent to account email address
   - Includes:
     - Payment amount and date
     - Invoice(s) paid
     - Remaining balance (if any)
     - Receipt attachment

---

### Scenario 3: Customer Views Usage and Transactions

**Business Context**: A mobile MVNO customer wants to see their data, voice, and SMS usage for the current billing cycle.

#### User Journey: Usage & Transaction Monitoring

##### Step 1: Access Usage Dashboard

**Navigation**:
- Customer logs in to selfcare portal
- Navigates to **"Billing Data" → "View Transactions"**

**Required Permission**: `VIEW_TRANSACTIONS`

---

##### Step 2: View Current Balances

**Navigation**:
- Go to **"Billing Data" → "Manage Balances"**

**Required Permission**: `VIEW_BALANCES`

**API Call**: GraphQL `getBalanceUnitByAccountId`

**Balance Dashboard Displays**:

| Balance Type | Current | Limit/Allowance | % Used |
|--------------|---------|-----------------|--------|
| **Prepaid Balance** | $25.00 USD | N/A | - |
| **Monthly Allowance** | $50.00 USD | N/A | - |
| **Data Grant** | 5.2 GB | 10 GB | 48% |
| **Voice Grant** | 450 min | 1,000 min | 55% |
| **SMS Grant** | 890 msgs | 1,000 msgs | 11% |

**Usage Accumulators (This Billing Cycle)**:

| Metric | Usage This Cycle |
|--------|------------------|
| Total Data | 4.8 GB |
| Total Voice | 550 minutes |
| International Calls | 25 minutes |

---

##### Step 3: View Transaction History
   - GraphQL: `getTransactionUnit` with filters:
     - `accountId`
     - `fromDate`, `toDate` (current billing cycle)
     - `transactionType` (e.g., USAGE, RECURRING, ONE_TIME, ADJUSTMENT)
   
   **Transaction List Shows:**
   
   | Date | Type | Description | Amount | Balance |
   |------|------|-------------|--------|---------|
   | 2026-02-08 | USAGE | Data usage (500 MB) | -$2.50 | $22.50 |
   | 2026-02-07 | USAGE | Voice call (15 min) | -$3.75 | $25.00 |
   | 2026-02-05 | ADJUSTMENT | Credit for outage | +$10.00 | $28.75 |
   | 2026-02-01 | RECURRING | Monthly subscription | -$50.00 | $18.75 |
   | 2026-01-30 | TOP_UP | Account recharge | +$68.75 | $68.75 |

4. **Detailed CDR View** (if enabled)
   - Advanced users can access raw CDR data
   - Navigates to "Reports" → "Raw CDR Data"
   - GraphQL: `getRawCdrData` with parameters:
     - `accountId`
     - `fromDate`, `toDate`
     - `serviceType` (DATA, VOICE, SMS)
   
   **CDR Details:**
   - Call date/time
   - Destination number
   - Duration
   - Rate applied
   - Amount charged
   - Jurisdiction (for telecom tax)

---

## Order-to-Cash Complete Workflows

### Workflow 1: Subscription Order Creation to Revenue Recognition

**Business Context**: Enterprise customer orders a new UCaaS subscription with annual commitment. Track the complete journey from order to revenue.

#### Phase 1: Order Initiation (CRM)

1. **Sales Opportunity** (Salesforce)
   - Sales rep creates opportunity for "Acme Corp"
   - Product: UCaaS Professional - 500 users
   - Contract: 12 months, annual billing
   - Total contract value (TCV): $294,000 ($49/user/month × 500 × 12)
   - Opportunity → Won
   - Generates Order in Salesforce

2. **Order Integration** (crm_gateway)
   - Salesforce triggers order export
   - Order message published to ActiveMQ queue: `OMS`
   - Queue format: JSON with canonical order structure
   
   ```json
   {
     "externalOrderId": "SF-0034567",
     "accountId": "ACC-001",
     "orderDate": "2026-02-10",
     "orderType": "NEW_SERVICE",
     "orderLines": [
       {
         "itemId": "UCAAS-PRO",
         "quantity": 500,
         "serviceStartDate": "2026-03-01",
         "term": 12,
         "termUnit": "MONTH",
         "billableServices": [...]
       }
     ]
   }
   ```

3. **Order Consumption** (crm_gateway → service-transactional)
   - `OmsProcessor` consumes from OMS queue
   - Maps external order to internal Order DTO
   - Validates account exists
   - Calls `OrderService.createOrder()`
   - Publishes to PROVISIONING queue

#### Phase 2: Order Processing & Provisioning

4. **Order Processing** (engine → customerHub)
   - `PGOrderProcessService.submitMultiSubscriptionOrder()`
   - Creates entities:
     - **Order**: status = PENDING_PROVISIONING
     - **OrderLines**: one per product/bundle
     - **OrderServices**: billable service configurations
     - **Subscription**: status = PENDING, startDate = 2026-03-01
     - **PriceUnits**: recurring pricing rules from price offer
     - **ServiceUnits**: service-level details
   
5. **Provisioning** (provision_gateway)
   - Consumes order from PROVISIONING queue
   - Maps to ServiceNow format
   - Creates service request in ServiceNow
   - ServiceNow assigns to fulfillment team
   - Vendor systems provisioned:
     - User accounts created
     - DIDs assigned
     - Trunk configuration
     - Endpoints activated
   - Returns provisioningId and operative status
   - Updates Order status: PROVISIONED
   - Publishes to PROVISIONING_RESPONSE queue

6. **Subscription Activation**
   - `SubscriptionService.updateStatus(ACTIVE)`
   - Service start date: 2026-03-01
   - First billing cycle established

#### Phase 3: Billing & Invoicing

7. **Billing Run** (service-billing)
   - **Trigger**: Scheduled job (e.g., monthly on day 1)
   - **Or**: Manual via service-proxy: `runBilling` mutation
   
   **Process** (`PGBillUnitService.runBilling`):
   - Fetches all active subscriptions due for billing
   - For each subscription:
     - Identifies PriceUnits to bill
     - Calculates prorated amount (if mid-cycle start)
     - Applies volume discounts (if configured)
     - Creates TransactionUnit for each charge
     - Updates BalanceUnit (if prepaid)
     - Creates AccumulatorBalance entries
   - Creates BillUnit with status = PENDING
   - Links TransactionUnits to BillUnit

8. **Tax Calculation** (tax-gateway)
   - `InvoiceTaxService.calculate()`
   - Calls tax-gateway: POST `/calculateTax`
   - Request includes:
     - Line items with amounts
     - Service addresses
     - Tax jurisdiction codes
   - tax-gateway routes to Avalara (or internal engine)
   - Returns tax amounts per line
   - Creates TransactionTaxData entities

9. **Invoice Generation** (service-invoice)
   - **Trigger**: Scheduled job or manual via service-proxy
   - **Process** (`InvoicingService.invoiceAccount`):
     - Fetches BillUnit(s) with status = PENDING
     - Groups TransactionUnits
     - Calculates totals:
       - Subtotal: $24,500 (one month of service)
       - Tax: $2,205 (9% telecom tax)
       - **Total: $26,705**
     - Creates InvoiceUnit:
       - invoiceNumber: INV-202602-00123
       - invoiceDate: 2026-02-28
       - dueDate: 2026-03-15 (NET 15)
       - status: OPEN
       - amount: $26,705
     - Generates PDF via iText library
     - Stores in document repository
     - Updates BillUnit status: BILLED

10. **Invoice Distribution**
    - Sends invoice via email (Thymeleaf template)
    - Syncs to accounting system via finance-gateway
    - GraphQL mutation: `createInvoice` to QuickBooks/NetSuite

#### Phase 4: Revenue Recognition

##### 11. Revenue Journal Creation (engine → revenueHub)

**Trigger**: BillUnit status = BILLED

**Service**: `PGBillUnitService.createRevenueJournal()`

**Process Flow**:

```
┌──────────────────────────────────────────────────────────────────┐
│  Initial Journal Entry (Day 1)                                   │
├──────────────────────────────────────────────────────────────────┤
│  • Determines revenue recognition type from Item configuration   │
│  • Type: MONTHLY_STRAIGHT_LINE_AMORTIZATION (annual contract)    │
│                                                                   │
│  Creates ReferenceRevenueJournal:                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Transaction ID:     TXN-202602-12345                      │ │
│  │  Amount:             $24,500.00                            │ │
│  │  Revenue Period:     2026-03-01 to 2027-02-28 (12 months)  │ │
│  │  Amount Recognized:  $0.00 (initially)                     │ │
│  │  GL Accounts:                                              │ │
│  │    • Revenue:         4000 (Service Revenue)               │ │
│  │    • Deferred:        2400 (Deferred Revenue)              │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Monthly Schedule Created**:

| Month | Accounting Period | Recognition Amount | Status | GL Entries |
|-------|-------------------|-------------------|--------|------------|
| Mar 2026 | 2026-03 | $2,041.67 | PENDING | Dr: 2400, Cr: 4000 |
| Apr 2026 | 2026-04 | $2,041.67 | PENDING | Dr: 2400, Cr: 4000 |
| May 2026 | 2026-05 | $2,041.67 | PENDING | Dr: 2400, Cr: 4000 |
| ... | ... | ... | PENDING | ... |
| Feb 2027 | 2027-02 | $2,041.67 | PENDING | Dr: 2400, Cr: 4000 |

**Total**: 12 months × $2,041.67 = $24,500.00

---

##### 12. Monthly Revenue Recognition (service-revenue)

**Trigger**: Monthly job on last day of month

**Service**: `RecognizeRevenueService.recognizeRevenue()`

**Process Flow**:

```
┌──────────────────────────────────────────────────────────────────┐
│  Month-End Processing                                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. Query Pending Journals                                       │
│     └─> WHERE accountingPeriod = current month                   │
│         AND status = PENDING                                     │
│                                                                   │
│  2. For Each Journal Entry:                                      │
│     ┌──────────────────────────────────────────────────────┐    │
│     │  Amount: $2,041.67                                   │    │
│     │                                                       │    │
│     │  GL Entry #1:                                        │    │
│     │  ├─ Account:  2400 (Deferred Revenue)               │    │
│     │  ├─ Debit:    $2,041.67                             │    │
│     │  └─ Memo:     "Revenue recognition - Feb 2026"      │    │
│     │                                                       │    │
│     │  GL Entry #2:                                        │    │
│     │  ├─ Account:  4000 (Service Revenue)                │    │
│     │  ├─ Credit:   $2,041.67                             │    │
│     │  └─ Memo:     "Revenue recognition - Feb 2026"      │    │
│     │                                                       │    │
│     │  Update Journal:                                     │    │
│     │  ├─ amountRecognized += $2,041.67                   │    │
│     │  ├─ status = RECOGNIZED                             │    │
│     │  └─ recognizedDate = 2026-02-28                     │    │
│     └──────────────────────────────────────────────────────┘    │
│                                                                   │
│  3. Sync to External Finance System                              │
│     └─> finance-gateway → createJournal()                        │
│         └─> QuickBooks / NetSuite                                │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Balance Sheet Impact Over Time**:

| Month | Deferred Revenue | Recognized Revenue (YTD) | Remaining |
|-------|------------------|--------------------------|-----------|
| Feb 2026 (Initial) | $24,500.00 | $0 | $24,500.00 |
| Mar 2026 | $22,458.33 | $2,041.67 | $22,458.33 |
| Jun 2026 | $16,291.67 | $8,208.33 | $16,291.67 |
| Dec 2026 | $4,083.33 | $20,416.67 | $4,083.33 |
| Feb 2027 (Final) | $0 | $24,500.00 | $0 |

#### Phase 5: Collections & Payment

13. **Payment Application** (service-payment)
    - Customer pays invoice via:
      - **Option A**: Self-care portal (covered earlier)
      - **Option B**: ACH/wire transfer (backend applied)
      - **Option C**: Auto-charge from stored payment method
    
    **Auto-Charge Flow**:
    - **Trigger**: Invoice due date approaching (e.g., 3 days before)
    - **Job**: CollectionsService.invoiceDueReminder
    - **Process**:
      - Identifies invoices due
      - Checks account has payment profile with autoCharge = true
      - Calls payment-gateway to charge card
      - If successful:
        - Creates Payment entity
        - Creates PaymentAllocation
        - Updates Invoice status: PAID
        - Updates Account arBalance
      - If failed:
        - Creates notification
        - Sends email to customer
        - Creates CollectionUnit if past due

14. **Collections Management** (if payment fails)
    - **Trigger**: Invoice past due date
    - **Process** (`CollectionsService.createCollectionUnit`):
      - Creates CollectionUnit:
        - invoiceId
        - dueDate: 2026-03-15
        - collectionDate: 2026-03-16
        - amount: $26,705
        - status: NEW
      - Assigns to collections queue
      - Sends dunning emails (days 1, 7, 14, 30)
      - If 30 days past due:
        - Suspends services
        - GraphQL: `updateSubscriptionStatus(SUSPENDED)`
      - If 60 days past due:
        - Creates write-off proposal
        - Requires management approval

---

### Workflow 2: Prepaid Mobile Top-Up and Usage Rating

**Business Context**: Prepaid mobile customer tops up account and makes calls/uses data. Real-time rating and balance deduction.

#### Phase 1: Account Top-Up

1. **Customer Initiates Top-Up**
   - Methods:
     - Self-care portal
     - USSD (*123*PIN#)
     - Mobile app
     - Retail voucher
     - Credit card online
   
2. **Payment Processing**
   - If credit card:
     - Calls payment-gateway
     - Braintree processes payment
     - Returns authorization
   - If voucher:
     - Validates voucher PIN
     - Checks voucher not already redeemed
   
3. **Balance Update** (engine → arHub)
   - `BalanceUnitService.create/update()`
   - Creates BalanceUnitBalance entity:
     - accountId
     - balanceType: CURRENCY
     - currencyCode: USD
     - amount: +$50.00 (top-up)
     - effectiveDate: now
     - expiryDate: +90 days
   - Also updates BalanceUnitGrant if purchasing data/voice packages:
     - grantType: DATA
     - quantity: +5 GB
     - expiryDate: end of month

4. **Notification**
   - SMS sent: "Your account has been recharged with $50. New balance: $75.50. Valid until 2026-05-10."

#### Phase 2: Real-Time Usage Rating (Prepaid)

**Scenario**: Customer makes 10-minute voice call to another mobile number.

##### Real-Time Rating Workflow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   REAL-TIME USAGE RATING PIPELINE                         │
└──────────────────────────────────────────────────────────────────────────┘

Step 1: Usage Event Capture
┌─────────────────────────────────────────────────────────────────┐
│  Telecom Network (Soft switch / MSC)                            │
│  ├─> Call completed: +1234567890 → +9876543210                 │
│  ├─> Duration: 600 seconds (10 minutes)                         │
│  └─> Generates CDR (Call Detail Record)                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Push to mediation platform
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│  Mediation Platform                                             │
│  └─> Publishes to ActiveMQ queue: USAGE                        │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼

Step 2: Usage Ingestion
┌─────────────────────────────────────────────────────────────────┐
│  service-mediation: MCMMediationService                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  • Consumes CDR batch from USAGE queue                   │  │
│  │  • Parses file format (CSV/XML/JSON)                     │  │
│  │  • Creates DetailRecord entity:                          │  │
│  │    ┌─────────────────────────────────────────────────┐   │  │
│  │    │  serviceType:     VOICE                         │   │  │
│  │    │  callType:        MOBILE_TO_MOBILE              │   │  │
│  │    │  originNumber:    +1234567890                   │   │  │
│  │    │  destNumber:      +9876543210                   │   │  │
│  │    │  startTime:       2026-02-10T14:32:15           │   │  │
│  │    │  duration:        600 seconds                   │   │  │
│  │    │  rawData:         [full CDR]                    │   │  │
│  │    └─────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼

Step 3: Pre-Processing Pipeline
┌─────────────────────────────────────────────────────────────────┐
│  engine → usageProcessHub → PreProcessingService                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Module Chain (configured in UsageProcessMapConfig):     │  │
│  │                                                           │  │
│  │  ┌─ Module A: Account Lookup ──────────────────────────┐ │  │
│  │  │  • Maps originNumber → accountId                    │ │  │
│  │  │  • Query: ProvisioningId mapping table              │ │  │
│  │  │  • Result: accountId = ACC-12345                    │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  ┌─ Module B: Balance Lookup ──────────────────────────┐ │  │
│  │  │  • Fetches BalanceUnit for accountId                │ │  │
│  │  │  • Currency balance: $75.50                         │ │  │
│  │  │  • Voice grant: 450 minutes remaining               │ │  │
│  │  │  • Sufficient balance: ✓ YES                        │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  ┌─ Module C: Rating Route ────────────────────────────┐ │  │
│  │  │  • UsageRecIndicator: PREPAID                       │ │  │
│  │  │  • Routes to → PrepaidRatingService                 │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  ┌─ Module D: Jurisdiction Lookup ─────────────────────┐ │  │
│  │  │  • Destination zone lookup                          │ │  │
│  │  │  • ConfigRegionMap query                            │ │  │
│  │  │  • Result: "MOBILE_ON_NET" (same carrier)           │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼

Step 4: Prepaid Rating
┌─────────────────────────────────────────────────────────────────┐
│  PrepaidRatingService.rateUsageRecord()                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Rating Calculation:                                      │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Fetch PriceOffer:                                  │  │  │
│  │  │  • Type: USAGE_TIERED                               │  │  │
│  │  │  • Zone: MOBILE_ON_NET                              │  │  │
│  │  │  • Rate: $0.10/minute                               │  │  │
│  │  │                                                      │  │  │
│  │  │  Calculate Charge:                                  │  │  │
│  │  │  • Duration: 10 minutes                             │  │  │
│  │  │  • Rate: $0.10/min                                  │  │  │
│  │  │  • CHARGE: $1.00                                    │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  Balance Deduction:                                       │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │  Option A: Deduct from Currency Balance            │  │  │
│  │  │  • Before: $75.50                                   │  │  │
│  │  │  • Deduct: $1.00                                    │  │  │
│  │  │  • After:  $74.50  ✓                                │  │  │
│  │  │                                                      │  │  │
│  │  │  Option B: Deduct from Voice Grant (if available)  │  │  │
│  │  │  • Before: 450 minutes                              │  │  │
│  │  │  • Deduct: 10 minutes                               │  │  │
│  │  │  • After:  440 minutes  ✓                           │  │  │
│  │  │  • Currency balance: unchanged                      │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

Result: ✓ Call Rated  ✓ Balance Updated  ✓ Transaction Created
```

**Balance After Rating**:

| Balance Type | Before | Charge | After | Status |
|--------------|--------|--------|-------|--------|
| Currency (USD) | $75.50 | -$1.00 | $74.50 | ✓ Sufficient |
| Voice Grant (min) | 450 | -10 | 440 | ✓ Available |
| Data Grant (GB) | 5.2 | 0 | 5.2 | Unchanged |

5. **Transaction Creation**
   - Creates TransactionUnit:
     - transactionType: USAGE
     - amount: -$1.00
     - description: "Voice call - 10 min to +1234567890"
     - transactionDate: 2026-02-10T14:32:15
     - status: RATED
   - Links to DetailRecord (CDR)
   - Updates BalanceUnit
   - Updates AccumulatorBalance (for volume discounts)

6. **Real-Time Balance Check**
   - If balance < $5.00 (low balance threshold):
     - Sends SMS: "Your balance is low: $4.50. Recharge now to avoid service interruption."
     - Creates notification in selfcare portal
   
   - If balance ≤ $0.00:
     - Suspends outbound services
     - Allows emergency calls only (E911)
     - Status update: SUSPENDED_LOW_BALANCE

7. **Usage Record Storage**
   - UsageContainer persisted to database
   - Status: PROCESSED
   - Available in selfcare for customer to view
   - CDR available for regulatory reporting

---

## Telecom-Specific Scenarios

### Scenario 4: Operator Reconciliation & Settlement

**Business Context**: MVNO (Mobile Virtual Network Operator) receives monthly invoice from MNO (host operator) for network usage. Must reconcile wholesale charges against retail billing.

#### Monthly Reconciliation Process

1. **Operator Invoice Receipt**
   - MNO sends invoice via:
     - SFTP file drop
     - API push
     - Email attachment
   - File format: CSV/Excel with usage summary

2. **Invoice Ingestion** (provision_gateway)
   - `OperatorRecordService.create()`
   - Creates OperatorInvoice entity:
     - operatorName: "Verizon Wholesale"
     - invoiceNumber: "OP-202601-0045"
     - invoiceDate: 2026-01-31
     - periodStart: 2026-01-01
     - periodEnd: 2026-01-31
     - totalAmount: $125,000
     - status: NEW

3. **Usage Reconciliation**
   - **Process**: Compare operator CDRs vs. internal CDRs
   - Query: `getRawCdrData` for date range
   - Match on:
     - Calling number
     - Called number
     - Start time
     - Duration
   
   **Reconciliation Report**:
   | Category | Operator | Internal | Variance | Notes |
   |----------|----------|----------|----------|-------|
   | Voice minutes | 1,245,890 | 1,247,123 | +1,233 | 0.1% over |
   | Data GB | 54,321 | 54,319 | -2 | 0.003% under |
   | SMS count | 456,789 | 456,789 | 0 | Match |
   | **Total amount** | **$125,000** | **$125,456** | **+$456** | 0.36% over |

4. **Dispute Management** (if variance > threshold)
   - Creates OperatorDispute:
     - operatorInvoiceId
     - disputeType: USAGE_VARIANCE
     - amount: $456
     - reason: "CDR count mismatch for voice"
     - status: OPEN
   - Generates dispute report with CDR details
   - Exported for operator review

5. **Settlement**
   - If dispute resolved:
     - Updates OperatorInvoice amount (if adjusted)
   - Creates Payment:
     - paymentType: OPERATOR_SETTLEMENT
     - amount: $124,544 (after adjustment)
     - paymentDate: 2026-02-15
   - Syncs to finance system as COGS (Cost of Goods Sold)
   - GL Entry:
     - Debit: COGS - Wholesale Network (5100): $124,544
     - Credit: Cash/AP (2000): $124,544

6. **Margin Analysis**
   - **Revenue** (from retail customers): $287,650
   - **COGS** (wholesale network): $124,544
   - **Gross Profit**: $163,106
   - **Gross Margin**: 56.7%
   
   Report includes:
   - Revenue by service type (voice, data, SMS)
   - COGS by service type
   - Margin by customer segment
   - Identifies unprofitable customers/services

---

### Scenario 5: Number Porting & Provisioning

**Business Context**: Customer requests to port their existing phone number from another carrier to the new service.

#### Port-In Workflow

1. **Port Request Initiation**
   - Customer initiates in selfcare or via sales agent
   - Provides:
     - Current phone number
     - Current carrier
     - Account number with current carrier
     - PIN/password for authorization

2. **Port Request Validation**
   - System checks:
     - Number is valid and portable
     - Not in recent port history
     - Account in good standing
   - Creates Order:
     - orderType: NUMBER_PORT_IN
     - orderServices includes:
       - serviceType: DID
       - provisioningId: [phone number]
       - portDetails: { carrier, accountNumber, pin }

3. **Provisioning Flow** (provision_gateway)
   - Order published to PROVISIONING queue
   - `ProvisionGatewayService.processProvisioning()`
   - Calls carrier port-in API (or submits LSR - Local Service Request)
   - Creates work order in ServiceNow:
     - workOrderType: PORT_IN
     - expectedCompletionDate: +3 business days
     - status: PENDING_CARRIER

4. **Carrier Processing** (External)
   - Current carrier receives port request
   - Validates customer authorization
   - Returns:
     - **Approved**: Port will complete on [date]
     - **Rejected**: Invalid account/PIN
   
5. **Port Completion**
   - On port date:
     - Current carrier releases number
     - New carrier activates number
   - Vendor system notifies via webhook
   - Updates Order status: PROVISIONED
   - Updates ServiceUnit:
     - provisioningId: [phone number]
     - provisioningStatus: ACTIVE
     - activationDate: [port completion date]

6. **Service Activation**
   - Number now routes to new platform
   - Customer can make/receive calls
   - Billing begins (prorated from activation date)
   - Old carrier sends final invoice

---

## Multi-Tenant SaaS Operations

### Scenario 6: New Tenant Onboarding

**Business Context**: Embrix O2X platform is sold as white-label solution. New partner company wants their own branded self-care portal.

#### Tenant Onboarding Process

1. **Tenant Configuration Creation** (ui-core → Ops Hub)
   - Admin user accesses "Tenant Onboarding" module
   - Creates new tenant record:
     - tenantName: "Acme Communications"
     - tenantCode: "acme-com"
     - domain: "selfcare.acme-communications.com"
     - logoUrl: "https://cdn.acme.com/logo.png"
     - themeColors: { primary: "#0066CC", secondary: "#FF6600" }
     - supportEmail: "support@acme-communications.com"
     - supportPhone: "+1-800-555-0100"

2. **Database Tenant Setup** (engine → opsHub)
   - Creates tenant schema (if silo model):
     - Schema name: `acme_com`
     - Copies table structure from template
     - Applies Flyway migrations
   - Or configures tenant_id column filtering (if shared schema)

3. **Self-Care Configuration** (`TenantSelfCareConfig`)
   - Enables/disables features per tenant:
     - enableSelfRegistration: true
     - enableCreditCardPayment: true
     - enableUsageReports: false (enterprise only)
     - enableVoiceCDR: false
   - Sets permission defaults for new users
   - Configures package visibility

4. **Integration Setup**
   - CRM Gateway:
     - Salesforce credentials for tenant's SFDC org
     - Maps tenant→SF org mapping
   - Payment Gateway:
     - Braintree merchant account credentials
     - Tenant gets their own merchant account
   - Tax Gateway:
     - Avalara account credentials
     - Tax jurisdiction setup
   - Finance Gateway:
     - QuickBooks/NetSuite credentials
     - Chart of accounts mapping

5. **Credential Storage** (Vault)
   - Creates Vault path: `/secret/embrix/tenant/acme-com/`
   - Stores:
     - `vendorCredentials/SFDC`
     - `vendorCredentials/BRAINTREE`
     - `vendorCredentials/AVALARA`
     - `vendorCredentials/QUICKBOOKS`
   - Each credential includes:
     - API keys/tokens
     - Endpoints
     - Org/merchant IDs

6. **URL/DNS Configuration**
   - Creates subdomain: `selfcare.acme-communications.com`
   - Points to Embrix O2X load balancer
   - SSL certificate provisioned (Let's Encrypt or custom)
   - Nginx/ALB routes by hostname → tenant resolution

7. **Initial Data Population**
   - **Pricing**: Imports tenant's product catalog
   - **Users**: Creates admin user for tenant
   - **Reports**: Configures report templates
   - **Notifications**: Sets up email templates with tenant branding

8. **Testing & Validation**
   - QA performs smoke tests:
     - User registration flow
     - Payment processing
     - Invoice generation
     - External integrations
   - Tenant admin reviews and approves

9. **Go-Live**
   - Tenant status: ACTIVE
   - Users can access portal
   - Billing begins
   - Support team notified

---

### Scenario 7: Tenant-Specific Customization

**Business Context**: Tenant "Acme Communications" needs custom business logic for their vertical (e.g., healthcare compliance, non-standard billing rules).

#### Customization Types

1. **Custom Attributes**
   - Account level:
     - `hipaaCompliant` (boolean)
     - `emrSystem` (string) - which EMR they integrate with
     - `npiNumber` (string) - National Provider Identifier
   - Stored in `custom_attributes` JSONB column
   - Accessible in pricing/billing rules

2. **Custom Pricing Rules**
   - Volume discount tiers specific to Acme:
     - 0-1,000 users: $49/user
     - 1,001-5,000 users: $45/user
     - 5,001+ users: $40/user
   - Configured in PriceOffer with tenant-specific tiers

3. **Custom Reports**
   - HIPAA audit log export
   - Compliance reporting
   - Custom CDR format for EMR integration
   - GraphQL: Custom queries registered in tenant config

4. **Custom Workflows**
   - Order approval workflow (for healthcare orgs):
     - Orders > $10,000 require manager approval
     - Implemented via `ConfigOrderApproval` with tenant filter
   - Auto-suspension rules:
     - Different grace periods per customer type
     - Configured in `CollectionsConfig`

---

## External System Integrations

### Scenario 8: Salesforce → Embrix → ServiceNow End-to-End

**Business Context**: Complete order lifecycle across three systems.

#### Integration Flow

1. **Salesforce (CRM)**
   - Sales rep creates Opportunity
   - Adds products to quote
   - Quote → Order
   - Order status: WAITING_PROVISIONING
   - Triggers Process Builder / Flow
   - Publishes to OMS queue via CRM Gateway webhook

2. **CRM Gateway**
   - Receives webhook from Salesforce
   - Authenticates via OAuth2 (Salesforce → Vault)
   - Maps SF Order → Canonical Order DTO
   - Publishes to ActiveMQ: `OMS` queue
   - Returns acknowledgment to Salesforce

3. **Embrix O2X (OMS/Billing)**
   - `OmsProcessor` consumes from queue
   - Creates Order, Subscription, BillUnit
   - Runs billing (if charges due immediately)
   - Publishes to `PROVISIONING` queue
   - Updates SF Order via CRM Gateway:
     - embrixOrderId
     - status: PENDING_PROVISIONING

4. **Provision Gateway**
   - Consumes from PROVISIONING queue
   - Maps to ServiceNow format:
     - Creates Work Order in ServiceNow
     - workOrderType: NEW_SERVICE
     - assignedGroup: Network Ops
   - ServiceNow assigns to technician

5. **ServiceNow (ITSM/Fulfillment)**
   - Technician completes work order:
     - Provisions equipment
     - Activates service
     - Tests connectivity
   - Updates work order status: COMPLETED
   - Triggers webhook to Provision Gateway

6. **Provision Gateway (Callback)**
   - Receives ServiceNow webhook
   - Maps ServiceNow response → Canonical
   - Updates Order status: PROVISIONED
   - Publishes to `PROVISIONING_RESPONSE` queue

7. **Embrix O2X (Completion)**
   - Consumes from PROVISIONING_RESPONSE
   - Updates Order status: COMPLETED
   - Activates Subscription
   - Notifies customer (email/SMS)
   - Updates SF Order via CRM Gateway:
     - status: ACTIVATED
     - activationDate
     - provisioningId

8. **Salesforce (Status Update)**
   - Order status: ACTIVATED
   - Triggers Success Playbook:
     - Schedules onboarding call
     - Sends welcome kit
     - Creates support case record

---

### Scenario 9: QuickBooks Revenue Sync

**Business Context**: Monthly revenue recognition entries need to sync to QuickBooks for financial reporting.

#### Monthly Sync Process

1. **Revenue Recognition** (Embrix O2X)
   - Month-end job runs: `recognizeRevenue`
   - Processes all pending revenue journals for the month
   - Creates GL entries in internal ledger

2. **Journal Entry Batch Creation**
   - Groups revenue journals by:
     - GL account
     - Department/cost center
     - Customer (if needed)
   - Creates batch:
     - Batch date: Last day of month
     - Description: "February 2026 Revenue Recognition"
     - Entries: 1,234 line items

3. **Finance Gateway Call**
   - GraphQL: `createJournal` mutation
   - Parameters:
     - journalEntries: [{ account, debit, credit, memo }]
     - batchId
   - Finance Gateway receives request

4. **QuickBooks Mapping** (finance-gateway)
   - Maps Embrix GL accounts → QuickBooks accounts:
     - 4000 (Revenue) → "4000 - Service Revenue"
     - 2400 (Deferred) → "2400 - Deferred Revenue"
   - Uses `ConfigChartOfAccount` mapping table
   - Formats as QuickBooks Journal Entry:

   ```json
   {
     "TxnDate": "2026-02-28",
     "Line": [
       {
         "DetailType": "JournalEntryLineDetail",
         "Amount": 125000.00,
         "JournalEntryLineDetail": {
           "PostingType": "Debit",
           "AccountRef": { "value": "82" } // Deferred Revenue
         }
       },
       {
         "DetailType": "JournalEntryLineDetail",
         "Amount": 125000.00,
         "JournalEntryLineDetail": {
           "PostingType": "Credit",
           "AccountRef": { "value": "79" } // Service Revenue
         }
       }
     ]
   }
   ```

5. **QuickBooks API Call**
   - finance-gateway calls QuickBooks API:
     - Endpoint: POST `/v3/company/{realmId}/journalentry`
     - Auth: OAuth2 token from Vault
   - QuickBooks validates and creates entry
   - Returns: JournalEntry ID

6. **Sync Confirmation**
   - finance-gateway updates RevenueJournal:
     - externalId: QuickBooks JournalEntry ID
     - syncStatus: SYNCED
     - syncDate: 2026-02-28T23:45:12Z
   - If error:
     - syncStatus: FAILED
     - errorMessage: stored for retry
     - Notification sent to accounting team

7. **Reconciliation Report**
   - Compares Embrix GL → QuickBooks:
     - Revenue by account
     - Deferred revenue balance
     - Month-over-month variance
   - Report generated and emailed to CFO

---

## Advanced Business Rules

### Scenario 10: Complex Volume Discount with Tiered Pricing

**Business Context**: Enterprise customer has negotiated custom pricing: tiered rates with volume discounts that apply retroactively.

#### Pricing Structure

**Base Pricing (per user/month)**:
- Tier 1 (0-100 users): $50/user
- Tier 2 (101-500 users): $45/user
- Tier 3 (501-2,000 users): $40/user
- Tier 4 (2,001+ users): $35/user

**Volume Discount** (applied retroactively to ALL users):
- < 500 users: 0% discount
- 500-1,999 users: 5% discount
- 2,000-4,999 users: 10% discount
- 5,000+ users: 15% discount

**Customer has 1,800 users.**

#### Billing Calculation

1. **Tiered Rate Calculation** (`PGBillUnitService`)
   - `applyMCMTieredComplexVolumeDiscountForData()`
   
   **Step 1: Calculate by tiers**:
   - Tier 1: 100 users × $50 = $5,000
   - Tier 2: 400 users × $45 = $18,000
   - Tier 3: 1,300 users × $40 = $52,000
   - **Subtotal: $75,000**

2. **Volume Discount Application** (`applyVolumeDiscount`)
   - Total users: 1,800
   - Volume discount tier: 500-1,999 → 5%
   - Discount amount: $75,000 × 5% = $3,750
   - **Total after discount: $71,250**

3. **Transaction Creation**
   - Recurring charge transaction:
     - amount: $71,250
     - description: "UCaaS Service - 1,800 users"
     - pricingDetail: JSON with tier breakdown
   - Volume discount transaction:
     - amount: -$3,750
     - description: "Volume discount - 5%"
     - discountType: VOLUME_RETROACTIVE

4. **Invoice Display**
   
   ```
   INVOICE INV-202602-00789
   
   Services:
   - UCaaS Professional (0-100 users @ $50)     $5,000
   - UCaaS Professional (101-500 users @ $45)   $18,000
   - UCaaS Professional (501-1,800 users @ $40) $52,000
   
   Subtotal:                                     $75,000
   Volume Discount (5% - 1,800 users):           ($3,750)
   
   Subtotal after discount:                      $71,250
   Tax (9%):                                     $6,412.50
   
   TOTAL DUE:                                    $77,662.50
   ```

---

### Scenario 11: Proration for Mid-Cycle Changes

**Business Context**: Customer adds 50 users on day 15 of a 30-day billing cycle. Need to prorate the charges.

#### Proration Calculation

1. **Change Order Processing**
   - Order type: ADD_SEATS
   - Original subscription: 500 users
   - New subscription: 550 users
   - Change date: 2026-02-15 (day 15 of 30-day cycle)

2. **Proration Logic** (`PGBillUnitService.alignedToCycleBilling`)
   - Days remaining in cycle: 30 - 15 + 1 = 16 days
   - Proration factor: 16 / 30 = 0.533
   
   **Calculation**:
   - Monthly rate per user: $45
   - New users: 50
   - Full month charge: 50 × $45 = $2,250
   - **Prorated charge: $2,250 × 0.533 = $1,199.25**

3. **Immediate Billing** (`runPendingBill`)
   - Creates pending bill immediately
   - TransactionUnit:
     - amount: $1,199.25
     - description: "Prorated charge - 50 users added (Feb 15-28)"
     - prorationFactor: 0.533
     - billingPeriod: 2026-02-15 to 2026-02-28
   - Invoiced immediately
   - Next regular bill will include full month for 550 users

---

### Scenario 12: Revenue Recognition for Annual Contracts

**Business Context**: Customer pays $120,000 upfront for 12-month contract. Revenue must be recognized monthly per GAAP.

#### Revenue Recognition Flow

1. **Payment Received**
   - Payment: $120,000 on 2026-01-15
   - Service period: 2026-01-15 to 2027-01-14

2. **Initial Journal Entry** (Day 1)
   - **Dr**: Cash (1000) - $120,000
   - **Cr**: Deferred Revenue (2400) - $120,000

3. **Monthly Recognition Schedule** (`RevenueRecognitionType: MONTHLY_STRAIGHT_LINE_AMORTIZATION`)
   - Creates 12 RevenueJournal entries:
   
   | Month | Accounting Period | Amount | GL Entries |
   |-------|-------------------|--------|------------|
   | Jan 2026 | 2026-01 | $10,000 | Dr: Deferred Revenue (2400) $10,000<br>Cr: Revenue (4000) $10,000 |
   | Feb 2026 | 2026-02 | $10,000 | Same |
   | ... | ... | ... | ... |
   | Jan 2027 | 2027-01 | $10,000 | Same |

4. **Month-End Processing**
   - Job runs on last day of month
   - `RecognizeRevenueService.recognizeRevenue()`
   - Queries journals for current month
   - Creates GL entries
   - Syncs to QuickBooks via finance-gateway
   - Updates RevenueJournal.amountRecognized
   - Status: RECOGNIZED

5. **Balance Sheet Impact**
   - Month 1 (Jan 2026):
     - Cash: $120,000
     - Deferred Revenue: $110,000 (after $10,000 recognized)
   - Month 6 (Jun 2026):
     - Cash: $120,000
     - Deferred Revenue: $60,000 (after $60,000 recognized)
   - Month 12 (Jan 2027):
     - Cash: $120,000 (may be spent on ops)
     - Deferred Revenue: $0 (all recognized)

6. **Early Termination Handling**
   - If customer cancels in month 8:
     - Recognized revenue: $80,000 (8 months)
     - Remaining deferred: $40,000
   - Options:
     - **Refund**: Return $40,000, reverse deferred revenue
     - **Accelerate**: Recognize all $40,000 immediately (revenue hit)
     - **Forfeit**: Keep as termination fee (contract dependent)

---

## Summary & Key Takeaways

### Business Capabilities Demonstrated

1. **Self-Service Operations**: Complete customer portal with registration, billing, payments, usage tracking
2. **Complex Pricing**: Tiered, volume, bundle-based, proration, discounts
3. **Real-Time Rating**: Prepaid/postpaid usage processing with balance management
4. **Multi-Tenant**: Per-tenant configuration, branding, integrations, data isolation
5. **Order Orchestration**: CRM → OMS → Provisioning → Billing → Payment
6. **Revenue Compliance**: GAAP-compliant recognition, deferred revenue, milestones
7. **External Integrations**: Pre-built connectors for major CRM, ERP, payment, tax systems
8. **Telecom-Specific**: CDR mediation, operator settlement, number porting, regulatory reporting

### Typical Customer Profile

| Industry | Use Cases | Key Features Used |
|----------|-----------|-------------------|
| **UCaaS/CCaaS Provider** | B2B subscriptions, usage-based add-ons | Tiered pricing, self-care, Salesforce integration, QuickBooks sync |
| **MVNO (Mobile Operator)** | Prepaid/postpaid mobile, data plans | Real-time rating, CDR mediation, operator reconciliation, tax compliance |
| **SaaS Provider** | B2B software subscriptions | Multi-tenant, revenue recognition, payment gateway, dunning |
| **Wholesale Carrier** | Carrier-to-carrier services | Operator billing, usage reconciliation, bulk invoice processing |
| **IoT Platform** | Device connectivity, API usage | Usage rating, micro-transactions, volume discounts, GraphQL API |

### Deployment Patterns

1. **Single-Tenant (Silo)**: Enterprise customer, dedicated instance, full customization
2. **Multi-Tenant (Shared)**: SaaS provider, thousands of tenants, per-tenant configuration
3. **Hybrid**: Large tenants get dedicated, small tenants share infrastructure

---

## Next Steps

- **For Implementation Teams**: Use these scenarios as test cases during onboarding
- **For Sales/Presales**: Customize scenarios to match prospect's business model
- **For Developers**: Reference these workflows when debugging cross-module issues
- **For Product Managers**: Identify gaps or enhancement opportunities

For technical details on any scenario, see:
- [Architecture Guide](NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md)
- [Technical Deep Dive](NEWCOMER_GUIDE_PART2_TECHNICAL_DEEP_DIVE.md)
- [Services & Development](NEWCOMER_GUIDE_PART3_SERVICES_AND_DEVELOPMENT.md)
- [Multi-Tenant Guide](docs/MULTI_TENANT_COMPLETE_GUIDE.md)
