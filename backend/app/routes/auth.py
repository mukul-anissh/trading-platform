from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserOut, UserLogin, Token
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/signup', response_model=UserOut)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    email = user.email.lower()
    existing = db.query(User).filter(User.email==email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    new_user = User(email=email, username=user.username, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post('/login', response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    email = user.email.lower()
    fetch_user = db.query(User).filter(User.email == email).first()
    if not fetch_user or not verify_password(user.password, fetch_user.password_hash):
        raise HTTPException(status_code=400, detail='Invalid Credentials')
    token = create_access_token({'sub':str(fetch_user.id)})
    return {'access_token': token, 'token_type': 'bearer'}