from sqlalchemy import Integer, String, Column, Boolean, ForeignKey

from model.base import HRSystemBase, DateTimeMixin


class Skill(HRSystemBase, DateTimeMixin):
    __tablename__ = "m_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_role_id = Column(ForeignKey("m_job_roles.id"), nullable=True, comment="Reference to job role master data")
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)