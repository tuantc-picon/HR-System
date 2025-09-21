from sqlalchemy import Integer, String, Column, Boolean

from model.base import HRSystemBase, DateTimeMixin


class JobRole(HRSystemBase, DateTimeMixin):
    __tablename__ = "m_job_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
