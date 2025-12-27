from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional, List

from ..core.models import Job

DEFAULT_DB = Path("data/jobs.sqlite3")


class JobStore:
    def __init__(self, db_path: Path = DEFAULT_DB):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._conn() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    json TEXT NOT NULL
                )"""
            )
            conn.commit()

    def put(self, job: Job) -> None:
        with self._conn() as conn:
            conn.execute("INSERT OR REPLACE INTO jobs(id,json) VALUES(?,?)", (job.id, job.model_dump_json()))
            conn.commit()

    def get(self, job_id: str) -> Optional[Job]:
        with self._conn() as conn:
            row = conn.execute("SELECT json FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row:
                return None
            return Job.model_validate_json(row[0])

    def list(self, limit: int = 50) -> List[Job]:
        with self._conn() as conn:
            rows = conn.execute("SELECT json FROM jobs LIMIT ?", (limit,)).fetchall()
            return [Job.model_validate_json(r[0]) for r in rows]
