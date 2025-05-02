#!/usr/bin/env python3
import sys
import os

# - Estados -
START_STATE = 0
ID_STATE = 1
ACCEPT_STATE = 2
ERROR_STATE = 3

# - Categorías -
LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET, CHAR, DIGIT, DEL, OTHER = range(10)

# - Tabla de transiciones corregida -
T = {
    START_STATE: {
        CHAR: ID_STATE,
        LPAREN: ACCEPT_STATE, RPAREN: ACCEPT_STATE,
        LBRACE: ACCEPT_STATE, RBRACE: ACCEPT_STATE,
        LBRACKET: ACCEPT_STATE, RBRACKET: ACCEPT_STATE,
        DEL: ERROR_STATE,
        OTHER: ERROR_STATE
    },
    ID_STATE: {
        CHAR: ID_STATE,
        DIGIT: ID_STATE,
        LPAREN: ACCEPT_STATE, RPAREN: ACCEPT_STATE,
        LBRACE: ACCEPT_STATE, RBRACE: ACCEPT_STATE,
        LBRACKET: ACCEPT_STATE, RBRACKET: ACCEPT_STATE,
        DEL: ACCEPT_STATE,
        OTHER: ACCEPT_STATE  # Permite fin de input como aceptación
    }
}

# - Códigos de token -
TOKEN_CODES = {'(':1, ')':2, '{':3, '}':4, '[':5, ']':6}
RESERVED_KEYWORDS = {'class':7, 'this':8, 'new':9}
ID_CODE = 20

class Scanner:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self.symtab = {}
        self.error = False

    def categorize(self, ch):
        if ch == '(': return LPAREN
        elif ch == ')': return RPAREN
        elif ch == '{': return LBRACE
        elif ch == '}': return RBRACE
        elif ch == '[': return LBRACKET
        elif ch == ']': return RBRACKET
        elif ch.isalpha() or ch == '_': return CHAR
        elif ch.isdigit(): return DIGIT
        elif ch.isspace(): return DEL
        else: return OTHER

    def scan(self):
        n = len(self.text)
     
        if n > 0 and self.text[0].isspace():
            self.error = True
            return self.tokens, self.symtab, self.error
        
        while self.pos < n and not self.error:
            # Verificar si hay 2 o más espacios consecutivos
            space_count = 0
            pos_temp = self.pos
            
            while pos_temp < n and self.text[pos_temp] == ' ':
                space_count += 1
                pos_temp += 1
                # Error si hay 2 o más espacios consecutivos
                if space_count >= 2:
                    self.error = True
                    break
            
            if self.error:
                break
                
            # Saltar espacios (solo si es uno) y otros delimitadores
            while self.pos < n and self.categorize(self.text[self.pos]) == DEL:
                self.pos += 1
            
            if self.pos >= n: 
                break

            start_pos = self.pos
            state = START_STATE
            lexeme = ''

            # Procesar token
            while self.pos < n:
                ch = self.text[self.pos]
                cat = self.categorize(ch)
                
                # Transición de estados
                next_state = T.get(state, {}).get(cat, ERROR_STATE)
                
                # Si estamos en ID_STATE y encontramos un carácter que nos llevaría a ACCEPT_STATE
                # (como un paréntesis), debemos detener el procesamiento del identificador actual
                if state == ID_STATE and next_state == ACCEPT_STATE:
                    break
                
                if next_state == ERROR_STATE:
                    break
                
                # Acumular lexema
                if next_state == ID_STATE:
                    lexeme += ch
                
                state = next_state
                self.pos += 1

                # Detener si es estado de aceptación
                if state == ACCEPT_STATE:
                    break

            # Manejar fin de input como aceptación para identificadores
            if state == ID_STATE and self.pos >= n:
                state = ACCEPT_STATE
                lexeme = self.text[start_pos:self.pos]
            # Si acabamos de salir porque encontramos un carácter que nos llevaría a ACCEPT_STATE
            # pero no llegamos a procesar ese carácter (como un paréntesis después de un ID)
            elif state == ID_STATE and T.get(state, {}).get(cat, ERROR_STATE) == ACCEPT_STATE:
                state = ACCEPT_STATE
                lexeme = self.text[start_pos:self.pos]
                # No avanzamos el puntero aquí para que el próximo ciclo procese el símbolo

            # Registrar token o error
            if state == ACCEPT_STATE:
                if lexeme:
                    key = lexeme.lower()
                    if key in RESERVED_KEYWORDS:
                        self.tokens.append(RESERVED_KEYWORDS[key])
                    else:
                        idx = self.symtab.setdefault(lexeme, len(self.symtab)+1)
                        self.tokens.append((ID_CODE, idx))
                else:
                    symbol = self.text[start_pos]
                    if symbol in TOKEN_CODES:
                        self.tokens.append(TOKEN_CODES[symbol])
                        # Si procesamos un símbolo directamente, aseguramos que el puntero avance
                        if self.pos == start_pos:
                            self.pos += 1
            else:
                self.error = True
                break

        return self.tokens, self.symtab, self.error

# - Programa principal -
def main():
    if len(sys.argv) != 2:
        print("Uso: python lexical_analyzer.py <archivo_entrada>")
        sys.exit(1)
    
    infile = sys.argv[1]
    if not os.path.isfile(infile):
        print(f"Error: no existe el archivo '{infile}'")
        sys.exit(1)

    text = open(infile, encoding='utf-8').read()
    scanner = Scanner(text)
    tokens, symtab, error = scanner.scan()

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
