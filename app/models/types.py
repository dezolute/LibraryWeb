from enum import Enum


class Role(Enum):
    user = "user"
    admin = "admin"
    employee = "employee"


class Priority(Enum):
    low = "low"
    high = "high"


class Status(Enum):
    accepted = "accepted"
    in_queued = "in_queued"
    awaiting = "awaiting"
    given = "given"
    returned = "returned"
