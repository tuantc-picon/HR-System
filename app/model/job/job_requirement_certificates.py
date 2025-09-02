from sqlalchemy import Column, Integer, ForeignKey

from model.base import DateTimeMixin, HRSystemBase


class JobRequirementCertificate(HRSystemBase, DateTimeMixin):
    __tablename__ = "t_job_requirement_certificates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_requirement_id = Column(ForeignKey("t_job_requirements.id"), nullable=False)
    certificate_id = Column(ForeignKey("m_certificates.id"), nullable=False)


