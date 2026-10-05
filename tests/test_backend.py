"""
BASGUARD — Automated Backend Unit & Integration Tests (Built-in unittest)
File: tests/test_backend.py
"""

import sys
import os
import unittest
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cv_worker import CVWorker
from src.llm_auditor import AsyncLLMAuditor, ProtocolAudit


class TestBASGuardBackend(unittest.TestCase):
    def test_cv_worker_synthetic_generation(self):
        """Verify CVWorker synthetic frame generation and Base64 encoding."""
        worker = CVWorker(source=0, fps_target=30.0)
        frame = worker._generate_synthetic_frame()
        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (1080, 1920, 3))

        b64_str = worker.encode_frame_base64(frame, quality=50)
        self.assertIsInstance(b64_str, str)
        self.assertGreater(len(b64_str), 100)

    def test_llm_auditor_mock(self):
        """Verify AsyncLLMAuditor mock Pydantic v2 response."""
        async def run_test():
            auditor = AsyncLLMAuditor()
            result = await auditor.audit_frame(
                base64_image="mock_b64",
                current_step_id="PICK_YELLOW",
                telemetry_context={"fps": 30.0}
            )
            self.assertIsInstance(result, ProtocolAudit)
            self.assertTrue(result.is_protocol_compliant)
            self.assertGreaterEqual(result.confidence_score, 0.9)
            self.assertEqual(result.step_name, "PICK_YELLOW")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
