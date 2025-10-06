from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from services.resume_service import resume_service
from services.job_service import job_service
from services.candidate_service import candidate_service
from core.common.exceptions import HRSystemBaseException
from starlette import status
import json
import google.generativeai as genai
import os

class CVAssessmentService:
    def __init__(self):
        pass

    def prepare_assessment_data(self, db: Session, candidate_id: int, job_id: int) -> Dict[str, Any]:
        """Prepare resume and job description data for CV assessment"""
        # Retrieve candidate information
        candidate = candidate_service.get_by_id(db, candidate_id)
        if not candidate:
            raise HRSystemBaseException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Candidate not found."
            )

        # Retrieve resumes for the candidate
        resumes = resume_service.get_resumes_by_candidate(db, candidate_id)
        if not resumes:
            raise HRSystemBaseException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="No resumes found for the candidate."
            )

        # Retrieve job details with requirements and skills
        job_details = job_service.get_job_with_details(db, job_id)
        if not job_details:
            raise HRSystemBaseException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Job not found."
            )

        # Get job skills and certificates
        job_skills = job_service.get_job_skills(db, job_id)
        job_certificates = job_service.get_job_certificates(db, job_id)
        job_blacklists = job_service.get_job_black_lists(db, job_id)

        # Combine data for assessment
        assessment_data = {
            "candidate": {
                "id": candidate.id,
                "full_name": candidate.full_name,
                "email": candidate.email,
                "phone": getattr(candidate, 'phone', None),
                "address": getattr(candidate, 'address', None),
            },
            "resumes": [
                {
                    "id": resume.id,
                    "file_path": resume.file_path,
                    "note": resume.note,
                    "created_at": resume.created_at.isoformat() if resume.created_at else None
                } for resume in resumes
            ],
            "job": {
                "id": job_details["job"].id,
                "title": job_details["job"].title,
                "description": job_details["job"].description,
                "area": job_details["job"].area,
                "employment_type": job_details["job"].employment_type,
                "salary_min": getattr(job_details["job"], 'salary_min', None),
                "salary_max": getattr(job_details["job"], 'salary_max', None),
            },
            "job_role": {
                "id": job_details["job_role"].id,
                "name": job_details["job_role"].name,
                "description": job_details["job_role"].description,
            } if job_details["job_role"] else None,
            "job_requirements": [
                {
                    "id": req.id,
                    "min_experience": req.min_experience,
                    "max_experience": req.max_experience,
                    "min_salary": req.min_salary,
                    "max_salary": req.max_salary,
                    "note": req.note,
                } for req in job_details["job_requirements"]
            ],
            "required_skills": [
                {
                    "id": skill.id,
                    "name": skill.name,
                    "description": skill.description,
                } for skill in job_skills
            ],
            "required_certificates": [
                {
                    "id": cert.id,
                    "name": cert.name,
                    "description": cert.description,
                } for cert in job_certificates
            ],
            "blacklisted_items": [
                {
                    "id": bl.id,
                    "name": bl.name,
                    "description": bl.description,
                } for bl in job_blacklists
            ]
        }

        return assessment_data

    def create_llm_prompt(self, assessment_data: Dict[str, Any], cv_content: str = None) -> str:
        """Create a structured prompt for LLM to assess CV against job requirements"""
        
        job = assessment_data["job"]
        candidate = assessment_data["candidate"]
        job_requirements = assessment_data["job_requirements"]
        required_skills = assessment_data["required_skills"]
        required_certificates = assessment_data["required_certificates"]
        blacklisted_items = assessment_data["blacklisted_items"]
        job_role = assessment_data.get("job_role")

        prompt = f"""
Please assess the following candidate's CV against the job requirements and provide a detailed evaluation.

**CANDIDATE INFORMATION:**
- Name: {candidate['full_name']}
- Email: {candidate['email']}
- Phone: {candidate.get('phone', 'Not provided')}

**JOB INFORMATION:**
- Position: {job['title']}
- Description: {job['description']}
- Job Role: {job_role['name'] if job_role else 'Not specified'}
- Employment Type: {job['employment_type']}
- Location/Area: {job['area']}

**JOB REQUIREMENTS:**
"""
        
        for i, req in enumerate(job_requirements, 1):
            prompt += f"""
{i}. Experience: {req['min_experience']}-{req['max_experience']} years
   Salary Range: ${req['min_salary']:,} - ${req['max_salary']:,}
   Additional Notes: {req['note'] or 'None'}
"""

        if required_skills:
            prompt += f"""
**REQUIRED SKILLS:**
{', '.join([skill['name'] for skill in required_skills])}
"""

        if required_certificates:
            prompt += f"""
**REQUIRED CERTIFICATES:**
{', '.join([cert['name'] for cert in required_certificates])}
"""

        if blacklisted_items:
            prompt += f"""
**DISQUALIFYING FACTORS (Blacklist):**
{', '.join([bl['name'] for bl in blacklisted_items])}
"""

        if cv_content:
            prompt += f"""
**CANDIDATE'S CV CONTENT:**
{cv_content}
"""
        else:
            prompt += """
**CANDIDATE'S CV CONTENT:**
[CV content should be extracted from the resume file paths provided in the assessment data]
"""

        prompt += """
**ASSESSMENT REQUIREMENTS:**
Please provide a comprehensive assessment including:

1. **Overall Match Score** (0-100): Rate how well the candidate matches the job requirements
2. **Experience Analysis**: Evaluate if the candidate meets the experience requirements
3. **Skill Assessment**: Analyze which required skills the candidate possesses
4. **Certificate Verification**: Check if the candidate has required certifications
5. **Salary Expectation**: Assess if candidate's profile fits the salary range
6. **Red Flags**: Identify any blacklisted items or concerning factors
7. **Strengths**: Highlight the candidate's key strengths for this position
8. **Weaknesses**: Point out areas where the candidate may be lacking
9. **Recommendation**: Provide a clear recommendation (Highly Recommended/Recommended/Consider/Not Recommended)
10. **Additional Comments**: Any other relevant observations

Please structure your response in JSON format for easy parsing.
"""

        return prompt

    def assess_cv_with_llm(self, db: Session, candidate_id: int, job_id: int, cv_content: str = None) -> Dict[str, Any]:
        """Complete CV assessment workflow with Gemini LLM integration"""

        assessment_data = self.prepare_assessment_data(db, candidate_id, job_id)

        llm_prompt = self.create_llm_prompt(assessment_data, cv_content)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "assessment_data": assessment_data,
                "llm_prompt": llm_prompt,
                "llm_response": None,
                "status": "error",
                "message": "Gemini API key not found in environment variables."
            }

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")

        try:
            response = model.generate_content(llm_prompt)
            llm_response = response.text
            processed_response = self.process_llm_response(llm_response)
            status_msg = "LLM assessment completed."
            status = "completed"
        except Exception as e:
            llm_response = None
            processed_response = None
            status_msg = f"Error during Gemini LLM call: {str(e)}"
            status = "error"

        result = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "assessment_data": assessment_data,
            "llm_prompt": llm_prompt,
            "llm_response": llm_response,
            "processed_response": processed_response,
            "status": status,
            "message": status_msg
        }

        return result

    def process_llm_response(self, llm_response: str) -> Dict[str, Any]:
        """Process and structure the LLM response"""
        try:
            if llm_response.strip().startswith('{'):
                return json.loads(llm_response)
            else:
                return {
                    "raw_response": llm_response,
                    "parsed": False,
                    "message": "Response received but not in JSON format"
                }
        except json.JSONDecodeError:
            return {
                "raw_response": llm_response,
                "parsed": False,
                "error": "Failed to parse LLM response as JSON"
            }


cv_assessment_service = CVAssessmentService()