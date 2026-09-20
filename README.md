# N42 SAP Agentic Supply Chain MVP

A standards-oriented MVP for an SAP S/4HANA supply disruption agent.

## Use case
Late supplier delivery -> projected material shortage -> evaluate:
1. interplant stock transfer,
2. approved alternate supplier,
3. combined response,
4. human approval,
5. standard SAP execution.

## Design principle
AI recommends. SAP remains the system of record and executes governed business transactions.

## Current MVP
- FastAPI service
- Mock S/4 adapter for local development
- S/4 OData adapter skeleton
- Shortage calculation
- Interplant transfer recommendation
- Alternate supplier recommendation
- Scenario ranking
- Approval endpoint
- Execution stub

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Open:
- Swagger UI: http://127.0.0.1:8000/docs

Try:
POST `/api/v1/disruptions/analyze`

```json
{
  "material": "RM-10045",
  "plant": "1000",
  "required_date": "2026-09-25",
  "required_quantity": 15000,
  "current_po": "4500012345",
  "current_supplier": "SUP-A",
  "new_confirmed_date": "2026-10-04"
}
```

Then approve a returned recommendation:

POST `/api/v1/recommendations/{recommendation_id}/approve`

Finally execute:

POST `/api/v1/recommendations/{recommendation_id}/execute`

## SAP integration points for production
Replace `MockSapAdapter` with `S4HanaAdapter` and map released APIs/events for:
- purchase order changes/events,
- purchase requisitions / purchase orders,
- stock by plant / MRP area,
- approved source determination,
- production demand,
- sales-order / ATP impact,
- stock transport order creation.

Do not execute business transactions directly from an LLM. Execution should pass through policy, authorization, approval, and SAP-side controls/workflow.
