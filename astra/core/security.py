"""
Security management for Astra voice assistant.
"""

import hashlib
import hmac
import os
import platform
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt

from .config import settings
from .logging import get_logger


class SecurityManager:
    """Manages security features for Astra."""
    
    def __init__(self):
        self.logger = get_logger("security")
        self._encryption_key = None
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption components."""
        if settings.encryption_key:
            key = settings.encryption_key.encode()
        else:
            # Generate key from secret key
            salt = settings.secret_key.encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode()))
        
        self._encryption_key = key
        self._fernet = Fernet(key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data using AES-256."""
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error("Encryption failed", error=str(e))
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using AES-256."""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error("Decryption failed", error=str(e))
            raise
    
    def generate_hardware_fingerprint(self) -> str:
        """Generate unique hardware fingerprint."""
        try:
            # Collect system information
            system_info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "node": platform.node(),
            }
            
            # Get MAC address
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                  for elements in range(0,2*6,2)][::-1])
            system_info["mac_address"] = mac_address
            
            # Get CPU info
            try:
                import psutil
                cpu_info = {
                    "cpu_count": psutil.cpu_count(),
                    "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                }
                system_info.update(cpu_info)
            except ImportError:
                pass
            
            # Generate fingerprint
            fingerprint_data = json.dumps(system_info, sort_keys=True)
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            return fingerprint
        except Exception as e:
            self.logger.error("Hardware fingerprint generation failed", error=str(e))
            return "unknown"
    
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """Validate license key and return license info."""
        try:
            # Decode license key
            decoded_key = base64.b64decode(license_key.encode())
            license_data = json.loads(decoded_key.decode())
            
            # Verify signature
            expected_signature = self._generate_license_signature(license_data)
            if license_data.get("signature") != expected_signature:
                raise ValueError("Invalid license signature")
            
            # Check expiration
            expiration_date = datetime.fromisoformat(license_data["expiration"])
            if datetime.now() > expiration_date:
                raise ValueError("License expired")
            
            # Verify hardware binding
            if settings.hardware_fingerprinting:
                current_fingerprint = self.generate_hardware_fingerprint()
                if license_data.get("hardware_fingerprint") != current_fingerprint:
                    raise ValueError("License not bound to this hardware")
            
            return license_data
        except Exception as e:
            self.logger.error("License validation failed", error=str(e))
            raise
    
    def _generate_license_signature(self, license_data: Dict[str, Any]) -> str:
        """Generate license signature for validation."""
        # Remove signature from data for signing
        data_to_sign = {k: v for k, v in license_data.items() if k != "signature"}
        data_string = json.dumps(data_to_sign, sort_keys=True)
        
        # Generate HMAC signature
        signature = hmac.new(
            settings.secret_key.encode(),
            data_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def generate_license(self, edition: str, user_count: int, 
                        expiration_days: int = 365) -> str:
        """Generate a new license key."""
        try:
            license_data = {
                "edition": edition,
                "user_count": user_count,
                "issued_date": datetime.now().isoformat(),
                "expiration": (datetime.now() + timedelta(days=expiration_days)).isoformat(),
                "hardware_fingerprint": self.generate_hardware_fingerprint(),
                "license_id": str(uuid.uuid4()),
            }
            
            # Generate signature
            license_data["signature"] = self._generate_license_signature(license_data)
            
            # Encode license
            license_json = json.dumps(license_data)
            encoded_license = base64.b64encode(license_json.encode()).decode()
            
            return encoded_license
        except Exception as e:
            self.logger.error("License generation failed", error=str(e))
            raise
    
    def create_jwt_token(self, user_id: str, user_role: str = "user") -> str:
        """Create JWT token for user authentication."""
        try:
            payload = {
                "user_id": user_id,
                "role": user_role,
                "exp": datetime.utcnow() + timedelta(seconds=settings.jwt_expiration),
                "iat": datetime.utcnow(),
            }
            
            token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
            return token
        except Exception as e:
            self.logger.error("JWT token creation failed", error=str(e))
            raise
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            self.logger.error("Invalid JWT token", error=str(e))
            raise ValueError("Invalid token")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        try:
            import bcrypt
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode(), salt)
            return hashed.decode()
        except ImportError:
            # Fallback to simple hash if bcrypt not available
            return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), hashed_password.encode())
        except ImportError:
            # Fallback verification
            return hashlib.sha256(password.encode()).hexdigest() == hashed_password
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate secure random token."""
        return base64.b64encode(os.urandom(length)).decode()
    
    def validate_input(self, data: str, max_length: int = 1000) -> bool:
        """Validate user input for security."""
        if len(data) > max_length:
            return False
        
        # Check for potential injection patterns
        dangerous_patterns = [
            "<script", "javascript:", "data:", "vbscript:", 
            "onload=", "onerror=", "onclick="
        ]
        
        data_lower = data.lower()
        for pattern in dangerous_patterns:
            if pattern in data_lower:
                return False
        
        return True
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for security."""
        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename


# Global security manager instance
security_manager = SecurityManager() 