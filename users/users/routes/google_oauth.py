from fastapi import HTTPException

from db_handler import DocumentNotFound
from ..dependencies import get_google_auth_client, get_mongo_client, get_jwt_helper
from ..models import GoogleLoginIn

from fastapi import APIRouter, Depends

router = APIRouter()

@router.post(
    "/o/google-oauth2"
)
async def login(
    google_data: GoogleLoginIn,
    auth_client=Depends(get_google_auth_client),
    db_client=Depends(get_mongo_client),
    helper=Depends(get_jwt_helper)
):
    # viene con user data 
    google_response = await auth_client.get_user_data(google_data.code)
    user_email = google_response["email"]

    # ver si tengo este user en db}
    try:
        user = db_client.get_user_by_email(user_email)
    except DocumentNotFound:
        new_user_dict = {
            "auth_source": {
                "name": "google_auth2",
                "username": user_email,
                "email": user_email
            }
        }
        # error aqui debe generar error 500??
        user = db_client.create_new_user(new_user_dict)
    
    except Exception as e:
        # otro error
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    

    user_token = helper.create_user_token(user)
    refresh_token = helper.create_refresh_token(user)
    
    return {
        "access": user_token,
        "refresh": refresh_token
    }
  