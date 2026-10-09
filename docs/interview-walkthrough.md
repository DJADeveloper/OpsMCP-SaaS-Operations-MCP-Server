# Explain OpsMCP in an interview

**Problem:** Give AI hosts a safe, discoverable interface to deterministic SaaS operations data.

**Design:** A Python FastMCP server registers five typed read-only tools and two resources. A separate service implements domain logic and tenant-scoped data access.

**Why MCP instead of REST?** A compatible host can discover schemas and invoke tools through a standard protocol. REST remains appropriate for conventional application clients.

**Security:** The model is not an authorization boundary. The operator selects one organization when launching the local stdio process; tools cannot override it. This is not production multi-user auth.

**Testing:** Unit tests cover scoped data, calculations, and bad arguments. A separate MCP client smoke test checks the protocol handshake, tool discovery, resource reads, and cross-tenant denial.

**Tradeoff:** Fixture data makes the demo reproducible but does not establish production readiness. A future real integration needs verified caller identity, per-request authorization, rate limits, audit trails, and operational controls.

**Challenge:** If you move from local stdio to a shared remote HTTP endpoint, what changes? Answer: authenticate each caller, derive tenant scope from trusted identity, isolate request context, and prevent one user's scope from leaking into another's session.
