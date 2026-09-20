from datetime import date
from typing import Literal
from pydantic import BaseModel, Field

class DisruptionEvent(BaseModel):
    material: str
    plant: str
    required_date: date
    required_quantity: float = Field(gt=0)
    current_po: str | None = None
    current_supplier: str | None = None
    new_confirmed_date: date | None = None

class PlantStock(BaseModel):
    plant: str
    unrestricted_stock: float
    local_requirement: float
    safety_stock: float = 0

    @property
    def transferable(self) -> float:
        return max(
            0.0,
            self.unrestricted_stock - self.local_requirement - self.safety_stock
        )

class SupplierSource(BaseModel):
    supplier: str
    approved: bool
    blocked: bool = False
    lead_time_days: int
    unit_price: float
    max_quantity: float
    currency: str = "USD"

class Impact(BaseModel):
    projected_shortage: float
    production_orders_at_risk: int
    sales_orders_at_risk: int
    order_value_at_risk: float
    currency: str = "USD"

class Action(BaseModel):
    type: Literal[
        "STOCK_TRANSFER",
        "ALTERNATE_SUPPLIER",
        "EXPEDITE",
        "RESCHEDULE",
        "NO_ACTION"
    ]
    quantity: float
    source_plant: str | None = None
    supplier: str | None = None
    estimated_cost: float = 0
    rationale: str

class Recommendation(BaseModel):
    recommendation_id: str
    material: str
    plant: str
    impact: Impact
    actions: list[Action]
    residual_shortage: float
    total_incremental_cost: float
    confidence: float = Field(ge=0, le=1)
    requires_human_approval: bool = True
    status: Literal["PROPOSED", "APPROVED", "REJECTED", "EXECUTED"] = "PROPOSED"
