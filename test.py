import io, unittest
from contextlib import redirect_stdout
from lexical_analyzer import Scanner   


def run(text: str) -> str:
    """Ejecuta Scanner(text) y devuelve todo lo impreso (incluye saltos de línea)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        Scanner(text).scan()
    return buf.getvalue()


class ScannerTests(unittest.TestCase):
    # 1) símbolo inválido o dígito al inicio → "ERROR\n"
    def test_invalid_start(self):
        for ch in "$@#%&!" + "0123456789":
            with self.subTest(ch=ch):
                self.assertEqual(run(ch + "x"), "ERROR\n")

    # 2) entrada vacía → sin salida
    def test_empty(self):
        self.assertEqual(run(""), "")

    # 3‑7) casos con salida conocida
    def test_expected_outputs(self):
        casos = {
            # 3) identificadores distintos con llaves
            "foo{bar}":        "<20, 1>\n<3>\n<20, 2>\n<4>\n",

            # 4) identificador duplicado
            "foo{foo}":        "<20, 1>\n<3>\n<20, 1>\n<4>\n",

            # 5) espacios, tab y salto de línea mezclados
            "foo  \tbar\nbaz": "<20, 1>\n<20, 2>\n<20, 3>\n",

            # 6) delimitadores consecutivos
            "(){}":            "<1>\n<2>\n<3>\n<4>\n",

            # 7) palabra reservada como prefijo (debe ser identificador)
            "class1 new_var":  "<20, 1>\n<20, 2>\n",
        }
        for entrada, esperado in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(run(entrada), esperado)


if __name__ == "__main__":
    unittest.main()
