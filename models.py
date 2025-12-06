from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, text, Enum
from sqlalchemy.orm import relationship
from database import Base
from audit_enum import AuditLogStatus
from typing import List

class InventoryItem(Base):
    __tablename__ = "inventoryitem"
    
    item_id = Column(Integer, primary_key = True, nullable = False)
    name = Column(String(50))
    quantity = Column(Integer)
    warehouse_location = Column(String(50))
    last_audit_date = Column(TIMESTAMP(timezone=True))
    
    audits = relationship("AuditLog", back_populates="inventory")
    
    model_config = {
        "from_attributes": True
    }
    
class AuditLog(Base):
    __tablename__ = "auditlog"
    
    audit_id = Column(Integer, primary_key = True, nullable = False)
    inventory_item_fk = Column(Integer, ForeignKey("inventoryitem.item_id"))
    timestamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    status = Column(Enum(AuditLogStatus),default = AuditLogStatus.PENDING)
    notes = Column(String(255))
    
    inventory = relationship("InventoryItem", back_populates="audits")
    
    model_config = {
        "from_attributes": True
    }
    
