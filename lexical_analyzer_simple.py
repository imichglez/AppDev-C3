#!/usr/bin/env python3
"""
Analizador Léxico Optimizado para C++
------------------------------------
Implementación eficiente basada en matriz de transición para análisis léxico.
Optimizado para reducir tiempo de ejecución y consumo de memoria.

Características:
- Uso de NumPy para matrices de transición de alta eficiencia
- Procesamiento de tokens con un solo paso por el archivo
- Manejo optimizado de cadenas
- Formato de salida simplificado: <token_id> <entrada_tabla>
"""

import sys
import numpy as np
from enum import IntEnum, auto

class CharType(IntEnum):
    """Enumeración de tipos de caracteres para la matriz de transición."""
    LETTER = 0      # Letras (a-z, A-Z, _)
    DIGIT = 1       # Dígitos (0-9)
    WHITE = 2       # Espacios en blanco
    OP_CHAR = 3     # Operadores
    DELIM_CHAR = 4  # Delimitadores
    HASH = 5        # Almohadilla (#)
    D_QUOTE = 6     # Comilla doble (")
    S_QUOTE = 7     # Comilla simple (')
    SLASH = 8       # Barra (/)
    DOT = 9         # Punto (.)
    OTHER = 10      # Otros caracteres

class State(IntEnum):
    """Enumeración de estados para el autómata finito."""
    INITIAL = 0     # Estado inicial
    ID = 1          # Identificador
    NUM = 2         # Número
    OP = 3          # Operador
    DELIM = 4       # Delimitador
    PREPROC = 5     # Directiva de preprocesador
    STRING = 6      # Cadena
    CHAR = 7        # Carácter
    COMMENT = 8     # Comentario
    ERROR = 9       # Error

class Scanner:
    """
    Analizador léxico optimizado para C++ basado en matrices.
    Utiliza un enfoque table-driven con matrices NumPy para
    maximizar la eficiencia de procesamiento.
    """

    def __init__(self):
        """Inicialización del escáner con tablas precomputadas."""
        # Conjuntos de caracteres (mapeo rápido)
        self._init_char_maps()

        # Palabras clave
        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
            'if', 'int', 'long', 'register', 'return', 'short', 'signed',
            'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
            'unsigned', 'void', 'volatile', 'while', 'bool', 'class',
            'delete', 'friend', 'inline', 'new', 'operator', 'private',
            'protected', 'public', 'template', 'this', 'throw', 'try',
            'catch', 'true', 'false', 'namespace', 'using', 'virtual'
        }

        # Matrices de transición (NumPy para eficiencia)
        self.T = self._build_transition_table()

        # Estados de aceptación
        self.accept_states = {
            State.ID, State.NUM, State.OP, State.DELIM,
            State.PREPROC, State.STRING, State.CHAR
        }

        # Inicializar tablas de símbolos
        self.reset_tables()

    def reset_tables(self):
        """Reinicia las tablas de tokens para un nuevo análisis."""
        # Usar diccionarios para búsqueda O(1)
        self.id_table = {}
        self.num_table = {}
        self.str_table = {}
        self.tokens = []
        self.id_count = 1
        self.num_count = 1
        self.str_count = 1

    def _init_char_maps(self):
        """
        Inicializa mapeos de caracteres para clasificación rápida.
        Utiliza tables precalculadas para mejorar rendimiento.
        """
        # Crear mapeo ASCII rápido para tipo de carácter
        self.char_type_map = np.ones(128, dtype=np.uint8) * CharType.OTHER

        # Inicializar todas las letras y '_'
        for c in range(ord('a'), ord('z')+1):
            self.char_type_map[c] = CharType.LETTER
        for c in range(ord('A'), ord('Z')+1):
            self.char_type_map[c] = CharType.LETTER
        self.char_type_map[ord('_')] = CharType.LETTER

        # Inicializar todos los dígitos
        for c in range(ord('0'), ord('9')+1):
            self.char_type_map[c] = CharType.DIGIT

        # Inicializar espacios en blanco comunes
        for c in ' \t\n\r\f':
            self.char_type_map[ord(c)] = CharType.WHITE

        # Inicializar operadores
        for c in '+-*/=<>!&|^%~':
            self.char_type_map[ord(c)] = CharType.OP_CHAR
        self.char_type_map[ord('/')] = CharType.SLASH  # Caso especial

        # Inicializar delimitadores
        for c in '(){}[],;:':
            self.char_type_map[ord(c)] = CharType.DELIM_CHAR

        # Caracteres especiales
        self.char_type_map[ord('#')] = CharType.HASH
        self.char_type_map[ord('"')] = CharType.D_QUOTE
        self.char_type_map[ord("'")] = CharType.S_QUOTE
        self.char_type_map[ord('.')] = CharType.DOT

    def _build_transition_table(self):
        """
        Construye la matriz de transición optimizada.
        Usa NumPy para acelerar el procesamiento.
        """
        # Crear matriz con valores por defecto (Estado ERROR)
        T = np.ones((10, 11), dtype=np.uint8) * State.ERROR

        # Transiciones desde el estado INITIAL
        T[State.INITIAL, CharType.LETTER] = State.ID
        T[State.INITIAL, CharType.DIGIT] = State.NUM
        T[State.INITIAL, CharType.WHITE] = State.INITIAL
        T[State.INITIAL, CharType.OP_CHAR] = State.OP
        T[State.INITIAL, CharType.DELIM_CHAR] = State.DELIM
        T[State.INITIAL, CharType.HASH] = State.PREPROC
        T[State.INITIAL, CharType.D_QUOTE] = State.STRING
        T[State.INITIAL, CharType.S_QUOTE] = State.CHAR
        T[State.INITIAL, CharType.SLASH] = State.OP
        T[State.INITIAL, CharType.DOT] = State.NUM

        # Transiciones desde el estado ID
        T[State.ID, CharType.LETTER] = State.ID
        T[State.ID, CharType.DIGIT] = State.ID

        # Transiciones desde el estado NUM
        T[State.NUM, CharType.DIGIT] = State.NUM
        T[State.NUM, CharType.DOT] = State.NUM

        # OP, DELIM y otros estados son manejados especialmente en scan()

        return T

    def get_char_type(self, ch):
        """
        Determina el tipo de carácter de forma optimizada.

        Args:
            ch (str): Carácter a clasificar.

        Returns:
            CharType: Tipo de carácter.
        """
        # Comprobación de rango para evitar errores
        if ord(ch) < 128:
            return self.char_type_map[ord(ch)]
        return CharType.OTHER

    def scan(self, filename):
        """
        Escanea el archivo de forma optimizada.
        Recorre el contenido una sola vez generando tokens.

        Args:
            filename (str): Ruta del archivo a analizar.

        Returns:
            list: Lista de tokens generados.
        """
        try:
            # Leer el archivo completo de una vez
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error al leer archivo: {e}")
            return []

        # Reiniciar tablas
        self.reset_tables()

        # Longitud precalculada
        content_len = len(content)
        i = 0

        # Recorrer todo el contenido
        while i < content_len:
            # Saltar espacios en blanco
            while i < content_len and self.get_char_type(content[i]) == CharType.WHITE:
                i += 1

            if i >= content_len:
                break  # EOF

            # Iniciar análisis de token
            state = State.INITIAL
            token = []  # Usar lista para mejorar rendimiento de concatenación

            # Manejar comentarios (caso especial)
            if i+1 < content_len and content[i:i+2] == "//":
                i = content.find('\n', i)
                if i == -1:  # Si no hay salto de línea, ir al final
                    i = content_len
                continue

            if i+1 < content_len and content[i:i+2] == "/*":
                end_pos = content.find("*/", i+2)
                if end_pos == -1:  # Comentario no cerrado
                    i = content_len
                else:
                    i = end_pos + 2
                continue

            # Procesamiento optimizado para preprocesador
            if content[i] == '#':
                newline_pos = content.find('\n', i)
                if newline_pos == -1:
                    token_str = content[i:]
                    i = content_len
                else:
                    token_str = content[i:newline_pos]
                    i = newline_pos
                self.tokens.append(('PREPROC', token_str))
                continue

            # Procesamiento optimizado para cadenas
            if content[i] == '"':
                start_pos = i
                i += 1
                # Buscar el fin de la cadena
                while i < content_len:
                    if content[i] == '\\' and i+1 < content_len:  # Secuencia de escape
                        i += 2
                    elif content[i] == '"':
                        i += 1
                        break
                    else:
                        i += 1

                token_str = content[start_pos:i]
                if token_str not in self.str_table:
                    self.str_table[token_str] = self.str_count
                    self.str_count += 1
                self.tokens.append(('STRING', self.str_table[token_str]))
                continue

            # Procesamiento optimizado para caracteres
            if content[i] == "'":
                start_pos = i
                i += 1
                # Buscar el fin del carácter
                while i < content_len:
                    if content[i] == '\\' and i+1 < content_len:  # Secuencia de escape
                        i += 2
                    elif content[i] == "'":
                        i += 1
                        break
                    else:
                        i += 1

                token_str = content[start_pos:i]
                if token_str not in self.str_table:
                    self.str_table[token_str] = self.str_count
                    self.str_count += 1
                self.tokens.append(('CHAR', self.str_table[token_str]))
                continue

            # Procesamiento general para otros tokens
            start_pos = i

            # Algoritmo table-driven optimizado
            while i < content_len:
                ch = content[i]
                char_type = self.get_char_type(ch)

                # Transición de estado
                next_state = self.T[state, char_type]

                # Estados especiales y condiciones de terminación
                if next_state == State.ERROR:
                    break

                # Casos de límite para operadores y delimitadores
                if state in (State.OP, State.DELIM) and i > start_pos:
                    break

                # Actualizar estado
                state = next_state
                token.append(ch)
                i += 1

                # Comprobación de término para ID y NUM
                if i < content_len:
                    next_ch = content[i]
                    next_type = self.get_char_type(next_ch)

                    if state == State.ID and next_type != CharType.LETTER and next_type != CharType.DIGIT:
                        break

                    if state == State.NUM and next_type != CharType.DIGIT and next_type != CharType.DOT:
                        break

            # Convertir lista a string (más eficiente que concatenación repetida)
            token_str = ''.join(token)

            # Registrar token
            if token_str:
                if state == State.ID:
                    if token_str in self.keywords:
                        self.tokens.append(('KEYWORD', token_str))
                    else:
                        if token_str not in self.id_table:
                            self.id_table[token_str] = self.id_count
                            self.id_count += 1
                        self.tokens.append(('ID', self.id_table[token_str]))

                elif state == State.NUM:
                    if token_str not in self.num_table:
                        self.num_table[token_str] = self.num_count
                        self.num_count += 1
                    self.tokens.append(('NUM', self.num_table[token_str]))

                elif state == State.OP:
                    self.tokens.append(('OP', token_str))

                elif state == State.DELIM:
                    self.tokens.append(('DELIM', token_str))

                # Los casos de PREPROC, STRING y CHAR ya están manejados arriba

        return self.tokens

    def print_results(self):
        """
        Imprime los resultados con el formato solicitado:
        <token_id> <entrada_tabla>
        """
        print("\n=== TOKENS ===")
        for token in self.tokens:
            print(f"<{token[0]}>", end="\t\t")
            print(f"<{token[0]}, {token[1]}>")

        print("\n=== TABLA DE IDENTIFICADORES ===")
        for name, idx in sorted(self.id_table.items(), key=lambda x: x[1]):
            print(f"{idx}: {name}")

        print("\n=== TABLA DE CONSTANTES NUMÉRICAS ===")
        for val, idx in sorted(self.num_table.items(), key=lambda x: x[1]):
            print(f"{idx}: {val}")

        print("\n=== TABLA DE CADENAS ===")
        for val, idx in sorted(self.str_table.items(), key=lambda x: x[1]):
            print(f"{idx}: {val}")


def main():
    """Función principal con manejo optimizado."""
    if len(sys.argv) != 2:
        print("Uso: python lexical_analyzer.py <archivo.cpp>")
        return 1

    # Crear escáner y medir tiempo (opcional)
    import time
    start_time = time.time()

    scanner = Scanner()
    scanner.scan(sys.argv[1])
    scanner.print_results()

    # Mostrar tiempo de ejecución
    elapsed = time.time() - start_time
    print(f"\nTiempo de ejecución: {elapsed:.4f} segundos")

    return 0


if __name__ == "__main__":
    sys.exit(main())
