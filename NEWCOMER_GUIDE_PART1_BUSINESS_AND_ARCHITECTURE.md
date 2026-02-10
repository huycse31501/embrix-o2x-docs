# Embrix O2X Platform - Newcomer's Guide (Part 1)
## Business Overview & System Architecture

**Version**: 3.1.9-SNAPSHOT  
**Last Updated**: February 2026  
**Target Audience**: New developers, business analysts, and technical stakeholders

---

## Table of Contents - Part 1

1. [What is Embrix O2X?](#1-what-is-embrix-o2x)
2. [Business Purpose & Use Cases](#2-business-purpose--use-cases)
3. [Current Production Deployments](#3-current-production-deployments)
4. [System Architecture Overview](#4-system-architecture-overview)
5. [Technology Stack](#5-technology-stack)
6. [Multi-Tenant Architecture](#6-multi-tenant-architecture)
7. [Key Business Capabilities](#7-key-business-capabilities)

---

## 1. What is Embrix O2X?

### 1.1 Platform Definition

**Embrix O2X (Order-to-X)** is an enterprise-grade **telecommunications billing and order management platform** designed for service providers. The platform handles the complete customer lifecycle from order entry through provisioning, usage tracking, billing, invoicing, payment processing, and revenue recognition.

**"Order-to-X" means:**
- **Order-to-Cash**: Order → Provisioning → Billing → Payment
- **Order-to-Revenue**: Revenue recognition and financial compliance
- **Order-to-Service**: Service activation and lifecycle management

### 1.2 Target Market

**Primary Market:** Telecommunications & Service Providers
- Internet Service Providers (ISPs)
- Mobile Network Operators (MNOs)
- Cable Companies
- VoIP Service Providers
- Cloud Service Providers
- Utility Companies (expanding market)

### 1.3 Problem Statement

Traditional telecom billing systems struggle with:
- ❌ Complex pricing models (tiered, bundled, promotional)
- ❌ High-volume usage data processing (millions of CDRs daily)
- ❌ Multi-country tax compliance (especially LATAM)
- ❌ Real-time service provisioning integration
- ❌ Revenue recognition compliance (IFRS 15, ASC 606)
- ❌ Integration with diverse external systems (CRM, ERP, payment gateways)

**Embrix O2X Solution:**
✅ Flexible product catalog and pricing engine  
✅ High-performance usage mediation and rating  
✅ Automated tax compliance (Mexican CFDI, etc.)  
✅ Multi-vendor provisioning orchestration  
✅ Built-in revenue recognition  
✅ Gateway-based integration architecture

---

## 2. Business Purpose & Use Cases

### 2.1 Real-World Business Scenarios

#### Scenario 1: New Customer Signs Up for Internet Service

**Business Flow:**
```
Customer submits order via web portal
    ↓
Order validated (address serviceable, credit check)
    ↓
Service provisioned (ONT configured, VLAN assigned)
    ↓
Billing cycle started (prorated first month)
    ↓
Invoice generated with taxes
    ↓
Customer receives email with invoice PDF
    ↓
Payment processed (bank transfer)
    ↓
Payment allocated to invoice
    ↓
Revenue recognized over service period
```

**Embrix O2X Components Involved:**
- `crm_gateway` - Order intake from Salesforce
- `provision_gateway` - Nokia/ServiceNow provisioning
- `service-billing` - Charge generation
- `tax-gateway` - Tax calculation
- `service-invoice` - PDF generation
- `service-payment` - Payment processing
- `service-revenue` - Revenue recognition

#### Scenario 2: Mobile Customer Makes 100 Phone Calls

**Business Flow:**
```
Network switches generate 100 CDR records
    ↓
CDR file placed on SFTP server
    ↓
Mediation system ingests and normalizes CDRs
    ↓
Rating engine calculates charges (minutes used vs plan quota)
    ↓
Charges accumulated for monthly invoice
    ↓
End of month: Invoice includes usage charges
    ↓
Customer pays invoice
    ↓
Revenue recognized
```

**Embrix O2X Components Involved:**
- `service-mediation` - CDR ingestion and normalization
- `service-usage` - Rating and charge calculation
- `service-billing` - Monthly billing cycle
- `service-invoice` - Invoice generation
- `service-payment` - Payment processing

#### Scenario 3: Customer Payment Restores Suspended Service

**Business Flow:**
```
Customer account has negative balance (overdue invoices)
    ↓
Service automatically suspended (EP-5480 auto-suspend)
    ↓
Customer makes payment via bank transfer
    ↓
Payment file uploaded by bank daily
    ↓
Payment allocated to outstanding invoices
    ↓
Account balance becomes positive
    ↓
System auto-generates RESUME order (EP-5480 enhancement)
    ↓
Service restored on network
    ↓
Customer receives "Service Restored" notification
```

**Embrix O2X Components Involved:**
- `service-payment` - Bank file processing
- `crm_gateway` - Auto-resume order generation
- `provision_gateway` - Service restoration
- Notification service - Customer communication

### 2.2 Key Business Capabilities

#### 2.2.1 Order Management
**What it does:**
- Accepts orders from CRM systems (Salesforce, Dynamics)
- Validates order feasibility (service availability, credit limits)
- Orchestrates complex fulfillment workflows
- Tracks order status through lifecycle
- Handles order modifications and cancellations

**Business Value:**
- Automated order processing reduces manual errors
- Real-time validation prevents invalid orders
- Order tracking provides transparency to customers and support teams

#### 2.2.2 Service Provisioning
**What it does:**
- Integrates with network provisioning systems (Nokia, ServiceNow, Cisco)
- Assigns network resources (IP addresses, DIDs, VLANs)
- Configures customer equipment (ONTs, STBs, routers)
- Handles asynchronous provisioning workflows
- Manages equipment inventory

**Business Value:**
- Reduces provisioning time from days to minutes
- Eliminates manual configuration errors
- Enables zero-touch provisioning for customers

#### 2.2.3 Usage Mediation & Rating
**What it does:**
- Collects usage data from network elements (voice, SMS, data)
- Normalizes diverse CDR formats to canonical format
- Deduplicates records to prevent double-billing
- Rates usage according to customer pricing plans
- Tracks quotas and triggers overage charges

**Business Value:**
- Processes millions of CDRs daily
- Supports complex pricing (tiered, bundled, time-of-day)
- Ensures accurate billing for usage-based services
- Real-time quota monitoring prevents bill shock

#### 2.2.4 Billing & Invoicing
**What it does:**
- Generates recurring charges (monthly subscriptions)
- Calculates prorated charges for mid-cycle changes
- Aggregates usage charges
- Calculates taxes (VAT, sales tax, telecom-specific taxes)
- Generates customer-facing invoices (PDF, HTML, XML)

**Business Value:**
- Automated billing reduces manual effort
- Accurate proration ensures fair charging
- Multi-format invoices support diverse customer preferences
- Tax compliance reduces audit risk

#### 2.2.5 Payment Processing
**What it does:**
- Integrates with payment gateways (Stripe, PayPal, bank transfers)
- Processes automated bank file uploads (Banamex, Bancomer, Santander)
- Allocates payments to outstanding invoices
- Manages payment methods (credit cards, ACH, wire transfer)
- Handles payment failures and retries

**Business Value:**
- Multiple payment options improve collection rates
- Automated reconciliation reduces manual effort
- Real-time payment processing improves cash flow

#### 2.2.6 Tax Compliance
**What it does:**
- **Mexican CFDI Compliance**: Generates digital invoices (Comprobante Fiscal Digital por Internet)
- **PAC Integration**: Submits invoices to authorized stamping providers
- **UUID Tracking**: Tracks digital stamp IDs for audit purposes
- **SFTP Automation**: Automated file exchange with PAC providers
- **Audit Trail**: Complete compliance documentation

**Business Value:**
- Avoids penalties from Mexican tax authority (SAT)
- Automated stamping reduces manual effort
- Complete audit trail for compliance verification
- Supports multi-country expansion

#### 2.2.7 Revenue Recognition
**What it does:**
- **IFRS 15 / ASC 606 Compliance**: Follows international accounting standards
- **Deferred Revenue**: Tracks prepaid services
- **Performance Obligations**: Manages revenue recognition schedules
- **Journal Entry Generation**: Exports to ERP systems
- **Revenue Reporting**: Financial dashboards and reports

**Business Value:**
- Ensures compliance with accounting standards
- Provides accurate financial reporting
- Supports audits and SEC reporting (for public companies)
- Automates complex revenue recognition rules

#### 2.2.8 Financial Integration
**What it does:**
- **ERP Integration**: QuickBooks, NetSuite, Oracle EBS, SAP
- **GL Posting**: Automated general ledger entries
- **Reconciliation**: Matches billing to financial records
- **OAuth2 Authentication**: Secure integration with financial systems

**Business Value:**
- Eliminates manual data entry in accounting systems
- Ensures consistency between billing and financial data
- Reduces month-end close time
- Improves financial reporting accuracy

---

## 3. Current Production Deployments

### 3.1 Live Tenants

Based on Helm configurations and production deployments:

| Tenant | Country | Industry | Services | Status |
|--------|---------|----------|----------|--------|
| **MCM Telecom** | Mexico | Fixed-line ISP | Internet, Voice | Production |
| **CoopeG** | Costa Rica | Cooperative Telecom | Internet, Voice, TV | Production |
| **CoopeG Energy** | Costa Rica | Energy Utility | Electricity Billing | Production |
| **Urbanos** | (TBD) | (TBD) | (TBD) | Development |
| **SHM** | (TBD) | (TBD) | (TBD) | Production |

### 3.2 Scale Indicators

**MCM Telecom (Mexico):**
- Processes millions of CDRs monthly
- Mexican CFDI compliance with PAC integration
- Multi-bank payment processing (Banamex, Bancomer, Banorte, Santander)
- Nokia provisioning integration
- ServiceNow ticketing integration

**CoopeG (Costa Rica):**
- Multi-service provider (Internet, Voice, TV)
- Complex bundled pricing
- Customer self-service portal
- High transaction volume

---

## 4. System Architecture Overview

### 4.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SYSTEMS                              │
│  Salesforce CRM | Nokia Provisioning | Banks | PAC Providers | ERP  │
└────────────┬────────────────────────────────────┬────────────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         GATEWAY LAYER                                │
│  crm_gateway (8080) | provision_gateway (8081) | tax-gateway        │
│  payment-gateway | finance-gateway | diameter-gateway               │
│  Purpose: Normalize external data, protect core from changes        │
└────────────┬────────────────────────────────────┬────────────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│              MESSAGING & ORCHESTRATION LAYER                         │
│         ActiveMQ Broker (tcp://localhost:61616)                      │
│  Queues: OMS | PROVISIONING_RESPONSE | MEDIATION | USAGE | BULK     │
│  Purpose: Async processing, decoupling, resilience                  │
└────────────┬────────────────────────────────────┬────────────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CORE SERVICES LAYER                             │
│  service-billing | service-invoice | service-usage | service-payment│
│  service-mediation | service-revenue | batch-process                │
│  Purpose: Exposes business capabilities via GraphQL APIs            │
└────────────┬────────────────────────────────────┬────────────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   SHARED FOUNDATION LAYER                            │
│  ENGINE (Business Logic Hubs) | COMMON (DTOs/Enums)                 │
│  oms-component | gateway-common | jobs-common                        │
│  Purpose: Centralized business rules, shared libraries              │
└────────────┬────────────────────────────────────┬────────────────────┘
             │                                    │
             ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                              │
│  PostgreSQL 10.5 | Redis | ActiveMQ 5.15.9 | Vault | AWS S3         │
│  Purpose: Data persistence, caching, secrets, storage               │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Architecture Principles

#### 4.2.1 Shared Engine Pattern
**Principle:** Centralize business logic in shared library (`engine`)

**Why:**
- Single source of truth for business rules
- Consistency across all services
- Easier maintenance and testing
- Reduced code duplication

**Example:**
```groovy
// In engine/src/main/groovy/com/embrix/core/engine/billingHub/
class BillingEngine {
    Charge calculateProration(Subscription sub, ProrationModel model) {
        // Complex proration logic used by ALL services
    }
}

// In service-billing (uses engine)
@Autowired
BillingEngine billingEngine

def charge = billingEngine.calculateProration(subscription, ProrationModel.DAYS_IN_MONTH)
```

#### 4.2.2 Event-Driven Architecture
**Principle:** Asynchronous communication via ActiveMQ

**Why:**
- Resilience: Services can be down without losing messages
- Scalability: Queue consumers can scale independently
- Decoupling: Services don't need direct dependencies
- Retry: Automatic retry with exponential backoff

**Example:**
```groovy
// crm_gateway publishes order
activemqTemplate.send("OMS", orderMessage)

// provisioning orchestrator consumes
from("activemq://OMS")
    .process(provisioningProcessor)
```

#### 4.2.3 Gateway Pattern
**Principle:** Gateways isolate core from external systems

**Why:**
- Core services don't know about external system details
- External API changes don't break core logic
- Easier to swap providers (e.g., change tax provider)
- Simplified testing with mocked gateways

**Example:**
```
service-billing → tax-gateway → [Avalara OR custom tax engine]
                      ↑
                      Changes here don't affect service-billing
```

#### 4.2.4 GraphQL-First API
**Principle:** Core services expose GraphQL endpoints

**Why:**
- Flexible data fetching (clients request exactly what they need)
- Strongly typed schema
- Single endpoint for all operations
- Built-in documentation (GraphiQL)
- Reduces over-fetching and under-fetching

**Example:**
```graphql
# Client can request only needed fields
query {
  getAccount(id: "ACC-001") {
    id
    balance
    subscriptions {
      priceOfferId
      status
    }
  }
}
```

#### 4.2.5 Hub-Based Organization
**Principle:** Business domains organized into "Hubs" in engine

**Why:**
- Clear separation of concerns
- Team ownership by business domain
- Easier navigation of large codebase
- Logical grouping of related functionality

**Hubs:**
- `arHub` - Accounts Receivable
- `billingHub` - Billing Operations
- `customerHub` - Customer Management
- `pricingHub` - Product Catalog & Pricing
- `revenueHub` - Revenue Recognition
- `usageProcessHub` - Usage Rating
- `mediationHub` - Usage Data Mediation
- `opsHub` - Operations & Admin

---

## 5. Technology Stack

### 5.1 Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Java** | 8 | Core language |
| **Groovy** | 2.4.15 | Business logic (more concise than Java) |
| **Spring Boot** | 2.1.4 | Microservice framework |
| **Apache Camel** | 2.22.0 - 2.23.1 | Integration and routing |
| **GraphQL Java** | 5.0.2 | API layer |
| **JOOQ** | 3.11.10 | Type-safe SQL generation |
| **Flyway** | 5.2.4 | Database migrations |
| **Maven** | 3.6+ | Build and dependency management |

**Why Groovy?**
- Less boilerplate than Java
- Native JSON/XML support
- Dynamic typing when needed
- Seamless Java interoperability
- Concise collection operations

**Example:**
```groovy
// Groovy (concise)
def activeSubscriptions = subscriptions.findAll { it.status == 'ACTIVE' }
def totalRevenue = activeSubscriptions.sum { it.monthlyCharge }

// Equivalent Java (verbose)
List<Subscription> activeSubscriptions = subscriptions.stream()
    .filter(s -> "ACTIVE".equals(s.getStatus()))
    .collect(Collectors.toList());
BigDecimal totalRevenue = activeSubscriptions.stream()
    .map(Subscription::getMonthlyCharge)
    .reduce(BigDecimal.ZERO, BigDecimal::add);
```

### 5.2 Data Layer

| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 10.5+ | Primary relational database |
| **JOOQ** | 3.11.10 | Type-safe SQL queries |
| **Flyway** | 5.2.4 | Schema version control |
| **HikariCP** | (via Spring Boot) | Connection pooling |

**Why JOOQ over JPA/Hibernate?**
- ✅ Type-safe SQL checked at compile time
- ✅ Full SQL power (complex joins, CTEs, window functions)
- ✅ Near-native performance (no ORM overhead)
- ✅ Excellent for read-heavy workloads
- ✅ Generated code from schema

**Example:**
```groovy
// JOOQ query (type-safe)
def invoices = dsl
    .select()
    .from(INVOICE)
    .where(INVOICE.ACCOUNT_ID.eq(accountId))
    .and(INVOICE.STATUS.eq("PENDING"))
    .orderBy(INVOICE.DUE_DATE.asc())
    .fetch()
// Compile error if INVOICE.STATUS doesn't exist!
```

### 5.3 Messaging & Integration

| Technology | Version | Purpose |
|------------|---------|---------|
| **ActiveMQ** | 5.15.9 | Message broker |
| **Apache Camel** | 2.22.0 - 2.23.1 | Integration framework |

**ActiveMQ Queues:**
- `OMS` - Order intake
- `PROVISIONING_RESPONSE` - Provisioning callbacks
- `MEDIATION` - CDR file processing
- `USAGE` - Usage rating
- `BULK` - Bulk operations

**Retry Policy:**
```yaml
maxRetries: 7
initialDelay: 250ms
backoffMultiplier: 1.5x
# Retry delays: 250ms, 375ms, 562ms, 843ms, 1.26s, 1.9s, 2.85s
```

### 5.4 Security & Configuration

| Technology | Version | Purpose |
|------------|---------|---------|
| **HashiCorp Vault** | 2.0.2 | Secrets management |
| **OAuth2** | (Spring Security) | Authorization |
| **JWT** | (Spring Security) | Token-based auth |

**Vault Secrets:**
- Database credentials
- ActiveMQ credentials
- External API keys (QuickBooks, Stripe, etc.)
- JWT signing keys
- Slack webhook URLs

### 5.5 Document Generation

| Technology | Version | Purpose |
|------------|---------|---------|
| **iText** | 7.1.5 | PDF generation |
| **Apache FOP** | 2.3 | XSL-FO to PDF |
| **Thymeleaf** | 3.0.11 | HTML templates |

### 5.6 Caching & Performance

| Technology | Version | Purpose |
|------------|---------|---------|
| **Redis** | 6.2+ | Caching, real-time counters |
| **Jedis** | (via Spring Data Redis) | Redis client |

**Redis Use Cases:**
- Pricing catalog cache (fast lookup)
- Real-time usage quotas (prepaid balance checks)
- Session data
- Temporary computation results

### 5.7 Testing

| Technology | Version | Purpose |
|------------|---------|---------|
| **Spock Framework** | 1.1-groovy-2.4 | BDD testing (Groovy) |
| **JUnit** | 4.12 | Unit testing (Java) |
| **Embedded PostgreSQL** | 2.9 | Integration tests |
| **Embedded Redis** | 0.7.3 | Cache tests |

**Why Spock?**
- Readable BDD-style tests
- Built-in mocking
- Data-driven testing
- Groovy's expressiveness

**Example:**
```groovy
def "should calculate correct proration for mid-cycle activation"() {
    given: "a subscription starting mid-month"
    def subscription = new Subscription(
        monthlyPrice: 30.0,
        startDate: LocalDate.of(2024, 1, 16)
    )
    
    when: "proration is calculated"
    def charge = billingEngine.calculateProration(
        subscription, 
        ProrationModel.DAYS_IN_MONTH
    )
    
    then: "charge should be prorated for 16 days"
    charge.amount == 15.48  // (30.00 / 31) * 16
    charge.chargeType == ChargeType.RECURRING
}
```

### 5.8 DevOps & Infrastructure

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization |
| **Kubernetes** | Container orchestration |
| **Helm** | Deployment configuration |
| **AWS S3** | Document storage |
| **GitLab CI** | CI/CD pipeline |

---

## 6. Multi-Tenant Architecture

### 6.1 Deployment-Level Multi-Tenancy

**Architecture Pattern:** Each tenant gets:
- ✅ Dedicated Kubernetes deployment
- ✅ Dedicated database (`coredb-{tenant-name}`)
- ✅ Dedicated service instances
- ✅ Shared infrastructure (Kubernetes cluster, RDS instance)

**NOT shared-database multi-tenancy with `tenant_id` columns.**

### 6.2 Database Architecture

```
PostgreSQL RDS: embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com
├── coredb-urbanos (TIDLT-100005)
│   ├── account (no tenant_id column)
│   ├── subscription
│   ├── order
│   ├── invoice
│   └── ...
├── coredb-coopeg-sbx (TIDLT-100001)
│   ├── account (separate data)
│   ├── subscription
│   └── ...
└── coredb-coopegenergy (TIDLT-100007)
    ├── account (separate data)
    └── ...
```

**Shared Configuration Schema:**
```sql
-- Exists in all tenant databases
core_config.tenant
  ├── id (VARCHAR) - e.g., TIDLT-100005
  ├── name (VARCHAR) - e.g., urbanos
  ├── vaulturi - Vault URL
  └── licensekey

core_config.tenant_merchants
  ├── tenant_id - References tenant.id
  ├── name - QUICKBOOKS, STRIPE, AVALARA, etc.
  ├── type - FINANCE_GATEWAY, PAYMENT_GATEWAY, TAX_GATEWAY
  └── authtype - OAUTH1, OAUTH2, API_KEY
```

### 6.3 Service Naming Convention

```
Kubernetes Services: {tenant-name}-{service-name}

Examples:
  urbanos-service-transactional
  urbanos-service-billing
  urbanos-payment-gateway
  coopeg-prd-service-transactional
  coopeg-prd-tax-gateway
```

### 6.4 Tenant Context Injection

**Via Helm Values:**
```yaml
app:
  tenantId: TIDLT-100005
  tenantName: urbanos
  postgres:
    url: jdbc:postgresql://.../coredb-urbanos
  vault:
    api: http://urbanos-vault-interface/
```

**In Application Code:**
```groovy
@Value('${tenant.id}')
private String tenantId

@Value('${TENANT_ID}')
private String tenant_id
```

### 6.5 Advantages of This Architecture

**✅ Strong Data Isolation**
- Complete database separation
- No risk of cross-tenant data leaks
- Simplified compliance/auditing

**✅ Performance Isolation**
- One tenant's load doesn't impact others
- Dedicated resources per tenant
- Independent scaling

**✅ Customization Flexibility**
- Can deploy different versions per tenant
- Tenant-specific configuration
- Easy A/B testing

**✅ Simplified Development**
- No `tenant_id` filtering in business logic
- No complex query interceptors
- Easier testing

**✅ Independent Operations**
- Deploy/upgrade tenants independently
- Rollback single tenant without affecting others
- Different maintenance windows

### 6.6 Trade-offs

**⚠️ Infrastructure Cost**
- Higher resource usage (one deployment per tenant)
- More Kubernetes pods
- Database licensing

**⚠️ Operational Complexity**
- More deployments to monitor
- More CI/CD pipelines
- Helm chart management per tenant

**⚠️ Shared Resources**
- Single RDS instance (potential bottleneck)
- Shared Kubernetes cluster
- Shared Redis/ActiveMQ

---

## 7. Key Business Capabilities

### 7.1 Platform Capabilities Matrix

| Capability | Maturity | Complexity | Business Value |
|------------|----------|------------|----------------|
| Order Management | Production | Medium | High |
| Service Provisioning | Production | High | High |
| Usage Mediation | Production | High | Critical |
| Usage Rating | Production | High | Critical |
| Billing | Production | High | Critical |
| Invoicing | Production | Medium | High |
| Payment Processing | Production | Medium | High |
| Tax Compliance (CFDI) | Production | High | Critical (Mexico) |
| Revenue Recognition | Production | Medium | Medium |
| Financial Integration | Production | Medium | Medium |
| Multi-Tenant | Production | High | High |

### 7.2 Integration Capabilities

**Supported Integrations:**

| Category | Systems | Status |
|----------|---------|--------|
| **CRM** | Salesforce | Production |
| **Provisioning** | Nokia, ServiceNow | Production |
| **Tax** | PAC Providers (Mexico) | Production |
| **Tax** | Avalara | Design Phase |
| **Payment** | Stripe, PayPal | Production |
| **Payment** | Mexican Banks | Production |
| **ERP** | QuickBooks | Production |
| **ERP** | NetSuite | Design Phase |
| **ERP** | Oracle EBS | Design Phase |
| **Notifications** | Slack | Production |

### 7.3 Business KPIs Supported

**Operational Metrics:**
- Orders processed per day
- Provisioning success rate
- Average provisioning time
- CDR processing throughput
- Invoice generation time

**Financial Metrics:**
- Monthly recurring revenue (MRR)
- Annual recurring revenue (ARR)
- Churn rate
- Average revenue per user (ARPU)
- Collection efficiency
- Days sales outstanding (DSO)

**Compliance Metrics:**
- Tax stamping success rate (CFDI)
- Revenue recognition accuracy
- Billing accuracy
- Payment reconciliation rate

---

## Summary of Part 1

You've learned:
1. ✅ What Embrix O2X is and why it exists
2. ✅ Real-world business use cases
3. ✅ Current production deployments
4. ✅ High-level system architecture
5. ✅ Technology stack and rationale
6. ✅ Multi-tenant architecture model
7. ✅ Key business capabilities

**Next:** Part 2 covers detailed technical architecture, component interactions, and business flows.

**Next:** Part 3 covers development workflows, testing strategies, and operational procedures.

