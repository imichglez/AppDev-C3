import sys
import os
import re


class TokenParser:
    """
    Clase para parsear la salida del analizador léxico
    """

    def __init__(self, scanner_output):
        self.scanner_output = scanner_output
        self.tokens = []

    def parse_scanner_output(self):
        """
        Convierte la salida del scanner en tokens para el parser
        """
        # Mapeo de códigos del scanner a tokens del parser
        TOKEN_MAP = {
            "7": "class",  # class keyword
            "1": "(",  # left parenthesis
            "2": ")",  # right parenthesis
            "3": "{",  # left brace
            "4": "}",  # right brace
        }

        lines = self.scanner_output.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Ignorar tabla de símbolos
            if (
                line.startswith("Symbol Table:")
                or ":" in line
                and not line.startswith("<")
            ):
                break

            # Parsear tokens del formato <codigo> o <codigo, id>
            if line.startswith("<") and line.endswith(">"):
                token_content = line[1:-1]  # Remover < y >

                # Token simple <codigo>
                if "," not in token_content:
                    code = token_content
                    if code in TOKEN_MAP:
                        token_type = TOKEN_MAP[code]
                        self.tokens.append((token_type, token_type))

                # Token con ID <codigo, id> (identificadores)
                else:
                    parts = token_content.split(",")
                    code = parts[0].strip()
                    if code == "20":  # Identificador
                        self.tokens.append(("id", f"id_{parts[1].strip()}"))

        return self.tokens


class RecursiveDescentParser:
    """
    Recursive Descent Parser
    """

    def __init__(self, tokens):
        self.tokens = tokens + [("$", "$")]
        self.position = 0
        self.current_token = self.tokens[0] if self.tokens else ("$", "$")
        self.tokens_total = len(self.tokens) - 1  # Excluir EOF

        # Contadores para clasificación (best match tracking)
        self.clases_encontradas = 0
        self.funciones_encontradas = 0
        self.tokens_programacion_validos = 0
        self.tokens_procesados_exitosamente = 0
        self.errores_sintacticos = 0

        # Best match tracking
        self.best_match_position = 0
        self.best_match_clases = 0
        self.best_match_funciones = 0
        self.best_match_tokens_procesados = 0

        # Recovery limitado
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3

    def get_next_token(self):
        """Obtiene el siguiente token del scanner"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        return self.current_token

    def match(self, expected_token):

        if self.current_token[0] == expected_token:
            self.tokens_procesados_exitosamente += 1
            if expected_token in ["class", "id", "{", "}", "(", ")"]:
                self.tokens_programacion_validos += 1
            self.get_next_token()
            self.update_best_match()
        else:
            self.errores_sintacticos += 1
            # En lugar de Error, best match recovery
            self.best_match_recovery()

    def update_best_match(self):
        """Actualiza el mejor match encontrado"""
        if self.position >= self.best_match_position:
            self.best_match_position = self.position
            self.best_match_clases = self.clases_encontradas
            self.best_match_funciones = self.funciones_encontradas
            self.best_match_tokens_procesados = self.tokens_procesados_exitosamente

    def best_match_recovery(self):
        """
        Recovery
        """
        if self.recovery_attempts >= self.max_recovery_attempts:
            return

        self.recovery_attempts += 1
        self.update_best_match()

        # Tokens de sincronización
        sync_tokens = {"class", "id", "{", "}", "(", ")", "$"}

        # Buscar token de sincronización
        while self.current_token[0] not in sync_tokens and self.current_token[0] != "$":
            self.get_next_token()
            if self.position >= len(self.tokens):
                break

        self.update_best_match()

    # =====================================================
    # PROCEDIMIENTOS RECURSIVOS
    # =====================================================

    def S_procedure(self):
        """
        S -> DCL S'
        FIRST(S) = {class, id, {, (, ε}
        """
        # Verificar First(S) antes de proceder
        if self.current_token[0] in ["class", "id", "{", "("]:
            # Para S -> DCL S'
            # DCL es no-terminal, llamar procedimiento DCL
            self.DCL_procedure()
            # S' es no-terminal, llamar procedimiento S'
            self.S_prime_procedure()
        elif self.current_token[0] in ["$", "}"]:
            # S puede derivar ε a través de DCL -> ε
            self.DCL_procedure()
            self.S_prime_procedure()
        else:
            self.best_match_recovery()

    def S_prime_procedure(self):
        """
        S' -> S | ε
        FIRST+(S' -> S) = {class, id, {, (}
        FIRST+(S' -> ε) = {$, }}
        """
        if self.current_token[0] in ["class", "id", "{", "("]:
            # S' -> S
            # S es no-terminal, llamar procedimiento S
            self.S_procedure()
        elif self.current_token[0] in ["$", "}"]:
            # S' -> ε
            return
        else:
            self.best_match_recovery()

    def DCL_procedure(self):
        """
        DCL -> class id { S } | id (TEXT) | TEXT DCL' | ε
        """
        if self.current_token[0] == "class":
            # DCL -> class id { S }
            # DETECCIÓN OOP: Clase encontrada
            self.clases_encontradas += 1
            self.update_best_match()

            # Para all symbols of the RHS: class id { S }
            self.match("class")
            self.match("id")
            self.match("{")
            # S es no-terminal, llamar procedimiento S
            self.S_procedure()
            self.match("}")

        elif self.current_token[0] == "id":
            # Lookahead para distinguir entre DCL -> id (TEXT) y DCL -> TEXT DCL'
            saved_pos = self.position
            saved_token = self.current_token

            self.get_next_token()
            if self.current_token[0] == "(":
                # DCL -> id (TEXT)
                # DETECCIÓN PP: Función encontrada
                self.funciones_encontradas += 1
                self.update_best_match()

                # Restaurar posición
                self.position = saved_pos
                self.current_token = saved_token

                # Para all symbols of the RHS: id ( TEXT )
                self.match("id")
                self.match("(")
                # TEXT es no-terminal, llamar procedimiento TEXT
                self.TEXT_procedure()
                self.match(")")
            else:
                # DCL -> TEXT DCL'
                # Restaurar posición
                self.position = saved_pos
                self.current_token = saved_token

                # Para all symbols of the RHS: TEXT DCL'
                # TEXT es no-terminal, llamar procedimiento TEXT
                self.TEXT_procedure()
                # DCL' es no-terminal, llamar procedimiento DCL'
                self.DCL_prime_procedure()

        elif self.current_token[0] in ["{", "("]:
            # DCL -> TEXT DCL' (donde TEXT -> ε)
            # Para all symbols of the RHS: TEXT DCL'
            self.TEXT_procedure()
            self.DCL_prime_procedure()

        elif self.current_token[0] in ["$", "}"]:
            # DCL -> ε según conjuntos corregidos
            return
        else:
            self.best_match_recovery()

    def DCL_prime_procedure(self):
        """
        Procedimiento para DCL' según framework del Recipe
        DCL' -> { S } | (TEXT) { S } | ε
        """
        if self.current_token[0] == "{":
            # DCL' -> { S }
            # Para all symbols of the RHS: { S }
            self.match("{")
            # S es no-terminal, llamar procedimiento S
            self.S_procedure()
            self.match("}")

        elif self.current_token[0] == "(":
            # DCL' -> (TEXT) { S }
            # DETECCIÓN PP: Función con parámetros
            self.funciones_encontradas += 1
            self.update_best_match()

            # Para all symbols of the RHS: ( TEXT ) { S }
            self.match("(")
            # TEXT es no-terminal, llamar procedimiento TEXT
            self.TEXT_procedure()
            self.match(")")
            self.match("{")
            # S es no-terminal, llamar procedimiento S
            self.S_procedure()
            self.match("}")

        elif self.current_token[0] in ["class", "id", "{", "(", "$", "}"]:
            # DCL' -> ε según Follow(DCL')
            return
        else:
            self.best_match_recovery()

    def TEXT_procedure(self):
        """
        Procedimiento para TEXT
        TEXT -> id TEXT' | ε
        """
        if self.current_token[0] == "id":
            # TEXT -> id TEXT'
            # Para all symbols of the RHS: id TEXT'
            self.match("id")
            # TEXT' es no-terminal, llamar procedimiento TEXT'
            self.TEXT_prime_procedure()

        elif self.current_token[0] in [")", "{", "(", "class", "id", "$", "}"]:
            # TEXT -> ε según Follow(TEXT)
            return
        else:
            self.best_match_recovery()

    def TEXT_prime_procedure(self):
        """
        Procedimiento para TEXT'
        TEXT' -> TEXT | ε
        """
        if self.current_token[0] == "id":
            # TEXT' -> TEXT
            # Para all symbols of the RHS: TEXT
            # TEXT es no-terminal, llamar procedimiento TEXT
            self.TEXT_procedure()

        elif self.current_token[0] in [")", "{", "(", "class", "id", "$", "}"]:
            # TEXT' -> ε según Follow(TEXT')
            return
        else:
            self.best_match_recovery()

    # =====================================================
    # FUNCIÓN PRINCIPAL DEL PARSER
    # =====================================================

    def parse(self):
        """
        Función principal del parser
        Comienza con el símbolo inicial S
        """
        self.S_procedure()

        # Verificar si llegamos al final exitosamente
        if self.current_token[0] == "$":
            self.update_best_match()

        return self.clasificar_mejor_match()

    # =====================================================
    # SISTEMA DE CLASIFICACIÓN Y CÁLCULO DE MÉTRICAS
    # =====================================================

    def calcular_porcentaje_lectura(self):
        """Calcula el porcentaje de código leído/procesado"""
        if self.tokens_total == 0:
            return 100.0

        posicion_final = max(self.best_match_position, self.position)
        porcentaje = (posicion_final / self.tokens_total) * 100
        return min(round(porcentaje, 1), 100.0)

    def calcular_certeza(self, paradigma):
        """Calcula el porcentaje de certeza de la clasificación"""
        if self.tokens_total == 0:
            return 50

        # Factor 1: Porcentaje de tokens procesados exitosamente (40%)
        ratio_procesados = min(
            self.best_match_tokens_procesados / self.tokens_total, 1.0
        )
        factor_procesado = ratio_procesados * 40

        # Factor 2: Fuerza de las características encontradas (35%)
        total_caracteristicas = self.best_match_clases + self.best_match_funciones

        if paradigma == "OOP":
            if self.best_match_clases > 0:
                factor_caracteristicas = min(
                    (self.best_match_clases / max(total_caracteristicas, 1)) * 35, 35
                )
            else:
                factor_caracteristicas = 0
        elif paradigma == "PP":
            if self.best_match_funciones > 0:
                factor_caracteristicas = min(
                    (self.best_match_funciones / max(total_caracteristicas, 1)) * 35, 35
                )
            else:
                factor_caracteristicas = 0
        elif paradigma == "HYB":
            if self.best_match_clases > 0 and self.best_match_funciones > 0:
                balance = min(self.best_match_clases, self.best_match_funciones) / max(
                    total_caracteristicas, 1
                )
                factor_caracteristicas = balance * 35
            else:
                factor_caracteristicas = 0
        else:  # TEXT
            if total_caracteristicas == 0:
                factor_caracteristicas = 25
            else:
                factor_caracteristicas = max(0, 25 - (total_caracteristicas * 2))

        # Factor 3: Coherencia estructural (15%)
        factor_coherencia = max(5, 15 - (self.errores_sintacticos * 1.5))

        # Factor 4: Densidad de tokens de programación (10%)
        if self.tokens_total > 0:
            ratio_programacion = self.tokens_programacion_validos / self.tokens_total
            factor_densidad = ratio_programacion * 10
        else:
            factor_densidad = 0

        # Cálculo final
        certeza_total = (
            factor_procesado
            + factor_caracteristicas
            + factor_coherencia
            + factor_densidad
        )

        # Ajustes específicos por paradigma
        if paradigma == "TEXT":
            if ratio_procesados < 0.3:
                certeza_total = min(certeza_total + 10, 85)
        elif paradigma in ["OOP", "PP", "HYB"]:
            if total_caracteristicas < 1:
                certeza_total *= 0.8

        return max(15, min(round(certeza_total), 90))

    def clasificar_mejor_match(self):
        """Clasificación basada en el mejor match encontrado"""
        if self.best_match_clases == 0 and self.best_match_funciones == 0:
            paradigma = "TEXT"
        elif self.best_match_clases > 0 and self.best_match_funciones > 0:
            paradigma = "HYB"
        elif self.best_match_clases > 0:
            paradigma = "OOP"
        elif self.best_match_funciones > 0:
            paradigma = "PP"
        else:
            paradigma = "TEXT"

        certeza = self.calcular_certeza(paradigma)
        lectura = self.calcular_porcentaje_lectura()
        return paradigma, certeza, lectura


def leer_salida_scanner(archivo_scanner):
    """Lee la salida del analizador léxico"""
    try:
        with open(archivo_scanner, "r", encoding="utf-8") as file:
            return file.read()
    except Exception:
        return None


def clasificar_desde_scanner(archivo_scanner):
    """Función principal que clasifica código desde la salida del scanner"""
    scanner_output = leer_salida_scanner(archivo_scanner)
    if scanner_output is None:
        return "TEXT", 85, 100.0

    try:
        token_parser = TokenParser(scanner_output)
        tokens = token_parser.parse_scanner_output()

        if not tokens:
            return "TEXT", 90, 100.0

        # Usar el Recursive Descent Parser
        parser = RecursiveDescentParser(tokens)
        paradigma, certeza, lectura = parser.parse()

        return paradigma, certeza, lectura

    except Exception:
        return "TEXT", 80, 100.0


def ejecutar_analisis_completo(archivo_codigo):
    """Ejecuta el análisis completo: Scanner + Parser"""
    import subprocess

    try:
        subprocess.run(
            [sys.executable, "lexical_analyzer.py", archivo_codigo],
            check=True,
            capture_output=True,
        )

        paradigma, certeza, lectura = clasificar_desde_scanner("output.txt")
        return paradigma, certeza, lectura

    except Exception:
        return "TEXT", 75, 100.0


def main():
    if len(sys.argv) != 2:
        print("TEXT 80 100.0")
        sys.exit(0)

    archivo_entrada = sys.argv[1]

    if not os.path.exists(archivo_entrada):
        print("TEXT 85 100.0")
        sys.exit(0)

    try:
        with open(archivo_entrada, "r", encoding="utf-8") as f:
            contenido = f.read().strip()

        if contenido.startswith("<") and ">" in contenido:
            paradigma, certeza, lectura = clasificar_desde_scanner(archivo_entrada)
        else:
            paradigma, certeza, lectura = ejecutar_analisis_completo(archivo_entrada)

        print(f"{paradigma} {certeza} {lectura}")

    except Exception:
        print("TEXT 75 100.0")


if __name__ == "__main__":
    main()
