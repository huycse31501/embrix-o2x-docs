# Embrix O2X Platform - Infrastructure & Operations Guide

**Version**: 3.1.9-SNAPSHOT  
**Last Updated**: February 2026  
**Purpose**: Complete guide to infrastructure, deployment, and operational procedures

---

## Table of Contents

1. [Infrastructure Overview](#infrastructure-overview)
2. [AWS Architecture](#aws-architecture)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Service Configuration](#service-configuration)
5. [Secrets Management](#secrets-management)
6. [Monitoring & Observability](#monitoring--observability)
7. [Message Queue Operations](#message-queue-operations)
8. [Database Operations](#database-operations)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Operational Procedures](#operational-procedures)

---

## Infrastructure Overview

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Compute** | Kubernetes (EKS) | 1.27+ | Container orchestration |
| **Database** | PostgreSQL (RDS) | 10.5+ | Primary datastore |
| **Cache** | Redis (ElastiCache) | 6.2+ | Session/cache storage |
| **Messaging** | ActiveMQ (Amazon MQ) | 5.15.9 | Message broker |
| **Secrets** | HashiCorp Vault | Latest | Secrets management |
| **Storage** | AWS S3 | N/A | Object storage |
| **Load Balancer** | AWS ALB | N/A | Application load balancing |
| **DNS** | Route 53 | N/A | DNS management |
| **Monitoring** | Prometheus + Grafana | Latest | Metrics and dashboards |
| **Logging** | ELK Stack | Latest | Log aggregation |

### Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     ROUTE 53 (DNS)                               │
│  selfcare.urbanos.com → ALB                                     │
│  api.urbanos.com → ALB                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│              APPLICATION LOAD BALANCER (ALB)                     │
│  SSL Termination, Path-based routing                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                 KUBERNETES CLUSTER (EKS)                         │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Namespace: urbanos                                      │   │
│  │                                                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │   │
│  │  │ crm_gateway  │  │service-billing│ │service-invoice│ │   │
│  │  │  (2 pods)    │  │  (2 pods)     │ │  (2 pods)     │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │   │
│  │                                                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │   │
│  │  │service-usage │  │service-payment│ │service-revenue│ │   │
│  │  │  (2 pods)    │  │  (2 pods)     │ │  (2 pods)     │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │   │
│  │                                                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │   │
│  │  │provision_gwy │  │payment_gwy   │  │tax_gateway   │ │   │
│  │  │  (2 pods)    │  │  (2 pods)     │ │  (2 pods)     │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     DATA & MESSAGING LAYER                       │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ RDS Postgres │  │  ElastiCache │  │  Amazon MQ   │         │
│  │coredb-urbanos│  │    (Redis)   │  │  (ActiveMQ)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  S3 Buckets  │  │    Vault     │                            │
│  │ (Invoices)   │  │  (Secrets)   │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  MONITORING & LOGGING                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Prometheus  │  │   Grafana    │  │  ELK Stack   │         │
│  │  (Metrics)   │  │ (Dashboards) │  │   (Logs)     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## AWS Architecture

### AWS Services Used

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **EKS** | Kubernetes cluster | Multi-AZ, Auto-scaling node groups |
| **RDS** | PostgreSQL databases | Multi-AZ, Automated backups |
| **ElastiCache** | Redis cache | Cluster mode, Multi-AZ |
| **Amazon MQ** | ActiveMQ broker | Active/Standby, Multi-AZ |
| **S3** | Object storage | Versioning enabled, Lifecycle policies |
| **ALB** | Load balancing | SSL termination, Path-based routing |
| **Route 53** | DNS management | Health checks, Failover routing |
| **CloudWatch** | Monitoring | Metrics, Alarms, Logs |
| **IAM** | Access management | Role-based access |
| **VPC** | Networking | Public/private subnets, NAT gateways |

### Network Architecture

**VPC Configuration**:
```
VPC: 10.0.0.0/16

Public Subnets (ALB, NAT Gateway):
  - 10.0.1.0/24 (us-east-1a)
  - 10.0.2.0/24 (us-east-1b)

Private Subnets (EKS nodes, RDS, ElastiCache):
  - 10.0.10.0/24 (us-east-1a)
  - 10.0.11.0/24 (us-east-1b)
  - 10.0.20.0/24 (us-east-1a) - Database subnet
  - 10.0.21.0/24 (us-east-1b) - Database subnet
```

**Security Groups**:
- **ALB SG**: 80/443 from 0.0.0.0/0
- **EKS Node SG**: 8080-8100 from ALB SG, All traffic within SG
- **RDS SG**: 5432 from EKS Node SG
- **ElastiCache SG**: 6379 from EKS Node SG
- **Amazon MQ SG**: 61617 from EKS Node SG

---

## Kubernetes Deployment

### Cluster Configuration

**EKS Cluster**: `embrix-eks-prod`

**Node Groups**:
| Node Group | Instance Type | Min | Max | Desired |
|------------|---------------|-----|-----|---------|
| **core-services** | m5.xlarge | 2 | 10 | 4 |
| **gateways** | m5.large | 2 | 8 | 3 |
| **batch-jobs** | m5.2xlarge | 1 | 5 | 1 |

**Kubernetes Version**: 1.27

### Namespace Organization

**Tenant Namespaces**:
- `urbanos` - Urbanos tenant
- `coopeg-prd` - CoopeG production
- `coopeg-sbx` - CoopeG sandbox
- `demo` - Demo tenant
- `shm` - SHM tenant

**Shared Namespaces**:
- `monitoring` - Prometheus, Grafana
- `logging` - ELK Stack
- `ingress-nginx` - Ingress controller

### Deployment Manifest Example

**Service Deployment** (`service-billing`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: urbanos-service-billing
  namespace: urbanos
  labels:
    app: service-billing
    tenant: urbanos
    version: 3.1.9
spec:
  replicas: 2
  selector:
    matchLabels:
      app: service-billing
      tenant: urbanos
  template:
    metadata:
      labels:
        app: service-billing
        tenant: urbanos
    spec:
      containers:
      - name: service-billing
        image: embrix/service-billing:3.1.9
        ports:
        - containerPort: 8090
          name: http
        env:
        - name: TENANT_ID
          value: "TIDLT-100005"
        - name: SPRING_PROFILES_ACTIVE
          value: "prod"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: urbanos-db-secret
              key: url
        - name: DATABASE_USERNAME
          valueFrom:
            secretKeyRef:
              name: urbanos-db-secret
              key: username
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: urbanos-db-secret
              key: password
        - name: VAULT_URI
          value: "http://vault.default.svc.cluster.local:8200"
        - name: VAULT_TOKEN
          valueFrom:
            secretKeyRef:
              name: vault-token
              key: token
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 8090
          initialDelaySeconds: 120
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 8090
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
---
apiVersion: v1
kind: Service
metadata:
  name: urbanos-service-billing
  namespace: urbanos
spec:
  selector:
    app: service-billing
    tenant: urbanos
  ports:
  - port: 8090
    targetPort: 8090
    name: http
  type: ClusterIP
```

### Horizontal Pod Autoscaler (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: urbanos-service-billing-hpa
  namespace: urbanos
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: urbanos-service-billing
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 1
        periodSeconds: 60
```

### Ingress Configuration

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: urbanos-ingress
  namespace: urbanos
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:123456789012:certificate/xxx
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
spec:
  rules:
  - host: api.urbanos.com
    http:
      paths:
      - path: /graphql
        pathType: Prefix
        backend:
          service:
            name: urbanos-crm-gateway
            port:
              number: 8080
      - path: /api/v1/tax
        pathType: Prefix
        backend:
          service:
            name: urbanos-tax-gateway
            port:
              number: 8082
  - host: selfcare.urbanos.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: urbanos-selfcare-ui
            port:
              number: 80
```

---

## Service Configuration

### Environment Variables

**Common Environment Variables** (All Services):
```bash
# Tenant Configuration
TENANT_ID=TIDLT-100005
SPRING_PROFILES_ACTIVE=prod

# Logging
LOGS_DIR=/var/log/embrix
LOG_LEVEL=INFO

# Vault
VAULT_URI=http://vault.default.svc.cluster.local:8200
VAULT_TOKEN=<from Kubernetes Secret>

# Database (from Vault via Spring Cloud Vault)
# These are loaded automatically from Vault path: secret/ctg-oms/prod

# Redis Cache
REDIS_HOST=master.prod-cache-rg.8fxuvv.use1.cache.amazonaws.com
REDIS_PORT=6379

# ActiveMQ
AMQ_BROKER_URL=ssl://broker.mq.us-east-1.amazonaws.com:61617
# AMQ credentials loaded from Vault

# AWS S3
AWS_S3_PUBLICURL=https://s3.amazonaws.com/embrix-public-prod
AWS_REGION=us-east-1

# Gateway URLs
TAX_GATEWAY_URL=http://urbanos-tax-gateway.urbanos.svc.cluster.local:8082
PAYMENT_GATEWAY_URL=http://urbanos-payment-gateway.urbanos.svc.cluster.local:8083
FINANCE_GATEWAY_URL=http://urbanos-finance-gateway.urbanos.svc.cluster.local:8084
PROVISIONING_GATEWAY_URL=http://urbanos-provision-gateway.urbanos.svc.cluster.local:8081
```

**Service-Specific Variables**:

**crm_gateway**:
```bash
SERVER_PORT=8080
OAUTH2_ENABLED=true
JWT_SECRET=<from Vault>
```

**service-billing**:
```bash
SERVER_PORT=8090
BILLING_CYCLE_DAY=1
```

**service-invoice**:
```bash
SERVER_PORT=8091
INVOICE_PDF_TEMPLATE=default
S3_INVOICE_BUCKET=embrix-invoices-prod
```

### Spring Boot Configuration

**application.yml** (Template):
```yaml
spring:
  application:
    name: service-billing
  profiles:
    active: ${SPRING_PROFILES_ACTIVE:dev}
  
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USERNAME}
    password: ${DATABASE_PASSWORD}
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 50
      minimum-idle: 10
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
  
  cloud:
    vault:
      uri: ${VAULT_URI}
      token: ${VAULT_TOKEN}
      generic:
        enabled: true
        application-name: ctg-oms
      kv:
        enabled: true
        backend: secret
        profile-separator: '/'
  
  jooq:
    sql-dialect: POSTGRES
  
  flyway:
    enabled: false  # Only in engine module

server:
  port: ${SERVER_PORT:8090}

management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics
  endpoint:
    health:
      show-details: when-authorized
  metrics:
    export:
      prometheus:
        enabled: true

logging:
  level:
    root: ${LOG_LEVEL:INFO}
    com.embrix: DEBUG
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n"
  file:
    name: ${LOGS_DIR:/var/log}/service-billing.log
    max-size: 100MB
    max-history: 30

tenant:
  id: ${TENANT_ID}

redis:
  host: ${REDIS_HOST}
  port: ${REDIS_PORT:6379}

activemq:
  broker-url: ${AMQ_BROKER_URL}
```

---

## Secrets Management

### HashiCorp Vault Setup

**Vault Paths**:
```
secret/
├── ctg-oms/
│   ├── dev/
│   │   ├── database
│   │   ├── activemq
│   │   ├── jwt
│   │   └── oauth2
│   ├── staging/
│   └── prod/
│       ├── database       # DB credentials per tenant
│       ├── activemq       # ActiveMQ credentials
│       ├── jwt            # JWT signing key
│       ├── oauth2         # OAuth2 client secrets
│       ├── slack          # Slack webhook URLs
│       └── external-apis  # Third-party API keys
└── tenant/
    ├── urbanos/
    │   ├── salesforce     # Salesforce OAuth
    │   ├── braintree      # Braintree credentials
    │   ├── avalara        # Avalara credentials
    │   └── quickbooks     # QuickBooks OAuth
    └── coopeg-prd/
        └── ...
```

**Example Secret Structure**:
```json
// secret/ctg-oms/prod/database
{
  "url": "jdbc:postgresql://embrix-rds-prod.xxx.rds.amazonaws.com:5432/coredb-urbanos?sslmode=require",
  "username": "omsadmin",
  "password": "SuperSecurePassword123!"
}

// secret/ctg-oms/prod/activemq
{
  "broker-url": "ssl://broker.mq.us-east-1.amazonaws.com:61617",
  "username": "embrix-prod",
  "password": "AnotherSecurePassword456!"
}

// secret/tenant/urbanos/salesforce
{
  "client-id": "3MVG9...",
  "client-secret": "ABC123...",
  "username": "integration@urbanos.com",
  "password": "Password789!",
  "security-token": "XYZ456..."
}
```

### Kubernetes Secret Management

**Creating Secrets**:
```bash
# Database secret
kubectl create secret generic urbanos-db-secret \
  --from-literal=url='jdbc:postgresql://...' \
  --from-literal=username='omsadmin' \
  --from-literal=password='SuperSecure123!' \
  --namespace=urbanos

# Vault token secret
kubectl create secret generic vault-token \
  --from-literal=token='s.XXXXXXXXXXXX' \
  --namespace=urbanos
```

**Sealed Secrets** (Encrypted in Git):
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: urbanos-db-secret
  namespace: urbanos
spec:
  encryptedData:
    url: AgBX7+... (encrypted)
    username: AgCQ3... (encrypted)
    password: AgDL9... (encrypted)
```

---

## Monitoring & Observability

### Prometheus Metrics

**Metrics Collected**:
- **System Metrics**: CPU, memory, disk, network
- **JVM Metrics**: Heap usage, GC pauses, thread count
- **HTTP Metrics**: Request rate, latency, error rate
- **Business Metrics**: Orders/hour, bills/day, invoices sent, payments processed
- **Database Metrics**: Connection pool usage, query latency
- **ActiveMQ Metrics**: Queue depth, message rate, consumer count

**Prometheus Configuration**:
```yaml
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)
    - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
      action: replace
      regex: ([^:]+)(?::\d+)?;(\d+)
      replacement: $1:$2
      target_label: __address__
    - source_labels: [__meta_kubernetes_namespace]
      action: replace
      target_label: kubernetes_namespace
    - source_labels: [__meta_kubernetes_pod_name]
      action: replace
      target_label: kubernetes_pod_name
```

**Pod Annotations for Scraping**:
```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8090"
    prometheus.io/path: "/actuator/prometheus"
```

### Grafana Dashboards

**Key Dashboards**:

1. **System Overview**
   - Total requests/sec across all services
   - Error rate (5xx responses)
   - Average response time
   - Pod CPU/Memory usage
   - Database connection pool status

2. **Business Metrics**
   - Orders created (last 24h, 7d, 30d)
   - Billing cycles executed
   - Invoices generated
   - Payments processed
   - Revenue recognized

3. **Service Health**
   - Per-service request rate
   - Per-service error rate
   - Per-service latency (p50, p95, p99)
   - Pod restart count
   - Liveness/readiness probe failures

4. **Infrastructure**
   - Node CPU/Memory usage
   - Disk usage
   - Network I/O
   - Database performance
   - Cache hit rate

**Alert Rules**:
```yaml
groups:
- name: embrix-alerts
  interval: 30s
  rules:
  - alert: HighErrorRate
    expr: rate(http_server_requests_seconds_count{status=~"5.."}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate on {{ $labels.job }}"
      description: "Error rate is {{ $value | humanizePercentage }}"
  
  - alert: HighMemoryUsage
    expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage on {{ $labels.pod }}"
      description: "Memory usage is {{ $value | humanizePercentage }}"
  
  - alert: PodRestarting
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Pod {{ $labels.pod }} is restarting"
      description: "Pod has restarted {{ $value }} times in the last 15 minutes"
```

### Logging

**ELK Stack Configuration**:

**Logback Configuration** (JSON logging):
```xml
<configuration>
  <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
      <customFields>{"service":"service-billing","tenant":"${TENANT_ID}"}</customFields>
    </encoder>
  </appender>
  
  <root level="INFO">
    <appender-ref ref="CONSOLE" />
  </root>
</configuration>
```

**Filebeat Configuration** (Ships logs to Elasticsearch):
```yaml
filebeat.inputs:
- type: container
  paths:
    - '/var/log/containers/*.log'
  processors:
  - add_kubernetes_metadata:
      host: ${NODE_NAME}
      matchers:
      - logs_path:
          logs_path: "/var/log/containers/"

output.elasticsearch:
  hosts: ["elasticsearch.logging.svc.cluster.local:9200"]
  index: "embrix-logs-%{+yyyy.MM.dd}"
```

**Kibana Queries**:
```
# Find errors in service-billing
service:service-billing AND level:ERROR

# Find slow queries
service:service-billing AND duration:>5000

# Find specific tenant logs
tenant:TIDLT-100005 AND level:ERROR

# Find order processing errors
message:"Order processing failed" AND orderId:*
```

---

## Message Queue Operations

### ActiveMQ Management

**Web Console**: `http://localhost:8161` (admin/admin)

**Queue Monitoring**:
```bash
# List all queues
curl -u admin:admin http://localhost:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=*

# Get queue depth
curl -u admin:admin http://localhost:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=OMS/QueueSize

# Purge queue
curl -u admin:admin -X POST http://localhost:8161/api/jolokia/exec/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=OMS/purge
```

**Queue Statistics**:
| Queue | Avg Depth | Peak Depth | Enqueue Rate | Dequeue Rate |
|-------|-----------|------------|--------------|--------------|
| OMS | 50 | 500 | 100/min | 95/min |
| MEDIATION | 1000 | 5000 | 500/min | 480/min |
| USAGE | 2000 | 10000 | 1000/min | 950/min |
| PROVISIONING_RESPONSE | 10 | 100 | 50/min | 50/min |

**Dead Letter Queue (DLQ) Handling**:
```groovy
// Check DLQ
def dlqMessages = dsl
    .select()
    .from(ACTIVEMQ_MESSAGES)
    .where(ACTIVEMQ_MESSAGES.DESTINATION.like('ActiveMQ.DLQ%'))
    .fetch()

// Replay message from DLQ
def message = consumeFromDLQ('OMS.DLQ')
// Fix issue
sendToQueue('OMS', message)
```

---

## Database Operations

### Daily Operations

**Connection Monitoring**:
```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Long-running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Kill long-running query
SELECT pg_terminate_backend(pid);
```

**Index Maintenance**:
```sql
-- Find missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
AND n_distinct > 100
ORDER BY abs(correlation) DESC;

-- Rebuild index
REINDEX INDEX CONCURRENTLY idx_invoice_account;

-- Analyze table
ANALYZE invoice;
```

**Partition Management**:
```bash
# Create next month's partition
psql -U omsadmin -d coredb-urbanos -c "
CREATE TABLE IF NOT EXISTS usage_record_2026_03
PARTITION OF usage_record
FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

CREATE INDEX idx_usage_account_2026_03 ON usage_record_2026_03(account_id);
CREATE INDEX idx_usage_subscription_2026_03 ON usage_record_2026_03(subscription_id);
"
```

### Backup & Restore

**Manual Backup**:
```bash
# Full backup
pg_dump -h localhost -U omsadmin -d coredb-urbanos \
  -F c -b -v -f backup-$(date +%Y%m%d).dump

# Schema-only backup
pg_dump -h localhost -U omsadmin -d coredb-urbanos \
  -s -F p -f schema-$(date +%Y%m%d).sql

# Specific table backup
pg_dump -h localhost -U omsadmin -d coredb-urbanos \
  -t core_billing.invoice -F c -f invoice-backup.dump
```

**Restore**:
```bash
# Full restore
pg_restore -h localhost -U omsadmin -d coredb-urbanos-new \
  -v backup-20260211.dump

# Table-only restore
pg_restore -h localhost -U omsadmin -d coredb-urbanos \
  -t invoice -v invoice-backup.dump
```

---

## CI/CD Pipeline

### GitLab CI/CD

**Pipeline Stages**:
1. **Build**: Compile Java/Groovy, run unit tests
2. **Test**: Integration tests, static code analysis
3. **Package**: Build Docker image
4. **Deploy**: Deploy to Kubernetes (dev/staging/prod)

**.gitlab-ci.yml**:
```yaml
stages:
  - build
  - test
  - package
  - deploy

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=$CI_PROJECT_DIR/.m2/repository"
  DOCKER_REGISTRY: "embrix.registry.com"
  IMAGE_NAME: "$DOCKER_REGISTRY/service-billing"

build:
  stage: build
  image: maven:3.8-openjdk-17
  script:
    - cd service-billing
    - mvn clean compile
  artifacts:
    paths:
      - service-billing/target/
    expire_in: 1 hour
  cache:
    paths:
      - .m2/repository

test:
  stage: test
  image: maven:3.8-openjdk-17
  script:
    - cd service-billing
    - mvn test
  artifacts:
    reports:
      junit: service-billing/target/surefire-reports/TEST-*.xml

package:
  stage: package
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $DOCKER_REGISTRY
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA -t $IMAGE_NAME:latest .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $IMAGE_NAME:latest
  only:
    - main
    - develop

deploy_dev:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context dev-cluster
    - kubectl set image deployment/urbanos-service-billing \
        service-billing=$IMAGE_NAME:$CI_COMMIT_SHA \
        -n urbanos
    - kubectl rollout status deployment/urbanos-service-billing -n urbanos
  environment:
    name: development
  only:
    - develop

deploy_prod:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context prod-cluster
    - kubectl set image deployment/urbanos-service-billing \
        service-billing=$IMAGE_NAME:$CI_COMMIT_SHA \
        -n urbanos
    - kubectl rollout status deployment/urbanos-service-billing -n urbanos
  environment:
    name: production
  when: manual
  only:
    - main
```

---

## Operational Procedures

### Service Deployment

**Standard Deployment Process**:
```bash
# 1. Build and push Docker image
docker build -t embrix/service-billing:3.1.9 .
docker push embrix/service-billing:3.1.9

# 2. Update Kubernetes deployment
kubectl set image deployment/urbanos-service-billing \
  service-billing=embrix/service-billing:3.1.9 \
  -n urbanos

# 3. Monitor rollout
kubectl rollout status deployment/urbanos-service-billing -n urbanos

# 4. Verify deployment
kubectl get pods -n urbanos | grep service-billing
kubectl logs -f urbanos-service-billing-xxx -n urbanos

# 5. Check health endpoint
curl http://urbanos-service-billing.urbanos.svc.cluster.local:8090/actuator/health
```

**Rollback**:
```bash
# Rollback to previous version
kubectl rollout undo deployment/urbanos-service-billing -n urbanos

# Rollback to specific revision
kubectl rollout history deployment/urbanos-service-billing -n urbanos
kubectl rollout undo deployment/urbanos-service-billing --to-revision=3 -n urbanos
```

### Scaling Operations

**Manual Scaling**:
```bash
# Scale up
kubectl scale deployment urbanos-service-billing --replicas=5 -n urbanos

# Scale down
kubectl scale deployment urbanos-service-billing --replicas=2 -n urbanos
```

**Auto-scaling Setup**:
```bash
# Enable HPA
kubectl autoscale deployment urbanos-service-billing \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n urbanos

# Check HPA status
kubectl get hpa -n urbanos
```

### Troubleshooting

**Pod Issues**:
```bash
# Check pod status
kubectl get pods -n urbanos

# Describe pod (events, conditions)
kubectl describe pod urbanos-service-billing-xxx -n urbanos

# View logs
kubectl logs urbanos-service-billing-xxx -n urbanos
kubectl logs urbanos-service-billing-xxx -n urbanos --previous  # Previous container

# Execute commands in pod
kubectl exec -it urbanos-service-billing-xxx -n urbanos -- /bin/bash

# Port-forward for local testing
kubectl port-forward urbanos-service-billing-xxx 8090:8090 -n urbanos
```

**Database Issues**:
```bash
# Check connection
psql -h embrix-rds-prod.xxx.rds.amazonaws.com -U omsadmin -d coredb-urbanos

# Check connection count
SELECT count(*) FROM pg_stat_activity WHERE datname='coredb-urbanos';

# Kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname='coredb-urbanos' 
AND state='idle' 
AND state_change < current_timestamp - INTERVAL '1 hour';
```

**ActiveMQ Issues**:
```bash
# Check queue depth
curl -u admin:admin http://activemq:8161/api/jolokia/read/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=OMS/QueueSize

# Purge stuck queue
curl -u admin:admin -X POST http://activemq:8161/api/jolokia/exec/org.apache.activemq:type=Broker,brokerName=localhost,destinationType=Queue,destinationName=OMS/purge
```

### Incident Response

**Severity Levels**:
- **P1 (Critical)**: System down, data loss, security breach
- **P2 (High)**: Major feature unavailable, performance degradation
- **P3 (Medium)**: Minor feature issue, workaround available
- **P4 (Low)**: Cosmetic issue, no functional impact

**Response Times**:
- P1: 15 minutes
- P2: 1 hour
- P3: 4 hours
- P4: Next business day

**Incident Procedure**:
1. **Detect**: Alert fires, user reports
2. **Assess**: Determine severity
3. **Communicate**: Notify stakeholders
4. **Investigate**: Check logs, metrics, traces
5. **Mitigate**: Implement temporary fix
6. **Resolve**: Deploy permanent fix
7. **Document**: Post-mortem analysis

---

## Summary

### Infrastructure Highlights

- **AWS-based**: EKS, RDS, ElastiCache, Amazon MQ, S3
- **Kubernetes orchestration**: Multi-tenant namespace isolation
- **Auto-scaling**: HPA for services, ASG for nodes
- **Multi-AZ**: High availability across availability zones
- **Monitoring**: Prometheus + Grafana + ELK Stack
- **Secrets**: HashiCorp Vault + Kubernetes Secrets
- **CI/CD**: GitLab CI with automated deployments

### Operational Practices

- **Zero-downtime deployments**: Rolling updates
- **Health checks**: Liveness and readiness probes
- **Resource limits**: CPU/memory limits per pod
- **Backup strategy**: Automated daily RDS snapshots
- **Incident response**: Defined severity levels and SLAs
- **Log aggregation**: Centralized logging via ELK

---

**For service-specific topology and call flows, see the Technical Deep Dive guide (`part2-technical-deep-dive.html`) and the Services & Development guide (`part3-services-development.html`).**
