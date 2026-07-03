"""OpenStock static category loader.

Parses the canonical OpenStock data-capability scope document pulled in
via the ``deps/openstock`` git submodule. The document lives at
``<repo_root>/deps/openstock/docs/DATA_CAPABILITY_SCOPE.md`` and uses
Markdown tables whose first cell per row is the category identifier in
backticks (e.g. ``| `FUND_FLOW` | ... |``).

The loader is invoked once at FastAPI lifespan startup (before any
``register_extra_source`` call) and the result is cached in a
module-level frozenset consumed by both the registry and the router.

Failure mode is intentionally strict: a missing file or empty parse
raises — that signals a CI / submodule configuration problem, not a
runtime degradation we should silently fall back from.
"""

from __future__ import annotations

import re
from pathlib import Path

__all__ = [
    "OpenStockDataScopeFileMissingError",
    "OpenStockDataScopeParseError",
    "load_openstock_categories_from_submodule",
]


class OpenStockDataScopeFileMissingError(RuntimeError):
    """Raised when the OpenStock ``DATA_CAPABILITY_SCOPE.md`` file
    cannot be located. Usually means the ``deps/openstock`` submodule
    was not checked out (CI forgot ``submodules: recursive`` or a
    fresh clone forgot ``--recursive``)."""


class OpenStockDataScopeParseError(RuntimeError):
    """Raised when the scope document was found but no category tokens
    could be extracted. Indicates the document format changed in a way
    the regex parser does not handle."""


# Match backtick-wrapped ALL_CAPS tokens with at least 3 chars. This
# tolerates the document mixing table cells, inline code spans, and
# headings — only the uppercase category identifiers match.
_CATEGORY_PATTERN = re.compile(r"`([A-Z][A-Z0-9_]{2,})`")


def load_openstock_categories_from_submodule(repo_root: Path | None = None) -> frozenset[str]:
    """Parse OpenStock's canonical 70-category list from the submodule.

    Args:
        repo_root: Repository root containing the ``deps/openstock``
            submodule. When ``None``, the loader walks up from this
            file's location to find a directory containing
            ``deps/openstock``. Explicit pass-through is preferred in
            production (lifespan) to avoid ambiguity.

    Returns:
        frozenset[str]: de-duplicated category identifiers (e.g.
        ``"FUND_FLOW"``, ``"ANNOUNCEMENTS"``).

    Raises:
        OpenStockDataScopeFileMissingError: scope document not found.
        OpenStockDataScopeParseError: document found but no tokens.
    """
    if repo_root is None:
        repo_root = _discover_repo_root()

    scope_path = repo_root / "deps" / "openstock" / "docs" / "DATA_CAPABILITY_SCOPE.md"
    if not scope_path.is_file():
        raise OpenStockDataScopeFileMissingError(
            f"OpenStock data-capability scope document not found at {scope_path}. "
            "Ensure the deps/openstock submodule is checked out "
            "(try: git submodule update --init --recursive)."
        )

    text = scope_path.read_text(encoding="utf-8")
    matches = _CATEGORY_PATTERN.findall(text)
    # De-duplicate while preserving the frozenset contract.
    categories = frozenset(matches)

    if not categories:
        raise OpenStockDataScopeParseError(
            f"OpenStock data-capability scope document {scope_path} contained no "
            "parseable category tokens. Verify the document format hasn't drifted."
        )

    return categories


def _discover_repo_root() -> Path:
    """Walk up from this file to find the directory containing
    ``deps/openstock``. Used only when callers don't pass an explicit
    ``repo_root``.
    """
    current = Path(__file__).resolve()
    for ancestor in [current, *current.parents]:
        if (ancestor / "deps" / "openstock").is_dir():
            return ancestor
    # Fall back to a sensible default if the submodule layout changes.
    return Path.cwd()
