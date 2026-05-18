from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ReconciliationAccountDescriptor(BaseModel):
    """Selectable account descriptor for reconciliation statement views."""

    account_id: str = Field(description="Synthetic reconciliation account id")
    label: str = Field(description="Display label")
    account_type: str = Field(description="Account source type")


class InternalStatementRow(BaseModel):
    """Internal trade statement row used as reconciliation truth."""

    account_id: str = Field(description="Synthetic reconciliation account id")
    trade_id: str = Field(description="Internal trade identifier")
    order_id: str = Field(description="Synthetic order identifier")
    symbol: str = Field(description="Security symbol")
    direction: str = Field(description="Trade direction")
    trade_time: datetime = Field(description="Trade timestamp")
    price: Decimal = Field(description="Trade price")
    quantity: int = Field(description="Trade quantity")
    amount: Decimal = Field(description="Trade amount")
    commission: Decimal = Field(description="Trade commission")


class InternalStatementSummary(BaseModel):
    """Aggregate totals for internal statement rows."""

    total_count: int = Field(description="Filtered row count")
    total_amount: Decimal = Field(description="Filtered gross amount")
    total_commission: Decimal = Field(description="Filtered total commission")


class ReconciliationAccountsPayload(BaseModel):
    """Payload listing accounts that can be reconciled."""

    status: str = Field(description="Availability status")
    endpoint: str = Field(description="Owning endpoint family")
    resource: str = Field(description="Resource identifier")
    items: list[ReconciliationAccountDescriptor] = Field(description="Available reconciliation accounts")
    total_count: int = Field(description="Account count")


class ReconciliationStatementsPayload(BaseModel):
    """Payload containing internal statement rows for one account."""

    status: str = Field(description="Availability status")
    endpoint: str = Field(description="Owning endpoint family")
    resource: str = Field(description="Resource identifier")
    account_id: str = Field(description="Selected synthetic reconciliation account")
    items: list[InternalStatementRow] = Field(description="Paginated statement rows")
    summary: InternalStatementSummary = Field(description="Filtered statement summary")
    total_count: int = Field(description="Filtered statement count")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Current page size")
    source: str = Field(description="Underlying internal truth source")


class ReconciliationImportBatchPayload(BaseModel):
    """Payload describing an imported broker statement batch."""

    status: str = Field(description="Availability status")
    endpoint: str = Field(description="Owning endpoint family")
    resource: str = Field(description="Resource identifier")
    import_batch_id: str = Field(description="In-memory import batch identifier")
    account_id: str | None = Field(description="Resolved reconciliation account for this batch")
    source_type: str = Field(description="Imported CSV source type")
    row_count: int = Field(description="Imported canonical row count")
