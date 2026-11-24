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

## Reflection

* Design choice made: While analyzing the rubric for the course, I noticed a discrepancy when compared with the instructions. One states the put endpoint should be "api/orders/{order_id}" while the other references "api/orders/{order_id}/status". I made the decision to include both in this implementation.
* Something I learned through the testing from the TDD process is why the Red-Phase matters. When I wrote the test to make sure update_order_status does not change the original order in place, it passed against the empty stub before any code was written. A method that does nothing also changes nothing, so the test was not actually testing anything. I tightened it to also check that a separate copy was saved with the new status. After that it failed for the right reason in the Red-Phase, and it still protects against the in-place change in the Green-Phase.
* For future improvements on this project, I would add created_at and updated_at timestamp fields that log when the order was created and when it was updated. I would also add the "Delivered" status to the frontend's status options. Both of these could then be combined to create an archive functionality that could be used to hide any orders that have been delivered with an updated_at time of a certain period.
