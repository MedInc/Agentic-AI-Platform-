from app.adapters.base import SapAdapter
from app.models import Recommendation

class ExecutionService:
    def __init__(self, sap: SapAdapter):
        self.sap = sap

    async def execute(self, rec: Recommendation) -> list[dict]:
        if rec.status != "APPROVED":
            raise ValueError("Recommendation must be approved before execution.")

        results: list[dict] = []

        for action in rec.actions:
            if action.type == "STOCK_TRANSFER":
                result = await self.sap.create_stock_transfer(
                    material=rec.material,
                    qty=action.quantity,
                    source_plant=action.source_plant,
                    receiving_plant=rec.plant,
                )
                results.append(result)

            elif action.type == "ALTERNATE_SUPPLIER":
                result = await self.sap.create_purchase_requisition(
                    material=rec.material,
                    plant=rec.plant,
                    qty=action.quantity,
                    supplier=action.supplier,
                )
                results.append(result)

            elif action.type == "NO_ACTION":
                results.append({"document_type": "NONE", "status": "NO_ACTION"})

        rec.status = "EXECUTED"
        return results
