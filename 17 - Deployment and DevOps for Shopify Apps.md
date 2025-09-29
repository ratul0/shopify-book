# Deployment and DevOps for Shopify Apps

Based on the latest Shopify documentation as of September 2025, I'll teach you deployment and DevOps for Shopify apps, drawing parallels to your Laravel, Spring Boot, and Angular experience. Let me start by verifying the current best practices and patterns.

## 1. Current Shopify Documentation Check

According to Shopify's documentation as of September 2025, the deployment landscape has evolved significantly. The current approach emphasizes:

- **Simplified deployment model** with app versions (introduced 2024)
- **CLI-first deployment strategy** using `shopify app deploy`
- **Multi-environment configuration** through TOML files
- **Integrated CI/CD** with GitHub Actions and CircleCI support
- **Docker-first deployment** with included Dockerfile templates
- **Environment-based secrets management** similar to Laravel's `.env` approach

## 2. The Laravel/Spring Boot Equivalent

Coming from Laravel and Spring Boot, you're already familiar with these concepts:

**Laravel Parallels:**
- `.env` files → Shopify uses similar environment variables
- `php artisan migrate` → Prisma migrations with `npm run setup`
- Laravel Forge/Vapor → Fly.io, Render, Heroku for Shopify
- `composer.json` → `package.json` with lockfiles
- Laravel Mix/Vite → Vite is already configured in Shopify templates

**Spring Boot Parallels:**
- Application profiles → Shopify's multi-environment TOML files
- Maven/Gradle builds → npm/yarn/pnpm build processes
- Spring Boot Actuator → Custom health endpoints + monitoring
- Flyway/Liquibase → Prisma for database migrations
- JAR deployment → Docker container deployment

## 3. The Current Shopify Way - Complete Architecture

Let me walk you through the modern Shopify deployment architecture:

### Environment Configuration Strategy

Shopify now uses a multi-file approach for environment management. Unlike Laravel's single `.env` file or Spring Boot's `application-{profile}.yml`, Shopify uses:

```toml
# shopify.app.development.toml
name = "my-app-dev"
client_id = "dev_client_id"
application_url = "https://localhost:3000"
embedded = true

[build]
dev_store_url = "dev-store.myshopify.com"

[auth]
redirect_urls = ["https://localhost:3000/auth/callback"]

[webhooks]
api_version = "2025-01"
```

```toml
# shopify.app.production.toml
name = "my-app"
client_id = "prod_client_id"
application_url = "https://my-app.fly.dev"
embedded = true

[build]
include_config_on_deploy = true

[auth]
redirect_urls = ["https://my-app.fly.dev/auth/callback"]
```

The system works by selecting configurations through the CLI, similar to Spring Boot profiles but more explicit:

```bash
# Switch between environments
shopify app config use development
shopify app config use production

# Deploy with specific config
shopify app deploy --config production
```

### Secret Management Architecture

Unlike Laravel's straightforward `.env` approach, Shopify requires a layered security model:

```javascript
// server.js - Production secrets handling
export default {
  async fetch(request, env, ctx) {
    // Environment variables are injected by the hosting platform
    const shopifyApp = shopifyAppFactory({
      apiKey: env.SHOPIFY_API_KEY,        // Public - can be in repository
      apiSecretKey: env.SHOPIFY_API_SECRET, // Secret - never commit
      scopes: env.SCOPES?.split(','),
      hostName: env.SHOPIFY_APP_URL,
      
      // Session storage with encryption
      sessionStorage: new PrismaSessionStorage(prisma, {
        tableName: 'sessions',
        // Encrypt session data at rest
        encryptionKey: env.SESSION_ENCRYPTION_KEY
      }),
    });
    
    return shopifyApp.fetch(request, env, ctx);
  }
};
```

For different providers, secret management varies:

```yaml
# GitHub Actions secrets
env:
  SHOPIFY_CLI_PARTNERS_TOKEN: ${{ secrets.SHOPIFY_CLI_PARTNERS_TOKEN }}
  SHOPIFY_API_SECRET: ${{ secrets.SHOPIFY_API_SECRET }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

```bash
# Fly.io secrets
fly secrets set SHOPIFY_API_SECRET=your_secret
fly secrets set DATABASE_URL=postgresql://...
```

### Database Migration Strategy

Shopify apps use Prisma, which provides a more structured approach than Laravel's migrations:

```javascript
// prisma/schema.prisma
datasource db {
  provider = "postgresql" // Switch from SQLite for production
  url      = env("DATABASE_URL")
}

model Session {
  id            String    @id
  shop          String
  state         String
  isOnline      Boolean   @default(false)
  scope         String?
  expires       DateTime?
  accessToken   String    @db.Text // Encrypted in production
  userId        BigInt?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt
}
```

Migration workflow for production:

```javascript
// package.json
{
  "scripts": {
    "setup": "prisma generate && prisma migrate deploy",
    "dev:migrate": "prisma migrate dev",
    "prod:migrate": "prisma migrate deploy --schema ./prisma/schema.production.prisma"
  }
}
```

Zero-downtime migration strategy:

```javascript
// deployment/migrate.js
async function performMigration() {
  // Step 1: Add new columns as nullable
  await prisma.$executeRaw`
    ALTER TABLE products 
    ADD COLUMN IF NOT EXISTS new_field VARCHAR(255)`;
  
  // Step 2: Backfill data in batches
  const batchSize = 1000;
  let offset = 0;
  while (true) {
    const records = await prisma.products.findMany({
      skip: offset,
      take: batchSize,
      where: { new_field: null }
    });
    
    if (records.length === 0) break;
    
    await prisma.products.updateMany({
      where: { id: { in: records.map(r => r.id) }},
      data: { new_field: calculateValue() }
    });
    
    offset += batchSize;
    await new Promise(resolve => setTimeout(resolve, 100)); // Rate limiting
  }
  
  // Step 3: Make column non-nullable after deployment
  // This happens in a separate deployment
}
```

## 4. Complete Production Deployment Example

Let me show you a complete production-ready setup:

### Project Structure
```
my-shopify-app/
├── .github/
│   └── workflows/
│       ├── deploy-production.yml
│       └── deploy-staging.yml
├── app/
│   ├── routes/
│   ├── models/
│   └── services/
├── prisma/
│   ├── schema.prisma
│   └── migrations/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── pre-deploy.js
│   └── health-check.js
├── shopify.app.development.toml
├── shopify.app.staging.toml
├── shopify.app.production.toml
└── package.json
```

### Complete Dockerfile with optimizations:

```dockerfile
# Multi-stage build for smaller production images
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Build stage
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

WORKDIR /app

# Copy only necessary files
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/prisma ./prisma

# Generate Prisma client
RUN npx prisma generate

EXPOSE 3000

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]
CMD ["npm", "run", "docker:start"]
```

### Complete CI/CD Pipeline:

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

env:
  FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run linter
        run: npm run lint

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Fly.io
        uses: superfly/flyctl-actions/setup-flyctl@master
      
      - name: Deploy app to Fly.io
        run: flyctl deploy --remote-only
        
      - name: Run database migrations
        run: |
          flyctl ssh console -C "npm run setup"
      
      - name: Deploy Shopify configuration
        env:
          SHOPIFY_CLI_PARTNERS_TOKEN: ${{ secrets.SHOPIFY_CLI_PARTNERS_TOKEN }}
          SHOPIFY_API_KEY: ${{ secrets.PROD_SHOPIFY_API_KEY }}
        run: |
          npm install -g @shopify/cli@latest
          shopify app deploy --config production -f \
            --source-control-url "${{ github.server_url }}/${{ github.repository }}/commit/${{ github.sha }}"
      
      - name: Health check
        run: |
          curl --fail https://my-app.fly.dev/api/health || exit 1
      
      - name: Notify deployment
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Monitoring and Health Endpoints:

```javascript
// app/routes/api.health.jsx
export async function loader({ context }) {
  try {
    // Check database connection
    await context.db.session.findFirst();
    
    // Check Shopify API connectivity
    const { admin } = await authenticate.admin(request);
    await admin.rest.Shop.current();
    
    // Check Redis if used
    if (context.redis) {
      await context.redis.ping();
    }
    
    return json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: process.env.APP_VERSION || 'unknown',
      checks: {
        database: 'ok',
        shopify: 'ok',
        redis: context.redis ? 'ok' : 'not configured'
      }
    });
  } catch (error) {
    return json({
      status: 'unhealthy',
      error: error.message
    }, { status: 503 });
  }
}
```

## 5. Hosting Provider Comparison & Setup

Based on current documentation and community practices:

### Fly.io (Recommended for most apps)
```toml
# fly.toml
app = "my-shopify-app"
primary_region = "iad" # US East for lowest Shopify latency

[env]
  PORT = "3000"
  NODE_ENV = "production"

[experimental]
  allowed_public_ports = []
  auto_rollback = true

[[services]]
  http_checks = []
  internal_port = 3000
  protocol = "tcp"
  
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

Setup commands:
```bash
fly launch
fly secrets set SHOPIFY_API_SECRET=xxx DATABASE_URL=xxx
fly deploy
```

### Render (Simplest setup)
```yaml
# render.yaml
services:
  - type: web
    name: shopify-app
    env: docker
    region: oregon
    plan: standard
    healthCheckPath: /api/health
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: shopifydb
          property: connectionString

databases:
  - name: shopifydb
    plan: standard
    region: oregon
```

### Heroku (Traditional but expensive)
```json
// app.json
{
  "name": "Shopify App",
  "scripts": {
    "postdeploy": "npm run setup"
  },
  "env": {
    "NODE_ENV": "production",
    "NPM_CONFIG_PRODUCTION": "false"
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "standard-1x"
    }
  },
  "addons": ["heroku-postgresql:standard-0"]
}
```

## 6. Advanced Production Patterns

### Blue-Green Deployment Strategy:

```javascript
// scripts/blue-green-deploy.js
async function blueGreenDeploy() {
  // Deploy to green environment
  await exec('fly deploy --app my-app-green');
  
  // Run smoke tests
  const healthCheck = await fetch('https://my-app-green.fly.dev/api/health');
  if (!healthCheck.ok) throw new Error('Green deployment unhealthy');
  
  // Switch traffic
  await exec('fly ips allocate-v4 --app my-app-green');
  await exec('fly ips release --app my-app-blue');
  
  // Update Shopify configuration
  await exec('shopify app deploy --config production');
}
```

### Scaling Configuration:

```javascript
// config/scaling.js
export const scalingRules = {
  autoscale: {
    min: 2,
    max: 10,
    target_cpu: 70,
    target_memory: 80
  },
  regions: ['iad', 'lhr', 'syd'], // Multi-region for global apps
  database: {
    connection_limit: 20, // Per instance
    pool_timeout: 10
  }
};
```

## 7. Production Considerations for 2025

According to current Shopify best practices:

**Performance Requirements:**
- Response time < 1 second for API calls
- Database queries optimized with proper indexes
- CDN usage for static assets
- Implement caching layers (Redis recommended)

**Security Requirements:**
- All secrets encrypted at rest
- HTTPS only (enforced by hosting providers)
- Session encryption mandatory
- Regular dependency updates

**Compliance:**
- GDPR webhooks implemented
- Data retention policies
- Audit logging for sensitive operations

## 8. Hands-On Exercise

Create a complete deployment pipeline for a Shopify app:

**Requirements:**
1. Set up three environments (dev, staging, prod)
2. Implement zero-downtime deployments
3. Add health monitoring
4. Configure automatic rollbacks

**Starter template:**
```bash
# Clone the exercise repository
git clone https://github.com/your-repo/shopify-deployment-exercise
cd shopify-deployment-exercise

# Your tasks:
# 1. Create shopify.app.*.toml files for each environment
# 2. Set up GitHub Actions workflow
# 3. Configure Fly.io deployment
# 4. Implement health check endpoint
# 5. Add database migration strategy
```

## 9. Common Pitfalls and Solutions

**Issue 1: Database connection exhaustion**
```javascript
// Wrong - creates new connection each request
const prisma = new PrismaClient();

// Correct - singleton pattern
let prisma;
if (!global.prisma) {
  global.prisma = new PrismaClient({
    datasources: {
      db: {
        url: process.env.DATABASE_URL,
      },
    },
    log: process.env.NODE_ENV === 'development' ? ['query'] : [],
  });
}
prisma = global.prisma;
```

**Issue 2: Missing environment variables in production**
```javascript
// Add validation on startup
const requiredEnvVars = [
  'SHOPIFY_API_KEY',
  'SHOPIFY_API_SECRET', 
  'DATABASE_URL',
  'SESSION_SECRET'
];

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
}
```

## 10. Resources and Next Steps

**Documentation verified on September 24, 2025:**
- [Deploy to hosting service](https://shopify.dev/docs/apps/launch/deployment/deploy-to-hosting-service)
- [Deploy in CI/CD pipeline](https://shopify.dev/docs/apps/launch/deployment/deploy-in-ci-cd-pipeline)
- [App versions](https://shopify.dev/docs/apps/launch/deployment/app-versions)

**Recommended progression:**
1. Start with Fly.io for simplicity
2. Implement basic CI/CD with GitHub Actions
3. Add monitoring with Sentry or Datadog
4. Scale to multiple regions as needed

The current Shopify deployment model emphasizes containerization, automated deployments through CLI, and proper environment separation - all concepts you're familiar with from Laravel and Spring Boot, just with Node.js/JavaScript tooling instead.
