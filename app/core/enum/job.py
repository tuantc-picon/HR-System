from enum import IntEnum


class JobStatusEnum(IntEnum):
    """Job status"""

    DRAFT = 1
    OPEN = 3
    CLOSED = 5
    CANCELLED = 7


class JobSourceEnum(IntEnum):
    """Job source"""

    HR_SYSTEM = 1
    OTHER = 2


class JobAreaEnum(IntEnum):
    """Job area"""

    DA_NANG = 1
    HO_CHI_MINH = 3
    HANOI = 5


class JobEmploymentTypeEnum(IntEnum):
    """Job employment type"""

    FULL_TIME = 1
    PART_TIME = 3
    FRESHER = 5
    INTERNSHIP = 7
    VENDOR = 9
