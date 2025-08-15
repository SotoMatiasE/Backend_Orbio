from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.deps import get_current_user
from fastapi import Depends

app = FastAPI()

# Middleware CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta protegida
@app.get("/protegido")
def ruta_protegida(usuario=Depends(get_current_user)):
    return {"mensaje": f"Hola {usuario.nombre}, accediste con tu token."}

#CREAR TABLAS
from app.db.session import Base, engine
from app import models 

Base.metadata.create_all(bind=engine)

from app.api import auth
app.include_router(auth.router)

#Superadmin
# El Super Admin ahora puede:
# Crear, listar, modificar y eliminar negocios y empleados
from app.api import superadmin
app.include_router(superadmin.router)

#Empleados
from app.api import empleados
app.include_router(empleados.router)

#Ruta publica cliente
from app.api.publico import router_publico
app.include_router(router_publico)

