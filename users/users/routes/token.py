from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/current"
)
async def current_user():
    pass

@router.post(
    "/verify"
)
async def verify_token():
    pass

@router.post(
    "/refresh"
)
async def refresh_token():
    pass