from enum import Enum


class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    EMPLOYEE = "EMPLOYEE"


class Priority(str, Enum):
    LOW = "LOW"
    HIGH = "HIGH"


class Status(str, Enum):
    ACCEPTED = "ACCEPTED"
    IN_QUEUED = "IN_QUEUED"
    AWAITING = "AWAITING"
    GIVEN = "GIVEN"
    RETURNED = "RETURNED"
