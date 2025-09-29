# Shopify App Types and Distribution Models

I'll teach you about Shopify App Types and Distribution Models using the latest Shopify documentation. Let me start by accessing the current Shopify development resources to ensure we're working with the most up-to-date information.Now let me search for the latest documentation on app types and distribution models.Let me search for more specific documentation about the different app types and distribution models.# Shopify App Types and Distribution Models - Complete Guide

Based on the latest Shopify documentation (as of September 2025), I'll teach you about the different app types and distribution models in the Shopify ecosystem. This is crucial knowledge for Phase 2 of your learning path.

## 1. Current Shopify Documentation Check

**API Version:** 2025-07 (Latest stable)  
**Documentation Last Verified:** September 23, 2025

According to the current Shopify documentation, the platform has simplified its app types significantly. Many older patterns you might find in tutorials are now deprecated:
- **Private apps** were deprecated in January 2022 (replaced by custom apps)
- **Unpublished apps** were deprecated in December 2019
- The Partner Dashboard now provides streamlined distribution selection

## 2. The Laravel/Spring Boot Equivalent

In your familiar frameworks, you've dealt with deployment and distribution concepts:

**Laravel Context:**
- You deploy applications to servers (similar to embedded apps needing hosting)
- You use service providers and packages (similar to extensions)
- You have middleware that intercepts requests (similar to Shopify Functions)
- Laravel Nova creates admin panels (similar to embedded admin pages)

**Spring Boot Context:**
- You deploy JARs/WARs to application servers (embedded apps)
- You use Spring Boot Starters for functionality (app extensions)
- You have filters and interceptors (Shopify Functions equivalent)
- Spring profiles manage different deployment configurations (distribution models)

**Angular Context:**
- You build SPAs that run in browsers (embedded app pages)
- You use Angular modules and components (app extensions)
- You have guards and interceptors (authentication flows)

## 3. The Current Shopify Way - App Types Deep Dive

### **Embedded vs Standalone Apps**

**Embedded Apps** are the standard and recommended approach. They integrate seamlessly into the Shopify Admin using App Bridge, providing a native experience where your app appears as part of Shopify's interface.

Think of embedded apps like how Angular components integrate into a larger application. Your app's UI components are rendered within Shopify's admin iframe, using Shopify's navigation and maintaining consistent UX. This is similar to how you might embed Angular micro-frontends into a larger portal application.

**Key characteristics of embedded apps:**
- They use Shopify App Bridge for deep integration with the admin interface
- Authentication happens through token exchange and session tokens
- The UI feels native to Shopify, using Polaris components
- They can access Shopify's native features like resource pickers and modals
- Mobile-compatible through Shopify's mobile admin app

**Standalone Apps** run independently outside the Shopify Admin. They're less common now but still valid for specific use cases like backend services or external dashboards.

This is similar to building a separate Laravel admin panel that connects to your main application via API. The app has its own URL, authentication flow, and UI but still interacts with Shopify through APIs.

### **Public vs Custom Apps - Distribution Models**

The distribution model determines how your app reaches merchants and what approval processes are required.

**Public Apps** are distributed through the Shopify App Store to any merchant. This is like publishing a package to Packagist (Laravel) or Maven Central (Spring Boot).

Requirements for public apps include:
- Must pass Shopify's app review process
- Need to implement proper billing through Shopify's Billing API
- Must sync certain data back to Shopify
- Use token exchange for authentication if embedded
- Follow all security and UX requirements

**Custom Apps** are designed for specific merchants or organizations. Think of these like private Laravel packages or internal Spring Boot libraries used only within your company.

Custom apps have different characteristics:
- No app review required
- Can't use Shopify's Billing API (handle payments externally)
- Can be installed on single stores or Plus organizations
- Perfect for client-specific solutions
- Use the same authentication methods as public apps

There's also a third type created directly in the **Shopify Admin**, which has more limitations:
- Can't use App Bridge for embedding
- No app extensions support
- Authentication happens directly in the admin
- Best for simple, single-store integrations

### **Extension-Only Apps**

Extension-only apps are a newer pattern that's perfect for lightweight functionality. They don't have any server component or embedded pages - just extensions that add features to Shopify.

This is similar to creating Angular directives or Laravel macros that extend functionality without needing a full application structure. All the code runs on Shopify's infrastructure.

**Benefits of extension-only apps:**
- No server hosting required (Shopify hosts everything)
- Simplified deployment through Shopify CLI
- Perfect for checkout customizations, admin actions, Flow integrations
- Lower maintenance overhead
- Currently limited to custom distribution only

Compatible extensions include:
- Admin UI extensions (actions and blocks)
- Checkout UI extensions
- Shopify Functions
- Flow triggers and actions
- POS extensions
- Theme app extensions

### **Sales Channel Apps**

Sales channel apps are specialized apps that allow merchants to sell on external platforms. They're like building a bridge between Shopify and platforms like Instagram, Amazon, or your own marketplace.

Think of this as creating a Spring Boot integration that syncs data between two systems, but with specific commerce requirements. Your platform becomes a destination where Shopify products can be sold.

**Key requirements for sales channels:**
- Must be converted to a sales channel in Partner Dashboard (irreversible)
- Implement product publishing workflows
- Handle order creation back to Shopify
- Use cart permalinks or Storefront API for checkout
- Must embed in Shopify admin
- Require Polaris UI components for consistency

## 4. Complete Working Example - Building Your First App

Let me show you how to create each type of app using Shopify CLI with the latest patterns:

```bash
#!/bin/bash

# =====================================================
# SHOPIFY APP CREATION EXAMPLES
# API Version: 2025-07
# Last Verified: September 23, 2025
# =====================================================

# -----------------------------------------------------
# 1. EMBEDDED APP (STANDARD PATTERN)
# -----------------------------------------------------
# This creates a full-stack embedded app with Remix
# Similar to creating a new Laravel project with authentication scaffolding

shopify app init my-embedded-app

# During the interactive prompt, select:
# - Name your app: My Embedded App
# - Build option: Start with Remix (recommended)
# - Development store: Select or create one

# The generated structure will include:
# /app                 # Remix app (like Laravel's app/ directory)
#   /routes           # Page components and API routes
#   /components       # Reusable UI components
# /extensions         # App extensions directory
# /shopify.app.toml   # Configuration (like .env in Laravel)
# package.json        # Dependencies (like composer.json)

# -----------------------------------------------------
# 2. EXTENSION-ONLY APP (NO SERVER REQUIRED)
# -----------------------------------------------------
# Perfect for lightweight functionality
# Like creating a Laravel package without a full app

shopify app init my-extension-only-app

# During the prompt, select:
# - Build option: Start by adding your first extension
# This creates an extension-only app structure

# Generate your first extension:
cd my-extension-only-app
shopify app generate extension

# Select extension type (e.g., checkout_ui, admin_ui_extension)
# Each extension gets its own directory:
# /extensions/my-checkout-extension
#   /src
#     /index.jsx      # Extension entry point
#   /shopify.extension.toml  # Extension config

# -----------------------------------------------------
# 3. CUSTOM APP WITH LIMITED DISTRIBUTION
# -----------------------------------------------------
# For client-specific solutions
# Like a private Laravel repository

# First create the app using CLI
shopify app init my-custom-app

# Configure for custom distribution in shopify.app.toml:
cat > shopify.app.toml << 'EOF'
# This file stores configurations for your Shopify app

scopes = "read_products,write_products"
distribution = "custom"  # Key setting for custom apps

[auth]
redirect_urls = [
  "https://localhost:3000/api/auth",
  "https://localhost:3000/api/auth/callback"
]

[webhooks]
api_version = "2025-07"

[app_proxy]
subpath = "apps/my-app"
prefix = "apps"

[build]
automatically_update_urls_on_dev = true
dev_store_url = "my-test-store.myshopify.com"
EOF

# -----------------------------------------------------
# 4. CONVERTING TO A SALES CHANNEL
# -----------------------------------------------------
# This is done through the Partner Dashboard after app creation
# Similar to adding OAuth providers in Laravel

# Step 1: Create a public app first
shopify app init my-sales-channel

# Step 2: In Partner Dashboard:
# - Navigate to your app
# - Click "API Access"
# - Find "Sales channel" section
# - Click "Turn app into sales channel"
# - IMPORTANT: This is irreversible!

# Step 3: Implement required components
# Your app must now include:

# Product Publishing Handler (app/routes/products.publish.jsx):
cat > app/routes/products.publish.jsx << 'EOF'
import { json } from "@remix-run/node";
import { authenticate } from "../shopify.server";

// Handle product publishing from Shopify to your platform
export async function action({ request }) {
  const { admin, session } = await authenticate.webhook(request);
  
  const payload = await request.json();
  const { product_listing } = payload;
  
  // Sync product to your platform
  // Similar to Laravel's event listeners
  await syncProductToExternalPlatform(product_listing);
  
  return json({ success: true });
}
EOF

# -----------------------------------------------------
# 5. AUTHENTICATION SETUP FOR EACH TYPE
# -----------------------------------------------------

# EMBEDDED APP (Token Exchange - Current Best Practice)
# app/shopify.server.js configuration:
cat > app/shopify.server.js << 'EOF'
import { shopifyApp } from "@shopify/shopify-app-remix/server";

const shopify = shopifyApp({
  apiKey: process.env.SHOPIFY_API_KEY,
  apiSecretKey: process.env.SHOPIFY_API_SECRET,
  apiVersion: "2025-07",  // Latest API version
  scopes: process.env.SCOPES?.split(","),
  appUrl: process.env.SHOPIFY_APP_URL,
  authPathPrefix: "/auth",
  sessionStorage: new PrismaSessionStorage(prisma),
  distribution: AppDistribution.AppStore, // or AppDistribution.SingleMerchant for custom
  embedded: true,  // Key setting for embedded apps
  isEmbeddedApp: true,
  // Token exchange is now the default for embedded apps
  future: {
    unstable_newEmbeddedAuthStrategy: true
  }
});

export default shopify;
export const authenticate = shopify.authenticate;
EOF

# CUSTOM APP (Direct Admin Authentication)
# For apps created in Shopify Admin:
cat > simple-custom-app.js << 'EOF'
// Simple custom app without embedding
// Uses admin-generated access token

const accessToken = process.env.ADMIN_ACCESS_TOKEN; // From Shopify Admin
const shop = 'my-store.myshopify.com';

async function makeAdminAPICall() {
  const response = await fetch(
    `https://${shop}/admin/api/2025-07/graphql.json`,
    {
      method: 'POST',
      headers: {
        'X-Shopify-Access-Token': accessToken,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: `
          query {
            products(first: 10) {
              edges {
                node {
                  id
                  title
                }
              }
            }
          }
        `
      })
    }
  );
  
  return response.json();
}
EOF

# -----------------------------------------------------
# 6. DEPLOYMENT COMMANDS
# -----------------------------------------------------

# Development mode (all app types)
shopify app dev

# Deploy app version (includes all extensions)
shopify app deploy

# For extension-only apps, deploy directly:
shopify app deploy --reset  # Creates fresh deployment

# Generate extension for any app type:
shopify app generate extension --type=checkout_ui

# -----------------------------------------------------
# 7. DISTRIBUTION CONFIGURATION
# -----------------------------------------------------

# After deployment, configure distribution in Partner Dashboard:

# PUBLIC DISTRIBUTION:
# 1. Go to Apps > Your App > Distribution
# 2. Select "Public distribution"
# 3. Complete app listing
# 4. Submit for review

# CUSTOM DISTRIBUTION:
# 1. Go to Apps > Your App > Distribution  
# 2. Select "Custom distribution"
# 3. Enter target store domain
# 4. Generate install link
# 5. Share link with client

echo "✅ App creation patterns demonstrated for all types!"
echo "📚 Remember: Extension-only apps can only use custom distribution"
echo "⚠️  Converting to sales channel is permanent!"

```

## 5. Recent Changes to Be Aware Of

The Shopify app ecosystem has undergone significant changes recently that differ from many online tutorials:

**Deprecated Patterns (Avoid These):**
- OAuth 2.0 flow is now legacy for embedded apps - token exchange is the standard
- EASDK (Embedded App SDK) is completely deprecated - use App Bridge
- Private apps no longer exist - migrated to custom apps in January 2023
- Session storage in cookies/localStorage won't work - use server-side session management
- Direct theme code injection is discouraged - use theme app extensions

**New Recommended Patterns (Use These):**
- Token exchange for embedded app authentication (automatic with latest Shopify CLI)
- Shopify managed installation for smoother merchant experience
- App Bridge version 4+ for all embedded functionality
- Extension-only apps for lightweight features
- Shopify Functions instead of Script Editor (deprecated for Plus stores)

## 6. Production Considerations for 2025

### Decision Framework: Choosing the Right App Type

Let me provide you with a comprehensive decision tree that considers your specific use case. This is similar to choosing between a monolithic Laravel app versus microservices in Spring Boot.

# Shopify App Type Decision Framework

## Step 1: Determine Distribution Requirements

**Question: Who will use your app?**

### → Many merchants (Public Distribution)
- **Requirements:**
  - App review process (4-6 weeks typically)
  - Billing API implementation mandatory
  - Strict UX/security requirements
  - App Store listing creation
  - Ongoing support obligations

**Choose if:**
- Building a SaaS product
- Want marketplace visibility
- Need recurring revenue model
- Targeting broad merchant base

### → Specific client(s) (Custom Distribution)
- **Benefits:**
  - No review process
  - Faster deployment
  - More flexibility in implementation
  - Direct client relationships

**Choose if:**
- Agency building for clients
- Enterprise solutions
- Internal tools for Plus organizations
- Proof of concept/MVP

### → Single store only (Admin-created Custom App)
- **Limitations:**
  - No embedding capabilities
  - No app extensions
  - Basic functionality only

**Choose if:**
- Simple automation needs
- Quick data sync requirements
- Store owner managing own tools

## Step 2: Determine Architecture Requirements

**Question: What functionality do you need?**

### → Full Application Features
**Build an Embedded App when you need:**
- Complex user interfaces
- Multi-page workflows
- Data storage and management
- Custom business logic
- Integration with external services
- Merchant configuration options

**Technical Stack:**
- Server infrastructure required (Heroku, Fly.io, AWS)
- Database for app data
- Backend API development
- Frontend framework (Remix recommended)

### → Lightweight Modifications Only
**Build an Extension-Only App when you need:**
- Checkout customizations
- Admin UI modifications
- Shopify Functions (discounts, shipping)
- Flow triggers/actions
- Theme extensions
- No merchant-facing UI beyond extensions

**Benefits:**
- Zero infrastructure costs
- Shopify handles all hosting
- Simplified deployment
- Lower maintenance

### → External Sales Platform
**Build a Sales Channel when you:**
- Own/operate an external marketplace
- Want to list Shopify products elsewhere
- Need order attribution
- Require product sync capabilities

**Requirements:**
- Must be embedded app
- Polaris UI mandatory
- Product publishing implementation
- Order management workflow

## Step 3: Technical Decision Matrix

| Requirement | Embedded App | Extension-Only | Sales Channel | Custom (Admin) |
|------------|--------------|----------------|---------------|----------------|
| **Hosting** | Self-hosted | Shopify-hosted | Self-hosted | N/A |
| **UI in Admin** | ✅ Full pages | ❌ No pages | ✅ Required | ❌ No |
| **Checkout Mods** | Via extensions | ✅ Direct | Via extensions | ❌ No |
| **Functions** | Via extensions | ✅ Direct | Via extensions | ❌ No |
| **Billing API** | ✅ Yes | ❌ No (custom only) | ✅ Yes | ❌ No |
| **Review Required** | If public | No (custom only) | Yes | No |
| **Database** | ✅ Yes | ❌ No | ✅ Yes | External only |
| **Merchant Config** | ✅ Complex | ⚠️ Limited | ✅ Complex | ❌ None |
| **API Limits** | Standard | Standard | Higher | Standard |
| **Development Speed** | Moderate | Fast | Slow | Very Fast |
| **Maintenance** | High | Low | High | Low |

## Step 4: Use Case Examples

### Scenario A: "Inventory Management System"
**Requirements:** Complex UI, external warehouse sync, reporting
**Recommendation:** **Embedded App with Custom Distribution**
- Why: Needs database, complex UI, but for specific clients

### Scenario B: "Custom Discount Calculator"
**Requirements:** Modify checkout pricing, no UI needed
**Recommendation:** **Extension-Only App**
- Why: Shopify Functions handle this perfectly, no server needed

### Scenario C: "Instagram Shopping Integration"
**Requirements:** Sync products to Instagram, manage listings
**Recommendation:** **Sales Channel App**
- Why: External platform integration, needs attribution

### Scenario D: "Quick Data Export Tool"
**Requirements:** Export orders to CSV, single store
**Recommendation:** **Custom App (Admin-created)**
- Why: Simple requirement, single store, no UI needed

### Scenario E: "Multi-Store Shipping Manager"
**Requirements:** Manage shipping across Plus organization
**Recommendation:** **Embedded App with Custom Distribution**
- Why: Complex features but limited to Plus org

## Step 5: Migration Paths

### Starting Simple → Scaling Up

1. **Prototype Phase:** Extension-only app (custom)
2. **Client Testing:** Add embedded pages if needed
3. **Market Validation:** Keep as custom distribution
4. **Scale:** Convert to public distribution

### Extension-Only → Full App

```bash
# Original extension-only structure
/extensions
  /checkout-ui
  /admin-action

# Convert by adding app server
shopify app generate remix
# Move existing extensions to new app
# Update shopify.app.toml with application_url
```

### Custom → Public Distribution

**Cannot change after selection!** Must:
1. Create new app in Partner Dashboard
2. Copy codebase
3. Add billing implementation
4. Submit for review
5. Migrate merchants manually

## Step 6: Cost-Benefit Analysis

### Extension-Only Apps
**Costs:**
- Limited to custom distribution
- No complex business logic
- No merchant configuration UI

**Benefits:**
- $0 hosting costs
- Minimal maintenance
- Fast deployment
- No server monitoring

### Embedded Apps
**Costs:**
- Hosting fees ($20-500/month)
- Development time (2-6 months)
- Maintenance overhead
- Security responsibilities

**Benefits:**
- Full control
- Complex features
- Public distribution possible
- Revenue potential

### Sales Channels
**Costs:**
- Irreversible conversion
- Strict requirements
- Complex implementation
- Extended review process

**Benefits:**
- Direct order attribution
- Platform integration
- High merchant value
- Premium positioning

## Decision Flowchart

```
Start
  ↓
Need merchant UI? 
  → No → Need extensions? 
           → Yes → Extension-Only App
           → No → Custom Admin App
  → Yes ↓
       Multiple merchants?
         → No → Custom Embedded App
         → Yes ↓
              External platform?
                → Yes → Sales Channel App
                → No → Public Embedded App
```

## Final Recommendations

1. **Start with Extension-Only** if possible - lowest complexity
2. **Use Custom Distribution** for client work - faster to market
3. **Only go Public** when you have product-market fit
4. **Avoid Sales Channel** unless it's core to your business model
5. **Never use Admin-created apps** for anything beyond basic automation

Remember: You cannot change distribution method after selection, so choose carefully based on long-term goals rather than immediate needs.


## 7. Real-World Scenarios Based on Current Capabilities

Let me walk you through three practical scenarios that demonstrate how these app types work in production environments, including edge cases and current best practices.

### Scenario 1: Multi-Channel Inventory Sync Application

Imagine you're building an app that synchronizes inventory between Shopify and an external ERP system, similar to how you might build a Spring Boot integration service. The app needs to handle real-time updates, bulk operations, and provide merchants with a configuration dashboard.

For this scenario, you would build an **Embedded App with Custom Distribution** initially, because you're likely working with specific enterprise clients. The app architecture would include webhook handlers for inventory updates, similar to your Laravel event listeners. Your app would subscribe to `inventory_levels/update` webhooks and use the GraphQL Admin API to push changes back to Shopify. The embedded interface would use Polaris components to maintain consistency with Shopify's admin, much like how you use Angular Material for consistent UI in Angular applications.

Edge cases to consider include rate limiting when syncing large catalogs, handling webhook delivery failures with retry logic similar to Laravel's queue system, and managing conflicting updates between systems using optimistic locking patterns you're familiar with from JPA.

### Scenario 2: Checkout Warranty Upsell Extension

Consider building a feature that adds warranty options during checkout, similar to adding middleware in Laravel that intercepts requests. This is perfect for an **Extension-Only App** because it requires no merchant configuration UI and runs entirely on Shopify's infrastructure.

You would create a checkout UI extension that renders warranty options based on cart contents, and a Shopify Function that calculates warranty prices dynamically. The extension would use React (similar to your Angular component experience) to create an interactive warranty selector. The function would be written in JavaScript and deployed to Shopify's Functions runtime, which is similar to deploying Lambda functions but with Shopify-specific constraints.

The key challenge here is working within the sandbox environment. Unlike your typical Spring Boot application where you have full server access, Shopify Functions run in a restricted environment with no network access and limited computation time. You must pre-calculate all possible warranty prices or use simple formulas that can execute quickly.

### Scenario 3: Facebook Marketplace Integration

If you're building a sales channel that lists products on Facebook Marketplace, you're creating a bridge between two platforms, similar to building an API gateway in Spring Boot. This requires a **Sales Channel App** with full embedded capabilities.

The implementation would include a product publishing pipeline that transforms Shopify product data to Facebook's format, similar to DTOs in Spring Boot. You'd implement webhook handlers for product updates to keep listings synchronized, use Shopify's resource feedback API to report listing errors back to merchants, and create cart permalinks to direct Facebook customers to Shopify's checkout.

The critical consideration here is that converting to a sales channel is irreversible. Once converted, your app gains special capabilities like appearing in the sales channel section of the admin and getting higher API rate limits, but you can never revert this change. It's like choosing between SQL and NoSQL databases early in a project; the decision has long-lasting architectural implications.

## 8. Hands-On Exercise: Build Your First Extension-Only App

Let's create a practical extension-only app that adds a custom action to the order details page. This exercise will help you understand the simplicity of extension-only apps compared to full embedded applications, similar to the difference between creating a simple Laravel artisan command versus building a full web application.

```
/**
 * HANDS-ON EXERCISE: Order Risk Assessment Extension-Only App
 * 
 * Objective: Create an admin action extension that analyzes order risk
 * Similar to: Creating a Laravel command or Angular service
 * 
 * This extension will:
 * 1. Add an action to the order details page
 * 2. Analyze order data for risk factors
 * 3. Display results in a modal
 * 
 * No server required - runs entirely on Shopify!
 */

// ============================================
// STEP 1: Initialize the Extension-Only App
// ============================================

// In your terminal, run:
// shopify app init order-risk-analyzer
// Select: "Start by adding your first extension"

// ============================================
// STEP 2: Generate Admin Action Extension
// ============================================

// shopify app generate extension
// Select: admin_action
// Name: order-risk-action

// ============================================
// STEP 3: Extension Configuration
// File: extensions/order-risk-action/shopify.extension.toml
// ============================================

const extensionConfig = `
name = "order-risk-action"
type = "admin_action"
api_version = "2025-07"

[[targeting]]
module = "admin.order-details.action.render"
target = "admin.order-details.action.render"

[input.variables]
# Define what data the extension receives
[input.variables.order]
query = """
  query GetOrder($id: ID!) {
    order(id: $id) {
      id
      name
      email
      customer {
        ordersCount
        createdAt
      }
      totalPrice
      shippingAddress {
        country
      }
      lineItems(first: 50) {
        nodes {
          quantity
          variant {
            price
          }
        }
      }
      risks {
        level
        message
      }
    }
  }
"""
`;

// ============================================
// STEP 4: Main Extension Logic
// File: extensions/order-risk-action/src/index.tsx
// ============================================

import React, { useState, useEffect } from 'react';
import {
  AdminAction,
  BlockStack,
  Text,
  Badge,
  Button,
  Modal,
  DataTable,
  Banner,
  Card,
  InlineStack,
} from '@shopify/ui-extensions-react/admin';

/**
 * Main Extension Component
 * Similar to an Angular component with dependency injection
 * Shopify automatically injects the order data based on our query
 */
export default function OrderRiskAction() {
  return (
    <AdminAction
      title="Analyze Order Risk"
      primaryAction={
        <Button
          onPress={async (remoteApi, { data }) => {
            // This is like accessing injected services in Angular
            const { order } = data;
            const riskScore = calculateRiskScore(order);
            
            // Open a modal with the analysis
            // Similar to Angular Material Dialog
            const modal = remoteApi.createModal('risk-analysis-modal');
            modal.open();
          }}
        >
          Run Risk Analysis
        </Button>
      }
    />
  );
}

// ============================================
// STEP 5: Risk Calculation Logic
// Business logic similar to a Spring Boot service
// ============================================

interface Order {
  id: string;
  name: string;
  email: string;
  customer?: {
    ordersCount: number;
    createdAt: string;
  };
  totalPrice: string;
  shippingAddress?: {
    country: string;
  };
  lineItems: {
    nodes: Array<{
      quantity: number;
      variant: {
        price: string;
      };
    }>;
  };
  risks: Array<{
    level: string;
    message: string;
  }>;
}

interface RiskFactor {
  factor: string;
  score: number;
  severity: 'low' | 'medium' | 'high';
  explanation: string;
}

function calculateRiskScore(order: Order): {
  totalScore: number;
  factors: RiskFactor[];
  recommendation: string;
} {
  const factors: RiskFactor[] = [];
  let totalScore = 0;

  // Risk Factor 1: New Customer
  // Similar to validation rules in Laravel
  if (!order.customer || order.customer.ordersCount === 1) {
    const score = 20;
    factors.push({
      factor: 'New Customer',
      score,
      severity: 'medium',
      explanation: 'First-time customers have higher risk profiles',
    });
    totalScore += score;
  }

  // Risk Factor 2: High Order Value
  const orderValue = parseFloat(order.totalPrice);
  if (orderValue > 500) {
    const score = orderValue > 1000 ? 30 : 15;
    factors.push({
      factor: 'High Order Value',
      score,
      severity: orderValue > 1000 ? 'high' : 'medium',
      explanation: `Order value of $${orderValue} is above normal`,
    });
    totalScore += score;
  }

  // Risk Factor 3: Bulk Quantities
  const hasHighQuantity = order.lineItems.nodes.some(
    item => item.quantity > 10
  );
  if (hasHighQuantity) {
    factors.push({
      factor: 'Bulk Order',
      score: 15,
      severity: 'medium',
      explanation: 'Large quantities may indicate reseller activity',
    });
    totalScore += 15;
  }

  // Risk Factor 4: International Shipping
  const isInternational = order.shippingAddress?.country !== 'US';
  if (isInternational) {
    factors.push({
      factor: 'International Order',
      score: 10,
      severity: 'low',
      explanation: 'International orders require additional verification',
    });
    totalScore += 10;
  }

  // Risk Factor 5: Email Domain Analysis
  // Similar to custom validators in Angular reactive forms
  const emailDomain = order.email.split('@')[1];
  const riskyDomains = ['tempmail.com', 'guerrillamail.com'];
  if (riskyDomains.includes(emailDomain)) {
    factors.push({
      factor: 'Suspicious Email',
      score: 25,
      severity: 'high',
      explanation: 'Temporary email service detected',
    });
    totalScore += 25;
  }

  // Generate recommendation based on total score
  // Similar to a strategy pattern in Spring Boot
  let recommendation: string;
  if (totalScore >= 60) {
    recommendation = 'High Risk: Manual review recommended before fulfillment';
  } else if (totalScore >= 30) {
    recommendation = 'Medium Risk: Consider additional verification';
  } else {
    recommendation = 'Low Risk: Safe to process normally';
  }

  return {
    totalScore,
    factors,
    recommendation,
  };
}

// ============================================
// STEP 6: Risk Analysis Modal Component
// File: extensions/order-risk-action/src/RiskAnalysisModal.tsx
// ============================================

export function RiskAnalysisModal({ order, onClose }: {
  order: Order;
  onClose: () => void;
}) {
  const [analysis, setAnalysis] = useState<ReturnType<typeof calculateRiskScore>>();

  useEffect(() => {
    // Calculate risk when modal opens
    // Similar to ngOnInit in Angular
    const result = calculateRiskScore(order);
    setAnalysis(result);
  }, [order]);

  if (!analysis) {
    return <Text>Analyzing order...</Text>;
  }

  // Determine banner tone based on risk level
  const bannerTone = analysis.totalScore >= 60 ? 'critical' : 
                     analysis.totalScore >= 30 ? 'warning' : 'success';

  return (
    <Modal
      title={`Risk Analysis for ${order.name}`}
      onClose={onClose}
      primaryAction={{
        label: 'Close',
        onPress: onClose,
      }}
      secondaryActions={[
        {
          label: 'Export Report',
          onPress: () => exportReport(analysis, order),
        },
      ]}
    >
      <BlockStack spacing="loose">
        {/* Summary Banner */}
        <Banner tone={bannerTone}>
          <Text fontWeight="bold">
            Risk Score: {analysis.totalScore}/100
          </Text>
          <Text>{analysis.recommendation}</Text>
        </Banner>

        {/* Risk Factors Table */}
        <Card>
          <Text fontWeight="bold">Risk Factors Identified</Text>
          <DataTable
            columnContentTypes={['text', 'numeric', 'text', 'text']}
            headings={['Factor', 'Score', 'Severity', 'Explanation']}
            rows={analysis.factors.map(factor => [
              factor.factor,
              factor.score.toString(),
              <Badge tone={
                factor.severity === 'high' ? 'critical' :
                factor.severity === 'medium' ? 'warning' : 'info'
              }>
                {factor.severity.toUpperCase()}
              </Badge>,
              factor.explanation,
            ])}
          />
        </Card>

        {/* Order Details */}
        <Card>
          <Text fontWeight="bold">Order Information</Text>
          <BlockStack spacing="tight">
            <InlineStack>
              <Text>Customer:</Text>
              <Text>{order.email}</Text>
            </InlineStack>
            <InlineStack>
              <Text>Order Count:</Text>
              <Text>{order.customer?.ordersCount || 0}</Text>
            </InlineStack>
            <InlineStack>
              <Text>Total Value:</Text>
              <Text>${order.totalPrice}</Text>
            </InlineStack>
            <InlineStack>
              <Text>Shipping Country:</Text>
              <Text>{order.shippingAddress?.country || 'Not specified'}</Text>
            </InlineStack>
          </BlockStack>
        </Card>

        {/* Existing Shopify Risks */}
        {order.risks.length > 0 && (
          <Card>
            <Text fontWeight="bold">Shopify Risk Assessment</Text>
            {order.risks.map((risk, index) => (
              <Banner key={index} tone="warning">
                <Text>{risk.level}: {risk.message}</Text>
              </Banner>
            ))}
          </Card>
        )}
      </BlockStack>
    </Modal>
  );
}

// ============================================
// STEP 7: Helper Functions
// ============================================

function exportReport(
  analysis: ReturnType<typeof calculateRiskScore>,
  order: Order
): void {
  // Create CSV export
  // Similar to response downloads in Laravel
  const csv = [
    ['Order Risk Analysis Report'],
    [`Order: ${order.name}`],
    [`Date: ${new Date().toISOString()}`],
    [''],
    ['Factor', 'Score', 'Severity', 'Explanation'],
    ...analysis.factors.map(f => [
      f.factor,
      f.score.toString(),
      f.severity,
      f.explanation,
    ]),
    [''],
    ['Total Score', analysis.totalScore.toString()],
    ['Recommendation', analysis.recommendation],
  ];

  // In a real app, you'd trigger a download
  console.log('Export data:', csv);
}

// ============================================
// STEP 8: Testing Instructions
// ============================================

/**
 * TO TEST YOUR EXTENSION:
 * 
 * 1. Run the development server:
 *    shopify app dev
 * 
 * 2. Install on your test store when prompted
 * 
 * 3. Navigate to any order in Shopify Admin
 * 
 * 4. Look for "Analyze Order Risk" in the actions menu
 * 
 * 5. Click to see the risk analysis modal
 * 
 * EXERCISE CHALLENGES:
 * 
 * A. Add a new risk factor for orders with mismatched billing/shipping
 * B. Implement a caching mechanism to avoid recalculating
 * C. Add a configuration modal to adjust risk thresholds
 * D. Create a bulk action version for multiple orders
 * 
 * HINTS FOR CHALLENGES:
 * 
 * A. Compare order.billingAddress with order.shippingAddress
 *    (You'll need to add these to the GraphQL query)
 * 
 * B. Use React's useMemo hook, similar to Angular's OnPush
 *    change detection strategy
 * 
 * C. Use the Admin UI extension's settings API to store
 *    merchant preferences
 * 
 * D. Change targeting to "admin.order-index.action.render"
 *    and handle multiple order IDs
 */

// ============================================
// ACCEPTANCE CRITERIA
// ============================================

/**
 * ✅ Extension appears on order detail pages
 * ✅ Risk score calculates correctly
 * ✅ Modal displays comprehensive analysis
 * ✅ Different banner tones for risk levels
 * ✅ All risk factors explained clearly
 * ✅ No server infrastructure required
 * ✅ Instant deployment via Shopify CLI
 * 
 * This demonstrates the power of extension-only apps:
 * - Zero hosting costs
 * - Runs on Shopify's infrastructure
 * - Direct integration with admin UI
 * - No authentication complexity
 * - Perfect for utility features
 */
 ```

## 9. Migration Path and Current Best Practices

Understanding migration paths between app types is crucial since some decisions, like converting to a sales channel, cannot be reversed. This is similar to database migration planning in Laravel where you need to carefully consider the long-term implications of schema changes.

When you start with an extension-only app and realize you need more complex features, the migration path involves adding a server component. You'll keep all your existing extensions and add an application URL to your configuration. This transforms your app from Shopify-hosted to a hybrid model where extensions remain on Shopify's infrastructure while your new embedded pages run on your own servers. The process is straightforward because Shopify CLI generates the necessary boilerplate code, much like how Laravel's artisan commands scaffold new features.

Common mistakes developers make include using outdated authentication patterns from older tutorials. Many online resources still show OAuth 2.0 flows, but Shopify has moved to token exchange for embedded apps as of 2024. Another frequent error is attempting to store session data in cookies or localStorage, which won't work in Safari and other privacy-focused browsers. The correct approach uses server-side session storage with libraries like Prisma or Redis, similar to how you handle sessions in Spring Boot applications.

Performance implications vary significantly between app types. Extension-only apps have near-zero latency since they run on Shopify's edge network, similar to CDN-hosted static assets. Embedded apps require careful optimization of your server infrastructure, database queries, and API calls to maintain acceptable response times. You'll need to implement caching strategies similar to Laravel's cache facades or Spring Boot's @Cacheable annotation.

A critical troubleshooting insight is that many issues stem from incorrect scope permissions. Unlike traditional web applications where you might have full database access, Shopify apps must explicitly request permission for each type of data they access. If your app suddenly stops working after a Shopify update, first check if new scopes are required for your API calls, similar to how Angular route guards might block access when permissions change.

## 10. Verification and Resources

Throughout this lesson, I've used the Shopify Dev MCP tools to verify all information against the current documentation. The search_docs_chunks tool confirmed that extension-only apps are limited to custom distribution, and the fetch_full_docs tool provided complete details about the current authentication patterns and distribution requirements.

The documentation was last updated in September 2025, with the most significant recent change being the full adoption of token exchange for embedded apps. The GraphQL Admin API continues to evolve, with version 2025-07 being the current stable release that includes improved performance for bulk operations and new fields for order risk assessment.

Related concepts you should explore next include Shopify Functions for backend customization, which work seamlessly with extension-only apps, and the new Web Pixel API for analytics, which replaces the deprecated ScriptTag API. Both of these build on the foundation of app types and distribution models you've learned today.

## Key Takeaways and Next Steps

The Shopify app ecosystem has been significantly simplified compared to what you might find in older tutorials. The modern approach favors extension-only apps for lightweight features, embedded apps with token exchange for complex applications, and clear distribution models that separate public App Store apps from custom client solutions.

Your background in Laravel and Spring Boot gives you an excellent foundation for understanding these concepts. The middleware patterns you know translate directly to Shopify Functions, your experience with dependency injection helps you understand how Shopify injects data into extensions, and your familiarity with Angular's component architecture maps perfectly to building UI extensions with React.

As you move forward in your Shopify development journey, remember that the platform strongly favors convention over configuration, much like Rails or Laravel. When you follow Shopify's recommended patterns, like using Polaris components and implementing proper authentication flows, your apps will integrate seamlessly with the platform and provide merchants with a consistent, professional experience.

The next phase of your learning should focus on Phase 3: Development Environment Setup, where you'll put this theoretical knowledge into practice. Start with an extension-only app to get comfortable with the deployment process, then gradually add complexity as you build confidence with the platform. The hands-on exercise I provided gives you a concrete starting point that you can expand upon as you explore more advanced features.

Remember that unlike traditional web development where you have full control, Shopify development involves working within a constrained environment that prioritizes merchant safety and platform stability. These constraints, similar to Angular's strict typing or Spring Boot's opinionated defaults, ultimately lead to more maintainable and reliable applications. Embrace these patterns rather than fighting against them, and you'll find Shopify development both productive and rewarding.
