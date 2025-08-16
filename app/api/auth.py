from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin, ShowUser
from app.models.user import User
from app.utils.security import ACCESS_TOKEN_EXPIRE_MINUTES, hash_password, verify_password, create_access_token
from app.core.deps import get_db
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=ShowUser)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está en uso")

    user = User(
        nombre=user_data.nombre,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        rol=user_data.rol,
        negocio_id=user_data.negocio_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token(
        data={"sub": str(user.id), "rol": user.rol},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}