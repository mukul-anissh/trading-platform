from fastapi import APIRouter, Depends
from app.schemas.users import UserOut
from app.utils.security import get_current_user
from app.models import User

router = APIRouter(prefix='/users', tags=['Users'])

@router.get('/me', response_model=UserOut)
def get_user_details(me: User = Depends(get_current_user)):
    return me