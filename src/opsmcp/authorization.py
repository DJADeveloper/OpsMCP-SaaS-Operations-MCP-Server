"""Trusted, fail-closed role policy for the local OpsMCP demonstration.

The caller role must be established by a trusted host; never take it from
model-generated tool arguments. This does not authenticate remote users.
"""
from dataclasses import dataclass
from enum import Enum


class PermissionDenied(PermissionError):
    """Caller lacks permission for the requested operation."""


class Role(str, Enum):
    ADMIN = "admin"
    SUPPORT_AGENT = "support_agent"
    FINANCE_ANALYST = "finance_analyst"


class Permission(str, Enum):
    CUSTOMERS_READ = "customers:read"
    TICKETS_READ = "tickets:read"
    INCIDENTS_READ = "incidents:read"
    POLICIES_READ = "policies:read"
    REVENUE_READ = "revenue:read"


ROLE_PERMISSIONS = {
    Role.ADMIN: frozenset(Permission),
    Role.SUPPORT_AGENT: frozenset({
        Permission.CUSTOMERS_READ, Permission.TICKETS_READ,
        Permission.INCIDENTS_READ, Permission.POLICIES_READ,
    }),
    Role.FINANCE_ANALYST: frozenset({
        Permission.CUSTOMERS_READ, Permission.REVENUE_READ,
        Permission.POLICIES_READ,
    }),
}


@dataclass(frozen=True)
class AuthorizationPolicy:
    role: Role

    def __post_init__(self):
        if not isinstance(self.role, Role):
            raise ValueError("A recognized trusted role is required")

    def require(self, permission: Permission) -> None:
        if not isinstance(permission, Permission) or permission not in ROLE_PERMISSIONS[self.role]:
            raise PermissionDenied("Permission denied")

    def permits(self, permission: Permission) -> bool:
        return isinstance(permission, Permission) and permission in ROLE_PERMISSIONS[self.role]
