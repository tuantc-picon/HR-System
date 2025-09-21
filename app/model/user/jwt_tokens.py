from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from model.base import DateTimeMixin, HRSystemBase


class JWTToken(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_jwt_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("t_users.id"), nullable=False)
    token_type = Column(String(20), nullable=False)  # 'access' or 'refresh'
    token_hash = Column(String(255), nullable=False, unique=True)
    jti = Column(
        String(36), nullable=False, unique=True
    )  # JWT ID for token identification
    is_blacklisted = Column(Boolean, default=False, nullable=False)
    expires_at = Column(Integer, nullable=False)  # Unix timestamp

    # Relationship
    user = relationship("User", back_populates="jwt_tokens")
