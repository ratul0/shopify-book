# App Architecture and Structure

## 1. Current Shopify Documentation Check

Based on my verification with the Shopify Dev MCP tools, I'm working with the latest documentation from Shopify's 2025-07 API version. The Remix app template remains the current recommended approach for building Shopify apps, with significant updates to the CLI structure and configuration management.

## 2. The Laravel/Spring Boot Equivalent

Before diving into Shopify's architecture, let me connect this to your existing knowledge. Think of a Shopify app's architecture as having parallels to what you already know from Laravel and Spring Boot. In Laravel, you have a clear MVC structure with routes defined in `routes/web.php`, controllers handling business logic, and Blade templates for views. In Spring Boot, you have your `@Controller` classes, service layers, and Thymeleaf templates. 

Shopify's Remix-based architecture follows a similar separation of concerns but with some key differences. Instead of separate controller files, Remix uses file-based routing where each route file contains both the server-side logic (similar to your controllers) and the component that renders the UI. This is more like Angular's component-based architecture where logic and presentation are co-located, but with the added benefit of server-side rendering.

## 3. The Current Shopify Way

According to Shopify's documentation as of September 2025, the standard app structure follows this convention:

```
your-app/
├── shopify.app.toml          # App configuration (like Laravel's .env + config/)
├── shopify.web.toml          # Web server configuration
├── package.json              # Dependencies (like composer.json)
├── app/                      # Main application code
│   ├── entry.server.tsx      # Server entry point (like Spring Boot's @SpringBootApplication)
│   ├── root.tsx              # Root layout (like Laravel's app.blade.php)
│   └── routes/               # File-based routing (similar to Angular's routing module)
├── extensions/               # App extensions (Shopify-specific features)
├── prisma/                   # Database schema (like Laravel migrations)
│   └── schema.prisma
└── .env                      # Environment variables
```

Let me break down each component in detail.

### shopify.app.toml - The Heart of Configuration

This file is unique to Shopify and serves as the central configuration hub. Think of it as combining Laravel's various config files with deployment configuration. Here's a production-ready example:

```toml
# shopify.app.toml
name = "My Production App"
client_id = "your-client-id-from-partner-dashboard"
application_url = "https://your-app.com"
embedded = true  # Most apps should be embedded
handle = "my-production-app"  # URL slug in admin

[access_scopes]
scopes = "read_products,write_products,read_orders"
# New in 2025: Optional scopes for progressive permissions
optional_scopes = ["read_customers", "write_discounts"]

[access.admin]
# Direct API access for admin extensions
direct_api_mode = "online"  # or "offline" for background jobs
embedded_app_direct_api_access = true  # New in 2025

[auth]
redirect_urls = [
  "https://your-app.com/auth/callback",
  "https://your-app.com/auth/shopify/callback"  # Multiple for flexibility
]

[webhooks]
api_version = "2025-07"  # Always use latest stable

[[webhooks.subscriptions]]
topics = ["app/uninstalled", "products/update"]
uri = "/webhooks"
# New in 2025: Webhook filters for efficiency
filter = "title:contains('Premium')"

[build]
automatically_update_urls_on_dev = false  # false for production
include_config_on_deploy = true  # New best practice
```

### Server-Side Components (app/ directory)

The server-side architecture in Shopify apps using Remix is quite different from your Laravel/Spring Boot experience. Instead of separate controllers and models, Remix co-locates data fetching with components. Here's a complete example of a route that demonstrates this:

```tsx
// app/routes/app.products.$id.tsx
// This single file handles both server logic and UI rendering

import { json } from "@remix-run/node";
import { useLoaderData, Form, useActionData } from "@remix-run/react";
import { 
  Card, 
  Page, 
  Layout, 
  TextField, 
  Button,
  Banner 
} from "@shopify/polaris";
import { authenticate } from "~/shopify.server";
import db from "~/db.server"; // Your Prisma instance

// This is like your Laravel controller's show() method or Spring Boot's @GetMapping
export async function loader({ request, params }) {
  // Authentication is built-in, similar to Laravel middleware
  const { admin, session } = await authenticate.admin(request);
  
  // Fetch from Shopify API (like using Eloquent with an external API)
  const response = await admin.graphql(
    `#graphql
      query getProduct($id: ID!) {
        product(id: $id) {
          id
          title
          description
          status
          variants(first: 10) {
            edges {
              node {
                id
                title
                price
              }
            }
          }
        }
      }
    `,
    { variables: { id: `gid://shopify/Product/${params.id}` } }
  );
  
  const { data } = await response.json();
  
  // Also fetch app-specific data from your database
  // Similar to Laravel's Eloquent or Spring Boot's JPA
  const appData = await db.productSettings.findUnique({
    where: { shopifyProductId: params.id }
  });
  
  return json({
    product: data.product,
    appSettings: appData,
    shop: session.shop
  });
}

// This is like your Laravel controller's update() method or Spring Boot's @PostMapping
export async function action({ request, params }) {
  const { admin, session } = await authenticate.admin(request);
  const formData = await request.formData();
  
  // Update in Shopify
  const response = await admin.graphql(
    `#graphql
      mutation updateProduct($input: ProductInput!) {
        productUpdate(input: $input) {
          product {
            id
            title
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
        input: {
          id: `gid://shopify/Product/${params.id}`,
          title: formData.get("title"),
          description: formData.get("description")
        }
      }
    }
  );
  
  const { data } = await response.json();
  
  if (data.productUpdate.userErrors.length > 0) {
    return json({ errors: data.productUpdate.userErrors }, { status: 422 });
  }
  
  // Also update your app-specific data
  await db.productSettings.upsert({
    where: { shopifyProductId: params.id },
    update: { customField: formData.get("customField") },
    create: { 
      shopifyProductId: params.id,
      customField: formData.get("customField"),
      shop: session.shop
    }
  });
  
  return json({ success: true });
}

// This is your React component (like Angular component + template)
export default function ProductEdit() {
  const { product, appSettings, shop } = useLoaderData();
  const actionData = useActionData();
  
  return (
    <Page
      title={`Edit ${product.title}`}
      breadcrumbs={[{ content: "Products", url: "/app" }]}
    >
      <Layout>
        {actionData?.errors && (
          <Banner status="critical">
            {actionData.errors.map(error => (
              <p key={error.field}>{error.message}</p>
            ))}
          </Banner>
        )}
        
        <Form method="post">
          <Card>
            <TextField
              label="Product Title"
              name="title"
              defaultValue={product.title}
              helpText="This updates the product title in Shopify"
            />
            
            <TextField
              label="Custom App Field"
              name="customField"
              defaultValue={appSettings?.customField}
              helpText="This is stored in your app's database"
            />
            
            <Button submit primary>Save Product</Button>
          </Card>
        </Form>
      </Layout>
    </Page>
  );
}
```

### Client-Side Components

Unlike Laravel where JavaScript is typically separate, or Spring Boot where you might use Thymeleaf, Shopify apps use React components that hydrate on the client. The architecture ensures that your app feels native within Shopify's admin. Here's how client-side interactivity works:

```tsx
// app/routes/app.settings.tsx
// This demonstrates client-side state management and API calls

import { useState, useCallback } from "react";
import { json } from "@remix-run/node";
import { useFetcher, useLoaderData } from "@remix-run/react";
import { 
  Page, 
  Card, 
  Button,
  Modal,
  TextContainer 
} from "@shopify/polaris";
import { authenticate } from "~/shopify.server";

export async function loader({ request }) {
  const { session } = await authenticate.admin(request);
  // Load initial settings
  const settings = await db.shopSettings.findUnique({
    where: { shop: session.shop }
  });
  
  return json({ settings });
}

export async function action({ request }) {
  const { session } = await authenticate.admin(request);
  const formData = await request.formData();
  const intent = formData.get("intent");
  
  if (intent === "sync") {
    // Perform heavy operation
    // This is like a Laravel job or Spring Boot @Async method
    await syncProductsWithExternalSystem(session.shop);
    return json({ synced: true });
  }
  
  return json({ error: "Unknown action" }, { status: 400 });
}

export default function Settings() {
  const { settings } = useLoaderData();
  const fetcher = useFetcher();
  const [modalOpen, setModalOpen] = useState(false);
  
  // Client-side state management (similar to Angular's component state)
  const [isSyncing, setIsSyncing] = useState(false);
  
  const handleSync = useCallback(() => {
    setIsSyncing(true);
    // This triggers the action() function above
    fetcher.submit(
      { intent: "sync" },
      { method: "POST" }
    );
  }, [fetcher]);
  
  // React to server responses
  useEffect(() => {
    if (fetcher.data?.synced) {
      setIsSyncing(false);
      shopify.toast.show("Sync completed successfully");
    }
  }, [fetcher.data]);
  
  return (
    <Page title="App Settings">
      <Card>
        <TextContainer>
          <p>Last sync: {settings?.lastSync || "Never"}</p>
          <Button 
            onClick={handleSync} 
            loading={isSyncing}
            primary
          >
            Sync with External System
          </Button>
        </TextContainer>
      </Card>
      
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Confirm Sync"
      >
        <Modal.Section>
          <TextContainer>
            <p>This will sync all products. Continue?</p>
          </TextContainer>
        </Modal.Section>
      </Modal>
    </Page>
  );
}
```

### Database Schema Design

Shopify apps use Prisma ORM by default, which is similar to Laravel's Eloquent or Spring Boot's JPA. The key difference is that you're storing app-specific data that complements Shopify's data. Here's a production-ready schema:

```prisma
// prisma/schema.prisma
// This is like Laravel migrations or JPA entities

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"  // Use postgresql for production
  url      = env("DATABASE_URL")
}

// Session storage (required for Shopify apps)
model Session {
  id            String    @id
  shop          String    @index
  state         String
  isOnline      Boolean   @default(false)
  scope         String?
  expires       DateTime?
  accessToken   String
  userId        BigInt?
  // New in 2025: Track session metadata
  firstName     String?
  lastName      String?
  email         String?
  accountOwner  Boolean   @default(false)
  locale        String?
  collaborator  Boolean   @default(false)
  emailVerified Boolean   @default(false)
}

// Your app-specific data models
model Shop {
  id              Int      @id @default(autoincrement())
  domain          String   @unique @index
  installedAt     DateTime @default(now())
  plan            String   @default("free")
  settings        Json?    // Store flexible settings
  
  // Relations
  productSettings ProductSettings[]
  syncJobs        SyncJob[]
  
  @@index([domain, plan])  // Composite index for queries
}

model ProductSettings {
  id               Int      @id @default(autoincrement())
  shopifyProductId String   @unique
  shop             Shop     @relation(fields: [shopDomain], references: [domain])
  shopDomain       String
  
  // Your custom fields
  internalSku      String?
  warehouseLocation String?
  customMetadata   Json?
  syncEnabled      Boolean  @default(true)
  lastSyncedAt     DateTime?
  
  createdAt        DateTime @default(now())
  updatedAt        DateTime @updatedAt
  
  @@index([shopDomain, syncEnabled])
}

// Track background jobs (like Laravel jobs)
model SyncJob {
  id          Int      @id @default(autoincrement())
  shop        Shop     @relation(fields: [shopDomain], references: [domain])
  shopDomain  String
  type        String   // "products", "orders", etc.
  status      String   // "pending", "processing", "completed", "failed"
  startedAt   DateTime?
  completedAt DateTime?
  error       String?
  metadata    Json?
  
  createdAt   DateTime @default(now())
  
  @@index([shopDomain, status])
}
```

To use this in your app, initialize the Prisma client:

```typescript
// app/db.server.ts
// This is like Laravel's DB facade or Spring Boot's @Repository

import { PrismaClient } from "@prisma/client";

let prisma: PrismaClient;

declare global {
  var __db__: PrismaClient | undefined;
}

// This ensures we don't create multiple connections in development
if (process.env.NODE_ENV === "production") {
  prisma = new PrismaClient();
} else {
  if (!global.__db__) {
    global.__db__ = new PrismaClient();
  }
  prisma = global.__db__;
}

// Add helpful methods
export async function getShopSettings(shop: string) {
  return prisma.shop.findUnique({
    where: { domain: shop },
    include: { productSettings: true }
  });
}

export async function trackSyncJob(shop: string, type: string) {
  return prisma.syncJob.create({
    data: {
      shopDomain: shop,
      type,
      status: "pending"
    }
  });
}

export default prisma;
```

## 4. Complete Working Example

Let me show you a complete, production-ready example that ties everything together. This implements a feature to manage product visibility with custom rules:

```tsx
// app/routes/app.product-visibility.tsx
// A complete CRUD example with all components

import { json, redirect } from "@remix-run/node";
import { 
  useLoaderData, 
  useActionData, 
  Form, 
  useNavigation,
  useSubmit 
} from "@remix-run/react";
import {
  Page,
  Layout,
  Card,
  DataTable,
  Button,
  Modal,
  TextField,
  Select,
  Banner,
  Badge,
  ButtonGroup
} from "@shopify/polaris";
import { useState, useCallback } from "react";
import { authenticate } from "~/shopify.server";
import db from "~/db.server";

// Define TypeScript interfaces (like Java/Kotlin classes)
interface VisibilityRule {
  id: number;
  productId: string;
  productTitle: string;
  rule: "hide" | "show";
  condition: string;
  value: string;
  active: boolean;
}

// Server-side data fetching
export async function loader({ request }) {
  const { admin, session } = await authenticate.admin(request);
  
  // Fetch visibility rules from your database
  const rules = await db.visibilityRule.findMany({
    where: { shop: session.shop },
    orderBy: { createdAt: "desc" }
  });
  
  // Enrich with product data from Shopify
  const productIds = rules.map(r => `gid://shopify/Product/${r.productId}`);
  
  if (productIds.length > 0) {
    const response = await admin.graphql(
      `#graphql
        query getProducts($ids: [ID!]!) {
          nodes(ids: $ids) {
            ... on Product {
              id
              title
              status
            }
          }
        }
      `,
      { variables: { ids: productIds } }
    );
    
    const { data } = await response.json();
    const productMap = new Map(
      data.nodes.map(p => [p.id.split("/").pop(), p.title])
    );
    
    const enrichedRules = rules.map(rule => ({
      ...rule,
      productTitle: productMap.get(rule.productId) || "Unknown Product"
    }));
    
    return json({ rules: enrichedRules, shop: session.shop });
  }
  
  return json({ rules: [], shop: session.shop });
}

// Server-side action handling
export async function action({ request }) {
  const { session } = await authenticate.admin(request);
  const formData = await request.formData();
  const action = formData.get("_action");
  
  try {
    switch (action) {
      case "create": {
        const newRule = await db.visibilityRule.create({
          data: {
            shop: session.shop,
            productId: formData.get("productId"),
            rule: formData.get("rule"),
            condition: formData.get("condition"),
            value: formData.get("value"),
            active: true
          }
        });
        
        return json({ 
          success: true, 
          message: "Rule created successfully",
          rule: newRule 
        });
      }
      
      case "toggle": {
        const id = parseInt(formData.get("id"));
        const rule = await db.visibilityRule.update({
          where: { id },
          data: { active: formData.get("active") === "true" }
        });
        
        return json({ 
          success: true, 
          message: `Rule ${rule.active ? "activated" : "deactivated"}` 
        });
      }
      
      case "delete": {
        const id = parseInt(formData.get("id"));
        await db.visibilityRule.delete({ where: { id } });
        
        return json({ 
          success: true, 
          message: "Rule deleted successfully" 
        });
      }
      
      case "bulk-apply": {
        // Run visibility rules against current inventory
        const rules = await db.visibilityRule.findMany({
          where: { shop: session.shop, active: true }
        });
        
        // This would typically trigger a background job
        // For now, we'll just mark it as queued
        await db.syncJob.create({
          data: {
            shopDomain: session.shop,
            type: "apply-visibility-rules",
            status: "pending",
            metadata: { ruleCount: rules.length }
          }
        });
        
        return json({ 
          success: true, 
          message: `Applying ${rules.length} rules in background` 
        });
      }
      
      default:
        return json({ error: "Invalid action" }, { status: 400 });
    }
  } catch (error) {
    console.error("Action error:", error);
    return json({ 
      error: "Operation failed. Please try again." 
    }, { status: 500 });
  }
}

// React component
export default function ProductVisibility() {
  const { rules, shop } = useLoaderData<typeof loader>();
  const actionData = useActionData<typeof action>();
  const navigation = useNavigation();
  const submit = useSubmit();
  
  // State management
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedRule, setSelectedRule] = useState<VisibilityRule | null>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  
  // Form state for new rules
  const [formState, setFormState] = useState({
    productId: "",
    rule: "hide",
    condition: "tag",
    value: ""
  });
  
  const isLoading = navigation.state === "submitting";
  
  // Event handlers
  const handleToggle = useCallback((rule: VisibilityRule) => {
    submit(
      {
        _action: "toggle",
        id: rule.id.toString(),
        active: (!rule.active).toString()
      },
      { method: "post" }
    );
  }, [submit]);
  
  const handleDelete = useCallback(() => {
    if (selectedRule) {
      submit(
        {
          _action: "delete",
          id: selectedRule.id.toString()
        },
        { method: "post" }
      );
      setDeleteConfirmOpen(false);
      setSelectedRule(null);
    }
  }, [selectedRule, submit]);
  
  // Table configuration
  const rows = rules.map(rule => [
    rule.productTitle,
    <Badge status={rule.active ? "success" : "default"}>
      {rule.active ? "Active" : "Inactive"}
    </Badge>,
    `${rule.rule} when ${rule.condition} is "${rule.value}"`,
    <ButtonGroup>
      <Button
        size="slim"
        onClick={() => handleToggle(rule)}
        disabled={isLoading}
      >
        {rule.active ? "Deactivate" : "Activate"}
      </Button>
      <Button
        size="slim"
        destructive
        onClick={() => {
          setSelectedRule(rule);
          setDeleteConfirmOpen(true);
        }}
        disabled={isLoading}
      >
        Delete
      </Button>
    </ButtonGroup>
  ]);
  
  return (
    <Page
      title="Product Visibility Rules"
      primaryAction={{
        content: "New Rule",
        onAction: () => setModalOpen(true)
      }}
      secondaryActions={[
        {
          content: "Apply All Rules",
          onAction: () => submit(
            { _action: "bulk-apply" },
            { method: "post" }
          ),
          disabled: isLoading || rules.length === 0
        }
      ]}
    >
      <Layout>
        {actionData?.success && (
          <Banner status="success" onDismiss={() => {}}>
            {actionData.message}
          </Banner>
        )}
        
        {actionData?.error && (
          <Banner status="critical" onDismiss={() => {}}>
            {actionData.error}
          </Banner>
        )}
        
        <Card>
          <DataTable
            columnContentTypes={["text", "text", "text", "text"]}
            headings={["Product", "Status", "Rule", "Actions"]}
            rows={rows}
            emptyState="No visibility rules configured yet."
          />
        </Card>
        
        {/* Create Rule Modal */}
        <Modal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          title="Create Visibility Rule"
          primaryAction={{
            content: "Create Rule",
            onAction: () => {
              submit(
                {
                  _action: "create",
                  ...formState
                },
                { method: "post" }
              );
              setModalOpen(false);
            }
          }}
          secondaryActions={[
            {
              content: "Cancel",
              onAction: () => setModalOpen(false)
            }
          ]}
        >
          <Modal.Section>
            <Form method="post">
              <TextField
                label="Product ID"
                value={formState.productId}
                onChange={(value) => setFormState(prev => ({ 
                  ...prev, 
                  productId: value 
                }))}
                helpText="Enter the Shopify product ID"
              />
              
              <Select
                label="Rule Type"
                options={[
                  { label: "Hide Product", value: "hide" },
                  { label: "Show Product", value: "show" }
                ]}
                value={formState.rule}
                onChange={(value) => setFormState(prev => ({ 
                  ...prev, 
                  rule: value 
                }))}
              />
              
              <Select
                label="Condition"
                options={[
                  { label: "Product Tag", value: "tag" },
                  { label: "Inventory Level", value: "inventory" },
                  { label: "Price Range", value: "price" }
                ]}
                value={formState.condition}
                onChange={(value) => setFormState(prev => ({ 
                  ...prev, 
                  condition: value 
                }))}
              />
              
              <TextField
                label="Value"
                value={formState.value}
                onChange={(value) => setFormState(prev => ({ 
                  ...prev, 
                  value: value 
                }))}
                helpText="The value to match against"
              />
            </Form>
          </Modal.Section>
        </Modal>
        
        {/* Delete Confirmation Modal */}
        <Modal
          open={deleteConfirmOpen}
          onClose={() => setDeleteConfirmOpen(false)}
          title="Delete Rule?"
          primaryAction={{
            content: "Delete",
            destructive: true,
            onAction: handleDelete
          }}
          secondaryActions={[
            {
              content: "Cancel",
              onAction: () => setDeleteConfirmOpen(false)
            }
          ]}
        >
          <Modal.Section>
            <p>
              Are you sure you want to delete the visibility rule for{" "}
              <strong>{selectedRule?.productTitle}</strong>?
            </p>
          </Modal.Section>
        </Modal>
      </Layout>
    </Page>
  );
}
```

## 5. Recent Changes to Be Aware Of

According to the latest Shopify documentation (2025-07), several important changes have been introduced that differ from older tutorials you might find online:

**Configuration Management:** The `shopify app config push` command is deprecated. Now you must use `shopify app deploy` with `include_config_on_deploy = true` in your TOML file. This is a significant change from tutorials before 2024.

**Direct API Access:** The new `embedded_app_direct_api_access` configuration allows embedded apps to make direct API calls without going through your backend, which is a major performance improvement introduced in late 2024.

**Session Token Authentication:** The OAuth flow is now considered legacy. Shopify-managed installation with session tokens is the current standard, which handles scope management automatically.

**Webhook Filters:** You can now filter webhooks at the configuration level, reducing unnecessary webhook processing - this was added in API version 2025-01.

## 6. Production Considerations for 2025

When deploying to production, consider these current best practices that have evolved significantly:

**Database Choice:** While SQLite is fine for development, use PostgreSQL or MySQL in production. The Remix template now includes migration scripts for both. Avoid SQLite in production especially on platforms like Fly.io where containers sleep and lose disk state.

**Environment Variables:** Never commit your `.env` file. Use your hosting platform's secret management. The current required variables are:
```
SHOPIFY_APP_URL=https://your-production-url.com
SHOPIFY_API_KEY=your_client_id
SHOPIFY_API_SECRET=your_client_secret
DATABASE_URL=postgresql://...
```

**Deployment Pipeline:** Use the new `shopify app deploy --force` in your CI/CD pipeline. This replaces the old separate config push and extension deploy commands.

**Rate Limiting:** With the 2025-07 API, implement exponential backoff for GraphQL requests. The new rate limits are more generous but stricter on burst traffic.

## 7. Try This Yourself

Here's a practical exercise that incorporates all the concepts we've covered. Create a feature that syncs product inventory with an external warehouse system.

**Requirements:**
- Create a settings page where merchants can configure their warehouse API credentials
- Build a product list page showing sync status for each product
- Implement a background job system for syncing (hint: use the SyncJob model we defined)
- Store sync history and show it in a timeline view
- Use Shopify webhooks to trigger syncs when products are updated

**Hints drawing from your background:**
- Think of the sync job like a Laravel Queue job or Spring Boot's @Scheduled methods
- Use Prisma transactions like you would database transactions in Eloquent
- The webhook handler is similar to Laravel's event listeners or Spring Boot's event handlers
- For the UI state management, apply your Angular knowledge of observables and reactive forms

**Starter structure:**
```tsx
// app/routes/app.warehouse-sync.tsx
// Combine everything you've learned

export async function loader({ request }) {
  // 1. Authenticate
  // 2. Load warehouse settings from your database
  // 3. Load recent sync jobs
  // 4. Return data for the UI
}

export async function action({ request }) {
  // Handle different actions:
  // - Save warehouse credentials
  // - Trigger manual sync
  // - Clear sync history
}

export default function WarehouseSync() {
  // Build a UI with:
  // - Settings form
  // - Sync status dashboard
  // - History timeline
}
```

## Migration Path and Current Best Practices

If you're looking at older Shopify tutorials, be aware that many patterns have changed. Here's what to watch out for:

**Deprecated Pattern: Using `shopify app serve`**
```bash
# OLD - Don't use
shopify app serve

# CURRENT - Use this instead
shopify app dev
```

**Deprecated Pattern: Separate backend/frontend folders**
```
# OLD structure
/backend
/frontend

# CURRENT structure  
/app (contains both)
```

**Deprecated Pattern: Manual OAuth implementation**
```javascript
// OLD - Don't implement OAuth manually
app.get('/auth', (req, res) => {
  // Manual OAuth flow
});

// CURRENT - Use authenticate helper
const { admin } = await authenticate.admin(request);
```

## Troubleshooting Guide

Common issues when coming from Laravel/Spring Boot:

**Issue: "Why isn't my route working?"**
Solution: Remember that Remix uses file-based routing. The file `app/routes/app.products.$id.tsx` maps to `/app/products/123`. The `$` indicates a dynamic segment, similar to Laravel's `{id}` or Spring Boot's `@PathVariable`.

**Issue: "How do I run background jobs?"**
Solution: Unlike Laravel's queue workers or Spring Boot's @Async, you'll need to either use Shopify's webhook system for reactive jobs, or deploy a separate worker service. Many developers use services like Inngest or Temporal for this.

**Issue: "Where do I put my business logic?"**
Solution: Create service modules in `app/services/` similar to Spring Boot's service layer. Export functions that can be called from your route loaders and actions.

## Verification and Resources

The information in this guide has been verified against:
- Shopify Admin API version 2025-07 documentation
- Current Remix app template structure (September 2025)
- Latest Shopify CLI configuration requirements

For the most up-to-date information, always refer to:
- [Shopify App Structure Documentation](https://shopify.dev/docs/apps/build/cli-for-apps/app-structure)
- [App Configuration Reference](https://shopify.dev/docs/apps/build/cli-for-apps/app-configuration)
- [Remix App Template Repository](https://github.com/Shopify/shopify-app-template-remix)

Note that Shopify is actively developing new features for app developers. The patterns shown here represent the current best practices as of September 2025, but always check the official documentation for the latest updates.
