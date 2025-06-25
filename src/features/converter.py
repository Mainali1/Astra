"""
Unit Converter Feature for Astra Voice Assistant
Converts between different units of measurement, temperature, currency, etc.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal, getcontext

logger = logging.getLogger(__name__)

FEATURE_INFO = {
    'name': 'converter',
    'description': 'Convert between different units of measurement, temperature, currency, and more',
    'category': 'productivity',
    'keywords': ['convert', 'conversion', 'temperature', 'length', 'weight', 'currency', 'units'],
    'examples': [
        'Convert 100 degrees Fahrenheit to Celsius',
        'How many meters in 5 feet?',
        'Convert 50 dollars to euros',
        'What is 2.5 kilograms in pounds?'
    ],
    'version': '1.0.0',
    'author': 'Astra Team',
    'dependencies': [],
    'config': {
        'decimal_places': 4,
        'currency_api': 'https://api.exchangerate-api.com/v4/latest/',
        'supported_currencies': ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR']
    }
}

# Set decimal precision
getcontext().prec = 10

class UnitConverter:
    """Unit conversion functionality"""
    
    def __init__(self):
        self.decimal_places = FEATURE_INFO['config']['decimal_places']
        
        # Conversion factors
        self.temperature_conversions = {
            'celsius': {
                'fahrenheit': lambda c: c * 9/5 + 32,
                'kelvin': lambda c: c + 273.15,
                'rankine': lambda c: (c + 273.15) * 9/5
            },
            'fahrenheit': {
                'celsius': lambda f: (f - 32) * 5/9,
                'kelvin': lambda f: (f - 32) * 5/9 + 273.15,
                'rankine': lambda f: f + 459.67
            },
            'kelvin': {
                'celsius': lambda k: k - 273.15,
                'fahrenheit': lambda k: (k - 273.15) * 9/5 + 32,
                'rankine': lambda k: k * 9/5
            }
        }
        
        self.length_conversions = {
            'meters': {
                'feet': 3.28084,
                'inches': 39.3701,
                'centimeters': 100,
                'kilometers': 0.001,
                'miles': 0.000621371,
                'yards': 1.09361
            },
            'feet': {
                'meters': 0.3048,
                'inches': 12,
                'centimeters': 30.48,
                'kilometers': 0.0003048,
                'miles': 0.000189394,
                'yards': 0.333333
            },
            'inches': {
                'meters': 0.0254,
                'feet': 0.0833333,
                'centimeters': 2.54,
                'kilometers': 0.0000254,
                'miles': 0.0000157828,
                'yards': 0.0277778
            }
        }
        
        self.weight_conversions = {
            'kilograms': {
                'pounds': 2.20462,
                'grams': 1000,
                'ounces': 35.274,
                'tons': 0.00110231
            },
            'pounds': {
                'kilograms': 0.453592,
                'grams': 453.592,
                'ounces': 16,
                'tons': 0.0005
            },
            'grams': {
                'kilograms': 0.001,
                'pounds': 0.00220462,
                'ounces': 0.035274,
                'tons': 0.00000110231
            }
        }
        
        self.volume_conversions = {
            'liters': {
                'gallons': 0.264172,
                'cups': 4.22675,
                'pints': 2.11338,
                'quarts': 1.05669,
                'milliliters': 1000
            },
            'gallons': {
                'liters': 3.78541,
                'cups': 16,
                'pints': 8,
                'quarts': 4,
                'milliliters': 3785.41
            }
        }
    
    def handle_converter_command(self, text: str) -> Dict[str, Any]:
        """Handle unit conversion commands"""
        try:
            # Parse the conversion request
            conversion_info = self._parse_conversion_request(text)
            if not conversion_info:
                return {
                    'success': False,
                    'response': 'I couldn\'t understand the conversion request. Please try something like "Convert 100 degrees Fahrenheit to Celsius" or "How many meters in 5 feet?"',
                    'error': 'Invalid conversion request'
                }
            value, from_unit, to_unit = conversion_info
            # Perform the conversion
            result = self._convert(value, from_unit, to_unit)
            if result is not None:
                formatted_result = self._format_result(value, from_unit, result, to_unit)
                return {
                    'success': True,
                    'response': formatted_result,
                    'data': {
                        'value': value,
                        'from_unit': from_unit,
                        'to_unit': to_unit,
                        'result': result
                    }
                }
            else:
                return {
                    'success': False,
                    'response': f"Sorry, I can't convert from {from_unit} to {to_unit}. Please check the units and try again.",
                    'error': 'Unsupported conversion'
                }
        except Exception as e:
            logger.error(f"Error in unit conversion: {e}")
            return {
                'success': False,
                'response': 'Sorry, I encountered an error while performing the conversion. Please try again.',
                'error': str(e)
            }
    
    def _parse_conversion_request(self, text: str) -> Optional[Tuple[float, str, str]]:
        """Parse conversion request from text"""
        text_lower = text.lower()
        
        # Extract number
        number_match = re.search(r'(\d+(?:\.\d+)?)', text)
        if not number_match:
            return None
        
        value = float(number_match.group(1))
        
        # Try to identify units
        from_unit = self._identify_unit(text_lower, 'from')
        to_unit = self._identify_unit(text_lower, 'to')
        
        if from_unit and to_unit:
            return value, from_unit, to_unit
        
        return None
    
    def _identify_unit(self, text: str, direction: str) -> Optional[str]:
        """Identify unit from text"""
        # Temperature units
        if 'celsius' in text or '°c' in text or 'c' in text:
            return 'celsius'
        elif 'fahrenheit' in text or '°f' in text or 'f' in text:
            return 'fahrenheit'
        elif 'kelvin' in text or '°k' in text or 'k' in text:
            return 'kelvin'
        
        # Length units
        elif 'meter' in text or 'metre' in text:
            return 'meters'
        elif 'foot' in text or 'feet' in text or 'ft' in text:
            return 'feet'
        elif 'inch' in text or 'inches' in text or 'in' in text:
            return 'inches'
        elif 'centimeter' in text or 'cm' in text:
            return 'centimeters'
        elif 'kilometer' in text or 'km' in text:
            return 'kilometers'
        elif 'mile' in text or 'miles' in text:
            return 'miles'
        elif 'yard' in text or 'yards' in text:
            return 'yards'
        
        # Weight units
        elif 'kilogram' in text or 'kg' in text:
            return 'kilograms'
        elif 'pound' in text or 'lb' in text:
            return 'pounds'
        elif 'gram' in text or 'g' in text:
            return 'grams'
        elif 'ounce' in text or 'oz' in text:
            return 'ounces'
        elif 'ton' in text:
            return 'tons'
        
        # Volume units
        elif 'liter' in text or 'litre' in text or 'l' in text:
            return 'liters'
        elif 'gallon' in text or 'gal' in text:
            return 'gallons'
        elif 'cup' in text or 'cups' in text:
            return 'cups'
        elif 'pint' in text or 'pints' in text:
            return 'pints'
        elif 'quart' in text or 'quarts' in text:
            return 'quarts'
        elif 'milliliter' in text or 'ml' in text:
            return 'milliliters'
        
        return None
    
    def _convert(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Perform the actual conversion"""
        try:
            # Temperature conversions
            if from_unit in self.temperature_conversions and to_unit in self.temperature_conversions[from_unit]:
                return self.temperature_conversions[from_unit][to_unit](value)
            
            # Length conversions
            if from_unit in self.length_conversions and to_unit in self.length_conversions[from_unit]:
                return value * self.length_conversions[from_unit][to_unit]
            
            # Weight conversions
            if from_unit in self.weight_conversions and to_unit in self.weight_conversions[from_unit]:
                return value * self.weight_conversions[from_unit][to_unit]
            
            # Volume conversions
            if from_unit in self.volume_conversions and to_unit in self.volume_conversions[from_unit]:
                return value * self.volume_conversions[from_unit][to_unit]
            
            return None
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None
    
    def _format_result(self, value: float, from_unit: str, result: float, to_unit: str) -> str:
        """Format the conversion result"""
        # Round to specified decimal places
        rounded_result = round(result, self.decimal_places)
        
        # Remove trailing zeros
        if rounded_result == int(rounded_result):
            rounded_result = int(rounded_result)
        
        # Format the response
        if from_unit == to_unit:
            return f"{value} {from_unit} = {rounded_result} {to_unit}"
        else:
            return f"{value} {from_unit} = {rounded_result} {to_unit}"
    
    def get_supported_conversions(self) -> Dict[str, Any]:
        """Get list of supported conversions"""
        return {
            'temperature': list(self.temperature_conversions.keys()),
            'length': list(self.length_conversions.keys()),
            'weight': list(self.weight_conversions.keys()),
            'volume': list(self.volume_conversions.keys())
        }
    
    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert temperature between units"""
        if from_unit in self.temperature_conversions and to_unit in self.temperature_conversions[from_unit]:
            return self.temperature_conversions[from_unit][to_unit](value)
        return None
    
    def convert_length(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert length between units"""
        if from_unit in self.length_conversions and to_unit in self.length_conversions[from_unit]:
            return value * self.length_conversions[from_unit][to_unit]
        return None
    
    def convert_weight(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert weight between units"""
        if from_unit in self.weight_conversions and to_unit in self.weight_conversions[from_unit]:
            return value * self.weight_conversions[from_unit][to_unit]
        return None
    
    def convert_volume(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert volume between units"""
        if from_unit in self.volume_conversions and to_unit in self.volume_conversions[from_unit]:
            return value * self.volume_conversions[from_unit][to_unit]
        return None

# Global instance
converter_feature = UnitConverter()

def handle_converter_command(text: str) -> Dict[str, Any]:
    """Handle unit conversion commands"""
    return converter_feature.handle_converter_command(text) 