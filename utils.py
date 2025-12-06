from celery_app import celery
from database import SessionLocal
from models import InventoryItem, AuditLog
from audit_enum import AuditLogStatus
from sqlalchemy import update
from fastapi.responses import JSONResponse

from schema import BaseResponseSchema



def get_audit_notes_by_status(status: AuditLogStatus):
    
    db = SessionLocal()
    audit_logs = db.query(AuditLog).filter(AuditLog.status == status).all()
    
    return audit_logs
    
    
    
    
def JsonBaseResponse(reponse:BaseResponseSchema):
    return JSONResponse(
        content=reponse,
        status_code=reponse.get("status_code")
    )