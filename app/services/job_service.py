from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.job.jobs import Job
from model.job.job_requirements import JobRequirement
from model.master.job_roles import JobRole
from model.master.skills import Skill
from model.master.certificates import Certificate
from model.job.job_requirement_certificates import JobRequirementCertificate
from model.job.job_requirement_black_lists import JobRequirementBlackList
from model.job.job_skills import JobSkill
from model.master.black_lists import BlackList
from services.base_service import BaseService
from schema.request.job_schemas import JobCreateRequest, JobUpdateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status


class JobService(BaseService[Job]):
    def __init__(self):
        super().__init__(Job)

    def create_job(self, db: Session, job_data: JobCreateRequest) -> Dict[str, Any]:
        """Create a new job with requirements, skills, and certificates"""
        try:
            # Validate job_role_id if provided
            if job_data.job_role_id:
                job_role = db.query(JobRole).filter(JobRole.id == job_data.job_role_id).first()
                if not job_role:
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Job role not found"
                    )
                if not job_role.is_active:
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Job role is not active"
                    )

            # Validate skill IDs if provided
            if job_data.skill_ids:
                skills = db.query(Skill).filter(Skill.id.in_(job_data.skill_ids)).all()
                if len(skills) != len(job_data.skill_ids):
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="One or more skills not found"
                    )

            # Create the job first
            job_dict = job_data.model_dump(exclude={"job_requirements", "skill_ids", "include_black_list_check"})
            job = self.create(db, job_dict)

            # Create job requirements if provided
            job_requirements = []
            if job_data.job_requirements:
                for req_data in job_data.job_requirements:
                    # Create job requirement
                    requirement = JobRequirement(
                        job_id=job.id,
                        min_experience=req_data.min_experience,
                        max_experience=req_data.max_experience,
                        min_salary=req_data.min_salary,
                        max_salary=req_data.max_salary,
                        note=req_data.note
                    )
                    db.add(requirement)
                    db.flush()  # Get the ID
                    job_requirements.append(requirement)

                    # Create certificate associations if provided
                    if req_data.certificate_ids:
                        for cert_id in req_data.certificate_ids:
                            cert_assoc = JobRequirementCertificate(
                                job_requirement_id=requirement.id,
                                certificate_id=cert_id
                            )
                            db.add(cert_assoc)

                    # Create black list associations if provided
                    if req_data.black_list_ids:
                        for bl_id in req_data.black_list_ids:
                            bl_assoc = JobRequirementBlackList(
                                job_requirement_id=requirement.id,
                                black_list_id=bl_id
                            )
                            db.add(bl_assoc)

            # Create job skill associations if provided
            if job_data.skill_ids:
                for skill_id in job_data.skill_ids:
                    job_skill = JobSkill(
                        job_id=job.id,
                        skill_id=skill_id
                    )
                    db.add(job_skill)

            db.commit()

            # Return job with related data
            return {
                "job": job,
                "job_requirements": job_requirements,
                "skill_ids": job_data.skill_ids or [],
                "include_black_list_check": job_data.include_black_list_check
            }

        except Exception as e:
            db.rollback()
            if isinstance(e, HRSystemBaseException):
                raise e
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to create job: {str(e)}"
            )

    def update_job(self, db: Session, job_id: int, job_data: JobUpdateRequest) -> Optional[Dict[str, Any]]:
        """Update job with requirements, skills, and certificates"""
        try:
            # Check if job exists
            job = self.get_by_id(db, job_id)
            if not job:
                return None

            # Validate job_role_id if provided
            if job_data.job_role_id:
                job_role = db.query(JobRole).filter(JobRole.id == job_data.job_role_id).first()
                if not job_role:
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Job role not found"
                    )
                if not job_role.is_active:
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Job role is not active"
                    )

            # Validate skill IDs if provided
            if job_data.skill_ids is not None:
                if job_data.skill_ids:
                    skills = db.query(Skill).filter(Skill.id.in_(job_data.skill_ids)).all()
                    if len(skills) != len(job_data.skill_ids):
                        raise HRSystemBaseException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            message="One or more skills not found"
                        )

            # Update basic job fields
            job_dict = job_data.model_dump(exclude_unset=True, exclude={"job_requirements", "skill_ids", "include_black_list_check"})
            if job_dict:
                updated_job = self.update(db, job_id, job_dict)
                if not updated_job:
                    return None
                job = updated_job

            # Update job requirements if provided
            job_requirements = []
            if job_data.job_requirements is not None:
                # Delete existing requirements
                db.query(JobRequirementCertificate).filter(
                    JobRequirementCertificate.job_requirement_id.in_(
                        db.query(JobRequirement.id).filter(JobRequirement.job_id == job_id)
                    )
                ).delete(synchronize_session=False)

                db.query(JobRequirementBlackList).filter(
                    JobRequirementBlackList.job_requirement_id.in_(
                        db.query(JobRequirement.id).filter(JobRequirement.job_id == job_id)
                    )
                ).delete(synchronize_session=False)

                db.query(JobRequirement).filter(JobRequirement.job_id == job_id).delete()

                # Create new requirements
                for req_data in job_data.job_requirements:
                    requirement = JobRequirement(
                        job_id=job.id,
                        min_experience=req_data.min_experience,
                        max_experience=req_data.max_experience,
                        min_salary=req_data.min_salary,
                        max_salary=req_data.max_salary,
                        note=req_data.note
                    )
                    db.add(requirement)
                    db.flush()
                    job_requirements.append(requirement)

                    # Create certificate associations
                    if req_data.certificate_ids:
                        for cert_id in req_data.certificate_ids:
                            cert_assoc = JobRequirementCertificate(
                                job_requirement_id=requirement.id,
                                certificate_id=cert_id
                            )
                            db.add(cert_assoc)

                    # Create black list associations
                    if req_data.black_list_ids:
                        for bl_id in req_data.black_list_ids:
                            bl_assoc = JobRequirementBlackList(
                                job_requirement_id=requirement.id,
                                black_list_id=bl_id
                            )
                            db.add(bl_assoc)

            # Update job skills if provided
            if job_data.skill_ids is not None:
                # Delete existing job skills
                db.query(JobSkill).filter(JobSkill.job_id == job_id).delete()

                # Create new job skills
                for skill_id in job_data.skill_ids:
                    job_skill = JobSkill(
                        job_id=job.id,
                        skill_id=skill_id
                    )
                    db.add(job_skill)

            db.commit()

            # Return updated job with related data
            return {
                "job": job,
                "job_requirements": job_requirements,
                "skill_ids": job_data.skill_ids,
                "include_black_list_check": job_data.include_black_list_check
            }

        except Exception as e:
            db.rollback()
            if isinstance(e, HRSystemBaseException):
                raise e
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to update job: {str(e)}"
            )

    def get_jobs_by_area(self, db: Session, area: int) -> List[Job]:
        """Get jobs by area (1: Da Nang, 3: Ho Chi Minh, 5: Hanoi)"""
        return db.query(Job).filter(
            and_(
                Job.area == area,
                Job.deleted_at.is_(None)
            )
        ).all()

    def get_jobs_by_employment_type(self, db: Session, employment_type: int) -> List[Job]:
        """Get jobs by employment type"""
        return db.query(Job).filter(
            and_(
                Job.employment_type == employment_type,
                Job.deleted_at.is_(None)
            )
        ).all()

    def get_jobs_by_creator(self, db: Session, created_by: int) -> List[Job]:
        """Get jobs created by a specific user"""
        return db.query(Job).filter(
            and_(
                Job.created_by == created_by,
                Job.deleted_at.is_(None)
            )
        ).all()

    def search_jobs_by_title(self, db: Session, title_keyword: str) -> List[Job]:
        """Search jobs by title keyword"""
        return db.query(Job).filter(
            and_(
                Job.title.ilike(f"%{title_keyword}%"),
                Job.deleted_at.is_(None)
            )
        ).all()

    def get_job_with_details(self, db: Session, job_id: int) -> Optional[Dict[str, Any]]:
        """Get job with job role and requirements details using separate queries"""
        # Get the job first
        job = db.query(Job).filter(
            and_(
                Job.id == job_id,
                Job.deleted_at.is_(None)
            )
        ).first()

        if not job:
            return None

        # Get job role if exists
        job_role = None
        if job.job_role_id:
            job_role = db.query(JobRole).filter(JobRole.id == job.job_role_id).first()

        # Get job requirements
        job_requirements = db.query(JobRequirement).filter(
            and_(
                JobRequirement.job_id == job.id,
                JobRequirement.deleted_at.is_(None)
            )
        ).all()

        return {
            "job": job,
            "job_role": job_role,
            "job_requirements": job_requirements
        }

    def get_jobs_by_role(self, db: Session, job_role_id: int) -> List[Job]:
        """Get jobs by job role"""
        return db.query(Job).filter(
            and_(
                Job.job_role_id == job_role_id,
                Job.deleted_at.is_(None)
            )
        ).all()

    def get_all_with_details(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all jobs with job role and requirements details using separate queries"""
        # Get jobs first
        jobs = db.query(Job).filter(
            Job.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()

        if not jobs:
            return []

        # Get all job IDs
        job_ids = [job.id for job in jobs]

        # Get all job roles for these jobs
        job_role_ids = [job.job_role_id for job in jobs if job.job_role_id]
        job_roles_dict = {}
        if job_role_ids:
            job_roles = db.query(JobRole).filter(JobRole.id.in_(job_role_ids)).all()
            job_roles_dict = {role.id: role for role in job_roles}

        # Get all job requirements for these jobs
        job_requirements = db.query(JobRequirement).filter(
            and_(
                JobRequirement.job_id.in_(job_ids),
                JobRequirement.deleted_at.is_(None)
            )
        ).all()

        # Group requirements by job_id
        requirements_dict = {}
        for req in job_requirements:
            if req.job_id not in requirements_dict:
                requirements_dict[req.job_id] = []
            requirements_dict[req.job_id].append(req)

        # Combine data
        result = []
        for job in jobs:
            result.append({
                "job": job,
                "job_role": job_roles_dict.get(job.job_role_id),
                "job_requirements": requirements_dict.get(job.id, [])
            })

        return result

    def get_job_skills(self, db: Session, job_id: int) -> List[Skill]:
        """Get skills for a job through job_skills table"""
        # Get skill IDs from job_skills table
        job_skill_associations = db.query(JobSkill).filter(
            and_(
                JobSkill.job_id == job_id,
                JobSkill.deleted_at.is_(None)
            )
        ).all()

        if not job_skill_associations:
            return []

        # Get skills
        skill_ids = [assoc.skill_id for assoc in job_skill_associations]
        return db.query(Skill).filter(
            and_(
                Skill.id.in_(skill_ids),
                Skill.is_active == True,
                Skill.deleted_at.is_(None)
            )
        ).all()

    def get_job_certificates(self, db: Session, job_id: int) -> List[Certificate]:
        """Get certificates required for a job"""
        # Get job requirements first
        job_requirements = db.query(JobRequirement).filter(
            and_(
                JobRequirement.job_id == job_id,
                JobRequirement.deleted_at.is_(None)
            )
        ).all()

        if not job_requirements:
            return []

        # Get certificate IDs from job requirement certificates
        req_ids = [req.id for req in job_requirements]
        cert_associations = db.query(JobRequirementCertificate).filter(
            and_(
                JobRequirementCertificate.job_requirement_id.in_(req_ids),
                JobRequirementCertificate.deleted_at.is_(None)
            )
        ).all()

        if not cert_associations:
            return []

        # Get certificates
        cert_ids = [assoc.certificate_id for assoc in cert_associations]
        return db.query(Certificate).filter(
            and_(
                Certificate.id.in_(cert_ids),
                Certificate.is_active == True,
                Certificate.deleted_at.is_(None)
            )
        ).all()

    def get_job_black_lists(self, db: Session, job_id: int) -> List[BlackList]:
        """Get black lists for a job"""
        # Get job requirements first
        job_requirements = db.query(JobRequirement).filter(
            and_(
                JobRequirement.job_id == job_id,
                JobRequirement.deleted_at.is_(None)
            )
        ).all()

        if not job_requirements:
            return []

        # Get black list IDs from job requirement black lists
        req_ids = [req.id for req in job_requirements]
        bl_associations = db.query(JobRequirementBlackList).filter(
            and_(
                JobRequirementBlackList.job_requirement_id.in_(req_ids),
                JobRequirementBlackList.deleted_at.is_(None)
            )
        ).all()

        if not bl_associations:
            return []

        # Get black lists
        bl_ids = [assoc.black_list_id for assoc in bl_associations]
        return db.query(BlackList).filter(
            and_(
                BlackList.id.in_(bl_ids),
                BlackList.is_active == True,
                BlackList.deleted_at.is_(None)
            )
        ).all()


# Create singleton instance
job_service = JobService()
