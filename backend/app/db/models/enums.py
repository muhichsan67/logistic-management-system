import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    COURIER = "COURIER"
    CUSTOMER = "CUSTOMER"


class ShipmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ASSIGNED = "ASSIGNED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    COMPLETED = "COMPLETED"
