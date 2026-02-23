from sqlalchemy.orm import Session
from app import models

class ResourceAgent:
    def allocate(self, db: Session, alert_id: int, r_type: str, qty: int):
        if qty <= 0:
            return f"No {r_type} requested."

        # Find the resource in inventory
        resource = db.query(models.Resource).filter(
            models.Resource.resource_name.like(f"%{r_type}%")
        ).first()

        if resource and resource.available_quantity >= qty:
            # Deduct from inventory
            resource.available_quantity -= qty
            
            # Record the assignment
            assignment = models.ResourceAssignment(
                alert_id=alert_id,
                resource_type=resource.resource_name,
                quantity_assigned=qty
            )
            db.add(assignment)
            db.commit()
            return f"Successfully dispatched {qty} {resource.resource_name}(s)."
        
        return f"Failed: Insufficient {r_type} in stock."