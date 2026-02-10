# Embrix O2X Platform - Newcomer's Guide (Part 2)
## Technical Deep Dive & Component Architecture

**Version**: 3.1.9-SNAPSHOT  
**Last Updated**: February 2026  
**Prerequisites**: Read Part 1 first

---

## Table of Contents - Part 2

1. [Foundation Layer - Shared Libraries](#1-foundation-layer---shared-libraries)
2. [Gateway Layer](#2-gateway-layer)
3. [Core Services Layer](#3-core-services-layer)
4. [Message Queue Architecture](#4-message-queue-architecture)
5. [Database Architecture](#5-database-architecture)
6. [Complete Business Flows](#6-complete-business-flows)

---

## 1. Foundation Layer - Shared Libraries

### 1.1 The `engine` Module - Heart of the System

**Location:** `/engine`  
**Artifact:** `com.embrix.core:engine:3.1.9-SNAPSHOT`  
**Purpose:** Centralized business logic for entire platform

**Why Critical:**
- ✅ Every microservice depends on it
- ✅ Single source of truth for business rules
- ✅ Contains all data access logic (JOOQ)
- ✅ Manages database migrations (Flyway)

#### 1.1.1 Hub-Based Organization

The engine is organized into "Hubs" - each representing a major business domain:

```
engine/src/main/groovy/com/embrix/core/engine/
├── arHub/                    # Accounts Receivable
│   ├── payment/              # Payment processing
│   ├── collection/           # Collections and aging
│   ├── creditDebitNotes/     # Credit/debit notes
│   └── arOps/                # AR operations
├── billingHub/               # Billing Operations
│   ├── billing/              # Billing cycles
│   ├── invoicing/            # Invoice generation
│   ├── rating/               # Charge calculation
│   └── taxation/             # Tax integration
├── customerHub/              # Customer Management
│   ├── customerManagement/   # Account CRUD
│   ├── orderManagement/      # Order processing
│   ├── subscriptionManagement/ # Subscription lifecycle
│   ├── quoteManagement/      # Quote generation
│   └── customizedPricingManagement/ # Custom pricing
├── pricingHub/               # Product Catalog
│   ├── pricingManagement/    # Price offers
│   └── bundleManagement/     # Bundles and packages
├── revenueHub/               # Revenue Recognition
│   ├── service/              # Revenue logic
│   └── entities/             # Revenue entities
├── usageProcessHub/          # Usage Rating
│   ├── service/              # Rating engine
│   └── entities/             # Usage entities
├── mediationHub/             # Usage Mediation
│   ├── service/              # Mediation logic
│   └── entities/             # Mediation entities
├── opsHub/                   # Operations
│   ├── userManagement/       # Users and roles
│   ├── jobManagement/        # Job scheduling
│   ├── correspondence/       # Notifications
│   ├── tenantOnboarding/     # Multi-tenant setup
│   └── singleSignOn/         # SSO integration
└── commonHub/                # Shared Services
    ├── document/             # Document generation
    ├── fileManagement/       # File operations
    ├── customAttributes/     # Custom fields
    └── oms/                  # Order management
```

#### 1.1.2 Real-World Hub Example: billingHub

**Location:** `engine/src/main/groovy/com/embrix/core/engine/billingHub/`

**Key Services:**

**1. ProrationEngine**
```groovy
class ProrationEngine {
    /**
     * Calculate prorated charge for mid-cycle activation/termination
     * 
     * Business Rule: 
     *   If customer activates on day 16 of 30-day month
     *   and monthly charge is $30.00
     *   then prorated charge = (30.00 / 30) * 15 = $15.00
     */
    Charge calculateProration(
        Subscription subscription,
        ProrationModel model,
        LocalDate startDate,
        LocalDate endDate
    ) {
        switch (model) {
            case ProrationModel.DAYS_IN_MONTH:
                return calculateDailyProration(subscription, startDate, endDate)
            case ProrationModel.FULL_DAY:
                return calculateFullDayProration(subscription, startDate, endDate)
            case ProrationModel.NO_PRORATION:
                return subscription.monthlyCharge
        }
    }
}
```

**2. BillingCycleEngine**
```groovy
class BillingCycleEngine {
    /**
     * Execute billing cycle for all accounts on specific bill day
     * 
     * Process:
     * 1. Find all accounts with bill_cycle_day = today
     * 2. For each account:
     *    - Generate recurring charges
     *    - Aggregate usage charges
     *    - Calculate taxes
     *    - Create invoice
     *    - Update account balance
     */
    void executeBillingCycle(Integer billCycleDay) {
        List<Account> accounts = findAccountsByBillCycleDay(billCycleDay)
        
        accounts.each { account ->
            try {
                // Generate charges
                List<Charge> charges = generateChargesForAccount(account)
                
                // Calculate taxes
                TaxCalculation taxes = taxGateway.calculateTax(charges)
                
                // Create invoice
                Invoice invoice = createInvoice(account, charges, taxes)
                
                // Update balance
                updateAccountBalance(account, invoice.totalAmount)
                
                log.info("Billing complete for account ${account.id}")
            } catch (Exception e) {
                log.error("Billing failed for account ${account.id}", e)
                // Continue with next account
            }
        }
    }
}
```

**3. DiscountEngine**
```groovy
class DiscountEngine {
    /**
     * Apply discounts to charges
     * 
     * Supports:
     * - Percentage discounts (e.g., 20% off)
     * - Fixed amount discounts (e.g., $10 off)
     * - Conditional discounts (e.g., first 3 months)
     * - Tiered discounts (e.g., volume discounts)
     */
    BigDecimal applyDiscount(Charge charge, Discount discount) {
        if (!discount.isApplicable(charge)) {
            return charge.amount
        }
        
        switch (discount.type) {
            case DiscountType.PERCENTAGE:
                return charge.amount * (1 - discount.value / 100)
            case DiscountType.FIXED_AMOUNT:
                return Math.max(charge.amount - discount.value, 0)
            default:
                return charge.amount
        }
    }
}
```

#### 1.1.3 Data Access with JOOQ

**Why JOOQ in Engine:**
- Type-safe queries checked at compile time
- Full SQL power (complex joins, CTEs, window functions)
- Near-native performance
- Generated code from database schema

**Example: Account Lookup**
```groovy
import static com.embrix.engine.jooq.Tables.*

class AccountRepository {
    @Autowired
    DSLContext dsl
    
    Account findById(String accountId) {
        return dsl
            .select()
            .from(ACCOUNT)
            .where(ACCOUNT.ID.eq(accountId))
            .fetchOneInto(Account.class)
    }
    
    List<Account> findOverdueAccounts() {
        return dsl
            .select()
            .from(ACCOUNT)
            .where(ACCOUNT.BALANCE.lt(BigDecimal.ZERO))
            .and(ACCOUNT.STATUS.eq("ACTIVE"))
            .orderBy(ACCOUNT.BALANCE.asc())
            .fetchInto(Account.class)
    }
    
    List<Invoice> findUnpaidInvoices(String accountId) {
        return dsl
            .select()
            .from(INVOICE)
            .join(ACCOUNT).on(INVOICE.ACCOUNT_ID.eq(ACCOUNT.ID))
            .where(ACCOUNT.ID.eq(accountId))
            .and(INVOICE.STATUS.in("PENDING", "OVERDUE"))
            .orderBy(INVOICE.DUE_DATE.asc())
            .fetchInto(Invoice.class)
    }
}
```

**JOOQ Code Generation:**
```bash
# Migrations are run
mvn flyway:migrate

# JOOQ generates Java classes from schema
mvn generate-sources

# Result: target/generated-sources/jooq-postgres/
# Contains type-safe table definitions
```

#### 1.1.4 Database Migrations with Flyway

**Location:** `engine/src/main/resources/db/migration/`

**Migration Structure:**
```
db/migration/
├── V1__Create_Schema.sql              # Core schemas
├── V2__Create_Enum_Types.sql          # Enum definitions
├── V3__Create_Config_Tables.sql       # Config schema
├── V4__Create_Domain_Tables.sql       # Business tables
├── V5__Create_Indexes.sql             # Performance indexes
├── V6__Create_Constraints.sql         # Foreign keys
├── V7__Create_Views.sql               # Database views
├── V8__Create_Functions.sql           # Stored procedures
├── V9__Create_Triggers.sql            # Database triggers
└── V10__Initial_Config_Data.sql       # Seed data
```

**Example Migration:**
```sql
-- V4.1__Create_Account_Table.sql
CREATE TABLE IF NOT EXISTS account (
    id VARCHAR(50) PRIMARY KEY,
    parent_account_id VARCHAR(50),
    account_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    currency_code VARCHAR(3) DEFAULT 'USD',
    balance NUMERIC(19,4) DEFAULT 0,
    credit_limit NUMERIC(19,4),
    bill_cycle_day INTEGER,
    created_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP,
    CONSTRAINT fk_parent_account FOREIGN KEY (parent_account_id) 
        REFERENCES account(id)
);

CREATE INDEX idx_account_status ON account(status);
CREATE INDEX idx_account_bill_cycle ON account(bill_cycle_day);
```

**Running Migrations:**
```bash
cd engine
mvn flyway:migrate -Dspring.profiles.active=dev

# Output:
# Flyway 5.2.4 by Boxfuse
# Database: jdbc:postgresql://localhost:5432/coredb-urbanos
# Successfully validated 10 migrations
# Current version: V10
# Schema is up to date
```

### 1.2 The `common` Module - Shared Data Model

**Location:** `/common`  
**Artifact:** `com.embrix.core:common:3.1.9-SNAPSHOT`  
**Purpose:** Consistent DTOs, enums, and utilities across all services

**Why Important:**
- Ensures all services use same data structures
- Prevents version skew between services
- Central location for domain enums

#### 1.2.1 Domain Enums

**Order Management:**
```groovy
enum OrderType {
    NEW,                    // New service order
    ADD_PRODUCT,            // Add service to existing account
    MODIFY_PRODUCT,         // Change service parameters
    TERMINATE_SERVICE,      // Cancel service
    SUSPEND,                // Suspend due to non-payment
    RESUME,                 // Resume after payment
    CHANGE                  // General change order
}

enum OrderStatus {
    CREATED,                // Initial state
    VALIDATED,              // Passed validation
    PROVISIONING_INITIATED, // Sent to provisioning
    PROVISIONING,           // In progress
    PROVISIONED,            // Network activated
    COMPLETED,              // Fully fulfilled
    FAILED,                 // Provisioning failed
    CANCELLED               // Cancelled by customer/system
}

enum ServiceLineAction {
    ADD,                    // Add new service
    MODIFY,                 // Change existing service
    CANCEL,                 // Remove service
    SUSPEND,                // Temporary suspension
    RESUME                  // Reactivate service
}
```

**Billing:**
```groovy
enum ChargeType {
    RECURRING,              // Monthly/annual subscription
    ONE_TIME,               // Installation fee, device purchase
    USAGE,                  // Based on consumption
    ADHOC,                  // Manual adjustment
    ADJUSTMENT              // Correction
}

enum InvoiceStatus {
    PENDING,                // Generated, not sent
    SENT,                   // Emailed to customer
    PAID,                   // Fully paid
    PARTIALLY_PAID,         // Partial payment received
    OVERDUE,                // Past due date
    CANCELLED,              // Voided
    REFUNDED                // Refunded
}

enum ProrationModel {
    FULL_DAY,               // Charge for any partial day
    DAYS_IN_MONTH,          // Daily rate * days active
    NO_PRORATION            // Full charge regardless
}
```

**Accounts Receivable:**
```groovy
enum PaymentMethodType {
    CREDIT_CARD,
    DEBIT_CARD,
    ACH,                    // Bank transfer (US)
    WIRE_TRANSFER,
    CHECK,
    CASH,
    PAYPAL,
    STRIPE
}

enum PaymentStatus {
    PENDING,                // Submitted, not processed
    PROCESSING,             // In progress
    COMPLETED,              // Successfully processed
    FAILED,                 // Payment failed
    REFUNDED,               // Refunded to customer
    CANCELLED               // Cancelled before processing
}
```

#### 1.2.2 Shared DTOs

**OrderDTO:**
```groovy
class OrderDTO {
    String id                           // ORD-2024-001
    String accountId                    // ACC-1001
    String userId                       // User who created
    OrderType type                      // NEW, MODIFY, etc.
    OrderStatus status                  // CREATED, COMPLETED, etc.
    Boolean allowedPartialFulfillment   // Can partially fulfill?
    LocalDateTime createdDate
    LocalDateTime completedDate
    
    List<ServiceDTO> services           // Nested services
    Map<String, Object> extendedData    // Flexible attributes
}

class ServiceDTO {
    Integer index                       // Line number
    String type                         // /service/mobile/5g
    String provisioningId               // External network ID
    ServiceLineStatus status
    List<ServiceLineDTO> lines          // Service line items
}

class ServiceLineDTO {
    Integer index
    String priceOfferId                 // PLAN-5G-UNLIMITED
    ServiceLineAction action            // ADD, MODIFY, CANCEL
    ServiceLineStatus status
    Integer quantity
    String assetId                      // Device/equipment ID
    Map<String, Object> extendedData    // {IMEI: "...", SIM: "..."}
}
```

**InvoiceDTO:**
```groovy
class InvoiceDTO {
    String id                           // INV-2024-001
    String accountId
    LocalDate invoiceDate
    LocalDate dueDate
    LocalDate billingPeriodStart
    LocalDate billingPeriodEnd
    
    BigDecimal subtotal                 // Charges before tax
    BigDecimal taxTotal                 // Total tax
    BigDecimal totalAmount              // subtotal + taxTotal
    BigDecimal amountPaid               // Payments applied
    BigDecimal balance                  // totalAmount - amountPaid
    
    InvoiceStatus status
    String pdfUrl                       // S3 URL
    
    List<ChargeDTO> charges             // Line items
    List<TaxBreakdownDTO> taxBreakdown  // Tax details
}
```

**UsageRecordDTO:**
```groovy
class UsageRecordDTO {
    String id
    String accountId
    String subscriptionId
    String sourceId                     // IMSI, IP, device ID
    LocalDateTime startTime
    LocalDateTime endTime
    Integer duration                    // Seconds
    Long volume                         // Bytes
    String destination                  // Called number, URL
    String serviceType                  // VOICE_CALL, SMS, DATA
    BigDecimal ratedAmount              // Calculated charge
    String ratingPlanId
    UsageStatus status                  // UNRATED, RATED, BILLED
    Boolean billed
}
```

### 1.3 The `oms-component` Module - Orchestration Framework

**Location:** `/oms-component`  
**Artifact:** `com.congerotechnology:ctg-oms-component:0.0.1-SNAPSHOT`  
**Purpose:** Standardized framework for building order orchestrators

**What is an Orchestrator?**
An orchestrator is a workflow processor that:
1. Receives an order from ActiveMQ
2. Validates the order
3. Performs business logic (provisioning, billing, etc.)
4. Updates the order status
5. Routes to next orchestrator if needed

#### 1.3.1 Standard Orchestration Pipeline

```
Order Message (ActiveMQ)
    ↓
[1] OrderLoader
    ├─→ Fetch order from database via REST API
    ├─→ Set order in Camel exchange body
    └─→ Pass to next processor
    ↓
[2] OrderValidator
    ├─→ Execute validate() method (implemented by subclass)
    ├─→ Check required fields, business rules
    ├─→ If validation fails: throw NonRetryableException
    └─→ If transient issue: throw RetryableException
    ↓
[3] OrderProcessor
    ├─→ Execute process() method (implemented by subclass)
    ├─→ Main business logic
    ├─→ Call external gateways
    └─→ Update order data
    ↓
[4] OrderUpdater
    ├─→ Save order changes to database via REST API
    ├─→ Update status, timestamps
    └─→ Persist all modifications
    ↓
[5] RouteHandler
    ├─→ Check if next orchestrator configured
    ├─→ Forward to next queue if needed
    └─→ Order processing complete for this orchestrator
```

#### 1.3.2 Exception Handling Strategy

**NonRetryableException:**
- Validation errors (missing required field)
- Business rule violations (credit limit exceeded)
- Data integrity issues
- **Action:** Mark order as FAILED, execute `processError()`, no retry

**RetryableException:**
- Network timeouts
- External system unavailable
- Database deadlock
- **Action:** Retry with exponential backoff (7 retries max)

**Configuration:**
```yaml
application:
  queues:
    redeliveryPolicy:
      maxRetries: 7
      multiplier: 1.5
      delay: 250
# Retry delays: 250ms, 375ms, 562ms, 843ms, 1.26s, 1.9s, 2.85s
```

**Slack Alerting:**
```groovy
// Automatic Slack notification on critical failure
camel:
  component:
    slack:
      webhook-url: "https://hooks.slack.com/services/..."
# Posts to #camel-devops channel with order ID and error details
```

#### 1.3.3 Creating a Custom Orchestrator

**Example: Mobile Provisioning Orchestrator**

```groovy
package com.embrix.orchestrator.mobile

import com.congerotechnology.ctgomscomponent.OmsComponent
import org.apache.camel.Exchange
import org.springframework.stereotype.Component

@Component
class MobileProvisioningOrchestrator extends OmsComponent {
    
    @Autowired
    ProvisioningGatewayClient provisioningGateway
    
    @Autowired
    TaxGatewayClient taxGateway
    
    /**
     * Validate order data
     * Throw ValidationException if invalid
     */
    @Override
    void validate(Exchange exchange) {
        Order order = exchange.in.getBody(Order)
        
        // Validate account
        if (!order.accountId) {
            throw new ValidationException("Account ID required")
        }
        
        // Validate service line
        def serviceLine = order.services[0]?.lines[0]
        if (!serviceLine) {
            throw new ValidationException("At least one service line required")
        }
        
        // Validate mobile-specific attributes
        def extendedData = serviceLine.extendedData
        if (!extendedData.IMEI) {
            throw new ValidationException("IMEI required for mobile provisioning")
        }
        if (!extendedData.SIM_ID) {
            throw new ValidationException("SIM ID required")
        }
        
        log.info("Validation passed for order: ${order.id}")
    }
    
    /**
     * Main business logic
     * Call external systems, update order data
     */
    @Override
    void process(Exchange exchange) {
        Order order = exchange.in.getBody(Order)
        log.info("Processing mobile provisioning for order: ${order.id}")
        
        try {
            // Step 1: Calculate taxes
            def taxRequest = buildTaxRequest(order)
            def taxResponse = taxGateway.calculateTax(taxRequest)
            order.estimatedTax = taxResponse.totalTax
            log.info("Tax calculated: ${taxResponse.totalTax}")
            
            // Step 2: Provision service on network
            def provisionRequest = buildProvisionRequest(order)
            def provisionResponse = provisioningGateway.activateMobileService(provisionRequest)
            
            if (provisionResponse.status == 'SUCCESS') {
                // Update service line with network ID
                def serviceLine = order.services[0].lines[0]
                serviceLine.provisioningId = provisionResponse.networkId
                serviceLine.status = ServiceLineStatus.PROVISIONED
                
                log.info("Mobile service provisioned: ${provisionResponse.networkId}")
            } else {
                // Transient failure - will retry
                throw new RetryableException(
                    "Provisioning failed: ${provisionResponse.errorMessage}"
                )
            }
            
            // Step 3: Update order status
            order.status = OrderStatus.COMPLETED
            log.info("Order ${order.id} completed successfully")
            
        } catch (RetryableException e) {
            throw e  // Let framework handle retry
        } catch (Exception e) {
            log.error("Unexpected error processing order ${order.id}", e)
            throw new NonRetryableException("Processing failed: ${e.message}")
        }
    }
    
    /**
     * Error cleanup logic
     * Called when order fails permanently
     */
    @Override
    void processError(Exchange exchange) {
        Order order = exchange.in.getBody(Order)
        log.error("Order ${order.id} failed permanently")
        
        // Cleanup logic
        // - Rollback any partial provisioning
        // - Send notification to customer
        // - Create support ticket
        
        order.status = OrderStatus.FAILED
        order.services[0].lines[0].status = ServiceLineStatus.FAILED
    }
    
    private TaxRequest buildTaxRequest(Order order) {
        return new TaxRequest(
            accountId: order.accountId,
            serviceAddress: order.serviceAddress,
            lineItems: order.services.collect { service ->
                new TaxLineItem(
                    description: service.type,
                    amount: service.lines[0].estimatedPrice
                )
            }
        )
    }
    
    private ProvisionRequest buildProvisionRequest(Order order) {
        def serviceLine = order.services[0].lines[0]
        return new ProvisionRequest(
            serviceType: 'MOBILE_5G',
            imei: serviceLine.extendedData.IMEI,
            simId: serviceLine.extendedData.SIM_ID,
            plan: serviceLine.priceOfferId,
            accountId: order.accountId
        )
    }
}
```

**Queue Auto-Creation:**
When this orchestrator starts, OMS Component framework automatically:
1. Creates ActiveMQ queue: `MobileProvisioningOrchestrator`
2. Sets up consumer with retry policy
3. Wires validation → processing → update → routing pipeline

**To trigger this orchestrator from another service:**
```groovy
activemqTemplate.send("MobileProvisioningOrchestrator", orderMessage)
```

### 1.4 The `gateway-common` Module

**Location:** `/gateway-common`  
**Artifact:** `com.embrix.core:gateway-common:3.1.9-SNAPSHOT`  
**Purpose:** Shared logic for external system integration

**Features:**
- Generic Request/Response envelopes
- Error mapping and handling
- Retry policies for external API calls
- Authentication patterns (OAuth1, OAuth2, API key)
- Tenant configuration lookup

**Key Service: TenantRepositoryService**
```groovy
class TenantRepositoryServiceImpl {
    /**
     * Lookup tenant-specific gateway configuration
     * 
     * Example: Find QuickBooks OAuth credentials for tenant TIDLT-100005
     */
    Tenant findByTenantId(String tenantId, MerchantType gatewayType) {
        return jdbcTemplate.query(
            """
            SELECT * FROM core_config.tenant_merchants 
            WHERE id = ? 
            AND type = ? 
            AND status = 'ACTIVE'
            """,
            new TenantMerchantsRowMapper(),
            tenantId,
            gatewayType.name()
        )
    }
    
    /**
     * Get OAuth2 attributes for tenant
     */
    OAuth2Attributes getOAuth2Attributes(String tenantId, String merchantName) {
        // Query core_config.oauth2_attributes table
        // Returns: clientId, clientSecret, tokenUrl, scope, etc.
    }
}
```

---

## 2. Gateway Layer

Gateways are the **entry and exit points** of the platform. They normalize external data and protect core services from external system changes.

### 2.1 `crm_gateway` - The Front Door

**Location:** `/crm_gateway`  
**Internal Name:** `ctg-oms`  
**Port:** 8080 (default)  
**Purpose:** Main entry point for external systems (CRM, portals)

#### 2.1.1 Key Responsibilities

1. **GraphQL API** - Expose order and account management endpoints
2. **OAuth2 Authorization Server** - Issue JWT tokens
3. **Order Intake** - Receive orders from Salesforce
4. **Message Dispatch** - Push orders to ActiveMQ
5. **Order Status Queries** - Track order progress

#### 2.1.2 GraphQL Schema

**Create Order Mutation:**
```graphql
mutation CreateOrder {
  createOrder(input: {
    accountId: "ACC-1001"
    type: NEW
    status: CREATED
    userId: "user@example.com"
    allowedPartialFulfillment: false
    createdDate: "2024-01-15T10:30:00.000Z"
    services: [{
      index: 1
      type: "/service/internet/fiber"
      provisioningId: null
      status: CREATED
      lines: [{
        index: 1
        priceOfferId: "FIBER-100M-UNLIMITED"
        action: ADD
        status: SUBMITTED
        quantity: 1
        assetId: "ONT-12345"
        extendedData: {
          INSTALLATION_ADDRESS: "123 Main St, Apt 4B"
          INSTALLATION_DATE: "2024-01-20"
          SERVICE_SPEED: "100Mbps"
        }
      }]
    }]
  }) {
    id
    status
    createdDate
    services {
      lines {
        status
        provisioningId
      }
    }
  }
}
```

**Query Orders:**
```graphql
query GetOrders {
  searchOrders(filter: {
    accountId: "ACC-1001"
    status: PROVISIONING
    dateFrom: "2024-01-01"
    dateTo: "2024-01-31"
  }) {
    id
    type
    status
    createdDate
    services {
      type
      status
      lines {
        priceOfferId
        action
        status
        provisioningId
      }
    }
  }
}
```

#### 2.1.3 OAuth2 Flow

**Token Request:**
```bash
curl -X POST http://localhost:8080/oauth/token \
  -H "Authorization: Basic $(echo -n 'congero:ctg-secret' | base64)" \
  -d "grant_type=client_credentials" \
  -d "scope=all"
```

**Token Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "all"
}
```

**Using Token:**
```bash
curl -X POST http://localhost:8080/graphql \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { createOrder(...) { id } }"}'
```

#### 2.1.4 Order Processing Flow in CRM Gateway

```
GraphQL Request
    ↓
[1] Authentication Interceptor
    ├─→ Validate JWT token
    ├─→ Check authorization scopes
    └─→ Extract tenant context
    ↓
[2] GraphQL Resolver: createOrder()
    ├─→ Validate input schema
    ├─→ Map GraphQL input to Order DTO
    └─→ Call OMS service
    ↓
[3] PGOmsService.processOrder()
    ├─→ Check if order already exists
    ├─→ If new: create order in database (status: CREATED)
    ├─→ Create activity log
    └─→ Return order to resolver
    ↓
[4] OmsProcessor (Apache Camel route)
    ├─→ Archive message to OMS_ARCHIVE queue (compliance)
    ├─→ Push message to OMS queue for processing
    └─→ Push success response to OMS_RESPONSE queue
    ↓
[5] Response to Client
    └─→ Return order ID and status
```

### 2.2 `provision_gateway` - Service Activation

**Location:** `/provision_gateway`  
**Port:** 8081 (default)  
**Purpose:** Bridge to network provisioning systems

#### 2.2.1 Supported Provisioning Systems

**1. Nokia ESB (MCM Telecom)**
- Internet service provisioning
- Equipment configuration (ONT, CPE)
- VLAN assignment
- IP address management

**2. ServiceNow**
- Ticket creation for manual provisioning
- Workflow orchestration
- Status tracking

**3. Generic REST/SOAP**
- Customizable adapters for any vendor

#### 2.2.2 Provisioning Flow

```
Order from crm_gateway
    ↓
[1] PGProvisioningGatewayService.processProvisioning()
    ├─→ Analyze order requirements
    │   - Service type (internet, voice, TV)
    │   - Equipment needed (ONT, STB, router)
    │   - Network resources (IP, VLAN, bandwidth)
    ├─→ Assign resources from inventory
    │   - Equipment: ONT-12345
    │   - IP address: 10.5.123.45
    │   - VLAN: 100
    │   - Speed: 100Mbps
    └─→ Configure parameters in order
    ↓
[2] createProvisioningOrder()
    ├─→ Map order to vendor-specific format
    │   (Nokia ESB format for MCM)
    ├─→ Send SOAP/REST request to Nokia
    └─→ Return provisioning request ID
    ↓
[3] Wait for callback
    └─→ External system processes provisioning
        (can take minutes to hours)
    ↓
[4] Provisioning Complete Callback
    └─→ Message arrives on MCM_BILLING_OMS_RESPONSE queue
    ↓
[5] ProvisioningResponseProcessor
    ├─→ Parse callback message
    ├─→ Extract network ID and status
    ├─→ Update order.services[*].lines[*].provisioningId
    ├─→ Update status to PROVISIONED
    └─→ Trigger billing
```

#### 2.2.3 Resource Management

**Equipment Assignment:**
```groovy
class EquipmentService {
    /**
     * Assign equipment from inventory
     */
    String assignEquipment(String equipmentType, String serviceType) {
        // Query available equipment
        Equipment equipment = findAvailableEquipment(equipmentType)
        
        if (equipment == null) {
            throw new ResourceUnavailableException(
                "No ${equipmentType} available for ${serviceType}"
            )
        }
        
        // Mark as assigned
        equipment.status = "ASSIGNED"
        equipment.assignedDate = LocalDateTime.now()
        save(equipment)
        
        return equipment.id
    }
}
```

**DID/Phone Number Assignment:**
```groovy
class DidService {
    /**
     * Assign phone number from pool
     */
    String assignDid(String countryCode, String areaCode) {
        // Query available DIDs
        Did did = dsl
            .select()
            .from(DID)
            .where(DID.COUNTRY_CODE.eq(countryCode))
            .and(DID.AREA_CODE.eq(areaCode))
            .and(DID.STATUS.eq("AVAILABLE"))
            .limit(1)
            .fetchOneInto(Did.class)
        
        if (did == null) {
            throw new ResourceUnavailableException(
                "No DID available for ${countryCode}-${areaCode}"
            )
        }
        
        // Mark as assigned
        did.status = "ASSIGNED"
        did.assignedDate = LocalDateTime.now()
        save(did)
        
        return did.phoneNumber
    }
}
```

### 2.3 `tax-gateway` & `tax-engine` - Tax Compliance

**Location:** `/tax-gateway`, `/tax-engine`  
**Purpose:** Unified tax calculation interface

#### 2.3.1 Tax Calculation API

**Request:**
```json
POST /api/tax/calculate
{
  "tenantId": "TIDLT-100005",
  "accountId": "ACC-1001",
  "billingAddress": {
    "street1": "Av. Insurgentes Sur 1234",
    "street2": "Col. Del Valle",
    "city": "Ciudad de México",
    "state": "CDMX",
    "postalCode": "03100",
    "country": "MX"
  },
  "lineItems": [
    {
      "description": "Internet 100Mbps",
      "amount": 599.00,
      "taxable": true,
      "productCode": "INTERNET"
    },
    {
      "description": "Equipment Rental",
      "amount": 50.00,
      "taxable": true,
      "productCode": "EQUIPMENT"
    }
  ]
}
```

**Response:**
```json
{
  "totalTax": 103.84,
  "taxBreakdown": [
    {
      "jurisdiction": "Federal (IVA)",
      "rate": 0.16,
      "taxableAmount": 649.00,
      "taxAmount": 103.84
    }
  ],
  "lineItemTaxes": [
    {
      "lineItemIndex": 0,
      "taxAmount": 95.84
    },
    {
      "lineItemIndex": 1,
      "taxAmount": 8.00
    }
  ]
}
```

#### 2.3.2 Mexican CFDI Compliance Flow

```
Invoice Generated in service-invoice
    ↓
[1] Generate CFDI XML (Comprobante Fiscal Digital por Internet)
    ├─→ XML version 3.3 (SAT specification)
    ├─→ Include all required fields:
    │   - RFC (tax ID)
    │   - Folio (invoice number)
    │   - Fecha (issue date)
    │   - Subtotal, Total
    │   - Receptor (customer RFC)
    │   - Conceptos (line items)
    │   - Impuestos (taxes)
    └─→ Save to local directory:
        /data/{tenant}/pac_interface/upload/invoice/{INVOICE_ID}.xml
    ↓
[2] CRON Job (every 2 minutes)
    └─→ /data/{tenant}/pac_interface/script/process_pac_invoice_upload.sh
    ↓
[3] SFTP Upload to PAC Provider
    ├─→ Connect: sftp pac-provider-host
    ├─→ Upload XML file
    └─→ Move local file to processed folder
    ↓
[4] PAC Provider Processes
    ├─→ Validate XML schema
    ├─→ Validate business rules
    ├─→ Generate digital stamp (UUID)
    └─→ Place stamped files on SFTP server:
        - {INVOICE_ID}_stamped.pdf
        - {INVOICE_ID}_stamped.xml
        - {INVOICE_ID}_status.txt
    ↓
[5] CRON Job (every 2 minutes)
    └─→ /data/{tenant}/pac_interface/script/process_pac_invoice_download.sh
    ↓
[6] SFTP Download from PAC Provider
    ├─→ Download stamped files
    └─→ Save to local directory:
        /data/{tenant}/pac_interface/download/invoice/
    ↓
[7] service-invoice processes stamped files
    ├─→ Extract UUID from stamped XML
    ├─→ Upload PDF to S3:
        s3://{tenant}-invoices/2024/01/{INVOICE_ID}_stamped.pdf
    ├─→ Update invoice record:
        invoice.uuid = "ABC123..."
        invoice.stampedDate = now()
        invoice.pdfUrl = "s3://..."
    └─→ Send email to customer with stamped PDF
```

**CFDI XML Example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
    xmlns:cfdi="http://www.sat.gob.mx/cfd/3"
    Version="3.3"
    Folio="INV-2024-001"
    Fecha="2024-01-15T10:30:00"
    SubTotal="649.00"
    Total="752.84"
    TipoDeComprobante="I"
    MetodoPago="PUE"
    LugarExpedicion="03100">
    
    <cfdi:Emisor Rfc="MCM123456789" Nombre="MCM Telecom SA de CV"/>
    
    <cfdi:Receptor 
        Rfc="XAXX010101000" 
        Nombre="Juan Perez" 
        UsoCFDI="G03"/>
    
    <cfdi:Conceptos>
        <cfdi:Concepto 
            ClaveProdServ="81112200"
            Cantidad="1"
            ClaveUnidad="E48"
            Descripcion="Internet 100Mbps"
            ValorUnitario="599.00"
            Importe="599.00"/>
    </cfdi:Conceptos>
    
    <cfdi:Impuestos TotalImpuestosTrasladados="103.84">
        <cfdi:Traslados>
            <cfdi:Traslado Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="103.84"/>
        </cfdi:Traslados>
    </cfdi:Impuestos>
</cfdi:Comprobante>
```

### 2.4 `payment-gateway` - Payment Processing

**Location:** `/payment-gateway`  
**Purpose:** Payment processor integration

#### 2.4.1 Supported Payment Methods

**1. Credit/Debit Cards (Stripe, PayPal)**
- Real-time authorization
- Tokenized card storage
- PCI compliance

**2. Bank Transfers (Mexican Banks)**
- Banamex
- Bancomer (BBVA)
- Banorte
- Santander
- Scotiabank

**3. Bank File Processing Flow**

```
Bank generates daily payment file
    ↓
[1] Bank uploads file to S3 or SFTP
    └─→ s3://{tenant}-payments/{BANK}/input/payments_20240115.csv
    ↓
[2] CRON job detects file
    └─→ /data/{tenant}/batch_payment/script/load_payment_by_type.sh
    ↓
[3] Download and load to database
    ├─→ pgloader --type csv {FILE} postgresql://...
    └─→ Insert into {bank}_payment table
    ↓
[4] service-payment: processBatchPayment()
    └─→ Query: SELECT * FROM {bank}_payment WHERE processed = false
    ↓
[5] For each payment record:
    ├─→ Parse account reference
    │   (e.g., "INV-2024-001" or "ACC-1001")
    ├─→ Find account by reference
    ├─→ Find pending invoices for account
    ├─→ Create payment record
    ├─→ Allocate payment to invoices (oldest first)
    ├─→ Update invoice status (PAID if fully paid)
    ├─→ Update account balance
    └─→ Mark bank record as processed = true
    ↓
[6] If account was suspended due to non-payment:
    └─→ Auto-generate RESUME order (EP-5480 enhancement)
```

**Bank File Format (CSV):**
```csv
Date,Reference,Amount,BankTransactionId
2024-01-15,INV-2024-001,752.84,BNX123456789
2024-01-15,ACC-1001,1500.00,BNX123456790
2024-01-15,INV-2024-002,399.00,BNX123456791
```

### 2.5 `finance-gateway` - ERP Integration

**Location:** `/finance-gateway`  
**Purpose:** Sync billing data to ERP systems

#### 2.5.1 Supported ERP Systems

**1. QuickBooks Online**
- OAuth2 authentication
- Real-time invoice sync
- Payment matching
- Customer sync

**2. NetSuite (Planned)**
- RESTlet integration
- Journal entry export
- Revenue recognition

**3. Oracle EBS (Planned)**
- API integration
- GL posting

#### 2.5.2 QuickBooks Integration Flow

```
Invoice finalized in service-invoice
    ↓
[1] Trigger finance sync event
    └─→ Push to finance-gateway queue
    ↓
[2] finance-gateway: QuickBooksService
    ├─→ Lookup tenant's QuickBooks OAuth tokens from Vault
    ├─→ Refresh access token if expired
    └─→ Authenticate with QuickBooks API
    ↓
[3] Map Embrix invoice to QuickBooks format
    ├─→ Customer mapping (Embrix Account → QB Customer)
    ├─→ Product mapping (Embrix Price Offer → QB Item)
    ├─→ Tax mapping (Embrix Tax → QB Tax Code)
    └─→ Build QB invoice JSON
    ↓
[4] POST /v3/company/{companyId}/invoice
    ├─→ Send invoice to QuickBooks
    └─→ Receive QB invoice ID
    ↓
[5] Update Embrix invoice
    ├─→ invoice.externalId = QB invoice ID
    ├─→ invoice.syncStatus = "SYNCED"
    └─→ invoice.syncDate = now()
```

**QuickBooks API Request:**
```json
POST https://quickbooks.api.intuit.com/v3/company/123456789/invoice
Authorization: Bearer {access_token}
Accept: application/json
Content-Type: application/json

{
  "CustomerRef": {"value": "67"},
  "TxnDate": "2024-01-15",
  "DueDate": "2024-02-15",
  "Line": [
    {
      "DetailType": "SalesItemLineDetail",
      "Amount": 599.00,
      "SalesItemLineDetail": {
        "ItemRef": {"value": "12"},
        "Qty": 1,
        "UnitPrice": 599.00
      },
      "Description": "Internet 100Mbps"
    }
  ],
  "TxnTaxDetail": {
    "TotalTax": 103.84
  }
}
```

---

**Continue to Part 2B for Core Services Layer and Business Flows...**

