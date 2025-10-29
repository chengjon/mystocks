"""
Integration Test Utilities Package

This package provides utility modules for Playwright integration tests:
- browser_helpers: Screenshot, wait, and UI utilities
- layer_validation: 5-layer verification model implementation

Author: MyStocks Development Team
Created: 2025-10-29
"""

from .browser_helpers import (
    take_screenshot,
    take_full_page_screenshot,
    take_element_screenshot,
    wait_for_page_load,
    wait_for_element,
    wait_for_text,
    wait_for_api_response,
    smart_wait,
    CommonSelectors,
    ConsoleCapture,
    NetworkMonitor,
    login,
    logout,
    assert_table_has_data,
    get_table_data,
    assert_no_loading_spinner,
)

from .layer_validation import (
    LayerValidation,
    validate_layer_5_database,
    validate_layer_2_api,
    validate_layer_4_ui,
    validate_all_layers,
    LayerValidationResult,
)

__all__ = [
    # Browser helpers
    "take_screenshot",
    "take_full_page_screenshot",
    "take_element_screenshot",
    "wait_for_page_load",
    "wait_for_element",
    "wait_for_text",
    "wait_for_api_response",
    "smart_wait",
    "CommonSelectors",
    "ConsoleCapture",
    "NetworkMonitor",
    "login",
    "logout",
    "assert_table_has_data",
    "get_table_data",
    "assert_no_loading_spinner",
    # Layer validation
    "LayerValidation",
    "validate_layer_5_database",
    "validate_layer_2_api",
    "validate_layer_4_ui",
    "validate_all_layers",
    "LayerValidationResult",
]
