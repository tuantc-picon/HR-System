from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean

from model.base import DateTimeMixin, HRSystemBase


class Job(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    job_role_id = Column(
        ForeignKey("m_job_roles.id"),
        nullable=True,
        comment="Reference to job role master data",
    )
    area = Column(
        Integer,
        default=1,
        nullable=False,
        comment="1: Da Nang, 3: Ho Chi Minh, 5: Hanoi",
    )
    employment_type = Column(
        Integer,
        default=1,
        nullable=False,
        comment="1: Full-time, 3: Part-time, 5: Fresher, 7: Internship, 9: Vendor",
    )
    status = Column(
        Integer,
        default=1,
        nullable=False,
        comment="1: Draft, 3: Open, 5: Closed, 7: Cancelled",
    )
    application_deadline = Column(
        DateTime(timezone=True), nullable=True, comment="Deadline for job applications"
    )
    description = Column(Text, nullable=True)
    source = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
