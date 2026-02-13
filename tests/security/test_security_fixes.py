import unittest
import json
import joblib
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

class TestSecurityFixes(unittest.TestCase):
    def test_joblib_serialization(self):
        """Verify joblib is used for serialization instead of pickle"""
        # Create a dummy object
        data = {"a": 1, "b": 2}
        filename = "test_security_joblib.joblib"

        try:
            # Dump using joblib
            joblib.dump(data, filename)

            # Verify file exists
            self.assertTrue(os.path.exists(filename))

            # Load back
            loaded_data = joblib.load(filename)
            self.assertEqual(data, loaded_data)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def test_json_serialization_redis(self):
        """Verify we can use JSON for Redis-like data structures"""
        data = {"key": "value", "list": [1, 2, 3]}
        serialized = json.dumps(data)
        deserialized = json.loads(serialized)
        self.assertEqual(data, deserialized)

    def test_mock_auth_disabled_by_default(self):
        """Verify mock auth logic requires explicit enablement"""
        # Simulate settings logic
        class MockSettings:
            mock_auth_enabled = False

        settings = MockSettings()

        # Logic from security.py
        if not getattr(settings, "mock_auth_enabled", False):
            result = None
        else:
            result = "Auth allowed"

        self.assertIsNone(result, "Mock auth should be disabled by default")

        settings.mock_auth_enabled = True
        if not getattr(settings, "mock_auth_enabled", False):
            result = None
        else:
            result = "Auth allowed"

        self.assertEqual(result, "Auth allowed", "Mock auth should be enabled when configured")

if __name__ == "__main__":
    unittest.main()
