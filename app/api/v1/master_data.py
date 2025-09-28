from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Union, Optional

from core.common.database import get_db_session
from core.enum.master import MasterDataTypeEnum
from services.master_data_service import master_data_service
from schema.response.job_role_schemas import JobRoleResponse
from schema.response.skill_schemas import SkillResponse
from schema.response.certificate_schemas import CertificateResponse
from schema.response.role_schemas import RoleResponse

router = APIRouter()


class MasterDataResponse:
    """Response model for unified master data"""

    def __init__(
        self,
        job_roles: List[JobRoleResponse],
        skills: List[SkillResponse],
        certificates: List[CertificateResponse],
    ):
        self.job_roles = job_roles
        self.skills = skills
        self.certificates = certificates


@router.get("/all")
def get_all_master_data(db: Session = Depends(get_db_session)):
    """Get all master data as lists (excludes black_list as requested)"""
    try:
        master_data = master_data_service.get_all_master_data(db)

        # Convert to response models
        job_roles = [
            JobRoleResponse.model_validate(role) for role in master_data["job_roles"]
        ]
        skills = [
            SkillResponse.model_validate(skill) for skill in master_data["skills"]
        ]
        certificates = [
            CertificateResponse.model_validate(cert)
            for cert in master_data["certificates"]
        ]

        # Include user_roles in the response
        user_roles = [
            RoleResponse.model_validate(role) for role in master_data["user_roles"]
        ]

        return {
            "job_roles": job_roles,
            "skills": skills,
            "certificates": certificates,
            "user_roles": user_roles,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve master data: {str(e)}",
        )


@router.get("/")
def get_master_data_by_type(
    data_type: MasterDataTypeEnum = Query(
        ..., description="Type of master data to retrieve"
    ),
    db: Session = Depends(get_db_session),
) -> Union[
    List[JobRoleResponse],
    List[SkillResponse],
    List[CertificateResponse],
    List[RoleResponse],
]:
    """Get specific master data by type using enum parameter"""
    try:
        data = master_data_service.get_master_data_by_type(db, data_type)

        # Convert to appropriate response models based on data type
        if data_type == MasterDataTypeEnum.CERTIFICATES:
            return [CertificateResponse.model_validate(item) for item in data]
        elif data_type == MasterDataTypeEnum.JOB_ROLES:
            return [JobRoleResponse.model_validate(item) for item in data]
        elif data_type == MasterDataTypeEnum.SKILLS:
            return [SkillResponse.model_validate(item) for item in data]
        elif data_type == MasterDataTypeEnum.USER_ROLES:
            return [RoleResponse.model_validate(item) for item in data]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve {data_type} data: {str(e)}",
        )


@router.get("/entities")
def get_master_data_by_entities(
    entities: str = Query(
        ...,
        description="Comma-separated list of entity types (e.g., 'skills,job_roles,certificates')",
    ),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """Get specific master data entities by comma-separated list"""
    try:
        # Parse the comma-separated entities
        entity_list = [entity.strip().lower() for entity in entities.split(",")]

        # Validate entity types
        valid_entities = {
            "skills": MasterDataTypeEnum.SKILLS,
            "job_roles": MasterDataTypeEnum.JOB_ROLES,
            "certificates": MasterDataTypeEnum.CERTIFICATES,
            "user_roles": MasterDataTypeEnum.USER_ROLES,
        }

        invalid_entities = [
            entity for entity in entity_list if entity not in valid_entities
        ]
        if invalid_entities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entity types: {', '.join(invalid_entities)}. Valid types are: {', '.join(valid_entities.keys())}",
            )

        # Fetch data for requested entities
        result = {}

        for entity in entity_list:
            data_type = valid_entities[entity]
            data = master_data_service.get_master_data_by_type(db, data_type)

            # Convert to appropriate response models based on data type
            if data_type == MasterDataTypeEnum.CERTIFICATES:
                result[entity] = [
                    CertificateResponse.model_validate(item) for item in data
                ]
            elif data_type == MasterDataTypeEnum.JOB_ROLES:
                result[entity] = [JobRoleResponse.model_validate(item) for item in data]
            elif data_type == MasterDataTypeEnum.SKILLS:
                result[entity] = [SkillResponse.model_validate(item) for item in data]
            elif data_type == MasterDataTypeEnum.USER_ROLES:
                result[entity] = [RoleResponse.model_validate(item) for item in data]

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve master data entities: {str(e)}",
        )


@router.post("/populate-from-csv")
def populate_master_data_from_csv(db: Session = Depends(get_db_session)):
    """Populate master data from CSV files"""
    try:
        results = master_data_service.populate_from_csv(db)
        return {
            "message": "Master data populated successfully from CSV files",
            "results": results,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to populate master data: {str(e)}",
        )
