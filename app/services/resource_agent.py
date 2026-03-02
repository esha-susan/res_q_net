from sqlalchemy.orm import Session
from app import models

class ResourceAgent:
    def allocate(self, db: Session, alert_id: int, res_type: str, qty: int, status: str = "Pending"):
        # Case-insensitive lookup
        resource = db.query(models.Resource).filter(models.Resource.type.ilike(res_type)).first()
        
        if not resource:
            print(f"Error: Resource {res_type} not found.")
            return {"type": res_type, "status": "Failed"}

        # Create the assignment
        new_assignment = models.ResourceAssignment(
            alert_id=alert_id,
            resource_id=resource.id,
            resource_type=resource.type, # Use type from DB to maintain consistency
            quantity_assigned=qty,
            status=status
        )
        
        try:
            db.add(new_assignment)
            db.commit()
            db.refresh(new_assignment)
            return {"type": res_type, "qty": qty, "status": status}
        except Exception as e:
            db.rollback()
            print(f"DB Error: {e}")
            return {"status": "Error"}