"""ExtraSourceRouter — category-driven dispatch to ExtraSource adapters.

Sibling to (not part of) :class:`HybridDataSource`. Route handlers call
this router when they need data for a category that is NOT in
:data:`OPENSTOCK_STATIC_CATEGORIES`. OpenStock-managed categories MUST
be served by ``OpenStockClient`` directly; this router refuses to
dispatch them so that programmer errors surface immediately rather
than silently dispatching a shadow implementation.

See ``openspec/changes/add-extra-source-adapter-contract/`` §6 for
the routing-decision tree and the rationale for keeping this separate
from the endpoint-driven ``HybridDataSource``.
"""

from __future__ import annotations

import logging
from typing import Any

from .contract import ExtraSourceAdapter, ExtraSourceResult
from .registry import find_by_category, get_openstock_static_categories

logger = logging.getLogger(__name__)


class UnsupportedCategoryError(RuntimeError):
    """Raised when :class:`ExtraSourceRouter` is asked to serve a
    category it cannot handle.

    Two cases:

    * The category is in :data:`OPENSTOCK_STATIC_CATEGORIES` — the
      route handler should have called ``OpenStockClient`` directly;
      this is a programmer error.
    * The category is unknown (not in OpenStock, not registered) —
      the route handler should map this to the ``UNSUPPORTED_CATEGORY``
      error envelope.
    """

    def __init__(self, category: str, reason: str) -> None:
        self.category = category
        self.reason = reason
        super().__init__(f"Unsupported category '{category}': {reason}")


class ExtraSourceFetchError(RuntimeError):
    """Raised when an ExtraSource adapter's ``fetch()`` call raises.

    The route handler should map this to the ``DATA_GATEWAY_UNAVAILABLE``
    error envelope. ``adapter_name`` and ``cause_type`` are populated
    for diagnostic context; the original exception is chained via
    ``__cause__`` for full traceback access.
    """

    def __init__(
        self,
        adapter_name: str,
        category: str,
        cause: BaseException,
    ) -> None:
        self.adapter_name = adapter_name
        self.category = category
        self.cause_type = type(cause).__name__
        super().__init__(
            f"ExtraSource '{adapter_name}' fetch failed for category " f"'{category}': {self.cause_type}: {cause}"
        )
        # Chain the original exception so callers can walk `__cause__`
        # for the full traceback. We cannot use `raise ... from cause`
        # here because we're inside __init__, not a raise statement.
        self.__cause__ = cause


class ExtraSourceRouter:
    """Category-driven dispatch to registered ExtraSource adapters.

    Stateless wrapper around :func:`find_by_category`. A single module
    instance is exposed as :data:`default_router` for convenient
    import; route handlers may also construct their own instance for
    test isolation.
    """

    def fetch(self, category: str, params: dict[str, Any]) -> ExtraSourceResult:
        if category in get_openstock_static_categories():
            raise UnsupportedCategoryError(
                category=category,
                reason=("belongs to OpenStock static inventory; route handlers " "must call OpenStockClient directly"),
            )
        adapter: ExtraSourceAdapter | None = find_by_category(category)
        if adapter is None:
            raise UnsupportedCategoryError(
                category=category,
                reason="not registered with any ExtraSource adapter",
            )
        meta = adapter.get_meta()
        try:
            result = adapter.fetch(params)
        except Exception as cause:
            logger.warning(
                "ExtraSource %r fetch failed for %r: %s: %s",
                meta.name,
                category,
                type(cause).__name__,
                cause,
            )
            raise ExtraSourceFetchError(
                adapter_name=meta.name,
                category=category,
                cause=cause,
            ) from cause
        return result


default_router = ExtraSourceRouter()


__all__ = [
    "ExtraSourceRouter",
    "UnsupportedCategoryError",
    "ExtraSourceFetchError",
    "default_router",
]
