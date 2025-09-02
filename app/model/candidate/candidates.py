from sqlalchemy import Integer, Column, String, Text

from app.model.base import DateTimeMixin, HRSystemBase


class Candidate(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    note = Column(Text, nullable=True)