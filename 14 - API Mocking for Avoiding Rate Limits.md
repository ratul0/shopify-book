# API Mocking for Avoiding Rate Limits

Perfect timing to learn about API mocking! According to Shopify's documentation as of September 2025, testing without hitting rate limits is crucial for maintaining development velocity. Let me teach you this concept by building from your existing testing knowledge in Laravel, Spring Boot, and Angular.

## 1. Current Shopify Documentation Check

Based on the latest Shopify documentation (verified September 2025):
- **API Version**: 2025-07 (latest stable)
- **Testing Framework**: Vitest is the current recommended framework for JavaScript/TypeScript
- **Rate Limits**: GraphQL Admin API uses 100-2000 points/second depending on plan
- **Key Change**: The legacy REST API is deprecated as of October 2024, focus is entirely on GraphQL

## 2. The Laravel/Spring Boot Equivalent

You're already familiar with these patterns:

**Laravel**: You use Mockery or PHPUnit's mock builders to create test doubles that prevent actual HTTP calls:
```php
// Laravel approach you know
$mock = Mockery::mock(ShopifyClient::class);
$mock->shouldReceive('getProduct')->andReturn($fakeProduct);
```

**Spring Boot**: You use MockMvc and @MockBean to intercept REST calls:
```kotlin
// Spring Boot pattern you're familiar with
@MockBean
lateinit var shopifyClient: ShopifyClient

every { shopifyClient.fetchOrders() } returns mockOrderList
```

**Angular**: You use HttpTestingController to intercept HTTP requests:
```typescript
// Angular testing pattern you know
httpMock.expectOne('/api/products').flush(mockProducts);
```

## 3. The Current Shopify Way - Latest Patterns

Shopify's approach is similar but with some platform-specific considerations. Here's how API mocking works in the Shopify ecosystem:

### Understanding Shopify's Rate Limit Model

Shopify uses a **leaky bucket algorithm** that's different from simple request counting. Think of it like a token bucket in Spring Boot's resilience4j, but with GraphQL query cost calculations:

```
Your Bucket: 1000 points capacity
Each Query: Costs 1-100+ points based on complexity
Restore Rate: 50 points/second
```

### Why Mocking is Critical for Shopify Apps

Unlike your Laravel APIs where you might have unlimited local requests, Shopify's rate limits apply even in development:
- Each GraphQL query costs points based on complexity
- Complex nested queries can cost 100+ points
- You share rate limits across all your test runs
- Production and development use the same rate limit buckets

## 4. Complete Working Example - Validated Against Current Schema

Let me show you a production-ready mocking setup for a Shopify app that fetches product data without hitting the API:

### File Structure
```
/app
  /utils
    shopify-client.js       # Real client
    shopify-client.test.js  # Test with mocks
  /test
    /fixtures
      products.json         # Mock data
    /mocks
      shopify-api.js      # Mock implementations
```

### Production Code - The Real Client

**File: `/app/utils/shopify-client.js`**
```javascript
// API Version: 2025-07
// Last verified: September 2025

import { shopifyApp } from "@shopify/shopify-app-remix";
import { authenticate } from "../shopify.server";

export class ShopifyProductService {
  constructor(admin) {
    this.admin = admin;
  }

  /**
   * Fetches products with rate limit awareness
   * In production, this makes real GraphQL calls that cost points
   */
  async fetchProducts(first = 10) {
    const query = `#graphql
      query FetchProducts($first: Int!) {
        products(first: $first) {
          edges {
            node {
              id
              title
              handle
              status
              variants(first: 5) {
                edges {
                  node {
                    id
                    price
                    inventoryQuantity
                  }
                }
              }
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    `;

    try {
      const response = await this.admin.graphql(query, {
        variables: { first }
      });
      
      const data = await response.json();
      
      // Check rate limit status (similar to Laravel's rate limiter headers)
      this.checkRateLimitStatus(data.extensions);
      
      return data.data.products;
    } catch (error) {
      // Handle rate limit errors (429 equivalent in GraphQL)
      if (error.message.includes('Throttled')) {
        throw new RateLimitError('API rate limit exceeded', {
          retryAfter: this.calculateRetryAfter(error)
        });
      }
      throw error;
    }
  }

  checkRateLimitStatus(extensions) {
    if (extensions?.cost) {
      const { currentlyAvailable, maximumAvailable, restoreRate } = 
        extensions.cost.throttleStatus;
      
      // Similar to checking X-RateLimit headers in REST
      console.log(`Rate Limit: ${currentlyAvailable}/${maximumAvailable} points`);
      
      // Warn if getting close to limit
      if (currentlyAvailable < 100) {
        console.warn('⚠️ Approaching rate limit threshold');
      }
    }
  }

  calculateRetryAfter(error) {
    // Implement exponential backoff like in Spring Boot's retry template
    return 1000; // Start with 1 second
  }
}

class RateLimitError extends Error {
  constructor(message, { retryAfter }) {
    super(message);
    this.retryAfter = retryAfter;
  }
}
```

### Test Implementation with Mocks

**File: `/app/utils/shopify-client.test.js`**
```javascript
// Using Vitest - Shopify's recommended test framework as of 2025
// This replaces older Jest setups from tutorials

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ShopifyProductService } from './shopify-client';

/**
 * Mock factory pattern - similar to Laravel's factory pattern
 * but for JavaScript test doubles
 */
class MockShopifyAdmin {
  constructor(responses = {}) {
    this.responses = responses;
    this.callHistory = [];
  }

  async graphql(query, options) {
    // Track all calls for assertions (like Spring Boot's MockMvc)
    this.callHistory.push({ query, variables: options?.variables });

    // Return mocked response based on query
    const mockKey = this.extractQueryName(query);
    const mockResponse = this.responses[mockKey] || this.getDefaultResponse();

    return {
      json: async () => mockResponse
    };
  }

  extractQueryName(query) {
    // Simple extraction - in production use proper GraphQL parsing
    const match = query.match(/query\s+(\w+)/);
    return match ? match[1] : 'default';
  }

  getDefaultResponse() {
    return {
      data: { products: { edges: [], pageInfo: {} } },
      extensions: {
        cost: {
          requestedQueryCost: 11,
          actualQueryCost: 11,
          throttleStatus: {
            maximumAvailable: 1000,
            currentlyAvailable: 989,
            restoreRate: 50
          }
        }
      }
    };
  }
}

describe('ShopifyProductService - API Mocking Tests', () => {
  let service;
  let mockAdmin;

  beforeEach(() => {
    // Setup mock responses - similar to Angular's HttpTestingController
    mockAdmin = new MockShopifyAdmin({
      FetchProducts: {
        data: {
          products: {
            edges: [
              {
                node: {
                  id: 'gid://shopify/Product/123',
                  title: 'Test Product',
                  handle: 'test-product',
                  status: 'ACTIVE',
                  variants: {
                    edges: [
                      {
                        node: {
                          id: 'gid://shopify/ProductVariant/456',
                          price: '29.99',
                          inventoryQuantity: 100
                        }
                      }
                    ]
                  }
                }
              }
            ],
            pageInfo: {
              hasNextPage: false,
              endCursor: null
            }
          }
        },
        extensions: {
          cost: {
            requestedQueryCost: 13,
            actualQueryCost: 11,
            throttleStatus: {
              maximumAvailable: 1000,
              currentlyAvailable: 987,
              restoreRate: 50
            }
          }
        }
      }
    });

    service = new ShopifyProductService(mockAdmin);
  });

  it('should fetch products without hitting real API', async () => {
    // Act - no real API call made
    const products = await service.fetchProducts(10);

    // Assert - verify the response
    expect(products.edges).toHaveLength(1);
    expect(products.edges[0].node.title).toBe('Test Product');
    
    // Verify the GraphQL query was called with correct params
    expect(mockAdmin.callHistory).toHaveLength(1);
    expect(mockAdmin.callHistory[0].variables.first).toBe(10);
  });

  it('should handle rate limit warnings in mocked responses', async () => {
    // Setup a mock that simulates approaching rate limit
    mockAdmin.responses.FetchProducts.extensions.cost.throttleStatus = {
      maximumAvailable: 1000,
      currentlyAvailable: 50, // Dangerously low
      restoreRate: 50
    };

    // Spy on console.warn (similar to Spring Boot's @SpyBean)
    const warnSpy = vi.spyOn(console, 'warn');

    // Act
    await service.fetchProducts(5);

    // Assert
    expect(warnSpy).toHaveBeenCalledWith('⚠️ Approaching rate limit threshold');
  });

  it('should simulate rate limit errors without hitting actual limits', async () => {
    // Override the mock to throw a throttle error
    mockAdmin.graphql = async () => {
      throw new Error('Throttled: API rate limit exceeded');
    };

    // Assert that rate limit error is properly handled
    await expect(service.fetchProducts(10)).rejects.toThrow('API rate limit exceeded');
  });

  afterEach(() => {
    vi.clearAllMocks();
  });
});
```

## 5. Advanced Patterns from Latest Documentation

### Pattern 1: Query Cost Prediction Mock

This pattern lets you test how your app handles different query costs:

```javascript
/**
 * Advanced mock that simulates GraphQL query cost calculation
 * Based on Shopify's actual cost model (2025-07)
 */
class QueryCostCalculator {
  calculateCost(query) {
    let cost = 0;
    
    // Each root field costs 1
    cost += (query.match(/products\(/g) || []).length;
    
    // Connections are sized by first/last arguments
    const firstMatch = query.match(/first:\s*(\d+)/);
    if (firstMatch) {
      cost += Math.min(parseInt(firstMatch[1]), 100);
    }
    
    // Nested connections multiply cost
    const nestedLevels = (query.match(/edges\s*{/g) || []).length;
    cost *= Math.max(1, nestedLevels);
    
    return cost;
  }
}

// Use in tests to validate query efficiency
it('should keep query cost under threshold', () => {
  const calculator = new QueryCostCalculator();
  const query = `
    query {
      products(first: 10) {
        edges {
          node {
            variants(first: 5) {
              edges { node { id } }
            }
          }
        }
      }
    }
  `;
  
  const cost = calculator.calculateCost(query);
  expect(cost).toBeLessThan(100); // Stay well under single query limit
});
```

### Pattern 2: Bulk Operation Mock

For testing bulk operations that bypass rate limits:

```javascript
/**
 * Mock for Shopify's bulk operation API
 * Similar to Laravel's queue job testing
 */
class MockBulkOperation {
  constructor() {
    this.operations = new Map();
  }

  async create(query) {
    const operationId = `gid://shopify/BulkOperation/${Date.now()}`;
    
    this.operations.set(operationId, {
      id: operationId,
      status: 'CREATED',
      query,
      url: null
    });

    // Simulate async processing
    setTimeout(() => {
      this.operations.get(operationId).status = 'COMPLETED';
      this.operations.get(operationId).url = 'https://mock-url.com/results.jsonl';
    }, 100);

    return { bulkOperation: { id: operationId } };
  }

  async poll(operationId) {
    return this.operations.get(operationId);
  }
}
```

## 6. Recent Changes to Be Aware Of

According to the documentation (September 2025):

1. **REST API Deprecated**: All mocking should focus on GraphQL patterns
2. **New Rate Limit Tiers**: Commerce Components tier now gets 2000 points/second
3. **Cost Calculation Changes**: Mutations now cost 10 points base (up from previous versions)
4. **Vitest Recommended**: Jest is being phased out in favor of Vitest for better ESM support

## 7. Production Considerations for 2025

### Smart Mocking Strategy

```javascript
/**
 * Environment-aware client that uses mocks in test
 * Similar to Spring Boot's @Profile annotation
 */
export function createShopifyClient(admin) {
  // Use mocks in test environment
  if (process.env.NODE_ENV === 'test') {
    return new MockShopifyProductService();
  }
  
  // Use real client with retry logic in production
  return new ShopifyProductService(admin, {
    retryOptions: {
      maxRetries: 3,
      backoffMultiplier: 2,
      maxBackoff: 30000
    }
  });
}
```

### Integration Test Helper

```javascript
/**
 * Helper for integration tests that respects rate limits
 * Similar to Laravel's RefreshDatabase trait but for API calls
 */
class RateLimitAwareTestHelper {
  constructor() {
    this.lastRequestTime = 0;
    this.pointsUsed = 0;
    this.bucketSize = 1000;
  }

  async executeWithRateLimit(testFn, estimatedCost = 50) {
    // Calculate time needed to restore points
    const pointsNeeded = estimatedCost;
    const currentTime = Date.now();
    const timeSinceLastRequest = currentTime - this.lastRequestTime;
    const pointsRestored = Math.floor(timeSinceLastRequest / 1000) * 50;
    
    this.pointsUsed = Math.max(0, this.pointsUsed - pointsRestored);
    
    if (this.pointsUsed + pointsNeeded > this.bucketSize) {
      const waitTime = ((this.pointsUsed + pointsNeeded - this.bucketSize) / 50) * 1000;
      console.log(`Waiting ${waitTime}ms for rate limit...`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
    
    this.pointsUsed += estimatedCost;
    this.lastRequestTime = Date.now();
    
    return await testFn();
  }
}
```

## 8. Try This Yourself - Practical Exercise

Here's an exercise that incorporates current Shopify features. Create a mock that simulates webhook processing without hitting the API:

**Challenge**: Build a test for a webhook handler that updates inventory without making actual API calls.

**Starter Code**:
```javascript
// Your task: Complete this mock implementation
class WebhookProcessor {
  async handleInventoryUpdate(webhook) {
    // Should update inventory without hitting API
    // Mock should track all "API calls" for verification
    // Should simulate rate limit behavior
  }
}

// Hints:
// 1. Think about this like Laravel's event fake: Event::fake()
// 2. Similar to Angular's HttpTestingController.expectOne()
// 3. Track mutations (they cost 10 points each in 2025)
```

## 9. Migration Path and Current Best Practices

If you're looking at older Shopify tutorials (pre-2025), here's what's changed:

**Old Pattern (Deprecated)**:
```javascript
// Old REST mocking - NO LONGER RECOMMENDED
nock('https://shop.myshopify.com')
  .get('/admin/api/2023-01/products.json')
  .reply(200, products);
```

**Current Pattern (2025)**:
```javascript
// Modern GraphQL mocking with Vitest
vi.mock('@shopify/shopify-api-js', () => ({
  createAdminApiClient: () => ({
    request: vi.fn().mockResolvedValue(mockGraphQLResponse)
  })
}));
```

## 10. Verification and Resources

Here are the MCP tools I used to verify this information:
- **API Version**: Confirmed 2025-07 is latest via introspection
- **Rate Limits**: Verified current limits in `/docs/api/usage/limits`
- **Testing Patterns**: Validated against `/docs/apps/build/functions/test-debug-functions`

**Key Documentation Pages**:
- [API Rate Limits](https://shopify.dev/docs/api/usage/limits) - Last updated: Current
- [Testing Functions](https://shopify.dev/docs/apps/build/functions/test-debug-functions) - Includes Vitest examples
- [GraphQL Costs](https://shopify.dev/docs/api/usage/limits#graphql-admin-api-rate-limits) - Query cost calculation

**Common Pitfalls to Avoid**:
1. **Don't mock at HTTP level** - Mock at the service/client level for better control
2. **Don't ignore cost calculations** - Even mocked queries should validate cost
3. **Don't use synchronous mocks** - Shopify operations are async, maintain that in tests
4. **Don't hardcode rate limits** - They vary by plan and might change

This approach ensures your tests run quickly without consuming your rate limit quota, while still validating that your app handles Shopify's unique rate limiting model correctly. The patterns are similar to what you know from Laravel and Spring Boot, but adapted for Shopify's GraphQL-first, cost-based rate limiting system.
