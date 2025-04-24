#!/usr/bin/env python3
"""
Analizador Léxico Simplificado para C++
Maneja directivas de preprocesador y strings pero sin tabla de strings
"""

class Scanner:
    # Estados
    INITIAL = 0
    ID = 1
    NUM = 2
    OP = 3
    DELIM = 4
    PREPROC = 5
    STRING = 6
    COMMENT_LINE = 7
    COMMENT_MULTI = 8
    ERROR = 99
    
    # Tipos de caracteres
    LETTER = 0
    DIGIT = 1
    WHITE = 2
    OP_CHAR = 3
    DELIM_CHAR = 4
    HASH = 5
    QUOTE = 6
    SLASH = 7
    OTHER = 8
    
    def __init__(self):
        # Definir conjuntos de caracteres
        self.letters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
        self.digits = set('0123456789')
        self.white = set(' \t\n\r')
        self.operators = set('+-*/=<>!&|^%~')
        self.delimiters = set('(){}[],;:.')
        
        # Matriz de transición [estado][tipo_caracter]
        self.T = [
            # LETTER  DIGIT   WHITE   OP      DELIM   HASH    QUOTE   SLASH   OTHER
            [self.ID, self.NUM, self.INITIAL, self.OP, self.DELIM, self.PREPROC, self.STRING, self.OP, self.ERROR],  # INITIAL
            [self.ID, self.ID, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL],  # ID
            [self.INITIAL, self.NUM, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL],  # NUM
            [self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL],  # OP
            [self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL, self.INITIAL],  # DELIM
            [self.PREPROC, self.PREPROC, self.PREPROC, self.PREPROC, self.PREPROC, self.PREPROC, self.PREPROC, self.PREPROC, self.PREPROC],  # PREPROC
            [self.STRING, self.STRING, self.STRING, self.STRING, self.STRING, self.STRING, self.INITIAL, self.STRING, self.STRING],  # STRING
            [self.COMMENT_LINE, self.COMMENT_LINE, self.INITIAL, self.COMMENT_LINE, self.COMMENT_LINE, self.COMMENT_LINE, self.COMMENT_LINE, self.COMMENT_LINE, self.COMMENT_LINE],  # COMMENT_LINE
            [self.COMMENT_MULTI, self.COMMENT_MULTI, self.COMMENT_MULTI, self.COMMENT_MULTI, self.COMMENT_MULTI, self.COMMENT_MULTI, self.COMMENT_MULTI, self.COMMENT_MULTI, self.COMMENT_MULTI]   # COMMENT_MULTI
        ]
        
        # Palabras clave
        self.keywords = {
            'if', 'else', 'while', 'for', 'int', 'char', 'float', 'void',
            'return', 'break', 'continue', 'class', 'struct', 'const',
            'bool', 'true', 'false', 'namespace', 'using', 'public', 'private'
        }
        
        # Tablas y tokens
        self.id_table = {}
        self.num_table = {}
        self.tokens = []
    
    def get_char_type(self, ch):
        """Determina el tipo de un carácter"""
        if ch in self.letters:
            return self.LETTER
        elif ch in self.digits:
            return self.DIGIT
        elif ch in self.white:
            return self.WHITE
        elif ch in self.operators:
            if ch == '/':
                return self.SLASH
            return self.OP_CHAR
        elif ch in self.delimiters:
            return self.DELIM_CHAR
        elif ch == '#':
            return self.HASH
        elif ch == '"':
            return self.QUOTE
        else:
            return self.OTHER
    
    def scan(self, filename):
        """Escanea un archivo y genera tokens"""
        try:
            with open(filename, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return []
        
        # Reiniciar tablas
        self.id_table = {}
        self.num_table = {}
        self.tokens = []
        
        # Índices para las tablas
        id_count = 1
        num_count = 1
        
        i = 0
        while i < len(content):
            # Ignorar espacios en blanco
            while i < len(content) and content[i] in self.white:
                i += 1
            
            if i >= len(content):
                break
            
            # Iniciar estado
            state = self.INITIAL
            token = ""
            
            # Manejar comentarios de línea
            if i+1 < len(content) and content[i:i+2] == "//":
                while i < len(content) and content[i] != '\n':
                    i += 1
                continue
            
            # Manejar comentarios multilínea
            if i+1 < len(content) and content[i:i+2] == "/*":
                i += 2
                while i+1 < len(content) and content[i:i+2] != "*/":
                    i += 1
                i += 2
                continue
            
            # Leer un token
            start_pos = i
            while i < len(content):
                ch = content[i]
                char_type = self.get_char_type(ch)
                
                # Casos especiales
                if state == self.INITIAL and char_type == self.HASH:
                    # Procesar directiva de preprocesador (#include, etc.)
                    while i < len(content) and content[i] != '\n':
                        token += content[i]
                        i += 1
                    self.tokens.append((token, 'PREPROC'))
                    break
                
                if state == self.INITIAL and char_type == self.QUOTE:
                    # Procesar string (e.g. "hello")
                    token += ch
                    i += 1
                    while i < len(content) and content[i] != '"':
                        token += content[i]
                        i += 1
                    if i < len(content):
                        token += content[i]  # Incluir comilla final
                        i += 1
                    
                    # Incluir directamente el contenido de la cadena en el token
                    self.tokens.append((token, 'STRING'))
                    break
                
                # Siguiente estado
                next_state = self.T[state][char_type]
                
                # Si volvemos al estado inicial, terminamos el token actual
                if next_state == self.INITIAL and state != self.INITIAL:
                    break
                
                # Si es un error, terminamos el token actual
                if next_state == self.ERROR:
                    if state == self.INITIAL:
                        print(f"Caracter ignorado: '{ch}'")
                        i += 1
                    break
                
                # Actualizar estado
                state = next_state
                
                # Si no es espacio en blanco, agregar al token
                if char_type != self.WHITE:
                    token += ch
                
                # Avanzar
                i += 1
                
                # Si llegamos al final del contenido
                if i >= len(content):
                    break
            
            # Registrar token según el estado
            if token:
                if state == self.ID:
                    if token in self.keywords:
                        self.tokens.append((token.upper(), token))
                    else:
                        if token not in self.id_table:
                            self.id_table[token] = id_count
                            id_count += 1
                        self.tokens.append(('ID', self.id_table[token]))
                
                elif state == self.NUM:
                    if token not in self.num_table:
                        self.num_table[token] = num_count
                        num_count += 1
                    self.tokens.append(('NUM', self.num_table[token]))
                
                elif state == self.OP:
                    self.tokens.append((token, 'OP'))
                
                elif state == self.DELIM:
                    self.tokens.append((token, 'DELIM'))
        
        return self.tokens
    
    def print_results(self):
        """Imprime los resultados del análisis"""
        print("Tokens generados:")
        for token in self.tokens:
            print(f"<{token[0]}, {token[1]}>")
        
        print("\nTabla de Identificadores:")
        for name, idx in sorted(self.id_table.items(), key=lambda x: x[1]):
            print(f"{idx}: {name}")
        
        print("\nTabla de Constantes Numéricas:")
        for val, idx in sorted(self.num_table.items(), key=lambda x: x[1]):
            print(f"{idx}: {val}")


def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python simplified_analyzer.py <archivo.cpp>")
        sys.exit(1)
    
    scanner = Scanner()
    scanner.scan(sys.argv[1])
    scanner.print_results()


if __name__ == "__main__":
    main()