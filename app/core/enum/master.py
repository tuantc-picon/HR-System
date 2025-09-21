from enum import IntEnum, Enum


class CertificateCategoryEnum(IntEnum):
    """Certificate category"""

    LANGUAGE = 1
    TESTING = 2
    PROJECT_MANAGEMENT = 3
    CLOUD = 4
    TECHNICAL = 5
    OTHER = 6


class MasterDataTypeEnum(str, Enum):
    """Master data types for API endpoints"""

    CERTIFICATES = "certificates"
    JOB_ROLES = "job_roles"
    SKILLS = "skills"
    USER_ROLES = "user_roles"
