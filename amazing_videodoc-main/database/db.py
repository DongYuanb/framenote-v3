"""Lightweight SQLite helpers for persisting payment orders and membership data."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from settings import get_settings

_INITIALIZED = False


def _get_db_path() -> Path:
    settings = get_settings()
    url = settings.DATABASE_URL
    if not url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported for local persistence")
    raw_path = url.removeprefix("sqlite:///")
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def init_db() -> None:
    """Create required tables if they do not exist."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                membership_level TEXT NOT NULL DEFAULT 'free',
                membership_expires_at TEXT,
                auto_renew INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_orders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                order_no TEXT NOT NULL UNIQUE,
                plan TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                payment_provider TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                status TEXT NOT NULL,
                provider_order_id TEXT,
                provider_trade_no TEXT,
                paid_at TEXT,
                expires_at TEXT NOT NULL,
                metadata TEXT,
                auto_renew INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )

        conn.execute(
            """CREATE INDEX IF NOT EXISTS idx_payment_orders_user_id ON payment_orders(user_id)"""
        )
        conn.execute(
            """CREATE INDEX IF NOT EXISTS idx_payment_orders_status ON payment_orders(status)"""
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sms_codes (
                phone TEXT NOT NULL,
                action TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                used_at TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (phone, action)
            )
            """
        )

        # 记录用户每日已使用的处理时长（秒）
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_daily_usage (
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                seconds_used INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (user_id, date)
            )
            """
        )

        conn.execute(
            """CREATE INDEX IF NOT EXISTS idx_sms_codes_expires_at ON sms_codes(expires_at)"""
        )

        conn.commit()
    finally:
        conn.close()

    _INITIALIZED = True


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    """Yield a SQLite connection with row factory enabled."""
    db_path = _get_db_path()
    conn = sqlite3.connect(
        db_path,
        detect_types=sqlite3.PARSE_DECLTYPES,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def current_timestamp() -> str:
    """Utility returning current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def save_sms_code(phone: str, action: str, code_hash: str, expires_at: str) -> None:
    now = current_timestamp()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO sms_codes (phone, action, code_hash, expires_at, used, used_at, attempts, created_at, updated_at)
            VALUES (?, ?, ?, ?, 0, NULL, 0, ?, ?)
            ON CONFLICT(phone, action) DO UPDATE SET
                code_hash=excluded.code_hash,
                expires_at=excluded.expires_at,
                used=0,
                used_at=NULL,
                attempts=0,
                updated_at=excluded.updated_at
            """,
            (phone, action, code_hash, expires_at, now, now),
        )


def get_sms_code(phone: str, action: str) -> Optional[sqlite3.Row]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sms_codes WHERE phone = ? AND action = ?",
            (phone, action),
        ).fetchone()
    return row


def mark_sms_code_used(phone: str, action: str) -> None:
    now = current_timestamp()
    with get_db() as conn:
        conn.execute(
            """
            UPDATE sms_codes
            SET used = 1,
                used_at = ?,
                updated_at = ?
            WHERE phone = ? AND action = ?
            """,
            (now, now, phone, action),
        )


def increment_sms_attempts(phone: str, action: str) -> int:
    now = current_timestamp()
    with get_db() as conn:
        conn.execute(
            """
            UPDATE sms_codes
            SET attempts = attempts + 1,
                updated_at = ?
            WHERE phone = ? AND action = ?
            """,
            (now, phone, action),
        )
        row = conn.execute(
            "SELECT attempts FROM sms_codes WHERE phone = ? AND action = ?",
            (phone, action),
        ).fetchone()
    return row["attempts"] if row else 0


def delete_sms_code(phone: str, action: str) -> None:
    with get_db() as conn:
        conn.execute(
            "DELETE FROM sms_codes WHERE phone = ? AND action = ?",
            (phone, action),
        )


def purge_expired_sms_codes(reference_time: Optional[str] = None) -> None:
    if reference_time is None:
        reference_time = current_timestamp()
    with get_db() as conn:
        conn.execute(
            "DELETE FROM sms_codes WHERE expires_at < ? OR (used = 1 AND used_at < ?)",
            (reference_time, reference_time),
        )


def add_usage_seconds(user_id: str, seconds: int) -> int:
    """为当日累加使用秒数并返回最新数值。"""
    today = datetime.utcnow().date().isoformat()
    now = current_timestamp()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO user_daily_usage (user_id, date, seconds_used, updated_at)
            VALUES (?, ?, 0, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                seconds_used = user_daily_usage.seconds_used + excluded.seconds_used,
                updated_at = excluded.updated_at
            """,
            (user_id, today, now),
        )
        conn.execute(
            "UPDATE user_daily_usage SET seconds_used = seconds_used + ? , updated_at = ? WHERE user_id = ? AND date = ?",
            (seconds, now, user_id, today),
        )
        row = conn.execute(
            "SELECT seconds_used FROM user_daily_usage WHERE user_id = ? AND date = ?",
            (user_id, today),
        ).fetchone()
    return int(row["seconds_used"]) if row else 0


def get_usage_seconds(user_id: str, date_iso: Optional[str] = None) -> int:
    date_iso = date_iso or datetime.utcnow().date().isoformat()
    with get_db() as conn:
        row = conn.execute(
            "SELECT seconds_used FROM user_daily_usage WHERE user_id = ? AND date = ?",
            (user_id, date_iso),
        ).fetchone()
    return int(row["seconds_used"]) if row else 0
