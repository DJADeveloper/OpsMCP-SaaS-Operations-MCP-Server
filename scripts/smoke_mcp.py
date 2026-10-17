"""End-to-end MCP stdio handshake, discovery, calls, and tenant boundaries."""
import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


REQUIRED_TOOLS = {
    "list_customers",
    "get_customer",
    "get_account_health",
    "list_open_tickets",
    "search_incidents",
}
REQUIRED_RESOURCES = {"company://policies", "company://summary"}


async def verify_organization(
    organization_id: str, own_customer_id: str, foreign_customer_id: str, own_name: str
) -> None:
    # Tenant identity is controlled by the launching host, not a model argument.
    env = dict(os.environ)
    env["OPSMCP_ORG_ID"] = organization_id
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "opsmcp.server"], env=env
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            assert REQUIRED_TOOLS <= {tool.name for tool in tools.tools}

            own = await session.call_tool(
                "get_customer", {"customer_id": own_customer_id}
            )
            assert not own.isError, own
            assert own_name in str(own.content)

            customers = await session.call_tool("list_customers", {"limit": 50})
            assert not customers.isError, customers
            assert own_customer_id in str(customers.content)
            assert foreign_customer_id not in str(customers.content)

            tickets = await session.call_tool(
                "list_open_tickets", {"customer_id": own_customer_id}
            )
            assert not tickets.isError, tickets

            health = await session.call_tool(
                "get_account_health", {"customer_id": own_customer_id}
            )
            assert not health.isError, health

            foreign = await session.call_tool(
                "get_customer", {"customer_id": foreign_customer_id}
            )
            assert foreign.isError, foreign
            assert "Customer not found" in str(foreign.content)

            foreign_tickets = await session.call_tool(
                "list_open_tickets", {"customer_id": foreign_customer_id}
            )
            assert foreign_tickets.isError, foreign_tickets

            resources = await session.list_resources()
            assert REQUIRED_RESOURCES <= {
                str(resource.uri) for resource in resources.resources
            }
            policy = await session.read_resource("company://policies")
            summary = await session.read_resource("company://summary")
            assert policy.contents, "Expected nonempty policies resource"
            assert organization_id in str(summary), "Summary must reflect host scope"
            assert foreign_customer_id not in str(summary)
            assert foreign_customer_id not in str(policy)


async def main() -> None:
    await verify_organization("acme", "cus-101", "cus-201", "Northwind Labs")
    await verify_organization("beacon", "cus-201", "cus-101", "Confidential Beacon")
    print("PASS: MCP stdio handshake, discovery, calls, cross-tenant denials, resources (both scopes)")


if __name__ == "__main__":
    asyncio.run(main())
