# Milestone 3: Configure Flask Service and Verify

We need to complete the service configuration, run it securely in the background, and verify health and authentication.

Your tasks are:
1. Improve config generation in the `bootstrap` command to use a cryptographically secure `SECRET_KEY` (using Python's `secrets` module, at least 32 characters long).
2. Fix the background service management in the `start` command. The service must write stdout/stderr logs to `/app/run/logs/flask.log` and save its process ID (PID) to `/app/run/flask.pid`.
3. Fix the `check` command to perform robust verification:
   - Poll the `/health` endpoint. Since Flask may take a moment to start up and bind, implement a retry loop (attempting up to 5 times with a 1-second delay) rather than failing on immediate connection errors.
   - Verify the admin token generation endpoint by POSTing the correct credentials (`username = "admin"` and `password = "secret-provision-password"`) to the `/api/token` endpoint. 

Ensure all paths are absolute and the service is verified properly.
