from sqlalchemy import Column, Integer, String, Boolean

from app.model.base import DateTimeMixin, HRSystemBase


class Certificate(HRSystemBase, DateTimeMixin):
    __tablename__ = "m_certificates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    category = Column(Integer, default=1, nullable=False)
