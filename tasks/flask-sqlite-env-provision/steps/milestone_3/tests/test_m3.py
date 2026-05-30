"""Tests for Milestone 3: Configure Flask Service and Verify."""
import os
import subprocess


class TestMilestone3:
    """Verifies service configurations, background status, logs, PID, and health checks."""

    def test_secret_key_security(self):
        """Verify the SECRET_KEY is cryptographically secure and meets size requirements."""
        config_path = "/app/run/config.py"
        assert os.path.exists(config_path), "config.py is missing"
        
        cfg = {}
        with open(config_path) as f:
            exec(f.read(), cfg)
            
        secret_key = cfg.get("SECRET_KEY", "")
        assert len(secret_key) >= 32, f"SECRET_KEY is too short: {len(secret_key)} characters (must be >= 32)"
        assert not secret_key.startswith("key_0."), "SECRET_KEY is using a weak random generation method"

    def test_process_running_in_background(self):
        """Verify Flask runs in the background and its PID is stored correctly."""
        pid_path = "/app/run/flask.pid"
        assert os.path.exists(pid_path), "flask.pid file not found"
        
        with open(pid_path) as f:
            pid_str = f.read().strip()
            
        assert pid_str.isdigit(), f"PID file contains non-numeric value: {pid_str}"
        pid = int(pid_str)
        
        assert os.path.exists(f"/proc/{pid}"), f"No running process found with PID {pid}"
        
        with open(f"/proc/{pid}/cmdline") as f:
            cmdline = f.read()
            assert "python" in cmdline.lower() or "flask" in cmdline.lower(), \
                f"Process with PID {pid} is not a Python/Flask process: {cmdline}"

    def test_logs_created(self):
        """Verify that service logs are written to /app/run/logs/flask.log."""
        log_path = "/app/run/logs/flask.log"
        assert os.path.exists(log_path), "flask.log file not found"
        assert os.path.getsize(log_path) > 0, "flask.log is empty"

    def test_cli_check_command(self):
        """Verify that provision.py check command successfully verifies the running service."""
        result = subprocess.run(
            ["/app/provision.py", "check", "--port", "5000"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"check command failed: stdout: {result.stdout}, stderr: {result.stderr}"
        assert "Service health check: PASS" in result.stdout
        assert "Authentication: SUCCESS" in result.stdout
