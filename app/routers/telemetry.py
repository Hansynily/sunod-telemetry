from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas


router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])
admin_ui_router = APIRouter(prefix="/admin", tags=["admin-ui"])

templates = Jinja2Templates(directory="templates")


@router.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.User)
        .filter(
            (models.User.username == user_in.username)
            | (models.User.email == user_in.email)
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username or email already exists.",
        )

    user = models.User(
        player_id=str(uuid.uuid4()),
        username=user_in.username,
        email=user_in.email
        )    
    db.add(user)
    db.flush()

    if user_in.riasec_profile:
        profile = models.UserRIASECProfile(
            user_id=user.id,
            **user_in.riasec_profile.dict(),
        )
        db.add(profile)

    db.commit()
    db.refresh(user)
    return user


@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.post(
    "/users/{user_id}/quest-attempts",
    response_model=schemas.QuestAttempt,
    status_code=status.HTTP_201_CREATED,
)
def create_quest_attempt(
    user_id: int,
    quest_in: schemas.QuestAttemptCreate,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    quest_attempt = models.QuestAttempt(
        user_id=user_id,
        quest_name=quest_in.quest_name,
        success=quest_in.success,
        completed_at=quest_in.completed_at,
    )
    db.add(quest_attempt)
    db.flush()

    for skill_in in quest_in.skills_used:
        skill = models.SkillUsed(
            quest_attempt_id=quest_attempt.id,
            skill_name=skill_in.skill_name,
            usage_count=skill_in.usage_count,
        )
        db.add(skill)

    db.commit()
    db.refresh(quest_attempt)
    return quest_attempt


@router.get(
    "/users/{user_id}/quest-attempts",
    response_model=List[schemas.QuestAttempt],
)
def list_quest_attempts(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    quests = (
        db.query(models.QuestAttempt)
        .filter(models.QuestAttempt.user_id == user_id)
        .order_by(models.QuestAttempt.started_at.desc())
        .all()
    )
    return quests


@router.post(
    "/quest-attempt",
    response_model=schemas.QuestAttemptTelemetryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_quest_attempt_telemetry(
    payload: schemas.QuestAttemptTelemetryIn,
    db: Session = Depends(get_db),
):
    # Find or create user by player_id
    user = (
        db.query(models.User)
        .filter(models.User.player_id == payload.player_id)
        .first()
    )

    if not user:
        user = models.User(
            player_id=payload.player_id,
            username=payload.username,
            email=payload.email,
        )
        db.add(user)
        db.flush()

    # Ensure RIASEC profile exists
    profile = user.riasec_profile
    if not profile:
        profile = models.UserRIASECProfile(
            user_id=user.id,
            realistic=0.0,
            investigative=0.0,
            artistic=0.0,
            social=0.0,
            enterprising=0.0,
            conventional=0.0,
        )
        db.add(profile)
        db.flush()

    # Create quest attempt
    quest_attempt = models.QuestAttempt(
        user_id=user.id,
        quest_id=payload.quest_id,
        quest_name=payload.quest_id,
        completed_at=datetime.utcnow(),
        time_spent_seconds=payload.time_spent_seconds,
        quest_result=payload.quest_result,
        success=1 if payload.quest_result.lower() == "success" else 0,
    )
    db.add(quest_attempt)
    db.flush()

    # Insert selected skills and update RIASEC profile counts
    for selected in payload.selected_skills:
        skill = models.SkillUsed(
            quest_attempt_id=quest_attempt.id,
            skill_name=selected.skill_name,
            riasec_code=selected.riasec_code,
            usage_count=1,
        )
        db.add(skill)

        code = selected.riasec_code.upper()
        if "R" in code:
            profile.realistic += 1
        if "I" in code:
            profile.investigative += 1
        if "A" in code:
            profile.artistic += 1
        if "S" in code:
            profile.social += 1
        if "E" in code:
            profile.enterprising += 1
        if "C" in code:
            profile.conventional += 1

    db.commit()

    return schemas.QuestAttemptTelemetryOut(
        success=True,
        message="Quest attempt telemetry recorded successfully.",
    )


@admin_router.get(
    "/users",
    response_model=List[schemas.AdminUser],
)
def admin_list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()

    return [
        schemas.AdminUser(
            user_id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            last_login=user.last_login,
            total_quest_attempts=len(user.quest_attempts),
        )
        for user in users
    ]


@admin_router.get(
    "/users/{user_id}",
    response_model=schemas.AdminUser,
)
def admin_get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return schemas.AdminUser(
        user_id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        last_login=user.last_login,
        total_quest_attempts=len(user.quest_attempts),
    )


@admin_router.get(
    "/users/{user_id}/performance",
    response_model=schemas.UserPerformance,
)
def admin_get_user_performance(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    attempts = (
        db.query(models.QuestAttempt)
        .filter(models.QuestAttempt.user_id == user_id)
        .order_by(models.QuestAttempt.started_at.desc())
        .all()
    )

    profile = user.riasec_profile
    if profile:
        aggregated = schemas.UserRIASECProfileBase(
            realistic=profile.realistic,
            investigative=profile.investigative,
            artistic=profile.artistic,
            social=profile.social,
            enterprising=profile.enterprising,
            conventional=profile.conventional,
        )
    else:
        aggregated = schemas.UserRIASECProfileBase(
            realistic=0.0,
            investigative=0.0,
            artistic=0.0,
            social=0.0,
            enterprising=0.0,
            conventional=0.0,
        )

    return schemas.UserPerformance(
        user_id=user.id,
        username=user.username,
        total_attempts=len(attempts),
        attempts=attempts,
        aggregated_riasec=aggregated,
    )


@admin_ui_router.get(
    "/users",
    response_class=HTMLResponse,
)
def admin_users_page(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).order_by(models.User.created_at.desc()).all()
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users,
        },
    )


@admin_ui_router.get(
    "/users/{user_id}",
    response_class=HTMLResponse,
)
def admin_user_performance_page(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    attempts = (
        db.query(models.QuestAttempt)
        .filter(models.QuestAttempt.user_id == user_id)
        .order_by(models.QuestAttempt.started_at.desc())
        .all()
    )

    profile = user.riasec_profile
    riasec = {
        "realistic": profile.realistic if profile else 0.0,
        "investigative": profile.investigative if profile else 0.0,
        "artistic": profile.artistic if profile else 0.0,
        "social": profile.social if profile else 0.0,
        "enterprising": profile.enterprising if profile else 0.0,
        "conventional": profile.conventional if profile else 0.0,
    }

    total_attempts = len(attempts)
    success_count = sum(1 for a in attempts if a.success == 1)
    total_time = sum(a.time_spent_seconds or 0 for a in attempts)

    success_rate = (success_count / total_attempts * 100) if total_attempts > 0 else 0.0
    avg_time = (total_time / total_attempts) if total_attempts > 0 else 0.0
    last_result = attempts[0].quest_result if attempts else "N/A"

    summary = {
        "total_attempts": total_attempts,
        "success_rate": success_rate,
        "avg_time_seconds": avg_time,
        "last_result": last_result,
    }

    return templates.TemplateResponse(
        "user_performance.html",
        {
            "request": request,
            "user": user,
            "attempts": attempts,
            "riasec": riasec,
            "summary": summary,
        },
    )

