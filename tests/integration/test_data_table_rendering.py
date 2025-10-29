"""
Integration Test: Data Table Rendering

Tests that data tables (Dragon Tiger, ETF, Fund Flow, Chip Race) render correctly
with actual data from the database, implementing complete 5-layer verification.

Test Coverage:
- Layer 5: Database tables have data
- Layer 2: Market data APIs return valid data
- Layer 4: Table UI elements render correctly
- Layer 3: Complete data flow from DB → API → Table UI

Requirement: FR-006 (Data Table Rendering with All Layers)

Author: MyStocks Development Team
Created: 2025-10-29
"""

import pytest
import os
from playwright.sync_api import Page, expect
from tests.integration.utils import (
    login,
    take_screenshot,
    wait_for_page_load,
    wait_for_element,
    assert_table_has_data,
    get_table_data,
    assert_no_loading_spinner,
    CommonSelectors,
    ConsoleCapture,
    validate_all_layers,
)

# Configuration
MYSTOCKS_URL = os.getenv("MYSTOCKS_URL", "http://localhost:8000")
MYSTOCKS_USER = os.getenv("MYSTOCKS_USER", "admin")
MYSTOCKS_PASS = os.getenv("MYSTOCKS_PASS", "admin123")


class TestDragonTigerTable:
    """Test Dragon Tiger (龙虎榜) data table rendering."""

    def test_dragon_tiger_table_renders(self, page: Page):
        """
        Test that Dragon Tiger table renders on page.

        Layer 4: UI validation
        """
        # Log in
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)

        # Navigate to Dragon Tiger page
        page.goto(f"{MYSTOCKS_URL}/dragon-tiger")
        wait_for_page_load(page)
        assert_no_loading_spinner(page)

        # Wait for table element
        wait_for_element(page, CommonSelectors.DRAGON_TIGER_TABLE, state="visible")

        # Verify table exists
        table = page.locator(CommonSelectors.DRAGON_TIGER_TABLE)
        expect(table).to_be_visible()

        print("✅ Dragon Tiger table rendered")

        # Take screenshot
        take_screenshot(page, "test_dragon_tiger_table")

    def test_dragon_tiger_table_has_data(self, page: Page, db_cursor):
        """
        Test that Dragon Tiger table displays actual data.

        Layers: 5 (Database) → 4 (UI)
        """
        # Layer 5: Verify database has data
        db_cursor.execute("SELECT COUNT(*) FROM cn_stock_top")
        db_count = db_cursor.fetchone()[0]

        assert db_count > 0, "No data in cn_stock_top table"
        print(f"✅ Layer 5: Database has {db_count} records")

        # Layer 4: Verify table displays data
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        page.goto(f"{MYSTOCKS_URL}/dragon-tiger")
        wait_for_page_load(page)
        assert_no_loading_spinner(page)

        # Count rows in table
        row_count = assert_table_has_data(
            page, CommonSelectors.DRAGON_TIGER_TABLE, min_rows=1
        )

        print(f"✅ Layer 4: Table displays {row_count} rows")

        # Take screenshot
        take_screenshot(page, "test_dragon_tiger_data")

    def test_dragon_tiger_all_layers(self, page: Page, db_cursor, api_client):
        """
        Complete multi-layer validation of Dragon Tiger table.

        Validates: Layer 5 → Layer 2 → Layer 4 → Layer 3
        """
        print("\n=== Dragon Tiger Multi-Layer Validation ===\n")

        # Log in and navigate
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        page.goto(f"{MYSTOCKS_URL}/dragon-tiger")
        wait_for_page_load(page)

        # Multi-layer validation
        result = validate_all_layers(
            db_cursor=db_cursor,
            api_client=api_client,
            page=page,
            config={
                "database_table": "cn_stock_top",
                "api_endpoint": "/api/market/v3/dragon-tiger?limit=10",
                "api_expected_fields": ["stock_code", "stock_name", "trade_date"],
                "ui_elements": {
                    "table": CommonSelectors.DRAGON_TIGER_TABLE,
                    "table_header": "thead, .table-header",
                    "table_body": "tbody, .table-body",
                },
                "expected_min_count": 5,
            },
        )

        # Check results
        assert result.all_passed, f"Multi-layer validation failed:\n{result}"

        print("\n✅ ✅ ✅ Dragon Tiger all layers validated!")
        take_screenshot(page, "test_dragon_tiger_all_layers_SUCCESS")


class TestETFTable:
    """Test ETF data table rendering."""

    def test_etf_table_renders(self, page: Page):
        """
        Test that ETF table renders on page.

        Layer 4: UI validation
        """
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)

        # Navigate to ETF page
        page.goto(f"{MYSTOCKS_URL}/etf")
        wait_for_page_load(page)
        assert_no_loading_spinner(page)

        # Wait for table
        wait_for_element(page, CommonSelectors.ETF_TABLE, state="visible")

        # Verify table exists
        table = page.locator(CommonSelectors.ETF_TABLE)
        expect(table).to_be_visible()

        print("✅ ETF table rendered")
        take_screenshot(page, "test_etf_table")

    def test_etf_table_all_layers(self, page: Page, db_cursor, api_client):
        """
        Complete multi-layer validation of ETF table.
        """
        print("\n=== ETF Multi-Layer Validation ===\n")

        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        page.goto(f"{MYSTOCKS_URL}/etf")
        wait_for_page_load(page)

        result = validate_all_layers(
            db_cursor=db_cursor,
            api_client=api_client,
            page=page,
            config={
                "database_table": "cn_etf_spot",
                "api_endpoint": "/api/market/v3/etf-data?limit=10",
                "api_expected_fields": ["stock_code", "stock_name"],
                "ui_elements": {"table": CommonSelectors.ETF_TABLE},
                "expected_min_count": 5,
            },
        )

        assert result.all_passed, f"Multi-layer validation failed:\n{result}"
        print("\n✅ ✅ ✅ ETF all layers validated!")
        take_screenshot(page, "test_etf_all_layers_SUCCESS")


class TestFundFlowTable:
    """Test Fund Flow (资金流向) data table rendering."""

    def test_fund_flow_table_renders(self, page: Page):
        """
        Test that Fund Flow table renders on page.

        Layer 4: UI validation
        """
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)

        # Navigate to Fund Flow page
        page.goto(f"{MYSTOCKS_URL}/fund-flow")
        wait_for_page_load(page)
        assert_no_loading_spinner(page)

        # Wait for table
        wait_for_element(page, CommonSelectors.FUND_FLOW_TABLE, state="visible")

        # Verify table exists
        table = page.locator(CommonSelectors.FUND_FLOW_TABLE)
        expect(table).to_be_visible()

        print("✅ Fund Flow table rendered")
        take_screenshot(page, "test_fund_flow_table")

    def test_fund_flow_table_all_layers(self, page: Page, db_cursor, api_client):
        """
        Complete multi-layer validation of Fund Flow table.
        """
        print("\n=== Fund Flow Multi-Layer Validation ===\n")

        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        page.goto(f"{MYSTOCKS_URL}/fund-flow")
        wait_for_page_load(page)

        result = validate_all_layers(
            db_cursor=db_cursor,
            api_client=api_client,
            page=page,
            config={
                "database_table": "cn_stock_fund_flow_industry",
                "api_endpoint": "/api/market/v3/fund-flow?industry_type=csrc&limit=10",
                "api_expected_fields": ["industry_name", "main_net_inflow"],
                "ui_elements": {"table": CommonSelectors.FUND_FLOW_TABLE},
                "expected_min_count": 5,
            },
        )

        assert result.all_passed, f"Multi-layer validation failed:\n{result}"
        print("\n✅ ✅ ✅ Fund Flow all layers validated!")
        take_screenshot(page, "test_fund_flow_all_layers_SUCCESS")


class TestChipRaceTable:
    """Test Chip Race (竞价抢筹) data table rendering."""

    def test_chip_race_table_renders(self, page: Page):
        """
        Test that Chip Race table renders on page.

        Layer 4: UI validation
        """
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)

        # Navigate to Chip Race page
        page.goto(f"{MYSTOCKS_URL}/chip-race")
        wait_for_page_load(page)
        assert_no_loading_spinner(page)

        # Wait for table
        wait_for_element(page, CommonSelectors.CHIP_RACE_TABLE, state="visible")

        # Verify table exists
        table = page.locator(CommonSelectors.CHIP_RACE_TABLE)
        expect(table).to_be_visible()

        print("✅ Chip Race table rendered")
        take_screenshot(page, "test_chip_race_table")

    def test_chip_race_table_all_layers(self, page: Page, db_cursor, api_client):
        """
        Complete multi-layer validation of Chip Race table.
        """
        print("\n=== Chip Race Multi-Layer Validation ===\n")

        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        page.goto(f"{MYSTOCKS_URL}/chip-race")
        wait_for_page_load(page)

        result = validate_all_layers(
            db_cursor=db_cursor,
            api_client=api_client,
            page=page,
            config={
                "database_table": "cn_stock_chip_race_open",
                "api_endpoint": "/api/market/v3/chip-race?limit=10",
                "api_expected_fields": ["stock_code", "stock_name"],
                "ui_elements": {"table": CommonSelectors.CHIP_RACE_TABLE},
                "expected_min_count": 5,
            },
        )

        assert result.all_passed, f"Multi-layer validation failed:\n{result}"
        print("\n✅ ✅ ✅ Chip Race all layers validated!")
        take_screenshot(page, "test_chip_race_all_layers_SUCCESS")


class TestTableDataExtraction:
    """Test data extraction from tables for validation."""

    def test_extract_dragon_tiger_table_data(self, page: Page):
        """
        Test extracting actual data from Dragon Tiger table.

        Demonstrates how to validate specific data values.
        """
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        page.goto(f"{MYSTOCKS_URL}/dragon-tiger")
        wait_for_page_load(page)
        assert_no_loading_spinner(page)

        # Extract table data
        table_data = get_table_data(page, CommonSelectors.DRAGON_TIGER_TABLE)

        assert len(table_data) > 0, "No data extracted from table"
        print(f"✅ Extracted {len(table_data)} rows from table")

        # Validate first row structure
        first_row = table_data[0]
        print(f"\nFirst row data: {first_row}")

        # Expected fields (adjust based on actual table)
        # This demonstrates data-level validation
        assert len(first_row) > 0, "Row has no data"

        print(f"✅ Table data extraction successful")


class TestTableConsoleErrors:
    """Test that table pages load without console errors."""

    @pytest.mark.parametrize(
        "page_name,page_url",
        [
            ("Dragon Tiger", "/dragon-tiger"),
            ("ETF", "/etf"),
            ("Fund Flow", "/fund-flow"),
            ("Chip Race", "/chip-race"),
        ],
    )
    def test_table_page_no_console_errors(self, page: Page, page_name, page_url):
        """
        Test that table pages load without console errors.

        Layer 4: Console validation
        """
        # Set up console capture
        console = ConsoleCapture(page)

        # Log in and navigate
        login(page, MYSTOCKS_USER, MYSTOCKS_PASS, MYSTOCKS_URL)
        page.goto(f"{MYSTOCKS_URL}{page_url}")
        wait_for_page_load(page)

        # Wait for any async operations
        page.wait_for_timeout(2000)

        # Check console errors
        errors = console.get_errors()

        if errors:
            print(f"⚠️  {page_name} page has console errors:")
            for error in errors:
                print(f"   - {error}")
            pytest.fail(f"{page_name} page has console errors")

        print(f"✅ {page_name} page: No console errors")
