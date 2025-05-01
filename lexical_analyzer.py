# lexical_analyzer.py

import sys

# ————————————————————————————————
# 1. Token IDs y palabras reservadas
# ————————————————————————————————
CLASS = 1
LPAREN = 2
RPAREN = 3
LBRACE = 4
RBRACE = 5
THIS = 6
NEW = 7
IDENTIFIER = 20

# Palabras reservadas
RESERVED = {"class": CLASS, "this": THIS, "new": NEW}

# ————————————————————————————————
# 2. Categorías de entrada para el DFA
# ————————————————————————————————
CAT_LETTER, CAT_WS, CAT_LP, CAT_RP, CAT_LB, CAT_RB, CAT_OTHER = range(7)

# ————————————————————————————————
# 3. Tabla de transiciones como diccionario
#    (estado, categoría) → ('state', nuevo_estado)
#                      o ('accept', token_id)
#                      o ('error', None)
# ————————————————————————————————
T = {
    (0, CAT_LETTER): ('state', 1),
    (0, CAT_WS):     ('state', 0),
    (0, CAT_LP):     ('accept', LPAREN),
    (0, CAT_RP):     ('accept', RPAREN),
    (0, CAT_LB):     ('accept', LBRACE),
    (0, CAT_RB):     ('accept', RBRACE),

    (1, CAT_LETTER): ('state', 1),
    (1, CAT_WS):     ('accept', IDENTIFIER),
    (1, CAT_LP):     ('accept', IDENTIFIER),
    (1, CAT_RP):     ('accept', IDENTIFIER),
    (1, CAT_LB):     ('accept', IDENTIFIER),
    (1, CAT_RB):     ('accept', IDENTIFIER),
}

# ————————————————————————————————
# 4. Funciones que replican el pseudocódigo
# ————————————————————————————————
def next_input_character(la):
    """next_input_character(): devuelve siguiente carácter o None."""
    if la.pos < len(la.text):
        ch = la.text[la.pos]
        la.pos += 1
        return ch
    return None

def unget_char(la):
    """ungetchar(): retrocede un carácter."""
    if la.pos > 0:
        la.pos -= 1

def categorize(ch):
    """column(ch): mapea ch a una categoría."""
    if   ch is None:      return CAT_OTHER
    elif ch.isalpha():    return CAT_LETTER
    elif ch.isspace():    return CAT_WS
    elif ch == '(' :      return CAT_LP
    elif ch == ')' :      return CAT_RP
    elif ch == '{' :      return CAT_LB
    elif ch == '}' :      return CAT_RB
    else:                 return CAT_OTHER

def record_token(la, token_id, lexeme, category):
    """record_Token(): construye y almacena el token en la lista."""
    if token_id == IDENTIFIER:
        text = lexeme or la.last_char
        lw = text.lower()
        if lw in RESERVED:
            la.tokens.append((RESERVED[lw],))
        else:
            idx = la.symbol_table.setdefault(text, len(la.symbol_table) + 1)
            la.tokens.append((IDENTIFIER, idx))
        # si aceptamos IDENTIFIER al ver un símbolo, retrocede
        if category in (CAT_LP, CAT_RP, CAT_LB, CAT_RB):
            unget_char(la)
    else:
        la.tokens.append((token_id,))

def error_message(la, ch):
    """error_message(): maneja errores (aquí simplemente ignora)."""
    # Opcional: print(f"Error: símbolo no reconocido '{ch}'")

# ————————————————————————————————
# 5. Scanner table-driven
# ————————————————————————————————
class LexicalAnalyzer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.symbol_table = {}
        self.last_char = None

    def scan(self):
        ch = next_input_character(self)
        while ch is not None:                 # while (!EOF)
            state, lexeme = 0, ""
            self.last_char = ch
            while True:                       # while (!Accept && !Error)
                col = categorize(ch)
                action, val = T.get((state, col), ('error', None))
                if action == 'error':
                    error_message(self, ch)
                    break
                if action == 'accept':
                    record_token(self, val, lexeme, col)
                    break
                # action == 'state'
                if state == 1 or val == 1:
                    lexeme += ch
                state = val
                ch = next_input_character(self)
                self.last_char = ch
                if ch is None and state == 1:  # EOF dentro de identificador
                    record_token(self, IDENTIFIER, lexeme, col)
                    break
            ch = next_input_character(self)
            self.last_char = ch
        return self.tokens

# ————————————————————————————————
# 6. Main: entrada, escaneo y salida
# ————————————————————————————————
def main():
    if len(sys.argv) < 2:
        print("Uso: python lexical_analyzer.py archivo_fuente.txt")
        return
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        text = f.read()

    tokens = LexicalAnalyzer(text).scan()

    # escribe cada token en output.txt
    with open("output.txt", "w", encoding="utf-8") as outf:
        for tid, *attr in tokens:
            if tid == IDENTIFIER:
                outf.write(f"<{IDENTIFIER},{attr[0]}>\n")
            else:
                outf.write(f"<{tid}>\n")

if __name__ == "__main__":
    main()
