import subprocess
import sys
import os

# Ensure syntax_analyzer.py is in the same directory or accessible via PYTHONPATH
# If not, this import will fail. The main() function includes a check.
from syntax_analyzer import TokenParser, RecursiveDescentParser

# Define test cases - focusing on one for each target classification
TEST_CASES = [
    {
        "name": "Target: OOP Classification",
        # Simple class with a member variable - aiming for OOP only
        "code": """class MyClass {
    id myVariable
}"""
    },
    {
        "name": "Target: PP Classification",
        # Multiple standalone functions - aiming for PP
        "code": """id calculateSum ( id a id b ) {
    id sumResult
}

id printMessage ( id msg ) {
    // Some comment
}

id anotherFunction ( ) {
    id temp
}"""
    },
    {
        "name": "Target: HYB Classification",
        # Contains both a class and a standalone function - aiming for HYB
        "code": """class DataProcessor {
    id processData ( id input ) {
        id processed
    }
}

id setupSystem ( ) {
    id config
}"""
    },
    {
        "name": "Target: TEXT Classification",
        # Text with no keywords or structural symbols - aiming for TEXT
        "code": """This is just some text.
More text here.
Identifiers like var1 var2.
Punctuation . , ; ! ?
Lines without programming structure.
Not a function.
"""
    },
    {
        "name": "Faulty OOP Syntax (Expected < 100% Read)",
        # Missing id and closing brace - designed to cause a syntax error
        "code": """class {}
    id myVariable
    id anotherVar 
    }
""" 
    }
]

LEXICAL_ANALYZER_SCRIPT = "lexical_analyzer.py"
TEMP_CODE_FILE = "temp_code_input.txt"
# lexical_analyzer.py writes to this fixed name, as per its implementation
LEXER_OUTPUT_FILE = "output.txt" 

def run_test_case(snippet_name, code_snippet):
    """
    Runs a single test case:
    1. Writes snippet to temp file.
    2. Runs lexical analyzer.
    3. Reads lexer output.
    4. Parses tokens using TokenParser.
    5. Classifies tokens using RecursiveDescentParser.
    6. Prints results and cleans up.
    """
    print(f"--- Test Case: {snippet_name} ---")
    print("Original Snippet:")
    print(f"'''{code_snippet}'''") # Print snippet clearly
    print("-" * 30)

    # 1. Write snippet to a temporary file
    try:
        with open(TEMP_CODE_FILE, "w", encoding="utf-8") as f:
            f.write(code_snippet)
    except IOError as e:
        print(f"Error writing to temporary file {TEMP_CODE_FILE}: {e}")
        print("=" * 40 + "\n")
        return

    # 2. Run lexical analyzer
    try:
        # sys.executable ensures we use the same Python interpreter
        # capture_output=True helps debug lexical_analyzer.py if it fails
        process_result = subprocess.run(
            [sys.executable, LEXICAL_ANALYZER_SCRIPT, TEMP_CODE_FILE],
            check=False,  # We'll check returncode manually for better error reporting
            capture_output=True,
            text=True
        )
        if process_result.returncode != 0:
            print(f"Error running lexical analyzer for snippet: {snippet_name}")
            print(f"Command: {' '.join(process_result.args)}")
            print(f"Return code: {process_result.returncode}")
            if process_result.stdout:
                print(f"Stdout:\n{process_result.stdout}")
            if process_result.stderr:
                print(f"Stderr:\n{process_result.stderr}")
            # Attempt cleanup even if lexer fails
            if os.path.exists(TEMP_CODE_FILE):
                os.remove(TEMP_CODE_FILE)
            if os.path.exists(LEXER_OUTPUT_FILE): # Lexer might create it before erroring
                 os.remove(LEXER_OUTPUT_FILE)
            print("=" * 40 + "\n")
            return

    except FileNotFoundError:
        print(f"Error: {LEXICAL_ANALYZER_SCRIPT} not found.")
        print("Please ensure it's in the same directory as this script or in PATH.")
        if os.path.exists(TEMP_CODE_FILE): # Clean up temp input file
            os.remove(TEMP_CODE_FILE)
        print("=" * 40 + "\n")
        return
    except Exception as e: # Catch other potential subprocess errors
        print(f"An unexpected error occurred while running the lexical analyzer: {e}")
        if os.path.exists(TEMP_CODE_FILE):
            os.remove(TEMP_CODE_FILE)
        print("=" * 40 + "\n")
        return

    # 3. Read the generated "output.txt"
    lexer_output_str = ""
    try:
        with open(LEXER_OUTPUT_FILE, "r", encoding="utf-8") as f:
            lexer_output_str = f.read()
    except FileNotFoundError:
        print(f"Error: Lexer output file '{LEXER_OUTPUT_FILE}' not found after running lexer.")
        # This might happen if lexical_analyzer.py failed silently or had an issue with file I/O.
    except IOError as e:
        print(f"Error reading lexer output file {LEXER_OUTPUT_FILE}: {e}")
    
    if not lexer_output_str and code_snippet.strip(): # If lexer output is empty but input was not
        print(f"Warning: Lexer output file '{LEXER_OUTPUT_FILE}' is empty for non-empty snippet: {snippet_name}")

    print("\nRaw Output from Lexical Analyzer (content of output.txt):")
    print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
    print(lexer_output_str.strip())
    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

    # 4. Feed this output string to TokenParser().parse_scanner_output()
    token_parser = TokenParser(lexer_output_str)
    tokens = token_parser.parse_scanner_output()

    print("\nTokens Processed by TokenParser (from syntax_analyzer.py):")
    print("(These are the tokens passed to the syntax analyzer's main parsing logic)")
    if not tokens and code_snippet.strip():
        print(f"(No tokens parsed. Raw lexer output was:\n{lexer_output_str.strip()}\n)")
    elif not tokens and not code_snippet.strip():
        print("(No tokens, input snippet was empty or whitespace)")
    else:
        for token_idx, token_val in enumerate(tokens):
            print(f"  {token_idx + 1}: {token_val}")
    print("-" * 30)

    # 5. Feed the resulting tokens to RecursiveDescentParser().parse()
    classification_paradigm = "TEXT (Default or error)" # Default if parsing fails badly
    classification_certeza = 0
    classification_lectura = 0
    try:
        # Use RecursiveDescentParser and expect three return values
        syntax_parser = RecursiveDescentParser(tokens)
        classification_paradigm, classification_certeza, classification_lectura = syntax_parser.parse()
    except Exception as e:
        # This catch is for unexpected errors within RecursiveDescentParser
        print(f"Error during syntax analysis for snippet '{snippet_name}': {e}")

    print("Classification from Syntax Analyzer:")
    print(f"  Paradigm: {classification_paradigm}")
    print(f"  Certainty: {classification_certeza}%")
    print(f"  Percentage Read: {classification_lectura}%")
    print("=" * 40 + "\n")

    # 6. Clean up temporary files
    try:
        if os.path.exists(TEMP_CODE_FILE):
            os.remove(TEMP_CODE_FILE)
        if os.path.exists(LEXER_OUTPUT_FILE):
            os.remove(LEXER_OUTPUT_FILE)
    except OSError as e:
        print(f"Warning: Could not remove temporary file(s): {e}")


def main():
    # Check for lexical_analyzer.py
    if not os.path.exists(LEXICAL_ANALYZER_SCRIPT):
        print(f"Critical Error: The lexical analyzer script '{LEXICAL_ANALYZER_SCRIPT}' was not found.")
        print("Please ensure it is in the same directory as this test script.")
        return

    # Check if syntax_analyzer.py classes can be imported
    try:
        # This is a redundant check if the top-level import worked,
        # but good for a clear message if it's run in an env where it's missing.
        _ = TokenParser("") 
        _ = RecursiveDescentParser([])
    except NameError: # Catches if TokenParser or RecursiveDescentParser are not defined
        print("Critical Error: Could not use classes from 'syntax_analyzer.py'.")
        print("Please ensure 'syntax_analyzer.py' is in the same directory or accessible via PYTHONPATH,")
        print("and that it defines TokenParser and RecursiveDescentParser.")
        return
    except Exception as e: # Catch other import-related issues
        print(f"Critical Error: Problem with 'syntax_analyzer.py' components: {e}")
        return


    for test_case in TEST_CASES:
        run_test_case(test_case["name"], test_case["code"])

if __name__ == "__main__":
    main() 