"""TriageBot API + web UI."""
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app import config, db
from app.triage import triage_ticket

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="TriageBot", version=config.APP_VERSION,
              description="AI-powered customer support ticket triage")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_requests: dict = defaultdict(deque)


@app.on_event("startup")
def startup() -> None:
    db.init_db()


# ---------- models ----------
class TicketIn(BaseModel):
    customer_name: str
    email: str
    subject: str = ""
    message: str


class OverrideIn(BaseModel):
    priority: Optional[str] = None
    category: Optional[str] = None
    agent_name: Optional[str] = None


# ---------- helpers ----------
def check_rate_limit(request: Request) -> None:
    client = request.headers.get("x-forwarded-for") or request.client.host
    now = time.time()
    window = _requests[client]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= config.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many requests. Try again in a minute.")
    window.append(now)


# ---------- routes ----------
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": config.APP_VERSION, "llm_mode": config.LLM_MODE}


@app.post("/api/tickets", status_code=201)
def create_ticket(payload: TicketIn, request: Request):
    check_rate_limit(request)
    if not payload.customer_name.strip():
        raise HTTPException(status_code=400, detail="customer_name is required")
    if len(payload.subject) > config.MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail="message is too long (max 5000 characters)")

    result = triage_ticket(payload.customer_name, payload.subject, payload.message)
    ticket_id = db.insert_ticket({
        "customer_name": payload.customer_name,
        "email": payload.email,
        "subject": payload.subject,
        "message": payload.message,
        **result,
    })
    return db.get_ticket(ticket_id)


@app.get("/api/tickets")
def list_tickets(priority: Optional[str] = None, category: Optional[str] = None,
                 status: Optional[str] = None, q: Optional[str] = None):
    return db.list_tickets(priority=priority, category=category, status=status, q=q)


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket["audit_log"] = db.get_audit(ticket_id)
    return ticket


@app.patch("/api/tickets/{ticket_id}/override")
def override_ticket(ticket_id: int, payload: OverrideIn):
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    changes = {}
    if payload.priority:
        changes["priority"] = payload.priority
    if payload.category:
        changes["category"] = payload.category
    if not changes:
        raise HTTPException(status_code=400, detail="Nothing to override")

    changes["status"] = "reviewed"
    db.update_ticket(ticket_id, changes)
    old = f"{ticket['priority']}/{ticket['category']}"
    new = f"{changes.get('priority', ticket['priority'])}/{changes.get('category', ticket['category'])}"
    db.add_audit(ticket_id, "override", old, new, payload.agent_name)
    return db.get_ticket(ticket_id)


@app.get("/api/metrics")
def metrics():
    total = db.count("SELECT COUNT(*) FROM tickets")
    overrides = db.count("SELECT COUNT(*) FROM audit_log WHERE action = 'override'")
    by_priority = {
        p: db.count(f"SELECT COUNT(*) FROM tickets WHERE priority = '{p}'") for p in config.PRIORITIES
    }
    return {
        "total_tickets": total,
        "overrides": overrides,
        "ai_accuracy": round((total - overrides) / total, 3) if total else None,
        "by_priority": by_priority,
    }
