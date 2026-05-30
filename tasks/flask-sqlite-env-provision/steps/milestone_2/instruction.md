# Milestone 2: Provision SQLite Database

We need to initialize the SQLite database and seed it with validation records.

Your tasks are:
1. Fix the SQL syntax error in `/app/api/schema.sql`. You must also add a `UNIQUE` constraint to the `code` column in the `assets` table.
2. Repair the `db-init` command of `/app/provision.py` so that it:
   - Initializes `/app/run/assets.db` using the schema script.
   - Loads initial asset data from `/app/api/assets.json` and seeds it into the database.
   - Validates the `quantity` of each asset record: if it is not a valid integer (or cannot be converted to one), skip that asset.
   - Ensures **idempotency**: running `db-init` multiple times should not throw errors or insert duplicate records (i.e. handle `sqlite3.IntegrityError` and table/index creation gracefully).

Ensure you only modify the necessary database and script files, using absolute paths throughout.
