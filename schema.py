from pydantic import BaseModel
from datetime import datetime
from audit_enum import AuditLogStatus
from typing import List, Any, Optional
from fastapi import status


class AuditLogSchema(BaseModel):
    audit_id: int
    timestamp: datetime
    status: AuditLogStatus
    notes: str
    
class  InventoryItemSchema(BaseModel):
    item_id: int
    name: str
    quantity: int
    warehouse_location: str
    last_audit_date: datetime
    
    audits: List[AuditLogSchema]
    
class InventoryCheckSchema(BaseModel):
    item_id: int
    
    
class BaseResponseSchema(BaseModel):
    data: Optional[Any] = None
    status_code:status
    message:str
    
    model_config = {
        "arbitrary_types_allowed": True 
    }