from sqlalchemy import Integer, String, Column, Boolean, ForeignKey

from model.base import HRSystemBase, DateTimeMixin


class JobRoleSkill(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_job_role_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_role_id = Column(ForeignKey("m_job_roles.id"), nullable=False)
    skill_id = Column(ForeignKey("m_skills.id"), nullable=False)
