from sqlalchemy import Column, Integer, ForeignKey

from model.base import DateTimeMixin, HRSystemBase


class JobRequirementSkill(HRSystemBase, DateTimeMixin):
    """Junction table for job requirements and skills"""

    __tablename__ = "t_job_requirement_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_requirement_id = Column(
        ForeignKey("t_job_requirements.id"),
        nullable=False,
        comment="Reference to job requirement",
    )
    skill_id = Column(
        ForeignKey("m_skills.id"),
        nullable=False,
        comment="Reference to skill",
    )
