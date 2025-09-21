from sqlalchemy import Integer, Column, String, Text, Boolean

from model.base import DateTimeMixin, HRSystemBase


class Candidate(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    is_blocklisted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the candidate is blocklisted",
    )
    note = Column(Text, nullable=True)
