from enum import Enum


class Role(str, Enum):
    user = "user"
    admin = "admin"
    employee = "employee"


class Priority(str, Enum):
    low = "low"
    high = "high"


class Status(str, Enum):
    accepted = "accepted"
    in_queued = "in_queued"
    awaiting = "awaiting"
    given = "given"
    returned = "returned"
