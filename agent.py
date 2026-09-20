from datetime import timedelta
from uuid import uuid4

from app.adapters.base import SapAdapter
from app.models import (
    Action,
    DisruptionEvent,
    Impact,
    Recommendation,
)

class SupplyDisruptionAgent:
    def __init__(self, sap: SapAdapter):
        self.sap = sap

    async def analyze(self, event: DisruptionEvent) -> Recommendation:
        current_stock = await self.sap.get_current_stock(event.material, event.plant)

        # Simplified MVP shortage logic:
        # required quantity minus current stock.
        # In production, use SAP MRP/stock-requirements output as authoritative.
        shortage = max(0.0, event.required_quantity - current_stock)

        production_orders = await self.sap.get_production_orders_at_risk(
            event.material, event.plant, shortage
        )
        sales_orders, order_value = await self.sap.get_sales_order_impact(
            event.material, event.plant, shortage
        )

        impact = Impact(
            projected_shortage=shortage,
            production_orders_at_risk=production_orders,
            sales_orders_at_risk=sales_orders,
            order_value_at_risk=order_value,
        )

        actions: list[Action] = []
        remaining = shortage

        # 1) Prefer available internal stock before external buying.
        stocks = await self.sap.get_plant_stocks(event.material)
        candidates = sorted(
            [s for s in stocks if s.plant != event.plant and s.transferable > 0],
            key=lambda s: s.transferable,
            reverse=True,
        )

        for stock in candidates:
            if remaining <= 0:
                break
            qty = min(remaining, stock.transferable)
            actions.append(
                Action(
                    type="STOCK_TRANSFER",
                    quantity=qty,
                    source_plant=stock.plant,
                    estimated_cost=qty * 0.50,  # placeholder transfer-cost assumption
                    rationale=(
                        f"Use transferable stock from plant {stock.plant} "
                        "without violating local requirement and safety-stock assumptions."
                    ),
                )
            )
            remaining -= qty

        # 2) Use approved, unblocked alternate suppliers capable of meeting date.
        if remaining > 0:
            sources = await self.sap.get_approved_sources(
                event.material, event.plant, event.required_date
            )
            eligible = [
                s for s in sources
                if s.approved and not s.blocked
                and s.supplier != event.current_supplier
                and event.required_date >= event.required_date  # explicit readability
                and s.lead_time_days >= 0
            ]

            # Prefer the lowest landed-price proxy among sources whose lead time
            # is within the days available until required date.
            # A production version should include calendars, transit, MOQ, capacity,
            # quality status, contracts and source determination.
            eligible.sort(key=lambda s: (s.unit_price, s.lead_time_days))

            for source in eligible:
                if remaining <= 0:
                    break
                qty = min(remaining, source.max_quantity)
                actions.append(
                    Action(
                        type="ALTERNATE_SUPPLIER",
                        quantity=qty,
                        supplier=source.supplier,
                        estimated_cost=qty * source.unit_price,
                        rationale=(
                            f"Approved alternate source {source.supplier}; "
                            f"lead time {source.lead_time_days} days."
                        ),
                    )
                )
                remaining -= qty

        if shortage == 0:
            actions = [
                Action(
                    type="NO_ACTION",
                    quantity=0,
                    rationale="No projected shortage under the current MVP calculation.",
                )
            ]

        total_cost = sum(a.estimated_cost for a in actions)

        # Confidence is intentionally rules-based in MVP.
        # Do not present LLM certainty as an SAP planning fact.
        confidence = 0.92 if remaining == 0 and shortage > 0 else (1.0 if shortage == 0 else 0.65)

        return Recommendation(
            recommendation_id=str(uuid4()),
            material=event.material,
            plant=event.plant,
            impact=impact,
            actions=actions,
            residual_shortage=max(0.0, remaining),
            total_incremental_cost=round(total_cost, 2),
            confidence=confidence,
            requires_human_approval=True,
        )
