from fastapi import FastAPI, Response, Depends, status, Request, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uvicorn
from sqlalchemy.orm import Session, selectinload
from schema import InventoryItemSchema, InventoryCheckSchema, AuditLogSchema
from database import get_db, engine, Base
from models import AuditLog, InventoryItem
import models
from typing import List
from inventory_chain import main_chain
from utils import get_audit_notes_by_status, JsonBaseResponse
from custom_logger import logger
from tasks import run_full_inventory_audit

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def health():
    response = {"message":"The server is working fine",
                "status_code":status.HTTP_200_OK,
                "data" : []}
    return JsonBaseResponse(response)

@app.get("/api/inventory/list-with-logs", response_model=List[InventoryItemSchema])
def get_audit_logs(db:Session = Depends(get_db)):
    inventory = db.query(InventoryItem).options(selectinload(InventoryItem.audits)).all()
    
    # Getting the last three audit logs
    for i in inventory:
        i.audits = i.audits[-3:]
    
    response = {"message":"Data Fetched Successfully",
                "status_code":status.HTTP_200_OK,
                "data" : jsonable_encoder(inventory)}
    
    return JsonBaseResponse(response)
    

@app.post("/api/audit/start-check")
async def start_check(inventory:InventoryCheckSchema):
    run_full_inventory_audit.delay(inventory.item_id)
    response = {"message":"Process Started",
                "status_code":status.HTTP_202_ACCEPTED,
                "data" : []
                }
    return JsonBaseResponse(response)
    
@app.post("/api/ai/query-audit",response_model=List[AuditLogSchema])   
def query_audit(question:str = Form(...)):   
    logger.info(f"Question user asked: {question}")
    response_status = main_chain.invoke({"question":question}).get("status")
    logger.info(f"Status the user is asking for is: {response_status}")
    data = get_audit_notes_by_status(response_status)
    
    response = {
        "message":"Data Fetched Successfully",
        "status_code":status.HTTP_200_OK,
        "data":jsonable_encoder(data)
    }
    
    return JsonBaseResponse(response)
    
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)
