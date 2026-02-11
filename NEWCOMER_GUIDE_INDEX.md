# Embrix O2X Platform - Complete Newcomer's Guide

**Version**: 3.1.9-SNAPSHOT  
**Last Updated**: February 2026  
**Purpose**: Comprehensive onboarding for new developers, business analysts, and technical stakeholders

---

## 📚 Documentation Structure

This guide is split into 3 comprehensive parts to help you understand everything about the Embrix O2X platform, from business context to hands-on development.

---

## Part 1: Business Overview & System Architecture
**File**: `NEWCOMER_GUIDE_PART1_BUSINESS_AND_ARCHITECTURE.md`  
**Time to Read**: 45-60 minutes

### What You'll Learn:
- ✅ What Embrix O2X is and why it exists
- ✅ Real-world business use cases and customer journeys
- ✅ Current production deployments (MCM Telecom, CoopeG, etc.)
- ✅ High-level system architecture (7 layers explained)
- ✅ Technology stack and rationale (why Groovy, JOOQ, GraphQL, etc.)
- ✅ Multi-tenant architecture model (deployment-level isolation)
- ✅ Key business capabilities matrix

### Key Sections:
1. **What is Embrix O2X?** - Platform definition and target market
2. **Business Purpose & Use Cases** - Real scenarios with detailed flows
3. **Current Production Deployments** - Live tenant information
4. **System Architecture Overview** - Layered architecture diagrams
5. **Technology Stack** - Complete technology inventory with explanations
6. **Multi-Tenant Architecture** - How tenants are isolated
7. **Key Business Capabilities** - What the platform can do

### Who Should Read This:
- New developers joining the team
- Business analysts understanding the product
- Technical stakeholders evaluating the platform
- Anyone needing high-level system understanding

---

## Part 2: Technical Deep Dive & Component Architecture
**File**: `NEWCOMER_GUIDE_PART2_TECHNICAL_DEEP_DIVE.md`  
**Time to Read**: 60-90 minutes

### What You'll Learn:
- ✅ Foundation layer (engine, common, oms-component, gateway-common)
- ✅ Hub-based business logic organization (11 hubs explained)
- ✅ Gateway layer (crm_gateway, provision_gateway, tax-gateway, etc.)
- ✅ JOOQ data access patterns
- ✅ Flyway database migrations
- ✅ Apache Camel orchestration framework
- ✅ External system integrations

### Key Sections:
1. **Foundation Layer - Shared Libraries**
   - The `engine` module (heart of the system)
   - Hub-based organization (arHub, billingHub, customerHub, etc.)
   - Real-world hub examples with code
   - JOOQ data access patterns
   - Flyway migration structure

2. **Gateway Layer**
   - `crm_gateway` - The front door (GraphQL API, OAuth2)
   - `provision_gateway` - Service activation
   - `tax-gateway` & `tax-engine` - Tax compliance
   - `payment-gateway` - Payment processing
   - `finance-gateway` - ERP integration

### Who Should Read This:
- Developers who need to understand the codebase structure
- Architects evaluating the technical design
- Anyone implementing new features or integrations
- Tech leads planning modifications

### Code Examples Included:
- Hub service implementations
- JOOQ query patterns
- Flyway migration templates
- Apache Camel routes
- GraphQL schemas
- OAuth2 flows

---

## Part 3: Core Services, Business Flows & Development Guide
**File**: `NEWCOMER_GUIDE_PART3_SERVICES_AND_DEVELOPMENT.md`  
**Time to Read**: 90-120 minutes

---

## Part 4: Frontend Applications & User Interfaces
**File**: `NEWCOMER_GUIDE_PART4_FRONTEND_AND_UI.md`  
**Time to Read**: 60-90 minutes
**Status**: ✨ NEW - February 2026

### What You'll Learn:
- ✅ All 7 core services explained (billing, invoice, usage, payment, etc.)
- ✅ Complete database schema architecture
- ✅ 3 complete end-to-end business flows with code
- ✅ Local development environment setup (step-by-step)
- ✅ Build sequences and dependencies
- ✅ Testing strategies

---

## Part 4: Frontend Applications & User Interfaces
**File**: `NEWCOMER_GUIDE_PART4_FRONTEND_AND_UI.md`  
**Time to Read**: 60-90 minutes
**Status**: ✨ NEW - February 2026

### What You'll Learn:
- ✅ All 4 React frontend applications (ui-core, selfcare, ui, embrix-lite)
- ✅ Complete customer journey flows (registration, billing, payments, usage)
- ✅ GraphQL API integration patterns with Apollo Client
- ✅ OAuth2/JWT authentication implementation
- ✅ Multi-tenant branding and theming
- ✅ State management and routing patterns
- ✅ Build and deployment configurations

### Key Sections:
1. **Core Services Layer**
   - `service-billing` - Billing operations (proration, discounts)
   - `service-invoice` - Invoice generation (PDF, CFDI)
   - `service-usage` - Usage data repository
   - `service-mediation` - CDR ingestion and normalization
   - `service-payment` - Payment processing
   - `service-revenue` - Revenue recognition (IFRS 15)
   - `batch-process` - Background jobs

2. **Database Architecture**
   - Schema organization (9 schemas explained)
   - Key tables deep dive (account, order, invoice, usage_record)
   - Partitioning strategy
   - Performance optimizations
   - Indexing patterns

3. **Complete End-to-End Business Flows**
   - **Flow 1**: New Customer Signup → First Invoice (30-day timeline)
   - **Flow 2**: Mobile Customer Usage Processing (CDR → Rating → Billing)
   - **Flow 3**: Service Suspension → Auto-Resume (EP-5480 feature)

4. **Development Environment Setup**
   - Prerequisites (Java 8, Maven, Docker)
   - Infrastructure setup (PostgreSQL, ActiveMQ, Redis, Vault)
   - Database migrations
   - Build sequences
   - Running services locally

### Who Should Read This:
- Developers starting hands-on coding
- Anyone setting up local development environment
- QA engineers understanding test data flows
- DevOps understanding deployment requirements

### Practical Guides Included:
- Docker commands for all infrastructure
- Vault secret configuration
- Database setup and migrations
- Build order and dependencies
- GraphQL query examples
- Testing setup

### Key Sections:
1. **Frontend Architecture Overview**
   - 4 React applications and their purposes
   - Technology stack (React 16.x, Apollo Client, Material-UI)
   
2. **ui-core (Admin Portal)**
   - Tenant onboarding and configuration
   - System administration dashboards
   - User and role management
   
3. **selfcare (Customer Portal)**
   - Customer registration and authentication
   - Billing and invoice viewing
   - Payment processing (Braintree integration)
   - Usage reports and CDR viewing
   - Service upgrade workflows
   
4. **API Integration Patterns**
   - GraphQL client setup
   - Authentication flows
   - Error handling
   - State management

### Who Should Read This:
- Frontend developers
- Full-stack developers
- UI/UX designers
- Anyone working on customer-facing or admin interfaces

### Code Examples Included:
- React component structures
- GraphQL queries and mutations
- Authentication service implementation
- Theme provider with dynamic branding
- CI/CD pipeline configurations

---

## Part 5: Message Queue Architecture & Integration Patterns
**File**: `NEWCOMER_GUIDE_PART5_MESSAGE_QUEUES_AND_INTEGRATION.md`  
**Time to Read**: 75-105 minutes
**Status**: ✨ NEW - February 2026

### What You'll Learn:
- ✅ ActiveMQ infrastructure (Amazon MQ deployment + local setup)
- ✅ Complete inventory of 10+ production queues
- ✅ Message flow patterns (order-to-cash, usage pipeline, bulk operations)
- ✅ Error handling and retry mechanisms with exponential backoff
- ✅ Message formats for all queue types with JSON examples
- ✅ Performance tuning and monitoring strategies
- ✅ Development guide (creating consumers and producers)
- ✅ Troubleshooting common issues (high queue depth, DLQ, duplicates)

### Key Sections:
1. **ActiveMQ Infrastructure**
   - Amazon MQ broker architecture
   - Docker Compose local setup
   - Connection configuration with Vault

2. **Queue Inventory**
   - OMS (Order intake from CRM)
   - PROVISIONING_RESPONSE (Network callbacks)
   - MEDIATION (CDR file processing - 100,000+ records/batch)
   - USAGE (Usage rating - hourly batches)
   - BULK (Bulk operations - invoice regeneration, payments)
   - And 5+ more queues

3. **Message Flow Patterns**
   - Order-to-Cash (async order processing with provisioning callbacks)
   - Usage Rating Pipeline (MEDIATION → USAGE → Billing)
   - Bulk Operations (parallel processing with chunking)
   - Time breakdowns and performance metrics

4. **Error Handling**
   - Retryable vs NonRetryable exceptions
   - Exponential backoff configuration (7 retries, 250ms → 2841ms)
   - Dead Letter Queue (DLQ) management
   - Reprocessing strategies

5. **Development Guide**
   - Creating queue consumers (step-by-step with code)
   - Sending messages (producer patterns)
   - Integration testing examples
   - Best practices and anti-patterns

6. **Monitoring & Performance**
   - Key metrics (queue depth, throughput, consumer lag)
   - ActiveMQ console monitoring
   - Grafana dashboard queries
   - Performance tuning (concurrent consumers, prefetch, persistence)

### Who Should Read This:
- Backend developers
- Integration engineers
- DevOps engineers
- Anyone working with asynchronous processing or external integrations

### Code Examples Included:
- Consumer implementation with error handling
- Producer implementation with batch sending
- Integration test examples
- Monitoring and alerting queries
- DLQ reprocessing scripts

---

## 🎯 Recommended Reading Path

**Choose your learning path based on your role:**

| Role | Day/Phase | Content | Time | Goal |
|------|-----------|---------|------|------|
| **New Developer** | Day 1 AM | Part 1 (Business & Architecture) | 60 min | Understand what you're building |
| | Day 1 PM | Part 2 (Technical Deep Dive) | 90 min | Understand how it's built |
| | Day 2 AM | Part 3 Sections 1-2 (Services & DB) | 60 min | Understand the components |
| | Day 2 PM | Part 3 Sections 3-4 (Flows & Setup) | 90 min | See it in action, set up locally |
| | Day 3 AM | Part 4 (Frontend Applications) | 90 min | Understand UI architecture |
| | Day 3 PM | Part 5 (Message Queues) | 105 min | Master async messaging patterns |
| | Day 4 | Explore codebase with guide | Full day | Navigate confidently with context |
| **Business Analyst** | Phase 1 | Part 1 (Full) | 60 min | Business use cases, capabilities |
| | Phase 2 | Part 2 Sections 1-2 (Gateways) | 30 min | External integrations |
| | Phase 3 | Part 3 Section 3 (Business Flows) | 45 min | End-to-end scenarios |
| **Technical Evaluator** | Phase 1 | Part 1 Sections 1, 4, 5, 6 | 45 min | Architecture, technology, multi-tenancy |
| | Phase 2 | Part 2 (Full) | 90 min | Technical implementation details |
| | Phase 3 | Part 3 Section 2 (Database) | 30 min | Data model and performance |
| **QA Engineer** | Phase 1 | Part 1 Sections 1-2 | 30 min | Business use cases |
| | Phase 2 | Part 3 Section 3 (Business Flows) | 60 min | Test scenarios |
| | Phase 3 | Part 3 Section 4 (Development Setup) | 45 min | Test environment setup |

---

## 📖 Quick Reference Guide

### Business Use Cases Covered:

| Use Case | Flow | Documentation |
|----------|------|---------------|
| **New Customer Signup** | Internet service order → provisioning → first invoice | Part 3, Section 3.1 |
| **Mobile Usage Processing** | Phone calls → CDR mediation → rating → billing | Part 3, Section 3.2 |
| **Service Suspension/Resume** | Overdue payment → suspension → payment → auto-resume | Part 3, Section 3.3 |
| **Payment Processing** | Bank file upload → payment allocation → invoice updates | Part 2, Section 2.4 |
| **Tax Compliance** | Invoice generation → CFDI XML → PAC stamping → delivery | Part 2, Section 2.3 |

### Architecture Patterns Explained:
- **Shared Engine Pattern** - Centralized business logic in `engine`
- **Event-Driven Architecture** - ActiveMQ message queues
- **Gateway Pattern** - External system isolation
- **GraphQL-First API** - Flexible data fetching
- **Hub-Based Organization** - Domain-driven design
- **Multi-Tenant Deployment** - Database-per-tenant isolation

### Technologies Covered:
- **Backend**: Java 8, Groovy 2.4.15, Spring Boot 2.1.4
- **API**: GraphQL Java 5.0.2
- **Data**: PostgreSQL 10.5, JOOQ 3.11.10, Flyway 5.2.4
- **Messaging**: Apache Camel 2.23.1, ActiveMQ 5.15.9
- **Security**: Vault 2.0.2, OAuth2, JWT
- **Documents**: iText 7.1.5, Thymeleaf 3.0.11
- **Infrastructure**: Docker, Kubernetes, Helm

### Hubs in Engine:

| Hub | Purpose | Key Responsibilities |
|-----|---------|---------------------|
| **arHub** | Accounts Receivable | Payments, collections, payment allocation |
| **billingHub** | Billing Operations | Billing cycles, proration, discounts, invoice generation |
| **customerHub** | Customer Management | Accounts, orders, subscriptions, contacts |
| **pricingHub** | Product Catalog | Products, pricing, bundles, promotions |
| **revenueHub** | Revenue Recognition | IFRS 15, ASC 606, deferred revenue, schedules |
| **usageProcessHub** | Usage Rating | Charge calculation, pricing plan application |
| **mediationHub** | Usage Mediation | CDR processing, normalization, deduplication |
| **opsHub** | Operations | Users, jobs, notifications, tenants, permissions |
| **commonHub** | Shared Services | Documents, files, templates, utilities |
| **migrationHub** | Data Migration | Legacy system migration, data import |
| **selfCareHub** | Customer Self-Service | Self-care portal APIs, customer actions |

### Core Services:

| Service | Purpose | Key Features |
|---------|---------|--------------|
| **service-billing** | Billing cycle execution | Invoice generation, proration, recurring charges |
| **service-invoice** | Invoice document generation | PDF/HTML/XML creation, templates |
| **service-usage** | Usage data repository | CDR storage, usage aggregation |
| **service-mediation** | CDR ingestion | Usage import, normalization, deduplication |
| **service-payment** | Payment processing | Payment application, reconciliation |
| **service-revenue** | Revenue recognition | GAAP compliance, deferred revenue |
| **service-transactional** | Real-time operations | GraphQL API, main business logic |
| **service-sso** | Single sign-on | Authentication, authorization, JWT |
| **service-proxy** | API gateway | Request routing, rate limiting |
| **batch-process** | Background jobs | Scheduled jobs, billing runs, reports |

### Gateways:

| Gateway | Port | Integration Target | Purpose |
|---------|------|-------------------|---------|
| **crm_gateway** | 8080 | Salesforce, MS Dynamics | CRM integration, order capture |
| **provision_gateway** | 8081 | Nokia, ServiceNow, Cisco | Network provisioning, equipment config |
| **tax-gateway** | 8082 | Avalara, PAC providers | Tax calculation, CFDI stamping |
| **payment-gateway** | 8083 | Stripe, Braintree, banks | Payment processing, bank files |
| **finance-gateway** | 8084 | QuickBooks, NetSuite, SAP | ERP integration, GL posting |
| **diameter-gateway** | 8085 | Network elements | Real-time charging, quota management |

---

## 🔗 Additional Resources

### Core Documentation Suite:
- **`COMPLETE_SYSTEM_OVERVIEW.md`** - Complete bird's-eye view of entire platform ⭐ **NEW**
- **`FRONTEND_UI_ARCHITECTURE.md`** - Complete frontend/UI guide (React apps, GraphQL) ⭐ **NEW**
- **`DATABASE_ARCHITECTURE_COMPLETE.md`** - Complete database reference (50+ tables) ⭐ **NEW**
- **`INFRASTRUCTURE_OPERATIONS_GUIDE.md`** - Infrastructure & operations (K8s, AWS, monitoring) ⭐ **NEW**
- `MULTI_TENANT_ARCHITECTURE.md` - Detailed multi-tenancy analysis
- `BUSINESS_SCENARIOS_AND_WORKFLOWS.md` - Real-world business scenarios
- `COMPREHENSIVE_ARCHITECTURE.md` - Original architecture documentation

### Specialized Guides:
- `QUICK_START.md` - Quick setup and getting started
- `QUICK_REFERENCE_GUIDE.md` - Quick reference for common tasks
- `DEPLOYMENT_GUIDE.md` - Deployment procedures
- `STEP_BY_STEP_DEPLOYMENT.md` - Step-by-step deployment guide
- Individual service READMEs in each module folder

### Upgrade Documentation:
- `UPGRADE_PROGRESS_TRACKER.md` - Dependency upgrade tracking
- `DEPENDENCIES_UPGRADE_GUIDE.md` - Complete upgrade guide
- `DEPENDENCY_UPGRADE_MASTER_PLAN.md` - Master upgrade plan
- `HIBERNATE_PROXY_BEST_PRACTICES.md` - Hibernate upgrade guide

### Codebase Entry Points:
```
Recommended exploration order:
1. common/src/main/groovy/com/embrix/core/common/enums/
   └─→ Understand domain enums

2. engine/src/main/groovy/com/embrix/core/engine/{hub}/
   └─→ Explore business logic by hub

3. crm_gateway/src/main/resources/graphql/
   └─→ See GraphQL schema

4. core/service-*/src/main/groovy/
   └─→ Understand service implementations

5. gateway-common/src/main/groovy/
   └─→ Gateway integration patterns
```

### Development Tools:
- **GraphQL Playground**: http://localhost:8080/graphiql
- **ActiveMQ Console**: http://localhost:8161 (admin/admin)
- **Vault UI**: http://localhost:8200/ui
- **PostgreSQL**: `psql -U omsadmin -d omsdevdb`
- **Redis CLI**: `docker exec -it redis redis-cli`

---

## 💡 Getting Help

### Common Questions:
- **Q**: Where is business logic for billing?
  - **A**: `engine/src/main/groovy/com/embrix/core/engine/billingHub/`

- **Q**: How do I add a new GraphQL endpoint?
  - **A**: See Part 2, Section 2.1.2 (GraphQL Schema)

- **Q**: Where are database tables defined?
  - **A**: `engine/src/main/resources/db/migration/`

- **Q**: How do orders flow through the system?
  - **A**: See Part 3, Section 3.1 (Complete Business Flow)

- **Q**: How do I set up local development?
  - **A**: Follow Part 3, Section 4 step-by-step

### Troubleshooting:
- **Build Errors**: Check dependency order (common → engine → services)
- **Database Connection**: Verify Docker containers running (`docker ps`)
- **Vault Secrets**: Ensure VAULT_URI and VAULT_TOKEN set
- **ActiveMQ**: Check broker running on port 61616
- **GraphQL 404**: Verify service started on correct port

---

## 📈 Document Statistics

**Total Pages**: ~270 (across 5 parts + supplementary guides)  
**Code Examples**: 190+  
**Diagrams**: 45+  
**Business Flows**: 8+ complete end-to-end  
**Hub Explanations**: 11 detailed  
**Service Descriptions**: 10+ core services  
**Gateway Coverage**: 8 gateways  
**Queue Documentation**: 10+ ActiveMQ queues  
**Frontend Applications**: 4 React apps fully documented

**Time Investment**:
- Part 1: 45-60 minutes (Business & Architecture)
- Part 2: 60-90 minutes (Technical Deep Dive)
- Part 3: 90-120 minutes (Services & Development)
- Part 4: 60-90 minutes (Frontend & UI) ✨ NEW
- Part 5: 75-105 minutes (Message Queues) ✨ NEW
- **Total**: 5.5-7.5 hours for complete understanding

**Worth It**: This investment gives you comprehensive knowledge that would take 3-4 weeks to acquire through code exploration alone. With these guides, you'll be productive in 1 week.

---

## 🚀 Next Steps After Reading

1. **Set Up Local Environment**
   - Follow Part 3, Section 4
   - Get all infrastructure running
   - Build and run crm_gateway

2. **Explore Codebase**
   - Navigate hubs in engine
   - Read GraphQL schemas
   - Review database migrations

3. **Run a Test Transaction**
   - Create an account via GraphQL
   - Submit an order
   - Track it through the system

4. **Pick a Small Task**
   - Find a simple bug or feature request
   - Implement using patterns from guide
   - Write tests following examples

5. **Contribute**
   - Understand the architecture
   - Follow established patterns
   - Ask questions when stuck

---

## 📝 Document Maintenance

**This guide should be updated when:**
- New major features are added
- Architecture changes significantly
- New services or gateways are introduced
- Technology stack is upgraded
- Production deployments change

**Last Updated**: February 2026  
**Maintainer**: Development Team  
**Review Frequency**: Quarterly

---

**Welcome to Embrix O2X! Happy Coding! 🎉**

