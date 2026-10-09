import pytest
from opsmcp.service import OperationsError, OperationsService

@pytest.fixture
def acme():
    return OperationsService("acme")

def test_customer_scope(acme):
    assert acme.get_customer("cus-101")["name"] == "Northwind Labs"
    with pytest.raises(OperationsError, match="Customer not found"):
        acme.get_customer("cus-201")
    with pytest.raises(OperationsError, match="Customer not found"):
        acme.get_customer("does-not-exist")

def test_list_customers_scoped(acme):
    assert {c["id"] for c in acme.list_customers()} == {"cus-101", "cus-102"}
    assert {c["id"] for c in OperationsService("beacon").list_customers()} == {"cus-201"}

def test_tickets_scoped(acme):
    assert {t["id"] for t in acme.list_open_tickets("cus-101")} == {"tic-11", "tic-12"}
    with pytest.raises(OperationsError):
        acme.list_open_tickets("cus-201")

def test_health_is_rule_based(acme):
    result = acme.get_account_health("cus-101")
    assert result["health_band"] == "watch"
    assert result["open_ticket_count"] == 2
    assert result["high_severity_open_tickets"] == 1

def test_incident_scope(acme):
    assert [i["id"] for i in acme.search_incidents("SSO")] == ["inc-11"]
    assert acme.search_incidents("Confidential Beacon") == []

def test_summary_scope(acme):
    result = acme.organization_summary()
    assert result["monthly_recurring_revenue_usd"] == 6200
    assert result["open_ticket_count"] == 2
    assert "Beacon" not in str(result)

def test_resource_scope(acme):
    assert "Beacon" not in acme.get_policies()
    assert "Beacon" in OperationsService("beacon").get_policies()

@pytest.mark.parametrize("limit", [0, -1, 51, True, 1.5])
def test_invalid_limits(acme, limit):
    with pytest.raises(OperationsError):
        acme.list_customers(limit)

@pytest.mark.parametrize("query", ["", " ", "a" * 201])
def test_invalid_search(acme, query):
    with pytest.raises(OperationsError):
        acme.search_incidents(query)

def test_invalid_organization():
    with pytest.raises(ValueError):
        OperationsService("other")
