from app.db.base_class import Base  # Importar la Base declarativa única
from app.db.models.organization import Organization
from app.db.models.user import User
from app.db.models.role import Role
from app.db.models.asset import Asset
from app.db.models.risk import Risk
from app.db.models.control import Control
from app.db.models.risk_control import risk_controls
from app.db.models.activity_log import ActivityLog
from app.db.models.area import Area