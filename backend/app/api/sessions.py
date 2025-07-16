from typing import Any, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.api import deps
from app.models.user import User
from app.models.session import CounselingSession
from app.schemas.session import (
    Session as SessionSchema,
    SessionCreate,
    SessionUpdate,
    SessionWithRelations
)


router = APIRouter()


@router.get("/", response_model=List[SessionWithRelations])
def read_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve sessions based on user role and permissions
    """
    query = db.query(CounselingSession)
    
    # Filter based on user role
    if current_user.role == "counselor":
        query = query.filter(CounselingSession.counselor_id == current_user.id)
    elif current_user.role == "manager":
        # Managers can see sessions from their clinic
        query = query.join(User, CounselingSession.counselor_id == User.id).filter(
            User.clinic_id == current_user.clinic_id
        )
    # Admins can see all sessions (no additional filter)
    
    sessions = query.offset(skip).limit(limit).all()
    return sessions


@router.post("/", response_model=SessionSchema)
def create_session(
    *,
    db: Session = Depends(deps.get_db),
    session_in: SessionCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new counseling session
    """
    # Validate that counselor belongs to current user's clinic (for managers)
    if current_user.role == "manager":
        counselor = db.query(User).filter(User.id == session_in.counselor_id).first()
        if not counselor or counselor.clinic_id != current_user.clinic_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create session for counselor outside your clinic"
            )
    elif current_user.role == "counselor":
        # Counselors can only create sessions for themselves
        if session_in.counselor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Counselors can only create sessions for themselves"
            )
    
    session = CounselingSession(
        id=str(uuid4()),
        **session_in.dict(),
        status="recorded"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionSchema)
def read_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get session by ID
    """
    session = db.query(CounselingSession).filter(CounselingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check permissions
    if current_user.role == "counselor" and session.counselor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == "manager":
        counselor = db.query(User).filter(User.id == session.counselor_id).first()
        if not counselor or counselor.clinic_id != current_user.clinic_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return session


@router.put("/{session_id}", response_model=SessionSchema)
def update_session(
    *,
    db: Session = Depends(deps.get_db),
    session_id: str,
    session_in: SessionUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update session
    """
    session = db.query(CounselingSession).filter(CounselingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check permissions (same as read_session)
    if current_user.role == "counselor" and session.counselor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == "manager":
        counselor = db.query(User).filter(User.id == session.counselor_id).first()
        if not counselor or counselor.clinic_id != current_user.clinic_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    # Update session
    update_data = session_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/upload-recording")
def upload_recording(
    *,
    db: Session = Depends(deps.get_db),
    session_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload audio recording for a session
    """
    session = db.query(CounselingSession).filter(CounselingSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check permissions
    if current_user.role == "counselor" and session.counselor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate file type
    if not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file"
        )
    
    # TODO: Implement actual file upload to S3
    # For now, we'll just simulate the upload
    recording_url = f"s3://counseling-recordings/{session_id}/{file.filename}"
    
    session.recording_url = recording_url
    session.status = "recorded"
    db.add(session)
    db.commit()
    
    return {"message": "Recording uploaded successfully", "recording_url": recording_url}