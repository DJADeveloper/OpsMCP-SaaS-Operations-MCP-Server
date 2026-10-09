# OpsMCP — SaaS Operations MCP Server

A standalone Python MCP server that exposes **deterministic, read-only SaaS operations intelligence** to compatible AI hosts.

## What it does

Five typed tools:
- `list_customers(limit)`
- `get_customer(customer_id)`
- `get_account_health(customer_id)`
- `list_open_tickets(customer_id, limit)`
- `search_incidents(query, limit)`

Two resources: `company://policies` and `company://summary`.

Uses synthetic data for two organizations. The trusted host sets the organization's scope at process launch; tools cannot select arbitrary tenants. **This is a local demo, not production authentication.**

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
uv run pytest -q
uv run python scripts/smoke_mcp.py
```

The last command starts a real MCP server subprocess over stdio and verifies discovery, tool calls, cross-tenant denial, and resource access.

## Connect to Claude Code

From a terminal with this project checked out:

```bash
claude mcp add opsmcp --env OPSMCP_ORG_ID=acme -- uv --directory "$(pwd)" run opsmcp
claude mcp list
```

Then ask Claude: *Use OpsMCP to investigate Northwind Labs and summarize its open support issues.* Confirm it actually invokes the OpsMCP tools.

## Design and limits

Host → MCP client → stdio MCP server → tenant-scoped OperationsService → JSON fixtures.

The model proposes calls; the trusted service validates and executes them. Tool results are data, not instructions. No LLM, agent, database, or remote HTTP endpoint is required for this demo.

Read [architecture decisions](docs/architecture.md) and the [interview walkthrough](docs/interview-walkthrough.md).

**Not yet verified:** the real MCP protocol smoke test until dependencies are installed and executed in a suitable environment. Do not claim production readiness.
