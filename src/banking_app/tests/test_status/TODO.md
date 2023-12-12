### Testing:

- [x] Test endpoint GET /status/list (get_all_statuses).
- [x] Test endpoint GET /status/{status_num} (get_status_with_status_number).
- [x] Test endpoint POST /status (add_status).
- [x] Test endpoint DELETE /status/{status_num} (delete_status_with_status_number).
- [x] Test method update of StatusManager.
- [x] Test endpoint PUT /status/{status_num} (full_update_status_with_status_number).
- [x] Test endpoint PATCH /status/{status_num} (partial_update_status_with_status_number).

---

### Endpoints:

- [x] Add endpoint for update existent status, ONLY status description.
    - because if assign one status number to more than one status,
      IntegrityError exception will happen (status is unique field).
- [ ] Add endpoint for create more than one status in one request.

---

### Manager:

- [x] Declare update method in StatusManager. (don't need, I inherit this method
      from UpdateManager).
