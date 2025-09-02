from fastapi import APIRouter
from api.v1.users import router as users_router
from api.v1.roles import router as roles_router
from api.v1.certificates import router as certificates_router
from api.v1.black_lists import router as black_lists_router
from api.v1.jobs import router as jobs_router
from api.v1.job_requirements import router as job_requirements_router
from api.v1.candidates import router as candidates_router
from api.v1.resumes import router as resumes_router
from api.v1.applications import router as applications_router
from api.v1.job_requirement_certificates import router as job_requirement_certificates_router
from api.v1.job_requirement_black_lists import router as job_requirement_black_lists_router

router = APIRouter(redirect_slashes=False)

# Include all routers with their respective prefixes and tags
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(roles_router, prefix="/roles", tags=["Roles"])
router.include_router(certificates_router, prefix="/certificates", tags=["Certificates"])
router.include_router(black_lists_router, prefix="/black-lists", tags=["Black Lists"])
router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
router.include_router(job_requirements_router, prefix="/job-requirements", tags=["Job Requirements"])
router.include_router(candidates_router, prefix="/candidates", tags=["Candidates"])
router.include_router(resumes_router, prefix="/resumes", tags=["Resumes"])
router.include_router(applications_router, prefix="/applications", tags=["Applications"])
router.include_router(job_requirement_certificates_router, prefix="/job-requirement-certificates", tags=["Job Requirement Certificates"])
router.include_router(job_requirement_black_lists_router, prefix="/job-requirement-black-lists", tags=["Job Requirement Black Lists"])


@router.get("/health")
def health_check():
    return {"status": "healthy"}