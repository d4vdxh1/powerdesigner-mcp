"""Pruebas sin PowerDesigner ni Windows COM."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from seguridad import verificar_modelo_autorizado


class EscrituraPorModeloTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        carpeta = Path(self.tmp.name)
        self.modelo = carpeta / "principal.oom"
        self.otro = carpeta / "otro.oom"
        self.modelo.write_bytes(b"modelo original")
        self.otro.write_bytes(b"otro modelo")

    def test_sin_configuracion_se_bloquea(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(PermissionError):
                verificar_modelo_autorizado(str(self.modelo))

    def test_modelo_autorizado_funciona(self):
        with patch.dict(os.environ, {"POWERDESIGNER_MCP_WRITE_MODEL": str(self.modelo)}):
            self.assertEqual(
                verificar_modelo_autorizado(str(self.modelo)),
                self.modelo.resolve(),
            )

    def test_modelo_diferente_se_bloquea(self):
        with patch.dict(os.environ, {"POWERDESIGNER_MCP_WRITE_MODEL": str(self.modelo)}):
            with self.assertRaises(PermissionError):
                verificar_modelo_autorizado(str(self.otro))

    def test_ruta_relativa_se_bloquea(self):
        with patch.dict(os.environ, {"POWERDESIGNER_MCP_WRITE_MODEL": "principal.oom"}):
            with self.assertRaises(PermissionError):
                verificar_modelo_autorizado(str(self.modelo))

    def test_autorizacion_inexistente_se_bloquea(self):
        with patch.dict(os.environ, {"POWERDESIGNER_MCP_WRITE_MODEL": str(self.modelo) + ".notfound"}):
            with self.assertRaises(PermissionError):
                verificar_modelo_autorizado(str(self.modelo))


if __name__ == "__main__":
    unittest.main()
