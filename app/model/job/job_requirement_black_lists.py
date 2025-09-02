from sqlalchemy import Column, Integer, ForeignKey

from app.model.base import DateTimeMixin, HRSystemBase


class JobRequirementBlackList(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_job_requirement_black_lists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_requirement_id = Column(ForeignKey("t_job_requirements.id"), nullable=False)
    black_list_id = Column(ForeignKey("m_black_lists.id"), nullable=False)