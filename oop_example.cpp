 // Object-Oriented Programming Example
#include <iostream>
#include <string>
#include <vector>

// Base class
class Shape {
protected:
    std::string name;

public:
    Shape(const std::string& n) : name(n) {}
    virtual ~Shape() {}

    virtual double calculateArea() const = 0;
    virtual void display() const {
        std::cout << "Shape: " << name << std::endl;
    }
};

// Derived class
class Circle : public Shape {
private:
    double radius;

public:
    Circle(double r) : Shape("Circle"), radius(r) {}

    double calculateArea() const override {
        return 3.14159 * radius * radius;
    }

    void display() const override {
        Shape::display();
        std::cout << "Radius: " << radius << std::endl;
        std::cout << "Area: " << calculateArea() << std::endl;
    }
};

// Another derived class
class Rectangle : public Shape {
private:
    double width;
    double height;

public:
    Rectangle(double w, double h) : Shape("Rectangle"), width(w), height(h) {}

    double calculateArea() const override {
        return width * height;
    }

    void display() const override {
        Shape::display();
        std::cout << "Width: " << width << std::endl;
        std::cout << "Height: " << height << std::endl;
        std::cout << "Area: " << calculateArea() << std::endl;
    }
};

// Main function
int main() {
    // Create objects
    Circle circle(5.0);
    Rectangle rectangle(4.0, 6.0);

    // Use polymorphism
    std::vector<Shape*> shapes;
    shapes.push_back(&circle);
    shapes.push_back(&rectangle);

    // Process shapes
    for (Shape* shape : shapes) {
        shape->display();
        std::cout << std::endl;
    }

    return 0;
}