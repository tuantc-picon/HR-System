from sqlalchemy import Column, Integer, Text, ForeignKey

from app.model.base import DateTimeMixin, HRSystemBase


class JobRequirement(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_job_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(ForeignKey("t_jobs.id"), nullable=False)
    min_experience = Column(Integer, nullable=True)
    max_experience = Column(Integer, nullable=True)
    min_salary = Column(Integer, nullable=True)
    max_salary = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)