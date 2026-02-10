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

### What You'll Learn:
- ✅ All 7 core services explained (billing, invoice, usage, payment, etc.)
- ✅ Complete database schema architecture
- ✅ 3 complete end-to-end business flows with code
- ✅ Local development environment setup (step-by-step)
- ✅ Build sequences and dependencies
- ✅ Testing strategies

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

---

## 🎯 Recommended Reading Path

**Choose your learning path based on your role:**

| Role | Day/Phase | Content | Time | Goal |
|------|-----------|---------|------|------|
| **New Developer** | Day 1 AM | Part 1 (Business & Architecture) | 60 min | Understand what you're building |
| | Day 1 PM | Part 2 (Technical Deep Dive) | 90 min | Understand how it's built |
| | Day 2 AM | Part 3 Sections 1-2 (Services & DB) | 60 min | Understand the components |
| | Day 2 PM | Part 3 Sections 3-4 (Flows & Setup) | 90 min | See it in action, set up locally |
| | Day 3 | Explore codebase with guide | Full day | Navigate confidently with context |
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

### Related Documentation:
- `MULTI_TENANT_ARCHITECTURE.md` - Detailed multi-tenancy analysis
- `COMPREHENSIVE_ARCHITECTURE.md` - Original architecture documentation
- `PRODUCT_FLOW_CUSTOMER_JOURNEY_VERIFIED.md` - Customer journey flows
- `CURRENT_TAX_CALCULATION_FLOW.md` - Tax processing details
- Individual service READMEs in each module folder

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

**Total Pages**: ~150 (across 3 parts)  
**Code Examples**: 50+  
**Diagrams**: 15+  
**Business Flows**: 3 complete end-to-end  
**Hub Explanations**: 11 detailed  
**Service Descriptions**: 10 core services  
**Gateway Coverage**: 6 gateways

**Time Investment**:
- Part 1: 45-60 minutes
- Part 2: 60-90 minutes
- Part 3: 90-120 minutes
- **Total**: 3-4.5 hours for complete understanding

**Worth It**: This investment gives you comprehensive knowledge that would take weeks to acquire through code exploration alone.

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

