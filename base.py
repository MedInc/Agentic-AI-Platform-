from abc import ABC, abstractmethod
from datetime import date
from app.models import PlantStock, SupplierSource

class SapAdapter(ABC):
    @abstractmethod
    async def get_current_stock(self, material: str, plant: str) -> float:
        ...

    @abstractmethod
    async def get_plant_stocks(self, material: str) -> list[PlantStock]:
        ...

    @abstractmethod
    async def get_approved_sources(
        self, material: str, plant: str, required_date: date
    ) -> list[SupplierSource]:
        ...

    @abstractmethod
    async def get_production_orders_at_risk(
        self, material: str, plant: str, shortage_qty: float
    ) -> int:
        ...

    @abstractmethod
    async def get_sales_order_impact(
        self, material: str, plant: str, shortage_qty: float
    ) -> tuple[int, float]:
        ...

    @abstractmethod
    async def create_stock_transfer(
        self, material: str, qty: float, source_plant: str, receiving_plant: str
    ) -> dict:
        ...

    @abstractmethod
    async def create_purchase_requisition(
        self, material: str, plant: str, qty: float, supplier: str
    ) -> dict:
        ...
