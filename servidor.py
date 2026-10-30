import shutil
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
import pythoncom
import win32com.client
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "PowerDesigner MCP", host="127.0.0.1", port=8000,
    stateless_http=True, json_response=True,
)
respaldos = {}

@contextmanager
def conexion():
    pythoncom.CoInitialize()
    pd = modelo = None
    try:
        pd = win32com.client.Dispatch("PowerDesigner.Application")
        modelo = pd.ActiveModel
        if modelo is None:
            raise ValueError("No hay modelo activo.")
        yield pd, modelo
    finally:
        modelo = pd = None
        pythoncom.CoUninitialize()

def dato(obj, nombre):
    try:
        valor = getattr(obj, nombre)
        return valor if isinstance(valor, (str, int, float, bool)) else str(valor)
    except Exception:
        return None

def resumen(obj):
    return {
        k: dato(obj, k)
        for k in ("ObjectID", "Name", "Code", "ClassName")
    }

def resolver(modelo, ruta):
    obj = modelo
    for paso in ruta:
        coleccion, identificador = paso.split(":", 1)
        if coleccion.startswith("_"):
            raise ValueError("Coleccion no permitida.")
        encontrado = None
        for indice, candidato in enumerate(getattr(obj, coleccion)):
            coincide = (
                identificador == "@" + str(indice)
                if identificador.startswith("@")
                else str(dato(candidato, "ObjectID")) == identificador
            )
            if coincide:
                encontrado = candidato
                break
        if encontrado is None:
            raise ValueError("Objeto no encontrado: " + paso)
        obj = encontrado
    return obj

def respaldar(modelo):
    nombre = str(modelo.FileName or "")
    archivo = Path(nombre)
    if not nombre or not archivo.is_file():
        raise ValueError("Guarda primero el modelo desde PowerDesigner.")
    clave = str(archivo.resolve())
    if clave not in respaldos:
        sello = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        copia = archivo.with_name(
            archivo.stem + "_respaldo_" + sello + archivo.suffix
        )
        shutil.copy2(archivo, copia)
        respaldos[clave] = str(copia)
    return respaldos[clave]

@mcp.tool()
def consultar_modelo_activo() -> dict:
    """Consulta version, modelo y archivo activo."""
    with conexion() as (pd, modelo):
        return {
            "version": str(pd.Version),
            "modelo": resumen(modelo),
            "archivo": dato(modelo, "FileName"),
        }

@mcp.tool()
def listar_coleccion(
    coleccion: str, ruta: list[str] | None = None
) -> dict:
    """Lista objetos de una coleccion del modelo o de otro objeto.
    Ejemplos: Packages, UseCaseDiagrams, Actors, UseCases,
    Associations, Dependencies, Symbols.
    Cada resultado incluye una ruta reutilizable en otras herramientas.
    Las colecciones disponibles dependen del tipo de objeto.
    """
    ruta = ruta or []
    if coleccion.startswith("_"):
        raise ValueError("Coleccion no permitida.")
    with conexion() as (_, modelo):
        padre = resolver(modelo, ruta)
        objetos = []
        for indice, obj in enumerate(getattr(padre, coleccion)):
            item = resumen(obj)
            identificador = dato(obj, "ObjectID")
            if identificador is None:
                identificador = "@" + str(indice)
            item["ruta"] = ruta + [coleccion + ":" + str(identificador)]
            objetos.append(item)
        return {"objetos": objetos}

@mcp.tool()
def leer_propiedades(ruta: list[str], propiedades: list[str]) -> dict:
    """Lee propiedades escalares concretas de un objeto o simbolo.
    Para relaciones, devuelve tambien los extremos Object1 y Object2
    cuando existen. No modifica el modelo.
    """
    with conexion() as (_, modelo):
        obj = resolver(modelo, ruta)
        resultado = resumen(obj)
        resultado["propiedades"] = {
            p: dato(obj, p) for p in propiedades if not p.startswith("_")
        }
        for extremo in ("Object", "Object1", "Object2"):
            try:
                vinculado = getattr(obj, extremo)
                if vinculado is not None:
                    resultado[extremo] = resumen(vinculado)
            except Exception:
                pass
        return resultado

@mcp.tool()
def editar_propiedad(ruta: list[str], propiedad: str, valor: str) -> dict:
    """Modifica Name, Code, Comment o Description de un objeto.
    Crea un respaldo del archivo guardado antes de la primera edicion.
    Los cambios quedan en memoria hasta guardar_modelo.
    """
    if propiedad not in {"Name", "Code", "Comment", "Description"}:
        raise ValueError("Propiedad no habilitada para edicion.")
    with conexion() as (_, modelo):
        obj = resolver(modelo, ruta)
        anterior = dato(obj, propiedad)
        respaldo = respaldar(modelo)
        setattr(obj, propiedad, valor)
        return {
            "objeto": resumen(obj),
            "anterior": anterior,
            "actual": dato(obj, propiedad),
            "respaldo": respaldo,
        }

@mcp.tool()
def crear_objeto(
    coleccion: str,
    nombre: str,
    codigo: str,
    ruta_padre: list[str] | None = None,
) -> dict:
    """Crea un actor o caso de uso en Actors o UseCases.
    El objeto aun no aparece en un diagrama: usar mostrar_en_diagrama.
    """
    if coleccion not in {"Actors", "UseCases"}:
        raise ValueError("Solo se permite crear Actors o UseCases.")
    ruta_padre = ruta_padre or []
    with conexion() as (_, modelo):
        padre = resolver(modelo, ruta_padre)
        respaldo = respaldar(modelo)
        obj = getattr(padre, coleccion).CreateNew()
        obj.Name = nombre
        obj.Code = codigo
        return {
            "objeto": resumen(obj),
            "ruta": ruta_padre + [coleccion + ":" + str(obj.ObjectID)],
            "respaldo": respaldo,
        }

@mcp.tool()
def mostrar_en_diagrama(
    ruta_diagrama: list[str], ruta_objeto: list[str]
) -> dict:
    """Agrega la representacion de un objeto existente a un diagrama."""
    with conexion() as (_, modelo):
        diagrama = resolver(modelo, ruta_diagrama)
        obj = resolver(modelo, ruta_objeto)
        respaldo = respaldar(modelo)
        simbolo = diagrama.AttachObject(obj)
        if simbolo is None:
            raise ValueError("PowerDesigner no devolvio un simbolo.")
        return {
            "simbolo": resumen(simbolo),
            "indicacion": "Vuelve a listar Symbols para obtener su ruta actual.",
            "respaldo": respaldo,
        }

@mcp.tool()
def guardar_modelo() -> dict:
    """Guarda las modificaciones del modelo activo en su archivo."""
    with conexion() as (_, modelo):
        respaldo = respaldar(modelo)
        modelo.Save()
        return {
            "archivo": dato(modelo, "FileName"),
            "respaldo": respaldo,
            "mensaje": "Se ejecuto Save; comprobar el resultado en PowerDesigner.",
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
