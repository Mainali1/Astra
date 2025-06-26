"""
Astra AI Assistant - Calculator Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import re
from typing import Dict, Any
import math
from src.config import Config

logger = logging.getLogger(__name__)


class CalculatorFeature:
    """Calculator feature for Astra."""

    def __init__(self, config: Config):
        """Initialize the calculator feature."""
        self.config = config
        self._operators = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y if y != 0 else float("inf"),
            "^": lambda x, y: x**y,
            "sqrt": lambda x: math.sqrt(x) if x >= 0 else float("nan"),
            "sin": lambda x: math.sin(math.radians(x)),
            "cos": lambda x: math.cos(math.radians(x)),
            "tan": lambda x: math.tan(math.radians(x)),
        }

    def _tokenize(self, expression: str) -> list:
        """Convert expression string into tokens."""
        # Replace mathematical words with symbols
        expression = expression.lower()
        expression = expression.replace("plus", "+")
        expression = expression.replace("minus", "-")
        expression = expression.replace("times", "*")
        expression = expression.replace("divided by", "/")
        expression = expression.replace("power", "^")

        # Add spaces around operators
        expression = re.sub(r"([\+\-\*/\(\)\^])", r" \1 ", expression)

        # Split into tokens
        return [token.strip() for token in expression.split() if token.strip()]

    def _evaluate(self, tokens: list) -> float:
        """Evaluate a mathematical expression from tokens."""
        try:
            # Simple recursive descent parser
            def parse_number() -> float:
                token = tokens.pop(0)
                if token in ["sin", "cos", "tan", "sqrt"]:
                    # Handle functions
                    if tokens and tokens[0] == "(":
                        tokens.pop(0)  # Remove '('
                        value = parse_expression()
                        if tokens and tokens[0] == ")":
                            tokens.pop(0)  # Remove ')'
                            return self._operators[token](value)
                return float(token)

            def parse_factor() -> float:
                if not tokens:
                    raise ValueError("Unexpected end of expression")

                if tokens[0] == "(":
                    tokens.pop(0)  # Remove '('
                    result = parse_expression()
                    if tokens and tokens[0] == ")":
                        tokens.pop(0)  # Remove ')'
                        return result
                    raise ValueError("Missing closing parenthesis")

                if tokens[0] in ["sin", "cos", "tan", "sqrt"]:
                    return parse_number()

                try:
                    return parse_number()
                except ValueError:
                    raise ValueError(f"Invalid number: {tokens[0]}")

            def parse_term() -> float:
                result = parse_factor()
                while tokens and tokens[0] in ["*", "/", "^"]:
                    op = tokens.pop(0)
                    result = self._operators[op](result, parse_factor())
                return result

            def parse_expression() -> float:
                result = parse_term()
                while tokens and tokens[0] in ["+", "-"]:
                    op = tokens.pop(0)
                    result = self._operators[op](result, parse_term())
                return result

            return parse_expression()

        except Exception as e:
            logger.error(f"Error evaluating expression: {str(e)}")
            raise ValueError(f"Invalid expression: {str(e)}")

    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle calculator-related intents."""
        try:
            expression = intent.get("parameters", {}).get("expression", "")
            if not expression:
                return "I need an expression to calculate."

            # Tokenize and evaluate
            tokens = self._tokenize(expression)
            result = self._evaluate(tokens.copy())

            # Format result
            if result.is_integer():
                return f"The result is {int(result)}"
            else:
                return f"The result is {result:.2f}"

        except ValueError as e:
            return f"I couldn't calculate that: {str(e)}"
        except Exception as e:
            logger.error(f"Error in calculator: {str(e)}")
            return "I'm sorry, but I encountered an error while calculating."

    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Calculator is always available as it's offline

    async def cleanup(self):
        """Clean up resources."""
        pass  # No cleanup needed for calculator
