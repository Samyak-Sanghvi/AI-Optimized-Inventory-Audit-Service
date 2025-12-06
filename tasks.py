
from celery_app import celery
from database import SessionLocal
from models import InventoryItem, AuditLog
from audit_enum import AuditLogStatus
from sqlalchemy import update
from custom_logger import logger



@celery.task(bind=True, acks_late=True, max_retries=3)
def run_full_inventory_audit(self, item_id):
    logger.info(f"Task started: run_full_inventory_audit | item_id={item_id}")
    db = SessionLocal()
    try:
        audits_query = db.query(AuditLog).filter(AuditLog.inventory_item_fk == item_id)
        audits_count = audits_query.count()
        logger.info(f"Found {audits_count} audit log(s) for item_id={item_id}")
        if audits_count == 0:
            logger.warning(f"No audit logs found for item_id={item_id}, nothing to update.")
        else:
            audits_query.update({AuditLog.status: AuditLogStatus.SUCCESS},synchronize_session=False)
            db.commit()
            logger.info(f"Successfully updated {audits_count} audit log(s) to SUCCESS for item_id={item_id}")
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=10)
    finally:
        db.close()