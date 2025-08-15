from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.negocio import NegocioCreate, NegocioUpdate
from app.models.negocio import Negocio
from app.models.user import User, UserRole
from app.utils.security import hash_password
from app.core.deps import get_db
from app.core.roles import verify_role
from app.schemas.empleado import EmpleadoUpdate, EmpleadoCreate
from app.models.servicio import Servicio
from app.schemas.servicio import ServicioCreate, ServicioUpdate
from app.models.turno import Turno
from app.schemas.turno import TurnoCreate, TurnoUpdate

router = APIRouter(prefix="/superadmin", tags=["Super Admin"])

@router.post("/negocios")
def crear_negocio(data: NegocioCreate, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("super_admin"))):

    alias_existente = db.query(Negocio).filter(Negocio.alias == data.alias).first()
    if alias_existente:
        raise HTTPException(status_code=400, detail="Alias ya en uso")

    admin_existente = db.query(User).filter(User.email == data.admin_email).first()
    if admin_existente:
        raise HTTPException(status_code=400, detail="Email del admin ya existe")

    nuevo_negocio = Negocio(
        nombre=data.nombre,
        alias=data.alias,
        direccion=data.direccion,
        provincia=data.provincia
    )
    db.add(nuevo_negocio)
    db.commit()
    db.refresh(nuevo_negocio)

    nuevo_admin = User(
        nombre=data.admin_nombre,
        email=data.admin_email,
        hashed_password=hash_password(data.admin_password),
        rol=UserRole.admin,
        negocio_id=nuevo_negocio.id
    )
    db.add(nuevo_admin)

    nuevo_negocio.dueño_id = nuevo_admin.id
    db.commit()

    return {
        "mensaje": "Negocio y admin creados correctamente",
        "negocio_id": nuevo_negocio.id,
        "admin_id": nuevo_admin.id
    }

@router.get("/negocios")
def listar_negocios(db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("super_admin"))):
    return db.query(Negocio).all()

@router.put("/negocios/{negocio_id}")
def actualizar_negocio(negocio_id: int, update: NegocioUpdate,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(verify_role("super_admin"))):
    negocio = db.query(Negocio).filter(Negocio.id == negocio_id).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    for field, value in update.dict(exclude_unset=True).items():
        setattr(negocio, field, value)

    db.commit()
    db.refresh(negocio)
    return negocio

@router.delete("/negocios/{negocio_id}")
def eliminar_negocio(negocio_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(verify_role("super_admin"))):
    negocio = db.query(Negocio).filter(Negocio.id == negocio_id).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    db.delete(negocio)
    db.commit()
    return {"mensaje": "Negocio eliminado"}

@router.get("/negocios/{negocio_id}/empleados")
def listar_empleados_por_negocio(
    negocio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_role("super_admin"))
):
    negocio = db.query(Negocio).filter(Negocio.id == negocio_id).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    empleados = db.query(User).filter(
        User.negocio_id == negocio_id,
        User.rol == UserRole.empleado
    ).all()

    return empleados

#Obtener todos los servicios de un negocio específico:
@router.get("/negocios/{negocio_id}/servicios")
def listar_servicios_de_negocio(
    negocio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_role("super_admin"))
):
    negocio = db.query(Negocio).filter(Negocio.id == negocio_id).first()
    if not negocio:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")

    servicios = db.query(Servicio).filter(Servicio.negocio_id == negocio_id).all()
    return servicios

#Obtener todos los servicios de un empleado específico dentro de un negocio específico
@router.get("/negocios/{negocio_id}/empleados/{empleado_id}/servicios")
def listar_servicios_empleado_de_negocio(
    negocio_id: int,
    empleado_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_role("super_admin"))
):
    empleado = db.query(User).filter(
        User.id == empleado_id,
        User.negocio_id == negocio_id,
        User.rol == UserRole.empleado
    ).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado en este negocio")

    servicios = db.query(Servicio).filter(
        Servicio.negocio_id == negocio_id,
        Servicio.empleado_id == empleado_id
    ).all()

    return servicios


# CRUD de empleados (modo Super Admin)

@router.post("/empleados")
def crear_empleado(data: EmpleadoCreate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("super_admin"))):
    existente = db.query(User).filter(User.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    nuevo_empleado = User(
        nombre=data.nombre,
        email=data.email,
        hashed_password=hash_password(data.password),
        rol=UserRole.empleado,
        negocio_id=data.negocio_id
    )
    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)
    return {"mensaje": "Empleado creado correctamente", "empleado_id": nuevo_empleado.id}

@router.post("/empleados/{empleado_id}/servicios")
def crear_servicio_para_empleado(
    empleado_id: int,
    data: ServicioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_role("super_admin"))
):
    empleado = db.query(User).filter(
        User.id == empleado_id,
        User.rol == UserRole.empleado
    ).first()

    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    nuevo_servicio = Servicio(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
        duracion=data.duracion,
        negocio_id=empleado.negocio_id,  # lo toma del empleado
        empleado_id=empleado.id
    )
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)

    return {
        "mensaje": "Servicio creado para el empleado correctamente",
        "servicio_id": nuevo_servicio.id
    }

@router.get("/empleados")
def listar_todos_empleados(db: Session = Depends(get_db),
                            current_user: User = Depends(verify_role("super_admin"))):
    return db.query(User).filter(User.rol == UserRole.empleado).all()

@router.put("/empleados/{empleado_id}")
def editar_empleado(empleado_id: int, update: EmpleadoUpdate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("super_admin"))):
    empleado = db.query(User).filter(User.id == empleado_id, User.rol == UserRole.empleado).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    for field, value in update.dict(exclude_unset=True).items():
        setattr(empleado, field, value)

    db.commit()
    db.refresh(empleado)
    return empleado

@router.delete("/empleados/{empleado_id}")
def eliminar_empleado(empleado_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(verify_role("super_admin"))):
    empleado = db.query(User).filter(User.id == empleado_id, User.rol == UserRole.empleado).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    db.delete(empleado)
    db.commit()
    return {"mensaje": "Empleado eliminado correctamente"}

# CRUD Servicios

@router.post("/servicios")
def crear_servicio(data: ServicioCreate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("super_admin"))):
    nuevo = Servicio(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/servicios")
def listar_servicios_por_negocio(
    negocio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_role("super_admin"))
):
    servicios = db.query(Servicio).filter(Servicio.negocio_id == negocio_id).all()
    return servicios


@router.put("/servicios/{servicio_id}")
def editar_servicio(servicio_id: int, update: ServicioUpdate,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(verify_role("super_admin"))):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(servicio, field, value)
    db.commit()
    db.refresh(servicio)
    return servicio

@router.delete("/servicios/{servicio_id}")
def eliminar_servicio(servicio_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(verify_role("super_admin"))):
    servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(servicio)
    db.commit()
    return {"mensaje": "Servicio eliminado"}

# Turnos

@router.post("/turnos")
def crear_turno(data: TurnoCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(verify_role("super_admin"))):
    nuevo = Turno(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/turnos")
def listar_turnos(db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("super_admin"))):
    return db.query(Turno).all()

@router.put("/turnos/{turno_id}")
def actualizar_turno(turno_id: int, update: TurnoUpdate,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(verify_role("super_admin"))):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(turno, field, value)
    db.commit()
    db.refresh(turno)
    return turno

@router.delete("/turnos/{turno_id}")
def eliminar_turno(turno_id: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(verify_role("super_admin"))):
    turno = db.query(Turno).filter(Turno.id == turno_id).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    db.delete(turno)
    db.commit()
    return {"mensaje": "Turno eliminado"}