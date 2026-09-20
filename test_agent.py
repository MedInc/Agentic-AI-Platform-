import pytest

from app.adapters.mock_sap import MockSapAdapter
from app.models import DisruptionEvent
from app.services.agent import SupplyDisruptionAgent

@pytest.mark.asyncio
async def test_shortage_is_fully_covered():
    agent = SupplyDisruptionAgent(MockSapAdapter())
    event = DisruptionEvent(
        material="RM-10045",
        plant="1000",
        required_date="2026-09-25",
        required_quantity=15000,
        current_po="4500012345",
        current_supplier="SUP-A",
        new_confirmed_date="2026-10-04",
    )
    rec = await agent.analyze(event)

    assert rec.impact.projected_shortage == 7000
    assert rec.residual_shortage == 0
    assert rec.requires_human_approval is True
    assert any(a.type == "STOCK_TRANSFER" for a in rec.actions)
