"""
Simple storage layer using SQLite.
"""
import json
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from models import AIEvent, Anomaly


class EventStorage:
    """SQLite storage for events and anomalies."""

    def __init__(self, db_path: str = "ai_monitoring.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """Create database and tables."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # Create events table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt TEXT,
                prompt_length INTEGER,
                response TEXT,
                response_length INTEGER,
                latency_ms REAL,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                cost_usd REAL,
                success INTEGER,
                error_message TEXT,
                has_pii INTEGER,
                injection_detected INTEGER,
                risk_level TEXT,
                user_id TEXT,
                session_id TEXT,
                metadata TEXT
            )
        """)

        # Create anomalies table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                anomaly_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                details TEXT,
                recommended_action TEXT,
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        """)

        # Create indexes
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_provider ON events(provider)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_model ON events(model)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_risk ON events(risk_level)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity)")

        self.conn.commit()

    def store_event(self, event: AIEvent):
        """Store an event."""
        self.conn.execute("""
            INSERT INTO events (
                id, timestamp, event_type, provider, model,
                prompt, prompt_length, response, response_length,
                latency_ms, prompt_tokens, completion_tokens, total_tokens,
                cost_usd, success, error_message, has_pii, injection_detected,
                risk_level, user_id, session_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.id,
            event.timestamp.isoformat(),
            event.event_type.value,
            event.provider.value,
            event.model,
            event.prompt,
            event.prompt_length,
            event.response,
            event.response_length,
            event.latency_ms,
            event.tokens.prompt_tokens if event.tokens else None,
            event.tokens.completion_tokens if event.tokens else None,
            event.tokens.total_tokens if event.tokens else None,
            event.cost_usd,
            1 if event.success else 0,
            event.error_message,
            1 if event.has_pii else 0,
            1 if event.injection_detected else 0,
            event.risk_level.value,
            event.user_id,
            event.session_id,
            json.dumps(event.metadata)
        ))
        self.conn.commit()

    def store_anomaly(self, anomaly: Anomaly):
        """Store an anomaly."""
        self.conn.execute("""
            INSERT INTO anomalies (
                id, event_id, timestamp, anomaly_type, severity,
                description, details, recommended_action
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            anomaly.id,
            anomaly.event_id,
            anomaly.timestamp.isoformat(),
            anomaly.anomaly_type,
            anomaly.severity.value,
            anomaly.description,
            json.dumps(anomaly.details),
            anomaly.recommended_action
        ))
        self.conn.commit()

    def get_recent_events(self, limit: int = 100, minutes: int = 60) -> List[Dict]:
        """Get recent events."""
        cutoff = datetime.utcnow().replace(microsecond=0)
        # Simple time-based filter (SQLite datetime comparison)
        cursor = self.conn.execute("""
            SELECT * FROM events
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_recent_anomalies(self, limit: int = 50) -> List[Dict]:
        """Get recent anomalies."""
        cursor = self.conn.execute("""
            SELECT * FROM anomalies
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for the last N hours."""
        cursor = self.conn.execute("""
            SELECT
                COUNT(*) as total_events,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as total_cost,
                AVG(latency_ms) as avg_latency,
                MAX(latency_ms) as max_latency,
                SUM(CASE WHEN has_pii = 1 THEN 1 ELSE 0 END) as pii_events,
                SUM(CASE WHEN injection_detected = 1 THEN 1 ELSE 0 END) as injection_events
            FROM events
            WHERE datetime(timestamp) >= datetime('now', ?)
        """, (f'-{hours} hours',))

        row = cursor.fetchone()
        stats = dict(row) if row else {}

        # Get anomaly count
        cursor = self.conn.execute("""
            SELECT COUNT(*) as anomaly_count
            FROM anomalies
            WHERE datetime(timestamp) >= datetime('now', ?)
        """, (f'-{hours} hours',))

        anomaly_row = cursor.fetchone()
        stats['anomalies'] = anomaly_row['anomaly_count'] if anomaly_row else 0

        return stats

    def get_events_by_risk(self, risk_level: str, limit: int = 50) -> List[Dict]:
        """Get events by risk level."""
        cursor = self.conn.execute("""
            SELECT * FROM events
            WHERE risk_level = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (risk_level, limit))

        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
