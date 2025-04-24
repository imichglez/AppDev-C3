 // Procedural Programming Example
#include <iostream>
#include <string>

// Function declarations
int calculateSum(int a, int b);
void printMessage(const std::string& message);
bool isEven(int number);
void processNumbers(int* numbers, int size);

// Main function
int main() {
    // Variable declarations
    int x = 42;
    int y = 10;
    int numbers[] = {1, 2, 3, 4, 5};

    // Function calls
    int sum = calculateSum(x, y);
    printMessage("The sum is: " + std::to_string(sum));

    // Control structures
    if (isEven(sum)) {
        printMessage("The sum is even");
    } else {
        printMessage("The sum is odd");
    }

    // Loop
    for (int i = 0; i < 5; i++) {
        printMessage("Processing number: " + std::to_string(numbers[i]));
    }

    // Array processing
    processNumbers(numbers, 5);

    return 0;
}

// Function definitions
int calculateSum(int a, int b) {
    return a + b;
}

void printMessage(const std::string& message) {
    std::cout << message << std::endl;
}

bool isEven(int number) {
    return number % 2 == 0;
}

void processNumbers(int* numbers, int size) {
    for (int i = 0; i < size; i++) {
        if (numbers[i] > 0) {
            std::cout << "Positive number: " << numbers[i] << std::endl;
        } else if (numbers[i] < 0) {
            std::cout << "Negative number: " << numbers[i] << std::endl;
        } else {
            std::cout << "Zero" << std::endl;
        }
    }
}