"""Authentication routes: signup and login."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from dto.login_dto import LoginDto
from dto.login_token_response_dto import LoginTokenResponseDto
from dto.refresh_token_request_dto import RefreshTokenRequestDto
from dto.signup_dto import SignupDto
from dto.token_response_dto import TokenResponseDto
from dto.user_public_dto import UserPublicDto
from services.auth_service import AuthService
from utils.logger import get_logger


def _get_logger():
    return get_logger(__name__)


router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.container.auth_service()


@router.post(
    "/signup",
    response_model=UserPublicDto,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    body: SignupDto,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserPublicDto:
    try:
        user = auth_service.signup(body)
        _get_logger().info("User signed up username=%s role=%s", user.username, user.role)
        return user
    except ValueError as e:
        msg = str(e)
        if "Username already" in msg:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=msg,
            ) from e
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=msg) from e


@router.post("/login", response_model=LoginTokenResponseDto, response_model_by_alias=True)
def login(
    body: LoginDto,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginTokenResponseDto:
    try:
        tokens = auth_service.login(body)
        _get_logger().info("User logged in username=%s", body.username)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e


@router.post("/refresh", response_model=TokenResponseDto, response_model_by_alias=True)
def refresh_access_token(
    body: RefreshTokenRequestDto,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponseDto:
    try:
        return auth_service.refresh_access_token(body)
    except ValueError as e:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e
