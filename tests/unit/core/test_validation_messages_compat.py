from __future__ import annotations

from app.core.validation import CommonMessages as PackageCommonMessages
from app.core.validation import ValidationErrorBuilder as PackageValidationErrorBuilder
from app.core.validation.messages import CommonMessages as CanonicalCommonMessages
from app.core.validation.messages import ValidationErrorBuilder as CanonicalValidationErrorBuilder
from app.core.validation_messages import CommonMessages as LegacyCommonMessages
from app.core.validation_messages import ValidationErrorBuilder as LegacyValidationErrorBuilder


def test_validation_message_compatibility_paths_export_same_symbols() -> None:
    assert LegacyCommonMessages is CanonicalCommonMessages
    assert PackageCommonMessages is CanonicalCommonMessages
    assert LegacyValidationErrorBuilder is CanonicalValidationErrorBuilder
    assert PackageValidationErrorBuilder is CanonicalValidationErrorBuilder


def test_validation_error_builder_remains_usable_from_canonical_path() -> None:
    error = CanonicalValidationErrorBuilder.build_symbol_error("600519", "empty")

    assert error == {
        "field": "symbol",
        "message": CanonicalCommonMessages.SYMBOL_REQUIRED,
        "code": "FIELD_VALIDATION_ERROR",
    }
