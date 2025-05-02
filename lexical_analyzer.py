ACCEPT_STATE = 2
ERROR_STATE = 3

LPAREN, RPAREN, CHAR, DEL = range(4)

def categorize(ch: str): 
    if ch == '(':
        return LPAREN
    elif ch == ')':
        return RPAREN
    elif ch.isalpha():
        return CHAR
    else:
        return DEL

T = {
    0: {LPAREN: ACCEPT_STATE, RPAREN: ACCEPT_STATE, CHAR: 1, DEL: ERROR_STATE},
    1: {LPAREN: ACCEPT_STATE, RPAREN: ACCEPT_STATE, CHAR: 1, DEL: ACCEPT_STATE}
}

# Set of recognizable tokens
TOKENS = {
    '(': 2, ')': 3, '{': 4, '}': 5
}

RESERVED_KEYWORDS = {
    'class': 1, 'this': 6, 'new': 7
}

# Global variables
input_text = ""
pos = 0
EOF = None
tokens = []
symbol_table = {}
error_flag = False
lexeme = ""

def next_input_character():
    global pos
    if pos < len(input_text):
        c = input_text[pos]
        pos += 1
        return c
    return EOF

def Accept(state):
    return state == ACCEPT_STATE

def Error(state):
    return state == ERROR_STATE

def Advance(state, ch):
    cat = categorize(ch)
    nxt = T.get(state, {}).get(cat, ERROR_STATE)
    return not (Accept(nxt) or Error(nxt))

def record_Token(ch):
    global lexeme, error_flag
    if lexeme:
        key = lexeme.lower()
        if key in RESERVED_KEYWORDS:
            tokens.append(RESERVED_KEYWORDS[key])
        else:
            idx = symbol_table.setdefault(key, len(symbol_table) + 1)
            tokens.append((20, idx))  # IDENTIFIER = 20
        lexeme = ""
    else:
        if ch in TOKENS:
            tokens.append(TOKENS[ch])
        else:
            error_flag = True

def error_message():
    global error_flag
    error_flag = True

# Main DFA loop
def scan():
    global lexeme
    ch = next_input_character()
    while ch != EOF:
        state = 0
        lexeme = ""
        while not Accept(state) and not Error(state):
            cat = categorize(ch)
            state = T[state].get(cat, ERROR_STATE)
            if Advance(state, ch):
                if cat == CHAR:
                    lexeme += ch
                ch = next_input_character()
                if ch == EOF:
                    break

        if Accept(state):
            record_Token(ch)
            if ch not in TOKENS:
                ch = next_input_character()
        else:
            error_message()
        ch = next_input_character()

# Example usage
def main():
    global input_text, pos
    input_text = "(class new this)"
    pos = 0
    scan()
    if error_flag:
        print("ERROR")
    else:
        print("Tokens:", tokens)

if __name__ == "__main__":
    main()