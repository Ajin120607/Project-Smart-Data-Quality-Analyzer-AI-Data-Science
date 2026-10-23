"""In-memory session and temporary artifact storage with TTL expiration."""

import time
import threading
from typing import Any, Dict, Optional
import pandas as pd
from app.utils.security import generate_secure_id

TTL_SECONDS = 3600  # 1 hour expiration for temporary artifacts


class SessionStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._reports: Dict[str, Dict[str, Any]] = {}
        self._downloads: Dict[str, Dict[str, Any]] = {}

    def _cleanup_expired(self):
        """Removes expired sessions, reports, and downloads."""
        now = time.time()
        for d in [self._sessions, self._reports, self._downloads]:
            expired_keys = [k for k, v in d.items() if now - v["created_at"] > TTL_SECONDS]
            for k in expired_keys:
                del d[k]

    def store_dataset(self, df: pd.DataFrame, file_name: str) -> str:
        """Stores parsed DataFrame in temporary session and returns secure session_id."""
        with self._lock:
            self._cleanup_expired()
            session_id = generate_secure_id()
            self._sessions[session_id] = {
                "created_at": time.time(),
                "df": df.copy(),
                "file_name": file_name,
            }
            return session_id

    def get_dataset(self, session_id: str) -> Optional[pd.DataFrame]:
        """Retrieves DataFrame by session_id."""
        with self._lock:
            self._cleanup_expired()
            entry = self._sessions.get(session_id)
            if entry:
                return entry["df"].copy()
            return None

    def store_report(self, report_id: str, session_id: str, report_data: Dict[str, Any]):
        """Stores generated quality report."""
        with self._lock:
            self._cleanup_expired()
            self._reports[report_id] = {
                "created_at": time.time(),
                "session_id": session_id,
                "data": report_data,
            }

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves quality report by report_id."""
        with self._lock:
            self._cleanup_expired()
            entry = self._reports.get(report_id)
            if entry:
                return entry["data"]
            return None

    def store_download(self, csv_bytes: bytes, file_name: str) -> str:
        """Stores cleaned CSV bytes ready for download, returning secure file_id."""
        with self._lock:
            self._cleanup_expired()
            file_id = generate_secure_id()
            self._downloads[file_id] = {
                "created_at": time.time(),
                "content": csv_bytes,
                "file_name": file_name,
            }
            return file_id

    def get_download(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves downloadable content by file_id."""
        with self._lock:
            self._cleanup_expired()
            return self._downloads.get(file_id)


# Global singleton store
session_store = SessionStore()
