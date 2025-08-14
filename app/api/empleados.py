from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.db.session import get_db
from app.models import turno as TurnoModel, agenda as AgendaModel, servicio as ServicioModel, user as UserModel
from app.schemas.turno import ShowTurno, TurnoEmpleadoUpdate
from app.schemas.empleado import EmpleadoCreate, EmpleadoOut, AgendaCreateEmpleado, ServicioEmpleado, ServicioUpdateEmpleado
from app.schemas.agenda import ShowAgenda
from app.utils.security import hash_password
from app.core.roles import verify_role

router = APIRouter(prefix="/empleados", tags=["Empleados"])

# --- FUNCIONALIDADES ADMIN ---
@router.post("/", response_model=EmpleadoOut)
def crear_empleado(data: EmpleadoCreate,
                    db: Session = Depends(get_db),
                    current_user: UserModel.User = Depends(verify_role("admin"))):
    existente = db.query(UserModel.User).filter(UserModel.User.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    nuevo_empleado = UserModel.User(
        nombre=data.nombre,
        email=data.email,
        hashed_password=hash_password(data.password),
        rol=UserModel.UserRole.empleado,
        negocio_id=current_user.negocio_id
    )
    db.add(nuevo_empleado)
    db.commit()
    db.refresh(nuevo_empleado)
    return nuevo_empleado

@router.get("/", response_model=list[EmpleadoOut])
def listar_empleados(db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("admin"))):
    return db.query(UserModel.User).filter(
        UserModel.User.rol == UserModel.UserRole.empleado,
        UserModel.User.negocio_id == current_user.negocio_id
    ).all()

@router.delete("/{empleado_id}")
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

# --- FUNCIONALIDADES EMPLEADO ---
@router.get("/mis-turnos", response_model=list[ShowTurno])
def listar_mis_turnos(db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("empleado"))):
    return db.query(TurnoModel.Turno).filter(TurnoModel.Turno.empleado_id == current_user.id).all()

@router.put("/turnos/{turno_id}", response_model=ShowTurno)
def actualizar_turno_empleado(turno_id: int, update: TurnoEmpleadoUpdate,
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

@router.get("/agenda", response_model=list[ShowAgenda])
def listar_mi_agenda(db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("empleado"))):
    hoy = date.today()
    max_dia = hoy + timedelta(weeks=2)
    return db.query(AgendaModel.Agenda).filter(
        AgendaModel.Agenda.empleado_id == current_user.id,
        AgendaModel.Agenda.dia >= hoy.isoformat(),
        AgendaModel.Agenda.dia <= max_dia.isoformat()
    ).all()

@router.post("/servicios")
def crear_mi_servicio(data: ServicioEmpleado,
                        db: Session = Depends(get_db),
                        current_user: UserModel.User = Depends(verify_role("empleado"))):
    nuevo = ServicioModel.Servicio(**data.dict(), negocio_id=current_user.negocio_id, empleado_id=current_user.id)
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
