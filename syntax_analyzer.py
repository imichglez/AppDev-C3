import sys
import os

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
        First(S) = First(DCL) = {class, id}
        S is not nullable.
        """
        if self.current_token[0] in ["class", "id"]:
            self.DCL_procedure()
            self.S_prime_procedure()
        else:
            # Error: S must start with 'class' or 'id' based on the grammar
            self.best_match_recovery()

    def S_prime_procedure(self):
        """
        S' -> S | ε
        First+(S' -> S) = {class, id}
        First+(S' -> ε) = Follow(S') = { $, } }
        """
        if self.current_token[0] in ["class", "id"]:
            # S' -> S
            self.S_procedure()
        elif self.current_token[0] in ["$", "}"]: # Follow(S') for S' -> ε
            # S' -> ε
            return
        else:
            self.best_match_recovery()

    def DCL_procedure(self):
        """
        DCL -> class id { S } | id DCL''
        First+(DCL -> class id { S }) = {class}
        First+(DCL -> id DCL'') = {id}
        DCL is not nullable.
        """
        if self.current_token[0] == "class":
            # DCL -> class id { S }
            self.clases_encontradas += 1
            self.update_best_match()

            self.match("class")
            self.match("id")
            self.match("{")
            self.S_procedure()
            self.match("}")
        elif self.current_token[0] == "id":
            # DCL -> id DCL''
            self.match("id")
            self.DCL_double_prime_procedure() # New procedure for DCL''
        else:
            # Error: DCL must start with 'class' or 'id'
            self.best_match_recovery()

    def DCL_double_prime_procedure(self): # New procedure for DCL''
        """
        DCL'' -> (TEXT) DCL''' | TEXT DCL'
        First+(DCL'' -> (TEXT) DCL''') = {(}
        First(TEXT DCL') = (First(TEXT) - {ε}) U (if ε in First(TEXT) then First(DCL') else {})
                         = {id} U First(DCL') (since TEXT is nullable)
                         = {id} U {(, {, ε}} = {id, (, {, ε}
        """
        token = self.current_token[0]

        if token == "(":
            # Path: DCL'' -> (TEXT) DCL'''
            # This is part of "id (params) body_or_nothing" structure from DCL -> id DCL''
            self.funciones_encontradas += 1 # Count as function
            self.update_best_match()

            self.match("(")
            self.TEXT_procedure()
            self.match(")")
            self.DCL_triple_prime_procedure()
        elif token == "id":
            # Path: DCL'' -> TEXT DCL' where TEXT starts with 'id'
            # This is part of "id id ..." structure
            self.TEXT_procedure() # Will consume 'id' and then TEXT'
            self.DCL_prime_procedure()
        elif token == "{":
            # Path: DCL'' -> TEXT DCL' where TEXT -> ε and DCL' starts with '{'
            # This is part of "id {S}" structure
            self.TEXT_procedure() # TEXT -> ε
            self.DCL_prime_procedure() # DCL' -> {S} ...
        # Case where DCL'' -> TEXT DCL' and TEXT -> ε and DCL' -> ε. So DCL'' -> ε.
        # Check Follow(DCL'') = { class, id, $, } }
        # 'id' and potential '(' '{' are handled by specific productions of TEXT or DCL'.
        # Remaining tokens in Follow(DCL'') indicate DCL'' -> ε.
        elif token in ["class", "$", "}"]: # Follow(DCL'') for DCL'' -> ε (via TEXT->ε and DCL'->ε)
            self.TEXT_procedure()    # Must take TEXT -> ε path
            self.DCL_prime_procedure() # Must take DCL' -> ε path
        else:
            self.best_match_recovery()

    def DCL_triple_prime_procedure(self): # New procedure for DCL'''
        """
        DCL''' -> { S } | ε
        First+(DCL''' -> { S }) = {{ }
        First+(DCL''' -> ε) = Follow(DCL''') = { class, id, $, } }
        """
        if self.current_token[0] == "{":
            # DCL''' -> { S }
            self.match("{")
            self.S_procedure()
            self.match("}")
        elif self.current_token[0] in ["class", "id", "$", "}"]: # Follow(DCL''') for DCL''' -> ε
            # DCL''' -> ε
            return
        else:
            self.best_match_recovery()

    def DCL_prime_procedure(self): # Corrected version of existing DCL_prime_procedure
        """
        DCL' -> { S } | (TEXT) { S } | ε
        First+(DCL' -> { S }) = {{ }
        First+(DCL' -> (TEXT) { S }) = {( }
        First+(DCL' -> ε) = Follow(DCL') = { class, id, $, } }
        """
        if self.current_token[0] == "{":
            # DCL' -> { S }
            self.match("{")
            self.S_procedure()
            self.match("}")
        elif self.current_token[0] == "(":
            # DCL' -> (TEXT) { S }
            # This structure `(...) {S}` might also be counted as a function-like construct
            self.funciones_encontradas += 1 # As per original code's intent
            self.update_best_match()

            self.match("(")
            self.TEXT_procedure()
            self.match(")")
            self.match("{")
            self.S_procedure()
            self.match("}")
        elif self.current_token[0] in ["class", "id", "$", "}"]: # Follow(DCL') for DCL' -> ε
            # DCL' -> ε
            return
        else:
            self.best_match_recovery()

    def TEXT_procedure(self): # Corrected version
        """
        TEXT -> id TEXT' | ε
        First+(TEXT -> id TEXT') = {id}
        First+(TEXT -> ε) = Follow(TEXT) = { ), (, {, class, id, $, } }
        """
        if self.current_token[0] == "id":
            # TEXT -> id TEXT'
            self.match("id")
            self.TEXT_prime_procedure()
        # Check for TEXT -> ε using Follow(TEXT).
        # 'id' is already handled by the 'if' branch.
        # So, for ε, current_token must be in Follow(TEXT) - {id}.
        elif self.current_token[0] in [")", "(", "{", "class", "$", "}"]: # Follow(TEXT) excluding 'id'
            # TEXT -> ε
            return
        else:
            self.best_match_recovery()

    def TEXT_prime_procedure(self): # Corrected version
        """
        TEXT' -> TEXT | ε
        First(TEXT) = {id, ε}. If current_token is 'id', choose TEXT' -> TEXT.
        First+(TEXT' -> ε) = Follow(TEXT') = { ), (, {, class, id, $, } }
        """
        if self.current_token[0] == "id":
            # TEXT' -> TEXT
            self.TEXT_procedure()
        # Check for TEXT' -> ε using Follow(TEXT').
        # 'id' is handled by the 'if' branch.
        # So, for ε, current_token must be in Follow(TEXT') - {id}.
        elif self.current_token[0] in [")", "(", "{", "class", "$", "}"]: # Follow(TEXT') excluding 'id'
            # TEXT' -> ε
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
        # Convert relative path to absolute path
        archivo_absoluto = os.path.abspath(archivo_scanner)
        with open(archivo_absoluto, "r", encoding="utf-8") as file:
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
        # Convert relative path to absolute path
        archivo_absoluto = os.path.abspath(archivo_codigo)
        
        subprocess.run(
            [sys.executable, "lexical_analyzer.py", archivo_absoluto],
            check=True,
            capture_output=True,
        )

        # Use absolute path for output.txt in current directory
        output_path = os.path.abspath("output.txt")
        paradigma, certeza, lectura = clasificar_desde_scanner(output_path)
        return paradigma, certeza, lectura

    except Exception:
        return "TEXT", 75, 100.0


def main():
    if len(sys.argv) != 2:
        print("Uso: python syntax_analyzer.py <archivo_entrada>")
        sys.exit(0)

    archivo_entrada = sys.argv[1]

    try:
        # Convert relative path to absolute path
        archivo_absoluto = os.path.abspath(archivo_entrada)
        
        with open(archivo_absoluto, "r", encoding="utf-8") as f:
            contenido = f.read().strip()

        if contenido.startswith("<") and ">" in contenido:
            paradigma, certeza, lectura = clasificar_desde_scanner(archivo_absoluto)
        else:
            paradigma, certeza, lectura = ejecutar_analisis_completo(archivo_absoluto)

        print(f"{paradigma} {certeza} {lectura}")

    except Exception:
        print("Error al procesar el archivo")


if __name__ == "__main__":
    main()
