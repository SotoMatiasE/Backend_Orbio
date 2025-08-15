from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.turno import TurnoCreate, ShowTurno
from app.db.session import get_db
from app.models import turno as TurnoModel, cliente as ClienteModel, servicio as ServicioModel
from app.models.agenda import Agenda  # importás directamente el modelo
from datetime import datetime, timedelta

router_publico = APIRouter()

@router_publico.post("/reserva", response_model=ShowTurno)
def reservar_turno(data: TurnoCreate, db: Session = Depends(get_db)):
    # Verificar si el empleado tiene agenda para esa fecha
    fecha_turno = data.fecha
    agenda = db.query(Agenda).filter(
        Agenda.empleado_id == data.empleado_id,
        Agenda.dia == fecha_turno.date().isoformat()
    ).first()

    if not agenda:
        raise HTTPException(status_code=400, detail="El empleado no tiene agenda ese día.")

    # Obtener la duración del servicio
    servicio = db.query(ServicioModel.Servicio).filter(
        ServicioModel.id == data.servicio_id
    ).first()

    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    # Calcular hora de fin del nuevo turno
    hora_inicio_turno = fecha_turno
    hora_fin_turno = hora_inicio_turno + timedelta(minutes=servicio.duracion_turno)

    # Verificar que el turno esté dentro del horario de agenda
    hora_inicio_agenda = datetime.combine(agenda.dia, agenda.hora_inicio)
    hora_fin_agenda = datetime.combine(agenda.dia, agenda.hora_fin)

    if not (hora_inicio_agenda <= hora_inicio_turno and hora_fin_turno <= hora_fin_agenda):
        raise HTTPException(status_code=400, detail="El turno está fuera del rango horario disponible")

    # Verificar solapamiento con otros turnos
    turnos_existentes = db.query(TurnoModel.Turno).filter(
        TurnoModel.empleado_id == data.empleado_id,
        TurnoModel.fecha.between(hora_inicio_agenda, hora_fin_agenda)
    ).all()

    for turno in turnos_existentes:
        turno_inicio = turno.fecha
        turno_fin = turno_inicio + timedelta(minutes=servicio.duracion_turno)

        if (hora_inicio_turno < turno_fin and hora_fin_turno > turno_inicio):
            raise HTTPException(status_code=400, detail="Este horario ya está ocupado")

    # Crear cliente si no existe
    cliente = None
    if data.cliente_email:
        cliente = db.query(ClienteModel.Cliente).filter_by(email=data.cliente_email).first()
    if not cliente and data.cliente_telefono:
        cliente = db.query(ClienteModel.Cliente).filter_by(telefono=data.cliente_telefono).first()
    if not cliente:
        cliente = ClienteModel.Cliente(
            nombre=data.cliente_nombre,
            email=data.cliente_email,
            telefono=data.cliente_telefono
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

    # Crear turno
    nuevo_turno = TurnoModel.Turno(
        fecha=data.fecha,
        cliente_nombre=data.cliente_nombre,
        cliente_email=data.cliente_email,
        cliente_telefono=data.cliente_telefono,
        metodo_pago=data.metodo_pago,
        monto_pagado=data.monto_pagado,
        estado=data.estado,
        servicio_id=data.servicio_id,
        empleado_id=data.empleado_id,
        cliente_id=cliente.id
    )
    db.add(nuevo_turno)
    db.commit()
    db.refresh(nuevo_turno)
    return nuevo_turno

#DISPONIBILIDAD
from app.models.agenda import Agenda
from app.models.turno import Turno
from datetime import datetime, timedelta, time

@router_publico.get("/disponibilidad/{empleado_id}")
def obtener_disponibilidad(empleado_id: int, db: Session = Depends(get_db)):
    hoy = datetime.now().date()
    dias_disponibles = []

    for i in range(14):  # próximos 14 días
        dia_actual = hoy + timedelta(days=i)

        agenda = db.query(Agenda).filter_by(
            empleado_id=empleado_id,
            dia=dia_actual
        ).first()

        if not agenda:
            continue

        hora_actual = datetime.combine(dia_actual, agenda.hora_inicio)
        hora_fin = datetime.combine(dia_actual, agenda.hora_fin)

        turnos_existentes = db.query(Turno).filter(
            Turno.empleado_id == empleado_id,
            Turno.fecha.between(hora_actual, hora_fin)
        ).all()

        horarios_ocupados = [
            (turno.fecha, turno.fecha + timedelta(minutes=agenda.duracion_turno))
            for turno in turnos_existentes
        ]

        horarios_disponibles = []
        while hora_actual + timedelta(minutes=agenda.duracion_turno) <= hora_fin:
            inicio = hora_actual
            fin = hora_actual + timedelta(minutes=agenda.duracion_turno)

            # Validar superposición
            ocupado = any(
                inicio < o_fin and fin > o_inicio
                for o_inicio, o_fin in horarios_ocupados
            )

            if not ocupado:
                horarios_disponibles.append(inicio.strftime("%H:%M"))

            hora_actual = fin

        if horarios_disponibles:
            dias_disponibles.append({
                "fecha": dia_actual.isoformat(),
                "horarios": horarios_disponibles
            })

    return dias_disponibles

