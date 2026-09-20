import httpx
from datetime import date
from app.adapters.base import SapAdapter
from app.config import settings
from app.models import PlantStock, SupplierSource

class S4HanaAdapter(SapAdapter):
    '''
    Production adapter skeleton.

    IMPORTANT:
    API entity names and payload fields must be confirmed against the exact
    S/4HANA deployment/release and the released APIs enabled in that system.
    '''

    def __init__(self):
        self.base_url = settings.sap_base_url.rstrip("/")
        self.auth = (settings.sap_username, settings.sap_password)

    async def _get(self, path: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            timeout=30.0
        ) as client:
            r = await client.get(path, params=params, headers={"Accept": "application/json"})
            r.raise_for_status()
            return r.json()

    async def _post(self, path: str, payload: dict) -> dict:
        # For productive S/4, implement CSRF-token handling or OAuth/client flow
        # according to your landscape and communication arrangement.
        async with httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            timeout=30.0
        ) as client:
            r = await client.post(
                path,
                json=payload,
                headers={"Accept": "application/json", "Content-Type": "application/json"}
            )
            r.raise_for_status()
            return r.json()

    async def get_current_stock(self, material: str, plant: str) -> float:
        raise NotImplementedError(
            "Map this to the released stock/inventory API available in your S/4 release."
        )

    async def get_plant_stocks(self, material: str) -> list[PlantStock]:
        raise NotImplementedError(
            "Map this to released stock/MRP-area APIs or a governed custom CDS exposure."
        )

    async def get_approved_sources(
        self, material: str, plant: str, required_date: date
    ) -> list[SupplierSource]:
        raise NotImplementedError(
            "Map source list/PIR/contract/quota data via released APIs/CDS views."
        )

    async def get_production_orders_at_risk(
        self, material: str, plant: str, shortage_qty: float
    ) -> int:
        raise NotImplementedError(
            "Map to production-order / MRP demand data available in your S/4 system."
        )

    async def get_sales_order_impact(
        self, material: str, plant: str, shortage_qty: float
    ) -> tuple[int, float]:
        raise NotImplementedError(
            "Map to sales-order and availability data; ATP remains authoritative."
        )

    async def create_stock_transfer(
        self, material: str, qty: float, source_plant: str, receiving_plant: str
    ) -> dict:
        # Often represented using a purchase order/STO business process.
        # Map to the released Purchase Order API for your target S/4 edition.
        raise NotImplementedError(
            "Implement via released Purchase Order API after approval."
        )

    async def create_purchase_requisition(
        self, material: str, plant: str, qty: float, supplier: str
    ) -> dict:
        # SAP documents API_PURCHASEREQUISITION_2 as OData V4.
        path = (
            "/sap/opu/odata4/sap/api_purchaserequisition_2/"
            "srvd_a2x/sap/purchaserequisition/0001/PurchaseReqn"
        )

        # Illustrative payload only. Confirm mandatory fields, units, purchasing
        # organization/group, account assignment, and supplier/source semantics
        # in the target S/4 release before enabling.
        payload = {
            "PurchaseRequisitionType": "NB",
            "_PurchaseRequisitionItem": [{
                "Material": material,
                "Plant": plant,
                "RequestedQuantity": qty,
                "Supplier": supplier
            }]
        }
        return await self._post(path, payload)
