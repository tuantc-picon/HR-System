from sqlalchemy import Column, Integer, String, Boolean, Text

from model.base import DateTimeMixin, HRSystemBase


class Job(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    area = Column(Integer, default=1, nullable=False, comment="1: Da Nang, 3: Ho Chi Minh, 5: Hanoi")
    employment_type = Column(Integer, default=1, nullable=False, comment="1: Full-time, 3: Part-time, 5: Fresher, 7: Internship, 9: Vendor")
    description = Column(Text, nullable=True)
    source = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)