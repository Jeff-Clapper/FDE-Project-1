# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_api_errors.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

## API Reference

Start the server from the project root with `python -m backend.app`. The base URL is `http://127.0.0.1:5000`.

Request and response bodies are JSON. Every error response has the same shape:

```json
{"error": "message"}
```

| Status | Meaning |
|---|---|
| 200 OK | Order(s) returned or updated |
| 201 Created | Order created |
| 204 No Content | Order deleted |
| 400 Bad Request | Invalid input (missing field, bad quantity, invalid status, body is not a JSON object) |
| 404 Not Found | No order with that ID |
| 409 Conflict | An order with that ID already exists |

Valid statuses: `pending`, `processing`, `shipped`, `delivered`, `cancelled`.

> The examples use `curl` (macOS, Linux, Git Bash). In Windows PowerShell, type `curl.exe` instead of `curl` and put the whole command on one line, since PowerShell does not use `\` to continue a line.

### Create an order

`POST /api/orders`

`order_id`, `item_name` and `customer_id` must be non-empty strings, and `quantity` must be a positive integer. `status` is optional and defaults to `pending`.

```bash
curl -X POST http://127.0.0.1:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"order_id": "ORD001", "item_name": "Laptop", "quantity": 1, "customer_id": "CUST001"}'
```

Response `201`:

```json
{"customer_id": "CUST001", "item_name": "Laptop", "order_id": "ORD001", "quantity": 1, "status": "pending"}
```

Errors: `400` for invalid input, `409` if the ID already exists.

### Get an order

`GET /api/orders/<order_id>`

```bash
curl http://127.0.0.1:5000/api/orders/ORD001
```

Response `200`: the order. Errors: `404` with `{"error": "Order not found"}`.

### Update an order's status

`PUT /api/orders/<order_id>` (also available as `PUT /api/orders/<order_id>/status`)

```bash
curl -X PUT http://127.0.0.1:5000/api/orders/ORD001 \
  -H "Content-Type: application/json" \
  -d '{"new_status": "shipped"}'
```

Response `200`: the updated order. Errors: `400` for a missing or invalid `new_status`, `404` if the order does not exist.

### Delete an order

`DELETE /api/orders/<order_id>`

```bash
curl -i -X DELETE http://127.0.0.1:5000/api/orders/ORD001
```

Response `204` with an empty body. Errors: `404` if the order does not exist.

### List and filter orders

`GET /api/orders`

| Query | Returns |
|---|---|
| (none) | Every order |
| `?status=<status>` | Orders with that status |
| `?customer_id=<id>` | Orders for that customer |
| `?customer_id=<id>&status=<status>` | Orders for that customer with that status |

```bash
curl http://127.0.0.1:5000/api/orders
curl "http://127.0.0.1:5000/api/orders?status=shipped"
curl "http://127.0.0.1:5000/api/orders?customer_id=CUST001&status=pending"
```

Response `200`: a JSON list, `[]` if nothing matches. Errors: `400` for an empty or invalid `status`, or an empty `customer_id`.

## Reflection

* Design choice made: While analyzing the rubric for the course, I noticed a discrepancy when compared with the instructions. One states the put endpoint should be "api/orders/{order_id}" while the other references "api/orders/{order_id}/status". I made the decision to include both in this implementation.
* Something I learned through the testing from the TDD process is why the Red-Phase matters. When I wrote the test to make sure update_order_status does not change the original order in place, it passed against the empty stub before any code was written. A method that does nothing also changes nothing, so the test was not actually testing anything. I tightened it to also check that a separate copy was saved with the new status. After that it failed for the right reason in the Red-Phase, and it still protects against the in-place change in the Green-Phase.
* For future improvements on this project, I would add created_at and updated_at timestamp fields that log when the order was created and when it was updated. I would also add the "Delivered" status to the frontend's status options. Both of these could then be combined to create an archive functionality that could be used to hide any orders that have been delivered with an updated_at time of a certain period.
