from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text)
    severity = Column(String(50))
    priority = Column(String(50))
    zone = Column(String(100), default="Unassigned")
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship to ResourceAssignment
    assignments = relationship("ResourceAssignment", back_populates="alert")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_name = Column(String(100), unique=True)
    total_quantity = Column(Integer)
    available_quantity = Column(Integer)


class ResourceAssignment(Base):
    __tablename__ = "resource_assignments"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    resource_type = Column(String(100))
    quantity_assigned = Column(Integer)
    
    alert = relationship("Alert", back_populates="assignments")