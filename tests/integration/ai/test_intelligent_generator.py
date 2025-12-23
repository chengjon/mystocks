"""
Dummy AI Test Data Generator for testing purposes.
"""

from typing import List, Dict, Any


class TestDataGenerator:
    def generate_test_cases(self, code_snippet: str) -> List[Dict[str, Any]]:
        """
        Generates dummy test cases based on a code snippet.
        """
        return [
            {
                "name": "dummy_test_case_1",
                "description": f"Generated for {code_snippet}",
                "status": "passed",
            },
            {
                "name": "dummy_test_case_2",
                "description": f"Generated for {code_snippet}",
                "status": "failed",
            },
        ]
