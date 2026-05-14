"""Portfolio domain exceptions."""

from __future__ import annotations


class PortfolioConcurrencyException(Exception):
    """Raised when a portfolio operation detects a concurrency conflict."""

    def __init__(self, message: str, entity_type: str | None = None, entity_id: str | None = None):
        self.entity_type = entity_type
        self.entity_id = entity_id

        if entity_type and entity_id:
            full_message = f"Concurrency conflict for {entity_type} {entity_id}: {message}"
        else:
            full_message = message

        super().__init__(full_message)
