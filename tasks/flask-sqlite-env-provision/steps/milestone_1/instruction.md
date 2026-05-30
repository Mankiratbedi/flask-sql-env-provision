# Milestone 1: Bootstrap App Environment

We need to configure the local service environment for our Flask and SQLite asset-management API. 

Your task is to fix the `bootstrap` command of the provisioning tool at `/app/provision.py` so that it:
1. Creates the directory layout at `/app/run/` and `/app/run/logs/`.
2. Initializes a python virtual environment at `/app/run/venv/` and installs the required libraries from `/app/api/requirements.txt`. Note that the container runs offline (internet access is disabled), so all dependencies must be resolved locally from the pre-cached packages inside `/opt/wheels/`.
3. Parses the configuration template `/app/api/config.py.template` and renders it to `/app/run/config.py`, substituting the appropriate template placeholders:
   - `SECRET_KEY`: Generate a random key.
   - `DATABASE`: Set to the absolute path `/app/run/assets.db`.

Ensure you verify that the template substitutions run correctly and write absolute paths to all target files.
