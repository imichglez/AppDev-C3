 // Example file with lexical errors
#include <iostream>

int main() {
    // Error 1: Invalid identifier (starts with number)
    int 123variable = 42;

    // Error 2: Invalid operator combination
    int x = 5;
    x =+ 3;  // Should be +=

    // Error 3: Unclosed string literal
    std::string message = "This is an unclosed string;

    // Error 4: Invalid character in identifier
    int my@variable = 10;

    // Error 5: Invalid number format
    double number = 123.456.789;

    // Error 6: Unmatched parentheses
    if (x > 0 {
        std::cout << "Positive" << std::endl;
    }

    // Error 7: Invalid escape sequence
    char c = '\q';

    // Error 8: Invalid comment
    /* This is an unclosed comment

    // Error 9: Invalid operator
    int y = x @ 5;

    // Error 10: Invalid punctuation
    int z = x . y;

    return 0;
}