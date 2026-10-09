# OpsMCP architecture and decisions

## Problem
An AI host needs discoverable, typed, read-only SaaS operations capabilities without direct access to a database or unrestricted organization selection.

## Why MCP?
MCP provides standardized tool and resource discovery for compatible AI hosts. It is not needed for ordinary internal function calls or a single tightly coupled HTTP client.

## Architecture
MCP host → stdio MCP client → FastMCP server → OperationsService → deterministic JSON fixtures.

The protocol layer registers tools and resources. The service implements authorization scoping and deterministic business calculations, independently of MCP.

## Trust boundary
The operator starts one stdio process with OPSMCP_ORG_ID. Tool callers cannot choose an organization. All business collections are filtered by that trusted process scope. Missing and foreign customer IDs return the same error.

This is a local demonstration, **not** production authentication. Environment variables do not authenticate arbitrary remote users. Never expose this server as public multi-user HTTP without authentication, per-request authorization, and appropriate data controls.

## Why not an agent, RAG, database, or HTTP server?
Tools read structured facts; no autonomous planning, retrieval pipeline, persistence, or remote transport is required yet. These capabilities should be added only when concrete requirements justify them.

## Failure experiments
Try cross-tenant customer IDs, invalid limits, empty incident searches, missing customers, and a stopped server. Confirm errors are bounded and no foreign customer details appear.

## Limitations
Fixtures are synthetic; health bands are rule-based, not predictive; no live third-party integrations or remote authentication. The MCP protocol smoke test requires installation of the official SDK.
