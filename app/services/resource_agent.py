from sqlalchemy.orm import Session
from app import models

class ResourceAgent:
    def allocate(self, db: Session, alert_id: int, res_type: str, qty: int, status: str = "Pending"):
        # Find the resource in the database
        resource = db.query(models.Resource).filter(models.Resource.type == res_type).first()
        
        if not resource:
            print(f"Error: Resource {res_type} not found.")
            return {"type": res_type, "status": "Failed"}

        # Create the assignment
        new_assignment = models.ResourceAssignment(
            alert_id=alert_id,
            resource_id=resource.id,
            resource_type=res_type,
            quantity_assigned=qty,
            status=status
        )
        
        db.add(new_assignment)
        db.commit()
        return {"type": res_type, "qty": qty, "status": status}