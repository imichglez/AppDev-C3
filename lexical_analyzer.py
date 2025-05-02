#!/usr/bin/env python3
import sys
import os

# — Estados de aceptación y error —
ACCEPT_STATE = 2
ERROR_STATE  = 3

# — Categorías para la tabla —
LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET, CHAR, DIGIT, DEL, OTHER = range(10)

def categorize(ch: str):
    if ch == '(':        return LPAREN
    elif ch == ')':      return RPAREN
    elif ch == '{':      return LBRACE
    elif ch == '}':      return RBRACE
    elif ch == '[':      return LBRACKET
    elif ch == ']':      return RBRACKET
    elif ch.isalpha() or ch == '_':
        return CHAR
    elif ch.isdigit():
        return DIGIT
    elif ch.isspace():
        return DEL
    else:
        return OTHER

# — Tabla de transiciones según tu diagrama —
T = {
    0: {LPAREN:2, RPAREN:2, LBRACE:2, RBRACE:2, LBRACKET:2, RBRACKET:2, CHAR:1, DIGIT:3, DEL:0, OTHER:3},
    1: {LPAREN:2, RPAREN:2, LBRACE:2, RBRACE:2, LBRACKET:2, RBRACKET:2, CHAR:1, DIGIT:1, DEL:2, OTHER:3},
}

# — Códigos de token para símbolos y palabras reservadas —
TOKEN_CODES = {'(':1, ')':2, '{':3, '}':4, '[':5, ']':6}
RESERVED_KEYWORDS = {'class':7, 'this':8, 'new':9}
ID_CODE = 20

# — Función principal de escaneo —
def scan(text):
    tokens = []
    symtab = {}
    error = False
    i, n = 0, len(text)

    # Error si inicia con delimitador
    if i < n and categorize(text[i]) == DEL:
        return [], {}, True

    # Procesar hasta el final o error
    while i < n and not error:
        # Detectar delimitadores consecutivos
        if categorize(text[i]) == DEL:
            # primer delimitador ya es error porque tokens no iniciado
            error = True
            break

        state = 0
        lexeme = ''
        j = i
        delim_count = 0

        # DFA: recorrer desde j hasta aceptación/error
        while j < n:
            cat = categorize(text[j])
            # si encontramos delimitador, lo contaremos y detendremos
            if cat == DEL:
                break
            next_state = T[state].get(cat, ERROR_STATE)
            if next_state == ERROR_STATE:
                error = True
                break
            if next_state == ACCEPT_STATE:
                break
            # Estado 1: acumula letras/dígitos
            state = next_state
            if state == 1:
                lexeme += text[j]
            j += 1

        if error:
            break

        # Grabación de token según estado y lexema
        if state == 1 and lexeme:
            key = lexeme.lower()
            if key in RESERVED_KEYWORDS:
                tokens.append(RESERVED_KEYWORDS[key])
            else:
                idx = symtab.setdefault(key, len(symtab) + 1)
                tokens.append((ID_CODE, idx))
            i += len(lexeme)
        else:
            # es un símbolo único en text[i]
            ch = text[i]
            if ch in TOKEN_CODES:
                tokens.append(TOKEN_CODES[ch])
                i += 1
            else:
                error = True
                break

        # Saltar delimitadores, contando cuantos hay seguidos
        delim_count = 0
        while i < n and categorize(text[i]) == DEL:
            delim_count += 1
            i += 1
        if delim_count > 1:
            error = True
            break

    return tokens, symtab, error

# — Programa principal —
def main():
    if len(sys.argv) != 2:
        print("Uso: python lexical_analyzer.py <archivo_entrada>")
        sys.exit(1)
    infile = sys.argv[1]
    if not os.path.isfile(infile):
        print(f"Error: no existe el archivo '{infile}'")
        sys.exit(1)

    text = open(infile, encoding='utf-8').read()
    tokens, symtab, error = scan(text)

    with open('output.txt', 'w', encoding='utf-8') as f:
        if error:
            f.write("ERROR\n")
        else:
            for tok in tokens:
                if isinstance(tok, tuple):
                    f.write(f"<{tok[0]},{tok[1]}>\n")
                else:
                    f.write(f"<{tok}>\n")

if __name__ == '__main__':
    main()
