# Embrix O2X Platform - Newcomer's Guide (Part 4)
## Frontend Applications & User Interfaces

**Version**: 3.1.9-SNAPSHOT  
**Last Updated**: February 2026  
**Prerequisites**: Read Parts 1, 2, and 3 first  
**Target Audience**: Frontend developers, full-stack developers, UI/UX designers

---

## Table of Contents - Part 4

1. [Frontend Architecture Overview](#1-frontend-architecture-overview)
2. [ui-core - Admin & Operations Application](#2-ui-core---admin--operations-application)
3. [selfcare - Customer Self-Service Portal](#3-selfcare---customer-self-service-portal)
4. [ui - Public Website & Discovery](#4-ui---public-website--discovery)
5. [embrix-lite - Lightweight UI Variant](#5-embrix-lite---lightweight-ui-variant)
6. [API Integration Patterns](#6-api-integration-patterns)
7. [Authentication & Authorization](#7-authentication--authorization)
8. [Multi-Tenant Branding & Customization](#8-multi-tenant-branding--customization)
9. [State Management & Routing](#9-state-management--routing)
10. [Build & Deployment](#10-build--deployment)

---

## 1. Frontend Architecture Overview

### 1.1 Application Ecosystem

Embrix O2X provides **four React-based frontend applications**, each serving distinct user roles and use cases:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND ECOSYSTEM                              │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│   ui-core            │  │   selfcare           │  │   ui                 │
│   (Admin Portal)     │  │   (Customer Portal)  │  │   (Public Site)      │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│ • Tenant onboarding  │  │ • Customer login     │  │ • Package comparison │
│ • System config      │  │ • View bills         │  │ • Sign-up flows      │
│ • User management    │  │ • Make payments      │  │ • Marketing pages    │
│ • Ops dashboard      │  │ • Usage reports      │  │ • Lead generation    │
│ • Analytics          │  │ • Service upgrades   │  │ • Product info       │
└──────────┬───────────┘  └──────────┬───────────┘  └──────────┬───────────┘
           │                         │                         │
           │                         │                         │
           └─────────────────────────┴─────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       GraphQL API (crm_gateway)                          │
│                       http://localhost:8080/graphql                      │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       Backend Services Layer                             │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   embrix-lite        │
│   (Lightweight)      │
├──────────────────────┤
│ • Simplified UI      │
│ • Reduced features   │
│ • Faster load times  │
└──────────────────────┘
```

### 1.2 Technology Stack

| Application | Framework | Version | Build Tool | State Management |
|-------------|-----------|---------|------------|------------------|
| **ui-core** | React | 16.12.0 | React Scripts 3.2.0 | Context API / Redux (likely) |
| **selfcare** | React | 16.8.6 | React Scripts 3.0.1 | Context API / Redux (likely) |
| **ui** | React | 16.12.0 | React Scripts 3.2.0 | Context API |
| **embrix-lite** | React | 16.12.0 | React Scripts 3.2.0 | Context API |

**Common Dependencies**:
- **GraphQL Client**: Apollo Client or similar
- **HTTP Client**: Axios / Fetch API
- **Routing**: React Router
- **UI Components**: Material-UI or custom components
- **Form Management**: Formik / React Hook Form
- **Authentication**: OAuth2/JWT with Vault integration

### 1.3 Application Separation Rationale

| Concern | Benefit of Separate Apps |
|---------|-------------------------|
| **Security** | Admin operations isolated from customer access |
| **Performance** | Smaller bundle sizes, faster load times |
| **Scalability** | Independent deployment and scaling |
| **User Experience** | Tailored UX for different user roles |
| **Development** | Teams can work independently on different apps |

---

## 2. ui-core - Admin & Operations Application

### 2.1 Purpose & Target Users

**Purpose**: Internal operations and administration for service provider staff

**Target Users**:
- System administrators
- Operations managers
- Finance team members
- Customer support agents
- Implementation consultants

### 2.2 Key Features

#### 2.2.1 Tenant Onboarding

**What It Is**: Complete tenant provisioning and configuration workflow

**Steps**:
1. **Tenant Creation**
   ```javascript
   const tenantData = {
     tenantName: "newclient",
     tenantCode: "TIDLT-100008",
     domain: "newclient.embrix.com",
     logoUrl: "https://s3.../logo.png",
     themeColors: {
       primaryColor: "#1976D2",
       secondaryColor: "#DC004E"
     },
     supportEmail: "support@newclient.com",
     supportPhone: "+1-555-0100"
   };
   ```

2. **Self-Care Configuration**
   ```javascript
   const selfCareConfig = {
     tenantId: "TIDLT-100008",
     enableSelfRegistration: true,
     enableCreditCardPayment: true,
     enableUsageReports: true,
     enableVoiceCDR: false,
     enableDataCDR: true,
     defaultLanguage: "en-US",
     supportedLanguages: ["en-US", "es-MX"],
     permissions: {
       VIEW_BILLS: true,
       VIEW_INVOICE: true,
       ADD_CREDIT_CARD: true,
       MAKE_PAYMENT: true,
       VIEW_USAGE: true
     }
   };
   ```

3. **Gateway Configuration**
   - Payment gateway credentials (Stripe, Braintree)
   - Tax provider setup (Avalara, PAC)
   - ERP integration (QuickBooks, NetSuite)
   - Provisioning system connection

4. **Database Provisioning**
   ```sql
   -- Automated via backend
   CREATE DATABASE coredb_newclient;
   -- Run Flyway migrations
   -- Seed initial data
   ```

#### 2.2.2 System Configuration Dashboard

**Configuration Screens**:

| Screen | Purpose | Key Actions |
|--------|---------|-------------|
| **Tenants List** | View all tenants | Create, Edit, Deactivate |
| **Tenant Details** | Configure specific tenant | Update settings, View health |
| **Gateway Management** | External system configs | Add/Edit credentials, Test connection |
| **Feature Flags** | Enable/disable features per tenant | Toggle features, Set rollout % |
| **Rate Plans** | Configure billing rates | Create plans, Set pricing tiers |
| **Product Catalog** | Manage products | Add products, Bundle configuration |

#### 2.2.3 User & Role Management

**User Management Features**:
- Create/Edit/Deactivate users
- Assign roles and permissions
- Bulk user import
- Password reset workflows
- Session management

**Role Examples**:
```javascript
const roles = [
  {
    name: "SUPER_ADMIN",
    permissions: ["*"]  // All permissions
  },
  {
    name: "TENANT_ADMIN",
    permissions: [
      "VIEW_DASHBOARD",
      "MANAGE_USERS",
      "CONFIGURE_TENANT",
      "VIEW_REPORTS"
    ]
  },
  {
    name: "FINANCE_MANAGER",
    permissions: [
      "VIEW_INVOICES",
      "VIEW_PAYMENTS",
      "EXPORT_REPORTS",
      "MANAGE_PRICING"
    ]
  },
  {
    name: "CUSTOMER_SUPPORT",
    permissions: [
      "VIEW_ACCOUNTS",
      "VIEW_ORDERS",
      "CREATE_TICKETS",
      "APPLY_CREDITS"
    ]
  }
];
```

#### 2.2.4 Operations Dashboard

**Key Metrics Displayed**:
```
┌─────────────────────────────────────────────────────────────┐
│ System Health Dashboard                                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Active Tenants: 7          Total Accounts: 15,234          │
│  Orders Today: 142          Invoices Generated: 1,053        │
│  Payments: $125,340         Failed Orders: 3                 │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐│
│  │ Message Queues  │  │ Service Status  │  │ DB Health    ││
│  ├─────────────────┤  ├─────────────────┤  ├──────────────┤│
│  │ OMS: 23         │  │ Billing: ✅     │  │ Conn: 45/50  ││
│  │ USAGE: 1,234    │  │ Invoice: ✅     │  │ Queries: 120 ││
│  │ MEDIATION: 5    │  │ Payment: ⚠️     │  │ Locks: 2     ││
│  │ BULK: 0         │  │ Usage: ✅       │  │ Size: 145GB  ││
│  └─────────────────┘  └─────────────────┘  └──────────────┘│
│                                                               │
│  Recent Errors:                                              │
│  • Payment gateway timeout (3 occurrences)                   │
│  • CDR file parsing error (mcm_2024_02_11.csv)              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Component Structure

**Example Component Hierarchy**:
```
ui-core/
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   │   ├── SystemHealth.jsx
│   │   │   ├── QueueMetrics.jsx
│   │   │   └── ServiceStatus.jsx
│   │   ├── Tenants/
│   │   │   ├── TenantList.jsx
│   │   │   ├── TenantForm.jsx
│   │   │   ├── TenantDetails.jsx
│   │   │   └── SelfCareConfig.jsx
│   │   ├── Users/
│   │   │   ├── UserList.jsx
│   │   │   ├── UserForm.jsx
│   │   │   └── RoleAssignment.jsx
│   │   ├── Gateways/
│   │   │   ├── GatewayList.jsx
│   │   │   ├── GatewayConfig.jsx
│   │   │   └── ConnectionTest.jsx
│   │   └── Common/
│   │       ├── Header.jsx
│   │       ├── Sidebar.jsx
│   │       └── ErrorBoundary.jsx
│   ├── pages/
│   │   ├── DashboardPage.jsx
│   │   ├── TenantsPage.jsx
│   │   ├── UsersPage.jsx
│   │   └── SettingsPage.jsx
│   ├── services/
│   │   ├── api.js              // GraphQL client
│   │   ├── auth.js             // Authentication
│   │   └── tenantService.js    // Tenant operations
│   ├── utils/
│   │   ├── validation.js
│   │   └── formatters.js
│   └── App.jsx
└── package.json
```

---

## 3. selfcare - Customer Self-Service Portal

### 3.1 Purpose & Target Users

**Purpose**: Customer-facing portal for account self-management

**Target Users**:
- End customers (residential)
- Business customers (small-medium)
- Account administrators
- Authorized users

### 3.2 Customer Journey & Features

#### 3.2.1 Registration & Onboarding

**Self-Registration Flow**:
```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Email Verification                                   │
│ • Enter email address                                        │
│ • Receive verification code                                  │
│ • Validate code                                              │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Account Lookup                                       │
│ • Enter account number or service address                    │
│ • System validates eligibility                               │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Create Credentials                                   │
│ • Set password (strength requirements)                       │
│ • Set security questions                                     │
│ • Accept terms of service                                    │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Welcome & Dashboard                                  │
│ • Account overview                                           │
│ • Pending bills                                              │
│ • Quick actions                                              │
└─────────────────────────────────────────────────────────────┘
```

**GraphQL Registration Mutation**:
```javascript
const REGISTER_SELF_CARE_USER = gql`
  mutation RegisterSelfCareUser($input: SelfCareRegistrationInput!) {
    registerSelfCareUser(input: $input) {
      userId
      status
      activationToken
      errors {
        field
        message
      }
    }
  }
`;

// Usage
const { data } = await apolloClient.mutate({
  mutation: REGISTER_SELF_CARE_USER,
  variables: {
    input: {
      email: "customer@example.com",
      password: "SecurePass123!",
      accountId: "ACC-1001",
      firstName: "Jane",
      lastName: "Customer",
      phone: "+52 55 9876 5432"
    }
  }
});
```

#### 3.2.2 Dashboard & Account Overview

**Dashboard Components**:

```
┌─────────────────────────────────────────────────────────────┐
│ Customer Dashboard                              👤 Jane Doe  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Account Summary                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Account ID: ACC-1001          Status: ✅ Active         │ │
│ │ Current Balance: -$125.00     Next Bill Date: Feb 28    │ │
│ │ Bill Cycle Day: 28th          Payment Method: ****1234  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ Active Services                                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🌐 Internet 100 Mbps              $50.00/month          │ │
│ │ 📺 Cable TV Premium               $79.99/month          │ │
│ │ ☎️  VoIP Business Line            $29.99/month          │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ Quick Actions                                                │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│ │💳 Pay Bill│ │📄 Invoices│ │📊 Usage  │ │⚙️ Settings│       │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                               │
│ Recent Activity                                              │
│ • Invoice INV-2024-002 generated ($159.98) - Feb 10         │
│ • Payment $159.98 received - Feb 8                          │
│ • Speed upgrade activated - Jan 25                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Dashboard Query**:
```javascript
const DASHBOARD_QUERY = gql`
  query GetCustomerDashboard($accountId: String!) {
    getAccount(id: $accountId) {
      id
      status
      balance
      billCycleDay
      nextBillingDate
      subscriptions {
        id
        productCode
        productName
        status
        recurringCharge
        activationDate
      }
      paymentMethods {
        id
        type
        last4
        expiryDate
        isDefault
      }
      recentActivity {
        date
        type
        description
        amount
      }
    }
  }
`;
```

#### 3.2.3 Billing & Invoices

**View Bills Screen**:
```
┌─────────────────────────────────────────────────────────────┐
│ My Bills                                                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Filters: [All] [Paid] [Pending] [Overdue]                   │
│ Date Range: [Last 12 Months ▼]                              │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Invoice #INV-2024-002          Amount: $159.98          │ │
│ │ Date: Feb 10, 2024             Due: Feb 28, 2024        │ │
│ │ Status: ⚠️ PENDING             [Download PDF] [Pay Now] │ │
│ │                                                           │ │
│ │ Charges:                                                  │ │
│ │   Internet 100 Mbps          $50.00                      │ │
│ │   Cable TV Premium           $79.99                      │ │
│ │   VoIP Business Line         $29.99                      │ │
│ │   Subtotal:                 $159.98                      │ │
│ │   Tax (16%):                 $25.60                      │ │
│ │   Total:                    $185.58                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Invoice #INV-2024-001          Amount: $159.98          │ │
│ │ Date: Jan 10, 2024             Due: Jan 28, 2024        │ │
│ │ Status: ✅ PAID                [Download PDF]            │ │
│ │ Payment: Jan 25, 2024 via Bank Transfer                  │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Invoices Query**:
```javascript
const VIEW_BILLS_QUERY = gql`
  query ViewMyBills($filter: BillFilterInput!) {
    myBills(filter: $filter) {
      invoices {
        id
        invoiceNumber
        invoiceDate
        dueDate
        subtotal
        taxTotal
        totalAmount
        amountPaid
        balance
        status
        pdfUrl
        canDownload
        charges {
          description
          chargeType
          amount
          taxAmount
          totalAmount
        }
        payments {
          paymentDate
          amount
          paymentMethod
        }
      }
      summary {
        totalInvoices
        totalAmount
        totalPaid
        totalDue
      }
    }
  }
`;
```

#### 3.2.4 Payment Management

**Make Payment Screen**:
```
┌─────────────────────────────────────────────────────────────┐
│ Make a Payment                                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Account Balance: $185.58                                     │
│                                                               │
│ Select Invoices to Pay:                                     │
│ ☑️ INV-2024-002  Due: Feb 28  Amount: $185.58               │
│ ☐ INV-2024-001  Due: Jan 28  Amount: $0.00 (Paid)          │
│                                                               │
│ Payment Amount: $185.58                                      │
│                                                               │
│ Payment Method:                                              │
│ ( ) Credit Card ending in 1234                              │
│ ( ) Bank Transfer                                            │
│ (•) New Payment Method                                       │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Card Number:   [____-____-____-____]                     │ │
│ │ Expiry:        [MM] / [YY]                               │ │
│ │ CVV:           [___]                                      │ │
│ │ Name on Card:  [____________________________]            │ │
│ │ ☑️ Save this payment method for future use               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ [Cancel]                              [Process Payment $185.58]│
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Payment Processing**:
```javascript
const PROCESS_PAYMENT = gql`
  mutation ProcessPayment($input: PaymentInput!) {
    processPayment(input: $input) {
      paymentId
      status
      transactionId
      confirmationNumber
      allocations {
        invoiceId
        amount
        remainingBalance
      }
      accountBalance
      errors {
        code
        message
      }
    }
  }
`;

// Braintree tokenization (client-side)
const BraintreeVaultController = {
  tokenizeCard: async (cardData) => {
    const response = await fetch('/api/payment/tokenize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cardData)
    });
    return response.json(); // { token: "tok_xxxxx" }
  }
};

// Payment submission
const submitPayment = async () => {
  // 1. Tokenize card (PCI-compliant)
  const { token } = await BraintreeVaultController.tokenizeCard({
    number: cardNumber,
    expiryMonth: expiryMM,
    expiryYear: expiryYY,
    cvv: cvv
  });

  // 2. Process payment with token
  const { data } = await apolloClient.mutate({
    mutation: PROCESS_PAYMENT,
    variables: {
      input: {
        accountId: "ACC-1001",
        paymentMethodToken: token,
        amount: 185.58,
        allocateToInvoices: [
          { invoiceId: "INV-2024-002", amount: 185.58 }
        ],
        savePaymentMethod: true
      }
    }
  });

  // 3. Show confirmation
  if (data.processPayment.status === "COMPLETED") {
    showSuccessMessage("Payment processed successfully!");
  }
};
```

#### 3.2.5 Usage Reports & CDR Viewing

**Usage Reports Screen**:
```
┌─────────────────────────────────────────────────────────────┐
│ Usage Reports                                                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Period: [January 2024 ▼]                                    │
│ Service: [All Services ▼]                                    │
│                                                               │
│ Usage Summary                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📞 Voice:     450 minutes     Charges: $15.50           │ │
│ │ 📱 SMS:       120 messages    Charges: $2.40            │ │
│ │ 🌐 Data:      25.5 GB         Charges: $0.00 (included)│ │
│ │                                                           │ │
│ │ Total Usage Charges: $17.90                              │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ Daily Usage Chart                                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │        📊 [Bar chart showing daily usage]                │ │
│ │ GB                                                        │ │
│ │ 2.0│     █                                               │ │
│ │ 1.5│   █ █ █   █                                         │ │
│ │ 1.0│ █ █ █ █ █ █ █                                       │ │
│ │ 0.5│ █ █ █ █ █ █ █ █                                     │ │
│ │ 0.0└─────────────────────                                │ │
│ │     1 2 3 4 5 6 7 8 ... 31                               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ Voice CDR (Last 50 calls)        [Export to CSV]            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Date/Time          Number Called    Duration    Cost    │ │
│ │ Feb 11 10:45 AM    +52 55 1234 5678  12:34     $0.45   │ │
│ │ Feb 11 09:15 AM    +1 415 555 0199   5:12      $0.18   │ │
│ │ Feb 10 03:30 PM    +52 55 9876 5432  25:18     $0.89   │ │
│ │ ...                                                       │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Usage Query**:
```javascript
const USAGE_SUMMARY_QUERY = gql`
  query GetUsageSummary($input: UsageSummaryInput!) {
    getUsageSummary(input: $input) {
      voiceMinutes
      smsCount
      dataGB
      totalCharges
      breakdown {
        date
        voiceMinutes
        smsCount
        dataGB
        charges
      }
    }
    
    getVoiceCDR(input: {
      accountId: $accountId
      periodStart: $periodStart
      periodEnd: $periodEnd
    }) {
      records {
        timestamp
        calledNumber
        duration
        cost
        callType
      }
    }
  }
`;
```

#### 3.2.6 Service Upgrades

**Upgrade Service Flow**:
```
┌─────────────────────────────────────────────────────────────┐
│ Upgrade Your Service                                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ Current Plan: Internet 100 Mbps ($50.00/month)              │
│                                                               │
│ Available Upgrades:                                          │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🚀 Internet 200 Mbps         $70.00/month              │ │
│ │    • 2x faster downloads                                 │ │
│ │    • Better for streaming                                │ │
│ │    • Price difference: +$20.00/month                     │ │
│ │                         [Select & Continue →]            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🚀🚀 Internet 500 Mbps        $100.00/month            │ │
│ │    • 5x faster downloads                                 │ │
│ │    • Perfect for home office                             │ │
│ │    • Price difference: +$50.00/month                     │ │
│ │                         [Select & Continue →]            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🚀🚀🚀 Internet 1 Gbps       $150.00/month             │ │
│ │    • Maximum speed                                       │ │
│ │    • No throttling                                       │ │
│ │    • Price difference: +$100.00/month                    │ │
│ │                         [Select & Continue →]            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Upgrade Mutation**:
```javascript
const UPGRADE_SERVICE = gql`
  mutation UpgradeService($input: ServiceUpgradeInput!) {
    createOrder(input: {
      accountId: $accountId
      orderType: MODIFY
      services: [{
        action: MODIFY
        subscriptionId: $subscriptionId
        newProductCode: $newProductCode
      }]
    }) {
      orderId
      status
      estimatedCompletionDate
      proratedCharges {
        description
        amount
      }
    }
  }
`;
```

### 3.3 selfcare Component Structure

```
selfcare/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ForgotPassword.jsx
│   │   ├── Dashboard/
│   │   │   ├── AccountSummary.jsx
│   │   │   ├── ActiveServices.jsx
│   │   │   ├── QuickActions.jsx
│   │   │   └── RecentActivity.jsx
│   │   ├── Billing/
│   │   │   ├── InvoiceList.jsx
│   │   │   ├── InvoiceDetail.jsx
│   │   │   ├── PaymentForm.jsx
│   │   │   └── PaymentHistory.jsx
│   │   ├── Usage/
│   │   │   ├── UsageSummary.jsx
│   │   │   ├── UsageChart.jsx
│   │   │   ├── CDRList.jsx
│   │   │   └── ExportDialog.jsx
│   │   ├── Services/
│   │   │   ├── ServiceList.jsx
│   │   │   ├── ServiceDetails.jsx
│   │   │   └── UpgradeWizard.jsx
│   │   └── Profile/
│   │       ├── PersonalInfo.jsx
│   │       ├── PaymentMethods.jsx
│   │       ├── Notifications.jsx
│   │       └── Security.jsx
│   ├── pages/
│   │   ├── DashboardPage.jsx
│   │   ├── BillingPage.jsx
│   │   ├── UsagePage.jsx
│   │   └── ProfilePage.jsx
│   ├── services/
│   │   ├── apolloClient.js
│   │   ├── authService.js
│   │   └── braintreeService.js
│   └── App.jsx
└── package.json
```

---

## 4. ui - Public Website & Discovery

### 4.1 Purpose

**Purpose**: Customer acquisition and brand presence

**Target Audience**:
- Prospective customers
- Leads researching options
- Market segment explorers

### 4.2 Key Pages

#### 4.2.1 Package Comparison

```
┌─────────────────────────────────────────────────────────────┐
│ Choose Your Perfect Plan                                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│ │  Starter    │  │ Professional│  │  Enterprise │          │
│ │   $19/mo    │  │   $49/mo    │  │   Custom    │          │
│ ├─────────────┤  ├─────────────┤  ├─────────────┤          │
│ │ • 50 Mbps   │  │ • 200 Mbps  │  │ • 1 Gbps+   │          │
│ │ • 100 GB    │  │ • Unlimited │  │ • Unlimited │          │
│ │ • Email     │  │ • Priority  │  │ • Dedicated │          │
│ │   Support   │  │   Support   │  │   Account   │          │
│ │             │  │ • Free      │  │   Manager   │          │
│ │             │  │   Install   │  │ • SLA 99.9% │          │
│ │             │  │             │  │ • Custom    │          │
│ │             │  │             │  │   Solutions │          │
│ │             │  │             │  │             │          │
│ │[Start Trial]│  │[Sign Up Now]│  │[Contact Us] │          │
│ └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2.2 Sign-Up Flow

```
Registration Funnel:
1. Package selection
2. Service address check (serviceability)
3. Personal information
4. Payment method (optional)
5. Schedule installation
6. Confirmation
```

**Package Query**:
```javascript
const SEARCH_PACKAGES = gql`
  query SearchPackages($filter: PackageFilterInput) {
    searchPackages(filter: $filter) {
      packages {
        id
        packageCode
        name
        description
        price
        billingFrequency
        features {
          name
          value
          included
        }
        popular
        availableForSelfRegistration
      }
    }
  }
`;
```

### 4.3 Lead Generation

**Features**:
- Contact forms with CRM integration
- Live chat widget
- Request callback functionality
- Email newsletter signup

---

## 5. embrix-lite - Lightweight UI Variant

### 5.1 Purpose

**Purpose**: Reduced functionality for specific use cases or lower-bandwidth scenarios

**Potential Use Cases**:
- Kiosk mode for retail locations
- Limited-feature customer portals
- Mobile-optimized lightweight version
- Emerging markets with slower connections

### 5.2 Characteristics

| Feature | Full (selfcare) | Lite |
|---------|----------------|------|
| **Bundle Size** | ~2-3 MB | ~500 KB |
| **Features** | All features | Core features only |
| **Animations** | Rich animations | Minimal |
| **Dependencies** | Full stack | Essential only |
| **Target** | Desktop/Mobile | Mobile-first |

---

## 6. API Integration Patterns

### 6.1 GraphQL Client Setup

**Apollo Client Configuration**:
```javascript
// apolloClient.js
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: process.env.REACT_APP_GRAPHQL_URL || 'http://localhost:8080/graphql',
});

const authLink = setContext((_, { headers }) => {
  // Get token from localStorage or session
  const token = localStorage.getItem('authToken');
  
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
      'X-Tenant-ID': process.env.REACT_APP_TENANT_ID || 'urbanos',
    }
  };
});

export const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
    },
  },
});
```

### 6.2 Error Handling

```javascript
// ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service (e.g., Sentry)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-page">
          <h1>Something went wrong</h1>
          <p>We're sorry for the inconvenience. Please try refreshing the page.</p>
          <button onClick={() => window.location.reload()}>
            Refresh Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// GraphQL error handling
const handleGraphQLError = (error) => {
  if (error.networkError) {
    console.error('Network error:', error.networkError);
    showNotification('Network error. Please check your connection.', 'error');
  }
  
  if (error.graphQLErrors) {
    error.graphQLErrors.forEach(({ message, extensions }) => {
      if (extensions?.code === 'UNAUTHENTICATED') {
        // Redirect to login
        window.location.href = '/login';
      } else {
        showNotification(message, 'error');
      }
    });
  }
};
```

---

## 7. Authentication & Authorization

### 7.1 OAuth2 Login Flow

```javascript
// authService.js
class AuthService {
  
  async login(username, password) {
    try {
      // Get OAuth2 token
      const tokenResponse = await fetch('/oauth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': 'Basic ' + btoa('client:secret')
        },
        body: new URLSearchParams({
          grant_type: 'password',
          username: username,
          password: password,
          scope: 'all'
        })
      });

      const tokenData = await tokenResponse.json();
      
      // Store token
      localStorage.setItem('authToken', tokenData.access_token);
      localStorage.setItem('refreshToken', tokenData.refresh_token);
      
      // Decode JWT to get user info
      const userInfo = this.decodeToken(tokenData.access_token);
      localStorage.setItem('userInfo', JSON.stringify(userInfo));
      
      return { success: true, userInfo };
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: error.message };
    }
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    
    const response = await fetch('/oauth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + btoa('client:secret')
      },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: refreshToken
      })
    });

    const tokenData = await response.json();
    localStorage.setItem('authToken', tokenData.access_token);
    
    return tokenData.access_token;
  }

  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userInfo');
    window.location.href = '/login';
  }

  decodeToken(token) {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  }

  hasPermission(permission) {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
    return userInfo.permissions?.includes(permission) || false;
  }
}

export default new AuthService();
```

### 7.2 Permission-Based Rendering

```javascript
// ProtectedComponent.jsx
import React from 'react';
import authService from '../services/authService';

const ProtectedComponent = ({ permission, children, fallback = null }) => {
  const hasPermission = authService.hasPermission(permission);
  
  if (!hasPermission) {
    return fallback || <div>You don't have permission to view this.</div>;
  }
  
  return <>{children}</>;
};

// Usage
<ProtectedComponent permission="VIEW_BILLS">
  <InvoiceList />
</ProtectedComponent>

<ProtectedComponent permission="MAKE_PAYMENT">
  <button onClick={processPayment}>Pay Now</button>
</ProtectedComponent>
```

---

## 8. Multi-Tenant Branding & Customization

### 8.1 Tenant Configuration

```javascript
// tenantConfig.js
export const getTenantConfig = async (tenantId) => {
  const response = await fetch(`/api/tenant/${tenantId}/config`);
  return response.json();
};

// Example tenant config
const tenantConfig = {
  tenantId: "TIDLT-100005",
  tenantName: "urbanos",
  branding: {
    logoUrl: "https://s3.../urbanos-logo.png",
    faviconUrl: "https://s3.../urbanos-favicon.ico",
    primaryColor: "#1976D2",
    secondaryColor: "#DC004E",
    accentColor: "#FFC107",
    fontFamily: "Roboto, sans-serif"
  },
  contact: {
    supportEmail: "support@urbanos.com",
    supportPhone: "+52 55 1234 5678",
    website: "https://www.urbanos.com"
  },
  features: {
    enableSelfRegistration: true,
    enableCreditCardPayment: true,
    enableUsageReports: true,
    enableVoiceCDR: true
  },
  localization: {
    defaultLanguage: "es-MX",
    supportedLanguages: ["es-MX", "en-US"],
    currency: "MXN",
    timezone: "America/Mexico_City"
  },
  domains: {
    selfcare: "selfcare.urbanos.com",
    api: "api.urbanos.com"
  }
};
```

### 8.2 Dynamic Theming

```javascript
// ThemeProvider.jsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { ThemeProvider as MUIThemeProvider, createTheme } from '@mui/material/styles';

const TenantThemeContext = createContext();

export const TenantThemeProvider = ({ children }) => {
  const [tenantConfig, setTenantConfig] = useState(null);

  useEffect(() => {
    // Load tenant config
    const tenantId = process.env.REACT_APP_TENANT_ID;
    getTenantConfig(tenantId).then(setTenantConfig);
  }, []);

  if (!tenantConfig) {
    return <div>Loading...</div>;
  }

  const theme = createTheme({
    palette: {
      primary: {
        main: tenantConfig.branding.primaryColor,
      },
      secondary: {
        main: tenantConfig.branding.secondaryColor,
      },
    },
    typography: {
      fontFamily: tenantConfig.branding.fontFamily,
    },
  });

  return (
    <TenantThemeContext.Provider value={tenantConfig}>
      <MUIThemeProvider theme={theme}>
        {children}
      </MUIThemeProvider>
    </TenantThemeContext.Provider>
  );
};

export const useTenantConfig = () => useContext(TenantThemeContext);
```

---

## 9. State Management & Routing

### 9.1 State Management (Context API Example)

```javascript
// AppContext.jsx
import React, { createContext, useReducer, useContext } from 'react';

const AppStateContext = createContext();
const AppDispatchContext = createContext();

const initialState = {
  user: null,
  account: null,
  notifications: [],
  loading: false
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_ACCOUNT':
      return { ...state, account: action.payload };
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [...state.notifications, action.payload]
      };
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
}

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppStateContext.Provider value={state}>
      <AppDispatchContext.Provider value={dispatch}>
        {children}
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  );
};

export const useAppState = () => useContext(AppStateContext);
export const useAppDispatch = () => useContext(AppDispatchContext);
```

### 9.2 Routing (React Router)

```javascript
// App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { TenantThemeProvider } from './context/ThemeProvider';
import PrivateRoute from './components/PrivateRoute';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import BillingPage from './pages/BillingPage';
import UsagePage from './pages/UsagePage';
import ProfilePage from './pages/ProfilePage';

function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <TenantThemeProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Protected routes */}
            <Route path="/dashboard" element={
              <PrivateRoute>
                <DashboardPage />
              </PrivateRoute>
            } />
            
            <Route path="/billing" element={
              <PrivateRoute permission="VIEW_BILLS">
                <BillingPage />
              </PrivateRoute>
            } />
            
            <Route path="/usage" element={
              <PrivateRoute permission="VIEW_USAGE">
                <UsagePage />
              </PrivateRoute>
            } />
            
            <Route path="/profile" element={
              <PrivateRoute>
                <ProfilePage />
              </PrivateRoute>
            } />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </TenantThemeProvider>
      </AppProvider>
    </BrowserRouter>
  );
}

export default App;
```

---

## 10. Build & Deployment

### 10.1 Build Configuration

**package.json** (example for selfcare):
```json
{
  "name": "embrix-selfcare",
  "version": "3.1.9",
  "private": true,
  "dependencies": {
    "react": "^16.8.6",
    "react-dom": "^16.8.6",
    "react-router-dom": "^6.0.0",
    "react-scripts": "3.0.1",
    "@apollo/client": "^3.0.0",
    "graphql": "^15.0.0",
    "@mui/material": "^5.0.0",
    "axios": "^0.21.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": "react-app"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

### 10.2 Environment Configuration

**.env.production**:
```bash
REACT_APP_GRAPHQL_URL=https://api.urbanos.embrix.com/graphql
REACT_APP_TENANT_ID=urbanos
REACT_APP_BRAINTREE_TOKENIZATION_KEY=production_xxxxx
REACT_APP_GOOGLE_ANALYTICS_ID=UA-XXXXX-Y
```

**.env.development**:
```bash
REACT_APP_GRAPHQL_URL=http://localhost:8080/graphql
REACT_APP_TENANT_ID=urbanos
REACT_APP_BRAINTREE_TOKENIZATION_KEY=sandbox_xxxxx
```

### 10.3 Build & Deploy

```bash
# Build for production
npm run build

# Output: build/ directory with optimized static files

# Deploy to S3 (example)
aws s3 sync build/ s3://selfcare-urbanos-embrix/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"
```

### 10.4 CI/CD Pipeline (Example)

```yaml
# .gitlab-ci.yml or .github/workflows/deploy.yml
name: Deploy Selfcare

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '14'
      
      - name: Install dependencies
        run: npm ci
        working-directory: ./selfcare
      
      - name: Run tests
        run: npm test
        working-directory: ./selfcare
      
      - name: Build
        run: npm run build
        working-directory: ./selfcare
        env:
          REACT_APP_GRAPHQL_URL: ${{ secrets.GRAPHQL_URL }}
          REACT_APP_TENANT_ID: urbanos
      
      - name: Deploy to S3
        uses: jakejarvis/s3-sync-action@master
        with:
          args: --delete
        env:
          AWS_S3_BUCKET: selfcare-urbanos-embrix
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          SOURCE_DIR: 'selfcare/build'
```

---

## Summary & Next Steps

### What We Covered

✅ **Four React Applications**: ui-core, selfcare, ui, embrix-lite  
✅ **Complete Feature Set**: Registration, billing, payments, usage, upgrades  
✅ **API Integration**: GraphQL with Apollo Client  
✅ **Authentication**: OAuth2/JWT implementation  
✅ **Multi-Tenancy**: Dynamic branding and configuration  
✅ **State Management**: Context API and routing  
✅ **Build & Deploy**: Production-ready deployment strategies

### For Developers

- **Start with selfcare** - Most feature-rich customer-facing app
- **Explore GraphQL Playground** - http://localhost:8080/graphiql
- **Set up local environment** - Follow Part 3 for backend setup
- **Review component structure** - Modular, reusable components
- **Understand permissions** - Role-based access control

### Next Steps

1. **Set up local development** for frontend apps
2. **Connect to backend GraphQL API**
3. **Explore existing components** in each application
4. **Implement a new feature** following established patterns
5. **Test across different tenants** to understand multi-tenancy

---

**Ready to build amazing user experiences for Embrix O2X customers! 🎨**
