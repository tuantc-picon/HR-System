from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timezone
import logging

from model.job.jobs import Job
from model.candidate.candidates import Candidate
from model.candidate.resumes import Resume
from model.application.applications import Application
from services.base_service import BaseService
from services.application_service import application_service
from schema.request.application_schemas import ApplicationCreateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutomaticApplicationService:
    """
    Service for automatically creating job applications by matching candidates to jobs.

    This service implements the following validation criteria:
    1. No Duplicate Applications: Verify the candidate has not already applied to this specific job
    2. Job Status Validation: Only process jobs with status = OPEN (status code 3)
    3. Deadline Check: Ensure the job application deadline has not passed
    4. Candidate Verification: Only include candidates where is_blocklisted = false
    5. Timing Constraint: Only create automatic applications for candidates who were created AFTER the job was opened
    """

    def __init__(self):
        self.logger = logger

    def get_eligible_jobs(self, db: Session) -> List[Job]:
        """
        Get all jobs that are eligible for automatic application creation.

        Criteria:
        - Status = 3 (OPEN)
        - Application deadline has not passed (or no deadline set)
        - Job is not deleted
        """
        current_time = datetime.now(timezone.utc)

        return (
            db.query(Job)
            .filter(
                and_(
                    Job.status == 3,  # OPEN status
                    Job.deleted_at.is_(None),
                    or_(
                        Job.application_deadline.is_(None),  # No deadline set
                        Job.application_deadline > current_time,  # Deadline not passed
                    ),
                )
            )
            .all()
        )

    def get_eligible_candidates(self, db: Session, job: Job) -> List[Candidate]:
        """
        Get all candidates that are eligible for automatic application to a specific job.

        Criteria:
        - is_blocklisted = false
        - Candidate was created AFTER the job was opened (created_at > job.created_at)
        - Candidate is not deleted
        - Candidate has at least one resume
        """
        return (
            db.query(Candidate)
            .filter(
                and_(
                    Candidate.is_blocklisted == False,
                    Candidate.created_at
                    > job.created_at,  # Created after job was opened
                    Candidate.deleted_at.is_(None),
                    # Ensure candidate has at least one resume
                    Candidate.id.in_(
                        db.query(Resume.candidate_id).filter(
                            Resume.deleted_at.is_(None)
                        )
                    ),
                )
            )
            .all()
        )

    def has_existing_application(
        self, db: Session, job_id: int, candidate_id: int
    ) -> bool:
        """
        Check if a candidate has already applied to a specific job.
        """
        existing_application = (
            db.query(Application)
            .filter(
                and_(
                    Application.job_id == job_id,
                    Application.candidate_id == candidate_id,
                    Application.deleted_at.is_(None),
                )
            )
            .first()
        )

        return existing_application is not None

    def get_candidate_resume(self, db: Session, candidate_id: int) -> Optional[Resume]:
        """
        Get the most recent resume for a candidate.
        """
        return (
            db.query(Resume)
            .filter(
                and_(Resume.candidate_id == candidate_id, Resume.deleted_at.is_(None))
            )
            .order_by(Resume.created_at.desc())
            .first()
        )

    def create_automatic_application(
        self, db: Session, job: Job, candidate: Candidate
    ) -> Optional[Application]:
        """
        Create an automatic application for a candidate to a job.

        Returns:
        - Application object if successful
        - None if creation failed or was skipped
        """
        try:
            # Check if application already exists
            if self.has_existing_application(db, job.id, candidate.id):
                self.logger.debug(
                    f"Skipping: Candidate {candidate.id} already applied to job {job.id}"
                )
                return None

            # Get candidate's resume
            resume = self.get_candidate_resume(db, candidate.id)
            if not resume:
                self.logger.warning(f"Skipping: Candidate {candidate.id} has no resume")
                return None

            # Create application request
            application_data = ApplicationCreateRequest(
                job_id=job.id,
                candidate_id=candidate.id,
                resume_id=resume.id,
                status=1,  # Applied status
                note="Automatically created application",
                created_by=None,  # System-generated
                updated_by=None,
            )

            # Create the application
            application = application_service.create_application(db, application_data)

            self.logger.info(
                f"Created automatic application: Job {job.id} -> Candidate {candidate.id}"
            )
            return application

        except Exception as e:
            self.logger.error(
                f"Failed to create automatic application for job {job.id}, candidate {candidate.id}: {str(e)}"
            )
            return None

    def process_automatic_applications(self, db: Session) -> Dict[str, Any]:
        """
        Main method to process automatic application creation for all eligible jobs and candidates.

        Returns:
        - Dictionary with processing statistics and results
        """
        start_time = datetime.now(timezone.utc)
        stats = {
            "start_time": start_time,
            "jobs_processed": 0,
            "candidates_evaluated": 0,
            "applications_created": 0,
            "applications_skipped": 0,
            "errors": 0,
            "job_details": [],
        }

        try:
            self.logger.info("Starting automatic application creation process")

            # Get eligible jobs
            eligible_jobs = self.get_eligible_jobs(db)
            self.logger.info(f"Found {len(eligible_jobs)} eligible jobs")

            for job in eligible_jobs:
                job_stats = {
                    "job_id": job.id,
                    "job_title": job.title,
                    "candidates_evaluated": 0,
                    "applications_created": 0,
                    "applications_skipped": 0,
                }

                try:
                    # Get eligible candidates for this job
                    eligible_candidates = self.get_eligible_candidates(db, job)
                    job_stats["candidates_evaluated"] = len(eligible_candidates)
                    stats["candidates_evaluated"] += len(eligible_candidates)

                    self.logger.info(
                        f"Job {job.id} ({job.title}): Found {len(eligible_candidates)} eligible candidates"
                    )

                    for candidate in eligible_candidates:
                        try:
                            application = self.create_automatic_application(
                                db, job, candidate
                            )
                            if application:
                                job_stats["applications_created"] += 1
                                stats["applications_created"] += 1
                            else:
                                job_stats["applications_skipped"] += 1
                                stats["applications_skipped"] += 1

                        except Exception as e:
                            self.logger.error(
                                f"Error processing candidate {candidate.id} for job {job.id}: {str(e)}"
                            )
                            stats["errors"] += 1

                    stats["jobs_processed"] += 1
                    stats["job_details"].append(job_stats)

                except Exception as e:
                    self.logger.error(f"Error processing job {job.id}: {str(e)}")
                    stats["errors"] += 1

            # Commit all changes
            db.commit()

            end_time = datetime.now(timezone.utc)
            stats["end_time"] = end_time
            stats["duration_seconds"] = (end_time - start_time).total_seconds()

            self.logger.info(f"Automatic application creation completed:")
            self.logger.info(f"  - Jobs processed: {stats['jobs_processed']}")
            self.logger.info(
                f"  - Candidates evaluated: {stats['candidates_evaluated']}"
            )
            self.logger.info(
                f"  - Applications created: {stats['applications_created']}"
            )
            self.logger.info(
                f"  - Applications skipped: {stats['applications_skipped']}"
            )
            self.logger.info(f"  - Errors: {stats['errors']}")
            self.logger.info(f"  - Duration: {stats['duration_seconds']:.2f} seconds")

            return stats

        except Exception as e:
            db.rollback()
            self.logger.error(
                f"Critical error in automatic application creation: {str(e)}"
            )
            stats["errors"] += 1
            stats["end_time"] = datetime.now(timezone.utc)
            stats["duration_seconds"] = (stats["end_time"] - start_time).total_seconds()
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Automatic application creation failed: {str(e)}",
            )

    def get_processing_summary(self, db: Session) -> Dict[str, Any]:
        """
        Get a summary of the current state for automatic application processing.

        Returns statistics about eligible jobs, candidates, and potential applications.
        """
        try:
            eligible_jobs = self.get_eligible_jobs(db)
            total_eligible_candidates = 0
            total_potential_applications = 0

            for job in eligible_jobs:
                eligible_candidates = self.get_eligible_candidates(db, job)
                total_eligible_candidates += len(eligible_candidates)

                # Count potential new applications (candidates without existing applications)
                for candidate in eligible_candidates:
                    if not self.has_existing_application(db, job.id, candidate.id):
                        total_potential_applications += 1

            return {
                "eligible_jobs": len(eligible_jobs),
                "total_eligible_candidates": total_eligible_candidates,
                "potential_new_applications": total_potential_applications,
                "timestamp": datetime.now(timezone.utc),
            }

        except Exception as e:
            self.logger.error(f"Error getting processing summary: {str(e)}")
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to get processing summary: {str(e)}",
            )


# Create singleton instance
automatic_application_service = AutomaticApplicationService()
