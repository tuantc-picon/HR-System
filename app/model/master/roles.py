from sqlalchemy import Column, Integer, String, Boolean

from model.base import DateTimeMixin, HRSystemBase


class Role(HRSystemBase, DateTimeMixin):
    __tablename__ = "m_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)