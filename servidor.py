import shutil
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
import pythoncom
import win32com.client
from mcp.server.fastmcp import FastMCP
from seguridad import verificar_modelo_autorizado
from geometria_validacion import coordenadas_coinciden

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
    verificar_modelo_autorizado(nombre)
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

# -------------------- Nuevas funciones de geometria --------------------


def _diagrama(modelo, ruta_diagrama):
    if not ruta_diagrama or not all(
        paso.startswith("ClassDiagrams:") or paso.startswith("Packages:")
        for paso in ruta_diagrama
    ):
        raise ValueError("Indica la ruta de un diagrama de clases existente.")
    d = resolver(modelo, ruta_diagrama)
    if str(d.ClassName) != "Class Diagram":
        raise ValueError("Solo se permite trabajar en diagramas de clases.")
    return d


def _id(obj):
    try:
        return str(obj.ObjectID)
    except Exception:
        return None


def _objeto_simbolo(simbolo):
    try:
        return simbolo.Object
    except Exception:
        return None


def _xy_posicion(simbolo):
    try:
        pos = simbolo.Position
        return {"x": int(pos.X), "y": int(pos.Y)}
    except Exception:
        return None


def _tamano(simbolo):
    try:
        return {"ancho": int(simbolo.Width), "alto": int(simbolo.Height)}
    except Exception:
        try:
            sz = simbolo.Size
            return {"ancho": int(sz.X), "alto": int(sz.Y)}
        except Exception:
            return None


def _puntos(simbolo):
    try:
        lista = simbolo.ListOfPoints
        return [
            {"x": int(lista.Item(i).X), "y": int(lista.Item(i).Y)}
            for i in range(int(lista.Count))
        ]
    except Exception:
        return None


def _mapa_simbolos(diagrama):
    """No usa Symbol.ObjectID: algunos simbolos de PowerDesigner no lo tienen."""
    mapa = {}
    extras = []
    for indice, simbolo in enumerate(diagrama.Symbols):
        obj = _objeto_simbolo(simbolo)
        oid = _id(obj) if obj is not None else None
        tipo = dato(obj, "ClassName") if obj is not None else None
        registro = {
            "indice": indice,
            "tipo": tipo or dato(simbolo, "ClassName"),
            "nombre": dato(obj, "Name") if obj is not None else None,
            "objeto_id": oid,
            "posicion": _xy_posicion(simbolo),
            "tamano": _tamano(simbolo),
            "puntos_flecha": _puntos(simbolo),
        }
        if obj is not None and tipo == "Dependency":
            for k in ("Object1", "Object2"):
                try:
                    ext = getattr(obj, k)
                    registro[k] = dato(ext, "Name")
                except Exception:
                    pass
        if oid:
            mapa.setdefault(oid, []).append((simbolo, registro))
        extras.append(registro)
    return mapa, extras


def _seleccionar_unico(mapa, oid, tipo):
    coincidencias = [
        par for par in mapa.get(oid, []) if par[1]["tipo"] == tipo
    ]
    if len(coincidencias) != 1:
        raise ValueError(
            f"Se esperaban 1 simbolo de tipo {tipo} con id {oid}, "
            f"se encontraron {len(coincidencias)}. Revisar inspeccionar_diagrama."
        )
    return coincidencias[0][0]


def _entero_acotado(valor, etiqueta):
    if type(valor) is not int or not -2_000_000 <= valor <= 2_000_000:
        raise ValueError(f"{etiqueta}: usar entero entre -2000000 y 2000000.")
    return valor


def _refrescar(diagrama):
    try:
        diagrama.RedrawAllViews()
    except Exception:
        pass


@mcp.tool()
def inspeccionar_diagrama(ruta_diagrama: list[str]) -> dict:
    """Lista la geometria real de paquetes, dependencias y notas del diagrama.
    No modifica nada. Proporciona objeto_id, posicion, tamano y puntos de flecha.
    """
    with conexion() as (_, modelo):
        diagrama = _diagrama(modelo, ruta_diagrama)
        _, elementos = _mapa_simbolos(diagrama)
        return {
            "modelo": dato(modelo, "Name"),
            "diagrama": dato(diagrama, "Name"),
            "unidades": "coordenadas internas de PowerDesigner, NO pixeles",
            "total": len(elementos),
            "simbolos": elementos,
        }


@mcp.tool()
def mover_paquetes(
    ruta_diagrama: list[str],
    movimientos: list[dict],
    confirmar: bool = False,
) -> dict:
    """Mueve SOLO simbolos de paquetes, sin cambiar relaciones ni clases.
    movimientos: [{"objeto_id":"{GUID}", "x":10000, "y":20000}, ...].
    Por defecto solo PREVISUALIZA. confirmar=True aplica cambios EN MEMORIA.
    Crea respaldo antes de editar. Luego llamar guardar_modelo.
    """
    if not movimientos or len(movimientos) > 30:
        raise ValueError("Indicar entre 1 y 30 movimientos.")
    with conexion() as (_, modelo):
        diagrama = _diagrama(modelo, ruta_diagrama)
        mapa, _ = _mapa_simbolos(diagrama)
        usados = set()
        plan = []
        for movimiento in movimientos:
            oid = movimiento.get("objeto_id")
            if not isinstance(oid, str) or oid in usados:
                raise ValueError("objeto_id ausente o repetido.")
            usados.add(oid)
            x = _entero_acotado(movimiento.get("x"), "x")
            y = _entero_acotado(movimiento.get("y"), "y")
            simbolo = _seleccionar_unico(mapa, oid, "Package")
            anterior = _xy_posicion(simbolo)
            if anterior is None:
                raise ValueError(f"No pude leer Position de {oid}.")
            plan.append({
                "objeto_id": oid,
                "nombre": dato(_objeto_simbolo(simbolo), "Name"),
                "antes": anterior,
                "despues": {"x": x, "y": y},
                "_simbolo": simbolo,
            })
        visible = [
            {k: v for k, v in p.items() if not k.startswith("_")}
            for p in plan
        ]
        if not confirmar:
            return {"aplicado": False, "previsualizacion": visible}
        respaldo = respaldar(modelo)
        procesados = []
        try:
            for p in plan:
                simbolo = p["_simbolo"]
                nueva = simbolo.Position
                nueva.X = p["despues"]["x"]
                nueva.Y = p["despues"]["y"]
                simbolo.Position = nueva
                leida = _xy_posicion(simbolo)
                if not coordenadas_coinciden(leida, p["despues"]):
                    raise RuntimeError(f"Posicion no confirmada para {p['nombre']}: {leida}")
                # Report the actual COM position; rounding of 1 internal unit is expected.
                p["real"] = leida
                procesados.append(p)
            _refrescar(diagrama)
        except Exception as exc:
            for p in reversed(plan):
                try:
                    s = p["_simbolo"]
                    pos = s.Position
                    pos.X, pos.Y = p["antes"]["x"], p["antes"]["y"]
                    s.Position = pos
                except Exception:
                    pass
            _refrescar(diagrama)
            raise RuntimeError(
                "No se pudo completar el movimiento. Se intento restaurar "
                "la geometria previa en memoria; verificar el respaldo. "
                + str(exc)
            ) from exc
        return {
            "aplicado": True,
            "movimientos": [
                {k: v for k, v in p.items() if not k.startswith("_")}
                for p in plan
            ],
            "respaldo": respaldo,
            "nota": "Cambios en memoria. Ejecutar guardar_modelo tras revisar.",
        }


def _sustituir_puntos(simbolo, puntos):
    """Recrea trazado con los metodos documentados de PtList.
    Remove elimina el ultimo punto; AddPoint agrega uno al final.
    """
    lista = simbolo.ListOfPoints
    while int(lista.Count) > 1:
        lista.Remove()
    for p in puntos[1:]:
        lista.AddPoint(p["x"], p["y"])


@mcp.tool()
def enderezar_flechas(
    ruta_diagrama: list[str],
    dependencias_ids: list[str],
    confirmar: bool = False,
) -> dict:
    """Quita los puntos intermedios de dependencias concretas.
    Mantiene el punto inicial y el final. NO invierte la flecha ni modifica
    Object1/Object2. Primero PREVISUALIZAR; confirmar=True edita EN MEMORIA.
    Utilizar despues de mover paquetes; luego guardar_modelo.
    """
    if not dependencias_ids or len(dependencias_ids) > 30:
        raise ValueError("Indicar de 1 a 30 IDs de dependencias.")
    if len(set(dependencias_ids)) != len(dependencias_ids):
        raise ValueError("IDs de dependencias repetidos.")
    with conexion() as (_, modelo):
        diagrama = _diagrama(modelo, ruta_diagrama)
        mapa, _ = _mapa_simbolos(diagrama)
        plan = []
        for oid in dependencias_ids:
            simbolo = _seleccionar_unico(mapa, oid, "Dependency")
            antes = _puntos(simbolo)
            if antes is None or len(antes) < 2:
                raise ValueError(f"No se pudo leer ListOfPoints: {oid}")
            plan.append({
                "objeto_id": oid, "antes": antes,
                "despues": [antes[0], antes[-1]], "_simbolo": simbolo,
            })
        visible = [
            {k: v for k, v in p.items() if not k.startswith("_")}
            for p in plan
        ]
        if not confirmar:
            return {"aplicado": False, "previsualizacion": visible}
        respaldo = respaldar(modelo)
        try:
            for p in plan:
                _sustituir_puntos(p["_simbolo"], p["despues"])
            _refrescar(diagrama)
            for p in plan:
                leida = _puntos(p["_simbolo"])
                if leida != p["despues"]:
                    raise RuntimeError(
                        f"Trayectoria no confirmada para {p['objeto_id']}: {leida}"
                    )
        except Exception as exc:
            for p in plan:
                try:
                    _sustituir_puntos(p["_simbolo"], p["antes"])
                except Exception:
                    pass
            _refrescar(diagrama)
            raise RuntimeError(
                "Falló la edicion de rutas; se intento restaurar los puntos "
                "anteriores. Verificar el respaldo. " + str(exc)
            ) from exc
        return {
            "aplicado": True,
            "dependencias": visible,
            "respaldo": respaldo,
            "nota": "Revisar visualmente las flechas y guardar_modelo.",
        }


@mcp.tool()
def insertar_codo_flecha(
    ruta_diagrama: list[str],
    dependencia_id: str,
    x: int,
    y: int,
    confirmar: bool = False,
) -> dict:
    """Inserta UN codo intermedio en una dependencia de dos puntos.
    No cambia los extremos UML. Usa PtList.InsertPoint(1,x,y).
    PREVISUALIZA por defecto. Antes, usar enderezar_flechas si hay mas de
    dos puntos. Guardar despues de comprobar el resultado.
    """
    x = _entero_acotado(x, "x")
    y = _entero_acotado(y, "y")
    with conexion() as (_, modelo):
        diagrama = _diagrama(modelo, ruta_diagrama)
        mapa, _ = _mapa_simbolos(diagrama)
        simbolo = _seleccionar_unico(mapa, dependencia_id, "Dependency")
        antes = _puntos(simbolo)
        if antes is None or len(antes) != 2:
            raise ValueError(
                "Esta herramienta requiere una flecha de exactamente "
                "dos puntos. Inspeccionar y enderezar antes."
            )
        despues = [antes[0], {"x": x, "y": y}, antes[1]]
        if not confirmar:
            return {"aplicado": False, "antes": antes, "despues": despues}
        respaldo = respaldar(modelo)
        try:
            simbolo.ListOfPoints.InsertPoint(1, x, y)
            _refrescar(diagrama)
            leida = _puntos(simbolo)
            if leida != despues:
                raise RuntimeError(
                    f"Trayectoria no confirmada para {dependencia_id}: {leida}"
                )
        except Exception as exc:
            try:
                _sustituir_puntos(simbolo, antes)
            except Exception:
                pass
            raise RuntimeError(
                "No se pudo insertar codo. Se intento restaurar la ruta. "
                + str(exc)
            ) from exc
        return {
            "aplicado": True, "antes": antes,
            "despues": leida, "respaldo": respaldo,
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
