# Embrix O2X Platform - Newcomer's Guide (Part 5)
## Message Queue Architecture & Integration Patterns

**Version**: 3.1.9-SNAPSHOT  
**Last Updated**: February 2026  
**Prerequisites**: Read Parts 1-4 first  
**Target Audience**: Backend developers, integration engineers, DevOps engineers

---

## Table of Contents - Part 5

1. [Message Queue Architecture Overview](#1-message-queue-architecture-overview)
2. [ActiveMQ Infrastructure](#2-activemq-infrastructure)
3. [Complete Queue Inventory](#3-complete-queue-inventory)
4. [Message Flow Patterns](#4-message-flow-patterns)
5. [Error Handling & Retry Mechanisms](#5-error-handling--retry-mechanisms)
6. [Message Formats & Examples](#6-message-formats--examples)
7. [Performance & Monitoring](#7-performance--monitoring)
8. [Development Guide](#8-development-guide)
9. [Troubleshooting](#9-troubleshooting)
10. [Best Practices](#10-best-practices)

---

## 1. Message Queue Architecture Overview

### 1.1 Why Message Queues?

**Embrix O2X uses message queues (ActiveMQ) as the backbone for asynchronous processing**, enabling:

| Benefit | Description | Example Use Case |
|---------|-------------|------------------|
| **Decoupling** | Services don't need to know about each other | CRM system sends orders; gateway processes independently |
| **Resilience** | System continues even if a service is down | Mediation continues even if usage service restarts |
| **Scalability** | Horizontal scaling of consumers | Multiple service-usage instances process USAGE queue |
| **Load Leveling** | Smooth out traffic spikes | 10,000 CDRs arrive at once, processed gradually |
| **Async Processing** | Non-blocking operations | Order submitted immediately, provisioning happens later |

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MESSAGE QUEUE ECOSYSTEM                           │
└─────────────────────────────────────────────────────────────────────────┘

 EXTERNAL SYSTEMS                   QUEUES                CONSUMERS
┌──────────────────┐          ┌──────────────┐      ┌─────────────────┐
│  Salesforce CRM  │──────────▶│  OMS         │──────▶│ crm_gateway     │
│  Orders/Accounts │          │  (Order      │      │ OmsReceiver     │
└──────────────────┘          │   Intake)    │      └─────────────────┘
                              └──────────────┘              │
                                     │                      │
                              ┌──────▼──────┐              │
┌──────────────────┐          │ OMS_ARCHIVE │              │
│  Nokia/ServiceNow│◀─────────┤ (Audit)     │              │
│  Provisioning    │          └─────────────┘              │
│  Callbacks       │                                        ▼
└───────┬──────────┘          ┌──────────────┐      ┌─────────────────┐
        │                     │ OMS_ERROR    │◀─────│ Archive/Error   │
        │                     │ (Failures)   │      │ Handling        │
        │                     └──────────────┘      └─────────────────┘
        │
        └────────────────────▶┌──────────────┐      ┌─────────────────┐
                              │ PROVISIONING │──────▶│ crm_gateway     │
                              │ _RESPONSE    │      │ OrderUpdater    │
                              │ (Callbacks)  │      └─────────────────┘
                              └──────────────┘              │
                                                            │
┌──────────────────┐          ┌──────────────┐            ▼
│  CDR Files       │          │ MEDIATION    │      ┌─────────────────┐
│  SFTP/S3         │──────────▶│ (CDR Process)│──────▶│ service-        │
└──────────────────┘          └──────────────┘      │ mediation       │
                                     │               │ MediationRcvr   │
                                     │               └────────┬────────┘
                                     │                        │
                                     │                        ▼
                              ┌──────▼──────┐      ┌─────────────────┐
│  Batch Process   │──────────▶│ USAGE      │──────▶│ service-usage   │
│  (Rating Trigger)│          │ (Rating)    │      │ UsageProcessor  │
└──────────────────┘          └──────────────┘      └─────────────────┘
                                     │
                                     │
┌──────────────────┐          ┌──────▼──────┐      ┌─────────────────┐
│  service-proxy   │──────────▶│ BULK       │──────▶│ jobs-common     │
│  Bulk Operations │          │ (Bulk Ops)  │      │ BulkProcessor   │
└──────────────────┘          └──────────────┘      └─────────────────┘
                                     │
                                     │
┌──────────────────┐          ┌──────▼──────┐      ┌─────────────────┐
│  Price Vendor    │──────────▶│ price-sync │──────▶│ pricing_sync    │
│  Updates         │          │             │      │ ConsumerProcess │
└──────────────────┘          └──────────────┘      └─────────────────┘
```

---

## 2. ActiveMQ Infrastructure

### 2.1 Deployment Architecture

**Embrix O2X uses Amazon MQ** (managed ActiveMQ service) for production:

```
┌─────────────────────────────────────────────────────────────┐
│ Amazon MQ Broker (ActiveMQ 5.16.x)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Deployment Mode: Active/Standby                            │
│  Instance Type: mq.m5.large                                 │
│  Storage: 100 GB EBS (auto-scaling enabled)                 │
│  Multi-AZ: Yes (High Availability)                          │
│                                                              │
│  Endpoints:                                                  │
│  • OpenWire (Java): ssl://b-xxx.mq.us-east-1.amazonaws.com:61617 │
│  • STOMP: ssl://b-xxx.mq.us-east-1.amazonaws.com:61614     │
│  • Web Console: https://b-xxx.mq.us-east-1.amazonaws.com:8162   │
│                                                              │
│  Authentication: Username/Password (Vault-managed)          │
│  Encryption: TLS 1.2+                                        │
│  VPC: Private subnet (no public access)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Local Development Setup

**Docker Compose** for local ActiveMQ:
```yaml
# docker-compose.yml (excerpt)
version: '3.8'
services:
  activemq:
    image: rmohr/activemq:5.15.9
    container_name: embrix-activemq
    ports:
      - "61616:61616"  # OpenWire (Java clients)
      - "8161:8161"    # Web Console
      - "5672:5672"    # AMQP
      - "61613:61613"  # STOMP
    environment:
      - ACTIVEMQ_ADMIN_LOGIN=admin
      - ACTIVEMQ_ADMIN_PASSWORD=admin
    volumes:
      - ./activemq-data:/var/activemq/data
      - ./activemq-conf:/opt/activemq/conf
    networks:
      - embrix-network
```

**Start ActiveMQ**:
```bash
docker-compose up -d activemq

# Verify running
docker ps | grep activemq

# Access Web Console
open http://localhost:8161/admin
# Credentials: admin/admin
```

### 2.3 Connection Configuration

**Spring Boot Configuration** (application.yml):
```yaml
spring:
  activemq:
    broker-url: tcp://localhost:61616
    # Production: ssl://b-xxx.mq.us-east-1.amazonaws.com:61617
    user: ${MQ_USERNAME}  # From Vault
    password: ${MQ_PASSWORD}  # From Vault
    pool:
      enabled: true
      max-connections: 10
      idle-timeout: 30000
    packages:
      trust-all: false
      trusted: com.embrix.core

# Camel configuration
camel:
  component:
    activemq:
      broker-url: ${spring.activemq.broker-url}
      username: ${spring.activemq.user}
      password: ${spring.activemq.password}
      concurrent-consumers: 3
      max-concurrent-consumers: 10
```

**Vault Secrets**:
```bash
# Store in Vault
vault kv put secret/activemq/production \
  username=embrix-prod-user \
  password=<secure-password>

# Retrieve in application
export MQ_USERNAME=$(vault kv get -field=username secret/activemq/production)
export MQ_PASSWORD=$(vault kv get -field=password secret/activemq/production)
```

---

## 3. Complete Queue Inventory

### 3.1 Active Production Queues

| Queue Name | Purpose | Producer(s) | Consumer(s) | Message Type | Avg Volume |
|------------|---------|-------------|-------------|--------------|------------|
| **OMS** | Order intake | Salesforce CRM, External systems | crm_gateway (OmsReceiver) | OrderDTO | 500-1000/day |
| **OMS_ARCHIVE** | Audit trail | crm_gateway | Audit system (passive) | OrderDTO | Same as OMS |
| **OMS_ERROR** | Failed orders | crm_gateway | Error handling / Manual review | OrderDTO + Error | 5-10/day |
| **OMS_RESPONSE** | Order confirmations | crm_gateway | External CRM | OrderResponseDTO | 500-1000/day |
| **PROVISIONING_RESPONSE** | Provisioning callbacks | Nokia, ServiceNow, Cisco | crm_gateway (OrderUpdater) | ProvisioningResponseDTO | 300-600/day |
| **MCM_BILLING_OMS_RESPONSE** | MCM-specific responses | MCM/Nokia systems | provision_gateway | MCMResponseDTO | 200-400/day |
| **MEDIATION** | CDR processing | External mediation system | service-mediation (MediationProcessor) | ProcessCdrsInput | 10-50 files/day |
| **USAGE** | Usage rating | batch-process | service-usage (UsageProcessor) | UsageContainerInput | Hourly batches |
| **BULK** | Bulk operations | service-proxy | jobs-common (BulkProcessor) | BulkProcessInput | 50-200/day |
| **price-sync** | Price catalog updates | External price vendor | pricing_sync | PriceSyncMessage | Weekly |

### 3.2 Defined but Inactive Queues

| Queue Name | Status | Reason | Future Use |
|------------|--------|--------|------------|
| **PRICING_SYNC** | Disabled | Feature EP-4729 disabled | Potential re-enable for automated pricing |
| **BILLING** | Not Used | Direct service invocation preferred | Reserved for future async billing |
| **PAYMENT** | Not Used | Payments processed synchronously | May be used for async payment webhooks |
| **INVOICE** | Not Used | Invoices generated on-demand | Reserved for batch invoice generation |
| **ACCOUNT** | Not Used | Accounts created synchronously | Reserved for future account events |

### 3.3 Custom/Dynamic Queues

**OmsComponent Framework** allows creation of custom queues per orchestrator:

```groovy
// Example: Custom queue for complex provisioning
@Component
class ComplexProvisioningOrchestrator extends OmsComponent {
    @Override
    String getQueueName() {
        return "COMPLEX_PROVISIONING"  // Creates dedicated queue
    }
    
    // Processing logic...
}
```

---

## 4. Message Flow Patterns

### 4.1 Order-to-Cash Flow (Synchronous + Async)

**Complete Flow with Queue Integration**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: ORDER INTAKE (Async via OMS Queue)                             │
└─────────────────────────────────────────────────────────────────────────┘

Salesforce CRM
  │ [1] Order Created
  │ POST to external endpoint
  ▼
┌─────────────────────┐
│ External Gateway    │
│ (Salesforce)        │
└──────────┬──────────┘
           │ [2] Send to OMS queue
           ▼
     ┌──────────┐
     │   OMS    │
     │  Queue   │
     └─────┬────┘
           │ [3] Consume message
           ▼
┌─────────────────────┐
│ crm_gateway         │
│ OmsReceiver         │
├─────────────────────┤
│ • Validate message  │
│ • Parse OrderDTO    │
│ • Enrich data       │
└──────────┬──────────┘
           │
           ├──────────────────┐ [4a] Archive (audit)
           │                  ▼
           │            ┌──────────────┐
           │            │ OMS_ARCHIVE  │
           │            └──────────────┘
           │
           ├──────────────────┐ [4b] On error
           │                  ▼
           │            ┌──────────────┐
           │            │  OMS_ERROR   │
           │            └──────────────┘
           │
           │ [5] Process order
           ▼
┌─────────────────────┐
│ OmsProcessor        │
├─────────────────────┤
│ • Create account    │
│ • Create order      │
│ • Create subs       │
└──────────┬──────────┘
           │
           ├──────────────────┐ [6] Send response
           │                  ▼
           │            ┌──────────────┐
           │            │OMS_RESPONSE  │──────▶ Back to CRM
           │            └──────────────┘
           │
           │ [7] Trigger provisioning
           ▼
┌─────────────────────┐
│ provision_gateway   │
│ • Nokia ESB call    │
└─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: PROVISIONING CALLBACK (Async via PROVISIONING_RESPONSE)        │
└─────────────────────────────────────────────────────────────────────────┘

Nokia/Network Element
  │ [8] Provisioning Complete
  │ Callback webhook
  ▼
┌───────────────────────┐
│ Provisioning System   │
│ (Nokia, ServiceNow)   │
└──────────┬────────────┘
           │ [9] Send callback
           ▼
     ┌──────────────────────┐
     │ PROVISIONING_RESPONSE│
     │      Queue           │
     └─────┬────────────────┘
           │ [10] Consume
           ▼
┌─────────────────────┐
│ crm_gateway         │
│ OrderUpdater        │
├─────────────────────┤
│ • Update order      │
│ • Set COMPLETED     │
└──────────┬──────────┘
           │
           │ [11] Trigger billing
           ▼
┌─────────────────────┐
│ service-billing     │
│ • Create charges    │
│ • Schedule billing  │
└──────────┬──────────┘
           │
           │ [12] Generate invoice
           ▼
┌─────────────────────┐
│ service-invoice     │
│ • Create PDF        │
│ • Send to customer  │
└─────────────────────┘

Time Breakdown:
[1-7]  : 2-5 seconds (async order processing)
[8-10] : 5-30 minutes (provisioning varies by network)
[11-12]: 1-2 seconds (billing trigger)
Total: 5-30 minutes for complete flow
```

### 4.2 Usage Rating Pipeline (Multi-Queue Async)

**High-Volume CDR Processing**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: MEDIATION (MEDIATION Queue)                                    │
└─────────────────────────────────────────────────────────────────────────┘

CDR Files on SFTP/S3
  │ 1000s-100,000s of records
  ▼
┌─────────────────────┐
│ External Mediation  │
│ System / Batch Job  │
└──────────┬──────────┘
           │ [1] Trigger mediation
           │ Message: { fileName, serviceType, tenantName }
           ▼
     ┌──────────┐
     │MEDIATION │
     │  Queue   │
     └─────┬────┘
           │ [2] Consume
           ▼
┌─────────────────────────────────┐
│ service-mediation               │
│ MediationProcessor              │
├─────────────────────────────────┤
│ [3] Download CDR file           │
│ • SFTP or S3                    │
│ [4] Parse and normalize         │
│ • Vendor format → Canonical     │
│ • Enrich with account data      │
│ [5] Deduplicate                 │
│ • Check for existing records    │
│ [6] Store UNRATED records       │
│ • core_usage.usage_record       │
│ • status = 'UNRATED'            │
└──────────┬──────────────────────┘
           │
           │ [7] Mediation complete
           │ Stored: 50,000 UNRATED records
           ▼

Processing Time: 5-30 minutes for 50,000 CDRs
Database Inserts: Batch insert (1000 per batch)

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: RATING (USAGE Queue)                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│ batch-process       │
│ (Scheduled Job)     │
├─────────────────────┤
│ [8] Hourly trigger  │
│ Query UNRATED usage │
│ Group by account    │
└──────────┬──────────┘
           │ [9] Trigger rating
           │ Message: { usageRecordIds[], batchId }
           ▼
     ┌──────────┐
     │  USAGE   │
     │  Queue   │
     └─────┬────┘
           │ [10] Consume
           ▼
┌─────────────────────────────────┐
│ service-usage                   │
│ UsageProcessor                  │
├─────────────────────────────────┤
│ [11] Rate usage records         │
│ • Apply pricing plans           │
│ • Calculate tiered charges      │
│ • Check quotas/limits           │
│ [12] Update records             │
│ • status = 'RATED'              │
│ • rated_amount = calculated     │
│ [13] Create accumulators        │
│ • Monthly voice minutes         │
│ • Data GB consumed              │
└──────────┬──────────────────────┘
           │
           │ [14] Rating complete
           │ 50,000 records now RATED
           ▼

Processing Time: 10-60 minutes for 50,000 CDRs
Rate: ~1000 CDRs/second

┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: BILLING (Direct Service Call - No Queue)                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│ batch-process       │
│ (End of Month)      │
├─────────────────────┤
│ [15] Monthly billing│
│ run                 │
└──────────┬──────────┘
           │ [16] Direct GraphQL call
           ▼
┌─────────────────────────────────┐
│ service-billing                 │
├─────────────────────────────────┤
│ [17] Query RATED usage          │
│ • WHERE billed = false          │
│ [18] Create charges             │
│ • Aggregate by account          │
│ • Apply discounts               │
│ [19] Update usage               │
│ • billed = true                 │
└──────────┬──────────────────────┘
           │
           │ [20] Invoicing
           ▼
┌─────────────────────┐
│ service-invoice     │
│ • Generate invoice  │
│ • Create PDF        │
│ • Email customer    │
└─────────────────────┘

Total End-to-End Time:
CDR Creation → Customer Invoice: 1-4 hours (depending on batch schedules)
```

**Key Insights**:
- **MEDIATION Queue**: Low message volume (10-50/day), but each message triggers processing of 1,000s-100,000s of CDRs
- **USAGE Queue**: Medium volume (24-72 messages/day for hourly batches), each processes thousands of records
- **No Queue for Billing**: Direct service invocation for billing cycle (scheduled job)

### 4.3 Bulk Operations Flow (BULK Queue)

**Use Cases**: Invoice regeneration, payment allocation, credit/debit notes, adjustments

```
┌─────────────────────────────────────────────────────────────────────────┐
│ BULK OPERATIONS PATTERN                                                  │
└─────────────────────────────────────────────────────────────────────────┘

User/System (UI or API)
  │ [1] Bulk operation request
  │ Example: "Regenerate invoices for 500 accounts"
  ▼
┌─────────────────────┐
│ service-proxy       │
│ BulkProcessService  │
├─────────────────────┤
│ [2] Create bulk job │
│ • Generate job ID   │
│ • Validate payload  │
│ [3] Split into      │
│     chunks (100)    │
└──────────┬──────────┘
           │ [4] Send messages (5 chunks)
           ▼
     ┌──────────┐
     │   BULK   │
     │  Queue   │
     └─────┬────┘
           │ [5] Consume (parallel)
           ▼
┌─────────────────────────────────────────┐
│ jobs-common                             │
│ BulkProcessor (3 consumers)             │
├─────────────────────────────────────────┤
│ Consumer 1 │ Consumer 2 │ Consumer 3   │
│ Chunk 1    │ Chunk 2    │ Chunk 3      │
│ 100 ops    │ 100 ops    │ 100 ops      │
└──────────┬──────────────┴──────────────┘
           │ [6] Execute operations
           │ • REGENERATE_INVOICE → service-invoice
           │ • ALLOCATE_PAYMENT → service-payment
           │ • CREATE_ADJUSTMENT → service-billing
           ▼
┌─────────────────────────────────┐
│ Core Services                   │
│ • service-invoice               │
│ • service-payment               │
│ • service-billing               │
└──────────┬──────────────────────┘
           │
           │ [7] Update bulk_action_stats
           │ • Success count
           │ • Failure count
           │ • Completed percentage
           ▼

Processing Time:
500 operations in chunks of 100 = 5 messages
With 3 consumers: ~2-5 minutes total
```

**Supported Bulk Operations**:
```groovy
enum BulkApiName {
    // Invoice operations
    RESEND_INVOICE_TO_VENDOR,
    REGENERATE_INVOICE,
    CANCEL_INVOICE,
    
    // Payment operations
    REVERSE_PAYMENT,
    ALLOCATE_PAYMENT,
    PROCESS_BANK_FILE,
    
    // Credit/Debit notes
    CREATE_CREDIT_NOTE,
    CREATE_DEBIT_NOTE,
    
    // Adjustments
    CREATE_ADJUSTMENT,
    REVERSE_ADJUSTMENT
}
```

**BULK Message Format**:
```json
{
  "id": "BULK-2024-02-11-001",
  "apiName": "REGENERATE_INVOICE",
  "payloads": [
    {
      "invoiceId": "INV-2024-001",
      "reason": "Tax calculation correction"
    },
    {
      "invoiceId": "INV-2024-002",
      "reason": "Tax calculation correction"
    }
    // ... up to 100 per message
  ],
  "createdBy": "admin@embrix.com",
  "createdDate": "2024-02-11T10:30:00Z"
}
```

---

## 5. Error Handling & Retry Mechanisms

### 5.1 Exception Types

**Two Categories of Exceptions**:

```groovy
// NonRetryableException - Business validation failures
class NonRetryableException extends RuntimeException {
    String errorCode
    Map<String, Object> details
    
    NonRetryableException(String message, String errorCode) {
        super(message)
        this.errorCode = errorCode
    }
}

// Examples:
// • Account not found
// • Duplicate order
// • Invalid product code
// • Insufficient balance
// • Business rule violation

// RetryableException - Transient failures
class RetryableException extends RuntimeException {
    RetryableException(String message, Throwable cause) {
        super(message, cause)
    }
}

// Examples:
// • Database connection timeout
// • External API timeout
// • Network error
// • Temporary service unavailable
```

### 5.2 Retry Configuration

**Exponential Backoff with Jitter**:

```groovy
// Retry policy configuration
@Configuration
class JmsRetryConfig {
    
    @Bean
    DefaultErrorHandler errorHandler() {
        def errorHandler = new DefaultErrorHandler()
        
        errorHandler.setMaximumRedeliveries(7)
        errorHandler.setRedeliveryDelay(250)  // Initial delay: 250ms
        errorHandler.setBackOffMultiplier(1.5)  // Exponential multiplier
        errorHandler.setUseExponentialBackOff(true)
        errorHandler.setMaximumRedeliveryDelay(60000)  // Max delay: 60s
        errorHandler.setUseCollisionAvoidance(true)  // Add jitter
        
        return errorHandler
    }
}
```

**Retry Schedule**:
```
Attempt 1: Immediate (0ms)
Attempt 2: 250ms
Attempt 3: 375ms (250 * 1.5)
Attempt 4: 562ms (375 * 1.5)
Attempt 5: 843ms (562 * 1.5)
Attempt 6: 1264ms (843 * 1.5)
Attempt 7: 1896ms (1264 * 1.5)
Attempt 8: 2841ms (1896 * 1.5) - Final attempt

Total retry time: ~8 seconds
```

### 5.3 Dead Letter Queue (DLQ)

**Messages that fail after max retries → DLQ**:

```groovy
@Component
class OmsReceiver {
    
    @JmsListener(destination = "OMS", containerFactory = "jmsFactory")
    void receiveMessage(String message) {
        try {
            processOrder(message)
        } catch (NonRetryableException e) {
            log.error("Business validation failed: ${e.message}")
            // Send to OMS_ERROR for manual review
            jmsTemplate.convertAndSend("OMS_ERROR", [
                originalMessage: message,
                errorMessage: e.message,
                errorCode: e.errorCode,
                timestamp: new Date()
            ])
            // ACK message (do not retry)
        } catch (Exception e) {
            log.error("Transient error: ${e.message}")
            // Throw RetryableException to trigger retry
            throw new RetryableException("Failed to process order", e)
        }
    }
}
```

**DLQ Monitoring**:
```bash
# View DLQ messages in ActiveMQ Console
http://localhost:8161/admin/browse.jsp?JMSDestination=ActiveMQ.DLQ

# Programmatically reprocess DLQ messages
@Component
class DLQReprocessor {
    
    @Scheduled(cron = "0 0 */6 * * *")  // Every 6 hours
    void checkDLQ() {
        def dlqMessages = browseQueue("ActiveMQ.DLQ")
        
        dlqMessages.each { message ->
            if (shouldRetry(message)) {
                moveToOriginalQueue(message)
            } else {
                createIncident(message)  // Alert ops team
            }
        }
    }
}
```

---

## 6. Message Formats & Examples

### 6.1 OMS Message Format

**Order Creation**:
```json
{
  "object_type": "ORDER",
  "account_id": "ACC-1001",
  "user_id": "USR-501",
  "order_type": "NEW",
  "services": [
    {
      "action": "ADD",
      "product_code": "INTERNET_100",
      "quantity": 1,
      "pricing": {
        "monthly_recurring_charge": 50.00,
        "one_time_charge": 99.00,
        "currency": "USD"
      },
      "customization": {
        "installation_date": "2024-02-20",
        "ont_serial": "ONT123456",
        "service_address": {
          "street": "456 Service Road",
          "city": "Mexico City",
          "state": "CDMX",
          "postal_code": "01000"
        }
      }
    }
  ],
  "extended_data": {
    "sales_rep": "John Doe",
    "campaign_code": "PROMO2024",
    "notes": "Customer requested morning installation"
  },
  "submission_timestamp": "2024-02-11T10:45:00Z",
  "source_system": "Salesforce",
  "correlation_id": "SF-ORD-20240211-12345"
}
```

**Account Update**:
```json
{
  "object_type": "ACCOUNT",
  "account_id": "ACC-1001",
  "action": "UPDATE",
  "updates": {
    "billing_address": {
      "street": "789 New Street",
      "city": "Guadalajara",
      "state": "Jalisco",
      "postal_code": "44100"
    },
    "payment_method": {
      "type": "CREDIT_CARD",
      "token": "tok_visa_1234",
      "is_default": true
    }
  },
  "submission_timestamp": "2024-02-11T11:00:00Z"
}
```

### 6.2 PROVISIONING_RESPONSE Message

**Successful Provisioning Callback**:
```json
{
  "order_id": "ORD-20240211-001",
  "provisioning_id": "PROV-12345",
  "status": "COMPLETED",
  "completion_timestamp": "2024-02-11T11:30:00Z",
  "network_details": {
    "ont_serial": "ONT123456",
    "olt": "OLT-ZONE1-01",
    "port": "1/1/5",
    "vlan": 100,
    "ip_address": "10.1.1.150",
    "gateway": "10.1.1.1",
    "speed_profile": "100M_DOWN_20M_UP",
    "service_activation_date": "2024-02-11T11:30:00Z"
  },
  "vendor": "Nokia",
  "vendor_reference": "NOKIA-ACT-789456"
}
```

**Failed Provisioning**:
```json
{
  "order_id": "ORD-20240211-002",
  "provisioning_id": "PROV-12346",
  "status": "FAILED",
  "failure_timestamp": "2024-02-11T12:00:00Z",
  "error": {
    "code": "PORT_UNAVAILABLE",
    "message": "No available ports on OLT-ZONE2-03",
    "details": {
      "olt": "OLT-ZONE2-03",
      "requested_port": "1/1/8",
      "available_ports": []
    }
  },
  "vendor": "Nokia",
  "retry_recommended": false
}
```

### 6.3 MEDIATION Message

**CDR File Processing Request**:
```json
{
  "service_type": "VOICE",
  "file_name": "mcm_voice_cdr_20240211.csv",
  "tenant_name": "coopeg-prd",
  "file_location": "sftp://cdr.mcm.com/outbound/mcm_voice_cdr_20240211.csv",
  "file_size_bytes": 52428800,
  "record_count_estimate": 150000,
  "generation_timestamp": "2024-02-11T00:00:00Z",
  "processing_priority": "NORMAL",
  "vendor": "MCM",
  "vendor_format": "MCM_VOICE_V2"
}
```

### 6.4 USAGE Message

**Usage Rating Batch**:
```json
{
  "batch_id": "USAGE-BATCH-20240211-001",
  "usage_record_ids": [
    "USG-001",
    "USG-002",
    "USG-003"
    // ... up to 10,000 IDs
  ],
  "rating_date": "2024-02-11",
  "account_ids": ["ACC-1001", "ACC-1002"],
  "service_type": "VOICE",
  "priority": "HIGH",
  "initiated_by": "batch-process",
  "submission_timestamp": "2024-02-11T01:00:00Z"
}
```

**Re-rating Request**:
```json
{
  "reprocess_type": "RE_RATE",
  "usage_record_ids": ["USG-1001", "USG-1002"],
  "reason": "Corrected pricing plan",
  "new_rating_plan_id": "PLAN-2024-NEW",
  "initiated_by": "admin@embrix.com",
  "submission_timestamp": "2024-02-11T14:00:00Z"
}
```

### 6.5 BULK Message

**Invoice Regeneration**:
```json
{
  "id": "BULK-2024-02-11-005",
  "api_name": "REGENERATE_INVOICE",
  "payloads": [
    {
      "invoice_id": "INV-2024-001",
      "account_id": "ACC-1001",
      "reason": "Tax calculation correction",
      "regenerate_pdf": true,
      "send_notification": false
    },
    {
      "invoice_id": "INV-2024-002",
      "account_id": "ACC-1002",
      "reason": "Tax calculation correction",
      "regenerate_pdf": true,
      "send_notification": false
    }
    // ... up to 100
  ],
  "total_count": 2,
  "created_by": "admin@embrix.com",
  "created_date": "2024-02-11T15:30:00Z",
  "callback_url": "https://api.embrix.com/bulk/status/BULK-2024-02-11-005"
}
```

---

## 7. Performance & Monitoring

### 7.1 Key Metrics

**Monitor in ActiveMQ Console** (`http://localhost:8161/admin`):

| Metric | Description | Healthy Range | Alert Threshold |
|--------|-------------|---------------|-----------------|
| **Queue Depth** | Messages waiting | 0-100 | > 1000 |
| **Enqueue Rate** | Messages/second added | Varies by queue | - |
| **Dequeue Rate** | Messages/second processed | Should match enqueue | < 50% of enqueue |
| **Consumer Count** | Active consumers | 1-10 per queue | 0 (no consumers) |
| **Average Enqueue Time** | Time to add message | < 10ms | > 100ms |
| **Memory Usage** | Broker memory | < 70% | > 90% |
| **Store Percent** | Disk usage | < 70% | > 90% |

### 7.2 Monitoring Queries

**View Queue Metrics**:
```bash
# Using ActiveMQ API
curl -u admin:admin \
  http://localhost:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=OMS

# Response includes:
# {
#   "value": {
#     "QueueSize": 23,
#     "EnqueueCount": 15234,
#     "DequeueCount": 15211,
#     "ConsumerCount": 3,
#     "AverageEnqueueTime": 5.2,
#     "MemoryPercentUsage": 12
#   }
# }
```

**Grafana Dashboard Queries** (Prometheus metrics):
```promql
# Queue depth over time
activemq_queue_size{queue="OMS"}

# Message throughput
rate(activemq_enqueue_count{queue="OMS"}[5m])

# Consumer lag (messages not being processed fast enough)
activemq_queue_size > 500

# Alert on no consumers
activemq_consumer_count{queue="OMS"} == 0
```

### 7.3 Performance Tuning

**Concurrent Consumers**:
```yaml
# Increase concurrent consumers for high-volume queues
camel:
  component:
    activemq:
      concurrent-consumers: 5      # Start with 5
      max-concurrent-consumers: 20  # Scale up to 20 under load
```

**Prefetch Limit** (how many messages consumer fetches at once):
```groovy
@Bean
ConnectionFactory connectionFactory() {
    def factory = new ActiveMQConnectionFactory()
    factory.brokerURL = "tcp://localhost:61616"
    factory.prefetchPolicy.queuePrefetch = 100  // Fetch 100 messages at a time
    return factory
}
```

**Message Persistence**:
```groovy
// For non-critical messages, use non-persistent mode (faster)
jmsTemplate.deliveryMode = DeliveryMode.NON_PERSISTENT

// For critical messages, use persistent mode (slower, but safe)
jmsTemplate.deliveryMode = DeliveryMode.PERSISTENT  // Default
```

---

## 8. Development Guide

### 8.1 Creating a Queue Consumer

**Step 1: Define Message DTO**:
```groovy
// dto/MyMessage.groovy
class MyMessage {
    String id
    String accountId
    String operation
    Map<String, Object> data
    Date timestamp
}
```

**Step 2: Create Consumer**:
```groovy
// consumer/MyQueueReceiver.groovy
@Component
class MyQueueReceiver {
    
    @Autowired
    MyProcessingService processingService
    
    @JmsListener(destination = "MY_QUEUE", containerFactory = "jmsListenerContainerFactory")
    void receiveMessage(String message) {
        log.info("Received message: ${message}")
        
        try {
            // Parse message
            def myMessage = parseMessage(message)
            
            // Validate
            validateMessage(myMessage)
            
            // Process
            processingService.process(myMessage)
            
            log.info("Successfully processed message ${myMessage.id}")
            
        } catch (NonRetryableException e) {
            log.error("Business validation failed: ${e.message}")
            sendToErrorQueue(message, e)
            // Do not throw - message will be ACKed
            
        } catch (Exception e) {
            log.error("Transient error processing message: ${e.message}", e)
            // Throw to trigger retry
            throw new RetryableException("Failed to process message", e)
        }
    }
    
    private MyMessage parseMessage(String json) {
        try {
            return new JsonSlurper().parseText(json) as MyMessage
        } catch (Exception e) {
            throw new NonRetryableException("Invalid JSON format", "INVALID_MESSAGE")
        }
    }
    
    private void validateMessage(MyMessage message) {
        if (!message.accountId) {
            throw new NonRetryableException("Missing accountId", "MISSING_FIELD")
        }
        // Additional validations...
    }
    
    private void sendToErrorQueue(String originalMessage, Exception error) {
        jmsTemplate.convertAndSend("MY_QUEUE_ERROR", [
            originalMessage: originalMessage,
            errorMessage: error.message,
            errorCode: error.errorCode,
            timestamp: new Date()
        ])
    }
}
```

**Step 3: Configure Listener Factory**:
```groovy
// config/JmsConfig.groovy
@Configuration
class JmsConfig {
    
    @Bean
    JmsListenerContainerFactory<?> jmsListenerContainerFactory(
        ConnectionFactory connectionFactory,
        DefaultErrorHandler errorHandler) {
        
        def factory = new DefaultJmsListenerContainerFactory()
        factory.setConnectionFactory(connectionFactory)
        factory.setErrorHandler(errorHandler)
        factory.setConcurrency("3-10")  // Min 3, max 10 consumers
        factory.setSessionTransacted(true)
        return factory
    }
}
```

### 8.2 Sending Messages

**Producer Example**:
```groovy
@Component
class MyQueueProducer {
    
    @Autowired
    JmsTemplate jmsTemplate
    
    void sendMessage(MyMessage message) {
        def json = JsonOutput.toJson(message)
        
        jmsTemplate.convertAndSend("MY_QUEUE", json) { messagePostProcessor ->
            // Add custom headers
            messagePostProcessor.setStringProperty("correlationId", message.id)
            messagePostProcessor.setStringProperty("messageType", "MY_MESSAGE")
            messagePostProcessor.setIntProperty("priority", 5)
            return messagePostProcessor
        }
        
        log.info("Sent message ${message.id} to MY_QUEUE")
    }
    
    void sendBatch(List<MyMessage> messages) {
        jmsTemplate.execute { session, messageProducer ->
            messages.each { message ->
                def json = JsonOutput.toJson(message)
                def textMessage = session.createTextMessage(json)
                messageProducer.send(textMessage)
            }
        }
        
        log.info("Sent ${messages.size()} messages to MY_QUEUE")
    }
}
```

### 8.3 Testing Queue Flows

**Integration Test Example**:
```groovy
@SpringBootTest
@TestPropertySource(locations = "classpath:application-test.properties")
class MyQueueIntegrationTest {
    
    @Autowired
    MyQueueProducer producer
    
    @Autowired
    MyRepository repository
    
    @Autowired
    JmsTemplate jmsTemplate
    
    @Test
    void testMessageFlow() {
        // Given
        def message = new MyMessage(
            id: "TEST-001",
            accountId: "ACC-TEST",
            operation: "CREATE",
            data: [key: "value"]
        )
        
        // When
        producer.sendMessage(message)
        
        // Wait for async processing
        Thread.sleep(2000)
        
        // Then
        def result = repository.findById("TEST-001")
        assert result.isPresent()
        assert result.get().status == "PROCESSED"
    }
    
    @Test
    void testErrorHandling() {
        // Given - invalid message
        def invalidMessage = new MyMessage(
            id: "TEST-002",
            accountId: null,  // Missing required field
            operation: "CREATE"
        )
        
        // When
        producer.sendMessage(invalidMessage)
        
        // Wait
        Thread.sleep(2000)
        
        // Then - should be in error queue
        def errorMessage = jmsTemplate.receiveAndConvert("MY_QUEUE_ERROR")
        assert errorMessage != null
        assert errorMessage.errorCode == "MISSING_FIELD"
    }
}
```

---

## 9. Troubleshooting

### 9.1 Common Issues

#### Issue 1: High Queue Depth (Messages Piling Up)

**Symptoms**:
- Queue depth increasing
- Messages not being consumed
- System slowdown

**Diagnosis**:
```bash
# Check consumer count
curl -u admin:admin http://localhost:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=OMS | jq '.value.ConsumerCount'

# Check if consumers are stuck
# Look for repeated errors in logs
tail -f service-mediation/logs/application.log | grep ERROR
```

**Possible Causes & Solutions**:

| Cause | Solution |
|-------|----------|
| **No consumers running** | Restart service: `kubectl rollout restart deployment/service-mediation` |
| **Consumer processing too slow** | Increase concurrent consumers in config |
| **Database connection pool exhausted** | Increase pool size or optimize queries |
| **External API timeouts** | Implement circuit breaker, increase timeouts |
| **Messages causing exceptions** | Check error logs, fix business logic bug |

#### Issue 2: Messages Going to DLQ

**Symptoms**:
- Messages in ActiveMQ.DLQ
- Errors in logs after max retries

**Diagnosis**:
```bash
# Browse DLQ
http://localhost:8161/admin/browse.jsp?JMSDestination=ActiveMQ.DLQ

# Check message details
curl -u admin:admin http://localhost:8161/api/jolokia/exec/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=ActiveMQ.DLQ/browse | jq '.'
```

**Solutions**:
1. **Identify root cause** from error logs
2. **Fix business logic** or data issue
3. **Reprocess messages**:
```groovy
@Component
class DLQReprocessor {
    
    @Autowired
    JmsTemplate jmsTemplate
    
    void reprocessDLQ(String originalQueue) {
        def dlqMessages = browseDLQ()
        
        dlqMessages.each { message ->
            // Move back to original queue
            jmsTemplate.convertAndSend(originalQueue, message.text)
        }
    }
}
```

#### Issue 3: Duplicate Messages

**Symptoms**:
- Same order processed twice
- Duplicate database records

**Cause**: Message redelivery after consumer crash before ACK

**Solution**: Implement idempotency

```groovy
@Component
class IdempotentOmsReceiver {
    
    @Autowired
    ProcessedMessageRepository processedRepo
    
    @JmsListener(destination = "OMS")
    @Transactional
    void receiveMessage(String message, @Header("JMSMessageID") String messageId) {
        
        // Check if already processed
        if (processedRepo.existsById(messageId)) {
            log.warn("Message ${messageId} already processed, skipping")
            return  // ACK without reprocessing
        }
        
        // Process message
        processOrder(message)
        
        // Mark as processed
        processedRepo.save(new ProcessedMessage(
            id: messageId,
            processedAt: new Date()
        ))
    }
}
```

---

## 10. Best Practices

### 10.1 Message Design

✅ **DO**:
- Include correlation IDs for traceability
- Add timestamps (UTC)
- Use JSON for complex messages
- Include version field for schema evolution
- Keep messages < 1 MB

❌ **DON'T**:
- Send sensitive data unencrypted
- Include large binary data (use S3 reference instead)
- Use ambiguous field names
- Omit error context

### 10.2 Consumer Design

✅ **DO**:
- Make consumers idempotent
- Use transactional message processing
- Log correlation IDs
- Implement proper error handling (Retryable vs NonRetryable)
- Monitor consumer lag

❌ **DON'T**:
- Block consumer thread with long operations
- Swallow exceptions silently
- Retry non-retryable errors
- Process messages out of order when order matters

### 10.3 Performance Optimization

1. **Batch Processing**: Process multiple records per message
2. **Concurrent Consumers**: Scale horizontally
3. **Prefetch**: Fetch multiple messages at once
4. **Compression**: For large messages
5. **Partitioning**: Separate queues by tenant or priority

---

## Summary & Next Steps

### What We Covered

✅ **ActiveMQ Architecture**: Amazon MQ deployment, local setup  
✅ **Queue Inventory**: All 10+ production queues documented  
✅ **Message Patterns**: Order-to-cash, usage pipeline, bulk operations  
✅ **Error Handling**: Retry mechanisms, DLQ management  
✅ **Message Formats**: Complete examples for all queue types  
✅ **Monitoring**: Key metrics and alerting  
✅ **Development Guide**: How to create consumers and producers  
✅ **Troubleshooting**: Common issues and solutions

### For Developers

- **Understand async flows** before implementing new features
- **Test with local ActiveMQ** using Docker
- **Monitor queue health** in production
- **Implement idempotency** for all consumers
- **Use proper exception types** (Retryable vs NonRetryable)

### Next Steps

1. **Set up local ActiveMQ** with Docker
2. **Explore ActiveMQ Console** (http://localhost:8161)
3. **Test message flows** with integration tests
4. **Monitor production queues** with Grafana
5. **Implement new queue consumer** following patterns

---

**Master asynchronous messaging for scalable Embrix O2X architecture! 📨**
