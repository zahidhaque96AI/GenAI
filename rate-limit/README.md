What we are trying to achieve?
RateLimit: 

When the application sends requests to an LLM provider, the provider may restrict how many requests you can send within a particular time period.

For example, suppose we configure our application to allow:
- Maximum 5 requests per minute.
- Maximum 100 requests per hour.
- If the provider returns HTTP 429 (Too Many Requests), retry after an appropriate delay.
We want to control outgoing API requests, avoid unnecessary failures, and handle provider throttling gracefully.

There are actually two separate responsibilities:
1. Rate limiter: Controls how frequently our application sends requests.
2. Retry mechanism: Handles temporary failures, such as HTTP 429 responses.