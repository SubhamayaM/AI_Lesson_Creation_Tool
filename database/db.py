
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from config import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                lesson_json TEXT NOT NULL,
                research_json TEXT,
                factual_qc_json TEXT,
                instructional_qc_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        connection.commit()


def save_lesson(
    lesson,
    research=None,
    factual_report=None,
    instructional_report=None,
    lesson_id=None
):
    if not isinstance(lesson, dict):
        raise ValueError("Lesson must be a dictionary.")

    title = lesson.get("title", "Untitled Lesson")
    now = datetime.now().isoformat(timespec="seconds")

    lesson_json = json.dumps(lesson, ensure_ascii=False)
    research_json = json.dumps(research or {}, ensure_ascii=False)
    factual_json = json.dumps(factual_report or {}, ensure_ascii=False)
    instructional_json = json.dumps(
        instructional_report or {},
        ensure_ascii=False
    )

    with get_connection() as connection:
        if lesson_id is not None:
            existing = connection.execute(
                "SELECT id FROM lessons WHERE id = ?",
                (lesson_id,)
            ).fetchone()

            if existing:
                connection.execute("""
                    UPDATE lessons
                    SET title = ?,
                        lesson_json = ?,
                        research_json = ?,
                        factual_qc_json = ?,
                        instructional_qc_json = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    title,
                    lesson_json,
                    research_json,
                    factual_json,
                    instructional_json,
                    now,
                    lesson_id
                ))
                connection.commit()
                return lesson_id

        cursor = connection.execute("""
            INSERT INTO lessons (
                title,
                lesson_json,
                research_json,
                factual_qc_json,
                instructional_qc_json,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            title,
            lesson_json,
            research_json,
            factual_json,
            instructional_json,
            now,
            now
        ))

        connection.commit()
        return cursor.lastrowid


def get_lesson(lesson_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM lessons WHERE id = ?",
            (lesson_id,)
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["id"],
        "title": row["title"],
        "lesson": json.loads(row["lesson_json"]),
        "research": json.loads(row["research_json"] or "{}"),
        "factual_report": json.loads(row["factual_qc_json"] or "{}"),
        "instructional_report": json.loads(
            row["instructional_qc_json"] or "{}"
        ),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }


def list_lessons():
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, title, created_at, updated_at
            FROM lessons
            ORDER BY updated_at DESC
        """).fetchall()

    return [dict(row) for row in rows]


def delete_lesson(lesson_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM lessons WHERE id = ?",
            (lesson_id,)
        )
        connection.commit()
