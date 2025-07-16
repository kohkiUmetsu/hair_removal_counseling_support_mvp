"""
Authentication API router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    Token,
    TokenRefresh,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest
)
from app.schemas.user import User as UserSchema


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    User login endpoint
    """
    auth_service = AuthService(db)
    return auth_service.login(login_data)


@router.post("/refresh", response_model=Token)
def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token endpoint
    """
    auth_service = AuthService(db)
    return auth_service.refresh_access_token(token_data.refresh_token)


@router.post("/register", response_model=UserSchema)
def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    User registration endpoint (admin only in production)
    """
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)


@router.post("/password-reset-request")
def request_password_reset(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset endpoint
    """
    auth_service = AuthService(db)
    token = auth_service.request_password_reset(request_data.email)
    
    return {
        "message": "If your email is registered, you will receive a password reset link.",
        "reset_token": token  # In production, this would be sent via email
    }


@router.post("/password-reset-confirm")
def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset endpoint
    """
    auth_service = AuthService(db)
    success = auth_service.reset_password(reset_data.token, reset_data.new_password)
    
    if success:
        return {"message": "Password reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password"
        )


@router.post("/change-password")
def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change password endpoint
    """
    auth_service = AuthService(db)
    success = auth_service.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    
    if success:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )


@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information
    """
    return current_user


@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side token removal)
    """
    return {"message": "Successfully logged out"}