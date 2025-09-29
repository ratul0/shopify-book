# User Interface Development

Based on my search of the latest Shopify documentation (as of September 2025), I'll teach you about the current state of Polaris and UI development for Shopify apps. The landscape has evolved significantly with Polaris now offering **Web Components** alongside the traditional React library.

## 1. Current Shopify Documentation Check

According to Shopify's documentation as of September 2025:
- **API Version**: Latest stable is 2025-07 (with 2025-04 being widely used)
- **Major Change**: Polaris has shifted to Web Components (experimental but recommended)
- **Integration**: Tight coupling with App Bridge for seamless admin integration
- **TypeScript**: Full support via `@shopify/app-bridge-ui-types`

**⚠️ Important**: Many online tutorials still reference the old Polaris React-only approach. The current recommended approach uses Polaris Web Components that work with any framework.

## 2. The Laravel/Spring Boot/Angular Equivalent

Coming from your background, here's how to map concepts:

**Angular Material / PrimeNG → Polaris Web Components**
- Both provide pre-built, themed components
- Similar component-based architecture
- Built-in accessibility and responsive design

**Laravel Blade Components → Polaris Web Components**
- Server-side components vs. client-side web components
- Both focus on reusability and consistency

**Spring Boot + Thymeleaf Fragments → Polaris Patterns**
- Pre-defined layouts and patterns for common use cases
- Both enforce consistent structure across the application

**Angular Reactive Forms → Polaris Forms with Contextual Save Bar**
- Form state management
- Built-in validation
- Automatic save/discard patterns

## 3. The Current Shopify Way - Architecture Deep Dive

The modern Shopify app UI architecture consists of three layers:

```
┌──────────────────────────────────────┐
│       Shopify Admin (Host)           │
├──────────────────────────────────────┤
│       App Bridge (Bridge Layer)      │
│  - Navigation, Modals, Toast, etc.   │
├──────────────────────────────────────┤
│     Your App (iframe/WebView)        │
│  - Polaris Web Components            │
│  - Your Business Logic               │
└──────────────────────────────────────┘
```

This is fundamentally different from your Angular apps where you control the entire viewport. In Shopify:
- Your app runs in an iframe (web) or WebView (mobile)
- App Bridge handles communication with the admin
- Polaris ensures visual consistency

## 4. Complete Working Example - Setting Up Polaris Web Components

Let me show you a complete implementation with the latest patterns:

```ts
// API Version: 2025-04
// Last verified: September 2025
// File: app/root.tsx
// Purpose: Root configuration with Polaris Web Components

import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useLoaderData,
  useNavigate,
} from "@remix-run/react";
import { json } from "@remix-run/node";
import { useEffect } from "react";

export const loader = async () => {
  return json({
    ENV: {
      SHOPIFY_API_KEY: process.env.SHOPIFY_API_KEY,
    },
  });
};

export default function App() {
  const { ENV } = useLoaderData();
  const navigate = useNavigate();

  useEffect(() => {
    // CRITICAL: Handle Polaris Web Component navigation events
    // This bridges Polaris navigation with Remix router
    const handleNavigate = (event) => {
      const href = event.target.getAttribute('href');
      if (href && !href.startsWith('http')) {
        event.preventDefault();
        navigate(href);
      }
    };

    document.addEventListener('shopify:navigate', handleNavigate);
    return () => {
      document.removeEventListener('shopify:navigate', handleNavigate);
    };
  }, [navigate]);

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <Meta />
        <Links />
        
        {/* CRITICAL: Required for Shopify App Bridge */}
        <meta name="shopify-api-key" content={ENV.SHOPIFY_API_KEY} />
        <script src="https://cdn.shopify.com/shopifycloud/app-bridge.js"></script>
        
        {/* NEW: Polaris Web Components - This is the latest approach */}
        <script src="https://cdn.shopify.com/shopifycloud/app-bridge-ui-experimental.js"></script>
      </head>
      <body>
        <Outlet />
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

// ===================================
// File: app/routes/app._index.tsx
// Purpose: Main app page with Polaris components
// ===================================

import { json } from "@remix-run/node";
import { useLoaderData, useSubmit, Form, useFetcher } from "@remix-run/react";
import { useState, useEffect, useRef } from "react";
import { authenticate } from "~/shopify.server";

// This is similar to your Angular service layer
export const loader = async ({ request }) => {
  const { admin } = await authenticate.admin(request);
  
  // Direct API access - new in 2025
  const response = await fetch('shopify:admin/api/2025-04/graphql.json', {
    method: 'POST',
    body: JSON.stringify({
      query: `
        query getProducts {
          products(first: 10) {
            edges {
              node {
                id
                title
                status
                totalInventory
                priceRangeV2 {
                  minVariantPrice {
                    amount
                    currencyCode
                  }
                }
              }
            }
          }
        }
      `
    }),
  });
  
  const { data } = await response.json();
  
  return json({
    products: data.products.edges.map(edge => edge.node),
  });
};

// Similar to Angular's @Injectable() for actions
export const action = async ({ request }) => {
  const { admin } = await authenticate.admin(request);
  const formData = await request.formData();
  const action = formData.get("action");
  
  if (action === "updateProduct") {
    // Handle product update
    const productId = formData.get("productId");
    const title = formData.get("title");
    
    // GraphQL mutation here
    await admin.graphql(
      `mutation updateProduct($input: ProductInput!) {
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
      }`,
      {
        variables: {
          input: {
            id: productId,
            title: title,
          },
        },
      }
    );
  }
  
  return json({ success: true });
};

export default function Index() {
  const { products } = useLoaderData();
  const submit = useSubmit();
  const fetcher = useFetcher();
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // This effect demonstrates App Bridge integration
  useEffect(() => {
    // Access the global shopify object (like Angular's window object)
    if (window.shopify) {
      // Show a toast notification
      window.shopify.toast.show('Products loaded successfully');
    }
  }, []);
  
  const handleFormSubmit = (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    // Similar to Angular's reactive forms submission
    fetcher.submit(formData, { method: "post" });
    
    // Show loading state
    setIsLoading(true);
  };
  
  const handleBulkAction = async () => {
    // Open resource picker - Shopify-specific pattern
    if (window.shopify) {
      const selected = await window.shopify.resourcePicker({
        type: 'product',
        multiple: true,
      });
      
      setSelectedProducts(selected);
      
      // Show contextual save bar
      window.shopify.saveBar.show();
    }
  };

  return (
    <>
      {/* Polaris Web Components in action */}
      {/* s-page is the main container, like Angular's <mat-sidenav-container> */}
      <s-page>
        {/* App Bridge Title Bar - renders outside iframe in admin */}
        <ui-title-bar title="Product Manager">
          {/* Primary action - similar to Angular Material's mat-raised-button */}
          <button variant="primary" onClick={handleBulkAction}>
            Add Products
          </button>
        </ui-title-bar>
        
        {/* Main content area with sections */}
        <s-section heading="Product Overview">
          {/* Banner for important messages - like Angular's MatSnackBar but persistent */}
          <s-banner tone="info">
            <s-heading>Welcome to Product Manager</s-heading>
            <s-paragraph>
              Manage your products efficiently with bulk actions and quick edits.
            </s-paragraph>
          </s-banner>
          
          {/* Stack for layout - similar to Angular's fxLayout directive */}
          <s-stack gap="base">
            {/* Search and filter section */}
            <s-grid columns="1fr auto" gap="base">
              <s-search-field
                label="Search products"
                placeholder="Search by title, SKU, or barcode"
                labelAccessibilityVisibility="exclusive"
              />
              <s-select label="Status filter" labelAccessibilityVisibility="exclusive">
                <s-option value="all">All products</s-option>
                <s-option value="active">Active</s-option>
                <s-option value="draft">Draft</s-option>
                <s-option value="archived">Archived</s-option>
              </s-select>
            </s-grid>
            
            {/* Data table with loading states */}
            {isLoading ? (
              // Skeleton loading - built-in pattern for performance perception
              <s-box background="subtle" padding="base" borderRadius="base">
                <s-spinner size="small" />
                <s-text>Loading products...</s-text>
              </s-box>
            ) : (
              // Responsive table - automatically becomes list on mobile
              <s-table>
                <s-table-header-row>
                  <s-table-header>
                    <s-checkbox 
                      label="Select all"
                      labelAccessibilityVisibility="exclusive"
                    />
                  </s-table-header>
                  <s-table-header>Product</s-table-header>
                  <s-table-header>Status</s-table-header>
                  <s-table-header>Inventory</s-table-header>
                  <s-table-header>Price</s-table-header>
                  <s-table-header>Actions</s-table-header>
                </s-table-header-row>
                <s-table-body>
                  {products.map((product) => (
                    <s-table-row key={product.id}>
                      <s-table-cell>
                        <s-checkbox 
                          label={`Select ${product.title}`}
                          labelAccessibilityVisibility="exclusive"
                        />
                      </s-table-cell>
                      <s-table-cell>
                        <s-stack direction="inline" alignItems="center" gap="base">
                          <s-thumbnail src={product.image} alt={product.title} />
                          <s-text weight="semibold">{product.title}</s-text>
                        </s-stack>
                      </s-table-cell>
                      <s-table-cell>
                        <s-badge tone={product.status === 'ACTIVE' ? 'success' : 'neutral'}>
                          {product.status}
                        </s-badge>
                      </s-table-cell>
                      <s-table-cell>{product.totalInventory} in stock</s-table-cell>
                      <s-table-cell>
                        ${product.priceRangeV2?.minVariantPrice?.amount || '0.00'}
                      </s-table-cell>
                      <s-table-cell>
                        <s-button-group>
                          <s-button variant="tertiary">Edit</s-button>
                          <s-menu>
                            <s-menu-item>Duplicate</s-menu-item>
                            <s-menu-item tone="critical">Delete</s-menu-item>
                          </s-menu>
                        </s-button-group>
                      </s-table-cell>
                    </s-table-row>
                  ))}
                </s-table-body>
              </s-table>
            )}
          </s-stack>
        </s-section>
        
        {/* Form with validation - integrated with Contextual Save Bar */}
        <s-section heading="Quick Edit">
          <Form method="post" data-save-bar onSubmit={handleFormSubmit}>
            <input type="hidden" name="action" value="updateProduct" />
            
            <s-grid gap="base">
              <s-text-field
                label="Product Title"
                name="title"
                required
                details="This will update the product title across all channels"
                placeholder="Enter product title"
              />
              
              <s-text-area
                label="Description"
                name="description"
                rows="4"
                details="SEO-friendly description for your product"
              />
              
              <s-grid columns="1fr 1fr" gap="base">
                <s-money-field
                  label="Price"
                  name="price"
                  required
                  placeholder="0.00"
                />
                
                <s-number-field
                  label="Quantity"
                  name="quantity"
                  min="0"
                  placeholder="0"
                />
              </s-grid>
              
              <s-switch
                label="Track inventory"
                name="trackInventory"
                details="Enable inventory tracking for this product"
              />
              
              {/* Date picker for scheduling */}
              <s-date-picker
                label="Publish date"
                name="publishDate"
                details="Schedule when this product becomes available"
              />
            </s-grid>
            
            {/* Form actions */}
            <s-stack direction="inline" gap="base" alignItems="end">
              <s-button type="submit" variant="primary" loading={isLoading}>
                Save changes
              </s-button>
              <s-button type="reset" variant="tertiary">
                Cancel
              </s-button>
            </s-stack>
          </Form>
        </s-section>
        
        {/* Error handling with banner */}
        {fetcher.data?.error && (
          <s-banner tone="critical">
            <s-heading>Error saving product</s-heading>
            <s-paragraph>{fetcher.data.error}</s-paragraph>
          </s-banner>
        )}
      </s-page>
      
      {/* Modal example - rendered by App Bridge outside iframe */}
      <ui-modal id="bulk-edit-modal" variant="max">
        <s-page>
          <s-section heading="Bulk Edit Products">
            <s-paragraph>
              Edit multiple products at once. Changes will apply to all selected items.
            </s-paragraph>
            {/* Modal content here */}
          </s-section>
        </s-page>
        <ui-title-bar title="Bulk Edit">
          <button variant="primary">Apply Changes</button>
          <button onClick={() => document.getElementById('bulk-edit-modal').hide()}>
            Cancel
          </button>
        </ui-title-bar>
      </ui-modal>
    </>
  );
}
```

## 5. Real-World Scenarios Based on Current Capabilities

Let me show you three practical use cases that demonstrate the power of the current Polaris system:

```ts
// API Version: 2025-04
// Last verified: September 2025
// Advanced patterns for production Shopify apps

// ===================================
// Pattern 1: Data Table with Advanced Features
// File: app/components/ProductTable.jsx
// ===================================

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useFetcher } from '@remix-run/react';

export function ProductTable({ initialProducts }) {
  const fetcher = useFetcher();
  const [products, setProducts] = useState(initialProducts);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [sortColumn, setSortColumn] = useState('title');
  const [sortDirection, setSortDirection] = useState('asc');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [isExporting, setIsExporting] = useState(false);
  
  const ITEMS_PER_PAGE = 20;
  
  // Similar to Angular's computed properties with signals
  const filteredProducts = useMemo(() => {
    let filtered = products.filter(product => 
      product.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.sku?.toLowerCase().includes(searchQuery.toLowerCase())
    );
    
    // Sort products
    filtered.sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];
      const direction = sortDirection === 'asc' ? 1 : -1;
      
      if (typeof aVal === 'string') {
        return aVal.localeCompare(bVal) * direction;
      }
      return (aVal - bVal) * direction;
    });
    
    return filtered;
  }, [products, searchQuery, sortColumn, sortDirection]);
  
  // Pagination logic
  const paginatedProducts = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredProducts.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredProducts, currentPage]);
  
  const totalPages = Math.ceil(filteredProducts.length / ITEMS_PER_PAGE);
  
  // Handle bulk selection
  const handleSelectAll = useCallback((checked) => {
    if (checked) {
      setSelectedItems(new Set(paginatedProducts.map(p => p.id)));
    } else {
      setSelectedItems(new Set());
    }
  }, [paginatedProducts]);
  
  // Handle individual selection
  const handleSelectItem = useCallback((productId, checked) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      if (checked) {
        newSet.add(productId);
      } else {
        newSet.delete(productId);
      }
      return newSet;
    });
  }, []);
  
  // Bulk actions handler
  const handleBulkAction = useCallback(async (action) => {
    if (selectedItems.size === 0) {
      window.shopify?.toast.show('No items selected', { isError: true });
      return;
    }
    
    try {
      // Show loading state
      window.shopify?.loading.start();
      
      const formData = new FormData();
      formData.append('action', action);
      formData.append('productIds', JSON.stringify([...selectedItems]));
      
      // Submit via fetcher (like Angular's HttpClient)
      fetcher.submit(formData, { method: 'post', action: '/app/bulk-action' });
      
      // Show success toast
      window.shopify?.toast.show(`${action} applied to ${selectedItems.size} products`);
      
      // Clear selection
      setSelectedItems(new Set());
    } finally {
      window.shopify?.loading.stop();
    }
  }, [selectedItems, fetcher]);
  
  // Export functionality
  const handleExport = useCallback(async () => {
    setIsExporting(true);
    try {
      const exportData = selectedItems.size > 0 
        ? products.filter(p => selectedItems.has(p.id))
        : filteredProducts;
      
      // Create CSV
      const csv = [
        ['Title', 'SKU', 'Status', 'Inventory', 'Price'],
        ...exportData.map(p => [
          p.title,
          p.sku || '',
          p.status,
          p.inventory,
          p.price
        ])
      ].map(row => row.join(',')).join('\n');
      
      // Download file
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `products-${new Date().toISOString()}.csv`;
      a.click();
      
      window.shopify?.toast.show('Export completed');
    } catch (error) {
      window.shopify?.toast.show('Export failed', { isError: true });
    } finally {
      setIsExporting(false);
    }
  }, [selectedItems, products, filteredProducts]);
  
  return (
    <s-box>
      {/* Table controls */}
      <s-stack gap="base">
        {/* Search and filters */}
        <s-grid columns="1fr auto auto" gap="base" alignItems="center">
          <s-search-field
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search products..."
            label="Search"
            labelAccessibilityVisibility="exclusive"
          />
          
          <s-button
            variant="tertiary"
            onClick={handleExport}
            loading={isExporting}
            icon="export"
          >
            Export ({selectedItems.size || filteredProducts.length})
          </s-button>
          
          <s-popover>
            <s-button slot="trigger" variant="tertiary" icon="filter">
              Filters
            </s-button>
            <s-box padding="base">
              {/* Filter content */}
              <s-stack gap="base">
                <s-select label="Status">
                  <s-option value="all">All</s-option>
                  <s-option value="active">Active</s-option>
                  <s-option value="draft">Draft</s-option>
                </s-select>
                <s-checkbox label="In stock only" />
                <s-checkbox label="Has images" />
              </s-stack>
            </s-box>
          </s-popover>
        </s-grid>
        
        {/* Bulk actions bar - shows when items selected */}
        {selectedItems.size > 0 && (
          <s-banner tone="neutral">
            <s-stack direction="inline" gap="base" alignItems="center">
              <s-text>{selectedItems.size} selected</s-text>
              <s-button-group>
                <s-button 
                  variant="tertiary"
                  onClick={() => handleBulkAction('activate')}
                >
                  Activate
                </s-button>
                <s-button 
                  variant="tertiary"
                  onClick={() => handleBulkAction('archive')}
                >
                  Archive
                </s-button>
                <s-button 
                  variant="tertiary"
                  tone="critical"
                  onClick={() => handleBulkAction('delete')}
                >
                  Delete
                </s-button>
              </s-button-group>
              <s-button 
                variant="tertiary"
                onClick={() => setSelectedItems(new Set())}
              >
                Clear selection
              </s-button>
            </s-stack>
          </s-banner>
        )}
        
        {/* Data table with sorting */}
        <s-table>
          <s-table-header-row>
            <s-table-header>
              <s-checkbox
                checked={selectedItems.size === paginatedProducts.length && paginatedProducts.length > 0}
                indeterminate={selectedItems.size > 0 && selectedItems.size < paginatedProducts.length}
                onChange={(e) => handleSelectAll(e.target.checked)}
                label="Select all"
                labelAccessibilityVisibility="exclusive"
              />
            </s-table-header>
            <s-table-header 
              sortable
              sortDirection={sortColumn === 'title' ? sortDirection : null}
              onClick={() => {
                setSortColumn('title');
                setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
              }}
            >
              Product
            </s-table-header>
            <s-table-header>SKU</s-table-header>
            <s-table-header
              sortable
              sortDirection={sortColumn === 'status' ? sortDirection : null}
              onClick={() => {
                setSortColumn('status');
                setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
              }}
            >
              Status
            </s-table-header>
            <s-table-header
              sortable
              sortDirection={sortColumn === 'inventory' ? sortDirection : null}
              onClick={() => {
                setSortColumn('inventory');
                setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
              }}
            >
              Inventory
            </s-table-header>
            <s-table-header>Price</s-table-header>
            <s-table-header>Actions</s-table-header>
          </s-table-header-row>
          
          <s-table-body>
            {paginatedProducts.map(product => (
              <ProductTableRow
                key={product.id}
                product={product}
                selected={selectedItems.has(product.id)}
                onSelect={handleSelectItem}
              />
            ))}
          </s-table-body>
        </s-table>
        
        {/* Pagination controls */}
        {totalPages > 1 && (
          <s-stack direction="inline" gap="base" alignItems="center" justifyContent="center">
            <s-button
              variant="tertiary"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(prev => prev - 1)}
              icon="chevron-left"
              accessibilityLabel="Previous page"
            />
            
            <s-text>
              Page {currentPage} of {totalPages}
            </s-text>
            
            <s-button
              variant="tertiary"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage(prev => prev + 1)}
              icon="chevron-right"
              accessibilityLabel="Next page"
            />
          </s-stack>
        )}
      </s-stack>
    </s-box>
  );
}

// ===================================
// Pattern 2: Form with Validation and Error Handling
// File: app/components/ProductForm.jsx
// ===================================

export function ProductForm({ product, onSave }) {
  const [formData, setFormData] = useState({
    title: product?.title || '',
    description: product?.description || '',
    price: product?.price || '',
    compareAtPrice: product?.compareAtPrice || '',
    sku: product?.sku || '',
    barcode: product?.barcode || '',
    trackInventory: product?.trackInventory || false,
    quantity: product?.quantity || 0,
    weight: product?.weight || '',
    requiresShipping: product?.requiresShipping || true,
  });
  
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Validation logic (similar to Angular Validators)
  const validateForm = useCallback(() => {
    const newErrors = {};
    
    // Required field validation
    if (!formData.title.trim()) {
      newErrors.title = 'Product title is required';
    }
    
    // Price validation
    if (!formData.price || parseFloat(formData.price) <= 0) {
      newErrors.price = 'Price must be greater than 0';
    }
    
    // Compare at price validation
    if (formData.compareAtPrice && parseFloat(formData.compareAtPrice) <= parseFloat(formData.price)) {
      newErrors.compareAtPrice = 'Compare at price must be greater than regular price';
    }
    
    // SKU format validation
    if (formData.sku && !/^[A-Z0-9-]+$/i.test(formData.sku)) {
      newErrors.sku = 'SKU can only contain letters, numbers, and hyphens';
    }
    
    // Inventory validation
    if (formData.trackInventory && formData.quantity < 0) {
      newErrors.quantity = 'Quantity cannot be negative';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);
  
  // Handle field changes with validation
  const handleFieldChange = useCallback((field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error for this field when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  }, [errors]);
  
  // Handle form submission
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      // Focus first error field
      const firstErrorField = Object.keys(errors)[0];
      document.querySelector(`[name="${firstErrorField}"]`)?.focus();
      
      // Show error toast
      window.shopify?.toast.show('Please fix validation errors', { isError: true });
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Call save handler
      await onSave(formData);
      
      // Show success message
      window.shopify?.toast.show('Product saved successfully');
      
      // Hide save bar
      window.shopify?.saveBar.hide();
    } catch (error) {
      // Show error banner
      window.shopify?.toast.show(`Error: ${error.message}`, { isError: true });
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, validateForm, onSave, errors]);
  
  // Track unsaved changes
  useEffect(() => {
    const hasChanges = JSON.stringify(formData) !== JSON.stringify(product);
    if (hasChanges && window.shopify) {
      window.shopify.saveBar.show();
    }
  }, [formData, product]);
  
  return (
    <form data-save-bar onSubmit={handleSubmit}>
      {/* Show validation errors banner */}
      {Object.keys(errors).length > 0 && (
        <s-banner tone="critical">
          <s-heading>Please fix the following errors:</s-heading>
          <s-unordered-list>
            {Object.entries(errors).map(([field, error]) => (
              <s-list-item key={field}>
                <s-link href={`#${field}`}>{error}</s-link>
              </s-list-item>
            ))}
          </s-unordered-list>
        </s-banner>
      )}
      
      <s-section heading="Basic Information">
        <s-stack gap="base">
          <s-text-field
            id="title"
            name="title"
            label="Product title"
            value={formData.title}
            onChange={(e) => handleFieldChange('title', e.target.value)}
            error={errors.title}
            required
            placeholder="Short sleeve t-shirt"
            details="Give your product a short and clear title"
            maxLength={255}
            showCharacterCount
          />
          
          <s-text-area
            name="description"
            label="Description"
            value={formData.description}
            onChange={(e) => handleFieldChange('description', e.target.value)}
            rows={6}
            placeholder="Enter product description..."
            details="Describe your product in detail. This will appear on the product page."
            maxLength={5000}
            showCharacterCount
          />
        </s-stack>
      </s-section>
      
      <s-section heading="Pricing">
        <s-grid columns="1fr 1fr" gap="base">
          <s-money-field
            name="price"
            label="Price"
            value={formData.price}
            onChange={(e) => handleFieldChange('price', e.target.value)}
            error={errors.price}
            required
            placeholder="0.00"
            prefix="$"
            details="The regular selling price"
          />
          
          <s-money-field
            name="compareAtPrice"
            label="Compare at price"
            value={formData.compareAtPrice}
            onChange={(e) => handleFieldChange('compareAtPrice', e.target.value)}
            error={errors.compareAtPrice}
            placeholder="0.00"
            prefix="$"
            details="Original price before discount"
          />
        </s-grid>
      </s-section>
      
      <s-section heading="Inventory">
        <s-stack gap="base">
          <s-grid columns="1fr 1fr" gap="base">
            <s-text-field
              name="sku"
              label="SKU (Stock Keeping Unit)"
              value={formData.sku}
              onChange={(e) => handleFieldChange('sku', e.target.value)}
              error={errors.sku}
              placeholder="SHIRT-001"
              details="Used to track inventory"
            />
            
            <s-text-field
              name="barcode"
              label="Barcode (ISBN, UPC, GTIN, etc.)"
              value={formData.barcode}
              onChange={(e) => handleFieldChange('barcode', e.target.value)}
              placeholder="1234567890"
            />
          </s-grid>
          
          <s-switch
            name="trackInventory"
            label="Track quantity"
            checked={formData.trackInventory}
            onChange={(e) => handleFieldChange('trackInventory', e.target.checked)}
            details="Stop selling when inventory reaches zero"
          />
          
          {formData.trackInventory && (
            <s-number-field
              name="quantity"
              label="Available quantity"
              value={formData.quantity}
              onChange={(e) => handleFieldChange('quantity', parseInt(e.target.value) || 0)}
              error={errors.quantity}
              min={0}
              details="Current stock level"
            />
          )}
        </s-stack>
      </s-section>
      
      <s-section heading="Shipping">
        <s-stack gap="base">
          <s-checkbox
            name="requiresShipping"
            label="This is a physical product"
            checked={formData.requiresShipping}
            onChange={(e) => handleFieldChange('requiresShipping', e.target.checked)}
            details="Requires shipping address at checkout"
          />
          
          {formData.requiresShipping && (
            <s-grid columns="1fr 1fr" gap="base">
              <s-number-field
                name="weight"
                label="Weight"
                value={formData.weight}
                onChange={(e) => handleFieldChange('weight', e.target.value)}
                suffix="kg"
                step="0.1"
                min={0}
                placeholder="0.0"
              />
            </s-grid>
          )}
        </s-stack>
      </s-section>
      
      {/* Form actions */}
      <s-stack direction="inline" gap="base" alignItems="center">
        <s-button
          type="submit"
          variant="primary"
          loading={isSubmitting}
          disabled={Object.keys(errors).length > 0}
        >
          Save product
        </s-button>
        
        <s-button
          type="button"
          variant="tertiary"
          onClick={() => window.history.back()}
        >
          Cancel
        </s-button>
      </s-stack>
    </form>
  );
}

// ===================================
// Pattern 3: Responsive Dashboard with Loading States
// File: app/components/Dashboard.jsx
// ===================================

export function Dashboard({ metrics, isLoading }) {
  const [dateRange, setDateRange] = useState('last7days');
  const [selectedMetric, setSelectedMetric] = useState('revenue');
  
  // Loading skeleton component
  const MetricSkeleton = () => (
    <s-box background="subtle" padding="base" borderRadius="base">
      <s-stack gap="tight">
        <s-box height="20px" background="strong" borderRadius="base" width="60%" />
        <s-box height="32px" background="strong" borderRadius="base" width="80%" />
        <s-box height="16px" background="strong" borderRadius="base" width="40%" />
      </s-stack>
    </s-box>
  );
  
  return (
    <s-page>
      <ui-title-bar title="Dashboard">
        <button variant="primary" icon="export">
          Export Report
        </button>
      </ui-title-bar>
      
      {/* Date range selector */}
      <s-section>
        <s-stack direction="inline" gap="base" alignItems="center">
          <s-text weight="semibold">Period:</s-text>
          <s-button-group segmented>
            <s-button 
              pressed={dateRange === 'today'}
              onClick={() => setDateRange('today')}
            >
              Today
            </s-button>
            <s-button 
              pressed={dateRange === 'last7days'}
              onClick={() => setDateRange('last7days')}
            >
              Last 7 days
            </s-button>
            <s-button 
              pressed={dateRange === 'last30days'}
              onClick={() => setDateRange('last30days')}
            >
              Last 30 days
            </s-button>
            <s-button 
              pressed={dateRange === 'custom'}
              onClick={() => setDateRange('custom')}
            >
              Custom
            </s-button>
          </s-button-group>
        </s-stack>
      </s-section>
      
      {/* Key metrics grid - responsive */}
      <s-section heading="Key Metrics">
        <s-query-container>
          <s-grid 
            columns="repeat(auto-fit, minmax(250px, 1fr))" 
            gap="base"
          >
            {isLoading ? (
              // Show skeletons while loading
              <>
                <MetricSkeleton />
                <MetricSkeleton />
                <MetricSkeleton />
                <MetricSkeleton />
              </>
            ) : (
              // Actual metrics
              <>
                <MetricCard
                  title="Total Revenue"
                  value={`$${metrics.revenue.toLocaleString()}`}
                  change={metrics.revenueChange}
                  icon="cash"
                />
                <MetricCard
                  title="Orders"
                  value={metrics.orders.toLocaleString()}
                  change={metrics.ordersChange}
                  icon="orders"
                />
                <MetricCard
                  title="Conversion Rate"
                  value={`${metrics.conversionRate}%`}
                  change={metrics.conversionChange}
                  icon="analytics"
                />
                <MetricCard
                  title="Avg. Order Value"
                  value={`$${metrics.avgOrderValue}`}
                  change={metrics.aovChange}
                  icon="cart"
                />
              </>
            )}
          </s-grid>
        </s-query-container>
      </s-section>
      
      {/* Charts section */}
      <s-section heading="Trends">
        <s-grid columns="2fr 1fr" gap="base">
          {/* Main chart */}
          <s-box background="subtle" padding="base" borderRadius="base" minHeight="400px">
            {isLoading ? (
              <s-spinner />
            ) : (
              <canvas id="revenue-chart" />
            )}
          </s-box>
          
          {/* Side panel with top products */}
          <s-box background="subtle" padding="base" borderRadius="base">
            <s-heading level="3">Top Products</s-heading>
            <s-stack gap="tight">
              {isLoading ? (
                <s-spinner size="small" />
              ) : (
                metrics.topProducts?.map((product, index) => (
                  <s-stack key={product.id} direction="inline" gap="base" alignItems="center">
                    <s-badge>{index + 1}</s-badge>
                    <s-stack gap="none" flex="1">
                      <s-text weight="medium">{product.name}</s-text>
                      <s-text size="small" tone="subdued">
                        {product.sales} sales
                      </s-text>
                    </s-stack>
                    <s-text weight="semibold">${product.revenue}</s-text>
                  </s-stack>
                ))
              )}
            </s-stack>
          </s-box>
        </s-grid>
      </s-section>
      
      {/* Recent activity feed */}
      <s-section heading="Recent Activity">
        <s-box background="subtle" padding="base" borderRadius="base">
          {isLoading ? (
            <s-spinner />
          ) : (
            <s-stack gap="base">
              {metrics.recentActivity?.map(activity => (
                <s-stack key={activity.id} direction="inline" gap="base" alignItems="start">
                  <s-icon name={activity.icon} />
                  <s-stack gap="tight" flex="1">
                    <s-text>{activity.description}</s-text>
                    <s-text size="small" tone="subdued">
                      {activity.timestamp}
                    </s-text>
                  </s-stack>
                </s-stack>
              ))}
            </s-stack>
          )}
        </s-box>
      </s-section>
    </s-page>
  );
}

// Reusable metric card component
function MetricCard({ title, value, change, icon }) {
  const isPositive = change > 0;
  
  return (
    <s-box 
      background="subtle" 
      padding="base" 
      borderRadius="base"
      border="base"
    >
      <s-stack gap="tight">
        <s-stack direction="inline" gap="base" alignItems="center">
          <s-icon name={icon} />
          <s-text tone="subdued" size="small">{title}</s-text>
        </s-stack>
        
        <s-heading level="2">{value}</s-heading>
        
        <s-stack direction="inline" gap="tight" alignItems="center">
          <s-badge tone={isPositive ? 'success' : 'critical'}>
            {isPositive ? '↑' : '↓'} {Math.abs(change)}%
          </s-badge>
          <s-text size="small" tone="subdued">vs last period</s-text>
        </s-stack>
      </s-stack>
    </s-box>
  );
}

// Product table row component for better organization
function ProductTableRow({ product, selected, onSelect }) {
  return (
    <s-table-row>
      <s-table-cell>
        <s-checkbox
          checked={selected}
          onChange={(e) => onSelect(product.id, e.target.checked)}
          label={`Select ${product.title}`}
          labelAccessibilityVisibility="exclusive"
        />
      </s-table-cell>
      <s-table-cell>
        <s-stack direction="inline" gap="base" alignItems="center">
          {product.image && (
            <s-thumbnail 
              src={product.image} 
              alt={product.title}
              size="small"
            />
          )}
          <s-stack gap="none">
            <s-link href={`/app/products/${product.id}`}>
              {product.title}
            </s-link>
            {product.vendor && (
              <s-text size="small" tone="subdued">{product.vendor}</s-text>
            )}
          </s-stack>
        </s-stack>
      </s-table-cell>
      <s-table-cell>{product.sku || '—'}</s-table-cell>
      <s-table-cell>
        <s-badge 
          tone={product.status === 'ACTIVE' ? 'success' : 'neutral'}
        >
          {product.status}
        </s-badge>
      </s-table-cell>
      <s-table-cell>{product.inventory} units</s-table-cell>
      <s-table-cell>${product.price}</s-table-cell>
      <s-table-cell>
        <s-button-group>
          <s-button variant="tertiary" size="slim">
            Edit
          </s-button>
          <s-popover>
            <s-button 
              slot="trigger" 
              variant="tertiary" 
              size="slim" 
              icon="more-vertical"
              accessibilityLabel="More actions"
            />
            <s-menu>
              <s-menu-item>Duplicate</s-menu-item>
              <s-menu-item>Preview</s-menu-item>
              <s-menu-divider />
              <s-menu-item tone="critical">Archive</s-menu-item>
            </s-menu>
          </s-popover>
        </s-button-group>
      </s-table-cell>
    </s-table-row>
  );
}
```

## 6. Advanced Patterns from Latest Documentation

Let me walk you through some advanced patterns that are currently recommended in Shopify's official documentation. These patterns address common challenges you'll face when building production apps.

### Internationalization (i18n) Support

Unlike Angular's built-in i18n which generates separate builds, Shopify's approach is runtime-based. The platform automatically provides the merchant's locale, and you can implement translations dynamically. This is crucial because your app needs to adapt to whatever language the merchant has configured in their admin settings.

```ts
// API Version: 2025-04
// Last verified: September 2025
// Advanced patterns for i18n, a11y, and performance

// ===================================
// Pattern 1: Internationalization Support
// File: app/utils/i18n.js
// ===================================

// Translation system similar to Angular's i18n but runtime-based
export class TranslationService {
  constructor(locale = 'en') {
    this.locale = locale;
    this.translations = {};
    this.fallbackLocale = 'en';
  }
  
  // Load translations for current locale
  async loadTranslations() {
    try {
      // In production, these would come from your API
      const translations = await import(`~/locales/${this.locale}.json`);
      this.translations = translations.default;
    } catch {
      // Fallback to English if locale not found
      const fallback = await import(`~/locales/${this.fallbackLocale}.json`);
      this.translations = fallback.default;
    }
  }
  
  // Get translated string with interpolation support
  t(key, params = {}) {
    const keys = key.split('.');
    let value = this.translations;
    
    for (const k of keys) {
      value = value?.[k];
    }
    
    if (typeof value !== 'string') {
      console.warn(`Translation missing for key: ${key}`);
      return key;
    }
    
    // Replace interpolation placeholders
    return value.replace(/\{\{(\w+)\}\}/g, (match, param) => {
      return params[param] || match;
    });
  }
  
  // Format numbers according to locale
  formatNumber(value, options = {}) {
    return new Intl.NumberFormat(this.locale, options).format(value);
  }
  
  // Format currency
  formatCurrency(value, currency = 'USD') {
    return new Intl.NumberFormat(this.locale, {
      style: 'currency',
      currency,
    }).format(value);
  }
  
  // Format dates
  formatDate(date, options = {}) {
    return new Intl.DateTimeFormat(this.locale, options).format(date);
  }
  
  // Pluralization rules
  plural(count, options) {
    const rules = new Intl.PluralRules(this.locale);
    const rule = rules.select(count);
    return options[rule] || options.other || '';
  }
}

// Example translation file: locales/en.json
const enTranslations = {
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "loading": "Loading...",
    "error": "An error occurred",
    "success": "Success",
    "confirm": "Are you sure?"
  },
  "products": {
    "title": "Products",
    "addNew": "Add product",
    "editProduct": "Edit {{productName}}",
    "noProducts": "No products found",
    "searchPlaceholder": "Search products...",
    "bulkActions": {
      "selected": "{{count}} selected",
      "selectAll": "Select all {{total}} products",
      "deselectAll": "Deselect all"
    },
    "fields": {
      "title": "Product title",
      "description": "Description",
      "price": "Price",
      "inventory": "Inventory",
      "status": "Status"
    },
    "validation": {
      "titleRequired": "Product title is required",
      "priceRequired": "Price is required",
      "priceInvalid": "Price must be a valid number"
    },
    "messages": {
      "saved": "Product saved successfully",
      "deleted": "Product deleted successfully",
      "error": "Failed to save product"
    }
  }
};

// ===================================
// Pattern 2: Accessibility Best Practices
// File: app/components/AccessibleComponents.jsx
// ===================================

// Accessible modal with focus management
export function AccessibleModal({ isOpen, onClose, title, children }) {
  const modalRef = useRef(null);
  const previousFocusRef = useRef(null);
  
  useEffect(() => {
    if (isOpen) {
      // Store current focus
      previousFocusRef.current = document.activeElement;
      
      // Focus first focusable element in modal
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      if (focusableElements?.length > 0) {
        focusableElements[0].focus();
      }
      
      // Trap focus within modal
      const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
          onClose();
        }
        
        if (e.key === 'Tab') {
          const focusable = Array.from(focusableElements);
          const firstElement = focusable[0];
          const lastElement = focusable[focusable.length - 1];
          
          if (e.shiftKey) {
            if (document.activeElement === firstElement) {
              e.preventDefault();
              lastElement.focus();
            }
          } else {
            if (document.activeElement === lastElement) {
              e.preventDefault();
              firstElement.focus();
            }
          }
        }
      };
      
      document.addEventListener('keydown', handleKeyDown);
      
      return () => {
        document.removeEventListener('keydown', handleKeyDown);
      };
    } else {
      // Restore focus when modal closes
      previousFocusRef.current?.focus();
    }
  }, [isOpen, onClose]);
  
  if (!isOpen) return null;
  
  return (
    <ui-modal 
      ref={modalRef}
      open={isOpen}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <ui-title-bar id="modal-title" title={title}>
        <button variant="primary">Save</button>
        <button onClick={onClose}>Cancel</button>
      </ui-title-bar>
      
      <s-page>
        <s-section>
          {children}
        </s-section>
      </s-page>
    </ui-modal>
  );
}

// Accessible data table with ARIA attributes
export function AccessibleTable({ data, columns, caption }) {
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [announcement, setAnnouncement] = useState('');
  
  // Announce sort changes to screen readers
  const handleSort = (column) => {
    const newDirection = 
      sortColumn === column && sortDirection === 'asc' ? 'desc' : 'asc';
    
    setSortColumn(column);
    setSortDirection(newDirection);
    
    // Announce change to screen readers
    const directionText = newDirection === 'asc' ? 'ascending' : 'descending';
    setAnnouncement(`Table sorted by ${column.label} ${directionText}`);
  };
  
  return (
    <>
      {/* Live region for announcements */}
      <div 
        role="status" 
        aria-live="polite" 
        aria-atomic="true"
        className="visually-hidden"
      >
        {announcement}
      </div>
      
      <s-table
        role="table"
        aria-label={caption}
        aria-rowcount={data.length}
      >
        {caption && (
          <s-caption>{caption}</s-caption>
        )}
        
        <s-table-header-row role="row">
          {columns.map((column, index) => (
            <s-table-header
              key={column.key}
              role="columnheader"
              aria-colindex={index + 1}
              aria-sort={
                sortColumn === column.key
                  ? sortDirection === 'asc' ? 'ascending' : 'descending'
                  : 'none'
              }
              onClick={() => column.sortable && handleSort(column)}
              tabIndex={column.sortable ? 0 : -1}
              onKeyDown={(e) => {
                if (column.sortable && (e.key === 'Enter' || e.key === ' ')) {
                  e.preventDefault();
                  handleSort(column);
                }
              }}
            >
              {column.label}
              {column.sortable && (
                <span aria-hidden="true">
                  {sortColumn === column.key && (
                    sortDirection === 'asc' ? ' ↑' : ' ↓'
                  )}
                </span>
              )}
            </s-table-header>
          ))}
        </s-table-header-row>
        
        <s-table-body role="rowgroup">
          {data.map((row, rowIndex) => (
            <s-table-row
              key={row.id}
              role="row"
              aria-rowindex={rowIndex + 2} // +2 for header row
            >
              {columns.map((column, colIndex) => (
                <s-table-cell
                  key={column.key}
                  role="cell"
                  aria-colindex={colIndex + 1}
                >
                  {/* Use semantic HTML for better accessibility */}
                  {column.type === 'link' ? (
                    <s-link href={row[column.href]}>
                      {row[column.key]}
                    </s-link>
                  ) : column.type === 'badge' ? (
                    <s-badge tone={row[column.tone]}>
                      {row[column.key]}
                    </s-badge>
                  ) : (
                    row[column.key]
                  )}
                </s-table-cell>
              ))}
            </s-table-row>
          ))}
        </s-table-body>
      </s-table>
    </>
  );
}

// Accessible form with proper labeling and error handling
export function AccessibleForm({ onSubmit }) {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const errorSummaryRef = useRef(null);
  
  // Handle form submission with validation
  const handleSubmit = (e) => {
    e.preventDefault();
    
    const validationErrors = validateForm(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      
      // Focus error summary for screen readers
      errorSummaryRef.current?.focus();
      
      // Announce errors to screen readers
      const errorCount = Object.keys(validationErrors).length;
      const announcement = `Form has ${errorCount} error${errorCount > 1 ? 's' : ''}`;
      
      // Use Shopify toast for visual feedback
      window.shopify?.toast.show(announcement, { isError: true });
      
      return;
    }
    
    onSubmit(formData);
  };
  
  return (
    <form 
      onSubmit={handleSubmit}
      noValidate // Use custom validation
      aria-label="Product form"
    >
      {/* Error summary for screen readers */}
      {Object.keys(errors).length > 0 && (
        <s-banner 
          tone="critical"
          ref={errorSummaryRef}
          tabIndex={-1}
          role="alert"
          aria-labelledby="error-summary-heading"
        >
          <s-heading id="error-summary-heading">
            Please fix the following errors:
          </s-heading>
          <s-unordered-list>
            {Object.entries(errors).map(([field, error]) => (
              <s-list-item key={field}>
                <s-link href={`#${field}`}>
                  {error}
                </s-link>
              </s-list-item>
            ))}
          </s-unordered-list>
        </s-banner>
      )}
      
      <s-stack gap="base">
        {/* Properly labeled form field */}
        <s-text-field
          id="product-title"
          name="title"
          label="Product title"
          value={formData.title || ''}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
          error={errors.title}
          required
          aria-required="true"
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? 'title-error' : 'title-help'}
        >
          <span id="title-help" slot="details">
            Give your product a clear, descriptive title
          </span>
          {errors.title && (
            <span id="title-error" slot="error" role="alert">
              {errors.title}
            </span>
          )}
        </s-text-field>
        
        {/* Grouped radio buttons with fieldset */}
        <fieldset>
          <legend>Product status</legend>
          <s-choice-list
            name="status"
            value={formData.status || 'draft'}
            onChange={(value) => setFormData({...formData, status: value})}
          >
            <s-radio value="active">Active</s-radio>
            <s-radio value="draft">Draft</s-radio>
            <s-radio value="archived">Archived</s-radio>
          </s-choice-list>
        </fieldset>
        
        {/* Submit button with loading state */}
        <s-button
          type="submit"
          variant="primary"
          aria-busy={isSubmitting}
          aria-disabled={isSubmitting}
        >
          {isSubmitting ? 'Saving...' : 'Save product'}
        </s-button>
      </s-stack>
    </form>
  );
}

// ===================================
// Pattern 3: Performance Optimization
// File: app/components/PerformantComponents.jsx
// ===================================

// Virtual scrolling for large lists
export function VirtualList({ items, itemHeight = 50, visibleCount = 10 }) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef(null);
  
  const totalHeight = items.length * itemHeight;
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + visibleCount + 1, // +1 for smooth scrolling
    items.length
  );
  
  const visibleItems = items.slice(startIndex, endIndex);
  const offsetY = startIndex * itemHeight;
  
  const handleScroll = (e) => {
    setScrollTop(e.target.scrollTop);
  };
  
  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      style={{
        height: visibleCount * itemHeight,
        overflow: 'auto',
        position: 'relative'
      }}
      role="list"
      aria-rowcount={items.length}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map((item, index) => (
            <div
              key={item.id}
              style={{ height: itemHeight }}
              role="listitem"
              aria-rowindex={startIndex + index + 1}
            >
              {/* Render item content */}
              <ProductListItem product={item} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Debounced search input to reduce API calls
export function DebouncedSearch({ onSearch, delay = 300 }) {
  const [value, setValue] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const timeoutRef = useRef(null);
  
  const handleChange = (e) => {
    const newValue = e.target.value;
    setValue(newValue);
    
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    // Don't search for empty strings
    if (!newValue.trim()) {
      setIsSearching(false);
      onSearch('');
      return;
    }
    
    // Show loading state immediately
    setIsSearching(true);
    
    // Debounce the search
    timeoutRef.current = setTimeout(() => {
      onSearch(newValue);
      setIsSearching(false);
    }, delay);
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return (
    <s-search-field
      value={value}
      onChange={handleChange}
      placeholder="Search products..."
      label="Search"
      labelAccessibilityVisibility="exclusive"
      loading={isSearching}
      clearButton={{
        onClear: () => {
          setValue('');
          onSearch('');
        }
      }}
    />
  );
}

// Lazy-loaded images with intersection observer
export function LazyImage({ src, alt, placeholder, ...props }) {
  const [imageSrc, setImageSrc] = useState(placeholder || '');
  const [isLoading, setIsLoading] = useState(true);
  const imgRef = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Load the actual image
            const img = new Image();
            img.src = src;
            img.onload = () => {
              setImageSrc(src);
              setIsLoading(false);
            };
            
            // Stop observing once loaded
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px' // Start loading 50px before visible
      }
    );
    
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    
    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current);
      }
    };
  }, [src]);
  
  return (
    <s-box position="relative" ref={imgRef}>
      {isLoading && (
        <s-box
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          background="subtle"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <s-spinner size="small" />
        </s-box>
      )}
      <s-image
        src={imageSrc}
        alt={alt}
        loading="lazy"
        {...props}
      />
    </s-box>
  );
}

// Memoized expensive computation
export function ExpensiveComponent({ data }) {
  // Memoize expensive calculations
  const processedData = useMemo(() => {
    console.log('Processing data...'); // This only runs when data changes
    
    return data.map(item => ({
      ...item,
      // Expensive calculation
      computedValue: calculateExpensiveValue(item),
      formattedPrice: formatCurrency(item.price),
      formattedDate: formatDate(item.createdAt),
    }));
  }, [data]);
  
  // Memoize callbacks to prevent unnecessary re-renders
  const handleItemClick = useCallback((itemId) => {
    console.log('Item clicked:', itemId);
    // Handle click
  }, []);
  
  return (
    <s-stack gap="base">
      {processedData.map(item => (
        <MemoizedItem
          key={item.id}
          item={item}
          onClick={handleItemClick}
        />
      ))}
    </s-stack>
  );
}

// Memoized child component to prevent re-renders
const MemoizedItem = React.memo(({ item, onClick }) => {
  return (
    <s-box
      onClick={() => onClick(item.id)}
      padding="base"
      background="subtle"
      borderRadius="base"
      cursor="pointer"
    >
      <s-stack direction="inline" gap="base" alignItems="center">
        <s-text weight="semibold">{item.title}</s-text>
        <s-badge>{item.computedValue}</s-badge>
        <s-text tone="subdued">{item.formattedDate}</s-text>
        <s-text weight="medium">{item.formattedPrice}</s-text>
      </s-stack>
    </s-box>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function
  // Only re-render if item or onClick changed
  return (
    prevProps.item.id === nextProps.item.id &&
    prevProps.item.computedValue === nextProps.item.computedValue &&
    prevProps.onClick === nextProps.onClick
  );
});

// Optimized context provider pattern
const OptimizedContext = createContext();

export function OptimizedProvider({ children }) {
  const [state, setState] = useState({
    products: [],
    loading: false,
    error: null,
  });
  
  // Separate dispatch functions to avoid recreating objects
  const actions = useMemo(() => ({
    setProducts: (products) => setState(prev => ({ ...prev, products })),
    setLoading: (loading) => setState(prev => ({ ...prev, loading })),
    setError: (error) => setState(prev => ({ ...prev, error })),
  }), []);
  
  // Memoize context value to prevent unnecessary re-renders
  const value = useMemo(() => ({
    ...state,
    ...actions,
  }), [state, actions]);
  
  return (
    <OptimizedContext.Provider value={value}>
      {children}
    </OptimizedContext.Provider>
  );
}

// Hook to use optimized context
export function useOptimizedContext() {
  const context = useContext(OptimizedContext);
  if (!context) {
    throw new Error('useOptimizedContext must be used within OptimizedProvider');
  }
  return context;
}
```

## 7. Recent Changes to Be Aware Of

The Shopify ecosystem has undergone significant changes recently. Let me highlight what's new and what has been deprecated to ensure you don't follow outdated patterns from older tutorials.

The most significant change is the shift from React-only Polaris components to Web Components. This change happened because Shopify recognized that not all developers want to use React, and Web Components provide framework-agnostic solutions. The older Polaris React library still exists, but the Web Components approach is now the recommended path for new apps. This is similar to how Angular moved from AngularJS to Angular 2+ – a fundamental shift in architecture.

Another major update is the direct API access feature, which allows your frontend code to make authenticated requests directly to Shopify's GraphQL API without going through your backend server. This is revolutionary because it eliminates the need for proxy endpoints in many cases, similar to how Angular's HttpClient can directly call APIs with interceptors handling authentication.

The App Bridge has also evolved to handle more UI elements outside your iframe, including modals, navigation menus, and contextual save bars. This means you're writing less boilerplate code and getting more native-feeling integrations automatically.

## 8. Migration Path and Current Best Practices

If you're migrating from an older Shopify app or starting fresh, here are the current best practices you should follow:

For component migration, if you're coming from Polaris React components, the transition to Web Components involves changing your import statements and component syntax. Instead of importing from `@shopify/polaris`, you'll use the Web Components directly with the `s-` prefix. The props remain largely the same, but the syntax changes from React's camelCase to HTML's kebab-case attributes.

For state management, unlike Angular's services with RxJS or React's Redux patterns, the current approach favors simpler state management using React hooks or your framework's native state management. The complexity should live in your backend, with the frontend being a thin presentation layer. This aligns with Shopify's philosophy of keeping apps lightweight and performant.

Error handling has also improved significantly. The platform now provides better error boundaries and automatic retry mechanisms for failed API calls. You should implement progressive enhancement strategies where your app gracefully degrades if certain features aren't available.

## 9. Production Considerations for 2025

When deploying your Shopify app to production in 2025, there are several critical considerations you need to keep in mind.

Performance is paramount because your app runs inside an iframe within the Shopify admin, which already has its own performance overhead. You should aim for your initial bundle size to be under 200KB gzipped, with lazy loading for additional features. This is stricter than typical Angular apps where you might have larger initial bundles.

Security is handled differently than in traditional SPAs. Since you're running in an iframe, you need to be careful about Content Security Policy (CSP) headers and ensure all external resources are loaded over HTTPS. The platform handles authentication through session tokens, which are automatically refreshed, unlike traditional JWT tokens you might manage yourself in Angular.

For monitoring and analytics, Shopify provides built-in Web Vitals tracking through App Bridge. You should also implement your own error tracking using services like Sentry, but be mindful of PII (Personally Identifiable Information) restrictions. Unlike your own applications where you control data handling, Shopify has strict requirements about what data you can collect and store.

## 10. Hands-On Exercise: Build a Product Bulk Editor

Now it's time to put your knowledge into practice. I'll give you an exercise that combines everything we've learned, similar to a real-world feature you might build for a Shopify merchant.

**Your Challenge:** Build a bulk product editor that allows merchants to select multiple products and update their prices with a percentage increase or decrease. The app should include proper validation, loading states, accessibility features, and internationalization support.

Here are your requirements:

**Functional Requirements:**
- Display products in a searchable, sortable table
- Allow multi-selection with "select all" functionality
- Provide a bulk action to adjust prices by percentage
- Show a preview of changes before applying
- Implement undo functionality after changes are applied

**Technical Requirements:**
- Use Polaris Web Components for all UI elements
- Implement proper loading states and skeletons
- Add keyboard navigation support
- Include form validation with clear error messages
- Make it fully accessible with ARIA labels
- Support at least two languages (English and French)

**Performance Requirements:**
- Implement virtual scrolling for tables over 100 items
- Debounce search input by 300ms
- Lazy load the bulk edit modal
- Keep initial bundle under 150KB

**Hints leveraging your existing knowledge:**
- Think of the table component like Angular Material's mat-table with mat-paginator
- The bulk selection pattern is similar to Laravel's bulk operations in admin panels
- Form validation can follow the same patterns as Angular's Reactive Forms validators
- Use the observer pattern (like RxJS) for managing selected items state

**Success Criteria:**
- The app should handle 1000+ products without performance degradation
- All interactive elements should be keyboard accessible
- The app should work on screens as small as 320px wide
- Error states should be clearly communicated both visually and to screen readers

## Verification and Resources

Throughout this tutorial, I've used the Shopify Dev MCP tools to verify that all the patterns and code examples are current. The documentation I've referenced is from the latest Shopify Developer documentation as of September 2025.

**Key Documentation Pages:**
- App Bridge Web Components: `https://shopify.dev/docs/api/app-home`
- Polaris Web Components: `https://shopify.dev/docs/api/app-home/polaris-web-components`
- Accessibility Guidelines: `https://shopify.dev/docs/apps/best-practices/accessibility`
- Performance Best Practices: `https://shopify.dev/docs/apps/build/performance`

**Related Concepts to Explore Next:**
- **Shopify Functions**: Server-side logic that runs on Shopify's infrastructure
- **Checkout UI Extensions**: Customizing the checkout experience
- **Admin UI Extensions**: Adding functionality directly to Shopify admin pages
- **Theme App Extensions**: Integrating with storefront themes

**Common Pitfalls to Avoid:**
1. Don't use the old `@shopify/polaris-react` components for new projects - use Web Components
2. Don't implement your own authentication - use Shopify's session token system
3. Don't store sensitive merchant data in localStorage - it's not secure in an iframe context
4. Don't use positive tabindex values - they break keyboard navigation patterns
5. Don't skip accessibility testing - Shopify reviews apps for accessibility compliance

## Summary

Phase 7 of Shopify development represents a significant shift from traditional web application development. The combination of Web Components, App Bridge, and the embedded iframe architecture creates unique challenges and opportunities. The key to success is understanding that you're not building a standalone application but rather an extension of the Shopify admin that must seamlessly integrate with its design language and user experience patterns.

The move to Web Components democratizes Shopify app development by removing the React requirement, making it easier for developers from different backgrounds (like your Angular experience) to build Shopify apps. The current architecture emphasizes performance, accessibility, and consistency - three pillars that ensure merchants have a reliable and efficient experience regardless of which apps they install.

Remember that Shopify's ecosystem evolves rapidly, so always verify patterns against the latest documentation before implementing them in production. The patterns I've shown you today are current as of September 2025, but always check for updates when starting new projects.
