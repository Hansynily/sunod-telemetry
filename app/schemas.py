from datetime import datetime
from typing import List, Optional

# pyright: reportMissingImports=false
from pydantic import BaseModel, EmailStr, Field


class SkillUsedBase(BaseModel):
    skill_name: str = Field(..., max_length=100)
    usage_count: int = Field(1, ge=1)


class SkillUsedCreate(SkillUsedBase):
    pass


class SkillUsed(SkillUsedBase):
    id: int
    quest_attempt_id: int

    class Config:
        orm_mode = True


class QuestAttemptBase(BaseModel):
    quest_name: str = Field(..., max_length=100)
    success: int = Field(0, ge=0, le=1)
    completed_at: Optional[datetime] = None


class QuestAttemptCreate(QuestAttemptBase):
    skills_used: List[SkillUsedCreate] = []


class QuestAttempt(QuestAttemptBase):
    id: int
    user_id: int
    started_at: datetime
    skills_used: List[SkillUsed] = []

    class Config:
        orm_mode = True


class UserRIASECProfileBase(BaseModel):
    realistic: float
    investigative: float
    artistic: float
    social: float
    enterprising: float
    conventional: float


class UserRIASECProfileCreate(UserRIASECProfileBase):
    pass


class UserRIASECProfile(UserRIASECProfileBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    riasec_profile: Optional[UserRIASECProfileCreate] = None


class User(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    quest_attempts: List[QuestAttempt] = []
    riasec_profile: Optional[UserRIASECProfile] = None

    class Config:
        orm_mode = True


class SelectedSkill(BaseModel):
    riasec_code: str = Field(..., max_length=10)
    skill_name: str = Field(..., max_length=100)


class QuestAttemptTelemetryIn(BaseModel):
    player_id: str
    username: str
    email: Optional[EmailStr] = None
    quest_id: str
    selected_skills: List[SelectedSkill]
    quest_result: str
    time_spent_seconds: int = Field(..., ge=0)


class QuestAttemptTelemetryOut(BaseModel):
    success: bool
    message: str


class AdminUser(BaseModel):
    user_id: int
    username: str
    email: Optional[EmailStr] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    total_quest_attempts: int


class UserPerformance(BaseModel):
    user_id: int
    username: str
    total_attempts: int
    attempts: List[QuestAttempt]
    aggregated_riasec: UserRIASECProfileBase

