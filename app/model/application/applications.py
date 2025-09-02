from sqlalchemy import Integer, Column, ForeignKey, Text

from model.base import DateTimeMixin, HRSystemBase


class Application(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(ForeignKey("t_jobs.id"), nullable=False)
    candidate_id = Column(ForeignKey("t_candidates.id"), nullable=False)
    resume_id = Column(ForeignKey("t_resumes.id"), nullable=False)
    status = Column(Integer, default=1, nullable=False, comment="1: Applied, 3: Screening, 5: Shortlisted, ...")
    score_overall = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)
    created_by = Column(Integer, nullable=True, comment="User ID")
    updated_by = Column(Integer, nullable=True, comment="User ID")
