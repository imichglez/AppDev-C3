import io
import unittest
from contextlib import redirect_stdout

from lexical_analyzer import Scanner   

def capture(text: str) -> str:
    """ Run Scanner(text) and return everything it prints (including trailing newlines) as a single string. """
    buf = io.StringIO()
    with redirect_stdout(buf):
        Scanner(text).scan()
    return buf.getvalue()

class ScannerTests(unittest.TestCase):

    # 1) Invalid first character (symbol or digit) → "ERROR\n"
    def test_invalid_start(self):
        for ch in "$@#%&!" + "0123456789":
            with self.subTest(char=ch):
                self.assertEqual(capture(ch + "x"), "ERROR\n")

    # 2) Empty input → no output at all
    def test_empty_input(self):
        self.assertEqual(capture(""), "")

    # 3–7) Pre‑designed inputs with known expected output
    def test_expected_outputs(self):
        cases = {
            # 3) Two different identifiers separated by braces
            "foo{bar}": "<20, 1>\n<3>\n<20, 2>\n<4>\n",

            # 4) Duplicate identifier should reuse the same symbol‑table index
            "foo{foo}": "<20, 1>\n<3>\n<20, 1>\n<4>\n",

            # 5) Identifiers separated only by mixed whitespace
            "foo  \tbar\nbaz": "<20, 1>\n<20, 2>\n<20, 3>\n",

            # 6) Consecutive delimiters without spacing
            "(){}": "<1>\n<2>\n<3>\n<4>\n",

            # 7) Reserved‑word prefix inside an identifier (should NOT be a keyword)
            "class1 new_var": "<20, 1>\n<20, 2>\n",
        }
        for src, expected in cases.items():
            with self.subTest(source=src):
                self.assertEqual(capture(src), expected)

if __name__ == "__main__":
    unittest.main()