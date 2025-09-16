from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from model.base import DateTimeMixin, HRSystemBase


class User(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)
    role_id = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    jwt_tokens = relationship("JWTToken", back_populates="user")



