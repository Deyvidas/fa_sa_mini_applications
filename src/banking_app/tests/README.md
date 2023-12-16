### Tests execution order:

---

- `0.XX_XX` Testing schemas (test pydantic models):
    - `0.00_00 tests/test_status/test_schemas.py::TestStatusField`
    - `0.00_01 tests/test_status/test_schemas.py::TestDescriptionField`
    - `0.00_02 tests/test_status/test_schemas.py::TestSideModels`

    - `0.01_00 tests/test_client/test_schemas.py::TestClientIdField`
    - `0.01_01 tests/test_client/test_schemas.py::TestFullNameField`
    - `0.01_02 tests/test_client/test_schemas.py::TestBirthDateField`
    - `0.01_03 tests/test_client/test_schemas.py::TestSexField`
    - `0.01_04 tests/test_client/test_schemas.py::TestPhoneField`
    - `0.01_05 tests/test_client/test_schemas.py::TestDocNumField`
    - `0.01_06 tests/test_client/test_schemas.py::TestDocSeriesField`
    - `0.01_07 tests/test_client/test_schemas.py::TestRegDateField`
    - `0.01_08 tests/test_client/test_schemas.py::TestVipFlagField`
    - `0.01_09 tests/test_client/test_schemas.py::TestSideModels`

- `1.XX_XX` Testing managers:
    - `1.00_00 tests/test_status/test_managers.py::TestCreate`
    - `1.00_01 tests/test_status/test_managers.py::TestBulkCreate`
    - `1.00_02 tests/test_status/test_managers.py::TestFilter`
    - `1.00_03 tests/test_status/test_managers.py::TestUpdate`

- `2.XX_XX` Testing endpoints:
    - `2.00_00 tests/test_status/test_endpoints.py::TestRetrieve`
    - `2.00_01 tests/test_status/test_endpoints.py::TestPost`
    - `2.00_02 tests/test_status/test_endpoints.py::TestUpdate`
    - `2.00_03 tests/test_status/test_endpoints.py::TestDelete`