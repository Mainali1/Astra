"""
Calculator Feature for Astra Voice Assistant
Supports basic arithmetic, scientific functions, and unit conversions
"""

import re
import math
from typing import Dict, Any, Optional
from datetime import datetime

# Feature information
FEATURE_INFO = {
    'name': 'calculator',
    'description': 'Perform mathematical calculations including basic arithmetic, scientific functions, and unit conversions',
    'category': 'productivity',
    'keywords': ['calculate', 'math', 'equation', 'compute', 'add', 'subtract', 'multiply', 'divide', 'percentage'],
    'examples': [
        'Calculate 15 plus 27',
        'What is 25 times 4?',
        'What is 15 percent of 200?',
        'Calculate the square root of 144',
        'Convert 100 degrees Celsius to Fahrenheit'
    ],
    'version': '1.0.0',
    'author': 'Astra Team'
}

class Calculator:
    """Advanced calculator with scientific functions and unit conversions"""
    
    def __init__(self):
        self.history = []
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'phi': 1.618033988749895,  # Golden ratio
            'sqrt2': math.sqrt(2),
            'sqrt3': math.sqrt(3)
        }
        
        # Unit conversion factors
        self.conversions = {
            'temperature': {
                'celsius_to_fahrenheit': lambda c: (c * 9/5) + 32,
                'fahrenheit_to_celsius': lambda f: (f - 32) * 5/9,
                'celsius_to_kelvin': lambda c: c + 273.15,
                'kelvin_to_celsius': lambda k: k - 273.15
            },
            'length': {
                'meters_to_feet': lambda m: m * 3.28084,
                'feet_to_meters': lambda f: f / 3.28084,
                'kilometers_to_miles': lambda km: km * 0.621371,
                'miles_to_kilometers': lambda mi: mi / 0.621371
            },
            'weight': {
                'kilograms_to_pounds': lambda kg: kg * 2.20462,
                'pounds_to_kilograms': lambda lb: lb / 2.20462
            }
        }
    
    def parse_expression(self, text: str) -> str:
        """Parse natural language into mathematical expression"""
        text = text.lower().strip()
        
        # Replace words with operators
        replacements = {
            'plus': '+',
            'minus': '-',
            'times': '*',
            'multiplied by': '*',
            'divided by': '/',
            'over': '/',
            'to the power of': '**',
            'squared': '**2',
            'cubed': '**3',
            'percent': '/100',
            'percentage': '/100'
        }
        
        for word, symbol in replacements.items():
            text = text.replace(word, symbol)
        
        # Handle special cases
        text = re.sub(r'(\d+)\s*percent\s*of\s*(\d+)', r'\1/100*\2', text)
        text = re.sub(r'(\d+)\s*%\s*of\s*(\d+)', r'\1/100*\2', text)
        
        # Extract numbers and operators
        expression = re.sub(r'[^0-9+\-*/()., ]', '', text)
        expression = expression.replace(',', '')
        
        return expression.strip()
    
    def evaluate_expression(self, expression: str) -> float:
        """Safely evaluate mathematical expression"""
        try:
            # Replace constants
            for const_name, const_value in self.constants.items():
                expression = expression.replace(const_name, str(const_value))
            
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'pow': pow,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'floor': math.floor,
                'ceil': math.ceil,
                'pi': math.pi,
                'e': math.e
            })
            
            return float(result)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
    
    def convert_units(self, text: str) -> Optional[Dict[str, Any]]:
        """Convert units based on natural language input"""
        text = text.lower()
        
        # Temperature conversions
        temp_patterns = [
            (r'(\d+(?:\.\d+)?)\s*degrees?\s*celsius?\s*to\s*fahrenheit', 'celsius_to_fahrenheit'),
            (r'(\d+(?:\.\d+)?)\s*degrees?\s*fahrenheit\s*to\s*celsius', 'fahrenheit_to_celsius'),
            (r'(\d+(?:\.\d+)?)\s*celsius?\s*to\s*fahrenheit', 'celsius_to_fahrenheit'),
            (r'(\d+(?:\.\d+)?)\s*fahrenheit\s*to\s*celsius', 'fahrenheit_to_celsius')
        ]
        
        for pattern, conversion in temp_patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                result = self.conversions['temperature'][conversion](value)
                return {
                    'type': 'temperature_conversion',
                    'from_value': value,
                    'to_value': round(result, 2),
                    'conversion': conversion
                }
        
        # Length conversions
        length_patterns = [
            (r'(\d+(?:\.\d+)?)\s*meters?\s*to\s*feet', 'meters_to_feet'),
            (r'(\d+(?:\.\d+)?)\s*feet?\s*to\s*meters', 'feet_to_meters'),
            (r'(\d+(?:\.\d+)?)\s*kilometers?\s*to\s*miles', 'kilometers_to_miles'),
            (r'(\d+(?:\.\d+)?)\s*miles?\s*to\s*kilometers', 'miles_to_kilometers')
        ]
        
        for pattern, conversion in length_patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                result = self.conversions['length'][conversion](value)
                return {
                    'type': 'length_conversion',
                    'from_value': value,
                    'to_value': round(result, 2),
                    'conversion': conversion
                }
        
        return None
    
    def format_result(self, result: float) -> str:
        """Format calculation result for display"""
        if result == int(result):
            return str(int(result))
        else:
            return f"{result:.4f}".rstrip('0').rstrip('.')
    
    def add_to_history(self, expression: str, result: float):
        """Add calculation to history"""
        self.history.append({
            'expression': expression,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 calculations
        if len(self.history) > 50:
            self.history.pop(0)

def handle_calculator_command(text: str) -> Dict[str, Any]:
    """Handle calculator commands"""
    calculator = Calculator()
    try:
        # Check for unit conversion first
        conversion_result = calculator.convert_units(text)
        if conversion_result:
            if conversion_result['type'] == 'temperature_conversion':
                if 'celsius_to_fahrenheit' in conversion_result['conversion']:
                    response = f"{conversion_result['from_value']}°C is {conversion_result['to_value']}°F"
                else:
                    response = f"{conversion_result['from_value']}°F is {conversion_result['to_value']}°C"
                return {
                    'success': True,
                    'response': response,
                    'data': conversion_result
                }
            elif conversion_result['type'] == 'length_conversion':
                response = f"{conversion_result['from_value']} {conversion_result['conversion'].split('_')[0]} is {conversion_result['to_value']} {conversion_result['conversion'].split('_')[-1]}"
                return {
                    'success': True,
                    'response': response,
                    'data': conversion_result
                }
            # TODO: Integrate with main converter feature for more unit types
        # Otherwise, try to parse and evaluate as math
        expression = calculator.parse_expression(text)
        if not expression:
            return {
                'success': False,
                'response': 'Could not parse the expression. Please try again.',
                'error': 'Parse error'
            }
        try:
            result = calculator.evaluate_expression(expression)
            calculator.add_to_history(expression, result)
            formatted = calculator.format_result(result)
            return {
                'success': True,
                'response': f'Result: {formatted}',
                'data': {
                    'expression': expression,
                    'result': result
                }
            }
        except Exception as e:
            return {
                'success': False,
                'response': f'Error evaluating expression: {e}',
                'error': str(e)
            }
    except Exception as e:
        return {
            'success': False,
            'response': f'Error: {e}',
            'error': str(e)
        } 