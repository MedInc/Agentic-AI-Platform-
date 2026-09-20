from datetime import date
from app.adapters.base import SapAdapter
from app.models import PlantStock, SupplierSource

class MockSapAdapter(SapAdapter):
    async def get_current_stock(self, material: str, plant: str) -> float:
        return 8000.0

    async def get_plant_stocks(self, material: str) -> list[PlantStock]:
        return [
            PlantStock(
                plant="1000",
                unrestricted_stock=8000,
                local_requirement=15000,
                safety_stock=2000
            ),
            PlantStock(
                plant="1100",
                unrestricted_stock=12000,
                local_requirement=5000,
                safety_stock=2000
            ),
            PlantStock(
                plant="1200",
                unrestricted_stock=6000,
                local_requirement=4000,
                safety_stock=1000
            ),
        ]

    async def get_approved_sources(
        self, material: str, plant: str, required_date: date
    ) -> list[SupplierSource]:
        return [
            SupplierSource(
                supplier="SUP-A",
                approved=True,
                blocked=False,
                lead_time_days=12,
                unit_price=10.00,
                max_quantity=10000
            ),
            SupplierSource(
                supplier="SUP-B",
                approved=True,
                blocked=False,
                lead_time_days=4,
                unit_price=10.80,
                max_quantity=5000
            ),
            SupplierSource(
                supplier="SUP-C",
                approved=True,
                blocked=False,
                lead_time_days=6,
                unit_price=9.90,
                max_quantity=1000
            ),
        ]

    async def get_production_orders_at_risk(
        self, material: str, plant: str, shortage_qty: float
    ) -> int:
        return 3 if shortage_qty > 0 else 0

    async def get_sales_order_impact(
        self, material: str, plant: str, shortage_qty: float
    ) -> tuple[int, float]:
        if shortage_qty <= 0:
            return 0, 0
        return 11, 1_800_000.0

    async def create_stock_transfer(
        self, material: str, qty: float, source_plant: str, receiving_plant: str
    ) -> dict:
        return {
            "document_type": "STO",
            "document_id": "4500099001",
            "material": material,
            "qty": qty,
            "source_plant": source_plant,
            "receiving_plant": receiving_plant
        }

    async def create_purchase_requisition(
        self, material: str, plant: str, qty: float, supplier: str
    ) -> dict:
        return {
            "document_type": "PR",
            "document_id": "10012345",
            "material": material,
            "plant": plant,
            "qty": qty,
            "supplier": supplier
        }
