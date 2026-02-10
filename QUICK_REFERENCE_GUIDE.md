# Embrix O2X - Quick Reference Guide

**For**: Developers who've read the full guides and need quick lookups  
**Version**: 3.1.9-SNAPSHOT

---

## 🏗️ Architecture Cheat Sheet

### Layers (Bottom to Top):
```
Infrastructure: PostgreSQL, Redis, ActiveMQ, Vault, S3
     ↓
Foundation: engine (hubs), common (DTOs), oms-component, gateway-common
     ↓
Core Services: billing, invoice, usage, payment, revenue, mediation
     ↓
Messaging: ActiveMQ queues (OMS, PROVISIONING_RESPONSE, MEDIATION, USAGE)
     ↓
Gateways: crm, provision, tax, payment, finance, diameter
     ↓
External: Salesforce, Nokia, Banks, PAC Providers, ERP
```

### Key Principles:
- **Shared Engine**: All business logic in `engine`
- **Event-Driven**: ActiveMQ for async processing
- **Gateway Pattern**: Isolate external systems
- **GraphQL-First**: Flexible API layer
- **Multi-Tenant**: Database-per-tenant

---

## 📦 Module Quick Reference

| Module | Purpose | Depends On | Port |
|--------|---------|------------|------|
| `common` | DTOs, Enums | - | N/A |
| `engine` | Business Logic | common | N/A |
| `oms-component` | Orchestration | engine, common | N/A |
| `gateway-common` | Gateway Utils | common | N/A |
| `jobs-common` | Batch Jobs | engine, common | N/A |
| `crm_gateway` | Order Intake | engine, common, oms-component | 8080 |
| `provision_gateway` | Provisioning | gateway-common | 8081 |
| `tax-gateway` | Tax Calc | gateway-common | varies |
| `payment-gateway` | Payments | gateway-common | varies |
| `finance-gateway` | ERP Sync | gateway-common | varies |
| `service-billing` | Billing | engine, common | varies |
| `service-invoice` | Invoicing | engine, common | varies |
| `service-usage` | Usage Data | engine, common | varies |
| `service-payment` | Payment Mgmt | engine, common | varies |
| `service-revenue` | Rev Rec | engine, common | varies |
| `batch-process` | Batch Jobs | engine, common, jobs-common | varies |

---

## 🗄️ Database Quick Reference

### Schemas:
```sql
core_engine      -- Shared entities (account, subscription, user)
core_oms         -- Orders (order, service_line, order_activity)
core_billing     -- Financial (charge, invoice, payment)
core_pricing     -- Catalog (product, price_offer, discount)
core_usage       -- Usage (usage_record - partitioned)
core_revenue     -- Rev Rec (journal_entry, deferred_revenue)
core_config      -- Config (tenant, tenant_merchants, oauth*)
core_mediation   -- CDR processing
```

### Key Tables:
```sql
-- Account
core_engine.account
  - id, parent_account_id, account_type, status, balance, bill_cycle_day

-- Order
core_oms.order
  - id, account_id, type, status, extended_data (JSONB)

-- Invoice
core_billing.invoice
  - id, account_id, invoice_date, due_date, subtotal, tax_total, total_amount, 
    amount_paid, balance, status, pdf_url, uuid (CFDI)

-- Usage (Partitioned by usage_date)
core_usage.usage_record
  - id, account_id, subscription_id, source_id, usage_date, start_time, 
    duration, volume, destination, service_type, rated_amount, status, billed
```

### Common Queries:
```sql
-- Find active accounts
SELECT * FROM core_engine.account WHERE status = 'ACTIVE';

-- Find overdue invoices
SELECT * FROM core_billing.invoice 
WHERE status = 'OVERDUE' AND account_id = ?;

-- Find unbilled usage
SELECT * FROM core_usage.usage_record 
WHERE account_id = ? AND billed = false AND status = 'RATED';

-- Find account balance
SELECT balance FROM core_engine.account WHERE id = ?;
```

---

## 📨 ActiveMQ Queues

| Queue | Purpose | Producer | Consumer |
|-------|---------|----------|----------|
| `OMS` | Order intake | Salesforce CRM | crm_gateway |
| `OMS_ARCHIVE` | Audit trail | crm_gateway | Audit system |
| `OMS_RESPONSE` | Order confirmations | crm_gateway | Salesforce CRM |
| `PROVISIONING_RESPONSE` | Provision callback | Nokia/ServiceNow | crm_gateway |
| `MCM_BILLING_OMS_RESPONSE` | MCM responses | Nokia | provision_gateway |
| `MEDIATION` | CDR processing | Mediation system | service-mediation |
| `USAGE` | Usage rating | Batch process | service-usage |
| `BULK` | Bulk operations | service-proxy | batch-process |
| `{OrchestratorName}` | Custom queues | Any | OmsComponent-based |

**Retry Policy**: 7 retries, 250ms initial, 1.5x multiplier

---

## 🌐 GraphQL Endpoints

### crm_gateway (Port 8080)
```graphql
# Create Order
mutation {
  createOrder(input: {...}) { id status }
}

# Query Orders
query {
  searchOrders(filter: {...}) { id status services {...} }
}

# Get Account
query {
  getAccount(id: "ACC-001") { id balance subscriptions {...} }
}
```

### service-billing
```graphql
mutation {
  runBillingCycle(input: {...}) { totalAccountsBilled totalAmount }
  calculateProration(input: {...}) { proratedAmount daysActive }
}
```

### service-invoice
```graphql
mutation {
  generateInvoice(input: {...}) { invoiceId pdfUrl totalAmount }
}
```

### service-usage
```graphql
query {
  searchUsageRecords(filter: {...}) { records {...} totalAmount }
  getUsageSummary(input: {...}) { voiceMinutes dataGB totalCharges }
}
```

### service-payment
```graphql
mutation {
  processPayment(input: {...}) { paymentId status transactionId }
}
```

**Access**: http://localhost:8080/graphiql

---

## 🔐 Security & Configuration

### OAuth2 Token (crm_gateway):
```bash
curl -X POST http://localhost:8080/oauth/token \
  -H "Authorization: Basic $(echo -n 'congero:ctg-secret' | base64)" \
  -d "grant_type=client_credentials&scope=all"
```

### Vault Secrets:
```bash
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=myroot

vault kv put secret/ctg-oms/dev \
  spring.datasource.url="..." \
  spring.datasource.username="..." \
  spring.datasource.password="..." \
  spring.activemq.broker-url="..." \
  application.tenant="..."
```

---

## 🛠️ Development Commands

### Build Order:
```bash
1. common:         mvn clean install -DskipTests
2. engine:         mvn clean install -DskipTests
3. oms-component:  mvn clean install -DskipTests
4. gateway-common: mvn clean install -DskipTests
5. jobs-common:    mvn clean install -DskipTests
6. services:       mvn clean install -DskipTests
```

### Run Service:
```bash
export VAULT_URI=http://localhost:8200
export VAULT_TOKEN=myroot
mvn spring-boot:run -Dspring.profiles.active=dev
```

### Database Migration:
```bash
cd engine
export DB_URL=jdbc:postgresql://localhost:5432/omsdevdb
export DB_USER=omsadmin
export DB_PASSWORD=password
mvn flyway:migrate -Dspring.profiles.active=dev
```

### Infrastructure:
```bash
# Start all
docker-compose up -d  # If docker-compose.yml exists

# Or individually
docker run -d --name postgres10 -p 5432:5432 -e POSTGRES_USER=omsadmin -e POSTGRES_PASSWORD=password -e POSTGRES_DB=omsdevdb postgres:10.5
docker run -d --name activemq -p 8161:8161 -p 61616:61616 webcenter/activemq:5.14.3
docker run -d --name redis -p 6379:6379 redis:6.2
docker run -d --name vault -p 8200:8200 -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' vault

# Check status
docker ps
```

---

## 🧪 Testing

### Unit Test (Spock):
```groovy
def "should calculate correct proration"() {
    given:
    def subscription = new Subscription(monthlyPrice: 30.0, startDate: LocalDate.of(2024, 1, 16))
    
    when:
    def charge = billingEngine.calculateProration(subscription, ProrationModel.DAYS_IN_MONTH)
    
    then:
    charge.amount == 15.48
}
```

### Run Tests:
```bash
# All tests
mvn test

# Specific hub
mvn test -PbillingHubMarker
mvn test -ParHubMarker
```

---

## 🔍 Debugging

### Enable Debug Logging:
```yaml
logging:
  level:
    com.embrix: DEBUG
    org.apache.camel: DEBUG
    org.jooq: DEBUG
```

### Check ActiveMQ:
- URL: http://localhost:8161
- Login: admin/admin
- Browse queues for stuck messages

### Database Query:
```bash
docker exec -it postgres10 psql -U omsadmin -d omsdevdb

# Recent orders
SELECT id, status, created_date FROM core_oms.order ORDER BY created_date DESC LIMIT 10;

# Unbilled charges
SELECT * FROM core_billing.charge WHERE status = 'UNBILLED';
```

### Redis:
```bash
docker exec -it redis redis-cli
KEYS *
GET pricing:product:123
```

---

## 📋 Common Tasks

### Add New Database Table:
```sql
-- 1. Create migration: engine/src/main/resources/db/migration/V1.XX__description.sql
CREATE TABLE core_billing.payment_method (...);

-- 2. Run migration
mvn flyway:migrate -Dspring.profiles.active=dev

-- 3. Regenerate JOOQ
mvn clean compile
```

### Add GraphQL Endpoint:
```graphql
-- 1. Define in schema.graphqls
type Query {
  getPaymentMethods(accountId: ID!): [PaymentMethod!]!
}

-- 2. Create resolver
@Component
class PaymentMethodResolver implements GraphQLQueryResolver {
    List<PaymentMethod> getPaymentMethods(String accountId) {...}
}
```

### Create Custom Orchestrator:
```groovy
@Component
class MyOrchestrator extends OmsComponent {
    @Override
    void validate(Exchange exchange) {...}
    
    @Override
    void process(Exchange exchange) {...}
    
    @Override
    void processError(Exchange exchange) {...}
}
// Queue auto-created: MyOrchestrator
```

---

## 🚨 Troubleshooting

| Problem | Check | Solution |
|---------|-------|----------|
| Build fails | Dependency order | Build common → engine first |
| Can't connect to DB | Docker running | `docker ps` → restart if needed |
| Vault secrets not found | Env vars | Set VAULT_URI, VAULT_TOKEN |
| ActiveMQ connection failed | Broker running | Check port 61616, restart broker |
| GraphQL 404 | Service started | Check logs, verify port |
| JOOQ classes missing | Generate sources | `mvn generate-sources` |
| Tests fail | Test DB | Check embedded PostgreSQL config |

---

## 📊 Business Flow Cheat Sheet

### Order Processing:
```
Salesforce CRM → crm_gateway.createOrder() → OMS queue → 
Orchestrator → provision_gateway → Nokia → Callback → 
service-billing → service-invoice → Customer notification
```

### Usage Processing:
```
Network CDR → SFTP → service-mediation (MEDIATION queue) → 
Normalize → service-usage (USAGE queue) → Rate → 
Store (billed=false) → Monthly billing → Invoice
```

### Payment Processing:
```
Bank file → S3 → CRON → service-payment → 
Parse → Allocate to invoices → Update account balance → 
Auto-resume if needed → Customer notification
```

### Tax Compliance (CFDI):
```
Invoice → Generate CFDI XML → SFTP upload to PAC → 
PAC stamps → SFTP download → Extract UUID → 
Upload to S3 → Update invoice → Send to customer
```

---

## 🔗 Useful URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| GraphQL Playground | http://localhost:8080/graphiql | OAuth2 token |
| ActiveMQ Console | http://localhost:8161 | admin/admin |
| Vault UI | http://localhost:8200/ui | Root token |
| PostgreSQL | localhost:5432 | omsadmin/password |
| Redis | localhost:6379 | (none) |

---

## 📞 Getting Help

**Documentation**:
- Full Guide: `NEWCOMER_GUIDE_INDEX.md`
- Part 1: Business & Architecture
- Part 2: Technical Deep Dive
- Part 3: Services & Development

**Codebase**:
- Business Logic: `engine/src/main/groovy/.../engine/{hub}/`
- Services: `core/service-*/src/main/groovy/`
- Gateways: `{gateway}/src/main/groovy/`
- Migrations: `engine/src/main/resources/db/migration/`
- GraphQL: `*/src/main/resources/graphql/`

**Common Questions**:
- Where is X business logic? → Check appropriate hub in engine
- How do I add Y? → See Part 3, Section 5 (Common Development Tasks)
- System isn't working? → See Troubleshooting section above

---

**Print This Page for Quick Reference! 📄**

