# Debugging Techniques in Shopify App Development

## **1. Current Shopify Documentation Check**

According to Shopify's documentation as of September 2025, the debugging landscape for Shopify apps has evolved significantly with enhanced tooling support. The current recommended debugging approach emphasizes using Shopify CLI's built-in debugging capabilities, structured logging practices, and integration with third-party monitoring services. The latest API version (2025-07) includes improved debugging features, particularly for Functions and embedded apps.

## **2. The Laravel/Spring Boot Equivalent**

Coming from Laravel and Spring Boot, you're already familiar with comprehensive debugging ecosystems. In Laravel, you've used tools like Laravel Telescope for request monitoring, the debug bar for real-time inspection, and Laravel's logging channels for structured logging. Spring Boot provides you with actuator endpoints for health monitoring, integrated debugging with IntelliJ IDEA, and sophisticated logging with SLF4J and Logback.

Shopify's debugging approach shares similar principles but adapts them to its distributed architecture. Just as Laravel uses middleware to intercept and log requests, Shopify CLI streams function execution logs in real-time. Similar to Spring Boot's actuator providing health metrics, Shopify offers webhook delivery metrics and function execution monitoring through the Partner Dashboard.

## **3. The Current Shopify Way**

Shopify's debugging ecosystem centers around three key components: the Shopify CLI for local development debugging, the Partner Dashboard for production monitoring, and integration points for third-party monitoring services. The architecture reflects Shopify's event-driven nature, where debugging often involves tracing webhook deliveries, function executions, and API interactions across multiple services.

The debugging flow follows a layered approach. At the development layer, Shopify CLI provides real-time streaming of logs, function execution details, and network request inspection. The platform layer offers webhook metrics, function run logs, and API response tracking through the Partner Dashboard. The application layer enables integration with external monitoring services like Sentry for comprehensive error tracking.

## **4. Complete Working Example: Comprehensive Debugging Setup**

Let me show you how to implement a complete debugging infrastructure for a Shopify app with all the modern debugging techniques:
```ts
// ========================================
// File: app/lib/debugging/logger.ts
// Purpose: Centralized structured logging system
// API Version: 2025-07
// Last verified: September 2025
// ========================================

import winston from 'winston';
import * as Sentry from '@sentry/node';
import { ProfilingIntegration } from '@sentry/profiling-node';

// Initialize Sentry for production error tracking
// This is similar to Laravel's Bugsnag or Spring Boot's error reporting
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  integrations: [
    new ProfilingIntegration(),
  ],
  // Performance Monitoring
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  // Capture replay sessions for debugging
  profilesSampleRate: 1.0,
});

// Define log levels similar to Laravel's channels
const logLevels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
};

// Create structured logging format
// This provides similar functionality to Spring Boot's logback patterns
const logFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json(),
  winston.format.printf(({ timestamp, level, message, ...metadata }) => {
    let msg = `${timestamp} [${level}] : ${message} `;
    
    // Include metadata for context (similar to Laravel's context array)
    if (Object.keys(metadata).length > 0) {
      msg += JSON.stringify(metadata);
    }
    
    return msg;
  })
);

// Configure transports based on environment
const transports: winston.transport[] = [
  // Console output for development (similar to Laravel's 'daily' channel)
  new winston.transports.Console({
    format: winston.format.combine(
      winston.format.colorize(),
      winston.format.simple()
    ),
    silent: process.env.NODE_ENV === 'test',
  }),
];

// Add file transport for production
if (process.env.NODE_ENV === 'production') {
  transports.push(
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    }),
    new winston.transports.File({
      filename: 'logs/combined.log',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
    })
  );
}

// Create the logger instance
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  levels: logLevels,
  format: logFormat,
  transports,
  exitOnError: false,
});

// ========================================
// File: app/lib/debugging/request-debugger.ts
// Purpose: Network request debugging and monitoring
// ========================================

import { logger } from './logger';
import { performance } from 'perf_hooks';

interface RequestDebugInfo {
  method: string;
  url: string;
  headers: Record<string, string>;
  body?: any;
  startTime: number;
}

interface ResponseDebugInfo {
  status: number;
  headers: Record<string, string>;
  body?: any;
  duration: number;
}

export class NetworkDebugger {
  private activeRequests = new Map<string, RequestDebugInfo>();
  
  // Log outgoing API requests (similar to Laravel's HTTP client debugging)
  logRequest(requestId: string, method: string, url: string, options?: RequestInit) {
    const debugInfo: RequestDebugInfo = {
      method,
      url,
      headers: options?.headers as Record<string, string> || {},
      body: options?.body,
      startTime: performance.now(),
    };
    
    this.activeRequests.set(requestId, debugInfo);
    
    logger.http('Outgoing API Request', {
      requestId,
      method,
      url,
      headers: this.sanitizeHeaders(debugInfo.headers),
      // In development, log the full body
      body: process.env.NODE_ENV === 'development' ? debugInfo.body : '[REDACTED]',
    });
  }
  
  // Log API responses with timing information
  logResponse(requestId: string, response: Response, body?: any) {
    const request = this.activeRequests.get(requestId);
    
    if (!request) {
      logger.warn('Response logged for unknown request', { requestId });
      return;
    }
    
    const duration = performance.now() - request.startTime;
    
    const responseInfo: ResponseDebugInfo = {
      status: response.status,
      headers: Object.fromEntries(response.headers.entries()),
      body,
      duration,
    };
    
    // Log with appropriate level based on status
    const logLevel = response.status >= 400 ? 'error' : 'http';
    
    logger[logLevel]('API Response Received', {
      requestId,
      url: request.url,
      status: response.status,
      duration: `${duration.toFixed(2)}ms`,
      // Include rate limit headers for debugging
      rateLimitRemaining: response.headers.get('X-Shopify-Shop-Api-Call-Limit'),
      // Log response body in development or on error
      body: (process.env.NODE_ENV === 'development' || response.status >= 400) 
        ? body 
        : '[REDACTED]',
    });
    
    // Track slow requests (similar to Laravel's slow query logging)
    if (duration > 1000) {
      logger.warn('Slow API Request Detected', {
        url: request.url,
        duration: `${duration.toFixed(2)}ms`,
        threshold: '1000ms',
      });
    }
    
    // Clean up
    this.activeRequests.delete(requestId);
    
    // Send to Sentry if error
    if (response.status >= 500) {
      Sentry.captureException(new Error(`API Error: ${response.status}`), {
        tags: {
          url: request.url,
          status: response.status,
        },
        extra: responseInfo,
      });
    }
  }
  
  // Sanitize sensitive headers before logging
  private sanitizeHeaders(headers: Record<string, string>): Record<string, string> {
    const sensitiveHeaders = ['authorization', 'x-shopify-access-token', 'cookie'];
    const sanitized = { ...headers };
    
    sensitiveHeaders.forEach(key => {
      if (sanitized[key.toLowerCase()]) {
        sanitized[key.toLowerCase()] = '[REDACTED]';
      }
    });
    
    return sanitized;
  }
}

// ========================================
// File: app/lib/debugging/shopify-api-debugger.ts
// Purpose: Enhanced Shopify API client with debugging
// ========================================

import { shopifyApp } from '@shopify/shopify-app-remix';
import { NetworkDebugger } from './request-debugger';
import { logger } from './logger';
import { v4 as uuidv4 } from 'uuid';

const networkDebugger = new NetworkDebugger();

// Wrapper for GraphQL queries with debugging
export async function debuggedGraphQLQuery(
  admin: any,
  query: string,
  variables?: any
) {
  const requestId = uuidv4();
  const operationName = extractOperationName(query);
  
  logger.debug('GraphQL Query Execution', {
    requestId,
    operationName,
    variables: process.env.NODE_ENV === 'development' ? variables : '[REDACTED]',
  });
  
  const startTime = performance.now();
  
  try {
    // Execute the query
    const response = await admin.graphql(query, { variables });
    
    const duration = performance.now() - startTime;
    
    // Parse response for debugging
    const responseBody = await response.json();
    
    // Log successful query
    logger.info('GraphQL Query Completed', {
      requestId,
      operationName,
      duration: `${duration.toFixed(2)}ms`,
      hasErrors: !!responseBody.errors,
      // Log extensions for cost analysis
      cost: responseBody.extensions?.cost,
    });
    
    // Log GraphQL errors separately
    if (responseBody.errors) {
      logger.error('GraphQL Errors', {
        requestId,
        operationName,
        errors: responseBody.errors,
      });
      
      // Send to Sentry for monitoring
      Sentry.captureException(new Error('GraphQL Query Error'), {
        tags: { operationName },
        extra: {
          query,
          variables,
          errors: responseBody.errors,
        },
      });
    }
    
    // Check for rate limiting
    const cost = responseBody.extensions?.cost;
    if (cost?.throttleStatus?.currentlyAvailable < 100) {
      logger.warn('GraphQL Rate Limit Warning', {
        available: cost.throttleStatus.currentlyAvailable,
        maximum: cost.throttleStatus.maximumAvailable,
        restoreRate: cost.throttleStatus.restoreRate,
      });
    }
    
    return responseBody;
  } catch (error) {
    const duration = performance.now() - startTime;
    
    logger.error('GraphQL Query Failed', {
      requestId,
      operationName,
      duration: `${duration.toFixed(2)}ms`,
      error: error.message,
      stack: error.stack,
    });
    
    // Send to Sentry
    Sentry.captureException(error, {
      tags: { operationName },
      extra: { query, variables },
    });
    
    throw error;
  }
}

// Extract operation name from GraphQL query
function extractOperationName(query: string): string {
  const match = query.match(/^\s*(query|mutation)\s+(\w+)/);
  return match ? match[2] : 'Anonymous';
}

// ========================================
// File: app/lib/debugging/function-debugger.ts
// Purpose: Shopify Functions debugging helpers
// ========================================

import { exec } from 'child_process';
import { promisify } from 'util';
import { logger } from './logger';

const execAsync = promisify(exec);

export class FunctionDebugger {
  // Replay function execution locally for debugging
  async replayFunction(
    functionHandle: string,
    logFileId?: string
  ): Promise<void> {
    try {
      const command = logFileId
        ? `shopify app function replay --log ${logFileId}`
        : `shopify app function replay`;
      
      logger.info('Replaying function execution', {
        functionHandle,
        logFileId,
      });
      
      const { stdout, stderr } = await execAsync(command, {
        cwd: `extensions/${functionHandle}`,
      });
      
      if (stdout) {
        logger.info('Function replay output', { output: stdout });
      }
      
      if (stderr) {
        logger.error('Function replay error', { error: stderr });
      }
    } catch (error) {
      logger.error('Failed to replay function', {
        functionHandle,
        error: error.message,
      });
      throw error;
    }
  }
  
  // Run function with custom input for testing
  async runFunctionWithInput(
    functionHandle: string,
    input: any
  ): Promise<any> {
    try {
      const inputJson = JSON.stringify(input);
      const command = `echo '${inputJson}' | shopify app function run --json`;
      
      logger.debug('Running function with input', {
        functionHandle,
        inputSize: inputJson.length,
      });
      
      const { stdout } = await execAsync(command, {
        cwd: `extensions/${functionHandle}`,
      });
      
      const result = JSON.parse(stdout);
      
      // Log performance metrics
      logger.info('Function execution metrics', {
        functionHandle,
        duration: result.duration,
        memory: result.memory,
        logs: result.logs,
      });
      
      // Check for performance issues
      if (result.duration > 5) {
        logger.warn('Function performance warning', {
          functionHandle,
          duration: result.duration,
          threshold: 5,
        });
      }
      
      return result;
    } catch (error) {
      logger.error('Function execution failed', {
        functionHandle,
        error: error.message,
      });
      throw error;
    }
  }
}

// ========================================
// File: app/lib/debugging/webhook-debugger.ts
// Purpose: Webhook delivery monitoring and debugging
// ========================================

interface WebhookDelivery {
  topic: string;
  shop: string;
  timestamp: Date;
  success: boolean;
  responseTime?: number;
  error?: string;
}

export class WebhookDebugger {
  private deliveries: WebhookDelivery[] = [];
  private readonly maxDeliveries = 100;
  
  // Log webhook reception
  logWebhookReceived(topic: string, shop: string, body: any) {
    const timestamp = new Date();
    
    logger.info('Webhook Received', {
      topic,
      shop,
      timestamp,
      bodySize: JSON.stringify(body).length,
      // Log sample of body in development
      bodySample: process.env.NODE_ENV === 'development' 
        ? JSON.stringify(body).substring(0, 200) 
        : undefined,
    });
    
    return { topic, shop, timestamp };
  }
  
  // Log webhook processing result
  logWebhookProcessed(
    delivery: { topic: string; shop: string; timestamp: Date },
    success: boolean,
    error?: Error
  ) {
    const responseTime = Date.now() - delivery.timestamp.getTime();
    
    const deliveryRecord: WebhookDelivery = {
      ...delivery,
      success,
      responseTime,
      error: error?.message,
    };
    
    // Store for analysis
    this.deliveries.unshift(deliveryRecord);
    if (this.deliveries.length > this.maxDeliveries) {
      this.deliveries.pop();
    }
    
    const logLevel = success ? 'info' : 'error';
    
    logger[logLevel]('Webhook Processed', {
      topic: delivery.topic,
      shop: delivery.shop,
      success,
      responseTime: `${responseTime}ms`,
      error: error?.message,
    });
    
    // Alert on slow webhooks (similar to Spring Boot's metrics)
    if (responseTime > 3000) {
      logger.warn('Slow Webhook Processing', {
        topic: delivery.topic,
        responseTime: `${responseTime}ms`,
        threshold: '3000ms',
      });
    }
    
    // Send errors to Sentry
    if (!success && error) {
      Sentry.captureException(error, {
        tags: {
          webhook_topic: delivery.topic,
          shop: delivery.shop,
        },
      });
    }
  }
  
  // Get webhook metrics for monitoring
  getMetrics() {
    const totalDeliveries = this.deliveries.length;
    const failedDeliveries = this.deliveries.filter(d => !d.success).length;
    const avgResponseTime = this.deliveries
      .filter(d => d.responseTime)
      .reduce((sum, d) => sum + d.responseTime!, 0) / totalDeliveries;
    
    return {
      totalDeliveries,
      failedDeliveries,
      failureRate: (failedDeliveries / totalDeliveries) * 100,
      avgResponseTime,
      recentDeliveries: this.deliveries.slice(0, 10),
    };
  }
}

// ========================================
// File: app/lib/debugging/error-boundary.tsx
// Purpose: React error boundary with debugging
// ========================================

import React from 'react';
import * as Sentry from '@sentry/react';
import { logger } from './logger';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

export class DebugErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log to our custom logger
    logger.error('React Error Boundary Triggered', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });
    
    // Send to Sentry with React context
    Sentry.withScope((scope) => {
      scope.setContext('react', {
        componentStack: errorInfo.componentStack,
      });
      Sentry.captureException(error);
    });
    
    this.setState({ error, errorInfo });
  }
  
  render() {
    if (this.state.hasError) {
      // Development error display with full details
      if (process.env.NODE_ENV === 'development') {
        return (
          <div style={{ padding: '20px', backgroundColor: '#fee', border: '1px solid #fcc' }}>
            <h2>Application Error</h2>
            <details style={{ whiteSpace: 'pre-wrap' }}>
              <summary>Error Details</summary>
              {this.state.error?.toString()}
              <br />
              {this.state.errorInfo?.componentStack}
            </details>
          </div>
        );
      }
      
      // Production error display
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Something went wrong</h2>
          <p>We've been notified and are working on a fix.</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}

// ========================================
// File: app/routes/api.debug.tsx
// Purpose: Debug endpoint for development
// Only available in development environment
// ========================================

import { json } from '@remix-run/node';
import type { LoaderFunction } from '@remix-run/node';
import { logger } from '~/lib/debugging/logger';
import { WebhookDebugger } from '~/lib/debugging/webhook-debugger';

const webhookDebugger = new WebhookDebugger();

export const loader: LoaderFunction = async ({ request }) => {
  // Only allow in development
  if (process.env.NODE_ENV !== 'development') {
    return json({ error: 'Not available in production' }, { status: 403 });
  }
  
  // Get debug information
  const url = new URL(request.url);
  const type = url.searchParams.get('type');
  
  switch (type) {
    case 'logs':
      // Return recent logs (implement log retrieval)
      return json({
        logs: 'Recent logs here',
      });
      
    case 'webhooks':
      // Return webhook metrics
      return json(webhookDebugger.getMetrics());
      
    case 'health':
      // Return health check (similar to Spring Boot actuator)
      return json({
        status: 'UP',
        timestamp: new Date(),
        environment: process.env.NODE_ENV,
        memory: process.memoryUsage(),
        uptime: process.uptime(),
      });
      
    default:
      return json({
        available: ['logs', 'webhooks', 'health'],
      });
  }
};

// ========================================
// File: app/root.tsx
// Purpose: Integrate debugging into the app root
// ========================================

import { json } from '@remix-run/node';
import { Links, Meta, Outlet, Scripts, ScrollRestoration } from '@remix-run/react';
import { DebugErrorBoundary } from '~/lib/debugging/error-boundary';
import { logger } from '~/lib/debugging/logger';

// Wrap the app in error boundary for debugging
export default function App() {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <DebugErrorBoundary>
          <Outlet />
        </DebugErrorBoundary>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

// Enhanced error boundary for better debugging
export function ErrorBoundary({ error }: { error: Error }) {
  // Log the error
  logger.error('Application Error', {
    message: error.message,
    stack: error.stack,
  });
  
  return (
    <html>
      <head>
        <title>Error!</title>
        <Meta />
        <Links />
      </head>
      <body>
        <div>
          <h1>Application Error</h1>
          {process.env.NODE_ENV === 'development' && (
            <pre>{error.stack}</pre>
          )}
        </div>
        <Scripts />
      </body>
    </html>
  );
}

// ========================================
// File: package.json additions
// Purpose: Required debugging dependencies
// ========================================
/*
{
  "dependencies": {
    "@sentry/node": "^7.80.0",
    "@sentry/react": "^7.80.0",
    "@sentry/profiling-node": "^1.3.0",
    "winston": "^3.11.0",
    "uuid": "^9.0.1"
  },
  "devDependencies": {
    "@types/uuid": "^9.0.7"
  }
}
*/

// ========================================
// File: .env.example
// Purpose: Environment variables for debugging
// ========================================
/*
# Sentry Configuration
SENTRY_DSN=your-sentry-dsn-here

# Logging Configuration
LOG_LEVEL=debug # Options: error, warn, info, http, debug

# Development Debugging
NODE_ENV=development
DEBUG=shopify:*
*/
```

## **5. Recent Changes to Be Aware Of**

According to Shopify's current documentation, several important debugging features have been introduced or updated recently. The `app logs` command now provides JSON output format and advanced filtering capabilities, which wasn't available in older CLI versions. The Partner Dashboard has enhanced webhook delivery metrics that show failed delivery rates, removed webhooks, and response times with up to 7 days of historical data. Additionally, Shopify Functions now support the `app function replay` command, allowing you to replay production function executions locally, which significantly improves debugging capabilities compared to the previous approach of only having static logs.

The move away from REST API debugging toward GraphQL debugging represents a significant shift. The GraphQL Admin API now includes cost analysis in the extensions field, helping you debug rate limiting issues more effectively. The development version of Shopify App Bridge now includes TypeScript-like error messages, providing much clearer debugging information than the previous generic error responses.

## **6. Real-World Scenarios Based on Current Capabilities**

Let me walk you through three practical debugging scenarios you'll encounter when building Shopify apps, each demonstrating different debugging techniques.

**Scenario 1: Debugging a Failed Webhook Delivery**

Imagine your app isn't receiving order creation webhooks. The debugging process starts in your Partner Dashboard's webhook metrics, where you notice a 15% failure rate for the `orders/create` topic. The logs show 429 status codes, indicating your endpoint is being rate-limited.

Using the debugging setup I've shown you, you'd check your application logs and find that webhook processing is taking 4-5 seconds due to synchronous API calls. The solution involves implementing asynchronous processing: receiving the webhook, immediately returning a 200 response, then processing the order data in a background job. This pattern is similar to Laravel's queued jobs or Spring Boot's @Async methods.

**Scenario 2: Tracking Down a GraphQL Rate Limit Issue**

Your app suddenly starts receiving errors during peak hours. The debugging process reveals that your GraphQL queries are hitting rate limits. Using the cost analysis from the GraphQL response extensions, you discover that a single query is consuming 800 points out of your 1000-point budget.

The solution involves query optimization: breaking large queries into smaller ones, implementing field-level caching, and using the bulk operations API for large data fetches. The debugging tools help you identify expensive query patterns and optimize them, much like analyzing slow queries in Laravel's query log or Spring Boot's SQL logging.

**Scenario 3: Debugging Shopify Function Performance Issues**

A discount function is timing out intermittently. Using the `app function replay` command with production inputs, you reproduce the issue locally. The function logs reveal that it's iterating through 10,000 line items inefficiently.

The debugging process involves using the `--json` flag with `app function run` to get precise performance metrics, then optimizing the algorithm to use hash maps instead of nested loops. This is similar to profiling performance bottlenecks in Spring Boot with tools like JProfiler or debugging Laravel applications with Clockwork.

## **7. Advanced Patterns from Latest Documentation**

Shopify's latest documentation emphasizes several advanced debugging patterns that improve application reliability. 

The circuit breaker pattern for API calls prevents cascading failures when Shopify's API experiences issues. When your app detects multiple failed API calls, it temporarily stops making requests and returns cached data or graceful degradation responses. This pattern, familiar from Spring Boot's Resilience4j library, is particularly important for maintaining app stability during Shopify platform incidents.

Distributed tracing across webhook processing and API calls helps you understand the full request lifecycle. By generating trace IDs at the webhook entry point and propagating them through all subsequent API calls and function executions, you can correlate logs across different services. This approach mirrors Spring Boot's distributed tracing with Sleuth and Zipkin.

The implementation of health check endpoints provides proactive monitoring capabilities. These endpoints check database connectivity, API availability, and webhook processing status, returning structured health information that monitoring services can consume. This pattern, directly inspired by Spring Boot's actuator endpoints, enables early detection of issues before they impact merchants.

## **8. Hands-On Exercise**

Now it's time to put your debugging skills into practice with a realistic scenario that combines multiple debugging techniques.

**Exercise: Debug a Webhook Processing Pipeline**

Your task is to build and debug a webhook processing system that handles `products/update` webhooks with the following requirements: Process webhooks asynchronously to respond within 5 seconds, implement retry logic for failed API calls, track processing metrics for monitoring, and provide detailed debugging information without exposing sensitive data.

Start by implementing the webhook endpoint using the debugging infrastructure from our example. Add artificial delays to simulate slow API calls and observe how the debugging tools help identify bottlenecks. Introduce intentional errors to test your error tracking integration with Sentry.

**Acceptance Criteria:**
- Webhook endpoint responds within 500ms regardless of processing time
- Failed webhooks are logged with full context but sensitive data is redacted
- Slow API calls (>1 second) generate warning logs
- Metrics endpoint provides processing statistics
- Error boundary catches and reports React component errors

**Hints from Your Background:**
Think about this like Laravel's job queues - receive the webhook, queue the job, and process asynchronously. Use middleware patterns similar to Spring Boot for consistent request/response logging. Apply the same structured logging principles you'd use with SLF4J in Spring Boot, but adapted for Winston in Node.js.

## **9. Migration Path and Current Best Practices**

Moving from older debugging patterns to current best practices requires systematic updates to your debugging infrastructure. 

Replace console.log statements with structured logging using Winston or similar libraries. The old pattern of scattered console.log calls makes debugging production issues nearly impossible. The new approach uses structured logging with consistent formatting, log levels, and contextual information, similar to migrating from print statements to proper logging in Spring Boot.

Migrate from the deprecated `app generate node` CLI commands to the current `app dev` and `app logs` commands. The old commands lacked real-time streaming and function execution details. The new commands provide comprehensive debugging information including function inputs, outputs, and performance metrics.

Update error handling from try-catch blocks that silently swallow errors to proper error boundaries and Sentry integration. The old pattern lost valuable debugging information, while the new approach captures full error context including stack traces, user actions, and application state.

Common mistakes developers make include not implementing proper webhook timeout handling, leading to webhook removal after failed retries. Another frequent error is not monitoring GraphQL query costs, resulting in unexpected rate limiting during traffic spikes. Developers often forget to implement health check endpoints, making it difficult to detect issues proactively.

## **10. Verification and Resources**

The debugging techniques and code examples I've provided are based on current Shopify documentation verified through the MCP tools. The GraphQL debugging patterns align with the 2025-07 API version's cost analysis features. The Shopify CLI commands reflect the latest 3.80+ version capabilities.

Key documentation resources for debugging include:
- [Test and debug Shopify Functions](https://shopify.dev/docs/apps/build/functions/test-debug-functions) - Last updated for 2025-07 API version
- [Troubleshooting webhooks](https://shopify.dev/docs/apps/build/webhooks/troubleshooting-webhooks) - Includes latest webhook metrics dashboard
- [Select a networking option](https://shopify.dev/docs/apps/build/cli-for-apps/networking-options) - Updated with localhost development options

Related concepts to explore next include performance optimization using the subrequest profiler, implementing caching strategies to reduce API calls, and setting up continuous integration with automated testing.

## **Production Considerations for 2025**

As we head into production, several critical debugging considerations have emerged from recent Shopify platform updates. The Partner Dashboard now retains webhook logs for only 7 days, making external log aggregation essential for long-term debugging. Shopify Functions have stricter timeout limits (11ms for cart operations), requiring careful performance monitoring. The platform's move toward event-driven architectures means debugging often involves tracing events across multiple systems.

Implement comprehensive monitoring from day one rather than adding it after issues arise. Set up alerts for critical thresholds: webhook failure rates above 0.5%, GraphQL costs exceeding 80% of available points, and function execution times approaching timeout limits. These proactive measures prevent debugging from becoming reactive firefighting.

Remember that debugging in production requires different strategies than local development. You can't attach debuggers or add console.log statements on the fly. Instead, you rely on structured logging, distributed tracing, and error tracking services to understand application behavior. The debugging infrastructure we've built provides these capabilities while maintaining security and performance.
