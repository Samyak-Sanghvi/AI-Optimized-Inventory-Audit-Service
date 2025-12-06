**Project Overview**

This repository contains a small FastAPI service that performs and tracks inventory audits. It exposes HTTP endpoints to list inventory with recent audit logs, start an audit (delegated to a Celery worker), and to query audit notes using an AI chain that extracts an audit status from natural-language questions.

**Note**: This README was AI-generated.

**Requirements**
- **Python**: 3.8+ (virtual environment recommended)
- **Broker / Backend**: Redis (or another broker supported by Celery)
- **Database**: MySQL (configured via `DB_URL` environment variable)
- **Python packages**: see the `pip` install commands below (project does not include `requirements.txt`).

**Quick Setup (Windows PowerShell)**

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

2. Install key dependencies (add others as needed):

```powershell
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv celery redis
# If using the LangChain Groq integration used in `inventory_chain.py`:
pip install langchain-groq langchain-core
```

3. Configure environment variables. Copy the example env and edit:

```powershell
copy .example.env .env
# open .env and set DB_URL, CELERY_BROKER_URL and CELERY_BACKEND_URL
```

Minimum .env keys the app expects:

- `DB_URL` — SQLAlchemy connect string (MySQL) e.g. `mysql+pymysql://user:pass@host:3306/dbname`
- `CELERY_BROKER_URL` — e.g. `redis://localhost:6379/0`
- `CELERY_BACKEND_URL` — e.g. `redis://localhost:6379/0`

**Database**
- The SQLAlchemy `Base` models are in `models.py`.
- The application creates tables on startup using `Base.metadata.create_all(bind=engine)` (in `main.py`).
- Ensure the `DB_URL` connection string is valid and the DB server is reachable.

**Run the API (development)**
- Option A: Use `uvicorn` directly:

```powershell
uvicorn main:app --reload --port 8000
```

- Option B: Run the module (the file `main.py` calls `uvicorn.run` when executed):

```powershell
python main.py
```

The health endpoint is at `GET /`.

**Run Celery worker**
- Start a Redis server (or your chosen broker) first.
- From the repository root run:

```powershell
# point Celery to the module that defines the Celery app instance (module: celery_app)
celery -A celery_app worker --loglevel=info
```

**API Endpoints**
- `GET /` — Health check. Returns a JSON base response.
- `GET /api/inventory/list-with-logs` — Returns inventory items; each item includes its last three `AuditLog` entries.
- `POST /api/audit/start-check` — Start an audit; JSON body: `{ "item_id": <int> }`. This enqueues the Celery task `run_full_inventory_audit`.
- `POST /api/ai/query-audit` — Form field `question` (string). The service forwards the question to the AI chain in `inventory_chain.py`, which returns a status; the app then fetches audit logs with that status.

Example using `curl` (replace host/port as needed):

```powershell
# list inventory
curl "http://127.0.0.1:8000/api/inventory/list-with-logs"

# start check
curl -X POST -H "Content-Type: application/json" -d '{"item_id":1}' "http://127.0.0.1:8000/api/audit/start-check"

# AI query (form data)
curl -X POST -F "question=show me pending audits" "http://127.0.0.1:8000/api/ai/query-audit"
```

**How the pieces fit together**
- `main.py`: FastAPI app and endpoints. Creates DB tables at startup.
- `models.py`: SQLAlchemy models: `InventoryItem` and `AuditLog`.
- `schema.py`: Pydantic schemas used for request/response validation.
- `database.py`: SQLAlchemy engine/session factory and `get_db` dependency.
- `tasks.py`: Celery tasks (notably `run_full_inventory_audit`) that modify audit log statuses in the DB.
- `celery_app.py`: Defines the Celery app and broker/backend configuration.
- `inventory_chain.py`: A LangChain-based chain using `ChatGroq` that parses a natural-language question and extracts an `AuditLogStatus` (e.g., `PENDING`, `SUCCESS`, `FAILED`).
- `utils.py`: Small helpers, including `get_audit_notes_by_status` and a JSON response helper used by endpoints.
- `custom_logger.py` / `logger.py`: Logging configuration (both files provide similar logger setups and write to `app.log`).

**Logging**
- Application logs are written to `app.log` (rotating handler configured).


**Seed this data for quick start**

```sql
-- Insert dummy inventory items
INSERT INTO inventoryitem (item_id, name, quantity, warehouse_location, last_audit_date)
VALUES
(1, 'Steel Rods', 120, 'A1-Section-3', '2025-01-10 10:15:00'),
(2, 'Copper Wires', 450, 'B2-Section-1', '2025-01-12 14:30:00'),
(3, 'Nuts & Bolts', 3000, 'C4-Section-7', '2025-02-01 09:00:00'),
(4, 'Aluminium Sheets', 250, 'A3-Section-2', '2025-01-20 11:45:00'),
(5, 'Plastic Pipes', 780, 'D1-Section-5', '2025-02-05 16:20:00');

-- Insert dummy audit logs for the above items
INSERT INTO auditlog (audit_id, inventory_item_fk, timestamp, status, notes)
VALUES
(1, 1, '2025-01-10 11:00:00', 'SUCCESS', 'Audit completed successfully.'),
(2, 1, '2025-02-01 09:30:00', 'PENDING', 'Next audit scheduled.'),
(3, 2, '2025-01-12 15:00:00', 'SUCCESS', 'Copper wire stock matched accurately.'),
(4, 3, '2025-02-01 10:15:00', 'FAILED', 'Discrepancy found: shortage of 20 units.'),
(5, 4, '2025-01-20 12:00:00', 'SUCCESS', 'Audit OK. All aluminium sheets accounted.'),
(6, 5, '2025-02-05 17:00:00', 'PENDING', 'Awaiting verification from QA team.');
```