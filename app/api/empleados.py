from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.db.session import get_db
from app.models import turno as TurnoModel, agenda as AgendaModel, servicio as ServicioModel, user as UserModel
from app.schemas.turno import ShowTurno, TurnoUpdate
from app.schemas.servicio import ServicioCreate, ServicioOut, ServicioUpdate, ServicioCreateAdmin
from app.schemas.empleado import EmpleadoCreate, EmpleadoOut, AgendaCreateEmpleado, ServicioEmpleado, ServicioUpdateEmpleado, EmpleadoUpdate
from app.schemas.agenda import ShowAgenda
from app.utils.security import hash_password
from app.core.roles import verify_role

router = APIRouter(prefix="/empleados", tags=["Empleados"])

# --- FUNCIONALIDADES EMPLEADO ---
@router.get("/agenda", response_model=list[ShowAgenda])
def listar_mi_agenda(db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("empleado"))):
    hoy = date.today()
    max_dia = hoy + timedelta(weeks=2)
    return db.query(AgendaModel.Agenda).filter(
        AgendaModel.Agenda.empleado_id == current_user.id,
        AgendaModel.Agenda.dia >= hoy,
        AgendaModel.Agenda.dia <= max_dia
    ).all()

@router.post("/agenda", response_model=ShowAgenda)
def crear_mi_agenda(data: AgendaCreateEmpleado,
                    db: Session = Depends(get_db),
                    current_user: UserModel.User = Depends(verify_role("empleado"))):
    agendas_existentes = db.query(AgendaModel.Agenda).filter(
        AgendaModel.Agenda.empleado_id == current_user.id,
        AgendaModel.Agenda.dia == data.dia
    ).all()

    for agenda in agendas_existentes:
        if (data.hora_inicio < agenda.hora_fin and data.hora_fin > agenda.hora_inicio):
            raise HTTPException(status_code=400, detail="Existe una agenda solapada en el mismo día")

    nueva = AgendaModel.Agenda(**data.dict(), empleado_id=current_user.id)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/mis-turnos", response_model=list[ShowTurno])
def listar_mis_turnos(db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("empleado"))):
    return db.query(TurnoModel.Turno).filter(TurnoModel.Turno.empleado_id == current_user.id).all()

@router.put("/turnos/{turno_id}", response_model=ShowTurno)
def actualizar_turno_empleado(turno_id: int, update: TurnoUpdate,
                                db: Session = Depends(get_db),
                                current_user: UserModel.User = Depends(verify_role("empleado"))):
    turno = db.query(TurnoModel.Turno).filter(
        TurnoModel.Turno.id == turno_id,
        TurnoModel.Turno.empleado_id == current_user.id
    ).first()
    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(turno, field, value)
    db.commit()
    db.refresh(turno)
    return turno

@router.post("/servicios")
def crear_mi_servicio(data: ServicioEmpleado,
                        db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("empleado"))):
    nuevo = ServicioModel.Servicio(
        **data.dict(),
        negocio_id=current_user.negocio_id,
        empleado_id=current_user.id
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/servicios/{servicio_id}")
def editar_mi_servicio(servicio_id: int, data: ServicioUpdateEmpleado,
                        db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("empleado"))):
    servicio = db.query(ServicioModel.Servicio).filter(
        ServicioModel.Servicio.id == servicio_id,
        ServicioModel.Servicio.empleado_id == current_user.id
    ).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(servicio, field, value)
    db.commit()
    db.refresh(servicio)
    return servicio

@router.delete("/servicios/{servicio_id}")
def eliminar_mi_servicio(servicio_id: int,
                            db: Session = Depends(get_db),
                            current_user: UserModel.User = Depends(verify_role("empleado"))):
    servicio = db.query(ServicioModel.Servicio).filter(
        ServicioModel.Servicio.id == servicio_id,
        ServicioModel.Servicio.empleado_id == current_user.id
    ).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(servicio)
    db.commit()
    return {"detail": "Servicio eliminado con éxito"}

@router.post("/empleado/servicio", response_model=ServicioOut)
def crear_servicio_empleado(
    data: ServicioCreate,
    db: Session = Depends(get_db),
    current_user: UserModel.User = Depends(verify_role("empleado"))
):
    nuevo_servicio = ServicioModel.Servicio(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
        negocio_id=data.negocio_id,
        empleado_id=current_user.id,
        duracion=data.duracion
    )
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    return nuevo_servicio

@router.put("/empleado/servicio/{servicio_id}", response_model=ServicioOut)
def editar_servicio_empleado(
    servicio_id: int,
    data: ServicioUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel.User = Depends(verify_role("empleado"))
):
    servicio = db.query(ServicioModel.Servicio).filter_by(id=servicio_id, empleado_id=current_user.id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado o no te pertenece")

    if data.nombre is not None:
        servicio.nombre = data.nombre
    if data.descripcion is not None:
        servicio.descripcion = data.descripcion
    if data.precio is not None:
        servicio.precio = data.precio
    if data.duracion is not None:
        servicio.duracion = data.duracion

    db.commit()
    db.refresh(servicio)
    return servicio

@router.delete("/empleado/servicio/{servicio_id}")
def eliminar_servicio_empleado(
    servicio_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel.User = Depends(verify_role("empleado"))
):
    servicio = db.query(ServicioModel.Servicio).filter_by(id=servicio_id, empleado_id=current_user.id).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado o no te pertenece")

    db.delete(servicio)
    db.commit()
    return {"message": "Servicio eliminado correctamente"}


# --- FUNCIONALIDADES ADMIN ---
@router.get("/admin", response_model=list[EmpleadoOut])
def listar_empleados(db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("admin"))):
    return db.query(UserModel.User).filter(
        UserModel.User.rol == UserModel.UserRole.empleado,
        UserModel.User.negocio_id == current_user.negocio_id
    ).all()

@router.post("/admin", response_model=EmpleadoOut)
def crear_empleado(data: EmpleadoCreate,
                    db: Session = Depends(get_db),
                    current_user: UserModel.User = Depends(verify_role("admin"))):
    existente = db.query(UserModel.User).filter(UserModel.User.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    nuevo = UserModel.User(
        nombre=data.nombre,
        email=data.email,
        hashed_password=hash_password(data.password),
        rol=UserModel.UserRole.empleado,
        negocio_id=current_user.negocio_id
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/admin/{empleado_id:int}", response_model=EmpleadoOut)
def obtener_empleado(empleado_id: int,
                        db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("admin"))):
    empleado = db.query(UserModel.User).filter(
        UserModel.User.id == empleado_id,
        UserModel.User.rol == UserModel.UserRole.empleado,
        UserModel.User.negocio_id == current_user.negocio_id
    ).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@router.put("/admin/{empleado_id:int}", response_model=EmpleadoOut)
def editar_empleado(empleado_id: int, data: EmpleadoUpdate,
                    db: Session = Depends(get_db),
                    current_user: UserModel.User = Depends(verify_role("admin"))):
    empleado = db.query(UserModel.User).filter(
        UserModel.User.id == empleado_id,
        UserModel.User.rol == UserModel.UserRole.empleado,
        UserModel.User.negocio_id == current_user.negocio_id
    ).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    for field, value in data.dict(exclude_unset=True).items():
        if field == "password":
            setattr(empleado, "hashed_password", hash_password(value))
        else:
            setattr(empleado, field, value)
    db.commit()
    db.refresh(empleado)
    return empleado

@router.delete("/admin/{empleado_id:int}")
def eliminar_empleado(empleado_id: int,
                        db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("admin"))):
    empleado = db.query(UserModel.User).filter(
        UserModel.User.id == empleado_id,
        UserModel.User.rol == UserModel.UserRole.empleado,
        UserModel.User.negocio_id == current_user.negocio_id
    ).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    db.delete(empleado)
    db.commit()
    return {"mensaje": "Empleado eliminado"}

@router.post("/admin/{empleado_id:int}/servicios", response_model=ServicioOut)
def crear_servicio_para_empleado(
    empleado_id: int,
    data: ServicioCreateAdmin,
    db: Session = Depends(get_db),
    current_user: UserModel.User = Depends(verify_role("admin"))
):
    empleado = db.query(UserModel.User).filter(
        UserModel.User.id == empleado_id,
        UserModel.User.rol == UserModel.UserRole.empleado,
        UserModel.User.negocio_id == current_user.negocio_id
    ).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    nuevo_servicio = ServicioModel.Servicio(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
        duracion=data.duracion,
        direccion=data.direccion,
        empleado_id=empleado.id,
        negocio_id=current_user.negocio_id
    )
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    return nuevo_servicio

@router.put("/admin/servicios/{servicio_id}", response_model=ServicioOut)
def editar_servicio(servicio_id: int, data: ServicioUpdate,
                    db: Session = Depends(get_db),
                    current_user: UserModel.User = Depends(verify_role("admin"))):
    servicio = db.query(ServicioModel.Servicio).filter(
        ServicioModel.Servicio.id == servicio_id,
        ServicioModel.Servicio.negocio_id == current_user.negocio_id
    ).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(servicio, field, value)
    db.commit()
    db.refresh(servicio)
    return servicio

@router.delete("/admin/servicios/{servicio_id}")
def eliminar_servicio(servicio_id: int,
                        db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("admin"))):
    servicio = db.query(ServicioModel.Servicio).filter(
        ServicioModel.Servicio.id == servicio_id,
        ServicioModel.Servicio.negocio_id == current_user.negocio_id
    ).first()
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(servicio)
    db.commit()
    return {"mensaje": "Servicio eliminado correctamente"}
