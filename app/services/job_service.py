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

# JobRoleSkill removed - using direct FK in m_skills table
from model.job.job_requirement_skills import JobRequirementSkill
from model.job.job_skills import JobSkill
from model.master.black_lists import BlackList
from model.application.applications import Application
from model.candidate.candidates import Candidate
from model.candidate.resumes import Resume
from services.base_service import BaseService
from services.file_upload_service import file_upload_service
from schema.request.job_schemas import JobCreateRequest, JobUpdateRequest
from schema.response.job_schemas import ResumeFileInfo, ApplicationResumeInfo
from core.common.exceptions import HRSystemBaseException
from starlette import status
from config import UPLOAD_CLOUD_TARGET


class JobService(BaseService[Job]):
    def __init__(self):
        super().__init__(Job)

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Job]:
        """Get all jobs with optional filtering (excluding soft deleted)"""
        query = db.query(self.model).filter(self.model.deleted_at.is_(None))

        if filters:
            for field, value in filters.items():
                if value is not None and hasattr(self.model, field):
                    if field == "title":
                        # Use ILIKE for case-insensitive partial matching on title
                        query = query.filter(
                            getattr(self.model, field).ilike(f"%{value}%")
                        )
                    else:
                        # Exact match for other fields
                        query = query.filter(getattr(self.model, field) == value)

        return query.offset(skip).limit(limit).all()

    def create_job(self, db: Session, job_data: JobCreateRequest) -> Dict[str, Any]:
        """Create a new job with requirements and selected skills"""
        try:
            # Create the job first
            job_dict = job_data.model_dump(
                exclude={"job_requirements", "include_black_list_check"}
            )
            job = self.create(db, job_dict)

            # Create job requirements if provided
            job_requirements = []
            if job_data.job_requirements:
                for req_data in job_data.job_requirements:
                    # Validate job_role_id if provided
                    if req_data.job_role_id:
                        job_role = (
                            db.query(JobRole)
                            .filter(JobRole.id == req_data.job_role_id)
                            .first()
                        )
                        if not job_role:
                            raise HRSystemBaseException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                message="Job role not found",
                            )
                        if not job_role.is_active:
                            raise HRSystemBaseException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                message="Job role is not active",
                            )

                    # Create job requirement
                    requirement = JobRequirement(
                        job_id=job.id,
                        job_role_id=req_data.job_role_id,
                        min_experience=req_data.min_experience,
                        max_experience=req_data.max_experience,
                        min_salary=req_data.min_salary,
                        max_salary=req_data.max_salary,
                        note=req_data.note,
                    )
                    db.add(requirement)
                    db.flush()  # Get the ID
                    job_requirements.append(requirement)

                    # Create skill associations if provided
                    if req_data.skill_ids:
                        # Validate skills exist and are active
                        skills = (
                            db.query(Skill)
                            .filter(
                                and_(
                                    Skill.id.in_(req_data.skill_ids),
                                    Skill.is_active == True,
                                    Skill.deleted_at.is_(None),
                                )
                            )
                            .all()
                        )

                        if len(skills) != len(req_data.skill_ids):
                            raise HRSystemBaseException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                message="One or more skills not found or inactive",
                            )

                        # If job_role_id is specified, validate skills belong to that job role
                        if req_data.job_role_id:
                            # Check skills directly using job_role_id FK in m_skills
                            valid_skills = (
                                db.query(Skill)
                                .filter(
                                    and_(
                                        Skill.job_role_id == req_data.job_role_id,
                                        Skill.id.in_(req_data.skill_ids),
                                        Skill.is_active == True,
                                        Skill.deleted_at.is_(None),
                                    )
                                )
                                .all()
                            )

                            valid_skill_ids = {skill.id for skill in valid_skills}
                            if not set(req_data.skill_ids).issubset(valid_skill_ids):
                                raise HRSystemBaseException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    message="Some skills are not associated with the specified job role",
                                )

                        # Create skill associations
                        for skill_id in req_data.skill_ids:
                            skill_assoc = JobRequirementSkill(
                                job_requirement_id=requirement.id,
                                skill_id=skill_id,
                            )
                            db.add(skill_assoc)

                    # Create certificate associations if provided
                    if req_data.certificate_ids:
                        for cert_id in req_data.certificate_ids:
                            cert_assoc = JobRequirementCertificate(
                                job_requirement_id=requirement.id,
                                certificate_id=cert_id,
                            )
                            db.add(cert_assoc)

                    # Create black list associations if provided
                    if req_data.black_list_ids:
                        for bl_id in req_data.black_list_ids:
                            bl_assoc = JobRequirementBlackList(
                                job_requirement_id=requirement.id, black_list_id=bl_id
                            )
                            db.add(bl_assoc)

            db.commit()

            # Return job with related data
            return {
                "job": job,
                "job_requirements": job_requirements,
                "include_black_list_check": job_data.include_black_list_check,
            }

        except Exception as e:
            db.rollback()
            if isinstance(e, HRSystemBaseException):
                raise e
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to create job: {str(e)}",
            )

    def update_job(
        self, db: Session, job_id: int, job_data: JobUpdateRequest
    ) -> Optional[Dict[str, Any]]:
        """Update job with requirements, skills, and certificates"""
        try:
            # Check if job exists
            job = self.get_by_id(db, job_id)
            if not job:
                return None

            # Update basic job fields
            job_dict = job_data.model_dump(
                exclude_unset=True,
                exclude={"job_requirements", "include_black_list_check"},
            )
            if job_dict:
                updated_job = self.update(db, job_id, job_dict)
                if not updated_job:
                    return None
                job = updated_job

            # Update job requirements if provided
            job_requirements = []
            if job_data.job_requirements is not None:
                # Delete existing requirements and their associations

                # Delete skill associations first
                db.query(JobRequirementSkill).filter(
                    JobRequirementSkill.job_requirement_id.in_(
                        db.query(JobRequirement.id).filter(
                            JobRequirement.job_id == job_id
                        )
                    )
                ).delete(synchronize_session=False)

                db.query(JobRequirementCertificate).filter(
                    JobRequirementCertificate.job_requirement_id.in_(
                        db.query(JobRequirement.id).filter(
                            JobRequirement.job_id == job_id
                        )
                    )
                ).delete(synchronize_session=False)

                db.query(JobRequirementBlackList).filter(
                    JobRequirementBlackList.job_requirement_id.in_(
                        db.query(JobRequirement.id).filter(
                            JobRequirement.job_id == job_id
                        )
                    )
                ).delete(synchronize_session=False)

                db.query(JobRequirement).filter(
                    JobRequirement.job_id == job_id
                ).delete()

                # Create new requirements
                for req_data in job_data.job_requirements:
                    # Validate job_role_id if provided
                    if req_data.job_role_id:
                        job_role = (
                            db.query(JobRole)
                            .filter(JobRole.id == req_data.job_role_id)
                            .first()
                        )
                        if not job_role:
                            raise HRSystemBaseException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                message="Job role not found",
                            )
                        if not job_role.is_active:
                            raise HRSystemBaseException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                message="Job role is not active",
                            )

                    # Create job requirement
                    requirement = JobRequirement(
                        job_id=job.id,
                        job_role_id=req_data.job_role_id,
                        min_experience=req_data.min_experience,
                        max_experience=req_data.max_experience,
                        min_salary=req_data.min_salary,
                        max_salary=req_data.max_salary,
                        note=req_data.note,
                    )
                    db.add(requirement)
                    db.flush()  # Get the ID
                    job_requirements.append(requirement)

                    # Create skill associations if provided
                    if req_data.skill_ids:
                        # Validate skills exist and are active
                        skills = (
                            db.query(Skill)
                            .filter(
                                and_(
                                    Skill.id.in_(req_data.skill_ids),
                                    Skill.is_active == True,
                                    Skill.deleted_at.is_(None),
                                )
                            )
                            .all()
                        )

                        if len(skills) != len(req_data.skill_ids):
                            raise HRSystemBaseException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                message="One or more skills not found or inactive",
                            )

                        # If job_role_id is specified, validate skills belong to that job role
                        if req_data.job_role_id:
                            # Check skills directly using job_role_id FK in m_skills
                            valid_skills = (
                                db.query(Skill)
                                .filter(
                                    and_(
                                        Skill.job_role_id == req_data.job_role_id,
                                        Skill.id.in_(req_data.skill_ids),
                                        Skill.is_active == True,
                                        Skill.deleted_at.is_(None),
                                    )
                                )
                                .all()
                            )

                            valid_skill_ids = {skill.id for skill in valid_skills}
                            if not set(req_data.skill_ids).issubset(valid_skill_ids):
                                raise HRSystemBaseException(
                                    status_code=status.HTTP_400_BAD_REQUEST,
                                    message="Some skills are not associated with the specified job role",
                                )

                        # Create skill associations
                        for skill_id in req_data.skill_ids:
                            skill_assoc = JobRequirementSkill(
                                job_requirement_id=requirement.id,
                                skill_id=skill_id,
                            )
                            db.add(skill_assoc)

                    # Create certificate associations
                    if req_data.certificate_ids:
                        for cert_id in req_data.certificate_ids:
                            cert_assoc = JobRequirementCertificate(
                                job_requirement_id=requirement.id,
                                certificate_id=cert_id,
                            )
                            db.add(cert_assoc)

                    # Create black list associations
                    if req_data.black_list_ids:
                        for bl_id in req_data.black_list_ids:
                            bl_assoc = JobRequirementBlackList(
                                job_requirement_id=requirement.id, black_list_id=bl_id
                            )
                            db.add(bl_assoc)

            db.commit()

            # Return updated job with related data
            return {
                "job": job,
                "job_requirements": job_requirements,
                "include_black_list_check": job_data.include_black_list_check,
            }

        except Exception as e:
            db.rollback()
            if isinstance(e, HRSystemBaseException):
                raise e
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to update job: {str(e)}",
            )

    def get_jobs_by_area(self, db: Session, area: int) -> List[Job]:
        """Get jobs by area (1: Da Nang, 3: Ho Chi Minh, 5: Hanoi)"""
        return (
            db.query(Job).filter(and_(Job.area == area, Job.deleted_at.is_(None))).all()
        )

    def get_jobs_by_employment_type(
        self, db: Session, employment_type: int
    ) -> List[Job]:
        """Get jobs by employment type"""
        return (
            db.query(Job)
            .filter(
                and_(Job.employment_type == employment_type, Job.deleted_at.is_(None))
            )
            .all()
        )

    def get_jobs_by_creator(self, db: Session, created_by: int) -> List[Job]:
        """Get jobs created by a specific user"""
        return (
            db.query(Job)
            .filter(and_(Job.created_by == created_by, Job.deleted_at.is_(None)))
            .all()
        )

    def search_jobs_by_title(self, db: Session, title_keyword: str) -> List[Job]:
        """Search jobs by title keyword"""
        return (
            db.query(Job)
            .filter(
                and_(Job.title.ilike(f"%{title_keyword}%"), Job.deleted_at.is_(None))
            )
            .all()
        )

    def get_job_with_details(
        self, db: Session, job_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get job with job role and requirements details using separate queries"""
        # Get the job first
        job = (
            db.query(Job)
            .filter(and_(Job.id == job_id, Job.deleted_at.is_(None)))
            .first()
        )

        if not job:
            return None

        # Get job role if exists
        job_role = None
        if job.job_role_id:
            job_role = db.query(JobRole).filter(JobRole.id == job.job_role_id).first()

        # Get job requirements
        job_requirements = (
            db.query(JobRequirement)
            .filter(
                and_(
                    JobRequirement.job_id == job.id, JobRequirement.deleted_at.is_(None)
                )
            )
            .all()
        )

        return {"job": job, "job_role": job_role, "job_requirements": job_requirements}

    def get_jobs_by_role(self, db: Session, job_role_id: int) -> List[Job]:
        """Get jobs by job role"""
        return (
            db.query(Job)
            .filter(and_(Job.job_role_id == job_role_id, Job.deleted_at.is_(None)))
            .all()
        )

    def get_all_with_details(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Get all jobs with job role and requirements details using separate queries"""
        # Get jobs first with filtering
        query = db.query(Job).filter(Job.deleted_at.is_(None)).order_by(Job.id.desc())

        if filters:
            for field, value in filters.items():
                if value is not None and hasattr(Job, field):
                    if field == "title":
                        # Use ILIKE for case-insensitive partial matching on title
                        query = query.filter(getattr(Job, field).ilike(f"%{value}%"))
                    else:
                        # Exact match for other fields
                        query = query.filter(getattr(Job, field) == value)

        jobs = query.offset(skip).limit(limit).all()

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
        job_requirements = (
            db.query(JobRequirement)
            .filter(
                and_(
                    JobRequirement.job_id.in_(job_ids),
                    JobRequirement.deleted_at.is_(None),
                )
            )
            .all()
        )

        # Group requirements by job_id
        requirements_dict = {}
        for req in job_requirements:
            if req.job_id not in requirements_dict:
                requirements_dict[req.job_id] = []
            requirements_dict[req.job_id].append(req)

        # Combine data
        result = []
        for job in jobs:
            result.append(
                {
                    "job": job,
                    "job_role": job_roles_dict.get(job.job_role_id),
                    "job_requirements": requirements_dict.get(job.id, []),
                }
            )

        return result

    def get_job_skills(self, db: Session, job_id: int) -> List[Skill]:
        """Get skills for a job through job requirement skills"""
        # Get all job requirements for this job
        job_requirements = (
            db.query(JobRequirement)
            .filter(
                and_(
                    JobRequirement.job_id == job_id,
                    JobRequirement.deleted_at.is_(None),
                )
            )
            .all()
        )

        if not job_requirements:
            return []

        # Get all skill associations for these job requirements
        requirement_ids = [req.id for req in job_requirements]
        job_requirement_skill_associations = (
            db.query(JobRequirementSkill)
            .filter(
                and_(
                    JobRequirementSkill.job_requirement_id.in_(requirement_ids),
                    JobRequirementSkill.deleted_at.is_(None),
                )
            )
            .all()
        )

        if not job_requirement_skill_associations:
            return []

        # Get unique skills
        skill_ids = list(
            set([assoc.skill_id for assoc in job_requirement_skill_associations])
        )
        return (
            db.query(Skill)
            .filter(
                and_(
                    Skill.id.in_(skill_ids),
                    Skill.is_active == True,
                    Skill.deleted_at.is_(None),
                )
            )
            .all()
        )

    def _get_job_role_skill_ids(self, db: Session, job_role_id: int) -> List[int]:
        """Get all skill IDs available for a job role using direct FK"""
        skills = (
            db.query(Skill)
            .filter(
                and_(
                    Skill.job_role_id == job_role_id,
                    Skill.is_active == True,
                    Skill.deleted_at.is_(None),
                )
            )
            .all()
        )
        return [skill.id for skill in skills]

    def get_job_certificates(self, db: Session, job_id: int) -> List[Certificate]:
        """Get certificates required for a job"""
        # Get job requirements first
        job_requirements = (
            db.query(JobRequirement)
            .filter(
                and_(
                    JobRequirement.job_id == job_id, JobRequirement.deleted_at.is_(None)
                )
            )
            .all()
        )

        if not job_requirements:
            return []

        # Get certificate IDs from job requirement certificates
        req_ids = [req.id for req in job_requirements]
        cert_associations = (
            db.query(JobRequirementCertificate)
            .filter(
                and_(
                    JobRequirementCertificate.job_requirement_id.in_(req_ids),
                    JobRequirementCertificate.deleted_at.is_(None),
                )
            )
            .all()
        )

        if not cert_associations:
            return []

        # Get certificates
        cert_ids = [assoc.certificate_id for assoc in cert_associations]
        return (
            db.query(Certificate)
            .filter(
                and_(
                    Certificate.id.in_(cert_ids),
                    Certificate.is_active == True,
                    Certificate.deleted_at.is_(None),
                )
            )
            .all()
        )

    def get_job_black_lists(self, db: Session, job_id: int) -> List[BlackList]:
        """Get black lists for a job"""
        # Get job requirements first
        job_requirements = (
            db.query(JobRequirement)
            .filter(
                and_(
                    JobRequirement.job_id == job_id, JobRequirement.deleted_at.is_(None)
                )
            )
            .all()
        )

        if not job_requirements:
            return []

        # Get black list IDs from job requirement black lists
        req_ids = [req.id for req in job_requirements]
        bl_associations = (
            db.query(JobRequirementBlackList)
            .filter(
                and_(
                    JobRequirementBlackList.job_requirement_id.in_(req_ids),
                    JobRequirementBlackList.deleted_at.is_(None),
                )
            )
            .all()
        )

        if not bl_associations:
            return []

        # Get black lists
        bl_ids = [assoc.black_list_id for assoc in bl_associations]
        return (
            db.query(BlackList)
            .filter(
                and_(
                    BlackList.id.in_(bl_ids),
                    BlackList.is_active == True,
                    BlackList.deleted_at.is_(None),
                )
            )
            .all()
        )

    def _process_resume_file_info(self, resume: Resume) -> ResumeFileInfo:
        """Process resume file information based on storage type"""
        file_url = None
        storage_type = "local"

        # Determine storage type based on file path
        if resume.file_path.startswith("http"):
            # Google Drive file (has web URL)
            storage_type = "google_drive"
            file_url = resume.file_path
        else:
            # Local file
            storage_type = "local"
            # For local files, we could construct a full URL if needed
            # file_url = f"http://localhost:8000/uploads/{resume.file_path}"
            file_url = f"/uploads/{resume.file_path}"

        return ResumeFileInfo(
            id=resume.id,
            candidate_id=resume.candidate_id,
            file_path=resume.file_path,
            file_url=file_url,
            storage_type=storage_type,
            note=resume.note,
            created_at=resume.created_at,
        )

    def get_job_with_resumes(
        self, db: Session, job_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get job with full details including resume files from applications"""
        # Get basic job details first
        job_details = self.get_job_with_details(db, job_id)
        if not job_details:
            return None

        # Get applications for this job with candidate and resume information
        applications = (
            db.query(Application)
            .join(Candidate, Application.candidate_id == Candidate.id)
            .join(Resume, Application.resume_id == Resume.id)
            .filter(
                and_(
                    Application.job_id == job_id,
                    Application.deleted_at.is_(None),
                    Candidate.deleted_at.is_(None),
                    Resume.deleted_at.is_(None),
                )
            )
            .all()
        )

        # Process applications with resume information
        applications_with_resumes = []
        for app in applications:
            # Get candidate info
            candidate = (
                db.query(Candidate)
                .filter(
                    and_(
                        Candidate.id == app.candidate_id, Candidate.deleted_at.is_(None)
                    )
                )
                .first()
            )

            # Get resume info
            resume = (
                db.query(Resume)
                .filter(and_(Resume.id == app.resume_id, Resume.deleted_at.is_(None)))
                .first()
            )

            if candidate and resume:
                resume_info = self._process_resume_file_info(resume)

                app_resume_info = ApplicationResumeInfo(
                    application_id=app.id,
                    candidate_id=candidate.id,
                    candidate_name=f"{candidate.first_name} {candidate.last_name}",
                    application_status=app.status,
                    resume=resume_info,
                )
                applications_with_resumes.append(app_resume_info)

        # Add resume information to job details
        job_details["applications_with_resumes"] = applications_with_resumes

        return job_details


# Create singleton instance
job_service = JobService()
