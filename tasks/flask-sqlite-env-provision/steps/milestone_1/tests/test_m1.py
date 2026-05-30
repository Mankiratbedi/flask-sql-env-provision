"""Tests for Milestone 1: Bootstrap App Environment."""
import os
import subprocess


class TestMilestone1:
    """Verifies that the bootstrap step sets up the directories, config, and virtualenv."""

    def test_run_directory_layout(self):
        """Verify that the required runtime directories were created under /app/run."""
        assert os.path.isdir("/app/run"), "Directory /app/run does not exist"
        assert os.path.isdir("/app/run/logs"), "Directory /app/run/logs does not exist"

    def test_config_file_generation(self):
        """Verify config.py exists and rendered correct secret key and DB path placeholders."""
        config_path = "/app/run/config.py"
        assert os.path.exists(config_path), "Configuration file was not rendered at /app/run/config.py"
        
        cfg = {}
        with open(config_path) as f:
            exec(f.read(), cfg)
            
        assert "SECRET_KEY" in cfg, "SECRET_KEY variable is missing in config.py"
        assert "DATABASE" in cfg, "DATABASE variable is missing in config.py"
        assert cfg["DATABASE"] == "/app/run/assets.db", "DATABASE path in config.py is incorrect"

    def test_virtual_environment(self):
        """Verify virtualenv exists under /app/run/venv and has python interpreter executable."""
        venv_python = "/app/run/venv/bin/python"
        assert os.path.exists(venv_python), "Virtualenv Python interpreter not found at /app/run/venv/bin/python"
        assert os.access(venv_python, os.X_OK), "Virtualenv Python interpreter is not executable"

    def test_dependencies_installed(self):
        """Verify Flask can be imported using the virtual environment interpreter."""
        venv_python = "/app/run/venv/bin/python"
        result = subprocess.run(
            [venv_python, "-c", "import flask; print(flask.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Flask is not successfully installed in the venv: {result.stderr}"
