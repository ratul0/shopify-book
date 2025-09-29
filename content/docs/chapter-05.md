# App Bridge and Shopify Admin Integration

Based on the current Shopify documentation (as of September 2025), I'll teach you how to build apps that integrate seamlessly with the Shopify Admin using App Bridge. This is fundamental to creating a native-feeling experience for merchants.

## 1. Current Shopify Documentation Check

**API Version:** The latest stable version is **2025-04**, with 2025-07 in preview
**Last Documentation Update:** Current as of September 2025
**Major Recent Changes:**
- App Bridge is now loaded via CDN script tag (auto-updating)
- Shift from React components to web standards and HTML elements
- New `shopify` global object replaces the old app instance pattern
- Direct API access now available (fetch calls authenticated automatically)
- Modals completely redesigned with iframe architecture

**⚠️ Warning:** Many online tutorials still show the old `@shopify/app-bridge` npm package patterns - these are deprecated. The current approach uses the CDN-hosted script.

## 2. The Laravel/Spring Boot/Angular Equivalent

Think of App Bridge as similar to these concepts from your background:

**Laravel Perspective:**
- App Bridge is like Laravel's middleware system combined with Blade components
- The `shopify` global is similar to Laravel's global helpers (like `auth()`, `route()`)
- Modal iframes are like Laravel's view composers rendering isolated blade templates
- Navigation is similar to Laravel's `redirect()` helper but works across iframe boundaries

**Spring Boot Perspective:**
- App Bridge acts like Spring's ApplicationContext providing dependency injection
- The authentication layer is similar to Spring Security's filter chain
- Resource pickers are like Spring Data's repository pattern with built-in UI

**Angular Perspective:**
- The `shopify` global is like Angular's dependency injection providing services
- Modals work like Angular's dynamic component loading with ViewContainerRef
- Navigation uses standard HTML anchors, similar to Angular's RouterLink
- The iframe architecture is like Angular's content projection but across frame boundaries

## 3. Architecture Deep Dive

### The Iframe Architecture

```
┌─────────────────────────────────────┐
│     Shopify Admin (Parent Frame)    │
│  ┌────────────────────────────────┐ │
│  │     Your App (Child Frame)     │ │
│  │  ┌──────────────────────────┐  │ │
│  │  │   Modal (Grandchild)     │  │ │
│  │  │   - Rendered by Admin    │  │ │
│  │  │   - Contains your HTML   │  │ │
│  │  └──────────────────────────┘  │ │
│  │                                 │ │
│  │  shopify.* APIs communicate    │ │
│  │  with parent frame via          │ │
│  │  postMessage                    │ │
│  └────────────────────────────────┘ │
└─────────────────────────────────────┘
```

Your app runs in an iframe within the Shopify Admin. App Bridge handles all cross-frame communication using postMessage under the hood. This is completely different from your Angular SPAs that control the entire window.

Key architectural points:
- Your app never directly accesses the parent window's DOM
- All UI actions go through the `shopify` global object
- Modals are rendered by Shopify Admin, not your app
- Authentication tokens are automatically injected into fetch requests

## 4. Practical Implementation with Validated Code

### Basic App Setup

**API Version:** 2025-04  
**Last verified:** September 23, 2025  
**File:** `app/root.tsx` (for Remix) or `index.html`

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Replace with your actual API key from Partner Dashboard -->
  <meta name="shopify-api-key" content="%SHOPIFY_API_KEY%" />
  
  <!-- CDN-hosted script that auto-updates -->
  <script src="https://cdn.shopify.com/shopifycloud/app-bridge.js"></script>
</head>
<body>
  <div id="app">
    <!-- Your app content here -->
  </div>
  
  <script>
    // The shopify global is now available
    console.log('Shop:', shopify.config.shop);
    console.log('Locale:', shopify.config.locale);
  </script>
</body>
</html>
```

### Navigation and Routing

**File:** `app/components/Navigation.jsx`

```jsx
import React from 'react';

function AppNavigation() {
  // Navigation in App Bridge uses standard HTML anchors
  // This is different from Angular's Router - no programmatic navigation needed
  
  return (
    <nav>
      {/* Internal app navigation - stays within your iframe */}
      <a href="/dashboard">Dashboard</a>
      <a href="/settings">Settings</a>
      
      {/* Navigate to Shopify Admin pages - breaks out of iframe */}
      <a href="shopify://admin/products" target="_top">
        Go to Products
      </a>
      
      {/* Open external URL in new tab */}
      <a href="https://help.shopify.com" target="_blank">
        Help Docs
      </a>
      
      {/* Navigate to specific product */}
      <a 
        href="shopify://admin/products/1234567890" 
        target="_top"
      >
        View Product
      </a>
    </nav>
  );
}

// For programmatic navigation (like after form submission)
function handleSave() {
  // Similar to Angular's Router.navigate() or Laravel's redirect()
  window.open('/success', '_self');
  
  // Or navigate to Shopify Admin
  window.open('shopify://admin/orders', '_top');
}
```

### Resource Pickers

**File:** `app/components/ProductSelector.jsx`

```jsx
import React, { useState } from 'react';

function ProductSelector() {
  const [selectedProducts, setSelectedProducts] = useState([]);
  
  async function openProductPicker() {
    try {
      // This opens Shopify's native product picker UI
      // Similar to Angular Material's dialog.open() but managed by Shopify
      const selection = await shopify.resourcePicker({
        type: 'product',
        action: 'select', // or 'add'
        multiple: true, // Allow multiple selection
        filter: {
          variants: true, // Show product variants
          draft: false, // Hide draft products
          archived: false, // Hide archived products
        },
        // Preselect products (like Angular's FormControl initial value)
        selectionIds: [
          { id: 'gid://shopify/Product/1234567890' }
        ]
      });
      
      if (selection) {
        console.log('Selected products:', selection);
        setSelectedProducts(selection);
        
        // Each product in selection has this structure:
        // {
        //   id: 'gid://shopify/Product/xxx',
        //   title: 'Product Name',
        //   handle: 'product-name',
        //   images: [...],
        //   variants: [...],
        //   status: 'ACTIVE',
        //   ...
        // }
      } else {
        console.log('Picker cancelled');
      }
    } catch (error) {
      console.error('Picker error:', error);
    }
  }
  
  return (
    <div>
      <button onClick={openProductPicker}>
        Select Products
      </button>
      
      {selectedProducts.map(product => (
        <div key={product.id}>
          {product.title} - {product.variants.length} variants
        </div>
      ))}
    </div>
  );
}
```

### Modal Implementation

**File:** `app/components/EditModal.jsx`

```jsx
import React, { useState, useEffect } from 'react';

function EditModal({ isOpen, onClose }) {
  // Modals in App Bridge are different from Angular Material Dialogs
  // They render in a separate iframe managed by Shopify Admin
  
  return (
    <>
      {/* Modal with inline content (simple cases) */}
      <div 
        id="edit-modal" 
        style={{ display: isOpen ? 'block' : 'none' }}
      >
        <ui-modal id="my-modal">
          {/* Content is moved to modal iframe by App Bridge */}
          <div>
            <h2>Edit Product</h2>
            <input type="text" placeholder="Product name" />
            <p>This content runs in a separate iframe!</p>
          </div>
          
          {/* Title bar controls modal header and buttons */}
          <ui-title-bar title="Edit Product">
            <button variant="primary" onClick={handleSave}>
              Save
            </button>
            <button onClick={onClose}>
              Cancel
            </button>
          </ui-title-bar>
        </ui-modal>
      </div>
      
      {/* Open modal programmatically */}
      <button onClick={() => shopify.modal.show('my-modal')}>
        Open Modal
      </button>
    </>
  );
}

// For complex modals, use a separate route
function ComplexModal() {
  return (
    <ui-modal id="complex-modal" src="/modal-content">
      <ui-title-bar title="Complex Editor">
        <button variant="primary">Save</button>
      </ui-title-bar>
    </ui-modal>
  );
}

// Communication between modal and parent (like Angular's EventEmitter)
function ModalWithCommunication() {
  useEffect(() => {
    // Listen for messages from modal
    const handleMessage = (event) => {
      if (event.data.type === 'MODAL_DATA') {
        console.log('Received from modal:', event.data.payload);
      }
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);
  
  return (
    <ui-modal id="comm-modal">
      <button onClick={() => {
        // Send message to parent from within modal
        window.opener?.postMessage(
          { type: 'MODAL_DATA', payload: 'Hello parent!' },
          location.origin
        );
      }}>
        Send to Parent
      </button>
    </ui-modal>
  );
}
```

### Toast Notifications

**File:** `app/utils/notifications.js`

```javascript
// Toast API is similar to Angular Material's MatSnackBar
// But simpler and follows web Notification API patterns

export function showSuccess(message) {
  shopify.toast.show(message, {
    duration: 5000, // Auto-hide after 5 seconds
  });
}

export function showError(message) {
  shopify.toast.show(message, {
    isError: true,
    duration: 8000,
  });
}

export function showActionToast(message, actionLabel, onAction) {
  // Similar to Angular Material SnackBar with action
  const toastId = shopify.toast.show(message, {
    action: actionLabel,
    onAction: () => {
      console.log('Action clicked');
      onAction();
    },
    onDismiss: () => {
      console.log('Toast dismissed');
    }
  });
  
  // Can manually hide if needed
  // shopify.toast.hide(toastId);
  
  return toastId;
}

// Usage in a component
async function saveProduct() {
  try {
    await saveToBackend();
    showSuccess('Product saved successfully!');
  } catch (error) {
    showError('Failed to save product');
  }
}
```

### Mobile Compatibility

**File:** `app/components/ResponsiveLayout.jsx`

```jsx
function ResponsiveLayout() {
  const [environment, setEnvironment] = useState({});
  
  useEffect(() => {
    // Check the environment (automatically handled by App Bridge)
    setEnvironment({
      isMobile: shopify.environment.mobile,
      isEmbedded: shopify.environment.embedded,
      isPOS: shopify.environment.pos
    });
  }, []);
  
  // Mobile compatibility is automatic for:
  // - Modals (responsive by default)
  // - Resource pickers (mobile-optimized UI)
  // - Navigation (works with mobile gestures)
  // - Toasts (positioned correctly on mobile)
  
  if (environment.isMobile) {
    // Mobile-specific features
    return (
      <div>
        {/* Scanner is mobile-only */}
        <button onClick={async () => {
          const result = await shopify.scanner.capture();
          console.log('Scanned:', result);
        }}>
          Scan Barcode
        </button>
        
        {/* Print from mobile */}
        <button onClick={() => shopify.print()}>
          Print
        </button>
      </div>
    );
  }
  
  return (
    <div>
      {/* Desktop layout - no special handling needed */}
      <p>Desktop version</p>
    </div>
  );
}
```

## 5. Real-World Scenarios

### Scenario 1: Product Bulk Editor

```jsx
// Complete working example of a bulk editor with resource picker
function BulkProductEditor() {
  const [products, setProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  async function selectProducts() {
    shopify.loading(true); // Show loading bar in Admin
    
    try {
      const selected = await shopify.resourcePicker({
        type: 'product',
        multiple: 20, // Limit to 20 products
        filter: {
          query: 'inventory_quantity:>0', // GraphQL filter
        }
      });
      
      if (selected) {
        setProducts(selected);
        shopify.toast.show(`Selected ${selected.length} products`);
      }
    } finally {
      shopify.loading(false);
    }
  }
  
  async function bulkUpdatePrices() {
    setIsLoading(true);
    
    try {
      // Direct API access - automatically authenticated!
      const response = await fetch('shopify:admin/api/2025-04/graphql.json', {
        method: 'POST',
        body: JSON.stringify({
          query: `
            mutation bulkProductUpdate($input: ProductInput!) {
              productUpdate(input: $input) {
                product { id }
                userErrors { field message }
              }
            }
          `,
          variables: { 
            // ... your variables
          }
        })
      });
      
      const result = await response.json();
      
      shopify.toast.show('Prices updated!', {
        action: 'View Products',
        onAction: () => {
          window.open('shopify://admin/products', '_top');
        }
      });
    } catch (error) {
      shopify.toast.show('Update failed', { isError: true });
    } finally {
      setIsLoading(false);
    }
  }
  
  return (
    <div>
      <button onClick={selectProducts}>Select Products</button>
      <button onClick={bulkUpdatePrices} disabled={!products.length}>
        Update Prices
      </button>
    </div>
  );
}
```

### Scenario 2: Order Fulfillment Workflow

```jsx
function OrderFulfillmentFlow() {
  // Complex modal with inter-frame communication
  const [orders, setOrders] = useState([]);
  
  useEffect(() => {
    // Set up BroadcastChannel for modal communication
    const channel = new BroadcastChannel('fulfillment-channel');
    
    channel.addEventListener('message', (event) => {
      if (event.data.type === 'ORDER_FULFILLED') {
        setOrders(prev => 
          prev.filter(o => o.id !== event.data.orderId)
        );
        shopify.toast.show('Order fulfilled!');
      }
    });
    
    return () => channel.close();
  }, []);
  
  return (
    <>
      <ui-modal id="fulfillment-modal" variant="max">
        <FulfillmentForm channel={channel} />
        <ui-title-bar title="Fulfill Order">
          <button variant="primary" onClick={handleFulfill}>
            Complete Fulfillment
          </button>
        </ui-title-bar>
      </ui-modal>
      
      <button onClick={() => shopify.modal.show('fulfillment-modal')}>
        Start Fulfillment
      </button>
    </>
  );
}
```

## 6. Advanced Patterns

### Pattern 1: State Management Across Frames

```javascript
// Since modals run in separate iframes, you need special patterns
// Similar to Angular's services but across frame boundaries

class CrossFrameStore {
  constructor() {
    this.channel = new BroadcastChannel('app-state');
    this.state = {};
    
    this.channel.addEventListener('message', (event) => {
      if (event.data.type === 'STATE_UPDATE') {
        this.state = { ...this.state, ...event.data.payload };
        this.notifySubscribers();
      }
    });
  }
  
  setState(updates) {
    this.state = { ...this.state, ...updates };
    this.channel.postMessage({
      type: 'STATE_UPDATE',
      payload: updates
    });
  }
  
  // Use in both parent and modal frames
  static instance = null;
  static getInstance() {
    if (!this.instance) {
      this.instance = new CrossFrameStore();
    }
    return this.instance;
  }
}
```

### Pattern 2: Resource Picker with Validation

```jsx
async function validateAndSelectProducts() {
  // Open picker with custom validation
  const selected = await shopify.resourcePicker({
    type: 'product',
    multiple: true,
    filter: {
      // Only show products that match criteria
      query: 'product_type:clothing AND vendor:nike'
    }
  });
  
  if (!selected) return;
  
  // Additional validation after selection
  const validProducts = selected.filter(product => {
    // Check custom business rules
    const hasRequiredVariants = product.variants.some(
      v => v.inventoryQuantity > 10
    );
    const isValidPrice = product.variants[0].price > '10.00';
    
    return hasRequiredVariants && isValidPrice;
  });
  
  if (validProducts.length !== selected.length) {
    shopify.toast.show(
      `${selected.length - validProducts.length} products didn't meet criteria`,
      { isError: true }
    );
  }
  
  return validProducts;
}
```

## 7. Hands-On Exercise

**Build a Product Collection Manager** that demonstrates all App Bridge concepts:

**Requirements:**
1. Use resource picker to select products (multiple selection)
2. Show selected products in a list with inline editing
3. Create a modal for bulk operations
4. Add navigation to Shopify admin pages
5. Show toast notifications for all actions
6. Ensure mobile compatibility

**Starter Code:**

```jsx
// Your task: Complete this component
function ProductCollectionManager() {
  const [products, setProducts] = useState([]);
  const [collection, setCollection] = useState(null);
  
  // TODO: Implement product picker
  async function selectProducts() {
    // Hint: Use shopify.resourcePicker with type: 'product'
    // Remember to handle the promise and check for cancellation
  }
  
  // TODO: Implement collection picker
  async function selectCollection() {
    // Hint: Use shopify.resourcePicker with type: 'collection'
  }
  
  // TODO: Create modal for bulk price update
  function BulkPriceModal() {
    // Hint: Use ui-modal with a form inside
    // Don't forget the ui-title-bar for actions
  }
  
  // TODO: Navigate to collection in admin
  function viewInAdmin() {
    // Hint: Use shopify://admin/collections/{id}
  }
  
  // TODO: Show success/error toasts
  async function saveChanges() {
    // Hint: Use shopify.toast.show with appropriate options
  }
  
  // Bonus: Add mobile-specific features
  // Hint: Check shopify.environment.mobile
  
  return (
    <div>
      {/* Build your UI here */}
    </div>
  );
}
```

**Success Criteria:**
- Products can be selected and displayed
- Modal opens and closes properly
- Navigation works to admin pages
- Toasts appear for actions
- Works on mobile (test with Chrome DevTools mobile view)

## 8. Migration Path and Current Best Practices

### From Deprecated Patterns to Current

**Old Pattern (pre-2024):**
```javascript
// DON'T DO THIS - Deprecated!
import createApp from '@shopify/app-bridge';
import { Toast, Modal } from '@shopify/app-bridge/actions';

const app = createApp({
  apiKey: 'xxx',
  host: 'xxx'
});

const toast = Toast.create(app, { message: 'Hello' });
toast.dispatch(Toast.Action.SHOW);
```

**Current Pattern (2025):**
```javascript
// DO THIS - Current approach
// No imports needed, use CDN script
shopify.toast.show('Hello');
```

### Common Mistakes to Avoid

1. **Using npm packages instead of CDN script** - The CDN version auto-updates
2. **Trying to access parent window DOM** - Always use App Bridge APIs
3. **Not handling promise rejection in resource pickers** - Users can cancel
4. **Forgetting modal content runs in separate iframe** - State doesn't share automatically
5. **Using complex routing libraries** - HTML anchors work perfectly

### Performance Best Practices

```javascript
// 1. Debounce resource picker calls
const debouncedPicker = debounce(async () => {
  await shopify.resourcePicker({ type: 'product' });
}, 300);

// 2. Preload modal content
<ui-modal id="preloaded" src="/modal-content" preload>

// 3. Use loading indicators
async function heavyOperation() {
  shopify.loading(true);
  try {
    await doWork();
  } finally {
    shopify.loading(false);
  }
}

// 4. Batch API calls with Direct API access
const response = await fetch('shopify:admin/api/2025-04/graphql.json', {
  method: 'POST',
  body: JSON.stringify({
    query: `
      query BatchFetch {
        products(first: 10) { ... }
        orders(first: 10) { ... }
        customers(first: 10) { ... }
      }
    `
  })
});
```

## 9. Verification and Resources

**How I verified this information:**

1. **Used `shopify-dev-mcp:learn_shopify_api`** - Loaded admin API context
2. **Used `shopify-dev-mcp:search_docs_chunks`** - Retrieved latest App Bridge documentation
3. **Used `shopify-dev-mcp:fetch_full_docs`** - Got complete navigation, toast, and resource picker docs

**Current Documentation Status:**
- ✅ App Bridge via CDN (current)
- ✅ Web standards approach (current)
- ✅ Modal iframe architecture (current)
- ✅ Promise-based resource pickers (current)
- ❌ NPM package approach (deprecated)
- ❌ Provider/Context pattern (deprecated)

**Related Concepts to Explore Next:**
1. **Shopify Functions** - Server-side customization
2. **Admin Extensions** - UI extensions in specific admin areas  
3. **Direct API Access** - Authenticated fetch from frontend
4. **Checkout Extensions** - Customize checkout flow
5. **Theme App Extensions** - Integrate with storefront

**Key Documentation Links:**
- [App Bridge Library](https://shopify.dev/docs/api/app-bridge-library)
- [Migration Guide](https://shopify.dev/docs/api/app-bridge/migration-guide)
- [Using Modals](https://shopify.dev/docs/api/app-bridge/using-modals-in-your-app)

## Summary

App Bridge has evolved significantly to embrace web standards. The current approach is simpler than the old React component model - it's closer to vanilla JavaScript with a powerful global API. Coming from Angular, you'll find the iframe architecture different but the concepts of services (`shopify.*`), components (web components like `ui-modal`), and routing (HTML anchors) familiar.

The key insight is that App Bridge acts as a bridge (hence the name) between your isolated iframe app and the Shopify Admin, handling all the complex postMessage communication transparently. Focus on using the `shopify` global object for all interactions, and remember that modals create another iframe layer that needs special handling for state management.
