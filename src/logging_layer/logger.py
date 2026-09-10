"""
Logging Layer — Structured Experiment Logger
==============================================
Append-only JSON Lines logging with human-readable summary
report generation.
"""

import json
import os
import time
import logging
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ExperimentLogger:
    """
    Structured logging for experiment events.
    
    - Writes append-only JSON Lines (.jsonl) log files
    - Generates human-readable summary reports (.txt)
    - Tracks step completions, errors, alerts, and timings
    """

    def __init__(self, config: dict):
        self.output_dir = config.get("output_dir", "logs/")
        self.log_format = config.get("log_format", "jsonl")

        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Generate session-specific log filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._log_filename = os.path.join(
            self.output_dir, f"experiment_{timestamp}.jsonl"
        )
        self._log_file = open(self._log_filename, 'a')

        # In-memory event log for summary generation
        self._events: List[Dict] = []
        self._start_time = time.time()
        self._start_monotonic = time.monotonic()
        self._step_timings: Dict[str, float] = {}  # step_id → duration
        self._error_count = 0
        self._step_count = 0

        logger.info(f"ExperimentLogger initialized: {self._log_filename}")

    def log_event(
        self,
        step_id: str,
        status: str,
        confidence: float = 0.0,
        alert_type: Optional[str] = None,
        message: str = "",
        details: Optional[Dict] = None
    ):
        """
        Log an experiment event.
        
        Args:
            step_id: Current step ID
            status: Event status (COMPLETED, STARTED, ERROR, SKIPPED, OUT_OF_SEQUENCE, etc.)
            confidence: Classifier confidence score
            alert_type: Type of alert if applicable
            message: Human-readable message
            details: Additional details dict
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "monotonic": round(time.monotonic() - self._start_monotonic, 3),
            "elapsed_seconds": round(time.time() - self._start_time, 2),
            "step_id": step_id,
            "status": status,
            "confidence": round(confidence, 4),
            "alert_type": alert_type,
            "message": message,
        }
        if details:
            event["details"] = details

        # Write to file
        try:
            self._log_file.write(json.dumps(event) + '\n')
            self._log_file.flush()
        except Exception as e:
            logger.error(f"Failed to write log: {e}")

        # Store in memory
        self._events.append(event)

        # Track metrics
        if status in ("COMPLETED", "step_completed"):
            self._step_count += 1
        elif status in ("ERROR", "SKIPPED", "OUT_OF_SEQUENCE", "skipped_step", "out_of_sequence"):
            self._error_count += 1

    def log_step_timing(self, step_id: str, duration: float):
        """Record the duration spent on a step."""
        self._step_timings[step_id] = duration

    def generate_summary(self, output_path: Optional[str] = None) -> str:
        """
        Generate a human-readable summary report.
        
        Returns the summary text and optionally writes to file.
        """
        elapsed = time.time() - self._start_time
        elapsed_str = self._format_duration(elapsed)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

        lines = [
            "=" * 60,
            "  BAS EXPERIMENT SUMMARY REPORT",
            "  ISRO Human Activity Recognition System",
            "=" * 60,
            "",
            f"  Date:              {now_str}",
            f"  Duration:          {elapsed_str}",
            f"  Total Steps:       {self._step_count}",
            f"  Errors/Alerts:     {self._error_count}",
            f"  Log File:          {self._log_filename}",
            "",
            "-" * 60,
            "  STEP TIMELINE",
            "-" * 60,
        ]

        # Build timeline from events
        step_events = [
            e for e in self._events
            if e["status"] in (
                "COMPLETED", "step_completed", "STARTED", "experiment_started",
                "experiment_complete"
            )
        ]

        for i, event in enumerate(step_events, 1):
            elapsed_s = event.get("elapsed_seconds", 0)
            status_icon = "[OK]" if "complet" in event["status"].lower() else "[>>]"
            lines.append(
                f"  {status_icon} [{self._format_duration(elapsed_s)}] "
                f"{event['step_id']} — {event.get('message', event['status'])}"
            )

        lines.append("")
        lines.append("-" * 60)
        lines.append("  ERRORS & ALERTS")
        lines.append("-" * 60)

        error_events = [
            e for e in self._events
            if e["status"] in (
                "ERROR", "SKIPPED", "OUT_OF_SEQUENCE", "skipped_step",
                "out_of_sequence", "uncertain", "precondition_failed"
            )
        ]

        if error_events:
            for event in error_events:
                elapsed_s = event.get("elapsed_seconds", 0)
                lines.append(
                    f"  [WARN] [{self._format_duration(elapsed_s)}] "
                    f"{event['status'].upper()} at {event['step_id']}: "
                    f"{event.get('message', 'No details')}"
                )
        else:
            lines.append("  No errors or alerts recorded. [OK]")

        lines.extend([
            "",
            "-" * 60,
            "  STEP TIMINGS",
            "-" * 60,
        ])

        if self._step_timings:
            for step_id, duration in self._step_timings.items():
                lines.append(f"  {step_id}: {duration:.1f}s")
        else:
            lines.append("  No step timing data available.")

        lines.extend([
            "",
            "=" * 60,
            f"  Report generated at {now_str}",
            "=" * 60,
        ])

        summary = '\n'.join(lines)

        # Write to file
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.output_dir, f"summary_{timestamp}.txt"
            )

        try:
            with open(output_path, 'w') as f:
                f.write(summary)
            logger.info(f"Summary report written to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to write summary: {e}")

        return summary

    def get_recent_events(self, count: int = 50) -> List[Dict]:
        """Get the most recent N events."""
        return self._events[-count:]

    def get_log_filename(self) -> str:
        """Get the path to the current log file."""
        return self._log_filename

    def compute_log_hash(self) -> str:
        """Compute SHA-256 hash of the current log file for tamper evidence."""
        try:
            self._log_file.flush()
            sha256 = hashlib.sha256()
            with open(self._log_filename, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to compute log hash: {e}")
            return ""

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format seconds into a human-readable duration string."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        if minutes < 60:
            return f"{minutes}m {secs:02d}s"
        hours = int(minutes // 60)
        mins = minutes % 60
        return f"{hours}h {mins:02d}m {secs:02d}s"

    @property
    def event_count(self) -> int:
        return len(self._events)

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def step_count(self) -> int:
        return self._step_count

    def close(self):
        """Close the log file."""
        if self._log_file and not self._log_file.closed:
            self._log_file.flush()
            self._log_file.close()
            logger.info(f"Log file closed: {self._log_filename}")
