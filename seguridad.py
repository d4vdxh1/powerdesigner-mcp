"""Control de escritura para modelos PowerDesigner.

El servidor puede consultar cualquier modelo abierto, pero solo puede editar
el archivo exacto autorizado mediante POWERDESIGNER_MCP_WRITE_MODEL.
"""
import os
from pathlib import Path


def verificar_modelo_autorizado(ruta_modelo: str) -> Path:
    """Devuelve la ruta canónica o bloquea la escritura antes de modificar."""
    ruta_permitida = os.environ.get("POWERDESIGNER_MCP_WRITE_MODEL", "").strip()
    if not ruta_permitida:
        raise PermissionError(
            "Edicion deshabilitada. Configura write_model con la ruta completa "
            "del archivo autorizado y reinicia el servidor MCP."
        )

    actual = Path(ruta_modelo)
    autorizada = Path(ruta_permitida)
    if not actual.is_absolute() or not autorizada.is_absolute():
        raise PermissionError("La escritura requiere rutas absolutas.")

    if not actual.is_file() or not autorizada.is_file():
        raise PermissionError("El modelo activo y el autorizado deben existir en disco.")

    normalizar = lambda ruta: os.path.normcase(str(ruta.resolve(strict=True)))
    if normalizar(actual) != normalizar(autorizada):
        raise PermissionError(
            "Edicion bloqueada: el archivo activo no es el modelo autorizado."
        )
    return actual.resolve(strict=True)
