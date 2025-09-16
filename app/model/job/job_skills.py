from sqlalchemy import Column, Integer, ForeignKey

from model.base import DateTimeMixin, HRSystemBase


class JobSkill(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_job_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(ForeignKey("t_jobs.id"), nullable=False)
    skill_id = Column(ForeignKey("m_skills.id"), nullable=False)
