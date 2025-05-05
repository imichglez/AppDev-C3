import io
import unittest
from contextlib import redirect_stdout

from lexical_analyzer import Scanner   


def run(text: str) -> str:
    """
    Execute the Scanner on `text`, then print the symbol table,
    and capture the whole stdout as a single string.
    """
    buf = io.StringIO()
    with redirect_stdout(buf):
        s = Scanner(text)
        s.scan()
        s.print_symbol_table()          # new ‑‑> include symbol‑table output
    return buf.getvalue()

class ScannerTests(unittest.TestCase):

    # 1) Invalid first character (symbol or digit) → "ERROR\nSymbol Table:\n"
    def test_invalid_start(self):
        expected = "ERROR\nSymbol Table:\n"
        for ch in "$@#%&!" + "0123456789":
            with self.subTest(char=ch):
                self.assertEqual(run(ch + "x"), expected)

    # 2) Empty input → only the symbol‑table header
    def test_empty_input(self):
        self.assertEqual(run(""), "Symbol Table:\n")

    # 3‑7) Pre‑designed inputs with known expected output
    def test_expected_outputs(self):
        cases = {
            # 3) Two different identifiers separated by braces
            "foo{bar}":
                "<20, 1>\n<3>\n<20, 2>\n<4>\n"
                "Symbol Table:\nfoo: 1\nbar: 2\n",

            # 4) Duplicate identifier → same symbol‑table index reused
            "foo{foo}":
                "<20, 1>\n<3>\n<20, 1>\n<4>\n"
                "Symbol Table:\nfoo: 1\n",

            # 5) Identifiers separated only by mixed whitespace
            "foo  \tbar\nbaz":
                "<20, 1>\n<20, 2>\n<20, 3>\n"
                "Symbol Table:\nfoo: 1\nbar: 2\nbaz: 3\n",

            # 6) Consecutive delimiters without spacing
            "(){}":
                "<1>\n<2>\n<3>\n<4>\n"
                "Symbol Table:\n",

            # 7) Reserved‑word prefix inside an identifier
            "class1 new_var":
                "<20, 1>\n<20, 2>\n"
                "Symbol Table:\nclass1: 1\nnew_var: 2\n",
        }

        for src, expected in cases.items():
            with self.subTest(source=src):
                self.assertEqual(run(src), expected)

if __name__ == "__main__":
    unittest.main()