from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.adapters.mock_sap import MockSapAdapter
from app.adapters.s4hana import S4HanaAdapter
from app.config import settings
from app.models import DisruptionEvent, Recommendation
from app.services.agent import SupplyDisruptionAgent
from app.services.execution import ExecutionService
from app.services.repository import repo

app = FastAPI(
    title="N42 SAP Agentic Supply Chain",
    version="0.1.0",
    description="Supply disruption response agent for SAP S/4HANA."
)

sap = MockSapAdapter() if settings.use_mock_sap else S4HanaAdapter()
agent = SupplyDisruptionAgent(sap)
executor = ExecutionService(sap)

class ApprovalRequest(BaseModel):
    approved_by: str
    comment: str | None = None

@app.get("/health")
async def health():
    return {"status": "ok", "mock_sap": settings.use_mock_sap}

@app.post("/api/v1/disruptions/analyze", response_model=Recommendation)
async def analyze_disruption(event: DisruptionEvent):
    rec = await agent.analyze(event)
    repo.save(rec)
    return rec

@app.get("/api/v1/recommendations/{recommendation_id}", response_model=Recommendation)
async def get_recommendation(recommendation_id: str):
    rec = repo.get(recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec

@app.post("/api/v1/recommendations/{recommendation_id}/approve", response_model=Recommendation)
async def approve_recommendation(recommendation_id: str, request: ApprovalRequest):
    rec = repo.get(recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    if rec.status != "PROPOSED":
        raise HTTPException(status_code=409, detail=f"Current status is {rec.status}")

    # Production: enforce SAP/BTP identity, SoD, thresholds, workflow and audit trail.
    rec.status = "APPROVED"
    repo.save(rec)
    return rec

@app.post("/api/v1/recommendations/{recommendation_id}/execute")
async def execute_recommendation(recommendation_id: str):
    rec = repo.get(recommendation_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    try:
        documents = await executor.execute(rec)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    repo.save(rec)
    return {
        "recommendation_id": recommendation_id,
        "status": rec.status,
        "sap_documents": documents
    }
