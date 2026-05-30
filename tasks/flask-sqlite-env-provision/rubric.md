# Rubrics for flask-sqlite-env-provision Task

This file defines the binary, objective rubric criteria for the Flask & SQLite service provisioning milestone task.

## Milestone 1: Bootstrap App Environment

#Rubric 1
Agent inspects the template files and directory layout under /app/api/ before bootstrapping, +2
Agent configures pip install in /app/provision.py to run offline using --no-index and --find-links=/opt/wheels/, +3
Agent renders /app/run/config.py substituting the correct absolute path to the SQLite database, +3
Agent creates required runtime directories at /app/run/ and /app/run/logs/, +2
Agent allows pip to attempt downloading packages over the internet causing a connection failure, -3
Agent hardcodes configuration parameters instead of parsing /app/api/config.py.template, -3
Agent writes virtual environment or configurations outside the /app/run/ target path, -2

#Rubric 1 — checks = 7 · positives = 10 · negatives = 3 · no 4s ok

---

## Milestone 2: Provision SQLite Database

#Rubric 2
Agent repairs the syntax error in /app/api/schema.sql by adding the missing comma, +3
Agent adds a UNIQUE constraint to the code column in the SQLite assets schema, +3
Agent validates and filters inputs from /app/api/assets.json, skipping non-integer quantities, +2
Agent handles duplicate records or SQLite constraints gracefully to ensure db-init is idempotent, +3
Agent fails to define the UNIQUE constraint on the asset code column, -3
Agent allows duplicate asset records to be seeded into the database, -3
Agent does not validate quantities resulting in database insertion failures in the trace, -2

#Rubric 2 — checks = 7 · positives = 11 · negatives = 3 · no 4s ok

---

## Milestone 3: Configure Flask Service and Verify

#Rubric 3
Agent replaces the weak secret key generation with a cryptographically secure token using secrets module, +3
Agent configures Flask to log to /app/run/logs/flask.log and saves its PID to /app/run/flask.pid, +3
Agent implements a retry loop with delay backoff in the health check command to wait for Flask to bind, +3
Agent configures check credentials payload to use username admin and password secret-provision-password, +2
Agent leaves the weak random-based SECRET_KEY generation active, -3
Agent fails to save the Flask service process ID to /app/run/flask.pid, -3
Agent keeps the hardcoded wrong password in the check verification command, -3

#Rubric 3 — checks = 7 · positives = 11 · negatives = 3 · no 4s ok
