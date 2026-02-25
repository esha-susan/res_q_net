from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    severity = Column(String(50))
    status = Column(String(50), default="Pending") # For IVR
    assignments = relationship("ResourceAssignment", back_populates="alert")

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), unique=True)
    available_quantity = Column(Integer) # We will use this for logic

class ResourceAssignment(Base):
    __tablename__ = "resource_assignments"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    resource_id = Column(Integer) # Links to Resource.id
    resource_type = Column(String(100))
    quantity_assigned = Column(Integer)
    status = Column(String(50), default="Pending") # Added for confirmation logic
    
    alert = relationship("Alert", back_populates="assignments")