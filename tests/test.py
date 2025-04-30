import os
import re

class ScannerOutputTester:
    """Tests the output of a scanner based on expected token patterns"""
    
    def __init__(self):
        # Define token IDs for the language
        self.TOKEN_IDS = {
            "class": 1,
            "(": 2,
            ")": 3,
            "{": 4,
            "}": 5,
            "this": 6,
            "new": 7,
            "identifier": 20
        }
        
        # Regular expression pattern to match valid tokens
        self.token_pattern = re.compile(r"<(\d+)(?:,(\d+))?>")
    
    def test_output_format(self, output_file="output.txt"):
        """Test if all tokens in the output file have the correct format"""
        if not os.path.exists(output_file):
            print(f"Error: Output file '{output_file}' not found")
            return False
        
        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            print("Warning: Output file is empty, no tokens to test")
            return False
        
        # Check each token for correct format
        all_passed = True
        for i, token in enumerate(lines, 1):
            if not self.token_pattern.fullmatch(token):
                print(f"Line {i}: Invalid token format: '{token}'")
                print(f"Expected format: <NUM> or <NUM,NUM>")
                all_passed = False
        
        if all_passed:
            print(f"All tokens in {output_file} have valid format")
            print(f"Total tokens: {len(lines)}")
        
        return all_passed
    
    def test_token_values(self, output_file="output.txt"):
        """Test if token values are within expected ranges"""
        if not os.path.exists(output_file):
            print(f"Error: Output file '{output_file}' not found")
            return False
        
        # Valid token ID ranges
        keyword_ids = set(self.TOKEN_IDS.values())
        identifier_id = self.TOKEN_IDS["identifier"]
        
        # Read and parse tokens
        tokens = []
        with open(output_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                match = self.token_pattern.fullmatch(line)
                if match:
                    token_id = int(match.group(1))
                    if match.group(2):
                        token_attr = int(match.group(2))
                        tokens.append((token_id, token_attr))
                    else:
                        tokens.append((token_id,))
        
        if not tokens:
            print("Warning: No valid tokens found in output file")
            return False
        
        # Check token values
        all_passed = True
        for i, token in enumerate(tokens, 1):
            if len(token) == 1:
                # Single value token (keyword or symbol)
                if token[0] not in keyword_ids:
                    print(f"Token {i}: Invalid token ID: {token[0]}")
                    print(f"Expected one of: {sorted(keyword_ids)}")
                    all_passed = False
            elif len(token) == 2:
                # Token with attribute (identifier)
                if token[0] != identifier_id:
                    print(f"Token {i}: Expected identifier ID {identifier_id}, got {token[0]}")
                    all_passed = False
                if token[1] <= 0:
                    print(f"Token {i}: Invalid symbol table reference: {token[1]}")
                    print("Symbol table references should be positive")
                    all_passed = False
        
        if all_passed:
            print(f"All token values in {output_file} are valid")
        
        return all_passed
    
    def compare_with_expected(self, expected_tokens, output_file="output.txt"):
        """Compare scanner output with expected tokens"""
        if not os.path.exists(output_file):
            print(f"Error: Output file '{output_file}' not found")
            return False
        
        # Read actual tokens
        actual_tokens = []
        with open(output_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    actual_tokens.append(line)
        
        # Convert expected tokens to string format if needed
        expected_str_tokens = []
        for token in expected_tokens:
            if isinstance(token, tuple):
                if len(token) == 1:
                    expected_str_tokens.append(f"<{token[0]}>")
                else:
                    expected_str_tokens.append(f"<{token[0]},{token[1]}>")
            else:
                expected_str_tokens.append(token)
        
        # Compare lengths
        if len(actual_tokens) != len(expected_str_tokens):
            print(f"Token count mismatch. Expected {len(expected_str_tokens)}, got {len(actual_tokens)}")
            return False
        
        # Compare each token
        all_match = True
        for i, (expected, actual) in enumerate(zip(expected_str_tokens, actual_tokens), 1):
            if expected != actual:
                print(f"Token mismatch at position {i}. Expected {expected}, got {actual}")
                all_match = False
        
        if all_match:
            print("All tokens match expected output!")
        
        return all_match
    
    def print_token_statistics(self, output_file="output.txt"):
        """Print statistics about tokens in the output file"""
        if not os.path.exists(output_file):
            print(f"Error: Output file '{output_file}' not found")
            return
        
        # Token type names (reverse of TOKEN_IDS)
        token_names = {v: k for k, v in self.TOKEN_IDS.items()}
        
        # Count occurrences of each token type
        token_counts = {}
        identifiers = set()
        
        with open(output_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                match = self.token_pattern.fullmatch(line)
                if match:
                    token_id = int(match.group(1))
                    token_counts[token_id] = token_counts.get(token_id, 0) + 1
                    
                    if token_id == self.TOKEN_IDS["identifier"] and match.group(2):
                        identifiers.add(int(match.group(2)))
        
        # Print statistics
        print(f"\nToken Statistics for {output_file}:")
        print("-" * 40)
        for token_id, count in sorted(token_counts.items()):
            token_name = token_names.get(token_id, f"Unknown token ({token_id})")
            print(f"{token_name}: {count}")
        
        print(f"\nUnique identifiers: {len(identifiers)}")
        print(f"Total tokens: {sum(token_counts.values())}")

def main():
    """Main function to test scanner output"""
    tester = ScannerOutputTester()
    
    print("Scanner Output Tester")
    print("=====================")
    
    # Test case 1: Format validation
    print("\n1. Testing token format...")
    format_valid = tester.test_output_format()
    
    # Test case 2: Value validation
    print("\n2. Testing token values...")
    values_valid = tester.test_token_values()
    
    # Test case 3: Compare with expected output for "class Example { method() { } }"
    print("\n3. Testing specific example...")
    expected_tokens = [
        "<1>",           # class
        "<20,1>",        # Example (identifier)
        "<4>",           # {
        "<20,2>",        # method (identifier)
        "<2>",           # (
        "<3>",           # )
        "<4>",           # {
        "<5>",           # }
        "<5>"            # }
    ]
    tester.compare_with_expected(expected_tokens)
    
    # Print token statistics
    print("\n4. Token statistics:")
    tester.print_token_statistics()
    
    # Overall result
    print("\nSummary:")
    print("-" * 40)
    if format_valid and values_valid:
        print("✓ Basic tests passed! Scanner output seems valid.")
    else:
        print("✗ Some tests failed. See above for details.")

if __name__ == "__main__":
    main()
