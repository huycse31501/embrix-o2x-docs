# Embrix O2X Multi-Tenant Architecture & Onboarding Guide

## Document Information

- **Last Updated:** February 10, 2026
- **Version:** 1.0
- **Audience:** DevOps Engineers, Solutions Architects, Technical Account Managers
- **Purpose:** Complete reference for understanding and managing multi-tenant infrastructure

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Current Tenant Inventory](#current-tenant-inventory)
3. [Infrastructure Components](#infrastructure-components)
4. [Tenant Onboarding Process](#tenant-onboarding-process)
5. [Configuration Management](#configuration-management)
6. [Feature Customization](#feature-customization)
7. [Monitoring & Observability](#monitoring--observability)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Appendices](#appendices)

---

## Architecture Overview

### Multi-Tenancy Model

Embrix O2X implements **Deployment-Level Multi-Tenancy** (also known as "Instance-per-Tenant" or "Silo Model"), where each tenant receives dedicated application-layer resources while sharing underlying infrastructure.

### Key Characteristics

```
┌─────────────────────────────────────────────────────────────────────────┐
│ TENANT ISOLATION LAYER                                                   │
│                                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐ │
│  │ Tenant A            │  │ Tenant B            │  │ Tenant C         │ │
│  │ (urbanos)           │  │ (coopeg-prd)        │  │ (demo)           │ │
│  │                     │  │                     │  │                  │ │
│  │ ┌─────────────────┐ │  │ ┌─────────────────┐ │  │ ┌──────────────┐ │ │
│  │ │ Service Stack   │ │  │ │ Service Stack   │ │  │ │ Service Stack│ │ │
│  │ │ • Transactional │ │  │ │ • Transactional │ │  │ │ • ...        │ │ │
│  │ │ • Billing       │ │  │ │ • Billing       │ │  │ │              │ │ │
│  │ │ • Invoice       │ │  │ │ • Invoice       │ │  │ │              │ │ │
│  │ │ • Payment       │ │  │ │ • Payment       │ │  │ │              │ │ │
│  │ │ • Revenue       │ │  │ │ • Revenue       │ │  │ │              │ │ │
│  │ │ • Usage         │ │  │ │ • Usage         │ │  │ │              │ │ │
│  │ └─────────────────┘ │  │ └─────────────────┘ │  │ └──────────────┘ │ │
│  │                     │  │                     │  │                  │ │
│  │ ┌─────────────────┐ │  │ ┌─────────────────┐ │  │ ┌──────────────┐ │ │
│  │ │ Gateway Stack   │ │  │ │ Gateway Stack   │ │  │ │ Gateway Stack│ │ │
│  │ │ • Payment GW    │ │  │ │ • Payment GW    │ │  │ │ • ...        │ │ │
│  │ │ • Tax GW        │ │  │ │ • Tax GW        │ │  │ │              │ │ │
│  │ │ • Finance GW    │ │  │ │ • Finance GW    │ │  │ │              │ │ │
│  │ │ • Provision GW  │ │  │ │ • Provision GW  │ │  │ │              │ │ │
│  │ │ • CRM GW        │ │  │ │ • CRM GW        │ │  │ │              │ │ │
│  │ └─────────────────┘ │  │ └─────────────────┘ │  │ └──────────────┘ │ │
│  │         │           │  │         │           │  │         │        │ │
│  │         ▼           │  │         ▼           │  │         ▼        │ │
│  │  DB: coredb-urbanos│  │  DB: coredb-coopeg  │  │  DB: coredb-demo │ │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘ │
│           │                         │                         │          │
└───────────┼─────────────────────────┼─────────────────────────┼──────────┘
            │                         │                         │
            ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ SHARED INFRASTRUCTURE LAYER                                              │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │ PostgreSQL RDS Instance                                             │  │
│  │ embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com         │  │
│  │                                                                      │  │
│  │ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │  │
│  │ │coredb-urbanos│ │coredb-coopeg │ │coredb-demo   │ │core_config  │ │  │
│  │ │(Full Schema) │ │(Full Schema) │ │(Full Schema) │ │(Shared Meta)│ │  │
│  │ └──────────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ Kubernetes       │  │ Redis/ElastiCache│  │ ActiveMQ             │  │
│  │ EKS Cluster      │  │ Session/Cache    │  │ Message Broker       │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘  │
│                                                                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │ HashiCorp Vault  │  │ AWS S3           │  │ Monitoring Stack     │  │
│  │ Secrets Mgmt     │  │ Object Storage   │  │ Prometheus/Grafana   │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Isolation Boundaries

| Component | Isolation Level | Notes |
|-----------|----------------|-------|
| **Business Data** | ✅ Complete | Separate database per tenant |
| **Application Pods** | ✅ Complete | Dedicated K8s deployments |
| **Compute Resources** | ✅ Quota-based | K8s resource limits per namespace |
| **Network** | ✅ Logical | Service mesh + ingress rules |
| **Secrets/Credentials** | ✅ Logical | Vault namespaces per tenant |
| **Configuration** | ✅ Logical | Tenant-specific Helm values |
| **Database Server** | 🔄 Shared | Multi-database RDS instance |
| **Kubernetes Cluster** | 🔄 Shared | Shared control plane & nodes |
| **Cache Layer** | 🔄 Shared | Redis with key prefixing |
| **Message Queue** | 🔄 Shared | ActiveMQ with queue isolation |
| **Monitoring** | 🔄 Shared | Tenant labels for filtering |

---

## Current Tenant Inventory

### Active Tenants (as of Feb 2026)

| Tenant ID | Tenant Name | Environment | Database | Primary Region | Status |
|-----------|-------------|-------------|----------|----------------|--------|
| TIDLT-100001 | coopeg-sbx | Sandbox | coredb-coopeg-sbx | us-east-1 | Active |
| TIDLT-100002 | demo | Demo | coredb-demo | us-east-1 | Active |
| TIDLT-100003 | dev | Development | enginedevdb | us-east-1 | Active |
| TIDLT-100004 | shm | Production | coredb-shm | us-east-1 | Active |
| TIDLT-100005 | urbanos | Development | coredb-urbanos | us-east-1 | Active |
| TIDLT-100006 | coopeg-prd | Production | coredb-coopeg-prd | us-east-1 | Active |
| TIDLT-100007 | coopegenergy | Production | coredb-coopegenergy | us-east-1 | Active |

### Tenant Naming Conventions

**Tenant ID Format:** `TIDLT-{6-digit-number}`
- `TIDLT` = Tenant ID Prefix (Tenant Identifier)
- Sequential numbering starting from 100001

**Tenant Name Format:** `{company-name}[-environment]`
- Use lowercase
- Hyphenate multi-word names
- Append environment suffix for non-production (e.g., `-sbx`, `-dev`)

**Database Name Format:** `coredb-{tenant-name}` or `{legacy-name}db`
- Prefer: `coredb-{tenant-name}` for new tenants
- Legacy: `enginedevdb` (kept for backwards compatibility)

**Kubernetes Resource Naming:** `{tenant-name}-{service-name}`
- Examples: `urbanos-service-transactional`, `coopeg-prd-payment-gateway`

---

## Infrastructure Components

### AWS Resources

#### RDS PostgreSQL Instance

**Primary Instance:**
- **Endpoint:** `embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com`
- **Port:** 5432
- **Engine:** PostgreSQL 13.x
- **Instance Class:** db.r5.xlarge (or higher)
- **Multi-AZ:** Yes
- **Backup Retention:** 7 days
- **Storage:** gp3 SSD, auto-scaling enabled

**Database Layout:**
```
embrix-rds-dev-db
├── coredb-urbanos       (Tenant: urbanos)
├── coredb-coopeg-sbx    (Tenant: coopeg-sbx)
├── coredb-coopeg-prd    (Tenant: coopeg-prd)
├── coredb-demo          (Tenant: demo)
├── coredb-shm           (Tenant: shm)
├── coredb-coopegenergy  (Tenant: coopegenergy)
├── enginedevdb          (Tenant: dev - legacy name)
└── [Each database contains:]
    ├── public schema (business data)
    └── core_config schema (tenant metadata - shared across all DBs)
```

#### ElastiCache Redis

**Cluster:**
- **Endpoint:** `master.{env}-cache-rg.8fxuvv.use1.cache.amazonaws.com`
- **Port:** 6379
- **Engine:** Redis 6.x
- **Node Type:** cache.r5.large
- **Cluster Mode:** Disabled
- **Usage:** Session storage, caching, rate limiting

**Key Prefixing Pattern:**
```
{tenant-id}:session:{session-id}
{tenant-id}:cache:{cache-key}
{tenant-id}:rate-limit:{user-id}
```

#### Amazon MQ (ActiveMQ)

**Broker:**
- **Endpoint:** `b-{broker-id}.mq.us-east-1.amazonaws.com`
- **Port:** 61617 (SSL)
- **Engine:** ActiveMQ 5.16.x
- **Instance Type:** mq.m5.large
- **Deployment:** Active/Standby

**Queue Naming:**
```
{tenant-id}.billing.invoice
{tenant-id}.payment.processing
{tenant-id}.usage.rating
{tenant-id}.jobs.{job-type}
```

#### S3 Buckets

**Static Assets:**
- **Bucket:** `embrix-static-files`
- **URL:** `https://embrix-static-files.s3.amazonaws.com`
- **Usage:** Invoice templates, report templates, static resources

**Data Storage:**
- **Bucket:** `embrix-{env}-data`
- **Structure:**
  ```
  embrix-dev-data/
  ├── {tenant-id}/
  │   ├── invoices/
  │   ├── reports/
  │   ├── exports/
  │   └── imports/
  ```

#### HashiCorp Vault

**Service:**
- **Endpoint:** `http://{tenant-name}-vault-interface/`
- **Authentication:** Kubernetes Service Account
- **Usage:** Secrets management, merchant credentials

**Secret Paths:**
```
secret/tenant/{tenant-name}/license/
secret/tenant/{tenant-name}/quickbooks/{client_id,client_secret,tokens}
secret/tenant/{tenant-name}/netsuite/{account,consumer_key,token_id}
secret/tenant/{tenant-name}/stripe/{api_key,webhook_secret}
secret/tenant/{tenant-name}/avalara/{account_id,license_key}
```

### Kubernetes (EKS) Architecture

#### Cluster Configuration

**EKS Cluster:**
- **Name:** `embrix-eks-{env}`
- **Version:** 1.28+
- **Region:** us-east-1
- **Networking:** VPC with private subnets
- **Node Groups:** Mixed (on-demand + spot)

#### Namespace Strategy

**Per-Tenant Namespace (Optional):**
While services are named per-tenant, namespaces can be:
1. **Shared namespace approach** (current): All tenant services in same namespace with unique names
2. **Per-tenant namespace** (alternative): Each tenant gets dedicated namespace

**Current Implementation:** Services deployed in shared namespaces with tenant-prefixed names.

#### Service Architecture per Tenant

Each tenant deployment includes:

**Core Services (service-*):**
1. **service-transactional** - Customer, Order, Subscription management
   - Replicas: 2-4
   - Resources: 2 CPU, 4Gi memory
   - Port: 8080

2. **service-billing** - Billing cycle, bill generation
   - Replicas: 2-3
   - Resources: 2 CPU, 4Gi memory
   - Port: 8080

3. **service-invoice** - Invoice generation, PDF rendering
   - Replicas: 2-3
   - Resources: 2 CPU, 4Gi memory
   - Port: 8080

4. **service-payment** - Payment processing, allocation
   - Replicas: 2-4
   - Resources: 2 CPU, 4Gi memory
   - Port: 8080

5. **service-revenue** - Revenue recognition, accounting
   - Replicas: 2
   - Resources: 1 CPU, 2Gi memory
   - Port: 8080

6. **service-usage** - Usage rating, mediation
   - Replicas: 2-4
   - Resources: 4 CPU, 8Gi memory (high compute)
   - Port: 8080

7. **service-mediation** - CDR processing, normalization
   - Replicas: 2-3
   - Resources: 2 CPU, 4Gi memory
   - Port: 8080

8. **service-sso** - Authentication, authorization
   - Replicas: 2
   - Resources: 1 CPU, 2Gi memory
   - Port: 8080

9. **service-proxy** - API Gateway, GraphQL endpoint
   - Replicas: 3-5
   - Resources: 2 CPU, 4Gi memory
   - Port: 8080

**Gateway Services (*-gateway):**
1. **payment-gateway** - Payment processor integrations
2. **tax-gateway** - Tax calculation integrations
3. **finance-gateway** - ERP/accounting integrations
4. **provision-gateway** - Service provisioning integrations
5. **crm-gateway** - CRM system integrations

**Batch Processing:**
1. **batch-process** - Scheduled data processing
2. **jobs-common** - Job execution framework

---

## Tenant Onboarding Process

### Prerequisites Checklist

Before starting tenant onboarding, ensure you have:

- [ ] Tenant business information (company name, contact, region)
- [ ] License agreement and key
- [ ] Merchant account details (QuickBooks, NetSuite, Stripe, etc.)
- [ ] AWS credentials with appropriate permissions
- [ ] kubectl access to EKS cluster
- [ ] Helm 3.x installed
- [ ] Database admin credentials
- [ ] Vault admin token
- [ ] DNS management access (if custom domain needed)

### Step 1: Generate Tenant ID

**Generate next available Tenant ID:**

```bash
# Query existing tenants to find highest ID
psql -h embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com \
     -U admin -d enginedevdb \
     -c "SELECT id FROM core_config.tenant ORDER BY id DESC LIMIT 1;"

# Result example: TIDLT-100007
# Next ID: TIDLT-100008
```

**Assign Tenant Name:**
```bash
# Format: {company-name}[-env]
# Examples:
TENANT_NAME="newclient"          # Production tenant
TENANT_NAME="newclient-sbx"      # Sandbox tenant
TENANT_NAME="newclient-dev"      # Development tenant

# Generate Tenant ID
TENANT_ID="TIDLT-100008"  # Use next sequential ID
```

### Step 2: Database Provisioning

#### 2.1 Create Database

```bash
# Connect to RDS
psql -h embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com \
     -U admin -d postgres

# Create database
CREATE DATABASE "coredb-${TENANT_NAME}"
    WITH 
    OWNER = admin
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = 100;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE "coredb-${TENANT_NAME}" TO admin;
GRANT CONNECT ON DATABASE "coredb-${TENANT_NAME}" TO appuser;

# Exit psql
\q
```

#### 2.2 Run Database Migrations

```bash
# Set database connection
export DB_URL="jdbc:postgresql://embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com:5432/coredb-${TENANT_NAME}?stringtype=unspecified&sslmode=require"
export DB_USER="admin"
export DB_PASSWORD="<password-from-secrets>"

# Option A: Using Flyway (if available)
cd engine/
flyway migrate \
  -url="${DB_URL}" \
  -user="${DB_USER}" \
  -password="${DB_PASSWORD}" \
  -locations="filesystem:./db/migration" \
  -schemas=public,core_config

# Option B: Using Spring Boot application
cd engine/
./mvnw spring-boot:run \
  -Dspring-boot.run.arguments=--spring.flyway.enabled=true \
  -Dspring.datasource.url="${DB_URL}" \
  -Dspring.datasource.username="${DB_USER}" \
  -Dspring.datasource.password="${DB_PASSWORD}"
```

**Verify migrations:**
```bash
psql -h embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com \
     -U admin -d "coredb-${TENANT_NAME}" \
     -c "\dt public.*" \
     -c "\dt core_config.*"

# Expected output: List of all application tables
```

#### 2.3 Insert Tenant Metadata

```sql
-- Connect to database
psql -h embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com \
     -U admin -d "coredb-${TENANT_NAME}"

-- Insert tenant record
INSERT INTO core_config.tenant (
    id,
    name,
    vaulturi,
    vaultpath,
    licensekey,
    status
) VALUES (
    'TIDLT-100008',
    'newclient',
    'http://newclient-vault-interface/',
    'tenant/newclient/production',
    'LICENSE-KEY-PROVIDED-BY-BUSINESS',
    'ACTIVE'
);

-- Insert tenant profile (optional - for additional metadata)
INSERT INTO core_config.tenant_profile (
    tenantid,
    companyname,
    address,
    city,
    state,
    country,
    timezone,
    currency
) VALUES (
    'TIDLT-100008',
    'New Client Inc.',
    '123 Main Street',
    'New York',
    'NY',
    'USA',
    'America/New_York',
    'USD'
);

-- Verify
SELECT * FROM core_config.tenant WHERE id = 'TIDLT-100008';
```

### Step 3: Configure Merchant Integrations

#### 3.1 Create Merchant Accounts in Database

```sql
-- Continue in same psql session

-- Example: QuickBooks Finance Gateway
INSERT INTO core_config.tenant_merchants (
    id,
    tenant_id,
    index,
    name,
    type,
    status,
    authtype,
    apitype,
    baseurl
) VALUES (
    'TIDLT-100008',
    'TIDLT-100008',
    0,
    'QUICKBOOKS',
    'FINANCE_GATEWAY',
    'ACTIVE',
    'OAUTH2',
    'REST',
    'https://quickbooks.api.intuit.com'
);

-- Insert OAuth2 attributes for QuickBooks
INSERT INTO core_config.oauth2_attributes (
    id,
    index,
    realmid,
    environment,
    redirecturi,
    state
) VALUES (
    'TIDLT-100008',
    0,
    '123456789',  -- QuickBooks Company ID
    'PRODUCTION', -- or 'SANDBOX'
    'https://newclient.embrix.com/oauth2/callback',
    'random-state-string'
);

-- Insert finance gateway specific attributes
INSERT INTO core_config.finance_gateway_attributes (
    id,
    index,
    subsidiary,
    accountingmethod,
    fiscalyearstart
) VALUES (
    'TIDLT-100008',
    0,
    'PRIMARY',
    'ACCRUAL',
    '01-01'
);

-- Repeat for other gateways (Payment, Tax, CRM, etc.)
```

#### 3.2 Store Credentials in Vault

```bash
# Authenticate to Vault
export VAULT_ADDR="http://vault-interface/"
export VAULT_TOKEN="<vault-admin-token>"

# Create tenant namespace
vault kv put secret/tenant/newclient/info \
  tenant_id=TIDLT-100008 \
  tenant_name=newclient \
  environment=production

# Store QuickBooks credentials
vault kv put secret/tenant/newclient/quickbooks \
  client_id="<quickbooks-client-id>" \
  client_secret="<quickbooks-client-secret>" \
  access_token="<initial-access-token>" \
  refresh_token="<initial-refresh-token>" \
  realm_id="123456789" \
  token_expiry="<expiry-timestamp>"

# Store Stripe credentials (if applicable)
vault kv put secret/tenant/newclient/stripe \
  api_key="sk_live_..." \
  webhook_secret="whsec_..." \
  publishable_key="pk_live_..."

# Store Avalara credentials (if applicable)
vault kv put secret/tenant/newclient/avalara \
  account_id="<avalara-account-id>" \
  license_key="<avalara-license-key>" \
  company_code="<company-code>"

# Store license key
vault kv put secret/tenant/newclient/license/onboarding \
  license_key="LICENSE-KEY-PROVIDED-BY-BUSINESS" \
  decrypt_key="<generated-decrypt-key>"

# Verify
vault kv get secret/tenant/newclient/quickbooks
```

### Step 4: Create Helm Configurations

#### 4.1 Directory Structure Setup

```bash
# Navigate to repository root
cd /path/to/embrix-o2x

# Create Helm values directories for new tenant
mkdir -p core/helm_values/newclient
mkdir -p payment-gateway/helm_values/newclient
mkdir -p tax-gateway/helm_values/newclient
mkdir -p finance-gateway/helm_values/newclient
mkdir -p provision_gateway/helm_values/newclient
mkdir -p crm_gateway/helm_values/newclient

echo "Created Helm values directories for tenant: newclient"
```

#### 4.2 Core Service Helm Values

**Create: `core/helm_values/newclient/service-transactional.yaml`**

```yaml
app:
  env: production
  envMap:
  - name: LOGS_DIR
    value: /logs
  - name: LOG_LEVEL
    value: INFO
  - name: REDIS_HOST
    value: master.production-cache-rg.8fxuvv.use1.cache.amazonaws.com
  - name: REDIS_PORT
    value: "6379"
  - name: AWS_S3_PUBLICURL
    value: https://embrix-static-files.s3.amazonaws.com
  - name: AMQ_BROKER_URL
    value: ssl://b-xxxxx.mq.us-east-1.amazonaws.com:61617
  - name: TAX_GATEWAY_URL
    value: http://newclient-tax-gateway
  - name: PAYMENT_GATEWAY_URL
    value: http://newclient-payment-gateway
  - name: FINANCE_GATEWAY_URL
    value: http://newclient-finance-gateway
  - name: PROVISIONING_GATEWAY_URL
    value: http://newclient-provision-gateway
  - name: CRM_GATEWAY_URL
    value: http://newclient-crm-gateway
  - name: VAULT_API
    value: http://newclient-vault-interface/
  postgres:
    secret: pg-secret
    url: jdbc:postgresql://embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com:5432/coredb-newclient?stringtype=unspecified&sslmode=require
  spring:
    port: 8080
    profile: pg
  tenantId: TIDLT-100008
  tenantName: newclient
  vault:
    secret: app-vault-token
  volumes:
    dataPvc: newclient-data-pvc
fullnameOverride: newclient-service-transactional
image:
  pullPolicy: Always
  tag: v2.5.0  # Use appropriate version
replicaCount: 2
resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 1000m
    memory: 2Gi
```

**Repeat for other core services:**
- `service-billing.yaml`
- `service-invoice.yaml`
- `service-payment.yaml`
- `service-revenue.yaml`
- `service-usage.yaml`
- `service-mediation.yaml`
- `service-sso.yaml`
- `service-proxy.yaml`
- `batch-process.yaml`
- `jobs-common.yaml`

**Template for other services:** Copy from existing tenant (e.g., `urbanos/`) and update:
- `tenantId: TIDLT-100008`
- `tenantName: newclient`
- `postgres.url` with `coredb-newclient`
- `fullnameOverride: newclient-{service-name}`
- All gateway URLs: `http://newclient-{gateway-name}`
- `volumes.dataPvc: newclient-data-pvc`

#### 4.3 Gateway Service Helm Values

**Create: `finance-gateway/helm_values/newclient/finance-gateway.yaml`**

```yaml
app:
  envMap:
  - name: REDIS_HOST
    value: master.production-cache-rg.8fxuvv.use1.cache.amazonaws.com
  - name: REDIS_PORT
    value: "6379"
  - name: LOGS_DIR
    value: /logs
  - name: DATA_DIR
    value: /data
  license:
    decryptKey: <generated-decrypt-key-for-tenant>
    vault:
      api: http://newclient-vault-interface/read/license/onboarding/
      path: tenant/newclient/production
  postgres:
    secret: pg-secret
    url: jdbc:postgresql://embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com:5432/coredb-newclient?stringtype=unspecified&sslmode=require
  tenantId: TIDLT-100008
  vault:
    api: http://newclient-vault-interface/
    secret: app-vault-token
  volumes:
    dataPvc: newclient-data-pvc
fullnameOverride: newclient-finance-gateway
image:
  pullPolicy: Always
  tag: v2.5.0
replicaCount: 2
resources:
  limits:
    cpu: 1000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 1Gi
```

**Repeat for:**
- `payment-gateway/helm_values/newclient/payment-gateway.yaml`
- `tax-gateway/helm_values/newclient/tax-gateway.yaml`
- `provision_gateway/helm_values/newclient/provision-gateway.yaml`
- `crm_gateway/helm_values/newclient/crm-gateway.yaml`

### Step 5: Kubernetes Deployment

#### 5.1 Create Persistent Volume Claims

```bash
# Create data PVC for tenant
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: newclient-data-pvc
  namespace: default  # or tenant-specific namespace
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: efs-sc  # or appropriate storage class
  resources:
    requests:
      storage: 100Gi
EOF

# Verify
kubectl get pvc newclient-data-pvc
```

#### 5.2 Create Kubernetes Secrets

```bash
# PostgreSQL credentials (if not using existing secret)
kubectl create secret generic pg-secret \
  --from-literal=username=appuser \
  --from-literal=password='<db-password>' \
  --namespace=default

# Vault token (if not using existing secret)
kubectl create secret generic app-vault-token \
  --from-literal=token='<vault-token>' \
  --namespace=default

# Verify
kubectl get secrets | grep -E "pg-secret|app-vault-token"
```

#### 5.3 Deploy Core Services

```bash
# Set working directory
cd /path/to/embrix-o2x

# Deploy services in order (respecting dependencies)

# 1. Deploy SSO (authentication service first)
helm upgrade --install newclient-service-sso ./core/charts/service-sso \
  -f core/helm_values/newclient/service-sso.yaml \
  --namespace default \
  --create-namespace \
  --wait \
  --timeout 10m

# 2. Deploy transactional service
helm upgrade --install newclient-service-transactional ./core/charts/service-transactional \
  -f core/helm_values/newclient/service-transactional.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# 3. Deploy billing service
helm upgrade --install newclient-service-billing ./core/charts/service-billing \
  -f core/helm_values/newclient/service-billing.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# 4. Deploy invoice service
helm upgrade --install newclient-service-invoice ./core/charts/service-invoice \
  -f core/helm_values/newclient/service-invoice.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# 5. Deploy payment service
helm upgrade --install newclient-service-payment ./core/charts/service-payment \
  -f core/helm_values/newclient/service-payment.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# 6. Deploy revenue service
helm upgrade --install newclient-service-revenue ./core/charts/service-revenue \
  -f core/helm_values/newclient/service-revenue.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# 7. Deploy usage/mediation services
helm upgrade --install newclient-service-usage ./core/charts/service-usage \
  -f core/helm_values/newclient/service-usage.yaml \
  --namespace default \
  --wait \
  --timeout 10m

helm upgrade --install newclient-service-mediation ./core/charts/service-mediation \
  -f core/helm_values/newclient/service-mediation.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# 8. Deploy batch/jobs services
helm upgrade --install newclient-batch-process ./core/charts/batch-process \
  -f core/helm_values/newclient/batch-process.yaml \
  --namespace default \
  --wait \
  --timeout 10m

helm upgrade --install newclient-jobs-common ./core/charts/jobs-common \
  -f core/helm_values/newclient/jobs-common.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# 9. Deploy API proxy (last, after all services are up)
helm upgrade --install newclient-service-proxy ./core/charts/service-proxy \
  -f core/helm_values/newclient/service-proxy.yaml \
  --namespace default \
  --wait \
  --timeout 10m
```

**Verify core services:**
```bash
kubectl get pods -l tenant=newclient
kubectl get services -l tenant=newclient

# Check pod logs for startup
kubectl logs -l app=newclient-service-transactional --tail=100
```

#### 5.4 Deploy Gateway Services

```bash
# Deploy gateways (can be done in parallel)

# Finance Gateway
helm upgrade --install newclient-finance-gateway ./finance-gateway/charts/finance-gateway \
  -f finance-gateway/helm_values/newclient/finance-gateway.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# Payment Gateway
helm upgrade --install newclient-payment-gateway ./payment-gateway/charts/payment-gateway \
  -f payment-gateway/helm_values/newclient/payment-gateway.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# Tax Gateway
helm upgrade --install newclient-tax-gateway ./tax-gateway/charts/tax-gateway \
  -f tax-gateway/helm_values/newclient/tax-gateway.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# Provision Gateway
helm upgrade --install newclient-provision-gateway ./provision_gateway/charts/provision-gateway \
  -f provision_gateway/helm_values/newclient/provision-gateway.yaml \
  --namespace default \
  --wait \
  --timeout 10m

# CRM Gateway
helm upgrade --install newclient-crm-gateway ./crm_gateway/charts/crm-gateway \
  -f crm_gateway/helm_values/newclient/crm-gateway.yaml \
  --namespace default \
  --wait \
  --timeout 10m
```

**Verify gateway services:**
```bash
kubectl get pods | grep newclient-.*-gateway
kubectl get services | grep newclient-.*-gateway

# Test gateway health endpoints
kubectl port-forward svc/newclient-finance-gateway 8080:8080
curl http://localhost:8080/actuator/health
```

### Step 6: DNS & Ingress Configuration

#### 6.1 Create Ingress Resources

```yaml
# Create: k8s/ingress/newclient-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: newclient-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
spec:
  tls:
  - hosts:
    - newclient.embrix.com
    - api.newclient.embrix.com
    secretName: newclient-tls-cert
  rules:
  - host: newclient.embrix.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: newclient-service-proxy
            port:
              number: 8080
  - host: api.newclient.embrix.com
    http:
      paths:
      - path: /graphql
        pathType: Prefix
        backend:
          service:
            name: newclient-service-proxy
            port:
              number: 8080
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: newclient-service-proxy
            port:
              number: 8080
```

```bash
# Apply ingress
kubectl apply -f k8s/ingress/newclient-ingress.yaml

# Verify ingress created
kubectl get ingress newclient-ingress
kubectl describe ingress newclient-ingress

# Check certificate issuance (if using cert-manager)
kubectl get certificate newclient-tls-cert
```

#### 6.2 Configure DNS Records

**In AWS Route 53 (or DNS provider):**

```bash
# Get LoadBalancer external IP/hostname
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Create DNS records
# A/CNAME records pointing to LoadBalancer:
# newclient.embrix.com -> <LoadBalancer-DNS>
# api.newclient.embrix.com -> <LoadBalancer-DNS>
# *.newclient.embrix.com -> <LoadBalancer-DNS> (optional wildcard)
```

**AWS CLI example:**
```bash
# Get hosted zone ID
HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
  --query "HostedZones[?Name=='embrix.com.'].Id" \
  --output text | cut -d'/' -f3)

# Get LoadBalancer DNS
LB_DNS=$(kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Create DNS record
aws route53 change-resource-record-sets \
  --hosted-zone-id ${HOSTED_ZONE_ID} \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "newclient.embrix.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'${LB_DNS}'"}]
      }
    }]
  }'

# Repeat for api.newclient.embrix.com
```

**Verify DNS propagation:**
```bash
# Test DNS resolution
dig newclient.embrix.com +short
nslookup newclient.embrix.com

# Test HTTPS endpoint
curl -I https://newclient.embrix.com
curl -I https://api.newclient.embrix.com/graphql
```

### Step 7: Initial Configuration & Testing

#### 7.1 Create Admin User

```bash
# Port-forward to service-sso
kubectl port-forward svc/newclient-service-sso 8080:8080

# Create admin user via API (adjust based on your API)
curl -X POST http://localhost:8080/api/users/create \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@newclient.com",
    "password": "ChangeMe123!",
    "email": "admin@newclient.com",
    "firstName": "Admin",
    "lastName": "User",
    "roleId": "ADMIN_ROLE_ID",
    "status": "ACTIVE"
  }'
```

Or via database:
```sql
-- Connect to tenant database
psql -h embrix-rds-dev-db.chg5bgdk4yyp.us-east-1.rds.amazonaws.com \
     -U admin -d "coredb-newclient"

-- Insert admin user (adjust schema based on your user table structure)
INSERT INTO core_config.users (
    id,
    userid,
    password,  -- use bcrypt hash
    email,
    firstname,
    lastname,
    type,
    status,
    category
) VALUES (
    gen_random_uuid()::text,
    'admin@newclient.com',
    '$2a$10$...',  -- bcrypt hash of password
    'admin@newclient.com',
    'Admin',
    'User',
    'INTERNAL',
    'ACTIVE',
    'SYSTEM_ADMIN'
);
```

#### 7.2 Integration Testing

**Test Core Services:**
```bash
# Health checks
for service in transactional billing invoice payment revenue usage; do
  echo "Testing newclient-service-${service}..."
  kubectl exec -it deployment/newclient-service-${service} -- \
    curl -s http://localhost:8080/actuator/health | jq .
done
```

**Test Gateway Integrations:**
```bash
# Test Finance Gateway - QuickBooks connection
kubectl port-forward svc/newclient-finance-gateway 8080:8080

curl -X POST http://localhost:8080/api/quickbooks/test-connection \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: TIDLT-100008" \
  -d '{}'

# Test Payment Gateway - Stripe connection
kubectl port-forward svc/newclient-payment-gateway 8080:8080

curl -X POST http://localhost:8080/api/stripe/validate \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: TIDLT-100008" \
  -d '{}'

# Test Tax Gateway - Avalara connection
kubectl port-forward svc/newclient-tax-gateway 8080:8080

curl -X POST http://localhost:8080/api/avalara/ping \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: TIDLT-100008" \
  -d '{}'
```

**Test GraphQL API:**
```bash
# Test via ingress
curl -X POST https://api.newclient.embrix.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "query { getTenantConfig(input: {id: \"TIDLT-100008\"}) { tenantId tenantName status } }"
  }'
```

**Test End-to-End Workflow:**
```bash
# Create customer -> Create order -> Generate bill -> Generate invoice
# (Use your actual API endpoints and payloads)

# 1. Create customer
curl -X POST https://api.newclient.embrix.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "mutation { createCustomer(input: { firstName: \"Test\", lastName: \"User\", email: \"test@example.com\" }) { id accountNumber } }"
  }'

# 2. Create subscription/order
# 3. Trigger billing cycle
# 4. Verify invoice generation
# 5. Process payment
```

#### 7.3 Smoke Test Checklist

- [ ] All pods are running and healthy
- [ ] Database connectivity verified
- [ ] Vault secrets accessible
- [ ] Redis connection working
- [ ] ActiveMQ queue creation successful
- [ ] Admin user can log in
- [ ] GraphQL endpoint responding
- [ ] Gateway integrations authenticated
- [ ] Can create test customer
- [ ] Can create test order
- [ ] Billing cycle can be triggered
- [ ] Invoice PDF generation works
- [ ] Payment processing functional
- [ ] Reports can be generated

### Step 8: Monitoring & Alerting Setup

#### 8.1 Configure Prometheus Monitoring

```yaml
# Create: monitoring/servicemonitor-newclient.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: newclient-services
  namespace: monitoring
  labels:
    tenant: newclient
spec:
  selector:
    matchLabels:
      tenant: newclient
  endpoints:
  - port: metrics
    interval: 30s
    path: /actuator/prometheus
```

```bash
kubectl apply -f monitoring/servicemonitor-newclient.yaml
```

#### 8.2 Create Grafana Dashboards

```bash
# Import tenant-specific dashboard
# Dashboard ID or JSON with tenant filter: tenant="newclient"

# Key metrics to monitor:
# - Pod CPU/Memory usage
# - Request rate & latency
# - Database connection pool
# - Cache hit rate
# - Queue depth (ActiveMQ)
# - Error rate per service
# - Gateway API call success rate
```

#### 8.3 Configure Alerts

```yaml
# Create: alerts/newclient-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: newclient-alerts
  namespace: monitoring
spec:
  groups:
  - name: newclient
    interval: 30s
    rules:
    - alert: NewClientServiceDown
      expr: up{tenant="newclient"} == 0
      for: 2m
      labels:
        severity: critical
        tenant: newclient
      annotations:
        summary: "Service {{ $labels.service }} is down for tenant newclient"
        description: "Service has been down for more than 2 minutes"
    
    - alert: NewClientHighErrorRate
      expr: rate(http_server_requests_seconds_count{tenant="newclient",status=~"5.."}[5m]) > 0.05
      for: 5m
      labels:
        severity: warning
        tenant: newclient
      annotations:
        summary: "High error rate for tenant newclient"
        description: "Error rate is {{ $value }} errors/sec"
    
    - alert: NewClientDatabaseConnectionPoolExhausted
      expr: hikaricp_connections_active{tenant="newclient"} >= hikaricp_connections_max{tenant="newclient"} * 0.9
      for: 5m
      labels:
        severity: warning
        tenant: newclient
      annotations:
        summary: "Database connection pool near capacity"
        description: "Active connections: {{ $value }}"
```

```bash
kubectl apply -f alerts/newclient-alerts.yaml
```

### Step 9: Documentation & Handoff

#### 9.1 Create Tenant Runbook

Create: `docs/runbooks/TENANT_newclient.md`

```markdown
# Tenant: newclient (TIDLT-100008)

## Overview
- **Tenant Name:** newclient
- **Tenant ID:** TIDLT-100008
- **Environment:** Production
- **Region:** us-east-1
- **Database:** coredb-newclient
- **Onboarding Date:** 2026-02-10
- **Primary Contact:** contact@newclient.com

## Access Information
- **GraphQL API:** https://api.newclient.embrix.com/graphql
- **Admin Portal:** https://newclient.embrix.com
- **Monitoring Dashboard:** https://grafana.embrix.com/d/tenant-newclient

## Service Endpoints
- service-proxy: http://newclient-service-proxy:8080
- service-transactional: http://newclient-service-transactional:8080
- finance-gateway: http://newclient-finance-gateway:8080
- payment-gateway: http://newclient-payment-gateway:8080
- tax-gateway: http://newclient-tax-gateway:8080

## Integrations
- **Finance:** QuickBooks (Production)
- **Payment:** Stripe (Live)
- **Tax:** Avalara (Production)
- **CRM:** None

## Credentials Locations
- Database: AWS Secrets Manager - `embrix/rds/appuser`
- Vault Token: Kubernetes Secret - `app-vault-token`
- QuickBooks: Vault - `secret/tenant/newclient/quickbooks`
- Stripe: Vault - `secret/tenant/newclient/stripe`
- Avalara: Vault - `secret/tenant/newclient/avalara`

## Operational Procedures

### Restart Services
```bash
kubectl rollout restart deployment newclient-service-transactional
kubectl rollout restart deployment newclient-finance-gateway
```

### View Logs
```bash
kubectl logs -l tenant=newclient -f --tail=100
kubectl logs deployment/newclient-service-billing -f
```

### Scale Services
```bash
kubectl scale deployment newclient-service-transactional --replicas=4
```

### Database Backup
```bash
# RDS automated backups: 7-day retention
# Manual snapshot:
aws rds create-db-snapshot \
  --db-instance-identifier embrix-rds-dev-db \
  --db-snapshot-identifier newclient-manual-$(date +%Y%m%d-%H%M%S)
```

## Troubleshooting

### Common Issues
1. **Service won't start:** Check database connectivity, verify Vault secrets
2. **Gateway authentication fails:** Verify OAuth tokens in Vault, check token expiry
3. **High latency:** Check database connection pool, Redis cache hit rate

### Emergency Contacts
- **DevOps On-Call:** devops-oncall@embrix.com
- **Tenant Account Manager:** account-manager@embrix.com
- **Client Technical Contact:** tech@newclient.com
```

#### 9.2 Update Tenant Inventory

Add to `docs/TENANT_INVENTORY.md`:

```markdown
## newclient (TIDLT-100008)
- **Status:** Active
- **Environment:** Production
- **Onboarded:** 2026-02-10
- **Version:** v2.5.0
- **Database:** coredb-newclient
- **Integrations:** QuickBooks, Stripe, Avalara
- **Special Notes:** Standard configuration, no customizations
```

---

## Configuration Management

### Environment Variables Reference

**Common Environment Variables (All Services):**

| Variable | Purpose | Example |
|----------|---------|---------|
| `TENANT_ID` | Unique tenant identifier | `TIDLT-100008` |
| `LOGS_DIR` | Log file directory | `/logs` |
| `LOG_LEVEL` | Logging verbosity | `INFO`, `DEBUG`, `WARN` |
| `REDIS_HOST` | Redis cache endpoint | `master.cache-rg.us-east-1.cache.amazonaws.com` |
| `REDIS_PORT` | Redis port | `6379` |
| `AWS_S3_PUBLICURL` | S3 static assets URL | `https://embrix-static-files.s3.amazonaws.com` |
| `AMQ_BROKER_URL` | ActiveMQ broker URL | `ssl://broker.mq.us-east-1.amazonaws.com:61617` |
| `VAULT_API` | Vault interface URL | `http://tenant-vault-interface/` |

**Service-Specific Variables:**

| Service | Variable | Purpose |
|---------|----------|---------|
| All Core | `TAX_GATEWAY_URL` | Tax calculation service |
| All Core | `PAYMENT_GATEWAY_URL` | Payment processing service |
| All Core | `FINANCE_GATEWAY_URL` | Finance/ERP integration |
| All Core | `PROVISIONING_GATEWAY_URL` | Service provisioning |
| All Core | `CRM_GATEWAY_URL` | CRM integration |
| Gateways | `DATA_DIR` | Data file storage | `/data` |

### Database Connection Configuration

**JDBC URL Format:**
```
jdbc:postgresql://<host>:<port>/<database>?stringtype=unspecified&sslmode=require
```

**Connection Pool Settings (HikariCP):**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      leak-detection-threshold: 60000
```

### Vault Configuration Patterns

**Path Structure:**
```
secret/
└── tenant/
    └── {tenant-name}/
        ├── info                    # Tenant metadata
        ├── license/
        │   └── onboarding          # License keys
        ├── quickbooks/             # QuickBooks credentials
        ├── netsuite/               # NetSuite credentials
        ├── stripe/                 # Stripe API keys
        ├── avalara/                # Avalara credentials
        ├── authorize-net/          # Authorize.Net credentials
        └── custom/                 # Custom integrations
```

**Secret Format Examples:**

**QuickBooks OAuth2:**
```json
{
  "client_id": "AB...",
  "client_secret": "xyz...",
  "access_token": "eyJh...",
  "refresh_token": "AB11...",
  "realm_id": "123456789",
  "token_expiry": "2026-02-11T10:00:00Z"
}
```

**Stripe:**
```json
{
  "api_key": "sk_live_...",
  "publishable_key": "pk_live_...",
  "webhook_secret": "whsec_..."
}
```

**NetSuite OAuth1:**
```json
{
  "account": "1234567",
  "consumer_key": "abc...",
  "consumer_secret": "def...",
  "token_id": "ghi...",
  "token_secret": "jkl..."
}
```

### Feature Flags

**Database-Driven Feature Flags:**
```sql
-- Table: core_config.feature_flags
CREATE TABLE core_config.feature_flags (
    tenant_id VARCHAR(255),
    feature_key VARCHAR(255),
    enabled BOOLEAN DEFAULT false,
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (tenant_id, feature_key)
);

-- Example: Enable advanced reporting for tenant
INSERT INTO core_config.feature_flags (tenant_id, feature_key, enabled, config)
VALUES ('TIDLT-100008', 'ADVANCED_REPORTING', true, '{"export_formats": ["PDF", "EXCEL", "CSV"]}');
```

**Application Usage:**
```groovy
@Service
class FeatureFlagService {
    
    @Autowired
    JdbcTemplate jdbcTemplate
    
    boolean isEnabled(String tenantId, String featureKey) {
        String sql = "SELECT enabled FROM core_config.feature_flags WHERE tenant_id = ? AND feature_key = ?"
        try {
            return jdbcTemplate.queryForObject(sql, Boolean.class, tenantId, featureKey)
        } catch (EmptyResultDataAccessException e) {
            return false // Feature not configured = disabled
        }
    }
    
    Map<String, Object> getFeatureConfig(String tenantId, String featureKey) {
        String sql = "SELECT config FROM core_config.feature_flags WHERE tenant_id = ? AND feature_key = ?"
        String json = jdbcTemplate.queryForObject(sql, String.class, tenantId, featureKey)
        return new ObjectMapper().readValue(json, Map.class)
    }
}
```

---

## Feature Customization

### Customization Levels

#### Level 1: Configuration-Only (Recommended)
**Effort:** Low | **Maintenance:** Low | **Risk:** Low

**Examples:**
- Enable/disable features via feature flags
- Configure business rules (payment terms, tax rules)
- Customize invoice/report templates
- Set integration endpoints
- Configure merchant accounts

**Implementation:**
```yaml
# Helm values
app:
  features:
    advancedReporting: true
    customWorkflows: true
    bulkOperations: false
```

```sql
-- Database configuration
INSERT INTO core_config.tenant_property_defaults (tenant_id, property_key, property_value)
VALUES 
  ('TIDLT-100008', 'invoice.due_days', '30'),
  ('TIDLT-100008', 'payment.auto_retry', 'true'),
  ('TIDLT-100008', 'billing.cycle_day', '1');
```

#### Level 2: Template/UI Customization
**Effort:** Medium | **Maintenance:** Medium | **Risk:** Low

**Examples:**
- Custom invoice templates
- Branded self-care portal
- Custom email templates
- Report layouts
- Dashboard widgets

**Implementation:**
```sql
-- Store custom template
INSERT INTO core_config.invoice_template (tenant_id, template_name, template_html, template_css)
VALUES ('TIDLT-100008', 'DEFAULT', '<html>...</html>', 'body { color: #333; }');

-- Store branding
INSERT INTO core_config.selfcare_config (tenantid, logo_url, primary_color, secondary_color)
VALUES ('TIDLT-100008', 'https://s3.../logo.png', '#0066cc', '#ff6600');
```

#### Level 3: Integration Customization
**Effort:** Medium-High | **Maintenance:** Medium | **Risk:** Medium

**Examples:**
- Custom field mappings for ERP
- Specific payment provider not in standard list
- Custom tax calculation rules
- Unique provisioning workflows

**Implementation:**
```json
// Store in core_config.finance_gateway_attributes.custom_mappings (JSONB)
{
  "customer_mapping": {
    "embrix_field": "netsuite_field",
    "accountNumber": "customer_id",
    "taxId": "federal_tax_id",
    "customField1": "netsuite_custom_field_123"
  },
  "invoice_mapping": {
    "invoiceNumber": "tranid",
    "amount": "total",
    "customTaxCode": "taxcode"
  }
}
```

```groovy
// Gateway code reads custom mappings
@Service
class NetSuiteIntegrationService {
    
    Map<String, String> getCustomerFieldMapping(String tenantId) {
        String sql = """
            SELECT custom_mappings->'customer_mapping' 
            FROM core_config.finance_gateway_attributes 
            WHERE id = ?
        """
        String json = jdbcTemplate.queryForObject(sql, String.class, tenantId)
        return objectMapper.readValue(json, Map.class)
    }
    
    NetSuiteCustomer mapCustomer(Customer embrixCustomer, String tenantId) {
        Map<String, String> mapping = getCustomerFieldMapping(tenantId)
        NetSuiteCustomer netsuiteCustomer = new NetSuiteCustomer()
        
        mapping.each { embrixField, netsuiteField ->
            def value = embrixCustomer."${embrixField}"
            netsuiteCustomer."${netsuiteField}" = value
        }
        
        return netsuiteCustomer
    }
}
```

#### Level 4: Version-Based Customization (Use Sparingly)
**Effort:** High | **Maintenance:** High | **Risk:** High

**When to use:**
- Tenant willing to pay premium for custom development
- Feature genuinely unique (won't benefit other tenants)
- Willing to accept slower upgrade cycle
- Feature is non-core (won't conflict with future platform changes)

**Implementation:**
```bash
# Deploy different version to specific tenant
helm upgrade --install newclient-service-transactional ./core/charts/service-transactional \
  -f core/helm_values/newclient/service-transactional.yaml \
  --set image.tag=v2.5.0-newclient-custom \
  --namespace default
```

**⚠️ Warning:** Avoid code forking. Instead:
1. Build feature in main codebase with feature flag
2. Deploy to tenant with flag enabled
3. Keep codebase unified but behavior configurable

### Adding New Integrations

**Process for adding new merchant/integration:**

1. **Database Configuration:**
```sql
-- Add merchant to tenant
INSERT INTO core_config.tenant_merchants (
    id, tenant_id, index, name, type, status, authtype, apitype, baseurl
) VALUES (
    'TIDLT-100008',
    'TIDLT-100008',
    1,  -- Index for multiple merchants of same type
    'NEW_MERCHANT',
    'FINANCE_GATEWAY',
    'ACTIVE',
    'OAUTH2',
    'REST',
    'https://api.newmerchant.com'
);

-- Add auth attributes (if OAuth2)
INSERT INTO core_config.oauth2_attributes (
    id, index, environment, redirecturi
) VALUES (
    'TIDLT-100008',
    1,
    'PRODUCTION',
    'https://newclient.embrix.com/oauth2/callback'
);

-- Add gateway-specific attributes
INSERT INTO core_config.finance_gateway_attributes (
    id, index, custom_config
) VALUES (
    'TIDLT-100008',
    1,
    '{"api_version": "v2", "webhook_url": "https://api.newclient.embrix.com/webhooks/newmerchant"}'::jsonb
);
```

2. **Store Credentials in Vault:**
```bash
vault kv put secret/tenant/newclient/newmerchant \
  client_id="..." \
  client_secret="..." \
  api_key="..."
```

3. **Gateway Code (if new merchant type):**
```groovy
@Service
class NewMerchantService {
    
    @Autowired
    TenantRepositoryService tenantRepo
    
    @Autowired
    VaultService vaultService
    
    def authenticate(String tenantId) {
        // Get tenant merchant config
        Tenant tenant = tenantRepo.findByTenantIdAndMerchant(
            tenantId, 
            MerchantType.FINANCE_GATEWAY, 
            "NEW_MERCHANT"
        )
        
        // Get credentials from Vault
        Map<String, String> creds = vaultService.getSecret(
            "secret/tenant/${tenant.name}/newmerchant"
        )
        
        // Authenticate with merchant API
        // ...
    }
}
```

4. **Test Integration:**
```bash
# Port-forward to gateway
kubectl port-forward svc/newclient-finance-gateway 8080:8080

# Test authentication
curl -X POST http://localhost:8080/api/newmerchant/authenticate \
  -H "X-Tenant-ID: TIDLT-100008"
```

---

## Monitoring & Observability

### Key Metrics to Monitor

**Application Metrics:**
| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| Pod CPU usage | > 80% for 5min | Warning |
| Pod Memory usage | > 85% for 5min | Warning |
| Pod restart count | > 3 in 1hr | Critical |
| HTTP error rate (5xx) | > 5% for 5min | Critical |
| HTTP latency (p95) | > 2s | Warning |
| HTTP latency (p99) | > 5s | Critical |
| Database connection pool | > 90% capacity | Warning |
| Cache hit rate | < 70% | Warning |
| Queue depth (ActiveMQ) | > 1000 msgs | Warning |
| Disk usage | > 85% | Warning |

**Business Metrics:**
| Metric | Monitoring |
|--------|-----------|
| Orders created/hour | Track trends |
| Bills generated/day | Track against expected |
| Invoices sent/day | Track delivery rate |
| Payments processed/hour | Track success rate |
| Failed API calls | Track per endpoint |
| Gateway integration failures | Alert on > 5% |

### Logging Standards

**Log Levels:**
- **ERROR:** System errors, exceptions, integration failures
- **WARN:** Deprecated API usage, slow queries, retry attempts
- **INFO:** Business events (order created, bill generated, payment processed)
- **DEBUG:** Detailed flow, variable values (not in production)

**Log Format (JSON):**
```json
{
  "timestamp": "2026-02-10T15:30:00.123Z",
  "level": "INFO",
  "service": "service-billing",
  "tenant_id": "TIDLT-100008",
  "correlation_id": "abc-123-def",
  "message": "Bill generated successfully",
  "context": {
    "bill_id": "BILL-12345",
    "customer_id": "CUST-67890",
    "amount": 150.00,
    "currency": "USD"
  }
}
```

**Correlation ID Pattern:**
Request tracking across services using `X-Correlation-ID` header.

### Dashboards

**Tenant Overview Dashboard:**
- Service health status (green/yellow/red per service)
- Request rate & latency (per service)
- Error rate (per service)
- Database connections (active vs max)
- Cache hit rate
- Queue depth
- Recent errors (last 100)
- Recent deployments

**Business Metrics Dashboard:**
- Daily orders/bills/invoices
- Payment success rate
- Revenue processed (last 7 days)
- Top API consumers
- Gateway integration health
- Customer growth

**Infrastructure Dashboard:**
- Pod CPU/Memory usage
- Node capacity
- PVC usage
- Network traffic
- Database performance (queries/sec, slow queries)
- Cache performance

### Log Aggregation

**ELK Stack (Elasticsearch, Logstash, Kibana):**
```bash
# Query logs for specific tenant
GET /logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "tenant_id": "TIDLT-100008" } },
        { "range": { "timestamp": { "gte": "now-1h" } } }
      ]
    }
  }
}

# Query errors for tenant
GET /logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "tenant_id": "TIDLT-100008" } },
        { "term": { "level": "ERROR" } },
        { "range": { "timestamp": { "gte": "now-24h" } } }
      ]
    }
  },
  "sort": [ { "timestamp": "desc" } ]
}
```

### Alerting Rules

**Critical Alerts (Page immediately):**
- All pods down for a tenant
- Database connection failure
- Payment gateway complete failure
- Security breach detected
- Data loss detected

**Warning Alerts (Email/Slack):**
- High error rate (> 5%)
- High latency (> 2s p95)
- Resource usage high (> 80%)
- Integration intermittent failures
- Queue backlog growing
- Certificate expiring soon (< 7 days)

**Alert Routing:**
```yaml
# Prometheus AlertManager config
route:
  receiver: 'default'
  group_by: ['tenant', 'severity']
  routes:
  - match:
      severity: critical
      tenant: newclient
    receiver: 'newclient-oncall-pagerduty'
  - match:
      severity: warning
      tenant: newclient
    receiver: 'newclient-slack-channel'
```

---

## Troubleshooting

### Common Issues & Resolutions

#### 1. Service Won't Start

**Symptoms:**
- Pod in `CrashLoopBackOff` state
- Container exits immediately after start

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -l tenant=newclient

# Check pod events
kubectl describe pod <pod-name>

# Check container logs
kubectl logs <pod-name> --previous

# Check if config is correct
kubectl get configmap <configmap-name> -o yaml
kubectl get secret <secret-name> -o yaml
```

**Common Causes & Fixes:**

**Database connection failure:**
```bash
# Verify database exists
psql -h embrix-rds-dev-db... -U admin -l | grep newclient

# Test connection from pod
kubectl exec -it <pod-name> -- psql "${DB_URL}"

# Check security group allows connection
aws ec2 describe-security-groups --group-ids <sg-id>
```

**Missing environment variables:**
```bash
# Check pod env vars
kubectl exec <pod-name> -- env | grep TENANT

# Fix: Update Helm values and redeploy
helm upgrade newclient-service-transactional ./charts/service-transactional \
  -f helm_values/newclient/service-transactional.yaml
```

**Vault secrets not accessible:**
```bash
# Check if vault token is valid
kubectl get secret app-vault-token -o json | jq -r '.data.token' | base64 -d

# Test vault access from pod
kubectl exec -it <pod-name> -- \
  curl -H "X-Vault-Token: <token>" http://vault-interface/v1/secret/tenant/newclient/info
```

#### 2. Gateway Authentication Failing

**Symptoms:**
- Gateway returns 401 Unauthorized
- Logs show "Invalid credentials" or "Token expired"

**Diagnosis:**
```bash
# Check gateway logs
kubectl logs deployment/newclient-finance-gateway | grep -i auth

# Check merchant configuration in database
psql -h embrix-rds-dev-db... -U admin -d coredb-newclient \
  -c "SELECT * FROM core_config.tenant_merchants WHERE tenant_id='TIDLT-100008';"

# Check OAuth2 token expiry
psql -h embrix-rds-dev-db... -U admin -d coredb-newclient \
  -c "SELECT * FROM core_config.oauth2_attributes WHERE id='TIDLT-100008';"
```

**Common Causes & Fixes:**

**OAuth token expired:**
```bash
# Get current tokens from Vault
vault kv get secret/tenant/newclient/quickbooks

# Use refresh token to get new access token (QuickBooks example)
curl -X POST https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer \
  -H "Accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Basic $(echo -n "${CLIENT_ID}:${CLIENT_SECRET}" | base64)" \
  -d "grant_type=refresh_token&refresh_token=${REFRESH_TOKEN}"

# Store new tokens in Vault
vault kv put secret/tenant/newclient/quickbooks \
  access_token="<new-access-token>" \
  refresh_token="<new-refresh-token>" \
  token_expiry="<new-expiry>"

# Restart gateway to pick up new tokens
kubectl rollout restart deployment/newclient-finance-gateway
```

**Wrong credentials stored:**
```bash
# Re-verify credentials with merchant
# Update Vault with correct credentials
vault kv put secret/tenant/newclient/quickbooks \
  client_id="<correct-client-id>" \
  client_secret="<correct-client-secret>"
```

#### 3. High Latency / Slow Responses

**Symptoms:**
- API responses taking > 5 seconds
- Timeouts occurring
- Users reporting slow performance

**Diagnosis:**
```bash
# Check pod resource usage
kubectl top pods -l tenant=newclient

# Check database query performance
psql -h embrix-rds-dev-db... -U admin -d coredb-newclient \
  -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check cache hit rate
redis-cli -h <redis-host> INFO stats | grep -E "keyspace_hits|keyspace_misses"

# Check network latency between services
kubectl exec -it deployment/newclient-service-billing -- \
  curl -w "@curl-format.txt" -o /dev/null -s http://newclient-service-transactional:8080/actuator/health
```

**Common Causes & Fixes:**

**Database connection pool exhausted:**
```bash
# Check active connections
kubectl logs deployment/newclient-service-billing | grep -i "HikariPool"

# Increase pool size in application config
# Update Helm values:
# spring.datasource.hikari.maximum-pool-size: 30

helm upgrade newclient-service-billing ...
```

**Missing database indexes:**
```sql
-- Find slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
WHERE mean_time > 1000 
ORDER BY mean_time DESC;

-- Add missing indexes
CREATE INDEX idx_account_tenant_email ON account(tenant_id, email);
CREATE INDEX idx_invoice_customer_date ON invoice(customer_id, invoice_date);
```

**Cache not configured:**
```groovy
// Ensure cache is enabled in application code
@Cacheable(value = "customers", key = "#customerId")
Customer getCustomer(String customerId) {
    // ...
}
```

**Need to scale up:**
```bash
# Increase replicas for high-load service
kubectl scale deployment newclient-service-transactional --replicas=4

# Or update Helm values for permanent change
# replicaCount: 4
```

#### 4. Payment Processing Failures

**Symptoms:**
- Payments failing with errors
- Payment gateway returning errors
- Payments stuck in "PENDING" state

**Diagnosis:**
```bash
# Check payment service logs
kubectl logs deployment/newclient-service-payment | grep -i "payment.*fail"

# Check payment gateway logs
kubectl logs deployment/newclient-payment-gateway | grep -i error

# Check payment records in database
psql -h embrix-rds-dev-db... -U admin -d coredb-newclient \
  -c "SELECT * FROM payment WHERE status='FAILED' ORDER BY created_date DESC LIMIT 10;"
```

**Common Causes & Fixes:**

**Gateway API credentials invalid:**
```bash
# Test Stripe API directly
curl https://api.stripe.com/v1/charges \
  -u sk_test_...: \
  -d amount=100 \
  -d currency=usd \
  -d source=tok_visa

# If fails, update credentials in Vault
vault kv put secret/tenant/newclient/stripe api_key="<correct-key>"
```

**Webhook not configured:**
```bash
# Verify webhook endpoint is reachable
curl -X POST https://api.newclient.embrix.com/webhooks/stripe \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: <test-signature>" \
  -d '{"type": "payment_intent.succeeded", "data": {...}}'

# Configure webhook in Stripe dashboard
# URL: https://api.newclient.embrix.com/webhooks/stripe
# Events: payment_intent.succeeded, payment_intent.failed, charge.refunded
```

**Payment method expired:**
```sql
-- Check customer payment methods
SELECT customer_id, payment_method_type, expiry_date, status 
FROM payment_profile 
WHERE tenant_id='TIDLT-100008' AND customer_id='<customer-id>';

-- Customer needs to update payment method via self-care portal
```

#### 5. Billing/Invoice Generation Issues

**Symptoms:**
- Bills not generating on schedule
- Invoices missing data
- PDF generation failing

**Diagnosis:**
```bash
# Check billing job logs
kubectl logs deployment/newclient-jobs-common | grep -i "billing"

# Check invoice service logs
kubectl logs deployment/newclient-service-invoice | grep -i error

# Check billing records
psql -h embrix-rds-dev-db... -U admin -d coredb-newclient \
  -c "SELECT * FROM bill WHERE status IN ('FAILED', 'PENDING') ORDER BY created_date DESC LIMIT 10;"
```

**Common Causes & Fixes:**

**Job scheduler not running:**
```bash
# Check if job scheduler pod is running
kubectl get pods -l app=newclient-jobs-common

# Check job schedule configuration
psql -h embrix-rds-dev-db... -U admin -d coredb-newclient \
  -c "SELECT * FROM job_schedule WHERE tenant_id='TIDLT-100008' AND status='ACTIVE';"

# Manually trigger billing job
curl -X POST http://newclient-jobs-common:8080/api/jobs/billing/trigger \
  -H "X-Tenant-ID: TIDLT-100008"
```

**Template missing:**
```sql
-- Check if invoice template exists
SELECT * FROM core_config.invoice_template WHERE tenant_id='TIDLT-100008';

-- If missing, create default template
INSERT INTO core_config.invoice_template (tenant_id, template_name, template_html)
VALUES ('TIDLT-100008', 'DEFAULT', '<html>...</html>');
```

**S3 upload failing:**
```bash
# Check S3 bucket permissions
aws s3 ls s3://embrix-dev-data/TIDLT-100008/invoices/

# Test upload from pod
kubectl exec -it deployment/newclient-service-invoice -- \
  aws s3 cp test.txt s3://embrix-dev-data/TIDLT-100008/invoices/

# Fix IAM role permissions if needed
```

### Emergency Procedures

#### Rollback Deployment

```bash
# View deployment history
helm history newclient-service-transactional

# Rollback to previous version
helm rollback newclient-service-transactional <revision>

# Or rollback all services
for service in transactional billing invoice payment revenue; do
  helm rollback newclient-service-${service} <revision>
done
```

#### Scale Down (Maintenance Mode)

```bash
# Scale all services to 0 (emergency maintenance)
kubectl scale deployment -l tenant=newclient --replicas=0

# Scale back up
kubectl scale deployment -l tenant=newclient --replicas=2
```

#### Database Restore

```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier embrix-rds-dev-db \
  --query "DBSnapshots[?contains(DBSnapshotIdentifier, 'newclient')].DBSnapshotIdentifier"

# Restore from snapshot (creates new instance)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier embrix-rds-dev-db-restore \
  --db-snapshot-identifier <snapshot-id>

# Update connection strings to point to restored instance
# (Update Helm values and redeploy services)
```

#### Clear Cache

```bash
# Clear Redis cache for tenant
redis-cli -h <redis-host> KEYS "TIDLT-100008:*" | xargs redis-cli -h <redis-host> DEL

# Or flush specific pattern
redis-cli -h <redis-host> --scan --pattern "TIDLT-100008:session:*" | xargs redis-cli -h <redis-host> DEL
```

---

## Best Practices

### Development Best Practices

1. **Configuration Over Code**
   - Use feature flags for new features
   - Store configurations in database (core_config schema)
   - Avoid hard-coding tenant-specific logic

2. **Backward Compatibility**
   - Database migrations must be backward compatible
   - Support multiple API versions if breaking changes needed
   - Gradual rollout of new features

3. **Tenant Isolation**
   - Always filter by tenant_id in database queries (even with separate DBs for defense in depth)
   - Log tenant_id in all log messages
   - Include tenant_id in all async messages

4. **Testing**
   - Integration tests must use test tenant (TIDLT-000000)
   - Load testing against dev tenant before production rollout
   - Smoke test all critical paths after deployment

### Operational Best Practices

1. **Deployment Strategy**
   - Deploy to dev tenant first
   - Deploy to sandbox tenants second
   - Deploy to production tenants last (staggered)
   - Monitor for 24 hours after each production deployment

2. **Version Management**
   - Tag all releases with semantic versioning
   - Document breaking changes in CHANGELOG
   - Maintain version compatibility matrix

3. **Monitoring**
   - Set up alerts before tenant goes live
   - Review metrics weekly
   - Perform monthly capacity planning

4. **Security**
   - Rotate Vault tokens quarterly
   - Rotate database passwords semi-annually
   - Review IAM permissions quarterly
   - Update dependencies monthly (security patches)

5. **Documentation**
   - Update tenant runbook after any major configuration change
   - Document all customizations
   - Keep integration credentials inventory up to date

### Cost Optimization

1. **Right-Size Resources**
   - Monitor actual CPU/memory usage
   - Adjust resource requests/limits quarterly
   - Use horizontal pod autoscaling (HPA) for variable load

2. **Database Optimization**
   - Regular VACUUM and ANALYZE
   - Archive old data (> 2 years)
   - Consider read replicas for reporting

3. **Cache Effectively**
   - Identify frequently accessed data
   - Implement multi-level caching
   - Monitor cache hit rates

4. **Scheduled Jobs**
   - Run resource-intensive jobs during off-peak hours
   - Use spot instances for batch processing
   - Implement job throttling

---

## Appendices

### Appendix A: Service Dependency Matrix

| Service | Depends On |
|---------|-----------|
| service-sso | Database, Redis, Vault |
| service-transactional | Database, Redis, service-sso, all gateways |
| service-billing | Database, Redis, service-transactional, service-usage |
| service-invoice | Database, Redis, S3, service-billing, finance-gateway |
| service-payment | Database, Redis, service-billing, payment-gateway, finance-gateway |
| service-revenue | Database, Redis, service-invoice, finance-gateway |
| service-usage | Database, Redis, service-transactional |
| service-mediation | Database, Redis, ActiveMQ, service-usage |
| service-proxy | All core services |
| finance-gateway | Database, Vault, External APIs (QuickBooks, NetSuite) |
| payment-gateway | Database, Vault, External APIs (Stripe, Authorize.Net) |
| tax-gateway | Database, Vault, External APIs (Avalara, TaxJar) |
| provision-gateway | Database, Vault, External APIs (Broadsoft, etc.) |
| crm-gateway | Database, Vault, External APIs (Salesforce, etc.) |

### Appendix B: Port Reference

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| service-* | 8080 | HTTP | Application/API |
| service-* | 8081 | HTTP | Actuator/Metrics |
| *-gateway | 8080 | HTTP | Application/API |
| PostgreSQL | 5432 | TCP | Database |
| Redis | 6379 | TCP | Cache |
| ActiveMQ | 61617 | TCP (SSL) | Message Queue |
| ActiveMQ | 8161 | HTTP | Admin Console |
| Vault | 8200 | HTTP | Secrets API |

### Appendix C: Helm Chart Repository Structure

```
embrix-o2x/
├── core/
│   ├── charts/
│   │   ├── service-transactional/
│   │   │   ├── Chart.yaml
│   │   │   ├── values.yaml
│   │   │   └── templates/
│   │   ├── service-billing/
│   │   ├── service-invoice/
│   │   └── ... (other core services)
│   └── helm_values/
│       ├── urbanos/
│       │   ├── service-transactional.yaml
│       │   ├── service-billing.yaml
│       │   └── ...
│       ├── newclient/
│       │   └── ... (tenant-specific values)
│       └── ... (other tenants)
├── finance-gateway/
│   ├── charts/finance-gateway/
│   └── helm_values/
├── payment-gateway/
│   ├── charts/payment-gateway/
│   └── helm_values/
└── ... (other gateways)
```

### Appendix D: Database Schema Overview

**Business Data Schemas (per tenant database):**
- `public.account` - Customer accounts
- `public.subscription` - Active subscriptions
- `public.order` - Order history
- `public.bill` - Bills generated
- `public.invoice` - Invoices generated
- `public.payment` - Payment transactions
- `public.transaction` - Usage transactions
- `public.service_unit` - Service instances
- `public.price_unit` - Pricing instances

**Configuration Schema (shared core_config):**
- `core_config.tenant` - Tenant master data
- `core_config.tenant_merchants` - Gateway configurations
- `core_config.oauth1_attributes` - OAuth1 credentials
- `core_config.oauth2_attributes` - OAuth2 credentials
- `core_config.*_gateway_attributes` - Gateway-specific configs
- `core_config.users` - User accounts
- `core_config.roles` - Role definitions
- `core_config.feature_flags` - Feature toggles

### Appendix E: API Endpoint Reference

**GraphQL API:**
- **Endpoint:** `https://api.{tenant}.embrix.com/graphql`
- **Authentication:** Bearer token (JWT)
- **Rate Limit:** 1000 requests/minute per tenant

**Core Operations:**
- Customer Management: `createCustomer`, `updateCustomer`, `getCustomer`
- Order Management: `createOrder`, `submitOrder`, `getOrder`
- Billing: `triggerBilling`, `getBills`, `getInvoices`
- Payments: `processPayment`, `getPaymentHistory`
- Reports: `generateReport`, `getReportData`

**REST API (Legacy):**
- **Base URL:** `https://api.{tenant}.embrix.com/api/v1`
- **Authentication:** API Key or OAuth2

### Appendix F: Contact Information

**Internal Teams:**
- **DevOps/SRE:** devops@embrix.com, Slack: #devops-support
- **Engineering:** engineering@embrix.com, Slack: #engineering
- **Product:** product@embrix.com
- **Customer Success:** success@embrix.com

**On-Call Rotation:**
- **PagerDuty:** https://embrix.pagerduty.com
- **Escalation Policy:** L1 DevOps → L2 Engineering → L3 Principal Engineer

**Vendor Support:**
- **AWS Support:** Premium Support (Case Portal)
- **HashiCorp Vault:** Enterprise Support
- **QuickBooks API:** Intuit Developer Support
- **Stripe:** Stripe Support Portal

---

## Document Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-02-10 | 1.0 | Initial comprehensive guide created | DevOps Team |

---

**End of Document**
