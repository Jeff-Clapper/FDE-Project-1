# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

VALID_STATUSES = ("pending", "processing", "shipped", "delivered", "cancelled")


class DuplicateOrderError(ValueError):
    """Raised when an order ID is already in use."""


class OrderNotFoundError(ValueError):
    """Raised when an order ID does not match any stored order."""


def _require_non_empty_string(value, field_label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_label} must be a non-empty string.")


def _require_valid_status(status):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'.")


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        _require_non_empty_string(order_id, "Order ID")
        _require_non_empty_string(item_name, "Item name")
        # bool is a subclass of int, so True/False must be rejected explicitly.
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        _require_non_empty_string(customer_id, "Customer ID")
        _require_valid_status(status)

        if self.storage.get_order(order_id):
            raise DuplicateOrderError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order)
        return order

    def get_order_by_id(self, order_id: str):
        _require_non_empty_string(order_id, "Order ID")
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        _require_valid_status(new_status)
        _require_non_empty_string(order_id, "Order ID")

        existing_order = self.storage.get_order(order_id)
        if not existing_order:
            raise OrderNotFoundError(f"Order with ID '{order_id}' does not exist.")

        updated_order = existing_order.copy()
        updated_order["status"] = new_status
        self.storage.save_order(order_id, updated_order)
        return updated_order

    def list_all_orders(self):
        return list(self.storage.get_all_orders().values())

    def list_orders_by_status(self, status: str):
        _require_valid_status(status)
        return [order for order in self.list_all_orders() if order["status"] == status]
