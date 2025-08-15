from fastapi import APIRouter
from app.controllers import auth_controller
from app.models.password_reset import PasswordResetRequest, PasswordResetConfirm

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/forgot-password")
async def forgot_password_route(request: PasswordResetRequest):
    return await auth_controller.forgot_password_handler(request)

@router.post("/reset-password")
async def reset_password_route(request: PasswordResetConfirm):
    return await auth_controller.reset_password_handler(request)

