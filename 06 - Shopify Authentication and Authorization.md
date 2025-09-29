# Shopify Authentication and Authorization

Based on the latest Shopify documentation (September 2025), I'll teach you the modern authentication and authorization patterns for Shopify apps, relating them to your Laravel and Spring Boot experience.

## 1. Current Shopify Documentation Check

According to Shopify's documentation as of September 2025:

**Major Recent Changes:**
- **Shopify Managed Installation** is now the default and recommended approach (replaced manual OAuth flows)
- **Token Exchange** has replaced OAuth 2.0 as the primary authorization method for embedded apps
- **Session Tokens** are mandatory for all embedded apps (third-party cookies don't work anymore)
- **Authorization Code Grant** is now considered legacy but still supported for non-embedded apps

**Current API Version:** 2025-07 (latest stable)

**Critical Update:** The old OAuth 2.0 flow that many tutorials show is now deprecated for embedded apps. If you're following online tutorials from before 2024, they're likely outdated.

## 2. The Laravel/Spring Boot Equivalent

Let me connect Shopify's auth concepts to what you already know:

**Session Tokens (Shopify) ≈ JWT Tokens (Laravel Passport/Spring Security)**
- In Laravel: You might use `tymon/jwt-auth` or Passport for JWT authentication
- In Spring Boot: You'd use Spring Security with JWT filters
- In Shopify: Session tokens are JWTs that authenticate requests between your app's frontend and backend

**Token Exchange (Shopify) ≈ OAuth2 Password Grant (Spring Boot)**
- In Spring Boot: Password grant exchanges credentials for tokens directly
- In Shopify: Token exchange swaps a session token for an API access token
- Both avoid the redirect dance of authorization code flow

**Access Scopes (Shopify) ≈ Laravel Gates/Policies or Spring Security Authorities**
- Laravel: `$user->can('edit-posts')` checks permissions
- Spring Boot: `@PreAuthorize("hasAuthority('WRITE_ORDERS')")` 
- Shopify: Scopes like `write_orders` define what your app can access

**Shopify Managed Installation ≈ Laravel Socialite Auto-Registration**
- Laravel Socialite can auto-register users from OAuth providers
- Shopify now auto-handles the entire installation flow without redirects

## 3. The Current Shopify Way - Architecture Deep Dive

Let me show you the modern authentication flow with an ASCII diagram:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODERN SHOPIFY AUTH FLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. INSTALLATION (Shopify Managed - No Code Required!)           │
│     Merchant clicks install → Shopify handles everything         │
│                                                                   │
│  2. APP LOADS IN IFRAME                                          │
│     ┌──────────┐                                                 │
│     │ Shopify  │──────iframe──────► Your App Frontend           │
│     │  Admin   │                    (React/Remix)                │
│     └──────────┘                                                 │
│                                                                   │
│  3. SESSION TOKEN FLOW (Authentication)                          │
│     Frontend                        Backend                      │
│        │                               │                         │
│        ├──1. Request Session Token────►│                         │
│        │   (App Bridge)                │                         │
│        │                               │                         │
│        ├◄─2. JWT Token (1 min TTL)────┤                         │
│        │                               │                         │
│        ├──3. API Request with ────────►│                         │
│        │   Authorization: Bearer JWT   │                         │
│        │                               │                         │
│        │                          4. Validate JWT               │
│        │                          (shared secret)               │
│        │                               │                         │
│                                                                   │
│  4. TOKEN EXCHANGE (Authorization - First Request Only)          │
│        │                               │                         │
│        │                          5. Exchange JWT               │
│        │                          for Access Token              │
│        │                               │                         │
│        │                          POST /admin/oauth/            │
│        │                          access_token                   │
│        │                               │                         │
│        │                          6. Store Token                │
│        │                          (Database/Redis)              │
│        │                               │                         │
│  5. API CALLS TO SHOPIFY                                         │
│        │                               │                         │
│        ├◄─7. Response Data────────────┤                         │
│        │                               │                         │
│        │                          8. Call GraphQL Admin         │
│        │                          with Access Token             │
│        │                               │                         │
│                                   Shopify GraphQL API           │
└─────────────────────────────────────────────────────────────────┘
```

**Key Differences from Laravel/Spring Boot:**

1. **Iframe Context**: Unlike typical SPAs, Shopify apps run inside an iframe, which creates unique challenges:
   - Can't use cookies (cross-domain restrictions)
   - Must escape iframe for certain operations
   - Session tokens replace CSRF tokens

2. **Dual Token System**: 
   - **Session Token**: Short-lived (1 minute), for frontend→backend auth
   - **Access Token**: Long-lived, for backend→Shopify API calls
   - This is like having both JWT auth tokens AND API keys in Laravel

3. **No Direct Frontend→Shopify API**: 
   - In Angular, you might call APIs directly from the frontend
   - In Shopify, frontend MUST go through your backend (security requirement)

## 4. Complete Working Example - Modern Implementation

Let me provide a complete, production-ready implementation validated against Shopify's current APIs:

### Project Structure (Remix-based, as recommended by Shopify)
```
shopify-app/
├── app/
│   ├── routes/
│   │   ├── app._index.tsx          # Main app page
│   │   ├── app.orders.tsx          # Orders management
│   │   └── auth.$.tsx               # Auth callbacks
│   ├── models/
│   │   └── session.server.ts       # Token storage
│   └── shopify.server.ts           # Shopify config
├── prisma/
│   └── schema.prisma               # Database schema
└── shopify.app.toml                # App configuration
```

### Configuration File (shopify.app.toml)
```toml
# API Version: 2025-07
# Last verified: September 2025
# This replaces the old OAuth scope request!

name = "My Inventory Manager"
client_id = "your-client-id-here"
application_url = "https://your-app.com"
embedded = true

[access_scopes]
# Required scopes (merchant must grant these)
scopes = "read_products,write_inventory,read_orders"

# Optional scopes (can request later)
use_legacy_install_flow = false
optional_scopes = ["read_customers", "write_customers"]

[auth]
redirect_urls = [
  "https://your-app.com/auth/callback",
  "https://your-app.com/auth/shopify/callback"
]

[webhooks]
api_version = "2025-07"
```

### Backend Implementation - Session Token Validation and Token Exchange

```typescript
// app/shopify.server.ts
// API Version: 2025-07
// This is similar to Laravel's auth middleware or Spring Boot's SecurityConfig

import { shopifyApp } from "@shopify/shopify-app-remix/server";
import { PrismaSessionStorage } from "@shopify/shopify-app-session-storage-prisma";
import { restResources } from "@shopify/shopify-api/rest/admin/2025-07";
import prisma from "~/db.server";

// This is like configuring JWT secret in Laravel's config/auth.php
const shopify = shopifyApp({
  apiKey: process.env.SHOPIFY_API_KEY!,
  apiSecretKey: process.env.SHOPIFY_API_SECRET!, // Your "shared secret" for JWT validation
  apiVersion: "2025-07",
  scopes: process.env.SCOPES?.split(",") || [],
  appUrl: process.env.SHOPIFY_APP_URL!,
  authPathPrefix: "/auth",
  
  // Session storage - like Laravel's session driver config
  sessionStorage: new PrismaSessionStorage(prisma),
  
  // Distribution mode - affects auth flow
  distribution: "public", // or "custom" for private client apps
  
  // NEW: Shopify Managed Installation (no OAuth redirect!)
  isEmbeddedApp: true,
  
  // Future flags for upcoming changes
  future: {
    unstable_newEmbeddedAuthStrategy: true, // Uses token exchange
  },
  
  // Webhook handlers - like Laravel event listeners
  webhooks: {
    APP_UNINSTALLED: {
      deliveryMethod: "http",
      callbackUrl: "/webhooks",
    },
  },
  
  // Hook for token exchange completion
  afterAuth: async ({ session, admin }) => {
    // This runs after successful token exchange
    // Similar to Laravel's "authenticated" event listener
    console.log("✅ Token exchange successful for shop:", session.shop);
    
    // Register webhooks (like Laravel job scheduling)
    await registerWebhooks({ session, admin });
  },
});

export default shopify;
export const authenticate = shopify.authenticate;
```

### Session Token Validation Middleware

```typescript
// app/middleware/validateSession.server.ts
// This is like Laravel's auth middleware or Spring Boot's JwtAuthenticationFilter

import jwt from 'jsonwebtoken';
import { json } from '@remix-run/node';

interface SessionTokenPayload {
  iss: string;  // Shop's admin domain
  dest: string; // Shop's domain
  aud: string;  // Your app's client ID
  sub: string;  // User ID
  exp: number;  // Expiration time
  nbf: number;  // Not before time
  iat: number;  // Issued at time
  jti: string;  // Unique token ID
  sid: string;  // Session ID
}

export async function validateSessionToken(request: Request): Promise<SessionTokenPayload> {
  // Extract token from Authorization header
  // In Laravel: $request->bearerToken()
  // In Spring Boot: @RequestHeader("Authorization")
  const authHeader = request.headers.get('Authorization');
  
  if (!authHeader?.startsWith('Bearer ')) {
    throw json({ error: 'Missing session token' }, { status: 401 });
  }
  
  const token = authHeader.slice(7); // Remove "Bearer " prefix
  
  try {
    // Verify JWT signature using shared secret
    // Similar to Laravel's JWT::decode() or Spring's JwtDecoder
    const decoded = jwt.verify(
      token, 
      process.env.SHOPIFY_API_SECRET!,
      { algorithms: ['HS256'] }
    ) as SessionTokenPayload;
    
    // Additional validation checks (Shopify-specific)
    const now = Math.floor(Date.now() / 1000);
    
    // 1. Check expiration (token valid for 1 minute)
    if (decoded.exp < now) {
      throw new Error('Session token expired');
    }
    
    // 2. Check not-before time
    if (decoded.nbf > now) {
      throw new Error('Session token not yet valid');
    }
    
    // 3. Verify shop domain format
    const shopRegex = /^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$/;
    if (!shopRegex.test(decoded.dest)) {
      throw new Error('Invalid shop domain');
    }
    
    // 4. Verify audience matches our app
    if (decoded.aud !== process.env.SHOPIFY_API_KEY) {
      throw new Error('Token not for this app');
    }
    
    return decoded;
    
  } catch (error) {
    throw json({ error: 'Invalid session token' }, { status: 401 });
  }
}
```

### Token Exchange Implementation

```typescript
// app/services/tokenExchange.server.ts
// This is the NEW way - replaces OAuth flow for embedded apps!

interface TokenExchangeResponse {
  access_token: string;
  scope: string;
  expires_in?: number; // Only for online tokens
  associated_user_scope?: string; // User's actual permissions
  associated_user?: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    email_verified: boolean;
    account_owner: boolean;
    locale: string;
    collaborator: boolean;
  };
}

export async function exchangeSessionTokenForAccessToken(
  sessionToken: string,
  shop: string,
  requestedTokenType: 'online' | 'offline' = 'offline'
): Promise<TokenExchangeResponse> {
  // Token Exchange API endpoint (NEW - not OAuth!)
  const tokenExchangeUrl = `https://${shop}/admin/oauth/access_token`;
  
  // Prepare the exchange request
  // This is like OAuth's password grant in Spring Security
  const requestBody = {
    client_id: process.env.SHOPIFY_API_KEY!,
    client_secret: process.env.SHOPIFY_API_SECRET!,
    grant_type: "urn:ietf:params:oauth:grant-type:token-exchange", // RFC 8693 standard
    subject_token: sessionToken,
    subject_token_type: "urn:ietf:params:oauth:token-type:id_token",
    requested_token_type: requestedTokenType === 'online' 
      ? "urn:shopify:params:oauth:token-type:online-access-token"
      : "urn:shopify:params:oauth:token-type:offline-access-token"
  };
  
  try {
    const response = await fetch(tokenExchangeUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    if (!response.ok) {
      // Session token might be expired or invalid
      const error = await response.text();
      throw new Error(`Token exchange failed: ${error}`);
    }
    
    const tokenData = await response.json() as TokenExchangeResponse;
    
    // Store the access token for future API calls
    // Similar to storing API keys in Laravel's database
    await storeAccessToken({
      shop,
      accessToken: tokenData.access_token,
      scope: tokenData.scope,
      expiresAt: tokenData.expires_in 
        ? new Date(Date.now() + tokenData.expires_in * 1000)
        : null, // Offline tokens don't expire
      userId: tokenData.associated_user?.id,
    });
    
    return tokenData;
    
  } catch (error) {
    console.error('Token exchange error:', error);
    throw error;
  }
}
```

### Database Schema for Token Storage

```prisma
// prisma/schema.prisma
// Similar to Laravel's migrations or Spring Boot's JPA entities

model Session {
  id            String    @id @default(cuid())
  shop          String    @unique
  accessToken   String    // Encrypted in production!
  scope         String
  state         String?
  isOnline      Boolean   @default(false)
  expiresAt     DateTime? // NULL for offline tokens
  userId        BigInt?   // Associated user for online tokens
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
  
  @@index([shop])
  @@index([userId])
}

// Store app-specific data
model Shop {
  id                String   @id @default(cuid())
  domain            String   @unique
  name              String?
  email             String?
  installedAt       DateTime @default(now())
  uninstalledAt     DateTime?
  
  // Your app's data
  inventorySettings Json?
  syncEnabled       Boolean  @default(true)
  
  @@index([domain])
}
```

### Frontend Implementation with App Bridge

```tsx
// app/routes/app._index.tsx
// React component using Shopify App Bridge for session tokens

import { useEffect, useState } from "react";
import { json } from "@remix-run/node";
import { useFetcher, useLoaderData } from "@remix-run/react";
import { Page, Card, Button, DataTable } from "@shopify/polaris";
import { authenticate } from "~/shopify.server";

// Loader function - runs on the server
// Similar to Laravel's Controller or Spring Boot's @GetMapping
export async function loader({ request }: LoaderFunctionArgs) {
  // NEW: This single line handles ALL authentication!
  // - Validates session token
  // - Performs token exchange if needed
  // - Returns admin API client
  const { admin, session } = await authenticate.admin(request);
  
  // Now you can make authenticated API calls
  const response = await admin.graphql(`
    query getProducts {
      products(first: 10) {
        edges {
          node {
            id
            title
            totalInventory
            status
          }
        }
      }
    }
  `);
  
  const { data } = await response.json();
  
  return json({
    products: data.products.edges.map(edge => edge.node),
    shop: session.shop,
  });
}

// Action function - handles POST requests
// Like Laravel's store() or Spring Boot's @PostMapping
export async function action({ request }: ActionFunctionArgs) {
  const { admin } = await authenticate.admin(request);
  
  const formData = await request.formData();
  const productId = formData.get("productId");
  const quantity = formData.get("quantity");
  
  // Update inventory using GraphQL Admin API
  const response = await admin.graphql(`
    mutation adjustInventory($input: InventoryAdjustQuantityInput!) {
      inventoryAdjustQuantity(input: $input) {
        inventoryLevel {
          available
        }
        userErrors {
          field
          message
        }
      }
    }
  `, {
    variables: {
      input: {
        inventoryItemId: productId,
        availableDelta: parseInt(quantity as string),
      }
    }
  });
  
  return json({ success: true });
}

export default function Index() {
  const { products, shop } = useLoaderData<typeof loader>();
  const fetcher = useFetcher();
  
  // App Bridge automatically includes session token in requests!
  // No manual JWT handling needed on the frontend
  
  const updateInventory = (productId: string) => {
    // This automatically includes the session token
    fetcher.submit(
      { productId, quantity: "10" },
      { method: "post" }
    );
  };
  
  return (
    <Page title="Inventory Manager">
      <Card>
        <p>Managing inventory for: {shop}</p>
        <DataTable
          columnContentTypes={["text", "numeric", "text"]}
          headings={["Product", "Inventory", "Actions"]}
          rows={products.map(product => [
            product.title,
            product.totalInventory,
            <Button onClick={() => updateInventory(product.id)}>
              Add 10 Units
            </Button>
          ])}
        />
      </Card>
    </Page>
  );
}
```

## 5. Advanced Patterns - Access Management

### Online vs Offline Access Tokens

```typescript
// app/models/accessToken.server.ts
// Understanding the token lifecycle - crucial for production apps

/**
 * OFFLINE ACCESS TOKENS (Default)
 * - Never expire (valid until app uninstalled)
 * - Used for background jobs, webhooks
 * - Like API keys in Laravel or service accounts in Spring
 * - One per shop
 */
export async function getOfflineAccessToken(shop: string): Promise<string> {
  const session = await prisma.session.findUnique({
    where: { shop, isOnline: false }
  });
  
  if (!session || !session.accessToken) {
    throw new Error('No offline access token found');
  }
  
  // Decrypt token if encrypted (you should encrypt in production!)
  return decryptToken(session.accessToken);
}

/**
 * ONLINE ACCESS TOKENS
 * - Expire after 24 hours OR when user logs out
 * - Tied to specific user (respects user permissions)
 * - Like user sessions in Laravel or Spring Security context
 * - Multiple per shop (one per user session)
 */
export async function getOnlineAccessToken(
  shop: string, 
  userId: string
): Promise<string | null> {
  const session = await prisma.session.findFirst({
    where: { 
      shop, 
      userId,
      isOnline: true,
      expiresAt: { gt: new Date() } // Not expired
    }
  });
  
  if (!session) {
    // Need to re-authenticate (user needs to log in again)
    return null;
  }
  
  // Check if token needs refresh (within 1 hour of expiry)
  const oneHourFromNow = new Date(Date.now() + 60 * 60 * 1000);
  if (session.expiresAt && session.expiresAt < oneHourFromNow) {
    return await refreshOnlineToken(shop, userId);
  }
  
  return decryptToken(session.accessToken);
}

// Token refresh strategy for online tokens
async function refreshOnlineToken(shop: string, userId: string): Promise<string> {
  // Online tokens can't be refreshed - need new token exchange
  // This is why most apps use offline tokens
  console.log('Online token expiring soon, need re-authentication');
  
  // In practice, you'd trigger a re-authentication flow
  throw new Error('Online token refresh required');
}
```

### Handling Protected Customer Data

```typescript
// app/services/protectedData.server.ts
// NEW: Shopify now requires explicit permission for customer PII

interface ProtectedCustomerDataConfig {
  // Level 1: Basic customer data (no PII)
  level1: {
    enabled: boolean;
    fields: string[];
  };
  
  // Level 2: PII (name, email, phone, address)
  level2: {
    enabled: boolean;
    fields: ('name' | 'email' | 'phone' | 'address')[];
    dataProtectionOfficer?: string;
    gdprCompliant: boolean;
    dataRetentionDays: number;
  };
}

export class ProtectedDataHandler {
  private config: ProtectedCustomerDataConfig;
  
  constructor(config: ProtectedCustomerDataConfig) {
    this.config = config;
  }
  
  // Check if we have access to specific fields
  async queryCustomerData(admin: AdminApiContext, customerId: string) {
    try {
      const response = await admin.graphql(`
        query getCustomer($id: ID!) {
          customer(id: $id) {
            id
            ${this.config.level2.fields.includes('name') ? 'firstName lastName' : ''}
            ${this.config.level2.fields.includes('email') ? 'email' : ''}
            ${this.config.level2.fields.includes('phone') ? 'phone' : ''}
            ${this.config.level2.fields.includes('address') ? `
              addresses(first: 5) {
                address1
                address2
                city
                province
                country
                zip
              }
            ` : ''}
          }
        }
      `, {
        variables: { id: customerId }
      });
      
      const { data, errors } = await response.json();
      
      // Handle field-level access errors
      if (errors) {
        errors.forEach(error => {
          if (error.message.includes('not approved to access')) {
            console.warn('Protected field access denied:', error.path);
            // Field will be null in response
          }
        });
      }
      
      return data.customer;
      
    } catch (error) {
      console.error('Failed to fetch customer data:', error);
      throw error;
    }
  }
  
  // Implement data retention policy (GDPR requirement)
  async enforceDataRetention() {
    const retentionDate = new Date();
    retentionDate.setDate(retentionDate.getDate() - this.config.level2.dataRetentionDays);
    
    // Delete old customer data from your database
    await prisma.customerData.deleteMany({
      where: {
        createdAt: { lt: retentionDate }
      }
    });
  }
  
  // Log access for audit trail (Level 2 requirement)
  async logDataAccess(userId: string, customerId: string, fields: string[]) {
    await prisma.dataAccessLog.create({
      data: {
        userId,
        customerId,
        accessedFields: fields,
        timestamp: new Date(),
        ip: getClientIp(), // Track who accessed what
      }
    });
  }
}
```

### Dynamic Scope Management

```typescript
// app/services/scopeManager.server.ts
// Dynamically request additional permissions after installation

export class ScopeManager {
  // Check current scopes
  async getCurrentScopes(admin: AdminApiContext): Promise<string[]> {
    const response = await admin.graphql(`
      query {
        currentAppInstallation {
          accessScopes {
            handle
          }
        }
      }
    `);
    
    const { data } = await response.json();
    return data.currentAppInstallation.accessScopes.map(s => s.handle);
  }
  
  // Request additional optional scopes (NEW in 2024)
  async requestOptionalScopes(
    shop: string, 
    requestedScopes: string[]
  ): Promise<void> {
    // This triggers a permission update flow in Shopify admin
    // User must approve the new scopes
    
    const requestUrl = `https://admin.shopify.com/store/${shop}/oauth/request_grant`;
    
    const params = new URLSearchParams({
      client_id: process.env.SHOPIFY_API_KEY!,
      scope: requestedScopes.join(','),
      redirect_uri: `${process.env.SHOPIFY_APP_URL}/auth/grant_callback`,
    });
    
    // This URL is shown to the merchant for approval
    console.log('Request scope upgrade:', `${requestUrl}?${params}`);
    
    // In practice, you'd redirect the user or show a modal
    // using App Bridge's Redirect action
  }
  
  // Handle scope update webhook
  async handleScopeUpdate(webhook: WebhookPayload) {
    const { shop, updated_scopes } = webhook;
    
    // Update stored scopes in database
    await prisma.shop.update({
      where: { domain: shop },
      data: {
        grantedScopes: updated_scopes,
        scopesUpdatedAt: new Date(),
      }
    });
    
    console.log(`Scopes updated for ${shop}:`, updated_scopes);
  }
}
```

## 6. Real-World Scenarios

### Scenario 1: Multi-Store Inventory Sync

```typescript
// app/jobs/inventorySync.server.ts
// Background job using offline access token

export async function syncInventoryAcrossStores() {
  // Get all shops with our app installed
  const shops = await prisma.shop.findMany({
    where: { 
      uninstalledAt: null,
      syncEnabled: true 
    }
  });
  
  for (const shop of shops) {
    try {
      // Get offline access token (never expires)
      const accessToken = await getOfflineAccessToken(shop.domain);
      
      // Create admin context for this shop
      const admin = createAdminApiClient({
        shop: shop.domain,
        accessToken,
        apiVersion: '2025-07',
      });
      
      // Fetch inventory levels
      const response = await admin.graphql(`
        query {
          locations(first: 10) {
            edges {
              node {
                id
                inventoryLevels(first: 100) {
                  edges {
                    node {
                      item { sku }
                      available
                    }
                  }
                }
              }
            }
          }
        }
      `);
      
      // Process and sync inventory...
      
    } catch (error) {
      console.error(`Sync failed for ${shop.domain}:`, error);
      
      // Handle token expiration (shouldn't happen with offline tokens)
      if (error.message.includes('401')) {
        // App might have been reinstalled - need new token
        await markShopForReauthorization(shop.domain);
      }
    }
  }
}

// Run this job every hour
// In Laravel: Schedule::job(new SyncInventory)->hourly();
// In Spring Boot: @Scheduled(fixedRate = 3600000)
```

### Scenario 2: User-Specific Permissions with Online Tokens

```typescript
// app/services/userPermissions.server.ts
// Respecting individual user permissions

export async function performUserAction(
  request: Request,
  action: 'viewReports' | 'editProducts' | 'manageOrders'
) {
  // Get session token from request
  const sessionToken = await validateSessionToken(request);
  
  // Exchange for ONLINE token (respects user permissions)
  const tokenData = await exchangeSessionTokenForAccessToken(
    sessionToken.jti,
    sessionToken.dest,
    'online' // Important: online token for user-specific actions
  );
  
  // Check if user has required scope
  const userScopes = tokenData.associated_user_scope?.split(',') || [];
  
  const requiredScopes = {
    viewReports: ['read_reports'],
    editProducts: ['write_products'],
    manageOrders: ['write_orders'],
  };
  
  const hasPermission = requiredScopes[action].every(
    scope => userScopes.includes(scope)
  );
  
  if (!hasPermission) {
    // User lacks permission - similar to Laravel's abort(403)
    throw new Response('Insufficient permissions', { status: 403 });
  }
  
  // Perform action with user's token...
  // Token automatically respects user's permission level
  // Staff members without write_products can't edit products
}
```

### Scenario 3: Handling Session Token Expiry

```typescript
// app/components/AuthenticatedFetcher.tsx
// Frontend component that handles token refresh automatically

import { useFetcher } from "@remix-run/react";
import { useAppBridge } from "@shopify/app-bridge-react";
import { getSessionToken } from "@shopify/app-bridge/utilities";

export function useAuthenticatedFetcher() {
  const fetcher = useFetcher();
  const app = useAppBridge();
  
  const authenticatedSubmit = async (
    data: FormData | Record<string, any>,
    options?: SubmitOptions
  ) => {
    // Always get fresh session token (1-minute TTL)
    const token = await getSessionToken(app);
    
    // Add token to request headers
    const headers = new Headers(options?.headers || {});
    headers.set('Authorization', `Bearer ${token}`);
    
    // Retry logic for expired tokens
    let retries = 0;
    const maxRetries = 3;
    
    while (retries < maxRetries) {
      try {
        return await fetcher.submit(data, {
          ...options,
          headers,
        });
      } catch (error) {
        if (error.status === 401 && retries < maxRetries - 1) {
          // Token might have expired mid-request
          // Get new token and retry
          const newToken = await getSessionToken(app);
          headers.set('Authorization', `Bearer ${newToken}`);
          retries++;
          
          // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, retries) * 100));
        } else {
          throw error;
        }
      }
    }
  };
  
  return {
    ...fetcher,
    submit: authenticatedSubmit,
  };
}
```

## 7. Migration Path from Legacy OAuth

If you have an existing app using the old OAuth flow, here's how to migrate:

```typescript
// app/migration/oauthToTokenExchange.ts
// Step-by-step migration guide

export class AuthMigration {
  // Step 1: Update shopify.app.toml
  async updateConfiguration() {
    // Old (OAuth):
    // scopes = "read_products,write_orders"
    // use_legacy_install_flow = true
    
    // New (Shopify Managed):
    // [access_scopes]
    // scopes = "read_products,write_orders"
    // use_legacy_install_flow = false
  }
  
  // Step 2: Replace OAuth routes with token exchange
  async migrateAuthRoutes() {
    // DELETE these OAuth routes:
    // - /auth/shopify (OAuth initiation)
    // - /auth/shopify/callback (OAuth callback)
    
    // ADD token exchange in your authenticated routes:
    // The authenticate.admin() function handles it automatically
  }
  
  // Step 3: Update frontend to use session tokens
  async migrateFrontend() {
    // Old: Direct API calls with stored access token
    // await fetch('/api/products', {
    //   headers: { 'X-Shopify-Access-Token': storedToken }
    // });
    
    // New: Use session tokens
    // const token = await getSessionToken(app);
    // await fetch('/api/products', {
    //   headers: { 'Authorization': `Bearer ${token}` }
    // });
  }
  
  // Step 4: Handle existing installations
  async handleExistingInstallations() {
    // Existing OAuth tokens continue to work!
    // New installations use token exchange
    // You can run both in parallel during migration
    
    const isLegacyInstallation = (shop: string) => {
      // Check if shop was installed before migration
      return prisma.shop.findFirst({
        where: { 
          domain: shop,
          installedAt: { lt: new Date('2025-01-01') }
        }
      });
    };
    
    // Use appropriate auth method
    if (await isLegacyInstallation(shop)) {
      // Use stored OAuth token
      return getStoredOAuthToken(shop);
    } else {
      // Use token exchange
      return authenticate.admin(request);
    }
  }
}
```

## 8. Production Considerations for 2025

Based on current Shopify best practices, here are critical production considerations:

### Security Checklist

```typescript
// app/security/checklist.ts

export const SECURITY_REQUIREMENTS = {
  // 1. Token Storage
  tokenStorage: {
    encryption: 'AES-256-GCM', // Encrypt tokens at rest
    keyRotation: '90 days',     // Rotate encryption keys
    storage: 'database',        // Never store in code or env files
  },
  
  // 2. Session Token Validation
  sessionValidation: {
    verifySignature: true,      // Always verify JWT signature
    checkExpiration: true,      // Tokens expire in 1 minute
    validateShopDomain: true,   // Prevent shop spoofing
    validateAudience: true,     // Ensure token is for your app
  },
  
  // 3. Protected Customer Data (GDPR)
  customerData: {
    minimizeCollection: true,   // Only collect what you need
    encryptPII: true,          // Encrypt names, emails, addresses
    retentionPolicy: '2 years', // Auto-delete old data
    auditLogging: true,        // Log all PII access
    rightToErasure: true,      // Support customer deletion requests
  },
  
  // 4. Rate Limiting
  rateLimiting: {
    sessionTokenRequests: '60/min',  // Prevent token exhaustion
    apiRequests: '2/sec',            // Respect Shopify limits
    retryStrategy: 'exponential',    // Back off on 429 errors
  },
  
  // 5. Webhook Verification
  webhookSecurity: {
    verifyHMAC: true,          // Always verify webhook signatures
    replayProtection: true,    // Prevent replay attacks
    timeoutValidation: '5min', // Reject old webhooks
  },
};
```

### Performance Optimizations

```typescript
// app/performance/optimizations.ts

export class PerformanceOptimizer {
  // Cache access tokens to avoid repeated exchanges
  private tokenCache = new Map<string, { token: string; expires: Date }>();
  
  async getAccessTokenWithCache(shop: string): Promise<string> {
    // Check cache first
    const cached = this.tokenCache.get(shop);
    if (cached && cached.expires > new Date()) {
      return cached.token;
    }
    
    // Get token from database
    const token = await getOfflineAccessToken(shop);
    
    // Cache for 5 minutes (safe for offline tokens)
    this.tokenCache.set(shop, {
      token,
      expires: new Date(Date.now() + 5 * 60 * 1000),
    });
    
    return token;
  }
  
  // Batch GraphQL queries to reduce API calls
  async batchGraphQLQueries(shop: string, queries: string[]) {
    const admin = await this.getAdminContext(shop);
    
    // Combine multiple queries into one request
    const combinedQuery = `
      query BatchQuery {
        ${queries.map((q, i) => `q${i}: ${q}`).join('\n')}
      }
    `;
    
    return admin.graphql(combinedQuery);
  }
  
  // Use database connection pooling
  // Similar to Laravel's DB::connection()->getPdo()
  private dbPool = new PrismaClient({
    datasources: {
      db: {
        url: process.env.DATABASE_URL,
      },
    },
    log: ['error', 'warn'],
    // Connection pool settings
    connection_limit: 10,
    pool_timeout: 10,
  });
}
```

## 9. Hands-On Exercise

Let's build a complete feature that demonstrates all authentication concepts:

**Exercise: Build a Customer Data Export Feature**

Requirements:
1. Authenticate admin users with online tokens (respect permissions)
2. Request access to protected customer fields
3. Export customer data with GDPR compliance
4. Handle token expiry gracefully

**Your Challenge:**

```typescript
// TODO: Implement this complete feature
// app/routes/app.customers.export.tsx

export async function action({ request }: ActionFunctionArgs) {
  // TODO: 
  // 1. Validate session token
  // 2. Exchange for ONLINE token (user-specific)
  // 3. Check if user has 'read_customers' scope
  // 4. Query customers with protected fields
  // 5. Handle field-level access errors
  // 6. Log data access for GDPR audit
  // 7. Generate CSV with only approved fields
  // 8. Return file download response
  
  // Hints:
  // - Use authenticate.admin(request) with { online: true }
  // - Check tokenData.associated_user_scope for permissions
  // - Wrap customer queries in try-catch for field errors
  // - Use ProtectedDataHandler class from earlier
  // - Remember to encrypt exported data
}
```

**Solution Framework:**

```typescript
// Complete solution with all security considerations

import { authenticate } from "~/shopify.server";
import { ProtectedDataHandler } from "~/services/protectedData.server";
import { createReadStream } from "fs";
import { parse } from "csv-parse";
import { stringify } from "csv-stringify";
import crypto from "crypto";

export async function action({ request }: ActionFunctionArgs) {
  // Step 1: Authenticate with ONLINE token for user permissions
  const { admin, session } = await authenticate.admin(request, {
    // Request online token to respect user permissions
    online: true,
  });
  
  // Step 2: Verify user has permission to export customers
  const formData = await request.formData();
  const exportType = formData.get("exportType") as string;
  
  // Get user's actual permissions from the token
  const tokenInfo = await admin.graphql(`
    query {
      currentAppInstallation {
        accessScopes {
          handle
        }
        userGrants {
          handle
        }
      }
    }
  `);
  
  const { data } = await tokenInfo.json();
  const userScopes = data.currentAppInstallation.userGrants.map(g => g.handle);
  
  if (!userScopes.includes("read_customers")) {
    throw new Response("You don't have permission to export customer data", {
      status: 403,
    });
  }
  
  // Step 3: Initialize protected data handler
  const protectedDataHandler = new ProtectedDataHandler({
    level1: { enabled: true, fields: ["id", "createdAt"] },
    level2: {
      enabled: true,
      fields: ["name", "email"], // Only export approved fields
      gdprCompliant: true,
      dataRetentionDays: 730,
    },
  });
  
  // Step 4: Query customers with error handling for protected fields
  let customers = [];
  let hasNextPage = true;
  let cursor = null;
  
  while (hasNextPage) {
    const query = `
      query getCustomers($cursor: String) {
        customers(first: 50, after: $cursor) {
          edges {
            node {
              id
              createdAt
              firstName
              lastName
              email
              phone
              ordersCount
              totalSpent {
                amount
                currencyCode
              }
            }
            cursor
          }
          pageInfo {
            hasNextPage
          }
        }
      }
    `;
    
    try {
      const response = await admin.graphql(query, {
        variables: { cursor },
      });
      
      const { data, errors } = await response.json();
      
      // Handle field-level errors for protected data
      if (errors) {
        errors.forEach(error => {
          if (error.path?.includes("phone")) {
            console.log("Phone field not approved, will be excluded from export");
          }
        });
      }
      
      // Process customers, filtering null protected fields
      const edges = data.customers.edges;
      customers.push(...edges.map(edge => ({
        id: edge.node.id,
        createdAt: edge.node.createdAt,
        firstName: edge.node.firstName || "[REDACTED]",
        lastName: edge.node.lastName || "[REDACTED]",
        email: edge.node.email || "[REDACTED]",
        phone: edge.node.phone || "[NOT APPROVED]",
        ordersCount: edge.node.ordersCount,
        totalSpent: edge.node.totalSpent?.amount || "0",
      })));
      
      hasNextPage = data.customers.pageInfo.hasNextPage;
      cursor = edges[edges.length - 1]?.cursor;
      
    } catch (error) {
      console.error("Failed to fetch customers:", error);
      throw new Response("Export failed", { status: 500 });
    }
  }
  
  // Step 5: Log data access for GDPR compliance
  await protectedDataHandler.logDataAccess(
    session.userId,
    "bulk_export",
    ["firstName", "lastName", "email"]
  );
  
  // Step 6: Generate encrypted CSV
  const csv = await stringify(customers, {
    header: true,
    columns: [
      "id", "createdAt", "firstName", "lastName", 
      "email", "ordersCount", "totalSpent"
    ],
  });
  
  // Encrypt the CSV for secure download
  const algorithm = 'aes-256-gcm';
  const password = crypto.randomBytes(32);
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, password, iv);
  
  let encrypted = cipher.update(csv, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  const authTag = cipher.getAuthTag();
  
  // Step 7: Return secure download response
  return new Response(encrypted, {
    status: 200,
    headers: {
      "Content-Type": "application/octet-stream",
      "Content-Disposition": `attachment; filename="customers_export_${Date.now()}.enc"`,
      "X-Encryption-Key": password.toString('base64'),
      "X-Encryption-IV": iv.toString('base64'),
      "X-Auth-Tag": authTag.toString('base64'),
      "X-Export-Count": customers.length.toString(),
    },
  });
}
```

**Hints for the Exercise:**
- Think about why we use online tokens here (user permissions)
- Consider what happens if a field is not approved
- Remember GDPR requirements for data exports
- Test with users having different permission levels

## 10. Troubleshooting Guide

Common issues and solutions based on current Shopify patterns:

```typescript
// app/debug/authTroubleshooting.ts

export const AUTH_TROUBLESHOOTING = {
  // Problem 1: "Missing session token" errors
  missingSessionToken: {
    symptoms: ["401 Unauthorized", "Missing Authorization header"],
    causes: [
      "App Bridge not initialized",
      "Request made outside iframe context",
      "Direct API call instead of using App Bridge fetch",
    ],
    solutions: [
      "Ensure App Bridge is initialized with correct API key",
      "Use authenticatedFetch from App Bridge",
      "Check if app is running in embedded context",
    ],
  },
  
  // Problem 2: "Invalid session token" errors
  invalidSessionToken: {
    symptoms: ["401 Unauthorized", "JWT verification failed"],
    causes: [
      "Token expired (1-minute TTL)",
      "Wrong API secret for verification",
      "Clock skew between client and server",
    ],
    solutions: [
      "Always get fresh token before requests",
      "Verify SHOPIFY_API_SECRET is correct",
      "Implement retry logic with fresh tokens",
    ],
  },
  
  // Problem 3: Token exchange failures
  tokenExchangeFailed: {
    symptoms: ["400 Bad Request", "invalid_grant error"],
    causes: [
      "Session token already used",
      "Session token expired",
      "Wrong grant_type parameter",
    ],
    solutions: [
      "Never reuse session tokens for exchange",
      "Get fresh session token for each exchange",
      "Use exact grant_type: 'urn:ietf:params:oauth:grant-type:token-exchange'",
    ],
  },
  
  // Problem 4: Protected customer data access denied
  protectedDataDenied: {
    symptoms: ["null values for customer fields", "field access errors"],
    causes: [
      "App not approved for protected data",
      "Specific fields not approved",
      "Development vs production environment",
    ],
    solutions: [
      "Request access in Partner Dashboard",
      "Check which fields are approved",
      "Test with development stores first",
    ],
  },
  
  // Problem 5: Webhook verification failures
  webhookVerificationFailed: {
    symptoms: ["401 on webhook endpoints", "HMAC mismatch"],
    causes: [
      "Wrong webhook secret",
      "Body parsing before verification",
      "Incorrect HMAC calculation",
    ],
    solutions: [
      "Use raw body for HMAC calculation",
      "Verify webhook secret matches",
      "Use Shopify's webhook verification utilities",
    ],
  },
};

// Debug helper function
export async function debugAuthIssue(error: any, context: any) {
  console.group("🔍 Auth Debug Info");
  console.log("Error:", error.message);
  console.log("Status:", error.status);
  console.log("Context:", {
    shop: context.shop,
    isOnline: context.isOnline,
    hasToken: !!context.token,
    tokenAge: context.tokenAge,
  });
  
  // Suggest likely solution
  if (error.message.includes("Missing session token")) {
    console.warn("💡 Likely solution: Ensure App Bridge is initialized");
  } else if (error.message.includes("expired")) {
    console.warn("💡 Likely solution: Get fresh session token");
  } else if (error.message.includes("not approved")) {
    console.warn("💡 Likely solution: Request protected data access in Partner Dashboard");
  }
  
  console.groupEnd();
}
```

## Summary and Key Takeaways

**According to Shopify's latest documentation (September 2025):**

1. **Shopify Managed Installation** is now standard - no more OAuth redirect dance
2. **Token Exchange** replaces OAuth for embedded apps - simpler and faster
3. **Session Tokens** (1-minute JWT) authenticate frontend→backend
4. **Access Tokens** (long-lived) authenticate backend→Shopify API
5. **Online vs Offline Tokens** - choose based on use case
6. **Protected Customer Data** requires explicit approval and GDPR compliance

**Critical Differences from Laravel/Spring Boot:**
- Dual token system (session + access)
- Iframe context complications
- Mandatory backend proxy for API calls
- Strict GDPR requirements for customer data

**Next Steps:**
- Practice implementing token exchange in a real app
- Set up proper token storage with encryption
- Implement GDPR compliance for customer data
- Build webhook handlers with proper verification

This modern approach is significantly simpler than the old OAuth flow, but requires understanding the dual-token system and iframe context. The key is letting Shopify handle as much as possible through managed installation and token exchange.
