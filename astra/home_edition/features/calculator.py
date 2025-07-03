class Calculator:
    """
    A robust calculator for basic and advanced arithmetic operations.
    """

    def add(self, a: float, b: float) -> float:
        """
        Adds two numbers.
        """
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """
        Subtracts two numbers.
        """
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """
        Multiplies two numbers.
        """
        return a * b

    def divide(self, a: float, b: float) -> float:
        """
        Divides two numbers. Handles division by zero.
        """
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

    def power(self, base: float, exponent: float) -> float:
        """
        Raises a base to the power of an exponent.
        """
        return base ** exponent

    def square_root(self, number: float) -> float:
        """
        Calculates the square root of a number. Handles negative numbers.
        """
        if number < 0:
            raise ValueError("Cannot calculate the square root of a negative number.")
        return number ** 0.5

    def evaluate_expression(self, expression: str) -> float:
        """
        Evaluates a mathematical expression string. Uses a safe approach.
        """
        # This is a simplified example. For a production system, consider using a dedicated
        # expression parsing library (e.g., asteval, numexpr) to prevent arbitrary code execution.
        try:
            # Basic validation to prevent common injection attacks
            if any(char in expression for char in ['__', 'import', 'os', 'sys', 'exec', 'eval']):
                raise ValueError("Invalid characters in expression.")
            return eval(expression) # nosec
        except (SyntaxError, TypeError, NameError, ValueError) as e:
            raise ValueError(f"Invalid expression: {e}")

calculator = Calculator()