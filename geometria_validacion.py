"""Coordinate verification helpers for PowerDesigner COM geometry.

PowerDesigner sometimes converts assigned integer coordinates back with
a one-unit rounding difference. This module does not access COM.
"""

def coordenadas_coinciden(observada: dict, solicitada: dict, tolerancia: int = 1) -> bool:
    """Accept at most one internal-unit rounding difference per axis.

    Does not allow missing keys or non-integer coordinate values.
    """
    if type(tolerancia) is not int or tolerancia < 0:
        return False
    for eje in ("x", "y"):
        a = observada.get(eje) if isinstance(observada, dict) else None
        b = solicitada.get(eje) if isinstance(solicitada, dict) else None
        if type(a) is not int or type(b) is not int or abs(a - b) > tolerancia:
            return False
    return True
