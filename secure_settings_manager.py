#!/usr/bin/env python3
"""
Secure Settings Manager v2.1
Enhanced security with encryption for sensitive settings
"""

import os
import json
import base64
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Set up logging
logger = logging.getLogger(__name__)


class SecureSettingsManager:
    """Enhanced settings manager with encryption for sensitive data"""
    
    def __init__(self, settings_file: str = "settings.json", use_encryption: bool = True):
        self.settings_file = settings_file
        self.encrypted_file = settings_file.replace(".json", "_secure.dat")
        self.use_encryption = use_encryption
        
        # Sensitive keys that should be encrypted
        self.sensitive_keys = {
            'discord_webhook',
            'api_keys',
            'passwords',
            'tokens'
        }
        
        # Default settings with proper security defaults
        self.default_settings = {
            "backup_network": "",
            "discord_webhook": "",
            "discord_enabled": False,
            "auto_switch_enabled": False,
            "auto_switch_confirm": True,
            "notifications_enabled": True,
            "log_attacks": True,
            "demo_mode": False,
            "security_level": "high",
            "max_threat_score": 7,
            "enable_logging": True,
            "log_level": "INFO",
            "connection_timeout": 15,
            "monitoring_interval": 1,
            "pattern_analysis_interval": 15
        }
        
        self.settings = self.load_settings()
        self._cipher_suite = None
        
    def _get_machine_key(self) -> bytes:
        """Generate a machine-specific key for encryption"""
        try:
            # Use multiple machine-specific identifiers
            import platform
            machine_info = f"{platform.machine()}{platform.processor()}{platform.system()}"
            
            # Add user-specific information
            try:
                import getpass
                machine_info += getpass.getuser()
            except:
                pass
            
            # Create a consistent key from machine info
            key_material = machine_info.encode()
            
            # Use PBKDF2 to derive a proper key
            salt = b"WiFiDeauthDetectorSalt2024"  # Fixed salt for consistency
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            return base64.urlsafe_b64encode(kdf.derive(key_material))
            
        except Exception as e:
            logger.warning(f"Could not generate machine key: {e}")
            # Fallback to a default key (less secure but functional)
            return base64.urlsafe_b64encode(b"default_key_wifi_detector_2024"[:32].ljust(32, b'0'))
    
    def _get_cipher_suite(self) -> Fernet:
        """Get or create cipher suite for encryption"""
        if self._cipher_suite is None:
            key = self._get_machine_key()
            self._cipher_suite = Fernet(key)
        return self._cipher_suite
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value"""
        if not self.use_encryption or not value:
            return value
        
        try:
            cipher_suite = self._get_cipher_suite()
            encrypted_data = cipher_suite.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting value: {e}")
            return value  # Return unencrypted if encryption fails
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value"""
        if not self.use_encryption or not encrypted_value:
            return encrypted_value
        
        try:
            cipher_suite = self._get_cipher_suite()
            encrypted_data = base64.urlsafe_b64decode(encrypted_value.encode())
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.warning(f"Error decrypting value (may be unencrypted): {e}")
            return encrypted_value  # Return as-is if decryption fails
    
    def _validate_setting_value(self, key: str, value: Any) -> tuple[bool, str]:
        """Validate setting values for security and correctness"""
        
        # Discord webhook validation
        if key == 'discord_webhook' and value:
            if not isinstance(value, str):
                return False, "Discord webhook must be a string"
            if value and not value.startswith('https://discord.com/api/webhooks/'):
                return False, "Invalid Discord webhook URL format"
        
        # Network name validation
        elif key == 'backup_network' and value:
            if not isinstance(value, str):
                return False, "Network name must be a string"
            if len(value) > 32:
                return False, "Network name too long (max 32 characters)"
            # Check for dangerous characters
            import re
            if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', value):
                return False, "Network name contains invalid characters"
        
        # Numeric validations
        elif key in ['max_threat_score', 'connection_timeout', 'monitoring_interval']:
            if not isinstance(value, (int, float)):
                return False, f"{key} must be a number"
            if value < 0:
                return False, f"{key} must be positive"
        
        # Boolean validations
        elif key in ['discord_enabled', 'auto_switch_enabled', 'auto_switch_confirm', 
                    'notifications_enabled', 'log_attacks', 'demo_mode']:
            if not isinstance(value, bool):
                return False, f"{key} must be true or false"
        
        # Security level validation
        elif key == 'security_level':
            if value not in ['low', 'medium', 'high', 'paranoid']:
                return False, "Security level must be low, medium, high, or paranoid"
        
        # Log level validation
        elif key == 'log_level':
            if value not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                return False, "Invalid log level"
        
        return True, "Valid"
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings with security validation"""
        settings = self.default_settings.copy()
        
        try:
            # Try to load from encrypted file first
            if self.use_encryption and os.path.exists(self.encrypted_file):
                settings.update(self._load_encrypted_settings())
            # Fallback to regular file
            elif os.path.exists(self.settings_file):
                settings.update(self._load_regular_settings())
            
            # Validate all loaded settings
            validated_settings = {}
            for key, value in settings.items():
                is_valid, error_msg = self._validate_setting_value(key, value)
                if is_valid:
                    validated_settings[key] = value
                else:
                    logger.warning(f"Invalid setting {key}={value}: {error_msg}, using default")
                    if key in self.default_settings:
                        validated_settings[key] = self.default_settings[key]
            
            logger.info("Settings loaded successfully")
            return validated_settings
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def _load_encrypted_settings(self) -> Dict[str, Any]:
        """Load settings from encrypted file"""
        try:
            with open(self.encrypted_file, 'rb') as f:
                encrypted_data = f.read()
            
            cipher_suite = self._get_cipher_suite()
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            
            settings_data = json.loads(decrypted_data.decode())
            logger.debug("Loaded encrypted settings")
            return settings_data
            
        except Exception as e:
            logger.error(f"Error loading encrypted settings: {e}")
            return {}
    
    def _load_regular_settings(self) -> Dict[str, Any]:
        """Load settings from regular JSON file"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            
            # Decrypt sensitive values if they appear to be encrypted
            for key, value in settings_data.items():
                if key in self.sensitive_keys and isinstance(value, str):
                    settings_data[key] = self._decrypt_value(value)
            
            logger.debug("Loaded regular settings")
            return settings_data
            
        except Exception as e:
            logger.error(f"Error loading regular settings: {e}")
            return {}
    
    def save_settings(self) -> bool:
        """Save settings with encryption for sensitive data"""
        try:
            # Validate all settings before saving
            for key, value in self.settings.items():
                is_valid, error_msg = self._validate_setting_value(key, value)
                if not is_valid:
                    logger.error(f"Cannot save invalid setting {key}={value}: {error_msg}")
                    return False
            
            # Prepare settings for saving
            settings_to_save = self.settings.copy()
            
            if self.use_encryption:
                # Save to encrypted file
                success = self._save_encrypted_settings(settings_to_save)
                
                # Remove old unencrypted file if encryption succeeded
                if success and os.path.exists(self.settings_file):
                    try:
                        os.remove(self.settings_file)
                        logger.info("Removed old unencrypted settings file")
                    except:
                        pass  # Don't fail if we can't remove old file
                
                return success
            else:
                # Save to regular file with encrypted sensitive values
                for key, value in settings_to_save.items():
                    if key in self.sensitive_keys and isinstance(value, str) and value:
                        settings_to_save[key] = self._encrypt_value(value)
                
                return self._save_regular_settings(settings_to_save)
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def _save_encrypted_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Save settings to encrypted file"""
        try:
            # Convert to JSON
            json_data = json.dumps(settings_data, indent=2, ensure_ascii=False)
            
            # Encrypt the entire JSON
            cipher_suite = self._get_cipher_suite()
            encrypted_data = cipher_suite.encrypt(json_data.encode('utf-8'))
            
            # Write to file
            with open(self.encrypted_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Set restrictive file permissions
            try:
                os.chmod(self.encrypted_file, 0o600)  # Read/write for owner only
            except:
                pass  # May not work on Windows
            
            logger.info("Settings saved to encrypted file")
            return True
            
        except Exception as e:
            logger.error(f"Error saving encrypted settings: {e}")
            return False
    
    def _save_regular_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Save settings to regular JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
            
            # Set restrictive file permissions
            try:
                os.chmod(self.settings_file, 0o600)  # Read/write for owner only
            except:
                pass  # May not work on Windows
            
            logger.info("Settings saved to regular file")
            return True
            
        except Exception as e:
            logger.error(f"Error saving regular settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value with automatic decryption for sensitive keys"""
        value = self.settings.get(key, default)
        
        # Decrypt sensitive values if needed
        if key in self.sensitive_keys and isinstance(value, str) and value:
            return self._decrypt_value(value)
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set setting value with validation"""
        # Validate the setting
        is_valid, error_msg = self._validate_setting_value(key, value)
        if not is_valid:
            logger.error(f"Invalid setting value: {error_msg}")
            return False
        
        # Store the value (encryption happens during save)
        self.settings[key] = value
        return True
    
    def get_security_info(self) -> Dict[str, Any]:
        """Get information about security settings"""
        return {
            'encryption_enabled': self.use_encryption,
            'encrypted_file_exists': os.path.exists(self.encrypted_file),
            'regular_file_exists': os.path.exists(self.settings_file),
            'sensitive_keys_count': len(self.sensitive_keys),
            'security_level': self.get('security_level', 'medium'),
            'last_modified': self._get_file_modification_time()
        }
    
    def _get_file_modification_time(self) -> Optional[str]:
        """Get last modification time of settings file"""
        try:
            file_path = self.encrypted_file if os.path.exists(self.encrypted_file) else self.settings_file
            if os.path.exists(file_path):
                mtime = os.path.getmtime(file_path)
                return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.error(f"Error getting file modification time: {e}")
        return None
    
    def backup_settings(self, backup_path: str) -> bool:
        """Create a backup of current settings"""
        try:
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'settings': self.settings.copy(),
                'version': '2.1',
                'encrypted': self.use_encryption
            }
            
            # Don't include actual sensitive values in backup
            for key in self.sensitive_keys:
                if key in backup_data['settings'] and backup_data['settings'][key]:
                    backup_data['settings'][key] = "[REDACTED]"
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings backup created: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating settings backup: {e}")
            return False
    
    def export_settings(self, export_path: str, include_sensitive: bool = False) -> bool:
        """Export settings for sharing (with option to exclude sensitive data)"""
        try:
            export_data = self.settings.copy()
            
            if not include_sensitive:
                for key in self.sensitive_keys:
                    if key in export_data:
                        export_data[key] = ""  # Clear sensitive values
            
            export_wrapper = {
                'export_timestamp': datetime.now().isoformat(),
                'version': '2.1',
                'includes_sensitive_data': include_sensitive,
                'settings': export_data
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_wrapper, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings exported: {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            return False


# Legacy SettingsManager for backward compatibility
class SettingsManager:
    """Legacy settings manager - redirects to SecureSettingsManager"""
    
    def __init__(self, settings_file: str = "settings.json"):
        try:
            # Try to use encryption if cryptography is available
            self.secure_manager = SecureSettingsManager(settings_file, use_encryption=True)
        except ImportError:
            logger.warning("Cryptography library not available, using unencrypted storage")
            self.secure_manager = SecureSettingsManager(settings_file, use_encryption=False)
        
        logger.warning("Using legacy SettingsManager. Consider upgrading to SecureSettingsManager.")
    
    def load_settings(self) -> Dict[str, Any]:
        """Legacy method"""
        return self.secure_manager.settings
    
    def save_settings(self) -> bool:
        """Legacy method"""
        return self.secure_manager.save_settings()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Legacy method"""
        return self.secure_manager.get(key, default)
    
    def set(self, key: str, value: Any):
        """Legacy method"""
        self.secure_manager.set(key, value)
    
    @property
    def settings(self) -> Dict[str, Any]:
        """Legacy property"""
        return self.secure_manager.settings
