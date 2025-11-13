from enum import Enum


class Role(str, Enum):
    READER = "READER"
    ADMIN = "ADMIN"
    EMPLOYEE = "EMPLOYEE"


class BookCopyStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    BORROWED = "BORROWED"
    RESERVED = "RESERVED"


class BookAccessType(str, Enum):
    READING_ROOM = "READING_ROOM"
    TAKE_HOME = "TAKE_HOME"


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    FULFILLED = "FULFILLED"
    QUEUED = "QUEUED"
