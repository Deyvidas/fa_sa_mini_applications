### Tests execution order:

---

- `0.XXX` Testing schemas (test pydantic models):
    - `0.001 tests/test_status/test_schemas.py::TestStatusField`
    - `0.002 tests/test_status/test_schemas.py::TestDescriptionField`

- `1.XXX` Testing managers:
    - `1.001 tests/test_status/test_managers.py::TestManager`

- `2.XXX` Testing endpoints:
    - `2.001 tests/test_status/test_endpoints.py::TestGET`