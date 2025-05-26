import sys

ACCEPT_STATE = 2
ERROR_STATE  = 3

LPAREN_ID, RPAREN_ID, LBRACE, RBRACE_ID, CHAR, DIGIT, DEL, BLANK = range(8)

class Scanner():
    def __init__(self, input_text):
        
        self.T = {
            0: {
                CHAR: 1,
                BLANK: 0,
                LPAREN_ID: ACCEPT_STATE, 
                RPAREN_ID: ACCEPT_STATE,
                LBRACE: ACCEPT_STATE, 
                RBRACE_ID: ACCEPT_STATE,
                DEL: 0,
                DIGIT: 0,
            },
            1: {
                CHAR: 1,
                DIGIT: 1,
                BLANK: ACCEPT_STATE,
                LPAREN_ID: ACCEPT_STATE, 
                RPAREN_ID: ACCEPT_STATE,
                LBRACE: ACCEPT_STATE, 
                RBRACE_ID: ACCEPT_STATE,
                DEL: ACCEPT_STATE,
            },
        }

        self.TOKEN_CODES = {'(':1, ')':2, '{':3, '}':4}
        self.RESERVED_KEYWORDS = {'class':7, 'if': 8, 'else':9, 'while': 10, 'for': 11}
        self.IDENTIFIER_ID = 20

        self.input_text = input_text
        self.input_iterator = iter(input_text)  # Create iterator from input text

        self.current_token = ""
        self.ch = None

        self.state = 0

        self.symbol_entry = {}

    def Accept(self, state: int) -> bool:
        """Checks if the current state is an accepting state."""
        return state == ACCEPT_STATE

    def Error(self, state: int) -> bool:
        """Checks if the current state is an error state."""
        return state == ERROR_STATE
        
    def error_message(self):
        """Handles lexical errors."""
        # print("ERROR")
        pass

    def categorize(self, ch: str):
        if ch is None:
            return DEL
        if ch == '(':        return LPAREN_ID
        elif ch == ')':      return RPAREN_ID
        elif ch == '{':      return LBRACE
        elif ch == '}':      return RBRACE_ID
        elif ch == ' ':      return BLANK
        elif ch == '\n':     return BLANK
        elif ch == '\t':     return BLANK
        elif ch == '\r':     return BLANK
        elif ch == '\f':     return BLANK
        elif ch == '\v':     return BLANK
        elif ch.isalpha() or ch == '_':
            return CHAR
        elif ch.isdigit():
            return DIGIT
        else:
            return DEL
        
    def record_token(self):
        # Make a substring from the initial token position to index
        token = self.current_token.strip()

        should_move_char = True
        #Here I identify the las valid character
        if len(self.current_token) > 1:
            if self.current_token[-1] in self.TOKEN_CODES: # ! CHANGED
                should_move_char = False 
            if self.categorize(self.current_token[-1]) != CHAR:
                token = self.current_token[:-1]

        # Check if the token is a reserved keyword
        if token in self.RESERVED_KEYWORDS:
            print(f"<{self.RESERVED_KEYWORDS[token]}>")

        elif token in self.TOKEN_CODES:         # Check if the token is a special symbol
            print(f"<{self.TOKEN_CODES[token]}>")

        elif token == '': # Ignore empty tokens
            # Ignore blank spaces
            pass
        else: # Identifier
            
            if token not in self.symbol_entry: # Generate a new entry
                # Add the token to the symbol table
                # and assign it a unique identifier
                self.symbol_entry[token] = len(self.symbol_entry) + 1
            print(f"<{self.IDENTIFIER_ID}, {self.symbol_entry[token]}>")

        if should_move_char:
            self.ch = self.next_input_character()

    def Advance(self, state: int, ch: str) -> bool:
        """Advances the scanner state and records the character."""
        # If the state is 0, reset the current token
        if state == 0:
            self.current_token = ""

        # If the state is error or accept, do not advance
        return not (self.Error(state) or self.Accept(state))

    def next_input_character(self):
        """Returns the next character from the input string using iterator."""
        try:
            return next(self.input_iterator)
        except StopIteration:
            self.state = ACCEPT_STATE # End of input
            return None

    def scan(self):
        self.ch = self.next_input_character()
        while self.ch is not None:  # not EOF
            self.state = 0  # start DFA
            self.current_token = ""  # reset token
            while not self.Accept(self.state) and not self.Error(self.state):
                self.current_token += self.ch
                cat = self.categorize(self.ch)
                self.state = self.T[self.state][cat]
                
                if self.Advance(self.state, self.ch):  # Updated to use self.ch
                    self.ch = self.next_input_character()
            
            # end of DFA
            if self.Accept(self.state):
                
                self.record_token()
                
            else:
                self.error_message()
                # Stop on error
                # break
    def print_symbol_table(self):
        """Prints the symbol table."""
        print("Symbol Table:")
        for token, id in self.symbol_entry.items():
            print(f"{token}: {id}")
        
def main():
    if len(sys.argv) < 2:
        print("Uso: python lexical_analyzer.py <archivo>")
        return

    with open(sys.argv[1], encoding="utf-8") as f:
        input_text = f.read()

    original_stdout = sys.stdout          # guardamos stdout “normal”
    sys.stdout = open("output.txt", "w", encoding="utf-8")

    try:
        scanner = Scanner(input_text)
        scanner.scan()        # todo lo que imprima → output.txt
        scanner.print_symbol_table()  # Imprime la tabla de símbolos
    finally:
        sys.stdout.close()                # cerramos archivo
        sys.stdout = original_stdout      # restauramos stdout

if __name__ == "__main__":
    main()