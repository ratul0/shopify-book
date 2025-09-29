# App Versions and Updates

## **Maintaining App versions and Updates**

I've verified the latest Shopify deployment documentation using the MCP tools. According to Shopify's documentation as of September 2025, the deployment model has undergone significant improvements since 2023, with app configuration becoming versioned in January 2024. The current recommended approach uses the `shopify app deploy` command for all deployments, which replaced the deprecated `config push` command.

## **The Laravel/Spring Boot Equivalent**

Coming from your Laravel and Spring Boot background, think of Shopify's app versioning system as similar to:

**Laravel's Migration & Release System**: Just as Laravel uses migrations for database versioning and Envoy/Forge for deployment with rollback capabilities, Shopify uses app versions that snapshot your entire configuration and extensions. The `shopify app deploy` command is analogous to running `php artisan migrate --force` combined with `git tag` and deployment scripts.

**Spring Boot's JAR Versioning**: Similar to how Spring Boot creates versioned JAR files with embedded configuration that you can deploy to different environments, Shopify creates immutable app versions. Each version contains your app configuration (like `application.yml`) and all extensions (like your compiled classes). The key difference is that Shopify versions are deployed atomically - either everything updates or nothing does.

**Angular's Build Artifacts**: Like Angular's `ng build --prod` creating versioned bundles with hashed filenames for cache-busting, Shopify's deploy creates versioned snapshots. However, unlike Angular where you might use feature flags or lazy loading for gradual rollouts, Shopify's model is more about complete version switching.

## **The Current Shopify Way**

According to the latest documentation, Shopify's deployment model centers around **app versions** - immutable snapshots of your app configuration and all extensions. This approach ensures consistency across all merchants using your app. When you deploy, you're creating a new version and immediately releasing it to all stores that have your app installed.

The deployment workflow follows this pattern: your local development work gets bundled into an app version through the CLI, which then gets distributed to all merchant stores. It takes several minutes for the new version to propagate to all users, similar to a CDN cache invalidation pattern you might know from web deployment.

## **Architecture Deep Dive**

The Shopify deployment architecture works quite differently from traditional web applications. When you run `shopify app deploy`, here's what happens under the hood:

First, the CLI validates your local configuration file (`shopify.app.toml`), which is similar to Laravel's `.env` file but versioned. It then bundles your app configuration with all CLI-managed extensions from your local environment. Crucially, any extensions not present locally will be removed from the new version - this is like Spring Boot's "what's in the JAR is what gets deployed" philosophy.

The system also pulls in the latest drafts of any dashboard-managed extensions. This dual-source approach is unique to Shopify - imagine if your Angular app could pull components from both your repository and a web-based editor simultaneously.

Here's the data flow:
```
Local Environment → shopify app deploy → App Version Created → Released to Stores
     ↓                                           ↓
[app config]                            [immutable snapshot]
[extensions]                                     ↓
[drafts from dashboard]                 [gradual rollout to merchants]
```

A critical gotcha for developers coming from traditional deployment: extensions missing from your local environment won't just be skipped - they'll be actively removed from merchant stores when the new version activates. This is like deploying a Spring Boot app where missing endpoints don't just return 404s, they completely disappear from the API.

## **Complete Working Example**

Let me show you a production-ready deployment setup with all the current best practices:

**API Version: 2025-01**
**Last verified: September 24, 2025**

### File: `.github/workflows/deploy.yml`
```yaml
# Production deployment workflow with rollback capabilities
name: Deploy to Production
on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Shopify CLI
        run: npm install -g @shopify/cli@latest
      
      - name: Create deployment with version tracking
        env:
          SHOPIFY_CLI_PARTNERS_TOKEN: ${{ secrets.SHOPIFY_CLI_PARTNERS_TOKEN }}
          SHOPIFY_API_KEY: ${{ secrets.SHOPIFY_API_KEY }}
        run: |
          # Generate version name from git commit
          VERSION="v$(date +%Y%m%d)-${GITHUB_SHA::8}"
          COMMIT_URL="${{ github.server_url }}/${{ github.repository }}/commit/${{ github.sha }}"
          
          # Deploy without immediate release for safety
          shopify app deploy \
            --version "$VERSION" \
            --message "Deployment from GitHub Actions" \
            --source-control-url "$COMMIT_URL" \
            --no-release \
            --force
          
          # Run automated tests against the new version
          # (your test scripts here)
          
          # If tests pass, release the version
          shopify app release --version "$VERSION" --force
```

### File: `scripts/rollback.sh`
```bash
#!/bin/bash
# Rollback script for emergency situations
# Similar to Laravel's `php artisan migrate:rollback`

# List recent versions to choose from
echo "Recent app versions:"
shopify app versions list

# Prompt for version to rollback to
read -p "Enter version name to rollback to: " VERSION

# Confirm the rollback
read -p "Are you sure you want to rollback to $VERSION? (y/n): " CONFIRM
if [ "$CONFIRM" = "y" ]; then
    shopify app release --version="$VERSION" --force
    echo "Rolled back to version: $VERSION"
    
    # Log the rollback for audit purposes
    echo "$(date): Rolled back to $VERSION" >> rollback.log
else
    echo "Rollback cancelled"
fi
```

### File: `shopify.app.production.toml`
```toml
# Production configuration with version management
name = "My Production App"
client_id = "production_client_id_here"
application_url = "https://my-app.example.com"
embedded = true

[access_scopes]
scopes = "read_products,write_orders"

[webhooks]
api_version = "2025-01"  # Always use latest stable version

[build]
# Critical: ensures config is included in deployments
include_config_on_deploy = true
# Disable URL updates in production
automatically_update_urls_on_dev = false
```

## **Real-World Scenarios Based on Current Capabilities**

### Scenario 1: Blue-Green Deployment Pattern
While Shopify doesn't natively support blue-green deployments like you might implement in Spring Boot with multiple service instances, you can achieve similar safety through the `--no-release` flag:

```bash
# Deploy new version without releasing (blue environment)
shopify app deploy --no-release --version "blue-$(date +%s)"

# Run your validation suite
npm run test:production

# If tests pass, switch traffic (green environment)
shopify app release --version "blue-1695564320"
```

### Scenario 2: Canary Releases Through Extension Management
Unlike Angular's lazy-loaded modules, Shopify doesn't support percentage-based rollouts directly. However, you can implement a form of canary release by managing features through metafields:

```javascript
// In your app code, check merchant eligibility for new features
const isCanaryMerchant = await checkCanaryStatus(shop.id);
if (isCanaryMerchant) {
  // Enable new feature
  enableNewCheckoutFlow();
}
```

### Scenario 3: Emergency Rollback Procedure
When a critical bug is discovered in production:

```bash
# 1. List recent versions with their timestamps
shopify app versions list

# 2. Identify the last known good version
# (e.g., "prod-20250923-stable")

# 3. Immediate rollback
shopify app release --version "prod-20250923-stable" --force

# 4. Notify team and investigate
echo "EMERGENCY: Rolled back to prod-20250923-stable at $(date)" | \
  mail -s "Production Rollback Alert" team@example.com
```

## **Advanced Patterns from Latest Documentation**

The documentation reveals several advanced patterns that aren't immediately obvious:

**Continuous Deployment with Version Locking**: You can create a deployment pipeline that maintains version consistency across environments by using the `--source-control-url` flag to link commits directly to app versions. This creates an audit trail similar to Spring Boot's actuator info endpoint.

**Extension Orchestration**: Since dashboard-managed extensions always deploy their latest drafts, coordinate dashboard changes with CLI deployments by implementing a "freeze window" before deployments where no dashboard changes are allowed.

**Multi-Repository Management**: For teams managing extensions across multiple repositories (similar to microservices), use the `extension_directories` configuration to point to git submodules:

```toml
[build]
extension_directories = [
  "extensions/*",
  "external/payment-extensions/*",
  "external/checkout-extensions/*"
]
```

## **Hands-On Exercise**

Here's a practical exercise that demonstrates version management with rollback capabilities:

**Challenge**: Implement a safe deployment pipeline with automatic rollback on error detection.

**Requirements**:
1. Deploy a new version with a simulated bug
2. Detect the issue through webhook monitoring
3. Automatically rollback to the previous version
4. Send notifications about the rollback

**Starter Code**:
```javascript
// monitor-deployment.js
const { shopifyApp } = require("@shopify/shopify-app-express");

class DeploymentMonitor {
  constructor() {
    this.errorThreshold = 5;
    this.monitoringWindow = 300000; // 5 minutes
    this.errorCount = 0;
  }
  
  async checkDeploymentHealth() {
    // Monitor webhook delivery failures
    const webhookHealth = await this.getWebhookMetrics();
    
    if (webhookHealth.failureRate > 0.1) {
      console.error("High webhook failure rate detected");
      await this.initiateRollback();
    }
  }
  
  async initiateRollback() {
    // Get the previous version
    const versions = await this.getVersionList();
    const previousVersion = versions[1]; // Second most recent
    
    // Perform rollback
    console.log(`Rolling back to ${previousVersion.name}`);
    // Implementation here
  }
}

// Your task: Complete the rollback implementation
```

**Hints**: 
- In Laravel, you'd use `DB::transaction()` for atomic operations - here, use Shopify's version atomicity
- Like Spring Boot's `@Retryable`, implement retry logic for the release command
- Similar to Angular's error boundaries, implement graceful degradation

## **Migration Path and Current Best Practices**

Based on the latest documentation, here's how to modernize your deployment practices:

**From Legacy `config push` to Modern `deploy`**:
```bash
# Old way (deprecated)
shopify app config push --force

# Current way (2025)
shopify app deploy --force
```

**Common Mistakes to Avoid**:
1. **Missing Extensions**: Forgetting that local absence means production removal
2. **Immediate Release**: Not using `--no-release` for critical deployments
3. **Version Naming**: Not using semantic versioning or meaningful identifiers
4. **Webhook Timing**: Not accounting for the propagation delay to all merchants

**Performance Best Practices**:
- Deploy during low-traffic periods when possible
- Use the `--source-control-url` flag for tracability
- Implement deployment monitoring for the first 30 minutes
- Keep a deployment runbook with rollback procedures

## **Verification and Resources**

Here's how I verified this information using the Shopify MCP tools:

```javascript
// Verification process:
// 1. Called: shopify-dev-mcp:search_docs_chunks
//    Query: "shopify cli deploy app configuration updates extension deployment"
//    Result: Found current deployment documentation confirming simplified model

// 2. Called: shopify-dev-mcp:fetch_full_docs
//    Paths: ["/docs/api/shopify-cli/app/app-deploy", 
//            "/docs/api/shopify-cli/app/app-release"]
//    Result: Confirmed current CLI commands and flags
```

**Key Documentation Links**:
- [App Versions Overview](https://shopify.dev/apps/launch/deployment/app-versions) - Last updated: 2025
- [Deploy App Versions](https://shopify.dev/apps/launch/deployment/deploy-app-versions) - Current best practices
- [CI/CD Pipeline Integration](https://shopify.dev/apps/launch/deployment/deploy-in-ci-cd-pipeline) - Automation patterns

**Related Learning Paths**:
- **Next**: Learn about [Shopify Functions deployment](https://shopify.dev/docs/apps/build/functions) which has special compilation requirements
- **Advanced**: Explore [multi-store deployment patterns](https://shopify.dev/docs/apps/build/graphql-admin-api-rate-limits) for Plus merchants

**Recent Changes (2024-2025)**:
- January 2024: App configuration became versioned
- `config push` command deprecated in favor of unified `deploy`
- New `--source-control-url` flag added for commit linking
- Dashboard-managed extensions now included automatically

This deployment model represents a significant evolution from traditional web deployment, emphasizing consistency and safety over granular control. The immutable version approach ensures that all merchants experience the same app behavior, which is critical for commerce applications where consistency equals trust.
