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

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

def test_add_order_saves_order_details_with_default_status(order_tracker, mock_storage):
    """Tests that the stored order contains every field and defaults to 'pending'."""
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
    order_tracker.add_order("ORD002", "Mouse", 2, "CUST002", status="processing")

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
def test_add_order_rejects_invalid_order_id(order_tracker, mock_storage, bad_order_id):
    """Tests that order_id must be a non-empty string."""
    with pytest.raises(ValueError, match="Order ID must be a non-empty string."):
        order_tracker.add_order(bad_order_id, "Laptop", 1, "CUST001")

    mock_storage.save_order.assert_not_called()

@pytest.mark.parametrize("bad_item_name", ["", "   ", None, 42])
def test_add_order_rejects_invalid_item_name(order_tracker, mock_storage, bad_item_name):
    """Tests that item_name must be a non-empty string."""
    with pytest.raises(ValueError, match="Item name must be a non-empty string."):
        order_tracker.add_order("ORD001", bad_item_name, 1, "CUST001")

    mock_storage.save_order.assert_not_called()

@pytest.mark.parametrize("bad_customer_id", ["", "   ", None, 7])
def test_add_order_rejects_invalid_customer_id(order_tracker, mock_storage, bad_customer_id):
    """Tests that customer_id must be a non-empty string."""
    with pytest.raises(ValueError, match="Customer ID must be a non-empty string."):
        order_tracker.add_order("ORD001", "Laptop", 1, bad_customer_id)

    mock_storage.save_order.assert_not_called()

@pytest.mark.parametrize("bad_quantity", [0, -1, 1.5, "1", None, True])
def test_add_order_rejects_invalid_quantity(order_tracker, mock_storage, bad_quantity):
    """Tests that quantity must be a positive integer (booleans are not accepted)."""
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD001", "Laptop", bad_quantity, "CUST001")

    mock_storage.save_order.assert_not_called()

@pytest.mark.parametrize("bad_status", ["flying", "", "Pending", None])
def test_add_order_rejects_invalid_status(order_tracker, mock_storage, bad_status):
    """Tests that only the allowed statuses can be used when creating an order."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.add_order("ORD001", "Laptop", 1, "CUST001", status=bad_status)

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
def test_get_order_rejects_invalid_id(order_tracker, mock_storage, bad_order_id):
    """Tests that an empty or non-string ID is rejected without reading storage."""
    with pytest.raises(ValueError, match="Order ID must be a non-empty string."):
        order_tracker.get_order_by_id(bad_order_id)

    mock_storage.get_order.assert_not_called()
