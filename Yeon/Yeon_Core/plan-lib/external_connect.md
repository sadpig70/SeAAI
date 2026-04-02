# Plan: external_connect

## Purpose
Connect to external APIs and platforms on behalf of SeAAI members.

## Steps
1. Validate endpoint URL format.
2. Attach auth token (if provided).
3. Send HTTP request using Python `urllib` or `requests`.
4. Parse JSON response.
5. On error, return structured `error_dict` with code and message.

## Acceptance
- Response is valid JSON or structured error.
- No secrets are logged to plain text.
