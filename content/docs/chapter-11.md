# App Extensions and Advanced Features

Based on my verification with the Shopify Dev MCP tools, I'll teach you about Theme App Extensions and Shopify Functions using the most current documentation and APIs as of September 2025.

## 1. Current Shopify Documentation Check

I've verified the latest documentation using the Shopify Dev MCP tools. Here's what's current:

**API Version**: 2025-07 (latest stable)
**Key Updates**:
- Theme App Extensions now use Online Store 2.0 architecture
- Shopify Functions support both JavaScript and Rust (Rust strongly recommended for performance)
- New Discount API unifies product, order, and shipping discounts
- Functions can have multiple targets (e.g., both `run` and `fetch`)

**Deprecated Patterns to Avoid**:
- Legacy ScriptTag API (replaced by app embeds)
- Asset API for theme modifications (now restricted)
- Old discount function APIs (Product Discount, Order Discount, Shipping Discount) replaced by unified Discount API

## 2. Conceptual Overview with Framework Comparisons

### Theme App Extensions

Think of Theme App Extensions as **Laravel Blade Components** or **Angular Components** that can be dynamically inserted into Shopify themes. They're self-contained modules with their own:
- Liquid templates (like Blade/Angular templates)
- Assets (CSS/JS bundles)
- Configuration schema (similar to component props/inputs)

**Key Difference from Your Frameworks**: Unlike Laravel where you control the entire view layer, or Angular where you own the SPA, Theme App Extensions must coexist within merchant-controlled themes. You're essentially creating plugins that merchants can position and configure themselves.

### Shopify Functions

Shopify Functions are **serverless middleware** that intercept and modify Shopify's backend logic. If you're familiar with Laravel middleware or Spring Boot interceptors, Functions work similarly but in a more restricted, sandboxed environment.

**The Laravel/Spring Boot Equivalent**: 
```php
// Laravel Middleware
public function handle($request, Closure $next) {
    // Modify request
    $modifiedRequest = $this->applyDiscount($request);
    return $next($modifiedRequest);
}
```

In Shopify Functions, you receive input, apply logic, and return operations for Shopify to execute.

**Key Architectural Difference**: Functions are:
- **Pure** (no side effects, network calls, or database access)
- **Deterministic** (same input always produces same output)
- **Compiled to WebAssembly** (for performance and security)

## 3. Architecture Deep Dive

### Theme App Extensions Architecture

```
Your App Server
    ↓
Theme App Extension Bundle
    ├── /blocks           (App blocks - inline content)
    │   └── product-reviews.liquid
    ├── /assets          (Static files served from CDN)
    │   ├── app.css
    │   └── app.js
    ├── /snippets        (Reusable Liquid partials)
    └── shopify.extension.toml (Configuration)
    
Merchant's Theme
    ├── Sections with {% content_for 'blocks' %}
    └── Theme Editor → Merchant adds your blocks
```

**Data Flow**:
1. Merchant installs your app
2. Theme app extension registers with the theme
3. Merchant uses theme editor to add blocks
4. Shopify renders blocks within theme context
5. Your JS/CSS loads asynchronously from CDN

### Shopify Functions Architecture

```
Trigger Event (e.g., Add to Cart)
    ↓
Shopify Backend
    ↓
Your Function (WASM Module)
    ├── Input Query (GraphQL) → JSON Input
    ├── Function Logic (Rust/JS)
    └── Output → JSON Operations
    ↓
Shopify Executes Operations
```

**Similar to Spring Boot's Filter Chain**, but instead of modifying HTTP requests, you're modifying commerce operations.

## 4. Practical Implementation with Validated Code

### Theme App Extension Example

Let's create a product rating app block that integrates with themes.

**File Structure**:
```
extensions/
└── product-rating/
    ├── blocks/
    │   └── star-rating.liquid
    ├── assets/
    │   ├── rating.css
    │   └── rating.js
    ├── locales/
    │   └── en.default.json
    └── shopify.extension.toml
```

**blocks/star-rating.liquid**:
```liquid
{%- comment -%}
  This block integrates with any product section
  Similar to Angular's @Input() decorators
{%- endcomment -%}

{%- assign product_id = block.settings.product | default: product.id -%}
{%- assign rating = product.metafields.reviews.rating | default: 0 -%}
{%- assign count = product.metafields.reviews.count | default: 0 -%}

<div class="app-rating" 
     data-product-id="{{ product_id }}"
     {{ block.shopify_attributes }}>
  
  <div class="app-rating__stars" 
       style="--rating: {{ rating }}; 
              --star-size: {{ block.settings.star_size }}px;
              --star-color: {{ block.settings.star_color }};">
    {%- for i in (1..5) -%}
      <span class="app-rating__star" 
            data-rating="{{ i }}"
            aria-label="{{ 'ratings.star' | t: number: i }}">
        ★
      </span>
    {%- endfor -%}
  </div>
  
  {%- if block.settings.show_count -%}
    <span class="app-rating__count">
      ({{ count }} {{ 'ratings.reviews' | t }})
    </span>
  {%- endif -%}
</div>

{% stylesheet %}
  .app-rating {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .app-rating__stars {
    display: inline-flex;
    font-size: var(--star-size);
    color: #ddd;
    position: relative;
  }
  
  .app-rating__stars::before {
    content: '★★★★★';
    position: absolute;
    color: var(--star-color);
    width: calc(var(--rating) * 20%);
    overflow: hidden;
  }
{% endstylesheet %}

{% javascript %}
  // Lazy-loaded when block is present
  // Similar to Angular's lifecycle hooks
  document.addEventListener('DOMContentLoaded', () => {
    const ratings = document.querySelectorAll('.app-rating');
    
    ratings.forEach(rating => {
      // Could make API calls to your app server here
      rating.addEventListener('click', handleRatingClick);
    });
  });
{% endjavascript %}

{% schema %}
{
  "name": "Product Rating",
  "target": "section",
  "enabled_on": {
    "templates": ["product", "collection"]
  },
  "settings": [
    {
      "type": "product",
      "id": "product",
      "label": "Product",
      "info": "Leave empty to use current product"
    },
    {
      "type": "range",
      "id": "star_size",
      "label": "Star Size",
      "min": 12,
      "max": 32,
      "step": 2,
      "unit": "px",
      "default": 20
    },
    {
      "type": "color",
      "id": "star_color",
      "label": "Star Color",
      "default": "#FFD700"
    },
    {
      "type": "checkbox",
      "id": "show_count",
      "label": "Show Review Count",
      "default": true
    }
  ]
}
{% endschema %}
```

**shopify.extension.toml**:
```toml
api_version = "2025-07"
name = "Product Rating Extension"
type = "theme"

[[metafields]]
namespace = "reviews"
key = "rating"
type = "number_decimal"
owner_type = "PRODUCT"

[[metafields]]
namespace = "reviews"
key = "count"
type = "number_integer"
owner_type = "PRODUCT"
```

### Shopify Functions Example - Volume Discount

Now let's create a discount function using the latest Discount API. This provides volume discounts based on quantity.

**Shopify CLI Command**:
```bash
shopify app generate extension --template discount --flavor rust --name volume-discount
```

**src/main.rs**:
```rust
use std::process;
use shopify_function::prelude::*;

// Module for the discount logic
pub mod cart_lines_discounts_generate_run;

// GraphQL schema definition
#[typegen("./schema.graphql")]
pub mod schema {
    // Link the GraphQL query to the module
    #[query(
        "src/cart_lines_discounts_generate_run.graphql",
        custom_scalar_overrides = {
            "Input.discount.metafield.jsonValue" => super::cart_lines_discounts_generate_run::Configuration
        }
    )]
    pub mod cart_lines_discounts_generate_run {}
}

fn main() {
    eprintln!("Please invoke a named export.");
    process::exit(1);
}
```

**src/cart_lines_discounts_generate_run.rs**:
```rust
use crate::schema;
use shopify_function::prelude::*;
use shopify_function::Result;

// Configuration from metafield (like Laravel's config)
#[derive(Deserialize, Default, PartialEq)]
#[shopify_function(rename_all = "camelCase")]
pub struct Configuration {
    tiers: Vec<DiscountTier>,
    apply_to_collections: Vec<String>,
}

#[derive(Deserialize, Default, PartialEq)]
struct DiscountTier {
    min_quantity: i32,
    discount_percentage: f64,
}

// Main function logic - similar to a Laravel controller action
#[shopify_function]
fn cart_lines_discounts_generate_run(
    input: schema::cart_lines_discounts_generate_run::Input,
) -> Result<schema::CartLinesDiscountsGenerateRunResult> {
    // Get configuration from metafield
    let config = match input.discount().metafield() {
        Some(metafield) => metafield.json_value(),
        None => return Ok(schema::CartLinesDiscountsGenerateRunResult { 
            operations: vec![] 
        }),
    };
    
    // Check if we can apply product discounts
    let has_product_discount = input
        .discount()
        .discount_classes()
        .contains(&schema::DiscountClass::Product);
    
    if !has_product_discount {
        return Ok(schema::CartLinesDiscountsGenerateRunResult { 
            operations: vec![] 
        });
    }
    
    let mut product_discounts = vec![];
    
    // Process each cart line (like iterating request items in Laravel)
    for line in input.cart().lines() {
        // Pattern matching - similar to Java switch expressions
        let variant = match &line.merchandise() {
            schema::cart_lines_discounts_generate_run::input::cart::lines::Merchandise::ProductVariant(v) => v,
            _ => continue,
        };
        
        // Check if product is in eligible collections
        let in_collection = config.apply_to_collections.is_empty() 
            || *variant.product().in_any_collection();
        
        if !in_collection {
            continue;
        }
        
        let quantity = line.quantity();
        
        // Find applicable tier (like finding a matching route in Laravel)
        let applicable_tier = config.tiers
            .iter()
            .filter(|tier| quantity >= tier.min_quantity)
            .max_by_key(|tier| tier.min_quantity);
        
        if let Some(tier) = applicable_tier {
            product_discounts.push(schema::ProductDiscountCandidate {
                targets: vec![
                    schema::ProductDiscountCandidateTarget::CartLine(
                        schema::CartLineTarget {
                            id: line.id().to_string(),
                            quantity: None,
                        }
                    )
                ],
                value: schema::ProductDiscountCandidateValue::Percentage(
                    schema::Percentage {
                        value: Decimal::from(tier.discount_percentage),
                    }
                ),
                message: Some(format!(
                    "{}% off for {} or more",
                    tier.discount_percentage,
                    tier.min_quantity
                )),
                associated_discount_code: None,
            });
        }
    }
    
    // Return operations for Shopify to execute
    if product_discounts.is_empty() {
        Ok(schema::CartLinesDiscountsGenerateRunResult { 
            operations: vec![] 
        })
    } else {
        Ok(schema::CartLinesDiscountsGenerateRunResult {
            operations: vec![
                schema::CartOperation::ProductDiscountsAdd(
                    schema::ProductDiscountsAddOperation {
                        selection_strategy: schema::ProductDiscountSelectionStrategy::First,
                        candidates: product_discounts,
                    }
                )
            ],
        })
    }
}

// Unit tests - similar to PHPUnit or JUnit
#[cfg(test)]
mod tests {
    use super::*;
    use shopify_function::run_function_with_input;
    
    #[test]
    fn test_volume_discount_applied() -> Result<()> {
        let result = run_function_with_input(
            cart_lines_discounts_generate_run,
            r#"
            {
                "cart": {
                    "lines": [{
                        "id": "gid://shopify/CartLine/1",
                        "quantity": 10,
                        "merchandise": {
                            "__typename": "ProductVariant",
                            "product": {
                                "inAnyCollection": true
                            }
                        }
                    }]
                },
                "discount": {
                    "discountClasses": ["PRODUCT"],
                    "metafield": {
                        "jsonValue": {
                            "tiers": [
                                {"minQuantity": 5, "discountPercentage": 10},
                                {"minQuantity": 10, "discountPercentage": 15}
                            ],
                            "applyToCollections": []
                        }
                    }
                }
            }
            "#,
        )?;
        
        assert_eq!(result.operations.len(), 1);
        Ok(())
    }
}
```

**src/cart_lines_discounts_generate_run.graphql**:
```graphql
query Input($collectionIds: [ID!]) {
  cart {
    lines {
      id
      quantity
      merchandise {
        __typename
        ... on ProductVariant {
          product {
            inAnyCollection(ids: $collectionIds)
          }
        }
      }
    }
  }
  discount {
    discountClasses
    metafield(namespace: "$app:volume-discount", key: "config") {
      jsonValue
    }
  }
}
```

## 5. Real-World Scenarios Based on Current Capabilities

### Scenario 1: Product Reviews with Dynamic Loading

**Use Case**: Display reviews that load dynamically without impacting initial page load.

**Implementation Approach**:
1. Create app blocks for review display and submission
2. Use intersection observer to lazy-load reviews
3. Leverage Shopify CDN for asset delivery
4. Store review data in metafields

**Key Pattern**: Unlike Angular's built-in lazy loading, you implement this manually:
```javascript
// In your app block's JavaScript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadReviews(entry.target.dataset.productId);
    }
  });
});
```

### Scenario 2: Tiered Shipping Discounts

**Use Case**: Offer free shipping at different thresholds per currency.

**Implementation**:
```rust
// Check cart subtotal against currency-specific thresholds
let threshold = match input.cart().cost().subtotal_amount().currency_code() {
    "USD" => 100.0,
    "EUR" => 85.0,
    "GBP" => 75.0,
    _ => 100.0,
};

if subtotal >= threshold {
    // Apply free shipping
}
```

### Scenario 3: Bundle Builder with Cart Transform

**Use Case**: Allow customers to build custom bundles with dynamic pricing.

**Implementation Strategy**:
1. Use Cart Transform function to merge bundle items
2. Apply bundle discount based on selection
3. Update cart display with bundle information

## 6. Advanced Patterns from Latest Documentation

### Pattern 1: Multi-Target Functions

Functions can now have multiple entry points. This is like having multiple controller actions in Laravel:

```rust
// src/main.rs
pub mod schema {
    #[query("src/run.graphql")]
    pub mod run {}
    
    #[query("src/fetch.graphql")]
    pub mod fetch {}
}
```

Use `fetch` for network operations (when enabled) and `run` for pure logic.

### Pattern 2: Conditional App Blocks

Control block visibility based on app data:

```liquid
{% schema %}
{
  "name": "Premium Feature",
  "available_if": "{{ app.metafields.subscription.isPremium }}",
  "settings": [...]
}
{% endschema %}
```

### Pattern 3: Function Composition

Chain multiple discount operations:
```rust
Ok(schema::CartLinesDiscountsGenerateRunResult {
    operations: vec![
        // First apply product discounts
        schema::CartOperation::ProductDiscountsAdd(...),
        // Then apply order discount
        schema::CartOperation::OrderDiscountsAdd(...),
    ],
})
```

## 7. Hands-On Exercise

**Challenge**: Build a "Frequently Bought Together" recommendation system.

**Requirements**:
1. Create a Theme App Extension that displays related products
2. Build a Discount Function that applies a bundle discount when all items are in cart
3. Use metafields to store product relationships

**Acceptance Criteria**:
- Block should respect theme's typography and colors (use CSS variables)
- Discount should only apply when all bundle items present
- Support multiple bundles per product
- Mobile-responsive design

**Hints from Your Background**:
- Think of the block like an Angular component with @Input() bindings
- The function logic is similar to Laravel's validation rules
- Use pattern matching (like Java switch expressions) for cart analysis

**Starter Structure**:
```
extensions/
├── frequently-bought/
│   ├── blocks/
│   │   └── recommendations.liquid
│   └── shopify.extension.toml
└── bundle-discount/
    ├── src/
    │   ├── main.rs
    │   └── cart_lines_discounts_generate_run.rs
    └── shopify.extension.toml
```

## 8. Migration Path and Current Best Practices

### Migrating from Legacy Patterns

**From ScriptTag to App Embeds**:
```javascript
// OLD: ScriptTag approach (deprecated)
POST /admin/api/2024-01/script_tags.json
{
  "script_tag": {
    "event": "onload",
    "src": "https://yourapp.com/script.js"
  }
}

// NEW: App Embed Block
// blocks/app-embed.liquid
{% schema %}
{
  "name": "App Analytics",
  "target": "body",
  "settings": [...]
}
{% endschema %}
```

**Common Mistakes to Avoid**:
1. Don't hardcode theme selectors - themes vary widely
2. Never modify theme files directly via Asset API
3. Don't assume jQuery is available (many themes removed it)
4. Avoid synchronous asset loading - use async/defer
5. Don't store sensitive data in frontend code

**Performance Best Practices**:
- Use Shopify's CDN for all assets
- Implement code splitting for large JavaScript files
- Leverage browser caching with proper headers
- Minimize Liquid processing in blocks
- Use CSS containment for complex layouts

### Troubleshooting Guide

**Issue: Function times out with large carts**
- Solution: Use Rust instead of JavaScript
- Optimize queries to fetch only needed data
- Implement early returns for non-applicable cases

**Issue: App blocks don't appear in theme editor**
- Check theme supports Online Store 2.0
- Verify `enabled_on` settings in schema
- Ensure proper JSON syntax in schema

**Issue: Discount not applying**
- Verify discount classes are enabled
- Check metafield namespace and key match
- Test with simplified input/output

## 9. Verification and Resources

### MCP Tools Used for Verification

I've verified all information using:
- `shopify-dev-mcp:learn_shopify_api` - Loaded latest API contexts
- `shopify-dev-mcp:search_docs_chunks` - Found current documentation
- `shopify-dev-mcp:fetch_full_docs` - Retrieved complete implementation details

**Documentation Last Updated**: September 2025
**API Version Used**: 2025-07

### Related Learning Topics

**Next in your journey**:
1. **Shopify Flow Integration** - Automate merchant workflows
2. **Web Pixels API** - Advanced analytics tracking
3. **Checkout UI Extensions** - Customize checkout experience
4. **B2B Features** - Company accounts and wholesale

### Beta Features and Upcoming Changes

**Currently in Beta**:
- Network access in Functions (fetch target)
- New validation function capabilities
- Enhanced metaobject support

**Deprecation Timeline**:
- ScriptTag API: Fully deprecated for new apps
- Asset API write access: Restricted without exemption
- Legacy discount APIs: Use unified Discount API instead

## Important Architecture Notes

Coming from Laravel/Spring Boot, remember these key differences:

1. **No Direct Database Access**: Functions can't query databases. All data comes through the input query.

2. **Immutable Operations**: You return operations for Shopify to execute, not directly modify data.

3. **Theme Sandbox**: Your extensions run within merchant themes, not standalone applications.

4. **Pure Functions**: No side effects, network calls, or state management in Functions.

5. **Performance Critical**: Functions have strict time limits (5ms for some operations).

This architecture ensures security, performance, and merchant control while allowing powerful customizations. Think of it as building plugins for a platform rather than standalone applications.
