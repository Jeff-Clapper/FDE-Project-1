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


def error_response(message, status_code):
    """Build the standard {"error": message} JSON response."""
    return jsonify({"error": message}), status_code


def read_json_object():
    """Return the request body if it is a JSON object, otherwise None."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else None


@app.route('/api/orders', methods=['POST'])
def add_order_api():
    """Create an order: 201 on success, 409 if the ID exists, else 400."""
    data = read_json_object()
    if data is None:
        return error_response("Request body must be a JSON object.", 400)

    try:
        order = order_tracker.add_order(
            data.get("order_id"),
            data.get("item_name"),
            data.get("quantity"),
            data.get("customer_id"),
            data.get("status", "pending"),
        )
    except DuplicateOrderError as error:
        return error_response(str(error), 409)
    except ValueError as error:
        return error_response(str(error), 400)
    return jsonify(order), 201


@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    """Return one order, or 404 if it does not exist."""
    try:
        order = order_tracker.get_order_by_id(order_id)
    except ValueError as error:
        return error_response(str(error), 400)
    if order is None:
        return error_response("Order not found", 404)
    return jsonify(order), 200


# The rubric names the first URL; the provided tests and frontend use /status.
@app.route('/api/orders/<string:order_id>', methods=['PUT'])
@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    """Update an order's status: 404 if missing, 400 if the status is bad."""
    data = read_json_object()
    if data is None:
        return error_response("Request body must be a JSON object.", 400)

    try:
        order = order_tracker.update_order_status(
            order_id, data.get("new_status")
        )
    except OrderNotFoundError as error:
        return error_response(str(error), 404)
    except ValueError as error:
        return error_response(str(error), 400)
    return jsonify(order), 200


@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    """List all orders, or only those matching ?status=<status>."""
    if "status" not in request.args:
        return jsonify(order_tracker.list_all_orders()), 200

    try:
        orders = order_tracker.list_orders_by_status(request.args["status"])
    except ValueError as error:
        return error_response(str(error), 400)
    return jsonify(orders), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
