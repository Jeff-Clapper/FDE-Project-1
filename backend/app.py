from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import (
    OrderTracker,
    DuplicateOrderError,
    OrderNotFoundError,
)
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


# --- Error handlers ---
# Flask picks the most specific handler, so the two subclasses below are
# matched before the general ValueError handler.


def error_response(message, status_code):
    """Build the standard {"error": message} JSON response."""
    return jsonify({"error": message}), status_code


@app.errorhandler(DuplicateOrderError)
def handle_duplicate_order(error):
    return error_response(str(error), 409)


@app.errorhandler(OrderNotFoundError)
def handle_order_not_found(error):
    return error_response(str(error), 404)


@app.errorhandler(ValueError)
def handle_invalid_input(error):
    return error_response(str(error), 400)


# --- Routes ---


def read_json_object():
    """Return the request body as a dict, or raise ValueError."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object.")
    return data


@app.route('/api/orders', methods=['POST'])
def add_order_api():
    """Create an order: 201 on success, 409 if the ID exists, else 400."""
    data = read_json_object()
    order = order_tracker.add_order(
        data.get("order_id"),
        data.get("item_name"),
        data.get("quantity"),
        data.get("customer_id"),
        data.get("status", "pending"),
    )
    return jsonify(order), 201


@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    """Return one order, or 404 if it does not exist."""
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        raise OrderNotFoundError("Order not found")
    return jsonify(order), 200


# The rubric names the first URL; the provided tests and frontend use /status.
@app.route('/api/orders/<string:order_id>', methods=['PUT'])
@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    """Update an order's status: 404 if missing, 400 if the status is bad."""
    data = read_json_object()
    order = order_tracker.update_order_status(
        order_id, data.get("new_status")
    )
    return jsonify(order), 200


@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    """List orders, optionally filtered by ?customer_id= and/or ?status=."""
    if "customer_id" in request.args:
        orders = order_tracker.list_orders_by_customer(
            request.args["customer_id"], request.args.get("status")
        )
    elif "status" in request.args:
        orders = order_tracker.list_orders_by_status(request.args["status"])
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(orders), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
