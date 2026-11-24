import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---


@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock


@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#

# --- add_order ---


def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(
        ValueError, match="Order with ID 'ORD_EXISTING' already exists."
    ):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")


def test_add_order_saves_order_details_with_default_status(
        order_tracker, mock_storage):
    """Tests that the stored order has every field and defaults to pending."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    mock_storage.save_order.assert_called_once_with("ORD001", {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    })


def test_add_order_with_explicit_valid_status(order_tracker, mock_storage):
    """Tests that a valid status supplied by the caller is stored."""
    order_tracker.add_order(
        "ORD002", "Mouse", 2, "CUST002", status="processing"
    )

    saved_order = mock_storage.save_order.call_args.args[1]
    assert saved_order["status"] == "processing"


def test_add_order_returns_created_order(order_tracker):
    """Tests that add_order returns the order it created."""
    order = order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    assert order == {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }


def test_add_order_duplicate_does_not_save(order_tracker, mock_storage):
    """Tests that a duplicate order is not written to storage."""
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize("bad_order_id", ["", "   ", None, 123])
def test_add_order_rejects_invalid_order_id(
        order_tracker, mock_storage, bad_order_id):
    """Tests that order_id must be a non-empty string."""
    with pytest.raises(
        ValueError, match="Order ID must be a non-empty string."
    ):
        order_tracker.add_order(bad_order_id, "Laptop", 1, "CUST001")

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize("bad_item_name", ["", "   ", None, 42])
def test_add_order_rejects_invalid_item_name(
        order_tracker, mock_storage, bad_item_name):
    """Tests that item_name must be a non-empty string."""
    with pytest.raises(
        ValueError, match="Item name must be a non-empty string."
    ):
        order_tracker.add_order("ORD001", bad_item_name, 1, "CUST001")

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize("bad_customer_id", ["", "   ", None, 7])
def test_add_order_rejects_invalid_customer_id(
        order_tracker, mock_storage, bad_customer_id):
    """Tests that customer_id must be a non-empty string."""
    with pytest.raises(
        ValueError, match="Customer ID must be a non-empty string."
    ):
        order_tracker.add_order("ORD001", "Laptop", 1, bad_customer_id)

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize("bad_quantity", [0, -1, 1.5, "1", None, True])
def test_add_order_rejects_invalid_quantity(
        order_tracker, mock_storage, bad_quantity):
    """Tests that quantity must be a positive integer (not a boolean)."""
    with pytest.raises(
        ValueError, match="Quantity must be a positive integer."
    ):
        order_tracker.add_order("ORD001", "Laptop", bad_quantity, "CUST001")

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize("bad_status", ["flying", "", "Pending", None])
def test_add_order_rejects_invalid_status(
        order_tracker, mock_storage, bad_status):
    """Tests that only the allowed statuses can be used for a new order."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.add_order(
            "ORD001", "Laptop", 1, "CUST001", status=bad_status
        )

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()

# --- get_order_by_id ---


def test_get_order_returns_existing_order(order_tracker, mock_storage):
    """Tests that an existing order is returned from storage."""
    existing_order = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing_order

    order = order_tracker.get_order_by_id("ORD001")

    assert order == existing_order
    mock_storage.get_order.assert_called_once_with("ORD001")


def test_get_order_returns_none_when_missing(order_tracker, mock_storage):
    """Tests that None is returned when no order matches the ID."""
    mock_storage.get_order.return_value = None

    order = order_tracker.get_order_by_id("MISSING")

    assert order is None
    mock_storage.get_order.assert_called_once_with("MISSING")


@pytest.mark.parametrize("bad_order_id", ["", "   ", None, 123])
def test_get_order_rejects_invalid_id(
        order_tracker, mock_storage, bad_order_id):
    """Tests that an empty or non-string ID is rejected before storage."""
    with pytest.raises(
        ValueError, match="Order ID must be a non-empty string."
    ):
        order_tracker.get_order_by_id(bad_order_id)

    mock_storage.get_order.assert_not_called()

# --- update_order_status ---


def test_update_order_status_saves_new_status(order_tracker, mock_storage):
    """Tests that an existing order is saved with its new status."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }

    order_tracker.update_order_status("ORD001", "shipped")

    mock_storage.get_order.assert_called_once_with("ORD001")
    mock_storage.save_order.assert_called_once_with("ORD001", {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "shipped",
    })


def test_update_order_status_returns_updated_order(
        order_tracker, mock_storage):
    """Tests that the updated order is returned to the caller."""
    mock_storage.get_order.return_value = {
        "order_id": "ORD001", "status": "pending"
    }

    updated_order = order_tracker.update_order_status("ORD001", "shipped")

    assert updated_order == {"order_id": "ORD001", "status": "shipped"}


def test_update_order_status_does_not_mutate_stored_order(
        order_tracker, mock_storage):
    """Tests that the order from storage is copied, not changed in place."""
    existing_order = {"order_id": "ORD001", "status": "pending"}
    mock_storage.get_order.return_value = existing_order

    order_tracker.update_order_status("ORD001", "shipped")

    saved_order = mock_storage.save_order.call_args.args[1]
    assert saved_order["status"] == "shipped"
    assert saved_order is not existing_order
    assert existing_order["status"] == "pending"


@pytest.mark.parametrize("bad_status", ["flying", "", None])
def test_update_order_status_rejects_invalid_status_before_storage(
        order_tracker, mock_storage, bad_status):
    """Tests that an invalid status fails before storage is read or written."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.update_order_status("ORD001", bad_status)

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_raises_error_if_missing(
        order_tracker, mock_storage):
    """Tests that updating a nonexistent order raises a ValueError."""
    mock_storage.get_order.return_value = None

    with pytest.raises(
        ValueError, match="Order with ID 'MISSING' does not exist."
    ):
        order_tracker.update_order_status("MISSING", "shipped")

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize("bad_order_id", ["", "   ", None, 123])
def test_update_order_status_rejects_invalid_id(
        order_tracker, mock_storage, bad_order_id):
    """Tests that an empty or non-string ID is rejected before storage."""
    with pytest.raises(
        ValueError, match="Order ID must be a non-empty string."
    ):
        order_tracker.update_order_status(bad_order_id, "shipped")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()

# --- list_all_orders ---


def test_list_all_orders_returns_empty_list_when_no_orders(
        order_tracker, mock_storage):
    """Tests that an empty list is returned when storage has no orders."""
    mock_storage.get_all_orders.return_value = {}

    orders = order_tracker.list_all_orders()

    assert orders == []
    mock_storage.get_all_orders.assert_called_once_with()


def test_list_all_orders_returns_every_order(order_tracker, mock_storage):
    """Tests that every stored order is returned as a list of dictionaries."""
    order_1 = {
        "order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
        "customer_id": "CUST001", "status": "pending",
    }
    order_2 = {
        "order_id": "ORD002", "item_name": "Mouse", "quantity": 2,
        "customer_id": "CUST002", "status": "shipped",
    }
    mock_storage.get_all_orders.return_value = {
        "ORD001": order_1, "ORD002": order_2
    }

    orders = order_tracker.list_all_orders()

    assert isinstance(orders, list)
    assert len(orders) == 2
    assert order_1 in orders
    assert order_2 in orders
    mock_storage.get_all_orders.assert_called_once_with()

# --- list_orders_by_status ---


@pytest.fixture
def mixed_status_orders():
    """Three stored orders: one pending and two shipped."""
    return {
        "ORD001": {
            "order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
            "customer_id": "CUST001", "status": "pending",
        },
        "ORD002": {
            "order_id": "ORD002", "item_name": "Mouse", "quantity": 2,
            "customer_id": "CUST002", "status": "shipped",
        },
        "ORD003": {
            "order_id": "ORD003", "item_name": "Monitor", "quantity": 1,
            "customer_id": "CUST003", "status": "shipped",
        },
    }


def test_list_orders_by_status_returns_matching_orders(
        order_tracker, mock_storage, mixed_status_orders):
    """Tests that only orders with the requested status are returned."""
    mock_storage.get_all_orders.return_value = mixed_status_orders

    orders = order_tracker.list_orders_by_status("shipped")

    assert isinstance(orders, list)
    order_ids = sorted(order["order_id"] for order in orders)
    assert order_ids == ["ORD002", "ORD003"]


def test_list_orders_by_status_returns_empty_list_when_no_match(
        order_tracker, mock_storage, mixed_status_orders):
    """Tests that a valid status with no matching orders returns []."""
    mock_storage.get_all_orders.return_value = mixed_status_orders

    orders = order_tracker.list_orders_by_status("delivered")

    assert orders == []


def test_list_orders_by_status_returns_empty_list_when_storage_empty(
        order_tracker, mock_storage):
    """Tests that filtering an empty store returns an empty list."""
    mock_storage.get_all_orders.return_value = {}

    orders = order_tracker.list_orders_by_status("pending")

    assert orders == []
    mock_storage.get_all_orders.assert_called_once_with()


@pytest.mark.parametrize("bad_status", ["", "flying", None])
def test_list_orders_by_status_rejects_invalid_status(
        order_tracker, mock_storage, bad_status):
    """Tests that an empty or invalid status is rejected before storage."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.list_orders_by_status(bad_status)

    mock_storage.get_all_orders.assert_not_called()

# --- list_orders_by_customer ---


@pytest.fixture
def mixed_customer_orders():
    """Three stored orders: two for CUST001 and one for CUST002."""
    return {
        "ORD001": {
            "order_id": "ORD001", "item_name": "Laptop", "quantity": 1,
            "customer_id": "CUST001", "status": "pending",
        },
        "ORD002": {
            "order_id": "ORD002", "item_name": "Mouse", "quantity": 2,
            "customer_id": "CUST001", "status": "shipped",
        },
        "ORD003": {
            "order_id": "ORD003", "item_name": "Monitor", "quantity": 1,
            "customer_id": "CUST002", "status": "pending",
        },
    }


def test_list_orders_by_customer_returns_only_that_customers_orders(
        order_tracker, mock_storage, mixed_customer_orders):
    """Tests that only orders for the requested customer are returned."""
    mock_storage.get_all_orders.return_value = mixed_customer_orders

    orders = order_tracker.list_orders_by_customer("CUST001")

    assert isinstance(orders, list)
    order_ids = sorted(order["order_id"] for order in orders)
    assert order_ids == ["ORD001", "ORD002"]


def test_list_orders_by_customer_with_status_applies_both_filters(
        order_tracker, mock_storage, mixed_customer_orders):
    """Tests that customer and status filters can be combined."""
    mock_storage.get_all_orders.return_value = mixed_customer_orders

    orders = order_tracker.list_orders_by_customer(
        "CUST001", status="pending"
    )

    assert [order["order_id"] for order in orders] == ["ORD001"]


def test_list_orders_by_customer_returns_empty_list_when_no_match(
        order_tracker, mock_storage, mixed_customer_orders):
    """Tests that a customer with no orders gets an empty list."""
    mock_storage.get_all_orders.return_value = mixed_customer_orders

    orders = order_tracker.list_orders_by_customer("CUST999")

    assert orders == []


def test_list_orders_by_customer_returns_empty_list_when_storage_empty(
        order_tracker, mock_storage):
    """Tests that filtering an empty store returns an empty list."""
    mock_storage.get_all_orders.return_value = {}

    orders = order_tracker.list_orders_by_customer("CUST001")

    assert orders == []
    mock_storage.get_all_orders.assert_called_once_with()


@pytest.mark.parametrize("bad_customer_id", ["", "   ", None, 7])
def test_list_orders_by_customer_rejects_invalid_customer_id(
        order_tracker, mock_storage, bad_customer_id):
    """Tests that an empty or non-string customer ID is rejected."""
    with pytest.raises(
        ValueError, match="Customer ID must be a non-empty string."
    ):
        order_tracker.list_orders_by_customer(bad_customer_id)

    mock_storage.get_all_orders.assert_not_called()


@pytest.mark.parametrize("bad_status", ["flying", ""])
def test_list_orders_by_customer_rejects_invalid_status(
        order_tracker, mock_storage, bad_status):
    """Tests that an invalid status is rejected before storage is read."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.list_orders_by_customer("CUST001", status=bad_status)

    mock_storage.get_all_orders.assert_not_called()
