"""Tests for `DatabaseManager._apply_migrations`.

We construct a pre-migration ("old") sqlite file that lacks the
`was_skipped` column on `questions_answered`, then open it via
`DatabaseManager(db_path=...)` and confirm:

- Migration ran (column exists).
- Existing rows default to `was_skipped = 0`.
- No rows were lost.
- Re-opening the DB doesn't error or duplicate columns
  (idempotency).
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.database.db_manager import DatabaseManager


# Pre-migration schema. Note: no `was_skipped` column on
# `questions_answered`. We also purposefully omit the schema for
# tables that aren't on the migration path — `initialize_db` will fill
# them in as needed.
OLD_SCHEMA = """
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    mode_type TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    duration_seconds INTEGER,
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    avg_time_per_question REAL NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE questions_answered (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_type TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    user_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    time_taken_seconds REAL NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
"""


def _build_old_db(path: str):
    """Hand-build an old-schema database and seed a session + questions."""
    conn = sqlite3.connect(path)
    conn.executescript(OLD_SCHEMA)

    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO sessions
            (timestamp, mode_type, category, difficulty,
             duration_seconds, total_questions, correct_answers,
             total_score, avg_time_per_question, completed)
        VALUES (?, 'marathon', 'arithmetic', 'easy',
                60, 3, 2, 100, 4.0, 1)
        """,
        (datetime.now(),),
    )
    sid = cursor.lastrowid

    for i, (correct, answer) in enumerate([(1, "4"), (1, "5"), (0, "wrong")]):
        cursor.execute(
            """
            INSERT INTO questions_answered
                (session_id, question_type, difficulty, question_text,
                 correct_answer, user_answer, is_correct,
                 time_taken_seconds, timestamp)
            VALUES (?, 'addition', 'easy', '2+2', '4', ?, ?, ?, ?)
            """,
            (sid, answer, correct, 4.0 + i, datetime.now()),
        )
    conn.commit()
    conn.close()
    return sid


@pytest.fixture
def old_db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Migration applies new column with default 0.
# ---------------------------------------------------------------------------


class TestMigration:

    def test_was_skipped_column_added(self, old_db_path):
        sid = _build_old_db(old_db_path)
        # Open via DatabaseManager — triggers `_apply_migrations`.
        db = DatabaseManager(old_db_path)

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(questions_answered)")
        cols = {row["name"] for row in cursor.fetchall()}
        conn.close()

        assert "was_skipped" in cols

    def test_existing_rows_default_to_zero(self, old_db_path):
        _build_old_db(old_db_path)
        db = DatabaseManager(old_db_path)

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT was_skipped FROM questions_answered")
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 3
        assert all(row["was_skipped"] == 0 for row in rows)

    def test_no_data_lost(self, old_db_path):
        _build_old_db(old_db_path)
        db = DatabaseManager(old_db_path)

        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_answer, is_correct FROM questions_answered ORDER BY id"
        )
        rows = cursor.fetchall()
        cursor.execute("SELECT total_questions, correct_answers FROM sessions")
        session = cursor.fetchone()
        conn.close()

        assert [r["user_answer"] for r in rows] == ["4", "5", "wrong"]
        assert [r["is_correct"] for r in rows] == [1, 1, 0]
        assert session["total_questions"] == 3
        assert session["correct_answers"] == 2


# ---------------------------------------------------------------------------
# Idempotency.
# ---------------------------------------------------------------------------


class TestIdempotency:

    def test_reopening_does_not_error(self, old_db_path):
        _build_old_db(old_db_path)
        # First open — applies the migration.
        DatabaseManager(old_db_path)
        # Second open — must not raise "duplicate column".
        DatabaseManager(old_db_path)

    def test_no_duplicate_columns(self, old_db_path):
        _build_old_db(old_db_path)
        DatabaseManager(old_db_path)
        DatabaseManager(old_db_path)
        # Sanity: only one was_skipped column.
        conn = sqlite3.connect(old_db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(questions_answered)")
        was_skipped_count = sum(1 for row in cursor.fetchall() if row[1] == "was_skipped")
        conn.close()
        assert was_skipped_count == 1


# ---------------------------------------------------------------------------
# Fresh-install path also yields the column.
# ---------------------------------------------------------------------------


class TestFreshInstall:

    def test_new_db_has_was_skipped(self, tmp_path):
        path = str(tmp_path / "new.db")
        db = DatabaseManager(path)
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(questions_answered)")
        cols = {row["name"] for row in cursor.fetchall()}
        conn.close()
        assert "was_skipped" in cols
