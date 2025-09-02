from sqlalchemy import Column, Integer, ForeignKey, String

from model.base import DateTimeMixin, HRSystemBase


class Resume(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(ForeignKey("t_candidates.id"), nullable=False)
    file_path = Column(String, nullable=False)
    note = Column(String, nullable=True)

