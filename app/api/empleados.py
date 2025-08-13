from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.schemas.empleado import EmpleadoCreate, EmpleadoOut
from app.utils.security import hash_password
from app.core.deps import get_db, get_current_user
from app.core.roles import verify_role

router = APIRouter(prefix="/empleados", tags=["Empleados"])

@router.post("/", response_model=EmpleadoOut)
def crear_empleado(data: EmpleadoCreate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("admin"))):

    existente = db.query(User).filter(User.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    nuevo_empleado = User(
        nombre=data.nombre,
        email=data.email,
        hashed_password=hash_password(data.password),
        rol=UserRole.empleado,
        negocio_id=current_user.negocio_id
    )
    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)
    return nuevo_empleado

@router.get("/", response_model=list[EmpleadoOut])
def listar_empleados(db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("admin"))):
    return db.query(User).filter(User.rol == UserRole.empleado,
                                User.negocio_id == current_user.negocio_id).all()

@router.delete("/{empleado_id}")
def eliminar_empleado(empleado_id: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("admin"))):
    empleado = db.query(User).filter(User.id == empleado_id,
                                    User.rol == UserRole.empleado,
                                    User.negocio_id == current_user.negocio_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    db.delete(empleado)
    db.commit()
    return {"mensaje": "Empleado eliminado"}