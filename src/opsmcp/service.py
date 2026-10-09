"""Tenant-scoped business logic, independent of the MCP protocol."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

DEFAULT_DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "operations.json"

class OperationsError(ValueError):
    """Invalid or unauthorized operational request."""

class OperationsService:
    def __init__(self, organization_id: str, data_file: Path | None = None):
        if not isinstance(organization_id, str) or not organization_id.strip():
            raise ValueError("A server-controlled organization scope is required")
        self.organization_id = organization_id
        with (data_file or DEFAULT_DATA_FILE).open(encoding="utf-8") as f:
            self._data: dict[str, Any] = json.load(f)
        self._organization = next(
            (o for o in self._data["organizations"] if o["id"] == organization_id), None
        )
        if self._organization is None:
            raise ValueError("Configured organization does not exist")

    def _scoped(self, collection: str) -> list[dict[str, Any]]:
        return [row for row in self._data[collection]
                if row["organization_id"] == self.organization_id]

    def _customer(self, customer_id: str) -> dict[str, Any]:
        customer = next((c for c in self._scoped("customers")
                         if c["id"] == customer_id), None)
        if customer is None:
            # Avoid distinguishing missing IDs from cross-tenant IDs.
            raise OperationsError("Customer not found")
        return customer

    @staticmethod
    def _validate_limit(limit: int) -> None:
        if type(limit) is not int or not 1 <= limit <= 50:
            raise OperationsError("Limit must be between 1 and 50")

    def list_customers(self, limit: int = 20) -> list[dict[str, Any]]:
        self._validate_limit(limit)
        return [dict(c) for c in sorted(self._scoped("customers"),
                                      key=lambda c: c["id"])[:limit]]

    def get_customer(self, customer_id: str) -> dict[str, Any]:
        return dict(self._customer(customer_id))

    def list_open_tickets(self, customer_id: str, limit: int = 20) -> list[dict[str, Any]]:
        self._validate_limit(limit)
        self._customer(customer_id)
        tickets = [t for t in self._scoped("tickets")
                   if t["customer_id"] == customer_id and t["status"] == "open"]
        return [dict(t) for t in sorted(tickets,
                key=lambda t: (t["created_at"], t["id"]), reverse=True)[:limit]]

    def get_account_health(self, customer_id: str) -> dict[str, Any]:
        customer = self._customer(customer_id)
        # Count all tickets, not merely a paginated tool response.
        tickets = [t for t in self._scoped("tickets")
                   if t["customer_id"] == customer_id and t["status"] == "open"]
        score = customer["health_score"]
        return {
            "customer_id": customer_id,
            "customer_name": customer["name"],
            "health_score": score,
            "health_band": "low" if score < 50 else "watch" if score < 75 else "healthy",
            "usage_change_pct": customer["usage_change_pct"],
            "open_ticket_count": len(tickets),
            "high_severity_open_tickets": sum(
                t["severity"] in ("high", "critical") for t in tickets
            ),
            "interpretation": "Rule-based snapshot; not a churn prediction.",
        }

    def search_incidents(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        self._validate_limit(limit)
        if not isinstance(query, str) or not query.strip() or len(query) > 200:
            raise OperationsError("Query must contain 1 to 200 characters")
        needle = query.strip().casefold()
        incidents = [i for i in self._scoped("incidents")
                     if needle in (i["title"] + " " + i["summary"]).casefold()]
        return [dict(i) for i in sorted(incidents, key=lambda i: i["id"])[:limit]]

    def get_policies(self) -> str:
        return self._data["policies"][self.organization_id]

    def organization_summary(self) -> dict[str, Any]:
        customers = self._scoped("customers")
        return {
            "organization_id": self.organization_id,
            "organization_name": self._organization["name"],
            "customer_count": len(customers),
            "active_customer_count": sum(c["status"] == "active" for c in customers),
            "monthly_recurring_revenue_usd": sum(
                c["mrr_usd"] for c in customers if c["status"] == "active"
            ),
            "open_ticket_count": sum(
                t["status"] == "open" for t in self._scoped("tickets")
            ),
            "data_source": "deterministic demonstration fixtures",
        }
