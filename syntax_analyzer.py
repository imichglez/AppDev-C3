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
            '7': 'class',    # class keyword  # for keyword
            '1': '(',        # left parenthesis
            '2': ')',        # right parenthesis
            '3': '{',        # left brace
            '4': '}',        # right brace
        }
        
        lines = self.scanner_output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Ignorar tabla de símbolos
            if line.startswith('Symbol Table:') or ':' in line and not line.startswith('<'):
                break
                
            # Parsear tokens del formato <codigo> o <codigo, id>
            if line.startswith('<') and line.endswith('>'):
                token_content = line[1:-1]  # Remover < y >
                
                # Token simple <codigo>
                if ',' not in token_content:
                    code = token_content
                    if code in TOKEN_MAP:
                        token_type = TOKEN_MAP[code]
                        self.tokens.append((token_type, token_type))
                
                # Token con ID <codigo, id> (identificadores)
                else:
                    parts = token_content.split(',')
                    code = parts[0].strip()
                    if code == '20':  # Identificador
                        self.tokens.append(('id', f'id_{parts[1].strip()}'))
        
        return self.tokens

class ParserClasificadorIntegrado:
    """
    Parser clasificador integrado con el analizador léxico
    """
    def __init__(self, tokens):
        self.tokens = tokens + [('$', '$')]
        self.position = 0
        self.current_token = self.tokens[0] if self.tokens else ('$', '$')
        
        # Contadores para clasificación
        self.clases_encontradas = 0
        self.funciones_encontradas = 0
        
        # Control de errores con recovery
        self.errores_encontrados = 0
        self.best_match_position = 0
        self.best_match_clases = 0
        self.best_match_funciones = 0
        
    def get_next_token(self):
        """Obtiene el siguiente token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        return self.current_token
    
    def match(self, expected_token):
        """
        Match() según el documento TC3002B
        Retorna True si coincide, False si no
        """
        if self.current_token[0] == expected_token:
            self.get_next_token()
            return True
        return False
    
    def update_best_match(self):
        """Actualiza el mejor match encontrado"""
        if self.position > self.best_match_position:
            self.best_match_position = self.position
            self.best_match_clases = self.clases_encontradas
            self.best_match_funciones = self.funciones_encontradas
    
    def clasificar_mejor_match(self):
        """Clasifica basado en el mejor match"""
        if self.best_match_clases > 0:
            return "OOP"
        else:
            return "PP"
    
    def skip_to_sync_token(self):
        """Recovery: salta hasta token de sincronización"""
        sync_tokens = {'class', '{', '}', '$', ')'}
        while (self.current_token[0] not in sync_tokens and 
               self.current_token[0] != '$'):
            self.get_next_token()
    
    def parse(self):
        """Función principal de parsing con recovery"""
        try:
            self.S()
            if self.current_token[0] == '$':
                self.update_best_match()
                return True, self.clasificar_mejor_match()
        except:
            pass
        
        # Si falla, usar mejor match encontrado
        return False, self.clasificar_mejor_match()
    
    def S(self):
        """S -> DCL S'"""
        if self.current_token[0] in ['class', 'id', '{', '(', '$']:
            self.DCL()
            self.S_prime()
        else:
            self.skip_to_sync_token()
    
    def S_prime(self):
        """S' -> S | ε"""
        if self.current_token[0] in ['class', 'id', '{', '(']:
            self.S()
        elif self.current_token[0] in ['$', '}']:
            return  # epsilon production
        else:
            self.skip_to_sync_token()
    
    def DCL(self):
        """
        DCL -> class id { S }    # OOP
             | id (TEXT)         # PP
             | TEXT DCL'
        """
        if self.current_token[0] == 'class':
            # DETECTADO: Código OOP
            self.clases_encontradas += 1
            self.update_best_match()
            
            if not self.match('class'):
                self.skip_to_sync_token()
                return
            if not self.match('id'):
                self.skip_to_sync_token()
                return
            if not self.match('{'):
                self.skip_to_sync_token()
                return
            self.S()
            if not self.match('}'):
                self.skip_to_sync_token()
                return
                
        elif self.current_token[0] == 'id':
            # Lookahead para decidir función vs TEXT DCL'
            saved_pos = self.position
            saved_token = self.current_token
            
            self.get_next_token()
            if self.current_token[0] == '(':
                # DETECTADO: Función (PP)
                self.funciones_encontradas += 1
                self.update_best_match()
                
                # Restaurar y procesar id (TEXT)
                self.position = saved_pos
                self.current_token = saved_token
                if not self.match('id'):
                    self.skip_to_sync_token()
                    return
                if not self.match('('):
                    self.skip_to_sync_token()
                    return
                self.TEXT()
                if not self.match(')'):
                    self.skip_to_sync_token()
                    return
            else:
                # Restaurar y procesar TEXT DCL'
                self.position = saved_pos
                self.current_token = saved_token
                self.TEXT()
                self.DCL_prime()
                
        elif self.current_token[0] in ['{', '('] or self.current_token[0] in ['class', 'id', '{', '(', '$', '}']:
            self.TEXT()
            self.DCL_prime()
        else:
            self.skip_to_sync_token()
    
    def DCL_prime(self):
        """
        DCL' -> { S }
              | (TEXT) { S }    # PP - Función con parámetros
              | ε
        """
        if self.current_token[0] == '{':
            if not self.match('{'):
                self.skip_to_sync_token()
                return
            self.S()
            if not self.match('}'):
                self.skip_to_sync_token()
                return
                
        elif self.current_token[0] == '(':
            # DETECTADO: Función con parámetros (PP)
            self.funciones_encontradas += 1
            self.update_best_match()
            
            if not self.match('('):
                self.skip_to_sync_token()
                return
            self.TEXT()
            if not self.match(')'):
                self.skip_to_sync_token()
                return
            if not self.match('{'):
                self.skip_to_sync_token()
                return
            self.S()
            if not self.match('}'):
                self.skip_to_sync_token()
                return
                
        elif self.current_token[0] in ['class', 'id', '{', '(', '$', '}']:
            return  # epsilon production
        else:
            self.skip_to_sync_token()
    
    def TEXT(self):
        """TEXT -> id TEXT' | ε"""
        if self.current_token[0] == 'id':
            if not self.match('id'):
                self.skip_to_sync_token()
                return
            self.TEXT_prime()
        elif self.current_token[0] in [')', '{', '(', 'class', 'id', '$', '}']:
            return  # epsilon production
        else:
            self.skip_to_sync_token()
    
    def TEXT_prime(self):
        """TEXT' -> TEXT | ε"""
        if self.current_token[0] == 'id':
            self.TEXT()
        elif self.current_token[0] in [')', '{', '(', 'class', 'id', '$', '}']:
            return  # epsilon production
        else:
            self.skip_to_sync_token()

def leer_salida_scanner(archivo_scanner):
    """Lee la salida del analizador léxico"""
    try:
        with open(archivo_scanner, 'r', encoding='utf-8') as file:
            return file.read()
    except:
        return None

def clasificar_desde_scanner(archivo_scanner):
    """
    Función principal que clasifica código desde la salida del scanner
    
    Args:
        archivo_scanner (str): Archivo con la salida del analizador léxico
        
    Returns:
        str: "OOP" o "PP"
    """
    # Leer salida del scanner
    scanner_output = leer_salida_scanner(archivo_scanner)
    if scanner_output is None:
        return "PP"
    
    try:
        # Parsear tokens del scanner
        token_parser = TokenParser(scanner_output)
        tokens = token_parser.parse_scanner_output()
        
        if not tokens:
            return "PP"
        
        # Crear parser y clasificar
        parser = ParserClasificadorIntegrado(tokens)
        resultado, paradigma = parser.parse()
        
        return paradigma
        
    except Exception:
        return "PP"

def ejecutar_analisis_completo(archivo_codigo):
    """
    Ejecuta el análisis completo: Scanner + Parser
    
    Args:
        archivo_codigo (str): Archivo con código fuente
        
    Returns:
        str: "OOP" o "PP"
    """
    # Paso 1: Ejecutar scanner sobre el archivo de código
    import subprocess
    
    try:
        # Ejecutar el scanner (asumiendo que genera output.txt)
        subprocess.run([sys.executable, "scanner.py", archivo_codigo], 
                      check=True, capture_output=True)
        
        # Paso 2: Clasificar usando la salida del scanner
        resultado = clasificar_desde_scanner("output.txt")
        
        return resultado
        
    except Exception:
        return "PP"

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("PP")
        sys.exit(0)
    
    archivo_entrada = sys.argv[1]
    
    if not os.path.exists(archivo_entrada):
        print("PP")
        sys.exit(0)
    
    # Determinar si es salida de scanner o código fuente
    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        contenido = f.read().strip()
    
    # Si contiene tokens del formato <codigo>, es salida del scanner
    if contenido.startswith('<') and '>' in contenido:
        resultado = clasificar_desde_scanner(archivo_entrada)
    else:
        # Es código fuente, ejecutar análisis completo
        resultado = ejecutar_analisis_completo(archivo_entrada)
    
    print(resultado)

if __name__ == "__main__":
    main()
