#VALIDAR ROLES

from fastapi import Depends, HTTPException, status
from app.core.deps import get_current_user
from app.models.user import User

def verify_role(required_role: str):
    def role_dependency(current_user: User = Depends(get_current_user)):
        actual_role = str(getattr(current_user.rol, "value", current_user.rol))
        print(f"🔍 Verificando rol: actual = {actual_role} | requerido = {required_role}")
        if actual_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: se requiere rol '{required_role}'"
            )
        return current_user
    return role_dependency


