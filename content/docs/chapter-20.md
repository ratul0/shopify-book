# Monetization Strategies

### The Laravel/Spring Boot Equivalent

In your Laravel and Spring Boot applications, you're familiar with several comparable concepts that will help you understand Shopify's monetization approach. In Laravel, you might use packages like Laravel Cashier for subscription billing with Stripe, implementing middleware for subscription checks, and using policies for authorization. Spring Boot applications often integrate with payment gateways through REST APIs, implement OAuth2 for security, and use Spring Security for compliance requirements. 

Shopify takes these familiar patterns and wraps them in a merchant-centric ecosystem where billing is deeply integrated into the platform itself, making it both more restrictive and more streamlined than typical SaaS implementations.

### Part 1: Monetization Strategies

#### Billing API Implementation

The Shopify Billing API is fundamentally different from integrating Stripe or PayPal in your Laravel apps. Instead of you handling payment processing, Shopify manages all financial transactions and pays you monthly. Think of it as a reverse dependency injection pattern - Shopify injects itself as the payment processor and you just define the billing model.

Here's a complete implementation of subscription billing in a Remix-based Shopify app:

```typescript
// app/models/billing.server.ts
// API Version: 2024-10 (latest stable as of general knowledge)
// File purpose: Centralized billing logic for the app

import { shopify } from "../shopify.server";
import type { AdminApiContext } from "@shopify/shopify-app-remix/server";

// TypeScript interfaces for billing (similar to your Angular interfaces)
interface BillingPlan {
  name: string;
  amount: number;
  currencyCode: string;
  interval: 'EVERY_30_DAYS' | 'ANNUAL';
  trialDays?: number;
  test?: boolean;
}

interface UsageCharge {
  description: string;
  amount: number;
  currencyCode: string;
}

// Main billing configuration (like Laravel config files)
export const BILLING_PLANS = {
  basic: {
    name: "Basic Plan",
    amount: 9.99,
    currencyCode: "USD",
    interval: "EVERY_30_DAYS" as const,
    trialDays: 7,
    test: process.env.NODE_ENV === "development"
  },
  professional: {
    name: "Professional Plan", 
    amount: 29.99,
    currencyCode: "USD",
    interval: "EVERY_30_DAYS" as const,
    trialDays: 14,
    test: process.env.NODE_ENV === "development"
  },
  enterprise: {
    name: "Enterprise Plan",
    amount: 299.99,
    currencyCode: "USD",
    interval: "ANNUAL" as const,
    trialDays: 30,
    test: process.env.NODE_ENV === "development"
  }
} as const;

// Create subscription (similar to Laravel Cashier's newSubscription)
export async function createSubscription(
  admin: AdminApiContext,
  plan: BillingPlan,
  returnUrl: string
): Promise<string> {
  // GraphQL mutation for creating subscription
  // In Laravel, this would be like Cashier's subscription()->create()
  const response = await admin.graphql(
    `#graphql
      mutation CreateSubscription(
        $name: String!
        $returnUrl: URL!
        $test: Boolean
        $lineItems: [AppSubscriptionLineItemInput!]!
      ) {
        appSubscriptionCreate(
          name: $name
          returnUrl: $returnUrl
          test: $test
          lineItems: $lineItems
        ) {
          appSubscription {
            id
          }
          confirmationUrl
          userErrors {
            field
            message
          }
        }
      }
    `,
    {
      variables: {
        name: plan.name,
        returnUrl,
        test: plan.test || false,
        lineItems: [
          {
            plan: {
              appRecurringPricingDetails: {
                price: {
                  amount: plan.amount,
                  currencyCode: plan.currencyCode
                },
                interval: plan.interval
              }
            }
          }
        ],
        trialDays: plan.trialDays
      }
    }
  );

  const { appSubscriptionCreate } = response.json();
  
  if (appSubscriptionCreate.userErrors.length > 0) {
    throw new Error(appSubscriptionCreate.userErrors[0].message);
  }

  return appSubscriptionCreate.confirmationUrl;
}

// Check active subscription (middleware-like function)
export async function hasActiveSubscription(
  admin: AdminApiContext,
  session: Session
): Promise<boolean> {
  // This is like Laravel middleware checking if user has active subscription
  const response = await admin.graphql(
    `#graphql
      query GetActiveSubscriptions {
        currentAppInstallation {
          activeSubscriptions {
            id
            name
            status
            currentPeriodEnd
            test
          }
        }
      }
    `
  );

  const { currentAppInstallation } = response.json();
  const activeSubscriptions = currentAppInstallation.activeSubscriptions;
  
  return activeSubscriptions.some(
    (sub: any) => sub.status === "ACTIVE" && !sub.test
  );
}

// Usage-based charging implementation
export async function createUsageCharge(
  admin: AdminApiContext,
  charge: UsageCharge
): Promise<void> {
  // Find active subscription first
  const subscriptionResponse = await admin.graphql(
    `#graphql
      query GetSubscriptionId {
        currentAppInstallation {
          activeSubscriptions {
            id
            status
          }
        }
      }
    `
  );
  
  const { currentAppInstallation } = subscriptionResponse.json();
  const activeSubscription = currentAppInstallation.activeSubscriptions[0];
  
  if (!activeSubscription) {
    throw new Error("No active subscription found");
  }

  // Create usage charge
  const chargeResponse = await admin.graphql(
    `#graphql
      mutation CreateUsageCharge(
        $subscriptionLineItemId: ID!
        $price: MoneyInput!
        $description: String!
      ) {
        appUsageRecordCreate(
          subscriptionLineItemId: $subscriptionLineItemId
          price: $price
          description: $description
        ) {
          appUsageRecord {
            id
          }
          userErrors {
            field
            message
          }
        }
      }
    `,
    {
      variables: {
        subscriptionLineItemId: activeSubscription.id,
        price: {
          amount: charge.amount,
          currencyCode: charge.currencyCode
        },
        description: charge.description
      }
    }
  );

  const { appUsageRecordCreate } = chargeResponse.json();
  
  if (appUsageRecordCreate.userErrors.length > 0) {
    throw new Error(appUsageRecordCreate.userErrors[0].message);
  }
}
```

Now let's implement the billing routes and middleware pattern:

```typescript
// app/routes/app.billing.tsx
// Route handler for billing operations (like Laravel controllers)

import { json, redirect } from "@remix-run/node";
import type { LoaderFunction, ActionFunction } from "@remix-run/node";
import { Form, useLoaderData } from "@remix-run/react";
import { authenticate } from "../shopify.server";
import { 
  BILLING_PLANS, 
  createSubscription, 
  hasActiveSubscription 
} from "../models/billing.server";
import { 
  Card, 
  Page, 
  Layout, 
  Button, 
  BlockStack,
  Text,
  Banner
} from "@shopify/polaris";

// Loader function (like Laravel's controller index method)
export const loader: LoaderFunction = async ({ request }) => {
  const { admin, session, redirect } = await authenticate.admin(request);
  
  const hasSubscription = await hasActiveSubscription(admin, session);
  const currentPlan = hasSubscription ? await getCurrentPlan(admin) : null;
  
  return json({
    plans: BILLING_PLANS,
    currentPlan,
    hasSubscription
  });
};

// Action handler (like Laravel's store/update methods)
export const action: ActionFunction = async ({ request }) => {
  const { admin, session } = await authenticate.admin(request);
  const formData = await request.formData();
  const planKey = formData.get("plan") as keyof typeof BILLING_PLANS;
  
  if (!planKey || !BILLING_PLANS[planKey]) {
    return json({ error: "Invalid plan selected" }, { status: 400 });
  }
  
  const plan = BILLING_PLANS[planKey];
  const returnUrl = `${process.env.SHOPIFY_APP_URL}/app/billing/callback`;
  
  try {
    const confirmationUrl = await createSubscription(admin, plan, returnUrl);
    return redirect(confirmationUrl);
  } catch (error) {
    return json({ error: error.message }, { status: 500 });
  }
};

// React component for billing page
export default function Billing() {
  const { plans, currentPlan, hasSubscription } = useLoaderData();
  
  return (
    <Page title="Billing & Subscription">
      <Layout>
        {hasSubscription && currentPlan && (
          <Layout.Section>
            <Banner status="info">
              <p>You're currently on the {currentPlan.name} plan.</p>
            </Banner>
          </Layout.Section>
        )}
        
        <Layout.Section>
          <BlockStack gap="500">
            {Object.entries(plans).map(([key, plan]) => (
              <Card key={key}>
                <BlockStack gap="200">
                  <Text as="h2" variant="headingMd">
                    {plan.name}
                  </Text>
                  <Text variant="bodyMd">
                    ${plan.amount} {plan.currencyCode} / {plan.interval}
                  </Text>
                  {plan.trialDays && (
                    <Text variant="bodyMd" tone="positive">
                      {plan.trialDays} day free trial
                    </Text>
                  )}
                  <Form method="post">
                    <input type="hidden" name="plan" value={key} />
                    <Button submit primary>
                      Select Plan
                    </Button>
                  </Form>
                </BlockStack>
              </Card>
            ))}
          </BlockStack>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
```

### Part 2: Legal and Compliance

Compliance in Shopify apps is more stringent than typical web applications because you're handling merchant data across international boundaries. Here's a complete implementation of GDPR compliance and mandatory webhooks:

```typescript
// app/webhooks/compliance.server.ts
// Handles all compliance-related webhooks (mandatory for app approval)

import type { WebhookHandler } from "@shopify/shopify-app-remix/server";
import { db } from "../db.server"; // Your Prisma/database instance

// GDPR customer data request webhook
// This is like implementing GDPR export in Laravel, but webhook-driven
export const customersDataRequest: WebhookHandler = async ({
  shop,
  body,
  webhookId
}) => {
  const payload = JSON.parse(body);
  
  // Log the request (required for compliance)
  await db.gdprRequest.create({
    data: {
      shop,
      customerId: payload.customer.id,
      email: payload.customer.email,
      requestType: "DATA_REQUEST",
      webhookId,
      requestedAt: new Date(payload.orders_requested_at)
    }
  });
  
  // Collect all customer data from your database
  // This is similar to Laravel's personal data export
  const customerData = await db.customerData.findMany({
    where: {
      shop,
      customerId: payload.customer.id
    },
    select: {
      id: true,
      createdAt: true,
      // Include all fields you store about the customer
      preferences: true,
      analyticsData: true,
      customFields: true
    }
  });
  
  // You have 10 days to provide this data to Shopify
  // Send data to Shopify's endpoint (not shown here for brevity)
  // In production, you'd queue this job like Laravel Queue
  await sendCustomerDataToShopify(shop, payload.customer.id, customerData);
  
  return new Response("OK", { status: 200 });
};

// GDPR customer redact webhook
// This is permanent deletion - like Laravel's soft deletes but irreversible
export const customersRedact: WebhookHandler = async ({
  shop,
  body,
  webhookId
}) => {
  const payload = JSON.parse(body);
  
  // Log the redaction request
  await db.gdprRequest.create({
    data: {
      shop,
      customerId: payload.customer.id,
      email: payload.customer.email,
      requestType: "REDACT",
      webhookId,
      requestedAt: new Date()
    }
  });
  
  // Permanently delete all customer data
  // This is like Laravel's forceDelete() but for all related data
  await db.$transaction([
    db.customerData.deleteMany({
      where: {
        shop,
        customerId: payload.customer.id
      }
    }),
    db.customerAnalytics.deleteMany({
      where: {
        shop,
        customerId: payload.customer.id
      }
    }),
    db.customerPreferences.deleteMany({
      where: {
        shop,
        customerId: payload.customer.id
      }
    })
  ]);
  
  // You cannot restore this data after deletion
  return new Response("OK", { status: 200 });
};

// Shop redact webhook - when merchant uninstalls your app
export const shopRedact: WebhookHandler = async ({
  shop,
  webhookId
}) => {
  // This is like cascade delete in Laravel but for entire shop
  // Must delete ALL shop data within 30 days
  
  await db.gdprRequest.create({
    data: {
      shop,
      requestType: "SHOP_REDACT",
      webhookId,
      requestedAt: new Date()
    }
  });
  
  // Queue for deletion (gives time for any disputes)
  // In Laravel terms, this is like scheduling a job
  await scheduleShopDataDeletion(shop, 30); // Delete after 30 days
  
  return new Response("OK", { status: 200 });
};

// Security headers middleware (like Laravel middleware)
export function securityHeaders() {
  return {
    "Content-Security-Policy": [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.shopify.com",
      "style-src 'self' 'unsafe-inline' https://cdn.shopify.com",
      "img-src 'self' data: https://cdn.shopify.com https://*.myshopify.com",
      "connect-src 'self' https://*.myshopify.com"
    ].join("; "),
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
  };
}
```

Now let's implement data privacy configuration:

```typescript
// app/privacy/privacy-policy.server.ts
// Manages privacy policy requirements for app submission

export const PRIVACY_POLICY = {
  // Required data usage declarations for app review
  dataUse: {
    customerData: {
      collected: ["email", "name", "phone"],
      purpose: ["app_functionality", "analytics"],
      retention: "until_merchant_uninstall",
      sharing: "none" // or specify third parties
    },
    shopData: {
      collected: ["products", "orders", "inventory"],
      purpose: ["app_functionality"],
      retention: "until_merchant_uninstall",
      sharing: "none"
    }
  },
  
  // Required URLs for app listing
  urls: {
    privacyPolicy: "https://yourapp.com/privacy",
    termsOfService: "https://yourapp.com/terms",
    dataProcessingAgreement: "https://yourapp.com/dpa"
  },
  
  // Security practices (OWASP compliance)
  security: {
    encryption: {
      atRest: "AES-256",
      inTransit: "TLS 1.3",
      keyManagement: "AWS KMS" // or your provider
    },
    authentication: {
      sessionManagement: "JWT with rotation",
      mfa: "available for team accounts",
      passwordPolicy: "minimum 12 characters"
    },
    monitoring: {
      logging: "CloudWatch/Datadog",
      alerting: "PagerDuty",
      incidentResponse: "24 hours SLA"
    }
  }
};

// App configuration for compliance
export const APP_COMPLIANCE_CONFIG = {
  // Mandatory webhook endpoints
  webhooks: {
    "CUSTOMERS_DATA_REQUEST": "/webhooks/customers/data-request",
    "CUSTOMERS_REDACT": "/webhooks/customers/redact", 
    "SHOP_REDACT": "/webhooks/shop/redact"
  },
  
  // Required scopes with justification (for app review)
  scopes: {
    "read_products": "Display product recommendations",
    "write_products": "Update product metadata",
    "read_orders": "Analyze order patterns",
    "read_customers": "Personalize experience"
  },
  
  // Rate limiting (prevents abuse)
  rateLimits: {
    api: "2 requests per second",
    webhooks: "10000 per day",
    bulk: "1 operation per minute"
  }
};
```

### Part 3: Support and Maintenance

Here's a complete implementation of support infrastructure and app analytics:

```typescript
// app/support/analytics.server.ts
// Analytics tracking for app usage (like Laravel Telescope but for Shopify apps)

import { db } from "../db.server";
import type { Session } from "@shopify/shopify-api";

interface AppEvent {
  shop: string;
  eventType: string;
  metadata?: Record<string, any>;
  userId?: string;
}

export class AppAnalytics {
  // Track feature usage (similar to Laravel events)
  static async trackEvent(event: AppEvent): Promise<void> {
    await db.analyticsEvent.create({
      data: {
        shop: event.shop,
        eventType: event.eventType,
        metadata: event.metadata || {},
        userId: event.userId,
        timestamp: new Date()
      }
    });
    
    // Send to external analytics if configured
    if (process.env.MIXPANEL_TOKEN) {
      await this.sendToMixpanel(event);
    }
  }
  
  // Track app performance metrics
  static async trackPerformance(
    shop: string,
    operation: string,
    duration: number
  ): Promise<void> {
    await db.performanceMetric.create({
      data: {
        shop,
        operation,
        duration,
        timestamp: new Date()
      }
    });
    
    // Alert if operation is slow
    if (duration > 3000) {
      await this.alertSlowOperation(shop, operation, duration);
    }
  }
  
  // Generate usage reports for merchants
  static async generateUsageReport(shop: string, startDate: Date, endDate: Date) {
    const events = await db.analyticsEvent.groupBy({
      by: ['eventType'],
      where: {
        shop,
        timestamp: {
          gte: startDate,
          lte: endDate
        }
      },
      _count: {
        eventType: true
      }
    });
    
    const performance = await db.performanceMetric.aggregate({
      where: {
        shop,
        timestamp: {
          gte: startDate,
          lte: endDate
        }
      },
      _avg: {
        duration: true
      },
      _max: {
        duration: true
      },
      _min: {
        duration: true
      }
    });
    
    return {
      usage: events,
      performance,
      period: { startDate, endDate }
    };
  }
}

// app/support/documentation.tsx
// In-app documentation component

import { Card, Text, Link, BlockStack } from "@shopify/polaris";

export function DocumentationPanel({ section }: { section: string }) {
  const docs = {
    billing: {
      title: "Billing & Subscriptions",
      articles: [
        {
          title: "Understanding your subscription",
          url: "/docs/billing/subscription",
          description: "Learn about plan features and billing cycles"
        },
        {
          title: "Usage charges explained",
          url: "/docs/billing/usage",
          description: "How we calculate usage-based billing"
        }
      ],
      videos: [
        {
          title: "Getting started with billing",
          url: "https://youtube.com/...",
          duration: "5 min"
        }
      ]
    },
    features: {
      title: "Feature Documentation",
      articles: [
        {
          title: "Quick start guide",
          url: "/docs/quickstart",
          description: "Get up and running in 5 minutes"
        },
        {
          title: "Advanced features",
          url: "/docs/advanced",
          description: "Power user features and workflows"
        }
      ]
    }
  };
  
  const content = docs[section] || docs.features;
  
  return (
    <Card>
      <BlockStack gap="400">
        <Text as="h2" variant="headingMd">
          {content.title}
        </Text>
        
        <BlockStack gap="200">
          {content.articles.map((article) => (
            <div key={article.url}>
              <Link url={article.url} external={false}>
                {article.title}
              </Link>
              <Text variant="bodySm" tone="subdued">
                {article.description}
              </Text>
            </div>
          ))}
        </BlockStack>
        
        {content.videos && (
          <>
            <Text as="h3" variant="headingSm">
              Video Tutorials
            </Text>
            {content.videos.map((video) => (
              <Link key={video.url} url={video.url} external>
                {video.title} ({video.duration})
              </Link>
            ))}
          </>
        )}
      </BlockStack>
    </Card>
  );
}

// app/support/changelog.server.ts
// Manages app updates and notifications

interface ChangelogEntry {
  version: string;
  date: Date;
  type: 'major' | 'minor' | 'patch';
  changes: {
    category: 'feature' | 'improvement' | 'bugfix' | 'breaking';
    description: string;
  }[];
}

export class ChangelogManager {
  static async addEntry(entry: ChangelogEntry): Promise<void> {
    // Store in database
    await db.changelog.create({
      data: {
        version: entry.version,
        date: entry.date,
        type: entry.type,
        changes: entry.changes
      }
    });
    
    // Notify merchants of major changes
    if (entry.type === 'major' || 
        entry.changes.some(c => c.category === 'breaking')) {
      await this.notifyMerchants(entry);
    }
  }
  
  static async notifyMerchants(entry: ChangelogEntry): Promise<void> {
    // Get all active installations
    const shops = await db.shop.findMany({
      where: { active: true }
    });
    
    // Create in-app notifications
    for (const shop of shops) {
      await db.notification.create({
        data: {
          shopId: shop.id,
          type: 'CHANGELOG',
          title: `New version ${entry.version} available`,
          message: this.formatChangelog(entry),
          read: false
        }
      });
      
      // Also send email for breaking changes
      if (entry.changes.some(c => c.category === 'breaking')) {
        await this.sendChangelogEmail(shop.email, entry);
      }
    }
  }
  
  static formatChangelog(entry: ChangelogEntry): string {
    const sections = {
      breaking: '⚠️ Breaking Changes',
      feature: '✨ New Features',
      improvement: '🚀 Improvements',
      bugfix: '🐛 Bug Fixes'
    };
    
    let message = `Version ${entry.version}\n\n`;
    
    for (const [category, title] of Object.entries(sections)) {
      const changes = entry.changes.filter(c => c.category === category);
      if (changes.length > 0) {
        message += `${title}:\n`;
        changes.forEach(change => {
          message += `• ${change.description}\n`;
        });
        message += '\n';
      }
    }
    
    return message;
  }
}
```

### Real-World Scenarios

Here are three practical implementations combining all these concepts:

**Scenario 1: Freemium Model with Usage Tracking**

```typescript
// app/models/freemium-billing.server.ts
// Implements a freemium model with usage limits

export class FreemiumBilling {
  static readonly FREE_TIER_LIMITS = {
    ordersPerMonth: 100,
    productsSync: 1000,
    apiCallsPerDay: 1000
  };
  
  static async checkUsageLimit(
    shop: string, 
    limitType: keyof typeof this.FREE_TIER_LIMITS
  ): Promise<{ allowed: boolean; usage: number; limit: number }> {
    const subscription = await this.getActiveSubscription(shop);
    
    // Paid users have no limits
    if (subscription?.status === 'ACTIVE') {
      return { allowed: true, usage: 0, limit: Infinity };
    }
    
    // Check free tier usage
    const usage = await this.getCurrentUsage(shop, limitType);
    const limit = this.FREE_TIER_LIMITS[limitType];
    
    return {
      allowed: usage < limit,
      usage,
      limit
    };
  }
  
  static async enforceUsageLimit(
    shop: string,
    limitType: keyof typeof this.FREE_TIER_LIMITS
  ): Promise<void> {
    const { allowed, usage, limit } = await this.checkUsageLimit(shop, limitType);
    
    if (!allowed) {
      // Track the limit hit for analytics
      await AppAnalytics.trackEvent({
        shop,
        eventType: 'usage_limit_hit',
        metadata: { limitType, usage, limit }
      });
      
      // Show upgrade prompt
      throw new UpgradeRequiredError(
        `You've reached the free tier limit of ${limit} ${limitType}. ` +
        `Please upgrade to continue.`
      );
    }
    
    // Increment usage counter
    await this.incrementUsage(shop, limitType);
  }
}
```

**Scenario 2: Enterprise Compliance Package**

```typescript
// app/compliance/enterprise.server.ts
// Advanced compliance features for enterprise clients

export class EnterpriseCompliance {
  // Data residency compliance (GDPR requirement)
  static async ensureDataResidency(shop: string, region: 'EU' | 'US' | 'CA') {
    const shopData = await db.shop.findUnique({ where: { domain: shop } });
    
    // Check if data needs migration
    if (shopData.dataRegion !== region) {
      // Queue migration job (like Laravel job dispatch)
      await queue.dispatch('MigrateShopData', {
        shop,
        fromRegion: shopData.dataRegion,
        toRegion: region,
        complianceReason: 'merchant_request'
      });
    }
  }
  
  // Audit logging for enterprise accounts
  static async logAdminAction(
    shop: string,
    userId: string,
    action: string,
    resourceType: string,
    resourceId: string,
    changes?: Record<string, any>
  ) {
    await db.auditLog.create({
      data: {
        shop,
        userId,
        action,
        resourceType,
        resourceId,
        changes,
        ipAddress: await this.getCurrentIpAddress(),
        userAgent: await this.getUserAgent(),
        timestamp: new Date()
      }
    });
    
    // Check for suspicious activity
    await this.checkSuspiciousActivity(shop, userId);
  }
  
  // SOC2 compliance reporting
  static async generateComplianceReport(shop: string, type: 'SOC2' | 'ISO27001') {
    const report = {
      generatedAt: new Date(),
      shop,
      type,
      sections: {
        accessControl: await this.auditAccessControl(shop),
        dataEncryption: await this.auditEncryption(shop),
        incidentResponse: await this.auditIncidents(shop),
        changeManagement: await this.auditChanges(shop),
        backupRecovery: await this.auditBackups(shop)
      }
    };
    
    return report;
  }
}
```

### Advanced Patterns from Current Best Practices

**Pattern 1: Progressive Pricing with Feature Flags**

```typescript
// app/features/feature-flags.server.ts
// Feature flag system tied to billing tiers

export class FeatureFlags {
  static readonly FEATURES = {
    basic: ['core_features', 'email_support'],
    professional: ['advanced_analytics', 'api_access', 'priority_support'],
    enterprise: ['white_label', 'dedicated_support', 'custom_integrations']
  };
  
  static async isEnabled(shop: string, feature: string): Promise<boolean> {
    const plan = await this.getShopPlan(shop);
    const enabledFeatures = this.getFeaturesForPlan(plan);
    
    // Check if feature is enabled for plan
    if (!enabledFeatures.includes(feature)) {
      // Check for feature trial
      const trial = await db.featureTrial.findFirst({
        where: {
          shop,
          feature,
          expiresAt: { gt: new Date() }
        }
      });
      
      return !!trial;
    }
    
    return true;
  }
  
  // Enable feature trial
  static async enableTrial(shop: string, feature: string, days: number = 14) {
    await db.featureTrial.create({
      data: {
        shop,
        feature,
        startedAt: new Date(),
        expiresAt: new Date(Date.now() + days * 24 * 60 * 60 * 1000)
      }
    });
    
    // Track trial start
    await AppAnalytics.trackEvent({
      shop,
      eventType: 'feature_trial_started',
      metadata: { feature, days }
    });
  }
}
```

### Hands-On Exercise

**Build a Complete Monetization System**

Your task is to implement a billing system that combines the concepts from your Laravel/Spring Boot experience with Shopify's requirements:

**Requirements:**
1. Implement a three-tier pricing model (Free, Pro, Enterprise)
2. Add usage-based charging for API calls beyond limits
3. Include GDPR-compliant data handling
4. Create an analytics dashboard showing revenue metrics
5. Implement upgrade/downgrade flows with proration

**Acceptance Criteria:**
- Free tier: 100 API calls/day, 1 store
- Pro tier: $29/month, 10,000 API calls/day, 5 stores
- Enterprise: $299/month, unlimited API calls, unlimited stores
- Usage overage: $0.001 per API call beyond limit
- All GDPR webhooks must respond within 5 seconds
- Analytics must show MRR, churn rate, and usage patterns

**Hints:**
- Think of Shopify's billing like Laravel Cashier but webhook-driven
- Use database transactions (like Spring Boot's @Transactional) for billing operations
- Implement middleware pattern for checking subscription status
- Use your Angular experience for building the analytics dashboard with charts
- Remember: Shopify handles all payment processing, you just define the model

### Production Considerations for 2025

When deploying your monetized Shopify app, consider these critical factors that differ from standard SaaS applications. Unlike your Laravel or Spring Boot apps where you control the entire payment flow, Shopify acts as an intermediary, which introduces unique considerations.

First, implement robust webhook retry logic since Shopify requires response times under 5 seconds for all webhooks, especially GDPR compliance webhooks. Missing these can result in app suspension. Second, always test billing flows in development stores with test charges enabled before going live. Third, implement proper idempotency for all billing operations since webhooks can be delivered multiple times. Fourth, use Shopify's built-in proration handling rather than calculating it yourself to avoid billing disputes.

For compliance, maintain detailed audit logs of all data access and modifications, as Shopify may request these during app reviews or merchant disputes. Implement rate limiting on your own endpoints to prevent abuse, as excessive API usage by your app affects all your merchants' API limits. Finally, always version your database schema and maintain backward compatibility for at least 90 days, as merchants may not update immediately.

---

This comprehensive guide covers the business and monetization aspects of Shopify app development, drawing parallels to your existing knowledge while highlighting Shopify-specific implementations. The key difference from your Laravel/Spring Boot experience is that Shopify handles all payment processing, compliance verification, and merchant relationships, while you focus on defining the business model and implementing the technical integration.

Would you like me to dive deeper into any specific aspect, such as implementing specific pricing strategies, handling subscription migrations, or setting up advanced analytics tracking?
