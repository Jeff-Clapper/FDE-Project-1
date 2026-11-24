import pytest
from backend.app import app, in_memory_storage

VALID_ORDER = {
    "order_id": "ERR001",
    "item_name": "Keyboard",
    "quantity": 1,
    "customer_id": "C1",
}


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client


# --- POST /api/orders ---


def test_add_order_api_returns_full_order_with_default_status(client):
    response = client.post('/api/orders', json=VALID_ORDER)
    assert response.status_code == 201
    assert response.json == {**VALID_ORDER, "status": "pending"}


def test_add_order_api_duplicate_returns_409(client):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.post('/api/orders', json=VALID_ORDER)
    assert response.status_code == 409
    assert response.json == {
        "error": "Order with ID 'ERR001' already exists."
    }


@pytest.mark.parametrize(
    "missing_field", ["order_id", "item_name", "quantity", "customer_id"]
)
def test_add_order_api_missing_field_returns_400(client, missing_field):
    order_data = {
        k: v for k, v in VALID_ORDER.items() if k != missing_field
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 400
    assert "error" in response.json


def test_add_order_api_invalid_quantity_returns_400(client):
    response = client.post('/api/orders', json={**VALID_ORDER, "quantity": 0})
    assert response.status_code == 400
    assert response.json == {"error": "Quantity must be a positive integer."}


def test_add_order_api_invalid_status_returns_400(client):
    response = client.post(
        '/api/orders', json={**VALID_ORDER, "status": "flying"}
    )
    assert response.status_code == 400
    assert "error" in response.json


@pytest.mark.parametrize("body", ["not json", "[1, 2, 3]"])
def test_add_order_api_non_object_body_returns_400(client, body):
    response = client.post(
        '/api/orders', data=body, content_type='application/json'
    )
    assert response.status_code == 400
    assert "error" in response.json


# --- GET /api/orders/<order_id> ---


def test_get_order_api_not_found_returns_error_message(client):
    response = client.get('/api/orders/NONEXISTENT')
    assert response.status_code == 404
    assert response.json == {"error": "Order not found"}


# --- PUT /api/orders/<order_id> and /api/orders/<order_id>/status ---


@pytest.mark.parametrize(
    "url", ['/api/orders/ERR001', '/api/orders/ERR001/status']
)
def test_update_order_api_success_on_both_routes(client, url):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.put(url, json={"new_status": "shipped"})
    assert response.status_code == 200
    assert response.json == {**VALID_ORDER, "status": "shipped"}


def test_update_order_api_invalid_status_returns_400(client):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.put(
        '/api/orders/ERR001/status', json={"new_status": "flying"}
    )
    assert response.status_code == 400
    assert "error" in response.json


def test_update_order_api_missing_new_status_returns_400(client):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.put('/api/orders/ERR001/status', json={})
    assert response.status_code == 400
    assert "error" in response.json


def test_update_order_api_missing_order_returns_404(client):
    response = client.put(
        '/api/orders/NONEXISTENT/status', json={"new_status": "shipped"}
    )
    assert response.status_code == 404
    assert response.json == {
        "error": "Order with ID 'NONEXISTENT' does not exist."
    }


# --- GET /api/orders and GET /api/orders?status=<status> ---


def test_list_orders_api_empty_returns_empty_list(client):
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert response.json == []


def test_list_orders_api_filter_with_no_match_returns_empty_list(client):
    client.post('/api/orders', json=VALID_ORDER)
    response = client.get('/api/orders?status=delivered')
    assert response.status_code == 200
    assert response.json == []


@pytest.mark.parametrize("query", ['?status=flying', '?status='])
def test_list_orders_api_invalid_status_filter_returns_400(client, query):
    response = client.get(f'/api/orders{query}')
    assert response.status_code == 400
    assert "error" in response.json
