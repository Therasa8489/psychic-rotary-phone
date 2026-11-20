import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import get_conn, init_db

app = FastAPI(title="Nalla Chennai API")
init_db()

RETENTION_DAYS = {"fine": 730, "accident": 3650, "dispute": 3650, "litter": 90}


def now():
    return datetime.now(timezone.utc)


def audit(conn, actor, action, evidence_id=None):
    conn.execute("INSERT INTO audit_log(actor, action, evidence_id, at) VALUES (?,?,?,?)",
                 (actor, action, evidence_id, now().isoformat()))


class EvidenceIn(BaseModel):
    clip_path: str
    incident_type: str  # fine / accident / dispute / litter


@app.post("/evidence")
def create_evidence(body: EvidenceIn):
    if body.incident_type not in RETENTION_DAYS:
        raise HTTPException(400, "unknown incident_type")
    eid = str(uuid.uuid4())
    try:
        with open(body.clip_path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        digest = None
    retain = now() + timedelta(days=RETENTION_DAYS[body.incident_type])
    hold = 1 if body.incident_type in ("accident", "dispute") else 0
    with get_conn() as c:
        c.execute("INSERT INTO evidence VALUES (?,?,?,?,?,?,?)",
                  (eid, body.clip_path, body.incident_type, digest,
                   now().isoformat(), retain.isoformat(), hold))
        audit(c, "system", "create", eid)
    return {"id": eid, "legal_hold": bool(hold), "sha256": digest}


@app.get("/evidence")
def list_evidence():
    with get_conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM evidence")]


@app.post("/evidence/{eid}/hold")
def set_hold(eid: str, actor: str = "officer"):
    with get_conn() as c:
        cur = c.execute("UPDATE evidence SET legal_hold=1 WHERE id=?", (eid,))
        if cur.rowcount == 0:
            raise HTTPException(404, "not found")
        audit(c, actor, "legal_hold_on", eid)
    return {"id": eid, "legal_hold": True}


@app.post("/admin/cleanup")
def cleanup():
    """Delete only expired evidence that is NOT under legal hold."""
    with get_conn() as c:
        rows = c.execute("SELECT id FROM evidence WHERE legal_hold=0 AND retain_until < ?",
                         (now().isoformat(),)).fetchall()
        for r in rows:
            c.execute("DELETE FROM evidence WHERE id=?", (r["id"],))
            audit(c, "system", "auto_delete", r["id"])
    return {"deleted": len(rows)}
