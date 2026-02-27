from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String(50), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    quest_attempts = relationship(
        "QuestAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    riasec_profile = relationship(
        "UserRIASECProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class QuestAttempt(Base):
    __tablename__ = "quest_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quest_id = Column(String(100), nullable=False)
    quest_name = Column(String(100), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    time_spent_seconds = Column(Integer, nullable=False, default=0)
    quest_result = Column(String(50), nullable=False, default="unknown")
    success = Column(Integer, default=0, nullable=False)  # 0 = fail, 1 = success

    user = relationship("User", back_populates="quest_attempts")
    skills_used = relationship(
        "SkillUsed",
        back_populates="quest_attempt",
        cascade="all, delete-orphan",
    )


class SkillUsed(Base):
    __tablename__ = "skills_used"

    id = Column(Integer, primary_key=True, index=True)
    quest_attempt_id = Column(
        Integer,
        ForeignKey("quest_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    skill_name = Column(String(100), nullable=False)
    riasec_code = Column(String(10), nullable=False)
    usage_count = Column(Integer, default=1, nullable=False)

    quest_attempt = relationship("QuestAttempt", back_populates="skills_used")


class UserRIASECProfile(Base):
    __tablename__ = "user_riasec_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    realistic = Column(Float, nullable=False)
    investigative = Column(Float, nullable=False)
    artistic = Column(Float, nullable=False)
    social = Column(Float, nullable=False)
    enterprising = Column(Float, nullable=False)
    conventional = Column(Float, nullable=False)

    user = relationship("User", back_populates="riasec_profile")

