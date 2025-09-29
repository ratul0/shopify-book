# Testing and Quality Assurance for Shopify Apps

Welcome to one of the most critical phases of Shopify app development! Testing in the Shopify ecosystem requires a unique approach that combines traditional testing patterns you know from Laravel and Spring Boot with Shopify-specific considerations. Let me guide you through the current testing landscape and best practices as of September 2025.

## 1. Current Shopify Documentation Check

**API Version:** 2025-07 (Latest Stable)  
**Last Verified:** September 24, 2025  
**Testing Stack:** Remix + Vitest + Playwright  
**Recent Changes:** Shopify has standardized on Vitest for unit testing in JavaScript/TypeScript apps, replacing Jest in most templates. The `app function replay` command was introduced for better function testing.

## 2. The Laravel/Spring Boot Equivalent

Coming from your background, here's how Shopify testing maps to what you already know:

**Laravel Testing → Shopify Testing:**
- PHPUnit → Vitest (for JavaScript/TypeScript)
- Laravel's TestCase → Custom test utilities with Shopify mocks
- Database Factories → Mock data generators for GraphQL responses
- Laravel Dusk → Playwright for E2E testing
- Eloquent Mocking → GraphQL response mocking
- Middleware testing → Webhook handler testing

**Spring Boot Testing → Shopify Testing:**
- JUnit → Vitest
- @MockBean → Manual mocks of Shopify clients
- @DataJpaTest → GraphQL query/mutation testing
- MockMvc → Supertest for API endpoint testing
- TestContainers → Development stores for integration testing

The key difference in Shopify development is that you're testing against external APIs rather than your own database, which fundamentally changes your testing strategy. Instead of testing database transactions, you're testing API interactions and webhook processing.

## 3. The Current Shopify Testing Architecture
### Shopify App Testing Architecture

#### Testing Pyramid for Shopify Apps

```
         /\
        /E2E\         <- Test on Development Store
       /______\
      /        \
     /Integration\    <- Test API Interactions
    /______________\
   /                \
  /   Unit Tests     \  <- Test Business Logic
 /____________________\
```

### Testing Strategy by Component

#### 1. Unit Testing (70% of tests)
**Purpose:** Test isolated business logic without external dependencies

**What to Test:**
- Data transformation functions
- Price calculations
- Validation logic
- Utility functions
- React component behavior
- State management logic

**Tools:**
- Vitest (primary test runner)
- React Testing Library
- MSW (Mock Service Worker) for API mocking

#### 2. Integration Testing (20% of tests)
**Purpose:** Test how your app integrates with Shopify APIs

**What to Test:**
- GraphQL query/mutation execution
- Webhook handler processing
- Session management
- Authentication flows
- Database operations with Prisma
- App proxy endpoints

**Tools:**
- Vitest with integration test suites
- Supertest for HTTP testing
- Development stores for real API testing

#### 3. End-to-End Testing (10% of tests)
**Purpose:** Test complete user workflows

**What to Test:**
- App installation flow
- Complete purchase workflows
- Admin UI interactions
- Checkout UI extensions
- Theme app extensions

**Tools:**
- Playwright
- Cypress (alternative)
- Development stores

### Test File Structure

```
your-shopify-app/
├── app/
│   ├── routes/
│   │   ├── app._index.jsx
│   │   └── app._index.test.jsx          # Route tests
│   ├── models/
│   │   ├── Product.server.js
│   │   └── Product.server.test.js       # Model tests
│   └── utils/
│       ├── price-calculator.js
│       └── price-calculator.test.js     # Utility tests
├── extensions/
│   ├── checkout-ui/
│   │   ├── src/
│   │   │   ├── Checkout.jsx
│   │   │   └── Checkout.test.jsx       # Extension tests
│   └── product-discount/
│       ├── src/
│       │   ├── run.js
│       │   └── run.test.js             # Function tests
├── tests/
│   ├── fixtures/                        # Test data
│   ├── integration/                     # Integration tests
│   └── e2e/                            # End-to-end tests
├── test-utils/
│   ├── shopify-mocks.js                # Mock implementations
│   └── test-helpers.js                 # Shared test utilities
└── vitest.config.js                    # Test configuration
```

## Current Best Practices (2025)

### 1. Mock Shopify API Responses Accurately
```javascript
// Use realistic mock data that matches actual API responses
const mockProductResponse = {
  data: {
    product: {
      id: "gid://shopify/Product/123456789",
      title: "Test Product",
      // Include all fields your code actually uses
    }
  }
};
```

### 2. Test Rate Limiting Behavior
```javascript
// Simulate rate limit responses
const mockRateLimitedResponse = {
  errors: [{
    message: "Throttled",
    extensions: {
      code: "THROTTLED",
      retryAfter: 2.0
    }
  }]
};
```

### 3. Test Webhook Verification
```javascript
// Always test webhook HMAC verification
test('verifies webhook signature', async () => {
  const rawBody = JSON.stringify({ /* webhook data */ });
  const hmac = createHmac(rawBody, secret);
  // Test both valid and invalid signatures
});
```

### 4. Use Development Stores for Integration Tests
- Create dedicated test stores with consistent data
- Use Shopify CLI's `app dev` for real-time testing
- Test with both online and offline sessions

### 5. Test Error States Thoroughly
```javascript
// Test all error scenarios
test.each([
  ['network error', new Error('Network failed')],
  ['GraphQL error', { errors: [{ message: 'Not found' }] }],
  ['invalid session', { error: 'Invalid session token' }],
])('handles %s correctly', async (scenario, error) => {
  // Test error handling
});
```

## Environment-Specific Testing

### Development Environment
```bash
# Run with hot reload
npm run dev
npm run test:watch
```

### CI/CD Pipeline
```bash
# Run all tests once
npm run test
npm run test:integration
npm run test:e2e
```

### Production Monitoring
- Use Shopify Partner Dashboard for error tracking
- Implement custom error logging
- Monitor webhook processing success rates

## Common Testing Pitfalls to Avoid

1. **Don't test Shopify's API behavior** - Test your integration, not whether Shopify's API works
2. **Don't use production credentials in tests** - Use test stores and mock data
3. **Don't skip webhook verification tests** - Security is critical
4. **Don't ignore rate limiting** - Test retry logic and backoff strategies
5. **Don't test against live stores** - Always use development stores

## Testing Checklist

- [ ] Unit tests for all business logic
- [ ] Integration tests for API interactions
- [ ] Webhook handler tests with signature verification
- [ ] Authentication flow tests
- [ ] Error handling tests for all failure modes
- [ ] Rate limiting and retry logic tests
- [ ] E2E test for critical user paths
- [ ] Performance tests for bulk operations
- [ ] Security tests for data validation
- [ ] Accessibility tests for UI components

## 4. Complete Working Example: Unit Testing

Let me show you a comprehensive unit testing setup that reflects how modern Shopify apps are tested, particularly focusing on a Remix app with Vitest.

```js
// File: app/utils/price-calculator.js
// This module handles complex pricing logic with Shopify-specific considerations

/**
 * Calculates the final price after applying various discount types
 * This is similar to Laravel's pricing services but adapted for Shopify's model
 */
export class PriceCalculator {
  constructor(shopifyClient) {
    this.shopifyClient = shopifyClient;
  }

  /**
   * Calculate price with percentage discount
   * @param {number} originalPrice - Original price in cents
   * @param {number} discountPercentage - Discount as percentage (0-100)
   * @returns {number} Final price in cents
   */
  calculatePercentageDiscount(originalPrice, discountPercentage) {
    if (discountPercentage < 0 || discountPercentage > 100) {
      throw new Error('Discount percentage must be between 0 and 100');
    }
    
    const discount = Math.floor(originalPrice * (discountPercentage / 100));
    return originalPrice - discount;
  }

  /**
   * Calculate price with fixed amount discount
   * @param {number} originalPrice - Original price in cents
   * @param {number} discountAmount - Fixed discount in cents
   * @returns {number} Final price in cents (minimum 0)
   */
  calculateFixedDiscount(originalPrice, discountAmount) {
    if (discountAmount < 0) {
      throw new Error('Discount amount cannot be negative');
    }
    
    return Math.max(0, originalPrice - discountAmount);
  }

  /**
   * Apply multiple discounts with Shopify's stacking rules
   * Similar to how Laravel might chain discount middleware
   */
  applyDiscountStack(originalPrice, discounts) {
    let currentPrice = originalPrice;
    
    // Sort discounts by priority (Shopify-specific logic)
    const sortedDiscounts = discounts.sort((a, b) => a.priority - b.priority);
    
    for (const discount of sortedDiscounts) {
      switch (discount.type) {
        case 'PERCENTAGE':
          currentPrice = this.calculatePercentageDiscount(currentPrice, discount.value);
          break;
        case 'FIXED_AMOUNT':
          currentPrice = this.calculateFixedDiscount(currentPrice, discount.value);
          break;
        case 'BOGO':
          currentPrice = this.applyBogoDiscount(currentPrice, discount);
          break;
        default:
          console.warn(`Unknown discount type: ${discount.type}`);
      }
      
      // Shopify rule: Stop if we hit free
      if (currentPrice === 0) break;
    }
    
    return currentPrice;
  }

  /**
   * Apply Buy One Get One discount logic
   */
  applyBogoDiscount(price, discount) {
    if (discount.quantity >= discount.requiredQuantity) {
      const setsEligible = Math.floor(discount.quantity / discount.requiredQuantity);
      const freeItems = setsEligible * discount.freeQuantity;
      const pricePerItem = price / discount.quantity;
      return Math.floor(price - (freeItems * pricePerItem * (discount.percentOff / 100)));
    }
    return price;
  }

  /**
   * Fetch and apply automatic discounts from Shopify
   * This would integrate with actual Shopify GraphQL in production
   */
  async applyAutomaticDiscounts(productId, originalPrice, customerData = {}) {
    try {
      // In production, this would call Shopify's GraphQL API
      const discounts = await this.shopifyClient.fetchAutomaticDiscounts(productId);
      
      // Check customer eligibility
      const eligibleDiscounts = discounts.filter(discount => 
        this.isCustomerEligible(discount, customerData)
      );
      
      return this.applyDiscountStack(originalPrice, eligibleDiscounts);
    } catch (error) {
      console.error('Failed to fetch automatic discounts:', error);
      // Fail gracefully - return original price if discounts can't be fetched
      return originalPrice;
    }
  }

  /**
   * Check if customer is eligible for a discount
   * Similar to Laravel's authorization policies
   */
  isCustomerEligible(discount, customerData) {
    // Check customer tags
    if (discount.customerTags?.length > 0) {
      const hasRequiredTag = discount.customerTags.some(tag => 
        customerData.tags?.includes(tag)
      );
      if (!hasRequiredTag) return false;
    }
    
    // Check minimum purchase amount
    if (discount.minimumPurchase && customerData.cartTotal < discount.minimumPurchase) {
      return false;
    }
    
    // Check customer segment
    if (discount.customerSegment) {
      return this.matchesSegment(customerData, discount.customerSegment);
    }
    
    return true;
  }

  /**
   * Match customer to a segment
   */
  matchesSegment(customerData, segment) {
    switch (segment) {
      case 'NEW':
        return customerData.orderCount === 0;
      case 'RETURNING':
        return customerData.orderCount > 0;
      case 'VIP':
        return customerData.totalSpent >= 100000; // $1000 in cents
      default:
        return false;
    }
  }

  /**
   * Format price for display (Shopify money format)
   */
  formatPrice(priceInCents, currencyCode = 'USD') {
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currencyCode,
      minimumFractionDigits: 2,
    });
    
    return formatter.format(priceInCents / 100);
  }
}

// ============================================
// File: app/utils/price-calculator.test.js
// Comprehensive unit tests using Vitest

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { PriceCalculator } from './price-calculator';

describe('PriceCalculator', () => {
  let calculator;
  let mockShopifyClient;

  beforeEach(() => {
    // Create a mock Shopify client similar to how you'd mock in Laravel
    mockShopifyClient = {
      fetchAutomaticDiscounts: vi.fn(),
    };
    calculator = new PriceCalculator(mockShopifyClient);
  });

  describe('calculatePercentageDiscount', () => {
    it('calculates 20% discount correctly', () => {
      const originalPrice = 10000; // $100 in cents
      const discount = 20; // 20%
      const result = calculator.calculatePercentageDiscount(originalPrice, discount);
      
      expect(result).toBe(8000); // $80
    });

    it('handles 100% discount (free)', () => {
      const result = calculator.calculatePercentageDiscount(5000, 100);
      expect(result).toBe(0);
    });

    it('throws error for invalid discount percentage', () => {
      expect(() => calculator.calculatePercentageDiscount(1000, -5))
        .toThrow('Discount percentage must be between 0 and 100');
      
      expect(() => calculator.calculatePercentageDiscount(1000, 101))
        .toThrow('Discount percentage must be between 0 and 100');
    });

    // This is similar to PHPUnit's data providers in Laravel
    it.each([
      [10000, 10, 9000],
      [10000, 25, 7500],
      [10000, 50, 5000],
      [10000, 75, 2500],
      [9999, 33, 6699], // Test rounding
    ])('calculates %i with %i%% discount to be %i', (original, discount, expected) => {
      expect(calculator.calculatePercentageDiscount(original, discount)).toBe(expected);
    });
  });

  describe('calculateFixedDiscount', () => {
    it('subtracts fixed amount correctly', () => {
      const result = calculator.calculateFixedDiscount(10000, 2000);
      expect(result).toBe(8000);
    });

    it('returns 0 when discount exceeds price', () => {
      const result = calculator.calculateFixedDiscount(5000, 10000);
      expect(result).toBe(0);
    });

    it('throws error for negative discount', () => {
      expect(() => calculator.calculateFixedDiscount(1000, -100))
        .toThrow('Discount amount cannot be negative');
    });
  });

  describe('applyDiscountStack', () => {
    it('applies multiple discounts in priority order', () => {
      const discounts = [
        { type: 'PERCENTAGE', value: 10, priority: 2 },
        { type: 'FIXED_AMOUNT', value: 1000, priority: 1 },
      ];
      
      // Should apply fixed first (priority 1), then percentage
      // $100 - $10 = $90, then 10% off = $81
      const result = calculator.applyDiscountStack(10000, discounts);
      expect(result).toBe(8100);
    });

    it('stops applying discounts when price reaches 0', () => {
      const discounts = [
        { type: 'FIXED_AMOUNT', value: 15000, priority: 1 },
        { type: 'PERCENTAGE', value: 50, priority: 2 },
      ];
      
      const result = calculator.applyDiscountStack(10000, discounts);
      expect(result).toBe(0);
    });

    it('handles BOGO discounts', () => {
      const discounts = [{
        type: 'BOGO',
        priority: 1,
        quantity: 4,
        requiredQuantity: 2,
        freeQuantity: 1,
        percentOff: 100
      }];
      
      // 4 items, buy 2 get 1 free = 2 free items
      const result = calculator.applyDiscountStack(10000, discounts);
      expect(result).toBe(5000); // Half price overall
    });

    it('warns about unknown discount types', () => {
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      const discounts = [{ type: 'UNKNOWN', value: 10, priority: 1 }];
      const result = calculator.applyDiscountStack(10000, discounts);
      
      expect(result).toBe(10000); // Price unchanged
      expect(consoleSpy).toHaveBeenCalledWith('Unknown discount type: UNKNOWN');
      
      consoleSpy.mockRestore();
    });
  });

  describe('applyAutomaticDiscounts', () => {
    it('fetches and applies automatic discounts', async () => {
      const mockDiscounts = [
        { type: 'PERCENTAGE', value: 15, priority: 1 }
      ];
      
      mockShopifyClient.fetchAutomaticDiscounts.mockResolvedValue(mockDiscounts);
      
      const result = await calculator.applyAutomaticDiscounts(
        'gid://shopify/Product/123',
        10000
      );
      
      expect(mockShopifyClient.fetchAutomaticDiscounts).toHaveBeenCalledWith('gid://shopify/Product/123');
      expect(result).toBe(8500);
    });

    it('filters discounts based on customer eligibility', async () => {
      const mockDiscounts = [
        { type: 'PERCENTAGE', value: 20, priority: 1, customerTags: ['VIP'] },
        { type: 'PERCENTAGE', value: 10, priority: 2 } // No restrictions
      ];
      
      mockShopifyClient.fetchAutomaticDiscounts.mockResolvedValue(mockDiscounts);
      
      const customerData = { tags: ['REGULAR'] }; // Not VIP
      const result = await calculator.applyAutomaticDiscounts(
        'gid://shopify/Product/123',
        10000,
        customerData
      );
      
      // Only 10% discount should apply
      expect(result).toBe(9000);
    });

    it('handles API errors gracefully', async () => {
      mockShopifyClient.fetchAutomaticDiscounts.mockRejectedValue(
        new Error('Network error')
      );
      
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      const result = await calculator.applyAutomaticDiscounts(
        'gid://shopify/Product/123',
        10000
      );
      
      expect(result).toBe(10000); // Returns original price
      expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });
  });

  describe('isCustomerEligible', () => {
    it('checks customer tags correctly', () => {
      const discount = { customerTags: ['VIP', 'GOLD'] };
      
      expect(calculator.isCustomerEligible(discount, { tags: ['VIP'] })).toBe(true);
      expect(calculator.isCustomerEligible(discount, { tags: ['SILVER'] })).toBe(false);
      expect(calculator.isCustomerEligible(discount, {})).toBe(false);
    });

    it('checks minimum purchase amount', () => {
      const discount = { minimumPurchase: 5000 };
      
      expect(calculator.isCustomerEligible(discount, { cartTotal: 6000 })).toBe(true);
      expect(calculator.isCustomerEligible(discount, { cartTotal: 4000 })).toBe(false);
    });

    it('checks customer segment', () => {
      const discount = { customerSegment: 'NEW' };
      
      expect(calculator.isCustomerEligible(discount, { orderCount: 0 })).toBe(true);
      expect(calculator.isCustomerEligible(discount, { orderCount: 5 })).toBe(false);
    });
  });

  describe('matchesSegment', () => {
    it.each([
      ['NEW', { orderCount: 0 }, true],
      ['NEW', { orderCount: 1 }, false],
      ['RETURNING', { orderCount: 5 }, true],
      ['RETURNING', { orderCount: 0 }, false],
      ['VIP', { totalSpent: 150000 }, true],
      ['VIP', { totalSpent: 50000 }, false],
      ['UNKNOWN', {}, false],
    ])('segment %s with data %o returns %s', (segment, customerData, expected) => {
      expect(calculator.matchesSegment(customerData, segment)).toBe(expected);
    });
  });

  describe('formatPrice', () => {
    it('formats USD correctly', () => {
      expect(calculator.formatPrice(10000)).toBe('$100.00');
      expect(calculator.formatPrice(9999)).toBe('$99.99');
      expect(calculator.formatPrice(0)).toBe('$0.00');
    });

    it('formats other currencies', () => {
      expect(calculator.formatPrice(10000, 'EUR')).toBe('€100.00');
      expect(calculator.formatPrice(10000, 'GBP')).toBe('£100.00');
    });
  });
});
```

## 5. Integration Testing: Bridging Your App and Shopify

Integration testing in Shopify development requires a different mindset than what you might be used to in Laravel or Spring Boot. Instead of testing against your own database with transactions you can roll back, you're testing against external APIs that you need to mock carefully. Let me show you how to approach this effectively.

```js
// File: app/webhooks/order-fulfillment.server.js
// This handles order fulfillment webhooks from Shopify

import crypto from 'crypto';
import { json } from '@remix-run/node';
import { unauthenticated } from '../shopify.server';
import { db } from '../db.server';

/**
 * Process order fulfillment webhook from Shopify
 * Similar to Laravel's webhook controllers but with Shopify-specific verification
 */
export async function processOrderFulfillment(request) {
  const rawBody = await request.text();
  const signature = request.headers.get('X-Shopify-Hmac-Sha256');
  
  // Step 1: Verify webhook authenticity (critical for security)
  if (!verifyWebhookSignature(rawBody, signature)) {
    console.error('Invalid webhook signature');
    return json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  // Step 2: Parse the webhook payload
  const orderData = JSON.parse(rawBody);
  
  try {
    // Step 3: Process the fulfillment
    await handleFulfillment(orderData);
    
    // Step 4: Send notifications if needed
    await sendFulfillmentNotifications(orderData);
    
    return json({ success: true }, { status: 200 });
  } catch (error) {
    console.error('Failed to process fulfillment:', error);
    // Shopify will retry webhooks that return 5xx errors
    return json({ error: 'Processing failed' }, { status: 500 });
  }
}

/**
 * Verify webhook signature using HMAC
 * This is critical for security - never skip this in production!
 */
export function verifyWebhookSignature(rawBody, signature) {
  const secret = process.env.SHOPIFY_WEBHOOK_SECRET;
  
  if (!secret || !signature) {
    return false;
  }
  
  const hash = crypto
    .createHmac('sha256', secret)
    .update(rawBody, 'utf8')
    .digest('base64');
    
  return hash === signature;
}

/**
 * Handle the fulfillment logic
 */
async function handleFulfillment(orderData) {
  // Update local database
  await db.fulfillment.upsert({
    where: { orderId: orderData.id },
    update: {
      status: 'fulfilled',
      trackingNumber: orderData.fulfillments?.[0]?.tracking_number,
      trackingUrl: orderData.fulfillments?.[0]?.tracking_urls?.[0],
      fulfilledAt: new Date(orderData.fulfillments?.[0]?.created_at),
    },
    create: {
      orderId: orderData.id,
      orderNumber: orderData.order_number,
      status: 'fulfilled',
      trackingNumber: orderData.fulfillments?.[0]?.tracking_number,
      trackingUrl: orderData.fulfillments?.[0]?.tracking_urls?.[0],
      fulfilledAt: new Date(orderData.fulfillments?.[0]?.created_at),
      customerEmail: orderData.email,
    },
  });
  
  // Update inventory if needed
  for (const lineItem of orderData.line_items) {
    await updateInventory(lineItem.variant_id, lineItem.quantity);
  }
}

/**
 * Update inventory counts
 */
async function updateInventory(variantId, quantity) {
  const { admin } = await unauthenticated.admin(process.env.SHOP_DOMAIN);
  
  const response = await admin.graphql(
    `#graphql
    mutation adjustInventory($input: InventoryAdjustQuantitiesInput!) {
      inventoryAdjustQuantities(input: $input) {
        inventoryAdjustmentGroup {
          createdAt
          reason
        }
        userErrors {
          field
          message
        }
      }
    }`,
    {
      variables: {
        input: {
          reason: "Order fulfillment",
          changes: [{
            variantId,
            quantityAdjustment: -quantity,
          }]
        }
      }
    }
  );
  
  const result = response.json();
  
  if (result.data?.inventoryAdjustQuantities?.userErrors?.length > 0) {
    throw new Error(`Inventory update failed: ${result.data.inventoryAdjustQuantities.userErrors[0].message}`);
  }
  
  return result;
}

/**
 * Send customer notifications
 */
async function sendFulfillmentNotifications(orderData) {
  // Here you would integrate with your notification service
  // For example, send an email via SendGrid, Postmark, etc.
  console.log(`Sending fulfillment notification for order ${orderData.order_number}`);
}

// ============================================
// File: app/webhooks/order-fulfillment.server.test.js
// Integration tests for webhook processing

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { processOrderFulfillment, verifyWebhookSignature } from './order-fulfillment.server';
import { db } from '../db.server';
import crypto from 'crypto';

// Mock the database - similar to Laravel's RefreshDatabase trait
vi.mock('../db.server', () => ({
  db: {
    fulfillment: {
      upsert: vi.fn(),
    },
  },
}));

// Mock the Shopify admin client
vi.mock('../shopify.server', () => ({
  unauthenticated: {
    admin: vi.fn(() => ({
      admin: {
        graphql: vi.fn(),
      },
    })),
  },
}));

describe('Order Fulfillment Webhook Integration Tests', () => {
  let mockRequest;
  const webhookSecret = 'test_webhook_secret';
  const originalEnv = process.env;
  
  beforeEach(() => {
    // Set up test environment variables
    process.env = {
      ...originalEnv,
      SHOPIFY_WEBHOOK_SECRET: webhookSecret,
      SHOP_DOMAIN: 'test-shop.myshopify.com',
    };
    
    // Reset all mocks before each test
    vi.clearAllMocks();
  });
  
  afterEach(() => {
    // Restore original environment
    process.env = originalEnv;
  });
  
  describe('Webhook Signature Verification', () => {
    it('verifies valid webhook signature', () => {
      const rawBody = '{"test": "data"}';
      const validSignature = crypto
        .createHmac('sha256', webhookSecret)
        .update(rawBody, 'utf8')
        .digest('base64');
      
      expect(verifyWebhookSignature(rawBody, validSignature)).toBe(true);
    });
    
    it('rejects invalid webhook signature', () => {
      const rawBody = '{"test": "data"}';
      const invalidSignature = 'invalid_signature';
      
      expect(verifyWebhookSignature(rawBody, invalidSignature)).toBe(false);
    });
    
    it('rejects when secret is missing', () => {
      delete process.env.SHOPIFY_WEBHOOK_SECRET;
      
      expect(verifyWebhookSignature('body', 'signature')).toBe(false);
    });
  });
  
  describe('processOrderFulfillment', () => {
    const validOrderData = {
      id: 'gid://shopify/Order/123456',
      order_number: '1001',
      email: 'customer@example.com',
      fulfillments: [
        {
          tracking_number: 'TRACK123',
          tracking_urls: ['https://tracking.example.com/TRACK123'],
          created_at: '2025-09-24T10:00:00Z',
        },
      ],
      line_items: [
        {
          variant_id: 'gid://shopify/ProductVariant/789',
          quantity: 2,
        },
      ],
    };
    
    function createMockRequest(body, signature) {
      return {
        text: vi.fn().mockResolvedValue(JSON.stringify(body)),
        headers: {
          get: vi.fn((header) => {
            if (header === 'X-Shopify-Hmac-Sha256') return signature;
            return null;
          }),
        },
      };
    }
    
    it('processes valid webhook successfully', async () => {
      const rawBody = JSON.stringify(validOrderData);
      const validSignature = crypto
        .createHmac('sha256', webhookSecret)
        .update(rawBody, 'utf8')
        .digest('base64');
      
      mockRequest = createMockRequest(validOrderData, validSignature);
      
      // Mock successful GraphQL response for inventory update
      const { unauthenticated } = await import('../shopify.server');
      const mockGraphql = vi.fn().mockResolvedValue({
        json: () => ({
          data: {
            inventoryAdjustQuantities: {
              inventoryAdjustmentGroup: {
                createdAt: '2025-09-24T10:00:00Z',
                reason: 'Order fulfillment',
              },
              userErrors: [],
            },
          },
        }),
      });
      
      unauthenticated.admin.mockResolvedValue({
        admin: { graphql: mockGraphql },
      });
      
      const response = await processOrderFulfillment(mockRequest);
      const responseData = await response.json();
      
      // Verify success response
      expect(response.status).toBe(200);
      expect(responseData).toEqual({ success: true });
      
      // Verify database was updated
      expect(db.fulfillment.upsert).toHaveBeenCalledWith({
        where: { orderId: validOrderData.id },
        update: expect.objectContaining({
          status: 'fulfilled',
          trackingNumber: 'TRACK123',
          trackingUrl: 'https://tracking.example.com/TRACK123',
        }),
        create: expect.objectContaining({
          orderId: validOrderData.id,
          orderNumber: '1001',
          customerEmail: 'customer@example.com',
        }),
      });
      
      // Verify inventory was updated
      expect(mockGraphql).toHaveBeenCalledWith(
        expect.stringContaining('inventoryAdjustQuantities'),
        expect.objectContaining({
          variables: {
            input: {
              reason: 'Order fulfillment',
              changes: [{
                variantId: 'gid://shopify/ProductVariant/789',
                quantityAdjustment: -2,
              }],
            },
          },
        })
      );
    });
    
    it('returns 401 for invalid signature', async () => {
      mockRequest = createMockRequest(validOrderData, 'invalid_signature');
      
      const response = await processOrderFulfillment(mockRequest);
      const responseData = await response.json();
      
      expect(response.status).toBe(401);
      expect(responseData).toEqual({ error: 'Unauthorized' });
      
      // Verify database was NOT updated
      expect(db.fulfillment.upsert).not.toHaveBeenCalled();
    });
    
    it('returns 500 when processing fails', async () => {
      const rawBody = JSON.stringify(validOrderData);
      const validSignature = crypto
        .createHmac('sha256', webhookSecret)
        .update(rawBody, 'utf8')
        .digest('base64');
      
      mockRequest = createMockRequest(validOrderData, validSignature);
      
      // Mock database error
      db.fulfillment.upsert.mockRejectedValue(new Error('Database connection failed'));
      
      const response = await processOrderFulfillment(mockRequest);
      const responseData = await response.json();
      
      expect(response.status).toBe(500);
      expect(responseData).toEqual({ error: 'Processing failed' });
    });
    
    it('handles inventory update errors gracefully', async () => {
      const rawBody = JSON.stringify(validOrderData);
      const validSignature = crypto
        .createHmac('sha256', webhookSecret)
        .update(rawBody, 'utf8')
        .digest('base64');
      
      mockRequest = createMockRequest(validOrderData, validSignature);
      
      // Mock GraphQL error response
      const { unauthenticated } = await import('../shopify.server');
      const mockGraphql = vi.fn().mockResolvedValue({
        json: () => ({
          data: {
            inventoryAdjustQuantities: {
              userErrors: [{
                field: 'variantId',
                message: 'Variant not found',
              }],
            },
          },
        }),
      });
      
      unauthenticated.admin.mockResolvedValue({
        admin: { graphql: mockGraphql },
      });
      
      const response = await processOrderFulfillment(mockRequest);
      
      // Should return 500 due to inventory update failure
      expect(response.status).toBe(500);
    });
  });
  
  describe('GraphQL Mutation Testing', () => {
    it('constructs inventory adjustment mutation correctly', async () => {
      const { unauthenticated } = await import('../shopify.server');
      const mockGraphql = vi.fn().mockResolvedValue({
        json: () => ({
          data: {
            inventoryAdjustQuantities: {
              inventoryAdjustmentGroup: {
                createdAt: '2025-09-24T10:00:00Z',
              },
              userErrors: [],
            },
          },
        }),
      });
      
      unauthenticated.admin.mockResolvedValue({
        admin: { graphql: mockGraphql },
      });
      
      // Import the actual function to test GraphQL construction
      const { updateInventory } = await import('./order-fulfillment.server');
      
      await updateInventory('gid://shopify/ProductVariant/123', 5);
      
      // Verify the GraphQL mutation was called with correct structure
      expect(mockGraphql).toHaveBeenCalledWith(
        expect.stringContaining('mutation adjustInventory'),
        expect.objectContaining({
          variables: {
            input: {
              reason: 'Order fulfillment',
              changes: [{
                variantId: 'gid://shopify/ProductVariant/123',
                quantityAdjustment: -5,
              }],
            },
          },
        })
      );
    });
  });
});
```

Now that we've covered integration testing, let me help you understand how this differs from what you're used to in Laravel and Spring Boot. In Laravel, you might use the `RefreshDatabase` trait to ensure each test starts with a clean slate, and in Spring Boot, you'd use `@Transactional` to roll back changes after each test. In Shopify development, we don't have that luxury since we're working with external APIs, so we rely heavily on mocking to ensure our tests are predictable and fast.

The integration test I showed you tests the critical path of webhook processing, which is one of the most important aspects of Shopify app development. Think of webhooks as Shopify's way of implementing the Observer pattern - when something happens in a store (like an order being fulfilled), Shopify notifies your app so you can react accordingly. The signature verification is absolutely critical here, as it's your defense against malicious actors trying to send fake webhooks to your app.

## 6. End-to-End Testing: The Complete User Journey

End-to-end testing in Shopify development is where things get really interesting. Unlike unit and integration tests that focus on specific components, E2E tests validate entire user workflows. This is similar to what you might do with Laravel Dusk or Selenium in Spring Boot, but with some Shopify-specific considerations.

```js
// File: tests/e2e/app-installation.spec.js
// End-to-end test for complete app installation and setup flow
// This is similar to Laravel Dusk tests but for Shopify apps

import { test, expect } from '@playwright/test';
import { createDevelopmentStore, cleanupStore } from '../helpers/store-helpers';
import { generateTestData } from '../helpers/test-data';

/**
 * These tests run against actual development stores
 * Think of this as your acceptance testing suite
 */
test.describe('App Installation and Setup', () => {
  let storeUrl;
  let storeAccessToken;
  
  // Similar to Laravel's setUp() method
  test.beforeAll(async () => {
    // Create a fresh development store for testing
    const store = await createDevelopmentStore({
      name: `test-store-${Date.now()}`,
      type: 'development',
      includeTestData: true,
    });
    
    storeUrl = store.url;
    storeAccessToken = store.accessToken;
  });
  
  // Similar to Laravel's tearDown() method
  test.afterAll(async () => {
    // Clean up the test store
    await cleanupStore(storeUrl);
  });
  
  test('completes full app installation flow', async ({ page }) => {
    // Step 1: Navigate to app installation URL
    const appUrl = process.env.APP_URL || 'http://localhost:3000';
    const installUrl = `${appUrl}/auth?shop=${storeUrl}`;
    
    await page.goto(installUrl);
    
    // Step 2: Verify we're redirected to Shopify OAuth screen
    await expect(page).toHaveURL(/.*admin.shopify.com.*oauth.*/);
    
    // Step 3: Log in to the store (if not already logged in)
    const needsLogin = await page.locator('#account_email').isVisible();
    if (needsLogin) {
      await page.fill('#account_email', process.env.TEST_STORE_EMAIL);
      await page.fill('#account_password', process.env.TEST_STORE_PASSWORD);
      await page.click('button[type="submit"]');
      
      // Wait for login to complete
      await page.waitForURL(/.*oauth.*/);
    }
    
    // Step 4: Accept app permissions
    const installButton = page.locator('button:has-text("Install app")');
    await expect(installButton).toBeVisible();
    
    // Verify requested scopes are displayed
    const scopesList = page.locator('[data-testid="oauth-scopes-list"]');
    await expect(scopesList).toContainText('Read products');
    await expect(scopesList).toContainText('Write orders');
    
    await installButton.click();
    
    // Step 5: Verify redirect to app after installation
    await page.waitForURL(`${appUrl}/**`);
    
    // Step 6: Verify app loads correctly
    await expect(page.locator('h1')).toContainText('Welcome to Your App');
    
    // Step 7: Verify session is established
    const appBridgeInitialized = await page.evaluate(() => {
      return window.shopify && window.shopify.config && window.shopify.config.apiKey;
    });
    expect(appBridgeInitialized).toBeTruthy();
  });
  
  test('handles billing acceptance flow', async ({ page }) => {
    // Navigate to app (assuming already installed from previous test)
    await page.goto(`https://${storeUrl}/admin/apps/${process.env.APP_HANDLE}`);
    
    // Check if billing prompt appears
    const billingPrompt = page.locator('[data-testid="billing-prompt"]');
    if (await billingPrompt.isVisible()) {
      // Click on select plan button
      await page.click('button:has-text("Select Plan")');
      
      // Should redirect to Shopify billing confirmation
      await page.waitForURL(/.*admin.shopify.com.*charges.*/);
      
      // Approve the charge (test mode)
      await page.click('button:has-text("Approve")');
      
      // Should redirect back to app
      await page.waitForURL(/.*admin\/apps.*/);
    }
    
    // Verify app is now fully accessible
    await expect(page.locator('[data-testid="app-dashboard"]')).toBeVisible();
  });
  
  test('creates and manages products through the app', async ({ page }) => {
    // This test validates the core functionality of your app
    await page.goto(`https://${storeUrl}/admin/apps/${process.env.APP_HANDLE}`);
    
    // Navigate to products section
    await page.click('nav a:has-text("Products")');
    
    // Click create product button
    await page.click('button:has-text("Create Product")');
    
    // Fill in product details
    const productData = generateTestData.product();
    await page.fill('input[name="title"]', productData.title);
    await page.fill('textarea[name="description"]', productData.description);
    await page.fill('input[name="price"]', productData.price);
    
    // Select product type
    await page.selectOption('select[name="productType"]', 'physical');
    
    // Upload product image (if your app supports it)
    const fileInput = page.locator('input[type="file"]');
    if (await fileInput.isVisible()) {
      await fileInput.setInputFiles('tests/fixtures/test-product-image.jpg');
    }
    
    // Save the product
    await page.click('button:has-text("Save Product")');
    
    // Verify success message
    await expect(page.locator('.Polaris-Banner--statusSuccess')).toBeVisible();
    await expect(page.locator('.Polaris-Banner__Content')).toContainText('Product created successfully');
    
    // Verify product appears in list
    await page.click('nav a:has-text("Products")');
    await expect(page.locator(`text="${productData.title}"`)).toBeVisible();
  });
  
  test('handles webhook processing correctly', async ({ page, request }) => {
    // This tests that your app responds correctly to Shopify webhooks
    const webhookEndpoint = `${process.env.APP_URL}/webhooks/orders/create`;
    
    // Create a test order through Shopify Admin API
    const orderResponse = await request.post(
      `https://${storeUrl}/admin/api/2025-07/orders.json`,
      {
        headers: {
          'X-Shopify-Access-Token': storeAccessToken,
          'Content-Type': 'application/json',
        },
        data: {
          order: {
            line_items: [
              {
                variant_id: 447654529,
                quantity: 1,
              },
            ],
            customer: {
              email: 'test@example.com',
            },
            financial_status: 'pending',
            test: true, // Important: mark as test order
          },
        },
      }
    );
    
    const order = await orderResponse.json();
    
    // Navigate to app dashboard
    await page.goto(`https://${storeUrl}/admin/apps/${process.env.APP_HANDLE}/dashboard`);
    
    // Wait for webhook to be processed (your app should update UI)
    await page.waitForTimeout(5000); // Give webhook time to process
    
    // Verify order appears in app's order list
    await page.click('nav a:has-text("Orders")');
    await expect(page.locator(`text="#${order.order.order_number}"`)).toBeVisible();
    
    // Verify order details are correct
    await page.click(`text="#${order.order.order_number}"`);
    await expect(page.locator('[data-testid="order-customer-email"]')).toContainText('test@example.com');
    await expect(page.locator('[data-testid="order-status"]')).toContainText('Pending');
  });
});

// ============================================
// File: tests/e2e/checkout-extension.spec.js
// Test checkout UI extensions

test.describe('Checkout UI Extension', () => {
  test('displays custom field in checkout', async ({ page }) => {
    // Create a test cart
    await page.goto(`https://${storeUrl}`);
    
    // Add a product to cart
    await page.click('[data-testid="product-card"]:first-child');
    await page.click('button:has-text("Add to Cart")');
    
    // Navigate to checkout
    await page.click('button:has-text("Checkout")');
    
    // Verify our extension loads
    const extensionContainer = page.locator('[data-extension-target="purchase.checkout.block.render"]');
    await expect(extensionContainer).toBeVisible();
    
    // Verify custom field is present
    const customField = extensionContainer.locator('input[name="gift_message"]');
    await expect(customField).toBeVisible();
    
    // Fill in the custom field
    await customField.fill('Happy Birthday!');
    
    // Complete checkout (test mode)
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="firstName"]', 'Test');
    await page.fill('input[name="lastName"]', 'Customer');
    await page.fill('input[name="address1"]', '123 Test St');
    await page.fill('input[name="city"]', 'Test City');
    await page.selectOption('select[name="country"]', 'US');
    await page.selectOption('select[name="province"]', 'CA');
    await page.fill('input[name="postalCode"]', '90210');
    
    // Continue to payment
    await page.click('button:has-text("Continue to payment")');
    
    // Use test payment
    await page.click('label:has-text("Bogus Gateway")');
    
    // Complete order
    await page.click('button:has-text("Pay now")');
    
    // Verify order confirmation shows our custom field
    await expect(page.locator('[data-testid="gift-message-confirmation"]')).toContainText('Happy Birthday!');
  });
});

// ============================================
// File: tests/helpers/store-helpers.js
// Helper functions for managing test stores

import fetch from 'node-fetch';

/**
 * Create a development store for testing
 * This uses the Partner API to create stores programmatically
 */
export async function createDevelopmentStore(options) {
  const response = await fetch('https://partners.shopify.com/api/unstable/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Access-Token': process.env.PARTNER_API_TOKEN,
    },
    body: JSON.stringify({
      query: `
        mutation createDevelopmentStore($input: DevelopmentStoreInput!) {
          developmentStoreCreate(input: $input) {
            store {
              id
              url
              name
            }
            userErrors {
              field
              message
            }
          }
        }
      `,
      variables: {
        input: {
          name: options.name,
          storeType: 'TEST_STORE',
          includeTestData: options.includeTestData || false,
        },
      },
    }),
  });
  
  const result = await response.json();
  
  if (result.data.developmentStoreCreate.userErrors.length > 0) {
    throw new Error(`Failed to create store: ${result.data.developmentStoreCreate.userErrors[0].message}`);
  }
  
  const store = result.data.developmentStoreCreate.store;
  
  // Get access token for the store
  const accessToken = await getStoreAccessToken(store.url);
  
  return {
    ...store,
    accessToken,
  };
}

/**
 * Clean up test store after tests
 */
export async function cleanupStore(storeUrl) {
  // Archive the development store
  await fetch('https://partners.shopify.com/api/unstable/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Access-Token': process.env.PARTNER_API_TOKEN,
    },
    body: JSON.stringify({
      query: `
        mutation archiveStore($storeUrl: String!) {
          developmentStoreArchive(storeUrl: $storeUrl) {
            userErrors {
              field
              message
            }
          }
        }
      `,
      variables: {
        storeUrl,
      },
    }),
  });
}

/**
 * Get access token for API calls to the test store
 */
async function getStoreAccessToken(storeUrl) {
  // In a real scenario, you'd implement OAuth flow
  // For testing, you might use a pre-configured token
  return process.env.TEST_STORE_ACCESS_TOKEN;
}

// ============================================
// File: playwright.config.js
// Playwright configuration for E2E tests

export default {
  testDir: './tests/e2e',
  timeout: 60000, // 60 seconds per test
  retries: 2, // Retry failed tests twice
  workers: 1, // Run tests sequentially for Shopify
  use: {
    baseURL: process.env.APP_URL || 'http://localhost:3000',
    headless: process.env.CI === 'true', // Run headless in CI
    viewport: { width: 1280, height: 720 },
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  globalSetup: './tests/e2e/global-setup.js',
  globalTeardown: './tests/e2e/global-teardown.js',
};
```

Let me explain what's happening in these end-to-end tests and how they differ from what you might be familiar with in your Laravel and Spring Boot experience. When you write feature tests in Laravel using PHPUnit, you often test against your actual database but with transactions that roll back after each test. In Spring Boot with @SpringBootTest, you might spin up an embedded H2 database for testing. 

In Shopify development, end-to-end testing requires a fundamentally different approach because you're testing against actual Shopify stores, even if they're development stores. This means your tests are hitting real APIs, processing real webhooks, and dealing with eventual consistency issues that you wouldn't encounter in traditional monolithic applications. The test I've shown you actually creates a development store, installs your app on it, and validates that everything works as expected from the user's perspective.

The Playwright tests simulate exactly what a merchant would do when installing and using your app. This is crucial because Shopify apps have complex installation flows involving OAuth, billing acceptance, and permission grants that can't be properly tested with unit or integration tests alone.

## 7. API Mocking: The Foundation of Reliable Tests

One of the biggest challenges when moving from Laravel or Spring Boot to Shopify development is learning how to effectively mock Shopify's APIs. In Laravel, you might mock Eloquent models or use database factories. In Spring Boot, you'd use @MockBean or Mockito. In Shopify development, you need to mock GraphQL responses, REST API calls, and webhook payloads in a way that accurately represents what Shopify actually sends.

Let me show you a comprehensive mocking strategy that will make your tests both reliable and maintainable:

```js
// File: test-utils/shopify-test-factory.js
// Comprehensive mock factory for Shopify API responses
// This is similar to Laravel's factory pattern but for external API responses

/**
 * ShopifyTestFactory provides consistent, realistic mock data for testing
 * Think of this as your database factory but for API responses
 */
export class ShopifyTestFactory {
  /**
   * Generate a mock product with all the fields Shopify actually returns
   * This ensures your tests are realistic and catch issues early
   */
  static product(overrides = {}) {
    const id = overrides.id || `gid://shopify/Product/${this.randomId()}`;
    const defaults = {
      id,
      title: 'Test Product',
      description: 'A test product description',
      handle: 'test-product',
      vendor: 'Test Vendor',
      productType: 'Test Type',
      status: 'ACTIVE',
      publishedAt: '2025-09-24T10:00:00Z',
      createdAt: '2025-09-24T09:00:00Z',
      updatedAt: '2025-09-24T10:00:00Z',
      tags: ['test', 'sample'],
      options: [
        {
          id: `gid://shopify/ProductOption/${this.randomId()}`,
          name: 'Size',
          values: ['Small', 'Medium', 'Large'],
        },
      ],
      variants: {
        edges: [
          {
            node: this.productVariant({ productId: id }),
          },
        ],
      },
      images: {
        edges: [
          {
            node: {
              id: `gid://shopify/ProductImage/${this.randomId()}`,
              url: 'https://cdn.shopify.com/s/files/1/test/image.jpg',
              altText: 'Test product image',
            },
          },
        ],
      },
      priceRangeV2: {
        minVariantPrice: {
          amount: '10.00',
          currencyCode: 'USD',
        },
        maxVariantPrice: {
          amount: '20.00',
          currencyCode: 'USD',
        },
      },
    };
    
    return this.deepMerge(defaults, overrides);
  }
  
  /**
   * Generate a mock product variant
   */
  static productVariant(overrides = {}) {
    return {
      id: `gid://shopify/ProductVariant/${this.randomId()}`,
      title: 'Default',
      sku: 'TEST-SKU-001',
      price: '15.00',
      compareAtPrice: '20.00',
      availableForSale: true,
      inventoryQuantity: 100,
      weight: 1.5,
      weightUnit: 'POUNDS',
      ...overrides,
    };
  }
  
  /**
   * Generate a mock order with realistic data
   */
  static order(overrides = {}) {
    const orderId = `gid://shopify/Order/${this.randomId()}`;
    const customerId = `gid://shopify/Customer/${this.randomId()}`;
    
    return {
      id: orderId,
      name: '#1001',
      orderNumber: 1001,
      createdAt: '2025-09-24T10:00:00Z',
      updatedAt: '2025-09-24T10:00:00Z',
      test: true,
      fulfillmentStatus: 'UNFULFILLED',
      financialStatus: 'PENDING',
      customer: this.customer({ id: customerId }),
      lineItems: {
        edges: [
          {
            node: this.lineItem({ orderId }),
          },
        ],
      },
      totalPriceSet: {
        shopMoney: {
          amount: '115.00',
          currencyCode: 'USD',
        },
      },
      subtotalPriceSet: {
        shopMoney: {
          amount: '100.00',
          currencyCode: 'USD',
        },
      },
      totalTaxSet: {
        shopMoney: {
          amount: '15.00',
          currencyCode: 'USD',
        },
      },
      shippingAddress: this.address(),
      billingAddress: this.address(),
      ...overrides,
    };
  }
  
  /**
   * Generate a mock customer
   */
  static customer(overrides = {}) {
    return {
      id: `gid://shopify/Customer/${this.randomId()}`,
      email: 'test@example.com',
      firstName: 'Test',
      lastName: 'Customer',
      phone: '+1234567890',
      acceptsMarketing: true,
      createdAt: '2025-09-01T10:00:00Z',
      updatedAt: '2025-09-24T10:00:00Z',
      ordersCount: 5,
      totalSpent: {
        amount: '500.00',
        currencyCode: 'USD',
      },
      tags: ['vip', 'repeat-customer'],
      ...overrides,
    };
  }
  
  /**
   * Generate mock GraphQL responses
   */
  static graphqlResponse(data, errors = null) {
    const response = {
      data,
      extensions: {
        cost: {
          requestedQueryCost: 10,
          actualQueryCost: 8,
          throttleStatus: {
            maximumAvailable: 2000,
            currentlyAvailable: 1992,
            restoreRate: 100,
          },
        },
      },
    };
    
    if (errors) {
      response.errors = errors;
    }
    
    return response;
  }
  
  /**
   * Generate GraphQL error responses for testing error handling
   */
  static graphqlError(type = 'THROTTLED') {
    const errorTypes = {
      THROTTLED: {
        message: 'Throttled',
        extensions: {
          code: 'THROTTLED',
          documentation: 'https://shopify.dev/api/usage/rate-limits',
          retryAfter: 2.0,
        },
      },
      NOT_FOUND: {
        message: 'Product not found',
        extensions: {
          code: 'NOT_FOUND',
        },
        path: ['product'],
      },
      INVALID_INPUT: {
        message: 'Variable $id of type ID! was provided invalid value',
        extensions: {
          code: 'INVALID_INPUT',
          argumentName: 'id',
        },
      },
      ACCESS_DENIED: {
        message: 'Access denied',
        extensions: {
          code: 'ACCESS_DENIED',
          requiredScope: 'write_products',
        },
      },
    };
    
    return [errorTypes[type] || errorTypes.NOT_FOUND];
  }
  
  /**
   * Generate webhook payloads
   */
  static webhookPayload(topic, overrides = {}) {
    const payloads = {
      'orders/create': this.order(overrides),
      'orders/updated': this.order(overrides),
      'products/create': this.product(overrides),
      'products/update': this.product(overrides),
      'customers/create': this.customer(overrides),
      'app/uninstalled': {
        id: 12345678,
        name: 'Test Shop',
        email: 'shop@example.com',
        domain: 'test-shop.myshopify.com',
        ...overrides,
      },
    };
    
    return payloads[topic] || {};
  }
  
  /**
   * Generate mock webhook headers with valid HMAC
   */
  static webhookHeaders(payload, secret = 'test_secret') {
    const crypto = require('crypto');
    const rawBody = typeof payload === 'string' ? payload : JSON.stringify(payload);
    
    const hmac = crypto
      .createHmac('sha256', secret)
      .update(rawBody, 'utf8')
      .digest('base64');
    
    return {
      'X-Shopify-Topic': 'orders/create',
      'X-Shopify-Hmac-Sha256': hmac,
      'X-Shopify-Shop-Domain': 'test-shop.myshopify.com',
      'X-Shopify-Webhook-Id': this.randomId(),
      'X-Shopify-API-Version': '2025-07',
      'Content-Type': 'application/json',
    };
  }
  
  // Utility methods
  
  static randomId() {
    return Math.floor(Math.random() * 1000000000).toString();
  }
  
  static address(overrides = {}) {
    return {
      address1: '123 Test St',
      address2: 'Suite 100',
      city: 'Test City',
      province: 'California',
      provinceCode: 'CA',
      country: 'United States',
      countryCode: 'US',
      zip: '90210',
      phone: '+1234567890',
      ...overrides,
    };
  }
  
  static lineItem(overrides = {}) {
    return {
      id: `gid://shopify/LineItem/${this.randomId()}`,
      title: 'Test Product',
      quantity: 2,
      variant: this.productVariant(),
      price: {
        amount: '50.00',
        currencyCode: 'USD',
      },
      ...overrides,
    };
  }
  
  static deepMerge(target, source) {
    const output = { ...target };
    if (isObject(target) && isObject(source)) {
      Object.keys(source).forEach(key => {
        if (isObject(source[key])) {
          if (!(key in target)) {
            Object.assign(output, { [key]: source[key] });
          } else {
            output[key] = this.deepMerge(target[key], source[key]);
          }
        } else {
          Object.assign(output, { [key]: source[key] });
        }
      });
    }
    return output;
  }
}

function isObject(item) {
  return item && typeof item === 'object' && !Array.isArray(item);
}

// ============================================
// File: test-utils/mock-shopify-admin.js
// Mock implementation of Shopify Admin client for testing

import { ShopifyTestFactory } from './shopify-test-factory';

/**
 * MockShopifyAdmin provides a complete mock of the Shopify Admin API client
 * This allows you to test without hitting real APIs
 */
export class MockShopifyAdmin {
  constructor() {
    this.products = new Map();
    this.orders = new Map();
    this.customers = new Map();
    this.callHistory = [];
    this.shouldThrottle = false;
    this.errorMode = null;
  }
  
  /**
   * Mock GraphQL method that simulates Shopify's GraphQL API
   */
  async graphql(query, options = {}) {
    // Track the call for assertions
    this.callHistory.push({ query, variables: options.variables });
    
    // Simulate throttling if enabled
    if (this.shouldThrottle) {
      return {
        json: () => ShopifyTestFactory.graphqlResponse(null, 
          ShopifyTestFactory.graphqlError('THROTTLED')
        ),
      };
    }
    
    // Simulate errors if error mode is set
    if (this.errorMode) {
      return {
        json: () => ShopifyTestFactory.graphqlResponse(null, 
          ShopifyTestFactory.graphqlError(this.errorMode)
        ),
      };
    }
    
    // Parse the query to determine what's being requested
    const operation = this.parseGraphQLOperation(query);
    
    // Route to appropriate handler
    switch (operation.type) {
      case 'query':
        return this.handleQuery(operation, options.variables);
      case 'mutation':
        return this.handleMutation(operation, options.variables);
      default:
        throw new Error(`Unknown operation type: ${operation.type}`);
    }
  }
  
  /**
   * Handle GraphQL queries
   */
  async handleQuery(operation, variables) {
    const handlers = {
      product: () => {
        const product = this.products.get(variables.id) || 
          ShopifyTestFactory.product({ id: variables.id });
        return { product };
      },
      products: () => {
        const products = Array.from(this.products.values()).slice(0, variables.first || 10);
        return {
          products: {
            edges: products.map(node => ({ node })),
            pageInfo: {
              hasNextPage: products.length === (variables.first || 10),
            },
          },
        };
      },
      order: () => {
        const order = this.orders.get(variables.id) || 
          ShopifyTestFactory.order({ id: variables.id });
        return { order };
      },
      customer: () => {
        const customer = this.customers.get(variables.id) || 
          ShopifyTestFactory.customer({ id: variables.id });
        return { customer };
      },
    };
    
    const handler = handlers[operation.name];
    if (!handler) {
      throw new Error(`No handler for query: ${operation.name}`);
    }
    
    const data = await handler();
    return {
      json: () => ShopifyTestFactory.graphqlResponse(data),
    };
  }
  
  /**
   * Handle GraphQL mutations
   */
  async handleMutation(operation, variables) {
    const handlers = {
      productCreate: () => {
        const product = ShopifyTestFactory.product(variables.input);
        this.products.set(product.id, product);
        return {
          productCreate: {
            product,
            userErrors: [],
          },
        };
      },
      productUpdate: () => {
        const existing = this.products.get(variables.input.id);
        const updated = { ...existing, ...variables.input };
        this.products.set(updated.id, updated);
        return {
          productUpdate: {
            product: updated,
            userErrors: [],
          },
        };
      },
      orderUpdate: () => {
        const existing = this.orders.get(variables.input.id);
        const updated = { ...existing, ...variables.input };
        this.orders.set(updated.id, updated);
        return {
          orderUpdate: {
            order: updated,
            userErrors: [],
          },
        };
      },
    };
    
    const handler = handlers[operation.name];
    if (!handler) {
      throw new Error(`No handler for mutation: ${operation.name}`);
    }
    
    const data = await handler();
    return {
      json: () => ShopifyTestFactory.graphqlResponse(data),
    };
  }
  
  /**
   * Parse GraphQL query to extract operation details
   */
  parseGraphQLOperation(query) {
    // Simple parser for testing - in production you'd use graphql-tag
    const isQuery = query.includes('query ');
    const isMutation = query.includes('mutation ');
    
    if (isMutation) {
      const match = query.match(/mutation\s+(\w+)/);
      return {
        type: 'mutation',
        name: match ? match[1] : 'unknown',
      };
    }
    
    // Extract query name
    const match = query.match(/{\s*(\w+)/);
    return {
      type: 'query',
      name: match ? match[1] : 'unknown',
    };
  }
  
  // Test helper methods
  
  /**
   * Enable throttling for the next N calls
   */
  simulateThrottling(enabled = true) {
    this.shouldThrottle = enabled;
  }
  
  /**
   * Simulate specific error conditions
   */
  simulateError(errorType) {
    this.errorMode = errorType;
  }
  
  /**
   * Reset all mock data
   */
  reset() {
    this.products.clear();
    this.orders.clear();
    this.customers.clear();
    this.callHistory = [];
    this.shouldThrottle = false;
    this.errorMode = null;
  }
  
  /**
   * Seed mock data for testing
   */
  seed(data) {
    if (data.products) {
      data.products.forEach(p => this.products.set(p.id, p));
    }
    if (data.orders) {
      data.orders.forEach(o => this.orders.set(o.id, o));
    }
    if (data.customers) {
      data.customers.forEach(c => this.customers.set(c.id, c));
    }
  }
  
  /**
   * Get call history for assertions
   */
  getCallHistory() {
    return this.callHistory;
  }
  
  /**
   * Assert a specific call was made
   */
  assertCalled(queryFragment) {
    const called = this.callHistory.some(call => 
      call.query.includes(queryFragment)
    );
    
    if (!called) {
      throw new Error(`Expected query containing "${queryFragment}" was not called`);
    }
  }
}

// ============================================
// File: vitest.config.js
// Complete Vitest configuration for Shopify app testing

import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    // Test environment
    environment: 'jsdom',
    
    // Setup files
    setupFiles: ['./test-utils/setup.js'],
    
    // Global test utilities
    globals: true,
    
    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'test-utils/',
        '*.config.js',
        'dist/',
        '.shopify/',
      ],
      // Thresholds to enforce
      thresholds: {
        statements: 80,
        branches: 75,
        functions: 80,
        lines: 80,
      },
    },
    
    // Test timeouts
    testTimeout: 10000,
    hookTimeout: 10000,
    
    // Mock configuration
    mockReset: true,
    clearMocks: true,
    restoreMocks: true,
    
    // Retry flaky tests
    retry: process.env.CI ? 2 : 0,
    
    // Reporter configuration
    reporters: process.env.CI ? ['json', 'verbose'] : ['verbose'],
    
    // Watch mode exclusions
    watchExclude: ['node_modules', 'dist', '.shopify'],
  },
  
  // Resolve aliases to match your app structure
  resolve: {
    alias: {
      '~': '/app',
      '@': '/app',
    },
  },
});

// ============================================
// File: test-utils/setup.js
// Global test setup file

import { vi } from 'vitest';
import { MockShopifyAdmin } from './mock-shopify-admin';
import '@testing-library/jest-dom';

// Set up global mocks
global.fetch = vi.fn();

// Mock Shopify App Bridge
global.shopify = {
  config: {
    apiKey: 'test-api-key',
    host: 'test-host',
  },
  app: {
    init: vi.fn(),
  },
  toast: {
    show: vi.fn(),
  },
  redirect: {
    dispatch: vi.fn(),
  },
};

// Mock environment variables
process.env.SHOPIFY_API_KEY = 'test-api-key';
process.env.SHOPIFY_API_SECRET = 'test-api-secret';
process.env.SHOPIFY_APP_URL = 'https://test-app.ngrok.io';
process.env.SHOPIFY_WEBHOOK_SECRET = 'test-webhook-secret';

// Create global mock admin client
global.mockShopifyAdmin = new MockShopifyAdmin();

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
  global.mockShopifyAdmin.reset();
});
```

The mocking infrastructure I've just shown you represents a fundamental shift in how you approach testing when moving from monolithic applications to apps that integrate with external platforms. In Laravel, you might be used to using database factories and the RefreshDatabase trait to ensure clean test state. In Spring Boot, you'd use @DataJpaTest with an in-memory database. But in Shopify development, you're dealing with an external API that you can't control directly, which is why this comprehensive mocking strategy is so important.

The ShopifyTestFactory class I've created serves the same purpose as Laravel's factory classes or Spring Boot's test fixtures, but instead of generating database records, it generates API responses that exactly match what Shopify would return. This attention to detail is crucial because small discrepancies between your mocks and reality can lead to bugs that only appear in production.

## 8. Hands-On Exercise: Building Your First Comprehensive Test Suite

Now that you understand the testing landscape, let me guide you through a practical exercise that will help you apply these concepts to a real-world scenario. We'll build a test suite for a common Shopify app feature: a discount calculator that integrates with Shopify Functions.

This exercise will help you understand how unit tests, integration tests, and end-to-end tests work together to provide comprehensive coverage. Think of it as building a safety net for your code, where each layer catches different types of issues.

```js
// ===================================================
// HANDS-ON EXERCISE: Building a Complete Test Suite
// ===================================================
// 
// Scenario: You're building a Shopify Function that applies
// volume discounts based on quantity purchased. The function
// needs to:
// 1. Apply different discount tiers based on quantity
// 2. Respect customer segment restrictions
// 3. Handle edge cases gracefully
// 4. Integrate with Shopify's discount system
//
// Your task: Complete the test suite following TDD principles

// File: extensions/volume-discount/src/index.js
// The main function that Shopify will execute

export function run(input) {
  // Define discount tiers
  const discountTiers = [
    { minQuantity: 10, maxQuantity: 19, discount: 5 },   // 5% off for 10-19 items
    { minQuantity: 20, maxQuantity: 49, discount: 10 },  // 10% off for 20-49 items
    { minQuantity: 50, maxQuantity: null, discount: 15 }, // 15% off for 50+ items
  ];
  
  const discounts = [];
  
  // Process each line item in the cart
  input.cart.lines.forEach((line) => {
    // Skip if not a product variant
    if (line.merchandise.__typename !== 'ProductVariant') {
      return;
    }
    
    // Check if customer is eligible (VIP customers only for this example)
    const isVIP = input.cart.buyerIdentity?.customer?.hasAnyTag?.includes('VIP');
    
    if (!isVIP && line.quantity >= 10) {
      // Non-VIP customers need to be VIP for volume discounts
      return;
    }
    
    // Find applicable discount tier
    const applicableTier = discountTiers.find(tier => 
      line.quantity >= tier.minQuantity && 
      (tier.maxQuantity === null || line.quantity <= tier.maxQuantity)
    );
    
    if (applicableTier) {
      discounts.push({
        targets: [{
          cartLine: {
            id: line.id,
          },
        }],
        value: {
          percentage: {
            value: applicableTier.discount.toString(),
          },
        },
        message: `Volume discount: ${applicableTier.discount}% off`,
      });
    }
  });
  
  return {
    discounts,
    discountApplicationStrategy: 'FIRST',
  };
}

// ===================================================
// EXERCISE PART 1: Unit Tests
// ===================================================
// File: extensions/volume-discount/src/index.test.js
// 
// Task: Complete the unit tests for the discount function
// Hint: Think about all the edge cases and business rules

import { describe, it, expect } from 'vitest';
import { run } from './index';

describe('Volume Discount Function - Unit Tests', () => {
  // Helper function to create test input
  function createTestInput(lineItems = [], customerTags = []) {
    return {
      cart: {
        lines: lineItems.map((item, index) => ({
          id: `gid://shopify/CartLine/${index + 1}`,
          quantity: item.quantity || 1,
          merchandise: {
            __typename: item.type || 'ProductVariant',
            id: `gid://shopify/ProductVariant/${index + 1}`,
          },
        })),
        buyerIdentity: customerTags.length > 0 ? {
          customer: {
            hasAnyTag: customerTags,
          },
        } : null,
      },
    };
  }
  
  describe('Discount Tier Application', () => {
    it('applies 5% discount for 10-19 items for VIP customers', () => {
      // TODO: Complete this test
      // Create input with a VIP customer buying 15 items
      // Assert that a 5% discount is applied
      
      const input = createTestInput(
        [{ quantity: 15 }],
        ['VIP']
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(1);
      expect(result.discounts[0].value.percentage.value).toBe('5');
      expect(result.discounts[0].message).toBe('Volume discount: 5% off');
    });
    
    it('applies 10% discount for 20-49 items for VIP customers', () => {
      // TODO: Complete this test
      // Hint: Test the middle tier
      
      const input = createTestInput(
        [{ quantity: 35 }],
        ['VIP']
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(1);
      expect(result.discounts[0].value.percentage.value).toBe('10');
    });
    
    it('applies 15% discount for 50+ items for VIP customers', () => {
      // TODO: Complete this test
      // Hint: Test the highest tier with no upper limit
      
      const input = createTestInput(
        [{ quantity: 100 }],
        ['VIP']
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(1);
      expect(result.discounts[0].value.percentage.value).toBe('15');
    });
    
    it('applies no discount for quantities below 10', () => {
      // TODO: Complete this test
      // Hint: Even VIP customers don't get discounts below threshold
      
      const input = createTestInput(
        [{ quantity: 9 }],
        ['VIP']
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(0);
    });
  });
  
  describe('Customer Eligibility', () => {
    it('does not apply discount for non-VIP customers', () => {
      // TODO: Complete this test
      // Test that regular customers don't get volume discounts
      
      const input = createTestInput(
        [{ quantity: 20 }],
        ['REGULAR']
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(0);
    });
    
    it('applies discount for customers with multiple tags including VIP', () => {
      // TODO: Complete this test
      // Test that VIP tag works even with other tags present
      
      const input = createTestInput(
        [{ quantity: 15 }],
        ['WHOLESALE', 'VIP', 'RETURNING']
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(1);
      expect(result.discounts[0].value.percentage.value).toBe('5');
    });
    
    it('handles missing customer identity gracefully', () => {
      // TODO: Complete this test
      // Test when buyerIdentity is null (guest checkout)
      
      const input = createTestInput(
        [{ quantity: 20 }],
        [] // No customer tags
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(0);
      expect(result.discountApplicationStrategy).toBe('FIRST');
    });
  });
  
  describe('Multiple Line Items', () => {
    it('applies discounts to multiple eligible line items', () => {
      // TODO: Complete this test
      // Test cart with multiple products at different quantities
      
      const input = createTestInput(
        [
          { quantity: 15 }, // Should get 5% off
          { quantity: 25 }, // Should get 10% off
          { quantity: 5 },  // No discount
        ],
        ['VIP']
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(2);
      expect(result.discounts[0].value.percentage.value).toBe('5');
      expect(result.discounts[1].value.percentage.value).toBe('10');
      expect(result.discounts[0].targets[0].cartLine.id).toBe('gid://shopify/CartLine/1');
      expect(result.discounts[1].targets[0].cartLine.id).toBe('gid://shopify/CartLine/2');
    });
    
    it('skips non-product variants in the cart', () => {
      // TODO: Complete this test
      // Test that gift cards or custom line items are ignored
      
      const input = createTestInput(
        [
          { quantity: 20, type: 'ProductVariant' },
          { quantity: 20, type: 'GiftCard' },
        ],
        ['VIP']
      );
      
      const result = run(input);
      
      expect(result.discounts).toHaveLength(1);
      expect(result.discounts[0].targets[0].cartLine.id).toBe('gid://shopify/CartLine/1');
    });
  });
  
  describe('Edge Cases', () => {
    it('handles empty cart', () => {
      const input = createTestInput([], ['VIP']);
      const result = run(input);
      
      expect(result.discounts).toHaveLength(0);
      expect(result.discountApplicationStrategy).toBe('FIRST');
    });
    
    it('handles exact tier boundaries correctly', () => {
      // Test quantities at exact tier boundaries: 10, 19, 20, 49, 50
      const testCases = [
        { quantity: 10, expectedDiscount: '5' },
        { quantity: 19, expectedDiscount: '5' },
        { quantity: 20, expectedDiscount: '10' },
        { quantity: 49, expectedDiscount: '10' },
        { quantity: 50, expectedDiscount: '15' },
      ];
      
      testCases.forEach(({ quantity, expectedDiscount }) => {
        const input = createTestInput([{ quantity }], ['VIP']);
        const result = run(input);
        
        expect(result.discounts[0].value.percentage.value).toBe(expectedDiscount);
      });
    });
  });
});

// ===================================================
// EXERCISE PART 2: Integration Tests
// ===================================================
// File: extensions/volume-discount/src/integration.test.js
// 
// Task: Test the function's integration with Shopify's system

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { run } from './index';

describe('Volume Discount Function - Integration Tests', () => {
  let mockShopifyContext;
  
  beforeEach(() => {
    // Set up mock Shopify context
    mockShopifyContext = {
      api: {
        query: vi.fn(),
      },
      sessionToken: 'mock-session-token',
      shop: 'test-shop.myshopify.com',
    };
  });
  
  it('integrates with Shopify Function runtime', async () => {
    // TODO: Complete this integration test
    // Test that the function can be executed in Shopify's runtime
    
    // Simulate Shopify calling our function
    const input = {
      cart: {
        lines: [{
          id: 'gid://shopify/CartLine/1',
          quantity: 20,
          merchandise: {
            __typename: 'ProductVariant',
            id: 'gid://shopify/ProductVariant/123',
          },
        }],
        buyerIdentity: {
          customer: {
            hasAnyTag: ['VIP'],
          },
        },
      },
    };
    
    // Execute the function
    const result = await run(input);
    
    // Verify the output matches Shopify's expected format
    expect(result).toHaveProperty('discounts');
    expect(result).toHaveProperty('discountApplicationStrategy');
    expect(result.discounts[0]).toHaveProperty('targets');
    expect(result.discounts[0]).toHaveProperty('value');
    expect(result.discounts[0]).toHaveProperty('message');
    
    // Verify the structure matches Shopify's schema
    expect(result.discounts[0].targets[0]).toHaveProperty('cartLine');
    expect(result.discounts[0].value).toHaveProperty('percentage');
    expect(result.discounts[0].value.percentage).toHaveProperty('value');
  });
  
  it('handles large cart performance', () => {
    // TODO: Test with a large number of line items
    // Ensure the function performs well with realistic data
    
    const lineItems = Array.from({ length: 100 }, (_, i) => ({
      quantity: Math.floor(Math.random() * 60) + 1,
    }));
    
    const input = {
      cart: {
        lines: lineItems.map((item, index) => ({
          id: `gid://shopify/CartLine/${index + 1}`,
          quantity: item.quantity,
          merchandise: {
            __typename: 'ProductVariant',
            id: `gid://shopify/ProductVariant/${index + 1}`,
          },
        })),
        buyerIdentity: {
          customer: {
            hasAnyTag: ['VIP'],
          },
        },
      },
    };
    
    const startTime = performance.now();
    const result = run(input);
    const endTime = performance.now();
    
    // Function should execute in under 10ms even with 100 items
    expect(endTime - startTime).toBeLessThan(10);
    expect(result.discounts).toBeDefined();
  });
});

// ===================================================
// EXERCISE PART 3: Function Output Validation
// ===================================================
// File: extensions/volume-discount/src/validation.test.js
// 
// Task: Validate that your function output matches Shopify's schema

import { describe, it, expect } from 'vitest';
import { run } from './index';

describe('Volume Discount Function - Output Validation', () => {
  // Shopify's expected output schema
  const validateDiscountOutput = (output) => {
    // Check required top-level fields
    expect(output).toHaveProperty('discounts');
    expect(output).toHaveProperty('discountApplicationStrategy');
    
    // Validate discountApplicationStrategy enum
    expect(['FIRST', 'MAXIMUM', 'ALL']).toContain(output.discountApplicationStrategy);
    
    // Validate each discount
    output.discounts.forEach(discount => {
      // Required fields
      expect(discount).toHaveProperty('targets');
      expect(discount).toHaveProperty('value');
      
      // Validate targets structure
      expect(Array.isArray(discount.targets)).toBe(true);
      discount.targets.forEach(target => {
        expect(target).toHaveProperty('cartLine');
        expect(target.cartLine).toHaveProperty('id');
        expect(typeof target.cartLine.id).toBe('string');
        expect(target.cartLine.id).toMatch(/^gid:\/\/shopify\/CartLine\/\d+$/);
      });
      
      // Validate value structure (percentage discount)
      expect(discount.value).toHaveProperty('percentage');
      expect(discount.value.percentage).toHaveProperty('value');
      expect(typeof discount.value.percentage.value).toBe('string');
      
      // Optional message field
      if (discount.message) {
        expect(typeof discount.message).toBe('string');
      }
    });
    
    return true;
  };
  
  it('produces valid output for all test scenarios', () => {
    const testScenarios = [
      {
        name: 'Single item with discount',
        input: {
          cart: {
            lines: [{
              id: 'gid://shopify/CartLine/1',
              quantity: 20,
              merchandise: {
                __typename: 'ProductVariant',
                id: 'gid://shopify/ProductVariant/1',
              },
            }],
            buyerIdentity: {
              customer: {
                hasAnyTag: ['VIP'],
              },
            },
          },
        },
      },
      {
        name: 'Multiple items with different discounts',
        input: {
          cart: {
            lines: [
              {
                id: 'gid://shopify/CartLine/1',
                quantity: 15,
                merchandise: {
                  __typename: 'ProductVariant',
                  id: 'gid://shopify/ProductVariant/1',
                },
              },
              {
                id: 'gid://shopify/CartLine/2',
                quantity: 50,
                merchandise: {
                  __typename: 'ProductVariant',
                  id: 'gid://shopify/ProductVariant/2',
                },
              },
            ],
            buyerIdentity: {
              customer: {
                hasAnyTag: ['VIP'],
              },
            },
          },
        },
      },
      {
        name: 'No applicable discounts',
        input: {
          cart: {
            lines: [{
              id: 'gid://shopify/CartLine/1',
              quantity: 5,
              merchandise: {
                __typename: 'ProductVariant',
                id: 'gid://shopify/ProductVariant/1',
              },
            }],
            buyerIdentity: {
              customer: {
                hasAnyTag: ['VIP'],
              },
            },
          },
        },
      },
    ];
    
    testScenarios.forEach(scenario => {
      const output = run(scenario.input);
      
      // Validate output structure
      expect(validateDiscountOutput(output)).toBe(true);
      
      // Log for debugging
      console.log(`✓ Scenario "${scenario.name}" produces valid output`);
    });
  });
});
```

This hands-on exercise demonstrates how testing in Shopify development requires you to think differently than you might be accustomed to in Laravel or Spring Boot applications. When you write tests for a Laravel application, you're typically testing code that runs entirely within your control. You can manipulate the database, mock services, and control every aspect of the environment. In Shopify development, particularly with Functions, you're writing code that will run in Shopify's infrastructure, which means your tests need to validate not just that your logic is correct, but that your output conforms exactly to what Shopify expects.

The exercise I've provided follows a Test-Driven Development (TDD) approach, which is particularly valuable in Shopify development because the cost of bugs can be high. A broken discount function could cost merchants money, and a security vulnerability in webhook processing could expose sensitive customer data. By writing comprehensive tests first, you ensure that your code meets requirements before you even start implementing the business logic.

## 9. Production Considerations and Best Practices

As you transition from learning to building production Shopify apps, there are several critical testing practices that will help you maintain high quality and avoid common pitfalls. These practices come from real-world experience building apps that serve thousands of merchants and process millions of dollars in transactions.

First, always test with realistic data volumes. It's easy to write code that works perfectly with a store that has ten products, but fails catastrophically when a merchant has ten thousand. Shopify stores can vary enormously in size and complexity, from single-product stores to massive catalogs with hundreds of thousands of SKUs. Your tests should reflect this reality by including performance benchmarks and testing with large datasets.

Second, implement comprehensive error handling and test it thoroughly. In Laravel or Spring Boot, an unhandled exception might result in a 500 error that you can fix and deploy quickly. In a Shopify app, especially in webhook handlers or checkout extensions, errors can disrupt critical business processes. Always test not just the happy path, but also network failures, API rate limiting, malformed data, and edge cases you might not expect.

Third, maintain separate test environments that mirror your production setup as closely as possible. Create dedicated development stores for different testing scenarios, such as stores with different Shopify plans, stores with various apps installed, and stores with different configurations. This helps you catch compatibility issues early.

## 10. Your Testing Action Plan

Now that you understand the testing landscape for Shopify apps, let me provide you with a concrete action plan to implement these practices in your development workflow.

Start by setting up your testing infrastructure. Create a new Shopify app project if you haven't already, and configure Vitest with the settings I've shown you. Set up your mock factories and test utilities, as these will save you countless hours as your app grows. Think of this initial setup as an investment that will pay dividends throughout your development process.

Next, adopt a test-first mindset for all new features. Before you write any production code, write at least one failing test that describes what the code should do. This practice, which you might know from your Laravel or Spring Boot experience, is even more valuable in Shopify development because it forces you to think about edge cases and error conditions upfront.

As you build your app, maintain a balance between different types of tests. Aim for approximately 70% unit tests, 20% integration tests, and 10% end-to-end tests. This pyramid structure ensures fast feedback during development while still providing confidence that your app works correctly when all the pieces come together.

When you encounter bugs in production, and you will, always write a test that reproduces the bug before fixing it. This regression testing approach ensures that bugs don't reappear and helps you build a comprehensive test suite over time. Document these tests with comments explaining what went wrong and why the test is important.

Finally, integrate testing into your deployment pipeline. Set up continuous integration to run your tests automatically when you push code, and configure your deployment process to prevent releases if tests fail. This safety net becomes increasingly important as your app grows and serves more merchants.

## Moving Forward with Confidence

Testing in Shopify development might feel overwhelming at first, especially coming from frameworks where testing patterns are more established. However, the investment you make in learning these testing strategies will pay off tremendously as you build more complex apps that merchants rely on for their businesses.

Remember that testing is not about achieving 100% code coverage or following rigid rules. It's about building confidence that your app works correctly, handles edge cases gracefully, and won't break when Shopify updates their platform or when merchants use it in unexpected ways. The tests you write are a form of living documentation that explains how your app should behave and helps future developers, including your future self, understand and modify the code safely.

As you continue your Shopify development journey, you'll discover that the testing patterns I've shown you are just the beginning. Each app has unique testing challenges, and you'll develop your own patterns and practices that work for your specific needs. The key is to start with a solid foundation and evolve your testing strategy as you learn more about the Shopify platform and your merchants' needs.

The transition from Laravel and Spring Boot to Shopify development requires adapting your testing mindset, but your existing knowledge provides a strong foundation. You understand the importance of testing, you know how to structure test cases, and you appreciate the value of automated testing. Now you're equipped with Shopify-specific testing strategies that will help you build robust, reliable apps that merchants can trust with their businesses.
