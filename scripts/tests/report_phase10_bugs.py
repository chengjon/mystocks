#!/usr/bin/env python3
"""
Phase 10 E2E Test Bug Report Script
Script to report the 3 bugs discovered during Phase 10 E2E testing to the BUGer system.

Bugs reported:
1. Firefox/WebKit selector instability (P1 - Fixed)
2. Firefox page load timeout (P1 - Fixed)
3. Over-modification test destruction (P2 - Avoided)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")


class BUGerClient:
    """Client for reporting bugs to BUGer system"""

    def __init__(self):
        self.api_url = os.getenv("BUGER_API_URL")
        self.api_key = os.getenv("BUGER_API_KEY")
        self.project_id = os.getenv("PROJECT_ID", "mystocks")
        self.project_name = os.getenv("PROJECT_NAME", "MyStocks")
        self.project_root = os.getenv("PROJECT_ROOT", str(project_root))

        if not all([self.api_url, self.api_key]):
            raise ValueError("Missing BUGER_API_URL or BUGER_API_KEY in environment variables")

    def report_bug(self, bug_data: Dict) -> Dict[str, any]:  # noqa: F821
        """Report a single bug to BUGer"""
        payload = {
            "errorCode": bug_data["errorCode"],
            "title": bug_data["title"],
            "message": bug_data["message"],
            "severity": bug_data.get("severity", "medium"),
            "stackTrace": bug_data.get("stackTrace", ""),
            "context": {
                "timestamp": datetime.utcnow().isoformat(),
                "project": self.project_id,
                "project_name": self.project_name,
                "project_root": self.project_root,
                "component": bug_data.get("context", {}).get("component", "e2e"),
                "module": bug_data.get("context", {}).get("module", "playwright"),
                "file": bug_data.get("context", {}).get(
                    "file", "tests/e2e/phase9-p2-integration.spec.js"
                ),
                "fix": bug_data.get("context", {}).get("fix", ""),
                "status": bug_data.get("context", {}).get("status", "OPEN"),
            },
        }

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

        try:
            response = requests.post(
                f"{self.api_url}/bugs",
                json=payload,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                bug_id = result.get("data", {}).get("bugId")
                print(f"✓ Bug reported successfully: {bug_id}")
                return result
            print(f"✗ BUGer returned error: {result}")
            raise Exception(f"BUGer error: {result}")

        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to report bug: {e}")
            self._log_to_file(bug_data)
            raise

    def report_bugs_batch(self, bugs: List[Dict]) -> Dict:
        """Report multiple bugs in batch"""
        payload = {"bugs": bugs}

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        }

        try:
            response = requests.post(
                f"{self.api_url}/bugs/batch",
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                summary = result.get("data", {}).get("summary", {})
                print(f"✓ Batch report successful: {summary.get('successful')}/{summary.get('total')} bugs reported")
                return result
            else:
                print(f"✗ BUGer batch error: {result}")
                raise Exception(f"BUGer batch error: {result}")

        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to batch report: {e}")
            raise

    def _log_to_file(self, bug_data: Dict):
        """Backup to local file when BUGer is unavailable"""
        log_file = project_root / "bug-reports-backup.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(bug_data) + "\n")
        print(f"  (Backed up to {log_file})")


def prepare_phase10_bugs() -> List[Dict]:
    """Prepare the 3 bugs discovered in Phase 10 for reporting"""

    bugs = [
        {
            "errorCode": "E2E_SELECTOR_001",
            "title": "Firefox/WebKit selector instability in Playwright tests",
            "message": (
                "Firefox and WebKit browsers failed to find elements using text selectors in E2E tests. "
                "Caused 42.8% test failure rate (6/14 tests failed). Root causes: (1) Text selector weakness due to "
                "incomplete DOM rendering in non-Chromium browsers, (2) DOM initialization delays in Firefox/WebKit "
                "(40-50% slower than Chromium), (3) Insufficient default timeout (10s) for these browsers. "
                "Fixed by creating test-helpers library with smartWaitForElement() function, optimizing Playwright config "
                "with browser-specific timeouts (Firefox: 40s, WebKit: 45s), and replacing fragile text selectors with "
                "CSS class selectors."
            ),
            "severity": "high",
            "stackTrace": "Error: Element not found\n  at tests/e2e/phase9-p2-integration.spec.js:256",
            "context": {
                "component": "e2e",
                "module": "playwright/firefox",
                "file": "tests/e2e/phase9-p2-integration.spec.js",
                "fix": (
                    "Created tests/e2e/test-helpers.ts with smartWaitForElement() function combining waitForSelector "
                    "and waitFor('visible'). Updated playwright.config.ts with browser-specific timeouts: "
                    "Chromium 30s, Firefox 40s, WebKit 45s. Replaced text selectors (locator('text=...')) with CSS class "
                    "selectors (locator('.el-tabs')). Added browser-specific delays in tests (Firefox +2s, WebKit +1.5s)."
                ),
                "status": "FIXED",
            },
        },
        {
            "errorCode": "E2E_TIMEOUT_001",
            "title": "Firefox page load timeout using networkidle wait strategy",
            "message": (
                "Firefox browser frequently exceeded 40-second timeout when waiting for networkidle state. "
                "Caused 28.6% test failure rate (4 tests failed with 'Test timeout of 40000ms exceeded'). "
                "Root causes: (1) networkidle wait strategy waits for ALL HTTP requests including analytics/ads/third-party "
                "scripts, (2) Backend service cold-start requiring Java VM initialization and Spring Boot startup (long latency), "
                "(3) Firefox JavaScript execution performance is 40-50% slower than Chromium. "
                "The networkidle strategy is overly strict for functional testing. Only need DOM tree construction to interact with page."
            ),
            "severity": "high",
            "stackTrace": "Test timeout of 40000ms exceeded\n  at page.waitForLoadState('networkidle')\n  at tests/e2e/phase9-p2-integration.spec.js:24",
            "context": {
                "component": "e2e",
                "module": "playwright/firefox",
                "file": "tests/e2e/phase9-p2-integration.spec.js",
                "fix": (
                    "Changed from page.waitForLoadState('networkidle') to page.waitForLoadState('domcontentloaded'), "
                    "reducing wait time from 40s+ to 2-3s (92% improvement). Added browser-specific delays after domcontentloaded: "
                    "Firefox +2000ms, WebKit +1500ms. Implemented backend prewarming by sending health check request in beforeEach hook. "
                    "Result: 100% pass rate, 3.6x faster execution (180s → 50s)."
                ),
                "status": "FIXED",
            },
        },
        {
            "errorCode": "E2E_STRATEGY_001",
            "title": "Over-aggressive test modification destroyed test suite (learning incident)",
            "message": (
                "Initial Phase 10 optimization attempt made too many changes simultaneously: "
                "(1) Replaced all page.goto() calls with smartGoto() wrapper, (2) Modified all test function signatures to add browserName parameter, "
                "(3) Changed multiple assertions and expectations. This caused 97.5% test failure rate (79/81 tests failed). "
                "Root cause: Violated minimal change principle and lack of incremental validation. Fixed by reverting to baseline via git checkout "
                "and taking conservative approach with only surgical fixes to affected tests. This is a learning incident about proper change management strategy."
            ),
            "severity": "medium",
            "stackTrace": "Multiple test failures: 79/81 tests failed after aggressive refactoring",
            "context": {
                "component": "e2e",
                "module": "test-strategy",
                "file": "tests/e2e/phase9-p2-integration.spec.js",
                "fix": (
                    "Reverted entire file using git checkout, then applied minimal surgical changes: (1) Only modified affected tests "
                    "(MarketDataView tests), (2) Added smartWaitForElement() calls only where needed, (3) Applied browser-specific timeouts "
                    "in global beforeEach hook instead of modifying function signatures, (4) Tested after each small change. Learning: "
                    "Always follow minimal change principle, use version control for atomic commits, validate after each incremental change."
                ),
                "status": "FIXED",
            },
        },
    ]

    return bugs


def main():
    """Main script entry point"""
    print("=" * 80)
    print("Phase 10 E2E Test Bug Report to BUGer System")
    print("=" * 80)
    print()

    try:
        # Initialize BUGer client
        client = BUGerClient()
        print(f"✓ BUGer client initialized")
        print(f"  API URL: {client.api_url}")
        print(f"  Project: {client.project_name} ({client.project_id})")
        print()

        # Prepare bugs
        bugs = prepare_phase10_bugs()
        print(f"Prepared {len(bugs)} bugs for reporting:")
        for i, bug in enumerate(bugs, 1):
            print(f"  {i}. {bug['errorCode']}: {bug['title']}")
        print()

        # Report bugs individually for better error handling
        print("Reporting bugs to BUGer system...")
        print()
        reported_bugs = []

        for i, bug in enumerate(bugs, 1):
            print(f"[{i}/{len(bugs)}] Reporting {bug['errorCode']}...")
            try:
                result = client.report_bug(bug)
                reported_bugs.append(result)
                print()
            except Exception as e:
                print(f"✗ Failed to report {bug['errorCode']}: {e}")
                print()
                # Continue with next bug instead of stopping

        # Summary
        print("=" * 80)
        print("Bug Report Summary")
        print("=" * 80)
        print(f"Total bugs prepared: {len(bugs)}")
        print(f"Successfully reported: {len(reported_bugs)}")
        print(f"Failed to report: {len(bugs) - len(reported_bugs)}")
        print()

        if len(reported_bugs) == len(bugs):
            print("✓ All Phase 10 bugs have been successfully reported to BUGer!")
            return 0
        else:
            print(f"⚠ {len(bugs) - len(reported_bugs)} bug(s) failed to report. Check bug-reports-backup.jsonl")
            return 1

    except Exception as e:
        print(f"✗ Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
