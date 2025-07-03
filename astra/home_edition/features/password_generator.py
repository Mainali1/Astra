import random
import string

def generate_password(length: int = 12, include_uppercase: bool = True, include_digits: bool = True, include_symbols: bool = True) -> str:
    """
    Generates a strong, random password.

    Args:
        length: The desired length of the password.
        include_uppercase: Whether to include uppercase letters.
        include_digits: Whether to include digits.
        include_symbols: Whether to include symbols.

    Returns:
        The generated password.
    """
    if length < 4:
        raise ValueError("Password length must be at least 4.")

    characters = string.ascii_lowercase
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_digits:
        characters += string.digits
    if include_symbols:
        characters += string.punctuation

    if not characters:
        raise ValueError("At least one character type (lowercase, uppercase, digits, symbols) must be selected.")

    password = ''.join(random.choice(characters) for i in range(length))
    return password