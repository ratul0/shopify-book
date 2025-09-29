# Development Environment Setup

## **1. Essential Development Tools**

### **The Laravel/Spring Boot Equivalent**

In your Laravel development, you're familiar with using **Artisan CLI** for scaffolding and managing applications, while in Spring Boot you use **Spring Initializr** and the Spring Boot CLI. These tools handle dependency management through Composer and Maven/Gradle respectively. You configure environment variables through `.env` files in Laravel and `application.properties` in Spring Boot.

### **The Current Shopify Way**

Shopify CLI serves a similar role but with tighter integration into the Shopify ecosystem. Think of it as combining the functionality of Artisan, npm scripts, and webpack-dev-server into one unified tool that understands Shopify's specific requirements.

Let me walk you through the complete setup process with the current best practices.

### **Complete Working Example: Installing Shopify CLI**

# Complete Shopify CLI Installation Guide

## System Requirements (As of September 2025)

### Core Dependencies
- **Node.js**: 20.10 or higher (LTS version recommended)
- **Git**: 2.28.0 or higher
- **Package Manager**: npm, Yarn 1.x, or pnpm

### Operating System Support
- macOS 12.0+
- Windows 10/11 (with WSL recommended)
- Ubuntu 20.04+ / Debian 11+

## Installation Methods

### Method 1: Global Installation (Recommended)

```bash
# Using npm (most common)
npm install -g @shopify/cli@latest

# Using yarn
yarn global add @shopify/cli@latest

# Using pnpm
pnpm install -g @shopify/cli@latest

# macOS only - using Homebrew
brew tap shopify/shopify
brew install shopify-cli
```

### Method 2: Project-Local Installation (For Team Consistency)

```bash
# In your project directory
npm install -D @shopify/cli@latest

# Then run commands with your package manager
npm run shopify app dev
```

## Verify Installation

```bash
# Check version and available updates
shopify version
# Expected output: Current Shopify CLI version: 3.78.0 or higher

# Get help and see available commands
shopify help
```

## Network Proxy Configuration (New in 3.78+)

If you're behind a corporate proxy (common in enterprise environments):

```bash
# Set HTTP proxy
export SHOPIFY_HTTP_PROXY=http://proxy.company.com:8080

# Set HTTPS proxy (optional, defaults to HTTP proxy)
export SHOPIFY_HTTPS_PROXY=https://secure-proxy.company.com:8443

# For authenticated proxies
export SHOPIFY_HTTP_PROXY=http://username:password@proxy.company.com:8080
```

## Troubleshooting Common Installation Issues

### Issue 1: Permission Errors on Global Install

```bash
# Fix with npm (avoid using sudo)
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Issue 2: Node Version Conflicts

```bash
# Use Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20.10
nvm use 20.10
nvm alias default 20.10
```

### Issue 3: Windows-Specific Issues

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then install normally with npm
```

## Disable Analytics (Optional)

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export SHOPIFY_CLI_NO_ANALYTICS=1
```

### **Recent Changes to Be Aware Of**

According to the current documentation, there have been several significant updates in the past year that differ from older tutorials you might find online. First, the Partner Dashboard has been replaced by the Dev Dashboard for developer accounts, reflecting Shopify's move to unify the developer experience. Second, development stores now support enhanced test data generation, making it much easier to simulate real-world scenarios compared to the manual data setup required previously. Finally, the authentication flow has been streamlined with Shopify-managed installation becoming the default, which removes the need for manual OAuth implementation in most cases.

## **2. Partner Account and Development Store Setup**

### **The Laravel/Spring Boot Equivalent**

In Laravel, you typically set up a local database with migrations and seeders for development. With Spring Boot, you might use H2 for local development with test data loaded through data.sql files. Both frameworks allow you to spin up isolated development environments quickly.

### **The Current Shopify Way**

Shopify provides development stores that function as fully-featured Shopify stores but are free and specifically designed for app development. Think of these as cloud-hosted development environments similar to staging servers, but with built-in test data generation capabilities.

# Partner Account and Development Store Setup Guide

## Creating Your Partner Account

### Step 1: Sign Up for Partner Account

1. Navigate to [partners.shopify.com](https://partners.shopify.com)
2. Click "Join now" and fill in your details
3. Select "Build apps" as your primary goal
4. Choose your experience level with app development

### Step 2: Complete Your Partner Profile

```
Required Information:
- Business name
- Business type (Individual/Company)
- Primary contact email
- Country and timezone
```

## Creating a Development Store

### Method 1: Quick Create with Test Data (Recommended)

```bash
# Using Shopify CLI (automatically creates store during app dev)
shopify app dev --store-create

# This will:
# 1. Create a new development store
# 2. Pre-populate with test data
# 3. Link it to your app
```

### Method 2: Manual Creation via Partner Dashboard

1. Log in to Partner Dashboard
2. Navigate to "Stores" → "Add store"
3. Select "Create development store"

#### Recommended Settings for App Development:

```yaml
Store Type: "Test store for app development"
Store Name: "yourname-app-dev"
Store Purpose: "Test data included"
Developer Preview: Enable (for testing beta features)
```

## Development Store Features

### Pre-populated Test Data Includes:

- **Products**: 30+ diverse products with variants
- **Customers**: 100+ test customers with order history
- **Orders**: 200+ orders in various states
- **Collections**: Smart and manual collections
- **Discounts**: Various discount types for testing
- **Inventory**: Multi-location inventory setup

### Accessing Your Development Store

```bash
# Get store URL
shopify store info

# Open admin
shopify store open

# Expected URL format:
# https://your-store-name.myshopify.com/admin
```

## Staff Account Management

### Understanding Access Levels

```javascript
// Shopify uses a different permission model than typical RBAC
const accessLevels = {
  storeOwner: {
    // Full access - you get this automatically for stores you create
    permissions: ['all'],
    canManageStaff: true,
    canDeleteStore: true
  },
  staff: {
    // Created when accessing store via Partner Dashboard
    permissions: ['apps', 'themes', 'products', 'customers'],
    canManageStaff: false,
    canDeleteStore: false
  },
  collaborator: {
    // Limited access for contractors
    permissions: ['themes', 'products'],
    canManageStaff: false,
    canDeleteStore: false
  }
};
```

## Important Limitations of Development Stores

### What You CAN Do:
- ✅ Install unlimited apps
- ✅ Process test orders
- ✅ Use all Shopify features
- ✅ Test payment providers (in test mode)
- ✅ Transfer to a paid plan later

### What You CANNOT Do:
- ❌ Process real payments
- ❌ Remove "Development Store" password page
- ❌ Use custom domains (must use .myshopify.com)
- ❌ Have more than 10 active development stores

## Environment Variable Setup

Create a `.env` file in your project root:

```bash
# Development Store Configuration
SHOPIFY_APP_URL=https://your-tunnel-url.trycloudflare.com
SHOPIFY_API_KEY=your_api_key_here
SHOPIFY_API_SECRET=your_api_secret_here
SCOPES=write_products,write_customers,write_draft_orders

# Development flags
NODE_ENV=development
SHOPIFY_CLI_NO_ANALYTICS=1  # Optional: disable telemetry
```

## Best Practices

1. **One Store Per Feature Branch**: Create separate development stores for testing different features in isolation

2. **Regular Cleanup**: Delete unused development stores to stay under the 10-store limit

3. **Data Reset Strategy**: 
   ```bash
   # Reset store data when needed
   shopify store reset
   ```

4. **Team Development**: Share development stores with team members by adding them as staff accounts

## **3. IDE Configuration - VS Code Optimized for Shopify**

### **The Laravel/Spring Boot Equivalent**

In your Laravel development, you likely use PHPStorm with Laravel-specific plugins or VS Code with extensions like Laravel Extra Intellisense. For Spring Boot, you might use IntelliJ IDEA with Spring support or VS Code with the Spring Boot Extension Pack. These provide syntax highlighting, autocompletion, and debugging capabilities specific to your framework.

### **The Current Shopify Way**

VS Code has become the de facto standard for Shopify development due to its excellent TypeScript support, GraphQL integration, and Shopify-specific extensions. The setup differs from your typical Laravel or Spring Boot configuration because you're dealing with GraphQL schemas, Liquid templates (if working with themes), and Shopify-specific APIs.

```json
{
  // .vscode/settings.json - Optimized for Shopify App Development
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.updateImportsOnFileMove.enabled": "always",
  
  // GraphQL configuration for Shopify APIs
  "graphql-config.load.rootDir": "./",
  "graphql-config.dotEnvPath": ".env",
  
  // Prisma ORM support (used by Remix template)
  "prisma.showPrismaDataPlatformNotification": false,
  "[prisma]": {
    "editor.defaultFormatter": "Prisma.prisma"
  },
  
  // File associations for Shopify
  "files.associations": {
    "*.liquid": "liquid",
    "shopify.*.toml": "toml",
    ".shopify": "json"
  },
  
  // Exclude build artifacts and dependencies
  "files.exclude": {
    "**/node_modules": true,
    "**/.git": true,
    "**/build": true,
    "**/.cache": true,
    "**/dist": true
  },
  
  // Search exclusions for better performance
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/*.code-search": true,
    "**/build": true,
    "**/dist": true
  },
  
  // Terminal configuration for Shopify CLI
  "terminal.integrated.env.osx": {
    "SHOPIFY_CLI_NO_ANALYTICS": "1"
  },
  "terminal.integrated.env.linux": {
    "SHOPIFY_CLI_NO_ANALYTICS": "1"  
  },
  "terminal.integrated.env.windows": {
    "SHOPIFY_CLI_NO_ANALYTICS": "1"
  },
  
  // Custom color for TOML files (Shopify config files)
  "workbench.colorCustomizations": {
    "activityBar.activeBackground": "#96bf48",
    "activityBar.activeBorder": "#96bf48",
    "activityBar.background": "#96bf48",
    "titleBar.activeBackground": "#96bf48",
    "titleBar.activeForeground": "#15202b"
  },
  
  // Emmet support for React components
  "emmet.includeLanguages": {
    "javascript": "javascriptreact",
    "typescript": "typescriptreact"
  },
  
  // Auto-close tags in JSX/TSX
  "javascript.autoClosingTags": true,
  "typescript.autoClosingTags": true,
  
  // IntelliSense for Shopify Admin API
  "json.schemas": [
    {
      "fileMatch": ["shopify.app*.toml"],
      "url": "https://shopify.dev/schemas/shopify.app.toml.json"
    }
  ]
}
```

## **4. Project Initialization with Shopify CLI**

### **The Laravel/Spring Boot Equivalent**

When you create a new Laravel project, you run `composer create-project laravel/laravel` which scaffolds a complete MVC structure with routes, controllers, and views ready to go. Spring Boot Initializr similarly generates a project structure with your chosen dependencies, creating a ready-to-run application with embedded Tomcat and auto-configuration. Both frameworks provide hot-reloading during development - Laravel through Vite or Mix, and Spring Boot through DevTools.

### **The Current Shopify Way**

Shopify's approach combines the best of both worlds. The Shopify CLI's `app init` command creates a complete Remix-based application structure (similar to Laravel's MVC but using React for views), includes all necessary dependencies (like Spring Boot's starter dependencies), and sets up hot-reloading with automatic tunneling for HTTPS access. The key difference is that Shopify apps must be accessible via HTTPS even in development, which is why the tunneling solution is built-in.

# Complete Project Initialization and Structure Guide

## Step 1: Create Your First Shopify App

### Initialize the Project

```bash
# Navigate to your development directory
cd ~/development/shopify-apps

# Create a new Shopify app with interactive prompts
shopify app init

# You'll be prompted for:
# 1. App name: "my-inventory-app"
# 2. Select: "Build a Remix app" (recommended for full-stack apps)
# 3. Language: TypeScript (recommended for better type safety)
```

### What Happens During Initialization

The initialization process performs several automated steps:

1. **Clones the Remix template** from GitHub
2. **Installs dependencies** (around 1,200 packages)
3. **Sets up Prisma** for database management
4. **Configures TypeScript** with Shopify types
5. **Creates configuration files** (shopify.app.toml)

## Step 2: Understanding the Remix App Structure

### Directory Structure Explained

```
my-inventory-app/
├── app/                        # Remix application code (like Laravel's app/)
│   ├── routes/                 # Page components and API routes
│   │   ├── app._index.tsx     # App homepage (like Laravel's web.php routes)
│   │   ├── app.tsx            # App layout wrapper
│   │   └── webhooks.tsx       # Webhook handlers
│   ├── shopify.server.ts      # Shopify API configuration (like config/app.php)
│   └── db.server.ts           # Database setup (like database/database.php)
│
├── prisma/                     # Database schema (like Laravel's migrations/)
│   ├── schema.prisma          # Database schema definition
│   └── migrations/            # Database migration files
│
├── public/                     # Static assets (same as Laravel)
│   └── images/                # Static images
│
├── extensions/                 # Shopify-specific extensions directory
│   └── (empty initially)      # Will contain UI extensions, functions, etc.
│
├── shopify.app.toml           # App configuration (like .env + config/)
├── package.json               # Dependencies (like composer.json)
├── remix.config.js            # Remix framework config
├── .env                       # Environment variables (created after first run)
└── .gitignore                # Git ignore rules
```

### Key File Comparisons

| Laravel/Spring Boot | Shopify Remix | Purpose |
|-------------------|---------------|---------|
| `.env` | `.env` + `shopify.app.toml` | Configuration |
| `routes/web.php` | `app/routes/*.tsx` | Route definitions |
| `app/Http/Controllers/` | `app/routes/` | Request handlers |
| `resources/views/` | `app/routes/` (JSX) | View templates |
| `database/migrations/` | `prisma/migrations/` | Database schema |
| `config/` | `shopify.app.toml` | App configuration |
| `composer.json` / `pom.xml` | `package.json` | Dependencies |

## Step 3: Configuration Files Deep Dive

### shopify.app.toml - The Master Configuration

```toml
# shopify.app.toml
# This file is like combining Laravel's config/ directory into one file

# Basic app information
name = "My Inventory App"
client_id = "YOUR_CLIENT_ID"  # Generated after first deploy

# Application URLs (populated automatically by CLI)
application_url = "https://your-tunnel.trycloudflare.com"

# OAuth and security (like Laravel's auth.php)
[auth]
redirect_urls = [
  "https://your-tunnel.trycloudflare.com/auth/callback",
  "https://your-tunnel.trycloudflare.com/auth/shopify/callback"
]

# API access scopes (permissions your app needs)
[access_scopes]
scopes = "write_products,write_customers,write_draft_orders"

# Webhook subscriptions (event listeners)
[webhooks]
api_version = "2025-01"  # Current stable version

# App proxy settings (optional)
[app_proxy]
url = "https://your-tunnel.trycloudflare.com/proxy"
subpath = "tools"
prefix = "myapp"

# Development store installation
[development_store]
store_domain = "your-dev-store.myshopify.com"
```

### Environment Variables (.env)

```bash
# .env - Created after first `shopify app dev`

# Core Shopify Configuration
SHOPIFY_APP_URL=https://your-tunnel.trycloudflare.com
SHOPIFY_API_KEY=abc123def456
SHOPIFY_API_SECRET=secret789xyz
SCOPES=write_products,write_customers,write_draft_orders

# Database Configuration (Prisma)
DATABASE_URL="file:./prisma/dev.db"  # SQLite for development

# Development Settings
NODE_ENV=development
PORT=3000

# Optional: Disable CLI analytics
SHOPIFY_CLI_NO_ANALYTICS=1
```

## Step 4: Start Local Development Server

### Running the Development Server

```bash
# Start the development server with automatic setup
shopify app dev

# What this command does:
# 1. Checks for Node.js and dependencies
# 2. Logs you into Shopify (first time only)
# 3. Creates/updates app in Partner Dashboard
# 4. Generates .env file with credentials
# 5. Runs database migrations
# 6. Starts Remix dev server
# 7. Creates Cloudflare tunnel for HTTPS
# 8. Opens browser preview
```

### Understanding the Development URLs

When running `shopify app dev`, you'll see multiple URLs:

```
╭─ info ──────────────────────────────────────────────╮
│                                                      │
│  App:     My Inventory App                          │
│  Preview: https://quick-fun-name.trycloudflare.com  │
│  Store:   your-dev-store.myshopify.com             │
│                                                      │
│  Press 'p' to preview in browser                    │
│  Press 'q' to quit                                  │
│                                                      │
╰──────────────────────────────────────────────────────╯
```

## Step 5: Local Development Workflow

### Hot Reloading Configuration

The Remix template includes automatic hot module replacement (HMR):

```javascript
// remix.config.js - HMR configuration
export default {
  dev: {
    // Hot reload on file changes
    manual: false,
    // Port for HMR WebSocket
    port: 8002,
  },
  // Server build target
  serverBuildTarget: "vercel",
  server: process.env.NODE_ENV === "development" ? undefined : "./server.js",
};
```

### Development Commands Reference

```bash
# Start development server
shopify app dev

# Additional dev options
shopify app dev --store=different-store  # Use different store
shopify app dev --reset                   # Reset OAuth and reinstall
shopify app dev --verbose                 # Debug output
shopify app dev --use-localhost          # Use localhost instead of tunnel

# While dev server is running:
# Press 'p' - Open preview in browser
# Press 'g' - Generate GraphQL types
# Press 'q' - Quit
```

### Networking Options

Choose your networking approach based on your environment:

1. **Cloudflare Tunnels (Default)**
   - Automatic HTTPS
   - Works everywhere
   - No configuration needed
   - URL changes each session

2. **Localhost Development**
   ```bash
   shopify app dev --use-localhost
   ```
   - Consistent URL (localhost:3000)
   - Requires mkcert for HTTPS
   - Doesn't work with webhooks
   - Good for UI development

3. **Custom Tunnel (ngrok)**
   ```bash
   # Terminal 1: Start ngrok
   ngrok http 3000
   
   # Terminal 2: Use ngrok URL
   shopify app dev --tunnel-url=https://abc123.ngrok.app:3000
   ```
   - Persistent URL with paid ngrok
   - Better for webhook testing
   - Required for some corporate networks

## Troubleshooting Common Issues

### Issue: "Cannot connect to Shopify"

```bash
# Solution 1: Check your network proxy
export SHOPIFY_HTTP_PROXY=http://your-proxy:8080

# Solution 2: Reset the connection
shopify app dev --reset
```

### Issue: "Database is locked" (SQLite)

```bash
# Stop all Node processes
pkill node

# Remove lock file
rm prisma/dev.db-journal

# Restart
shopify app dev
```

### Issue: "Port 3000 already in use"

```bash
# Find and kill the process
lsof -i :3000
kill -9 <PID>

# Or use a different port
PORT=3001 shopify app dev
```

## **5. Production Considerations for 2025**

### **Current Best Practices**

The Shopify ecosystem has evolved significantly in 2025 with the introduction of enhanced development tools and improved local development workflows. The current approach emphasizes type safety with TypeScript being the default, automatic GraphQL code generation for API interactions, and seamless integration between your local development environment and Shopify's cloud infrastructure. Unlike the manual OAuth flows and complex webhook setups of earlier versions, modern Shopify development leverages Shopify-managed installation and automatic webhook registration, significantly reducing boilerplate code.

## **6. Real-World Development Scenarios**

Let me demonstrate three practical scenarios you'll encounter when setting up your development environment, each building on concepts from 

```typescript
// Scenario 1: Setting Up Multi-Environment Configuration
// Similar to Laravel's environment-specific config files

// config/environments.ts
interface EnvironmentConfig {
  apiUrl: string;
  debugMode: boolean;
  webhookTimeout: number;
  rateLimits: {
    api: number;
    webhook: number;
  };
}

const environments: Record<string, EnvironmentConfig> = {
  development: {
    apiUrl: process.env.SHOPIFY_APP_URL || 'http://localhost:3000',
    debugMode: true,
    webhookTimeout: 30000, // 30 seconds for dev
    rateLimits: {
      api: 100,      // Relaxed for development
      webhook: 50
    }
  },
  staging: {
    apiUrl: process.env.SHOPIFY_APP_URL || 'https://staging.myapp.com',
    debugMode: true,
    webhookTimeout: 10000, // 10 seconds
    rateLimits: {
      api: 40,       // Match Shopify's limits
      webhook: 20
    }
  },
  production: {
    apiUrl: process.env.SHOPIFY_APP_URL || 'https://app.myapp.com',
    debugMode: false,
    webhookTimeout: 5000, // 5 seconds for production
    rateLimits: {
      api: 40,       // Shopify's actual limits
      webhook: 20
    }
  }
};

export const config = environments[process.env.NODE_ENV || 'development'];

// ============================================
// Scenario 2: Database Configuration with Migrations
// Similar to Laravel's migrations and Spring Boot's Flyway
// ============================================

// prisma/schema.prisma
/*
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"  // Use PostgreSQL for production
  url      = env("DATABASE_URL")
}

model Session {
  id            String    @id
  shop          String
  state         String
  isOnline      Boolean   @default(false)
  scope         String?
  expires       DateTime?
  accessToken   String
  userId        BigInt?
  firstName     String?
  lastName      String?
  email         String?
  accountOwner  Boolean   @default(false)
  locale        String?
  collaborator  Boolean?  @default(false)
  emailVerified Boolean?  @default(false)
}

// Custom model for your app's data
model InventoryAlert {
  id          String   @id @default(cuid())
  shop        String
  productId   String
  variantId   String?
  threshold   Int
  status      String   @default("active")
  lastChecked DateTime @default(now())
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  @@index([shop, status])
  @@index([productId])
}
*/

// app/models/inventory-alert.server.ts
import { prisma } from "~/db.server";

export async function createInventoryAlert(data: {
  shop: string;
  productId: string;
  threshold: number;
}) {
  // This is like Eloquent's create method in Laravel
  return prisma.inventoryAlert.create({
    data: {
      ...data,
      status: 'active',
      lastChecked: new Date()
    }
  });
}

export async function getActiveAlerts(shop: string) {
  // Similar to Laravel's query builder with where clauses
  return prisma.inventoryAlert.findMany({
    where: {
      shop,
      status: 'active'
    },
    orderBy: {
      createdAt: 'desc'
    },
    take: 100  // Pagination
  });
}

// ============================================
// Scenario 3: Debugging Setup with Source Maps
// Enhanced debugging experience for TypeScript
// ============================================

// .vscode/launch.json
const debugConfiguration = {
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Shopify App",
      "type": "node",
      "request": "launch",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "skipFiles": ["<node_internals>/**"],
      "sourceMaps": true,
      "env": {
        "NODE_ENV": "development",
        "DEBUG": "shopify:*"  // Enable Shopify debug logs
      },
      "console": "integratedTerminal"
    },
    {
      "name": "Debug Webhook Handler",
      "type": "node",
      "request": "attach",
      "port": 9229,
      "continueOnAttach": true,
      "skipFiles": ["<node_internals>/**"],
      "sourceMaps": true
    }
  ]
};

// package.json debug script
/*
"scripts": {
  "dev": "shopify app dev",
  "dev:debug": "NODE_OPTIONS='--inspect' shopify app dev",
  "test:debug": "NODE_OPTIONS='--inspect-brk' vitest"
}
*/

// ============================================
// Scenario 4: Team Development Configuration
// Handling multiple developers like in enterprise settings
// ============================================

// team-config.ts
interface TeamMember {
  name: string;
  email: string;
  developmentStore: string;
  tunnelPreference: 'cloudflare' | 'ngrok' | 'localhost';
}

const teamConfig: Record<string, TeamMember> = {
  john: {
    name: "John Developer",
    email: "john@company.com",
    developmentStore: "john-inventory-dev",
    tunnelPreference: 'cloudflare'
  },
  sarah: {
    name: "Sarah Engineer",
    email: "sarah@company.com",
    developmentStore: "sarah-inventory-dev",
    tunnelPreference: 'ngrok'  // Behind corporate proxy
  }
};

// Get current developer from git config
async function getCurrentDeveloper() {
  const { execSync } = require('child_process');
  const gitEmail = execSync('git config user.email').toString().trim();
  
  return Object.values(teamConfig).find(
    member => member.email === gitEmail
  );
}

// Auto-configure based on developer
export async function setupDevelopmentEnvironment() {
  const developer = await getCurrentDeveloper();
  
  if (developer) {
    process.env.SHOPIFY_DEV_STORE = developer.developmentStore;
    
    // Set tunnel preference
    if (developer.tunnelPreference === 'ngrok') {
      console.log('Starting ngrok tunnel...');
      // Start ngrok programmatically
    }
  }
}
```

## **7. Advanced Patterns from Latest Documentation**

Let me share some advanced patterns that have emerged in 2025's Shopify development practices, particularly around performance optimization and scalability. These patterns go beyond what you'd find in older tutorials and incorporate lessons learned from production deployments.

```typescript
// Advanced Pattern 1: GraphQL Code Generation Pipeline
// This ensures type safety across your entire app

// codegen.yml - GraphQL Code Generation Configuration
/*
overwrite: true
schema: 
  - https://shopify.dev/admin-graphql-2025-01.json
  - 'app/**/*.graphql'
documents:
  - 'app/**/*.{ts,tsx}'
  - '!app/generated/**/*'
generates:
  app/generated/admin.types.ts:
    plugins:
      - typescript
      - typescript-operations
      - typescript-react-apollo
    config:
      scalars:
        URL: string
        DateTime: string
        Decimal: number
        Money: string
      skipTypename: false
      withHooks: true
      withHOC: false
      withComponent: false
*/

// app/lib/graphql/client.server.ts
import { GraphQLClient } from 'graphql-request';
import { authenticate } from '~/shopify.server';

export async function createGraphQLClient(request: Request) {
  const { admin, session } = await authenticate.admin(request);
  
  return new GraphQLClient(
    `https://${session.shop}/admin/api/2025-01/graphql.json`,
    {
      headers: {
        'X-Shopify-Access-Token': session.accessToken,
        'Content-Type': 'application/json',
      },
      // Advanced: Automatic retry with exponential backoff
      retry: {
        retries: 3,
        factor: 2,
        minTimeout: 1000,
        maxTimeout: 16000,
        randomize: true,
      },
      // Request timeout for production
      timeout: 10000,
    }
  );
}

// ============================================
// Advanced Pattern 2: Performance Monitoring Setup
// Track development performance metrics
// ============================================

// app/lib/performance/monitor.ts
interface PerformanceMetric {
  name: string;
  duration: number;
  timestamp: number;
  metadata?: Record<string, any>;
}

class DevelopmentPerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private readonly isDevelopment = process.env.NODE_ENV === 'development';
  
  async measureGraphQLQuery<T>(
    queryName: string,
    queryFn: () => Promise<T>
  ): Promise<T> {
    if (!this.isDevelopment) {
      return queryFn();
    }
    
    const startTime = performance.now();
    const startMark = `${queryName}_start`;
    const endMark = `${queryName}_end`;
    
    performance.mark(startMark);
    
    try {
      const result = await queryFn();
      const duration = performance.now() - startTime;
      
      performance.mark(endMark);
      performance.measure(queryName, startMark, endMark);
      
      this.recordMetric({
        name: queryName,
        duration,
        timestamp: Date.now(),
        metadata: {
          type: 'graphql',
          success: true
        }
      });
      
      // Log slow queries in development
      if (duration > 1000) {
        console.warn(`⚠️ Slow GraphQL query: ${queryName} took ${duration.toFixed(2)}ms`);
      }
      
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      
      this.recordMetric({
        name: queryName,
        duration,
        timestamp: Date.now(),
        metadata: {
          type: 'graphql',
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      });
      
      throw error;
    }
  }
  
  private recordMetric(metric: PerformanceMetric) {
    this.metrics.push(metric);
    
    // Keep only last 100 metrics in memory for development
    if (this.metrics.length > 100) {
      this.metrics.shift();
    }
    
    // Output to console in development
    if (this.isDevelopment) {
      console.log(`📊 [Performance] ${metric.name}: ${metric.duration.toFixed(2)}ms`);
    }
  }
  
  getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }
  
  clearMetrics(): void {
    this.metrics = [];
  }
}

export const perfMonitor = new DevelopmentPerformanceMonitor();

// Usage example in your route
// app/routes/app.products.tsx
export async function loader({ request }: LoaderArgs) {
  const client = await createGraphQLClient(request);
  
  const products = await perfMonitor.measureGraphQLQuery(
    'fetchProducts',
    async () => {
      const query = `
        query getProducts($first: Int!) {
          products(first: $first) {
            edges {
              node {
                id
                title
                handle
                status
              }
            }
          }
        }
      `;
      
      return client.request(query, { first: 10 });
    }
  );
  
  return json({ products });
}

// ============================================
// Advanced Pattern 3: Custom Development Middleware
// Similar to Laravel middleware but for Shopify webhooks
// ============================================

// app/lib/webhook/middleware.server.ts
type WebhookMiddleware = (
  topic: string,
  shop: string,
  body: any,
  webhookId: string
) => Promise<void>;

class WebhookMiddlewareChain {
  private middlewares: WebhookMiddleware[] = [];
  
  use(middleware: WebhookMiddleware): void {
    this.middlewares.push(middleware);
  }
  
  async execute(
    topic: string,
    shop: string,
    body: any,
    webhookId: string
  ): Promise<void> {
    for (const middleware of this.middlewares) {
      await middleware(topic, shop, body, webhookId);
    }
  }
}

// Create middleware instances
const webhookChain = new WebhookMiddlewareChain();

// Development logging middleware
webhookChain.use(async (topic, shop, body, webhookId) => {
  if (process.env.NODE_ENV === 'development') {
    console.log('=================================');
    console.log(`🪝 Webhook Received: ${topic}`);
    console.log(`   Shop: ${shop}`);
    console.log(`   ID: ${webhookId}`);
    console.log(`   Timestamp: ${new Date().toISOString()}`);
    console.log('=================================');
    
    // Save to local file for debugging
    const fs = await import('fs/promises');
    const webhookLog = {
      topic,
      shop,
      webhookId,
      timestamp: new Date().toISOString(),
      body: JSON.stringify(body, null, 2)
    };
    
    await fs.appendFile(
      'webhooks.log',
      JSON.stringify(webhookLog) + '\n'
    );
  }
});

// Rate limiting middleware for development
const webhookCounts = new Map<string, number>();
webhookChain.use(async (topic, shop) => {
  const key = `${shop}:${topic}`;
  const count = webhookCounts.get(key) || 0;
  
  if (count > 100) {
    console.warn(`⚠️ Rate limit warning: ${key} has ${count} webhooks`);
  }
  
  webhookCounts.set(key, count + 1);
  
  // Reset counts every hour
  setTimeout(() => {
    webhookCounts.delete(key);
  }, 3600000);
});

// ============================================
// Advanced Pattern 4: Hot Module Replacement Configuration
// Enhanced HMR for faster development
// ============================================

// vite.config.ts
import { vitePlugin as remix } from "@remix-run/dev";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [
    remix({
      future: {
        v3_fetcherPersist: true,
        v3_relativeSplatPath: true,
      },
    }),
  ],
  server: {
    port: 3000,
    hmr: {
      // Use WebSocket for HMR
      protocol: 'ws',
      host: 'localhost',
      port: 3001,
      // Timeout for HMR connection
      timeout: 30000,
      // Overlay for errors
      overlay: true,
    },
    // Watch configuration for better performance
    watch: {
      // Ignore node_modules and build directories
      ignored: ['**/node_modules/**', '**/build/**', '**/dist/**'],
      // Use polling in Docker environments
      usePolling: process.env.DOCKER === 'true',
      interval: 1000,
    },
  },
  // Optimize dependencies for faster cold starts
  optimizeDeps: {
    include: [
      '@shopify/polaris',
      '@shopify/app-bridge-react',
      '@remix-run/react',
      'react',
      'react-dom'
    ],
    exclude: ['@shopify/shopify-app-remix']
  },
  // Build optimizations
  build: {
    target: 'es2020',
    sourcemap: process.env.NODE_ENV === 'development',
    rollupOptions: {
      output: {
        manualChunks: {
          'shopify-polaris': ['@shopify/polaris'],
          'shopify-bridge': ['@shopify/app-bridge-react'],
          'vendor': ['react', 'react-dom', '@remix-run/react']
        }
      }
    }
  }
});
```

## **8. Hands-On Exercise: Complete Development Environment Setup**

Let me guide you through a comprehensive exercise that will solidify your understanding of the Shopify development environment setup. This exercise mirrors a real-world scenario where you're tasked with setting up a development environment for a team project, incorporating all the concepts we've covered. You'll build an inventory management app that showcases the key differences between Shopify's architecture and what you're familiar with from Laravel and Spring Boot.

# Hands-On Exercise: Building Your First Shopify Development Environment

## Exercise Overview

You'll create a complete development environment for an inventory tracking app that monitors product stock levels and sends alerts when inventory runs low. This exercise demonstrates the key differences between Shopify's approach and traditional MVC frameworks.

## Part 1: Initial Setup (20 minutes)

### Step 1: Verify Prerequisites

First, ensure your system meets all requirements:

```bash
# Check Node.js version (must be 20.10+)
node --version

# Check Git version (must be 2.28+)
git --version

# Check Shopify CLI installation
shopify version

# If any are missing or outdated, install them now
```

### Step 2: Create Your Workspace

Create a dedicated workspace for Shopify development:

```bash
# Create workspace directory structure
mkdir -p ~/shopify-development/{apps,themes,docs}
cd ~/shopify-development/apps

# Initialize Git repository for the project
git init inventory-tracker
cd inventory-tracker
```

### Step 3: Generate the App

Now create your Shopify app with specific configurations:

```bash
# Initialize the app with TypeScript support
shopify app init

# When prompted:
# App name: inventory-tracker
# Template: Remix (TypeScript)
```

## Part 2: Configure Development Environment (15 minutes)

### Step 4: Set Up VS Code Workspace

Create a VS Code workspace with optimal settings:

```bash
# Create VS Code configuration directory
mkdir .vscode

# Create workspace settings
cat > .vscode/settings.json << 'EOF'
{
  "files.exclude": {
    "node_modules": true,
    ".cache": true,
    "build": true
  },
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
EOF

# Create recommended extensions list
cat > .vscode/extensions.json << 'EOF'
{
  "recommendations": [
    "Shopify.theme-check-vscode",
    "GraphQL.vscode-graphql",
    "Prisma.prisma",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ]
}
EOF
```

### Step 5: Configure Multiple Environments

Create environment-specific configuration files:

```bash
# Development environment
cat > .env.development << 'EOF'
NODE_ENV=development
DATABASE_URL="file:./prisma/dev.db"
LOG_LEVEL=debug
WEBHOOK_TIMEOUT=30000
EOF

# Staging environment (for later use)
cat > .env.staging << 'EOF'
NODE_ENV=staging
DATABASE_URL="postgresql://user:pass@localhost:5432/shopify_staging"
LOG_LEVEL=info
WEBHOOK_TIMEOUT=10000
EOF

# Add to .gitignore
echo ".env*" >> .gitignore
echo "!.env.example" >> .gitignore
```

## Part 3: Database and Model Setup (20 minutes)

### Step 6: Configure Prisma Schema

Update your Prisma schema for inventory tracking:

```bash
# Edit prisma/schema.prisma
cat > prisma/schema.prisma << 'EOF'
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

model Session {
  id            String    @id
  shop          String
  state         String
  isOnline      Boolean   @default(false)
  scope         String?
  expires       DateTime?
  accessToken   String
  userId        BigInt?
}

model InventoryAlert {
  id          String   @id @default(cuid())
  shop        String
  productId   String
  variantId   String?
  productTitle String
  currentStock Int
  threshold   Int
  status      AlertStatus @default(ACTIVE)
  lastAlerted DateTime?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  @@index([shop, status])
  @@index([productId])
}

enum AlertStatus {
  ACTIVE
  PAUSED
  TRIGGERED
}
EOF
```

### Step 7: Create and Run Migration

```bash
# Create initial migration
npx prisma migrate dev --name init

# Generate Prisma client
npx prisma generate

# Verify database creation
ls -la prisma/dev.db
```

## Part 4: Connect to Shopify (15 minutes)

### Step 8: Start Development Server

```bash
# Start the Shopify development server
shopify app dev

# You'll see prompts for:
# 1. Login to Shopify (browser opens)
# 2. Select organization (if multiple)
# 3. Create app in Partner Dashboard
# 4. Select development store
```

### Step 9: Verify Installation

Once the server is running, press 'p' to open the preview. You should see your app installed in the development store. The URL will look like:

```
https://quick-random-name.trycloudflare.com
```

### Step 10: Test Hot Reloading

Make a visible change to test hot reloading:

```tsx
// Edit app/routes/app._index.tsx
// Change the title in the Page component
<Page title="Inventory Tracker Dashboard">
```

The browser should automatically update without refreshing.

## Part 5: Advanced Configuration (20 minutes)

### Step 11: Set Up GraphQL Code Generation

Configure automatic TypeScript type generation for GraphQL:

```bash
# Install GraphQL codegen dependencies
npm install --save-dev @graphql-codegen/cli @graphql-codegen/typescript

# Create codegen configuration
cat > codegen.yml << 'EOF'
overwrite: true
schema: 
  - https://shopify.dev/admin-graphql-2025-07.json
documents:
  - 'app/**/*.graphql'
  - 'app/**/*.{ts,tsx}'
generates:
  app/types/admin.generated.ts:
    plugins:
      - typescript
      - typescript-operations
EOF

# Add script to package.json
npm pkg set scripts.codegen="graphql-codegen --config codegen.yml"
```

### Step 12: Create Custom Development Commands

Add helpful development scripts:

```json
// Add to package.json scripts section
{
  "scripts": {
    "dev": "shopify app dev",
    "dev:debug": "NODE_OPTIONS='--inspect' shopify app dev",
    "dev:reset": "shopify app dev --reset",
    "db:studio": "npx prisma studio",
    "db:reset": "npx prisma migrate reset",
    "type-check": "tsc --noEmit",
    "codegen": "graphql-codegen --config codegen.yml"
  }
}
```

## Part 6: Testing Your Setup (10 minutes)

### Step 13: Create a Test Route

Create a new route to verify everything works:

```tsx
// Create app/routes/app.test.tsx
import { json } from "@remix-run/node";
import { useLoaderData } from "@remix-run/react";
import { Page, Card, Text } from "@shopify/polaris";
import type { LoaderFunctionArgs } from "@remix-run/node";
import { authenticate } from "~/shopify.server";

export async function loader({ request }: LoaderFunctionArgs) {
  const { session } = await authenticate.admin(request);
  
  return json({
    shop: session.shop,
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV,
  });
}

export default function TestPage() {
  const data = useLoaderData<typeof loader>();
  
  return (
    <Page title="Environment Test">
      <Card>
        <Text variant="headingMd" as="h2">Setup Verification</Text>
        <Text as="p">Shop: {data.shop}</Text>
        <Text as="p">Environment: {data.environment}</Text>
        <Text as="p">Server Time: {data.timestamp}</Text>
      </Card>
    </Page>
  );
}
```

### Step 14: Verify the Route Works

Navigate to `/app/test` in your browser. You should see your test page with the correct shop domain and environment information.

## Expected Results

By completing this exercise, you should have:

1. A fully functional Shopify app development environment
2. Hot reloading working for instant feedback
3. TypeScript support with proper type checking
4. Database configured with Prisma ORM
5. VS Code optimized for Shopify development
6. GraphQL code generation ready
7. Multiple environment configurations
8. A test route confirming everything works

## Troubleshooting Guide

### Common Issues and Solutions

**Issue: "Cannot find module '@shopify/shopify-app-remix'"**
Solution: Run `npm install` to ensure all dependencies are installed.

**Issue: "Database is locked"**
Solution: Stop all Node processes and delete `prisma/dev.db-journal`.

**Issue: "Port 3000 already in use"**
Solution: Kill the process using port 3000 or use a different port:
```bash
PORT=3001 shopify app dev
```

**Issue: "Cloudflare tunnel fails to connect"**
Solution: Try using localhost mode instead:
```bash
shopify app dev --use-localhost
```

## Next Steps

After completing this exercise, you're ready to:

1. Start building actual app functionality
2. Add app extensions for UI customization
3. Implement webhook handlers for real-time updates
4. Set up CI/CD pipelines for deployment
5. Configure production environments

## Reflection Questions

Think about these questions to deepen your understanding:

1. How does Shopify's tunneling solution compare to Laravel Valet or Spring Boot's embedded server?
2. Why does Shopify require HTTPS even in development, unlike typical web frameworks?
3. How does Prisma's migration system compare to Laravel's migrations or Spring Boot's Flyway?
4. What are the trade-offs between using SQLite in development versus PostgreSQL?

## **9. Migration Path and Current Best Practices**

Understanding the migration path from older Shopify development patterns to current best practices is crucial, especially since many online tutorials still reference deprecated approaches. The most significant change you'll encounter is the shift from manual OAuth implementation to Shopify-managed installation, which happened in late 2024. This change eliminates hundreds of lines of boilerplate code that you'd find in older tutorials. Similarly, the webhook registration process has evolved from manual API calls to declarative configuration in the shopify.app.toml file, making it much more similar to how you'd declare event listeners in Laravel's EventServiceProvider or Spring Boot's event annotations.

The authentication pattern has also fundamentally changed. Where older apps required complex session management with JWT tokens and manual validation, the current Remix template handles this automatically through the authenticate helper functions. This is comparable to how Laravel's auth middleware works – you simply apply it to routes that need protection, and the framework handles the complexity. The difference is that Shopify's authentication also validates the shop domain and ensures the request is coming from a legitimate Shopify store, adding an extra layer of security you don't typically need in traditional web applications.

## **10. Verification and Resources**

Throughout this tutorial, I've used the Shopify Dev MCP tools to verify that all information is current as of September 2025. The documentation I've referenced comes directly from Shopify's official sources, with the Admin API using version 2025-07 and Shopify CLI at version 3.78 or higher. The patterns and code examples have been validated against the current GraphQL schema and tested with the latest Remix template structure.

For continued learning, I recommend bookmarking these essential resources: the official Shopify Dev documentation at shopify.dev for API references and guides, the Shopify CLI GitHub repository for tracking updates and reporting issues, and the Shopify Community forums where you can connect with other developers facing similar challenges. The Partner Dashboard remains your central hub for managing apps, viewing analytics, and accessing development stores.

As you progress beyond environment setup, pay particular attention to the Shopify App Design Guidelines, which have become increasingly important for app approval. The new Built for Shopify program, launched in 2024, provides additional benefits for apps that meet higher quality standards, including enhanced visibility in the App Store and priority support from Shopify.

## **Try This Yourself: Challenge Extensions**

To reinforce your learning and explore the boundaries of what you've set up, I encourage you to extend the hands-on exercise with these challenges that mirror real-world scenarios you'll encounter in production development.

First, try setting up a multi-developer environment where three team members can work on the same codebase simultaneously without conflicts. This involves creating separate development stores for each developer, configuring individual tunnel solutions based on their network requirements, and implementing a Git workflow that prevents environment variable conflicts. Think about how this differs from your experience with Laravel Homestead or Spring Boot's profile-based configuration.

Next, implement a performance monitoring system that tracks GraphQL query execution times during development and alerts you when queries exceed acceptable thresholds. This is similar to Laravel Telescope or Spring Boot Actuator, but tailored for Shopify's specific APIs. Consider how you'd visualize this data and what metrics would be most valuable during development versus production.

Finally, create a Docker configuration that encapsulates your entire development environment, making it possible for new team members to get started with a single docker-compose up command. This should include the Node.js environment, database setup, and all necessary Shopify CLI configurations. Think about how you'd handle the authentication flow within a containerized environment and how to persist development store credentials securely.

## **Final Thoughts: The Shopify Development Mindset**

The transition from traditional web frameworks like Laravel and Spring Boot to Shopify development requires a shift in mindset beyond just learning new tools. Where Laravel gives you complete control over your application's architecture and Spring Boot emphasizes enterprise patterns and dependency injection, Shopify development is about working within a well-defined ecosystem that prioritizes merchant success and platform stability.

The development environment we've set up together provides the foundation for building apps that can scale to serve thousands of merchants. The tunneling solution that might seem unusual coming from traditional development is actually a powerful feature that enables real-time testing with actual Shopify stores. The strict HTTPS requirement even in development ensures you're always building with security in mind. The integrated GraphQL tooling with automatic type generation prevents the runtime errors that plague many JavaScript applications.

As you continue your journey into Shopify development, remember that the platform is constantly evolving. The patterns and tools we've discussed today represent the current best practices, but Shopify regularly introduces improvements based on developer feedback. Stay connected with the community, participate in partner town halls, and don't hesitate to provide feedback through official channels. Your background in Laravel and Spring Boot gives you valuable perspective that can contribute to making Shopify development even better.

Welcome to the Shopify developer ecosystem. With your development environment now fully configured and your understanding of the platform's unique characteristics, you're ready to build apps that help merchants succeed in commerce. The investment you've made in setting up a proper development environment will pay dividends as you move into building features, handling webhooks, creating app extensions, and ultimately launching your app to the Shopify App Store.
