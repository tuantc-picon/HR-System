from sqlalchemy import Column, Integer, String, Boolean

from app.model.base import DateTimeMixin, HRSystemBase


class BlackList(HRSystemBase, DateTimeMixin):
    __tablename__ = "m_black_lists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    category = Column(Integer, default=1, nullable=False, comment="1: Candidate, 3: Company")
