from sqlalchemy import Column, Integer, ForeignKey, Table
from app.db.base_class import Base

risk_controls = Table(
    "risk_controls",
    Base.metadata,
    Column("risk_id", Integer, ForeignKey("risks.id", ondelete="CASCADE"), primary_key=True),
    Column("control_id", Integer, ForeignKey("controls.id", ondelete="CASCADE"), primary_key=True),
)