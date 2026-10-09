"""End-to-end MCP stdio handshake, discovery, calls, and resource checks."""
import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    env = dict(os.environ)
    env["OPSMCP_ORG_ID"] = "acme"
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "opsmcp.server"], env=env
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            required = {"list_customers", "get_customer", "get_account_health",
                        "list_open_tickets", "search_incidents"}
            assert required <= {t.name for t in tools.tools}
            health = await session.call_tool("get_account_health", {"customer_id": "cus-101"})
            assert not health.isError, health
            assert "Northwind Labs" in str(health.content)
            forbidden = await session.call_tool("get_customer", {"customer_id": "cus-201"})
            assert forbidden.isError, forbidden
            assert "Confidential Beacon" not in str(forbidden.content)
            resources = await session.list_resources()
            assert {"company://policies", "company://summary"} <= {
                str(r.uri) for r in resources.resources
            }
            policy = await session.read_resource("company://policies")
            assert "Read-only" in str(policy)
            print("PASS: MCP stdio handshake, discovery, calls, tenant denial, resources")

if __name__ == "__main__":
    asyncio.run(main())
