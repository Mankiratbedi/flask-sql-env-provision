"""Tests for Milestone 2: Provision SQLite Database."""
import os
import sqlite3
import subprocess
import pytest


class TestMilestone2:
    """Verifies that the database schema is loaded, constraints are defined, and data is seeded correctly."""

    def test_database_exists(self):
        """Verify the database file was created at /app/run/assets.db."""
        db_path = "/app/run/assets.db"
        assert os.path.exists(db_path), f"Database file not found at {db_path}"

    def test_schema_applied_and_uniqueness(self):
        """Verify that the assets table exists and has a UNIQUE constraint on 'code'."""
        db_path = "/app/run/assets.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assets';")
        assert cursor.fetchone() is not None, "Table 'assets' was not created"
        
        # Verify UNIQUE constraint on code by attempting to insert duplicates
        try:
            cursor.execute("INSERT INTO assets (code, name, quantity) VALUES ('TEST01', 'Test A', 1);")
            cursor.execute("INSERT INTO assets (code, name, quantity) VALUES ('TEST01', 'Test B', 2);")
            conn.commit()
            pytest.fail("Database table is missing a UNIQUE constraint on the code column")
        except sqlite3.IntegrityError:
            pass
        finally:
            conn.close()

    def test_seeded_data(self):
        """Verify assets from assets.json were seeded, invalid records skipped, and duplicates handled."""
        db_path = "/app/run/assets.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM assets;")
        rows = cursor.fetchall()
        assets = {row["code"]: dict(row) for row in rows}
        conn.close()
        
        assert "AST001" in assets, "AST001 was not seeded"
        assert assets["AST001"]["quantity"] == 10, f"Expected AST001 quantity to be 10, got {assets['AST001']['quantity']}"
        
        assert "AST002" not in assets, "AST002 should have been skipped due to invalid quantity"
        
        assert "AST003" in assets, "AST003 was not seeded"
        assert assets["AST003"]["quantity"] == 5, f"Expected AST003 quantity to be 5, got {assets['AST003']['quantity']}"
        
        assert len(assets) == 2, f"Expected exactly 2 seeded assets in the database, found {len(assets)}"

    def test_db_init_idempotency(self):
        """Verify running db-init again is idempotent and does not crash or double-seed."""
        result = subprocess.run(
            ["/app/provision.py", "db-init"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"db-init command failed on second execution: {result.stderr}"
        
        db_path = "/app/run/assets.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM assets;")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 2, f"Seeded count is {count} instead of 2 after rerun. Idempotency failed."
